# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ статті «BJT: навантаження» (bjt-load-driving-d.md).
Запуск:  python figs-d.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def ground(x, y, label=None):
    out = [line(x, y, x, y + 6, color=INK, sw=1.8),
           line(x - 14, y + 6, x + 14, y + 6, color=INK, sw=2.2),
           line(x - 9, y + 11, x + 9, y + 11, color=INK, sw=2.0),
           line(x - 4, y + 16, x + 4, y + 16, color=INK, sw=1.8)]
    if label:
        out.append(text(x + 34, y + 12, label, size=10, color=MUTED, anchor="start"))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Три робочі точки на вихідних характеристиках: відсічка · активний · насичення
#    (ГЛИБШЕ за базову: показує лінію навантаження й ЧОМУ ключ сидить у куті)
# ─────────────────────────────────────────────────────────────────────────────
def fig_load_line():
    W, H = 780, 470
    f = [text(W / 2, 26, "Лінія навантаження на вихідних характеристиках Ic(Vce)",
              size=16, bold=True)]

    ox, oy = 110, 380          # початок осей
    ax_w, ax_h = 560, 300
    # осі
    f.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w - 4, oy + 26, "Vce (В)", size=12, anchor="end"))
    f.append(text(ox - 8, oy - ax_h + 6, "Ic (мА)", size=12, anchor="end"))

    Vcc_x = ox + ax_w - 60     # точка Vcc на осі напруг (Ic=0)
    Ic_top = oy - ax_h + 40    # рівень Ic = Vcc/Rload (Vce=0)

    # родина вихідних кривих (різні Ib) — насичення злива ліворуч, поличка праворуч
    curves_y = [oy - 250, oy - 205, oy - 165, oy - 130, oy - 100]
    lbl = ["Ib велике", "", "", "", "Ib мале"]
    knee_x = ox + 70
    for i, yy in enumerate(curves_y):
        d = 'M %.1f %.1f ' % (ox, oy)
        # круте зростання в насиченні (коліно)
        d += 'C %.1f %.1f %.1f %.1f %.1f %.1f ' % (ox + 14, yy + 8, knee_x - 26, yy, knee_x, yy)
        # майже горизонтальна поличка в активному (легкий нахил — ефект Ерлі)
        d += 'L %.1f %.1f' % (ox + ax_w - 20, yy - 14)
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d, MUTED))
    f.append(text(knee_x + 150, curves_y[0] - 20, "більший Ib → вища поличка", size=10, color=MUTED, anchor="start"))
    f.append(text(knee_x + 150, curves_y[-1] + 4, "менший Ib → нижча", size=10, color=MUTED, anchor="start"))

    # лінія навантаження: від (Vcc, 0) до (0, Vcc/R)
    f.append(line(Vcc_x, oy, ox, Ic_top, color=POS, sw=2.4))
    f.append(text(Vcc_x - 40, oy - 8, "лінія навантаження", size=11, color=POS, anchor="end"))
    f.append(text(Vcc_x, oy + 18, "Vcc", size=11, color=INK))
    f.append(line(ox, Ic_top, ox - 5, Ic_top, color=INK, sw=1.5))
    f.append(text(ox - 10, Ic_top + 4, "Vcc/R", size=10, color=INK, anchor="end"))

    # точка НАСИЧЕННЯ (перетин лінії з верхньою кривою — у коліні)
    sx, sy = knee_x + 6, Ic_top + 6
    f.append(circle(sx, sy, 6, fill=FIELD, stroke=INK, sw=1.6))
    f.append(text(sx + 4, sy - 14, "НАСИЧЕННЯ", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(sx + 4, sy + 22, "Vce(sat) мала, Ic ≈ Vcc/R", size=10, color=MUTED, anchor="start"))

    # точка ВІДСІЧКИ (Ic≈0, Vce≈Vcc)
    cx, cy = Vcc_x, oy - 6
    f.append(circle(cx, cy, 6, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(cx - 6, cy - 12, "ВІДСІЧКА", size=11, bold=True, color=NEG, anchor="end"))

    # точка АКТИВНОГО (посередині лінії)
    mx, my = (sx + cx) / 2 + 20, (sy + cy) / 2 - 4
    f.append(circle(mx, my, 6, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(mx + 10, my + 4, "активний — тут гріється", size=10, color=POS, anchor="start"))

    note = ("Ключ ЖИВЕ у двох кінцях лінії: насичення (ліворуч, холодно) або відсічка (праворуч, холодно).\n"
            "Провал посередині — активний режим: і Vce, і Ic великі → добуток великий → грійка.")
    f.append(fitbox(ox, oy + 40, ax_w, 44, note, size=11, fill=FILL, stroke=MUTED))
    render(os.path.join(IMG, "load-line.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Чотири фази перемикання в часі: затримка · наростання · СХОВОК · спад
#    (ГЛИБШЕ: базова цього не має; storage time — головний ворог ШІМ на BJT)
# ─────────────────────────────────────────────────────────────────────────────
def fig_switching():
    W, H = 800, 430
    f = [text(W / 2, 26, "Перемикання BJT у часі: чотири фази й де ховається затримка",
              size=16, bold=True)]

    ox = 90
    top = 70
    row_h = 150
    ax_w = 630

    # ── верхній графік: струм бази Ib(t) — прямокутний ──
    yb = top
    f.append(text(ox - 10, yb - 4, "Ib", size=13, bold=True, anchor="end"))
    f.append(line(ox, yb + 60, ox + ax_w, yb + 60, color=MUTED, sw=1.2))   # нуль
    t_on, t_off = ox + 60, ox + 380
    f.append(line(ox, yb + 60, t_on, yb + 60, color=NEG, sw=2.2))
    f.append(line(t_on, yb + 60, t_on, yb + 12, color=NEG, sw=2.2))
    f.append(line(t_on, yb + 12, t_off, yb + 12, color=NEG, sw=2.2))
    f.append(line(t_off, yb + 12, t_off, yb + 60, color=NEG, sw=2.2))
    f.append(line(t_off, yb + 60, ox + ax_w, yb + 60, color=NEG, sw=2.2))
    f.append(text(t_on + 8, yb + 8, "+Ib (уливаємо)", size=10, color=NEG, anchor="start"))
    f.append(text(t_off + 8, yb + 8, "0 (знімаємо)", size=10, color=NEG, anchor="start"))

    # ── нижній графік: струм колектора Ic(t) — із затримками ──
    yc = top + row_h
    f.append(text(ox - 10, yc - 4, "Ic", size=13, bold=True, anchor="end"))
    base = yc + 90
    peak = yc + 18
    f.append(line(ox, base, ox + ax_w, base, color=MUTED, sw=1.2))   # нуль

    # фаза 1: td — затримка ввімкнення (Ic ще нуль трохи після Ib)
    td = t_on + 26
    # фаза 2: tr — наростання
    tr = td + 40
    # тримається ввімкненим…
    # фаза 3: ts — СХОВОК (storage): Ib уже знято, а Ic ще тече!
    ts = t_off + 70
    # фаза 4: tf — спад
    tf = ts + 46

    d = ('M %.1f %.1f L %.1f %.1f ' % (ox, base, td, base) +           # td: нуль
         'L %.1f %.1f ' % (tr, peak) +                                  # tr: наростання
         'L %.1f %.1f ' % (ts, peak) +                                  # плато (ввімкнено)
         'L %.1f %.1f ' % (tf, base))                                   # tf: спад (після ts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))

    # вертикальні маркери фаз
    for xx, lab, col in [(td, "t_d", MUTED), (tr, "t_r", MUTED), (ts, "t_s", INK), (tf, "t_f", MUTED)]:
        f.append(line(xx, top + 60, xx, base, color="#c9ccd1", sw=1.0, dash="3,3"))
    # підписи інтервалів
    f.append(text((t_on + td) / 2, base + 18, "t_d", size=11, color=MUTED))
    f.append(text((td + tr) / 2, base + 18, "t_r", size=11, color=MUTED))
    f.append(text((t_off + ts) / 2, base + 18, "t_s", size=12, bold=True, color=POS))
    f.append(text((ts + tf) / 2, base + 18, "t_f", size=11, color=MUTED))

    # виноска на storage time
    f.append(line(t_off, yb + 12, t_off, base + 40, color=POS, sw=1.0, dash="2,3"))
    box = ("t_s — «сховок» (storage): базу вже вимкнули, а колектор ще проводить.\n"
           "Причина — надлишковий заряд у базі від глибокого насичення. Це головна\n"
           "затримка вимкнення й головна втрата на ШІМ. Лікують клампом Бейкера.")
    f.append(fitbox(ox, base + 40, ax_w, 60, box, size=11, fill="#fdf0ee", stroke=POS))
    render(os.path.join(IMG, "switching-phases.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Тепловий ланцюг опорів: перехід → корпус → радіатор → повітря
#    (ГЛИБШЕ: базова каже «перевір грійку»; тут — ЯК рахувати Tj по ланцюгу)
# ─────────────────────────────────────────────────────────────────────────────
def fig_thermal_chain():
    W, H = 820, 300
    f = [text(W / 2, 26, "Тепловий ланцюг: як потужність-грійка піднімає температуру переходу",
              size=16, bold=True)]

    y = 130
    # вузли (температури) і між ними — опори θ
    nodes = [
        (90,  "Перехід", "Tj", "#fdecea", POS),
        (300, "Корпус",  "Tc", FILL, INK),
        (510, "Радіатор", "Ts", FILL, INK),
        (720, "Повітря",  "Ta", "#eaf0fd", NEG),
    ]
    nx = []
    for x, name, t, fill, col in nodes:
        f.append(circle(x, y, 30, fill=fill, stroke=col, sw=2.0))
        f.append(text(x, y - 2, t, size=15, bold=True, color=col))
        f.append(text(x, y + 46, name, size=11, color=MUTED))
        nx.append(x)

    thetas = ["θ(j-c)\nперехід→корпус", "θ(c-s)\nкорпус→радіатор", "θ(s-a)\nрадіатор→повітря"]
    for i in range(3):
        x1, x2 = nx[i] + 30, nx[i + 1] - 30
        f.append(arrow(x1, y, x2, y, color=INK, sw=1.8))
        mid = (x1 + x2) / 2
        f.append(text(mid, y - 44, thetas[i].split("\n")[0], size=12, bold=True))
        f.append(text(mid, y - 28, thetas[i].split("\n")[1], size=9, color=MUTED))

    # символ джерела тепла зліва
    f.append(text(90, y - 52, "P = Vce·Ic", size=12, bold=True, color=POS))

    note = ("Tj = Ta + P · (θjc + θcs + θsa).   Опори θ (°C/Вт) складаються послідовно, як у колі.\n"
            "Радіатор зменшує ОСТАННЮ ланку θsa — і весь ланцюг холоне. Без радіатора θca велике → Tj злітає.")
    f.append(fitbox(90, y + 70, 660, 50, note, size=11, fill=FILL, stroke=FIELD))
    render(os.path.join(IMG, "thermal-chain.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Область безпечної роботи (SOA): чому P=Vce·Ic — не єдина межа
#    (ГЛИБША ідея: другий пробій дає скошену межу, якої немає в базовій)
# ─────────────────────────────────────────────────────────────────────────────
def fig_soa():
    W, H = 760, 500
    f = [text(W / 2, 26, "Область безпечної роботи (SOA): чотири стіни, а не одна",
              size=16, bold=True)]

    ox, oy = 110, 400
    ax_w, ax_h = 540, 320
    f.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w - 4, oy + 26, "Vce (лог.)", size=12, anchor="end"))
    f.append(text(ox - 8, oy - ax_h + 4, "Ic (лог.)", size=12, anchor="end"))

    top = oy - ax_h + 30
    right = ox + ax_w - 30

    # 1) горизонтальна стеля — Ic(max)
    f.append(line(ox, top, ox + 150, top, color=INK, sw=2.4))
    f.append(text(ox + 6, top - 8, "Ic(max)", size=11, bold=True, anchor="start"))

    # 2) похила P(max) — постійна потужність (у лог-лог = пряма з нахилом −1)
    px1, py1 = ox + 150, top
    px2, py2 = ox + 330, top + 120
    f.append(line(px1, py1, px2, py2, color=FIELD, sw=2.4))
    f.append(text(px1 + 30, py1 + 40, "P(max) = Vce·Ic", size=11, bold=True, color=FIELD, anchor="start"))

    # 3) КРУТІШИЙ злам — другий пробій (нахил крутіший за −1)
    b1x, b1y = px2, py2
    b2x, b2y = ox + 430, top + 235
    f.append(line(b1x, b1y, b2x, b2y, color=POS, sw=2.8))
    f.append(text(b1x + 8, b1y + 44, "другий пробій", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(b1x + 8, b1y + 60, "(тільки в BJT!)", size=9, color=POS, anchor="start"))

    # 4) вертикальна стіна — Vceo (пробій напруги)
    f.append(line(right, oy, right, top + 200, color=NEG, sw=2.4))
    f.append(text(right - 6, top + 196, "Vceo", size=11, bold=True, color=NEG, anchor="end"))
    # замкнути нижній правий кут до осі
    f.append(line(b2x, b2y, right, oy - (oy - (top + 235)) + 0, color=MUTED, sw=1.0, dash="4,3"))

    # затінена безпечна зона (грубий полігон)
    poly = "%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" % (
        ox, oy, ox, top, px2, py2, b2x, b2y, right, top + 200, right, oy)
    f.append('<polygon points="%s" fill="#27ae60" fill-opacity="0.07" stroke="none"/>' % poly)
    f.append(text(ox + 150, oy - 60, "БЕЗПЕЧНО", size=13, bold=True, color=FIELD))

    note = ("Базова формула P=Vce·Ic — це лише ЗЕЛЕНА стіна. У BJT є ще ЧЕРВОНА, крутіша: другий\n"
            "пробій. На високій Vce струм збирається у гарячу нитку-філамент і пропалює кристал\n"
            "РАНІШЕ, ніж досягнуто P(max). Тому індуктивний зрив небезпечний удвічі: там і Vce, і Ic великі.")
    f.append(fitbox(ox, oy + 40, ax_w, 62, note, size=11, fill="#fdf0ee", stroke=POS))
    render(os.path.join(IMG, "soa.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Три способи причепити навантаження: low-side · high-side (PNP) · рівнозсув
#    (ГЛИБШЕ: базова робить лише low-side NPN; тут — повна карта)
# ─────────────────────────────────────────────────────────────────────────────
def fig_side_topologies():
    W, H = 900, 400
    f = [text(W / 2, 26, "Куди ставити ключ: нижній, верхній і чому напряму NPN зверху не можна",
              size=16, bold=True)]

    def npn(cx, cy, lab):
        out = [line(cx, cy - 20, cx, cy + 20, color=INK, sw=2.4),
               line(cx - 22, cy, cx, cy, color=INK, sw=1.6),
               line(cx, cy - 14, cx + 20, cy - 30, color=INK, sw=1.6),
               line(cx + 20, cy - 30, cx + 20, cy - 44, color=INK, sw=1.6),
               line(cx, cy + 14, cx + 20, cy + 30, color=INK, sw=1.6),
               line(cx + 20, cy + 30, cx + 20, cy + 44, color=INK, sw=1.6),
               '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
                   cx + 11, cy + 20, cx + 20, cy + 30, cx + 9, cy + 29, INK),
               text(cx - 6, cy + 4, lab, size=10, color=MUTED, anchor="end")]
        return "".join(out)

    def pnp(cx, cy, lab):
        out = [line(cx, cy - 20, cx, cy + 20, color=INK, sw=2.4),
               line(cx - 22, cy, cx, cy, color=INK, sw=1.6),
               line(cx, cy - 14, cx + 20, cy - 30, color=INK, sw=1.6),
               line(cx + 20, cy - 30, cx + 20, cy - 44, color=INK, sw=1.6),
               line(cx, cy + 14, cx + 20, cy + 30, color=INK, sw=1.6),
               line(cx + 20, cy + 30, cx + 20, cy + 44, color=INK, sw=1.6),
               '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
                   cx + 2, cy - 12, cx, cy, cx + 11, cy - 4, INK),
               text(cx - 6, cy + 4, lab, size=10, color=MUTED, anchor="end")]
        return "".join(out)

    col_w = 280
    # ── панель 1: LOW-SIDE (NPN знизу) ──
    x0 = 30
    f.append(rect(x0, 56, col_w - 20, 300, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(x0 + (col_w - 20) / 2, 78, "Нижній ключ (low-side)", size=13, bold=True))
    cx = x0 + 130
    f.append(plus(cx, 108)); f.append(text(cx + 20, 112, "+V", size=11, anchor="start"))
    f.append(rect(cx - 26, 128, 52, 30, fill="#eef1f5", stroke=INK, sw=1.4, rx=4))
    f.append(text(cx, 148, "навант.", size=10))
    f.append(line(cx, 108 + 9, cx, 128, color=INK, sw=1.6))
    f.append(line(cx, 158, cx, 176, color=INK, sw=1.6))
    f.append(npn(cx, 200, "NPN"))
    f.append(ground(cx + 20, 244))
    f.append(line(cx - 22, 200, cx - 70, 200, color=INK, sw=1.6))
    f.append(text(cx - 74, 204, "МК", size=10, anchor="end", color=NEG))
    f.append(fitbox(x0 + 8, 300, col_w - 36, 48,
                    "Навантаження між +V і колектором. Емітер на землі — Vbe чистий.\nПРОСТО. Базовий випадок.",
                    size=10, fill="#f0f7f1", stroke=FIELD))

    # ── панель 2: HIGH-SIDE PNP ──
    x0 = 30 + col_w
    f.append(rect(x0, 56, col_w - 20, 300, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(x0 + (col_w - 20) / 2, 78, "Верхній ключ на PNP", size=13, bold=True))
    cx = x0 + 130
    f.append(plus(cx, 104)); f.append(text(cx + 20, 108, "+V", size=11, anchor="start"))
    f.append(line(cx, 104 + 9, cx, 156, color=INK, sw=1.6))
    f.append(pnp(cx, 180, "PNP"))
    f.append(line(cx, 180 + 44, cx, 236, color=INK, sw=1.6))
    f.append(rect(cx - 26, 236, 52, 30, fill="#eef1f5", stroke=INK, sw=1.4, rx=4))
    f.append(text(cx, 256, "навант.", size=10))
    f.append(line(cx, 266, cx, 284, color=INK, sw=1.6))
    f.append(ground(cx, 284))
    # база PNP керується ЧЕРЕЗ ключ до землі
    f.append(line(cx - 22, 180, cx - 66, 180, color=INK, sw=1.6))
    f.append(text(cx - 70, 184, "тягнути\nвниз", size=9, anchor="end", color=POS).replace("\n", " "))
    f.append(fitbox(x0 + 8, 300, col_w - 36, 48,
                    "Емітер на +V. Вмикається, коли базу тягнуть НИЖЧЕ +V.\nАле МК на 3.3 В не закриє базу при +12 В — треба ще ключ.",
                    size=10, fill="#fdf0ee", stroke=POS))

    # ── панель 3: чому NPN зверху ПОГАНО ──
    x0 = 30 + 2 * col_w
    f.append(rect(x0, 56, col_w - 20, 300, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(x0 + (col_w - 20) / 2, 78, "NPN зверху — пастка", size=13, bold=True))
    cx = x0 + 120
    f.append(plus(cx, 104)); f.append(text(cx + 20, 108, "+V", size=11, anchor="start"))
    f.append(line(cx, 104 + 9, cx, 132, color=INK, sw=1.6))
    f.append(npn(cx, 156, "NPN"))
    f.append(line(cx, 156 + 44, cx, 214, color=INK, sw=1.6))
    f.append(rect(cx - 26, 214, 52, 30, fill="#eef1f5", stroke=INK, sw=1.4, rx=4))
    f.append(text(cx, 234, "навант.", size=10))
    f.append(line(cx, 244, cx, 262, color=INK, sw=1.6))
    f.append(ground(cx, 262))
    f.append(line(cx - 22, 156, cx - 60, 156, color=INK, sw=1.6))
    f.append(text(cx - 64, 160, "Vб", size=10, anchor="end", color=NEG))
    f.append(fitbox(x0 + 8, 300, col_w - 36, 48,
                    "Емітер «плаває» на Vнавант. Щоб відкрити, базі треба Vе+0.7 —\nВИЩЕ за +V. МК цього не дасть. Емітерний повторювач ≠ ключ.",
                    size=10, fill="#fdf0ee", stroke=POS))

    render(os.path.join(IMG, "side-topologies.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Кламп Бейкера: діод колектор→база зливає надлишок і не пускає в глибоке насичення
# ─────────────────────────────────────────────────────────────────────────────
def fig_baker():
    W, H = 720, 400
    f = [text(W / 2, 26, "Кламп Бейкера: як прибрати «сховок» і прискорити вимкнення",
              size=16, bold=True)]

    # транзистор у центрі
    cx, cy = 340, 210
    f.append(line(cx, cy - 28, cx, cy + 28, color=INK, sw=2.6))         # база-планка
    f.append(line(cx, cy - 18, cx + 26, cy - 40, color=INK, sw=1.8))    # колектор
    f.append(line(cx + 26, cy - 40, cx + 26, cy - 66, color=INK, sw=1.8))
    f.append(line(cx, cy + 18, cx + 26, cy + 40, color=INK, sw=1.8))    # емітер
    f.append(line(cx + 26, cy + 40, cx + 26, cy + 66, color=INK, sw=1.8))
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>' % (
        cx + 17, cy + 30, cx + 26, cy + 40, cx + 15, cy + 39, INK))
    f.append(text(cx - 6, cy - 4, "T", size=12, color=MUTED, anchor="end"))

    # колектор угору → навантаження → +V
    f.append(line(cx + 26, cy - 66, cx + 26, cy - 96, color=INK, sw=1.8))
    f.append(rect(cx + 6, cy - 138, 40, 26, fill="#eef1f5", stroke=INK, sw=1.4, rx=4))
    f.append(text(cx + 26, cy - 120, "навант.", size=9))
    f.append(line(cx + 26, cy - 112, cx + 26, cy - 96, color=INK, sw=1.6))
    f.append(plus(cx + 26, cy - 152)); f.append(text(cx + 48, cy - 148, "+V", size=11, anchor="start"))

    # емітер → земля
    f.append(ground(cx + 26, cy + 66))

    # база: вхід через Rb зліва
    f.append(line(cx, cy, cx - 40, cy, color=INK, sw=1.6))
    f.append(rect(cx - 118, cy - 13, 54, 26, fill="#eef1f5", stroke=INK, sw=1.4, rx=4))
    f.append(text(cx - 91, cy + 4, "Rb", size=11))
    f.append(line(cx - 64, cy, cx - 40, cy, color=INK, sw=1.6))
    f.append(line(cx - 118, cy, cx - 158, cy, color=INK, sw=1.6))
    f.append(text(cx - 162, cy + 4, "з МК", size=10, anchor="end", color=NEG))
    f.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (cx - 40, cy, INK))

    # КЛАМП-ДІОД: від колектора (верх) до бази (вузол cx-40) — вістря до бази
    node_x, node_y = cx - 40, cy
    col_x, col_y = cx + 26, cy - 81
    # ведемо провід від колектора ліворуч-угору, тоді вниз до вузла бази
    f.append(line(col_x, col_y, node_x, col_y, color=POS, sw=1.8))
    # діод на вертикалі node_x між col_y і node_y (провідність згори вниз: анод угорі=колектор)
    dy1, dy2 = col_y + 18, col_y + 50
    f.append(line(node_x, col_y, node_x, dy1, color=POS, sw=1.8))
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="1.8"/>' % (
        node_x - 9, dy1, node_x + 9, dy1, node_x, dy1 + 16, POS))
    f.append(line(node_x - 9, dy1 + 16, node_x + 9, dy1 + 16, color=POS, sw=2.4))   # катод-планка
    f.append(line(node_x, dy1 + 16, node_x, node_y, color=POS, sw=1.8))
    f.append(text(node_x - 14, (col_y + node_y) / 2, "діод\nБейкера", size=10, color=POS, anchor="end").replace("\n", " "))

    note = ("Коли колектор намагається впасти нижче за базу (глибоке насичення), діод відкривається\n"
            "й зливає ЗАЙВИЙ струм бази прямо в колектор. Транзистор застигає на межі насичення:\n"
            "Vce ≈ 0.3…0.4 В замість 0.1 В — трохи більша грійка, зате майже НУЛЬ зайвого заряду,\n"
            "тож «сховок» t_s зникає. У TTL-серії «S» це роблять діодом Шотткі прямо в кристалі.")
    f.append(fitbox(70, 300, 580, 74, note, size=11, fill="#fdf0ee", stroke=POS))
    render(os.path.join(IMG, "baker-clamp.svg"), W, H, *f)


if __name__ == "__main__":
    fig_load_line()
    fig_switching()
    fig_thermal_chain()
    fig_soa()
    fig_side_topologies()
    fig_baker()
    print("OK: load-line, switching-phases, thermal-chain, soa, side-topologies, baker-clamp")
