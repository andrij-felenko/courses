# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Блок-схема контуру PLL ────────────────────────────────────────────────
def fig_loop():
    W, H = 820, 330
    f = []
    y = 130
    # три блоки в ряд
    bx = [70, 305, 540]
    bw = 150
    labels = [
        ("Фазовий\nдетектор", "порівнює фази", NEG),
        ("Фільтр\nконтуру", "згладжує похибку", FIELD),
        ("Керований\nгенератор (ГКН)", "крутить частоту", POS),
    ]
    for i, (lab, sub, col) in enumerate(labels):
        f.append(fitbox(bx[i], y - 34, bw, 68, lab, size=15, bold=True,
                        stroke=col, sw=2.2, fill="#ffffff"))
        f.append(text(bx[i] + bw / 2, y + 56, sub, size=12, color=MUTED, italic=True))

    # вхід опорного сигналу
    f.append(text(40, y - 12, "опора", size=13, color=INK, anchor="end"))
    f.append(text(40, y + 8, "f_оп", size=12, color=MUTED, anchor="end"))
    f.append(arrow(44, y, bx[0], y, color=INK, sw=2.2))

    # між блоками
    f.append(text((bx[0] + bw + bx[1]) / 2, y - 10, "похибка", size=11, color=MUTED))
    f.append(arrow(bx[0] + bw, y, bx[1], y, color=INK, sw=2.2))
    f.append(text((bx[1] + bw + bx[2]) / 2, y - 10, "напруга", size=11, color=MUTED))
    f.append(arrow(bx[1] + bw, y, bx[2], y, color=INK, sw=2.2))

    # вихід
    outx = bx[2] + bw
    f.append(arrow(outx, y, outx + 90, y, color=INK, sw=2.2))
    f.append(text(outx + 96, y - 12, "вихід", size=13, color=INK, anchor="start"))
    f.append(text(outx + 96, y + 8, "f_вих", size=12, color=MUTED, anchor="start"))

    # зворотний зв'язок: від виходу вниз і назад до детектора
    fy = y + 110
    f.append(line(outx + 40, y, outx + 40, fy, color=POS, sw=2.2))
    f.append(line(outx + 40, fy, bx[0] + bw / 2, fy, color=POS, sw=2.2))
    f.append(arrow(bx[0] + bw / 2, fy, bx[0] + bw / 2, y + 34, color=POS, sw=2.2))
    f.append(text((outx + 40 + bx[0] + bw / 2) / 2, fy + 18,
                  "зворотний зв'язок: вихід порівнюється з опорою", size=12,
                  color=POS, italic=True))

    render(os.path.join(IMG, "pll-loop.svg"), W, H, *f,
           title="Контур фазового автопідстроювання")


# ── 2. Фазовий детектор: вихід росте з різницею фаз ──────────────────────────
def fig_phase_detector():
    W, H = 720, 360
    f = []
    # ліва панель: дві синусоїди майже у фазі -> мала похибка
    # права панель: зсунуті -> велика похибка
    def panel(ox, dphi, lab):
        cx0, w = ox, 250
        y0 = 130
        amp = 38
        f.append(text(cx0 + w / 2, 56, lab, size=14, bold=True))
        # осі
        f.append(line(cx0, y0, cx0 + w, y0, color=MUTED, sw=1.2))
        # дві хвилі
        def wave(phi, col, dash=None):
            pts = []
            for k in range(0, w + 1, 4):
                t = k / w * 2 * math.pi * 2
                yy = y0 - amp * math.sin(t + phi)
                pts.append("%.1f,%.1f" % (cx0 + k, yy))
            return ('<polyline points="%s" fill="none" stroke="%s" '
                    'stroke-width="2.4"%s/>' % (" ".join(pts),
                    col, ' stroke-dasharray="6 4"' if dash else ''))
        f.append(wave(0, NEG))
        f.append(wave(dphi, POS, dash=True))
        # стовпчик «середній вихід»
        bar_h = abs(dphi) / math.pi * 70
        bxx = cx0 + w / 2 - 22
        byy = y0 + 70
        f.append(rect(bxx, byy + (70 - bar_h), 44, bar_h,
                      fill="#fdecea", stroke=POS, sw=2, rx=4))
        f.append(text(cx0 + w / 2, byy + 92, "середній\nвихід детектора".split("\n")[0],
                      size=11, color=MUTED))
        f.append(text(cx0 + w / 2, byy + 106, "вихід детектора", size=11, color=MUTED))
    panel(50, 0.35, "Майже у фазі → мала похибка")
    panel(420, 1.7, "Розійшлись → велика похибка")
    # легенда
    f.append(line(250, 330, 280, 330, color=NEG, sw=2.4))
    f.append(text(286, 334, "опора", size=12, color=INK, anchor="start"))
    f.append(line(360, 330, 390, 330, color=POS, sw=2.4, dash="6 4"))
    f.append(text(396, 334, "генератор", size=12, color=INK, anchor="start"))
    render(os.path.join(IMG, "phase-detector.svg"), W, H, *f,
           title="Чим далі фази розійшлись, тим більша похибка")


