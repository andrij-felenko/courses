# -*- coding: utf-8 -*-
"""Фігури до теми «LPDDR».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Дві різні мети: настільна DDR vs мобільна LPDDR ───────────────────────
def fig_two_targets():
    W, H = 840, 430
    frags = []

    # ліва колонка — DDR (сервер/ПК)
    frags.append(text(215, 66, "DDR — настільна / серверна", size=15, bold=True, color=NEG))
    frags.append(fitbox(70, 86, 290, 300,
        "Головна мета — МАКСИМУМ пропускної здатності.\n\n"
        "• живлення з розетки — струм майже не рахують\n"
        "• планка з кількох чіпів на спільній шині\n"
        "• довгі доріжки, багато відгалужень\n"
        "• вища напруга сигналу — щоб пробити шумну шину\n"
        "• термінація весь час палить струм\n"
        "• простій рідкісний: сервер працює 24/7\n\n"
        "Ціна за швидкість — ват — прийнятна.",
        size=12, fill="#eef2ff", stroke=NEG))

    # права колонка — LPDDR (телефон)
    frags.append(text(625, 66, "LPDDR — мобільна", size=15, bold=True, color=FIELD))
    frags.append(fitbox(480, 86, 290, 300,
        "Головна мета — МІНІМУМ енергії на біт + мізерний\nструм у простої.\n\n"
        "• живлення з батареї — кожен міліват на рахунку\n"
        "• чіп сидить упритул до процесора (PoP)\n"
        "• короткі доріжки, точка-в-точку, без термінації\n"
        "• низька напруга сигналу — розмах у сотні мВ\n"
        "• глибокі режими сну між зверненнями\n"
        "• розумна регенерація: гріти лиш зайняте й холодно\n\n"
        "Швидкість важлива, але НЕ ціною батареї.",
        size=12, fill="#eafaf1", stroke=FIELD))

    # низ — спільна комірка
    frags.append(fitbox(150, 396, 540, 30,
        "Комірка DRAM під обома — та сама. Різниця вся у ФІЗИЧНОМУ рівні й керуванні живленням.",
        size=12, fill="#fffef0", stroke="#caa300"))

    render(os.path.join(IMG, "two-targets.svg"), W, H, *frags,
           title="DDR цілиться в пропускну здатність, LPDDR — в енергію на біт")


# ── 2. Низький розмах: енергія перемикання лінії ∝ розмах² ───────────────────
def fig_low_swing():
    W, H = 840, 440
    frags = []

    # ліва вісь — напруга; малюємо два «розмахи» як прямокутні хвилі
    def wave(x0, y_gnd, swing_px, unit, patt, color, label, vlabel):
        y_hi = y_gnd - swing_px
        out = [line(x0 - 10, y_gnd, x0 + len(patt) * unit + 10, y_gnd, color=MUTED, sw=1, dash="3,3")]
        out.append(text(x0 - 16, y_gnd + 4, "0 В", size=10, color=MUTED, anchor="end"))
        out.append(text(x0 - 16, y_hi + 4, vlabel, size=10, color=color, anchor="end", bold=True))
        x = x0
        prev = None
        for c in patt:
            y = y_hi if c == '1' else y_gnd
            if prev is not None and prev != y:
                out.append(line(x, prev, x, y, color=color, sw=2.6))
            out.append(line(x, y, x + unit, y, color=color, sw=2.6))
            prev = y
            x += unit
        out.append(text(x0 + len(patt) * unit / 2, y_hi - 12, label, size=12.5, color=color, bold=True))
        # двобічна стрілка розмаху
        xa = x0 + len(patt) * unit + 24
        out.append(line(xa, y_hi, xa, y_gnd, color=color, sw=1.4))
        out.append(line(xa - 4, y_hi, xa + 4, y_hi, color=color, sw=1.4))
        out.append(line(xa - 4, y_gnd, xa + 4, y_gnd, color=color, sw=1.4))
        return "".join(out), xa

    unit = 46
    patt = "10110"
    # DDR-подібний великий розмах
    s1, _ = wave(150, 150, 96, unit, patt, NEG, "великий розмах (класична DDR)", "1.5 В")
    frags.append(s1)
    # LPDDR малий розмах
    s2, _ = wave(150, 320, 40, unit, patt, FIELD, "малий розмах (LPDDR4X, VDDQ 0.6 В)", "0.6 В")
    frags.append(s2)

    # праворуч — «шкала струму/енергії» стовпчиками
    bx = 560
    frags.append(text(bx + 110, 104, "енергія перемикання ∝ розмах²", size=12.5, bold=True, color=INK))
    # стовпчик 1: (1.5)² = 2.25
    frags.append(rect(bx + 40, 130, 60, 150, fill="#eaf0fd", stroke=NEG, sw=1.6))
    frags.append(text(bx + 70, 300, "1.5² ≈ 2.25", size=11, color=NEG, bold=True))
    frags.append(text(bx + 70, 318, "«одиниць»", size=10, color=MUTED))
    # стовпчик 2: (0.6)² = 0.36  → у ~6.25× менше
    frags.append(rect(bx + 160, 256, 60, 24, fill="#eafaf1", stroke=FIELD, sw=1.6))
    frags.append(text(bx + 190, 300, "0.6² ≈ 0.36", size=11, color=FIELD, bold=True))
    frags.append(text(bx + 190, 318, "≈ у 6× менше", size=10, color=FIELD, bold=True))

    frags.append(fitbox(70, 372, 700, 56,
        "Заряджати ємність лінії до меншої напруги дешевше КВАДРАТИЧНО: половину розмаху —\n"
        "чверть енергії на кожен перемик. Тому LPDDR тисне напругу сигналу вниз аж до сотень мВ.\n"
        "Розплата — менший запас над завадами, тож коротка доріжка точка-в-точку тут обов'язкова.",
        size=12, fill="#f7fdfa", stroke=FIELD))

    render(os.path.join(IMG, "low-swing.svg"), W, H, *frags,
           title="Малий розмах напруги — квадратична економія енергії на кожен біт")


# ── 3. Розумна регенерація: PASR (тільки зайняте) + TCSR (рідше на холоді) ───
def fig_smart_refresh():
    W, H = 840, 430
    frags = []

    # ---- PASR: масив із 8 банків, регенеруємо лише перші 2 ----
    frags.append(text(210, 66, "PASR — гріти лише зайняту частину", size=13.5, bold=True, color=FIELD))
    n = 8
    bw, bh = 44, 60
    x0, y0 = 70, 90
    gap = 6
    active = [True, True, False, False, False, False, False, False]
    for i in range(n):
        x = x0 + i * (bw + gap)
        on = active[i]
        fill = "#eafaf1" if on else "#f1f1f3"
        stroke = FIELD if on else MUTED
        frags.append(rect(x, y0, bw, bh, fill=fill, stroke=stroke, sw=1.8, rx=4))
        frags.append(text(x + bw / 2, y0 + bh / 2 + 4, "банк\n" + str(i), size=9.5,
                          color=(FIELD if on else MUTED)))
        if on:
            frags.append(text(x + bw / 2, y0 + bh + 16, "греємо", size=9, color=FIELD, bold=True))
        else:
            frags.append(text(x + bw / 2, y0 + bh + 16, "спить", size=9, color=MUTED))
    frags.append(fitbox(70, y0 + bh + 34, 700, 46,
        "Дані живуть лише у двох банках — решту регенерувати нема сенсу. Система каже чіпові,\n"
        "які банки тримати живими; решта не оновлюється й струму не їсть (вміст там втрачається).",
        size=11.5, fill="#f7fdfa", stroke=FIELD))

    # ---- TCSR: період регенерації залежить від температури ----
    ty = 250
    frags.append(text(210, ty + 6, "TCSR — на холоді регенерувати рідше", size=13.5, bold=True, color=POS))
    # осі
    ax0, ay0, aw, ah = 90, ty + 30, 300, 110
    frags.append(line(ax0, ay0, ax0, ay0 + ah, color=INK, sw=1.6))      # вісь Y
    frags.append(line(ax0, ay0 + ah, ax0 + aw, ay0 + ah, color=INK, sw=1.6))  # вісь X
    frags.append(text(ax0 - 8, ay0 + 6, "часто", size=10, color=MUTED, anchor="end"))
    frags.append(text(ax0 - 8, ay0 + ah, "рідко", size=10, color=MUTED, anchor="end"))
    frags.append(text(ax0 - 14, ay0 + ah / 2, "як часто", size=10, color=INK, anchor="end"))
    frags.append(text(ax0 - 14, ay0 + ah / 2 + 14, "гріємо", size=10, color=INK, anchor="end"))
    frags.append(text(ax0, ay0 + ah + 16, "холодно", size=10, color=NEG))
    frags.append(text(ax0 + aw, ay0 + ah + 16, "гаряче", size=10, color=POS, anchor="end"))
    # крива: спадає при холоді (рідко), круто росте при жарі (часто) — струм витоку ∝ температурі
    pts = []
    for i in range(41):
        t = i / 40.0
        # витік росте експоненційно з температурою → частота теж
        val = math.exp(2.4 * (t - 1.0))
        y = ay0 + ah - (ah - 8) * val
        pts.append((ax0 + t * aw, y))
    for a, b in zip(pts, pts[1:]):
        frags.append(line(a[0], a[1], b[0], b[1], color=POS, sw=2.6))

    frags.append(fitbox(424, ty + 22, 346, 152,
        "Комірка тримає заряд довше, коли\n"
        "чіп холодний: витік крізь транзистор\n"
        "різко спадає з температурою. Датчик\n"
        "тепла це вимірює — чіп сам розріджує\n"
        "регенерацію на холоді, а на спеці згущує.\n\n"
        "Разом PASR і TCSR роблять сон LPDDR\n"
        "ощадним: у простої гріємо лічені банки\n"
        "лічені рази.",
        size=11.5, fill="#fdf2f2", stroke=POS))

    render(os.path.join(IMG, "smart-refresh.svg"), W, H, *frags,
           title="PASR гріє лише зайняті банки, TCSR розріджує регенерацію на холоді")


if __name__ == "__main__":
    fig_two_targets()
    fig_low_swing()
    fig_smart_refresh()
    print("OK: 3 SVG у", IMG)
