# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки 2.9.2c
«Absolute Maximum на практиці: латч-ап, перенапруга на вході, гаряче підключення».
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена fig-r09-2c-*).
Головний figs.py розділу НЕ чіпаємо; допоміжні функції скопійовано звідти (AUTHORING §9).
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
LYEL  = "#fdf4dd"
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


def poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def filt(pts, col):
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" fill="{col}" stroke="none"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def diode(x, y, vert=True, up=True, col=INK):
    """Маленький символ діода. Трикутник + риска. up=True: струм проводить угору."""
    s = ""
    sz = 9
    if vert:
        if up:  # катод зверху, провідність угору
            s += filt([(x - sz, y + sz), (x + sz, y + sz), (x, y - sz)], col)
            s += line(x - sz, y - sz, x + sz, y - sz, col, 2.4)
        else:
            s += filt([(x - sz, y - sz), (x + sz, y - sz), (x, y + sz)], col)
            s += line(x - sz, y + sz, x + sz, y + sz, col, 2.4)
    return s


# ── Рис. 2.9.2c.1 — захисні діоди на вході ───────────────────────────────────
def fig_clamp():
    W, H = 720, 380
    s = header(W, H)
    s += text(W / 2, 30, "Захисні діоди на вході — і коли вони відмикаються", 16, INK, "middle", "bold")

    # рейки
    vy, gy = 78, 300
    rx0, rx1 = 90, 470
    s += line(rx0, vy, rx1, vy, RED, 3)
    s += text(rx0 - 6, vy - 8, "Vcc (рейка +)", 12, RED, "start", "bold")
    s += line(rx0, gy, rx1, gy, BLUE, 3)
    s += text(rx0 - 6, gy + 20, "GND (рейка −)", 12, BLUE, "start", "bold")

    # вузол входу (ніжка)
    px = 250
    s += line(px, 130, px, 248, INK, 2.6)
    s += circle(px, 189, 4, INK, INK, 1)
    # вхідна ніжка ліворуч
    s += arrow(150, 189, px, 189, GREY, 2.4)
    s += text(120, 175, "вхід", 12, INK, "middle", "bold")
    s += text(120, 192, "(ніжка)", 9.5, GREY, "middle")
    # лінія всередину чипа
    s += line(px, 189, 360, 189, INK, 2.6)
    s += rect(360, 150, 95, 80, "#eef2f7", "#7f93a8", 2, 8)
    s += text(407, 185, "логіка", 11, INK, "middle", "bold")
    s += text(407, 202, "чипа", 11, INK, "middle")

    # верхній діод: від ніжки до Vcc (проводить угору при вході > Vcc)
    s += diode(px, 152, True, True, INK)
    s += text(px + 16, 150, "до Vcc", 10, GREY, "start")
    # нижній діод: від GND до ніжки (проводить угору; відкривається при вході < GND)
    s += diode(px, 268, True, True, INK)
    s += text(px + 16, 272, "до GND", 10, GREY, "start")

    # шкала станів праворуч
    bx = 530
    s += line(bx, vy, bx, gy, INK, 2)
    s += text(bx, vy - 14, "напруга на вході", 11, INK, "middle", "bold")
    # зелена зона 0..Vcc
    s += rect(bx + 4, vy, 150, gy - vy, LGRN, "none", 0)
    s += text(bx + 12, (vy + gy) / 2 - 6, "0 … Vcc:", 11, GREEN, "start", "bold")
    s += text(bx + 12, (vy + gy) / 2 + 12, "обидва діоди", 10, INK, "start")
    s += text(bx + 12, (vy + gy) / 2 + 28, "закриті — мовчать", 10, INK, "start")
    # верх — вище Vcc
    s += rect(bx + 4, vy - 34, 150, 28, LRED, "none", 0)
    s += text(bx + 12, vy - 14, "> Vcc+0.6: верхній відкрито →", 9.5, RED, "start", "bold")
    # низ — нижче GND
    s += rect(bx + 4, gy + 6, 150, 28, LRED, "none", 0)
    s += text(bx + 12, gy + 24, "< −0.6: нижній відкрито →", 9.5, RED, "start", "bold")

    s += text(W / 2, H - 16, "Поки сигнал між рейками — діоди закриті. Вийшов за рейку — відмикається, і крізь ніжку рине струм.",
              10.5, GREY, "middle", style="italic")
    save("fig-r09-2c-1-clamp-diodes.svg", s)


