# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def wave(x0, y0, w, amp, periods=2.0, phase=0.0, color=INK, sw=2.2, n=80):
    """Полілінія-синусоїда від (x0,y0) завширшки w, амплітуда amp."""
    import math
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * w
        y = y0 - amp * math.sin(2 * math.pi * periods * t + phase)
        pts.append('%.1f,%.1f' % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (' '.join(pts), color, sw))


def wave_noisy(x0, y0, w, amp, periods, phase, noise_amp, color, sw=2.2, n=120):
    """Синусоїда плюс дрібний детермінований 'шум' (видно бруд)."""
    import math
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * w
        clean = amp * math.sin(2 * math.pi * periods * t + phase)
        # детермінований ряд як 'наводка' — однаковий між викликами
        nz = noise_amp * (math.sin(2 * math.pi * 7.3 * t) * 0.6
                          + math.sin(2 * math.pi * 13.1 * t + 1.1) * 0.4)
        y = y0 - clean - nz
        pts.append('%.1f,%.1f' % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (' '.join(pts), color, sw))


# ── Фігура 1: однопровідна vs диференційна ──────────────────────────────────
def fig_single_vs_diff():
    W, H = 760, 470
    f = []

    # --- верх: однопровідна ---
    top = 70
    f.append(text(20, 36, "Однопровідна: сигнал від землі — наводка сідає поверх",
                  size=15, bold=True, anchor="start"))
    # блоки передавач/приймач
    tx, _, _ = textbox(95, top + 30, "ПЕРЕДАВАЧ", size=12, min_w=110)
    rx, _, _ = textbox(665, top + 30, "ПРИЙМАЧ", size=12, min_w=110)
    f.append(tx); f.append(rx)
    # сигнальний провід із наводкою
    f.append(wave_noisy(155, top + 30, 450, 22, 2.0, 0.0, 14, POS, sw=2.4))
    f.append(text(380, top - 6, "сигнальний провід  +  наводка δ", size=12,
                  color=POS, bold=True))
    # земля
    gy = top + 80
    f.append(line(155, gy, 605, gy, color=MUTED, sw=2.0, dash="6 5"))
    f.append(text(380, gy + 18, "спільна земля (хитка опора)", size=12, color=MUTED))
    # вердикт
    v1, _, _ = textbox(665, gy + 2, "читає\nсигнал + δ", size=11, min_w=110,
                       stroke=POS)
    f.append(v1)

    # роздільник
    f.append(line(20, 245, W - 20, 245, color="#dddddd", sw=1.2))

    # --- низ: диференційна ---
    bot = 290
    f.append(text(20, 272, "Диференційна: сигнал — різниця двох; наводка спільна → гасне",
                  size=15, bold=True, anchor="start"))
    tx2, _, _ = textbox(95, bot + 50, "ПЕРЕДАВАЧ", size=12, min_w=110)
    f.append(tx2)
    # два проводи: прямий і інверсний, обидва з ОДНАКОВОЮ наводкою
    f.append(wave_noisy(175, bot + 8, 410, 16, 2.0, 0.0, 12, POS, sw=2.3))
    f.append(wave_noisy(175, bot + 70, 410, 16, 2.0, 3.14159, 12, NEG, sw=2.3))
    f.append(plus(162, bot + 8, r=9))    # маркер «+» біля прямого
    f.append(minus(162, bot + 70, r=9))  # маркер «−» біля інверсного
    # суматор-різниця
    cy_sub = bot + 39
    sub = circle(615, cy_sub, 22, fill="#eafaf1", stroke=FIELD, sw=2)
    f.append(sub)
    f.append(text(615, cy_sub + 6, "−", size=24, color=FIELD, bold=True))
    f.append(line(585, bot + 8, 595, cy_sub - 8, color=POS, sw=2))
    f.append(line(585, bot + 70, 595, cy_sub + 8, color=NEG, sw=2))
    out, _, _ = textbox(700, cy_sub, "2V\n(δ зникла)", size=11, min_w=88,
                        stroke=FIELD)
    f.append(out)
    f.append(line(637, cy_sub, 656, cy_sub, color=FIELD, sw=2))
    f.append(text(615, cy_sub + 40, "різниця", size=11, color=FIELD))

    return render(os.path.join(IMG, 'single-vs-diff.svg'), W, H, *f)


