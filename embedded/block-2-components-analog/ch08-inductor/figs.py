# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 8 — «Котушка та індуктивність» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
магнітний полюс N — червоний, S — синій; стрілки через marker; шрифт sans-serif.
Підписи нумеруються посекційно (Рис. C.S.N); для історії до розділу — секція 0
(Рис. 8.0.N). Спільні допоміжні функції скопійовано з розділу 7 (єдиний вигляд).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+), полюс N
BLUE  = "#1f47b5"   # від'ємний (−), полюс S
GREEN = "#1f8a3b"   # поле
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
COPP  = "#b5732e"   # мідь (дріт котушки)
IRON  = "#9aa0a6"   # залізо осердя
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── магнітні будівельники ────────────────────────────────────────────────────
def coil_h(cx, cy, length, turns=6, ry=28, col=COPP, lead=0):
    """Котушка з горизонтальною віссю: набір витків-еліпсів. Повертає (svg, (xL, xR))."""
    x0 = cx - length / 2
    dx = length / turns
    s = ""
    for i in range(turns + 1):
        x = x0 + i * dx
        s += f'<ellipse cx="{x:.1f}" cy="{cy:.1f}" rx="7" ry="{ry}" fill="none" stroke="{col}" stroke-width="2.2"/>\n'
    return s, (x0, x0 + length)


def bar_magnet(x, y, w, h, n_left=True):
    """Брусковий магніт (горизонтальний): N — червона половина, S — синя."""
    nx = x if n_left else x + w / 2
    sx = x + w / 2 if n_left else x
    s = rect(nx, y, w / 2, h, "#f4d9d6", RED, 1.6)
    s += rect(sx, y, w / 2, h, "#d9e1f4", BLUE, 1.6)
    s += text(nx + w / 4, y + h / 2 + 7, "N", 19, RED, "middle", "bold")
    s += text(sx + w / 4, y + h / 2 + 7, "S", 19, BLUE, "middle", "bold")
    return s


def compass(cx, cy, ang, r=20):
    """Компас: голка N (червона) під кутом ang (градуси), S (синя) навпроти."""
    s = circle(cx, cy, r, "#fff", INK, 1.6)
    a = math.radians(ang)
    s += line(cx, cy, cx + (r - 4) * math.cos(a), cy + (r - 4) * math.sin(a), RED, 2.4)
    s += line(cx, cy, cx - (r - 4) * math.cos(a), cy - (r - 4) * math.sin(a), BLUE, 2.4)
    s += circle(cx, cy, 2, INK, INK, 0)
    return s


def galvo(cx, cy, deflect=0, r=26, label="G"):
    """Гальванометр: стрілка, відхилена на 'deflect' градусів (+ праворуч)."""
    s = circle(cx, cy, r, "#fff", INK, 2)
    piv = cy + r * 0.55
    L = r * 1.4
    a = math.radians(90 - deflect)
    nx = cx + L * math.cos(a)
    ny = piv - L * math.sin(a)
    col = RED if deflect > 0 else (BLUE if deflect < 0 else INK)
    s += line(cx, piv, nx, ny, col, 2.4)
    s += circle(cx, piv, 2.5, INK, INK, 0)
    s += text(cx, cy - r + 12, "0", 10, GREY, "middle")
    s += text(cx, cy + r + 15, label, 13, INK, "middle", "bold")
    return s


def battery(cx, cy):
    s = line(cx, cy - 30, cx, cy - 9, INK, 2.4)
    s += line(cx - 16, cy - 9, cx + 16, cy - 9, INK, 2.6)
    s += line(cx - 9, cy + 2, cx + 9, cy + 2, INK, 5)
    s += line(cx, cy + 2, cx, cy + 30, INK, 2.4)
    return s, (cx, cy - 30), (cx, cy + 30)


def switch(x1, y, x2, closed=False):
    """Перемикач між (x1,y) і (x2,y)."""
    s = circle(x1, y, 3, INK, INK, 0)
    s += circle(x2, y, 3, INK, INK, 0)
    if closed:
        s += line(x1, y, x2, y, INK, 2.4)
    else:
        s += line(x1, y, x2 - 4, y - 14, INK, 2.4)
    return s


# ── Рис. 8.0.1 — таймлайн «ланцюг питань» ────────────────────────────────────
def fig_timeline():
    W, H = 880, 640
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: рух магніту народжує струм", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "кожен крок — нове питання (сірим — те, що стане змістом Розділу 8)",
              12.5, GREY, "middle", style="italic")
    spine = 210
    top, bot = 96, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1820", "Ерстед / Ørsted", "Струм відхиляє компас — електрика РОБИТЬ магнетизм", False, False),
        ("1820–25", "Ампер / Ampère", "Струми діють один на одного; котушка = магніт (електродинаміка)", False, False),
        ("1820-ті", "Зворотне питання", "А чи зробить магніт струм? Усі шукають сталий ефект — і марно", False, False),
        ("1831", "Фарадей / Faraday", "ТАК — але лише при ЗМІНІ поля: електромагнітна індукція", False, True),
        ("1830–32", "Генрі / Henry", "Котушка опирається зміні ВЛАСНОГО струму — самоіндукція, «генрі»", False, False),
        ("1834", "Ленц / Lenz", "Наведений струм завжди ПРОТИ зміни (збереження енергії)", False, False),
        ("Розділ 8", "Котушка", "Що таке індуктивність і чому котушка не любить зміни струму", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 28 + (bot - top - 56) * i / (n - 1)
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
    save("fig-8-0-1-timeline.svg", s)


# ── Рис. 8.0.2 — дослід Ерстеда (кругове поле струму) ────────────────────────
def fig_oersted():
    W, H = 720, 470
    s = header(W, H)
    s += text(W / 2, 34, "Дослід Ерстеда (1820): струм робить кругове магнітне поле", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "переріз дроту зі струмом «на нас»; поле обвиває його кільцями, компаси стають по дотичній",
              12, GREY, "middle", style="italic")
    cx, cy = 360, 270
    # концентричні кільця поля
    for r in (60, 105, 150):
        s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{GREEN}" stroke-width="1.6" stroke-dasharray="5,5"/>\n'
    # стрілка напрямку поля на середньому кільці
    s += arrow(cx + 105, cy - 8, cx + 105, cy + 12, GREEN, 2)
    s += text(cx + 120, cy + 4, "B", 14, GREEN, "start", "bold")
    # дріт зі струмом «на нас» (⊙)
    s += circle(cx, cy, 13, "#fff", INK, 2.4)
    s += circle(cx, cy, 3.5, INK, INK, 0)
    s += text(cx, cy - 24, "струм на нас", 12, INK, "middle", "bold")
    # компаси на середньому кільці (по дотичній → кут = радіус+90°)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        px = cx + 105 * math.cos(a)
        py = cy + 105 * math.sin(a)
        s += compass(px, py, ang + 90, 18)
    s += rect(60, H - 46, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 26, "Дві «окремі» сили Гілберта виявились пов'язані: рух заряду народжує магнетизм.",
              12.5, INK, "middle", "bold")
    save("fig-8-0-2-oersted.svg", s)


# ── Рис. 8.0.3 — індукційне кільце Фарадея ───────────────────────────────────
def fig_faraday_ring():
    W, H = 760, 460
    s = header(W, H)
    s += text(W / 2, 34, "Індукційне кільце Фарадея (1831): струм наводиться лише при ЗМІНІ", 17.5, INK, "middle", "bold")
    cx, cy = 380, 230
    # залізне кільце (кільцевий тор)
    s += f'<circle cx="{cx}" cy="{cy}" r="92" fill="none" stroke="{IRON}" stroke-width="20"/>\n'
    s += text(cx, cy + 5, "залізне", 12, GREY, "middle")
    s += text(cx, cy + 21, "кільце", 12, GREY, "middle")
    # первинна котушка (ліворуч) — кілька витків міді на дузі
    for i in range(5):
        ay = cy - 40 + i * 20
        s += f'<ellipse cx="{cx-92}" cy="{ay}" rx="20" ry="8" fill="none" stroke="{COPP}" stroke-width="2.2"/>\n'
    s += text(cx - 92, cy - 60, "первинна", 11.5, COPP, "middle", "bold")
    # вторинна котушка (праворуч)
    for i in range(5):
        ay = cy - 40 + i * 20
        s += f'<ellipse cx="{cx+92}" cy="{ay}" rx="20" ry="8" fill="none" stroke="{COPP}" stroke-width="2.2"/>\n'
    s += text(cx + 92, cy - 60, "вторинна", 11.5, COPP, "middle", "bold")
    # батарея + вимикач до первинної
    bx = cx - 92
    s += line(bx - 20, cy + 40, bx - 20, cy + 110, INK, 2)
    s += line(bx + 20, cy + 40, bx + 20, cy + 110, INK, 2)
    bat, bt, bb = battery(bx - 20, cy + 110)
    # (battery drawn vertically at that point would overflow; draw simple cell)
    s += line(bx - 20, cy + 110, bx + 20, cy + 110, INK, 2)
    s += line(bx - 4, cy + 104, bx - 4, cy + 116, INK, 2.4)
    s += line(bx + 4, cy + 100, bx + 4, cy + 120, INK, 4)
    s += switch(bx - 20, cy + 75, bx - 2, closed=False)
    s += text(bx - 40, cy + 75, "вимикач", 11, INK, "end")
    s += text(bx, cy + 134, "батарея", 11, INK, "middle")
    # гальванометр на вторинній
    gx = cx + 92
    s += line(gx - 20, cy + 40, gx - 20, cy + 95, INK, 2)
    s += line(gx + 20, cy + 40, gx + 20, cy + 95, INK, 2)
    s += line(gx - 20, cy + 95, gx - 6, cy + 95, INK, 2)
    s += line(gx + 20, cy + 95, gx + 6, cy + 95, INK, 2)
    s += galvo(gx, cy + 95, deflect=24, r=22)
    # підпис-висновок
    s += rect(60, H - 64, W - 120, 48, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 42, "Гальванометр смикається ТІЛЬКИ в мить вмикання чи вимикання струму в первинній —",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 24, "коли поле змінюється. Сталий струм → стале поле → нічого. Ось чого всі не помічали.",
              12, INK, "middle", "bold")
    save("fig-8-0-3-faraday-ring.svg", s)


# ── Рис. 8.0.4 — рух магніту крізь котушку ───────────────────────────────────
def fig_moving_magnet():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Рух магніту крізь котушку наводить струм", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "напрямок струму залежить від напрямку руху; нерухомий магніт — нуль",
              12, GREY, "middle", style="italic")

    def panel(x0, title, arrow_dir, deflect, note):
        out = rect(x0, 80, 270, 230, "none", FAINT, 1.6, 12)
        out += text(x0 + 135, 104, title, 13.5, INK, "middle", "bold")
        ccx, ccy = x0 + 160, 180
        coil, (xl, xr) = coil_h(ccx, ccy, 70, 5, 26)
        out += coil
        # магніт ліворуч від котушки
        out += bar_magnet(x0 + 30, ccy - 16, 70, 32, n_left=False)
        if arrow_dir != 0:
            ax = x0 + 105
            out += arrow(ax, ccy - 40, ax + 40 * arrow_dir, ccy - 40, INK, 2.4)
            out += text(ax + 20 * arrow_dir, ccy - 48, note, 11, INK, "middle", "bold")
        else:
            out += text(x0 + 100, ccy - 44, note, 11, GREY, "middle", "bold")
        # гальванометр праворуч
        out += line(xr, ccy - 26, xr + 24, ccy - 26, INK, 2)
        out += line(xr, ccy + 26, xr + 24, ccy + 26, INK, 2)
        out += line(xr + 24, ccy - 26, xr + 24, ccy - 18, INK, 2)
        out += line(xr + 24, ccy + 26, xr + 24, ccy + 18, INK, 2)
        out += galvo(xr + 24, ccy, deflect, 20)
        return out

    s += panel(20, "заштовхуємо", 1, 26, "→")
    s += panel(300, "тримаємо", 0, 0, "нерухомо")
    s += panel(580, "витягуємо", -1, -26, "←")
    s += text(W / 2, H - 18, "Струм народжує саме ЗМІНА потоку (рух), а не присутність магніту.",
              12.5, GREEN, "middle", "bold")
    save("fig-8-0-4-moving-magnet.svg", s)


# ── Рис. 8.0.5 — закон Ленца ─────────────────────────────────────────────────
def fig_lenz():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 34, "Закон Ленца: наведений струм протидіє зміні", 19, INK, "middle", "bold")

    def panel(x0, title, approaching):
        out = rect(x0, 76, 340, 240, "none", FAINT, 1.6, 12)
        out += text(x0 + 170, 100, title, 13.5, INK, "middle", "bold")
        ccx, ccy = x0 + 230, 190
        coil, (xl, xr) = coil_h(ccx, ccy, 64, 5, 30)
        out += coil
        # магніт ліворуч, N до котушки
        mx = x0 + 40 if approaching else x0 + 70
        out += bar_magnet(mx, ccy - 18, 74, 36, n_left=False)  # S | N (N праворуч, до котушки)
        # рух магніту
        if approaching:
            out += arrow(mx + 80, ccy - 36, mx + 120, ccy - 36, INK, 2.4)
            out += text(mx + 100, ccy - 44, "наближається", 10.5, INK, "middle", "bold")
        else:
            out += arrow(mx + 120, ccy - 36, mx + 80, ccy - 36, INK, 2.4)
            out += text(mx + 100, ccy - 44, "віддаляється", 10.5, INK, "middle", "bold")
        # наведений полюс на лівому торці котушки
        face = "N" if approaching else "S"
        fcol = RED if approaching else BLUE
        out += text(xl - 4, ccy + 5, face, 18, fcol, "middle", "bold")
        out += text(xl + 14, ccy + 44, "наведений", 10, fcol, "middle")
        # сила опору
        if approaching:
            out += arrow(ccx - 6, ccy + 60, ccx - 50, ccy + 60, RED, 2.2)
            out += text(ccx - 28, ccy + 78, "відштовхує", 10.5, RED, "middle", "bold")
        else:
            out += arrow(ccx - 50, ccy + 60, ccx - 6, ccy + 60, BLUE, 2.2)
            out += text(ccx - 28, ccy + 78, "притягує", 10.5, BLUE, "middle", "bold")
        return out

    s += panel(20, "магніт наближається → котушка відштовхує", True)
    s += panel(440, "магніт віддаляється → котушка притягує", False)
    s += rect(60, H - 40, W - 120, 28, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 21, "Котушка завжди «впирається» зміні — інакше енергія бралася б з нічого (вічний двигун).",
              11.5, INK, "middle", "bold")
    save("fig-8-0-5-lenz.svg", s)


