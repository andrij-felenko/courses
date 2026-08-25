# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра сигналів
CLK_COL = NEG          # тактовий сигнал SCK — синій
DAT_COL = "#8e44ad"    # лінія даних MOSI/MISO — фіолетовий
SETUP_COL = FIELD      # часові інтервали t_su — зелений
HOLD_COL = "#d35400"   # часові інтервали t_h — помаранчевий
WARN_COL = POS         # критичні зони / затримки — червоний
GRAY_COL = MUTED       # розмірні лінії та допоміжні сітки

def draw_dim_h(x1, x2, y, label, color=INK, size=11, offset_y=-5, arrows="both"):
    """Горизонтальна розмірна лінія з двома стрілками та підписом."""
    frags = []
    frags.append(line(x1, y - 5, x1, y + 5, color=color, sw=1.2))
    frags.append(line(x2, y - 5, x2, y + 5, color=color, sw=1.2))
    if arrows == "both":
        frags.append(line(x1, y, x2, y, color=color, sw=1.2))
        frags.append(arrow(x1 + 8, y, x1, y, color=color, sw=1.2))
        frags.append(arrow(x2 - 8, y, x2, y, color=color, sw=1.2))
    elif arrows == "right":
        frags.append(arrow(x1, y, x2, y, color=color, sw=1.2))
    elif arrows == "left":
        frags.append(arrow(x2, y, x1, y, color=color, sw=1.2))
    else:
        frags.append(line(x1, y, x2, y, color=color, sw=1.2))
    frags.append(text((x1 + x2) / 2, y + offset_y, label, size=size, color=color, bold=True))
    return "".join(frags)


# ── 1. timing-overview.svg: Повний огляд часових параметрів SPI ───────────────
def fig_timing_overview():
    W, H = 880, 390
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    p.append(text(75, 95, "SCLK", size=14, color=CLK_COL, bold=True, anchor="end"))
    p.append(text(75, 225, "MOSI/MISO", size=13, color=DAT_COL, bold=True, anchor="end"))

    t0 = 120
    t1 = 280
    t2 = 440
    t3 = 600
    t4 = 760

    y_sck_hi = 70
    y_sck_lo = 120
    sck_pts = [
        (90, y_sck_lo),
        (t0, y_sck_lo), (t0, y_sck_hi),
        (t1, y_sck_hi), (t1, y_sck_lo),
        (t2, y_sck_lo), (t2, y_sck_hi),
        (t3, y_sck_hi), (t3, y_sck_lo),
        (t4, y_sck_lo), (t4, y_sck_hi),
        (830, y_sck_hi)
    ]
    poly_sck = " ".join("%.1f,%.1f" % pt for pt in sck_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (poly_sck, CLK_COL))

    for tx in [t0, t1, t2, t3, t4]:
        p.append(line(tx, 45, tx, 310, color="#d0d7de", sw=1.0, dash="3,3"))

    p.append(draw_dim_h(t0, t1, 52, "t_HIGH", color=CLK_COL, size=11, offset_y=-5))
    p.append(draw_dim_h(t1, t2, 52, "t_LOW", color=CLK_COL, size=11, offset_y=-5))
    p.append(draw_dim_h(t0, t2, 33, "t_CLK = 1 / f_MAX (Період)", color=INK, size=12, offset_y=-5))

    y_d_hi = 200
    y_d_lo = 250
    y_d_mid = 225

    t_chg = t1 + 45
    t_hold_end = t3 - 35

    p.append(line(90, y_d_hi, t1 - 10, y_d_hi, color=DAT_COL, sw=2.2))
    p.append(line(90, y_d_lo, t1 - 10, y_d_lo, color=DAT_COL, sw=2.2))
    p.append(line(t1 - 10, y_d_hi, t_chg, y_d_lo, color=DAT_COL, sw=2.0))
    p.append(line(t1 - 10, y_d_lo, t_chg, y_d_hi, color=DAT_COL, sw=2.0))

    p.append(rect(t_chg, y_d_hi, t_hold_end - t_chg, y_d_lo - y_d_hi, fill="#e8f8f5", stroke="none"))
    p.append(line(t_chg, y_d_hi, t_hold_end, y_d_hi, color=DAT_COL, sw=2.2))
    p.append(line(t_chg, y_d_lo, t_hold_end, y_d_lo, color=DAT_COL, sw=2.2))
    p.append(text((t_chg + t_hold_end) / 2, y_d_mid + 4, "Дійсні стабільні дані", size=11, color="#16a085", bold=True))

    p.append(line(t_hold_end, y_d_hi, t3 + 35, y_d_lo, color=DAT_COL, sw=2.0))
    p.append(line(t_hold_end, y_d_lo, t3 + 35, y_d_hi, color=DAT_COL, sw=2.0))
    p.append(line(t3 + 35, y_d_hi, 830, y_d_hi, color=DAT_COL, sw=2.2))
    p.append(line(t3 + 35, y_d_lo, 830, y_d_lo, color=DAT_COL, sw=2.2))

    p.append(draw_dim_h(t1, t_chg, 168, "t_V", color=WARN_COL, size=11, offset_y=-4))
    p.append(draw_dim_h(t_chg, t2, 280, "t_SU (Встановлення)", color=SETUP_COL, size=11, offset_y=14))
    p.append(draw_dim_h(t2, t_hold_end, 280, "t_H (Утримання)", color=HOLD_COL, size=11, offset_y=14))

    p.append(arrow(t2, 155, t2, 190, color=SETUP_COL, sw=2.4))
    tb, _, _ = textbox(t2, 142, "Фронт вибірки", size=10, pad=4, fill="#eafaf1", stroke=SETUP_COL, bold=True)
    p.append(tb)

    p.append(text(W / 2, H - 16, "Часові параметри такту й ліній даних: t_CLK = період, t_SU = запас до вибірки, t_H = утримання після вибірки", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "timing-overview.svg"), W, H, *p, title="Часові інтервали SPI")


