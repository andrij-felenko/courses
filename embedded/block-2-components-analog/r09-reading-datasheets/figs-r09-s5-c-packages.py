# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки r09-s5-c-packages (до теми 2.9.5).
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс r09-5c-...), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки marker; sans-serif.
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
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3df"
BODY  = "#3a3a3a"
PAD   = "#c9923f"
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="{fill}" stroke="{col}" stroke-width="{wv}"{d}/>\n')


# ── фігура 1: THT проти SMD у розрізі плати ────────────────────────────────────
def fig_tht_vs_smd():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Два способи сісти на плату: крізь дірку проти на поверхню",
              17, INK, "middle", "bold")

    boardY = 250          # верх плати
    boardH = 26           # товщина міді/скла
    bx0, bx1 = 60, 700

    # — спільна підкладка (плата) у розрізі
    def board(x0, x1):
        b = rect(x0, boardY, x1 - x0, boardH, "#f3ece0", COPP, 1.5)
        # хрест-навхрест склотекстоліт
        b += line(x0, boardY + boardH, x1, boardY + boardH, COPP, 2)
        return b

    s += board(bx0, 360)
    s += board(400, bx1)

    # ── ЛІВОРУЧ: THT — вивід крізь отвір, паяння з другого боку
    cxL = 210
    s += text(cxL, 70, "THT", 16, BLUE, "middle", "bold")
    s += text(cxL, 90, "(through-hole, виводи)", 12.5, GREY, "middle", style="italic")
    # корпус компонента
    s += rect(cxL - 70, 110, 140, 70, LBLUE, BLUE, 2, 6)
    s += text(cxL, 150, "корпус", 13.5, INK, "middle")
    # два дротяні виводи вниз крізь плату
    holeY = boardY + boardH
    for hx in (cxL - 38, cxL + 38):
        s += line(hx, 180, hx, holeY + 34, INK, 3)          # дріт
        # отвір у платі (металізований)
        s += rect(hx - 7, boardY - 1, 14, boardH + 2, "#ffffff", COPP, 1.5)
        # галтель припою з нижнього боку (конус)
        s += _poly([(hx - 16, holeY + 26), (hx, holeY + 6),
                    (hx + 16, holeY + 26)], GREY, 1.5, fill="#cfcfcf")
    s += text(cxL, holeY + 52, "припій із ЗВОРОТНОГО боку", 12, GREEN, "middle")
    s += arrow(cxL + 96, holeY + 16, cxL + 30, holeY + 16, GREEN, 2)
    s += text(cxL + 150, holeY + 6, "тримає й", 11.5, GREEN, "middle")
    s += text(cxL + 150, holeY + 21, "контачить сам", 11.5, GREEN, "middle")

    # ── ПРАВОРУЧ: SMD — лежить на майданчику, паяння з того ж боку
    cxR = 545
    s += text(cxR, 70, "SMD", 16, RED, "middle", "bold")
    s += text(cxR, 90, "(surface-mount, майданчики)", 12.5, GREY, "middle", style="italic")
    # корпус лежить ПОВЕРХ плати на двох контактних майданчиках
    padY = boardY - 8
    for px in (cxR - 46, cxR + 46):
        s += rect(px - 18, padY, 36, 8, PAD, COPP, 1.2)     # майданчик (pad)
        # галтель припою збоку контакту
        s += _poly([(px - 22, padY + 8), (px - 10, padY - 14),
                    (px - 2, padY + 8)], GREY, 1.2, fill="#cfcfcf")
    # тіло чипа
    s += rect(cxR - 60, padY - 56, 120, 50, LRED, RED, 2, 5)
    s += text(cxR, padY - 26, "корпус", 13.5, INK, "middle")
    # короткі L-виводи / або зовсім без виводів
    s += line(cxR - 60, padY - 12, cxR - 46, padY - 2, INK, 3)
    s += line(cxR + 60, padY - 12, cxR + 46, padY - 2, INK, 3)
    s += text(cxR, padY + 40, "припій із ТОГО Ж боку", 12, GREEN, "middle")
    s += text(cxR, padY + 56, "отворів немає", 12, GREY, "middle")

    # підсумкова смуга внизу
    yB = 372
    s += line(bx0, yB, bx1, yB, FAINT, 1.5)
    s += text(cxL, yB + 24, "паяльник заходить з низу — легко",
              13, BLUE, "middle", "bold")
    s += text(cxL, yB + 44, "велике, місця багато, прощає руки",
              12, GREY, "middle")
    s += text(cxR, yB + 24, "усе паяння — згори, поряд із сусідами",
              13, RED, "middle", "bold")
    s += text(cxR, yB + 44, "дрібне; крок виводів вирішує, чи спаяєш",
              12, GREY, "middle")
    save("fig-r09-5c-1-tht-vs-smd.svg", s)


