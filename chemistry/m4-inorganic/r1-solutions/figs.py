# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4.1 — «Вода і розчини» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; заряд «+» червоний, «−» синій;
атоми-кульки — O червона, H біла з сірим контуром, C темно-сіра, N синя,
Cl зелена, метали сіро-фіолетові; електрони — маленькі сині крапки;
стрілки через marker. Усі підписи українською.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED    = "#c0271e"   # додатний (+)
BLUE   = "#1f47b5"   # від'ємний (−)
GREEN  = "#1f8a3b"   # «так / розчинилося»
INK    = "#1b1b1b"   # основний текст/лінії
GREY   = "#8a8a8a"   # допоміжне
FAINT  = "#e9e9e9"   # бліде тло
O_FILL = "#d9483c"   # Оксиген
O_LINE = "#9f2c22"
H_FILL = "#ffffff"   # Гідроген
H_LINE = "#9a9a9a"
C_FILL = "#454545"   # Карбон
N_FILL = "#2c52b0"   # Нітроген
CL_FILL = "#3f9e54"  # Хлор
MET_FILL = "#8a7fae"  # метали
WATER  = "#cfe6f5"   # вода в посудині
OIL    = "#e7b23a"   # олія / бензин (бурштин)
OILpale = "#f1d79a"  # розчин олії в бензині
SUGAR  = "#caa24a"   # крупинки цукру
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    m = "aGreen" if color == GREEN else "aInk"
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def curve(x1, y1, x2, y2, cx, cy, color=INK, w=2):
    m = "aGreen" if color == GREEN else "aInk"
    return (f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def poly(points, color=INK, w=2, fill="none"):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>\n')


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


def plus(cx, cy, size=6, color=RED, w=2.4):
    return (line(cx - size, cy, cx + size, cy, color, w)
            + line(cx, cy - size, cx, cy + size, color, w))


def minus(cx, cy, size=6, color=BLUE, w=2.4):
    return line(cx - size, cy, cx + size, cy, color, w)


def ball(cx, cy, r, fill, stroke, label=None, lsize=12, lcolor="#ffffff"):
    s = circle(cx, cy, r, fill, stroke, 1.8)
    if label:
        s += text(cx, cy + lsize * 0.36, label, lsize, lcolor, "middle", "bold")
    return s


def edot(cx, cy, r=2.6):
    """електрон — маленька синя крапка."""
    return circle(cx, cy, r, BLUE, BLUE, 0)


def water_molecule(cx, cy, ang_deg, ro=12, rh=7, bond=20, show_charge=False, label_o=False):
    """Молекула води. ang_deg — куди дивиться плюсовий (водневий) полюс."""
    a = math.radians(ang_deg)
    half = math.radians(53)  # ~106° між зв'язками O–H
    h1 = (cx + bond * math.cos(a - half), cy + bond * math.sin(a - half))
    h2 = (cx + bond * math.cos(a + half), cy + bond * math.sin(a + half))
    s = line(cx, cy, h1[0], h1[1], H_LINE, 3)
    s += line(cx, cy, h2[0], h2[1], H_LINE, 3)
    s += ball(cx, cy, ro, O_FILL, O_LINE, "O" if label_o else None, lsize=ro)
    s += ball(h1[0], h1[1], rh, H_FILL, H_LINE)
    s += ball(h2[0], h2[1], rh, H_FILL, H_LINE)
    if show_charge:
        mx, my = cx - (ro + 9) * math.cos(a), cy - (ro + 9) * math.sin(a)
        px = (h1[0] + h2[0]) / 2 + (rh + 7) * math.cos(a)
        py = (h1[1] + h2[1]) / 2 + (rh + 7) * math.sin(a)
        s += minus(mx, my, 6, BLUE)
        s += plus(px, py, 6, RED)
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 4.1.1-1 — гідратація: обліпити й розтягти ───────────────────────────
def fig_hydration():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Як вода розчиняє: обліпити й розтягти", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "молекули-магнітики повертаються потрібним полюсом і відтягують частинки одну за одною",
              12.5, GREY, "middle", style="italic")

    # ── легенда: одна молекула води як магнітик ──
    lx, ly = 116, 270
    s += rect(28, 188, 176, 182, "none", FAINT, 2, 14)
    s += water_molecule(lx, ly, ang_deg=90, ro=18, rh=11, bond=34, show_charge=True, label_o=True)
    s += text(116, 214, "молекула води", 13.5, INK, "middle", "bold")
    s += text(116, 344, "− біля Оксигену,", 12.5, BLUE, "middle")
    s += text(116, 360, "+ біля Гідрогенів", 12.5, RED, "middle")

    # ── центр: крупинка цукру, обліплена водою ──
    ccx, ccy = 470, 268
    # крупинка — щільна купка сірих частинок
    s += text(ccx, 150, "крупинка цукру", 13.5, INK, "middle", "bold")
    units = [(0, 0), (-26, -8), (26, -8), (-14, 20), (14, 20), (0, -28), (0, 30)]
    for dx, dy in units:
        s += ball(ccx + dx, ccy + dy, 15, SUGAR, "#a07f33")
    # шість молекул води навколо, повернуті до купки (полюс — досередини, по черзі)
    R = 86
    for i in range(6):
        th = math.radians(-90 + i * 60)
        wx, wy = ccx + R * math.cos(th), ccy + R * math.sin(th)
        inward = math.degrees(math.atan2(ccy - wy, ccx - wx))
        # по черзі: то «+» полюсом досередини, то «−» (O) досередини
        ang = inward if i % 2 == 0 else inward + 180
        s += water_molecule(wx, wy, ang_deg=ang, ro=11, rh=6.5, bond=17)

    # ── стрілка: одну частинку відтягнуто в розчин ──
    s += curve(560, 232, 666, 244, 620, 196, INK, 2.4)
    s += text(632, 196, "відтягує", 12.5, INK, "middle", style="italic")

    # ── справа: розчинена частинка, обліплена водою ──
    dcx, dcy = 742, 286
    s += ball(dcx, dcy, 15, SUGAR, "#a07f33")
    for i in range(4):
        th = math.radians(45 + i * 90)
        wx, wy = dcx + 44 * math.cos(th), dcy + 44 * math.sin(th)
        inward = math.degrees(math.atan2(dcy - wy, dcx - wx))
        s += water_molecule(wx, wy, ang_deg=inward + (0 if i % 2 == 0 else 180), ro=10, rh=6, bond=15)
    s += text(742, 360, "розчинена частинка:", 12.5, INK, "middle", "bold")
    s += text(742, 376, "відтягнута й обліплена", 12.5, INK, "middle")

    save("fig-4-1-1-1-hydration.svg", s)


