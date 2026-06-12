# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 2.10 — «Резонатори й опорні частоти» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи посекційно: Рис. 2.10.S.N,
тож імена файлів fig-2-10-S-N-*.svg. Допоміжні функції скопійовано з попередніх розділів.
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
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3df"
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


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _fillpoly(pts, fill, stroke="none", wv=1.0, op=1.0):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    so = f' stroke="{stroke}" stroke-width="{wv}"' if stroke != "none" else ""
    return f'<path d="M {d} Z" fill="{fill}" fill-opacity="{op}"{so}/>\n'


def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12.5, INK, "middle", "bold")
    return s


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 6, oy - h - 20, ylab, 13, INK, "middle", "bold")
    return s


def _sine(ox, oy, w, amp, cycles, col, wv=2.4, phase=0.0):
    pts = []
    n = max(int(w), 60)
    for j in range(0, n + 1):
        t = j / n
        y = oy - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((ox + w * t, y))
    return _poly(pts, col, wv)


def _cap_h(cx, cy, gap=7, plate=13, col=INK):
    return (line(cx - gap, cy - plate, cx - gap, cy + plate, col, 2.4)
            + line(cx + gap, cy - plate, cx + gap, cy + plate, col, 2.4))


def _cap_v(cx, cy, gap=7, plate=13, col=INK):
    return (line(cx - plate, cy - gap, cx + plate, cy - gap, col, 2.4)
            + line(cx - plate, cy + gap, cx + plate, cy + gap, col, 2.4))


def _coil_h(cx, cy, length, turns=4, r=9, col=INK):
    """Котушка горизонтально як низка арок."""
    x0 = cx - length / 2
    dx = length / turns
    s = ""
    for i in range(turns):
        x = x0 + i * dx
        s += (f'<path d="M {x:.1f},{cy} '
              f'a {dx/2:.1f},{r:.1f} 0 0 1 {dx:.1f},0" '
              f'fill="none" stroke="{col}" stroke-width="2.2"/>\n')
    return s, (x0, x0 + length)


def _res_h(cx, cy, length=46, h=9, col=INK):
    """Резистор-зигзаг горизонтально."""
    x0 = cx - length / 2
    seg = length / 6
    pts = [(x0, cy)]
    for i in range(1, 6):
        pts.append((x0 + seg * i, cy + (h if i % 2 else -h)))
    pts.append((x0 + length, cy))
    return _poly(pts, col, 2.2), (x0, x0 + length)


def _crystal_sym(cx, cy, col=INK):
    """Символ кварцу: прямокутник між двома пластинами."""
    s = rect(cx - 9, cy - 16, 18, 32, "#eef2f7", col, 2.0, 2)
    s += line(cx - 17, cy - 18, cx - 17, cy + 18, col, 2.4)
    s += line(cx + 17, cy - 18, cx + 17, cy + 18, col, 2.4)
    s += line(cx - 17, cy, cx - 28, cy, col, 2)
    s += line(cx + 17, cy, cx + 28, cy, col, 2)
    return s


def _inv_sym(cx, cy, w=46, h=40, col=INK):
    """Символ інвертора (трикутник з кружком)."""
    s = (f'<path d="M {cx-w/2:.0f},{cy-h/2:.0f} L {cx-w/2:.0f},{cy+h/2:.0f} '
         f'L {cx+w/2-8:.0f},{cy:.0f} Z" fill="#fbfbfb" stroke="{col}" stroke-width="1.9"/>\n')
    s += circle(cx + w / 2 - 4, cy, 4, "#ffffff", col, 1.8)
    return s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.1  Навіщо системі опорна частота
# ─────────────────────────────────────────────────────────────────────────────

def fig_1_1_what_clock_drives():
    """Один тактовий сигнал розгалужується на споживачів точного часу."""
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 26, "Один опорний такт живить усе, що залежить від часу", 16, INK, "middle", "bold")

    # джерело такту
    ox, oy = 60, 180
    s += rect(ox, oy - 40, 130, 80, LSUN, SUN, 2.2, 8)
    s += text(ox + 65, oy - 12, "Опорний", 14, INK, "middle", "bold")
    s += text(ox + 65, oy + 6, "генератор", 14, INK, "middle", "bold")
    s += text(ox + 65, oy + 26, "(кварц)", 12, GREY, "middle")
    # маленька прямокутна хвиля всередині-знизу
    base = oy + 52
    pts = []
    x = ox + 8
    hi, lo = base - 12, base
    for i in range(7):
        pts.append((x, lo if i % 2 == 0 else hi))
        pts.append((x + 16, lo if i % 2 == 0 else hi))
        x += 16
    s += _poly(pts, SUN, 2.2)
    s += text(ox + 65, base + 22, "стабільні імпульси", 11.5, GREY, "middle")

    consumers = [
        ("Такт процесора", "кожна команда — за тактом", 60),
        ("Відлік часу", "годинник, таймери, дати", 140),
        ("UART / шина", "момент кожного біта", 220),
        ("ШІМ, АЦП", "коли семплувати", 300),
    ]
    cx = 470
    for name, sub, cy in consumers:
        s += arrow(ox + 132, oy, cx - 4, cy, INK, 2)
        s += rect(cx, cy - 24, 210, 48, LBLUE, BLUE, 1.8, 8)
        s += text(cx + 105, cy - 3, name, 13.5, INK, "middle", "bold")
        s += text(cx + 105, cy + 16, sub, 11.5, GREY, "middle")
    return W, H, s


