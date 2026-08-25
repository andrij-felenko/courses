# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «N20 мікромотор з редуктором».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def block(cx, cy, w, h, s, size=13, fill=FILL, stroke=LINE, sw=1.8):
    return fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size, fill=fill, stroke=stroke, sw=sw)


# ── 1. Анатомія: моторчик + редуктор + D-вал ─────────────────────────────────
def fig_anatomy():
    W, H = 1120, 470
    f = [text(W / 2, 32, "Що всередині: швидкий моторчик крутить редуктор, той — повільний D-вал",
              size=15, bold=True)]

    # моторний «стакан» ліворуч
    mcx, mcy = 235, 220
    mw, mh = 250, 150
    f.append(rect(mcx - mw / 2, mcy - mh / 2, mw, mh, fill="#eef3fb", stroke=INK, sw=2.2, rx=10))
    f.append(text(mcx, mcy - mh / 2 - 16, "мотор-«стакан» (~10 × 12 мм)", size=12, bold=True, color=NEG))
    # ротор-котушка як коло з витком
    f.append(circle(mcx, mcy, 40, fill=BG, stroke=INK, sw=1.8))
    f.append(circle(mcx, mcy, 13, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(mcx, mcy + 4, "якір", size=11, color=INK))
    # два магніти по боках усередині стакана
    f.append(text(mcx - mw / 2 + 24, mcy + 4, "N", size=13, bold=True, color=POS))
    f.append(text(mcx + mw / 2 - 24, mcy + 4, "S", size=13, bold=True, color=NEG))
    f.append(text(mcx, mcy + mh / 2 + 22, "20 000 об/хв, крутного моменту майже нема", size=11, color=MUTED))
    # дві живлячі ніжки-дротики ліворуч
    f.append(line(mcx - mw / 2, mcy - 26, mcx - mw / 2 - 46, mcy - 26, color=POS, sw=2))
    f.append(line(mcx - mw / 2, mcy + 26, mcx - mw / 2 - 46, mcy + 26, color=NEG, sw=2))
    f.append(text(mcx - mw / 2 - 52, mcy - 22, "+", size=15, bold=True, color=POS, anchor="end"))
    f.append(text(mcx - mw / 2 - 52, mcy + 31, "−", size=15, bold=True, color=NEG, anchor="end"))

    # редуктор праворуч — металева коробка з двома шестернями
    gcx, gcy = 620, 220
    gw, gh = 210, 150
    f.append(rect(gcx - gw / 2, gcy - gh / 2, gw, gh, fill="#f0f2f5", stroke=INK, sw=2.2, rx=8))
    f.append(text(gcx, gcy - gh / 2 - 16, "металевий редуктор", size=12, bold=True))
    # мала шестерня (від мотора) і велика (до валу) — прості кола з рисками зубців
    def gear(cx, cy, r, teeth, col=INK):
        out = [circle(cx, cy, r, fill=BG, stroke=col, sw=1.6)]
        import math
        for k in range(teeth):
            a = 2 * math.pi * k / teeth
            out.append(line(cx + (r) * math.cos(a), cy + (r) * math.sin(a),
                            cx + (r + 6) * math.cos(a), cy + (r + 6) * math.sin(a), color=col, sw=1.4))
        return "".join(out)
    f.append(gear(gcx - 40, gcy - 18, 22, 12))
    f.append(gear(gcx + 34, gcy + 16, 40, 20))
    f.append(text(gcx, gcy + gh / 2 + 22, "багато ступенів → сильно ділить оберти", size=11, color=MUTED))

    # вал зчеплення мотор→редуктор
    f.append(arrow(mcx + mw / 2, mcy, gcx - gw / 2, gcy))

    # D-вал праворуч
    sx = gcx + gw / 2
    f.append(rect(sx, gcy - 10, 150, 20, fill="#d8dde3", stroke=INK, sw=1.6, rx=3))
    # площинка «D» — темна риска зверху
    f.append(line(sx + 40, gcy - 10, sx + 120, gcy - 10, color=NEG, sw=3))
    f.append(text(sx + 150 + 8, gcy - 14, "вихідний вал", size=12, bold=True, anchor="start"))
    f.append(text(sx + 150 + 8, gcy + 6, "⌀3 мм, зі зрізом-«D»", size=11, color=MUTED, anchor="start"))
    f.append(text(sx + 150 + 8, gcy + 26, "50 об/хв, момент у сотні разів більший", size=11, color=FIELD, anchor="start"))

    # нижня формула-підсумок
    f.append(line(90, 400, W - 90, 400, color="#e5e7eb", sw=1))
    f.append(text(W / 2, 432, "редуктор ділить швидкість у N разів  →  множить момент приблизно у стільки ж разів",
                  size=14, bold=True))
    return W, H, f


# ── 2. Компроміс редуктора: оберти вниз, момент угору ─────────────────────────
def fig_tradeoff():
    W, H = 1040, 430
    f = [text(W / 2, 32, "Один моторчик, різні редуктори: обираєш точку на кривій «оберти ↔ момент»",
              size=15, bold=True)]

    # осі
    ox, oy = 130, 360      # початок координат
    axW, axH = 800, 250
    f.append(arrow(ox, oy, ox + axW, oy))                 # вісь X (оберти)
    f.append(arrow(ox, oy, ox, oy - axH))                 # вісь Y (момент)
    f.append(text(ox + axW, oy + 26, "оберти валу (об/хв)", size=12, bold=True, anchor="end"))
    f.append(text(ox - 16, oy - axH, "момент на валу", size=12, bold=True, anchor="end"))

    # спадна крива компромісу (гіпербола-подібна): момент × оберти ≈ const
    import math
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        x = ox + 40 + t * (axW - 70)
        # момент обернено до обертів
        rel = 1.0 / (0.18 + 1.9 * t)
        y = oy - 30 - rel * (axH - 60) * 0.5
        pts.append((x, y))
    path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, MUTED))

    # три робочі точки: сильний редуктор / середній / слабкий
    marks = [(0.10, "1:1000\n30 об/хв\nсильний момент", FIELD),
             (0.42, "1:298\n50 об/хв", INK),
             (0.86, "1:50\n300 об/хв\nслабкий момент", POS)]
    for t, lab, col in marks:
        x = ox + 40 + t * (axW - 70)
        rel = 1.0 / (0.18 + 1.9 * t)
        y = oy - 30 - rel * (axH - 60) * 0.5
        f.append(circle(x, y, 6, fill=col, stroke=col))
        # підпис ставимо праворуч-угору від точки, з запасом, без накладань
        f.append(mtext(x + 14, y - 14, lab, size=11, color=col, anchor="start"))

    f.append(text(W / 2, H - 12, "добуток «оберти × момент» задає сам моторчик; редуктор лише перерозподіляє його",
                  size=11.5, color=MUTED))
    return W, H, f


