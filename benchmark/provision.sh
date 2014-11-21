#!/bin/bash
set -e -E -u -x

# Enable YUM Repos that where copied into the chroot by the packer template
sed -i -e '1,12s/enabled=.*/enabled=1/' /etc/yum.repos.d/*.repo

# install some packages
time yum -y install tomcat8 java-1.8.0-openjdk mongodb-server httpd mysql-server
