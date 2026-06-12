# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 2.10
«Як кварц став серцебиттям електроніки: від Кюрі до FT-243».

Окремий скрипт ВСТАВКИ (НЕ головний figs.py розділу). Чистий Python без
залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-r10-hist-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано з
figs.py попередніх розділів (єдиний вигляд курсу).
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
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LGREY = "#f1f3f5"
QFILL = "#e7ecf3"   # колір кварцової пластинки
BRASS = "#caa44e"   # латунь корпусу FT-243
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


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return circle(cx, cy, r, "none", color, w) + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


def _sine(ox, oy, w, amp, cycles, col, wv=2.4, phase=0.0, decay=0.0):
    pts = []
    for j in range(0, 241):
        f = j / 240
        env = math.exp(-decay * f)
        y = oy - amp * env * math.sin(2 * math.pi * cycles * f + phase)
        pts.append((ox + f * w, y))
    return _poly(pts, col, wv)


def cap_sym(cx, cy, half=14, gap=9, col=INK):
    s = line(cx - gap / 2, cy - half, cx - gap / 2, cy + half, col, 2.6)
    s += line(cx + gap / 2, cy - half, cx + gap / 2, cy + half, col, 2.6)
    return s


def xtal_sym(cx, cy, half=18, col=INK):
    """Позначення кварцу: дві обкладки + прямокутник-кристал між ними."""
    s = line(cx - 12, cy - half, cx - 12, cy + half, col, 2.6)      # ліва обкладка
    s += line(cx + 12, cy - half, cx + 12, cy + half, col, 2.6)     # права обкладка
    s += rect(cx - 6, cy - half * 0.7, 12, half * 1.4, QFILL, col, 2.2, 2)  # кристал
    return s


