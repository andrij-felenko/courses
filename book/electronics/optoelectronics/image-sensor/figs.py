# -*- coding: utf-8 -*-
"""Фігури до теми «Сенсор зображення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Фотоефект: фотон вибиває з кремнію електрон ───────────────────────────
def fig_photoeffect():
    W, H = 780, 360
    f = [text(W / 2, 26, "Фотон вибиває з кремнію електрон", size=17, bold=True),
         text(W / 2, 47, "що яскравіше світло, то більше фотонів — і більше вільних електронів",
              size=12, color=MUTED)]

    # сонце-джерело ліворуч
    sx, sy = 70, 150
    f.append(circle(sx, sy, 30, fill="#fff4cc", stroke="#e0a800", sw=2))
    f.append(text(sx, sy + 5, "світло", size=11, bold=True, color="#9a7400"))

    # три фотони летять у кремній
    for i, dy in enumerate((-46, 0, 46)):
        x1 = sx + 34
        y1 = sy + dy * 0.5
        x2 = 300
        y2 = 150 + dy
        f.append(line(x1, y1, x2, y2, color="#e0a800", sw=2.2, dash="2,5"))
        f.append(text((x1 + x2) / 2, (y1 + y2) / 2 - 6, "фотон", size=9,
                      color="#9a7400", anchor="middle"))

    # брус кремнію — ґратка атомів
    gx, gy, gw, gh = 320, 96, 250, 168
    f.append(rect(gx, gy, gw, gh, fill="#eef2f7", stroke=INK, sw=1.6))
    f.append(text(gx + gw / 2, gy - 10, "КРЕМНІЙ (ґратка атомів)", size=11, bold=True))
    for r in range(3):
        for c in range(4):
            ax = gx + 38 + c * 58
            ay = gy + 42 + r * 50
            f.append(circle(ax, ay, 13, fill="#d6deea", stroke="#9aa8bd", sw=1.3))
            # зв'язані електрони — дрібні сині точки навколо
            f.append(circle(ax - 16, ay, 3.2, fill=NEG, stroke="none"))
            f.append(circle(ax + 16, ay, 3.2, fill=NEG, stroke="none"))

    # один електрон вибито й летить геть (вільний)
    ex0, ey0 = gx + 38 + 1 * 58 + 16, gy + 42 + 1 * 50
    f.append(line(ex0, ey0, 650, 150, color=NEG, sw=2))
    f.append(circle(650, 150, 9, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(650, 154, "−", size=15, color=NEG, bold=True))
    f.append(text(672, 150, "вільний", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(672, 166, "електрон", size=11, color=NEG, anchor="start", bold=True))

    f.append(text(W / 2, H - 14,
                  "Світло-причина → електрон-наслідок: кількість вибитих електронів пропорційна кількості світла.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "photoeffect.svg"), W, H, *f)


# ── 2. Піксель як відерце: фотодіод накопичує заряд → напруга → число ────────
def fig_bucket():
    W, H = 820, 380
    f = [text(W / 2, 26, "Піксель — відерце для електронів", size=17, bold=True),
         text(W / 2, 47, "фотодіод накопичує заряд за час витримки; рівень = яскравість цятки",
              size=12, color=MUTED)]

    # фотони сиплються згори
    for i in range(6):
        x = 110 + i * 26
        f.append(line(x, 70, x - 10, 150, color="#e0a800", sw=1.8, dash="2,4"))
    f.append(text(150, 64, "фотони", size=11, color="#9a7400", bold=True))

    # відерце (потенціальна яма) частково повне
    bx, by, bw, bh = 92, 150, 150, 150
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2"/>'
             % (bx, by, bx + 18, by + bh, bx + bw - 18, by + bh, bx + bw, by, INK))
    # рівень заряду
    lvl = 92
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d Z" fill="#cfe0ff" stroke="none"/>'
             % (bx + 12, by + bh - lvl, bx + 18, by + bh,
                bx + bw - 18, by + bh, bx + bw - 12, by + bh - lvl))
    # електрони у відерці
    import random
    random.seed(5)
    for _ in range(16):
        rx = bx + 26 + random.random() * (bw - 52)
        ry = by + bh - 12 - random.random() * (lvl - 24)
        f.append(circle(rx, ry, 3, fill=NEG, stroke="none"))
    f.append(text(bx + bw / 2, by + bh + 20, "потенціальна яма (фотодіод)", size=10.5,
                  color=MUTED))
    f.append(text(bx + bw + 6, by + bh - lvl, "рівень", size=10, color=NEG, anchor="start"))

    # ланцюжок перетворень праворуч
    steps = ["заряд", "напруга", "АЦП", "число"]
    colors = ["#cfe0ff", "#dcfce7", "#fde9c8", "#e9e9ef"]
    x = 330
    cy = 200
    for i, (s, col) in enumerate(zip(steps, colors)):
        bw2 = 92
        f.append(rect(x, cy - 28, bw2, 56, fill=col, stroke=INK, sw=1.5, rx=8))
        f.append(text(x + bw2 / 2, cy + 5, s, size=13, bold=True))
        if i < len(steps) - 1:
            f.append(arrow(x + bw2 + 4, cy, x + bw2 + 32, cy, sw=2.2))
        x += bw2 + 36
    f.append(text(330 + 2 * (92 + 36) - 18, cy - 44,
                  "[аналого-цифровий перетворювач]", size=9, color=MUTED))

    f.append(text(W / 2, H - 28,
                  "Світло → електрони → заряд → напруга → число: це число і є яскравість пікселя.",
                  size=11.5, color=MUTED, italic=True))
    f.append(text(W / 2, H - 12,
                  "Саме відерце сліпе до кольору — лічить усі фотони підряд, тобто міряє лише яскравість.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "bucket.svg"), W, H, *f)


# ── 3. Витримка: компроміс світло проти різкості ─────────────────────────────
def fig_exposure():
    W, H = 800, 360
    f = [text(W / 2, 26, "Витримка: скільки тримати відерце відкритим", size=17, bold=True),
         text(W / 2, 47, "довша набирає більше світла, та розмиває рух",
              size=12, color=MUTED)]

    # ліворуч — коротка витримка
    f.append(text(210, 86, "КОРОТКА", size=13, color=NEG, bold=True))
    f.append(rect(120, 100, 180, 96, fill="#1f2937", stroke=INK, sw=1.5, rx=8))
    # різкий контур об'єкта
    f.append(circle(210, 148, 22, fill="none", stroke="#e5e7eb", sw=2.4))
    f.append(text(210, 216, "мало світла → темно", size=10.5, color=MUTED))
    f.append(text(210, 234, "рух застигає різко", size=10.5, color=NEG, bold=True))

    # праворуч — довга витримка
    f.append(text(590, 86, "ДОВГА", size=13, color=POS, bold=True))
    f.append(rect(500, 100, 180, 96, fill="#9aa3b2", stroke=INK, sw=1.5, rx=8))
    # розмазаний об'єкт — кілька напівпрозорих кіл
    for i, dx in enumerate((-24, -8, 8, 24)):
        f.append('<circle cx="%d" cy="148" r="20" fill="none" stroke="#1f2937" '
                 'stroke-width="2" stroke-opacity="%.2f"/>' % (590 + dx, 0.3 + i * 0.15))
    f.append(text(590, 216, "багато світла → яскраво", size=10.5, color=MUTED))
    f.append(text(590, 234, "рух розмазується (motion blur)", size=10.5, color=POS, bold=True))

    # вісь часу між ними
    f.append(arrow(310, 300, 490, 300, sw=2))
    f.append(text(400, 290, "довша витримка", size=11, color=MUTED))
    f.append(text(400, 320, "більше світла, більше змазування", size=10, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "На тремкому летючому апараті радше коротша витримка: різкий темний кадр кращий за яскравий мазок.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "exposure.svg"), W, H, *f)


# ── 4. Стеля й підлога: насичення та шум, динамічний діапазон ────────────────
def fig_saturation():
    W, H = 760, 400
    f = [text(W / 2, 26, "Стеля й підлога пікселя", size=17, bold=True),
         text(W / 2, 47, "корисний піксель лежить між шумом і насиченням",
              size=12, color=MUTED)]

    # центральне відерце з трьома зонами
    bx, by, bw, bh = 300, 80, 160, 270
    f.append(rect(bx, by, bw, bh, fill="white", stroke=INK, sw=1.8, rx=4))

    # зона насичення (верх) — червона
    f.append(rect(bx, by, bw, 54, fill="#fde2e2", stroke="none"))
    f.append(line(bx, by + 54, bx + bw, by + 54, color=POS, sw=2, dash="5,3"))
    f.append(text(bx + bw / 2, by + 30, "НАСИЧЕННЯ", size=11, color=POS, bold=True))
    f.append(text(bx + bw / 2, by + 46, "(пересвіт, біле)", size=9, color=POS))

    # корисна зона (середина) — зелена
    f.append(rect(bx, by + 54, bw, 158, fill="#eafaef", stroke="none"))
    f.append(text(bx + bw / 2, by + 130, "КОРИСНИЙ", size=12, color="#15803d", bold=True))
    f.append(text(bx + bw / 2, by + 148, "діапазон", size=11, color="#15803d", bold=True))

    # зона шуму (низ) — синя
    f.append(line(bx, by + 212, bx + bw, by + 212, color=NEG, sw=2, dash="5,3"))
    f.append(rect(bx, by + 212, bw, 58, fill="#eaf0fd", stroke="none"))
    f.append(text(bx + bw / 2, by + 244, "ПІДЛОГА ШУМУ", size=11, color=NEG, bold=True))
    f.append(text(bx + bw / 2, by + 260, "(деталь тоне)", size=9, color=NEG))
    f.append(rect(bx, by, bw, bh, fill="none", stroke=INK, sw=1.8, rx=4))

    # підписи стелі/підлоги
    f.append(text(bx - 12, by + 54, "повна місткість", size=10, color=POS, anchor="end"))
    f.append(text(bx - 12, by + 70, "(full-well)", size=9, color=POS, anchor="end"))
    f.append(text(bx + bw + 12, by + 212, "тепловий шум,", size=10, color=NEG, anchor="start"))
    f.append(text(bx + bw + 12, by + 228, "завади", size=10, color=NEG, anchor="start"))

    # стрілка «динамічний діапазон» праворуч
    f.append(arrow(bx + bw + 92, by + 54, bx + bw + 92, by + 212, sw=2, ))
    f.append(arrow(bx + bw + 92, by + 212, bx + bw + 92, by + 54, sw=2))
    f.append(text(bx + bw + 100, by + 130, "динамічний", size=10.5, anchor="start", bold=True))
    f.append(text(bx + bw + 100, by + 146, "діапазон", size=10.5, anchor="start", bold=True))

    f.append(text(W / 2, H - 12,
                  "І пересвіт, і чорний провал — це втрачені назавжди дані: там просто нема чого витягати.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "saturation.svg"), W, H, *f)


# ── 5. Мозаїка Баєра: один колір на піксель → демозаїка ──────────────────────
def fig_bayer():
    W, H = 820, 380
    f = [text(W / 2, 26, "Колір: мозаїка Баєра й демозаїка", size=17, bold=True),
         text(W / 2, 47, "над кожним відерцем — один світлофільтр; решту кольорів домислюють",
              size=12, color=MUTED)]

    G = "#27ae60"
    R = "#c0392b"
    B = "#2457d6"
    # ліворуч — сітка фільтрів RGGB
    ox, oy, cell = 90, 86, 46
    pat = [[R, G], [G, B]]
    for r in range(4):
        for c in range(4):
            col = pat[r % 2][c % 2]
            x = ox + c * cell
            y = oy + r * cell
            f.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" '
                     'fill-opacity="0.85" stroke="white" stroke-width="2"/>'
                     % (x, y, cell, cell, col))
    f.append(rect(ox, oy, 4 * cell, 4 * cell, fill="none", stroke=INK, sw=1.6))
    f.append(text(ox + 2 * cell, oy - 10, "фільтри над пікселями", size=11, bold=True))
    f.append(text(ox + 2 * cell, oy + 4 * cell + 20,
                  "узор RGGB — зелених удвічі більше", size=10, color=MUTED))
    f.append(text(ox + 2 * cell, oy + 4 * cell + 36,
                  "(око чутливіше до зеленого)", size=9.5, color=MUTED))

    # стрілка
    f.append(arrow(ox + 4 * cell + 18, oy + 2 * cell, ox + 4 * cell + 70, oy + 2 * cell, sw=2.4))
    f.append(text(ox + 4 * cell + 44, oy + 2 * cell - 10, "демозаїка", size=10.5, bold=True))

    # праворуч — один піксель знає 1 колір, 2 домислює
    px = 470
    f.append(text(px + 120, oy - 10, "кожен піксель домислює 2 колори з сусідів",
                  size=11, bold=True))
    rows = [("виміряв сам", G, "зелений — є з фільтра"),
            ("домислив", R, "червоний — з сусідів-R"),
            ("домислив", B, "синій — з сусідів-B")]
    for i, (lab, col, note) in enumerate(rows):
        y = oy + 24 + i * 56
        f.append(rect(px, y, 30, 30, fill=col, stroke=INK, sw=1.3))
        f.append(text(px + 44, y + 13, lab, size=11, anchor="start", bold=True))
        f.append(text(px + 44, y + 28, note, size=10, color=MUTED, anchor="start"))
    # результат — повноколірний піксель
    f.append(text(px + 120, oy + 24 + 3 * 56 + 6,
                  "разом → повний колір RGB цього пікселя", size=10.5, color="#15803d",
                  bold=True))

    f.append(text(W / 2, H - 12,
                  "Сенсор лічить лише яскравість; колір дає мозаїка фільтрів плюс домислювання (демозаїка).",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "bayer.svg"), W, H, *f)


# ── 6. CCD проти CMOS: де перетворюють заряд на напругу ──────────────────────
def fig_ccd_vs_cmos():
    W, H = 840, 380
    f = [text(W / 2, 26, "Дві архітектури: CCD проти CMOS", size=17, bold=True),
         text(W / 2, 47, "різниця — де заряд стає напругою: один спільний вузол чи свій у кожному пікселі",
              size=12, color=MUTED)]

    def matrix(x0, y0, cell, n):
        out = []
        for r in range(n):
            for c in range(n):
                out.append(rect(x0 + c * cell, y0 + r * cell, cell - 4, cell - 4,
                                fill="#eef2f7", stroke="#9aa8bd", sw=1))
        return out

    # ── CCD ліворуч ──
    cx0, cy0, cell, n = 70, 96, 40, 4
    f.append(text(cx0 + n * cell / 2 - 8, cy0 - 12, "CCD", size=14, bold=True, color=NEG))
    f += matrix(cx0, cy0, cell, n)
    # заряд переноситься вниз стовпцями (стрілки), один вузол унизу
    for c in range(n):
        x = cx0 + c * cell + (cell - 4) / 2
        f.append(arrow(x, cy0 + n * cell - 6, x, cy0 + n * cell + 20, color=NEG, sw=1.6))
    node_y = cy0 + n * cell + 28
    f.append(rect(cx0, node_y, n * cell - 4, 30, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    f.append(text(cx0 + (n * cell) / 2 - 2, node_y + 20,
                  "один підсилювач на всіх", size=10.5, color=NEG, bold=True))
    f.append(mtext(cx0 + (n * cell) / 2 - 2, node_y + 52,
                   ["заряд переносять із пікселя в піксель,", "аж до спільного вузла → чисто, але повільно"],
                   size=9.5, color=MUTED, lh=1.35))

    # ── CMOS праворуч ──
    mx0 = 480
    f.append(text(mx0 + n * cell / 2 - 8, cy0 - 12, "CMOS", size=14, bold=True, color=POS))
    for r in range(n):
        for c in range(n):
            x = mx0 + c * cell
            y = cy0 + r * cell
            f.append(rect(x, y, cell - 4, cell - 4, fill="#fde2e2", stroke=POS, sw=1))
            # крихітний підсилювач у кутку кожного пікселя
            f.append(circle(x + cell - 11, y + 8, 3.2, fill="white", stroke=POS, sw=1.2))
    f.append(text(mx0 + n * cell / 2 - 2, cy0 + n * cell + 18,
                  "свій підсилювач у кожному пікселі", size=10.5, color=POS, bold=True))
    f.append(mtext(mx0 + n * cell / 2 - 2, cy0 + n * cell + 44,
                   ["заряд читають на місці й адресують рядок-стовпець,", "тож швидко й дешево, частина площі — на схему"],
                   size=9.5, color=MUTED, lh=1.35))

    render(os.path.join(IMG, "ccd-vs-cmos.svg"), W, H, *f)


# ── 7. Мікролінзи й квантова ефективність: щоб не губити фотони ──────────────
def fig_microlens():
    W, H = 800, 390
    f = [text(W / 2, 26, "Мікролінзи, fill factor і квантова ефективність", size=16, bold=True),
         text(W / 2, 47, "усе заради того, щоб якомога більше фотонів дали електрон",
              size=12, color=MUTED)]

    # ЛІВОРУЧ: без мікролінзи — частина світла б'є в «мертву» схему
    lx = 150
    f.append(text(lx, 80, "БЕЗ мікролінзи", size=12, bold=True))
    # фоточутлива площа (мала) + схема навколо (мертва)
    f.append(rect(lx - 70, 200, 140, 36, fill="#9aa8bd", stroke=INK, sw=1.3))
    f.append(text(lx, 222, "схема (мертва площа)", size=9, color="white", bold=True))
    f.append(rect(lx - 30, 200, 60, 36, fill="#cfe0ff", stroke=NEG, sw=1.5))
    f.append(text(lx, 254, "фотодіод", size=9.5, color=NEG))
    # промені — деякі влучають у схему (втрата)
    for dx in (-50, -18, 18, 50):
        col = NEG if abs(dx) < 30 else MUTED
        dash = None if abs(dx) < 30 else "2,4"
        f.append(line(lx + dx, 100, lx + dx, 198, color=col, sw=1.8, dash=dash))
    f.append(text(lx, 286, "частина світла гине в схемі", size=10, color=MUTED))
    f.append(text(lx, 302, "fill factor низький", size=10, color=POS, bold=True))

    # ПРАВОРУЧ: з мікролінзою — світло зведено у фотодіод
    rx = 560
    f.append(text(rx, 80, "З мікролінзою", size=12, bold=True))
    f.append(rect(rx - 70, 200, 140, 36, fill="#9aa8bd", stroke=INK, sw=1.3))
    f.append(rect(rx - 30, 200, 60, 36, fill="#cfe0ff", stroke=NEG, sw=1.5))
    # лінза — півколо зверху
    f.append('<path d="M%d 150 A 60 36 0 0 1 %d 150 Z" fill="#dcfce7" stroke="%s" stroke-width="1.6"/>'
             % (rx - 60, rx + 60, FIELD))
    f.append(text(rx, 138, "мікролінза", size=9.5, color="#15803d", bold=True))
    # промені сходяться у фотодіод
    for dx in (-50, -18, 18, 50):
        f.append(line(rx + dx, 100, rx + dx * 0.4, 150, color=NEG, sw=1.8))
        f.append(line(rx + dx * 0.4, 150, rx, 198, color=NEG, sw=1.8))
    f.append(text(rx, 286, "майже все світло — у фотодіод", size=10, color=MUTED))
    f.append(text(rx, 302, "fill factor високий", size=10, color="#15803d", bold=True))

    # внизу — визначення QE
    f.append(rect(W / 2 - 280, 326, 560, 44, fill="#f4f4f5", stroke=INK, sw=1.3, rx=8))
    f.append(text(W / 2, 344,
                  "Квантова ефективність (QE): яка частка фотонів, що дійшли, справді дала електрон.",
                  size=11, bold=True))
    f.append(text(W / 2, 362,
                  "Підсвітка ззаду (BSI) прибирає схему зі шляху світла — QE й fill factor ще вищі.",
                  size=10, color=MUTED))
    render(os.path.join(IMG, "microlens.svg"), W, H, *f)


# ╔══ Фігури до вставки 📜 hist-farnsworth ══════════════════════════════════╗

# ── h1. Ідея сканування: 2D-образ розгортають у сигнал у часі ────────────────
def fig_scanning():
    W, H = 820, 380
    f = [text(W / 2, 26, "Сканування: образ стає сигналом у часі", size=17, bold=True),
         text(W / 2, 47, "двовимірну картину розбивають на рядки й читають по черзі",
              size=12, color=MUTED)]

    # ліворуч — образ із рядками, у середині яскрава пляма
    ox, oy, ow, oh = 80, 86, 200, 200
    f.append(rect(ox, oy, ow, oh, fill="#1f2937", stroke=INK, sw=1.6))
    # яскрава пляма
    f.append(circle(ox + 120, oy + 100, 40, fill="#e5e7eb", stroke="none"))
    f.append('<circle cx="%d" cy="%d" r="40" fill="white" fill-opacity="0.5"/>'
             % (ox + 120, oy + 100))
    n = 8
    for i in range(n):
        yy = oy + 12 + i * (oh - 24) / (n - 1)
        col = POS if i == 4 else MUTED
        sw = 2.2 if i == 4 else 1
        f.append(line(ox, yy, ox + ow, yy, color=col, sw=sw, dash="3,3" if i != 4 else None))
    f.append(text(ox + ow / 2, oy - 10, "ОБРАЗ (рядки)", size=11, bold=True))
    f.append(text(ox + ow + 8, oy + 12 + 4 * (oh - 24) / (n - 1) - 4,
                  "цей рядок →", size=9.5, color=POS, anchor="start", bold=True))

    # стрілка
    f.append(arrow(ox + ow + 92, oy + oh / 2, ox + ow + 140, oy + oh / 2, sw=2.4))

    # праворуч — графік яскравості вздовж рядка: сплеск на плямі
    gx, gy, gw, gh = 500, 110, 250, 150
    f.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.5))  # вісь часу
    f.append(line(gx, gy, gx, gy + gh, color=INK, sw=1.5))            # вісь яскравості
    f.append(text(gx + gw / 2, gy + gh + 24, "час (рух уздовж рядка) →", size=10, color=MUTED))
    f.append(text(gx - 8, gy + 4, "яскравість", size=10, color=MUTED, anchor="end"))
    # крива: рівно-сплеск-рівно
    pts = []
    for i in range(51):
        t = i / 50
        import math
        y = math.exp(-((t - 0.5) ** 2) / (2 * 0.012))
        pts.append("%.1f,%.1f" % (gx + t * gw, gy + gh - 8 - y * (gh - 24)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), POS))
    f.append(text(gx + gw / 2, gy - 6, "сплеск там, де яскрава пляма", size=10, color=POS))

    f.append(text(W / 2, H - 12,
                  "Багато рядків підряд — і ціла картина стає єдиним одновимірним потоком «світло-темно».",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "scanning.svg"), W, H, *f)


# ── h2. Механічне (диск Нипкова) проти електронного скану ────────────────────
def fig_mechanical_vs_electronic():
    W, H = 820, 360
    f = [text(W / 2, 26, "Чому переміг електронний скан", size=17, bold=True),
         text(W / 2, 47, "рухомий диск повільний і тендітний; пучок електронів — ні",
              size=12, color=MUTED)]

    # ліворуч — диск Нипкова
    cx, cy, r = 220, 200, 86
    f.append(circle(cx, cy, r, fill="#eef2f7", stroke=INK, sw=1.8))
    f.append(circle(cx, cy, 8, fill="#9aa8bd", stroke=INK, sw=1.3))
    import math
    for i in range(12):
        ang = i * (2 * math.pi / 12)
        rr = r - 12 - i * 4
        hx = cx + rr * math.cos(ang)
        hy = cy + rr * math.sin(ang)
        f.append(circle(hx, hy, 4, fill="white", stroke=INK, sw=1.2))
    f.append('<path d="M%d %d A 30 30 0 0 1 %d %d" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>'
             % (cx + 30, cy - 40, cx + 44, cy - 18, MUTED))
    f.append(text(cx, cy + r + 24, "ДИСК НИПКОВА (механічне)", size=11.5, bold=True, color=MUTED))
    f.append(text(cx, cy + r + 42, "повільно, грубо, тендітно", size=10, color=POS))

    # праворуч — електронний пучок гуляє по екрану
    bx, by, bw, bh = 480, 120, 230, 150
    f.append(rect(bx, by, bw, bh, fill="#1f2937", stroke=INK, sw=1.6))
    # гармата зліва
    f.append(circle(bx - 22, by + bh / 2, 12, fill="#fde2e2", stroke=POS, sw=1.6))
    f.append(text(bx - 22, by + bh / 2 + 28, "гармата", size=9, color=POS))
    # пучок до точки + рядкова траєкторія
    tx, ty = bx + 150, by + 54
    f.append(line(bx - 10, by + bh / 2, tx, ty, color=POS, sw=2))
    f.append(circle(tx, ty, 4, fill=POS, stroke="none"))
    for i in range(3):
        yy = by + 30 + i * 40
        f.append(line(bx + 12, yy, bx + bw - 12, yy, color="#6b7280", sw=1, dash="3,3"))
    f.append(text(bx + bw / 2, by + bh + 22, "ПУЧОК ЕЛЕКТРОНІВ (електронне)",
                  size=11.5, bold=True, color="#15803d"))
    f.append(text(bx + bw / 2, by + bh + 40, "безінерційний → у тисячі разів швидше",
                  size=10, color="#15803d"))

    f.append(text(W / 2, H - 12,
                  "Електрони майже нічого не важать, тож ганяти їх можна без жодної рухомої деталі — чіткіше й надійніше.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "mechanical-vs-electronic.svg"), W, H, *f)


# ── h3. Образорозкладач: фотокатод → щілина → струм ──────────────────────────
def fig_image_dissector():
    W, H = 820, 340
    f = [text(W / 2, 26, "Образорозкладач Фарнсворта", size=17, bold=True),
         text(W / 2, 47, "образ стає електронами, що по черзі проходять крізь щілину",
              size=12, color=MUTED)]

    # лінза
    f.append('<ellipse cx="90" cy="170" rx="14" ry="48" fill="#dcfce7" stroke="%s" stroke-width="1.6"/>' % FIELD)
    f.append(text(90, 240, "лінза", size=10, color="#15803d"))
    # образ-промені у фотокатод
    for dy in (-40, 0, 40):
        f.append(line(40, 170 + dy * 0.4, 76, 170 + dy * 0.5, color="#e0a800", sw=1.8, dash="2,4"))
    # фотокатод (вертикальна пластина)
    f.append(rect(150, 110, 16, 120, fill="#cfe0ff", stroke=NEG, sw=1.6))
    f.append(text(158, 250, "фотокатод", size=10, color=NEG))
    f.append(text(158, 100, "сипле електрони", size=9, color=MUTED))
    # лінза кидає образ на фотокатод
    for dy in (-44, 0, 44):
        f.append(line(104, 170, 150, 170 + dy, color="#e0a800", sw=1.6))
    # електронний образ дрейфує праворуч до щілини
    for dy in (-40, -14, 14, 40):
        f.append(arrow(170, 170 + dy, 360, 170 + dy * 0.3, color=NEG, sw=1.5))
    f.append(text(265, 110, "електронний образ зсувають", size=10, color=MUTED))
    # щілина (вузька пластина з прорізом)
    f.append(rect(370, 110, 14, 50, fill="#9aa8bd", stroke=INK, sw=1.3))
    f.append(rect(370, 178, 14, 52, fill="#9aa8bd", stroke=INK, sw=1.3))
    f.append(text(377, 250, "щілина", size=10, bold=True))
    # крізь щілину — потік до колектора → струм
    f.append(arrow(384, 170, 470, 170, color=NEG, sw=1.8))
    f.append(rect(470, 140, 110, 60, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(525, 166, "струм =", size=12, bold=True))
    f.append(text(525, 186, "яскравість точки", size=11))
    # графік сигналу
    f.append(text(680, 120, "відеосигнал", size=11, bold=True))
    gx, gy = 620, 150
    pts = []
    import math
    for i in range(41):
        t = i / 40
        y = math.exp(-((t - 0.5) ** 2) / (2 * 0.02))
        pts.append("%.1f,%.1f" % (gx + t * 140, gy + 60 - y * 56))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join(pts), POS))
    f.append(line(gx, gy + 60, gx + 140, gy + 60, color=INK, sw=1.2))

    f.append(text(W / 2, H - 12,
                  "Скільки електронів пройшло крізь щілину тієї миті — така яскравість точки: образ став струмом у часі.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "image-dissector.svg"), W, H, *f)


# ── h4. Той самий скан сьогодні: матриця → одновимірний потік ────────────────
def fig_legacy():
    W, H = 820, 360
    f = [text(W / 2, 26, "Той самий скан сьогодні", size=17, bold=True),
         text(W / 2, 47, "кремнієва матриця читає пікселі рядок за рядком — ідея Фарнсворта в залізі",
              size=12, color=MUTED)]

    # матриця пікселів, один рядок підсвічено
    ox, oy, cell, n = 110, 90, 34, 6
    active = 2
    for r in range(n):
        for c in range(n):
            x = ox + c * cell
            y = oy + r * cell
            fill = "#fde2e2" if r == active else "#eef2f7"
            stroke = POS if r == active else "#9aa8bd"
            f.append(rect(x, y, cell - 4, cell - 4, fill=fill, stroke=stroke, sw=1.2))
    f.append(text(ox + n * cell / 2, oy - 10, "КРЕМНІЄВА МАТРИЦЯ", size=11, bold=True))
    f.append(text(ox + n * cell + 8, oy + active * cell + cell / 2 - 4,
                  "рядок, що зчитується", size=9.5, color=POS, anchor="start", bold=True))

    # стрілка зчитування → потік
    f.append(arrow(ox + n * cell + 100, oy + n * cell / 2,
                   ox + n * cell + 148, oy + n * cell / 2, sw=2.4))

    # одновимірний потік чисел
    sx = ox + n * cell + 156
    sy = oy + n * cell / 2
    vals = ["12", "44", "201", "198", "33", "..."]
    for i, v in enumerate(vals):
        f.append(rect(sx + i * 40, sy - 16, 36, 32, fill="#e9e9ef", stroke=INK, sw=1.2, rx=5))
        f.append(text(sx + i * 40 + 18, sy + 5, v, size=11, bold=True))
    f.append(text(sx + 3 * 40, sy - 28, "одновимірний потік значень", size=10.5, bold=True))
    f.append(text(sx + 3 * 40, sy + 36, "→ у дріт, радіо чи пам'ять", size=10, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "Образ → рядки → потік → канал: рівно та ідея, що Філо Фарнсворт побачив у борознах поля 1921 року.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "legacy.svg"), W, H, *f)


if __name__ == "__main__":
    fig_photoeffect()
    fig_bucket()
    fig_exposure()
    fig_saturation()
    fig_bayer()
    fig_ccd_vs_cmos()
    fig_microlens()
    # вставка hist-farnsworth
    fig_scanning()
    fig_mechanical_vs_electronic()
    fig_image_dissector()
    fig_legacy()
    print("OK: photoeffect, bucket, exposure, saturation, bayer, ccd-vs-cmos, microlens, "
          "scanning, mechanical-vs-electronic, image-dissector, legacy")
