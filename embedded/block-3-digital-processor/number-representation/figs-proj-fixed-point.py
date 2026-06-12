# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для ⚙️-вставки до теми §3.4.5 — «Фіксована кома без FPU».
Окремий скрипт (головний figs.py не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Імена файлів: fig-17-5a-k-<slug>.svg, підписи — Рис. 3.4.5a.k.

Стиль (AUTHORING §9) узгоджений із figs.py розділу: білий фон; «1» червоний,
«0»/від'ємне синій; «дійсне»/правильний результат зелений; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділу (розділи не
ділять коду, щоб loop'и не конфліктували).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=15, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: ряд бітових клітинок із підписом-вагою ───────────────────────
def bitrow(x, y, cells, cw=26, ch=30):
    """cells: список (символ, колір_заливки, колір_тексту). Повертає (svg, ширина)."""
    out = ""
    for i, (sym, fill, fg) in enumerate(cells):
        cx = x + i * cw
        out += rect(cx, y, cw, ch, fill, INK, 1.4)
        out += text(cx + cw / 2, y + ch * 0.68, sym, 14, fg, "middle", "bold")
    return out, len(cells) * cw


# ── Рис. 3.4.5a.1 — конвеєр множення Q-чисел: розширити → × → округлити → зсув → звузити
def fig_mul_pipeline():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Множення у форматі Q (тут Q8.8): чотири кроки одного добутку",
              21, INK, "middle", "bold")
    s += text(W / 2, 56, "беремо ширший тип → перемножуємо як цілі → додаємо «пів-біта» для округлення → зсуваємо назад на n → звужуємо",
              12.5, GREY, "middle", style="italic")

    # робочий приклад: a = 1.5 (Q8.8 = 384), b = 2.5 (Q8.8 = 640)
    boxw, boxh = 150, 56
    y0 = 96
    colx = [70, 70, 70, 70, 70]

    # крок 1: два 16-бітні операнди
    s += rect(colx[0], y0, boxw, boxh, "#eef3ff", BLUE, 1.8, 6)
    s += text(colx[0] + boxw / 2, y0 + 22, "a = 1.5", 14, INK, "middle", "bold")
    s += mono(colx[0] + boxw / 2, y0 + 42, "int16 = 384", 12.5, BLUE, "middle")
    s += rect(colx[0] + 360, y0, boxw, boxh, "#eef3ff", BLUE, 1.8, 6)
    s += text(colx[0] + 360 + boxw / 2, y0 + 22, "b = 2.5", 14, INK, "middle", "bold")
    s += mono(colx[0] + 360 + boxw / 2, y0 + 42, "int16 = 640", 12.5, BLUE, "middle")
    s += text(colx[0] + 290, y0 + 36, "×", 26, INK, "middle", "bold")
    s += text(W - 40, y0 + 14, "крок 1", 12.5, GREY, "end", style="italic")
    s += text(W - 40, y0 + 32, "два операнди", 11.5, GREY, "end")
    s += text(W - 40, y0 + 48, "Q8.8, масштаб 256", 11.5, GREY, "end")

    # стрілка вниз
    s += arrow(W / 2, y0 + boxh + 4, W / 2, y0 + boxh + 30, INK, 2.2)

    # крок 2: широкий добуток
    y1 = y0 + boxh + 34
    s += rect(280, y1, 380, boxh, "#fff6e6", AMBER, 2.0, 6)
    s += text(470, y1 + 22, "32-бітний добуток (int32_t)", 14, INK, "middle", "bold")
    s += mono(470, y1 + 43, "384 × 640 = 245760   ← масштаб 256·256", 12.5, AMBER, "middle")
    s += text(W - 40, y1 + 22, "крок 2", 12.5, GREY, "end", style="italic")
    s += text(W - 40, y1 + 40, "ширший тип, щоб не", 11.5, GREY, "end")
    s += text(W - 40, y1 + 56, "переповнитись (масштаб²)", 11.5, RED, "end")

    s += arrow(W / 2, y1 + boxh + 4, W / 2, y1 + boxh + 30, INK, 2.2)

    # крок 3: округлення (+ half)
    y2 = y1 + boxh + 34
    s += rect(280, y2, 380, boxh, "#eef9ee", GREEN, 2.0, 6)
    s += text(470, y2 + 22, "додати «пів-біта» перед зсувом", 14, INK, "middle", "bold")
    s += mono(470, y2 + 43, "245760 + (1<<7) = 245888   ← +128 = ½·256", 12.5, GREEN, "middle")
    s += text(W - 40, y2 + 22, "крок 3", 12.5, GREY, "end", style="italic")
    s += text(W - 40, y2 + 40, "необов'язково, але без", 11.5, GREY, "end")
    s += text(W - 40, y2 + 56, "нього зсув лише вниз", 11.5, GREY, "end")

    s += arrow(W / 2, y2 + boxh + 4, W / 2, y2 + boxh + 30, INK, 2.2)

    # крок 4: зсув назад + звуження
    y3 = y2 + boxh + 34
    s += rect(280, y3, 380, boxh, "#eef9ee", GREEN, 2.4, 6)
    s += text(470, y3 + 22, "зсув ≫ 8, потім назад у int16", 14, INK, "middle", "bold")
    s += mono(470, y3 + 43, "245888 ≫ 8 = 960   →  960/256 = 3.75 ✓", 13, GREEN, "middle")
    s += text(W - 40, y3 + 22, "крок 4", 12.5, GREY, "end", style="italic")
    s += text(W - 40, y3 + 40, "результат знову Q8.8", 11.5, GREY, "end")
    s += text(W - 40, y3 + 56, "1.5 × 2.5 = 3.75", 11.5, INK, "end", "bold")

    # бічна нота про знак
    s += line(46, y1 - 6, 46, y3 + boxh + 6, FAINT, 6)
    s += text(40, (y1 + y3) / 2, "ширший тип", 12, GREY, "middle", style="italic")

    # підсумкова стрічка
    s += rect(70, H - 56, W - 140, 36, "#f7f7f7", GREY, 1.4, 8)
    s += text(W / 2, H - 33, "Те саме «множення зі зсувом», та на знаковому типі зсув мусить бути арифметичним (≫ зберігає знак).",
              12.5, INK, "middle")
    save("fig-17-5a-1-mul-pipeline.svg", s)


