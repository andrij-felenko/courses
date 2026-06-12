# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 28 — «Фізика давачів» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; для історії до розділу — секція 0 (Рис. 28.0.N).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+) / гаряче
BLUE  = "#1f47b5"   # від'ємний (−) / холодне
GREEN = "#1f8a3b"   # поле / напруга
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
HOT   = "#e8702a"   # полум'я
HOTF  = "#fff0e2"   # бліде тепле тло
COLDF = "#e8f1fb"   # бліде холодне тло
WARMF = "#fbf3e2"   # бліде «жовте» тло
METALA = "#b07a32"  # метал A (тепла сурма/хромель)
METALB = "#6f7e8c"  # метал B (холодний вісмут/алюмель)
COPPER = "#b5651d"  # мідь
GOLD  = "#caa24a"
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
        f'  <marker id="aHot" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{HOT}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", HOT: "aHot"}


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
    if weight == "italic":          # зручність: italic у слоті ваги → курсив
        weight, style = "normal", "italic"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def dot(cx, cy, r=5, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def plus(cx, cy, r=11, color=RED, w=2.5):
    return (line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=11, color=BLUE, w=2.5):
    return line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)


def electron(cx, cy, r=7, fill=BLUE):
    """Електрон — синій кружок зі знаком −."""
    return (circle(cx, cy, r, fill="#dfe7f7", stroke=fill, w=1.5)
            + line(cx - r * 0.5, cy, cx + r * 0.5, cy, fill, 1.8))


def flame(cx, cy, scale=1.0):
    """Полум'я: зовнішній помаранчевий + внутрішній жовтий язик; вершина вгорі."""
    H = 46 * scale
    W = 14 * scale
    s = (f'<path d="M {cx:.1f},{cy:.1f} '
         f'C {cx-W:.1f},{cy-H*0.2:.1f} {cx-W*0.7:.1f},{cy-H*0.75:.1f} {cx:.1f},{cy-H:.1f} '
         f'C {cx+W*0.7:.1f},{cy-H*0.75:.1f} {cx+W:.1f},{cy-H*0.2:.1f} {cx:.1f},{cy:.1f} Z" '
         f'fill="{HOT}"/>\n')
    s += (f'<path d="M {cx:.1f},{cy-H*0.12:.1f} '
          f'C {cx-W*0.5:.1f},{cy-H*0.3:.1f} {cx-W*0.35:.1f},{cy-H*0.62:.1f} {cx:.1f},{cy-H*0.78:.1f} '
          f'C {cx+W*0.35:.1f},{cy-H*0.62:.1f} {cx+W*0.5:.1f},{cy-H*0.3:.1f} {cx:.1f},{cy-H*0.12:.1f} Z" '
          f'fill="#f6c84a"/>\n')
    return s


def snow(cx, cy, r=12, color=BLUE):
    """Сніжинка — 6 променів."""
    s = ""
    for k in range(6):
        a = math.radians(k * 60)
        s += line(cx, cy, cx + r * math.cos(a), cy + r * math.sin(a), color, 2)
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("  saved", name)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 28 — ефект Зеебека й термопара (секція 0)
# ════════════════════════════════════════════════════════════════════════════

def fig_seebeck_experiment():
    """Рис. 28.0.1 — петля з двох металів, нагрітий спай, відхилення компаса."""
    w, h = 680, 420
    s = header(w, h)
    s += text(w / 2, 30, "Дослід Зеебека (1821): петля з двох металів і компас",
              16, INK, "middle", "bold")

    xL, xR, ym = 185, 495, 130
    yT, yB = 92, 168
    # дві гілки-метали (кожна — 3 сегменти: вгору, поперек, вниз)
    s += poly([(xL, ym), (xL, yT), (xR, yT), (xR, ym)], color=METALA, w=7)
    s += poly([(xL, ym), (xL, yB), (xR, yB), (xR, ym)], color=METALB, w=7)
    s += text(xH := (xL + xR) / 2, yT - 10, "метал A  (сурма, Sb)", 13, METALA, "middle", "bold")
    s += text(xH, yB + 22, "метал B  (вісмут, Bi)", 13, METALB, "middle", "bold")

    # вузли-спаї
    s += dot(xL, ym, 7, INK)
    s += dot(xR, ym, 7, INK)

    # лівий спай — гарячий
    s += flame(xL, ym + 52, 1.0)
    s += text(xL, ym + 70, "нагрів", 12, HOT, "middle", "bold")
    s += text(xL - 8, ym - 14, "гарячий спай  T₁", 12.5, RED, "end", "bold")
    # правий спай — холодний
    s += snow(xR + 30, ym, 11)
    s += text(xR + 8, ym - 14, "холодний спай  T₂", 12.5, BLUE, "start", "bold")

    # струм по петлі (за годинниковою): верх ←, низ →  (умовний напрям)
    s += arrow(xH + 30, yT, xH - 30, yT, GREEN, 3)
    s += arrow(xH - 30, yB, xH + 30, yB, GREEN, 3)
    s += text(xH, yT - 24, "термострум  I", 12.5, GREEN, "middle", "italic")

    # вплив на компас (пунктир від верхньої гілки вниз)
    s += line(xH, yT + 4, xH, 250, GREY, 1.4, dash="3,4")

    # компас
    ccx, ccy, cr = xH, 300, 46
    s += circle(ccx, ccy, cr, fill="#ffffff", stroke=INK, w=2)
    s += circle(ccx, ccy, cr + 5, fill="none", stroke=GREY, w=1)
    for k in range(8):
        a = math.radians(k * 45)
        s += line(ccx + (cr - 6) * math.cos(a), ccy + (cr - 6) * math.sin(a),
                  ccx + cr * math.cos(a), ccy + cr * math.sin(a), GREY, 1)
    # стрілка, відхилена на ~35°
    ang = math.radians(-35 - 90)  # від вертикалі
    nx, ny = math.cos(ang), math.sin(ang)
    s += line(ccx - nx * (cr - 12), ccy - ny * (cr - 12),
              ccx + nx * (cr - 12), ccy + ny * (cr - 12), GREY, 1, dash="2,3")
    s += f'<path d="M {ccx + nx*(cr-12):.1f},{ccy + ny*(cr-12):.1f} L {ccx - nx*8 + ny*7:.1f},{ccy - ny*8 - nx*7:.1f} L {ccx - nx*8 - ny*7:.1f},{ccy - ny*8 + nx*7:.1f} Z" fill="{RED}"/>\n'
    s += f'<path d="M {ccx - nx*(cr-12):.1f},{ccy - ny*(cr-12):.1f} L {ccx + nx*8 + ny*7:.1f},{ccy + ny*8 - nx*7:.1f} L {ccx + nx*8 - ny*7:.1f},{ccy + ny*8 + nx*7:.1f} Z" fill="{BLUE}"/>\n'
    s += dot(ccx, ccy, 3, INK)
    s += text(ccx, ccy + cr + 22, "стрілка відхиляється", 12.5, INK, "middle", "italic")

    # пояснювальна рамка
    bx, by = 510, 248
    s += rect(bx, by, 158, 142, fill="#fbfbf6", stroke=GREY, sw=1.2, rx=6)
    s += text(bx + 10, by + 22, "Що бачив Зеебек:", 12.5, INK, "start", "bold")
    for i, ln in enumerate([
        "стрілка хитнулась →",
        "він вирішив, що це",
        "магнетизм («термо-",
        "магнетизм»).",
        "Насправді ΔT гонить",
        "струм, а струм хитає",
        "стрілку (Ерстед, 1820).",
    ]):
        s += text(bx + 10, by + 42 + i * 15, ln, 11.5, INK, "start")

    save("fig-28-0-1-seebeck-experiment.svg", s)


def fig_diffusion():
    """Рис. 28.0.2 — мікромеханізм: носії дифундують гарячий→холодний → напруга."""
    w, h = 660, 360
    s = header(w, h)
    s += text(w / 2, 30, "Чому ΔT робить напругу: носії тікають з гарячого кінця",
              16, INK, "middle", "bold")

    xL, xR = 120, 540
    yT, yB = 110, 188
    midY = (yT + yB) / 2
    # стрижень із градієнтом тла (двома половинами)
    s += rect(xL, yT, (xR - xL) / 2, yB - yT, fill=HOTF, stroke="none")
    s += rect(xL + (xR - xL) / 2, yT, (xR - xL) / 2, yB - yT, fill=COLDF, stroke="none")
    s += rect(xL, yT, xR - xL, yB - yT, fill="none", stroke=INK, sw=2)
    s += text(xL + 50, yT - 12, "гарячий кінець (T↑)", 12.5, RED, "middle", "bold")
    s += text(xR - 60, yT - 12, "холодний кінець (T↓)", 12.5, BLUE, "middle", "bold")

    # електрони: біля гарячого — довгі стрілки руху, накопичення біля холодного
    import_e = [
        (xL + 35, midY - 14, 34), (xL + 60, midY + 16, 30), (xL + 95, midY - 4, 26),
        (xL + 135, midY + 10, 20), (xL + 180, midY - 12, 16),
    ]
    for (ex, ey, ln) in import_e:
        s += arrow(ex, ey, ex + ln, ey - 2, INK, 1.6)
        s += electron(ex, ey)
    # накопичення біля холодного кінця
    for (ex, ey) in [(xR - 30, midY - 16), (xR - 30, midY + 2), (xR - 30, midY + 18),
                     (xR - 52, midY - 8), (xR - 52, midY + 12), (xR - 14, midY)]:
        s += electron(ex, ey)

    # знаки на кінцях
    s += text(xL + 16, midY + 5, "+", 26, RED, "middle", "bold")
    s += text(xR - 8, midY + 5, "−", 26, BLUE, "middle", "bold")

    # вольтметр між кінцями
    s += line(xL, yB, xL, 250, INK, 2)
    s += line(xR, yB, xR, 250, INK, 2)
    s += line(xL, 250, 300, 250, INK, 2)
    s += line(xR, 250, 360, 250, INK, 2)
    s += circle(330, 250, 26, fill="#ffffff", stroke=INK, w=2)
    s += text(330, 256, "V", 17, GREEN, "middle", "bold")

    # формула
    s += text(w / 2, 312, "ΔV = S · ΔT      (S — коефіцієнт Зеебека, мкВ/°C)",
              15, GREEN, "middle", "bold")
    s += text(w / 2, 336,
              "гарячі носії енергійніші → дифундують до холодного → там надлишок (−), тут нестача (+)",
              12.5, INK, "middle", "italic")
    save("fig-28-0-2-diffusion.svg", s)


def fig_three_effects():
    """Рис. 28.0.3 — три термоелектричні ефекти й об'єднання Кельвіна."""
    w, h = 720, 400
    s = header(w, h)
    s += text(w / 2, 28, "Три термоелектричні ефекти — одне сімейство",
              16, INK, "middle", "bold")

    bw, bh, by = 210, 168, 70
    gap = 18
    x0 = (w - (3 * bw + 2 * gap)) / 2

    def junction(cx, cy, hot_left=True):
        """маленький спай двох металів."""
        out = poly([(cx - 34, cy + 16), (cx, cy - 6), (cx + 34, cy + 16)], color=METALA, w=5)
        out += poly([(cx - 34, cy + 16), (cx, cy - 6)], color=METALA, w=5)
        out += poly([(cx, cy - 6), (cx + 34, cy + 16)], color=METALB, w=5)
        out += dot(cx, cy - 6, 5, INK)
        return out

    # Панель 1 — Зеебек
    bx = x0
    s += rect(bx, by, bw, bh, fill=HOTF, stroke=RED, sw=1.6, rx=8)
    s += text(bx + bw / 2, by + 24, "Зеебек · 1821", 14, RED, "middle", "bold")
    s += text(bx + bw / 2, by + 44, "тепло → напруга", 12.5, INK, "middle", "italic")
    s += junction(bx + bw / 2, by + 92)
    s += flame(bx + bw / 2, by + 132, 0.7)
    s += arrow(bx + 30, by + 92, bx + bw / 2 - 40, by + 92, RED, 2)
    s += text(bx + 16, by + 80, "ΔT", 13, RED, "middle", "bold")
    s += circle(bx + bw - 34, by + 92, 16, fill="#fff", stroke=INK, w=1.6)
    s += text(bx + bw - 34, by + 97, "V", 13, GREEN, "middle", "bold")
    s += arrow(bx + bw / 2 + 40, by + 92, bx + bw - 52, by + 92, GREEN, 2)
    s += text(bx + bw / 2, by + 158, "термопара", 11.5, GREY, "middle", "italic")

    # Панель 2 — Пельтьє
    bx = x0 + bw + gap
    s += rect(bx, by, bw, bh, fill=COLDF, stroke=BLUE, sw=1.6, rx=8)
    s += text(bx + bw / 2, by + 24, "Пельтьє · 1834", 14, BLUE, "middle", "bold")
    s += text(bx + bw / 2, by + 44, "струм → тепло/холод", 12.5, INK, "middle", "italic")
    s += junction(bx + bw / 2, by + 96)
    s += arrow(bx + 24, by + 96, bx + bw / 2 - 40, by + 96, INK, 2)
    s += text(bx + 18, by + 84, "I", 13, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 70, "▲ гріється", 11.5, RED, "middle", "bold")
    s += text(bx + bw / 2, by + 132, "▼ холоне", 11.5, BLUE, "middle", "bold")
    s += text(bx + bw / 2, by + 158, "Пельтьє-кулер", 11.5, GREY, "middle", "italic")

    # Панель 3 — Томсон
    bx = x0 + 2 * (bw + gap)
    s += rect(bx, by, bw, bh, fill=WARMF, stroke=GOLD, sw=1.6, rx=8)
    s += text(bx + bw / 2, by + 24, "Томсон · 1851", 14, "#9a7a1e", "middle", "bold")
    s += text(bx + bw / 2, by + 44, "струм+градієнт → тепло", 12, INK, "middle", "italic")
    s += rect(bx + 28, by + 84, bw - 56, 20, fill="#fff", stroke=INK, sw=1.6)
    # градієнт-стрілка
    s += arrow(bx + 34, by + 74, bx + bw - 40, by + 74, RED, 1.8)
    s += text(bx + bw / 2, by + 66, "градієнт T", 11, RED, "middle")
    s += arrow(bx + 34, by + 94, bx + bw - 44, by + 94, INK, 2)
    s += text(bx + 22, by + 116, "I", 12.5, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 132, "тепло вздовж дроту", 11.5, "#9a7a1e", "middle")
    s += text(bx + bw / 2, by + 158, "(передбачив теорією)", 11.5, GREY, "middle", "italic")

    # об'єднувальна стрічка
    s += rect(x0, by + bh + 22, 3 * bw + 2 * gap, 40, fill="#f2f6ff", stroke=INK, sw=1.4, rx=8)
    s += text(w / 2, by + bh + 47,
              "Кельвін (В. Томсон): термодинаміка зв'язала всі три — співвідношення Кельвіна",
              13, INK, "middle", "bold")
    save("fig-28-0-3-three-effects.svg", s)


