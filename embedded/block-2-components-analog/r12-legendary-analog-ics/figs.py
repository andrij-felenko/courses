# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 2.12 — «Легендарні аналогові ІМС» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи посекційно (Рис. 2.12.T.k).
Імена файлів: fig-2-12-T-k-<slug>.svg. Допоміжні функції скопійовано з
попередніх розділів модуля для єдиного вигляду.
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


def dot(cx, cy, r=3.6, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


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


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


def _cap_h(cx, cy, gap=7, plate=13, col=INK):
    return (line(cx - gap, cy - plate, cx - gap, cy + plate, col, 2.4)
            + line(cx + gap, cy - plate, cx + gap, cy + plate, col, 2.4))


def _cap_v(cx, cy, gap=7, plate=13, col=INK):
    return (line(cx - plate, cy - gap, cx + plate, cy - gap, col, 2.4)
            + line(cx - plate, cy + gap, cx + plate, cy + gap, col, 2.4))


def _res_h(cx, cy, length=46, h=10, col=INK, w=2):
    """Зигзаг-резистор (горизонтальний)."""
    x0 = cx - length / 2
    n = 6
    dx = length / n
    pts = [(x0, cy)]
    for i in range(n):
        xx = x0 + dx * (i + 0.5)
        pts.append((xx, cy - h if i % 2 == 0 else cy + h))
    pts.append((x0 + length, cy))
    return _poly(pts, col, w)


def _res_v(cx, cy, length=46, hh=10, col=INK, w=2):
    y0 = cy - length / 2
    n = 6
    dy = length / n
    pts = [(cx, y0)]
    for i in range(n):
        yy = y0 + dy * (i + 0.5)
        pts.append((cx - hh if i % 2 == 0 else cx + hh, yy))
    pts.append((cx, y0 + length))
    return _poly(pts, col, w)


def _opamp(cx, cy, w=70, h=64, plus_top=False, label=""):
    """Трикутник ОП. plus_top=True → '+' згори. Повертає рядок і словник пінів."""
    t = f'<path d="M {cx-w/2:.0f},{cy-h/2:.0f} L {cx-w/2:.0f},{cy+h/2:.0f} L {cx+w/2:.0f},{cy:.0f} Z" fill="#fbfbfb" stroke="{INK}" stroke-width="1.8"/>\n'
    yt, yb = cy - h / 4, cy + h / 4
    if plus_top:
        t += text(cx - w / 2 + 12, yt + 5, "+", 13, RED, "middle", "bold")
        t += text(cx - w / 2 + 12, yb + 5, "−", 15, BLUE, "middle", "bold")
        pins = {"in_top": (cx - w / 2, yt), "in_bot": (cx - w / 2, yb)}
    else:
        t += text(cx - w / 2 + 12, yt + 5, "−", 15, BLUE, "middle", "bold")
        t += text(cx - w / 2 + 12, yb + 5, "+", 13, RED, "middle", "bold")
        pins = {"in_top": (cx - w / 2, yt), "in_bot": (cx - w / 2, yb)}
    pins["out"] = (cx + w / 2, cy)
    if label:
        t += text(cx - 6, cy + 5, label, 12, GREY, "middle", "bold")
    return t, pins


def _comp(cx, cy, w=62, h=58, plus_top=True, label="cmp"):
    """Компаратор — той самий трикутник, але з підписом."""
    t, pins = _opamp(cx, cy, w, h, plus_top, label)
    return t, pins


def _gnd(cx, cy, col=INK):
    return (line(cx, cy, cx, cy + 10, col, 2)
            + line(cx - 12, cy + 10, cx + 12, cy + 10, col, 2)
            + line(cx - 7, cy + 15, cx + 7, cy + 15, col, 2)
            + line(cx - 3, cy + 20, cx + 3, cy + 20, col, 2))


def _vdd(cx, cy, txt="+Vcc", col=RED):
    return (line(cx, cy, cx, cy - 12, col, 2)
            + line(cx - 11, cy - 12, cx + 11, cy - 12, col, 2.4)
            + text(cx, cy - 18, txt, 12, col, "middle", "bold"))


def _frame(x, y, w, h, title="", col="#c9d3dc"):
    s = rect(x, y, w, h, "#ffffff", col, 1.4, 8)
    if title:
        s += text(x + w / 2, y - 7, title, 12.5, INK, "middle", "bold")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  2.12.1 — Чому деякі мікросхеми живуть 50 років
# ════════════════════════════════════════════════════════════════════════════

def fig_1_1_timeline():
    """Лінія часу: легендарні аналогові ІМС, що випускають десятиліттями."""
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 30, "Аналогові цеглинки, які пережили свою епоху",
              17, INK, "middle", "bold")
    ox, oy = 70, 270
    axw = 630
    s += line(ox, oy, ox + axw, oy, INK, 2.5)
    s += arrow(ox + axw, oy, ox + axw + 14, oy, INK, 2.5)
    # роки 1965..2025
    y0, y1 = 1965, 2025
    def xof(y):
        return ox + axw * (y - y0) / (y1 - y0)
    for yr in range(1965, 2026, 10):
        x = xof(yr)
        s += line(x, oy, x, oy + 6, INK, 2)
        s += text(x, oy + 22, str(yr), 12, INK, "middle")
    s += text(ox + axw + 6, oy + 22, "рік", 12, GREY, "middle")
    # бруски: (назва, рік народження, рядок)
    bars = [
        ("741 — операційний підсилювач", 1968, 0, RED),
        ("555 — таймер", 1971, 1, BLUE),
        ("78xx — лінійний стабілізатор", 1972, 2, GREEN),
        ("LM358 — здвоєний ОП", 1976, 0, RED),
        ("TL431 — опорна напруга", 1978, 1, BLUE),
        ("4051/4066 — аналогові ключі", 1975, 2, GREEN),
    ]
    rowy = {0: 70, 1: 120, 2: 170}
    for name, born, row, col in bars:
        y = rowy[row]
        x = xof(born)
        s += line(x, y + 9, x, oy, col, 1.2, "3 4")
        s += rect(x, y, (ox + axw) - x, 20, _tint(col), col, 1.5, 4)
        s += text(x + 8, y + 14, name, 12, INK, "start", "bold")
        s += text(x - 6, y + 14, "▶", 11, col, "end")
    s += text(ox + axw, 220, "досі у виробництві →", 12.5, GREY, "end", "bold")
    return s


