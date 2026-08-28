import struct
import zlib
import sys

def parse_firmware_binary(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    # Пошук магічного числа 'VERS' у бінарному файлі
    offset = data.find(b"VERS")
    if offset == -1:
        raise ValueError("Секцію .version_header не знайдено в двійковому файлі!")

    header_bytes = data[offset : offset + 72]
    if len(header_bytes) < 72:
        raise ValueError("Пошкоджений або усічений заголовок версії!")

    # Розпакування формату Little-Endian:
    # I (magic), H (struct_ver), H (flags), H (major), H (minor),
    # H (patch), H (reserved), I (commits), 8s (sha), Q (timestamp),
    # 32s (tag), I (crc32)
    fmt = "<IHHHHHHI8sQ32sI"
    fields = struct.unpack(fmt, header_bytes)

    magic, s_ver, flags, maj, min_, patch, res, commits, sha, ts, tag, crc = fields

    # Валідація контрольної суми CRC32 від перших 68 байтів
    computed_crc = zlib.crc32(header_bytes[:68])
    if crc != computed_crc:
        raise ValueError(f"Помилка CRC32: очікувалося {hex(computed_crc)}, отримано {hex(crc)}")

    is_dirty = bool(flags & 0x0001)
    tag_clean = tag.decode("utf-8", errors="replace").rstrip("\0")
    sha_clean = sha.decode("utf-8", errors="replace").rstrip("\0")

    return {
        "version": f"{maj}.{min_}.{patch}",
        "commits_ahead": commits,
        "git_sha": sha_clean,
        "tag": tag_clean,
        "is_dirty": is_dirty,
        "timestamp_unix": ts,
    }
