#!/bin/bash
unzip -Z -st $1 |sed -e '$d';
