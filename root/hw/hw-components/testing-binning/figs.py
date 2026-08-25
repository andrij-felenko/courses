# -*- coding: utf-8 -*-
"""Фігури до теми «Тестування й binning» та її вставок.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори сортів/станів понад палітру svgkit
GOOD = "#cfe7d2"   # придатний (світло-зелений)
GOODK = "#1f8a3b"
SORT = "#fde9b0"   # нижчий сорт (бурштин)
SORTK = "#b8860b"
BAD = "#f6d4d0"    # брак (світло-червоний)
BADK = "#c0392b"
SILV = "#e7eef8"   # кремній/кристал
GOLD = "#e0a020"   # контактні площадки


# ── Тема, фіг.1: зондовий контроль на пластині + карта результатів ───────────
def fig_probe():
    W, H = 720, 380
    f = [text(W / 2, 26, "Зондовий контроль: кожен кристал перевіряють на пластині",
              size=16, bold=True)]

    # ЛІВОРУЧ: один кристал під зондовою картою з голками
    f.append(text(200, 64, "зондова карта (голки)", size=11.5, color=MUTED, bold=True))
    f.append(rect(120, 70, 160, 18, fill="#dfe3e8", stroke=INK, sw=1.4))
    f.append(rect(120, 130, 160, 110, fill=SILV, stroke=INK, sw=2))
    f.append(text(200, 150, "один кристал", size=11.5, color=INK))
    # голки опускаються на площадки
    pads = [136 + i * 26 for i in range(6)]
    for px in pads:
        f.append(line(px, 88, px, 214, color=MUTED, sw=1.6))
        f.append(rect(px - 6, 214, 12, 10, fill=GOLD, stroke="#9a6a00", sw=1.0, rx=2))
    f.append(text(200, 256, "торкаються площадок, подають живлення й тести",
                  size=10.5, color=MUTED))
    f.append(arrow(360, 175, 410, 175, color=INK, sw=2.0))

    # ПРАВОРУЧ: пластина з картою результатів (придатний/сорт/брак)
    f.append(circle(545, 168, 104, fill="#f3f7fc", stroke=INK, sw=2))
    # flat-зріз
    f.append(line(512, 263, 578, 263, color=BG, sw=5))
    import math
    cx, cy, R = 545, 168, 102
    s = 19
    # псевдовипадковий, але детермінований розклад сортів
    seed = 7
    def nxt():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) & 0x7fffffff
        return seed
    for r in range(-5, 6):
        for c in range(-5, 6):
            x = cx + c * s
            y = cy + r * s
            if (c * s) ** 2 + (r * s) ** 2 > (R - s * 0.5) ** 2:
                continue
            # центр частіше придатний, край частіше брак (фізика виходу)
            d = math.hypot(c, r)
            v = nxt() % 100
            if d < 2.2:
                col = GOOD if v < 88 else SORT
            elif d < 4:
                col = GOOD if v < 70 else (SORT if v < 90 else BAD)
            else:
                col = GOOD if v < 45 else (SORT if v < 72 else BAD)
            f.append(rect(x - s / 2 + 1, y - s / 2 + 1, s - 2, s - 2,
                          fill=col, stroke="#8a8a8a", sw=0.7, rx=2))
    f.append(text(545, 300, "карта результатів (bin map)", size=11.5, color=INK, bold=True))
    # легенда
    leg = [(GOOD, "придатний"), (SORT, "сорт"), (BAD, "брак")]
    lx = 458
    for col, lab in leg:
        f.append(rect(lx, 312, 14, 14, fill=col, stroke="#8a8a8a", sw=1))
        f.append(text(lx + 19, 324, lab, size=11, anchor="start"))
        lx += len(lab) * 8 + 38
    render(os.path.join(IMG, "wafer-probe.svg"), W, H, *f)


# ── Тема, фіг.2: один дизайн → кілька продуктів (сорт за частотою + вимкнення) ─
def fig_binning():
    W, H = 720, 430
    f = [text(W / 2, 26, "Один дизайн — кілька продуктів (binning)", size=16, bold=True)]

    # зверху ряд однакових кристалів з пластини
    f.append(text(W / 2, 52, "однакові кристали з однієї пластини", size=11.5, color=MUTED))
    n = 7
    dx0 = (W - n * 70) / 2
    for i in range(n):
        f.append(rect(dx0 + i * 70 + 8, 64, 54, 40, fill=SILV, stroke=INK, sw=1.4))
        # 4 «ядра» всередині — деякі биті
        for k in range(4):
            bad = (i >= 4 and k == i - 4) or (i == 6 and k == 1)
            f.append(rect(dx0 + i * 70 + 13 + (k % 2) * 24, 70 + (k // 2) * 16,
                          20, 12, fill=BAD if bad else GOOD,
                          stroke="#8a8a8a", sw=0.8, rx=2))
    # три стрілки вниз до трьох кошиків
    cols = [
        (150, GOOD, GOODK, "топ-сорт", ["усі блоки цілі,", "висока частота", "дорожче"]),
        (360, SORT, SORTK, "середній", ["усі блоки цілі,", "нижча частота", "дешевше"]),
        (570, BAD, BADK, "молодша модель", ["биті блоки —", "вимкнути й продати", "найдешевше"]),
    ]
    f.append(text(W / 2, 134, "тест сортує за частотою та цілістю блоків", size=11, color=MUTED))
    for x, col, ck, name, lines in cols:
        f.append(arrow(x, 150, x, 178, color=ck, sw=2.0))
        f.append(rect(x - 95, 184, 190, 96, fill=col, stroke=ck, sw=1.8))
        f.append(text(x, 206, name, size=13, color=INK, bold=True))
        yy = 226
        for ln in lines:
            f.append(text(x, yy, ln, size=10.5, color=INK))
            yy += 17
    # нижній підпис-висновок
    f.append(text(W / 2, 320, "Один із битих блоків назавжди вимикають — і восьмиядерний",
                  size=11.5, color=INK))
    f.append(text(W / 2, 338, "кристал стає справним шестиядерним, а не йде у відходи.",
                  size=11.5, color=INK))
    f.append(text(W / 2, 366, "Так із одного дизайну виходить ціла лінійка за різною ціною —",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, 384, "і майже жоден кристал не марнується.", size=11.5, color=MUTED))
    render(os.path.join(IMG, "binning.svg"), W, H, *f)


# ── proj-scan, фіг.1: scan-комірка (MUX перед тригером) і вся низка ───────────
def fig_scan_cell():
    W, H = 720, 380
    f = [text(W / 2, 26, "Scan-комірка: MUX перед тригером і вся низка як зсувний регістр",
              size=16, bold=True)]

    # ── зблизька: одна комірка ──
    f.append(text(180, 58, "одна scan-комірка", size=12, color=MUTED, bold=True))
    # MUX (трапеція)
    f.append('<polygon points="120,96 152,108 152,148 120,160" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (FILL, LINE))
    f.append(text(136, 132, "MUX", size=10, color=INK, bold=True))
    f.append(text(108, 110, "0", size=10, color=INK, anchor="end"))
    f.append(text(108, 152, "1", size=10, color=INK, anchor="end"))
    # входи в MUX
    f.append(line(60, 106, 120, 106, color=LINE, sw=1.6))
    f.append(text(58, 102, "від логіки", size=9.5, color=INK, anchor="end"))
    f.append(line(60, 150, 120, 150, color=NEG, sw=1.6))
    f.append(text(58, 146, "від сусіда (scan-in)", size=9.5, color=NEG, anchor="end"))
    # тригер
    f.append(rect(176, 108, 64, 48, fill=SILV, stroke=INK, sw=1.6))
    f.append(text(208, 128, "FF", size=13, color=INK, bold=True))
    f.append(text(184, 150, "D", size=9, color=MUTED, anchor="start"))
    f.append(text(232, 150, "Q", size=9, color=MUTED, anchor="end"))
    f.append(line(152, 128, 176, 128, color=LINE, sw=1.6))
    f.append(arrow(240, 132, 296, 132, color=LINE, sw=1.6))
    f.append(text(300, 136, "Q → далі / до наступної комірки", size=9.5, color=INK, anchor="start"))
    # selector scan_en
    f.append(line(136, 175, 136, 160, color=POS, sw=1.6))
    f.append(text(136, 190, "scan_en", size=10, color=POS, bold=True))

    # два режими
    f.append(rect(420, 96, 270, 30, fill="#eef7f0", stroke=GOODK, sw=1.2))
    f.append(text(432, 116, "scan_en = 0  →  робочий режим (стан від логіки)",
                  size=10.5, color=INK, anchor="start"))
    f.append(rect(420, 134, 270, 30, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(432, 154, "scan_en = 1  →  scan-режим (стан від сусіда)",
                  size=10.5, color=INK, anchor="start"))

    # ── вся низка як одна стрічка ──
    f.append(text(W / 2, 232, "у scan-режимі всі тригери — одна стрічка від scan-in до scan-out",
                  size=11.5, color=MUTED))
    y = 258
    f.append(text(60, y + 24, "scan-in", size=10, color=NEG, anchor="end", bold=True))
    f.append(line(60, y + 20, 96, y + 20, color=NEG, sw=1.8))
    bx = 96
    for i in range(6):
        f.append(rect(bx + i * 86, y, 58, 40, fill=SILV, stroke=INK, sw=1.4))
        f.append(text(bx + i * 86 + 29, y + 25, "FF", size=12, color=INK, bold=True))
        if i < 5:
            f.append(arrow(bx + i * 86 + 58, y + 20, bx + (i + 1) * 86, y + 20,
                           color=NEG, sw=1.6))
    f.append(arrow(bx + 5 * 86 + 58, y + 20, bx + 5 * 86 + 92, y + 20, color=NEG, sw=1.8))
    f.append(text(bx + 5 * 86 + 96, y + 24, "scan-out", size=10, color=NEG, anchor="start", bold=True))
    f.append(text(W / 2, y + 64, "Ціна — один MUX і один дріт на тригер, тобто кілька відсотків площі.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "scan-cell.svg"), W, H, *f)


# ── proj-scan, фіг.2: чому кількох ніжок досить (простір → час) + TAP ─────────
def fig_few_pins():
    W, H = 752, 360
    f = [text(W / 2, 26, "Кількох ніжок досить на мільярд вузлів: простір → час",
              size=16, bold=True)]

    # ЛІВОРУЧ: дві властивості
    f.append(rect(40, 60, 300, 86, fill="#eef7f0", stroke=GOODK, sw=1.4))
    f.append(text(56, 82, "Контрольованість (controllability)", size=11.5, color=INK,
                  anchor="start", bold=True))
    f.append(text(56, 102, "задати вузлу потрібне значення —", size=10.5, color=INK, anchor="start"))
    f.append(text(56, 118, "scan ЗАСОВУЄ стан у тригери зсувом", size=10.5, color=INK, anchor="start"))
    f.append(text(56, 134, "ззовні.", size=10.5, color=INK, anchor="start"))

    f.append(rect(40, 158, 300, 86, fill="#eaf0fd", stroke=NEG, sw=1.4))
    f.append(text(56, 180, "Спостережуваність (observability)", size=11.5, color=INK,
                  anchor="start", bold=True))
    f.append(text(56, 200, "побачити, що вузол видав —", size=10.5, color=INK, anchor="start"))
    f.append(text(56, 216, "тригери ЛОВЛЯТЬ реакцію логіки,", size=10.5, color=INK, anchor="start"))
    f.append(text(56, 232, "а зсув ВИШТОВХУЄ її назовні.", size=10.5, color=INK, anchor="start"))

    f.append(text(190, 268, "обидві йдуть через дві ніжки + такт + scan_en", size=10.5, color=MUTED))
    f.append(text(190, 292, "простір мільярдів вузлів → час: стільки тактів,", size=10.5, color=INK))
    f.append(text(190, 308, "скільки тригерів у ланцюзі", size=10.5, color=INK))

    f.append(arrow(348, 175, 392, 175, color=INK, sw=2.0))

    # ПРАВОРУЧ: порт TAP — 4 ніжки
    f.append(text(540, 60, "стандартний порт доступу (TAP)", size=12, color=MUTED, bold=True))
    f.append(rect(470, 76, 150, 150, fill=SILV, stroke=INK, sw=1.8))
    f.append(text(545, 156, "чіп", size=13, color=INK, bold=True))
    pins = [("TCK", "такт"), ("TMS", "режим"), ("TDI", "вхід даних"), ("TDO", "вихід даних")]
    yy = 96
    for name, role in pins:
        f.append(line(620, yy, 648, yy, color=INK, sw=1.6))
        f.append(circle(648, yy, 3, fill=INK, stroke=INK, sw=0))
        f.append(text(656, yy + 4, "%s — %s" % (name, role), size=10.5, anchor="start"))
        yy += 30
    f.append(text(545, 246, "+ необов'язковий TRST", size=10, color=MUTED))
    f.append(text(545, 268, "той самий порт згодом служить", size=10.5, color=INK))
    f.append(text(545, 284, "і для внутрішньосхемної налагодки (JTAG)", size=10.5, color=INK))
    render(os.path.join(IMG, "few-pins.svg"), W, H, *f)


# ── proj-scan, фіг.3: тестовий цикл shift-in → capture → shift-out + конвеєр ──
def fig_scan_cycle():
    W, H = 720, 400
    f = [text(W / 2, 26, "Тестовий цикл: засунути вектор, один такт capture, виштовхнути",
              size=16, bold=True)]

    # схема: дві стінки тригерів і логіка між ними
    f.append(text(150, 58, "вхідні scan-тригери", size=10.5, color=MUTED))
    for i in range(3):
        f.append(rect(96, 70 + i * 40, 44, 30, fill=SILV, stroke=INK, sw=1.3))
        f.append(text(118, 90 + i * 40, "FF", size=10, color=INK, bold=True))
    f.append('<polygon points="170,66 250,86 250,158 170,178" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (FILL, LINE))
    f.append(text(205, 126, "логіка", size=11, color=INK, bold=True))
    f.append(text(205, 192, "(те, що тестуємо)", size=9.5, color=MUTED))
    for i in range(3):
        f.append(line(140, 85 + i * 40, 170, 95 + i * 12, color=LINE, sw=1.2))
    f.append(text(330, 58, "вихідні scan-тригери", size=10.5, color=MUTED))
    for i in range(3):
        f.append(rect(290, 70 + i * 40, 44, 30, fill=SILV, stroke=INK, sw=1.3))
        f.append(text(312, 90 + i * 40, "FF", size=10, color=INK, bold=True))
        f.append(line(250, 95 + i * 12, 290, 85 + i * 40, color=LINE, sw=1.2))

    # три фази
    phases = [
        (430, GOODK, "1. SHIFT-IN", "scan_en = 1", ["засунути вектор", "по біту за такт"]),
        (430, SORTK, "2. CAPTURE", "scan_en = 0", ["рівно ОДИН такт:", "виходи логіки", "сідають у тригери"]),
        (430, NEG, "3. SHIFT-OUT", "scan_en = 1", ["виштовхнути відповідь", "і вже засунути", "наступний вектор"]),
    ]
    yy = 64
    for _, ck, name, en, lines in phases:
        f.append(rect(400, yy, 300, 30 + len(lines) * 0 + 8, fill="none", stroke=ck, sw=1.4))
        f.append(text(412, yy + 20, name, size=11.5, color=ck, anchor="start", bold=True))
        f.append(text(560, yy + 20, en, size=10.5, color=INK, anchor="start"))
        ty = yy + 36
        for ln in lines:
            f.append(text(412, ty, ln, size=10, color=INK, anchor="start"))
            ty += 15
        yy = ty + 8

    # конвеєр унизу
    f.append(text(W / 2, 320, "фази зсуву перекривають: shift-out попереднього й shift-in наступного — одним рухом",
                  size=11, color=MUTED))
    f.append(rect(120, 334, 200, 26, fill=GOOD, stroke=GOODK, sw=1.2))
    f.append(text(220, 351, "shift-out вектора A", size=10.5, color=INK))
    f.append(rect(120, 334, 200, 26, fill="none", stroke=NEG, sw=1.2, rx=6))
    f.append(text(220, 372, "= shift-in вектора B (той самий зсув)", size=10, color=NEG))
    f.append(text(520, 351, "далі: відповідь ≠ еталон → брак", size=10.5, color=BADK, bold=True))
    render(os.path.join(IMG, "scan-cycle.svg"), W, H, *f)


# ── comp-markings, фіг.1: лазерний напис → 4 поля ────────────────────────────
def fig_marking_decode():
    W, H = 720, 340
    f = [text(W / 2, 26, "Напис на корпусі: чотири незалежні відомості",
              size=16, bold=True)]

    # корпус чіпа з написом
    f.append(rect(90, 70, 230, 190, fill="#2b2b2b", stroke=INK, sw=2, rx=10))
    f.append(circle(108, 88, 5, fill="#555", stroke="#777", sw=1))  # ключ 1-го виводу
    lines = [("ACME32F407", "#ffffff"), ("VGT6", "#cfcfcf"),
             ("2438", "#cfcfcf"), ("K7B  C2", "#cfcfcf")]
    yy = 120
    for s, col in lines:
        f.append(text(205, yy, s, size=16, color=col, bold=True))
        yy += 36

    # чотири картки-поля праворуч
    fields = [
        (GOOD, GOODK, "партномер (part number)", "за ним шукають даташит"),
        ("#eef2f7", MUTED, "дата-код", "коли випущено"),
        ("#eef2f7", MUTED, "код партії (lot)", "слід для відстеження браку"),
        (SORT, SORTK, "ревізія кристала (stepping)", "версія самого кремнію"),
    ]
    yy = 78
    for col, ck, name, role in fields:
        f.append(arrow(326, yy + 18, 372, yy + 18, color=ck, sw=1.6))
        f.append(rect(380, yy, 312, 40, fill=col, stroke=ck, sw=1.4))
        f.append(text(392, yy + 18, name, size=11, color=INK, anchor="start", bold=True))
        f.append(text(392, yy + 33, role, size=10, color=MUTED, anchor="start"))
        yy += 48
    f.append(text(W / 2, H - 14, "Дата-код і ревізію легко сплутати, хоч кажуть вони про геть різне.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "marking-decode.svg"), W, H, *f)


# ── comp-markings, фіг.2: дата-код YYWW → рік + тиждень ──────────────────────
def fig_date_code():
    W, H = 720, 320
    f = [text(W / 2, 26, "Дата-код YYWW: рік і робочий тиждень", size=16, bold=True)]

    # великий код 2438
    f.append(text(W / 2, 96, "2438", size=54, color=INK, bold=True))
    # дві дужки під парами
    f.append(text(300, 130, "24", size=22, color=NEG, bold=True))
    f.append(text(420, 130, "38", size=22, color=POS, bold=True))
    f.append(rect(264, 150, 96, 56, fill="#eaf0fd", stroke=NEG, sw=1.4))
    f.append(text(312, 172, "рік", size=12, color=INK, bold=True))
    f.append(text(312, 192, "24 → 2024", size=11, color=INK))
    f.append(rect(384, 150, 96, 56, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(432, 172, "тиждень", size=12, color=INK, bold=True))
    f.append(text(432, 192, "38 → 38-й", size=11, color=INK))

    # стрічка-календар
    f.append(text(W / 2, 236, "де 38-й тиждень лежить у році:", size=11, color=MUTED))
    bx, bw = 110, 500
    f.append(rect(bx, 248, bw, 22, fill=FILL, stroke=LINE, sw=1.2))
    # позначка 38/52
    mx = bx + bw * 38 / 52
    f.append(rect(bx, 248, bw * 38 / 52, 22, fill="#fbe3c8", stroke="none", sw=0))
    f.append(line(mx, 244, mx, 274, color=POS, sw=2))
    f.append(text(mx, 288, "≈ кінець вересня", size=10.5, color=POS, bold=True))
    f.append(text(bx, 288, "січ", size=9.5, color=MUTED))
    f.append(text(bx + bw, 288, "груд", size=9.5, color=MUTED, anchor="end"))
    f.append(text(W / 2, H - 6, "Формат поширений, але не єдиний — підтверджує лише даташит.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "date-code.svg"), W, H, *f)


# ── comp-markings, фіг.3: errata тримаються ревізії (маски → ревізія) ─────────
def fig_errata_revision():
    W, H = 720, 360
    f = [text(W / 2, 26, "Errata тримаються ревізії: баг живе в наборі масок",
              size=16, bold=True)]

    # ЛІВОРУЧ: rev B0 з багом
    f.append(rect(60, 64, 200, 130, fill=SILV, stroke=INK, sw=1.8))
    f.append(text(160, 86, "кристал rev B0", size=12, color=INK, bold=True))
    f.append(rect(86, 100, 148, 30, fill=BAD, stroke=BADK, sw=1.4))
    f.append(text(160, 120, "баг X у масках", size=11, color=INK, bold=True))
    f.append(text(160, 152, "errata: «баг X присутній»", size=10.5, color=BADK))
    f.append(text(160, 174, "(виправити можна лише", size=10, color=MUTED))
    f.append(text(160, 188, "новим набором масок)", size=10, color=MUTED))

    # стрілка: новий набір масок
    f.append(arrow(268, 130, 332, 130, color=INK, sw=2.0))
    f.append(text(300, 118, "новий", size=9.5, color=MUTED))
    f.append(text(300, 152, "набір масок", size=9.5, color=MUTED))

    # ПРАВОРУЧ: rev C0 виправлено
    f.append(rect(340, 64, 200, 130, fill=SILV, stroke=INK, sw=1.8))
    f.append(text(440, 86, "кристал rev C0", size=12, color=INK, bold=True))
    f.append(rect(366, 100, 148, 30, fill=GOOD, stroke=GOODK, sw=1.4))
    f.append(text(440, 120, "баг X прибрано", size=11, color=INK, bold=True))
    f.append(text(440, 152, "errata: рядок закрито", size=10.5, color=GOODK))
    f.append(text(440, 174, "«виправлено в C0»", size=10, color=MUTED))

    # як цим користується код
    f.append(rect(560, 70, 140, 124, fill="#eef2f7", stroke=MUTED, sw=1.4))
    f.append(text(630, 90, "код:", size=11, color=INK, bold=True))
    f.append(text(630, 110, "читає ревізію", size=10, color=INK))
    f.append(text(630, 126, "з регістра ID", size=10, color=INK))
    f.append(text(630, 146, "→ дивиться errata", size=10, color=INK))
    f.append(text(630, 162, "саме цієї ревізії", size=10, color=INK))
    f.append(text(630, 182, "→ вмикає обхід", size=10, color=INK))
    f.append(arrow(540, 130, 558, 130, color=INK, sw=1.4))

    f.append(text(W / 2, 244, "Хиба сидить у самому кремнії — у наборі фотомасок, за якими цей кристал надруковано.",
                  size=11.5, color=INK))
    f.append(text(W / 2, 266, "Поки набір той самий, баг є в кожному вирізаному кристалі;",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, 284, "виправлення = змінити маски = нова ревізія.", size=11.5, color=MUTED))
    f.append(text(W / 2, 314, "Тому одна родина чіпів у різних ревізіях може потребувати різних обхідних шляхів.",
                  size=11, color=INK))
    render(os.path.join(IMG, "errata-revision.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури ДЕТАЛЬНОЇ версії (testing-binning-d.md)
# ════════════════════════════════════════════════════════════════════════════

# ── d-фіг.1: повний конвеєр тесту wafer sort → … → burn-in → відвантаження ────
def fig_test_flow():
    W, H = 720, 360
    f = [text(W / 2, 26, "Конвеєр тесту: брак відсікають якомога раніше",
              size=16, bold=True)]

    # сходи вартості: що далі по конвеєру, то дорожчий уже вкладений у кристал
    f.append(text(W / 2, 50, "вартість, уже вкладена в кристал, росте зліва направо →",
                  size=11, color=MUTED))

    stages = [
        ("wafer sort", "зондовий", "тест на пластині", GOOD, GOODK),
        ("dicing", "різання", "пластину ріжуть", "#eef2f7", MUTED),
        ("packaging", "корпусування", "кристал у корпус", "#eef2f7", MUTED),
        ("final test", "фінальний", "тест запакованого", GOOD, GOODK),
        ("burn-in", "припрацювання", "лише критичні чіпи", SORT, SORTK),
        ("ship", "відвантаження", "до замовника", GOOD, GOODK),
    ]
    n = len(stages)
    bw, gap = 96, 16
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    ytop = 78
    bh = 64
    for i, (en, ua, sub, col, ck) in enumerate(stages):
        x = x0 + i * (bw + gap)
        # сходинка-висота показує накопичену вартість
        rise = 8 * i
        f.append(rect(x, ytop + (40 - rise * 0.0), bw, bh, fill=col, stroke=ck, sw=1.6))
        f.append(text(x + bw / 2, ytop + 60, ua, size=11.5, color=INK, bold=True))
        f.append(text(x + bw / 2, ytop + 78, sub, size=9, color=MUTED))
        f.append(text(x + bw / 2, ytop + 30, en, size=9, color=ck, italic=True))
        if i < n - 1:
            ax = x + bw
            f.append(arrow(ax + 2, ytop + 72, ax + gap - 2, ytop + 72, color=INK, sw=1.6))

    # дві точки відсіву браку — зі стрілками «у відходи» вниз
    for idx, lab in [(0, "брак → геть"), (3, "брак → геть")]:
        x = x0 + idx * (bw + gap) + bw / 2
        f.append(arrow(x, ytop + bh + 18, x, ytop + bh + 48, color=BADK, sw=1.6))
        f.append(text(x, ytop + bh + 62, lab, size=9.5, color=BADK, bold=True))

    # підпис-логіка
    f.append(text(W / 2, 250, "Кожен іспит відсіює брак ДО наступного, дорожчого кроку:",
                  size=11.5, color=INK))
    f.append(text(W / 2, 270, "немає сенсу корпусувати або припрацьовувати кристал, що вже провалив тест.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, 300, "Зондовий ловить брак ще на пластині; фінальний — пошкодження від корпусування;",
                  size=10.5, color=INK))
    f.append(text(W / 2, 318, "burn-in (лише для авто/медицини/серверів) — приховані ранні відмови.",
                  size=10.5, color=INK))
    render(os.path.join(IMG, "test-flow.svg"), W, H, *f)


# ── d-фіг.2: один канал ATE (драйвер + компаратор) на вивід + multisite ───────
def fig_ate_channel():
    W, H = 720, 380
    f = [text(W / 2, 26, "Канал ATE: драйвер задає, компаратор зчитує — по одному на вивід",
              size=16, bold=True)]

    # ── один канал зблизька ──
    f.append(text(180, 56, "один канал (pin electronics)", size=12, color=MUTED, bold=True))
    # драйвер (трикутник-підсилювач) — задає вхід
    f.append('<polygon points="70,86 70,134 118,110" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % ("#eaf0fd", NEG))
    f.append(text(88, 114, "DRV", size=9.5, color=NEG, bold=True))
    f.append(text(64, 78, "вектор (що подати)", size=9, color=NEG, anchor="start"))
    f.append(line(40, 110, 70, 110, color=NEG, sw=1.6))
    # компаратор (трикутник) — зчитує вихід
    f.append('<polygon points="70,176 70,224 118,200" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % ("#eef7f0", GOODK))
    f.append(text(88, 204, "CMP", size=9.5, color=GOODK, bold=True))
    f.append(text(64, 246, "відповідь = еталон?", size=9, color=GOODK, anchor="start"))
    # очікуваний рівень на компаратор
    f.append(line(40, 200, 70, 200, color=GOODK, sw=1.6))
    f.append(text(40, 188, "еталон", size=9, color=GOODK, anchor="start"))
    # вивід чіпа — спільна точка
    f.append(line(118, 110, 158, 110, color=INK, sw=1.8))
    f.append(line(118, 200, 158, 200, color=INK, sw=1.8))
    f.append(line(158, 110, 158, 200, color=INK, sw=1.8))
    f.append(circle(158, 155, 4, fill=GOLD, stroke="#9a6a00", sw=1))
    f.append(line(158, 155, 196, 155, color=INK, sw=1.8))
    f.append(rect(196, 120, 70, 70, fill=SILV, stroke=INK, sw=1.8))
    f.append(text(231, 160, "вивід", size=10, color=INK, bold=True))
    f.append(text(231, 205, "чіпа (DUT)", size=9, color=MUTED))
    # драйвер і компаратор не одночасно — підпис
    f.append(text(170, 300, "драйвер ЗАДАЄ рівень входу,", size=10, color=NEG, anchor="middle"))
    f.append(text(170, 318, "компаратор ЗЧИТУЄ й порівнює вихід", size=10, color=GOODK, anchor="middle"))
    f.append(text(170, 340, "з еталоном — на кожнісінькому виводі", size=10, color=INK, anchor="middle"))

    f.append(arrow(300, 200, 344, 200, color=INK, sw=2.0))

    # ── multisite: один тестер — багато кристалів ──
    f.append(text(540, 56, "multisite: один тестер — багато кристалів", size=11.5,
                  color=MUTED, bold=True))
    f.append(rect(372, 72, 300, 150, fill="#f3f7fc", stroke=INK, sw=1.6))
    f.append(text(522, 92, "тестер ATE", size=11, color=INK, bold=True))
    # 4 DUT під одним тестером
    for i in range(4):
        dx = 392 + (i % 2) * 150
        dy = 108 + (i // 2) * 56
        f.append(rect(dx, dy, 120, 44, fill=SILV, stroke=INK, sw=1.4))
        f.append(text(dx + 60, dy + 27, "кристал %d" % (i + 1), size=10, color=INK))
        f.append(arrow(dx - 14, dy + 22, dx - 1, dy + 22, color=INK, sw=1.3))
    f.append(text(522, 244, "ATE дорогий і платять за ЧАС;", size=10.5, color=INK))
    f.append(text(522, 262, "тому багато кристалів тестують паралельно —", size=10.5, color=INK))
    f.append(text(522, 280, "час-на-кристал падає, а з ним і ціна тесту.", size=10.5, color=INK))
    f.append(text(522, 308, "Канали драйвер/компаратор на кожен вивід ×", size=9.5, color=MUTED))
    f.append(text(522, 324, "багато сайтів — головний кошт тестера.", size=9.5, color=MUTED))
    render(os.path.join(IMG, "ate-channel.svg"), W, H, *f)


# ── d-фіг.3: shmoo-діаграма (область працездатності частота×напруга + guard) ──
def fig_shmoo():
    W, H = 720, 420
    f = [text(W / 2, 26, "Shmoo: область працездатності в осях напруга × частота",
              size=16, bold=True)]

    import math
    # осі
    ox, oy = 110, 330          # початок осей (лівий-нижній)
    ax_w, ax_h = 470, 250
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))          # X
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))          # Y
    f.append(text(ox + ax_w / 2, oy + 40, "напруга живлення Vdd →", size=11.5, color=INK))
    f.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">частота f →</text>'
             % (40, oy - ax_h / 2, FONT, INK, 40, oy - ax_h / 2))

    # сітка точок: PASS, якщо f нижча за межу, що росте з Vdd (бо вища напруга → швидше)
    cols, rows = 11, 9
    cw = ax_w / cols
    rh = ax_h / rows
    for c in range(cols):
        vdd_frac = c / (cols - 1)             # 0..1 уздовж X
        # межа працездатної частоти росте з Vdd (приблизно лінійно з overdrive)
        fmax_frac = 0.30 + 0.62 * vdd_frac
        for r in range(rows):
            fr = r / (rows - 1)               # 0 унизу .. 1 угорі
            cx = ox + c * cw + cw / 2
            cy = oy - r * rh - rh / 2
            passing = fr <= fmax_frac + 1e-9
            col = GOOD if passing else BAD
            mark = "P" if passing else "F"
            mk = GOODK if passing else BADK
            f.append(rect(cx - cw / 2 + 2, cy - rh / 2 + 2, cw - 4, rh - 4,
                          fill=col, stroke="#9aa0a6", sw=0.6, rx=2))
            f.append(text(cx, cy + 4, mark, size=9, color=mk, bold=True))

    # межа PASS/FAIL — ламана по краю зеленого
    pts = []
    for c in range(cols):
        vdd_frac = c / (cols - 1)
        fmax_frac = 0.30 + 0.62 * vdd_frac
        # знайти рядок, де ще PASS
        rr = int(round(fmax_frac * (rows - 1)))
        rr = max(0, min(rows - 1, rr))
        cx = ox + c * cw + cw / 2
        cy = oy - rr * rh - rh / 2
        pts.append((cx, cy))
    pl = " ".join("%.0f,%.0f" % (x, y) for x, y in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pl, INK))

    # робоча точка: гарантована частота нижча за межу на guard-band
    gx = ox + 6 * cw + cw / 2
    g_edge_r = int(round((0.30 + 0.62 * (6 / (cols - 1))) * (rows - 1)))
    g_edge_y = oy - g_edge_r * rh - rh / 2
    g_op_y = g_edge_y + 2.0 * rh        # нижче межі на ~2 рядки = запас
    f.append(circle(gx, g_op_y, 6, fill="#ffffff", stroke=NEG, sw=2.4))
    f.append(text(gx + 12, g_op_y + 4, "гарантована робоча точка", size=10, color=NEG,
                  anchor="start", bold=True))
    # стрілка guard-band між межею й робочою точкою
    f.append(line(gx, g_edge_y, gx, g_op_y, color=POS, sw=1.6, dash="4 3"))
    f.append(text(gx - 10, (g_edge_y + g_op_y) / 2 + 4, "guard-band", size=10, color=POS,
                  anchor="end", bold=True))

    # легенда
    f.append(rect(ox + ax_w - 96, oy - ax_h - 6, 18, 14, fill=GOOD, stroke="#9aa0a6", sw=1))
    f.append(text(ox + ax_w - 74, oy - ax_h + 6, "працює", size=10, anchor="start"))
    f.append(rect(ox + ax_w - 96, oy - ax_h + 14, 18, 14, fill=BAD, stroke="#9aa0a6", sw=1))
    f.append(text(ox + ax_w - 74, oy - ax_h + 26, "збоїть", size=10, anchor="start"))

    f.append(text(W / 2, H - 14,
                  "Гарантують частоту НИЖЧУ за виміряну межу — на запас (guard-band) проти старіння й нагріву.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "shmoo.svg"), W, H, *f)


# ── d-фіг.4: bathtub curve (рання смертність + випадкові + знос) + burn-in ────
def fig_bathtub():
    W, H = 720, 380
    f = [text(W / 2, 26, "Крива «ванни»: інтенсивність відмов за час життя чіпа",
              size=16, bold=True)]

    import math
    ox, oy = 90, 300
    ax_w, ax_h = 560, 210
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 40, "час роботи →", size=11.5, color=INK))
    f.append('<text x="%.0f" y="%.0f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.0f %.0f)">інтенсивність відмов λ →</text>'
             % (32, oy - ax_h / 2, FONT, INK, 32, oy - ax_h / 2))

    # три зони
    z1 = ox + ax_w * 0.22
    z2 = ox + ax_w * 0.78
    f.append(rect(ox, oy - ax_h, z1 - ox, ax_h, fill="#fdecec", stroke="none", sw=0, rx=0))
    f.append(rect(z2, oy - ax_h, ox + ax_w - z2, ax_h, fill="#fdecec", stroke="none", sw=0, rx=0))
    f.append(rect(z1, oy - ax_h, z2 - z1, ax_h, fill="#eef7f0", stroke="none", sw=0, rx=0))

    # крива ванни: спад + пласко + ріст
    def bath(t):  # t у [0,1] → висота λ у [0,1]
        early = 0.95 * math.exp(-t * 14)        # рання смертність (спадна)
        flat = 0.16                              # випадкові відмови (пласко)
        wear = 0.85 * max(0.0, (t - 0.72)) ** 2 / (0.28 ** 2)  # знос (зростна)
        return early + flat + wear

    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        y = bath(t)
        px = ox + t * ax_w
        py = oy - min(1.0, y) * ax_h
        pts.append((px, py))
    pl = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pl, INK))

    # підписи зон
    f.append(text((ox + z1) / 2, oy - ax_h + 18, "рання смертність", size=11, color=BADK, bold=True))
    f.append(text((ox + z1) / 2, oy - ax_h + 34, "(спадна)", size=9.5, color=BADK))
    f.append(text((z1 + z2) / 2, oy - ax_h + 18, "випадкові відмови (пласка)", size=11, color=GOODK, bold=True))
    f.append(text((z1 + z2) / 2, oy - ax_h + 34, "корисний строк служби", size=9.5, color=GOODK))
    f.append(text((z2 + ox + ax_w) / 2, oy - ax_h + 18, "знос", size=11, color=BADK, bold=True))
    f.append(text((z2 + ox + ax_w) / 2, oy - ax_h + 34, "(зростна)", size=9.5, color=BADK))

    # burn-in зрізає лівий горб
    f.append(line(z1, oy, z1, oy - ax_h, color=NEG, sw=1.6, dash="5 4"))
    f.append(arrow(ox + 6, oy - ax_h - 0, z1 - 4, oy - ax_h - 0, color=NEG, sw=1.4))
    f.append(text((ox + z1) / 2, oy - ax_h - 8, "burn-in зрізає цей горб", size=10, color=NEG, bold=True))
    f.append(text((ox + z1) / 2, 350, "прискорене старіння (вища T і V):", size=10, color=NEG))
    f.append(text((ox + z1) / 2, 366, "слабкі гинуть тут, на стенді", size=10, color=NEG))

    f.append(text(z2 + (ox + ax_w - z2) / 2, 350, "сюди чіп уже не доживає", size=9.5, color=MUTED))
    f.append(text(z2 + (ox + ax_w - z2) / 2, 366, "в межах гарантії", size=9.5, color=MUTED))
    render(os.path.join(IMG, "bathtub.svg"), W, H, *f)


# ── d-фіг.5: learning curve — D падає, вихід росте за час життя процесу ───────
def fig_learning_curve():
    W, H = 720, 360
    f = [text(W / 2, 26, "Дозрівання процесу: густина дефектів падає, вихід росте",
              size=16, bold=True)]

    import math
    ox, oy = 92, 290
    ax_w, ax_h = 540, 210
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 38, "час життя техпроцесу (місяці → роки) →", size=11.5, color=INK))

    # крива виходу Y росте (зліва низько → справа високо)
    def yld(t):   # t∈[0,1] → Y∈[0,1]
        return 0.06 + 0.86 * (1 - math.exp(-t * 3.0))
    # крива густини D падає
    def dd(t):
        return 0.92 * math.exp(-t * 2.6) + 0.05

    pts_y = []
    pts_d = []
    N = 120
    for i in range(N + 1):
        t = i / N
        px = ox + t * ax_w
        pts_y.append((px, oy - yld(t) * ax_h))
        pts_d.append((px, oy - dd(t) * ax_h))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts_y), GOODK))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6 4"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts_d), BADK))

    # підписи кривих
    f.append(text(ox + ax_w - 4, oy - yld(1.0) * ax_h - 10, "вихід Y", size=11.5, color=GOODK,
                  anchor="end", bold=True))
    f.append(text(ox + ax_w - 4, oy - dd(1.0) * ax_h - 10, "густина дефектів D", size=11.5,
                  color=BADK, anchor="end", bold=True))

    # дві вертикалі: старт і зрілість
    for tt, lab, c in [(0.06, "запуск процесу", MUTED), (0.85, "зрілий процес", INK)]:
        px = ox + tt * ax_w
        f.append(line(px, oy, px, oy - ax_h, color=c, sw=1.0, dash="3 4"))
    f.append(text(ox + 0.06 * ax_w, oy + 20, "запуск", size=10, color=MUTED))
    f.append(text(ox + 0.06 * ax_w, oy - ax_h - 8, "Y низький,", size=9.5, color=BADK))
    f.append(text(ox + 0.85 * ax_w, oy + 20, "зрілість", size=10, color=INK))

    f.append(text(W / 2, 322,
                  "Інженери методично прибирають джерела дефектів → D у формулі Y ≈ e^(−A·D) падає, вихід росте.",
                  size=11, color=INK))
    f.append(text(W / 2, 342,
                  "Той самий дизайн на зрілому процесі дешевший — без жодної зміни в самому кристалі.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "learning-curve.svg"), W, H, *f)


if __name__ == "__main__":
    fig_probe()
    fig_binning()
    fig_scan_cell()
    fig_few_pins()
    fig_scan_cycle()
    fig_marking_decode()
    fig_date_code()
    fig_errata_revision()
    # детальна версія:
    fig_test_flow()
    fig_ate_channel()
    fig_shmoo()
    fig_bathtub()
    fig_learning_curve()
    print("OK: 13 SVG у", IMG)
