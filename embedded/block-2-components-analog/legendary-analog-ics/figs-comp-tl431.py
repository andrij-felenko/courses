# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 🔌 «TL431-клас: програмований стабілітрон»
(тема 2.12.5, Модуль 2). Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; стрілки
через marker; шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділів
цього модуля (єдиний вигляд). Імена SVG — унікальні (префікс fig-12-5c-…),
щоб НЕ зачіпати головний figs.py розділу.
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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def path(d, color=INK, w=2, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da} '
            f'stroke-linejoin="round" stroke-linecap="round"/>\n')


def res_h(x, y, w, h, color=INK):
    """Резистор-зигзаг у ГОРИЗОНТАЛЬНІЙ орієнтації (вивід зліва→направо)."""
    n = 6
    step = w / n
    pts = [(x, y)]
    amp = h / 2
    for i in range(n):
        yy = y + (amp if i % 2 == 0 else -amp)
        pts.append((x + step * (i + 0.5), yy))
    pts.append((x + w, y))
    return polyline(pts, color=color, w=2)


def res_v(x, y, w, h, color=INK):
    """Резистор-зигзаг у ВЕРТИКАЛЬНІЙ орієнтації (вивід зверху→вниз)."""
    n = 6
    step = h / n
    pts = [(x, y)]
    amp = w / 2
    for i in range(n):
        xx = x + (amp if i % 2 == 0 else -amp)
        pts.append((xx, y + step * (i + 0.5)))
    pts.append((x, y + h))
    return polyline(pts, color=color, w=2)


def cap_v(x, y, gap=8, plate=18, color=INK):
    """Конденсатор: дві горизонтальні пластини на вертикальному проводі (центр y)."""
    s = line(x - plate, y - gap / 2, x + plate, y - gap / 2, color=color, w=3)
    s += line(x - plate, y + gap / 2, x + plate, y + gap / 2, color=color, w=3)
    return s


def opamp(cx, cy, w=70, h=64, color=INK, fill="none", label="A"):
    """Трикутник ОП вістрям вправо; повертає (svg, x_in_top, y_in_top, x_in_bot, y_in_bot, x_out, y_out)."""
    x0 = cx - w / 2
    xt = cx + w / 2
    yt = cy - h / 2
    yb = cy + h / 2
    s = path(f"M {x0:.1f},{yt:.1f} L {x0:.1f},{yb:.1f} L {xt:.1f},{cy:.1f} Z",
             color=color, w=2, fill=fill)
    y_in_a = cy - h / 4
    y_in_b = cy + h / 4
    if label:
        s += text(cx - w / 6, cy + 5, label, size=15, anchor="middle", weight="bold", color=color)
    return s, x0, y_in_a, x0, y_in_b, xt, cy


def diode_down(x, ytop, ybot, color=INK, fill=LSUN):
    """Символ діода (трикутник + риска), струм униз (анод зверху). Центр по вертикалі."""
    mid = (ytop + ybot) / 2
    s = line(x, ytop, x, mid - 9, color=color, w=2)
    s += path(f"M {x-9:.1f},{mid-9:.1f} L {x+9:.1f},{mid-9:.1f} L {x:.1f},{mid+9:.1f} Z",
              color=color, w=2, fill=fill)
    s += line(x - 10, mid + 9, x + 10, mid + 9, color=color, w=2.4)
    s += line(x, mid + 9, x, ybot, color=color, w=2)
    return s


