# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Світлодіодна матриця 8×8 (1588BS)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Внутрішня будова: спільний анод — рядки-аноди, стовпці-катоди ──────────
def fig_inside():
    W, H = 780, 600
    f = [text(W / 2, 30, "Усередині 1588BS: 64 діоди на перетинах 8 рядків і 8 стовпців",
              size=15, bold=True)]

    # сітка перетинів (зсунута донизу, щоб над нею було місце під підписи)
    n = 8
    gx0, gy0 = 250, 150         # лівий-верхній перетин
    step = 46
    # шини рядків (аноди) — горизонтальні лінії ліворуч
    for r in range(n):
        y = gy0 + r * step
        f.append(line(gx0 - 30, y, gx0 + (n - 1) * step + 24, y, color=POS, sw=1.6))
    # шини стовпців (катоди) — вертикальні лінії донизу
    for c in range(n):
        x = gx0 + c * step
        f.append(line(x, gy0 - 26, x, gy0 + (n - 1) * step + 30, color=NEG, sw=1.6))

    # діоди на перетинах (маленькі трикутники-стрілки: анод→катод, тобто ↓)
    for r in range(n):
        for c in range(n):
            x = gx0 + c * step
            y = gy0 + r * step
            lit = (r == 0 and c == 0)
            fill = "#e74c3c" if lit else "#f7d9d5"
            # трикутник діода вершиною вниз (струм із рядка-анода в стовпець-катод)
            f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" '
                     'fill="%s" stroke="%s" stroke-width="1.1"/>'
                     % (x - 6, y - 5, x + 6, y - 5, x, y + 6, fill, POS))

    # підпис лівої шини — рядки-аноди (вертикальний, повз саму шину)
    lblx = gx0 - 90
    lcy = gy0 + (n - 1) * step / 2
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">'
             'рядки = аноди (+)</text>' % (lblx, lcy, FONT, POS, lblx, lcy))
    for r in range(n):
        f.append(text(gx0 - 40, gy0 + r * step + 4, "R%d" % (r + 1),
                      size=9.5, color=POS, anchor="end"))
    # підпис верхньої шини — стовпці-катоди (над сіткою, по центру)
    f.append(text(gx0 + (n - 1) * step / 2, gy0 - 44, "стовпці = катоди (−)",
                  size=12, bold=True, color=NEG, anchor="middle"))
    for c in range(n):
        f.append(text(gx0 + c * step, gy0 + (n - 1) * step + 52, "C%d" % (c + 1),
                      size=9.5, color=NEG, anchor="middle"))

    # виноска до засвіченого діода R1/C1 — над правим краєм сітки, з'єднана лінією
    cx0, cy0 = gx0, gy0          # центр діода R1/C1
    calcx, calcy = gx0 + (n - 1) * step - 10, gy0 - 48
    f.append(line(cx0 + 8, cy0 - 4, calcx - 40, calcy + 12, color=INK, sw=1.0, dash="3,3"))
    b0, _, _ = textbox(calcx, calcy, "R1 = +5 В, C1 = 0 В\n→ цей діод горить",
                       size=10, fill="#fdecea", stroke=POS)
    f.append(b0)

    b, _, _ = textbox(W / 2, 575,
                      "діод горить лише коли його рядок = «+», а стовпець = «−»; жоден вивід не належить одному діоду — усі спільні",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Розгортка: рядок за рядком, а око бачить цілий кадр ────────────────────
def fig_scan():
    W, H = 780, 430
    f = [text(W / 2, 28, "Розгортка: МК світить один рядок за раз, око зливає в кадр",
              size=15, bold=True)]

    # три «фази» по 8×8 сітки: горить рядок 1, рядок 2, рядок 3 …
    def grid(px, py, cell, active_row, caption):
        cols = 8
        rows = 8
        for r in range(rows):
            for c in range(cols):
                x = px + c * cell
                y = py + r * cell
                on = (r == active_row) and (c in (1, 2, 4, 5, 6))  # довільний узор рядка
                f.append(rect(x, y, cell - 3, cell - 3,
                              fill=("#e74c3c" if on else "#f2f2f2"),
                              stroke="#d0d0d0", sw=0.8, rx=2))
        f.append(text(px + cols * cell / 2, py + rows * cell + 20, caption,
                      size=10.5, color=MUTED))

    cell = 20
    y0 = 70
    grid(70, y0, cell, 0, "такт 1: рядок 1")
    grid(290, y0, cell, 1, "такт 2: рядок 2")
    grid(510, y0, cell, 2, "такт 3: рядок 3 …")

    # стрілки між фазами
    f.append(arrow(240, y0 + 80, 285, y0 + 80, color=INK, sw=2.0))
    f.append(arrow(460, y0 + 80, 505, y0 + 80, color=INK, sw=2.0))

    # результат — «око бачить усе разом»
    ry = y0 + 250
    f.append(text(W / 2, ry - 8, "≈ 800 разів за секунду по колу — швидше за око",
                  size=12, bold=True, color=FIELD))
    b, _, _ = textbox(W / 2, ry + 30,
                      "у кожну мить фізично світиться лише один рядок; зорова інерція ока (≈1/16 с) зливає вісім спалахів у суцільну картинку",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "scan.svg"), W, H, *f)


