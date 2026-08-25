# -*- coding: utf-8 -*-
"""Фігури теми «Газорозрядник». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: один принцип — два корпуси ─────────────────────────────────────
# Голий іскровий проміжок у повітрі поряд із тим самим зазором, запаяним у колбу
# з газом. Знизу — як прилад стоїть поперек лінії на землю.
def fig_devices():
    W, H = 940, 470
    p = []

    # ── ліва панель: голий проміжок ──
    p.append(rect(40, 55, 410, 270, fill="#fbfbfb", stroke="#e4e4e4", sw=1.5, rx=10))
    p.append(text(245, 80, "Іскровий проміжок (spark gap)", size=15, bold=True))
    p.append(text(245, 100, "просто два електроди в повітрі", size=12, color=MUTED, italic=True))
    # верхній електрод (вістря донизу)
    p.append(line(245, 135, 245, 172, color=INK, sw=8))
    p.append('<path d="M 231,172 L 259,172 L 245,182 Z" fill="%s"/>' % INK)
    # нижній електрод (вістря догори)
    p.append(line(245, 218, 245, 255, color=INK, sw=8))
    p.append('<path d="M 231,218 L 259,218 L 245,208 Z" fill="%s"/>' % INK)
    # іскра в зазорі
    p.append('<polyline points="245,182 252,187 238,193 252,198 238,203 245,208" '
             'fill="none" stroke="#e08030" stroke-width="3" stroke-linejoin="round"/>')
    # виводи
    p.append(line(245, 135, 100, 135, color=POS, sw=2.5))
    p.append(circle(100, 135, 4, fill=POS, stroke=POS, sw=2))
    p.append(text(94, 127, "лінія / антена", size=12, color=POS, anchor="end"))
    p.append(line(245, 255, 100, 255, color=NEG, sw=2.5))
    p.append(circle(100, 255, 4, fill=NEG, stroke=NEG, sw=2))
    p.append(text(94, 271, "земля", size=12, color=NEG, anchor="end"))
    p.append(text(273, 184, "зазор", size=12, color="#e08030", anchor="start"))
    p.append(text(273, 200, "(повітря)", size=11, color=MUTED, anchor="start"))
    p.append(text(245, 300, "Дешево, грубо. Іскрить на повітрі,", size=11, anchor="middle"))
    p.append(text(245, 316, "псується, ловить пил і вологу.", size=11, anchor="middle"))

    # ── права панель: GDT у колбі ──
    p.append(rect(490, 55, 410, 270, fill="#fbfbfb", stroke="#e4e4e4", sw=1.5, rx=10))
    p.append(text(695, 80, "Газорозрядник (GDT)", size=15, bold=True))
    p.append(text(695, 100, "той самий зазор, але в запаяній колбі з газом", size=12, color=MUTED, italic=True))
    p.append(rect(600, 130, 190, 110, fill="#eef4ff", stroke=INK, sw=2.5, rx=14))
    p.append(rect(618, 150, 22, 70, fill="#8a8a8a", stroke=INK, sw=2, rx=3))
    p.append(rect(750, 150, 22, 70, fill="#8a8a8a", stroke=INK, sw=2, rx=3))
    p.append(text(695, 154, "Ne / Ar", size=11, color="#7a3fb0", italic=True))
    p.append('<polyline points="642,185 660,177 677,193 695,177 713,193 730,177 748,185" '
             'fill="none" stroke="#e08030" stroke-width="3" stroke-linejoin="round"/>')
    p.append('<ellipse cx="695" cy="185" rx="48" ry="22" fill="#e08030" opacity="0.12"/>')
    p.append(line(600, 185, 550, 185, color=POS, sw=3))
    p.append(circle(550, 185, 4, fill=POS, stroke=POS, sw=2))
    p.append(text(544, 177, "лінія", size=12, color=POS, anchor="end"))
    p.append(line(790, 185, 850, 185, color=NEG, sw=3))
    p.append(circle(850, 185, 4, fill=NEG, stroke=NEG, sw=2))
    p.append(text(856, 177, "земля", size=12, color=NEG, anchor="start"))
    p.append(text(695, 300, "Газ і тиск підібрані під потрібний поріг;", size=11, anchor="middle"))
    p.append(text(695, 316, "герметично, без зносу. Тримає тисячі ампер.", size=11, anchor="middle"))

    # ── нижня смуга: увімкнення поперек лінії ──
    p.append(rect(40, 352, 860, 95, fill=BG, stroke="#e4e4e4", sw=1.5, rx=10))
    p.append(text(60, 374, "Де стоїть: ПОПЕРЕК (паралельно) між лінією та землею — у нормі його наче нема",
                  size=13, anchor="start", bold=True))
    p.append(text(70, 397, "сплеск", size=12, color="#e08030", anchor="middle"))
    p.append('<polyline points="70,403 74,407 66,411 70,415" fill="none" '
             'stroke="#e08030" stroke-width="2.2" stroke-linejoin="round"/>')
    p.append(line(70, 415, 760, 415, color=INK, sw=3))
    p.append(circle(420, 415, 4.5, fill=INK, stroke=INK, sw=2))
    p.append(line(420, 415, 420, 423, color=INK, sw=2.5))
    # символ GDT
    p.append(circle(420, 438, 15, fill="#eef4ff", stroke=INK, sw=2))
    p.append('<path d="M 408,432 L 420,432 L 414,438 Z" fill="%s"/>' % INK)
    p.append('<path d="M 420,444 L 432,444 L 426,438 Z" fill="%s"/>' % INK)
    p.append(line(420, 453, 420, 462, color=NEG, sw=2.5))
    p.append(line(405, 462, 435, 462, color=NEG, sw=3))
    p.append(line(410, 466, 430, 466, color=NEG, sw=2.5))
    p.append(line(414, 470, 426, 470, color=NEG, sw=2))
    p.append(text(444, 442, "GDT", size=12, anchor="start", bold=True))
    p.append(rect(745, 397, 30, 36, fill=BG, stroke=INK, sw=2, rx=3))
    p.append(text(800, 419, "схема,", size=12, anchor="start"))
    p.append(text(800, 435, "яку бережемо", size=12, anchor="start"))

    render(os.path.join(IMG, "spark-gdt-devices.svg"), W, H, *p,
           title="Один принцип — два корпуси: іскра в повітрі та іскра в запаяній колбі")


# ── Фігура 2: GDT як «лом» (crowbar) у часі ──────────────────────────────────
# Напруга на затисках: росте зі сплеском, на пробої — пік, тоді складається до
# напруги дуги в десятки вольтів; тримає, поки тече струм, тоді деіонізується.
def fig_crowbar():
    W, H = 940, 440
    p = []

    # осі
    p.append('<line x1="90" y1="340" x2="90" y2="80" stroke="%s" stroke-width="2" '
             'marker-end="url(#arrow)" stroke-linecap="round"/>' % INK)
    p.append('<line x1="90" y1="340" x2="850" y2="340" stroke="%s" stroke-width="2" '
             'marker-end="url(#arrow)" stroke-linecap="round"/>' % INK)
    p.append(text(78, 84, "U на GDT", size=13, anchor="end", bold=True))
    p.append(text(850, 362, "час", size=13, anchor="middle"))

    # рівні
    p.append(line(90, 120, 850, 120, color=POS, sw=1.4, dash="5 5"))
    p.append(text(850, 112, "напруга спрацювання (sparkover) ~ сотні В…кВ", size=12, color=POS, anchor="end"))
    p.append(line(90, 300, 850, 300, color=FIELD, sw=1.4, dash="5 5"))
    p.append(text(850, 318, "напруга дуги (arc) ~ 10…20 В — ось чому захищає", size=12, color=FIELD, anchor="end"))

    # крива напруги: росте → пік → складається → дуга → згасання
    rise = "100,334 130,330 160,322 190,308 220,288 250,262 280,228 310,180 320,120"
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % (rise, NEG))
    p.append('<polyline points="320,120 338,300" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % NEG)
    p.append('<polyline points="338,300 650,300" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % NEG)
    p.append('<polyline points="650,300 730,270 830,285" fill="none" stroke="%s" stroke-width="3" '
             'stroke-dasharray="2 4" stroke-linejoin="round"/>' % NEG)

    # підписи стадій
    p.append(text(210, 332, "1. сплеск росте,", size=12, color=NEG, anchor="middle"))
    p.append(text(210, 348, "GDT ще «не бачить»", size=11, color=MUTED, anchor="middle"))
    p.append(circle(320, 120, 5, fill=POS, stroke=POS, sw=2))
    p.append(text(328, 106, "2. пробій газу", size=12, color=POS, anchor="start", bold=True))
    p.append('<line x1="360" y1="200" x2="344" y2="235" stroke="%s" stroke-width="1.8" '
             'marker-end="url(#arrow)" stroke-linecap="round"/>' % INK)
    p.append(text(366, 206, "3. напруга «складається»", size=12, anchor="start"))
    p.append(text(366, 222, "(crowbar — коротке на землю)", size=11, color=MUTED, anchor="start"))
    p.append(text(485, 288, "4. тримає дугу, поки тече струм", size=12, color=FIELD, anchor="middle"))
    p.append(text(760, 252, "5. струм згас →", size=12, color=MUTED, anchor="start"))
    p.append(text(760, 268, "GDT знову ізолятор", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "gdt-crowbar.svg"), W, H, *p,
           title="GDT як «лом» (crowbar): спрацював — і коротить сплеск на землю")


if __name__ == "__main__":
    fig_devices()
    fig_crowbar()
    print("OK: фігури теми «Газорозрядник» згенеровано в", IMG)
