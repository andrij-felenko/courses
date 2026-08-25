# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SYS = "#27ae60"      # систематичні дані — зелене
SYSFILL = "#eafaf0"
PAR = "#2457d6"      # контроль (parity) — синє
PARFILL = "#eef4ff"
HOT = "#c0392b"      # гарячий біт / слабке місце — червоне
HOTFILL = "#fdecea"
ILV = "#c77d0a"      # перемішувач — тепле виділення
ILVFILL = "#fdf3e3"


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ── encoder: паралельна конкатенація двох згорткових кодерів ──────────────────

def fig_encoder():
    W, H = 940, 470
    p = []

    ymid = 232
    ytop = 104
    ybot = 360

    # вхід
    p.append(text(120, 218, "інформаційні біти", size=12, color=INK, bold=True))
    p.append(arrow(58, ymid, 176, ymid, sw=2.2))
    split = 182
    p.append(circle(split, ymid, 4.5, fill=INK, stroke=INK, sw=1.0))

    # три відгалуження від точки розбиття
    p.append(line(split, ymid, split, ytop, color=SYS, sw=2.2))       # угору — систематичні
    p.append(line(split, ymid, split, ybot, color=INK, sw=2.0))       # униз — до перемішувача
    p.append(arrow(split, ymid, 344, ymid, sw=2.0))                   # прямо — у кодер 1

    # систематична дорога (верх)
    p.append(arrow(split, ytop, 726, ytop, color=SYS, sw=2.2))
    p.append(text(452, ytop - 12, "систематичні дані — у канал без змін", size=11.5,
                  color=SYS, bold=True))

    # кодер 1
    p.append(rect(346, ymid - 26, 176, 52, fill=PARFILL, stroke=PAR, sw=2.2, rx=7))
    p.append(mtext(434, ymid - 4, ["згортковий", "кодер 1"], size=12.5, color=PAR, bold=True))
    p.append(arrow(522, ymid, 726, ymid, color=PAR, sw=2.2))
    p.append(text(624, ymid - 12, "контроль 1", size=11.5, color=PAR, bold=True))

    # униз до перемішувача
    p.append(arrow(split, ybot, 300, ybot, sw=2.0))
    # перемішувач
    p.append(rect(302, ybot - 24, 150, 48, fill=ILVFILL, stroke=ILV, sw=2.4, rx=7))
    p.append(text(377, ybot + 5, "перемішувач Π", size=12.5, color=ILV, bold=True))
    p.append(arrow(452, ybot, 500, ybot, sw=2.0))
    # кодер 2
    p.append(rect(502, ybot - 26, 176, 52, fill=PARFILL, stroke=PAR, sw=2.2, rx=7))
    p.append(mtext(590, ybot - 4, ["згортковий", "кодер 2"], size=12.5, color=PAR, bold=True))
    p.append(arrow(678, ybot, 726, ybot, color=PAR, sw=2.2))
    p.append(text(624, ybot - 34, "контроль 2", size=11.5, color=PAR, bold=True))
    p.append(text(590, ybot + 40, "бачить ті самі біти — але переставленими", size=11,
                  color=ILV, italic=True))

    # мультиплексор
    mx0 = 728
    p.append(rect(mx0, ytop - 20, 54, ybot - ytop + 40, fill="#f4f6f8", stroke=INK, sw=2.0, rx=8))
    p.append(mtext(mx0 + 27, (ytop + ybot) / 2 - 6, ["М", "У", "К", "С"], size=13, color=INK, bold=True))

    # вихід у канал
    p.append(arrow(mx0 + 54, ymid, 872, ymid, sw=2.4))
    p.append(mtext(838, ymid - 20, ["у канал"], size=12, color=INK, bold=True))
    p.append(text(838, H - 40, "1 біт даних", size=11, color=MUTED))
    p.append(text(838, H - 24, "+ 2 контролю", size=11, color=MUTED))

    box, bw, bh = textbox(W / 2, H - 42,
                          "паралельна конкатенація: обидва кодери йдуть прямо на дані,\n"
                          "а не один поверх одного, як у послідовному каскаді.  Швидкість 1/3.",
                          size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "encoder.svg"), W, H, *p,
           title="Турбокодувальник: два кодери на одне повідомлення, розділені перемішувачем")


# ── interleaver-protect: слабке місце одного кодера — сильне місце іншого ──────