def fig_thermocouple_sensor():
    """Рис. 28.0.4 — термопара як давач: вимірювальний і опорний спаї, ХКК, типи."""
    w, h = 720, 430
    s = header(w, h)
    s += text(w / 2, 28, "Термопара як давач: різниця спаїв і опорна точка",
              16, INK, "middle", "bold")

    # вимірювальний (гарячий) спай зліва — у пічці
    fx, fy = 95, 150
    s += rect(40, 95, 120, 120, fill=HOTF, stroke=HOT, sw=1.6, rx=6)
    s += text(100, 112, "піч / процес", 12, HOT, "middle", "bold")
    s += flame(100, 195, 0.8)
    s += dot(fx + 60, fy, 7, INK)
    s += text(fx + 60, fy - 14, "вимір. спай", 11.5, RED, "middle", "bold")
    s += text(fx + 60, fy + 28, "T_вимір", 12, RED, "middle", "italic")

    # два дроти до клемного блоку
    jx = fx + 60
    s += poly([(jx, fy), (260, 120), (430, 120)], color=METALA, w=6)
    s += poly([(jx, fy), (260, 180), (430, 180)], color=METALB, w=6)
    s += text(345, 110, "метал A", 11.5, METALA, "middle", "bold")
    s += text(345, 196, "метал B", 11.5, METALB, "middle", "bold")

    # опорний (холодний) спай — клемний блок + ХКК
    s += rect(430, 100, 120, 100, fill=COLDF, stroke=BLUE, sw=1.6, rx=6)
    s += dot(430, 120, 6, INK)
    s += dot(430, 180, 6, INK)
    s += text(490, 92, "опорний спай  T_оп", 11.5, BLUE, "middle", "bold")
    # мідні дроти далі
    s += line(550, 120, 610, 120, COPPER, 4)
    s += line(550, 180, 610, 180, COPPER, 4)
    s += text(580, 112, "мідь", 10.5, COPPER, "middle")
    # давач ХКК
    s += rect(452, 142, 76, 30, fill="#fff", stroke=INK, sw=1.4, rx=4)
    s += text(490, 162, "ХКК-давач", 11, INK, "middle", "bold")
    s += text(490, 214, "(або лазня з льодом 0 °C)", 10.5, GREY, "middle", "italic")

    # підсилювач + формула
    s += poly([(610, 105), (660, 150), (610, 195)], color=INK, w=1.8, fill="#fff")
    s += text(632, 155, "×", 16, GREEN, "middle", "bold")
    s += text(635, 230, "мкВ → В", 11, GREEN, "middle", "italic")

    s += text(w / 2, 270, "V ≈ S · (T_вимір − T_оп)      сигнал — десятки мкВ/°C",
              14, GREEN, "middle", "bold")
    s += text(w / 2, 292, "термопара міряє РІЗНИЦЮ спаїв → опорну треба знати окремо",
              12.5, INK, "middle", "italic")

    # таблиця типів
    tx, ty = 70, 312
    cols = [0, 60, 230, 360, 470, 580]
    rows_h = 22
    head = ["тип", "метали (сплави)", "S, мкВ/°C", "діапазон, °C", "де"]
    s += rect(tx, ty, 590, rows_h, fill="#eef1f6", stroke=GREY, sw=1)
    for i, htxt in enumerate(head):
        s += text(tx + cols[i] + 8, ty + 15, htxt, 11.5, INK, "start", "bold")
    data = [
        ["K", "хромель / алюмель", "≈ 41", "−200…+1260", "загальний"],
        ["J", "залізо / константан", "≈ 51", "0…+760", "старий пром."],
        ["T", "мідь / константан", "≈ 41", "−200…+370", "низькі t"],
        ["S", "Pt / Pt-Rh 10%", "≈ 7", "0…+1600", "еталон, печі"],
    ]
    for r, row in enumerate(data):
        yy = ty + rows_h * (r + 1)
        s += rect(tx, yy, 590, rows_h, fill="#ffffff", stroke=GREY, sw=0.8)
        for i, cell in enumerate(row):
            col = RED if i == 0 else INK
            wt = "bold" if i == 0 else "normal"
            s += text(tx + cols[i] + 8, yy + 15, cell, 11, col, "start", wt)
    save("fig-28-0-4-thermocouple-sensor.svg", s)


# ── додаткові помічники (сигнали й схемні символи) ───────────────────────────

def sine(x0, y0, w, amp, cycles=2, color=GREEN, sw=2):
    pts = []
    N = 48
    for i in range(N + 1):
        t = i / N
        pts.append((x0 + w * t, y0 - amp * math.sin(2 * math.pi * cycles * t)))
    return poly(pts, color, sw)


def square(x0, y0, w, h, cycles=3, color=INK, sw=2):
    seg = w / (cycles * 2)
    pts = [(x0, y0)]
    x, low = x0, True
    for _ in range(cycles * 2):
        ny = y0 - h if low else y0
        pts.append((x, ny))
        x += seg
        pts.append((x, ny))
        low = not low
    pts.append((x, y0))
    return poly(pts, color, sw)


def res_h(x0, y0, w, color=INK, sw=2, n=6):
    pts = [(x0, y0)]
    seg = w / n
    for i in range(n):
        pts.append((x0 + seg * (i + 0.5), y0 - 8 if i % 2 == 0 else y0 + 8))
    pts.append((x0 + w, y0))
    return poly(pts, color, sw)


def res_v(x0, y0, ht, color=INK, sw=2, n=6):
    pts = [(x0, y0)]
    seg = ht / n
    for i in range(n):
        pts.append((x0 - 8 if i % 2 == 0 else x0 + 8, y0 + seg * (i + 0.5)))
    pts.append((x0, y0 + ht))
    return poly(pts, color, sw)


def vmeter(cx, cy, r=20, label="V", color=GREEN):
    return circle(cx, cy, r, "#ffffff", INK, 2) + text(cx, cy + r * 0.32, label, int(r * 0.8), color, "middle", "bold")


def source(cx, cy, r=20):
    """Символ джерела ЕРС — кружок зі знаками +/−."""
    return (circle(cx, cy, r, "#ffffff", INK, 2)
            + text(cx, cy - r * 0.25, "+", 15, RED, "middle", "bold")
            + line(cx - 7, cy + r * 0.45, cx + 7, cy + r * 0.45, BLUE, 2.4))


# ════════════════════════════════════════════════════════════════════════════
#  §28.1 Що таке давач: фізична величина → електричний сигнал
# ════════════════════════════════════════════════════════════════════════════

def fig_translator():
    w, h = 680, 320
    s = header(w, h)
    s += text(w / 2, 28, "Давач — перекладач: фізична величина → електричний сигнал",
              16, INK, "middle", "bold")
    bx, by, bw, bh = 268, 92, 150, 152
    s += rect(bx, by, bw, bh, fill="#eef6ef", stroke=GREEN, sw=2, rx=10)
    s += text(bx + bw / 2, by + bh / 2 - 4, "ДАВАЧ", 19, GREEN, "middle", "bold")
    s += text(bx + bw / 2, by + bh / 2 + 18, "перетворювач", 12, INK, "middle", "italic")

    s += text(118, 78, "ФІЗИЧНИЙ СВІТ", 12, GREY, "middle", "bold")
    measur = [("температура", "ефект Зеебека"), ("світло", "фотоефект"),
              ("сила / тиск", "п'єзоефект"), ("відстань", "час відлуння")]
    for i, (m, eff) in enumerate(measur):
        yy = 122 + i * 36
        s += text(52, yy, m, 13.5, INK, "start", "bold")
        s += text(52, yy + 15, eff, 10.5, GREY, "start", "italic")
        s += arrow(206, yy - 4, bx - 6, yy - 4, INK, 2)

    s += text(585, 78, "ЕЛЕКТРИКА", 12, GREY, "middle", "bold")
    s += sine(470, by + bh / 2 - 34, 86, 12, 2, GREEN, 2)
    s += arrow(bx + bw + 6, by + bh / 2, 560, by + bh / 2, GREEN, 2.5)
    s += text(588, by + bh / 2 - 2, "напруга", 14, GREEN, "middle", "bold")
    s += text(588, by + bh / 2 + 18, "→ число", 11.5, INK, "middle", "italic")
    save("fig-28-1-1-translator.svg", s)


def _chain_boxes(stages, y, bh=72, x0=30, x1=690):
    """Малює ряд боксів-ланок зі стрілками; повертає (svg, centers_x)."""
    n = len(stages)
    bw = 116
    gap = (x1 - x0 - n * bw) / (n - 1)
    out, cx = "", []
    for i, (title, sub, col) in enumerate(stages):
        bx = x0 + i * (bw + gap)
        out += rect(bx, y, bw, bh, fill="#ffffff", stroke=col, sw=2, rx=8)
        out += text(bx + bw / 2, y + 28, title, 12, INK, "middle", "bold")
        out += text(bx + bw / 2, y + 48, sub, 10.5, col, "middle", "italic")
        cx.append(bx + bw / 2)
        if i > 0:
            out += arrow(cx[i - 1] + bw / 2 + 3, y + bh / 2, bx - 4, y + bh / 2, INK, 2)
    return out, cx, bw


def fig_chain():
    w, h = 720, 220
    s = header(w, h)
    s += text(w / 2, 28, "Вимірювальний ланцюг: від величини до числа",
              16, INK, "middle", "bold")
    stages = [
        ("величина", "T, світло…", GREY),
        ("чутл. елемент", "Розділ 28", GREEN),
        ("нормування", "підсил. Розд.13", BLUE),
        ("АЦП", "Розділ 26", RED),
        ("число в МК", "Модуль 4", INK),
    ]
    body, cx, bw = _chain_boxes(stages, 78)
    s += body
    s += text(w / 2, 180, "сирий мкВ-сигнал → підсилений → відфільтрований → оцифрований → зміст",
              12.5, INK, "middle", "italic")
    save("fig-28-1-2-chain.svg", s)


def fig_families():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 28, "Дві сім'ї давачів за джерелом енергії сигналу",
              16, INK, "middle", "bold")

    # ── ліворуч: самогенерувальний ──
    s += rect(30, 50, 310, 246, fill=HOTF, stroke=RED, sw=1.6, rx=10)
    s += text(185, 74, "САМОГЕНЕРУВАЛЬНИЙ", 13.5, RED, "middle", "bold")
    s += text(185, 92, "сам джерело ЕРС — живлення не треба", 11, INK, "middle", "italic")
    # стрілка енергії (тепло/світло) у давач-джерело
    s += arrow(70, 150, 120, 150, HOT, 2.4)
    s += text(70, 138, "тепло/світло", 10.5, HOT, "middle")
    s += source(150, 150, 22)
    s += line(150, 172, 150, 210, INK, 2)
    s += line(172, 150, 250, 150, INK, 2)
    s += line(250, 150, 250, 210, INK, 2)
    s += line(150, 210, 224, 210, INK, 2)
    s += vmeter(250, 210, 20, "V")
    s += line(270, 210, 250, 210, INK, 2)
    s += text(150, 250, "термопара · фотодіод · п'єзо", 11, INK, "middle", "bold")
    s += text(185, 282, "сигнал малий, але автономний", 11, GREY, "middle", "italic")

    # ── праворуч: параметричний (дільник напруги з давачем-резистором) ──
    s += rect(360, 50, 310, 246, fill=COLDF, stroke=BLUE, sw=1.6, rx=10)
    s += text(515, 74, "ПАРАМЕТРИЧНИЙ", 13.5, BLUE, "middle", "bold")
    s += text(515, 92, "змінний R/C/L — його треба живити", 11, INK, "middle", "italic")
    xv, yt, yb = 560, 118, 256          # вісь дільника, верх/низ
    # опорне джерело зліва
    s += source(412, 187, 18)
    s += text(412, 158, "V_оп", 11, INK, "middle", "bold")
    s += line(412, 169, 412, yt, INK, 2)        # + до верхньої шини
    s += line(412, yt, xv, yt, INK, 2)          # верхня шина
    s += line(412, 205, 412, yb, INK, 2)        # − до нижньої шини
    s += line(412, yb, xv, yb, INK, 2)          # нижня шина
    # верхнє (фіксоване) плече
    s += res_v(xv, yt, 50, INK, 2)
    s += text(xv + 16, yt + 28, "R", 12, INK, "start", "bold")
    # середня точка (вузол) → АЦП
    s += dot(xv, yt + 58, 4, INK)
    s += line(xv, yt + 50, xv, yt + 66, INK, 2)
    s += line(xv, yt + 58, 632, yt + 58, GREEN, 2)
    s += text(636, yt + 62, "→ АЦП", 11, GREEN, "start", "bold")
    # нижнє плече — давач (змінний R)
    s += res_v(xv, yt + 66, 50, GREEN, 2.4)
    s += line(xv, yt + 116, xv, yb, INK, 2)
    s += arrow(xv + 40, yt + 92, xv + 12, yt + 90, GREEN, 1.8)
    s += text(xv + 44, yt + 96, "R(вимір.)", 10.5, GREEN, "start", "bold")
    s += text(515, 282, "терморезистор · фоторезистор · ємнісний", 10.5, GREY, "middle", "italic")
    save("fig-28-1-3-families.svg", s)


def fig_duality():
    w, h = 680, 300
    s = header(w, h)
    s += text(w / 2, 28, "Перетворювач читається у два боки: давач ↔ виконавчий пристрій",
              15.5, INK, "middle", "bold")
    # центральний блок
    bx, by, bw, bh = 285, 78, 110, 80
    s += rect(bx, by, bw, bh, fill="#f2f0fb", stroke="#6a4ea8", sw=2, rx=8)
    s += text(bx + bw / 2, by + 34, "перетво-", 12.5, "#6a4ea8", "middle", "bold")
    s += text(bx + bw / 2, by + 52, "рювач", 12.5, "#6a4ea8", "middle", "bold")
    s += text(120, by + 20, "ФІЗИЧНЕ", 12.5, GREY, "middle", "bold")
    s += text(560, by + 20, "ЕЛЕКТРИЧНЕ", 12.5, GREY, "middle", "bold")
    # давач: фіз → ел (верхня стрілка зліва направо)
    s += arrow(150, by + 40, bx - 6, by + 40, GREEN, 2.4)
    s += arrow(bx + bw + 6, by + 40, 540, by + 40, GREEN, 2.4)
    s += text(bx + bw / 2, by - 6, "давач:  фізичне → електричне", 12, GREEN, "middle", "bold")
    # актуатор: ел → фіз (нижня стрілка справа наліво)
    s += arrow(540, by + 116, bx + bw + 6, by + 116, RED, 2.4)
    s += arrow(bx - 6, by + 116, 150, by + 116, RED, 2.4)
    s += text(bx + bw / 2, by + 138, "виконавчий пристрій:  електричне → фізичне", 12, RED, "middle", "bold")

    # таблиця пар
    pairs = [["динамік", "↔", "мікрофон"], ["мотор", "↔", "генератор"],
             ["п'єзо-пищалка", "↔", "давач удару"], ["Пельтьє", "↔", "термопара"]]
    ty = 196
    s += text(w / 2, ty, "та сама фізика — два застосування:", 12, INK, "middle", "italic")
    for i, (a, m, b) in enumerate(pairs):
        xx = 90 + i * 140
        s += rect(xx - 8, ty + 16, 130, 36, fill="#fafafa", stroke=GREY, sw=1, rx=6)
        s += text(xx + 57, ty + 33, a, 11, RED, "middle", "bold")
        s += text(xx + 57, ty + 47, b, 11, GREEN, "middle", "bold")
    save("fig-28-1-4-duality.svg", s)


