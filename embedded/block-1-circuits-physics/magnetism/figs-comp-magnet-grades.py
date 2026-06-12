# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки §1.8.3c — «Ферит проти неодиму: класи N35–N52».
ОКРЕМИЙ скрипт вставки (НЕ головний figs.py розділу). Чистий Python, без залежностей.
Вивід → ./img/. Імена SVG — УНІКАЛЬНІ (префікс fig-8-3c-...).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — скрипт самодостатній).
Нумерація підписів — за темою-вставкою: Рис. 1.8.3c.k.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
STEEL = "#6f7d8c"
GOLD = "#c9952b"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.8.3c.1 — енергетична сила: ферит проти класів неодиму ─────────────
def fig_energy_bars():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Скільки поля «запасено»: енергетичний добуток (BH)max", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "вища смужка = сильніший магніт того самого розміру. Одиниця — кДж/м³ (та сама в МГс·Е).",
              12, GREY, "middle", style="italic")

    # осі
    base = 392
    x0 = 90
    full = 300.0          # пікселів на максимум шкали
    vmax = 400.0          # кДж/м³ верх шкали
    s += line(x0, 90, x0, base, INK, 2)
    s += line(x0, base, W - 40, base, INK, 2)
    # сітка
    for v in (100, 200, 300, 400):
        yy = base - full * (v / vmax)
        s += line(x0 - 4, yy, W - 50, yy, FAINT, 1)
        s += text(x0 - 10, yy + 4, str(v), 11, GREY, "end")
    s += text(34, 230, "(BH)max, кДж/м³", 12, GREY, "middle", "bold",)
    # ↑ повернути підпис осі
    s = s.replace('<text x="34.0" y="230.0"',
                  '<text transform="rotate(-90 34 230)" x="34.0" y="230.0"', 1)

    bars = [
        ("Ферит\n(керамічний)", 28, STEEL, "≈ 28"),
        ("N35", 279, GREEN, "≈ 279"),
        ("N42", 334, GREEN, "≈ 334"),
        ("N52", 398, RED, "≈ 398"),
    ]
    bw = 96
    gap = 56
    xx = x0 + 46
    for label, val, col, tag in bars:
        h = full * (val / vmax)
        s += rect(xx, base - h, bw, h, col, INK, 1.8, 4)
        s += text(xx + bw / 2, base - h - 10, tag, 13, INK, "middle", "bold")
        # дворядковий підпис
        for i, ln in enumerate(label.split("\n")):
            s += text(xx + bw / 2, base + 22 + i * 16, ln, 12.5, INK, "middle",
                      "bold" if i == 0 else "normal")
        xx += bw + gap

    # коментар-зноска
    s += rect(x0, 430, W - x0 - 40, 30, "#f1f6ef", GREEN, 1.4, 8)
    s += text((x0 + W - 40) / 2, 450,
              "Число в марці Nxx — це і є приблизно (BH)max у МГс·Е: N52 ≈ 52 МГс·Е ≈ 398 кДж/м³.",
              12, INK, "middle", "bold")
    save("fig-8-3c-1-energy-bars.svg", s)


# ── Рис. 1.8.3c.2 — температурна межа: робоча T і точка Кюрі ──────────────────
def fig_temp_limits():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 34, "Температурна стеля: робоча межа і точка Кюрі", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за робочою межею магніт слабшає (частково оборотно), за точкою Кюрі поле зникає назавжди.",
              12, GREY, "middle", style="italic")

    # шкала температур
    x0, x1 = 120, W - 60
    yA = 150     # ферит
    yB = 250     # неодим N-клас
    yC = 340     # неодим SH-клас
    tmin, tmax = 0.0, 600.0
    span = float(x1 - x0)

    def tx(t):
        return x0 + span * (t / tmax)

    # вісь
    s += line(x0, 390, x1, 390, INK, 2)
    for t in (0, 80, 150, 200, 310, 450, 600):
        s += line(tx(t), 386, tx(t), 394, INK, 1.6)
        s += text(tx(t), 410, f"{t}", 11, GREY, "middle")
    s += text((x0 + x1) / 2, 430, "температура, °C", 12, GREY, "middle", "bold")

    def band(y, name, t_work, t_curie, col):
        # робоча зона: 0..t_work — зелена; t_work..t_curie — жовта; > Кюрі — сіра (зникло)
        s_local = ""
        s_local += text(x0 - 12, y + 5, name, 12.5, INK, "end", "bold")
        h = 26
        s_local += rect(x0, y - h / 2, tx(t_work) - x0, h, "#dff0df", GREEN, 1.4, 4)
        s_local += rect(tx(t_work), y - h / 2, tx(t_curie) - tx(t_work), h, "#fdeccd", GOLD, 1.4, 0)
        s_local += rect(tx(t_curie), y - h / 2, x1 - tx(t_curie), h, "#ececec", GREY, 1.2, 0)
        # маркери
        s_local += line(tx(t_work), y - h / 2 - 8, tx(t_work), y + h / 2 + 8, col, 2, "4 3")
        s_local += text(tx(t_work), y - h / 2 - 12, f"≈{t_work}°C", 11, col, "middle", "bold")
        s_local += line(tx(t_curie), y - h / 2 - 8, tx(t_curie), y + h / 2 + 8, RED, 2)
        s_local += text(tx(t_curie), y + h / 2 + 22, f"Кюрі ≈{t_curie}°C", 11, RED, "middle", "bold")
        return s_local

    s += band(yA, "Ферит", 250, 450, GREEN)
    s += band(yB, "Неодим N", 80, 310, GOLD)
    s += band(yC, "Неодим SH", 150, 340, GOLD)

    # легенда
    lx = x0
    s += rect(lx, 70, 18, 14, "#dff0df", GREEN, 1.2, 3)
    s += text(lx + 24, 82, "робоча зона", 11.5, INK, "start")
    s += rect(lx + 150, 70, 18, 14, "#fdeccd", GOLD, 1.2, 0)
    s += text(lx + 174, 82, "слабшає (втрата сили)", 11.5, INK, "start")
    s += rect(lx + 360, 70, 18, 14, "#ececec", GREY, 1.2, 0)
    s += text(lx + 384, 82, "поля немає (за Кюрі)", 11.5, INK, "start")

    save("fig-8-3c-2-temp-limits.svg", s)


if __name__ == "__main__":
    fig_energy_bars()
    fig_temp_limits()
    print("done")
