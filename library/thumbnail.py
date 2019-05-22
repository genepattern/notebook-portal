import os
import requests
from PIL import Image
from library import settings


def path(id):
    return os.path.join('static/images/thumbnails', f'{id}.png')


def exists(id):
    return os.path.exists(path(id))


def generate(id):
    url = f'{settings.BASE_HUB_URL}/services/sharing/notebooks/{id}/preview/image/'

    # Download the preview image
    r = requests.get(url)
    filename = path(id)
    thumb_file = open(filename, 'wb')
    thumb_file.write(r.content)
    thumb_file.close()

    # Overwrite it with the thumbnail
    create_thumbnail(filename)


def create_thumbnail(filename):
    desired_size = 200

    im = Image.open(filename)
    old_width, old_height = im.size  # old_size[0] is in (width, height) format

    new_height = int(float(old_height * desired_size) / old_width)

    im = im.resize((desired_size, new_height), Image.ANTIALIAS)
    im = im.crop((0, 0, desired_size, desired_size))

    # create a new image and paste the resized on it
    new_im = Image.new("RGB", (desired_size, desired_size), (255, 255, 255, 0))
    new_im.paste(im, (0, 0))

    new_im.save(filename)