# ── 2. setup-hold-window.svg: Апертура фіксації D-тригера ──────────────────────
def fig_setup_hold_window():
    W, H = 760, 320
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    t_edge = 380
    t_su_w = 120
    t_h_w = 90
    t_su_start = t_edge - t_su_w
    t_h_end = t_edge + t_h_w

    p.append(rect(t_su_start, 45, t_su_w + t_h_w, 200, fill="#fdebd0", stroke=WARN_COL, sw=1.5, rx=4))
    p.append(text(t_edge, 62, "ЗАБОРОНЕНА ЗОНА ЗМІНИ ДАНИХ (Апертура)", size=11, color=WARN_COL, bold=True))

    p.append(rect(30, 45, t_su_start - 30, 200, fill="#e8f8f5", stroke="#a3e4d7", sw=1.2, rx=4))
    p.append(text((30 + t_su_start) / 2, 62, "Дані стабільні (Data Setup)", size=10, color=SETUP_COL, bold=True))

    p.append(rect(t_h_end, 45, (W - 30) - t_h_end, 200, fill="#eaf2f8", stroke="#aed6f1", sw=1.2, rx=4))
    p.append(text((t_h_end + W - 30) / 2, 62, "Дані зафіксовано (Data Hold)", size=10, color=CLK_COL, bold=True))

    y_clk_lo = 135
    y_clk_hi = 85
    p.append(line(40, y_clk_lo, t_edge, y_clk_lo, color=CLK_COL, sw=2.5))
    p.append(line(t_edge, y_clk_lo, t_edge, y_clk_hi, color=CLK_COL, sw=2.5))
    p.append(line(t_edge, y_clk_hi, W - 40, y_clk_hi, color=CLK_COL, sw=2.5))
    p.append(text(100, y_clk_lo - 8, "SCLK (фронт вибірки)", size=12, color=CLK_COL, bold=True))

    y_d_mid = 195
    p.append(line(40, y_d_mid - 20, t_su_start, y_d_mid - 20, color=DAT_COL, sw=2.2))
    p.append(line(40, y_d_mid + 20, t_su_start, y_d_mid + 20, color=DAT_COL, sw=2.2))
    p.append(line(t_su_start, y_d_mid - 20, t_h_end, y_d_mid - 20, color=DAT_COL, sw=2.2))
    p.append(line(t_su_start, y_d_mid + 20, t_h_end, y_d_mid + 20, color=DAT_COL, sw=2.2))
    p.append(line(t_h_end, y_d_mid - 20, W - 40, y_d_mid - 20, color=DAT_COL, sw=2.2))
    p.append(line(t_h_end, y_d_mid + 20, W - 40, y_d_mid + 20, color=DAT_COL, sw=2.2))
    p.append(text(100, y_d_mid - 26, "Вхідні дані D (MOSI/MISO)", size=12, color=DAT_COL, bold=True))

    p.append(draw_dim_h(t_su_start, t_edge, 225, "t_SU (Час встановлення)", color=SETUP_COL, size=11, offset_y=14))
    p.append(draw_dim_h(t_edge, t_h_end, 225, "t_H (Час утримання)", color=HOLD_COL, size=11, offset_y=14))

    p.append(arrow(t_edge, 275, t_edge, 140, color=WARN_COL, sw=2.2))
    p.append(text(t_edge, 290, "Момент спрацьовування D-тригера приймача", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "setup-hold-window.svg"), W, H, *p, title="Апертура встановлення та утримання")