def fig_interleaver_protect():
    W, H = 960, 540
    p = []

    cw = 34

    def strip(x0, y, bits, hot, on_color, off_color, on_fill, off_fill):
        out = []
        for k, b in enumerate(bits):
            ishot = k in hot
            if ishot:
                fill, strk = HOTFILL, HOT
            elif b:
                fill, strk = on_fill, on_color
            else:
                fill, strk = off_fill, off_color
            out.append(rect(x0 + k * cw, y, cw, cw, fill=fill, stroke=strk,
                            sw=2.2 if (ishot or b) else 1.2, rx=4))
            out.append(text(x0 + k * cw + cw / 2, y + cw / 2 + 5, str(b), size=14,
                            color=strk if (ishot or b) else "#b8bec6", bold=(ishot or b)))
        return out

    inp = [0, 0, 1, 0, 0, 0, 0, 1]          # низьковаговий вхід: дві одиниці
    inp_perm = [0, 1, 0, 0, 0, 0, 1, 0]     # той самий, перетасований
    par1 = [0, 0, 0, 1, 0, 0]               # кволий контроль
    par2 = [1, 1, 0, 1, 1, 0, 1]            # повновагий контроль

    lx = 108
    rx = 566
    y_in = 122
    y_enc = 232
    y_par = 344

    # заголовки колонок
    p.append(text(lx + 4 * cw, 78, "перший кодер: вхід у прямому порядку", size=13,
                  color=INK, bold=True))
    p.append(text(rx + 4 * cw - 12, 78, "другий кодер: вхід перетасовано", size=13,
                  color=INK, bold=True))

    # вхідні смуги
    p.extend(strip(lx, y_in, inp, {2, 7}, PAR, "#c7ccd3", PARFILL, BG))
    p.extend(strip(rx, y_in, inp_perm, {1, 6}, PAR, "#c7ccd3", PARFILL, BG))

    # перемішувач між входами
    p.append(arrow(lx + 8 * cw + 16, y_in + cw / 2, rx - 16, y_in + cw / 2, color=ILV, sw=2.8))
    p.append(mtext((lx + 8 * cw + rx) / 2, y_in + cw / 2 - 20, ["Π"], size=16, color=ILV, bold=True))
    p.append(text((lx + 8 * cw + rx) / 2, y_in + cw / 2 + 28, "тасує", size=10.5, color=ILV, italic=True))

    # стрілки вниз до кодерів
    p.append(arrow(lx + 4 * cw, y_in + cw + 6, lx + 4 * cw, y_enc - 4, sw=1.8))
    p.append(arrow(rx + 4 * cw, y_in + cw + 6, rx + 4 * cw, y_enc - 4, sw=1.8))

    # кодери
    p.append(rect(lx + 4 * cw - 100, y_enc, 200, 46, fill=PARFILL, stroke=PAR, sw=2.2, rx=7))
    p.append(text(lx + 4 * cw, y_enc + 29, "згортковий кодер 1", size=12.5, color=PAR, bold=True))
    p.append(rect(rx + 4 * cw - 100, y_enc, 200, 46, fill=PARFILL, stroke=PAR, sw=2.2, rx=7))
    p.append(text(rx + 4 * cw, y_enc + 29, "згортковий кодер 2", size=12.5, color=PAR, bold=True))

    p.append(arrow(lx + 4 * cw, y_enc + 46 + 4, lx + 4 * cw, y_par - 4, sw=1.8))
    p.append(arrow(rx + 4 * cw, y_enc + 46 + 4, rx + 4 * cw, y_par - 4, sw=1.8))

    # контрольні смуги (центруємо під кодером)
    lpx = lx + 4 * cw - len(par1) * cw / 2
    rpx = rx + 4 * cw - len(par2) * cw / 2
    p.extend(strip(lpx, y_par, par1, set(), "#8a9099", "#c7ccd3", "#eef0f2", BG))
    p.extend(strip(rpx, y_par, par2, set(), SYS, "#c7ccd3", SYSFILL, BG))

    p.append(text(lx + 4 * cw, y_par + cw + 22, "контроль 1: мала вага → слабко", size=12,
                  color="#8a9099", bold=True))
    p.append(text(rx + 4 * cw, y_par + cw + 22, "контроль 2: повна вага → сильно", size=12,
                  color=SYS, bold=True))

    box, bw, bh = textbox(W / 2, H - 46,
                          "щоб усе турбослово вийшло слабким, візерунок мусив би бути «поганим» для ОБОХ порядків одразу —\n"
                          "а перемішувач робить такий подвійний збіг майже неможливим",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "interleaver-protect.svg"), W, H, *p,
           title="Слабке місце одного кодера перемішувач робить сильним місцем іншого")