def _tint(col):
    return {RED: LRED, BLUE: LBLUE, GREEN: LGRN, SUN: LSUN}.get(col, "#f0f2f5")


def fig_1_2_second_source():
    """Друге джерело постачання: один чип — багато виробників."""
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 30, "Друге джерело: одна цоколівка — багато виробників",
              16.5, INK, "middle", "bold")
    # центральний «стандарт»
    cx, cy = 360, 175
    s += rect(cx - 80, cy - 38, 160, 76, LSUN, SUN, 2, 10)
    s += text(cx, cy - 8, "Стандарт «555»", 14, INK, "middle", "bold")
    s += text(cx, cy + 13, "8 ніжок, та сама логіка", 11.5, GREY, "middle")
    # виробники
    makers = [
        ("Signetics\n(оригінал, 1971)", 150, 90),
        ("Texas\nInstruments", 150, 260),
        ("STMicro-\nelectronics", 570, 90),
        ("ON Semi /\nNXP / …", 570, 260),
    ]
    for nm, mx, my in makers:
        s += rect(mx - 78, my - 28, 156, 56, "#ffffff", INK, 1.6, 8)
        lines = nm.split("\n")
        for i, ln in enumerate(lines):
            s += text(mx, my - 6 + i * 17, ln, 12, INK, "middle",
                      "bold" if i == 0 else "normal")
        # стрілка до центру
        s += arrow(mx + (78 if mx < cx else -78), my,
                   cx + (-82 if mx < cx else 82), cy + (-20 if my < cy else 20),
                   GREEN, 2)
    s += text(W / 2, H - 16,
              "Зник один постачальник — паяєш чужий тієї самої цоколівки. Ціна не диктується монополістом.",
              12, GREEN, "middle", "bold")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  2.12.2 — Таймер 555 зсередини
# ════════════════════════════════════════════════════════════════════════════

def fig_2_1_block():
    """Блок-схема 555: дільник 3×5к, два компаратори, RS-тригер, розряд."""
    W, H = 820, 500
    s = header(W, H)
    s += text(W / 2, 30, "Таймер 555 зсередини", 17, INK, "middle", "bold")
    # рамка кристала
    L, T, R, B = 150, 60, 740, 430
    s += rect(L - 10, T - 5, (R - L) + 70, (B - T) + 30, "#fcfdff", "#c9d3dc", 1.6, 10)
    # +Vcc шина згори, GND знизу
    s += line(L, T, R, T, RED, 2.2)
    s += dot(L, T, 3, RED); s += text(L - 8, T - 8, "+Vcc (8)", 12, RED, "end", "bold")
    s += line(L, B, R, B, INK, 2.2)
    s += dot(L, B, 3); s += text(L - 8, B + 16, "GND (1)", 12, INK, "end", "bold")

    # ── дільник трьох резисторів 5 кОм (вертикально, зліва) ──
    rx = L
    segs = [(T, 150), (150, 250), (250, B)]
    for (ya, yb) in segs:
        mid = (ya + yb) / 2
        s += line(rx, ya, rx, mid - (yb - ya) * 0.32, INK, 2)
        s += _res_v(rx, mid, length=(yb - ya) * 0.6, hh=8)
        s += line(rx, mid + (yb - ya) * 0.32, rx, yb, INK, 2)
        s += text(rx + 14, mid + 4, "5 кΩ", 11, INK, "start")
    # вузли порогів
    s += dot(rx, 150, 4, RED); s += text(rx + 14, 150 - 8, "⅔Vcc", 11.5, RED, "start", "bold")
    s += dot(rx, 250, 4, BLUE); s += text(rx + 14, 250 + 16, "⅓Vcc", 11.5, BLUE, "start", "bold")
    # CTRL(5) — відведення від вузла ⅔
    s += line(rx, 150, rx - 40, 150, RED, 1.5, "3 4")
    s += dot(rx - 40, 150, 3, RED); s += text(rx - 44, 154, "CTRL (5)", 10.5, GREY, "end")

    # ── два компаратори ──
    c1x, c1y = 330, 150     # верхній: поріг (THRESH)
    c2x, c2y = 330, 300     # нижній: запуск (TRIG)
    t1, p1 = _comp(c1x, c1y, 72, 62, plus_top=True, label="C1")   # «+» згори, «−» знизу
    t2, p2 = _comp(c2x, c2y, 72, 62, plus_top=False, label="C2")  # «−» згори, «+» знизу
    s += t1 + t2
    # ⅔Vcc → «−» C1 (нижній вхід C1)
    s += line(rx, 150, 250, 150, RED, 2)
    s += line(250, 150, 250, p1["in_bot"][1], RED, 2)
    s += line(250, p1["in_bot"][1], p1["in_bot"][0], p1["in_bot"][1], RED, 2)
    # THRESH(6) → «+» C1 (верхній вхід C1) — заходить з лівого краю поверх дільника
    s += line(L - 10, 95, 285, 95, INK, 2)
    s += line(285, 95, 285, p1["in_top"][1], INK, 2)
    s += line(285, p1["in_top"][1], p1["in_top"][0], p1["in_top"][1], INK, 2)
    s += dot(L - 10, 95, 3); s += text(L - 14, 99, "THRESH (6)", 10.5, GREY, "end", "bold")
    # ⅓Vcc → «−» C2 (верхній вхід C2)
    s += line(rx, 250, 230, 250, BLUE, 2)
    s += line(230, 250, 230, p2["in_top"][1], BLUE, 2)
    s += line(230, p2["in_top"][1], p2["in_top"][0], p2["in_top"][1], BLUE, 2)
    # TRIG(2) → «+» C2 (нижній вхід C2)
    s += line(L - 10, 360, 285, 360, INK, 2)
    s += line(285, 360, 285, p2["in_bot"][1], INK, 2)
    s += line(285, p2["in_bot"][1], p2["in_bot"][0], p2["in_bot"][1], INK, 2)
    s += dot(L - 10, 360, 3); s += text(L - 14, 364, "TRIG (2)", 10.5, GREY, "end", "bold")

    # ── RS-тригер ──
    fx, fy, fw, fh = 470, 225, 120, 130
    s += rect(fx, fy - fh / 2, fw, fh, "#f4f7fb", INK, 1.8, 8)
    s += text(fx + fw / 2, fy - fh / 2 + 22, "RS-тригер", 12.5, INK, "middle", "bold")
    s += text(fx + 14, fy - 18, "R", 14, INK, "start", "bold")
    s += text(fx + 14, fy + 30, "S", 14, INK, "start", "bold")
    s += text(fx + fw - 14, fy + 5, "Q", 14, INK, "end", "bold")
    s += arrow(p1["out"][0], 150, fx, fy - 24, INK, 2)      # C1 → R
    s += arrow(p2["out"][0], 300, fx, fy + 24, INK, 2)      # C2 → S

    # ── вихідний буфер ──
    obx = 640
    s += line(fx + fw, fy, obx - 26, fy, INK, 2.4)
    t3, p3 = _comp(obx, fy, 52, 46, plus_top=True, label="")
    s += t3
    s += text(obx - 8, fy + 5, "буфер", 9.5, GREY, "middle")
    s += line(p3["out"][0], fy, R + 20, fy, INK, 2.4)
    s += dot(R, fy, 3); s += text(R + 24, fy + 4, "OUT (3)", 12, INK, "start", "bold")

    # ── розрядний транзистор (відведення від Q) ──
    dgx = 560
    s += line(fx + fw / 2, fy + fh / 2, fx + fw / 2, 380, INK, 2)   # Q-low → база
    s += line(fx + fw / 2, 380, dgx - 22, 380, INK, 2)
    s += line(dgx, 360, dgx, 410, INK, 3)                           # вертикаль транзистора
    s += line(dgx - 22, 380, dgx, 380, INK, 2)                      # база
    s += line(dgx, 368, dgx + 24, 350, INK, 2) + line(dgx + 24, 350, dgx + 24, 320, INK, 2)  # колектор
    s += line(dgx, 392, dgx + 24, 410, INK, 2) + line(dgx + 24, 410, dgx + 24, B, INK, 2)    # емітер→GND
    s += arrow(dgx + 8, 398, dgx + 22, 408, INK, 1.8)
    s += line(dgx + 24, 320, R + 20, 320, INK, 2)
    s += dot(R, 320, 3); s += text(R + 24, 324, "DISCH (7)", 12, INK, "start", "bold")
    s += text(dgx + 32, 396, "розряд", 10, GREY, "start")
    # RESET(4) — згадка
    s += text(fx + fw / 2, fy - fh / 2 - 10, "RESET (4) → скидання Q", 10, GREY, "middle")
    return s


