XZ_MAGIC = b'\xfd7zXZ\x00'


def fetch(link, uri):
    """Завантажити файл за адресою — з борту або з мережі."""
    if uri.startswith('mftp://'):
        return ftp_download(link, '/' + uri[len('mftp://'):].lstrip('/'))
    if uri.startswith(('http://', 'https://')):
        try:
            return urlopen(uri, timeout=30).read()
        except Exception as exc:
            print('мережа:', exc, file=sys.stderr)
            return None
    return None


def fetch_cached(link, meta_type, sources):
    """Джерела по черзі, для кожного: кеш → завантаження.
    CRC у кожного джерела свій, тож і тег кешу свій."""
    for uri, crc in sources:
        if not uri:
            continue
        tag = None if crc is None else cache_tag(meta_type, crc)
        hit = cache_load(tag)
        if hit is not None:
            return maybe_decompress(hit)
        raw = fetch(link, uri)
        if raw:
            cache_store(tag, raw)                    # кешуємо СТИСНЕНИЙ оригінал
            return maybe_decompress(raw)
    return None


def maybe_decompress(data):
    """Стиснення пізнається за вмістом: у самій адресі його може бути не видно."""
    return lzma.decompress(data) if data.startswith(XZ_MAGIC) else data


def sources_for(general, meta_type):
    """Пари «адреса, CRC» одного виду опису: спершу головна, потім запасна."""
    for entry in general.get('metadataTypes', []):
        if entry.get('type') == meta_type:
            return [(entry.get('uri', ''),         entry.get('fileCrc')),
                    (entry.get('uriFallback', ''), entry.get('fileCrcFallback'))]
    return None
