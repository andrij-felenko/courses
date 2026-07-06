# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def chip(cx, cy, label, fill, stroke, w=150, h=40, size=13):
    x, y = cx - w / 2, cy - h / 2
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=8)
            + text(cx, cy + size * 0.35, label, size=size, color=stroke, bold=True))


# ── 1. Один вибір тягне два атрибути в різні боки ─────────────────────────────
def fig_tension():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 32, "Один вибір — і два атрибути тягнуться в різні боки", size=16, bold=True))

    # центральне рішення
    dec = chip(W / 2, 150, "кешувати відповіді", "#eef7ef", FIELD, w=210, h=46, size=14)
    p.append(dec)
    p.append(text(W / 2, 186, "(архітектурне рішення)", size=10.5, color=MUTED, italic=True))

    # ліворуч — виграш
    p.append(chip(160, 150, "швидкість ↑", "#eaf6ef", FIELD, w=170, h=44, size=14))
    p.append(text(160, 200, "відповідь за 5 мс", size=11, color=FIELD, bold=True))
    p.append(text(160, 220, "замість 200 мс", size=11, color=FIELD))
    p.append(arrow(W / 2 - 108, 150, 250, 150, color=FIELD, sw=2.2))

    # праворуч — програш
    p.append(chip(600, 150, "свіжість ↓", "#fdecea", POS, w=170, h=44, size=14))
    p.append(text(600, 200, "дані можуть", size=11, color=POS, bold=True))
    p.append(text(600, 220, "відставати на секунди", size=11, color=POS))
    p.append(arrow(W / 2 + 108, 150, 510, 150, color=POS, sw=2.2))

    # підсумок
    p.append(rect(70, 262, 620, 96, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 288, "Немає «просто кращого» рішення — є вибір, ЩО з чим міняємо.",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 312, "Ремесло архітектора — назвати обидва боки числом і вирішити свідомо,",
                  size=11, color=INK))
    p.append(text(W / 2, 332, "а не відкрити відставання даних випадково у проді.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "tension.svg"), W, H, *p)


# ── 2. Анатомія сценарію: розмите «має бути швидко» → перевірне ───────────────
def fig_scenario():
    W, H = 860, 500
    p = []
    p.append(text(W / 2, 30, "Сценарій перетворює гасло на перевірну вимогу", size=16, bold=True))

    # верх — розмите гасло
    p.append(rect(230, 50, 400, 46, fill="#fdecea", stroke=POS, sw=1.6, rx=10))
    p.append(text(W / 2, 79, "«система має бути швидкою»  — не перевіриш", size=13, color=POS, bold=True))
    p.append(arrow(W / 2, 100, W / 2, 128, color=INK, sw=2))

    # шість частин сценарію — рядки таблиці
    rows = [
        ("джерело", "1000 користувачів у пік розпродажу", "хто/що створює навантаження"),
        ("подразник", "надсилають запит кошика", "яка саме подія"),
        ("артефакт", "сервіс оформлення", "над чим діє"),
        ("умови", "звичайне навантаження, БД жива", "у якому стані системи"),
        ("відгук", "запит опрацьовано, кошик збережено", "що система має зробити"),
        ("міра відгуку", "95-й перцентиль ≤ 300 мс", "як виміряти успіх — ЧИСЛО"),
    ]
    x0, y0 = 70, 138
    cw = [140, 330, 320]
    rh = 42
    hdr = ["частина сценарію", "приклад (оформлення замовлення)", "що вона фіксує"]
    # шапка
    cx = x0
    for j, htxt in enumerate(hdr):
        p.append(rect(cx, y0, cw[j], rh, fill="#eef1f4", stroke=MUTED, sw=1.3, rx=0))
        p.append(text(cx + cw[j] / 2, y0 + 26, htxt, size=11.5, color=INK, bold=True))
        cx += cw[j]
    # тіло
    for i, (a, b, c) in enumerate(rows):
        ry = y0 + rh + i * rh
        last = (i == len(rows) - 1)
        fillc = "#eaf6ef" if last else BG
        strc = FIELD if last else "#d7dbe0"
        cx = x0
        for j, cell in enumerate((a, b, c)):
            p.append(rect(cx, ry, cw[j], rh, fill=fillc if j == 0 or last else BG,
                          stroke=strc, sw=1.2, rx=0))
            col = FIELD if last else (INK if j < 2 else MUTED)
            bold = (j == 0) or last
            it = (j == 2 and not last)
            p.append(text(cx + cw[j] / 2, ry + 26, cell, size=11, color=col, bold=bold, italic=it))
            cx += cw[j]

    p.append(text(W / 2, y0 + rh * 7 + 30,
                  "Остання клітина — число, яке або досягнуто, або ні. Оце й робить атрибут перевірним.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "scenario.svg"), W, H, *p)


# ── 3. Ланцюг міркування архітектора ─────────────────────────────────────────
def fig_reasoning():
    W, H = 880, 300
    p = []
    p.append(text(W / 2, 30, "Ланцюг рішення: від турботи стейкхолдера до свідомого компромісу", size=15, bold=True))

    ky = 130
    boxes = [
        ("турбота", "«у пік не має\nгальмувати»", "#eef1f4", MUTED),
        ("→ атрибут", "продуктивність", "#eaf6ef", FIELD),
        ("→ сценарій", "p95 ≤ 300 мс\nпри 1000 корист.", "#eaf0fd", NEG),
        ("→ тактика", "кеш + черга\nна запис", "#fef6e9", "#8a6508"),
        ("→ компроміс", "свіжість ↓,\nскладність ↑", "#fdecea", POS),
    ]
    n = len(boxes)
    bw, gap = 148, 20
    total = n * bw + (n - 1) * gap
    x = (W - total) / 2 + bw / 2
    centers = []
    for i, (tag, body, fc, sc) in enumerate(boxes):
        centers.append(x)
        p.append(text(x, ky - 44, tag, size=12, color=sc, bold=True))
        bx = x - bw / 2
        p.append(rect(bx, ky - 28, bw, 62, fill=fc, stroke=sc, sw=1.6, rx=8))
        p.append(mtext(x, ky - 2, body, size=12, color=sc, bold=True))
        x += bw + gap
    for i in range(n - 1):
        p.append(arrow(centers[i] + bw / 2 + 1, ky + 3, centers[i + 1] - bw / 2 - 1, ky + 3,
                       color=INK, sw=2))

    p.append(rect(70, 222, W - 140, 60, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 246, "Кожна ланка витікає з попередньої. Пропустиш будь-яку — і рішення",
                  size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 268, "стає смаком, а не інженерією: нема числа, нема названого боку, який ти віддав.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "reasoning.svg"), W, H, *p)


if __name__ == "__main__":
    fig_tension()
    fig_scenario()
    fig_reasoning()
    print("OK: figs written to", OUT)
