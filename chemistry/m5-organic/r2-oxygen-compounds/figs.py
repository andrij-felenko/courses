# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 5.2 — «Кисень приєднується» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; атоми-кульки — C темно-сіра,
H біла з сірим контуром, O червона; зв'язки — сірі лінії. Хелпери скопійовані.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e9e9e9"
GREEN = "#1f8a3b"
C_FILL = "#454545"
C_LINE = "#2a2a2a"
H_FILL = "#ffffff"
H_LINE = "#9a9a9a"
O_FILL = "#d9483c"
O_LINE = "#9f2c22"
BOND = "#7c7c7c"
RBLOB = "#e7e4ee"
RBLINE = "#9b90bd"
WINE = "#7a2740"
VIN = "#e9c46a"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    m = "aGreen" if color == GREEN else "aInk"
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


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


def poly(points, color=INK, w=2, fill="none", close=False):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + (" Z" if close else "")
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>\n'


def wavy(x0, y0, length, amp=6, n=4, color="#caa24a", w=3.5, direction=1):
    steps = 24
    pts = [(x0 + direction * length * i / steps, y0 + amp * math.sin(i / steps * n * 2 * math.pi))
           for i in range(steps + 1)]
    return poly(pts, color, w)


def bond(x1, y1, x2, y2, w=4):
    return line(x1, y1, x2, y2, BOND, w)


def double_bond(x1, y1, x2, y2, w=3.4, gap=4):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    px, py = -dy / L * gap, dx / L * gap
    return (line(x1 + px, y1 + py, x2 + px, y2 + py, BOND, w)
            + line(x1 - px, y1 - py, x2 - px, y2 - py, BOND, w))


def atom(cx, cy, kind, r=14):
    spec = {"C": (C_FILL, C_LINE, "C", "#fff"), "H": (H_FILL, H_LINE, "H", INK),
            "O": (O_FILL, O_LINE, "O", "#fff")}
    fill, ln, lab, lc = spec[kind]
    rr = r if kind != "H" else r * 0.7
    s = circle(cx, cy, rr, fill, ln, 1.8)
    s += text(cx, cy + rr * 0.36, lab, rr * 0.95, lc, "middle", "bold")
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def fgroup(cx, cy, kind, rC=14):
    """Ключовий Карбон із групою; ліворуч — R (решта ланцюга)."""
    s = bond(cx - 44, cy, cx - 12, cy)
    s += circle(cx - 46, cy, 17, RBLOB, RBLINE, 1.8) + text(cx - 46, cy + 5, "R", 14, "#5b5170", "middle", "bold")
    if kind == "H":
        for hx, hy in [(cx, cy - 28), (cx, cy + 28), (cx + 30, cy)]:
            s += bond(cx, cy, hx, hy) + atom(hx, hy, "H", 11)
        s += atom(cx, cy, "C", rC)
    elif kind == "OH":
        for hx, hy in [(cx, cy - 28), (cx, cy + 28)]:
            s += bond(cx, cy, hx, hy) + atom(hx, hy, "H", 11)
        s += bond(cx, cy, cx + 34, cy) + atom(cx + 34, cy, "O", 13)
        s += bond(cx + 34, cy, cx + 58, cy - 16) + atom(cx + 58, cy - 16, "H", 10)
        s += atom(cx, cy, "C", rC)
    else:  # COOH
        s += double_bond(cx, cy - 14, cx, cy - 27)
        s += atom(cx, cy - 40, "O", 13)
        s += bond(cx, cy, cx + 32, cy + 12) + atom(cx + 32, cy + 12, "O", 13)
        s += bond(cx + 32, cy + 12, cx + 56, cy + 4) + atom(cx + 56, cy + 4, "H", 10)
        s += atom(cx, cy, "C", rC)
    return s


def bottle(cx, by, h, fill, label, sub=None):
    s = rect(cx - 12, by - 22, 24, 22, fill, INK, 2, 2)        # шийка
    s += rect(cx - 14, by - 30, 28, 8, "#5a4632", INK, 1.5, 2)  # корок
    s += rect(cx - 28, by, 56, h, fill, INK, 2.2, 8)           # тіло
    s += text(cx, by + h + 20, label, 13.5, INK, "middle", "bold")
    if sub:
        s += text(cx, by + h + 37, sub, 11.5, GREY, "middle")
    return s


