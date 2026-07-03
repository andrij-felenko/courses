# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: три виходи з чипа до динаміка ────────────────────────────────
def fig_three_exits():
    W, H = 780, 430
    f = []
    f.append(text(W/2, 26, "Три дороги від чисел у RAM до звуку", size=17, bold=True))

    # джерело — буфер відліків у RAM
    src = fitbox(30, 175, 130, 80,
                 "Буфер відліків\nу RAM\n(PCM, числа)",
                 size=13, fill="#eef2ff", stroke=NEG, bold=True)
    f.append(src)
    # спільний вузол DMA
    f.append(fitbox(190, 190, 90, 50, "DMA", size=14, fill="#f4f6f8", bold=True))
    f.append(arrow(160, 215, 190, 215, sw=2))

    # три гілки праворуч від DMA
    bx = 330            # старт рамок доріжок
    bw = 250            # ширина рамки доріжки
    ys = [70, 200, 330] # центри трьох доріжок
    labels = [
        ("Внутрішній ЦАП + підсилювач",
         "8 біт на ніжці GPIO25/26 →\nаналог → зовнішній підсилювач",
         "#eafaf1", FIELD),
        ("I2S → зовнішній ЦАП/кодек",
         "цифрою в мікросхему: ЦАП + класу D\nв одному корпусі (напр. MAX98357A)",
         "#fff8e6", "#b8860b"),
        ("PDM — 1-бітний потік",
         "щільність імпульсів = амплітуда →\nФНЧ або PDM-підсилювач",
         "#fdecf0", POS),
    ]
    # вертикальна шина від DMA до трьох відгалужень
    f.append(line(280, 215, 305, 215, sw=2))
    f.append(line(305, ys[0], 305, ys[2], sw=2))
    for y in ys:
        f.append(arrow(305, y, bx, y, sw=2))

    # три доріжки збігаються у спільний вузол перед динаміком
    merge_x = bx + bw + 40
    for (title, sub, fill, stroke), y in zip(labels, ys):
        f.append(fitbox(bx, y-42, bw, 84, title + "\n" + sub,
                        size=12, fill=fill, stroke=stroke, bold=False))
        # горизонтальний відрізок від рамки до вертикальної шини злиття
        f.append(line(bx+bw, y, merge_x, y, sw=2))
    # вертикальна шина злиття й одна стрілка в динамік
    f.append(line(merge_x, ys[0], merge_x, ys[2], sw=2))
    f.append(arrow(merge_x, 200, merge_x+28, 200, sw=2))

    # спільний динамік праворуч
    sx = merge_x + 28
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d Z" fill="#f4f6f8" stroke="%s" stroke-width="2"/>'
             % (sx+2, 185, sx+2, 215, sx+34, 232, sx+34, 168, INK))
    f.append(text(sx+18, 254, "динамік", size=12, color=MUTED))

    render(os.path.join(IMG, 'three-exits.svg'), W, H, *f)


# ── Фігура 2: кадр I2S — три дроти й слоти лівого/правого каналу ────────────
def fig_i2s_frame():
    W, H = 760, 340
    f = []
    f.append(text(W/2, 26, "I2S: три дроти несуть стерео-потік", size=17, bold=True))

    x0, x1 = 150, 720          # межі осей у часі
    labs_x = 20

    # ── WS (word select): лівий рівень / правий рівень ──
    yws = 80
    f.append(text(labs_x, yws+4, "WS", size=13, bold=True, anchor="start"))
    f.append(text(labs_x, yws+22, "(канал)", size=10, color=MUTED, anchor="start"))
    half = (x1 - x0)/2
    # низький = лівий, високий = правий
    f.append(line(x0, yws+15, x0+half, yws+15, color=NEG, sw=2.5))          # low = L
    f.append(line(x0+half, yws+15, x0+half, yws-15, color=NEG, sw=2.5))     # перехід
    f.append(line(x0+half, yws-15, x1, yws-15, color=NEG, sw=2.5))          # high = R
    f.append(text(x0+half/2, yws-24, "лівий", size=11, color=NEG))
    f.append(text(x0+half+half/2, yws-24, "правий", size=11, color=NEG))

    # ── BCLK: бітовий такт (пачка імпульсів) ──
    ybc = 170
    f.append(text(labs_x, ybc+4, "BCLK", size=13, bold=True, anchor="start"))
    f.append(text(labs_x, ybc+22, "(біт-такт)", size=10, color=MUTED, anchor="start"))
    nbits = 16
    step = (x1 - x0)/nbits
    for i in range(nbits):
        xa = x0 + i*step
        f.append(line(xa, ybc+12, xa+step*0.5, ybc+12, color=INK, sw=1.6))
        f.append(line(xa+step*0.5, ybc+12, xa+step*0.5, ybc-12, color=INK, sw=1.6))
        f.append(line(xa+step*0.5, ybc-12, xa+step, ybc-12, color=INK, sw=1.6))
        f.append(line(xa+step, ybc-12, xa+step, ybc+12, color=INK, sw=1.6))

    # ── SD: біти даних (MSB першим) ──
    ysd = 260
    f.append(text(labs_x, ysd+4, "SD", size=13, bold=True, anchor="start"))
    f.append(text(labs_x, ysd+22, "(дані)", size=10, color=MUTED, anchor="start"))
    bits = [1,0,1,1,0,0,1,0, 0,1,1,0,1,0,0,1]
    for i, b in enumerate(bits):
        xa = x0 + i*step
        yb = ysd-12 if b else ysd+12
        f.append(line(xa, yb, xa+step, yb, color=FIELD, sw=2.4))
        if i < len(bits)-1 and bits[i] != bits[i+1]:
            yn = ysd-12 if bits[i+1] else ysd+12
            f.append(line(xa+step, yb, xa+step, yn, color=FIELD, sw=2.4))
    f.append(line(x0+half, ysd-30, x0+half, ysd+30, color=MUTED, sw=1, dash="4 4"))
    f.append(text(x0+half/2, ysd+52, "16 біт лівого відліку", size=11, color=MUTED))
    f.append(text(x0+half+half/2, ysd+52, "16 біт правого", size=11, color=MUTED))

    render(os.path.join(IMG, 'i2s-frame.svg'), W, H, *f)