def fig_1_2_rc_vs_crystal_drift():
    """Дрейф фронтів передачі: RC vs кварц на тлі еталонних вікон біта."""
    W, H = 720, 380
    s = header(W, H)
    s += text(W / 2, 26, "Чому RC-генератора не досить для зв'язку: фронти «розповзаються»", 15.5, INK, "middle", "bold")

    ox, oy, w = 70, 120, 600
    # еталонні межі бітів
    nbits = 10
    bw = w / nbits
    for i in range(nbits + 1):
        s += line(ox + i * bw, oy - 22, ox + i * bw, oy + 250, FAINT, 1.4, "4 4")
    s += text(ox - 8, oy - 26, "межі бітів (ідеальні моменти семплування)", 11.5, GREY, "start")

    # ряд 1 — кварц: фронти точно по межах
    y1 = oy + 30
    s += text(ox - 8, y1 - 30, "Кварц ±20 ppm — кромки збігаються з межами весь кадр", 12.5, GREEN, "start", "bold")
    pts = []
    x = ox
    lvl = y1 - 16
    for i in range(nbits):
        hi = (i % 3 != 1)
        yy = (y1 - 16) if hi else y1
        pts.append((x, yy)); pts.append((x + bw, yy))
        x += bw
    s += _poly(pts, GREEN, 2.4)
    for i in range(nbits + 1):
        s += circle(ox + i * bw, y1 - 8, 2.4, GREEN, GREEN, 1)

    # ряд 2 — RC: фронти зсуваються накопичувально
    y2 = oy + 130
    s += text(ox - 8, y2 - 30, "RC ±5 % — кромки повзуть; до кінця кадру семпл уже не в той біт", 12.5, RED, "start", "bold")
    drift = 0.05
    pts = []
    x = ox
    for i in range(nbits):
        hi = (i % 3 != 1)
        yy = (y2 - 16) if hi else y2
        xx = ox + i * bw * (1 + drift)   # накопичення
        xx2 = ox + (i + 1) * bw * (1 + drift)
        pts.append((min(xx, ox + w + 30), yy))
        pts.append((min(xx2, ox + w + 30), yy))
    s += _poly(pts, RED, 2.4)
    # стрілка зсуву наприкінці
    s += arrow(ox + w, y2 + 30, ox + w * (1 + drift * nbits) - bw, y2 + 30, RED, 2)
    s += text(ox + w - 6, y2 + 50, "накопичений зсув", 11.5, RED, "end")

    s += text(W / 2, oy + 250 + 26,
              "Похибка часу множиться на кількість бітів — приймач втрачає синхронізацію.",
              12.5, INK, "middle")
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.2  П'єзоефект
# ─────────────────────────────────────────────────────────────────────────────

def fig_2_1_piezo_direct_inverse():
    """Прямий і зворотний п'єзоефект: дві панелі."""
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 24, "П'єзоефект: механіка ↔ електрика в обидва боки", 16, INK, "middle", "bold")

    # ── ліва панель: прямий ефект (тиск → напруга) ──
    s += _frame(40, 56, 300, 268, "Прямий: деформація → заряд")
    cx = 190
    # кристал
    s += rect(cx - 45, 150, 90, 90, LBLUE, BLUE, 2, 4)
    s += text(cx, 198, "кристал", 13, INK, "middle")
    # верхній та нижній електроди
    s += rect(cx - 50, 142, 100, 8, GREY, INK, 1.2)
    s += rect(cx - 50, 240, 100, 8, GREY, INK, 1.2)
    # стиск згори
    s += arrow(cx - 24, 96, cx - 24, 138, INK, 3)
    s += arrow(cx + 24, 96, cx + 24, 138, INK, 3)
    s += text(cx, 90, "натиск (сила)", 12.5, INK, "middle", "bold")
    # вихід на вольтметр
    s += line(cx + 50, 146, cx + 78, 146, INK, 2)
    s += line(cx + 50, 244, cx + 78, 244, INK, 2)
    s += line(cx + 78, 146, cx + 78, 195, INK, 2)
    s += line(cx + 78, 244, cx + 78, 195, INK, 2)
    s += circle(cx + 78, 195, 16, "#ffffff", INK, 1.8)
    s += text(cx + 78, 200, "V", 14, INK, "middle", "bold")
    # знаки зарядів
    s += text(cx - 30, 138, "+ + +", 12, RED, "middle", "bold")
    s += text(cx - 30, 256, "− − −", 12, BLUE, "middle", "bold")

    # ── права панель: зворотний ефект (напруга → деформація) ──
    s += _frame(380, 56, 300, 268, "Зворотний: напруга → деформація")
    cx2 = 530
    s += rect(cx2 - 45, 150, 90, 90, LRED, RED, 2, 4)
    # деформований контур (тонкий, ширший)
    s += rect(cx2 - 52, 162, 104, 66, "none", RED, 1.6, 4)
    s += text(cx2, 198, "кристал", 13, INK, "middle")
    s += rect(cx2 - 50, 142, 100, 8, GREY, INK, 1.2)
    s += rect(cx2 - 50, 240, 100, 8, GREY, INK, 1.2)
    # джерело напруги
    s += line(cx2 + 50, 146, cx2 + 86, 146, INK, 2)
    s += line(cx2 + 50, 244, cx2 + 86, 244, INK, 2)
    s += line(cx2 + 86, 146, cx2 + 86, 180, INK, 2)
    s += line(cx2 + 86, 210, cx2 + 86, 244, INK, 2)
    # символ батареї
    s += line(cx2 + 78, 180, cx2 + 94, 180, RED, 2.4)
    s += line(cx2 + 82, 190, cx2 + 90, 190, BLUE, 2.4)
    s += line(cx2 + 78, 200, cx2 + 94, 200, RED, 2.4)
    s += text(cx2 + 100, 196, "U~", 12.5, INK, "start", "bold")
    # стрілки розширення/стиску
    s += arrow(cx2 - 60, 240, cx2 - 60, 162, RED, 2.2)
    s += arrow(cx2 - 60, 150, cx2 - 60, 228, RED, 2.2)
    s += text(cx2, 86, "напруга жене зміну товщини", 12, INK, "middle", "bold")
    return W, H, s


def fig_2_2_resonance_pump():
    """Змінна напруга на власній частоті розгойдує кристал — резонанс."""
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 26, "Змінна напруга на власній частоті кристала його розгойдує", 15.5, INK, "middle", "bold")

    ox, oy, w = 70, 150, 250
    # вхідний сигнал
    s += text(ox + 125, oy - 80, "Збудження U(t)", 12.5, BLUE, "middle", "bold")
    s += _sine(ox, oy - 50, w, 26, 6, BLUE, 2.2)
    # кристал
    s += _crystal_sym(380, oy - 50, INK)
    s += text(380, oy - 95, "кристал", 12.5, INK, "middle", "bold")
    s += text(380, oy - 78, "власна частота f₀", 11.5, GREY, "middle")
    s += arrow(ox + w + 6, oy - 50, 350, oy - 50, INK, 2)

    # амплітуда відгуку як крива резонансу
    ax, ay, aw, ah = 440, oy + 70, 220, 130
    s += _axes(ax, ay, aw, ah, "f", "розмах")
    # пік у f0
    pts = []
    for i in range(0, 101):
        f = i / 100
        x = ax + aw * f
        d = (f - 0.5)
        amp = ah * 0.96 / (1 + (d / 0.025) ** 2)
        pts.append((x, ay - amp))
    s += _poly(pts, GREEN, 2.6)
    s += line(ax + aw * 0.5, ay, ax + aw * 0.5, ay - ah * 0.96, GREEN, 1.4, "4 4")
    s += text(ax + aw * 0.5, ay + 18, "f₀", 12.5, GREEN, "middle", "bold")
    s += text(ax + aw * 0.5, ay - ah - 4, "величезний відгук лише на f₀", 11.5, INK, "middle")

    # вихідний великий розмах
    s += text(ox + 125, oy + 92, "Відгук на f₀ — велика амплітуда", 12, GREEN, "middle", "bold")
    s += _sine(ox, oy + 130, w, 50, 6, GREEN, 2.4)
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.3  Кварцовий резонатор: висока добротність
# ─────────────────────────────────────────────────────────────────────────────