# ── Рис. 8.0.6 — що дала індукція ────────────────────────────────────────────
def fig_payoff():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Одне відкриття — багато машин", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "усе це — грані «зміна магнітного поля наводить струм»", 12.5, GREY, "middle", style="italic")
    cards = [
        ("ГЕНЕРАТОР", "рух → струм", "обертаєш магніт повз котушки", LGRN, GREEN),
        ("ДВИГУН", "струм → рух", "струм у котушці в полі — крутить", LBLUE, BLUE),
        ("ТРАНСФОРМАТОР", "зм. струм → струм", "обмотка наводить обмотку", LGRN, GREEN),
        ("САМОІНДУКЦІЯ", "зміна струму → напруга", "котушка опирається собі (§8.5)", LRED, RED),
    ]
    for i, (t, f, d, fill, col) in enumerate(cards):
        x = 40 + (i % 2) * 370
        y = 90 + (i // 2) * 135
        s += rect(x, y, 340, 115, fill, col, 1.8, 12)
        s += text(x + 20, y + 34, t, 16, INK, "start", "bold")
        s += text(x + 20, y + 62, f, 15, col, "start", "bold")
        s += text(x + 20, y + 90, d, 12, GREY, "start", style="italic")
    save("fig-8-0-6-payoff.svg", s)


# ── §8.1 будівельники ────────────────────────────────────────────────────────
def b_out(cx, cy, r=9, col=GREEN):
    return circle(cx, cy, r, "#fff", col, 1.8) + circle(cx, cy, 2.2, col, col, 0)


def b_in(cx, cy, r=9, col=GREEN):
    s = circle(cx, cy, r, "#fff", col, 1.8)
    s += line(cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6, col, 1.6)
    s += line(cx - r * 0.6, cy + r * 0.6, cx + r * 0.6, cy - r * 0.6, col, 1.6)
    return s


# ── Рис. 8.1.1 — поле прямого дроту (бічний вид) ─────────────────────────────
def fig11_wire_field():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 34, "Струм робить магнітне поле навколо дроту", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "бічний вид: над дротом поле «на нас» (⊙), під ним — «від нас» (⊗)",
              12, GREY, "middle", style="italic")
    y = 200
    s += line(110, y, 600, y, COPP, 4)
    s += arrow(540, y, 600, y, COPP, 4)
    s += text(355, y - 4, "струм I", 13, COPP, "middle", "bold")
    for x in (200, 290, 380, 470):
        s += b_out(x, y - 46)
        s += b_in(x, y + 46)
    s += text(160, y - 46, "B:", 13, GREEN, "end", "bold")
    s += text(160, y + 50, "B:", 13, GREEN, "end", "bold")
    s += rect(60, H - 58, W - 120, 40, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 40, "Права рука: великий палець уздовж струму — зігнуті пальці показують, куди",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 23, "обвиває поле (над дротом — до вас, під ним — від вас).", 12, INK, "middle", "bold")
    save("fig-8-1-1-wire-field.svg", s)


# ── Рис. 8.1.2 — правило правої руки для котушки ─────────────────────────────
def fig11_right_hand():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 34, "Правило правої руки для котушки", 20, INK, "middle", "bold")
    cx, cy = 330, 190
    coil, (xl, xr) = coil_h(cx, cy, 180, 6, 40)
    s += coil
    # струм у витках (стрілки на верхніх дугах)
    for i in range(6):
        x = xl + (i + 0.5) * (xr - xl) / 6
        s += arrow(x - 8, cy - 40, x + 8, cy - 40, COPP, 1.8)
    s += text(cx, cy - 58, "струм у витках", 11.5, COPP, "middle", "bold")
    # вісь поля → N
    s += arrow(xr + 10, cy, xr + 90, cy, GREEN, 3)
    s += text(xr + 60, cy - 12, "B", 14, GREEN, "middle", "bold")
    s += text(xr + 95, cy + 5, "N", 18, RED, "start", "bold")
    s += text(xl - 14, cy + 5, "S", 18, BLUE, "end", "bold")
    s += rect(60, H - 52, W - 120, 36, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 30, "Зігнуті пальці — за струмом у витках; відставлений великий палець — на північний полюс.",
              11.5, INK, "middle", "bold")
    save("fig-8-1-2-right-hand.svg", s)


# ── Рис. 8.1.3 — поле одного витка ───────────────────────────────────────────
def fig11_loop():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Один виток: кільцеві поля складаються крізь отвір", 18, INK, "middle", "bold")
    cx, cy = 320, 190
    # виток (еліпс, вид збоку — вертикальний)
    s += f'<ellipse cx="{cx}" cy="{cy}" rx="22" ry="80" fill="none" stroke="{COPP}" stroke-width="3"/>\n'
    s += arrow(cx + 22, cy - 30, cx + 22, cy + 10, COPP, 2)
    s += text(cx, cy + 100, "струм у витку", 11.5, COPP, "middle", "bold")
    # поле крізь отвір
    s += arrow(cx - 120, cy, cx + 120, cy, GREEN, 3)
    s += text(cx + 130, cy + 5, "B", 14, GREEN, "start", "bold")
    s += text(cx + 70, cy - 12, "поле крізь петлю", 11, GREEN, "middle", style="italic")
    s += text(cx + 100, cy + 30, "N", 18, RED, "middle", "bold")
    s += text(cx - 100, cy + 30, "S", 18, BLUE, "middle", "bold")
    s += rect(60, H - 50, W - 120, 34, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 28, "Виток зі струмом = крихітний магніт: один бік N, інший S. Це зародок котушки.",
              12, INK, "middle", "bold")
    save("fig-8-1-3-loop.svg", s)


# ── Рис. 8.1.4 — соленоїд концентрує поле ────────────────────────────────────
def fig11_solenoid():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Котушка концентрує поле: соленоїд = брусковий магніт", 18, INK, "middle", "bold")
    cx, cy = 380, 200
    coil, (xl, xr) = coil_h(cx, cy, 200, 7, 44)
    s += coil
    # сильне однорідне поле всередині (зелені стрілки вздовж осі)
    for dy in (-22, 0, 22):
        s += arrow(xl + 12, cy + dy, xr - 12, cy + dy, GREEN, 2)
    s += text(cx, cy + 64, "сильне однорідне поле всередині", 11.5, GREEN, "middle", "bold")
    # зовнішні лінії від N до S (дуги)
    s += f'<path d="M {xr-4},{cy-44} C {xr+120},{cy-150} {xl-120},{cy-150} {xl+4},{cy-44}" fill="none" stroke="{GREEN}" stroke-width="1.6"/>\n'
    s += f'<path d="M {xr-4},{cy+44} C {xr+120},{cy+150} {xl-120},{cy+150} {xl+4},{cy+44}" fill="none" stroke="{GREEN}" stroke-width="1.6"/>\n'
    s += text(xr + 18, cy + 4, "N", 18, RED, "start", "bold")
    s += text(xl - 18, cy + 4, "S", 18, BLUE, "end", "bold")
    s += rect(60, H - 50, W - 120, 34, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 28, "Поля багатьох витків складаються в одне сильне поле — котушка збирає розсіяне поле дроту.",
              11.5, INK, "middle", "bold")
    save("fig-8-1-4-solenoid.svg", s)


# ── Рис. 8.1.5 — магнітні лінії замкнені ─────────────────────────────────────
def fig11_field_lines():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Магнітні лінії замкнені; електричні — від зарядів", 18, INK, "middle", "bold")
    # ліворуч — електричні (від + до −)
    s += rect(40, 70, 330, 250, "none", FAINT, 1.6, 12)
    s += text(205, 94, "електричне поле", 13, INK, "middle", "bold")
    s += circle(120, 200, 22, LRED, RED, 2)
    s += plus(120, 200, 11, RED)
    s += circle(290, 200, 22, LBLUE, BLUE, 2)
    s += minus(290, 200, 11, BLUE)
    for dy in (-40, 0, 40):
        s += f'<path d="M {142},{200+dy*0.7:.0f} Q {205},{200+dy:.0f} {268},{200+dy*0.7:.0f}" fill="none" stroke="{GREEN}" stroke-width="1.8" marker-end="url(#aGreen)"/>\n'
    s += text(205, 300, "починаються на + , кінчаються на −", 11, GREY, "middle", style="italic")
    # праворуч — магнітні (замкнені)
    s += rect(390, 70, 330, 250, "none", FAINT, 1.6, 12)
    s += text(555, 94, "магнітне поле", 13, INK, "middle", "bold")
    s += rect(525, 175, 60, 50, "#eceae2", IRON, 1.6)
    s += text(540, 205, "N", 15, RED, "middle", "bold")
    s += text(570, 205, "S", 15, BLUE, "middle", "bold")
    for rr in (40, 70):
        s += f'<ellipse cx="555" cy="200" rx="{60+rr}" ry="{rr}" fill="none" stroke="{GREEN}" stroke-width="1.6"/>\n'
    s += arrow(555 - 2, 200 - 70, 555 + 2, 200 - 70, GREEN, 1.8)
    s += text(555, 300, "завжди замкнені петлі (нема монополя)", 11, GREY, "middle", style="italic")
    save("fig-8-1-5-field-lines.svg", s)


# ── Рис. 8.1.6 — осердя підсилює поле ────────────────────────────────────────
def fig11_core():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Осердя множить поле: домени вишиковуються", 19, INK, "middle", "bold")

    def domains(x0, y0, aligned):
        out = ""
        for ix in range(5):
            for iy in range(3):
                dx = x0 + ix * 18
                dy = y0 + iy * 18
                if aligned:
                    out += arrow(dx - 6, dy, dx + 6, dy, RED, 1.4)
                else:
                    ang = (ix * 53 + iy * 117) % 360
                    a = math.radians(ang)
                    out += arrow(dx - 6 * math.cos(a), dy - 6 * math.sin(a),
                                 dx + 6 * math.cos(a), dy + 6 * math.sin(a), GREY, 1.3)
        return out

    # без осердя
    s += rect(40, 76, 330, 240, "none", FAINT, 1.6, 12)
    s += text(205, 100, "без осердя — слабке поле", 12.5, INK, "middle", "bold")
    coil, (xl, xr) = coil_h(205, 180, 120, 5, 34)
    s += coil
    s += arrow(xl + 8, 180, xr - 8, 180, GREEN, 1.6)
    s += domains(150, 250, False)
    s += text(205, 300, "домени врізнобіч — гасяться", 10.5, GREY, "middle", style="italic")
    # з осердям
    s += rect(390, 76, 330, 240, "none", FAINT, 1.6, 12)
    s += text(555, 100, "із залізним осердям — ×сотні", 12.5, INK, "middle", "bold")
    s += rect(495, 162, 120, 36, "#eceae2", IRON, 1.4)
    coil2, (xl2, xr2) = coil_h(555, 180, 120, 5, 34)
    s += coil2
    s += arrow(xl2 + 6, 180, xr2 - 6, 180, GREEN, 3)
    s += domains(500, 250, True)
    s += text(555, 300, "домени в один бік — додають своє поле", 10.5, GREY, "middle", style="italic")
    save("fig-8-1-6-core.svg", s)


# ── Рис. 8.1.7 — ампер-витки ─────────────────────────────────────────────────
def fig11_ampere_turns():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Сила поля ∝ ампер-витки (N · I)", 20, INK, "middle", "bold")
    # дві котушки з однаковим NI
    s += _box_coil(120, "100 витків × 0.1 А", "= 10 А·витків")
    s += text(380, 180, "≈", 30, INK, "middle", "bold")
    s += _box_coil(440, "10 витків × 1 А", "= 10 А·витків")
    s += text(W / 2, 290, "однакові ампер-витки → однакове поле; а осердя множить його ще в сотні разів",
              12, GREEN, "middle", "bold")
    save("fig-8-1-7-ampere-turns.svg", s)


def _box_coil(x0, t1, t2):
    s = rect(x0, 70, 200, 150, "none", FAINT, 1.6, 12)
    coil, (xl, xr) = coil_h(x0 + 100, 130, 110, 6, 30)
    s += coil
    s += arrow(xl + 8, 130, xr - 8, 130, GREEN, 2)
    s += text(x0 + 100, 196, t1, 12, INK, "middle", "bold")
    s += text(x0 + 100, 214, t2, 12, GREY, "middle", style="italic")
    return s


# ── Рис. 8.1.8 — дзеркало конденсатора ───────────────────────────────────────
def fig11_dual():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Дзеркало: конденсатор тримає E-поле, котушка — B-поле", 18, INK, "middle", "bold")
    # конденсатор
    s += rect(40, 76, 330, 230, "none", FAINT, 1.6, 12)
    s += text(205, 100, "конденсатор", 13.5, INK, "middle", "bold")
    s += rect(150, 150, 12, 90, "#f7dada", RED, 1.6)
    s += rect(248, 150, 12, 90, "#dbe3f7", BLUE, 1.6)
    for dy in (-28, 0, 28):
        s += arrow(164, 195 + dy, 246, 195 + dy, GREEN, 2)
    s += line(150, 195, 110, 195, INK, 2)
    s += line(260, 195, 300, 195, INK, 2)
    s += text(205, 270, "електричне поле в зазорі", 11, GREEN, "middle", "bold")
    s += text(205, 288, "(від розділеного заряду)", 10.5, GREY, "middle", style="italic")
    # котушка
    s += rect(390, 76, 330, 230, "none", FAINT, 1.6, 12)
    s += text(555, 100, "котушка", 13.5, INK, "middle", "bold")
    coil, (xl, xr) = coil_h(555, 195, 150, 6, 40)
    s += coil
    s += arrow(xl + 10, 195, xr - 10, 195, GREEN, 2.4)
    s += text(555, 270, "магнітне поле в осерді", 11, GREEN, "middle", "bold")
    s += text(555, 288, "(від струму)", 10.5, GREY, "middle", style="italic")
    save("fig-8-1-8-dual.svg", s)


