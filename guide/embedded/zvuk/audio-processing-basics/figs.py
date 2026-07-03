# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: конвеєр обробки — від сирого буфера до готового звуку ──────────
def fig_pipeline():
    W, H = 760, 250
    parts = []
    # ланцюг блоків
    y = 110
    boxes = [
        ("сирий\nбуфер", MUTED, "#f4f6f8"),
        ("зняти\nпостійну", NEG, "#eaf0fd"),
        ("смуговий\nфільтр", INK, "#f4f6f8"),
        ("виміряти\nрівень", FIELD, "#eafaf1"),
        ("AGC:\nпідсилення", POS, "#fdecea"),
        ("готовий\nзвук", MUTED, "#f4f6f8"),
    ]
    n = len(boxes)
    bw, bh = 96, 58
    gap = (W - 40 - n * bw) / (n - 1)
    xs = []
    x = 20
    for i, (label, col, fill) in enumerate(boxes):
        parts.append(fitbox(x, y - bh / 2, bw, bh, label, size=14, stroke=col, fill=fill, bold=True))
        xs.append(x + bw)
        x += bw + gap
    # стрілки між блоками
    x = 20 + bw
    for i in range(n - 1):
        parts.append(arrow(x + 2, y, x + gap - 2, y))
        x += bw + gap
    # підпис зверху
    parts.append(text(W / 2, 40, "Що робить обробка між захопленням і використанням", size=15, bold=True))
    # зворотний зв'язок AGC (петля під блоком рівня → AGC)
    lvl_cx = xs[3] - bw / 2
    agc_cx = xs[4] - bw / 2
    fy = y + bh / 2 + 34
    parts.append(line(lvl_cx, y + bh / 2, lvl_cx, fy, color=FIELD, sw=1.6, dash="4 3"))
    parts.append(line(lvl_cx, fy, agc_cx, fy, color=FIELD, sw=1.6, dash="4 3"))
    parts.append(arrow(agc_cx, fy, agc_cx, y + bh / 2 + 2))
    parts.append(text((lvl_cx + agc_cx) / 2, fy + 16, "виміряний рівень керує підсиленням", size=11, color=FIELD))
    render(os.path.join(IMG, 'pipeline.svg'), W, H, *parts)