def fig_2_2_thresholds():
    """Дві опорні лінії ⅓ і ⅔ Vcc від дільника однакових резисторів."""
    W, H = 560, 300
    s = header(W, H)
    s += text(W / 2, 28, "Дільник із трьох однакових резисторів", 15.5, INK, "middle", "bold")
    x = 150
    top, bot = 60, 250
    s += _vdd(x, top, "+Vcc")
    s += line(x, top, x, bot, FAINT, 1.2)
    # три резистори
    seg = (bot - top) / 3
    labels = [("⅔Vcc", RED), ("⅓Vcc", BLUE)]
    for i in range(3):
        ya = top + seg * i
        s += _res_v(x, ya + seg / 2, length=seg * 0.6, hh=9)
        s += line(x, ya, x, ya + seg * 0.2, INK, 2)
        s += line(x, ya + seg * 0.8, x, ya + seg, INK, 2)
    s += _gnd(x, bot)
    # вузли
    n1 = top + seg      # ⅔
    n2 = top + 2 * seg  # ⅓
    s += dot(x, n1, 4, RED); s += dot(x, n2, 4, BLUE)
    s += arrow(x, n1, 360, n1, RED, 2)
    s += text(366, n1 + 4, "⅔ Vcc → на компаратор C1 (поріг)", 12.5, RED, "start", "bold")
    s += arrow(x, n2, 360, n2, BLUE, 2)
    s += text(366, n2 + 4, "⅓ Vcc → на компаратор C2 (запуск)", 12.5, BLUE, "start", "bold")
    s += text(x, bot + 34, "три «5» → 555 (за легендою)", 12, GREY, "middle", "italic")
    s += text(366, n1 - 26,
              "Однакові резистори → пороги не залежать", 11.5, GREY, "start")
    s += text(366, n1 - 12,
              "від абсолютного Vcc, лише від його часток.", 11.5, GREY, "start")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  2.12.3 — Астабільний режим
# ════════════════════════════════════════════════════════════════════════════