# ── §8.2 будівельники ────────────────────────────────────────────────────────
def cap_sym(cx, cy, half=15, gap=9, col=INK):
    s = line(cx - gap / 2, cy - half, cx - gap / 2, cy + half, col, 2.6)
    s += line(cx + gap / 2, cy - half, cx + gap / 2, cy + half, col, 2.6)
    return s, cx - gap / 2, cx + gap / 2


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


# ── Рис. 8.2.1 — самоіндукція ────────────────────────────────────────────────
def fig21_self_induction():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Самоіндукція: зміна струму наводить напругу в самій котушці", 17.5, INK, "middle", "bold")
    cx, cy = 360, 190
    coil, (xl, xr) = coil_h(cx, cy, 180, 6, 42)
    s += coil
    # струм росте
    s += arrow(xl - 70, cy, xl - 8, cy, COPP, 3)
    s += text(xl - 40, cy - 12, "↑ i", 15, COPP, "middle", "bold")
    s += text(xl - 40, cy + 22, "струм росте", 10.5, COPP, "middle")
    # поле росте
    for dy in (-20, 0, 20):
        s += arrow(xl + 14, cy + dy, xr - 14, cy + dy, GREEN, 1.8)
    s += text(cx, cy - 56, "↑ B (поле росте)", 12, GREEN, "middle", "bold")
    # наведена напруга проти
    s += text(xr + 30, cy - 14, "+", 18, BLUE, "middle", "bold")
    s += text(xr + 30, cy + 22, "−", 18, RED, "middle", "bold")
    s += arrow(xr + 70, cy + 30, xr + 70, cy - 30, BLUE, 2.4)
    s += text(xr + 95, cy, "проти-ЕРС", 11.5, BLUE, "start", "bold")
    s += text(xr + 95, cy + 16, "(проти зміни)", 10.5, GREY, "start", style="italic")
    s += rect(60, H - 50, W - 120, 34, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 28, "Фарадей: зміна потоку наводить напругу. Ленц: вона протидіє зміні струму.",
              12, INK, "middle", "bold")
    save("fig-8-2-1-self-induction.svg", s)


# ── Рис. 8.2.2 — V = L·di/dt (осцилограми) ───────────────────────────────────
def fig21_vldidt():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 32, "V = L·di/dt: напруга — від ШВИДКОСТІ зміни струму", 18, INK, "middle", "bold")
    ox, w = 110, 540
    # верхній графік — струм
    oyi, hi = 175, 95
    s += arrow(ox, oyi, ox, oyi - hi - 12, INK, 1.8)
    s += arrow(ox, oyi, ox + w + 12, oyi, INK, 1.8)
    s += text(ox - 8, oyi - hi - 6, "i", 14, COPP, "end", "bold")
    p = [(ox, oyi), (ox + 0.35 * w, oyi - 0.8 * hi), (ox + 0.62 * w, oyi - 0.8 * hi),
         (ox + w, oyi - 1.0 * hi)]
    s += _poly(p, COPP, 2.8)
    s += text(ox + 0.18 * w, oyi - 0.85 * hi, "круто", 11, COPP, "middle", "bold")
    s += text(ox + 0.48 * w, oyi - 0.7 * hi, "сталий", 11, GREY, "middle")
    s += text(ox + 0.82 * w, oyi - 0.78 * hi, "полого", 11, COPP, "middle")
    # нижній графік — напруга
    oyv, hv = 380, 95
    s += arrow(ox, oyv, ox, oyv - hv - 12, INK, 1.8)
    s += arrow(ox, oyv, ox + w + 12, oyv, INK, 1.8)
    s += text(ox - 8, oyv - hv - 6, "V", 14, BLUE, "end", "bold")
    pv = [(ox, oyv - 0.85 * hv), (ox + 0.35 * w, oyv - 0.85 * hv), (ox + 0.35 * w, oyv),
          (ox + 0.62 * w, oyv), (ox + 0.62 * w, oyv - 0.28 * hv), (ox + w, oyv - 0.28 * hv)]
    s += _poly(pv, BLUE, 2.8)
    s += text(ox + 0.18 * w, oyv - 0.92 * hv, "велика", 11, BLUE, "middle", "bold")
    s += text(ox + 0.48 * w, oyv - 0.12 * hv, "нуль", 11, GREY, "middle", "bold")
    s += text(ox + 0.82 * w, oyv - 0.36 * hv, "мала", 11, BLUE, "middle")
    s += text(W / 2, H - 12, "Котушка «бачить» нахил струму: крутий нахил → велика напруга, сталий струм → нуль.",
              11.5, GREY, "middle", style="italic")
    save("fig-8-2-2-vldidt.svg", s)


# ── Рис. 8.2.3 — котушка як інерція ──────────────────────────────────────────
def fig21_inertia():
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 34, "Конденсатор — пружина, котушка — інерція", 19, INK, "middle", "bold")
    # конденсатор = пружина
    s += rect(40, 76, 330, 210, "none", FAINT, 1.6, 12)
    s += text(205, 100, "конденсатор = пружина", 13, INK, "middle", "bold")
    cs, lx, rx = cap_sym(150, 180, 22, 12)
    s += line(110, 180, lx, 180, INK, 2)
    s += cs
    # пружинка
    sp = [(rx, 180)]
    for i in range(8):
        sp.append((rx + 10 + i * 16, 180 + (12 if i % 2 == 0 else -12)))
    sp.append((rx + 138, 180))
    s += _poly(sp, GREEN, 2)
    s += text(205, 250, "опирається зміні НАПРУГИ", 11.5, GREEN, "middle", "bold")
    s += text(205, 268, "(пружинить, запасає ½CV²)", 10.5, GREY, "middle", style="italic")
    # котушка = маса/маховик
    s += rect(390, 76, 330, 210, "none", FAINT, 1.6, 12)
    s += text(555, 100, "котушка = інерція (маховик)", 13, INK, "middle", "bold")
    coil, (xl, xr) = coil_h(500, 180, 90, 5, 30)
    s += line(460, 180, xl, 180, INK, 2)
    s += coil
    s += circle(620, 180, 34, "#eceae2", INK, 2.4)
    s += circle(620, 180, 6, INK, INK, 0)
    s += arrow(620 + 28, 180 - 14, 620 + 30, 180 + 14, GREY, 2)
    s += text(555, 250, "опирається зміні СТРУМУ", 11.5, BLUE, "middle", "bold")
    s += text(555, 268, "(розкручений струм прагне тривати)", 10.5, GREY, "middle", style="italic")
    save("fig-8-2-3-inertia.svg", s)


# ── Рис. 8.2.4 — генрі та діапазон ───────────────────────────────────────────
def fig21_henry():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 34, "Генрі = В·с/А; реальні котушки — мкГн…Гн", 19, INK, "middle", "bold")
    x0, x1, y = 90, 690, 170
    s += line(x0, y, x1, y, INK, 2.4)

    def X(e):
        return x0 + (e + 6) / 6 * (x1 - x0)

    for e in range(-6, 1):
        s += line(X(e), y - 5, X(e), y + 5, INK, 1.3)
    majors = {-6: "1 мкГн", -3: "1 мГн", 0: "1 Гн"}
    for e, lab in majors.items():
        s += line(X(e), y - 9, X(e), y + 9, INK, 2.6)
        s += text(X(e), y + 30, lab, 13, INK, "middle", "bold")
    s += rect(X(-6), 110, X(-3) - X(-6), 18, "#fdeecf", "none", 0, 4)
    s += text((X(-6) + X(-3)) / 2, 123, "радіо, ВЧ", 11, INK, "middle", "bold")
    s += rect(X(-3.5), 134, X(0.3) - X(-3.5), 18, "#dbe7f5", "none", 0, 4)
    s += text((X(-3.5) + X(0.3)) / 2, 147, "фільтри, дроселі живлення", 11, INK, "middle", "bold")
    s += text(W / 2, H - 22, "Чим більша L, тим завзятіше котушка опирається зміні струму.",
              12, GREY, "middle", style="italic")
    save("fig-8-2-4-henry.svg", s)


# ── Рис. 8.2.5 — L ∝ N² ──────────────────────────────────────────────────────
def fig21_n_squared():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Удвічі більше витків — учетверо більша індуктивність", 18, INK, "middle", "bold")
    coil1, (xl1, xr1) = coil_h(190, 170, 110, 5, 34)
    s += coil1
    s += text(190, 230, "N витків", 12.5, INK, "middle", "bold")
    s += text(190, 250, "L", 16, GREEN, "middle", "bold")
    s += text(380, 175, "→", 28, INK, "middle", "bold")
    coil2, (xl2, xr2) = coil_h(560, 170, 130, 10, 34)
    s += coil2
    s += text(560, 230, "2N витків", 12.5, INK, "middle", "bold")
    s += text(560, 250, "4 · L", 16, GREEN, "middle", "bold")
    s += rect(60, H - 48, W - 120, 32, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 27, "L ∝ N²: подвійні витки роблять подвійне поле, що пронизує подвійні витки → ×4.",
              11.5, INK, "middle", "bold")
    save("fig-8-2-5-n-squared.svg", s)


# ── Рис. 8.2.6 — від чого залежить L ─────────────────────────────────────────
def fig21_determinants():
    W, H = 740, 320
    s = header(W, H)
    s += text(W / 2, 36, "Що задає індуктивність котушки", 20, INK, "middle", "bold")
    cy = 150
    s += text(150, cy, "L", 38, INK, "middle", "bold")
    s += text(196, cy, "∝", 26, INK, "middle")
    s += text(250, cy, "μ", 28, "#9c7b46", "middle", "bold")
    s += text(286, cy, "·", 22, INK, "middle")
    s += text(326, cy - 14, "N²", 30, GREEN, "middle", "bold")
    s += text(326, cy + 8, "", 1, INK, "middle")
    s += text(390, cy - 16, "· A", 26, GREEN, "middle", "bold")
    s += line(420, cy + 2, 470, cy + 2, INK, 2.4)
    s += text(445, cy - 14, "", 1, INK, "middle")
    s += text(445, cy + 34, "довжина", 16, RED, "middle", "bold")
    s += arrow(326, cy - 50, 326, cy - 28, GREEN, 1.8)
    s += text(326, cy - 58, "↑↑ витки (квадрат)", 12, GREEN, "middle", "bold")
    s += arrow(250, cy + 40, 250, cy + 16, "#9c7b46", 1.8)
    s += text(250, cy + 58, "↑ осердя", 12, "#9c7b46", "middle", "bold")
    s += text(445, cy + 54, "↑ довжина → ↓ L", 12, RED, "middle", "bold")
    s += rect(110, 232, W - 220, 56, "#fbfbfb", GREY, 1.4, 10)
    s += text(W / 2, 256, "Дзеркало ємності C ∝ ε·A/d (§7.2): там діелектрик ε, тут осердя μ.",
              13, INK, "middle", "bold")
    s += text(W / 2, 277, "Осердя множить L у сотні разів — найсильніший важіль.", 11.5, GREY, "middle", style="italic")
    save("fig-8-2-6-determinants.svg", s)


# ── Рис. 8.2.7 — котушка пропускає постійний струм ───────────────────────────
def fig21_dc_short():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 34, "Постійний струм котушка пропускає; зміні — опирається", 18, INK, "middle", "bold")
    # сталий струм
    s += rect(40, 76, 330, 200, "none", FAINT, 1.6, 12)
    s += text(205, 100, "сталий струм (di/dt = 0)", 12.5, INK, "middle", "bold")
    coil, (xl, xr) = coil_h(205, 165, 110, 5, 28)
    s += line(120, 165, xl, 165, INK, 2.2)
    s += line(xr, 165, 290, 165, INK, 2.2)
    s += coil
    s += text(205, 220, "V = 0 → просто дріт", 13, GREEN, "middle", "bold")
    s += text(205, 240, "(пропускає постійний струм)", 10.5, GREY, "middle", style="italic")
    # струм змінюється
    s += rect(390, 76, 330, 200, "none", FAINT, 1.6, 12)
    s += text(555, 100, "струм змінюється", 12.5, INK, "middle", "bold")
    coil2, (xl2, xr2) = coil_h(555, 165, 110, 5, 28)
    s += line(470, 165, xl2, 165, INK, 2.2)
    s += line(xr2, 165, 640, 165, INK, 2.2)
    s += coil2
    s += arrow(455, 165, 468, 165, COPP, 2.4)
    s += text(555, 220, "V = L·di/dt ≠ 0 → опір", 13, BLUE, "middle", "bold")
    s += text(555, 240, "(дзеркало конденсатора)", 10.5, GREY, "middle", style="italic")
    save("fig-8-2-7-dc-short.svg", s)


# ── Рис. 8.2.8 — таблиця двоїстості ──────────────────────────────────────────
def fig21_duals():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Двоїстість: конденсатор ↔ котушка", 20, INK, "middle", "bold")
    rows = [("запасає енергію в…", "електричному полі", "магнітному полі"),
            ("реагує на зміну…", "напруги", "струму"),
            ("закон", "i = C·dV/dt", "V = L·di/dt"),
            ("одиниця", "фарад (Кл/В)", "генрі (В·с/А)"),
            ("постійний струм", "блокує", "пропускає"),
            ("аналогія", "пружина", "інерція (маса)")]
    x0, y0, c0, c1 = 60, 86, 320, 540
    s += text(c0, y0, "КОНДЕНСАТОР", 13.5, RED, "middle", "bold")
    s += text(c1, y0, "КОТУШКА", 13.5, BLUE, "middle", "bold")
    for i, (lab, a, b) in enumerate(rows):
        y = y0 + 26 + i * 44
        if i % 2 == 0:
            s += rect(x0, y - 18, W - 2 * x0, 40, "#f7f7f4", "none", 0, 4)
        s += text(x0 + 6, y + 6, lab, 12, GREY, "start", "bold")
        s += text(c0, y + 6, a, 13, INK, "middle", "bold")
        s += text(c1, y + 6, b, 13, INK, "middle", "bold")
    save("fig-8-2-8-duals.svg", s)


