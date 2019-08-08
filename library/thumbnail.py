import os
import requests
from PIL import Image
from library import settings


def thumbnail_path(id):
    return os.path.join(settings.STATIC_ROOT, 'images', 'thumbnails', f'{id}.png')


def exists(id):
    path = thumbnail_path(id)
    return os.path.exists(path) and os.path.getsize(path) > 1024


def generate(id):
    url = f'{settings.BASE_HUB_URL}/services/sharing/notebooks/{id}/preview/image/'

    # Lazily create thumbnail directory
    filename = thumbnail_path(id)
    create_directory(os.path.dirname(filename))

    # Download the preview image
    r = requests.get(url)
    thumb_file = open(filename, 'wb')
    thumb_file.write(r.content)
    thumb_file.close()

    # Overwrite it with the thumbnail
    create_thumbnail(filename)


def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)


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
