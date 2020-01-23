# Dockerfile for running an instance of the GenePattern Notebook Catalog

FROM ubuntu:18.04

MAINTAINER Thorin Tabor <tmtabor@cloud.ucsd.edu>

#############################################
##      System updates                     ##
#############################################

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install wget git bzip2 libcurl4-gnutls-dev gcc python3-dev libmysqlclient-dev && \
    apt-get purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV LANG C.UTF-8

#############################################
##      Create the config directory        ##
#############################################

RUN mkdir /config

#############################################
##      Install miniconda                  ##
#############################################

RUN wget -q https://repo.continuum.io/miniconda/Miniconda3-4.6.14-Linux-x86_64.sh -O /tmp/miniconda.sh  && \
    bash /tmp/miniconda.sh -f -b -p /opt/conda && \
    /opt/conda/bin/conda install --yes -c conda-forge \
      python=3.6 requests pip pycurl \
      nodejs configurable-http-proxy && \
    /opt/conda/bin/pip install --upgrade pip && \
    rm /tmp/miniconda.sh
ENV PATH=/opt/conda/bin:$PATH

#############################################
##      Create the webapp environment     ##
#############################################

# Create the Python 3.6 environment
RUN /opt/conda/bin/conda update -y conda
RUN /opt/conda/bin/conda create -y --name webapp python=3.6 pip

COPY ./requirements.txt /src/requirements.txt
RUN /bin/bash -c "source activate webapp && \
    pip install -r /src/requirements.txt"

#############################################
##      Add the library webservice         ##
#############################################

WORKDIR /srv/notebook-library/
RUN git clone https://github.com/genepattern/notebook-library.git /srv/notebook-library/

#############################################
##      Configure the repository           ##
#############################################

# Add settings.py to config dir
RUN cp /srv/notebook-library/library/settings.py /config/settings.py
RUN rm /srv/notebook-library/library/settings.py
RUN ln -s /config/settings.py /srv/notebook-library/library/settings.py

# Add the templates to the config dir
RUN cp -r /srv/notebook-library/templates /config/
RUN rm -r /srv/notebook-library/templates
RUN ln -s /config/templates /srv/notebook-library/templates

# Add the static files to the config dir
RUN cp -r /srv/notebook-library/static /config/
RUN rm -r /srv/notebook-library/static
RUN ln -s /config/static /srv/notebook-library/static

RUN /bin/bash -c "source activate webapp && \
    /srv/notebook-library/manage.py makemigrations"
RUN /bin/bash -c "source activate webapp && \
    /srv/notebook-library/manage.py migrate --run-syncdb"
RUN /bin/bash -c "source activate webapp && \
    /srv/notebook-library/manage.py collectstatic --noinput"

COPY ./start-server.sh /srv/notebook-library/start-server.sh

#############################################
##      Start the webapp                   ##
#############################################

CMD ["/srv/notebook-library/start-server.sh"]