# ── Рис. 4.1.1-2 — подібне розчиняється в подібному ──────────────────────────
def _beaker(x, y, w, h, rb=16):
    """Контур склянки: x,y — лівий верхній кут тіла, заокруглене дно."""
    return (f'<path d="M{x:.1f},{y:.1f} L{x:.1f},{y + h - rb:.1f} '
            f'Q{x:.1f},{y + h:.1f} {x + rb:.1f},{y + h:.1f} '
            f'L{x + w - rb:.1f},{y + h:.1f} Q{x + w:.1f},{y + h:.1f} {x + w:.1f},{y + h - rb:.1f} '
            f'L{x + w:.1f},{y:.1f}" fill="none" stroke="{INK}" stroke-width="2.4"/>\n')


def _liquid(x, y, w, h, fill, rb=16):
    return (f'<path d="M{x:.1f},{y:.1f} L{x:.1f},{y + h - rb:.1f} '
            f'Q{x:.1f},{y + h:.1f} {x + rb:.1f},{y + h:.1f} '
            f'L{x + w - rb:.1f},{y + h:.1f} Q{x + w:.1f},{y + h:.1f} {x + w:.1f},{y + h - rb:.1f} '
            f'L{x + w:.1f},{y:.1f} Z" fill="{fill}" stroke="none"/>\n')


def _magnet_dot(cx, cy):
    """крихітна водяна пара-магнітик: синя + червона крапка."""
    return circle(cx - 4, cy, 4, BLUE, BLUE, 0) + circle(cx + 4, cy, 4, RED, RED, 0)


