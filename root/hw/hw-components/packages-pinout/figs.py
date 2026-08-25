# -*- coding: utf-8 -*-
"""Фігури до теми «Корпуси й розпіновка». svgkit імпортуємо зі scripts/, НЕ
переписуємо (AUTHORING §5). Підписи — у Markdown, не в SVG: тут лише картинки.
Імена файлів — slug-описові (не fig-XX); нумерації в book/ немає.

Запуск:  python figs.py  → пише в ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#e0a32e"   # припій / фасування
DARK = "#2a2a2a"   # тіло корпусу
PAD  = "#bdbdbd"   # металевий вивід


# ════════════════════════════════════════════════════════════════════════════
# 1. THT проти SMD — два світи монтажу
# ════════════════════════════════════════════════════════════════════════════
def fig_tht_smd():
    W, H = 700, 300
    f = []

    # ── ЛІВА панель: THT ──
    f.append(rect(40, 50, 300, 220, fill=BG, stroke="#c9d3dc", sw=1.4))
    f.append(text(190, 74, "THT — у наскрізні отвори", size=13, bold=True))
    # плата
    f.append(rect(70, 206, 240, 12, fill="#cfe0c8", stroke=FIELD, sw=1.2, rx=0))
    f.append(text(300, 214, "плата", size=9, color=FIELD, anchor="end"))
    # тіло корпусу
    f.append(rect(110, 110, 160, 64, fill=DARK, stroke="#000", sw=1.5, rx=4))
    f.append(text(190, 148, "DIP", size=14, color="#fff", bold=True))
    # ніжки крізь плату
    for x in (132, 170, 208, 246):
        f.append(line(x, 110, x, 206, color="#777", sw=6))          # тіло ніжки
        f.append(line(x, 206, x, 236, color=INK, sw=2.6))           # хвіст під платою
    f.append(text(190, 256, "ніжки прошивають плату наскрізь", size=10, color=INK))
    f.append(text(190, 270, "міцно, легко паяти вручну", size=10, color=MUTED))

    # ── ПРАВА панель: SMD ──
    f.append(rect(360, 50, 300, 220, fill=BG, stroke="#c9d3dc", sw=1.4))
    f.append(text(510, 74, "SMD — на поверхню", size=13, bold=True))
    f.append(rect(400, 196, 220, 12, fill="#cfe0c8", stroke=FIELD, sw=1.2, rx=0))
    f.append(text(620, 204, "плата", size=9, color=FIELD, anchor="end"))
    f.append(rect(444, 150, 132, 46, fill=DARK, stroke="#000", sw=1.5, rx=4))
    f.append(text(510, 178, "SOIC", size=12, color="#fff", bold=True))
    # «крильця» лежать на майданчиках припою зверху
    for x in (456, 496, 536):
        f.append(rect(x, 196, 24, 6, fill=GOLD, stroke="#a07a16", sw=1))  # майданчик припою
        f.append(line(x + 12, 188, x + 12, 196, color=PAD, sw=4))         # коротка ніжка
    f.append(text(510, 246, "контакти лежать на майданчиках зверху", size=10, color=INK))
    f.append(text(510, 260, "дрібно, компактно, під автоскладання", size=10, color=MUTED))

    render(os.path.join(OUT, "tht-smd.svg"), W, H, *f,
           title="Вивідний монтаж (THT) і поверхневий (SMD)")


# ════════════════════════════════════════════════════════════════════════════
# 2. Галерея корпусів на одну шкалу
# ════════════════════════════════════════════════════════════════════════════
def fig_package_zoo():
    W, H = 720, 320
    f = []
    base = 250                       # спільна лінія «низу» корпусів

    def chip(cx, w, h, label, sub):
        x, y = cx - w / 2, base - h
        f.append(rect(x, y, w, h, fill=DARK, stroke="#000", sw=1.4, rx=4))
        # позначка 1-го виводу
        f.append(circle(x + 7, y + 7, 2.4, fill="#eee", stroke="#999", sw=0.8))
        f.append(text(cx, base - h / 2 + 4, label, size=11, color="#fff", bold=True))
        f.append(text(cx, base + 18, sub, size=9.5, color=MUTED))

    # DIP — великий, з довгими ніжками вниз
    f.append(text(110, 70, "DIP", size=12, bold=True, color=INK))
    dipx, dipw, diph = 110, 120, 56
    f.append(rect(dipx - dipw / 2, base - diph, dipw, diph, fill=DARK, stroke="#000", sw=1.4, rx=4))
    f.append(circle(dipx - dipw / 2 + 8, base - diph + 8, 2.6, fill="#eee", stroke="#999", sw=0.8))
    f.append(text(dipx, base - diph / 2 + 4, "DIP", size=11, color="#fff", bold=True))
    for i in range(4):
        xx = dipx - dipw / 2 + 16 + i * 28
        f.append(line(xx, base, xx, base + 22, color=INK, sw=3))
    f.append(text(dipx, base + 40, "вивідний, 2.54 мм", size=9.5, color=MUTED))

    chip(290, 88, 34, "SOIC", "SMD, ще рукою")
    chip(410, 30, 22, "SOT-23", "три виводи")

    # TQFP — квадрат із ніжками по 4 боках
    qx, qs = 530, 56
    f.append(text(qx, 70, "TQFP", size=12, bold=True, color=INK))
    f.append(rect(qx - qs / 2, base - qs, qs, qs, fill=DARK, stroke="#000", sw=1.4, rx=4))
    f.append(circle(qx - qs / 2 + 8, base - qs + 8, 2.6, fill="#eee", stroke="#999", sw=0.8))
    for i in range(4):
        off = -qs / 2 + 12 + i * 11
        f.append(line(qx + off, base - qs - 7, qx + off, base - qs, color=PAD, sw=3))  # верх
        f.append(line(qx + off, base, qx + off, base + 7, color=PAD, sw=3))            # низ
        f.append(line(qx - qs / 2 - 7, base - qs + 12 + i * 11, qx - qs / 2, base - qs + 12 + i * 11, color=PAD, sw=3))
        f.append(line(qx + qs / 2, base - qs + 12 + i * 11, qx + qs / 2 + 7, base - qs + 12 + i * 11, color=PAD, sw=3))
    f.append(text(qx, base + 18, "ніжки по 4 боках", size=9.5, color=MUTED))

    # QFN — квадрат, контакти знизу (пунктир)
    nx, ns = 640, 40
    f.append(text(nx, 70, "QFN", size=12, bold=True, color=INK))
    f.append(rect(nx - ns / 2, base - ns, ns, ns, fill=DARK, stroke="#000", sw=1.4, rx=4))
    f.append(circle(nx - ns / 2 + 7, base - ns + 7, 2.4, fill="#eee", stroke="#999", sw=0.8))
    for i in range(3):
        off = -ns / 2 + 10 + i * 10
        f.append(rect(nx + off - 2, base - 4, 6, 4, fill=PAD, stroke="#777", sw=0.6, rx=0))  # контакти знизу
    f.append(text(nx, base + 18, "контакти знизу", size=9.5, color=POS))

    render(os.path.join(OUT, "package-zoo.svg"), W, H, *f,
           title="Поширені корпуси в одному масштабі")


# ════════════════════════════════════════════════════════════════════════════
# 3. Перша ніжка: ключ
# ════════════════════════════════════════════════════════════════════════════
def fig_pin1():
    W, H = 700, 300
    f = []

    # ── DIP із виїмкою ──
    f.append(text(180, 70, "DIP: виїмка-«ключ»", size=12, bold=True))
    bx, by, bw, bh = 110, 90, 140, 130
    f.append(rect(bx, by, bw, bh, fill=DARK, stroke="#000", sw=1.5, rx=6))
    # півкругла виїмка зверху
    f.append('<path d="M%.0f %.0f a 12 12 0 0 0 24 0" fill="%s" stroke="#000" stroke-width="1.2"/>'
             % (bx + bw / 2 - 12, by, BG))
    # ніжки + номери, проти годинникової стрілки від лівої-верхньої
    nums_left = [1, 2, 3, 4]
    nums_right = [8, 7, 6, 5]
    for i in range(4):
        yy = by + 24 + i * 28
        f.append(line(bx - 16, yy, bx, yy, color=PAD, sw=4))
        f.append(line(bx + bw, yy, bx + bw + 16, yy, color=PAD, sw=4))
        f.append(text(bx - 24, yy + 4, str(nums_left[i]), size=11, color=INK, anchor="end",
                      bold=(nums_left[i] == 1)))
        f.append(text(bx + bw + 24, yy + 4, str(nums_right[i]), size=11, color=INK, anchor="start"))
    # підсвітити 1-й вивід
    f.append(circle(bx - 8, by + 24, 7, fill="none", stroke=POS, sw=2))
    f.append(text(bx + bw / 2, by + bh + 24, "ніжка 1 — ліворуч від виїмки", size=10, color=POS, bold=True))
    # стрілка напрямку (проти годинникової)
    f.append('<path d="M%.0f %.0f a 40 40 0 0 0 -34 -20" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (bx + bw / 2 + 30, by + 40, NEG))

    # ── SMD з крапкою/скошеним кутом ──
    f.append(text(520, 70, "SMD: крапка чи скіс", size=12, bold=True))
    sx, sy, ss = 460, 100, 110
    f.append(rect(sx, sy, ss, ss, fill=DARK, stroke="#000", sw=1.5, rx=6))
    # скошений кут
    f.append('<path d="M%.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="%s" stroke="#000" stroke-width="1"/>'
             % (sx, sy + 22, sx, sy, sx + 22, sy, BG))
    # втиснута крапка біля 1-го виводу
    f.append(circle(sx + 16, sy + 16, 4.5, fill="#111", stroke="#555", sw=1))
    f.append(circle(sx + 16, sy + 16, 9, fill="none", stroke=POS, sw=2))
    f.append(text(sx + ss / 2, sy + ss + 24, "крапка/скіс у кутку 1-го виводу", size=10, color=POS, bold=True))

    f.append(text(W / 2, 282, "Нумерація — проти годинникової стрілки. Корпус малюють ВИДОМ ЗВЕРХУ.",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "pin1.svg"), W, H, *f,
           title="Де перша ніжка")


# ════════════════════════════════════════════════════════════════════════════
# 4. Карта розпіновки здвоєного ОП
# ════════════════════════════════════════════════════════════════════════════
def fig_pinout():
    W, H = 700, 330
    f = []
    bx, by, bw, bh = 250, 70, 200, 200
    f.append(rect(bx, by, bw, bh, fill="#f0f2f5", stroke=INK, sw=1.8, rx=6))
    # виїмка зверху
    f.append('<path d="M%.0f %.0f a 13 13 0 0 0 26 0" fill="%s" stroke="%s" stroke-width="1.4"/>'
             % (bx + bw / 2 - 13, by, BG, INK))

    # 8 виводів здвоєного ОП (вид зверху), 1..4 ліворуч, 8..5 праворуч
    left = [("1", "OUT1", INK), ("2", "IN1−", NEG), ("3", "IN1+", POS), ("4", "V−", NEG)]
    right = [("8", "V+", POS), ("7", "OUT2", INK), ("6", "IN2−", NEG), ("5", "IN2+", POS)]
    for i, (n, lab, col) in enumerate(left):
        yy = by + 34 + i * 42
        f.append(line(bx - 22, yy, bx, yy, color=PAD, sw=5))
        f.append(text(bx - 28, yy - 4, n, size=10, color=MUTED, anchor="end"))
        f.append(text(bx + 12, yy + 4, lab, size=12, color=col, anchor="start", bold=True))
    for i, (n, lab, col) in enumerate(right):
        yy = by + 34 + i * 42
        f.append(line(bx + bw, yy, bx + bw + 22, yy, color=PAD, sw=5))
        f.append(text(bx + bw + 28, yy - 4, n, size=10, color=MUTED, anchor="start"))
        f.append(text(bx + bw - 12, yy + 4, lab, size=12, color=col, anchor="end", bold=True))

    f.append(circle(bx - 11, by + 34, 8, fill="none", stroke=INK, sw=2))   # 1-й вивід
    f.append(text(bx + bw / 2, by + bh / 2, "2× ОП", size=14, color=INK, bold=True))

    # пояснення-легенда
    f.append(text(120, 110, "«+/−» = ВХОДИ", size=12, color=POS, bold=True))
    f.append(text(120, 130, "(не живлення!)", size=10, color=MUTED))
    f.append(text(580, 110, "живлення V+/V−", size=12, color=NEG, bold=True))
    f.append(text(580, 130, "по діагоналі кутів", size=10, color=MUTED))
    # діагональ V+ (8, верх-право) ↔ V− (4, низ-ліво)
    f.append(line(bx + bw + 4, by + 34, bx - 4, by + 34 + 3 * 42, color=FIELD, sw=1.6, dash="5,4"))
    f.append(text(bx + bw / 2 + 30, by + bh - 8, "діагональ живлення", size=9.5, color=FIELD, anchor="middle"))

    render(os.path.join(OUT, "pinout.svg"), W, H, *f,
           title="Розпіновка здвоєного ОП (вид зверху)")


# ════════════════════════════════════════════════════════════════════════════
# 5. Маркування: повне й кодоване
# ════════════════════════════════════════════════════════════════════════════
def fig_marking():
    W, H = 700, 290
    f = []

    # ── великий корпус: усе читається ──
    f.append(text(180, 66, "Великий корпус (DIP)", size=12, bold=True))
    f.append(rect(70, 90, 220, 120, fill=DARK, stroke="#000", sw=1.5, rx=8))
    f.append(text(180, 128, "LM358N", size=20, color="#fff", bold=True))
    f.append(text(180, 154, "TI  ◆", size=12, color="#cfcfcf"))
    f.append(text(180, 180, "2417", size=13, color=GOLD, bold=True))
    f.append(text(180, 232, "повна назва + логотип + дата-код", size=10, color=INK))
    f.append(text(180, 248, "читається прямо", size=10, color=FIELD, bold=True))

    # ── дрібний SMD: код-загадка ──
    f.append(text(520, 66, "Крихітний SMD (SOT-23)", size=12, bold=True))
    f.append(rect(470, 110, 100, 70, fill=DARK, stroke="#000", sw=1.5, rx=6))
    f.append(text(520, 152, "A7W", size=22, color="#fff", bold=True))
    f.append(text(520, 206, "повний номер не влазить", size=10, color=INK))
    f.append(text(520, 222, "2–3 символи — код-загадка", size=10, color=POS, bold=True))
    f.append(text(520, 240, "шукати в таблиці маркування", size=10, color=MUTED))

    render(os.path.join(OUT, "marking.svg"), W, H, *f,
           title="Маркування: повне проти кодованого")


# ════════════════════════════════════════════════════════════════════════════
# 6. Код замовлення: розклад на частини
# ════════════════════════════════════════════════════════════════════════════
def fig_ordering():
    W, H = 700, 290
    f = []
    parts = [
        ("LM358", "сімейство",            "#eef2f7", INK,   160),
        ("I",     "темп. сорт (−40…85)",  "#eef6ef", FIELD, 56),
        ("D",     "корпус (SOIC)",         "#e9eefb", NEG,   56),
        ("R",     "стрічка/котушка",       "#fff3e0", GOLD,  56),
    ]
    x = 90
    for txt, sub, fill, col, w in parts:
        f.append(rect(x, 88, w, 46, fill=fill, stroke=col, sw=1.8, rx=6))
        f.append(text(x + w / 2, 118, txt, size=17, color=col, bold=True))
        f.append(arrow(x + w / 2, 138, x + w / 2, 168, color=MUTED))
        f.append(text(x + w / 2, 188, sub, size=9, color=INK))
        x += w + 4

    f.append(text(W / 2, 222, "Один суфікс — і це інший корпус, інший сорт чи інша фасовка.",
                  size=11, color=INK))
    f.append(text(W / 2, 246, "Замовиш не той суфікс — приїде той самий чип, але в корпусі, що не влазить.",
                  size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "ordering.svg"), W, H, *f,
           title="Код замовлення: один номер — багато сенсів")


ALL = [fig_tht_smd, fig_package_zoo, fig_pin1, fig_pinout, fig_marking, fig_ordering]

if __name__ == "__main__":
    for fn in ALL:
        fn()
    print("OK figs: %d" % len(ALL))
