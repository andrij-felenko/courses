# -*- coding: utf-8 -*-
"""Фігури до теми «Надійність даних» (book/communications/coding-theory/data-reliability).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Сходи надійності: від найдешевшого виявлення до виправлення пакетів ──────
# Ідея, яку важко передати словами: усі коди шикуються в один ряд за зростанням
# сили й ціни, і вибір — це спуск цими сходами рівно настільки, скільки вимагає
# канал. Праворуч у кожної сходинки — що саме вона робить (виявлення/виправлення).
def fig_decision():
    W = 880
    rows = [
        ("Парність  ·  1 біт", "бачить 1 помилку, не виправляє",
         "UART-кадр, простий регістр", "виявлення", "#caa24a"),
        ("Контрольна сума  ·  сума / Флетчер", "дешеве програмне виявлення",
         "легкі протоколи, файли без заліза CRC", "виявлення", "#caa24a"),
        ("CRC", "потужне виявлення пакетів, апаратно майже задарма",
         "CAN, Ethernet, SD, USB, серйозний кадр", "виявлення (сильне)", POS),
        ("ECC  ·  Геммінг / SECDED, BCH", "виправляє на льоту, платить зайвими бітами",
         "RAM серверів, Flash, пам'ять у радіації", "виправлення", FIELD),
        ("Рід–Соломон  ·  каскад", "виправляє пакети символів",
         "носії, супутник, далекий космос", "виправлення (пакети)", FIELD),
    ]
    box_w, box_h, gap = 560, 86, 18
    top = 86
    H = top + len(rows) * (box_h + gap) + 40
    f = []
    f.append(text(W / 2, 34, "Сходи надійності: від найдешевшого виявлення до виправлення пакетів",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 56, "три питання вибирають інструмент: виправляти чи виявити? поодинокі чи пакетні? скільки платити?",
                  11.5, MUTED, "middle", italic=True))

    x_left = 60
    for i, (name, what, where, tag, col) in enumerate(rows):
        y = top + i * (box_h + gap)
        x = x_left + i * 8                      # легкий каскад управо — відчуття «сходів»
        f.append(rect(x, y, box_w, box_h, fill=BG, stroke=col, sw=2.2, rx=9))
        f.append(text(x + 18, y + 28, name, 15.5, col, "start", bold=True))
        f.append(text(x + 18, y + 50, what, 11.8, INK, "start"))
        f.append(text(x + 18, y + 70, "де: " + where, 11.5, MUTED, "start"))
        # ярлик «виявлення / виправлення» праворуч
        tag_w = text_width(tag, 12.5, bold=True) + 24
        tx = x + box_w + 14
        f.append(rect(tx, y + box_h / 2 - 18, tag_w, 36, fill="#fbfbfb", stroke=col, sw=1.6, rx=8))
        f.append(text(tx + tag_w / 2, y + box_h / 2 + 5, tag, 12.5, col, "middle", bold=True))
        # стрілка-сходинка вниз
        if i < len(rows) - 1:
            ax = x + 26
            f.append(arrow(ax, y + box_h, ax + 8, y + box_h + gap, color=MUTED, sw=2))

    f.append(text(W / 2, H - 16,
                  "Стрілка вниз — «треба більше надійності й готовий платити дорожче». Більшість систем поєднує кілька рівнів разом.",
                  11.5, INK, "middle", italic=True))
    render(os.path.join(IMG, "decision-ladder.svg"), W, H, *f)


# ── 2. Коди складаються в шари, а не змагаються ────────────────────────────────
# Ідея: різні рівні захисту працюють одночасно на різних рубежах одного пакета;
# кожен ловить те, проти чого він найсильніший, і прикриває слабкість сусіда.
def fig_layers():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 32, "Коди складаються в шари, а не змагаються",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 54, "кожен шар ловить те, що пропустив попередній; разом дають надійність, недосяжну поодинці",
                  11.5, MUTED, "middle", italic=True))

    layers = [
        ("байт у пам'яті / комірці", "ловить: поодинокі біт-фліпи в RAM і Flash",
         "ECC  (Геммінг / BCH)", FIELD),
        ("символи на носії / в радіоканалі", "ловить: пакети, завмирання, подряпини",
         "Рід–Соломон  (FEC)", "#7a3da8"),
        ("кадр на шині / у протоколі", "ловить: усе, що проскочило крізь канал",
         "CRC", POS),
        ("логічний пакет (заголовок + дані)", "ловить: груба перевірка структури, дешево",
         "контрольна сума / парність полів", "#caa24a"),
    ]
    bx, bw, bh, gap = 70, 620, 56, 14
    y0 = 86
    for i, (title_l, catch, code, col) in enumerate(layers):
        y = y0 + i * (bh + gap)
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(bx + 18, y + 24, title_l, 13.5, INK, "start", bold=True))
        f.append(text(bx + 18, y + 44, catch, 11.5, MUTED, "start"))
        # ярлик коду праворуч
        tag_w = text_width(code, 13, bold=True) + 22
        tx = bx + bw - tag_w - 12
        f.append(rect(tx, y + bh / 2 - 16, tag_w, 32, fill="#fbfbfb", stroke=col, sw=1.6, rx=7))
        f.append(text(tx + tag_w / 2, y + bh / 2 + 5, code, 13, col, "middle", bold=True))

    f.append(text(W / 2, H - 14,
                  "Кожен рівень бере загрозу, проти якої найсильніший, і прикриває слабкість сусіда.",
                  11.5, INK, "middle", italic=True))
    render(os.path.join(IMG, "protection-layers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decision()
    fig_layers()
    print("OK: figures written to", IMG)