# ── turbo-loop: ітеративний декодер зі зворотним зв'язком ─────────────────────

def fig_turbo_loop():
    W, H = 920, 430
    p = []

    d1 = (252, 182)
    d2 = (668, 182)
    bw2, bh2 = 92, 52     # напівширина/напіввисота декодерів

    # вхід із каналу — ліворуч у DEC1
    p.append(mtext(126, 150, ["з каналу:", "дані + контроль 1"], size=10.5, color=INK, bold=True))
    p.append(arrow(70, d1[1], d1[0] - bw2 - 4, d1[1], sw=2.2))
    # вхід у DEC2 — праворуч
    p.append(mtext(802, 150, ["контроль 2", "(дані — через Π)"], size=10.5, color=INK, bold=True))
    p.append(arrow(850, d2[1], d2[0] + bw2 + 4, d2[1], sw=2.2))

    # верхня пряма: DEC1 → Π → DEC2
    yf = 158
    p.append(arrow(d1[0] + bw2, yf, 412, yf, color=SYS, sw=2.4))
    p.append(rect(414, yf - 18, 92, 36, fill=ILVFILL, stroke=ILV, sw=2.2, rx=7))
    p.append(text(460, yf + 5, "Π", size=15, color=ILV, bold=True))
    p.append(arrow(506, yf, d2[0] - bw2, yf, color=SYS, sw=2.4))
    p.append(text(460, yf - 26, "нове від DEC1 →", size=11, color=SYS, bold=True))

    # нижня зворотна: DEC2 → Π⁻¹ → DEC1 (П-подібна петля під блоками)
    yr = 300
    p.append(line(d2[0], d2[1] + bh2, d2[0], yr, color=PAR, sw=2.4))
    p.append(line(d2[0], yr, 506, yr, color=PAR, sw=2.4))
    p.append(rect(414, yr - 18, 92, 36, fill=ILVFILL, stroke=ILV, sw=2.2, rx=7))
    p.append(text(460, yr + 5, "Π⁻¹", size=14, color=ILV, bold=True))
    p.append(line(414, yr, d1[0], yr, color=PAR, sw=2.4))
    p.append(arrow(d1[0], yr, d1[0], d1[1] + bh2, color=PAR, sw=2.4))
    p.append(text(460, yr + 30, "← нове від DEC2 (розтасовано назад Π⁻¹)", size=11, color=PAR, bold=True))

    # декодери
    for (cx, cy), lab, n in ((d1, "контроль 1", "1"), (d2, "контроль 2", "2")):
        p.append(rect(cx - bw2, cy - bh2, 2 * bw2, 2 * bh2, fill="#f4f6f8", stroke=INK, sw=2.4, rx=9))
        p.append(mtext(cx, cy - 8, ["м'який декодер " + n, "(" + lab + ")"], size=12.5, color=INK, bold=True))

    # символ турбо в центрі петлі
    p.append(text((d1[0] + d2[0]) / 2, 244, "↻", size=30, color=HOT, bold=True))

    # вихід — тверде рішення (тап із DEC1 угору)
    p.append(arrow(d1[0], d1[1] - bh2, d1[0], 74, sw=2.2))
    p.append(text(d1[0], 62, "тверде рішення після ~15 обертів", size=11.5, color=INK, bold=True))

    box, bw, bh = textbox(W / 2, H - 34,
                          "зворотний зв'язок: вихід декодера живить його ж вхід — «вихлоп назад у турбіну».\n"
                          "щообертом кожен віддає лише СВОЮ нову звістку, а не відлунює почуте — інакше вийшов би виск самозбудження",
                          size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "turbo-loop.svg"), W, H, *p,
           title="Турбопринцип: два м'які декодери уточнюють одне одного по колу")


# ── waterfall-floor: крутий водоспад біля межі Шеннона й підлога помилок ──────

