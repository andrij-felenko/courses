# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-031 — давач стуку».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Механізм: котушка-пружина навколо осьового стрижня ──────────────────────
def fig_mechanism():
    W, H = 900, 470
    f = [text(W / 2, 30, "Усередині KY-031: котушка-пружина навколо осьового стрижня",
              size=16, bold=True)]

    def cell(cx, cy, knocked, caption, cap_c):
        # прозорий корпус-циліндр
        bw, bh = 170, 210
        f.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill="#eef2f6", stroke=MUTED, sw=2, rx=18))
        # осьовий стрижень (центральний вивід) — нерухома вертикаль по осі
        post_top = cy - bh / 2 + 22
        post_bot = cy + bh / 2 - 22
        f.append(line(cx, post_top, cx, post_bot, color=INK, sw=3.5))
        # нижній вивід — від стрижня вниз
        f.append(line(cx, post_bot, cx, cy + bh / 2 + 30, color=INK, sw=3))
        f.append(circle(cx, cy + bh / 2 + 30, 5, fill=INK, stroke=INK))
        # верхній вивід — від котушки вгору (пружина припаяна зверху збоку)
        coil_anchor_x = cx - 46
        f.append(line(coil_anchor_x, post_top - 8, coil_anchor_x, cy - bh / 2 - 30, color=INK, sw=3))
        f.append(circle(coil_anchor_x, cy - bh / 2 - 30, 5, fill=INK, stroke=INK))
        # котушка-пружина: витки як горизонтальні овали навколо осі; у спокої симетрична,
        # від стуку вся котушка хитнулась убік і торкнулась стрижня
        n = 7
        y0 = post_top + 6
        y1 = post_bot - 10
        step = (y1 - y0) / n
        lean = 30 if knocked else 0          # нахил осі котушки при стуку
        col = POS if knocked else NEG
        ring_w = 52
        for k in range(n + 1):
            yy = y0 + k * step
            off = lean * (k / n)             # чим нижче — тим сильніший зсув
            rcx = coil_anchor_x + off
            # напівовал-виток
            f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="7" fill="none" '
                     'stroke="%s" stroke-width="2.2"/>' % (rcx + ring_w / 2, yy, ring_w / 2, col))
        f.append(text(cx - bw / 2 - 8, cy - bh / 2 - 32, "котушка-", size=10.5, bold=True, color=col, anchor="start"))
        f.append(text(cx - bw / 2 - 8, cy - bh / 2 - 18, "пружина", size=10.5, bold=True, color=col, anchor="start"))
        # підпис осьового стрижня
        f.append(text(cx + bw / 2 + 10, cy - 6, "осьовий", size=10, color=MUTED, anchor="start"))
        f.append(text(cx + bw / 2 + 10, cy + 8, "стрижень", size=10, color=MUTED, anchor="start"))
        # позначка контакту при стуку
        if knocked:
            f.append(circle(cx, y1 - 6, 7, fill="#fdecea", stroke=POS, sw=2.4))
            f.append(text(cx, cy + bh / 2 + 58, "стук: котушка торкнулась стрижня", size=11.5, bold=True, color=POS))
            f.append(text(cx, cy + bh / 2 + 76, "коло ЗАМКНЕНЕ (кілька мс)", size=10.5, color=POS))
        else:
            f.append(text(cx, cy + bh / 2 + 58, "спокій: зазор навколо стрижня", size=11.5, bold=True, color=NEG))
            f.append(text(cx, cy + bh / 2 + 76, "коло РОЗІМКНЕНЕ", size=10.5, color=NEG))
        f.append(text(cx, cy + bh / 2 + 104, caption, size=11.5, color=cap_c, bold=True))

    cell(245, 220, False, "стан «нема удару»", NEG)
    cell(655, 220, True, "стан «удар»", POS)

    # стрілка-стук між станами
    f.append(arrow(430, 150, 470, 150, color=INK))
    f.append(text(450, 134, "стук", size=11.5, bold=True))
    return render(os.path.join(IMG, 'mechanism.svg'), W, H, *f)


