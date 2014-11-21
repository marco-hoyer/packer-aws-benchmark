packer-aws-benchmark
====================

This is a kind of framework allowing performance testing of packer chroot builder on AWS. It tests combinations of instance type and storage type in combination with code changes served as git branches. The idea is to find an optimum of build time and costs. Results of the tests get reported to a dynamodb table and are available via API or csv export.

Usage
====================
The simple way to start this is by creating a cloudformation stack from cfn_template.json.
It starts some instances in a vpc environment and automatically executes the tests.

Warning
====================
This causes AWS costs for running instances. Further more created AMIs aren't automatically deleted after test execution.
You have to delete all AMIs with a name tag starting with packer_benchmark_ami!
