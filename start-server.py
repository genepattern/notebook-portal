#!/usr/bin/env python3.6

import argparse
import subprocess

##########################################
# Get the arguments passed to the script #
##########################################

# Handle the --data and --port options
parser = argparse.ArgumentParser(description='Start the Docker container for the Notebook Library')
parser.add_argument('-c', '--config', type=str, default='/config', help='Set the config directory to be mounted in the container')
parser.add_argument('-p', '--port', type=int, default=8000, help='Set the port the repository will be available at')

# Parse the arguments
args = parser.parse_args()

##########################################
# Start the Notebook Library             #
##########################################

try:
    subprocess.Popen(f'docker run --rm \
                                  --name=website \
                                  -p {args.port}:8000 \
                                  -v {args.config}:/config \
                                  genepattern/notebook-library:19.08'.split())
except KeyboardInterrupt:
    print('Shutting down Notebook Library')
