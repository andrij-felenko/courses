# -*- coding: utf-8 -*-
"""Фігури до теми «Багатофазний buck-перетворювач»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

PHASE_COL = ["#c0392b", "#27ae60", "#2457d6", "#8e44ad"]  # 4 фази — 4 кольори


def coil(x0, y, n=3, r=9, color=INK):
    """Символ котушки з n дужок, зліва направо від x0 на рівні y."""
    out = []
    for k in range(n):
        cx = x0 + r + k * 2 * r
        out.append('<path d="M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f" '
                   'fill="none" stroke="%s" stroke-width="2"/>'
                   % (cx - r, y, r, r, cx + r, y, color))
    return "".join(out), x0 + n * 2 * r


# ── 1. Архітектура VRM: спільний вхід → N каскадів під контролером → вихід → CPU ──
def fig_architecture():
    W, H = 780, 500
    frags = []
    frags.append(text(W / 2, 28, "Багатофазний VRM: N каскадів на спільному виході живлять процесор", size=15, bold=True))

    xin = 100          # вхідна шина 12 В
    xblk0, xblk1 = 150, 405   # ліва/права межа блоків-каскадів
    xout = 470         # спільна вихідна шина
    ytop, ybot = 90, 320
    rows = [110, 180, 250, 320]

    # вхідна шина 12 В
    frags.append(line(xin, ytop - 12, xin, ybot, color=INK, sw=2.5))
    frags.append(plus(xin, ytop - 12, r=8))
    frags.append(text(xin, ytop - 30, "12 В", size=13, color=INK, bold=True))

    # N силових каскадів між шинами
    for i, y in enumerate(rows):
        c = PHASE_COL[i]
        frags.append(line(xin, y, xblk0, y, color=INK, sw=2))
        frags.append(rect(xblk0, y - 20, xblk1 - xblk0, 40, fill="#f4f6f8", stroke=c, sw=2.2))
        frags.append(text(xblk0 + 14, y + 5, "Ф%d" % (i + 1), size=13, color=c, bold=True))
        frags.append(text(xblk0 + 96, y + 5, "силовий каскад", size=12, color=INK, anchor="middle"))
        # маленька котушка всередині — праворуч у блоці
        cfrag, cend = coil(xblk0 + 168, y, n=3, r=7, color=INK)
        frags.append(cfrag)
        frags.append(text(xblk0 + 210, y + 5, "Lк", size=11, color=MUTED, anchor="start"))
        # вихід каскаду → спільна вихідна шина (кольором фази)
        frags.append(line(xblk1, y, xout, y, color=c, sw=2.5))
        frags.append(circle(xout, y, 3.5, fill=INK, stroke=INK))

    # спільна вихідна шина
    frags.append(line(xout, rows[0], xout, rows[-1], color=INK, sw=2.5))

    # відведення на вихід + конденсатор + навантаження
    ytap = 200
    xcap = 540
    xload = 590
    frags.append(line(xout, ytap, xload, ytap, color=INK, sw=2.5))
    frags.append(circle(xout, ytap, 3.5, fill=INK, stroke=INK))
    # вихідний конденсатор (гілка вниз)
    frags.append(line(xcap, ytap, xcap, ytap + 34, color=INK, sw=2))
    frags.append(line(xcap - 13, ytap + 34, xcap + 13, ytap + 34, color=INK, sw=2.5))
    frags.append(line(xcap - 13, ytap + 40, xcap + 13, ytap + 40, color=INK, sw=2.5))
    frags.append(text(xcap - 20, ytap + 30, "Cвих", size=11, color=MUTED, anchor="end"))
    # тик землі під конденсатором
    frags.append(line(xcap, ytap + 40, xcap, ytap + 58, color=INK, sw=2))
    for w in (11, 7, 3):
        frags.append(line(xcap - w, ytap + 58 + (11 - w), xcap + w, ytap + 58 + (11 - w), color=INK, sw=2))
    frags.append(text(xout + 8, ytap - 12, "Vвих ≈ 1 В", size=12, color=INK, anchor="start", bold=True))

    # блок навантаження — процесор
    frags.append(rect(xload, 150, 175, 100, fill="#fdecea", stroke=POS, sw=2.2))
    frags.append(text(xload + 87, 182, "ПРОЦЕСОР", size=14, color=POS, bold=True))
    frags.append(text(xload + 87, 205, "≈ 1 В · сотні А", size=12, color=INK))
    frags.append(text(xload + 87, 226, "струм ривками", size=12, color=INK))

    # контролер — знизу, з підписом трьох робіт
    cy0 = 380
    frags.append(fitbox(xin - 12, cy0, 402, 66,
                        "БАГАТОФАЗНИЙ КОНТРОЛЕР\n"
                        "зсув фаз 360°/N   ·   баланс струмів фаз   ·   скидання фаз",
                        size=12.5, fill="#eef6ff", stroke=NEG, bold=True))
    # керування фазами (одна стрілка до найнижчого блоку) + Vсенс від виходу
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" '
                 'marker-end="url(#arrow)" stroke-dasharray="5,4"/>' % (xblk0 + 60, cy0, xblk0 + 60, rows[-1] + 20, NEG))
    frags.append(text(xblk0 + 68, cy0 - 6, "ШІМ на всі фази", size=11, color=NEG, anchor="start"))
    # Vсенс від вихідної шини вниз до контролера
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)" stroke-dasharray="4,4"/>' % (xout, rows[-1] + 6, xout, cy0 + 8, FIELD))
    frags.append(line(xout, cy0 + 8, xin + 390, cy0 + 8, color=FIELD, sw=1.6, dash="4,4"))
    frags.append(text(xout + 8, rows[-1] + 34, "Vсенс", size=11, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "architecture.svg"), W, H, *frags)


# ── 2. Транзієнт: стрибок струму CPU і дві відповіді (1 велика L проти 6 малих) ──
def fig_transient():
    W, H = 780, 440
    frags = []
    frags.append(text(W / 2, 28, "Стрибок струму: повільна велика котушка проти шести прудких малих", size=15, bold=True))

    x0, x1 = 100, 700
    ybot, ytop = 350, 70
    Tmax = 8.0          # мкс
    Imax = 90.0         # А

    def mx(t):
        return x0 + (x1 - x0) * t / Tmax

    def my(i):
        return ybot - (ybot - ytop) * i / Imax

    # осі
    frags.append(line(x0, ybot, x1, ybot, color=INK, sw=1.8))
    frags.append(line(x0, ybot, x0, ytop, color=INK, sw=1.8))
    frags.append(text((x0 + x1) / 2, ybot + 40, "час, мкс", size=13, color=INK))
    frags.append(text(x0 - 44, (ybot + ytop) / 2, "струм, А", size=13, color=INK, anchor="middle"))
    for t in range(0, 9, 2):
        frags.append(line(mx(t), ybot, mx(t), ybot + 5, color=INK, sw=1.5))
        frags.append(text(mx(t), ybot + 20, str(t), size=11, color=MUTED))
    for i in (0, 20, 40, 60, 80):
        frags.append(line(x0 - 5, my(i), x0, my(i), color=INK, sw=1.5))
        frags.append(text(x0 - 12, my(i) + 4, str(i), size=11, color=MUTED, anchor="end"))

    t_step = 1.0
    i_lo, i_hi = 20.0, 80.0
    t_slow = t_step + (i_hi - i_lo) / 11.0     # 11 А/мкс → ≈6.45 мкс
    t_fast = t_step + (i_hi - i_lo) / 440.0    # 440 А/мкс → ≈1.14 мкс

    # дефіцит струму (трикутник між запитом 80 А і повільним розгоном) — заштрихований
    poly = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (mx(t_step), my(i_hi),
                                              mx(t_slow), my(i_hi),
                                              mx(t_step), my(i_lo))
    frags.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.9"/>' % poly)

    # запит процесора — сходинка (пунктир, чорний)
    dem = [(0, i_lo), (t_step, i_lo), (t_step, i_hi), (Tmax, i_hi)]
    pts = " ".join("%.1f,%.1f" % (mx(t), my(i)) for t, i in dem)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4"/>' % (pts, INK))
    frags.append(text(mx(6.4), my(i_hi) - 12, "запит процесора", size=12, color=INK, anchor="middle", bold=True))

    # повільна відповідь — одна велика котушка (11 А/мкс)
    slow = [(t_step, i_lo), (t_slow, i_hi), (Tmax, i_hi)]
    pts = " ".join("%.1f,%.1f" % (mx(t), my(i)) for t, i in slow)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, POS))
    frags.append(text(mx(4.3) + 6, my(38), "1 фаза: 11 А/мкс", size=12, color=POS, anchor="start", bold=True))

    # швидка відповідь — шість малих котушок разом (≈440 А/мкс)
    fast = [(t_step, i_lo), (t_fast, i_hi), (Tmax, i_hi)]
    pts = " ".join("%.1f,%.1f" % (mx(t), my(i)) for t, i in fast)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, FIELD))
    frags.append(text(mx(t_fast) + 10, my(72), "6 фаз разом:", size=12, color=FIELD, anchor="start", bold=True))
    frags.append(text(mx(t_fast) + 10, my(72) + 16, "≈ 440 А/мкс", size=12, color=FIELD, anchor="start", bold=True))

    # підпис дефіциту
    frags.append(text(mx(2.6), my(52), "дефіцит струму —", size=11, color=POS, anchor="middle"))
    frags.append(text(mx(2.6), my(52) + 15, "покривають", size=11, color=POS, anchor="middle"))
    frags.append(text(mx(2.6), my(52) + 30, "конденсатори", size=11, color=POS, anchor="middle"))

    # стрибок ΔI біля осі
    xb = mx(0.55)
    frags.append(line(xb, my(i_lo), xb, my(i_hi), color=MUTED, sw=1.3))
    frags.append(line(xb - 4, my(i_lo), xb + 4, my(i_lo), color=MUTED, sw=1.3))
    frags.append(line(xb - 4, my(i_hi), xb + 4, my(i_hi), color=MUTED, sw=1.3))
    frags.append(text(xb - 8, my(50) + 4, "ΔI", size=12, color=MUTED, anchor="end", bold=True))

    frags.append(fitbox(x0, 384, x1 - x0, 46,
                        "Мала котушка в кожній фазі + удар усіх фаз разом =\n"
                        "великий сумарний di/dt, а отже малий провал напруги",
                        size=12, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "transient.svg"), W, H, *frags)


# ── 3. Часова лінія: як живлення процесора дійшло до багатофазності ──────────
def fig_vrm_timeline():
    W, H = 800, 560
    frags = []
    frags.append(text(W / 2, 30, "Як живлення процесора дійшло до багатофазності", size=16, bold=True))

    xs = 150          # хребет лінії
    xb, wb = 174, 606  # рамка тексту
    y0, dy = 92, 58

    rows = [
        ("до 1995", "Процесор живиться 5 В просто з блока живлення — регулятора на платі нема",
         "#f4f6f8", MUTED),
        ("1995–1997", "Pentium Pro: регулятор — знімний модуль у сокеті (звідси «модуль» у назві)\n"
                      "VRM 8.1 — близько 14.5 А; напругу задає VID-код від самого процесора",
         "#f4f6f8", MUTED),
        ("1998", "Virginia Tech (APEC): вихід — навмисне МАЛА індуктивність\n"
                 "плюс кілька таких комірок, зсунутих у часі",
         "#eafaf0", FIELD),
        ("1999", "VRM 8.3: окремі виводи, щоб міряти напругу просто біля кристала",
         "#eef6ff", NEG),
        ("2000–2002", "Вхід переводять з 5 В на 12 В (ATX12V; настанови VRM 9.0 — квітень 2002)\n"
                      "на платах Athlon і Pentium 4 з'являються перші 2–3 фази",
         "#eafaf0", FIELD),
        ("2004", "DrMOS: драйвер і обидва ключі фази — в одному корпусі 8×8 мм",
         "#eef6ff", NEG),
        ("сер. 2000-х", "VRD 10.x (LGA775): 101 А тривало, 119 А пік, смуга ±19 мВ,\n"
                        "обов'язкова нахилена лінія навантаження",
         "#eef6ff", NEG),
        ("2013", "Haswell: FIVR — остання, найтонша сходинка переїжджає в корпус процесора",
         "#fdecea", POS),
    ]

    ylast = y0 + dy * (len(rows) - 1)
    frags.append(line(xs, y0 - 24, xs, ylast + 24, color=MUTED, sw=2.5))

    for i, (year, body, fill, col) in enumerate(rows):
        y = y0 + dy * i
        nlines = body.count("\n") + 1
        h = 30 if nlines == 1 else 46
        frags.append(fitbox(xb, y - h / 2, wb, h, body, size=12.5, fill=fill, stroke=col))
        frags.append(line(xs, y, xb, y, color=col, sw=1.8))
        frags.append(circle(xs, y, 6, fill=fill, stroke=col, sw=2.5))
        frags.append(text(xs - 22, y + 5, year, size=12, color=INK, anchor="end", bold=True))

    render(os.path.join(IMG, "vrm-timeline.svg"), W, H, *frags)


# ── 4. Три покоління процесорного живлення на платі ──────────────────────────
def fig_vrm_generations():
    W, H = 820, 430
    frags = []
    frags.append(text(W / 2, 28, "Три покоління останньої сходинки живлення процесора", size=16, bold=True))

    panels = [
        (145, POS, "#fdecea", "лінійний стабілізатор", "перша половина 1990-х",
         "5 В з блока живлення", "2.8 В · ≈6 А",
         "5 В → 2.8 В лінійно:\nрізниця згоряє на транзисторі,\nККД близько 56 %"),
        (410, NEG, "#eef6ff", "однофазний buck", "друга половина 1990-х",
         "5 В з блока живлення", "≈1.8 В · ≈20 А",
         "Ключ замість транзистора:\nККД під 90 %, та весь струм —\nкрізь один ключ і одну котушку"),
        (675, FIELD, "#eafaf0", "багатофазний VRM", "від початку 2000-х",
         "12 В з блока живлення", "≈1 В · сотні А",
         "12 В → ≈1 В зграєю фаз:\nструм і тепло поділені,\nа малі котушки встигають"),
    ]

    for k, (cx, col, fill, name, era, vin, vout, cap) in enumerate(panels):
        frags.append(rect(cx - 120, 52, 240, 278, fill=BG, stroke=col, sw=2))
        frags.append(text(cx, 76, name, size=13, color=col, bold=True))
        frags.append(text(cx, 94, era, size=11, color=MUTED))
        frags.append(text(cx, 118, vin, size=12, color=INK))
        frags.append('<line x1="%.1f" y1="124" x2="%.1f" y2="138" stroke="%s" '
                     'stroke-width="1.8" marker-end="url(#arrow)"/>' % (cx, cx, INK))

        if k == 0:
            frags.append(fitbox(cx - 85, 148, 170, 44, "прохідний\nтранзистор",
                                size=12, fill=fill, stroke=col))
            ybot = 192
        elif k == 1:
            frags.append(fitbox(cx - 85, 142, 170, 32, "ключ (ШІМ)", size=12, fill=fill, stroke=col))
            frags.append('<line x1="%.1f" y1="176" x2="%.1f" y2="188" stroke="%s" '
                         'stroke-width="1.6" marker-end="url(#arrow)"/>' % (cx, cx, INK))
            frags.append(fitbox(cx - 85, 190, 170, 32, "котушка L", size=12, fill=fill, stroke=col))
            ybot = 222
        else:
            for j, lab in enumerate(("фаза 1", "фаза 2", "фаза N")):
                c = PHASE_COL[j]
                frags.append(fitbox(cx - 95, 140 + j * 32, 190, 28, lab, size=12,
                                    fill=fill, stroke=c))
            ybot = 232

        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="254" stroke="%s" '
                     'stroke-width="1.8" marker-end="url(#arrow)"/>' % (cx, ybot + 8, cx, INK))
        frags.append(text(cx, 270, vout, size=12, color=INK, bold=True))
        frags.append(fitbox(cx - 75, 278, 150, 40, "ПРОЦЕСОР", size=12,
                            fill="#f4f6f8", stroke=INK, bold=True))
        frags.append(fitbox(cx - 120, 344, 240, 66, cap, size=11.5, fill=fill, stroke=col))

    render(os.path.join(IMG, "vrm-generations.svg"), W, H, *frags)


# ── Що всередині корпусу силового каскаду (до вставки comp-smart-power-stage) ──
def fig_power_stage_block():
    W, H = 880, 490
    frags = []
    frags.append(text(W / 2, 22, "Силовий каскад: що зібрано в одному корпусі", size=15, bold=True))

    # межа корпусу
    frags.append('<rect x="120" y="60" width="580" height="400" rx="10" fill="#fbfcfd" '
                 'stroke="%s" stroke-width="1.6" stroke-dasharray="7,5"/>' % MUTED)
    frags.append(text(132, 80, "корпус силового каскаду", size=11, color=MUTED, anchor="start"))

    BRAIN = dict(size=11, fill="#eef6ff", stroke=NEG, sw=1.8)
    frags.append(fitbox(145, 88, 175, 64, "вхідна логіка\nтри стани, витримка", **BRAIN))
    frags.append(fitbox(145, 168, 175, 58, "мертвий час\nза станом SW", **BRAIN))
    frags.append(fitbox(145, 250, 175, 54, "вимір струму\nпо Rds(on) нижнього", **BRAIN))
    frags.append(fitbox(145, 330, 175, 44, "давач температури\nкристала", **BRAIN))
    frags.append(fitbox(145, 398, 175, 44, "захисти: UVLO,\nструм, перегрів", **BRAIN))

    # поправка на температуру → у вимірювач струму
    frags.append('<line x1="232" y1="328" x2="232" y2="308" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)"/>' % NEG)
    frags.append(text(240, 322, "поправка", size=10, color=MUTED, anchor="start"))

    # ніжки ліворуч
    for y, name in ((100, "VCC"), (120, "PWM"), (140, "EN"),
                    (277, "IMON"), (352, "TMON"), (420, "аварія")):
        frags.append(line(45, y, 145, y, color=INK, sw=1.8))
        frags.append(text(48, y - 9, name, size=11, color=INK, anchor="start"))

    # ніжка BOOT згори → драйвер верхнього
    frags.append(line(430, 45, 430, 125, color=INK, sw=1.8))
    frags.append(line(430, 125, 385, 125, color=INK, sw=1.8))
    frags.append(line(385, 125, 385, 144, color=INK, sw=1.8))
    frags.append(text(436, 52, "BOOT", size=11, color=INK, anchor="start"))

    # драйвери — трикутники
    for cy in (153, 273):
        frags.append('<polygon points="360,%d 360,%d 410,%d" fill="%s" stroke="%s" '
                     'stroke-width="2"/>' % (cy - 20, cy + 20, cy, FILL, NEG))
    frags.append(text(385, 112, "драйвер", size=10, color=MUTED))
    frags.append(text(385, 245, "драйвер", size=10, color=MUTED))

    # шина керування від логіки до обох драйверів
    frags.append(line(320, 120, 345, 120, color=INK, sw=1.8))
    frags.append(line(345, 120, 345, 273, color=INK, sw=1.8))
    frags.append(circle(345, 153, 3.2, fill=INK, stroke=INK))
    frags.append(arrow(345, 153, 357, 153, color=INK, sw=1.8))
    frags.append(arrow(345, 273, 357, 273, color=INK, sw=1.8))

    # силова частина
    frags.append(line(470, 100, 800, 100, color=INK, sw=2.5))
    frags.append(text(712, 92, "VIN 12 В", size=11, color=INK, anchor="start", bold=True))
    frags.append(fitbox(480, 130, 80, 46, "верхній\nключ", size=11, fill="#fdecea", stroke=POS, sw=2))
    frags.append(line(520, 100, 520, 130, color=INK, sw=2.2))
    frags.append(line(520, 176, 520, 250, color=INK, sw=2.2))
    frags.append(fitbox(480, 250, 80, 46, "нижній\nключ", size=11, fill="#fdecea", stroke=POS, sw=2))
    frags.append(line(520, 296, 520, 360, color=INK, sw=2.2))
    frags.append(line(470, 360, 800, 360, color=INK, sw=2.5))
    frags.append(text(712, 352, "PGND", size=11, color=INK, anchor="start", bold=True))

    # затвори
    frags.append(arrow(412, 153, 476, 153, color=INK, sw=1.8))
    frags.append(arrow(412, 273, 476, 273, color=INK, sw=1.8))

    # вузол SW назовні, у котушку
    frags.append(line(520, 215, 760, 215, color=INK, sw=2.2))
    frags.append(circle(520, 215, 3.5, fill=INK, stroke=INK))
    frags.append(text(712, 207, "SW", size=11, color=INK, anchor="start", bold=True))
    cfrag, cend = coil(760, 215, n=3, r=9, color=INK)
    frags.append(cfrag)
    frags.append(line(cend, 215, 860, 215, color=INK, sw=2.2))
    frags.append(mtext(837, 190, ["котушка", "фази"], size=11, color=MUTED))

    # зворотний зв'язок: стан SW → мертвий час
    frags.append(line(520, 240, 450, 240, color=FIELD, sw=1.6, dash="5,4"))
    frags.append(line(450, 240, 450, 197, color=FIELD, sw=1.6, dash="5,4"))
    frags.append('<line x1="450" y1="197" x2="324" y2="197" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)" stroke-dasharray="5,4"/>' % FIELD)
    frags.append(circle(520, 240, 3.2, fill=FIELD, stroke=FIELD))

    # зворотний зв'язок: падіння на нижньому ключі → вимірювач струму
    frags.append(line(480, 255, 430, 255, color=POS, sw=1.6, dash="5,4"))
    frags.append(line(430, 255, 430, 340, color=POS, sw=1.6, dash="5,4"))
    frags.append(line(430, 340, 520, 340, color=POS, sw=1.6, dash="5,4"))
    frags.append('<line x1="430" y1="300" x2="324" y2="300" stroke="%s" stroke-width="1.6" '
                 'marker-end="url(#arrow)" stroke-dasharray="5,4"/>' % POS)
    frags.append(circle(430, 300, 3.2, fill=POS, stroke=POS))
    frags.append(circle(520, 340, 3.2, fill=POS, stroke=POS))

    render(os.path.join(IMG, "power-stage-block.svg"), W, H, *frags)


# ── Вимір струму по нижньому ключу: бланкування, зчитування, IMON ────────────
def fig_imon_sampling():
    W, H = 880, 400
    frags = []
    frags.append(text(W / 2, 22, "Вимірювання струму фази по відкритому нижньому ключу",
                      size=15, bold=True))

    def mx(t):
        return 100.0 + 318.18 * t

    def iy(i):
        return 340.0 - 150.0 * i / 70.0

    # межі тактів
    for t in (1.0, 2.0):
        frags.append(line(mx(t), 70, mx(t), 340, color="#d0d5dd", sw=1.0, dash="3,4"))

    # смуги вимірювання (позаду кривих)
    for k in (0, 1):
        x1, x2, x3 = mx(k + 0.27), mx(k + 0.35), mx(k + 0.98)
        frags.append('<rect x="%.1f" y="190" width="%.1f" height="150" fill="#fdecea" stroke="none"/>'
                     % (x1, x2 - x1))
        frags.append('<rect x="%.1f" y="190" width="%.1f" height="150" fill="#eafaf0" stroke="none"/>'
                     % (x2, x3 - x2))

    # верхня панель: стан ключів
    hs = [(0, 105), (0, 78), (0.25, 78), (0.25, 105), (1, 105), (1, 78), (1.25, 78),
          (1.25, 105), (2, 105), (2, 78), (2.2, 78)]
    ls = [(0, 150), (0.27, 150), (0.27, 123), (0.98, 123), (0.98, 150), (1.27, 150),
          (1.27, 123), (1.98, 123), (1.98, 150), (2.2, 150)]
    for pts, col in ((hs, POS), (ls, NEG)):
        s = " ".join("%.1f,%.1f" % (mx(t), y) for t, y in pts)
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (s, col))
    frags.append(text(92, 96, "верхній ключ", size=11, color=POS, anchor="end"))
    frags.append(text(92, 141, "нижній ключ", size=11, color=NEG, anchor="end"))

    # підписи смуг
    frags.append(text(mx(0.31), 182, "бланкування", size=10, color=POS))
    frags.append(line(mx(0.31), 186, mx(0.31), 190, color=POS, sw=1.2))
    frags.append(text(mx(0.665), 182, "вікно вимірювання", size=10, color=FIELD))
    frags.append(line(mx(0.665), 186, mx(0.665), 190, color=FIELD, sw=1.2))

    # осі нижньої панелі
    frags.append(line(100, 340, 810, 340, color=INK, sw=1.8))
    frags.append(line(100, 340, 100, 185, color=INK, sw=1.8))
    for i in (0, 20, 40, 60):
        frags.append(line(95, iy(i), 100, iy(i), color=INK, sw=1.4))
        frags.append(text(92, iy(i) + 4, str(i), size=10, color=MUTED, anchor="end"))
    frags.append(text(100, 178, "струм, А", size=11, color=MUTED))

    # струм котушки
    cur = [(0, 30), (0.25, 45), (1.0, 30), (1.25, 45), (2.0, 30), (2.2, 42)]
    s = " ".join("%.1f,%.1f" % (mx(t), iy(i)) for t, i in cur)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (s, POS))

    # IMON — утримується між зчитуваннями
    im = [(0, 0), (0.625, 0), (0.625, 37.5), (2.2, 37.5)]
    s = " ".join("%.1f,%.1f" % (mx(t), iy(i)) for t, i in im)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (s, NEG))
    frags.append(text(mx(1.35), 300, "IMON = середній струм фази", size=11, color=NEG, bold=True))

    # точки зчитування
    for t in (0.625, 1.625):
        frags.append(circle(mx(t), iy(37.5), 5, fill=NEG, stroke=NEG))
    frags.append(text(mx(0.625), 230, "зчитування посередині", size=10, color=NEG))
    frags.append(line(mx(0.625), 234, mx(0.625), 253, color=NEG, sw=1.2))

    # позначка такту
    frags.append(line(mx(0), 356, mx(1), 356, color=MUTED, sw=1.4))
    frags.append(line(mx(0), 352, mx(0), 360, color=MUTED, sw=1.4))
    frags.append(line(mx(1), 352, mx(1), 360, color=MUTED, sw=1.4))
    frags.append(text(mx(0.5), 374, "один такт", size=10, color=MUTED))

    render(os.path.join(IMG, "imon-sampling.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_architecture()
    fig_transient()
    fig_vrm_timeline()
    fig_vrm_generations()
    fig_power_stage_block()
    fig_imon_sampling()
    print("figs done")
