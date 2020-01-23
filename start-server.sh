#!/bin/bash

#/bin/bash -c "source activate webapp && /srv/notebook-library/manage.py createsuperuser -u foo -p bar"
#/bin/bash -c "source activate webapp && /srv/notebook-library/manage.py makemigrations"
#/bin/bash -c "source activate webapp && /srv/notebook-library/manage.py migrate --run-syncdb"
#/bin/bash -c "source activate webapp &&  /srv/notebook-library/manage.py collectstatic --noinput"

# This script is used INSIDE the Dockerfile to start the notebook portal server
source activate webapp
/srv/notebook-library/manage.py runserver 0.0.0.0:8000
