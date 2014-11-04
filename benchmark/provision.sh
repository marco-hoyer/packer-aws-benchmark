#!/bin/bash
set -e -E -u -x

# Enable YUM Repos that where copied into the chroot by the packer template
sed -i -e '1,12s/enabled=.*/enabled=1/' /etc/yum.repos.d/*.repo

# Amazon Linux uses latest as releasever, hard code it in their repos so that we can change it
sed -i -e 's/\$releasever/latest/g' /etc/yum.repos.d/amzn*repo

# Better teach yum repo server that latest is a valid alias for the highest 6X, 7X ... number
echo 6X >/etc/yum/vars/releasever

# Dump repos to know what was used here
yum repolist

# install some packages
yum -y install tomcat8 java-1.8.0-openjdk mongodb-server httpd mysql-server
