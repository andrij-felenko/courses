# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#c9923f"
BROWN = "#b5732e"
DARK = "#2c3e50"
TIN = "#94a3b8"
SOLDER = "#7f8c8d"


# ── 1. eia-sizes-scale: Зіставлення типорозмірів від 2512 до 01005 ──────────
def fig_eia_sizes_scale():
    W, H = 860, 470
    p = []

    # Заголовок зверху
    p.append(rect(20, 16, 820, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(430, 42, "Двосистемні типорозміри SMD чіп-компонентів: Imperial EIA проти Metric EIA",
                  size=15, color=INK, bold=True))

    # Шкала порівняння типорозмірів (1 мм = 18 px)
    scale = 18.0
    items = [
        # code_imp, code_met, L_mm, W_mm, cx, power
        ("2512", "6432M", 6.4, 3.2, 85, "1–2 Вт"),
        ("2010", "5025M", 5.0, 2.5, 200, "0.75 Вт"),
        ("1206", "3216M", 3.2, 1.6, 305, "0.25 Вт"),
        ("0805", "2012M", 2.0, 1.25, 395, "0.125 Вт"),
        ("0603", "1608M", 1.6, 0.8, 480, "0.10 Вт"),
        ("0402", "1005M", 1.0, 0.5, 560, "0.063 Вт"),
        ("0201", "0603M", 0.6, 0.3, 635, "0.05 Вт"),
        ("01005", "0402M", 0.4, 0.2, 705, "0.03 Вт"),
        ("008004", "0201M", 0.25, 0.125, 780, "0.01 Вт"),
    ]

    base_y = 210

    for code_imp, code_met, l_mm, w_mm, cx, pwr in items:
        w_px = max(l_mm * scale, 5.0)
        h_px = max(w_mm * scale, 3.5)
        x = cx - w_px / 2.0
        y = base_y - h_px / 2.0

        term_w = min(w_px * 0.22, 12.0)
        if term_w >= 1.5 and w_px > 2 * term_w:
            # Лівий торець
            p.append(rect(x, y, term_w, h_px, fill=COPPER, stroke=BROWN, sw=0.8, rx=0))
            # Середина тіла
            p.append(rect(x + term_w, y, w_px - 2 * term_w, h_px, fill="#e2e8f0", stroke="#475569", sw=0.8, rx=0))
            # Правий торець
            p.append(rect(x + w_px - term_w, y, term_w, h_px, fill=COPPER, stroke=BROWN, sw=0.8, rx=0))
        else:
            # Для крихітних
            p.append(rect(x, y, w_px, h_px, fill="#e2e8f0", stroke="#475569", sw=0.8, rx=0))

        # Підписи під корпусом
        p.append(text(cx, base_y + 40, code_imp, size=12.5, color=INK, bold=True))
        p.append(text(cx, base_y + 56, code_met, size=10, color=MUTED))
        p.append(text(cx, base_y + 72, "%.2f×%.2f" % (l_mm, w_mm) if l_mm < 1.0 else "%.1f×%.1f" % (l_mm, w_mm), size=9.5, color="#64748b"))
        p.append(text(cx, base_y + 88, pwr, size=9.5, color=FIELD, bold=True))

    # Спільна базова лінія для візуального рівняння
    p.append(line(25, base_y + 26, 835, base_y + 26, color="#e2e8f0", sw=1))

    # Нижній блок: попередження про збіги кодів
    p.append(rect(40, 330, 780, 115, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=8))
    p.append(text(430, 355, "КРИТИЧНА ПАСТКА: Збіг дюймових і метричних назв", size=13.5, color=POS, bold=True))

    p.append(text(230, 385, "Imperial 0402 = 1.0 × 0.5 мм (Metric 1005M)", size=11, color=INK, bold=True))
    p.append(text(230, 403, "Рядовий монтаж, береться ручним паяльником", size=10.5, color=MUTED))
    p.append(text(230, 423, "Площа чіпа: 0.50 мм²", size=10.5, color=FIELD))

    p.append(line(430, 370, 430, 435, color="#fca5a5", sw=1.2, dash="4 4"))

    p.append(text(630, 385, "Metric 0402M = 0.4 × 0.2 мм (Imperial 01005)", size=11, color=POS, bold=True))
    p.append(text(630, 403, "Ультрамініатюрна піщинка, лише лазерний SMT", size=10.5, color=MUTED))
    p.append(text(630, 423, "Площа чіпа: 0.08 мм² (у 6.25 раза менша!)", size=10.5, color=POS))

    render(os.path.join(OUT, "eia-sizes-scale.svg"), W, H, *p,
           title="Зіставлення типорозмірів SMD від 2512 до 01005")


# ── 2. ipc7351-fillets-density: Анатомія галтелей та рівні щільності ──────────
def fig_ipc7351_fillets_density():
    W, H = 860, 480
    p = []

    # Заголовок
    p.append(rect(20, 15, 820, 40, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(430, 40, "Стандарт IPC-7351B: Анатомія галтелей паяного шва та 3 рівні щільності монтажу",
                  size=14, color=INK, bold=True))

    # ЛІВА СТОРОНА: Розріз чіпа та площадки з галтелями
    lx = 240
    by = 220

    # Плата текстоліт
    p.append(rect(40, by + 12, 380, 20, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=0))
    p.append(text(80, by + 26, "Плата (PCB)", size=10, color=MUTED))

    # Дві мідні площадки (pads)
    pad_w = 90
    pad_h = 10
    p.append(rect(lx - 150, by + 2, pad_w, pad_h, fill=COPPER, stroke=BROWN, sw=1.2, rx=0))
    p.append(rect(lx + 60, by + 2, pad_w, pad_h, fill=COPPER, stroke=BROWN, sw=1.2, rx=0))

    # Тіло SMD чіпа
    chip_w = 190
    chip_h = 75
    chip_x = lx - chip_w / 2
    chip_y = by - chip_h
    tw = 40

    # Торці та середина окремо, щоб rect не накладався
    p.append(rect(chip_x, chip_y, tw, chip_h, fill=TIN, stroke="#64748b", sw=1.2, rx=0))
    p.append(rect(chip_x + tw, chip_y, chip_w - 2 * tw, chip_h, fill="#e2e8f0", stroke="#334155", sw=1.4, rx=0))
    p.append(rect(chip_x + chip_w - tw, chip_y, tw, chip_h, fill=TIN, stroke="#64748b", sw=1.2, rx=0))

    p.append(text(lx, chip_y + 35, "SMD-компонент", size=13, color=INK, bold=True))
    p.append(text(lx, chip_y + 52, "(кераміка / резистивний шар)", size=10, color=MUTED))

    # Галтелі припою (Toe і Heel)
    # Ліва зовнішня галтель (Toe)
    p.append('<path d="M %d %d Q %d %d %d %d L %d %d Z" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (chip_x - 45, by + 2, chip_x - 10, by - 15, chip_x, chip_y + 25,
                chip_x, by + 2, SOLDER, "#475569"))
    # Ліва внутрішня галтель (Heel)
    p.append('<path d="M %d %d Q %d %d %d %d L %d %d Z" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (chip_x + tw + 25, by + 2, chip_x + tw + 8, by - 8, chip_x + tw, chip_y + 40,
                chip_x + tw, by + 2, SOLDER, "#475569"))

    # Права внутрішня галтель (Heel)
    p.append('<path d="M %d %d Q %d %d %d %d L %d %d Z" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (chip_x + chip_w - tw - 25, by + 2, chip_x + chip_w - tw - 8, by - 8, chip_x + chip_w - tw, chip_y + 40,
                chip_x + chip_w - tw, by + 2, SOLDER, "#475569"))
    # Права зовнішня галтель (Toe)
    p.append('<path d="M %d %d Q %d %d %d %d L %d %d Z" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (chip_x + chip_w + 45, by + 2, chip_x + chip_w + 10, by - 15, chip_x + chip_w, chip_y + 25,
                chip_x + chip_w, by + 2, SOLDER, "#475569"))

    # Вказівники на елементи галтелей (рознесені високо вгору)
    p.append(line(chip_x - 22, by - 10, chip_x - 22, 115, color=POS, sw=1.4))
    p.append(text(chip_x - 22, 90, "Toe (Носок галтелі)", size=11, color=POS, bold=True))
    p.append(text(chip_x - 22, 105, "Припуск JT", size=9.5, color=MUTED))

    p.append(line(chip_x + tw + 12, by - 6, chip_x + tw + 12, 115, color=NEG, sw=1.4))
    p.append(text(chip_x + tw + 12, 90, "Heel (П'ята галтелі)", size=11, color=NEG, bold=True))
    p.append(text(chip_x + tw + 12, 105, "Припуск JH", size=9.5, color=MUTED))

    # Розмірні лінії знизу
    dim_y = by + 50
    p.append(line(lx - 150, dim_y, lx + 150, dim_y, color=INK, sw=1.2))
    p.append(line(lx - 150, dim_y - 6, lx - 150, dim_y + 6, color=INK, sw=1.2))
    p.append(line(lx + 150, dim_y - 6, lx + 150, dim_y + 6, color=INK, sw=1.2))
    p.append(text(lx, dim_y + 16, "Z_max (Загальний зовнішній габарит площадок)", size=10.5, color=INK))

    dim_y2 = by + 80
    p.append(line(lx - 60, dim_y2, lx + 60, dim_y2, color=INK, sw=1.2))
    p.append(line(lx - 60, dim_y2 - 6, lx - 60, dim_y2 + 6, color=INK, sw=1.2))
    p.append(line(lx + 60, dim_y2 - 6, lx + 60, dim_y2 + 6, color=INK, sw=1.2))
    p.append(text(lx, dim_y2 + 16, "G_min (Внутрішній зазор між площадками)", size=10.5, color=INK))

    # ПРАВА СТОРОНА: 3 Рівні щільності монтажу
    rx = 460
    cards = [
        (75, "Density Level A — Most Land Protrusion",
         "Максимальні припуски: Toe=+0.55, Heel=+0.10, Side=+0.05 мм",
         "Призначення: військова техніка, вібрації, ручне паяння та ремонт",
         "#eff6ff", "#3b82f6", NEG),
        (200, "Density Level B — Nominal Land Protrusion",
         "Номінальні припуски: Toe=+0.35, Heel=+0.00, Side=-0.05 мм",
         "Призначення: промисловий стандарт для масового автоматизованого SMT",
         "#f0fdf4", "#22c55e", FIELD),
        (325, "Density Level C — Least Land Protrusion",
         "Мінімальні припуски: Toe=+0.15, Heel=-0.05, Side=-0.10 мм",
         "Призначення: смартфони, портативна техніка, надщільна компоновка",
         "#fefce8", "#eab308", "#b45309"),
    ]

    for cy_card, title_c, dims_c, usage_c, fill_c, stroke_c, text_c in cards:
        p.append(rect(rx, cy_card, 370, 110, fill=fill_c, stroke=stroke_c, sw=1.4, rx=8))
        p.append(text(rx + 185, cy_card + 24, title_c, size=11.5, color=text_c, bold=True))
        p.append(text(rx + 185, cy_card + 50, dims_c, size=10, color=INK))
        p.append(text(rx + 185, cy_card + 72, usage_c, size=9.5, color=MUTED))
        p.append(text(rx + 185, cy_card + 92, "Courtyard Excess (зона безпеки навколо): %.2f мм" %
                      (0.50 if "A" in title_c else 0.25 if "B" in title_c else 0.12),
                      size=9.5, color=text_c, bold=True))

    render(os.path.join(OUT, "ipc7351-fillets-density.svg"), W, H, *p,
           title="IPC-7351B: Анатомія галтелей та рівні щільності")


