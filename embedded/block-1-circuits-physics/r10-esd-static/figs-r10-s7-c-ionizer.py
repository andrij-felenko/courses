# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки §1.10.7c
«Іонізатор повітря: нейтралізувати заряд там, де не можна заземлити».
Чистий Python, без залежностей. Вивід → ./img/.
Імена файлів УНІКАЛЬНІ (префікс fig-r10-s7c-ion-*); головний figs.py розділу
не чіпається. Стиль за AUTHORING §9: білий фон, sans-serif, спільні кольори,
«+» червоний, «−» синій, стрілки через marker.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#eef1f4"
AMBER = "#caa24a"
SAND  = "#fbf7ec"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey", GREEN: "aGreen", RED: "aRed", BLUE: "aBlue"}


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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(pts, color=INK, w=2.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round"/>\n')


def plus(cx, cy, r=6, color=RED, sw=2.4):
    s = circle(cx, cy, r, "#fff", color, sw)
    s += line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, sw)
    s += line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, sw)
    return s


def minus(cx, cy, r=6, color=BLUE, sw=2.4):
    s = circle(cx, cy, r, "#fff", color, sw)
    s += line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, sw)
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.10.7c.1 — чому дріт не допомагає ізолятору, а іонізатор допомагає ──
# Зліва: заряджений ізолятор + спроба заземлити дротом — заряд лишається на місці.
# Справа: той самий ізолятор під потоком біполярних іонів — заряд нейтралізовано.
def fig_why():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Дріт осушує лише провідник. Ізолятор нейтралізує лише повітря",
              20, INK, "middle", "bold")
    s += text(W / 2, 54, "заряд на пластику сидить там, де осів, і по дроту нікуди не стікає — потрібні іони з повітря",
              12.5, GREY, "middle", style="italic")

    pw = (W - 70) / 2 - 14
    # ── ліва панель: заземлення не діє ──
    lx = 40
    s += rect(lx, 80, pw, 350, FAINT, RED, 2, rx=10)
    s += text(lx + pw / 2, 106, "Спроба: заземлити ізолятор дротом", 14, RED, "middle", "bold")
    s += text(lx + pw / 2, 126, "— НЕ працює", 13, RED, "middle", "bold")

    # ізолятор-плитка з локальним зарядом (−), що сидить на місці
    bx, by, bw, bh = lx + 40, 160, pw - 80, 70
    s += rect(bx, by, bw, bh, "#f1ece0", "#b9ad8a", 2, rx=6)
    s += text(bx + bw / 2, by - 8, "заряджений ізолятор (пластик, плівка)", 11.5, "#6f6444", "middle", style="italic")
    # локальні − на поверхні
    for i in range(6):
        s += minus(bx + 24 + i * (bw - 48) / 5, by + 18, 6.5)
    s += text(bx + bw / 2, by + 46, "заряд осів локально й нерухомий", 11, BLUE, "middle")

    # дріт «на землю»
    gx = lx + pw / 2
    s += line(bx + bw, by + bh, bx + bw + 22, by + bh, INK, 2)
    s += line(bx + bw + 22, by + bh, bx + bw + 22, by + bh + 70, INK, 2)
    # символ землі
    gy = by + bh + 70
    s += line(bx + bw + 22 - 16, gy, bx + bw + 22 + 16, gy, INK, 2.4)
    s += line(bx + bw + 22 - 10, gy + 6, bx + bw + 22 + 10, gy + 6, INK, 2.2)
    s += line(bx + bw + 22 - 5, gy + 12, bx + bw + 22 + 5, gy + 12, INK, 2)
    # перекреслений шлях стікання
    s += text(bx + bw - 6, by + bh + 30, "✕", 24, RED, "middle", "bold")
    s += text(lx + pw / 2, 372, "по ізолятору заряд не доходить до дроту:", 11.5, INK, "middle")
    s += text(lx + pw / 2, 390, "немає вільних носіїв, провідності немає (§1.2.8)", 11.5, INK, "middle")
    s += text(lx + pw / 2, 412, "поверхня лишається зарядженою", 12, RED, "middle", "bold")

    # ── права панель: іонізатор діє ──
    rx0 = 40 + pw + 28
    s += rect(rx0, 80, pw, 350, FAINT, GREEN, 2, rx=10)
    s += text(rx0 + pw / 2, 106, "Рішення: облити поверхню", 14, GREEN, "middle", "bold")
    s += text(rx0 + pw / 2, 126, "біполярними іонами повітря", 13, GREEN, "middle", "bold")

    # іонізатор зверху (емітер з вістрям)
    ex = rx0 + pw / 2
    s += rect(ex - 46, 142, 92, 22, "#dfe5ea", GREY, 1.6, rx=5)
    s += text(ex, 157, "іонізатор", 11, INK, "middle", "bold")
    s += line(ex, 164, ex, 176, GREY, 2)
    # хмара іонів обох знаків, що падають до поверхні
    ions = [(-58, 0), (-30, 12), (-6, -4), (20, 10), (46, 2), (62, 14)]
    signs = [RED, BLUE, RED, BLUE, RED, BLUE]
    for (dx, dy), col in zip(ions, signs):
        if col == RED:
            s += plus(ex + dx, 188 + dy, 5.5)
        else:
            s += minus(ex + dx, 188 + dy, 5.5)

    # та сама плитка, але вже з притягнутим + до кожного −
    bx2 = rx0 + 40
    s += rect(bx2, 232, bw, bh, "#eef3ee", GREEN, 2, rx=6)
    s += text(bx2 + bw / 2, 226, "той самий ізолятор", 11.5, "#3a6f44", "middle", style="italic")
    for i in range(6):
        cx = bx2 + 24 + i * (bw - 48) / 5
        s += minus(cx - 6, 250, 6)
        s += plus(cx + 6, 250, 6)
        # стрілка падіння +-іона на −
        s += arrow(cx + 6, 210, cx + 6, 242, RED, 1.6)
    s += text(bx2 + bw / 2, 280, "+ з повітря сідають на − поверхні → 0", 11, GREEN, "middle", "bold")

    s += text(rx0 + pw / 2, 372, "поверхня сама притягує іон протилежного", 11.5, INK, "middle")
    s += text(rx0 + pw / 2, 390, "знаку — і нейтралізується за секунди", 11.5, INK, "middle")
    s += text(rx0 + pw / 2, 412, "заземлення не потрібне", 12, GREEN, "middle", "bold")

    save("fig-r10-s7c-ion-why.svg", s)


