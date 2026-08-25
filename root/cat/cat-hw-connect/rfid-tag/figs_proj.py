# -*- coding: utf-8 -*-
"""Фігури вставки-проєкту «Читаємо й пишемо брелок» (catalog/connect/rfid/rfid-tag).
Окремий файл, щоб не чіпати основний figs.py теми. Запуск: python figs_proj.py → ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: адресація блоків — з номера сектора в абсолютний номер блока ─────
# Головна плутанина при записі: «блок 4» це насправді блок 0 сектора 1.
# Абсолютний блок = сектор*4 + локальний; трейлер сектора S = S*4 + 3.
def fig_blockmap():
    W, H = 780, 430
    parts = []
    parts.append(text(390, 46, "абсолютний блок = сектор · 4 + локальний   "
                               "(трейлер сектора S = S·4 + 3)",
                     12, MUTED, "middle"))

    x0, y0 = 60, 78
    cw, ch = 118, 40          # клітинка блока
    lgap = 8                  # проміжок між локальними блоками
    sgap = 40                 # проміжок між секторами

    def sector(x, snum):
        out = [text(x + cw / 2, y0 - 12, "Сектор %d" % snum, 12, INK, "middle", bold=True)]
        for loc in range(4):
            absn = snum * 4 + loc
            y = y0 + loc * (ch + lgap)
            is_tr = (loc == 3)
            is_uid = (snum == 0 and loc == 0)
            if is_uid:
                fill, col, lbl = "#fdecea", POS, "блок 0\nUID (RO)"
            elif is_tr:
                fill, col, lbl = "#fdf0e0", "#d68910", "трейлер\nключі A/B"
            else:
                fill, col, lbl = "#eef2f7", INK, "дані"
            out.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=1.6, rx=5))
            # локальний номер зліва в клітинці, абсолютний — праворуч великим
            out.append(text(x + 8, y + ch / 2 + 4, "лок.%d" % loc, 10, MUTED, "start"))
            out.append(text(x + cw - 10, y + ch / 2 + 5, "#%d" % absn, 14, col, "end", bold=True))
        return out

    parts += sector(x0, 0)
    parts += sector(x0 + (cw + sgap), 1)
    # три крапки
    dotx = x0 + 2 * (cw + sgap) + 22
    parts.append(text(dotx, y0 + 1.5 * (ch + lgap), "···", 24, MUTED, "middle"))
    parts += sector(x0 + 2 * (cw + sgap) + 52, 15)

    # підпис-підказка знизу, рознесений
    yb = y0 + 4 * (ch + lgap) + 26
    parts.append(fitbox(60, yb, 330, 58,
                        "«Прочитай блок 4» = сектор 1, локальний 0.\n"
                        "Спершу автентифікуйся будь-яким блоком\n"
                        "цього сектора — відкриється весь сектор.",
                        size=11, fill="#eef2f7", stroke=INK, sw=1.2, color=INK))
    parts.append(fitbox(410, yb, 330, 58,
                        "Трейлер (лок.3, тобто #3, #7, #11 …) —\n"
                        "не пиши в нього наосліп: там ключі й біти\n"
                        "доступу. Помилка тут замикає сектор назавжди.",
                        size=11, fill="#fdf0e0", stroke="#d68910", sw=1.2, color=INK))

    render(os.path.join(IMG, "blockmap.svg"), W, H, *parts,
           title="Адресація блоків MIFARE Classic 1K: сектор → абсолютний номер")


# ── Фігура 2: життєвий цикл шифрування — чому без StopCrypto1 читач зависає ────
# Auth підіймає CRYPTO1 у читачі; поки він піднятий, наступна мітка не читається.
# Ланцюг: пошук → auth → read/write → StopCrypto1 → HaltA → знову вільно.
def fig_lifecycle():
    W, H = 800, 300
    parts = []

    y = 130
    bw, bh = 128, 62
    xs = [40, 210, 380, 560]

    def box(i, title, sub, fill, col):
        x = xs[i]
        parts.append(fitbox(x, y - bh / 2, bw, bh, title + "\n" + sub,
                            size=11, fill=fill, stroke=col, sw=1.8, color=INK, bold=True))
        return x

    box(0, "PICC_ReadCardSerial", "є UID", "#eef2f7", INK)
    box(1, "PCD_Authenticate", "CRYPTO1 ↑", "#fdecea", POS)
    box(2, "MIFARE_Read /\nWrite", "дані течуть", "#eafaf1", FIELD)
    box(3, "PCD_StopCrypto1", "CRYPTO1 ↓", "#eaf0fd", NEG)

    for i in range(3):
        parts.append(arrow(xs[i] + bw, y, xs[i + 1], y, color=INK, sw=2.0))

    # HaltA праворуч від StopCrypto1
    parts.append(text(xs[3] + bw / 2, y + bh / 2 + 20, "далі PICC_HaltA()", 11, MUTED, "middle"))

    # зона «шифрування підняте» — підсвітити проміжок від auth до stop
    zx1 = xs[1] + bw / 2
    zx2 = xs[3] + bw / 2
    parts.append(rect(zx1, y - bh / 2 - 34, zx2 - zx1, 20, fill="#fdf6ec", stroke="#d68910", sw=1.0, rx=4))
    parts.append(text((zx1 + zx2) / 2, y - bh / 2 - 20, "поки CRYPTO1 піднятий — читач зайнятий",
                     10, "#b9770e", "middle"))

    # застереження знизу
    parts.append(fitbox(40, y + bh / 2 + 40, 720, 40,
                        "Забув StopCrypto1 — CRYPTO1 лишається піднятим, і НАСТУПНА мітка не читається "
                        "(мовчазний «плаваючий» баг). Викликай його ЗАВЖДИ, навіть після невдалого читання.",
                        size=11, fill="#fff", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(IMG, "lifecycle.svg"), W, H, *parts,
           title="Цикл шифрування: auth підіймає CRYPTO1, StopCrypto1 його опускає")


fig_blockmap()
fig_lifecycle()
print("Done. SVG in", IMG)