# ── Фігура 2: AGC веде рівень до цілі — тихий і гучний вхід ──────────────────
def fig_agc_track():
    W, H = 720, 330
    parts = []
    x0, x1 = 60, W - 30
    ytop, ybot = 60, H - 60
    mid = (ytop + ybot) / 2
    # осі
    parts.append(line(x0, ybot, x1, ybot, color=INK, sw=1.5))          # час
    parts.append(line(x0, ytop, x0, ybot, color=INK, sw=1.5))          # рівень
    parts.append(text(x1, ybot + 22, "час", size=12, color=MUTED, anchor="end"))
    parts.append(text(x0 - 8, ytop + 4, "рівень", size=12, color=MUTED, anchor="end"))
    # цільова смуга (де AGC хоче тримати вихід)
    ty, th = mid - 22, 44
    parts.append(rect(x0, ty, x1 - x0, th, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    parts.append(text(x1 - 6, ty - 6, "цільовий рівень", size=11, color=FIELD, anchor="end"))

    N = 260
    def draw_curve(fn, color, sw=2.2, dash=None):
        pts = []
        for i in range(N + 1):
            t = i / N
            xx = x0 + t * (x1 - x0)
            yy = fn(t)
            pts.append("%.1f,%.1f" % (xx, yy))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                     % (" ".join(pts), color, sw, d))

    # ВХІД: перша половина тихий, друга — гучний (обвідна)
    def env_in(t):
        base = 0.16 if t < 0.5 else 0.72
        return ybot - base * (ybot - ytop)
    # ВИХІД: AGC підтягує до цілі з інерцією (attack/release)
    tgt = 0.5  # цільова частка шкали (центр смуги)
    def env_out(t):
        # проста релаксація до цілі з розривом на середині входу
        if t < 0.5:
            # старт трохи нижче цілі, повільно доходить (release піднімає тихе)
            v = tgt - (tgt - 0.28) * math.exp(-t / 0.10)
        else:
            # стрибок гучного: спершу вилітає вгору, attack тягне вниз до цілі
            over = 0.86
            v = tgt + (over - tgt) * math.exp(-(t - 0.5) / 0.05)
        return ybot - v * (ybot - ytop)

    draw_curve(env_in, MUTED, sw=1.8, dash="5 4")
    draw_curve(env_out, POS, sw=2.4)
    # вертикаль зміни гучності входу
    xm = x0 + 0.5 * (x1 - x0)
    parts.append(line(xm, ytop, xm, ybot, color=INK, sw=1.0, dash="2 4"))
    parts.append(text(xm, ytop - 8, "вхід став гучнішим", size=11, color=INK))

    # легенда
    parts.append(line(x0 + 6, ytop - 22, x0 + 34, ytop - 22, color=MUTED, sw=1.8, dash="5 4"))
    parts.append(text(x0 + 40, ytop - 18, "рівень входу", size=11, color=MUTED, anchor="start"))
    parts.append(line(x0 + 170, ytop - 22, x0 + 198, ytop - 22, color=POS, sw=2.4))
    parts.append(text(x0 + 204, ytop - 18, "рівень виходу (після AGC)", size=11, color=POS, anchor="start"))

    parts.append(text(W / 2, 30, "AGC веде вихід до цілі, хоч вхід стрибає", size=15, bold=True))
    render(os.path.join(IMG, 'agc-track.svg'), W, H, *parts)


# ── Фігура 3: однополюсний фільтр знімає постійну (АЧХ ескізом) ──────────────
def fig_hpf():
    W, H = 640, 300
    parts = []
    x0, x1 = 70, W - 30
    ytop, ybot = 60, H - 60
    # осі
    parts.append(line(x0, ybot, x1, ybot, color=INK, sw=1.5))
    parts.append(line(x0, ytop, x0, ybot, color=INK, sw=1.5))
    parts.append(text(x1, ybot + 22, "частота", size=12, color=MUTED, anchor="end"))
    parts.append(text(x0 - 8, ytop + 2, "пропускання", size=12, color=MUTED, anchor="end"))
    # рівень «пропускає повністю»
    parts.append(line(x0, ytop + 14, x1, ytop + 14, color=MUTED, sw=1.0, dash="3 4"))
    parts.append(text(x1 - 4, ytop + 10, "1.0", size=10, color=MUTED, anchor="end"))
    parts.append(text(x0 - 8, ybot + 2, "0", size=10, color=MUTED, anchor="end"))

    # крива ВЧ-фільтра: 0 на нулі частоти → плато. H = f / (f + fc)
    fc = 0.09  # частка шкали — зріз
    N = 240
    pts = []
    for i in range(N + 1):
        t = i / N
        f = t  # 0..1 частка шкали
        Hmag = f / (f + fc)
        xx = x0 + t * (x1 - x0)
        yy = ybot - Hmag * (ybot - (ytop + 14))
        pts.append("%.1f,%.1f" % (xx, yy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), NEG))

    # позначка зрізу fc
    xc = x0 + fc * (x1 - x0)
    parts.append(line(xc, ytop + 14, xc, ybot, color=NEG, sw=1.0, dash="2 3"))
    parts.append(text(xc, ybot + 20, "зріз ~10 Гц", size=11, color=NEG))
    # ліворуч від зрізу — придушене (постійна = частота 0)
    parts.append(text(x0 + 4, ybot - 8, "постійна (0 Гц) → 0", size=11, color=POS, anchor="start"))
    # праворуч — голос проходить
    parts.append(text(x1 - 6, ytop + 40, "голос проходить вільно", size=11, color=INK, anchor="end"))

    parts.append(text(W / 2, 30, "Знімання постійної: пропусти все, крім найнижчого", size=15, bold=True))
    render(os.path.join(IMG, 'hpf.svg'), W, H, *parts)


