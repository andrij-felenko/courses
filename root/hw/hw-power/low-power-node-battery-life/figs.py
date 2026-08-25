# -*- coding: utf-8 -*-
"""Фігури до теми «Розрахунок терміну служби батареї».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (AUTHORING §5)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Наївний розрахунок проти реального життя ─────────────────────────────
def fig_naive_vs_real_life():
    W, H = 840, 440
    f = [text(W / 2, 28, "Наївний розрахунок проти реального терміну служби", size=16, bold=True)]

    ox, oy = 110, 360
    ax_w, ax_h = 650, 280

    # осі
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    f.append(text(ox + ax_w / 2, oy + 44, "час експлуатації, роки", size=12, color=INK, bold=True))

    # Y label
    f.append('<text x="32" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 32 %.1f)">'
             'залишок ємності / працездатність, %%</text>' % (oy - ax_h / 2, FONT, INK, oy - ax_h / 2))

    # мітки X: 0 .. 10 років
    for yr in range(0, 11, 2):
        x = ox + yr / 10.0 * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        f.append(text(x, oy + 20, str(yr), size=11, color=MUTED))

    # мітки Y: 0 .. 100%
    for pct in (0, 20, 40, 60, 80, 100):
        y = oy - pct / 100.0 * ax_h
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.5))
        f.append(text(ox - 12, y + 4, str(pct) + "%", size=10, color=MUTED, anchor="end"))

    # 1. Наївна пряма (T = C / I_avg = 10 років)
    x_10 = ox + 1.0 * ax_w
    y_0 = oy
    f.append(line(ox, oy - ax_h, x_10, y_0, color=MUTED, sw=2, dash="6 4"))
    tb_naive, _, _ = textbox(ox + 480, oy - 235, "Наївна модель: T = C / I_сер (10 років)",
                             size=11, pad=6, fill="#ffffff", stroke=MUTED, color=MUTED, bold=True)
    f.append(tb_naive)

    # 2. Крива з урахуванням саморозряду (тягнеться до ~6 років)
    pts_self = []
    for i in range(101):
        t = i / 100.0 * 6.5
        rem = 100.0 * (1.0 - t / 10.0) * math.exp(-0.06 * t)
        if rem < 0: rem = 0
        px = ox + (t / 10.0) * ax_w
        py = oy - (rem / 100.0) * ax_h
        pts_self.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 3"/>' % (" ".join(pts_self), NEG))

    # 3. Реальна крива з просадкою напруги та відсічкою UVLO
    pts_real = []
    t_cutoff = 3.2
    for i in range(51):
        t = i / 50.0 * t_cutoff
        rem = 100.0 * (1.0 - t / 10.0) * math.exp(-0.07 * t)
        px = ox + (t / 10.0) * ax_w
        py = oy - (rem / 100.0) * ax_h
        pts_real.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts_real), POS))

    # Точка відсічки
    x_cut = ox + (t_cutoff / 10.0) * ax_w
    y_cut = oy - (58.0 / 100.0) * ax_h
    f.append(circle(x_cut, y_cut, 5, fill=POS, stroke=POS, sw=2))

    # Лінія аварійної відсічки (поріг UVLO)
    f.append(line(x_cut, y_cut, x_cut, oy, color=POS, sw=1.5, dash="3 3"))
    f.append(line(ox, y_cut, x_cut, y_cut, color=POS, sw=1, dash="2 2"))

    b1, _, _ = textbox(ox + 480, oy - 165,
                       "Апаратна відсічка UVLO (3.2 роки)\n"
                       "Напруга під піковим струмом < V_min\n"
                       "42% заряду лишається замкненим у хімії!",
                       size=10, pad=7, fill="#fdecea", stroke=POS, bold=True)
    f.append(b1)

    tb_self, _, _ = textbox(ox + 480, oy - 95, "+ Саморозряд хімії (1–3%/рік)",
                            size=10.5, pad=5, fill="#ffffff", stroke=NEG, color=NEG, bold=True)
    f.append(tb_self)

    render(os.path.join(IMG, "naive-vs-real-life.svg"), W, H, *f)


# ── 2. Профіль струму Duty Cycle ─────────────────────────────────────────────
def fig_duty_cycle_profile():
    W, H = 840, 430
    f = [text(W / 2, 28, "Профіль споживання автономного пристрою (Duty Cycle)", size=16, bold=True)]

    ox, oy = 90, 240
    pw, ph = 690, 160

    # вісь часу
    f.append(line(ox, oy, ox + pw + 20, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ph - 20, color=INK, sw=2))
    f.append(text(ox + pw / 2, oy + 42, "час одного робочого циклу (T_період = 60 с)", size=12, color=INK, bold=True))

    f.append('<text x="28" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 28 %.1f)">'
             'струм споживання, мА</text>' % (oy - ph / 2, FONT, INK, oy - ph / 2))

    # фази у часі
    y_sleep = oy - 2
    y_sense = oy - 35
    y_tx = oy - 150
    y_rx = oy - 55

    # контур графіка
    poly_pts = [
        (ox, y_sleep),
        (ox + 420, y_sleep),
        (ox + 420, y_sense),
        (ox + 490, y_sense),
        (ox + 490, y_tx),
        (ox + 570, y_tx),
        (ox + 570, y_rx),
        (ox + 630, y_rx),
        (ox + 630, y_sleep),
        (ox + pw, y_sleep)
    ]
    poly_str = " ".join("%.1f,%.1f" % pt for pt in poly_pts)
    fill_pts = poly_str + " %.1f,%.1f %.1f,%.1f" % (ox + pw, oy, ox, oy)

    f.append('<polygon points="%s" fill="#eaf0fd" stroke="none"/>' % fill_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly_str, NEG))

    # виділення TX
    f.append('<rect x="%.1f" y="%.1f" width="80" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.5"/>'
             % (ox + 490, y_tx, oy - y_tx, POS))
    f.append(text(ox + 530, y_tx - 12, "TX Burst\n120 мА", size=11, color=POS, bold=True))

    # підписи фаз
    f.append(text(ox + 210, oy - 20, "Глибокий сон (Deep Sleep): I_сон = 2 мкА (99.85% часу)", size=11, color=MUTED, bold=True))
    f.append(text(ox + 455, y_sense - 12, "Сенсор\n15 мА", size=10, color=INK))
    f.append(text(ox + 600, y_rx - 12, "RX\n25 мА", size=10, color=INK))

    # Порівняльні блоки внизу
    b_time = fitbox(ox + 10, oy + 70, 310, 85,
                    "Розподіл часу в циклі:\n"
                    "• Сон: 59.91 с (99.85% часу)\n"
                    "• Активні фази: 0.09 с (0.15% часу)",
                    size=11, fill="#f4f6f8", stroke=LINE)
    b_charge = fitbox(ox + 360, oy + 70, 330, 85,
                      "Розподіл витраченого заряду:\n"
                      "• Сон (2 мкА): 0.12 мкА·год (10% заряду)\n"
                      "• TX/RX/Сенсор: 1.10 мкА·год (90% заряду!)",
                      size=11, fill="#fdecea", stroke=POS, bold=True)
    f.append(b_time)
    f.append(b_charge)

    render(os.path.join(IMG, "duty-cycle-profile.svg"), W, H, *f)


# ── 3. Просадка напруги та відсічка UVLO ─────────────────────────────────────
def fig_voltage_sag_cutoff():
    W, H = 840, 440
    f = [text(W / 2, 28, "Просадка напруги під час імпульсу та відсічка UVLO", size=16, bold=True)]

    ox, oy = 110, 350
    ax_w, ax_h = 650, 260

    # осі
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    f.append(text(ox + ax_w / 2, oy + 42, "віддана ємність від номіналу, % (ступінь розряду SoC)", size=12, color=INK, bold=True))

    f.append('<text x="32" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 32 %.1f)">'
             'напруга елемента, В</text>' % (oy - ax_h / 2, FONT, INK, oy - ax_h / 2))

    # мітки X: 0% .. 100%
    for pct in range(0, 101, 20):
        x = ox + pct / 100.0 * ax_w
        f.append(line(ox, oy, x, oy + 5, color=INK, sw=1.5))
        f.append(text(x, oy + 20, str(pct) + "%", size=11, color=MUTED))
        if pct > 0:
            f.append(line(x, oy, x, oy - ax_h, color="#f0f2f5", sw=1))

    # мітки Y: 1.5 В .. 4.0 В (span = 2.5 В)
    def y_volt(v):
        return oy - (v - 1.5) / 2.5 * ax_h

    for v in (2.0, 2.5, 3.0, 3.5, 4.0):
        y = y_volt(v)
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.5))
        f.append(text(ox - 12, y + 4, "%.1f В" % v, size=10.5, color=MUTED, anchor="end"))
        f.append(line(ox, y, ox + ax_w, y, color="#f0f2f5", sw=1))

    # Поріг відсічки V_cut = 2.2 В
    y_cut = y_volt(2.2)
    f.append(line(ox, y_cut, ox + ax_w, y_cut, color=POS, sw=1.8, dash="5 4"))
    f.append(text(ox + ax_w - 90, y_cut - 10, "Поріг UVLO (V_min = 2.2 В)", size=11, color=POS, bold=True))

    # Крива 1: OCV (напруга розімкненого кола під час сну, ~3.65 В -> 3.2 В)
    pts_ocv = []
    for p in range(101):
        pct = p / 100.0
        if pct < 0.8:
            vocv = 3.65 - 0.45 * (pct / 0.8) ** 1.5
        else:
            vocv = 3.20 - 1.2 * ((pct - 0.8) / 0.2) ** 1.2
        px = ox + pct * ax_w
        py = y_volt(vocv)
        pts_ocv.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_ocv), FIELD))
    f.append(text(ox + 220, y_volt(3.68) - 12, "OCV у стані сну (струм 2 мкА): напруга висока", size=11, color=FIELD, bold=True))

    # Крива 2: Напруга під імпульсом 100 мА
    pts_pulse = []
    pct_shutdown = 58.0
    for p in range(int(pct_shutdown) + 1):
        pct = p / 100.0
        vocv = 3.65 - 0.45 * (pct / 0.8) ** 1.5
        r_int = 3.0 + 18.0 * (pct ** 2)
        vterm = vocv - 0.100 * r_int
        px = ox + pct * ax_w
        py = y_volt(vterm)
        pts_pulse.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_pulse), POS))
    f.append(text(ox + 180, y_volt(3.05) + 18, "V_терм під час радіоімпульсу (100 мА)", size=11, color=POS, bold=True))

    # Стрілка просадки Delta V = I * R_int
    x_arr = ox + 0.3 * ax_w
    y_top = y_volt(3.65 - 0.45 * (0.3 / 0.8) ** 1.5)
    r_mid = 3.0 + 18.0 * (0.3 ** 2)
    y_bot = y_volt((3.65 - 0.45 * (0.3 / 0.8) ** 1.5) - 0.100 * r_mid)
    f.append(line(x_arr, y_top, x_arr, y_bot, color=INK, sw=1.5))
    f.append(text(x_arr + 65, (y_top + y_bot) / 2 + 4, "ΔV = I_пік · R_внутр", size=10, color=INK, bold=True))

    # Точка аварійної відсічки
    x_sd = ox + (pct_shutdown / 100.0) * ax_w
    f.append(circle(x_sd, y_cut, 5, fill=POS, stroke=POS, sw=2))
    f.append(line(x_sd, y_cut, x_sd, oy, color=POS, sw=1.5, dash="3 3"))

    b_sd, _, _ = textbox(x_sd + 120, y_cut + 55,
                         "Зупинка на 58% ємності!\n"
                         "42% заряду лишається в батареї,\n"
                         "але радіочип перезавантажується\n"
                         "через падіння шини нижче 2.2 В",
                         size=10, pad=7, fill="#fdecea", stroke=POS, bold=True)
    f.append(b_sd)

    render(os.path.join(IMG, "voltage-sag-cutoff.svg"), W, H, *f)


# ── 4. Буферизація суперконденсатором / HLC ──────────────────────────────────
def fig_supercap_buffer():
    W, H = 840, 420
    f = [text(W / 2, 28, "Згладжування пікового струму суперконденсатором / HLC", size=16, bold=True)]

    # Ліва половина: принципова схема
    sx, sy = 60, 80
    sw_b, sh_b = 320, 300
    f.append(rect(sx, sy, sw_b, sh_b, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(sx + sw_b / 2, sy + 25, "Схема паралельного буфера", size=13, bold=True))

    # Елементи схеми
    bx, by = sx + 50, sy + 140
    f.append(rect(bx - 30, by - 40, 60, 80, fill="#f7f9fb", stroke=LINE, sw=1.5))
    f.append(text(bx, by - 15, "Батарея", size=11, bold=True))
    f.append(text(bx, by + 5, "Li-SOCl2", size=10, color=MUTED))
    f.append(text(bx, by + 22, "R_внутр ~20Ω", size=9.5, color=POS))

    cx, cy = sx + 170, sy + 140
    f.append(rect(cx - 28, cy - 40, 56, 80, fill="#eef6ef", stroke=FIELD, sw=1.5))
    f.append(text(cx, cy - 15, "Буфер", size=11, color=FIELD, bold=True))
    f.append(text(cx, cy + 5, "HLC / EDLC", size=10, color=FIELD))
    f.append(text(cx, cy + 22, "C ~10-100мФ", size=9.5, color=FIELD))

    lx, ly = sx + 270, sy + 140
    f.append(rect(lx - 28, ly - 40, 56, 80, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(lx, ly - 15, "Радіо / MCU", size=10.5, color=POS, bold=True))
    f.append(text(lx, ly + 5, "TX Імпульс", size=9.5, color=POS))
    f.append(text(lx, ly + 22, "120 мА", size=9.5, color=POS, bold=True))

    f.append(line(bx + 30, by - 25, cx - 28, by - 25, color=INK, sw=2))
    f.append(line(cx + 28, by - 25, lx - 28, by - 25, color=INK, sw=2))
    f.append(line(bx + 30, by + 25, cx - 28, by + 25, color=INK, sw=2))
    f.append(line(cx + 28, by + 25, lx - 28, by + 25, color=INK, sw=2))

    f.append(text(sx + 105, by - 38, "I_бат ~0.8 мА", size=10, color=MUTED, bold=True))
    f.append(line(bx + 32, by - 25, cx - 30, by - 25, color=FIELD, sw=2.5))

    f.append(text(sx + 220, by - 38, "I_пік 120 мА", size=10, color=POS, bold=True))
    f.append(line(cx + 30, by - 25, lx - 30, by - 25, color=POS, sw=3))

    f.append(text(sx + sw_b / 2, sy + sh_b - 20,
                  "Конденсатор віддає 99% імпульсу;\n"
                  "батарея спокійно дозаряджає його", size=10, color=MUTED))

    # Права половина: осцилограми струму й напруги
    rx, ry = 420, 80
    rw, rh = 380, 300
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(rx + rw / 2, ry + 25, "Форма струмів під час радіопередачі", size=13, bold=True))

    g1_y = ry + 80
    f.append(line(rx + 40, g1_y, rx + rw - 30, g1_y, color=INK, sw=1.5))
    f.append(text(rx + 35, g1_y - 25, "I_навант (120 мА)", size=10, color=POS, anchor="start", bold=True))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join(["%.1f,%.1f" % (rx + 40, g1_y),
                        "%.1f,%.1f" % (rx + 120, g1_y),
                        "%.1f,%.1f" % (rx + 120, g1_y - 30),
                        "%.1f,%.1f" % (rx + 180, g1_y - 30),
                        "%.1f,%.1f" % (rx + 180, g1_y),
                        "%.1f,%.1f" % (rx + rw - 30, g1_y)]), POS))

    g2_y = ry + 180
    f.append(line(rx + 40, g2_y, rx + rw - 30, g2_y, color=INK, sw=1.5))
    f.append(text(rx + 35, g2_y - 25, "I_батареї (згладжений, ~1 мА)", size=10, color=FIELD, anchor="start", bold=True))
    pts_bat = [
        (rx + 40, g2_y),
        (rx + 120, g2_y),
        (rx + 130, g2_y - 12),
        (rx + 160, g2_y - 15),
        (rx + 200, g2_y - 10),
        (rx + 260, g2_y - 3),
        (rx + 320, g2_y),
        (rx + rw - 30, g2_y)
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_bat), FIELD))

    g3_y = ry + 270
    f.append(line(rx + 40, g3_y, rx + rw - 30, g3_y, color=INK, sw=1.5))
    f.append(text(rx + 35, g3_y - 25, "Напруга шини V_bus (лише мала просадка ΔV)", size=10, color=NEG, anchor="start", bold=True))
    pts_v = [
        (rx + 40, g3_y - 20),
        (rx + 120, g3_y - 20),
        (rx + 180, g3_y - 8),
        (rx + 260, g3_y - 16),
        (rx + 320, g3_y - 20),
        (rx + rw - 30, g3_y - 20)
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in pts_v), NEG))

    render(os.path.join(IMG, "supercap-buffer.svg"), W, H, *f)


# ── 5. Вплив температури ────────────────────────────────────────────────────
def fig_temperature_effects():
    W, H = 840, 440
    f = [text(W / 2, 28, "Вплив температури: стрибок опору та падіння ємності", size=16, bold=True)]

    ox, oy = 110, 350
    ax_w, ax_h = 650, 260

    # осі
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))
    f.append(text(ox + ax_w / 2, oy + 42, "робоча температура навколишнього середовища, °C", size=12, color=INK, bold=True))

    # Y1 label
    f.append('<text x="32" y="%.1f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 32 %.1f)">'
             'внутрішній опір R_внутр, Ом</text>' % (oy - ax_h / 2, FONT, POS, oy - ax_h / 2))

    # Y2 вісь праворуч
    rx = ox + ax_w
    f.append(line(rx, oy, rx, oy - ax_h, color=INK, sw=2))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(90 %.1f %.1f)">'
             'доступна ємність, %%</text>' % (rx + 48, oy - ax_h / 2, FONT, NEG, rx + 48, oy - ax_h / 2))

    # мітки X: -30°C .. +60°C
    for temp in range(-30, 61, 15):
        x = ox + (temp + 30) / 90.0 * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        f.append(text(x, oy + 20, ("+%d" if temp > 0 else "%d") % temp + "°C", size=10.5, color=MUTED))
        f.append(line(x, oy, x, oy - ax_h, color="#f0f2f5", sw=1))

    # мітки Y1 (ліворуч: 0 .. 50 Ом)
    for r in (0, 10, 20, 30, 40, 50):
        y = oy - (r / 50.0) * ax_h
        f.append(line(ox - 5, y, ox, y, color=POS, sw=1.5))
        f.append(text(ox - 12, y + 4, str(r), size=10.5, color=POS, anchor="end"))

    # мітки Y2 (праворуч: 0 .. 100%)
    for pct in (0, 25, 50, 75, 100):
        y = oy - (pct / 100.0) * ax_h
        f.append(line(rx, y, rx + 5, y, color=NEG, sw=1.5))
        f.append(text(rx + 12, y + 4, str(pct) + "%", size=10.5, color=NEG, anchor="start"))

    # Крива 1: R_int(T)
    pts_r = []
    for i in range(91):
        temp = -30 + i
        r_val = 2.5 * math.exp(-0.045 * (temp - 25))
        if r_val > 50: r_val = 50
        px = ox + (temp + 30) / 90.0 * ax_w
        py = oy - (r_val / 50.0) * ax_h
        pts_r.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts_r), POS))
    f.append(text(ox + 130, oy - 230, "R_внутр злітає на морозі", size=11, color=POS, bold=True))

    # Крива 2: Cap(T)
    pts_c = []
    for i in range(91):
        temp = -30 + i
        cap_val = 100.0 / (1.0 + math.exp(-0.06 * (temp + 10)))
        px = ox + (temp + 30) / 90.0 * ax_w
        py = oy - (cap_val / 100.0) * ax_h
        pts_c.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="6 3"/>' % (" ".join(pts_c), NEG))
    f.append(text(ox + 450, oy - 190, "Доступна ємність падає за мінусових температур", size=11, color=NEG, bold=True))

    # Позначка кімнатної температури (+25°C)
    x_25 = ox + (25 + 30) / 90.0 * ax_w
    f.append(line(x_25, oy, x_25, oy - ax_h, color=MUTED, sw=1.5, dash="3 3"))
    f.append(text(x_25, oy - ax_h - 10, "+25°C (паспортні дані)", size=10, color=MUTED, bold=True))

    render(os.path.join(IMG, "temperature-effects.svg"), W, H, *f)


if __name__ == '__main__':
    fig_naive_vs_real_life()
    fig_duty_cycle_profile()
    fig_voltage_sag_cutoff()
    fig_supercap_buffer()
    fig_temperature_effects()
    print("All 5 figures generated successfully.")
