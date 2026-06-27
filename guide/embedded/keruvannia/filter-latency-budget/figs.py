# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Бюджет затримки фільтра».
Запуск:  python figs.py   → пише SVG у ./img/
Помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ───────────────────────── 1. Бюджет як віднімання (смуга) ───────────────────
def fig_budget_bar():
    """Дедлайн = сума незмінних ланок + залишок-бюджет фільтра."""
    W, H = 780, 430
    f = []
    f.append(text(W / 2, 30, "Бюджет затримки = дедлайн − незмінні ланки", size=18, bold=True))

    L, R = 70, 710
    full = R - L
    total = 40.0  # мс дедлайн
    # незмінні витрати (мс) + залишок
    segs = [
        ("давач 8", 8.0, "#fde2cf"),
        ("АЦП 1", 1.0, "#fce5d0"),
        ("канал 2", 2.0, "#fde8d4"),
        ("регул. 1", 1.0, "#fceada"),
        ("актуатор 10", 10.0, "#fdeede"),
        ("бюджет фільтра 18", 18.0, "#cdeccd"),
    ]
    ytop = 95
    bh = 66
    x = L
    for label, val, col in segs:
        w = full * val / total
        is_field = label.startswith("бюджет")
        stroke = FIELD if is_field else "#c9762e"
        f.append(rect(x, ytop, w, bh, fill=(("#27ae60") if False else col), stroke=stroke, sw=2.0, rx=4))
        f.append(fitbox(x + 2, ytop + bh / 2 - 13, w - 4, 26, label, size=12,
                        fill="none", stroke="none", color=INK))
        x += w

    # підпис усієї смуги — дедлайн
    f.append(line(L, ytop - 14, R, ytop - 14, color=MUTED, sw=1.4))
    f.append(line(L, ytop - 20, L, ytop - 8, color=MUTED, sw=1.4))
    f.append(line(R, ytop - 20, R, ytop - 8, color=MUTED, sw=1.4))
    f.append(text(W / 2, ytop - 22, "увесь дедлайн = 40 мс (диктує задача)", size=13, color=MUTED))

    # дужка під залишком
    xb0 = L + full * (40.0 - 18.0) / 40.0
    yb = ytop + bh + 16
    f.append(line(xb0, yb, R, yb, color=FIELD, sw=2.2))
    f.append(line(xb0, yb - 6, xb0, yb + 6, color=FIELD, sw=2.2))
    f.append(line(R, yb - 6, R, yb + 6, color=FIELD, sw=2.2))
    f.append(text((xb0 + R) / 2, yb + 22, "лишилось фільтрам", size=13, color=FIELD, bold=True))

    # дужка під незмінним
    yr = ytop + bh + 16
    f.append(line(L, yr, xb0, yr, color="#c9762e", sw=2.2))
    f.append(line(L, yr - 6, L, yr + 6, color="#c9762e", sw=2.2))
    f.append(line(xb0, yr - 6, xb0, yr + 6, color="#c9762e", sw=2.2))
    f.append(text((L + xb0) / 2, yr + 22, "незмінне (поза фільтром) — 22 мс", size=13, color="#c9762e", bold=True))

    # мораль
    body, bw, bhh = textbox(W / 2, 330,
                            ["Спершу відрахуй усе незмінне.",
                             "На фільтр — рівно решта. Як решти нема,",
                             "важке згладжування виключене ще до коду."],
                            size=13, pad=12, fill="#f4f6f8", stroke=MUTED)
    f.append(body)

    render(os.path.join(OUT, "budget-bar.svg"), W, H, *f)


