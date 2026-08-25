# -*- coding: utf-8 -*-
"""Фігури до статті «Родина ESP32/ESP8266 (Espressif)».
Дві фігури: дерево родини (Xtensa vs RISC-V) і мапа вибору чипа.
Запуск:  python figs.py   (вивід у ./img/)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

XT = "#2457d6"   # Xtensa — холодний (старша гілка)
RV = "#c0392b"   # RISC-V — гарячий (молодша гілка)


def chipbox(cx, cy, name, sub, accent, w=190, h=52):
    """Рамка чипа: назва (жирна) + дрібний підпис, кольоровий кант."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill="#f4f6f8", stroke=accent, sw=2.2, rx=8)
    out += text(cx, cy - 4, name, size=15, color=accent, bold=True)
    out += text(cx, cy + 15, sub, size=11, color=MUTED)
    return out, w, h


# ── Фігура 1: дерево родини ─────────────────────────────────────────────────
def family_tree():
    W, H = 860, 640
    frags = []

    # корінь
    root_cy = 78
    rb, rw, rh = textbox(W / 2, root_cy, "Espressif Systems\n(безфабрична, Шанхай)",
                         size=14, bold=True, fill="#eef2f7", stroke=INK, sw=2, pad=14)
    frags.append(rb)

    # дві колонки-заголовки гілок
    lx, rx = 235, 625
    head_cy = 175
    lb, lw, lh = textbox(lx, head_cy, "Гілка Xtensa\n(старша, потужніша)",
                         size=13, bold=True, color=XT, fill="#eaf0fd", stroke=XT, sw=2, pad=12)
    rbx, rwx, rhx = textbox(rx, head_cy, "Гілка RISC-V\n(молодша, дешевша)",
                            size=13, bold=True, color=RV, fill="#fdecea", stroke=RV, sw=2, pad=12)
    frags += [lb, rbx]

    # лінії від кореня до заголовків гілок
    frags.append(line(W / 2, root_cy + rh / 2, lx, head_cy - lh / 2, color=XT, sw=2))
    frags.append(line(W / 2, root_cy + rh / 2, rx, head_cy - rhx / 2, color=RV, sw=2))

    # чипи лівої гілки (Xtensa)
    xt_chips = [
        ("ESP8266", "1 ядро L106 · лише Wi-Fi"),
        ("ESP32", "2 ядра LX6 · Wi-Fi + Bluetooth"),
        ("ESP32-S2", "1 ядро LX7 · лише Wi-Fi + USB"),
        ("ESP32-S3", "2 ядра LX7 · Wi-Fi + BLE · нейромережі"),
    ]
    # чипи правої гілки (RISC-V)
    rv_chips = [
        ("ESP32-C3", "1 ядро · Wi-Fi + BLE"),
        ("ESP32-C6", "1 ядро · Wi-Fi 6 + BLE + 15.4"),
        ("ESP32-H2", "1 ядро · без Wi-Fi · BLE + 15.4"),
        ("ESP32-P4", "2 ядра · без радіо · сила"),
    ]

    top = 255
    step = 88
    prev_l = (lx, head_cy + lh / 2)
    prev_r = (rx, head_cy + rhx / 2)
    for i, (nm, sub) in enumerate(xt_chips):
        cy = top + i * step
        cb, cw, ch = chipbox(lx, cy, nm, sub, XT)
        # лінія від попереднього вузла до цього (стовбур гілки)
        frags.append(line(prev_l[0], prev_l[1], lx, cy - ch / 2, color=XT, sw=1.6))
        frags.append(cb)
        prev_l = (lx, cy + ch / 2)
    for i, (nm, sub) in enumerate(rv_chips):
        cy = top + i * step
        cb, cw, ch = chipbox(rx, cy, nm, sub, RV)
        frags.append(line(prev_r[0], prev_r[1], rx, cy - ch / 2, color=RV, sw=1.6))
        frags.append(cb)
        prev_r = (rx, cy + ch / 2)

    # спільний кістяк — стрічка внизу
    band_y = top + 4 * step - 18
    bb, bw, bh = textbox(W / 2, band_y,
                         "Спільний кістяк: радіо на кристалі · зовнішня Flash · 3.3 В · спільні інструменти",
                         size=12, bold=True, fill="#eafaf1", stroke=FIELD, sw=2, pad=12)
    frags.append(bb)

    render(os.path.join(OUT, 'family-tree.svg'), W, H, *frags)


