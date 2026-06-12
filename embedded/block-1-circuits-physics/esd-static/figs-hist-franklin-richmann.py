# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 1.10 —
«Франклін, Ріхман і приборкання блискавки» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs-r08-history-lodestone-oersted.py (за §9 — кожен скрипт самодостатній).
Нумерація: історія до розділу — секція 0 → Рис. 1.10.0.N.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
SKY = "#cfe0ec"
CLOUD = "#9aa6ad"
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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", ORANGE: "aOrange"}


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


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def _cloud(cx, cy, scale=1.0, fill=CLOUD):
    """Стилізована грозова хмара з кружалець."""
    s = ""
    blobs = [(-70, 8, 34), (-32, -6, 42), (12, -10, 46), (54, -2, 40), (88, 10, 32),
             (-40, 18, 30), (4, 22, 34), (48, 20, 30)]
    for dx, dy, r in blobs:
        s += circle(cx + dx * scale, cy + dy * scale, r * scale, fill, fill, 0)
    return s


def _bolt(x, y, dx, dy, color=ORANGE, w=3.2):
    """Зиґзаґ блискавки з (x,y) у напрямку (dx,dy)."""
    pts = [(x, y),
           (x + dx * 0.30 - 14, y + dy * 0.28),
           (x + dx * 0.46 + 10, y + dy * 0.48),
           (x + dx * 0.64 - 12, y + dy * 0.68),
           (x + dx, y + dy)]
    return polyline(pts, color, w)


def _ground(x0, x1, y, color=INK):
    """Лінія землі + штрихування."""
    s = line(x0, y, x1, y, color, 2.4)
    n = int((x1 - x0) // 16)
    for i in range(n):
        gx = x0 + 8 + i * 16
        s += line(gx, y, gx - 9, y + 11, color, 1.3)
    return s


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 1.10 — Франклін, Ріхман і приборкання блискавки. Рис. 1.10.0.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.0.1 — дослід із вартовою будкою ─────────────────────────────────
def fig_sentry_box():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 30, "Дослід із вартовою будкою (Франклін, 1750): зловити заряд хмари",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "шпиль набирає заряд із хмари; спостерігач на ізоляторі підносить заземлений дріт — проскік іскри доводить, що хмара заряджена",
              11, GREY, "middle", style="italic")

    # небо-смуга
    s += rect(40, 70, W - 80, 150, SKY, SKY, 0, 8)
    # заряджена хмара (низ — від'ємний, типово для грозової бази)
    s += _cloud(560, 130, 1.05)
    for i, (mx, my, sign, col) in enumerate([(470, 168, "−", BLUE), (540, 176, "−", BLUE),
                                             (610, 172, "−", BLUE), (660, 162, "−", BLUE)]):
        s += text(mx, my, sign, 19, col, "middle", "bold")
    s += text(560, 96, "грозова хмара", 12, INK, "middle", "bold")

    gy = 470
    s += _ground(60, W - 60, gy)

    # ── будка ──
    bx, bw = 250, 150
    s += rect(bx, 300, bw, gy - 300, "#f3ede2", COPPER, 2.2)
    s += rect(bx, 300, bw, 22, "#e7dcc8", COPPER, 2.2)  # дашок
    s += text(bx + bw / 2, 292, "суха ізольована будка", 11, COPPER, "middle", "bold")

    # шпиль із даху вгору
    spx = bx + bw / 2
    s += line(spx, 300, spx, 150, INK, 3.4)
    s += polygon([(spx, 138), (spx - 5, 152), (spx + 5, 152)], INK)  # вістря
    s += text(spx + 12, 158, "залізний шпиль", 11, INK, "start", "bold")
    s += text(spx + 12, 174, "(вістря вгорі)", 9.5, GREY, "start")
    # наведений + заряд на шпилі (верх додатний — індукція від'ємної бази хмари)
    for yy in (165, 185, 205):
        s += text(spx - 12, yy, "+", 14, RED, "middle", "bold")

    # ── спостерігач усередині на ізоляторі ──
    ox = bx + 44
    # ізолятор-підставка (віск/скло)
    s += rect(ox - 22, gy - 18, 44, 18, "#f6e9b0", ORANGE, 1.8, 3)
    s += text(ox, gy + 14, "ізолятор", 9.5, ORANGE, "middle", "bold")
    # схематична постать
    s += circle(ox, gy - 120, 11, "#ffffff", INK, 2)              # голова
    s += line(ox, gy - 109, ox, gy - 55, INK, 2.6)                # тулуб
    s += line(ox, gy - 95, ox + 34, gy - 80, INK, 2.4)            # рука до дроту
    s += line(ox, gy - 55, ox - 12, gy - 20, INK, 2.4)           # нога
    s += line(ox, gy - 55, ox + 12, gy - 20, INK, 2.4)           # нога

    # заземлений дріт у руці
    wx0, wy0 = ox + 34, gy - 80
    s += line(wx0, wy0, spx - 26, wy0, GREEN, 2.4)               # дріт до шпиля
    s += line(spx - 26, wy0, spx - 26, gy, GREEN, 2.4)          # …але насправді він заземлений
    # переграємо: заземлений дріт іде в землю (зелений = земля/захист)
    s += text(ox + 50, wy0 - 8, "заземлений дріт", 10, GREEN, "start", "bold")

    # іскровий проміжок між шпилем і дротом
    gap_x, gap_y = spx - 13, wy0
    s += text(gap_x, wy0 - 26, "іскра!", 12, ORANGE, "middle", "bold")
    s += _bolt(spx - 4, 218, -14, wy0 - 224, ORANGE, 2.6)
    s += polyline([(spx - 22, wy0 - 4), (spx - 16, wy0 + 2), (spx - 20, wy0 - 2), (spx - 12, wy0 + 3)],
                  ORANGE, 2.6)

    # підпис під іскрою
    s += text(spx + 6, wy0 + 22, "проміжок", 9.5, GREY, "start")

    # ── права колонка: дві ролі вістря ──
    px0 = 690
    s += rect(px0, 250, 210, 196, "#f7f7f7", GREY, 1.6, 10)
    s += text(px0 + 105, 274, "Дві ролі вістря", 13, INK, "middle", "bold")
    # роль 1: тихо стікає (корона)
    s += text(px0 + 16, 304, "1) тихо стікає заряд", 11, GREEN, "start", "bold")
    s += text(px0 + 26, 320, "(корона, без удару)", 9.5, GREY, "start")
    s += line(px0 + 30, 338, px0 + 30, 356, INK, 2.6)
    s += polygon([(px0 + 30, 330), (px0 + 26, 340), (px0 + 34, 340)], INK)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        s += line(px0 + 30, 332, px0 + 30 + 13 * math.cos(a), 332 - 13 * math.sin(a), GREEN, 1.3)
    # роль 2: приймає удар
    s += text(px0 + 16, 386, "2) приймає удар", 11, ORANGE, "start", "bold")
    s += text(px0 + 26, 402, "і веде в землю", 9.5, GREY, "start")
    s += _bolt(px0 + 120, 360, 24, 56, ORANGE, 2.6)
    s += line(px0 + 150, 416, px0 + 150, 436, INK, 2.6)

    s += text(W / 2, 512, "Це й поставили першими у Франції (Марлі-ла-Віль, травень 1752): заземлений дріт відводить заряд — людина лишається осторонь, на ізоляторі.",
              11, INK, "middle", "bold")
    save("fig-r10-hist-1-sentry-box.svg", s)