# ── Фігура 3: PDM — щільність імпульсів кодує амплітуду ─────────────────────
def fig_pdm_density():
    W, H = 760, 360
    f = []
    f.append(text(W/2, 26, "PDM: густота одиниць малює хвилю", size=17, bold=True))

    x0, x1 = 60, 720
    N = 120
    mid = 150
    amp = 70

    # аналогова хвиля (ціль), сірим
    pts = []
    for i in range(N+1):
        x = x0 + (x1-x0)*i/N
        t = i/N
        y = mid - amp*math.sin(2*math.pi*t)
        pts.append((x, y))
    d = "M" + " L".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, MUTED))
    f.append(text(x1-4, mid-amp-8, "цільова хвиля", size=11, color=MUTED, anchor="end"))

    # 1-бітний потік: імпульс угору, коли треба «більше», вниз — «менше».
    # дельта-сигма (перша різниця акумулятора) — груба, але наочна модель.
    ytop = 250
    ybot = 320
    acc = 0.0
    barw = (x1-x0)/N
    for i in range(N):
        t = i/N
        target = 0.5 + 0.5*math.sin(2*math.pi*t)   # 0..1 бажана густина
        acc += target
        bit = 1 if acc >= 1.0 else 0
        if bit:
            acc -= 1.0
        x = x0 + barw*i
        if bit:
            f.append(rect(x, ytop, barw*0.8, ybot-ytop, fill=POS, stroke=POS, sw=0.5, rx=1))
    f.append(text(x0, ybot+22, "1-бітний потік: де хвиля вища — одиниць густіше",
                  size=11, color=INK, anchor="start"))

    # рамка-підказка про ФНЧ
    f.append(fitbox(x0, ytop-48, 250, 34,
                    "усереднити (ФНЧ) → назад аналог",
                    size=11, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, 'pdm-density.svg'), W, H, *f)


# ── Фігура 4: три блоки в корпусі I2S-підсилювача ──────────────────────────
def fig_amp_blocks():
    W, H = 800, 380
    f = []
    f.append(text(W/2, 26, "Всередині корпусу: цифра заходить, звук виходить", size=16, bold=True))

    # межа кристала — велика пунктирна рамка
    cx0, cy0, cw, ch = 175, 90, 460, 200
    f.append(rect(cx0, cy0, cw, ch, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=10))
    f.append('<path d="M%d %d h%d v%d h%d" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="5 4"/>'
             % (cx0, cy0, cw, ch, -cw, MUTED))
    f.append(text(cx0+cw-8, cy0+16, "один кристал", size=10, color=MUTED, anchor="end"))

    by = 150            # верх блоків
    bh = 90
    bw = 132
    gap = 18
    bx0 = cx0 + 16
    # три блоки-станції
    f.append(fitbox(bx0, by, bw, bh, "Приймач I2S\n\nсам розпізнає\nформат",
                    size=11, fill="#eef2ff", stroke=NEG, bold=True))
    bx1 = bx0 + bw + gap
    f.append(fitbox(bx1, by, bw, bh, "ЦАП\n(дельта-сигма)\n\nаналог — лише\nвсередині",
                    size=11, fill="#eafaf1", stroke=FIELD, bold=True))
    bx2 = bx1 + bw + gap
    f.append(fitbox(bx2, by, bw, bh, "Підсилювач\nкласу D\n\nШІМ прямо\nна динамік",
                    size=11, fill="#fff8e6", stroke="#b8860b", bold=True))
    # стрілки між станціями
    f.append(arrow(bx0+bw, by+bh/2, bx1, by+bh/2, sw=2))
    f.append(arrow(bx1+bw, by+bh/2, bx2, by+bh/2, sw=2))

    # три дроти I2S заходять зліва
    lx = 30
    ins = [("BCLK", by+22), ("LRC", by+bh/2), ("DIN", by+bh-22)]
    for name, yy in ins:
        f.append(text(lx, yy+4, name, size=11, bold=True, anchor="start", color=NEG))
        f.append(arrow(lx+44, yy, bx0, yy, color=NEG, sw=1.8))
    f.append(text(lx, by-10, "3 дроти I2S", size=10, color=MUTED, anchor="start"))

    # керувальні ніжки знизу
    gy = cy0 + ch
    f.append(text(bx2-4, gy+22, "GAIN", size=11, bold=True, anchor="end", color=INK))
    f.append(line(bx2-40, by+bh, bx2-40, gy+14, color=INK, sw=1.4, dash="3 3"))
    f.append(text(bx2-4, gy+40, "SD (вимк./канал)", size=11, bold=True, anchor="end", color=POS))
    f.append(line(bx2+40, by+bh, bx2+40, gy+32, color=POS, sw=1.4, dash="3 3"))

    # динамік справа
    f.append(arrow(cx0+cw, by+bh/2, cx0+cw+30, by+bh/2, sw=2))
    sx = cx0 + cw + 30
    yc = by + bh/2
    f.append('<path d="M%d %d L%d %d L%d %d L%d %d Z" fill="#f4f6f8" stroke="%s" stroke-width="2"/>'
             % (sx+2, yc-14, sx+2, yc+14, sx+34, yc+30, sx+34, yc-30, INK))
    f.append(text(sx+18, yc+52, "динамік", size=11, color=MUTED))
    f.append(text(sx+18, by-10, "звук", size=11, color="#b8860b", bold=True))

    render(os.path.join(IMG, 'amp-blocks.svg'), W, H, *f)