def fig_3_1_astable_circuit():
    """Схема астабільного 555: Ra, Rb, C і ниточки до THRESH/TRIG/DISCH."""
    W, H = 640, 430
    s = header(W, H)
    s += text(W / 2, 28, "555 в астабільному режимі", 16.5, INK, "middle", "bold")
    # корпус
    bx, by, bw, bh = 230, 90, 170, 250
    s += rect(bx, by, bw, bh, "#fbfbfb", INK, 1.8, 8)
    s += text(bx + bw / 2, by + bh / 2, "555", 18, INK, "middle", "bold")
    # піни (зліва TRIG2, THRESH6; справа DISCH7); зверху Vcc8, RESET4; знизу GND1
    pin = {
        "trig": (bx, by + 150, "TRIG 2"),
        "thr":  (bx, by + 195, "THR 6"),
        "disch":(bx + bw, by + 60, "DIS 7"),
        "out":  (bx + bw, by + 150, "OUT 3"),
        "vcc":  (bx + 40, by, "Vcc 8"),
        "rst":  (bx + 130, by, "RST 4"),
        "gnd":  (bx + 85, by + bh, "GND 1"),
        "ctrl": (bx + bw, by + 210, "CTRL 5"),
    }
    for k, (px, py, lab) in pin.items():
        s += text(px + (8 if px <= bx else -8), py + (-6 if py in (by,) else 4),
                  lab, 10.5, GREY, "start" if px <= bx else "end")
    # Vcc згори
    s += _vdd(bx + 40, by - 0, "+Vcc")
    s += line(bx + 40, by - 12, bx + 40, by - 12, RED, 2)
    # RESET до Vcc
    s += line(pin["rst"][0], pin["rst"][1], pin["rst"][0], by - 26, RED, 2)
    s += line(bx + 40, by - 26, pin["rst"][0], by - 26, RED, 2)
    s += dot(bx + 40, by - 26, 3, RED)
    # GND
    s += _gnd(pin["gnd"][0], pin["gnd"][1] + 0)
    # CTRL → C мала на землю
    s += line(pin["ctrl"][0], pin["ctrl"][1], pin["ctrl"][0] + 30, pin["ctrl"][1], INK, 1.6)
    s += _cap_v(pin["ctrl"][0] + 30, pin["ctrl"][1] + 20)
    s += line(pin["ctrl"][0] + 30, pin["ctrl"][1], pin["ctrl"][0] + 30, pin["ctrl"][1] + 13, INK, 1.6)
    s += _gnd(pin["ctrl"][0] + 30, pin["ctrl"][1] + 27)
    s += text(pin["ctrl"][0] + 40, pin["ctrl"][1] + 22, "10 нФ", 10, GREY, "start")

    # Ra: Vcc → DISCH(7)
    s += line(bx + 40, by - 12, bx + 40, 56, RED, 2)
    s += line(bx + 40, 56, 540, 56, RED, 2)
    s += _res_v(540, 95, length=46, hh=9); s += text(556, 95, "Ra", 12, INK, "start", "bold")
    s += line(540, 56, 540, 72, RED, 2)
    s += line(540, 118, 540, pin["disch"][1], INK, 2)
    s += line(pin["disch"][0], pin["disch"][1], 540, pin["disch"][1], INK, 2)
    s += dot(540, pin["disch"][1], 3)
    # Rb: DISCH(7) → THRESH(6)=TRIG(2)=C top
    s += line(540, pin["disch"][1], 540, 175, INK, 2)
    s += _res_v(540, 200, length=46, hh=9); s += text(556, 200, "Rb", 12, INK, "start", "bold")
    s += line(540, 223, 540, 270, INK, 2)
    nodeC = 270
    s += dot(540, nodeC, 3)
    # C: вузол → GND
    s += _cap_v(540, nodeC + 30)
    s += line(540, nodeC, 540, nodeC + 23, INK, 2)
    s += line(540, nodeC + 37, 540, nodeC + 60, INK, 2)
    s += _gnd(540, nodeC + 60); s += text(556, nodeC + 40, "C", 12, INK, "start", "bold")
    # THRESH(6) і TRIG(2) на вузол
    s += line(pin["thr"][0], pin["thr"][1], 150, pin["thr"][1], BLUE, 2)
    s += line(150, pin["thr"][1], 150, nodeC, BLUE, 2)
    s += line(150, nodeC, 540, nodeC, BLUE, 2)
    s += line(pin["trig"][0], pin["trig"][1], 180, pin["trig"][1], BLUE, 2)
    s += line(180, pin["trig"][1], 180, nodeC, BLUE, 2)
    s += dot(180, nodeC, 3, BLUE)
    s += text(300, nodeC - 8, "THR=TRIG=Vc", 11, BLUE, "middle", "bold")
    # OUT
    s += arrow(pin["out"][0], pin["out"][1], pin["out"][0] + 50, pin["out"][1], INK, 2.2)
    s += text(pin["out"][0] + 56, pin["out"][1] + 4, "вихід ⎍", 12, INK, "start", "bold")
    return s


