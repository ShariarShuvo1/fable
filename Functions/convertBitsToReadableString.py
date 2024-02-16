def convert_bits_to_readable_string(bits):
    units = ['B', 'KB', 'MB', 'GB']
    index = 0
    while bits >= 1024 and index < len(units) - 1:
        bits /= 1024.0
        index += 1
    return '{:.1f}{}'.format(bits, units[index])