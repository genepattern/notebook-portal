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
        username = self.get_argument("user", strip=True)[0],
        servername = self.get_argument("server", strip=True)[0],
        ZipHandler._copy_notebook_project(copy[0], username, servername)

    @staticmethod
    def _copy_notebook_project(project_copy, mount_username, server_name):
        dir_path = f'/data/users/{mount_username}/{server_name}'

        # Create directory if it doesn't exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            os.chmod(dir_path, 0o777)

        with ZipFile(f'/data/repository/{project_copy}.zip', 'r') as zip:
            zip.extractall(path=dir_path)


def make_app():
    return tornado.web.Application([
        (r"/services/library/", ZipHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()
