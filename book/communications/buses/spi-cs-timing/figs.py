# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Часові параметри CS у SPI».
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори сигналів
CLK = NEG          # тактовий сигнал SCLK (синій)
CS_COL = POS       # сигнал вибору CS (червоний/теракотовий)
DAT = "#7a5fb0"    # дані MOSI / MISO (фіолетовий)
HI_Z = "#9ca3af"   # високий імпеданс Z (сірий)
HL_BG = "#eef2ff"  # підсвічування інтервалів (світло-блакитний)
WARN_BG = "#fef2f2"# підсвічування помилок (світло-рожевий)


# ── 1. Головна часова діаграма CS: t_CSS, t_CSH, t_CS_HIGH ────────────────────
def fig_timing_diagram():
    W, H = 840, 440
    p = []

    # Заголовок / фонова сітка
    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Вертикальні опорні лінії
    x_cs_fall   = 140
    x_clk_start = 240
    x_clk_end   = 560
    x_cs_rise   = 660
    x_next_fall = 770

    # Фонове підсвічування ключових часових інтервалів
    p.append(rect(x_cs_fall, 45, x_clk_start - x_cs_fall, 320, fill=HL_BG, stroke="none", rx=0))
    p.append(rect(x_clk_end, 45, x_cs_rise - x_clk_end, 320, fill=HL_BG, stroke="none", rx=0))
    p.append(rect(x_cs_rise, 45, x_next_fall - x_cs_rise, 320, fill="#fdf8e2", stroke="none", rx=0))

    # Пунктирні вертикалі
    for vx in [x_cs_fall, x_clk_start, x_clk_end, x_cs_rise, x_next_fall]:
        p.append(line(vx, 40, vx, 370, color=MUTED, sw=1.0, dash="3,3"))

    # 1. Сигнал CS
    y_cs_hi, y_cs_lo = 75, 115
    cs_pts = [
        (40, y_cs_hi), (x_cs_fall, y_cs_hi),
        (x_cs_fall, y_cs_lo), (x_cs_rise, y_cs_lo),
        (x_cs_rise, y_cs_hi), (W - 40, y_cs_hi)
    ]
    poly_cs = " ".join("%.1f,%.1f" % pt for pt in cs_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="miter"/>' % (poly_cs, CS_COL))
    p.append(text(30, 95, "CS (SS)", size=13, color=CS_COL, bold=True, anchor="end"))

    # 2. Сигнал SCLK (Mode 0: CPOL=0)
    y_clk_hi, y_clk_lo = 145, 185
    clk_pts = [(40, y_clk_lo), (x_clk_start, y_clk_lo)]
    t_step = (x_clk_end - x_clk_start) / 8.0
    for i in range(4):
        x1 = x_clk_start + (2 * i) * t_step
        x2 = x1 + t_step
        x3 = x2 + t_step
        clk_pts.extend([(x1, y_clk_hi), (x2, y_clk_hi), (x2, y_clk_lo), (x3, y_clk_lo)])
    clk_pts.append((W - 40, y_clk_lo))
    poly_clk = " ".join("%.1f,%.1f" % pt for pt in clk_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="miter"/>' % (poly_clk, CLK))
    p.append(text(30, 165, "SCLK", size=13, color=CLK, bold=True, anchor="end"))

    # 3. Сигнал MOSI (передача даних)
    y_mosi_mid = 235
    amp_m = 16
    p.append(line(40, y_mosi_mid, x_cs_fall + 20, y_mosi_mid, color=MUTED, sw=1.5))
    
    # Створюємо секції бітів замість суцільної лінії, щоб написи були всередині своїх рамок
    p.append(rect(x_cs_fall + 20, y_mosi_mid - amp_m, x_clk_end + 30 - (x_cs_fall + 20), 2 * amp_m, fill="#f3f4f6", stroke=DAT, sw=1.6, rx=4))
    p.append(text((x_cs_fall + x_clk_end) / 2 + 10, y_mosi_mid + 4, "Команда / Дані (D7...D0)", size=11, color=INK, bold=True, anchor="middle"))
    p.append(line(x_clk_end + 30, y_mosi_mid, W - 40, y_mosi_mid, color=MUTED, sw=1.5))
    p.append(text(30, 235, "MOSI", size=13, color=DAT, bold=True, anchor="end"))

    # 4. Сигнал MISO (Z-стан -> Активний -> Z-стан)
    y_miso_mid = 305
    # Z-стан ліворуч
    p.append(line(40, y_miso_mid, x_cs_fall + 40, y_miso_mid, color=HI_Z, sw=2.0, dash="4,4"))
    p.append(text(85, y_miso_mid - 8, "Hi-Z", size=11, color=MUTED, anchor="middle"))
    # Активний стан
    p.append(rect(x_cs_fall + 40, y_miso_mid - amp_m, x_cs_rise - (x_cs_fall + 40), 2 * amp_m, fill="#f3f4f6", stroke=DAT, sw=1.6, rx=4))
    p.append(text((x_cs_fall + 40 + x_cs_rise) / 2, y_miso_mid + 4, "Відповідь веденого", size=11, color=INK, bold=True, anchor="middle"))
    # Повернення в Z-стан праворуч
    p.append(line(x_cs_rise, y_miso_mid, W - 40, y_miso_mid, color=HI_Z, sw=2.0, dash="4,4"))
    p.append(text(x_cs_rise + 55, y_miso_mid - 8, "Hi-Z", size=11, color=MUTED, anchor="middle"))
    p.append(text(30, 305, "MISO", size=13, color=DAT, bold=True, anchor="end"))

    # Розмірні стрілки та позначення інтервалів
    y_dim = 365
    # t_CSS (t_LEAD)
    p.append(line(x_cs_fall, y_dim, x_clk_start, y_dim, color=POS, sw=1.8))
    p.append(line(x_cs_fall, y_dim - 6, x_cs_fall, y_dim + 6, color=POS, sw=1.8))
    p.append(line(x_clk_start, y_dim - 6, x_clk_start, y_dim + 6, color=POS, sw=1.8))
    p.append(text((x_cs_fall + x_clk_start) / 2, y_dim + 20, "t_CSS (t_LEAD)", size=12, color=POS, bold=True, anchor="middle"))
    p.append(text((x_cs_fall + x_clk_start) / 2, y_dim + 36, "час встановлення", size=10, color=MUTED, anchor="middle"))

    # t_CSH (t_LAG)
    p.append(line(x_clk_end, y_dim, x_cs_rise, y_dim, color=POS, sw=1.8))
    p.append(line(x_clk_end, y_dim - 6, x_clk_end, y_dim + 6, color=POS, sw=1.8))
    p.append(line(x_cs_rise, y_dim - 6, x_cs_rise, y_dim + 6, color=POS, sw=1.8))
    p.append(text((x_clk_end + x_cs_rise) / 2, y_dim + 20, "t_CSH (t_LAG)", size=12, color=POS, bold=True, anchor="middle"))
    p.append(text((x_clk_end + x_cs_rise) / 2, y_dim + 36, "час утримання", size=10, color=MUTED, anchor="middle"))

    # t_CS_HIGH (t_IDLE)
    p.append(line(x_cs_rise, y_dim, x_next_fall, y_dim, color=FIELD, sw=1.8))
    p.append(line(x_cs_rise, y_dim - 6, x_cs_rise, y_dim + 6, color=FIELD, sw=1.8))
    p.append(line(x_next_fall, y_dim - 6, x_next_fall, y_dim + 6, color=FIELD, sw=1.8))
    p.append(text((x_cs_rise + x_next_fall) / 2, y_dim + 20, "t_CS_HIGH (t_IDLE)", size=12, color=FIELD, bold=True, anchor="middle"))
    p.append(text((x_cs_rise + x_next_fall) / 2, y_dim + 36, "пауза між фреймами", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "timing-diagram.svg"), W, H, *p,
           title="Часові параметри сигналу Chip Select (CS) у протоколі SPI")


# ── 2. Передчасний підйом CS: обрив останнього біта і збій FSM ─────────────────
def fig_premature_cs_abort():
    W, H = 820, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    x0 = 80
    x_bit7_start = 480
    x_bit7_sample = 520
    x_cs_early_rise = 505
    x_bit7_end = 560

    # Червона зона збою
    p.append(rect(x_cs_early_rise, 45, x_bit7_end - x_cs_early_rise + 40, 260, fill=WARN_BG, stroke="none", rx=0))
    p.append(line(x_cs_early_rise, 40, x_cs_early_rise, 310, color=POS, sw=1.5, dash="4,4"))

    # Сигнал CS з передчасним підйомом
    y_cs_hi, y_cs_lo = 75, 110
    cs_pts = [
        (40, y_cs_lo), (x_cs_early_rise, y_cs_lo),
        (x_cs_early_rise, y_cs_hi), (W - 40, y_cs_hi)
    ]
    poly_cs = " ".join("%.1f,%.1f" % pt for pt in cs_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly_cs, CS_COL))
    p.append(text(30, 95, "CS", size=13, color=CS_COL, bold=True, anchor="end"))

    # Текст над підйомом CS
    p.append(text(x_cs_early_rise + 10, y_cs_hi - 12, "Передчасний підйом CS!", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(x_cs_early_rise + 10, y_cs_hi + 4, "(передача байта ще не завершена)", size=10, color=MUTED, anchor="start"))

    # Сигнал SCLK (8 тактів)
    y_clk_hi, y_clk_lo = 150, 185
    clk_pts = [(40, y_clk_lo)]
    t_bit = 60
    for i in range(8):
        x_st = x0 + i * t_bit
        x_mid = x_st + t_bit / 2
        x_en = x_st + t_bit
        clk_pts.extend([(x_st, y_clk_lo), (x_st, y_clk_hi), (x_mid, y_clk_hi), (x_mid, y_clk_lo), (x_en, y_clk_lo)])
    clk_pts.append((W - 40, y_clk_lo))
    poly_clk = " ".join("%.1f,%.1f" % pt for pt in clk_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly_clk, CLK))
    p.append(text(30, 168, "SCLK", size=13, color=CLK, bold=True, anchor="end"))

    # Номери бітів над тактом
    for i in range(7):
        p.append(text(x0 + i * t_bit + t_bit / 2, y_clk_hi - 8, "B%d" % (7 - i), size=11, color=INK, anchor="middle"))
    p.append(text(x0 + 7 * t_bit + t_bit / 2, y_clk_hi - 8, "B0 (обірвано)", size=11, color=POS, bold=True, anchor="middle"))

    # Лінія MISO / MOSI
    y_dat = 240
    amp_d = 16
    for i in range(7):
        cx = x0 + i * t_bit
        p.append(rect(cx, y_dat - amp_d, t_bit, 2 * amp_d, fill="#e5e7eb", stroke=DAT, sw=1.2, rx=2))
        p.append(text(cx + t_bit / 2, y_dat + 4, "біт %d" % (7 - i), size=10, color=INK, anchor="middle"))

    # 8-й біт — спотворений і скинутий у Hi-Z
    cx8 = x0 + 7 * t_bit
    w_valid = x_cs_early_rise - cx8
    p.append(rect(cx8, y_dat - amp_d, w_valid, 2 * amp_d, fill="#fee2e2", stroke=POS, sw=1.5, rx=2))
    p.append(text(cx8 + w_valid / 2, y_dat + 4, "обрив", size=9, color=POS, bold=True, anchor="middle"))
    # Після підйому CS лінія скидається в Z
    p.append(line(x_cs_early_rise, y_dat, W - 40, y_dat, color=HI_Z, sw=2.0, dash="4,4"))
    p.append(text(x_cs_early_rise + 50, y_dat - 8, "Hi-Z (вимкнено)", size=10, color=MUTED, anchor="start"))
    p.append(text(30, 240, "Дані", size=13, color=DAT, bold=True, anchor="end"))

    # Виноски з поясненням наслідків
    p.append(line(x_cs_early_rise, 290, x_cs_early_rise + 60, 290, color=POS, sw=1.5))
    p.append(text(x_cs_early_rise + 70, 285, "1. Останній біт B0 не зафіксовано в регістрі (Latching Error)", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x_cs_early_rise + 70, 305, "2. Лічильник бітів веденого залишається у стані 7/8 (Bit Slip при наступній транзакції)", size=11, color=INK, anchor="start"))
    p.append(text(x_cs_early_rise + 70, 325, "3. У Flash/EEPROM команда запису повністю ігнорується або блокується", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "premature-cs-abort.svg"), W, H, *p,
           title="Наслідки передчасного підйому CS: обрив 8-го біта та збій автомата станів")


# ── 3. Асиметрія затримок в ізоляторах / оптопарах (Skew) ─────────────────────
def fig_isolator_skew():
    W, H = 840, 410
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Секція 1: Передавач (MCU)
    p.append(rect(30, 35, 360, 325, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(210, 60, "На виході ведучого (MCU)", size=13, color=INK, bold=True, anchor="middle"))

    # MCU CS
    x_m_cs = 80
    x_m_clk = 220
    p.append(line(50, 100, x_m_cs, 100, color=CS_COL, sw=2.2))
    p.append(line(x_m_cs, 100, x_m_cs, 135, color=CS_COL, sw=2.2))
    p.append(line(x_m_cs, 135, 370, 135, color=CS_COL, sw=2.2))
    p.append(text(45, 118, "CS", size=11, color=CS_COL, bold=True, anchor="end"))

    # MCU SCLK
    p.append(line(50, 185, x_m_clk, 185, color=CLK, sw=2.2))
    p.append(line(x_m_clk, 185, x_m_clk, 150, color=CLK, sw=2.2))
    p.append(line(x_m_clk, 150, x_m_clk + 40, 150, color=CLK, sw=2.2))
    p.append(line(x_m_clk + 40, 150, x_m_clk + 40, 185, color=CLK, sw=2.2))
    p.append(line(x_m_clk + 40, 185, 370, 185, color=CLK, sw=2.2))
    p.append(text(45, 168, "SCLK", size=11, color=CLK, bold=True, anchor="end"))

    # Інтервал t_CSS на виході MCU (нормальний)
    p.append(line(x_m_cs, 220, x_m_clk, 220, color=FIELD, sw=1.8))
    p.append(line(x_m_cs, 214, x_m_cs, 226, color=FIELD, sw=1.8))
    p.append(line(x_m_clk, 214, x_m_clk, 226, color=FIELD, sw=1.8))
    p.append(text((x_m_cs + x_m_clk) / 2, 240, "t_CSS(MCU) = 50 ns", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(text((x_m_cs + x_m_clk) / 2, 258, "безпечний запас", size=10, color=MUTED, anchor="middle"))

    # Секція 2: Приймач (Slave за ізолятором)
    p.append(rect(450, 35, 360, 325, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(630, 60, "На вході веденого (після оптопари)", size=13, color=POS, bold=True, anchor="middle"))

    # Затримка CS: довгий спад через повільне вимкнення / RC (t_prop_CS = 65 ns)
    x_s_cs = 470 + (x_m_cs - 50) + 90   # зсув на +90px
    x_s_clk = 470 + (x_m_clk - 50) + 20 # зсув на +20px (швидший канал)

    # Ведений CS
    p.append(line(470, 100, x_s_cs, 100, color=CS_COL, sw=2.2))
    p.append(line(x_s_cs, 100, x_s_cs, 135, color=CS_COL, sw=2.2))
    p.append(line(x_s_cs, 135, 790, 135, color=CS_COL, sw=2.2))
    p.append(text(465, 118, "CS", size=11, color=CS_COL, bold=True, anchor="end"))

    # Ведений SCLK
    p.append(line(470, 185, x_s_clk, 185, color=CLK, sw=2.2))
    p.append(line(x_s_clk, 185, x_s_clk, 150, color=CLK, sw=2.2))
    p.append(line(x_s_clk, 150, x_s_clk + 40, 150, color=CLK, sw=2.2))
    p.append(line(x_s_clk + 40, 150, x_s_clk + 40, 185, color=CLK, sw=2.2))
    p.append(line(x_s_clk + 40, 185, 790, 185, color=CLK, sw=2.2))
    p.append(text(465, 168, "SCLK", size=11, color=CLK, bold=True, anchor="end"))

    # Затримка призвела до інверсії або стиснення t_CSS!
    # Пунктирні маркери
    p.append(line(x_s_clk, 90, x_s_clk, 200, color=POS, sw=1.2, dash="3,3"))
    p.append(line(x_s_cs, 90, x_s_cs, 200, color=POS, sw=1.2, dash="3,3"))

    # t_CSS реальний на веденому
    p.append(rect(x_s_clk, 205, x_s_cs - x_s_clk, 28, fill=WARN_BG, stroke=POS, sw=1.0, rx=3))
    p.append(text((x_s_clk + x_s_cs) / 2, 223, "t_CSS < 0 (SCLK раніше!)", size=10, color=POS, bold=True, anchor="middle"))
    p.append(text(630, 260, "Асиметрія: t_prop(CS) >> t_prop(CLK)", size=11, color=POS, bold=True, anchor="middle"))
    p.append(text(630, 278, "Перший такт пропущено: ведений ще в сні", size=10, color=MUTED, anchor="middle"))

    # Центральний блок ізолятора зі стрілками передачі
    p.append(rect(395, 120, 50, 80, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(text(420, 155, "Ізолятор", size=10, color="#92400e", bold=True, anchor="middle"))
    p.append(text(420, 172, "Skew", size=9, color="#92400e", anchor="middle"))
    p.append(arrow(370, 125, 465, 125, color=CS_COL, sw=1.8))
    p.append(arrow(370, 175, 465, 175, color=CLK, sw=1.8))

    # Нижній висновок
    p.append(text(W / 2, H - 22, "Через асиметрію затримок оптичних та цифрових ізоляторів t_CSS скорочується до критичного збою", size=12, color=INK, italic=True, anchor="middle"))

    render(os.path.join(OUT, "isolator-skew.svg"), W, H, *p,
           title="Вплив асиметрії затримок ізолятора на таймінг CS")


# ── 4. Апаратний NSS проти програмного GPIO з DMA ─────────────────────────────
def fig_hardware_nss_vs_gpio():
    W, H = 840, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=FILL, stroke=LINE, sw=1.0, rx=8))

    # Ліва половина: Апаратний NSS (проблеми)
    p.append(rect(30, 35, 370, 340, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(215, 60, "Апаратний NSS (Hardware Pulse / TXE)", size=13, color=POS, bold=True, anchor="middle"))

    # 1. Імпульс між байтами
    p.append(text(50, 90, "1. NSS Pulse між байтами пакету:", size=11, color=INK, bold=True, anchor="start"))
    # NSS лінія з підскоком
    p.append(line(50, 125, 150, 125, color=CS_COL, sw=2.0))
    p.append(line(150, 125, 150, 105, color=CS_COL, sw=2.0))
    p.append(line(150, 105, 180, 105, color=CS_COL, sw=2.0))
    p.append(line(180, 105, 180, 125, color=CS_COL, sw=2.0))
    p.append(line(180, 125, 280, 125, color=CS_COL, sw=2.0))
    p.append(text(165, 100, "глітч", size=9, color=POS, bold=True, anchor="middle"))
    p.append(text(330, 120, "Байт 1", size=10, color=MUTED, anchor="middle"))
    p.append(text(330, 136, "Байт 2", size=10, color=MUTED, anchor="middle"))
    p.append(text(215, 155, "Ведений скидає декодер посеред команди!", size=10, color=POS, anchor="middle"))

    # 2. Підйом по TXE до закінчення зсуву
    p.append(text(50, 195, "2. Підйом NSS по прапорцю TXE:", size=11, color=INK, bold=True, anchor="start"))
    p.append(line(50, 235, 220, 235, color=CS_COL, sw=2.0))
    p.append(line(220, 235, 220, 210, color=CS_COL, sw=2.0))
    p.append(line(220, 210, 380, 210, color=CS_COL, sw=2.0))
    p.append(text(220, 202, "TXE=1 (FIFO пусте)", size=10, color=POS, bold=True, anchor="middle"))

    # SCLK ще працює
    p.append(line(50, 275, 100, 275, color=CLK, sw=1.8))
    for i in range(5):
        cx = 100 + i * 35
        p.append(line(cx, 275, cx, 255, color=CLK, sw=1.8))
        p.append(line(cx, 255, cx + 17, 255, color=CLK, sw=1.8))
        p.append(line(cx + 17, 255, cx + 17, 275, color=CLK, sw=1.8))
        p.append(line(cx + 17, 275, cx + 35, 275, color=CLK, sw=1.8))
    p.append(text(310, 268, "SCLK ще тактує!", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(215, 305, "NSS піднято, коли зсувний регістр ще зайнятий", size=10, color=POS, anchor="middle"))
    p.append(text(215, 322, "→ втрата 8-го біта та порушення t_CSH", size=10, color=MUTED, anchor="middle"))

    # Права половина: Програмний GPIO + DMA (надійність)
    p.append(rect(440, 35, 370, 340, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(625, 60, "Програмний GPIO + перевірка BSY", size=13, color=FIELD, bold=True, anchor="middle"))

    # GPIO лінія
    x_g_fall = 470
    x_g_start_sclk = 520
    x_g_end_sclk = 720
    x_g_bsy_clr = 750
    x_g_rise = 770

    p.append(line(450, 110, x_g_fall, 110, color=CS_COL, sw=2.2))
    p.append(line(x_g_fall, 110, x_g_fall, 140, color=CS_COL, sw=2.2))
    p.append(line(x_g_fall, 140, x_g_rise, 140, color=CS_COL, sw=2.2))
    p.append(line(x_g_rise, 140, x_g_rise, 110, color=CS_COL, sw=2.2))
    p.append(line(x_g_rise, 110, 800, 110, color=CS_COL, sw=2.2))
    p.append(text(445, 125, "GPIO CS", size=10, color=CS_COL, bold=True, anchor="end"))

    # SCLK лінія
    p.append(line(450, 185, x_g_start_sclk, 185, color=CLK, sw=1.8))
    for i in range(5):
        cx = x_g_start_sclk + i * 40
        p.append(line(cx, 185, cx, 165, color=CLK, sw=1.8))
        p.append(line(cx, 165, cx + 20, 165, color=CLK, sw=1.8))
        p.append(line(cx + 20, 165, cx + 20, 185, color=CLK, sw=1.8))
        p.append(line(cx + 20, 185, cx + 40, 185, color=CLK, sw=1.8))
    p.append(line(x_g_end_sclk, 185, 800, 185, color=CLK, sw=1.8))
    p.append(text(445, 175, "SCLK", size=10, color=CLK, bold=True, anchor="end"))

    # Маркери затримок
    p.append(rect(x_g_fall, 210, x_g_start_sclk - x_g_fall, 24, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=3))
    p.append(text((x_g_fall + x_g_start_sclk) / 2, 226, "t_CSS", size=10, color=FIELD, bold=True, anchor="middle"))

    p.append(rect(x_g_end_sclk, 210, x_g_rise - x_g_end_sclk, 24, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=3))
    p.append(text((x_g_end_sclk + x_g_rise) / 2, 226, "t_CSH", size=10, color=FIELD, bold=True, anchor="middle"))

    # Пояснення кроків
    p.append(text(460, 260, "Послідовність роботи:", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(460, 280, "1. GPIO_ResetBits(CS) → активний рівень", size=10, color=INK, anchor="start"))
    p.append(text(460, 298, "2. Витримка t_CSS (інструкція або NOP)", size=10, color=INK, anchor="start"))
    p.append(text(460, 316, "3. Передача даних через DMA / FIFO", size=10, color=INK, anchor="start"))
    p.append(text(460, 334, "4. Очікування прапорця BSY = 0 (кінець зсуву)", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(460, 352, "5. GPIO_SetBits(CS) → деактивація", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "hardware-nss-vs-gpio.svg"), W, H, *p,
           title="Порівняння апаратного NSS та програмного GPIO керування CS")


if __name__ == "__main__":
    fig_timing_diagram()
    fig_premature_cs_abort()
    fig_isolator_skew()
    fig_hardware_nss_vs_gpio()
    print("All figures generated successfully.")
