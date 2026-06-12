# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.8.9m «Шумовий бюджет входу ОП»
(offset, дрейф, nV/√Гц). Чистий Python, без залежностей. Вивід → ./img/.

НЕ чіпає головний figs.py розділу. Імена файлів унікальні:
  fig-13-9m-noise-1-budget.svg  — складання похибок входу в один бюджет (стовпчики)
  fig-13-9m-noise-2-density.svg — спектральна густина шуму: 1/f-кут і білий поличка

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділу (самодостатній скрипт).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf2dd"
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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ---------------------------------------------------------------------------
# Рис. 2.8.9m.1 — складання похибок входу в один бюджет.
# Ліворуч три джерела похибки, наведені до ВХОДУ (offset, дрейф×ΔT, шум),
# праворуч — як вони складаються: постійні (offset+дрейф) арифметично,
# а до них корінь-із-суми-квадратів зі (систематична) ⊕ (шум).
# ---------------------------------------------------------------------------
def fig_budget():
    W, H = 720, 430
    s = header(W, H)
    s += text(W / 2, 28, "Шумовий бюджет, наведений до входу (мкВ)", 17, INK, "middle", "bold")

    # координати «осі» — спільна нульова лінія для всіх стовпчиків
    base_y = 350.0
    scale = 2.6  # пікселів на мкВ
    bw = 64      # ширина стовпчика

    # значення прикладу (мкВ, наведені до входу)
    Vos   = 60.0     # зсув (після підлаштування лишок)
    drift = 30.0     # дрейф: 1 мкВ/°C × 30 °C
    noise = 40.0     # інтегрований шум у смузі (rms)

    def bar(cx, h_uv, fill, stroke, label, val_s, sub=""):
        h = h_uv * scale
        o = rect(cx - bw / 2, base_y - h, bw, h, fill, stroke, 2, 4)
        o += text(cx, base_y - h - 10, val_s, 14, stroke, "middle", "bold")
        o += text(cx, base_y + 22, label, 13.5, INK, "middle", "bold")
        if sub:
            o += text(cx, base_y + 40, sub, 11.5, GREY, "middle")
        return o

    # три джерела ліворуч
    s += line(70, base_y, 360, base_y, INK, 2)
    s += bar(115, Vos, LBLUE, BLUE, "зсув Vos", "60", "(після підлашт.)")
    s += bar(205, drift, LSUN, SUN, "дрейф·ΔT", "30", "(1 мкВ/°C × 30°)")
    s += bar(295, noise, LGRN, GREEN, "шум (rms)", "40", "у смузі")

    # знак «постійні складають арифметично»
    s += text(160, base_y + 66, "+ (систематичні: пряма сума)", 12.5, INK, "middle", "bold")

    # праворуч — підсумок
    s += line(430, base_y, 660, base_y, INK, 2)

    # систематична частина = Vos + drift = 90, стек
    sys = Vos + drift
    h_vos = Vos * scale
    h_dr = drift * scale
    cx = 500
    s += rect(cx - bw / 2, base_y - h_vos, bw, h_vos, LBLUE, BLUE, 2, 4)
    s += rect(cx - bw / 2, base_y - h_vos - h_dr, bw, h_dr, LSUN, SUN, 2, 4)
    s += text(cx, base_y - (h_vos + h_dr) - 10, "90", 14, INK, "middle", "bold")
    s += text(cx, base_y + 22, "DC-похибка", 13.5, INK, "middle", "bold")
    s += text(cx, base_y + 40, "(зсув + дрейф)", 11.5, GREY, "middle")

    # повний бюджет = sqrt(sys^2 + noise^2) ≈ sqrt(90^2+40^2)=98.5
    tot = math.sqrt(sys * sys + noise * noise)
    cx2 = 610
    h_tot = tot * scale
    s += rect(cx2 - bw / 2, base_y - h_tot, bw, h_tot, "#f0e9f6", "#6b3fa0", 2.4, 4)
    s += text(cx2, base_y - h_tot - 10, "≈99", 14, "#6b3fa0", "middle", "bold")
    s += text(cx2, base_y + 22, "усього", 13.5, "#6b3fa0", "middle", "bold")
    s += text(cx2, base_y + 40, "√(90²+40²)", 11.5, GREY, "middle")

    # стрілка переходу
    s += arrow(372, 150, 422, 150, INK, 2.2)
    s += text(397, 138, "звести", 11.5, INK, "middle")

    # підпис-формула знизу
    s += text(W / 2, base_y + 78, "DC-частини — сумою; шум до них — коренем із суми квадратів (⊕)",
              12.5, INK, "middle")
    save("fig-13-9m-noise-1-budget.svg", s)


