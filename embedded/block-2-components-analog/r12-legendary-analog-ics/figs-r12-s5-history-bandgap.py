# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки §2.12.5
«Відлар, Брокау і bandgap» (Модуль 2, Розділ 2.12).

Чистий Python без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-12-5i-...), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон, sans-serif, '+' червоний, '−' синій,
поле зелене, стрілки через marker. Допоміжні функції скопійовано з
попередніх розділів задля єдиного вигляду.
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


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ───────────────────────── Рис. 2.12.5i.1 — лінія часу ─────────────────────────
def fig_timeline():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Як ідея bandgap дозрівала в прилад", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "опорна напруга з фізики PN-переходу, а не з пробою стабілітрона",
              14, GREY, "middle", style="italic")

    axis_y = 130
    x0, x1 = 70, W - 40
    s += line(x0, axis_y, x1, axis_y, INK, 2.5)
    s += arrow(x1 - 2, axis_y, x1 + 18, axis_y, INK, 2.5)

    # роки рівномірно по осі (нелінійно — просто рознесені віхи)
    nodes = [
        (0.04, "1963–64", "Гілбайбер", "Fairchild", "ідея й перший\nпатент: опора\nз ширини зони", RED),
        (0.33, "1971", "Відлар", "National Semi.", "LM113 — перша\nготова ІМС-опора\n1.220 В", BLUE),
        (0.62, "1974", "Брокау", "Analog Devices", "проста комірка\nна 2 транзистори\n→ AD580", GREEN),
        (0.90, "1977", "TL431", "Texas Instr.", "програмована\nопора-стабілітрон\n(всередині bandgap)", SUN),
    ]
    span = x1 - x0
    for fx, yr, who, org, desc, col in nodes:
        cx = x0 + fx * span
        s += line(cx, axis_y, cx, axis_y, col)
        s += circle(cx, axis_y, 8, col, INK, 2)
        s += text(cx, axis_y - 16, yr, 16, col, "middle", "bold")
        # картка під віссю
        bw, bh = 178, 168
        bx = cx - bw / 2
        by = axis_y + 30
        fill = {RED: LRED, BLUE: LBLUE, GREEN: LGRN, SUN: LSUN}[col]
        s += rect(bx, by, bw, bh, fill, col, 1.8, 10)
        s += text(cx, by + 28, who, 17, INK, "middle", "bold")
        s += text(cx, by + 49, org, 13, GREY, "middle", style="italic")
        s += line(bx + 16, by + 60, bx + bw - 16, by + 60, col, 1)
        for i, ln in enumerate(desc.split("\n")):
            s += text(cx, by + 84 + i * 20, ln, 13.5, INK, "middle")

    s += text(W / 2, H - 14,
              "Один опублікував принцип · другий зробив прилад · третій спростив його · далі — масовий продукт",
              13, GREY, "middle", style="italic")
    save("fig-12-5i-1-bandgap-timeline.svg", s)


# ───────────────────── Рис. 2.12.5i.2 — складання двох нахилів ─────────────────────
def fig_principle():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 32, "Фокус bandgap: скласти два протилежні нахили в нуль",
              20, INK, "middle", "bold")

    # осі
    ox, oy = 95, 360          # початок координат
    ax_w, ax_h = 600, 270
    top = oy - ax_h
    s += line(ox, oy, ox + ax_w, oy, INK, 2.2)      # вісь T
    s += arrow(ox + ax_w - 2, oy, ox + ax_w + 16, oy, INK, 2.2)
    s += line(ox, oy, ox, top, INK, 2.2)            # вісь U
    s += arrow(ox, top + 2, ox, top - 16, INK, 2.2)
    s += text(ox + ax_w + 14, oy + 5, "T, °C", 14, INK, "start")
    s += text(ox - 12, top - 4, "напруга", 14, INK, "end")

    # температурна шкала
    for i, tlab in enumerate(["−40", "+25", "+85", "+125"]):
        tx = ox + (i + 0.5) * ax_w / 4
        s += line(tx, oy, tx, oy + 5, GREY, 1.4)
        s += text(tx, oy + 22, tlab, 12, GREY, "middle")

    def Y(volts):
        # 0 В → oy, 1.4 В → top
        return oy - (volts / 1.4) * ax_h

    xL, xR = ox + 6, ox + ax_w - 30

    # CTAT: Vbe одного переходу, ~0.65 В при +25, нахил −2 мВ/°C (синій, спадає)
    yL = Y(0.78); yR = Y(0.46)
    s += _poly([(xL, yL), (xR, yR)], BLUE, 3)
    s += text(xR + 8, yR + 4, "V_BE", 14, BLUE, "start", "bold")
    s += text(xR + 8, yR + 22, "−2 мВ/°C", 11.5, BLUE, "start")
    s += text(xL + 8, yL - 10, "падає з нагрівом (CTAT)", 12.5, BLUE, "start")

    # PTAT: масштабований ΔVbe, росте (червоний)
    yL2 = Y(0.42); yR2 = Y(0.74)
    s += _poly([(xL, yL2), (xR, yR2)], RED, 3)
    s += text(xR + 8, yR2 + 4, "K·ΔV_BE", 14, RED, "start", "bold")
    s += text(xR + 8, yR2 + 22, "+ (росте)", 11.5, RED, "start")
    s += text(xL + 8, yL2 + 20, "PTAT: K разів різниця двох V_BE", 12.5, RED, "start")

    # сума — пласка лінія ~1.205 В (зелена), з легким горбом
    ysum = Y(1.205)
    bump = []
    for i in range(0, 41):
        fx = i / 40.0
        x = xL + fx * (xR - xL)
        # параболічний «горб» — реальна bandgap-опора має кривину ~кілька мВ
        y = ysum - 7 * (1 - (2 * fx - 1) ** 2) * 0.35
        bump.append((x, y))
    s += _poly(bump, GREEN, 3.4)
    s += text(xL + 8, ysum - 14, "СУМА ≈ 1.205 В — майже пласка", 13.5, GREEN, "start", "bold")
    s += line(ox, ysum, xR, ysum, GREEN, 1, dash="3,4")
    s += text(ox - 8, ysum + 4, "1.2", 12, GREEN, "end")

    # пунктир «ширина зони кремнію при 0 K»
    ygap = Y(1.205)
    s += text(ox + ax_w / 2, top - 6,
              "рівень = ширина забороненої зони кремнію, продовжена до 0 K (≈1.205 В)",
              12.5, GREEN, "middle", style="italic")

    # підпис-формула знизу
    s += rect(ox, oy + 40, ax_w, 44, "#fbfbfb", FAINT, 1.4, 8)
    s += text(ox + ax_w / 2, oy + 67,
              "V_REF = V_BE  +  K · ΔV_BE     (мінус ↓  плюс ↑  =  ≈0 мВ/°C)",
              15, INK, "middle", "bold")
    save("fig-12-5i-2-bandgap-sum.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_principle()
    print("done")