# ── Фігура 2: розклад на синфазну й різницеву ───────────────────────────────
def fig_cm_dm():
    W, H = 720, 420
    f = []
    f.append(text(W / 2, 30, "Дві координати тієї самої пари напруг", size=16, bold=True))

    # вісь зліва: дві висоти над землею
    axL = 150
    base = 360
    f.append(line(axL, base, axL, 70, color=INK, sw=1.8))      # вертикаль
    f.append(line(60, base, 250, base, color=MUTED, sw=2, dash="5 4"))
    f.append(text(155, base + 22, "земля", size=11, color=MUTED))
    # рівні V+ та V−
    yP = 130
    yM = 250
    f.append(line(95, yP, 215, yP, color=POS, sw=3))
    f.append(line(95, yM, 215, yM, color=NEG, sw=3))
    f.append(text(228, yP + 4, "V₊", size=14, color=POS, bold=True, anchor="start"))
    f.append(text(228, yM + 4, "V₋", size=14, color=NEG, bold=True, anchor="start"))
    f.append(text(axL, 56, "висоти над землею", size=12, bold=True))

    # стрілка переходу
    f.append(arrow(290, 215, 380, 215, color=INK, sw=2))
    f.append(text(335, 200, "розклад", size=11, color=MUTED))

    # вісь справа: синфазна (п'єдестал) + різницева
    axR = 540
    f.append(line(axR, base, axR, 70, color=INK, sw=1.8))
    f.append(line(450, base, 630, base, color=MUTED, sw=2, dash="5 4"))
    # синфазний рівень = середнє
    yCM = (yP + yM) / 2
    f.append(line(455, yCM, 625, yCM, color=FIELD, sw=3))
    f.append(text(540, yCM - 10, "Vсинф = спільний п'єдестал", size=12,
                  color=FIELD, bold=True))
    f.append(text(636, yCM + 4, "(сюди\nвлучає\nзавада)", anchor="start", size=10,
                  color=FIELD))
    # різниця — двостороння стрілка навколо п'єдесталу
    f.append(line(axR, yCM, axR, yP, color=POS, sw=2.5))
    f.append(line(axR, yCM, axR, yM, color=NEG, sw=2.5))
    f.append(arrow(axR, yCM - 2, axR, yP, color=POS, sw=2.5))
    f.append(arrow(axR, yCM + 2, axR, yM, color=NEG, sw=2.5))
    f.append(text(axR - 12, (yCM + yP) / 2, "Vрізн", size=12, color=INK,
                  bold=True, anchor="end"))
    f.append(text(axR - 12, (yCM + yM) / 2 + 12, "(сигнал)", size=10, color=MUTED,
                  anchor="end"))
    f.append(text(axR, 56, "синфазна + різницева", size=12, bold=True))

    # формули внизу
    fb = fitbox(150, 372, 420, 34,
                "Vрізн = V₊ − V₋        Vсинф = (V₊ + V₋) / 2",
                size=13, fill="#f7f7f7")
    f.append(fb)
    return render(os.path.join(IMG, 'cm-dm.svg'), W, H, *f)