# ── §8.3 фігури ──────────────────────────────────────────────────────────────
def fig31_work_to_build():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Звідки енергія: розгін струму проти проти-ЕРС", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "поки струм наростає з нуля, рання потужність мала, пізня повна → середнє ½",
              12, GREY, "middle", style="italic")
    snaps = [(2, "i = I/3", "мало"), (4, "i = 2I/3", "більше"), (6, "i = I", "повна")]
    for k, (iw, ilab, plab) in enumerate(snaps):
        cx = 180 + k * 250
        coil, (xl, xr) = coil_h(cx, 200, 110, 5, 30)
        s += coil
        s += arrow(xl - 60, 200, xl - 8, 200, COPP, iw)
        s += text(cx, 262, ilab, 13, COPP, "middle", "bold")
        # проти-ЕРС
        s += text(xr + 18, 188, "+", 14, BLUE, "middle", "bold")
        s += text(xr + 18, 214, "−", 14, RED, "middle", "bold")
        s += text(cx, 150, "P = V·i: " + plab, 11.5, INK, "middle", "bold")
    s += rect(60, H - 44, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Робота джерела проти проти-ЕРС осідає в полі: W = ½·L·I² (½ — бо струм ріс із нуля).",
              12, INK, "middle", "bold")
    save("fig-8-3-1-work-to-build.svg", s)


def fig31_half_formula():
    W, H = 700, 420
    s = header(W, H)
    s += text(W / 2, 34, "Енергія — площа під лінією «потік–струм»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "Φ = L·I — пряма крізь нуль; площа під нею = трикутник ½·L·I²", 12, GREY, "middle", style="italic")
    ox, oy = 130, 360
    Ix, Fy = ox + 430, oy - 250
    s += f'<rect x="{ox:.1f}" y="{Fy:.1f}" width="{Ix-ox:.1f}" height="{oy-Fy:.1f}" fill="none" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="5,5"/>\n'
    s += f'<path d="M {ox:.1f},{oy:.1f} L {Ix:.1f},{oy:.1f} L {Ix:.1f},{Fy:.1f} Z" fill="#e1eef6" stroke="none"/>\n'
    s += arrow(ox, oy, ox, 80, INK, 2)
    s += arrow(ox, oy, 640, oy, INK, 2)
    s += text(648, oy + 4, "I", 15, COPP, "start", "bold")
    s += text(ox - 8, 74, "Φ", 15, GREEN, "middle", "bold")
    s += text(ox - 10, oy + 22, "0", 12, GREY, "middle")
    s += line(ox, oy, Ix, Fy, GREEN, 2.8)
    s += text((ox + Ix) / 2 + 30, (oy + Fy) / 2 - 55, "½·L·I²", 17, "#15347f", "middle", "bold")
    s += text(ox + 90, Fy - 10, "прямокутник Φ·I (якби стало)", 12, GREY, "start", style="italic")
    s += text(Ix, oy + 22, "I", 13, GREY, "middle", "bold")
    s += text(ox - 12, Fy + 4, "Φ", 13, GREY, "end", "bold")
    save("fig-8-3-2-half-formula.svg", s)


def fig31_i_squared():
    W, H = 700, 420
    s = header(W, H)
    s += text(W / 2, 34, "Енергія росте з квадратом струму: W ∝ I²", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "удвічі більший струм — учетверо більше енергії", 12, GREY, "middle", style="italic")
    ox, oy = 120, 360
    s += arrow(ox, oy, ox, 80, INK, 2)
    s += arrow(ox, oy, 640, oy, INK, 2)
    s += text(648, oy + 4, "I", 15, COPP, "start", "bold")
    s += text(ox - 8, 74, "W", 15, INK, "middle", "bold")
    Imax, px_per, Wfull = 3.0, 150, 260
    pts = []
    for j in range(0, 91):
        v = Imax * j / 90
        x = ox + v * px_per
        y = oy - (v * v / (Imax * Imax)) * Wfull
        pts.append(f"{x:.1f},{y:.1f}")
    s += f'<path d="M {" L ".join(pts)}" fill="none" stroke="{GREEN}" stroke-width="2.8"/>\n'
    for v, lab in [(1, "I → W"), (2, "2I → 4W"), (3, "3I → 9W")]:
        x = ox + v * px_per
        y = oy - (v * v / 9.0) * Wfull
        s += line(x, oy, x, y, GREY, 1.3, dash="4,4")
        s += line(ox, y, x, y, GREY, 1.3, dash="4,4")
        s += circle(x, y, 4.5, GREEN, GREEN, 0)
        s += text(x + 6, y - 8, lab, 12.5, INK, "start", "bold")
    save("fig-8-3-3-i-squared.svg", s)


def fig31_field_storage():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 34, "Енергія в магнітному полі; його спад віддає її", 18, INK, "middle", "bold")
    # ліворуч — струм тече, поле є
    coil, (xl, xr) = coil_h(200, 190, 150, 6, 42)
    s += coil
    for dy in (-22, 0, 22):
        s += arrow(xl + 12, 190 + dy, xr - 12, 190 + dy, GREEN, 2)
    s += arrow(xl - 50, 190, xl - 8, 190, COPP, 3)
    s += text(200, 270, "струм тече → поле напнуте", 12, GREEN, "middle", "bold")
    s += text(200, 288, "енергія ½·L·I² у полі", 11, INK, "middle", style="italic")
    # стрілка
    s += arrow(360, 190, 440, 190, INK, 2.6)
    s += text(400, 178, "обрив", 11.5, RED, "middle", "bold")
    # праворуч — поле спадає, іскра
    coil2, (xl2, xr2) = coil_h(580, 190, 150, 6, 42)
    s += coil2
    s += text(580, 270, "струм обірвано → поле спадає", 12, GREY, "middle", "bold")
    # іскра на розриві
    bx = xr2 + 16
    s += line(bx, 190, bx + 18, 172, RED, 2.4)
    s += line(bx + 18, 172, bx + 6, 184, RED, 2.4)
    s += line(bx + 6, 184, bx + 26, 162, RED, 2.4)
    s += text(bx + 40, 178, "іскра!", 12, RED, "start", "bold")
    s += text(580, 288, "енергія виходить назовні", 11, INK, "middle", style="italic")
    save("fig-8-3-4-field-storage.svg", s)


def fig31_kinetic():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Конденсатор — потенціальна, котушка — кінетична", 18, INK, "middle", "bold")
    # пружина / конденсатор
    s += rect(40, 76, 330, 220, "none", FAINT, 1.6, 12)
    s += text(205, 100, "конденсатор = пружина", 13, INK, "middle", "bold")
    cs, lx, rx = cap_sym(130, 170, 22, 12)
    s += line(95, 170, lx, 170, INK, 2)
    s += cs
    sp = [(rx, 170)]
    for i in range(8):
        sp.append((rx + 10 + i * 14, 170 + (12 if i % 2 == 0 else -12)))
    sp.append((rx + 122, 170))
    s += _poly(sp, GREEN, 2)
    s += text(205, 240, "потенціальна:  ½·k·x²", 13, INK, "middle", "bold")
    s += text(205, 262, "½·C·V²", 14, RED, "middle", "bold")
    # маховик / котушка
    s += rect(390, 76, 330, 220, "none", FAINT, 1.6, 12)
    s += text(555, 100, "котушка = маховик", 13, INK, "middle", "bold")
    coil, (xl, xr) = coil_h(490, 170, 80, 5, 28)
    s += line(455, 170, xl, 170, INK, 2)
    s += coil
    s += circle(615, 170, 32, "#eceae2", INK, 2.4)
    s += circle(615, 170, 6, INK, INK, 0)
    s += arrow(615 + 26, 170 - 14, 615 + 28, 170 + 14, GREY, 2)
    s += text(555, 240, "кінетична:  ½·m·v²", 13, INK, "middle", "bold")
    s += text(555, 262, "½·L·I²", 14, BLUE, "middle", "bold")
    s += text(W / 2, H - 16, "L грає роль маси, струм — роль швидкості.", 12, GREEN, "middle", "bold")
    save("fig-8-3-5-kinetic.svg", s)


def fig31_store_vs_dissipate():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Котушка повертає енергію, резистор спалює", 18, INK, "middle", "bold")

    def box(x, y, w, h, lab, col, fill):
        return rect(x, y, w, h, fill, col, 1.8, 8) + text(x + w / 2, y + h / 2 + 5, lab, 14, INK, "middle", "bold")

    s += text(70, 108, "РЕЗИСТОР", 14, INK, "start", "bold")
    s += box(70, 122, 90, 54, "джерело", GREY, "#fbfbfb")
    s += arrow(160, 149, 240, 149, INK, 2.4)
    s += box(240, 122, 90, 54, "R", RED, "#fdeded")
    for k in range(3):
        xx = 360 + k * 24
        s += f'<path d="M {xx},166 q 5,-11 10,0 q 5,11 10,0" fill="none" stroke="{RED}" stroke-width="1.8"/>\n'
    s += text(420, 134, "100% → тепло", 12.5, RED, "start", "bold")
    s += text(420, 152, "необоротно", 11, GREY, "start", style="italic")

    s += text(70, 250, "КОТУШКА", 14, INK, "start", "bold")
    s += box(70, 264, 90, 54, "джерело", GREY, "#fbfbfb")
    s += arrow(160, 291, 240, 291, INK, 2.4)
    s += box(240, 264, 120, 54, "L (B-поле)", GREEN, "#eef6ef")
    s += arrow(240, 308, 162, 308, GREEN, 2.4)
    s += text(200, 330, "повертається", 11, GREEN, "middle", "bold")
    s += text(380, 284, "запас у полі →", 12.5, GREEN, "start", "bold")
    s += text(380, 302, "віддається назад (оборотно)", 11, GREY, "start", style="italic")
    save("fig-8-3-6-store-vs-dissipate.svg", s)


def fig31_release():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Накопичити поволі — віддати ривком", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама енергія за мікросекунди — величезна потужність (іскра, сплеск)",
              12, GREY, "middle", style="italic")
    ox, oy = 90, 320
    s += arrow(ox, oy, ox, 90, INK, 2)
    s += arrow(ox, oy, 700, oy, INK, 2)
    s += text(706, oy + 4, "час", 13, INK, "start", "bold")
    s += text(ox - 6, 84, "потужність", 12.5, INK, "middle", "bold")
    s += rect(130, oy - 44, 250, 44, "#e7f0e0", GREEN, 1.8)
    s += text(255, oy - 54, "накопичення: довго, мала потужність", 11, GREEN, "middle", "bold")
    s += rect(470, oy - 220, 24, 220, "#fdeded", RED, 1.8)
    s += text(560, oy - 150, "обрив: мить,", 12, RED, "middle", "bold")
    s += text(560, oy - 132, "величезна потужність", 12, RED, "middle", "bold")
    s += text(482, oy - 234, "(та сама площа)", 10.5, GREY, "middle", style="italic")
    s += rect(60, H - 38, W - 120, 26, "#fdeded", RED, 1.4, 8)
    s += text(W / 2, H - 20, "Звідси іскра на вимикачі й сплеск, що пробиває ключ — приборкання в §8.5.",
              11.5, INK, "middle", "bold")
    save("fig-8-3-7-release.svg", s)


# ── §8.4 будівельники ────────────────────────────────────────────────────────
def exp_path(ox, oy, w, h, kind, ncyc=5):
    pts = []
    for j in range(0, 101):
        t = ncyc * j / 100.0
        yf = (1 - math.exp(-t)) if kind == "charge" else math.exp(-t)
        x = ox + (t / ncyc) * w
        y = oy - yf * h
        pts.append(f"{x:.1f},{y:.1f}")
    return "M " + " L ".join(pts)


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


def resistor_h(x1, x2, y, label="R", col=INK):
    n = 6
    seg = (x2 - x1) / n
    pts = [(x1, y)]
    for i in range(n):
        pts.append((x1 + seg * (i + 0.5), y - 9 if i % 2 == 0 else y + 9))
    pts.append((x2, y))
    s = _poly(pts, col, 2)
    s += text((x1 + x2) / 2, y - 16, label, 14, INK, "middle", "bold")
    return s


def ind_sym(x1, x2, y, label="L", col=COPP):
    n = 4
    seg = (x2 - x1) / n
    s = ""
    for i in range(n):
        xa, xb = x1 + seg * i, x1 + seg * (i + 1)
        s += f'<path d="M {xa:.1f},{y:.1f} A {seg/2:.1f} {seg/2:.1f} 0 0 1 {xb:.1f},{y:.1f}" fill="none" stroke="{col}" stroke-width="2.2"/>\n'
    s += text((x1 + x2) / 2, y - 13, label, 13, INK, "middle", "bold")
    return s


def diode_v(cx, y1, y2, col=INK):
    mid = (y1 + y2) / 2
    s = line(cx, y1, cx, mid - 8, col, 2)
    s += f'<path d="M {cx-8},{mid-8:.1f} L {cx+8},{mid-8:.1f} L {cx},{mid+4:.1f} Z" fill="none" stroke="{col}" stroke-width="2"/>\n'
    s += line(cx - 8, mid + 4, cx + 8, mid + 4, col, 2)
    s += line(cx, mid + 4, cx, y2, col, 2)
    return s


# ── Рис. 8.4.1 — RL-коло ─────────────────────────────────────────────────────
def fig41_rl_circuit():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "RL-коло: резистор і котушка послідовно", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "R задає кінцевий струм (V/R), пара L і R — як швидко він установиться",
              12, GREY, "middle", style="italic")
    bat, bt, bb = battery(110, 230)
    s += bat
    s += text(86, 230, "V", 13, INK, "end", "bold")
    topY, botY = 120, 330
    s += line(bt[0], bt[1], 110, topY, INK, 2.2)
    s += switch(150, topY, 192, closed=True)
    s += line(192, topY, 230, topY, INK, 2.2)
    s += resistor_h(230, 330, topY, "R")
    s += line(330, topY, 380, topY, INK, 2.2)
    s += ind_sym(380, 500, topY, "L")
    s += line(500, topY, 600, topY, INK, 2.2)
    s += line(600, topY, 600, botY, INK, 2.2)
    s += line(bb[0], bb[1], 110, botY, INK, 2.2)
    s += line(110, botY, 600, botY, INK, 2.2)
    # струм
    s += arrow(420, topY - 22, 470, topY - 22, COPP, 2.4)
    s += text(445, topY - 32, "i", 13, COPP, "middle", "bold")
    # шлях для спаду (freewheel діод, пунктир)
    s += line(355, topY, 355, topY, INK, 0)
    s += f'<g opacity="0.7">'
    s += diode_v(540, topY + 10, botY - 10, GREEN)
    s += line(540, topY, 540, topY + 10, GREEN, 1.6)
    s += "</g>"
    s += text(560, 230, "шлях для струму", 10.5, GREEN, "start", "bold")
    s += text(560, 246, "при розмиканні (§8.5)", 10, GREY, "start", style="italic")
    save("fig-8-4-1-rl-circuit.svg", s)