# ── Рис. 5.2.1-1 — сходинки окиснення ────────────────────────────────────────
def fig_staircase():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 30, "Окиснення по сходинках: кисень додається крок за кроком", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "та сама молекула піднімається: вуглеводень → спирт → кислота",
              12.5, GREY, "middle", style="italic")

    plats = [(60, 330, "вуглеводень", "лише горить"),
             (330, 250, "спирт — етанол", "вино, антисептик"),
             (600, 170, "карбонова кислота", "оцтова = оцет")]
    for px, py, t1, t2 in plats:
        s += rect(px, py, 240, 58, "#f1eef6", "#cfc7e0", 1.6, 10)
        s += text(px + 120, py + 26, t1, 13.5, INK, "middle", "bold")
        s += text(px + 120, py + 45, t2, 11.5, GREY, "middle")

    s += fgroup(180, 286, "H")
    s += fgroup(450, 206, "OH")
    s += fgroup(720, 126, "COOH")

    s += arrow(298, 322, 360, 256, GREEN, 2.6)
    s += text(338, 292, "+ кисень", 12.5, GREEN, "start", "bold")
    s += arrow(568, 242, 630, 176, GREEN, 2.6)
    s += text(608, 212, "+ кисень", 12.5, GREEN, "start", "bold")

    s += text(160, 404, "R — решта вуглеводневого ланцюга", 11.5, GREY, "start", style="italic")
    save("fig-5-2-1-1-staircase.svg", s)


# ── Рис. 5.2.1-2 — вино → оцет ───────────────────────────────────────────────
def fig_wine_vinegar():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Чому відкрите вино скисає на оцет", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "спирт вина на повітрі піднімається на щабель — у оцтову кислоту",
              12.5, GREY, "middle", style="italic")

    s += bottle(150, 150, 130, WINE, "вино", "спирт")
    s += rect(118, 110, 64, 26, "#f1eef6", "#cfc7e0", 1.5, 6)
    s += text(150, 127, "–OH", 14, INK, "middle", "bold")

    s += bottle(560, 150, 130, VIN, "оцет", "оцтова кислота")
    s += rect(528, 110, 64, 26, "#fde7ea", "#e3b3b3", 1.5, 6)
    s += text(560, 127, "–COOH", 13, INK, "middle", "bold")

    s += arrow(232, 200, 466, 200, GREEN, 3)
    s += text(349, 182, "повітря (кисень) + бактерії", 12.5, GREEN, "middle", "bold")
    s += text(349, 224, "+ кисень: –OH → –COOH", 12, INK, "middle", "bold")

    # антисептик
    s += bottle(760, 168, 110, "#cfe6f5", "антисептик", "той самий спирт")
    s += rect(700, 150, 120, 0.1, "none", "none", 0)
    s += line(636, 150, 700, 150, FAINT, 2, dash="5 5")
    s += text(760, 132, "закритий від повітря", 11, GREY, "middle", style="italic")

    s += text(360, 326, "усе вирішує щабель окиснення: спирт ↔ кислота", 12.5, GREY, "middle", style="italic")
    save("fig-5-2-1-2-wine-vinegar.svg", s)