def fig_3_2_astable_waves():
    """Осцилограма астабільного: пилка на C між ⅓ і ⅔, меандр на виході."""
    W, H = 700, 380
    s = header(W, H)
    s += text(W / 2, 26, "Перезаряд конденсатора і вихід", 16, INK, "middle", "bold")
    ox, oy, axw, axh = 70, 200, 560, 130
    s += _axes(ox, oy, axw, axh, "t", "Vc")
    # рівні ⅓ і ⅔
    y23 = oy - axh * 2 / 3
    y13 = oy - axh * 1 / 3
    s += line(ox, y23, ox + axw, y23, RED, 1.4, "5 4"); s += text(ox - 8, y23 + 4, "⅔Vcc", 11, RED, "end", "bold")
    s += line(ox, y13, ox + axw, y13, BLUE, 1.4, "5 4"); s += text(ox - 8, y13 + 4, "⅓Vcc", 11, BLUE, "end", "bold")
    # експоненційна пилка між ⅓ і ⅔
    pts = []
    n = 560
    th = 0.45      # заряд (через Ra+Rb)
    tl = 0.30      # розряд (через Rb)
    seg = th + tl
    for j in range(n + 1):
        t = j / n * 3.0  # 3 «секунди»
        ph = t % seg
        cyc = int(t // seg)
        if ph < th:  # заряд від ⅓ до ⅔
            frac = 1 - math.exp(-ph / th * 1.5)
            frac /= (1 - math.exp(-1.5))
            v = 1 / 3 + (1 / 3) * frac
        else:        # розряд від ⅔ до ⅓
            p2 = ph - th
            frac = math.exp(-p2 / tl * 1.5)
            v = 1 / 3 + (1 / 3) * frac
        x = ox + axw * t / 3.0
        y = oy - axh * v
        pts.append((x, y))
    s += _poly(pts, INK, 2.6)
    # вихід (меандр) нижче
    oy2 = 350
    base = oy2
    high = oy2 - 36
    s += text(ox - 8, base - 18, "OUT", 11, GREEN, "end", "bold")
    wpts = []
    for j in range(n + 1):
        t = j / n * 3.0
        ph = t % seg
        v = high if ph < th else base
        wpts.append((ox + axw * t / 3.0, v))
    # додати вертикалі
    s += _poly(wpts, GREEN, 2.6)
    s += text(ox + axw * (th / seg) / 3 * 3 / 2, high - 8, "tH", 12, INK, "middle", "bold")
    s += text(ox + axw * (th + tl / 2) / seg / 3 * 3, base - 8, "tL", 12, INK, "middle", "bold")
    s += text(ox + axw + 6, base + 4, "t", 12, GREEN, "start", "bold")
    s += text(W / 2, oy2 + 26,
              "Заряд через Ra+Rb (вихід «1»), розряд через Rb (вихід «0»). tH > tL завжди.",
              11.5, GREY, "middle")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  2.12.4 — Моностабільний режим
# ════════════════════════════════════════════════════════════════════════════

def fig_4_1_mono_circuit():
    """Схема одновібратора: R до Vcc, C на землю, запуск на TRIG."""
    W, H = 620, 400
    s = header(W, H)
    s += text(W / 2, 28, "555 у моностабільному режимі", 16.5, INK, "middle", "bold")
    bx, by, bw, bh = 220, 90, 170, 230
    s += rect(bx, by, bw, bh, "#fbfbfb", INK, 1.8, 8)
    s += text(bx + bw / 2, by + bh / 2, "555", 18, INK, "middle", "bold")
    # піни
    trig = (bx, by + 130); thr = (bx, by + 175)
    disch = (bx + bw, by + 60); out = (bx + bw, by + 130)
    vcc = (bx + 40, by); gnd = (bx + 85, by + bh)
    s += text(bx + 8, trig[1] + 4, "TRIG 2", 10.5, GREY, "start")
    s += text(bx + 8, thr[1] + 4, "THR 6", 10.5, GREY, "start")
    s += text(bx + bw - 8, disch[1] + 4, "DIS 7", 10.5, GREY, "end")
    s += text(bx + bw - 8, out[1] + 4, "OUT 3", 10.5, GREY, "end")
    # Vcc
    s += _vdd(vcc[0], vcc[1], "+Vcc")
    s += _gnd(gnd[0], gnd[1])
    # R від Vcc до DISCH=THRESH=C
    s += line(vcc[0], vcc[1] - 12, vcc[0], 56, RED, 2)
    s += line(vcc[0], 56, 500, 56, RED, 2)
    s += _res_v(500, 95, length=46, hh=9); s += text(516, 95, "R", 12, INK, "start", "bold")
    s += line(500, 56, 500, 72, RED, 2)
    nodeC = 175
    s += line(500, 118, 500, nodeC, INK, 2)
    # DISCH і THRESH на цей вузол
    s += line(disch[0], disch[1], 500, disch[1], INK, 2); s += line(500, disch[1], 500, 118, INK, 2)
    s += dot(500, disch[1], 3)
    s += line(thr[0], thr[1], 160, thr[1], BLUE, 2); s += line(160, thr[1], 160, nodeC, BLUE, 2); s += line(160, nodeC, 500, nodeC, BLUE, 2)
    s += dot(500, nodeC, 3)
    # C на землю
    s += _cap_v(500, nodeC + 28)
    s += line(500, nodeC, 500, nodeC + 21, INK, 2); s += line(500, nodeC + 35, 500, nodeC + 58, INK, 2)
    s += _gnd(500, nodeC + 58); s += text(516, nodeC + 36, "C", 12, INK, "start", "bold")
    # запуск на TRIG (кнопка з підтяжкою до Vcc)
    s += line(trig[0], trig[1], 120, trig[1], INK, 2)
    s += line(120, trig[1], 120, trig[1] - 40, RED, 2)
    s += line(95, trig[1] - 40, 145, trig[1] - 40, RED, 2)
    s += text(120, trig[1] - 46, "+Vcc", 11, RED, "middle", "bold")
    s += line(120, trig[1], 120, trig[1] + 30, INK, 2)
    s += text(70, trig[1] + 8, "запуск", 11, GREY, "start")
    # кнопка-розрив
    s += line(120, trig[1] + 30, 120, trig[1] + 42, INK, 2)
    s += line(110, trig[1] + 42, 132, trig[1] + 34, INK, 2)
    s += line(120, trig[1] + 52, 120, trig[1] + 64, INK, 2)
    s += _gnd(120, trig[1] + 64)
    # OUT
    s += arrow(out[0], out[1], out[0] + 60, out[1], INK, 2.2)
    s += text(out[0] + 66, out[1] + 4, "імпульс", 12, INK, "start", "bold")
    return s


def fig_4_2_mono_waves():
    """Осцилограма одновібратора: короткий запуск → довгий імпульс T=1.1RC."""
    W, H = 700, 410
    s = header(W, H)
    s += text(W / 2, 26, "Один короткий запуск → один точний імпульс", 15.5, INK, "middle", "bold")
    ox, axw = 80, 540
    # три доріжки
    rows = [("TRIG (2)", 90, BLUE), ("Vc на C", 210, INK), ("OUT (3)", 350, GREEN)]
    for lab, oy, col in rows:
        s += line(ox, oy, ox + axw, oy, FAINT, 1.2)
        s += text(ox - 10, oy - 22, lab, 11.5, col, "end", "bold")
        s += arrow(ox, oy, ox + axw, oy, INK, 1.6)
    # часові мітки запуску
    t_trig = 0.18
    t_end = 0.70
    def X(t):
        return ox + axw * t
    # TRIG: висить «1», коротко падає в «0»
    oy = 90; hi = oy - 36
    s += _poly([(X(0), hi), (X(t_trig - 0.02), hi), (X(t_trig - 0.02), oy),
                (X(t_trig + 0.02), oy), (X(t_trig + 0.02), hi), (X(1), hi)], BLUE, 2.6)
    s += text(X(t_trig), oy + 16, "↓ запуск", 11, BLUE, "middle", "bold")
    # Vc: заряд від 0 до ⅔ потім різко в 0
    oy = 210; full = 96
    y23 = oy - full * 2 / 3
    s += line(ox, y23, ox + axw, y23, RED, 1.3, "5 4"); s += text(ox + axw + 4, y23 + 4, "⅔Vcc", 10.5, RED, "start", "bold")
    pts = [(X(0), oy)]
    n = 200
    for j in range(n + 1):
        t = t_trig + (t_end - t_trig) * j / n
        frac = 1 - math.exp(-(j / n) * 1.1)
        frac /= (1 - math.exp(-1.1))
        v = (2 / 3) * frac
        pts.append((X(t), oy - full * v))
    pts.append((X(t_end), oy))  # скидання в нуль
    pts.append((X(1), oy))
    s += _poly(pts, INK, 2.6)
    # OUT: «0» доти, поки запуск; «1» від запуску до t_end; назад «0»
    oy = 350; hi = oy - 36
    s += _poly([(X(0), oy), (X(t_trig), oy), (X(t_trig), hi),
                (X(t_end), hi), (X(t_end), oy), (X(1), oy)], GREEN, 2.8)
    # розмір T
    s += line(X(t_trig), 300, X(t_trig), 314, GREY, 1.2)
    s += line(X(t_end), 300, X(t_end), 314, GREY, 1.2)
    s += arrow(X(t_trig), 307, X(t_end), 307, GREY, 1.6); s += arrow(X(t_end), 307, X(t_trig), 307, GREY, 1.6)
    s += text((X(t_trig) + X(t_end)) / 2, 300, "T ≈ 1.1·R·C", 12.5, INK, "middle", "bold")
    s += text(W / 2, 392, "Тривалість виходу задана лише R і C, а не довжиною запуску.",
              12, GREY, "middle")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  2.12.5 — Опорна напруга
# ════════════════════════════════════════════════════════════════════════════

def fig_5_1_zener_drift():
    """Графік: відносний дрейф низьковольтного Зенера, «6.2 В» і bandgap по T."""
    W, H = 680, 380
    s = header(W, H)
    s += text(W / 2, 26, "Чому Зенер «пливе», а bandgap — ні", 16, INK, "middle", "bold")
    s += text(W / 2, 46, "відхилення опорної напруги від номіналу, %", 12, GREY, "middle")
    ox, axw = 110, 450
    # осьова система: 0% посередині
    y0 = 215                     # рівень 0% (номінал при 25 °C)
    span = 120                   # ±span пікселів = ±FS %
    FS = 4.0                     # повна шкала по вертикалі, ±4 %
    s += arrow(ox, y0 + span + 18, ox, y0 - span - 12, INK, 2)     # вісь V
    s += arrow(ox, y0, ox + axw + 14, y0, INK, 2)                  # вісь T
    s += text(ox + 4, y0 - span - 16, "ΔV, %", 12, INK, "start", "bold")
    s += text(ox + axw + 18, y0 + 4, "T, °C", 12, INK, "start", "bold")

    def Y(pct):
        return y0 - span * pct / FS
    # сітка ±2%, ±4%
    for pct in [-4, -2, 2, 4]:
        yy = Y(pct)
        s += line(ox, yy, ox + axw, yy, FAINT, 1.1, "4 4")
        s += text(ox - 8, yy + 4, ("+%d%%" % pct) if pct > 0 else ("%d%%" % pct), 10, GREY, "end")
    s += line(ox, y0, ox + axw, y0, GREY, 1.4)
    s += text(ox - 8, y0 + 4, "0", 10.5, GREY, "end")
    # температурна вісь -40..+85, 0 при 25 °C
    def X(T):
        return ox + axw * (T + 40) / 125.0
    for T in [-40, 0, 25, 50, 85]:
        s += line(X(T), y0 - 4, X(T), y0 + 4, INK, 1.6)
        s += text(X(T), y0 + 20, str(T), 10.5, INK, "middle")

    def curve(coeff_per_C_pct, col, wv, dash=None, quad=0.0):
        pts = []
        for j in range(126):
            T = -40 + j
            pct = coeff_per_C_pct * (T - 25) + quad * (T - 25) ** 2
            pts.append((X(T), Y(pct)))
        return _poly(pts, col, wv, dash), pts
    # низьковольтний Зенер ~3.3 В: −2 мВ/°C → ≈ −0.06 %/°C (спадає з нагрівом)
    cz, pz = curve(-0.06, BLUE, 2.6)
    s += cz
    s += text(X(-30), Y(3.9) + 16, "стабілітрон ~3.3 В (−2 мВ/°C)", 11.5, BLUE, "start", "bold")
    # «магічний» 6.2 В Зенер: майже компенсований, легкий +нахил
    ch, ph = curve(0.012, GREY, 2.0, "5 4")
    s += ch
    s += text(X(85) - 4, Y(0.72) - 8, "Зенер ~6.2 В", 11, GREY, "end")
    # bandgap: майже плоска парабола з вершиною біля 25 °C
    cb, pb = curve(0.0, RED, 3.0, None, quad=-0.00012)
    s += cb
    s += text(X(2), Y(-0.55) + 18, "bandgap (плоска)", 12, RED, "start", "bold")
    return s


def fig_5_2_bandgap_idea():
    """Ідея bandgap: −2 мВ/°C Vbe + (+k) ΔVbe = 0."""
    W, H = 680, 320
    s = header(W, H)
    s += text(W / 2, 26, "Складаємо дві протилежні залежності в нуль", 15.5, INK, "middle", "bold")
    ox, oy, axw, axh = 80, 250, 470, 180
    s += _axes(ox, oy, axw, axh, "T", "V")
    # Vbe спадає (від'ємний нахил)
    s += _poly([(ox, oy - axh * 0.82), (ox + axw, oy - axh * 0.30)], BLUE, 2.6)
    s += text(ox + axw + 4, oy - axh * 0.30, "Vbe (−2 мВ/°C)", 12, BLUE, "start", "bold")
    # PTAT зростає
    s += _poly([(ox, oy - axh * 0.12), (ox + axw, oy - axh * 0.64)], RED, 2.6)
    s += text(ox + axw + 4, oy - axh * 0.64, "K·ΔVbe (PTAT, +)", 12, RED, "start", "bold")
    # сума — плоска
    s += line(ox, oy - axh * 0.93, ox + axw, oy - axh * 0.93, GREEN, 3)
    s += text(ox + axw + 4, oy - axh * 0.93, "сума ≈ 1.25 В", 12.5, GREEN, "start", "bold")
    s += text(ox + axw / 2, oy + 38,
              "Падіння переходу + помножена різниця двох переходів = майже константа.",
              11.5, GREY, "middle")
    s += text(ox + axw / 2, oy + 56,
              "1.25 В — це і є ширина забороненої зони кремнію у вольтах.",
              11.5, GREY, "middle", "italic")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  2.12.6 — Аналогові ключі й мультиплексори
# ════════════════════════════════════════════════════════════════════════════

def fig_6_1_switch():
    """Аналоговий ключ: вхід-вихід двонапрямлений, керування цифрою, Ron."""
    W, H = 640, 320
    s = header(W, H)
    s += text(W / 2, 26, "Аналоговий ключ: керована цифрою «перемичка»", 15.5, INK, "middle", "bold")
    # сигнальний шлях
    y = 150
    s += arrow(70, y, 250, y, INK, 2.2); s += text(70, y - 12, "сигнал A↔B", 12, INK, "start", "bold")
    # ключ-прямокутник з Ron
    s += rect(250, y - 26, 130, 52, LGRN, GREEN, 2, 8)
    s += text(315, y - 5, "ключ", 13, INK, "middle", "bold")
    s += text(315, y + 14, "Ron ≈ 50–150 Ω", 11, GREEN, "middle")
    s += arrow(380, y, 560, y, INK, 2.2)
    s += text(560, y - 12, "далі в коло", 12, INK, "end", "bold")
    # двонапрямленість
    s += arrow(250, y + 0, 70, y + 0, GREY, 1.2)  # назад (схематично)
    # керування зверху
    s += arrow(315, 70, 315, y - 28, BLUE, 2.2)
    s += text(315, 60, "CTRL (цифровий «0/1»)", 12, BLUE, "middle", "bold")
    s += text(315, 230, "0 → розрив (висока ізоляція)", 12, INK, "middle")
    s += text(315, 250, "1 → з'єднано через малий Ron", 12, INK, "middle")
    s += text(315, 280, "Комутуємо СИГНАЛ, а не потужність — струми мікро/міліампери.",
              11.5, RED, "middle", "bold")
    return s


def fig_6_2_mux():
    """8-канальний мультиплексор: 8 входів → 1 вихід, 3 адресні біти."""
    W, H = 660, 485
    s = header(W, H)
    s += text(W / 2, 28, "Аналоговий мультиплексор 8→1", 16.5, INK, "middle", "bold")
    # 8 входів зліва
    inx = 90
    ys = [70 + i * 40 for i in range(8)]
    bx = 250
    bw = 130
    by = ys[0] - 18
    bh = ys[-1] - ys[0] + 36
    # тіло мультиплексора (трапеція)
    s += f'<path d="M {bx},{by} L {bx+bw},{by+50} L {bx+bw},{by+bh-50} L {bx},{by+bh} Z" fill="#f4f7fb" stroke="{INK}" stroke-width="1.8"/>\n'
    s += text(bx + bw / 2 - 6, (by + bh / 2), "MUX", 15, INK, "middle", "bold")
    for i, yy in enumerate(ys):
        col = GREEN if i == 3 else INK
        wv = 2.6 if i == 3 else 1.8
        s += line(inx, yy, bx, yy, col, wv)
        s += dot(inx, yy, 3, INK)
        s += text(inx - 8, yy + 4, f"CH{i}", 11, INK, "end")
    # обраний канал
    s += text(inx + 30, ys[3] - 8, "← обраний", 11, GREEN, "start", "bold")
    # вихід
    outx = bx + bw
    outy = by + bh / 2
    s += line(outx, by + 50, outx, by + bh - 50, FAINT, 1)
    s += arrow(outx, outy, outx + 90, outy, GREEN, 2.6)
    s += text(outx + 96, outy + 4, "COM (вихід)", 12, INK, "start", "bold")
    s += text(outx + 96, outy + 22, "→ один АЦП", 11, GREY, "start")
    # адресні біти знизу
    ax = bx + bw / 2
    s += arrow(ax, by + bh + 60, ax, by + bh, BLUE, 2.2)
    s += text(ax, by + bh + 78, "A2 A1 A0 = 011 → CH3", 12.5, BLUE, "middle", "bold")
    s += text(ax, by + bh + 96, "3 адресні біти обирають 1 із 8", 11, GREY, "middle")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  2.12.7 — Інструментальний підсилювач
# ════════════════════════════════════════════════════════════════════════════

def fig_7_1_problem():
    """Проблема: мілівольти різниці на тлі вольтів синфазної напруги."""
    W, H = 660, 320
    s = header(W, H)
    s += text(W / 2, 26, "Виміряти мілівольти на тлі вольтів", 16, INK, "middle", "bold")
    ox, oy, axw, axh = 90, 250, 470, 180
    s += _axes(ox, oy, axw, axh, "t", "V")
    # синфазний рівень ~ великий
    ycm = oy - axh * 0.62
    s += line(ox, ycm, ox + axw, ycm, GREY, 1.4, "5 4")
    s += text(ox + axw + 4, ycm + 4, "синфазний рівень (вольти)", 11, GREY, "start")
    # дві майже однакові лінії з крихітною різницею
    s += line(ox, ycm - 6, ox + axw, ycm - 6, RED, 2.4)
    s += line(ox, ycm + 6, ox + axw, ycm + 6, BLUE, 2.4)
    s += text(ox + 8, ycm - 12, "V+", 12, RED, "start", "bold")
    s += text(ox + 8, ycm + 20, "V−", 12, BLUE, "start", "bold")
    # позначка різниці
    s += line(ox + axw * 0.6, ycm - 6, ox + axw * 0.6, ycm + 6, INK, 1.4)
    s += arrow(ox + axw * 0.6 + 10, ycm - 6, ox + axw * 0.6 + 10, ycm + 6, INK, 1.4)
    s += arrow(ox + axw * 0.6 + 10, ycm + 6, ox + axw * 0.6 + 10, ycm - 6, INK, 1.4)
    s += text(ox + axw * 0.6 + 16, ycm + 4, "корисна різниця — лічені мВ", 11.5, INK, "start", "bold")
    # знизу нуль
    s += text(ox + axw / 2, oy + 34,
              "Потрібно підсилити різницю V+−V− і відкинути спільне. Це робота для CMRR.",
              11.5, GREEN, "middle", "bold")
    return s


def fig_7_2_three_opamp():
    """Класична схема трьох ОП: два буфери + Rg, потім різницевий каскад."""
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 28, "Інструментальний підсилювач: три ОП", 16.5, INK, "middle", "bold")
    # вхідні буфери
    a1x, a1y = 230, 120
    a2x, a2y = 230, 320
    t1, p1 = _opamp(a1x, a1y, 80, 64, plus_top=True, label="A1")
    t2, p2 = _opamp(a2x, a2y, 80, 64, plus_top=False, label="A2")
    s += t1 + t2
    # входи
    s += line(70, a1y - 16, p1["in_top"][0], a1y - 16, RED, 2)
    s += text(64, a1y - 20, "V+", 12, RED, "end", "bold")
    s += line(70, a2y + 16, p2["in_bot"][0], a2y + 16, BLUE, 2)
    s += text(64, a2y + 20, "V−", 12, BLUE, "end", "bold")
    # Rg між інверт. входами + два R зворотного зв'язку
    # A1: вихід → R1 → вузол(−)
    o1x = p1["out"][0]
    o2x = p2["out"][0]
    n1y = a1y + 16   # інверт. вхід A1 (нижній)
    n2y = a2y - 16   # інверт. вхід A2 (верхній)
    s += line(o1x, a1y, o1x + 20, a1y, INK, 2)
    s += line(o1x + 20, a1y, o1x + 20, n1y, INK, 2)
    s += _res_v(o1x + 20, (a1y + n1y) / 2 + 0, length=28, hh=8)
    s += line(p1["in_bot"][0], n1y, o1x + 20, n1y, INK, 2)
    s += dot(p1["in_bot"][0] + 0, n1y, 0)  # no
    s += text(o1x + 30, (a1y + n1y) / 2 + 4, "R", 11, INK, "start")
    s += line(o2x, a2y, o2x + 20, a2y, INK, 2)
    s += line(o2x + 20, a2y, o2x + 20, n2y, INK, 2)
    s += line(p2["in_top"][0], n2y, o2x + 20, n2y, INK, 2)
    s += text(o2x + 30, (a2y + n2y) / 2 + 4, "R", 11, INK, "start")
    # Rg між n1y і n2y
    midx = 150
    s += line(p1["in_bot"][0], n1y, midx, n1y, GREEN, 2)
    s += line(p2["in_top"][0], n2y, midx, n2y, GREEN, 2)
    s += _res_v(midx, (n1y + n2y) / 2, length=70, hh=10, col=GREEN)
    s += line(midx, n1y, midx, (n1y + n2y) / 2 - 35, GREEN, 2)
    s += line(midx, (n1y + n2y) / 2 + 35, midx, n2y, GREEN, 2)
    s += text(midx - 14, (n1y + n2y) / 2 + 4, "Rg", 12, GREEN, "end", "bold")
    s += text(midx - 14, (n1y + n2y) / 2 + 20, "(підсилення)", 10, GREEN, "end")
    # перший каскад → диф. виходи o1, o2
    # другий ОП — різницевий
    a3x, a3y = 560, 220
    t3, p3 = _opamp(a3x, a3y, 84, 70, plus_top=False, label="A3")
    s += t3
    # від A1 (верх) через R до «−» A3
    s += line(o1x + 20, a1y, 420, a1y, INK, 2)
    s += line(420, a1y, 420, p3["in_top"][1], INK, 2)
    s += _res_h(450, p3["in_top"][1], length=40)
    s += line(420, p3["in_top"][1], 430, p3["in_top"][1], INK, 2)
    s += line(470, p3["in_top"][1], p3["in_top"][0], p3["in_top"][1], INK, 2)
    s += text(450, p3["in_top"][1] - 8, "R", 10.5, INK, "middle")
    # від A2 (низ) через R до «+» A3, і R на землю
    s += line(o2x + 20, a2y, 420, a2y, INK, 2)
    s += line(420, a2y, 420, p3["in_bot"][1], INK, 2)
    s += _res_h(450, p3["in_bot"][1], length=40)
    s += line(420, p3["in_bot"][1], 430, p3["in_bot"][1], INK, 2)
    s += line(470, p3["in_bot"][1], p3["in_bot"][0], p3["in_bot"][1], INK, 2)
    s += text(450, p3["in_bot"][1] + 16, "R", 10.5, INK, "middle")
    # зв. зв. R від out до «−»
    s += line(p3["out"][0], a3y, p3["out"][0] + 18, a3y, INK, 2)
    s += line(p3["out"][0] + 18, a3y, p3["out"][0] + 18, p3["in_top"][1] - 26, INK, 2)
    s += line(p3["out"][0] + 18, p3["in_top"][1] - 26, p3["in_top"][0] - 0, p3["in_top"][1] - 26, INK, 2)
    s += line(p3["in_top"][0], p3["in_top"][1], p3["in_top"][0], p3["in_top"][1] - 26, INK, 2)
    s += _res_h((p3["in_top"][0] + p3["out"][0] + 18) / 2, p3["in_top"][1] - 26, length=40)
    # земля на «+» R
    s += line(p3["in_bot"][0] - 60, p3["in_bot"][1], p3["in_bot"][0] - 60, p3["in_bot"][1] + 34, INK, 2)
    # вихід
    s += arrow(p3["out"][0] + 18, a3y, p3["out"][0] + 80, a3y, INK, 2.4)
    s += text(p3["out"][0] + 86, a3y + 4, "Vout", 13, INK, "start", "bold")
    # підписи каскадів
    s += text(230, 405, "1) два буфери + Rg: підсилюють РІЗНИЦЮ", 12, INK, "middle", "bold")
    s += text(580, 405, "2) різницевий: прибирає СПІЛЬНЕ", 12, INK, "middle", "bold")
    return s