# ── Фігура 5: беззфільтровий клас D — котушка глушить ШІМ ───────────────────
def fig_filterless():
    W, H = 800, 340
    f = []
    f.append(text(W/2, 26, "Беззфільтровий клас D: фільтром служить сама котушка", size=15, bold=True))

    # ── зліва: різкий ШІМ-прямокутник ──
    x0 = 40
    xw = 210
    ymid = 170
    amp = 52
    # ШІМ зі змінною шпаруватістю (грубо відтворює синус)
    N = 22
    step = xw / N
    prev_y = ymid + amp
    xs = x0
    for i in range(N):
        t = i / N
        duty = 0.5 + 0.42*math.sin(2*math.pi*t)   # шпаруватість
        xa = x0 + i*step
        xhi = xa + step*duty
        yhi = ymid - amp
        ylo = ymid + amp
        # високий рівень
        f.append(line(xa, yhi, xhi, yhi, color=POS, sw=2))
        # спад
        f.append(line(xhi, yhi, xhi, ylo, color=POS, sw=2))
        # низький до кінця кроку
        f.append(line(xhi, ylo, xa+step, ylo, color=POS, sw=2))
        # підйом на межі кроку
        if i < N-1:
            f.append(line(xa+step, ylo, xa+step, yhi, color=POS, sw=2))
    f.append(text(x0+xw/2, ymid+amp+30, "ШІМ 330 кГц", size=12, color=POS, bold=True))
    f.append(text(x0+xw/2, ymid-amp-14, "різкий прямокутник", size=11, color=MUTED))

    # ── посередині: котушка динаміка ──
    coilx = x0 + xw + 40
    coilw = 150
    ccy = ymid
    # намалювати «пружинку»
    loops = 6
    lw = coilw/loops
    d = "M%.1f %.1f" % (coilx, ccy)
    for i in range(loops):
        cxl = coilx + i*lw
        d += " q %.1f -34 %.1f 0" % (lw/2, lw)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK))
    f.append(fitbox(coilx-6, ccy+30, coilw+12, 46,
                    "індуктивність котушки:\n330 кГц — глуха стіна,\nзвук — вільний прохід",
                    size=10.5, fill="#eef2ff", stroke=NEG))
    f.append(arrow(x0+xw+4, ymid, coilx-4, ymid, sw=2))

    # ── справа: плавна хвиля на мембрані ──
    wx0 = coilx + coilw + 40
    ww = 200
    f.append(arrow(coilx+coilw+4, ymid, wx0-4, ymid, sw=2))
    pts = []
    M = 80
    for i in range(M+1):
        x = wx0 + ww*i/M
        y = ymid - amp*math.sin(2*math.pi*i/M)
        pts.append((x, y))
    dd = "M" + " L".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dd, FIELD))
    f.append(text(wx0+ww/2, ymid+amp+30, "плавна хвиля", size=12, color=FIELD, bold=True))
    f.append(text(wx0+ww/2, ymid-amp-14, "рух мембрани", size=11, color=MUTED))

    render(os.path.join(IMG, 'filterless.svg'), W, H, *f)