# ── Фігура 4 (вставка hist): контури однакової гучності Флетчера–Мансона ─────
def fig_loudness():
    W, H = 680, 340
    parts = []
    x0, x1 = 74, W - 26
    ytop, ybot = 66, H - 62

    # осі
    parts.append(line(x0, ybot, x1, ybot, color=INK, sw=1.5))          # частота (лог)
    parts.append(line(x0, ytop, x0, ybot, color=INK, sw=1.5))          # потрібна енергія
    parts.append(text(x1, ybot + 38, "частота (лог), Гц", size=12, color=MUTED, anchor="end"))
    parts.append(text(x0 - 10, ytop - 14, "потрібна енергія (дБ)", size=12, color=MUTED, anchor="start"))
    parts.append(text(x0 - 10, ytop + 16, "більше", size=10, color=MUTED, anchor="end"))
    parts.append(text(x0 - 10, ybot - 6, "менше", size=10, color=MUTED, anchor="end"))

    # логарифмічна вісь частот: 20 Гц .. 16 кГц
    import math as _m
    fmin, fmax = 20.0, 16000.0
    lo, hi = _m.log10(fmin), _m.log10(fmax)
    def fx(f):
        return x0 + (_m.log10(f) - lo) / (hi - lo) * (x1 - x0)
    for f, lab in [(20, "20"), (100, "100"), (1000, "1к"), (3000, "3к"), (10000, "10к")]:
        xx = fx(f)
        parts.append(line(xx, ybot, xx, ybot + 5, color=MUTED, sw=1.0))
        parts.append(text(xx, ybot + 20, lab, size=10, color=MUTED))
    # позначка найчутливішої зони 3–4 кГц
    parts.append(line(fx(3500), ytop + 8, fx(3500), ybot, color=FIELD, sw=1.0, dash="2 4"))

    # форма контура однакової гучності (ескіз): висока чутливість коло 3–4 кГц
    # y — «потрібна енергія»: більша (вище на графіку) там, де вухо менш чутливе.
    # base_dip визначає глибину провалу коло 3.5 кГц; краї підняті.
    def contour(base, dip_extra=0.0):
        pts = []
        N = 220
        for i in range(N + 1):
            t = i / N
            lf = lo + t * (hi - lo)          # log10(f)
            f = 10 ** lf
            # відносна «потрібність енергії» у дБ понад мінімум у зоні чутливості
            L = lf  # у декадах
            # низи: круто вгору нижче ~200 Гц
            low = 26.0 * max(0.0, (_m.log10(200) - lf))
            # верхи: помірний підйом вище ~6 кГц
            high = 16.0 * max(0.0, (lf - _m.log10(6000)))
            # провал коло 3.5 кГц (резонанс слухового каналу)
            d = -6.0 * _m.exp(-((lf - _m.log10(3500)) ** 2) / (2 * 0.10 ** 2))
            val = base + low + high + d - dip_extra
            xx = x0 + t * (x1 - x0)
            # масштаб дБ → пікселі
            yy = ybot - (val) * (ybot - ytop) / 78.0
            if yy < ytop + 6:
                yy = ytop + 6
            pts.append("%.1f,%.1f" % (xx, yy))
        return " ".join(pts)

    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (contour(18.0), NEG))          # тихий контур (~40 фон) — основа A-зважування
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
                 'stroke-dasharray="6 4"/>' % (contour(46.0), MUTED))   # гучніший контур

    # підписи кривих
    parts.append(text(fx(150), ytop + 30, "тихий контур (~40 фон)", size=11, color=NEG, anchor="start"))
    parts.append(text(fx(150), ytop + 30 + 20, "→ основа A-зважування", size=11, color=NEG, anchor="start"))
    parts.append(text(fx(30), ytop + 96, "гучніший контур", size=11, color=MUTED, anchor="start"))
    parts.append(text(fx(3500), ytop + 4, "найчутливіше 3–4 кГц", size=11, color=FIELD))

    parts.append(text(W / 2, 32, "Скільки енергії треба, щоб звучало однаково гучно", size=15, bold=True))
    render(os.path.join(IMG, 'loudness.svg'), W, H, *parts)