# ── Рис. 8.4.2 — наростання струму ───────────────────────────────────────────
def fig41_current_rise():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 34, "Увімкнення: струм наростає за експонентою до V/R", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 350, 540, 250
    s += f'<line x1="{ox}" y1="{oy-h}" x2="{ox+w}" y2="{oy-h}" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="6,5"/>\n'
    s += text(ox + w, oy - h - 8, "I = V/R", 12.5, GREY, "end", "bold")
    for k in range(1, 6):
        x = ox + (k / 5) * w
        s += line(x, oy, x, oy + 6, INK, 1.4)
        s += text(x, oy + 22, f"{k}τ", 12, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "час t", "струм i")
    s += f'<path d="{exp_path(ox, oy, w, h, "charge")}" fill="none" stroke="{COPP}" stroke-width="2.8"/>\n'
    for k, lab in [(1, "63%"), (5, "99%")]:
        yf = 1 - math.exp(-k)
        x, y = ox + (k / 5) * w, oy - yf * h
        s += line(ox, y, x, y, GREY, 1.2, dash="4,4")
        s += circle(x, y, 4.5, COPP, COPP, 0)
        s += text(x - 8, y - 8, lab, 12.5, "#8a4a18", "end", "bold")
    s += text(W / 2, H - 14, "τ = L/R. Дзеркало напруги на конденсаторі (§7.4).", 12, GREY, "middle", style="italic")
    save("fig-8-4-2-current-rise.svg", s)


# ── Рис. 8.4.3 — спад напруги на котушці ─────────────────────────────────────
def fig41_voltage_decay():
    W, H = 720, 400
    s = header(W, H)
    s += text(W / 2, 34, "Напруга на котушці спадає від V до нуля", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 330, 540, 230
    for k in range(1, 6):
        x = ox + (k / 5) * w
        s += line(x, oy, x, oy + 6, INK, 1.4)
        s += text(x, oy + 22, f"{k}τ", 12, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "час t", "напруга на L")
    s += f'<path d="{exp_path(ox, oy, w, h, "discharge")}" fill="none" stroke="{BLUE}" stroke-width="2.8"/>\n'
    s += circle(ox, oy - h, 4.5, BLUE, BLUE, 0)
    s += text(ox + 8, oy - h - 6, "V (на старті)", 12.5, BLUE, "start", "bold")
    s += text(ox + w * 0.5, oy - h * 0.2, "струм установився → напруга 0", 11.5, GREY, "middle", style="italic")
    save("fig-8-4-3-voltage-decay.svg", s)


# ── Рис. 8.4.4 — спад струму ─────────────────────────────────────────────────
def fig41_current_decay():
    W, H = 720, 400
    s = header(W, H)
    s += text(W / 2, 34, "Вимкнення (із шляхом для струму): струм спадає за експонентою", 16.5, INK, "middle", "bold")
    ox, oy, w, h = 110, 330, 540, 230
    for k in range(1, 6):
        x = ox + (k / 5) * w
        s += line(x, oy, x, oy + 6, INK, 1.4)
        s += text(x, oy + 22, f"{k}τ", 12, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "час t", "струм i")
    s += f'<path d="{exp_path(ox, oy, w, h, "discharge")}" fill="none" stroke="{COPP}" stroke-width="2.8"/>\n'
    for k, lab in [(1, "37%"), (5, "<1%")]:
        yf = math.exp(-k)
        x, y = ox + (k / 5) * w, oy - yf * h
        s += line(ox, y, x, y, GREY, 1.2, dash="4,4")
        s += circle(x, y, 4.5, COPP, COPP, 0)
        s += text(x + 8, y - 8, lab, 12.5, "#8a4a18", "start", "bold")
    s += text(W / 2, H - 14, "Енергія поля ½·L·I² іде в тепло резистора. Але БЕЗ шляху — див. §8.5!",
              12, GREY, "middle", style="italic")
    save("fig-8-4-4-current-decay.svg", s)


# ── Рис. 8.4.5 — стала часу τ = L/R ──────────────────────────────────────────
def fig41_tau_meaning():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 34, "τ = L/R: більша L — повільніше, більший R — ШВИДШЕ", 17.5, INK, "middle", "bold")
    ox, oy, w, h = 110, 350, 540, 250
    s += f'<line x1="{ox}" y1="{oy-h}" x2="{ox+w}" y2="{oy-h}" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="6,5"/>\n'
    s += text(ox + w, oy - h - 8, "V/R", 12, GREY, "end", "bold")
    s += _axes(ox, oy, w, h, "час t", "струм i")
    tmax = 5.0
    curves = [(0.5, COPP, "велике R / мала L — швидко"), (1.0, "#9c7b46", "середнє"),
              (2.2, BLUE, "мале R / велика L — повільно")]
    for tau, col, lab in curves:
        pts = []
        for j in range(0, 101):
            t = tmax * j / 100
            yf = 1 - math.exp(-t / tau)
            pts.append((ox + (t / tmax) * w, oy - yf * h))
        s += _poly(pts, col, 2.6)
    s += text(ox + 130, oy - h + 26, "швидко (мала τ)", 12, COPP, "start", "bold")
    s += text(ox + 320, oy - 80, "повільно (велика τ)", 12, BLUE, "start", "bold")
    s += text(W / 2, H - 12, "τ = L/R: опір у знаменнику, тож більший R пришвидшує (дзеркало RC).",
              11.5, GREY, "middle", style="italic")
    save("fig-8-4-5-tau-meaning.svg", s)


# ── Рис. 8.4.6 — струм не стрибає ────────────────────────────────────────────
def fig41_no_jump():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Що не може стрибнути: напруга на C, струм у L", 18, INK, "middle", "bold")
    # конденсатор: напруга плавна
    s += rect(40, 76, 330, 230, "none", FAINT, 1.6, 12)
    s += text(205, 100, "конденсатор: V не стрибає", 12.5, INK, "middle", "bold")
    ox, oy, w, h = 70, 270, 250, 130
    s += _axes(ox, oy, w, h, "t", "V")
    # вхід-стрибок (сірий) і плавна напруга
    s += _poly([(ox, oy), (ox + 60, oy), (ox + 60, oy - h * 0.9), (ox + w, oy - h * 0.9)], GREY, 1.6, "5,4")
    s += f'<path d="{exp_path(ox + 60, oy, w - 60, h * 0.9, "charge", 4)}" fill="none" stroke="{RED}" stroke-width="2.6"/>\n'
    s += text(ox + 150, oy - h - 2, "плавно (i = C·dV/dt)", 10.5, RED, "middle", "bold")
    # котушка: струм плавний
    s += rect(390, 76, 330, 230, "none", FAINT, 1.6, 12)
    s += text(555, 100, "котушка: i не стрибає", 12.5, INK, "middle", "bold")
    ox2 = 420
    s += _axes(ox2, oy, w, h, "t", "i")
    s += _poly([(ox2, oy), (ox2 + 60, oy), (ox2 + 60, oy - h * 0.9), (ox2 + w, oy - h * 0.9)], GREY, 1.6, "5,4")
    s += f'<path d="{exp_path(ox2 + 60, oy, w - 60, h * 0.9, "charge", 4)}" fill="none" stroke="{COPP}" stroke-width="2.6"/>\n'
    s += text(ox2 + 150, oy - h - 2, "плавно (V = L·di/dt)", 10.5, COPP, "middle", "bold")
    s += text(W / 2, H - 14, "Сірим — бажаний миттєвий стрибок; кольором — реальна плавна відповідь.",
              11, GREY, "middle", style="italic")
    save("fig-8-4-6-no-jump.svg", s)


# ── Рис. 8.4.7 — правило 5τ ──────────────────────────────────────────────────
def fig41_5tau_table():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 34, "Правило 5·τ: струм «практично встановився»", 19, INK, "middle", "bold")
    rows = [(1, 63), (2, 86), (3, 95), (4, 98), (5, 99)]
    x0, ytop, barmax = 150, 84, 400
    for i, (k, pct) in enumerate(rows):
        y = ytop + i * 44
        s += text(x0 - 14, y + 16, f"{k}·τ", 13, INK, "end", "bold")
        s += rect(x0, y, barmax, 24, "#eef2f6", "#c9d3dc", 1, 3)
        col = GREEN if k >= 5 else COPP
        s += rect(x0, y, barmax * pct / 100, 24, "#e1f0e1" if k >= 5 else "#f6e7d8", col, 1.6, 3)
        s += text(x0 + barmax * pct / 100 + 10, y + 17, f"{pct}%", 13, col, "start", "bold")
    s += line(x0 + barmax, ytop - 6, x0 + barmax, ytop + len(rows) * 44 - 6, GREY, 1.3, dash="4,4")
    s += text(x0 + barmax, ytop - 12, "I = V/R (мета)", 11, GREY, "middle")
    s += text(W / 2, H - 16, "Та сама крива, що й у RC (§7.4): за кожну τ — 63% залишку.", 11.5, GREY, "middle", style="italic")
    save("fig-8-4-7-5tau-table.svg", s)


# ── Рис. 8.4.8 — RC проти RL ─────────────────────────────────────────────────
def fig41_rl_vs_rc():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Дзеркало: RC ↔ RL", 20, INK, "middle", "bold")
    # RC
    s += text(190, 86, "RC: наростає напруга", 13, RED, "middle", "bold")
    ox, oy, w, h = 80, 270, 220, 150
    s += _axes(ox, oy, w, h, "t", "V")
    s += f'<path d="{exp_path(ox, oy, w, h, "charge")}" fill="none" stroke="{RED}" stroke-width="2.6"/>\n'
    s += text(190, 300, "τ = R·C · більший R → повільніше", 10.5, GREY, "middle", style="italic")
    # RL
    s += text(570, 86, "RL: наростає струм", 13, COPP, "middle", "bold")
    ox2 = 460
    s += _axes(ox2, oy, w, h, "t", "i")
    s += f'<path d="{exp_path(ox2, oy, w, h, "charge")}" fill="none" stroke="{COPP}" stroke-width="2.6"/>\n'
    s += text(570, 300, "τ = L/R · більший R → швидше", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "Та сама експонента; напруга та струм помінялися ролями, а R грає протилежну роль.",
              11.5, INK, "middle", "bold")
    save("fig-8-4-8-rl-vs-rc.svg", s)


# ── §8.5 фігури ──────────────────────────────────────────────────────────────
def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


def _ind_load(cx, top, bot, label="L"):
    """Вертикальне індуктивне навантаження (котушка) між top і bot."""
    s = ""
    n = 4
    seg = (bot - top) / n
    for i in range(n):
        ya, yb = top + seg * i, top + seg * (i + 1)
        s += f'<path d="M {cx:.1f},{ya:.1f} A {seg/2:.1f} {seg/2:.1f} 0 0 1 {cx:.1f},{yb:.1f}" fill="none" stroke="{COPP}" stroke-width="2.2"/>\n'
    s += text(cx + 16, (top + bot) / 2, label, 13, INK, "start", "bold")
    return s


def fig51_spike_origin():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Розмикання котушки → миттєве di/dt → сплеск напруги", 18, INK, "middle", "bold")
    # коло ліворуч
    bat, bt, bb = battery(100, 220)
    s += bat
    s += text(76, 220, "V", 12, INK, "end", "bold")
    s += line(bt[0], bt[1], 100, 120, INK, 2.2)
    s += switch(150, 120, 196, closed=False)
    s += text(173, 104, "ключ", 11, INK, "middle")
    s += line(196, 120, 250, 120, INK, 2.2)
    s += _ind_load(250, 130, 290, "L")
    s += line(250, 290, 250, 300, INK, 2.2)
    s += line(bb[0], bb[1], 100, 300, INK, 2.2)
    s += line(100, 300, 250, 300, INK, 2.2)
    # іскра на ключі
    s += line(173, 120, 184, 108, RED, 2)
    s += line(184, 108, 178, 114, RED, 2)
    s += line(178, 114, 190, 102, RED, 2)
    s += text(173, 150, "розмикається", 10.5, RED, "middle", "bold")
    # осцилограма праворуч
    s += _frame(400, 90, 390, 240, "напруга на ключі")
    ox, oy, w, h = 430, 300, 330, 200
    s += _axes(ox, oy, w, h, "t", "V")
    s += line(ox, oy - h * 0.12, ox + 0.45 * w, oy - h * 0.12, GREY, 2)
    s += text(ox + 0.2 * w, oy - h * 0.12 - 6, "живлення", 10, GREY, "middle")
    peak = oy - h * 0.92
    s += _poly([(ox + 0.45 * w, oy - h * 0.12), (ox + 0.45 * w, peak),
                (ox + 0.55 * w, oy - h * 0.3), (ox + 0.62 * w, oy - h * 0.18),
                (ox + 0.7 * w, oy - h * 0.13), (ox + w, oy - h * 0.12)], RED, 2.6)
    s += text(ox + 0.47 * w, peak - 6, "СПЛЕСК (сотні В)", 11, RED, "start", "bold")
    save("fig-8-5-1-spike-origin.svg", s)


