# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для компонентної вставки до Розділу 1.9 —
🔌 «UTP/FTP зсередини: категорії, крок звивання, екран» (до теми 1.9.8).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена;
головний figs.py розділу й figs історії НЕ чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: компонентна вставка до теми 8 → секція 8c → Рис. 1.9.8c.N.
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
COPPER = "#cf8b5e"
ORANGE = "#e08030"
PURPLE = "#7a3fae"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"

# кольори чотирьох пар (стандарт TIA-568): помаранч, зелений, синій, бурий
P_ORANGE = "#e08030"
P_GREEN = "#2f9e44"
P_BLUE = "#1f47b5"
P_BROWN = "#8a5a2b"


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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", ORANGE: "aOrange"}


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
#  Рис. 1.9.8c.1 — крок звивання: чому скручені жили скасовують площу петлі
# ════════════════════════════════════════════════════════════════════════════
def fig_twist_cancel():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Крок звивання: кожен півкрок перевертає петлю — наводки скасовуються",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "зовнішнє магнітне поле пронизує два сусідні «вічка» з протилежних боків → ЕРС у них віднімаються",
              11.5, GREY, "middle", style="italic")

    # ── верх: пряма (нескручена) пара у зовнішньому полі ──
    yA = 120
    s += text(70, yA - 28, "Нескручена пара: одна велика петля", 14, RED, "start", "bold")
    # поле B (сіра штрихова сітка + підпис)
    for gx in range(150, 880, 46):
        s += line(gx, yA - 16, gx, yA + 46, FAINT, 1.2)
    s += text(884, yA - 10, "B (зовн.)", 11.5, GREY, "start", "bold")
    # дві прямі жили
    x0, x1 = 150, 860
    s += line(x0, yA, x1, yA, P_BLUE, 3.2)
    s += line(x0, yA + 30, x1, yA + 30, P_ORANGE, 3.2)
    s += line(x0, yA, x0, yA + 30, INK, 2)
    s += line(x1, yA, x1, yA + 30, INK, 2)
    # циркуляція наведеного струму (одна стрілка по контуру)
    s += arrow((x0 + x1) / 2 - 40, yA, (x0 + x1) / 2 + 40, yA, RED, 2.4)
    s += arrow((x0 + x1) / 2 + 40, yA + 30, (x0 + x1) / 2 - 40, yA + 30, RED, 2.4)
    s += text((x0 + x1) / 2, yA + 64, "вся площа петлі ловить заваду → велика наведена ЕРС",
              12.5, RED, "middle", "bold")

    # ── низ: скручена пара = ланцюг малих петель, що чергують знак ──
    yB = 300
    s += text(70, yB - 28, "Скручена пара: ланцюг дрібних петель, знак площі чергується",
              14, GREEN, "start", "bold")
    for gx in range(150, 880, 46):
        s += line(gx, yB - 16, gx, yB + 60, FAINT, 1.2)
    s += text(884, yB - 10, "те саме B", 11.5, GREY, "start", "bold")

    # дві синусоїдні жили (синя і помаранчева), що переплітаються
    yc = yB + 22         # центральна вісь
    amp = 18             # амплітуда переплетення
    period = 90.0        # крок звивання в пікселях (один повний оберт)
    n = 200
    blue_pts, ora_pts = [], []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        ph = 2 * math.pi * (x - x0) / period
        blue_pts.append((x, yc - amp * math.sin(ph)))
        ora_pts.append((x, yc + amp * math.sin(ph)))
    s += polyline(blue_pts, P_BLUE, 3.0)
    s += polyline(ora_pts, P_ORANGE, 3.0)

    # позначити «+» та «−» вічка по черзі (на кожному півкроці)
    half = period / 2.0
    k = 0
    cx = x0 + half / 2.0
    while cx < x1 - 6:
        sign = "+" if k % 2 == 0 else "−"
        col = RED if k % 2 == 0 else BLUE
        s += text(cx, yc - amp - 8, sign, 17, col, "middle", "bold")
        k += 1
        cx += half

    # дужка «крок звивання» (один повний період)
    bx0 = x0 + 2 * period
    bx1 = bx0 + period
    yk = yc + amp + 30
    s += line(bx0, yk, bx1, yk, INK, 1.8)
    s += line(bx0, yk - 5, bx0, yk + 5, INK, 1.8)
    s += line(bx1, yk - 5, bx1, yk + 5, INK, 1.8)
    s += text((bx0 + bx1) / 2, yk + 18, "крок звивання (twist pitch)", 12, INK, "middle", "bold")

    s += text((x0 + x1) / 2, yB + 96,
              "сусідні петлі пронизані з протилежних боків → +ЕРС і −ЕРС майже точно гасять одна одну",
              12.5, GREEN, "middle", "bold")

    # підказка-висновок праворуч унизу
    s += text(W / 2, H - 16,
              "що менший крок (щільніше звивання) — то дрібніші петлі й точніша компенсація → вища категорія",
              11.5, GREY, "middle", style="italic")
    save("fig-r09-8c-1-twist-cancel.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.9.8c.2 — система позначень екрана xx/yy (U/UTP … S/FTP)
# ════════════════════════════════════════════════════════════════════════════
def _cable_xsection(s, cx, cy, R, outer_shield, pair_shield, title, subtitle):
    """Малює переріз кабелю: 4 пари в оболонці; outer_shield/pair_shield — bool."""
    # загальний екран (фольга/оплітка) — сірий товстий обідок
    if outer_shield:
        s += circle(cx, cy, R + 7, "none", GREY, 6)
    # зовнішня оболонка (jacket)
    s += circle(cx, cy, R, "#fafafa", INK, 2.4)
    # 4 пари по колу
    pr = R * 0.30          # радіус розташування центрів пар
    wr = R * 0.135         # радіус жили
    cols = [P_ORANGE, P_GREEN, P_BLUE, P_BROWN]
    for j, col in enumerate(cols):
        a = math.pi / 4 + j * math.pi / 2
        px, py = cx + pr * math.cos(a) * 1.35, cy + pr * math.sin(a) * 1.35
        # екран навколо кожної пари
        if pair_shield:
            s += circle(px, py, wr * 1.95 + 3, "none", GREY, 4)
        # дві жили пари: кольорова + біло-смугаста (білий заповнювач)
        off = wr * 1.0
        s += circle(px - off * math.cos(a + math.pi / 2),
                    py - off * math.sin(a + math.pi / 2), wr,
                    fill=col, stroke=INK, w=1.4)
        s += circle(px + off * math.cos(a + math.pi / 2),
                    py + off * math.sin(a + math.pi / 2), wr,
                    fill="#ffffff", stroke=INK, w=1.4)
    s += text(cx, cy + R + 34, title, 15.5, INK, "middle", "bold")
    s += text(cx, cy + R + 54, subtitle, 11.5, GREY, "middle")
    return s


def fig_shield_naming():
    W, H = 1000, 560
    s = header(W, H)
    s += text(W / 2, 30, "Як читати назву екрана: xx/yyTP",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52,
              "xx — екран усього кабелю · yy — екран кожної пари · TP = twisted pair (вита пара)",
              12, GREY, "middle", style="italic")

    # легенда позначень літер
    ly = 86
    s += text(150, ly, "U = немає (unscreened)", 12.5, INK, "start")
    s += text(420, ly, "F = фольга (foil)", 12.5, INK, "start")
    s += text(640, ly, "S = оплітка (braid)", 12.5, INK, "start")

    R = 70
    row = 250

    s = _cable_xsection(s, 175, row, R, False, False,
                        "U/UTP", "без екранів — звичайний «UTP»")
    s = _cable_xsection(s, 430, row, R, True, False,
                        "F/UTP", "загальна фольга, пари без екрана")
    s = _cable_xsection(s, 685, row, R, False, True,
                        "U/FTP", "кожна пара у фользі, спільного нема")
    s = _cable_xsection(s, 900, row, R, True, True,
                        "S/FTP", "оплітка + фольга на кожній парі")

    # пояснювальна смуга знизу: що від чого захищає
    by = 430
    s += rect(110, by, 360, 96, "#f4faf4", GREEN, 1.6, 10)
    s += text(130, by + 26, "Загальний екран (xx)", 13.5, GREEN, "start", "bold")
    s += text(130, by + 48, "ловить зовнішнє поле для всього джгута —", 11.8, INK, "start")
    s += text(130, by + 66, "клітка Фарадея навколо сигналів (§1.9.7);", 11.8, INK, "start")
    s += text(130, by + 84, "заземлюють здебільшого з одного кінця.", 11.8, INK, "start")

    s += rect(530, by, 360, 96, "#f4f6fc", BLUE, 1.6, 10)
    s += text(550, by + 26, "Екран пари (yy)", 13.5, BLUE, "start", "bold")
    s += text(550, by + 48, "прибирає взаємні наводки між парами", 11.8, INK, "start")
    s += text(550, by + 66, "(перехресні завади, crosstalk) і лишок,", 11.8, INK, "start")
    s += text(550, by + 84, "який не догасило саме звивання.", 11.8, INK, "start")

    s += text(W / 2, H - 14,
              "більше екранів — вища завадостійкість і ціна, товщий і твердіший кабель, складніше заземлення",
              11.5, GREY, "middle", style="italic")
    save("fig-r09-8c-2-shield-naming.svg", s)


if __name__ == "__main__":
    fig_twist_cancel()
    fig_shield_naming()
    print("done")
