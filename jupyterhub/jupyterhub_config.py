import os

c = get_config()

# Configure named servers
c.JupyterHub.allow_named_servers = True

# Set the spawner
c.JupyterHub.spawner_class = 'portalspawner.PortalSpawner'

# Configure PortalSpawner
c.PortalSpawner.image = 'genepattern/genepattern-notebook:20.01.2'
c.PortalSpawner.image_whitelist = {
    'genepattern/genepattern-notebook': 'genepattern/genepattern-notebook:20.01.2',
    'genepattern/notebook-python36': 'genepattern/notebook-python36:19.12',
    'genepattern/notebook-python37': 'genepattern/notebook-python37:19.12',
    'genepattern/notebook-r36': 'genepattern/notebook-r36:19.12'
}
c.PortalSpawner.host_ip = '0.0.0.0'
c.PortalSpawner.name_template = "{prefix}-{username}-{servername}"
c.PortalSpawner.network_name = 'repo'
c.PortalSpawner.remove_containers = True
c.PortalSpawner.debug = True


# Services API configuration
c.JupyterHub.services = [
    {
        'name': 'library',
        'admin': True,
        'url': 'http://127.0.0.1:8011/',
        'cwd': '/data',
        'command': ['/opt/conda/envs/repository/bin/python', './library.py', 'runserver', '0.0.0.0:8011']
    },
    {
        'name': 'cull-idle',
        'admin': True,
        'command': ['python', '/srv/notebook-repository/scripts/cull-idle.py', '--timeout=3600']
    }
]

# Enable CORS
origin = 'http://localhost:8000'
c.Spawner.args = [f'--NotebookApp.allow_origin={origin} --NotebookApp.allow_credentials=True']
c.JupyterHub.tornado_settings = {
    'headers': {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Credentials': 'true',
    },
}