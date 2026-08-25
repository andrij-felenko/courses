# -*- coding: utf-8 -*-
"""Фігури до статті «Реактивна потужність і коефіцієнт потужності».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREEN = FIELD      # «бере енергію»
RED   = POS        # «віддає енергію»


def poly(pts, color=INK, sw=2.0, fill="none"):
    d = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (d, fill, color, sw))


def axes(x0, y0, w, h):
    """Осі: горизонталь часу (по середині висоти) і вертикаль зліва."""
    mid = y0 + h / 2
    return (line(x0, y0 - 4, x0, y0 + h, INK, 1.4) +
            line(x0, mid, x0 + w, mid, INK, 1.4))


# ── 1. Миттєва потужність: чому реактивна частина в середньому нуль ──────────
def fig_instant_power():
    W, H = 720, 360
    x0, y0, pw, ph = 60, 50, 600, 260
    mid = y0 + ph / 2
    amp = 70
    parts = [axes(x0, y0, pw, ph)]
    N = 240
    # напруга й струм (струм зсунутий на 90° — чиста реактивність)
    u = [(x0 + pw * i / N, mid - amp * math.sin(2 * math.pi * i / N)) for i in range(N + 1)]
    cur = [(x0 + pw * i / N, mid - amp * math.sin(2 * math.pi * i / N - math.pi / 2)) for i in range(N + 1)]
    parts.append(poly(u, NEG, 2.0))
    parts.append(poly(cur, "#c98a2b", 2.0))
    # миттєва потужність p = u*i, нормована; заливка під нею (зелена>0, червона<0)
    py = []
    for i in range(N + 1):
        pval = math.sin(2 * math.pi * i / N) * math.sin(2 * math.pi * i / N - math.pi / 2)
        py.append((x0 + pw * i / N, mid - amp * 1.1 * pval))
    # площі: розіб'ємо на сегменти за знаком
    seg = []
    cur_seg = [(x0, mid)]
    sign = None
    for (x, y) in py:
        s = 1 if y < mid else -1
        if sign is None:
            sign = s
        if s != sign:
            cur_seg.append((x, mid))
            seg.append((sign, cur_seg))
            cur_seg = [(x, mid)]
            sign = s
        cur_seg.append((x, y))
    cur_seg.append((py[-1][0], mid))
    seg.append((sign, cur_seg))
    for s, pts in seg:
        col = "#d7f0df" if s == 1 else "#f7dcd8"
        d = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
        parts.append('<polygon points="%s" fill="%s" stroke="none"/>' % (d, col))
    parts.append(poly(py, INK, 2.2))
    parts.append(line(x0, mid, x0 + pw, mid, MUTED, 1.4, dash="5,4"))  # середній рівень = 0
    # підписи кривих
    parts.append(text(x0 + pw + 4, mid - amp - 4, "u", 15, NEG, "start", bold=True))
    parts.append(text(x0 + pw + 4, mid + 4, "i", 15, "#c98a2b", "start", bold=True))
    parts.append(text(x0 + 150, y0 + 12, "p = u·i", 15, INK, "middle", bold=True))
    b1, w1, h1 = textbox(x0 + 150, mid + amp + 36, "бере енергію", 12, fill="#d7f0df", stroke=GREEN, color="#1c6b35")
    b2, w2, h2 = textbox(x0 + 420, mid + amp + 36, "віддає назад", 12, fill="#f7dcd8", stroke=RED, color="#9a2b22")
    parts.append(b1); parts.append(b2)
    cap = "середнє за період = 0  →  чиста реактивність роботи не робить"
    b3, w3, h3 = textbox(W / 2, H - 18, cap, 13, fill=FILL, stroke=MUTED, color=INK, bold=True)
    parts.append(b3)
    render(os.path.join(IMG, 'instant-power.svg'), W, H, *parts,
           title="Реактивний струм: енергія гойдається, середня потужність нуль")


# ── 2. Розклад струму на активну й реактивну складові (фазори) ───────────────
def fig_current_split():
    W, H = 660, 380
    cx, cy = 150, 150
    R = 150
    parts = []
    # осі
    parts.append(line(cx - 24, cy, cx + R + 46, cy, MUTED, 1.3))
    parts.append(line(cx, cy + R + 30, cx, cy - 30, MUTED, 1.3))
    parts.append(text(cx + R + 50, cy + 4, "U", 14, NEG, "start", bold=True))
    # повний струм під кутом φ (нижче осі — відстаючий, індуктивне навантаження)
    phi = math.radians(40)
    ix, iy = cx + R * math.cos(phi), cy + R * math.sin(phi)
    px = cx + R * math.cos(phi)
    parts.append(arrow(cx, cy, ix, iy, INK, 2.6))
    # активна складова (вздовж U)
    parts.append(arrow(cx, cy, px, cy, GREEN, 2.6))
    # реактивна складова (перпендикуляр)
    parts.append(arrow(px, cy, px, iy, RED, 2.4))
    parts.append(line(px, cy, px, iy, MUTED, 1.0, dash="3,3"))
    # дуга кута φ
    parts.append('<path d="M %.1f %.1f A 40 40 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                 % (cx + 40, cy, cx + 40 * math.cos(phi), cy + 40 * math.sin(phi), INK))
    parts.append(text(cx + 54, cy + 20, "φ", 15, INK, "middle", bold=True, italic=True))
    # підписи складових — біля самих стрілок, короткі
    parts.append(text(ix + 12, iy + 6, "I", 16, INK, "start", bold=True))
    parts.append(text((cx + px) / 2, cy - 8, "I·cos φ", 12.5, "#1c6b35", "middle", bold=True))
    parts.append(text(px + 8, (cy + iy) / 2 + 4, "I·sin φ", 12.5, "#9a2b22", "start", bold=True))
    # легенда праворуч, поза діаграмою
    lx = 380
    parts.append(rect(lx, 60, 250, 44, fill="#d7f0df", stroke=GREEN, sw=1.5))
    parts.append(text(lx + 14, 80, "I·cos φ — складова в фазі з U", 12.5, "#1c6b35", "start"))
    parts.append(text(lx + 14, 97, "переносить активну потужність", 12.5, "#1c6b35", "start"))
    parts.append(rect(lx, 120, 250, 44, fill="#f7dcd8", stroke=RED, sw=1.5))
    parts.append(text(lx + 14, 140, "I·sin φ — складова під 90°", 12.5, "#9a2b22", "start"))
    parts.append(text(lx + 14, 157, "лише гойдає енергію туди-сюди", 12.5, "#9a2b22", "start"))
    cap = ("Один струм I розкладається на дві складові: вздовж напруги U і впоперек неї.\n"
           "Лише поздовжня (зелена) переносить активну потужність; поперечна (червона) — реактивна.")
    b3, w3, h3 = textbox(W / 2, H - 26, cap, 12.5, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b3)
    render(os.path.join(IMG, 'current-split.svg'), W, H, *parts,
           title="Активна й реактивна складові струму")


# ── 3. Чому реактивний струм коштує: однаковий нагрів проводу ────────────────
def fig_copper_cost():
    W, H = 700, 300
    parts = []
    # дві однакові «лінії передачі» з тим самим струмом
    def feeder(y, pf, label):
        x0 = 70
        # джерело
        parts.append(circle(x0, y, 22, fill="#eaf0fd", stroke=NEG, sw=2))
        parts.append(text(x0, y + 5, "~", 22, NEG, bold=True))
        # провід (товщина = тепло I²R, однакова)
        parts.append(line(x0 + 22, y, x0 + 320, y, "#cf8b5e", 9))
        parts.append(line(x0 + 22, y + 0, x0 + 320, y, "#cf8b5e", 9))
        # навантаження
        b, w, h = textbox(x0 + 380, y, label, 13, fill=FILL, stroke=LINE, color=INK, bold=True, min_w=140)
        parts.append(b)
        # підпис струму
        parts.append(text(x0 + 170, y - 16, "I = 10 А (однаковий!)", 13, INK, "middle", bold=True))
        # тепло
        parts.append(text(x0 + 170, y + 26, "втрати в міді I²·R = 100·R", 12.5, RED, "middle"))
    feeder(95, 1.0, "P = 2300 Вт\ncos φ = 1.0")
    feeder(210, 0.5, "P = 1150 Вт\ncos φ = 0.5")
    parts.append(line(70, 152, 630, 152, MUTED, 1.0, dash="6,5"))
    cap = "Та сама напруга 230 В, той самий струм 10 А, ті самі втрати в проводі —\nале внизу корисної потужності вдвічі менше. За що ж гріється мідь?"
    b, w, h = textbox(W / 2, H - 26, cap, 12.5, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b)
    render(os.path.join(IMG, 'copper-cost.svg'), W, H, *parts,
           title="Реактивний струм гріє провід так само, як активний")


# ── 4. Компенсація cos φ: конденсатор «гасить» реактивну Q котушки ───────────
def fig_compensation():
    W, H = 700, 430
    parts = []
    bx, by = 200, 230
    scale = 1.15
    P = 120 * scale
    Qm = 110 * scale       # індуктивна Q мотора (вниз)
    Qc = 80 * scale        # ємнісна Q компенсації (вгору)
    # до компенсації: трикутник P, Qm, Sm
    parts.append(arrow(bx, by, bx + P, by, GREEN, 2.4))                 # P
    parts.append(arrow(bx + P, by, bx + P, by + Qm, RED, 2.2))         # Qm вниз
    parts.append(line(bx, by, bx + P, by + Qm, MUTED, 1.6, dash="5,4"))  # Sm
    parts.append(text(bx + P + 8, by + Qm / 2, "Q (мотор)", 12.5, RED, "start"))
    parts.append(text((2 * bx + P) / 2, by - 8, "P", 14, GREEN, "middle", bold=True))
    parts.append(text((bx + (bx + P)) / 2 - 30, by + Qm + 18, "Sₘ — велика", 12.5, MUTED, "middle"))
    # компенсація: конденсатор тягне вгору, нова Q' = Qm - Qc
    parts.append(arrow(bx + P, by + Qm, bx + P, by + Qm - Qc, NEG, 2.2))  # Qc вгору
    parts.append(text(bx + P + 8, by + Qm - Qc / 2, "Q (конд.)", 12.5, NEG, "start"))
    Qn = Qm - Qc
    parts.append(line(bx, by, bx + P, by + Qn, INK, 2.4))               # S'
    parts.append(text((bx + (bx + P)) / 2 + 6, by + Qn - 8, "S′ — менша", 12.5, INK, "middle", bold=True))
    # маленький конденсатор-значок
    parts.append(line(bx + P + 70, by + 40, bx + P + 70, by + 70, INK, 2))
    parts.append(line(bx + P + 60, by + 70, bx + P + 80, by + 70, INK, 2.4))
    parts.append(line(bx + P + 60, by + 78, bx + P + 80, by + 78, INK, 2.4))
    parts.append(line(bx + P + 70, by + 78, bx + P + 70, by + 108, INK, 2))
    cap = ("Конденсаторна Q (вгору) віднімається від індуктивної Q мотора (вниз).\n"
           "Гіпотенуза S коротшає до S′ — менший струм із мережі за ту саму корисну P.")
    b, w, h = textbox(W / 2, H - 26, cap, 12.5, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b)
    render(os.path.join(IMG, 'compensation.svg'), W, H, *parts,
           title="Компенсація cos φ: віднімання реактивних потужностей")


# ── 5. Дві школи означення: частотна (Будяну) проти часової (Фрізе) ──────────
def fig_two_schools():
    W, H = 760, 420
    parts = []
    # спотворений струм як спільне джерело вгорі
    sx0, sy = 90, 70
    sw = 580
    mid = sy
    samp = 26
    cur = []
    for i in range(241):
        t = i / 240.0
        v = (math.sin(2 * math.pi * t)
             + 0.33 * math.sin(2 * math.pi * 3 * t)
             + 0.20 * math.sin(2 * math.pi * 5 * t))
        cur.append((sx0 + sw * t, mid - samp * v))
    parts.append(line(sx0, mid, sx0 + sw, mid, MUTED, 1.0, dash="4,4"))
    parts.append(poly(cur, "#c98a2b", 2.2))
    parts.append(text(sx0 + sw / 2, sy - 34, "один спотворений струм i(t)", 14, INK, bold=True))
    # стрілки вниз до двох колонок
    lcx, rcx = 210, 552
    parts.append(arrow(sx0 + sw / 2, sy + 32, lcx, 132, MUTED, 1.8))
    parts.append(arrow(sx0 + sw / 2, sy + 32, rcx, 132, MUTED, 1.8))

    # ── ліва колонка: Будяну — частотна область (спектр) ──
    bx, by, bw, bh = 70, 140, 280, 210
    parts.append(rect(bx, by, bw, bh, fill="#f0f4ff", stroke=NEG, sw=1.6))
    parts.append(text(bx + bw / 2, by + 24, "Будяну: частотна область", 13.5, NEG, bold=True))
    # маленькі стовпчики спектра
    spx0 = bx + 30
    base = by + 150
    bars = [(0, 60), (1, 38), (2, 22), (3, 14), (4, 9)]
    labels = ["f₁", "3f₁", "5f₁", "7f₁", "9f₁"]
    for k, (idx, hgt) in enumerate(bars):
        xx = spx0 + idx * 40
        parts.append(rect(xx, base - hgt, 22, hgt, fill="#cfd9ff", stroke=NEG, sw=1.2, rx=2))
        parts.append(text(xx + 11, base + 16, labels[k], 11, MUTED))
    parts.append(line(spx0 - 6, base, spx0 + 4 * 40 + 28, base, INK, 1.3))
    parts.append(text(bx + bw / 2, by + bh - 12,
                      "складає потужність кожної гармоніки → P, Q, D", 11.5, INK))

    # ── права колонка: Фрізе — часова область (поділ струму) ──
    fx, fy, fw, fh = 410, 140, 280, 210
    parts.append(rect(fx, fy, fw, fh, fill="#eefaf1", stroke=FIELD, sw=1.6))
    parts.append(text(fx + fw / 2, fy + 24, "Фрізе: часова область", 13.5, "#1c6b35", bold=True))
    # активний струм (форма напруги) + неактивний залишок
    axx0 = fx + 24
    axw = fw - 48
    amid = fy + 110
    aamp = 24
    act = [(axx0 + axw * i / 120.0, amid - aamp * math.sin(2 * math.pi * i / 120.0)) for i in range(121)]
    non = []
    for i in range(121):
        t = i / 120.0
        full = (math.sin(2 * math.pi * t) + 0.33 * math.sin(2 * math.pi * 3 * t)
                + 0.20 * math.sin(2 * math.pi * 5 * t))
        non.append((axx0 + axw * t, amid - aamp * (full - math.sin(2 * math.pi * t))))
    parts.append(line(axx0, amid, axx0 + axw, amid, MUTED, 1.0, dash="4,4"))
    parts.append(poly(act, FIELD, 2.2))
    parts.append(poly(non, POS, 1.8))
    parts.append(text(fx + fw / 2, fy + bh - 12,
                      "активний струм (зел.) + неактивний залишок (черв.)", 11.5, INK))
    cap = ("Активна потужність P в обох однакова — різниться поділ «неактивного»:\n"
           "Будяну рахує його по гармоніках у спектрі, Фрізе — як зайвий струм у часі.")
    b, w, h = textbox(W / 2, H - 26, cap, 12.5, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b)
    render(os.path.join(IMG, 'two-schools.svg'), W, H, *parts,
           title="Дві школи реактивної потужності: спектр проти часу")


# ── 6. Часова стрічка суперечки про реактивну потужність ─────────────────────
def fig_dispute_timeline():
    # Не пропорційна шкала років: вузли рівновіддалені (важить послідовність),
    # а великий розрив 1931→1987 позначено явним «зломом» осі.
    W, H = 760, 360
    parts = []
    x0, x1 = 90, 670
    ay = 150
    # позиції чотирьох подій (рівні слоти) + точка зламу між 3-ю і 4-ю
    xs = [150, 280, 410, 600]
    brk = 505           # де ось «зламана»
    parts.append(line(x0, ay, brk - 12, ay, INK, 2.0))
    parts.append(line(brk + 12, ay, x1, ay, INK, 2.0))
    parts.append(arrow(x1 - 2, ay, x1 + 18, ay, INK, 2.0))
    # значок зламу осі (//)
    for dx in (-12, -4):
        parts.append(line(brk + dx - 4, ay + 8, brk + dx + 6, ay - 8, INK, 1.6))
    parts.append(text(brk + 1, ay + 28, "≈ 56 років", 10.5, MUTED, italic=True))

    events = [
        ("1927", "Будяну", "означення P, Q, D\n(Фур'є, спектр)", NEG, True),
        ("1930", "вар", "IEC, Стокгольм:\nодиниця прийнята", FIELD, False),
        ("1931", "Фрізе", "поділ у часі:\nактивний / неактивний", "#7a3fb0", True),
        ("1987", "Чарнецький", "«від D слід\nвідмовитися» → CPC", POS, True),
    ]
    for k, (yr, name, desc, col, up) in enumerate(events):
        x = xs[k]
        parts.append(circle(x, ay, 6, fill=col, stroke=INK, sw=1.4))
        parts.append(text(x, ay + 26, yr, 12.5, INK, bold=True))
        if up:
            ty = ay - 96
            parts.append(line(x, ay - 6, x, ty + 30, MUTED, 1.0, dash="3,3"))
            b, w, h = textbox(x, ty + 12, name, 13, fill="#ffffff", stroke=col, color=col, bold=True, min_w=104)
            parts.append(b)
            parts.append(mtext(x, ty + 40, desc, 11, MUTED))
        else:
            ty = ay + 66
            parts.append(line(x, ay + 6, x, ty - 18, MUTED, 1.0, dash="3,3"))
            b, w, h = textbox(x, ty, name, 13, fill="#ffffff", stroke=col, color="#1c6b35", bold=True, min_w=104)
            parts.append(b)
            parts.append(mtext(x, ty + 26, desc, 11, MUTED))
    # дужка «триває донині» після 1987
    parts.append(line(xs[3] + 14, ay, x1, ay, "#b04848", 3.0, dash="6,5"))
    parts.append(text((xs[3] + x1) / 2 + 6, ay - 12, "триває", 11.5, "#b04848", bold=True, italic=True))
    cap = ("Одиницю «вар» (зелене) прийняли швидко й безповоротно. А «правильне» означення\n"
           "реактивної потужності за спотворених струмів лишається відкритим від 1927 року.")
    b, w, h = textbox(W / 2, H - 24, cap, 12, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b)
    render(os.path.join(IMG, 'dispute-timeline.svg'), W, H, *parts,
           title="Суперечка про реактивну потужність: 1927 → донині")


if __name__ == "__main__":
    fig_instant_power()
    fig_current_split()
    fig_copper_cost()
    fig_compensation()
    fig_two_schools()
    fig_dispute_timeline()
    print("OK: figures written to", IMG)