def fig_like_like():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 36, "Подібне розчиняється в подібному", 21, INK, "middle", "bold")

    bw, bh, by = 200, 220, 96
    xs = [60, 330, 600]
    titles = ["вода + цукор", "вода + олія", "бензин + олія"]
    tags = ["розчинилося", "не змішується", "розчинилося"]
    tagcol = [GREEN, INK, GREEN]

    for k, x in enumerate(xs):
        s += text(x + bw / 2, by - 14, titles[k], 15, INK, "middle", "bold")
        if k == 0:
            # однорідний розчин: вода + рівномірні крупинки цукру
            s += _liquid(x, by, bw, bh, WATER)
            pts = [(40, 40), (95, 70), (150, 50), (60, 120), (120, 150),
                   (165, 110), (40, 175), (110, 95), (160, 175)]
            for px, py in pts:
                s += circle(x + px, by + py, 5, SUGAR, "#a07f33", 1)
            for px, py in [(70, 60), (130, 110), (60, 150), (150, 150)]:
                s += _magnet_dot(x + px, by + py)
        elif k == 1:
            # два шари: вода знизу, олія зверху краплями
            s += _liquid(x, by + 78, bw, bh - 78, WATER)
            s += _liquid(x, by, bw, 78, OIL)
            s += line(x, by + 78, x + bw, by + 78, "#b98e22", 2, dash="6 4")
            s += text(x + bw / 2, by + 40, "олія", 14, "#7a5a12", "middle", "bold")
            # у воді — магнітики, що тримаються одне одного
            for px, py in [(50, 130), (110, 120), (150, 165), (70, 180), (120, 175)]:
                s += _magnet_dot(x + px, by + py)
            # в олії — гладенькі «байдужі» овали
            for px, py in [(55, 35), (110, 50), (150, 32)]:
                s += f'<ellipse cx="{x + px:.1f}" cy="{by + py:.1f}" rx="13" ry="8" fill="{OILpale}" stroke="#b98e22" stroke-width="1.5"/>\n'
        else:
            # однорідна суміш: олія розійшлася в бензині
            s += _liquid(x, by, bw, bh, OILpale)
            for px, py in [(45, 55), (100, 40), (155, 65), (60, 110), (120, 100),
                           (165, 130), (50, 165), (110, 160), (150, 180)]:
                s += f'<ellipse cx="{x + px:.1f}" cy="{by + py:.1f}" rx="12" ry="7.5" fill="{OIL}" stroke="#b98e22" stroke-width="1.5"/>\n'
        s += _beaker(x, by, bw, bh)
        s += text(x + bw / 2, by + bh + 26, tags[k], 14.5, tagcol[k], "middle", "bold")

    s += text(W / 2, H - 14,
              "вода-магнітик бере магнітики (цукор, сіль); олія й бензин — обоє «гладенькі», тож радо змішуються",
              12.5, GREY, "middle", style="italic")
    save("fig-4-1-1-2-like-like.svg", s)


