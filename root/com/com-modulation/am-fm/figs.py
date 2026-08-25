# -*- coding: utf-8 -*-
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольори за змістом
MSG = FIELD        # повідомлення / огинаюча (зелене)
CAR = NEG          # несуча / сигнал (синє)
HOT = POS          # акцент-небезпека (червоне): перемодуляція, шум
LO  = MUTED        # другорядні підписи


def polyline(pts, color, sw=2.0, fill="none"):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, color, sw)


def path(pts, color, sw=2.0, fill="none", dash=None):
    d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)


def samp(x0, x1, n=240):
    return [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]


# ── Фігура 1: побудова AM — повідомлення стає огинаючою ──────────────────────

def fig_am_build():
    W, H = 760, 460
    x0, x1 = 70, 700
    p = []

    def axis(cy, lbl, col):
        out = line(x0, cy, x1, cy, color=MUTED, sw=1.0, dash="3 4")
        out += text(x0 - 8, cy + 4, lbl, size=12, color=col, bold=True, anchor="end")
        return out

    # геометрія повільного повідомлення (1.5 періоду)
    def m(x):
        u = (x - x0) / (x1 - x0)
        return 0.7 * math.sin(2 * math.pi * 1.5 * u)

    # рядок 1: повідомлення
    cy1 = 95
    p.append(axis(cy1, "m(t)", MSG))
    p.append(path([(x, cy1 - 36 * (m(x) / 0.7)) for x in samp(x0, x1)], MSG, sw=2.6))
    p.append(text(x0, 50, "повільне повідомлення (звук)", size=12.5, color=MSG, bold=True, anchor="start"))

    # рядок 2: несуча (стала амплітуда)
    cy2 = 205
    p.append(axis(cy2, "несуча", CAR))
    p.append(path([(x, cy2 - 34 * math.sin(2 * math.pi * 26 * (x - x0) / (x1 - x0))) for x in samp(x0, x1, 460)], CAR, sw=1.4))
    p.append(text(x0, 160, "швидка несуча (стала амплітуда)", size=12.5, color=CAR, bold=True, anchor="start"))

    # рядок 3: AM-сигнал + огинаючі
    cy3 = 350
    p.append(axis(cy3, "AM", CAR))
    p.append(text(x0, 290, "AM-сигнал: амплітуда «дихає» в такт із m(t)", size=12.5, color=INK, bold=True, anchor="start"))
    env = 0.92
    amp = [(0.5 + 0.5 * env * (m(x) / 0.7)) for x in samp(x0, x1, 460)]  # огинаюча 0..1
    A0 = 64
    sig = [(x, cy3 - A0 * a * math.sin(2 * math.pi * 26 * (x - x0) / (x1 - x0)))
           for x, a in zip(samp(x0, x1, 460), amp)]
    p.append(path(sig, CAR, sw=1.4))
    up = [(x, cy3 - A0 * a) for x, a in zip(samp(x0, x1, 460), amp)]
    dn = [(x, cy3 + A0 * a) for x, a in zip(samp(x0, x1, 460), amp)]
    p.append(path(up, MSG, sw=2.0))
    p.append(path(dn, MSG, sw=2.0))
    p.append(text(x1, cy3 - A0 - 6, "огинаюча = форма звуку", size=11.5, color=MSG, bold=True, anchor="end"))

    b, bw, bh = textbox(W / 2, 430, "Приймач: діод відсікає пів-хвилі, конденсатор згладжує — на виході вже огинаюча, тобто звук.",
                        size=12, color=INK, fill="#eef6ef", stroke=MSG, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "am-build.svg"), W, H, *p,
           title="AM: повідомлення керує амплітудою й стає огинаючою")


# ── Фігура 2: глибина модуляції μ ────────────────────────────────────────────