def fig51_energy_nowhere():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Енергії ½·L·I² нема куди дітися — вона рветься іскрою", 17.5, INK, "middle", "bold")
    cx = 300
    s += _ind_load(cx, 110, 230, "")
    s += text(cx - 14, 170, "½·L·I²", 14, COPP, "end", "bold")
    s += line(cx, 230, cx, 270, INK, 2.2)
    s += line(cx, 110, cx, 80, INK, 2.2)
    s += line(cx, 80, cx + 120, 80, INK, 2.2)
    s += line(cx + 120, 80, cx + 120, 150, INK, 2.2)
    # розрив ключа з дугою
    s += line(cx + 120, 200, cx + 120, 270, INK, 2.2)
    s += line(cx, 270, cx + 120, 270, INK, 2.2)
    s += circle(cx + 120, 158, 3, INK, INK, 0)
    s += circle(cx + 120, 192, 3, INK, INK, 0)
    for dy in (165, 175, 185):
        s += line(cx + 113, dy, cx + 127, dy + 3, RED, 1.8)
    s += text(cx + 140, 175, "дуга на ключі", 12, RED, "start", "bold")
    s += text(cx + 140, 192, "(вихід для енергії)", 10.5, GREY, "start", style="italic")
    s += rect(60, H - 44, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Сплеск напруги — це котушка, що шукає, куди скинути запас поля.", 12, INK, "middle", "bold")
    save("fig-8-5-2-energy-nowhere.svg", s)


def fig51_danger():
    W, H = 740, 320
    s = header(W, H)
    s += text(W / 2, 34, "Що вбиває сплеск: контакти й транзистор-ключ", 18, INK, "middle", "bold")
    # контакти
    s += _frame(40, 80, 320, 210, "механічні контакти")
    s += line(120, 180, 180, 180, INK, 3)
    s += line(220, 180, 280, 180, INK, 3)
    for dy in (172, 180, 188):
        s += line(184, dy, 216, dy + 2, RED, 2)
    s += text(200, 150, "іскра", 12, RED, "middle", "bold")
    s += text(200, 250, "випалюються від кожного розмикання", 10.5, GREY, "middle", style="italic")
    # транзистор
    s += _frame(380, 80, 320, 210, "транзистор-ключ")
    s += rect(490, 150, 100, 70, "#eef2f6", INK, 1.8, 6)
    s += text(540, 192, "ключ", 13, INK, "middle", "bold")
    s += line(525, 130, 540, 150, RED, 2.4)
    s += line(540, 150, 533, 160, RED, 2.4)
    s += line(533, 160, 552, 180, RED, 2.4)
    s += text(620, 150, "пробій", 12, RED, "start", "bold")
    s += text(540, 250, "сплеск перевищує допустиму напругу", 10.5, GREY, "middle", style="italic")
    save("fig-8-5-3-danger.svg", s)


def fig51_flyback_diode():
    W, H = 780, 340
    s = header(W, H)
    s += text(W / 2, 34, "Зворотний (flyback) діод дає струмові шлях", 18, INK, "middle", "bold")

    def circ(x0, title, closed, diode_on):
        out = _frame(x0, 76, 340, 240, title)
        cx = x0 + 90
        # котушка
        out += _ind_load(cx, 120, 220, "L")
        out += line(cx, 220, cx, 270, INK, 2)
        out += line(cx, 120, cx, 100, INK, 2)
        out += line(cx, 100, cx + 150, 100, INK, 2)
        # ключ праворуч (вертикальний перемикач)
        out += line(cx + 150, 100, cx + 150, 120, INK, 2)
        out += circle(cx + 150, 120, 3, INK, INK, 0)
        if closed:
            out += line(cx + 150, 120, cx + 150, 200, INK, 2.4)
        else:
            out += line(cx + 150, 120, cx + 164, 150, INK, 2.4)
        out += circle(cx + 150, 200, 3, INK, INK, 0)
        out += line(cx + 150, 200, cx + 150, 270, INK, 2)
        out += line(cx, 270, cx + 150, 270, INK, 2)
        out += text(cx + 168, 160, "ключ", 10, INK, "start")
        # діод паралельно котушці (праворуч від неї)
        dcol = GREEN if diode_on else GREY
        out += line(cx + 70, 120, cx + 70, 130, dcol, 2)
        out += diode_v(cx + 70, 130, 210, dcol)
        out += line(cx + 70, 210, cx + 70, 220, dcol, 2)
        out += line(cx, 120, cx + 70, 120, dcol, 2)
        out += line(cx, 220, cx + 70, 220, dcol, 2)
        if diode_on:
            out += text(cx + 88, 170, "проводить", 10.5, GREEN, "start", "bold")
            out += arrow(cx + 70, 150, cx + 70, 190, GREEN, 2)
        else:
            out += text(cx + 88, 170, "закритий", 10.5, GREY, "start", style="italic")
        return out

    s += circ(30, "норма: ключ замкнений", True, False)
    s += circ(410, "розмикання: діод проводить", False, True)
    save("fig-8-5-4-flyback-diode.svg", s)


def fig51_with_diode_decay():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "З діодом: напруга обмежена, струм згасає плавно", 18, INK, "middle", "bold")
    ox, oy, w, h = 100, 300, 560, 220
    s += _axes(ox, oy, w, h, "t", "V на ключі")
    s += line(ox, oy - h * 0.18, ox + 0.4 * w, oy - h * 0.18, GREY, 1.6)
    # без діода — сплеск
    s += _poly([(ox + 0.4 * w, oy - h * 0.18), (ox + 0.4 * w, oy - h * 0.95),
                (ox + 0.5 * w, oy - h * 0.3), (ox + 0.58 * w, oy - h * 0.2),
                (ox + 0.66 * w, oy - h * 0.18), (ox + w, oy - h * 0.18)], RED, 2.6)
    s += text(ox + 0.42 * w, oy - h * 0.95 - 4, "без діода: сплеск", 11, RED, "start", "bold")
    # з діодом — clamp
    s += _poly([(ox, oy - h * 0.18), (ox + 0.4 * w, oy - h * 0.18),
                (ox + 0.4 * w, oy - h * 0.26), (ox + 0.85 * w, oy - h * 0.24),
                (ox + 0.95 * w, oy - h * 0.18), (ox + w, oy - h * 0.18)], GREEN, 2.6)
    s += text(ox + 0.6 * w, oy - h * 0.34, "з діодом: ≈ живлення + 0.7 В", 11, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Струм при цьому плавно згасає за τ = L/R замість миттєвого обриву.",
              11.5, GREY, "middle", style="italic")
    save("fig-8-5-5-with-diode-decay.svg", s)


def fig51_tamers_tradeoff():
    W, H = 780, 360
    s = header(W, H)
    s += text(W / 2, 34, "Приборкувачі сплеску й компроміс", 19, INK, "middle", "bold")
    items = [("діод", "≈0.7 В", "повільно", GREEN),
             ("стабілітрон / TVS", "30–60 В", "швидко", BLUE),
             ("RC-снабер", "поглинає", "+ гасить дзвін", "#9c7b46")]
    for i, (name, clamp, speed, col) in enumerate(items):
        x = 50 + i * 240
        s += _frame(x, 76, 210, 160, name)
        cx = x + 60
        s += _ind_load(cx, 110, 190, "")
        s += line(cx, 110, cx, 100, INK, 2)
        s += line(cx, 190, cx, 200, INK, 2)
        if i == 0:
            s += diode_v(cx + 70, 110, 190, GREEN)
            s += line(cx, 110, cx + 70, 110, GREEN, 2)
            s += line(cx, 190, cx + 70, 190, GREEN, 2)
        elif i == 1:
            s += diode_v(cx + 70, 110, 190, BLUE)
            s += line(cx + 64, 116, cx + 76, 116, BLUE, 2)  # zener bar hint
            s += line(cx, 110, cx + 70, 110, BLUE, 2)
            s += line(cx, 190, cx + 70, 190, BLUE, 2)
        else:
            csym, lx, rx = cap_sym(cx + 70, 135, 12, 7)
            s += csym
            s += resistor_h(cx + 64, cx + 76, 165, "", "#9c7b46") if False else ""
            s += line(cx, 110, cx + 70, 110, "#9c7b46", 2)
            s += line(cx + 70, 110, cx + 70, 123, "#9c7b46", 2)
            s += line(cx + 70, 147, cx + 70, 190, "#9c7b46", 2)
            s += line(cx, 190, cx + 70, 190, "#9c7b46", 2)
        s += text(x + 105, 250, "напруга: " + clamp, 11, INK, "middle", "bold")
        s += text(x + 105, 268, "згасання: " + speed, 11, col, "middle", "bold")
    s += text(W / 2, H - 16, "Компроміс: що нижча дозволена напруга, то повільніше згасає струм.",
              12, GREY, "middle", style="italic")
    save("fig-8-5-6-tamers-tradeoff.svg", s)


def fig51_harnessed():
    W, H = 780, 320
    s = header(W, H)
    s += text(W / 2, 34, "Корисне «брикання»: висока напруга з низьковольтного джерела", 16.5, INK, "middle", "bold")
    # котушка запалювання
    s += _frame(40, 76, 330, 210, "котушка запалювання")
    s += _ind_load(160, 120, 220, "L")
    s += text(120, 110, "12 В", 10.5, INK, "middle")
    s += line(220, 150, 280, 150, RED, 2)
    for dy in (143, 150, 157):
        s += line(284, dy, 300, dy + 2, RED, 2)
    s += text(300, 130, "десятки кВ", 11, RED, "start", "bold")
    s += text(205, 268, "накопичив струм → різко обірвав → іскра", 10, GREY, "middle", style="italic")
    # boost
    s += _frame(390, 76, 350, 210, "підвищувальний перетворювач")
    s += _ind_load(450, 120, 190, "L")
    s += line(450, 120, 450, 110, INK, 2)
    s += line(450, 110, 540, 110, INK, 2)
    s += diode_v(540, 110, 110, INK) if False else ""
    # діод горизонтально: намалюємо трикутник
    s += f'<path d="M 540,104 L 540,116 L 556,110 Z" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += line(556, 104, 556, 116, INK, 2)
    s += line(556, 110, 600, 110, INK, 2)
    csym, lx, rx = cap_sym(600, 150, 22, 11)
    s += line(600, 110, 600, 128, INK, 2)
    s += csym
    s += line(600, 172, 600, 200, INK, 2)
    s += text(640, 150, "вища U", 11, RED, "start", "bold")
    s += text(450, 210, "ключ", 9.5, INK, "middle")
    s += line(450, 190, 450, 210, INK, 1.6)
    s += text(565, 268, "сплески накачують конденсатор", 10, GREY, "middle", style="italic")
    save("fig-8-5-7-harnessed.svg", s)


# ── §8.6 фігури ──────────────────────────────────────────────────────────────
def ac_source(cx, cy, r=20):
    s = circle(cx, cy, r, "#fff", INK, 2)
    pts = []
    for i in range(0, 33):
        t = i / 32
        x = cx - r * 0.72 + 1.44 * r * t
        y = cy - 0.5 * r * math.sin(2 * math.pi * t)
        pts.append((x, y))
    s += _poly(pts, INK, 1.8)
    return s


def xfmr(cx, cy, w=150, h=130, p_turns=4, s_turns=4):
    """Трансформатор: осердя-рамка + первинна (ліворуч) і вторинна (праворуч) обмотки.
    Повертає (svg, dict з точками виводів)."""
    L, R, T, B = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    out = rect(L, T, w, h, IRON, "#6f7479", 1.5)
    out += rect(L + 26, T + 20, w - 52, h - 40, "#ffffff", "#6f7479", 1.5)
    pcx, scx = L + 13, R - 13

    def coil(xc, n):
        o = ""
        span = h - 50
        for i in range(n):
            yy = cy - span / 2 + span * i / max(1, n - 1)
            o += f'<ellipse cx="{xc:.1f}" cy="{yy:.1f}" rx="13" ry="9" fill="none" stroke="{COPP}" stroke-width="2"/>\n'
        return o, (xc, cy - span / 2), (xc, cy + span / 2)

    pc, pt, pb = coil(pcx, p_turns)
    sc, st, sb = coil(scx, s_turns)
    out += pc + sc
    # потік в осерді
    out += text(cx, cy + 4, "Φ", 15, GREEN, "middle", "bold")
    out += f'<path d="M {cx-10:.1f},{T+11:.1f} A 26 14 0 0 1 {cx+10:.1f},{T+11:.1f}" fill="none" stroke="{GREEN}" stroke-width="1.6" marker-end="url(#aGreen)"/>\n'
    # виводи: первинна ліворуч, вторинна праворуч
    out += line(pcx, pt[1], pcx - 30, pt[1], INK, 2)
    out += line(pcx, pb[1], pcx - 30, pb[1], INK, 2)
    out += line(scx, st[1], scx + 30, st[1], INK, 2)
    out += line(scx, sb[1], scx + 30, sb[1], INK, 2)
    return out, dict(L=L, R=R, T=T, B=B,
                     p_top=(pcx - 30, pt[1]), p_bot=(pcx - 30, pb[1]),
                     s_top=(scx + 30, st[1]), s_bot=(scx + 30, sb[1]))


# ── Рис. 8.6.1 — взаємоіндукція ──────────────────────────────────────────────
def fig61_mutual():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Взаємоіндукція: змінне поле однієї котушки наводить напругу в іншій", 16.5, INK, "middle", "bold")
    # первинна
    c1, (xl1, xr1) = coil_h(220, 180, 90, 5, 40)
    s += c1
    src = ac_source(110, 180)
    s += src
    s += line(110, 160, 110, 130, INK, 2)
    s += line(110, 130, xl1, 130, INK, 2)
    s += line(xl1, 130, xl1, 150, INK, 2)
    s += line(110, 200, 110, 230, INK, 2)
    s += line(110, 230, xl1, 230, INK, 2)
    s += line(xl1, 230, xl1, 210, INK, 2)
    s += text(220, 250, "первинна (~ змінний струм)", 11, COPP, "middle", "bold")
    # поле між котушками
    for dy in (-20, 0, 20):
        s += arrow(xr1 + 4, 180 + dy, 470, 180 + dy, GREEN, 1.8)
    s += text(420, 150, "змінне поле", 11, GREEN, "middle", "bold")
    # вторинна + гальванометр
    c2, (xl2, xr2) = coil_h(540, 180, 90, 5, 40)
    s += c2
    s += line(xr2, 158, xr2 + 30, 158, INK, 2)
    s += line(xr2, 202, xr2 + 30, 202, INK, 2)
    s += line(xr2 + 30, 158, xr2 + 30, 162, INK, 2)
    s += line(xr2 + 30, 202, xr2 + 30, 198, INK, 2)
    s += galvo(xr2 + 30, 180, 22, 20)
    s += text(540, 250, "вторинна (наведена напруга)", 11, COPP, "middle", "bold")
    s += rect(60, H - 40, W - 120, 26, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 21, "Котушки не з'єднані дротом — енергія переходить через поле. Працює лише на ЗМІНІ.",
              11.5, INK, "middle", "bold")
    save("fig-8-6-1-mutual.svg", s)


