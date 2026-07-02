# -*- coding: utf-8 -*-
"""Фігури для детальної статті «Синусоїда на осцилографі» (guide/embedded/proshyvka).
Запуск: python figs.py  →  ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GRID = "#e2e5ea"
WAVE = "#c0392b"
WAVE2 = "#2457d6"
ALIAS = "#e08030"


def grid(x, y, w, h, nx, ny):
    """Сітка осцилографа nx×ny поділок у прямокутнику (x,y,w,h)."""
    out = [rect(x, y, w, h, fill="#fbfcf7", stroke=INK, sw=2, rx=3)]
    for i in range(1, nx):
        gx = x + w * i / nx
        out.append(line(gx, y, gx, y + h, color=GRID, sw=1.1))
    for j in range(1, ny):
        gy = y + h * j / ny
        out.append(line(x, gy, x + w, gy, color=GRID, sw=1.1))
    # осьові лінії трохи темніші
    out.append(line(x, y + h / 2, x + w, y + h / 2, color="#b9bec7", sw=1.4))
    out.append(line(x + w / 2, y, x + w / 2, y + h, color="#b9bec7", sw=1.4))
    return "".join(out)


def polyline(pts, color=WAVE, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (px, py) for px, py in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (p, color, sw, d))


def fork(bx, by, up=True, color=INK):
    """Стилізований камертон: ручка в точці (bx,by), два зубці. up=True — зубці вгору."""
    d = -1 if up else 1  # напрямок зубців від ручки
    handle = 22          # довжина ручки
    span = 30            # розхил зубців
    prong = 44           # довжина зубців
    ax = bx              # вершина ручки (звідки розходяться зубці)
    ay = by + d * handle
    out = [line(bx, by, ax, ay, color=color, sw=4)]                       # ручка
    out.append(line(ax, ay, ax - span / 2, ay, color=color, sw=4))       # поперечина
    out.append(line(ax, ay, ax + span / 2, ay, color=color, sw=4))
    out.append(line(ax - span / 2, ay, ax - span / 2, ay + d * prong, color=color, sw=4))  # лівий зубець
    out.append(line(ax + span / 2, ay, ax + span / 2, ay + d * prong, color=color, sw=4))  # правий зубець
    return "".join(out)


# ── Фігура 1. Виведення RMS: середнє від sin² = 1/2 ─────────────────────────
def fig_rms():
    W, H = 900, 470
    frags = [text(W / 2, 26, "Чому RMS синуса = Vₘ/√2: середнє від sin² дорівнює ½", size=17, bold=True)]
    frags.append(text(W / 2, 48, "площа під sin²θ за період точно вдвічі менша за прямокутник висотою 1",
                      size=11, color=MUTED, italic=True))

    gx, gy, gw, gh = 70, 80, 760, 300
    x0 = gx
    x1 = gx + gw
    base = gy + gh          # y для нуля
    top = gy + gh * 0.12    # y для рівня 1.0
    amp = base - top

    frags.append(rect(gx, gy, gw, gh, fill="#fbfcf7", stroke=INK, sw=2, rx=3))
    # рівень 1.0 і рівень 0.5
    frags.append(line(x0, top, x1, top, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(text(x0 - 8, top + 4, "1", size=12, color=MUTED, anchor="end"))
    half = base - amp * 0.5
    frags.append(line(x0, half, x1, half, color=FIELD, sw=2, dash="7 5"))
    frags.append(text(x1 + 6, half + 4, "½", size=13, color=FIELD, anchor="start", bold=True))
    frags.append(text(x0 - 8, base + 4, "0", size=12, color=MUTED, anchor="end"))

    N = 240
    # sin²θ, θ від 0 до 2π
    sin2 = [(x0 + gw * i / N, base - amp * (math.sin(2 * math.pi * i / N) ** 2)) for i in range(N + 1)]
    # для контрасту — сам sin (тонко)
    sinw = [(x0 + gw * i / N, base - amp * 0.5 - amp * 0.5 * math.sin(2 * math.pi * i / N)) for i in range(N + 1)]
    frags.append(polyline(sinw, color="#c9ccd2", sw=1.6))
    frags.append(polyline(sin2, color=WAVE, sw=2.8))
    # легка заливка під sin² (площа)
    fillpts = "%.2f,%.2f " % (x0, base) + " ".join("%.2f,%.2f" % p for p in sin2) + " %.2f,%.2f" % (x1, base)
    frags.append('<polygon points="%s" fill="#c0392b" fill-opacity="0.10"/>' % fillpts)

    # мітки осі θ
    for frac, lab in [(0, "0"), (0.25, "π/2"), (0.5, "π"), (0.75, "3π/2"), (1.0, "2π")]:
        xx = x0 + gw * frac
        frags.append(line(xx, base, xx, base + 5, color=INK, sw=1.2))
        frags.append(text(xx, base + 20, lab, size=12, color=INK))

    frags.append(text(x0 + gw * 0.20, base - amp * 0.30, "sin²θ", size=14, color=WAVE, bold=True))
    frags.append(text(x0 + gw * 0.70, base - amp * 0.85, "sinθ", size=12, color="#9aa0a8"))

    box, bw, bh = textbox(W / 2, 435,
                          "⟨sin²θ⟩ = ½  →  Vᵣₘₛ = √(Vₘ²·½) = Vₘ/√2 ≈ 0.707·Vₘ",
                          size=14, bold=True, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(OUT, "rms-derivation.svg"), W, H, *frags)


# ── Фігура 2. Аліасинг: замала частота дискретизації показує фальшивий синус ─
def fig_alias():
    W, H = 900, 430
    frags = [text(W / 2, 26, "Пастка дискретизації: рідкі відліки «домальовують» фальшивий синус", size=16, bold=True)]
    frags.append(text(W / 2, 48, "справжній сигнал швидкий, а відліки рідкі — прилад покаже повільний алІас, якого немає",
                      size=11, color=MUTED, italic=True))

    gx, gy, gw, gh = 60, 74, 780, 250
    frags.append(grid(gx, gy, gw, gh, 10, 6))
    midy = gy + gh / 2
    amp = gh * 0.36

    # справжній синус — багато періодів
    ftrue = 9.0
    N = 700
    real = [(gx + gw * i / N, midy - amp * math.sin(2 * math.pi * ftrue * i / N)) for i in range(N + 1)]
    frags.append(polyline(real, color="#c9ccd2", sw=1.8))

    # відліки: трохи менше, ніж один на період -> низькочастотний алІас
    ns = 10
    samp = []
    for k in range(ns + 1):
        frac = k / ns
        sx = gx + gw * frac
        sy = midy - amp * math.sin(2 * math.pi * ftrue * frac)
        samp.append((sx, sy))
        frags.append(circle(sx, sy, 4.5, fill=ALIAS, stroke="#a85c18", sw=1.4))
    # алІас — плавна крива через відліки
    frags.append(polyline(samp, color=ALIAS, sw=2.8))

    frags.append(text(gx + 120, gy + 22, "справжній сигнал", size=12, color="#9aa0a8"))
    frags.append(text(gx + gw - 90, gy + gh - 14, "«побачений» алІас", size=12, color=ALIAS, bold=True))

    box, bw, bh = textbox(W / 2, 392,
                          "щоб форма була чесною: fдискр ≳ 10·fсигн (стеля теореми — 2·f, але для ока треба з запасом)",
                          size=12, fill="#fdf3e8", stroke=ALIAS)
    frags.append(box)
    render(os.path.join(OUT, "aliasing-trap.svg"), W, H, *frags)


# ── Фігура 3. Режим XY (Ліссажу): фаза з еліпса, sinφ = y0/A ────────────────
def fig_lissajous():
    W, H = 900, 470
    frags = [text(W / 2, 26, "Режим XY: фазу читають прямо з форми еліпса", size=17, bold=True)]
    frags.append(text(W / 2, 48, "sinφ = (перетин по вертикалі)/(повна висота) = y₀/A — без вимірювання часу",
                      size=11, color=MUTED, italic=True))

    cx, cy, R = 285, 260, 150
    # квадрат-екран
    frags.append(rect(cx - R - 20, cy - R - 20, 2 * (R + 20), 2 * (R + 20), fill="#fbfcf7", stroke=INK, sw=2, rx=3))
    frags.append(line(cx - R - 20, cy, cx + R + 20, cy, color="#b9bec7", sw=1.4))
    frags.append(line(cx, cy - R - 20, cx, cy + R + 20, color="#b9bec7", sw=1.4))

    phi = math.radians(35)
    N = 360
    ell = []
    for i in range(N + 1):
        t = 2 * math.pi * i / N
        ex = cx + R * math.sin(t)
        ey = cy - R * math.sin(t + phi)
        ell.append((ex, ey))
    frags.append(polyline(ell, color=WAVE, sw=2.8))

    # A = повна висота (макс |y|), y0 = перетин осі Y (x=0 -> sin t=0 -> t=0 -> y=-R sinφ)
    A = R
    y0 = R * math.sin(phi)
    # позначки A (повний розмах по вертикалі) справа
    axr = cx + R + 6
    frags.append(line(axr, cy - A, axr, cy + A, color=NEG, sw=2))
    frags.append(line(axr - 4, cy - A, axr + 4, cy - A, color=NEG, sw=2))
    frags.append(line(axr - 4, cy + A, axr + 4, cy + A, color=NEG, sw=2))
    frags.append(text(axr + 12, cy, "A", size=15, color=NEG, bold=True, anchor="start"))
    # y0 — перетин з віссю Y
    frags.append(circle(cx, cy - y0, 4.5, fill=FIELD, stroke="#1e7d46", sw=1.5))
    frags.append(circle(cx, cy + y0, 4.5, fill=FIELD, stroke="#1e7d46", sw=1.5))
    frags.append(line(cx + 4, cy - y0, cx + 34, cy - y0, color=FIELD, sw=1.6, dash="4 3"))
    frags.append(text(cx + 40, cy - y0 + 4, "y₀", size=14, color=FIELD, bold=True, anchor="start"))

    # права колонка — формула й випадки
    tx = 560
    frags.append(text(tx, 100, "sinφ = y₀ / A", size=18, bold=True, anchor="start", color=WAVE))
    lines = [
        "φ = 0°  → пряма лінія (/)",
        "0<φ<90° → нахилений еліпс",
        "φ = 90° → коло (y₀ = A)",
        "φ =180° → пряма лінія (\\)",
    ]
    for i, ln in enumerate(lines):
        frags.append(text(tx, 140 + i * 30, ln, size=13, anchor="start", color=INK))

    # три міні-приклади форм
    mini = [(600, 320, 0.0, "0°"), (700, 320, math.radians(45), "45°"), (800, 320, math.radians(90), "90°")]
    for mcx, mcy, mp, lab in mini:
        r = 40
        pts = []
        for i in range(121):
            t = 2 * math.pi * i / 120
            pts.append((mcx + r * math.sin(t), mcy - r * math.sin(t + mp)))
        frags.append(rect(mcx - r - 6, mcy - r - 6, 2 * (r + 6), 2 * (r + 6), fill="#fbfcf7", stroke="#c9ccd2", sw=1.2, rx=3))
        frags.append(polyline(pts, color=WAVE2, sw=2.2))
        frags.append(text(mcx, mcy + r + 24, lab, size=12, color=INK, bold=True))

    render(os.path.join(OUT, "lissajous-phase.svg"), W, H, *frags)


# ── Фігура 4. AC-зв'язок нахиляє повільний синус (sag / tilt) ───────────────
def fig_sag():
    W, H = 900, 400
    frags = [text(W / 2, 26, "AC-зв'язок і повільний синус: якщо f нижче зрізу, хвиля кривиться", size=16, bold=True)]
    frags.append(text(W / 2, 48, "конденсатор входу — фільтр верхніх частот; біля f_c він з'їдає й спотворює низьку хвилю",
                      size=11, color=MUTED, italic=True))

    # два екрани поруч
    gw, gh, gy = 350, 210, 80
    gxa, gxb = 60, 490

    # ліворуч: f >> fc — чистий синус
    frags.append(grid(gxa, gy, gw, gh, 8, 6))
    midy = gy + gh / 2
    amp = gh * 0.36
    N = 400
    good = [(gxa + gw * i / N, midy - amp * math.sin(2 * math.pi * 3 * i / N)) for i in range(N + 1)]
    frags.append(polyline(good, color=WAVE, sw=2.6))
    frags.append(text(gxa + gw / 2, gy + gh + 26, "f ≫ f_c: чистий синус", size=13, bold=True, color=INK))

    # праворуч: f ~ fc — з нахилом/спотворенням (модель highpass: похідна-домішка)
    frags.append(grid(gxb, gy, gw, gh, 8, 6))
    dist = []
    for i in range(N + 1):
        ph = 2 * math.pi * 3 * i / N
        # highpass біля зрізу: підмішуємо похідну (cos) і легкий спад — видно нахил площинок
        y = math.sin(ph) * 0.72 + math.cos(ph) * 0.5
        dist.append((gxb + gw * i / N, midy - amp * y))
    frags.append(polyline(dist, color=ALIAS, sw=2.6))
    frags.append(text(gxb + gw / 2, gy + gh + 26, "f ≲ f_c: перекіс і завал амплітуди", size=13, bold=True, color="#a85c18"))

    box, bw, bh = textbox(W / 2, 360,
                          "f_c = 1/(2π·R·C) входу (типово ~1–10 Гц). Нижче — AC-зв'язок бреше про форму й амплітуду.",
                          size=12, fill="#fdf3e8", stroke=ALIAS)
    frags.append(box)
    render(os.path.join(OUT, "ac-coupling-sag.svg"), W, H, *frags)


# ── Фігура 5 (hist). Оптичний метод Лісажу: промінь на двох камертонах ──────
def fig_hist_forks():
    W, H = 900, 470
    frags = [text(W / 2, 26, "Оптичний метод Лісажу: звук стає видимою кривою", size=17, bold=True)]
    frags.append(text(W / 2, 48, "промінь відбивається від дзеркалець на двох камертонах, що гудуть у перпендикулярних напрямках",
                      size=11, color=MUTED, italic=True))

    # Джерело світла ліворуч
    src_x, src_y = 70, 200
    frags.append(circle(src_x, src_y, 14, fill="#fff6d8", stroke="#c8a41e", sw=2))
    for a in range(0, 360, 45):
        rad = math.radians(a)
        frags.append(line(src_x + 16 * math.cos(rad), src_y + 16 * math.sin(rad),
                          src_x + 24 * math.cos(rad), src_y + 24 * math.sin(rad), color="#c8a41e", sw=1.6))
    frags.append(text(src_x, src_y + 46, "джерело", size=12, color=INK, bold=True))
    frags.append(text(src_x, src_y + 62, "світла", size=12, color=INK))

    # Камертон 1 — гойдає по горизонталі (дзеркальце А)
    m1x, m1y = 300, 200
    frags.append(fork(m1x, m1y + 70, up=True, color=NEG))
    frags.append(rect(m1x - 22, m1y - 14, 12, 28, fill="#cfe0ff", stroke=NEG, sw=2, rx=2))  # дзеркальце
    frags.append(text(m1x, m1y + 128, "камертон 1", size=12, color=NEG, bold=True))
    frags.append(text(m1x, m1y + 144, "→ гойдає по горизонталі", size=11, color=NEG))

    # Камертон 2 — гойдає по вертикалі (дзеркальце Б)
    m2x, m2y = 560, 200
    frags.append(fork(m2x, m2y - 70, up=False, color=POS))
    frags.append(rect(m2x - 6, m2y - 22, 28, 12, fill="#fdd9d3", stroke=POS, sw=2, rx=2))  # дзеркальце
    frags.append(text(m2x, m2y + 60, "камертон 2", size=12, color=POS, bold=True))
    frags.append(text(m2x, m2y + 76, "↑ гойдає по вертикалі", size=11, color=POS))

    # Промінь: джерело → дзеркальце 1 → дзеркальце 2 → екран
    beam = "#e0a020"
    frags.append(line(src_x + 22, src_y - 2, m1x - 16, m1y, color=beam, sw=2.4))
    frags.append(line(m1x - 10, m1y, m2x, m2y - 16, color=beam, sw=2.4))
    # екран праворуч
    scr_x, scr_y, scr_s = 780, 200, 130
    frags.append(line(m2x + 8, m2y - 8, scr_x - scr_s / 2, scr_y, color=beam, sw=2.4))
    frags.append(text((m1x + src_x) / 2 - 4, (src_y + m1y) / 2 - 8, "промінь", size=11, color="#a8781a", italic=True))

    # Екран із фігурою Лісажу (еліпс-вісімка як приклад)
    frags.append(rect(scr_x - scr_s / 2, scr_y - scr_s / 2, scr_s, scr_s, fill="#111418", stroke=INK, sw=2, rx=4))
    fx, fy, fr = scr_x, scr_y, scr_s * 0.36
    fig = []
    for i in range(241):
        t = 2 * math.pi * i / 240
        fig.append((fx + fr * math.sin(t), fy - fr * math.sin(2 * t)))  # 1:2 вісімка
    frags.append(polyline(fig, color="#ffe14d", sw=2.6))
    frags.append(text(scr_x, scr_y + scr_s / 2 + 22, "екран: світна крива", size=12, color=INK, bold=True))

    box, bw, bh = textbox(W / 2, 440,
                          "інерція зору зливає біг зайчика в суцільну фігуру; форму задають відношення частот і різниця фаз",
                          size=12, fill=FILL, stroke=MUTED)
    frags.append(box)
    render(os.path.join(OUT, "lissajous-forks.svg"), W, H, *frags)


# ── Фігура 6 (hist). Нерухома проти рухомої фігури: рівність частот ──────────
def fig_hist_lock():
    W, H = 900, 430
    frags = [text(W / 2, 26, "Нерухома фігура = точна рівність частот", size=17, bold=True)]
    frags.append(text(W / 2, 48, "рівні частоти дають застиглу криву; найменша розбіжність — повільне обертання",
                      size=11, color=MUTED, italic=True))

    box_s = 210
    ya = 80
    # ── Ліворуч: рівні частоти, застигла фігура ──
    lx = 210
    frags.append(rect(lx - box_s / 2, ya, box_s, box_s, fill="#111418", stroke=INK, sw=2, rx=4))
    cx, cy, r = lx, ya + box_s / 2, box_s * 0.34
    ell = []
    phi = math.radians(50)
    for i in range(241):
        t = 2 * math.pi * i / 240
        ell.append((cx + r * math.sin(t), cy - r * math.sin(t + phi)))
    frags.append(polyline(ell, color="#ffe14d", sw=3.0))
    frags.append(text(lx, ya + box_s + 26, "f₁ = f₂ (1:1)", size=14, color=FIELD, bold=True))
    frags.append(text(lx, ya + box_s + 46, "фігура застигла — фаза стоїть", size=11, color=INK))

    # ── Праворуч: одна частота більша, фігура повзе (кілька положень) ──
    rx = 660
    frags.append(rect(rx - box_s / 2, ya, box_s, box_s, fill="#111418", stroke=INK, sw=2, rx=4))
    cx2, cy2 = rx, ya + box_s / 2
    fades = ["#4a4520", "#7a7030", "#b09a3a", "#ffe14d"]
    for k, ph0 in enumerate([0.0, math.radians(40), math.radians(80), math.radians(120)]):
        pts = []
        for i in range(241):
            t = 2 * math.pi * i / 240
            pts.append((cx2 + r * math.sin(t), cy2 - r * math.sin(t + ph0)))
        frags.append(polyline(pts, color=fades[k], sw=2.2 if k < 3 else 3.0))
    # стрілка обертання
    frags.append(arrow(cx2 + r + 16, cy2 - 6, cx2 + r + 16, cy2 + 20, color=POS, sw=2))
    frags.append(text(rx, ya + box_s + 26, "f₁ ≠ f₂ (трохи більша)", size=14, color=POS, bold=True))
    frags.append(text(rx, ya + box_s + 46, "фаза втікає — фігура обертається", size=11, color=INK))

    box, bw, bh = textbox(W / 2, 405,
                          "швидкість обертання = різниця частот; завмерла фігура означає точний збіг",
                          size=12, bold=True, fill="#eef7f0", stroke=FIELD)
    frags.append(box)
    render(os.path.join(OUT, "lissajous-lock.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_rms()
    fig_alias()
    fig_lissajous()
    fig_sag()
    fig_hist_forks()
    fig_hist_lock()
    print("done:", os.listdir(OUT))