# ── Рис. 4.1.2-1 — насичення як рух у два боки ───────────────────────────────
def fig_saturation():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому розчин «наїдається»: рух у два боки", 21, INK, "middle", "bold")
    s += text(W / 2, 56,
              "частинки не лише виходять у воду — вони й повертаються на тверде; межа — коли потоки зрівнялись",
              12.5, GREY, "middle", style="italic")
    # легенда стрілок
    s += arrow(300, 74, 300, 62, GREEN, 3)
    s += text(308, 74, "виходить у воду", 12, GREEN, "start")
    s += arrow(470, 62, 470, 74, INK, 3)
    s += text(478, 74, "вертається на тверде", 12, INK, "start")

    bw, bh, by = 210, 212, 96
    xs = [55, 335, 615]
    titles = ["ненасичений", "майже насичений", "насичений"]
    tags = ["крупинка тане", "майже повний", "виходить = вертається"]
    tagcol = [INK, INK, GREEN]
    # (ширина купки, к-сть розчинених крапок, довжина «виходить», «вертається»)
    data = [(60, 3, 80, 26), (46, 9, 60, 46), (40, 15, 52, 52)]
    dotsets = [
        [(70, 150), (130, 120), (150, 175)],
        [(45, 130), (95, 100), (150, 120), (60, 160), (120, 150), (165, 95),
         (40, 95), (110, 75), (160, 165)],
        [(40, 120), (90, 95), (150, 110), (60, 150), (120, 135), (165, 90),
         (45, 80), (105, 70), (160, 150), (75, 175), (130, 175), (35, 150),
         (155, 175), (100, 105), (185, 125)],
    ]

    for k, x in enumerate(xs):
        cx = x + bw / 2
        s += text(cx, by - 12, titles[k], 15, INK, "middle", "bold")
        s += _liquid(x, by, bw, bh, WATER)
        # крупинка на дні
        hw, ndots, lup, ldown = data[k]
        bot = by + bh - 3
        s += poly([(cx - hw, bot), (cx - hw * 0.5, bot - 26), (cx + hw * 0.5, bot - 26),
                   (cx + hw, bot)], "#7d7d7d", 1.5, fill="#b3b3b3")
        # розчинені крапки
        for px, py in dotsets[k]:
            s += circle(x + px, by + py, 4.5, SUGAR, "#a07f33", 1)
        # стрілки рівноваги біля купки
        htop = bot - 26
        s += arrow(cx - 24, htop - 6, cx - 24, htop - 6 - lup, GREEN, 3.2)
        s += arrow(cx + 24, htop - 6 - ldown, cx + 24, htop - 6, INK, 3.2)
        s += _beaker(x, by, bw, bh)
        s += text(cx, by + bh + 26, tags[k], 14, tagcol[k], "middle", "bold")
    save("fig-4-1-2-1-saturation.svg", s)


# ── Рис. 4.1.2-2 — розчинність росте з температурою; охолодження → кристал ────
def fig_solubility_temp():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Гарячіше — більше влазить; охолоне — зайве випадає", 20, INK, "middle", "bold")

    # ── графік ──
    ax, ay0, ay1 = 120, 340, 110   # x осі / низ / верх
    axr = 520
    s += arrow(ax, ay0, ax, ay1 - 6, INK, 2)           # вісь Y
    s += arrow(ax, ay0, axr + 6, ay0, INK, 2)          # вісь X
    s += text(ax - 8, ay1 - 12, "скільки солі влазить", 12.5, INK, "start", "bold")
    s += text(axr, ay0 + 22, "температура →", 12.5, INK, "end", "bold")
    s += text(ax + 6, ay0 + 22, "холодна", 11.5, GREY, "start")
    s += text(axr, ay0 + 38, "гаряча", 11.5, GREY, "end")

    def PX(t):
        return ax + t * (axr - ax)

    def PY(c):
        return ay0 - c * (ay0 - ay1)

    pts = [(0, 0.18), (0.2, 0.26), (0.4, 0.37), (0.6, 0.52), (0.8, 0.70), (1.0, 0.88)]
    s += poly([(PX(t), PY(c)) for t, c in pts], GREEN, 3)
    s += text(PX(0.62), PY(0.40), "розчинність", 12.5, GREEN, "start", "bold", "italic")

    # гаряча точка H
    hx, hy = PX(1.0), PY(0.88)
    s += circle(hx, hy, 5, RED, RED, 0)
    s += text(hx - 6, hy - 8, "гарячий насичений", 12, RED, "end", "bold")
    # охолодження: горизонталь вліво (амоунт сталий), тоді вниз до кривої
    cx_, ccap = PX(0.12), 0.22
    cold_x = PX(0.12)
    s += line(hx, hy, cold_x, hy, INK, 2, dash="6 5")
    s += text((hx + cold_x) / 2, hy - 8, "охолоджуємо →", 11.5, INK, "middle", style="italic")
    cap_y = PY(ccap)
    s += arrow(cold_x, hy + 4, cold_x, cap_y, INK, 2.6)
    s += circle(cold_x, cap_y, 5, BLUE, BLUE, 0)
    s += text(cold_x + 10, (hy + cap_y) / 2, "зайве", 12, BLUE, "start", "bold")
    s += text(cold_x + 10, (hy + cap_y) / 2 + 16, "випадає", 12, BLUE, "start", "bold")

    # ── вставка: склянка з кристалом на нитці ──
    gx, gy, gw, gh = 650, 150, 150, 188
    s += arrow(545, 250, gx - 12, 250, INK, 2.2)
    s += text((545 + gx) / 2, 240, "за кілька днів", 11.5, GREY, "middle", style="italic")
    s += _liquid(gx, gy, gw, gh, WATER)
    s += _beaker(gx, gy, gw, gh)
    # олівець на вінцях
    s += line(gx - 16, gy, gx + gw + 16, gy, "#b07a2a", 5)
    # нитка
    midx = gx + gw / 2
    s += line(midx, gy, midx, gy + 120, "#8a8a8a", 1.6)
    # кристал — кубик-ромб
    cyx, cyy, r = midx, gy + 140, 18
    s += poly([(cyx, cyy - r), (cyx + r, cyy), (cyx, cyy + r), (cyx - r, cyy)],
              "#9a9a9a", 1.6, fill="#e7eef3")
    s += line(cyx, cyy - r, cyx, cyy + r, "#9a9a9a", 1)
    s += line(cyx - r, cyy, cyx + r, cyy, "#9a9a9a", 1)
    s += text(midx, gy + gh + 22, "кристал на нитці", 12.5, INK, "middle", "bold")
    save("fig-4-1-2-2-solubility-temp.svg", s)


