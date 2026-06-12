# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🧮-вставки до теми 2.5.7 — «Фотон і заборонена зона».
НЕ чіпає головний figs.py розділу. Імена файлів унікальні (fig-10-7m-*).
Чистий Python, без залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; sans-serif; стрілки через marker; десятковий
роздільник — крапка. Допоміжні функції скопійовано з figs.py розділу (єдиний вигляд).
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREY: "aGrey"}


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


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 2.5.7m.1 — спектр: енергія ↔ довжина хвилі ↔ колір ↔ U_F ─────────────
def fig_spectrum():
    """Лінійка кольорів за енергією фотона. Над лінійкою — приблизне пряме
    падіння U_F (бо qU_F ≈ Eg), під лінійкою — довжина хвилі. Числа орієнтовні
    (реальні матеріали трохи різняться), але співвідношення E=hf=hc/λ точне."""
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Енергія фотона задає і колір, і пряме падіння світлодіода",
              19, INK, "middle", "bold")

    # вісь енергії: 1.6 .. 3.3 еВ зліва направо
    x0, x1 = 70, 810
    ybar_top, ybar_h = 150, 70
    Emin, Emax = 1.55, 3.45

    def ex(E):
        return x0 + (E - Emin) / (Emax - Emin) * (x1 - x0)

    # кольорова смуга (градієнт червоний→фіолетовий за зростанням енергії)
    stops = [
        (1.7, "#cc1f1f"), (1.9, "#e8601c"), (2.05, "#f0a81f"),
        (2.2, "#e9d11a"), (2.35, "#37a437"), (2.55, "#1fa0c8"),
        (2.75, "#1f5fd6"), (3.1, "#6a31c8"),
    ]
    grad = '<linearGradient id="spec" x1="0" y1="0" x2="1" y2="0">\n'
    for E, col in stops:
        off = (E - Emin) / (Emax - Emin) * 100
        grad += f'  <stop offset="{off:.1f}%" stop-color="{col}"/>\n'
    grad += '</linearGradient>\n'
    s += grad
    s += rect(x0, ybar_top, x1 - x0, ybar_h, "url(#spec)", INK, 1.4, 4)

    # шкала енергії знизу від смуги (вісь з поділками)
    yax = ybar_top + ybar_h + 6
    s += line(x0, yax, x1, yax, INK, 1.6)
    for E in [1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4]:
        xx = ex(E)
        s += line(xx, yax, xx, yax + 6, INK, 1.4)
        s += text(xx, yax + 22, f"{E:.1f}", 11.5, INK, "middle")
    s += text(x1 + 4, yax + 5, "E, еВ", 12.5, INK, "start", "bold")
    s += text(x0, yax + 44, "енергія фотона E = h·f  (зростає →)", 12.5, INK, "start")

    # довжина хвилі: λ(нм) = 1240 / E(еВ) — підписи під шкалою
    s += text(x0, yax + 70, "λ = 1240 / E:", 12.5, GREY, "start", "bold")
    for E in [1.7, 2.0, 2.3, 2.7, 3.1]:
        lam = 1240.0 / E
        s += text(ex(E), yax + 70, f"{lam:.0f} нм", 11.5, GREY, "middle")

    # маркери реальних світлодіодів над смугою: (E≈Eg, U_F, назва)
    leds = [
        (1.75, "ІЧ\n~1.4 В", "#7a1010"),
        (1.9,  "черв.\n~1.8 В", "#cc1f1f"),
        (2.1,  "жовт.\n~2.1 В", "#e0a32e"),
        (2.3,  "зел.\n~2.2 В", "#2e9e2e"),
        (2.7,  "син.\n~3.0 В", "#1f5fd6"),
        (3.1,  "УФ\n~3.4 В", "#6a31c8"),
    ]
    for E, lab, col in leds:
        xx = ex(E)
        parts = lab.split("\n")
        s += f'<circle cx="{xx:.1f}" cy="{ybar_top - 4:.1f}" r="4" fill="{col}"/>\n'
        s += text(xx, ybar_top - 90, parts[0], 12, col, "middle", "bold")
        s += text(xx, ybar_top - 74, parts[1], 11, col, "middle")
        s += line(xx, ybar_top - 68, xx, ybar_top - 4, col, 1.4, dash="3,3")

    # пояснення під шкалою
    s += text(W / 2, 338,
              "Маркери над смугою — типові світлодіоди: ширша щілина → синіший колір → більше U_F",
              12.5, GREY, "middle", style="italic")

    # пояснення: qU_F ≈ Eg
    s += text(W / 2, H - 14,
              "Грубе правило: q·U_F ≈ Eg = h·f  →  знаєш колір (λ) — оцінив падіння (U_F ≈ E[еВ] вольтів)",
              13, INK, "middle", "bold")
    save("fig-10-7m-1-photon-spectrum.svg", s)


