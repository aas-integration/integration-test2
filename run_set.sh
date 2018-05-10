#!/bin/bash

echo "Run for $1"
python experiment.py -g -rc -d "$1" -p $1
