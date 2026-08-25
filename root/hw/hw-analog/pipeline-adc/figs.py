# -*- coding: utf-8 -*-
"""Фігури до теми «Конвеєрний АЦП» (цифрова електроніка).
Чотири фігури:
  assembly-line.svg — конвеєр щаблів: кожен віддає кілька біт і передає залишок далі (як цех)
  one-stage.svg     — внутрішність одного щабля: суб-АЦП, ЦАП, віднімання, підсилення (MDAC)
  latency-throughput.svg — затримка vs пропускність: відлік іде кілька тактів, але потік щотакту
  residue-correction.svg — передавальна крива залишку: запас 1.5-біта прощає зсув компаратора
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def assembly_line():
    """Чотири щаблі в ряд: кожен зрізає кілька старших біт і пускає підсилений залишок далі."""
    W, H = 760, 360
    p = []
    cy = 150
    n = 4
    bw, bh = 116, 90
    gap = (W - 60 - n * bw) / (n - 1)
    x0 = 30
    bits = ["3 старші", "наступні 3", "наступні 3", "молодші"]
    # вхід
    p.append(arrow(8, cy, x0, cy, color=INK, sw=2))
    p.append(text(8, cy - 10, "Vвх", size=13, bold=True, color=NEG, anchor="start"))
    for i in range(n):
        x = x0 + i * (bw + gap)
        col = [NEG, INK, INK, FIELD][i]
        p.append(rect(x, cy - bh / 2, bw, bh, fill=FILL, stroke=LINE, sw=1.8))
        p.append(text(x + bw / 2, cy - bh / 2 - 10, "щабель %d" % (i + 1), size=13, bold=True))
        # що щабель видає вниз — кілька біт коду
        p.append(text(x + bw / 2, cy - 8, bits[i], size=12, color=col, bold=True))
        p.append(text(x + bw / 2, cy + 12, "біти", size=11, color=MUTED))
        # стрілка коду вниз
        p.append(arrow(x + bw / 2, cy + bh / 2, x + bw / 2, cy + bh / 2 + 34, color=col, sw=1.8))
        # стрілка залишку праворуч
        if i < n - 1:
            xr = x + bw
            p.append(arrow(xr, cy, xr + gap, cy, color=POS, sw=2.2))
            p.append(text(xr + gap / 2, cy - 12, "залишок", size=11, bold=True, color=POS))
            p.append(text(xr + gap / 2, cy + 16, "×підсил.", size=10, color=MUTED))
    # шина-збирач унизу
    busy = cy + bh / 2 + 50
    p.append(rect(x0, busy, W - 60, 38, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(W / 2, busy + 24, "цифровий збирач: складає біти всіх щаблів у повний код",
                  size=12, bold=True, color=FIELD))
    render(os.path.join(OUT, 'assembly-line.svg'), W, H, *p,
           title="Конвеєр щаблів: кожен зрізає кілька біт і передає залишок далі")


def one_stage():
    """Один щабель зсередини: груба оцінка → відновлення → віднімання → підсилення = залишок."""
    W, H = 740, 380
    p = []
    cy = 165
    # вхід
    inx = 30
    p.append(arrow(8, cy, inx, cy, color=NEG, sw=2.2))
    p.append(text(8, cy - 10, "Vвх", size=13, bold=True, color=NEG, anchor="start"))
    # вузол розгалуження
    nx = inx + 6
    p.append(circle(nx, cy, 4, fill=INK, stroke=INK))
    # суб-АЦП (груба оцінка кількох біт)
    adx, ady = nx + 40, cy - 95
    p.append(rect(adx, ady, 150, 56, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(adx + 75, ady + 24, "груба оцінка", size=13, bold=True))
    p.append(text(adx + 75, ady + 42, "(суб-АЦП, кілька біт)", size=11, color=MUTED))
    p.append(line(nx, cy, nx, ady + 28, color=NEG, sw=1.8))
    p.append(arrow(nx, ady + 28, adx, ady + 28, color=NEG, sw=1.8))
    # біти цього щабля — вниз/праворуч від суб-АЦП
    p.append(arrow(adx + 75, ady + 56, adx + 75, ady + 90, color=FIELD, sw=1.8))
    p.append(text(adx + 75, ady + 80, "біти щабля", size=11, bold=True, color=FIELD, anchor="middle"))
    # ЦАП — відновлює грубу оцінку назад у напругу
    dax, day = adx + 200, ady
    p.append(rect(dax, day, 110, 56, fill=FILL, stroke=LINE, sw=1.8))
    p.append(text(dax + 55, day + 24, "ЦАП", size=13, bold=True))
    p.append(text(dax + 55, day + 42, "код → V", size=11, color=MUTED))
    p.append(arrow(adx + 150, ady + 28, dax, day + 28, color=INK, sw=1.8))
    # суматор-віднімання
    sx = dax + 55
    sy = cy
    p.append(circle(sx, sy, 16, fill=BG, stroke=LINE, sw=1.8))
    p.append(text(sx, sy + 5, "−", size=20, bold=True, color=NEG))
    p.append(arrow(dax + 55, day + 56, sx, sy - 16, color=INK, sw=1.8))      # оцінка-напруга вниз
    # сам вхід також іде в суматор (нижньою гілкою)
    p.append(line(nx, cy, nx, cy + 70, color=NEG, sw=1.8))
    p.append(line(nx, cy + 70, sx - 60, cy + 70, color=NEG, sw=1.8))
    p.append(line(sx - 60, cy + 70, sx - 60, sy, color=NEG, sw=1.8))
    p.append(arrow(sx - 60, sy, sx - 16, sy, color=NEG, sw=1.8))
    p.append(text(sx - 38, cy + 84, "вхід як є", size=11, color=NEG))
    # підсилювач залишку
    gx = sx + 40
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (gx, cy - 26, gx, cy + 26, gx + 64, cy, FILL, LINE))
    p.append(text(gx + 22, cy + 5, "×2ᵏ", size=16, bold=True))
    p.append(arrow(sx + 16, cy, gx, cy, color=POS, sw=2))
    p.append(text(sx + 30, cy - 12, "залишок", size=11, bold=True, color=POS))
    # вихід — наступному щаблю
    p.append(arrow(gx + 64, cy, gx + 120, cy, color=POS, sw=2.2))
    p.append(text(gx + 120, cy - 10, "до наступного", size=12, bold=True, color=POS, anchor="end"))
    p.append(text(gx + 120, cy + 16, "щабля", size=12, bold=True, color=POS, anchor="end"))

    b, _, _ = textbox(W / 2, 348,
                      "Щабель грубо вимірює вхід, відновлює цю оцінку назад у напругу, віднімає її\n"
                      "й підсилює недомір — цей «залишок» і несе всю недопрацьовану точність далі.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'one-stage.svg'), W, H, *p,
           title="Один щабель зсередини: оцінка → віднімання → підсилення залишку")


def latency_throughput():
    """Косі смуги: один відлік проходить 4 щаблі за 4 такти (затримка), але потік виходить щотакту."""
    W, H = 740, 400
    p = []
    ox, oy = 80, 70
    rows = 4          # щаблі
    cols = 7          # такти
    cw, ch = 78, 46
    # сітка тактів згори
    for c in range(cols):
        x = ox + c * cw
        p.append(text(x + cw / 2, oy - 12, "t%d" % (c + 1), size=12, bold=True, color=MUTED))
    # підписи щаблів зліва
    for r in range(rows):
        y = oy + r * ch
        p.append(text(ox - 12, y + ch / 2 + 4, "щабель %d" % (r + 1), size=12, anchor="end"))
        # тонка лінійка рядка
        p.append(line(ox, y, ox + cols * cw, y, color="#e5e7eb", sw=1))
    p.append(line(ox, oy + rows * ch, ox + cols * cw, oy + rows * ch, color="#e5e7eb", sw=1))

    # чотири відліки A,B,C,D — кожен діагоналлю вниз-праворуч
    samples = [("A", NEG, "#eaf0fd"), ("B", FIELD, "#eafaf0"),
               ("C", POS, "#fdecea"), ("D", INK, "#eef2f7")]
    for s, (lbl, col, fillc) in enumerate(samples):
        for r in range(rows):
            c = s + r
            if c >= cols:
                continue
            x = ox + c * cw
            y = oy + r * ch
            p.append(rect(x + 4, y + 5, cw - 8, ch - 10, fill=fillc, stroke=col, sw=1.6, rx=4))
            p.append(text(x + cw / 2, y + ch / 2 + 5, lbl, size=14, bold=True, color=col))

    # стрілка «затримка» вздовж діагоналі A
    lat_x = ox + 3.5 * cw
    p.append(line(ox + 2, oy - 2, lat_x, oy + rows * ch + 2, color=MUTED, sw=1.4, dash="4 4"))
    p.append(text(lat_x + 8, oy + rows * ch - 6, "затримка: 4 такти на відлік",
                  size=12, bold=True, color=MUTED, anchor="start"))
    # стрілка «пропускність» — готові коди щотакту знизу
    fy = oy + rows * ch + 34
    p.append(text(ox - 12, fy + 4, "готовий код", size=12, anchor="end", color=FIELD))
    for c in range(rows - 1, cols):
        x = ox + c * cw
        lbl = samples[c - rows + 1][0]
        p.append(rect(x + 4, fy - 14, cw - 8, 28, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
        p.append(text(x + cw / 2, fy + 4, lbl, size=13, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 372,
                      "Кожен відлік повзе крізь усі щаблі кілька тактів — це затримка.\n"
                      "Та щойно конвеєр повний, готові коди сиплються ЩОТАКТУ — повна швидкість.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'latency-throughput.svg'), W, H, *p,
           title="Затримка проти пропускності: відлік іде довго, потік — щотакту")


def residue_correction():
    """Передавальна крива залишку: з запасом (1.5 біта) зсунутий поріг лишає залишок у межах,
    наступний щабель домірює — похибку компаратора виправлено цифрою."""
    W, H = 740, 410
    p = []
    ox, oy = 90, 320
    axw, axh = 540, 240
    # осі
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))               # вхід щабля →
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))               # залишок ↑
    p.append(text(ox + axw / 2, oy + 40, "вхід щабля (частка шкали)", size=12, bold=True))
    p.append(text(ox - 60, oy - axh / 2, "залишок", size=12, bold=True))
    # межі залишку, які приймає наступний щабель: ±повна шкала наступного
    top = oy - axh + 30
    bot = oy - 20
    p.append(line(ox, top, ox + axw, top, color=MUTED, sw=1.2, dash="5 4"))
    p.append(line(ox, bot, ox + axw, bot, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(ox + axw + 4, top + 4, "+межа", size=11, color=MUTED, anchor="start"))
    p.append(text(ox + axw + 4, bot + 4, "−межа", size=11, color=MUTED, anchor="start"))

    mid = (top + bot) / 2
    # «класична» 1-біт крива: дві ділянки з повним розмахом, що впритул торкаються межі (зелена)
    seg = axw / 2
    p.append(line(ox, bot, ox + seg, top, color=FIELD, sw=2.6))
    p.append(line(ox + seg, bot, ox + axw, top, color=FIELD, sw=2.6))
    p.append(text(ox + seg * 0.5, mid - 70, "без запасу:", size=11, bold=True, color=FIELD))
    p.append(text(ox + seg * 0.5, mid - 54, "залишок б'є в стелю", size=11, color=FIELD))

    # «1.5-біта»: три ділянки, кожна лише пів-розмаху — є вільний коридор (синя), зсув порога не страшний
    z1, z2 = ox + axw / 3, ox + 2 * axw / 3
    half = (mid - top) * 0.92
    # три похилі сегменти в межах коридору
    p.append(line(ox, mid + half, z1, mid - half, color=NEG, sw=2.6))
    p.append(line(z1, mid + half, z2, mid - half, color=NEG, sw=2.6))
    p.append(line(z2, mid + half, ox + axw, mid - half, color=NEG, sw=2.6))
    # пороги переходів
    for zx in (z1, z2):
        p.append(line(zx, oy, zx, top, color="#e5e7eb", sw=1))
    # зсунутий поріг (показуємо, що залишок усе одно в коридорі)
    zsh = z1 + 26
    p.append(line(zsh, mid - half * 0.4, zsh, mid + half * 0.6, color=POS, sw=2, dash="3 3"))
    p.append(text(zsh + 6, mid + half * 0.6 + 14, "поріг зсунувся —", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(zsh + 6, mid + half * 0.6 + 30, "залишок ще в межах", size=11, color=POS, anchor="start"))
    p.append(text(z2 + 26, mid + 70, "із запасом (1.5 біта):", size=11, bold=True, color=NEG, anchor="start"))
    p.append(text(z2 + 26, mid + 86, "коридор прощає похибку", size=11, color=NEG, anchor="start"))

    b, _, _ = textbox(W / 2, 384,
                      "Без запасу залишок упирається в межу — зсув компаратора її перевищує, біт пропав.\n"
                      "Із запасом 1.5-біта залишок завжди в коридорі: наступний щабель домірює, цифра виправляє.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'residue-correction.svg'), W, H, *p,
           title="Запас 1.5-біта: зсунутий поріг не губить код, наступний щабель домірює")


def transfer_15bit():
    """Точна передавальна крива щабля «1.5 біта»: вхід у ±Vref, два пороги ±Vref/4,
    три цифри D∈{0,1,2}, залишок 2·Vвх−(D−1)·Vref і межі ±Vref, у які він завжди влазить.
    Показано зсунутий поріг — залишок усе одно в межах, помилку добере наступний щабель."""
    W, H = 780, 580
    p = []
    ox, oy = 120, 310              # початок осей (нуль по вертикалі — mid)
    axw = 520
    span = 180                     # піврозмах у px, що відповідає ±Vref по y
    mid = oy                       # y=0 (залишок 0) посередині
    # осі
    p.append(line(ox, mid - span - 18, ox, mid + span + 18, color=INK, sw=2))     # залишок ↑
    p.append(line(ox - 8, mid, ox + axw + 18, mid, color=INK, sw=2))              # вхід →
    p.append(text(ox + axw + 10, mid + 22, "Vвх", size=13, bold=True, anchor="end"))
    p.append(text(ox + 2, mid - span - 26, "залишок", size=12, bold=True, anchor="start"))
    # мітки по x: −Vref, −Vref/4, +Vref/4, +Vref
    def xat(frac):     # frac у частках Vref: −1..+1
        return ox + (frac + 1) / 2 * axw
    for frac, lab in [(-1.0, "−Vref"), (-0.25, "−Vref/4"), (0.25, "+Vref/4"), (1.0, "+Vref")]:
        x = xat(frac)
        p.append(line(x, mid - 4, x, mid + 4, color=INK, sw=1.5))
        p.append(text(x, mid + 22, lab, size=11, color=MUTED))
    # межі, у які має влізти залишок (вхід наступного щабля): ±Vref
    p.append(line(ox, mid - span, ox + axw, mid - span, color=MUTED, sw=1.2, dash="5 4"))
    p.append(line(ox, mid + span, ox + axw, mid + span, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(ox + axw + 8, mid - span, "+Vref", size=11, color=MUTED, anchor="start"))
    p.append(text(ox + axw + 8, mid + span, "−Vref", size=11, color=MUTED, anchor="start"))
    # пороги суб-АЦП: вертикальні світлі лінії на ±Vref/4
    for frac in (-0.25, 0.25):
        x = xat(frac)
        p.append(line(x, mid - span, x, mid + span, color="#e5e7eb", sw=1))
    # три сегменти залишку = 2·Vвх − (D−1)·Vref, кожен нахил +2, кожен ходить від −Vref до +Vref
    #   D=0: Vвх∈[−Vref,−Vref/4] → залишок 2Vвх+Vref  : від −Vref до +Vref/2
    #   D=1: Vвх∈[−Vref/4,+Vref/4] → залишок 2Vвх    : від −Vref/2 до +Vref/2
    #   D=2: Vвх∈[+Vref/4,+Vref] → залишок 2Vвх−Vref : від −Vref/2 до +Vref
    def seg(fx0, fx1, fy0, fy1, col=NEG):
        p.append(line(xat(fx0), mid - fy0 * span, xat(fx1), mid - fy1 * span, color=col, sw=2.8))
    seg(-1.0, -0.25, -1.0, 0.5)     # D=0
    seg(-0.25, 0.25, -0.5, 0.5)     # D=1
    seg(0.25, 1.0, -0.5, 1.0)       # D=2
    # підписи цифр над кожним сегментом (трохи нижче верхньої межі, щоб не злитися з нею)
    p.append(text(xat(-0.62), mid - span - 6, "D=0", size=12, bold=True, color=NEG))
    p.append(text(xat(0.0),   mid - span - 6, "D=1", size=12, bold=True, color=NEG))
    p.append(text(xat(0.66),  mid - span - 6, "D=2", size=12, bold=True, color=NEG))
    # зсунутий поріг: правий поріг «поплив» праворуч; сегмент D=1 продовжується трохи далі,
    # але залишок 2·Vвх усе одно нижчий за +Vref → у межах
    xsh = xat(0.42)
    p.append(line(xsh, mid - span * 0.5, xsh, mid + span * 0.5, color=POS, sw=2, dash="4 3"))
    p.append(line(xat(0.25), mid - 0.5 * span, xsh, mid - 0.84 * span, color=POS, sw=2.6))  # продовжений D=1
    p.append(text(xat(0.25) + 4, mid + 60, "поріг зсунувся —", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(xat(0.25) + 4, mid + 76, "залишок 0.84·Vref < Vref: ще в межах", size=11, color=POS, anchor="start"))
    # формула на полотні
    b, _, _ = textbox(W / 2, 58,
                      "залишок = 2·Vвх − (D−1)·Vref,   D∈{0,1,2}   — нахил +2, крок −Vref на кожному порозі",
                      size=12, fill="#eef2ff", stroke=NEG, color=INK)
    p.append(b)
    b2, _, _ = textbox(W / 2, 548,
                       "Кожен сегмент ходить лише від −Vref до +Vref — рівно вхідний діапазон наступного щабля.\n"
                       "Тому навіть зсунутий поріг не викидає залишок за межі: помилку добере наступний щабель.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b2)
    render(os.path.join(OUT, 'transfer-15bit.svg'), W, H, *p,
           title="Передавальна крива щабля «1.5 біта»: три цифри, залишок завжди в ±Vref")


def shift_add():
    """Складання коду зі зсувом: кожен щабель дає 2-бітну цифру Dᵢ∈{0,1,2}, ваги сусідніх
    щаблів перекриваються на 1 розряд; стовпчики складаються з переносом у фінальний код.
    Числа фінального рядка РАХУЮТЬСЯ з пар щаблів — тож рівність завжди справжня."""
    # 4 щаблі, кожен дає 2-бітну цифру; вага молодшого біта щабля i = 2^(N-1-i).
    # Отже пари займають стовпчики (i, i+1) у полі шириною ncol = N+1.
    N = 4
    ncol = N + 1                                  # 5 бінарних розрядів на виході
    digits = [1, 2, 1, 2]                          # Dᵢ∈{0,1,2}: «2» = поріг спрацював, є перекрив
    # істинний код = Σ Dᵢ·2^(N-1-i)  (i=0..N-1) — рахуємо, не задаємо руками
    value = sum(d * (1 << (N - 1 - i)) for i, d in enumerate(digits))
    result = format(value, '0%db' % ncol)          # у двійковий рядок сталої ширини
    pair = [format(d, '02b') for d in digits]      # 2-бітний запис кожної цифри

    W, H = 760, 440
    p = []
    x0, y0 = 70, 92
    colw = 60
    rowh = 44
    fld = x0 + 150                                 # ліва межа поля стовпчиків
    # шапка — ваги розрядів (старший ліворуч)
    for c in range(ncol):
        cx = fld + c * colw
        p.append(text(cx + colw / 2, y0 - 8, "2^%d" % (ncol - 1 - c), size=11, color=MUTED))
    colors = [NEG, INK, INK, FIELD]
    for i in range(N):
        ry = y0 + 8 + i * rowh
        col = colors[i]
        p.append(text(x0, ry + (rowh - 10) / 2 + 4, "щабель %d" % (i + 1),
                      size=12, bold=True, color=col, anchor="start"))
        p.append(text(x0 + 96, ry + (rowh - 10) / 2 + 4, "D=%d" % digits[i],
                      size=12, bold=True, color=col, anchor="start"))
        # 2 біти цифри лягають у стовпчики i (старший) та i+1 (молодший)
        for j, b in enumerate(pair[i]):
            c = i + j
            cx = fld + c * colw
            p.append(rect(cx + 4, ry, colw - 8, rowh - 10, fill="#f4f6f8", stroke=col, sw=1.6, rx=4))
            p.append(text(cx + colw / 2, ry + (rowh - 10) / 2 + 4, b, size=15, bold=True, color=col))
    # лінія додавання
    ly = y0 + 8 + N * rowh + 6
    p.append(line(fld - 10, ly, fld + ncol * colw, ly, color=INK, sw=2))
    p.append(text(fld - 20, ly - rowh / 2, "+", size=22, bold=True, color=POS, anchor="end"))
    # результат — РАХОВАНИЙ код
    p.append(text(x0, ly + 8 + (rowh - 10) / 2 + 4, "код = %d" % value, size=12, bold=True, anchor="start"))
    for c in range(ncol):
        cx = fld + c * colw
        p.append(rect(cx + 4, ly + 8, colw - 8, rowh - 10, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
        p.append(text(cx + colw / 2, ly + 8 + (rowh - 10) / 2 + 4, result[c], size=15, bold=True, color=FIELD))
    # позначка спільного (перекривного) стовпчика між щаблями 1 і 2
    oc = fld + 1 * colw + colw / 2
    p.append(text(oc, y0 + 8 + 2 * rowh - 2, "↕ спільний розряд", size=10, bold=True, color=POS))
    b, _, _ = textbox(W / 2, ly + 96,
                      "Молодший біт кожного щабля стоїть у тому самому стовпчику, що старший біт наступного —\n"
                      "ваги перекриваються на 1 розряд. Складання з переносом зводить перекрив у єдиний код;\n"
                      "зайва «двійка» від зсунутого компаратора переливається переносом угору — код правильний.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'shift-add.svg'), W, H, *p,
           title="Складання зі зсувом: перекривні розряди сусідніх щаблів додаються з переносом")


def origin_timeline():
    """Родовід конвеєра: субдіапазон (1950-ті) → цифрова корекція Льюїса–Ґрея (1987)
    → аналогове усереднення Сона (1988) → надлишковий щабель 1.5-біта / RSD (1992).
    Показує, що архітектура — не один винахід, а ланцюг: субдіапазон дав ідею поділу,
    цифрова корекція зняла тягар точних компараторів, RSD-щабель зробив її дешевою."""
    W, H = 820, 470
    p = []
    ax = 90                      # вертикальна вісь часу
    top, bot = 80, 410
    p.append(line(ax, top, ax, bot, color=INK, sw=2.4))
    p.append(text(ax, top - 20, "час", size=12, bold=True, color=MUTED))
    p.append(arrow(ax, top + 6, ax, top - 8, color=INK, sw=2.4))

    # вузли: (частка осі 0..1, рік, заголовок, підпис-хто, колір, заливка)
    nodes = [
        (0.00, "1950-ті", "Субдіапазонний АЦП",
         "грубо → залишок → точно;\nщоб зменшити число компараторів", MUTED, "#eef2f7"),
        (0.34, "1987", "Цифрова корекція (пайплайн)",
         "Льюїс і Ґрей, Берклі:\nзалишок несе похибку, цифра її\nдобирає — компаратори можна\nробити грубими", NEG, "#eaf0fd"),
        (0.60, "1988", "Аналогове усереднення",
         "Сон, Томпсетт, Лакшмікумар,\nBell Labs: інша гілка — правити\nрозкид конденсаторів у аналозі", INK, "#eef2f7"),
        (0.86, "1992", "Щабель 1.5-біта · RSD",
         "Льюїс та ін. — надлишковий\nщабель на 3 стани; Джінетті,\nЄсперс, Вандемелебрук — принцип\nнадлишкової знакової цифри", FIELD, "#eafaf0"),
    ]
    for frac, year, head, who, col, fillc in nodes:
        y = top + frac * (bot - top)
        # маркер на осі
        p.append(circle(ax, y, 7, fill=col, stroke=col, sw=1.6))
        # рік ліворуч від осі
        p.append(text(ax - 16, y + 4, year, size=13, bold=True, color=col, anchor="end"))
        # картка праворуч
        cx = ax + 40
        lines = who.split("\n")
        bw = 470
        bh = 26 + len(lines) * 16
        p.append(rect(cx, y - bh / 2, bw, bh, fill=fillc, stroke=col, sw=1.7))
        p.append(text(cx + 12, y - bh / 2 + 18, head, size=13, bold=True, color=col, anchor="start"))
        for i, ln in enumerate(lines):
            p.append(text(cx + 12, y - bh / 2 + 36 + i * 16, ln, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, 'origin-timeline.svg'), W, H, *p,
           title="Родовід конвеєра: від субдіапазону до надлишкового щабля 1.5-біта")


if __name__ == '__main__':
    assembly_line()
    one_stage()
    latency_throughput()
    residue_correction()
    transfer_15bit()
    shift_add()
    origin_timeline()
    print("OK: 7 figures ->", OUT)
