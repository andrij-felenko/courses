# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-серія (Keyes 37-в-1)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія KY-модуля: цоколівка S / + (середній) / − ─────────────────────
def fig_ky_pinout():
    W, H = 900, 470
    f = [text(W / 2, 30, "Спільна цоколівка простого KY-модуля", size=16, bold=True)]

    # Плата модуля
    bx, by, bw, bh = 300, 70, 300, 190
    f.append(rect(bx, by, bw, bh, fill="#eef3fb", stroke=NEG, sw=2.2, rx=14))
    f.append(text(bx + bw / 2, by + 34, "KY-модуль", size=14, bold=True, color=NEG))
    f.append(text(bx + bw / 2, by + 56, "чутливий елемент + обвʼязка", size=10.5, color=MUTED))
    # символ давача всередині
    f.append(circle(bx + bw / 2, by + 108, 26, fill=BG, stroke=INK, sw=1.6))
    f.append(text(bx + bw / 2, by + 113, "давач", size=10, color=INK))

    # Гребінка на 3 штирі внизу плати
    pin_y = by + bh
    labels = [("S", "сигнал", NEG), ("+", "живлення", POS), ("−", "земля", NEG)]
    gap = 74
    x0 = bx + bw / 2 - gap
    xs = [x0, x0 + gap, x0 + 2 * gap]
    for (lab, _sub, col), px in zip(labels, xs):
        # штир
        f.append(rect(px - 7, pin_y, 14, 34, fill="#d9c27a", stroke=INK, sw=1.2, rx=3))
        # підпис букви ПІД штирем
        f.append(text(px, pin_y + 54, lab, size=17, bold=True,
                      color=POS if lab == "+" else INK))

    # Виноски-описи кожного штиря — розкидані з запасом, лінії ведуть повз написи
    # S (лівий) — виноска ліворуч-униз
    f.append(line(xs[0], pin_y + 62, 150, 360, color=MUTED, sw=1.2))
    b, _, _ = textbox(150, 388, "S — Signal\nвихід (або вхід)\nдавача", size=10.5,
                      fill=FILL, stroke=NEG)
    f.append(b)
    # + (середній) — виноска прямо вниз, акцент
    f.append(line(xs[1], pin_y + 62, W / 2, 372, color=POS, sw=1.6))
    b, _, _ = textbox(W / 2, 400, "+ — живлення 3.3–5 В\nНАВМИСНО в середині:\nважче зіскочити на нього",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)
    # − (правий) — виноска праворуч-униз
    f.append(line(xs[2], pin_y + 62, 750, 360, color=MUTED, sw=1.2))
    b, _, _ = textbox(750, 388, "− — GND\nспільна\nземля", size=10.5, fill=FILL, stroke=NEG)
    f.append(b)

    # Правило-нагадування — угорі праворуч, окремо від виносок
    b, _, _ = textbox(740, 110, "Підключай\nЗА ЛІТЕРАМИ,\nне за позицією", size=11,
                      fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b)

    render(os.path.join(IMG, "ky-pinout.svg"), W, H, *f)


