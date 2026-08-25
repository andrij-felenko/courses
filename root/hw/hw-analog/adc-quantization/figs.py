# -*- coding: utf-8 -*-
"""Фігури до теми «Квантування та шум АЦП» (аналогова електроніка).
Фігури теми:
  staircase-error.svg — сходинкова характеристика «вхід=вихід» + пилкоподібна похибка ±q/2
  snr-vs-bits.svg     — граничний SNR за розрядністю (8/12/16/24 біти), по 6 дБ за розряд
Фігури вставки hist-quantization-noise.md:
  dither-fix.svg      — тихий синус: без дизера похибка корельована (гармоніки) → з дизером білий шум
Фігури вставки math-quantization-noise.md:
  uniform-density.svg      — рівномірна густина 1/q на ±q/2; площа під e² дає q³/12, /q = q²/12
  oversampling-density.svg — та сама потужність q²/12 під вузьким і широким спектром; корисна смуга
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def staircase_error():
    """Угорі: ідеальна пряма «вхід=вихід» проти сходинок АЦП (крок q).
    Унизу: похибка округлення пиляє між −q/2 і +q/2, перетинаючи нуль на кожному рівні."""
    W, H = 720, 560
    p = []

    # ── параметри сітки ──
    n_steps = 6            # скільки кроків показуємо
    x0, y0 = 90, 240       # лівий-нижній кут верхньої панелі (вісь входу / нуль виходу)
    span = 480             # ширина по входу
    q_px = span / n_steps  # піксельний крок q
    top_h = 190            # висота верхньої панелі (по виходу)

    # ── ВЕРХНЯ ПАНЕЛЬ: характеристика ──
    # осі
    p.append(line(x0, y0, x0 + span + 20, y0, color=INK, sw=1.6))           # вісь входу
    p.append(line(x0, y0, x0, y0 - top_h - 10, color=INK, sw=1.6))          # вісь виходу
    p.append(text(x0 + span / 2, y0 + 34, "вхідна напруга (неперервна)", size=12, color=MUTED))
    p.append(text(x0 - 60, y0 - top_h / 2, "код", size=12, bold=True, color=MUTED))
    p.append(text(x0 - 60, y0 - top_h / 2 + 16, "АЦП", size=12, bold=True, color=MUTED))

    # ідеальна пряма вхід=вихід (пунктир)
    p.append(line(x0, y0, x0 + span, y0 - top_h, color=NEG, sw=1.8, dash="5 4"))
    p.append(text(x0 + span - 6, y0 - top_h + 2, "ідеал: вихід = вхід", size=12, color=NEG, anchor="end"))

    # сходинки: на кожному кроці вихід стрибає на один рівень
    step_y = top_h / n_steps
    sx = x0
    sy = y0
    seg = []
    for i in range(n_steps):
        # горизонтальна полиця на висоті центру сходинки
        cy = y0 - (i + 0.5) * step_y
        seg.append((sx, cy, sx + q_px, cy))
        sx += q_px
    for (a, b, c, d) in seg:
        p.append(line(a, b, c, d, color=POS, sw=2.6))
    # вертикальні переходи між полицями
    for i in range(1, n_steps):
        xv = x0 + i * q_px
        p.append(line(xv, y0 - (i - 0.5) * step_y, xv, y0 - (i + 0.5) * step_y, color=POS, sw=1.4, dash="2 3"))
    p.append(text(x0 + 2 * q_px + 6, y0 - 2.5 * step_y - 8, "сходинки АЦП", size=12, color=POS, anchor="start"))

    # позначка кроку q на осі входу
    qa = x0 + 3 * q_px
    p.append(line(qa, y0 + 6, qa, y0 + 18, color=INK, sw=1.2))
    p.append(line(qa + q_px, y0 + 6, qa + q_px, y0 + 18, color=INK, sw=1.2))
    p.append(line(qa, y0 + 12, qa + q_px, y0 + 12, color=INK, sw=1.4))
    p.append(text(qa + q_px / 2, y0 + 12 - 4, "q", size=13, bold=True))

    # ── НИЖНЯ ПАНЕЛЬ: похибка квантування (пилка) ──
    ex0 = x0
    e_mid = 410                 # середня лінія (e = 0)
    e_amp = 44                  # піксельний розмах до ±q/2
    p.append(line(ex0, e_mid, ex0 + span + 20, e_mid, color=MUTED, sw=1.4))   # нуль похибки
    p.append(line(ex0, e_mid - e_amp - 6, ex0, e_mid + e_amp + 6, color=INK, sw=1.6))  # вісь похибки
    p.append(text(ex0 + span / 2, e_mid + e_amp + 30, "та сама вхідна напруга", size=12, color=MUTED))

    # рівні +q/2 та −q/2 (пунктир)
    p.append(line(ex0, e_mid - e_amp, ex0 + span, e_mid - e_amp, color=FIELD, sw=1.2, dash="4 4"))
    p.append(line(ex0, e_mid + e_amp, ex0 + span, e_mid + e_amp, color=FIELD, sw=1.2, dash="4 4"))
    p.append(text(ex0 + span + 6, e_mid - e_amp + 4, "+q/2", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(ex0 + span + 6, e_mid + e_amp + 4, "−q/2", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(ex0 - 60, e_mid + 4, "похибка e", size=12, bold=True, color=MUTED))

    # пилка: усередині кроку похибка лінійно йде від −q/2 до +q/2, на межі — стрибок назад
    saw = []
    for i in range(n_steps):
        xa = ex0 + i * q_px
        # від +q/2 (на лівому краю кроку вхід трохи більший за рівень) до −q/2
        saw.append((xa, e_mid - e_amp))
        saw.append((xa + q_px, e_mid + e_amp))
    d_saw = "M" + " L".join("%.1f %.1f" % (sx, sy) for sx, sy in saw)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d_saw, POS))
    p.append(text(ex0 + 4.5 * q_px, e_mid - e_amp - 10, "пиляє ±q/2", size=12, color=POS, anchor="middle"))

    # підпис-висновок
    b, _, _ = textbox(W / 2, H - 26,
                      "Похибка округлення ніколи не виходить за ±q/2 і перетинає нуль на кожному рівні.\n"
                      "Коли сигнал гуляє багатьма рівнями, ця пилка діє як рівномірний білий шум.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, 'staircase-error.svg'), W, H, *p,
           title="Сходинки АЦП і пилкоподібна похибка квантування ±q/2")


def snr_vs_bits():
    """Стовпчики граничного SNR за розрядністю: по 6.02 дБ за розряд + зсув 1.76 дБ."""
    W, H = 700, 430
    p = []

    bits = [8, 12, 16, 24]
    snr = [6.02 * n + 1.76 for n in bits]     # 49.9, 74.0, 98.1, 146.2
    cols = [MUTED, NEG, FIELD, POS]
    fills = {MUTED: "#eef0f2", NEG: "#eaf0fd", FIELD: "#eafaf0", POS: "#fdecea"}

    ox, oy = 90, 340          # початок осей
    ax_h = 270                # висота осі рівнів
    plot_w = 520
    p.append(line(ox, oy, ox, oy - ax_h - 10, color=INK, sw=1.8))      # вісь SNR
    p.append(line(ox, oy, ox + plot_w, oy, color=INK, sw=1.8))         # вісь розрядності
    p.append(text(ox - 56, oy - ax_h / 2, "SNR", size=13, bold=True, color=MUTED))
    p.append(text(ox - 56, oy - ax_h / 2 + 16, "(дБ)", size=13, bold=True, color=MUTED))
    p.append(text(ox + plot_w / 2, oy + 50, "розрядність N (біт)", size=13, bold=True, color=MUTED))

    smax = 160.0              # верх шкали дБ
    def y_of(db):
        return oy - ax_h * (db / smax)

    # сітка по 24 дБ (= 4 розряди)
    for g in range(0, int(smax) + 1, 24):
        gy = y_of(g)
        p.append(line(ox, gy, ox + plot_w, gy, color="#e5e7eb", sw=1))
        p.append(text(ox - 10, gy + 4, "%d" % g, size=11, color=MUTED, anchor="end"))

    bw = 70
    gap = (plot_w - len(bits) * bw) / (len(bits) + 1)
    for i, (n, s, c) in enumerate(zip(bits, snr, cols)):
        cx = ox + gap + i * (bw + gap) + bw / 2
        top = y_of(s)
        p.append(rect(cx - bw / 2, top, bw, oy - top, fill=fills[c], stroke=c, sw=2))
        p.append(text(cx, top - 10, "%.0f дБ" % s, size=13, bold=True, color=c))
        p.append(text(cx, oy + 24, "%d біт" % n, size=13, bold=True, color=c))

    # стрілка-крок «+4 біти = +24 дБ» між 12 та 16 біт
    cx12 = ox + gap + 1 * (bw + gap) + bw / 2
    cx16 = ox + gap + 2 * (bw + gap) + bw / 2
    y12 = y_of(snr[1]); y16 = y_of(snr[2])
    midx = (cx12 + cx16) / 2
    p.append(line(midx, y12, midx, y16, color=INK, sw=1.6))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
             % (midx - 4, y16 + 6, midx + 4, y16 + 6, midx, y16, INK))
    p.append(text(midx + 8, (y12 + y16) / 2, "+4 біти", size=11, bold=True, anchor="start"))
    p.append(text(midx + 8, (y12 + y16) / 2 + 15, "= +24 дБ", size=11, bold=True, anchor="start"))

    b, _, _ = textbox(W / 2, H - 22,
                      "SNR = 6.02·N + 1.76 дБ: кожен розряд піднімає стелю рівно на 6 дБ.\n"
                      "Це межа ідеального АЦП — реальний завжди трохи нижче неї.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, 'snr-vs-bits.svg'), W, H, *p,
           title="Граничний SNR ідеального АЦП за розрядністю")


def dither_fix():
    """Вставка hist: тихий повільний синус, що гуляє лише кількома рівнями.
    Ліворуч — без дизера: похибка йде гладкою корельованою пилкою → на спектрі
    гострі гармоніки (спотворення). Праворуч — підмішали пів-LSB шуму (дизер):
    округлення знову випадкове, похибка некорельована → рівна шумова підлога."""
    W, H = 760, 490
    p = []

    # параметри спільної сітки рівнів
    n_lv = 5                    # скільки рівнів квантування показуємо
    lv_gap = 30                 # піксельна відстань між рівнями (= q)
    base = 150                  # y найнижчого рівня
    levels = [base - i * lv_gap for i in range(n_lv)]   # знизу вгору

    panels = [
        (60,  "Без дизера: похибка корельована", POS),
        (430, "З дизером (≈пів-LSB): похибка випадкова", FIELD),
    ]

    def sine_y(px, x_left, span, cy, amp, ph=0.0):
        t = (px - x_left) / span
        return cy - amp * math.sin(2 * math.pi * 1.0 * t + ph)

    span = 250
    cy = base - 2 * lv_gap      # середина розмаху синуса (між рівнями)
    amp = 1.35 * lv_gap         # амплітуда: гуляє ~2.7 рівня — «тихий» сигнал

    import random
    random.seed(7)

    for (x0, head, hue) in panels:
        # рівні квантування (горизонталі)
        for ly in levels:
            p.append(line(x0, ly, x0 + span, ly, color="#dfe3e8", sw=1))
        p.append(text(x0 + span / 2, base + 28, "час →", size=11, color=MUTED))
        p.append(text(x0 - 6, levels[2] + 4, "рівні", size=10, color=MUTED, anchor="end"))
        p.append(text(x0 - 6, levels[2] + 17, "АЦП", size=10, color=MUTED, anchor="end"))

        # неперервний синус
        pts = []
        for k in range(0, span + 1, 3):
            px = x0 + k
            pts.append((px, sine_y(px, x0, span, cy, amp)))
        d = "M" + " L".join("%.1f %.1f" % (a, b) for a, b in pts)
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>'
                 % (d, MUTED))

        # відліки: беремо значення синуса (+ дизер у правій панелі) і квантуємо до найближчого рівня
        n_samp = 26
        dith = (hue == FIELD)
        qpts = []
        for s in range(n_samp):
            px = x0 + span * s / (n_samp - 1)
            yv = sine_y(px, x0, span, cy, amp)
            if dith:
                yv += (random.random() - 0.5) * lv_gap     # ±пів-LSB трикутний-ish дизер
            # найближчий рівень
            qy = min(levels, key=lambda L: abs(L - yv))
            qpts.append((px, qy))
        # сходинкова квантована лінія
        for s in range(n_samp):
            px, qy = qpts[s]
            if s > 0:
                ppx, pqy = qpts[s - 1]
                p.append(line(ppx, pqy, px, pqy, color=hue, sw=2.0))   # полиця
                if abs(qy - pqy) > 0.5:
                    p.append(line(px, pqy, px, qy, color=hue, sw=1.2))  # перехід
            p.append(circle(px, qy, 2.2, fill=hue, stroke=hue, sw=0))

        p.append(text(x0 + span / 2, 44, head, size=12.5, bold=True, color=hue))

        # мікро-спектр під панеллю
        sx0 = x0
        sbase = 300
        sh = 90
        p.append(line(sx0, sbase, sx0 + span, sbase, color=INK, sw=1.4))
        p.append(line(sx0, sbase, sx0, sbase - sh - 6, color=INK, sw=1.4))
        p.append(text(sx0 + span / 2, sbase + 22, "частота →", size=10, color=MUTED))
        p.append(text(sx0 - 6, sbase - sh + 4, "рівень", size=10, color=MUTED, anchor="end"))

        if not dith:
            # основний тон + дискретні гармоніки
            bars = [(0.10, 0.95, "основний"), (0.30, 0.55, None), (0.50, 0.38, None),
                    (0.70, 0.27, None), (0.88, 0.18, None)]
            for fr, hh, lab in bars:
                bx = sx0 + fr * span
                p.append(line(bx, sbase, bx, sbase - sh * hh, color=POS, sw=3))
            p.append(text(sx0 + span / 2, sbase - sh + 2, "гострі гармоніки", size=11,
                          bold=True, color=POS, anchor="middle"))
        else:
            # основний тон + рівна низька шумова підлога
            bx = sx0 + 0.10 * span
            p.append(line(bx, sbase, bx, sbase - sh * 0.95, color=FIELD, sw=3))
            floor = []
            for k in range(0, span + 1, 6):
                jx = sx0 + k
                jy = sbase - sh * (0.16 + 0.05 * random.random())
                floor.append((jx, jy))
            d2 = "M" + " L".join("%.1f %.1f" % (a, b) for a, b in floor)
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d2, FIELD))
            p.append(text(sx0 + span / 2, sbase - sh + 2, "рівна шумова підлога", size=11,
                          bold=True, color=FIELD, anchor="middle"))

    # підпис-висновок
    b, _, _ = textbox(W / 2, H - 36,
                      "Тихий сигнал, що гуляє лише кількома рівнями, без дизера дає корельовану похибку —\n"
                      "на спектрі гострі гармоніки. Пів-LSB дизера робить округлення випадковим: гармоніки\n"
                      "розпливаються в чесну рівну шумову підлогу — рівно ту модель, що описав Беннетт.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, 'dither-fix.svg'), W, H, *p,
           title="Дизер: як спотворення тихого сигналу обертають назад на шум")


def uniform_density():
    """Вставка math: рівномірна густина похибки p(e)=1/q на відрізку [−q/2,+q/2].
    Показуємо два накладені сенси одного відрізка:
      • плоский прямокутник висотою 1/q — його площа (1/q·q) = 1 (повна ймовірність);
      • парабола e² над тим самим відрізком — площа під нею дає інтеграл q³/12,
        а поділена на ширину q — рівно середній квадрат q²/12.
    Праворуч — числова вісь із двома числами, що їх легко сплутати:
    максимум |e| = q/2 проти RMS = q/√12 ≈ 0.289q (RMS помітно менший за півкроку)."""
    W, H = 720, 470
    p = []

    # ── ЛІВА ПАНЕЛЬ: густина + парабола на відрізку ±q/2 ──
    ax = 90                     # x осі похибки (лівий край відрізка = ax)
    span = 300                  # піксельна ширина відрізка q
    q_px = span                 # весь відрізок = один крок q
    mid = ax + span / 2         # центр (e = 0)
    base = 300                  # y осі e (нульова густина / нульове e²)

    # осі
    p.append(line(ax - 30, base, ax + span + 40, base, color=INK, sw=1.6))   # вісь e
    p.append(line(mid, base + 8, mid, 70, color=INK, sw=1.6))                # вісь значень (густина / e²)
    p.append(text(ax + span + 44, base + 4, "e", size=13, bold=True, anchor="start"))

    # межі −q/2, +q/2 та нуль
    for xv, lab in [(ax, "−q/2"), (mid, "0"), (ax + span, "+q/2")]:
        p.append(line(xv, base - 4, xv, base + 4, color=INK, sw=1.2))
        p.append(text(xv, base + 22, lab, size=12, bold=(lab != "0"),
                      color=(INK if lab == "0" else NEG)))

    # плоский прямокутник густини висотою 1/q
    dens_top = base - 70        # рівень висоти 1/q
    p.append(rect(ax, dens_top, q_px, base - dens_top, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(line(ax - 30, dens_top, ax, dens_top, color=NEG, sw=1.4, dash="4 3"))
    p.append(text(ax - 34, dens_top + 4, "1/q", size=13, bold=True, color=NEG, anchor="end"))
    p.append(text(mid, dens_top + 26, "площа = 1/q · q = 1", size=12, bold=True, color=NEG))
    p.append(text(mid, dens_top + 44, "рівномірна p(e)", size=11, color=NEG))

    # парабола e² над тим самим відрізком (заштрихована — інтеграл q³/12)
    top = 92                    # y вершини параболи на краях відрізка (e=±q/2)
    def para_y(xv):
        u = (xv - mid) / (span / 2)          # −1..+1
        return base - (base - top) * (u * u) # 0 у центрі, max на краях
    pts = [(ax, para_y(ax))]
    k = ax
    while k <= ax + span:
        pts.append((k, para_y(k)))
        k += 5
    pts.append((ax + span, base))
    pts.append((ax, base))
    d = "M" + " L".join("%.1f %.1f" % (a, b) for a, b in pts) + " Z"
    p.append('<path d="%s" fill="#fdecea" fill-opacity="0.55" stroke="%s" stroke-width="2.2"/>'
             % (d, POS))
    p.append(text(ax + span - 4, top + 24, "e²", size=14, bold=True, italic=True,
                  color=POS, anchor="end"))
    # підпис площі під параболою
    b, _, _ = textbox(mid, base - 118,
                      "площа під e²  →  ∫ = q³/12\n"
                      "поділити на ширину q  →  ⟨e²⟩ = q²/12",
                      size=12, fill="#fff5f4", stroke=POS, color=POS)
    p.append(b)

    p.append(text(mid, 60, "Рівномірна густина 1/q і парабола e² на одному відрізку",
                  size=12.5, bold=True, color=INK))

    # ── ПРАВА СМУГА: два числа поряд (max проти RMS) ──
    nx = ax + span + 96         # центр правого блоку осі |e|
    ny0 = 130                   # верх
    ny1 = 300                   # низ = e = 0 (спільна база з лівою віссю)
    p.append(line(nx, ny1, nx, ny0 - 6, color=INK, sw=1.6))
    p.append(text(nx, ny0 - 14, "|e|", size=12, bold=True))
    scale = (ny1 - ny0) / 0.5   # px на одиницю q (0.5q від бази до верху осі)

    def mark(frac, lab, col, side):
        yy = ny1 - scale * frac
        p.append(line(nx - 6, yy, nx + 6, yy, color=col, sw=2))
        if side == "r":
            p.append(text(nx + 12, yy + 4, lab, size=12, bold=True, color=col, anchor="start"))
        else:
            p.append(text(nx - 12, yy + 4, lab, size=12, bold=True, color=col, anchor="end"))

    mark(0.5, "q/2  (максимум)", POS, "r")
    mark(0.2887, "q/√12 ≈ 0.289q  (RMS)", FIELD, "l")
    # стрілка різниці між ними
    ytop = ny1 - scale * 0.5
    ybot = ny1 - scale * 0.2887
    p.append(line(nx - 44, ytop, nx - 44, ybot, color=MUTED, sw=1.2))
    p.append(text(nx - 40, (ytop + ybot) / 2 + 4, "×1.73", size=10, color=MUTED, anchor="start"))

    # підпис-висновок
    b2, _, _ = textbox(W / 2, H - 30,
                       "Похибка рівномірна на ±q/2: густина плоска (площа = 1). Середній квадрат — це площа\n"
                       "під e², усереднена по ширині: q³/12 ÷ q = q²/12, звідки RMS = q/√12 ≈ 0.289q.\n"
                       "Максимум |e| = q/2 більший за RMS у √3 ≈ 1.73 раза: RMS усереднює, а не бере найгірше.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b2)

    render(os.path.join(OUT, 'uniform-density.svg'), W, H, *p,
           title="Рівномірна похибка: інтеграл e² дає q²/12, RMS = q/√12")


def oversampling_density():
    """Вставка math: та сама повна потужність q²/12 під двома спектрами.
    Угорі — повільна вибірка: вузька смуга Найквіста, високий килим щільності.
    Унизу — учетверо швидша: удвічі... ні, учетверо ширша смуга, учетверо нижчий килим
    (площа = та сама q²/12). Зелена корисна смуга сигналу B однакова в обох —
    але внизу вона ловить учетверо меншу частку шуму → удвічі менший RMS у смузі → +6 дБ."""
    W, H = 720, 500
    p = []

    left = 100
    plot_w = 520                # спільна ширина по частоті для обох панелей
    B_px = 92                   # піксельна ширина корисної смуги сигналу (однакова)
    narrow_w = plot_w * 0.25    # вузька смуга Найквіста (повільна вибірка)
    wide_w = plot_w * 1.00      # учетверо ширша смуга (швидша вибірка)
    tall_h = 128                # висота найвищого (вузького) килима
    # площа килима = висота·ширина = стала (та сама потужність q²/12)
    AREA = tall_h * narrow_w

    panels = [
        (196, narrow_w, "Повільна вибірка: вузька смуга Найквіста f_s/2"),
        (392, wide_w,   "Учетверо швидша: вчетверо ширша смуга — вчетверо нижчий килим"),
    ]

    for (baseline, band_w, head) in panels:
        carpet_h = AREA / band_w          # висота килима так, щоб площа була стала
        top = baseline - carpet_h
        head_y = baseline - tall_h - 18   # рядок заголовка панелі (над найвищим килимом)

        # осі панелі
        p.append(line(left, baseline, left + plot_w + 10, baseline, color=INK, sw=1.5))  # частота
        p.append(line(left, baseline, left, baseline - tall_h - 6, color=INK, sw=1.5))   # щільність
        p.append(text(left - 8, baseline - tall_h + 4, "щільн.", size=10, color=MUTED, anchor="end"))
        p.append(text(left + plot_w + 14, baseline + 4, "f", size=12, bold=True, anchor="start"))

        # килим шуму q²/12 (сірий прямокутник) — його ПЛОЩА однакова в обох панелях
        p.append(rect(left, top, band_w, carpet_h, fill="#eef0f2", stroke=MUTED, sw=1.6))
        p.append(text(left + band_w + 10, top + carpet_h / 2 + 4,
                      "площа = q²/12", size=11, bold=True, color=MUTED, anchor="start"))

        # межа смуги Найквіста
        p.append(line(left + band_w, baseline, left + band_w, top - 4, color=INK, sw=1.2, dash="3 3"))
        p.append(text(left + band_w, top - 8, "f_s/2", size=11, bold=True, anchor="middle"))

        # корисна смуга сигналу B (зелена, однаковий px у обох) — частка шуму під нею
        p.append(rect(left, top, B_px, carpet_h, fill="#dbf3e5", stroke=FIELD, sw=2))
        p.append(text(left + B_px / 2, baseline + 20, "смуга B", size=11, bold=True, color=FIELD))

        p.append(text(left + plot_w / 2, head_y, head, size=12, bold=True, color=INK,
                      anchor="middle"))

    # підпис-висновок
    b, _, _ = textbox(W / 2, H - 34,
                      "Площа під обома килимами однакова — це та сама повна потужність q²/12 (квантувач той самий).\n"
                      "Швидша вибірка розтягує її по ширшій смузі Найквіста: килим падає. Корисна смуга B (зелена)\n"
                      "однакова, тож унизу під нею вчетверо менше шуму — удвічі менший RMS = +6 дБ = +1 розряд.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, 'oversampling-density.svg'), W, H, *p,
           title="Передискретизація: та сама потужність, ширша смуга, нижчий килим")


if __name__ == '__main__':
    staircase_error()
    snr_vs_bits()
    dither_fix()
    uniform_density()
    oversampling_density()
    print("OK: 5 figures ->", OUT)