# ── Рис. 2.9.2c.2 — латч-ап (паразитний тиристор) ────────────────────────────
def fig_latchup():
    W, H = 720, 400
    s = header(W, H)
    s += text(W / 2, 30, "Латч-ап: паразитний тиристор замикає Vcc на GND", 16, INK, "middle", "bold")

    # рейки
    vy, gy = 72, 340
    s += line(70, vy, 470, vy, RED, 3)
    s += text(64, vy - 8, "Vcc", 13, RED, "start", "bold")
    s += line(70, gy, 470, gy, BLUE, 3)
    s += text(64, gy + 20, "GND", 13, BLUE, "start", "bold")

    # два паразитні транзистори як петля (символічно — кружечки з B/C/E)
    # PNP зверху
    tx1, ty1 = 200, 150
    s += circle(tx1, ty1, 30, "#fdeef0", RED, 2.2)
    s += text(tx1, ty1 + 5, "PNP", 12, RED, "middle", "bold")
    # NPN знизу
    tx2, ty2 = 300, 250
    s += circle(tx2, ty2, 30, "#eef0fd", BLUE, 2.2)
    s += text(tx2, ty2 + 5, "NPN", 12, BLUE, "middle", "bold")

    # з'єднання у петлю
    s += line(tx1, ty1 - 30, tx1, vy, RED, 2.4)            # PNP емітер до Vcc
    s += line(tx2, ty2 + 30, tx2, gy, BLUE, 2.4)           # NPN емітер до GND
    s += arrow(tx1 + 28, ty1 + 12, tx2 - 22, ty2 - 16, INK, 2.2)   # колектор PNP -> база NPN
    s += arrow(tx2 - 28, ty2 - 12, tx1 + 22, ty1 + 16, INK, 2.2)   # колектор NPN -> база PNP
    s += text(192, 212, "петля +ЗЗ", 10, INK, "middle", "bold", "italic")

    # інжекція струму ззовні
    s += arrow(110, 150, tx1 - 32, 150, GREEN, 2.6)
    s += text(108, 134, "інжекція струму", 10.5, GREEN, "middle", "bold")
    s += text(108, 176, "(з входу / hot-plug)", 9, GREEN, "middle")

    # результат: коротке Vcc->GND
    s += poly([(400, vy), (400, 200), (400, gy)], RED, 5)
    s += arrow(400, vy + 6, 400, gy - 6, RED, 5)
    s += text(412, 210, "коротке", 12, RED, "start", "bold")
    s += text(412, 228, "Vcc → GND", 12, RED, "start", "bold")
    s += text(412, 246, "крізь кристал", 9.5, GREY, "start")

    # пояснення праворуч
    bx, by = 500, 90
    s += rect(bx, by, 200, 250, "#fff", "#c9d3dc", 1.4, 6)
    s += text(bx + 100, by + 22, "Що відбувається", 12, INK, "middle", "bold")
    lines = [
        "• струм відмикає один",
        "  паразитний транзистор",
        "• той відмикає другий",
        "• другий тримає перший",
        "  → петля замкнулась",
        "Тримається САМА,",
        "доки не знято живлення.",
        "Скидання не рятує —",
        "лише вимкнути живлення.",
        "Не обмежив струм —",
        "кристал вигоряє.",
    ]
    for i, ln in enumerate(lines):
        col = RED if ("вигоряє" in ln or "САМА" in ln) else INK
        s += text(bx + 12, by + 44 + i * 18, ln, 10.5, col, "start",
                  "bold" if col == RED else "normal")

    s += text(W / 2, H - 12, "Паразитний тиристор у підкладці спить, доки інжектований струм його не «клацне» в самопідтримний коротень.",
              10, GREY, "middle", style="italic")
    save("fig-r09-2c-2-latchup.svg", s)


