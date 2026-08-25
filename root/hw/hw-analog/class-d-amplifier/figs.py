# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def path_of(pts):
    return "M %.2f %.2f " % pts[0] + " ".join("L %.2f %.2f" % p for p in pts[1:])


def fig_pwm_generation():
    """Як народжується ШІМ: трикутна несівна + сигнал → компаратор → імпульси,
    ширина яких іде за сигналом."""
    W, H = 760, 430
    frags = []
    x0, x1 = 60, 700
    span = x1 - x0
    n = 600

    # ── верхня панель: трикутник + повільний сигнал ──
    top = 60
    midA = top + 80
    ampA = 64
    # повільний корисний сигнал (синус)
    sig = []
    for i in range(n + 1):
        t = i / n
        sig.append((x0 + span * t, midA - ampA * 0.7 * math.sin(2 * math.pi * 1.0 * t)))
    # трикутна несівна (швидка)
    fc = 11.0
    tri = []
    for i in range(n + 1):
        t = i / n
        ph = (t * fc) % 1.0
        tw = 2 * abs(ph - 0.5)          # 0..1 трикутник 0..1..0
        tri.append((x0 + span * t, midA + ampA - 2 * ampA * tw))

    frags.append(rect(x0 - 6, top, span + 12, 170, fill="#ffffff", stroke=MUTED, sw=1.0))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (path_of(tri), MUTED))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path_of(sig), NEG))
    frags.append(text(x0 + 4, top + 18, "несівна (трикутник)", size=12, color=MUTED, anchor="start"))
    frags.append(text(x1 - 4, top + 18, "сигнал", size=13, color=NEG, anchor="end", bold=True))

    # ── нижня панель: імпульси (де сигнал > трикутник) ──
    bt = top + 220
    bh = 96
    lo = bt + bh
    hi = bt + 10
    frags.append(rect(x0 - 6, bt - 6, span + 12, bh + 18, fill="#ffffff", stroke=MUTED, sw=1.0))
    # будуємо прямокутні імпульси
    prev = None
    pulse_pts = [(x0, lo)]
    for i in range(n + 1):
        t = i / n
        sx = x0 + span * t
        # значення сигналу й несівної в цій точці
        sv = -0.7 * math.sin(2 * math.pi * 1.0 * t)        # нормований сигнал (−..+)
        ph = (t * fc) % 1.0
        tv = (2 * abs(ph - 0.5)) * 2 - 1                     # трикутник −1..+1
        on = sv > tv
        y = hi if on else lo
        if prev is None:
            pulse_pts.append((sx, y))
        elif y != prev:
            pulse_pts.append((sx, prev))
            pulse_pts.append((sx, y))
        else:
            pulse_pts.append((sx, y))
        prev = y
    pulse_pts.append((x1, prev))
    pulse_pts.append((x1, lo))
    frags.append('<path d="%s" fill="#eaf0fd" stroke="%s" stroke-width="2.0"/>' % (path_of(pulse_pts), NEG))
    frags.append(text(x0 + 4, bt - 20, "вихід ключа: широкі імпульси там, де сигнал високий, вузькі — де низький",
                      size=12, color=INK, anchor="start"))
    frags.append(text(x0 + 4, lo + 28, "вузькі", size=11, color=MUTED, anchor="start"))
    frags.append(text(x1 - 4, lo + 28, "знов вузькі", size=11, color=MUTED, anchor="end"))
    frags.append(text((x0 + x1) / 2, hi - 18, "широкі (пік сигналу)", size=11, color=NEG, anchor="middle", bold=True))

    # стрілка «компаратор»
    frags.append(text((x0 + x1) / 2, top + 198, "↓ компаратор: сигнал вище несівної?  → ключ увімкнено",
                      size=12, color=INK, anchor="middle", bold=True))
    render(os.path.join(OUT, 'pwm-generation.svg'), W, H, *frags,
           title="ШІМ: ширина імпульсу йде за миттєвим рівнем сигналу")