# ---------------------------------------------------------------------------
# Рис. 2.8.9m.2 — спектральна густина шуму: 1/f-«рожевий» нахил
# і білий «поличка» eₙ (nV/√Гц), кут зламу f_c, інтегрування у смузі.
# Лог-лог осі.
# ---------------------------------------------------------------------------
def fig_density():
    W, H = 720, 430
    s = header(W, H)
    s += text(W / 2, 28, "Спектральна густина шуму ОП  eₙ(f),  нВ/√Гц", 17, INK, "middle", "bold")

    # рамка графіка
    ox, oy = 95, 70          # лівий-верх
    pw, ph = 560, 270        # ширина/висота області
    bx0, bx1 = ox, ox + pw   # ліва/права
    by0, by1 = oy, oy + ph   # верх/низ
    s += rect(ox, oy, pw, ph, "#ffffff", "#c9d3dc", 1.4, 4)

    # осі
    s += arrow(bx0, by1, bx1 + 14, by1, INK, 2)         # X (lg f)
    s += arrow(bx0, by1, bx0, by0 - 12, INK, 2)         # Y (lg eₙ)
    s += text(bx1 + 16, by1 + 22, "lg f (частота)", 13, INK, "middle")
    s += text(ox - 8, by0 - 20, "eₙ", 14, INK, "middle", "bold")

    # декади по X: f від 0.1 до 100k -> 7 декад, рівномірно
    decades = ["0.1", "1", "10", "100", "1k", "10k", "100k"]
    nx = len(decades)
    for i, lab in enumerate(decades):
        x = bx0 + pw * i / (nx - 1)
        s += line(x, by1, x, by1 + 5, INK, 1.4)
        s += text(x, by1 + 22, lab, 12, INK, "middle")
        if i:
            s += line(x, by0, x, by1, FAINT, 1)

    # рівень білого шуму (поличка)
    floor_y = by0 + ph * 0.62        # рівень eₙ
    s += line(bx0, floor_y, bx1, floor_y, FAINT, 1, "4 4")
    s += text(bx1 - 4, floor_y - 8, "eₙ = 20 нВ/√Гц  (білий поличка)", 12.5, GREEN, "end")

    # крива: 1/f-нахил до f_c, далі поличка.
    # f_c (кут зламу) — на декаді «100» (індекс 3)
    fc_i = 3.0
    fc_x = bx0 + pw * fc_i / (nx - 1)
    # 1/f-вітка: на лог-лог -1/2 нахилу для напруги (e ~ 1/√f). Будуємо точками.
    pts = []
    for j in range(0, 121):
        t = j / 120.0
        idx = t * (nx - 1)                      # позиція в декадах 0..6
        if idx >= fc_i:
            y = floor_y
        else:
            # e(f) = eₙ * sqrt(f_c/f); у лог-координатах нахил −1/2 декади висоти
            dec_below = fc_i - idx              # на скільки декад нижче кута
            # висота: +1/2 декади густини за декаду частоти; одна декада висоти = ph*0.16
            y = floor_y - dec_below * (ph * 0.16) * 0.5
        x = bx0 + pw * idx / (nx - 1)
        pts.append((x, y))
    s += _poly(pts, RED, 2.8)
    s += text(bx0 + 70, by0 + 30, "1/f-шум", 13, RED, "start", "bold")
    s += text(bx0 + 70, by0 + 48, "(рожевий, ~1/√f)", 11.5, RED, "start")

    # кут зламу f_c
    s += line(fc_x, by0, fc_x, by1, BLUE, 1.4, "5 4")
    s += circle(fc_x, floor_y, 4, BLUE, BLUE, 1)
    s += text(fc_x + 6, by0 + 18, "f_c — кут зламу", 12.5, BLUE, "start", "bold")
    s += text(fc_x + 6, by0 + 34, "(нижче — 1/f, вище — білий)", 11, BLUE, "start")

    # смуга інтегрування [f1, f2] — заштрихована (тут уся корисна смуга до f2)
    f2_i = 5.0   # 10k
    f2_x = bx0 + pw * f2_i / (nx - 1)
    s += rect(bx0, by0, f2_x - bx0, ph, "rgba(31,138,59,0.06)", "none", 0)
    s += line(f2_x, by0, f2_x, by1, GREEN, 1.4, "5 4")
    s += text(f2_x - 4, by1 - 8, "f₂ (верх смуги)", 12, GREEN, "end")

    # підпис: інтегрування дає rms
    s += text(W / 2, by1 + 52,
              "Площу під eₙ²(f) у смузі беруть під корінь → повний rms-шум Vₙ",
              12.5, INK, "middle")
    s += text(W / 2, by1 + 72,
              "білу частину: Vₙ ≈ eₙ·√(смуга);  1/f додає внесок ∝ √(ln(f_c/f₁))",
              11.5, GREY, "middle")
    save("fig-13-9m-noise-2-density.svg", s)


if __name__ == "__main__":
    fig_budget()
    fig_density()
    print("done")