# ── 3. Захоплення і втримання: частота генератора доганяє опору ──────────────
def fig_lock():
    W, H = 720, 340
    f = []
    ox, oy, w, h = 70, 70, 600, 200
    # осі
    f.append(arrow(ox, oy + h, ox + w + 14, oy + h, color=INK, sw=1.6))
    f.append(arrow(ox, oy + h, ox, oy - 10, color=INK, sw=1.6))
    f.append(text(ox + w, oy + h + 24, "час", size=13, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - 4, "частота", size=13, color=INK, anchor="end"))

    # цільова частота (опора) — горизонталь
    yt = oy + 50
    f.append(line(ox, yt, ox + w, yt, color=NEG, sw=2.0, dash="7 5"))
    f.append(text(ox + w + 2, yt - 6, "f опори", size=12, color=NEG, anchor="end"))

    # крива генератора: старт нижче, перехід із загасаючим перельотом до yt
    y_start = oy + h - 20
    pts = []
    for k in range(0, w + 1, 3):
        x = k / w
        # експоненційне наближення з невеликим перельотом
        env = math.exp(-3.2 * x)
        over = math.sin(7 * x) * env * 0.12
        val = 1 - (1 - 0.0) * env + over   # 0..~1
        yy = y_start + (yt - y_start) * val
        pts.append("%.1f,%.1f" % (ox + k, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))
    f.append(text(ox + 8, y_start + 4, "f генератора", size=12, color=POS, anchor="start"))

    # фази: «захоплення» і «втримання»
    xcap = ox + w * 0.42
    f.append(line(xcap, oy - 6, xcap, oy + h, color=MUTED, sw=1.0, dash="3 4"))
    bcap, _, _ = textbox((ox + xcap) / 2, oy + 12, "захоплення", size=12,
                         color=INK, stroke=MUTED, sw=1.2, fill="#f4f6f8")
    f.append(bcap)
    bhold, _, _ = textbox((xcap + ox + w) / 2, oy + 12, "втримання (синхронізм)",
                          size=12, color=INK, stroke=FIELD, sw=1.6, fill="#eafaf0")
    f.append(bhold)
    render(os.path.join(IMG, "lock-capture.svg"), W, H, *f,
           title="Як контур ловить і тримає частоту")


