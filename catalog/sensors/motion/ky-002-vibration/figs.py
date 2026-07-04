# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-002 — давач вібрації (SW-18020P)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Механізм SW-18020P: пружина в корпусі, ненапрямлений контакт ────────────
def fig_mechanism():
    W, H = 860, 430
    f = [text(W / 2, 28, "Усередині SW-18020P: пружина в провідному корпусі — контакт від струсу",
              size=15, bold=True)]

    # два стани поруч: спокій (ліворуч) і струс (праворуч)
    def cartridge(cx, cy, shaken, caption):
        # циліндричний корпус
        bw, bh = 150, 190
        f.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill="#eef2f6", stroke=MUTED, sw=2, rx=16))
        # верхній вивід (нерухома ніжка), припаяний до пружини
        top_y = cy - bh / 2 - 26
        f.append(line(cx, top_y, cx, cy - bh / 2 + 6, color=INK, sw=3))
        f.append(circle(cx, top_y, 5, fill=INK, stroke=INK))
        # нижній вивід — від корпусу
        bot_y = cy + bh / 2 + 26
        f.append(line(cx, cy + bh / 2 - 6, cx, bot_y, color=INK, sw=3))
        f.append(circle(cx, bot_y, 5, fill=INK, stroke=INK))
        # пружина: зигзаг усередині, у спокої рівна по центру, при струсі — вигнута до стінки
        n = 9
        y0 = cy - bh / 2 + 14
        y1 = cy + bh / 2 - 30
        step = (y1 - y0) / n
        amp = 15
        bend = 30 if shaken else 0            # зсув центру пружини вбік при струсі
        pts = []
        for k in range(n + 1):
            yy = y0 + k * step
            side = amp if k % 2 == 0 else -amp
            # плавний нахил осі пружини при струсі
            axis = bend * (k / n)
            pts.append((cx + axis + side, yy))
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        col = POS if shaken else NEG
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))
        f.append(text(cx, cy - bh / 2 - 40, "рухома пружина", size=11, bold=True, color=col))
        # підпис стінки-корпусу
        f.append(text(cx + bw / 2 + 4, cy - bh / 2 + 20, "провідний", size=9.5, color=MUTED, anchor="start"))
        f.append(text(cx + bw / 2 + 4, cy - bh / 2 + 34, "корпус", size=9.5, color=MUTED, anchor="start"))
        # позначка контакту при струсі
        if shaken:
            tip = pts[3]
            f.append(circle(cx + bw / 2 - 3, tip[1], 6, fill="#fdecea", stroke=POS, sw=2))
            f.append(text(cx, cy + bh / 2 + 48, "струс → пружина торкнулась стінки", size=11, bold=True, color=POS))
            f.append(text(cx, cy + bh / 2 + 64, "коло ЗАМКНЕНЕ (≈2 мс)", size=10.5, color=POS))
        else:
            f.append(text(cx, cy + bh / 2 + 48, "спокій: пружина не торкається", size=11, bold=True, color=NEG))
            f.append(text(cx, cy + bh / 2 + 64, "коло РОЗІМКНЕНЕ (>10 МΩ)", size=10.5, color=NEG))
        f.append(text(cx, cy + bh / 2 + 92, caption, size=11, color=INK))

    cartridge(230, 210, False, "стан «нема вібрації»")
    cartridge(630, 210, True, "стан «є вібрація»")

    # стрілка «струс у будь-який бік»
    f.append(arrow(410, 175, 460, 175, color=INK))
    f.append(text(435, 160, "струс", size=11, bold=True))
    return render(os.path.join(IMG, 'mechanism.svg'), W, H, *f)


