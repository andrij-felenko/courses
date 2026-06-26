# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Специфікація фільтра».
Запуск:  python figs.py   → пише SVG у ./img/
Помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

import math

W, H = 760, 470


# ───────────────────────── 1. Маска допуску (tolerance mask) ─────────────────
def fig_mask():
    """Чотири числа специфікації, намальовані як «коридор», у який має влізти крива."""
    f = []
    f.append(text(W / 2, 30, "Специфікація — це коридор для характеристики", size=18, bold=True))

    # осі графіка |H| (дБ) проти частоти
    L, R = 95, 705          # ліво/право поля графіка
    TOP, BOT = 70, 360      # верх/низ поля графіка (0 дБ угорі)
    # рівні в дБ → y
    def ydb(db):            # 0 дБ → TOP, -80 дБ → BOT
        return TOP + (-db) * (BOT - TOP) / 80.0
    # частоти (умовні): fp=passband edge, fs=stopband edge
    fp_x = 300
    fs_x = 430

    y0 = ydb(0)
    yrip = ydb(-3)          # нижня межа смуги пропускання (приклад −3 дБ брижів)
    yatt = ydb(-45)         # стеля смуги затримання (приклад −45 дБ)

    # заборонені зони (сірим): куди характеристика заходити НЕ сміє
    # 1) над смугою пропускання — вище 0 дБ або нижче -брижі в смузі
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'stroke="none" opacity="0.55"/>' % (L, yrip, fp_x - L, BOT - yrip))   # під брижами в смузі пропускання
    # 2) у смузі затримання — все ВИЩЕ стелі затримання
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'stroke="none" opacity="0.55"/>' % (fs_x, TOP, R - fs_x, yatt - TOP))

    # дозволений коридор (зелений) у смузі пропускання: між 0 і -брижі
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" '
             'stroke="none" opacity="0.16"/>' % (L, y0, fp_x - L, yrip - y0))
    # дозволена зона затримання (зелений): нижче стелі
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" '
             'stroke="none" opacity="0.16"/>' % (fs_x, yatt, R - fs_x, BOT - yatt))

    # перехідна смуга (жовтим) — між краями, тут усе дозволено
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f4d35e" '
             'stroke="none" opacity="0.30"/>' % (fp_x, TOP, fs_x - fp_x, BOT - TOP))

    # осі
    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.6))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.6))
    f.append(text(L - 12, TOP - 10, "|H|, дБ", size=12, color=MUTED, anchor="middle"))
    f.append(text(R, BOT + 22, "частота →", size=12, color=MUTED, anchor="end"))

    # рівні 0 дБ і пунктири меж
    f.append(line(L, y0, R, y0, color=MUTED, sw=1.0, dash="2,3"))
    f.append(text(L - 8, y0 + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(line(L, yrip, fp_x, yrip, color=POS, sw=1.4, dash="4,3"))
    f.append(line(fs_x, yatt, R, yatt, color=POS, sw=1.4, dash="4,3"))

    # вертикалі країв
    f.append(line(fp_x, TOP - 6, fp_x, BOT, color=NEG, sw=1.4, dash="4,3"))
    f.append(line(fs_x, TOP - 6, fs_x, BOT, color=NEG, sw=1.4, dash="4,3"))

    # приклад характеристики, що ВЛІЗЛА в коридор (синя крива)
    pts = []
    n = 120
    for i in range(n + 1):
        x = L + (R - L) * i / n
        # модельна крива: ~1 у смузі з дрібним брижем, спад у перехідній, низько в затриманні
        t = (x - L) / (R - L)
        fp_t = (fp_x - L) / (R - L)
        fs_t = (fs_x - L) / (R - L)
        if t <= fp_t:
            db = -1.2 * (0.5 - 0.5 * math.cos(3 * math.pi * t / fp_t))   # дрібний бриж у межах
        elif t <= fs_t:
            u = (t - fp_t) / (fs_t - fp_t)
            db = -1.2 + (-(45 - 1.2)) * (u * u)                           # крутий спад
        else:
            u = (t - fs_t) / (1 - fs_t)
            db = -45 - 22 * u                                            # глибоко в затриманні
        db = max(db, -80)
        pts.append("%.1f,%.1f" % (x, ydb(db)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), NEG))

    # підписи зон
    f.append(text((L + fp_x) / 2, TOP - 14, "смуга пропускання", size=12, color=FIELD, bold=True))
    f.append(text((fp_x + fs_x) / 2, BOT + 22, "перехідна", size=11, color="#9a7d0a", anchor="middle"))
    f.append(text((fs_x + R) / 2, TOP - 14, "смуга затримання", size=12, color=FIELD, bold=True))

    # стрілки-міри: ширина брижів Ap, глибина затримання As, ширина переходу
    # Ap (зліва, між 0 і -брижі)
    f.append(line(L + 22, y0, L + 22, yrip, color=POS, sw=1.6))
    f.append(text(L + 30, (y0 + yrip) / 2 + 4, "Ap", size=12, color=POS, anchor="start", bold=True))
    # As (справа, від 0 до стелі)
    f.append(line(R - 18, y0, R - 18, yatt, color=POS, sw=1.6))
    f.append(text(R - 26, (y0 + yatt) / 2, "As", size=12, color=POS, anchor="end", bold=True))
    # ширина переходу
    f.append(line(fp_x, BOT + 30, fs_x, BOT + 30, color="#9a7d0a", sw=1.6))
    f.append(text((fp_x + fs_x) / 2, BOT + 44, "Δf", size=12, color="#9a7d0a", bold=True))
    # підписи краєвих частот
    f.append(text(fp_x, BOT + 14, "fp", size=11, color=NEG, bold=True))
    f.append(text(fs_x, BOT + 14, "fs", size=11, color=NEG, bold=True))

    # легенда внизу
    bx, by, bw, bh = L, 398, R - L, 56
    f.append(fitbox(bx, by, bw, bh,
                    "Чотири числа: fp, fs — краї смуг; Ap — дозволені брижі; As — придушення.\n"
                    "Червоне — заборонено, зелене — дозволено, жовте — перехід (нічия).\n"
                    "Будь-яка крива всередині коридору — прийнятний фільтр.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "tolerance-mask.svg"), W, H, *f)


# ───────────────────────── 2. Розмін: усе тягне порядок ──────────────────────
def fig_tradeoff():
    """Три вимоги — кожна тисне на ту саму ціну: порядок (складність) фільтра."""
    f = []
    f.append(text(W / 2, 30, "Жорсткіша вимога → дорожчий фільтр", size=18, bold=True))
    # центр — «порядок фільтра»
    cx, cy = W / 2, 250
    cbody, cw, ch = textbox(cx, cy, ["ПОРЯДОК", "(складність,", "затримка, ціна)"],
                            size=15, bold=True, fill="#eef2ff", stroke=NEG, pad=14)
    # три вимоги навколо
    specs = [
        (cx - 240, 130, ["вужча", "перехідна Δf"], POS),
        (cx + 240, 130, ["глибше", "придушення As"], POS),
        (cx, 410, ["менші", "брижі Ap"], POS),
    ]
    for (x, y, lines, col) in specs:
        b, bw, bh = textbox(x, y, lines, size=14, bold=True, fill="#fdecea", stroke=col, pad=12)
        f.append(b)
        # стрілка до центру з підписом «↑ порядок»
        # точка старту — край бокса в бік центру
        f.append(arrow(x + (cx - x) * 0.20, y + (cy - y) * 0.20,
                       x + (cx - x) * 0.74, y + (cy - y) * 0.74, color=col, sw=2.0))
    f.append(cbody)

    # підпис посередині стрілок
    f.append(text(cx - 150, 195, "↑ порядок", size=12, color=POS, bold=True))
    f.append(text(cx + 150, 195, "↑ порядок", size=12, color=POS, bold=True))
    f.append(text(cx + 70, 335, "↑ порядок", size=12, color=POS, bold=True))

    # нижня думка
    f.append(fitbox(70, 438, W - 140, 26,
                    "Вузький перехід, глибоке придушення, мізерні брижі — кожна вимога "
                    "коштує порядку.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "spec-tradeoff.svg"), W, H, *f)


# ───────────────────────── 3. Спека → порядок → вибір ────────────────────────
def fig_pipeline():
    """Specifikація — це ВХІД: з неї рахують порядок, а вже тоді обирають родину/КІХ-БІХ."""
    f = []
    f.append(text(W / 2, 30, "Специфікація — вхід для всього подальшого вибору", size=18, bold=True))
    y = 130
    boxes = [
        (135, ["1. ВИМОГИ", "до сигналу", "(що треба)"], "#f7f9fb", MUTED),
        (385, ["2. СПЕЦИФІКАЦІЯ", "fp, fs, Ap, As", "плюс fд"], "#eafaf0", FIELD),
        (635, ["3. ПОРЯДОК n", "(оцінка з", "формули)"], "#eef2ff", NEG),
    ]
    # перший ряд — три бокси зі стрілками
    prev = None
    coords = []
    for item in boxes:
        x = item[0]; lines = item[1]; fill = item[2]
        stroke = item[3] if len(item) > 3 else NEG
        b, bw, bh = textbox(x, y, lines, size=13, bold=True, fill=fill, stroke=stroke, pad=12)
        coords.append((x, bw))
        f.append(b)
    for i in range(len(coords) - 1):
        x1, w1 = coords[i]; x2, w2 = coords[i + 1]
        f.append(arrow(x1 + w1 / 2 + 4, y, x2 - w2 / 2 - 4, y, color=INK, sw=2.0))

    # другий ряд — з порядку розгалуження на вже відомі вибори
    y2 = 300
    targets = [
        (200, ["родина", "(Баттерворт/", "Чебишов/Бесель)"]),
        (440, ["КІХ чи БІХ", "(форма проти", "ресурсів)"]),
        (640, ["схема", "(RC, ОП,", "у числах)"]),
    ]
    # стрілка від боксу «порядок» униз-віяло
    src_x = 635
    for (tx, tlines) in targets:
        b, bw, bh = textbox(tx, y2, tlines, size=13, bold=True, fill="#fff8e1", stroke="#9a7d0a", pad=11)
        f.append(b)
        f.append(arrow(src_x, y + 36, tx, y2 - bh / 2 - 6, color=MUTED, sw=1.6))

    f.append(text(W / 2, 372, "далі: проєктування фільтра під цей коридор", size=13, color=MUTED, italic=True))

    f.append(fitbox(70, 408, W - 140, 46,
                    "Без чисел специфікації вибір родини й КІХ/БІХ — лише смак.\n"
                    "Щойно коридор заданий числами, порядок рахується формулою,\n"
                    "а далі весь вибір стає інженерним, а не на око.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "spec-pipeline.svg"), W, H, *f)


# ──────────────── 4. Пастка дискретної сітки: край між точками ───────────────
def fig_grid_miss():
    """|H| проколює стелю затримання МІЖ двома вузлами сітки частот:
    поточкова перевірка каже «вкладається», а реальна крива — ні."""
    f = []
    f.append(text(W / 2, 30, "Пастка: крива проколює маску МІЖ точками сітки", size=18, bold=True))

    L, R = 95, 705
    TOP, BOT = 78, 330

    def ydb(db):            # 0 дБ → TOP, -70 дБ → BOT
        return TOP + (-db) * (BOT - TOP) / 70.0

    fs_x = 250              # край смуги затримання
    yatt = ydb(-40)         # стеля затримання As = 40 дБ

    # дозволена (зелена) і заборонена (червона) зони у смузі затримання
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'stroke="none" opacity="0.55"/>' % (fs_x, TOP, R - fs_x, yatt - TOP))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" '
             'stroke="none" opacity="0.14"/>' % (fs_x, yatt, R - fs_x, BOT - yatt))

    # осі
    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.6))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.6))
    f.append(text(L - 12, TOP - 12, "|H|, дБ", size=12, color=MUTED))
    f.append(text(R, BOT + 36, "частота →", size=12, color=MUTED, anchor="end"))

    # стеля As
    f.append(line(fs_x, yatt, R, yatt, color=POS, sw=1.5, dash="5,3"))
    f.append(text(R - 4, yatt - 7, "стеля −As", size=12, color=POS, anchor="end", bold=True))
    f.append(line(fs_x, TOP - 6, fs_x, BOT, color=NEG, sw=1.3, dash="4,3"))
    f.append(text(fs_x, BOT + 18, "fs", size=11, color=NEG, bold=True))

    # справжня крива з вузьким викидом (lobe), що пробиває стелю
    def true_db(x):
        t = (x - fs_x) / (R - fs_x)
        base = -40 - 14 * t                      # загальний спад у затриманні
        # вузький викид угору біля центру — типовий «горб» між нулями
        bump = 22 * math.exp(-((x - 470) / 34.0) ** 2)
        return base + bump

    pts = []
    for i in range(121):
        x = fs_x + (R - fs_x) * i / 120
        pts.append("%.1f,%.1f" % (x, ydb(min(0, true_db(x)))))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" '
             'opacity="0.55"/>' % (" ".join(pts), MUTED))
    f.append(text(560, ydb(true_db(560)) - 10, "справжня |H(f)|", size=11,
                  color=MUTED, anchor="start", italic=True))

    # рідка сітка вузлів — і нещастя в тому, що вузли обабіч викиду
    grid = [300, 380, 520, 600, 660]            # навмисно НЕ влучають у пік (470)
    for gx in grid:
        gy = ydb(min(0, true_db(gx)))
        f.append(circle(gx, gy, 4.5, fill=NEG, stroke=BG, sw=1.5))
    # ламана, яку «бачить» поточкова перевірка — з'єднує вузли, оминаючи пік
    polypts = " ".join("%.1f,%.1f" % (gx, ydb(min(0, true_db(gx)))) for gx in grid)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="1,0"/>' % (polypts, NEG))

    # маркер самого піку, що стирчить у заборонену зону
    pk_x = 470
    pk_y = ydb(true_db(pk_x))
    f.append(circle(pk_x, pk_y, 5.5, fill=POS, stroke=BG, sw=1.6))
    f.append(line(pk_x, pk_y, pk_x, yatt, color=POS, sw=1.4, dash="2,2"))
    f.append(text(pk_x, pk_y - 12, "тут крива пробиває стелю", size=11.5,
                  color=POS, bold=True))
    f.append(text(pk_x, pk_y - 28, "— а вузла сітки тут немає!", size=11.5,
                  color=POS, bold=True))

    # підпис вузлів
    f.append(text(grid[2], ydb(min(0, true_db(grid[2]))) + 20,
                  "вузли сітки: усі під стелею", size=11, color=NEG, anchor="middle"))

    f.append(fitbox(L, 372, R - L, 78,
                    "Поточкова перевірка дивиться лише на вузли сітки (сині) — усі під стелею,\n"
                    "тож рапортує «вкладається». Але справжня крива (сіра) має вузький викид\n"
                    "між вузлами (червоний), що пробиває стелю. Між точками сітка сліпа:\n"
                    "густа сітка біля країв і за нулями — або перевірка з запасом.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "grid-miss.svg"), W, H, *f)


# ═════════════════════ ФІГУРИ ДО ВСТАВКИ math-order-formula ══════════════════

# ───────── M1. Порядок як ручка крутості (|H| Баттерворта за різних n) ────────
def fig_order_knob():
    """Та сама ручка — порядок n: що більший n, то крутіший зріз і глибше затримання.
    Малюємо |H| Баттерворта в дБ для кількох n на спільних осях."""
    f = []
    f.append(text(W / 2, 30, "Порядок n — це ручка крутості зрізу", size=18, bold=True))

    L, R = 90, 712
    TOP, BOT = 70, 358
    DBSPAN = 80.0

    def ydb(db):
        return TOP + (-db) * (BOT - TOP) / DBSPAN

    xmin, xmax = math.log10(0.3), math.log10(10.0)

    def xof(w):  # w = ω/ωc
        return L + (math.log10(w) - xmin) * (R - L) / (xmax - xmin)

    # сітка дБ
    for db in (0, -20, -40, -60, -80):
        y = ydb(db)
        f.append(line(L, y, R, y, color="#e5e7eb", sw=1.0))
        f.append(text(L - 8, y + 4, "%d" % db, size=11, color=MUTED, anchor="end"))
    # сітка частот (декади)
    for w, lab in ((0.3, "0.3"), (1, "1 (ωc)"), (3, "3"), (10, "10")):
        x = xof(w)
        f.append(line(x, TOP, x, BOT, color="#eef1f4", sw=1.0))
        f.append(text(x, BOT + 16, lab, size=11, color=MUTED))

    # осі
    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.6))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.6))
    f.append(text(L - 4, TOP - 12, "|H|, дБ", size=12, color=MUTED, anchor="middle"))
    f.append(text(R, BOT + 30, "ω / ωc  (лог)", size=12, color=MUTED, anchor="end"))

    # криві Баттерворта |H| = 1/sqrt(1+w^(2n))
    palette = [("#9aa3af", 1), ("#5b8def", 2), ("#2457d6", 4), ("#c0392b", 8)]
    Npt = 200
    for (col, n) in palette:
        pts = []
        for i in range(Npt + 1):
            lw = xmin + (xmax - xmin) * i / Npt
            w = 10 ** lw
            mag = 1.0 / math.sqrt(1.0 + w ** (2 * n))
            db = 20 * math.log10(mag) if mag > 1e-9 else -180
            db = max(db, -DBSPAN)
            pts.append("%.1f,%.1f" % (xof(w), ydb(db)))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (" ".join(pts), col, 2.6 if n == 8 else 2.0))
        wlab = 4.4
        maglab = 1.0 / math.sqrt(1.0 + wlab ** (2 * n))
        dblab = max(20 * math.log10(maglab), -DBSPAN + 5)
        f.append(text(xof(wlab) + 6, ydb(dblab) + 4, "n=%d" % n, size=12,
                      color=col, bold=True, anchor="start"))

    # вертикаль ωc і позначка -3 дБ
    f.append(line(xof(1), TOP - 6, xof(1), BOT, color="#9a7d0a", sw=1.3, dash="4,3"))
    f.append(text(xof(1), TOP - 12, "зріз: усі −3 дБ", size=11, color="#9a7d0a", bold=True))

    f.append(fitbox(L, 390, R - L, 60,
                    "Усі криві проходять через −3 дБ на зрізі ωc — хоч який порядок.\n"
                    "Різниця — у КРУТОСТІ після зрізу: кожен +1 до n додає ≈ 20 дБ/декаду.\n"
                    "Тому глибина затримання на заданій ωs росте з n — звідси й формула порядку.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "order-knob.svg"), W, H, *f)


# ───────── M2. Баттерворт проти Чебишова на тій самій масці ──────────────────
def fig_butter_cheby():
    """Чому Чебишов дає менший n: брижі в смузі «викуповують» крутість.
    Одна маска, дві криві однакового (низького) порядку."""
    f = []
    f.append(text(W / 2, 30, "Та сама маска: Чебишов влазить меншим порядком", size=18, bold=True))

    L, R = 90, 712
    TOP, BOT = 72, 350
    DBSPAN = 80.0

    def ydb(db):
        return TOP + (-db) * (BOT - TOP) / DBSPAN

    fmax = 2.0
    wp, ws = 1.0, 1.3

    def xof(w):
        return L + (w / fmax) * (R - L)

    Ap_db, As_db = 1.0, 40.0   # для наочної картинки м'якша маска, ніж у тексті

    yripple = ydb(-Ap_db)
    yatt = ydb(-As_db)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" opacity="0.5"/>'
             % (L, yripple, xof(wp) - L, BOT - yripple))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" opacity="0.5"/>'
             % (xof(ws), TOP, R - xof(ws), yatt - TOP))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f4d35e" opacity="0.25"/>'
             % (xof(wp), TOP, xof(ws) - xof(wp), BOT - TOP))

    f.append(line(L, yripple, xof(wp), yripple, color=POS, sw=1.4, dash="4,3"))
    f.append(line(xof(ws), yatt, R, yatt, color=POS, sw=1.4, dash="4,3"))
    f.append(line(xof(wp), TOP - 6, xof(wp), BOT, color=NEG, sw=1.2, dash="3,3"))
    f.append(line(xof(ws), TOP - 6, xof(ws), BOT, color=NEG, sw=1.2, dash="3,3"))

    for db in (0, -20, -40, -60):
        y = ydb(db)
        f.append(line(L, y, R, y, color="#e5e7eb", sw=0.8))
        f.append(text(L - 8, y + 4, "%d" % db, size=11, color=MUTED, anchor="end"))

    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.6))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.6))
    f.append(text(L - 4, TOP - 12, "|H|, дБ", size=12, color=MUTED, anchor="middle"))
    f.append(text(R, BOT + 30, "ω / ωp", size=12, color=MUTED, anchor="end"))
    f.append(text(xof(wp), BOT + 16, "ωp", size=11, color=NEG, bold=True))
    f.append(text(xof(ws), BOT + 16, "ωs", size=11, color=NEG, bold=True))

    eps = math.sqrt(10 ** (Ap_db / 10) - 1)

    def cheb(n, w):
        if w <= 1:
            Tn = math.cos(n * math.acos(w))
        else:
            Tn = math.cosh(n * math.acosh(w))
        return 1.0 / (1.0 + eps * eps * Tn * Tn)

    def butt(n, w):
        return 1.0 / (1.0 + w ** (2 * n))

    n_show = 4
    Npt = 240
    pts = []
    for i in range(Npt + 1):
        w = fmax * i / Npt
        db = max(10 * math.log10(butt(n_show, w)), -DBSPAN)
        pts.append("%.1f,%.1f" % (xof(w), ydb(db)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), NEG))

    pts = []
    for i in range(Npt + 1):
        w = fmax * i / Npt
        db = max(10 * math.log10(cheb(n_show, w)), -DBSPAN)
        pts.append("%.1f,%.1f" % (xof(w), ydb(db)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), POS))

    f.append(text(xof(0.16), ydb(-7.5), "Баттерворт", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(xof(0.16), ydb(-13.5), "(гладкий, ще не в масці)", size=10.5, color=NEG, anchor="start"))
    f.append(text(xof(0.05), ydb(-2.2), "Чебишов: брижі", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(xof(1.5), ydb(-50), "n однаковий,", size=12, color=INK, bold=True, anchor="middle"))
    f.append(text(xof(1.5), ydb(-56), "Чебишов крутіший", size=11, color=INK, anchor="middle"))

    f.append(fitbox(L, 384, R - L, 62,
                    "За того самого порядку n Чебишов спадає крутіше: «дозволені брижі» в смузі\n"
                    "він перетворює на додаткову крутість зрізу. Тому до тієї самої стелі −As на ωs\n"
                    "він дотягується меншим n — cosh росте швидше за степінь, звідси формула через acosh.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "butter-vs-cheby.svg"), W, H, *f)


# ───────── M3. Передкривлення осі: чому цифровий порядок інший ────────────────
def fig_prewarp():
    """Білінійне перетворення гне вісь частот тангенсом: Ω ∝ tan(πf/fд).
    Біля Найквіста вісь розтягується — перехідна смуга «ширшає», порядок падає."""
    f = []
    f.append(text(W / 2, 30, "Цифрова вісь скривлена: tan біля Найквіста розтягує", size=18, bold=True))

    L, R = 100, 690
    TOP, BOT = 80, 358
    fd = 16000.0
    fnyq = fd / 2.0

    def warp(fr_fd):          # fr_fd = f/fд (0..0.5)
        return math.tan(math.pi * fr_fd)

    ymax = warp(0.47)

    def xof(fr_ny):           # fr_ny = f/fнайк (0..1)
        return L + fr_ny * (R - L)

    def yof(val):
        return BOT - (val / ymax) * (BOT - TOP)

    f.append(line(L, TOP - 6, L, BOT, color=INK, sw=1.6))
    f.append(line(L, BOT, R + 6, BOT, color=INK, sw=1.6))
    f.append(text(L - 2, TOP - 26, "Ω аналог", size=11, color=MUTED, anchor="middle"))
    f.append(text(L - 2, TOP - 13, "(передкривл.)", size=11, color=MUTED, anchor="middle"))
    f.append(text(R + 6, BOT + 30, "f / fнайк  (цифрова)", size=12, color=MUTED, anchor="end"))

    # лінійна діагональ «якби осі збігались»
    f.append(line(xof(0), yof(0), xof(0.94), yof(warp(0.47)), color="#cbd5e1", sw=1.4, dash="5,4"))
    f.append(text(xof(0.34), yof(warp(0.34 * 0.5)) - 26, "якби лінійно", size=11,
                  color="#94a3b8", anchor="middle"))

    # крива tan
    pts = []
    Npt = 160
    for i in range(Npt + 1):
        fr_ny = i / Npt * 0.94
        val = min(warp(fr_ny * 0.5), ymax)
        pts.append("%.1f,%.1f" % (xof(fr_ny), yof(val)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))
    f.append(text(xof(0.72), yof(warp(0.72 * 0.5)) - 10, "Ω = tan(π·f/fд)", size=12,
                  color=NEG, bold=True, anchor="middle"))

    # fp=3.4к, fs=4к у частках Найквіста (fнайк = 8к)
    for (frn, lab, col) in ((3400.0 / fnyq, "fp=3.4к", FIELD), (4000.0 / fnyq, "fs=4к", POS)):
        val = warp(frn * 0.5)
        x, y = xof(frn), yof(val)
        f.append(line(x, BOT, x, y, color=col, sw=1.3, dash="3,3"))
        f.append(line(L, y, x, y, color=col, sw=1.3, dash="3,3"))
        f.append(circle(x, y, 4, fill=col, stroke=col))
        f.append(text(x, BOT + 16, lab, size=11, color=col, bold=True))

    f.append(text(xof(0.5), TOP - 14,
                  "перехід fp→fs після кривлення ширшає → порядок падає",
                  size=11.5, color="#9a7d0a", bold=True))

    f.append(fitbox(L, 390, R - L, 60,
                    "Білінійне перетворення кладе цифрову вісь на аналогову через tan(π·f/fд).\n"
                    "Поблизу Найквіста tan круто йде вгору: короткий цифровий інтервал fp→fs\n"
                    "розгортається в ШИРШИЙ аналоговий Ωp→Ωs — і формула дає менший порядок.",
                    size=12, fill="#f7f9fb", stroke=MUTED))
    render(os.path.join(OUT, "prewarp-axis.svg"), W, H, *f)


if __name__ == "__main__":
    fig_mask()
    fig_tradeoff()
    fig_pipeline()
    fig_grid_miss()
    fig_order_knob()
    fig_butter_cheby()
    fig_prewarp()
    print("OK: 7 figures ->", OUT)