# ── фігура 2: сходинка ручного паяння за кроком виводів ────────────────────────
def fig_solder_ladder():
    W, H = 770, 470
    s = header(W, H)
    s += text(W / 2, 30, "Сходинка ручного паяння: усе вирішує крок виводів (pin pitch)",
              17, INK, "middle", "bold")

    # вісь «кроку» згори: чим менший крок, тим важче
    axY = 70
    s += arrow(70, axY, 700, axY, INK, 2)
    s += text(70, axY - 12, "крок великий — легко", 12.5, GREEN, "start")
    s += text(700, axY - 12, "крок крихітний — важко", 12.5, RED, "end")

    # три «карти» корпусів
    cards = [
        # (x, заголовок, рядки опису, крок, метод, колір методу, fill)
        (60,  "SOT-23",
         ["3–6 виводів збоку", "крок ≈ 0.95 мм", "транзистор, регулятор"],
         "0.95 мм", "паяльник", GREEN, LGRN),
        (290, "SOIC",
         ["8–16 «крил» обабіч", "крок 1.27 мм", "ОП, логіка, пам'ять"],
         "1.27 мм", "паяльник", GREEN, LGRN),
        (520, "QFN",
         ["майданчики ПІД корпусом", "крок 0.4–0.5 мм", "МК, радіочипи"],
         "0.4–0.5 мм", "фен / піч", RED, LRED),
    ]
    cw, ch, cy = 190, 250, 110
    for x, title, rows, pitch, method, mc, fl in cards:
        s += rect(x, cy, cw, ch, fl, INK, 1.8, 10)
        s += text(x + cw / 2, cy + 30, title, 18, INK, "middle", "bold")
        # мініатюра корпуса
        mcx = x + cw / 2
        mcy = cy + 92
        if title == "SOT-23":
            s += rect(mcx - 30, mcy - 18, 60, 36, BODY, INK, 1.5, 3)
            # 2 виводи з одного боку, 1 з іншого
            for ly in (mcy - 11, mcy + 11):
                s += line(mcx - 30, ly, mcx - 48, ly, INK, 3)
            s += line(mcx + 30, mcy, mcx + 48, mcy, INK, 3)
        elif title == "SOIC":
            s += rect(mcx - 34, mcy - 22, 68, 44, BODY, INK, 1.5, 3)
            for i in range(4):
                ly = mcy - 16 + i * 11
                s += line(mcx - 34, ly, mcx - 52, ly, INK, 2.6)   # gull-wing крила
                s += line(mcx + 34, ly, mcx + 52, ly, INK, 2.6)
            s += circle(mcx - 24, mcy - 13, 2.4, INK, INK, 1)     # точка піна 1
        else:  # QFN
            s += rect(mcx - 32, mcy - 26, 64, 52, BODY, INK, 1.5, 4)
            # майданчики по периметру ПІД корпусом (пунктир — невидимі ззовні)
            for i in range(4):
                off = -19 + i * 12.7
                s += rect(mcx - 38, mcy + off - 3, 8, 6, PAD, COPP, 1)
                s += rect(mcx + 30, mcy + off - 3, 8, 6, PAD, COPP, 1)
            s += rect(mcx - 14, mcy - 12, 28, 24, "#4a4a4a", GREY, 1, 3)  # термопад
            s += text(mcx, mcy + 4, "↓", 14, "#dddddd", "middle")
        # рядки опису
        ty = cy + 142
        for r in rows:
            s += text(x + 16, ty, "• " + r, 12.5, BODY, "start")
            ty += 22
        # бейдж методу
        s += rect(x + 20, cy + ch - 46, cw - 40, 30,
                  "#ffffff", mc, 1.8, 6)
        s += text(x + cw / 2, cy + ch - 26, "→ " + method, 14, mc, "middle", "bold")

    # нижня нота: де проходить «межа паяльника»
    yL = 400
    s += line(60, yL, 710, yL, FAINT, 1.5)
    s += text(60, yL + 26, "Поки крок ≥ ~0.8 мм і виводи назовні — вистачає паяльника, флюсу й обплетення.",
              13, GREEN, "start")
    s += text(60, yL + 50, "Майданчики під корпусом (QFN, BGA) ховаються від жала — їх «тягне» лише розплавом знизу: фен, піч або паста з трафаретом.",
              12.5, RED, "start")
    save("fig-r09-5c-2-solder-ladder.svg", s)


if __name__ == "__main__":
    fig_tht_vs_smd()
    fig_solder_ladder()
    print("done")