# ── 2. Схема KY-002: пружинний ключ + 10к; ДВА варіанти доріжки ────────────────
def fig_schematic():
    W, H = 880, 470
    f = [text(W / 2, 28, "Схема KY-002: пружинний ключ SW-18020P + резистор 10 кΩ (два варіанти плати)",
              size=15, bold=True)]

    def variant(x0, title, pullup):
        # рамка варіанта
        f.append(rect(x0, 60, 360, 360, fill=BG, stroke=MUTED, sw=1.4, rx=12))
        f.append(text(x0 + 180, 84, title, size=13, bold=True,
                      color=(POS if pullup else FIELD)))

        vcc_y = 110
        gnd_y = 388
        railx = x0 + 300         # права шина живлення/землі
        node_x = x0 + 120        # вузол сигналу
        # рейки VCC та GND
        f.append(line(x0 + 40, vcc_y, railx, vcc_y, color=POS, sw=2))
        f.append(text(x0 + 30, vcc_y + 4, "+V", size=12, bold=True, color=POS, anchor="end"))
        f.append(line(x0 + 40, gnd_y, railx, gnd_y, color=INK, sw=2))
        f.append(text(x0 + 30, gnd_y + 4, "GND", size=12, bold=True, anchor="end"))

        # пружинний ключ (символ) — вертикально
        sw_top, sw_bot = 150, 250
        f.append(line(node_x, sw_top, node_x, sw_top + 14, color=INK, sw=2))
        f.append(line(node_x, sw_bot - 14, node_x, sw_bot, color=INK, sw=2))
        # контакти ключа
        f.append(circle(node_x, sw_top + 16, 3.5, fill=INK, stroke=INK))
        f.append(circle(node_x, sw_bot - 16, 3.5, fill=INK, stroke=INK))
        f.append('<path d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2"/>'
                 % (node_x, sw_top + 16, node_x + 22, sw_bot - 22, INK))  # похила «пелюстка» ключа
        f.append(text(node_x - 12, (sw_top + sw_bot) / 2, "SW-", size=10.5, bold=True, anchor="end"))
        f.append(text(node_x - 12, (sw_top + sw_bot) / 2 + 14, "18020P", size=10.5, bold=True, anchor="end"))

        # резистор 10к — прямокутник
        rx0 = node_x - 15
        if pullup:
            # ключ між node і GND; резистор між node і +V (підтяжка вгору)
            f.append(line(node_x, sw_top, node_x, 130, color=INK, sw=2))     # node вгору до резистора
            # резистор вертикально від node(130) до VCC
            f.append(rect(rx0, 116, 30, 14, fill=FILL, stroke=INK, sw=1.6, rx=3))
            f.append(line(node_x, 116, node_x, vcc_y, color=INK, sw=2))
            f.append(text(rx0 - 6, 128, "10к", size=10.5, bold=True, anchor="end"))
            # ключ униз до GND
            f.append(line(node_x, sw_bot, node_x, gnd_y, color=INK, sw=2))
            idle = "спокій: S ≈ +V (ВИСОКО)"
            act = "струс: ключ тягне S до GND (НИЗЬКО)"
            idle_c, act_c = POS, NEG
        else:
            # резистор між node і GND (підтяжка вниз); ключ між node і +V
            f.append(line(node_x, sw_bot, node_x, 300, color=INK, sw=2))
            f.append(rect(rx0, 300, 30, 14, fill=FILL, stroke=INK, sw=1.6, rx=3))
            f.append(line(node_x, 314, node_x, gnd_y, color=INK, sw=2))
            f.append(text(rx0 - 6, 312, "10к", size=10.5, bold=True, anchor="end"))
            # ключ угору до VCC
            f.append(line(node_x, sw_top, node_x, vcc_y, color=INK, sw=2))
            idle = "спокій: S ≈ GND (НИЗЬКО)"
            act = "струс: ключ тягне S до +V (ВИСОКО)"
            idle_c, act_c = NEG, POS

        # вивід сигналу S — вбік від вузла
        node_y = (sw_top + sw_bot) / 2
        f.append(line(node_x, node_y, x0 + 40, node_y, color=FIELD, sw=2.2))
        f.append(circle(node_x, node_y, 4, fill=FIELD, stroke=FIELD))
        f.append(text(x0 + 30, node_y + 4, "S", size=12, bold=True, color=FIELD, anchor="end"))

        # підписи поведінки — унизу рамки, кожен у своєму рядку з запасом
        f.append(text(x0 + 180, 356, idle, size=10.5, bold=True, color=idle_c))
        f.append(text(x0 + 180, 374, act, size=10.5, bold=True, color=act_c))

    variant(40, "варіант A — підтяжка вгору (pull-up)", True)
    variant(480, "варіант B — підтяжка вниз (pull-down)", False)
    return render(os.path.join(IMG, 'schematic.svg'), W, H, *f)


