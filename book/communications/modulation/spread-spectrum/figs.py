# -*- coding: utf-8 -*-
# Фігури теми «Розширений спектр» та її історичної вставки про Геді Ламарр.
# Імпортує спільний svgkit зі scripts/ (не переписувати примітиви).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACCENT = "#b08900"   # бурштиновий акцент (третій колір поряд з POS/NEG/FIELD)


def gauss_path(cx, base_y, peak_h, half_w, color, sw=2.4, n=40):
    """Дзвоник Гаусса як полілінія: центр cx, осідає на base_y, висота peak_h."""
    pts = []
    for i in range(n + 1):
        t = -3.0 + 6.0 * i / n
        x = cx + half_w * t / 3.0
        y = base_y - peak_h * math.exp(-0.5 * t * t)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (" ".join(pts), color, sw))


def grid(ox, oy, w, h, ncol, nrow, color="#e4e4e4"):
    """Сітка частота×час: вертикалі (час) і горизонталі (частота)."""
    p = []
    for i in range(ncol + 1):
        x = ox + w * i / ncol
        p.append(line(x, oy, x, oy - h, color=color, sw=1.0))
    for j in range(nrow + 1):
        y = oy - h * j / nrow
        p.append(line(ox, y, ox + w, y, color=color, sw=1.0))
    return "".join(p)


# ─────────────────────────────────────────────────────────────────────────────
# СТАТТЯ
# ─────────────────────────────────────────────────────────────────────────────

def fig_spread_idea():
    """Та сама потужність: вузька купка vs розмазана по широкій смузі."""
    W, H = 760, 340
    p = []
    base = 250
    # ліва вісь
    p.append(line(70, base, 360, base, color=INK, sw=1.8))
    p.append(gauss_path(200, base, 150, 34, POS, sw=2.6))
    p.append(text(200, 84, "вузька смуга", size=13, color=POS, bold=True))
    p.append(text(200, 272, "висока, помітна, вразлива", size=10.5, color=MUTED))
    # стрілка «розмазати»
    p.append(arrow(380, 165, 440, 165, color=INK, sw=2.2))
    p.append(text(410, 152, "розмазати", size=10.5, color=INK, bold=True))
    # права вісь
    p.append(line(460, base, 750, base, color=INK, sw=1.8))
    p.append(rect(498, base - 30, 224, 30, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=2))
    p.append(line(498, 165, 722, 165, color=MUTED, sw=1.2, dash="4 3"))
    p.append(text(610, 158, "рівень шуму", size=9.5, color=MUTED))
    p.append(text(610, 84, "широка смуга", size=13, color=FIELD, bold=True))
    p.append(text(610, 272, "низька, схожа на шум, стійка", size=10.5, color=MUTED))
    # підсумкова рамка
    p.append(fitbox(60, 296, 640, 30,
                    "Ширша смуга тут — не заради швидкості, а заради надійності й скритності.",
                    size=12, fill="#eef6ef", stroke=FIELD, bold=True))
    render(os.path.join(OUT, "spread-idea.svg"), W, H, *p,
           title="Розширений спектр: навмисне розмазати сигнал по широкій смузі")


def fhss_cells(ox, oy, w, h, ncol, nrow, seq, cell_w, cell_h,
               fill="#e9eefb", stroke=NEG, link=True):
    """Клітинки стрибків за послідовністю seq (рівні частоти, 0..nrow-1)."""
    p = []
    centers = []
    for i, lvl in enumerate(seq):
        cx = ox + w * (i + 0.5) / ncol
        cy = oy - h * (lvl + 0.5) / nrow
        centers.append((cx, cy))
    if link:
        for (x1, y1), (x2, y2) in zip(centers, centers[1:]):
            p.append(line(x1, y1, x2, y2, color=stroke, sw=1.0, dash="3 2"))
    for (cx, cy) in centers:
        p.append(rect(cx - cell_w / 2, cy - cell_h / 2, cell_w, cell_h,
                      fill=fill, stroke=stroke, sw=1.8, rx=3))
    return "".join(p), centers


