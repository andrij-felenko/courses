# -*- coding: utf-8 -*-
"""Фігури для ДЕТАЛЬНОЇ статті pwm-power-control-d («Керування потужністю: глибше»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/

Три нові фігури (базові фігури теми лишаються недоторканими):
  rms-vs-avg    — середнє проти діючого значення й потужність для ШІМ
  servo-loop    — внутрішня петля позиції серво
  mains-control — пакетне (в нулі) проти фазового керування мережею
  burst-thermostat — лічба нулів + вікно N півперіодів, k рівномірно розкиданих (для proj-термостата)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── rms-vs-avg: три криві U_avg=D, U_rms=√D, P=D на осях D∈[0,1] ──────────────
# Ідея: показати наочно, що для ШІМ середнє й діюче — РІЗНІ, а потужність (квадрат
# діючого) знову лінійна. Розбіжність avg↔rms максимальна посередині.
def fig_rms_vs_avg():
    W, H = 720, 430
    ox, oy = 90, 350            # початок осей (лівий-низ графіка)
    aw, ah = 500, 270           # ширина/висота поля графіка

    p = []
    # осі
    p.append(arrow(ox, oy, ox + aw + 24, oy, color=INK, sw=1.6))       # вісь D
    p.append(arrow(ox, oy, ox, oy - ah - 24, color=INK, sw=1.6))       # вісь величини
    p.append(text(ox + aw + 20, oy + 24, "шпаруватість D", size=13, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 14, oy - ah - 8, "частка від повного", size=12, color=INK, anchor="start"))

    # сітка 0, 0.5, 1 по обох осях
    for f in (0.0, 0.5, 1.0):
        x = ox + f * aw
        y = oy - f * ah
        p.append(line(x, oy, x, oy - ah, color="#e5e7eb", sw=1))
        p.append(line(ox, y, ox + aw, y, color="#e5e7eb", sw=1))
        p.append(text(x, oy + 20, ("%.1f" % f), size=11, color=MUTED))
        if f > 0:
            p.append(text(ox - 10, y + 4, ("%.1f" % f), size=11, color=MUTED, anchor="end"))

    def curve(fn, color, sw=2.6, dash=None):
        pts = []
        for i in range(0, 201):
            d = i / 200.0
            v = fn(d)
            pts.append("%.1f,%.1f" % (ox + d * aw, oy - v * ah))
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round"%s/>' % (" ".join(pts), color, sw, da))

    # P = D  (лінійна) — зелена
    p.append(curve(lambda d: d, FIELD, sw=2.8))
    # U_rms = √D  — червона
    p.append(curve(lambda d: math.sqrt(d), POS, sw=2.6))
    # U_avg = D  (та сама пряма, що P, але це НАПРУГА) — синя, пунктир, щоб не злилась
    p.append(curve(lambda d: d, NEG, sw=2.2, dash="7 5"))

    # маркер розбіжності при D=0.5
    xd = ox + 0.5 * aw
    y_avg = oy - 0.5 * ah
    y_rms = oy - math.sqrt(0.5) * ah
    p.append(line(xd, y_avg, xd, y_rms, color=MUTED, sw=1.4, dash="3 3"))
    p.append(circle(xd, y_rms, 4, fill=POS, stroke=POS, sw=1))
    p.append(circle(xd, y_avg, 4, fill=NEG, stroke=NEG, sw=1))
    # підпис маркера зсунуто ЛІВОРУЧ від точки (anchor="end"), щоб не збігтися з легендою b3 праворуч
    p.append(text(xd - 8, (y_avg + y_rms) / 2 + 4, "0.707 vs 0.500", size=11, color=MUTED, anchor="end"))

    # легенда (рамки-мітки під кривими)
    b1, w1, h1 = textbox(ox + 118, oy - ah + 26, "U_rms = √D  (діюче)", size=12, color=POS, stroke=POS, fill="#fdecea")
    b2, w2, h2 = textbox(ox + 300, oy - 0.30 * ah, "U_avg = D  (середнє, напруга)", size=12, color=NEG, stroke=NEG, fill="#eaf0fd")
    # зсунуто праворуч (ox+390 замість ox+360), щоб не налазити на підпис маркера "0.707 vs 0.500"
    b3, w3, h3 = textbox(ox + 390, oy - 0.62 * ah, "P = U_rms²/R = D  (потужність)", size=12, color=FIELD, stroke=FIELD, fill="#eafaf1")
    p += [b1, b2, b3]

    render(os.path.join(OUT, "rms-vs-avg.svg"), W, H, *p,
           title="ШІМ: середнє, діюче і потужність — три різні криві")

def fig_servo_loop():
    W, H = 760, 400
    yb = 150                    # рядок блоків
    bh = 62

    p = []

    # вхідний імпульс ШІМ (ліворуч)
    p.append(text(70, 60, "вхід ШІМ", size=12, color=INK, bold=True))
    p.append(text(70, 78, "ширина = бажаний кут", size=11, color=MUTED))
    # намалюємо маленький імпульс
    ix, iy = 40, 110
    p.append(line(ix, iy, ix + 20, iy, color=NEG, sw=2))
    p.append(line(ix + 20, iy, ix + 20, iy - 22, color=NEG, sw=2))
    p.append(line(ix + 20, iy - 22, ix + 44, iy - 22, color=NEG, sw=2))
    p.append(line(ix + 44, iy - 22, ix + 44, iy, color=NEG, sw=2))
    p.append(line(ix + 44, iy, ix + 74, iy, color=NEG, sw=2))

    # блок: компаратор ширини
    cx1 = 175
    b_cmp = fitbox(cx1, yb, 130, bh, "компаратор\nширини", size=13, bold=True, fill="#fff7e6", stroke="#b8860b")
    p.append(b_cmp)
    # блок: підсилювач
    cx2 = 355
    b_amp = fitbox(cx2, yb, 120, bh, "підсилювач\nпомилки", size=13, bold=True)
    p.append(b_amp)
    # блок: мотор + редуктор
    cx3 = 525
    b_mot = fitbox(cx3, yb, 120, bh, "мотор +\nредуктор", size=13, bold=True, fill="#eafaf1", stroke=FIELD)
    p.append(b_mot)
    # блок: вихідний вал
    cx4 = 685
    b_out = fitbox(cx4, yb, 60, bh, "ВАЛ", size=13, bold=True, fill="#eaf0fd", stroke=NEG)
    p.append(b_out)

    yc = yb + bh / 2
    # стрілки прямого шляху
    p.append(arrow(ix + 74, iy, cx1, yc, color=INK, sw=1.8))
    p.append(arrow(cx1 + 130, yc, cx2, yc, color=INK, sw=1.8))
    p.append(text((cx1 + 130 + cx2) / 2, yc - 8, "помилка", size=11, color=POS, bold=True))
    p.append(arrow(cx2 + 120, yc, cx3, yc, color=INK, sw=1.8))
    p.append(arrow(cx3 + 120, yc, cx4, yc, color=INK, sw=1.8))
    p.append(text(cx4 + 30, yc - bh / 2 - 8, "кут", size=11, color=NEG, bold=True))

    # блок: потенціометр (зворотний зв'язок), нижче
    yp = 300
    b_pot = fitbox(cx2 - 40, yp, 200, 56, "потенціометр на валу\n→ внутрішній імпульс", size=12, bold=True, fill="#f4f6f8")
    p.append(b_pot)

    # зворотний шлях: від вала вниз, ліворуч у потенціометр, з потенціометра — назад у компаратор
    p.append(line(cx4 + 30, yb + bh, cx4 + 30, yp + 28, color=MUTED, sw=1.8))
    p.append(arrow(cx4 + 30, yp + 28, cx2 + 160, yp + 28, color=MUTED, sw=1.8))
    # з потенціометра вгору-ліворуч у другий вхід компаратора
    p.append(line(cx2 - 40, yp + 28, cx1 + 65, yp + 28, color=MUTED, sw=1.8))
    p.append(arrow(cx1 + 65, yp + 28, cx1 + 65, yb + bh, color=MUTED, sw=1.8))
    # підпис відсунуто далі праворуч (cx1+100 замість cx1+72), щоб вертикальна стрілка
    # зворотного зв'язку (x=cx1+65) не перетинала початок напису біля (247,304)
    p.append(text(cx1 + 100, yp + 12, "поточний кут (ширина від потенціометра)", size=11, color=MUTED, anchor="start"))

    # підпис суті внизу
    b_note, wn, hn = textbox(W / 2, 370,
                             "збіг ширин → помилка = 0 → мотор стоїть → вал у заданому куті",
                             size=12, bold=True, fill="#eafaf1", stroke=FIELD)
    p.append(b_note)

    render(os.path.join(OUT, "servo-loop.svg"), W, H, *p,
           title="Серво зсередини: замкнена петля позиції")

def fig_mains_control():
    W, H = 760, 400
    amp = 70
    p = []

    def sine_axes( ox, oy, aw, label):
        seg = []
        seg.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.4))           # нуль
        seg.append(text(ox + aw / 2, oy + amp + 46, label, size=13, color=INK, bold=True))
        return seg

    # ── ЛІВОРУЧ: пакетне (burst-fire) ──
    oxL, oyL = 60, 150
    awL = 300
    periods = 4                # 4 півперіоди у вікні
    seg_w = awL / periods
    # маска увімкнення: 1,1,0,1 (3 з 4 → D=0.75)
    on = [1, 1, 0, 1]
    p += sine_axes(oxL, oyL, awL, "пакетне: цілі півперіоди, перемикання в НУЛІ")
    for k in range(periods):
        pts = []
        x0 = oxL + k * seg_w
        for i in range(0, 61):
            t = i / 60.0
            v = math.sin(t * math.pi)                # один півперіод (0..pi)
            # знак: чергуємо полярність півперіодів
            sign = 1 if k % 2 == 0 else -1
            y = oyL - sign * v * amp
            if on[k]:
                pts.append("%.1f,%.1f" % (x0 + t * seg_w, y))
        if on[k]:
            p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                     'stroke-linejoin="round"/>' % (" ".join(pts), POS))
        else:
            # вимкнений півперіод — сірий пунктир по нулю
            p.append(line(x0, oyL, x0 + seg_w, oyL, color=MUTED, sw=2.2, dash="4 4"))
        # позначка нуля-переходу
        p.append(circle(x0, oyL, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(circle(oxL + periods * seg_w, oyL, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    bL, wL, hL = textbox(oxL + awL / 2, oyL + amp + 74, "квант = півперіод (10 мс) · мінімум EMI · нагрівач",
                         size=11, color=INK, fill="#eafaf1", stroke=FIELD)
    p.append(bL)

    # ── ПРАВОРУЧ: фазове (phase-angle) ──
    oxR, oyR = 420, 150
    awR = 300
    p += sine_axes(oxR, oyR, awR, "фазове: частина півперіоду, увімкнення посеред")
    alpha = 0.45               # частка півперіоду ДО увімкнення (кут α)
    for k in range(periods):
        x0 = oxR + k * seg_w
        sign = 1 if k % 2 == 0 else -1
        # частина до alpha — вимкнено (по нулю), після — синусоїда до кінця
        p.append(line(x0, oyR, x0 + alpha * seg_w, oyR, color=MUTED, sw=2.2, dash="4 4"))
        pts = []
        for i in range(0, 61):
            t = alpha + (1 - alpha) * i / 60.0
            v = math.sin(t * math.pi)
            y = oyR - sign * v * amp
            pts.append("%.1f,%.1f" % (x0 + t * seg_w, y))
        # різкий фронт: вертикаль від нуля до першої точки
        x_fire = x0 + alpha * seg_w
        y_fire = oyR - sign * math.sin(alpha * math.pi) * amp
        p.append(line(x_fire, oyR, x_fire, y_fire, color=POS, sw=2.6))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), POS))
        # мітка кута α на першому півперіоді
        if k == 0:
            p.append(text(x_fire, oyR - amp - 10, "α", size=13, color=POS, bold=True, italic=True))
    bR, wR, hR = textbox(oxR + awR / 2, oyR + amp + 74, "тонше RMS · плавно для лампи · різкий фронт → EMI",
                         size=11, color=INK, fill="#fdecea", stroke=POS)
    p.append(bR)

    render(os.path.join(OUT, "mains-control.svg"), W, H, *p,
           title="Керування мережею: пакетне проти фазового")


# ── burst-thermostat: нулі мережі → лічильник → вікно з розкиданими квантами ──
# Ідея: показати ДВА масштаби. Зверху — синусоїда мережі з позначеними нулями
# (цоки лічильника). Знизу — «стрічка квантів»: вікно з N клітинок-півперіодів,
# де k увімкнених розкидані рівномірно (акумулятор Брезенхема), а не пачкою.
def fig_burst_thermostat():
    W, H = 720, 430
    p = []

    # ── Верх: синусоїда мережі з нулями як цоками ──
    oxT, oyT = 60, 120
    awT = 600
    amp = 46
    cycles = 3                      # 3 повні періоди у показі
    pts = []
    n = 360
    for i in range(0, n + 1):
        t = i / n
        y = oyT - math.sin(t * cycles * 2 * math.pi) * amp
        pts.append("%.1f,%.1f" % (oxT + t * awT, y))
    p.append(line(oxT, oyT, oxT + awT, oyT, color="#e5e7eb", sw=1))       # вісь нуля
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))
    p.append(text(oxT + awT / 2, oyT - amp - 22, "мережа 50 Гц", size=13, color=INK, bold=True))

    # нулі: кожен перехід через нуль = цок. Їх 2 на період → 2*cycles + 1.
    half = awT / (2 * cycles)
    for j in range(0, 2 * cycles + 1):
        x = oxT + j * half
        p.append(circle(x, oyT, 4, fill=FIELD, stroke=FIELD, sw=1))
        p.append(line(x, oyT + amp + 4, x, oyT + amp + 16, color=MUTED, sw=1.2, dash="2 2"))
    p.append(text(oxT + awT / 2, oyT + amp + 34,
                  "кожен нуль = цок (100/с) · квант = півперіод = 10 мс",
                  size=12, color=FIELD, bold=True))

    # ── Низ: стрічка квантів (вікно) з рівномірно розкиданими увімкненими ──
    oxB, oyB = 60, 300
    cells = 12                      # показове вікно N=12 клітинок
    cw = awT / cells
    ch = 46
    # k=5 із 12 (частка ≈ 0.42), розкидані АКУМУЛЯТОРОМ Брезенхема (як у коді)
    k_on = 5
    acc = 0
    on_mask = []
    for _ in range(cells):
        acc += k_on
        if acc >= cells:
            acc -= cells
            on_mask.append(1)
        else:
            on_mask.append(0)
    n_on = sum(on_mask)
    for c in range(cells):
        x = oxB + c * cw
        if on_mask[c]:
            p.append(rect(x + 2, oyB, cw - 4, ch, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=4))
            # маленький півперіод усередині увімкненої клітинки
            sp = []
            for i in range(0, 21):
                tt = i / 20.0
                yy = oyB + ch / 2 - math.sin(tt * math.pi) * (ch / 2 - 6)
                sp.append("%.1f,%.1f" % (x + 4 + tt * (cw - 8), yy))
            p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
                     'stroke-linejoin="round"/>' % (" ".join(sp), FIELD))
        else:
            p.append(rect(x + 2, oyB, cw - 4, ch, fill="#f4f6f8", stroke="#d1d5db", sw=1.4, rx=4))
            p.append(line(x + 4, oyB + ch / 2, x + cw - 4, oyB + ch / 2, color=MUTED, sw=1.6, dash="3 3"))

    b, wB, hB = textbox(oxB + awT / 2, oyB + ch + 40,
                        "вікно N = %d півперіодів · увімкнено k = %d → потужність = k/N ≈ %.0f%% · розкидані рівномірно"
                        % (cells, n_on, 100.0 * n_on / cells),
                        size=12, color=INK, fill="#eafaf1", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, "burst-thermostat.svg"), W, H, *p,
           title="Пакетне керування нагрівачем: цоки нулів і вікно квантів")


# ── hist-servo-frame: анатомія кадру серво (для вставки hist-servo-standard) ──
# Ідея: показати, ЗВІДКИ взялися числа. Кадр = низка коротких імпульсів каналів
# (по 1–2 мс) + довга пауза-роздільник; увесь кадр ≈ 20 мс. Один канал збільшено:
# 1.0 / 1.5 / 2.0 мс = край/центр/край. Меседж: 20 мс — «скільки каналів улізло»,
# 1–2 мс — «що надійно міряв тодішній лічильник», 1.5 — проста середина.
def fig_hist_servo_frame():
    W, H = 760, 440
    p = []

    # ── ВЕРХ: увесь кадр як низка каналів + пауза ──
    ox, oy = 60, 120           # база (нуль) верхньої доріжки
    aw = 640                   # ширина всього кадру (= 20 мс)
    pulse_h = 46
    ms = aw / 20.0             # пікселів на 1 мс (кадр 20 мс)

    p.append(text(W / 2, 56, "Кадр серво: низка каналів + пауза ≈ 20 мс", size=15, bold=True))
    # вісь-нуль
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))

    # чотири канали: старт кожного і ширина в мс (усі різні, у межах 1–2)
    chans = [(0.6, 1.0), (2.4, 1.5), (4.2, 2.0), (6.4, 1.2)]  # (старт_мс, ширина_мс)
    labels = ["к1", "к2", "к3", "к4"]
    last_end = 0.0
    for (st, wms), lb in zip(chans, labels):
        x0 = ox + st * ms
        x1 = ox + (st + wms) * ms
        # імпульс (прямокутник контуром)
        p.append(line(x0, oy, x0, oy - pulse_h, color=NEG, sw=2.4))
        p.append(line(x0, oy - pulse_h, x1, oy - pulse_h, color=NEG, sw=2.4))
        p.append(line(x1, oy - pulse_h, x1, oy, color=NEG, sw=2.4))
        p.append(text((x0 + x1) / 2, oy + 16, lb, size=11, color=MUTED))
        last_end = st + wms
    # низ-лінія уздовж каналів
    p.append(line(ox, oy, ox + last_end * ms, oy, color=NEG, sw=2.4))

    # пауза-роздільник (від кінця останнього каналу до кінця кадру)
    xg0 = ox + last_end * ms
    xg1 = ox + aw
    p.append(line(xg0, oy, xg1, oy, color=MUTED, sw=2.4, dash="5 4"))
    p.append(text((xg0 + xg1) / 2, oy - 14, "пауза-роздільник", size=11, color=MUTED))
    p.append(text((xg0 + xg1) / 2, oy + 16, "(де кадр скінчився)", size=10, color=MUTED))

    # розмір усього кадру (стрілка ↔ під доріжкою)
    ydim = oy + 40
    p.append(arrow(ox, ydim, ox + aw, ydim, color=INK, sw=1.4))
    p.append(arrow(ox + aw, ydim, ox, ydim, color=INK, sw=1.4))
    p.append(text(W / 2, ydim + 18, "увесь кадр ≈ 20 мс (50 Гц) — «скільки каналів улізло»",
                  size=12, color=INK, italic=True))

    # ── НИЗ: один канал збільшено — 1.0 / 1.5 / 2.0 мс ──
    bx, by = 130, 320          # база нижньої доріжки
    bw = 148                   # ширина 1 мс у збільшенні
    bph = 52
    p.append(text(W / 2, 262, "Один канал зблизька: ширина = кут", size=14, bold=True))

    specs = [(1.0, POS, "1.0 мс → 0°"), (1.5, INK, "1.5 мс → 90° (центр)"), (2.0, NEG, "2.0 мс → 180°")]
    sx = bx
    p.append(line(sx - 40, by, sx, by, color=INK, sw=1.8))          # підвід зліва
    for wms, col, _ in specs:
        x1 = sx + wms * bw
        ytop = by - bph
        p.append(line(sx, by, sx, ytop, color=col, sw=2.6))
        p.append(line(sx, ytop, x1, ytop, color=col, sw=2.6))
        p.append(line(x1, ytop, x1, by, color=col, sw=2.6))
    # спільна нульова лінія
    p.append(line(sx, by, sx + 2.0 * bw + 60, by, color=INK, sw=1.8))
    # шкала мс під доріжкою
    for mval in (1.0, 1.5, 2.0):
        xx = sx + mval * bw
        p.append(line(xx, by, xx, by + 8, color=MUTED, sw=1.2))
        p.append(text(xx, by + 22, ("%.1f мс" % mval), size=11, color=MUTED))

    # легенда праворуч
    ly = 302
    for wms, col, lab in specs:
        fillc = "#fdecea" if col == POS else ("#eaf0fd" if col == NEG else "#f4f6f8")
        b, w_, h_ = textbox(sx + 2.0 * bw + 150, ly, lab, size=12, color=col, stroke=col, fill=fillc)
        p.append(b)
        ly += 34

    # підсумковий меседж
    bnote, wn, hn = textbox(W / 2, 418,
                            "числа — відбиток заліза 1962-го: 1.5 мс = проста середина між 1 і 2",
                            size=12, bold=True, fill="#eafaf1", stroke=FIELD)
    p.append(bnote)

    render(os.path.join(OUT, "hist-servo-frame.svg"), W, H, *p)


# ── rms-shapes: три форми ШІМ і їхнє ⟨u²⟩ (вставка math-rms-harmonics) ────────
# Ідея: показати наочно, що рецепт ⟨u²⟩ один, а закон щоразу інший. Три панелі:
# прямокутник (√D), трапеція (поправка −τ/3), обрізана синусоїда (нелінійна RMS(α)).
def fig_rms_shapes():
    W, H = 780, 380
    p = []
    amp = 66
    panel_w = 210
    x0s = [50, 285, 540]
    ytop = 90                     # рівень «повної амплітуди» (лінія Vmax)
    ybase = ytop + amp            # нульова лінія форми

    def frame(ox, title):
        seg = []
        seg.append(line(ox, ybase, ox + panel_w, ybase, color=INK, sw=1.4))        # нуль
        seg.append(line(ox, ytop, ox + panel_w, ytop, color="#e5e7eb", sw=1, dash="4 4"))  # Vmax
        seg.append(text(ox - 6, ytop + 4, "Vₘₐₓ", size=10, color=MUTED, anchor="end"))
        seg.append(text(ox - 6, ybase + 4, "0", size=10, color=MUTED, anchor="end"))
        seg.append(text(ox + panel_w / 2, ytop - 16, title, size=13, color=INK, bold=True))
        return seg

    # ── Панель A: ідеальний прямокутник, D=0.5 ──
    oxA = x0s[0]
    p += frame(oxA, "прямокутник")
    D = 0.5
    xr0 = oxA + 0.12 * panel_w
    wpulse = D * panel_w * 0.76
    p.append(line(oxA, ybase, xr0, ybase, color=POS, sw=2.6))
    p.append(line(xr0, ybase, xr0, ytop, color=POS, sw=2.6))
    p.append(line(xr0, ytop, xr0 + wpulse, ytop, color=POS, sw=2.6))
    p.append(line(xr0 + wpulse, ytop, xr0 + wpulse, ybase, color=POS, sw=2.6))
    p.append(line(xr0 + wpulse, ybase, oxA + panel_w, ybase, color=POS, sw=2.6))
    bA, wA, hA = textbox(oxA + panel_w / 2, ybase + 62,
                         "⟨u²⟩ = D·Vₘₐₓ²\nU_rms = √D·Vₘₐₓ", size=12, color=INK,
                         fill="#fdecea", stroke=POS)
    p.append(bA)

    # ── Панель B: трапеція зі скінченними фронтами ──
    oxB = x0s[1]
    p += frame(oxB, "трапеція (фронти)")
    xt0 = oxB + 0.12 * panel_w
    te = 0.16 * panel_w           # ширина фронту (перебільшено для наочності)
    topw = 0.42 * panel_w
    p.append(line(oxB, ybase, xt0, ybase, color=NEG, sw=2.6))
    p.append(line(xt0, ybase, xt0 + te, ytop, color=NEG, sw=2.6))                 # наростання
    p.append(line(xt0 + te, ytop, xt0 + te + topw, ytop, color=NEG, sw=2.6))       # верх
    p.append(line(xt0 + te + topw, ytop, xt0 + 2 * te + topw, ybase, color=NEG, sw=2.6))  # спад
    p.append(line(xt0 + 2 * te + topw, ybase, oxB + panel_w, ybase, color=NEG, sw=2.6))
    p.append(line(xt0, ybase + 8, xt0 + te, ybase + 8, color=MUTED, sw=1.2))
    p.append(text(xt0 + te / 2, ybase + 20, "tₑ", size=10, color=MUTED, italic=True))
    bB, wB, hB = textbox(oxB + panel_w / 2, ybase + 62,
                         "⟨u²⟩ = (D − τₑ/3)·Vₘₐₓ²\nфронт дає лише ⅓ частки", size=12,
                         color=INK, fill="#eaf0fd", stroke=NEG)
    p.append(bB)

    # ── Панель C: частка потужності vs кут відсічки α ──
    oxC = x0s[2]
    p.append(text(oxC + panel_w / 2, ytop - 16, "обрізана синусоїда: P(α)/P_full", size=12, color=INK, bold=True))
    gx, gy = oxC + 20, ybase          # початок осей графіка (низ-ліво)
    gw, gh = panel_w - 30, amp
    p.append(arrow(gx, gy, gx + gw + 12, gy, color=INK, sw=1.4))     # вісь α
    p.append(arrow(gx, gy, gx, gy - gh - 12, color=INK, sw=1.4))     # вісь частки
    p.append(text(gx + gw + 8, gy + 16, "α", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(gx - 4, gy - gh - 4, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(gx - 4, gy + 4, "0", size=10, color=MUTED, anchor="end"))
    pts = []
    for i in range(0, 121):
        a = math.pi * i / 120.0
        f = 1 - a / math.pi + math.sin(2 * a) / (2 * math.pi)
        x = gx + (a / math.pi) * gw
        y = gy - f * gh
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts), FIELD))
    xm = gx + 0.5 * gw
    ym = gy - 0.5 * gh
    p.append(line(xm, gy, xm, ym, color=MUTED, sw=1.2, dash="3 3"))
    p.append(line(gx, ym, xm, ym, color=MUTED, sw=1.2, dash="3 3"))
    p.append(circle(xm, ym, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(xm + 6, ym - 6, "90°→½", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(gx + 0.5 * gw, gy + 16, "90°", size=10, color=MUTED))
    p.append(text(gx + gw, gy + 16, "180°", size=10, color=MUTED, anchor="end"))
    bC, wC, hC = textbox(oxC + panel_w / 2, ybase + 62,
                         "сильно нелінійна:\nформа диктує закон", size=12, color=INK,
                         fill="#eafaf1", stroke=FIELD)
    p.append(bC)

    render(os.path.join(OUT, "rms-shapes.svg"), W, H, *p,
           title="Один рецепт ⟨u²⟩ — три форми, три закони")


# ── spwm-spectrum: спектр SPWM — чистий баз, острови сміття на f_pwm і кратних ─
# Ідея: показати «острівну» будову. Ліворуч єдина корисна лінія на f0; праворуч
# групи бічних смуг навколо f_pwm (парні зсуви) і 2*f_pwm (непарні, несуча гасне).
def fig_spwm_spectrum():
    W, H = 800, 380
    p = []
    ax, ay = 60, 250              # початок осей
    aw = 690
    hmax = 150                    # висота під найвищу лінію

    p.append(arrow(ax, ay, ax + aw + 12, ay, color=INK, sw=1.6))        # вісь частоти
    p.append(arrow(ax, ay, ax, ay - hmax - 20, color=INK, sw=1.6))       # вісь амплітуди
    p.append(text(ax + aw + 8, ay + 20, "частота", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(ax - 8, ay - hmax - 8, "амплітуда", size=11, color=INK, anchor="start"))

    def stem(xf, h, color, sw=2.6):
        x = ax + xf * aw
        return line(x, ay, x, ay - h, color=color, sw=sw)

    f0 = 0.06
    fpwm = 0.5
    f2 = 0.88
    d = 0.028                     # крок бічної смуги (візуальний f0-зсув біля острова)

    # ── БАЗ: єдина корисна лінія на f0 ──
    p.append(stem(f0, hmax, POS, sw=3.2))
    p.append(text(ax + f0 * aw, ay + 18, "f₀", size=12, color=POS, bold=True))
    p.append(text(ax + f0 * aw + 6, ay - hmax + 2, "M·Vₘₐₓ", size=11, color=POS, anchor="start"))
    bB, wB, hB = textbox(ax + 0.25 * aw, ay - hmax + 24, "баз чистий:\nнизьких гармонік немає",
                         size=12, color=FIELD, fill="#eafaf1", stroke=FIELD)
    p.append(bB)

    # ── ОСТРІВ навколо f_pwm (несуча + парні зсуви ±2,±4) ──
    p.append(stem(fpwm, 0.62 * hmax, INK, sw=2.8))                       # несуча
    p.append(text(ax + fpwm * aw, ay + 18, "f_pwm", size=12, color=INK, bold=True))
    for k, h in [(-2, 0.40), (2, 0.40), (-4, 0.20), (4, 0.20)]:
        p.append(stem(fpwm + k * d, h * hmax, MUTED, sw=2.4))
    p.append(text(ax + fpwm * aw, ay - 0.62 * hmax - 8, "несуча", size=10, color=MUTED))
    p.append(text(ax + (fpwm + 2 * d) * aw + 4, ay - 0.40 * hmax - 6, "±2f₀", size=10, color=MUTED, anchor="start"))
    p.append(text(ax + (fpwm - 4 * d) * aw - 4, ay - 0.20 * hmax - 6, "±4f₀", size=10, color=MUTED, anchor="end"))

    # ── ОСТРІВ навколо 2*f_pwm (несуча гасне, непарні зсуви ±1,±3) ──
    p.append(text(ax + f2 * aw, ay + 18, "2·f_pwm", size=12, color=INK, bold=True))
    p.append(line(ax + f2 * aw, ay, ax + f2 * aw, ay - 0.06 * hmax, color=MUTED, sw=2.0, dash="3 3"))
    p.append(text(ax + f2 * aw, ay - 0.06 * hmax - 6, "≈0", size=9, color=MUTED))
    for k, h in [(-1, 0.34), (1, 0.34), (-3, 0.18), (3, 0.18)]:
        p.append(stem(f2 + k * d, h * hmax, MUTED, sw=2.4))
    p.append(text(ax + (f2 + d) * aw + 4, ay - 0.34 * hmax - 6, "±f₀", size=10, color=MUTED, anchor="start"))

    bI, wI, hI = textbox(ax + 0.69 * aw, ay - hmax + 14, "острови сміття: несуча ± кратні f₀",
                         size=12, color=INK, fill="#f4f6f8", stroke=MUTED)
    p.append(bI)
    bF, wF, hF = textbox(ax + 0.69 * aw, ay + 52, "фільтр-навантаження давить праву частину →",
                         size=11, color=NEG, fill="#eaf0fd", stroke=NEG)
    p.append(bF)

    render(os.path.join(OUT, "spwm-spectrum.svg"), W, H, *p,
           title="Спектр SPWM: чистий баз, острови сміття на f_pwm і кратних")


if __name__ == "__main__":
    fig_rms_vs_avg()
    fig_servo_loop()
    fig_mains_control()
    fig_burst_thermostat()
    fig_hist_servo_frame()
    fig_rms_shapes()
    fig_spwm_spectrum()
    print("OK: rms-vs-avg, servo-loop, mains-control, burst-thermostat, hist-servo-frame, rms-shapes, spwm-spectrum ->", OUT)
