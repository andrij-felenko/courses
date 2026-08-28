#!/usr/bin/env python3
"""pfn.py — у який фізичний кадр дивиться ця віртуальна адреса.
   sudo ./pfn.py 1234 0x7f2a4c014000
"""
import os, struct, sys

PAGE = os.sysconf("SC_PAGE_SIZE")

def read_u64(path, off):
    with open(path, "rb") as f:
        f.seek(off)
        return struct.unpack("=Q", f.read(8))[0]   # порядок байтів — рідний

pid, va = sys.argv[1], int(sys.argv[2], 0)

entry = read_u64(f"/proc/{pid}/pagemap", va // PAGE * 8)
if not entry & (1 << 63):
    sys.exit("кадру немає: сторінка не в пам'яті")

pfn = entry & ((1 << 55) - 1)
if not pfn:
    sys.exit("кадр 0 — найпевніше бракує CAP_SYS_ADMIN")

print(f"кадр {pfn:#x}, відображень {read_u64('/proc/kpagecount', pfn * 8)}")