def fig_output_forms():
    w, h = 700, 350
    s = header(w, h)
    s += text(w / 2, 28, "Форми вихідного сигналу давача — і чим читати кожну",
              16, INK, "middle", "bold")
    rows = [
        ("напруга", "просто на АЦП; боїться завад і падіння на дротах", "V"),
        ("струм 4–20 мА", "однаковий уздовж кола → стійкий на відстані", "I"),
        ("зміна R / C", "потребує дільника чи моста, далі АЦП", "RC"),
        ("частота / період", "рахує таймер — точно, без аналогу", "F"),
        ("цифрове число", "давач уже містить АЦП; читаємо готове", "D"),
    ]
    y0, dy = 64, 54
    for i, (name, note, kind) in enumerate(rows):
        yy = y0 + i * dy
        s += rect(28, yy, 644, 46, fill="#fbfbfb", stroke=FAINT, sw=1, rx=6)
        s += text(46, yy + 28, name, 13, INK, "start", "bold")
        # міні-ілюстрація
        gx = 210
        if kind == "V":
            s += line(gx, yy + 33, gx + 90, yy + 13, GREEN, 2.2)
        elif kind == "I":
            s += rect(gx, yy + 14, 90, 22, fill="none", stroke=RED, sw=1.6, rx=4)
            s += arrow(gx + 8, yy + 25, gx + 78, yy + 25, RED, 1.8)
        elif kind == "RC":
            s += res_h(gx, yy + 24, 90, INK, 2)
        elif kind == "F":
            s += square(gx, yy + 36, 90, 22, 3, BLUE, 2)
        elif kind == "D":
            s += text(gx + 45, yy + 30, "0 1 0 1 1 0", 14, "#6a4ea8", "middle", "bold")
        s += text(326, yy + 28, note, 11.5, INK, "start")
    save("fig-28-1-5-output-forms.svg", s)


def fig_imperfect_chain():
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 28, "Кожна ланка щось спотворює — і кожна має свою тему далі",
              15.5, INK, "middle", "bold")
    stages = [
        ("величина", "істина", GREY),
        ("чутл. елемент", "Розділ 28", GREEN),
        ("підсил.", "Розділ 13", BLUE),
        ("АЦП", "Розділ 26", RED),
        ("число", "оцінка", INK),
    ]
    body, cx, bw = _chain_boxes(stages, 120)
    s += body
    # джерела похибок над ланками (червоним) → донизу в ланку
    s += text(cx[1], 82, "нелінійність / дрейф / шум", 10.5, RED, "middle", "bold")
    s += arrow(cx[1], 90, cx[1], 116, RED, 1.8)
    s += text(cx[2], 100, "зсув, смуга", 10.5, RED, "middle", "bold")
    s += arrow(cx[2], 106, cx[2], 116, RED, 1.8)
    s += text(cx[3], 82, "квантування", 10.5, RED, "middle", "bold")
    s += arrow(cx[3], 90, cx[3], 116, RED, 1.8)
    # теми, що це лікують, — під ланками (зеленим)
    s += text(cx[1], 214, "§28.4–28.5", 11, GREEN, "middle", "bold")
    s += arrow(cx[1], 196, cx[1], 210, GREEN, 1.8)
    s += text(cx[2], 214, "§28.5 / Розд.30", 11, GREEN, "middle", "bold")
    s += arrow(cx[2], 196, cx[2], 210, GREEN, 1.8)
    s += text(cx[3], 214, "§28.6 калібр.", 11, GREEN, "middle", "bold")
    s += arrow(cx[3], 196, cx[3], 210, GREEN, 1.8)
    s += text(w / 2, 256, "давач дає не істину, а підказку — її треба грамотно витлумачити",
              13, INK, "middle", "italic")
    save("fig-28-1-6-imperfect-chain.svg", s)


# ── символи для §28.2 (конденсатор, котушка, AC-джерело, серпантин, промені) ──

def cap_plates(cx, cy, gap, ph, color=INK, sw=3):
    return (line(cx - gap / 2, cy - ph / 2, cx - gap / 2, cy + ph / 2, color, sw)
            + line(cx + gap / 2, cy - ph / 2, cx + gap / 2, cy + ph / 2, color, sw))


def coil_h(x0, y0, w, n=4, color=INK, sw=2):
    r = w / (2 * n)
    s = ""
    for i in range(n):
        cx = x0 + r * (2 * i + 1)
        s += (f'<path d="M {cx - r:.1f},{y0:.1f} A {r:.1f},{r:.1f} 0 1 1 {cx + r:.1f},{y0:.1f}" '
              f'fill="none" stroke="{color}" stroke-width="{sw}"/>\n')
    return s


def ac_source(cx, cy, r=18, color=INK):
    return circle(cx, cy, r, "#ffffff", color, 2) + sine(cx - 10, cy, 20, 6, 1, color, 1.8)


def serpentine(x0, y0, w, ht, n, color, sw=2):
    seg = w / n
    pts = []
    for i in range(n + 1):
        x = x0 + i * seg
        pts += ([(x, y0), (x, y0 + ht)] if i % 2 == 0 else [(x, y0 + ht), (x, y0)])
    return poly(pts, color, sw)


def rays(cx, cy, color=GOLD, n=3):
    s = ""
    for k in range(n):
        dx = (k - (n - 1) / 2) * 12
        s += arrow(cx + dx - 22, cy - 30, cx + dx - 4, cy - 8, color, 1.6)
    return s


# ════════════════════════════════════════════════════════════════════════════
#  §28.2 Класи перетворювачів: резистивні, ємнісні, індуктивні
# ════════════════════════════════════════════════════════════════════════════

def fig_three_handles():
    w, h = 690, 280
    s = header(w, h)
    s += text(w / 2, 28, "Одна ідея на три родини: світ крутить ручку в R, C або L",
              15.5, INK, "middle", "bold")
    s += text(w / 2, 47, "червоне — матеріал,  синє — геометрія (саме їх змінює фізична величина)",
              11, GREY, "middle", "italic")
    rows = [
        ("резистор", "R = ", ("ρ", RED), (" · L / A", BLUE), "нагрів / світло → ρ;   розтяг → L, A"),
        ("конденсатор", "C = ", ("ε", RED), (" · A / d", BLUE), "волога → ε;   тиск → d;   зсув → A"),
        ("котушка", "L = ", ("μ", RED), (" · N² · A / ℓ", BLUE), "метал / рух осердя → μ та магн. шлях"),
    ]
    y0, bh = 62, 58
    for i, (name, lhs, mat, geo, note) in enumerate(rows):
        by = y0 + i * (bh + 10)
        s += rect(30, by, w - 60, bh, fill="#fbfbfb", stroke=FAINT, sw=1.2, rx=8)
        s += text(50, by + 35, name, 13, INK, "start", "bold")
        s += text(178, by + 36, lhs, 17, INK, "start", "bold")
        s += text(178 + 42, by + 36, mat[0], 18, mat[1], "start", "bold")
        s += text(178 + 60, by + 36, geo[0], 17, geo[1], "start", "bold")
        s += text(400, by + 36, note, 11, GREY, "start", "italic")
    save("fig-28-2-1-three-handles.svg", s)


def fig_resistive():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Резистивні давачі: чотири способи змінити опір",
              16, INK, "middle", "bold")
    px = [20, 195, 370, 545]
    pw, py, ph = 155, 48, 178
    titles = ["терморезистор", "фоторезистор", "тензодавач", "потенціометр"]
    handles = ["ρ(T)", "ρ(світло)", "L · A", "положення"]
    for i in range(4):
        x = px[i]
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=FAINT, sw=1.2, rx=8)
        s += text(x + pw / 2, py + 22, titles[i], 12.5, INK, "middle", "bold")
        s += text(x + pw / 2, py + ph - 14, handles[i], 13, GREEN, "middle", "bold")
        cy = py + 96
        if i == 0:      # терморезистор
            s += res_h(x + 30, cy, 95, INK, 2.4)
            s += flame(x + pw / 2, cy + 46, 0.7)
        elif i == 1:    # фоторезистор
            s += res_h(x + 30, cy, 95, INK, 2.4)
            s += rays(x + pw / 2, cy - 6, GOLD, 3)
        elif i == 2:    # тензодавач
            s += rect(x + 24, cy - 4, 108, 30, fill="#eef0f2", stroke=GREY, sw=1, rx=3)
            s += serpentine(x + 34, cy + 2, 88, 16, 7, RED, 2)
            s += arrow(x + 30, cy + 40, x + 8, cy + 40, INK, 2)
            s += arrow(x + pw - 30, cy + 40, x + pw - 8, cy + 40, INK, 2)
            s += text(x + pw / 2, cy + 56, "розтяг", 10.5, INK, "middle", "italic")
        elif i == 3:    # потенціометр
            s += res_h(x + 30, cy, 95, INK, 2.4)
            s += arrow(x + pw / 2, cy - 34, x + pw / 2, cy - 8, BLUE, 2)
            s += text(x + pw / 2, cy - 40, "повзунок", 10, BLUE, "middle", "bold")
    save("fig-28-2-2-resistive.svg", s)


def _bridge(px, py, pw, ph, delta=False):
    """Один міст із двох вертикальних дільників; повертає svg."""
    pt, pb = py + 34, py + ph - 26
    midY = (pt + pb) / 2
    lx, rx = px + 78, px + pw - 78
    cxm = (lx + rx) / 2
    out = ""
    # шини живлення
    out += line(lx, pt, rx, pt, INK, 2)
    out += line(lx, pb, rx, pb, INK, 2)
    out += text(cxm, pt - 8, "V_зб", 11, INK, "middle", "bold")
    # «земля»
    out += line(cxm - 10, pb + 8, cxm + 10, pb + 8, INK, 2)
    out += line(cxm - 6, pb + 12, cxm + 6, pb + 12, INK, 1.6)
    # ліве плече (фіксоване)
    out += res_v(lx, pt + 6, midY - pt - 14, INK, 2)
    out += dot(lx, midY, 4, INK)
    out += res_v(lx, midY + 8, pb - midY - 14, INK, 2)
    # праве плече (нижній резистор — давач)
    out += res_v(rx, pt + 6, midY - pt - 14, INK, 2)
    out += dot(rx, midY, 4, INK)
    sens_col = GREEN
    out += res_v(rx, midY + 8, pb - midY - 14, sens_col, 2.4)
    out += text(rx + 16, midY + 34, "R+ΔR" if delta else "R", 11, sens_col, "start", "bold")
    # вольтметр у центрі між вузлами
    out += line(lx, midY, cxm - 20, midY, INK, 2)
    out += line(rx, midY, cxm + 20, midY, INK, 2)
    out += vmeter(cxm, midY, 19, "V")
    out += text(cxm, midY + 40, "V = ΔV" if delta else "V = 0",
                12, (GREEN if delta else GREY), "middle", "bold")
    return out


def fig_wheatstone():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 26, "Міст Вітстона: прибрати велику базу, лишити чисту ΔR",
              15.5, INK, "middle", "bold")
    s += rect(24, 44, 326, 256, fill="#f6f9f6", stroke=GREY, sw=1.2, rx=8)
    s += text(187, 64, "збалансований", 13, INK, "middle", "bold")
    s += _bridge(24, 64, 326, 232, delta=False)
    s += rect(360, 44, 316, 256, fill="#f1f7f1", stroke=GREEN, sw=1.4, rx=8)
    s += text(518, 64, "давач змінив опір на ΔR", 13, GREEN, "middle", "bold")
    s += _bridge(360, 64, 316, 232, delta=True)
    save("fig-28-2-3-wheatstone.svg", s)


def fig_capacitive():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Ємнісний давач: три ручки формули C = ε·A/d",
              16, INK, "middle", "bold")
    px = [30, 270, 510]
    pw, py, ph = 180, 48, 180
    titles = ["зазор d", "площа A", "діелектрик ε"]
    notes = ["тиск, наближення", "положення, зсув", "волога, рівень рідини"]
    for i in range(3):
        x = px[i]
        s += rect(x, py, pw, ph, fill="#eef4fb", stroke=BLUE, sw=1.3, rx=8)
        s += text(x + pw / 2, py + 22, titles[i], 13, BLUE, "middle", "bold")
        s += text(x + pw / 2, py + ph - 14, notes[i], 11, INK, "middle", "italic")
        cx, cy = x + pw / 2, py + 96
        if i == 0:      # зазор
            s += cap_plates(cx - 14, cy, 28, 60, INK, 3)
            s += arrow(cx + 30, cy, cx + 6, cy, RED, 2)
            s += text(cx + 50, cy + 4, "d↓", 13, RED, "middle", "bold")
        elif i == 1:    # площа (перекриття)
            s += line(cx - 40, cy - 30, cx + 10, cy - 30, INK, 3)
            s += line(cx - 10, cy + 30, cx + 40, cy + 30, INK, 3)
            s += arrow(cx - 6, cy + 48, cx + 30, cy + 48, RED, 2)
            s += text(cx + 12, cy - 44, "зсув → A", 11, RED, "middle", "bold")
        elif i == 2:    # діелектрик
            s += cap_plates(cx, cy, 44, 60, INK, 3)
            s += rect(cx - 18, cy - 28, 36, 56, fill="#cfe3f7", stroke=BLUE, sw=1, rx=2)
            s += text(cx, cy + 4, "ε", 16, BLUE, "middle", "bold")
    save("fig-28-2-4-capacitive.svg", s)


def fig_inductive():
    w, h = 700, 260
    s = header(w, h)
    s += text(w / 2, 26, "Індуктивні давачі: рухоме осердя та вихрові струми",
              15.5, INK, "middle", "bold")
    # ліворуч — рухоме осердя (LVDT)
    s += rect(28, 48, 318, 188, fill="#fbf6ee", stroke=GOLD, sw=1.3, rx=8)
    s += text(187, 70, "рухоме осердя → L", 13, "#9a7a1e", "middle", "bold")
    s += coil_h(95, 150, 160, 6, INK, 2)
    s += line(70, 150, 95, 150, INK, 2)
    s += line(255, 150, 280, 150, INK, 2)
    s += rect(120, 158, 70, 16, fill="#d9c08a", stroke="#9a7a1e", sw=1.4)
    s += arrow(150, 200, 200, 200, "#9a7a1e", 2)
    s += text(165, 220, "осердя рухається", 11, "#9a7a1e", "middle", "italic")
    # праворуч — вихрові струми / метал
    s += rect(360, 48, 312, 188, fill="#eef4fb", stroke=BLUE, sw=1.3, rx=8)
    s += text(516, 70, "метал поряд → вихрові струми", 12, BLUE, "middle", "bold")
    s += coil_h(420, 150, 110, 5, INK, 2)
    s += line(400, 150, 420, 150, INK, 2)
    s += line(530, 150, 545, 150, INK, 2)
    s += rect(575, 110, 60, 80, fill="#cfd6de", stroke=GREY, sw=1.4, rx=3)
    s += text(605, 104, "метал", 10.5, GREY, "middle", "bold")
    for yy in (135, 160):
        s += f'<path d="M 590,{yy} a 12,8 0 1 1 0.1,0" fill="none" stroke="{BLUE}" stroke-width="1.6"/>\n'
    s += arrow(548, 150, 568, 150, BLUE, 1.8)
    s += text(516, 214, "L і добротність змінюються", 11, BLUE, "middle", "italic")
    save("fig-28-2-5-inductive.svg", s)


