#!/usr/bin/env bash

set -a
source .env
set +a

mkdir -p output
python main.py $1