# ── Рис. 5.2.2-1 — естер: кислота + спирт − вода ─────────────────────────────
def fig_ester():
    W, H = 880, 300
    s = header(W, H)
    s += text(W / 2, 28, "Естер: кислота тисне руку спирту — і виходить запах", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "від кислоти йде –OH, від спирту — H; разом вони — крапля води, а решта зчіплюється",
              12.5, GREY, "middle", style="italic")

    # кислота R–COOH
    s += bond(102, 150, 126, 150)
    s += circle(86, 150, 16, RBLOB, RBLINE, 1.8) + text(86, 155, "R", 13, "#5b5170", "middle", "bold")
    s += double_bond(126, 136, 126, 122)
    s += atom(126, 110, "O", 12)
    s += bond(126, 150, 156, 164) + atom(156, 164, "O", 12)
    s += bond(156, 164, 178, 158) + atom(178, 158, "H", 9)
    s += atom(126, 150, "C", 13)
    s += text(126, 214, "кислота –COOH", 12.5, INK, "middle", "bold")

    s += text(228, 156, "+", 22, INK, "middle", "bold")

    # спирт R'–OH
    s += bond(296, 150, 320, 150)
    s += circle(280, 150, 16, RBLOB, RBLINE, 1.8) + text(280, 155, "R′", 12, "#5b5170", "middle", "bold")
    s += atom(320, 150, "O", 12)
    s += bond(320, 150, 344, 138) + atom(344, 138, "H", 9)
    s += text(312, 214, "спирт –OH", 12.5, INK, "middle", "bold")

    s += arrow(378, 150, 472, 150, INK, 2.6)
    s += text(425, 134, "− вода", 12.5, INK, "middle", "bold")
    s += text(425, 178, "H₂O", 12, "#1f47b5", "middle", "bold")

    # естер R–CO–O–R'
    s += rect(520, 100, 320, 96, "#f6fbf7", "#bfe0c8", 1.4, 12)
    s += bond(556, 150, 580, 150)
    s += circle(540, 150, 16, RBLOB, RBLINE, 1.8) + text(540, 155, "R", 13, "#5b5170", "middle", "bold")
    s += double_bond(580, 136, 580, 122)
    s += atom(580, 110, "O", 12)
    s += line(580, 150, 614, 150, GREEN, 4)
    s += atom(614, 150, "O", 12)
    s += line(614, 150, 648, 150, GREEN, 4)
    s += circle(664, 150, 16, RBLOB, RBLINE, 1.8) + text(664, 155, "R′", 12, "#5b5170", "middle", "bold")
    s += atom(580, 150, "C", 13)
    s += text(690, 150, "← новий зв'язок", 11, GREEN, "start", "bold")
    s += text(620, 178, "естер — пахне фруктами й квітами", 12, INK, "middle", "bold")
    save("fig-5-2-2-1-ester.svg", s)


# ── Рис. 5.2.2-2 — жир → мило → чому миє ─────────────────────────────────────
def fig_fat_soap():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 28, "Жир, мило — і чому мило миє", 20, INK, "middle", "bold")
    s += text(W / 2, 50, "луг розбирає жир на мильні молекули, що люблять і жир, і воду",
              12.5, GREY, "middle", style="italic")

    # — жир: гліцерин + 3 хвости
    gx = 110
    ys = [120, 168, 216]
    for i in range(2):
        s += bond(gx, ys[i], gx, ys[i + 1])
    for y in ys:
        s += bond(gx, y, gx + 28, y) + atom(gx + 28, y, "O", 10)
        s += wavy(gx + 40, y, 92, 6, 3)
        s += atom(gx, y, "C", 11)
    s += text(155, 286, "жир", 13.5, INK, "middle", "bold")
    s += text(155, 303, "гліцерин + 3 хвости", 11, GREY, "middle")

    s += arrow(300, 168, 372, 168, GREEN, 2.8)
    s += text(336, 152, "+ луг", 12.5, GREEN, "middle", "bold")
    s += text(336, 186, "розриває", 11, GREY, "middle", style="italic")

    # — одна мильна молекула
    hx, hy = 432, 168
    s += circle(hx, hy, 14, "#cfe0f5", "#1f47b5", 2) + text(hx, hy + 4, "−", 14, "#1f47b5", "middle", "bold")
    s += wavy(hx + 14, hy, 96, 6, 3)
    s += text(495, 250, "мило", 13.5, INK, "middle", "bold")
    s += text(495, 268, "голова — у воду", 11.5, "#1f47b5", "middle", "bold")
    s += text(495, 284, "хвіст — у жир", 11.5, "#9a7d1c", "middle", "bold")

    s += arrow(600, 168, 672, 168, INK, 2.6)
    s += text(636, 152, "у масній воді", 11, GREY, "middle", style="italic")

    # — міцела: мило обліплює жирну краплю
    mx, my, R = 800, 175, 34
    s += circle(mx, my, R, "#f3e1b6", "#caa24a", 2)
    s += text(mx, my + 4, "жир", 11.5, "#7a5a12", "middle", "bold")
    for k in range(10):
        a = math.radians(k * 36)
        ex, ey = mx + R * math.cos(a), my + R * math.sin(a)
        hx2, hy2 = mx + (R + 24) * math.cos(a), my + (R + 24) * math.sin(a)
        s += line(ex, ey, hx2, hy2, "#caa24a", 3)
        s += circle(hx2, hy2, 5, "#cfe0f5", "#1f47b5", 1.6)
    s += text(800, 290, "мило обліплює жир", 12, INK, "middle", "bold")
    s += text(800, 306, "→ змивається водою", 11, GREY, "middle", style="italic")
    save("fig-5-2-2-2-fat-soap.svg", s)


if __name__ == "__main__":
    fig_staircase()
    fig_wine_vinegar()
    fig_ester()
    fig_fat_soap()
