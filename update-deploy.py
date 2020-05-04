#!/usr/bin/env python3.6

import argparse
import subprocess
import time

##########################################
# Get the arguments passed to the script #
##########################################

parser = argparse.ArgumentParser(description='Redeploy the Docker container for the Notebook Library')
args = parser.parse_args()

##########################################
# Start the Notebook Library             #
##########################################

try:
    # Stop the running container
    print('Stopping Docker container...')
    subprocess.run(f'docker stop website'.split())
    print('Container stopped')

    # GIT pull
    print('Updating GIT clone...')
    subprocess.run(f'git -C notebook-library pull'.split())
    print('GIT updated')

    # Start the container again
    print('Restarting the Docker container...')
    subprocess.run(f'./start-server.py'.split())
    time.sleep(10)
    print('Container running')

    # Update the database
    print('Updating the database schema')
    subprocess.run('docker exec website /bin/bash -c "source activate webapp && /srv/notebook-library/manage.py makemigrations && /srv/notebook-library/manage.py migrate"', shell=True)
    print('Database update complete')
except KeyboardInterrupt:
    print('Interrupting script')