# ── 2. Три архетипи KY-модуля: аналог · компаратор (LM393) · випромінювач ──────
def fig_ky_archetypes():
    W, H = 1000, 560
    f = [text(W / 2, 30, "Три лекала, за якими розмовляє вся KY-серія", size=16, bold=True)]

    col_w = 300
    col_y = 66
    col_h = 400
    xs = [30, 350, 670]
    accents = [FIELD, POS, NEG]
    fills = ["#eef6ef", "#fdf3ee", "#eef2fb"]

    # МК праворуч від кожної колонки — спільний приймач; намалюємо стрілку потоку
    def head(x, title, sub, accent, fill):
        f.append(rect(x, col_y, col_w, col_h, fill=fill, stroke=accent, sw=2.2, rx=14))
        f.append(text(x + col_w / 2, col_y + 30, title, size=13.5, bold=True, color=accent))
        f.append(text(x + col_w / 2, col_y + 52, sub, size=10, color=MUTED))

    # --- Колонка 1: пасивний аналоговий ---
    x = xs[0]
    head(x, "Пасивний аналоговий", "давач + дільник, без мікросхеми", accents[0], fills[0])
    f.append(circle(x + col_w / 2, col_y + 118, 30, fill=BG, stroke=INK, sw=1.6))
    f.append(text(x + col_w / 2, col_y + 123, "давач", size=10, color=INK))
    b, _, _ = textbox(x + col_w / 2, col_y + 210, "1 вихід:\nS = плавна напруга", size=11,
                      fill=BG, stroke=accents[0])
    f.append(b)
    b, _, _ = textbox(x + col_w / 2, col_y + 300, "читаєш:\nanalogRead()", size=11.5,
                      fill=BG, stroke=accents[0], bold=True)
    f.append(b)
    f.append(text(x + col_w / 2, col_y + 366, "напр. KY-018, KY-013", size=10, color=MUTED))

    # --- Колонка 2: компараторний LM393 ---
    x = xs[1]
    head(x, "Компараторний (LM393)", "давач + компаратор + гвинтик", accents[1], fills[1])
    f.append(circle(x + 70, col_y + 118, 26, fill=BG, stroke=INK, sw=1.6))
    f.append(text(x + 70, col_y + 123, "давач", size=9.5, color=INK))
    f.append(rect(x + 150, col_y + 92, 116, 52, fill=BG, stroke=accents[1], sw=1.6, rx=7))
    f.append(text(x + 208, col_y + 114, "LM393", size=11, bold=True, color=accents[1]))
    f.append(text(x + 208, col_y + 132, "+ поріг-гвинтик", size=9, color=MUTED))
    b, _, _ = textbox(x + col_w / 2, col_y + 208, "2 виходи:\nAO = напруга · DO = 0/1", size=10.5,
                      fill=BG, stroke=accents[1])
    f.append(b)
    b, _, _ = textbox(x + col_w / 2, col_y + 300, "читаєш:\nanalogRead() або digitalRead()",
                      size=10.5, fill=BG, stroke=accents[1], bold=True)
    f.append(b)
    f.append(text(x + col_w / 2, col_y + 366, "напр. KY-038, KY-026", size=10, color=MUTED))

    # --- Колонка 3: цифровий випромінювач ---
    x = xs[2]
    head(x, "Цифровий випромінювач", "нічого не міряє — сам діє", accents[2], fills[2])
    f.append(circle(x + col_w / 2, col_y + 118, 30, fill=BG, stroke=INK, sw=1.6))
    f.append(text(x + col_w / 2, col_y + 123, "зумер / ІЧ", size=9.5, color=INK))
    b, _, _ = textbox(x + col_w / 2, col_y + 210, "S = ВХІД:\nплата керує ним", size=11,
                      fill=BG, stroke=accents[2])
    f.append(b)
    b, _, _ = textbox(x + col_w / 2, col_y + 300, "керуєш:\ndigitalWrite()", size=11.5,
                      fill=BG, stroke=accents[2], bold=True)
    f.append(b)
    f.append(text(x + col_w / 2, col_y + 366, "напр. KY-012, KY-005", size=10, color=MUTED))

    # Нижня смуга: куди тече інформація (стрілки — під колонками, підписи поруч)
    ay = col_y + col_h + 40
    # 1 і 2: давач → МК (інформація в плату)
    f.append(arrow(xs[0] + col_w / 2, ay, xs[0] + col_w / 2 + 90, ay, color=accents[0], sw=2.0))
    f.append(text(xs[0] + col_w / 2 + 120, ay + 4, "у плату", size=10, color=accents[0],
                  bold=True, anchor="start"))
    f.append(arrow(xs[1] + col_w / 2, ay, xs[1] + col_w / 2 + 90, ay, color=accents[1], sw=2.0))
    f.append(text(xs[1] + col_w / 2 + 120, ay + 4, "у плату", size=10, color=accents[1],
                  bold=True, anchor="start"))
    # 3: МК → модуль (команда з плати) — стрілка в інший бік
    f.append(arrow(xs[2] + col_w / 2 + 90, ay, xs[2] + col_w / 2, ay, color=accents[2], sw=2.0))
    f.append(text(xs[2] + col_w / 2 - 110, ay + 4, "з плати", size=10, color=accents[2],
                  bold=True, anchor="end"))

    render(os.path.join(IMG, "ky-archetypes.svg"), W, H, *f)


