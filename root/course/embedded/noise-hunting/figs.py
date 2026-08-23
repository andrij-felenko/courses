# -*- coding: utf-8 -*-
"""Фігури до детальної статті «Полювання на заваду».
Три фігури, кожна несе вагу:
  1. probe-ring   — земляний хвіст щупа як LC: довгий «крокодил» дзвонить, коротка пружина відсуває дзвін за смугу.
  2. spectrum     — ті самі завади у частотній області: гребінь гармонік мережі, лінія ключа БЖ, піднятий шумовий поріг.
  3. avg-modes    — некогерентне усереднення (√N глушить траву, гул виживає) проти синхронного (виловлює періодику).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SCOPE_BG = "#0d1f17"
SCOPE_GRID = "#143b2b"
SCOPE_AXIS = "#1f5740"
TRACE = "#ffd9b3"
TRACE2 = "#8fd4ff"


def scope_screen(x, y, w, h, cols=10, rows=8):
    """Тло екрана осцилографа з сіткою. Повертає (svg, функції x/y-мапінгу)."""
    out = [rect(x, y, w, h, fill=SCOPE_BG, stroke=INK, sw=1.8, rx=8)]
    for i in range(1, cols):
        gx = x + w * i / cols
        out.append(line(gx, y + 6, gx, y + h - 6, color=SCOPE_GRID, sw=1))
    for j in range(1, rows):
        gy = y + h * j / rows
        out.append(line(x + 6, gy, x + w - 6, gy, color=SCOPE_GRID, sw=1))
    # осьова лінія
    out.append(line(x + 6, y + h / 2, x + w - 6, y + h / 2, color=SCOPE_AXIS, sw=1.3))
    return "".join(out)


def polyline(pts, color=TRACE, sw=2.0):
    s = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (s, color, sw)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Земляний хвіст щупа = LC-контур: довгий крокодил дзвонить, коротка пружина — ні
# ─────────────────────────────────────────────────────────────────────────────
def fig_probe_ring():
    W, H = 980, 560
    parts = [text(W / 2, 30, "Земляний хвіст щупа — це котушка: довгий «крокодил» дзвонить", size=18, bold=True)]
    parts.append(text(W / 2, 52, "L хвоста + C наконечника = послідовний контур; він резонує на f = 1 / (2π·√(L·C))",
                      size=11.5, color=MUTED, italic=True))

    # ── ліворуч угорі: схема щупа з довгим хвостом ──
    sx, sy = 40, 78
    parts.append(text(sx + 150, sy + 8, "довгий земляний хвіст (≈15 см)", size=12, bold=True, color=INK))
    # наконечник до вузла
    tipx, tipy = sx + 40, sy + 60
    nodex, nodey = sx + 150, sy + 60
    parts.append(line(tipx, tipy, nodex, nodey, color=INK, sw=2.2))
    parts.append(circle(tipx, tipy, 5, fill=POS, stroke=INK, sw=1.5))
    parts.append(text(tipx, tipy - 12, "вістря", size=10, color=MUTED))
    parts.append(circle(nodex, nodey, 4, fill=INK, stroke=INK))
    # C наконечника вниз до землі щупа
    parts.append(line(nodex, nodey, nodex, nodey + 40, color=INK, sw=2))
    parts.append(line(nodex - 14, nodey + 40, nodex + 14, nodey + 40, color=INK, sw=2.4))
    parts.append(line(nodex - 10, nodey + 46, nodex + 10, nodey + 46, color=INK, sw=2.4))
    parts.append(text(nodex + 34, nodey + 46, "C ≈ 15 пФ", size=10.5, color=NEG, anchor="middle"))
    # земляний хвіст як котушка (зигзаг) від вузла праворуч і вниз
    coilx = nodex + 60
    parts.append(line(nodex, nodey + 66, coilx - 30, nodey + 66, color=INK, sw=2))
    # зигзаг-котушка
    zz = "M %.0f %.0f" % (coilx - 30, nodey + 66)
    step = 12
    for k in range(6):
        zz += " l %d -10 l %d 20 l %d -10" % (step / 2, 0, step / 2)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (zz, POS))
    endx = coilx - 30 + 6 * step
    parts.append(text(coilx + 24, nodey + 50, "L ≈ 150 нГн", size=10.5, color=POS))
    parts.append(line(endx, nodey + 66, endx, nodey + 90, color=INK, sw=2))
    # земля
    for i, wln in enumerate([16, 10, 5]):
        parts.append(line(endx - wln, nodey + 90 + i * 5, endx + wln, nodey + 90 + i * 5, color=INK, sw=2))
    parts.append(text(tipx + 6, nodey + 118, "земля точки виміру", size=10, color=MUTED, anchor="start"))

    # екран праворуч угорі: дзвін
    ex, ey, ew, eh = 470, 70, 470, 200
    parts.append(scope_screen(ex, ey, ew, eh))
    parts.append(text(ex + ew / 2, ey - 8, "фронт наводить ДЗВІН на ≈106 МГц", size=12, bold=True, color=INK))
    # ідеальна сходинка (сіра пунктирна) + дзвін
    base = ey + eh * 0.68
    top = ey + eh * 0.30
    stepx = ex + ew * 0.30
    ideal = [(ex + 8, base)] + [(stepx, base), (stepx, top), (ex + ew - 8, top)]
    parts.append(polyline(ideal, color="#6f8f80", sw=1.6))
    # дзвін: згасаючий синус після фронту
    ring = [(ex + 8, base)]
    N = 240
    for i in range(N):
        t = i / (N - 1)
        px = ex + 8 + t * (ew - 16)
        if px < stepx:
            py = base
        else:
            u = (px - stepx) / (ex + ew - 8 - stepx)
            env = math.exp(-u * 7)
            py = top - (base - top) * 0.55 * env * math.cos(u * 38)
        ring.append((px, py))
    parts.append(polyline(ring, color=TRACE, sw=2.2))
    parts.append(text(ex + ew * 0.62, ey + eh * 0.20, "паразитний дзвін", size=10.5, color=TRACE, anchor="middle"))

    # ── ліворуч унизу: коротка пружина ──
    sy2 = 330
    parts.append(text(sx + 150, sy2 + 8, "коротка пружина-контакт (≈1.5 см)", size=12, bold=True, color=INK))
    tipx2, tipy2 = sx + 40, sy2 + 60
    nodex2 = sx + 150
    parts.append(line(tipx2, tipy2, nodex2, tipy2, color=INK, sw=2.2))
    parts.append(circle(tipx2, tipy2, 5, fill=POS, stroke=INK, sw=1.5))
    parts.append(circle(nodex2, tipy2, 4, fill=INK, stroke=INK))
    parts.append(line(nodex2, tipy2, nodex2, tipy2 + 40, color=INK, sw=2))
    parts.append(line(nodex2 - 14, tipy2 + 40, nodex2 + 14, tipy2 + 40, color=INK, sw=2.4))
    parts.append(line(nodex2 - 10, tipy2 + 46, nodex2 + 10, tipy2 + 46, color=INK, sw=2.4))
    parts.append(text(nodex2 + 34, tipy2 + 46, "C ≈ 15 пФ", size=10.5, color=NEG, anchor="middle"))
    # маленька котушка
    coilx2 = nodex2 + 40
    parts.append(line(nodex2, tipy2 + 66, coilx2 - 14, tipy2 + 66, color=INK, sw=2))
    zz2 = "M %.0f %.0f" % (coilx2 - 14, tipy2 + 66)
    for k in range(3):
        zz2 += " l 4 -8 l 4 16 l 4 -8"
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (zz2, FIELD))
    endx2 = coilx2 - 14 + 3 * 12
    parts.append(text(coilx2 + 30, tipy2 + 50, "L ≈ 15 нГн", size=10.5, color=FIELD))
    parts.append(line(endx2, tipy2 + 66, endx2, tipy2 + 88, color=INK, sw=2))
    for i, wln in enumerate([16, 10, 5]):
        parts.append(line(endx2 - wln, tipy2 + 88 + i * 5, endx2 + wln, tipy2 + 88 + i * 5, color=INK, sw=2))

    # екран праворуч унизу: чистий фронт
    ex2, ey2 = 470, 322
    parts.append(scope_screen(ex2, ey2, ew, eh))
    parts.append(text(ex2 + ew / 2, ey2 - 8, "дзвін відсунуто на ≈335 МГц — за смугу, екран чистий", size=12, bold=True, color=INK))
    base2 = ey2 + eh * 0.68
    top2 = ey2 + eh * 0.30
    stepx2 = ex2 + ew * 0.30
    clean = [(ex2 + 8, base2), (stepx2, base2)]
    Nc = 60
    for i in range(Nc):
        u = i / (Nc - 1)
        px = stepx2 + u * (ex2 + ew - 8 - stepx2)
        env = math.exp(-u * 26)
        py = top2 - (base2 - top2) * 0.10 * env * math.cos(u * 30)
        clean.append((px, py))
    parts.append(polyline(clean, color=TRACE, sw=2.2))
    parts.append(text(ex2 + ew * 0.6, ey2 + eh * 0.20, "майже ідеальний фронт", size=10.5, color=TRACE, anchor="middle"))

    # нижній підпис-висновок
    body, bw, bh = textbox(W / 2, 540, "Коротший хвіст → менше L → вища f резонансу. Пружина заганяє дзвін ЗА смугу приладу — його просто не видно.",
                           size=11.5, pad=10, fill="#eef6f1", stroke=FIELD, color=INK)
    parts.append(body)

    render(os.path.join(OUT, 'probe-ring.svg'), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Ті самі завади у частотній області (FFT): відбиток у спектрі
# ─────────────────────────────────────────────────────────────────────────────
def fig_spectrum():
    W, H = 980, 470
    parts = [text(W / 2, 30, "Той самий «бруд» у частотній області: спектр видає джерело ще чіткіше", size=18, bold=True)]
    parts.append(text(W / 2, 52, "у часі три завади плутаються; у спектрі кожна дає свій упізнаваний малюнок ліній",
                      size=11.5, color=MUTED, italic=True))

    # три спектральні панелі поряд
    pw, ph = 290, 320
    gap = 24
    x0 = (W - 3 * pw - 2 * gap) / 2
    y0 = 80
    labels = [
        ("Гул мережі", "гребінь: 50 Гц і її гармоніки\n(100, 150, 200 …)", TRACE),
        ("Ключ БЖ", "вузька лінія на f_кл (≈100 кГц)\n+ її гармоніки", TRACE2),
        ("Широкосмуговий шум", "рівно піднятий шумовий\nпоріг, без ліній", "#c9f0d6"),
    ]

    def panel(px, kind):
        out = [rect(px, y0, pw, ph, fill=SCOPE_BG, stroke=INK, sw=1.6, rx=6)]
        # осі
        ax0, ay0 = px + 34, y0 + ph - 34
        axw = pw - 48
        axh = ph - 60
        out.append(line(ax0, ay0, ax0 + axw, ay0, color=SCOPE_AXIS, sw=1.4))  # X
        out.append(line(ax0, ay0, ax0, ay0 - axh, color=SCOPE_AXIS, sw=1.4))  # Y
        out.append(text(ax0 + axw / 2, y0 + ph - 8, "частота →", size=10, color=MUTED))
        out.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">амплітуда</text>'
                   % (px + 12, y0 + ph / 2, FONT, MUTED, px + 12, y0 + ph / 2))
        # шумовий поріг (базова трава)
        import random
        random.seed(kind)
        floor_h = 8 if kind < 2 else 30
        fl = []
        for i in range(axw):
            fl.append((ax0 + i, ay0 - floor_h * (0.4 + 0.6 * random.random()) if False else ay0 - (floor_h * (0.35 + 0.5 * random.random()))))
        out.append(polyline(fl, color="#3c6d55", sw=1.0))
        col = labels[kind][2]
        if kind == 0:
            # гребінь гармонік 50 Гц
            for h in range(1, 8):
                bx = ax0 + axw * (h / 8.2)
                amp = axh * (0.8 / h)  # спад із номером гармоніки
                out.append(line(bx, ay0, bx, ay0 - amp, color=col, sw=3))
                if h == 1:
                    out.append(text(bx, ay0 - amp - 8, "50", size=9.5, color=col))
                elif h == 2:
                    out.append(text(bx, ay0 - amp - 8, "100", size=9.5, color=col))
        elif kind == 1:
            # одна висока лінія + кілька гармонік десь у ВЧ
            for h, frac in enumerate([0.5, 0.75, 0.92]):
                bx = ax0 + axw * frac
                amp = axh * (0.85 if h == 0 else 0.4 / (h + 1))
                out.append(line(bx, ay0, bx, ay0 - amp, color=col, sw=3))
                if h == 0:
                    out.append(text(bx, ay0 - amp - 8, "f_кл", size=9.5, color=col))
        else:
            # лише піднятий поріг, без ліній — уже намальовано вище (floor_h=30)
            out.append(text(ax0 + axw / 2, ay0 - floor_h - 12, "немає ліній", size=10, color=col))
        return "".join(out)

    for i in range(3):
        px = x0 + i * (pw + gap)
        parts.append(panel(px, i))
        parts.append(text(px + pw / 2, y0 - 8, labels[i][0], size=12.5, bold=True, color=INK))
        cap = labels[i][1]
        body, bw, bh = textbox(px + pw / 2, y0 + ph + 30, cap, size=10.5, pad=8,
                               fill="#eef6f1", stroke=MUTED, color=INK)
        parts.append(body)

    render(os.path.join(OUT, 'spectrum.svg'), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Некогерентне усереднення проти синхронного
# ─────────────────────────────────────────────────────────────────────────────
def fig_avg_modes():
    W, H = 980, 500
    parts = [text(W / 2, 30, "Усереднення: некогерентне глушить траву, але гул виживає", size=18, bold=True)]
    parts.append(text(W / 2, 52, "випадкове гаситься як 1/√N; періодичне повторюється від разу до разу й НЕ гасить себе",
                      size=11.5, color=MUTED, italic=True))

    ew, eh = 430, 180

    # ── верхня пара: некогерентне усереднення (вхід — сигнал + трава + гул) ──
    # ліворуч: одна розгортка
    ex, ey = 40, 80
    parts.append(scope_screen(ex, ey, ew, eh))
    parts.append(text(ex + ew / 2, ey - 8, "1 розгортка: сигнал у траві + гул", size=12, bold=True))
    import random
    random.seed(7)
    mid = ey + eh / 2

    def signal(px_frac):
        # корисний вузький імпульс посередині
        c = 0.5
        return -eh * 0.30 * math.exp(-((px_frac - c) * 14) ** 2)

    def hum(px_frac, phase=0.0):
        return eh * 0.16 * math.sin(px_frac * 2 * math.pi * 2 + phase)

    one = []
    for i in range(ew - 16):
        f = i / (ew - 16)
        px = ex + 8 + i
        py = mid + signal(f) + hum(f) + (random.random() - 0.5) * eh * 0.5
        one.append((px, py))
    parts.append(polyline(one, color=TRACE, sw=1.4))

    # праворуч: некогерентно усереднено N=64 -> трава впала, гул лишився
    ex2 = 510
    parts.append(scope_screen(ex2, ey, ew, eh))
    parts.append(text(ex2 + ew / 2, ey - 8, "некогерентно ×64: трава впала, ГУЛ лишився", size=12, bold=True))
    avg = []
    for i in range(ew - 16):
        f = i / (ew - 16)
        px = ex2 + 8 + i
        # трава ÷8, гул із випадковою фазою кожної розгортки частково гаситься, але не зникає
        py = mid + signal(f) + hum(f) * 0.75 + (random.random() - 0.5) * eh * 0.5 / 8
        avg.append((px, py))
    parts.append(polyline(avg, color=TRACE, sw=2.0))
    parts.append(text(ex2 + ew * 0.5, ey + eh * 0.86, "залишковий гул 50 Гц", size=10.5, color="#ff9c9c"))

    # ── нижня пара: синхронне усереднення по тригеру, прив'язаному до гулу ──
    ey2 = 300
    ex3 = 40
    parts.append(scope_screen(ex3, ey2, ew, eh))
    parts.append(text(ex3 + ew / 2, ey2 - 8, "тригер прив'язано до 50 Гц → гул СТОЇТЬ", size=12, bold=True))
    mid2 = ey2 + eh / 2
    lock = []
    for i in range(ew - 16):
        f = i / (ew - 16)
        px = ex3 + 8 + i
        py = mid2 + hum(f) * 1.0 + (random.random() - 0.5) * eh * 0.5
        lock.append((px, py))
    parts.append(polyline(lock, color=TRACE, sw=1.4))

    ex4 = 510
    parts.append(scope_screen(ex4, ey2, ew, eh))
    parts.append(text(ex4 + ew / 2, ey2 - 8, "синхронно ×64: виловлено САМ гул (форму завади)", size=12, bold=True))
    ext = []
    for i in range(ew - 16):
        f = i / (ew - 16)
        px = ex4 + 8 + i
        py = mid2 + hum(f) * 1.0 + (random.random() - 0.5) * eh * 0.5 / 8
        ext.append((px, py))
    parts.append(polyline(ext, color=TRACE2, sw=2.2))
    parts.append(text(ex4 + ew * 0.5, ey2 + eh * 0.16, "чиста форма гулу", size=10.5, color=TRACE2))

    body, bw, bh = textbox(W / 2, 484, "Той самий інструмент, дві мети: за тригером сигналу — глушимо періодику як шум; за тригером самої завади — навпаки, витягуємо її форму.",
                           size=11.5, pad=10, fill="#eef6f1", stroke=FIELD, color=INK)
    parts.append(body)

    render(os.path.join(OUT, 'avg-modes.svg'), W, H, *parts)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Та сама частота, різна добротність: огинальна exp(−t/τ), число коливань ≈ Q/π
#    (для вставки math-probe-resonance.md — глибша математика контуру)
# ─────────────────────────────────────────────────────────────────────────────
def fig_probe_q_decay():
    W, H = 980, 560
    parts = [text(W / 2, 30, "Та сама частота f₀ — різна добротність Q: як довго тягнеться дзвін", size=18, bold=True)]
    parts.append(text(W / 2, 52, "огинальна exp(−t∕τ), τ = 2Q∕ω₀ ;  видимих коливань ≈ Q∕π",
                      size=11.5, color=MUTED, italic=True))

    # три панелі-екрани поряд: Q високий / середній / критичний
    pw, ph = 296, 300
    gap = 22
    x0 = (W - 3 * pw - 2 * gap) / 2
    y0 = 82
    cases = [
        ("високий Q = 10", 10.0, "≈ 3 коливання (Q∕π)", TRACE),
        ("малий Q ≈ 3", 3.16, "≈ 1 коливання", TRACE2),
        ("критичний Q = ½", 0.5, "коливань нема", "#c9f0d6"),
    ]

    cycles = 4.5           # скільки періодів синуса вкладаємо в екран
    for k, (title, Q, note, col) in enumerate(cases):
        px = x0 + k * (pw + gap)
        parts.append(scope_screen(px, y0, pw, ph, cols=8, rows=6))
        parts.append(text(px + pw / 2, y0 - 8, title, size=12.5, bold=True, color=INK))
        mid = y0 + ph / 2
        amp = ph * 0.36
        left = px + 10
        span = pw - 20
        # огинальна: за час усього екрана (cycles періодів) фаза йде до 2π·cycles,
        # тобто ω₀·t = 2π·cycles·u; τ у тих самих одиницях: exp(−t/τ)=exp(−ω₀t/(2Q))
        env_up, env_lo, wave = [], [], []
        N = 300
        for i in range(N):
            u = i / (N - 1)
            phase = 2 * math.pi * cycles * u          # ω₀·t
            env = math.exp(-phase / (2 * Q))          # exp(−t/τ), τ=2Q/ω₀
            x = left + u * span
            if Q >= 0.5001:
                y = mid - amp * env * math.cos(phase)
            else:
                # критичне згасання: чистий спад без коливань (a·e^{−ω₀t})
                y = mid - amp * math.exp(-phase)
            wave.append((x, y))
            env_up.append((x, mid - amp * env))
            env_lo.append((x, mid + amp * env))
        # огинальні (пунктир) — лише для коливальних випадків
        if Q >= 0.5001:
            parts.append(polyline(env_up, color="#7fa89a", sw=1.3))
            parts.append(polyline(env_lo, color="#7fa89a", sw=1.3))
        parts.append(polyline(wave, color=col, sw=2.2))
        # мітка τ на верхній огинальній: точка, де env = 1/e
        if Q >= 0.5001:
            ut = (2 * Q) / (2 * math.pi * cycles)     # u, при якому phase/(2Q)=1
            if ut < 1.0:
                xt = left + ut * span
                yt = mid - amp * math.exp(-1)
                parts.append(line(xt, mid, xt, y0 + ph - 12, color="#e8b04b", sw=1.2, dash="4,3"))
                parts.append(text(xt, y0 + ph - 16, "τ", size=12, bold=True, color="#e8b04b"))
        parts.append(text(px + pw / 2, y0 + ph - 34, note, size=10.5, color=col))

    body, bw, bh = textbox(W / 2, 522,
                           "Частота однакова — гойдається однаково швидко. Різниця лише в Q: він задає, як круто падає\nогинальна exp(−t∕τ) і скільки коливань устигне дзвін (≈ Q∕π). Опір втрат ↑ → Q ↓ → дзвін в'яне швидше.",
                           size=11.5, pad=10, fill="#eef6f1", stroke=FIELD, color=INK)
    parts.append(body)

    render(os.path.join(OUT, 'probe-q-decay.svg'), W, H, *parts)


if __name__ == "__main__":
    fig_probe_ring()
    fig_spectrum()
    fig_avg_modes()
    fig_probe_q_decay()
    print("done")