def fig_fhss():
    """Сітка частота×час: сигнал перестрибує каналами за псевдокодом."""
    W, H = 760, 360
    ox, oy, gw, gh = 100, 300, 620, 220
    ncol, nrow = 12, 9
    seq = [2, 5, 0, 8, 3, 6, 1, 4, 7, 2, 5, 8]
    p = [grid(ox, oy, gw, gh, ncol, nrow)]
    p.append(text(84, 190, "частота", size=11, color=INK, bold=True))
    p.append(text(ox + gw / 2, oy + 30, "час →", size=11, color=INK, bold=True))
    cells, _ = fhss_cells(ox, oy, gw, gh, ncol, nrow, seq, 44, 18)
    p.append(cells)
    p.append(text(ox + gw / 2, oy - gh + 8,
                  "сигнал «перестрибує» каналами — щомиті на новій частоті",
                  size=10.5, color=NEG, bold=True))
    render(os.path.join(OUT, "fhss.svg"), W, H, *p,
           title="Стрибки частоти (FHSS): передавач і приймач скачуть разом")


def fig_fhss_jam():
    """Постійна вузька завада псує лише ті стрибки, що на неї влучили."""
    W, H = 760, 380
    ox, oy, gw, gh = 100, 300, 620, 220
    ncol, nrow = 12, 9
    seq = [2, 5, 4, 1, 6, 3, 8, 4, 5, 2, 7, 4]  # рівень 4 = смуга завади
    jam_lvl = 4
    p = [grid(ox, oy, gw, gh, ncol, nrow)]
    # смуга завади
    jy = oy - gh * (jam_lvl + 0.5) / nrow
    p.append(rect(ox, jy - 12, gw, 24, fill="#fde3e3", stroke=POS, sw=1.6, rx=0))
    p.append(text(ox + gw + 8, jy - 1, "завада", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(ox + gw + 8, jy + 13, "(Wi-Fi)", size=9, color=MUTED, anchor="start"))
    # клітинки: влучені в смугу — червоні з ✗
    for i, lvl in enumerate(seq):
        cx = ox + gw * (i + 0.5) / ncol
        cy = oy - gh * (lvl + 0.5) / nrow
        hit = (lvl == jam_lvl)
        col = POS if hit else FIELD
        bg = "#fde3e3" if hit else "#eef6ef"
        p.append(rect(cx - 22, cy - 9, 44, 18, fill=bg, stroke=col, sw=1.8, rx=3))
        if hit:
            p.append(text(cx, cy + 4, "✗", size=12, color=POS, bold=True))
    p.append(text(ox + gw / 2, oy - gh + 8,
                  "лише 2 з 12 хопів зіпсовано — їх легко перевідправити; решта чисті",
                  size=10.5, color=FIELD, bold=True))
    p.append(fitbox(60, 344, 640, 30,
                    "Bluetooth робить ~1600 стрибків/с по 79 каналах і оминає зайняті (AFH).",
                    size=11, fill="#e9eefb", stroke=NEG, bold=True))
    render(os.path.join(OUT, "fhss-jam.svg"), W, H, *p,
           title="Чому стрибки б'ють заваду: губимо лише кілька хопів")


def square_wave(ox, y_hi, y_lo, x0, x1, bits, color, sw=2.2):
    """Прямокутний сигнал за списком bits (1→верх, 0→низ) на відрізку x0..x1."""
    n = len(bits)
    dx = (x1 - x0) / n
    pts = []
    prev_y = None
    for i, b in enumerate(bits):
        y = y_hi if b else y_lo
        xa = x0 + i * dx
        xb = x0 + (i + 1) * dx
        if prev_y is not None and prev_y != y:
            pts.append("%.1f,%.1f" % (xa, prev_y))
        pts.append("%.1f,%.1f" % (xa, y))
        pts.append("%.1f,%.1f" % (xb, y))
        prev_y = y
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), color, sw))