# ── Рис. 8.6.2 — трансформатор ───────────────────────────────────────────────
def fig61_transformer():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 34, "Трансформатор: дві обмотки на спільному осерді", 19, INK, "middle", "bold")
    t, d = xfmr(360, 190, 170, 150, 4, 4)
    s += t
    s += text(d["L"] + 13, d["B"] + 20, "первинна", 11, COPP, "middle", "bold")
    s += text(d["R"] - 13, d["B"] + 20, "вторинна", 11, COPP, "middle", "bold")
    s += text(360, d["T"] - 8, "осердя проводить потік Φ", 11.5, GREEN, "middle", "bold")
    # джерело ~ ліворуч
    src = ac_source(d["p_top"][0] - 40, (d["p_top"][1] + d["p_bot"][1]) / 2)
    s += src
    s += line(d["p_top"][0] - 40, d["p_top"][1] - 0, d["p_top"][0], d["p_top"][1], INK, 2) if False else ""
    sx = d["p_top"][0] - 40
    s += line(sx, (d["p_top"][1] + d["p_bot"][1]) / 2 - 20, sx, d["p_top"][1], INK, 2)
    s += line(sx, d["p_top"][1], d["p_top"][0], d["p_top"][1], INK, 2)
    s += line(sx, (d["p_top"][1] + d["p_bot"][1]) / 2 + 20, sx, d["p_bot"][1], INK, 2)
    s += line(sx, d["p_bot"][1], d["p_bot"][0], d["p_bot"][1], INK, 2)
    s += text(sx, d["p_bot"][1] + 24, "~", 18, INK, "middle", "bold")
    # навантаження праворуч
    lx = d["s_top"][0] + 40
    s += line(d["s_top"][0], d["s_top"][1], lx, d["s_top"][1], INK, 2)
    s += line(d["s_bot"][0], d["s_bot"][1], lx, d["s_bot"][1], INK, 2)
    s += rect(lx, (d["s_top"][1] + d["s_bot"][1]) / 2 - 16, 30, 32, "#eef2f6", INK, 1.6, 4)
    s += line(lx, d["s_top"][1], lx, (d["s_top"][1] + d["s_bot"][1]) / 2 - 16, INK, 2)
    s += line(lx, d["s_bot"][1], lx, (d["s_top"][1] + d["s_bot"][1]) / 2 + 16, INK, 2)
    s += text(lx + 15, (d["s_top"][1] + d["s_bot"][1]) / 2 + 40, "навант.", 10, INK, "middle")
    save("fig-8-6-2-transformer.svg", s)


# ── Рис. 8.6.3 — чому лише змінний струм ─────────────────────────────────────
def fig61_why_ac():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Трансформатор працює лише на ЗМІНІ потоку", 18, INK, "middle", "bold")
    # DC — нуль
    s += _frame(40, 76, 330, 230, "постійний струм")
    t1, d1 = xfmr(150, 180, 120, 110, 4, 4)
    s += t1
    bat, bt, bb = battery(d1["p_top"][0] - 26, (d1["p_top"][1] + d1["p_bot"][1]) / 2)
    s += bat
    s += galvo(d1["s_top"][0] + 24, (d1["s_top"][1] + d1["s_bot"][1]) / 2, 0, 18)
    s += text(205, 292, "сталий потік → у вторинній НУЛЬ", 11, RED, "middle", "bold")
    # AC — є
    s += _frame(400, 76, 330, 230, "змінний струм")
    t2, d2 = xfmr(520, 180, 120, 110, 4, 4)
    s += t2
    s += ac_source(d2["p_top"][0] - 26, (d2["p_top"][1] + d2["p_bot"][1]) / 2, 16)
    s += galvo(d2["s_top"][0] + 24, (d2["s_top"][1] + d2["s_bot"][1]) / 2, 24, 18)
    s += text(565, 292, "змінний потік → є напруга", 11, GREEN, "middle", "bold")
    save("fig-8-6-3-why-ac.svg", s)


# ── Рис. 8.6.4 — співвідношення витків ───────────────────────────────────────
def fig61_turns_ratio():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 34, "Співвідношення витків задає напругу", 19, INK, "middle", "bold")
    t, d = xfmr(360, 180, 180, 150, 8, 3)
    s += t
    s += text(d["L"] + 13, d["B"] + 20, "N₁ = 1000", 11.5, INK, "middle", "bold")
    s += text(d["R"] - 13, d["B"] + 20, "N₂ = 100", 11.5, INK, "middle", "bold")
    s += text(d["p_top"][0] - 70, 180, "230 В", 13, RED, "middle", "bold")
    s += text(d["s_top"][0] + 70, 180, "23 В", 13, GREEN, "middle", "bold")
    s += line(d["p_top"][0], d["p_top"][1], d["p_top"][0] - 40, d["p_top"][1], INK, 2)
    s += line(d["p_bot"][0], d["p_bot"][1], d["p_bot"][0] - 40, d["p_bot"][1], INK, 2)
    s += line(d["s_top"][0], d["s_top"][1], d["s_top"][0] + 40, d["s_top"][1], INK, 2)
    s += line(d["s_bot"][0], d["s_bot"][1], d["s_bot"][0] + 40, d["s_bot"][1], INK, 2)
    s += rect(60, H - 56, W - 120, 40, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 38, "V₂ / V₁ = N₂ / N₁ : удесятеро менше витків → удесятеро нижча напруга.",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 22, "Більше витків у вторинній — підвищувальний; менше — знижувальний.",
              11, GREY, "middle", style="italic")
    save("fig-8-6-4-turns-ratio.svg", s)


# ── Рис. 8.6.5 — потужність зберігається ─────────────────────────────────────
def fig61_power_conserved():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Потужність зберігається: підняв напругу — впав струм", 17.5, INK, "middle", "bold")
    # первинна сторона
    s += rect(70, 110, 240, 120, "#fdeded", RED, 1.6, 10)
    s += text(190, 138, "первинна", 13, INK, "middle", "bold")
    s += text(190, 168, "230 В · 0.1 А", 15, INK, "middle", "bold")
    s += text(190, 198, "= 23 Вт", 14, RED, "middle", "bold")
    s += arrow(316, 170, 404, 170, INK, 2.6)
    s += text(360, 158, "P", 13, INK, "middle", "bold")
    # вторинна сторона
    s += rect(410, 110, 240, 120, "#eef6ef", GREEN, 1.6, 10)
    s += text(530, 138, "вторинна", 13, INK, "middle", "bold")
    s += text(530, 168, "23 В · 1 А", 15, INK, "middle", "bold")
    s += text(530, 198, "= 23 Вт", 14, GREEN, "middle", "bold")
    s += text(W / 2, H - 26, "V ÷ 10  →  I × 10. Однакова потужність — безкоштовної енергії немає.",
              12.5, INK, "middle", "bold")
    save("fig-8-6-5-power-conserved.svg", s)


# ── Рис. 8.6.6 — гальванічна розв'язка ───────────────────────────────────────
def fig61_isolation():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Гальванічна розв'язка: кола зв'язані полем, а не дротом", 17.5, INK, "middle", "bold")
    t, d = xfmr(360, 180, 150, 130, 4, 4)
    s += t
    # бар'єр між обмотками
    s += line(360, 90, 360, 280, RED, 2, dash="6,5")
    s += text(360, 84, "немає електричного з'єднання", 11, RED, "middle", "bold")
    s += text(d["L"] - 30, 180, "мережа", 11, INK, "end", "bold")
    s += text(d["R"] + 30, 180, "безпечна", 11, INK, "start", "bold")
    s += text(d["R"] + 30, 196, "сторона", 11, INK, "start", "bold")
    s += line(d["p_top"][0], d["p_top"][1], d["p_top"][0] - 36, d["p_top"][1], INK, 2)
    s += line(d["p_bot"][0], d["p_bot"][1], d["p_bot"][0] - 36, d["p_bot"][1], INK, 2)
    s += line(d["s_top"][0], d["s_top"][1], d["s_top"][0] + 36, d["s_top"][1], INK, 2)
    s += line(d["s_bot"][0], d["s_bot"][1], d["s_bot"][0] + 36, d["s_bot"][1], INK, 2)
    s += rect(60, H - 40, W - 120, 26, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 21, "Енергія переходить лише крізь поле — тож небезпечна сторона лишається відділеною.",
              11.5, INK, "middle", "bold")
    save("fig-8-6-6-isolation.svg", s)


# ── Рис. 8.6.7 — застосування ────────────────────────────────────────────────
def fig61_applications():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо трансформатори", 20, INK, "middle", "bold")
    items = [("знизити напругу", "230 В → 5 В", "блоки живлення, зарядки"),
             ("підняти для передачі", "→ сотні кВ", "лінії електропередач"),
             ("розв'язати кола", "ізоляція", "безпека, медтехніка")]
    for i, (t1, t2, t3) in enumerate(items):
        x = 40 + i * 240
        s += _frame(x, 80, 220, 180, "")
        tt, d = xfmr(x + 110, 150, 110, 90, 4, 2 if i == 0 else (6 if i == 1 else 4))
        s += tt
        s += text(x + 110, 210, t1, 12.5, INK, "middle", "bold")
        s += text(x + 110, 230, t2, 12, GREEN, "middle", "bold")
        s += text(x + 110, 248, t3, 10.5, GREY, "middle", style="italic")
    save("fig-8-6-7-applications.svg", s)


# ── §8.6 історія (трансформатор) фігури ──────────────────────────────────────
def _bulb(cx, cy, r, bright):
    fill = "#fff4c2" if bright > 0.6 else ("#f1ead0" if bright > 0.3 else "#ededed")
    s = circle(cx, cy, r, fill, "#caa24a", 1.6)
    s += line(cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5, "#caa24a", 1.3)
    s += line(cx - r * 0.5, cy + r * 0.5, cx + r * 0.5, cy - r * 0.5, "#caa24a", 1.3)
    if bright > 0.6:
        for a in range(0, 360, 45):
            xa = cx + (r + 3) * math.cos(math.radians(a))
            ya = cy + (r + 3) * math.sin(math.radians(a))
            xb = cx + (r + 8) * math.cos(math.radians(a))
            yb = cy + (r + 8) * math.sin(math.radians(a))
            s += line(xa, ya, xb, yb, "#caa24a", 1.4)
    return s


def _house(cx, cy, w=40):
    s = rect(cx - w / 2, cy, w, w * 0.7, "#eef2f6", INK, 1.6)
    s += f'<path d="M {cx-w/2-4:.1f},{cy:.1f} L {cx:.1f},{cy-w*0.5:.1f} L {cx+w/2+4:.1f},{cy:.1f} Z" fill="#dcdce0" stroke="{INK}" stroke-width="1.6"/>\n'
    return s


def _tower(cx, base_y, h=40):
    s = _poly([(cx - 12, base_y), (cx - 5, base_y - h), (cx + 5, base_y - h), (cx + 12, base_y)], "#9a9aa0", 1.6)
    s += line(cx - 5, base_y - h, cx + 5, base_y - h, "#9a9aa0", 1.6)
    return s


def fig61i_dc_wall():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Едісонова стіна: постійний струм не їхав далеко", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "низька напруга → великий струм → втрати I²R з'їдають усе за кілька кварталів",
              12, GREY, "middle", style="italic")
    bat, bt, bb = battery(90, 150)
    s += bat
    s += text(90, 200, "110 В DC", 11.5, INK, "middle", "bold")
    y = 120
    s += line(90, y, 110, y, INK, 2)
    segs = [(120, 220), (300, 400), (480, 580)]
    bx = [260, 440, 620]
    bright = [0.85, 0.45, 0.18]
    prev = 110
    for i, (a, b) in enumerate(segs):
        s += resistor_h(a, b, y, "R")
        s += line(b, y, bx[i], y, INK, 2)
        s += line(bx[i], y, bx[i], 150, INK, 2)
        s += _bulb(bx[i], 165, 12, bright[i])
        s += line(bx[i], 180, bx[i], 200, INK, 2)
        if i < 2:
            s += line(bx[i], 200, segs[i + 1][0], 200, INK, 2)
            s += line(segs[i + 1][0], 200, segs[i + 1][0], y, INK, 2) if False else ""
    s += line(90, 168, 90, 200, INK, 2)
    s += line(90, 200, 120, 200, INK, 2)
    s += line(120, 200, 120, y, INK, 2) if False else ""
    # профіль напруги
    ox, oy, w, h = 110, 340, 560, 90
    s += _axes(ox, oy, w, h, "відстань", "V")
    s += _poly([(ox, oy - h * 0.95), (ox + 0.33 * w, oy - h * 0.6),
                (ox + 0.66 * w, oy - h * 0.32), (ox + w, oy - h * 0.14)], RED, 2.4)
    s += text(ox + 4, oy - h * 0.95 - 4, "110 В", 10.5, RED, "start", "bold")
    s += text(ox + w, oy - h * 0.14 - 6, "просіло", 10.5, RED, "end", "bold")
    s += text(W / 2, H - 10, "Станцію доводилось ставити мало не кожні 1.5 км.", 11, GREY, "middle", style="italic")
    save("fig-8-6i-1-dc-wall.svg", s)


def fig61i_transformer_grid():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Замкнене осердя (ZBD, 1885) зробило трансформатор практичним", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "енергомережа: підняти напругу → передати з малими втратами → знизити біля споживача",
              11.5, GREY, "middle", style="italic")
    y = 200
    # генератор
    s += ac_source(80, y, 22)
    s += text(80, y + 44, "генератор", 10.5, INK, "middle")
    s += line(102, y, 150, y, INK, 2)
    # підвищувальний
    t1, d1 = xfmr(200, y, 90, 90, 3, 7)
    s += t1
    s += text(200, y + 64, "↑ підняти", 10.5, GREEN, "middle", "bold")
    s += line(d1["s_top"][0], y, 320, y, INK, 2) if False else ""
    s += line(d1["R"], y - 10, 330, y - 10, INK, 2)
    # лінія з вежами
    s += line(330, y - 10, 500, y - 10, INK, 2)
    s += _tower(370, y + 20)
    s += _tower(460, y + 20)
    s += text(415, y - 22, "висока напруга, малий струм", 10.5, INK, "middle", "bold")
    # знижувальний
    t2, d2 = xfmr(560, y, 90, 90, 7, 3)
    s += t2
    s += line(500, y - 10, d2["L"], y - 10, INK, 2)
    s += text(560, y + 64, "↓ знизити", 10.5, GREEN, "middle", "bold")
    # будинок
    s += line(d2["R"], y, 700, y, INK, 2)
    s += _house(730, y - 14)
    s += text(730, y + 44, "споживач", 10.5, INK, "middle")
    save("fig-8-6i-2-transformer-grid.svg", s)