# ── 4. Синтез частоти: дільник у зворотному зв'язку ─────────────────────────
def fig_synth():
    W, H = 740, 320
    f = []
    y = 120
    bx = [60, 285, 510]
    bw = 150
    labels = [
        ("Фазовий\nдетектор", NEG),
        ("Фільтр\nконтуру", FIELD),
        ("ГКН", POS),
    ]
    for i, (lab, col) in enumerate(labels):
        f.append(fitbox(bx[i], y - 30, bw, 60, lab, size=15, bold=True,
                        stroke=col, sw=2.2, fill="#ffffff"))
    f.append(text(36, y - 4, "f_оп", size=13, color=INK, anchor="end"))
    f.append(arrow(40, y, bx[0], y, color=INK, sw=2.2))
    f.append(arrow(bx[0] + bw, y, bx[1], y, color=INK, sw=2.2))
    f.append(arrow(bx[1] + bw, y, bx[2], y, color=INK, sw=2.2))
    outx = bx[2] + bw
    f.append(arrow(outx, y, outx + 70, y, color=INK, sw=2.2))
    f.append(text(outx + 76, y - 4, "f_вих = N·f_оп", size=13, color=INK, anchor="start", bold=True))

    # дільник ÷N у зворотному зв'язку
    fy = y + 120
    dx = (bx[0] + bw / 2 + outx + 35) / 2
    f.append(line(outx + 35, y, outx + 35, fy, color=POS, sw=2.2))
    f.append(line(outx + 35, fy, dx + 45, fy, color=POS, sw=2.2))
    db, dw, dh = textbox(dx, fy, "Дільник ÷ N", size=15, bold=True,
                         stroke=POS, sw=2.2, fill="#fdecea")
    f.append(db)
    f.append(line(dx - 45, fy, bx[0] + bw / 2, fy, color=POS, sw=2.2))
    f.append(arrow(bx[0] + bw / 2, fy, bx[0] + bw / 2, y + 30, color=POS, sw=2.2))
    f.append(text(dx, fy + dh / 2 + 22,
                  "детектор бачить f_вих/N — і жене її до f_оп; отже f_вих = N·f_оп",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "synth-divider.svg"), W, H, *f,
           title="Дільник у контурі множить частоту")


# ── 5. Перемноження: сума + різниця частот, виживає повільна складова ─────────
def fig_product():
    W, H = 760, 360
    f = []
    ox, w = 70, 620
    y_top = 90      # вісь добутку
    amp = 46
    dc = 0.42       # рівень cos(Δφ) — повільна складова
    f.append(text(ox + w / 2, 54, "Добуток sin·sin: повільний рівень + швидке гойдання 2ω",
                  size=14, bold=True))
    # Добуток двох рівночастотних синусоїд = cos(Δφ) − cos(2ωt+…).
    # Модель: val(t) = dc − A·cos(2ωt), де dc=cos(Δφ) — повільна складова,
    # A·cos(2ωt) — швидке гойдання на подвоєній частоті.
    cycles = 3.0
    A = 1 - dc                                   # амплітуда швидкої складової
    vals = []
    for k in range(0, w + 1, 3):
        ph = k / w * 2 * math.pi * cycles
        vals.append((ox + k, dc - A * math.cos(2 * ph)))   # у [dc−A .. dc+A] = [2dc−1 .. 1]
    # нормуємо у пікселі: 0 -> базова лінія, 1 -> вгору на 96 px
    base = y_top + 70
    poly = ["%.1f,%.1f" % (xx, base - max(v, 0.0) * 96) for xx, v in vals]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(poly), POS))
    f.append(text(ox, base + 4, "0", size=12, color=MUTED, anchor="end"))
    f.append(line(ox, base, ox + w, base, color=MUTED, sw=1.0, dash="2 4"))
    # лінія середнього рівня (повільна складова) на висоті dc
    ydc = base - dc * 96
    f.append(line(ox, ydc, ox + w, ydc, color=NEG, sw=2.2, dash="8 5"))
    f.append(text(ox + w + 2, ydc - 6, "середній рівень ∝ cos(Δφ)", size=12,
                  color=NEG, anchor="end"))
    # підпис до швидкого гойдання
    f.append(text(ox + w * 0.5, base + 48,
                  "швидке гойдання на 2ω — фільтр його прибирає; лишається лише рівень",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "product-beat.svg"), W, H, *f,
           title="Чому добуток лишає складову з різниці фаз")


