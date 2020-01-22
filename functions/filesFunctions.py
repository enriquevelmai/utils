import os
from PIL import Image


def search_files_with_extension(path, extension):
    if not path:
        raise AttributeError('Path Need')

    if not extension:
        raise AttributeError('Extension Need')
    files_with_extension = list()
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".{}".format(extension)):
                file_path = os.path.join(root, f)
                files_with_extension.append(file_path)

    return files_with_extension


def change_recurency_extension(origin_extension, destiny_extension, path):
    files_with_extension = search_files_with_extension(path=path, extension=origin_extension)

    for f in files_with_extension:
        raw_name = os.path.splitext(f)[0]
        img = Image.open(f)
        img.save('{}.{}'.format(raw_name, destiny_extension))