def fig_dc_ac():
    w, h = 700, 270
    s = header(w, h)
    s += text(w / 2, 26, "R виявляє постійний струм; C і L — лише змінний",
              15.5, INK, "middle", "bold")
    # ліворуч — R / DC
    s += rect(28, 46, 318, 196, fill="#fbf2f1", stroke=RED, sw=1.3, rx=8)
    s += text(187, 68, "резистивний → постійний струм", 12, RED, "middle", "bold")
    s += source(80, 150, 18)
    s += text(80, 124, "DC", 11, INK, "middle", "bold")
    s += line(80, 132, 80, 110, INK, 2)
    s += line(80, 110, 200, 110, INK, 2)
    s += line(200, 110, 200, 130, INK, 2)
    s += res_v(200, 130, 40, GREEN, 2.4)
    s += text(220, 154, "R(вимір.)", 10.5, GREEN, "start", "bold")
    s += line(200, 170, 200, 190, INK, 2)
    s += line(80, 168, 80, 190, INK, 2)
    s += line(80, 190, 200, 190, INK, 2)
    s += line(245, 110, 290, 110, INK, 2)
    s += line(290, 110, 290, 112, INK, 2)
    s += vmeter(290, 130, 18, "V")
    s += text(187, 224, "дільник / міст — і одразу на АЦП", 11, INK, "middle", "italic")
    # праворуч — C, L / AC
    s += rect(360, 46, 312, 196, fill="#eef4fb", stroke=BLUE, sw=1.3, rx=8)
    s += text(516, 68, "ємнісний / індуктивний → змінний", 12, BLUE, "middle", "bold")
    s += ac_source(420, 150, 18, INK)
    s += text(420, 124, "AC", 11, INK, "middle", "bold")
    s += line(438, 150, 480, 150, INK, 2)
    s += cap_plates(495, 150, 18, 36, INK, 3)
    s += coil_h(520, 150, 60, 3, INK, 2)
    s += line(580, 150, 600, 150, INK, 2)
    s += text(516, 196, "Xc = 1/(2πfC)    XL = 2πfL", 11.5, BLUE, "middle", "bold")
    s += text(516, 224, "реактивні — вимір на змінному сигналі", 11, INK, "middle", "italic")
    save("fig-28-2-6-dc-vs-ac.svg", s)


def fig_compare():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Резистивні · ємнісні · індуктивні — стисла мапа вибору",
              15.5, INK, "middle", "bold")
    labels = ["ручка", "контакт", "зчитування", "сильне", "слабке", "де"]
    cols = [
        ("Резистивні", RED, ["ρ або L, A", "зазвичай так", "дільник / міст (DC)",
                              "просто, дешево", "самонагрів, дрейф", "темп., тензо, світло"]),
        ("Ємнісні", BLUE, ["d, A, ε", "ні", "AC / частота",
                           "чутл., безконтакт.", "паразити, волога", "наближення, дотик, рівень"]),
        ("Індуктивні", "#9a7a1e", ["μ, магн. шлях", "ні (метал)", "AC / добротність",
                                    "стійкий до бруду", "лише метал, AC", "метал-наближ., LVDT"]),
    ]
    x0, y0 = 24, 48
    lw, cw, rh = 120, 188, 36
    # шапка
    s += rect(x0, y0, lw, rh, fill="#eef1f6", stroke=GREY, sw=1)
    for j, (name, col, _d) in enumerate(cols):
        s += rect(x0 + lw + j * cw, y0, cw, rh, fill="#eef1f6", stroke=GREY, sw=1)
        s += text(x0 + lw + j * cw + cw / 2, y0 + 23, name, 13, col, "middle", "bold")
    # рядки
    for r, lab in enumerate(labels):
        yy = y0 + rh * (r + 1)
        s += rect(x0, yy, lw, rh, fill="#fafafa", stroke=GREY, sw=0.8)
        s += text(x0 + 10, yy + 23, lab, 11.5, INK, "start", "bold")
        for j, (_n, col, data) in enumerate(cols):
            s += rect(x0 + lw + j * cw, yy, cw, rh, fill="#ffffff", stroke=GREY, sw=0.8)
            s += text(x0 + lw + j * cw + cw / 2, yy + 23, data[r], 11, INK, "middle")
    save("fig-28-2-7-compare.svg", s)


# ── символи для §28.3 (осі, фотон, поле ⊗, експон. спад) ─────────────────────

def axes(x0, y0, w, ht, color=INK):
    return arrow(x0, y0, x0, y0 - ht, color, 1.6) + arrow(x0, y0, x0 + w, y0, color, 1.6)


def xfield(cx, cy, r=8, color=BLUE):
    """Поле «в площину» — кружок із хрестиком (⊗)."""
    d = r * 0.62
    return (circle(cx, cy, r, "none", color, 1.4)
            + line(cx - d, cy - d, cx + d, cy + d, color, 1.2)
            + line(cx - d, cy + d, cx + d, cy - d, color, 1.2))


def decay(x_edge, y0, peak, tau_px, x_end, color, sw=2, sign=-1):
    """Експоненційний сплеск від нульової лінії y0 і спад до неї."""
    pts = [(x_edge, y0)]
    N = 26
    for i in range(N + 1):
        x = x_edge + (x_end - x_edge) * i / N
        y = y0 + sign * peak * math.exp(-(x - x_edge) / tau_px)
        pts.append((x, y))
    return poly(pts, color, sw)


# ════════════════════════════════════════════════════════════════════════════
#  §28.3 П'єзо-, оптичні, напівпровідникові
# ════════════════════════════════════════════════════════════════════════════

def fig_28_3_overview():
    w, h = 712, 250
    s = header(w, h)
    s += text(w / 2, 28, "Три родини глибшої фізики — і часто з власним сигналом",
              15.5, INK, "middle", "bold")
    px = [20, 255, 490]
    pw, py, ph = 200, 50, 174
    data = [
        ("п'єзоелектричні", RED, "механічне напруження", "→ заряд", "самогенерувальні"),
        ("оптичні", GOLD, "світло", "→ струм", "самогенер. (фотовольт.)"),
        ("напівпровідникові", BLUE, "поле / температура", "→ напруга", "часто з АЦП у кристалі"),
    ]
    for i, (name, col, inp, outp, tag) in enumerate(data):
        x = px[i]
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.5, rx=8)
        s += text(x + pw / 2, py + 26, name, 13.5, col, "middle", "bold")
        s += text(x + pw / 2, py + 70, inp, 12, INK, "middle", "bold")
        s += arrow(x + pw / 2, py + 80, x + pw / 2, py + 104, col, 2)
        # маленька іконка
        cy = py + 120
        if i == 0:
            s += rect(x + pw / 2 - 22, cy - 10, 44, 22, fill="#f0e6e6", stroke=col, sw=1.4)
            s += arrow(x + pw / 2 - 40, cy, x + pw / 2 - 24, cy, INK, 1.6)
            s += arrow(x + pw / 2 + 40, cy, x + pw / 2 + 24, cy, INK, 1.6)
            s += text(x + pw / 2 - 14, cy + 5, "+", 13, RED, "middle", "bold")
            s += text(x + pw / 2 + 14, cy + 5, "−", 13, BLUE, "middle", "bold")
        elif i == 1:
            s += rays(x + pw / 2, cy - 2, GOLD, 3)
            s += rect(x + pw / 2 - 6, cy + 4, 12, 14, fill="#fff", stroke=INK, sw=1.4)
        else:
            s += rect(x + pw / 2 - 18, cy - 10, 36, 24, fill="#e6ecf5", stroke=col, sw=1.4, rx=3)
            for k in range(3):
                s += line(x + pw / 2 - 18, cy - 4 + k * 7, x + pw / 2 - 26, cy - 4 + k * 7, INK, 1.2)
                s += line(x + pw / 2 + 18, cy - 4 + k * 7, x + pw / 2 + 26, cy - 4 + k * 7, INK, 1.2)
        s += text(x + pw / 2, py + 158, outp, 12.5, col, "middle", "bold")
        s += text(x + pw / 2, py + ph - 8, tag, 10.5, GREY, "middle", "italic")
    save("fig-28-3-1-overview.svg", s)


def fig_piezo():
    w, h = 690, 300
    s = header(w, h)
    s += text(w / 2, 28, "П'єзоефект: стиск зміщує центри зарядів → напруга на гранях",
              15, INK, "middle", "bold")

    def cell(cx, cy, stressed):
        out = ""
        bw, bh = 120, (96 if stressed else 116)
        out += rect(cx - bw / 2, cy - bh / 2, bw, bh, fill="#f6f6f0", stroke=INK, sw=2, rx=4)
        if not stressed:
            # симетрично: центри + і − збігаються
            out += plus(cx, cy, 10, RED)
            out += circle(cx, cy, 16, "none", BLUE, 1.6)
            out += text(cx, cy + 34, "центри +/− збігаються", 10.5, GREY, "middle", "italic")
            out += text(cx, cy - bh / 2 - 10, "без навантаження", 12, INK, "middle", "bold")
        else:
            # стиск: стрілки, рознесені центри, заряд на гранях
            out += arrow(cx, cy - bh / 2 - 22, cx, cy - bh / 2 - 4, INK, 2.2)
            out += arrow(cx, cy + bh / 2 + 22, cx, cy + bh / 2 + 4, INK, 2.2)
            for k in (-1, 0, 1):
                out += text(cx + k * 26, cy - bh / 2 + 14, "+", 14, RED, "middle", "bold")
                out += text(cx + k * 26, cy + bh / 2 - 6, "−", 14, BLUE, "middle", "bold")
            out += plus(cx, cy - 12, 8, RED)
            out += minus(cx, cy + 12, 8, BLUE)
            out += text(cx, cy - bh / 2 - 32, "стиск", 12, INK, "middle", "bold")
        return out

    s += cell(180, 150, False)
    s += cell(440, 150, True)
    # вольтметр на стиснутій комірці
    s += line(440 - 60, 150 - 48, 560, 150 - 48, INK, 2)
    s += line(440 - 60, 150 + 48, 560, 150 + 48, INK, 2)
    s += line(560, 150 - 48, 560, 150 - 20, INK, 2)
    s += line(560, 150 + 48, 560, 150 + 20, INK, 2)
    s += vmeter(560, 150, 19, "V")
    s += text(560, 232, "є напруга!", 12, GREEN, "middle", "bold")
    s += text(180, 232, "V = 0", 12, GREY, "middle", "bold")
    save("fig-28-3-2-piezo.svg", s)


def fig_piezo_ac():
    w, h = 690, 320
    s = header(w, h)
    s += text(w / 2, 26, "П'єзо «бачить» лише зміни: сталий тиск дає заряд, що стікає",
              15, INK, "middle", "bold")
    x0, xe = 80, 630
    # верхній графік — сила
    yb1 = 120
    s += axes(x0, yb1, xe - x0 + 10, 70, GREY)
    s += text(x0 - 8, yb1 - 64, "сила F", 11.5, INK, "end", "bold")
    s += poly([(x0, yb1), (200, yb1), (200, yb1 - 50), (400, yb1 - 50),
               (400, yb1), (xe, yb1)], RED, 2.4)
    s += text(300, yb1 - 58, "сталий натиск", 11, RED, "middle", "italic")
    # нижній графік — вихід
    yb2 = 270
    s += axes(x0, yb2, xe - x0 + 10, 80, GREY)
    s += text(x0 - 8, yb2 - 74, "вихід V", 11.5, INK, "end", "bold")
    s += line(x0, yb2 - 40, xe, yb2 - 40, FAINT, 1, dash="3,3")  # нульова лінія
    base = yb2 - 40
    s += line(x0, base, 200, base, GREEN, 2.4)
    s += decay(200, base, 46, 38, 400, GREEN, 2.4, sign=-1)      # сплеск вгору
    s += line(398, base, 400, base, GREEN, 2.4)
    s += decay(400, base, 46, 38, xe, GREEN, 2.4, sign=+1)       # сплеск вниз
    s += text(214, base - 52, "фронт ↑", 10.5, GREEN, "middle", "bold")
    s += text(420, base + 52, "фронт ↓", 10.5, GREEN, "middle", "bold")
    s += text(300, base + 30, "між фронтами — спад до нуля (τ = RC)", 11, INK, "middle", "italic")
    save("fig-28-3-3-piezo-ac.svg", s)


def fig_photodiode():
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 26, "Фотодіод: фотон народжує пару, поле переходу дає фотострум",
              15, INK, "middle", "bold")
    # перехід зліва
    s += rect(40, 70, 90, 120, fill="#f3d9d9", stroke=RED, sw=1.4)
    s += rect(130, 70, 90, 120, fill="#d9e0f3", stroke=BLUE, sw=1.4)
    s += text(85, 60, "p", 13, RED, "middle", "bold")
    s += text(175, 60, "n", 13, BLUE, "middle", "bold")
    s += rect(118, 70, 24, 120, fill="#eee9c8", stroke=GOLD, sw=1.2)
    s += text(130, 205, "збіднена область", 10, "#9a7a1e", "middle", "italic")
    # фотон
    s += arrow(60, 40, 120, 122, GOLD, 2)
    s += text(58, 36, "фотон hν", 11, "#9a7a1e", "start", "bold")
    # пара
    s += plus(150, 130, 7, RED)
    s += electron(118, 110)
    s += arrow(146, 130, 138, 130, RED, 1.4)
    s += arrow(122, 110, 130, 110, BLUE, 1.4)
    # зовнішнє коло — фотострум
    s += line(40, 130, 20, 130, INK, 2)
    s += line(20, 130, 20, 250, INK, 2)
    s += line(220, 130, 250, 130, INK, 2)
    s += line(250, 130, 250, 250, INK, 2)
    s += line(20, 250, 250, 250, INK, 2)
    s += circle(135, 250, 16, "#fff", INK, 1.6)
    s += text(135, 255, "A", 12, GREEN, "middle", "bold")
    s += arrow(95, 250, 80, 250, GREEN, 2)
    s += text(135, 285, "фотострум ∝ освітленість", 11, GREEN, "middle", "bold")

    # застосування праворуч (3 іконки)
    s += line(300, 60, 300, 300, FAINT, 1)
    apps = [("оптичний енкодер", 80), ("оптопара (розв'язка)", 160), ("відбивний давач", 240)]
    for (lbl, yy) in apps:
        s += text(330, yy - 26, lbl, 11.5, INK, "start", "bold")
    # енкодер
    s += circle(360, 80, 4, INK);
    s += rect(330, 70, 70, 18, fill="none", stroke=GREY, sw=1)
    for dx in range(0, 70, 12):
        s += rect(330 + dx, 70, 6, 18, fill=INK, stroke="none")
    s += text(490, 84, "щілини рахують кут", 10.5, GREY, "start", "italic")
    # оптопара
    s += text(330, 164, "LED", 10, GOLD, "start", "bold")
    s += arrow(360, 160, 400, 160, GOLD, 2)
    s += rect(404, 150, 16, 20, fill="#d9e0f3", stroke=BLUE, sw=1.2)
    s += text(490, 164, "світло крізь ізоляцію", 10.5, GREY, "start", "italic")
    # відбивний
    s += arrow(345, 250, 380, 234, GOLD, 1.8)
    s += line(395, 226, 430, 226, INK, 3)
    s += text(440, 224, "перешкода", 10, INK, "start")
    s += arrow(380, 238, 350, 256, GOLD, 1.8)
    s += text(490, 250, "ловить відбиток", 10.5, GREY, "start", "italic")
    save("fig-28-3-4-photodiode.svg", s)