# ---------------------------------------------------------------------------
# Фігура 1: що всередині TL431 — еталон + підсилювач похибки + відкритий ключ,
# і три ноги REF / ANODE / CATHODE; поруч — символ «програмованого стабілітрона».
# ---------------------------------------------------------------------------
def fig_inside():
    W, H = 780, 430
    s = header(W, H)
    s += text(W / 2, 26, "Усередині TL431: підсилювач похибки порівнює REF із 2.5 В",
              size=17, anchor="middle", weight="bold")

    # рамка чипа
    bx, by, bw, bh = 70, 60, 360, 320
    s += rect(bx, by, bw, bh, fill="#fcfcfc", stroke=GREY, sw=1.5, rx=8)
    s += text(bx + 12, by + 22, "TL431 (всередині)", size=13, color=GREY, weight="bold")

    # ---- внутрішнє опорне джерело 2.5 В (bandgap) ----
    refx, refy = 150, 250
    s += rect(refx - 44, refy - 26, 88, 52, fill=LGRN, stroke=GREEN, sw=2, rx=6)
    s += text(refx, refy - 4, "опора", size=13, anchor="middle", color=GREEN, weight="bold")
    s += text(refx, refy + 15, "2.5 В", size=14, anchor="middle", color=GREEN, weight="bold")

    # ---- підсилювач похибки (ОП) ----
    amp_cx, amp_cy = 285, 175
    sa, xia, yia, xib, yib, xo, yo = opamp(amp_cx, amp_cy, w=78, h=72, color=INK, fill="#fff", label="")
    s += sa
    # неінвертуючий вхід (+) ← REF-нога; інвертуючий (−) ← опора 2.5 В
    s += text(xia - 14, yia + 5, "+", size=18, color=RED, anchor="middle", weight="bold")
    s += text(xib - 14, yib + 5, "−", size=18, color=BLUE, anchor="middle", weight="bold")
    s += text(amp_cx - 4, amp_cy - 26, "підсилювач", size=11, anchor="middle", color=INK)
    s += text(amp_cx - 4, amp_cy + 34, "похибки", size=11, anchor="middle", color=INK)

    # REF-нога → вхід (+)
    refnode_x = 56
    yref = yia
    s += line(bx, yref, xia, yref, color=INK, w=2)
    s += circle(bx, yref, 3.2, fill=INK, stroke=INK, w=1)
    s += text(bx - 10, yref + 5, "REF", size=13, anchor="end", weight="bold")

    # опора 2.5 В → вхід (−)
    s += line(refx, refy - 26, refx, yib, color=GREEN, w=2)
    s += line(refx, yib, xib, yib, color=GREEN, w=2)
    s += line(refx, refy + 26, refx, 350, color=GREEN, w=2)   # опора стоїть на аноді

    # ---- вихідний транзистор (відкритий колектор) ----
    # малюємо як NPN-ключ: база ← вихід ОП, колектор → CATHODE, емітер → ANODE
    tx, ty = 372, 175
    # вертикальна лінія транзистора (колектор–емітер)
    s += line(tx, ty - 48, tx, ty + 70, color=INK, w=2)
    # база
    s += line(xo, yo, tx - 22, ty, color=INK, w=2)
    s += line(tx - 22, ty - 16, tx - 22, ty + 16, color=INK, w=3)   # вертикальна риска бази
    s += line(tx - 22, ty, tx, ty - 12, color=INK, w=2)
    # колектор угору
    s += line(tx, ty - 12, tx, ty - 48, color=INK, w=2)
    # емітер униз зі стрілкою
    s += arrow(tx, ty + 12, tx + 16, ty + 40, color=INK, w=2)
    s += line(tx, ty, tx, ty + 12, color=INK, w=2)
    s += text(tx + 16, ty - 30, "вих.", size=11, anchor="start", color=INK)
    s += text(tx + 16, ty - 16, "ключ", size=11, anchor="start", color=INK)

    # CATHODE-нога (колектор)
    ycat = 90
    s += line(tx, ty - 48, tx, ycat, color=INK, w=2)
    s += line(tx, ycat, bx + bw, ycat, color=INK, w=2)
    s += circle(bx + bw, ycat, 3.2, fill=INK, stroke=INK, w=1)
    s += text(bx + bw + 10, ycat + 5, "CATHODE (K)", size=13, anchor="start", weight="bold")

    # ANODE-нога (емітер + низ опори) — спільна земля
    yan = 350
    s += line(tx + 16, ty + 40, tx + 16, yan, color=INK, w=2)
    s += line(refx, yan, tx + 16, yan, color=INK, w=2)
    s += line(bx + bw, yan, tx + 16, yan, color=INK, w=2)
    s += circle(bx + bw, yan, 3.2, fill=INK, stroke=INK, w=1)
    s += text(bx + bw + 10, yan + 5, "ANODE (A)", size=13, anchor="start", weight="bold")

    # підпис «коли REF > 2.5 В — ключ тягне K до A»
    s += text(amp_cx + 6, by + bh - 8,
              "REF > 2.5 В → ключ відкривається → K сідає до A",
              size=11.5, anchor="middle", color=RED, style="italic")

    # ---- праворуч: символ «програмований стабілітрон» ----
    symx = 640
    s += text(symx, by + 24, "Як це бачить схема:", size=13, anchor="middle", weight="bold")
    s += text(symx, by + 44, "регульований стабілітрон", size=12, anchor="middle", color=GREY)
    # K зверху, A знизу, REF — стрілка-вхід збоку
    syt, syb = 120, 300
    s += line(symx, syt, symx, 175, color=INK, w=2)
    # символ зенера: трикутник вістрям угору (катод зверху для стабілітрона) + загнута риска
    midy = 200
    s += path(f"M {symx-13:.1f},{midy+13:.1f} L {symx+13:.1f},{midy+13:.1f} L {symx:.1f},{midy-13:.1f} Z",
              color=INK, w=2, fill=LSUN)
    # «зенерівська» риска з загнутими кінцями
    s += polyline([(symx - 15, midy - 13 + 6), (symx - 13, midy - 13),
                   (symx + 13, midy - 13), (symx + 15, midy - 13 - 6)], color=INK, w=2.4)
    s += line(symx, midy + 13, symx, syb, color=INK, w=2)
    s += text(symx + 4, syt - 6, "K", size=14, anchor="start", weight="bold")
    s += text(symx + 4, syb + 16, "A", size=14, anchor="start", weight="bold")
    # REF-вхід збоку зі стрілкою досередини
    s += arrow(symx - 70, midy, symx - 16, midy, color=GREEN, w=2)
    s += text(symx - 74, midy + 5, "REF", size=13, anchor="end", weight="bold", color=GREEN)
    s += text(symx, syb + 40, "поріг = 2.5 В", size=12, anchor="middle", color=GREEN)
    s += text(symx, syb + 58, "(не фіксований!)", size=11, anchor="middle", color=GREY, style="italic")

    return W, H, s