# ── Фігура 5 (детальна): z-площина однополюсного ВЧ-фільтра ──────────────────
def fig_zplane_hpf():
    W, H = 560, 460
    parts = []
    cx, cy = W / 2, H / 2 + 6
    R = 150  # радіус одиничного кола в пікселях
    # осі
    parts.append(line(cx - R - 40, cy, cx + R + 40, cy, color=MUTED, sw=1.2))   # Re
    parts.append(line(cx, cy - R - 40, cx, cy + R + 44, color=MUTED, sw=1.2))   # Im
    parts.append(text(cx + R + 46, cy + 4, "Re", size=12, color=MUTED, anchor="start"))
    parts.append(text(cx + 6, cy - R - 30, "Im", size=12, color=MUTED, anchor="start"))
    # одиничне коло
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.8" stroke-dasharray="5 4"/>' % (cx, cy, R, INK))
    parts.append(text(cx - R * 0.72, cy - R * 0.72 - 4, "одиничне коло |z|=1",
                      size=11, color=MUTED, anchor="middle"))
    # позначки ±1 на осі Re
    parts.append(text(cx + R + 2, cy + 18, "+1", size=10, color=MUTED, anchor="middle"))
    parts.append(text(cx - R - 2, cy + 18, "−1", size=10, color=MUTED, anchor="middle"))

    # НУЛЬ у z = 1 (постійна складова, 0 Гц) — кружечок на колі праворуч
    zx = cx + R
    parts.append('<circle cx="%.1f" cy="%.1f" r="8" fill="white" stroke="%s" '
                 'stroke-width="2.4"/>' % (zx, cy, POS))
    parts.append(text(zx + 4, cy - 16, "нуль у z=1", size=12, color=POS, anchor="start", bold=True))
    parts.append(text(zx + 4, cy - 2, "(0 Гц → 0)", size=11, color=POS, anchor="start"))

    # ПОЛЮС у z = 1 − α, трохи всередині кола (α показуємо помітно збільшеною)
    a = 0.80  # для наочності: полюс усередині кола (реально ще ближче до 1)
    px = cx + a * R
    d = 7
    parts.append(line(px - d, cy - d, px + d, cy + d, color=NEG, sw=2.6))
    parts.append(line(px - d, cy + d, px + d, cy - d, color=NEG, sw=2.6))
    parts.append(text(px - 6, cy + 26, "полюс у z=1−α", size=12, color=NEG, anchor="middle", bold=True))
    parts.append(text(px - 6, cy + 42, "(ближче до 1 → вужча зона)", size=11, color=NEG, anchor="middle"))

    # напрямок зростання частоти по колу (стрілка проти годинникової вгору)
    parts.append(text(cx, cy - R - 12, "вища частота →", size=11, color=INK, anchor="middle"))

    parts.append(text(W / 2, 30, "Однополюсний ВЧ-фільтр на z-площині", size=15, bold=True))
    render(os.path.join(IMG, 'zplane-hpf.svg'), W, H, *parts)