# ── Рис. 1.10.0.2 — дослід зі змієм ───────────────────────────────────────────
def fig_kite():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 30, "Дослід зі змієм: де ховається безпека, а де — смертельна помилка",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "заряд стікає мокрим шнуром до ключа; уся безпека — на сухій шовковій стрічці-ізоляторі під накриттям",
              11, GREY, "middle", style="italic")

    s += rect(40, 70, W - 80, 150, SKY, SKY, 0, 8)
    s += _cloud(330, 130, 1.0)
    for mx, my in [(250, 170), (320, 176), (390, 168)]:
        s += text(mx, my, "−", 19, BLUE, "middle", "bold")
    s += text(330, 96, "грозова хмара (заряджена)", 12, INK, "middle", "bold")

    gy = 500
    s += _ground(60, W - 60, gy)

    # ── змій угорі ліворуч ──
    kx, ky = 300, 180
    kite = [(kx, ky - 40), (kx + 34, ky), (kx, ky + 40), (kx - 34, ky)]
    s += polygon(kite, "#e7dcc8", COPPER, 2)
    s += line(kx, ky - 40, kx, ky + 40, COPPER, 1.4)
    s += line(kx - 34, ky, kx + 34, ky, COPPER, 1.4)
    # загострений дротик угорі змія
    s += line(kx, ky - 40, kx, ky - 66, INK, 3)
    s += polygon([(kx, ky - 72), (kx - 4, ky - 62), (kx + 4, ky - 62)], INK)
    s += text(kx + 10, ky - 60, "загострений дротик", 10, INK, "start", "bold")
    # «висмоктує» заряд із хмари
    s += arrow(kx + 6, ky - 96, kx + 2, ky - 76, BLUE, 1.6)

    # ── мокрий шнур донизу до руки під накриттям ──
    handx, handy = 760, gy - 150  # людина праворуч під накриттям
    keyx, keyy = handx - 6, handy - 96
    # шнур від змія до ключа (зиґзаґом, мокрий — проводить)
    s += polyline([(kx, ky + 40), (440, 250), (560, 300), (keyx, keyy)], RED, 2.6)
    s += text(500, 268, "мокрий шнур", 11, RED, "start", "bold")
    s += text(500, 284, "(проводить заряд донизу)", 9, GREY, "start")
    # настовбурчені волокна на шнурі
    fx, fy = 600, 322
    for ang in (-40, -18, 0, 18, 40):
        a = math.radians(ang)
        s += line(fx, fy, fx + 16 * math.sin(a), fy - 16 * math.cos(a), RED, 1.3)
    s += text(fx + 26, fy - 6, "волокна настовбурчені", 9.5, RED, "start")
    s += text(fx + 26, fy + 8, "(однаковий заряд → відштовхування)", 8.5, GREY, "start")

    # ── ключ ──
    s += circle(keyx, keyy, 7, "#d9d2c4", INK, 1.8)
    s += rect(keyx - 2.5, keyy + 6, 5, 16, "#d9d2c4", INK, 1.4)
    s += text(keyx + 16, keyy - 4, "металевий ключ", 10, INK, "start", "bold")
    s += text(keyx + 16, keyy + 12, "(іскра пальцем; зарядити", 9, GREY, "start")
    s += text(keyx + 16, keyy + 26, "лейденську банку)", 9, GREY, "start")

    # ── суха шовкова стрічка-ізолятор між ключем і рукою ──
    s += line(keyx, keyy + 22, handx, handy, ORANGE, 3, "6,4")
    s += text((keyx + handx) / 2 + 4, (keyy + handy) / 2 + 20, "суха шовкова стрічка", 10.5, ORANGE, "middle", "bold")
    s += text((keyx + handx) / 2 + 4, (keyy + handy) / 2 + 35, "= ІЗОЛЯТОР (тримати сухою!)", 9.5, ORANGE, "middle", "bold")

    # ── накриття (навіс) над людиною ──
    s += line(700, handy - 150, 880, handy - 150, COPPER, 3)
    s += line(710, handy - 150, 710, handy - 130, COPPER, 2)
    s += line(870, handy - 150, 870, handy - 130, COPPER, 2)
    s += text(790, handy - 158, "накриття (шовк лишається сухим)", 10, COPPER, "middle", "bold")

    # ── постать людини ──
    s += circle(handx, handy + 8, 11, "#ffffff", INK, 2)
    s += line(handx, handy + 19, handx, handy + 72, INK, 2.6)
    s += line(handx, handy + 30, handx - 4, handy, INK, 2.4)   # рука вгору до стрічки
    s += line(handx, handy + 72, handx - 12, gy, INK, 2.4)
    s += line(handx, handy + 72, handx + 12, gy, INK, 2.4)

    # ── застереження-блок ──
    s += rect(70, 360, 300, 110, "#fbeeea", RED, 1.8, 10)
    s += text(220, 384, "Чому Франклін вижив", 12.5, RED, "middle", "bold")
    s += text(86, 406, "Дослід знімав лише НАВЕДЕНИЙ заряд", 10, INK, "start")
    s += text(86, 423, "із зарядженої (ще не розрядженої) хмари —", 10, INK, "start")
    s += text(86, 440, "слабкий струм, іскри ~сантиметри.", 10, INK, "start")
    s += text(86, 459, "Прямий удар блискавки шнур не пережив би.", 10, RED, "start", "bold")

    s += text(W / 2, 536, "Деталі саме франклінівського змія дійшли переказом (Прістлі, 1767) і в дрібницях ненадійні (перевірити); але заряд хмари 1752 р. зловлено — це факт.",
              10.5, GREY, "middle", style="italic")
    save("fig-r10-hist-2-kite.svg", s)