# ---------------------------------------------------------------------------
# Фігура 2: типове застосування — дільник задає поріг (Vka = 2.5·(1+R1/R2)),
# і роль у зворотному зв'язку ізольованого зарядного крізь оптопару.
# ---------------------------------------------------------------------------
def fig_application():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 24, "TL431 у зворотному зв'язку зарядного: два резистори задають напругу, оптопара несе сигнал крізь ізоляцію",
              size=14, anchor="middle", weight="bold")

    # ====== межа ізоляції ======
    xiso = 300
    s += line(xiso, 50, xiso, 410, color=GREY, w=1.5, dash="7 6")
    s += text(xiso, 404, "бар'єр ізоляції", size=11.5, color=GREY, anchor="middle", style="italic")
    s += text(xiso - 14, 70, "первинна сторона", size=11.5, color=GREY, anchor="end")
    s += text(xiso + 14, 70, "вторинна сторона (вихід)", size=11.5, color=GREY, anchor="start")

    # ====== вторинна сторона: рейки ======
    Vy = 96
    Gy = 372
    xVL = 330
    xVR = 800
    s += line(xVL, Vy, xVR, Vy, color=RED, w=2.6)
    s += line(xVL, Gy, xVR, Gy, color=BLUE, w=2.6)
    s += text(xVR - 4, Vy - 9, "Vout = 5.0 В", size=13, color=RED, anchor="end", weight="bold")
    s += text(xVR - 4, Gy + 19, "земля вторинки", size=12, color=BLUE, anchor="end")

    # ---- дільник R1/R2 у вузол FB ----
    xd = 720
    yfb = 250
    s += line(xd, Vy, xd, 128, color=INK, w=2)
    s += res_v(xd, 128, 16, 58, color=INK)
    s += line(xd, 186, xd, yfb, color=INK, w=2)
    s += text(xd + 13, 158, "R1", size=14, weight="bold")
    s += circle(xd, yfb, 3.4, fill=INK, stroke=INK, w=1)
    s += text(xd + 12, yfb - 7, "FB", size=11.5, color=GREY, anchor="start")
    s += res_v(xd, yfb + 6, 16, 58, color=INK)
    s += line(xd, yfb + 64, xd, Gy, color=INK, w=2)
    s += text(xd + 13, yfb + 40, "R2", size=14, weight="bold")

    # ---- TL431 (символ регульованого стабілітрона) ----
    tlx = 560
    yKtop = 150
    yAbot = 318
    midy = 236
    s += text(tlx, 118, "TL431", size=14, anchor="middle", weight="bold")
    s += path(f"M {tlx-14:.1f},{midy+14:.1f} L {tlx+14:.1f},{midy+14:.1f} L {tlx:.1f},{midy-14:.1f} Z",
              color=INK, w=2, fill=LSUN)
    s += polyline([(tlx - 16, midy - 14 + 7), (tlx - 14, midy - 14),
                   (tlx + 14, midy - 14), (tlx + 16, midy - 14 - 7)], color=INK, w=2.4)
    s += text(tlx + 7, midy + 5, "K", size=12, anchor="start", weight="bold")
    s += text(tlx - 7, midy + 5, "A", size=12, anchor="end", weight="bold")
    # A (низ) → земля
    s += line(tlx, midy + 14, tlx, Gy, color=INK, w=2)
    # REF ← FB
    s += arrow(xd, yfb, tlx + 18, midy, color=GREEN, w=2)
    s += text((xd + tlx) / 2 + 4, midy - 9, "REF", size=12, anchor="middle", color=GREEN, weight="bold")
    # K (верх) → катод світлодіода оптопари
    s += line(tlx, midy - 14, tlx, yKtop, color=INK, w=2)

    # ---- оптопара (світлодіод на вторинці) ----
    optx = 430
    # анод світлодіода ← Vout через обмежувальний резистор R; катод → K TL431
    s += line(optx, Vy, optx, 138, color=INK, w=2)
    s += res_v(optx, 138, 14, 40, color=COPP)
    s += text(optx + 12, 162, "R", size=12, weight="bold", color=COPP)
    # світлодіод (анод зверху → катод донизу), струм униз
    led_top = 186
    led_bot = yKtop
    s += diode_down(optx, led_top, led_bot, color=RED, fill=LRED)
    # стрілочки «світло»
    s += line(optx + 12, 214, optx + 24, 206, color=SUN, w=1.6)
    s += line(optx + 12, 224, optx + 24, 216, color=SUN, w=1.6)
    # катод світлодіода → K
    s += line(optx, led_bot, tlx, yKtop, color=INK, w=2)
    s += circle(tlx, yKtop, 3.0, fill=INK, stroke=INK, w=1)
    s += text(optx - 16, 132, "оптопара", size=11, color=GREY, anchor="end")

    # ====== первинна сторона: фототранзистор → контролер ШІМ ======
    # фототранзистор приймає світло, керує входом FB контролера
    ptx = 180
    # символ фототранзистора (коло з транзистором) — спрощено
    s += circle(ptx, 220, 26, fill="#fff", stroke=INK, w=2)
    s += line(ptx - 8, 200, ptx - 8, 240, color=INK, w=2)        # база-лінія
    s += line(ptx - 8, 210, ptx + 14, 198, color=INK, w=2)       # колектор
    s += arrow(ptx - 8, 230, ptx + 14, 242, color=INK, w=2)      # емітер
    # стрілки світла на фототранзистор
    s += arrow(ptx + 40, 205, ptx + 18, 213, color=SUN, w=1.8)
    s += arrow(ptx + 40, 215, ptx + 18, 223, color=SUN, w=1.8)
    s += text(ptx, 262, "фототранзистор", size=11, anchor="middle", color=GREY)

    # контролер ШІМ
    s += rect(70, 120, 70, 80, fill=LBLUE, stroke=BLUE, sw=2, rx=6)
    s += text(105, 150, "ШІМ-", size=12, anchor="middle", color=BLUE, weight="bold")
    s += text(105, 166, "контро-", size=12, anchor="middle", color=BLUE, weight="bold")
    s += text(105, 182, "лер", size=12, anchor="middle", color=BLUE, weight="bold")
    # колектор фототранзистора → вхід FB контролера
    s += line(ptx + 14, 198, ptx + 14, 160, color=INK, w=2)
    s += line(ptx + 14, 160, 140, 160, color=INK, w=2)
    s += text(150, 154, "FB", size=11, color=BLUE, anchor="start")
    # емітер фототранзистора → первинна земля
    s += line(ptx + 14, 242, ptx + 14, 300, color=INK, w=2)
    s += line(70, 300, ptx + 14, 300, color=INK, w=2)
    s += line(70, 300, 70, 200, color=INK, w=2)
    s += text(66, 320, "первинна земля", size=11, color=GREY, anchor="start")

    # ====== формула й логіка регулювання ======
    s += text(335, 408, "Поріг:  Vout = 2.5 · (1 + R1/R2)   —   міняєш R1/R2, міняєш напругу заряду",
              size=12.5, anchor="start", color=GREEN, weight="bold")

    # пояснювальна петля керування — у вільній смузі під заголовком
    s += text(560, 52,
              "Vout ↑ → FB > 2.5 В → TL431 тягне струм → світлодіод яскравіше → ШІМ зменшує → Vout вниз",
              size=10.5, anchor="middle", color=RED, style="italic")

    return W, H, s


def save(name, tup):
    W, H, body = tup
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name, f"({W}x{H})")


if __name__ == "__main__":
    save("fig-12-5c-1-inside.svg", fig_inside())
    save("fig-12-5c-2-feedback.svg", fig_application())
    print("done")