# ── 3. round-trip-delay.svg: Затримка круглого циклу та фазовий зсув ──────────
def fig_round_trip_delay():
    W, H = 820, 390
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    p.append(rect(30, 40, 180, 270, fill="#f4f6f9", stroke=CLK_COL, sw=1.8, rx=6))
    p.append(text(120, 65, "Ведучий (Master)", size=13, color=CLK_COL, bold=True))
    p.append(text(120, 85, "Генератор такту SCLK", size=10, color=MUTED))
    p.append(text(120, 100, "Вхідний D-тригер MISO", size=10, color=MUTED))

    p.append(rect(610, 40, 180, 270, fill="#fcf3cf", stroke="#b7950b", sw=1.8, rx=6))
    p.append(text(700, 65, "Ведений (Slave)", size=13, color="#7d6608", bold=True))
    p.append(text(700, 85, "Приймач такту SCLK", size=10, color=MUTED))
    p.append(text(700, 100, "Вихідний драйвер t_V", size=10, color=MUTED))

    y_sclk = 140
    p.append(arrow(210, y_sclk, 610, y_sclk, color=CLK_COL, sw=2.6))
    tb1, _, _ = textbox(410, y_sclk - 16, "SCLK: пряма затримка в кабелі t_prop(out)", size=11, pad=5, fill="#ebf5fb", stroke=CLK_COL, bold=True)
    p.append(tb1)

    p.append(rect(625, 135, 150, 85, fill="#fef9e7", stroke=WARN_COL, sw=1.4, rx=4))
    p.append(text(700, 155, "Затримка веденого:", size=10, color=INK, bold=True))
    p.append(text(700, 175, "t_V = t_CLK_to_Out", size=12, color=WARN_COL, bold=True))
    p.append(text(700, 195, "(від 5 нс до 40 нс)", size=9, color=MUTED))

    y_miso = 250
    p.append(arrow(610, y_miso, 210, y_miso, color=DAT_COL, sw=2.6))
    tb2, _, _ = textbox(410, y_miso - 16, "MISO: зворотна затримка в кабелі t_prop(in)", size=11, pad=5, fill="#f4ecf7", stroke=DAT_COL, bold=True)
    p.append(tb2)

    tb3, _, _ = textbox(410, 325, "Сумарний час відгуку: T_round_trip = t_prop(out) + t_V(slave) + t_prop(in) + t_SU(master) <= T_CLK", size=11, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    p.append(tb3)

    p.append(text(W / 2, H - 14, "Затримка подвійного пробігу кабелю (2 · t_prop) разом із t_V обмежує максимальну частоту читання", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "round-trip-delay.svg"), W, H, *p, title="Затримка круглого циклу SPI")


# ── 4. cpha-timing-comparison.svg: Порівняння часових запасів за CPHA=0 та CPHA=1
def fig_cpha_comparison():
    W, H = 820, 370
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    p.append(rect(25, 35, W - 50, 140, fill="#ffffff", stroke="#d0d7de", rx=6))
    p.append(text(40, 58, "Режим CPHA = 0: Вибірка на 1-му фронті (напівперіод T_CLK / 2)", size=12, color=INK, bold=True, anchor="start"))

    t0_a, t1_a, t2_a = 180, 340, 500
    p.append(text(150, 95, "SCLK", size=12, color=CLK_COL, bold=True, anchor="end"))
    p.append(line(160, 110, t0_a, 110, color=CLK_COL, sw=2.2))
    p.append(line(t0_a, 110, t0_a, 80, color=CLK_COL, sw=2.2))
    p.append(line(t0_a, 80, t1_a, 80, color=CLK_COL, sw=2.2))
    p.append(line(t1_a, 80, t1_a, 110, color=CLK_COL, sw=2.2))
    p.append(line(t1_a, 110, t2_a, 110, color=CLK_COL, sw=2.2))
    p.append(line(t2_a, 110, t2_a, 80, color=CLK_COL, sw=2.2))
    p.append(line(t2_a, 80, 680, 80, color=CLK_COL, sw=2.2))

    p.append(text(150, 145, "MISO", size=12, color=DAT_COL, bold=True, anchor="end"))
    p.append(line(160, 145, t1_a + 30, 145, color=DAT_COL, sw=2.0))
    p.append(line(t1_a + 30, 135, t2_a + 80, 135, color=DAT_COL, sw=2.0))
    p.append(line(t1_a + 30, 155, t2_a + 80, 155, color=DAT_COL, sw=2.0))
    p.append(draw_dim_h(t1_a, t2_a, 160, "Бюджет = T_CLK / 2 (Жорстке обмеження)", color=WARN_COL, size=10, offset_y=12))

    p.append(rect(25, 190, W - 50, 145, fill="#ffffff", stroke="#d0d7de", rx=6))
    p.append(text(40, 213, "Режим CPHA = 1: Вибірка на 2-му фронті (повний напівперіод / період)", size=12, color=INK, bold=True, anchor="start"))

    p.append(text(150, 250, "SCLK", size=12, color=CLK_COL, bold=True, anchor="end"))
    p.append(line(160, 265, t0_a, 265, color=CLK_COL, sw=2.2))
    p.append(line(t0_a, 265, t0_a, 235, color=CLK_COL, sw=2.2))
    p.append(line(t0_a, 235, t1_a, 235, color=CLK_COL, sw=2.2))
    p.append(line(t1_a, 235, t1_a, 265, color=CLK_COL, sw=2.2))
    p.append(line(t1_a, 265, t2_a, 265, color=CLK_COL, sw=2.2))
    p.append(line(t2_a, 265, t2_a, 235, color=CLK_COL, sw=2.2))
    p.append(line(t2_a, 235, 680, 235, color=CLK_COL, sw=2.2))

    p.append(text(150, 300, "MISO", size=12, color=DAT_COL, bold=True, anchor="end"))
    p.append(line(160, 300, t0_a + 30, 300, color=DAT_COL, sw=2.0))
    p.append(line(t0_a + 30, 290, t1_a + 80, 290, color=DAT_COL, sw=2.0))
    p.append(line(t0_a + 30, 310, t1_a + 80, 310, color=DAT_COL, sw=2.0))
    p.append(draw_dim_h(t0_a, t1_a, 315, "Інтервал t_HIGH (або повний такт для випереджальної вибірки)", color=FIELD, size=10, offset_y=12))

    p.append(text(W / 2, H - 12, "У режимах з вибіркою за протилежним фронтом критичним стає саме напівперіод t_HIGH або t_LOW", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cpha-timing-comparison.svg"), W, H, *p, title="Порівняння часових бюджетів CPHA=0 та CPHA=1")


# ── 5. isolator-delay-budget.svg: Вплив цифрових ізоляторів та перетворювачів рівнів
def fig_isolator_delay():
    W, H = 820, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", rx=8))

    p.append(rect(30, 50, 160, 240, fill="#eaf2f8", stroke=CLK_COL, sw=1.8, rx=6))
    p.append(text(110, 75, "MCU (3.3V)", size=13, color=CLK_COL, bold=True))
    p.append(text(110, 95, "SPI Контролер", size=10, color=MUTED))

    p.append(rect(290, 40, 240, 260, fill="#fef9e7", stroke="#d4ac0d", sw=2.0, rx=6))
    p.append(text(410, 65, "Гальванічна розв'язка / Рівні", size=12, color="#7d6608", bold=True))
    p.append(text(410, 83, "(ISO7741 / TXS0108E)", size=10, color=MUTED))

    p.append(rect(630, 50, 160, 240, fill="#eaeded", stroke="#717d7e", sw=1.8, rx=6))
    p.append(text(710, 75, "Периферія (5V)", size=13, color=INK, bold=True))
    p.append(text(710, 95, "ADC / SPI Flash", size=10, color=MUTED))

    y1 = 135
    p.append(arrow(190, y1, 290, y1, color=CLK_COL, sw=2.2))
    p.append(rect(310, y1 - 15, 200, 30, fill="#ffffff", stroke=WARN_COL, sw=1.2, rx=3))
    p.append(text(410, y1 + 4, "Затримка ізолятора t_p1 = 11 нс", size=10, color=WARN_COL, bold=True))
    p.append(arrow(490, y1, 630, y1, color=CLK_COL, sw=2.2))
    p.append(text(240, y1 - 8, "SCLK_MCU", size=9, color=CLK_COL))
    p.append(text(560, y1 - 8, "SCLK_ISO", size=9, color=CLK_COL))

    y2 = 220
    p.append(arrow(630, y2, 490, y2, color=DAT_COL, sw=2.2))
    p.append(rect(310, y2 - 15, 200, 30, fill="#ffffff", stroke=WARN_COL, sw=1.2, rx=3))
    p.append(text(410, y2 + 4, "Затримка ізолятора t_p2 = 11 нс", size=10, color=WARN_COL, bold=True))
    p.append(arrow(290, y2, 190, y2, color=DAT_COL, sw=2.2))
    p.append(text(560, y2 - 8, "MISO_DEV", size=9, color=DAT_COL))
    p.append(text(240, y2 - 8, "MISO_MCU", size=9, color=DAT_COL))

    tb, _, _ = textbox(410, 320, "Додаткова затримка ізоляції: Δt = t_p1 + t_p2 = 22 нс (зменшує f_MAX з 50 МГц до < 15 МГц)", size=11, pad=6, fill="#fdebd0", stroke=WARN_COL, bold=True)
    p.append(tb)

    render(os.path.join(OUT, "isolator-delay-budget.svg"), W, H, *p, title="Вплив затримок цифрової ізоляції")


if __name__ == "__main__":
    fig_timing_overview()
    fig_setup_hold_window()
    fig_round_trip_delay()
    fig_cpha_comparison()
    fig_isolator_delay()
    print("Всі фігури згенеровано успішно.")
