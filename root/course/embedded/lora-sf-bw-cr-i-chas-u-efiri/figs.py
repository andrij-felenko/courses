# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to root/scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. lora-chirp-spectrogram: Частотно-часова спектрограма чирпів LoRa ──────
def fig_chirp_spectrogram():
    W, H = 880, 420
    p = []

    # Фон графіка
    p.append(rect(70, 50, 750, 280, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))

    # Сітка частот і часу
    for y_val in [100, 160, 220, 280]:
        p.append(line(70, y_val, 820, y_val, color="#e2e8f0", sw=1, dash="4 4"))
    for x_val in [220, 370, 520, 670]:
        p.append(line(x_val, 50, x_val, 330, color="#e2e8f0", sw=1, dash="4 4"))

    # Осі
    p.append(arrow(70, 330, 840, 330, color=INK, sw=1.5))
    p.append(arrow(70, 330, 70, 35, color=INK, sw=1.5))
    p.append(text(845, 334, "Час (t)", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(70, 25, "Частота (f)", size=12, color=INK, bold=True, anchor="middle"))

    # Рівні частот
    p.append(text(60, 75, "f_max", size=11, color=MUTED, anchor="end"))
    p.append(text(60, 190, "f_0", size=11, color=MUTED, anchor="end"))
    p.append(text(60, 305, "f_min", size=11, color=MUTED, anchor="end"))

    # Позначка смуги BW
    p.append(line(85, 75, 85, 305, color=FIELD, sw=1.5))
    p.append(line(80, 75, 90, 75, color=FIELD, sw=1.5))
    p.append(line(80, 305, 90, 305, color=FIELD, sw=1.5))
    b_bw, _, _ = textbox(135, 190, "Смуга BW\n(125 кГц)", size=11, fill="#f0fdf4", stroke=FIELD, bold=True)
    p.append(b_bw)

    # 1) Базовий Up-chirp (символ 0) від 220 до 370
    p.append(line(220, 305, 370, 75, color=POS, sw=3))
    p.append(text(295, 360, "Символ 0 (Up-chirp)", size=12, color=POS, bold=True))
    p.append(text(295, 380, "Старт із f_min", size=10, color=MUTED))

    # 2) Модульований символ m (циклічний зсув) від 370 до 520
    p.append(line(370, 190, 445, 75, color=NEG, sw=3))
    p.append(line(445, 75, 445, 305, color=NEG, sw=1.2, dash="3 3"))
    p.append(line(445, 305, 520, 190, color=NEG, sw=3))
    p.append(circle(370, 190, 4, fill=NEG, stroke=INK, sw=1))
    p.append(text(445, 360, "Символ m (Data)", size=12, color=NEG, bold=True))
    p.append(text(445, 380, "Старт із f_start (зсув)", size=10, color=MUTED))

    # 3) Down-chirp (SFD / синхронізація) від 520 до 670
    p.append(line(520, 75, 670, 305, color="#7c3aed", sw=3))
    p.append(text(595, 360, "Down-chirp (SFD)", size=12, color="#7c3aed", bold=True))
    p.append(text(595, 380, "Спадний нахил", size=10, color=MUTED))

    # Інтервал символу Ts
    p.append(line(220, 45, 370, 45, color=LINE, sw=1.5))
    p.append(line(220, 40, 220, 50, color=LINE, sw=1.5))
    p.append(line(370, 40, 370, 50, color=LINE, sw=1.5))
    p.append(text(295, 38, "T_s = 2^SF / BW", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "lora-chirp-spectrogram.svg"), W, H, *p,
           title="Частотно-часова спектрограма чирпів LoRa")


# ── 2. lora-demodulation-snr: Демодуляція нижче рівня шуму (дечирпінг і FFT) ──
def fig_demodulation_snr():
    W, H = 920, 390
    p = []

    # Блок 1: Вхідний зашумлений чирп
    p.append(rect(20, 40, 255, 290, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(147, 65, "1. Прийом сигналу", size=13, color=INK, bold=True))
    p.append(text(147, 85, "Сигнал втоплений у шум", size=11, color=MUTED))

    # Міні-графік спектрограми в шумі
    p.append(rect(45, 105, 205, 130, fill="#1e293b", stroke="#334155", sw=1, rx=4))
    for ny in [120, 140, 160, 180, 200, 220]:
        p.append(line(50, ny, 245, ny, color="#475569", sw=1, dash="2 6"))
    p.append(line(65, 215, 230, 125, color="#38bdf8", sw=2.2))
    p.append(text(147, 260, "SNR = -15 dB .. -20 dB", size=11, color=NEG, bold=True))
    p.append(text(147, 280, "Сигнал нижче шуму на 20 dB", size=10, color=MUTED))

    # Стрілка переходу 1 -> 2
    p.append(arrow(280, 170, 315, 170, color=INK, sw=2))

    # Блок 2: Множник (Дечирпінг)
    p.append(rect(320, 40, 255, 290, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(447, 65, "2. Дечирпінг (Згортання)", size=13, color=INK, bold=True))
    p.append(text(447, 85, "Множення на Down-chirp", size=11, color=MUTED))

    p.append(rect(345, 105, 205, 130, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(line(355, 215, 540, 125, color="#38bdf8", sw=1.8))
    p.append(text(447, 135, "s(t) · c*(t)", size=12, color=INK, bold=True))
    p.append(line(355, 125, 540, 215, color="#7c3aed", sw=1.8, dash="4 2"))
    p.append(line(355, 170, 540, 170, color=POS, sw=2.5))
    p.append(text(447, 195, "f_diff = const (тон!)", size=11, color=POS, bold=True))
    p.append(text(447, 260, "Лінійний нахил зникає", size=11, color=INK, bold=True))
    p.append(text(447, 280, "Шум лишається некорельованим", size=10, color=MUTED))

    # Стрілка переходу 2 -> 3
    p.append(arrow(580, 170, 615, 170, color=INK, sw=2))

    # Блок 3: Швидке перетворення Фур'є (FFT)
    p.append(rect(620, 40, 280, 290, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(760, 65, "3. Обчислення FFT", size=13, color=INK, bold=True))
    p.append(text(760, 85, "Енергія збирається в 1 бін", size=11, color=MUTED))

    p.append(rect(640, 105, 240, 130, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(line(655, 220, 865, 220, color=LINE, sw=1.5))
    p.append(line(655, 205, 865, 205, color="#94a3b8", sw=1, dash="3 3"))
    p.append(text(670, 195, "Шум", size=10, color=MUTED))
    p.append(rect(745, 120, 16, 100, fill=POS, stroke=INK, sw=1))
    p.append(text(753, 112, "Символ m", size=11, color=POS, bold=True))

    b_pg, _, _ = textbox(760, 270, "Виграш обробки:\nPG = 10·log10(2^SF)", size=11, fill="#ecfdf5", stroke=POS, bold=True)
    p.append(b_pg)

    render(os.path.join(OUT, "lora-demodulation-snr.svg"), W, H, *p,
           title="Принцип дечирпінгу та виділення сигналу нижче рівня шуму через FFT")


# ── 3. lora-toa-structure: Структура кадру LoRa та розрахунок Time-on-Air ─────
def fig_toa_structure():
    W, H = 900, 380
    p = []

    # Загальний заголовок і часова вісь зверху
    p.append(text(450, 35, "Структура фізичного пакета LoRa та розподіл часу в ефірі (Time-on-Air)", size=14, color=INK, bold=True))

    # Секція 1: Преамбула (Preamble)
    p.append(rect(30, 70, 280, 150, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(170, 95, "ПРЕАМБУЛА (Preamble)", size=13, color=NEG, bold=True))
    p.append(text(170, 115, "Синхронізація AGC, AFC, Symbol Timing", size=10, color=MUTED))

    p.append(rect(45, 130, 115, 70, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(102, 155, "N_preamble", size=11, color=INK, bold=True))
    p.append(text(102, 175, "Up-chirps (тип. 8)", size=10, color=MUTED))

    p.append(rect(165, 130, 70, 70, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(200, 155, "Sync", size=11, color=INK, bold=True))
    p.append(text(200, 175, "2 симв.", size=10, color=MUTED))

    p.append(rect(240, 130, 60, 70, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(270, 155, "SFD", size=11, color=INK, bold=True))
    p.append(text(270, 175, "2.25", size=10, color=MUTED))

    # Секція 2: Заголовок (Header)
    p.append(rect(325, 70, 155, 150, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    p.append(text(402, 95, "ЗАГОЛОВОК", size=13, color="#d97706", bold=True))
    p.append(text(402, 115, "Explicit / Implicit (H)", size=10, color=MUTED))
    p.append(rect(340, 130, 125, 70, fill="#ffffff", stroke="#fde68a", sw=1.2, rx=4))
    p.append(text(402, 150, "Довжина PL", size=10, color=INK))
    p.append(text(402, 168, "Coding Rate (CR)", size=10, color=INK))
    p.append(text(402, 186, "Header CRC", size=10, color=INK))

    # Секція 3: Корисне навантаження (Payload)
    p.append(rect(495, 70, 255, 150, fill="#f0fdf4", stroke=POS, sw=1.8, rx=6))
    p.append(text(622, 95, "КОРИСНІ ДАНІ (Payload)", size=13, color=POS, bold=True))
    p.append(text(622, 115, "PL = 1 .. 255 байтів (Hamming FEC)", size=10, color=MUTED))
    p.append(rect(510, 130, 225, 70, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(622, 155, "N_payload символів", size=12, color=POS, bold=True))
    p.append(text(622, 175, "Враховує CR, LDRO (DE), SF", size=10, color=MUTED))

    # Секція 4: Контрольна сума кадру (CRC)
    p.append(rect(765, 70, 110, 150, fill="#fdf2f8", stroke="#db2777", sw=1.8, rx=6))
    p.append(text(820, 95, "CRC", size=13, color="#db2777", bold=True))
    p.append(text(820, 115, "16 біт", size=10, color=MUTED))
    p.append(rect(775, 130, 90, 70, fill="#ffffff", stroke="#fbcfe8", sw=1.2, rx=4))
    p.append(text(820, 155, "Payload CRC", size=10, color=INK, bold=True))
    p.append(text(820, 175, "Опція (CRC=1)", size=10, color=MUTED))

    # Формули внизу
    b_f1, _, _ = textbox(170, 275, "T_preamble = (N_preamble + 4.25) · T_s", size=11, fill="#eff6ff", stroke=NEG, bold=True)
    p.append(b_f1)

    b_f2, _, _ = textbox(622, 275, "T_payload = N_payload · T_s", size=11, fill="#f0fdf4", stroke=POS, bold=True)
    p.append(b_f2)

    # Підсумкова формула ToA
    b_toa, _, _ = textbox(450, 335, "Time-on-Air (ToA) = T_preamble + T_payload = (N_pream_total + N_payload) · (2^SF / BW)", size=11, fill="#f8fafc", stroke=INK, bold=True)
    p.append(b_toa)

    render(os.path.join(OUT, "lora-toa-structure.svg"), W, H, *p,
           title="Структура пакета LoRa та розрахунок часу передачі преамбули й корисних даних")


# ── 4. lora-duty-cycle-energy: Вплив SF на Duty Cycle 1% та витрату енергії ──
def fig_duty_cycle_energy():
    W, H = 880, 420
    p = []

    # Заголовок
    p.append(text(440, 35, "Порівняння тривалості передачі, паузи Duty Cycle (1%) та енергії для 16 байтів", size=13, color=INK, bold=True))

    # Ліва колонка: Швидкий профіль (SF7, BW 125 кГц)
    p.append(rect(35, 60, 390, 330, fill="#f8fafc", stroke=POS, sw=1.5, rx=8))
    p.append(text(230, 85, "SF7 / BW 125 кГц (Близько / Швидко)", size=13, color=POS, bold=True))

    # Таймлайн SF7
    p.append(text(55, 115, "Час у ефірі: ToA ≈ 56.6 мс", size=11, color=INK, bold=True, anchor="start"))
    p.append(rect(55, 125, 45, 30, fill=POS, stroke=INK, sw=1, rx=3))
    p.append(text(77, 144, "TX", size=10, color="#ffffff", bold=True))

    p.append(rect(105, 125, 300, 30, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=3))
    p.append(text(255, 144, "Обов'язкове мовчання (Time-off): 5.6 с", size=10, color=MUTED))

    b_sf7_stats, _, _ = textbox(230, 235, "• Швидкість даних: 5468 біт/с\n• Чутливість: -124.5 dBm\n• Енергія на 1 пакет: ~4.1 мДж (3.3 В, 22 мА)\n• Максимум пакетів/год (1% DC): 636 пакетів\n• Вплив на радіоефір: мінімальний (ефір вільний)", size=11, fill="#ffffff", stroke=POS)
    p.append(b_sf7_stats)

    p.append(text(230, 365, "Ідеально для частих вимірювань і довгого життя батареї", size=10, color=POS, bold=True))

    # Права колонка: Далекий профіль (SF12, BW 125 кГц)
    p.append(rect(455, 60, 390, 330, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(650, 85, "SF12 / BW 125 кГц (Далеко / Повільно)", size=13, color=NEG, bold=True))

    # Таймлайн SF12
    p.append(text(475, 115, "Час у ефірі: ToA ≈ 1318.9 мс (1.32 с!)", size=11, color=INK, bold=True, anchor="start"))
    p.append(rect(475, 125, 110, 30, fill=NEG, stroke=INK, sw=1, rx=3))
    p.append(text(530, 144, "TX (1.32 с)", size=10, color="#ffffff", bold=True))

    p.append(rect(590, 125, 235, 30, fill="#fef2f2", stroke="#fecaca", sw=1, rx=3))
    p.append(text(707, 144, "Time-off: 130.6 с (2.2 хв!)", size=10, color=NEG, bold=True))

    b_sf12_stats, _, _ = textbox(650, 235, "• Швидкість даних: 293 біт/с\n• Чутливість: -137.0 dBm (+12.5 dB дальність)\n• Енергія на 1 пакет: ~95.7 мДж (у 23 рази більше!)\n• Максимум пакетів/год (1% DC): 27 пакетів\n• Вплив на радіоефір: високий ризик колізій", size=11, fill="#ffffff", stroke=NEG)
    p.append(b_sf12_stats)

    p.append(text(650, 365, "Плата за екстремальну дальність: швидке виснаження батареї", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "lora-duty-cycle-energy.svg"), W, H, *p,
           title="Порівняння характеристик радіолінії, обов'язкової паузи 1% Duty Cycle та енергоспоживання для SF7 та SF12")


if __name__ == "__main__":
    fig_chirp_spectrogram()
    fig_demodulation_snr()
    fig_toa_structure()
    fig_duty_cycle_energy()
    print("All LoRa figures generated successfully!")
