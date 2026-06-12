# -*- coding: utf-8 -*-
"""
figs-r12-history-usb-birth.py — фігури до історії «USB: сім компаній проти зоопарку роз'ємів».

Фіг. 4.12.0.1  fig-r12-0-1-connector-zoo.svg
    Зоопарк роз'ємів 1990-х (ліворуч) → стрілка → один USB-A (праворуч).

Фіг. 4.12.0.2  fig-r12-0-2-usb-timeline-speeds.svg
    Горизонтальний таймлайн: USB 1.0 (1996) → 1.1 (1998) → 2.0 (2000) зі швидкостями.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4.12.0.1  Зоопарк роз'ємів → USB-A
# ─────────────────────────────────────────────────────────────────────────────
def fig_connector_zoo():
    W, H = 820, 400
    frags = []

    # ── Заголовок секції «До USB» ──
    frags.append(text(200, 36, "До USB: сім несумісних інтерфейсів", size=15, bold=True, color=INK))

    # ── Роз'єми (сітка 2×4, ліва половина) ──
    connectors = [
        ("PS/2  (миша)",      "#9b59b6", "круглий, 6 pin"),
        ("PS/2  (клавіатура)","#8e44ad", "круглий, 6 pin"),
        ("DB-9 RS-232",       "#e67e22", "серійний порт"),
        ("DB-25 LPT",         "#d35400", "паралельний, принтер"),
        ("SCSI",              "#c0392b", "жорсткий диск"),
        ("Ігровий / MIDI",    "#27ae60", "джойстик, синтезатор"),
        ("ADB (Apple)",       "#2980b9", "тільки на Mac"),
    ]

    cols = 2
    box_w, box_h = 178, 62
    gap_x, gap_y = 14, 12
    start_x, start_y = 22, 58

    for i, (name, color, subtitle) in enumerate(connectors):
        col = i % cols
        row = i // cols
        cx = start_x + col * (box_w + gap_x) + box_w / 2
        cy = start_y + row * (box_h + gap_y) + box_h / 2

        # рамка кольорова
        frags.append(rect(cx - box_w/2, cy - box_h/2, box_w, box_h,
                          fill="#f8f8f8", stroke=color, sw=2, rx=8))
        # назва
        frags.append(text(cx, cy - 8, name, size=13, bold=True, color=INK))
        # підпис
        frags.append(text(cx, cy + 12, subtitle, size=11, color=MUTED))

    # ── Велика стрілка в центрі ──
    ax1, ay = 406, H / 2
    ax2 = 454
    frags.append(arrow(ax1, ay, ax2, ay, color="#c0392b", sw=5))
    frags.append(text((ax1 + ax2) / 2, ay - 18, "USB замінив", size=12, bold=True, color=POS))
    frags.append(text((ax1 + ax2) / 2, ay + 28, "усі сім", size=12, bold=True, color=POS))

    # ── USB-A праворуч ──
    ux, uy = 628, H / 2
    uw, uh = 230, 110

    frags.append(rect(ux - uw/2, uy - uh/2, uw, uh,
                      fill="#eaf6ff", stroke="#2457d6", sw=3, rx=10))
    frags.append(text(ux, uy - 22, "USB Type-A", size=16, bold=True, color="#2457d6"))
    frags.append(text(ux, uy + 2,  "один роз'єм", size=13, color=INK))
    frags.append(text(ux, uy + 22, "для всіх пристроїв", size=13, color=INK))

    # «USB 1.0, 1996»
    frags.append(text(ux, uy + 42, "USB 1.0 — 1996 р.", size=11, color=MUTED))

    # ── Підпис під правою частиною ──
    frags.append(text(ux, H - 20, "Один стандарт · один кабель · один роз'єм", size=11, color=MUTED))

    render(os.path.join(OUT, 'fig-r12-0-1-connector-zoo.svg'), W, H, *frags)
    print("fig-r12-0-1-connector-zoo.svg — OK")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4.12.0.2  Таймлайн USB 1.0 → 1.1 → 2.0 зі швидкостями
# ─────────────────────────────────────────────────────────────────────────────
def fig_usb_timeline():
    W, H = 820, 340
    frags = []

    # ── Заголовок ──
    frags.append(text(W / 2, 34, "USB набирав швидкість: від 12 Мбіт/с до 480 Мбіт/с за чотири роки",
                      size=15, bold=True))

    # ── Горизонтальна вісь ──
    axis_y = 170
    axis_x1, axis_x2 = 80, 740
    frags.append(line(axis_x1, axis_y, axis_x2, axis_y, color=LINE, sw=2))
    frags.append(arrow(axis_x2 - 2, axis_y, axis_x2, axis_y, color=LINE, sw=2))

    # ── Вузли ──
    nodes = [
        {
            "x": 160,
            "year": "1996",
            "version": "USB 1.0",
            "speeds": "Low-Speed: 1.5 Мбіт/с\nFull-Speed: 12 Мбіт/с",
            "color": "#e67e22",
            "note": "Перший реліз.\nМало пристроїв,\nсирі драйвери.",
        },
        {
            "x": 400,
            "year": "1998",
            "version": "USB 1.1",
            "speeds": "Full-Speed: 12 Мбіт/с\n(виправлений)",
            "color": "#27ae60",
            "note": "iMac G3 викинув\nусі легасі-порти.\nWindows 98 підтримав.",
        },
        {
            "x": 640,
            "year": "2000",
            "version": "USB 2.0",
            "speeds": "Hi-Speed: 480 Мбіт/с",
            "color": "#2457d6",
            "note": "Стрибок ×40.\nУніверсальний для\nдисків і відео.",
        },
    ]

    for nd in nodes:
        nx, color = nd["x"], nd["color"]

        # вертикальна ризка
        frags.append(line(nx, axis_y - 12, nx, axis_y + 12, color=color, sw=2.5))

        # рамка версії (вгорі)
        box_frag, bw, bh = textbox(nx, axis_y - 82, nd["version"] + "\n" + nd["year"],
                                   size=13, bold=True, fill="#f0f4ff",
                                   stroke=color, sw=2, pad=10)
        frags.append(box_frag)

        # швидкості під рамкою версії
        frags.append(mtext(nx, axis_y - 38, nd["speeds"], size=11, color=color, anchor="middle"))

        # примітки під віссю
        frags.append(mtext(nx, axis_y + 36, nd["note"], size=11, color=MUTED, anchor="middle"))

    # ── Плашка «мережевий ефект» під правим вузлом ──
    note_x, note_y = 640, H - 26
    frags.append(text(note_x, note_y,
                      "Стандарт перемагає критичною масою: хост + ОС + периферія одночасно",
                      size=10, color=MUTED, anchor="middle"))

    # ── Підпис осі ──
    frags.append(text(axis_x2 + 12, axis_y + 5, "час", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'fig-r12-0-2-usb-timeline-speeds.svg'), W, H, *frags)
    print("fig-r12-0-2-usb-timeline-speeds.svg — OK")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    fig_connector_zoo()
    fig_usb_timeline()
    print("Усі фігури згенеровано.")
