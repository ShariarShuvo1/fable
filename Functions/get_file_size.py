import os


def get_file_size(file_path):
    if os.path.isfile(file_path):
        return os.path.getsize(file_path)
    else:
        return -1
