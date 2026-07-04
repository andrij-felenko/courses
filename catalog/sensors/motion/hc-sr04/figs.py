# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «HC-SR04 — ультразвуковий далекомір».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Принцип: луна летить туди й назад, час → відстань ───────────────────────
def fig_echo_principle():
    W, H = 880, 400
    f = [text(W / 2, 30, "Модуль міряє ЧАС, а не відстань: луна летить до перешкоди й назад",
              size=15, bold=True)]

    # Модуль ліворуч — два «ока» (передавач/приймач)
    mx, my, mw, mh = 40, 120, 120, 150
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(circle(mx + 40, my + 60, 26, fill="#dfe6f0", stroke=INK, sw=1.6))
    f.append(circle(mx + 40, my + 60, 12, fill=BG, stroke=MUTED, sw=1.2))
    f.append(circle(mx + 40, my + 118, 26, fill="#dfe6f0", stroke=INK, sw=1.6))
    f.append(circle(mx + 40, my + 118, 12, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(mx + 88, my + 64, "T", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(mx + 88, my + 122, "R", size=13, bold=True, color=NEG, anchor="start"))
    f.append(text(mx + mw / 2, my + mh + 22, "HC-SR04", size=12, bold=True))
    f.append(text(mx + mw / 2, my + mh + 40, "T — передавач", size=9.5, color=POS))
    f.append(text(mx + mw / 2, my + mh + 56, "R — приймач", size=9.5, color=NEG))

    # Перешкода праворуч
    ox = 720
    f.append(rect(ox, 100, 60, 200, fill="#f0ece0", stroke=MUTED, sw=1.8, rx=6))
    f.append(text(ox + 30, 90, "перешкода", size=11, bold=True, color=MUTED))

    # Хвиля туди (від T, згори) — червона стрілка
    f.append(arrow(mx + mw + 8, 180, ox - 6, 180, color=POS, sw=2.4))
    f.append(text((mx + mw + ox) / 2, 166, "1 · імпульс 40 кГц летить уперед", size=11, color=POS, bold=True))
    f.append(text((mx + mw + ox) / 2, 200, "8 хвиль у пачці", size=9.5, color=MUTED, italic=True))

    # Хвиля назад (до R, знизу) — синя
    f.append(arrow(ox - 6, 238, mx + mw + 8, 238, color=NEG, sw=2.4))
    f.append(text((mx + mw + ox) / 2, 260, "2 · відбита луна вертається до R", size=11, color=NEG, bold=True))

    # Нижня рамка: формула
    b, _, _ = textbox(W / 2, 344,
                      "час туди-й-назад t  →  відстань s = t · 340 / 2   (звук ~340 м/с; ділимо на 2 — луна пройшла шлях двічі)",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    b2, _, _ = textbox(W / 2, 382,
                       "зручна форма для мікроконтролера:  s(см) = t(мкс) / 58",
                       size=11.5, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
    f.append(b2)
    render(os.path.join(IMG, "echo-principle.svg"), W, H, *f)


# ── 2. Часова діаграма: TRIG-імпульс → пачка → ширина ECHO ─────────────────────
def fig_timing():
    W, H = 900, 470
    f = [text(W / 2, 30, "Протокол у часі: ти даєш поштовх на TRIG, модуль відповідає ширшим чи вужчим ECHO",
              size=14, bold=True)]

    left = 130          # де починаються назви ліній
    base = 210          # рівень «низько» для TRIG
    hi = 60             # висота імпульсу
    t0 = 200            # старт імпульсу TRIG по X
    tw = 60             # ширина TRIG-імпульсу (10 мкс)

    # --- Лінія TRIG ---
    f.append(text(left - 10, base - hi / 2, "TRIG", size=12, bold=True, color=POS, anchor="end"))
    f.append(text(left - 10, base - hi / 2 + 16, "(вхід)", size=9, color=MUTED, anchor="end"))
    # низько-високо-низько
    f.append(line(left, base, t0, base, color=POS, sw=2.2))
    f.append(line(t0, base, t0, base - hi, color=POS, sw=2.2))
    f.append(line(t0, base - hi, t0 + tw, base - hi, color=POS, sw=2.2))
    f.append(line(t0 + tw, base - hi, t0 + tw, base, color=POS, sw=2.2))
    f.append(line(t0 + tw, base, 830, base, color=POS, sw=2.2))
    # розмір 10 мкс над імпульсом
    f.append(line(t0, base - hi - 14, t0 + tw, base - hi - 14, color=INK, sw=1.2))
    f.append(text(t0 + tw / 2, base - hi - 20, "10 мкс", size=10, color=INK, bold=True))

    # --- Пачка 40 кГц (окрема доріжка) ---
    yb = base + 70
    f.append(text(left - 10, yb - 6, "звук", size=12, bold=True, color=MUTED, anchor="end"))
    f.append(text(left - 10, yb + 10, "40 кГц", size=9, color=MUTED, anchor="end"))
    bx0 = t0 + tw + 12
    # 8 «сплесків» синусоїди-схематично
    for i in range(8):
        cx = bx0 + i * 12
        f.append(line(cx, yb, cx, yb - 16 if i % 2 == 0 else yb + 0, color=MUTED, sw=1.6))
    f.append(text(bx0 + 8 * 12 + 60, yb, "8 хвиль у повітря", size=10, color=MUTED, anchor="start"))
    f.append(line(bx0 - 3, yb + 24, bx0 + 8 * 12, yb + 24, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(bx0 + 48, yb + 38, "пачка вилітає одразу після TRIG", size=9, color=MUTED, italic=True))

    # --- Лінія ECHO ---
    be = base + 170
    ehi = 60
    e0 = bx0 + 8 * 12 + 20          # ECHO піднявся (після пачки)
    e1 = e0 + 250                    # ECHO впав (пропорційно відстані)
    f.append(text(left - 10, be - ehi / 2, "ECHO", size=12, bold=True, color=NEG, anchor="end"))
    f.append(text(left - 10, be - ehi / 2 + 16, "(вихід)", size=9, color=MUTED, anchor="end"))
    f.append(line(left, be, e0, be, color=NEG, sw=2.2))
    f.append(line(e0, be, e0, be - ehi, color=NEG, sw=2.2))
    f.append(line(e0, be - ehi, e1, be - ehi, color=NEG, sw=2.2))
    f.append(line(e1, be - ehi, e1, be, color=NEG, sw=2.2))
    f.append(line(e1, be, 830, be, color=NEG, sw=2.2))
    # ширина = t, стрілка під полицею
    f.append(line(e0, be - ehi - 14, e1, be - ehi - 14, color=INK, sw=1.2))
    f.append(text((e0 + e1) / 2, be - ehi - 20, "ширина = час t (це й міряєш)", size=10.5, color=INK, bold=True))
    f.append(text((e0 + e1) / 2, be + 26, "ближче — вужче,   далі — ширше", size=10, color=NEG, italic=True))

    # нижня рамка
    b, _, _ = textbox(W / 2, be + 66,
                      "нема відбиття за ~38 мс — ECHO сам падає: «нічого в межах 4 м». Наступний замір — не частіше ніж раз на 60 мс.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "timing.svg"), W, H, *f)


# ── 3. Розводка 4 пінів + подільник для 3.3-В плати ───────────────────────────
def fig_wiring():
    W, H = 940, 500
    f = [text(W / 2, 28, "Чотири піни: живлення, земля й дві лінії даних — ECHO через подільник на 3.3-В плату",
              size=13.5, bold=True)]

    # координати рядів-сигналів (спільні для модуля й МК)
    yV = 96      # VCC / 5V
    yT = 150     # TRIG
    yE = 236     # ECHO (нижче, бо між ним і землею вставляємо подільник)
    yG = 320     # GND
    mrx = 220    # правий край модуля (звідки виходять дроти)
    clx = 700    # лівий край МК (куди приходять)

    # Модуль ліворуч
    mx, my, mw, mh = 56, 74, 164, 286
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.9, rx=10))
    f.append(text(mx + mw / 2, my + 22, "HC-SR04", size=13, bold=True))
    f.append(circle(mx + 46, my + 54, 20, fill="#dfe6f0", stroke=INK, sw=1.4))
    f.append(circle(mx + 118, my + 54, 20, fill="#dfe6f0", stroke=INK, sw=1.4))
    mpins = [("VCC", POS, yV), ("TRIG", INK, yT), ("ECHO", NEG, yE), ("GND", NEG, yG)]
    for nm, col, yy in mpins:
        f.append(circle(mrx - 10, yy, 5.5, fill="#c9a227", stroke=MUTED, sw=1.0))
        f.append(text(mrx - 24, yy + 4, nm, size=11, bold=True, color=col, anchor="end"))

    # МК праворуч
    cx, cy, cw, ch = clx, 74, 184, 286
    f.append(rect(cx, cy, cw, ch, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(cx + cw / 2, cy + 22, "плата / МК", size=13, bold=True, color=FIELD))
    cpins = [("5V  /  3V3+", yV), ("GPIO → TRIG", yT), ("GPIO ← ECHO", yE), ("GND", yG)]
    for nm, yy in cpins:
        f.append(circle(cx + 14, yy, 5.5, fill="#c9a227", stroke=MUTED, sw=1.0))
        f.append(text(cx + 28, yy + 4, nm, size=10.5, color=INK, anchor="start"))

    # Прямі горизонтальні дроти (напис — НАД дротом, не на ньому)
    def hwire(yy, col, lab, lx=None):
        f.append(line(mrx, yy, clx, yy, color=col, sw=2.0))
        f.append(text(lx if lx is not None else (mrx + clx) / 2, yy - 9, lab, size=10, color=col, bold=True))

    hwire(yV, POS, "VCC → 5 В")
    hwire(yT, INK, "TRIG ← поштовх 10 мкс від МК")
    # GND-напис зсунуто ліворуч, щоб не перетнути хвіст подільника (x≈486)
    hwire(yG, NEG, "GND — спільна земля", lx=320)

    # ECHO: модуль → R1 → вузол → МК; від вузла вниз R2 → земля
    dx = 400                 # лівий край R1
    rw = 62
    f.append(line(mrx, yE, dx, yE, color=NEG, sw=2.0))
    f.append(rect(dx, yE - 11, rw, 22, fill=BG, stroke=INK, sw=1.4, rx=3))
    f.append(text(dx + rw / 2, yE - 18, "R1 1 кОм", size=9.5, color=INK, bold=True))
    node = dx + rw + 24
    f.append(line(dx + rw, yE, node, yE, color=NEG, sw=2.0))
    f.append(circle(node, yE, 3.6, fill=INK, stroke=INK, sw=1.0))
    # вузол → МК (горизонтально, напис над лінією)
    f.append(line(node, yE, clx, yE, color=NEG, sw=2.0))
    f.append(text((node + clx) / 2, yE - 9, "≈ 3.3 В у GPIO", size=9.5, color=NEG, bold=True))
    # вузол → вниз → R2 → земля
    f.append(line(node, yE, node, yE + 34, color=NEG, sw=2.0))
    f.append(rect(node - rw / 2, yE + 34, rw, 22, fill=BG, stroke=INK, sw=1.4, rx=3))
    f.append(text(node + rw / 2 + 8, yE + 49, "R2 2 кОм", size=9.5, color=INK, bold=True, anchor="start"))
    f.append(line(node, yE + 56, node, yE + 82, color=NEG, sw=2.0))
    f.append(minus(node, yE + 92, r=8))
    f.append(text(node, yE + 116, "подільник на ECHO", size=9.5, color=INK, bold=True))

    # нижні дві рамки-попередження (внизу, з запасом)
    b, _, _ = textbox(W / 2, 452,
                      "5-В плата (Arduino Uno): ECHO — прямо в пін, подільник не потрібен",
                      size=11, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(b)
    b2, _, _ = textbox(W / 2, 484,
                       "!  3.3-В плата (ESP32): ECHO дає 5 В — без подільника спалиш ніжку",
                       size=11, fill="#fdecea", stroke=POS, color=INK)
    f.append(b2)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_echo_principle()
    fig_timing()
    fig_wiring()
    print("OK: 3 figures ->", IMG)
