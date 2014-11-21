#!/bin/bash

# configure branch in $1 if needed, otherwise master is used as default
BRANCH=${1:-master}

export GOPATH=$(pwd)
echo "Using gopath: $GOPATH"

echo "Installing dependencies"
yum install bzr git mercurial golang -y
go get -u github.com/mitchellh/gox
cd $GOPATH/src/github.com/mitchellh

echo "Cloning packer into $(pwd)"
git clone https://github.com/ImmobilienScout24/packer.git
cd $GOPATH/src/github.com/mitchellh/packer
git fetch
git checkout $BRANCH

PATH=$PATH:/tmp/packer-aws-benchmark/bin

echo "Building packer"
make updatedeps
make dev

echo "Installing packer binaries to /usr/bin"
cd $GOPATH/bin
mv packer packer.io
mv packer* /usr/bin

echo "Finished packer installation"