# ── Фігура 6 (детальна): атака й відпускання як сталі часу ───────────────────
def fig_attack_release():
    W, H = 720, 340
    parts = []
    x0, x1 = 66, W - 30
    ytop, ybot = 60, H - 58
    # осі
    parts.append(line(x0, ybot, x1, ybot, color=INK, sw=1.5))
    parts.append(line(x0, ytop, x0, ybot, color=INK, sw=1.5))
    parts.append(text(x1, ybot + 22, "час", size=12, color=MUTED, anchor="end"))
    parts.append(text(x0 - 8, ytop + 2, "підсилення", size=12, color=MUTED, anchor="end"))

    # ціль (де хочемо опинитися)
    yt = ytop + 40
    parts.append(line(x0, yt, x1, yt, color=FIELD, sw=1.4, dash="6 4"))
    parts.append(text(x1 - 4, yt - 6, "ціль (want)", size=11, color=FIELD, anchor="end"))
    # старт
    ys = ybot - 30

    import math as _m
    span = ys - yt  # відстань від старту до цілі (пікселі)

    # крива відпускання (повільна, велика τ): підповзає знизу до цілі
    def rel_y(t):   # t у 0..1
        return ys - span * (1 - _m.exp(-t / 0.34))
    # крива атаки (швидка, мала τ): майже стрибком
    def atk_y(t):
        return ys - span * (1 - _m.exp(-t / 0.06))

    def curve(fn, color, sw, dash=None):
        pts = []
        N = 240
        for i in range(N + 1):
            t = i / N
            xx = x0 + t * (x1 - x0)
            pts.append("%.1f,%.1f" % (xx, fn(t)))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                     % (" ".join(pts), color, sw, d))

    curve(rel_y, NEG, 2.6)
    curve(atk_y, POS, 2.6)

    # позначка «за одну τ — 63% шляху пройдено» (тобто до 37% лишилось) на кривій відпускання
    t_tau = 0.34
    xtau = x0 + t_tau * (x1 - x0)
    ytau = rel_y(t_tau)
    parts.append(line(xtau, yt, xtau, ybot, color=MUTED, sw=1.0, dash="2 3"))
    parts.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>' % (xtau, ytau, NEG))
    parts.append(text(xtau + 6, ytau + 4, "за 1·τ: 63% шляху", size=11, color=NEG, anchor="start"))
    parts.append(text(xtau, ybot + 20, "τ (відпускання)", size=11, color=MUTED, anchor="middle"))

    # підписи кривих
    parts.append(text(x0 + 150, atk_y(0.20) - 12, "атака: мала τ (швидко)",
                      size=12, color=POS, anchor="start", bold=True))
    parts.append(text(x0 + 250, rel_y(0.62) + 22, "відпускання: велика τ (повільно)",
                      size=12, color=NEG, anchor="start", bold=True))
    parts.append(text(x0 + 4, ys + 18, "старт", size=11, color=MUTED, anchor="start"))

    parts.append(text(W / 2, 30, "Атака й відпускання — це сталі часу", size=15, bold=True))
    render(os.path.join(IMG, 'attack-release.svg'), W, H, *parts)


