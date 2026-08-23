# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Проєктування антиаліасингового фільтра».
Запуск:  python figs.py   → пише SVG у ./img/
Помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

import math

W, H = 770, 480


# ───────────────────── 1. Затиск: стіна Найквіста проти смуги ────────────────
def fig_squeeze():
    """Антиаліасний затиск: смуга сигналу fp задана зовні, а край затримання
    мусить упертися в стіну fs/2. Близька fs → крихітний перехід → шалений порядок;
    піднята fs → широкий перехід → дешева RC."""
    f = []
    f.append(text(W / 2, 28, "Затиск антиаліасу: перехід мусить влізти між fp і fs/2",
                  size=17, bold=True))

    # дві панелі: ліва (fs впритул) і права (fs піднята)
    panels = [
        (40, "fs впритул до сигналу", 0.5 * 240, "крихітний перехід →\nпорядок шалений", POS, 8),
        (415, "fs піднята (×4)", 0.5 * 600, "широкий перехід →\nвистачить однієї RC", FIELD, 1),
    ]
    PW = 320
    TOP, BOT = 96, 330
    for (px, title, nyq_px, verdict, vcol, order) in panels:
        L = px + 14
        R = px + PW - 14
        # осі
        f.append(text(px + PW / 2, 56, title, size=13, bold=True, color=INK))
        f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.5))
        f.append(line(L, BOT, R, BOT, color=INK, sw=1.5))
        f.append(text(L - 6, TOP - 12, "|H|", size=11, color=MUTED, anchor="middle"))
        f.append(text(R, BOT + 30, "частота →", size=10.5, color=MUTED, anchor="end"))

        # положення країв: fp фіксований (однаковий у px-координатах),
        # стіна Найквіста fs/2 — близько / далеко
        fp_x = L + 0.30 * (R - L)
        if order == 8:      # ліва панель: стіна близько
            nyq_x = L + 0.46 * (R - L)
        else:               # права: стіна далеко
            nyq_x = L + 0.86 * (R - L)

        # смуга пропускання (зелена) до fp
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" '
                 'opacity="0.14"/>' % (L, TOP, fp_x - L, BOT - TOP))
        # перехідна смуга (жовта) fp..fs/2 — оце і є те, що треба «влізти»
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f4d35e" '
                 'opacity="0.40"/>' % (fp_x, TOP, nyq_x - fp_x, BOT - TOP))
        # заборонена зона за стіною (червона): усе вище fs/2 складеться вниз
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
                 'opacity="0.6"/>' % (nyq_x, TOP, R - nyq_x, BOT - TOP))

        # стіна Найквіста
        f.append(line(nyq_x, TOP - 6, nyq_x, BOT + 4, color=POS, sw=2.4))
        f.append(text(nyq_x, TOP - 12, "fs/2", size=11.5, color=POS, bold=True))
        f.append(line(fp_x, TOP - 2, fp_x, BOT, color=NEG, sw=1.4, dash="4,3"))
        f.append(text(fp_x, BOT + 14, "fp", size=11, color=NEG, bold=True))

        # крива фільтра, що мусить упасти від ~1 (на fp) до низу (на fs/2)
        pts = []
        N = 100
        for i in range(N + 1):
            x = L + (R - L) * i / N
            t = (x - L) / (R - L)
            fp_t = (fp_x - L) / (R - L)
            nq_t = (nyq_x - L) / (R - L)
            if t <= fp_t:
                yv = 1.0 - 0.04 * (t / max(fp_t, 1e-6))
            elif t <= nq_t:
                u = (t - fp_t) / (nq_t - fp_t)
                # порядок задає крутість: вищий order → крутіше падіння
                steep = 1.5 if order == 8 else 4.5
                yv = (1.0) * (1.0 - u) ** steep
            else:
                yv = 0.02
            yy = BOT - yv * (BOT - TOP) * 0.92
            pts.append("%.1f,%.1f" % (x, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), INK))

        # вердикт + порядок
        f.append(fitbox(L, BOT + 36, R - L, 70, verdict + "\nпорядок ≈ %d" % order,
                        size=12, fill="#f7f9fb", stroke=vcol, bold=False))

    f.append(text(W / 2, 466, "fp задає сигнал; fs/2 — стіна, яку не перейти. "
                  "Єдина зручна ручка — підняти fs і відсунути стіну.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "squeeze.svg"), W, H, *f)


# ───────────────────── 2. Що пролазить: складання назад у смугу ──────────────
def fig_fold():
    """Недостатнє придушення на fs/2: «хвіст» спектра за стіною складається вниз
    і сідає просто в захищену смугу [0..fp]. Видно зону-байдужість fp..fs/2."""
    f = []
    f.append(text(W / 2, 28, "Чого боїмося: хвіст за fs/2 складається назад у смугу",
                  size=17, bold=True))

    L, R = 80, 700
    TOP, BOT = 84, 300

    fp_x = L + 0.22 * (R - L)
    nyq_x = L + 0.50 * (R - L)
    # дзеркальна точка: частота fa = fs - f, для f трохи вище fs/2 падає трохи нижче fs/2
    src_x = nyq_x + 0.18 * (R - L)         # завада за стіною
    img_x = nyq_x - (src_x - nyq_x)        # її дзеркальний аліас (нижче fs/2)

    # зони
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" '
             'opacity="0.12"/>' % (L, TOP, fp_x - L, BOT - TOP))           # захищена смуга
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f4d35e" '
             'opacity="0.28"/>' % (fp_x, TOP, nyq_x - fp_x, BOT - TOP))    # байдужа зона
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef1f4" '
             'opacity="0.7"/>' % (nyq_x, TOP, R - nyq_x, BOT - TOP))       # за стіною

    # осі
    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.5))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.5))
    f.append(text(R, BOT + 30, "частота →", size=11, color=MUTED, anchor="end"))

    # стіна
    f.append(line(nyq_x, TOP - 8, nyq_x, BOT + 4, color=POS, sw=2.4))
    f.append(text(nyq_x, TOP - 14, "fs/2 (дзеркало)", size=12, color=POS, bold=True))
    f.append(line(fp_x, TOP - 2, fp_x, BOT, color=NEG, sw=1.3, dash="4,3"))
    f.append(text(fp_x, BOT + 14, "fp", size=11, color=NEG, bold=True))
    f.append(text(L + (fp_x - L) / 2, TOP - 12, "захищена", size=10.5,
                  color=FIELD, bold=True))
    f.append(text((fp_x + nyq_x) / 2, BOT + 14, "байдужа зона", size=10,
                  color="#9a7d0a", anchor="middle"))

    # завада-хвіст за стіною (сірий пік)
    f.append(line(src_x, BOT, src_x, TOP + 40, color=MUTED, sw=3))
    f.append(circle(src_x, TOP + 40, 4, fill=MUTED, stroke=BG))
    f.append(text(src_x, TOP + 30, "залишок ВЧ-шуму", size=10.5, color=MUTED, anchor="middle"))

    # дуга відбиття від стіни
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#arrow)"/>'
             % (src_x, TOP + 50, nyq_x, TOP + 12, img_x, TOP + 78, POS))

    # аліас, що сів у захищену смугу — АЛЕ тут img_x у байдужій зоні; зробимо ще одну
    # завада дзеркалить у байдужу — нестрашно. Покажемо ДРУГУ заваду, ближчу до fs,
    # що дзеркалить у захищену смугу.
    src2_x = R - 0.10 * (R - L)
    img2_x = nyq_x - (src2_x - nyq_x)
    f.append(line(src2_x, BOT, src2_x, TOP + 70, color=MUTED, sw=3))
    f.append(text(src2_x, TOP + 60, "ще вищий шум", size=10, color=MUTED, anchor="middle"))
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (src2_x, TOP + 80, nyq_x + 30, TOP + 4, img2_x, TOP + 56, POS))
    f.append(line(img2_x, BOT, img2_x, TOP + 56, color=POS, sw=3))
    f.append(circle(img2_x, TOP + 56, 4.5, fill=POS, stroke=BG))
    f.append(text(img2_x, TOP + 46, "аліас у смузі!", size=10.5, color=POS, bold=True, anchor="middle"))

    f.append(fitbox(L, 338, R - L, 96,
                    "Усе, що фільтр не дотиснув вище fs/2, дзеркалиться вниз. Шум, що падає в "
                    "БАЙДУЖУ зону (fp..fs/2),\nне страшний — там корисного немає, його однаково "
                    "виріже наступний цифровий фільтр. А от шум, що\nсклався в ЗАХИЩЕНУ смугу "
                    "[0..fp], — катастрофа: він невідрізнянний від сигналу назавжди.\n"
                    "Тому АА-фільтр має забезпечити потрібне придушення САМЕ на fs/2 і вище — "
                    "не нижче.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "fold-into-band.svg"), W, H, *f)


# ───────────────────── 3. Передискретизація + проріджування ──────────────────
def fig_oversample():
    """Виграшний конвеєр: дешева RC → швидкий АЦП на M·fs → крутий цифровий ФНЧ →
    проріджування до fs. Аналогову стіну відсунули, тягар переклали в код."""
    f = []
    f.append(text(W / 2, 28, "Виграш: оцифровуй швидко, ріж круто в коді, проріджуй",
                  size=17, bold=True))

    y = 120
    boxes = [
        (118, ["джерело", "+ дешева", "RC (1-й пор.)"], "#f7f9fb", MUTED),
        (320, ["АЦП", "на M·fs", "(швидко)"], "#eef2ff", NEG),
        (522, ["цифровий", "крутий ФНЧ", "(зріз ≈ fp)"], "#eafaf0", FIELD),
        (690, ["проріджу-", "вання ÷M", "→ вихід fs"], "#fff8e1", "#9a7d0a"),
    ]
    coords = []
    for (x, lines, fill, stroke) in boxes:
        b, bw, bh = textbox(x, y, lines, size=12.5, bold=True, fill=fill, stroke=stroke, pad=11)
        coords.append((x, bw))
        f.append(b)
    for i in range(len(coords) - 1):
        x1, w1 = coords[i]; x2, w2 = coords[i + 1]
        f.append(arrow(x1 + w1 / 2 + 3, y, x2 - w2 / 2 - 3, y, color=INK, sw=2.0))

    # вісь частот унизу: де стоїть стіна за швидкої fs
    L, R = 80, 700
    AY = 250
    f.append(line(L, AY, R, AY, color=INK, sw=1.4))
    f.append(text(R, AY + 22, "частота →", size=10.5, color=MUTED, anchor="end"))
    fp_x = L + 0.12 * (R - L)
    nyq_lo = L + 0.24 * (R - L)      # стара стіна fs/2 (повільна fs)
    nyq_hi = L + 0.92 * (R - L)      # нова стіна M·fs/2 (швидка fs)

    f.append(line(fp_x, AY - 8, fp_x, AY + 8, color=NEG, sw=2))
    f.append(text(fp_x, AY + 22, "fp", size=10.5, color=NEG, bold=True))
    f.append(line(nyq_lo, AY - 30, nyq_lo, AY + 8, color="#9a7d0a", sw=1.6, dash="3,3"))
    f.append(text(nyq_lo, AY - 36, "fs/2 (ціль)", size=10, color="#9a7d0a", bold=True, anchor="middle"))
    f.append(line(nyq_hi, AY - 46, nyq_hi, AY + 8, color=POS, sw=2.4))
    f.append(text(nyq_hi, AY - 52, "M·fs/2 (нова стіна)", size=10.5, color=POS, bold=True, anchor="middle"))

    # величезний перехід між fp і новою стіною
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f4d35e" '
             'opacity="0.30"/>' % (fp_x, AY - 18, nyq_hi - fp_x, 18))
    f.append('<path d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="1.6" '
             'marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
             % (fp_x + 4, AY - 26, nyq_hi - 4, AY - 26, "#9a7d0a"))
    f.append(text((fp_x + nyq_hi) / 2, AY - 30,
                  "тепер до стіни — океан місця: RC 1-го порядку встигає зрізати",
                  size=10.5, color="#9a7d0a", anchor="middle"))

    f.append(fitbox(L, 290, R - L, 150,
                    "Ключ — НЕ робити круту аналогову стіну, а ВІДСУНУТИ її. Беремо відліки в "
                    "M разів частіше (M = 4..256):\n"
                    "стіна Найквіста стрибає з fs/2 на M·fs/2, і між корисною смугою й нею "
                    "лишається океан місця —\n"
                    "де навіть млява RC 1-го порядку встигає зрізати ВЧ-шум до безпечного. "
                    "Усю круту роботу робить уже\n"
                    "ЦИФРОВИЙ фільтр (його легко зробити будь-яким крутим — він безкоштовний у "
                    "залізі), а тоді сигнал\n"
                    "ПРОРІДЖУЮТЬ назад до потрібної fs. Бонус: усереднення M відліків додає "
                    "≈ log4(M) «чесних» біт.",
                    size=12, fill="#f7f9fb", stroke=FIELD))
    render(os.path.join(OUT, "oversample-decimate.svg"), W, H, *f)


# ───────────────────── 4. Бюджет однієї RC: скільки дБ на fs/2 ───────────────
def fig_rc_budget():
    """Коли вистачає однієї RC: |H| RC у дБ, і скільки вона дає на fs/2 залежно від
    того, як далеко fs/2 від зрізу fc. Видно, що ÷10 за частотою = −20 дБ."""
    f = []
    f.append(text(W / 2, 28, "Скільки дає одна RC на стіні: відношення fs/2 до зрізу",
                  size=17, bold=True))

    L, R = 92, 712
    TOP, BOT = 70, 350
    DBSPAN = 60.0

    def ydb(db):
        return TOP + (-db) * (BOT - TOP) / DBSPAN

    xmin, xmax = math.log10(0.5), math.log10(100.0)

    def xof(r):    # r = f/fc
        return L + (math.log10(r) - xmin) * (R - L) / (xmax - xmin)

    # сітка дБ
    for db in (0, -10, -20, -30, -40, -50):
        yy = ydb(db)
        f.append(line(L, yy, R, yy, color="#e8eaed", sw=1.0))
        f.append(text(L - 8, yy + 4, "%d" % db, size=10.5, color=MUTED, anchor="end"))
    # сітка частот (декади від fc)
    for r, lab in ((1, "1 (fc)"), (10, "10"), (100, "100")):
        xx = xof(r)
        f.append(line(xx, TOP, xx, BOT, color="#eef1f4", sw=1.0))
        f.append(text(xx, BOT + 16, lab, size=10.5, color=MUTED))

    # осі
    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.5))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.5))
    f.append(text(L - 4, TOP - 12, "|H|, дБ", size=11.5, color=MUTED, anchor="middle"))
    f.append(text(R, BOT + 30, "f / fc  (лог)", size=11.5, color=MUTED, anchor="end"))

    # крива RC 1-го порядку: |H| = 1/sqrt(1+r^2) → дБ
    pts = []
    Npt = 200
    for i in range(Npt + 1):
        lr = xmin + (xmax - xmin) * i / Npt
        r = 10 ** lr
        mag = 1.0 / math.sqrt(1.0 + r * r)
        db = max(20 * math.log10(mag), -DBSPAN)
        pts.append("%.1f,%.1f" % (xof(r), ydb(db)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))
    f.append(text(xof(2.4), ydb(-9), "RC, 1-й порядок", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(xof(20), ydb(-30) + 16, "20 дБ/декаду", size=11, color=NEG, anchor="middle"))

    # позначка: якщо fs/2 = 10·fc → ~ -20 дБ
    for (r, note, col) in ((10, "fs/2 = 10·fc → −20 дБ\n(шум ослаблено ×10)", POS),
                           (100, "fs/2 = 100·fc → −40 дБ", FIELD)):
        xx = xof(r)
        mag = 1.0 / math.sqrt(1.0 + r * r)
        yy = ydb(20 * math.log10(mag))
        f.append(circle(xx, yy, 5, fill=col, stroke=BG, sw=1.5))
        f.append(line(xx, yy, xx, BOT, color=col, sw=1.2, dash="2,3"))

    f.append(text(xof(9.0), ydb(-20) - 14, "−20 дБ", size=11, color=POS, bold=True, anchor="end"))
    f.append(text(xof(92), ydb(-40) - 12, "−40 дБ", size=11, color=FIELD, bold=True, anchor="end"))

    f.append(fitbox(L, 384, R - L, 64,
                    "Одна RC падає на 20 дБ за кожну ДЕКАДУ (×10) частоти за зрізом fc. "
                    "Тож щоб дотиснути ВЧ-шум\n"
                    "на стіні fs/2 хоча б до −40 дБ (×100), стіна має бути на ДВІ декади вище "
                    "зрізу: fs/2 ≈ 100·fc.\n"
                    "Якщо стіна ближче — однієї RC замало, потрібен вищий порядок АБО "
                    "(краще) передискретизація.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "rc-budget.svg"), W, H, *f)


# ─────────── 5. Порядок проти передискретизації (вставка math) ───────────────
def fig_order_vs_osr():
    """n = As/(20·log10(OSR)) при As=60 дБ: гіпербола, що падає з логарифмом OSR.
    Лог-вісь по OSR; видно, що ×10 по fs скидає порядок на «сходинку»."""
    f = []
    f.append(text(W / 2, 28, "Підняв fs — упав порядок: n = As / (20·log₁₀ OSR)",
                  size=16, bold=True))
    f.append(text(W / 2, 50, "(на прикладі As = 60 дБ; OSR = fs / (2·fp))",
                  size=11.5, color=MUTED))

    L, R = 96, 716
    TOP, BOT = 82, 356
    osr_min, osr_max = 2.0, 1000.0
    lx0, lx1 = math.log10(osr_min), math.log10(osr_max)

    def xof(osr):
        return L + (math.log10(osr) - lx0) / (lx1 - lx0) * (R - L)

    n_max = 12.0

    def yof(n):
        n = min(n, n_max)
        return BOT - (n / n_max) * (BOT - TOP)

    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.5))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.5))
    f.append(text(L - 12, TOP - 14, "потрібний", size=10.5, color=MUTED, anchor="start"))
    f.append(text(L - 12, TOP, "порядок n", size=10.5, color=MUTED, anchor="start"))
    f.append(text(R, BOT + 36, "OSR = fs/(2·fp)  →", size=11, color=MUTED, anchor="end"))

    for n in (2, 4, 6, 8, 10, 12):
        yy = yof(n)
        f.append(line(L, yy, R, yy, color="#e3e7ec", sw=1))
        f.append(text(L - 8, yy + 4, str(n), size=10.5, color=MUTED, anchor="end"))

    for osr in (2, 10, 100, 1000):
        xx = xof(osr)
        f.append(line(xx, BOT, xx, BOT + 5, color=INK, sw=1.2))
        f.append(text(xx, BOT + 20, "×%d" % osr, size=11, color=INK, anchor="middle"))

    As = 60.0
    pts = []
    Npt = 160
    for i in range(Npt + 1):
        lx = lx0 + (lx1 - lx0) * i / Npt
        osr = 10 ** lx
        n = As / (20.0 * math.log10(osr))
        pts.append("%.1f,%.1f" % (xof(osr), yof(n)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    marks = [
        (2,   "впритул:\nn ≈ 10 — монстр", POS,   70),
        (10,  "×10: n ≈ 3",               INK,    0),
        (100, "×100: n ≈ 1.5\n(одна RC)", FIELD, -64),
    ]
    for (osr, note, col, dx) in marks:
        n = As / (20.0 * math.log10(osr))
        xx, yy = xof(osr), yof(n)
        f.append(circle(xx, yy, 5.5, fill=col, stroke=BG, sw=1.6))
        f.append(textbox(xx + dx, yy - 32, note, size=11, pad=6,
                         fill="#f7f9fb", stroke=col, color=INK)[0])

    f.append(fitbox(L, 384, R - L, 74,
                    "Порядок ОБЕРНЕНО пропорційний log₁₀(OSR): кожне десятикратне "
                    "підняття fs додає цілу декаду\n"
                    "в знаменник і скидає n на «сходинку». Перший крок (×2 → ×20) "
                    "дешевий і дає найбільше;\n"
                    "далі віддача спадає — у якийсь момент дешевше додати один порядок, "
                    "ніж знову ×10 гнати АЦП.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "order-vs-osr.svg"), W, H, *f)


# ─────────── 6. Біти роздільності від проріджування (вставка math) ───────────
def fig_decimation_bits():
    """Δбіт = log4(M): рівні сходинки по +1 біт на кожне ×4 передискретизування."""
    f = []
    f.append(text(W / 2, 28, "×4 проріджування = +1 біт:  Δбіт = log₄ M",
                  size=16, bold=True))
    f.append(text(W / 2, 50, "(SNR росте як √M, а біт коштує множника 2)",
                  size=11.5, color=MUTED))

    L, R = 96, 716
    TOP, BOT = 82, 348
    Ms = [1, 4, 16, 64, 256]
    lx0, lx1 = 0.0, math.log(256, 4)  # 0 .. 4

    def xof(M):
        return L + (math.log(M, 4) - lx0) / (lx1 - lx0) * (R - L)

    bit_max = 4.5

    def yof(b):
        return BOT - (b / bit_max) * (BOT - TOP)

    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.5))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.5))
    f.append(text(L - 12, TOP - 14, "додані", size=10.5, color=MUTED, anchor="start"))
    f.append(text(L - 12, TOP, "біти", size=10.5, color=MUTED, anchor="start"))
    f.append(text(R, BOT + 36, "коефіцієнт проріджування M  →", size=11, color=MUTED, anchor="end"))

    for b in (1, 2, 3, 4):
        yy = yof(b)
        f.append(line(L, yy, R, yy, color="#e3e7ec", sw=1))
        f.append(text(L - 8, yy + 4, "+%d" % b, size=10.5, color=MUTED, anchor="end"))

    pts = []
    Npt = 120
    for i in range(Npt + 1):
        lm = lx0 + (lx1 - lx0) * (i / Npt)
        M = 4 ** lm
        b = math.log(M, 4)
        pts.append("%.1f,%.1f" % (xof(M), yof(b)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), FIELD))

    for M in Ms:
        b = math.log(M, 4)
        xx, yy = xof(M), yof(b)
        f.append(line(xx, BOT, xx, BOT + 5, color=INK, sw=1.2))
        f.append(text(xx, BOT + 20, "×%d" % M, size=11, color=INK, anchor="middle"))
        if M > 1:
            f.append(circle(xx, yy, 5.5, fill=FIELD, stroke=BG, sw=1.6))
            f.append(text(xx, yy - 12, "+%d біт" % int(round(b)),
                          size=11.5, color=FIELD, bold=True, anchor="middle"))

    f.append(textbox(xof(16) + 70, yof(2) + 40, "12-біт АЦП ×16\n= 14-біт", size=11, pad=6,
                     fill="#eafaf0", stroke=FIELD, color=INK)[0])

    f.append(fitbox(L, 374, R - L, 84,
                    "Сигнал у сусідніх відліках додається ЛІНІЙНО (×M), а некорельований "
                    "шум — лише КОРЕНЕМ (×√M),\n"
                    "тож SNR росте як √M = +10·log₁₀M дБ. Один біт = 6.02 дБ, тому "
                    "Δбіт = log₄ M: рівні сходинки.\n"
                    "Засторога: працює, лише поки у вході є некорельований шум рівня "
                    "≥ молодшого біта (зазвичай є).",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "decimation-bits.svg"), W, H, *f)


if __name__ == "__main__":
    fig_squeeze()
    fig_fold()
    fig_oversample()
    fig_rc_budget()
    fig_order_vs_osr()
    fig_decimation_bits()
    print("OK: 6 figures ->", OUT)