def fig_waterfall_floor():
    W, H = 760, 480
    p = []

    px0, px1 = 100, 668
    py0, py1 = 74, 360
    snr_max = 8.0

    def X(s):
        return px0 + (s / snr_max) * (px1 - px0)

    def Y(e):                       # e — показник степеня 10 (−1 … −7)
        return py0 + ((-1 - e) / 6.0) * (py1 - py0)

    # горизонтальні декади
    for k in range(1, 8):
        y = Y(-k)
        p.append(line(px0, y, px1, y, color="#e6e9ee", sw=1.0))
        p.append(text(px0 - 10, y + 4, "10⁻%d" % k, size=11, color=MUTED, anchor="end"))
    # осі
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    for s in range(0, 9, 1):
        p.append(line(X(s), py1, X(s), py1 + 5, color=INK, sw=1.2))
        p.append(text(X(s), py1 + 20, str(s), size=11, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 40, "відношення сигнал/шум  Eb/N0 , дБ", size=12, color=INK))
    p.append(text(px0 - 66, (py0 + py1) / 2, "BER", size=12, color=INK))

    # межа Шеннона (rate 1/2 ≈ 0.2 дБ)
    xs = X(0.2)
    p.append(line(xs, py0 - 4, xs, py1, color=FIELD, sw=2.0, dash="6 5"))
    p.append(text(xs + 4, py0 - 12, "межа Шеннона", size=11, color=FIELD, bold=True, anchor="start"))

    # криві
    turbo = [(0.55, -1), (0.75, -2.4), (0.95, -4.3), (1.1, -5.7),
             (1.5, -6.15), (2.4, -6.35), (4.0, -6.45), (6.0, -6.5)]     # водоспад → підлога
    classic = [(2.6, -1), (4.2, -2.4), (5.8, -4.2), (7.0, -5.4)]
    unc = [(4.3, -1), (6.2, -1.7), (8.0, -2.5)]
    p.append(polyline([(X(s), Y(e)) for s, e in unc], color=MUTED, sw=2.4))
    p.append(polyline([(X(s), Y(e)) for s, e in classic], color=PAR, sw=2.6))
    p.append(polyline([(X(s), Y(e)) for s, e in turbo], color=HOT, sw=3.2))

    # ≈ пів дБ між межею і водоспадом
    p.append(line(xs, Y(-3.4), X(0.9), Y(-3.4), color=INK, sw=1.3, dash="3 3"))
    p.append(text((xs + X(0.9)) / 2, Y(-3.4) - 8, "≈ пів дБ", size=10.5, color=INK, italic=True))

    # підпис «водоспад» — праворуч від крутого спаду, у чистій зоні
    p.append(text(X(1.75), Y(-3.0), "водоспад", size=12, color=HOT, bold=True, anchor="start"))
    p.append(line(X(1.72), Y(-3.15), X(1.15), Y(-4.6), color=HOT, sw=1.1))

    # підпис «підлога помилок» — над пологим хвостом
    p.append(text(X(3.6), Y(-5.35), "підлога помилок", size=12, color=HOT, bold=True, anchor="middle"))
    p.append(line(X(3.6), Y(-5.5), X(3.4), Y(-6.28), color=HOT, sw=1.1))

    # легенда рядком під віссю
    ly = py1 + 62
    items = [("турбокод", HOT), ("класичний код", PAR), ("без коду", MUTED)]
    lx = px0 + 16
    for label, col in items:
        p.append(line(lx, ly, lx + 26, ly, color=col, sw=3.0))
        p.append(text(lx + 32, ly + 4, label, size=11.5, color=INK, anchor="start"))
        lx += 32 + text_width(label, 11.5) + 40

    render(os.path.join(OUT, "waterfall-floor.svg"), W, H, *p,
           title="Крива турбокоду: водоспад упритул до Шеннона — і підлога під ним")


# ── timeline: як народилися турбокоди (для hist-turbo-birth) ──────────────────