# ── Рис. 2.10.0.1 — таймлайн ─────────────────────────────────────────────────
def fig_timeline():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 36, "Як кварц став серцебиттям електроніки", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "ланцюг питань (сірим — кількісний зміст Розділу 2.10)",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 92, H - 28
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1880", "брати Кюрі / Curie", "Кристал перетворює тиск на напругу — п'єзоефект", False, False),
        ("1921", "Кеді / Cady  (перевірити)", "Перший кварцовий генератор: кристал дзвенить безперервно", False, True),
        ("1923", "П'єрс / Pierce", "Одна лампа замість кількох — схема, придатна для тиражу", False, True),
        ("1941–45", "FT-243 — Друга світова", "~30 млн кварців: уніфікований корпус і доведення частоти", False, False),
        ("Розділ 2.10", "Резонатори й опорні частоти", "П'єзоефект, добротність, генератор П'єрса, ppm, MEMS", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 32 + (bot - top - 64) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#fff", RED, 3)
            s += circle(spine, y, 4.5, RED, RED, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#fff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, (RED if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12.5, (INK if not dest else GREY), "start", style="italic")
    save("fig-r10-hist-1-timeline.svg", s)


# ── Рис. 2.10.0.2 — прямий і зворотний п'єзоефект ────────────────────────────
def fig_piezo():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "П'єзоефект: електрика й механіка зв'язані в обидва боки", 19, INK, "middle", "bold")

    # --- ЛІВО: прямий ефект (тиск -> напруга) ---
    s += _frame(34, 64, 360, 280, "прямий ефект — брати Кюрі, 1880")
    cx = 214
    base = 250
    # кристал стиснутий
    s += rect(cx - 46, 150, 92, base - 150, QFILL, INK, 2.4, 4)
    s += text(cx, 215, "кварц", 13, INK, "middle", "bold")
    # стрілки тиску
    s += arrow(cx, 96, cx, 146, INK, 3)
    s += arrow(cx, base + 50, cx, base + 4, INK, 3)
    s += text(cx, 90, "тиск F", 13, INK, "middle", "bold")
    s += text(cx, base + 66, "тиск F", 13, INK, "middle", "bold")
    # заряди на гранях
    s += plus(cx - 64, 150, 11)
    s += minus(cx + 64, base, 11)
    # провід до вольтметра
    s += line(cx - 46, 158, 110, 158, GREY, 2)
    s += line(110, 158, 110, 300, GREY, 2)
    s += line(cx + 46, base - 8, 318, base - 8, GREY, 2)
    s += line(318, base - 8, 318, 300, GREY, 2)
    s += circle(214, 300, 22, "#fff", GREEN, 2.6)
    s += text(214, 305, "V", 16, GREEN, "middle", "bold")
    s += text(214, 332, "з'являється напруга", 11.5, GREEN, "middle", style="italic")

    # --- ПРАВО: зворотний ефект (напруга -> деформація) ---
    s += _frame(426, 64, 360, 280, "зворотний ефект — Ліппман 1881, підтвердили Кюрі")
    cx2 = 606
    # кристал деформований (трохи ширший/нижчий пунктиром — початкова форма)
    s += rect(cx2 - 40, 150, 80, 100, "none", GREY, 1.6, 4)  # початкова форма (пунктир-сірий)
    s += rect(cx2 - 46, 158, 92, 84, QFILL, INK, 2.4, 4)     # деформована
    s += text(cx2, 205, "кварц", 13, INK, "middle", "bold")
    # джерело напруги
    s += plus(cx2 - 78, 150, 11)
    s += minus(cx2 + 78, 242, 11)
    s += line(cx2 - 46, 162, cx2 - 92, 162, GREY, 2)
    s += line(cx2 - 92, 162, cx2 - 92, 300, GREY, 2)
    s += line(cx2 + 46, 238, cx2 + 92, 238, GREY, 2)
    s += line(cx2 + 92, 238, cx2 + 92, 300, GREY, 2)
    s += circle(606, 300, 22, "#fff", RED, 2.6)
    s += text(606, 305, "U", 15, RED, "middle", "bold")
    # стрілки деформації
    s += arrow(cx2 - 60, 200, cx2 - 50, 200, BLUE, 2.4)
    s += arrow(cx2 + 60, 200, cx2 + 50, 200, BLUE, 2.4)
    s += text(cx2, 332, "кристал деформується", 11.5, BLUE, "middle", style="italic")

    save("fig-r10-hist-2-piezo.svg", s)


# ── Рис. 2.10.0.3 — від Кеді до П'єрса ───────────────────────────────────────
def fig_pierce():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 34, "Від багатолампового генератора Кеді — до однолампового П'єрса", 18.5, INK, "middle", "bold")

    # --- ЛІВО: Кеді (кілька ламп) ---
    s += _frame(30, 58, 372, 320, "Кеді, 1921 — кілька ламп, делікатне налаштування")
    # три лампи-кружечки
    for i, lx in enumerate((110, 216, 322)):
        s += circle(lx, 150, 26, "#fff", INK, 2.4)
        s += text(lx, 156, "лампа", 11, INK, "middle", "bold")
        if i < 2:
            s += arrow(lx + 28, 150, lx + 52, 150, GREY, 2.2)
    # кварц унизу
    s += xtal_sym(216, 270, 24)
    s += text(216, 318, "кварц (резонатор)", 12, INK, "middle", "bold")
    s += line(110, 176, 110, 270, GREY, 2)
    s += line(110, 270, 192, 270, GREY, 2)
    s += line(240, 270, 322, 270, GREY, 2)
    s += line(322, 270, 322, 176, GREY, 2)
    s += text(216, 350, "складно й дорого тиражувати", 12, RED, "middle", style="italic")

    # стрілка переходу
    s += arrow(414, 220, 452, 220, GREEN, 3.2)
    s += text(433, 205, "спрощення", 11.5, GREEN, "middle", "bold")

    # --- ПРАВО: Пірс (одна лампа/інвертор) ---
    s += _frame(466, 58, 372, 320, "П'єрс, 1923 — одна лампа, частоту диктує кварц")
    cx = 652
    # активний елемент
    s += circle(cx, 140, 30, "#fff", INK, 2.6)
    s += text(cx, 134, "лампа", 11, INK, "middle", "bold")
    s += text(cx, 150, "(сьогодні", 9.5, GREY, "middle")
    s += text(cx, 162, "інвертор)", 9.5, GREY, "middle")
    # кварц у петлі зворотного зв'язку
    s += xtal_sym(cx, 268, 24)
    s += text(cx, 316, "кварц", 12, INK, "middle", "bold")
    # два навантажувальні конденсатори по боках
    s += cap_sym(cx - 96, 268, 13, 9, INK)
    s += text(cx - 96, 300, "C", 12, INK, "middle", "bold")
    s += cap_sym(cx + 96, 268, 13, 9, INK)
    s += text(cx + 96, 300, "C", 12, INK, "middle", "bold")
    # з'єднання
    s += line(cx - 30, 152, cx - 96, 152, INK, 2)
    s += line(cx - 96, 152, cx - 96, 254, INK, 2)
    s += line(cx + 30, 152, cx + 96, 152, INK, 2)
    s += line(cx + 96, 152, cx + 96, 254, INK, 2)
    s += line(cx - 96, 282, cx - 12, 282, INK, 2)
    s += line(cx + 12, 282, cx + 96, 282, INK, 2)
    s += line(cx - 12, 268, cx - 96, 268, INK, 2)  # вхід кварцу
    s += line(cx + 12, 268, cx + 96, 268, INK, 2)
    s += text(cx, 350, "проста, надійна, тримає частоту намертво", 12, GREEN, "middle", style="italic")
    s += text(cx, 392, "ця сама топологія — у кожному МК (XTAL1/XTAL2)", 11.5, GREY, "middle", style="italic")

    save("fig-r10-hist-3-pierce.svg", s)


