# -*- coding: utf-8 -*-
"""Фігури до теми «Захист від блискавки» (курс embedded / Основи).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Головний принцип: дати заряду свій шлях повз чутливе ──────────────────
def fig_controlled_path():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 26, "Захист — це не стіна, а кращий шлях для струму", size=17, bold=True))

    # хмара / джерело кидка згори
    p.append(circle(W / 2, 70, 30, fill="#eef0f2", stroke=MUTED, sw=1.5))
    p.append(text(W / 2, 60, "кидок", size=12, color=MUTED))
    p.append(text(W / 2, 76, "напруги", size=12, color=MUTED))
    # стрілка вниз від джерела
    p.append(arrow(W / 2, 100, W / 2, 138, color=POS, sw=2.4))

    # земля знизу — суцільна смуга
    gy = 372
    p.append(line(40, gy, W - 40, gy, color=INK, sw=3))
    for gx in range(70, W - 50, 46):
        p.append(line(gx, gy, gx - 12, gy + 14, color=INK, sw=1.4))
    p.append(text(W - 90, gy + 30, "земля (нуль)", size=12, color=MUTED))

    # ── лівий бік: БЕЗ захисту, струм іде крізь чип ──
    lx = 210
    p.append(fitbox(lx - 95, 150, 190, 26, "без захисту", size=13, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))
    # чутливий чип
    chip = rect(lx - 45, 230, 90, 60, fill="#fdecea", stroke=POS, sw=2)
    p.append(chip)
    p.append(text(lx, 256, "чутливий", size=12, color=POS))
    p.append(text(lx, 272, "чип", size=12, color=POS, bold=True))
    # шлях крізь чип (червоний зигзаг)
    p.append(arrow(W / 2 - 4, 150, lx, 226, color=POS, sw=2.4))
    p.append(line(lx, 290, lx, gy, color=POS, sw=2.4))
    # «вибух»
    p.append(text(lx + 60, 262, "✺", size=26, color=POS))
    p.append(fitbox(lx - 92, 312, 184, 24, "весь струм — крізь чип",
                    size=12, color=POS, fill=BG, stroke=POS))

    # ── правий бік: ІЗ захистом, струм відведено повз чип ──
    rx = 560
    p.append(fitbox(rx - 95, 150, 190, 26, "із захистом", size=13, bold=True,
                    fill="#eafaf0", stroke=FIELD, color="#1e7e44"))
    # розрядник-шунт (короткий шлях у землю)
    p.append(arrow(W / 2 + 4, 150, rx - 18, 196, color=FIELD, sw=2.4))
    sb = rect(rx - 60, 196, 64, 40, fill="#eafaf0", stroke=FIELD, sw=2)
    p.append(sb)
    p.append(text(rx - 28, 213, "захис-", size=11, color="#1e7e44"))
    p.append(text(rx - 28, 226, "ник", size=11, color="#1e7e44", bold=True))
    # товстий зелений шлях у землю
    p.append(line(rx - 28, 236, rx - 28, gy, color=FIELD, sw=4.5))
    p.append(arrow(rx - 28, 300, rx - 28, gy - 4, color=FIELD, sw=4.5))
    # чип збоку — лишається цілим
    p.append(rect(rx + 26, 248, 78, 52, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(rx + 65, 270, "чип", size=12, color="#1e7e44", bold=True))
    p.append(text(rx + 65, 286, "цілий", size=11, color="#1e7e44"))
    # ледь-ледь у чип
    p.append(line(rx - 26, 250, rx + 24, 264, color=MUTED, sw=1.2, dash="3,3"))
    p.append(text(rx + 6, 244, "крихта", size=10, color=MUTED))
    p.append(fitbox(rx - 96, 312, 192, 24, "струм — повз чип у землю",
                    size=12, color="#1e7e44", fill=BG, stroke=FIELD))

    render(os.path.join(IMG, "controlled-path.svg"), W, H, *p)


# ── 2. Каскад захисту: грубий → середній → тонкий ───────────────────────────
def fig_cascade():
    W, H = 800, 360
    p = []
    p.append(text(W / 2, 26, "Каскад: щабель за щаблем збивати кидок усе нижче", size=17, bold=True))

    # лінія вхід → … → чип
    y = 150
    xin = 70
    p.append(text(xin, y - 40, "вхід", size=12, color=MUTED))
    p.append(text(xin, y - 24, "8 кВ", size=13, color=POS, bold=True))
    p.append(arrow(xin, y, xin + 50, y, color=POS, sw=2.4))

    stages = [
        (175, "GDT", "грубий", "сотні В", "кА", POS),
        (400, "MOV", "середній", "десятки В", "сотні А", "#d98a00"),
        (625, "TVS", "тонкий", "одиниці В", "десятки А", FIELD),
    ]
    prev_x = xin + 50
    levels = ["8 кВ", "≈700 В", "≈40 В", "≈6 В"]
    for i, (cx, name, role, clamp, cur, col) in enumerate(stages):
        # послідовний опір між щаблями (крім першого, що одразу після входу)
        if i > 0:
            p.append(rect(prev_x + 10, y - 9, 44, 18, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=4))
            p.append(text(prev_x + 32, y + 5, "R/L", size=11, color=MUTED))
            p.append(arrow(prev_x, y, prev_x + 10, y, color=INK, sw=1.8))
            p.append(arrow(prev_x + 54, y, cx - 28, y, color=INK, sw=1.8))
        else:
            p.append(arrow(prev_x, y, cx - 28, y, color=INK, sw=1.8))
        # блок-щабель
        p.append(rect(cx - 28, y - 26, 56, 52, fill="#ffffff", stroke=col, sw=2.2))
        p.append(text(cx, y - 4, name, size=14, color=col, bold=True))
        p.append(text(cx, y + 14, role, size=10, color=MUTED))
        # відведення в землю
        p.append(line(cx, y + 26, cx, y + 70, color=col, sw=3))
        p.append(arrow(cx, y + 55, cx, y + 70, color=col, sw=3))
        # підпис щабля
        p.append(fitbox(cx - 60, y - 96, 120, 44,
                        "тримає " + cur + "\nпускає далі " + clamp,
                        size=10, color=col, fill=BG, stroke=col))
        prev_x = cx + 28

    # чип
    p.append(arrow(prev_x, y, prev_x + 36, y, color=FIELD, sw=2.4))
    p.append(rect(prev_x + 36, y - 26, 80, 52, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(prev_x + 76, y - 2, "чип", size=13, color="#1e7e44", bold=True))
    p.append(text(prev_x + 76, y + 15, "5 В цілий", size=10, color="#1e7e44"))

    # земляна шина
    gy = y + 70
    p.append(line(120, gy, prev_x + 30, gy, color=INK, sw=3))
    for gx in range(150, int(prev_x), 50):
        p.append(line(gx, gy, gx - 10, gy + 12, color=INK, sw=1.3))
    p.append(text(prev_x + 5, gy + 26, "спільна земля", size=11, color=MUTED, anchor="end"))

    # шкала «скільки лишилось» унизу
    by = gy + 60
    p.append(text(W / 2, by - 16, "напруга, що доходить далі, падає на кожному щаблі:",
                  size=12, color=MUTED))
    xs = [110, 320, 540, 740]
    for i, (xx, lv) in enumerate(zip(xs, levels)):
        col = [POS, POS, "#d98a00", FIELD][i]
        p.append(circle(xx, by + 18, 6, fill=col, stroke=col))
        p.append(text(xx, by + 42, lv, size=12, color=col, bold=True))
        if i < len(xs) - 1:
            p.append(arrow(xx + 14, by + 18, xs[i + 1] - 14, by + 18, color=MUTED, sw=1.5))

    render(os.path.join(IMG, "protection-cascade.svg"), W, H, *p)


# ── 3. Спільний імпеданс землі: чому «одна земля» бреше під час кидка ────────
def fig_earthing():
    W, H = 780, 410
    p = []
    p.append(text(W / 2, 26, "Спільна земля під кидком — уже не одне число", size=17, bold=True))

    # верхній блок: пояснення V = I·Z на дроті землі
    p.append(text(W / 2, 56, "великий струм кидка × опір дроту землі = різниця напруг там, де чекав нуль",
                  size=12, color=MUTED))

    # горизонтальний «земляний» провідник із індуктивністю/опором
    y = 130
    p.append(line(80, y, W - 80, y, color=INK, sw=4))
    p.append(text(80, y - 12, "точка A", size=12, color=INK))
    p.append(text(W - 80, y - 12, "точка B", size=12, color=INK, anchor="end"))
    # кидок струму тече по землі A→B
    p.append(arrow(120, y - 30, 300, y - 30, color=POS, sw=3))
    p.append(text(210, y - 40, "I кидка (десятки А, нс)", size=12, color=POS, bold=True))
    # позначка опору/індуктивності ділянки
    p.append(rect(W / 2 - 40, y - 9, 80, 18, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=4))
    p.append(text(W / 2, y + 5, "R + L дроту", size=11, color=MUTED))
    # різниця потенціалів
    p.append(text(110, y + 28, "тут «0»", size=12, color="#1e7e44"))
    p.append(text(W - 110, y + 28, "тут уже +сотні В", size=12, color=POS, anchor="end"))

    # два вузли, що сидять на РІЗНІЙ землі під час кидка
    p.append(circle(110, y, 6, fill="#1a1a1a"))
    p.append(circle(W - 110, y, 6, fill="#1a1a1a"))

    # ── низ: рішення — звести в одну точку (зірка / бондинг) ──
    by = 250
    p.append(line(40, by + 120, W - 40, by + 120, color=INK, sw=3))  # справжня земля
    for gx in range(70, W - 50, 46):
        p.append(line(gx, by + 120, gx - 10, by + 132, color=INK, sw=1.3))

    # одна точка зведення
    starx = W / 2
    stary = by + 120
    p.append(circle(starx, stary, 9, fill="#eafaf0", stroke=FIELD, sw=2.4))
    p.append(text(starx, stary + 34, "одна точка зведення (бондинг)", size=12,
                  color="#1e7e44", bold=True))

    # три споживачі сходяться променями в одну точку
    nodes = [(starx - 230, by + 20, "блок 1"),
             (starx, by, "блок 2"),
             (starx + 230, by + 20, "блок 3")]
    for nx, ny, lab in nodes:
        p.append(rect(nx - 48, ny - 18, 96, 36, fill="#eafaf0", stroke=FIELD, sw=1.8))
        p.append(text(nx, ny + 5, lab, size=12, color="#1e7e44"))
        p.append(line(nx, ny + 18, starx, stary, color=FIELD, sw=2.6))
    p.append(text(W / 2, by - 36, "усі землі сходяться в ОДНІЙ точці — і піднімаються разом, "
                  "лишаючись між собою на нулі", size=12, color="#1e7e44"))

    render(os.path.join(IMG, "earthing-bonding.svg"), W, H, *p)


if __name__ == "__main__":
    fig_controlled_path()
    fig_cascade()
    fig_earthing()
    print("OK: 3 figures written to", IMG)