def hydrated_ion(cx, cy, fill, linec, positive, R=40):
    """Іон у «кожусі» з молекул води: + іон → O досередини; − іон → H досередини."""
    s = ""
    for i in range(4):
        th = math.radians(45 + i * 90)
        wx, wy = cx + R * math.cos(th), cy + R * math.sin(th)
        out = math.degrees(math.atan2(wy - cy, wx - cx))
        ang = out if positive else out + 180
        s += water_molecule(wx, wy, ang, ro=10, rh=6, bond=15)
    s += ball(cx, cy, 18, fill, linec)
    s += (plus(cx, cy, 7, RED) if positive else minus(cx, cy, 7, BLUE))
    return s


def lamp(cx, cy, r, lit):
    glow = "#f6cf3f" if lit else "#d4d4d4"
    ring = "#9a7d1c" if lit else GREY
    s = circle(cx, cy, r, glow, ring, 2)
    s += line(cx - r * 0.55, cy + 3, cx, cy - r * 0.35, ring, 1.6)
    s += line(cx, cy - r * 0.35, cx + r * 0.55, cy + 3, ring, 1.6)
    if lit:
        for a in range(8):
            th = math.radians(a * 45)
            s += line(cx + (r + 3) * math.cos(th), cy + (r + 3) * math.sin(th),
                      cx + (r + 9) * math.cos(th), cy + (r + 9) * math.sin(th), "#f0b400", 2)
    return s


def battery(cx, cy):
    s = line(cx + 7, cy - 15, cx + 7, cy + 15, INK, 2)   # довга тонка = +
    s += line(cx - 7, cy - 9, cx - 7, cy + 9, INK, 5)     # коротка товста = −
    s += text(cx + 7, cy - 19, "+", 13, RED, "middle", "bold")
    s += text(cx - 7, cy - 13, "−", 13, BLUE, "middle", "bold")
    return s


