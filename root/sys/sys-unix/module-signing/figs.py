# -*- coding: utf-8 -*-
"""Фігури до теми «Підпис модулів ядра»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT_F, SOFT_S = "#eaf0fd", NEG
BAD_F,  BAD_S  = "#fdecea", POS
OK_F,   OK_S   = "#e8f7ee", FIELD
CALM_F         = "#f4f6f8"


# ── 1. Розкладка підписаного .ko ────────────────────────────────────────────
def layout():
    W, H = 960, 340
    p = []

    x0, x1 = 50, 900
    top, bot = 110, 190

    segs = [
        (x0,  520, "образ модуля (ELF)", "усе, що дає модулю сенс", CALM_F, LINE),
        (520, 740, "підпис PKCS#7", "sig_len байтів", SOFT_F, NEG),
        (740, 830, "опис", "12 Б", OK_F, FIELD),
        (830, x1,  "маркер", "28 Б", OK_F, FIELD),
    ]
    for a, b, t1, t2, f, s in segs:
        p.append(fitbox(a, top, b - a, bot - top, t1 + "\n" + t2,
                        size=15, fill=f, stroke=s, sw=1.8))

    p.append(text(x0, 90, "початок файлу", size=13, color=MUTED, anchor="start"))
    p.append(text(x1, 90, "кінець файлу", size=13, color=MUTED, anchor="end"))

    # ядро читає з кінця
    p.append(arrow(880, 55, 560, 55, color=MUTED))
    p.append(text(720, 40, "ядро розбирає файл з кінця", size=14, color=MUTED))

    # дужка «що хешується»
    p.append(line(x0, 215, 520, 215, color=FIELD, sw=2))
    p.append(line(x0, 215, x0, 200, color=FIELD, sw=2))
    p.append(line(520, 215, 520, 200, color=FIELD, sw=2))
    p.append(text(285, 245, "хеш рахують рівно по цих байтах", size=15, color=FIELD, bold=True))

    p.append(line(520, 215, x1, 215, color=MUTED, sw=2, dash="5,4"))
    p.append(line(x1, 215, x1, 200, color=MUTED, sw=2))
    p.append(text(710, 245, "у хеш не входить", size=15, color=MUTED))

    p.append(text(480, 300,
                  "довжина тіла = розмір файлу − 28 − 12 − sig_len",
                  size=15, color=INK))

    render(os.path.join(OUT, 'signed-module-layout.svg'), W, H, *p)


# ── 2. Кільця ключів і хто на них спирається ───────────────────────────────
def keyrings():
    W, H = 1020, 480
    p = []

    src_x, src_w = 30, 300
    ring_x, ring_w = 390, 260
    use_x, use_w = 720, 270

    rows = [
        (60,  "ключ, вбудований\nу збірку ядра", ".builtin_trusted_keys", OK_F, FIELD),
        (170, "ключ, підписаний\nуже довіреним ключем", ".secondary_trusted_keys", OK_F, FIELD),
        (280, "MOK + mokutil --trust-mok\n(лише CA-ключі)", ".machine", OK_F, FIELD),
        (390, "UEFI db і решта MOK", ".platform", SOFT_F, NEG),
    ]
    bh = 76
    for y, s, ring, f, st in rows:
        p.append(fitbox(src_x, y, src_w, bh, s, size=14, fill=CALM_F, stroke=MUTED))
        p.append(arrow(src_x + src_w + 8, y + bh / 2, ring_x - 8, y + bh / 2, color=MUTED))
        p.append(fitbox(ring_x, y, ring_w, bh, ring, size=15, fill=f, stroke=st, sw=2, bold=True))

    # споживач
    p.append(fitbox(use_x, 70, use_w, 250,
                    "перевірка підпису\nмодуля\n\nшукає сертифікат\nпідписанта тут",
                    size=15, fill=OK_F, stroke=FIELD, sw=2))
    for y in (60, 170, 280):
        p.append(arrow(ring_x + ring_w + 8, y + bh / 2, use_x - 8, y + bh / 2, color=FIELD))

    p.append(fitbox(use_x, 390, use_w, bh, "kexec та IMA — так,\nмодулі — ні",
                    size=14, fill=SOFT_F, stroke=NEG))
    p.append(arrow(ring_x + ring_w + 8, 390 + bh / 2, use_x - 8, 390 + bh / 2, color=NEG))

    render(os.path.join(OUT, 'trusted-keyrings.svg'), W, H, *p)


# ── 3. Що вирішує ядро при завантаженні ────────────────────────────────────
def verdict():
    W, H = 1220, 440
    p = []

    cw, ch, cy = 190, 74, 45
    checks = [
        (110, "маркер\nу кінці?"),
        (330, "опис і CMS\nрозібрано?"),
        (550, "ключ\nзнайдено?"),
        (770, "хеш\nзбігся?"),
    ]
    for cx, s in checks:
        p.append(fitbox(cx - cw / 2, cy, cw, ch, s, size=15, fill=CALM_F, stroke=LINE, sw=1.8))
    for a, b in zip(checks, checks[1:]):
        p.append(arrow(a[0] + cw / 2 + 6, cy + ch / 2, b[0] - cw / 2 - 6, cy + ch / 2, color=FIELD))
    p.append(arrow(770 + cw / 2 + 6, cy + ch / 2, 1000 - 100 - 6, cy + ch / 2, color=FIELD))
    p.append(fitbox(1000 - 100, cy, 200, ch, "модуль\nзлінковано",
                    size=15, fill=OK_F, stroke=FIELD, sw=2, bold=True))

    ow, oh, oy = 210, 96, 190
    outs = [
        (110, "-ENODATA\nпідпису немає", SOFT_F, NEG),
        (330, "-EBADMSG\nсміття замість підпису\nфатально завжди", BAD_F, POS),
        (550, "-ENOKEY\nключа немає в кільцях", SOFT_F, NEG),
        (770, "-EKEYREJECTED\nпідпис не збігся\nфатально завжди", BAD_F, POS),
    ]
    for cx, s, f, st in outs:
        p.append(arrow(cx, cy + ch + 4, cx, oy - 6, color=st))
        p.append(fitbox(cx - ow / 2, oy, ow, oh, s, size=14, fill=f, stroke=st, sw=1.8))
    p.append(text(150, 165, "ні", size=13, color=MUTED, anchor="start"))

    pw, ph, py = 470, 96, 330
    px = 330 - pw / 2
    p.append(fitbox(px, py, pw, ph,
                    "sig_enforce увімкнено?\nтак → відмова, -EKEYREJECTED\nні → мітка E, модуль вантажиться",
                    size=15, fill=SOFT_F, stroke=NEG, sw=2))
    p.append(arrow(110, oy + oh + 4, 230, py - 6, color=NEG))
    p.append(arrow(550, oy + oh + 4, 440, py - 6, color=NEG))

    render(os.path.join(OUT, 'verify-verdict.svg'), W, H, *p)


layout()
keyrings()
verdict()
print("ok")