def fig_3_1_quartz_cut():
    """Зріз кварцу: пластина з електродами, осі, тримачі."""
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 26, "Кварцова пластина: тонкий зріз з електродами, що зрушує по товщині", 15, INK, "middle", "bold")

    # ── ліворуч: кристал кварцу й вирізана пластина ──
    s += _frame(40, 50, 300, 250, "Зріз під точним кутом до осей")
    cx, cy = 150, 175
    # шестигранна призма (схематично)
    hexp = [(cx, cy - 70), (cx + 40, cy - 45), (cx + 40, cy + 45),
            (cx, cy + 70), (cx - 40, cy + 45), (cx - 40, cy - 45)]
    s += _fillpoly(hexp, LBLUE, BLUE, 1.8)
    # пірамідки
    s += _poly([(cx - 40, cy - 45), (cx, cy - 95), (cx + 40, cy - 45)], BLUE, 1.8)
    # вирізана пластина (нахилена)
    plate = [(cx - 30, cy + 12), (cx + 30, cy - 14), (cx + 34, cy - 4), (cx - 26, cy + 22)]
    s += _fillpoly(plate, "#fde9c9", COPP, 2.0)
    s += text(cx, cy + 96, "AT-зріз ≈ 35° до осі", 11.5, GREY, "middle")
    s += arrow(cx + 50, cy - 60, cx + 50, cy + 60, GREY, 1.6)
    s += text(cx + 58, cy, "вісь", 11, GREY, "start")

    # ── праворуч: готова пластина з електродами + рух ──
    s += _frame(380, 50, 300, 250, "Коливання по товщині (thickness shear)")
    px, py = 530, 150
    # пластина в розрізі
    s += rect(px - 70, py - 16, 140, 32, "#fde9c9", COPP, 2)
    # електроди
    s += rect(px - 50, py - 22, 100, 6, GREY, INK, 1.2)
    s += rect(px - 50, py + 16, 100, 6, GREY, INK, 1.2)
    s += line(px - 50, py - 19, px - 96, py - 19, INK, 2)
    s += line(px + 50, py + 19, px + 96, py + 19, INK, 2)
    # стрілки зсуву (верх вправо, низ вліво)
    s += arrow(px - 40, py - 30, px + 10, py - 30, RED, 2.2)
    s += arrow(px + 40, py + 30, px - 10, py + 30, BLUE, 2.2)
    s += text(px, py - 44, "верхня грань →", 11, RED, "middle")
    s += text(px, py + 50, "← нижня грань", 11, BLUE, "middle")
    s += text(px, py + 86, "грані ковзають назустріч — це й є механічний резонанс", 11, INK, "middle")
    return W, H, s


def fig_3_2_q_decay():
    """Згасання дзвону: висока Q (кварц) vs низька Q (LC)."""
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 26, "Висока добротність = повільне згасання: кварц «дзвенить» довго", 15, INK, "middle", "bold")

    ox, oy, w, h = 70, 170, 600, 110

    # LC-контур: швидке згасання (Q ~ 100)
    s += text(ox, oy - 110, "LC-контур: Q ≈ 100 — дзвін гасне за десятки коливань", 12.5, RED, "start", "bold")
    pts = []
    n = 600
    for i in range(n + 1):
        t = i / n
        env = math.exp(-t * 5.0)
        y = oy - 70 - 36 * env * math.cos(2 * math.pi * 14 * t)
        pts.append((ox + w * t, y))
    s += _poly(pts, RED, 2.0)
    # обвідна
    for sgn in (1, -1):
        ep = [(ox + w * (i / n), oy - 70 - sgn * 36 * math.exp(-(i / n) * 5.0)) for i in range(n + 1)]
        s += _poly(ep, RED, 1.0, "3 3")

    # кварц: повільне згасання (Q ~ 50000) — практично не гасне
    s += text(ox, oy + 18, "Кварц: Q ≈ 50 000 — на цьому ж відрізку часу амплітуда майже не падає", 12.5, GREEN, "start", "bold")
    pts = []
    for i in range(n + 1):
        t = i / n
        env = math.exp(-t * 0.05)
        y = oy + 78 - 36 * env * math.cos(2 * math.pi * 14 * t)
        pts.append((ox + w * t, y))
    s += _poly(pts, GREEN, 2.0)
    for sgn in (1, -1):
        ep = [(ox + w * (i / n), oy + 78 - sgn * 36 * math.exp(-(i / n) * 0.05)) for i in range(n + 1)]
        s += _poly(ep, GREEN, 1.0, "3 3")

    s += arrow(ox, oy + 130, ox + w, oy + 130, GREY, 1.8)
    s += text(ox + w, oy + 148, "час", 12, GREY, "end")
    return W, H, s