# ── 3. Історія: джерело (Keyes) → наскрізна нумерація → розтеклося по всіх ──────
def fig_ky_history():
    W, H = 1000, 560
    f = [text(W / 2, 32, "Як «37-в-1» став стандартом, який копіюють усі", size=16, bold=True)]

    # ЛІВОРУЧ: джерело — Keyes збирає модулі в набір і нумерує
    sx, sy, sw, sh = 40, 80, 330, 400
    f.append(rect(sx, sy, sw, sh, fill="#fdf3ee", stroke=POS, sw=2.4, rx=16))
    f.append(text(sx + sw / 2, sy + 32, "ДЖЕРЕЛО", size=12, bold=True, color=POS))
    f.append(text(sx + sw / 2, sy + 54, "Shenzhen Keyes / Keyestudio", size=11.5, bold=True, color=INK))
    f.append(text(sx + sw / 2, sy + 74, "початок 2010-х", size=10, color=MUTED))

    # набір-коробка з кількома «модулями» всередині
    kx, ky_, kw, kh = sx + 46, sy + 100, sw - 92, 118
    f.append(rect(kx, ky_, kw, kh, fill=BG, stroke=INK, sw=1.6, rx=10))
    f.append(text(kx + kw / 2, ky_ + 22, "набір «37 in 1»", size=11, bold=True, color=INK))
    # ряди дрібних платок
    px0 = kx + 26
    for r in range(2):
        for c in range(5):
            cellx = px0 + c * 46
            celly = ky_ + 40 + r * 34
            f.append(rect(cellx, celly, 34, 22, fill="#eef3fb", stroke=NEG, sw=1.1, rx=4))
    f.append(text(kx + kw / 2, ky_ + kh - 8, "…37 різних модулів…", size=9, color=MUTED))

    # наскрізний рядок нумерації під коробкою
    b, _, _ = textbox(sx + sw / 2, sy + 296, "наскрізний рядок:\nKY-001 … KY-040\n(з пропусками — ріс наживо)",
                      size=11, fill=BG, stroke=POS, bold=True)
    f.append(b)
    f.append(text(sx + sw / 2, sy + 360, "«KY» ≈ Keyes", size=11, color=INK, bold=True))
    f.append(text(sx + sw / 2, sy + 380, "(загальне прочитання,", size=9, color=MUTED))
    f.append(text(sx + sw / 2, sy + 394, "офіційно не задокументоване)", size=9, color=MUTED))

    # СТРІЛКА через увесь малюнок: копіювання
    ax0, ax1, ayc = sx + sw + 8, 620, sy + sh / 2
    f.append(arrow(ax0, ayc, ax1, ayc, color=FIELD, sw=3.0))
    b, _, _ = textbox((ax0 + ax1) / 2, ayc - 44, "схеми прості\nй нічим не замкнені →\nкопіювати вільно",
                      size=10.5, fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b)

    # ПРАВОРУЧ: наслідок — ті самі номери в усіх виробників
    tx, ty, tw = 640, 90, 320
    f.append(text(tx + tw / 2, ty + 4, "НАСЛІДОК", size=12, bold=True, color=FIELD))
    f.append(text(tx + tw / 2, ty + 24, "той самий рядок — у всіх", size=10.5, color=MUTED))

    brands = [
        ("Keyes / Keyestudio", "першоджерело", POS),
        ("ELEGOO «37 in 1»", "ті самі номери", NEG),
        ("SunFounder", "ті самі номери", NEG),
        ("Joy-IT SensorKit", "ті самі номери (без згадки Keyes)", NEG),
        ("безіменний з ринку", "ті самі номери", MUTED),
    ]
    row_h = 62
    for i, (name, sub, col) in enumerate(brands):
        ry = ty + 44 + i * row_h
        f.append(rect(tx, ry, tw, row_h - 12, fill=BG, stroke=col, sw=1.8, rx=9))
        f.append(text(tx + 14, ry + 22, name, size=11.5, bold=True, color=INK, anchor="start"))
        f.append(text(tx + 14, ry + 40, sub, size=9.5, color=MUTED, anchor="start"))
        # ярлик спільного номера праворуч у рядку
        f.append(text(tx + tw - 12, ry + 30, "KY-038", size=11, bold=True, color=col, anchor="end"))

    render(os.path.join(IMG, "ky-history.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ky_pinout()
    fig_ky_archetypes()
    fig_ky_history()
    print("KY figs done ->", IMG)