def fig_hall():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "Ефект Холла: поле відхиляє носії вбік → поперечна напруга",
              15, INK, "middle", "bold")
    px, py, pw, ph = 180, 95, 280, 110
    midY = py + ph / 2
    s += rect(px, py, pw, ph, fill="#eef2f6", stroke=INK, sw=2, rx=4)
    # струм горизонтально (ліворуч → праворуч)
    s += arrow(116, midY, px - 4, midY, INK, 2.4)
    s += text(126, midY - 10, "струм I", 12, INK, "middle", "bold")
    s += arrow(px + pw + 4, midY, px + pw + 38, midY, INK, 2.4)
    # поле B у площину (фон)
    for ix in range(5):
        for iy in range(2):
            s += xfield(px + 36 + ix * 52, py + 34 + iy * 44, 7, BLUE)
    s += text(px + pw / 2, py + ph + 24, "поле B — у площину рисунка (⊗)", 11, BLUE, "middle", "bold")
    # носії (електрони) відхиляються вгору й накопичуються на верхній грані
    for ix in range(5):
        s += electron(px + 34 + ix * 52, py + 13)
    s += arrow(px + pw / 2, midY + 6, px + pw / 2, py + 24, GREEN, 2)
    s += text(px + pw / 2 + 64, midY + 2, "сила на носії", 10.5, GREEN, "middle", "italic")
    # заряд на гранях: верх − (зібрались електрони), низ +
    s += text(px + pw / 2, py - 8, "−  −  −  −  −", 14, BLUE, "middle", "bold")
    s += text(px + pw / 2, py + ph + 6, "+  +  +  +  +", 14, RED, "middle", "bold")
    # вольтметр Холла праворуч (відведення від верхньої та нижньої граней)
    mx = px + pw + 70
    s += line(px + pw, py + 6, mx, py + 6, INK, 1.6)
    s += line(mx, py + 6, mx, midY - 17, INK, 1.6)
    s += line(px + pw, py + ph - 6, mx, py + ph - 6, INK, 1.6)
    s += line(mx, py + ph - 6, mx, midY + 17, INK, 1.6)
    s += vmeter(mx, midY, 17, "V")
    s += text(mx, midY + 36, "V_H", 12, GREEN, "middle", "bold")
    s += text(w / 2, 288, "V_H ∝ B   (за сталого струму)", 12.5, GREEN, "middle", "bold")
    save("fig-28-3-5-hall.svg", s)


def fig_semic_temp():
    w, h = 710, 300
    s = header(w, h)
    s += text(w / 2, 26, "Напівпровідниковий давач температури: лінійний і «розумний»",
              15, INK, "middle", "bold")
    # графік Vf(T) ліворуч
    x0, yb = 70, 230
    s += axes(x0, yb, 250, 150, INK)
    s += text(x0 + 130, yb + 24, "температура →", 11, INK, "middle")
    s += text(x0 - 40, yb - 150, "V переходу", 11, INK, "start", "bold")
    s += poly([(x0 + 10, yb - 130), (x0 + 230, yb - 30)], RED, 2.6)   # майже пряма ↓
    s += text(x0 + 150, yb - 95, "≈ −2 мВ/°C", 11, RED, "middle", "bold")
    # для контрасту — крива NTC
    s += poly([(x0 + 10, yb - 20), (x0 + 60, yb - 70), (x0 + 130, yb - 105),
               (x0 + 230, yb - 122)], GREY, 1.8, dash="4,3")
    s += text(x0 + 150, yb - 128, "NTC (нелінійний)", 9.5, GREY, "middle", "italic")

    # «розумний» давач праворуч
    cx = 470
    s += rect(cx, 70, 218, 150, fill="#eef4fb", stroke=BLUE, sw=1.6, rx=10)
    s += text(cx + 109, 90, "один кристал", 11.5, BLUE, "middle", "bold")
    boxes = [("чутл.\nелемент", GREEN), ("підсил.", INK), ("АЦП", RED)]
    bx = cx + 16
    for i, (lbl, col) in enumerate(boxes):
        b = bx + i * 64
        s += rect(b, 120, 52, 44, fill="#fff", stroke=col, sw=1.4, rx=5)
        first, second = (lbl.split("\n") + [""])[:2]
        s += text(b + 26, 140, first, 10, col, "middle", "bold")
        s += text(b + 26, 154, second, 10, col, "middle", "bold")
        if i:
            s += arrow(b - 12, 142, b - 2, 142, INK, 1.6)
    s += arrow(bx + 3 * 64 - 12, 142, bx + 3 * 64 + 2, 142, INK, 1.6)
    s += text(cx + 205, 146, "цифра", 11, BLUE, "start", "bold")
    s += text(cx + 109, 198, "вимір переїхав у мікросхему", 10.5, GREY, "middle", "italic")
    save("fig-28-3-6-semiconductor-temp.svg", s)


def fig_28_3_compare():
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "П'єзо · оптичні · напівпровідникові — мапа вибору",
              15.5, INK, "middle", "bold")
    labels = ["величина", "самогенер.?", "сигнал", "зчитування", "де"]
    cols = [
        ("П'єзо", RED, ["динам. сила, звук", "так", "заряд (тільки зміни)",
                        "зарядовий підсил.", "удар, вібрація, УЗ"]),
        ("Оптичні", GOLD, ["світло", "так (фотовольт.)", "струм",
                           "перетв. струм→напр.", "енкодер, оптопара"]),
        ("Напівпровід.", BLUE, ["поле, темп.", "ні (живлення)", "напруга / цифра",
                                "часто вже в чипі", "Холл, IC-термо"]),
    ]
    x0, y0 = 24, 48
    lw, cw, rh = 122, 188, 38
    s += rect(x0, y0, lw, rh, fill="#eef1f6", stroke=GREY, sw=1)
    for j, (name, col, _d) in enumerate(cols):
        s += rect(x0 + lw + j * cw, y0, cw, rh, fill="#eef1f6", stroke=GREY, sw=1)
        s += text(x0 + lw + j * cw + cw / 2, y0 + 24, name, 13, col, "middle", "bold")
    for r, lab in enumerate(labels):
        yy = y0 + rh * (r + 1)
        s += rect(x0, yy, lw, rh, fill="#fafafa", stroke=GREY, sw=0.8)
        s += text(x0 + 10, yy + 24, lab, 11.5, INK, "start", "bold")
        for j, (_n, col, data) in enumerate(cols):
            s += rect(x0 + lw + j * cw, yy, cw, rh, fill="#ffffff", stroke=GREY, sw=0.8)
            s += text(x0 + lw + j * cw + cw / 2, yy + 24, data[r], 10.5, INK, "middle")
    save("fig-28-3-7-compare.svg", s)


# ── помічники для §28.4 (графіки характеристик) ──────────────────────────────

def _pt(x0, y0, w, ht, xv, uv):
    return (x0 + xv * w, y0 - uv * ht)


def _plot_path(x0, y0, w, ht, pts_norm, color, sw=2.4, dash=None):
    return poly([_pt(x0, y0, w, ht, xv, uv) for (xv, uv) in pts_norm], color, sw, dash=dash)


def _target(cx, cy, r, dots, dotcol=RED):
    s = circle(cx, cy, r, "#fff", INK, 1.4)
    s += circle(cx, cy, r * 0.62, "none", GREY, 1.1)
    s += circle(cx, cy, r * 0.26, "#f3dada", RED, 1.1)
    for (dx, dy) in dots:
        s += dot(cx + dx, cy + dy, 2.6, dotcol)
    return s


# ════════════════════════════════════════════════════════════════════════════
#  §28.4 Характеристики: чутливість, лінійність, діапазон
# ════════════════════════════════════════════════════════════════════════════

def fig_transfer():
    w, h = 620, 330
    s = header(w, h)
    s += text(w / 2, 26, "Передавальна характеристика: вихід як функція величини",
              15, INK, "middle", "bold")
    x0, y0, pw, ph = 96, 280, 450, 218
    s += axes(x0, y0, pw + 14, ph + 14)
    s += text(x0 - 8, y0 - ph - 6, "вихід U", 12, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "величина x", 12, INK, "middle", "bold")
    # ідеальна пряма U = U0 + S x
    s += _plot_path(x0, y0, pw, ph, [(0, 0.16), (1.0, 0.92)], GREEN, 2.8)
    # зсув нуля
    p0 = _pt(x0, y0, pw, ph, 0, 0.16)
    s += line(x0 - 6, p0[1], x0 + 6, p0[1], RED, 2)
    s += text(x0 - 10, p0[1] + 4, "U₀", 12.5, RED, "end", "bold")
    s += text(x0 + 70, p0[1] - 6, "зсув нуля (offset)", 11, RED, "start", "italic")
    # трикутник нахилу
    a = _pt(x0, y0, pw, ph, 0.45, 0.52)
    b = _pt(x0, y0, pw, ph, 0.75, 0.52)
    c = _pt(x0, y0, pw, ph, 0.75, 0.70)
    s += line(a[0], a[1], b[0], b[1], INK, 1.6, dash="3,3")
    s += line(b[0], b[1], c[0], c[1], INK, 1.6, dash="3,3")
    s += text((a[0] + b[0]) / 2, a[1] + 16, "Δx", 11, INK, "middle", "bold")
    s += text(c[0] + 8, (b[1] + c[1]) / 2, "ΔU", 11, INK, "start", "bold")
    s += text(x0 + 250, y0 - ph + 8, "S = ΔU/Δx  (чутливість)", 12, GREEN, "start", "bold")
    s += text(w / 2, 318, "ідеальний давач: пряма U = U₀ + S·x", 11.5, INK, "middle", "italic")
    save("fig-28-4-1-transfer.svg", s)


def fig_sensitivity():
    w, h = 620, 320
    s = header(w, h)
    s += text(w / 2, 26, "Чутливість — це нахил: крута крива дає більший сигнал",
              15, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 270, 460, 210
    s += axes(x0, y0, pw + 14, ph + 14)
    s += text(x0 - 8, y0 - ph - 6, "U", 12, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "x", 12, INK, "middle", "bold")
    s += _plot_path(x0, y0, pw, ph, [(0, 0.08), (1.0, 0.95)], GREEN, 2.8)
    s += _plot_path(x0, y0, pw, ph, [(0, 0.08), (1.0, 0.46)], BLUE, 2.8)
    s += text(*(_pt(x0, y0, pw, ph, 0.82, 0.86)), "велика S", 12, GREEN, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.82, 0.42)), "мала S", 12, BLUE, "start", "bold")
    # одна Δx, дві ΔU
    xv = 0.55
    lo = _pt(x0, y0, pw, ph, xv, 0.0)
    s += line(lo[0], y0, lo[0], _pt(x0, y0, pw, ph, xv, 0.86)[1], GREY, 1, dash="3,3")
    s += text(lo[0], y0 + 18, "та сама Δx", 11, INK, "middle", "italic")
    s += text(w / 2, 308, "більша S → легше прочитати, але швидше насичує вихід", 11.5, INK, "middle", "italic")
    save("fig-28-4-2-sensitivity.svg", s)