def fig_timeline():
    W, H = 1060, 450
    p = []

    px0, px1 = 150, 910
    spine = 220
    n = 6
    xs = [px0 + i * (px1 - px0) / (n - 1) for i in range(n)]

    # шкала часу — лінія зі стрілкою вправо
    p.append(line(px0 - 44, spine, px1 + 44, spine, color=INK, sw=2.0))
    p.append(arrow(px1 + 40, spine, px1 + 66, spine, sw=2.0))
    p.append(text(px1 + 62, spine - 12, "час", size=11.5, color=MUTED, anchor="middle"))

    # (рік, колір, зверху?, підпис)
    miles = [
        ("1948", FIELD, True,
         ["Шеннон: межа є —", "а коди сорок років", "за 3.5 дБ від неї"]),
        ("1989", NEG, False,
         ["SOVA Гаґенауера:", "м'який декодер —", "«підсилювач С/Ш»"]),
        ("1991", HOT, True,
         ["Брест: симуляція", "дає ≈ 0.5 дБ — Берру", "не вірить програмі"]),
        ("1993", HOT, False,
         ["Женева, ICC:", "зала певна — це", "«помилка на 3 дБ»"]),
        ("1994", FIELD, True,
         ["JPL відтворює", "результат —", "скепсис розвіяно"]),
        ("1998 →", MUTED, False,
         ["3G, космос,", "нагороди трьом", "(Гемінг, Марконі)"]),
    ]

    for x, (year, col, above, lines) in zip(xs, miles):
        cy = 118 if above else 322
        # з'єднувач від вузла до рамки (малюємо ПЕРШИМ — рамка його перекриє)
        if above:
            p.append(line(x, spine - 9, x, cy + 34, color=col, sw=1.4))
        else:
            p.append(line(x, spine + 9, x, cy - 34, color=col, sw=1.4))
        # рамка-підпис (сама підганяється під найдовший рядок)
        box, _, _ = textbox(x, cy, "\n".join(lines), size=12, pad=10,
                            fill="#f7f8fa", stroke=col, sw=1.8, color=INK)
        p.append(box)
        # вузол на шкалі
        p.append(circle(x, spine, 9, fill=col, stroke=BG, sw=2.4))
        # рік — з вільного боку вузла, біля шкали
        yy = spine + 30 if above else spine - 20
        p.append(text(x, yy, year, size=14, color=col, bold=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Шлях турбокодів: від межі Шеннона до женевської зневіри й тріумфу")


# ── iter-waterfall: РЕАЛЬНІ дані прогону — BER падає з кожним обертом петлі ────

def fig_iter_waterfall():
    import math
    W, H = 780, 470
    p = []

    px0, px1 = 116, 684
    py0, py1 = 78, 356
    e_top, e_bot = -0.7, -4.2          # показник степеня 10 угорі / унизу

    def X(i):                           # i — номер ітерації 1..10
        return px0 + (i - 1) / 9.0 * (px1 - px0)

    def Y(b):                           # b — BER; на осі — log10
        e = math.log10(b)
        return py0 + (e_top - e) / (e_top - e_bot) * (py1 - py0)

    # реальні дані прогону: N=1024, log-MAP, 80 кадрів (той самий код, що в статті)
    d10 = [6.08e-2, 1.79e-2, 5.43e-3, 1.64e-3, 8.91e-4,
           5.25e-4, 3.54e-4, 4.03e-4, 3.17e-4, 2.44e-4]
    d05 = [9.25e-2, 4.97e-2, 3.04e-2, 2.11e-2, 1.61e-2,
           1.33e-2, 1.13e-2, 9.96e-3, 9.19e-3, 8.80e-3]

    # декади
    for k in range(1, 5):
        y = Y(10 ** (-k))
        p.append(line(px0, y, px1, y, color="#e6e9ee", sw=1.0))
        p.append(text(px0 - 12, y + 4, "10⁻%d" % k, size=11, color=MUTED, anchor="end"))
    # осі
    p.append(line(px0, py0 - 6, px0, py1, color=INK, sw=1.6))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    for i in range(1, 11):
        p.append(line(X(i), py1, X(i), py1 + 5, color=INK, sw=1.2))
        p.append(text(X(i), py1 + 21, str(i), size=11, color=MUTED))
    p.append(text((px0 + px1) / 2, py1 + 44, "номер ітерації (оберт петлі декодера)", size=12.5, color=INK))
    p.append(text(px0 - 74, (py0 + py1) / 2, "BER", size=12.5, color=INK))

    # криві з маркерами
    def curve(data, col, sw):
        pts = [(X(i + 1), Y(b)) for i, b in enumerate(data)]
        p.append(polyline(pts, color=col, sw=sw))
        for x, y in pts:
            p.append(circle(x, y, 3.3, fill=BG, stroke=col, sw=2.0))

    curve(d05, PAR, 2.6)
    curve(d10, HOT, 3.2)

    # підпис d10 — у порожній правій зоні, лінія-поводир від-під тексту до коліна
    p.append(text(X(6.5), Y(1.15e-2), "1.0 дБ: за 4 оберти — на два порядки нижче",
                  size=11.5, color=HOT, bold=True, anchor="middle"))
    p.append(line(X(6.5), Y(8.0e-3), X(4.0), Y(1.64e-3), color=HOT, sw=1.1))
    p.append(text(X(8.6), Y(1.6e-3), "далі виположується —", size=10.5, color=HOT, italic=True, anchor="middle"))
    p.append(text(X(8.6), Y(1.15e-3), "близько підлоги", size=10.5, color=HOT, italic=True, anchor="middle"))
    p.append(line(X(8.6), Y(8.5e-4), X(8.7), Y(4.5e-4), color=HOT, sw=1.0))

    # підпис d05 — угорі, біля своєї кривої
    p.append(text(X(6.3), Y(7.0e-2), "0.5 дБ (біля порога): повзе, але теж униз",
                  size=11.5, color=PAR, bold=True, anchor="middle"))
    p.append(line(X(6.3), Y(5.2e-2), X(5.0), Y(1.61e-2), color=PAR, sw=1.1))

    # легенда рядком під віссю
    ly = py1 + 68
    items = [("Eb/N0 = 1.0 дБ", HOT), ("Eb/N0 = 0.5 дБ", PAR)]
    lx = px0 + 44
    for label, col in items:
        p.append(line(lx, ly, lx + 26, ly, color=col, sw=3.0))
        p.append(circle(lx + 13, ly, 3.3, fill=BG, stroke=col, sw=2.0))
        p.append(text(lx + 34, ly + 4, label, size=11.5, color=INK, anchor="start"))
        lx += 34 + text_width(label, 11.5) + 56

    render(os.path.join(OUT, "iter-waterfall.svg"), W, H, *p,
           title="Кожен оберт петлі знижує BER: реальний прогін турбодекодера")


# ── bcjr-trellis: прямий α, зворотний β, гілкова γ на решітці ─────────────────

def fig_bcjr_trellis():
    W, H = 960, 560
    p = []

    cols = [150, 320, 490, 660, 830]     # часові зрізи
    rows = [180, 240, 300, 360]          # стани
    tlab = ["…", "k−1", "k", "k+1", "…"]

    # зв'язність метелика 4-станового коду: 0→{0,2}, 1→{0,2}, 2→{1,3}, 3→{1,3}
    nxt = {0: (0, 2), 1: (0, 2), 2: (1, 3), 3: (1, 3)}

    # усі гілки — блідо
    for ci in range(len(cols) - 1):
        x1, x2 = cols[ci], cols[ci + 1]
        for r, outs in nxt.items():
            for rr in outs:
                p.append(line(x1 + 9, rows[r], x2 - 9, rows[rr], color="#d7dbe1", sw=1.2))

    # вузли
    for x in cols:
        for y in rows:
            p.append(circle(x, y, 6, fill="#f4f6f8", stroke="#aab0b8", sw=1.4))

    # виділена гілка k-го кроку: s′ (col2,row1) → s (col3,row2), uₖ=1
    sx, sy = cols[2], rows[1]
    dx, dy = cols[3], rows[2]
    p.append(line(sx + 9, sy, dx - 9, dy, color=HOT, sw=3.2))
    p.append(circle(sx, sy, 7.5, fill=HOTFILL, stroke=HOT, sw=2.4))
    p.append(circle(dx, dy, 7.5, fill=HOTFILL, stroke=HOT, sw=2.4))
    # мітки гілки — не по центру (там перетин з іншою діагоналлю решітки), а біля
    # кінця виділеної гілки, з тонким поводирем від напису до самої лінії
    lx1, ly1 = dx - 46, dy - 66
    p.append(text(lx1, ly1, "γₖ(s′,s)", size=13, color=HOT, bold=True, anchor="middle"))
    p.append(line(lx1, ly1 + 8, dx - 30, dy - 18, color=HOT, sw=1.1))
    lx2, ly2 = dx + 58, dy - 8
    p.append(text(lx2, ly2, "uₖ = 1", size=11, color=HOT, italic=True, anchor="middle"))
    p.append(line(lx2 - 4, ly2 + 6, dx + 6, dy + 4, color=HOT, sw=1.1))
    p.append(text(sx - 16, sy - 12, "αₖ₋₁(s′)", size=12.5, color=INK, bold=True, anchor="end"))
    p.append(text(dx + 16, dy + 22, "βₖ(s)", size=12.5, color=INK, bold=True, anchor="start"))

    # α — велика стрілка вгорі вправо
    yA = 122
    p.append(arrow(cols[0] - 6, yA, cols[2] + 6, yA, color=FIELD, sw=2.6))
    p.append(text((cols[0] + cols[2]) / 2, yA - 12,
                  "α  —  прямий хід: минуле y₁…yₖ₋₁", size=12, color=FIELD, bold=True))

    # β — велика стрілка внизу вліво
    yB = 434
    p.append(arrow(cols[4] + 6, yB, cols[2] - 6, yB, color=NEG, sw=2.6))
    p.append(text((cols[2] + cols[4]) / 2, yB + 22,
                  "β  —  зворотний хід: майбутнє yₖ₊₁…yₙ", size=12, color=NEG, bold=True))

    # мітки часу
    for x, t in zip(cols, tlab):
        p.append(text(x, 402, t, size=12, color=MUTED))

    box, bw, bh = textbox(W / 2, H - 42,
                          "апостеріор біта  L(uₖ) = ln [ Σ(uₖ=1) αₖ₋₁·γₖ·βₖ  /  Σ(uₖ=0) αₖ₋₁·γₖ·βₖ ]\n"
                          "сума по всіх шляхах бере́ться колонка за колонкою: минуле × гілка × майбутнє",
                          size=12.5, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=12)
    p.append(box)

    render(os.path.join(OUT, "bcjr-trellis.svg"), W, H, *p,
           title="BCJR: суму по всіх шляхах решітки беруть прямим α, зворотним β і гілковою γ")


# ── llr-decomposition: три частки апостеріора й обмін лише зовнішнім ───────────

def fig_llr_decomposition():
    W, H = 940, 470
    p = []

    bx0, bx1 = 220, 800
    by, bh = 96, 56
    g1 = bx0 + 170          # межа канал | апріор
    g2 = g1 + 165           # межа апріор | зовнішнє
    p.append(rect(bx0, by, g1 - bx0, bh, fill=SYSFILL, stroke=SYS, sw=2.2, rx=5))
    p.append(rect(g1, by, g2 - g1, bh, fill=ILVFILL, stroke=ILV, sw=2.2, rx=5))
    p.append(rect(g2, by, bx1 - g2, bh, fill=PARFILL, stroke=PAR, sw=2.4, rx=5))
    p.append(text((bx0 + g1) / 2, by + bh / 2 + 5, "L_канал", size=13.5, color=SYS, bold=True))
    p.append(text((g1 + g2) / 2, by + bh / 2 + 5, "L_апріор", size=13.5, color=ILV, bold=True))
    p.append(text((g2 + bx1) / 2, by + bh / 2 + 5, "L_зовн", size=13.5, color=PAR, bold=True))
    p.append(text(bx0 - 16, by + bh / 2 + 5, "L_апост(uₖ) =", size=14, color=INK, bold=True, anchor="end"))

    # підписи під частками
    yn = by + bh + 32
    p.append(mtext((bx0 + g1) / 2, yn, ["= Lᴄ·yˢ", "власний систематичний відлік"], size=10.6, color=SYS))
    p.append(mtext((g1 + g2) / 2, yn, ["від напарника", "(його попередня звістка)"], size=10.6, color=ILV))
    p.append(mtext((g2 + bx1) / 2, yn, ["нове — з контролю", "й сусідніх бітів"], size=10.6, color=PAR))

    # «не віддавати» під двома лівими
    yx = yn + 46
    p.append(text((bx0 + g1) / 2, yx, "✗ напарник це вже має", size=10.4, color=HOT, bold=True))
    p.append(text((g1 + g2) / 2, yx, "✗ він це щойно й сказав", size=10.4, color=HOT, bold=True))

    # винос зовнішнього вниз до напарника — трохи праворуч від підпису колонки,
    # щоб вертикаль не різала напис "нове — з контролю…" наскрізь
    ax = (g2 + bx1) / 2
    axl = ax + 62
    p.append(arrow(axl, by + bh + 6, axl, 330, color=PAR, sw=2.6))
    b2, w2, h2 = textbox(axl, 358, "лише L_зовн → напарникові\n(стає його L_апріор)",
                         size=12.5, bold=True, color=PAR, fill=PARFILL, stroke=PAR, sw=2.0, pad=11)
    p.append(b2)

    box, bw, bh2 = textbox(360, 398,
                           "віддати весь L_апост = повернути напарникові його ж слова\n"
                           "як «незалежне» підтвердження → фальшива певність, мов виск мікрофона",
                           size=11.6, bold=True, fill="#fdecea", stroke=HOT, sw=1.8, pad=11)
    p.append(box)

    render(os.path.join(OUT, "llr-decomposition.svg"), W, H, *p,
           title="Апостеріор = канал + апріор + зовнішнє; напарникові йде лише зовнішнє")


# ── exit-chart: тунель між двома кривими і траєкторія-сходинки ────────────────

def fig_exit_chart():
    W, H = 660, 620
    p = []

    px0, px1 = 120, 540
    py0, py1 = 92, 470          # py0 — верх (I_E=1), py1 — низ (I_E=0)

    def X(a):
        return px0 + a * (px1 - px0)

    def Y(e):
        return py1 - e * (py1 - py0)

    for t in (0.0, 0.5, 1.0):
        p.append(line(X(t), py0, X(t), py1, color="#eef0f3", sw=1.0))
        p.append(line(px0, Y(t), px1, Y(t), color="#eef0f3", sw=1.0))
        p.append(text(X(t), py1 + 20, "%.1f" % t, size=10.5, color=MUTED))
        p.append(text(px0 - 12, Y(t) + 4, "%.1f" % t, size=10.5, color=MUTED, anchor="end"))
    p.append(line(px0, py1, px1, py1, color=INK, sw=1.6))
    p.append(line(px0, py0, px0, py1, color=INK, sw=1.6))
    p.append(text((px0 + px1) / 2, py1 + 44, "I_A  —  взаємна інформація на вході (від напарника)", size=11.5, color=INK))
    p.append(text(px0 - 34, (py0 + py1) / 2, "I_E", size=12, color=INK, anchor="middle"))
    p.append(line(X(0), Y(0), X(1), Y(1), color="#cfd4da", sw=1.2, dash="4 4"))

    # крива декодера 1: I_E = T(I_A); декодера 2 — відбита через діагональ
    c1 = [(0.0, 0.25), (0.2, 0.45), (0.4, 0.60), (0.6, 0.72), (0.8, 0.85), (1.0, 1.0)]
    c2 = [(e, a) for (a, e) in c1]
    p.append(polyline([(X(a), Y(e)) for a, e in c1], color=PAR, sw=3.0))
    p.append(polyline([(X(a), Y(e)) for a, e in c2], color=FIELD, sw=3.0))
    p.append(text(X(0.55), Y(0.82), "декодер 1", size=11.5, color=PAR, bold=True, anchor="start"))
    p.append(text(X(0.82), Y(0.52), "декодер 2", size=11.5, color=FIELD, bold=True, anchor="start"))

    p.append(text(X(0.27), Y(0.30), "тунель", size=12, color=INK, italic=True))
    p.append(line(X(0.33), Y(0.31), X(0.46), Y(0.42), color=INK, sw=0.9))

    # траєкторія-сходинки між кривими
    traj = [(0.0, 0.0), (0.0, 0.25), (0.45, 0.25), (0.45, 0.63),
            (0.72, 0.63), (0.72, 0.82), (0.85, 0.82), (0.85, 0.90),
            (0.95, 0.90), (0.95, 0.97), (1.0, 1.0)]
    p.append(polyline([(X(a), Y(e)) for a, e in traj], color=HOT, sw=2.0))
    p.append(circle(X(1.0), Y(1.0), 5, fill=HOTFILL, stroke=HOT, sw=2.2))
    p.append(text(X(1.0) - 8, Y(1.0) - 12, "(1, 1): біти відомі", size=10.8, color=HOT, bold=True, anchor="end"))

    box, bw, bh = textbox(W / 2, H - 66,
                          "сходинки лізуть тунелем до кута (1, 1) — це водоспад.\n"
                          "падає Eb/N0 → криві провисають → тунель змикається: той рівень і є поріг збіжності",
                          size=11.3, bold=True, fill="#f6f4ec", stroke=INK, sw=1.8, pad=11)
    p.append(box)

    render(os.path.join(OUT, "exit-chart.svg"), W, H, *p,
           title="EXIT-діаграма: доки тунель між кривими відкритий, ітерація лізе до повної певності")


if __name__ == "__main__":
    fig_encoder()
    fig_interleaver_protect()
    fig_turbo_loop()
    fig_waterfall_floor()
    fig_timeline()
    fig_iter_waterfall()
    fig_bcjr_trellis()
    fig_llr_decomposition()
    fig_exit_chart()
    print("OK: figures written to", OUT)
