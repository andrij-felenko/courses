# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки «Струмові кліщі» (до теми 1.8.8).
НЕ чіпає головний figs.py розділу 8 (за §9 — самодостатній скрипт).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; струм помаранчевий; sans-serif.
Унікальні імена файлів: fig-8-8c-<k>-clamp-*.svg (8 = розділ 8, 8c = вставка до теми 1.8.8).
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
COPPER = "#cf8b5e"
IRON  = "#9aa3ad"
ORANGE = "#e08030"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREEN: "aGreen", ORANGE: "aOrange", BLUE: "aBlue", RED: "aRed"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None, marker=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n'


def arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.4, marker=None, dash=None):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n')


def cur_dot(cx, cy, r=11, color=ORANGE, w=2.6):
    """Струм НА нас (вістря стріли): кружок з крапкою."""
    out = circle(cx, cy, r, "#fff5ec", color, w)
    out += circle(cx, cy, 2.6, color, color, 1)
    return out


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ──────────────────────────────────────────────────────────────────────────────
# Рис. 1.8.8c.1 — два принципи кліщів поряд: трансформатор струму (тільки AC)
#                 та розрив осердя з елементом Холла (AC + DC).
# ──────────────────────────────────────────────────────────────────────────────
def fig_two_principles():
    W, H = 760, 410
    s = header(W, H)
    s += text(W / 2, 30, "Дві щелепи — дві фізики", 19, INK, "middle", "bold")

    # спільна підпис-вісь зверху
    # ── ЛІВА панель: трансформатор струму (CT) ──
    cx, cy, R = 195, 235, 92          # центр і радіус осердя-кільця
    s += text(cx, 66, "Трансформатор струму", 16, INK, "middle", "bold")
    s += text(cx, 86, "тільки AC", 13, GREY, "middle", style="italic")

    # феритове кільце (осердя) — товсте сіре кільце
    s += circle(cx, cy, R, "none", IRON, 18)
    # обмотка-вторинка: кілька витків міді на правій частині кільця (виток = дуга поперек тіла осердя)
    for k in range(6):
        a = math.radians(-32 + k * 14)
        bx, by = cx + R * math.cos(a), cy + R * math.sin(a)
        s += arc(bx, by, 12, 110, 430, COPPER, 2.6)
    s += text(cx + R + 16, cy + 70, "вторинна", 12.5, COPPER, "start")
    s += text(cx + R + 16, cy + 86, "обмотка", 12.5, COPPER, "start")

    # провідник зі струмом крізь центр кільця (на нас)
    s += cur_dot(cx, cy, 13, ORANGE, 2.8)
    s += text(cx, cy - 24, "I (вимірюваний)", 12.5, ORANGE, "middle", "bold")

    # змінне поле в осерді — зелена стрілка по колу
    s += arc(cx, cy, R - 30, -120, 120, GREEN, 2.4, marker=GREEN)
    s += text(cx - R - 6, cy, "B", 14, GREEN, "end", "bold")

    # лінія до приладу
    s += arrow(cx + R + 20, cy + 92, cx + R + 20, cy + 120, COPPER, 2.2)
    s += text(cx + R + 24, cy + 135, "→ I/N (мА) у прилад", 12, INK, "start")

    # роздільник
    s += line(W / 2, 60, W / 2, H - 22, FAINT, 2)

    # ── ПРАВА панель: розрив осердя + елемент Холла (AC+DC) ──
    dx, dy, Rr = 575, 235, 92
    s += text(dx, 66, "Розрив осердя + елемент Холла", 15.5, INK, "middle", "bold")
    s += text(dx, 86, "AC і DC", 13, GREY, "middle", style="italic")

    # осердя з вузьким зазором унизу (від 80° до 100°)
    s += arc(dx, dy, Rr, 100, 440, IRON, 18)  # майже повне кільце з розривом унизу
    # у зазорі — елемент Холла (маленька синя плитка)
    gx, gy = dx, dy + Rr
    s += rect(gx - 14, gy - 9, 28, 18, "#e2e9f7", BLUE, 2.2, rx=2)
    s += text(gx, gy + 34, "елемент Холла", 12, BLUE, "middle", "bold")
    s += text(gx, gy + 49, "(§1.8.8)", 11.5, BLUE, "middle", style="italic")

    # провідник зі струмом крізь центр
    s += cur_dot(dx, dy, 13, ORANGE, 2.8)
    s += text(dx, dy - 24, "I (вимірюваний)", 12.5, ORANGE, "middle", "bold")

    # поле в осерді концентрується в зазорі — зелена стрілка вниз крізь плитку
    s += arc(dx, dy, Rr - 30, 130, 410, GREEN, 2.4, marker=GREEN)
    s += arrow(gx, gy - 32, gx, gy - 14, GREEN, 2.2)  # короткий вектор B у зазор крізь плитку
    s += text(dx - Rr - 6, dy, "B", 14, GREEN, "end", "bold")

    # вихід Холла → напруга
    s += arrow(gx + 18, gy, gx + 70, gy, RED, 2.2)
    s += text(gx + 74, gy - 4, "U_H ∝ B ∝ I", 12.5, RED, "start", "bold")
    s += text(gx + 74, gy + 13, "(є й при DC!)", 11.5, RED, "start")

    return s, W, H