# ── Фігура (вставка): три режими зчепленого AGC на осі часу ──────────────────
#   голос → attack/release; тиша+утримання → ще ведемо; вичерпано → freeze.
#   пунктир — наївний AGC без зчеплення: у паузі задирає підсилення й тягне шум.
def fig_agc_vad_modes():
    W, H = 760, 400
    parts = []
    x0, x1 = 70, W - 30
    # три доріжки згори вниз: (A) прапорець VAD, (B) підсилення gain, (C) вихід
    # Доріжка A — прапорець голосу (сходинка)
    ayb = 90            # базова лінія «тиша»
    ayt = 55            # рівень «голос»
    # Доріжка B — підсилення
    byb = 250          # низ поля підсилення
    byt = 150          # верх поля підсилення
    # осі часу для кожної доріжки малюємо тонко
    parts.append(text(W / 2, 28, "Три режими зчепленого AGC у часі", size=15, bold=True))

    # часові межі подій (частки ширини)
    def X(t):
        return x0 + t * (x1 - x0)
    t_v_on  = 0.14      # голос почався
    t_v_off = 0.52      # голос стих
    t_hold  = 0.66      # утримання вичерпано → заморозка
    t_v2    = 0.86      # новий голос

    # ── Доріжка A: прапорець VAD ──
    parts.append(text(x0 - 8, (ayt + ayb) / 2, "VAD", size=12, color=INK,
                      anchor="end", bold=True))
    parts.append(line(x0, ayb, x1, ayb, color=MUTED, sw=1.0))
    # сходинка голосу: 0 → 1 на t_v_on, 1 → 0 на t_v_off, 0 → 1 на t_v2
    seg = [(x0, ayb), (X(t_v_on), ayb), (X(t_v_on), ayt), (X(t_v_off), ayt),
           (X(t_v_off), ayb), (X(t_v2), ayb), (X(t_v2), ayt), (x1, ayt)]
    pts = " ".join("%.1f,%.1f" % (a, b) for a, b in seg)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, FIELD))
    parts.append(text(X((t_v_on + t_v_off) / 2), ayt - 8, "голос", size=11,
                      color=FIELD, anchor="middle"))
    parts.append(text(X((t_v_off + t_v2) / 2), ayb + 15, "тиша", size=11,
                      color=MUTED, anchor="middle"))

    # ── Доріжка B: підсилення (зчеплене — суцільне; наївне — пунктир) ──
    parts.append(text(x0 - 8, (byt + byb) / 2, "gain", size=12, color=INK,
                      anchor="end", bold=True))
    parts.append(line(x0, byb, x1, byb, color=MUTED, sw=1.0))

    g_start = byb - 18           # стартове підсилення (низько)
    g_voice = byb - 70           # робоче підсилення на голосі
    g_freeze = g_voice           # заморожене там, де було
    # зчеплене підсилення: рівне до голосу → підйом до g_voice (відпускання) →
    # тримається → після t_hold рівна заморозка → на новому голосі знову веде
    segB = [(x0, g_start), (X(t_v_on), g_start),
            (X(t_v_off), g_voice),                 # веде вгору поки голос
            (X(t_hold), g_voice),                  # утримання: тримає
            (X(t_v2), g_freeze),                   # заморозка: рівно
            (x1, g_voice)]                          # новий голос — знову веде
    ptsB = " ".join("%.1f,%.1f" % (a, b) for a, b in segB)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (ptsB, NEG))

    # наївний AGC (без зчеплення): у паузі задирає підсилення вгору до стелі
    g_ceil = byt + 6
    segN = [(X(t_v_off), g_voice), (X(t_v2), g_ceil), (X(t_v2), g_voice)]
    ptsN = " ".join("%.1f,%.1f" % (a, b) for a, b in segN)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
                 'stroke-dasharray="5 4"/>' % (ptsN, POS))

    # вертикальні межі-орієнтири (тонкі), підписані ЗНИЗУ з запасом
    for t, lab in [(t_v_on, "голос почався"), (t_v_off, "голос стих"),
                   (t_hold, "утримання вичерпано"), (t_v2, "новий голос")]:
        parts.append(line(X(t), ayt - 6, X(t), byb + 6, color=MUTED, sw=0.8, dash="2 4"))

    # підписи режимів — під доріжкою підсилення, широко рознесені
    ly = byb + 34
    parts.append(text(X((t_v_on + t_v_off) / 2), ly, "attack / release",
                      size=12, color=NEG, anchor="middle", bold=True))
    parts.append(text(X((t_v_off + t_hold) / 2), ly + 20, "утримання (hold)",
                      size=11, color=INK, anchor="middle"))
    parts.append(text(X((t_hold + t_v2) / 2), ly, "freeze",
                      size=12, color=NEG, anchor="middle", bold=True))
    # підпис наївної кривої — окремим рядком нижче, щоб не лягав на іншу
    parts.append(text(X((t_v_off + t_v2) / 2), byt - 16,
                      "наївний AGC: задирає підсилення в паузі (тягне шум)",
                      size=11, color=POS, anchor="middle"))

    # межі-підписи знизу
    for t, lab in [(t_v_on, "голос"), (t_v_off, "стих"),
                   (t_hold, "freeze"), (t_v2, "голос")]:
        parts.append(text(X(t), byb + 74, lab, size=9, color=MUTED, anchor="middle"))
    parts.append(text(W / 2, H - 12,
                      "Заморожена лінія gain не дихає; наївна (пунктир) — тягне шум угору",
                      size=11, color=MUTED))
    render(os.path.join(IMG, 'agc-vad-modes.svg'), W, H, *parts)