# ────────────────────────────────────────────────────────────────────────────
def main():
    fns = [
        ("fig-2-12-1-1-timeline.svg", fig_1_1_timeline),
        ("fig-2-12-1-2-second-source.svg", fig_1_2_second_source),
        ("fig-2-12-2-1-block.svg", fig_2_1_block),
        ("fig-2-12-2-2-thresholds.svg", fig_2_2_thresholds),
        ("fig-2-12-3-1-astable-circuit.svg", fig_3_1_astable_circuit),
        ("fig-2-12-3-2-astable-waves.svg", fig_3_2_astable_waves),
        ("fig-2-12-4-1-mono-circuit.svg", fig_4_1_mono_circuit),
        ("fig-2-12-4-2-mono-waves.svg", fig_4_2_mono_waves),
        ("fig-2-12-5-1-zener-drift.svg", fig_5_1_zener_drift),
        ("fig-2-12-5-2-bandgap-idea.svg", fig_5_2_bandgap_idea),
        ("fig-2-12-6-1-switch.svg", fig_6_1_switch),
        ("fig-2-12-6-2-mux.svg", fig_6_2_mux),
        ("fig-2-12-7-1-problem.svg", fig_7_1_problem),
        ("fig-2-12-7-2-three-opamp.svg", fig_7_2_three_opamp),
    ]
    for name, fn in fns:
        save(name, fn())
    print("\nDone: %d figures -> %s" % (len(fns), OUT))


if __name__ == "__main__":
    main()
