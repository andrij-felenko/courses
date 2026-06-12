# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки §1.10.5і
«Статика як джерело займання».
Чистий Python, без залежностей. Вивід → ./img/.
Імена файлів УНІКАЛЬНІ (префікс fig-r10-s5hist-*); головний figs.py розділу
не чіпається. Стиль за AUTHORING §9: білий фон, sans-serif, спільні кольори.

Дві фігури:
  1) fig-r10-s5hist-energy-ladder.svg — драбина енергій займання:
     іскра від тіла (~10–30 мДж) поряд із MIE пилу (10–100 мДж) і потужнішими
     механічними джерелами; чому статику легко «звинуватити», коли причини не
     знайдено.
  2) fig-r10-s5hist-tank-washing.svg — механізм вибухів танкерів 1969:
     водяний струмінь → заряджений туман → поле росте → розряд + пара → вибух;
     і як інертний газ (O₂ < 5 %) розриває трикутник горіння.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#eef1f4"
AMBER = "#caa24a"
ORANGE = "#d9772b"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey", GREEN: "aGreen", RED: "aRed", BLUE: "aBlue", ORANGE: "aOrange"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", font=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(pts, color=INK, w=2.5, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round"/>\n')


def polygon(pts, fill="none", stroke=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d} stroke-linejoin="round"/>\n')


def spark(x1, y1, x2, y2, color=RED, w=2.4):
    """Зигзаг-розряд між двома точками."""
    import math as _m
    dx, dy = x2 - x1, y2 - y1
    L = _m.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    n = 5
    pts = [(x1, y1)]
    amp = [0, 7, -6, 6, -5, 0]
    for i in range(1, n + 1):
        t = i / n
        a = amp[i] if i < len(amp) else 0
        pts.append((x1 + dx * t + nx * a, y1 + dy * t + ny * a))
    return polyline(pts, color=color, w=w)


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.10.5і.1 — драбина енергій займання ────────────────────────────────
def fig_energy_ladder():
    W, H = 920, 660
    s = header(W, H)
    s += text(W / 2, 34, "Драбина енергій: чим займається пил і чому звинувачують статику",
              21, INK, "middle", "bold")
    s += text(W / 2, 56, "лог-шкала енергії іскри (мДж); зона MIE пилу перекривається з розрядом тіла, але грубі джерела — потужніші",
              12.5, GREY, "middle", style="italic")

    # горизонтальна лог-вісь від 0.01 до 100000 мДж (log10: -2 .. 5)
    L, R = 95, W - 55
    yax = H - 150
    import math as _m
    lo, hi = -2.0, 5.0

    def X(e):  # e у мДж
        return L + (R - L) * (_m.log10(e) - lo) / (hi - lo)

    # вісь
    s += arrow(L - 5, yax, R + 18, yax, INK, 2.2)
    s += text(R + 22, yax + 5, "мДж", 13, INK, "start")
    for dec in range(-2, 6):
        x = L + (R - L) * (dec - lo) / (hi - lo)
        s += line(x, yax - 5, x, yax + 5, INK, 1.6)
        lab = {-2: "0.01", -1: "0.1", 0: "1", 1: "10", 2: "100",
               3: "10³", 4: "10⁴", 5: "10⁵"}[dec]
        s += text(x, yax + 22, lab, 12.5, INK, "middle")

    # зона MIE горючого пилу: 10..100 мДж (помірно чутливий)
    x0, x1 = X(10), X(100)
    s += rect(x0, 95, x1 - x0, yax - 95 - 4, fill="#fff3e6", stroke=ORANGE, sw=1.6)
    s += text((x0 + x1) / 2, 116, "MIE горючого пилу", 14, ORANGE, "middle", "bold")
    s += text((x0 + x1) / 2, 134, "борошно · зерно · цукор", 12, ORANGE, "middle")
    s += text((x0 + x1) / 2, 150, "10–100 мДж (типово)", 12, ORANGE, "middle")

    # смужки-маркери джерел: підпис — НАД смужкою (зліва), щоб не вилазив за край.
    def band(elo, ehi, y, label, color, sub=""):
        a, b = X(elo), X(ehi)
        # підпис ставимо над смужкою, ліворуч вирівняний; clamp, щоб не вийти за R
        lx = min(a, R - 250)
        lx = max(lx, L)
        out = text(lx, y - 8, label, 13.5, color, "start", "bold")
        if sub:
            out += text(lx, y + 38, sub, 11.5, GREY, "start")
        out += rect(a, y, max(b - a, 9), 22, fill="none", stroke=color, sw=2.4, rx=4)
        out += line(a, y + 11, b, y + 11, color, 2.4)
        return out

    yA, yB, yC = 198, 268, 338
    # тонка електроніка гине набагато раніше — для контрасту (мікроджоулі)
    s += band(0.05, 0.5, yB, "Поріг загибелі КМОН-входу (для контрасту)", GREY,
              "мікроджоулі · те, що смертельне чипу, для пилу — ніщо")
    # розряд людського тіла: 10..30 мДж (ESD моделі HBM)
    s += band(10, 30, yA, "Іскра з пальця (тіло людини)", BLUE,
              "≈10–30 мДж · ледь дотягує до низу MIE пилу")
    # механічні / гарячі джерела: 1000..100000 мДж
    s += band(1000, 100000, yC, "Гаряча букса, іскра тертя, зварювання", RED,
              "джоулі · набагато потужніше за статику")

    # вертикальні пунктири від смужки «іскра з пальця» до осі — показати перекриття з MIE
    s += line(X(30), yA + 22, X(30), yax, BLUE, 1.2, dash="3,4")
    s += line(X(10), yA + 22, X(10), yax, BLUE, 1.2, dash="3,4")

    # нижній висновок-рамка
    by = yax + 48
    s += rect(L - 5, by, R - L + 28, 70, fill=FAINT, stroke=GREY, sw=1.4, rx=8)
    s += text(L + 14, by + 26,
              "Документований перекіс: коли джерело займання не знайдено,",
              13.5, INK, "start", "bold")
    s += text(L + 14, by + 46,
              "його часто списують на статику — бо вона невидима й нічого по собі не лишає.",
              13.5, INK, "start")
    s += text(L + 14, by + 63,
              "Понад половина пилових вибухів у статистиці — від БЕЗПОЛУМ'ЯНИХ джерел (тертя, гарячі поверхні), не обов'язково статика.",
              11.5, GREY, "start", style="italic")
    save("fig-r10-s5hist-energy-ladder.svg", s)


# ── Рис. 1.10.5і.2 — механізм вибухів танкерів 1969 і роль інертного газу ─────
def fig_tank_washing():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 32, "Танкери 1969: заряджений туман у порожньому танку",
              21, INK, "middle", "bold")
    s += text(W / 2, 54, "ланцюг подій під час миття танку струменем води — і де його розриває інертний газ",
              12.5, GREY, "middle", style="italic")

    # ── ліворуч: розріз танку ───────────────────────────────────────────────
    tx, ty, tw, th = 60, 90, 360, 420
    s += rect(tx, ty, tw, th, fill="#f4f7fb", stroke=INK, sw=2.4, rx=6)
    s += text(tx + tw / 2, ty - 12, "Вантажний танк (у баласті, після зливу нафти)",
              13, INK, "middle", "bold")

    # машинка-мийка зверху
    mx, my = tx + tw / 2, ty + 26
    s += rect(mx - 26, my - 18, 52, 26, fill="#dfe6ee", stroke=INK, sw=2, rx=4)
    s += text(mx, my - 1, "мийка", 11.5, INK, "middle", "bold")

    # струмені води (дві косі лінії) + бризки
    s += arrow(mx - 10, my + 8, tx + 70, ty + th - 60, BLUE, 2.6)
    s += arrow(mx + 10, my + 8, tx + tw - 70, ty + th - 60, BLUE, 2.6)
    s += text(tx + 86, ty + th - 70, "струмінь води", 12, BLUE, "middle", "bold")

    # заряджений туман — хмара крапель із зарядами
    import math as _m
    cx, cy = tx + tw / 2, ty + 150
    for i, (dx, dy, q) in enumerate([
        (-70, -10, "−"), (-30, 25, "−"), (10, -20, "−"), (55, 15, "−"),
        (-50, 55, "−"), (30, 50, "+"), (75, -25, "−"), (-10, 80, "−"),
        (-90, 35, "−"), (90, 45, "−")]):
        col = RED if q == "+" else BLUE
        s += circle(cx + dx, cy + dy, 8.5, fill="#ffffff", stroke=col, sw=1.8)
        s += text(cx + dx, cy + dy + 4.5, q, 12, col, "middle", "bold")
    s += text(cx, cy - 60, "заряджений водяний туман", 12.5, INK, "middle", "bold")
    s += text(cx, cy - 44, "(краплі несуть надлишок заряду)", 11, GREY, "middle")

    # накопичення заряду → виступ/конструкція → розряд
    proj_x, proj_y = tx + tw - 48, ty + 210
    s += line(tx + tw, proj_y - 30, proj_x, proj_y, INK, 3)  # виступ конструкції
    s += circle(proj_x, proj_y, 4, fill=INK, stroke=INK, sw=1)
    s += text(tx + tw - 6, proj_y - 36, "виступ", 11, INK, "end")
    # розряд (іскра) від хмари до виступу
    s += spark(cx + 70, cy + 30, proj_x, proj_y, color=RED, w=2.6)
    s += text(proj_x - 6, proj_y + 22, "розряд", 12, RED, "end", "bold")

    # пара палива внизу (залишкові вуглеводні)
    s += rect(tx + 8, ty + th - 52, tw - 16, 44, fill="#fdeede", stroke=ORANGE, sw=1.6, rx=4)
    s += text(tx + tw / 2, ty + th - 26, "пара вуглеводнів + повітря = горюча суміш",
              12.5, ORANGE, "middle", "bold")

    # ── праворуч: ланцюг подій + трикутник горіння ─────────────────────────
    rx0 = tx + tw + 70
    s += text(rx0, ty + 4, "Ланцюг подій", 15, INK, "start", "bold")
    steps = [
        ("1", "Струмінь б'є по сталі й рідині", BLUE),
        ("2", "Краплі зриваються зарядженими", BLUE),
        ("3", "Туман піднімає потенціал у танку", INK),
        ("4", "Біля виступу — пробій, ІСКРА", RED),
        ("5", "Іскра + пара палива → ВИБУХ", RED),
    ]
    yy = ty + 34
    for n, txt, col in steps:
        s += circle(rx0 + 12, yy, 12, fill="#ffffff", stroke=col, sw=2)
        s += text(rx0 + 12, yy + 4.5, n, 12.5, col, "middle", "bold")
        s += text(rx0 + 34, yy + 5, txt, 13, INK, "start")
        if n != "5":
            s += arrow(rx0 + 12, yy + 13, rx0 + 12, yy + 31, GREY, 1.8)
        yy += 44

    # трикутник горіння + як інертний газ його розриває
    tcx, tcy, tr = rx0 + 130, yy + 78, 74
    p1 = (tcx, tcy - tr)             # вершина: ПАЛИВО
    p2 = (tcx - tr * 0.92, tcy + tr * 0.6)  # КИСЕНЬ
    p3 = (tcx + tr * 0.92, tcy + tr * 0.6)  # ДЖЕРЕЛО
    s += polygon([p1, p2, p3], fill="#fff7ef", stroke=ORANGE, sw=2.4)
    s += text(p1[0], p1[1] - 8, "ПАЛИВО", 12, INK, "middle", "bold")
    s += text(p1[0], p1[1] + 8, "(пара)", 10.5, GREY, "middle")
    s += text(p2[0] - 4, p2[1] + 16, "КИСЕНЬ", 12, INK, "middle", "bold")
    s += text(p3[0] + 4, p3[1] + 16, "ІСКРА", 12, INK, "middle", "bold")
    s += text(tcx, tcy + 6, "трикутник", 11.5, GREY, "middle")
    s += text(tcx, tcy + 21, "горіння", 11.5, GREY, "middle")

    # інертний газ прибирає кисень — перекреслюємо вершину КИСЕНЬ
    s += line(p2[0] - 26, p2[1] - 8, p2[0] + 22, p2[1] + 20, RED, 3)
    # підсумок-рядок на повну ширину знизу (щоб не вилазив за правий край)
    cby = H - 58
    s += rect(60, cby, W - 120, 44, fill="#eef6ef", stroke=GREEN, sw=1.4, rx=8)
    s += text(74, cby + 19,
              "Розв'язок: інертний газ (O₂ < 5 %) прибирає кисень —", 12.5, GREEN, "start", "bold")
    s += text(74, cby + 36,
              "трикутник розпадається, навіть якщо іскра є. Так на танкерах з'явилися системи інертного газу (IGS).",
              12, GREEN, "start")

    save("fig-r10-s5hist-tank-washing.svg", s)


if __name__ == "__main__":
    fig_energy_ladder()
    fig_tank_washing()
    print("done")