# ── Рис. 4.1.3-1 — дисоціація: вода розбирає ґратку на іони ───────────────────
def fig_dissociation():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Дисоціація: вода розбирає ґратку солі на іони", 21, INK, "middle", "bold")
    s += text(W / 2, 56,
              "у солі іони вже заряджені — вода лише витягує їх нарізно й обгортає собою",
              12.5, GREY, "middle", style="italic")

    # ── ґратка солі ──
    gx = [100, 148, 196]
    gy = [168, 216, 264]
    s += rect(64, 150, 168, 168, "none", FAINT, 2, 12)
    for i in range(3):
        for j in range(3):
            if i < 2:
                s += line(gx[i], gy[j], gx[i + 1], gy[j], "#d3d3d3", 1.5)
            if j < 2:
                s += line(gx[i], gy[j], gx[i], gy[j + 1], "#d3d3d3", 1.5)
    for i in range(3):
        for j in range(3):
            na = (i + j) % 2 == 0
            if na:
                s += ball(gx[i], gy[j], 17, MET_FILL, "#6f6394")
                s += plus(gx[i], gy[j], 6.5, RED)
            else:
                s += ball(gx[i], gy[j], 17, CL_FILL, "#2c7a40")
                s += minus(gx[i], gy[j], 6.5, BLUE)
    s += text(148, 336, "ґратка солі: Na⁺ і Cl⁻ по черзі", 12.5, INK, "middle", "bold")

    # ── стрілка-процес ──
    s += arrow(252, 216, 430, 216, INK, 3)
    s += text(341, 200, "вода розтягує ґратку", 12.5, INK, "middle", style="italic")
    s += text(341, 238, "дисоціація", 14, GREEN, "middle", "bold")

    # ── вільні гідратовані іони ──
    s += hydrated_ion(600, 188, MET_FILL, "#6f6394", positive=True)
    s += text(600, 116, "вільний Na⁺", 13, INK, "middle", "bold")
    s += text(600, 132, "(у кожусі з води)", 11.5, GREY, "middle")
    s += hydrated_ion(726, 338, CL_FILL, "#2c7a40", positive=False)
    s += text(726, 404, "вільний Cl⁻", 13, INK, "middle", "bold")
    s += text(726, 420, "(у кожусі з води)", 11.5, GREY, "middle")
    save("fig-4-1-3-1-dissociation.svg", s)


# ── Рис. 4.1.3-2 — провідність: чиста вода vs солона ─────────────────────────
def fig_conduction():
    W, H = 900, 460
    s = header(W, H)
    s += text(W / 2, 30, "Чому солона вода проводить струм, а чиста — майже ні", 20, INK, "middle", "bold")

    def panel(x0, lit, salt, title, caption, capcol):
        bx, by, bw, bh = x0 + 95, 168, 190, 168
        out = text(bx + bw / 2, 58, title, 16, INK, "middle", "bold")
        ex1, ex2 = bx + 45, bx + bw - 45
        # дроти + лампа + батарейка
        out += line(ex1, 118, ex1, 84, INK, 2.4)
        out += line(ex1, 84, ex2, 84, INK, 2.4)
        out += line(ex2, 84, ex2, 118, INK, 2.4)
        out += lamp(x0 + 150, 84, 15, lit)
        out += battery(x0 + 235, 84)
        # рідина і склянка
        out += _liquid(bx, by, bw, bh, WATER)
        # електроди занурені
        out += line(ex1, 118, ex1, by + 120, BLUE, 7)
        out += line(ex2, 118, ex2, by + 120, RED, 7)
        out += text(ex1, 112, "−", 14, BLUE, "middle", "bold")
        out += text(ex2, 112, "+", 14, RED, "middle", "bold")
        if salt:
            # Na⁺ (+) пливуть до − (лівого); Cl⁻ (−) — до + (правого)
            for px, py in [(bx + 128, 214), (bx + 138, 262)]:
                out += ball(px, py, 12, MET_FILL, "#6f6394")
                out += plus(px, py, 5, RED)
                out += arrow(px - 16, py, px - 40, py, INK, 2)
            for px, py in [(bx + 60, 232), (bx + 70, 280)]:
                out += ball(px, py, 12, CL_FILL, "#2c7a40")
                out += minus(px, py, 5, BLUE)
                out += arrow(px + 16, py, px + 40, py, INK, 2)
        else:
            for px, py in [(bx + 55, 215), (bx + 120, 235), (bx + 150, 285), (bx + 70, 290)]:
                out += water_molecule(px, py, 60 + px, ro=8, rh=5, bond=12)
        out += _beaker(bx, by, bw, bh)
        out += text(bx + bw / 2, by + bh + 28, caption, 13, capcol, "middle", "bold")
        return out

    s += panel(10, False, False, "чиста вода", "вільних зарядів нема — струму майже нема", INK)
    s += panel(470, True, True, "солона вода", "іони рухаються — струм тече", GREEN)
    save("fig-4-1-3-2-conduction.svg", s)


if __name__ == "__main__":
    fig_hydration()
    fig_like_like()
    fig_saturation()
    fig_solubility_temp()
    fig_dissociation()
    fig_conduction()
