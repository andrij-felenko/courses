# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для компонентної вставки 3.2.6c —
«74HC138: дешифратор як chip select — три піни обирають один із восьми пристроїв»
(Модуль 3, Розділ 3.2, тема 3.2.6).

Окремий скрипт вставки (НЕ головний figs.py розділу). Чистий Python без
залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (префікс «-6c-»).
Допоміжні функції скопійовано зі стилю Розділу (AUTHORING §9):
білий фон; «1»/high червоний, «0»/low синій; дійсне/вибране зелене;
стрілки через marker; шрифт sans-serif. Нумерація підписів — Рис. 3.2.6c.k.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # «1» / high
BLUE  = "#1f47b5"   # «0» / low
GREEN = "#1f8a3b"   # вибране / дійсне
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LYEL  = "#fbf6e6"
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


def dot(cx, cy, r=3.4, col=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.2.6c.1 — клас пристрою + розпіновка 74HC138.
# Зліва: 3 адресні входи A0/A1/A2 і 3 дозволи (E1,E2 активні-0; E3 активний-1).
# Усередині: «дешифратор 3→8» (той самий, що в §3.2.6, лише в кремнії).
# Справа: 8 виходів Y0..Y7, АКТИВНІ-НИЗЬКІ — вибраний 0 (зелений), решта 1.
# Приклад: A=011=3, чип дозволено → активний лише Y3 (=0).
# ─────────────────────────────────────────────────────────────────────────────
def fig_pinout():
    W, H = 820, 560
    s = header(W, H)
    s += text(W / 2, 28, "74HC138: дешифратор 3→8 і його розпіновка", 18, INK, "middle", "bold")
    s += text(W / 2, 49, "три адресні піни обирають один із восьми виходів; виходи активні-НИЗЬКІ",
              12.5, GREY, "middle", style="italic")

    # корпус чипа
    bx, by, bw, bh = 300, 80, 220, 380
    s += rect(bx, by, bw, bh, fill="#fcfcfc", stroke=INK, sw=2, rx=10)
    s += text(bx + bw / 2, by + 26, "74HC138", 16, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 45, "decoder / demux", 11.5, GREY, "middle", style="italic")
    s += text(bx + bw / 2, by + bh / 2 + 4, "3 → 8", 26, FAINT, "middle", "bold")

    # ── адресні входи (ліворуч згори): A0=1, A1=1, A2=0  → число 011 = 3 ──
    addr = [("A0", "1", RED), ("A1", "1", RED), ("A2", "0", BLUE)]
    ay0 = by + 78
    for i, (nm, bit, col) in enumerate(addr):
        y = ay0 + i * 34
        s += arrow(bx - 120, y, bx, y, col, 2.2)
        s += text(bx - 126, y - 7, nm, 13.5, INK, "end", "bold")
        s += text(bx - 126, y + 10, f"= {bit}", 11.5, col, "end", "normal")
    s += text(bx - 120, ay0 - 26, "адреса (3 біти)", 12.5, INK, "start", "bold")
    s += text(bx - 120, ay0 - 10, "A2 A1 A0 = 0 1 1 → 3", 11, GREY, "start", style="italic")

    # ── дозволи (ліворуч знизу): E1,E2 активні-0; E3 активний-1 ──
    ey0 = by + 250
    ens = [("E1", "0", BLUE, "active-0"), ("E2", "0", BLUE, "active-0"), ("E3", "1", RED, "active-1")]
    for i, (nm, bit, col, tag) in enumerate(ens):
        y = ey0 + i * 30
        s += arrow(bx - 120, y, bx, y, col, 2)
        # бульбашка-інверсія на активних-0 дозволах (E1,E2)
        if nm in ("E1", "E2"):
            s += circle(bx - 7, y, 6, "#fff", INK, 1.8)
        s += text(bx - 126, y + 4, nm, 12.5, INK, "end", "bold")
        s += text(bx + 16, y + 4, tag, 10.5, GREY, "start", style="italic")
    s += text(bx - 120, ey0 - 18, "дозволи (enable)", 12.5, INK, "start", "bold")
    s += text(bx - 120, ey0 + 3 * 30 + 6, "усі три виконані → чип увімкнено", 10.5, GREEN, "start", style="italic")

    # ── 8 виходів праворуч: Y0..Y7, активні-низькі; вибраний Y3 = 0 ──
    sel = 3
    oy0 = by + 58
    for i in range(8):
        y = oy0 + i * 38
        active = (i == sel)
        col = GREEN if active else GREY
        bit = "0" if active else "1"
        s += line(bx + bw, y, bx + bw + 70, y, col, 2.6 if active else 1.8)
        # вихідна «бульбашка» — нагадування, що активний рівень тут НИЗЬКИЙ
        s += circle(bx + bw + 7, y, 6, "#fff", col, 1.8)
        s += dot(bx + bw + 70, y, 3.4 if active else 2.6, col)
        s += text(bx + bw + 14, y - 7, f"Y{i}", 12.5, INK if active else GREY,
                  "start", "bold" if active else "normal")
        s += text(bx + bw + 78, y + 4, f"= {bit}", 12, col, "start",
                  "bold" if active else "normal")
        if active:
            s += text(bx + bw + 120, y + 4, "← обраний (LOW)", 11.5, GREEN, "start", "bold")
    s += text(bx + bw + 14, oy0 - 18, "8 виходів (один активний)", 12, INK, "start", "bold")

    # підсумкова рамка
    s += rect(40, H - 56, W - 80, 40, fill=LGRN, stroke=GREEN, sw=1.4, rx=6)
    s += text(W / 2, H - 31, "Адреса 011 = 3, чип дозволено  →  активний лише Y3 (=0), решта сім — у 1.",
              12.5, INK, "middle", "normal")

    save("fig-15-6c-1-pinout.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.2.6c.2 — застосування chip select: МК з 3 ліній адреси керує '138,
# а 8 активних-низьких виходів ідуть на входи ~CS восьми пристроїв на спільній
# шині (SPI). Активний лише один (Y2 → пристрій 2 слухає), решта мовчать.
# Показано «перший байт»: виставив адресу → один ~CS впав → говориш по шині.
# ─────────────────────────────────────────────────────────────────────────────
def fig_chipselect():
    W, H = 860, 560
    s = header(W, H)
    s += text(W / 2, 28, "Один дешифратор — вісім ліній вибору (chip select)", 18, INK, "middle", "bold")
    s += text(W / 2, 49, "3 піни МК → 8 сигналів ~CS; активний лише обраний пристрій, решта на шині мовчать",
              12.5, GREY, "middle", style="italic")

    # ── мікроконтролер ліворуч ──
    mx, my, mw, mh = 36, 110, 150, 300
    s += rect(mx, my, mw, mh, fill="#f6f8fc", stroke=INK, sw=2, rx=10)
    s += text(mx + mw / 2, my + 26, "МК", 16, INK, "middle", "bold")
    s += text(mx + mw / 2, my + 44, "(ESP32)", 11, GREY, "middle", style="italic")

    # ── 74HC138 у центрі ──
    ux, uy, uw, uh = 300, 90, 150, 360
    s += rect(ux, uy, uw, uh, fill="#fcfcfc", stroke=INK, sw=2, rx=10)
    s += text(ux + uw / 2, uy + 24, "74HC138", 15, INK, "middle", "bold")
    s += text(ux + uw / 2, uy + 42, "3 → 8", 13, GREY, "middle", "bold")

    # 3 адресні лінії GPIO → A0,A1,A2 (число 010 = 2 → обрано пристрій 2)
    addr = [("A0", "0", BLUE), ("A1", "1", RED), ("A2", "0", BLUE)]
    for j, (nm, bit, col) in enumerate(addr):
        gy = my + 70 + j * 26
        ty = uy + 70 + j * 26
        s += line(mx + mw, gy, 250, gy, col, 2)
        s += line(250, gy, 250, ty, col, 2)
        s += arrow(250, ty, ux, ty, col, 2)
        s += text(ux + 6, ty - 5, nm, 10.5, INK, "start", "bold")
    s += text(mx + mw + 8, my + 70 - 14, "3 × GPIO (адреса)", 11.5, INK, "start", "bold")
    s += text(mx + mw + 8, my + 70 + 3 * 26 + 2, "A2A1A0 = 010 → 2", 10.5, GREY, "start", style="italic")

    # дозвіл E (одна лінія GPIO або просто притягнутий) — показано як «увімкнено»
    ey = uy + uh - 28
    s += arrow(250, ey, ux, ey, GREEN, 2)
    s += line(mx + mw, my + 70 + 3 * 26 + 22, 250, my + 70 + 3 * 26 + 22, GREEN, 2)
    s += line(250, my + 70 + 3 * 26 + 22, 250, ey, GREEN, 2)
    s += text(ux + 6, ey - 5, "E", 10.5, GREEN, "start", "bold")
    s += text(ux + 6, ey + 12, "увімкн.", 9.5, GREEN, "start", style="italic")

    # ── 8 пристроїв праворуч, кожен зі своїм ~CS від Y0..Y7 ──
    sel = 2
    dy0 = 86
    dxx = 690
    for i in range(8):
        y = dy0 + i * 50
        active = (i == sel)
        col = GREEN if active else GREY
        # коробка пристрою
        fill = LGRN if active else "#fafafa"
        s += rect(dxx, y - 16, 130, 32, fill=fill, stroke=col, sw=2 if active else 1.4, rx=5)
        s += text(dxx + 65, y - 1, f"пристрій {i}", 11.5, INK if active else GREY,
                  "middle", "bold" if active else "normal")
        s += text(dxx + 65, y + 13, "слухає шину" if active else "мовчить (CS=1)",
                  9.5, GREEN if active else GREY, "middle", style="italic")
        # лінія ~CS від виходу '138 до пристрою
        s += line(ux + uw, y, dxx, y, col, 2.6 if active else 1.5)
        s += circle(ux + uw + 7, y, 5, "#fff", col, 1.6)   # бульбашка активного-низького виходу
        s += text(ux + uw + 16, y - 6, f"~CS{i}", 9.5, INK if active else GREY,
                  "start", "bold" if active else "normal")
        s += text(ux + uw + 16, y + 9, "= 0" if active else "= 1", 9.5, col, "start",
                  "bold" if active else "normal")

    # спільна шина даних (SPI) — одна на всіх, паралельно
    busx = dxx - 22
    s += line(busx, dy0 - 26, busx, dy0 + 7 * 50 + 22, INK, 2.2, dash="2,3")
    s += text(busx, dy0 - 32, "спільна шина (SCK/MOSI/MISO)", 10.5, INK, "middle", "bold")
    s += line(mx + mw / 2, my + mh, mx + mw / 2, H - 70, INK, 2)
    s += line(mx + mw / 2, H - 70, busx, H - 70, INK, 2)
    s += line(busx, H - 70, busx, dy0 + 7 * 50 + 22, INK, 2)
    for i in range(8):
        y = dy0 + i * 50
        s += line(busx, y, dxx, y + 12, INK, 1.2, dash="2,3")
    s += text(mx + mw / 2 + 6, H - 60, "дані — паралельно до всіх", 10.5, GREY, "start", style="italic")

    save("fig-15-6c-2-chipselect.svg", s)


if __name__ == "__main__":
    fig_pinout()
    fig_chipselect()
    print("done")