# ── Фігура 2: мапа вибору ───────────────────────────────────────────────────
def choose_map():
    W, H = 900, 620
    frags = []

    # осі
    ox, oy = 120, 520          # початок осей (лівий низ)
    ax_r = 850                 # правий край горизонтальної осі
    ax_t = 90                  # верх вертикальної осі
    frags.append(arrow(ox, oy, ax_r, oy, color=INK, sw=2))      # горизонталь
    frags.append(arrow(ox, oy, ox, ax_t, color=INK, sw=2))      # вертикаль

    # підписи осей
    frags.append(text((ox + ax_r) / 2, oy + 40, "обчислювальна сила  →",
                      size=14, color=INK, bold=True))
    # вертикальний підпис
    frags.append('<text x="%d" y="%d" font-family="%s" font-size="14" fill="%s" '
                 'text-anchor="middle" font-weight="700" transform="rotate(-90 %d %d)">'
                 'радіо  →</text>' % (44, (oy + ax_t) / 2, FONT, INK, 44, (oy + ax_t) / 2))

    # позначки на осях (низ горизонталі)
    frags.append(text(ox + 30, oy + 40, "1 ядро", size=11, color=MUTED, anchor="start"))
    frags.append(text(ax_r - 70, oy + 40, "2 ядра", size=11, color=MUTED))
    # позначки вертикалі
    frags.append(text(ox - 46, oy - 4, "лише", size=10, color=MUTED, anchor="middle"))
    frags.append(text(ox - 46, oy + 10, "Wi-Fi", size=10, color=MUTED, anchor="middle"))
    frags.append(text(ox - 46, ax_t + 30, "Wi-Fi 6", size=10, color=MUTED, anchor="middle"))
    frags.append(text(ox - 46, ax_t + 44, "+ дім", size=10, color=MUTED, anchor="middle"))

    # чипи як точки-рамки: (cx, cy, назва, підпис, колір)
    # x росте з силою, y падає (менший y = вище радіо)
    # координати розставлені так, щоб рамки (176×48) НЕ накладались:
    # між сусідами по горизонталі ≥176 або по вертикалі ≥60.
    chips = [
        (250, 475, "ESP8266", "Wi-Fi за долар", XT),
        (250, 390, "ESP32-C3", "дешевий універсал", RV),
        (480, 320, "ESP32", "робочий кінь", XT),
        (490, 235, "ESP32-S3", "потужний універсал", XT),
        (300, 145, "ESP32-H2", "дім без Wi-Fi", RV),
        (540, 130, "ESP32-C6", "Wi-Fi 6 + дім", RV),
        (760, 320, "ESP32-S2", "1 ядро + USB", XT),
        (800, 475, "ESP32-P4", "сила, без радіо", RV),
    ]
    for cx, cy, nm, sub, col in chips:
        cb, cw, ch = chipbox(cx, cy, nm, sub, col, w=176, h=48)
        frags.append(cb)

    render(os.path.join(OUT, 'choose-map.svg'), W, H, *frags)