# ── 3. Підключення: N20 → драйвер → МК + батарея (пін-у-пін) ──────────────────
def fig_wiring():
    W, H = 1080, 500
    f = [text(W / 2, 30, "Підключення: мотор НІКОЛИ прямо в ногу МК — тільки через драйвер",
              size=15, bold=True)]

    # МК ліворуч
    mx, my, mw, mh = 90, 120, 220, 250
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=INK, sw=2.2, rx=14))
    f.append(text(mx + mw / 2, my + 28, "мікроконтролер", size=14, bold=True))
    f.append(text(mx + mw / 2, my + 48, "3.3 / 5 В логіка", size=10.5, color=MUTED))

    # драйвер H-міст посередині
    dx, dy, dw, dh = 430, 110, 230, 270
    f.append(rect(dx, dy, dw, dh, fill=BG, stroke=POS, sw=2.4, rx=12))
    f.append(text(dx + dw / 2, dy + 28, "драйвер (H-міст)", size=14, bold=True, color=POS))
    f.append(text(dx + dw / 2, dy + 48, "DRV8833 / L298N / TB6612", size=10, color=MUTED))

    # мотор праворуч
    ncx, ncy = 900, 175
    nw, nh = 150, 110
    f.append(rect(ncx - nw / 2, ncy - nh / 2, nw, nh, fill="#f0f2f5", stroke=INK, sw=2.2, rx=10))
    f.append(text(ncx, ncy - nh / 2 - 14, "N20-мотор", size=13, bold=True))
    f.append(text(ncx, ncy + 4, "M", size=22, bold=True, color=INK))
    f.append(circle(ncx, ncy, 26, fill=BG, stroke=INK, sw=1.6))

    # батарея праворуч-знизу
    bx, by, bw, bh = 820, 360, 170, 90
    f.append(rect(bx, by, bw, bh, fill="#fff7e6", stroke=POS, sw=2, rx=8))
    f.append(text(bx + bw / 2, by + 26, "батарея 6 В", size=12, bold=True, color=POS))
    f.append(text(bx + bw / 2, by + 48, "живлення МОТОРА", size=10.5, color=MUTED))
    f.append(text(bx + bw / 2, by + 68, "(окреме від логіки)", size=10, color=MUTED))

    # --- лінії керування МК → драйвер (три сигнали), рівно горизонтальні ---
    # підпис — НАД лінією з добрим відступом (жоден напис не лягає на дріт)
    def wire(y, lab, col=INK):
        f.append(circle(mx + mw, y, 4, fill=col, stroke=col))
        f.append(line(mx + mw, y, dx, y, color=col, sw=1.8))
        f.append(circle(dx, y, 4, fill=col, stroke=col))
        f.append(text((mx + mw + dx) / 2, y - 12, lab, size=10.5, color=col))

    wire(my + 78, "IN1 (напрям)", INK)
    wire(my + 128, "IN2 (напрям)", INK)
    wire(my + 178, "PWM (швидкість)", FIELD)
    # спільна земля логіки
    yg = my + 224
    f.append(circle(mx + mw, yg, 4, fill=NEG, stroke=NEG))
    f.append(line(mx + mw, yg, dx, yg, color=NEG, sw=1.8))
    f.append(circle(dx, yg, 4, fill=NEG, stroke=NEG))
    f.append(text((mx + mw + dx) / 2, yg - 12, "GND (спільна!)", size=10.5, color=NEG))

    # --- драйвер → мотор (два виходи OUT1/OUT2), підписи біля драйвера над лінією ---
    o1y, o2y = dy + 90, dy + 150
    f.append(circle(dx + dw, o1y, 4, fill=INK, stroke=INK))
    f.append(line(dx + dw, o1y, ncx - nw / 2, ncy - 16, color=INK, sw=2))
    f.append(text(dx + dw + 10, o1y - 16, "OUT1", size=11, bold=True, anchor="start"))
    f.append(circle(dx + dw, o2y, 4, fill=INK, stroke=INK))
    f.append(line(dx + dw, o2y, ncx - nw / 2, ncy + 16, color=INK, sw=2))
    f.append(text(dx + dw + 10, o2y + 22, "OUT2", size=11, bold=True, anchor="start"))
    f.append(text(ncx, ncy + nh / 2 + 22, "полярність OUT1/OUT2 задає напрям", size=10.5, color=MUTED))

    # --- батарея → живлення драйвера (VM) і спільна земля, чистим низом ---
    busV = 470                 # силова шина + (нижче всього)
    busG = 448                 # шина землі батареї
    vmx = dx + dw - 40         # вертикаль VM з дна драйвера
    f.append(circle(vmx, dy + dh, 4, fill=POS, stroke=POS))
    f.append(line(vmx, dy + dh, vmx, busV, color=POS, sw=2))          # вниз від драйвера
    f.append(line(vmx, busV, bx + 30, busV, color=POS, sw=2))          # вправо до батареї
    f.append(line(bx + 30, busV, bx + 30, by + bh, color=POS, sw=2))   # угору в «+» батареї
    f.append(circle(bx + 30, by + bh, 4, fill=POS, stroke=POS))
    f.append(text((vmx + bx + 30) / 2, busV + 16, "VM (силове + мотора)", size=10.5, color=POS))
    # земля батареї у вузол землі драйвера (лівіше за VM)
    gnx = dx + dw - 80         # вертикаль землі до драйвера
    f.append(circle(gnx, dy + dh, 4, fill=NEG, stroke=NEG))
    f.append(line(gnx, dy + dh, gnx, busG, color=NEG, sw=1.8))
    f.append(line(gnx, busG, bx + 130, busG, color=NEG, sw=1.8))
    f.append(line(bx + 130, busG, bx + 130, by + bh, color=NEG, sw=1.8))
    f.append(circle(bx + 130, by + bh, 4, fill=NEG, stroke=NEG))
    f.append(text((gnx + bx + 130) / 2, busG - 8, "GND батареї → GND драйвера", size=10.5, color=NEG))

    return W, H, f


