# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOOD = "#eaf7ee"
BAD  = "#fdecea"
NEUT = "#f4f6f8"


# ── Фіг. 1: три види замків — уся різниця в тому, кого ядро вважає власником ──
def fig_owners():
    W, H = 1060, 620
    p = []

    LX, LW = 30, 300          # колонка ситуацій
    CW, GAP = 228, 8          # колонки видів
    C0 = LX + LW + GAP

    def cx(i):
        return C0 + i * (CW + GAP)

    heads = ["flock\n(власник — опис)",
             "fcntl F_SETLK\n(власник — процес)",
             "fcntl F_OFD_SETLK\n(власник — опис)"]
    for i, h in enumerate(heads):
        p.append(fitbox(cx(i), 56, CW, 58, h, size=14, bold=True,
                        fill="#eef3fb", stroke=NEG, sw=1.6))
    p.append(text(LX + LW - 8, 92, "ситуація", size=14, color=MUTED,
                  anchor="end", bold=True))

    rows = [
        ("Дитина після fork",
         ("той самий замок", GOOD), ("не успадковує", BAD), ("той самий замок", GOOD)),
        ("Другий open того самого\nфайлу в тому ж процесі",
         ("конфлікт сам із собою", NEUT), ("конфлікту немає", NEUT), ("конфлікт сам із собою", NEUT)),
        ("Два потоки одного процесу",
         ("залежить від опису", NEUT), ("конфлікту немає ніколи", BAD), ("конфлікт, якщо описи різні", GOOD)),
        ("Стороння бібліотека\nзакрила свій fd на цей файл",
         ("замок живий", GOOD), ("усі замки зникли", BAD), ("замок живий", GOOD)),
        ("Що можна замкнути",
         ("лише весь файл", NEUT), ("діапазон байтів", GOOD), ("діапазон байтів", GOOD)),
        ("Перехід SH → EX",
         ("не атомарний", BAD), ("атомарний", GOOD), ("атомарний", GOOD)),
        ("Через NFS",
         ("емуляція діапазоном\nна весь файл", NEUT), ("на сервері", NEUT), ("на сервері", NEUT)),
    ]

    y = 128
    RH = 62
    for label, *cells in rows:
        p.append(fitbox(LX, y, LW, RH, label, size=13, pad=10,
                        fill="#ffffff", stroke=MUTED, sw=1.2))
        for i, (txt, col) in enumerate(cells):
            p.append(fitbox(cx(i), y, CW, RH, txt, size=13, pad=8,
                            fill=col, stroke=MUTED, sw=1.2))
        y += RH + 6

    render(os.path.join(OUT, "lock-owners.svg"), W, H, *p,
           title="Кого ядро вважає власником замка — і що з цього випливає")