# ── Фігура 3: хроніка поколінь (лінія часу) ─────────────────────────────────
def timeline():
    """Вертикальна вісь часу: рік → чип → що додав/прибрав. Дві гілки кольором."""
    W, H = 900, 940
    frags = []

    ax_x = 150                 # вертикальна вісь часу
    top, bot = 70, 900
    frags.append(line(ax_x, top, ax_x, bot, color=INK, sw=2.4))
    frags.append(text(ax_x, top - 22, "час", size=13, color=MUTED, bold=True))
    frags.append(text(ax_x, top - 6, "↓", size=15, color=MUTED))

    # (рік, назва, підпис-що-нового, колір-гілки)
    rows = [
        ("2014", "ESP8266", "1 ядро Xtensa L106 · лише Wi-Fi · без Bluetooth", XT),
        ("2016", "ESP32", "2 ядра LX6 · +Bluetooth Classic +BLE (єдиний із Classic)", XT),
        ("2019", "ESP32-S2", "1 ядро LX7 · лише Wi-Fi · +нативний USB · −Bluetooth", XT),
        ("2020", "ESP32-C3", "перший RISC-V · 1 ядро · Wi-Fi + BLE 5 · дешевий", RV),
        ("2020", "ESP32-S3", "2 ядра LX7 · +BLE 5 +USB +нейроінструкції", XT),
        ("2021", "ESP32-C6", "RISC-V · +Wi-Fi 6 +радіо 802.15.4 (Thread/Zigbee)", RV),
        ("2021", "ESP32-H2", "RISC-V · без Wi-Fi · BLE + 802.15.4 (лише дім)", RV),
        ("2023", "ESP32-P4", "2 ядра RISC-V · сила, відео, камера · без радіо", RV),
    ]
    # рядки з рівномірним кроком; кожен — точка на осі + рік ліворуч + рамка праворуч
    y0 = top + 55
    step = (bot - y0 - 20) / (len(rows) - 1)
    box_x = ax_x + 70          # лівий край рамок
    box_w = 640
    for i, (yr, nm, sub, col) in enumerate(rows):
        cy = y0 + i * step
        # точка на осі
        frags.append(circle(ax_x, cy, 7, fill=col, stroke=col, sw=1.5))
        # рік ліворуч від осі
        frags.append(text(ax_x - 22, cy + 5, yr, size=14, color=col, bold=True, anchor="end"))
        # з'єднувальна риска до рамки
        frags.append(line(ax_x + 7, cy, box_x, cy, color=col, sw=1.6))
        # рамка події: назва (жирна, кольором гілки) + що нового
        bh = 46
        frags.append(rect(box_x, cy - bh / 2, box_w, bh, fill="#f4f6f8", stroke=col, sw=2, rx=8))
        frags.append(text(box_x + 16, cy - 6, nm, size=15, color=col, bold=True, anchor="start"))
        frags.append(text(box_x + 16, cy + 15, sub, size=12, color=INK, anchor="start"))

    # позначка перелому: перехід Xtensa → RISC-V (між S2 і C3).
    # Текст — у власній рамці (textbox), по обидва боки від неї — короткі пунктири,
    # що НЕ перетинають напис (лінія проходить повз рамку, не крізь неї).
    split_y = (y0 + 2.5 * step)
    lab, lw, lh = textbox(box_x + box_w / 2, split_y, "тут родина повертає на відкриту RISC-V",
                          size=11, bold=True, color=RV, fill="#fdecea", stroke=RV, sw=1.6, pad=9)
    lab_left = box_x + box_w / 2 - lw / 2
    lab_right = box_x + box_w / 2 + lw / 2
    frags.append(line(box_x - 6, split_y, lab_left - 8, split_y, color=RV, sw=1.4, dash="6 5"))
    frags.append(line(lab_right + 8, split_y, box_x + box_w + 6, split_y, color=RV, sw=1.4, dash="6 5"))
    frags.append(lab)

    # легенда гілок (угорі праворуч)
    frags.append(rect(box_x + 380, top - 8, 22, 14, fill=XT, stroke=XT, sw=1, rx=3))
    frags.append(text(box_x + 408, top + 4, "гілка Xtensa", size=11, color=XT, bold=True, anchor="start"))
    frags.append(rect(box_x + 380, top + 12, 22, 14, fill=RV, stroke=RV, sw=1, rx=3))
    frags.append(text(box_x + 408, top + 24, "гілка RISC-V", size=11, color=RV, bold=True, anchor="start"))

    render(os.path.join(OUT, 'timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    family_tree()
    choose_map()
    timeline()
    print("OK: family-tree.svg, choose-map.svg, timeline.svg")