# ── Фігура 3 (для hist-вставки): родовід однієї думки ───────────────────────
def fig_lineage():
    """Часова смуга: та сама ідея 'неси різницю', доведена до різних рівнів
    напруг і швидкостей. Кожна віха — рік, назва, що несе, який розмах/синфаза."""
    W, H = 880, 470
    f = []
    f.append(text(W / 2, 30, "Одна думка «неси різницю» — через століття й рівні",
                  size=16, bold=True))

    # горизонтальна вісь часу
    axy = 150
    x0, x1 = 70, 810
    f.append(line(x0, axy, x1, axy, color=INK, sw=2.2))
    f.append(arrow(x1 - 4, axy, x1 + 18, axy, color=INK, sw=2.2))
    f.append(text(x1 + 8, axy - 12, "час", size=12, color=MUTED, anchor="start"))

    # віхи: (x, рік, заголовок, рядки-картка, колір крапки)
    posts = [
        (120, "1880-ті", "Транспозиція\nтелеграфу",
         "відкрита пара,\nперехрест проводів\n→ наводка спільна", MUTED),
        (290, "1881", "Вита пара\n(Белл, US 244 426)",
         "скручені проводи,\nметалічне коло\nзамість землі", POS),
        (470, "1975", "RS-422 / RS-485",
         "розмах ≈ ±2 В\nсинфаза\n−7…+7 / −7…+12 В", FIELD),
        (650, "1994", "LVDS\n(TIA/EIA-644)",
         "розмах ±175 мВ,\nсотні Мбіт/с,\nмала потужність", NEG),
    ]
    for (x, yr, head, body, col) in posts:
        f.append(circle(x, axy, 7, fill=col, stroke=col, sw=1.5))
        # рік над віссю
        f.append(text(x, axy - 18, yr, size=13, color=col, bold=True))
        # картка під віссю
        bx, bw, bh = textbox(x, axy + 95, body, size=10, min_w=150, stroke=col)
        f.append(line(x, axy + 7, x, axy + 95 - bh / 2, color=col, sw=1.4, dash="3 3"))
        f.append(bx)
        f.append(text(x, axy + 95 + bh / 2 + 18, head.replace("\n", " "),
                      size=11, color=INK, bold=True))

    # підсумковий рядок-стрічка внизу
    fb = fitbox(70, 410, 740, 40,
                "Скрізь те саме: інформація — у РІЗНИЦІ двох проводів; "
                "однакова на обох завада при відніманні гасне.",
                size=13, fill="#f0f7f1", stroke=FIELD)
    f.append(fb)
    return render(os.path.join(IMG, 'diff-lineage.svg'), W, H, *f)


# ── Фігура (вставка comp): блок-схема драйвер→лінія→приймач ──────────────────
def fig_link_blocks():
    W, H = 800, 360
    f = []
    f.append(text(W / 2, 30, "Збалансована лінія: драйвер · термінація · приймач-відніматель",
                  size=15, bold=True))

    midy = 185
    gap = 56  # піввідстань між двома проводами

    # --- драйвер ---
    drv, dw, dh = textbox(115, midy, "ДРАЙВЕР\n(жене дзеркало)", size=12, min_w=150,
                          stroke=INK)
    f.append(drv)
    dx_out = 115 + dw / 2  # права грань драйвера

    # --- приймач ---
    rcv, rw, rh = textbox(675, midy, "ПРИЙМАЧ\n(віднімає +/−)", size=12, min_w=160,
                          stroke=FIELD)
    rx_in = 675 - rw / 2  # ліва грань приймача
    f.append(rcv)

    # --- два проводи (символічно — пряма пара) ---
    yT = midy - gap   # прямий
    yB = midy + gap   # інверсний
    f.append(line(dx_out, yT, rx_in, yT, color=POS, sw=2.6))
    f.append(line(dx_out, yB, rx_in, yB, color=NEG, sw=2.6))
    f.append(plus(dx_out + 16, yT, r=9))
    f.append(minus(dx_out + 16, yB, r=9))
    f.append(text((dx_out + rx_in) / 2, yT - 12, "пряма (hot)", size=11, color=POS, bold=True))
    f.append(text((dx_out + rx_in) / 2, yB + 22, "інверсна (cold)", size=11, color=NEG, bold=True))
    f.append(text((dx_out + rx_in) / 2, midy + 4, "вита пара  ~100–120 Ω", size=11, color=MUTED))

    # --- термінальний резистор на дальньому кінці (між проводами біля приймача) ---
    tx = rx_in - 30
    f.append(line(tx, yT, tx, yB, color=INK, sw=1.4, dash="2 2"))
    # зиґзаґ-резистор по вертикалі
    zz = []
    n = 6
    for i in range(n + 1):
        yy = yT + (yB - yT) * i / n
        xx = tx + (8 if i % 2 else -8) if 0 < i < n else tx
        zz.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(zz), INK))
    rbox, _, rbh = textbox(tx, midy + 96, "термінатор\nRt ≈ Z₀", size=10, min_w=96, stroke=INK)
    f.append(line(tx, yB + 6, tx, midy + 96 - rbh / 2, color=MUTED, sw=1.2, dash="4 3"))
    f.append(rbox)

    # --- синфазне вікно під приймачем ---
    win, _, wbh = textbox(675, midy + 96, "синфазне вікно\n(напр. −7…+12 В)", size=10,
                          min_w=170, stroke=FIELD)
    f.append(line(675, midy + rh / 2 - 4, 675, midy + 96 - wbh / 2, color=FIELD, sw=1.2, dash="4 3"))
    f.append(win)

    # --- вихід приймача ---
    f.append(arrow(675 + rw / 2, midy, 675 + rw / 2 + 36, midy, color=FIELD, sw=2.2))
    f.append(text(675 + rw / 2 + 18, midy - 10, "Vрізн", size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG, 'link-blocks.svg'), W, H, *f)


