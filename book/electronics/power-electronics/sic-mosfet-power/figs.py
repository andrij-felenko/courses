# -*- coding: utf-8 -*-
"""Фігури до теми «SiC-MOSFET у силовій електроніці».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

EPS0 = 8.854e-14


def bfom(er, mu, ec):
    return er * EPS0 * mu * ec ** 3


BF_SI = bfom(11.7, 1350, 0.30e6)
BF_SIC = bfom(9.7, 950, 2.8e6)


# ══════════════════════════════════════════════════════════════════════════════
# Стаття sic-mosfet-power.md
# ══════════════════════════════════════════════════════════════════════════════

# ── 0a. Заборонена зона: кремній проти SiC, і критичне поле як наслідок ───────
def fig_band_gap_compare():
    W, H = 900, 480
    f = [text(W / 2, 30, "Заборонена зона: у SiC утричі ширша — і критичне поле майже вдесятеро вище",
              size=16, bold=True)]

    def bands(cx, gap_ev, label, accent):
        top, bot = 90, 330
        # шкала однакова для обох (0…3.6 еВ), щоб щілини порівнювались візуально
        scale = (bot - top) / 3.6
        cb_y = top
        vb_y = top + gap_ev * scale
        bw = 220
        x = cx - bw / 2
        f.append(rect(x, cb_y - 26, bw, 26, fill="#eafaf1", stroke=FIELD, sw=2, rx=4))
        f.append(text(cx, cb_y - 8, "зона провідності", size=12, color=FIELD, bold=True))
        f.append(rect(x, vb_y, bw, 26, fill="#eaf0fd", stroke=NEG, sw=2, rx=4))
        f.append(text(cx, vb_y + 18, "валентна зона", size=12, color=NEG, bold=True))
        # щілина — сама подвійна стрілка (без центральної лінії, щоб не різати напис "N.N еВ")
        f.append(arrow(cx - 70, cb_y - 4, cx - 70, vb_y + 4, color=accent, sw=2))
        f.append(arrow(cx - 70, vb_y + 4, cx - 70, cb_y - 4, color=accent, sw=2))
        f.append(fitbox(cx - 66, (cb_y + vb_y) / 2 - 20, 132, 40,
                        "%.1f еВ" % gap_ev, size=15, bold=True,
                        fill="#ffffff", stroke=accent, sw=2))
        f.append(text(cx, bot + 34, label, size=15, bold=True, color=INK))

    bands(230, 1.1, "кремній", NEG)
    bands(670, 3.3, "карбід кремнію (4H-SiC)", FIELD)

    f.append(line(450, 90, 450, 364, color="#dfe4ea", sw=1.4, dash="5,5"))

    f.append(arrow(340, 400, 560, 400, color=INK, sw=2))
    f.append(fitbox(280, 420, 340, 42,
                    "щілина втричі ширша  →  бар'єр міцніший  →\nкритичне поле Ec майже вдесятеро вище",
                    size=13, bold=True, fill="#fdecea", stroke=POS, sw=2))

    return render(os.path.join(IMG, 'band-gap-compare.svg'), W, H, *f)


# ── 0b. Дрейфова область на ту саму напругу: товста й рідка проти тонкої й густої
def fig_drift_region():
    W, H = 900, 520
    f = [text(W / 2, 30, "Дрейфова область на 1200 В: кремній товстий і рідкий, SiC — тонкий і густий",
              size=16, bold=True)]

    top, bot = 90, 380
    def slab(cx, width_px, thickness_um, dop_dots, label, sub, accent, bg):
        x = cx - width_px / 2
        f.append(rect(x, top, width_px, bot - top, fill=bg, stroke=accent, sw=2.4, rx=6))
        # легування — крапки, густіші в SiC
        import random as _r
        rnd = _r.Random(1234 if dop_dots > 40 else 42)
        for _ in range(dop_dots):
            px = x + 14 + rnd.random() * (width_px - 28)
            py = top + 14 + rnd.random() * (bot - top - 28)
            f.append(circle(px, py, 2.2, fill=accent, stroke="none"))
        f.append(text(cx, top - 14, label, size=15, bold=True, color=accent))
        f.append(text(cx, bot + 26, "d ≈ %s мкм" % thickness_um, size=14, bold=True, color=INK))
        f.append(text(cx, bot + 46, sub, size=12, color=MUTED))

    slab(230, 240, "60…100", 22, "кремній", "слабо легований, товстий", NEG, "#eaf0fd")
    slab(670, 44, "≈ 4.3", 90, "карбід кремнію", "легований у ~100× густіше", FIELD, "#eafaf1")

    # спільна шкала товщини (умовна) — стрілка з написом
    f.append(line(120, top - 40, 120, bot, color=MUTED, sw=1.2))
    f.append(text(120, top - 46, "той самий бар'єр 1200 В", size=12, color=MUTED, anchor="start"))

    f.append(arrow(360, 235, 560, 235, color=INK, sw=2))
    f.append(fitbox(340, 470, 500, 40,
                    "майже вдесятеро тонший і в рази густіший шар — той самий бар'єр,\n"
                    "але у SiC несе набагато менший опір",
                    size=13, bold=True, fill="#fdecea", stroke=POS, sw=2))

    return render(os.path.join(IMG, 'drift-region.svg'), W, H, *f)


# ── 0c. Повні втрати проти частоти: перетин IGBT/SiC ───────────────────────────
def fig_loss_crossover():
    W, H = 900, 520
    f = [text(W / 2, 30, "Повні втрати проти частоти: хвіст струму робить IGBT крутим, SiC — пологим",
              size=16, bold=True)]

    L, R = 110, 810
    T, B = 90, 380
    fmax, pmax = 60.0, 100.0
    px = lambda fr: L + (fr / fmax) * (R - L)
    py = lambda p: B - (p / pmax) * (B - T)

    for p in range(0, 101, 20):
        y = py(p)
        f.append(line(L - 5, y, L, y, color=MUTED, sw=1.2))
        f.append(text(L - 12, y + 4, "%d" % p, size=12, color=MUTED, anchor="end"))
    for fr in range(0, 61, 10):
        x = px(fr)
        f.append(line(x, B, x, B + 5, color=MUTED, sw=1.2))
        f.append(text(x, B + 22, "%d" % fr, size=12, color=MUTED))

    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(L - 8, T - 14, "повні втрати, Вт", size=13, color=INK, anchor="start", bold=True))
    f.append(text((L + R) / 2, B + 48, "частота перемикання, кГц", size=14, color=INK, bold=True))

    # IGBT: конд. база + квадратичний нахил (хвіст росте зі струмом/частотою різко)
    igbt_cond, igbt_k = 18.0, 0.020
    sic_cond, sic_k = 12.0, 0.0032
    igbt_pts = " ".join("%.1f,%.1f" % (px(fr), py(igbt_cond + igbt_k * fr * fr))
                        for fr in range(0, 61, 2))
    sic_pts = " ".join("%.1f,%.1f" % (px(fr), py(sic_cond + sic_k * fr * fr * fr / 12.0))
                       for fr in range(0, 61, 2))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (igbt_pts, POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (sic_pts, FIELD))

    # точка перетину (наближено там, де криві сходяться)
    fx = 8.0
    f.append(line(px(fx), T, px(fx), B, color=MUTED, sw=1.6, dash="6,4"))
    f.append(circle(px(fx), py(igbt_cond + igbt_k * fx * fx), 6, fill="#ffffff", stroke=INK, sw=2))
    f.append(fitbox(px(fx) + 14, py(igbt_cond) - 8, 190, 38,
                    "точка перетину", size=13, bold=True, fill="#ffffff", stroke=INK, sw=1.6))

    f.append(text(px(50), py(igbt_cond + igbt_k * 50 * 50) - 16, "IGBT — хвіст струму", size=13,
                  bold=True, color=POS))
    f.append(text(px(50), py(sic_cond + sic_k * 50 * 50 * 50 / 12.0) + 22, "SiC-MOSFET", size=13,
                  bold=True, color=FIELD))

    f.append(fitbox(L, B + 66, R - L, 40,
                    "Провідні втрати майже сталі; втрати перемикання ростуть із частотою.\n"
                    "У IGBT — крутіше через хвіст струму, у SiC — полого: праворуч від перетину SiC холодніший.",
                    size=13, fill="#f7f9fb", stroke=MUTED, sw=1.4))

    return render(os.path.join(IMG, 'loss-crossover.svg'), W, H, *f)


# ── 0d. Карта приладів у координатах напруга–частота ──────────────────────────
def fig_device_map():
    W, H = 900, 560
    f = [text(W / 2, 30, "Карта силових приладів: напруга проти частоти перемикання",
              size=16, bold=True)]

    L, R = 130, 800
    T, B = 90, 420
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(L - 10, T - 14, "напруга блокування", size=13, color=INK, anchor="start", bold=True))
    f.append(text((L + R) / 2, B + 40, "частота перемикання →", size=14, color=INK, bold=True))
    f.append(text(L - 10, B + 40, "низька", size=12, color=MUTED, anchor="start"))
    f.append(text(R, B + 40, "висока", size=12, color=MUTED, anchor="end"))
    f.append(text(L - 10, T + 10, "висока", size=12, color=MUTED, anchor="start"))
    f.append(text(L - 10, B - 6, "низька", size=12, color=MUTED, anchor="start"))

    midx, midy = (L + R) / 2.0, (T + B) / 2.0

    # нижня смуга — кремнієвий MOSFET (низька напруга, будь-яка частота)
    f.append(rect(L, midy, R - L, B - midy, fill="#eaf0fd", stroke=NEG, sw=2, rx=0))
    f.append(text((L + R) / 2, midy + (B - midy) / 2 + 5, "кремнієвий MOSFET",
                  size=15, bold=True, color=NEG))
    f.append(text((L + R) / 2, midy + (B - midy) / 2 + 26, "низька напруга — будь-яка частота",
                  size=12, color=MUTED))

    # верхньо-ліва зона — кремнієвий IGBT (висока напруга, низька частота)
    f.append(rect(L, T, midx - L, midy - T, fill="#fdecea", stroke=POS, sw=2, rx=0))
    f.append(text(L + (midx - L) / 2, T + (midy - T) / 2, "кремнієвий IGBT",
                  size=15, bold=True, color=POS))
    f.append(text(L + (midx - L) / 2, T + (midy - T) / 2 + 21, "висока напруга,",
                  size=12, color=MUTED))
    f.append(text(L + (midx - L) / 2, T + (midy - T) / 2 + 38, "низька частота",
                  size=12, color=MUTED))

    # верхньо-права зона — SiC-MOSFET (висока напруга, висока частота)
    f.append(rect(midx, T, R - midx, midy - T, fill="#eafaf1", stroke=FIELD, sw=2, rx=0))
    f.append(text(midx + (R - midx) / 2, T + (midy - T) / 2, "SiC-MOSFET",
                  size=16, bold=True, color=FIELD))
    f.append(text(midx + (R - midx) / 2, T + (midy - T) / 2 + 21, "висока напруга,",
                  size=12, color=MUTED))
    f.append(text(midx + (R - midx) / 2, T + (midy - T) / 2 + 38, "висока частота",
                  size=12, color=MUTED))

    f.append(line(L, midy, R, midy, color="#dfe4ea", sw=1.4, dash="5,5"))
    f.append(line(midx, T, midx, midy, color="#dfe4ea", sw=1.4, dash="5,5"))

    f.append(fitbox(L, B + 66, R - L, 42,
                    "Низька напруга — кремнієвий MOSFET поза конкуренцією за ціною. Висока напруга й "
                    "низька частота — IGBT ще тримається. Висока напруга з високою частотою — вотчина SiC.",
                    size=13, fill="#f7f9fb", stroke=MUTED, sw=1.4))

    return render(os.path.join(IMG, 'device-map.svg'), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
# Вставка math-baliga-fom.md
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Бухгалтерія куба: 1 від товщини + 2 від легування ──────────────────────
def fig_cube_ledger():
    W, H = 900, 500
    f = [text(W / 2, 30, "Звідки куб: один степінь від товщини, два від легування", size=16, bold=True)]

    # Вхід — один важіль
    f.append(fitbox(320, 52, 260, 46, "поле міцніше в 10 разів", size=14, bold=True,
                    fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(450, 116, "при ТІЙ САМІЙ напрузі BV", size=12, color=MUTED))

    # Дві гілки
    f.append(arrow(430, 124, 250, 168, color=FIELD, sw=2))
    f.append(arrow(470, 124, 650, 168, color=FIELD, sw=2))

    # Ліва гілка — товщина
    f.append(fitbox(100, 172, 300, 84,
                    "шар тонший у 10 разів\nd = 2·BV / Ec", size=13,
                    fill=FILL, stroke=LINE, sw=1.6))
    f.append(fitbox(100, 274, 300, 44, "менший опір: ÷ 10", size=13, bold=True,
                    fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(250, 344, "один степінь Ec", size=13, color=NEG, bold=True))

    # Права гілка — легування
    f.append(fitbox(500, 172, 300, 84,
                    "легування густіше у 100 разів\nNd = ε·Ec² / (2·q·BV)", size=13,
                    fill=FILL, stroke=LINE, sw=1.6))
    f.append(fitbox(500, 274, 300, 44, "менший опір: ÷ 100", size=13, bold=True,
                    fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(650, 344, "два степені Ec", size=13, color=NEG, bold=True))

    # Чому саме два — підказка
    f.append(text(650, 366, "бо BV — площа трикутника:", size=11, color=MUTED))
    f.append(text(650, 384, "і висота, і основа несуть поле", size=11, color=MUTED))
    f.append(text(250, 366, "бо напруга — поле × товщина", size=11, color=MUTED))

    # Зведення
    f.append(arrow(250, 398, 380, 428, color=LINE, sw=1.8))
    f.append(arrow(650, 398, 520, 428, color=LINE, sw=1.8))
    f.append(fitbox(300, 434, 300, 46, "1 + 2 = 3   →   Ron·A ÷ 1000", size=15, bold=True,
                    fill="#fdecea", stroke=POS, sw=2.2))

    return render(os.path.join(IMG, 'cube-ledger.svg'), W, H, *f)


# ── 2. Водоспад: із чого складається виграш SiC ───────────────────────────────
def fig_fom_waterfall():
    W, H = 900, 480
    f = [text(W / 2, 30, "Виграш SiC над кремнієм: куб поля дає, ε і μ віддають", size=16, bold=True)]

    ox, base = 110, 380          # початок осей, лінія «×1»
    top = 78
    f.append(line(ox, base, ox + 700, base, color=MUTED, sw=1.4))
    f.append(line(ox, base + 4, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox - 12, top - 10, "у скільки разів краще (лог)", size=11, color=MUTED, anchor="start"))

    # логарифмічна шкала від 1 до 1000
    def ypos(v):
        return base - (math.log10(max(v, 1.0)) / 3.0) * (base - top)

    for v in (1, 10, 100, 1000):
        yy = ypos(v)
        f.append(line(ox - 5, yy, ox + 700, yy, color="#e5e7eb", sw=1.0))
        f.append(text(ox - 12, yy + 4, "×%d" % v, size=11, color=MUTED, anchor="end"))

    steps = [
        (u"куб поля\n(2.8/0.3)³", 813.0, POS, "#fdecea"),
        (u"рухливість\n950/1350", 813.0 * 0.7037, NEG, "#eaf0fd"),
        (u"проникність\n9.7/11.7", 474.3, NEG, "#eaf0fd"),
    ]

    bw, gap = 150, 40
    x = ox + 55
    prev_top = base
    prev_x2 = None
    for i, (lab, val, col, fill) in enumerate(steps):
        yt = ypos(val)
        f.append(rect(x, yt, bw, base - yt, fill=fill, stroke=col, sw=2))
        f.append(text(x + bw / 2, yt - 12, "×%.0f" % val, size=14, bold=True, color=col))
        f.append(mtext(x + bw / 2, base + 26, lab.split("\n"), size=12, color=INK, lh=1.25))
        if prev_x2 is not None:
            f.append(line(prev_x2, prev_top, x, prev_top, color=MUTED, sw=1.2, dash="4,3"))
        prev_top, prev_x2 = yt, x + bw
        x += bw + gap

    # підсумкова позначка
    f.append(line(ox, ypos(474.3), ox + 700, ypos(474.3), color=FIELD, sw=1.6, dash="6,4"))
    f.append(text(ox + 700, ypos(474.3) - 10, "підсумок ×474", size=13, bold=True,
                  color=FIELD, anchor="end"))

    f.append(text(W / 2, 452, "Куб поля дає майже тисячу; нижча рухливість і нижча ε "
                              "забирають назад учетверо менше — і гору бере куб.",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, 'fom-waterfall.svg'), W, H, *f)


# ── 3. Сліпа пляма: яку частку опору BFOM узагалі бачить ──────────────────────
def fig_fom_blind_spot():
    W, H = 900, 520
    f = [text(W / 2, 30, "Що показник Баліги міряє, а що ні: частка дрейфу в опорі SiC-ключа",
              size=16, bold=True)]

    fixed = 2.5e-3            # Ом·см², «сталі» складники (канал, підкладка, контакти)
    cases = [(650, ), (1200, ), (3300, ), (10000, )]

    ox, base, top = 120, 400, 90
    bw, gap = 130, 60
    x = ox

    for (bv, ) in cases:
        drift = 4.0 * bv * bv / BF_SIC
        total = drift + fixed
        share = drift / total
        hh = base - top
        hd = hh * share
        # дрейф — зверху, зелений (це й міряє BFOM)
        f.append(rect(x, top + (hh - hd), bw, hd, fill="#eafaf1", stroke=FIELD, sw=2, rx=0))
        # решта — знизу, сірий
        f.append(rect(x, top, bw, hh - hd, fill="#f0f0f2", stroke=MUTED, sw=1.6, rx=0))
        # підписи
        f.append(text(x + bw / 2, top + (hh - hd) + hd / 2 + 5, "%.0f%%" % (share * 100),
                      size=14, bold=True, color=FIELD if share > 0.12 else INK))
        f.append(text(x + bw / 2, base + 26, "%d В" % bv, size=14, bold=True))
        f.append(text(x + bw / 2, base + 48, "дрейф %.2f" % (drift * 1e3), size=11, color=MUTED))
        f.append(text(x + bw / 2, base + 66, "усього %.2f мОм·см²" % (total * 1e3), size=11, color=MUTED))
        x += bw + gap

    # легенда — з великим запасом, окремим рядком
    f.append(rect(ox, 440, 26, 16, fill="#eafaf1", stroke=FIELD, sw=2, rx=3))
    f.append(text(ox + 36, 453, "дрейфова область — рівно те, що передбачає ε·μ·Ec³",
                  size=12, anchor="start"))
    f.append(rect(ox, 470, 26, 16, fill="#f0f0f2", stroke=MUTED, sw=1.6, rx=3))
    f.append(text(ox + 36, 483, "канал, підкладка, контакти — показник їх не бачить (взято ~2.5 мОм·см²)",
                  size=12, anchor="start"))

    return render(os.path.join(IMG, 'fom-blind-spot.svg'), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
# Вставка proj-sic-vs-igbt-losses.md
# ══════════════════════════════════════════════════════════════════════════════

WARM = "#fdecea"   # тло «тут холодніший IGBT»
COOL = "#eafaf1"   # тло «тут холодніший SiC»


# ── 4. Частота-перетин як пряма від струму ────────────────────────────────────
def fig_fcross_vs_current():
    W, H = 900, 570
    f = [text(W / 2, 30, "Частота-перетин залежить від струму (800 В, D = 0.5, гарячі прилади)",
              size=16, bold=True)]

    L, R = 115, 800
    T, B = 92, 424
    imax, fmax = 40.0, 18.0
    px = lambda i: L + (i / imax) * (R - L)
    py = lambda fr: B - (fr / fmax) * (B - T)

    ibe, slope = 7.51, 0.2674          # А, кГц/А — з моделі у тексті
    fk = lambda i: max(0.0, slope * (i - ibe))

    # тло: ліворуч від струму-беззбитковості SiC виграє всюди
    f.append(rect(L, T, px(ibe) - L, B - T, fill=COOL, stroke="none", sw=0, rx=0))
    # під прямою — зона IGBT
    pts = " ".join("%.1f,%.1f" % (px(i), py(fk(i)))
                   for i in [ibe + k * (imax - ibe) / 40.0 for k in range(41)])
    f.append('<polygon points="%.1f,%.1f %s %.1f,%.1f" fill="%s" stroke="none"/>'
             % (px(ibe), B, pts, px(imax), B, WARM))

    # смуга типових частот інвертора (заливка — під написами)
    f.append(rect(L, py(16), R - L, py(8) - py(16), fill="#eef2ff", stroke="none", sw=0, rx=0))

    # осі — лише засічки, без наскрізної сітки (щоб лінії не різали написи)
    for v in range(0, 19, 3):
        y = py(v)
        f.append(line(L - 5, y, L, y, color=MUTED, sw=1.2))
        f.append(text(L - 12, y + 4, "%d" % v, size=12, color=MUTED, anchor="end"))
    for i in range(0, 41, 5):
        x = px(i)
        f.append(line(x, B, x, B + 5, color=MUTED, sw=1.2))
        f.append(text(x, B + 22, "%d" % i, size=12, color=MUTED))

    f.append(line(L, py(8), R, py(8), color=NEG, sw=1.6, dash="7,5"))
    f.append(text(266, py(12), "типова частота інвертора: 8…16 кГц",
                  size=13, color=NEG, anchor="start", bold=True))

    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(L - 8, T - 14, "частота-перетин, кГц", size=13, color=INK,
                  anchor="start", bold=True))
    f.append(text((L + R) / 2, B + 48, "струм через ключ, А", size=14, color=INK, bold=True))

    # сама пряма
    f.append(line(px(ibe), py(0), px(imax), py(fk(imax)), color=POS, sw=3))

    # струм-беззбитковість
    f.append(line(px(ibe), T, px(ibe), B, color=FIELD, sw=2, dash="6,4"))
    f.append(circle(px(ibe), py(0), 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(px(ibe) + 4, B + 42, "струм-беззбитковість 7.5 А", size=12,
                  color="#1e7d4a", bold=True, anchor="start"))

    # робоча точка
    f.append(circle(px(20), py(fk(20)), 6, fill=POS, stroke="#ffffff", sw=2))
    f.append(line(px(20), py(fk(20)), px(20) + 60, py(fk(20)) - 46, color=INK, sw=1.2))
    f.append(fitbox(px(20) + 60, py(fk(20)) - 76, 128, 30, "20 А → 3.3 кГц",
                    size=13, fill="#ffffff", stroke=POS, sw=1.6))

    # підписи зон
    f.append(mtext(px(3.6), py(5.4), ["SiC", "виграє", "за будь-", "якої", "частоти"],
                   size=13, color="#1e7d4a", bold=True, lh=1.25))
    f.append(mtext(px(16.5), py(5.0), ["вище прямої —", "SiC холодніший"],
                   size=13, color="#1e7d4a", bold=True, lh=1.25))
    f.append(mtext(px(31), py(2.0), ["нижче прямої —", "IGBT холодніший"],
                   size=13, color="#a03227", bold=True, lh=1.25))

    f.append(fitbox(L, B + 66, R - L, 40,
                    "f = D · (Rds(on) − rce) · (I − I_бз) / k    —  струм скорочується, "
                    "і перетин виходить ПРЯМОЮ від I_бз = Vce0 / (Rds(on) − rce)",
                    size=13, fill="#f7f9fb", stroke=MUTED, sw=1.4))

    return render(os.path.join(IMG, 'fcross-vs-current.svg'), W, H, *f)


# ── 5. Склад втрат: провідність не росте, перемикання росте ───────────────────
def fig_loss_split_bars():
    W, H = 900, 560
    f = [text(W / 2, 30, "Із чого складаються втрати: 800 В, 20 А, D = 0.5, гарячі прилади",
              size=16, bold=True)]

    L, R = 110, 810
    T, B = 92, 432
    pmax = 265.0
    py = lambda p: B - (p / pmax) * (B - T)

    data = [("5 кГц", 28.8, 3.4, 15.4, 23.3),
            ("10 кГц", 28.8, 6.8, 15.4, 46.7),
            ("50 кГц", 28.8, 34.2, 15.4, 233.3)]
    C_COND_S, C_SW_S = "#1e7d4a", "#8fd6ac"
    C_COND_I, C_SW_I = "#8c2b21", "#f1a79c"

    for p in range(0, 261, 50):
        y = py(p)
        f.append(line(L - 5, y, L, y, color=MUTED, sw=1.2))
        f.append(text(L - 12, y + 4, "%d" % p, size=12, color=MUTED, anchor="end"))

    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(L - 8, T - 14, "втрати на ключ, Вт", size=13, color=INK,
                  anchor="start", bold=True))

    gw, bw = (R - L) / 3.0, 60.0
    for k, (lab, sc, ss, ic, isw) in enumerate(data):
        cx = L + gw * (k + 0.5)
        for j, (cond, swe, c1, c2, nm) in enumerate(
                [(sc, ss, C_COND_S, C_SW_S, "SiC"), (ic, isw, C_COND_I, C_SW_I, "IGBT")]):
            x = cx - bw - 14 + j * (bw + 28)
            hc = (cond / pmax) * (B - T)
            hs = (swe / pmax) * (B - T)
            f.append(rect(x, B - hc, bw, hc, fill=c1, stroke=INK, sw=1.2, rx=0))
            f.append(rect(x, B - hc - hs, bw, hs, fill=c2, stroke=INK, sw=1.2, rx=0))
            f.append(text(x + bw / 2, B - hc - hs - 10, "%.0f Вт" % (cond + swe),
                          size=13, color=INK, bold=True))
            f.append(text(x + bw / 2, B + 20, nm, size=12, color=INK, bold=True))
            if hs >= 32:
                f.append(text(x + bw / 2, B - hc - hs / 2 + 5, "%.0f" % swe, size=12, color=INK))
            if hc >= 32:
                f.append(text(x + bw / 2, B - hc / 2 + 5, "%.0f" % cond, size=12, color="#ffffff"))
        f.append(text(cx, B + 44, lab, size=15, color=INK, bold=True))

    ly = B + 66
    for j, (c, s) in enumerate([(C_COND_S, "провідні (SiC)"), (C_SW_S, "перемикання (SiC)"),
                                (C_COND_I, "провідні (IGBT)"), (C_SW_I, "перемикання (IGBT)")]):
        x = L + j * 176
        f.append(rect(x, ly, 20, 14, fill=c, stroke=INK, sw=1, rx=2))
        f.append(text(x + 26, ly + 12, s, size=12, color=INK, anchor="start"))

    f.append(fitbox(L, ly + 30, R - L, 36,
                    "Провідний стовпчик від частоти не залежить — росте лише стовпчик "
                    "перемикання. У SiC він росте вп'ятеро повільніше.",
                    size=13, fill="#f7f9fb", stroke=MUTED, sw=1.4))

    return render(os.path.join(IMG, 'loss-split-bars.svg'), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
# Вставка hist-sic-devices.md
# ══════════════════════════════════════════════════════════════════════════════

BAND = "#eef1f4"
GREEN_BG, RED_BG, AMBER_BG = "#eafaf1", "#fdecea", "#fff4e0"
AMBER = "#a06000"


# ── 6. Столітня дорога: фізику знали рано, кристал — пізно ────────────────────
def fig_sic_century():
    W, H = 960, 856
    SPINE, TX = 310, 345
    f = [text(W / 2, 30, "Сто років карбіду кремнію: фізику знали з 1907-го, кристал — аж наприкінці",
              size=16, bold=True)]

    def era(y0, y1, lines):
        f.append(rect(24, y0, 170, y1 - y0, fill=BAND, stroke="#dfe4ea", sw=1, rx=8))
        cy = (y0 + y1) / 2
        f.append(mtext(109, cy - (len(lines) - 1) * 13 * 1.3 / 2 + 13 * 0.35,
                       lines, size=13, color=MUTED, bold=True))

    era(66, 300, ["Матеріал є,", "приладу нема"])
    era(410, 650, ["Учаться", "вирощувати", "кристал"])
    era(650, 824, ["Прилади"])

    # хребет — розірваний рівно там, де стала промисловість
    f.append(line(SPINE, 66, SPINE, 300, color=MUTED, sw=2.5))
    f.append(line(SPINE, 410, SPINE, 824, color=MUTED, sw=2.5))

    def row(y, year, lines, accent=INK):
        f.append(circle(SPINE, y, 6, fill=BG, stroke=accent, sw=2.5))
        f.append(text(282, y + 5, year, size=15, color=accent, anchor="end", bold=True))
        f.append(mtext(TX, y - (len(lines) - 1) * 14 * 1.3 / 2 + 14 * 0.35,
                       lines, size=14, color=INK, anchor="start"))

    row(90, "1891", ["Ачесон плавить глину з коксом, шукаючи діамант.",
                     "Дістає карборунд — найтвердіший абразив свого часу."])
    row(152, "1906", ["Патент Данвуді: карборундовий детектор.",
                      "Карбід кремнію — перший напівпровідник у продажу."])
    row(214, "1907", ["Раунд: 10 В на кристал — і той світиться.",
                      "Два абзаци в Electrical World, без пояснення."])
    row(276, "1927", ["Лосєв дослідив те свічення й пояснив його квантово.",
                      "Сорок три праці; лист Айнштайнові."])

    f.append(rect(240, 300, 580, 110, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(530, 324, "Півстоліття без кристала", size=14, color=POS, bold=True))
    f.append(mtext(530, 348, ["Кремній тягнеться з розплаву (Чохральський, 1916).",
                              "Карбід кремнію розплаву не має: за ~2700 °C він сублімує.",
                              "Нема розплаву — нема булі, пластини, промисловості."],
                   size=13, color=MUTED))

    row(442, "1955", ["Лелі (Philips): сублімація дає чисті пластинки —",
                      "випадкового розміру й перемішаних політипів."])
    row(502, "1978", ["Таїров і Цвєтков (ЛЕТІ, Ленінград): затравка.",
                      "Сублімація на зерно → буля заданого політипу."])
    row(562, "1987", ["Палмор (NCSU): перший SiC-MOSFET у лабораторії.",
                      "Засновано Cree."])
    row(620, "1991", ["Cree: перші комерційні SiC-пластини.",
                      "Мікротрубок ≥100 на см² — приладу не збудувати."])
    row(682, "2001", ["Infineon: перший комерційний діод Шотткі.",
                      "Ні затвора, ні оксиду, кристал ≈1 мм² — терпить дефекти."], accent=FIELD)
    row(742, "2007", ["Cree: 100-мм пластина без мікротрубок (ZMP)."], accent=FIELD)
    row(794, "2010–11", ["ROHM: масове виробництво MOSFET (2010).",
                         "Cree: перший «повністю кваліфікований» (2011)."], accent=FIELD)

    return render(os.path.join(IMG, 'sic-century.svg'), W, H, *f)


# ── 7. Чому першим був діод: та сама пластина, різна площа кристала ───────────
def fig_micropipe_yield():
    W, H = 900, 476
    X0, LW, CW = 24, 320, 270
    f = [text(W / 2, 30, "Та сама пластина: діод уже можна продавати, MOSFET — ще ні",
              size=16, bold=True)]

    def cell(x, y, w, h, val, bg, fg):
        f.append(rect(x + 6, y + 6, w - 12, h - 12, fill=bg, stroke="#dfe4ea", sw=1, rx=6))
        f.append(text(x + w / 2, y + h / 2 + 8, val, size=22, color=fg, bold=True))

    f.append(rect(X0 + LW, 56, CW, 62, fill=BAND, stroke="#dfe4ea", sw=1, rx=6))
    f.append(mtext(X0 + LW + CW / 2, 80, ["Діод Шотткі", "кристал ≈ 1 мм²"], size=14, bold=True))
    f.append(rect(X0 + LW + CW, 56, CW, 62, fill=BAND, stroke="#dfe4ea", sw=1, rx=6))
    f.append(mtext(X0 + LW + CW + CW / 2, 80, ["MOSFET", "кристал ≈ 25 мм²"], size=14, bold=True))
    f.append(mtext(X0 + 10, 80, ["Густина мікротрубок", "у пластині"],
                   size=13, color=MUTED, bold=True, anchor="start"))

    rows = [("≥ 100 /см²", "перші комерційні пластини, 1991",
             "37 %", AMBER_BG, AMBER, "≈ 0", RED_BG, POS),
            ("≈ 20 /см²", "кінець 1990-х",
             "82 %", GREEN_BG, FIELD, "0.7 %", RED_BG, POS),
            ("≈ 1 /см²", "початок 2000-х",
             "99 %", GREEN_BG, FIELD, "78 %", GREEN_BG, FIELD),
            ("≈ 0.1 /см² і менше", "після ZMP, 2007",
             "99.9 %", GREEN_BG, FIELD, "97 %", GREEN_BG, FIELD)]

    y = 118
    for lab, sub, v1, b1, c1, v2, b2, c2 in rows:
        f.append(text(X0 + 10, y + 27, lab, size=15, anchor="start", bold=True))
        f.append(text(X0 + 10, y + 47, sub, size=12, color=MUTED, anchor="start"))
        cell(X0 + LW, y, CW, 66, v1, b1, c1)
        cell(X0 + LW + CW, y, CW, 66, v2, b2, c2)
        y += 66

    f.append(text(W / 2, 414, "Вихід придатних кристалів:   Y = e^(−D·A)", size=15, bold=True))
    f.append(text(W / 2, 442, "D — густина мікротрубок, A — площа кристала. Один наскрізний канал —",
                  size=13, color=MUTED))
    f.append(text(W / 2, 460, "і прилад пробитий; на великому кристалі влучає майже напевно.",
                  size=13, color=MUTED))

    return render(os.path.join(IMG, 'micropipe-yield.svg'), W, H, *f)


if __name__ == '__main__':
    print(fig_band_gap_compare())
    print(fig_drift_region())
    print(fig_loss_crossover())
    print(fig_device_map())
    print(fig_cube_ledger())
    print(fig_fom_waterfall())
    print(fig_fom_blind_spot())
    print(fig_fcross_vs_current())
    print(fig_loss_split_bars())
    print(fig_sic_century())
    print(fig_micropipe_yield())
