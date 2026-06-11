# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки «Тиристор у crowbar-захисті» (тема 2.11.2).
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс crowbar-…), щоб не перетинатися з головним figs.py розділу 2.11.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано з figs.py
попередніх розділів модуля 2.
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
LSUN  = "#fbf3e0"
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


def poly(pts, col, wv=2.4, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="{fill}" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ───────────────────────── елементи схем ─────────────────────────

def node(cx, cy, color=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.4" fill="{color}"/>\n'


def res_v(cx, cy, h=44, label="", lab_dx=14, color=INK):
    """Вертикальний резистор (прямокутник IEC) з центром у (cx,cy)."""
    w = 16
    s = rect(cx - w / 2, cy - h / 2, w, h, "#ffffff", color, 2, 2)
    if label:
        s += text(cx + lab_dx, cy + 5, label, 14, color, "start")
    return s


def scr(cx, cy, color=INK):
    """Тиристор (SCR): трикутник + катодна риска + затвор. Анод зверху, катод знизу."""
    s = ""
    # анодний/катодний вивід
    s += line(cx, cy - 40, cx, cy - 18, color)
    s += line(cx, cy + 18, cx, cy + 40, color)
    # трикутник (вістрям донизу)
    s += poly([(cx - 16, cy - 18), (cx + 16, cy - 18), (cx, cy + 6)], color, 2.2, fill="#ffffff")
    # катодна риска
    s += line(cx - 16, cy + 6, cx + 16, cy + 6, color, 2.2)
    s += line(cx, cy + 6, cx, cy + 18, color)
    # затвор (від катодної риски управо-вниз)
    s += line(cx + 16, cy + 2, cx + 40, cy + 14, color, 2)
    return s


def fuse(x1, x2, y, color=INK, label=""):
    """Запобіжник: прямокутник із діагоналлю."""
    w = x2 - x1
    h = 16
    s = line(x1, y, x1 + w * 0.18, y, color)
    s += line(x2 - w * 0.18, y, x2, y, color)
    s += rect(x1 + w * 0.18, y - h / 2, w * 0.64, h, "#ffffff", color, 2, 3)
    s += line(x1 + w * 0.18, y - h / 2, x2 - w * 0.18, y + h / 2, color, 1.6)
    if label:
        s += text((x1 + x2) / 2, y - 16, label, 13, color, "middle")
    return s


def zener(cx, cy, color=INK):
    """Стабілітрон (Zener): катод зверху. Трикутник вістрям угору + Z-риска."""
    s = ""
    s += line(cx, cy - 36, cx, cy - 12, color)
    s += line(cx, cy + 12, cx, cy + 36, color)
    # трикутник вістрям угору (анод знизу)
    s += poly([(cx - 14, cy + 12), (cx + 14, cy + 12), (cx, cy - 12)], color, 2.2, fill="#ffffff")
    # катодна риска з Z-загинами
    s += line(cx - 14, cy - 12, cx + 14, cy - 12, color, 2.2)
    s += line(cx - 14, cy - 12, cx - 14, cy - 18, color, 2.2)
    s += line(cx + 14, cy - 12, cx + 14, cy - 6, color, 2.2)
    return s


# ───────────────────────── Рис. 2.11.2c.1 ─────────────────────────
# Принцип: перенапруга → защіпка SCR → коротке → запобіжник рве лінію.

def fig_principle():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Crowbar: «коротке замикання за командою»", 18, INK, "middle", "bold")

    # ── три кроки зліва направо ──
    boxes = [
        (40, 70, LGRN, "1 · Норма", GREEN),
        (290, 70, LSUN, "2 · Перенапруга", SUN),
        (540, 70, LRED, "3 · Спрацював crowbar", RED),
    ]
    bw, bh = 180, 300
    for (bx, by, fillc, title, edge) in boxes:
        s += rect(bx, by, bw, bh, fillc, edge, 1.8, 8)
        s += text(bx + bw / 2, by + 24, title, 15, edge, "middle", "bold")

    def supply_block(bx, by, vtxt, vcol):
        """Спрощене коло: джерело → запобіжник → шина → навантаження(плата)."""
        gx = bx + 26          # ліва шина (земля/мінус не малюємо явно)
        topx = bx + 90        # вертикаль живлення
        s = ""
        # горизонтальна лінія живлення (плюс) зверху
        s += line(bx + 22, by + 70, bx + bw - 22, by + 70, INK, 2)
        # запобіжник у лінії
        return s, gx, topx

    # Загальний макет однаковий у трьох колонках; різниться підсвітка/підписи.
    def draw_circuit(bx, by, mode):
        s = ""
        x_in = bx + 24            # вхід живлення
        x_fuse1 = bx + 38
        x_fuse2 = bx + 78
        x_bus = bx + 96           # вузол шини (тут висить crowbar і навантаження)
        x_load = bx + 150         # навантаження (плата)
        y_top = by + 70           # плюсова шина
        y_bot = by + 250          # мінусова шина (земля)

        # верхня плюсова шина: вхід → запобіжник → вузол
        s += line(x_in, y_top, x_fuse1, y_top, INK, 2)
        blown = (mode == "fire")
        fcol = RED if blown else INK
        s += fuse(x_fuse1, x_fuse2, y_top, fcol, "")
        if blown:
            # розрив запобіжника
            s += line(x_fuse1 + 17, y_top - 9, x_fuse2 - 17, y_top + 9, RED, 2.4)
            s += text((x_fuse1 + x_fuse2) / 2, y_top - 14, "горить", 12, RED, "middle", "bold")
        else:
            s += text((x_fuse1 + x_fuse2) / 2, y_top - 14, "fuse", 12, GREY, "middle")
        s += line(x_fuse2, y_top, x_bus, y_top, INK, 2)
        s += node(x_bus, y_top)

        # вхідна стрілка живлення
        s += arrow(x_in - 16, y_top, x_in, y_top, INK, 2)
        s += text(x_in - 18, y_top - 9, "вхід", 11, INK, "end")

        # нижня шина (земля)
        s += line(x_in, y_bot, x_load, y_bot, INK, 2)

        # crowbar (SCR) між шиною і землею
        cx = x_bus
        s += line(cx, y_top, cx, by + 96, INK, 2)
        scr_col = RED if mode == "fire" else INK
        s += scr(cx, by + 132, scr_col)
        s += line(cx, by + 172, cx, y_bot, INK, 2)
        s += node(cx, y_bot)
        if mode == "fire":
            # стрілка великого струму крізь SCR
            s += arrow(cx + 6, by + 100, cx + 6, by + 168, RED, 3)
            s += text(cx - 22, by + 134, "I", 14, RED, "end", "bold")
            s += text(cx - 46, by + 152, "велик.", 11, RED, "end")
        s += text(cx + 44, by + 138, "SCR", 12, scr_col, "start",
                  "bold" if mode == "fire" else "normal")

        # навантаження (плата) праворуч
        s += line(x_bus, y_top, x_load, y_top, INK, 2)
        s += rect(x_load - 14, by + 110, 30, 44, "#ffffff", INK, 2, 4)
        s += line(x_load + 1, y_top, x_load + 1, by + 110, INK, 2)
        s += line(x_load + 1, by + 154, x_load + 1, y_bot, INK, 2)
        s += text(x_load + 22, by + 128, "плата", 12, INK, "start")
        s += text(x_load + 22, by + 144, "(ICs)", 11, GREY, "start")

        # напруга на шині
        if mode == "norm":
            s += text(x_bus + 4, by + 60, "+5.0 В", 13, GREEN, "start", "bold")
            s += text(x_load + 22, by + 174, "живиться", 11, GREEN, "start")
        elif mode == "over":
            s += text(x_bus + 4, by + 60, "+9 В !", 13, SUN, "start", "bold")
            s += text(x_load + 22, by + 174, "ще ціла", 11, SUN, "start")
            # «здіймається» стрілка напруги
            s += arrow(x_bus - 30, by + 78, x_bus - 30, by + 56, SUN, 2.4)
        else:  # fire
            s += text(x_bus + 4, by + 60, "≈0 В", 13, RED, "start", "bold")
            s += text(x_load + 22, by + 174, "врятована", 11, RED, "start", "bold")
        return s

    s += draw_circuit(40, 70, "norm")
    s += draw_circuit(290, 70, "over")
    s += draw_circuit(540, 70, "fire")

    # підпис-логіка внизу
    s += text(W / 2, H - 16,
              "Поріг перевищено → затвор отримує імпульс → SCR замикає шину на землю → "
              "просадка живить запобіжник, він рве вхід.",
              12.5, INK, "middle")
    save("crowbar-principle.svg", s)


# ───────────────────────── Рис. 2.11.2c.2 ─────────────────────────
# Класична схема: стабілітрон-сенсор → резистор затвора → SCR; запобіжник у лінії.

def fig_sense_circuit():
    W, H = 720, 472
    s = header(W, H)
    s += text(W / 2, 30, "Класичний crowbar: сенсор на стабілітроні", 18, INK, "middle", "bold")

    x_in = 70
    x_fuse1 = 110
    x_fuse2 = 162
    x_bus = 220          # вузол: сюди приходить живлення після запобіжника
    x_load = 560         # навантаження (плата)
    y_top = 110          # плюсова шина
    y_bot = 350          # земля

    # ── плюсова шина: вхід → запобіжник → вузол → навантаження ──
    s += arrow(x_in - 26, y_top, x_in, y_top, INK, 2)
    s += text(x_in - 28, y_top - 10, "+Vживл.", 13, RED, "end", "bold")
    s += line(x_in, y_top, x_fuse1, y_top, INK, 2)
    s += fuse(x_fuse1, x_fuse2, y_top, INK, "")
    s += text((x_fuse1 + x_fuse2) / 2, y_top - 14, "запобіжник", 12, INK, "middle")
    s += line(x_fuse2, y_top, x_load + 1, y_top, INK, 2)
    s += node(x_bus, y_top)

    # ── земляна шина ──
    s += line(x_in, y_bot, x_load + 1, y_bot, INK, 2)
    s += node(x_bus, y_bot)
    # символ землі під вузлом сенсора
    gx = x_in + 6
    s += line(gx, y_bot, gx, y_bot + 14, INK, 2)
    s += line(gx - 12, y_bot + 14, gx + 12, y_bot + 14, INK, 2)
    s += line(gx - 7, y_bot + 19, gx + 7, y_bot + 19, INK, 2)
    s += line(gx - 3, y_bot + 24, gx + 3, y_bot + 24, INK, 2)

    # ── навантаження (плата) ──
    s += rect(x_load - 16, y_top + 80, 34, 80, "#ffffff", INK, 2, 5)
    s += line(x_load + 1, y_top, x_load + 1, y_top + 80, INK, 2)
    s += line(x_load + 1, y_top + 160, x_load + 1, y_bot, INK, 2)
    s += text(x_load + 26, y_top + 112, "плата", 13, INK, "start", "bold")
    s += text(x_load + 26, y_top + 130, "(чутливі", 11, GREY, "start")
    s += text(x_load + 26, y_top + 144, " мікросхеми)", 11, GREY, "start")

    # ── гілка сенсора: стабілітрон (з шини) → вузол A → резистор → земля ──
    sx = x_bus + 130
    s += node(sx, y_top)
    s += line(x_bus, y_top, sx, y_top, INK, 1.6)
    s += zener(sx, y_top + 52, BLUE)
    yA = y_top + 116          # вузол A — затвор
    s += node(sx, yA)
    s += text(sx - 18, y_top + 40, "Zener", 12, BLUE, "end")
    s += text(sx - 18, y_top + 58, "Vz", 12, BLUE, "end", "bold")
    # резистор затвора A→земля
    s += res_v(sx, yA + 56, 44, "Rg", 14, INK)
    s += line(sx, yA, sx, yA + 34, INK, 2)
    s += line(sx, yA + 78, sx, y_bot, INK, 2)
    s += node(sx, y_bot)

    # ── SCR (crowbar) між шиною й землею ──
    cx = x_bus
    s += line(cx, y_top, cx, y_top + 58, INK, 2)
    s += scr(cx, y_top + 96, RED)
    s += line(cx, y_top + 136, cx, y_bot, INK, 2)
    s += text(cx - 46, y_top + 100, "SCR", 13, RED, "end", "bold")
    s += text(cx - 38, y_top + 118, "crowbar", 11, RED, "end")

    # затвор SCR з'єднати з вузлом A (через резистор обмеження вже неявно — Rg)
    gxa = cx + 40
    s += line(gxa, y_top + 110, sx, yA, INK, 2)
    s += node(sx, yA)
    s += text((gxa + sx) / 2, yA - 8, "затвор", 11, GREEN, "middle")

    # ── пояснення внизу, під усією схемою (нижче землі y=374) ──
    bx, by = 60, 392
    s += rect(bx, by, 600, 64, "#fbfbf7", GREY, 1.4, 8)
    s += text(bx + 16, by + 24, "Поки V < Vz + Vgt:", 13, INK, "start", "bold")
    s += text(bx + 170, by + 24, "Zener мовчить, спад на Rg ≈ 0, SCR закритий — плата живиться.",
              13, INK, "start")
    s += text(bx + 16, by + 48, "V підскочила:", 13, RED, "start", "bold")
    s += text(bx + 170, by + 48, "Zener пробитий → імпульс струму на Rg і затвор → SCR защіпнувся.",
              13, RED, "start")

    save("crowbar-sense-circuit.svg", s)


if __name__ == "__main__":
    fig_principle()
    fig_sense_circuit()
    print("OK — фігури crowbar-вставки (Рис. 2.11.2c.1–2) згенеровано в", OUT)
