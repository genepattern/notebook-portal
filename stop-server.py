#!/usr/bin/env python3.6

import argparse
import subprocess

##########################################
# Get the arguments passed to the script #
##########################################

# Handle the parameters
parser = argparse.ArgumentParser(description='Stop the Docker container for the Notebook Library')

args = parser.parse_args()

##########################################
# Start the Notebook Library             #
##########################################

try:
    subprocess.Popen(f'docker stop website'.split())
except KeyboardInterrupt:
    print('Shutting down Notebook Library')