# мапа цифр у Unicode-надрядкові (для «0.90²» без залежностей)
_SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
def sup(n):
    return "".join(_SUP[c] for c in str(n))


# ── 4. ККД множиться по ступенях: чому багатоступеневий редуктор «з'їдає» момент ──
def fig_efficiency():
    W, H = 1080, 500
    f = [text(W / 2, 32, "ККД множиться, а не додається: кожен ступінь бере свою частку моменту",
              size=15, bold=True)]

    # осі: X — номер ступеня, Y — частка ідеального моменту, що дійшла
    ox, oy = 150, 390
    axW, axH = 820, 290
    f.append(arrow(ox, oy, ox + axW, oy))
    f.append(arrow(ox, oy, ox, oy - axH))
    f.append(text(ox + axW, oy + 28, "після скількох ступенів (пар шестерень)", size=12, bold=True, anchor="end"))
    f.append(mtext(ox - 96, oy - axH + 10, "частка\nідеального\nмоменту", size=11, color=INK, anchor="middle"))

    # горизонталь «100 %»
    y100 = oy - axH * 0.92
    f.append(line(ox, y100, ox + axW, y100, color="#d1d5db", sw=1, dash="4,4"))
    f.append(text(ox + axW, y100 - 8, "100 % — ідеал (ККД = 1, без тертя)", size=10.5, color=MUTED, anchor="end"))

    # стовпчики: після k ступенів лишилось 0.90^k (реалістичні ~90% на ступінь
    # для дешевого дрібного редуктора — сковзання зубців, тертя в осях, мастило)
    eta = 0.90
    n_stages = 4
    bw = 104
    gap = (axW - 60 - n_stages * bw) / (n_stages + 1)
    for k in range(1, n_stages + 1):
        frac = eta ** k
        x = ox + 50 + gap * k + bw * (k - 1)
        h = axH * 0.92 * frac
        y = oy - h
        col = FIELD if k == 1 else (INK if k <= 2 else POS)
        f.append(rect(x, y, bw, h, fill="#eef3fb" if k <= 2 else "#fdecea",
                      stroke=col, sw=2, rx=4))
        f.append(text(x + bw / 2, y - 10, "%d %%" % round(frac * 100), size=13, bold=True, color=col))
        f.append(text(x + bw / 2, oy + 22, "%d ступ." % k, size=11.5, bold=True))
        f.append(text(x + bw / 2, oy + 40, "0.90%s" % ("" if k == 1 else sup(k)),
                      size=10.5, color=MUTED))

    # підсумковий рядок унизу
    f.append(line(ox, oy + 60, ox + axW, oy + 60, color="#e5e7eb", sw=1))
    f.append(text(W / 2, oy + 84,
                  "3 ступені по 90 %  →  0.90³ ≈ 0.73:  до виходу доходить лише ~73 % ідеального моменту",
                  size=13, bold=True))
    f.append(text(W / 2, oy + 104,
                  "дорожчий, точніший редуктор тримає більший ККД на ступінь — тому й дорожчий",
                  size=10.5, color=MUTED))
    return W, H, f


