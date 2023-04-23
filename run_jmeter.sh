#!/bin/bash

sudo apt install jmeter
jmeter -n -t Photo-Gallery-Test-Plan.jmx -JPhotogalleryAddress=localhost -JOutputPath=./data.csv
jmeter -g ./data.csv -o ./.benchmarks/jmeter
