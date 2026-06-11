# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки 2.11.7i —
«Баліга, RCA проти GE і спірне батьківство IGBT».

Чистий Python без залежностей. Вивід → ./img/ із УНІКАЛЬНИМИ іменами
(префікс fig-11-7i-…), щоб не зачіпати головний figs.py розділу.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Нумерація підписів у тексті —
посекційно за темою: «Рис. 2.11.7i.k».
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (копія спільного стилю розділів) ────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fbf3df"
AMBER = "#caa24a"
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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{r}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def write(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 2.11.7i.1 — стрічка часу: скупчення незалежних заявок 1968→1985
# Ідея, яку важко передати словами: чотири команди на трьох континентах
# прийшли до того самого приладу майже одночасно (1978–1982), а «справжнє
# народження» сталося аж тоді, коли прибрали защіпку (1984–1985).
# ════════════════════════════════════════════════════════════════════════════
def fig_timeline():
    W, H = 900, 540
    s = header(W, H)
    s += text(W / 2, 30, "Спірне батьківство IGBT: чотири незалежні внески за п'ятнадцять років",
              size=17, weight="bold", anchor="middle")

    # вісь часу
    x0, x1 = 70, 830
    axy = 250
    yr0, yr1 = 1967, 1987

    def X(year):
        return x0 + (year - yr0) / (yr1 - yr0) * (x1 - x0)

    s += line(x0, axy, x1, axy, color=INK, w=3)
    s += arrow(x1, axy, x1 + 20, axy, color=INK, w=3)
    for yr in range(1968, 1987, 2):
        s += line(X(yr), axy - 5, X(yr), axy + 5, color=GREY, w=1.5)
        s += text(X(yr), axy + 22, str(yr), size=12, color=GREY, anchor="middle")

    # «провалля непотрібності» 1968→1978
    s += rect(X(1968), axy - 36, X(1978) - X(1968), 18, fill=FAINT, stroke="none")
    s += text((X(1968) + X(1978)) / 2, axy - 23,
              "десять років ідея нікому не потрібна", size=11, color=GREY,
              anchor="middle", style="italic")

    # подія: рамка-картка з виноскою на вісь (tier=0 ближній ряд, 1 дальній)
    def event(year, side, title, who, color, bg, tier=0):
        x = X(year)
        bw, bh = 168, 64
        bx = x - bw / 2
        if side == "up":
            by = axy - 150 - tier * 78
            s_local = line(x, axy - 6, x, by + bh, color=color, w=2, dash="3,3")
        else:
            by = axy + 70 + tier * 78
            s_local = line(x, axy + 6, x, by, color=color, w=2, dash="3,3")
        s_local += circle(x, axy, 5, fill=color, stroke=color)
        s_local += rect(bx, by, bw, bh, fill=bg, stroke=color, sw=2, rx=7)
        s_local += text(bx + bw / 2, by + 19, title, size=12.5, weight="bold",
                        anchor="middle", color=color)
        # who може мати кілька рядків
        for i, ln in enumerate(who):
            s_local += text(bx + bw / 2, by + 36 + i * 14, ln, size=11,
                            anchor="middle", color=INK)
        return s_local

    s += event(1968, "up", "1968 · ідея на папері",
               ["Ямаґамі, Акаґірі", "Mitsubishi · яп. патент"], BLUE, LBLUE)
    s += event(1978, "down", "1978 · перші прилади",
               ["Пламмер, Шарф", "Stanford · патент + ISSCC"], GREEN, LGRN)
    s += event(1979, "up", "1979 · виготовив і виміряв",
               ["Баліга (GE)", "стаття, Electronics Letters"], RED, LRED)
    s += event(1980, "down", "1980 · конкурентний патент",
               ["Бекке, Вітлі (RCA)", "видано 1982, US 4,364,073"], INK, FAINT, tier=1)
    s += event(1984, "up", "1984–85 · без защіпки",
               ["Накаґава (Toshiba)", "«справжнє народження»"], AMBER, LAMB)

    # дужка «майже одночасно»: 1978 (Пламмер) → 1980 (RCA)
    by = axy + 230
    s += line(X(1978), by, X(1980), by, color=GREY, w=1.5)
    s += line(X(1978), by - 6, X(1978), by, color=GREY, w=1.5)
    s += line(X(1980), by - 6, X(1980), by, color=GREY, w=1.5)
    s += text((X(1978) + X(1980)) / 2, by + 16,
              "чотири команди — за ~2 роки", size=11, color=GREY,
              anchor="middle", style="italic")

    s += footer()
    write("fig-11-7i-1-igbt-timeline.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 2.11.7i.2 — паразитний тиристор усередині IGBT і защіпка (latch-up)
# Ідея, яку важко передати словами: чотири шари → схований PNPN → за великого
# струму він «защіпається» і затвор більше нічим не керує (саморуйнування).
# ════════════════════════════════════════════════════════════════════════════
def fig_latchup():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 30, "Чому IGBT десять років «не виходив»: схована защіпка",
              size=17, weight="bold", anchor="middle")

    # ── ліворуч: спрощений переріз із чотирма шарами ──
    cx, cy, cw = 70, 70, 300
    # затвор зверху
    s += rect(cx, cy, cw, 26, fill="#dfe6ef", stroke=INK, sw=1.5)
    s += text(cx + cw / 2, cy + 17, "затвор (MOS) — керує каналом",
              size=11.5, anchor="middle")
    # n+ емітер (два острівці)
    s += rect(cx, cy + 26, 70, 26, fill=LBLUE, stroke=INK, sw=1.5)
    s += text(cx + 35, cy + 43, "n+", size=12, anchor="middle", color=BLUE, weight="bold")
    s += rect(cx + cw - 70, cy + 26, 70, 26, fill=LBLUE, stroke=INK, sw=1.5)
    s += text(cx + cw - 35, cy + 43, "n+", size=12, anchor="middle", color=BLUE, weight="bold")
    # p-body
    s += rect(cx, cy + 52, cw, 40, fill=LRED, stroke=INK, sw=1.5)
    s += text(cx + cw / 2, cy + 76, "p (тіло)", size=12, anchor="middle", color=RED, weight="bold")
    # n- дрейф
    s += rect(cx, cy + 92, cw, 50, fill=LBLUE, stroke=INK, sw=1.5)
    s += text(cx + cw / 2, cy + 121, "n− (дрейф, тримає напругу)",
              size=11.5, anchor="middle", color=BLUE)
    # p+ анод/колектор — це і є додаткова інжекція дірок
    s += rect(cx, cy + 142, cw, 30, fill=LRED, stroke=INK, sw=1.5)
    s += text(cx + cw / 2, cy + 162, "p+ (анод) — нове проти MOSFET",
              size=11.5, anchor="middle", color=RED, weight="bold")
    # колектор
    s += rect(cx, cy + 172, cw, 22, fill="#dfe6ef", stroke=INK, sw=1.5)
    s += text(cx + cw / 2, cy + 187, "колектор", size=11.5, anchor="middle")

    s += text(cx + cw / 2, cy + 218, "Чотири шари n+/p/n−/p+ —",
              size=12, anchor="middle", style="italic", color=GREY)
    s += text(cx + cw / 2, cy + 234, "це схований PNPN-тиристор (§2.11.2)",
              size=12, anchor="middle", style="italic", color=GREY)

    # ── праворуч: еквівалентна схема (MOSFET + 2 транзистори = защіпка) ──
    rx = 470
    s += text(rx + 180, 60, "Що це насправді:", size=13.5, weight="bold", anchor="middle")

    # MOSFET (символічно)
    s += rect(rx + 20, 90, 110, 50, fill=LGRN, stroke=GREEN, sw=2, rx=6)
    s += text(rx + 75, 112, "MOSFET", size=12.5, anchor="middle", weight="bold", color=GREEN)
    s += text(rx + 75, 130, "(керує затвор)", size=10.5, anchor="middle", color=GREEN)

    # PNP
    s += rect(rx + 230, 90, 110, 50, fill=LRED, stroke=RED, sw=2, rx=6)
    s += text(rx + 285, 112, "PNP", size=12.5, anchor="middle", weight="bold", color=RED)
    s += text(rx + 285, 130, "(корисний)", size=10.5, anchor="middle", color=RED)

    # NPN — паразит
    s += rect(rx + 230, 175, 110, 50, fill=LBLUE, stroke=BLUE, sw=2, rx=6)
    s += text(rx + 285, 197, "NPN", size=12.5, anchor="middle", weight="bold", color=BLUE)
    s += text(rx + 285, 215, "паразит!", size=10.5, anchor="middle", color=BLUE, weight="bold")

    # зв'язки керування
    s += arrow(rx + 130, 115, rx + 230, 115, color=GREEN, w=2)
    s += text(rx + 180, 107, "вмикає", size=10.5, anchor="middle", color=GREEN)

    # позитивний зворотний зв'язок PNP↔NPN (защіпка)
    s += arrow(rx + 285, 140, rx + 285, 173, color=RED, w=2.4)
    s += arrow(rx + 270, 173, rx + 270, 142, color=BLUE, w=2.4)
    s += text(rx + 350, 160, "взаємний", size=10.5, anchor="start", color=INK)
    s += text(rx + 350, 175, "підкач —", size=10.5, anchor="start", color=INK)
    s += text(rx + 350, 190, "защіпка", size=11, anchor="start", color=INK, weight="bold")

    # підсумок-стрічка внизу праворуч
    s += rect(rx + 20, 250, 360, 92, fill=LAMB, stroke=AMBER, sw=2, rx=8)
    s += text(rx + 200, 273, "За великого струму NPN «прокидається»:",
              size=12, anchor="middle", weight="bold")
    s += text(rx + 200, 293, "PNP і NPN починають живити один одного,",
              size=11.5, anchor="middle")
    s += text(rx + 200, 311, "защіпка замикається — затвор уже нічим",
              size=11.5, anchor="middle")
    s += text(rx + 200, 329, "не керує — прилад згоряє. Розв'язок",
              size=11.5, anchor="middle")
    s += text(rx + 200, 347, "(Накаґава, 1984): не дати NPN увімкнутись.",
              size=11.5, anchor="middle")

    s += footer()
    write("fig-11-7i-2-latchup.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_latchup()
    print("done")
