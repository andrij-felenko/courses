def metadata_crc32(data):
    """CRC32 метаданих: поліном як у zip, але регістр стартує з нуля
    й наприкінці не інвертується. zlib робить обидва інвертування —
    обидва тут і скасовуються, звідси два 0xFFFFFFFF."""
    return zlib.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF


def cache_tag(meta_type, crc, translation=False):
    """Ім'я запису в кеші: CRC, вид опису, ознака перекладу — і більше нічого."""
    return '%08x_%02i_%i' % (crc, meta_type, int(translation))
