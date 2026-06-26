# -*- coding: utf-8 -*-
"""Фігури до теми «Віконний компаратор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def opamp_tri(cx, cy, w=84, h=86, plus_top=True):
    """Трикутник компаратора вістрям праворуч. Вхідні вузли — на лівій грані,
    вихід — на вістрі. plus_top=True → «+» зверху. Повертає (svg, in_top, in_bot, out)."""
    left = cx - w / 2
    tipx = cx + w / 2
    top, bot = cy - h / 2, cy + h / 2
    body = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" '
            'fill="#fbfbfb" stroke="%s" stroke-width="1.8"/>'
            % (left, top, left, bot, tipx, cy, INK))
    in_top = (left, cy - h / 4)
    in_bot = (left, cy + h / 4)
    s_top = ("+", POS) if plus_top else ("−", NEG)
    s_bot = ("−", NEG) if plus_top else ("+", POS)
    body += text(left + 13, in_top[1] + 5, s_top[0], size=15, color=s_top[1], bold=True)
    body += text(left + 13, in_bot[1] + 5, s_bot[0], size=14, color=s_bot[1], bold=True)
    return body, in_top, in_bot, (tipx, cy)


def ground(x, y):
    return (line(x - 13, y, x + 13, y, color=INK, sw=2) +
            line(x - 8, y + 5, x + 8, y + 5, color=INK, sw=1.6) +
            line(x - 4, y + 10, x + 4, y + 10, color=INK, sw=1.3))


def npn(cx, cy):
    """Маленький NPN-символ у колі: база ліворуч, колектор угору, емітер униз."""
    out = [circle(cx, cy, 20, fill="#fff", stroke=INK, sw=1.6)]
    out.append(line(cx - 5, cy - 11, cx - 5, cy + 11, color=INK, sw=2.4))    # база-планка
    out.append(line(cx - 16, cy, cx - 5, cy, color=INK, sw=1.6))             # вивід бази
    out.append(line(cx - 5, cy - 5, cx + 11, cy - 14, color=INK, sw=1.6))    # до колектора
    out.append(line(cx - 5, cy + 5, cx + 11, cy + 14, color=INK, sw=1.6))    # до емітера
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
               % (cx + 3, cy + 8, cx + 11, cy + 14, cx + 1, cy + 14, INK))
    return "".join(out)


# ══ 1. Ідея вікна: два компаратори + три зони ════════════════════════════════
def fig_window_idea():
    W, H = 720, 470
    f = [text(W / 2, 28, "Два компаратори стережуть два краї однієї смуги",
              size=16, bold=True)]

    # сигнал-вузол, від якого гілка вгору й униз
    sig_x = 90
    up_y, dn_y = 150, 320
    f.append(line(sig_x, up_y, sig_x, dn_y, color=POS, sw=2.4))
    f.append(circle(sig_x, (up_y + dn_y) / 2, 3.5, fill=POS, stroke=POS, sw=1))
    f.append(line(sig_x - 36, (up_y + dn_y) / 2, sig_x, (up_y + dn_y) / 2, color=POS, sw=2.4))
    f.append(text(sig_x - 40, (up_y + dn_y) / 2 - 8, "Vвх", size=13, color=POS, bold=True, anchor="end"))

    # ── верхній компаратор: «+»=V_в, «−»=Vвх  → «1», поки Vвх < V_в ──
    tri_u, it_u, ib_u, out_u = opamp_tri(250, up_y, plus_top=True)
    f.append(tri_u)
    f.append(line(sig_x, up_y, sig_x, ib_u[1], color=POS, sw=2))   # сигнал → «−» (нижній)
    f.append(line(sig_x, ib_u[1], it_u[0], ib_u[1], color=POS, sw=2))
    f.append(line(it_u[0], it_u[1], 165, it_u[1], color=NEG, sw=2))   # V_в → «+» (верхній)
    f.append(text(160, it_u[1] + 4, "V_в", size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(250, up_y - 56, "верхній компаратор", size=11, color=MUTED, bold=True))
    f.append(text(250, up_y + 60, "«1», поки Vвх < V_в", size=11, color=MUTED))
    f.append(line(out_u[0], out_u[1], 360, out_u[1], color=INK, sw=2))

    # ── нижній компаратор: «+»=Vвх, «−»=V_н  → «1», поки Vвх > V_н ──
    tri_d, it_d, ib_d, out_d = opamp_tri(250, dn_y, plus_top=True)
    f.append(tri_d)
    f.append(line(sig_x, dn_y, it_d[0], it_d[1], color=POS, sw=2))    # сигнал → «+» (верхній)
    f.append(line(it_d[0], ib_d[1], 165, ib_d[1], color=NEG, sw=2))   # V_н → «−» (нижній)
    f.append(text(160, ib_d[1] + 4, "V_н", size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(250, dn_y - 56, "нижній компаратор", size=11, color=MUTED, bold=True))
    f.append(text(250, dn_y + 60, "«1», поки Vвх > V_н", size=11, color=MUTED))
    f.append(line(out_d[0], out_d[1], 360, out_d[1], color=INK, sw=2))

    # ── таблиця трьох зон ──
    bx, by, bw = 400, 110, 286
    f.append(rect(bx, by, bw, 250, fill="#fbfbfb", stroke="#c9d3dc", sw=1.3, rx=10))
    f.append(text(bx + bw / 2, by + 26, "що кажуть два виходи", size=12, bold=True))
    rows = [
        ("Vвх < V_н", "нижній 0   верхній 1", "за вікном", MUTED),
        ("V_н < Vвх < V_в", "нижній 1   верхній 1", "У ВІКНІ", FIELD),
        ("Vвх > V_в", "нижній 1   верхній 0", "за вікном", MUTED),
    ]
    ry = by + 58
    for cond, outs, verdict, col in rows:
        hl = (col == FIELD)
        if hl:
            f.append(rect(bx + 10, ry - 22, bw - 20, 64, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=8))
        f.append(text(bx + bw / 2, ry, cond, size=12, bold=True))
        f.append(text(bx + bw / 2, ry + 19, outs, size=11, color=INK))
        f.append(text(bx + bw / 2, ry + 37, verdict, size=12, color=col, bold=True))
        ry += 70

    f.append(text(W / 2, H - 14,
                  "Обидва виходи високі рівно тоді, коли сигнал у вікні. "
                  "Виліз за будь-який край — той компаратор опускає вихід.",
                  size=11, color=INK, italic=True))
    return render(os.path.join(IMG, "window-idea.svg"), W, H, *f)


# ══ 2. Монтажне «І»: два відкриті колектори на спільній підтяжці ═════════════
def fig_wired_and():
    W, H = 720, 430
    f = [text(W / 2, 28, "Монтажне «І»: «1» лише коли ОБИДВА транзистори закриті",
              size=16, bold=True)]

    line_x = 430
    top_y, bot_y = 96, 348
    # підтяжка до живлення
    f.append(line(line_x, top_y, line_x, 66, color=POS, sw=2))
    f.append(text(line_x, 56, "+Vпідт", size=12, color=POS, bold=True))
    rb, _, _ = textbox(line_x, 118, "Rпідт", size=12, fill="#fff7e6", stroke="#b8860b", min_w=46)
    f.append(rb)
    f.append(line(line_x, 140, line_x, bot_y, color=INK, sw=2.4))

    # два канали з відкритим колектором
    ys = [185, 285]
    labels = ["нижній компаратор", "верхній компаратор"]
    states = ["закр.", "закр."]   # сигнал у вікні → обидва закриті
    for y, lab, st in zip(ys, labels, states):
        f.append(rect(60, y - 28, 150, 56, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=8))
        f.append(text(135, y - 6, lab, size=11, bold=True))
        f.append(text(135, y + 13, "транз. " + st, size=11, color=MUTED))
        f.append(npn(250, y))
        f.append(line(210, y, 230, y, color=INK, sw=1.6))            # вихід рамки → база
        f.append(line(261, y - 12, 261, y, color=INK, sw=1.8))       # колектор → лінія
        f.append(line(261, y, line_x, y, color=INK, sw=1.8))
        f.append(circle(line_x, y, 3.5, fill=INK, stroke=INK, sw=1))
        f.append(line(261, y + 12, 261, y + 34, color=INK, sw=1.8))  # емітер → земля
        f.append(ground(261, y + 34))

    f.append(text(line_x + 16, (140 + bot_y) / 2 - 8, "спільна лінія", size=12, bold=True, anchor="start"))
    f.append(text(line_x + 16, (140 + bot_y) / 2 + 11, "(у нашому випадку «1»)", size=11, color=FIELD, anchor="start"))

    # вихід на споживача
    f.append(line(line_x, bot_y, 560, bot_y, color=INK, sw=2))
    f.append(arrow(560, bot_y, 600, bot_y, color=INK, sw=2))
    b, _, _ = textbox(656, bot_y, "1 вхід\nMCU / LED", size=12, fill="#eef2fc", stroke=NEG)
    f.append(b)

    f.append(text(W / 2, H - 14,
                  "Будь-який відкритий транзистор сам садить лінію на землю → «0». "
                  "«1» — лише коли обидва відпустили. Це «І» зробив сам дріт.",
                  size=11, color=INK, italic=True))
    return render(os.path.join(IMG, "wired-and.svg"), W, H, *f)


# ══ 3. Триланковий дільник задає обидва пороги ═══════════════════════════════
def fig_threshold_divider():
    W, H = 700, 430
    f = [text(W / 2, 28, "Один дільник — обидва пороги від спільного джерела",
              size=16, bold=True)]

    dx = 200
    top_y = 80
    # +Vоп зверху
    f.append(line(dx, 56, dx, top_y, color=POS, sw=2))
    f.append(text(dx, 50, "+Vоп", size=12, color=POS, bold=True))

    # три резистори: R_верх, R_сер, R_низ
    seg = 76
    y0 = top_y
    boxes = [("R_верх", y0), ("R_сер", y0 + seg + 28), ("R_низ", y0 + 2 * (seg + 28))]
    rh = seg
    for lab, y in boxes:
        f.append(rect(dx - 16, y, 32, rh, fill="#fff", stroke=INK, sw=1.4, rx=0))
        f.append(text(dx + 30, y + rh / 2 + 4, lab, size=12, anchor="start"))

    # вузли між резисторами = пороги
    v_top = boxes[0][1] + rh         # після R_верх = V_в
    v_mid = boxes[1][1] + rh         # після R_сер = V_н
    # з'єднувальні відрізки між боксами
    f.append(line(dx, boxes[0][1] + rh, dx, boxes[1][1], color=INK, sw=2))
    f.append(line(dx, boxes[1][1] + rh, dx, boxes[2][1], color=INK, sw=2))
    # земля під R_низ
    f.append(line(dx, boxes[2][1] + rh, dx, boxes[2][1] + rh + 22, color=INK, sw=2))
    f.append(ground(dx, boxes[2][1] + rh + 22))

    # відведення порогів праворуч
    f.append(circle(dx, v_top, 3.5, fill=INK, stroke=INK, sw=1))
    f.append(line(dx, v_top, 420, v_top, color=NEG, sw=2))
    f.append(text(426, v_top + 4, "V_в  (верхній поріг)", size=12, color=NEG, bold=True, anchor="start"))

    f.append(circle(dx, v_mid, 3.5, fill=INK, stroke=INK, sw=1))
    f.append(line(dx, v_mid, 420, v_mid, color=NEG, sw=2))
    f.append(text(426, v_mid + 4, "V_н  (нижній поріг)", size=12, color=NEG, bold=True, anchor="start"))

    f.append(text(W / 2, H - 16,
                  "Просіло живлення — обидва пороги зсунулись разом, "
                  "а ширина вікна V_в − V_н лишилась тією самою.",
                  size=11, color=INK, italic=True))
    return render(os.path.join(IMG, "threshold-divider.svg"), W, H, *f)


# ══ 4. Галерея застосувань вікна ═════════════════════════════════════════════
def fig_applications():
    W, H = 720, 360
    f = [text(W / 2, 30, "Усюди, де питання — «в межах чи ні»",
              size=16, bold=True)]
    cards = [
        ("норма живлення", "4.75…5.25 В → «ОК»"),
        ("безпечна t°", "не замерзло й не перегрілось"),
        ("обрив давача", "сигнал виліз за вікно"),
        ("сортування", "розмір у вузькій смузі"),
        ("мертва зона нуля", "вузьке вікно довкола 0"),
        ("діапазон для АЦП", "сигнал ще в межах"),
    ]
    cw, ch, gx, gy = 200, 96, 24, 24
    x0, y0 = 36, 70
    for i, (ttl, sub) in enumerate(cards):
        col, row = i % 3, i // 3
        x = x0 + col * (cw + gx)
        y = y0 + row * (ch + gy)
        f.append(rect(x, y, cw, ch, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=10))
        f.append(text(x + cw / 2, y + 36, ttl, size=14, bold=True))
        f.append(fitbox(x + 10, y + 52, cw - 20, 32, sub, size=11,
                        fill="#fff", stroke="#e3e8ee", color=MUTED))
    f.append(text(W / 2, 344,
                  "Кожен випадок — та сама пара порогів і те саме «всередині / зовні».",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "applications.svg"), W, H, *f)


if __name__ == "__main__":
    fig_window_idea()
    fig_wired_and()
    fig_threshold_divider()
    fig_applications()
    print("OK: figures ->", IMG)