# ── 6. S-крива фазового детектора: лінійна ділянка ±90° ──────────────────────
def fig_scurve():
    W, H = 720, 380
    f = []
    cx, cy = 360, 200
    halfw, halfh = 280, 120
    # осі
    f.append(arrow(cx - halfw - 10, cy, cx + halfw + 16, cy, color=INK, sw=1.6))
    f.append(arrow(cx, cy + halfh + 30, cx, cy - halfh - 30, color=INK, sw=1.6))
    f.append(text(cx + halfw + 6, cy + 22, "Δφ", size=14, color=INK, anchor="end"))
    f.append(text(cx + 8, cy - halfh - 18, "вихід детектора", size=13, color=INK, anchor="start"))
    # позначки −180, −90, 0, +90, +180 (у градусах)
    marks = [(-180, "−π"), (-90, "−π/2"), (90, "+π/2"), (180, "+π")]
    for deg, lab in marks:
        x = cx + deg / 180.0 * halfw
        f.append(line(x, cy - 4, x, cy + 4, color=MUTED, sw=1.4))
        f.append(text(x, cy + 22, lab, size=12, color=MUTED))
    # крива: множник дає sin(Δφ) (після фільтра) — для множника синус;
    # покажемо sin як характеристику, з лінійною ділянкою ±90°
    pts = []
    for d in range(-180, 181, 2):
        ph = d / 180.0 * math.pi
        val = math.sin(ph)
        x = cx + d / 180.0 * halfw
        yy = cy - val * halfh
        pts.append("%.1f,%.1f" % (x, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), POS))
    # лінійна ділянка −90..+90 — підсвітити дотичну, що ЗБІГАЄТЬСЯ з кривою біля нуля.
    # Похідна sin у нулі = 1 (рад). У пікселях: 1 рад по Δφ = (halfw/π) px;
    # 1 одиниця виходу = halfh px. Нахил у px/px = halfh / (halfw/π).
    px_per_rad = halfw / math.pi
    slope_px = halfh / px_per_rad           # dy_px / dx_px дотичної в нулі
    # малюємо дотичну в межах ±60° (там вона ще близько до синуса)
    dxr = math.radians(60)
    dxp = dxr * px_per_rad
    f.append(line(cx - dxp, cy + dxp * slope_px,
                  cx + dxp, cy - dxp * slope_px,
                  color=NEG, sw=1.6, dash="6 4"))
    f.append(text(cx + dxp + 4, cy - dxp * slope_px - 2,
                  "майже пряма ≈ Δφ", size=11, color=NEG, anchor="start"))
    # рамка робочого діапазону ±90°
    x1 = cx - halfw / 2.0
    x2 = cx + halfw / 2.0
    f.append(rect(x1, cy - halfh - 6, x2 - x1, 2 * halfh + 12,
                  fill="none", stroke=FIELD, sw=1.6, rx=8))
    bb, bw, bh = textbox(cx, cy + halfh + 44, "робочий діапазон ±90°  (втримання)",
                         size=12, color=INK, stroke=FIELD, sw=1.4, fill="#eafaf0")
    f.append(bb)
    # точки нуля й піків
    f.append(circle(cx, cy, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(cx - 8, cy - 10, "у фазі → 0", size=11, color=MUTED, anchor="end"))
    render(os.path.join(IMG, "pd-scurve.svg"), W, H, *f,
           title="Характеристика фазового детектора: лінійна біля нуля")


# ── 7. Демпфування: родина перехідних характеристик ─────────────────────────
def fig_damping():
    W, H = 740, 360
    f = []
    ox, oy, w, h = 70, 70, 600, 220
    # осі
    f.append(arrow(ox, oy + h, ox + w + 14, oy + h, color=INK, sw=1.6))
    f.append(arrow(ox, oy + h, ox, oy - 10, color=INK, sw=1.6))
    f.append(text(ox + w, oy + h + 24, "час (·ωₙ)", size=13, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - 4, "відгук", size=13, color=INK, anchor="end"))
    # цільовий рівень 1
    y1 = oy + 40
    f.append(line(ox, y1, ox + w, y1, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(ox + w + 2, y1 - 6, "ціль", size=12, color=MUTED, anchor="end"))
    y0 = oy + h - 6

    def step(zeta, col, dash=None):
        pts = []
        for k in range(0, w + 1, 2):
            t = k / w * 9.0   # τ = ωn·t у [0..9]
            if zeta < 1:
                wd = math.sqrt(1 - zeta * zeta)
                y = 1 - math.exp(-zeta * t) * (math.cos(wd * t) +
                                               zeta / wd * math.sin(wd * t))
            elif abs(zeta - 1) < 1e-6:
                y = 1 - math.exp(-t) * (1 + t)
            else:
                s = math.sqrt(zeta * zeta - 1)
                a = zeta + s
                b = zeta - s
                y = 1 - (a * math.exp(-b * t) - b * math.exp(-a * t)) / (2 * s)
            yy = y0 + (y1 - y0) * y
            pts.append("%.1f,%.1f" % (ox + k, yy))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="2.6"%s/>' % (" ".join(pts), col, d))

    f.append(step(0.3, POS))                 # слабке демпфування — перельот
    f.append(step(0.707, FIELD))             # компроміс
    f.append(step(1.6, NEG, dash="7 5"))     # передемпфоване — повільне

    # легенда
    lx, ly = ox + 360, oy + 8
    f.append(line(lx, ly, lx + 26, ly, color=POS, sw=2.6))
    f.append(text(lx + 32, ly + 4, "ζ = 0.3 — перельот, дзвенить", size=12, color=INK, anchor="start"))
    f.append(line(lx, ly + 22, lx + 26, ly + 22, color=FIELD, sw=2.6))
    f.append(text(lx + 32, ly + 26, "ζ ≈ 0.707 — швидко й без дзвону", size=12, color=INK, anchor="start"))
    f.append(line(lx, ly + 44, lx + 26, ly + 44, color=NEG, sw=2.6, dash="7 5"))
    f.append(text(lx + 32, ly + 48, "ζ = 1.6 — спокійно, але мляво", size=12, color=INK, anchor="start"))
    render(os.path.join(IMG, "damping-step.svg"), W, H, *f,
           title="Демпфування контуру: швидкість проти перельоту")


# ── 8. [hist] Лампова стійка проти кремнієвого кристала ──────────────────────
def fig_tube_vs_chip():
    W, H = 760, 360
    f = []
    midx = W / 2
    f.append(line(midx, 56, midx, H - 24, color=MUTED, sw=1.2, dash="4 6"))

    # ── Ліва панель: PLL на лампах (дорого, гаряче, громіздко) ──
    f.append(text(190, 54, "PLL на лампах (1932)", size=15, bold=True, color=POS))
    # чотири «лампи» — видовжені колби з ниткою розжарення всередині
    tube_x = [70, 145, 220, 295]
    ty = 110
    for tx in tube_x:
        f.append('<rect x="%.1f" y="%.1f" width="34" height="92" rx="17" '
                 'fill="#fdecea" stroke="%s" stroke-width="2"/>' % (tx, ty, POS))
        f.append(line(tx + 17, ty + 16, tx + 17, ty + 76, color=POS, sw=1.4, dash="3 3"))
        f.append(circle(tx + 17, ty + 90, 3, fill=POS, stroke=POS, sw=1))
    f.append(text(190, ty + 116, "жменя гарячих колб + живлення розжарення",
                  size=11, color=MUTED, italic=True))
    box, _, _ = textbox(190, 292, "ціла стійка · гаряче · дорого · вручну",
                        size=12, color=INK, stroke=POS, sw=1.6, fill="#fdecea")
    f.append(box)

    # ── Права панель: та сама петля в одному кристалі ──
    f.append(text(570, 54, "PLL у кристалі (1969)", size=15, bold=True, color=FIELD))
    chip_x, chip_y, chip_w, chip_h = 505, 120, 130, 70
    for i in range(4):
        px = chip_x + 18 + i * 32
        f.append(line(px, chip_y + chip_h, px, chip_y + chip_h + 14, color=INK, sw=2))
        f.append(line(px, chip_y - 14, px, chip_y, color=INK, sw=2))
    f.append(rect(chip_x, chip_y, chip_w, chip_h, fill="#eafaf0", stroke=FIELD, sw=2, rx=8))
    f.append(text(chip_x + chip_w / 2, chip_y + chip_h / 2 + 5, "NE565",
                  size=15, bold=True, color=FIELD))
    f.append(text(570, chip_y + chip_h + 42, "уся петля в одному кремнієвому кристалі",
                  size=11, color=MUTED, italic=True))
    box2, _, _ = textbox(570, 292, "одна деталь · холодна · копійки",
                         size=12, color=INK, stroke=FIELD, sw=1.6, fill="#eafaf0")
    f.append(box2)

    render(os.path.join(IMG, "tube-vs-chip.svg"), W, H, *f,
           title="Змінилася не ідея, а ціна її втілення")


if __name__ == "__main__":
    fig_loop()
    fig_phase_detector()
    fig_lock()
    fig_synth()
    fig_product()
    fig_scurve()
    fig_damping()
    fig_tube_vs_chip()
    print("OK figs ->", IMG)