# ── 2. Схема KY-031: пружинний ключ + 10к; читання з внутрішньою підтяжкою ─────
def fig_schematic():
    W, H = 760, 460
    f = [text(W / 2, 30, "Схема KY-031: пружинний ключ + резистор 10 кΩ", size=16, bold=True)]

    # рамка модуля
    bx, by, bw, bh = 90, 70, 380, 330
    f.append(rect(bx, by, bw, bh, fill=BG, stroke=MUTED, sw=1.6, rx=14))
    f.append(text(bx + bw / 2, by + 26, "плата KY-031", size=13, bold=True, color=NEG))

    vcc_y = by + 70
    gnd_y = by + 285
    node_x = bx + 150          # вузол сигналу
    railx = bx + 320
    # рейки
    f.append(line(bx + 40, vcc_y, railx, vcc_y, color=POS, sw=2.2))
    f.append(text(bx + 30, vcc_y + 4, "+V", size=12.5, bold=True, color=POS, anchor="end"))
    f.append(line(bx + 40, gnd_y, railx, gnd_y, color=INK, sw=2.2))
    f.append(text(bx + 30, gnd_y + 4, "GND", size=12.5, bold=True, anchor="end"))

    # пружинний ключ між вузлом і GND (символ)
    sw_top, sw_bot = vcc_y + 40, gnd_y - 40
    f.append(line(node_x, sw_top, node_x, sw_top + 16, color=INK, sw=2))
    f.append(circle(node_x, sw_top + 18, 4, fill=INK, stroke=INK))
    f.append(circle(node_x, sw_bot - 18, 4, fill=INK, stroke=INK))
    f.append('<path d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2.4"/>'
             % (node_x, sw_top + 18, node_x + 26, sw_bot - 26, INK))       # похила пелюстка
    f.append(line(node_x, sw_bot - 16, node_x, sw_bot, color=INK, sw=2))
    f.append(line(node_x, sw_bot, node_x, gnd_y, color=INK, sw=2))
    f.append(text(node_x - 14, (sw_top + sw_bot) / 2 - 4, "пружинний", size=10.5, bold=True, anchor="end"))
    f.append(text(node_x - 14, (sw_top + sw_bot) / 2 + 12, "ключ", size=10.5, bold=True, anchor="end"))

    # послідовний резистор 10к від вузла до штиря S (обмежувач струму)
    node_y = (sw_top + sw_bot) / 2
    f.append(line(node_x, node_y, node_x + 40, node_y, color=FIELD, sw=2.2))
    f.append(rect(node_x + 40, node_y - 9, 34, 18, fill=FILL, stroke=INK, sw=1.6, rx=3))
    f.append(text(node_x + 57, node_y - 16, "10к", size=10.5, bold=True))
    f.append(line(node_x + 74, node_y, bx + 40, node_y, color=FIELD, sw=2.2))
    f.append(circle(node_x, node_y, 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(bx + 30, node_y + 4, "S", size=12.5, bold=True, color=FIELD, anchor="end"))

    # МК праворуч із внутрішньою підтяжкою
    mx, my, mw, mh = 540, 120, 170, 230
    f.append(rect(mx, my, mw, mh, fill="#f4f6f8", stroke=INK, sw=1.8, rx=12))
    f.append(text(mx + mw / 2, my + 24, "мікроконтролер", size=11.5, bold=True))
    # внутрішня підтяжка вгору всередині МК
    f.append(line(mx + mw / 2, my + 40, mx + mw / 2, my + 58, color=POS, sw=2))
    f.append(rect(mx + mw / 2 - 15, my + 58, 30, 16, fill=FILL, stroke=POS, sw=1.6, rx=3))
    f.append(text(mx + mw / 2 + 40, my + 70, "внутр.", size=9.5, color=POS, anchor="middle"))
    f.append(text(mx + mw / 2 + 40, my + 84, "підтяжка", size=9.5, color=POS, anchor="middle"))
    f.append(line(mx + mw / 2, my + 74, mx + mw / 2, my + 150, color=INK, sw=2))
    f.append(circle(mx + mw / 2, my + 150, 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(mx + mw / 2, my + 174, "вхід D", size=11, bold=True, color=FIELD))
    # дріт S → вхід
    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="2.4"/>'
             % (bx + 40, node_y, (bx + mx) / 2, node_y, (bx + mx) / 2, my + 150, mx + mw / 2, my + 150, FIELD))

    # підпис поведінки — унизу, з запасом
    f.append(text(W / 2, by + bh + 30, "спокій: підтяжка тримає вхід ВИСОКО  ·  удар: ключ садить його на GND (НИЗЬКО)",
                  size=11.5, bold=True, color=INK))
    return render(os.path.join(IMG, 'schematic.svg'), W, H, *f)


# ── 3. Підключення KY-031 до МК трьома дротами ────────────────────────────────
def fig_wiring():
    W, H = 840, 380
    f = [text(W / 2, 30, "Підключення KY-031: три дроти до мікроконтролера", size=16, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 100, 90, 195, 195
    f.append(rect(mx, my, mw, mh, fill="#eaf1fb", stroke=NEG, sw=2, rx=12))
    f.append(text(mx + mw / 2, my + 30, "KY-031", size=15, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 50, "давач стуку", size=10.5, color=MUTED))
    pins = [("S", my + 100, FIELD), ("+", my + 140, POS), ("−", my + 180, INK)]
    for lbl, py, col in pins:
        f.append(circle(mx + mw, py, 6.5, fill=col, stroke=col))
        f.append(text(mx + mw - 18, py + 4, lbl, size=13, bold=True, color=col, anchor="end"))

    # МК праворуч
    kx, ky, kw, kh = 575, 90, 190, 205
    f.append(rect(kx, ky, kw, kh, fill="#f4f6f8", stroke=INK, sw=2, rx=12))
    f.append(text(kx + kw / 2, ky + 28, "мікроконтролер", size=12.5, bold=True))
    f.append(text(kx + kw / 2, ky + 46, "(Arduino / ESP32)", size=10, color=MUTED))
    targets = [("D2  вхід", ky + 100, FIELD), ("5V / 3V3", ky + 140, POS), ("GND", ky + 180, INK)]
    for lbl, py, col in targets:
        f.append(circle(kx, py, 6.5, fill=col, stroke=col))
        f.append(text(kx + 18, py + 4, lbl, size=11.5, bold=True, color=col, anchor="start"))

    # три дроти
    for (l1, py1, c1), (l2, py2, c2) in zip(pins, targets):
        midx = (mx + mw + kx) / 2
        f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (mx + mw + 6, py1, midx, py1, midx, py2, kx - 6, py2, c1))

    # примітка про підтяжку
    note, nw, nh = textbox(W / 2, 335, "S → цифровий вхід; вмикай внутрішню підтяжку (INPUT_PULLUP):\n"
                                       "спокій = ВИСОКО, удар = короткий НИЗЬКО. Середній штир — завжди живлення",
                           size=11, fill="#fff8e6", stroke="#e0b400", pad=10)
    f.append(note)
    return render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── 4. Поріг чутливості: KY-031 (стук) проти KY-002 (вібрація) ─────────────────
def fig_sensitivity():
    W, H = 880, 430
    f = [text(W / 2, 30, "Поріг спрацювання: KY-031 глухіший — реагує лише на добрий удар",
              size=15, bold=True)]

    x0, x1 = 90, 830
    base = 250                  # вісь сили впливу (амплітуда струсу)
    # шкала сили впливу
    f.append(line(x0, base, x1, base, color=INK, sw=1.6))
    f.append(text(x1 + 4, base + 20, "сила", size=10, color=MUTED, anchor="start"))
    for i, name in enumerate(["дотик", "легкий\nструс", "тряска", "постук\nпальцем", "твердий\nстук", "удар"]):
        xt = x0 + (x1 - x0) * (i + 0.5) / 6
        f.append(line(xt, base - 5, xt, base + 5, color=MUTED, sw=1.2))
        f.append(mtext(xt, base + 22, name, size=9.5, color=MUTED))

    # порогові лінії двох давачів
    ky002_x = x0 + (x1 - x0) * 1.15 / 6      # KY-002 спрацьовує рано
    ky031_x = x0 + (x1 - x0) * 3.9 / 6       # KY-031 — пізно
    # KY-002 поріг (низький)
    f.append(line(ky002_x, base - 150, ky002_x, base + 5, color=FIELD, sw=2.2, dash="6,4"))
    f.append(text(ky002_x, base - 158, "поріг KY-002", size=11, bold=True, color=FIELD))
    f.append(text(ky002_x, base - 142, "(вібрація)", size=9.5, color=FIELD))
    # зона, де спрацьовує KY-002
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" '
             'fill-opacity="0.08"/>' % (ky002_x, base - 150, x1 - ky002_x, 150))
    # KY-031 поріг (високий)
    f.append(line(ky031_x, base - 190, ky031_x, base + 5, color=POS, sw=2.4, dash="6,4"))
    f.append(text(ky031_x, base - 198, "поріг KY-031", size=11, bold=True, color=POS))
    f.append(text(ky031_x, base - 182, "(стук)", size=9.5, color=POS))
    # зона, де спрацьовує KY-031
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c0392b" '
             'fill-opacity="0.10"/>' % (ky031_x, base - 190, x1 - ky031_x, 190))

    # підписи зон
    f.append(text((ky002_x + ky031_x) / 2, base - 70, "KY-002 вже кричить,", size=10.5, bold=True, color=FIELD))
    f.append(text((ky002_x + ky031_x) / 2, base - 54, "KY-031 ще мовчить", size=10.5, bold=True, color=POS))
    f.append(text((ky031_x + x1) / 2, base - 110, "тут спрацьовують", size=10.5, bold=True, color=INK))
    f.append(text((ky031_x + x1) / 2, base - 94, "обидва", size=10.5, bold=True, color=INK))

    # висновок унизу
    concl, cw, ch = textbox(W / 2, base + 110,
                            "Жорсткіша пружина KY-031 не хитається від дрібниць — тому він майже не ловить\n"
                            "фонову вібрацію й випадкові дотики, зате чисто відгукується на навмисний стук.",
                            size=11, fill="#f0f6ff", stroke=NEG, pad=12)
    f.append(concl)
    return render(os.path.join(IMG, 'sensitivity.svg'), W, H, *f)


if __name__ == "__main__":
    for fn in (fig_mechanism, fig_schematic, fig_wiring, fig_sensitivity):
        p = fn()
        print("wrote", p)