def fig61i_why_ac_won():
    W, H = 780, 360
    s = header(W, H)
    s += text(W / 2, 34, "Чому AC переміг: висока напруга — мізерні втрати", 18, INK, "middle", "bold")
    # без трансформатора (червоне)
    s += text(160, 92, "низька напруга", 12.5, RED, "middle", "bold")
    s += battery(70, 130)[0]
    s += line(82, 130, 110, 130, INK, 2)
    s += arrow(120, 130, 200, 130, RED, 5)
    s += text(160, 116, "великий струм", 10, RED, "middle", "bold")
    s += resistor_h(210, 300, 130, "дріт")
    for k in range(3):
        s += f'<path d="M {320+k*16},126 q 5,-9 10,0 q 5,9 10,0" fill="none" stroke="{RED}" stroke-width="1.6"/>\n'
    s += text(360, 112, "великі втрати", 10, RED, "middle", "bold")
    s += _bulb(440, 130, 13, 0.25)
    s += text(440, 156, "тьмяно", 10, GREY, "middle")
    # з трансформатором (зелене)
    s += text(160, 232, "трансформатор піднімає напругу", 12, GREEN, "middle", "bold")
    s += ac_source(70, 270, 16)
    t1, d1 = xfmr(150, 270, 70, 70, 3, 6)
    s += t1
    s += line(86, 270, d1["L"], 270, INK, 2) if False else ""
    s += line(d1["R"], 262, 300, 262, INK, 2)
    s += arrow(320, 262, 360, 262, GREEN, 2)
    s += text(340, 250, "малий струм", 9.5, GREEN, "middle", "bold")
    s += resistor_h(370, 440, 262, "дріт")
    s += text(490, 250, "втрати мізерні", 10, GREEN, "middle", "bold")
    t2, d2 = xfmr(560, 270, 70, 70, 6, 3)
    s += t2
    s += line(440, 262, d2["L"], 262, INK, 2)
    s += _bulb(650, 270, 13, 0.9)
    s += text(650, 298, "яскраво", 10, "#8a6d1a", "middle", "bold")
    save("fig-8-6i-3-why-ac-won.svg", s)


# ── §8.7 фігури ──────────────────────────────────────────────────────────────
def fig71_types():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 34, "Типи котушок за будовою й осердям", 19, INK, "middle", "bold")
    # повітряна
    s += _frame(30, 70, 185, 210, "повітряна")
    c, _ = coil_h(122, 150, 90, 5, 30)
    s += c
    s += line(72, 150, 77, 150, INK, 2)
    s += line(167, 150, 172, 150, INK, 2)
    s += text(122, 232, "мала L, без насичення", 10, GREY, "middle", style="italic")
    s += text(122, 248, "для ВЧ", 10, GREY, "middle", style="italic")
    # феритова/залізна
    s += _frame(225, 70, 185, 210, "феритова / залізна")
    s += rect(270, 138, 105, 24, "#cdd2d7", IRON, 1.4)
    c2, _ = coil_h(322, 150, 100, 5, 30)
    s += c2
    s += text(322, 232, "велика L у малому", 10, GREY, "middle", style="italic")
    s += text(322, 248, "об'ємі; насичується", 10, GREY, "middle", style="italic")
    # тороїдальна
    s += _frame(420, 70, 185, 210, "тороїдальна")
    s += f'<circle cx="512" cy="155" r="44" fill="none" stroke="{IRON}" stroke-width="16"/>\n'
    for a in range(0, 360, 30):
        x1 = 512 + 30 * math.cos(math.radians(a))
        y1 = 155 + 30 * math.sin(math.radians(a))
        x2 = 512 + 58 * math.cos(math.radians(a))
        y2 = 155 + 58 * math.sin(math.radians(a))
        s += line(x1, y1, x2, y2, COPP, 1.8)
    s += text(512, 232, "замкнене осердя —", 10, GREY, "middle", style="italic")
    s += text(512, 248, "низькі завади", 10, GREY, "middle", style="italic")
    # SMD
    s += _frame(615, 70, 175, 210, "SMD-дросель")
    s += rect(672, 125, 60, 55, "#3a3a3e", "#1b1b1b", 1.5, 8)
    s += text(702, 158, "L", 16, "#e0e0e0", "middle", "bold")
    s += text(702, 232, "масовий монтаж,", 10, GREY, "middle", style="italic")
    s += text(702, 248, "мільйони на платах", 10, GREY, "middle", style="italic")
    save("fig-8-7-1-types.svg", s)


def fig71_real_model():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 34, "Реальна котушка = L + опір обмотки + паразитна ємність", 17.5, INK, "middle", "bold")
    y = 150
    s += line(80, y, 140, y, INK, 2.2)
    s += ind_sym(140, 260, y, "L")
    s += line(260, y, 300, y, INK, 2.2)
    s += resistor_h(300, 400, y, "DCR")
    s += line(400, y, 640, y, INK, 2.2)
    # паразитна ємність паралельно
    s += line(110, y, 110, y + 60, GREY, 2)
    s += line(610, y, 610, y + 60, GREY, 2)
    cs, lx, rx = cap_sym(360, y + 60, 14, 9, GREY)
    s += line(110, y + 60, lx, y + 60, GREY, 2)
    s += line(rx, y + 60, 610, y + 60, GREY, 2)
    s += text(360, y + 90, "паразитна ємність між витками", 11, GREY, "middle", style="italic")
    s += rect(60, H - 46, W - 120, 32, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 33, "DCR гріє й «з'їдає» напругу; паразитна C задає стелю частоти (SRF).",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 17, "Дзеркало реальної моделі конденсатора (§7.5).", 10.5, GREY, "middle", style="italic")
    save("fig-8-7-2-real-model.svg", s)


def fig71_saturation():
    W, H = 700, 360
    s = header(W, H)
    s += text(W / 2, 34, "Струм насичення: вище за I_sat індуктивність падає", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 300, 520, 220
    s += _axes(ox, oy, w, h, "струм I", "індуктивність L")
    isat = ox + 0.55 * w
    s += _poly([(ox, oy - h * 0.85), (isat, oy - h * 0.82), (isat + 0.12 * w, oy - h * 0.45),
                (isat + 0.25 * w, oy - h * 0.18), (ox + w, oy - h * 0.08)], COPP, 2.8)
    s += line(isat, oy, isat, oy - h * 0.82, GREY, 1.4, dash="5,4")
    s += text(isat, oy + 20, "I_sat", 12.5, RED, "middle", "bold")
    s += text(ox + 0.25 * w, oy - h * 0.92, "стала L", 12, COPP, "middle", "bold")
    s += text(isat + 0.2 * w, oy - h * 0.5, "осердя насичене →", 11, RED, "middle", "bold")
    s += text(isat + 0.2 * w, oy - h * 0.36, "L падає", 11, RED, "middle", "bold")
    s += text(W / 2, H - 14, "Робочий струм беруть нижче за I_sat із запасом — дзеркало граничної напруги (§7.5).",
              11, GREY, "middle", style="italic")
    save("fig-8-7-3-saturation.svg", s)


def fig71_srf():
    W, H = 700, 360
    s = header(W, H)
    s += text(W / 2, 34, "Власна резонансна частота: вище за SRF — уже конденсатор", 17, INK, "middle", "bold")
    ox, oy, w, h = 110, 300, 520, 220
    s += _axes(ox, oy, w, h, "частота f", "|Z|")
    srf = ox + 0.55 * w
    s += _poly([(ox, oy - h * 0.12), (srf, oy - h * 0.9), (ox + w, oy - h * 0.18)], COPP, 2.8)
    s += line(srf, oy, srf, oy - h * 0.9, GREY, 1.4, dash="5,4")
    s += text(srf, oy + 20, "SRF", 12.5, RED, "middle", "bold")
    s += text(ox + 0.22 * w, oy - h * 0.35, "як КОТУШКА", 11.5, COPP, "middle", "bold")
    s += text(ox + 0.22 * w, oy - h * 0.2, "(|Z| росте)", 10, GREY, "middle")
    s += text(ox + 0.82 * w, oy - h * 0.42, "як КОНДЕНСАТОР", 11, BLUE, "middle", "bold")
    s += text(ox + 0.82 * w, oy - h * 0.27, "(|Z| падає)", 10, GREY, "middle")
    s += text(W / 2, H - 14, "Кожну котушку застосовують лише нижче за SRF (деталі частоти — Розділ 9).",
              11, GREY, "middle", style="italic")
    save("fig-8-7-4-srf.svg", s)


def fig71_choke():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Дросель: пропускає постійне, затримує швидку пульсацію", 17.5, INK, "middle", "bold")
    y = 150
    # вхід: постійне + шум
    s += text(150, 96, "вхід: DC + шум", 11.5, INK, "middle", "bold")
    s += _poly([(70 + i * 4, y - 30 - (10 if i % 3 else -10) * math.sin(i)) for i in range(0, 40)], GREY, 1.6)
    s += line(70, y, 150, y, INK, 2.2)
    s += ind_sym(150, 270, y, "дросель")
    s += line(270, y, 350, y, INK, 2.2)
    # конденсатор у землю
    cs, lx, rx = cap_sym(310, y + 40, 12, 8)
    s += line(310, y, 310, y + 31, INK, 2)
    s += line(310, y + 49, 310, y + 70, INK, 2)
    s += text(330, y + 45, "C", 11, INK, "start", "bold")
    # вихід: гладко
    s += text(560, 96, "вихід: чисте DC", 11.5, GREEN, "middle", "bold")
    s += line(450, y - 30, 660, y - 30, GREEN, 2.4)
    s += arrow(370, y, 440, y, INK, 2.2)
    s += text(415, y - 10, "→", 12, INK, "middle")
    s += rect(60, H - 56, W - 120, 40, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 38, "Котушка опирається швидкій зміні — тож гасить шум, а постійне пропускає.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, H - 21, "Дросель + конденсатор = фільтр живлення (дзеркало розв'язки §7.6).",
              10.5, GREY, "middle", style="italic")
    save("fig-8-7-5-choke.svg", s)


def fig71_applications():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 34, "Де живуть котушки", 20, INK, "middle", "bold")
    cards = [("дроселі / фільтри", "затримати шум", LGRN),
             ("накопичувач", "імпульсні БЖ (§8.5)", "#dbe7f5"),
             ("трансформатори", "змінити напругу (§8.6)", LGRN),
             ("електромагніти", "реле, мотори", "#fdeded"),
             ("контури радіо", "вибрати частоту", "#fdeecf"),
             ("антени", "випромінити (Модуль 6)", "#dbe7f5")]
    for i, (t1, t2, col) in enumerate(cards):
        x = 40 + (i % 3) * 240
        y = 80 + (i // 3) * 110
        s += rect(x, y, 220, 90, col, "#b9b9bf", 1.6, 10)
        s += text(x + 110, y + 36, t1, 13.5, INK, "middle", "bold")
        s += text(x + 110, y + 62, t2, 11, GREY, "middle", style="italic")
    save("fig-8-7-6-applications.svg", s)


def fig71_datasheet():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 34, "Як читати котушку: чотири головні числа", 19, INK, "middle", "bold")
    c, _ = coil_h(350, 165, 120, 6, 34)
    s += c
    params = [("L", "індуктивність — сила котушки", GREEN, 110, 90),
              ("I_sat", "струм насичення — межа струму", RED, 590, 90),
              ("DCR", "опір обмотки — нагрів", "#9c7b46", 110, 250),
              ("SRF", "стеля частоти", BLUE, 590, 250)]
    for name, desc, col, lx, ly in params:
        s += text(lx, ly, name, 17, col, "middle", "bold")
        s += text(lx, ly + 18, desc, 10.5, INK, "middle")
        s += line(lx, ly + (10 if ly < 165 else -28), 350, 165, col, 1.2, dash="3,3")
    s += text(W / 2, H - 16, "Як ємність+напруга для конденсатора — баланс цих чисел вирішує придатність.",
              11, GREY, "middle", style="italic")
    save("fig-8-7-7-datasheet.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 8 — електромагнітна індукція
    fig_timeline()
    fig_oersted()
    fig_faraday_ring()
    fig_moving_magnet()
    fig_lenz()
    fig_payoff()
    # §8.1 Котушка й магнітне поле струму
    fig11_wire_field()
    fig11_right_hand()
    fig11_loop()
    fig11_solenoid()
    fig11_field_lines()
    fig11_core()
    fig11_ampere_turns()
    fig11_dual()
    # §8.2 Індуктивність і самоіндукція
    fig21_self_induction()
    fig21_vldidt()
    fig21_inertia()
    fig21_henry()
    fig21_n_squared()
    fig21_determinants()
    fig21_dc_short()
    fig21_duals()
    # §8.3 Енергія в магнітному полі
    fig31_work_to_build()
    fig31_half_formula()
    fig31_i_squared()
    fig31_field_storage()
    fig31_kinetic()
    fig31_store_vs_dissipate()
    fig31_release()
    # §8.4 Перехідні процеси RL
    fig41_rl_circuit()
    fig41_current_rise()
    fig41_voltage_decay()
    fig41_current_decay()
    fig41_tau_meaning()
    fig41_no_jump()
    fig41_5tau_table()
    fig41_rl_vs_rc()
    # §8.5 «Брикання» котушки
    fig51_spike_origin()
    fig51_energy_nowhere()
    fig51_danger()
    fig51_flyback_diode()
    fig51_with_diode_decay()
    fig51_tamers_tradeoff()
    fig51_harnessed()
    # §8.6 Взаємоіндукція й трансформація
    fig61_mutual()
    fig61_transformer()
    fig61_why_ac()
    fig61_turns_ratio()
    fig61_power_conserved()
    fig61_isolation()
    fig61_applications()
    # Історія до §8.6 — трансформатор
    fig61i_dc_wall()
    fig61i_transformer_grid()
    fig61i_why_ac_won()
    # §8.7 Типи й застосування котушок
    fig71_types()
    fig71_real_model()
    fig71_saturation()
    fig71_srf()
    fig71_choke()
    fig71_applications()
    fig71_datasheet()
    print("OK — фігури Розділу 8 (повний: історія + §8.1–§8.7) згенеровано в", OUT)
