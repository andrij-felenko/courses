#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 43 (Модуль 7) — чистий Python, без залежностей.
Запуск:  python figs.py    →    кладе *.svg у ./img/

Стиль (єдиний для курсу, копіюється у кожен chNN/figs.py):
  білий фон; «+» червоний, «−» синій; поле — зелене; стрілки через marker;
  шрифт sans-serif. Підписи фігур у тексті — посекційно «Рис. C.S.N».
"""

import os
import math

# ── палітра ───────────────────────────────────────────────────────────────
INK   = "#1a1a1a"   # основні лінії й текст
MUTE  = "#6b7280"   # допоміжний сірий
RED   = "#cc0000"   # «+», гаряче, увага
BLUE  = "#1f4ed8"   # «−», холодне
GREEN = "#0a8f3c"   # поле / земля / «добре»
AMBER = "#d98a00"   # акцент / застереження
SKY   = "#dbeafe"   # небо (заливка)
GND   = "#dcfce7"   # земля (заливка)
PANEL = "#f4f4f5"   # нейтральна панель
BOX1  = "#eef2ff"   # залізо
BOX2  = "#eafaef"   # прошивка
BOX3  = "#fff5e6"   # наземна станція
FONT  = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def header(w, h):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"
     viewBox="0 0 {w} {h}" font-family="{FONT}">
  <defs>
    <marker id="arr" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{INK}"/></marker>
    <marker id="arrR" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{RED}"/></marker>
    <marker id="arrB" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{BLUE}"/></marker>
    <marker id="arrG" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{GREEN}"/></marker>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" fill="white"/>
'''


def footer():
    return "</svg>\n"


def text(x, y, s, size=14, fill=INK, anchor="start", weight="normal",
         italic=False, family=None):
    st = "italic" if italic else "normal"
    fam = f' font-family="{family}"' if family else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{st}"{fam}>{esc(s)}</text>\n')


def lines(x, y, rows, size=13, fill=INK, anchor="start", lh=16, weight="normal",
          family=None):
    out = ""
    for i, r in enumerate(rows):
        out += text(x, y + i * lh, r, size=size, fill=fill, anchor=anchor,
                    weight=weight, family=family)
    return out


def line(x1, y1, x2, y2, stroke=INK, w=1.6, dash=None, marker=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{w}"{d}{m} stroke-opacity="{opacity}" '
            f'stroke-linecap="round"/>\n')


def rect(x, y, w, h, fill="white", stroke=INK, sw=1.6, rx=8, dash=None,
         opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="white", stroke=INK, sw=1.6, opacity=1.0):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(pts, fill="none", stroke=INK, sw=1.6, closed=True, opacity=1.0):
    tag = "polygon" if closed else "polyline"
    p = " ".join(f"{x},{y}" for x, y in pts)
    return (f'<{tag} points="{p}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>\n')


def title(w, s, sub=None):
    out = text(w / 2, 30, s, size=18, anchor="middle", weight="bold")
    if sub:
        out += text(w / 2, 50, sub, size=13, anchor="middle", fill=MUTE)
    return out


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.0.1 — Хронологія (вертикальна вісь часу): дві лінії, спільне залізо, розкол
# ════════════════════════════════════════════════════════════════════════════
def fig_timeline():
    W, H = 900, 668
    s = header(W, H)
    s += title(W, "Як народився ArduPilot: дві лінії, спільне залізо, розкол ліцензій",
               "згори вниз — час · ліворуч від осі лінія ArduPilot, праворуч — лінія PX4/ETH")

    spine = 450
    y_top, y_bot = 92, 600

    # колонкові заголовки
    s += text(293, 78, "ArduPilot  (хобі → Arduino)", size=13, weight="bold",
              fill=RED, anchor="middle")
    s += text(620, 78, "PX4 / Pixhawk  (ETH Zürich)", size=13, weight="bold",
              fill=BLUE, anchor="middle")

    # вісь часу
    s += line(spine, y_top, spine, y_bot, stroke=INK, w=3.0, marker="arr")
    s += text(spine, y_bot + 22, "час", size=12, fill=MUTE, anchor="middle",
              italic=True)

    def card_L(y, year, rows):
        bx, bw, h = 150, 286, 46
        out = rect(bx, y - h / 2, bw, h, fill="#fff3f3", stroke=RED, sw=1.4, rx=8)
        out += line(bx + bw, y, spine - 5, y, stroke=RED, w=1.4)
        out += circle(spine, y, 5, fill=RED, stroke=INK, sw=1.2)
        out += text(spine + 12, y + 4, str(year), size=11, fill=MUTE,
                    weight="bold")
        out += lines(bx + 14, y - (len(rows) - 1) * 7.5 + 4, rows, size=11.5,
                     lh=15)
        return out

    def card_R(y, year, rows):
        bx, bw, h = 470, 300, 46
        out = rect(bx, y - h / 2, bw, h, fill="#eff4ff", stroke=BLUE, sw=1.4,
                   rx=8)
        out += line(spine + 5, y, bx, y, stroke=BLUE, w=1.4)
        out += circle(spine, y, 5, fill=BLUE, stroke=INK, sw=1.2)
        out += text(spine - 12, y + 4, str(year), size=11, fill=MUTE,
                    weight="bold", anchor="end")
        out += lines(bx + 14, y - (len(rows) - 1) * 7.5 + 4, rows, size=11.5,
                     lh=15)
        return out

    def rung(y, head, rows, color, fill):
        bx, bw = 222, 456
        out = line(150, y, 770, y, stroke=color, w=1.4, dash="4,4")
        out += rect(bx, y - 30, bw, 60, fill=fill, stroke=color, sw=1.8, rx=11)
        out += text(bx + 18, y - 9, head, size=12.5, weight="bold", fill=color)
        out += lines(bx + 18, y + 9, rows, size=11.5, lh=15)
        return out

    s += card_L(120, 2007, ["DIY Drones — Кріс Андерсон:",
                            "автопілот спершу на Lego Mindstorms"])
    s += card_L(176, 2009, ["ArduPilot на Arduino — Жорді Муньйос;",
                            "засновано 3D Robotics (3DR)"])
    s += card_R(232, 2009, ["MAVLink — протокол телеметрії",
                            "(Лоренц Маєр, ETH; див. Розділ 42)"])
    s += card_L(288, "2010–11", ["ArduPilotMega (APM): 8-біт ATmega2560 + IMU;",
                                 "ArduCopter — підтримка мультироторів"])
    s += rung(348, "2012–13 · Спільне 32-бітне залізо",
              ["8-біт уперся в стелю; PX4 і AP_HAL — 2012,",
               "плата Pixhawk (STM32) — 2013; стеки → ARM + RTOS"], GREEN, GND)
    s += card_R(414, 2014, ["Dronecode — фундація під Linux Foundation",
                            "(хостить PX4, MAVLink, QGroundControl)"])
    s += rung(476, "2016 · Розкол через ліцензії",
              ["ArduPilot виходить із Dronecode → незалежний (GPLv3);",
               "PX4 лишається в Dronecode (ліцензія BSD)"], AMBER, BOX3)
    s += card_L(548, "тепер", ["ArduPilot.org: RTOS ChibiOS, STM32H7;",
                               "Copter · Plane · Rover · Sub · Tracker"])
    s += card_R(548, "тепер", ["PX4 у Dronecode; спільний інструмент —",
                               "наземна станція QGroundControl"])

    s += text(W / 2, H - 16,
              "Хобі-лінія (Arduino) і академічна лінія (ETH) зійшлися на залізі "
              "Pixhawk, а потім розійшлися через ліцензії — звідси два великі "
              "відкриті автопілоти.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.0.2 — Термопарний (ІЧ) давач горизонту: дешевий спосіб «знати, де верх»
# ════════════════════════════════════════════════════════════════════════════
def fig_thermopile():
    W, H = 940, 500
    s = header(W, H)
    s += title(W, "Як перші автопілоти «бачили» горизонт без IMU: інфрачервоні термопари",
               "земля тепла (ІЧ-яскрава), небо холодне (ІЧ-темне) — різниця дає крен і тангаж")

    # ── сцена ліворуч: небо/земля + нахилений апарат ────────────────────────
    sx, sy, sw, sh = 40, 70, 540, 360
    horizon = sy + 200
    s += rect(sx, sy, sw, horizon - sy, fill=SKY, stroke="none", rx=0)
    s += rect(sx, horizon, sw, sy + sh - horizon, fill=GND, stroke="none", rx=0)
    s += line(sx, horizon, sx + sw, horizon, stroke=GREEN, w=2.0)
    s += rect(sx, sy, sw, sh, fill="none", stroke=INK, sw=1.4, rx=10)
    s += text(sx + 14, sy + 26, "холодне небо  ≈ −40 °C", size=12.5, fill=BLUE,
              weight="bold")
    s += text(sx + 14, sy + sh - 14, "тепла земля  ≈ +15 °C", size=12.5,
              fill=RED, weight="bold")

    # апарат (вид спереду), нахил/крен ~22°
    cx, cy = sx + sw / 2, horizon - 28
    bank = 22
    s += f'<g transform="rotate({bank} {cx} {cy})">\n'
    s += poly([(cx - 86, cy), (cx + 86, cy), (cx + 78, cy + 9),
               (cx - 78, cy + 9)], fill="#ffffff", stroke=INK, sw=1.6)  # крило
    s += circle(cx, cy - 2, 13, fill=PANEL, stroke=INK, sw=1.6)         # фюзеляж
    s += circle(cx - 86, cy + 4, 5, fill=RED, stroke=INK, sw=1.2)       # давач L
    s += circle(cx + 86, cy + 4, 5, fill=BLUE, stroke=INK, sw=1.2)      # давач R
    s += '</g>\n'

    # промені давачів (у НЕнахиленій системі — куди вони реально дивляться)
    a = math.radians(bank)
    lx = cx - 86 * math.cos(a)
    ly = cy - 86 * math.sin(a) + 4
    rx = cx + 86 * math.cos(a)
    ry = cy + 86 * math.sin(a) + 4
    s += line(lx, ly, lx - 28, ly + 70, stroke=RED, w=2.0, marker="arrR")
    s += line(rx, ry, rx + 28, ry - 70, stroke=BLUE, w=2.0, marker="arrB")
    s += text(lx - 70, ly + 92, "ІЧ-давач L", size=11.5, fill=RED, weight="bold")
    s += text(lx - 78, ly + 106, "→ тепла земля", size=11, fill=RED)
    s += text(rx - 4, ry - 76, "ІЧ-давач R", size=11.5, fill=BLUE, weight="bold")
    s += text(rx - 12, ry - 62, "→ холодне небо", size=11, fill=BLUE)
    s += text(cx + 2, cy - 44, "крен", size=11.5, fill=INK, italic=True,
              anchor="middle")

    # ── праворуч: два стани + формула + застереження ────────────────────────
    px = 610
    s += text(px, sy + 8, "Що «чує» автопілот", size=13.5, weight="bold")

    by = sy + 22
    s += rect(px, by, 290, 86, fill="white", stroke=INK, sw=1.3, rx=9)
    s += text(px + 14, by + 22, "Рівний політ", size=12.5, weight="bold")
    s += circle(px + 40, by + 52, 7, fill=RED, stroke=INK, sw=1.2)
    s += circle(px + 250, by + 52, 7, fill=RED, stroke=INK, sw=1.2)
    s += text(px + 40, by + 74, "T_L", size=11, anchor="middle", fill=MUTE)
    s += text(px + 250, by + 74, "T_R", size=11, anchor="middle", fill=MUTE)
    s += text(px + 145, by + 48, "T_L ≈ T_R", size=13, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(px + 145, by + 66, "→ крен 0", size=11.5, anchor="middle",
              fill=GREEN)

    by2 = by + 100
    s += rect(px, by2, 290, 86, fill="white", stroke=INK, sw=1.3, rx=9)
    s += text(px + 14, by2 + 22, "Крен праворуч", size=12.5, weight="bold")
    s += circle(px + 40, by2 + 52, 9, fill=RED, stroke=INK, sw=1.2)
    s += circle(px + 250, by2 + 54, 5, fill=BLUE, stroke=INK, sw=1.2)
    s += text(px + 145, by2 + 48, "T_L > T_R", size=13, anchor="middle",
              weight="bold", fill=AMBER)
    s += text(px + 145, by2 + 66, "→ виправити кермом", size=11.5,
              anchor="middle", fill=AMBER)

    by3 = by2 + 100
    s += rect(px, by3, 290, 56, fill=PANEL, stroke=INK, sw=1.3, rx=9)
    s += text(px + 145, by3 + 24, "крен ∝ T_L − T_R", size=13.5,
              anchor="middle", weight="bold", family="Consolas, monospace")
    s += text(px + 145, by3 + 44, "тангаж ∝ T_перед − T_зад", size=12,
              anchor="middle", family="Consolas, monospace")

    by4 = by3 + 70
    s += text(px, by4 + 4, "⚠ чому відмовилися:", size=12, weight="bold",
              fill=AMBER)
    s += lines(px, by4 + 22, [
        "хмари, захід сонця, гарячий дах і",
        "ліс плутають «горизонт». MEMS-IMU",
        "(Розділ 33) витіснили термопари.",
    ], size=11.5, lh=15, fill=MUTE)

    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.0.3 — Три шари назв: залізо ≠ прошивка ≠ наземна станція
# ════════════════════════════════════════════════════════════════════════════
def fig_naming():
    W, H = 920, 520
    s = header(W, H)
    s += title(W, "Чому стільки назв: залізо, прошивка й наземна станція — три різні шари",
               "їх обирають майже незалежно; плутанина тягнеться ще з епохи «APM»")

    bx, bw = 70, 520
    h = 96

    # шар 3 (зверху): наземна станція
    y3 = 80
    s += rect(bx, y3, bw, h, fill=BOX3, stroke=AMBER, sw=1.8, rx=12)
    s += text(bx + 18, y3 + 28, "НАЗЕМНА СТАНЦІЯ (GCS)", size=14, weight="bold",
              fill=AMBER)
    s += text(bx + 18, y3 + 50, "на ноутбуці/планшеті: карта, параметри, місія, логи",
              size=12, fill=INK)
    s += text(bx + 18, y3 + 74, "приклади:  Mission Planner · QGroundControl",
              size=12.5, weight="bold", fill=INK)

    # шар 2 (середина): прошивка
    y2 = y3 + h + 30
    s += rect(bx, y2, bw, h, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += text(bx + 18, y2 + 28, "ПРОШИВКА — польотний стек", size=14,
              weight="bold", fill=GREEN)
    s += text(bx + 18, y2 + 50, "заливається у плату; читає давачі й керує моторами",
              size=12, fill=INK)
    s += text(bx + 18, y2 + 74, "приклади:  ArduPilot (GPLv3) · PX4 (BSD)",
              size=12.5, weight="bold", fill=INK)

    # шар 1 (низ): залізо
    y1 = y2 + h + 30
    s += rect(bx, y1, bw, h, fill=BOX1, stroke=BLUE, sw=1.8, rx=12)
    s += text(bx + 18, y1 + 28, "ЗАЛІЗО — політний контролер (FMU)", size=14,
              weight="bold", fill=BLUE)
    s += text(bx + 18, y1 + 50, "STM32 + IMU + барометр + роз'єми; «мозок» у залізі",
              size=12, fill=INK)
    s += text(bx + 18, y1 + 74, "приклади:  Pixhawk · Cube · Matek · Holybro",
              size=12.5, weight="bold", fill=INK)

    # зв'язок прошивка ↔ GCS = MAVLink
    mx = bx + bw + 30
    s += line(mx, y2 + h / 2, mx, y3 + h / 2, stroke=INK, w=2.0, marker="arr")
    s += line(mx, y3 + h / 2 + 8, mx, y2 + h / 2 - 8, stroke=INK, w=2.0,
              marker="arr")
    s += rect(mx + 8, (y3 + h + y2) / 2 - 28, 222, 56, fill=PANEL, stroke=INK,
              sw=1.3, rx=9)
    s += lines(mx + 20, (y3 + h + y2) / 2 - 8, [
        "MAVLink — протокол", "(Розділ 42), по радіо/USB",
    ], size=12, lh=16)

    # зв'язок прошивка → залізо = «залити»
    s += line(bx + bw / 2, y2 + h, bx + bw / 2, y1, stroke=GREEN, w=2.2,
              marker="arrG")
    s += text(bx + bw / 2 + 12, (y2 + h + y1) / 2 + 4, "прошити (USB/UART)",
              size=11.5, fill=GREEN, italic=True)

    s += text(W / 2, H - 22,
              "Один FMU може нести або ArduPilot, або PX4; стара назва «APM» означала "
              "і плату, і прошивку — звідси вічна плутанина в чужих доках.",
              size=12, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.1.1 — Автономний апарат як ЗАМКНЕНИЙ контур керування
# ════════════════════════════════════════════════════════════════════════════
def fig_loop():
    W, H = 980, 470
    s = header(W, H)
    s += title(W, "Автономний апарат — це замкнений контур, а не пряма лінія",
               "давачі → оцінювач стану → керування → виконання → апарат → і знову давачі")
    yc, bh = 215, 72

    def blk(x, w, rows, fill, stroke):
        o = rect(x, yc - bh / 2, w, bh, fill=fill, stroke=stroke, sw=1.7, rx=10)
        o += lines(x + w / 2, yc - (len(rows) - 1) * 8 + 4, rows, size=12.5,
                   anchor="middle", lh=16, weight="bold")
        return o

    blocks = [
        (36, 150, ["ДАВАЧІ", "вимірюють"], BOX1, BLUE),
        (222, 168, ["ОЦІНЮВАЧ", "СТАНУ"], PANEL, INK),
        (426, 152, ["КЕРУВАННЯ", "порівняти й виправити"], BOX2, GREEN),
        (614, 160, ["ВИКОНАВЧІ", "МЕХАНІЗМИ"], BOX3, AMBER),
        (810, 140, ["АПАРАТ", "+ фізика"], "#ececef", INK),
    ]
    for x, w, rows, fill, stroke in blocks:
        s += blk(x, w, rows, fill, stroke)

    for x1, x2, lab in [(186, 222, "сирі виміри"), (390, 426, "оцінка стану"),
                        (578, 614, "команди"), (774, 810, "сили / моменти")]:
        s += line(x1, yc, x2 - 3, yc, stroke=INK, w=2.0, marker="arr")
        s += text((x1 + x2) / 2, 168, lab, size=11, anchor="middle", fill=MUTE)

    # уставка (бажаний стан) входить у блок керування згори
    s += rect(410, 64, 184, 50, fill="#eef6ff", stroke=BLUE, sw=1.5, rx=9)
    s += lines(502, 84, ["ЗАВДАННЯ — бажаний стан", "(уставка)"], size=11.5,
               anchor="middle", lh=15, weight="bold", fill=BLUE)
    s += line(502, 114, 502, yc - bh / 2 - 2, stroke=BLUE, w=2.0, marker="arrB")
    s += text(556, 150, "уставка", size=10.5, fill=BLUE, italic=True)

    # зворотний зв'язок: U-подібний шлях назад до давачів
    s += line(880, yc + bh / 2, 880, 372, stroke=INK, w=2.2)
    s += line(880, 372, 111, 372, stroke=INK, w=2.2)
    s += line(111, 372, 111, yc + bh / 2 + 2, stroke=INK, w=2.2, marker="arr")
    s += text(495, 365,
              "апарат рухається → давачі міряють новий стан: контур замикається",
              size=11.5, anchor="middle", fill=INK)

    s += text(W / 2, H - 14,
              "Ключова ідея: керування спирається на ОЦІНКУ стану, а не на сирі "
              "давачі, і безперервно порівнює її з уставкою.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.1.2 — Та сама абстракція у реальному залізі й коді
# ════════════════════════════════════════════════════════════════════════════
def fig_mapping():
    W, H = 900, 470
    s = header(W, H)
    s += title(W, "Та сама абстракція — у реальному залізі й коді",
               "кожна ланка контуру = конкретні компоненти апарата")
    rows = [
        (["ДАВАЧІ"], BOX1, BLUE,
         ["IMU (гіроскоп + акселерометр) · магнітометр · барометр",
          "GNSS-приймач · давач струму та напруги"]),
        (["ОЦІНЮВАЧ", "СТАНУ"], PANEL, INK,
         ["орієнтація: крен · тангаж · курс",
          "висота · положення · швидкість"]),
        (["КЕРУВАННЯ"], BOX2, GREEN,
         ["ПІД-контури й каскади (з Розділу 34):",
          "кутова швидкість → кут → положення → траєкторія"]),
        (["ВИКОНАВЧІ", "МЕХАНІЗМИ"], BOX3, AMBER,
         ["ESC → безколекторні мотори (тяга)",
          "серворушії → керма / елерони"]),
    ]
    for (lab, fill, stroke, rlist), cy in zip(rows, [108, 200, 292, 384]):
        s += rect(44, cy - 36, 196, 72, fill=fill, stroke=stroke, sw=1.7, rx=10)
        s += lines(142, cy - (len(lab) - 1) * 8 + 4, lab, size=13,
                   anchor="middle", lh=16, weight="bold")
        s += line(240, cy, 285, cy, stroke=INK, w=2.0, marker="arr")
        s += rect(288, cy - 36, 576, 72, fill="white", stroke=MUTE, sw=1.2, rx=9)
        s += lines(304, cy - 8, rlist, size=12.5, lh=20)
    s += text(W / 2, H - 14,
              "Контур із Рис. 43.1.1 — не метафора: за кожним блоком стоять "
              "відчутні мікросхеми, мотори й рядки коду.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.1.3 — Вкладені контури: різні задачі — різні темпи
# ════════════════════════════════════════════════════════════════════════════
def fig_nested():
    W, H = 860, 510
    s = header(W, H)
    s += title(W, "Контур у контурі: різні задачі — різні темпи",
               "зовнішній контур веде апарат туди, куди треба; внутрішній не дає впасти")
    bands = [
        (70, 96, 720, 356, "#f6f7fb", MUTE,
         "НАВІГАЦІЯ / МІСІЯ — куди летіти", "~1–10 Гц", 116, 690),
        (140, 172, 580, 212, "#eef2ff", BLUE,
         "КОНТУР ПОЛОЖЕННЯ / ШВИДКОСТІ — тримати траєкторію", "~20–50 Гц",
         192, 612),
        (220, 248, 420, 104, "#eafaef", GREEN,
         "КОНТУР ОРІЄНТАЦІЇ (attitude) — не впасти", "~250–1000 Гц", 274, 470),
    ]
    for x, y, w, h, fill, stroke, lab, rate, laby, ratex in bands:
        s += rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=12)
        s += text(x + 16, laby, lab, size=12.5, weight="bold", fill=stroke)
        s += rect(ratex, laby - 16, 84, 22, fill="white", stroke=stroke,
                  sw=1.2, rx=6)
        s += text(ratex + 42, laby - 1, rate, size=11, anchor="middle",
                  fill=stroke, weight="bold")
    s += text(228, 320, "вихід → команди на мотори та серво", size=11,
              fill=GREEN)
    s += text(96, 150, "↓ задає уставку", size=10.5, fill=MUTE, italic=True)
    s += text(166, 226, "↓ задає уставку", size=10.5, fill=MUTE, italic=True)
    s += text(W / 2, H - 16,
              "Внутрішній контур — найшвидший і найкритичніший: не встигне — апарат "
              "перекинеться раніше, ніж зреагує навігація.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.1.4 — Джерело «бажаного стану»: пілот чи місія — ядро те саме
# ════════════════════════════════════════════════════════════════════════════
def fig_setpoint():
    W, H = 900, 430
    s = header(W, H)
    s += title(W, "Звідки береться «бажаний стан»: пілот чи місія — ядро те саме",
               "ручний і автономний режими різняться лише джерелом уставки")
    s += rect(46, 78, 250, 78, fill="#eef6ff", stroke=BLUE, sw=1.7, rx=11)
    s += text(60, 102, "ПІЛОТ — RC-стіки", size=13, weight="bold", fill=BLUE)
    s += lines(60, 124, ["ручна уставка просто зараз:",
                         "«нахили праворуч на 15°»"], size=11.5, lh=15)
    s += rect(46, 250, 250, 78, fill="#eafaef", stroke=GREEN, sw=1.7, rx=11)
    s += text(60, 274, "АВТОНОМНА МІСІЯ", size=13, weight="bold", fill=GREEN)
    s += lines(60, 296, ["точки маршруту → навігація",
                         "рахує уставку: «лети до точки B»"], size=11.5, lh=15)

    s += rect(346, 165, 128, 76, fill=PANEL, stroke=INK, sw=1.6, rx=10)
    s += lines(410, 196, ["ВИБІР", "РЕЖИМУ"], size=12.5, anchor="middle",
               lh=16, weight="bold")
    s += line(296, 117, 344, 188, stroke=BLUE, w=2.0, marker="arrB")
    s += line(296, 289, 344, 218, stroke=GREEN, w=2.0, marker="arrG")

    s += rect(512, 165, 188, 76, fill=BOX2, stroke=GREEN, sw=1.7, rx=11)
    s += lines(606, 196, ["КЕРУВАННЯ", "(те саме ядро)"], size=12.5,
               anchor="middle", lh=16, weight="bold")
    s += line(474, 203, 510, 203, stroke=INK, w=2.0, marker="arr")

    s += rect(728, 165, 140, 76, fill=BOX3, stroke=AMBER, sw=1.7, rx=11)
    s += lines(798, 196, ["ВИКОНАВЧІ", "МЕХАНІЗМИ"], size=12.5,
               anchor="middle", lh=16, weight="bold")
    s += line(700, 203, 726, 203, stroke=INK, w=2.0, marker="arr")

    s += text(W / 2, H - 16,
              "Те, що нижче «вибору режиму» (керування → виконання → апарат → "
              "давачі), однакове для ручного й автономного польоту.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.1.5 — Розімкнено проти замкнено: чому потрібен зворотний зв'язок
# ════════════════════════════════════════════════════════════════════════════
def fig_openloop():
    W, H = 880, 380
    s = header(W, H)
    s += title(W, "Чому потрібен зворотний зв'язок: розімкнено проти замкнено",
               "однакове збурення; ліворуч — команда наосліп, праворуч — вимір-порівняння-корекція")

    def panel(x, ptitle, curve, ccolor, note):
        o = rect(x, 86, 360, 220, fill="white", stroke=INK, sw=1.4, rx=10)
        o += text(x + 180, 80, ptitle, size=12.5, weight="bold", anchor="middle")
        o += line(x + 20, 296, x + 344, 296, stroke=MUTE, w=1.2, marker="arr")
        o += text(x + 344, 290, "час", size=10, fill=MUTE, anchor="end")
        o += line(x + 20, 190, x + 348, 190, stroke=BLUE, w=1.3, dash="5,4")
        o += text(x + 24, 184, "уставка 0°", size=10, fill=BLUE)
        o += poly(curve, fill="none", stroke=ccolor, sw=2.4, closed=False)
        o += text(x + 180, 116, note, size=11, anchor="middle", fill=ccolor,
                  weight="bold")
        return o

    div = [(84, 190), (140, 186), (185, 178), (228, 166), (270, 148),
           (312, 122), (350, 106), (398, 98)]
    con = [(492, 190), (520, 150), (546, 138), (576, 158), (614, 178),
           (656, 188), (706, 191), (824, 190)]
    s += panel(60, "РОЗІМКНЕНО — без зворотного зв'язку", div, RED,
               "кут утікає → апарат падає")
    s += panel(470, "ЗАМКНЕНО — зі зворотним зв'язком", con, GREEN,
               "кут повертається до уставки")
    s += text(W / 2, H - 14,
              "Той самий поштовх: без зворотного зв'язку похибка накопичується, "
              "із ним — гаситься. Уся автономність тримається на цій лінії.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.1.6 — Навіщо оцінювач: жоден давач сам не дає «стану»
# ════════════════════════════════════════════════════════════════════════════
def fig_contrib():
    W, H = 900, 430
    s = header(W, H)
    s += title(W, "Навіщо окремий оцінювач: жоден давач сам не дає «стану»",
               "сильне одного закриває слабке іншого; дещо не міряє ніхто — це оцінюють")
    sensors = [
        (110, BLUE,  "Гіроскоп — кутова швидкість", "✗ кут із нього дрейфує"),
        (185, RED,   "Акселерометр — нахил (вниз)", "✗ трясеться від вібрації"),
        (260, GREEN, "Магнітометр — курс (північ)", "✗ плутає залізо й струми"),
        (335, AMBER, "GNSS — положення, швидкість", "✗ повільний, не всюди"),
    ]
    for cy, col, l1, l2 in sensors:
        s += rect(40, cy - 29, 310, 58, fill="white", stroke=col, sw=1.5, rx=9)
        s += text(56, cy - 6, l1, size=12, weight="bold", fill=col)
        s += text(56, cy + 13, l2, size=11, fill=MUTE)
        s += line(350, cy, 396, 240, stroke=MUTE, w=1.6, marker="arr")

    s += rect(400, 120, 150, 240, fill=PANEL, stroke=INK, sw=1.7, rx=11)
    s += lines(475, 228, ["ОЦІНЮВАЧ", "СТАНУ", "(фьюжн)"], size=13,
               anchor="middle", lh=18, weight="bold")
    s += line(550, 240, 596, 240, stroke=INK, w=2.2, marker="arr")

    s += rect(600, 150, 280, 180, fill="#eafaef", stroke=GREEN, sw=1.7, rx=11)
    s += text(618, 178, "СТАН (чистий, надійний):", size=12.5, weight="bold",
              fill=GREEN)
    s += lines(618, 202, ["крен · тангаж · курс",
                          "висота · положення · швидкість",
                          "",
                          "+ те, чого не міряє жоден давач",
                          "(напр. швидкість вітру) — ОЦІНЮЄТЬСЯ"],
               size=11.5, lh=19)
    s += text(W / 2, H - 12,
              "Оцінювач — це не «згладжування»: він поєднує давачі й виводить "
              "навіть те, що напряму не вимірюється.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.2.1 — Реальний час: вчасно важливіше, ніж швидко (детермінізм vs джиттер)
# ════════════════════════════════════════════════════════════════════════════
def fig_determinism():
    W, H = 980, 420
    s = header(W, H)
    s += title(W, "Реальний час: вчасно — важливіше, ніж «швидко в середньому»",
               "той самий контур на виділеному МК і на універсальній ОС; такт ~2.5 мс (≈400 Гц)")
    starts = [90, 190, 290, 390, 490, 590, 690, 790]
    # дедлайни (межі тактів)
    for bx in [190, 290, 390, 490, 590, 690, 790]:
        col = RED if bx == 490 else MUTE
        wsw = 1.6 if bx == 490 else 1.0
        s += line(bx, 104, bx, 252, stroke=col, w=wsw, dash="4,4",
                  opacity=0.9 if bx == 490 else 0.5)
    s += text(490, 100, "дедлайн", size=10, anchor="middle", fill=RED)

    # верхня смуга — виділений МК + RTOS
    s += text(90, 100, "Виділений МК + RTOS — кожен такт вчасно", size=12,
              weight="bold", fill=GREEN)
    for st in starts:
        s += rect(st, 108, 28, 28, fill="#bbf0cb", stroke=GREEN, sw=1.3, rx=4)

    # нижня смуга — універсальна ОС
    s += text(90, 204, "Універсальна ОС — інколи зайнята чимось іншим", size=12,
              weight="bold", fill=AMBER)
    for st in [90, 190, 290, 590, 690, 790]:
        s += rect(st, 216, 28, 28, fill="#bbf0cb", stroke=GREEN, sw=1.3, rx=4)
    # такт 3: завада ОС + спізнення через дедлайн
    s += rect(390, 216, 95, 28, fill="#e5e7eb", stroke=MUTE, sw=1.2, rx=4)
    s += text(437, 234, "ОС зайнялась", size=9.5, anchor="middle", fill=MUTE)
    s += rect(485, 216, 5, 28, fill="#bbf0cb", stroke=GREEN, sw=1.0, rx=2)
    s += rect(490, 216, 32, 28, fill="#f4b8b8", stroke=RED, sw=1.3, rx=4)
    s += text(506, 234, "пізно", size=9.5, anchor="middle", fill=RED)
    s += text(560, 268, "× такт пропущено", size=11, fill=RED, weight="bold")
    s += text(437, 286,
              "⚠ контур не оновився вчасно → апарат хитнуло", size=11.5,
              fill=RED, weight="bold")

    s += line(80, 320, 900, 320, stroke=INK, w=1.4, marker="arr")
    s += text(900, 314, "час", size=11, anchor="end", fill=MUTE)
    s += text(W / 2, H - 12,
              "Внутрішній контур мусить устигати КОЖЕН такт. Універсальна ОС "
              "буває швидкою, але не ГАРАНТУЄ строку — а тут запізнення = падіння.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.2.2 — Надійність: заздалегідь задані безпечні реакції (failsafe)
# ════════════════════════════════════════════════════════════════════════════
def fig_failsafe():
    W, H = 900, 450
    s = header(W, H)
    s += title(W, "Надійність: на кожну біду — заздалегідь задана безпечна реакція",
               "політний контролер не «думає» в аварії, а виконує наперед визначений failsafe")
    trig = [(110, "Втрата RC-зв'язку"), (190, "Низький заряд батареї"),
            (270, "Втрата GNSS-сигналу"), (350, "Вихід за геозону")]
    for cy, lab in trig:
        s += rect(36, cy - 30, 224, 60, fill="#fff3f3", stroke=RED, sw=1.5,
                  rx=10)
        s += text(148, cy + 5, lab, size=12.5, anchor="middle", weight="bold",
                  fill=INK)
        s += line(260, cy, 326, 240, stroke=MUTE, w=1.6, marker="arr")

    s += rect(330, 150, 184, 180, fill=BOX2, stroke=GREEN, sw=1.9, rx=12)
    s += lines(422, 222, ["ПОЛІТНИЙ", "КОНТРОЛЕР", "— безпечні реакції"],
               size=12.5, anchor="middle", lh=20, weight="bold", fill=GREEN)

    act = [(110, "Утримання на місці (Loiter)"),
           (190, "Повернення додому (RTL)"),
           (270, "Посадка (Land)"),
           (350, "Роззброєння — лише на землі")]
    for cy, lab in act:
        s += line(514, 240, 596, cy, stroke=GREEN, w=1.6, marker="arrG")
        s += rect(600, cy - 28, 268, 56, fill="white", stroke=GREEN, sw=1.4,
                  rx=10)
        s += text(734, cy + 5, lab, size=12, anchor="middle", weight="bold",
                  fill=INK)

    s += text(W / 2, H - 12,
              "Реакції зашиті заздалегідь, тож спрацьовують навіть тоді, коли "
              "решта системи відмовила. У цьому й суть «надійного» контролера.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.2.3 — Резервування: три IMU, голосування, відкидання відмови
# ════════════════════════════════════════════════════════════════════════════
def fig_redundancy():
    W, H = 900, 400
    s = header(W, H)
    s += title(W, "Резервування: три IMU не для точності, а щоб пережити відмову",
               "якщо один давач «збожеволів», голосування виявляє й відкидає його")
    imus = [(108, "IMU 1", "крен = +12.1°", GREEN, False),
            (200, "IMU 2", "крен = −47°  ⚠", RED, True),
            (292, "IMU 3", "крен = +12.3°", GREEN, False)]
    for cy, name, val, col, bad in imus:
        s += rect(46, cy - 30, 210, 60, fill="#fff3f3" if bad else "white",
                  stroke=col, sw=1.8 if bad else 1.4, rx=10)
        s += text(64, cy - 6, name, size=12.5, weight="bold", fill=col)
        s += text(64, cy + 14, val, size=12, fill=INK)
        if bad:
            s += line(256, cy, 356, 200, stroke=RED, w=1.8, dash="5,4",
                      marker="arrR")
            s += text(300, cy - 8, "✗ відкинуто", size=10.5, fill=RED,
                      weight="bold")
        else:
            s += line(256, cy, 356, 200, stroke=MUTE, w=1.6, marker="arr")

    s += rect(360, 140, 180, 120, fill=PANEL, stroke=INK, sw=1.7, rx=11)
    s += lines(450, 188, ["ГОЛОСУВАННЯ", "виявлення відмови", "→ відкинуто IMU 2"],
               size=12, anchor="middle", lh=20, weight="bold")
    s += line(540, 200, 596, 200, stroke=INK, w=2.2, marker="arr")
    s += rect(600, 165, 260, 70, fill="#eafaef", stroke=GREEN, sw=1.7, rx=11)
    s += lines(730, 193, ["ОЦІНЮВАЧ отримує", "крен ≈ +12.2°"], size=12.5,
               anchor="middle", lh=20, weight="bold", fill=GREEN)

    s += text(W / 2, H - 12,
              "Дублюються не лише IMU: бувають два барометри, кілька GNSS, "
              "подвійне живлення. Мета — не лишити жодної єдиної точки відмови.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.2.4 — Чому ВИДІЛЕНА плата: порівняння з універсальним комп'ютером
# ════════════════════════════════════════════════════════════════════════════
def fig_dedicated():
    W, H = 980, 470
    s = header(W, H)
    s += title(W, "Чому окрема плата: виділений контролер проти універсального комп'ютера",
               "критичне для виживання потребує гарантій, яких універсальна ОС не дає")
    lx, ax, bx = 30, 300, 645
    lw, aw, bw = 262, 335, 305
    # шапки
    s += rect(ax, 70, aw, 36, fill=BOX2, stroke=GREEN, sw=1.6, rx=8)
    s += text(ax + aw / 2, 94, "Виділений політний контролер", size=12.5,
              anchor="middle", weight="bold", fill=GREEN)
    s += rect(bx, 70, bw, 36, fill=BOX3, stroke=AMBER, sw=1.6, rx=8)
    s += text(bx + bw / 2, 94, "Універсальний комп'ютер (Linux/телефон)",
              size=11.5, anchor="middle", weight="bold", fill=AMBER)

    rows = [
        ("Тайминг", "гарантований, детермінований", "«швидко в середньому», джиттер"),
        ("Завантаження", "мілісекунди", "десятки секунд"),
        ("Скільки задач", "одна — керувати апаратом", "багато: ОС, мережа, застосунки"),
        ("Режими збою", "мало, передбачувані", "багато й несподівані"),
        ("Watchdog + failsafe", "вбудовано", "немає за замовчуванням"),
        ("Реальний час", "так (RTOS / голе залізо)", "ні"),
    ]
    y = 110
    rh = 46
    for i, (lab, a, b) in enumerate(rows):
        yy = y + i * rh
        s += rect(lx, yy, lw, rh - 6, fill=PANEL, stroke=MUTE, sw=1.0, rx=7)
        s += text(lx + 14, yy + 27, lab, size=12, weight="bold", fill=INK)
        s += rect(ax, yy, aw, rh - 6, fill="#f3fbf5", stroke=GREEN, sw=1.0, rx=7)
        s += text(ax + 14, yy + 27, a, size=11.5, fill=INK)
        s += rect(bx, yy, bw, rh - 6, fill="#fff8ef", stroke=AMBER, sw=1.0, rx=7)
        s += text(bx + 14, yy + 27, b, size=11.5, fill=INK)

    vy = y + len(rows) * rh + 4
    s += rect(lx, vy, bx + bw - lx, 38, fill="#eef2ff", stroke=BLUE, sw=1.5,
              rx=9)
    s += text(lx + 16, vy + 24,
              "Висновок: критичне для виживання — на виділеній платі; важке й "
              "«розумне» — на універсальній (про цей поділ — у 43.5).",
              size=12, weight="bold", fill=BLUE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.2.5 — Watchdog: апаратний таймер, що рятує від зависання
# ════════════════════════════════════════════════════════════════════════════
def fig_watchdog():
    W, H = 900, 410
    s = header(W, H)
    s += title(W, "Watchdog: рятівник від зависання керування",
               "контур мусить «відмічатися» щотакту; зупинився — апаратний таймер перезапускає МК")

    def panel(x, head, hcol):
        return (rect(x, 84, 410, 250, fill="white", stroke=hcol, sw=1.6, rx=12)
                + text(x + 205, 110, head, size=13, anchor="middle",
                       weight="bold", fill=hcol))

    # норма
    s += panel(40, "НОРМА — контур працює", GREEN)
    s += rect(70, 140, 150, 70, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += lines(145, 170, ["контур", "керування"], size=12, anchor="middle",
               lh=18, weight="bold")
    s += line(220, 175, 300, 175, stroke=GREEN, w=2.0, marker="arrG")
    s += text(260, 166, "скидаю", size=10, anchor="middle", fill=GREEN)
    s += rect(300, 140, 150, 70, fill="white", stroke=INK, sw=1.5, rx=10)
    s += lines(375, 170, ["WATCHDOG", "таймер"], size=12, anchor="middle",
               lh=18, weight="bold")
    s += rect(70, 250, 380, 22, fill="white", stroke=GREEN, sw=1.2, rx=6)
    s += rect(72, 252, 300, 18, fill="#bbf0cb", stroke="none", rx=5)
    s += text(80, 296, "таймер щоразу скидається — до 0 не доходить →",
              size=11.5, fill=INK)
    s += text(80, 314, "watchdog ніколи не спрацьовує. Усе гаразд.", size=11.5,
              fill=GREEN, weight="bold")

    # зависання
    s += panel(470, "ЗАВИСАННЯ — контур став", RED)
    s += rect(500, 140, 150, 70, fill="#fff3f3", stroke=RED, sw=1.6, rx=10)
    s += lines(575, 170, ["контур", "став  ✗"], size=12, anchor="middle",
               lh=18, weight="bold", fill=RED)
    s += line(650, 175, 730, 175, stroke=RED, w=2.0, dash="5,4")
    s += text(690, 166, "не скидаю", size=10, anchor="middle", fill=RED)
    s += rect(730, 140, 150, 70, fill="white", stroke=INK, sw=1.5, rx=10)
    s += lines(805, 170, ["WATCHDOG", "таймер"], size=12, anchor="middle",
               lh=18, weight="bold")
    s += rect(500, 250, 380, 22, fill="white", stroke=RED, sw=1.2, rx=6)
    s += rect(502, 252, 16, 18, fill="#f4b8b8", stroke="none", rx=5)
    s += text(510, 296, "таймер добіг до 0 → СПРАЦЮВАВ →", size=11.5, fill=INK)
    s += text(510, 314, "апаратний RESET МК + перехід у failsafe.", size=11.5,
              fill=RED, weight="bold")

    s += text(W / 2, H - 10,
              "Watchdog (Розділ 24) — остання лінія оборони: навіть якщо код "
              "зациклився, залізо саме перезапустить контролер.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.3.1 — Шари ArduPilot: від заліза (HAL) до місії
# ════════════════════════════════════════════════════════════════════════════
def fig_layers():
    W, H = 980, 560
    s = header(W, H)
    s += title(W, "Шари ArduPilot: знизу — залізо, згори — місія",
               "абстрактний контур із 43.1 стає стосом конкретних модулів")
    bands = [
        ("Апарат і режими", "ArduCopter · ArduPlane · Rover — головний цикл, мікшер",
         "#ececef", INK),
        ("Навігація", "AP_Mission · AC_WPNav · режими (Auto/RTL/Loiter) → уставка",
         "#fff5e6", AMBER),
        ("Керування", "AC_AttitudeControl · AC_PosControl · AC_PID",
         "#eafaef", GREEN),
        ("Оцінювач стану", "AP_AHRS + EKF3 — фьюжн → орієнтація, положення, швидкість",
         PANEL, INK),
        ("Драйвери давачів", "AP_InertialSensor · AP_GPS · AP_Baro · AP_Compass",
         "#eef2ff", BLUE),
        ("HAL — апаратна абстракція", "AP_HAL: UART · I2C · SPI · GPIO · RCOut · Scheduler",
         "#e3effb", BLUE),
    ]
    x, w, h, gap, y0 = 56, 590, 64, 5, 86
    for i, (role, mods, fill, stroke) in enumerate(bands):
        yy = y0 + i * (h + gap)
        s += rect(x, yy, w, h, fill=fill, stroke=stroke, sw=1.7, rx=10)
        s += text(x + 16, yy + 26, role, size=13.5, weight="bold", fill=stroke)
        s += text(x + 16, yy + 48, mods, size=11.5,
                  fill=INK, family="Consolas, monospace")

    # потік знизу вгору
    s += line(44, y0 + 6 * (h + gap) - gap - 6, 44, y0 + 6, stroke=MUTE,
              w=2.2, marker="arr")
    s += text(30, (y0 + 6 * (h + gap)) / 2, "потік", size=10, fill=MUTE,
              anchor="middle")

    # наскрізні служби (праворуч)
    sx, sw2 = 670, 250
    s += rect(sx, y0, sw2, 6 * (h + gap) - gap, fill="#fbfbfd", stroke=MUTE,
              sw=1.6, rx=12, dash="6,4")
    s += text(sx + sw2 / 2, y0 + 26, "НАСКРІЗНІ СЛУЖБИ", size=12.5,
              anchor="middle", weight="bold", fill=INK)
    svc = [("AP_Scheduler", "темпи задач"),
           ("GCS_MAVLink", "зв'язок із землею (Розд. 42)"),
           ("AP_Logger", "журнали польоту"),
           ("AP_Param", "параметри (→ 43.4)")]
    for j, (nm, what) in enumerate(svc):
        yy = y0 + 60 + j * 90
        s += rect(sx + 18, yy, sw2 - 36, 70, fill="white", stroke=MUTE, sw=1.2,
                  rx=9)
        s += text(sx + 32, yy + 28, nm, size=12.5, weight="bold", fill=BLUE,
                  family="Consolas, monospace")
        s += text(sx + 32, yy + 50, what, size=11, fill=MUTE)

    s += text(W / 2, H - 14,
              "Кожен шар спирається лише на сусідній знизу — тому шар можна "
              "замінити (інша плата, інший давач), не чіпаючи решти.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.3.2 — Той самий контур 43.1 — тепер з іменами модулів ArduPilot
# ════════════════════════════════════════════════════════════════════════════
def fig_modules():
    W, H = 980, 400
    s = header(W, H)
    s += title(W, "Той самий контур — тепер з іменами модулів ArduPilot",
               "чотири ланки з 43.1 — це конкретні бібліотеки у вихідниках")
    yc = 230
    blocks = [
        (40, 196, "ДАВАЧІ", ["AP_InertialSensor", "AP_GPS · AP_Baro", "AP_Compass"],
         "#eef2ff", BLUE),
        (276, 168, "ОЦІНЮВАЧ", ["AP_AHRS", "EKF3"], PANEL, INK),
        (484, 188, "КЕРУВАННЯ", ["AC_AttitudeControl", "AC_PosControl", "AC_PID"],
         "#eafaef", GREEN),
        (712, 196, "ВИКОНАННЯ", ["AP_Motors", "SRV_Channels"], "#fff5e6", AMBER),
    ]
    for x, w, role, mods, fill, stroke in blocks:
        s += rect(x, yc - 48, w, 96, fill=fill, stroke=stroke, sw=1.7, rx=11)
        s += text(x + w / 2, yc - 26, role, size=13, weight="bold",
                  anchor="middle", fill=stroke)
        s += lines(x + w / 2, yc - 4, mods, size=11, anchor="middle", lh=15,
                   family="Consolas, monospace")
    for x1, x2, lab in [(236, 276, "вимір"), (444, 484, "стан"),
                        (672, 712, "команди")]:
        s += line(x1, yc, x2 - 3, yc, stroke=INK, w=2.0, marker="arr")
        s += text((x1 + x2) / 2, yc - 56, lab, size=10.5, anchor="middle",
                  fill=MUTE)

    s += rect(470, 78, 216, 56, fill="#fff5e6", stroke=AMBER, sw=1.5, rx=9)
    s += text(578, 100, "Навігація / режими", size=12, anchor="middle",
              weight="bold", fill=AMBER)
    s += text(578, 120, "AP_Mission · AC_WPNav", size=11, anchor="middle",
              family="Consolas, monospace")
    s += line(578, 134, 578, yc - 50, stroke=AMBER, w=2.0, marker="arr")
    s += text(636, 168, "уставка", size=10.5, fill=AMBER, italic=True)

    s += line(810, yc + 48, 810, 340, stroke=INK, w=2.0)
    s += line(810, 340, 138, 340, stroke=INK, w=2.0)
    s += line(138, 340, 138, yc + 48 + 2, stroke=INK, w=2.0, marker="arr")
    s += text(474, 334, "апарат рухається → давачі міряють знову", size=11,
              anchor="middle", fill=INK)
    s += text(W / 2, H - 12,
              "Упізнавши ці імена у вихідниках, ти одразу знаєш, яку ланку "
              "контуру читаєш.", size=11.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.3.3 — HAL: один код, багато плат і симулятор
# ════════════════════════════════════════════════════════════════════════════
def fig_hal():
    W, H = 940, 440
    s = header(W, H)
    s += title(W, "HAL: один політний код — десятки плат і навіть симулятор",
               "AP_HAL ховає конкретне залізо, тож стек переноситься й тестується без ризику")
    s += rect(70, 86, 800, 66, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += text(470, 116, "Польотний код ArduPilot", size=14, weight="bold",
              anchor="middle", fill=GREEN)
    s += text(470, 138, "єдиний, незалежний від плати (оцінювач, керування, навігація)",
              size=11.5, anchor="middle", fill=INK)

    s += rect(70, 176, 800, 46, fill=PANEL, stroke=INK, sw=1.6, rx=10)
    s += text(470, 204, "AP_HAL — однаковий інтерфейс: UART · I2C · SPI · GPIO · RCOut · Scheduler",
              size=12, anchor="middle", weight="bold",
              family="Consolas, monospace")

    backs = [
        (70, "ChibiOS", "STM32: Pixhawk, Cube…", "#e3effb", BLUE),
        (275, "Linux", "одноплатники", "#e3effb", BLUE),
        (480, "ESP32", "Wi-Fi МК", "#e3effb", BLUE),
        (685, "SITL", "симуляція на ПК", "#eafaef", GREEN),
    ]
    for bx, nm, sub, fill, stroke in backs:
        s += line(bx + 92, 222, bx + 92, 268, stroke=MUTE, w=1.6, marker="arr")
        s += rect(bx, 270, 185, 74, fill=fill, stroke=stroke, sw=1.7, rx=11)
        s += text(bx + 92, 298, nm, size=13, weight="bold", anchor="middle",
                  fill=stroke)
        s += text(bx + 92, 320, sub, size=11, anchor="middle", fill=INK)

    s += text(W / 2, 384,
              "SITL — запусти ВЕСЬ стек на комп'ютері проти змодельованої фізики:",
              size=12, anchor="middle", weight="bold", fill=GREEN)
    s += text(W / 2, 404,
              "«розбивай» дрон тисячу разів безкоштовно, перш ніж торкнутися заліза.",
              size=12, anchor="middle", fill=GREEN)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.3.4 — Планувальник: таблиця задач за темпами
# ════════════════════════════════════════════════════════════════════════════
def fig_scheduler():
    W, H = 940, 430
    s = header(W, H)
    s += title(W, "Планувальник: кожна задача — у своєму темпі",
               "AP_Scheduler дає слот за пріоритетом; швидке біжить найчастіше (втілення Рис. 43.1.3)")
    tx, rx, dx = 40, 250, 420
    tw, rw, dw = 200, 160, 480
    # шапка
    s += rect(tx, 80, tw, 34, fill=INK, stroke=INK, rx=7)
    s += text(tx + 14, 103, "Задача", size=12, fill="white", weight="bold")
    s += rect(rx, 80, rw, 34, fill=INK, stroke=INK, rx=7)
    s += text(rx + 14, 103, "Частота", size=12, fill="white", weight="bold")
    s += rect(dx, 80, dw, 34, fill=INK, stroke=INK, rx=7)
    s += text(dx + 14, 103, "Що робить", size=12, fill="white", weight="bold")

    rows = [
        ("fast_loop", "400 Гц", "IMU → оцінювач → контур орієнтації", 12, True),
        ("update_GPS", "50 Гц", "оновити положення з GNSS", 5, False),
        ("update_nav", "10–50 Гц", "контур положення, навігація", 4, False),
        ("gcs_update", "50 Гц", "обмін MAVLink із землею", 5, False),
        ("update_logging", "25–400 Гц", "писати журнали польоту", 8, False),
        ("one_hz_loop", "1 Гц", "перевірки здоров'я, службове", 1, False),
    ]
    y = 114
    rh = 46
    for nm, rate, desc, dots, crit in rows:
        fill = "#eafaef" if crit else ("white" if (y // rh) % 2 else "#fafafa")
        s += rect(tx, y, tw, rh, fill=fill, stroke=MUTE, sw=1.0)
        s += text(tx + 14, y + 28, nm, size=12, weight="bold",
                  fill=GREEN if crit else INK, family="Consolas, monospace")
        s += rect(rx, y, rw, rh, fill=fill, stroke=MUTE, sw=1.0)
        s += text(rx + 14, y + 20, rate, size=12, fill=INK, weight="bold")
        for k in range(dots):
            s += circle(rx + 16 + k * 11, y + 34, 3,
                        fill=GREEN if crit else BLUE, stroke="none")
        s += rect(dx, y, dw, rh, fill=fill, stroke=MUTE, sw=1.0)
        s += text(dx + 14, y + 28, desc, size=11.5, fill=INK)
        y += rh

    s += text(W / 2, H - 14,
              "Точки = відносна частота. «fast_loop» — критичний внутрішній контур "
              "(43.2): мусить устигати кожні 2.5 мс.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.3.5 — Як це лежить у вихідниках (карта дерева)
# ════════════════════════════════════════════════════════════════════════════
def fig_tree():
    W, H = 940, 500
    s = header(W, H)
    s += title(W, "Де що шукати: карта вихідників ArduPilot",
               "імена з фігур вище — це реальні теки; ось куди дивитися")
    s += rect(50, 80, 840, 350, fill="#fbfbfd", stroke=MUTE, sw=1.5, rx=12)
    tree = [
        ("ardupilot/", "", INK),
        ("├─ ArduCopter/  ArduPlane/  Rover/  ArduSub/",
         "код апаратів: режими, головний цикл", INK),
        ("├─ libraries/", "", INK),
        ("│    ├─ AP_HAL*/", "HAL і бекенди (плата, SITL)", BLUE),
        ("│    ├─ AP_InertialSensor/ AP_GPS/ AP_Baro/",
         "драйвери давачів", BLUE),
        ("│    ├─ AP_AHRS/  AP_NavEKF3/", "оцінювач стану", INK),
        ("│    ├─ AC_AttitudeControl/ AC_PID/ AC_WPNav/",
         "керування й навігація", GREEN),
        ("│    └─ GCS_MAVLink/ AP_Logger/ AP_Param/",
         "наскрізні служби", AMBER),
        ("└─ Tools/", "SITL, autotest, скрипти", INK),
    ]
    y = 116
    for code, comment, col in tree:
        s += text(70, y, code, size=13, family="Consolas, monospace", fill=col,
                  weight="bold" if comment and col != INK else "normal")
        if comment:
            s += text(556, y, "← " + comment, size=11.5, fill=MUTE)
        y += 34

    s += rect(70, 392, 800, 30, fill="#eef2ff", stroke=BLUE, sw=1.3, rx=8)
    s += text(84, 412,
              "AP_*  — спільні бібліотеки ArduPilot   ·   AC_*  — родом з ArduCopter",
              size=12, fill=BLUE, weight="bold", family="Consolas, monospace")
    s += text(W / 2, H - 14,
              "Відкривши незнайому гілку коду, за префіксом і текою одразу видно "
              "її роль у контурі.", size=11.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.4.1 — Одна прошивка — багато апаратів через параметри
# ════════════════════════════════════════════════════════════════════════════
def fig_onefirmware():
    W, H = 940, 460
    s = header(W, H)
    s += title(W, "Одна прошивка — безліч апаратів: усе вирішують параметри",
               "той самий образ Copter стає квадро, гекса чи трикоптер — лише параметром")
    s += rect(320, 84, 300, 66, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += text(470, 110, "ArduCopter", size=15, weight="bold", anchor="middle",
              fill=GREEN)
    s += text(470, 132, "один двійковий образ (той самий код)", size=11.5,
              anchor="middle")
    frames = [(142, "Квадро", "×4 мотори", "FRAME_CLASS=1"),
              (367, "Гекса", "×6 моторів", "FRAME_CLASS=2"),
              (592, "Окто", "×8 моторів", "FRAME_CLASS=3"),
              (817, "Трикоптер", "×3 + кермо-серво", "FRAME_CLASS=7")]
    for cx, nm, sub, par in frames:
        s += line(470, 150, cx, 256, stroke=MUTE, w=1.5, marker="arr")
        s += rect(cx - 92, 258, 184, 86, fill="white", stroke=INK, sw=1.4, rx=10)
        s += text(cx, 284, nm, size=13, weight="bold", anchor="middle")
        s += text(cx, 304, sub, size=11, anchor="middle", fill=MUTE)
        s += rect(cx - 80, 316, 160, 22, fill=PANEL, stroke=MUTE, sw=1.0, rx=5)
        s += text(cx, 331, par, size=10.5, anchor="middle", weight="bold",
                  family="Consolas, monospace")
    s += text(W / 2, 396,
              "Інший ТИП апарата — літак чи ровер — то вже інший образ "
              "(ArduPlane/Rover), але та сама архітектура й ті самі бібліотеки.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Параметри — це «особистість» апарата поверх однакового коду.",
              size=12, anchor="middle", fill=GREEN, weight="bold")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.4.2 — Будова параметра: ім'я кодує сенс
# ════════════════════════════════════════════════════════════════════════════
def fig_paramanatomy():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Будова параметра: ім'я кодує сенс, значення — поведінку",
               "сотні іменованих величин у незалежній пам'яті налаштовують апарат без перекомпіляції")
    toks = [(150, 96, "ATC", "група: Attitude Control", BLUE),
            (252, 80, "RAT", "Rate — кутова швидкість", GREEN),
            (338, 80, "RLL", "Roll — вісь крену", AMBER),
            (424, 56, "P", "пропорційний коеф.", RED)]
    for x, w, t_, lab, col in toks:
        s += rect(x, 96, w, 40, fill="white", stroke=col, sw=1.7, rx=8)
        s += text(x + w / 2, 122, t_, size=15, weight="bold", anchor="middle",
                  fill=col, family="Consolas, monospace")
        s += line(x + w / 2, 136, x + w / 2, 160, stroke=col, w=1.2)
        s += text(x + w / 2, 174, lab, size=10, anchor="middle", fill=col)
    s += text(492, 122, "= 0.135", size=15, weight="bold",
              family="Consolas, monospace")
    s += text(610, 122, "← значення", size=12, fill=MUTE)
    s += text(150, 212,
              "Зберігається в незалежній пам'яті (AP_Param) — переживає "
              "перезавантаження (Розділ 19).", size=11.5, fill=INK)
    s += text(150, 250, "Приклади параметрів:", size=12.5, weight="bold")
    ex = [("BATT_LOW_VOLT = 14.0", "поріг низького заряду → failsafe"),
          ("ANGLE_MAX = 3000", "макс. нахил (у сотих градуса = 30°)"),
          ("FENCE_ENABLE = 1", "увімкнути геозону"),
          ("FS_THR_ENABLE = 1", "реакція на втрату RC-зв'язку"),
          ("AHRS_ORIENTATION = 0", "як фізично повернуто плату")]
    y = 268
    for nm, desc in ex:
        s += rect(150, y, 300, 30, fill=PANEL, stroke=MUTE, sw=1.0, rx=6)
        s += text(162, y + 20, nm, size=11.5, weight="bold",
                  family="Consolas, monospace", fill=INK)
        s += rect(458, y, 400, 30, fill="white", stroke=MUTE, sw=1.0, rx=6)
        s += text(470, y + 20, desc, size=11.5, fill=INK)
        y += 38
    s += text(W / 2, H - 12,
              "Код задає, ЩО апарат уміє; параметри — ЯК саме цей апарат це робить.",
              size=12, anchor="middle", fill=GREEN, weight="bold")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.4.3 — Наземна станція: кокпіт оператора на землі
# ════════════════════════════════════════════════════════════════════════════
def fig_gcsroles():
    W, H = 960, 430
    s = header(W, H)
    s += title(W, "Наземна станція: кокпіт оператора на землі",
               "конфігурує, планує, стежить, аналізує й командує — по MAVLink, але НЕ в контурі керування")
    s += rect(250, 78, 240, 70, fill=BOX3, stroke=AMBER, sw=1.8, rx=12)
    s += text(370, 104, "НАЗЕМНА СТАНЦІЯ", size=13.5, weight="bold",
              anchor="middle", fill=AMBER)
    s += text(370, 126, "Mission Planner · QGroundControl", size=10.5,
              anchor="middle")
    s += rect(600, 78, 240, 70, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += text(720, 104, "ПОЛІТНИЙ КОНТРОЛЕР", size=13, weight="bold",
              anchor="middle", fill=GREEN)
    s += text(720, 126, "на апараті", size=11, anchor="middle")
    s += line(490, 105, 598, 105, stroke=INK, w=2.0, marker="arr")
    s += line(598, 122, 490, 122, stroke=INK, w=2.0, marker="arr")
    s += text(544, 96, "MAVLink", size=10.5, anchor="middle", weight="bold")
    s += text(544, 142, "радіо/USB (Розд. 42)", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(110, 196, "Що робить наземна станція:", size=12.5, weight="bold")
    for x, nm, sub in [(60, "Налаштувати", "параметри + калібрування"),
                       (360, "Спланувати", "місія, точки маршруту"),
                       (660, "Стежити", "HUD: крен, висота, заряд")]:
        s += rect(x, 210, 240, 58, fill="white", stroke=AMBER, sw=1.4, rx=10)
        s += text(x + 120, 234, nm, size=12.5, weight="bold", anchor="middle")
        s += text(x + 120, 254, sub, size=10.5, anchor="middle", fill=MUTE)
    for x, nm, sub in [(210, "Аналізувати", "журнали польоту"),
                       (510, "Командувати", "arm · режим · RTL")]:
        s += rect(x, 288, 240, 58, fill="white", stroke=AMBER, sw=1.4, rx=10)
        s += text(x + 120, 312, nm, size=12.5, weight="bold", anchor="middle")
        s += text(x + 120, 332, sub, size=10.5, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 12,
              "Станція ДИВИТЬСЯ й ВЕЛИТЬ, але летить апарат сам: обірветься "
              "зв'язок — керування й failsafe лишаються на борту (43.2).",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.4.4 — Місія як послідовність точок
# ════════════════════════════════════════════════════════════════════════════
def fig_mission():
    W, H = 940, 470
    s = header(W, H)
    s += title(W, "Місія — це послідовність точок із діями",
               "станція планує точки → вантажить у FC (AP_Mission) → апарат летить сам")
    s += rect(40, 76, 860, 344, fill="#f7faf7", stroke=MUTE, sw=1.3, rx=12)
    nodes = [("home", 150, 360, "ДІМ — зліт/посадка"),
             ("1", 150, 180, "1 · Зліт на висоту"),
             ("2", 380, 120, "2 · Точка маршруту"),
             ("3", 620, 170, "3 · Очікування (Loiter)"),
             ("4", 700, 330, "4 · Точка маршруту")]
    pathpts = [(x, y) for _, x, y, _ in nodes]
    s += poly(pathpts, fill="none", stroke=INK, sw=2.4, closed=False)
    s += line(700, 330, 168, 356, stroke=AMBER, w=2.2, dash="7,5", marker="arrG")
    s += text(440, 406, "RTL → повернення додому й посадка", size=11.5,
              anchor="middle", fill=AMBER, weight="bold")
    for n, x, y, lab in nodes:
        col = GREEN if n == "home" else BLUE
        s += circle(x, y, 15, fill=col, stroke=INK, sw=1.6)
        if n != "home":
            s += text(x, y + 5, n, size=12, anchor="middle", fill="white",
                      weight="bold")
        s += rect(x + 22, y - 13, 150, 26, fill="white", stroke=col, sw=1.2,
                  rx=6)
        s += text(x + 30, y + 5, lab, size=10.5, fill=INK)
    s += text(W / 2, H - 14,
              "Той самий контур — лише уставку тепер дає список точок, а не "
              "пілот (джерело уставки з Рис. 43.1.4).",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.4.5 — Калібрування компаса: спотворена сфера → чесна
# ════════════════════════════════════════════════════════════════════════════
def fig_calibration():
    W, H = 940, 440
    s = header(W, H)
    s += title(W, "Калібрування компаса: від спотвореної сфери до чесної",
               "місцеве залізо й струми зміщують поле; «танець» з апаратом дає поправки → параметри")

    def cloud(px, head, cx, cy, ax, ay, ox, oy, col):
        o = rect(px, 86, 400, 248, fill="white", stroke=INK, sw=1.4, rx=10)
        o += text(px + 200, 80, head, size=12.5, weight="bold", anchor="middle")
        o += line(ox - 92, oy, ox + 92, oy, stroke=MUTE, w=1.0)
        o += line(ox, oy - 92, ox, oy + 92, stroke=MUTE, w=1.0)
        o += text(ox - 12, oy - 72, "0", size=10, fill=MUTE)
        for k in range(18):
            a = 2 * math.pi * k / 18
            o += circle(cx + ax * math.cos(a), cy + ay * math.sin(a), 3.5,
                        fill=col, stroke="none")
        return o

    s += cloud(40, "Сирий компас (до)", 250, 225, 78, 58, 200, 205, RED)
    s += line(200, 205, 250, 225, stroke=RED, w=1.8, dash="4,3", marker="arrR")
    s += text(120, 308, "зсув (hard iron) + стиск (soft iron)", size=10.5,
              fill=RED)
    s += cloud(500, "Після калібрування", 700, 205, 70, 70, 700, 205, GREEN)
    s += text(610, 308, "центровано на 0, кругла сфера", size=10.5, fill=GREEN)
    s += text(W / 2, 360,
              "«Танець»: обертаєш апарат у всі боки — давач описує сферу; "
              "калібрування знаходить центр і масштаб.", size=11.5,
              anchor="middle", fill=INK)
    s += text(W / 2, H - 12,
              "Поправки лягають у параметри COMPASS_OFS_* — і оцінювач "
              "(Розділ 33) знову може довіряти курсу.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.5.1 — Два мозки: політний контролер (політ) і бортовий комп'ютер (розум)
# ════════════════════════════════════════════════════════════════════════════
def fig_twobrains():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Два мозки апарата: «політ» і «розум» — поділені за роллю",
               "виділений контролер тримає апарат у повітрі; потужний комп'ютер думає — і може зависнути")

    s += rect(60, 88, 380, 304, fill=BOX2, stroke=GREEN, sw=1.9, rx=13)
    s += text(250, 120, "ПОЛІТНИЙ КОНТРОЛЕР", size=14, weight="bold",
              anchor="middle", fill=GREEN)
    s += text(250, 140, "«ПОЛІТ» — виживання", size=11.5, anchor="middle",
              fill=INK)
    for i, c in enumerate(["малий МК · RTOS або голе залізо",
                           "реальний час · детермінований",
                           "надійний · працює завжди"]):
        s += rect(80, 158 + i * 42, 340, 32, fill="white", stroke=GREEN,
                  sw=1.1, rx=7)
        s += text(250, 179 + i * 42, c, size=11.5, anchor="middle")
    s += rect(80, 300, 340, 70, fill="#d8f3e0", stroke=GREEN, sw=1.3, rx=9)
    s += lines(250, 326, ["Робота: стабілізація · оцінювач (EKF)",
                          "керування · failsafe"], size=11.5, anchor="middle",
               lh=18, weight="bold", fill=INK)

    s += rect(520, 88, 380, 304, fill="#eef2ff", stroke=BLUE, sw=1.9, rx=13)
    s += text(710, 120, "БОРТОВИЙ КОМП'ЮТЕР", size=14, weight="bold",
              anchor="middle", fill=BLUE)
    s += text(710, 140, "«РОЗУМ» — обчислення", size=11.5, anchor="middle",
              fill=INK)
    for i, c in enumerate(["Linux SBC (Raspberry Pi · Jetson)",
                           "потужний · НЕ реального часу",
                           "може зависнути — політ це переживе"]):
        s += rect(540, 158 + i * 42, 340, 32, fill="white", stroke=BLUE,
                  sw=1.1, rx=7)
        s += text(710, 179 + i * 42, c, size=11.5, anchor="middle")
    s += rect(540, 300, 340, 70, fill="#dde6ff", stroke=BLUE, sw=1.3, rx=9)
    s += lines(710, 326, ["Робота: бачення · планування",
                          "відео · ML · складна логіка"], size=11.5,
               anchor="middle", lh=18, weight="bold", fill=INK)

    # зв'язок MAVLink
    s += line(442, 215, 518, 215, stroke=INK, w=2.0, marker="arr")
    s += line(518, 240, 442, 240, stroke=INK, w=2.0, marker="arr")
    s += text(480, 205, "MAVLink", size=10, anchor="middle", weight="bold")
    s += text(480, 262, "UART", size=10, anchor="middle", fill=MUTE)

    s += text(W / 2, H - 14,
              "Бортовий комп'ютер — НАД контуром керування, не в ньому: зависне "
              "«розум» — «політ» і failsafe лишаються на виділеному контролері (43.2).",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.5.2 — Що де живе: розподіл задач між контролером і комп'ютером
# ════════════════════════════════════════════════════════════════════════════
def fig_allocation():
    W, H = 960, 500
    s = header(W, H)
    s += title(W, "Що де живе: розподіл задач за роллю",
               "критичне й швидке — на контролер; важке й розумне, але не миттєве — на комп'ютер")
    s += rect(60, 80, 400, 36, fill=BOX2, stroke=GREEN, sw=1.7, rx=8)
    s += text(260, 104, "ПОЛІТНИЙ КОНТРОЛЕР (реальний час)", size=12.5,
              weight="bold", anchor="middle", fill=GREEN)
    s += rect(500, 80, 400, 36, fill="#eef2ff", stroke=BLUE, sw=1.7, rx=8)
    s += text(700, 104, "БОРТОВИЙ КОМП'ЮТЕР (не реальний час)", size=12.5,
              weight="bold", anchor="middle", fill=BLUE)
    fc = ["Контур орієнтації (стабілізація)", "Оцінювач стану (EKF, фьюжн)",
          "Мікшер і виходи на мотори", "Failsafe й резервування",
          "RC-вхід, давачі польоту"]
    cc = ["Машинне бачення, трекінг цілі", "Візуальна одометрія / SLAM",
          "Планування маршруту", "Кодування й трансляція відео",
          "ML-інференс, складна логіка місії"]
    for i, (a, b) in enumerate(zip(fc, cc)):
        y = 130 + i * 52
        s += rect(60, y, 400, 44, fill="#f3fbf5", stroke=GREEN, sw=1.2, rx=8)
        s += text(80, y + 28, "• " + a, size=12, fill=INK)
        s += rect(500, y, 400, 44, fill="#f5f7ff", stroke=BLUE, sw=1.2, rx=8)
        s += text(520, y + 28, "• " + b, size=12, fill=INK)
    s += rect(60, 400, 840, 40, fill=PANEL, stroke=INK, sw=1.3, rx=9)
    s += text(480, 425,
              "Правило: «не впасти» — завжди ліворуч; «бути розумним» — праворуч. "
              "Перше не можна довірити тому, що буває зависає.",
              size=12, anchor="middle", weight="bold", fill=INK)
    s += text(W / 2, H - 14,
              "Багато апаратів комп'ютера не мають зовсім — і чудово літають. "
              "А ось без контролера не літає жоден.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.5.3 — Як вони говорять: guided/offboard + сторож команд
# ════════════════════════════════════════════════════════════════════════════
def fig_offboard():
    W, H = 940, 450
    s = header(W, H)
    s += title(W, "Як «розум» керує «політом»: високорівневі уставки + сторож",
               "комп'ютер каже КУДИ, контролер вирішує ЯК; замовк комп'ютер — контролер у failsafe")
    s += rect(60, 110, 270, 110, fill="#eef2ff", stroke=BLUE, sw=1.8, rx=12)
    s += text(195, 150, "БОРТОВИЙ", size=13, weight="bold", anchor="middle",
              fill=BLUE)
    s += text(195, 172, "КОМП'ЮТЕР", size=13, weight="bold", anchor="middle",
              fill=BLUE)
    s += text(195, 196, "(«розум»)", size=11, anchor="middle", fill=MUTE)
    s += rect(610, 110, 270, 110, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += text(745, 150, "ПОЛІТНИЙ", size=13, weight="bold", anchor="middle",
              fill=GREEN)
    s += text(745, 172, "КОНТРОЛЕР", size=13, weight="bold", anchor="middle",
              fill=GREEN)
    s += text(745, 196, "режим Guided / Offboard", size=10.5, anchor="middle",
              fill=MUTE)

    s += line(332, 150, 606, 150, stroke=BLUE, w=2.0, marker="arrB")
    s += text(469, 140, "уставки: «лети до X» · «тримай швидкість» · «ціль тут»",
              size=10.5, anchor="middle", fill=BLUE)
    s += line(606, 188, 334, 188, stroke=GREEN, w=2.0, marker="arrG")
    s += text(469, 206, "телеметрія: стан · положення · режим", size=10.5,
              anchor="middle", fill=GREEN)

    s += rect(250, 290, 440, 92, fill="#fff5e6", stroke=AMBER, sw=1.7, rx=12)
    s += text(470, 318, "⏱ Сторож команд", size=12.5, weight="bold",
              anchor="middle", fill=AMBER)
    s += lines(470, 340, ["Немає нових уставок довше за строк?",
                          "Контролер НЕ висить на «розумі» → сам у failsafe (утримання / RTL)."],
               size=11, anchor="middle", lh=18, fill=INK)
    s += line(195, 220, 195, 340, stroke=MUTE, w=1.4, dash="4,3")
    s += line(195, 340, 248, 340, stroke=MUTE, w=1.4, marker="arr")

    s += text(W / 2, H - 14,
              "Той самий принцип, що й з наземною станцією (43.4): джерело уставки "
              "може відмовити — контролер від цього не падає.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 43.5.4 — Уся Розділ 43 в одній карті (синтез)
# ════════════════════════════════════════════════════════════════════════════
def fig_synthesis():
    W, H = 980, 540
    s = header(W, H)
    s += title(W, "Весь розділ в одній карті: контур на борту, два джерела уставки над ним",
               "сенсори → контролер → виконавчі механізми; станція й комп'ютер лише задають мету")

    s += rect(70, 78, 360, 72, fill=BOX3, stroke=AMBER, sw=1.7, rx=12)
    s += text(250, 104, "НАЗЕМНА СТАНЦІЯ (на землі)", size=12.5, weight="bold",
              anchor="middle", fill=AMBER)
    s += text(250, 126, "оператор: параметри, місія, нагляд (43.4)", size=10.5,
              anchor="middle", fill=INK)
    s += rect(550, 78, 360, 72, fill="#eef2ff", stroke=BLUE, sw=1.7, rx=12)
    s += text(730, 104, "БОРТОВИЙ КОМП'ЮТЕР (на апараті)", size=12.5,
              weight="bold", anchor="middle", fill=BLUE)
    s += text(730, 126, "розум: бачення, планування, ML (43.5)", size=10.5,
              anchor="middle", fill=INK)

    # FC велика рамка
    s += rect(70, 210, 840, 246, fill="#f6fbf7", stroke=GREEN, sw=2.0, rx=14)
    s += text(490, 236, "ПОЛІТНИЙ КОНТРОЛЕР — серце апарата", size=13,
              weight="bold", anchor="middle", fill=GREEN)
    s += text(490, 256,
              "43.2: реальний час · надійність · резервування    |    43.3: шари HAL → драйвери → оцінювач → керування → навігація",
              size=10, anchor="middle", fill=MUTE)

    yc = 350
    blk = [(100, 150, "ДАВАЧІ", BOX1, BLUE),
           (280, 160, "ОЦІНЮВАЧ", PANEL, INK),
           (470, 160, "КЕРУВАННЯ", BOX2, GREEN),
           (660, 150, "ВИКОНАННЯ", BOX3, AMBER)]
    for x, w, t_, fill, stroke in blk:
        s += rect(x, yc - 26, w, 52, fill=fill, stroke=stroke, sw=1.6, rx=9)
        s += text(x + w / 2, yc + 5, t_, size=12, weight="bold",
                  anchor="middle", fill=stroke)
    for x1, x2 in [(250, 280), (440, 470), (630, 660)]:
        s += line(x1, yc, x2 - 3, yc, stroke=INK, w=1.8, marker="arr")
    # зворотний зв'язок
    s += line(810, yc + 26, 810, 420, stroke=INK, w=1.8)
    s += line(810, 420, 175, 420, stroke=INK, w=1.8)
    s += line(175, 420, 175, yc + 26 + 2, stroke=INK, w=1.8, marker="arr")
    s += text(492, 414, "апарат рухається → давачі міряють знову", size=10.5,
              anchor="middle", fill=INK)

    # уставки згори
    s += line(250, 150, 510, 322, stroke=AMBER, w=1.8, dash="5,4", marker="arr")
    s += line(730, 150, 560, 322, stroke=BLUE, w=1.8, dash="5,4", marker="arr")
    s += text(360, 232, "уставка", size=10, fill=AMBER, anchor="middle")
    s += text(648, 232, "уставка", size=10, fill=BLUE, anchor="middle")
    s += text(505, 300, "(MAVLink)", size=9.5, fill=MUTE, anchor="middle")

    s += rect(70, 472, 840, 36, fill="#fff5e6", stroke=AMBER, sw=1.4, rx=9)
    s += text(490, 495,
              "Обидва джерела уставки — НАД контуром. Відмовлять обидва — політ і "
              "failsafe лишаються на борту. Ось чому «політ» відділяють від «розуму».",
              size=11.5, anchor="middle", weight="bold", fill=INK)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-43-0-1-timeline.svg":     fig_timeline,
    "fig-43-0-2-thermopile.svg":   fig_thermopile,
    "fig-43-0-3-naming.svg":       fig_naming,
    "fig-43-1-1-loop.svg":         fig_loop,
    "fig-43-1-2-mapping.svg":      fig_mapping,
    "fig-43-1-3-nested.svg":       fig_nested,
    "fig-43-1-4-setpoint.svg":     fig_setpoint,
    "fig-43-1-5-openloop.svg":     fig_openloop,
    "fig-43-1-6-contrib.svg":      fig_contrib,
    "fig-43-2-1-determinism.svg":  fig_determinism,
    "fig-43-2-2-failsafe.svg":     fig_failsafe,
    "fig-43-2-3-redundancy.svg":   fig_redundancy,
    "fig-43-2-4-dedicated.svg":    fig_dedicated,
    "fig-43-2-5-watchdog.svg":     fig_watchdog,
    "fig-43-3-1-layers.svg":       fig_layers,
    "fig-43-3-2-modules.svg":      fig_modules,
    "fig-43-3-3-hal.svg":          fig_hal,
    "fig-43-3-4-scheduler.svg":    fig_scheduler,
    "fig-43-3-5-tree.svg":         fig_tree,
    "fig-43-4-1-onefirmware.svg":  fig_onefirmware,
    "fig-43-4-2-paramanatomy.svg": fig_paramanatomy,
    "fig-43-4-3-gcsroles.svg":     fig_gcsroles,
    "fig-43-4-4-mission.svg":      fig_mission,
    "fig-43-4-5-calibration.svg":  fig_calibration,
    "fig-43-5-1-twobrains.svg":    fig_twobrains,
    "fig-43-5-2-allocation.svg":   fig_allocation,
    "fig-43-5-3-offboard.svg":     fig_offboard,
    "fig-43-5-4-synthesis.svg":    fig_synthesis,
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "img")
    os.makedirs(out, exist_ok=True)
    for name, fn in FIGS.items():
        path = os.path.join(out, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(fn())
        print("wrote", os.path.relpath(path, here))


if __name__ == "__main__":
    main()