def fig_3_3_resonance_sharpness():
    """Гострота резонансу: вузький пік кварцу vs широкий LC."""
    W, H = 700, 360
    s = header(W, H)
    s += text(W / 2, 26, "Вузький резонанс = стабільна частота: де кварц «впирається»", 15, INK, "middle", "bold")

    ox, oy, w, h = 90, 300, 520, 230
    s += _axes(ox, oy, w, h, "частота", "відгук")
    f0 = ox + w * 0.5
    s += line(f0, oy, f0, oy - h, INK, 1.2, "4 4")
    s += text(f0, oy + 18, "f₀", 13, INK, "middle", "bold")

    # широкий LC
    pts = []
    for i in range(0, 521):
        f = (i / 520 - 0.5)
        amp = (h * 0.62) / (1 + (f / 0.10) ** 2)
        pts.append((ox + i, oy - amp))
    s += _poly(pts, RED, 2.4)
    s += text(ox + w * 0.80, oy - h * 0.30, "LC: Q≈100", 12.5, RED, "start", "bold")

    # вузький кварц
    pts = []
    for i in range(0, 521):
        f = (i / 520 - 0.5)
        amp = (h * 0.96) / (1 + (f / 0.006) ** 2)
        pts.append((ox + i, oy - amp))
    s += _poly(pts, GREEN, 2.6)
    s += text(f0 + 8, oy - h * 0.92, "кварц: Q≈50 000", 12.5, GREEN, "start", "bold")

    s += text(W / 2, oy + 42,
              "Що вужчий пік, то менше частота «гуляє» — генератор тримається саме f₀.",
              12, INK, "middle")
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.4  Еквівалентна RLC-схема (Баттерворт–ван Дайк)
# ─────────────────────────────────────────────────────────────────────────────

def fig_4_1_bvd_model():
    """Модель BVD: послідовна гілка R1-L1-C1 паралельно з C0."""
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 26, "Модель Баттерворта–ван Дайка: механіку кварцу описують як RLC", 14.5, INK, "middle", "bold")

    # вузли
    nL, nR = 120, 600
    yTop, yBot = 120, 250
    # ліва/права шини
    s += line(nL, yTop, nL, yBot, INK, 2)
    s += line(nR, yTop, nR, yBot, INK, 2)
    s += circle(nL, yTop, 3.5, INK, INK)
    s += circle(nR, yTop, 3.5, INK, INK)
    # виводи
    s += line(nL - 36, yTop, nL, yTop, INK, 2)
    s += line(nR, yTop, nR + 36, yTop, INK, 2)
    s += text(nL - 40, yTop - 8, "вивід", 11, GREY, "end")
    s += text(nR + 40, yTop - 8, "вивід", 11, GREY, "start")

    # послідовна гілка (motional): R1 - L1 - C1
    ym = yTop
    s += line(nL, ym, 200, ym, INK, 2)
    rr, (rx0, rx1) = _res_h(240, ym, 70, 8, INK)
    s += rr
    s += text(240, ym - 20, "R₁", 13, INK, "middle", "bold")
    s += line(rx1, ym, 330, ym, INK, 2)
    cc, (cx0, cx1) = _coil_h(380, ym, 80, 4, 9, INK)
    s += cc
    s += text(380, ym - 22, "L₁", 13, INK, "middle", "bold")
    s += line(cx1, ym, 470, ym, INK, 2)
    s += _cap_h(490, ym, 7, 13, INK)
    s += text(490, ym - 20, "C₁", 13, INK, "middle", "bold")
    s += line(497, ym, nR, ym, INK, 2)
    s += text(305, ym + 30, "механічна (motional) гілка: маса L₁, пружність C₁, втрати R₁", 11.5, GREY, "middle")

    # паралельна C0 (статична ємність електродів)
    yb = yBot
    s += line(nL, yb, 340, yb, INK, 2)
    s += _cap_h(360, yb, 7, 16, GREEN)
    s += text(360, yb + 28, "C₀ — ємність електродів і корпусу (реальна)", 11.5, GREEN, "middle")
    s += line(372, yb, nR, yb, INK, 2)
    return W, H, s


def fig_4_2_two_resonances():
    """Реактанс кварцу від частоти: fs (послідовний) і fp (паралельний)."""
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 26, "Реактанс кварцу: два близькі резонанси — fs і fp", 15.5, INK, "middle", "bold")

    ox, oy, w, h = 100, 200, 520, 130
    # осі: X(f), горизонтальна вісь f посередині
    s += arrow(ox, oy + h + 6, ox, oy - h - 16, INK, 2)
    s += arrow(ox, oy, ox + w + 16, oy, INK, 2)
    s += text(ox + w + 20, oy + 4, "f", 13, INK, "start", "bold")
    s += text(ox - 8, oy - h - 4, "+X", 12, INK, "end", "bold")
    s += text(ox - 8, oy + h + 2, "−X", 12, INK, "end", "bold")
    s += text(ox + 92, oy - h - 4, "індуктивний", 11, GREY, "start")
    s += text(ox + 92, oy + h + 2, "ємнісний", 11, GREY, "start")

    xs, xp = 0.46, 0.56            # нормовані позиції fs, fp
    fsX = ox + w * xs
    fpX = ox + w * xp
    ymax = h - 6                   # межа кривої по модулю

    def reac(f):
        """Спрощена реактанс-функція кварцу: нуль у fs, полюс у fp."""
        eps = 1e-4
        val = (f * f - xs * xs) / (f * (f * f - xp * xp) + eps)
        return val

    # три гілки, кожна обрізана по ymax, з розривом у полюсі fp
    def branch(a, b, col):
        pts = []
        N = 160
        for i in range(N + 1):
            f = a + (b - a) * i / N
            y = oy - reac(f) * 14.0
            y = max(oy - ymax, min(oy + ymax, y))
            pts.append((ox + w * f, y))
        return _poly(pts, col, 2.6)

    s += branch(0.02, xs - 0.002, INK)          # ємнісна нижче fs
    s += branch(xs + 0.001, xp - 0.004, INK)    # індуктивна між fs і fp
    s += branch(xp + 0.004, 0.98, INK)          # ємнісна вище fp

    # маркери fs, fp
    s += line(fsX, oy - ymax, fsX, oy + ymax, GREEN, 1.3, "4 4")
    s += line(fpX, oy - ymax, fpX, oy + ymax, RED, 1.3, "4 4")
    s += circle(fsX, oy, 4.2, GREEN, GREEN)
    s += text(fsX, oy + ymax + 18, "fs", 13, GREEN, "middle", "bold")
    s += text(fsX - 8, oy + 18, "X = 0", 11, GREEN, "end", "bold")
    s += text(fsX - 8, oy + 33, "послідовний", 10.5, GREEN, "end")
    s += text(fpX, oy - ymax - 8, "fp", 13, RED, "middle", "bold")
    s += text(fpX + 8, oy - ymax + 14, "X → ∞", 11, RED, "start", "bold")
    s += text(fpX + 8, oy - ymax + 29, "паралельний", 10.5, RED, "start")

    # «вікно» індуктивності між fs і fp (легка заливка)
    s += f'<rect x="{fsX:.1f}" y="{oy-ymax-2:.1f}" width="{fpX-fsX:.1f}" height="{2*ymax+4:.1f}" fill="#1f8a3b" fill-opacity="0.06"/>\n'

    s += rect(ox + w * 0.04, oy + h + 44, w * 0.92, 30, LSUN, SUN, 1.4, 6)
    s += text(ox + w * 0.5, oy + h + 63,
              "Між fs і fp — вузьке «вікно», де кварц поводиться як величезна індуктивність. fp − fs — частки відсотка.",
              11.5, INK, "middle")
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.5  Генератор П'єрса
# ─────────────────────────────────────────────────────────────────────────────

