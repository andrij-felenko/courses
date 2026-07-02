# -*- coding: utf-8 -*-
"""Фігури для статті ac-switch-need («Ключі для мережі»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── bipolar-sine: синусоїда ±325 В і тонке віконце логіки 0…3.3 В ─────────────
# Ідея: показати масштаб. Робочий діапазон логіки — нескінченно тонка смужка
# біля нуля проти повного розмаху мережі майже у 650 В.
def fig_bipolar_sine():
    W, H = 720, 360
    ox, oy = 90, 170            # початок осей: нуль по вертикалі — посередині
    aw = 540                    # довжина осі часу
    amp = 120                   # амплітуда синусоїди в px (= 325 В)
    p = []

    # вісь нуля (час) і вісь напруги
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy + amp + 24, ox, oy - amp - 24, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 12, oy - amp - 18, "U", size=13, color=INK, bold=True, italic=True, anchor="end"))

    # синусоїда двох періодів
    pts = []
    for i in range(0, 401):
        t = i / 400.0
        v = math.sin(t * 2 * math.pi * 2)        # два повні періоди
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - v * amp))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), POS))

    # пік +325 і −325 — пунктирні рівні
    p.append(line(ox, oy - amp, ox + aw, oy - amp, color=MUTED, sw=1.2, dash="6 4"))
    p.append(line(ox, oy + amp, ox + aw, oy + amp, color=MUTED, sw=1.2, dash="6 4"))
    p.append(text(ox + aw + 4, oy - amp + 4, "+325 В (пік)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(ox + aw + 4, oy + amp + 4, "−325 В (пік)", size=11, color=NEG, anchor="start", bold=True))

    # рівень RMS 230 В (≈ 0.707 від піку)
    rms = amp * 0.707
    p.append(line(ox, oy - rms, ox + aw * 0.5, oy - rms, color="#3a5bb8", sw=1.0, dash="2 3"))
    p.append(text(ox + 6, oy - rms - 5, "230 В (RMS)", size=10, color="#3a5bb8", anchor="start"))

    # тонке віконце логіки 0…3.3 В біля нуля — ледь помітна зелена смужка
    band = 4
    p.append(rect(ox, oy - band, aw, band, fill="#d6f0df", stroke=FIELD, sw=1.0, rx=0))
    b, bw, bh = textbox(ox + aw * 0.30, oy + amp + 40, "усе віконце логіки 0…3.3 В — отут",
                        size=11, color=FIELD, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.4)
    p.append(b)
    p.append(arrow(ox + aw * 0.30, oy + amp + 40 - bh / 2, ox + aw * 0.30, oy - 2, color=FIELD, sw=1.4))

    render(os.path.join(OUT, "bipolar-sine.svg"), W, H, *p,
           title="Мережа — синусоїда ±325 В; логіка живе у смужці біля нуля")


# ── three-problems: три вимоги до мережевого ключа ───────────────────────────
# Ідея: три бар'єри, що по черзі виводять звичайний транзистор з гри;
# разом вони визначають окремий клас силових приладів.
def fig_three_problems():
    W, H = 760, 300
    p = []
    cards = [
        (130, "1. полярність", "синусоїда йде\nв обидва боки →\nблокувати обидва знаки", POS, "#fdecea"),
        (380, "2. напруга", "пік ±325 В проти\nдесятків вольт ключа →\nзапас до 600 В", "#b8860b", "#fdf6e3"),
        (630, "3. ізоляція", "логіка й мережа\nмусять бути\nгальванічно розділені", NEG, "#eef4ff"),
    ]
    cy = 150
    for cx, title, body, col, fill in cards:
        # заголовок-плашка
        ht, hw, hh = textbox(cx, 78, title, size=13, bold=True, color=col, fill=fill, stroke=col, sw=1.8, min_w=180)
        p.append(ht)
        # тіло
        bt, bw, bh = textbox(cx, cy + 18, body, size=11, color=INK, fill=BG, stroke="#c9d3dc", sw=1.4, min_w=190)
        p.append(bt)

    p.append(text(W / 2, H - 26, "кожна вимога окремо вже виводить за межі звичайного транзистора — "
                  "разом вони задають клас силових приладів змінного струму",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-problems.svg"), W, H, *p,
           title="Три причини, чому звичайний транзистор не пасує мережі")


# ── isolation-barrier: два світи з різним нулем і бар'єр між ними ─────────────
# Ідея: сигнал керування перетинає бар'єр (світлом/полем/зарядом), а струм і
# небезпечний потенціал — ні.
def fig_isolation_barrier():
    W, H = 760, 300
    p = []
    bx = W / 2                  # бар'єр по центру

    # дві півплощини
    p.append(rect(40, 70, bx - 40 - 14, 170, fill="#eef4ff", stroke="#c9d3dc", sw=1.4))
    p.append(rect(bx + 14, 70, W - 40 - (bx + 14), 170, fill="#fdecea", stroke="#c9d3dc", sw=1.4))
    p.append(text((40 + bx - 14) / 2, 92, "бік логіки", size=13, bold=True, color=NEG))
    p.append(text((bx + 14 + W - 40) / 2, 92, "бік мережі", size=13, bold=True, color=POS))

    # вузли лівого боку
    lb, _, _ = textbox((40 + bx - 14) / 2, 140, "МК · 3.3 В · GND\n(USB у руках)",
                       size=11, color=INK, fill=BG, stroke=NEG, sw=1.4)
    p.append(lb)
    # вузли правого боку
    rb, _, _ = textbox((bx + 14 + W - 40) / 2, 140, "силовий ключ · 230 В\nсвій «нуль» (нейтраль)",
                       size=11, color=INK, fill=BG, stroke=POS, sw=1.4)
    p.append(rb)

    # бар'єр — штрихова смуга
    p.append(line(bx, 70, bx, 240, color=MUTED, sw=2.2, dash="7 6"))
    p.append(text(bx, 60, "бар'єр ізоляції", size=12, color=MUTED, bold=True))

    # сигнал ПРОХОДИТЬ крізь бар'єр (інформація)
    p.append(arrow((40 + bx - 14) / 2 + 70, 190, (bx + 14 + W - 40) / 2 - 70, 190, color=FIELD, sw=2.2))
    p.append(text(bx, 184, "сигнал: світло / поле / заряд", size=10, color=FIELD, bold=True))

    # струм НЕ проходить — перекреслена стрілка нижче
    p.append(line(bx - 26, 218, bx + 26, 218, color=POS, sw=2.0))
    p.append(line(bx - 14, 208, bx + 14, 228, color=POS, sw=2.2))   # перекреслення
    p.append(text(bx, 245, "струм і небезпечний потенціал — ні", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 18, "пропускаємо інформацію — не пропускаємо струм",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "isolation-barrier.svg"), W, H, *p,
           title="Гальванічна розв'язка: два світи з різним нулем")


# ── compare-switches: реле vs симістор vs твердотільне реле ───────────────────
# Ідея: три способи комутувати мережу 230 В і їхні компроміси за чотирма осями,
# які власне й випливають із трьох проблем (іскріння, швидкість, dV/dt, ізоляція).
def fig_compare_switches():
    W, H = 760, 330
    p = []
    col_x = [250, 430, 610]
    heads = [("електромех.\nреле", INK), ("симістор\n(голий)", POS), ("тверд. реле\n(SSR)", FIELD)]
    rows = [
        "контакти / іскра",
        "швидкість",
        "стійкість до dV/dt",
        "вбудована ізоляція",
    ]
    # ✓ / ~ / ✗ для кожної клітинки [реле, симістор, SSR]
    cells = [
        ["іскрить, знос", "нема контактів", "нема контактів"],   # іскра
        ["мс, гуде", "пів-/такти", "пів-/такти"],                # швидкість
        ["байдуже", "вразливий", "вразливий + снабер"],          # dV/dt
        ["так (зазор)", "ні — окремо", "так (опто)"],            # ізоляція
    ]
    colors = [
        [POS, FIELD, FIELD],
        [POS, FIELD, FIELD],
        [FIELD, POS, "#b8860b"],
        [FIELD, POS, FIELD],
    ]

    y0 = 70
    rh = 52
    # заголовки колонок
    for j, (lab, col) in enumerate(heads):
        ht, _, _ = textbox(col_x[j], y0, lab, size=12, bold=True, color=col,
                           fill=BG, stroke=col, sw=1.6, min_w=150)
        p.append(ht)
    # рядки
    for i, r in enumerate(rows):
        ry = y0 + 40 + i * rh
        p.append(text(60, ry + 4, r, size=12, color=INK, anchor="start", bold=True))
        for j in range(3):
            ct, _, _ = textbox(col_x[j], ry, cells[i][j], size=10, color=colors[i][j],
                               fill=BG, stroke="#dfe3e8", sw=1.0, min_w=150)
            p.append(ct)

    p.append(text(W / 2, H - 16,
                  "реле — простий гальванічний зазор, але іскра й знос; "
                  "симістор — швидко й тихо, але без ізоляції й вразливий до dV/dt; "
                  "SSR — симістор + опторозв'язка в одному корпусі",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "compare-switches.svg"), W, H, *p,
           title="Три способи комутувати мережу 230 В")


# ════════════════════════════════════════════════════════════════════════════
# Фігури вставки hist-thyristor.md
# ════════════════════════════════════════════════════════════════════════════

# ── timeline: естафета від газового тиратрона до кремнієвого SCR ──────────────
# Ідея: дорога була не стрибком, а естафетою через дві ери — газову й кремнієву.
def fig_hist_timeline():
    W, H = 900, 470
    p = []
    ax0, ax1, ay = 70, 830, 250

    # вісь часу
    p.append(line(ax0, ay, ax1, ay, color=MUTED, sw=2.4))
    p.append(line(ax0, ay - 6, ax0, ay + 6, color=MUTED, sw=2.4))
    p.append(line(ax1, ay - 6, ax1, ay + 6, color=MUTED, sw=2.4))

    # дві ери — кольорові смуги під віссю
    GOLD = "#b8860b"
    p.append(rect(ax0, ay - 4, 360, 8, fill="#f8efd6", stroke=GOLD, sw=1.0, rx=0))
    p.append(rect(470, ay - 4, 360, 8, fill="#e9eefb", stroke=NEG, sw=1.0, rx=0))
    p.append(text(250, ay + 64, "ера газових ламп (скло, розжарений катод, ртуть)",
                  size=12, color=GOLD, bold=True))
    p.append(text(650, ay + 64, "ера кремнію (твердотільні ключі)",
                  size=12, color=NEG, bold=True))

    # віхи: (x, рік, [рядки опису], колір, текст_зверху?)
    miles = [
        (140, "~1914", ["Ленгмюр і Мікл (GE):", "кероване випрямлення", "в газовій лампі"], GOLD, True),
        (300, "~1928", ["тиратрон Голла (GE):", "сітка вмикає дугу —", "перший кер. ключ"], GOLD, False),
        (430, "1956", ["Bell Labs: PNPN-", "перемикач (Молл,", "Танненбаум, Голді,", "Голоняк)"], POS, True),
        (560, "1957", ["GE, Клайд (NY):", "+ затвор; SCR —", "Голл, Гутцвіллер;", "перші 2 шт., липень"], FIELD, False),
        (760, ">1960-ті", ["тиристор витісняє", "тиратрон; IEC:", "thyristor = thyratron", "+ transistor"], NEG, True),
    ]
    for mx, year, lines, col, up in miles:
        p.append(circle(mx, ay, 6, fill=col, stroke=col, sw=1))
        if up:
            p.append(line(mx, ay - 6, mx, ay - 12, color=col, sw=1.4, dash="3 3"))
            ty = ay - 12 - len(lines) * 14 - 8
            p.append(text(mx, ty - 2, year, size=14, color=col, bold=True))
            for i, ln in enumerate(lines):
                p.append(text(mx, ty + 14 + i * 14, ln, size=11, color=INK))
        else:
            p.append(line(mx, ay + 6, mx, ay + 20, color=col, sw=1.4, dash="3 3"))
            p.append(text(mx, ay + 96, year, size=14, color=col, bold=True))
            for i, ln in enumerate(lines):
                p.append(text(mx, ay + 112 + i * 14, ln, size=11, color=INK))

    p.append(text(W / 2, H - 18,
                  "назва thyristor зшила обидві ери: «thyra» (грец. «брама/двері») "
                  "від тиратрона + «-tor» від transistor",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "hist-timeline.svg"), W, H, *p,
           title="Силова комутація: від газової лампи до кремнію")


# ── latch: чотири шари P-N-P-N = два переплетені транзистори ──────────────────
# Ідея: фізика приладу в одній картинці — додатний зворотний зв'язок двох
# транзисторів, що тримають один одного.
def fig_hist_latch():
    W, H = 900, 430
    p = []

    # ── ліворуч: стос P-N-P-N ──
    sx, sw_, layh = 90, 120, 58
    layers = [("P", POS, "#fbecec", "анод (A)"),
              ("N", NEG, "#e9eefb", None),
              ("P", POS, "#fbecec", "затвор (G)"),
              ("N", NEG, "#e9eefb", "катод (K)")]
    ly = 70
    for lab, col, fill, tag in layers:
        p.append(rect(sx, ly, sw_, layh, fill=fill, stroke=col, sw=1.8, rx=0))
        p.append(text(sx + sw_ / 2, ly + layh / 2 + 8, lab, size=22, color=col, bold=True))
        if tag:
            yy = ly + layh / 2
            p.append(line(sx + sw_, yy, sx + sw_ + 14, yy, color=INK, sw=2))
            p.append(text(sx + sw_ + 20, yy + 5, tag, size=12, color=INK, anchor="start", bold=True))
        ly += layh
    # вивід анода зверху ліворуч
    p.append(line(sx, 70 + layh / 2, sx - 24, 70 + layh / 2, color=INK, sw=2))
    p.append(text(sx - 28, 70 + layh / 2 + 5, "анод (A)", size=12, color=INK, anchor="end", bold=True))
    p.append(text(sx + sw_ / 2, ly + 26, "чотири шари P-N-P-N", size=13, color=INK, bold=True))
    p.append(text(sx + sw_ / 2, ly + 46, "(три переходи)", size=12, color=MUTED))

    # стрілка «те саме, що»
    p.append(arrow(280, 186, 360, 186, color=INK, sw=2.4))
    p.append(text(320, 174, "те саме, що", size=12, color=INK, italic=True))

    # ── праворуч: два транзистори Q1/Q2 ──
    cx = 560
    p.append(line(cx, 80, cx, 350, color=INK, sw=2))
    p.append(circle(cx, 80, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(cx, 70, "анод (A)  +", size=13, color=POS, bold=True))
    p.append(circle(cx, 350, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(cx, 372, "катод (K)  −", size=13, color=NEG, bold=True))
    p.append(circle(cx, 150, 30, fill=BG, stroke=POS, sw=2.2))
    p.append(text(cx, 155, "Q1", size=15, color=POS, bold=True))
    p.append(text(cx + 40, 128, "PNP", size=12, color=POS, anchor="start", bold=True))
    p.append(circle(cx, 280, 30, fill=BG, stroke=NEG, sw=2.2))
    p.append(text(cx, 285, "Q2", size=15, color=NEG, bold=True))
    p.append(text(cx + 40, 306, "NPN", size=12, color=NEG, anchor="start", bold=True))

    # струм Q1 → база Q2 (праворуч)
    p.append(line(cx + 22, 170, 680, 170, color=POS, sw=2))
    p.append(line(680, 170, 680, 276, color=POS, sw=2))
    p.append(arrow(680, 276, cx + 28, 272, color=POS, sw=2))
    p.append(text(688, 209, "струм Q1", size=11, color=POS, anchor="start", bold=True))
    p.append(text(688, 225, "→ база Q2", size=11, color=POS, anchor="start"))
    # струм Q2 → база Q1 (ліворуч)
    p.append(line(cx - 22, 260, 440, 260, color=NEG, sw=2))
    p.append(line(440, 260, 440, 154, color=NEG, sw=2))
    p.append(arrow(440, 154, cx - 28, 158, color=NEG, sw=2))
    p.append(text(432, 209, "струм Q2", size=11, color=NEG, anchor="end", bold=True))
    p.append(text(432, 225, "→ база Q1", size=11, color=NEG, anchor="end"))
    # імпульс на затвор
    p.append(arrow(760, 316, 590, 292, color=FIELD, sw=2.4))
    p.append(text(764, 322, "імпульс на затвор", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(764, 338, "(одна іскра — і все)", size=11, color=FIELD, anchor="start"))

    p.append(text(W / 2, H - 16,
                  "кожен транзистор живить базу іншого: відкрився один — відкрив другий — "
                  "той ще дужче відкрив перший; раз спалахнувши, защіпка тримається сама",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "hist-latch.svg"), W, H, *p,
           title="Защіпка: чотири шари = два транзистори, що тримають один одного")


# ════════════════════════════════════════════════════════════════════════════
# Фігури ДЕТАЛЬНОЇ статті ac-switch-need-d.md
# ════════════════════════════════════════════════════════════════════════════

# ── quadrants: чотири квадранти симістора й несиметрія Q4 ─────────────────────
# Ідея: симістор двобічний, але НЕ симетричний усередині. Керуючий струм
# затвора різний у різних квадрантах; Q4 (затвор +, MT2 −) найтугіший.
def fig_quadrants():
    W, H = 720, 470
    cx, cy = 360, 235          # центр осей
    ax = 190                   # піврозмах осей (у межах канви з полями)
    p = []

    # осі: горизонталь = полярність MT2 відносно MT1, вертикаль = полярність затвора
    p.append(arrow(cx - ax - 14, cy, cx + ax + 14, cy, color=INK, sw=1.6))
    p.append(arrow(cx, cy + ax + 14, cx, cy - ax - 14, color=INK, sw=1.6))
    p.append(text(cx + ax + 8, cy + 20, "MT2 +", size=12, color=POS, anchor="end", bold=True))
    p.append(text(cx - ax - 8, cy + 20, "MT2 −", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(cx + 6, cy - ax - 4, "затвор +", size=12, color=POS, anchor="start", bold=True))
    p.append(text(cx + 6, cy + ax + 14, "затвор −", size=12, color=NEG, anchor="start", bold=True))

    # чотири плашки-квадранти: (dx, dy, підпис, IGT-нота, колір, заливка)
    q = [
        ( 1, -1, "Q1", "затвор +, MT2 +\nнайчутливіший\n(мала IGT)", FIELD, "#eafaf0"),
        (-1, -1, "Q2", "затвор −, MT2 +\nчутливий", FIELD, "#eafaf0"),
        (-1,  1, "Q3", "затвор −, MT2 −\nчутливий", FIELD, "#eafaf0"),
        ( 1,  1, "Q4", "затвор +, MT2 −\nНАЙТУГІШИЙ\nIGT × 2…3", POS, "#fdecea"),
    ]
    off = 128
    for dx, dy, lab, note, col, fill in q:
        qx, qy = cx + dx * off, cy + dy * off
        p.append(text(qx, qy - 40, lab, size=20, color=col, bold=True))
        bt, _, _ = textbox(qx, qy + 6, note, size=10, color=INK, fill=fill,
                           stroke=col, sw=1.4, min_w=150)
        p.append(bt)

    p.append(text(W / 2, H - 16,
                  "симістор двобічний, але кристал НЕ дзеркальний: Q4 просить "
                  "у 2–3 рази більший струм затвора — тому опто-драйвери уникають Q4",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "quadrants.svg"), W, H, *p,
           title="Чотири квадранти запуску симістора")


# ── latch-current: защіпка, струм утримання й провал під час нуля ─────────────
# Ідея: защіпка тримається, ПОКИ струм > I_H. Латч-струм (щоб зафіксуватися)
# більший за струм утримання. Індуктивне навантаження зсуває струм — і той
# може провалитися нижче I_H посеред півперіоду → передчасне вимкнення.
def fig_latch_current():
    W, H = 760, 380
    ox, oy = 80, 210
    aw, amp = 600, 120
    p = []

    p.append(arrow(ox, oy, ox + aw + 14, oy, color=INK, sw=1.5))
    p.append(arrow(ox, oy + amp + 20, ox, oy - amp - 40, color=INK, sw=1.5))
    p.append(text(ox + aw + 10, oy + 18, "час", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 8, oy - amp - 30, "струм у ключі", size=12, color=INK, bold=True, anchor="start"))

    # синус струму (одна півхвиля з хвостиком), зсунутий фазою (індуктивне навантаження)
    pts = []
    for i in range(0, 421):
        t = i / 420.0
        v = math.sin((t * 1.5 - 0.06) * math.pi)
        y = oy - max(v, -0.12) * amp
        pts.append("%.1f,%.1f" % (ox + t * aw, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), POS))

    # рівні латч-струму й струму утримання
    ih = oy - 0.14 * amp
    il = oy - 0.30 * amp
    p.append(line(ox, il, ox + aw, il, color=FIELD, sw=1.3, dash="6 4"))
    p.append(line(ox, ih, ox + aw, ih, color="#b8860b", sw=1.3, dash="6 4"))
    p.append(text(ox + aw + 4, il + 4, "I_латч", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(ox + aw + 4, ih + 4, "I_утрим", size=11, color="#b8860b", anchor="start", bold=True))

    # момент імпульсу на затвор
    gx = ox + aw * 0.10
    p.append(arrow(gx, oy + 70, gx, oy - 6, color=NEG, sw=2.0))
    gb, _, _ = textbox(gx + 6, oy + 92, "імпульс\nна затвор", size=10, color=NEG,
                       fill="#eaf0fd", stroke=NEG, sw=1.4)
    p.append(gb)

    # зона «нижче I_утрим → защіпка гасне»
    dx = ox + aw * 0.86
    p.append(circle(dx, oy - 0.02 * amp, 6, fill="#fff", stroke=POS, sw=2))
    db, _, _ = textbox(dx - 40, oy - amp - 8, "струм упав нижче I_утрим —\nзащіпка вимикається сама",
                       size=10, color=POS, fill="#fdecea", stroke=POS, sw=1.4)
    p.append(db)
    p.append(line(dx, oy - 0.02 * amp - 6, dx, oy - amp + 8, color=POS, sw=1.2, dash="3 3"))

    p.append(text(W / 2, H - 14,
                  "щоб зафіксуватися, струм має перевищити I_латч; далі защіпка живе, "
                  "поки струм > I_утрим — тож індуктивне навантаження, що зсуває струм, здатне вимкнути ключ зарано",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "latch-current.svg"), W, H, *p,
           title="Струм утримання й латч-струм: коли защіпка гасне")


# ── creepage: клас ізоляції — зазор у повітрі vs шлях по поверхні ─────────────
# Ідея: ізоляційний бар'єр меряють двома різними числами. Clearance — найкоротша
# пряма крізь повітря; creepage — найкоротший шлях по поверхні діелектрика.
# Проріз у платі різко подовжує creepage.
def fig_creepage():
    W, H = 760, 360
    p = []
    # плата — сірий брус
    by, bh = 150, 60
    p.append(rect(70, by, 620, bh, fill="#eef1f4", stroke="#9aa4ad", sw=1.6, rx=4))
    p.append(text(80, by + bh + 26, "друкована плата (діелектрик)", size=11, color=MUTED, anchor="start"))

    # дві мідні доріжки/виводи
    padA_x, padB_x = 210, 550
    p.append(rect(padA_x - 40, by + 12, 80, bh - 24, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    p.append(rect(padB_x - 40, by + 12, 80, bh - 24, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=3))
    p.append(text(padA_x, by - 10, "бік мережі 230 В", size=11, color=POS, bold=True))
    p.append(text(padB_x, by - 10, "бік логіки", size=11, color=NEG, bold=True))

    # clearance — пряма крізь повітря
    ay = by + bh / 2
    p.append(line(padA_x + 40, ay - 22, padB_x - 40, ay - 22, color="#b8860b", sw=2.4))
    p.append(text((padA_x + padB_x) / 2, ay - 30, "clearance — найкоротша пряма крізь повітря",
                  size=11, color="#b8860b", bold=True))

    # проріз у платі (slot), що подовжує creepage
    slot_x = (padA_x + padB_x) / 2
    p.append(rect(slot_x - 12, by - 4, 24, bh + 8, fill=BG, stroke="#9aa4ad", sw=1.4, rx=3))
    p.append(text(slot_x, by + bh + 44, "проріз у платі", size=10, color=MUTED))

    # creepage — шлях по поверхні (огинає проріз)
    cp = [(padA_x + 40, ay + 14), (slot_x - 12, ay + 14), (slot_x - 12, by + bh + 2),
          (slot_x + 12, by + bh + 2), (slot_x + 12, ay + 14), (padB_x - 40, ay + 14)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="5 3" stroke-linejoin="round"/>'
             % (" ".join("%.1f,%.1f" % (x, y) for x, y in cp), FIELD))
    p.append(text(slot_x, ay + 70, "creepage — шлях по поверхні (проріз його подовжує)",
                  size=11, color=FIELD, bold=True))

    p.append(text(W / 2, H - 14,
                  "бар'єр меряють ДВОМА числами: clearance (пробій крізь повітря) і "
                  "creepage (повзучий струм по поверхні); проріз у платі різко збільшує друге",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "creepage.svg"), W, H, *p,
           title="Ізоляційний бар'єр: clearance проти creepage")


# ── snubber: реапплай-напруга при комутації на індуктивне навантаження ────────
# Ідея: на індуктивному навантаженні струм і напруга зсунуті; коли струм падає
# до нуля й защіпка гасне, до симістора РІЗКО прикладається напруга мережі
# (комутаційний dV/dt). RC-снабер згладжує цей фронт і не дає ключу защіпнутися.
def fig_snubber():
    W, H = 760, 380
    p = []

    # ── ліворуч: схема — симістор + паралельний RC-снабер ──
    lx = 150
    p.append(line(lx, 90, lx, 300, color=INK, sw=2))       # силова гілка
    p.append(circle(lx, 90, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(lx, 78, "MT2", size=11, color=INK, bold=True))
    p.append(circle(lx, 300, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(lx, 318, "MT1", size=11, color=INK, bold=True))
    # символ симістора (два трикутники)
    p.append(rect(lx - 26, 170, 52, 50, fill=BG, stroke=POS, sw=1.8, rx=4))
    p.append(text(lx, 200, "симістор", size=10, color=POS, bold=True))
    p.append(arrow(lx - 60, 240, lx - 28, 210, color=FIELD, sw=1.8))
    p.append(text(lx - 64, 250, "затвор", size=10, color=FIELD, anchor="end"))
    # RC-снабер паралельно
    rx = lx + 70
    p.append(line(lx, 120, rx, 120, color=NEG, sw=1.6))
    p.append(line(rx, 120, rx, 160, color=NEG, sw=1.6))
    p.append(rect(rx - 10, 160, 20, 34, fill=BG, stroke=NEG, sw=1.6, rx=2))   # R
    p.append(text(rx + 16, 180, "R", size=12, color=NEG, anchor="start", bold=True))
    p.append(line(rx, 194, rx, 210, color=NEG, sw=1.6))
    p.append(line(rx - 12, 210, rx + 12, 210, color=NEG, sw=2.2))             # C
    p.append(line(rx - 12, 216, rx + 12, 216, color=NEG, sw=2.2))
    p.append(text(rx + 16, 220, "C", size=12, color=NEG, anchor="start", bold=True))
    p.append(line(rx, 216, rx, 270, color=NEG, sw=1.6))
    p.append(line(lx, 270, rx, 270, color=NEG, sw=1.6))
    p.append(text(lx + 40, 300, "RC-снабер", size=11, color=NEG, bold=True))

    # ── праворуч: напруга на ключі в момент вимкнення ──
    ox, oy = 380, 200
    aw, amp = 330, 90
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=INK, sw=1.5))
    p.append(arrow(ox, oy + 40, ox, oy - amp - 30, color=INK, sw=1.5))
    p.append(text(ox + aw + 8, oy + 18, "час", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 6, oy - amp - 20, "напруга на ключі", size=11, color=INK, bold=True, anchor="start"))

    # без снабера — різкий стрибок (крутий фронт)
    tx = ox + aw * 0.42
    p.append(line(ox, oy, tx, oy, color=POS, sw=2.4))
    p.append(line(tx, oy, tx, oy - amp, color=POS, sw=2.4))
    p.append(line(tx, oy - amp, ox + aw, oy - amp, color=POS, sw=2.4))
    p.append(text(tx + 4, oy - amp - 6, "без снабера: крутий dV/dt → хибний запуск",
                  size=10, color=POS, anchor="start", bold=True))

    # зі снабером — плавний фронт (RC-експонента)
    ep = []
    for i in range(0, 201):
        t = i / 200.0
        x = tx + t * (aw * 0.5)
        v = amp * (1 - math.exp(-t * 3.2))
        ep.append("%.1f,%.1f" % (x, oy - v))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(ep), FIELD))
    p.append(text(tx + 4, oy + 22, "зі снабером: пологий фронт", size=10, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, H - 14,
                  "при вимкненні на індуктивному навантаженні напруга мережі "
                  "прикладається до ключа РІЗКО; RC-снабер розтягує фронт (τ = R·C) і не дає dV/dt защіпнути симістор",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "snubber.svg"), W, H, *p,
           title="RC-снабер проти комутаційного dV/dt")


# ── phase-timing: перехід нуля → затримка → імпульс на затвор ────────────────
# Ідея: показати повний ланцюг подій одного півперіоду 10 мс (50 Гц):
# синусоїда → мітка нуля → відлічена затримка t_fire → короткий імпульс →
# симістор проводить залишок півхвилі (зафарбована частина = середня потужність).
def fig_phase_timing():
    W, H = 720, 400
    ox, oy = 70, 130           # осі синусоїди: нуль по вертикалі
    aw = 600                   # два півперіоди по осі часу
    amp = 78
    half = aw / 2.0            # ширина одного півперіоду (10 мс)
    a = 0.42                   # частка півперіоду до запуску (кут ~75°)
    p = []

    # синусоїда (модуль — обидва півперіоди вгору, як «поточна півхвиля»)
    pts = []
    for i in range(0, 601):
        t = i / 600.0
        v = abs(math.sin(t * 2 * math.pi))
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - v * amp))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'stroke-dasharray="4 3" stroke-linejoin="round"/>' % (" ".join(pts), MUTED))

    # вісь часу
    p.append(arrow(ox, oy, ox + aw + 14, oy, color=INK, sw=1.5))
    p.append(text(ox + aw + 10, oy + 18, "час", size=11, color=INK, italic=True, anchor="end"))

    # зафарбувати провідну частину кожного півперіоду (від t_fire до кінця)
    for k in range(2):
        base = ox + k * half
        xf = base + a * half
        fill_pts = ["%.1f,%.1f" % (xf, oy)]
        n = 60
        for i in range(0, n + 1):
            tt = a + (1 - a) * i / n
            v = abs(math.sin(tt * math.pi))
            fill_pts.append("%.1f,%.1f" % (base + tt * half, oy - v * amp))
        fill_pts.append("%.1f,%.1f" % (base + half, oy))
        p.append('<polygon points="%s" fill="%s" fill-opacity="0.22" stroke="none"/>'
                 % (" ".join(fill_pts), POS))
        # крива провідної частини — суцільна червона
        cl = []
        for i in range(0, n + 1):
            tt = a + (1 - a) * i / n
            v = abs(math.sin(tt * math.pi))
            cl.append("%.1f,%.1f" % (base + tt * half, oy - v * amp))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-linejoin="round"/>' % (" ".join(cl), POS))

    # мітки переходу нуля (0, 10, 20 мс) — вертикальні пунктири
    for k, lbl in ((0, "0"), (1, "10"), (2, "20")):
        x = ox + k * half
        p.append(line(x, oy + 96, x, oy - amp - 8, color=NEG, sw=1.3, dash="3 3"))
        p.append(text(x, oy + 112, lbl + " мс", size=10, color=NEG, bold=True))

    # доріжка сигналу ZCD (перехід нуля з детектора) — імпульси на нулях
    zy = oy + 150
    p.append(text(ox - 8, zy - 14, "ZCD (нуль)", size=10, color=NEG, anchor="start", bold=True))
    p.append(line(ox, zy, ox + aw, zy, color=MUTED, sw=1.2))
    for k in range(3):
        x = ox + k * half
        p.append(line(x - 3, zy, x - 3, zy - 20, color=NEG, sw=2))
        p.append(line(x - 3, zy - 20, x + 3, zy - 20, color=NEG, sw=2))
        p.append(line(x + 3, zy - 20, x + 3, zy, color=NEG, sw=2))

    # доріжка імпульсу на затвор — короткий сплеск через t_fire після кожного нуля
    gy = oy + 210
    p.append(text(ox - 8, gy - 14, "затвор", size=10, color=POS, anchor="start", bold=True))
    p.append(line(ox, gy, ox + aw, gy, color=MUTED, sw=1.2))
    for k in range(2):
        xf = ox + k * half + a * half
        w = 8
        p.append(line(xf, gy, xf, gy - 22, color=POS, sw=2.2))
        p.append(line(xf, gy - 22, xf + w, gy - 22, color=POS, sw=2.2))
        p.append(line(xf + w, gy - 22, xf + w, gy, color=POS, sw=2.2))
        # стрілка затримки від нуля до імпульсу
        base = ox + k * half
        p.append(line(base, gy + 14, xf, gy + 14, color=INK, sw=1.2))
        p.append(line(base, gy + 10, base, gy + 18, color=INK, sw=1.2))
        p.append(line(xf, gy + 10, xf, gy + 18, color=INK, sw=1.2))
        p.append(text((base + xf) / 2, gy + 30, "t_fire", size=10, color=INK, italic=True))

    p.append(text(W / 2, H - 12,
                  "нуль → відлічити t_fire → коротко смикнути затвор → симістор проводить "
                  "залишок півхвилі (зафарбовано); більша t_fire → менша площа → менша потужність",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "phase-timing.svg"), W, H, *p,
           title="Фазове керування: ланцюг подій одного півперіоду")


# ── phase-power: залежність середньої потужності від кута відкриття ───────────
# Ідея: зв'язок НЕЛІНІЙНИЙ. P(α)/Pmax = (1/π)·[(π−α) + ½·sin(2α)] для резистора.
# Найкрутіша ділянка — біля 90° (середина півхвилі), де синус найбільший.
def fig_phase_power():
    W, H = 640, 380
    ox, oy = 90, 300
    aw, ah = 470, 235
    p = []

    p.append(arrow(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 14, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 24, "кут відкриття α", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 60, oy - ah + 4, "P / Pmax", size=12, color=INK, bold=True, anchor="start"))

    def px(alpha):     # alpha у радіанах 0..π
        return ox + (alpha / math.pi) * aw

    def py(frac):      # frac 0..1
        return oy - frac * ah

    # крива потужності для активного навантаження
    cl = []
    for i in range(0, 201):
        al = i / 200.0 * math.pi
        frac = (1.0 / math.pi) * ((math.pi - al) + 0.5 * math.sin(2 * al))
        cl.append("%.1f,%.1f" % (px(al), py(frac)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(cl), POS))

    # сітка: 0, 90, 180 по X; 0, 50, 100% по Y
    for al, lbl in ((0, "0°"), (math.pi / 2, "90°"), (math.pi, "180°")):
        x = px(al)
        p.append(line(x, oy, x, oy + 6, color=INK, sw=1.4))
        p.append(text(x, oy + 22, lbl, size=11, color=INK))
    for fr, lbl in ((0.0, "0"), (0.5, "50%"), (1.0, "100%")):
        y = py(fr)
        p.append(line(ox - 6, y, ox, y, color=INK, sw=1.4))
        p.append(text(ox - 12, y + 4, lbl, size=11, color=INK, anchor="end"))
        p.append(line(ox, y, ox + aw, y, color=MUTED, sw=0.8, dash="2 4"))

    # позначити середину (90°) — найкрутіша ділянка, 50 % потужності
    xm, ym = px(math.pi / 2), py(0.5)
    p.append(circle(xm, ym, 4.5, fill=POS, stroke=POS, sw=1))
    p.append(line(xm, ym, xm + 70, ym - 40, color=INK, sw=1))
    b, bw, bh = textbox(xm + 132, ym - 58, "90° → 50 %\nтут крива найкрутіша",
                        size=10, fill=BG, stroke=INK, bold=True)
    p.append(b)

    # затінити «мертві» краї, де регулювання майже не працює
    p.append(text(px(0.28), py(0.96), "мала α: майже\nповна потужність",
                  size=9, color=MUTED, anchor="middle"))
    p.append(text(px(math.pi - 0.5), py(0.10), "велика α:\nмайже нуль",
                  size=9, color=MUTED, anchor="middle"))

    p.append(text(W / 2, H - 10,
                  "зв'язок кута з потужністю НЕЛІНІЙНИЙ: рівні кроки α дають нерівні кроки P; "
                  "найчутливіша ділянка — біля 90°",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "phase-power.svg"), W, H, *p,
           title="Потужність від кута відкриття (активне навантаження)")


# ════════════════════════════════════════════════════════════════════════════
# Фігури вставки math-latch.md (механіка защіпки, повне виведення)
# ════════════════════════════════════════════════════════════════════════════

# ── latch-kcl: два транзистори з ПОМІЧЕНИМИ струмами, що їх додає KCL ──────────
# Ідея: qualitative-картинка защіпки вже є в hist-latch; тут — БУХГАЛТЕРІЯ
# виведення. Крізь прилад тече спільний I_A (він же емітерний для обох).
# Колектор Q1 віддає α1·I_A + I_CO1, колектор Q2 віддає α2·I_A + I_CO2; на
# катодному вузлі KCL: α1·I_A + I_CO1 + α2·I_A + I_CO2 (+ I_G) = I_A.
def fig_latch_kcl():
    W, H = 780, 450
    p = []

    cx = 300
    top, bot = 74, 360
    # силова вісь анод→катод
    p.append(line(cx, top, cx, bot, color=INK, sw=2))
    p.append(circle(cx, top, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(cx, top - 12, "анод A  (+)", size=13, color=POS, bold=True))
    p.append(circle(cx, bot, 4, fill=INK, stroke=INK, sw=1))
    p.append(text(cx, bot + 24, "катод K  (−)", size=13, color=NEG, bold=True))

    # спільний анодний струм I_A згори
    p.append(arrow(cx - 50, top + 8, cx - 50, top + 54, color=INK, sw=2.2))
    p.append(text(cx - 56, top + 32, "I_A", size=14, color=INK, anchor="end", bold=True))
    p.append(text(cx - 56, top + 48, "(спільний)", size=10, color=MUTED, anchor="end"))

    # Q1 (PNP) угорі, Q2 (NPN) унизу
    p.append(circle(cx, 158, 32, fill=BG, stroke=POS, sw=2.2))
    p.append(text(cx, 155, "Q1", size=16, color=POS, bold=True))
    p.append(text(cx, 173, "PNP", size=11, color=POS))
    p.append(circle(cx, 278, 32, fill=BG, stroke=NEG, sw=2.2))
    p.append(text(cx, 275, "Q2", size=16, color=NEG, bold=True))
    p.append(text(cx, 293, "NPN", size=11, color=NEG))

    # колекторний струм Q1 → база Q2 (праворуч): α1·I_A + I_CO1
    rx = 468
    p.append(line(cx + 24, 171, rx, 171, color=POS, sw=2))
    p.append(line(rx, 171, rx, 265, color=POS, sw=2))
    p.append(arrow(rx, 265, cx + 26, 265, color=POS, sw=2))
    b, bw, bh = textbox(rx + 96, 205, "колектор Q1\nα₁·I_A + I_CO1",
                        size=12, color=POS, fill="#fdecea", stroke=POS, sw=1.6, bold=True)
    p.append(b)
    p.append(line(rx, 205, rx + 96 - bw / 2, 205, color=POS, sw=1.2, dash="3 3"))

    # колекторний струм Q2 → база Q1 (ліворуч): α2·I_A + I_CO2
    lx = 132
    p.append(line(cx - 24, 265, lx, 265, color=NEG, sw=2))
    p.append(line(lx, 265, lx, 171, color=NEG, sw=2))
    p.append(arrow(lx, 171, cx - 26, 171, color=NEG, sw=2))
    b, bw, bh = textbox(lx - 8, 213, "колектор Q2\nα₂·I_A + I_CO2",
                        size=12, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.6, bold=True)
    p.append(b)

    # струм затвора I_G у базу Q2 (знизу-праворуч, зелений)
    p.append(arrow(cx + 104, 332, cx + 30, 302, color=FIELD, sw=2.2))
    p.append(text(cx + 108, 336, "I_G (пуск)", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(cx + 108, 352, "у базу Q2", size=10, color=FIELD, anchor="start"))

    # KCL-рамка на катодному вузлі
    p.append(fitbox(cx - 200, bot + 40, 400, 44,
                    "KCL:  α₁·I_A + α₂·I_A + I_CO + I_G = I_A",
                    size=14, color=INK, fill=FILL, stroke=INK, sw=1.6, bold=True))

    p.append(text(W / 2, H - 12,
                  "усе виведення — це KCL на одному вузлі: сума колекторних струмів обох "
                  "транзисторів плюс витік і затвор дорівнює спільному I_A",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "latch-kcl.svg"), W, H, *p,
           title="Струми в защіпці: що саме додає KCL")


# ── loop-gain-alpha: α(I) росте + вибух I_A = I_CO/(1−(α1+α2)) на межі ────────
# Ідея: ліва панель — чому α росте зі струмом (за малих струмів рекомбінація
# з'їдає підсилення); права панель — та сама дріб 1/(1−Σα) з полюсом у Σα=1,
# на якій позначено, де сидять I_H (спуск нижче 1) та I_L (підйом до 1).
def fig_loop_gain_alpha():
    W, H = 860, 410
    p = []

    # ── ЛІВА ПАНЕЛЬ: α проти струму емітера ──
    ox, oy = 74, 300
    aw, ah = 300, 200
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 14, color=INK, sw=1.6))
    p.append(text(ox + aw + 8, oy + 20, "струм I (лог.)", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 6, oy - ah - 20, "α = β/(β+1)", size=12, color=INK, bold=True, anchor="start"))

    # рівень α=1 (пунктир)
    p.append(line(ox, oy - ah, ox + aw, oy - ah, color=MUTED, sw=1.0, dash="5 4"))
    p.append(text(ox + aw + 4, oy - ah + 4, "α = 1", size=10, color=MUTED, anchor="start"))

    # крива α(I): мала за малих I, росте й насичується
    pts = []
    for i in range(0, 301):
        t = i / 300.0
        a = 0.05 + 0.9 / (1 + math.exp(-(t - 0.42) * 11))
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - a * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts), POS))

    # зона малих струмів — рекомбінація з'їдає α
    p.append(rect(ox, oy - 0.24 * ah, aw * 0.26, 0.24 * ah, fill="#fbecec", stroke="none", sw=0))
    b, bw, bh = textbox(ox + aw * 0.56, oy - ah * 0.34, "за малих струмів\nрекомбінація\nз'їдає підсилення",
                        size=10, color=INK, fill="#fff6f6", stroke=POS, sw=1.2)
    p.append(b)
    p.append(text(ox + aw * 0.5, oy + 40, "α РОСТЕ зі струмом", size=11, color=POS, bold=True))

    # ── ПРАВА ПАНЕЛЬ: вибух I_A = I_CO/(1−Σα) ──
    ox2, oy2 = 480, 300
    aw2, ah2 = 320, 200
    p.append(arrow(ox2, oy2, ox2 + aw2 + 12, oy2, color=INK, sw=1.6))
    p.append(arrow(ox2, oy2, ox2, oy2 - ah2 - 14, color=INK, sw=1.6))
    p.append(text(ox2 + aw2 + 8, oy2 + 20, "Σα = α₁+α₂", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox2 - 6, oy2 - ah2 - 20, "I_A", size=13, color=INK, bold=True, italic=True, anchor="start"))

    # вертикальна асимптота Σα → 1
    ax = ox2 + aw2 * 0.9
    p.append(line(ax, oy2, ax, oy2 - ah2 - 8, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(ax + 4, oy2 - ah2 + 6, "Σα → 1", size=10, color=MUTED, anchor="start"))
    p.append(text(ax + 4, oy2 - ah2 + 20, "полюс", size=10, color=MUTED, anchor="start"))

    # крива 1/(1−Σα)
    cp = []
    for i in range(0, 289):
        s = (i / 320.0) * 0.9
        val = 1.0 / (1.0 - s)
        yv = min(val * 11, ah2)
        cp.append("%.1f,%.1f" % (ox2 + (s / 0.9) * (aw2 * 0.9), oy2 - yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(cp), INK))

    # витік біля Σα≈0
    p.append(circle(ox2 + 2, oy2 - 11, 3, fill=INK, stroke=INK, sw=1))
    p.append(text(ox2 + 8, oy2 - 5, "закрито: I_A ≈ I_CO (витік)", size=10, color=INK, anchor="start"))

    # позначки I_H та I_L на осі Σα
    xh = ox2 + (0.72 / 0.9) * (aw2 * 0.9)
    xl = ox2 + (0.82 / 0.9) * (aw2 * 0.9)
    p.append(line(xh, oy2, xh, oy2 + 10, color=NEG, sw=2))
    p.append(text(xh, oy2 + 24, "I_H", size=12, color=NEG, bold=True))
    p.append(line(xl, oy2, xl, oy2 + 10, color=FIELD, sw=2))
    p.append(text(xl, oy2 + 40, "I_L", size=12, color=FIELD, bold=True))
    b, bw, bh = textbox(ox2 + aw2 * 0.46, oy2 - ah2 * 0.82, "I_L > I_H:\nфіксуватися важче,\nніж утриматися",
                        size=10, color=INK, fill=FILL, stroke=INK, sw=1.2)
    p.append(b)

    p.append(text(W / 2, H - 10,
                  "α росте зі струмом (ліворуч) → сума наближається до 1 → дріб 1/(1−Σα) вибухає (праворуч); "
                  "I_L — де Σα уперше сягає 1, I_H — де знову падає нижче",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "loop-gain-alpha.svg"), W, H, *p,
           title="Чому защіпка спалахує: α(I) і полюс 1/(1−Σα)")


if __name__ == "__main__":
    fig_bipolar_sine()
    fig_three_problems()
    fig_isolation_barrier()
    fig_compare_switches()
    fig_hist_timeline()
    fig_hist_latch()
    fig_quadrants()
    fig_latch_current()
    fig_creepage()
    fig_snubber()
    fig_phase_timing()
    fig_phase_power()
    fig_latch_kcl()
    fig_loop_gain_alpha()
    print("OK: figures written to", OUT)
