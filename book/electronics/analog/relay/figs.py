# -*- coding: utf-8 -*-
"""Фігури до статті «Реле» (book/electronics/analog/relay).
Чотири фігури:
  idea.svg     — суть: слабке коло керує сильним, два кола розв'язані (ізоляція)
  inside.svg   — механізм: котушка → магніт тягне якір → пружина → перемикаються контакти
  forms.svg    — конфігурації контактів: форма A (NO), форма B (NC), форма C (перекидний)
  flyback.svg  — пастка: котушка-індуктивність дає викид напруги; діод-обхідник його гасить
  repeater.svg — історія: реле як телеграфний повторювач (кволий вхід → свіже повносиле коло)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ─────────────────────────────────────────────────────────
def gnd(cx, y):
    return "".join([
        line(cx, y, cx, y + 7, color=INK, sw=1.8),
        line(cx - 12, y + 7, cx + 12, y + 7, color=INK, sw=2.2),
        line(cx - 7, y + 12, cx + 7, y + 12, color=INK, sw=2.0),
        line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)])


def coil(x, y0, y1, color=NEG, sw=2.0, loops=4):
    """Котушка-індуктивність: ланцюжок напівкіл уздовж вертикалі (x, y0..y1)."""
    out = [line(x, y0, x, y0 + 6, color=color, sw=sw)]
    seg = (y1 - y0 - 12) / loops
    yy = y0 + 6
    for _ in range(loops):
        out.append('<path d="M %.1f %.1f A %.1f %.1f 0 1 1 %.1f %.1f" '
                    'fill="none" stroke="%s" stroke-width="%.1f"/>'
                    % (x, yy, seg / 2, seg / 2, x, yy + seg, color, sw))
        yy += seg
    out.append(line(x, yy, x, y1, color=color, sw=sw))
    return "".join(out)


def battery(cx, cy, label=None, color=INK):
    """Маленька батарейка-джерело (горизонтальні пластини), вивід зверху/знизу."""
    out = [line(cx, cy - 16, cx, cy - 6, color=color, sw=1.8),
           line(cx - 11, cy - 6, cx + 11, cy - 6, color=color, sw=2.6),   # +
           line(cx - 6, cy, cx + 6, cy, color=color, sw=1.4),             # −
           line(cx, cy, cx, cy + 12, color=color, sw=1.8)]
    if label:
        out.append(text(cx - 16, cy - 2, label, size=12, color=color, bold=True, anchor="end"))
    return "".join(out), (cx, cy - 16), (cx, cy + 12)


def lamp(cx, cy, r=15, color=POS):
    """Навантаження-лампа: кружечок із хрестиком."""
    k = r * 0.7
    return "".join([
        circle(cx, cy, r, fill="#fff7f5", stroke=color, sw=2),
        line(cx - k, cy - k, cx + k, cy + k, color=color, sw=1.6),
        line(cx - k, cy + k, cx + k, cy - k, color=color, sw=1.6)])


def diode(cx, cy, color=FIELD, sw=2.0, up=True):
    """Діод-трикутник зі смужкою; провідний напрям — за вершиною трикутника.
    up=True → пропускає струм ВГОРУ (вершина зверху, катод-смужка зверху)."""
    s = 9
    if up:
        tri = '<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="%.1f"/>' \
              % (cx - s, cy + s, cx + s, cy + s, cx, cy - s, "#eafaf0", color, sw)
        bar = line(cx - s, cy - s, cx + s, cy - s, color=color, sw=2.6)
    else:
        tri = '<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="%.1f"/>' \
              % (cx - s, cy - s, cx + s, cy - s, cx, cy + s, "#eafaf0", color, sw)
        bar = line(cx - s, cy + s, cx + s, cy + s, color=color, sw=2.6)
    return tri + bar


# ════════════════════════════════════════════════════════════════════════════
# 1. idea.svg — слабке коло керує сильним; між ними нема електричного зв'язку
# ════════════════════════════════════════════════════════════════════════════
def fig_idea():
    W, H = 660, 330
    f = []

    # ліва панель — кероване (слабке) коло
    f.append(rect(40, 60, 250, 210, fill="#eef3fd", stroke=NEG, sw=2, rx=12))
    f.append(text(165, 86, "КЕРУВАННЯ", size=14, bold=True, color=NEG))
    f.append(text(165, 105, "слабке коло: 5 В, міліампери", size=11, color=MUTED))

    # права панель — комутоване (сильне) коло
    f.append(rect(370, 60, 250, 210, fill="#fdeeec", stroke=POS, sw=2, rx=12))
    f.append(text(495, 86, "НАВАНТАЖЕННЯ", size=14, bold=True, color=POS))
    f.append(text(495, 105, "сильне коло: 230 В, ампери", size=11, color=MUTED))

    # котушка в лівій панелі
    f.append(coil(120, 150, 230, color=NEG))
    f.append(text(150, 200, "котушка", size=12, color=NEG, anchor="start"))
    f.append(text(150, 216, "(електромагніт)", size=10, color=MUTED, anchor="start"))
    bb, t1, b1 = battery(120, 150 - 18 + 4)
    # маленьке джерело керування вгорі лівої котушки
    f.append(line(120, 150, 120, 130, color=NEG, sw=1.6))
    f.append(text(120, 124, "5 В", size=11, color=NEG, bold=True))

    # навантаження + контакт у правій панелі
    f.append(lamp(495, 175))
    f.append(text(495, 210, "увімкнеться,", size=11, color=POS))
    f.append(text(495, 225, "коли спрацює реле", size=11, color=MUTED))

    # центр: фізичний місток — магнітне поле, НЕ дріт
    f.append(line(232, 165, 300, 165, color=NEG, sw=1.6, dash="2 4"))
    f.append('<path d="M 300 130 Q 330 165 300 200" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 4"/>' % MUTED)
    f.append('<path d="M 360 130 Q 330 165 360 200" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 4"/>' % MUTED)
    f.append(text(330, 150, "магнітне", size=11, color=MUTED))
    f.append(text(330, 165, "поле", size=11, color=MUTED))
    f.append(line(360, 165, 420, 165, color=POS, sw=1.6, dash="2 4"))

    body, w0, h0 = textbox(W / 2, 300,
                           "Кола з'єднані лише полем, не дротом — між ними нема\nструмопровідного містка (гальванічна розв'язка)",
                           size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "idea.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. inside.svg — механізм: котушка → якір → пружина → контакти
# ════════════════════════════════════════════════════════════════════════════
def fig_inside():
    W, H = 680, 380
    f = []
    f.append(text(W / 2, 34, "Що всередині: струм у котушці притягує якір і перемикає контакт",
                  size=14, bold=True))

    # осердя + котушка ліворуч
    corex, corey0, corey1 = 150, 110, 300
    f.append(rect(corex - 14, corey0, 28, corey1 - corey0, fill="#e8eaee", stroke=INK, sw=1.6, rx=3))
    f.append(text(corex, corey1 + 22, "осердя", size=11, color=MUTED))
    # обмотка навколо осердя
    for i in range(7):
        yy = corey0 + 14 + i * 24
        f.append('<path d="M %.1f %.1f A 20 11 0 1 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (corex - 14, yy, corex + 14, yy + 12, NEG))
    f.append(text(corex - 40, corey0 - 6, "котушка", size=12, color=NEG, bold=True, anchor="start"))

    # струм у котушку
    f.append(arrow(corex, corey0 - 28, corex, corey0 - 6, color=NEG, sw=2.4))
    f.append(text(corex + 16, corey0 - 18, "I_кат", size=12, color=NEG, bold=True, anchor="start"))

    # верхня магнітна планка (ярмо) — від верху осердя праворуч до шарніра
    yokey = corey0 - 2
    pivx = 430
    f.append(line(corex, yokey, pivx, yokey, color=INK, sw=4))
    f.append(circle(pivx, yokey, 4, fill=INK, stroke=INK))           # шарнір якоря
    f.append(text(pivx + 8, yokey - 4, "шарнір", size=10, color=MUTED, anchor="start"))

    # ЯКІР — важіль від шарніра вниз-вліво до зазору над осердям (притягнутий стан — пунктир)
    armtipx, armtipy = corex, corey0 + 22
    f.append(line(pivx, yokey, armtipx + 10, armtipy, color=POS, sw=4))      # якір (поточний стан)
    f.append(text((pivx + armtipx) / 2, armtipy - 26, "якір (рухомий важіль)",
                  size=12, color=POS, bold=True))
    # сила притягання
    f.append(arrow(armtipx + 6, armtipy - 14, armtipx + 4, armtipy - 2, color=NEG, sw=2.2))
    f.append(text(armtipx + 40, armtipy - 6, "магніт тягне вниз", size=10, color=NEG, anchor="start"))

    # пружина повернення — тягне якір угору (праворуч від шарніра)
    sx = pivx + 50
    f.append('<path d="M %.0f %.0f l 8 -6 l -16 -6 l 16 -6 l -16 -6 l 8 -5" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (sx, yokey + 6, FIELD))
    f.append(line(pivx, yokey, sx, yokey + 6, color=POS, sw=2))
    f.append(text(sx + 18, yokey + 2, "пружина", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(sx + 18, yokey + 16, "(повертає назад)", size=10, color=MUTED, anchor="start"))

    # КОНТАКТИ праворуч унизу — рухомий (на якорі) між двома нерухомими
    cx = 540
    movy = 230
    f.append(line(pivx, yokey, cx, movy - 30, color=POS, sw=2))      # тяга від якоря до рухомого контакту
    # рухомий контакт
    f.append(circle(cx, movy, 4, fill=POS, stroke=POS))
    f.append(text(cx + 12, movy + 4, "рухомий контакт", size=10, color=POS, anchor="start"))
    # нерухомі: NO (нижче, зараз торкається) і NC (вище)
    f.append(circle(cx, movy + 30, 4, fill=INK, stroke=INK))
    f.append(line(cx, movy + 4, cx, movy + 26, color=POS, sw=2.4))   # замкнено на NO
    f.append(text(cx + 12, movy + 34, "NO (замкнувся)", size=10, color=INK, anchor="start"))
    f.append(circle(cx, movy - 30, 4, fill=MUTED, stroke=MUTED))
    f.append(text(cx + 12, movy - 26, "NC (відпав)", size=10, color=MUTED, anchor="start"))

    # підпис-причинність унизу
    body, w0, h0 = textbox(W / 2, 352,
                           "Струм → поле в осерді → якір притягується, стискаючи пружину → рухомий контакт перекидається",
                           size=11, color=INK, fill="#f4f6f8", stroke=INK)
    f.append(body)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. forms.svg — три типи контактів: A (NO), B (NC), C (перекидний)
# ════════════════════════════════════════════════════════════════════════════
def fig_forms():
    W, H = 680, 300
    f = []
    f.append(text(W / 2, 32, "Три базові форми контактів реле", size=14, bold=True))

    def common(cx, cy):
        return circle(cx, cy, 4, fill=INK, stroke=INK)

    def fixed(cx, cy, col=INK):
        return circle(cx, cy, 4, fill=col, stroke=col)

    # ── Форма A: нормально розімкнений (NO) ──
    ax = 130
    f.append(text(ax, 80, "Форма A", size=13, bold=True, color=FIELD))
    f.append(text(ax, 98, "нормально розімкнений (NO)", size=10, color=MUTED))
    f.append(common(ax - 40, 150))
    f.append(text(ax - 40, 175, "COM", size=10, color=MUTED))
    f.append(fixed(ax + 40, 150))
    f.append(text(ax + 40, 175, "NO", size=10, color=MUTED))
    # рухома лапка — піднята (розімкнено в спокої)
    f.append(line(ax - 40, 150, ax + 18, 124, color=INK, sw=2.4))
    f.append(text(ax, 220, "у спокої — розрив;", size=10, color=INK))
    f.append(text(ax, 234, "спрацює — з'єднує", size=10, color=FIELD, bold=True))

    # ── Форма B: нормально замкнений (NC) ──
    bx = 340
    f.append(text(bx, 80, "Форма B", size=13, bold=True, color=POS))
    f.append(text(bx, 98, "нормально замкнений (NC)", size=10, color=MUTED))
    f.append(common(bx - 40, 150))
    f.append(text(bx - 40, 175, "COM", size=10, color=MUTED))
    f.append(fixed(bx + 40, 150))
    f.append(text(bx + 40, 175, "NC", size=10, color=MUTED))
    # рухома лапка — лежить (замкнено в спокої)
    f.append(line(bx - 40, 150, bx + 40, 150, color=INK, sw=2.4))
    f.append(text(bx, 220, "у спокої — з'єднано;", size=10, color=INK))
    f.append(text(bx, 234, "спрацює — розриває", size=10, color=POS, bold=True))

    # ── Форма C: перекидний (SPDT) ──
    cx0 = 555
    f.append(text(cx0, 80, "Форма C", size=13, bold=True, color=NEG))
    f.append(text(cx0, 98, "перекидний (SPDT)", size=10, color=MUTED))
    f.append(common(cx0 - 44, 150))
    f.append(text(cx0 - 44, 175, "COM", size=10, color=MUTED))
    f.append(fixed(cx0 + 36, 124, col=MUTED))
    f.append(text(cx0 + 44, 120, "NC", size=10, color=MUTED, anchor="start"))
    f.append(fixed(cx0 + 36, 176, col=FIELD))
    f.append(text(cx0 + 44, 182, "NO", size=10, color=FIELD, anchor="start"))
    # рухома лапка — зараз на NC (спокій)
    f.append(line(cx0 - 44, 150, cx0 + 36, 124, color=INK, sw=2.4))
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="3 3"/>'
             % (cx0 + 10, 138, cx0 + 24, 158, cx0 + 36, 174, NEG))
    f.append(text(cx0, 220, "перекидає COM", size=10, color=INK))
    f.append(text(cx0, 234, "з NC на NO", size=10, color=NEG, bold=True))

    f.append(text(W / 2, 274, "Багатоконтактні реле — це просто кілька таких груп на одному якорі (2C = DPDT)",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "forms.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. flyback.svg — викид напруги на котушці й діод-обхідник
# ════════════════════════════════════════════════════════════════════════════
def fig_flyback():
    W, H = 680, 360
    f = []
    f.append(text(W / 2, 32, "Котушка — індуктивність: рвеш струм — отримуєш викид напруги",
                  size=14, bold=True))

    # ── ліва частина: схема ключ-котушка-діод ──
    top = 80
    railx0, railx1 = 70, 250
    f.append(line(railx0, top, railx1, top, color=INK, sw=2.2))
    f.append(text(railx0 - 6, top - 8, "+V", size=12, bold=True, anchor="start"))

    coilx = 130
    f.append(coil(coilx, top, top + 110, color=NEG))
    f.append(text(coilx - 16, top + 55, "котушка", size=11, color=NEG, bold=True, anchor="end"))
    f.append(text(coilx - 16, top + 70, "реле (L)", size=10, color=MUTED, anchor="end"))

    # діод паралельно котушці (катод до +V, провідний угору при викиді)
    diox = 210
    f.append(line(diox, top, diox, top + 28, color=FIELD, sw=2))
    f.append(diode(diox, top + 42, color=FIELD, up=True))
    f.append(line(diox, top + 52, diox, top + 110, color=FIELD, sw=2))
    f.append(line(coilx, top, diox, top, color=INK, sw=2))
    f.append(line(coilx, top + 110, diox, top + 110, color=INK, sw=2))
    f.append(text(diox + 12, top + 46, "діод-", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(diox + 12, top + 60, "обхідник", size=11, color=FIELD, bold=True, anchor="start"))

    # ключ знизу
    swy = top + 150
    f.append(line(coilx, top + 110, coilx, swy - 8, color=INK, sw=2))
    f.append(line(coilx, swy - 8, coilx + 26, swy - 22, color=INK, sw=2.4))   # розімкнений ключ
    f.append(circle(coilx, swy - 8, 3, fill=INK, stroke=INK))
    f.append(circle(coilx + 30, swy - 24, 3, fill=INK, stroke=INK))
    f.append(text(coilx + 36, swy - 18, "ключ розмикається", size=10, color=POS, anchor="start"))
    f.append(line(coilx + 30, swy - 24, coilx + 30, swy, color=INK, sw=2))
    f.append(line(diox, top + 110, diox, swy, color=FIELD, sw=2))
    f.append(line(coilx + 30, swy, diox, swy, color=INK, sw=2))
    f.append(gnd((coilx + 30 + diox) / 2, swy))

    # струм у петлі діод-котушка при викиді
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5 4"/>'
             % (coilx, top + 6, (coilx + diox) / 2, top - 18, diox, top + 6, FIELD))
    f.append(text((coilx + diox) / 2, top - 22, "струм добігає колом", size=10, color=FIELD))

    # ── права частина: осцилограма напруги без діода й з діодом ──
    ox, oy = 380, 250
    axw, axh = 250, 150
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 22, "час", size=11, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - axh + 6, "напруга", size=11, color=INK, anchor="end"))
    # момент розмикання
    tcut = ox + 70
    f.append(line(tcut, oy, tcut, oy - axh + 10, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(tcut, oy + 18, "ключ off", size=10, color=MUTED))

    # рівень живлення
    vlev = oy - 40
    f.append(line(ox, vlev, tcut, vlev, color=INK, sw=2))
    f.append(text(ox + 4, vlev - 6, "+V", size=10, color=INK, anchor="start"))

    # БЕЗ діода — гострий викид угору (далеко за межі)
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (tcut, vlev, tcut + 2, oy - axh + 4, tcut + 16, oy - 30, tcut + 70, oy - 36, POS))
    f.append(text(tcut + 30, oy - axh - 2, "без діода: викид", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(tcut + 30, oy - axh + 12, "сотні вольтів ↯", size=10, color=POS, anchor="start"))

    # З діодом — обмежено трохи вище +V, плавний спад
    f.append('<path d="M %.0f %.0f L %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (tcut, vlev, tcut + 3, vlev - 12, tcut + 50, oy - 6, ox + axw - 20, oy - 4, FIELD))
    f.append(text(tcut + 96, vlev - 18, "з діодом: ≈ +0.7 В", size=10, color=FIELD, bold=True, anchor="start"))

    body, w0, h0 = textbox(W / 2, 336,
                           "Без обхідника викид пробиває ключ; діод дає струму замкнене коло — напруга падає до краплі на діоді",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "flyback.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. repeater.svg — реле як телеграфний повторювач: кволий вхід → свіже коло
# ════════════════════════════════════════════════════════════════════════════
def fig_repeater():
    W, H = 720, 320
    f = []
    f.append(text(W / 2, 32, "Реле-повторювач: кволий струм відмикає свіже повносиле коло",
                  size=14, bold=True))

    midy = 170

    # ── ЛІВОРУЧ: довга лінія, сигнал згасає ──────────────────────────────────
    f.append(text(120, 70, "довга лінія (сотні км)", size=11, color=MUTED))
    # стрілка-сигнал, що згасає: товщина й колір тануть зліва направо
    sx0 = 40
    f.append(line(sx0, midy, 150, midy, color=NEG, sw=4.5))
    f.append(line(150, midy, 250, midy, color=NEG, sw=2.2))
    f.append('<line x1="250" y1="%d" x2="300" y2="%d" stroke="%s" stroke-width="1.2" stroke-dasharray="3 4"/>'
             % (midy, midy, MUTED))
    f.append(text(95, midy - 12, "сильний", size=10, color=NEG))
    f.append(text(265, midy - 12, "кволий", size=10, color=MUTED))

    # ── ЦЕНТР: чутлива котушка реле ловить кволий струм ──────────────────────
    f.append(coil(310, midy - 48, midy + 48, color=NEG, loops=5))
    f.append(text(310, midy + 78, "чутлива", size=11, color=NEG))
    f.append(text(310, midy + 93, "котушка реле", size=11, color=NEG))
    f.append(line(300, midy, 310, midy, color=MUTED, sw=1.2, dash="3 4"))

    # якір/контакт реле: кволий магніт перемикає окреме коло
    f.append(line(310, midy - 48, 360, midy - 70, color=POS, sw=3))      # якір-важіль
    f.append(circle(360, midy - 70, 4, fill=POS, stroke=POS))            # рухомий контакт
    f.append(circle(390, midy - 70, 4, fill=INK, stroke=INK))           # нерухомий контакт
    f.append(text(375, midy - 82, "контакт", size=10, color=POS))

    # пунктирна рамка «реле» навколо котушки+контакту — підкреслити розв'язку
    f.append(rect(285, midy - 95, 130, 200, fill="none", stroke=MUTED, sw=1.4, rx=10))
    f.append('<rect x="285" y="%d" width="130" height="200" rx="10" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="5 4"/>'
             % (midy - 95, MUTED))
    f.append(text(350, midy - 104, "РЕЛЕ", size=11, bold=True, color=MUTED))

    # ── ПРАВОРУЧ: свіже коло з новою батареєю жене сигнал далі ───────────────
    bx = 470
    bb, t1, b1 = battery(bx, midy)
    f.append(bb)
    f.append(text(bx - 18, midy - 2, "свіжа", size=11, color=INK, bold=True, anchor="end"))
    f.append(text(bx - 18, midy + 12, "батарея", size=10, color=MUTED, anchor="end"))
    # коло: батарея → контакт реле (верх) і батарея → лінія далі (низ)
    f.append(line(bx, midy - 16, bx, midy - 70, color=INK, sw=1.8))
    f.append(line(bx, midy - 70, 390, midy - 70, color=INK, sw=1.8))     # до нерухомого контакту
    f.append(line(bx, midy + 12, bx, midy + 60, color=POS, sw=1.8))
    f.append(line(bx, midy + 60, 560, midy + 60, color=POS, sw=1.8))
    f.append(line(560, midy + 60, 560, midy, color=POS, sw=1.8))

    # свіжий повносилий сигнал на наступну ділянку
    f.append(line(560, midy, 690, midy, color=POS, sw=4.5))
    f.append(text(625, midy - 12, "знову сильний —", size=11, color=POS))
    f.append(text(625, midy + 24, "на наступну станцію", size=11, color=MUTED))

    body, w0, h0 = textbox(W / 2, 295,
                           "Кволий струм не тягне приймач сам — він лише вмикає реле;\n"
                           "далі сигнал жене свіже коло. Згасання долається скільки завгодно разів.",
                           size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "repeater.svg"), W, H, *f)


if __name__ == "__main__":
    fig_idea()
    fig_inside()
    fig_forms()
    fig_flyback()
    fig_repeater()
    print("OK: 5 фігур у", IMG)