def fig_dsss():
    """Один біт × 11 чипів коду = широкий розмазаний сигнал у ефір."""
    W, H = 760, 360
    x0, x1 = 150, 660
    code = [1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1]   # 11-чиповий приклад
    # рядок 1: дані = суцільний +1
    p = []
    p.append(text(40, 104, "дані:", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(line(x0, 100, x1, 100, color=FIELD, sw=2.6))
    p.append(text(672, 104, "= 1", size=11, color=FIELD, bold=True, anchor="start"))
    # рядок 2: код
    p.append(text(40, 186, "код:", size=11, color=NEG, bold=True, anchor="start"))
    p.append(square_wave(x0, 170, 222, x0, x1, code, NEG, sw=2.2))
    p.append(text(672, 200, "11 чипів", size=10, color=NEG, bold=True, anchor="start"))
    # рядок 3: у ефір = код (бо дані=+1)
    p.append(text(40, 278, "у ефір:", size=11, color=INK, bold=True, anchor="start"))
    p.append(square_wave(x0, 262, 314, x0, x1, code, INK, sw=2.2))
    p.append(text(672, 292, "= код", size=10, color=MUTED, anchor="start"))
    p.append(fitbox(60, 330, 640, 26,
                    "Один біт розтягнувся на 11 чипів → смуга у 11 разів ширша, густина — нижча.",
                    size=11, fill=FILL, stroke=LINE, bold=True))
    render(os.path.join(OUT, "dsss.svg"), W, H, *p,
           title="Пряма послідовність (DSSS): кожен біт множать на швидкий код")


def fig_despread():
    """Множення на свій код: сигнал стискається, завада розмазується."""
    W, H = 760, 380
    base = 250
    p = []
    p.append(line(80, base, 700, base, color=INK, sw=1.8))
    p.append(text(700, base + 20, "частота", size=10, color=MUTED, anchor="end"))
    # до: розмазаний сигнал (низька широка плита) + вузька висока завада
    p.append(rect(140, base - 26, 230, 26, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=0))
    p.append(text(255, base - 34, "сигнал (розмазаний)", size=9.5, color=FIELD, bold=True))
    p.append(line(290, base, 290, 130, color=POS, sw=4))
    p.append(text(290, 122, "вузька завада", size=9.5, color=POS, bold=True))
    # стрілка ×код
    p.append(arrow(400, 175, 470, 175, color=INK, sw=2.4))
    p.append(text(435, 163, "× код", size=10, color=INK, bold=True))
    # після: сигнал зібрано (висока купка), завада розмазана (низька плита)
    p.append(line(560, base, 560, 120, color=FIELD, sw=5))
    p.append(text(560, 112, "сигнал зібрано", size=9.5, color=FIELD, bold=True))
    p.append(rect(490, base - 18, 200, 18, fill="#fdecec", stroke=POS, sw=1.2, rx=0))
    p.append(text(590, base - 26, "завада розмазана", size=9.5, color=POS, bold=True))
    # підсумок
    p.append(fitbox(60, 300, 640, 26,
                    "Виграш обробки піднімає сигнал над завадою — у стільки разів, скільки чипів.",
                    size=11, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(text(W / 2, 346, "Саме так GPS приймається, хоч його сигнал слабший за шум: код витягує його з-під шуму.",
                  size=10.5, color=INK))
    render(os.path.join(OUT, "despread.svg"), W, H, *p,
           title="Диво приймача: код збирає сигнал, а заваду — розмазує")


def fig_benefits():
    """Три картки-дарунки: завадостійкість, скритність, множинний доступ."""
    W, H = 760, 300
    cards = [
        (FIELD, "🛡️", "Стійкість до завад",
         ["Вузька завада чи глушилка", "псує лише частину —", "решта проходить."]),
        (NEG, "🕵️", "Скритність (LPI)",
         ["Без коду сигнал не", "відрізнити від шуму —", "важко виявити й підслухати."]),
        (ACCENT, "👥", "Множинний доступ",
         ["Багато пар із різними", "кодами говорять в одній", "смузі (це CDMA)."]),
    ]
    p = []
    cw, gap, y, ch = 230, 15, 78, 200
    x = 30
    for col, emoji, head, lines in cards:
        p.append(rect(x, y, cw, ch, fill="#fbfbfb", stroke=col, sw=2, rx=12))
        p.append(text(x + cw / 2, y + 44, emoji, size=24))
        p.append(text(x + cw / 2, y + 76, head, size=13.5, color=col, bold=True))
        for k, ln in enumerate(lines):
            p.append(text(x + cw / 2, y + 108 + k * 19, ln, size=10.5, color=INK))
        x += cw + gap
    render(os.path.join(OUT, "benefits.svg"), W, H, *p,
           title="Три дарунки розширеного спектра за одну ціну")


def fig_real():
    """Чотири картки: де розширений спектр живе насправді."""
    W, H = 760, 300
    cards = [
        (NEG, "Bluetooth", "FHSS", "1600 стрибків/с, 79 каналів"),
        (FIELD, "Wi-Fi (b)", "DSSS", "11-чиповий код Баркера"),
        (ACCENT, "GPS", "DSSS", "сигнал з-під шуму"),
        (POS, "LoRa", "CSS (чирп)", "дальність на кілометри"),
    ]
    p = []
    cw, gap, y, ch = 170, 14, 78, 190
    x = 30
    for col, name, kind, note in cards:
        p.append(rect(x, y, cw, ch, fill="#fbfbfb", stroke=col, sw=2, rx=12))
        p.append(text(x + cw / 2, y + 44, name, size=14.5, color=INK, bold=True))
        p.append(rect(x + cw / 2 - 52, y + 58, 104, 30, fill="#fbfbfb", stroke=col, sw=1.5, rx=6))
        p.append(text(x + cw / 2, y + 78, kind, size=12.5, color=col, bold=True))
        p.append(text(x + cw / 2, y + 116, note, size=10, color=MUTED))
        x += cw + gap
    p.append(text(W / 2, 290,
                  "«Військова» технологія давно живе в кишені кожного.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "real.svg"), W, H, *p,
           title="Хто користується розширеним спектром")


# ─────────────────────────────────────────────────────────────────────────────
# ІСТОРИЧНА ВСТАВКА (Геді Ламарр)
# ─────────────────────────────────────────────────────────────────────────────

def fig_hl_timeline():
    """Вертикальна стрічка часу: від народження до посмертного визнання."""
    W, H = 780, 600
    ax = 250
    rows = [
        ("1914", NEG, "Народилася у Відні", "Гедвіґа Кіслер, з єврейської родини в Австрії"),
        ("1933", NEG, "Кіно і шлюб з Мандлем", "На зустрічах чоловіка-зброяра вбирає знання про озброєння"),
        ("~1937", NEG, "Втеча до Голлівуду", "Тікає від чоловіка й нацистської Європи; стає зіркою MGM"),
        ("1940", FIELD, "Зустріч з Антайлом", "З композитором задумує незаглушуване радіо"),
        ("1942", FIELD, "Патент 2 292 387", "«Secret Communication System» — стрибки по 88 частотах"),
        ("1942", POS, "Флот відкладає", "«Завелике для торпеди» — винахід кладуть під сукно"),
        ("1959", POS, "Патент згасає", "Так і не використаний; винахідники не дістали ні цента"),
        ("1962", MUTED, "Військові беруть схоже", "Споріднену техніку впроваджують — уже після згасання патенту"),
        ("1997", FIELD, "Нарешті визнання", "Премія EFF Pioneer повертає їй ім'я винахідниці"),
        ("2014", FIELD, "Зала слави (посмертно)", "Національна зала слави винахідників США"),
    ]
    p = [line(ax, 92, ax, 580, color=MUTED, sw=3)]
    y = 116
    dy = (580 - 116) / (len(rows) - 1)
    for yr, col, head, sub in rows:
        p.append(circle(ax, y, 7, fill=BG, stroke=col, sw=2.6))
        p.append(text(ax - 22, y + 5, yr, size=12, color=MUTED, bold=True, anchor="end"))
        p.append(text(ax + 26, y - 2, head, size=14.5, color=col, bold=True, anchor="start"))
        p.append(text(ax + 26, y + 16, sub, size=10.5, color=INK, italic=True, anchor="start"))
        y += dy
    render(os.path.join(OUT, "hl-timeline.svg"), W, H, *p,
           title="Геді Ламарр: кінозірка, що запатентувала стрибки частоти")


def fig_hl_problem():
    """Радіокеровану торпеду на одній частоті ворог глушить."""
    W, H = 760, 340
    p = []
    # корабель
    p.append(rect(70, 140, 90, 30, fill="#e9eefb", stroke=NEG, sw=1.8, rx=4))
    p.append(text(115, 160, "корабель", size=10, color=NEG, bold=True))
    p.append(line(115, 140, 115, 112, color=MUTED, sw=2))
    # хвиля керівної частоти
    pts = []
    for i in range(0, 181):
        x = 165 + i * 2.0
        if x > 525:
            break
        y = 170 - 14 * math.sin((x - 165) / 14.0)
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join(pts), FIELD))
    p.append(text(345, 150, "одна керівна частота", size=10.5, color=FIELD, bold=True))
    # торпеда
    p.append(rect(560, 156, 110, 26, fill="#f3f3f3", stroke=INK, sw=1.6, rx=13))
    p.append(circle(660, 169, 6, fill=INK, stroke=INK, sw=0))
    p.append(text(615, 148, "торпеда", size=10, color=INK, bold=True))
    # глушилка (зірка-вибух)
    cx, cy = 420, 235
    star = []
    for k in range(8):
        a = math.pi * k / 4
        r = 18 if k % 2 == 0 else 8
        star.append("%.1f,%.1f" % (cx + r * math.cos(a), cy + r * math.sin(a)))
    p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(star), POS))
    p.append(text(420, 272, "ворожа глушилка", size=11, color=POS, bold=True))
    p.append(line(420, 235, 365, 182, color=POS, sw=2))
    p.append('<line x1="420" y1="235" x2="365" y2="182" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % POS)
    p.append(text(700, 235, "ціль", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(700, 251, "втрачено", size=10, color=POS, anchor="start"))
    p.append(fitbox(60, 290, 640, 32,
                    "Глуши одну частоту — і дорога зброя стає некерованою. Потрібен сигнал, який не «прибити».",
                    size=11, fill="#fbecec", stroke=POS, bold=True))
    render(os.path.join(OUT, "hl-problem.svg"), W, H, *p,
           title="Проблема 1940 року: радіокеровану торпеду легко заглушити")


def fig_hl_idea():
    """Корабель і торпеда стрибають разом за таємним розкладом — FHSS."""
    W, H = 760, 360
    ox, oy, gw, gh = 100, 300, 620, 210
    ncol, nrow = 11, 6
    seq = [2, 5, 0, 4, 1, 5, 2, 4, 0, 3, 5]
    p = [grid(ox, oy, gw, gh, ncol, nrow)]
    p.append(text(84, 200, "частота", size=10.5, color=INK, bold=True))
    p.append(text(ox + gw / 2, oy + 30, "час →", size=10.5, color=INK, bold=True))
    cells, _ = fhss_cells(ox, oy, gw, gh, ncol, nrow, seq, 46, 22, fill="#eef6ef", stroke=FIELD)
    p.append(cells)
    p.append(text(ox + gw / 2, oy - gh + 8,
                  "це — ті самі стрибки частоти, але придумані за десятиліття до Bluetooth",
                  size=11, color=FIELD, bold=True))
    render(os.path.join(OUT, "hl-idea.svg"), W, H, *p,
           title="Ідея Ламарр: хай керівний сигнал стрибає по частотах")


def fig_hl_pianoroll():
    """Однакові перфострічки в передавачі й приймачі = спільний розклад; 88 клавіш."""
    W, H = 760, 360
    p = []
    holes = [(0.05, 0.2), (0.13, 0.55), (0.21, 0.35), (0.29, 0.8), (0.37, 0.5),
             (0.45, 0.65), (0.53, 0.85), (0.61, 0.35), (0.69, 0.95), (0.77, 0.6),
             (0.85, 0.75), (0.93, 0.2)]
    for label, col, ry in [("передавач", NEG, 100), ("приймач", FIELD, 170)]:
        p.append(rect(120, ry, 520, 44, fill="#fbf7ec", stroke=ACCENT, sw=1.6, rx=4))
        p.append(text(110, ry + 26, label, size=10.5, color=col, bold=True, anchor="end"))
        for hx, hy in holes:
            p.append(circle(120 + hx * 520 + 26, ry + 8 + hy * 28, 3.2,
                            fill="#3a3a3a", stroke="#3a3a3a", sw=0))
    p.append(text(380, 244,
                  "однакові дірочки → однакова послідовність частот → ідеальна синхронність",
                  size=10.5, color=INK, bold=True))
    # клавіатура фортепіано
    kx, ky, kw = 300, 280, 16
    nkeys = 14
    for i in range(nkeys):
        p.append(rect(kx + i * kw, ky, kw, 46, fill=BG, stroke=INK, sw=1, rx=0))
    blacks = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12]
    for i in blacks:
        p.append(rect(kx + i * kw + 11, ky, 10, 28, fill="#222", stroke="#222", sw=0, rx=0))
    p.append(text(kx + nkeys * kw / 2, ky + 66,
                  "88 частот = 88 клавіш фортепіано", size=10.5, color=ACCENT, bold=True))
    render(os.path.join(OUT, "hl-pianoroll.svg"), W, H, *p,
           title="Геніальний хід: синхронізація стрічкою механічного піаніно")


def fig_hl_collective():
    """Три рамки: справжня заслуга / чого не робили / чому міф про Wi-Fi."""
    W, H = 760, 400
    p = []
    blocks = [
        (FIELD, "Їхня справжня заслуга",
         ["Конкретна, запатентована реалізація стрибків частоти (синхронізація піанолою, 88 частот)",
          "для незаглушуваної торпеди — сміливо й на десятиліття випереджаючи час."]),
        (ACCENT, "Чого вони не робили",
         ["Самі стрибки частоти існували й раніше: патент Тесли (1903), Ценнек і Телефункен.",
          "Сучасний розширений спектр інженери розвинули значною мірою незалежно, у 1950–60-х."]),
        (POS, "Тож гасло «винайшла Wi-Fi»",
         ["перебільшення: прямої лінії «її патент → Wi-Fi» немає.",
          "Правда чесніша — вона видатна попередниця, чий внесок несправедливо стерли."]),
    ]
    y = 78
    for col, head, lines in blocks:
        p.append(rect(40, y, 680, 96, fill="#fbfbfb", stroke=col, sw=1.8, rx=10))
        p.append(text(58, y + 28, head, size=14, color=col, bold=True, anchor="start"))
        for k, ln in enumerate(lines):
            p.append(text(58, y + 54 + k * 22, ln, size=10.5, color=INK, anchor="start"))
        y += 106
    render(os.path.join(OUT, "hl-collective.svg"), W, H, *p,
           title="Чесно: що належить їм, а що — ні")


def fig_hl_recognition():
    """Забуття (через упередження) → запізніле визнання."""
    W, H = 760, 340
    p = []
    p.append(rect(40, 84, 330, 220, fill="#fbecec", stroke=POS, sw=1.8, rx=12))
    p.append(text(205, 112, "Забуття", size=15, color=POS, bold=True))
    for k, ln in enumerate([
            "«Найвродливіша жінка кіно» —",
            "і нікого не цікавив її розум.",
            "Патент згас раніше, ніж техніку",
            "застосували: ні визнання, ні грошей.",
            "Десятиліття внесок мовчазно",
            "приписували «комусь розумному»."]):
        p.append(text(205, 142 + k * 26, ln, size=10.5, color=INK))
    p.append('<line x1="375" y1="194" x2="405" y2="194" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % INK)
    p.append(rect(410, 84, 330, 220, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=12))
    p.append(text(575, 112, "Визнання", size=15, color=FIELD, bold=True))
    for k, ln in enumerate([
            "1997 — премія EFF Pioneer:",
            "світ нарешті назвав її винахідницею.",
            "2014 — Національна зала слави",
            "винахідників (посмертно).",
            "9 листопада, її день народження,",
            "у німецькомовних країнах — День винахідника."]):
        p.append(text(575, 142 + k * 26, ln, size=10.2, color=INK))
    render(os.path.join(OUT, "hl-recognition.svg"), W, H, *p,
           title="Несправедливість — і запізніле визнання")


def fig_hl_legacy():
    """Що лишилось: ідея всюди; кредит чесно; урок про упередження."""
    W, H = 760, 300
    cards = [
        (NEG, "📡", "Ідея — у кишені",
         ["Стрибки частоти —", "серце Bluetooth; родинні", "техніки — у Wi-Fi і GPS."]),
        (ACCENT, "⚖️", "Кредит — чесно",
         ["Видатна попередниця, чий", "внесок стерли; не «винайшла", "все», але й не «ніщо»."]),
        (FIELD, "👤", "Урок — про упередження",
         ["Талант не питає про", "зовнішність чи фах:", "винахідником буває й кінозірка."]),
    ]
    p = []
    cw, gap, y, ch = 230, 15, 78, 200
    x = 30
    for col, emoji, head, lines in cards:
        p.append(rect(x, y, cw, ch, fill="#fbfbfb", stroke=col, sw=2, rx=12))
        p.append(text(x + cw / 2, y + 44, emoji, size=23))
        p.append(text(x + cw / 2, y + 76, head, size=13, color=col, bold=True))
        for k, ln in enumerate(lines):
            p.append(text(x + cw / 2, y + 108 + k * 19, ln, size=10.5, color=INK))
        x += cw + gap
    render(os.path.join(OUT, "hl-legacy.svg"), W, H, *p,
           title="Що лишилось: ідея — всюди, а урок — подвійний")


if __name__ == "__main__":
    fig_spread_idea()
    fig_fhss()
    fig_fhss_jam()
    fig_dsss()
    fig_despread()
    fig_benefits()
    fig_real()
    fig_hl_timeline()
    fig_hl_problem()
    fig_hl_idea()
    fig_hl_pianoroll()
    fig_hl_collective()
    fig_hl_recognition()
    fig_hl_legacy()
    print("OK: 14 figures ->", OUT)
