# -*- coding: utf-8 -*-
"""Фігури для guide/embedded/keruvannia/tone-detection/tone-detection.md
Генерує SVG у ./img/  Запуск: python figs.py
Імпортує спільний svgkit зі scripts/ (примітиви не переписувати).
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# F1 — Сітка DTMF: кнопка = перетин рядка (низька частота) і стовпця (висока).
# ─────────────────────────────────────────────────────────────────────────────
def fig_dtmf_grid():
    W, H = 560, 360
    f = []
    f.append(text(W / 2, 26, "Сітка DTMF: кнопка — перетин рядка і стовпця", size=15, bold=True))

    rows = [697, 770, 852, 941]
    cols = [1209, 1336, 1477, 1633]
    keys = [['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']]

    # геометрія таблиці
    x0, y0 = 150, 92          # лівий-верхній кут сітки кнопок
    cw, ch = 84, 56           # розмір клітинки

    # підписи стовпцевих (високих) частот — зверху
    f.append(text(x0 + 2 * cw, 56, "стовпці — високі частоти, Гц", size=11, color=NEG, bold=True))
    for j, fr in enumerate(cols):
        cx = x0 + j * cw + cw / 2
        f.append(text(cx, 80, "%d" % fr, size=11, color=NEG, bold=True))

    # підпис рядкових (низьких) частот — збоку (вертикально вздовж лівого краю)
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 34 %.1f)">'
             '%s</text>' % (y0 + 2 * ch, FONT, FIELD, y0 + 2 * ch,
                            esc("рядки — низькі частоти, Гц")))
    for i, fr in enumerate(rows):
        cy = y0 + i * ch + ch / 2
        f.append(text(x0 - 14, cy + 4, "%d" % fr, size=11, color=FIELD,
                      anchor="end", bold=True))

    # клітинки-кнопки
    for i in range(4):
        for j in range(4):
            x = x0 + j * cw
            y = y0 + i * ch
            # четвертий стовпець (A/B/C/D) — приглушений: рідко використовують
            extra = (j == 3)
            fill = "#f7f7f7" if extra else "#eef3fb"
            stroke = MUTED if extra else NEG
            f.append(rect(x, y, cw - 6, ch - 6, fill=fill, stroke=stroke, sw=1.4, rx=8))
            col = MUTED if extra else INK
            f.append(text(x + (cw - 6) / 2, y + (ch - 6) / 2 + 8, keys[i][j],
                          size=22, color=col, bold=True))

    # виділити кнопку «5» як приклад (рядок 770, стовпець 1336)
    hx = x0 + 1 * cw
    hy = y0 + 1 * ch
    f.append(rect(hx - 1, hy - 1, cw - 4, ch - 4, fill="none", stroke=POS, sw=2.6, rx=9))
    f.append(text(W / 2, 344,
                  "приклад: «5» = 770 Гц (рядок) + 1336 Гц (стовпець)",
                  size=11, color=POS, italic=True))

    render(os.path.join(OUT, "dtmf-grid.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F2 — Детектор: вісім бінів Ґерцеля, два переможці (770 і 1336 Гц) для «5».
# ─────────────────────────────────────────────────────────────────────────────
def fig_dtmf_detect():
    W, H = 720, 340
    f = []
    f.append(text(W / 2, 26, "Натиск «5»: два піки серед восьми бінів", size=15, bold=True))

    ox, oy = 70, 250          # початок осей
    axw = 600
    # осі
    f.append(arrow(ox, oy, ox, 62, color=INK, sw=1.4))
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.4))
    f.append(text(ox + axw - 6, oy + 20, "частота →", size=10, color=INK, bold=True))
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="10" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %.1f)">power</text>'
             % ((oy + 62) / 2, FONT, INK, (oy + 62) / 2))

    # вісім бінів: (частота, висота, переможець?)
    bins = [
        (697, 22, False), (770, 150, True), (852, 20, False), (941, 16, False),
        (1209, 24, False), (1336, 138, True), (1477, 18, False), (1633, 14, False),
    ]
    n = len(bins)
    step = axw / (n + 1)
    # пунктир порога
    thr = 70
    f.append(line(ox, oy - thr, ox + axw, oy - thr, color=MUTED, sw=1.0, dash="5,4"))
    f.append(text(ox + axw - 4, oy - thr - 5, "поріг", size=9, color=MUTED, anchor="end", italic=True))

    # розділова смуга між групами (між 941 і 1209)
    gx = ox + 4.5 * step
    f.append(line(gx, oy, gx, 70, color="#dddddd", sw=1.0, dash="3,5"))
    f.append(text(ox + 2.0 * step, 78, "низька група", size=10, color=FIELD, bold=True))
    f.append(text(ox + 6.5 * step, 78, "висока група", size=10, color=NEG, bold=True))

    for i, (fr, h, win) in enumerate(bins):
        x = ox + (i + 1) * step
        col = POS if win else ("#9aa0a6")
        sw = 11 if win else 9
        f.append(line(x, oy, x, oy - h, color=col, sw=sw))
        f.append(text(x, oy + 16, "%d" % fr, size=9.5,
                      color=(INK if win else MUTED), bold=win))
        if win:
            f.append(text(x, oy - h - 8, "пік", size=10, color=POS, bold=True))

    f.append(text(W / 2, 318,
                  "два найсильніші біни (770 + 1336 Гц) над порогом → перетин у таблиці = «5»",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "dtmf-detect.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F3 (proj) — Потік даних декодера: АЦП-ISR кидає відліки → банк із 8 Ґерцелів
#   рахує на льоту → на межі блоку рішення → автомат дебаунсу → подія «цифра».
#   Підкреслює межу «швидко в ISR» / «важко в головному циклі».
# ─────────────────────────────────────────────────────────────────────────────
def fig_pipeline():
    W, H = 760, 350
    f = []
    f.append(text(W / 2, 26, "Потік даних декодера DTMF: від ISR АЦП до події «цифра»",
                  size=15, bold=True))

    # межа ISR / головний цикл
    f.append(rect(30, 52, 200, 270, fill="#fdf6f5", stroke=POS, sw=1.4, rx=10))
    f.append(text(130, 72, "у перериванні АЦП", size=11, color=POS, bold=True))
    f.append(text(130, 88, "(коротко, щотакту fs)", size=9.5, color=MUTED, italic=True))

    f.append(rect(250, 52, 480, 270, fill="#f3f8ff", stroke=NEG, sw=1.4, rx=10))
    f.append(text(490, 72, "у головному циклі (раз на блок)", size=11, color=NEG, bold=True))

    # ── у ISR: відлік → банк ─────────────────────────────────────────────
    b1 = fitbox(52, 104, 156, 50, "1 відлік x\nз АЦП", size=11,
                fill="#ffffff", stroke=POS, sw=1.5, color=INK, bold=True)
    f.append(b1)
    f.append(arrow(130, 154, 130, 176, color=INK, sw=1.8))
    b2 = fitbox(52, 176, 156, 64,
                "g_push() ×8:\nкожен фільтр\nковтає відлік",
                size=10.5, fill="#ffffff", stroke=POS, sw=1.5, color=INK)
    f.append(b2)
    f.append(text(130, 262, "стан = 8 пар (s1,s2)", size=9.5, color=MUTED, italic=True))
    f.append(text(130, 280, "буфера НЕ треба", size=9.5, color=FIELD, bold=True))
    f.append(text(130, 304, "набрали N? →", size=10, color=POS, bold=True))

    # стрілка через межу: набрано N
    f.append(arrow(212, 208, 268, 208, color=INK, sw=2))
    f.append(text(240, 200, "N", size=10, color=INK, bold=True))

    # ── у головному циклі: рішення → перевірки → FSM → подія ──────────────
    col_x, col_w = 268, 200
    s1 = fitbox(col_x, 104, col_w, 50,
                "8 значень power →\nдва переможці (рядок, стовпець)",
                size=10, fill="#ffffff", stroke=NEG, sw=1.5, color=INK)
    f.append(s1)
    f.append(arrow(col_x + col_w / 2, 154, col_x + col_w / 2, 174, color=INK, sw=1.8))
    s2 = fitbox(col_x, 174, col_w, 58,
                "перевірки надійності:\nпоріг · суперник · twist",
                size=10, fill="#ffffff", stroke=NEG, sw=1.5, color=INK)
    f.append(s2)
    f.append(arrow(col_x + col_w / 2, 232, col_x + col_w / 2, 252, color=INK, sw=1.8))
    s3 = fitbox(col_x, 252, col_w, 56,
                "сирий символ блоку\n(або «тиша»)",
                size=10.5, fill="#ffffff", stroke=NEG, sw=1.5, color=INK)
    f.append(s3)

    # → FSM
    fsm_x = 492
    f.append(arrow(col_x + col_w, 280, fsm_x - 2, 280, color=INK, sw=2))
    s4 = fitbox(fsm_x, 174, 218, 92,
                "автомат дебаунсу:\nпідтвердити M блоків\n+ дочекатися тиші\nміж цифрами",
                size=11, fill="#eafaf0", stroke=FIELD, sw=1.7, color=INK, bold=True)
    f.append(s4)
    f.append(arrow(fsm_x + 109, 174, fsm_x + 109, 150, color=INK, sw=1.8))
    s5 = fitbox(fsm_x, 104, 218, 46,
                "подія «натиснуто X»\n(рівно один раз)",
                size=11, fill="#ffffff", stroke=FIELD, sw=1.6, color=FIELD, bold=True)
    f.append(s5)

    f.append(text(W / 2, 340,
                  "межа головна: у ISR — лише дешевий g_push; усе важке рішення — у головному циклі",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "pipeline.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F4 (proj) — Автомат дебаунсу: IDLE → MATCHING (лічимо однакові блоки) →
#   PRESSED (видали подію) → RELEASE (чекаємо тиші) → IDLE. Без тиші немає
#   повторного спрацювання — одна цифра не «дзвенить».
# ─────────────────────────────────────────────────────────────────────────────
def fig_debounce_fsm():
    W, H = 760, 380
    f = []
    f.append(text(W / 2, 26, "Автомат дебаунсу: підтвердження часом + вимога тиші",
                  size=15, bold=True))

    # чотири стани по колу
    states = {
        "IDLE":     (140, 150, "тиша / чекаємо тон"),
        "MATCHING": (430, 150, "той самий символ,\nлічимо до M"),
        "PRESSED":  (620, 280, "ВИДАЛИ подію\n(один раз)"),
        "RELEASE":  (300, 300, "чекаємо K блоків\nтиші"),
    }
    r = 52
    for name, (cx, cy, sub) in states.items():
        col = FIELD if name == "PRESSED" else NEG
        fillc = "#eafaf0" if name == "PRESSED" else "#f3f8ff"
        f.append(circle(cx, cy, r, fill=fillc, stroke=col, sw=2.0))
        f.append(text(cx, cy - 4, name, size=12, color=col, bold=True))
        f.append(mtext(cx, cy + 12, sub.split("\n"), size=9, color=MUTED))

    def edge(a, b, label, lcol=INK, curve=0, lx=None, ly=None):
        ax, ay, _ = states[a]
        bx, by, _ = states[b]
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        x1, y1 = ax + ux * r, ay + uy * r
        x2, y2 = bx - ux * r, by - uy * r
        out = arrow(x1, y1, x2, y2, color=lcol, sw=1.8)
        mx = lx if lx is not None else (x1 + x2) / 2
        my = ly if ly is not None else (y1 + y2) / 2
        return out, mx, my

    # IDLE → MATCHING: побачили валідний символ
    e, mx, my = edge("IDLE", "MATCHING", "")
    f.append(e)
    f.append(text((140 + 430) / 2, 138, "побачили валідний символ", size=10, color=INK, bold=True))

    # MATCHING → PRESSED: M блоків поспіль однакові
    e, mx, my = edge("MATCHING", "PRESSED", "")
    f.append(e)
    f.append(text(560, 205, "M однакових", size=10, color=FIELD, bold=True))
    f.append(text(560, 220, "поспіль", size=10, color=FIELD, bold=True))

    # PRESSED → RELEASE: символ зник / змінився
    e, mx, my = edge("PRESSED", "RELEASE", "")
    f.append(e)
    f.append(text(470, 305, "символ зник", size=10, color=INK))

    # RELEASE → IDLE: K блоків тиші
    e, mx, my = edge("RELEASE", "IDLE", "")
    f.append(e)
    f.append(text(205, 245, "K блоків тиші", size=10, color=POS, bold=True))

    # самопетля MATCHING (символ змінився → лічильник у нуль) — підпис
    f.append(text(430, 80, "(символ змінився → лічильник з нуля)", size=9, color=MUTED, italic=True))
    # самопетля PRESSED (символ той самий → нічого не видаємо)
    f.append(text(620, 358, "той самий символ → мовчимо", size=9, color=MUTED, italic=True))

    f.append(fitbox(40, 332, 360, 34,
                    "без стану RELEASE одна цифра видавала б подію щоблока — «дзвеніла» б повторами",
                    size=10, fill="#fdf6f5", stroke=POS, sw=1.3, color=INK))
    render(os.path.join(OUT, "debounce-fsm.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F5 (proj) — Скидання стану між блоками: якщо не обнулити (s1,s2), хвіст
#   попереднього блоку «протікає» в наступний і спотворює power.
# ─────────────────────────────────────────────────────────────────────────────
def fig_state_reset():
    W, H = 740, 300
    f = []
    f.append(text(W / 2, 26, "Скидання стану між блоками: чому обнуляти (s1, s2)",
                  size=15, bold=True))

    ox, oy = 60, 170
    axw = 620
    f.append(line(ox, oy, ox + axw, oy, color="#dcdcdc", sw=1.2))

    # три блоки по N відліків
    bw = axw / 3
    labels = ["блок 1: тон A", "блок 2: тиша", "блок 3: тон B"]
    for i in range(3):
        bx = ox + i * bw
        f.append(line(bx, oy - 60, bx, oy + 60, color="#bbbbbb", sw=1.0, dash="4,4"))
        f.append(text(bx + bw / 2, oy + 84, labels[i], size=10, color=INK, bold=True))
    f.append(line(ox + axw, oy - 60, ox + axw, oy + 60, color="#bbbbbb", sw=1.0, dash="4,4"))

    # ВЕРХ: без скидання — енергія блоку 1 «протікає» далі (спадний хвіст)
    f.append(text(ox - 6, oy - 70, "без скидання:", size=10, color=POS, anchor="start", bold=True))
    pts = []
    for i in range(0, int(axw) + 1, 4):
        x = ox + i
        # пилкоподібне накопичення в блоці 1, далі — повільне згасання-хвіст
        if i < bw:
            v = 30 * (i / bw)
        else:
            v = 30 * math.exp(-(i - bw) / (bw * 1.4))   # хвіст тягнеться у блоки 2,3
        pts.append("%.1f,%.1f" % (x, oy - 38 - v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), POS))
    f.append(text(ox + bw * 1.7, oy - 96, "хвіст блоку 1 бруднить блоки 2 і 3", size=9.5,
                  color=POS, italic=True))

    # НИЗ: зі скиданням — кожен блок чистий, починається з нуля
    f.append(text(ox - 6, oy + 116, "зі скиданням (g_init на межі):", size=10, color=FIELD,
                  anchor="start", bold=True))
    pts = []
    for i in range(0, int(axw) + 1, 4):
        x = ox + i
        seg = i % bw
        which = int(i // bw)
        peak = [30, 4, 26][min(which, 2)]   # блок2 — тиша (майже нуль)
        v = peak * (seg / bw)
        pts.append("%.1f,%.1f" % (x, oy + 60 - v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), FIELD))
    f.append(text(ox + axw / 2, oy + 100, "кожен блок міряє лише свій вміст", size=9.5,
                  color=FIELD, italic=True))

    render(os.path.join(OUT, "state-reset.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F6 (hist-touch-tone) — Чому частоти «кострубаті»: у кожній групі сусіди
#   розділені рівним МНОЖНИКОМ ≈1.105 (=21/19, геометрична прогресія), а
#   подвоєні частоти (гармоніки) кількох тонів лягають у проміжки — нікого
#   не імітують. Логарифмічна вісь → геометрична прогресія = рівні кроки.
# ─────────────────────────────────────────────────────────────────────────────
def fig_dtmf_spacing():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 24, "Чому частоти такі: рівний множник 1.105, гармоніки не влучають",
                  size=14, bold=True))

    lo = [697, 770, 852, 941]
    hi = [1209, 1336, 1477, 1633]

    fmin, fmax = 600.0, 3400.0           # вмістити й подвоєні частоти
    ox, axw = 60, 660
    base = math.log10(fmin)
    span = math.log10(fmax) - base

    def xf(fr):
        return ox + (math.log10(fr) - base) / span * axw

    y_lo, y_hi = 150, 232                 # рівні рисок двох груп
    y_axis = 300
    y_harm = 78                          # рівень дуг гармонік

    # вісь частоти (логарифмічна)
    f.append(arrow(ox, y_axis, ox + axw + 8, y_axis, color=INK, sw=1.4))
    f.append(text(ox + axw + 6, y_axis + 20, "частота (лог. шкала) →", size=10,
                  color=INK, anchor="end", bold=True))
    for fr in (700, 1000, 1500, 2000, 3000):
        x = xf(fr)
        f.append(line(x, y_axis, x, y_axis + 5, color=MUTED, sw=1.0))
        f.append(text(x, y_axis + 18, "%d" % fr, size=9, color=MUTED))

    def draw_group(freqs, y, col, label):
        f.append(text(ox, y - 16, label, size=10, color=col, anchor="start", bold=True))
        for fr in freqs:
            x = xf(fr)
            f.append(line(x, y, x, y_axis, color="#dce0e5", sw=1.0, dash="2,4"))
            f.append(line(x, y, x, y + 26, color=col, sw=7))
            f.append(text(x, y - 4, "%d" % fr, size=10, color=INK, bold=True))
        for i in range(len(freqs) - 1):
            xa, xb = xf(freqs[i]), xf(freqs[i + 1])
            yb = y + 40
            f.append(line(xa, y + 28, xa, yb, color=col, sw=1.0))
            f.append(line(xb, y + 28, xb, yb, color=col, sw=1.0))
            f.append(line(xa, yb, xb, yb, color=col, sw=1.0))
            f.append(text((xa + xb) / 2, yb + 11, "×1.105", size=9, color=col))

    draw_group(lo, y_lo, FIELD, "низька група")
    draw_group(hi, y_hi, NEG, "висока група")

    # гармоніки (×2) кількох низьких тонів — стрілка вгорі в порожнечу між частотами
    def harm(fr):
        x1, x2 = xf(fr), xf(2 * fr)
        f.append(line(x1, y_lo, x1, y_harm + 6, color=MUTED, sw=0.8, dash="1,3"))
        f.append(arrow(x1, y_harm + 6, x2, y_harm + 6, color=POS, sw=1.3))
        f.append(line(x2, y_harm + 6, x2, y_axis, color=POS, sw=0.8, dash="2,4"))
        f.append(text((x1 + x2) / 2, y_harm, "×2 → %d" % (2 * fr), size=9,
                      color=POS, bold=True))

    harm(697)    # 1394 — повз 1336 і 1477
    harm(852)    # 1704 — повз 1633
    f.append(text(W / 2, y_harm - 16,
                  "подвоєні частоти (гармоніки) лягають у проміжки — нікого не імітують",
                  size=10, color=POS, italic=True))

    f.append(text(W / 2, 348,
                  "рівний множник по всій шкалі → усі вісім розрізняються однаково добре",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "dtmf-spacing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dtmf_grid()
    fig_dtmf_detect()
    fig_pipeline()
    fig_debounce_fsm()
    fig_state_reset()
    fig_dtmf_spacing()
    print("Done — 6 SVG written to", OUT)
