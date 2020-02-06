import os
import shutil
from zipfile import ZipFile
from dockerspawner import DockerSpawner


class PortalSpawner(DockerSpawner):
    def __init__(self, **kwargs):
        self.remove_containers = True
        self.debug = True
        self.volumes = {  # Mount the user's directory in the project container
            os.environ['DATA_DIR'] + '/users/{mount_username}/{servername}': '/home/jovyan',
        }
        super(PortalSpawner, self).__init__(**kwargs)

    def run_pre_spawn_hook(self):
        project_copy = getattr(self, "project_copy", "")
        mount_username = getattr(self, "mount_username", self.user.name)
        server_name = getattr(self, "name", "")
        if project_copy:  # If this is launching a new public notebook
            self._copy_notebook_project(project_copy, mount_username, server_name)
        else:  # Otherwise, lazily create the directory if necessary
            self._create_directory(mount_username, server_name)

        super(PortalSpawner, self).run_pre_spawn_hook()

    def run_post_stop_hook(self):
        super(PortalSpawner, self).run_post_stop_hook()

    def template_namespace(self):
        escaped_image = self.image.replace("/", "_")
        server_name = getattr(self, "name", "")
        mount_username = getattr(self, "mount_username", self.user.name)
        return {
            "username": self.escaped_name,
            "safe_username": self.user.name,
            "raw_username": self.user.name,
            "imagename": escaped_image,
            "servername": server_name,
            "prefix": self.prefix,
            "mount_username": mount_username
        }

    @staticmethod
    def _copy_notebook_project(project_copy, mount_username, server_name):
        dir_path = os.environ['DATA_DIR'] + '/users/' + mount_username + '/' + server_name

        # Create directory if it doesn't exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            os.chmod(dir_path, 0o777)

        with ZipFile(project_copy, 'r') as zip:
            zip.extractall(path=dir_path)

    @staticmethod
    def _create_directory(username, servername):
        default_nb_dir = os.environ['DATA_DIR'] + '/defaults'
        dir_path = os.environ['DATA_DIR'] + '/users/' + username + '/' + servername

        # Create directory if it doesn't exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            os.chmod(dir_path, 0o777)

            # Copy default files over if the directory was just created
            all_files = os.listdir(default_nb_dir)
            for f in all_files:
                file_path = os.path.join(default_nb_dir, f)
                if not os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.copytree(file_path, os.path.join(dir_path, f))
                    elif os.path.isfile(file_path):
                        shutil.copy(file_path, dir_path)