# ── Рис. 2.9.2c.3 — звідки береться перенапруга на вході ─────────────────────
def fig_overvoltage():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 30, "Звідки береться перенапруга на вході", 16, INK, "middle", "bold")

    cards = [
        ("5 В на 3.3-вольтовий вхід", "сигнал «1» (5 В) вищий за рейку Vcc=3.3 В",
         "сигнал ↗ діод до Vcc відкрито", LRED),
        ("Сигнал раніше за живлення", "Vcc ще 0, а на вході вже повні вольти",
         "вхід «вище» нульової рейки", LYEL),
        ("Індуктивний викид / наводка", "котушка чи довгий дріт кидає голку",
         "коротка піка поза рейками", LBLUE),
        ("Гаряче підключення", "ємнісне перекидання в мить стику",
         "стрибок штовхає вхід за рейку", LGRN),
    ]
    bw, bh = 300, 110
    xs = [50, 370]
    ys = [56, 186]
    for i, (t1, t2, t3, col) in enumerate(cards):
        x = xs[i % 2]
        y = ys[i // 2]
        s += rect(x, y, bw, bh, col, "#9bb0c2", 1.4, 8)
        s += text(x + 14, y + 26, f"{i + 1}. {t1}", 12.5, INK, "start", "bold")
        s += text(x + 14, y + 50, t2, 10.5, INK, "start")
        s += line(x + 14, y + 62, x + bw - 14, y + 62, FAINT, 1.2)
        s += text(x + 14, y + 84, "→ " + t3, 10.5, RED, "start", "bold")

    s += text(W / 2, H - 14, "Усі чотири шляхи кінчаються однаково: захисний діод входу відмикається — і починається струм крізь ніжку.",
              10.5, GREY, "middle", style="italic")
    save("fig-r09-2c-3-overvoltage.svg", s)


# ── Рис. 2.9.2c.4 — гаряче підключення ───────────────────────────────────────
def fig_hotplug():
    W, H = 720, 380
    s = header(W, H)
    s += text(W / 2, 30, "Гаряче підключення: що коїться в мить дотику", 16, INK, "middle", "bold")

    # дві половини роз'єму
    sys_x = 90
    mod_x = 470
    s += rect(sys_x, 90, 150, 210, "#eef2f7", "#7f93a8", 2, 8)
    s += text(sys_x + 75, 112, "система", 12, INK, "middle", "bold")
    s += text(sys_x + 75, 128, "(під напругою)", 9, GREY, "middle")
    s += rect(mod_x, 90, 160, 210, "#eef2f7", "#7f93a8", 2, 8)
    s += text(mod_x + 80, 112, "новий модуль", 12, INK, "middle", "bold")
    s += text(mod_x + 80, 128, "(щойно встромили)", 9, GREY, "middle")

    # контакти різної довжини: GND/VCC довші (зходяться першими), сигнали коротші
    rows = [
        ("GND",  150, BLUE,  "довгий — першим"),
        ("VCC",  185, RED,   "довгий — першим"),
        ("SIG",  235, INK,   "короткий — останнім"),
        ("SIG2", 270, INK,   "короткий — останнім"),
    ]
    for name, yy, col, note in rows:
        long_pin = name in ("GND", "VCC")
        x_sys_end = 240
        x_mod_end = mod_x
        gap_l = 305 if long_pin else 330      # довгі сходяться раніше (менший проміжок)
        gap_r = 405 if long_pin else 380
        s += line(x_sys_end, yy, gap_l, yy, col, 3)
        s += line(gap_r, yy, x_mod_end, yy, col, 3)
        # позначка контакту
        s += text(x_sys_end - 4, yy + 4, name, 10.5, col, "end", "bold")
        s += text((gap_l + gap_r) / 2, yy - 8, note, 8.5, GREY, "middle")
        if long_pin:
            s += text((gap_l + gap_r) / 2, yy + 16, "✓ контакт є", 8.5, GREEN, "middle", "bold")
        else:
            s += text((gap_l + gap_r) / 2, yy + 16, "ще нема", 8.5, RED, "middle", "bold")

    # три ефекти внизу
    eff = [
        ("порядок дотику", "сигнал раніше за землю → вхід поза рейками"),
        ("кидок струму", "розряджені ємності модуля = коротке на мить"),
        ("викид напруги", "індуктивність кабелю + кидок струму"),
    ]
    ey = 320
    for i, (a, b) in enumerate(eff):
        x = 40 + i * 225
        s += text(x, ey, f"• {a}:", 11, RED, "start", "bold")
        s += text(x, ey + 16, b, 9, INK, "start")

    s += text(W / 2, H - 8, "Довші земля й живлення сходяться першими; усе одно кидок, викид і порядок дотику штовхають вхід за рейки.",
              9.5, GREY, "middle", style="italic")
    save("fig-r09-2c-4-hotplug.svg", s)


if __name__ == "__main__":
    fig_clamp()
    fig_latchup()
    fig_overvoltage()
    fig_hotplug()
    print("done.")