# ── Фігура 6 (detailed): три формати I2S-кадру ─────────────────────────────
def fig_i2s_formats():
    W, H = 820, 470
    f = []
    f.append(text(W/2, 26, "Три формати I2S-кадру: де стоїть старший біт", size=16, bold=True))

    x0, x1 = 200, 780          # часова вісь
    labs_x = 20
    half = (x1 - x0) / 2       # межа лівий/правий канал = перемикання WS
    nbits = 8                  # умовно 8 біт на слот, щоб було видно
    step = (x1 - x0) / (2 * nbits)   # ширина одного біта (16 бітів на кадр)

    # ── WS угорі (спільний) ──
    yws = 74
    f.append(text(labs_x, yws + 4, "WS", size=13, bold=True, anchor="start"))
    f.append(line(x0, yws + 14, x0 + half, yws + 14, color=NEG, sw=2.5))
    f.append(line(x0 + half, yws + 14, x0 + half, yws - 14, color=NEG, sw=2.5))
    f.append(line(x0 + half, yws - 14, x1, yws - 14, color=NEG, sw=2.5))
    f.append(text(x0 + half/2, yws - 22, "лівий канал", size=11, color=NEG))
    f.append(text(x0 + half + half/2, yws - 22, "правий канал", size=11, color=NEG))
    # пунктир межі каналу вниз через усі рядки
    f.append(line(x0 + half, yws + 20, 430, yws + 20, color=MUTED, sw=0.8, dash="3 3"))

    def data_row(y, name, offset_bits, note):
        """Малюємо слот даних: 8 «комірок» біта, зсунутих на offset_bits."""
        f.append(text(labs_x, y + 4, name, size=12, bold=True, anchor="start", color=INK))
        f.append(text(labs_x, y + 20, note, size=9, color=MUTED, anchor="start"))
        # лівий слот
        start = x0 + offset_bits * step
        for i in range(nbits):
            xa = start + i * step
            fillc = "#eef2ff" if i == 0 else FILL
            f.append(rect(xa, y - 12, step, 24, fill=fillc, stroke=FIELD, sw=1.2, rx=2))
        f.append(text(start + step/2, y + 5, "MSB", size=8, color=NEG))
        # позначка зсуву, якщо є
        if offset_bits > 0:
            f.append(line(x0, y, start, y, color=POS, sw=1.6))
            f.append(text((x0 + start)/2, y - 16, "зсув 1 такт", size=8.5, color=POS))

    data_row(150, "Philips (I2S)", 1, "старший біт відстає від WS на 1 такт BCLK")
    data_row(240, "Ліво-вирівняний", 0, "старший біт одразу з перемиканням WS")

    # право-вирівняний: дані притиснуто до КІНЦЯ слоту (правий край лівого слоту = half)
    y = 330
    f.append(text(labs_x, y + 4, "Право-вирівняний", size=12, bold=True, anchor="start", color=INK))
    f.append(text(labs_x, y + 20, "молодший біт притиснуто до кінця слоту", size=9, color=MUTED, anchor="start"))
    end = x0 + half            # кінець лівого слоту
    for i in range(nbits):
        xa = end - (nbits - i) * step
        fillc = "#eef2ff" if i == 0 else FILL
        f.append(rect(xa, y - 12, step, 24, fill=fillc, stroke=FIELD, sw=1.2, rx=2))
    f.append(text(end - nbits*step + step/2, y + 5, "MSB", size=8, color=NEG))
    f.append(text(end - step/2, y + 5, "LSB", size=8, color=MUTED))

    f.append(fitbox(x0, 388, x1 - x0, 46,
                    "Передавач і приймач мусять домовитися про формат:\n"
                    "інакше приймач читає біти зсунутими — спотворення або шум.",
                    size=11.5, fill="#fff8e6", stroke="#b8860b"))
    render(os.path.join(IMG, 'i2s-formats.svg'), W, H, *f)


# ── Фігура 7 (detailed): формування шуму — три спектри ─────────────────────
def fig_noise_shaping():
    W, H = 840, 380
    f = []
    f.append(text(W/2, 26, "Куди дівається шум квантування", size=16, bold=True))

    # три панелі поруч
    pw = 240
    gap = 30
    px = [40, 40 + pw + gap, 40 + 2*(pw + gap)]
    baseY = 300      # вісь частоти (низ графіка)
    topY = 70        # верх області
    sigW = 46        # ширина звукової смуги на осі

    titles = ["Найквіст", "Передискретизування", "Формування шуму"]
    for k, x in enumerate(px):
        # осі
        f.append(line(x, baseY, x + pw, baseY, color=INK, sw=1.4))          # частота →
        f.append(line(x, baseY, x, topY, color=INK, sw=1.4))                # потужність ↑
        f.append(text(x + pw, baseY + 16, "частота →", size=9, color=MUTED, anchor="end"))
        f.append(text(x + pw/2, topY - 12, titles[k], size=12, bold=True))
        # звукова смуга (зелена) — вузька зліва, однакова в усіх
        f.append(rect(x + 1, baseY - 70, sigW, 70, fill="#d7f2e2", stroke=FIELD, sw=1.2, rx=2))
        f.append(text(x + sigW/2 + 2, baseY + 16, "звук", size=9, color=FIELD))

    # панель 1 — Найквіст: шум рівний, лише у вузькій смузі, високий стовпчик
    x = px[0]
    # шум лежить понад сигналом у тій самій вузькій смузі — високий стовпчик над зеленим
    f.append(rect(x + 1, baseY - 150, sigW, 80, fill="#f3d0cc", stroke=POS, sw=1))
    f.append(mtext(x + pw*0.62, baseY - 90, ["увесь шум", "у вузькій", "смузі —", "багато"],
                   size=9.5, color=POS))

    # панель 2 — передискретизування: шум розмазано на всю широку смугу, низько й рівно
    x = px[1]
    f.append(rect(x + 1, baseY - 22, pw - 2, 22, fill="#f3d0cc", stroke=POS, sw=1))
    f.append(mtext(x + pw*0.66, baseY - 46, ["та сама енергія", "розтягнута —", "у смузі звуку", "її мало"],
                   size=9.5, color=POS))
    f.append(text(x + pw - 4, baseY - 30, "≈3 дБ/окт", size=9, color=INK, anchor="end"))

    # панель 3 — формування: шум завалено внизу, задерто гіркою вгорі
    x = px[2]
    pts = []
    N = 60
    for i in range(N + 1):
        t = i / N
        xx = x + 1 + (pw - 2) * t
        # низько зліва, круто вгору справа (гірка шуму)
        h = 4 + 100 * (t ** 2.2)
        pts.append((xx, baseY - h))
    d = "M%.1f %.1f " % (x + 1, baseY) + " ".join("L%.1f %.1f" % p for p in pts) + \
        " L%.1f %.1f Z" % (x + pw - 1, baseY)
    f.append('<path d="%s" fill="#f3d0cc" stroke="%s" stroke-width="1"/>' % (d, POS))
    f.append(mtext(x + pw*0.34, baseY - 150, ["шум вигнано", "вгору, поза", "чутне"],
                   size=9.5, color=POS))
    f.append(text(x + pw - 4, baseY - 30, "≈9 дБ/окт", size=9, color=INK, anchor="end"))

    f.append(text(W/2, H - 12,
                  "Корисний звук (зелений) незмінний у всіх трьох; міняється лише форма шуму (рожевий).",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, 'noise-shaping.svg'), W, H, *f)