def fig_5_1_pierce_schematic():
    """Класична схема П'єрса: інвертор + Rf + кварц + два конденсатори."""
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 26, "Генератор П'єрса: інвертор, кварц у зворотному зв'язку і два конденсатори", 14, INK, "middle", "bold")

    # інвертор посередині
    ix, iy = 360, 150
    s += _inv_sym(ix, iy, 56, 46, INK)
    s += text(ix, iy - 36, "інвертор (у чипі)", 11.5, GREY, "middle")
    inL = ix - 28   # вхід
    inR = ix + 24   # вихід (з кружком)
    s += text(inL - 6, iy + 24, "XTAL_IN", 10.5, GREY, "end")
    s += text(inR + 8, iy + 24, "XTAL_OUT", 10.5, GREY, "start")

    # вхідний/вихідний вузли
    nx1, nx2 = 200, 540
    s += line(inL, iy, nx1, iy, INK, 2)
    s += line(inR, iy, nx2, iy, INK, 2)
    s += circle(nx1, iy, 3.5, INK, INK)
    s += circle(nx2, iy, 3.5, INK, INK)

    # кварц зверху між вузлами
    s += line(nx1, iy, nx1, 90, INK, 2)
    s += line(nx2, iy, nx2, 90, INK, 2)
    s += line(nx1, 90, 330, 90, INK, 2)
    s += _crystal_sym(370, 90, INK)
    s += line(398, 90, nx2, 90, INK, 2)
    s += text(370, 64, "кварц", 12.5, INK, "middle", "bold")

    # Rf паралельно інвертору (між вузлами, нижче)
    rr, (rx0, rx1) = _res_h(370, iy + 0, 0, 0)  # not used
    s += line(nx1, iy, nx1, 200, INK, 2)
    s += line(nx2, iy, nx2, 200, INK, 2)
    s += line(nx1, 200, 330, 200, INK, 2)
    rr, (rx0, rx1) = _res_h(370, 200, 64, 8, GREY)
    s += rr
    s += line(rx1, 200, nx2, 200, INK, 2)
    s += text(370, 222, "Rf — зміщує інвертор у лінійний режим", 11, GREY, "middle")

    # два конденсатори на землю
    gy = 300
    s += line(nx1, iy, nx1, 240, INK, 2)
    s += _cap_v(nx1, 256, 7, 14, GREEN)
    s += line(nx1, 270, nx1, gy, INK, 2)
    s += text(nx1 - 18, 262, "C₁", 12.5, GREEN, "end", "bold")

    s += line(nx2, iy, nx2, 240, INK, 2)
    s += _cap_v(nx2, 256, 7, 14, GREEN)
    s += line(nx2, 270, nx2, gy, INK, 2)
    s += text(nx2 + 18, 262, "C₂", 12.5, GREEN, "start", "bold")

    # шина землі
    s += line(nx1, gy, nx2, gy, INK, 2)
    s += line(335, gy, 385, gy, INK, 2.4)
    s += line(345, gy + 6, 375, gy + 6, INK, 2)
    s += line(353, gy + 11, 367, gy + 11, INK, 2)
    s += text(360, gy + 30, "GND", 11, GREY, "middle")
    return W, H, s


def fig_5_2_load_cap():
    """Навантажувальна ємність CL = (C1·C2)/(C1+C2) + Cstray і зсув частоти."""
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 26, "Навантажувальна ємність CL і підстроювання частоти", 15.5, INK, "middle", "bold")

    # ліворуч — формула CL як послідовне з'єднання
    s += _frame(40, 56, 300, 250, "Що «бачить» кварц")
    cx = 150
    s += _crystal_sym(cx, 110, INK)
    s += line(cx - 28, 110, 70, 110, INK, 2)
    s += line(cx + 28, 110, 230, 110, INK, 2)
    # C1, C2 вниз
    s += line(70, 110, 70, 170, INK, 2)
    s += _cap_v(70, 184, 6, 12, GREEN)
    s += line(70, 196, 70, 250, INK, 2)
    s += text(54, 190, "C₁", 11.5, GREEN, "end", "bold")
    s += line(230, 110, 230, 170, INK, 2)
    s += _cap_v(230, 184, 6, 12, GREEN)
    s += line(230, 196, 230, 250, INK, 2)
    s += text(246, 190, "C₂", 11.5, GREEN, "start", "bold")
    s += line(70, 250, 230, 250, INK, 2)
    s += text(150, 272, "CL = C₁·C₂/(C₁+C₂) + Cпар", 12, INK, "middle", "bold")
    s += text(150, 290, "(Cпар — паразитна ємність доріжок і ніжок)", 10.5, GREY, "middle")

    # праворуч — частота від CL: монотонно спадає між fs і fp
    ax, ay, aw, ah = 410, 270, 230, 170
    s += _axes(ax, ay, aw, ah, "CL", "f")
    pts = []
    for i in range(0, 231):
        cl = i / 230
        # f між fp (мала CL) і fs (велика CL)
        y = ay - ah * (0.25 + 0.6 * math.exp(-cl * 2.6))
        pts.append((ax + i, y))
    s += _poly(pts, BLUE, 2.6)
    s += line(ax, ay - ah * 0.85, ax + aw, ay - ah * 0.85, GREEN, 1.2, "4 4")
    s += text(ax + aw, ay - ah * 0.85 - 4, "fp", 11, GREEN, "end")
    s += line(ax, ay - ah * 0.25, ax + aw, ay - ah * 0.25, RED, 1.2, "4 4")
    s += text(ax + aw, ay - ah * 0.25 - 4, "fs", 11, RED, "end")
    s += text(ax + aw * 0.5, ay - ah - 4, "↑ CL  →  ↓ f", 12, INK, "middle", "bold")
    s += text(ax + aw * 0.5, ay + 40, "Маленька зміна CL «тягне» частоту на одиниці ppm.", 10.5, GREY, "middle")
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.6  Точність у ppm
# ─────────────────────────────────────────────────────────────────────────────