# ── Фіг. 2: чужий close знімає ваш POSIX-замок ──────────────────────────────
def fig_close_drops_lock():
    W, H = 1060, 700
    p = []

    AX, AW = 66, 350
    BX, BW = 440, 300
    SX, SW = 774, 250

    p.append(text(AX + AW / 2, 74, "ваш код", size=15, bold=True))
    p.append(text(BX + BW / 2, 74, "стороння бібліотека", size=15, bold=True))
    p.append(text(SX + SW / 2, 74, "стан вашого замка", size=15, bold=True))

    p.append(text(36, 100, "час", size=13, color=MUTED))
    p.append(arrow(36, 116, 36, 596, color=MUTED, sw=1.6))

    RH = 54
    ys = [138, 218, 298, 378, 458, 538]

    steps = [
        (0, 'open("db", O_RDWR) → fd 3', ("вільно", NEUT)),
        (0, "fcntl(fd 3, F_SETLK, WRITE)", ("тримаєте його ви", GOOD)),
        (1, 'open("db", O_RDONLY) → fd 7', ("тримаєте його ви", GOOD)),
        (1, "fstat(fd 7, &st)", ("тримаєте його ви", GOOD)),
        (1, "close(fd 7)", ("ядро зняло ВСІ ваші\nзамки на цей файл", BAD)),
        (0, "write(fd 3, …) — без помилки", ("вільно, пише будь-хто", BAD)),
    ]

    for (lane, txt, (st, col)), y in zip(steps, ys):
        x, w = (AX, AW) if lane == 0 else (BX, BW)
        fill = "#eef3fb" if lane == 0 else "#f7f2ea"
        p.append(fitbox(x, y, w, RH, txt, size=14, pad=10,
                        fill=fill, stroke=INK if lane == 0 else MUTED, sw=1.4))
        p.append(fitbox(SX, y, SW, RH, st, size=13, pad=8,
                        fill=col, stroke=MUTED, sw=1.2))

    p.append(line(BX + BW / 2, ys[4] + RH, SX, ys[4] + RH / 2, color=POS, sw=2, dash="5 4"))

    p.append(text(66, 622, "fd 3 лишається відкритим і робочим — зникає тільки замок, "
                           "і жоден виклик про це не повідомляє.",
                  size=14, color=POS, anchor="start"))
    p.append(text(66, 652, "З F_OFD_SETLK крок close(fd 7) нічого не змінює: "
                           "замок належить опису, який створив ВАШ open.",
                  size=14, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "close-drops-lock.svg"), W, H, *p,
           title="Чому POSIX-замок зникає від чужого close")


# ── Фіг. 3: діапазони байтів і розрізання замка ─────────────────────────────
def fig_byte_ranges():
    W, H = 1020, 470
    p = []
    X0, X1 = 96, 936
    SPAN = X1 - X0
    TOTAL = 4096

    def bx(b):
        return X0 + b * SPAN / TOTAL

    def bar(y, segs, h=42):
        out = [rect(X0, y, SPAN, h, fill="#ffffff", stroke=MUTED, sw=1.4)]
        for b0, b1, col, stroke in segs:
            out.append(rect(bx(b0), y, bx(b1 + 1) - bx(b0), h,
                            fill=col, stroke=stroke, sw=1.6))
        return out

    p.append(text(X0, 84, "було", size=14, color=MUTED, anchor="start", bold=True))
    p.append(text(bx(1024), 112, "A: замок на запис, байти 0–2047", size=13))
    p.append(text(bx(3584), 112, "B: замок на читання, 3072–4095", size=13))
    p.extend(bar(126, [(0, 2047, "#fdecea", POS), (3072, 4095, "#eaf0fd", NEG)]))

    p.append(text(X0, 226, "після F_UNLCK на байтах 512–1535", size=14, color=MUTED,
                  anchor="start", bold=True))
    p.append(text(bx(256), 254, "0–511", size=13))
    p.append(text(bx(1024), 254, "вільно", size=13, color=MUTED))
    p.append(text(bx(1792), 254, "1536–2047", size=13))
    p.append(text(bx(3584), 254, "без змін", size=13))
    p.extend(bar(268, [(0, 511, "#fdecea", POS), (1536, 2047, "#fdecea", POS),
                       (3072, 4095, "#eaf0fd", NEG)]))

    p.append(line(X0, 336, X1, 336, color=MUTED, sw=1.2))
    for b in (0, 1024, 2048, 3072, 4096):
        x = bx(min(b, TOTAL - 1)) if b == TOTAL else bx(b)
        p.append(line(x, 330, x, 342, color=MUTED, sw=1.2))
        p.append(text(x, 360, str(b), size=12, color=MUTED))
    p.append(text((X0 + X1) / 2, 386, "зміщення у файлі, байти", size=13, color=MUTED))

    p.append(text(X0, 422, "Один замок став двома окремими записами в ядрі — "
                           "саме на цьому розрізанні й вичерпується їх запас (ENOLCK).",
                  size=14, anchor="start"))
    p.append(text(X0, 448, "Замок на весь файл — це просто l_start = 0, l_len = 0: "
                           "від початку й до кінця, хоч би куди той кінець доріс.",
                  size=14, anchor="start", color=MUTED))

    render(os.path.join(OUT, "byte-ranges.svg"), W, H, *p,
           title="Замок на діапазон байтів і що з ним робить часткове зняття")