# ── Фігура (вставка): архітектура зчеплення VAD ↔ AGC ────────────────────────
#   два незалежні модулі, одна ниточка керування (прапорець) + синхронізація гейта.
def fig_agc_vad_coupling():
    W, H = 780, 340
    parts = []
    parts.append(text(W / 2, 30, "Зчеплення VAD ↔ AGC: два модулі, одна ниточка керування",
                      size=15, bold=True))

    yrow = 150         # головний рядок конвеєра
    bw, bh = 116, 60

    # блоки конвеєра: чистий кадр → (роздвоєння) → AGC → важкий модуль
    x_in   = 24
    x_split = x_in + bw + 40
    x_agc  = 430
    x_out  = x_agc + bw + 54

    parts.append(fitbox(x_in, yrow - bh / 2, bw, bh,
                        "чистий кадр\n(пост.+смуга)", size=12, stroke=INK, fill=FILL, bold=True))
    # точка роздвоєння
    parts.append(circle(x_split, yrow, 4, fill=INK, stroke=INK))
    parts.append(arrow(x_in + bw + 2, yrow, x_split - 2, yrow))

    # AGC (нижче — на головному рядку)
    parts.append(fitbox(x_agc, yrow - bh / 2, bw, bh,
                        "зчеплений AGC\n(gain / freeze)", size=12, stroke=POS,
                        fill="#fdecea", bold=True))
    parts.append(arrow(x_split, yrow, x_agc - 2, yrow))

    # вихід
    parts.append(fitbox(x_out, yrow - bh / 2, bw, bh,
                        "рівний звук\n→ важке", size=12, stroke=MUTED, fill=FILL, bold=True))
    parts.append(arrow(x_agc + bw + 2, yrow, x_out - 2, yrow))

    # VAD — окремим блоком ЗВЕРХУ, живиться з точки роздвоєння
    yvad = 66
    x_vad = x_split - bw / 2
    parts.append(fitbox(x_vad, yvad - bh / 2 + 4, bw, bh,
                        "сторож VAD\n(є голос?)", size=12, stroke=FIELD,
                        fill="#eafaf1", bold=True))
    # відгалуження вгору до VAD
    parts.append(line(x_split, yrow - 2, x_split, yvad + bh / 2 - 4 + 8, color=INK, sw=1.4))
    parts.append(arrow(x_split, yvad + bh / 2, x_split, yvad + bh / 2 - 2, color=INK))

    # ниточка керування: прапорець voice з VAD → AGC (згори вниз, праворуч)
    xflag = x_vad + bw
    parts.append(line(xflag, yvad, xflag + 150, yvad, color=FIELD, sw=2.0))
    parts.append(line(xflag + 150, yvad, xflag + 150, yrow - bh / 2 - 2, color=FIELD, sw=2.0))
    parts.append(arrow(xflag + 150, yrow - bh / 2 - 2, x_agc + bw / 2, yrow - bh / 2 - 2, color=FIELD))
    parts.append(text(xflag + 78, yvad - 8, "прапорець voice", size=11,
                      color=FIELD, anchor="middle", bold=True))

    # тонша стрілка синхронізації: фон VAD → шумовий поріг AGC (знизу, пунктир)
    ysync = yrow + bh / 2 + 44
    parts.append(line(x_vad, yvad + bh / 2 - 4 + 8, x_vad, ysync, color=MUTED, sw=1.3, dash="4 3"))
    parts.append(line(x_vad, ysync, x_agc + 20, ysync, color=MUTED, sw=1.3, dash="4 3"))
    parts.append(arrow(x_agc + 20, ysync, x_agc + 20, yrow + bh / 2 + 2, color=MUTED))
    parts.append(text((x_vad + x_agc) / 2, ysync + 15,
                      "фон VAD задає шумовий поріг AGC", size=11, color=MUTED, anchor="middle"))

    parts.append(text(W / 2, H - 12,
                      "Сторож вирішує «чи є голос»; AGC — «яким бути підсиленню». Один булів прапорець між ними.",
                      size=11, color=MUTED))
    render(os.path.join(IMG, 'agc-vad-coupling.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_pipeline()
    fig_agc_track()
    fig_hpf()
    fig_loudness()
    fig_zplane_hpf()
    fig_attack_release()
    fig_agc_vad_modes()
    fig_agc_vad_coupling()
    print("figs done")