# ──────────────────────────────────────────────────────────────────────────────
# Рис. 1.8.8c.2 — головні граблі: затискати ОДИН провід, не весь кабель.
# ──────────────────────────────────────────────────────────────────────────────
def fig_one_conductor():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 30, "Затискати ОДИН провід, а не кабель", 18, INK, "middle", "bold")

    # ── ЛІВО: весь кабель у щелепах → нуль ──
    cx, cy, R = 200, 170, 70
    s += circle(cx, cy, R, "none", IRON, 14)
    # два проводи: L (на нас, помаранч.) і N (від нас, синій) поряд у центрі
    s += cur_dot(cx - 16, cy, 11, ORANGE, 2.6)
    s += text(cx - 16, cy - 22, "L", 13, ORANGE, "middle", "bold")
    # N — від нас: кружок з хрестиком
    s += circle(cx + 16, cy, 11, "#eef2fb", BLUE, 2.6)
    s += line(cx + 16 - 7, cy - 7, cx + 16 + 7, cy + 7, BLUE, 2.4)
    s += line(cx + 16 - 7, cy + 7, cx + 16 + 7, cy - 7, BLUE, 2.4)
    s += text(cx + 16, cy - 22, "N", 13, BLUE, "middle", "bold")
    s += text(cx, cy + R + 28, "L і N разом", 13.5, INK, "middle")
    s += text(cx, cy + R + 48, "поля гасяться → читання ≈ 0", 13, RED, "middle", "bold")

    # роздільник
    s += line(W / 2, 56, W / 2, H - 18, FAINT, 2)

    # ── ПРАВО: один провід → правильно ──
    dx, dy = 560, 170
    s += circle(dx, dy, R, "none", IRON, 14)
    s += cur_dot(dx, dy, 12, ORANGE, 2.8)
    s += text(dx, dy - 24, "лише L", 13, ORANGE, "middle", "bold")
    # поле по колу — є
    s += arc(dx, dy, R - 22, -120, 120, GREEN, 2.4, marker=GREEN)
    s += text(dx, dy + R + 28, "один провід", 13.5, INK, "middle")
    s += text(dx, dy + R + 48, "поле є → читаємо струм", 13, GREEN, "middle", "bold")

    return s, W, H


if __name__ == "__main__":
    s, w, h = fig_two_principles()
    save("fig-8-8c-1-clamp-principles.svg", s)
    s, w, h = fig_one_conductor()
    save("fig-8-8c-2-clamp-one-conductor.svg", s)
    print("done")