# ── Рис. 3.4.5a.2 — насичення проти обгортки: передавальна крива ─────────────
def fig_saturation():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 34, "Що робити з переповненням: насичення (clamp) проти обгортки (wrap)",
              21, INK, "middle", "bold")
    s += text(W / 2, 56, "вхід виходить за межі int8 (−128…+127): обгортка перестрибує на інший край, насичення прилипає до межі",
              12.5, GREY, "middle", style="italic")

    # спільна вісь: вхід (ідеальне значення) по горизонталі
    ax, ay = 110, 110          # лівий-верх області графіка
    aw, ah = W - 200, 270
    cx0 = ax + aw / 2          # центр (нуль входу)
    cy0 = ay + ah / 2          # центр (нуль виходу)
    # масштаб: показуємо вхід від -320 до +320, вихід від -160 до +160
    sx = aw / 640.0
    sy = ah / 320.0

    def X(v):  # вхід → екран
        return cx0 + v * sx

    def Y(v):  # вихід → екран
        return cy0 - v * sy

    # сітка меж ±127/-128
    for v in (-128, 127):
        s += line(ax, Y(v), ax + aw, Y(v), FAINT, 1.4, "4 3")
        s += line(X(v), ay, X(v), ay + ah, FAINT, 1.4, "4 3")
    # осі
    s += arrow(ax - 6, cy0, ax + aw + 14, cy0, INK, 1.8)
    s += arrow(cx0, ay + ah + 6, cx0, ay - 14, INK, 1.8)
    s += text(ax + aw + 18, cy0 + 4, "вхід", 13, INK, "start")
    s += text(cx0 + 8, ay - 18, "збережений байт", 13, INK, "start")

    # ідеальна пряма y=x (сіра пунктирна)
    s += line(X(-160), Y(-160), X(160), Y(160), GREY, 1.6, "5 4")
    s += text(X(120), Y(120) - 8, "ідеал y = x", 12, GREY, "start", style="italic")

    # ── насичення (зелене): y = clamp(x, -128, 127)
    sat = [(-320, -128), (-128, -128), (127, 127), (320, 127)]
    s += polyline([(X(a), Y(b)) for a, b in sat], GREEN, 3.2)
    s += text(X(-300), Y(-128) - 10, "насичення (clamp): прилипає до −128 / +127",
              13, GREEN, "start", "bold")

    # ── обгортка (червоне): зубчаста пилка, період 256
    wrap = []
    v = -320
    while v <= 320:
        # обгортка: ((v + 128) mod 256) - 128
        m = ((int(v) + 128) % 256) - 128
        wrap.append((v, m))
        v += 4
    # намалюємо як набір коротких сегментів, розриваючи на стрибках
    seg = []
    prev = None
    for a, b in wrap:
        if prev is not None and abs(b - prev[1]) > 200:
            if len(seg) > 1:
                s += polyline([(X(p), Y(q)) for p, q in seg], RED, 2.6)
            seg = []
        seg.append((a, b))
        prev = (a, b)
    if len(seg) > 1:
        s += polyline([(X(p), Y(q)) for p, q in seg], RED, 2.6)
    s += text(X(150), Y(-128) + 22, "обгортка (wrap): зривається на −128", 12.5, RED, "middle", "bold")

    # позначки меж
    s += text(ax - 10, Y(127) + 4, "+127", 12, INK, "end")
    s += text(ax - 10, Y(-128) + 4, "−128", 12, BLUE, "end")

    # підпис-висновок
    s += rect(110, H - 52, W - 220, 34, "#f7f7f7", GREY, 1.4, 8)
    s += text(W / 2, H - 30, "Для звуку/керування різкий стрибок обгортки — це тріск і нестійкість; насичення лише «впирається» в межу.",
              12.5, INK, "middle")
    save("fig-17-5a-2-saturation.svg", s)


if __name__ == "__main__":
    fig_mul_pipeline()
    fig_saturation()
    print("ch17 s5a (fixed-point) figures done.")
