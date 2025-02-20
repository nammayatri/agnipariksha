#!/bin/bash
set +x

# to export env variables
set -a
. ./local.env
set +a

echo "Running customer locust ..."

# Run locust
locust -f customer.py --web-port 8099