# ── Рис. 2.5.7m.2 — куди дівається енергія: щілина, фотон, надлишок U_F ────────
def fig_energy_budget():
    """Енергетична діаграма однієї рекомбінації: електрон падає через щілину Eg,
    віддає фотон h·f = Eg. Поряд — стовпчики: теоретична межа U_F = Eg/q проти
    реального U_F (різниця йде на бар'єр контактів і втрати → тепло)."""
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 32, "Куди дівається енергія: фотон бере щілину, решта гріє перехід",
              18, INK, "middle", "bold")

    # ── ліва панель: рівні енергії й перехід електрона ──
    Lx = 70
    s += text(Lx + 120, 70, "Один акт рекомбінації", 14, INK, "middle", "bold")
    c_top, c_bot = 110, 320          # рівень зони провідності / валентної
    band_l, band_r = Lx + 30, Lx + 210
    # зона провідності
    s += rect(band_l, c_top - 22, band_r - band_l, 22, "#e9eefb", BLUE, 1.4, 3)
    s += text(band_l - 6, c_top - 6, "зона провідності", 11.5, BLUE, "end")
    # валентна зона
    s += rect(band_l, c_bot, band_r - band_l, 22, "#fbecec", RED, 1.4, 3)
    s += text(band_l - 6, c_bot + 16, "валентна зона", 11.5, RED, "end")
    # щілина Eg
    s += line(band_r - 30, c_top, band_r - 30, c_bot, GREY, 1.4, dash="4,4")
    s += arrow(band_r - 30, c_top, band_r - 30, c_top + 60, GREY, 1.6)
    s += arrow(band_r - 30, c_bot, band_r - 30, c_bot - 60, GREY, 1.6)
    s += text(band_r - 22, (c_top + c_bot) / 2 - 4, "Eg", 14, INK, "start", "bold")
    s += text(band_r - 22, (c_top + c_bot) / 2 + 14, "щілина", 11, GREY, "start")
    # електрон угорі, дірка внизу, падіння
    ex_e = band_l + 55
    s += f'<circle cx="{ex_e:.1f}" cy="{c_top - 11:.1f}" r="7" fill="{BLUE}"/>\n'
    s += text(ex_e, c_top - 30, "електрон", 11, BLUE, "middle", "bold")
    s += f'<circle cx="{ex_e:.1f}" cy="{c_bot + 11:.1f}" r="7" fill="none" stroke="{RED}" stroke-width="2"/>\n'
    s += text(ex_e, c_bot + 40, "дірка", 11, RED, "middle", "bold")
    s += arrow(ex_e, c_top - 4, ex_e, c_bot + 4, INK, 2.4)
    # фотон, що вилітає
    s += _poly([(ex_e + 12, (c_top + c_bot) / 2 - 18),
                (ex_e + 30, (c_top + c_bot) / 2 - 30),
                (ex_e + 48, (c_top + c_bot) / 2 - 18),
                (ex_e + 66, (c_top + c_bot) / 2 - 30),
                (ex_e + 84, (c_top + c_bot) / 2 - 18)], GREEN, 2.6)
    s += arrow(ex_e + 84, (c_top + c_bot) / 2 - 18, ex_e + 104, (c_top + c_bot) / 2 - 25, GREEN, 2)
    s += text(ex_e + 60, (c_top + c_bot) / 2 - 40, "фотон  h·f = Eg", 12.5, GREEN, "middle", "bold")

    # вертикальний роздільник
    s += line(W / 2 + 20, 80, W / 2 + 20, H - 60, FAINT, 1.4)

    # ── права панель: стовпчики U_F (теорія Eg/q проти реальності) ──
    Rx = W / 2 + 70
    s += text(Rx + 150, 70, "Чому U_F більше за Eg/q", 14, INK, "middle", "bold")
    base = 340
    scale = 70  # пікселів на вольт
    cols = [
        ("червоний", 1.9, "#cc1f1f"),
        ("синій", 3.0, "#1f5fd6"),
    ]
    bw = 70
    gap = 110
    x = Rx + 30
    for name, uf, col in cols:
        eg_v = uf * 0.0   # перерахуємо нижче
        # теоретична межа Eg/q (≈ 0.85·U_F для ілюстрації різниці)
        eg_part = uf - 0.35
        # стовпчик повного U_F
        h_full = uf * scale
        s += rect(x, base - h_full, bw, h_full, "#f3f5f7", col, 1.8, 3)
        # нижня частина = Eg/q
        h_eg = eg_part * scale
        s += rect(x, base - h_eg, bw, h_eg, col, col, 0, 3)
        # підписи
        s += text(x + bw / 2, base + 18, name, 12, INK, "middle", "bold")
        s += text(x + bw / 2, base + 34, f"U_F ≈ {uf:.1f} В", 11.5, INK, "middle")
        s += text(x + bw / 2, base - h_eg + 16, "Eg/q", 11, "#ffffff", "middle", "bold")
        s += text(x + bw / 2, base - h_full - 8, "надлишок", 10.5, GREY, "middle")
        x += bw + gap
    s += line(Rx + 20, base, Rx + 320, base, INK, 1.6)
    s += text(Rx + 20, base + 52,
              "Зафарбоване — енергія, що йде у фотон (Eg).", 11.5, INK, "start")
    s += text(Rx + 20, base + 68,
              "Світле зверху — надлишок на бар'єрах і опорі → тепло.", 11.5, GREY, "start")

    save("fig-10-7m-2-energy-budget.svg", s)


if __name__ == "__main__":
    fig_spectrum()
    fig_energy_budget()
    print("done")
