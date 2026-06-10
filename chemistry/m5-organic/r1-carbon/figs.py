# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 5.1 — «Карбон і його ланцюги» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; атоми-кульки — C темно-сіра,
H біла з сірим контуром, O червона, N синя; зв'язки — сірі лінії.
Хелпери скопійовані (розділи не діляться файлами).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e9e9e9"
GREEN = "#1f8a3b"
C_FILL = "#454545"
C_LINE = "#2a2a2a"
H_FILL = "#ffffff"
H_LINE = "#9a9a9a"
O_FILL = "#d9483c"
O_LINE = "#9f2c22"
N_FILL = "#2c52b0"
N_LINE = "#1c3576"
BOND  = "#7c7c7c"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#aInk)"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def bond(x1, y1, x2, y2, w=4):
    return line(x1, y1, x2, y2, BOND, w)


def atom(cx, cy, kind, r=14):
    spec = {"C": (C_FILL, C_LINE, "C", "#fff"), "H": (H_FILL, H_LINE, "H", INK),
            "O": (O_FILL, O_LINE, "O", "#fff"), "N": (N_FILL, N_LINE, "N", "#fff")}
    fill, ln, lab, lc = spec[kind]
    rr = r if kind != "H" else r * 0.66
    s = circle(cx, cy, rr, fill, ln, 1.8)
    s += text(cx, cy + rr * 0.36, lab, rr * 0.95, lc, "middle", "bold")
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 5.1.1-1 — чотири руки + ланцюг/розгалуження/кільце ───────────────────
def fig_skeletons():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 30, "Карбон: чотири руки — і вміння братися за себе", 21, INK, "middle", "bold")
    s += text(W / 2, 52, "ланцюги, розгалуження, кільця — усе з того самого атома", 12.5, GREY, "middle", style="italic")

    # легенда — один C з чотирма руками (метан)
    cx, cy = 150, 150
    s += text(150, 92, "чотири руки", 14, INK, "middle", "bold")
    hs = [(cx - 40, cy - 34), (cx + 40, cy - 34), (cx - 40, cy + 34), (cx + 40, cy + 34)]
    for hx, hy in hs:
        s += bond(cx, cy, hx, hy)
    s += atom(cx, cy, "C", 17)
    for hx, hy in hs:
        s += atom(hx, hy, "H", 14)
    s += text(150, 232, "(валентність 4)", 11.5, GREY, "middle", style="italic")

    # три скелети
    base = 320
    # (a) ланцюг
    chain = [(360, base + 12), (400, base - 12), (440, base + 12), (480, base - 12)]
    for i in range(len(chain) - 1):
        s += bond(*chain[i], *chain[i + 1])
    for x, y in chain:
        s += atom(x, y, "C", 13)
    s += text(420, base + 60, "ланцюг", 13.5, INK, "middle", "bold")

    # (b) розгалуження
    bx = 600
    main = [(bx - 30, base + 12), (bx + 10, base - 12), (bx + 50, base + 12)]
    for i in range(len(main) - 1):
        s += bond(*main[i], *main[i + 1])
    s += bond(bx + 10, base - 12, bx + 10, base - 52)
    for x, y in main:
        s += atom(x, y, "C", 13)
    s += atom(bx + 10, base - 52, "C", 13)
    s += text(bx + 10, base + 60, "розгалуження", 13.5, INK, "middle", "bold")

    # (c) кільце (шестикутник)
    rx, ry, rr = 790, base - 4, 36
    ring = [(rx + rr * math.cos(math.radians(60 * k - 90)),
             ry + rr * math.sin(math.radians(60 * k - 90))) for k in range(6)]
    for i in range(6):
        s += bond(*ring[i], *ring[(i + 1) % 6])
    for x, y in ring:
        s += atom(x, y, "C", 12)
    s += text(rx, base + 60, "кільце", 13.5, INK, "middle", "bold")

    save("fig-5-1-1-1-skeletons.svg", s)


# ── Рис. 5.1.1-2 — катенація: лише Карбон тягне ланцюг без кінця ──────────────
def fig_catenation():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Рідкісний хист: Карбон чіпляється сам до себе без кінця", 19, INK, "middle", "bold")

    # Карбон — довгий ланцюг
    y = 110
    s += text(60, y + 5, "Карбон:", 14, INK, "start", "bold")
    xs = [180 + i * 64 for i in range(7)]
    for i in range(len(xs) - 1):
        s += bond(xs[i], y + (8 if i % 2 else -8), xs[i + 1], y + (-8 if i % 2 else 8))
    for i, x in enumerate(xs):
        s += atom(x, y + (-8 if i % 2 else 8), "C", 13)
    s += text(xs[-1] + 40, y + 5, "… і далі →", 13, GREEN, "start", "bold")

    # Оксиген — лише по двоє
    y = 200
    s += text(60, y + 5, "Оксиген:", 14, INK, "start", "bold")
    s += bond(190, y, 230, y)
    s += atom(190, y, "O", 14)
    s += atom(230, y, "O", 14)
    s += text(280, y + 5, "далі не хоче", 12.5, GREY, "start", style="italic")

    # Нітроген — лише по двоє
    y = 256
    s += text(60, y + 5, "Нітроген:", 14, INK, "start", "bold")
    s += bond(190, y, 230, y)
    s += atom(190, y, "N", 14)
    s += atom(230, y, "N", 14)
    s += text(280, y + 5, "далі не хоче", 12.5, GREY, "start", style="italic")

    s += text(W / 2, 302, "більшість елементів зчепляться по двоє — лише Карбон будує нескінченно",
              12.5, GREY, "middle", style="italic")
    save("fig-5-1-1-2-catenation.svg", s)


if __name__ == "__main__":
    fig_skeletons()
    fig_catenation()