# ── 3. esl-current-loop: Контур струму та індуктивність 0603 проти 0306 ───────
def fig_esl_current_loop():
    W, H = 860, 430
    p = []

    # Заголовок
    p.append(rect(20, 15, 820, 40, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(430, 40, "Паразитна індуктивність ESL: Стандартний 0603 проти Wide-Terminal 0306",
                  size=14, color=INK, bold=True))

    # ЛІВА ПАНЕЛЬ: Стандартний 0603
    p.append(rect(40, 75, 370, 335, fill="#ffffff", stroke="#cbd5e1", sw=1.4, rx=8))
    p.append(text(225, 102, "Стандартний чіп 0603 (1608M)", size=14, color=INK, bold=True))
    p.append(text(225, 122, "Виводи по вузьких торцях (довгий шлях)", size=11, color=MUTED))

    # Чіп 0603
    p.append(rect(155, 150, 28, 70, fill=COPPER, stroke=BROWN, sw=1, rx=0))
    p.append(rect(183, 150, 84, 70, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=0))
    p.append(rect(267, 150, 28, 70, fill=COPPER, stroke=BROWN, sw=1, rx=0))
    p.append(text(225, 190, "L = 1.6 мм", size=11, color=INK))

    # Стрілка струму (довга петля)
    p.append('<path d="M 170 235 L 170 265 L 280 265 L 280 235" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5 4"/>' % POS)
    p.append(arrow(220, 265, 235, 265, color=POS, sw=2.5))
    p.append(text(225, 290, "Велика площа контуру струму", size=11, color=POS, bold=True))
    p.append(text(225, 310, "Довгий і вузький провідник", size=10.5, color=MUTED))

    # Характеристики 0603
    p.append(rect(60, 335, 330, 60, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(225, 355, "Паразитна індуктивність ESL ≈ 0.6 – 0.8 нГн", size=11, color=POS, bold=True))
    p.append(text(225, 375, "Резонанс SRF (100 нФ) ≈ 18 МГц", size=10.5, color=INK))

    # ПРАВА ПАНЕЛЬ: Зворотна геометрія 0306
    p.append(rect(450, 75, 370, 335, fill="#ffffff", stroke="#cbd5e1", sw=1.4, rx=8))
    p.append(text(635, 102, "Wide-Terminal / Зворотна геометрія 0306", size=14, color=FIELD, bold=True))
    p.append(text(635, 122, "Виводи по широких сторонах (короткий шлях)", size=11, color=MUTED))

    # Чіп 0306 (повернутий: L=0.8, W=1.6)
    p.append(rect(565, 150, 140, 18, fill=COPPER, stroke=BROWN, sw=1, rx=0))
    p.append(rect(565, 168, 140, 34, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=0))
    p.append(rect(565, 202, 140, 18, fill=COPPER, stroke=BROWN, sw=1, rx=0))
    p.append(text(635, 188, "L = 0.8 мм (шлях струму)", size=11, color=FIELD, bold=True))

    # Стрілка струму (стиснута петля)
    p.append('<path d="M 590 235 L 590 248 L 680 248 L 680 235" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5 4"/>' % FIELD)
    p.append(arrow(630, 248, 645, 248, color=FIELD, sw=2.5))
    p.append(text(635, 275, "Стиснута петля струму (у 4 рази менша)", size=11, color=FIELD, bold=True))
    p.append(text(635, 295, "Широкий і ультракороткий провідник", size=10.5, color=MUTED))

    # Характеристики 0306
    p.append(rect(470, 335, 330, 60, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(635, 355, "Паразитна індуктивність ESL ≈ 0.15 – 0.20 нГн", size=11, color=FIELD, bold=True))
    p.append(text(635, 375, "Резонанс SRF (100 нФ) ≈ 40 МГц (у 2.2 рази вище)", size=10.5, color=INK))

    render(os.path.join(OUT, "esl-current-loop.svg"), W, H, *p,
           title="ESL: стандартний 0603 проти Wide-Terminal 0306")


# ── 4. resistor-power-derating: Потужність розсіювання та крива дератингу ──────
def fig_resistor_power_derating():
    W, H = 860, 440
    p = []

    # Заголовок
    p.append(rect(20, 15, 820, 40, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(430, 40, "Теплові ліміти потужності SMD-резисторів та крива дератингу (IPC / EIA-575)",
                  size=14, color=INK, bold=True))

    # ЛІВА ЧАСТИНА: Графік дератингу
    gx = 80
    gy = 340
    gw = 350
    gh = 230

    # Осі графіка
    p.append(line(gx, gy, gx + gw + 20, gy, color=INK, sw=1.8))
    p.append(line(gx, gy, gx, gy - gh - 20, color=INK, sw=1.8))

    # Стрілки
    p.append(arrow(gx + gw + 10, gy, gx + gw + 25, gy, color=INK, sw=1.8))
    p.append(arrow(gx, gy - gh - 10, gx, gy - gh - 25, color=INK, sw=1.8))

    # Підписи осей
    p.append(text(gx + gw - 20, gy + 32, "Температура T_amb (°C)", size=11, color=INK, bold=True))
    p.append(text(gx + 30, gy - gh - 28, "Потужність P / P_nom (%)", size=11, color=INK, bold=True))

    # Розмітка сітки та значення
    # Y: 0%, 50%, 100%
    p.append(line(gx - 4, gy, gx, gy, color=INK, sw=1.4))
    p.append(text(gx - 18, gy + 4, "0%", size=10, color=MUTED))

    p.append(line(gx - 4, gy - gh / 2, gx, gy - gh / 2, color=INK, sw=1.4))
    p.append(line(gx, gy - gh / 2, gx + gw, gy - gh / 2, color="#e2e8f0", sw=1, dash="4 4"))
    p.append(text(gx - 24, gy - gh / 2 + 4, "50%", size=10, color=MUTED))

    p.append(line(gx - 4, gy - gh, gx, gy - gh, color=INK, sw=1.4))
    p.append(line(gx, gy - gh, gx + gw, gy - gh, color="#e2e8f0", sw=1, dash="4 4"))
    p.append(text(gx - 28, gy - gh + 4, "100%", size=10, color=MUTED))

    # X: 0, 70°C, 125°C, 155°C
    x_70 = gx + gw * (70.0 / 170.0)
    x_155 = gx + gw * (155.0 / 170.0)

    p.append(line(x_70, gy, x_70, gy + 6, color=INK, sw=1.4))
    p.append(text(x_70, gy + 20, "70 °C", size=10.5, color=FIELD, bold=True))
    p.append(line(x_70, gy, x_70, gy - gh, color="#bbf7d0", sw=1.2, dash="3 3"))

    p.append(line(x_155, gy, x_155, gy + 6, color=INK, sw=1.4))
    p.append(text(x_155, gy + 20, "155 °C (T_max)", size=10.5, color=POS, bold=True))
    p.append(line(x_155, gy, x_155, gy - gh, color="#fecaca", sw=1.2, dash="3 3"))

    # Крива дератингу (товста лінія)
    p.append(line(gx, gy - gh, x_70, gy - gh, color=FIELD, sw=3.0))
    p.append(line(x_70, gy - gh, x_155, gy, color=POS, sw=3.0))

    # Точки перегину
    p.append(circle(x_70, gy - gh, 4.5, fill=FIELD, stroke=INK, sw=1.2))
    p.append(circle(x_155, gy, 4.5, fill=POS, stroke=INK, sw=1.2))

    p.append(text(x_70 - 45, gy - gh - 12, "100% P_nom до 70 °C", size=10, color=FIELD, bold=True))
    p.append(text(x_70 + 75, gy - gh / 2 - 10, "Зниження (Derating)", size=10, color=POS, bold=True))

    # ПРАВА ЧАСТИНА: Таблиця лімітів потужності та теплового розсіювання
    tx = 490
    p.append(rect(tx, 75, 340, 335, fill="#ffffff", stroke="#cbd5e1", sw=1.4, rx=8))
    p.append(text(tx + 170, 102, "Номінальна потужність SMD-резисторів", size=13, color=INK, bold=True))
    p.append(text(tx + 170, 120, "(при T_amb ≤ 70 °C на стандартній FR-4)", size=10.5, color=MUTED))

    # Рядки таблиці
    rows = [
        ("0201 (0603M)", "1/20 Вт (0.050 Вт)", "25 В", "#f8fafc"),
        ("0402 (1005M)", "1/16 Вт (0.063 Вт)", "50 В", "#ffffff"),
        ("0603 (1608M)", "1/10 Вт (0.100 Вт)", "75 В", "#f8fafc"),
        ("0805 (2012M)", "1/8 Вт (0.125 Вт)", "150 В", "#ffffff"),
        ("1206 (3216M)", "1/4 Вт (0.250 Вт)", "200 В", "#f8fafc"),
        ("1210 (3225M)", "1/2 Вт (0.500 Вт)", "200 В", "#ffffff"),
        ("2010 (5025M)", "3/4 Вт (0.750 Вт)", "200 В", "#f8fafc"),
        ("2512 (6432M)", "1 – 2 Вт (з міддю)", "250 В", "#ffffff"),
    ]

    # Шапка таблиці
    p.append(rect(tx + 12, 135, 316, 24, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=3))
    p.append(text(tx + 55, 151, "Корпус", size=10.5, color=INK, bold=True))
    p.append(text(tx + 170, 151, "Потужність P_nom", size=10.5, color=INK, bold=True))
    p.append(text(tx + 285, 151, "U_max", size=10.5, color=INK, bold=True))

    for i, (pkg, pwr, volt, bg_row) in enumerate(rows):
        ry = 162 + i * 24
        p.append(rect(tx + 12, ry, 316, 22, fill=bg_row, stroke="#e2e8f0", sw=0.8, rx=0))
        p.append(text(tx + 55, ry + 15, pkg, size=10, color=INK))
        p.append(text(tx + 170, ry + 15, pwr, size=10, color=FIELD if "1 – 2" in pwr else INK, bold=("1 – 2" in pwr)))
        p.append(text(tx + 285, ry + 15, volt, size=10, color=MUTED))

    # Нижній висновок про тепловий зв'язок з міддю
    p.append(rect(tx + 12, 360, 316, 40, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(tx + 170, 376, "> 85% тепла скидається через мідь плати", size=10, color=FIELD, bold=True))
    p.append(text(tx + 170, 392, "Площа полігона PCB — головний радіатор SMD", size=9.5, color=MUTED))

    render(os.path.join(OUT, "resistor-power-derating.svg"), W, H, *p,
           title="Теплові ліміти потужності та дератинг SMD")


if __name__ == "__main__":
    fig_eia_sizes_scale()
    fig_ipc7351_fillets_density()
    fig_esl_current_loop()
    fig_resistor_power_derating()
    print("OK: All 4 figures generated successfully in", OUT)