def fig_6_1_ppm_to_seconds():
    """Шкала: ppm → секунди на добу/рік."""
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 26, "Що означає ppm у реальному часі", 16, INK, "middle", "bold")

    rows = [
        ("±100 ppm", "дешевий кварц / RC", "≈ 8.6 с/добу", "≈ 53 хв/рік", RED),
        ("±20 ppm", "звичайний кварц плати", "≈ 1.7 с/добу", "≈ 10.5 хв/рік", SUN),
        ("±5 ppm", "хороший годинниковий", "≈ 0.43 с/добу", "≈ 2.6 хв/рік", GREEN),
        ("±0.5 ppm", "TCXO", "≈ 43 мс/добу", "≈ 16 с/рік", BLUE),
    ]
    x0, y0 = 60, 70
    cw = [150, 220, 160, 140]
    heads = ["Допуск", "Тип джерела", "Похибка за добу", "Похибка за рік"]
    cx = x0
    for hh, ww in zip(heads, cw):
        s += text(cx + ww / 2, y0, hh, 12.5, INK, "middle", "bold")
        cx += ww
    s += line(x0, y0 + 10, x0 + sum(cw), y0 + 10, INK, 1.6)

    y = y0 + 28
    for tol, typ, day, year, col in rows:
        s += rect(x0 - 6, y - 18, sum(cw) + 12, 44, "#fbfbfb", FAINT, 1, 6)
        cx = x0
        vals = [tol, typ, day, year]
        for i, v in enumerate(vals):
            c = col if i == 0 else INK
            wgt = "bold" if i == 0 else "normal"
            s += text(cx + cw[i] / 2, y + 6, v, 13 if i == 0 else 12.5, c, "middle", wgt)
            cx += cw[i]
        y += 54
    s += text(W / 2, y + 4, "1 ppm = 10⁻⁶ = 1 частина з мільйона. ±X ppm на 86 400 с/добу = ±0.0864·X секунд.",
              11.5, GREY, "middle")
    return W, H, s


def fig_6_2_tempco_aging():
    """Дві криві: температурна парабола AT-зрізу і повільне старіння."""
    W, H = 720, 350
    s = header(W, H)
    s += text(W / 2, 26, "Дві причини дрейфу: температура (швидко) і старіння (повільно)", 15, INK, "middle", "bold")

    # ── ліворуч: температурна крива AT-зрізу (кубічна) ──
    ox, oy, w, h = 80, 230, 250, 170
    s += _axes(ox, oy - h / 2, w, h / 2, "T, °C", "Δf, ppm")
    # вісь нуля посередині
    yz = oy - h / 2
    s += line(ox, yz, ox + w, yz, GREY, 1.2, "3 3")
    s += line(ox - 4, yz - h / 2 + 10, ox - 4, yz - h / 2 + 10, GREY, 1)
    s += text(ox - 8, yz + 4, "0", 11, GREY, "end")
    s += text(ox - 8, yz - h * 0.42, "+", 12, INK, "end")
    s += text(ox - 8, yz + h * 0.42, "−", 12, INK, "end")
    # кубічна крива з точкою перегину ~25°C
    pts = []
    for i in range(0, 251):
        Tn = (i / 250) * 100 - 30      # -30..70 °C
        x = (Tn + 30) / 100
        df = 0.000018 * (Tn - 25) ** 3   # ppm
        y = yz - df * 6
        y = max(yz - h * 0.46, min(yz + h * 0.46, y))
        pts.append((ox + w * x, y))
    s += _poly(pts, BLUE, 2.6)
    s += text(ox + w * 0.5, oy + 22, "AT-зріз: S-крива", 12, BLUE, "middle", "bold")
    s += text(ox + w * 0.5, oy + 40, "плаский ≈ при кімнатній T", 10.5, GREY, "middle")

    # ── праворуч: старіння — логарифмічний дрейф у часі ──
    ax, ay, aw, ah = 420, 230, 230, 170
    s += _axes(ax, ay, aw, ah, "роки", "Δf, ppm")
    pts = []
    for i in range(0, 231):
        t = i / 230 * 10  # роки
        df = 3.0 * math.log10(1 + t * 1.2)
        y = ay - df * (ah / 6)
        pts.append((ax + aw * (t / 10), y))
    s += _poly(pts, COPP, 2.6)
    s += text(ax + aw * 0.5, ay - ah - 4, "≈ кілька ppm за перший рік", 11, COPP, "middle", "bold")
    s += text(ax + aw * 0.5, ay + 22, "Старіння: швидке спершу,", 11, GREY, "middle")
    s += text(ax + aw * 0.5, ay + 38, "потім дедалі повільніше", 11, GREY, "middle")
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.7  Годинниковий кварц 32768 Гц і RTC
# ─────────────────────────────────────────────────────────────────────────────

def fig_7_1_divide_chain():
    """32768 Гц → дільник на 2 п'ятнадцять разів → 1 Гц."""
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 26, "Чому саме 32768 = 2¹⁵: п'ятнадцять поділів навпіл дають рівно 1 Гц", 14.5, INK, "middle", "bold")

    # кварц
    s += _crystal_sym(90, 150, INK)
    s += text(90, 110, "32768 Гц", 13, INK, "middle", "bold")
    s += text(90, 200, "камертон", 11, GREY, "middle")
    s += arrow(120, 150, 175, 150, INK, 2)

    # ланцюжок тригерів ÷2
    x = 185
    freq = 32768
    for i in range(5):
        s += rect(x, 128, 54, 44, LBLUE, BLUE, 1.6, 6)
        s += text(x + 27, 154, "÷2", 13, INK, "middle", "bold")
        x += 70
        if i < 4:
            s += arrow(x - 16, 150, x, 150, INK, 1.8)
    # три крапки
    s += text(x + 6, 154, "· · ·", 18, GREY, "start", "bold")
    s += arrow(x + 40, 150, x + 70, 150, INK, 1.8)
    # фінальний
    s += rect(x + 70, 128, 54, 44, LGRN, GREEN, 1.8, 6)
    s += text(x + 97, 154, "÷2", 13, INK, "middle", "bold")
    s += text(x + 97, 118, "15-й", 10.5, GREY, "middle")
    s += arrow(x + 124, 150, x + 160, 150, GREEN, 2.2)
    s += text(x + 168, 154, "1 Гц", 14, GREEN, "start", "bold")
    s += text(x + 168, 174, "(секунда)", 10.5, GREY, "start")

    # підпис під ланцюжком
    s += rect(150, 224, 460, 30, LSUN, SUN, 1.4, 6)
    s += text(380, 244, "32768 ÷ 2¹⁵ = 1.000000 — рівно одна секунда, без округлень.", 12, INK, "middle")
    return W, H, s


