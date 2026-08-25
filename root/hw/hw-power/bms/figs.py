# -*- coding: utf-8 -*-
"""Фігури до теми «Захист і BMS».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AMBER = "#b8860b"   # надструм/проміжний рівень
VIOL  = "#7d3c98"   # коротке замикання


# ── Чотири загрози й вартовий ─────────────────────────────────────────────────
def fig_threats():
    W, H = 820, 380
    f = [text(W / 2, 30, "Захист: останній рубіж проти чотирьох загроз",
              size=17, bold=True)]
    cx, cy = W / 2, 200
    # комірка з захистом — у центрі
    f.append(rect(cx - 85, cy - 48, 170, 96, fill="#e9f7ef", stroke=FIELD, sw=2))
    f.append(text(cx, cy - 18, "комірка", size=13, bold=True, color=FIELD))
    f.append(text(cx, cy + 5, "+ ЗАХИСТ", size=13, bold=True, color=POS))
    f.append(text(cx, cy + 28, "(відрубує на межі)", size=10.5, color=MUTED))
    # чотири загрози по кутах
    threats = [
        (150, 110, "Перезаряд", "OVP: V > ~4.3 В\nосідання літію, пожежа", POS, "#fbeee6"),
        (670, 110, "Глибокий розряд", "UVP: V < ~2.5 В\nрозчиняється мідь, смерть", NEG, "#eef3fb"),
        (150, 300, "Надструм", "OCP: забагато ампер\nджоулеве тепло", AMBER, "#fbf3e0"),
        (670, 300, "Коротке замикання", "SCP: миттєвий стрибок\nобрив умить", VIOL, "#f3eaf7"),
    ]
    bw, bh = 230, 78
    for bx, by, ttl, body, col, fill in threats:
        f.append(rect(bx - bw / 2, by - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        f.append(text(bx, by - bh / 2 + 22, ttl, size=13, bold=True, color=col))
        f.append(mtext(bx, by - bh / 2 + 42, body, size=10, color=INK))
        # стрілка від загрози до центру
        sx = bx + (bw / 2 if bx < cx else -bw / 2)
        sy = by + (10 if by < cy else -10)
        tx = cx + (-90 if bx < cx else 90)
        ty = cy + (-30 if by < cy else 30)
        f.append(arrow(sx, sy, tx, ty, color=MUTED, sw=1.5))
    b, _, _ = textbox(W / 2, 360,
                      "у нормі захист мовчить; вийшла напруга чи струм за межі — аварійно відрубує комірку. Це не зарядник, а остання сітка",
                      size=11, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "threats.svg"), W, H, *f)


# ── Захисна плата: чип + два MOSFET ───────────────────────────────────────────
def fig_board():
    W, H = 820, 360
    f = [text(W / 2, 30, "Захисна плата: чип і два послідовні MOSFET",
              size=17, bold=True)]
    cy = 150
    # комірка
    f.append(rect(60, cy - 38, 110, 76, fill="#e9f7ef", stroke=FIELD, sw=1.8))
    f.append(text(115, cy - 6, "комірка", size=12, bold=True, color=FIELD))
    f.append(text(115, cy + 16, "Li 1S", size=10.5, color=MUTED))
    # плюсова лінія (B+ → P+)
    f.append(line(170, cy - 22, 740, cy - 22, color=POS, sw=2.4))
    f.append(text(150, cy - 26, "B+", size=10, color=POS, anchor="end"))
    # мінусова лінія через два FET (B− → P−)
    f.append(line(170, cy + 22, 320, cy + 22, color=INK, sw=2))
    f.append(text(150, cy + 26, "B−", size=10, color=INK, anchor="end"))
    f.append(rect(320, cy + 5, 60, 34, fill="#fbf3e0", stroke=AMBER, sw=1.8))
    f.append(text(350, cy + 27, "FET₁", size=11, bold=True, color=AMBER))
    f.append(text(350, cy + 54, "заряд", size=9.5, color=MUTED))
    f.append(line(380, cy + 22, 410, cy + 22, color=INK, sw=2))
    f.append(rect(410, cy + 5, 60, 34, fill="#fbf3e0", stroke=AMBER, sw=1.8))
    f.append(text(440, cy + 27, "FET₂", size=11, bold=True, color=AMBER))
    f.append(text(440, cy + 54, "розряд", size=9.5, color=MUTED))
    f.append(line(470, cy + 22, 740, cy + 22, color=INK, sw=2))
    # вихідні клеми
    f.append(circle(740, cy - 22, 4, fill=POS, stroke=POS, sw=0))
    f.append(text(752, cy - 26, "P+", size=10, bold=True, color=POS, anchor="start"))
    f.append(circle(740, cy + 22, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(752, cy + 26, "P−", size=10, bold=True, color=INK, anchor="start"))
    f.append(text(740, cy - 44, "до пристрою / зарядки", size=9.5, color=MUTED, anchor="middle"))
    # захисний чип
    f.append(rect(330, cy + 95, 160, 70, fill="#eef3fb", stroke=NEG, sw=1.8))
    f.append(text(410, cy + 120, "захисний чип", size=12, bold=True, color=NEG))
    f.append(text(410, cy + 140, "DW01-клас", size=10.5, color=INK))
    f.append(text(410, cy + 157, "міряє V і I", size=9.5, color=MUTED))
    # чип керує затворами
    f.append(arrow(350, cy + 95, 350, cy + 41, color=FIELD, sw=1.5))
    f.append(arrow(440, cy + 95, 440, cy + 41, color=FIELD, sw=1.5))
    f.append(text(410, cy + 88, "керує затворами", size=9.5, bold=True, color=FIELD))
    # чип міряє напругу комірки
    f.append(line(115, cy + 38, 115, cy + 200, color=NEG, sw=1.2, dash="3,3"))
    f.append(line(115, cy + 200, 330, cy + 200, color=NEG, sw=1.2, dash="3,3"))
    f.append(text(222, cy + 195, "міряє напругу комірки", size=9.5, color=NEG))
    b, _, _ = textbox(W / 2, 340,
                      "два MOSFET увімкнено зустрічно (тіловими діодами назустріч), щоб обірвати струм в обидва боки; чип розмикає потрібний на аварії",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "board.svg"), W, H, *f)


# ── Вікно напруги + пороги струму й тепла ─────────────────────────────────────
def fig_window():
    W, H = 820, 380
    f = [text(W / 2, 30, "Вікно безпеки: поза ним комірку від'єднують",
              size=17, bold=True)]
    # вертикальна шкала-вікно зліва
    bx, top, bw = 230, 70, 130
    bot = 300
    # OVP-смуга
    f.append(rect(bx, top, bw, 34, fill="#fbeee6", stroke=POS, sw=1.4))
    f.append(text(bx + bw / 2, top + 22, "OVP → обрив заряду", size=9.5, bold=True, color=POS))
    # робоче вікно
    f.append(rect(bx, top + 34, bw, 158, fill="#e9f7ef", stroke=FIELD, sw=1.4))
    f.append(text(bx + bw / 2, top + 105, "робоче вікно", size=11, bold=True, color=FIELD))
    f.append(text(bx + bw / 2, top + 124, "2.5–4.2 В", size=10, color=INK))
    # UVP-смуга
    f.append(rect(bx, top + 192, bw, 38, fill="#eef3fb", stroke=NEG, sw=1.4))
    f.append(text(bx + bw / 2, top + 216, "UVP → обрив розряду", size=9.5, bold=True, color=NEG))
    f.append(text(bx - 8, top + 16, "OVP ≈ 4.3", size=9.5, bold=True, color=POS, anchor="end"))
    f.append(text(bx - 8, top + 214, "UVP ≈ 2.5", size=9.5, bold=True, color=NEG, anchor="end"))
    # права колонка: струм і тепло
    px, py, pw, ph = 470, 80, 300, 210
    f.append(rect(px, py, pw, ph, fill=FILL, stroke=MUTED, sw=1.4))
    f.append(text(px + pw / 2, py + 26, "А ще — за струмом і теплом", size=12, bold=True))
    items = [
        ("OCP — надструм", "тривале перевищення → обрив", AMBER),
        ("SCP — коротке", "миттєвий стрибок → обрив умить", VIOL),
        ("гістерезис", "вмикає назад лише після відновлення", FIELD),
        ("OTP — перегрів", "є у складніших платах", POS),
    ]
    yy = py + 56
    for ttl, sub, col in items:
        f.append(text(px + 20, yy, "• " + ttl, size=11, bold=True, color=col, anchor="start"))
        f.append(text(px + 34, yy + 16, sub, size=9.5, color=MUTED, anchor="start"))
        yy += 38
    b, _, _ = textbox(W / 2, 358,
                      "пороги ввімкнення й вимкнення рознесені (гістерезис), інакше захист деренчав би на самій межі",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "window.svg"), W, H, *f)


# ── Балансування: пасивне проти активного ─────────────────────────────────────
def fig_balancing():
    W, H = 820, 380
    f = [text(W / 2, 30, "Балансування: злити надлишок проти перелити заряд",
              size=17, bold=True)]
    # ── пасивне (ліворуч) ──
    f.append(rect(40, 56, 360, 250, fill="#fbf3e0", stroke=AMBER, sw=1.6))
    f.append(text(220, 80, "Пасивне: зливає надлишок у тепло", size=12, bold=True, color=AMBER))
    cells_p = [("4.20 В", 120, True), ("4.15 В", 178, False), ("4.10 В", 236, False)]
    for volt, y, hot in cells_p:
        f.append(rect(110, y, 90, 44, fill="#e9f7ef", stroke=FIELD, sw=1.6))
        f.append(text(155, y + 18, "комірка", size=9.5, color=MUTED))
        f.append(text(155, y + 36, volt, size=11, bold=True, color=FIELD))
        if hot:
            f.append(rect(230, y + 8, 46, 28, fill=BG, stroke=POS, sw=1.6))
            f.append(text(253, y + 27, "R", size=12, bold=True, color=POS))
            f.append(text(290, y + 27, "→ тепло", size=9.5, bold=True, color=POS, anchor="start"))
    f.append(text(220, 294, "просто й дешево — та енергію палимо", size=10, color=INK))
    # ── активне (праворуч) ──
    f.append(rect(420, 56, 360, 250, fill="#e9f7ef", stroke=FIELD, sw=1.6))
    f.append(text(600, 80, "Активне: переливає заряд", size=12, bold=True, color=FIELD))
    cells_a = [("4.20 В", 120), ("4.15 В", 178), ("4.10 В", 236)]
    for volt, y in cells_a:
        f.append(rect(490, y, 90, 44, fill="#e9f7ef", stroke=FIELD, sw=1.6))
        f.append(text(535, y + 18, "комірка", size=9.5, color=MUTED))
        f.append(text(535, y + 36, volt, size=11, bold=True, color=FIELD))
    f.append(arrow(590, 138, 590, 236, color=NEG, sw=2))
    f.append(text(630, 178, "переливає заряд", size=9.5, bold=True, color=NEG, anchor="start"))
    f.append(text(630, 195, "з повної в порожнішу", size=9.5, color=INK, anchor="start"))
    f.append(text(600, 294, "ефективно — та складно й дорого", size=10, color=INK))
    b, _, _ = textbox(W / 2, 358,
                      "у послідовній збірці комірки дрейфують; балансир вирівнює їх. Струми скромні (десятки мА) — вирівнюють різницю за цикл",
                      size=11, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "balancing.svg"), W, H, *f)


# ── Найслабша комірка диктує обидва краї ──────────────────────────────────────
def fig_weakest():
    W, H = 820, 360
    f = [text(W / 2, 30, "Найслабша комірка диктує обидва краї",
              size=17, bold=True)]
    f.append(text(W / 2, 56, "послідовна збірка 4S", size=11, color=MUTED))
    cells = [(120, "100%", "повна", FIELD, 1.0),
             (270, "100%", "", FIELD, 1.0),
             (420, "85%", "слабша", POS, 0.85),
             (570, "100%", "", FIELD, 1.0)]
    bx0, by, bw, bh = 0, 72, 110, 120
    for cx, pct, tag, col, frac in cells:
        f.append(rect(cx, by, bw, bh, fill="#f0f0f0", stroke=MUTED, sw=1.4))
        fh = bh * frac
        f.append(rect(cx + 4, by + (bh - fh) + 2, bw - 8, fh - 4,
                      fill=col, stroke=col, sw=1.4))
        f.append(text(cx + bw / 2, by + bh + 18, pct, size=11, bold=True, color=col))
        if tag:
            f.append(text(cx + bw / 2, by + bh + 34, tag, size=9.5, bold=True, color=col))
        if cx < 570:
            f.append(text(cx + bw + 20, by + bh / 2 + 6, "+", size=16, bold=True))
    box = rect(40, 250, 740, 92, fill="#fbeee6", stroke=POS, sw=1.5)
    f.append(box)
    f.append(text(410, 274, "на ЗАРЯДІ слабша перша впирається в OVP → решта недозаряджені, пакет не добирає",
                  size=10.5, color=INK))
    f.append(text(410, 296, "на РОЗРЯДІ вона ж перша падає до UVP → пакет стає, хоч у сильніших ще є заряд",
                  size=10.5, color=INK))
    f.append(text(410, 322, "корисна ємність пакета = найслабша комірка; балансування й добір однакових це лікують",
                  size=10.5, bold=True, color=POS))
    render(os.path.join(IMG, "weakest.svg"), W, H, *f)


# ── Спектр: від плати за долар до повної BMS ──────────────────────────────────
def fig_spectrum():
    W, H = 820, 360
    f = [text(W / 2, 30, "Спектр захисту: від плати за долар до повної BMS",
              size=17, bold=True)]
    cards = [
        (50, "Захисна плата", "1S, одна комірка", ["OVP/UVP/OCP/SCP", "чип + 2 FET (~$1)"], FIELD),
        (300, "Захист + баланс", "кілька комірок (nS)", ["+ балансування", "+ моніторинг комірок"], AMBER),
        (550, "Повна BMS", "великі пакети", ["+ облік SoC/SoH", "+ зв'язок, тепло"], POS),
    ]
    cw, ch, cy = 220, 170, 80
    for cx, ttl, sub, body, col in cards:
        f.append(rect(cx, cy, cw, ch, fill=BG, stroke=col, sw=2))
        f.append(text(cx + cw / 2, cy + 30, ttl, size=13.5, bold=True, color=col))
        f.append(text(cx + cw / 2, cy + 52, sub, size=10, color=MUTED, italic=True))
        f.append(line(cx + 20, cy + 64, cx + cw - 20, cy + 64, color="#e4e4e4", sw=1))
        yy = cy + 92
        for ln in body:
            f.append(text(cx + cw / 2, yy, ln, size=10.5, color=INK))
            yy += 24
    f.append(arrow(270, cy + ch / 2, 298, cy + ch / 2, color=INK, sw=2))
    f.append(arrow(520, cy + ch / 2, 548, cy + ch / 2, color=INK, sw=2))
    b, _, _ = textbox(W / 2, 320,
                      "мінімум для будь-якого літію — захисна плата (часто вже в комірці); чим більший і відповідальніший пакет, тим вище по спектру",
                      size=11, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "spectrum.svg"), W, H, *f)


if __name__ == "__main__":
    fig_threats()
    fig_board()
    fig_window()
    fig_balancing()
    fig_weakest()
    fig_spectrum()
    print("OK: 6 figures ->", IMG)
