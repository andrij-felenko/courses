# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки 3.7.1c — «Де ви вже
зустрічали FPGA». НЕ чіпає головний figs.py розділу. Вивід → ./img/ з
УНІКАЛЬНИМИ іменами (fig-r07-s1c-*). Стиль (AUTHORING §9): білий фон;
'+' червоний, '−' синій; поле зелене; стрілки через marker; шрифт
sans-serif. Допоміжні функції скопійовано з figs.py розділу (єдиний
вигляд між розділами).
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
COPP  = "#b5732e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LCOP  = "#fff7e6"
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
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aCopp" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{COPP}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", COPP: "aCopp"}


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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _block(x, y, w, h, title, sub=None, fill=LBLUE, stroke=BLUE, tsize=15.5):
    """Прямокутний блок із заголовком (і дрібним підписом)."""
    s = rect(x, y, w, h, fill, stroke, 2.2, rx=8)
    if sub:
        s += text(x + w / 2, y + h / 2 - 5, title, tsize, INK, "middle", "bold")
        s += text(x + w / 2, y + h / 2 + 15, sub, 11.5, GREY, "middle", style="italic")
    else:
        s += text(x + w / 2, y + h / 2 + 5, title, tsize, INK, "middle", "bold")
    return s


# ── Рис. 3.7.1c.1 — місце FPGA у тракті вимірювального приладу ───────────────
def fig_instrument_block():
    """Сигнальний тракт цифрового осцилографа / логічного аналізатора.
    Швидкий потік відліків з кількох входів іде СПЕРШУ у FPGA (передова лінія):
    вона ловить кожен відлік без пропуску, шукає запуск, складає в буфер; далі
    процесор підхоплює вже зібране й малює екран. Поряд із FPGA — обов'язковий
    «почет»: флеш конфігурації (вантажить схему при старті), кварц такту,
    кілька джерел живлення. Показує, ЧОМУ FPGA — «передова лінія» (паралельний
    прийом), а не банальність."""
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 34, "Де у приладі стоїть FPGA: «передова лінія» швидкого потоку даних",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "цифровий осцилограф / логічний аналізатор: відліки йдуть СПЕРШУ у FPGA — вона приймає всі канали паралельно",
              12.5, GREY, "middle", style="italic")

    yrow = 200          # вісь головного тракту
    # ── 1) Аналогові входи / канали ──────────────────────────────────────────
    inx, iny, inw, inh = 40, yrow - 52, 132, 104
    s += rect(inx, iny, inw, inh, "#fcfcfc", GREY, 1.8, rx=8)
    s += text(inx + inw / 2, iny - 8, "входи приладу", 12.5, INK, "middle", "bold")
    # кілька каналів-ліній, що сходяться у джгут праворуч
    chy = [iny + 24, iny + 44, iny + 64, iny + 84]
    labs = ["CH1", "CH2", "CH3", "…"]
    for i, cy in enumerate(chy):
        s += line(inx + 14, cy, inx + inw - 16, cy, BLUE, 2.2)
        s += circle(inx + 14, cy, 3, BLUE, BLUE, 1)
        s += text(inx + 6, cy + 4, "", 10)
        s += text(inx + inw - 10, cy + 4, labs[i], 10.5, GREY, "start")

    # ── 2) FPGA — велика, з полем клітинок (передова лінія) ──────────────────
    fx, fy, fw, fh = 250, yrow - 78, 248, 156
    s += rect(fx, fy, fw, fh, LGRN, GREEN, 2.6, rx=10)
    s += text(fx + fw / 2, fy + 26, "FPGA", 20, GREEN, "middle", "bold")
    s += text(fx + fw / 2, fy + 44, "(ПЛІС) — паралельне залізо", 11.5, GREY, "middle", style="italic")
    # поле однакових клітинок логіки/тригерів
    gx0, gy0, cell, gap = fx + 22, fy + 58, 22, 8
    for r in range(3):
        for c in range(6):
            cx = gx0 + c * (cell + gap)
            cy = gy0 + r * (cell + gap)
            s += rect(cx, cy, cell, cell, "#ffffff", GREEN, 1.4, rx=3)
    s += text(fx + fw / 2, fy + fh - 10, "ловить КОЖЕН відлік · шукає запуск · буфер",
              11, GREEN, "middle", style="italic")
    # широкий джгут із входів у FPGA (паралельний прийом)
    bus_y = yrow
    s += text((inx + inw + fx) / 2, bus_y - 64, "швидкий потік", 11.5, RED, "middle", "bold")
    s += text((inx + inw + fx) / 2, bus_y - 49, "відліків", 11.5, RED, "middle", "bold")
    for off in (-9, 0, 9):
        s += arrow(inx + inw, bus_y + off, fx, bus_y + off, RED, 2.4)
    s += text((inx + inw + fx) / 2 + 2, bus_y + 30, "усі канали", 10.5, GREY, "middle", style="italic")
    s += text((inx + inw + fx) / 2 + 2, bus_y + 44, "паралельно", 10.5, GREY, "middle", style="italic")

    # ── 3) Процесор — підхоплює зібране, малює екран ─────────────────────────
    px, py, pw, ph = 570, yrow - 52, 150, 104
    s += rect(px, py, pw, ph, LBLUE, BLUE, 2.2, rx=9)
    s += text(px + pw / 2, py + 34, "процесор", 16, BLUE, "middle", "bold")
    s += text(px + pw / 2, py + 56, "малює екран,", 11.5, GREY, "middle", style="italic")
    s += text(px + pw / 2, py + 72, "рахує, меню", 11.5, GREY, "middle", style="italic")
    # FPGA → процесор: вже зібрані дані (вузька шина)
    s += arrow(fx + fw, yrow, px, yrow, INK, 2.6)
    s += text((fx + fw + px) / 2, yrow - 10, "готові дані", 11, INK, "middle", "bold")
    s += text((fx + fw + px) / 2, yrow + 18, "(спокійний темп)", 10.5, GREY, "middle", style="italic")

    # ── 4) Екран ─────────────────────────────────────────────────────────────
    scx, scy, scw, sch = 770, yrow - 44, 150, 88
    s += rect(scx, scy, scw, sch, "#fbfbff", GREY, 1.8, rx=6)
    s += text(scx + scw / 2, scy - 8, "екран", 12.5, INK, "middle", "bold")
    # проста хвиля на екрані
    wx = scx + 12
    pts = []
    import math
    for i in range(0, scw - 24):
        xx = wx + i
        yy = scy + sch / 2 + 18 * math.sin(i / 9.0)
        pts.append(f"{xx:.1f},{yy:.1f}")
    s += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{GREEN}" stroke-width="2"/>\n'
    s += arrow(px + pw, yrow, scx, yrow, INK, 2.2)

    # ── Почет FPGA: флеш конфігурації, кварц, живлення ───────────────────────
    # межа «що оточує FPGA на платі»
    sup_y = 380
    s += line(40, sup_y - 18, W - 40, sup_y - 18, FAINT, 1.6, "6 5")
    s += text(fx + fw / 2, sup_y + 2, "обов'язковий «почет» FPGA на платі", 13.5, INK, "middle", "bold")

    # флеш конфігурації — над/під FPGA, вантажить схему при старті
    cfx, cfy, cfw, cfh = 250, sup_y + 18, 150, 62
    s += _block(cfx, cfy, cfw, cfh, "флеш", "конфігурації", LCOP, COPP, 15)
    s += arrow(cfx + cfw / 2, cfy, fx + 64, fy + fh, COPP, 2.4)
    s += text(cfx + cfw + 12, cfy + 26, "вантажить СХЕМУ", 11.5, COPP, "start", "bold")
    s += text(cfx + cfw + 12, cfy + 44, "при ввімкненні → DONE", 11, COPP, "start", style="italic")

    # кварц такту
    qx, qy, qw, qh = 470, sup_y + 18, 130, 62
    s += _block(qx, qy, qw, qh, "кварц", "такт (§3.3.6)", "#fff", GREY, 15)
    s += arrow(qx + qw / 2, qy, fx + fw - 40, fy + fh, GREY, 2.2, "4 3")

    # живлення — кілька рейок
    pwx, pwy, pww, pwh = 650, sup_y + 18, 200, 62
    s += rect(pwx, pwy, pww, pwh, LRED, RED, 2.2, rx=8)
    s += text(pwx + pww / 2, pwy + 22, "живлення: кілька рейок", 13, INK, "middle", "bold")
    s += text(pwx + pww / 2, pwy + 42, "ядро 1.2 В + банки 1.8 / 3.3 В", 11, GREY, "middle", style="italic")
    s += arrow(pwx, pwy + pwh / 2, fx + fw + 8, fy + fh - 8, RED, 2.2, "4 3")

    # підпис-висновок
    s += text(W / 2, H - 14,
              "FPGA — паралельний приймач на вході; процесор — послідовний оброблювач позаду; "
              "схему чип вантажить із флеші при старті",
              12, GREY, "middle", style="italic")

    save("fig-r07-s1c-1-instrument-block.svg", s)


if __name__ == "__main__":
    fig_instrument_block()
    print("done r07-s1c figures")
