#!/bin/bash
for i in {1..10}; do
  /usr/bin/time --append -o time.txt -f %E sudo packer.io build template.json
done
