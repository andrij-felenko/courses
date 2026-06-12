# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки §1.8.5c —
«Реле, соленоїд, електромагнітний клапан: електромагніт як актуатор».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена s5c-*).
НЕ чіпає головний figs.py розділу (за §9 — самодостатній скрипт).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; sans-serif.
Нумерація підписів у тексті: Рис. 1.8.5c.k.
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
ORANGE = "#e08030"
COPPER = "#cf8b5e"
COPEDGE = "#9c6038"
IRON = "#9aa3ad"
IRONFILL = "#dfe3e8"
FIELD = "#1f8a3b"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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


def plus(cx, cy, r=11, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=11, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def coil(x, y, w, h, turns=7, color=COPPER, edge=COPEDGE):
    """Котушка як ряд кілець (поперечний переріз обмотки) на каркасі x..x+w."""
    out = rect(x, y, w, h, "#ffffff", edge, 1.3, 3)
    step = w / turns
    for i in range(turns):
        cx = x + step * (i + 0.5)
        out += (f'<ellipse cx="{cx:.1f}" cy="{y + h / 2:.1f}" rx="{step*0.34:.1f}" '
                f'ry="{h/2 - 3:.1f}" fill="{color}" stroke="{edge}" stroke-width="1.1"/>\n')
    return out


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.8.5c.1 — спільне серце: котушка тягне якір ────────────────────────
def fig_core():
    W, H = 900, 472
    s = header(W, H)
    s += text(W / 2, 30, "Спільне серце всіх трьох: котушка тягне залізо в себе", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "подав струм — поле всмоктує рухомий якір; зняв струм — пружина повертає його назад",
              12.5, GREY, "middle", style="italic")

    def spring(x_left, x_right, ymid, color=INK):
        """Зиґзаг-пружина від x_left до стінки на x_right; n зубців підлаштовується."""
        out = ""
        n = 9
        step = (x_right - x_left) / n
        pts = []
        for k in range(n + 1):
            px = x_left + k * step
            py = ymid + (-7 if k % 2 else 7)
            pts.append(f"{px:.1f},{py:.1f}")
        out += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="1.8"/>\n'
        out += line(x_right, ymid - 14, x_right, ymid + 14, color, 2.4)  # стінка-опора
        return out

    panel_y, panel_h, pw = 84, 350, 380
    coil_y, coil_h = 198, 64
    arm_y, arm_h = 212, 36
    ymid = arm_y + arm_h / 2  # 230

    # ── ЛІВА панель: котушка ЗНЕСТРУМЛЕНА ──
    lx = 30
    s += rect(lx, panel_y, pw, panel_h, "#fcfcfc", FAINT, 1.4, 8)
    s += text(lx + pw / 2, 108, "СТРУМУ НЕМА", 14, GREY, "middle", "bold")
    s += text(lx + pw / 2, 126, "пружина тримає якір зовні (контакт розімкнено)", 11.5, GREY, "middle")

    coil_x, coil_w = lx + 56, 150
    s += rect(lx + 22, 204, 34, 52, IRONFILL, IRON, 2, 3)   # нерухомий стоп-осердя
    s += text(lx + 39, 278, "стоп", 10.5, GREY, "middle")
    s += coil(coil_x, coil_y, coil_w, coil_h, 7, "#d7d7d7", "#a8a8a8")  # сіра (без струму)
    s += text(coil_x + coil_w / 2, 192, "котушка", 11.5, GREY, "middle")

    # якір зовні (зсунутий праворуч), пружина розтиснута до стінки панелі
    arm_x = lx + 196
    s += rect(arm_x, arm_y, 86, arm_h, IRONFILL, IRON, 2, 3)
    s += text(arm_x + 43, arm_y + 23, "якір", 11, INK, "middle", "bold")
    s += spring(arm_x + 86, lx + pw - 16, ymid, INK)
    s += text(arm_x + 118, arm_y - 4, "пружина", 10.5, INK, "middle")

    # ── ПРАВА панель: котушка ПІД СТРУМОМ ──
    rx = lx + pw + 50  # 460
    s += rect(rx, panel_y, pw, panel_h, "#fbfdf8", "#c7e0c2", 1.4, 8)
    s += text(rx + pw / 2, 108, "СТРУМ УВІМКНЕНО", 14, GREEN, "middle", "bold")
    s += text(rx + pw / 2, 126, "поле всмоктує якір — пружина стиснута (контакт замкнено)", 11.5, GREEN, "middle")

    coil_x2 = rx + 56
    s += rect(rx + 22, 204, 34, 52, IRONFILL, IRON, 2, 3)   # стоп
    s += text(rx + 39, 278, "стоп", 10.5, GREY, "middle")
    s += coil(coil_x2, coil_y, coil_w, coil_h, 7, COPPER, COPEDGE)  # мідна (під струмом)

    # силові лінії поля крізь котушку (зелені) — поле «закручене» в осерді
    for dy in (-1, 1):
        yy = coil_y + coil_h / 2 + dy * 20
        s += f'<path d="M {coil_x2+8:.1f},{yy:.1f} L {coil_x2+coil_w-8:.1f},{yy:.1f}" fill="none" stroke="{FIELD}" stroke-width="1.4" stroke-dasharray="5 4"/>\n'
    s += arrow(coil_x2 + coil_w - 30, coil_y + coil_h / 2 - 20, coil_x2 + coil_w - 10, coil_y + coil_h / 2 - 20, FIELD, 1.4)
    s += text(coil_x2 + coil_w / 2, 192, "поле B (§1.8.5)", 11.5, FIELD, "middle", "bold")

    # якір ВТЯГНУТО до стопу; пружина стиснута, стрілка тяги
    arm_x2 = rx + 150
    s += rect(arm_x2, arm_y, 86, arm_h, IRONFILL, IRON, 2, 3)
    s += text(arm_x2 + 43, arm_y + 23, "якір", 11, INK, "middle", "bold")
    s += arrow(arm_x2 + 124, ymid, arm_x2 + 92, ymid, RED, 3)
    s += text(arm_x2 + 134, arm_y - 4, "тяга F", 13, RED, "start", "bold")
    s += spring(arm_x2 + 86, rx + pw - 16, ymid, INK)

    # провід живлення котушки
    for px0 in (coil_x2 + 24, coil_x2 + coil_w - 24):
        s += line(px0, coil_y + coil_h, px0, coil_y + coil_h + 24, COPEDGE, 2)
    s += line(coil_x2 + 24, coil_y + coil_h + 24, coil_x2 + coil_w - 24, coil_y + coil_h + 24, COPEDGE, 2)
    s += text(coil_x2 + coil_w / 2, coil_y + coil_h + 42, "котушка під напругою", 11, COPEDGE, "middle")

    # нижній підпис-висновок на всю ширину
    s += text(W / 2, 458, "Це й є електромагніт-актуатор: керований струмом «магнітний кулак», що смикає залізо. Далі важить лише, ЩО причеплено до якоря.",
              12.5, INK, "middle", style="italic")
    save("s5c-1-core.svg", s)


# ── Рис. 1.8.5c.2 — три пристрої з одного серця + блок керування ─────────────
def fig_three():
    W, H = 880, 540
    s = header(W, H)
    s += text(W / 2, 30, "Один механізм — три пристрої: що причеплено до якоря", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "реле рухає контакти · соленоїд штовхає тягу · клапан перекриває отвір",
              12.5, GREY, "middle", style="italic")

    panel_y, panel_h = 74, 312
    pw = 270
    gap = 16
    x0 = 20

    def coil_block(cx, cy):
        out = coil(cx, cy, 92, 50, 6, COPPER, COPEDGE)
        out += text(cx + 46, cy - 6, "котушка", 10.5, COPEDGE, "middle")
        return out

    # ── Панель 1: РЕЛЕ ──
    px = x0
    s += rect(px, panel_y, pw, panel_h, "#fcfcfc", FAINT, 1.4, 8)
    s += text(px + pw / 2, panel_y + 24, "РЕЛЕ (relay)", 15, INK, "middle", "bold")
    s += text(px + pw / 2, panel_y + 42, "якір замикає КОНТАКТИ", 11, GREY, "middle")
    s += coil_block(px + 26, panel_y + 70)
    # коромисло-якір
    pivot_x, pivot_y = px + 150, panel_y + 76
    s += circle(pivot_x, pivot_y, 4, INK, INK, 1)
    s += line(pivot_x, pivot_y, px + 60, panel_y + 70, IRON, 6)   # тягнеться до котушки
    s += line(pivot_x, pivot_y, px + 210, panel_y + 118, IRON, 6)  # вільний кінець вниз
    s += text(px + 96, panel_y + 60, "якір", 10.5, INK, "middle", "bold")
    # контакти COM / NO / NC
    s += line(px + 210, panel_y + 118, px + 210, panel_y + 150, INK, 2)
    s += circle(px + 210, panel_y + 152, 4, RED, RED, 1)
    s += text(px + 210, panel_y + 170, "COM", 10, RED, "middle", "bold")
    s += circle(px + 178, panel_y + 132, 4, INK, INK, 1)
    s += text(px + 168, panel_y + 128, "NC", 10, GREY, "end")
    s += circle(px + 242, panel_y + 132, 4, INK, INK, 1)
    s += text(px + 252, panel_y + 128, "NO", 10, GREEN, "start")
    s += text(px + pw / 2, panel_y + 210, "силове коло й логіка —", 11, INK, "middle")
    s += text(px + pw / 2, panel_y + 226, "РОЗДІЛЕНІ (гальв. розв'язка)", 11, INK, "middle", "bold")
    s += text(px + pw / 2, panel_y + 256, "комутує AC чи DC,", 11, GREY, "middle")
    s += text(px + pw / 2, panel_y + 272, "великі струми «однією лапкою»", 11, GREY, "middle")

    # ── Панель 2: СОЛЕНОЇД ──
    px = x0 + (pw + gap)
    s += rect(px, panel_y, pw, panel_h, "#fcfcfc", FAINT, 1.4, 8)
    s += text(px + pw / 2, panel_y + 24, "СОЛЕНОЇД (solenoid)", 15, INK, "middle", "bold")
    s += text(px + pw / 2, panel_y + 42, "якір ШТОВХАЄ/ТЯГНЕ тягу", 11, GREY, "middle")
    # котушка горизонтально, плунжер всередині
    csx, csy = px + 40, panel_y + 96
    s += coil(csx, csy, 130, 54, 8, COPPER, COPEDGE)
    s += text(csx + 65, csy - 8, "котушка", 10.5, COPEDGE, "middle")
    # плунжер (рухомий стрижень) виходить праворуч
    s += rect(csx + 60, csy + 16, 130, 22, IRONFILL, IRON, 2, 3)
    s += text(csx + 95, csy + 31, "плунжер", 10, INK, "middle", "bold")
    s += arrow(csx + 150, csy + 60, csx + 110, csy + 60, RED, 2.6)
    s += text(csx + 168, csy + 64, "хід", 11, RED, "start", "bold")
    # навантаження (засувка) на кінці
    s += rect(csx + 190, csy + 8, 16, 38, "#e7e7e7", GREY, 1.6, 2)
    s += text(px + pw / 2, panel_y + 210, "перетворює струм на", 11, INK, "middle")
    s += text(px + pw / 2, panel_y + 226, "ЛІНІЙНИЙ РУХ і силу", 11, INK, "middle", "bold")
    s += text(px + pw / 2, panel_y + 256, "засувки, замки, штовхачі,", 11, GREY, "middle")
    s += text(px + pw / 2, panel_y + 272, "пневмо/гідророзподільники", 11, GREY, "middle")

    # ── Панель 3: КЛАПАН ──
    px = x0 + 2 * (pw + gap)
    s += rect(px, panel_y, pw, panel_h, "#fcfcfc", FAINT, 1.4, 8)
    s += text(px + pw / 2, panel_y + 24, "КЛАПАН (solenoid valve)", 15, INK, "middle", "bold")
    s += text(px + pw / 2, panel_y + 42, "якір ПЕРЕКРИВАЄ ОТВІР", 11, GREY, "middle")
    cvx, cvy = px + 90, panel_y + 70
    s += coil(cvx, cvy, 90, 46, 6, COPPER, COPEDGE)
    s += text(cvx + 45, cvy - 6, "котушка", 10.5, COPEDGE, "middle")
    # тіло клапана: труба з сідлом
    tube_y = panel_y + 150
    s += rect(px + 28, tube_y, 214, 40, "#eef3f8", "#9bb6cf", 1.8, 4)
    s += line(px + 28, tube_y + 20, px + 110, tube_y + 20, BLUE, 3)   # потік вхід
    s += arrow(px + 60, tube_y + 20, px + 96, tube_y + 20, BLUE, 3)
    # сідло-отвір + плунжер-голка зверху
    s += rect(px + 118, tube_y - 4, 24, 8, "#cfcfcf", GREY, 1.4, 1)
    s += rect(cvx + 36, cvy + 46, 18, tube_y - (cvy + 46), IRONFILL, IRON, 2, 2)  # шток
    s += rect(px + 116, tube_y + 4, 28, 14, IRONFILL, IRON, 1.8, 2)  # голка-затвор у сідлі
    s += text(px + 130, tube_y + 36, "сідло", 10, GREY, "middle")
    s += line(px + 150, tube_y + 20, px + 242, tube_y + 20, GREY, 3, "5 4")  # вихід (поки перекрито)
    s += text(px + pw / 2, panel_y + 230, "немає струму — пружина", 11, INK, "middle")
    s += text(px + pw / 2, panel_y + 246, "тримає клапан (NC),", 11, INK, "middle")
    s += text(px + pw / 2, panel_y + 262, "струм відкриває потік", 11, GREEN, "middle", "bold")

    # ── НИЖНІЙ блок: ланцюг керування + граблі (на всю ширину) ──
    by = panel_y + panel_h + 18
    s += rect(x0, by, W - 2 * x0, 92, "#fbfbf4", "#c9c178", 1.6, 8)
    s += text(x0 + 16, by + 24, "Як це вмикає мікроконтролер (спільне для всіх трьох):", 13.5, INK, "start", "bold")

    # блок-схема MCU → драйвер → котушка
    bxs = x0 + 24
    yb = by + 56
    def box(x, w, label, col=INK):
        out = rect(x, yb - 18, w, 34, "#ffffff", col, 1.8, 5)
        out += text(x + w / 2, yb + 4, label, 12, col, "middle", "bold")
        return out, x + w
    blk, nx = box(bxs, 92, "МК (3.3 В)")
    s += blk
    s += arrow(nx, yb, nx + 30, yb, INK, 2.2)
    blk, nx = box(nx + 30, 150, "ключ-драйвер", INK)
    s += blk
    s += arrow(nx, yb, nx + 30, yb, INK, 2.2)
    blk, nx = box(nx + 30, 110, "котушка", COPEDGE)
    s += blk
    # гасний діод над котушкою
    s += text(nx + 70, yb - 22, "⊳⊢ гасний діод", 11.5, RED, "middle", "bold")
    s += arrow(nx + 70, yb - 12, nx + 70, yb - 2, RED, 1.8)
    s += text(nx + 70, yb + 6, "(на котушці)", 9.5, RED, "middle")

    # текст-попередження праворуч
    wx = bxs + 560
    s += text(wx, yb - 6, "⚠ Котушка індуктивна: при розмиканні дає різкий", 11.5, RED, "start", "bold")
    s += text(wx, yb + 10, "сплеск напруги — потрібен гасний діод (механізм — далі, §2.2).", 11.5, GREY, "start")

    save("s5c-2-three.svg", s)


if __name__ == "__main__":
    fig_core()
    fig_three()
    print("done")