# ── Фігура 8 (detailed): кільце DMA-буферів у часі ─────────────────────────
def fig_dma_ring():
    W, H = 780, 440
    f = []
    f.append(text(W/2, 26, "Кільце DMA-буферів: потік без розривів", size=16, bold=True))

    cx, cy, R = 250, 210, 118
    n = 4
    import math as _m
    # чотири шматки по колу
    states = [("грає\n(DMA→шина)", "#fff8e6", "#b8860b"),
              ("наповнює\n(ядро)",   "#eef2ff", NEG),
              ("готовий",            "#eafaf1", FIELD),
              ("готовий",            "#eafaf1", FIELD)]
    for i in range(n):
        a = -_m.pi/2 + 2*_m.pi*i/n
        bx = cx + R*_m.cos(a)
        by = cy + R*_m.sin(a)
        lab, fill, stroke = states[i]
        f.append(fitbox(bx - 62, by - 30, 124, 60, "шматок %d\n%s" % (i+1, lab),
                        size=11, fill=fill, stroke=stroke, bold=(i < 2)))
    # стрілка руху по колу (DMA просувається)
    f.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2" marker-end="url(#arrow)"/>'
             % (cx + R + 34, cy - 8, R + 34, R + 34, cx + 8, cy + R + 34, MUTED))
    f.append(text(cx, cy + R + 70, "DMA просувається по колу", size=10, color=MUTED))
    f.append(text(cx, cy - 4, "по колу,", size=11, color=INK))
    f.append(text(cx, cy + 12, "без кінця", size=11, color=INK))

    # права колонка — часова шкала й недобіг
    tx = 500
    f.append(fitbox(tx, 90, 250, 62,
                    "Поки ГРАЄ шматок 1,\nядро НАПОВНЮЄ шматок 2.\nВстигло за T_шматка → потік цілий.",
                    size=11, fill="#eafaf1", stroke=FIELD))
    f.append(fitbox(tx, 172, 250, 62,
                    "Переривання на стику:\n«шматок віддано» → долий.\nБільше шматків = більший запас.",
                    size=11, fill="#eef2ff", stroke=NEG))
    f.append(fitbox(tx, 254, 250, 78,
                    "Ядро спізнилось?\nШматок спорожнів → апаратура\nповторює старе / дає тишу →\nрозрив на хвилі = КЛАЦ.",
                    size=11, fill="#fdecf0", stroke=POS))
    render(os.path.join(IMG, 'dma-ring.svg'), W, H, *f)


