#!/usr/bin/env bash

set -a
source .env
set +a

python main.py $1