def fig_am_index():
    W, H = 780, 360
    p = []
    panel_w = 230
    gap = 18
    x = 40
    cases = [(0.5, "μ = 0.5 — недомодуляція", "запас не вичерпано", MUTED),
             (1.0, "μ = 1.0 — повна", "максимум без спотворень", MSG),
             (1.45, "μ = 1.45 — перемодуляція", "огинаюча рве за нуль", HOT)]
    cy = 175
    A0 = 70
    for mu, ttl, sub, col in cases:
        cx = x + panel_w / 2
        # осі
        p.append(line(x + 8, cy, x + panel_w - 8, cy, color=MUTED, sw=1.0, dash="3 4"))
        # огинаюча та сигнал
        def env(t):  # t у 0..1, дві півхвилі
            return 0.5 + 0.5 * mu * math.sin(2 * math.pi * 1.0 * t)
        pts = []
        ups, dns = [], []
        for i in range(220):
            t = i / 219
            xx = x + 12 + (panel_w - 24) * t
            a = env(t)
            ac = max(a, 0.0)  # фізично огинаюча не від'ємна
            # ефект перемодуляції: фаза перевертається там, де env<0
            sign = 1.0 if a >= 0 else -1.0
            pts.append((xx, cy - A0 * abs(a) * sign * math.sin(2 * math.pi * 11 * t)))
            ups.append((xx, cy - A0 * abs(a)))
            dns.append((xx, cy + A0 * abs(a)))
        p.append(path(pts, col if mu > 1 else CAR, sw=1.3))
        p.append(path(ups, col, sw=2.0))
        p.append(path(dns, col, sw=2.0))
        # нульова лінія акцент при перемодуляції
        if mu > 1:
            p.append(text(cx, cy + A0 + 30, "хрип, спотворення", size=11, color=HOT, bold=True))
        p.append(text(cx, 40, ttl, size=12.5, color=col, bold=True))
        p.append(text(cx, 58, sub, size=10.5, color=MUTED))
        x += panel_w + gap

    b, bw, bh = textbox(W / 2, 330, "μ = (A_max − A_min) / (A_max + A_min);  тримай μ ≤ 1.",
                        size=12.5, color=INK, bold=True, min_w=440)
    p.append(b)

    render(os.path.join(OUT, "am-index.svg"), W, H, *p,
           title="Глибина модуляції μ: наскільки можна гойдати амплітуду")


# ── Фігура 3: спектр AM — несуча + дві бічні смуги ────────────────────────────

def fig_am_sidebands():
    W, H = 740, 360
    ax, ay, axw = 70, 250, 600
    p = []
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 22, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 6, ay + 5, "f", size=15, color=INK, italic=True, anchor="start"))

    f_c = ax + 320
    df = 120
    f_l, f_u = f_c - df, f_c + df

    def stick(fx, h, col, lbl, sub=None):
        out = line(fx, ay, fx, ay - h, color=col, sw=3.2)
        out += line(fx, ay - 4, fx, ay + 4, color=MUTED, sw=1.2)
        out += text(fx, ay + 20, lbl, size=12, color=col, bold=True)
        if sub:
            out += text(fx, ay + 36, sub, size=10.5, color=MUTED)
        return out

    # несуча — висока лінія, та в ній нуль інформації
    p.append(stick(f_c, 150, CAR, "fₒ", "несуча"))
    p.append(text(f_c, ay - 158, "несе ~½ потужності, 0 інформації", size=11, color=HOT, bold=True))
    # бічні смуги
    p.append(stick(f_l, 70, MSG, "fₒ−fₘ"))
    p.append(stick(f_u, 70, MSG, "fₒ+fₘ"))
    p.append(text(f_l, ay - 78, "бічна", size=11, color=MSG, bold=True))
    p.append(text(f_u, ay - 78, "бічна", size=11, color=MSG, bold=True))
    p.append(text(f_c, ay - 96, "уся інформація — тут →", size=11, color=MSG, bold=True))

    # смуга B = 2 fм
    yb = ay + 64
    p.append(line(f_l, yb, f_u, yb, color=INK, sw=1.4))
    p.append(line(f_l, yb - 5, f_l, yb + 5, color=INK, sw=1.4))
    p.append(line(f_u, yb - 5, f_u, yb + 5, color=INK, sw=1.4))
    p.append(text(f_c, yb + 18, "смуга B = 2·fₘ", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "am-sidebands.svg"), W, H, *p,
           title="Спектр AM: несуча та дві бічні смуги")


# ── Фігура 4: побудова FM — повідомлення керує частотою ───────────────────────

