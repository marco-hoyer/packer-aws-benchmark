from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import ItemNotFound
from boto.exception import NoAuthHandlerFound
from boto.utils import get_instance_metadata
from time import time
import subprocess
import argparse
import logging
import sys
import json


class DynamoDbMetricWriter(object):

    def __init__(self, region, table_name, benchmark_config, localrun, debug):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                            datefmt='%d.%m.%Y %H:%M:%S',level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)

        self.benchmark_config = benchmark_config
        self.localrun = localrun

        try:
            self.logger.info("Connecting to dynamodb table {0} in region {1}".format(table_name, region))
            self.connection = DynamoDBConnection(host='dynamodb.{0}.amazonaws.com'.format(region), region=region)
            self.table = Table(table_name, connection=self.connection)
        except NoAuthHandlerFound as e:
            self.logger.error("Could not authenticate against aws api: {0}".format(str(e)))
            sys.exit(1)
        except Exception as e:
            self.logger.error("Could not load metrics table from dynamodb: {0}".format(str(e)))

    def put_metrics(self, build_time_metrics):
        if not build_time_metrics:
            return None

        try:
            item = self.table.get_item(instance_type=_get_instance_type(self.localrun), config=self.benchmark_config)
            self.logger.debug("Found existing entity in dynamodb")
        except ItemNotFound:
            self.logger.debug("No existing entity found in dynamodb, creating new one")
            item = Item(self.table, data={'instance_type': _get_instance_type(self.localrun),
                                          'config': self.benchmark_config})

        build_time_json = item['build_time']

        if build_time_json:
            self.logger.debug("Extending existing metric list for build_time")
            # extend existing list
            build_time = json.loads(build_time_json)
            build_time.extend(build_time_metrics)
            item['build_time'] = json.dumps(build_time)
        else:
            item['build_time'] = json.dumps(build_time_metrics)

        if item.needs_save():
            item.partial_save()
            self.logger.debug("Saved item to dynamodb")


class TimedTestRunner(object):

    def __init__(self, dynamodb_metric_writer, command, debug):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                            datefmt='%d.%m.%Y %H:%M:%S',level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)

        self.dynamodb = dynamodb_metric_writer
        self.command = command

    def _execute(self, command_string):
        command = command_string.split(' ')
        self.logger.info("Executing '{0}'".format(command_string))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.stdout.read()
        err = p.stderr.read()
        return p.wait(), out, err

    def _run_once(self):
        try:
            start = time()
            (exit_code, out, err) = self._execute(self.command)
            end = time()
            elapsed = end - start
        except Exception as e:
            self.logger.error(
                "Error occured executing '{0}': {1}, dropping metric for this run".format(self.command, str(e)))
            return None

        if exit_code != 0:
            self.logger.error(
                "'{0}' terminated with exit code {1}, dropping metric for this run".format(self.command, exit_code))
            self.logger.debug("StdOut: {0}".format(out))
            self.logger.debug("StdErr: {0}".format(err))
            return None
        else:
            self.logger.debug("Single execution took {0}s".format(elapsed))
            # 1s resolution is enough, eases handling
            return int(elapsed)

    def run_looped_test(self, count):
        build_time_metrics = []
        for i in range(1,count+1):
            build_time = self._run_once()
            if build_time is not None:
                build_time_metrics.append(build_time)
            i += 1
        self.logger.debug(
            "Collected metrics to be stored in dynamodb (rounded to full seconds): {0}".format(build_time_metrics))
        self.dynamodb.put_metrics(build_time_metrics)


def _get_instance_type(localrun):
    if localrun:
        return "t2.micro"
    else:
        metadata = get_instance_metadata()
        return metadata['instance-type']


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('executable', help="The tests commandline command to be executed", type=str)
    parser.add_argument('config', help="A configuration key examining the benchmarked configuration", type=str)
    parser.add_argument('--iterations', help="Number of Packer build runs to be executed", type=int, default=10)
    parser.add_argument('--region', help="AWS region to operate within", type=str, default="eu-west-1")
    parser.add_argument('--dynamodbtable', help="Dynamodb table name", type=str, default="packer_build_metrics")
    parser.add_argument("--localrun", help="Run on ec2 instance", action="store_true", default=False)
    parser.add_argument("--debug", help="Set Loglevel to debug", action="store_true", default=False)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    dynamodb_metric_writer = DynamoDbMetricWriter(args.region, args.dynamodbtable,
                                                  args.config, args.localrun, args.debug)
    runner = TimedTestRunner(dynamodb_metric_writer, args.executable, args.debug)
    runner.run_looped_test(args.iterations)