# ── 5. Пряма «момент ↔ оберти» двигуна і як редуктор її розтягує ──────────────
def fig_torque_speed():
    W, H = 1120, 510
    f = [text(W / 2, 30, "Двигун — це пряма між двома точками; редуктор її перемасштабовує",
              size=15, bold=True)]

    ox, oy = 160, 390
    axW, axH = 840, 280
    f.append(arrow(ox, oy, ox + axW, oy))
    f.append(arrow(ox, oy, ox, oy - axH))
    f.append(text(ox + axW, oy + 26, "оберти", size=12, bold=True, anchor="end"))
    f.append(text(ox + 8, oy - axH - 8, "момент", size=12, bold=True, anchor="start"))

    # координати кінців прямої
    x0, y0 = ox, oy - axH * 0.88       # τ_stall при 0 об/хв (верхній лівий)
    x1, y1 = ox + axW * 0.88, oy       # ω₀ при 0 моменту (нижній правий)

    # сама спадна пряма
    f.append(line(x0, y0, x1, y1, color=INK, sw=2.6))

    # точка застопорення — блок напису у ПОРОЖНЬОМУ куті вгорі-праворуч (де пряма
    # вже низько), звʼязаний із точкою тонким виноском; так пряма не ріже напис
    f.append(circle(x0, y0, 6, fill=POS, stroke=POS))
    lx, ly = x0 + 150, y0 - 58
    f.append(line(x0 + 6, y0 - 4, lx - 4, ly + 34, color=POS, sw=1, dash="3,3"))  # короткий виносок
    f.append(mtext(lx, ly, "застопорення:\nоберти = 0\nмомент максимальний (τ_stall)",
                   size=11, color=POS, anchor="start"))

    # точка холостого ходу — блок напису ВГОРІ-ПРАВОРУЧ від точки, поза прямою
    f.append(circle(x1, y1, 6, fill=NEG, stroke=NEG))
    f.append(mtext(x1 + 14, y1 - 64, "холостий хід:\nмомент = 0\nоберти макс. (ω₀)",
                   size=11, color=NEG, anchor="start"))

    # точка максимальної потужності — середина прямої
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    f.append(circle(xm, ym, 6, fill=FIELD, stroke=FIELD))
    # пунктири до осей
    f.append(line(xm, ym, xm, oy, color=FIELD, sw=1, dash="4,4"))
    f.append(line(xm, ym, ox, ym, color=FIELD, sw=1, dash="4,4"))
    # блок напису — у ВЕЛИКОМУ порожньому трикутнику НИЖЧЕ-ЛІВОРУЧ під прямою,
    # звʼязаний із точкою тонким виноском; так спадна пряма проходить ВИЩЕ напису
    mlx, mly = ox + 70, oy - 92
    f.append(line(xm - 4, ym + 6, mlx + 60, mly - 4, color=FIELD, sw=1, dash="3,3"))  # виносок до точки
    f.append(mtext(mlx, mly, "макс. потужність тут:\n½·ω₀ × ½·τ_stall\n(електричний ККД мотора ~50 %)",
                   size=11, color=FIELD, anchor="start"))

    # робоча (номінальна) точка — ближче до холостого, невеликий момент;
    # підпис ПІД точкою (по центру), окремо від блоку макс. потужності
    xr = x0 + (x1 - x0) * 0.76
    yr = y0 + (y1 - y0) * 0.76
    f.append(circle(xr, yr, 5, fill=INK, stroke=INK))
    f.append(mtext(xr, yr + 24, "номінальна\nробоча точка", size=10.5, color=INK, anchor="middle"))

    f.append(text(W / 2, H - 14,
                  "редуктор 1:N ділить вісь обертів на N, а вісь моменту множить на N·ККД — форма прямої лишається",
                  size=11, color=MUTED))
    return W, H, f


