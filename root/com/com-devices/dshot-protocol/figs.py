# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми dshot-protocol."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_analog_vs_digital_timing():
    """Порівняння аналогових протоколів (PWM, OneShot, MultiShot) із цифровим DShot."""
    w, h = 880, 500
    frags = []

    # Загальна рамка полотна
    frags.append(rect(20, 20, 840, 460, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(440, 48, "Еволюція інтерфейсів ESC: від аналогової тривалості до цифрового кадру", size=16, bold=True, color=INK))

    # Секція 1: Standard PWM (50–400 Гц, 1000–2000 мкс)
    y1 = 110
    frags.append(rect(40, y1 - 25, 800, 75, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(55, y1, "Standard PWM (50–400 Гц):", size=13, bold=True, color=INK, anchor="start"))
    frags.append(text(55, y1 + 22, "Тривалість: 1000...2000 мкс  |  Період: 2.5...20 мс  |  Аналоговий вимір часу", size=11, color=MUTED, anchor="start"))
    
    # Хвиля PWM
    pw1 = 120
    p1 = f"M 520 {y1+25} L 550 {y1+25} L 550 {y1-10} L {550+pw1} {y1-10} L {550+pw1} {y1+25} L 810 {y1+25}"
    frags.append(f'<path d="{p1}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(rect(550, y1-10, pw1, 35, fill="#fee2e2", stroke="none"))
    frags.append(text(550 + pw1/2, y1 - 15, "1000–2000 мкс", size=10, bold=True, color=POS))

    # Секція 2: OneShot125 / MultiShot (Аналоговий ШІМ високої частоти)
    y2 = 200
    frags.append(rect(40, y2 - 25, 800, 75, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(55, y2, "OneShot125 / MultiShot:", size=13, bold=True, color=INK, anchor="start"))
    frags.append(text(55, y2 + 22, "OneShot125: 125...250 мкс  |  MultiShot: 5...25 мкс (до 32 кГц)  |  Вразливість до джиттеру", size=11, color=MUTED, anchor="start"))
    
    # Хвиля MultiShot (короткі імпульси)
    pw2 = 30
    p2 = f"M 520 {y2+25} L 560 {y2+25} L 560 {y2-10} L {560+pw2} {y2-10} L {560+pw2} {y2+25} L 630 {y2+25} L 630 {y2-10} L {630+pw2} {y2-10} L {630+pw2} {y2+25} L 810 {y2+25}"
    frags.append(f'<path d="{p2}" fill="none" stroke="#d97706" stroke-width="2"/>')
    frags.append(rect(560, y2-10, pw2, 35, fill="#fef3c7", stroke="none"))
    frags.append(text(560 + pw2/2, y2 - 15, "5–25 мкс", size=10, bold=True, color="#b45309"))

    # Секція 3: DShot (Цифровий потік DShot600, 16 бітів)
    y3 = 290
    frags.append(rect(40, y3 - 25, 800, 95, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
    frags.append(text(55, y3, "DShot (DShot150 / 300 / 600 / 1200):", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(text(55, y3 + 22, "16-бітний цифровий кадр  |  DShot600: 26.7 мкс  |  Абсолютна дискретність", size=11, color=INK, anchor="start"))
    frags.append(text(55, y3 + 42, "Вбудований 4-бітний CRC: нульова чутливість до дрейфу тактування й наведень", size=11, bold=True, color=FIELD, anchor="start"))
    
    # Хвиля DShot (серія бітових імпульсів)
    bits = [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1]
    bx0 = 500
    bit_w = 18
    p3 = [f"M {bx0} {y3+35}"]
    for i, b in enumerate(bits):
        cx = bx0 + i * bit_w
        hi_w = bit_w * 0.67 if b == 1 else bit_w * 0.33
        p3.append(f"L {cx} {y3-5} L {cx+hi_w:.1f} {y3-5} L {cx+hi_w:.1f} {y3+35} L {cx+bit_w} {y3+35}")
    frags.append(f'<path d="{" ".join(p3)}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    frags.append(rect(bx0, y3-8, len(bits)*bit_w, 45, fill="#eff6ff", stroke=MUTED, sw=1, rx=4))
    frags.append(text(bx0 + len(bits)*bit_w/2, y3 - 15, "16-бітний потік (11 біт дані + 1 біт TLM + 4 біти CRC)", size=10, bold=True, color=NEG))

    # Порівняльна плашка внизу
    frags.append(rect(40, 400, 800, 60, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(440, 424, "Головний недолік аналогових протоколів: необхідність ручного калібрування діапазону (1000..2000 мкс) та шум фронтів.", size=11, color=INK))
    frags.append(text(440, 444, "DShot гарантує сталий нуль (Disarmed = 0) та 2000 дискретних градацій газу без ризику помилки декодування.", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "fig-analog-vs-digital-timing.svg"), w, h, *frags)


def fig_dshot_frame_structure():
    """Структура 16-бітного пакета DShot та кодування бітів 0 і 1."""
    w, h = 880, 520
    frags = []

    # Рамка
    frags.append(rect(20, 20, 840, 480, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(440, 48, "Формат 16-бітного кадру DShot та модуляція бітових інтервалів", size=16, bold=True, color=INK))

    # Секція А: Анатомія кадру 16 бітів
    frags.append(text(40, 85, "А. Розподіл бітів у кадрі (MSB First):", size=13, bold=True, color=INK, anchor="start"))

    # 11 бітів газу/команд (Біти 15..5)
    frags.append(rect(40, 100, 440, 75, fill="#dbeafe", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(260, 125, "11 бітів: Значення газу або команди (Throttle / Command)", size=12, bold=True, color=NEG))
    frags.append(text(260, 145, "Біти 15..5 (0 = Stop, 1..47 = Команди, 48..2047 = Газ 0..100%)", size=10, color=INK))
    frags.append(text(260, 162, "2000 градацій роздільної здатності", size=10, bold=True, color=MUTED))

    # 1 біт телеметрії (Бит 4)
    frags.append(rect(490, 100, 120, 75, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(text(550, 125, "1 біт: TLM", size=12, bold=True, color="#b45309"))
    frags.append(text(550, 145, "Бит 4", size=10, color=INK))
    frags.append(text(550, 162, "Запит телеметрії", size=10, color=MUTED))

    # 4 біти CRC (Біти 3..0)
    frags.append(rect(620, 100, 220, 75, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(730, 125, "4 біти: CRC (Checksum)", size=12, bold=True, color=FIELD))
    frags.append(text(730, 145, "Біти 3..0 (XOR-сума трьох ніблів)", size=10, color=INK))
    frags.append(text(730, 162, "(data ^ (data>>4) ^ (data>>8)) & 0x0F", size=9, bold=True, color=FIELD))

    # Секція Б: Кодування бітів (PWM Bit Encoding)
    frags.append(text(40, 215, "Б. Фізичне кодування логічного нуля та одиниці (Шпаруватість у межах T_bit):", size=13, bold=True, color=INK, anchor="start"))

    # Блок Біт 0
    bx0, by0 = 60, 240
    frags.append(rect(bx0, by0, 360, 170, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(bx0 + 180, by0 + 25, "Логічний 0 (Шпаруватість ≈ 33.3% / 1:2)", size=13, bold=True, color=INK))
    
    # Хвиля біта 0
    w_bit = 240
    h_hi = w_bit * (1.0 / 3.0) # 80 px
    p_b0 = f"M {bx0+60} {by0+120} L {bx0+60} {by0+60} L {bx0+60+h_hi:.1f} {by0+60} L {bx0+60+h_hi:.1f} {by0+120} L {bx0+60+w_bit} {by0+120}"
    frags.append(f'<path d="{p_b0}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    frags.append(rect(bx0+60, by0+60, h_hi, 60, fill="#eff6ff", stroke="none"))
    frags.append(text(bx0+60 + h_hi/2, by0 + 52, "T_high = 33.3% T", size=10, bold=True, color=NEG))
    frags.append(text(bx0+60 + h_hi + (w_bit-h_hi)/2, by0 + 138, "T_low = 66.7% T", size=10, color=MUTED))
    frags.append(line(bx0+60, by0+150, bx0+60+w_bit, by0+150, color=LINE, sw=1.2))
    frags.append(text(bx0+60+w_bit/2, by0+165, "Період T_bit", size=11, bold=True, color=INK))

    # Блок Біт 1
    bx1, by1 = 460, 240
    frags.append(rect(bx1, by1, 360, 170, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(bx1 + 180, by1 + 25, "Логічна 1 (Шпаруватість ≈ 66.7% / 2:1)", size=13, bold=True, color=INK))
    
    # Хвиля біта 1
    h_hi1 = w_bit * (2.0 / 3.0) # 160 px
    p_b1 = f"M {bx1+60} {by1+120} L {bx1+60} {by1+60} L {bx1+60+h_hi1:.1f} {by1+60} L {bx1+60+h_hi1:.1f} {by1+120} L {bx1+60+w_bit} {by1+120}"
    frags.append(f'<path d="{p_b1}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(rect(bx1+60, by1+60, h_hi1, 60, fill="#fee2e2", stroke="none"))
    frags.append(text(bx1+60 + h_hi1/2, by1 + 52, "T_high = 66.7% T", size=10, bold=True, color=POS))
    frags.append(text(bx1+60 + h_hi1 + (w_bit-h_hi1)/2, by1 + 138, "T_low = 33.3% T", size=10, color=MUTED))
    frags.append(line(bx1+60, by1+150, bx1+60+w_bit, by1+150, color=LINE, sw=1.2))
    frags.append(text(bx1+60+w_bit/2, by1+165, "Період T_bit", size=11, bold=True, color=INK))

    # Секція В: Таблиця швидкостей
    frags.append(rect(40, 430, 800, 55, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(440, 452, "DShot150: T_bit = 6.67 мкс (Кадр 106.7 мкс)  |  DShot300: T_bit = 3.33 мкс (Кадр 53.3 мкс)", size=11, color=INK))
    frags.append(text(440, 472, "DShot600: T_bit = 1.67 мкс (Кадр 26.7 мкс)  |  DShot1200: T_bit = 0.83 мкс (Кадр 13.3 мкс)", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "fig-dshot-frame-structure.svg"), w, h, *frags)


def fig_bidirectional_dshot_timing():
    """Двосторонній DShot (Bi-directional DShot): часова діаграма напівдуплексу та GCR-відповіді."""
    w, h = 900, 480
    frags = []

    # Рамка
    frags.append(rect(20, 20, 860, 440, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(450, 48, "Двосторонній DShot (Bi-directional DShot) у контурі регулювання PID", size=16, bold=True, color=INK))

    # Часова шкала повного циклу PID (125 мкс / 8 кГц або 250 мкс / 4 кГц)
    frags.append(line(60, 95, 840, 95, color=LINE, sw=1.5))
    frags.append(text(60, 85, "Початок циклу PID (t = 0)", size=11, bold=True, color=INK, anchor="start"))
    frags.append(text(840, 85, "Наступний цикл PID (125 мкс / 8 кГц)", size=11, bold=True, color=INK, anchor="end"))

    # Блок 1: Польотний контролер передає команду (FC TX Inverted DShot600)
    frags.append(rect(60, 115, 200, 110, fill="#dbeafe", stroke=NEG, sw=2, rx=6))
    frags.append(text(160, 140, "FC → ESC (Пакет газу)", size=12, bold=True, color=NEG))
    frags.append(text(160, 160, "16 бітів (Інвертований DShot)", size=10, color=INK))
    frags.append(text(160, 180, "Тривалість: 26.7 мкс", size=11, bold=True, color=NEG))
    frags.append(text(160, 205, "FC пін: Вихід (TX Active Low)", size=9, color=MUTED))

    # Блок 2: Захисний інтервал перемикання лінії (Turnaround Time)
    frags.append(rect(270, 115, 120, 110, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(330, 145, "Guard Time", size=12, bold=True, color=POS))
    frags.append(text(330, 170, "≈ 30 мкс", size=12, bold=True, color=POS))
    frags.append(text(330, 195, "Перемикання TX/RX", size=9, color=MUTED))
    frags.append(text(330, 210, "Лінія підтягнута до VCC", size=9, color=MUTED))

    # Блок 3: Регулятор передає телеметрію (ESC TX GCR Telemetry)
    frags.append(rect(400, 115, 260, 110, fill="#dcfce7", stroke=FIELD, sw=2, rx=6))
    frags.append(text(530, 140, "ESC → FC (Пакет телеметрії eGCR)", size=12, bold=True, color=FIELD))
    frags.append(text(530, 160, "21 біт (GCR 5b4b кодування)", size=10, color=INK))
    frags.append(text(530, 180, "16 бітів ERPM періоду + CRC", size=11, bold=True, color=FIELD))
    frags.append(text(530, 205, "ESC пін: Вихід (TX) | FC: Вхід (RX/Timer Capture)", size=9, color=MUTED))

    # Блок 4: Обчислення фільтрації та контуру PID
    frags.append(rect(670, 115, 170, 110, fill="#f3e8ff", stroke="#9333ea", sw=1.5, rx=6))
    frags.append(text(755, 140, "FC: Обробка", size=12, bold=True, color="#7e22ce"))
    frags.append(text(755, 160, "Декодування GCR", size=10, color=INK))
    frags.append(text(755, 180, "RPM Notch Filter", size=11, bold=True, color="#7e22ce"))
    frags.append(text(755, 205, "PID Loop Step", size=9, color=MUTED))

    # Сигналограма фізичної лінії зв'язку
    sy = 270
    frags.append(text(60, sy - 15, "Фізичний стан сигнальної лінії (Half-Duplex Single Wire):", size=12, bold=True, color=INK, anchor="start"))
    frags.append(rect(60, sy, 780, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    
    # Хвиля інвертованого DShot
    p_sig = [f"M 70 {sy+15} L 70 {sy+50} L 85 {sy+50} L 85 {sy+15} L 100 {sy+15} L 100 {sy+50} L 125 {sy+50} L 125 {sy+15} L 240 {sy+15}"]
    # Guard time (High)
    p_sig.append(f"L 380 {sy+15}")
    # GCR pulses
    p_sig.append(f"L 400 {sy+15} L 400 {sy+50} L 415 {sy+50} L 415 {sy+15} L 430 {sy+15} L 430 {sy+50} L 445 {sy+50} L 445 {sy+15} L 640 {sy+15}")
    # Idle line till next frame
    p_sig.append(f"L 830 {sy+15}")
    frags.append(f'<path d="{" ".join(p_sig)}" fill="none" stroke="{LINE}" stroke-width="2"/>')

    frags.append(text(150, sy + 35, "Інвертований DShot (FC TX)", size=10, bold=True, color=NEG))
    frags.append(text(325, sy + 35, "Line Idle (3.3V)", size=10, bold=True, color=POS))
    frags.append(text(520, sy + 35, "GCR Телеметрія (ESC TX)", size=10, bold=True, color=FIELD))
    frags.append(text(735, sy + 35, "Line Idle", size=10, color=MUTED))

    # Нижній висновок
    frags.append(rect(40, 370, 820, 70, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(450, 395, "GCR (Group Code Recording) перетворює 4-бітні ніблі в 5-бітні коди, усуваючи довгі серії нулів чи одиниць.", size=11, color=INK))
    frags.append(text(450, 420, "Це дозволяє польотному контролеру точно відновити синхронізацію прийому без окремої лінії тактування.", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "fig-bidirectional-dshot-timing.svg"), w, h, *frags)


def fig_dshot_dma_timer_pipeline():
    """Апаратний конвеєр генерації DShot за допомогою Timer + DMA на мікроконтролері."""
    w, h = 900, 500
    frags = []

    # Рамка
    frags.append(rect(20, 20, 860, 460, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(450, 48, "Апаратна генерація DShot: зв'язка ОЗП → DMA → Таймер PWM (STM32)", size=16, bold=True, color=INK))

    # Блок 1: Буфер у пам'яті (RAM Buffer)
    frags.append(rect(40, 100, 200, 280, fill="#ffffff", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(140, 125, "ОЗП (SRAM Buffer)", size=13, bold=True, color=NEG))
    frags.append(text(140, 145, "uint32_t dshot_dmabuf[17]", size=10, color=MUTED))

    cells = [
        ("dshot_dmabuf[0]", "Bit 15 (MSB)", "#dbeafe"),
        ("dshot_dmabuf[1]", "Bit 14", "#dbeafe"),
        ("...", "...", "#ffffff"),
        ("dshot_dmabuf[11]", "Bit 4 (TLM)", "#fef3c7"),
        ("dshot_dmabuf[12..15]", "Bits 3..0 (CRC)", "#dcfce7"),
        ("dshot_dmabuf[16]", "0 (Reset / Low)", "#f1f5f9"),
    ]
    for i, (c_name, c_desc, c_fill) in enumerate(cells):
        cy = 165 + i * 32
        frags.append(rect(50, cy, 180, 26, fill=c_fill, stroke=LINE, sw=1, rx=3))
        frags.append(text(60, cy + 17, c_name, size=9, bold=True, color=INK, anchor="start"))
        frags.append(text(220, cy + 17, c_desc, size=9, color=MUTED, anchor="end"))

    # Стрілка від RAM до DMA
    frags.append(arrow(240, 240, 310, 240, color=LINE, sw=2))
    frags.append(text(275, 230, "Memory Read", size=10, bold=True, color=INK))

    # Блок 2: Контролер прямого доступу до пам'яті (DMA Controller)
    frags.append(rect(310, 150, 180, 180, fill="#fef3c7", stroke="#d97706", sw=2, rx=6))
    frags.append(text(400, 180, "DMA Engine", size=14, bold=True, color="#b45309"))
    frags.append(text(400, 205, "(DMA Stream / Channel)", size=10, color=INK))
    frags.append(text(400, 230, "Circular / Normal Mode", size=10, color=MUTED))
    frags.append(text(400, 255, "Трансфер: 17 слів (32-bit)", size=10, bold=True, color="#b45309"))
    frags.append(text(400, 280, "Trigger: TIM_UP Event", size=10, bold=True, color=POS))
    frags.append(text(400, 305, "Нульове навантаження CPU!", size=9, color=MUTED))

    # Стрілка від DMA до Timer CCR
    frags.append(arrow(490, 240, 560, 240, color=LINE, sw=2))
    frags.append(text(525, 230, "Peripheral Write", size=10, bold=True, color=INK))

    # Блок 3: Апаратний таймер (Timer PWM Channel)
    frags.append(rect(560, 100, 260, 280, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
    frags.append(text(690, 125, "Таймер (TIMx Peripheral)", size=13, bold=True, color=FIELD))
    frags.append(text(690, 145, "PWM Mode 1  |  ARR = Period (T_bit)", size=10, color=MUTED))

    # Регістри таймера
    frags.append(rect(580, 165, 220, 45, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(690, 185, "TIMx->ARR (Auto-Reload)", size=11, bold=True, color=INK))
    frags.append(text(690, 200, "Фіксована база часу біта (1.67 мкс при DShot600)", size=9, color=MUTED))

    frags.append(rect(580, 225, 220, 55, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(690, 245, "TIMx->CCR1 (Compare Reg)", size=11, bold=True, color=FIELD))
    frags.append(text(690, 260, "Записується через DMA кожен період!", size=9, bold=True, color=POS))
    frags.append(text(690, 273, "CCR = 33% ARR (0) або 66% ARR (1)", size=9, color=INK))

    frags.append(rect(580, 295, 220, 65, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(690, 315, "Вихідний пін (GPIO Output)", size=11, bold=True, color=NEG))
    frags.append(text(690, 335, "DShot Signal → ESC", size=12, bold=True, color=NEG))
    frags.append(text(690, 350, "Ідеальні апаратні фронти", size=9, color=MUTED))

    # Зворотний тригер від Timer UP до DMA
    frags.append(f'<path d="M 580 185 L 525 185 L 525 210 L 490 210" fill="none" stroke="{POS}" stroke-width="1.8" stroke-dasharray="3,3"/>')
    frags.append(text(535, 175, "TIM_UP Request", size=9, bold=True, color=POS))

    # Нижній блок опису
    frags.append(rect(40, 400, 820, 65, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(450, 423, "Процесор формує значення CCR у буфері ОЗП і запускає DMA. Уся 16-бітна пачка вистрілюється", size=11, color=INK))
    frags.append(text(450, 443, "повністю апаратно без переривань на кожен біт, що усуває будь-який джиттер затримки переривань (ISR jitter).", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "fig-dshot-dma-timer-pipeline.svg"), w, h, *frags)


def fig_rpm_filter_frequency_response():
    """Динамічна RPM-фільтрація: спектр вібрацій та адаптивні режекторні фільтри."""
    w, h = 900, 480
    frags = []

    # Рамка
    frags.append(rect(20, 20, 860, 440, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    frags.append(text(450, 48, "Динамічна RPM-фільтрація (RPM Notch Filtering) на основі телеметрії DShot", size=16, bold=True, color=INK))

    # Графік спектра шуму гіроскопа та АЧХ фільтрів
    gx0, gy0, gw, gh = 110, 300, 700, 130

    # Осі координат
    frags.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.5))
    frags.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.5))
    frags.append(text(gx0 + gw - 10, gy0 + 28, "Частота f (Гц)", size=12, bold=True, color=INK, anchor="end"))
    frags.append(text(gx0 - 10, gy0 - gh - 10, "Амплітуда (дБ)", size=11, bold=True, color=INK, anchor="start"))

    # Позначки частот по осі X
    for fx_val, fx_lbl in [(0, "0 Гц"), (150, "150 Гц"), (300, "f_motor (1x)"), (600, "2x f_motor"), (900, "3x f_motor")]:
        cx = gx0 + (fx_val / 1000.0) * gw
        frags.append(line(cx, gy0 - 5, cx, gy0 + 5, color=MUTED, sw=1))
        frags.append(text(cx, gy0 + 20, fx_lbl, size=10, bold=(fx_val > 150), color=INK if fx_val <= 150 else POS))

    # Спектр вібрацій гіроскопа (Піки шуму від обертання моторів)
    p_noise = [f"M {gx0} {gy0-15}"]
    for x_i in range(5, 705, 5):
        freq_hz = (x_i / float(gw)) * 1000.0
        peak1 = 80.0 * math.exp(-((freq_hz - 300.0)**2) / (2 * 18.0**2))
        peak2 = 55.0 * math.exp(-((freq_hz - 600.0)**2) / (2 * 22.0**2))
        peak3 = 35.0 * math.exp(-((freq_hz - 900.0)**2) / (2 * 25.0**2))
        y_val = gy0 - 15 - peak1 - peak2 - peak3
        p_noise.append(f"L {gx0+x_i} {y_val:.1f}")
    p_noise.append(f"L {gx0+gw} {gy0-15}")
    frags.append(f'<path d="{" ".join(p_noise)}" fill="none" stroke="{POS}" stroke-width="2"/>')
    frags.append(text(gx0 + 210, gy0 - 105, "Пік вібрації мотора (f_1)", size=10, bold=True, color=POS))
    frags.append(text(gx0 + 420, gy0 - 75, "2-га гармоніка (f_2)", size=10, bold=True, color=POS))

    # АЧХ динамічних режекторних фільтрів (RPM Notch Filters)
    p_notch = [f"M {gx0} {gy0-110}"]
    for x_i in range(5, 705, 5):
        freq_hz = (x_i / float(gw)) * 1000.0
        notch1 = 90.0 * math.exp(-((freq_hz - 300.0)**2) / (2 * 12.0**2))
        notch2 = 70.0 * math.exp(-((freq_hz - 600.0)**2) / (2 * 15.0**2))
        notch3 = 45.0 * math.exp(-((freq_hz - 900.0)**2) / (2 * 18.0**2))
        y_val = gy0 - 110 + notch1 + notch2 + notch3
        p_notch.append(f"L {gx0+x_i} {y_val:.1f}")
    p_notch.append(f"L {gx0+gw} {gy0-110}")
    frags.append(f'<path d="{" ".join(p_notch)}" fill="none" stroke="{FIELD}" stroke-width="2.5" stroke-dasharray="4,2"/>')
    frags.append(text(gx0 + 210, gy0 - 30, "Notch 1 (вирізає f_1)", size=10, bold=True, color=FIELD))
    frags.append(text(gx0 + 420, gy0 - 45, "Notch 2 (вирізає f_2)", size=10, bold=True, color=FIELD))

    # Верхня інформаційна панель
    frags.append(rect(40, 80, 820, 65, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(450, 105, "Телеметрія DShot передає ERPM кожного мотора в реальному часі (4–8 кГц).", size=12, bold=True, color=INK))
    frags.append(text(450, 125, "Контролер автоматично центрує вузькі режекторні фільтри на точних частотах гармонік двигунів.", size=11, color=MUTED))
    frags.append(text(450, 138, "Результат: нульове фазове запізнення в робочій зоні керування (0..50 Гц) при повному зрізанні шумів!", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "fig-rpm-filter-frequency-response.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_analog_vs_digital_timing()
    fig_dshot_frame_structure()
    fig_bidirectional_dshot_timing()
    fig_dshot_dma_timer_pipeline()
    fig_rpm_filter_frequency_response()
    print("Фігури згенеровано успішно.")
