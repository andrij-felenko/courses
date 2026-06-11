# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 7 — «Змінний струм: синусоїда, фаза й RMS» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація: історія до розділу — секція 0 (Рис. 7.0.N); теми — Рис. 7.M.k.
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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange"}


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


def _resistor(x, y, w=70, h=24, label="R"):
    out = rect(x, y - h / 2, w, h, "#fff", INK, 2, 3)
    if label:
        out += text(x + w / 2, y - h / 2 - 8, label, 12.5, INK, "middle", "bold", "italic")
    return out


# ── допоміжне для історії: дугова стрілка (поворот) ───────────────────────────
def _arc_arrow(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.4):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def _sine_path(x0, y0, width, amp, cycles=1.0, phase=0.0, n=120):
    """Полілінія синусоїди: вісь по y0, амплітуда amp (вгору додатна), width пікселів на cycles періодів."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * width
        y = y0 - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((x, y))
    return pts


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 7 — Штейнмец і математика змінного струму.  Рис. 7.0.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 7.0.1 — «до» і «після» Штейнмеца ────────────────────────────────────
def fig_before_after():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 30, "Те саме коло двома мовами: нестерпні рівняння — і проста алгебра",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "Штейнмец показав, як перекласти задачу зі змінним струмом із диференціальних рівнянь на комплексні числа",
              11, GREY, "middle", style="italic")

    # ── ЛІВА панель: «до» — жмут синусів зі зсувами фаз + страшні рівняння ──
    s += rect(40, 74, 400, 322, "#fdecea", RED, 1.8, 12)
    s += text(240, 100, "ДО: синуси, зсунуті по фазі", 13.5, RED, "middle", "bold")
    ax, ay, aw = 80, 175, 320
    s += line(ax, ay, ax + aw, ay, GREY, 1.4)          # вісь часу
    s += line(ax, ay - 52, ax, ay + 52, GREY, 1.4)      # вісь
    s += text(ax + aw + 4, ay + 4, "t", 11, GREY, "start", "bold", "italic")
    s += polyline(_sine_path(ax, ay, aw, 42, 2.0, 0.0), RED, 2.4)
    s += polyline(_sine_path(ax, ay, aw, 36, 2.0, 1.9), BLUE, 2.4)
    s += polyline(_sine_path(ax, ay, aw, 30, 2.0, 3.5), GREEN, 2.4, "5,3")
    s += text(ax + 6, ay - 60, "напруга", 9.5, RED, "start", "bold")
    s += text(ax + 96, ay - 60, "струм (зсунутий)", 9.5, BLUE, "start", "bold")
    # «страшна» математика
    s += rect(72, 250, 336, 120, "#ffffff", "#e0a9a4", 1.4, 8)
    s += text(240, 274, "доводиться розв'язувати:", 10.5, GREY, "middle", style="italic")
    s += text(240, 302, "L·di/dt + R·i + (1/C)∫i dt = v(t)", 14, INK, "middle", "bold")
    s += text(240, 330, "v = Vm·sin(ωt),  i = Im·sin(ωt − φ)", 12, INK, "middle")
    s += text(240, 356, "тригонометрія + диф. рівняння для КОЖНОГО кола",
              10, RED, "middle", "bold")

    # ── стрілка-перехід ──
    s += arrow(448, 235, 492, 235, GREEN, 3.2)
    s += text(470, 224, "переклад", 10, GREEN, "middle", "bold")
    s += text(470, 258, "j", 13, GREEN, "middle", "bold", "italic")

    # ── ПРАВА панель: «після» — комплексні стрілки на площині ──
    s += rect(500, 74, 360, 322, "#eef7f0", GREEN, 1.8, 12)
    s += text(680, 100, "ПІСЛЯ: комплексні стрілки", 13.5, GREEN, "middle", "bold")
    cx, cy = 680, 235
    # осі re/im
    s += arrow(cx - 130, cy, cx + 130, cy, GREY, 1.4)
    s += arrow(cx, cy + 110, cx, cy - 110, GREY, 1.4)
    s += text(cx + 128, cy + 18, "Re", 10.5, GREY, "middle", "bold")
    s += text(cx + 20, cy - 104, "Im", 10.5, GREY, "middle", "bold")
    # фазори
    s += arrow(cx, cy, cx + 96, cy - 18, RED, 2.8)
    s += text(cx + 104, cy - 22, "V", 13, RED, "start", "bold", "italic")
    s += arrow(cx, cy, cx + 52, cy - 74, BLUE, 2.8)
    s += text(cx + 54, cy - 80, "I", 13, BLUE, "start", "bold", "italic")
    # дуга кута φ між ними
    s += _arc_arrow(cx, cy, 42, -10.6, -54.9, GREEN, 1.8)
    s += text(cx + 60, cy - 44, "φ", 12, GREEN, "start", "bold", "italic")
    s += rect(540, 320, 280, 50, "#ffffff", "#a9d4b5", 1.4, 8)
    s += text(680, 342, "зсув фаз = кут між стрілками", 10.5, INK, "middle", "bold")
    s += text(680, 360, "додавання й ділення — проста алгебра", 10.5, GREEN, "middle", "bold")

    s += text(W / 2, 416, "Замість рівняння на кожне коло — арифметика стрілок на площині. Ось чим Штейнмец полегшив життя інженерам.",
              11, INK, "middle", "bold")
    save("fig-7-0-1-before-after.svg", s)


# ── Рис. 7.0.2 — фазор: синусоїда як проєкція обертового вектора ──────────────
def fig_phasor():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 30, "Фазор: синусоїда — це тінь вектора, що обертається",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "обертовий вектор на комплексній площині, а збоку — його проєкція в часі (саме та синусоїда)",
              11, GREY, "middle", style="italic")

    # ── ліворуч: коло з обертовим вектором ──
    cx, cy, R = 200, 215, 110
    s += circle(cx, cy, R, "none", FAINT, 1.6)
    s += arrow(cx - R - 24, cy, cx + R + 28, cy, GREY, 1.4)      # Re
    s += arrow(cx, cy + R + 26, cx, cy - R - 28, GREY, 1.4)      # Im
    s += text(cx + R + 26, cy + 18, "Re", 10.5, GREY, "middle", "bold")
    s += text(cx + 20, cy - R - 22, "Im", 10.5, GREY, "middle", "bold")
    ang = math.radians(38)
    vx, vy = cx + R * math.cos(ang), cy - R * math.sin(ang)
    s += arrow(cx, cy, vx, vy, RED, 3.0)
    s += text((cx + vx) / 2 - 6, (cy + vy) / 2 - 8, "Vm", 12.5, RED, "middle", "bold", "italic")
    # кут ωt
    s += _arc_arrow(cx, cy, 36, 0, -38, GREEN, 1.8)
    s += text(cx + 46, cy - 16, "ωt", 11.5, GREEN, "start", "bold", "italic")
    # проєкція на Im (пунктир)
    s += line(vx, vy, cx, vy, BLUE, 1.6, "4,3")
    s += circle(cx, vy, 3.5, BLUE, BLUE, 1)
    s += text(cx - 8, vy - 6, "проєкція", 9.5, BLUE, "end", "bold")
    s += text(cx, cy + R + 50, "вектор обертається зі швидкістю ω", 10.5, INK, "middle", "bold")
    s += text(cx, cy + R + 68, "обертання на 90° = множення на j", 10, GREEN, "middle", style="italic")

    # ── праворуч: розгортка в часі (синусоїда) ──
    ax, ay, aw = 410, 215, 420
    s += arrow(ax, ay, ax + aw + 10, ay, GREY, 1.4)
    s += arrow(ax, ay + R + 12, ax, ay - R - 12, GREY, 1.4)
    s += text(ax + aw + 8, ay + 18, "t", 11, GREY, "middle", "bold", "italic")
    s += text(ax - 10, ay - R - 8, "v(t)", 10.5, GREY, "end", "bold")
    s += polyline(_sine_path(ax, ay, aw, R, 1.6, 0.0), RED, 2.8)
    # горизонтальна нитка від проєкції до старту синуса
    s += line(cx, vy, ax, vy, BLUE, 1.4, "4,3")
    s += circle(ax, vy, 3.5, BLUE, BLUE, 1)
    # рівень амплітуди
    s += line(ax, ay - R, ax + aw, ay - R, FAINT, 1.2, "3,3")
    s += text(ax + aw - 4, ay - R - 4, "Vm", 10, RED, "end", "bold", "italic")
    s += text(ax + aw / 2, ay + R + 36, "та сама величина, розгорнута в часі: v(t) = Vm·sin(ωt)",
              11, INK, "middle", "bold")
    save("fig-7-0-2-phasor.svg", s)


# ── Рис. 7.0.3 — колективний внесок: не міф про одного генія ──────────────────
def fig_collective():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 30, "Метод фазорів — праця багатьох, а не винахід одинака",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "Штейнмец СИСТЕМАТИЗУВАВ і навчив покоління; математика й паралельні внески — чужі",
              11, GREY, "middle", style="italic")

    # фундамент: математика
    s += rect(70, 92, 760, 56, "#eef2fb", BLUE, 1.6, 10)
    s += text(W / 2, 114, "Фундамент — математика комплексних чисел",
              12.5, BLUE, "middle", "bold")
    s += text(W / 2, 134, "формула Ейлера (Леонард Ейлер) · комплексна площина (Ґаусс, Арґан)",
              11, INK, "middle")
    s += arrow(W / 2, 150, W / 2, 176, GREY, 2.2)

    # паралельні сучасники
    peers = [("Олівер Гевісайд", "операційне числення", 200),
             ("Артур Кеннеллі", "комплексний імпеданс, 1893 (незалежно)", 470),
             ("Майкл Пупин", "аналіз кіл змінного струму", 740)]
    for name, note, xc in peers:
        s += rect(xc - 125, 184, 250, 56, "#f6f8fc", GREY, 1.5, 9)
        s += text(xc, 206, name, 11.5, INK, "middle", "bold")
        s += text(xc, 224, note, 9.3, GREY, "middle")
        s += arrow(xc, 242, xc if xc == 470 else (xc + (470 - xc) * 0.18), 274, GREY, 1.6)

    # Штейнмец: систематизатор
    s += rect(250, 278, 400, 60, "#eef7f0", GREEN, 2.0, 12)
    s += text(W / 2, 301, "Штейнмец (1893, AIEE): звів усе в стандартний метод",
              12.5, GREEN, "middle", "bold")
    s += text(W / 2, 322, "імпеданс як комплексна величина · підручник 1897 · «навчив покоління»",
              10.3, INK, "middle")
    save("fig-7-0-3-collective.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.7.1 — Чому синусоїда: природна форма коливань.  Рис. 7.1.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 7.1.1 — обертання по колу → проєкція дає синус ───────────────────────
def fig_circle_to_sine():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 28, "Звідки береться синус: проєкція рівномірного руху по колу",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "точка біжить колом зі сталою швидкістю; її «тінь» на вертикальній осі гойдається саме синусоїдою",
              11, GREY, "middle", style="italic")

    # ── ліворуч: коло з рухомою точкою ──
    cx, cy, R = 195, 215, 120
    s += circle(cx, cy, R, "none", FAINT, 1.8)
    s += line(cx - R - 28, cy, cx + R + 30, cy, GREY, 1.3)        # горизонт
    s += arrow(cx, cy + R + 30, cx, cy - R - 34, GREY, 1.4)       # вертикальна вісь
    s += text(cx + 16, cy - R - 26, "y", 12, GREY, "middle", "bold", "italic")
    ang = math.radians(40)
    px, py = cx + R * math.cos(ang), cy - R * math.sin(ang)
    s += arrow(cx, cy, px, py, RED, 3.0)                          # радіус-вектор
    s += text((cx + px) / 2 - 12, (cy + py) / 2 - 8, "Vm", 13, RED, "middle", "bold", "italic")
    s += circle(px, py, 4.5, RED, RED, 1)
    s += _arc_arrow(cx, cy, 40, 0, -40, GREEN, 1.8)
    s += text(cx + 50, cy - 18, "ωt", 12, GREEN, "start", "bold", "italic")
    # проєкція на вертикальну вісь
    s += line(px, py, cx, py, BLUE, 1.6, "4,3")
    s += circle(cx, py, 4.5, BLUE, BLUE, 1)
    s += text(cx - 10, py - 6, "y = Vm·sin(ωt)", 10.5, BLUE, "end", "bold")
    s += text(cx, cy + R + 54, "висота точки над горизонтом", 10.5, INK, "middle", "bold")

    # ── праворуч: розгортка цієї висоти в часі ──
    ax, ay, aw = 400, 215, 470
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.4)
    s += arrow(ax, ay + R + 14, ax, ay - R - 14, GREY, 1.4)
    s += text(ax + aw + 8, ay + 18, "t", 12, GREY, "middle", "bold", "italic")
    s += text(ax - 8, ay - R - 8, "y", 11, GREY, "end", "bold", "italic")
    s += polyline(_sine_path(ax, ay, aw, R, 1.6, 0.0), RED, 2.8)
    # нитка від проєкції до старту синуса + поточна точка на хвилі
    s += line(cx, py, ax, py, BLUE, 1.3, "4,3")
    s += circle(ax, py, 4.5, BLUE, BLUE, 1)
    # амплітудні рівні
    s += line(ax, ay - R, ax + aw, ay - R, FAINT, 1.2, "3,3")
    s += line(ax, ay + R, ax + aw, ay + R, FAINT, 1.2, "3,3")
    s += text(ax + aw - 4, ay - R - 5, "+Vm", 10, RED, "end", "bold", "italic")
    s += text(ax + aw - 4, ay + R + 14, "−Vm", 10, BLUE, "end", "bold", "italic")
    s += text(ax + aw / 2, ay + R + 54, "та сама висота, розгорнута в часі — це і є синусоїда",
              11, INK, "middle", "bold")
    save("fig-7-1-1-circle-to-sine.svg", s)


# ── Рис. 7.1.2 — повертальна сила: маса-пружина й маятник ─────────────────────
def fig_restoring_force():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 28, "Спільний механізм коливань: сила тягне назад, до рівноваги",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "що далі відхилення, то сильніше тягне назад — і саме лінійний зв'язок F = −k·x народжує синус",
              11, GREY, "middle", style="italic")

    # ── ліворуч: маса на пружині ──
    wall = 70
    s += rect(wall, 110, 16, 170, "#d9d9d9", INK, 1.5)            # стіна
    s += line(wall, 110, wall + 16, 110, INK, 1.2)
    eqx = 250                                                     # положення рівноваги
    mx = 320                                                      # зміщена маса (x > 0)
    my = 195
    # пружина (зигзаг) від стіни до маси
    n = 9
    sx0, sx1 = wall + 16, mx - 26
    zz = [(sx0, my)]
    for i in range(1, n):
        xx = sx0 + (sx1 - sx0) * i / n
        zz.append((xx, my + (14 if i % 2 else -14)))
    zz.append((sx1, my))
    s += polyline(zz, INK, 2.0)
    s += rect(mx - 26, my - 26, 52, 52, "#eef2fb", BLUE, 2.0, 4)  # маса
    s += text(mx, my + 5, "m", 15, BLUE, "middle", "bold", "italic")
    # лінія рівноваги
    s += line(eqx, 120, eqx, 290, GREEN, 1.6, "5,4")
    s += text(eqx, 308, "рівновага", 10.5, GREEN, "middle", "bold")
    s += text(eqx, 322, "(x = 0)", 9.5, GREEN, "middle")
    # відхилення x
    s += arrow(eqx, 150, mx - 26, 150, GREY, 1.6)
    s += text((eqx + mx) / 2, 142, "x", 12, INK, "middle", "bold", "italic")
    # повертальна сила (назад до рівноваги)
    s += arrow(mx, my, mx - 70, my, RED, 3.2)
    s += text(mx - 36, my - 14, "F = −k·x", 12.5, RED, "middle", "bold", "italic")
    s += text(180, 350, "Пружина: F = −k·x  →  a = −(k/m)·x", 12, INK, "middle", "bold")
    s += text(180, 372, "ω = √(k/m)", 12.5, GREEN, "middle", "bold", "italic")

    # ── праворуч: маятник ──
    px, py = 670, 108                                            # точка підвісу
    L = 150
    th = math.radians(26)
    bx, by = px + L * math.sin(th), py + L * math.cos(th)
    s += line(px - 60, py, px + 60, py, INK, 2.0)                # стеля
    s += line(px, py, bx, by, INK, 2.0)                          # нитка
    s += circle(bx, by, 20, "#eef2fb", BLUE, 2.0)               # тягарець
    # вертикаль рівноваги
    s += line(px, py, px, py + L + 24, GREEN, 1.4, "5,4")
    s += circle(px, py + L, 3.0, GREEN, GREEN, 1)
    s += text(px, py + L + 40, "рівновага", 10.5, GREEN, "middle", "bold")
    # кут θ
    s += _arc_arrow(px, py, 44, 90, 90 - 26, GREEN, 1.6)
    s += text(px + 30, py + 52, "θ", 12, GREEN, "start", "bold", "italic")
    # повертальна сила вздовж дуги, до рівноваги
    tx, ty = bx - 56 * math.cos(th), by + 56 * math.sin(th)
    s += arrow(bx, by, tx, ty, RED, 3.0)
    s += text(bx + 6, by + 34, "тягне назад", 10, RED, "start", "bold")
    s += text(px, 350, "Маятник (малі кути): F ∝ −θ", 12, INK, "middle", "bold")
    s += text(px, 372, "ω = √(g/L)", 12.5, GREEN, "middle", "bold", "italic")
    save("fig-7-1-2-restoring-force.svg", s)


# ── Рис. 7.1.3 — інтуїція d²x/dt² = −ω²·x: кривина ∝ −відхилення ───────────────
def fig_curvature():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 28, "Чому виходить саме синус: кривина графіка ∝ мінус відхилення",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "прискорення (вигин кривої) завжди напрямлене до осі й тим більше, чим далі ми від неї — лише синус так уміє",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 80, 180, 760
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.4)
    s += arrow(ax, ay + 120, ax, ay - 120, GREY, 1.4)
    s += text(ax + aw + 8, ay + 18, "t", 12, GREY, "middle", "bold", "italic")
    s += text(ax - 8, ay - 108, "x", 11, GREY, "end", "bold", "italic")
    amp = 92
    pts = _sine_path(ax, ay, aw, amp, 1.5, 0.0)
    s += polyline(pts, INK, 2.8)

    # позначити: на гребені — вигин униз (прискорення вниз), у западині — вгору
    def at(frac):
        i = int(frac * (len(pts) - 1))
        return pts[i]
    # гребінь (максимум, x>0): сила/вигин униз
    gx, gy = at(1.0 / 6.0)
    s += arrow(gx, gy + 6, gx, gy + 64, RED, 3.0)
    s += text(gx, gy - 10, "x максимальне", 10, INK, "middle", "bold")
    s += text(gx + 8, gy + 46, "вигин ↓ (a < 0)", 10, RED, "start", "bold")
    # западина (мінімум, x<0): сила/вигин угору
    vx, vy = at(0.5)
    s += arrow(vx, vy - 6, vx, vy - 64, BLUE, 3.0)
    s += text(vx, vy + 22, "x мінімальне", 10, INK, "middle", "bold")
    s += text(vx + 8, vy - 46, "вигин ↑ (a > 0)", 10, BLUE, "start", "bold")
    # перетин осі (x=0): кривина нульова, найшвидший рух
    zx, zy = at(1.0 / 3.0)
    s += circle(zx, zy, 4.0, GREEN, GREEN, 1)
    s += text(zx, zy - 14, "x = 0: прямо (a = 0)", 9.5, GREEN, "middle", "bold")

    s += rect(280, 300, 340, 44, "#eef7f0", GREEN, 1.6, 9)
    s += text(W / 2, 327, "d²x/dt² = −ω²·x   →   x(t) = Vm·sin(ωt + φ)",
              13.5, GREEN, "middle", "bold")
    save("fig-7-1-3-curvature.svg", s)


# ── Рис. 7.1.4 — генератор: виток у полі → потік-косинус, ЕРС-синус ───────────
def fig_generator():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 28, "Чому мережа синусоїдна: виток, що обертається в магнітному полі",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "потік крізь рамку міняється як косинус кута; наведена ЕРС — швидкість його зміни, тобто синус",
              11, GREY, "middle", style="italic")

    # ── ліворуч: магніт + рамка, що обертається ──
    bx0 = 70
    s += rect(bx0, 120, 40, 180, "#fdecea", RED, 1.8, 4)         # N
    s += text(bx0 + 20, 218, "N", 18, RED, "middle", "bold")
    s += rect(bx0 + 250, 120, 40, 180, "#eef2fb", BLUE, 1.8, 4)  # S
    s += text(bx0 + 270, 218, "S", 18, BLUE, "middle", "bold")
    # лінії поля B зліва направо
    for yy in (150, 185, 220, 255, 290):
        s += arrow(bx0 + 44, yy, bx0 + 246, yy, GREEN, 1.4)
    s += text(bx0 + 145, 112, "B", 12, GREEN, "middle", "bold", "italic")
    # рамка під кутом (еліпс натяком: дві сторони + вісь)
    fcx, fcy = bx0 + 145, 210
    s += line(fcx, fcy - 70, fcx, fcy + 70, GREY, 1.4, "4,3")   # вісь обертання
    fa = math.radians(35)
    w2 = 58
    x1, x2 = fcx - w2 * math.cos(fa), fcx + w2 * math.cos(fa)
    s += line(x1, fcy - 70, x1, fcy + 70, COPPER, 3.0)
    s += line(x2, fcy - 70, x2, fcy + 70, COPPER, 3.0)
    s += line(x1, fcy - 70, x2, fcy - 70, COPPER, 2.4)
    s += line(x1, fcy + 70, x2, fcy + 70, COPPER, 2.4)
    s += _arc_arrow(fcx, fcy, 86, -20, 40, INK, 1.8)
    s += text(fcx + 80, fcy - 70, "обертання", 10, INK, "start", "bold")
    s += text(fcx, 326, "рамка крутиться → кут θ = ωt", 10.5, INK, "middle", "bold")

    # ── праворуч: два графіки — потік (косинус) і ЕРС (синус) ──
    ax, ay, aw = 470, 150, 400
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.3)
    s += arrow(ax, ay + 64, ax, ay - 64, GREY, 1.3)
    s += text(ax + aw + 8, ay + 16, "t", 11, GREY, "middle", "bold", "italic")
    s += polyline(_sine_path(ax, ay, aw, 50, 1.0, math.pi / 2), GREEN, 2.6)  # косинус
    s += text(ax + 8, ay - 52, "потік Φ = Φm·cos(ωt)", 10.5, GREEN, "start", "bold")

    ay2 = ay + 150
    s += arrow(ax, ay2, ax + aw + 12, ay2, GREY, 1.3)
    s += arrow(ax, ay2 + 64, ax, ay2 - 64, GREY, 1.3)
    s += text(ax + aw + 8, ay2 + 16, "t", 11, GREY, "middle", "bold", "italic")
    s += polyline(_sine_path(ax, ay2, aw, 50, 1.0, 0.0), RED, 2.8)           # синус
    s += text(ax + 8, ay2 - 52, "ЕРС = −dΦ/dt = Vm·sin(ωt)", 10.5, RED, "start", "bold")
    # стрілка «похідна»
    s += arrow(ax + aw / 2, ay + 70, ax + aw / 2, ay2 - 70, INK, 2.2)
    s += text(ax + aw / 2 + 8, (ay + ay2) / 2, "швидкість зміни", 10, INK, "start", "bold")
    save("fig-7-1-4-generator.svg", s)


# ── Рис. 7.1.5 — синус лишається синусом крізь R/L/C, меандр спотворюється ────
def fig_shape_preserved():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 28, "Головна причина: у лінійному колі синус лишається синусом",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "елементи R, L, C диференціюють та інтегрують — а похідна й інтеграл синуса знову синус (тих самих ω)",
              11, GREY, "middle", style="italic")

    # ── верхній рядок: синус → коло → синус (інша амплітуда/фаза) ──
    def mini_axis(x, y, w):
        out = line(x, y, x + w, y, GREY, 1.2)
        return out

    yA = 150
    s += text(120, 96, "СИНУС", 13, GREEN, "middle", "bold")
    s += mini_axis(40, yA, 160)
    s += polyline(_sine_path(40, yA, 160, 40, 1.3, 0.0), RED, 2.6)
    s += text(120, yA + 56, "на вході", 10, INK, "middle")
    # блок R L C
    s += rect(235, yA - 42, 120, 84, "#eef7f0", GREEN, 1.8, 8)
    s += text(295, yA - 6, "R · L · C", 14, GREEN, "middle", "bold", "italic")
    s += text(295, yA + 16, "(лінійне коло)", 10, INK, "middle")
    s += arrow(205, yA, 233, yA, INK, 2.4)
    s += arrow(357, yA, 388, yA, INK, 2.4)
    s += mini_axis(395, yA, 175)
    # вихід: той самий синус, менша амплітуда + зсув фази
    s += polyline(_sine_path(395, yA, 175, 28, 1.3, 0.7), RED, 2.6)
    s += polyline(_sine_path(395, yA, 175, 40, 1.3, 0.0), FAINT, 1.6, "4,3")
    s += text(482, yA + 56, "ТОЙ САМИЙ синус:", 10.5, GREEN, "middle", "bold")
    s += text(482, yA + 72, "інші амплітуда й фаза", 9.5, INK, "middle")
    s += text(700, yA, "✓  форма збережена", 13, GREEN, "start", "bold")

    s += line(40, 250, 880, 250, FAINT, 1.4)

    # ── нижній рядок: меандр → коло → спотворений (RC-заряд/розряд) ──
    yB = 350
    s += text(120, 296, "МЕАНДР", 13, RED, "middle", "bold")
    # прямокутна хвиля на вході
    sq = []
    x0, w0, hi, lo = 40, 160, yB - 36, yB + 36
    seg = w0 / 4.0
    lvl = hi
    sq.append((x0, lvl))
    for k in range(4):
        sq.append((x0 + k * seg, lvl))
        lvl = lo if lvl == hi else hi
        sq.append((x0 + k * seg, lvl))
    sq.append((x0 + w0, lvl))
    s += polyline(sq, BLUE, 2.6)
    s += text(120, yB + 58, "на вході", 10, INK, "middle")
    s += rect(235, yB - 42, 120, 84, "#eef2fb", BLUE, 1.8, 8)
    s += text(295, yB - 6, "R · L · C", 14, BLUE, "middle", "bold", "italic")
    s += text(295, yB + 16, "(те саме коло)", 10, INK, "middle")
    s += arrow(205, yB, 233, yB, INK, 2.4)
    s += arrow(357, yB, 388, yB, INK, 2.4)
    # вихід: спотворений — експоненційні заряди/розряди
    dist = [(395, yB + 30)]
    xx = 395
    segp = 175 / 4.0
    up = True
    for k in range(4):
        x_start = 395 + k * segp
        for j in range(13):
            t = j / 12.0
            x = x_start + t * segp
            if up:
                y = (yB + 30) - 60 * (1 - math.exp(-3 * t))
            else:
                y = (yB - 30) + 60 * (1 - math.exp(-3 * t))
            dist.append((x, y))
        up = not up
    s += polyline(dist, ORANGE, 2.6)
    s += text(482, yB + 58, "СПОТВОРЕНИЙ:", 10.5, RED, "middle", "bold")
    s += text(482, yB + 74, "вже не меандр", 9.5, INK, "middle")
    s += text(700, yB, "✗  форма змінилась", 13, RED, "start", "bold")
    save("fig-7-1-5-shape-preserved.svg", s)


# ── Рис. 7.1.6 — Фур'є: меандр = основна + 3-тя + 5-та… гармоніки ─────────────
def fig_fourier():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 28, "Синус як цеглинка: будь-який періодичний сигнал — це сума синусів",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "меандр складається з основної частоти та непарних гармонік (3-ї, 5-ї, 7-ї…) — що більше їх, то ближче до прямокутника",
              11, GREY, "middle", style="italic")

    # ── ліворуч: окремі гармоніки ──
    ax, aw = 70, 300
    rows = [("основна (f)", 1, 70, RED, 1.0),
            ("+ 3-тя (3f)", 3, 150, BLUE, 1.0 / 3.0),
            ("+ 5-та (5f)", 5, 230, GREEN, 1.0 / 5.0),
            ("+ 7-ма (7f)", 7, 310, ORANGE, 1.0 / 7.0)]
    for label, mult, yy, col, amp in rows:
        s += line(ax, yy, ax + aw, yy, GREY, 1.1)
        s += polyline(_sine_path(ax, yy, aw, 28 * amp + 6, mult, 0.0), col, 2.2)
        s += text(ax - 6, yy + 4, label, 10.5, col, "end", "bold")
    s += text(ax + aw / 2, 350, "кожна гармоніка — чистий синус", 10.5, INK, "middle", "bold")
    s += text(ax + aw / 2, 368, "амплітуди спадають: 1, 1/3, 1/5, 1/7 …", 9.5, GREY, "middle")

    # ── стрілка «сума» ──
    s += arrow(395, 190, 445, 190, INK, 3.0)
    s += text(420, 178, "Σ", 17, INK, "middle", "bold")
    s += text(420, 208, "сума", 9.5, INK, "middle", "bold")

    # ── праворуч: часткові суми наближаються до меандру ──
    bx, bw = 470, 380
    by = 190
    # ідеальний меандр (ціль) — блідий
    sq = []
    seg = bw / 4.0
    lvl = by - 70
    sq.append((bx, lvl))
    for k in range(4):
        sq.append((bx + k * seg, lvl))
        lvl = (by + 70) if lvl == (by - 70) else (by - 70)
        sq.append((bx + k * seg, lvl))
    sq.append((bx + bw, lvl))
    s += polyline(sq, FAINT, 2.0, "5,4")
    s += text(bx + bw, by - 84, "ціль: меандр", 10, GREY, "end", "bold")

    # часткова сума 1+3+5+7 (нормована)
    pts = []
    N = 260
    for i in range(N + 1):
        t = i / N
        val = 0.0
        for m, a in ((1, 1.0), (3, 1.0 / 3.0), (5, 1.0 / 5.0), (7, 1.0 / 7.0)):
            val += a * math.sin(2 * math.pi * m * t)
        x = bx + t * bw
        y = by - 70 * (val / (4.0 / math.pi)) * 0.82
        pts.append((x, y))
    s += polyline(pts, RED, 2.8)
    s += text(bx + bw / 2, 350, "основна + 3 + 5 + 7 гармоніки", 10.5, RED, "middle", "bold")
    s += text(bx + bw / 2, 368, "вже схоже на прямокутник — і тим точніше, чим більше доданків", 9.5, INK, "middle")
    save("fig-7-1-6-fourier.svg", s)


# ── Рис. 7.1.7 — синус із позначеними Vm, T і зв'язком ω = 2πf ────────────────
def fig_sine_anatomy():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 28, "Анатомія синусоїди: амплітуда Vm, період T і кутова частота ω",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 50, "одна хвиля несе все: висоту (Vm), тривалість циклу (T) та швидкість обертання вектора (ω = 2πf)",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 90, 195, 700
    amp = 95
    s += arrow(ax, ay, ax + aw + 14, ay, GREY, 1.4)
    s += arrow(ax, ay + 130, ax, ay - 130, GREY, 1.4)
    s += text(ax + aw + 10, ay + 18, "t", 12, GREY, "middle", "bold", "italic")
    s += text(ax - 8, ay - 118, "v", 12, GREY, "end", "bold", "italic")
    s += polyline(_sine_path(ax, ay, aw, amp, 2.0, 0.0), RED, 2.9)

    # рівень амплітуди
    s += line(ax, ay - amp, ax + aw, ay - amp, FAINT, 1.2, "3,3")
    s += line(ax, ay + amp, ax + aw, ay + amp, FAINT, 1.2, "3,3")
    # стрілка Vm від осі до піка (перший гребінь при чверті періоду одного циклу)
    quarter = aw / 8.0   # 2 цикли на aw → чверть циклу = aw/8
    s += arrow(ax + quarter, ay, ax + quarter, ay - amp, BLUE, 2.4)
    s += text(ax + quarter + 8, ay - amp / 2, "Vm", 13, BLUE, "start", "bold", "italic")
    s += text(ax + aw - 4, ay - amp - 6, "+Vm", 10, RED, "end", "bold", "italic")
    s += text(ax + aw - 4, ay + amp + 16, "−Vm", 10, RED, "end", "bold", "italic")

    # період T: один повний цикл = aw/2
    period = aw / 2.0
    ty = ay + amp + 30
    s += arrow(ax, ty, ax + period, ty, GREEN, 2.2)
    s += arrow(ax + period, ty, ax, ty, GREEN, 2.2)
    s += line(ax, ay, ax, ty + 8, GREEN, 1.2, "3,3")
    s += line(ax + period, ay, ax + period, ty + 8, GREEN, 1.2, "3,3")
    s += text(ax + period / 2, ty + 20, "період T (один повний цикл)", 11, GREEN, "middle", "bold")

    # формульний блок
    s += rect(255, 320, 390, 44, "#eef2fb", BLUE, 1.6, 9)
    s += text(W / 2, 347, "f = 1/T      ω = 2π·f      v(t) = Vm·sin(2π·f·t + φ)",
              13, INK, "middle", "bold")
    save("fig-7-1-7-sine-anatomy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.7.2 — Амплітуда, період, частота.  Рис. 7.2.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 7.2.1 — три способи назвати «висоту»: Vm, Vpp, миттєве v(t) ──────────
def fig_amplitude_kinds():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 28, "Три «висоти» синусоїди: амплітуда, розмах і миттєве значення",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "Vm — від осі до піка; Vpp — від низу до верху (удвічі більше); v(t) — значення в конкретну мить",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 120, 200, 640
    amp = 110
    s += arrow(ax - 30, ay, ax + aw + 14, ay, GREY, 1.4)
    s += arrow(ax, ay + 140, ax, ay - 140, GREY, 1.4)
    s += text(ax + aw + 10, ay + 18, "t", 12, GREY, "middle", "bold", "italic")
    s += text(ax - 36, ay - 128, "v", 12, GREY, "middle", "bold", "italic")
    s += polyline(_sine_path(ax, ay, aw, amp, 1.6, 0.0), RED, 2.9)

    # рівні піків
    s += line(ax, ay - amp, ax + aw, ay - amp, FAINT, 1.2, "3,3")
    s += line(ax, ay + amp, ax + aw, ay + amp, FAINT, 1.2, "3,3")
    s += text(ax - 36, ay - amp + 4, "+Vm", 10.5, RED, "middle", "bold", "italic")
    s += text(ax - 36, ay + amp + 4, "−Vm", 10.5, RED, "middle", "bold", "italic")

    # Vm: від осі до першого піка (чверть «періоду» при 1.6 циклах на aw)
    qx = ax + aw / 1.6 / 4.0
    s += arrow(qx, ay, qx, ay - amp, BLUE, 2.4)
    s += text(qx + 8, ay - amp / 2, "Vm (амплітуда)", 11.5, BLUE, "start", "bold")

    # Vpp: повний розмах на іншій вертикалі (де хвиля проходить пік-низ поряд)
    px = ax + aw * 0.62
    s += arrow(px, ay - amp, px, ay + amp, GREEN, 2.4)
    s += arrow(px, ay + amp, px, ay - amp, GREEN, 2.4)
    s += text(px + 8, ay, "Vpp = 2·Vm", 11.5, GREEN, "start", "bold")
    s += text(px + 8, ay + 16, "(розмах)", 10, GREEN, "start")

    # миттєве v(t): точка на хвилі
    tfrac = 0.86
    pts = _sine_path(ax, ay, aw, amp, 1.6, 0.0)
    i = int(tfrac * (len(pts) - 1))
    vx, vy = pts[i]
    s += line(ax, vy, vx, vy, ORANGE, 1.4, "4,3")
    s += line(vx, ay, vx, vy, ORANGE, 1.4, "4,3")
    s += circle(vx, vy, 4.5, ORANGE, ORANGE, 1)
    s += text(vx + 6, vy - 8, "v(t) — миттєве", 10.5, ORANGE, "start", "bold")
    save("fig-7-2-1-amplitude-kinds.svg", s)


# ── Рис. 7.2.2 — період і частота: повільна vs швидка хвиля, f = 1/T ──────────
def fig_period_frequency():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 28, "Період і частота — дві мови про одне: як часто повторюється цикл",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "довгий період = низька частота; короткий період = висока частота; завжди f = 1/T",
              11, GREY, "middle", style="italic")

    aw = 720
    ax = 120
    amp = 52

    # верх: повільна хвиля (2 цикли на aw) → довгий T, мала f
    ay = 130
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.3)
    s += polyline(_sine_path(ax, ay, aw, amp, 2.0, 0.0), RED, 2.7)
    s += text(ax - 8, ay - amp - 8, "повільна", 11, RED, "end", "bold")
    # позначити один період = aw/2
    T1 = aw / 2.0
    ty = ay + amp + 22
    s += arrow(ax, ty, ax + T1, ty, GREEN, 2.0)
    s += arrow(ax + T1, ty, ax, ty, GREEN, 2.0)
    s += line(ax, ay, ax, ty + 6, FAINT, 1.1, "3,3")
    s += line(ax + T1, ay, ax + T1, ty + 6, FAINT, 1.1, "3,3")
    s += text(ax + T1 / 2, ty + 18, "T = 20 мс", 11, GREEN, "middle", "bold")
    s += text(ax + aw - 4, ay - amp - 8, "f = 1/T = 50 Гц", 11, INK, "end", "bold")

    # низ: швидка хвиля (6 циклів) → короткий T, велика f
    ay2 = 300
    s += arrow(ax, ay2, ax + aw + 12, ay2, GREY, 1.3)
    s += polyline(_sine_path(ax, ay2, aw, amp, 6.0, 0.0), BLUE, 2.7)
    s += text(ax - 8, ay2 - amp - 8, "швидка", 11, BLUE, "end", "bold")
    T2 = aw / 6.0
    ty2 = ay2 + amp + 22
    s += arrow(ax, ty2, ax + T2, ty2, GREEN, 2.0)
    s += arrow(ax + T2, ty2, ax, ty2, GREEN, 2.0)
    s += line(ax, ay2, ax, ty2 + 6, FAINT, 1.1, "3,3")
    s += line(ax + T2, ay2, ax + T2, ty2 + 6, FAINT, 1.1, "3,3")
    s += text(ax + T2 + 8, ty2 + 18, "T менший", 10.5, GREEN, "start", "bold")
    s += text(ax + aw - 4, ay2 - amp - 8, "f більша", 11, INK, "end", "bold")

    s += text(W / 2, 392, "та сама амплітуда, інша частота: хвилі різняться лише тим, як часто повторюється цикл",
              11, INK, "middle", "bold")
    save("fig-7-2-2-period-frequency.svg", s)


# ── Рис. 7.2.3 — спектр частот: від мережі до радіо (логарифмічна шкала) ──────
def fig_frequency_scale():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 28, "Шкала частот: одна формула f = 1/T — від мережі до радіо",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "частота охоплює багато порядків; назви діапазонів — лише ярлики на тій самій осі f",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 70, 235, 760
    s += arrow(ax - 10, ay, ax + aw + 16, ay, INK, 2.0)
    s += text(ax + aw + 12, ay + 22, "f", 13, INK, "middle", "bold", "italic")
    # декади 10^1 … 10^9
    decades = [("10¹", "10 Гц"), ("10²", ""), ("10³", "1 кГц"), ("10⁴", ""),
               ("10⁵", ""), ("10⁶", "1 МГц"), ("10⁷", ""), ("10⁸", ""), ("10⁹", "1 ГГц")]
    n = len(decades)
    for k, (pw, lab) in enumerate(decades):
        x = ax + aw * k / (n - 1)
        s += line(x, ay - 7, x, ay + 7, INK, 1.6)
        s += text(x, ay + 24, pw, 10.5, INK, "middle", "bold")
        if lab:
            s += text(x, ay + 40, lab, 9, GREY, "middle")

    # маркери явищ над віссю (позиція ~ десяткова шкала)
    def xat(decade):  # decade у логарифмі 1..9
        return ax + aw * (decade - 1) / (n - 1)

    bands = [("мережа 50/60 Гц", 1.75, RED, 95),
             ("звук (чутний) 20 Гц–20 кГц", 3.3, GREEN, 130),
             ("ШІМ, аудіо-ЦАП", 4.5, ORANGE, 95),
             ("AM-радіо ~1 МГц", 6.0, BLUE, 130),
             ("FM, Wi-Fi 10⁸–10⁹", 8.3, BLUE, 95)]
    for lab, dec, col, ytop in bands:
        x = xat(dec)
        s += line(x, ay - 7, x, ytop + 8, col, 1.6, "4,3")
        s += circle(x, ay - 7, 3.4, col, col, 1)
        s += rect(x - 78, ytop - 16, 156, 24, "#ffffff", col, 1.4, 7)
        s += text(x, ytop, lab, 9.5, col, "middle", "bold")

    s += text(W / 2, 310, "ω = 2π·f      f = 1/T      T = 1/f   — три імені тієї самої швидкості повторення",
              12.5, INK, "middle", "bold")
    save("fig-7-2-3-frequency-scale.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.7.3 — Фаза й зсув фаз.  Рис. 7.3.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 7.3.1 — фаза як точка старту циклу (0°, 90°, 180°) ───────────────────
def fig_phase_start():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 28, "Фаза — це з якої точки циклу хвиля стартує",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "та сама амплітуда й частота; різний доданок φ зсуває всю хвилю вздовж осі часу",
              11, GREY, "middle", style="italic")

    aw = 760
    ax = 90
    amp = 70
    rows = [("φ = 0  — синус від нуля вгору", 0.0, RED, 130),
            ("φ = +90°  — стартує з піка (косинус)", math.pi / 2, BLUE, 250),
            ("φ = 180°  — дзеркальний (−sin)", math.pi, GREEN, 370)]
    for lab, ph, col, ay in rows:
        s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.3)
        s += text(ax + aw + 8, ay + 16, "t", 11, GREY, "middle", "bold", "italic")
        s += polyline(_sine_path(ax, ay, aw, amp, 1.6, ph), col, 2.7)
        s += text(ax - 8, ay - amp - 10, lab, 11, col, "end", "bold")
        # точка старту
        y0 = ay - amp * math.sin(ph)
        s += circle(ax, y0, 4.5, col, col, 1)
    # вертикаль t=0
    s += line(ax, 100, ax, 400, FAINT, 1.2, "3,3")
    s += text(ax, 92, "t = 0", 10, GREY, "middle", "bold")
    save("fig-7-3-1-phase-start.svg", s)


# ── Рис. 7.3.2 — зсув фаз: випередження/відставання, Δφ і Δt ──────────────────
def fig_phase_shift():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 28, "Зсув фаз: на скільки одна хвиля випереджає іншу",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "дві синусоїди тієї самої частоти; кут між ними Δφ — це часовий зсув Δt у частках періоду",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 90, 215, 760
    amp = 100
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.4)
    s += arrow(ax, ay + 130, ax, ay - 130, GREY, 1.4)
    s += text(ax + aw + 8, ay + 18, "t", 12, GREY, "middle", "bold", "italic")
    s += text(ax - 8, ay - 118, "v", 12, GREY, "end", "bold", "italic")

    ph = math.radians(60)  # друга хвиля відстає на 60°
    s += polyline(_sine_path(ax, ay, aw, amp, 2.0, 0.0), RED, 2.8)
    s += polyline(_sine_path(ax, ay, aw, amp * 0.82, 2.0, -ph), BLUE, 2.8)
    s += text(ax + 6, ay - amp - 8, "хвиля A (випереджає)", 10.5, RED, "start", "bold")
    s += text(ax + 6, ay + amp + 18, "хвиля B (відстає на Δφ)", 10.5, BLUE, "start", "bold")

    # позначити Δt між першими підйомними нулями
    # A проходить нуль вгору при t=0; B — при фазі ωt = ph
    cyc = aw / 2.0  # пікселів на період (2 цикли на aw)
    x_b = ax + cyc * (ph / (2 * math.pi))
    yb = ay + 60
    s += line(ax, ay, ax, yb + 10, FAINT, 1.2, "3,3")
    s += line(x_b, ay, x_b, yb + 10, FAINT, 1.2, "3,3")
    s += arrow(ax, yb, x_b, yb, GREEN, 2.2)
    s += arrow(x_b, yb, ax, yb, GREEN, 2.2)
    s += text((ax + x_b) / 2, yb + 18, "Δt", 12, GREEN, "middle", "bold", "italic")
    s += rect(ax + 250, 320, 360, 44, "#eef7f0", GREEN, 1.6, 9)
    s += text(W / 2, 347, "Δφ = 2π · (Δt / T)      зсув у градусах = 360° · Δt/T",
              12.5, GREEN, "middle", "bold")
    save("fig-7-3-2-phase-shift.svg", s)


# ── Рис. 7.3.3 — три характерні зсуви: синфазно, квадратура, протифазно ───────
def fig_phase_cases():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 28, "Три характерні зсуви фаз, які треба впізнавати",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "0° — разом; 90° — чверть періоду (квадратура); 180° — у протифазі (гасять одне одного)",
              11, GREY, "middle", style="italic")

    aw = 230
    amp = 50
    panels = [("синфазно  Δφ = 0", 0.0, 150),
              ("квадратура  Δφ = 90°", math.pi / 2, 460),
              ("протифаза  Δφ = 180°", math.pi, 770)]
    for lab, ph, cx in panels:
        ax = cx - aw / 2
        ay = 180
        s += arrow(ax, ay, ax + aw + 8, ay, GREY, 1.2)
        s += polyline(_sine_path(ax, ay, aw, amp, 1.5, 0.0), RED, 2.5)
        s += polyline(_sine_path(ax, ay, aw, amp * 0.78, 1.5, -ph), BLUE, 2.5)
        s += text(cx, 96, lab, 12, INK, "middle", "bold")
        s += line(ax, 110, ax, 250, FAINT, 1.1, "3,3")
    # підписи знизу
    s += text(150, 300, "ідуть нога в ногу", 10, GREEN, "middle")
    s += text(460, 300, "одна на чверть позаду", 10, ORANGE, "middle")
    s += text(770, 300, "піки проти западин", 10, RED, "middle")
    save("fig-7-3-3-phase-cases.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.7.4 — Середнє й діюче значення (RMS).  Рис. 7.4.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 7.4.1 — середнє за період = 0; середнє випрямленого ──────────────────
def fig_mean_zero():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 28, "Чому просте середнє синусоїди — нуль (і чому воно нам не годиться)",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "додатна й від'ємна половини рівні: площа над віссю гасить площу під нею",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 100, 200, 700
    amp = 110
    s += arrow(ax, ay, ax + aw + 14, ay, GREY, 1.4)
    s += arrow(ax, ay + 140, ax, ay - 140, GREY, 1.4)
    s += text(ax + aw + 10, ay + 18, "t", 12, GREY, "middle", "bold", "italic")
    s += text(ax - 8, ay - 128, "v", 12, GREY, "end", "bold", "italic")

    pts = _sine_path(ax, ay, aw, amp, 2.0, 0.0)
    # заштрихувати додатні (+) червоним напівпрозоро, від'ємні (−) синім
    # півперіод = aw/4
    half = aw / 4.0
    for k in range(4):
        seg = [(ax + k * half, ay)]
        i0 = int((k * half) / aw * (len(pts) - 1))
        i1 = int(((k + 1) * half) / aw * (len(pts) - 1))
        seg += pts[i0:i1 + 1]
        seg += [(ax + (k + 1) * half, ay)]
        fill = "#f7d6d2" if k % 2 == 0 else "#d6def5"
        s += polygon(seg, fill, "none", 0)
    s += polyline(pts, INK, 2.8)
    s += text(ax + half * 0.5, ay - amp / 2, "+", 22, RED, "middle", "bold")
    s += text(ax + half * 1.5, ay + amp / 2, "−", 22, BLUE, "middle", "bold")
    s += text(ax + half * 2.5, ay - amp / 2, "+", 22, RED, "middle", "bold")
    s += text(ax + half * 3.5, ay + amp / 2, "−", 22, BLUE, "middle", "bold")
    s += rect(ax + 200, 330, 300, 40, "#f3f3f3", GREY, 1.4, 8)
    s += text(W / 2, 356, "⟨v⟩ за період = 0   →   просте середнє марне",
              12.5, INK, "middle", "bold")
    save("fig-7-4-1-mean-zero.svg", s)


# ── Рис. 7.4.2 — RMS як еквівалентний за нагрівом постійний струм ──────────────
def fig_rms_heating():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 28, "RMS: постійне значення, що гріє так само, як цей змінний струм",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "однаковий резистор, однакове тепло за секунду — у цьому й сенс «діючого» значення",
              11, GREY, "middle", style="italic")

    # ── ліворуч: змінний струм гріє резистор ──
    ax, ay, aw = 70, 175, 300
    amp = 70
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.3)
    s += polyline(_sine_path(ax, ay, aw, amp, 2.0, 0.0), RED, 2.7)
    s += text(ax + aw / 2, ay - amp - 14, "AC: i(t) = Im·sin(ωt)", 11, RED, "middle", "bold")
    s += _resistor(ax + 90, ay + 150, 120, 30, "R")
    s += line(ax + 90, ay + 150, ax + 60, ay + 150, INK, 2)
    s += line(ax + 210, ay + 150, ax + 240, ay + 150, INK, 2)
    s += text(ax + aw / 2, ay + 200, "віддає тепло P за секунду", 10.5, INK, "middle", "bold")

    # ── стрілка-еквівалентність ──
    s += text(W / 2, 175, "≙", 30, GREEN, "middle", "bold")
    s += text(W / 2, 205, "те саме", 10, GREEN, "middle", "bold")
    s += text(W / 2, 219, "тепло", 10, GREEN, "middle", "bold")

    # ── праворуч: постійний струм Irms гріє так само ──
    bx, by, bw = 540, 175, 300
    s += arrow(bx, by, bx + bw + 12, by, GREY, 1.3)
    s += line(bx, by - 44, bx + bw, by - 44, BLUE, 2.7)
    s += text(bx + bw / 2, by - 58, "DC: I = Irms (стала)", 11, BLUE, "middle", "bold")
    s += line(bx, by - 44, bx, by, FAINT, 1.2, "3,3")
    s += _resistor(bx + 90, by + 150, 120, 30, "R")
    s += line(bx + 90, by + 150, bx + 60, by + 150, INK, 2)
    s += line(bx + 210, by + 150, bx + 240, by + 150, INK, 2)
    s += text(bx + bw / 2, by + 200, "віддає те саме тепло P", 10.5, INK, "middle", "bold")

    s += rect(230, 350, 440, 44, "#eef7f0", GREEN, 1.6, 9)
    s += text(W / 2, 377, "для синусоїди:  Irms = Im / √2 ≈ 0.707·Im",
              13.5, GREEN, "middle", "bold")
    save("fig-7-4-2-rms-heating.svg", s)


# ── Рис. 7.4.3 — рецепт RMS: квадрат → середнє → корінь ───────────────────────
def fig_rms_recipe():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 28, "Звідки √2: квадрат синуса, його середнє ½ і корінь",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "Root-Mean-Square читають справа наліво: піднести в Квадрат → взяти Середнє → Корінь",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 80, 215, 760
    amp = 95
    # синус
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.3)
    s += text(ax + aw + 8, ay + 16, "t", 11, GREY, "middle", "bold", "italic")
    s += polyline(_sine_path(ax, ay, aw, amp, 2.0, 0.0), RED, 2.6)
    s += text(ax + 6, ay - amp - 8, "i = Im·sin(ωt)", 10.5, RED, "start", "bold")

    # квадрат: sin² завжди ≥ 0, коливається коло ½ з подвоєною частотою
    sq = []
    nn = 240
    for k in range(nn + 1):
        t = k / nn
        val = math.sin(2 * math.pi * 2.0 * t) ** 2     # 0..1
        sq.append((ax + t * aw, ay - val * amp))
    s += polyline(sq, BLUE, 2.6)
    # рівень середнього ½
    s += line(ax, ay - amp / 2, ax + aw, ay - amp / 2, GREEN, 1.8, "6,4")
    s += text(ax + aw + 4, ay - amp / 2, "⟨i²⟩ = Im²/2", 10.5, GREEN, "start", "bold")
    s += text(ax + 6, ay - amp - 26, "i² = Im²·sin²(ωt)  (завжди ≥ 0, удвічі частіше)",
              10.5, BLUE, "start", "bold")

    # підпис кроків знизу
    box = [("1. КВАДРАТ", "sin² ≥ 0", 170, BLUE),
           ("2. СЕРЕДНЄ", "⟨sin²⟩ = ½", 450, GREEN),
           ("3. КОРІНЬ", "√(Im²/2) = Im/√2", 740, RED)]
    for t1, t2, cx, col in box:
        s += rect(cx - 110, 330, 220, 50, "#ffffff", col, 1.5, 8)
        s += text(cx, 351, t1, 11.5, col, "middle", "bold")
        s += text(cx, 369, t2, 11, INK, "middle", "bold")
    s += arrow(282, 355, 338, 355, GREY, 2.2)
    s += arrow(562, 355, 628, 355, GREY, 2.2)
    save("fig-7-4-3-rms-recipe.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.7.5 — Синусоїда на осцилографі.  Рис. 7.5.k
# ════════════════════════════════════════════════════════════════════════════

def _graticule(x0, y0, w, h, cols, rows):
    """Сітка осцилографа: рамка + поділки. Повертає (svg, cellw, cellh)."""
    out = rect(x0, y0, w, h, "#fbfcf7", INK, 2.0, 4)
    cw, ch = w / cols, h / rows
    for c in range(1, cols):
        out += line(x0 + c * cw, y0, x0 + c * cw, y0 + h, FAINT, 1.1)
    for r in range(1, rows):
        out += line(x0, y0 + r * ch, x0 + w, y0 + r * ch, FAINT, 1.1)
    # центральні осі — жирніші
    out += line(x0 + cols // 2 * cw, y0, x0 + cols // 2 * cw, y0 + h, GREY, 1.5)
    out += line(x0, y0 + rows // 2 * ch, x0 + w, y0 + rows // 2 * ch, GREY, 1.5)
    return out, cw, ch


# ── Рис. 7.5.1 — зчитати Vpp, Vm і період із поділок екрана ───────────────────
def fig_scope_read():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 28, "Синус на екрані: рахуємо амплітуду й період у поділках",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "висоту й тривалість беруть у клітинках і множать на масштаб «В/поділка» та «час/поділка»",
              11, GREY, "middle", style="italic")

    cols, rows = 10, 8
    x0, y0, w, h = 80, 80, 600, 300
    grat, cw, ch = _graticule(x0, y0, w, h, cols, rows)
    s += grat
    cy = y0 + h / 2
    # синус: амплітуда 3 поділки, період 4 поділки
    amp = 3 * ch
    cycles = w / (4 * cw)  # 2.5 цикли на 10 поділок
    s += polyline(_sine_path(x0, cy, w, amp, cycles, 0.0), RED, 2.8)

    # Vpp: між піком і низом (вертикальна двонапрямлена)
    mx = x0 + 1 * cw
    s += arrow(mx, cy - amp, mx, cy + amp, BLUE, 2.2)
    s += arrow(mx, cy + amp, mx, cy - amp, BLUE, 2.2)
    s += text(mx + 8, cy, "6 поділок", 10.5, BLUE, "start", "bold")
    s += text(mx + 8, cy + 15, "= Vpp", 10.5, BLUE, "start", "bold")

    # період: одна повна хвиля = 4 поділки по горизонталі
    py = y0 + h + 22
    s += arrow(x0, py, x0 + 4 * cw, py, GREEN, 2.2)
    s += arrow(x0 + 4 * cw, py, x0, py, GREEN, 2.2)
    s += line(x0, cy, x0, py + 6, FAINT, 1.1, "3,3")
    s += line(x0 + 4 * cw, cy, x0 + 4 * cw, py + 6, FAINT, 1.1, "3,3")
    s += text(x0 + 2 * cw, py + 18, "T = 4 поділки", 11, GREEN, "middle", "bold")

    # ручки масштабу
    s += text(x0, y0 - 10, "1 В/поділка", 11, RED, "start", "bold")
    s += text(x0 + w, y0 - 10, "1 мс/поділка", 11, GREEN, "end", "bold")

    # розрахунок збоку
    bx = 700
    s += rect(bx, 90, 180, 250, "#f6f8fc", GREY, 1.5, 8)
    s += text(bx + 90, 114, "Зчитування:", 12, INK, "middle", "bold")
    lines = ["Vpp = 6×1 = 6 В", "Vm = Vpp/2 = 3 В",
             "T = 4×1 = 4 мс", "f = 1/T = 250 Гц",
             "Vrms = Vm/√2", "    ≈ 2.12 В"]
    for k, ln in enumerate(lines):
        col = RED if k < 2 else (GREEN if k < 4 else BLUE)
        s += text(bx + 14, 142 + k * 30, ln, 11.5, col, "start", "bold")
    save("fig-7-5-1-scope-read.svg", s)


# ── Рис. 7.5.2 — вхід AC/DC/GND: де опиняється та сама хвиля ──────────────────
def fig_scope_coupling():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 28, "Вхідний режим AC/DC: де на екрані сяде сигнал зі зміщенням",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "сигнал — мала синусоїда на сталому «постаменті» (DC-зміщенні); режим входу вирішує, чи видно постамент",
              11, GREY, "middle", style="italic")

    panels = [("DC-зв'язок", 0, 175, "видно й зміщення, й хвилю", ORANGE),
              ("AC-зв'язок", 1, 525, "постамент відрізано — лише хвиля", GREEN),
              ("GND", 2, 800, "вхід замкнено: рівна лінія = 0", GREY)]
    h = 170
    for lab, kind, cx, note, col in panels:
        x0 = cx - 130
        y0 = 95
        w = 260
        grat, cw, ch = _graticule(x0, y0, w, h, 8, 6)
        s += grat
        cy = y0 + h / 2
        if kind == 0:   # DC: хвиля піднята на 2 поділки
            yc = cy - 2 * ch
            s += polyline(_sine_path(x0, yc, w, 1.2 * ch, 2.0, 0.0), col, 2.6)
            s += line(x0, cy, x0 + w, cy, FAINT, 1.0, "3,3")
        elif kind == 1:  # AC: та сама хвиля, центрована
            s += polyline(_sine_path(x0, cy, w, 1.2 * ch, 2.0, 0.0), col, 2.6)
        else:            # GND: рівна лінія
            s += line(x0 + 6, cy, x0 + w - 6, cy, col, 2.6)
        s += text(cx, y0 - 8, lab, 12.5, col, "middle", "bold")
        s += text(cx, y0 + h + 22, note, 9.8, INK, "middle", "bold")
    save("fig-7-5-2-scope-coupling.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.7.6 — Чому мережа змінна: транспорт енергії.  Рис. 7.6.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 7.6.1 — втрати I²R: висока напруга = малий струм = малі втрати ───────
def fig_transmission_loss():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 28, "Чому передають високою напругою: втрати в дроті ростуть із квадратом струму",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "та сама потужність P = U·I; підняли U удесятеро → струм у 10 разів менший → втрати I²R у 100 разів менші",
              11, GREY, "middle", style="italic")

    # дві лінії передачі — «низька U» і «висока U»
    def line_panel(y0, title, U, I, loss_w, col, note):
        out = text(70, y0 - 22, title, 13, col, "start", "bold")
        # джерело
        out += circle(120, y0, 26, "#fff", col, 2.2)
        out += text(120, y0 + 5, "~", 22, col, "middle", "bold")
        out += text(120, y0 + 44, f"{U}", 11, INK, "middle", "bold")
        # дріт з опором R (зигзаг-резистор посередині)
        out += line(146, y0, 360, y0, COPPER, 3.0)
        out += line(540, y0, 740, y0, COPPER, 3.0)
        out += _resistor(390, y0, 120, 26, "R дроту")
        # навантаження
        out += rect(740, y0 - 28, 56, 56, "#eef7f0", GREEN, 2.0, 5)
        out += text(768, y0 + 5, "P", 16, GREEN, "middle", "bold", "italic")
        # струм
        out += arrow(180, y0 - 38, 320, y0 - 38, INK, 2.2)
        out += text(250, y0 - 46, f"I = {I}", 11, INK, "middle", "bold")
        # втрати — товщина стрічки тепла з дроту
        out += rect(360, y0 + 30, 156, loss_w, "#f7d6d2", RED, 1.2, 3)
        out += text(438, y0 + 30 + loss_w + 14, note, 10.5, RED, "middle", "bold")
        return out

    s += line_panel(150, "НИЗЬКА напруга", "1 кВ", "100 А", 40, RED,
                    "втрати ∝ 100² — великі")
    s += line_panel(330, "ВИСОКА напруга", "100 кВ", "1 А", 4, GREEN,
                    "втрати ∝ 1² — у 10000× менші")

    s += text(W / 2, 408, "P_втрат = I²·R — менший струм коштує квадратично менших втрат; тому в магістраль ідуть сотні кіловольтів",
              11, INK, "middle", "bold")
    save("fig-7-6-1-transmission-loss.svg", s)


# ── Рис. 7.6.2 — ланцюг напруг: генератор → ЛЕП → дім (трансформатори) ────────
def fig_grid_chain():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 28, "Чому саме AC: трансформатор піднімає й опускає напругу майже без втрат",
              18, INK, "middle", "bold")
    s += text(W / 2, 50, "змінний струм легко «перевести» на іншу напругу — підняти для далекої передачі й опустити до безпечної",
              11, GREY, "middle", style="italic")

    y = 185
    # станції-вузли ланцюга
    nodes = [("Генератор", "~15 кВ", 95, BLUE),
             ("⇧ транс.", "→ 400 кВ", 270, GREEN),
             ("ЛЕП", "400 кВ", 445, INK),
             ("⇩ транс.", "→ 10 кВ", 605, GREEN),
             ("Дім", "230 В", 790, RED)]
    for lab, val, cx, col in nodes:
        s += rect(cx - 62, y - 34, 124, 68, "#ffffff", col, 1.9, 9)
        s += text(cx, y - 8, lab, 12.5, col, "middle", "bold")
        s += text(cx, y + 14, val, 12, INK, "middle", "bold")

    # стрілки між вузлами
    xs = [95, 270, 445, 605, 790]
    for a, b in zip(xs[:-1], xs[1:]):
        s += arrow(a + 64, y, b - 64, y, INK, 2.4)

    # символ трансформатора (дві котушки) під ⇧ і ⇩
    def xfmr(cx):
        out = ""
        for off, col in ((-12, COPPER), (12, COPPER)):
            for k in range(3):
                out += circle(cx + off, y + 70 + k * 9, 5, "none", col, 1.6)
        out += line(cx, y + 64, cx, y + 100, GREY, 1.4)
        return out
    s += xfmr(270)
    s += xfmr(605)
    s += text(270, y + 120, "підвищує U", 9.5, GREEN, "middle", "bold")
    s += text(605, y + 120, "знижує U", 9.5, GREEN, "middle", "bold")

    s += text(W / 2, 320, "трансформатор працює ЛИШЕ на змінному струмі — у цьому вирішальна перевага AC для енергомережі",
              11, INK, "middle", "bold")
    save("fig-7-6-2-grid-chain.svg", s)


if __name__ == "__main__":
    fig_before_after()
    fig_phasor()
    fig_collective()
    # Тема 1.7.1
    fig_circle_to_sine()
    fig_restoring_force()
    fig_curvature()
    fig_generator()
    fig_shape_preserved()
    fig_fourier()
    fig_sine_anatomy()
    # Тема 1.7.2
    fig_amplitude_kinds()
    fig_period_frequency()
    fig_frequency_scale()
    # Тема 1.7.3
    fig_phase_start()
    fig_phase_shift()
    fig_phase_cases()
    # Тема 1.7.4
    fig_mean_zero()
    fig_rms_heating()
    fig_rms_recipe()
    # Тема 1.7.5
    fig_scope_read()
    fig_scope_coupling()
    # Тема 1.7.6
    fig_transmission_loss()
    fig_grid_chain()
    print("OK")
