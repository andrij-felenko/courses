def cache_load(tag):
    if tag is None:                                  # немає CRC — немає імені
        return None
    path = os.path.join(CACHE_DIR, tag)
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            return fh.read()
    return None


def cache_store(tag, data):
    if tag is None:                                  # свідомо не кешуємо
        return
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, tag), 'wb') as fh:
        fh.write(data)
