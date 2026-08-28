import struct, zlib

SEC = 512                          # логічний блок; на 4Kn-диску тут 4096

with open("/dev/sda", "rb") as dev:
    dev.seek(1 * SEC)
    hdr = dev.read(SEC)

    sig, rev, hsize, hcrc = struct.unpack_from("<8s I I I", hdr, 0)
    if sig != b"EFI PART" or rev != 0x00010000:
        raise SystemExit("не GPT")
    if not 92 <= hsize <= SEC:
        raise SystemExit("HeaderSize поза межами")

    zeroed = hdr[:16] + b"\x00" * 4 + hdr[20:hsize]
    if zlib.crc32(zeroed) != hcrc:
        raise SystemExit("заголовок побито")

    entry_lba, count, esize, acrc = struct.unpack_from("<Q I I I", hdr, 72)
    dev.seek(entry_lba * SEC)
    if zlib.crc32(dev.read(count * esize)) != acrc:
        raise SystemExit("масив записів побито")