# ── 3. Підключення до МК: резистори на стовпцях, транзистори на рядках ────────
def fig_wiring():
    W, H = 900, 560
    f = [text(W / 2, 28, "Пряме керування від МК: струм ставить резистор, рядок вмикає ключ",
              size=15, bold=True)]

    # матриця-блок у центрі
    mx, my, mw, mh = 360, 130, 200, 200
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(mx + mw / 2, my + mh / 2 - 8, "матриця", size=12, bold=True, color=MUTED))
    f.append(text(mx + mw / 2, my + mh / 2 + 10, "8×8 (1588BS)", size=10, color=MUTED))

    # 8 стовпців зверху → через резистори до МК
    ncol = 8
    for c in range(ncol):
        x = mx + 18 + c * ((mw - 36) / (ncol - 1))
        f.append(line(x, my, x, my - 26, color=NEG, sw=1.4))
        # резистор-прямокутник
        f.append(rect(x - 5, my - 52, 10, 24, fill="#eef2f8", stroke=INK, sw=1.2, rx=2))
        f.append(line(x, my - 52, x, my - 70, color=INK, sw=1.4))
    f.append(text(mx + mw / 2, my - 84, "8 резисторів (≈220 Ом) → 8 виводів МК",
                  size=10.5, bold=True, color=INK))
    f.append(text(mx - 92, my - 40, "стовпці (катоди)", size=10, color=NEG, anchor="start"))

    # 8 рядків праворуч → через транзистори до землі + керування МК
    nrow = 8
    for r in range(nrow):
        y = my + 16 + r * ((mh - 32) / (nrow - 1))
        f.append(line(mx + mw, y, mx + mw + 24, y, color=POS, sw=1.4))
    # блок «транзисторні ключі»
    tx = mx + mw + 24
    f.append(rect(tx, my + 6, 96, mh - 12, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(tx + 48, my + mh / 2 - 8, "8 ключів", size=11, bold=True, color=POS))
    f.append(text(tx + 48, my + mh / 2 + 10, "(транзистори)", size=9.5, color=POS))
    f.append(text(tx + 48, my - 8, "рядки (аноди)", size=10, color=POS))
    f.append(text(tx + 48, my + mh + 22, "+5 В крізь ключ", size=9.5, color=POS))
    # керування ключами від МК (стрілка вліво до блоку ключів)
    ctlx = tx + 96 + 16
    f.append(arrow(ctlx + 44, my + mh / 2, tx + 96 + 4, my + mh / 2, color=INK, sw=1.8))
    f.append(text(ctlx + 6, my + mh / 2 - 8, "8 виводів МК", size=10, color=INK, anchor="start"))
    f.append(text(ctlx + 6, my + mh / 2 + 10, "(вибір рядка)", size=9.5, color=MUTED, anchor="start"))

    # блок МК ліворуч (куди йдуть стовпці-резистори)
    mcx = 120
    f.append(rect(mcx - 60, my + 30, 120, 90, fill="#eef2f8", stroke=INK, sw=1.6, rx=8))
    f.append(text(mcx, my + 62, "МК", size=13, bold=True))
    f.append(text(mcx, my + 84, "(8 + 8 виводів)", size=9.5, color=MUTED))
    f.append(text(mcx, my + 104, "тягне стовпці в 0", size=9, color=NEG))

    # два коротких підсумкових рядки (кожен рядок — короткий, textbox по найдовшому)
    b, _, _ = textbox(W / 2, 470,
                      "резистори на стовпцях обмежують струм; транзисторний ключ на рядку\n"
                      "тримає струм восьми діодів, який не подужав би один вивід МК",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    b2, _, _ = textbox(W / 2, 525,
                       "без спецдрайвера це 16 виводів МК і ручна розгортка в перериванні",
                       size=10.5, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Кадр MAX7219: 16 біт = адреса реєстра + байт даних, старший біт першим ─
def fig_max_frame():
    W, H = 900, 470
    f = [text(W / 2, 28, "Кадр MAX7219: 16 біт у чип — старша половина адреса, молодша дані",
              size=15, bold=True)]

    # 16 клітинок бітів у ряд
    n = 16
    cw, ch = 46, 46
    x0 = (W - n * cw) / 2
    y0 = 120
    for i in range(n):
        bit = n - 1 - i          # D15 … D0 зліва направо
        x = x0 + i * cw
        # група: D15..D12 «не важливо», D11..D8 адреса, D7..D0 дані
        if bit >= 12:
            fill, br = "#f2f2f2", MUTED
        elif bit >= 8:
            fill, br = "#fdecea", POS
        else:
            fill, br = "#eaf0fd", NEG
        f.append(rect(x, y0, cw - 3, ch, fill=fill, stroke=br, sw=1.4, rx=3))
        f.append(text(x + (cw - 3) / 2, y0 + ch / 2 + 5, "D%d" % bit,
                      size=11, color=INK))

    # фігурні підписи-групи під клітинками
    def brace(a_bit_hi, a_bit_lo, label, color, yoff=0):
        xi_hi = x0 + (n - 1 - a_bit_hi) * cw
        xi_lo = x0 + (n - 1 - a_bit_lo) * cw + (cw - 3)
        yb = y0 + ch + 14 + yoff
        f.append(line(xi_hi, yb, xi_lo, yb, color=color, sw=1.6))
        f.append(line(xi_hi, yb, xi_hi, yb - 6, color=color, sw=1.6))
        f.append(line(xi_lo, yb, xi_lo, yb - 6, color=color, sw=1.6))
        f.append(text((xi_hi + xi_lo) / 2, yb + 18, label, size=11, bold=True, color=color))

    brace(15, 12, "не важливо (0)", MUTED)
    brace(11, 8, "адреса реєстра (D11..D8)", POS)
    brace(7, 0, "байт даних (D7..D0)", NEG)

    # приклад конкретного кадру
    ey = y0 + ch + 70
    b, _, _ = textbox(W / 2, ey + 6,
                      "приклад: записати в рядок 3 узор 0b10110010\n"
                      "адреса 0x03, дані 0xB2  →  у чип іде 0x03B2",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)

    # такт і LOAD
    b2, _, _ = textbox(W / 2, ey + 70,
                       "16 бітів вганяєш по одному фронтом CLK, старший першим;\n"
                       "коли всі 16 усередині — фронт LOAD клацає їх у реєстр за адресою",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "max-frame.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_scan()
    fig_wiring()
    fig_max_frame()
    print("OK: 4 figures ->", IMG)
