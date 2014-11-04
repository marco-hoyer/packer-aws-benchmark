#!/bin/bash

export GOPATH=$(pwd)
echo "Using gopath: $GOPATH"
sudo yum install bzr git mercurial golang -y
go get -u github.com/mitchellh/gox
cd $GOPATH/src/github.com/mitchellh
git clone https://github.com/ImmobilienScout24/packer.git
cd $GOPATH/src/github.com/mitchellh/packer
make updatedeps
make dev
cd $GOPATH/bin
mv packer packer.io
sudo mv packer* /usr/bin