# ── Фігура (math): розмивання розриває кореляцію похибки ────────────────────
def fig_dither_decorrelation():
    import math as _m
    W, H = 840, 400
    f = []
    f.append(text(W/2, 26, "Що дає розмивання: похибка перестає повторювати сигнал", size=15, bold=True))

    pw = 350
    gap = 90
    px = [40, 40 + pw + gap]
    axY = 150        # рівень «0» верхнього графіка (сигнал коло одного LSB)
    lsb = 34         # висота одного LSB на екрані
    x0 = 10          # відступ усередині панелі

    heads = ["Без розмивання", "З трикутним розмиванням (TPDF)"]
    for k, x in enumerate(px):
        f.append(text(x + pw/2, 52, heads[k], size=12.5, bold=True,
                      color=(POS if k == 0 else FIELD)))
        # три рівні квантування (сходинки), горизонтальні пунктири
        for lv in range(3):
            yy = axY + lsb - lv * lsb
            f.append(line(x + x0, yy, x + x0 + pw - 2*x0, yy,
                          color="#d0d0d0", sw=1, dash="3,3"))
        f.append(text(x + x0 - 2, axY + lsb + 4, "n·LSB", size=8, color=MUTED, anchor="end"))

    N = 120
    # тихий синус амплітудою ~1 LSB коло рівня квантування
    def sig(i):
        t = i / N
        return 0.95 * lsb * _m.sin(2 * _m.pi * 1.5 * t)

    # ── ліва панель: округлення без розмивання — сходинки, зчеплені з сигналом
    x = px[0]
    sig_pts = []
    q_pts = []
    for i in range(N + 1):
        xx = x + x0 + (pw - 2*x0) * i / N
        s = sig(i)
        sig_pts.append((xx, axY + lsb - (s + lsb)/1.0 * 0 - s))  # плавна лінія сигналу
        # квантуємо до найближчого LSB
        q = round(s / lsb) * lsb
        q_pts.append((xx, axY + lsb - lsb + (lsb - q) - lsb*0 + (lsb - q)*0 - q + 0))
    # плавний сигнал (сірий)
    d = "M" + " L".join("%.1f %.1f" % (p[0], axY - sig(i)) for i, p in enumerate(sig_pts))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (d, MUTED))
    # квантований ступінчастий вихід (червоний, «сходинки»)
    qd = []
    for i in range(N + 1):
        xx = x + x0 + (pw - 2*x0) * i / N
        q = round(sig(i) / lsb) * lsb
        qd.append((xx, axY - q))
    step = "M%.1f %.1f " % qd[0]
    for i in range(1, len(qd)):
        step += "L%.1f %.1f L%.1f %.1f " % (qd[i][0], qd[i-1][1], qd[i][0], qd[i][1])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (step, POS))
    # смуга похибки внизу — регулярна, повторює форму (гребінка однакових зубців)
    eb = 300
    f.append(text(x + pw/2, eb - 58, "похибка = сходинки − сигнал", size=9.5, color=INK))
    for i in range(0, N, 6):
        xx = x + x0 + (pw - 2*x0) * i / N
        e = (round(sig(i)/lsb)*lsb - sig(i))
        f.append(line(xx, eb, xx, eb - e * 0.9, color=POS, sw=2))
    f.append(line(x + x0, eb, x + x0 + pw - 2*x0, eb, color=INK, sw=1))
    f.append(mtext(x + pw/2, eb + 16, ["регулярна, зчеплена з сигналом →",
                                       "гармоніки, чутне спотворення"],
                   size=9.5, color=POS, lh=1.25))

    # ── права панель: те саме, але з домішаним TPDF-шумом перед округленням
    x = px[1]
    # той самий сірий сигнал
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
             % ("M" + " L".join("%.1f %.1f" % (x + x0 + (pw-2*x0)*i/N, axY - sig(i))
                                for i in range(N+1)), MUTED))
    # псевдовипадкове TPDF (сума двох рівномірних) — детерміноване для відтворюваності
    import random as _r
    _r.seed(7)
    tri = [ (_r.random() + _r.random() - 1.0) * lsb for _ in range(N+1) ]  # ±1 LSB, трикутне
    qd2 = []
    for i in range(N + 1):
        xx = x + x0 + (pw - 2*x0) * i / N
        q = round((sig(i) + tri[i]) / lsb) * lsb
        qd2.append((xx, axY - q))
    step2 = "M%.1f %.1f " % qd2[0]
    for i in range(1, len(qd2)):
        step2 += "L%.1f %.1f L%.1f %.1f " % (qd2[i][0], qd2[i-1][1], qd2[i][0], qd2[i][1])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (step2, FIELD))
    # смуга похибки внизу — хаотична (різнонапрямлені зубці)
    f.append(text(x + pw/2, eb - 58, "похибка = сходинки − сигнал", size=9.5, color=INK))
    for i in range(0, N, 6):
        xx = x + x0 + (pw - 2*x0) * i / N
        e = (round((sig(i)+tri[i])/lsb)*lsb - sig(i))
        f.append(line(xx, eb, xx, eb - e * 0.9, color=FIELD, sw=2))
    f.append(line(x + x0, eb, x + x0 + pw - 2*x0, eb, color=INK, sw=1))
    f.append(mtext(x + pw/2, eb + 16, ["випадкова, не зчеплена →",
                                       "рівний м'який шум, без гармонік"],
                   size=9.5, color=FIELD, lh=1.25))

    render(os.path.join(IMG, 'dither-decorrelation.svg'), W, H, *f)


