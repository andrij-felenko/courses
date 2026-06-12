# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для КОМПОНЕНТНОЇ вставки 🔌 до теми 2.12.7 —
«Інструментальний підсилювач: чому три ОП» (Модуль 2, Розділ 2.12, тема 7).

Окремий скрипт вставки (НЕ головний figs.py розділу і НЕ скрипт 🧮-вставки
inamp-cmrr). Чистий Python без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ
іменами (префікс inamp-bridge-), щоб не зіткнутися з inamp-topology.svg /
inamp-cm-vs-dm.svg математичної вставки.

Кут цієї вставки — ПРИСТРІЙ (а не виведення формул): in-amp як готовий чип,
його розпіновка, підключення мостового давача й ADC, дискрет проти мікросхеми.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи — секція «c»: Рис. 2.12.7c.k.
Допоміжні функції скопійовано зі стилю Розділу 13 (єдиний вигляд курсу).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
SUN   = "#e0a32e"
PURP  = "#7a3aa0"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
LPUR  = "#f2ecf7"
LGREY = "#f2f2f2"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", font=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def dot(cx, cy, r=3.4, col=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}"/>\n'


def res_h(cx, cy, w=40, lab="", col=INK, labdy=-13, labcol=None):
    """Горизонтальний резистор-коробочка з підписом зверху."""
    s = rect(cx - w / 2, cy - 9, w, 18, "#ffffff", col, 1.8, 3)
    if lab:
        s += text(cx, cy + labdy, lab, 12, labcol or col, "middle", "bold")
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def gnd(x, y, col=INK):
    s = line(x, y, x, y + 12, col, 2)
    s += line(x - 12, y + 12, x + 12, y + 12, col, 2.4)
    s += line(x - 8, y + 17, x + 8, y + 17, col, 2.0)
    s += line(x - 4, y + 22, x + 4, y + 22, col, 1.6)
    return s


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.12.7c.1 — in-amp як готовий чип: розпіновка + міст + Rg + REF + ADC.
#   Показує реальне підключення (вивідний кут), не виведення формул.
# ─────────────────────────────────────────────────────────────────────────────
def fig_pinout_hookup():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "In-amp як чип: міст → Rg задає G → REF зсуває нуль → ADC",
              19, INK, "middle", "bold")

    # ── 1. Мостовий давач (зліва), ромб ──
    bx, by = 130, 235            # центр моста
    a = 78                       # півдіагональ
    top = (bx, by - a); bot = (bx, by + a)
    lft = (bx - a, by); rgt = (bx + a, by)
    # чотири плеча
    for p, q in [(top, lft), (top, rgt), (lft, bot), (rgt, bot)]:
        s += line(p[0], p[1], q[0], q[1], INK, 2)
    # маленькі прямокутники-резистори на плечах
    def arm_res(p, q, strain=False):
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        col = GREEN if strain else INK
        r = rect(mx - 8, my - 6, 16, 12, "#ffffff", col, 1.6, 2)
        return r
    s += arm_res(top, lft); s += arm_res(rgt, bot, strain=True)
    s += arm_res(top, rgt, strain=True); s += arm_res(lft, bot)
    # живлення моста
    s += line(bx, by - a, bx, by - a - 26, RED, 2)
    s += text(bx, by - a - 32, "+EXC", 12, RED, "middle", "bold")
    s += gnd(bx, by + a + 4, INK)
    # виходи моста → входи in-amp
    s += text(lft[0] - 6, lft[1] - 10, "IN−", 12, BLUE, "end", "bold")
    s += text(rgt[0] + 6, rgt[1] - 10, "IN+", 12, RED, "start", "bold")
    s += text(bx, by + a + 40, "тензоміст / RTD", 12.5, GREY, "middle", "italic")
    s += text(bx, by + a + 56, "ΔR → мВ-різниця", 11.5, GREEN, "middle", "bold")

    # ── 2. Чип in-amp (центр), 8-вивідний корпус ──
    cx, cy, cw, ch = 430, 150, 180, 210
    s += rect(cx, cy, cw, ch, "#f7f7f7", INK, 2.4, 8)
    s += text(cx + cw / 2, cy + 26, "IN-AMP", 17, INK, "middle", "bold")
    s += text(cx + cw / 2, cy + 44, "(3 ОП + точні R)", 11.5, GREY, "middle", "italic")
    # виїмка-ключ зверху
    s += (f'<path d="M{cx + cw/2 - 11},{cy} a11,11 0 0,0 22,0" '
          f'fill="#ffffff" stroke="{INK}" stroke-width="2"/>\n')

    # ліві виводи (входи + Rg)
    pinL = cx
    yIN_p = cy + 70
    yIN_n = cy + 100
    yRG1  = cy + 150
    yRG2  = cy + 180
    for yy, lab, col in [(yIN_p, "IN+", RED), (yIN_n, "IN−", BLUE),
                         (yRG1, "RG", GREEN), (yRG2, "RG", GREEN)]:
        s += line(pinL - 22, yy, pinL, yy, col, 2.2)
        s += text(pinL + 8, yy + 4, lab, 11.5, col, "start", "bold")

    # праві виводи (OUT, REF, V+, V−)
    pinR = cx + cw
    yOUT = cy + 70
    yREF = cy + 100
    yVp  = cy + 150
    yVn  = cy + 180
    for yy, lab, col in [(yOUT, "OUT", INK), (yREF, "REF", PURP),
                         (yVp, "V+", RED), (yVn, "V−", BLUE)]:
        s += line(pinR, yy, pinR + 22, yy, col, 2.2)
        s += text(pinR - 8, yy + 4, lab, 11.5, col, "end", "bold")

    # під'єднання моста до IN+/IN−
    s += line(rgt[0], rgt[1], rgt[0] + 18, rgt[1], RED, 2)
    s += line(rgt[0] + 18, rgt[1], rgt[0] + 18, yIN_p, RED, 2)
    s += line(rgt[0] + 18, yIN_p, pinL - 22, yIN_p, RED, 2)
    s += line(lft[0], lft[1], lft[0] - 22, lft[1], BLUE, 2)
    s += line(lft[0] - 22, lft[1], lft[0] - 22, by + a + 90, BLUE, 2)
    s += line(lft[0] - 22, by + a + 90, 300, by + a + 90, BLUE, 2)
    s += line(300, by + a + 90, 300, yIN_n, BLUE, 2)
    s += line(300, yIN_n, pinL - 22, yIN_n, BLUE, 2)

    # один зовнішній Rg між двома RG-виводами — головна «ручка»
    s += line(pinL - 22, yRG1, pinL - 52, yRG1, GREEN, 2.2)
    s += line(pinL - 22, yRG2, pinL - 52, yRG2, GREEN, 2.2)
    s += line(pinL - 52, yRG1, pinL - 52, yRG2, GREEN, 2.2)
    s += rect(pinL - 80, (yRG1 + yRG2) / 2 - 9, 18, 18, "#ffffff", GREEN, 2, 3)
    s += text(pinL - 96, (yRG1 + yRG2) / 2 + 5, "R", 13, GREEN, "end", "bold")
    s += text(pinL - 90, (yRG1 + yRG2) / 2 + 5, "g", 9, GREEN, "start", "bold")
    s += text(pinL - 86, yRG1 - 16, "1 резистор", 11, GREEN, "middle", "bold")
    s += text(pinL - 86, yRG2 + 26, "задає G", 11, GREEN, "middle", "bold")

    # живлення чипа
    s += line(pinR + 22, yVp, pinR + 60, yVp, RED, 2)
    s += text(pinR + 64, yVp + 4, "+V", 11.5, RED, "start", "bold")
    s += line(pinR + 22, yVn, pinR + 60, yVn, BLUE, 2)
    s += gnd(pinR + 60, yVn, BLUE)

    # REF → опорна напруга (зсув нуля)
    s += line(pinR + 22, yREF, pinR + 60, yREF, PURP, 2)
    s += rect(pinR + 48, yREF + 14, 26, 18, LPUR, PURP, 1.6, 4)
    s += text(pinR + 61, yREF + 27, "Vref", 10.5, PURP, "middle", "bold")
    s += line(pinR + 61, yREF, pinR + 61, yREF + 14, PURP, 2)
    s += gnd(pinR + 61, yREF + 32, PURP)
    s += text(pinR + 70, yREF + 4, "зсув 0", 10.5, PURP, "start", "italic")

    # ── 3. OUT → ADC мікроконтролера ──
    ax, ay, aw, ah = 770, cy + 40, 120, 90
    s += line(pinR + 22, yOUT, ax, yOUT, INK, 2)
    s += arrow(ax - 1, yOUT, ax, yOUT, INK, 2)
    s += rect(ax, ay, aw, ah, LBLUE, BLUE, 2, 8)
    s += text(ax + aw / 2, ay + 30, "ADC", 16, BLUE, "middle", "bold")
    s += text(ax + aw / 2, ay + 50, "МК", 12.5, BLUE, "middle", "bold")
    s += text(ax + aw / 2, ay + 70, "0…Vref·2", 11, GREY, "middle", "italic")

    # підписи-стрілки логіки знизу
    s += rect(120, 410, 700, 44, LGRN, GREEN, 1.4, 8)
    s += text(135, 430, "Ланцюг: міст дає крихітну ΔV (мВ) на тлі великого спільного рівня;",
              12.5, INK, "start")
    s += text(135, 448, "in-amp множить ΔV на G (одним Rg), синфазне ріже, REF підпирає нуль під ADC.",
              12.5, INK, "start")

    save("inamp-bridge-pinout.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.12.7c.2 — дискрет проти чипа: чому купують готовий in-amp.
#   Ліворуч — три ОП + п'ять зовнішніх R (треба підбирати); праворуч — один
#   корпус + один Rg. Акцент: узгодженість резисторів = CMRR.
# ─────────────────────────────────────────────────────────────────────────────
def fig_discrete_vs_chip():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 30, "Те саме на дискретах проти готового чипа: за що платять",
              18, INK, "middle", "bold")

    def opamp(cx, cy, w=42, h=38, lab=""):
        t = (f'<path d="M {cx-w/2:.0f},{cy-h/2:.0f} L {cx-w/2:.0f},{cy+h/2:.0f} '
             f'L {cx+w/2:.0f},{cy:.0f} Z" fill="#fbfbfb" stroke="{INK}" stroke-width="1.6"/>\n')
        if lab:
            t += text(cx - 6, cy + 4, lab, 10.5, GREY, "middle", "bold")
        return t

    # ── ЛІВА панель: дискрет ──
    s += rect(40, 56, 410, 280, "none", RED, 1.6, 10)
    s += text(245, 80, "Зібрати самому: 3 ОП + 5 точних R", 14, RED, "middle", "bold")
    # три ОП
    s += opamp(150, 130, lab="A1")
    s += opamp(150, 250, lab="A2")
    s += opamp(330, 190, lab="A3")
    # натяк на резистори
    for (rx, ry, lab) in [(150, 190, "Rg"), (240, 130, "R₁"), (240, 250, "R₁"),
                          (300, 130, "R₂"), (300, 250, "R₂")]:
        s += rect(rx - 12, ry - 7, 24, 14, "#ffffff", INK, 1.4, 2)
        s += text(rx, ry - 11, lab, 10, INK, "middle", "bold")
    # дроти-натяк
    s += line(171, 130, 228, 130, INK, 1.4)
    s += line(171, 250, 228, 250, INK, 1.4)
    s += line(150, 149, 150, 183, GREEN, 1.6)
    s += line(150, 197, 150, 231, GREEN, 1.6)
    s += line(312, 130, 309, 130, INK, 1.4)
    s += line(312, 250, 309, 250, INK, 1.4)
    s += line(351, 190, 400, 190, INK, 1.6)
    s += arrow(400, 190, 426, 190, INK, 1.8)
    # «червоний» висновок
    s += rect(60, 286, 370, 42, LRED, RED, 1.4, 6)
    s += text(245, 304, "CMRR = наскільки точно збіглися R-и.", 12, INK, "middle", "bold")
    s += text(245, 320, "0.1% резистори → CMRR лише ~60–66 дБ.", 11.5, RED, "middle")

    # ── ПРАВА панель: чип ──
    s += rect(490, 56, 410, 280, "none", GREEN, 1.6, 10)
    s += text(695, 80, "Купити чип: 1 корпус + 1 Rg", 14, GREEN, "middle", "bold")
    # корпус
    s += rect(620, 120, 150, 120, "#f7f7f7", INK, 2.4, 8)
    s += text(695, 165, "IN-AMP", 18, INK, "middle", "bold")
    s += text(695, 188, "R-и підігнані", 11.5, GREEN, "middle", "italic")
    s += text(695, 206, "лазером на кристалі", 11, GREY, "middle", "italic")
    # входи / вихід
    s += line(598, 150, 620, 150, RED, 2); s += text(610, 144, "IN+", 9.5, RED, "middle", "bold")
    s += line(598, 210, 620, 210, BLUE, 2); s += text(610, 226, "IN−", 9.5, BLUE, "middle", "bold")
    s += line(770, 180, 800, 180, INK, 2); s += arrow(800, 180, 824, 180, INK, 1.8)
    s += text(816, 172, "OUT", 9.5, INK, "middle", "bold")
    # зовнішній Rg
    s += line(620, 175, 600, 175, GREEN, 2)
    s += line(620, 185, 600, 185, GREEN, 2)
    s += line(600, 175, 600, 185, GREEN, 2)
    s += rect(580, 171, 16, 18, "#ffffff", GREEN, 2, 3)
    s += text(572, 184, "Rg", 11, GREEN, "end", "bold")
    # «зелений» висновок
    s += rect(510, 286, 370, 42, LGRN, GREEN, 1.4, 6)
    s += text(695, 304, "Узгодженість гарантована заводом:", 12, INK, "middle", "bold")
    s += text(695, 320, "CMRR ~90–130 дБ «з коробки».", 11.5, GREEN, "middle")

    save("inamp-bridge-discrete-vs-chip.svg", s)


if __name__ == "__main__":
    fig_pinout_hookup()
    fig_discrete_vs_chip()
    print("done")