# ── Рис. 1.10.7c.2 — будова й дві ключові цифри: баланс і час спаду ──
def fig_specs():
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 32, "Будова іонізатора і дві цифри, за якими його судять", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "корона на вістрі (§1.10.3) народжує іони; вентилятор несе їх до деталі",
              12.5, GREY, "middle", style="italic")

    # ── верх: блок-схема тракту ──
    by = 90
    boxes = [
        (40,  "Високовольтне\nживлення\n(кВ, AC або DC)", BLUE),
        (250, "Емітер-вістря\nкорона (§1.10.3)\nіони + і −", RED),
        (470, "Вентилятор\nнесе іони\nдо зони", GREEN),
        (690, "Заряджена\nдеталь / поверхня\nнейтралізується", INK),
    ]
    bw, bh = 170, 78
    for i, (x, label, col) in enumerate(boxes):
        s += rect(x, by, bw, bh, SAND if col is INK else "#ffffff", col, 2, rx=8)
        lines = label.split("\n")
        for j, ln in enumerate(lines):
            wt = "bold" if j == 0 else "normal"
            s += text(x + bw / 2, by + 24 + j * 18, ln, 12 if j == 0 else 11.5,
                      col, "middle", wt)
        if i < len(boxes) - 1:
            s += arrow(x + bw, by + bh / 2, x + bw + 38, by + bh / 2, INK, 2.4)

    # вістря-емітер крупним планом (під другим боксом)
    ex = 250 + bw / 2
    ny = by + bh + 26
    s += line(ex, ny, ex, ny + 16, GREY, 3)
    # гостряк
    s += polyline([(ex - 8, ny + 16), (ex, ny + 30), (ex + 8, ny + 16)], RED, 2.4)
    # короткі промені корони
    for a in (-40, -20, 0, 20, 40):
        import math
        rad = math.radians(a - 90)
        s += line(ex, ny + 30, ex + 22 * math.cos(rad), ny + 30 + 22 * math.sin(rad),
                  RED, 1.4, dash="2 3")
    s += plus(ex - 26, ny + 44, 5)
    s += minus(ex + 26, ny + 44, 5)
    s += text(ex, ny + 64, "поле біля вістря ≫ середнього (§1.10.3)", 11, "#6f6444", "middle", style="italic")

    # ── низ: дві криві спаду напруги пластини (charged-plate monitor) ──
    gx0, gy0 = 70, 300
    gw, gh = W - 140, 150
    s += rect(gx0, gy0, gw, gh, "#fff", GREY, 1.4, rx=6)
    # осі
    s += line(gx0 + 50, gy0 + 18, gx0 + 50, gy0 + gh - 26, INK, 2)
    s += line(gx0 + 50, gy0 + gh - 26, gx0 + gw - 20, gy0 + gh - 26, INK, 2)
    s += text(gx0 + 50 - 8, gy0 + 14, "U пластини", 11.5, INK, "end", "bold")
    s += text(gx0 + gw - 20, gy0 + gh - 8, "час, с", 11.5, INK, "end", "bold")

    bx, byb = gx0 + 50, gy0 + gh - 26          # початок осей
    top = gy0 + 24
    # старт із +1000 В і спад до ~0 за ~10 с (хороший іонізатор)
    import math
    pts_fast = []
    for k in range(0, 121):
        t = k / 12.0
        u = 1000.0 * math.exp(-t / 2.2)
        x = bx + (t / 10.0) * (gw - 80)
        y = byb - (u / 1100.0) * (byb - top)
        pts_fast.append((x, y))
    s += polyline(pts_fast, GREEN, 3)
    s += text(pts_fast[20][0] + 6, pts_fast[20][1] - 6, "час спаду ~ кілька секунд", 11.5, GREEN, "start", "bold")

    # рівень +1000 В і ціль ~0
    s += line(bx, top, bx + gw - 80, top, FAINT, 1.4)
    s += text(bx - 6, top + 4, "+1000", 10.5, GREY, "end", font=MONO)
    s += text(bx - 6, byb + 4, "0", 10.5, GREY, "end", font=MONO)

    # офсет (баланс): лінія, що сіла НЕ на 0, а на невелику напругу
    off_y = byb - (40.0 / 1100.0) * (byb - top)
    s += line(bx, off_y, bx + gw - 80, off_y, AMBER, 1.8, dash="5 4")
    s += text(bx + gw - 84, off_y - 6, "залишковий офсет (баланс): ±кілька В — добре", 11, "#8a6a14", "end", "bold")

    # дві цифри-плашки
    s += rect(gx0 + gw - 250, gy0 + 22, 232, 44, SAND, AMBER, 1.8, rx=8)
    s += text(gx0 + gw - 250 + 12, gy0 + 40, "1) баланс (offset): чим ближче до 0 В", 11, "#8a6a14", "start", "bold")
    s += text(gx0 + gw - 250 + 12, gy0 + 58, "2) час спаду: 1000→100 В за < ~20 с", 11, "#8a6a14", "start", "bold")

    save("fig-r10-s7c-ion-specs.svg", s)


if __name__ == "__main__":
    fig_why()
    fig_specs()
    print("done.")