def fig_range():
    w, h = 640, 320
    s = header(w, h)
    s += text(w / 2, 26, "Діапазон — робоче вікно; поза ним мертва зона й насичення",
              14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 262, 500, 200
    s += axes(x0, y0, pw + 14, ph + 14)
    s += text(x0 - 8, y0 - ph - 6, "U", 12, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "x", 12, INK, "middle", "bold")
    # мертва зона (плато низько) → лінійно → насичення (плато високо)
    s += _plot_path(x0, y0, pw, ph, [(0, 0.06), (0.12, 0.06), (0.78, 0.86),
                                     (1.0, 0.9)], GREEN, 2.8)
    # позначка мертвої зони (над плато на старті)
    dz = _pt(x0, y0, pw, ph, 0.04, 0.06)
    s += text(dz[0], dz[1] - 8, "мертва зона", 9, BLUE, "start", "italic")
    # робочий діапазон бракет
    xa = _pt(x0, y0, pw, ph, 0.12, 0)[0]
    xb = _pt(x0, y0, pw, ph, 0.78, 0)[0]
    s += line(xa, y0 + 30, xb, y0 + 30, GREEN, 2)
    s += line(xa, y0 + 26, xa, y0 + 34, GREEN, 2)
    s += line(xb, y0 + 26, xb, y0 + 34, GREEN, 2)
    s += text((xa + xb) / 2, y0 + 46, "робочий діапазон (повна шкала FS)", 11.5, GREEN, "middle", "bold")
    # насичення
    sat = _pt(x0, y0, pw, ph, 0.88, 0.9)
    s += text(sat[0] + 6, sat[1] - 8, "насичення", 11, RED, "start", "bold")
    s += text(sat[0] + 6, sat[1] + 8, "(вихід уперся в стелю)", 10, RED, "start", "italic")
    save("fig-28-4-3-range.svg", s)


def fig_linearity():
    w, h = 620, 320
    s = header(w, h)
    s += text(w / 2, 26, "Лінійність: відхилення реальної кривої від опорної прямої",
              14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 268, 460, 206
    s += axes(x0, y0, pw + 14, ph + 14)
    s += text(x0 - 8, y0 - ph - 6, "U", 12, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "x", 12, INK, "middle", "bold")
    # опорна пряма (через кінці)
    s += _plot_path(x0, y0, pw, ph, [(0, 0.1), (1.0, 0.9)], GREY, 2, dash="6,4")
    s += text(*(_pt(x0, y0, pw, ph, 0.7, 0.78)), "опорна пряма", 11, GREY, "start", "italic")
    # реальна вигнута крива (бовтається під прямою)
    real = [(0, 0.1), (0.2, 0.33), (0.4, 0.5), (0.5, 0.56), (0.6, 0.61),
            (0.8, 0.74), (1.0, 0.9)]
    s += _plot_path(x0, y0, pw, ph, real, GREEN, 2.8)
    s += text(*(_pt(x0, y0, pw, ph, 0.28, 0.46)), "реальна крива", 11, GREEN, "start", "bold")
    # макс. відхилення на x=0.5: пряма дає 0.5, крива 0.56 → стрілка
    xv = 0.5
    pl = _pt(x0, y0, pw, ph, xv, 0.5)
    pc = _pt(x0, y0, pw, ph, xv, 0.56)
    s += line(pl[0], pl[1], pc[0], pc[1], RED, 2)
    s += line(pl[0] - 4, pl[1], pl[0] + 4, pl[1], RED, 2)
    s += text(pc[0] + 8, (pl[1] + pc[1]) / 2 - 16, "нелінійність", 11, RED, "start", "bold")
    s += text(pc[0] + 8, (pl[1] + pc[1]) / 2 - 2, "(макс., % FS)", 10, RED, "start", "italic")
    save("fig-28-4-4-linearity.svg", s)


def fig_accuracy_precision():
    w, h = 560, 360
    s = header(w, h)
    s += text(w / 2, 26, "Точність ≠ прецизійність: чотири випадки на мішені",
              15, INK, "middle", "bold")
    cells = [
        (150, 110, "точно + прецизійно", [(-3, -2), (2, -3), (-1, 3), (3, 2), (0, 0)], (0, 0)),
        (410, 110, "прецизійно, не точно", [(-3, -2), (2, -3), (-1, 3), (3, 2), (0, 0)], (15, -13)),
        (150, 270, "точно, не прецизійно", [(-15, -11), (13, -14), (-16, 10), (16, 12), (1, -2)], (0, 0)),
        (410, 270, "ні те, ні те", [(-15, -11), (13, -14), (-16, 10), (16, 12), (1, -2)], (15, -13)),
    ]
    for (cx, cy, lbl, dots, bias) in cells:
        biased = [(dx + bias[0], dy + bias[1]) for (dx, dy) in dots]
        s += _target(cx, cy, 46, biased)
        s += text(cx, cy + 70, lbl, 12, INK, "middle", "bold")
    s += text(w / 2, 348, "тіснота купки = прецизійність · де купка = точність", 11.5, GREY, "middle", "italic")
    save("fig-28-4-5-accuracy-precision.svg", s)


def fig_resolution():
    w, h = 620, 300
    s = header(w, h)
    s += text(w / 2, 26, "Роздільність: гладку величину вихід бачить сходинками",
              15, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 480, 190
    s += axes(x0, y0, pw + 14, ph + 14)
    s += text(x0 - 8, y0 - ph - 6, "U", 12, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "час →", 11.5, INK, "middle", "bold")
    # справжня гладка лінія
    s += _plot_path(x0, y0, pw, ph, [(0, 0.08), (1.0, 0.9)], GREY, 1.8, dash="5,4")
    s += text(*(_pt(x0, y0, pw, ph, 0.66, 0.78)), "справжня величина", 10.5, GREY, "start", "italic")
    # сходинки
    steps = 8
    pts = []
    for i in range(steps + 1):
        xv = i / steps
        uv = 0.08 + round((0.82 * xv) / 0.1025) * 0.1025
        if i > 0:
            pts.append((xv, prev_u))
        pts.append((xv, uv))
        prev_u = uv
    s += _plot_path(x0, y0, pw, ph, pts, GREEN, 2.6)
    # позначка одного кроку
    a = _pt(x0, y0, pw, ph, 0.5, 0.08 + 4 * 0.1025)
    b = _pt(x0, y0, pw, ph, 0.5, 0.08 + 5 * 0.1025)
    s += line(a[0] + 30, a[1], a[0] + 30, b[1], RED, 2)
    s += line(a[0] + 26, a[1], a[0] + 34, a[1], RED, 2)
    s += line(a[0] + 26, b[1], a[0] + 34, b[1], RED, 2)
    s += text(a[0] + 40, (a[1] + b[1]) / 2 + 4, "крок = роздільність", 11, RED, "start", "bold")
    save("fig-28-4-6-resolution.svg", s)


def fig_datasheet():
    w, h = 640, 350
    s = header(w, h)
    s += text(w / 2, 26, "Як читати даташит: усі числа — на одній кривій",
              15, INK, "middle", "bold")
    x0, y0, pw, ph = 96, 286, 440, 226
    s += axes(x0, y0, pw + 14, ph + 14)
    s += text(x0 - 8, y0 - ph - 6, "вихід U", 12, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "величина x", 12, INK, "middle", "bold")
    # смуга нелінійності навколо прямої
    s += _plot_path(x0, y0, pw, ph, [(0.1, 0.18), (0.85, 0.82)], FAINT, 9)
    s += _plot_path(x0, y0, pw, ph, [(0.1, 0.18), (0.85, 0.82)], GREEN, 2.8)
    # зсув нуля
    p0 = _pt(x0, y0, pw, ph, 0.1, 0.18)
    s += dot(p0[0], p0[1], 4, RED)
    s += text(p0[0] - 6, p0[1] + 4, "U₀", 12, RED, "end", "bold")
    # нахил
    s += text(*(_pt(x0, y0, pw, ph, 0.3, 0.55)), "нахил = S", 11.5, GREEN, "start", "bold")
    # смуга нелінійності
    s += text(*(_pt(x0, y0, pw, ph, 0.6, 0.46)), "смуга нелінійності", 10.5, "#9a7a1e", "start", "italic")
    # діапазон бракет
    xa = _pt(x0, y0, pw, ph, 0.1, 0)[0]
    xb = _pt(x0, y0, pw, ph, 0.85, 0)[0]
    s += line(xa, y0 + 30, xb, y0 + 30, INK, 1.8)
    s += line(xa, y0 + 26, xa, y0 + 34, INK, 1.8)
    s += line(xb, y0 + 26, xb, y0 + 34, INK, 1.8)
    s += text((xa + xb) / 2, y0 + 46, "діапазон / повна шкала", 11.5, INK, "middle", "bold")
    # крок роздільності (інсет)
    rb = _pt(x0, y0, pw, ph, 0.85, 0.82)
    s += line(rb[0] + 8, rb[1], rb[0] + 8, rb[1] - 14, BLUE, 2)
    s += line(rb[0] + 4, rb[1], rb[0] + 12, rb[1], BLUE, 2)
    s += line(rb[0] + 4, rb[1] - 14, rb[0] + 12, rb[1] - 14, BLUE, 2)
    s += text(rb[0] + 16, rb[1] - 4, "крок", 10, BLUE, "start", "bold")
    save("fig-28-4-7-datasheet.svg", s)


# ── помічники для §28.5 (детермінований «шумовий» слід) ──────────────────────

def _noise(t, phase=0.0):
    """Детермінований шумоподібний сигнал у [-1..1] (сума несумірних синусів)."""
    return (math.sin(0.7 * t + phase) + math.sin(1.7 * t + 1.3)
            + math.sin(2.9 * t + 2.1) + math.sin(5.3 * t + 0.7)) / 4.0


# ════════════════════════════════════════════════════════════════════════════
#  §28.5 Дрейф, гістерезис, шум
# ════════════════════════════════════════════════════════════════════════════

def fig_28_5_overview():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Три біди передавальної кривої: дрейф, гістерезис, шум",
              15, INK, "middle", "bold")
    px = [22, 262, 502]
    pw, py, ph = 196, 52, 150
    for i, name in enumerate(["дрейф", "гістерезис", "шум"]):
        x = px[i]
        col = [RED, "#9a4ea8", BLUE][i]
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.5, rx=8)
        s += text(x + pw / 2, py + 22, name, 13, col, "middle", "bold")
        ox, oy, gw, gh = x + 26, py + ph - 18, pw - 50, ph - 56
        s += axes(ox, oy, gw + 6, gh + 6, GREY)
        if i == 0:      # дрейф — зсунута крива
            s += _plot_path(ox, oy, gw, gh, [(0, 0.12), (1, 0.7)], GREY, 1.8, dash="5,3")
            s += _plot_path(ox, oy, gw, gh, [(0, 0.32), (1, 0.9)], RED, 2.4)
            s += arrow(ox + gw * 0.5, oy - gh * 0.42, ox + gw * 0.5, oy - gh * 0.62, RED, 1.8)
        elif i == 1:    # гістерезис — петля
            s += _plot_path(ox, oy, gw, gh, [(0.08, 0.12), (0.4, 0.3), (0.7, 0.58), (0.92, 0.86)], "#9a4ea8", 2.2)
            s += _plot_path(ox, oy, gw, gh, [(0.92, 0.86), (0.7, 0.7), (0.4, 0.46), (0.08, 0.12)], "#9a4ea8", 2.2)
        else:           # шум — розмита смуга
            base = [(j / 30, 0.15 + 0.6 * (j / 30)) for j in range(31)]
            noisy = [(xv, uv + 0.07 * _noise(j)) for j, (xv, uv) in enumerate(base)]
            s += _plot_path(ox, oy, gw, gh, base, GREY, 1.6, dash="4,3")
            s += _plot_path(ox, oy, gw, gh, noisy, BLUE, 1.6)
    save("fig-28-5-1-overview.svg", s)


def fig_drift():
    w, h = 660, 300
    s = header(w, h)
    s += text(w / 2, 26, "Дрейф нуля зсуває криву паралельно, дрейф нахилу її повертає",
              14, INK, "middle", "bold")
    for k, (title, x0) in enumerate([("дрейф нуля (offset)", 60), ("дрейф нахилу (span)", 380)]):
        y0, pw, ph = 250, 230, 180
        s += axes(x0, y0, pw + 10, ph + 10)
        s += text(x0 + pw / 2, y0 + 30, title, 12.5, INK, "middle", "bold")
        s += text(x0 - 6, y0 - ph - 4, "U", 11, INK, "end", "bold")
        s += text(x0 + pw + 6, y0 + 16, "x", 11, INK, "middle", "bold")
        s += _plot_path(x0, y0, pw, ph, [(0, 0.12), (1, 0.78)], GREY, 1.8, dash="5,3")
        if k == 0:      # паралельний зсув
            s += _plot_path(x0, y0, pw, ph, [(0, 0.34), (1, 1.0)], RED, 2.6)
            s += arrow(x0 + pw * 0.3, y0 - ph * 0.34, x0 + pw * 0.3, y0 - ph * 0.5, RED, 1.8)
        else:           # поворот навколо нуля
            s += _plot_path(x0, y0, pw, ph, [(0, 0.12), (1, 1.0)], RED, 2.6)
            s += arrow(x0 + pw * 0.82, y0 - ph * 0.66, x0 + pw * 0.82, y0 - ph * 0.82, RED, 1.8)
        s += text(x0 + pw * 0.5, y0 - ph - 2, "було → стало", 10.5, RED, "middle", "italic")
    save("fig-28-5-2-drift.svg", s)


def fig_tempco():
    w, h = 620, 290
    s = header(w, h)
    s += text(w / 2, 26, "Температурний коефіцієнт: величина стала, а показ повзе",
              14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 240, 460, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "показ U", 11.5, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "температура →", 11.5, INK, "middle", "bold")
    # ідеал: горизонталь (показ не має залежати від T)
    s += _plot_path(x0, y0, pw, ph, [(0, 0.5), (1, 0.5)], GREY, 1.8, dash="6,4")
    s += text(*(_pt(x0, y0, pw, ph, 0.05, 0.55)), "ідеал: не залежить від T", 10.5, GREY, "start", "italic")
    # реальність: паразитний нахил
    s += _plot_path(x0, y0, pw, ph, [(0, 0.3), (1, 0.82)], RED, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.72)), "нахил = TC (ppm/°C)", 11.5, RED, "start", "bold")
    s += text(w / 2, 280, "величина не змінюється — змінюється лише температура довкілля",
              11, INK, "middle", "italic")
    save("fig-28-5-3-tempco.svg", s)


def fig_hysteresis():
    w, h = 600, 300
    s = header(w, h)
    s += text(w / 2, 26, "Петля гістерезису: шлях «вгору» й «униз» не збігаються",
              14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 250, 420, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "вихід", 11.5, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "величина x", 11.5, INK, "middle", "bold")
    up = [(0.08, 0.1), (0.35, 0.26), (0.6, 0.46), (0.8, 0.66), (0.92, 0.88)]
    dn = [(0.92, 0.88), (0.78, 0.74), (0.55, 0.58), (0.3, 0.4), (0.08, 0.1)]
    s += _plot_path(x0, y0, pw, ph, up, GREEN, 2.6)
    s += _plot_path(x0, y0, pw, ph, dn, RED, 2.6)
    # стрілки напрямку
    a = _pt(x0, y0, pw, ph, 0.47, 0.36)
    s += text(a[0] + 4, a[1] + 14, "▲ зростання", 10.5, GREEN, "start", "bold")
    b = _pt(x0, y0, pw, ph, 0.5, 0.56)
    s += text(b[0] - 4, b[1] - 8, "▼ спадання", 10.5, RED, "end", "bold")
    # макс. гістерезис при x=0.5
    pl = _pt(x0, y0, pw, ph, 0.5, 0.37)
    ph2 = _pt(x0, y0, pw, ph, 0.5, 0.54)
    s += line(pl[0], pl[1], ph2[0], ph2[1], INK, 2)
    s += line(pl[0] - 4, pl[1], pl[0] + 4, pl[1], INK, 2)
    s += line(ph2[0] - 4, ph2[1], ph2[0] + 4, ph2[1], INK, 2)
    s += text(ph2[0] + 8, (pl[1] + ph2[1]) / 2, "гістерезис (% FS)", 10.5, INK, "start", "bold")
    save("fig-28-5-4-hysteresis.svg", s)


def fig_noise():
    w, h = 660, 300
    s = header(w, h)
    s += text(w / 2, 24, "Шум на сигналі: розмах, СКЗ і поріг — плюс спектр (інсет)",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 230, 400, 170
    s += axes(x0, y0, pw + 10, ph + 10)
    s += text(x0 - 8, y0 - ph - 4, "U", 11.5, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    # чистий сигнал (полога синусоїда) + зашумлений
    clean = [(j / 60, 0.5 + 0.22 * math.sin(2 * math.pi * 1.5 * j / 60)) for j in range(61)]
    noisy = [(xv, uv + 0.09 * _noise(j * 1.7)) for j, (xv, uv) in enumerate(clean)]
    s += _plot_path(x0, y0, pw, ph, clean, GREY, 1.8, dash="5,3")
    s += _plot_path(x0, y0, pw, ph, noisy, BLUE, 1.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.86)), "сигнал + шум", 10.5, BLUE, "start", "bold")
    # розмах pp
    pt_hi = _pt(x0, y0, pw, ph, 0.92, 0.62)
    pt_lo = _pt(x0, y0, pw, ph, 0.92, 0.38)
    s += line(pt_hi[0], pt_hi[1], pt_lo[0], pt_lo[1], RED, 1.8)
    s += text(pt_hi[0] + 6, (pt_hi[1] + pt_lo[1]) / 2, "розмах", 10, RED, "start", "bold")
    s += text(pt_hi[0] + 6, (pt_hi[1] + pt_lo[1]) / 2 + 13, "(pp ≈ 6.6·СКЗ)", 9, RED, "start", "italic")
    # спектр-інсет
    ix, iy, iw, ih = 500, 150, 130, 90
    s += rect(ix - 10, iy - 96, iw + 24, ih + 30, fill="#fbfbfb", stroke=FAINT, sw=1, rx=5)
    s += text(ix + iw / 2, iy - 84, "спектр", 10.5, INK, "middle", "bold")
    s += axes(ix, iy, iw, ih, GREY)
    s += text(ix + iw / 2, iy + 16, "частота", 9, GREY, "middle")
    # білий (рівний) + 1/f (підйом ліворуч)
    s += _plot_path(ix, iy, iw, ih, [(0, 0.35), (1, 0.35)], BLUE, 2)
    s += _plot_path(ix, iy, iw, ih, [(0.02, 0.92), (0.1, 0.6), (0.3, 0.42), (1, 0.36)], RED, 2)
    s += text(ix + iw * 0.6, iy - ih * 0.5, "білий", 9, BLUE, "start", "bold")
    s += text(ix + 2, iy - ih * 0.92, "1/f", 9, RED, "start", "bold")
    save("fig-28-5-5-noise.svg", s)