def fig_fm_build():
    W, H = 760, 360
    x0, x1 = 70, 700
    p = []

    def m(x):
        u = (x - x0) / (x1 - x0)
        return math.sin(2 * math.pi * 1.0 * u)

    cy1 = 95
    p.append(line(x0, cy1, x1, cy1, color=MUTED, sw=1.0, dash="3 4"))
    p.append(text(x0 - 8, cy1 + 4, "m(t)", size=12, color=MSG, bold=True, anchor="end"))
    p.append(path([(x, cy1 - 38 * m(x)) for x in samp(x0, x1)], MSG, sw=2.6))
    p.append(text(x0, 50, "повідомлення керує миттєвою частотою", size=12.5, color=MSG, bold=True, anchor="start"))

    # FM: інтегруємо частоту
    cy2 = 250
    p.append(line(x0, cy2, x1, cy2, color=MUTED, sw=1.0, dash="3 4"))
    p.append(text(x0 - 8, cy2 + 4, "FM", size=12, color=CAR, bold=True, anchor="end"))
    fc, dfc = 22.0, 13.0
    N = 700
    phase = 0.0
    pts = []
    xs = samp(x0, x1, N)
    dt = 1.0 / (N - 1)
    for x in xs:
        inst = fc + dfc * m(x)
        phase += 2 * math.pi * inst * dt
        pts.append((x, cy2 - 60 * math.sin(phase)))
    p.append(path(pts, CAR, sw=1.5))
    p.append(text(x0, 175, "густо = висока частота · рідко = низька · амплітуда стала", size=12, color=INK, bold=True, anchor="start"))
    # позначки густо/рідко
    p.append(text(x0 + 150, cy2 + 78, "густо", size=11, color=HOT, bold=True))
    p.append(text(x0 + 460, cy2 + 78, "рідко", size=11, color=NEG, bold=True))

    b, bw, bh = textbox(W / 2, 338, "Амплітуда нічого не несе → приймач сміливо зрізає її обмежувачем (а з нею і шум).",
                        size=12, color=INK, fill="#eef6ef", stroke=MSG, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "fm-build.svg"), W, H, *p,
           title="FM: повідомлення керує частотою, амплітуда стала")


# ── Фігура 5: AM проти FM під одним шумом ─────────────────────────────────────

def fig_noise():
    import random
    random.seed(7)
    W, H = 760, 400
    x0, x1 = 70, 700
    p = []
    noise = [(random.random() - 0.5) for _ in range(700)]
    xs = samp(x0, x1, 700)

    def m(x):
        u = (x - x0) / (x1 - x0)
        return math.sin(2 * math.pi * 1.0 * u)

    # ВЕРХ: AM + шум → тріск чутно
    cyA = 120
    p.append(text(x0, 56, "AM + шум: шум б'є по амплітуді — а звук саме в амплітуді → тріск чутно", size=12, color=HOT, bold=True, anchor="start"))
    A0 = 56
    amp = [0.5 + 0.45 * m(x) for x in xs]
    sig = []
    for i, x in enumerate(xs):
        n = 20 * noise[i]
        sig.append((x, cyA - (A0 * amp[i] * math.sin(2 * math.pi * 24 * (x - x0) / (x1 - x0)) + n)))
    p.append(path(sig, CAR, sw=1.2))
    # «вирвана» огинаюча з шумом
    env = [(x, cyA - (A0 * amp[i] + 20 * abs(noise[i]))) for i, x in enumerate(xs)]
    p.append(path(env, HOT, sw=1.6, dash="4 3"))

    # НИЗ: FM → обмежувач зрізає шум
    cyF = 300
    p.append(text(x0, 232, "FM → обмежувач зрізає амплітуду (і шум) · частота недоторкана → звук чистий", size=12, color=MSG, bold=True, anchor="start"))
    fc, dfc = 22.0, 12.0
    phase = 0.0
    dt = 1.0 / 699
    clipped = []
    for i, x in enumerate(xs):
        inst = fc + dfc * m(x)
        phase += 2 * math.pi * inst * dt
        v = math.sin(phase) + 0.35 * noise[i]
        v = max(-1.0, min(1.0, v * 3))   # «обрізання» до сталого рівня
        clipped.append((x, cyF - 52 * v))
    p.append(path(clipped, CAR, sw=1.3))
    # рамка-обмежувач
    p.append(line(x0, cyF - 52, x1, cyF - 52, color=MSG, sw=1.0, dash="2 4"))
    p.append(line(x0, cyF + 52, x1, cyF + 52, color=MSG, sw=1.0, dash="2 4"))
    p.append(text(x1, cyF - 58, "сталий «стеля/підлога»", size=10.5, color=MSG, bold=True, anchor="end"))

    b, bw, bh = textbox(W / 2, 378, "Ширша девіація Δf → глибше тоне шум: ширша смуга → тихіше (парадокс Армстронга).",
                        size=12, color=INK, bold=True, min_w=W - 120)
    p.append(b)

    render(os.path.join(OUT, "noise.svg"), W, H, *p,
           title="Під тим самим шумом: AM тріщить, FM лишається чистим")


# ── Фігура 6: смуга FM — правило Карсона ──────────────────────────────────────