# ── Рис. 2.10.0.4 — будова тримача FT-243 ────────────────────────────────────
def fig_ft243():
    W, H = 840, 420
    s = header(W, H)
    s += text(W / 2, 34, "Тримач FT-243: стандарт корпусу, а не марка кристала", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "уніфікація → взаємозамінність → виробництво мільйонами", 12.5, GREY, "middle", style="italic")

    # --- ЛІВО: розріз корпусу з пластинкою ---
    s += _frame(40, 78, 360, 300, "усередині — кварцова пластинка між електродами")
    bx, by, bw, bh = 120, 120, 200, 180
    # латунний корпус
    s += rect(bx, by, bw, bh, "#fbf3da", BRASS, 3, 6)
    # дві металеві обкладки (електроди)
    s += rect(bx + 46, by + 30, 14, bh - 80, "#cfd6dd", GREY, 2)
    s += rect(bx + bw - 60, by + 30, 14, bh - 80, "#cfd6dd", GREY, 2)
    # кварцова пластинка між ними
    s += rect(bx + 70, by + 24, bw - 140, bh - 70, QFILL, INK, 2.4, 3)
    s += text(bx + bw / 2, by + bh / 2 - 6, "кварц", 13, INK, "middle", "bold")
    s += text(bx + bw / 2, by + bh / 2 + 14, "пластинка", 11, INK, "middle")
    # штирі
    s += rect(bx + 50, by + bh, 10, 36, "#b8b8b8", "#7d7d7d", 1.6, 2)
    s += rect(bx + bw - 60, by + bh, 10, 36, "#b8b8b8", "#7d7d7d", 1.6, 2)
    s += text(bx + bw / 2, by + bh + 56, "два штирі: фіксований крок і діаметр", 11.5, INK, "middle", style="italic")

    # --- ПРАВО: стрибок виробництва (стовпчики у лог-масштабі) ---
    s += _frame(440, 78, 360, 300, "стрибок виробництва на три порядки")
    ox, oy = 500, 330
    axh = 210
    s += arrow(ox, oy, ox, oy - axh - 12, INK, 2)
    s += text(ox - 8, oy - axh - 18, "штук/рік", 11.5, INK, "middle", "bold")
    s += arrow(ox, oy, ox + 250, oy, INK, 2)
    # лог-сітка: 10^4 .. 10^7
    decades = [("10⁴", 0.0), ("10⁵", 0.33), ("10⁶", 0.66), ("10⁷", 1.0)]
    for lab, fr in decades:
        yy = oy - 30 - fr * (axh - 50)
        s += line(ox - 4, yy, ox + 240, yy, FAINT, 1)
        s += text(ox - 10, yy + 4, lab, 11, GREY, "end")
    # два стовпчики: до війни (~10^4..10^5) і війна (~3·10^7)
    def _bar(x, frac, col, top_lab, bot_lab):
        yy = oy - 30 - frac * (axh - 50)
        b = rect(x, yy, 70, oy - yy, col, INK, 1.6, 3)
        b += text(x + 35, yy - 8, top_lab, 12, INK, "middle", "bold")
        b += text(x + 35, oy + 20, bot_lab, 11, INK, "middle")
        return b
    s += _bar(ox + 30, 0.30, LGREY, "десятки тис.", "до війни")
    s += _bar(ox + 150, 0.96, LRED, "≈30 млн", "1941–45")
    s += text(660, oy + 44, "(сумарно за роки війни)", 10.5, GREY, "middle", style="italic")
    save("fig-r10-hist-4-ft243.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_piezo()
    fig_pierce()
    fig_ft243()
    print("done")