# ── Фігура (math): |NTF|² = 4·sin²(πf/fs) — форма фільтра шуму ───────────────
def fig_ntf_curve():
    import math as _m
    W, H = 760, 430
    f = []
    f.append(text(W/2, 26, "Фільтр шуму формувача 1-го порядку:  |NTF|² = 4·sin²(πf/fₛ)", size=15, bold=True))

    Lx, Rx = 90, 700       # ліва/права межа осі частоти
    By, Ty = 330, 70       # низ/верх осі потужності
    fmax = 0.5             # вісь у частках fs, від 0 до fs/2
    ymax = 4.0             # |NTF|² від 0 до 4

    def X(fr):  return Lx + (Rx - Lx) * (fr / fmax)
    def Y(v):   return By - (By - Ty) * (v / ymax)

    # осі
    f.append(line(Lx, By, Rx + 10, By, color=INK, sw=1.6))
    f.append(line(Lx, By, Lx, Ty - 6, color=INK, sw=1.6))
    f.append(text(Rx + 6, By + 34, "частота f  (0 … fₛ/2)", size=10, color=INK, anchor="end"))
    f.append(text(Lx - 8, Ty - 10, "|NTF|²", size=10, color=INK, anchor="end"))
    # мітки по осі y
    for v in (1, 2, 3, 4):
        f.append(line(Lx - 4, Y(v), Lx, Y(v), color=INK, sw=1))
        f.append(text(Lx - 8, Y(v) + 4, str(v), size=9, color=MUTED, anchor="end"))
    # мітки по осі x
    f.append(text(Lx, By + 18, "0", size=9, color=MUTED))
    f.append(text(X(0.25), By + 18, "fₛ/4", size=9, color=MUTED))
    f.append(text(X(0.5), By + 18, "fₛ/2", size=9, color=MUTED))

    # крива |NTF|² = 4 sin²(pi f / fs)
    pts = []
    Nn = 200
    for i in range(Nn + 1):
        fr = fmax * i / Nn
        v = 4 * (_m.sin(_m.pi * fr)) ** 2
        pts.append((X(fr), Y(v)))
    d = "M" + " L".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))

    # звукова смуга — вузька коло 0 (in-band), зелена заливка під кривою
    fb = 0.5 / 16          # умовна межа звукової смуги при OSR=16
    band = []
    Nb = 40
    for i in range(Nb + 1):
        fr = fb * i / Nb
        v = 4 * (_m.sin(_m.pi * fr)) ** 2
        band.append((X(fr), Y(v)))
    bd = "M%.1f %.1f " % (X(0), By) + " ".join("L%.1f %.1f" % p for p in band) + \
         " L%.1f %.1f Z" % (X(fb), By)
    f.append('<path d="%s" fill="#d7f2e2" stroke="%s" stroke-width="1.4"/>' % (bd, FIELD))
    f.append(line(X(fb), By, X(fb), Ty + 40, color=FIELD, sw=1, dash="4,3"))
    f.append(mtext(X(fb) + 8, Ty + 70, ["звукова смуга", "(f мала → шум", "≈ розчавлено)"],
                   size=10, color=FIELD, lh=1.25, anchor="start"))

    # нахил на малих f: |NTF|² ≈ (2πf/fs)² — квадрат, +9 дБ/окт
    f.append(line(X(0.06), Y(4*(_m.sin(_m.pi*0.06))**2),
                  X(0.14), Y(4*(_m.sin(_m.pi*0.14))**2), color=NEG, sw=1.4, dash="2,2"))
    f.append(mtext(X(0.22), Y(3.0), ["на малих f:", "|NTF|² ≈ (2πf/fₛ)²", "→ +9 дБ/октаву"],
                   size=10, color=NEG, lh=1.3, anchor="start"))

    # пік коло fs/2
    f.append(circle(X(0.5), Y(4), 3, fill=POS, stroke=POS))
    f.append(text(X(0.5) - 6, Y(4) - 8, "пік = 4 (×6 дБ)", size=9.5, color=POS, anchor="end"))

    f.append(text(W/2, H - 14,
                  "Контур прозорий для звуку (крива тисне шум коло 0) і задирає його до fₛ/2 — геть із чутного.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, 'ntf-curve.svg'), W, H, *f)


# ── Фігура (proj): акумулятор похибки формувача 1-го порядку ────────────────
def fig_pdm_accumulator():
    W, H = 820, 440
    f = []
    f.append(text(W/2, 26, "Акумулятор похибки: пила набігає, поріг видає біт", size=16, bold=True))

    # Симуляція формувача 1-го порядку під сталим входом на чверть шкали.
    FS = 32768
    sample = FS // 4          # +чверть шкали
    N = 40                    # кроків показу
    acc = 0
    traj = [acc]              # значення акумулятора ПІСЛЯ кроку
    bits = []
    for _ in range(N):
        acc += sample
        if acc >= 0:
            bit = 1; out = +FS
        else:
            bit = 0; out = -FS
        acc -= out
        bits.append(bit)
        traj.append(acc)

    # ── графік акумулятора ──
    gx0, gx1 = 100, 770       # межі осі часу
    gy_mid = 150              # рівень порога (нуль) на екрані
    span = FS                 # масштаб: ±FS відображаємо як ±amp_px
    amp_px = 88
    def sx(i): return gx0 + (gx1 - gx0) * i / N
    def sy(v): return gy_mid - amp_px * v / span

    # межі ±FS (тонкі орієнтири)
    f.append(line(gx0, sy(+FS), gx1, sy(+FS), color="#e0e0e0", sw=1))
    f.append(line(gx0, sy(-FS), gx1, sy(-FS), color="#e0e0e0", sw=1))
    f.append(text(gx0 - 10, sy(+FS) + 4, "+FS", size=10, color=MUTED, anchor="end"))
    f.append(text(gx0 - 10, sy(-FS) + 4, "−FS", size=10, color=MUTED, anchor="end"))
    # вісь порога (нуль)
    f.append(line(gx0, gy_mid, gx1, gy_mid, color=MUTED, sw=1.2, dash="5 4"))
    f.append(text(gx0 - 10, gy_mid + 4, "поріг 0", size=11, color=MUTED, anchor="end"))

    # траєкторія акумулятора: ламана по значеннях після кожного кроку
    pts = [(sx(i), sy(v)) for i, v in enumerate(traj[:N+1])]
    d = "M" + " L".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, NEG))
    f.append(text(gx0 + 4, sy(-FS) - 10, "вміст акумулятора крок за кроком",
                  size=11, color=NEG, anchor="start"))

    # ── стовпчики бітів унизу ──
    ytop, ybot = 300, 360
    barw = (gx1 - gx0) / N
    for i, b in enumerate(bits):
        x = sx(i)
        if b:
            f.append(rect(x, ytop, barw * 0.72, ybot - ytop, fill=POS, stroke=POS, sw=0.5, rx=1))
    f.append(text(gx0, ybot + 24, "потік бітів (стовпчик = одиниця)", size=11, color=INK, anchor="start"))

    # підпис-рамка: густина = рівень
    ones = sum(bits)
    note = "вхід +¼ шкали → ≈ %d%% одиниць" % round(100 * ones / N)
    f.append(fitbox(gx1 - 236, ytop - 2, 236, 34, note,
                    size=11.5, fill="#fdecf0", stroke=POS))

    render(os.path.join(IMG, 'pdm-accumulator.svg'), W, H, *f)


