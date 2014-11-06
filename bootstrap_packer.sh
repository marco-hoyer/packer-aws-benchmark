#!/bin/bash

export GOPATH=$(pwd)
echo "Using gopath: $GOPATH"

echo "Installing dependencies"
sudo yum install bzr git mercurial golang -y
go get -u github.com/mitchellh/gox
cd $GOPATH/src/github.com/mitchellh

echo "Cloning packer into $(pwd)"
git clone https://github.com/ImmobilienScout24/packer.git
PATH=$PATH:/tmp/packer-aws-benchmark/bin
cd $GOPATH/src/github.com/mitchellh/packer

echo "Building packer"
make updatedeps
make dev

echo "Installing packer binaries to /usr/bin"
cd $GOPATH/bin
mv packer packer.io
sudo mv packer* /usr/bin

echo "Finished packer installation"
echo "You can execute packer with packer.io <params>"

echo "Runnging benchmark in $GOPATH/benchmark"
cd $GOPATH/benchmark
sudo ./run.sh