# ── 6. Керування: два світи (логіка / сила), зшиті спільною землею ────────────
def fig_signals():
    W, H = 1100, 470
    f = [text(W / 2, 30, "Керуємо не мотором, а драйвером: логіка (слабка) і сила (потужна) — окремі, зшиті землею",
              size=15, bold=True)]

    # рамка «світ логіки» ліворуч
    lx, ly, lw, lh = 60, 70, 470, 320
    f.append(rect(lx, ly, lw, lh, fill="#f2f8f2", stroke=FIELD, sw=1.6, rx=14))
    f.append(text(lx + 16, ly + 26, "світ логіки — міліампери, 3.3 / 5 В", size=12.5, bold=True, color=FIELD, anchor="start"))

    # рамка «світ сили» праворуч
    rx, ry, rw, rh = 600, 70, 440, 320
    f.append(rect(rx, ry, rw, rh, fill="#fff7f4", stroke=POS, sw=1.6, rx=14))
    f.append(text(rx + rw - 16, ry + 26, "світ сили — ампери, батарея мотора", size=12.5, bold=True, color=POS, anchor="end"))

    # МК у світі логіки
    mx, my, mw, mh = 100, 150, 170, 180
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=INK, sw=2.2, rx=12))
    f.append(text(mx + mw / 2, my + 26, "мікроконтролер", size=13, bold=True))
    f.append(text(mx + mw / 2, my + 46, "лише командує", size=10.5, color=MUTED))

    # драйвер — на межі двох світів (стоїть у силовій рамці, входи дивляться в логіку)
    dx, dy, dw, dh = 620, 120, 200, 240
    f.append(rect(dx, dy, dw, dh, fill=BG, stroke=POS, sw=2.4, rx=12))
    f.append(text(dx + dw / 2, dy + 26, "драйвер H-міст", size=13, bold=True, color=POS))
    f.append(text(dx + dw / 2, dy + 44, "DRV8833", size=10, color=MUTED))
    f.append(text(dx + dw / 2, dy + 62, "тягне — він", size=10, color=MUTED))

    # мотор — глибоко у світі сили
    ncx, ncy = 960, 200
    f.append(circle(ncx, ncy, 30, fill=BG, stroke=INK, sw=2))
    f.append(text(ncx, ncy + 7, "M", size=22, bold=True))
    f.append(text(ncx, ncy - 44, "N20", size=12, bold=True))

    # батарея мотора внизу праворуч
    bx, by, bw, bh = 610, 320, 150, 54
    f.append(rect(bx, by, bw, bh, fill="#fff0e6", stroke=POS, sw=2, rx=8))
    f.append(text(bx + bw / 2, by + 22, "батарея 6 В", size=11.5, bold=True, color=POS))
    f.append(text(bx + bw / 2, by + 40, "живлення мотора", size=10, color=MUTED))

    # три сигнали МК → драйвер; підпис НАД лінією з великим відступом
    def sig(y, lab, col):
        f.append(circle(mx + mw, y, 4, fill=col, stroke=col))
        f.append(line(mx + mw, y, dx, y, color=col, sw=1.9))
        f.append(circle(dx, y, 4, fill=col, stroke=col))
        f.append(text((mx + mw + dx) / 2, y - 11, lab, size=11, color=col))

    sig(my + 40, "IN1 — тримає напрям", INK)
    sig(my + 92, "IN2 — тут ШІМ-швидкість", FIELD)

    # спільна земля — жирна лінія через увесь низ, підпис під нею
    yg = my + 150
    f.append(circle(mx + mw, yg, 4, fill=NEG, stroke=NEG))
    f.append(line(mx + mw, yg, dx, yg, color=NEG, sw=2.6))
    f.append(circle(dx, yg, 4, fill=NEG, stroke=NEG))
    f.append(text((mx + mw + dx) / 2, yg + 20, "GND — СПІЛЬНА земля (без неї сигнали «не мають опори»)",
                  size=11, bold=True, color=NEG))

    # драйвер → мотор: два силові виходи (товсті), підписи над лініями
    o1y, o2y = dy + 80, dy + 140
    f.append(circle(dx + dw, o1y, 4, fill=POS, stroke=POS))
    f.append(line(dx + dw, o1y, ncx - 26, ncy - 14, color=POS, sw=3))
    f.append(text(dx + dw + 12, o1y - 14, "OUT1", size=11, bold=True, color=POS, anchor="start"))
    f.append(circle(dx + dw, o2y, 4, fill=POS, stroke=POS))
    f.append(line(dx + dw, o2y, ncx - 26, ncy + 14, color=POS, sw=3))
    f.append(text(dx + dw + 12, o2y + 20, "OUT2", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(ncx, ncy + 52, "полярність задає напрям", size=10, color=MUTED))

    # батарея → VM драйвера (товста силова, унизу)
    vmx = dx + dw / 2 + 40
    f.append(circle(vmx, dy + dh, 4, fill=POS, stroke=POS))
    f.append(line(vmx, dy + dh, vmx, by, color=POS, sw=3))
    f.append(text(vmx + 8, (dy + dh + by) / 2, "VM", size=11, bold=True, color=POS, anchor="start"))

    # нижній підсумок
    f.append(text(W / 2, H - 12,
                  "з логіки виходять три слабкі сигнали; сильний струм мотора живе окремо й іде лише через драйвер",
                  size=11, color=MUTED))
    return W, H, f


# ── 7. Народний міф «20 = діаметр 20 мм» проти реальних розмірів корпусів ──────
def fig_name_myth():
    """Три моторні «стакани» в один масштаб із їхнім СПРАВЖНІМ поперечником.
    Народна версія каже «N20 = 20 мм банка» — та банка ~20 мм має «130», а не «N20».
    Масштаб: 1 мм = SC пікселів; кола по РЕАЛЬНОМУ радіусу, підписи з запасом."""
    W, H = 1060, 470
    SC = 5.4  # пікселів на міліметр (щоб φ20 мм читалося помітно більшим за φ12)
    f = [text(W / 2, 30, "«20» — це не діаметр банки: три корпуси в один масштаб",
              size=15, bold=True)]

    baseY = 250  # спільна лінія «землі» під усіма банками
    f.append(line(70, baseY, W - 70, baseY, color="#e5e7eb", sw=1))

    # (позначка, справжній Ø корпусу в мм, колір, підпис-факт)
    cans = [
        ("N20",      12.0, FIELD, "банка ~10–12 мм\n(тіло моторчика)"),
        ("«130»\n(FA-130)", 20.1, POS, "банка φ20.1 мм\n— ось ХТО ~20 мм"),
        ("«260»\n(RE-260)", 24.0, NEG, "банка ~24 мм\n(більша за «N20»)"),
    ]
    xs = [230, 540, 850]
    for (lab, dmm, col, note), cx in zip(cans, xs):
        r = dmm * SC / 2.0
        # банку малюємо як коло (вид з торця), сидить на спільній лінії
        cy = baseY - r
        f.append(circle(cx, cy, r, fill="#f4f6f8", stroke=col, sw=2.4))
        # позначка — усередині банки
        f.append(mtext(cx, cy - (0 if "\n" in lab else 6), lab, size=13, color=col, bold=True))
        # мірна лінія діаметра під банкою з підписом Ø
        my = baseY + 26
        f.append(line(cx - r, my, cx + r, my, color=col, sw=1.6))
        f.append(line(cx - r, my - 5, cx - r, my + 5, color=col, sw=1.6))
        f.append(line(cx + r, my - 5, cx + r, my + 5, color=col, sw=1.6))
        f.append(text(cx, my + 18, "Ø %.0f мм" % round(dmm), size=12, bold=True, color=col))
        # факт-підпис ще нижче, з запасом
        f.append(mtext(cx, my + 42, note, size=10.5, color=MUTED))

    # висновок унизу — де саме ламається народна версія
    f.append(text(W / 2, H - 40,
                  "Народна версія: «N20 = банка 20 мм». Але банка «N20» удвічі менша,",
                  size=12.5, bold=True))
    f.append(text(W / 2, H - 20,
                  "а рівно ~20 мм має зовсім інший мотор — «130». Отже «20» — не міліметри корпусу.",
                  size=12.5, bold=True, color=POS))
    return W, H, f


for name, fn in [("anatomy", fig_anatomy),
                 ("tradeoff", fig_tradeoff),
                 ("wiring", fig_wiring),
                 ("efficiency", fig_efficiency),
                 ("torque_speed", fig_torque_speed),
                 ("signals", fig_signals),
                 ("name_myth", fig_name_myth)]:
    W, H, frags = fn()
    render(os.path.join(IMG, name + ".svg"), W, H, *frags)
    print("wrote", name + ".svg")
