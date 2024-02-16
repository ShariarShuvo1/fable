import os


def sanitize_filename(filename):
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    sanitized_filename = ''.join(char for char in filename if char not in invalid_chars)

    if os.name != 'nt':
        sanitized_filename = sanitized_filename.replace('\0', '')

    return sanitized_filename
