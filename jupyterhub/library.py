from zipfile import ZipFile

import tornado.ioloop
import tornado.web
import shutil
import os


class ZipHandler(tornado.web.RequestHandler):
    def post(self):
        id = self.get_argument("id"),
        username = self.get_argument("user", strip=True),
        servername = self.get_argument("server", strip=True),
        zip = f'/data/repository/{id[0]}'
        shutil.make_archive(zip, 'zip', f'/data/users/{username[0]}/{servername[0]}')
        os.chmod(f'{zip}.zip', 0o777)

    def get(self):
        copy = self.get_argument("copy", strip=True),
        username = self.get_argument("user", strip=True),
        servername = self.get_argument("server", strip=True),
        unique_name = ZipHandler._copy_notebook_project(f'{copy[0]}', f'{username[0]}', f'{servername[0]}')
        self.write(unique_name)

    @staticmethod
    def _copy_notebook_project(project_copy, mount_username, server_name):
        # Set a unique server name
        unique_name = ZipHandler._ensure_new_directory(mount_username, server_name)
        dir_path = f'/data/users/{mount_username}/{unique_name}'
        print(dir_path)
        with ZipFile(f'/data/repository/{project_copy}.zip', 'r') as zip:
            zip.extractall(path=dir_path)
        for root, dirs, files in os.walk(dir_path):
            for f in dirs:
                os.chmod(os.path.join(root, f), 0o777)
            for f in files:
                os.chmod(os.path.join(root, f), 0o777)
        return unique_name

    @staticmethod
    def _ensure_new_directory(mount_username, server_name, count=0):
        if not count: unique_name = server_name
        else: unique_name = f'{server_name}{count}'
        dir_path = f'/data/users/{mount_username}/{unique_name}'

        if os.path.exists(dir_path):
            return ZipHandler._ensure_new_directory(mount_username, f'{server_name}', count + 1)
        else:
            os.makedirs(dir_path)
            os.chmod(dir_path, 0o777)
            return unique_name


def make_app():
    return tornado.web.Application([
        (r"/services/library/", ZipHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()