def fig_7_2_rtc_power():
    """Окреме живлення RTC від батарейки через діод-розв'язку (Vbat)."""
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 26, "Окреме живлення годинника: RTC цокає навіть із вимкненою платою", 14.5, INK, "middle", "bold")

    # основне живлення
    s += rect(50, 90, 110, 50, LRED, RED, 1.8, 8)
    s += text(105, 112, "Живлення", 12.5, INK, "middle", "bold")
    s += text(105, 130, "плати 3.3 В", 11, GREY, "middle")
    # діод до вузла Vrtc
    s += line(160, 115, 210, 115, INK, 2)
    s += _diode_to(230, 115, INK)
    s += line(250, 115, 330, 115, INK, 2)

    # батарейка
    s += rect(50, 200, 110, 50, LBLUE, BLUE, 1.8, 8)
    s += text(105, 222, "Батарейка", 12.5, INK, "middle", "bold")
    s += text(105, 240, "CR2032", 11, GREY, "middle")
    s += line(160, 225, 210, 225, INK, 2)
    s += _diode_to(230, 225, INK)
    s += line(250, 225, 330, 225, INK, 2)

    # вузол Vrtc
    s += line(330, 115, 330, 225, INK, 2)
    s += circle(330, 170, 3.5, INK, INK)
    s += line(330, 170, 380, 170, INK, 2)
    s += text(338, 162, "V_RTC (хто вищий — той живить)", 11, GREY if False else GREY, "start")

    # блок RTC
    s += rect(380, 120, 200, 110, LGRN, GREEN, 2, 10)
    s += text(480, 146, "RTC-домен", 13.5, INK, "middle", "bold")
    s += text(480, 168, "лічильник часу + дільник", 11, GREY, "middle")
    # маленький кварц всередині
    s += _crystal_sym(440, 200, INK)
    s += text(508, 204, "32768 Гц", 11.5, INK, "start")

    s += text(W / 2, 290, "Діоди-розв'язки дають живлення з того входу, де напруга вища; батарея тримає лише крихітний RTC-домен.",
              11, GREY, "middle")
    return W, H, s


def _diode_to(cx, cy, col=INK, right=True):
    size = 11
    if right:
        t = f'<path d="M {cx-size},{cy-size} L {cx-size},{cy+size} L {cx+size*0.8:.1f},{cy} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
        t += line(cx + size * 0.8, cy - size, cx + size * 0.8, cy + size, col, 2.4)
    else:
        t = f'<path d="M {cx+size},{cy-size} L {cx+size},{cy+size} L {cx-size*0.8:.1f},{cy} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
        t += line(cx - size * 0.8, cy - size, cx - size * 0.8, cy + size, col, 2.4)
    return t


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.8  Керамічні резонатори й MEMS
# ─────────────────────────────────────────────────────────────────────────────

def fig_8_1_three_technologies():
    """Порівняння: кварц, керамічний резонатор, MEMS — точність vs міцність."""
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 26, "Три технології резонаторів: за що платимо", 16, INK, "middle", "bold")

    cards = [
        ("Кварцовий", BLUE, LBLUE, ["точність ±10…30 ppm", "Q дуже висока", "крихкий до ударів", "повільний старт"]),
        ("Керамічний", COPP, LSUN, ["точність ±0.1…0.5 %", "вбудовані конденсатори", "дешевий, 3 виводи", "де ppm не критичні"]),
        ("MEMS", GREEN, LGRN, ["точність до ±0.5 ppm", "ударостійкий", "швидкий старт", "програмована частота"]),
    ]
    x0 = 40
    cw = 213
    gap = 14
    for i, (name, col, lcol, items) in enumerate(cards):
        x = x0 + i * (cw + gap)
        s += rect(x, 56, cw, 270, lcol, col, 2, 10)
        s += rect(x, 56, cw, 36, col, col, 0, 10)
        s += text(x + cw / 2, 80, name, 15, "#ffffff", "middle", "bold")
        yy = 120
        for it in items:
            s += circle(x + 22, yy - 4, 3, col, col)
            s += text(x + 36, yy, it, 12, INK, "start")
            yy += 34
        # маленький значок
        if name == "MEMS":
            s += text(x + cw / 2, 300, "кремнієва балка під кришкою", 10.5, GREY, "middle")
        elif name == "Кварцовий":
            s += text(x + cw / 2, 300, "механічний дзвін кристала", 10.5, GREY, "middle")
        else:
            s += text(x + cw / 2, 300, "п'єзокераміка, не монокристал", 10.5, GREY, "middle")
    return W, H, s


def fig_8_2_jitter_phase_noise():
    """Джиттер у часовій області: чистий край vs тремтливий."""
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 26, "Джиттер: фронти такту «тремтять» у часі", 15.5, INK, "middle", "bold")

    ox, oy, w = 70, 130, 560
    # ідеальні межі
    nper = 8
    pw = w / nper
    for i in range(nper + 1):
        s += line(ox + i * pw, oy - 40, ox + i * pw, oy + 150, FAINT, 1.2, "4 4")

    # верх: чистий
    y1 = oy
    s += text(ox, y1 - 50, "Низький джиттер: кожен фронт точно на межі", 12.5, GREEN, "start", "bold")
    pts = []
    x = ox
    for i in range(nper):
        yy = y1 - 28 if i % 2 == 0 else y1
        pts.append((x, yy)); pts.append((x + pw, yy))
        x += pw
    s += _poly(pts, GREEN, 2.4)

    # низ: тремтливий (зсунуті фронти)
    import random
    random.seed(7)
    y2 = oy + 110
    s += text(ox, y2 - 22, "Високий джиттер: фронти «гуляють» — приймач помиляється з моментом", 12.5, RED, "start", "bold")
    pts = []
    x = ox
    for i in range(nper):
        j = (random.random() - 0.5) * pw * 0.5
        yy = y2 - 28 if i % 2 == 0 else y2
        nx = x + j
        pts.append((nx, yy))
        pts.append((nx + pw, yy))
        x += pw
    s += _poly(pts, RED, 2.4)
    # стрілки тремтіння
    for i in range(1, nper, 2):
        bx = ox + i * pw
        s += arrow(bx - 10, y2 + 32, bx + 10, y2 + 32, RED, 1.6)
        s += arrow(bx + 10, y2 + 32, bx - 10, y2 + 32, RED, 1.6)
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
# 2.10.9  TCXO та OCXO — піраміда точності
# ─────────────────────────────────────────────────────────────────────────────