def fig_chain():
    """Ланцюг класу D: ключі (півміст) → потік імпульсів → LC-фільтр → гладка хвиля."""
    W, H = 780, 360
    frags = []
    y_mid = 175

    # ── блок 1: півміст із двох ключів ──
    bx, by, bw, bh = 40, 95, 150, 150
    frags.append(rect(bx, by, bw, bh, fill=FILL, stroke=INK, sw=1.6))
    frags.append(text(bx + bw / 2, by - 12, "два ключі (півміст)", size=13, color=INK, bold=True))
    # верхній ключ до +V
    frags.append(text(bx + bw / 2, by + 26, "+V", size=13, color=POS, bold=True))
    frags.append(rect(bx + bw / 2 - 26, by + 36, 52, 26, fill="#fbe3df", stroke=POS, sw=1.4, rx=4))
    frags.append(text(bx + bw / 2, by + 54, "верх", size=12, color=POS, bold=True))
    frags.append(rect(bx + bw / 2 - 26, by + 84, 52, 26, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    frags.append(text(bx + bw / 2, by + 102, "низ", size=12, color=NEG, bold=True))
    frags.append(text(bx + bw / 2, by + bh - 6, "0 В", size=12, color=MUTED))
    # точка з'єднання → вихід
    frags.append(circle(bx + bw, by + 73, 3.5, fill=INK, stroke=INK))

    # ── потік прямокутних імпульсів ──
    px0 = bx + bw
    px1 = 360
    pw = px1 - px0
    lo, hi = y_mid + 36, y_mid - 36
    fc = 7.0
    pulse = [(px0, y_mid)]
    prev = None
    nn = 300
    for i in range(nn + 1):
        t = i / nn
        sx = px0 + pw * t
        sv = -0.6 * math.sin(2 * math.pi * 1.0 * t)
        ph = (t * fc) % 1.0
        tv = (2 * abs(ph - 0.5)) * 2 - 1
        y = hi if sv > tv else lo
        if prev is None:
            pulse.append((sx, y))
        elif y != prev:
            pulse.append((sx, prev)); pulse.append((sx, y))
        else:
            pulse.append((sx, y))
        prev = y
    pulse.append((px1, prev))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (path_of(pulse), INK))
    frags.append(text((px0 + px1) / 2, hi - 14, "тільки +V або 0 — край у край", size=11, color=MUTED, anchor="middle"))

    # ── блок 2: LC-фільтр ──
    fx, fy, fw, fh = 372, 110, 150, 130
    frags.append(rect(fx, fy, fw, fh, fill="#e3f4e9", stroke=FIELD, sw=1.6))
    frags.append(text(fx + fw / 2, fy - 12, "LC-фільтр (ФНЧ)", size=13, color=FIELD, bold=True))
    frags.append(text(fx + fw / 2, fy + 40, "L послідовно", size=12, color=INK))
    frags.append(text(fx + fw / 2, fy + 66, "C паралельно", size=12, color=INK))
    frags.append(text(fx + fw / 2, fy + 100, "зрізає клацання,", size=11, color=MUTED))
    frags.append(text(fx + fw / 2, fy + 116, "лишає звук", size=11, color=MUTED))

    # ── гладка хвиля на виході ──
    gx0 = fx + fw
    gx1 = 720
    gw = gx1 - gx0
    sm = [(gx0 + gw * (i / 200), y_mid - 30 * math.sin(2 * math.pi * 1.0 * (i / 200))) for i in range(201)]
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path_of(sm), FIELD))
    frags.append(text((gx0 + gx1) / 2, y_mid - 44, "відновлений сигнал", size=12, color=FIELD, anchor="middle", bold=True))
    # динамік-навантаження
    frags.append(text(gx1 + 4, y_mid + 4, "→ динамік", size=12, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, 'class-d-chain.svg'), W, H, *frags,
           title="Тракт класу D: клацання → LC-фільтр → гладкий звук")


def fig_switch_vs_linear():
    """Чому ключ майже не гріється: добуток U·I. Лінійний транзистор сидить
    посередині (U і I великі разом), ключ — або U≈0, або I≈0."""
    W, H = 760, 360
    frags = []

    def panel(cx, title, mode):
        col_w = 300
        top = 80
        x = cx - col_w / 2
        h = 200
        frags.append(rect(x, top, col_w, h, fill="#ffffff", stroke=MUTED, sw=1.0))
        frags.append(text(cx, top - 14, title, size=14, color=INK, bold=True))
        bx = x + 40
        baseY = top + h - 30
        bw = 46
        gap = 28
        # три стовпчики: U на приладі, I крізь нього, P=U·I
        if mode == "linear":
            U, I = 0.5, 0.5      # обидва середні
        elif mode == "on":
            U, I = 0.06, 0.9     # увімкнено: U≈0
        else:  # off
            U, I = 0.95, 0.04    # вимкнено: I≈0
        P = U * I
        maxh = 150
        items = [("U", U, NEG), ("I", I, FIELD), ("U·I", P, POS)]
        for j, (lab, val, col) in enumerate(items):
            xx = bx + j * (bw + gap)
            hh = max(2, maxh * val)
            frags.append(rect(xx, baseY - hh, bw, hh, fill=col, stroke=INK, sw=1.0, rx=3))
            frags.append(text(xx + bw / 2, baseY + 16, lab, size=13, color=INK, bold=True))
        # підпис висновку
        if mode == "linear":
            msg = "U і I великі РАЗОМ → велике тепло"
        elif mode == "on":
            msg = "U≈0 → тепла майже нема"
        else:
            msg = "I≈0 → тепла майже нема"
        frags.append(text(cx, top + h + 26, msg, size=12, color=INK, bold=True))

    panel(200, "Лінійний (клас A/B): посередині", "linear")
    panel(560, "Ключ увімкнено: U≈0", "on")
    # третя панель не вліземо — додамо рядок про вимкнений стан текстом
    frags.append(text(W / 2, H - 16,
                      "Ключ вимкнено — дзеркально: струму майже нема (I≈0), тож U·I знову ≈ 0. Тепло є лише в коротку мить перемикання.",
                      size=12, color=MUTED, anchor="middle"))
    render(os.path.join(OUT, 'switch-vs-linear.svg'), W, H, *frags,
           title="Чому ключ майже не гріється: добуток U·I")