# ── Рис. 1.10.0.3 — фатальна установка Ріхмана vs безпечна будка ───────────────
def fig_richmann():
    W, H = 940, 520
    s = header(W, H)
    s += text(W / 2, 30, "Чому установка Ріхмана була смертельною: різниця — у шляху струму",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "стрижень із даху вів заряд просто до приладу в кімнаті, без заземлення на проміжку — і людина опинилася на шляху розряду",
              11, GREY, "middle", style="italic")

    gy = 458

    # ── ЛІВА панель: безпечно (вартова будка, заземлено повз людину) ──
    s += rect(40, 78, 410, gy - 60, "#eef7f0", GREEN, 1.8, 12)
    s += text(245, 104, "БЕЗПЕЧНО: заземлено повз людину", 13, GREEN, "middle", "bold")
    s += _ground(70, 420, gy - 18, INK)
    # хмара-натяк
    s += _cloud(245, 150, 0.62)
    s += text(310, 132, "−", 16, BLUE, "middle", "bold")
    # шпиль
    s += line(245, 200, 245, 250, INK, 3)
    s += polygon([(245, 192), (241, 204), (249, 204)], INK)
    # заземлений дріт ОСТОРОНЬ → у землю
    s += line(245, 250, 360, 250, GREEN, 2.6)
    s += line(360, 250, 360, gy - 18, GREEN, 2.6)
    s += text(366, 300, "заземлений", 9.5, GREEN, "start", "bold")
    s += text(366, 314, "дріт у землю", 9.5, GREEN, "start", "bold")
    # людина осторонь на ізоляторі
    px = 150
    s += rect(px - 20, gy - 36, 40, 16, "#f6e9b0", ORANGE, 1.6, 3)
    s += text(px, gy - 2, "ізолятор", 9, ORANGE, "middle", "bold")
    s += circle(px, gy - 120, 10, "#ffffff", INK, 2)
    s += line(px, gy - 110, px, gy - 64, INK, 2.4)
    s += line(px, gy - 96, px + 26, gy - 86, INK, 2.2)
    s += line(px, gy - 64, px - 10, gy - 36, INK, 2.2)
    s += line(px, gy - 64, px + 10, gy - 36, INK, 2.2)
    s += text(px, gy - 134, "осторонь", 9.5, GREEN, "middle", "bold")
    # розряд іде в землю повз людину
    s += _bolt(245, 210, 0, 36, ORANGE, 2.4)
    s += arrow(360, 360, 360, 420, GREEN, 2)
    s += text(300, 400, "струм → земля", 10, GREEN, "middle", "bold")

    # ── ПРАВА панель: смертельно (стрижень просто в кімнату, без заземлення) ──
    s += rect(500, 78, 400, gy - 60, "#fbeeea", RED, 1.9, 12)
    s += text(700, 104, "СМЕРТЕЛЬНО: стрижень просто в кімнату", 12.5, RED, "middle", "bold")
    s += _ground(530, 880, gy - 18, INK)
    s += _cloud(700, 150, 0.62)
    s += text(760, 130, "−", 16, BLUE, "middle", "bold")
    # удар блискавки поряд
    s += _bolt(700, 168, 22, 60, ORANGE, 3.0)
    s += text(742, 196, "поряд б'є блискавка", 10, ORANGE, "start", "bold")

    # дах + стрижень
    roofy = 250
    s += line(560, roofy, 840, roofy, COPPER, 3)
    s += line(640, roofy, 640, 200, INK, 3)
    s += polygon([(640, 192), (636, 204), (644, 204)], INK)
    s += text(648, 200, "стрижень з даху", 10, INK, "start", "bold")

    # стіна кімнати
    s += rect(560, roofy, 280, gy - 18 - roofy, "#f3ede2", COPPER, 1.6)
    s += text(700, roofy + 18, "кімната", 10.5, COPPER, "middle", "bold")

    # дріт від стрижня ВНИЗ до приладу (без заземлення!)
    s += line(640, roofy, 640, 360, RED, 2.8)
    # прилад (електрометр зі стрілкою/ниткою)
    s += rect(612, 360, 56, 50, "#ffffff", INK, 2, 4)
    s += line(640, 360, 640, 400, INK, 1.6)         # вертикальна лінійка
    s += line(640, 366, 658, 396, GREY, 1.6)        # відхилена нитка
    s += text(640, 350, "«електричний покажчик»", 9, INK, "middle", "bold")
    s += text(640, 426, "(відхилення нитки = заряд)", 8.5, GREY, "middle")

    # НЕМАЄ заземлення — підкреслити
    s += text(700, 452, "✗ без заземлення на проміжку", 11, RED, "middle", "bold")

    # людина впритул до приладу
    hx = 730
    s += circle(hx, 384, 9, "#ffffff", INK, 2)
    s += line(hx, 393, hx, 430, INK, 2.4)
    s += line(hx, 402, hx - 24, 396, INK, 2.2)   # рука до приладу
    s += line(hx, 430, hx - 8, gy - 18, INK, 2.2)
    s += line(hx, 430, hx + 8, gy - 18, INK, 2.2)
    # світна куля б'є в чоло
    s += circle(hx - 2, 372, 6.5, ORANGE, RED, 2)
    s += text(hx + 14, 366, "світна куля", 9.5, RED, "start", "bold")
    s += text(hx + 14, 380, "→ у чоло", 9.5, RED, "start", "bold")

    s += text(W / 2, gy + 30, "Та сама фізика, та сама блискавка — різниця лише в тому, КУДИ тече струм і ДЕ стоїть людина. Звідси правило: спершу шлях у землю повз людину.",
              11, INK, "middle", "bold")
    save("fig-r10-hist-3-richmann.svg", s)


if __name__ == "__main__":
    fig_sentry_box()
    fig_kite()
    fig_richmann()
    print("done.")
