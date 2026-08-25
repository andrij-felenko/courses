# -*- coding: utf-8 -*-
"""Фігури до теми «SerDes (серіалізатор-десеріалізатор)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── допоміжне: згладжений фронт 0..1 і полілінія ────────────────────────────
def edge(x0, x1, y0, y1, n=16):
    pts = []
    for i in range(n + 1):
        t = i / n
        s = 0.5 * (1 - math.cos(math.pi * t))
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * s))
    return pts


def polyline(pts, color=INK, sw=1.8, opacity=1.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    o = ' stroke-opacity="%.2f"' % opacity if opacity < 1 else ''
    pd = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s%s/>'
            % (pd, color, sw, o, d))


def wave(x0, y_hi, y_lo, ub, bits, color=INK, sw=1.8, edge_frac=0.28):
    """Цифрова хвиля зі списку бітів; перший біт задає стартовий рівень."""
    prev = bits[0]
    seq = []
    for i, b in enumerate(bits):
        x = x0 + i * ub
        yb = y_hi if b else y_lo
        yp = y_hi if prev else y_lo
        seq += edge(x, x + ub * edge_frac, yp, yb) + [(x + ub, yb)]
        prev = b
    return polyline(seq, color=color, sw=sw)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 1 — стіна перекосу: та сама розбіжність з'їдає вузьке вікно біта
# ════════════════════════════════════════════════════════════════════════════
def fig_skew_wall():
    W, H = 720, 400
    els = [text(W / 2, 24, "Стіна паралельної шини: перекіс не зникає, а вікно біта коротшає", size=15, bold=True)]

    NL = 4                                   # показуємо 4 з 8 ліній
    delays = [0, 7, 15, 24]                  # px — різні затримки ліній (перекіс)

    def panel(px, py, ub, title, ok):
        out = [text(px + 150, py - 14, title, size=13, bold=True,
                    color=(FIELD if ok else POS))]
        lane_h = 20
        for k in range(NL):
            y0 = py + k * (lane_h + 8)
            yhi, ylo = y0, y0 + lane_h
            d = delays[k]
            # одна лінія: піднімається (0→1) із власною затримкою d
            pts = [(px, ylo)] + edge(px + d, px + d + ub * 0.30, ylo, yhi) + [(px + 300, yhi)]
            out.append(polyline(pts, color=INK, sw=1.7))
            out.append(text(px - 8, y0 + lane_h * 0.7, "L%d" % (k + 1),
                            size=10.5, color=MUTED, anchor="end"))
        # мить читання приймача — вертикаль за спільним тактом (кінець вікна біта)
        smp = px + ub
        top = py - 2
        bot = py + NL * (lane_h + 8) - 8
        out.append(line(smp, top, smp, bot, color=NEG, sw=1.6, dash="5,4"))
        out.append(text(smp, bot + 16, "мить читання", size=11, color=NEG, bold=True))
        # діапазон перекосу (де фронти ще не збіглися) — сіра смуга
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
                   % (px + delays[0], top, delays[-1], bot - top, MUTED))
        out.append(text(px + 150, bot + 34,
                        ("вікно широке — усі лінії встигли: чисто"
                         if ok else "вікно вузьке — не всі встигли: байт б'ється"),
                        size=11.5, color=(FIELD if ok else POS)))
        return out

    els += panel(70, 70, 200, "Повільно: біт довгий", True)
    els += panel(430, 70, 42, "Швидко: біт короткий", False)
    render(os.path.join(IMG, "skew-wall.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 2 — лінійне кодування: сирий потік німіє, кодований несе ритм і кому
# ════════════════════════════════════════════════════════════════════════════
def fig_line_coding():
    W, H = 720, 360
    els = [text(W / 2, 24, "Навіщо кодувати: потік має сам нести ритм, баланс і межу", size=15, bold=True)]

    x0, wv = 150, 470
    yhi, ylo = 0, 0  # placeholders

    # ── верх: СИРИЙ потік з довгою серією нулів ──
    hi1, lo1 = 66, 104
    raw = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]      # довга німа серія нулів
    ub = wv / len(raw)
    els.append(line(x0, hi1, x0 + wv, hi1, color=MUTED, sw=1, dash="3,4"))
    els.append(line(x0, lo1, x0 + wv, lo1, color=MUTED, sw=1, dash="3,4"))
    els.append(wave(x0, hi1, lo1, ub, raw, color=INK, sw=1.9))
    els.append(text(x0 - 12, 88, "сирий\nбайт", size=11.5, color=INK, anchor="end")
               if False else mtext(x0 - 12, 82, ["сирий", "потік"], size=11.5, color=INK, anchor="end"))
    # позначити німу ділянку
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
               % (x0 + ub * 2, hi1 - 6, ub * 8, (lo1 - hi1) + 12, POS))
    els.append(text(x0 + ub * 6, lo1 + 22, "лінія стоїть — CDR пливе, межі не видно",
                    size=11.5, color=POS))

    # ── стрілка «8b/10b» ──
    els.append(arrow(x0 + wv * 0.5, 150, x0 + wv * 0.5, 182, color=FIELD, sw=2.4))
    els.append(text(x0 + wv * 0.5 + 8, 170, "8b/10b: 8 бітів → 10", size=12, color=FIELD, bold=True, anchor="start"))

    # ── низ: КОДОВАНИЙ потік — часті переходи + кома-мітка ──
    hi2, lo2 = 230, 268
    # кома K28.5 (RD−): 001111 1010 — канонічний comma-візерунок
    comma = [0, 0, 1, 1, 1, 1, 1, 0, 1, 0]
    body = [1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1]     # збалансований «даних» шматок
    enc = comma + body
    ub2 = wv / len(enc)
    els.append(line(x0, hi2, x0 + wv, hi2, color=MUTED, sw=1, dash="3,4"))
    els.append(line(x0, lo2, x0 + wv, lo2, color=MUTED, sw=1, dash="3,4"))
    els.append(wave(x0, hi2, lo2, ub2, enc, color=INK, sw=1.9))
    els.append(mtext(x0 - 12, hi2 + 16, ["після", "8b/10b"], size=11.5, color=INK, anchor="end"))
    # рамка навколо коми
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.12" stroke="%s" stroke-width="1.4" rx="4"/>'
               % (x0, hi2 - 10, ub2 * len(comma), (lo2 - hi2) + 20, FIELD, FIELD))
    els.append(text(x0 + ub2 * len(comma) / 2, hi2 - 16, "кома — мітка межі байта", size=11, color=FIELD, bold=True))
    els.append(text(x0 + wv * 0.72, lo2 + 22, "не більш ніж 5 однакових поспіль → рясні переходи; нулів і одиниць порівну",
                    size=11, color=INK, anchor="middle"))

    # підсумкова легенда трьох виграшів
    yb = 312
    labels = ["густі переходи → такт (CDR)", "баланс 0/1 → розв'язка", "кома → вирівнювання"]
    cols = [NEG, POS, FIELD]
    bx = 60
    for lab, c in zip(labels, cols):
        els.append(fitbox(bx, yb - 18, 196, 30, lab, size=11, fill=FILL, stroke=c, color=c, bold=True))
        bx += 206
    render(os.path.join(IMG, "line-coding.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 3 — тракт SerDes: від байта до байта через одну лінію
# ════════════════════════════════════════════════════════════════════════════
def fig_chain():
    W, H = 940, 300
    els = [text(W / 2, 24, "Тракт SerDes: одна лінія несе байт — і сама несе такт", size=15, bold=True)]

    cy = 150
    bh = 56
    bw = 78
    gap = 12
    grpw = 4 * bw + 3 * gap          # 348

    def group(x_start, boxes, caption):
        x = x_start
        for lab, fill, stroke in boxes:
            els.append(fitbox(x, cy - bh / 2, bw, bh, lab, size=12, fill=fill, stroke=stroke, bold=True))
            x += bw + gap
        xx = x_start + bw
        for _ in range(len(boxes) - 1):
            els.append(arrow(xx, cy, xx + gap, cy, color=LINE, sw=1.7))
            xx += bw + gap
        els.append(text(x_start + grpw / 2, cy - bh / 2 - 12, caption, size=12, color=INK, bold=True))

    # ── передача (ліворуч) ──
    tx_x = 26
    group(tx_x, [("байт\n8 біт", FILL, LINE), ("кодер\n8b/10b", "#eafaf0", FIELD),
                 ("серіалі-\nзатор", FILL, LINE), ("драйвер", "#eaf0fd", NEG)], "ПЕРЕДАЧА")

    # ── лінія: диференційна пара ──
    lx0 = tx_x + grpw + gap          # 386
    lx1 = lx0 + 120                  # 506
    els.append(line(lx0, cy - 6, lx1, cy - 6, color=POS, sw=2.2))
    els.append(line(lx0, cy + 6, lx1, cy + 6, color=NEG, sw=2.2))
    els.append(mtext((lx0 + lx1) / 2, cy - 14, ["диф. пара"], size=11, color=INK, bold=True))
    els.append(mtext((lx0 + lx1) / 2, cy + 30, ["1 лінія,", "без такту"], size=10.5, color=MUTED))
    els.append(arrow(lx0 + 6, cy, lx1 - 6, cy, color=FIELD, sw=1.6))

    # ── прийом (праворуч) ──
    rx_x = lx1 + gap                 # 518 → правий край групи 866 < 940
    group(rx_x, [("CDR:\nтакт", "#eaf0fd", NEG), ("читання\nбітів", FILL, LINE),
                 ("вирівн.\nпо комі", "#eafaf0", FIELD), ("декодер\n→ байт", FILL, LINE)], "ПРИЙОМ")

    # підпис про перекіс, якого нема
    els.append(text(W / 2, cy + bh / 2 + 40,
                    "між чипами — жодного окремого такту й жодного перекосу між лініями: лінія одна",
                    size=11.5, color=MUTED))
    render(os.path.join(IMG, "serdes-chain.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 4 — тумблер RD (два стани) + сходинка накопиченого заряду в ямі ±1
# ════════════════════════════════════════════════════════════════════════════
def fig_disparity():
    W, H = 760, 380
    els = [text(W / 2, 24, "Поточна невідповідність: тумблер RD і заряд у вузькій ямі",
                size=15, bold=True)]

    # ── ЛІВОРУЧ: автомат із двох станів RD− ⇄ RD+ ──
    cxL = 170
    yminus, yplus = 140, 280
    r = 40
    els.append(text(cxL, 66, "Два стани, тумблер", size=12.5, bold=True, color=INK))
    # стан RD− (сума = −1)
    els.append(circle(cxL, yminus, r, fill="#eaf0fd", stroke=NEG, sw=2.2))
    els.append(mtext(cxL, yminus - 6, ["RD−", "сума = −1"], size=12, color=NEG, bold=True))
    # стан RD+ (сума = +1)
    els.append(circle(cxL, yplus, r, fill="#fdecea", stroke=POS, sw=2.2))
    els.append(mtext(cxL, yplus - 6, ["RD+", "сума = +1"], size=12, color=POS, bold=True))

    # переходи ±2 між станами (дві дуги збоку)
    els.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
               'stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
               % (cxL + r - 4, yminus + 12, cxL + r + 52, yminus + 24,
                  cxL + r + 52, yplus - 24, cxL + r - 4, yplus - 12, POS))
    els.append(text(cxL + r + 62, (yminus + yplus) / 2 - 6, "символ", size=11, color=POS, bold=True, anchor="start"))
    els.append(text(cxL + r + 62, (yminus + yplus) / 2 + 9, "+2", size=11, color=POS, bold=True, anchor="start"))
    els.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
               'stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
               % (cxL - r + 4, yplus - 12, cxL - r - 52, yplus - 24,
                  cxL - r - 52, yminus + 24, cxL - r + 4, yminus + 12, NEG))
    els.append(text(cxL - r - 62, (yminus + yplus) / 2 - 6, "символ", size=11, color=NEG, bold=True, anchor="end"))
    els.append(text(cxL - r - 62, (yminus + yplus) / 2 + 9, "−2", size=11, color=NEG, bold=True, anchor="end"))

    # петлі «нейтральний символ (0) — стан не змінюється»
    # RD− : петля зверху; RD+ : петля знизу; підпис «0» — збоку від петлі
    els.append('<path d="M%.1f %.1f a 15 15 0 1 0 24 0" fill="none" stroke="%s" '
               'stroke-width="1.6" marker-end="url(#arrow)"/>' % (cxL - 12, yminus - r - 2, MUTED))
    els.append(text(cxL + 26, yminus - r - 12, "0", size=11, color=MUTED, bold=True))
    els.append('<path d="M%.1f %.1f a 15 15 0 1 1 24 0" fill="none" stroke="%s" '
               'stroke-width="1.6" marker-end="url(#arrow)"/>' % (cxL - 12, yplus + r + 2, MUTED))
    els.append(text(cxL + 26, yplus + r + 12, "0", size=11, color=MUTED, bold=True))

    # ── ПРАВОРУЧ: сходинка накопиченого заряду на межах символів ──
    px, py = 430, 96
    pw, ph = 290, 176
    # значення з прикладу статті (4 символи): заряд на межах символів
    syms = ["D24.1", "D0.0", "D31.5", "D3.3"]
    charge = [0, 2, 2, 0, 0]           # старт 0, далі після кожного символу
    rd_state = [1, 1, -1, -1]          # RD після кожного символу (−1/+1)
    ymid = py + ph / 2
    els.append(text(px + pw / 2, py - 16, "Накопичений заряд на межах символів", size=12.5, bold=True))
    els.append(line(px, ymid, px + pw, ymid, color=MUTED, sw=1.2))
    els.append(text(px + pw + 4, ymid + 4, "0", size=10.5, color=MUTED, anchor="start"))
    # сітка рівнів ±2
    unit = ph / 8                       # діапазон осі приблизно ±4
    for lvl in (-2, 2):
        yy = ymid - lvl * unit
        els.append(line(px, yy, px + pw, yy, color=MUTED, sw=1, dash="3,4"))
        els.append(text(px - 6, yy + 4, "%+d" % lvl, size=10.5, color=MUTED, anchor="end"))
    # коридор ±1 (зелена смуга — RD на межах символів)
    yhi = ymid - 1 * unit
    ylo = ymid + 1 * unit
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
               % (px, yhi, pw, ylo - yhi, FIELD))
    els.append(text(px + pw - 2, yhi - 5, "коридор RD = ±1 на межах", size=10, color=FIELD, bold=True, anchor="end"))

    # сходинка заряду: горизонтальні полички + вертикальні стрибки
    n = len(syms)
    step = pw / n
    seq = []
    for i in range(n):
        y0 = ymid - charge[i] * unit
        y1 = ymid - charge[i + 1] * unit
        x0 = px + i * step
        x1 = px + (i + 1) * step
        seq += [(x0, y0), (x1, y0), (x1, y1)]
    els.append(polyline(seq, color=INK, sw=2.4))
    # точки на межах + мітка стану RD кольором
    for i in range(1, n + 1):
        x = px + i * step
        y = ymid - charge[i] * unit
        col = POS if rd_state[i - 1] > 0 else NEG
        els.append(circle(x, y, 4.5, fill=col, stroke=col, sw=1))
    # підписи символів під поличками
    for i, s in enumerate(syms):
        xc = px + (i + 0.5) * step
        els.append(text(xc, py + ph + 20, s, size=10, color=INK, anchor="middle"))
    els.append(text(px + pw / 2, py + ph + 44,
                    "заряд гойдається в ямі — ніколи не тікає", size=11, color=FIELD, bold=True))

    # спільний підпис-правило внизу під лівим автоматом
    els.append(text(cxL, 360, "нейтральний (0) — стан стоїть; ±2 — перекидає тумблер",
                    size=10.5, color=MUTED))

    render(os.path.join(IMG, "disparity-rd.svg"), W, H, *els)


if __name__ == "__main__":
    fig_skew_wall()
    fig_line_coding()
    fig_chain()
    fig_disparity()
    print("OK: figures written to", IMG)
