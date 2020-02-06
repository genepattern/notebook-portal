import tornado.ioloop
import tornado.web
import shutil
import os


class ZipHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.get_argument("id"),
        username = self.get_argument("user", strip=True),
        servername = self.get_argument("server", strip=True),
        zip = f'/data/repository/{id[0]}'
        shutil.make_archive(zip, 'zip', f'/data/users/{username[0]}/{servername[0]}')
        os.chmod(f'{zip}.zip', 0o777)


def make_app():
    return tornado.web.Application([
        (r"/services/library/", ZipHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()
