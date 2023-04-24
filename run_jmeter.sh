#!/bin/bash

wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.5.tgz
sudo apt install openjdk-8-jdk -y
tar xf apache-jmeter-5.5.tgz
export PATH=$PATH:apache-jmeter-5.5/bin
jmeter -n -t Photo-Gallery-Test-Plan.jmx -JPhotogalleryAddress=localhost -JOutputPath=./data.csv
jmeter -g ./data.csv -o ./.benchmarks/jmeter