# ── Фігура (вставка comp): balanced vs differential + XLR ────────────────────
def fig_balanced_xlr():
    W, H = 800, 440
    f = []
    f.append(text(W / 2, 30, "Що ловить заваду: баланс імпедансів, а не дзеркальний привод",
                  size=15, bold=True))

    yT, yB = 110, 175

    # ── ліва колонка: differential (дзеркальний привод) ──
    cxL = 205
    f.append(text(cxL, 68, "differential — про ПРИВОД", size=13, bold=True, color=POS))
    f.append(circle(125, yT, 17, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(125, yT + 5, "+V", size=12, color=POS, bold=True))
    f.append(circle(125, yB, 17, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(125, yB + 5, "−V", size=12, color=NEG, bold=True))
    f.append(line(142, yT, 300, yT, color=POS, sw=2.4))
    f.append(line(142, yB, 300, yB, color=NEG, sw=2.4))
    f.append(text(cxL, 212, "розмах подвоюється: 2V", size=11, color=INK, bold=True))

    # ── права колонка: balanced (рівні імпеданси) ──
    cxR = 590
    f.append(text(cxR, 68, "balanced — про ІМПЕДАНС", size=13, bold=True, color=FIELD))
    f.append(line(505, yT, 665, yT, color=INK, sw=2.4))
    f.append(line(505, yB, 665, yB, color=INK, sw=2.4))
    gyy = yB + 58
    f.append(text(485, yT + 5, "Z", size=12, color=FIELD, bold=True, anchor="end"))
    f.append(text(485, yB + 5, "Z", size=12, color=FIELD, bold=True, anchor="end"))
    f.append(text(cxR, 212, "рівний Z обох плечей до землі", size=11, color=FIELD, bold=True))
    f.append(line(470, gyy, 700, gyy, color=MUTED, sw=2, dash="5 4"))
    f.append(line(525, yT, 525, gyy, color=FIELD, sw=1.6))
    f.append(line(545, yB, 545, gyy, color=FIELD, sw=1.6))

    # роздільна вертикаль
    f.append(line(W / 2, 58, W / 2, 232, color="#dddddd", sw=1.2))

    # підсумковий рядок
    fb = fitbox(95, 250, 610, 36,
                "наводка гасне ⟺ плеча ЗБАЛАНСОВАНІ (рівний Z); дзеркальний привод лише додає розмах",
                size=12, fill="#eafaf1", stroke=FIELD)
    f.append(fb)

    # ── XLR-розпіновка внизу ──
    f.append(text(W / 2, 322, "XLR (студійний звук): 1 — екран · 2 — hot (+) · 3 — cold (−)",
                  size=13, bold=True))
    import math
    cx, cy, R = W / 2, 388, 34
    f.append(circle(cx, cy, R, fill="#f4f6f8", stroke=INK, sw=2))
    # кут, текст, колір, окремий радіус-винос підпису (top коротший — щоб не лізти в заголовок)
    pins = [(-90, "1 — екран", MUTED, 6), (150, "2 — hot", POS, 56), (30, "3 — cold", NEG, 56)]
    for ang, lab, col, lr in pins:
        px = cx + 0.5 * R * math.cos(math.radians(ang))
        py = cy + 0.5 * R * math.sin(math.radians(ang))
        f.append(circle(px, py, 7, fill="#ffffff", stroke=col, sw=2))
        lx = cx + lr * math.cos(math.radians(ang))
        ly = cy + (R + 20) * math.sin(math.radians(ang))
        f.append(text(lx, ly + 4, lab, size=11, color=col, bold=True))

    return render(os.path.join(IMG, 'balanced-xlr.svg'), W, H, *f)


if __name__ == '__main__':
    p1 = fig_single_vs_diff()
    p2 = fig_cm_dm()
    p3 = fig_lineage()
    p4 = fig_link_blocks()
    p5 = fig_balanced_xlr()
    print("wrote", p1)
    print("wrote", p2)
    print("wrote", p3)
    print("wrote", p4)
    print("wrote", p5)