# ── Фіг. 4: геометрія діапазону — l_whence / l_start / l_len і size у lockf ──
def fig_region_geometry():
    W, H = 1080, 700
    p = []

    LX, LW = 28, 392
    BX0, BXE = 440, 1044
    SPAN = BXE - BX0
    TOTAL = 5000          # 0…4000 — сам файл, далі — за його кінцем
    EOFB = 4000

    def bx(b):
        return BX0 + b * SPAN / TOTAL

    p.append(text(LX + LW / 2, 76, "заявка", size=14, bold=True, color=MUTED))

    # вісь зміщень
    p.append(line(bx(0), 92, bx(TOTAL), 92, color=MUTED, sw=1.2))
    for b, lab in ((0, "0"), (1000, "1000"), (2000, "2000"),
                   (3000, "3000"), (EOFB, "EOF = 4000")):
        p.append(line(bx(b), 86, bx(b), 98, color=MUTED, sw=1.2))
        p.append(text(bx(b), 76, lab, size=12, color=MUTED))

    rows = [
        ("l_whence = SEEK_SET\nl_start = 1000, l_len = 1000\n→ байти 1000 … 1999",
         1000, 2000, False, "#eaf0fd", NEG),
        ("l_whence = SEEK_SET\nl_start = 2000, l_len = 0\n→ 2000 … і далі без межі",
         2000, TOTAL, True, "#eaf0fd", NEG),
        ("l_whence = SEEK_SET\nl_start = 3000, l_len = −1000\n→ байти 2000 … 2999",
         2000, 3000, False, "#eaf0fd", NEG),
        ("l_whence = SEEK_END\nl_start = 0, l_len = 0\n→ зараз нічого, дописане — під замком",
         EOFB, TOTAL, True, "#eaf0fd", NEG),
        ("lockf(fd, F_LOCK, 1000)\nпоточна позиція = 1500\n→ байти 1500 … 2499",
         1500, 2500, False, "#fdecea", POS),
        ("lockf(fd, F_LOCK, −500)\nпоточна позиція = 1500\n→ байти 1000 … 1499",
         1000, 1500, False, "#fdecea", POS),
    ]

    y, RH = 116, 76
    for label, b0, b1, endless, fill, stroke in rows:
        p.append(fitbox(LX, y, LW, RH, label, size=13, pad=9,
                        fill="#ffffff", stroke=MUTED, sw=1.2))
        by, bh = y + 17, RH - 34
        cuts = sorted({0, b0, b1, EOFB, TOTAL})
        for s, e in zip(cuts, cuts[1:]):
            inside = s >= b0 and e <= b1
            p.append(rect(bx(s), by, bx(e) - bx(s), bh,
                          fill=fill if inside else (NEUT if s >= EOFB else "#ffffff"),
                          stroke=stroke if inside else MUTED,
                          sw=1.8 if inside else 1.1, rx=0))
        if endless:
            p.append(arrow(bx(TOTAL) - 26, by + bh / 2, bx(TOTAL) + 8, by + bh / 2,
                           color=stroke, sw=2))
        y += RH + 8

    p.append(text(LX, y + 30, "Ліворуч від EOF — байти, що вже є; праворуч — ті, "
                              "що з'являться, коли файл доросте.",
                  size=14, anchor="start"))
    p.append(text(LX, y + 56, "Синє — struct flock: відлік від точки, заданої l_whence. "
                              "Червоне — lockf: відлік ЗАВЖДИ від поточної позиції.",
                  size=14, anchor="start", color=MUTED))

    render(os.path.join(OUT, "lock-region.svg"), W, H, *p,
           title="Який саме шматок файлу замикає заявка")


fig_owners()
fig_close_drops_lock()
fig_byte_ranges()
fig_region_geometry()
print("ok")
