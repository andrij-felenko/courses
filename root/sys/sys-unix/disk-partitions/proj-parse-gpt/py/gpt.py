#!/usr/bin/env python3
"""gpt.py — перелік розділів GPT із файлу-образу або блокового пристрою.
   Запуск: sudo ./gpt.py /dev/sda      ./gpt.py disk.img [розмір-сектора]"""
import fcntl, os, stat, struct, sys, uuid, zlib

HDR = "<8sIIII QQQQ 16s Q III"          # 92 байти заголовка
ENT = "<16s16s QQQ 72s"                 # 128 байтів одного запису
BLKSSZGET, BLKGETSIZE64 = 0x1268, 0x80081272


def geometry(f):
    """У пристрою сектор і місткість питаємо в ядра, у файлу — беремо розмір."""
    st = os.fstat(f.fileno())
    if stat.S_ISBLK(st.st_mode):
        ss = struct.unpack("i", fcntl.ioctl(f, BLKSSZGET, b"\0" * 4))[0]
        size = struct.unpack("Q", fcntl.ioctl(f, BLKGETSIZE64, b"\0" * 8))[0]
        return ss, size
    return 512, st.st_size


def read_header(f, lba, ss):
    """Прочитати й перевірити заголовок у секторі lba. Не сходиться — None."""
    f.seek(lba * ss)
    sect = f.read(ss)
    if len(sect) < 92 or sect[:8] != b"EFI PART":
        return None
    (_sig, _rev, hsize, hcrc, _res, my, alt, first, last,
     disk, ent_lba, n, esz, acrc) = struct.unpack_from(HDR, sect)
    if not 92 <= hsize <= ss:
        return None
    body = bytearray(sect[:hsize])
    body[16:20] = b"\0\0\0\0"                   # поле суми на час рахунку — нулі
    if zlib.crc32(body) & 0xFFFFFFFF != hcrc:
        return None
    if my != lba:                               # заголовок мусить знати власне місце
        return None
    return dict(alt=alt, first=first, last=last, disk=uuid.UUID(bytes_le=disk),
                ent_lba=ent_lba, n=n, esz=esz, acrc=acrc)


def read_entries(f, h, ss):
    if h["esz"] < 128 or h["esz"] % 128 or not 0 < h["n"] <= 4096:
        raise ValueError("неправдоподібні розміри масиву записів")
    f.seek(h["ent_lba"] * ss)
    raw = f.read(h["n"] * h["esz"])
    if len(raw) != h["n"] * h["esz"]:
        raise ValueError("масив записів обірвано")
    if zlib.crc32(raw) & 0xFFFFFFFF != h["acrc"]:
        raise ValueError("CRC32 масиву записів не сходиться")
    for i in range(h["n"]):
        tg, pg, a, b, attrs, nm = struct.unpack_from(ENT, raw, i * h["esz"])
        if tg == b"\0" * 16:                    # порожній запис
            continue
        yield i + 1, uuid.UUID(bytes_le=tg), uuid.UUID(bytes_le=pg), a, b, attrs, \
            nm.decode("utf-16-le").split("\0")[0]


def main(path, ss_arg=0):
    with open(path, "rb") as f:
        ss, size = geometry(f)
        ss = ss_arg or ss
        last = size // ss - 1
        h, src = read_header(f, 1, ss), "основна"
        if h is None:                           # основна копія не зійшлася
            h, src = read_header(f, last, ss), "РЕЗЕРВНА"
        if h is None:
            sys.exit("GPT не знайдено: жодна з копій не сходиться")
        print("сектор %d Б · останній LBA %d · копія таблиці: %s" % (ss, last, src))
        print("диск %s · записів %d по %d Б\n" % (str(h["disk"]).upper(), h["n"], h["esz"]))
        for n, tg, pg, a, b, attrs, name in read_entries(f, h, ss):
            mib = (b - a + 1) * ss / 1048576.0   # останній сектор — ВКЛЮЧНО
            print("%2d %10d %10d %9.1f МіБ  %s  %s" % (n, a, b, mib, str(tg).upper(), name))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0)
