#!/usr/bin/env python3
"""Таблиця initcall зібраного ядра: рівень, номер у рівні, ім'я функції.
   ./initcalls.py vmlinux System.map [ширина-запису: 4 (зсув) або 8 (покажчик)]"""
import bisect, os, subprocess, sys, tempfile

LEVELS = ["pure", "core", "postcore", "arch", "subsys", "fs", "device", "late"]


def symbols(path):
    """System.map → адреси й імена, відсортовані для пошуку «хто тут живе»."""
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.split(None, 2)
            if len(parts) == 3:
                rows.append((int(parts[0], 16), parts[2].strip()))
    rows.sort()
    return [a for a, _ in rows], [n for _, n in rows]


def section_vma(vmlinux, name):
    """Початкова адреса секції — щоб перевести адресу запису в зсув у файлі."""
    out = subprocess.run(["objdump", "-h", vmlinux],
                         capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 4 and f[1] == name:
            return int(f[3], 16)
    raise SystemExit("у файлі немає секції " + name)


def main(vmlinux, sysmap, width):
    addrs, names = symbols(sysmap)
    mark = dict(zip(names, addrs))          # межі мають унікальні імена
    vma = section_vma(vmlinux, ".init.data")

    tmp = tempfile.NamedTemporaryFile(suffix=".bin", delete=False)
    tmp.close()
    subprocess.run(["objcopy", "-O", "binary", "--only-section=.init.data",
                    vmlinux, tmp.name], check=True)
    with open(tmp.name, "rb") as f:
        blob = f.read()
    os.unlink(tmp.name)

    ranges = [("early", mark["__initcall_start"], mark["__initcall0_start"])]
    for i, level in enumerate(LEVELS):
        stop = "__initcall_end" if i == 7 else "__initcall%d_start" % (i + 1)
        ranges.append((level, mark["__initcall%d_start" % i], mark[stop]))
    rootfs = mark.get("__initcallrootfs_start")

    for level, start, stop in ranges:
        for k, at in enumerate(range(start, stop, width)):
            raw = blob[at - vma: at - vma + width]
            target = (at + int.from_bytes(raw, "little", signed=True)
                      if width == 4 else int.from_bytes(raw, "little"))
            i = bisect.bisect_right(addrs, target) - 1
            # Запис мусить указувати РІВНО на початок функції; інакше ширина не та.
            note = "" if addrs[i] == target else "   ← не на межі символу"
            tag = level + ("/rootfs" if rootfs and level == "fs"
                           and at >= rootfs else "")
            print("%-12s %3d  %s%s" % (tag, k, names[i], note))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 4)
