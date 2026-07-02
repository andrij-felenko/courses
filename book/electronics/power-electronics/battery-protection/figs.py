# -*- coding: utf-8 -*-
"""Фігури до статті «Захист акумулятора» (book/electronics/power-electronics)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: вікно безпеки комірки ─────────────────────────────────────────
def fig_window():
    W, H = 820, 440
    # вісь напруги: 4.4 В угорі → 2.0 В унизу
    x0 = 150          # ліва межа смуги
    xw = 180          # ширина смуги напруги
    top, bot = 80, 390
    vmax, vmin = 4.4, 2.0

    def yv(v):
        return top + (vmax - v) / (vmax - vmin) * (bot - top)

    frags = []
    y_ov = yv(4.25)   # межа перезаряду
    y_uv = yv(2.45)   # межа переглибокого розряду
    y_full = yv(4.2)
    y_empty = yv(3.0)

    # три зони по висоті
    frags.append(rect(x0, top, xw, y_ov - top, fill="#fdecea", stroke="none", rx=0))
    frags.append(rect(x0, y_ov, xw, y_uv - y_ov, fill="#eafaf0", stroke="none", rx=0))
    frags.append(rect(x0, y_uv, xw, bot - y_uv, fill="#eaf0fd", stroke="none", rx=0))
    frags.append(rect(x0, top, xw, bot - top, fill="none", stroke=INK, sw=1.5, rx=0))

    # нормальний робочий діапазон (3.0..4.2) — зелена смужка всередині
    frags.append(rect(x0 + 8, y_full, 12, y_empty - y_full, fill=FIELD, stroke="none", rx=3))
    frags.append(text(x0 + 30, (y_full + y_empty) / 2 - 6, "нормальна", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(text(x0 + 30, (y_full + y_empty) / 2 + 8, "робота", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(text(x0 + 30, (y_full + y_empty) / 2 + 22, "3.0 … 4.2 В", size=9, color=MUTED, anchor="start"))

    # позначки напруги ліворуч
    for v, lab in [(4.4, "4.4"), (4.2, "4.2"), (3.7, "3.7"), (3.0, "3.0"), (2.0, "2.0")]:
        frags.append(text(x0 - 10, yv(v) + 4, lab + " В", size=10, color=MUTED, anchor="end"))
        frags.append(line(x0 - 4, yv(v), x0, yv(v), color=MUTED, sw=1))

    # межа OVP
    frags.append(line(x0, y_ov, x0 + xw, y_ov, color=POS, sw=2.2, dash="6,4"))
    frags.append(text(x0 + xw + 12, y_ov - 4, "OVP ≈ 4.25 В — рубає ЗАРЯД", size=11, color=POS, anchor="start", bold=True))
    # межа UVP
    frags.append(line(x0, y_uv, x0 + xw, y_uv, color=NEG, sw=2.2, dash="6,4"))
    frags.append(text(x0 + xw + 12, y_uv + 4, "UVP ≈ 2.45 В — рубає РОЗРЯД", size=11, color=NEG, anchor="start", bold=True))

    # точки зняття (гістерезис) — риски всередину вікна
    y_ovr = yv(4.1)
    y_uvr = yv(2.9)
    frags.append(line(x0 + xw - 34, y_ov, x0 + xw - 34, y_ovr, color=POS, sw=1.2))
    frags.append(text(x0 + xw - 30, (y_ov + y_ovr) / 2 + 3, "знімає ~4.1", size=8, color=POS, anchor="start"))
    frags.append(line(x0 + xw - 34, y_uv, x0 + xw - 34, y_uvr, color=NEG, sw=1.2))
    frags.append(text(x0 + xw - 30, (y_uv + y_uvr) / 2 + 3, "знімає ~2.9", size=8, color=NEG, anchor="start"))

    # підписи небезпечних зон — рамки праворуч (ширина влазить: x до 800)
    bx = x0 + xw + 12   # = 342
    bw = 460
    frags.append(fitbox(bx, top, bw, 44,
                 "ВИЩЕ: літій осідає металом на аноді (плакування),\n"
                 "газ і розклад електроліту — незворотно, аж до дендритів",
                 size=9, pad=8, fill="#fdecea", stroke=POS, sw=1.2))
    frags.append(fitbox(bx, bot - 44, bw, 44,
                 "НИЖЧЕ: окислюється мідний струмознімач анода,\n"
                 "містки Cu крізь сепаратор — незворотно, аж до КЗ",
                 size=9, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.2))
    frags.append(fitbox(bx, (top + bot) / 2 - 26, bw, 52,
                 "МІЖ МЕЖАМИ — робоче вікно. Тут захист МОВЧИТЬ\n"
                 "і просто пропускає струм. Він втручається лише\n"
                 "на межах; зняття нижче/вище порога — гістерезис,\n"
                 "щоб плата не «торохтіла» біля самої межі.",
                 size=9, pad=8, fill="#eafaf0", stroke=FIELD, sw=1.2))

    render(os.path.join(IMG, 'window.svg'), W, H, *frags,
           title="Вузьке вікно безпеки літієвої комірки й дві межі захисту")


# ── Фігура 2: де стоїть захист і що він рве ─────────────────────────────────
def fig_topology():
    W, H = 780, 340
    frags = []

    # комірка
    cell = fitbox(60, 130, 100, 80, "комірка\nLi 1S", size=12, pad=8,
                  fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True)
    frags.append(cell)
    frags.append(plus(160, 150, 8))
    frags.append(minus(160, 190, 8))

    # верхня шина (+) — навпростець
    frags.append(line(168, 150, 700, 150, color=POS, sw=2.4))
    frags.append(circle(700, 150, 4, fill=POS, stroke=POS, sw=0))
    # нижня шина (−) — через два ключі
    frags.append(line(168, 190, 300, 190, color=INK, sw=2))
    # два ключі
    sw1 = fitbox(300, 172, 70, 36, "ключ\nрозряду", size=9, pad=4, fill="#fff7e6", stroke="#caa24a", sw=1.6)
    sw2 = fitbox(390, 172, 70, 36, "ключ\nзаряду", size=9, pad=4, fill="#fff7e6", stroke="#caa24a", sw=1.6)
    frags.append(sw1)
    frags.append(sw2)
    frags.append(line(370, 190, 390, 190, color=INK, sw=2))
    frags.append(line(460, 190, 700, 190, color=INK, sw=2))
    frags.append(circle(700, 190, 4, fill=INK, stroke=INK, sw=0))

    # виходи
    frags.append(text(712, 150, "до пристрою /", size=9, color=MUTED, anchor="start"))
    frags.append(text(712, 163, "зарядки (+)", size=9, color=MUTED, anchor="start"))
    frags.append(text(712, 192, "(−)", size=9, color=MUTED, anchor="start"))

    # монітор
    mon = fitbox(280, 260, 200, 60, "сторож (монітор)\nстежить за V комірки й струмом",
                 size=10, pad=6, fill="#eef3fb", stroke="#1f47b5", sw=1.8, bold=False)
    frags.append(mon)
    # живлення монітора від комірки
    frags.append(line(110, 210, 110, 290, color=INK, sw=1.1, dash="3,3"))
    frags.append(line(110, 290, 280, 290, color=INK, sw=1.1, dash="3,3"))
    frags.append(text(150, 283, "живиться від комірки, міряє V", size=8, color=MUTED, anchor="start"))
    # керує затворами
    frags.append(line(320, 260, 320, 208, color=FIELD, sw=1.4))
    frags.append(line(415, 260, 415, 208, color=FIELD, sw=1.4))
    frags.append(text(367, 250, "розмикає ключі", size=8, color=FIELD, anchor="middle"))
    # струм за падінням на ключах
    frags.append(line(480, 285, 545, 285, color="#caa24a", sw=1.2))
    frags.append(line(545, 285, 545, 192, color="#caa24a", sw=1.2, dash="3,3"))
    frags.append(text(490, 300, "струм — за падінням на ключах", size=8, color="#caa24a", anchor="start"))

    render(os.path.join(IMG, 'topology.svg'), W, H, *frags,
           title="Захист сидить на самій батареї й рве нижню шину двома ключами")


# ── Фігура 3: чому ключів два (діоди тіла назустріч) ────────────────────────
def fig_backtoback():
    W, H = 760, 360
    frags = []

    def fet(cx, cy, flip, label, sub):
        """Ключ як прямокутник + діод тіла (трикутник+риска)."""
        out = rect(cx - 34, cy - 26, 68, 52, fill="#fff7e6", stroke="#caa24a", sw=1.8, rx=6)
        out += text(cx, cy - 6, "ключ", size=10, color="#a07a20", bold=True)
        out += text(cx, cy + 9, label, size=9, color="#a07a20")
        # діод тіла: трикутник спрямований за flip (+1 вправо, -1 вліво)
        dy = cy + 40
        dx = cx
        s = 9 * flip
        # трикутник
        out += ('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="none" stroke="%s" stroke-width="1.6"/>'
                % (dx - s, dy - 8, dx - s, dy + 8, dx + s, dy, MUTED))
        # риска
        out += line(dx + s, dy - 8, dx + s, dy + 8, color=MUTED, sw=1.6)
        out += text(dx, dy + 24, sub, size=8, color=MUTED)
        return out

    # спільна вісь струму
    y = 130
    frags.append(text(380, 55, "у нормі обидва ключі відкриті — струм тече в обидва боки вільно", size=11, color=INK))

    # ліва частина: розряд заблоковано
    frags.append(fet(300, y, +1, "розряду", "діод ↦"))
    frags.append(fet(460, y, -1, "заряду", "діод ↤"))
    frags.append(line(210, y, 266, y, color=INK, sw=2))
    frags.append(line(334, y, 426, y, color=INK, sw=2))
    frags.append(line(494, y, 560, y, color=INK, sw=2))
    frags.append(text(200, y + 4, "комірка", size=9, color=MUTED, anchor="end"))
    frags.append(text(570, y + 4, "вихід", size=9, color=MUTED, anchor="start"))

    # блок пояснення
    exp = fitbox(120, 210, 520, 110,
                 "Один ключ не перекриває коло: закритий, він блокує струм лише в один бік,\n"
                 "а назад струм проходить крізь власний діод тіла (body diode) — наче ключа нема.\n"
                 "Розв'язок: два ключі «спина до спини», їхні діоди дивляться НАЗУСТРІЧ.\n"
                 "Закрив ключ розряду → його діод блокує розряд; закрив ключ заряду → блокує заряд.\n"
                 "Тому окремий ключ на кожен напрямок: заряд і розряд рубаються незалежно.",
                 size=10, pad=10, fill=FILL, stroke=INK, sw=1.4)
    frags.append(exp)

    render(os.path.join(IMG, 'back-to-back.svg'), W, H, *frags,
           title="Чому ключів два: діод тіла й зустрічне ввімкнення")


# ── Фігура 4: як пливе поріг OCP з температурою ключів ──────────────────────
def fig_ocp_drift():
    W, H = 780, 440
    frags = []
    # осі: X — температура ключів (°C), Y — струм спрацювання (А)
    ox, oy = 110, 360          # початок координат
    ax_w, ax_h = 590, 300      # довжина осей
    t_lo, t_hi = 25.0, 125.0   # діапазон температури
    i_lo, i_hi = 2.0, 3.4      # діапазон струму

    def xt(t):
        return ox + (t - t_lo) / (t_hi - t_lo) * ax_w

    def yi(i):
        return oy - (i - i_lo) / (i_hi - i_lo) * ax_h

    # осі
    frags.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    frags.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    frags.append(text(ox + ax_w, oy + 26, "температура ключів,  °C", size=11, color=INK, anchor="end"))
    frags.append(text(ox - 92, oy - ax_h + 6, "струм", size=11, color=INK, anchor="start"))
    frags.append(text(ox - 92, oy - ax_h + 22, "спрацю-", size=11, color=INK, anchor="start"))
    frags.append(text(ox - 92, oy - ax_h + 38, "вання, А", size=11, color=INK, anchor="start"))

    # риски по X
    for t in [25, 50, 75, 100, 125]:
        frags.append(line(xt(t), oy, xt(t), oy + 4, color=MUTED, sw=1))
        frags.append(text(xt(t), oy + 18, str(t), size=10, color=MUTED))
    # риски по Y
    for i in [2.0, 2.5, 3.0]:
        frags.append(line(ox - 4, yi(i), ox, yi(i), color=MUTED, sw=1))
        frags.append(text(ox - 10, yi(i) + 4, "%.1f" % i, size=10, color=MUTED, anchor="end"))

    # ── пряма шунта: поріг НЕ пливе (опір шунта майже сталий) ──
    frags.append(line(xt(t_lo), yi(3.0), xt(t_hi), yi(3.0), color=FIELD, sw=2.6))
    frags.append(text(xt(t_hi) - 6, yi(3.0) - 10, "точний шунт: 3.0 А — стабільно",
                      size=11, color=FIELD, anchor="end", bold=True))

    # ── крива Rds(on): I_trip = V_OCP / (R25·(1+0.004·ΔT)), падає з T ──
    R25 = 0.050
    VOCP = 0.150
    pts = []
    t = t_lo
    while t <= t_hi + 0.01:
        R = R25 * (1 + 0.004 * (t - 25.0))
        pts.append((xt(t), yi(VOCP / R)))
        t += 2.5
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    frags.append(text(xt(88), yi(VOCP / (R25 * (1 + 0.004 * 63))) - 14,
                      "поріг «за ключами»: пливе вниз", size=11, color=POS, anchor="middle", bold=True))

    # позначки двох крапок на кривій
    for t, lab in [(25, "3.0 А"), (75, "2.5 А")]:
        R = R25 * (1 + 0.004 * (t - 25.0))
        ii = VOCP / R
        frags.append(circle(xt(t), yi(ii), 4.5, fill=POS, stroke=BG, sw=1.5))
        frags.append(text(xt(t) + 8, yi(ii) + 16, lab, size=10, color=POS, anchor="start", bold=True))

    # вертикаль ΔT=50 і стрілка провалу
    frags.append(line(xt(75), yi(3.0), xt(75), yi(2.5), color=MUTED, sw=1.2, dash="4,3"))
    frags.append(text(xt(75) + 10, yi(2.75) + 4, "−17 % за +50 °C", size=9, color=MUTED, anchor="start"))

    frags.append(fitbox(ox + 12, oy - ax_h + 4, 250, 44,
                 "V_OCP = 150 мВ (фіксоване в чипі)\nR ключів = 50 мОм за 25 °C, +0.4 %/°C",
                 size=9, pad=7, fill=FILL, stroke=MUTED, sw=1.1))

    render(os.path.join(IMG, 'ocp-drift.svg'), W, H, *frags,
           title="Поріг OCP «за ключами» пливе з нагрівом; поріг за шунтом — ні")


# ── Фігура 5: розкид Rds(on) між екземплярами розмиває поріг ─────────────────
def fig_spread():
    W, H = 780, 360
    frags = []
    cx = W / 2

    # шкала струму спрацювання внизу
    ax_lo, ax_hi = 2.2, 3.8
    sx0, sxw = 120, 540
    ybar = 250

    def xs(i):
        return sx0 + (i - ax_lo) / (ax_hi - ax_lo) * sxw

    frags.append(line(sx0, ybar + 40, sx0 + sxw, ybar + 40, color=INK, sw=1.6))
    for i in [2.4, 2.7, 3.0, 3.3, 3.6]:
        frags.append(line(xs(i), ybar + 40, xs(i), ybar + 45, color=MUTED, sw=1))
        frags.append(text(xs(i), ybar + 60, "%.1f" % i, size=10, color=MUTED))
    frags.append(text(sx0 + sxw, ybar + 78, "струм спрацювання OCP,  А", size=11, color=INK, anchor="end"))

    # ── широка смуга Rds(on): ±20 % розкид опору → ±20 % розкид порога ──
    # R ном 50 мОм → I ном 3.0 А; R±20% → I від 3.0/1.2=2.5 до 3.0/0.8=3.75
    i_lo_r, i_hi_r = 3.0 / 1.2, 3.0 / 0.8
    x1, x2 = xs(i_lo_r), xs(i_hi_r)
    frags.append(rect(x1, ybar - 18, x2 - x1, 36, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    frags.append(text((x1 + x2) / 2, ybar + 4, "2.5 … 3.75 А", size=11, color=POS, bold=True))
    frags.append(text(x2 + 12, ybar - 4, "поріг «за ключами»", size=10, color=POS, anchor="start", bold=True))
    frags.append(text(x2 + 12, ybar + 12, "розкид Rds(on) ±20 %", size=9, color=POS, anchor="start"))

    # ── вузька смуга шунта: ±1 % → майже риска ──
    ish_lo, ish_hi = 3.0 / 1.01, 3.0 / 0.99
    xs1, xs2 = xs(ish_lo), xs(ish_hi)
    yshb = 120
    frags.append(rect(xs1 - 1, yshb - 16, (xs2 - xs1) + 2, 32, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=3))
    frags.append(text((xs1 + xs2) / 2, yshb - 26, "3.0 А ± 1 %", size=11, color=FIELD, bold=True))
    frags.append(text(xs2 + 12, yshb + 4, "точний шунт: майже риска", size=10, color=FIELD, anchor="start", bold=True))

    # номінал — вертикаль 3.0 А
    frags.append(line(xs(3.0), yshb - 16, xs(3.0), ybar + 40, color=MUTED, sw=1.1, dash="4,3"))
    frags.append(text(xs(3.0), 92, "номінал 3.0 А", size=9, color=MUTED))

    frags.append(fitbox(sx0, 300, sxw, 40,
                 "Той самий заданий V_OCP, але кожен ключ має СВІЙ Rds(on): паспортний розкид ±20–30 % "
                 "розмазує поріг у широку смугу. Шунт відомого опору (±1 %) лишає поріг майже точкою.",
                 size=9, pad=8, fill=FILL, stroke=INK, sw=1.2))

    render(os.path.join(IMG, 'spread.svg'), W, H, *frags,
           title="Розкид Rds(on) між екземплярами розмиває поріг; шунт — ні")


# ── Фігура 6: блок-схема класу (чип + спарений FET) ─────────────────────────
def fig_ic_block():
    W, H = 820, 400
    frags = []
    GOLD = "#caa24a"
    GOLDF = "#fff7e6"

    # комірка ліворуч
    frags.append(fitbox(40, 150, 96, 90, "комірка\nLi 1S", size=12, pad=8,
                        fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    frags.append(plus(136, 170, 8))
    frags.append(minus(136, 220, 8))

    # плюс навпростець на вихід
    frags.append(line(144, 170, 760, 170, color=POS, sw=2.4))
    frags.append(circle(760, 170, 4, fill=POS, stroke=POS, sw=0))
    frags.append(text(690, 160, "P+", size=12, color=POS, anchor="middle", bold=True))

    # мінус комірки → до спареного FET
    frags.append(line(144, 220, 300, 220, color=INK, sw=2))
    frags.append(text(210, 212, "B−", size=11, color=INK, anchor="middle", bold=True))

    # спарений FET (два ключі в одному корпусі)
    frags.append(rect(300, 190, 190, 70, fill=GOLDF, stroke=GOLD, sw=1.8, rx=8))
    frags.append(text(395, 205, "спарений N-MOSFET", size=10, color="#8a6d20", bold=True))
    frags.append(rect(316, 216, 68, 34, fill=BG, stroke=GOLD, sw=1.4, rx=4))
    frags.append(text(350, 237, "розряд", size=9, color="#8a6d20"))
    frags.append(rect(406, 216, 68, 34, fill=BG, stroke=GOLD, sw=1.4, rx=4))
    frags.append(text(440, 237, "заряд", size=9, color="#8a6d20"))
    # вихід FET → P−
    frags.append(line(490, 220, 760, 220, color=INK, sw=2))
    frags.append(circle(760, 220, 4, fill=INK, stroke=INK, sw=0))
    frags.append(text(690, 212, "P−", size=11, color=INK, anchor="middle", bold=True))

    # мітки виходів
    frags.append(text(772, 170, "до пристрою", size=9, color=MUTED, anchor="start"))
    frags.append(text(772, 220, "/ зарядки", size=9, color=MUTED, anchor="start"))

    # захисний чип (контролер) угорі
    frags.append(rect(300, 66, 190, 80, fill="#eef3fb", stroke="#1f47b5", sw=1.9, rx=8))
    frags.append(text(395, 88, "захисний чип", size=12, color="#1f47b5", bold=True))
    frags.append(text(395, 104, "(аналоговий сторож)", size=9, color=MUTED))
    frags.append(text(395, 120, "пороги зашиті в кремній", size=9, color=MUTED))
    frags.append(text(395, 136, "жодного коду / шини", size=9, color=MUTED))

    # VCC через R від плюса комірки
    frags.append(rect(212, 96, 40, 16, fill=BG, stroke=INK, sw=1.2, rx=2))
    frags.append(text(232, 108, "R", size=9, color=INK))
    frags.append(line(160, 104, 212, 104, color=INK, sw=1.2))
    frags.append(line(160, 170, 160, 104, color=INK, sw=1.2))
    frags.append(line(252, 104, 300, 104, color=INK, sw=1.2))
    frags.append(text(300, 60, "VCC", size=9, color="#1f47b5", anchor="start", bold=True))
    # кондер VCC→GND
    frags.append(line(276, 104, 276, 128, color=INK, sw=1.1))
    frags.append(line(268, 128, 284, 128, color=INK, sw=2))
    frags.append(line(270, 133, 282, 133, color=INK, sw=2))
    frags.append(line(276, 133, 276, 146, color=INK, sw=1.1))
    frags.append(text(288, 126, "C", size=8, color=MUTED, anchor="start"))
    frags.append(text(196, 92, "RC-фільтр", size=8, color=MUTED, anchor="middle"))

    # GND чипа → мінус комірки
    frags.append(line(326, 146, 326, 163, color=INK, sw=1.2))
    frags.append(line(326, 163, 220, 163, color=INK, sw=1.2, dash="3,3"))
    frags.append(text(332, 158, "GND", size=9, color="#1f47b5", anchor="start", bold=True))

    # OD, OC → затвори ключів
    frags.append(line(352, 146, 352, 190, color=FIELD, sw=1.5))
    frags.append(text(358, 170, "OD", size=9, color=FIELD, anchor="start", bold=True))
    frags.append(line(438, 146, 438, 190, color=FIELD, sw=1.5))
    frags.append(text(444, 170, "OC", size=9, color=FIELD, anchor="start", bold=True))

    # CS → вузол B− (між коміркою й FET) — вимір струму
    frags.append(line(470, 146, 470, 178, color=GOLD, sw=1.5))
    frags.append(line(470, 178, 292, 178, color=GOLD, sw=1.4, dash="4,3"))
    frags.append(line(292, 178, 292, 220, color=GOLD, sw=1.4, dash="4,3"))
    frags.append(text(476, 164, "CS", size=9, color="#8a6d20", anchor="start", bold=True))

    # пояснення виміру струму
    frags.append(fitbox(300, 300, 460, 46,
                 "Струм чип міряє за падінням напруги на самих ключах:\n"
                 "CS «дивиться» на спад між B− і виходом FET — окремого шунта нема.",
                 size=9, pad=8, fill="#fff7e6", stroke=GOLD, sw=1.2))
    # пояснення 5 ніг
    frags.append(fitbox(40, 300, 240, 46,
                 "П'ять сигналів чипа:\nVCC живлення · GND відлік ·\nOD/OC затвори · CS вимір струму",
                 size=9, pad=8, fill="#eef3fb", stroke="#1f47b5", sw=1.2))

    render(os.path.join(IMG, 'ic-block.svg'), W, H, *frags,
           title="Клас: захисний чип + спарений N-MOSFET у розриві мінуса")


# ── Фігура 7: типова розпіновка (корпус на 6 ніг) ───────────────────────────
def fig_ic_pinout():
    W, H = 800, 360
    frags = []

    # корпус чипа (SOT-23-6-подібний): 3 ноги ліворуч, 3 праворуч
    bx, by, bw, bh = 310, 86, 180, 190
    frags.append(rect(bx, by, bw, bh, fill="#eef3fb", stroke="#1f47b5", sw=2, rx=10))
    frags.append(text(bx + bw/2, by + bh/2 - 8, "захисний", size=12, color="#1f47b5", bold=True))
    frags.append(text(bx + bw/2, by + bh/2 + 10, "чип", size=12, color="#1f47b5", bold=True))
    # крапка-ключ (перша нога)
    frags.append(circle(bx + 20, by + 20, 5, fill=BG, stroke="#1f47b5", sw=1.4))

    # ліві ноги
    left = [(by + 40, "OD", "затвор ключа РОЗРЯДУ"),
            (by + 95, "CS", "вузол виміру струму (B−)"),
            (by + 150, "OC", "затвор ключа ЗАРЯДУ")]
    for y, name, desc in left:
        frags.append(line(bx - 40, y, bx, y, color=INK, sw=2))
        frags.append(rect(bx - 40, y - 9, 18, 18,
                          fill=("#eafaf0" if name in ("OD", "OC") else "#fff7e6"),
                          stroke=INK, sw=1, rx=2))
        frags.append(text(bx - 52, y + 4, name, size=11, color=INK, anchor="end", bold=True))
        frags.append(text(bx - 86, y + 4, desc, size=9, color=MUTED, anchor="end"))

    # праві ноги
    right = [(by + 40, "VCC", "живлення через R (RC-фільтр)"),
             (by + 95, "TD", "тех. нога (затримка) — не чіпати"),
             (by + 150, "GND", "спільний мінус / відлік")]
    for y, name, desc in right:
        frags.append(line(bx + bw, y, bx + bw + 40, y, color=INK, sw=2))
        col = "#eef3fb" if name != "TD" else FILL
        frags.append(rect(bx + bw + 22, y - 9, 18, 18, fill=col, stroke=INK, sw=1, rx=2))
        frags.append(text(bx + bw + 52, y + 4, name, size=11, color=INK, anchor="start", bold=True))
        frags.append(text(bx + bw + 88, y + 4, desc, size=9, color=MUTED, anchor="start"))

    frags.append(text(bx + bw/2, by - 16, "перша нога — крапка/скіс", size=9, color=MUTED))

    # підсумок унизу
    frags.append(fitbox(150, 300, 500, 42,
                 "Ноги-двійники в усіх виробників: живлення (VCC+GND), два затвори (OD/OC),\n"
                 "вузол виміру струму (CS). Назви літер різняться, зміст — той самий.",
                 size=9, pad=8, fill=FILL, stroke=INK, sw=1.3))

    render(os.path.join(IMG, 'ic-pinout.svg'), W, H, *frags,
           title="Типова розпіновка однокоміркового захисного чипа")


# ── Фігура 8: підключення в пакеті — B− проти P− ────────────────────────────
def fig_ic_connect():
    W, H = 800, 380
    frags = []
    GOLD = "#caa24a"

    # межа плати захисту (пунктиром)
    frags.append(rect(200, 66, 380, 210, fill="none", stroke=MUTED, sw=1.2, rx=10))
    frags.append(text(390, 58, "плата захисту (модуль)", size=9, color=MUTED))

    # комірка
    frags.append(fitbox(56, 148, 90, 80, "комірка", size=11, pad=8,
                        fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    frags.append(text(101, 136, "B+", size=11, color=POS, anchor="middle", bold=True))
    frags.append(text(101, 248, "B−", size=11, color=INK, anchor="middle", bold=True))
    frags.append(plus(146, 163, 7))
    frags.append(minus(146, 213, 7))

    # B+ навпростець → P+
    frags.append(line(153, 163, 720, 163, color=POS, sw=2.4))
    frags.append(circle(720, 163, 5, fill=POS, stroke=POS, sw=0))
    frags.append(text(720, 150, "P+", size=12, color=POS, anchor="middle", bold=True))

    # B− → спарений FET → P−
    frags.append(line(153, 213, 300, 213, color=INK, sw=2))
    frags.append(rect(300, 193, 150, 44, fill="#fff7e6", stroke=GOLD, sw=1.7, rx=6))
    frags.append(text(375, 211, "два ключі", size=10, color="#8a6d20", bold=True))
    frags.append(text(375, 226, "(спарений FET)", size=8, color="#8a6d20"))
    frags.append(line(450, 213, 720, 213, color=INK, sw=2))
    frags.append(circle(720, 213, 5, fill=INK, stroke=INK, sw=0))
    frags.append(text(720, 200, "P−", size=12, color=INK, anchor="middle", bold=True))

    # чип (спрощено)
    frags.append(rect(320, 92, 120, 46, fill="#eef3fb", stroke="#1f47b5", sw=1.7, rx=6))
    frags.append(text(380, 113, "захисний", size=10, color="#1f47b5", bold=True))
    frags.append(text(380, 127, "чип", size=10, color="#1f47b5", bold=True))
    frags.append(line(345, 138, 345, 193, color=FIELD, sw=1.3))
    frags.append(line(405, 138, 405, 193, color=FIELD, sw=1.3))

    # підпис виходів
    frags.append(text(600, 148, "P+ / P− — до світу", size=9, color=MUTED, anchor="start"))
    frags.append(text(600, 230, "(єдиний правильний", size=8, color=MUTED, anchor="start"))
    frags.append(text(600, 242, "вихід пакета)", size=8, color=MUTED, anchor="start"))

    # ключова різниця B− vs P−
    frags.append(fitbox(200, 300, 400, 62,
                 "Навантаження вішай на P−, НЕ на B−!\n"
                 "B− — «сира» клема комірки до ключів; на аварії вона лишається\n"
                 "живою, а захист відрубає лише P−. Чіпляти пристрій на B− — обійти\n"
                 "захист: комірку вже не вбереже ні OCP, ні UVP.",
                 size=9, pad=8, fill="#fdecea", stroke=POS, sw=1.3))

    render(os.path.join(IMG, 'ic-connect.svg'), W, H, *frags,
           title="Підключення: світ бачить лише P+/P−, а не сирі B+/B−")


# ── Фігура 9 (вставка hist): три хвилі приборкання літію ─────────────────────
def fig_history():
    W, H = 860, 340
    frags = []

    cy = 150
    bw, bh = 236, 152
    gap = 22
    x1 = 30
    x2 = x1 + bw + gap
    x3 = x2 + bw + gap

    # три картки-віхи
    frags.append(fitbox(x1, cy - bh / 2, bw, bh,
                 "1989 — металевий літій ГОРИТЬ\n"
                 "Moli Energy / NTT: телефон на\n"
                 "комірці Molicel загорівся,\n"
                 "≈10 000 апаратів відкликано.\n"
                 "Дендрити металу колють\n"
                 "сепаратор → коротке → вогонь.",
                 size=11, pad=10, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(fitbox(x2, cy - bh / 2, bw, bh,
                 "1991 — Sony: вуглецевий анод\n"
                 "прибирає МЕТАЛ. Літій сидить\n"
                 "усередині графіту як іон —\n"
                 "звідси «літій-іонна». Небезпека\n"
                 "щезає в РОБОЧОМУ вікні, та\n"
                 "лишається на його краях.",
                 size=11, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.6))
    frags.append(fitbox(x3, cy - bh / 2, bw, bh,
                 "1993–1995 — захисна МІКРОСХЕМА\n"
                 "(Seiko Instruments; Ricoh RS5VG).\n"
                 "Аналоговий автономний сторож\n"
                 "стереже краї вікна: перезаряд,\n"
                 "переглибокий розряд, надструм —\n"
                 "живиться від самої комірки.",
                 size=11, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.6))

    # стрілки між картками
    frags.append(arrow(x1 + bw + 2, cy, x2 - 2, cy, color=INK, sw=2))
    frags.append(arrow(x2 + bw + 2, cy, x3 - 2, cy, color=INK, sw=2))

    # підпис над стрілками — що саме штовхнуло далі
    frags.append(text((x1 + bw + x2) / 2, cy - bh / 2 - 8, "змінити хімію", size=9, color=MUTED))
    frags.append(text((x2 + bw + x3) / 2, cy - bh / 2 - 8, "додати сторожа", size=9, color=MUTED))

    # нижня нитка-висновок
    frags.append(fitbox(x1, cy + bh / 2 + 12, x3 + bw - x1, 42,
                 "Літій прибрав хімічний запобіжник нікелевих акумуляторів (кисневу рекомбінацію) — і його роль\n"
                 "довелося відбудувати заново, з кремнію та двох зустрічних ключів, при кожній комірці.",
                 size=10, pad=8, fill=FILL, stroke=INK, sw=1.3))

    render(os.path.join(IMG, 'history-timeline.svg'), W, H, *frags,
           title="Три хвилі, якими приборкали норов літію")


if __name__ == '__main__':
    fig_window()
    fig_topology()
    fig_backtoback()
    fig_ocp_drift()
    fig_spread()
    fig_ic_block()
    fig_ic_pinout()
    fig_ic_connect()
    fig_history()
    print("figures written to", IMG)
