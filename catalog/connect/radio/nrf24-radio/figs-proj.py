# -*- coding: utf-8 -*-
"""Фігури для API-вставки proj-nrf24 (catalog/connect/radio). Запуск: python figs-proj.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо). Окремий файл, щоб не чіпати figs.py статті."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура: шість «труб» і як збігаються адреси ──────────────────────────────
# База слухає до 6 адрес одночасно. Труби 0,1 тримають повну 5-байтову адресу;
# труби 2..5 — лише СВІЙ останній байт, а старші 4 позичають у труби 1.
# Ключ до коду: openWritingPipe передавача = openReadingPipe тієї ж адреси на базі.
def fig_pipes():
    W, H = 820, 470
    parts = []

    # ── База (приймач) праворуч: колонка з 6 труб ──
    bx, by, bw = 470, 70, 300
    parts.append(rect(bx, by, bw, 350, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    parts.append(text(bx + bw / 2, by - 16, "База — слухає 6 адрес водночас", 13, INK, "middle", bold=True))

    pipes = [
        ("Труба 0", "E7 E7 E7 E7 E7", "повна 5-байт адреса (+ TX)", POS),
        ("Труба 1", "C2 C2 C2 C2 C2", "повна 5-байт адреса", NEG),
        ("Труба 2", "C2 C2 C2 C2 C3", "тільки останній байт", FIELD),
        ("Труба 3", "C2 C2 C2 C2 C4", "тільки останній байт", FIELD),
        ("Труба 4", "C2 C2 C2 C2 C5", "тільки останній байт", FIELD),
        ("Труба 5", "C2 C2 C2 C2 C6", "тільки останній байт", FIELD),
    ]
    y0, dy = by + 34, 52
    rowy = []
    for i, (name, addr, note, col) in enumerate(pipes):
        y = y0 + i * dy
        rowy.append(y)
        parts.append(circle(bx + 26, y + 14, 7, fill=col, stroke=INK, sw=1.2))
        parts.append(text(bx + 26, y + 18, str(i), 9, BG, "middle", bold=True))
        parts.append(text(bx + 46, y + 10, name, 11, col, "start", bold=True))
        # адреса моноширинно — байти з розрядкою; підсвітити спільні 4 байти труб 2..5
        shared = i >= 2
        parts.append(text(bx + 46, y + 27, addr, 12, INK if not shared else MUTED, "start"))
        if shared:
            # рамка навколо спільних 4 байтів (перші 4 групи по 3 символи)
            parts.append(rect(bx + 43, y + 16, 96, 15, fill="none", stroke=FIELD, sw=1.0, rx=3))
        parts.append(text(bx + 150, y + 27, note, 9, MUTED, "start"))

    # дужка «спільні старші 4 байти від труби 1» — праворуч труб 2..5
    braces_x = bx + bw - 8
    parts.append(line(braces_x, rowy[2] + 6, braces_x, rowy[5] + 22, color=FIELD, sw=2.0))
    parts.append(line(braces_x, rowy[2] + 6, braces_x - 8, rowy[2] + 6, color=FIELD, sw=2.0))
    parts.append(line(braces_x, rowy[5] + 22, braces_x - 8, rowy[5] + 22, color=FIELD, sw=2.0))

    # ── Три передавачі ліворуч ──
    txs = [
        ("Пульт", "E7 E7 E7 E7 E7", "→ труба 0", POS),
        ("Датчик A", "C2 C2 C2 C2 C3", "→ труба 2", FIELD),
        ("Датчик B", "C2 C2 C2 C2 C5", "→ труба 4", FIELD),
    ]
    ty0, tdy = 130, 96
    for i, (name, addr, hit, col) in enumerate(txs):
        y = ty0 + i * tdy
        b, w, h = textbox(120, y, "%s\nwrite → %s" % (name, addr), size=11,
                          fill="#eef2f7", stroke=INK, sw=1.4, color=INK, bold=True, min_w=200)
        parts.append(b)
        # стрілка до відповідної труби бази
        target_y = rowy[[0, 2, 4][i]] + 14
        parts.append(arrow(120 + w / 2, y, bx - 4, target_y, color=col, sw=2.0))
        parts.append(text(120 + w / 2 + (bx - 4 - 120 - w / 2) / 2, y - 8 - i * 4, hit, 9, col, "middle", bold=True))

    parts.append(text(W / 2, H - 14,
                      "Адреса, на яку передавач пише (openWritingPipe), мусить дослівно збігтися з трубою, "
                      "яку база відкрила на читання (openReadingPipe).",
                      10, MUTED, "middle"))

    render(os.path.join(IMG, "pipes.svg"), W, H, *parts,
           title="Шість «труб» nRF24: одна база чує кількох передавачів")


fig_pipes()
print("Done. SVG in", IMG)
