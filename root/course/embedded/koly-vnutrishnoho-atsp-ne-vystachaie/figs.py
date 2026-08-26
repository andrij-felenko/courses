# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. internal-vs-external-noise: Внутрішній АЦП МК проти зовнішнього АЦП ───
def fig_internal_vs_external_noise():
    W, H = 900, 430
    p = []

    # Ліва половина — кристал мікроконтролера
    p.append(rect(30, 45, 405, 320, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(232, 72, "Вбудований АЦП: спільний кристал МК", size=14, color=POS, bold=True))
    p.append(text(232, 92, "Кремнієва підкладка зв'язує цифру та аналог", size=11, color=MUTED))

    # Цифрове ядро МК
    p.append(rect(50, 115, 160, 110, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(130, 138, "Цифрове ядро МК", size=12, color=POS, bold=True))
    p.append(text(130, 158, "CPU 80–480 МГц", size=10.5, color=INK))
    p.append(text(130, 176, "Шини Flash, RAM, DMA", size=10.5, color=INK))
    p.append(text(130, 196, "Імпульси di/dt > 10⁹ А/с", size=10, color=POS))

    # Вбудований SAR АЦП
    p.append(rect(255, 115, 160, 110, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(335, 138, "Вбудований SAR АЦП", size=12, color=INK, bold=True))
    p.append(text(335, 158, "Номінал: 12 бітів", size=10.5, color=INK))
    p.append(text(335, 176, "Ємнісний ЦАП (CDAC)", size=10.5, color=INK))
    p.append(text(335, 196, "Шумна опора VDDA", size=10, color=POS))

    # Зв'язок шумів через підкладку
    p.append(arrow(210, 170, 255, 170, color=POS, sw=2))
    p.append(text(232, 160, "Шум", size=10, color=POS, bold=True))

    # Наслідки внизу зліва
    b_left, _, _ = textbox(232, 290,
                           "Завади підкладки (Substrate Noise) + дзвін шини живлення\n"
                           "Реальна розрядність ENOB: лише 9.0–10.2 біта\n"
                           "Шум вихідного коду: ±4–12 LSB (непридатний для < 1 мВ)",
                           size=11, fill="#ffffff", stroke=POS, min_w=370)
    p.append(b_left)

    # Права половина — зовнішній прецизійний АЦП
    p.append(rect(465, 45, 405, 320, fill="#eefaf1", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(667, 72, "Зовнішній виділений АЦП", size=14, color=FIELD, bold=True))
    p.append(text(667, 92, "Повна фізична ізоляція від цифрового процесора", size=11, color=MUTED))

    # Зовнішнє прецизійне джерело Vref
    p.append(rect(485, 115, 160, 110, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(565, 138, "Прецизійна опора Vref", size=12, color=FIELD, bold=True))
    p.append(text(565, 158, "Дрейф < 3 ppm/°C", size=10.5, color=INK))
    p.append(text(565, 176, "Шум < 1.5 мкВ p-p", size=10.5, color=INK))
    p.append(text(565, 196, "Kelvin-підключення", size=10, color=FIELD))

    # Ядро зовнішнього АЦП (Sigma-Delta / SAR)
    p.append(rect(690, 115, 160, 110, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(770, 138, "Зовнішнє ядро АЦП", size=12, color=FIELD, bold=True))
    p.append(text(770, 158, "16–24 біти (ΣΔ або SAR)", size=10.5, color=INK))
    p.append(text(770, 176, "Вбудований малошумний PGA", size=10.5, color=INK))
    p.append(text(770, 196, "Диференційний вхід", size=10, color=FIELD))

    p.append(arrow(645, 170, 690, 170, color=FIELD, sw=2))
    p.append(text(667, 160, "Vref", size=10, color=FIELD, bold=True))

    # Наслідки внизу справа
    b_right, _, _ = textbox(667, 290,
                            "Чиста кремнієва підкладка без потужних цифрових ядер\n"
                            "Реальна розрядність ENOB: 16–22.5 біта (шум < 1 мкВ RMS)\n"
                            "Стабільність відліків: вимірювання мікровольтів без дрижання",
                            size=11, fill="#ffffff", stroke=FIELD, min_w=370)
    p.append(b_right)

    # Загальний підсумок знизу
    b_bot, _, _ = textbox(W / 2, 395,
                          "Зовнішній АЦП переносить перетворення на чистий кремній: власне стабільне живлення, виділене Vref і нуль цифрових наведень ядра МК.",
                          size=11.5, stroke=MUTED, fill="#ffffff", min_w=840)
    p.append(b_bot)

    render(os.path.join(OUT, "internal-vs-external-noise.svg"), W, H, *p,
           title="Порівняння шумового середовища: вбудований АЦП проти зовнішнього")


# ── 2. adc-architectures-tradeoff: Карта архітектур АЦП ──────────────────────
def fig_adc_architectures_tradeoff():
    W, H = 900, 450
    p = []

    # Вісі координат
    p.append(arrow(85, 365, 855, 365, color=LINE, sw=2))  # X: Швидкість
    p.append(text(845, 390, "Частота вибірки (fs)", size=12, color=INK, bold=True))

    p.append(arrow(85, 365, 85, 45, color=LINE, sw=2))   # Y: Розрядність
    p.append(text(85, 35, "Розрядність (біти)", size=12, color=INK, bold=True))

    # Позначки по X (Швидкість)
    x_ticks = [(150, "10 SPS"), (280, "10 kSPS"), (470, "1 MSPS"), (650, "10 MSPS"), (800, "1 GSPS")]
    for x_pos, label in x_ticks:
        p.append(line(x_pos, 360, x_pos, 370, color=MUTED, sw=1.2))
        p.append(text(x_pos, 385, label, size=10, color=MUTED))

    # Позначки по Y (Розрядність)
    y_ticks = [(315, "10 біт"), (245, "14 біт"), (175, "18 біт"), (90, "24 біти")]
    for y_pos, label in y_ticks:
        p.append(line(80, y_pos, 90, y_pos, color=MUTED, sw=1.2))
        p.append(text(50, y_pos + 4, label, size=10, color=MUTED, anchor="end"))

    # Зона 1: Sigma-Delta (ΣΔ)
    p.append(rect(100, 60, 235, 290, fill="#eefaf1", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(217, 85, "Sigma-Delta (ΣΔ) АЦП", size=13, color=FIELD, bold=True))
    p.append(text(217, 105, "16–24 біти, 10 SPS–250 kSPS", size=10.5, color=INK))
    p.append(text(217, 132, "• Тензомості та ваги (ADS1232)", size=10, color=MUTED))
    p.append(text(217, 154, "• Термопари, RTD PT100 (ADS1220)", size=10, color=MUTED))
    p.append(text(217, 176, "• ЕКГ / Біопотенціали (ADS1298)", size=10, color=MUTED))
    p.append(text(217, 198, "• Прецизійні вольтметри (AD7124)", size=10, color=MUTED))
    p.append(text(217, 230, "Формування шуму (Noise Shaping)", size=10, color=FIELD, bold=True))
    p.append(text(217, 250, "Цифрова фільтрація (Sinc3/4)", size=10, color=FIELD))
    p.append(text(217, 275, "Гранична точність для", size=9.5, color=INK))
    p.append(text(217, 293, "повільних фізичних процесів", size=9.5, color=INK))
    p.append(text(217, 325, "Шум квантування витіснено у ВЧ", size=9, color=MUTED, italic=True))

    # Зона 2: Послідовне наближення (Зовнішній SAR)
    p.append(rect(350, 60, 245, 185, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(472, 85, "Зовнішній SAR АЦП", size=13, color=NEG, bold=True))
    p.append(text(472, 105, "14–18 бітів, 100 kSPS–10 MSPS", size=10.5, color=INK))
    p.append(text(472, 130, "• Фазовий облік U/I (AD7606)", size=10, color=MUTED))
    p.append(text(472, 150, "• Керування двигунами (FOC)", size=10, color=MUTED))
    p.append(text(472, 170, "• Віброаналіз і БПФ (LTC2387)", size=10, color=MUTED))
    p.append(text(472, 192, "• Одночасне семплювання (Simultaneous)", size=10, color=MUTED))
    p.append(text(472, 222, "Нульова затримка (Zero Latency)", size=10, color=NEG, bold=True))

    # Зона 2б: Вбудований АЦП МК (в окремій зоні нижче)
    p.append(rect(350, 255, 245, 95, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(472, 277, "Вбудований АЦП МК (SAR)", size=11.5, color=POS, bold=True))
    p.append(text(472, 296, "12 біт номінал (ENOB 9–10 біт)", size=10, color=POS))
    p.append(text(472, 316, "0.5–2 MSPS (послідовний MUX)", size=9.5, color=MUTED))
    p.append(text(472, 334, "Контроль батареї, прості потенціометри", size=9, color=MUTED))

    # Зона 3: Конвеєрні / Flash АЦП (Pipeline)
    p.append(rect(610, 155, 235, 195, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(727, 180, "Pipeline / Flash АЦП", size=12.5, color=INK, bold=True))
    p.append(text(727, 200, "8–14 бітів, 10 MSPS–1 GSPS+", size=10, color=INK))
    p.append(text(727, 230, "• Програмне радіо (SDR)", size=10, color=MUTED))
    p.append(text(727, 252, "• Цифрові осцилографи", size=10, color=MUTED))
    p.append(text(727, 274, "• Радари, LiDAR та оптика", size=10, color=MUTED))
    p.append(text(727, 305, "Екстремальна смуга частот", size=10, color=INK, bold=True))
    p.append(text(727, 325, "Паралельна конвеєризація", size=9.5, color=MUTED))

    # Підсумок
    b_bot, _, _ = textbox(W / 2, 425,
                          "Вибір архітектури диктується фізикою задачі: ΣΔ дає граничну роздільну здатність для повільних процесів, а SAR — швидкість та точний тайминг фаз.",
                          size=11, stroke=MUTED, fill="#ffffff", min_w=850)
    p.append(b_bot)

    render(os.path.join(OUT, "adc-architectures-tradeoff.svg"), W, H, *p,
           title="Ландшафт технологій АЦП: баланс розрядності, швидкості та архітектури")


# ── 3. simultaneous-vs-multiplexed: Фазова похибка мультиплексованого АЦП ───
def fig_simultaneous_vs_multiplexed():
    W, H = 900, 440
    p = []

    # Верхній блок — Мультиплексований АЦП (Вбудований МК)
    p.append(rect(30, 45, 840, 170, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(180, 70, "1. Послідовний мультиплексований АЦП (типовий МК)", size=13, color=POS, bold=True))

    # Схема каналів і комутатора
    p.append(rect(50, 95, 110, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(105, 114, "Канал U(t) [Напруга]", size=10, color=INK, bold=True))

    p.append(rect(50, 140, 110, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(105, 159, "Канал I(t) [Струм]", size=10, color=INK, bold=True))

    p.append(line(160, 110, 200, 120, color=LINE, sw=1.5))
    p.append(line(160, 155, 200, 145, color=LINE, sw=1.5))

    # MUX блок
    p.append(rect(200, 105, 60, 55, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(text(230, 137, "MUX", size=12, color=POS, bold=True))

    # S/H + ADC
    p.append(arrow(260, 132, 295, 132, color=LINE, sw=1.5))
    p.append(rect(295, 105, 90, 55, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(text(340, 128, "Один T/H", size=11, color=INK, bold=True))
    p.append(text(340, 146, "+ Одне ядро", size=10, color=MUTED))

    # Часова шкала дискретизації мультиплексу
    p.append(line(420, 140, 840, 140, color=LINE, sw=1.5))
    p.append(arrow(830, 140, 850, 140, color=LINE, sw=1.5))
    p.append(text(845, 158, "Час t", size=10, color=MUTED))

    # Відліки U і I з часовим зсувом Δt
    p.append(circle(480, 110, 5, fill=POS, stroke=INK, sw=1.2))
    p.append(line(480, 115, 480, 140, color=POS, sw=1.2, dash="3 3"))
    p.append(text(480, 98, "U(t₀)", size=10.5, color=POS, bold=True))

    p.append(circle(550, 170, 5, fill=NEG, stroke=INK, sw=1.2))
    p.append(line(550, 140, 550, 165, color=NEG, sw=1.2, dash="3 3"))
    p.append(text(550, 188, "I(t₀ + Δt)", size=10.5, color=NEG, bold=True))

    # Стрілка зсуву Δt
    p.append(line(480, 130, 550, 130, color=POS, sw=1.5))
    p.append(text(515, 123, "Зсув Δt", size=10, color=POS, bold=True))

    b_mux_err, _, _ = textbox(700, 105,
                              "Штучний фазовий зсув: Δφ = 2·π·f·Δt\n"
                              "Створює фальшиву похибку активної\n"
                              "потужності P = U · I · cos(φ ± Δφ)",
                              size=10.5, fill="#ffffff", stroke=POS, min_w=240)
    p.append(b_mux_err)

    # Нижній блок — Одночасне семплювання (Simultaneous Sampling)
    p.append(rect(30, 230, 840, 170, fill="#eefaf1", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(215, 255, "2. Справжнє одночасне семплювання (AD7606 / ADS8588S)", size=13, color=FIELD, bold=True))

    # Канал U(t) зі своїм T/H
    p.append(rect(50, 280, 110, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(105, 299, "Канал U(t) [Напруга]", size=10, color=INK, bold=True))

    p.append(arrow(160, 295, 200, 295, color=LINE, sw=1.5))
    p.append(rect(200, 278, 90, 35, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(245, 300, "T/H Блок 1", size=10.5, color=FIELD, bold=True))

    # Канал I(t) зі своїм T/H
    p.append(rect(50, 335, 110, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(105, 354, "Канал I(t) [Струм]", size=10, color=INK, bold=True))

    p.append(arrow(160, 350, 200, 350, color=LINE, sw=1.5))
    p.append(rect(200, 333, 90, 35, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(245, 355, "T/H Блок 2", size=10.5, color=FIELD, bold=True))

    # Лінія синхронного запуску CONVST
    p.append(line(245, 255, 245, 278, color=FIELD, sw=2))
    p.append(line(245, 313, 245, 333, color=FIELD, sw=2))
    p.append(text(295, 268, "Імпульс CONVST (одночасна фіксація)", size=10, color=FIELD, bold=True))

    # Паралельні ядра АЦП
    p.append(arrow(290, 295, 325, 295, color=LINE, sw=1.5))
    p.append(arrow(290, 350, 325, 350, color=LINE, sw=1.5))
    p.append(rect(325, 278, 80, 90, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(365, 318, "Ядра", size=11, color=FIELD, bold=True))
    p.append(text(365, 335, "АЦП", size=11, color=FIELD, bold=True))

    # Часова шкала без затримки
    p.append(line(430, 325, 840, 325, color=LINE, sw=1.5))
    p.append(arrow(830, 325, 850, 325, color=LINE, sw=1.5))
    p.append(text(845, 343, "Час t", size=10, color=MUTED))

    p.append(circle(520, 295, 5, fill=POS, stroke=INK, sw=1.2))
    p.append(circle(520, 355, 5, fill=NEG, stroke=INK, sw=1.2))
    p.append(line(520, 295, 520, 355, color=FIELD, sw=2, dash="3 3"))
    p.append(text(520, 283, "U(t₀)", size=10.5, color=POS, bold=True))
    p.append(text(520, 373, "I(t₀)", size=10.5, color=NEG, bold=True))
    p.append(text(565, 320, "Δt = 0 нс (Синфазно)", size=10.5, color=FIELD, bold=True))

    b_sim_ok, _, _ = textbox(720, 290,
                             "Нульовий апаратний перекіс фаз\n"
                             "Ідеальний розрахунок cos(φ), RMS\n"
                             "та вищих гармонік у трифазній мережі",
                             size=10.5, fill="#ffffff", stroke=FIELD, min_w=240)
    p.append(b_sim_ok)

    # Загальний підсумок знизу
    b_bot, _, _ = textbox(W / 2, 418,
                          "Мультиплексор вбудованого АЦП створює фазову часову затримку між каналами; зовнішні багатоканальні SAR фіксують усі канали в одну мить.",
                          size=11, stroke=MUTED, fill="#ffffff", min_w=850)
    p.append(b_bot)

    render(os.path.join(OUT, "simultaneous-vs-multiplexed.svg"), W, H, *p,
           title="Походження фазової похибки: мультиплексування проти синхронного семплювання")


# ── 4. external-adc-precision-layout: Схемотехніка та трасування ─────────────
def fig_external_adc_precision_layout():
    W, H = 900, 440
    p = []

    # Весь блок друкованої плати
    p.append(rect(30, 45, 840, 350, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))

    # Зона 1: Чиста аналогова частина (ліворуч)
    p.append(rect(45, 60, 340, 320, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(215, 82, "Аналогова зона (Clean Analog)", size=13, color=NEG, bold=True))

    # Давач (тензоміст / RTD)
    p.append(rect(60, 110, 110, 80, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(115, 135, "Давач", size=11, color=INK, bold=True))
    p.append(text(115, 153, "Тензоміст /", size=10, color=MUTED))
    p.append(text(115, 169, "RTD PT100", size=10, color=MUTED))

    # Диференційний RC фільтр
    p.append(rect(200, 110, 165, 80, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(282, 130, "Диференційний RC-фільтр", size=10.5, color=NEG, bold=True))
    p.append(text(282, 148, "R_filt (0.1% симетрія)", size=9.5, color=INK))
    p.append(text(282, 164, "C_diff = 10 · C_cm (C0G/NP0)", size=9.5, color=INK))
    p.append(text(282, 180, "Придушення синфазного шуму", size=9, color=MUTED))

    p.append(arrow(170, 150, 200, 150, color=NEG, sw=1.5))

    # Джерело Vref
    p.append(rect(60, 220, 305, 140, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(212, 242, "Прецизійне джерело Vref (ADR4525 / REF5025)", size=11, color=NEG, bold=True))
    p.append(text(212, 262, "• Температурний дрейф: < 3 ppm/°C", size=10, color=INK))
    p.append(text(212, 280, "• Kelvin Connection (Force/Sense до пінів АЦП)", size=10, color=NEG, bold=True))
    p.append(text(212, 298, "• Блокувальні конденсатори: 0.1 мкФ C0G + 10 мкФ X7R", size=10, color=INK))
    p.append(text(212, 316, "• Окрема чиста аналогова шина живлення LDO", size=10, color=INK))
    p.append(text(212, 342, "Суцільний суміжний шар GND під усім трактом", size=10, color=FIELD, bold=True))

    # Зона 2: ЧИП Зовнішнього АЦП (по центру)
    p.append(rect(410, 100, 140, 240, fill="#ffffff", stroke=FIELD, sw=2.2, rx=6))
    p.append(text(480, 125, "Зовнішній АЦП", size=12, color=FIELD, bold=True))
    p.append(text(480, 143, "(ADS1220 / AD7606)", size=10, color=MUTED))

    # Входи АЦП зліва
    p.append(arrow(365, 150, 410, 150, color=NEG, sw=1.8))
    p.append(text(388, 140, "AIN+", size=9.5, color=NEG, bold=True))
    p.append(arrow(365, 170, 410, 170, color=NEG, sw=1.8))
    p.append(text(388, 185, "AIN−", size=9.5, color=NEG, bold=True))

    p.append(arrow(365, 270, 410, 270, color=NEG, sw=1.8))
    p.append(text(388, 260, "REFP", size=9.5, color=NEG, bold=True))
    p.append(arrow(365, 290, 410, 290, color=NEG, sw=1.8))
    p.append(text(388, 305, "REFN", size=9.5, color=NEG, bold=True))

    # Виходи АЦП справа
    p.append(arrow(550, 160, 600, 160, color=POS, sw=1.8))
    p.append(text(575, 150, "SCLK", size=9.5, color=POS, bold=True))
    p.append(arrow(600, 185, 550, 185, color=POS, sw=1.8))
    p.append(text(575, 175, "MOSI", size=9.5, color=POS, bold=True))
    p.append(arrow(550, 210, 600, 210, color=POS, sw=1.8))
    p.append(text(575, 200, "MISO", size=9.5, color=POS, bold=True))
    p.append(arrow(600, 235, 550, 235, color=POS, sw=1.8))
    p.append(text(575, 225, "CS", size=9.5, color=POS, bold=True))
    p.append(arrow(550, 260, 600, 260, color=POS, sw=1.8))
    p.append(text(575, 250, "DRDY", size=9.5, color=POS, bold=True))

    # Зона 3: Цифрова частина МК (праворуч)
    p.append(rect(600, 60, 255, 320, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(727, 82, "Цифрова зона (MCU Domain)", size=13, color=POS, bold=True))

    p.append(rect(620, 120, 215, 180, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(727, 145, "Мікроконтролер (MCU)", size=12, color=POS, bold=True))
    p.append(text(727, 168, "SPI Контролер + DMA", size=10.5, color=INK))
    p.append(text(727, 188, "Обробка переривання DRDY", size=10, color=INK))
    p.append(text(727, 212, "Послідовні резистори 22–47 Ом", size=9.5, color=POS))
    p.append(text(727, 228, "на лініях SPI для гасіння дзвону", size=9.5, color=POS))
    p.append(text(727, 252, "Опціональний цифровий ізолятор", size=9.5, color=MUTED))
    p.append(text(727, 268, "(ISO7741 / ADuM140)", size=9.5, color=MUTED))

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 415,
                          "Суцільний полігон землі без розрізів + просторове зонування аналог/цифра гарантує повне збереження паспортної розрядності зовнішнього АЦП.",
                          size=11, stroke=MUTED, fill="#ffffff", min_w=850)
    p.append(b_bot)

    render(os.path.join(OUT, "external-adc-precision-layout.svg"), W, H, *p,
           title="Архітектура прецизійного вимірювального вузла на друкованій платі")


if __name__ == "__main__":
    fig_internal_vs_external_noise()
    fig_adc_architectures_tradeoff()
    fig_simultaneous_vs_multiplexed()
    fig_external_adc_precision_layout()
    print("All figures generated successfully.")