# ── 3. Підключення KY-002 до МК трьома дротами ────────────────────────────────
def fig_wiring():
    W, H = 820, 380
    f = [text(W / 2, 28, "Підключення KY-002: три дроти до мікроконтролера", size=15, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 90, 90, 190, 190
    f.append(rect(mx, my, mw, mh, fill="#eaf1fb", stroke=NEG, sw=2, rx=12))
    f.append(text(mx + mw / 2, my + 26, "KY-002", size=14, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 46, "(SW-18020P)", size=10.5, color=MUTED))
    # три штирі праворуч на модулі
    pins = [("S", my + 95, FIELD), ("+", my + 135, POS), ("−", my + 175, INK)]
    for lbl, py, col in pins:
        f.append(circle(mx + mw, py, 6, fill=col, stroke=col))
        f.append(text(mx + mw - 16, py + 4, lbl, size=13, bold=True, color=col, anchor="end"))

    # МК праворуч
    kx, ky, kw, kh = 560, 90, 180, 200
    f.append(rect(kx, ky, kw, kh, fill="#f4f6f8", stroke=INK, sw=2, rx=12))
    f.append(text(kx + kw / 2, ky + 26, "мікроконтролер", size=12.5, bold=True))
    f.append(text(kx + kw / 2, ky + 44, "(Arduino / ESP32)", size=10, color=MUTED))
    targets = [("D2  вхід", ky + 95, FIELD), ("5V / 3V3", ky + 135, POS), ("GND", ky + 175, INK)]
    for lbl, py, col in targets:
        f.append(circle(kx, py, 6, fill=col, stroke=col))
        f.append(text(kx + 16, py + 4, lbl, size=11.5, bold=True, color=col, anchor="start"))

    # три дроти
    for (l1, py1, c1), (l2, py2, c2) in zip(pins, targets):
        midx = (mx + mw + kx) / 2
        f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (mx + mw + 6, py1, midx, py1, midx, py2, kx - 6, py2, c1))

    # примітка про підтяжку
    note, nw, nh = textbox(W / 2, 330, "S → цифровий вхід; увімкни внутрішню підтяжку (INPUT_PULLUP),\n"
                                       "якщо на платі підтяжки немає — інакше вхід «висітиме»",
                           size=11, fill="#fff8e6", stroke="#e0b400", pad=10)
    f.append(note)
    return render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── 4. Опитування vs переривання: чому повільний digitalRead губить контакт ───
def fig_poll_vs_int():
    W, H = 900, 470
    f = [text(W / 2, 28, "Опитування vs переривання: контакт живе ~2 мс", size=15, bold=True)]

    x0, x1 = 90, 830          # межі осі часу
    span_ms = 60.0            # уся вісь — 60 мс
    def X(t): return x0 + (x1 - x0) * t / span_ms

    # три коротких імпульси контакту (кожен ~2 мс) у моменти струсу
    pulses = [(8, 2), (9.5, 1.6), (30, 2)]   # (початок мс, тривалість мс)

    # ── доріжка 1: сигнал на нозі S ──
    sy = 90
    f.append(text(x0 - 12, sy + 4, "S на нозі", size=11, bold=True, anchor="end"))
    base = sy + 26
    top = sy - 4
    f.append(line(x0, base, x1, base, color=MUTED, sw=1.4))          # рівень спокою
    for (t, d) in pulses:
        xa, xb = X(t), X(t + d)
        f.append(line(xa, base, xa, top, color=POS, sw=2))
        f.append(line(xa, top, xb, top, color=POS, sw=2))
        f.append(line(xb, top, xb, base, color=POS, sw=2))
    f.append(text(X(8) + 6, top - 6, "струс → контакт замкнувся (~2 мс)", size=10, color=POS, anchor="start"))
    f.append(text(X(30) + 6, top - 6, "новий струс", size=10, color=POS, anchor="start"))

    # ── доріжка 2: повільне опитування раз на 20 мс ──
    py = 200
    f.append(mtext(x0 - 12, py, ["опитування", "раз на 20 мс"], size=10.5, anchor="end", bold=True))
    f.append(line(x0, py + 40, x1, py + 40, color=MUTED, sw=1.2, dash="2,4"))
    hit_any = False
    for t in range(0, int(span_ms) + 1, 20):
        xt = X(t)
        # чи потрапляє мить опитування в якийсь імпульс?
        inside = any(t >= s and t <= s + d for (s, d) in pulses)
        col = FIELD if inside else INK
        f.append(line(xt, py + 8, xt, py + 40, color=col, sw=2))
        f.append(circle(xt, py + 8, 4, fill=(FIELD if inside else BG), stroke=col, sw=2))
        f.append(text(xt, py + 56, ("влучив" if inside else "мимо"), size=9.5,
                      color=col, bold=inside, anchor="middle"))
        hit_any = hit_any or inside
    f.append(text(x1, py - 2, "усі три струси проґавлено", size=10.5, bold=True, color=POS, anchor="end"))

    # ── доріжка 3: переривання по фронту ──
    iy = 330
    f.append(mtext(x0 - 12, iy, ["переривання", "по фронту"], size=10.5, anchor="end", bold=True))
    f.append(line(x0, iy + 30, x1, iy + 30, color=MUTED, sw=1.2, dash="2,4"))
    for (t, d) in pulses:
        xt = X(t)
        f.append(arrow(xt, iy + 30, xt, iy + 4, color=FIELD, sw=2.2))
        f.append(circle(xt, iy + 30, 4, fill=FIELD, stroke=FIELD))
    f.append(text(X(8), iy - 6, "ISR", size=10, bold=True, color=FIELD, anchor="middle"))
    f.append(text(X(9.5), iy - 6, "ISR", size=10, bold=True, color=FIELD, anchor="middle"))
    f.append(text(X(30), iy - 6, "ISR", size=10, bold=True, color=FIELD, anchor="middle"))
    f.append(text(x1, iy - 2, "залізо зловило кожен фронт", size=10.5, bold=True, color=FIELD, anchor="end"))

    # шкала часу
    ax = 420
    f.append(line(x0, ax, x1, ax, color=INK, sw=1.4))
    for t in range(0, int(span_ms) + 1, 10):
        xt = X(t)
        f.append(line(xt, ax - 4, xt, ax + 4, color=INK, sw=1.2))
        f.append(text(xt, ax + 18, "%d" % t, size=9.5, color=MUTED))
    f.append(text(x1 + 4, ax + 18, "мс", size=9.5, color=MUTED, anchor="start"))
    return render(os.path.join(IMG, 'poll-vs-int.svg'), W, H, *f)


# ── 5. Брязкіт → вікно придушення: один струс, багато імпульсів ────────────────
def fig_debounce_window():
    W, H = 900, 400
    f = [text(W / 2, 28, "Один струс дає чергу імпульсів — вікно придушення злічує його як ОДИН",
              size=14.5, bold=True)]

    x0, x1 = 80, 840
    span = 420.0
    def X(t): return x0 + (x1 - x0) * t / span

    # черга дотиків від ОДНОГО струсу (торохтіння пружини), тоді тиша, тоді другий струс
    burst1 = [(20, 3), (28, 2), (34, 2.5), (41, 2), (52, 3), (66, 2)]     # один струс
    burst2 = [(240, 3), (248, 2), (255, 2.5)]                              # другий струс

    # доріжка сигналу
    sy = 96
    base = sy + 30
    top = sy - 2
    f.append(text(x0 - 10, sy + 6, "S", size=12, bold=True, anchor="end"))
    f.append(line(x0, base, x1, base, color=MUTED, sw=1.3))
    for (t, d) in burst1 + burst2:
        xa, xb = X(t), X(t + d)
        f.append(line(xa, base, xa, top, color=POS, sw=1.8))
        f.append(line(xa, top, xb, top, color=POS, sw=1.8))
        f.append(line(xb, top, xb, base, color=POS, sw=1.8))

    # дужки над двома струсами
    def brace(ta, tb, label, col):
        xa, xb = X(ta), X(tb)
        yb = sy - 18
        f.append(line(xa, yb, xb, yb, color=col, sw=1.6))
        f.append(line(xa, yb, xa, yb + 8, color=col, sw=1.6))
        f.append(line(xb, yb, xb, yb + 8, color=col, sw=1.6))
        f.append(text((xa + xb) / 2, yb - 6, label, size=10.5, bold=True, color=col))
    brace(20, 68, "ОДИН струс (пружина торохтить)", INK)
    brace(250, 268, "другий струс", INK)

    # доріжка «наївний лічильник» — рахує кожен фронт
    ny = 200
    f.append(mtext(x0 - 10, ny, ["наївний", "лічильник"], size=10, anchor="end", bold=True))
    n = 0
    for (t, d) in burst1 + burst2:
        n += 1
        xt = X(t)
        f.append(arrow(xt, ny + 24, xt, ny + 2, color=POS, sw=1.8))
        f.append(text(xt, ny + 38, "%d" % n, size=9.5, color=POS, bold=True))
    f.append(text(x1, ny - 4, "9 спрацювань на 2 струси — БРЕХНЯ", size=10.5, bold=True, color=POS, anchor="end"))

    # доріжка «вікно придушення» — після першого фронту глухнемо на LOCKOUT
    wy = 300
    lock = 120.0    # вікно придушення, мс
    f.append(mtext(x0 - 10, wy, ["вікно", "придушення"], size=10, anchor="end", bold=True))
    # перший струс: зараховуємо перший фронт burst1, тоді сіре вікно
    for (start, brs, idx) in [(20, burst1, 1), (240, burst2, 2)]:
        xa = X(start)
        xe = min(X(start + lock), x1)      # не вилазити за праву межу осі
        # сіра «глуха» смуга
        f.append(rect(xa, wy - 6, xe - xa, 30, fill="#eef0f2", stroke=MUTED, sw=1, rx=4))
        f.append(arrow(xa, wy + 24, xa, wy + 2, color=FIELD, sw=2.4))
        f.append(text(xa, wy - 12, "струс #%d" % idx, size=10, bold=True, color=FIELD, anchor="middle"))
        f.append(text((xa + xe) / 2, wy + 16, "глухі %d мс" % int(lock), size=9, color=MUTED))
    f.append(text(x1, wy - 4, "2 струси = 2 події — ПРАВДА", size=10.5, bold=True, color=FIELD, anchor="end"))

    # шкала часу
    ax = 366
    f.append(line(x0, ax, x1, ax, color=INK, sw=1.3))
    for t in range(0, int(span) + 1, 50):
        xt = X(t)
        f.append(line(xt, ax - 4, xt, ax + 4, color=INK, sw=1.1))
        f.append(text(xt, ax + 17, "%d" % t, size=9, color=MUTED))
    f.append(text(x1 + 4, ax + 17, "мс", size=9, color=MUTED, anchor="start"))
    return render(os.path.join(IMG, 'debounce-window.svg'), W, H, *f)


# ── 6. Сила струсу за кількістю імпульсів у вікні ─────────────────────────────
def fig_strength_buckets():
    W, H = 880, 430
    f = [text(W / 2, 28, "«Сила» струсу — скільки імпульсів набіглo за вікно вимірювання",
              size=14.5, bold=True)]

    # три вікна однакової тривалості з різною щільністю імпульсів
    win_w = 230
    gap = 30
    x_start = 55
    win_y = 70
    win_h = 210
    labels = [
        ("легкий дотик", 3, FIELD),
        ("помітний струс", 9, "#e08a1e"),
        ("сильний удар", 22, POS),
    ]
    import random
    random.seed(7)
    for i, (name, cnt, col) in enumerate(labels):
        wx = x_start + i * (win_w + gap)
        # рамка вікна
        f.append(rect(wx, win_y, win_w, win_h, fill=BG, stroke=MUTED, sw=1.4, rx=8))
        f.append(text(wx + win_w / 2, win_y - 10, name, size=12, bold=True, color=col))
        # базова лінія імпульсів
        baseY = win_y + win_h - 30
        f.append(line(wx + 12, baseY, wx + win_w - 12, baseY, color=MUTED, sw=1.2))
        # рівномірно, але з дрібним джиттером розкидані імпульси
        inner = win_w - 40
        for k in range(cnt):
            frac = (k + 0.5) / cnt
            px = wx + 20 + inner * frac + random.uniform(-3, 3)
            f.append(line(px, baseY, px, baseY - 70, color=col, sw=1.8))
        # підпис кількості й вердикт
        f.append(text(wx + win_w / 2, baseY + 22, "імпульсів за вікно: %d" % cnt,
                      size=11, bold=True, color=INK))

    # спільна вісь-«вікно вимірювання» під усіма трьома
    ax = win_y + win_h + 60
    f.append(text(W / 2, ax - 8, "однакове вікно вимірювання (напр. 100 мс) для всіх трьох", size=11, color=MUTED))

    # поріг «сильний струс»
    thr_y = ax + 28
    f.append(rect(55, thr_y, W - 110, 46, fill="#fdf4f4", stroke=POS, sw=1.4, rx=8))
    f.append(mtext(W / 2, thr_y + 18,
                   ["поріг «сильний струс»: якщо імпульсів за вікно ≥ N (напр. 12) — вважаємо удар сильним",
                    "менше — легкий; так із голого «замкнено/розімкнено» дістаємо грубу шкалу сили"],
                   size=10.5, color=INK))
    return render(os.path.join(IMG, 'strength-buckets.svg'), W, H, *f)


if __name__ == "__main__":
    for fn in (fig_mechanism, fig_schematic, fig_wiring,
               fig_poll_vs_int, fig_debounce_window, fig_strength_buckets):
        p = fn()
        print("wrote", p)
