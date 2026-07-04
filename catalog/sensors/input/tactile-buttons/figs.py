# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Тактильні кнопки з ковпачками».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія: дві фази купола (звідки «клац»), 4 ніжки знизу, ковпачок ──────
def fig_anatomy():
    W, H = 940, 520
    f = [text(W / 2, 32, "Анатомія тактильної кнопки: звідки «клац» і навіщо ковпачок",
              size=16, bold=True)]

    # ── верх: дві фази купола-пружини (спокій ↔ натиск) ──
    f.append(text(W / 2, 70, "Розріз: усередині — куполок-пружинка над двома контактами",
                  size=12, bold=True, color=MUTED))
    phases = [(150, "СПОКІЙ", "купол вигнутий угору,\nконтакти розімкнені", MUTED, False),
              (560, "НАТИСК", "купол «пролускнув» униз,\nконтакти замкнені — «клац»", FIELD, True)]
    for (x0, lab, note, col, pressed) in phases:
        base_y = 200
        # корпус-рамка фази
        f.append(rect(x0, 100, 230, 150, fill="#eef4f0", stroke=INK, sw=1.8, rx=10))
        # штовхач згори
        f.append(rect(x0 + 95, 76 + (12 if pressed else 0), 40, 30, fill=BG, stroke=INK, sw=1.6, rx=4))
        # два нерухомі контакти на дні
        cxl, cxr, cy = x0 + 60, x0 + 170, base_y + 20
        f.append(line(x0 + 30, cy, x0 + 200, cy, color=INK, sw=1.6))
        f.append(circle(cxl, cy, 5, fill=BG, stroke=INK, sw=1.6))
        f.append(circle(cxr, cy, 5, fill=BG, stroke=INK, sw=1.6))
        # купол
        if not pressed:
            arc = ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="3"/>'
                   % (cxl, cy - 2, x0 + 115, cy - 44, cxr, cy - 2, POS))
        else:
            arc = ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="3"/>'
                   % (cxl, cy - 2, x0 + 115, cy + 10, cxr, cy - 2, FIELD))
        f.append(arc)
        f.append(text(x0 + 115, 128, lab, size=13, bold=True, color=col))
        b, _, _ = textbox(x0 + 115, 300, note, size=10.5, fill=BG, stroke=col)
        f.append(b)

    # ── низ ліворуч: 4 ніжки знизу ──
    lx, ly = 150, 380
    f.append(text(lx + 90, ly - 18, "вигляд знизу: 4 ніжки", size=12, bold=True, color=MUTED))
    f.append(rect(lx, ly, 180, 100, fill="#f7f9fc", stroke=INK, sw=1.8, rx=8))
    for (x, y, lab) in [(lx, ly + 22, "1"), (lx, ly + 78, "2"),
                        (lx + 180, ly + 22, "4"), (lx + 180, ly + 78, "3")]:
        ext = -26 if x > lx + 90 else 26
        f.append(line(x, y, x + ext, y, color=INK, sw=2.4))
        f.append(circle(x + ext, y, 4, fill=BG, stroke=INK, sw=1.6))
        tx = x + ext + (14 if ext > 0 else -14)
        f.append(text(tx, y + 4, lab, size=12, bold=True, color=INK,
                      anchor="start" if ext > 0 else "end"))
    f.append(text(lx + 90, ly + 56, "6×6 мм", size=11, bold=True, color=MUTED))

    # ── низ праворуч: ковпачок сідає на штовхач ──
    cx = 620
    f.append(text(cx + 90, ly - 18, "ковпачок надівається на штовхач", size=12, bold=True, color=MUTED))
    f.append(rect(cx + 70, ly + 62, 40, 28, fill=BG, stroke=INK, sw=1.8, rx=4))
    f.append(text(cx + 90, ly + 108, "штовхач (отвір Ø 3.5 мм)", size=10, color=MUTED))
    f.append(rect(cx + 62, ly + 4, 56, 40, fill="#fdecea", stroke=POS, sw=2.2, rx=6))
    f.append(text(cx + 90, ly + 29, "ковпачок", size=11, bold=True, color=POS))
    f.append(arrow(cx + 90, ly + 46, cx + 90, ly + 58, color=INK, sw=2.4))

    render(os.path.join(IMG, "anatomy.svg"), W, H, *f)