# ───────────────────────── 2. Затримки ланок додаються ───────────────────────
def fig_cascade_sum():
    """Медіана + біквад + згладжувач: групові затримки складаються."""
    W, H = 780, 410
    f = []
    f.append(text(W / 2, 30, "Затримки ланок тракту додаються", size=18, bold=True))

    ymid = 150
    bw, bh = 150, 70
    gap = 46
    x0 = 60
    blocks = [
        ("медіана(3)", "≈ 1 відлік", "1 мс"),
        ("біквад-notch", "≈ 1 відлік", "1 мс"),
        ("ковзне сер. N=21", "(N−1)/2 = 10", "10 мс"),
    ]
    centers = []
    x = x0
    for title, mid, ms in blocks:
        f.append(rect(x, ymid - bh / 2, bw, bh, fill="#eef2f7", stroke=LINE, sw=1.8, rx=8))
        f.append(text(x + bw / 2, ymid - 12, title, size=13, bold=True))
        f.append(text(x + bw / 2, ymid + 7, mid, size=12, color=MUTED))
        f.append(text(x + bw / 2, ymid + 24, ms, size=13, color=POS, bold=True))
        centers.append(x + bw / 2)
        x += bw + gap

    # сигнал входить зліва, виходить справа
    f.append(arrow(20, ymid, x0 - 6, ymid, color=NEG, sw=2.2))
    f.append(text(20, ymid - 12, "сирий", size=12, color=NEG, anchor="start"))
    # стрілки між блоками
    x = x0 + bw
    for i in range(len(blocks) - 1):
        f.append(arrow(x + 4, ymid, x + gap - 4, ymid, color=LINE, sw=2.0))
        x += bw + gap
    f.append(arrow(x + 4, ymid, x + gap + 22, ymid, color=FIELD, sw=2.2))
    f.append(text(x + gap + 26, ymid - 12, "чистий", size=12, color=FIELD, anchor="start"))

    # сума знизу
    sy = 300
    f.append(line(centers[0], ymid + bh / 2 + 8, centers[0], sy - 18, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(centers[-1], ymid + bh / 2 + 8, centers[-1], sy - 18, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(centers[0], sy - 18, centers[-1], sy - 18, color=MUTED, sw=1.4))
    body, w2, h2 = textbox(W / 2, sy + 8,
                           "1 + 1 + 10 = 12 мс  —  повна групова затримка тракту",
                           size=15, pad=12, bold=True, fill="#cdeccd", stroke=FIELD)
    f.append(body)
    f.append(text(W / 2, sy + 56,
                  "кожна ланка окремо дрібна — разом легко пробʼють бюджет",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "cascade-sum.svg"), W, H, *f)


# ───────────────────────── 3. Довідка затримки за типом ──────────────────────
def fig_latency_table():
    """Групова затримка для кожного типу фільтра — у відліках."""
    W, H = 780, 430
    f = []
    f.append(text(W / 2, 30, "Групова затримка за типом фільтра (у відліках)", size=18, bold=True))

    rows = [
        ("Ковзне середнє", "(N−1)/2", "рівно, стала на всіх частотах", FIELD),
        ("EMA", "≈ (1−α)/α ≈ 1/α", "мала α → гладше й загайніше", NEG),
        ("Лінійно-фазовий КІХ", "(M−1)/2", "стала; гострий → велике M", FIELD),
        ("Біквад / БІХ", "мала, але…", "пік біля свого зрізу/вирізу", POS),
        ("Медіана", "≈ (вікно−1)/2", "приблизно (нелінійна)", MUTED),
    ]
    L, R = 60, 720
    ytop = 70
    rh = 60
    # заголовки колонок
    cx_name = 70
    cx_form = 330
    cx_note = 520
    f.append(text(cx_name, ytop - 8, "тип", size=12, color=MUTED, anchor="start"))
    f.append(text(cx_form, ytop - 8, "затримка", size=12, color=MUTED, anchor="middle"))
    f.append(text(cx_note + 80, ytop - 8, "характер", size=12, color=MUTED, anchor="middle"))

    y = ytop
    for name, form, note, col in rows:
        f.append(rect(L, y, R - L, rh - 8, fill="#f7f9fb", stroke="#dde3ea", sw=1.2, rx=6))
        f.append(text(cx_name, y + (rh - 8) / 2 + 5, name, size=14, bold=True, anchor="start"))
        # формула в моноподібній рамці
        bodyf = fitbox(cx_form - 90, y + (rh - 8) / 2 - 15, 180, 30, form,
                       size=14, fill="#eef2f7", stroke=col, sw=1.6, color=INK, bold=True)
        f.append(bodyf)
        f.append(fitbox(cx_note, y + (rh - 8) / 2 - 13, 195, 26, note,
                        size=12, fill="none", stroke="none", color=MUTED))
        y += rh

    f.append(text(W / 2, H - 22,
                  "відліки × крок (1/fд) = мілісекунди",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, "latency-table.svg"), W, H, *f)


# ───────────────────────── 4. Затримка зʼїдає запас по фазі ──────────────────
def fig_phase_eaten():
    """Та сама Δt → більше зʼїденої фази на вищій частоті кросовера."""
    W, H = 780, 440
    f = []
    f.append(text(W / 2, 30, "Затримка зʼїдає запас по фазі: Δφ = 2π·fc·Δt", size=18, bold=True))

    # графік: вісь fc (Гц) →, вісь Δφ (°) ↑, для сталого Δt=12 мс
    L, R = 90, 700
    TOP, BOT = 80, 330
    dt = 0.012  # с
    fc_max = 25.0
    phi_max = 180.0

    def X(fc):
        return L + (fc / fc_max) * (R - L)

    def Y(phi):
        return BOT - (phi / phi_max) * (BOT - TOP)

    # осі
    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.6))
    f.append(line(L, BOT, R + 6, BOT, color=INK, sw=1.6))
    f.append(text(L - 14, TOP - 12, "зʼїдено", size=12, color=MUTED, anchor="middle"))
    f.append(text(L - 14, TOP + 2, "фази, °", size=12, color=MUTED, anchor="middle"))
    f.append(text(R + 6, BOT + 22, "частота кросовера fc →", size=12, color=MUTED, anchor="end"))

    # сітка: 60° (типовий запас) і 180°
    for phi, lab, col in [(60, "запас 60°", "#c9762e"), (180, "180° (зрив)", POS)]:
        yy = Y(phi)
        f.append(line(L, yy, R, yy, color=col, sw=1.3, dash="6 5"))
        f.append(text(R + 4, yy + 4, lab, size=11, color=col, anchor="start"))

    # крива Δφ(fc) для сталого Δt
    pts = []
    fc = 0.0
    while fc <= fc_max + 0.01:
        phi = math.degrees(2 * math.pi * fc * dt)
        phi = min(phi, phi_max)
        pts.append("%.1f,%.1f" % (X(fc), Y(phi)))
        fc += 0.5
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))

    # дві точки: повільний і швидкий контур (той самий Δt!)
    for fc0, name, col in [(3.0, "повільний", FIELD), (20.0, "швидкий", POS)]:
        phi0 = math.degrees(2 * math.pi * fc0 * dt)
        xx, yy = X(fc0), Y(min(phi0, phi_max))
        f.append(line(xx, BOT, xx, yy, color=col, sw=1.2, dash="3 3"))
        f.append(circle(xx, yy, 5, fill=col, stroke=col))
        f.append(text(xx, BOT + 18, name, size=11, color=col, anchor="middle"))
        f.append(text(xx, yy - 10, "%d°" % round(phi0), size=12, color=col, bold=True, anchor="middle"))

    # підпис: той самий фільтр
    body, w2, h2 = textbox(W / 2, 388,
                           ["Той самий фільтр (Δt = 12 мс): у повільному контурі зʼїдає крихту,",
                            "у швидкому — десятки градусів і заганяє запас у мінус."],
                           size=12, pad=11, fill="#f4f6f8", stroke=MUTED)
    f.append(body)

    render(os.path.join(OUT, "phase-eaten.svg"), W, H, *f)


if __name__ == "__main__":
    fig_budget_bar()
    fig_cascade_sum()
    fig_latency_table()
    fig_phase_eaten()
    print("OK: 4 SVG ->", OUT)
