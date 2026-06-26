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


if __name__ == "__main__":
    fig_bipolar_sine()
    fig_three_problems()
    fig_isolation_barrier()
    fig_compare_switches()
    fig_hist_timeline()
    fig_hist_latch()
    print("OK: figures written to", OUT)
