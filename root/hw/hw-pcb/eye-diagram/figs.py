# -*- coding: utf-8 -*-
"""Фігури до теми «Діаграма ока».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# ── допоміжне: одна «дуга» переходу рівня (згладжений фронт, tanh-подібний) ──
def edge(x0, x1, y0, y1, n=24):
    """Список точок згладженого переходу від (x0,y0) до (x1,y1)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        s = 0.5 * (1 - math.cos(math.pi * t))   # плавний S-перехід 0..1
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * s))
    return pts

def polyline(pts, color=INK, sw=1.6, opacity=1.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    o = ' stroke-opacity="%.2f"' % opacity if opacity < 1 else ''
    pd = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s%s/>'
            % (pd, color, sw, o, d))

# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 1 — як народжується око: нарізати потік по бітах і накласти
# ════════════════════════════════════════════════════════════════════════════
def fig_build():
    W, H = 772, 340
    els = [text(W/2, 26, "Як народжується око: нарізати потік і накласти шматки один на одний", size=15, bold=True)]

    # ── ліворуч: довга послідовність бітів ──
    lx, lw = 40, 300
    hi, lo = 70, 150          # рівні 1 і 0
    bits = [1,0,1,1,0,0,1,0]
    ub = lw / len(bits)       # ширина біта
    # осьові рівні
    els.append(line(lx, hi, lx+lw, hi, color=MUTED, sw=1, dash="3,4"))
    els.append(line(lx, lo, lx+lw, lo, color=MUTED, sw=1, dash="3,4"))
    els.append(text(lx-6, hi+4, "1", size=12, color=MUTED, anchor="end"))
    els.append(text(lx-6, lo+4, "0", size=12, color=MUTED, anchor="end"))
    # сама траса
    prev = bits[0]
    seq = []
    for i, b in enumerate(bits):
        x0 = lx + i*ub
        yb = hi if b else lo
        yp = hi if prev else lo
        seq += edge(x0, x0+ub*0.35, yp, yb) + [(x0+ub, yb)]
        prev = b
    els.append(polyline(seq, color=INK, sw=1.8))
    # вертикальні межі бітів (пунктир) — місця розрізу
    for i in range(len(bits)+1):
        x = lx + i*ub
        els.append(line(x, hi-14, x, lo+14, color=POS, sw=1, dash="2,3"))
    els.append(text(lx+lw/2, lo+40, "довгий потік бітів — ріжемо по межах (червоне)", size=12, color=MUTED))
    els.append(text(lx+lw/2, 52, "приймач бачить це", size=12, color=INK))

    # ── стрілка «накласти» ──
    els.append(arrow(360, 130, 410, 130, color=FIELD, sw=2.4))
    els.append(text(385, 116, "накласти", size=12, color=FIELD, bold=True))

    # ── праворуч: усі шматки поверх себе → око ──
    rx, rw = 470, 210
    rhi, rlo = 70, 150
    els.append(line(rx, rhi, rx+rw, rhi, color=MUTED, sw=1, dash="3,4"))
    els.append(line(rx, rlo, rx+rw, rlo, color=MUTED, sw=1, dash="3,4"))
    els.append(text(rx-6, rhi+4, "1", size=12, color=MUTED, anchor="end"))
    els.append(text(rx-6, rlo+4, "0", size=12, color=MUTED, anchor="end"))
    # накладаємо всі 4 типи переходів у одному вікні шириною ub2 (одна UI по центру)
    ub2 = rw
    cx0 = rx
    def seg(a, b, jit=0.0, col=INK, op=0.5):
        # перехід рівня a→b у вікні; jit — зсув моменту переходу
        y_a = rhi if a else rlo
        y_b = rhi if b else rlo
        m0 = cx0 + ub2*(0.30+jit)
        m1 = cx0 + ub2*(0.62+jit)
        pts = [(cx0, y_a)] + edge(m0, m1, y_a, y_b) + [(cx0+ub2, y_b)]
        return polyline(pts, color=col, sw=1.5, opacity=op)
    for j in (-0.03, 0.0, 0.03):
        els.append(seg(0,1,j)); els.append(seg(1,0,j))
        els.append(seg(1,1,j)); els.append(seg(0,0,j))
    els.append(text(rx+rw/2, 52, "усе поверх усього = ОКО", size=12, color=INK))
    els.append(text(rx+rw/2, rlo+40, "переходи ↑↓ малюють повіки,\nа «1→1» і «0→0» — верхню й нижню рейку", size=11.5, color=MUTED))

    render(os.path.join(IMG, "eye-build.svg"), W, H, *els)

# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 2 — анатомія розкритого ока: висота, ширина, мить відліку
# ════════════════════════════════════════════════════════════════════════════
def fig_anatomy():
    W, H = 700, 380
    els = [text(W/2, 26, "Анатомія розкритого ока: що з нього зчитують", size=15, bold=True)]

    ox, oy = 120, 60          # лівий верх поля ока
    ow, oh = 380, 250
    top, bot = oy+20, oy+oh-20        # рівні 1 і 0
    left, right = ox, ox+ow
    midx = ox+ow/2
    midy = (top+bot)/2

    # рамка-осі
    els.append(line(left, top, right, top, color=MUTED, sw=1, dash="3,4"))
    els.append(line(left, bot, right, bot, color=MUTED, sw=1, dash="3,4"))
    els.append(text(left-8, top+4, "1", size=12, color=MUTED, anchor="end"))
    els.append(text(left-8, bot+4, "0", size=12, color=MUTED, anchor="end"))
    els.append(text(left-30, midy+4, "V", size=13, color=INK, anchor="end", italic=True))
    els.append(text(right+6, bot+26, "час (одна UI)", size=12, color=MUTED, anchor="end"))

    # точки перетину повік — ліворуч і праворуч від центру
    cxl = left + ow*0.16
    cxr = left + ow*0.84
    # КАНОНІЧНЕ око: кілька накладених прямих трас із легким розкидом за фазою,
    # усі проходять через два перетини (cxl,midy) та (cxr,midy).
    # рейка «1»-«1» (верх) і «0»-«0» (низ) — плоскі, поза перетинами
    for dx in (-6, 0, 6):
        # верхня рейка з боків + спуски до перетинів (falling / rising edges)
        els.append(polyline([(left,top),(cxl+dx,midy)], color=INK, sw=1.5))   # 1→0 ліворуч
        els.append(polyline([(left,bot),(cxl+dx,midy)], color=INK, sw=1.5))   # 0→1 ліворуч
        els.append(polyline([(cxr+dx,midy),(right,top)], color=INK, sw=1.5))  # 0→1 праворуч
        els.append(polyline([(cxr+dx,midy),(right,bot)], color=INK, sw=1.5))  # 1→0 праворуч
    # плоскі рейки, що тримають рівень (1→1 і 0→0) крізь усе вікно
    for dy in (-3, 0, 3):
        els.append(line(left, top+dy, right, top+dy, color=INK, sw=1.4))
        els.append(line(left, bot+dy, right, bot+dy, color=INK, sw=1.4))

    # внутрішній отвір ока (зелений ромб — реальна форма розкриву)
    eye_top = top + (midy-top)*0.30
    eye_bot = bot - (bot-midy)*0.30
    # ромб-розкрив: вершини — два перетини (боки) і верх/низ отвору
    rhx = midx - (cxr-cxl)/2*0.78
    els.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" fill-opacity="0.14" stroke="%s" stroke-width="1.3" stroke-dasharray="4,4"/>'
               % (rhx, midy, midx, eye_top, midx+(midx-rhx), midy, midx, eye_bot, FIELD, FIELD))

    # ВИСОТА ока (вертикальна стрілка по центру)
    els.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
               % (midx, eye_top, midx, eye_bot, NEG))
    els.append(text(midx+8, midy-4, "висота", size=12, color=NEG, anchor="start", bold=True))
    els.append(text(midx+8, midy+12, "= запас за напругою", size=11, color=NEG, anchor="start"))

    # ШИРИНА ока (горизонтальна стрілка на рівні midy, трохи вище низу)
    wy = eye_bot+14
    els.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
               % (cxl+6, wy, cxr-6, wy, POS))
    els.append(text(midx, wy+16, "ширина = запас за часом", size=12, color=POS, bold=True))

    # мить відліку — вертикаль по центру
    els.append(line(midx, top-6, midx, bot+6, color=INK, sw=1.4, dash="5,4"))
    els.append(text(midx, top-10, "мить відліку", size=11.5, color=INK, bold=True))

    # точки перетину
    els.append(circle(cxl, midy, 3.5, fill=INK, stroke=INK))
    els.append(circle(cxr, midy, 3.5, fill=INK, stroke=INK))
    els.append(text(cxl-4, midy+20, "перетин", size=10.5, color=MUTED, anchor="middle"))

    # права легенда
    lx = right+40
    els.append(fitbox(lx, 70, 150, 60, "Ширше й вище око —\nнадійніший приймач", size=12, fill="#eafaf0", stroke=FIELD))
    els.append(fitbox(lx, 150, 150, 74, "Читаємо саме\nв мить відліку —\nу центрі, де око\nнайрозкритіше", size=11.5, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "eye-anatomy.svg"), W, H, *els)

# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 3 — що стуляє око: три різні винуватці
# ════════════════════════════════════════════════════════════════════════════
def fig_closing():
    W, H = 720, 300
    els = [text(W/2, 24, "Три способи стулити око — і кожен вказує на свою причину", size=15, bold=True)]

    pw = 210                    # ширина панелі
    gap = 22
    x0 = 30
    ptop, pbot = 70, 210        # рівні 1 і 0 в панелі
    mid = (ptop+pbot)/2

    def panel(px, title, sub, kind):
        out = [text(px+pw/2, 50, title, size=13, bold=True)]
        # осі
        out.append(line(px, ptop, px+pw, ptop, color=MUTED, sw=1, dash="3,4"))
        out.append(line(px, pbot, px+pw, pbot, color=MUTED, sw=1, dash="3,4"))
        cxl, cxr = px+pw*0.16, px+pw*0.84
        # ідеальні межі ока (сірий контур для порівняння)
        out.append(polyline([(px,ptop),(cxl,mid),(px,pbot)], color=MUTED, sw=1, opacity=0.6))
        out.append(polyline([(px+pw,ptop),(cxr,mid),(px+pw,pbot)], color=MUTED, sw=1, opacity=0.6))
        if kind == "isi":
            # мляві фронти: перетини «розповзаються» по вертикалі → око нижче
            for d in (0.0, 0.05, -0.05, 0.10, -0.10):
                yl = mid + (pbot-mid)*d*2.2
                yr = mid - (pbot-mid)*d*2.2
                out.append(polyline([(px,ptop),(cxl,yl),(px,pbot)], color=INK, sw=1.3, opacity=0.55))
                out.append(polyline([(px+pw,ptop),(cxr,yr),(px+pw,pbot)], color=INK, sw=1.3, opacity=0.55))
            arrows = ("вертикально", NEG)
        elif kind == "noise":
            # шум: рівні «дрижать» по вертикалі — товсті розмиті рейки
            import random
            random.seed(3)
            for k in range(9):
                jt = (k-4)*1.8
                out.append(polyline([(px,ptop+jt),(cxl,mid),(px,pbot+jt)], color=INK, sw=1.1, opacity=0.4))
                out.append(polyline([(px+pw,ptop+jt),(cxr,mid),(px+pw,pbot+jt)], color=INK, sw=1.1, opacity=0.4))
                out.append(line(px, ptop+jt, cxl, ptop+jt, color=INK, sw=1.0, dash=None))
                out.append(line(cxr, ptop+jt, px+pw, ptop+jt, color=INK, sw=1.0))
                out.append(line(px, pbot+jt, cxl, pbot+jt, color=INK, sw=1.0))
                out.append(line(cxr, pbot+jt, px+pw, pbot+jt, color=INK, sw=1.0))
            arrows = ("вертикально", NEG)
        else:  # jitter
            # тремтіння фаз: перетини «розповзаються» по горизонталі → око вужче
            for d in (-0.09,-0.045,0,0.045,0.09):
                cl = cxl + pw*d
                cr = cxr + pw*d
                out.append(polyline([(px,ptop),(cl,mid),(px,pbot)], color=INK, sw=1.3, opacity=0.55))
                out.append(polyline([(px+pw,ptop),(cr,mid),(px+pw,pbot)], color=INK, sw=1.3, opacity=0.55))
            arrows = ("горизонтально", POS)
        out.append(text(px+pw/2, pbot+30, sub, size=11.5, color=INK))
        out.append(text(px+pw/2, pbot+48, "око стуляється " + arrows[0], size=11, color=arrows[1], bold=True))
        return out

    els += panel(x0,             "МІЖСИМВОЛЬНА ЗАВАДА", "мляві фронти не встигають —\nхвіст біта лізе в сусідній", "isi")
    els += panel(x0+pw+gap,      "ШУМ", "рівні «дрижать» по напрузі —\nрейки розмиваються", "noise")
    els += panel(x0+2*(pw+gap),  "ДЖИТЕР", "моменти переходів «пливуть» —\nперетини розповзаються", "jitter")

    render(os.path.join(IMG, "eye-closing.svg"), W, H, *els)

# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 4 — маска: заборонений шестикутник у центрі ока
# ════════════════════════════════════════════════════════════════════════════
def fig_mask():
    W, H = 700, 320
    els = [text(W/2, 26, "Маска: заборонена зона в центрі — жодна траса не сміє її торкнутись", size=15, bold=True)]

    def scene(px, title, ok):
        top, bot = 70, 250
        ow = 250
        mid = (top+bot)/2
        left, right = px, px+ow
        cxl, cxr = left+ow*0.18, right-ow*0.18
        midx = (left+right)/2
        out = [text(midx, 52, title, size=13, bold=True, color=(FIELD if ok else POS))]
        out.append(line(left, top, right, top, color=MUTED, sw=1, dash="3,4"))
        out.append(line(left, bot, right, bot, color=MUTED, sw=1, dash="3,4"))
        # око (кілька трас)
        squeeze = 0.0 if ok else 0.32     # у поганому випадку око піджате
        for d in (-0.06,-0.03,0,0.03,0.06):
            yl = mid + (bot-mid)*squeeze
            yr = mid - (bot-mid)*squeeze
            out.append(polyline([(left,top),(cxl+ow*d,mid),(left,bot)], color=INK, sw=1.3, opacity=0.5))
            out.append(polyline([(right,top),(cxr+ow*d,mid),(right,bot)], color=INK, sw=1.3, opacity=0.5))
        # у поганому — одна траса ПРОВАЛЮЄТЬСЯ в маску
        if not ok:
            out.append(polyline([(left,top),(midx-6,mid+6),(right,bot)], color=POS, sw=2.2))
            out.append(polyline([(left,bot),(midx+6,mid-6),(right,top)], color=POS, sw=2.2))
        # шестикутник-маска
        mw, mh = (cxr-cxl)*0.46, (bot-top)*0.30
        hx = [(midx-mw*0.5, mid),(midx-mw*0.22, mid-mh*0.5),(midx+mw*0.22, mid-mh*0.5),
              (midx+mw*0.5, mid),(midx+mw*0.22, mid+mh*0.5),(midx-mw*0.22, mid+mh*0.5)]
        pd = " ".join("%.1f,%.1f" % p for p in hx)
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="1.8"/>'
                   % (pd, POS, POS))
        out.append(text(midx, mid+4, "маска", size=11, color=POS, bold=True))
        verdict = "ПРОЙДЕНО" if ok else "ПРОВАЛ"
        out.append(text(midx, bot+34, verdict + ": " + ("маска чиста" if ok else "траса зайшла в маску"),
                        size=12, color=(FIELD if ok else POS), bold=True))
        return out

    els += scene(60,  "око розкрите", True)
    els += scene(390, "око стулилось", False)
    render(os.path.join(IMG, "eye-mask.svg"), W, H, *els)

# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 5 — багаторівневе око SIGSALY: 6 рівнів PCM → драбина з 5 просвітів
# ════════════════════════════════════════════════════════════════════════════
def fig_sigsaly_eye():
    W, H = 730, 360
    els = [text(W/2, 24, "Багаторівневе око SIGSALY: шість рівнів голосу → драбина просвітів", size=15, bold=True)]

    NLEV = 6                       # рівні 0..5
    # спільна вертикальна шкала рівнів
    ytop, ybot = 60, 300           # рівень 5 (верх) .. рівень 0 (низ)
    def ylev(v):                   # y для рівня v (0..5): рівень 0 знизу, 5 зверху
        return ybot - (ybot - ytop) * v / (NLEV - 1)

    # ── ліворуч: сходинковий сигнал шести рівнів ──
    lx, lw = 40, 300
    seqv = [2, 5, 3, 0, 4, 1, 3, 2]        # довільні рівні комірок
    ub = lw / len(seqv)
    # горизонтальні сітки-рівні
    for v in range(NLEV):
        y = ylev(v)
        els.append(line(lx, y, lx + lw, y, color=MUTED, sw=1, dash="2,4"))
        els.append(text(lx - 6, y + 4, str(v), size=11, color=MUTED, anchor="end"))
    # сама сходинкова траса з плавними переходами
    prev = seqv[0]
    seq = []
    for i, v in enumerate(seqv):
        x0 = lx + i * ub
        seq += edge(x0, x0 + ub * 0.32, ylev(prev), ylev(v)) + [(x0 + ub, ylev(v))]
        prev = v
    els.append(polyline(seq, color=INK, sw=1.9))
    # межі комірок (місця розрізу, кожні 20 мс)
    for i in range(len(seqv) + 1):
        x = lx + i * ub
        els.append(line(x, ytop - 8, x, ybot + 8, color=POS, sw=1, dash="2,3"))
    els.append(text(lx + lw/2, 46, "оцифрована мова: рівень кожні 20 мс", size=12, color=INK))
    els.append(text(lx + lw/2, ybot + 30, "ріжемо по межах комірок (червоне)", size=11.5, color=MUTED))

    # ── стрілка ──
    els.append(arrow(352, 175, 398, 175, color=FIELD, sw=2.4))
    els.append(text(375, 161, "накласти", size=12, color=FIELD, bold=True))

    # ── праворуч: усі комірки поверх одного вікна → 5 просвітів ──
    rx, rw = 452, 230
    for v in range(NLEV):
        y = ylev(v)
        els.append(line(rx, y, rx + rw, y, color=MUTED, sw=1, dash="2,4"))
    # накладаємо переходи між усіма парами сусідніх/далеких рівнів з легким розкидом фази
    def trans(a, b, jit, op=0.42):
        ya, yb = ylev(a), ylev(b)
        m0 = rx + rw * (0.30 + jit)
        m1 = rx + rw * (0.64 + jit)
        pts = [(rx, ya)] + edge(m0, m1, ya, yb) + [(rx + rw, yb)]
        return polyline(pts, color=INK, sw=1.2, opacity=op)
    pairs = [(0,1),(1,0),(1,2),(2,1),(2,3),(3,2),(3,4),(4,3),(4,5),(5,4),
             (0,3),(3,0),(2,5),(5,2),(1,4),(4,1),(0,5),(5,0),(2,2),(3,3)]
    for (a, b) in pairs:
        for j in (-0.035, 0.0, 0.035):
            els.append(trans(a, b, j))

    # мить відліку — вертикаль, де просвіти найширші (центр вікна переходів)
    smpx = rx + rw * 0.47
    els.append(line(smpx, ytop - 6, smpx, ybot + 6, color=INK, sw=1.5, dash="5,4"))
    els.append(text(smpx, ytop - 10, "мить відліку", size=11.5, color=INK, bold=True))
    # підсвітити 5 просвітів зеленими вічками в миті відліку
    for v in range(NLEV - 1):
        yc = (ylev(v) + ylev(v + 1)) / 2
        gap = abs(ylev(v) - ylev(v + 1))
        els.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="1.1"/>'
                    % (smpx, yc, rw * 0.11, gap * 0.30, FIELD, FIELD))
    els.append(text(rx + rw/2, 46, "усі комірки поверх себе = 5 «вічок»", size=12, color=INK))
    els.append(text(rx + rw/2, ybot + 30, "де вічка найширші — там читаємо рівень", size=11.5, color=FIELD))

    render(os.path.join(IMG, "sigsaly-eye.svg"), W, H, *els)

if __name__ == "__main__":
    fig_build()
    fig_anatomy()
    fig_closing()
    fig_mask()
    fig_sigsaly_eye()
    print("OK: figures written to", IMG)
