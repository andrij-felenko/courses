# -*- coding: utf-8 -*-
"""Фігури для статті biudzhet-telemetrii-pro-samu-telemetriiu.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_meta_telemetry_breakdown():
    """Порівняння структури та накладних витрат пакета: наївний JSON проти бітово-упакованого кадру."""
    W, H = 840, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Анатомія кадру: корисні дані проти мета-телеметрії здоров'я", size=16, color=INK, bold=True))

    # Ліва колонка — Наївний JSON із роздутою діагностикою
    p.append(rect(30, 55, 370, 395, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(215, 82, "Наївний підхід: JSON у кожному пакеті", size=14, color=POS, bold=True))
    p.append(text(215, 102, "Загальний розмір корисного тіла: 146 байтів", size=11, color=MUTED))

    # Блоки всередині лівої колонки
    # Корисні дані
    p.append(rect(50, 120, 330, 48, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(215, 142, "Корисні вимірювання: 4 байти (2.7 %)", size=12, color=FIELD, bold=True))
    p.append(text(215, 158, "{\"t\":22.5,\"h\":60}", size=10, color=INK))

    # Мета-телеметрія
    p.append(rect(50, 178, 330, 110, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 198, "Мета-телеметрія стану: 72 байти (49.3 %)", size=12, color=POS, bold=True))
    p.append(text(215, 218, "\"v_bat\":3.62,\"sag\":0.18,\"rssi\":-88,\"snr\":6,", size=10, color=INK))
    p.append(text(215, 236, "\"uptime\":86400,\"free_heap\":14200,\"wdt_rst\":0,", size=10, color=INK))
    p.append(text(215, 254, "\"stack_hw\":840,\"mcu_temp\":28.4,\"retries\":2", size=10, color=INK))
    p.append(text(215, 274, "Діагностика важить у 18 разів більше за дані!", size=10, color=POS, bold=True))

    # JSON синтаксис та ключі
    p.append(rect(50, 298, 330, 52, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(215, 318, "Синтаксичний оверхед JSON: 70 байтів (48.0 %)", size=11, color="#475569", bold=True))
    p.append(text(215, 336, "Назви ключів, лапки, коми, фігурні дужки", size=10, color=MUTED))

    # Наслідки ліворуч
    p.append(rect(45, 362, 340, 72, fill="#ffffff", stroke=POS, sw=1.0, rx=4))
    p.append(text(215, 382, "Ціна в LoRaWAN (SF10, BW125):", size=11, color=POS, bold=True))
    p.append(text(215, 400, "Час у радіоефірі (ToA): 618 мс", size=11, color=INK))
    p.append(text(215, 418, "Енергія передачі: ~225 мДж на один вимір", size=11, color=POS, bold=True))

    # Права колонка — Оптимізоване бітове пакування + Piggyback
    p.append(rect(440, 55, 370, 395, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(625, 82, "Оптимізоване бітове пакування", size=14, color=FIELD, bold=True))
    p.append(text(625, 102, "Загальний розмір тіла: 12 байтів (стиснення у 12 разів)", size=11, color=MUTED))

    # Блоки всередині правої колонки
    # Корисні дані
    p.append(rect(460, 120, 330, 68, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(625, 142, "Корисні вимірювання: 4 байти (33.3 %)", size=12, color=FIELD, bold=True))
    p.append(text(625, 160, "int16_t temp_c_x100 (2Б), uint16_t hum_x100 (2Б)", size=10, color=INK))
    p.append(text(625, 176, "Фіксована кома замість ASCII рядків", size=10, color=MUTED))

    # Мета-телеметрія
    p.append(rect(460, 198, 330, 110, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(625, 218, "Упакована мета-телеметрія: 8 байтів (66.7 %)", size=12, color="#0369a1", bold=True))
    p.append(text(625, 238, "Байт 0: 6 статус-прапорців + 2b код ресету", size=10, color=INK))
    p.append(text(625, 254, "Байт 1-2: Напруга + просадка (дельта V_sag)", size=10, color=INK))
    p.append(text(625, 270, "Байт 3-4: RSSI/Retries + Min Free Heap (кванти 256Б)", size=10, color=INK))
    p.append(text(625, 290, "Байт 5-7: Температура кристала + Uptime delta", size=10, color=INK))

    # Відсутність синтаксичного баласту
    p.append(rect(460, 318, 330, 32, fill="#f8fafc", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(625, 338, "Синтаксичний оверхед: 0 байтів (жорсткий контракт)", size=10, color=FIELD, bold=True))

    # Наслідки праворуч
    p.append(rect(455, 362, 340, 72, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(625, 382, "Ціна в LoRaWAN (SF10, BW125):", size=11, color=FIELD, bold=True))
    p.append(text(625, 400, "Час у радіоефірі (ToA): 98 мс (у 6.3 раза менше)", size=11, color=INK))
    p.append(text(625, 418, "Енергія передачі: ~36 мДж (економія 84 % заряду)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "meta-telemetry-breakdown.svg"), W, H, *p)


def fig_piggyback_vs_burst_timeline():
    """Хронограма трьох стратегій передачі мета-телеметрії: постійна, piggyback та адаптивний burst."""
    W, H = 840, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Стратегії передачі: постійний звіт, Piggybacking та адаптивний сплеск", size=16, color=INK, bold=True))

    # Стратегія 1: Постійна передача важкої діагностики
    p.append(rect(25, 45, 790, 120, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(40, 68, "1. Постійна повна діагностика (Naive Continuous): важкий пакет кожні 10 хв", size=12, color=POS, bold=True, anchor="start"))
    # Вісь часу
    p.append(line(50, 135, 780, 135, color="#94a3b8", sw=1.5))
    # Сплески кожні 120px
    for i, tx in enumerate([100, 220, 340, 460, 580, 700]):
        p.append(rect(tx - 18, 85, 36, 48, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
        p.append(text(tx, 104, "146 Б", size=10, color=POS, bold=True))
        p.append(text(tx, 122, "225 мДж", size=10, color=INK))
        p.append(text(tx, 152, "%d0 хв" % (i + 1), size=10, color=MUTED))
    p.append(text(760, 85, "Батарея сідає за 4 міс.", size=11, color=POS, bold=True, anchor="end"))

    # Стратегія 2: Підсаджування (Piggybacking) та розріджений Heartbeat
    p.append(rect(25, 180, 790, 140, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(40, 203, "2. Підсаджування (Piggybacking): легкі дані що 10 хв + повний звіт раз на 6 год", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(line(50, 285, 780, 285, color="#94a3b8", sw=1.5))
    # Легкі пакети (корисні дані + 1 статус-байт)
    for i, tx in enumerate([100, 220, 340, 460, 580]):
        p.append(rect(tx - 14, 245, 28, 38, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=2))
        p.append(text(tx, 262, "5 Б", size=10, color=FIELD, bold=True))
        p.append(text(tx, 276, "22 мДж", size=9, color=INK))
        p.append(text(tx, 304, "%d0 хв" % (i + 1), size=10, color=MUTED))
    # Повний кадр здоров'я (раз на 6 год або за розкладом)
    p.append(rect(700 - 18, 235, 36, 48, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=3))
    p.append(text(700, 254, "12 Б", size=10, color="#0284c7", bold=True))
    p.append(text(700, 272, "36 мДж", size=9, color=INK))
    p.append(text(700, 304, "60 хв (Pulse)", size=10, color="#0284c7", bold=True))
    p.append(text(760, 218, "Батарея живе 5+ років", size=11, color=FIELD, bold=True, anchor="end"))

    # Стратегія 3: Адаптивний сплеск при аномалії (Event-Driven Diagnostic Burst)
    p.append(rect(25, 335, 790, 165, fill="#eff6ff", stroke="#2563eb", sw=1.2, rx=6))
    p.append(text(40, 358, "3. Адаптивний сплеск (Event-Driven Diagnostic Burst): детекція деградації", size=12, color="#1d4ed8", bold=True, anchor="start"))
    p.append(line(50, 455, 780, 455, color="#94a3b8", sw=1.5))

    # Спокійний режим
    for tx in [100, 220]:
        p.append(rect(tx - 14, 415, 28, 38, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=2))
        p.append(text(tx, 432, "5 Б", size=10, color=FIELD, bold=True))
        p.append(text(tx, 474, "Норма", size=10, color=FIELD))

    # Поріг аномалії
    p.append(line(310, 365, 310, 465, color=POS, sw=1.5, dash="4,3"))
    p.append(text(310, 380, "Тригер аномалії: V_sag > 400 мВ або Retries > 4", size=10, color=POS, bold=True))

    # Сплеск діагностики (Burst)
    burst_txs = [360, 415, 470, 525, 580]
    for btx in burst_txs:
        p.append(rect(btx - 16, 405, 32, 48, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
        p.append(text(btx, 424, "12 Б", size=10, color=POS, bold=True))
        p.append(text(btx, 442, "36 мДж", size=9, color=INK))
        p.append(text(btx, 474, "Burst", size=10, color=POS))

    # Відновлення або Blackbox dump
    p.append(rect(680 - 18, 400, 36, 52, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    p.append(text(680, 422, "Dump", size=10, color="#b45309", bold=True))
    p.append(text(680, 440, "Flash", size=9, color=INK))
    p.append(text(680, 474, "Збереження", size=10, color="#b45309"))

    p.append(text(760, 378, "Повний постмортем до знеструмлення", size=11, color="#1d4ed8", bold=True, anchor="end"))

    render(os.path.join(OUT, "piggyback-vs-burst-timeline.svg"), W, H, *p)


def fig_diagnostic_bit_packing():
    """Порозрядна структура компактного 8-байтового діагностичного кадру."""
    W, H = 840, 460
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Порозрядна розкладка 8-байтового діагностичного кадру", size=16, color=INK, bold=True))

    bytes_desc = [
        ("Байт 0: Прапорці статусу та код перезавантаження", [
            ("Reset Cause [7:5]", 3, "#fef3c7", "#b45309", "0:POR, 1:WDT, 2:BOR, 3:Soft, 4:HardFault, 5:Pin"),
            ("LowBatt [4]", 1, "#fee2e2", POS, "1: V < 3.0V"),
            ("RadioRetry [3]", 1, "#fee2e2", POS, "1: PER > 15%"),
            ("FlashErr [2]", 1, "#fee2e2", POS, "1: I/O Fail"),
            ("SensErr [1]", 1, "#fee2e2", POS, "1: I2C NACK"),
            ("Tamper [0]", 1, "#f3e8fd", "#7e22ce", "1: Злам"),
        ], 60),
        ("Байт 1–2: Напруга під навантаженням та просадка (Sag)", [
            ("V_batt [15:8] (8 бітів)", 8, "#dcfce7", FIELD, "Діапазон 2000..4550 мВ з кроком 10 мВ (uint8_t)"),
            ("ΔV_sag [7:0] (8 бітів)", 8, "#fee2e2", POS, "Просадка 0..510 мВ з кроком 2 мВ (R_int = ΔV / I_tx)"),
        ], 160),
        ("Байт 3–4: Якість зв'язку та пам'ять RTOS", [
            ("RSSI & SNR [15:8] (8 бітів)", 8, "#e0f2fe", "#0284c7", "RSSI: -120..-57 dBm (6b) + SNR: -10..+5 dB (2b)"),
            ("Min Free Heap [7:0] (8 бітів)", 8, "#f3e8fd", "#7e22ce", "Вільна купа: 0..64 КБ із квантом 256 байтів"),
        ], 260),
        ("Байт 5–7: Температура кристала та аптайм", [
            ("MCU Temp [23:16] (8 бітів)", 8, "#ffedd5", "#c2410c", "Температура: -40..+87 °C зі зміщенням +40 (uint8_t)"),
            ("Uptime Delta [15:0] (16 бітів)", 16, "#f1f5f9", "#475569", "Дельта годин від базової епохи або інтервалів (0..65535 год)"),
        ], 360),
    ]

    for group_title, fields, y in bytes_desc:
        p.append(rect(30, y, 780, 78, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
        p.append(text(45, y + 20, group_title, size=12, color=INK, bold=True, anchor="start"))

        # Малюємо блоки бітових полів
        total_bits = sum(bits for _, bits, _, _, _ in fields)
        cur_x = 45
        available_w = 750

        for fname, bits, fcol, scol, fdesc in fields:
            bw = (bits / total_bits) * available_w
            p.append(rect(cur_x, y + 28, bw - 6, 42, fill=fcol, stroke=scol, sw=1.2, rx=4))
            p.append(text(cur_x + (bw - 6) / 2, y + 45, fname, size=10, color=scol, bold=True))
            p.append(text(cur_x + (bw - 6) / 2, y + 62, fdesc, size=9, color=INK))
            cur_x += bw

    render(os.path.join(OUT, "diagnostic-bit-packing.svg"), W, H, *p)


if __name__ == "__main__":
    fig_meta_telemetry_breakdown()
    fig_piggyback_vs_burst_timeline()
    fig_diagnostic_bit_packing()
    print("All figures generated successfully.")