# ── 2. Пастка 4 ніжок: дві внутрішні пари вже з'єднані ────────────────────────
def fig_legs():
    W, H = 900, 520
    f = [text(W / 2, 32, "Пастка чотирьох ніжок: це НЕ чотири окремі виводи, а дві пари",
              size=16, bold=True)]

    # корпус кнопки по центру
    cx, cy = W / 2, 210
    bw, bh = 200, 150
    f.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill="#eef4f0", stroke=INK, sw=2.2, rx=12))
    f.append(text(cx, cy - bh / 2 - 14, "тактильна кнопка (вид зверху)", size=12, bold=True, color=MUTED))

    # чотири ніжки в кутах
    off_x, off_y = bw / 2 + 46, bh / 2 - 6
    corners = {
        "1": (cx - off_x, cy - off_y),
        "2": (cx - off_x, cy + off_y),
        "4": (cx + off_x, cy - off_y),
        "3": (cx + off_x, cy + off_y),
    }
    # відведення від корпусу до ніжок
    edges = {"1": (cx - bw / 2, cy - off_y), "2": (cx - bw / 2, cy + off_y),
             "4": (cx + bw / 2, cy - off_y), "3": (cx + bw / 2, cy + off_y)}
    for lab, (x, y) in corners.items():
        ex, ey = edges[lab]
        f.append(line(ex, ey, x, y, color=INK, sw=2.2))
        f.append(circle(x, y, 8, fill=BG, stroke=INK, sw=2.2))
        f.append(text(x, y + 5, lab, size=13, bold=True, color=INK))

    # ЛІВА пара (1,2) вже з'єднана металом усередині — зелена дужка
    lx = cx - off_x
    f.append(line(lx - 26, corners["1"][1], lx - 26, corners["2"][1], color=FIELD, sw=3))
    f.append(line(lx - 26, corners["1"][1], lx - 8, corners["1"][1], color=FIELD, sw=3))
    f.append(line(lx - 26, corners["2"][1], lx - 8, corners["2"][1], color=FIELD, sw=3))
    f.append(text(lx - 60, cy + 4, "1 і 2 —\nодин вузол", size=11, bold=True, color=FIELD, anchor="middle"))

    # ПРАВА пара (3,4) вже з'єднана — зелена дужка
    rx = cx + off_x
    f.append(line(rx + 26, corners["4"][1], rx + 26, corners["3"][1], color=FIELD, sw=3))
    f.append(line(rx + 26, corners["4"][1], rx + 8, corners["4"][1], color=FIELD, sw=3))
    f.append(line(rx + 26, corners["3"][1], rx + 8, corners["3"][1], color=FIELD, sw=3))
    f.append(text(rx + 60, cy + 4, "3 і 4 —\nодин вузол", size=11, bold=True, color=FIELD, anchor="middle"))

    # натиск замикає ліву пару з правою — червоний місток по центру (розімкнений)
    f.append(text(cx, cy + 6, "натиск\nзамикає\nліву пару\nз правою", size=10.5, bold=True, color=POS))

    # висновок рамкою (широкою, з запасом)
    b, _, _ = textbox(W / 2, 430,
                      "Усередині 1–2 вже спаяні між собою, і 3–4 теж. Кнопка замикає ліву пару з правою.\n"
                      "БЕЗПЕЧНО брати по діагоналі (напр. 1 і 3): ці дві точно з різних пар.\n"
                      "Якщо взяти 1 і 2 (одна пара) — коло замкнене ЗАВЖДИ, натиск нічого не змінить.",
                      size=11, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "legs.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: кнопка між GPIO і GND, підтяжка, натиск = LOW ────
def fig_wiring():
    W, H = 900, 480
    f = [text(W / 2, 32, "Підключення: кнопка між GPIO і GND, внутрішня підтяжка → натиск = LOW",
              size=15.5, bold=True)]

    # плата ліворуч
    bx, by, bw, bh = 90, 110, 230, 250
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=12))
    f.append(text(bx + bw / 2, by + 26, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    # пін GPIO і GND
    gpio_y = by + 90
    gnd_y = by + 180
    f.append(circle(bx + bw, gpio_y, 6, fill=BG, stroke=FIELD, sw=2.4))
    f.append(text(bx + bw - 14, gpio_y + 4, "GPIO", size=11, bold=True, color=FIELD, anchor="end"))
    f.append(circle(bx + bw, gnd_y, 6, fill=BG, stroke=NEG, sw=2.4))
    f.append(text(bx + bw - 14, gnd_y + 4, "GND", size=11, bold=True, color=NEG, anchor="end"))

    # внутрішня підтяжка (INPUT_PULLUP) — усередині плати, від GPIO до +
    f.append(rect(bx + 40, gpio_y - 8, 16, 16, fill=BG, stroke=POS, sw=1.6, rx=3))
    f.append(line(bx + 48, gpio_y - 8, bx + 48, gpio_y - 34, color=POS, sw=1.6))
    f.append(text(bx + 48, gpio_y - 40, "+3.3/5 В", size=9.5, bold=True, color=POS))
    f.append(line(bx + 48, gpio_y, bx + 40, gpio_y, color=INK, sw=1.4))
    f.append(text(bx + 100, gpio_y - 22, "внутрішня\nпідтяжка", size=9, color=POS))

    # кнопка праворуч
    kx, ky = 560, by + 70
    f.append(rect(kx, ky, 120, 120, fill="#eef4f0", stroke=INK, sw=2.0, rx=12))
    f.append(text(kx + 60, ky - 14, "кнопка", size=12, bold=True, color=MUTED))
    # два виводи кнопки (по діагоналі — з різних пар)
    f.append(circle(kx, ky + 24, 6, fill=BG, stroke=INK, sw=2))
    f.append(circle(kx + 120, ky + 96, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(kx + 60, ky + 66, "1 ↔ 3\n(діагональ)", size=10, bold=True, color=INK))

    # дроти: GPIO → вивід1 кнопки ; вивід3 → GND
    f.append(line(bx + bw + 6, gpio_y, kx - 6, ky + 24, color=FIELD, sw=2.2))
    f.append(line(kx + 120 + 6, ky + 96, kx + 120 + 40, ky + 96, color=NEG, sw=2.2))
    f.append(line(kx + 120 + 40, ky + 96, kx + 120 + 40, gnd_y, color=NEG, sw=2.2))
    f.append(line(kx + 120 + 40, gnd_y, bx + bw + 6, gnd_y, color=NEG, sw=2.2))

    # стан ліній
    b, _, _ = textbox(W / 2, 420,
                      "Один вивід кнопки — на GPIO, протилежний (по діагоналі) — на GND. Живлення й землі кнопці НЕ треба.\n"
                      "Вмикаємо внутрішню підтяжку (INPUT_PULLUP): у спокої пін тримається у «1» (HIGH),\n"
                      "натиск замикає його на землю → пін падає в «0» (LOW). Отже: натиснуто = LOW, відпущено = HIGH.",
                      size=10.5, fill="#fff8e6", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_legs()
    fig_wiring()
    print("tactile-buttons figs done ->", IMG)