def fig_averaging():
    w, h = 620, 300
    s = header(w, h)
    s += text(w / 2, 26, "Усереднення гасить шум як 1/√N — але зсув не чіпає",
              14.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 240, 470, 180
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "похибка", 11, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "N (усереднено)", 11, INK, "middle", "bold")
    # крива шуму 1/sqrt(N)
    pts = [(i / 64, 0.9 / math.sqrt(1 + i)) for i in range(0, 65)]
    s += _plot_path(x0, y0, pw, ph, pts, BLUE, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.25, 0.5)), "шум ∝ 1/√N", 12, BLUE, "start", "bold")
    # пласка лінія зсуву
    s += _plot_path(x0, y0, pw, ph, [(0, 0.4), (1, 0.4)], RED, 2.4, dash="6,4")
    s += text(*(_pt(x0, y0, pw, ph, 0.5, 0.46)), "дрейф / зсув — не міняється", 11, RED, "start", "bold")
    # позначки N=1,4,16
    for nrm, lbl in [(0 / 64, "N=1"), (3 / 64, "4"), (15 / 64, "16")]:
        pp = _pt(x0, y0, pw, ph, nrm, 0.9 / math.sqrt(1 + nrm * 64))
        s += dot(pp[0], pp[1], 3, INK)
        s += text(pp[0], pp[1] - 8, lbl, 9.5, INK, "middle", "bold")
    save("fig-28-5-6-averaging.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §28.6 Калібрування: від сирого сигналу до величини
# ════════════════════════════════════════════════════════════════════════════

def fig_inverse():
    w, h = 660, 230
    s = header(w, h)
    s += text(w / 2, 28, "Калібрування будує зворотний шлях від сигналу до величини",
              14.5, INK, "middle", "bold")
    boxes = [("величина x", "#eef6ef", GREEN), ("сирий відлік", "#fff7e6", GOLD),
             ("величина в одиницях", "#eef4fb", BLUE)]
    bw, bh, y = 150, 64, 96
    xs = [40, 255, 470]
    for (lbl, fill, col), x in zip(boxes, xs):
        s += rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8)
        s += text(x + bw / 2, y + bh / 2 + 5, lbl, 12.5, col, "middle", "bold")
    s += arrow(xs[0] + bw + 4, y + bh / 2, xs[1] - 4, y + bh / 2, GREEN, 2.4)
    s += text((xs[0] + bw + xs[1]) / 2, y - 8, "давач (прямий)", 11.5, GREEN, "middle", "bold")
    s += arrow(xs[1] + bw + 4, y + bh / 2, xs[2] - 4, y + bh / 2, BLUE, 2.4)
    s += text((xs[1] + bw + xs[2]) / 2, y - 8, "калібрування", 11.5, BLUE, "middle", "bold")
    s += text((xs[1] + bw + xs[2]) / 2, y + bh + 18, "(обернений)", 10.5, BLUE, "middle", "italic")
    s += text(w / 2, 210, "сире «615» → осмислені «50.0 °C»", 12, INK, "middle", "italic")
    save("fig-28-6-1-inverse.svg", s)


def fig_two_point():
    w, h = 600, 320
    s = header(w, h)
    s += text(w / 2, 26, "Двоточкове калібрування: дві відомі точки задають пряму",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 96, 256, 430, 196
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "сирий відлік", 11, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "відома величина", 11, INK, "middle", "bold")
    # пряма через дві точки
    s += _plot_path(x0, y0, pw, ph, [(0.0, 0.16), (1.0, 0.92)], GREEN, 2.6)
    p1 = _pt(x0, y0, pw, ph, 0.05, 0.2)
    p2 = _pt(x0, y0, pw, ph, 0.92, 0.86)
    for (p, lab) in [(p1, "0 °C → 410"), (p2, "100 °C → 820")]:
        s += dot(p[0], p[1], 5, RED)
        s += line(p[0], p[1], p[0], y0, GREY, 1, dash="3,3")
    s += text(p1[0] + 8, p1[1] - 8, "точка 1: 0 °C → 410", 10.5, RED, "start", "bold")
    s += text(p2[0] - 8, p2[1] + 16, "точка 2: 100 °C → 820", 10.5, RED, "end", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.36, 0.42)), "S = Δвідлік / Δ°C", 11, GREEN, "start", "bold")
    s += text(x0 - 10, p1[1] + 4, "U₀", 11, GREEN, "end", "bold")
    s += text(w / 2, 308, "обернення: T = (відлік − U₀) / S", 12, INK, "middle", "bold")
    save("fig-28-6-2-two-point.svg", s)


def fig_tare():
    w, h = 660, 290
    s = header(w, h)
    s += text(w / 2, 26, "Одна точка зсуває (тара); дві точки зсувають і масштабують",
              14, INK, "middle", "bold")
    for k, (title, x0) in enumerate([("тара: 1 точка (нуль)", 60), ("повне: 2 точки", 380)]):
        y0, pw, ph = 244, 230, 176
        s += axes(x0, y0, pw + 10, ph + 10)
        s += text(x0 + pw / 2, y0 + 30, title, 12, INK, "middle", "bold")
        # «попливла» крива (пунктир)
        s += _plot_path(x0, y0, pw, ph, [(0, 0.34), (1, 0.86)], GREY, 1.8, dash="5,3")
        if k == 0:
            # тара: лише зсув вниз до нуля
            s += _plot_path(x0, y0, pw, ph, [(0, 0.1), (1, 0.62)], GREEN, 2.6)
            s += arrow(x0 + pw * 0.25, y0 - ph * 0.34, x0 + pw * 0.25, y0 - ph * 0.16, GREEN, 1.8)
            s += text(x0 + pw / 2, y0 - ph - 2, "лише зсув ↓", 10.5, GREEN, "middle", "italic")
        else:
            # повне: зсув + поворот
            s += _plot_path(x0, y0, pw, ph, [(0, 0.1), (1, 0.96)], GREEN, 2.6)
            s += arrow(x0 + pw * 0.2, y0 - ph * 0.34, x0 + pw * 0.2, y0 - ph * 0.16, GREEN, 1.8)
            s += arrow(x0 + pw * 0.85, y0 - ph * 0.7, x0 + pw * 0.85, y0 - ph * 0.88, GREEN, 1.8)
            s += text(x0 + pw / 2, y0 - ph - 2, "зсув + масштаб", 10.5, GREEN, "middle", "italic")
    save("fig-28-6-3-tare.svg", s)


def fig_multipoint():
    w, h = 620, 300
    s = header(w, h)
    s += text(w / 2, 26, "Багатоточкове: крива через відомі точки, між ними — інтерполяція",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 250, 460, 188
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "відлік", 11, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "величина", 11, INK, "middle", "bold")
    # справжня крива (гладка, нелінійна)
    real = [(j / 40, 0.1 + 0.82 * (j / 40) ** 1.7) for j in range(41)]
    s += _plot_path(x0, y0, pw, ph, real, GREY, 1.6, dash="4,3")
    s += text(*(_pt(x0, y0, pw, ph, 0.62, 0.34)), "справжня крива", 10, GREY, "start", "italic")
    # калібрувальні точки + кусково-лінійна
    knots = [0.05, 0.3, 0.55, 0.78, 0.95]
    kpts = [(kx, 0.1 + 0.82 * kx ** 1.7) for kx in knots]
    s += _plot_path(x0, y0, pw, ph, kpts, GREEN, 2.4)
    for (kx, ky) in kpts:
        p = _pt(x0, y0, pw, ph, kx, ky)
        s += dot(p[0], p[1], 4.5, RED)
    s += text(*(_pt(x0, y0, pw, ph, 0.18, 0.5)), "відомі точки + інтерполяція", 10.5, GREEN, "start", "bold")
    save("fig-28-6-4-multipoint.svg", s)


def fig_traceability():
    w, h = 560, 320
    s = header(w, h)
    s += text(w / 2, 26, "Простежуваність: точність стікає від еталона СІ до давача",
              13.5, INK, "middle", "bold")
    levels = [
        ("національний еталон / СІ", "#e6ecf5", "#2b3a67", 150),
        ("лабораторний еталон", "#eef2f6", BLUE, 230),
        ("робочий еталон", "#eef6ef", GREEN, 320),
        ("ваш давач", "#fff7e6", GOLD, 410),
    ]
    cy = 60
    bh = 46
    for (lbl, fill, col, bw) in levels:
        x = (w - bw) / 2
        s += rect(x, cy, bw, bh, fill=fill, stroke=col, sw=1.8, rx=6)
        s += text(w / 2, cy + bh / 2 + 5, lbl, 12, col, "middle", "bold")
        cy += bh + 14
    # стрілка «точність вниз»
    s += arrow(40, 80, 40, 280, RED, 2.4)
    s += text(30, 180, "точність", 11, RED, "middle", "bold")
    s += text(525, 80, "довіра", 11, GREY, "middle", "bold")
    s += text(525, 96, "↓", 14, GREY, "middle", "bold")
    s += text(w / 2, 312, "кожна ланка точніша за нижчу; калібрування не варте більше за еталон",
              10.5, INK, "middle", "italic")
    save("fig-28-6-5-traceability.svg", s)


def fig_pipeline():
    w, h = 700, 220
    s = header(w, h)
    s += text(w / 2, 28, "Де калібрування вмикається в тракт: коефіцієнти → величина",
              14, INK, "middle", "bold")
    boxes = [("АЦП:\nсирий відлік", GREY), ("застосувати\nкоефіцієнти", GREEN),
             ("величина\nв одиницях", BLUE)]
    bw, bh, y = 168, 70, 110
    xs = [30, 266, 502]
    for (lbl, col), x in zip(boxes, xs):
        s += rect(x, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.8, rx=8)
        a, b = lbl.split("\n")
        s += text(x + bw / 2, y + 28, a, 12, col, "middle", "bold")
        s += text(x + bw / 2, y + 46, b, 12, col, "middle", "bold")
    s += arrow(xs[0] + bw + 4, y + bh / 2, xs[1] - 4, y + bh / 2, INK, 2.2)
    s += arrow(xs[1] + bw + 4, y + bh / 2, xs[2] - 4, y + bh / 2, INK, 2.2)
    # джерело коефіцієнтів — згори в середній бокс
    s += text(xs[1] + bw / 2, 64, "нуль/нахил · LUT · поліном", 10.5, GREEN, "middle", "bold")
    s += text(xs[1] + bw / 2, 80, "(завод / поле / самокалібр.)", 10, GREY, "middle", "italic")
    s += arrow(xs[1] + bw / 2, 86, xs[1] + bw / 2, y - 4, GREEN, 1.8)
    save("fig-28-6-6-pipeline.svg", s)


def fig_fixes():
    w, h = 640, 300
    s = header(w, h)
    s += text(w / 2, 26, "Інструмент під ваду: що чим лікувати", 15, INK, "middle", "bold")
    rows = [
        ("зсув нуля", "калібрування / тара", GREEN),
        ("похибка нахилу", "калібрування (2 точки)", GREEN),
        ("нелінійність", "калібрування (багато точок)", GREEN),
        ("відомий дрейф", "калібрування + темп-компенсація", GREEN),
        ("випадковий шум", "усереднення / фільтр (Розд. 30)", BLUE),
        ("гістерезис", "підхід з одного боку", "#9a4ea8"),
    ]
    x0, y0 = 40, 50
    cw1, cw2, rh = 230, 330, 36
    s += rect(x0, y0, cw1, rh, fill="#eef1f6", stroke=GREY, sw=1)
    s += rect(x0 + cw1, y0, cw2, rh, fill="#eef1f6", stroke=GREY, sw=1)
    s += text(x0 + 12, y0 + 23, "вада", 12.5, INK, "start", "bold")
    s += text(x0 + cw1 + 12, y0 + 23, "лік", 12.5, INK, "start", "bold")
    for i, (defect, fix, col) in enumerate(rows):
        yy = y0 + rh * (i + 1)
        s += rect(x0, yy, cw1, rh, fill="#ffffff", stroke=GREY, sw=0.8)
        s += rect(x0 + cw1, yy, cw2, rh, fill="#ffffff", stroke=GREY, sw=0.8)
        s += text(x0 + 12, yy + 23, defect, 11.5, INK, "start", "bold")
        s += text(x0 + cw1 + 12, yy + 23, fix, 11.5, col, "start", "bold")
    s += text(w / 2, y0 + rh * 7 + 22, "систематичне — калібрують; випадкове — фільтрують; шлях — підходом",
              11, GREY, "middle", "italic")
    save("fig-28-6-7-fixes.svg", s)


# ── символи для §28.7 (ОП, рівневий стовпчик) ────────────────────────────────

def opamp(cx, cy, sz=30, col=INK):
    out = (f'<path d="M {cx - sz:.1f},{cy - sz:.1f} L {cx - sz:.1f},{cy + sz:.1f} '
           f'L {cx + sz:.1f},{cy:.1f} Z" fill="#ffffff" stroke="{col}" stroke-width="1.8"/>\n')
    out += text(cx - sz + 7, cy - sz * 0.4 + 4, "+", 12, col, "start", "bold")
    out += text(cx - sz + 7, cy + sz * 0.4 + 4, "−", 12, col, "start", "bold")
    return out


def _bar(x, y, h, frac, col, lbl=""):
    out = rect(x, y, 26, h, fill="#ffffff", stroke=INK, sw=1.4)
    fh = h * frac
    out += rect(x, y + h - fh, 26, fh, fill=col, stroke="none")
    out += rect(x, y, 26, h, fill="none", stroke=INK, sw=1.4)
    if lbl:
        out += text(x + 13, y + h + 16, lbl, 11, INK, "middle", "bold")
    return out


# ════════════════════════════════════════════════════════════════════════════
#  §28.7 Узгодження давача з входом
# ════════════════════════════════════════════════════════════════════════════