def fig_9_1_accuracy_pyramid():
    """Піраміда точності джерел частоти."""
    W, H = 720, 400
    s = header(W, H)
    s += text(W / 2, 26, "Піраміда точності: що дорожче — то стабільніша частота", 15.5, INK, "middle", "bold")

    levels = [
        ("Атомний (рубідій, цезій)", "±0.001 ppb і краще", "еталони, базові станції", RED, 120),
        ("OCXO — кварц у термостаті", "±1…20 ppb", "радіо, метрологія", SUN, 200),
        ("TCXO — з компенсацією T", "±0.1…2 ppm", "GPS, рації, модеми", GREEN, 300),
        ("Простий кварц (XO)", "±10…50 ppm", "МК, UART, USB", BLUE, 420),
        ("RC-генератор у чипі", "±1…5 %", "де час не критичний", GREY, 560),
    ]
    cx = W / 2
    yTop = 60
    rowh = 60
    for i, (name, acc, use, col, wbar) in enumerate(levels):
        y = yTop + i * rowh
        s += _fillpoly([(cx - wbar / 2, y), (cx + wbar / 2, y),
                        (cx + wbar / 2, y + rowh - 12), (cx - wbar / 2, y + rowh - 12)],
                       _light(col), col, 2)
        s += text(cx, y + 22, name, 12.5, INK, "middle", "bold")
        s += text(cx, y + 40, acc + "   ·   " + use, 11, GREY, "middle")

    s += arrow(60, yTop + 4, 60, yTop + 4 * rowh + 30, INK, 2)
    s += text(48, yTop + 2 * rowh, "точність ↑", 12, INK, "middle", "bold")
    return W, H, s


def _light(col):
    m = {RED: LRED, SUN: LSUN, GREEN: LGRN, BLUE: LBLUE, GREY: "#f0f0f0"}
    return m.get(col, "#f4f4f4")


def fig_9_2_tcxo_block():
    """Блок-схема TCXO: давач T → корекція → керована ємність → кварц."""
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 26, "TCXO зсередини: схема міряє температуру і підправляє частоту", 14.5, INK, "middle", "bold")

    # кварц + генератор
    s += rect(70, 120, 130, 80, LBLUE, BLUE, 2, 10)
    s += _crystal_sym(110, 160, INK)
    s += text(160, 150, "генератор", 11, INK, "start", "bold")
    s += text(160, 168, "П'єрса", 11, GREY, "start")
    s += arrow(200, 160, 250, 160, INK, 2)
    s += rect(250, 130, 100, 60, LGRN, GREEN, 2, 8)
    s += text(300, 156, "вихід", 12.5, INK, "middle", "bold")
    s += text(300, 174, "f точна", 10.5, GREY, "middle")
    s += arrow(350, 160, 410, 160, GREEN, 2.2)
    s += text(420, 164, "до системи", 11.5, INK, "start")

    # давач температури
    s += rect(70, 240, 130, 50, LSUN, SUN, 1.8, 8)
    s += text(135, 262, "давач T", 12.5, INK, "middle", "bold")
    s += text(135, 280, "у тому ж корпусі", 10, GREY, "middle")
    s += arrow(200, 265, 250, 265, INK, 2)
    # корекційна функція
    s += rect(250, 235, 160, 60, "#ffffff", INK, 1.8, 8)
    s += text(330, 256, "корекція f(T)", 12, INK, "middle", "bold")
    s += text(330, 274, "поліном / таблиця", 10, GREY, "middle")
    # корекція тягне керовану ємність (варікап) назад у генератор
    s += line(410, 265, 460, 265, INK, 2)
    s += line(460, 215, 460, 265, INK, 2)
    s += arrow(460, 215, 130, 215, INK, 1.8, "5 4")
    s += line(130, 200, 130, 215, INK, 2)
    s += text(300, 208, "підстроює навантажувальну ємність CL", 10.5, INK, "middle")
    return W, H, s


# ─────────────────────────────────────────────────────────────────────────────
ALL = [
    ("fig-2-10-1-1-clock-fanout.svg", fig_1_1_what_clock_drives),
    ("fig-2-10-1-2-rc-vs-crystal-drift.svg", fig_1_2_rc_vs_crystal_drift),
    ("fig-2-10-2-1-piezo-direct-inverse.svg", fig_2_1_piezo_direct_inverse),
    ("fig-2-10-2-2-resonance-pump.svg", fig_2_2_resonance_pump),
    ("fig-2-10-3-1-quartz-cut.svg", fig_3_1_quartz_cut),
    ("fig-2-10-3-2-q-decay.svg", fig_3_2_q_decay),
    ("fig-2-10-3-3-resonance-sharpness.svg", fig_3_3_resonance_sharpness),
    ("fig-2-10-4-1-bvd-model.svg", fig_4_1_bvd_model),
    ("fig-2-10-4-2-two-resonances.svg", fig_4_2_two_resonances),
    ("fig-2-10-5-1-pierce-schematic.svg", fig_5_1_pierce_schematic),
    ("fig-2-10-5-2-load-cap.svg", fig_5_2_load_cap),
    ("fig-2-10-6-1-ppm-to-seconds.svg", fig_6_1_ppm_to_seconds),
    ("fig-2-10-6-2-tempco-aging.svg", fig_6_2_tempco_aging),
    ("fig-2-10-7-1-divide-chain.svg", fig_7_1_divide_chain),
    ("fig-2-10-7-2-rtc-power.svg", fig_7_2_rtc_power),
    ("fig-2-10-8-1-three-technologies.svg", fig_8_1_three_technologies),
    ("fig-2-10-8-2-jitter.svg", fig_8_2_jitter_phase_noise),
    ("fig-2-10-9-1-accuracy-pyramid.svg", fig_9_1_accuracy_pyramid),
    ("fig-2-10-9-2-tcxo-block.svg", fig_9_2_tcxo_block),
]


def main():
    for name, fn in ALL:
        w, h, body = fn()
        save(name, body)
    print(f"done: {len(ALL)} figures")


if __name__ == "__main__":
    main()
