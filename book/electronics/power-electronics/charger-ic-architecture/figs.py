# -*- coding: utf-8 -*-
"""Фігури до теми «Архітектура зарядного чипа (клас BQ24xxx/MP2625)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Блок-схема: шлях енергії + керування ──────────────────────────────────
def fig_block():
    W, H = 880, 500
    f = [text(W / 2, 28, "Зарядний чип: силовий шлях згори, керування знизу",
              size=16, bold=True)]
    yc = 158  # центр силового ланцюга

    def box(x, w, h, s, **kw):
        y = yc - h / 2
        return fitbox(x, y, w, h, s, size=13, **kw)

    # силові блоки (зліва направо)
    f.append(box(24, 86, 52, "VBUS\nвхід", fill="#eef3fb", stroke=NEG))
    f.append(box(128, 104, 58, "Q1 · RBFET\nвхідний ключ"))
    f.append(box(252, 158, 88, "Синхронний buck\nQ2 (HS) / Q3 (LS)\n≈1.5 МГц",
                 fill="#eef7f0", stroke=FIELD, bold=True))
    f.append(box(430, 74, 50, "котушка L\n(зовні)", fill="#ffffff", stroke=MUTED))
    f.append(box(524, 64, 50, "SYS", fill="#eef7f0", stroke=FIELD, bold=True))
    f.append(box(608, 118, 58, "Q4 · BATFET"))
    f.append(box(744, 78, 52, "BAT\n(комірка)", fill="#fdecea", stroke=POS))

    # з'єднання силового ланцюга
    for x1, x2 in [(110, 128), (232, 252), (410, 430), (504, 524), (588, 608), (726, 744)]:
        f.append(arrow(x1, yc, x2, yc))

    # система над SYS
    f.append(fitbox(481, 48, 150, 46, "Система\n(навантаження)", size=12,
                    fill="#f4f6f8", stroke=LINE))
    f.append(arrow(556, 133, 556, 96))

    # блок керування знизу
    f.append(fitbox(180, 372, 372, 72,
                    "Керування: підсилювачі похибки → вибір мінімуму → ШІМ",
                    size=13, fill="#fff8e8", stroke="#b8860b", bold=True))
    # керування ключами buck (два затвори)
    f.append(arrow(316, 372, 316, 202, color="#b8860b"))
    f.append(arrow(360, 372, 360, 202, color="#b8860b"))
    f.append(text(300, 300, "керує ключами", size=11, color=MUTED, anchor="end"))

    # цифрові входи справа
    f.append(fitbox(600, 366, 120, 42, "I2C · SCL/SDA", size=12,
                    fill="#eef3fb", stroke=NEG))
    f.append(arrow(600, 387, 554, 387, color=NEG))
    f.append(fitbox(600, 418, 120, 42, "TS · термістор", size=12,
                    fill="#f4f6f8", stroke=LINE))
    f.append(arrow(600, 439, 554, 439))

    b, _, _ = textbox(W / 2, 478,
                      "Зовні лишаються тільки котушка й конденсатори; чотири силові MOSFET і весь розум — на кристалі.",
                      size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "block.svg"), W, H, *f)


# ── 2. Вибір мінімуму: багато контурів — один каскад ─────────────────────────
def fig_loops():
    W, H = 900, 470
    f = [text(W / 2, 26, "Вибір мінімуму: найтісніша межа забирає кермо",
              size=16, bold=True)]

    amps = [
        (87,  "VREG · напруга 4.2 В", LINE, FILL),
        (147, "ICHG · струм заряду",  FIELD, "#eef7f0"),   # активний
        (207, "IINDPM · вхідний струм", LINE, FILL),
        (267, "VINDPM · вхідна напруга", LINE, FILL),
        (327, "TREG · температура",   LINE, FILL),
    ]
    busx = 372
    for cy, label, stroke, fill in amps:
        f.append(fitbox(40, cy - 23, 228, 46, label, size=12, stroke=stroke, fill=fill,
                        bold=(stroke == FIELD)))
        col = FIELD if stroke == FIELD else MUTED
        sw = 2.4 if stroke == FIELD else 1.4
        f.append(line(268, cy, busx, cy, color=col, sw=sw))
    # мітка активного контуру
    f.append(text(292, 138, "зараз керує", size=10.5, color=FIELD, anchor="middle"))

    # спільна шина «тільки донизу»
    f.append(line(busx, 80, busx, 334, color=MUTED, sw=2))
    f.append(text(busx + 6, 66, "виходи лише тягнуть вузол донизу",
                  size=11, color=MUTED, anchor="middle"))

    # вузол вибору мінімуму
    f.append(arrow(busx, 200, 430, 200, color=INK))
    f.append(fitbox(430, 170, 170, 60, "вибір мінімуму\n(найнижчий керує)",
                    size=13, fill="#fff8e8", stroke="#b8860b", bold=True))
    # ШІМ і каскад
    f.append(arrow(600, 200, 650, 200))
    f.append(fitbox(650, 176, 118, 48, "ШІМ ·\nскважність", size=12,
                    fill="#eef3fb", stroke=NEG))
    f.append(arrow(709, 224, 709, 286))
    f.append(fitbox(636, 286, 150, 52, "силовий каскад (buck)", size=12,
                    fill="#eef7f0", stroke=FIELD, bold=True))

    # зворотний зв'язок вимірювання (пунктир, вторинне)
    f.append(line(711, 338, 711, 400, color=MUTED, sw=1.3, dash="5,4"))
    f.append(line(711, 400, 20, 400, color=MUTED, sw=1.3, dash="5,4"))
    f.append(line(20, 400, 20, 200, color=MUTED, sw=1.3, dash="5,4"))
    f.append(arrow(20, 200, 40, 200, color=MUTED, sw=1.3))
    f.append(text(W / 2, 420, "виміряні з каскаду величини повертаються в контури",
                  size=11, color=MUTED, anchor="middle"))

    b, _, _ = textbox(W / 2, 450,
                      "Кожен контур може лише зменшувати струм; хто вимагає найменшого — той і керує, решта чекають.",
                      size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "loops.svg"), W, H, *f)


# ── 3. Профіль заряду, поділений на смуги за активним контуром ────────────────
def fig_profile():
    W, H = 860, 470
    f = [text(W / 2, 26, "Профіль заряду очима контурів",
              size=16, bold=True)]
    ox, oy, top = 80, 360, 96
    span = 680
    end = ox + span
    x_pc = ox + 0.10 * span
    x_cc = ox + 0.52 * span
    x_tm = ox + 0.90 * span

    # кольорові смуги активного контуру
    def band(x0, x1, fill):
        return rect(x0, top, x1 - x0, oy - top, fill=fill, stroke=fill, sw=0, rx=0)
    f.append(band(ox, x_pc, "#f0f0f0"))
    f.append(band(x_pc, x_cc, "#e9f0fc"))
    f.append(band(x_cc, x_tm, "#fdeceb"))
    f.append(band(x_tm, end, "#f0f0f0"))
    # підписи смуг
    f.append(text((ox + x_pc) / 2, top + 16, "перед-", size=10.5, color=MUTED))
    f.append(text((ox + x_pc) / 2, top + 30, "заряд", size=10.5, color=MUTED))
    f.append(text((x_pc + x_cc) / 2, top + 18, "CC — керує ICHG", size=12.5, color=NEG, bold=True))
    f.append(text((x_cc + x_tm) / 2, top + 18, "CV — керує VREG", size=12.5, color=POS, bold=True))
    f.append(text((x_tm + end) / 2, top + 18, "стоп", size=10.5, color=MUTED))

    # осі
    f.append(line(ox, oy, end, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(end, oy + 22, "час →", size=11, color=MUTED, anchor="end"))

    # рівні
    def vy(v):  # 3.0 В → 296, 4.2 В → 120
        return 296 - (v - 3.0) / 1.2 * (296 - 120)
    def iy(fr):  # частка повного струму → y
        return 356 - fr * (356 - 150)
    y42 = vy(4.2)
    f.append(line(ox, y42, end, y42, color=NEG, sw=1.0, dash="2,4"))
    f.append(text(ox - 8, y42 + 4, "4.2 В", size=10.5, color=NEG, anchor="end"))
    f.append(text(ox - 8, vy(3.0) + 4, "3.0 В", size=10.5, color=MUTED, anchor="end"))
    ytm = iy(0.1)
    f.append(text(end + 4, ytm + 4, "C/10", size=10, color=POS, anchor="start"))

    # криві
    vpts, ipts = [], []
    N = 150
    for k in range(N + 1):
        x = ox + span * k / N
        # напруга
        if x <= x_pc:
            t = (x - ox) / (x_pc - ox)
            v = 3.0 + 0.30 * t
        elif x <= x_cc:
            t = (x - x_pc) / (x_cc - x_pc)
            v = 3.30 + 0.90 * (1 - math.exp(-2.5 * t)) / (1 - math.exp(-2.5))
        else:
            v = 4.2
        vpts.append((x, vy(v)))
        # струм
        if x <= x_pc:
            fr = 0.12
        elif x <= x_cc:
            fr = 1.0
        elif x <= x_tm:
            t = (x - x_cc) / (x_tm - x_cc)
            fr = 0.1 + 0.9 * math.exp(-3.0 * t)
        else:
            fr = 0.0
        ipts.append((x, iy(fr)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in vpts), NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="7,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in ipts), POS))

    # легенда
    lx, ly = ox + 30, top + 44
    f.append(line(lx, ly, lx + 28, ly, color=NEG, sw=2.8))
    f.append(text(lx + 34, ly + 4, "напруга", size=11.5, color=INK, anchor="start"))
    f.append(line(lx, ly + 20, lx + 28, ly + 20, color=POS, sw=2.8, dash="7,4"))
    f.append(text(lx + 34, ly + 24, "струм", size=11.5, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 448,
                      "При слабкому вході на початку CC струм нижчий за заданий — там кермо перехоплює вхідний контур (IINDPM/VINDPM).",
                      size=11, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "profile.svg"), W, H, *f)


# ── 4. Баланс потужності: та сама енергія в комірку, менше тепла ──────────────
def fig_powerbal():
    W, H = 900, 470
    f = [text(W / 2, 30, "Та сама потужність у комірку — менше тепла й менший струм із входу",
              size=15, bold=True)]
    x0 = 250            # старт стовпчика потужності
    ppw = 40.0         # пікселів на ват
    barh = 48

    def ledger(y, label, deliv, loss, note, bold_label=False):
        out = [text(30, y + barh / 2 + 5, label, size=13, anchor="start", bold=bold_label)]
        gw = deliv * ppw
        rw = loss * ppw
        out.append(rect(x0, y, gw, barh, fill="#eef7f0", stroke=FIELD, sw=1.5))
        out.append(text(x0 + gw / 2, y + barh / 2 + 5,
                        "у комірку %.1f Вт" % deliv, size=12, color=INK))
        out.append(rect(x0 + gw, y, rw, barh, fill="#fdecea", stroke=POS, sw=1.5))
        rlabel = "втрати %.1f Вт" % loss
        if rw >= text_width(rlabel, 11.5) + 8:
            out.append(text(x0 + gw + rw / 2, y + barh / 2 + 5, rlabel, size=11.5, color=POS))
        else:
            out.append(text(x0 + gw + rw + 8, y + barh / 2 + 5, rlabel,
                            size=11.5, color=POS, anchor="start"))
        # струмова примітка праворуч
        nx = x0 + gw + max(rw, 60) + (104 if rw < 60 else 16)
        out.append(text(nx, y + barh / 2 + 5, note, size=11.5, color=NEG, anchor="start"))
        return out

    # рядок «лінійний»
    yL = 150
    f += ledger(yL, "Лінійний", 7.2, 2.8, "Iвх 2.0 А → Iзар 2.0 А")
    # рядок «buck»
    yB = 268
    f += ledger(yB, "Buck · η 90%", 7.2, 0.8, "Iвх 1.6 А → Iзар 2.0 А", bold_label=True)

    # вертикальний орієнтир по спільному краю зеленого (7.2 Вт)
    xg = x0 + 7.2 * ppw
    f.append(line(xg, 128, xg, 340, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(xg, 120, "однакова корисна енергія в комірку",
                  size=11, color=MUTED, anchor="middle"))

    # проста шкала потужності
    f.append(line(x0, 356, x0 + 11 * ppw, 356, color=MUTED, sw=1.0))
    for wv in (0, 5, 10):
        xx = x0 + wv * ppw
        f.append(line(xx, 356, xx, 361, color=MUTED, sw=1.0))
        f.append(text(xx, 375, "%d" % wv, size=10.5, color=MUTED))
    f.append(text(x0 + 11 * ppw, 375, "Вт →", size=10.5, color=MUTED, anchor="end"))

    b, _, _ = textbox(W / 2, 430,
                      "У комірку зайшло порівну (зелене), але buck лишив собі втричі менше тепла (червоне) і взяв менший струм із входу.",
                      size=11.5, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "powerbal.svg"), W, H, *f)


# ── 5. Три стелі струму заряду: діє найнижча ─────────────────────────────────
def fig_ceilings():
    W, H = 900, 440
    f = [text(W / 2, 30, "Досяжний струм заряду — найменша зі стель", size=16, bold=True)]
    f.append(text(W / 2, 52, "слабкий 5 В-адаптер (Rвн 0.5 Ω) у теплому корпусі (Ta 60 °C)",
                  size=12, color=MUTED))

    x0 = 300           # старт горизонтальних смуг
    apw = 128.0        # пікселів на ампер
    baseY = 320

    # осі
    f.append(line(x0, 88, x0, baseY, color=MUTED, sw=1.3))
    f.append(line(x0, baseY, x0 + 3.3 * apw, baseY, color=MUTED, sw=1.3))
    for a in (0, 1, 2, 3):
        xx = x0 + a * apw
        f.append(line(xx, baseY, xx, baseY + 5, color=MUTED, sw=1.0))
        f.append(text(xx, baseY + 20, "%d А" % a, size=11, color=MUTED))

    def cbar(y, val, label, fill, stroke, active=False):
        out = [text(30, y + 17, label, size=12.5, anchor="start",
                    bold=active, color=(INK if active else INK))]
        w = val * apw
        out.append(rect(x0, y, w, 34, fill=fill, stroke=stroke, sw=(2.2 if active else 1.4)))
        out.append(text(x0 + w + 8, y + 17, "%.2f А" % val, size=12,
                        anchor="start", bold=active, color=stroke))
        if active:
            out.append(text(x0 + w / 2, y + 17, "← керує", size=11.5,
                            color=FIELD, bold=True))
        return out

    f += cbar(96,  3.00, "уставка ICHG (просив хост)", "#f4f6f8", MUTED)
    f += cbar(158, 2.73, "стеля TREG (гарячий кристал)", "#fdeceb", POS)
    f += cbar(220, 1.28, "стеля VINDPM (просілий вхід)", "#eef7f0", FIELD, active=True)

    # пунктир від найнижчої стелі вниз до осі
    xmin = x0 + 1.28 * apw
    f.append(line(xmin, 254, xmin, baseY, color=FIELD, sw=1.3, dash="4,4"))

    b, _, _ = textbox(W / 2, 400,
                      "Кожна межа ставить свою стелю; діє найнижча. Тут просів вхід — керує VINDPM, а не «зламаний» заряд.",
                      size=11.5, fill="#eef7f0", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "ceilings.svg"), W, H, *f)


# ── 6. Стіна лінійного зарядника: тепло проти струму (вставка hist) ──────────
def fig_hist_wall():
    W, H = 880, 500
    f = [text(W / 2, 28, "Стіна лінійного зарядника: тепло проти струму заряду",
              size=16, bold=True)]
    ox, oy, top, right = 100, 410, 100, 780
    Imax, Pmax = 3.0, 4.5

    def X(I): return ox + I / Imax * (right - ox)
    def Y(P): return oy - P / Pmax * (oy - top)

    # зона теплового відкату (легкий червоний) над бюджетом корпусу
    f.append(rect(ox, top, right - ox, Y(1.35) - top, fill="#fdeeee", stroke="#fdeeee", sw=0, rx=0))
    # смуга теплового бюджету корпусу (~1 Вт)
    f.append(rect(ox, Y(1.35), right - ox, Y(1.0) - Y(1.35), fill="#f6e6c8", stroke="#d9b779", sw=1, rx=0))
    f.append(text(ox + 8, Y(1.35) - 8, "тепловий бюджет корпусу ≈ 1 Вт",
                  size=10.5, color="#a9772a", anchor="start"))

    # осі
    f.append(line(ox, oy, right, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    for I in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        f.append(line(X(I), oy, X(I), oy + 5, color=MUTED))
        f.append(text(X(I), oy + 20, "%.1f" % I, size=10.5, color=MUTED))
    f.append(text(right, oy + 38, "струм заряду, А →", size=11.5, color=MUTED, anchor="end"))
    for P in [1, 2, 3, 4]:
        f.append(line(ox - 5, Y(P), ox, Y(P), color=MUTED))
        f.append(text(ox - 9, Y(P) + 4, "%d" % P, size=10.5, color=MUTED, anchor="end"))
    f.append(text(ox - 6, top - 12, "тепло, Вт", size=11.5, color=MUTED, anchor="start"))

    # лінії розсіяної потужності
    f.append(line(X(0), Y(0), X(3), Y(1.4 * 3), color=POS, sw=2.8))    # лінійний: 1.4·I
    f.append(line(X(0), Y(0), X(3), Y(0.4 * 3), color=FIELD, sw=2.8))  # buck: ~0.4·I
    f.append(text(560, 118, "лінійний — палить надлишок", size=12, color=POS, anchor="middle", bold=True))
    f.append(text(600, 300, "імпульсний buck", size=12, color=FIELD, anchor="middle", bold=True))

    # стіна: лінійний входить у бюджет коло ~0.9 А
    xw = X(0.857)
    f.append(line(xw, oy, xw, Y(1.2), color=POS, sw=1.3, dash="4,4"))
    f.append(text(xw, oy + 20, "≈0.9 А", size=10.5, color=POS, anchor="middle"))

    # робочі точки на тому самому струмі
    f.append(circle(X(2.5), Y(3.5), 4.5, fill=POS, stroke=POS))
    f.append(text(X(2.5) + 12, Y(3.5) - 4, "швидкий заряд 2–3 А", size=11, color=POS, anchor="start"))
    f.append(circle(X(2.5), Y(1.0), 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(X(2.5) + 14, Y(1.0) + 22, "той самий струм — без перегріву",
                  size=11, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 470,
                      "Лінійний розсіює (Uвх−Uком)·I і швидко впирається в тепловий бюджет;\nbuck переносить ту саму енергію майже без втрат і з ростом струму лишається внизу.",
                      size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "hist-wall.svg"), W, H, *f)


# ── 7. Родовід префіксів: два потоки в одну полицю (вставка hist) ─────────────
def fig_hist_timeline():
    W, H = 1040, 520
    f = [text(W / 2, 30, "Родовід зарядного чипа: два префікси, дві історії",
              size=16, bold=True)]
    axy = 288
    left, per = 60, 35.4

    def X(yr): return left + (yr - 1988) * per

    # фонові смуги епох
    xsplit = X(2009)
    f.append(rect(left, 78, xsplit - left, 350, fill="#eef3fb", stroke="#eef3fb", sw=0, rx=0))
    f.append(rect(xsplit, 78, X(2014.4) - xsplit, 350, fill="#eef7f0", stroke="#eef7f0", sw=0, rx=0))
    f.append(text((left + xsplit) / 2, 70, "лінійні зарядники — надлишок у тепло",
                  size=12, color=NEG, anchor="middle"))
    f.append(text((xsplit + X(2014)) / 2, 70, "імпульсний power-path (buck + I2C)",
                  size=12, color=FIELD, anchor="middle"))

    # вісь часу з десятковими мітками
    f.append(line(left, axy, X(2014), axy, color=MUTED, sw=1.6))
    for yr in [1990, 2000, 2010]:
        f.append(line(X(yr), axy - 5, X(yr), axy + 5, color=MUTED))
        f.append(text(X(yr), axy + 22, str(yr), size=11, color=MUTED))

    def flag(cx, up, s, color, w=176, h=54):
        cy = 168 if up else 408
        box = fitbox(cx - w / 2, cy - h / 2, w, h, s, size=11.5, stroke=color,
                     fill="#ffffff", bold=False)
        stem_y = cy + h / 2 if up else cy - h / 2
        return [box, line(cx, stem_y, cx, axy, color=color, sw=1.4),
                circle(cx, axy, 4.5, fill=color, stroke=color)]

    for frag in flag(X(1989), True, "1989 · Benchmarq\n(Даллас) → префікс «bq»", NEG):
        f.append(frag)
    for frag in flag(X(1998.5), True, "1998–99 · Unitrode,\nтоді TI купують «bq»", NEG, w=186):
        f.append(frag)
    for frag in flag(X(2012), True, "2012 · bq2419x + MP2625\nімпульсний power-path", FIELD, w=196):
        f.append(frag)
    for frag in flag(X(1997), False, "1997 · MPS (Сан-Хосе)\n→ префікс «MP»", "#8e44ad"):
        f.append(frag)
    for frag in flag(X(2008), False, "2008 · TP4056\nлінійний стає масовим", NEG, w=168):
        f.append(frag)

    b, _, _ = textbox(W / 2, 486,
                      "Струми телефонів перерости за ~1 А — і лінійний тепловий бюджет тріснув: галузь перейшла на однокристальний buck.\n«bq» (Даллас→Unitrode→TI) і «MP» (MPS) — сліди двох родоводів у тій самій полиці.",
                      size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_block()
    fig_loops()
    fig_profile()
    fig_powerbal()
    fig_ceilings()
    fig_hist_wall()
    fig_hist_timeline()
    print("OK: block.svg, loops.svg, profile.svg, powerbal.svg, ceilings.svg, hist-wall.svg, hist-timeline.svg")


# ── Два життя чипа: default / host + watchdog (до proj-i2c-charger-driver) ────
def fig_wdstate():
    W, H = 880, 430
    f = [text(W / 2, 28, "Два життя чипа: default і host, а між ними — watchdog",
              size=16, bold=True)]

    f.append(fitbox(58, 62, 168, 44, "увімкнення / POR", size=12,
                    fill="#f4f6f8", stroke=MUTED))
    f.append(arrow(142, 106, 160, 166))

    f.append(fitbox(60, 166, 240, 108,
                    "DEFAULT MODE\nрегістри = типові\nавтономний заряд «як є»\nREG09[7] = 1",
                    size=12.5, fill="#f0f0f0", stroke=MUTED))
    f.append(fitbox(580, 166, 240, 108,
                    "HOST MODE\nваші IINLIM · ICHG · VREG\nчип слухає I2C\nREG09[7] = 0",
                    size=12.5, fill="#eef7f0", stroke=FIELD, bold=True))

    f.append(fitbox(610, 74, 180, 50, "годуй watchdog\nREG01[6]=1  ( < 40 с )",
                    size=11.5, fill="#fff8e8", stroke="#b8860b"))
    f.append(arrow(700, 124, 700, 166, color="#b8860b"))

    f.append(arrow(300, 196, 580, 196, color=INK))
    f.append(text(440, 186, "будь-який I2C-запис", size=12, color=INK))

    f.append(arrow(580, 240, 300, 240, color=POS))
    f.append(text(440, 258, "watchdog сплив без годування", size=12, color=POS))
    f.append(text(440, 273, "→ усі регістри в default, уставки втрачено", size=11, color=POS))

    b, _, _ = textbox(W / 2, 388,
        "Вимкнути watchdog (REG05[5:4]=00) — таймера нема зовсім:\n"
        "чип не зітре ваших уставок, але й сам не відкотиться\n"
        "в безпечний режим, якщо господар зависне.",
        size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "wdstate.svg"), W, H, *f)


# ── Порядок підняття + реакція на USB-PD (до proj-i2c-charger-driver) ─────────
def fig_sequence():
    W, H = 880, 620
    f = [text(W / 2, 28, "Порядок підняття драйвера і реакція на USB-PD",
              size=16, bold=True)]

    bx, bw, bh = 70, 500, 44
    cx = bx + bw / 2
    steps = [
        (62,  "1 · Хто на шині?  читаємо REG0A (PN)", FILL, LINE, False),
        (120, "2 · REG_RST=1 → перехід у host mode",   FILL, LINE, False),
        (178, "3 · Заборонити заряд  (CHG_CONFIG=00)",  FILL, LINE, False),
        (236, "4 · Вхідний ліміт IINLIM ← скільки джерело дає", "#eef7f0", FIELD, True),
        (294, "5 · Струм ICHG · напруга VREG · поріг ITERM", FILL, LINE, False),
        (352, "6 · Дозволити заряд  (CHG_CONFIG=01)",   "#eef7f0", FIELD, True),
    ]
    for cy, label, fill, stroke, bold in steps:
        f.append(fitbox(bx, cy - bh / 2, bw, bh, label, size=12.5,
                        fill=fill, stroke=stroke, bold=bold))
    for i in range(len(steps) - 1):
        y1 = steps[i][0] + bh / 2
        y2 = steps[i + 1][0] - bh / 2
        f.append(arrow(cx, y1, cx, y2))

    xb = bx + bw + 18
    f.append(line(xb, 236, xb, 352, color=FIELD, sw=2.4))
    f.append(line(xb, 236, xb - 8, 236, color=FIELD, sw=2.4))
    f.append(line(xb, 352, xb - 8, 352, color=FIELD, sw=2.4))
    f.append(mtext(xb + 8, 284, ["ліміт входу", "— ДО дозволу", "заряду"],
                   size=11.5, color=FIELD, anchor="start", bold=True))

    f.append(line(bx, 406, bx + bw, 406, color=MUTED, sw=1.2, dash="4,4"))

    f.append(fitbox(bx, 420, bw, 50,
                    "ЦИКЛ  < 40 с:  годуй watchdog (REG01[6]=1)  +  читай REG08 → активний контур",
                    size=12, fill="#fff8e8", stroke="#b8860b"))
    f.append(text(cx, 486, "повторюється, доки заряджаємо", size=10.5, color=MUTED))

    f.append(fitbox(bx, 502, bw, 50,
                    "подія USB-PD:  вхід  5 В / 0.5 А  →  9 В / 2 А",
                    size=13, fill="#eef3fb", stroke=NEG, bold=True))

    f.append(line(bx + bw, 527, 700, 527, color=NEG, sw=1.8))
    f.append(line(700, 527, 700, 236, color=NEG, sw=1.8))
    f.append(arrow(700, 236, bx + bw + 2, 236, color=NEG))
    f.append(mtext(708, 366, ["новий вхід →", "знову IINLIM", "першим,", "тоді ICHG"],
                   size=11, color=NEG, anchor="start"))
    render(os.path.join(IMG, "sequence.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wdstate()
    fig_sequence()
    print("OK(proj): wdstate.svg, sequence.svg")