def fig_loading():
    w, h = 640, 280
    s = header(w, h)
    s += text(w / 2, 26, "Під'єднання утворює дільник: вхід просаджує джерело давача",
              14, INK, "middle", "bold")
    # модель давача: джерело + R_дж
    gnd = 220
    s += source(80, 150, 18)
    s += text(80, 122, "U_дж", 11, INK, "middle", "bold")
    s += text(60, 168, "давач", 10.5, GREY, "middle", "italic")
    s += line(80, 132, 80, 100, INK, 2)
    s += line(80, 100, 150, 100, INK, 2)
    s += res_h(150, 100, 80, INK, 2)
    s += text(190, 86, "R_дж", 11, INK, "middle", "bold")
    s += line(230, 100, 330, 100, INK, 2)
    s += dot(330, 100, 4, INK)
    s += text(330, 88, "вузол", 10, GREY, "middle", "italic")
    # вхід: R_вх до землі
    s += line(330, 100, 330, 130, INK, 2)
    s += res_v(330, 130, 60, BLUE, 2.2)
    s += text(352, 162, "R_вх", 11, BLUE, "start", "bold")
    s += line(330, 190, 330, gnd, INK, 2)
    # земля
    s += line(80, 168, 80, gnd, INK, 2)
    s += line(80, gnd, 410, gnd, INK, 2)
    # відведення на АЦП
    s += line(330, 100, 420, 100, GREEN, 2)
    s += text(426, 104, "→ АЦП (U_вим)", 11, GREEN, "start", "bold")
    s += text(w / 2, 258, "U_вим = U_дж · R_вх / (R_дж + R_вх)   — завжди менше за U_дж",
              12.5, INK, "middle", "bold")
    save("fig-28-7-1-loading.svg", s)


def fig_high_z():
    w, h = 660, 280
    s = header(w, h)
    s += text(w / 2, 26, "Малий вхідний опір просаджує сигнал, великий — зберігає",
              14, INK, "middle", "bold")
    for k, (title, frac, rin, col) in enumerate(
            [("R_вх ≈ R_дж", 0.5, "малий R_вх", RED),
             ("R_вх ≫ R_дж (×100)", 0.99, "великий R_вх", GREEN)]):
        x0 = 40 + k * 330
        s += rect(x0, 52, 290, 200, fill="#fbfbfb", stroke=col, sw=1.4, rx=8)
        s += text(x0 + 145, 74, title, 12.5, col, "middle", "bold")
        # дільник схематично
        s += source(x0 + 50, 150, 15)
        s += line(x0 + 50, 135, x0 + 50, 115, INK, 1.8)
        s += line(x0 + 50, 115, x0 + 100, 115, INK, 1.8)
        s += res_h(x0 + 100, 115, 50, INK, 1.8)
        s += line(x0 + 150, 115, x0 + 175, 115, INK, 1.8)
        s += res_v(x0 + 175, 122, 48, col, 2)
        s += line(x0 + 175, 170, x0 + 175, 195, INK, 1.8)
        s += line(x0 + 50, 165, x0 + 50, 195, INK, 1.8)
        s += line(x0 + 50, 195, x0 + 175, 195, INK, 1.8)
        s += text(x0 + 175, 210, rin, 9.5, col, "middle", "italic")
        # стовпчик рівня
        s += _bar(x0 + 232, 100, 110, frac, col)
        s += text(x0 + 245, 96, "доходить", 9.5, INK, "middle")
        s += text(x0 + 245, 230, f"{int(frac*100)} %", 12, col, "middle", "bold")
    save("fig-28-7-2-high-z.svg", s)


def fig_buffer():
    w, h = 660, 250
    s = header(w, h)
    s += text(w / 2, 26, "Повторювач напруги розв'язує високоомний давач від АЦП",
              14, INK, "middle", "bold")
    # давач (джерело + великий R)
    s += source(70, 140, 18)
    s += text(70, 112, "U_дж", 11, INK, "middle", "bold")
    s += line(70, 122, 70, 96, INK, 2)
    s += line(70, 96, 130, 96, INK, 2)
    s += res_h(130, 96, 60, INK, 2)
    s += text(160, 82, "R_дж велике", 10, INK, "middle", "bold")
    s += line(190, 96, 235, 96, INK, 2)
    s += line(70, 158, 70, 210, INK, 2)
    s += line(70, 210, 470, 210, INK, 2)
    # ОП-повторювач
    cx, cy = 280, 96
    s += opamp(cx, cy, 30)
    s += line(235, cy - 12, cx - 30, cy - 12, INK, 2)   # + вхід від давача
    s += line(cx + 30, cy, 360, cy, INK, 2)             # вихід
    s += line(360, cy, 360, cy + 34, INK, 2)            # зворотний зв'язок
    s += line(360, cy + 34, cx - 44, cy + 34, INK, 2)
    s += line(cx - 44, cy + 34, cx - 44, cy + 12, INK, 2)
    s += line(cx - 44, cy + 12, cx - 30, cy + 12, INK, 2)
    s += text(cx, cy + 58, "повторювач (×1)", 10.5, INK, "middle", "bold")
    # до АЦП
    s += line(360, cy, 430, cy, GREEN, 2)
    s += rect(430, cy - 22, 70, 44, fill="#eef4fb", stroke=BLUE, sw=1.5, rx=6)
    s += text(465, cy + 4, "АЦП", 12, BLUE, "middle", "bold")
    s += text(180, 150, "вхід ∞ → не вантажить", 10.5, GREEN, "middle", "italic")
    s += text(400, 150, "вихід ≈ 0 → живить АЦП", 10.5, GREEN, "middle", "italic")
    save("fig-28-7-3-buffer.svg", s)


def fig_level():
    w, h = 600, 280
    s = header(w, h)
    s += text(w / 2, 26, "Підгонка рівня: розмах давача — рівно на шкалу АЦП",
              14, INK, "middle", "bold")
    # лівий стовпчик — давач (вузький, зі зсувом)
    s += rect(110, 60, 60, 180, fill="#fff", stroke=INK, sw=1.4)
    s += rect(110, 150, 60, 50, fill="#cfe0cf", stroke=GREEN, sw=1.4)
    s += text(140, 252, "давач", 11, INK, "middle", "bold")
    s += text(140, 145, "розмах", 9.5, GREEN, "middle", "italic")
    # права — АЦП (повна шкала)
    s += rect(430, 60, 60, 180, fill="#fff", stroke=INK, sw=1.4)
    s += rect(430, 64, 60, 172, fill="#cfe0f3", stroke=BLUE, sw=1.4)
    s += text(460, 252, "шкала АЦП", 11, BLUE, "middle", "bold")
    # стрілки розтягу
    s += arrow(180, 175, 420, 230, GREEN, 2)
    s += arrow(180, 150, 420, 66, GREEN, 2)
    s += text(300, 130, "підсилення + зсув", 12, GREEN, "middle", "bold")
    s += text(300, 150, "(розтягти на всю шкалу)", 10.5, INK, "middle", "italic")
    save("fig-28-7-4-level.svg", s)


def fig_settling():
    w, h = 660, 290
    s = header(w, h)
    s += text(w / 2, 26, "Конденсатор вибірки АЦП мусить устигнути зарядитись",
              14, INK, "middle", "bold")
    # джерело + R_дж → ключ → C_вб
    s += source(60, 130, 16)
    s += line(60, 130, 60, 96, INK, 2)
    s += line(60, 96, 110, 96, INK, 2)
    s += res_h(110, 96, 60, INK, 2)
    s += text(140, 82, "R_дж", 10.5, INK, "middle", "bold")
    s += line(170, 96, 220, 96, INK, 2)
    # ключ вибірки
    s += line(220, 96, 244, 84, INK, 2)
    s += dot(220, 96, 3, INK)
    s += dot(248, 96, 3, INK)
    s += text(234, 74, "вибірка", 9.5, GREY, "middle", "italic")
    s += line(248, 96, 290, 96, INK, 2)
    # C_вб
    s += line(290, 96, 290, 112, INK, 2)
    s += line(276, 112, 304, 112, INK, 3)
    s += line(276, 120, 304, 120, INK, 3)
    s += line(290, 120, 290, 150, INK, 2)
    s += text(314, 118, "C_вб", 10.5, INK, "start", "bold")
    s += line(60, 146, 60, 175, INK, 2)
    s += line(60, 175, 290, 175, INK, 2)
    s += line(290, 150, 290, 175, INK, 2)
    # графік заряду
    gx, gy, gw, gh = 380, 230, 230, 150
    s += axes(gx, gy, gw + 8, gh + 8, GREY)
    s += text(gx - 6, gy - gh - 4, "U_C", 10.5, INK, "end", "bold")
    s += text(gx + gw, gy + 16, "час", 10, INK, "middle")
    s += line(gx, gy - gh + 6, gx + gw, gy - gh + 6, FAINT, 1, dash="3,3")
    s += text(gx + gw - 6, gy - gh - 2, "ціль", 9.5, GREY, "end")
    # низький R — швидко доходить
    s += _plot_path(gx, gy, gw, gh, [(0, 0), (0.15, 0.55), (0.35, 0.85), (0.6, 0.95), (1, 0.97)], GREEN, 2.4)
    s += text(*(_pt(gx, gy, gw, gh, 0.5, 0.8)), "малий R_дж ✓", 10, GREEN, "start", "bold")
    # високий R — не встигає
    s += _plot_path(gx, gy, gw, gh, [(0, 0), (0.3, 0.22), (0.6, 0.4), (1, 0.58)], RED, 2.4)
    s += text(*(_pt(gx, gy, gw, gh, 0.55, 0.34)), "велике R_дж ✗", 10, RED, "start", "bold")
    s += line(gx + gw * 0.62, gy, gx + gw * 0.62, gy - gh, BLUE, 1.4, dash="4,3")
    s += text(gx + gw * 0.62, gy + 16, "кінець вибірки", 9, BLUE, "middle")
    save("fig-28-7-5-settling.svg", s)


def fig_input_filter():
    w, h = 660, 270
    s = header(w, h)
    s += text(w / 2, 26, "Вхідна RC-ланка: фільтр, антиаліас і захист одночасно",
              14, INK, "middle", "bold")
    y = 120
    s += text(60, y - 24, "сигнал", 11, INK, "middle", "bold")
    s += line(40, y, 90, y, INK, 2)
    s += res_h(90, y, 70, INK, 2)
    s += text(125, y - 14, "R", 11, INK, "middle", "bold")
    s += line(160, y, 300, y, INK, 2)
    s += dot(230, y, 4, INK)
    # C до землі
    s += line(230, y, 230, y + 24, INK, 2)
    s += line(216, y + 24, 244, y + 24, INK, 3)
    s += line(216, y + 32, 244, y + 32, INK, 3)
    s += line(230, y + 32, 230, y + 62, INK, 2)
    s += text(252, y + 30, "C", 11, INK, "start", "bold")
    # діоди-обмежувачі від вузла до V+ і GND
    s += line(230, y, 230, y - 50, BLUE, 1.6)
    s += f'<path d="M 222,{y-50} L 238,{y-50} L 230,{y-62} Z" fill="#fff" stroke="{BLUE}" stroke-width="1.4"/>\n'
    s += line(222, y - 62, 238, y - 62, BLUE, 1.6)
    s += text(248, y - 54, "до V+", 9.5, BLUE, "start")
    s += dot(230, y, 3, INK)
    # земля
    s += line(40, y + 80, 300, y + 80, INK, 1.6)
    s += line(230, y + 62, 230, y + 80, INK, 2)
    s += line(40, y, 40, y + 80, INK, 1.6)
    # до АЦП
    s += line(230, y, 360, y, GREEN, 2)
    s += rect(360, y - 22, 64, 44, fill="#eef4fb", stroke=BLUE, sw=1.5, rx=6)
    s += text(392, y + 4, "АЦП", 12, BLUE, "middle", "bold")
    # підписи ролей
    s += rect(450, 60, 190, 150, fill="#fbfbfb", stroke=FAINT, sw=1, rx=6)
    s += text(545, 82, "три ролі однієї ланки:", 11, INK, "middle", "bold")
    for i, (t, c) in enumerate([("R+C — фільтр НЧ (шум)", INK),
                                ("R+C — антиаліас перед АЦП", INK),
                                ("R + діоди — захист ніжки", BLUE)]):
        s += text(465, 108 + i * 26, "• " + t, 10.5, c, "start")
    save("fig-28-7-6-input-filter.svg", s)


def fig_frontend():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Зведений «гарний» вхідний тракт давача",
              15, INK, "middle", "bold")
    # екран (пунктирна рамка навколо сигнального шляху)
    s += rect(30, 58, 530, 120, fill="none", stroke=GREY, sw=1.4, rx=10)
    s += text(48, 74, "екран", 10, GREY, "start", "italic")
    boxes = [("давач\n(high-Z)", GOLD), ("буфер", GREEN), ("рівень\n(×, зсув)", GREEN),
             ("RC +\nзахист", BLUE), ("АЦП", BLUE)]
    bw, bh, y = 92, 60, 90
    xs = [44, 152, 260, 368, 476]
    for (lbl, col), x in zip(boxes, xs):
        s += rect(x, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.7, rx=7)
        a, b = (lbl.split("\n") + [""])[:2]
        s += text(x + bw / 2, y + (26 if b else 34), a, 11, col, "middle", "bold")
        if b:
            s += text(x + bw / 2, y + 44, b, 11, col, "middle", "bold")
    for i in range(4):
        s += arrow(xs[i] + bw + 2, y + bh / 2, xs[i + 1] - 2, y + bh / 2, INK, 2)
    # аналогова земля
    s += line(300, 200, 300, 216, INK, 2)
    s += line(286, 216, 314, 216, INK, 2)
    s += line(290, 221, 310, 221, INK, 1.6)
    s += line(294, 226, 306, 226, INK, 1.4)
    s += text(300, 244, "окрема аналогова земля («зіркою»)", 11, INK, "middle", "bold")
    s += text(w / 2, 268, "для дальніх ліній — диференційна пара (синфазна завада скорочується)",
              11, GREY, "middle", "italic")
    save("fig-28-7-7-frontend.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 28 — Зеебек і термопара (секція 0)
    fig_seebeck_experiment()
    fig_diffusion()
    fig_three_effects()
    fig_thermocouple_sensor()
    # §28.1 Що таке давач
    fig_translator()
    fig_chain()
    fig_families()
    fig_duality()
    fig_output_forms()
    fig_imperfect_chain()
    # §28.2 Класи перетворювачів
    fig_three_handles()
    fig_resistive()
    fig_wheatstone()
    fig_capacitive()
    fig_inductive()
    fig_dc_ac()
    fig_compare()
    # §28.3 П'єзо-, оптичні, напівпровідникові
    fig_28_3_overview()
    fig_piezo()
    fig_piezo_ac()
    fig_photodiode()
    fig_hall()
    fig_semic_temp()
    fig_28_3_compare()
    # §28.4 Характеристики
    fig_transfer()
    fig_sensitivity()
    fig_range()
    fig_linearity()
    fig_accuracy_precision()
    fig_resolution()
    fig_datasheet()
    # §28.5 Дрейф, гістерезис, шум
    fig_28_5_overview()
    fig_drift()
    fig_tempco()
    fig_hysteresis()
    fig_noise()
    fig_averaging()
    # §28.6 Калібрування
    fig_inverse()
    fig_two_point()
    fig_tare()
    fig_multipoint()
    fig_traceability()
    fig_pipeline()
    fig_fixes()
    # §28.7 Узгодження з входом
    fig_loading()
    fig_high_z()
    fig_buffer()
    fig_level()
    fig_settling()
    fig_input_filter()
    fig_frontend()
    print("OK — фігури Розділу 28 (історія + §28.1–§28.7) згенеровано в", OUT)