# ── Фігура (історія): два родоводи, що сходяться в сучасному чипі ───────────
def fig_two_lineages():
    W, H = 860, 470
    f = []
    f.append(text(W/2, 28, "Два родоводи цього кроку", size=18, bold=True))

    # спільна вісь часу знизу
    ax0, ax1 = 100, 780
    ay = 430
    f.append(line(ax0, ay, ax1, ay, color=MUTED, sw=1.5))
    f.append(text(ax1 + 6, ay + 4, "час", size=11, color=MUTED, anchor="start"))
    years = [1946, 1954, 1962, 1986]
    # роки рівномірно, але з логічним порядком (не в масштабі)
    def yx(idx):
        return ax0 + (ax1 - ax0 - 30) * idx / (len(years) - 1)
    for i, yr in enumerate(years):
        x = yx(i)
        f.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.5))
        f.append(text(x, ay + 22, str(yr), size=12, color=MUTED, bold=True))

    # ── Верхня доріжка: формування шуму / дельта-сигма ──
    ytop = 110
    f.append(text(ax0 - 4, ytop - 44, "Родовід ідеї: формування шуму → дельта-сигма",
                  size=13, bold=True, anchor="start", color=NEG))

    b1 = fitbox(yx(0) - 78, ytop - 26, 156, 62,
                "Делорен (фр.)\nделта-модуляція\nпатент 1946",
                size=11, fill="#eaf0fd", stroke=NEG)
    b2 = fitbox(yx(1) - 78, ytop - 26, 156, 62,
                "Катлер, Bell Labs\nшумоформування\nпатент 1954",
                size=11, fill="#eaf0fd", stroke=NEG)
    b3 = fitbox(yx(2) - 90, ytop - 30, 180, 70,
                "Іносе · Ясуда · Муракамі\nТокійський ун-т, 1962\nдає ім'я «Δ-Σ»",
                size=11, fill="#dbe5fb", stroke=NEG, bold=True)
    f.append(b1); f.append(b2); f.append(b3)
    # стрілки прогресу вздовж доріжки
    f.append(arrow(yx(0) + 80, ytop + 4, yx(1) - 80, ytop + 4, color=NEG, sw=1.8))
    f.append(arrow(yx(1) + 80, ytop + 4, yx(2) - 92, ytop + 4, color=NEG, sw=1.8))

    # ── Нижня доріжка: домовленість Philips ──
    ymid = 270
    f.append(text(ax0 - 4, ymid - 44, "Родовід домовленості: шина між мікросхемами",
                  size=13, bold=True, anchor="start", color="#b8860b"))
    b4 = fitbox(yx(3) - 96, ymid - 30, 192, 70,
                "Philips Semiconductors\nспецифікація I²S\n1 лют. 1986 (ред. 1996)",
                size=11, fill="#fff8e6", stroke="#b8860b", bold=True)
    f.append(b4)

    # ── Злиття в сучасний чип ──
    cx, cy = 720, 200
    conv = textbox(cx, cy, "Сучасний\nаудіо-чип\n(I2S + Δ-Σ ЦАП / PDM)",
                   size=12, fill="#eafaf1", stroke=FIELD, bold=True)
    f.append(conv[0])
    cw, ch = conv[1], conv[2]
    # від Δ-Σ-доріжки вниз-праворуч у чип
    f.append(arrow(yx(2) + 90, ytop + 6, cx - cw/2 - 4, cy - 14, color=NEG, sw=1.9))
    # від Philips-доріжки вгору-праворуч у чип
    f.append(arrow(yx(3) + 96, ymid - 8, cx - cw/2 - 4, cy + 14, color="#b8860b", sw=1.9))

    # підпис-висновок унизу
    f.append(text(W/2, ay + 46,
                  "Ідея дозріла з патентів 1946/1954 до токійської праці 1962; домовленість — 1986. Сходяться в одній ніжці.",
                  size=12, color=INK))

    render(os.path.join(IMG, 'two-lineages.svg'), W, H, *f)


if __name__ == '__main__':
    fig_three_exits()
    fig_i2s_frame()
    fig_pdm_density()
    fig_amp_blocks()
    fig_filterless()
    fig_i2s_formats()
    fig_noise_shaping()
    fig_dma_ring()
    fig_dither_decorrelation()
    fig_ntf_curve()
    fig_pdm_accumulator()
    fig_two_lineages()
    print("figures written to", IMG)