def fig_history_timeline():
    """Часова смуга класу D: ідея 1932 → назва 1959 → перший серійний 1964 →
    масовість аж із MOSFET (1978→середина 1980-х). Наголос на півстолітній
    щілині між робочою ідеєю і масовим виробництвом."""
    W, H = 820, 320
    frags = []
    x0, x1 = 70, 760
    ymin, ymax = 1930, 1990
    axisY = 175

    def X(year):
        return x0 + (x1 - x0) * (year - ymin) / (ymax - ymin)

    # вісь часу
    frags.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2.2"/>'
                 % (x0, axisY, x1, axisY, INK))
    frags.append('<path d="M %.1f %d L %.1f %d L %.1f %d Z" fill="%s"/>'
                 % (x1, axisY - 6, x1 + 12, axisY, x1, axisY + 6, INK))
    # десятиліття-позначки
    for yr in range(1930, 1991, 10):
        xx = X(yr)
        frags.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.2"/>'
                     % (xx, axisY - 5, xx, axisY + 5, MUTED))
        frags.append(text(xx, axisY + 22, str(yr), size=12, color=MUTED, anchor="middle"))

    # події: (рік, підпис, рядки-деталь, угору?, колір)
    events = [
        (1932, "Бедфорд", ["патент US 1874159:", "ідея перемикання"], True, NEG),
        (1937, "Рівз", ["імпульсні методи", "(PCM, для зв'язку)"], False, MUTED),
        (1959, "Баксендолл", ["назва «клас D»", "(D = літера, не digital)"], True, POS),
        (1964, "Sinclair X-10", ["перший серійний", "лише ~2.5 Вт"], False, NEG),
        (1978, "Sony TA-N88", ["перші MOSFET-", "ключі в класі D"], True, FIELD),
    ]
    for yr, name, lines, up, col in events:
        xx = X(yr)
        frags.append(circle(xx, axisY, 5, fill=col, stroke=INK, sw=1.2))
        if up:
            ty = axisY - 30
            frags.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.0"/>'
                         % (xx, axisY - 6, xx, ty + 4, MUTED))
            frags.append(text(xx, ty - 22, name, size=13, color=col, anchor="middle", bold=True))
            for k, ln in enumerate(lines):
                frags.append(text(xx, ty - 6 + k * 14, ln, size=10.5, color=INK, anchor="middle"))
        else:
            ty = axisY + 44
            frags.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1.0"/>'
                         % (xx, axisY + 6, xx, ty - 4, MUTED))
            frags.append(text(xx, ty + 10, name, size=13, color=col, anchor="middle", bold=True))
            for k, ln in enumerate(lines):
                frags.append(text(xx, ty + 26 + k * 14, ln, size=10.5, color=INK, anchor="middle"))

    # дуга щілини «ідея → масовість»
    gx0, gx1 = X(1932), X(1985)
    frags.append('<path d="M %.1f %d Q %.1f %d %.1f %d" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="5 4"/>'
                 % (gx0, axisY - 96, (gx0 + gx1) / 2, axisY - 128, gx1, axisY - 96, FIELD))
    frags.append(text((gx0 + gx1) / 2, axisY - 134,
                      "~50 років між робочою ідеєю і масовим виробництвом", size=12, color=FIELD,
                      anchor="middle", bold=True))
    frags.append(text((gx0 + gx1) / 2, axisY - 118,
                      "(чекали на швидкі потужні MOSFET і дешеву логіку)", size=10.5, color=MUTED,
                      anchor="middle"))

    render(os.path.join(OUT, 'class-d-history.svg'), W, H, *frags,
           title="Часова смуга класу D: ідея 1932 → масовість аж із MOSFET")


if __name__ == '__main__':
    fig_pwm_generation()
    fig_chain()
    fig_switch_vs_linear()
    fig_history_timeline()
    print("OK figures written to", OUT)