def fig_fm_bandwidth():
    W, H = 760, 360
    p = []

    def gauss_band(ax, ay, df_px, peak, n, col, fill):
        # «гребінь» спектральних ліній FM у конверті завширшки ~2·df
        out = ""
        sig = df_px / 2.2
        for k in range(-n, n + 1):
            fx = ax + k * (df_px / n)
            h = peak * math.exp(-(k / (n / 1.6)) ** 2)
            if h < 4:
                continue
            out += line(fx, ay, fx, ay - h, color=col, sw=2.0)
        return out

    # ліва панель: мала девіація
    axL, ay = 190, 250
    p.append(line(60, ay, 350, ay, color=INK, sw=1.5))
    p.append(arrow(330, ay, 350, ay, color=INK, sw=1.5))
    p.append(gauss_band(axL, ay, 70, 120, 7, NEG, None))
    p.append(text(axL, 70, "мала Δf", size=12.5, color=NEG, bold=True))
    p.append(text(axL, 88, "вузько, але шумніше", size=10.5, color=MUTED))
    p.append(line(axL - 35, ay + 22, axL + 35, ay + 22, color=INK, sw=1.3))
    p.append(text(axL, ay + 40, "B", size=12, color=INK, bold=True))

    # права панель: велика девіація
    axR = 560
    p.append(line(410, ay, 700, ay, color=INK, sw=1.5))
    p.append(arrow(680, ay, 700, ay, color=INK, sw=1.5))
    p.append(gauss_band(axR, ay, 130, 120, 12, MSG, None))
    p.append(text(axR, 70, "велика Δf", size=12.5, color=MSG, bold=True))
    p.append(text(axR, 88, "широко, зате чисто", size=10.5, color=MUTED))
    p.append(line(axR - 65, ay + 22, axR + 65, ay + 22, color=INK, sw=1.3))
    p.append(text(axR, ay + 40, "B", size=12, color=INK, bold=True))

    b, bw, bh = textbox(W / 2, 330, "Правило Карсона:  B ≈ 2·(Δf + fₘ).  FM свідомо «витрачає» смугу заради тиші.",
                        size=12.5, color=INK, bold=True, min_w=480)
    p.append(b)

    render(os.path.join(OUT, "fm-bandwidth.svg"), W, H, *p,
           title="Ціна тиші — смуга: правило Карсона")


# ── Фігура 7: AM проти FM — компроміс ─────────────────────────────────────────

def fig_tradeoff():
    W, H = 760, 400
    p = []
    colA, colB = NEG, MSG
    # дві колонки-картки
    cw, ch = 320, 280
    yx = 70
    xa, xb = 40, 400
    p.append(rect(xa, yx, cw, ch, fill="#eef2fd", stroke=colA, sw=2.0, rx=10))
    p.append(rect(xb, yx, cw, ch, fill="#eef6ef", stroke=colB, sw=2.0, rx=10))
    p.append(text(xa + cw / 2, yx + 30, "AM", size=22, color=colA, bold=True))
    p.append(text(xb + cw / 2, yx + 30, "FM", size=22, color=colB, bold=True))

    rowsA = [("＋ вузька смуга (~10 кГц)", MSG),
             ("＋ найпростіший приймач", MSG),
             ("－ вразливе до шуму", HOT),
             ("－ марнує потужність на несучу", HOT),
             ("ніша: середні хвилі, авіація, КХ/SSB", MUTED)]
    rowsB = [("＋ стійке до завад, чистий звук", MSG),
             ("＋ сталий рівень — вигідний підсилювач", MSG),
             ("－ широка смуга (~200 кГц)", HOT),
             ("－ складніший приймач", HOT),
             ("ніша: FM-радіо, рації, звук ТБ", MUTED)]
    yy = yx + 68
    for (ta, ca), (tb, cb) in zip(rowsA, rowsB):
        p.append(text(xa + 18, yy, ta, size=12, color=ca, anchor="start"))
        p.append(text(xb + 18, yy, tb, size=12, color=cb, anchor="start"))
        yy += 40

    b, bw, bh = textbox(W / 2, 378, "Кращої немає — є компроміс «смуга ↔ завадостійкість».",
                        size=12.5, color=INK, bold=True, min_w=440)
    p.append(b)

    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p,
           title="AM проти FM: чесний компроміс")


if __name__ == "__main__":
    fig_am_build()
    fig_am_index()
    fig_am_sidebands()
    fig_fm_build()
    fig_noise()
    fig_fm_bandwidth()
    fig_tradeoff()
    print("OK: figures written to", OUT)
