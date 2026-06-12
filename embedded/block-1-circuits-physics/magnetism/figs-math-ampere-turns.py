# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.8.5m — «Ампер-витки: оцінити поле котушки із закону Ампера».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-8-5m-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 1.8.5m.k.
НЕ чіпає головний figs.py розділу.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
ORANGE = "#e08030"
COPPER = "#cf8b5e"
STEEL = "#9aa3ad"
PURPLE = "#7a3ea8"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.5m.1 — закон Ампера на соленоїді: прямокутний контур,
#  внесок дає лише внутрішній відрізок B·L = μ₀·N·I.
# ════════════════════════════════════════════════════════════════════════════
def fig_ampere_loop():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 30, "Закон Ампера на котушці: ∮B·dl = μ₀·N·I", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "Прямокутний контур вибрано так, що внесок дає лише відрізок усередині",
              12, GREY, "middle", style="italic")

    # --- котушка: ряд витків (кружечки в перерізі) ---
    # вісь котушки горизонтальна, на висоті yc
    yc = 250
    x0 = 150          # початок намотки
    nturns = 9
    pitch = 56
    x1 = x0 + (nturns - 1) * pitch   # кінець намотки
    coil_r = 17

    # тіло котушки (світла труба для наочності внутрішнього об'єму)
    s += rect(x0 - 26, yc - 44, (x1 - x0) + 52, 88, "#eef4ff", "#cfddf5", 1.4, 10)

    # витки: верхні й нижні «перерізи» дроту з позначками струму (× усередину, • назовні)
    for i in range(nturns):
        cx = x0 + i * pitch
        # верхній переріз: струм «на нас» (точка) — умовно
        s += circle(cx, yc - 44, coil_r, "#f6e7d6", COPPER, 2.4)
        s += circle(cx, yc - 44, 2.6, COPPER, COPPER, 1)         # • = до нас
        # нижній переріз: струм «від нас» (хрестик)
        s += circle(cx, yc + 44, coil_r, "#f6e7d6", COPPER, 2.4)
        s += line(cx - 5.5, yc + 44 - 5.5, cx + 5.5, yc + 44 + 5.5, COPPER, 2)
        s += line(cx - 5.5, yc + 44 + 5.5, cx + 5.5, yc + 44 - 5.5, COPPER, 2)

    s += text(x0 - 30, yc - 60, "N витків, струм I у кожному", 13, COPPER, "start", "bold")

    # --- поле B усередині: однорідні стрілки вздовж осі ---
    for i in range(5):
        ax = x0 + 18 + i * ((x1 - x0 - 36) / 4.0)
        s += arrow(ax, yc, ax + 40, yc, GREEN, 3.2)
    s += text((x0 + x1) / 2, yc - 8, "B (однорідне)", 14, GREEN, "middle", "bold", "italic")

    # --- прямокутний контур Ампера (синій), охоплює нижні витки ---
    lx, rx = x0 - 8, x1 + 8        # ліва/права межі контуру
    ty = yc + 18                   # верхній відрізок (усередині котушки)
    by = yc + 96                   # нижній відрізок (зовні, поле ≈ 0)
    # внутрішній (верхній) відрізок — напрям обходу вправо: дає B·L
    s += arrow(lx, ty, (lx + rx) / 2 + 10, ty, BLUE, 3)
    s += line((lx + rx) / 2, ty, rx, ty, BLUE, 3)
    # права сторона вниз
    s += arrow(rx, ty, rx, (ty + by) / 2 + 6, BLUE, 3)
    s += line(rx, (ty + by) / 2, rx, by, BLUE, 3)
    # нижня сторона вліво
    s += arrow(rx, by, (lx + rx) / 2 - 10, by, BLUE, 3)
    s += line((lx + rx) / 2, by, lx, by, BLUE, 3)
    # ліва сторона вгору
    s += arrow(lx, by, lx, (ty + by) / 2 - 6, BLUE, 3)
    s += line(lx, (ty + by) / 2, lx, ty, BLUE, 3)

    s += text((lx + rx) / 2, ty - 8, "L  (внесок B·L)", 13, BLUE, "middle", "bold")
    s += text((lx + rx) / 2, by + 22, "зовні: поле ≈ 0  →  внесок ≈ 0", 12.5, GREY, "middle", style="italic")
    s += text(lx - 10, (ty + by) / 2, "⊥ B", 12, GREY, "end")
    s += text(rx + 10, (ty + by) / 2, "⊥ B", 12, GREY, "start")
    s += text((lx + rx) / 2, (ty + by) / 2 + 5,
              "петлю пронизують усі N витків  →  I_охопл = N·I", 12.5, BLUE, "middle", "bold")

    # --- підсумкова рамка з результатом ---
    bx, byy, bw, bh = 250, 388, 400, 60
    s += rect(bx, byy, bw, bh, "#eaf6ee", GREEN, 1.6, 9)
    s += text(bx + bw / 2, byy + 25, "B · L = μ₀ · N · I", 17, INK, "middle", "bold")
    s += text(bx + bw / 2, byy + 47, "B = μ₀ · (N/L) · I = μ₀ · n · I", 15, GREEN, "middle", "bold")

    save("fig-8-5m-1-ampere-loop.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.5m.2 — однакові 500 ампер-витків, різне поле:
#  важелі — густина витків n та проникність осердя μᵣ.
# ════════════════════════════════════════════════════════════════════════════
def fig_levers():
    W, H = 900, 460
    s = header(W, H)
    s += text(W / 2, 30, "Однакові 500 ампер-витків — різне поле B", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "N·I задає «бюджет»; реальне B вирішують густина витків n і осердя μᵣ",
              12, GREY, "middle", style="italic")

    # три панелі
    panels = [
        ("рідка намотка", "мала n", "повітря", 0.10, "слабке B", STEEL, False),
        ("щільна намотка", "велика n", "повітря", 0.34, "більше B", STEEL, False),
        ("щільна + осердя", "велика n", "залізо μᵣ", 1.00, "B × сотні", RED, True),
    ]
    pw = 250
    gap = 22
    x_left = (W - (3 * pw + 2 * gap)) / 2
    top = 90
    base = 360            # рівень «підлоги» стовпчиків
    barmax = 215          # макс. висота стовпчика B (для відносного показу)

    for idx, (title, ndesc, core, frac, blab, bcol, has_core) in enumerate(panels):
        px = x_left + idx * (pw + gap)
        # рамка панелі
        s += rect(px, top, pw, 300, "#fafafa", FAINT, 1.4, 10)
        s += text(px + pw / 2, top + 22, title, 14.5, INK, "middle", "bold")

        # схематична котушка зверху панелі: ряд кружечків (густина = n)
        cy = top + 56
        cxs = px + 28
        cxe = px + pw - 28
        if idx == 0:
            ncoil = 4
        else:
            ncoil = 8
        for k in range(ncoil):
            cx = cxs + (cxe - cxs) * (k / (ncoil - 1))
            s += circle(cx, cy, 7.5, "#f6e7d6", COPPER, 2)
        # осердя під котушкою
        if has_core:
            s += rect(cxs - 6, cy + 14, (cxe - cxs) + 12, 16, "#d7dbe0", STEEL, 1.6, 4)
            s += text(px + pw / 2, cy + 45, "залізне осердя", 11, STEEL, "middle", "bold")
        else:
            s += text(px + pw / 2, cy + 45, "(без осердя)", 11, GREY, "middle", style="italic")

        # стовпчик B
        bw = 64
        bx = px + pw / 2 - bw / 2
        hbar = barmax * frac
        s += line(px + 18, base, px + pw - 18, base, GREY, 1.4)   # підлога
        s += rect(bx, base - hbar, bw, hbar, "#d8efdf" if not has_core else "#f6dcd9",
                  bcol, 2.2, 3)
        s += text(px + pw / 2, base - hbar - 8, blab, 12.5, bcol, "middle", "bold")

        # підписи важелів
        s += text(px + pw / 2, base + 22, ndesc, 12.5, INK, "middle", "bold")
        s += text(px + pw / 2, base + 40, "N·I = 500 А·в", 12, GREEN, "middle", "bold")

    # стрілка-висновок під третьою панеллю
    s += text(W / 2, 438,
              "B = μ₀ · μᵣ · (N/L) · I   →   ущільни намотку (n) або додай осердя (μᵣ), а не лише струм",
              12.5, INK, "middle", style="italic")

    save("fig-8-5m-2-levers.svg", s)


if __name__ == "__main__":
    fig_ampere_loop()
    fig_levers()
    print("done")
