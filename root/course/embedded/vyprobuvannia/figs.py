# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_flash_torn_write():
    W, H = 760, 430
    p = []

    # Заголовок / розділ: Наївний прямий перезапис vs Атомарний WAL / Shadow Sector
    left_x = 200
    p.append(rect(25, 20, 350, 390, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(left_x, 50, "Наївний прямий запис у сектор", size=15, color=POS, bold=True))
    
    # Кроки наївного запису
    b1, w1, h1 = textbox(left_x, 95, "1. Стерти сектор Flash (4 КБ)\n[усі байти = 0xFF, триває ~40-200 мс]", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b1)
    
    b2, w2, h2 = textbox(left_x, 170, "2. Програмування сторінки...\n[тунелювання електронів у комірки]", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b2)
    
    # Блискавка / Обрив живлення
    p.append(rect(45, 220, 310, 80, fill="#fde8e8", stroke=POS, sw=2, rx=6))
    p.append(text(left_x, 245, "⚡ ОБРИВ ЖИВЛЕННЯ (V_DD < 2.7 В)", size=12, color=POS, bold=True))
    p.append(text(left_x, 268, "Неповний заряд у плаваючих затворах", size=11, color=INK))
    p.append(text(left_x, 286, "Метастабільний біт · Torn Write · Битий сектор", size=10, color=POS, italic=True))
    
    b3, w3, h3 = textbox(left_x, 360, "Наслідок: втрата старих і нових даних,\nфайлова система не монтується (panic)", size=11, fill="#fce4ec", stroke=POS, pad=6)
    p.append(b3)

    # Права колонка: Атомарний журнал (WAL) + CRC32
    right_x = 560
    p.append(rect(395, 20, 345, 390, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(right_x, 50, "Атомарний журнал (WAL) + CRC32", size=15, color=FIELD, bold=True))

    b4, w4, h4 = textbox(right_x, 95, "Сектор A (Активний стан)\n[валідний стан N, CRC32 OK]", size=11, fill="#ffffff", stroke=FIELD, pad=6)
    p.append(b4)

    b5, w5, h5 = textbox(right_x, 170, "Запис нового запису в кінець логу\n[Header | Payload | CRC32 | CommitFlag]", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b5)

    # Обрив живлення
    p.append(rect(410, 220, 315, 80, fill="#e8f5e9", stroke=FIELD, sw=2, rx=6))
    p.append(text(right_x, 245, "⚡ ОБРИВ ЖИВЛЕННЯ ПІД ЧАС ЗАПИСУ", size=12, color=POS, bold=True))
    p.append(text(right_x, 268, "Хвіст не має валідного CRC32 або CommitFlag", size=11, color=INK))
    p.append(text(right_x, 286, "Відновлення відкидає лише неповний хвіст", size=10, color=FIELD, italic=True))

    b6, w6, h6 = textbox(right_x, 360, "Наслідок: гарантований відкат до стану N,\nнуль битих секторів, безпечний старт", size=11, fill="#e8f8f0", stroke=FIELD, pad=6)
    p.append(b6)

    render(os.path.join(IMG, 'flash-torn-write.svg'), W, H, *p,
           title="Поведінка Flash під час раптового обриву живлення: прямий запис проти журналу")


def fig_network_chaos_matrix():
    W, H = 760, 440
    p = []

    # Центр тестування Chaos Test Orchestrator
    cx = 380
    p.append(rect(20, 20, 720, 400, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(cx, 45, "Стенд наскрізного хаос-тестування (Chaos HIL Harness)", size=16, color=INK, bold=True))

    # Лівий блок: Тестовий оркестратор (Python / Pytest)
    bx_orch = 150
    p.append(rect(40, 80, 220, 310, fill="#f4f6f8", stroke=NEG, sw=1.5, rx=6))
    p.append(text(bx_orch, 108, "Тестовий хост (Pytest)", size=14, color=NEG, bold=True))
    
    b_act1, _, _ = textbox(bx_orch, 155, "1. Керування реле живлення\n[MOSFET / Smart Relay]", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b_act1)
    
    b_act2, _, _ = textbox(bx_orch, 230, "2. Ін'єкція tc-netem\n[drop, delay, jitter, split]", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b_act2)

    b_act3, _, _ = textbox(bx_orch, 315, "3. Збір логів UART + MQTT\n[перевірка послідовностей]", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b_act3)

    # Середній блок: Об'єкт тестування (DUT: Node & Gateway)
    bx_dut = 380
    p.append(rect(290, 80, 180, 310, fill="#fffaf0", stroke="#b8860b", sw=1.5, rx=6))
    p.append(text(bx_dut, 108, "Пристрій (DUT)", size=14, color="#b8860b", bold=True))
    
    b_node, _, _ = textbox(bx_dut, 160, "IoT-вузол (ESP32/STM32)\n- Flash Ring Buffer\n- Monotonic SeqID\n- Dual-Lane MQTT", size=10.5, fill="#ffffff", stroke=MUTED, pad=5)
    p.append(b_node)

    b_gw, _, _ = textbox(bx_dut, 275, "Шлюз / Edge Linux\n- Bridged Network\n- Local Cache\n- Ingress tc qdisc", size=10.5, fill="#ffffff", stroke=MUTED, pad=5)
    p.append(b_gw)

    p.append(arrow(bx_dut, 205, bx_dut, 235, color=LINE, sw=1.5))

    # Правий блок: Хмарний бекенд / Брокер / Сховище
    bx_cloud = 600
    p.append(rect(500, 80, 220, 310, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(bx_cloud, 108, "Бекенд та Інгресс", size=14, color=FIELD, bold=True))

    b_brk, _, _ = textbox(bx_cloud, 155, "MQTT Брокер\n[EMQX / Mosquitto]\n- Last Will & Testament", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b_brk)

    b_srv, _, _ = textbox(bx_cloud, 240, "Служба прийому\n- Дедуплікація (LRU)\n- Time-series Ingest", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b_srv)

    b_db, _, _ = textbox(bx_cloud, 325, "Сховище даних (TSDB)\n[Асерція цілісності]", size=11, fill="#ffffff", stroke=FIELD, pad=6)
    p.append(b_db)

    # Лінії взаємодії між блоками
    p.append(arrow(260, 230, 290, 275, color=POS, sw=2))
    p.append(text(275, 242, "netem", size=10, color=POS, bold=True))

    p.append(arrow(260, 155, 290, 160, color=POS, sw=2))
    p.append(text(275, 148, "power cut", size=10, color=POS, bold=True))

    p.append(arrow(470, 275, 500, 160, color=NEG, sw=2))
    p.append(text(485, 210, "MQTT/TLS", size=10, color=NEG))

    p.append(arrow(260, 335, 500, 335, color=FIELD, sw=1.8))
    p.append(text(380, 350, "Асерція: SeqID неперервні, дублікати відфільтровано", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, 'network-chaos-matrix.svg'), W, H, *p,
           title="Схема стенду наскрізного хаос-тестування IoT-системи")


def fig_clock_dual_time():
    W, H = 760, 420
    p = []

    # Верхня доріжка: Астрономічний час (Wall Clock / RTC) із стрибками
    p.append(rect(20, 25, 720, 175, fill="#fff8f8", stroke=POS, sw=1.5, rx=8))
    p.append(text(190, 52, "Астрономічний час (RTC / gettimeofday)", size=14, color=POS, bold=True))
    p.append(text(540, 52, "⚠ Немонотонний: стрибки NTP, скидання в 1970, дрейф кварцу", size=11, color=MUTED))

    # Вісь часу угорі
    p.append(line(50, 105, 700, 105, color=LINE, sw=2))
    p.append(arrow(690, 105, 715, 105, color=LINE, sw=2))

    # Точки часу
    p.append(circle(120, 105, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(120, 85, "12:00:00", size=11, color=INK, bold=True))
    p.append(text(120, 130, "Подія A", size=11, color=INK))

    p.append(circle(260, 105, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(260, 85, "12:00:05", size=11, color=INK, bold=True))
    p.append(text(260, 130, "Подія B", size=11, color=INK))

    # Стрибок назад через NTP корекцію або скидання
    p.append(circle(430, 105, 6, fill="#ffffff", stroke=POS, sw=2.5))
    p.append(text(430, 78, "11:59:58 ⚡", size=11, color=POS, bold=True))
    p.append(text(430, 130, "Подія C (NTP -7с)", size=11, color=POS, bold=True))
    p.append(text(430, 150, "dt < 0! Злам PID / TSDB", size=10, color=POS, italic=True))

    p.append(circle(590, 105, 5, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(590, 85, "12:00:03", size=11, color=INK, bold=True))
    p.append(text(590, 130, "Подія D", size=11, color=INK))

    # Нижня доріжка: Монотонний час та порядковий номер (SeqID)
    p.append(rect(20, 220, 720, 175, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(190, 247, "Монотонний час та Sequence ID", size=14, color=FIELD, bold=True))
    p.append(text(540, 247, "✓ Строго монотонний: dt > 0 завжди, стабільний причинний порядок", size=11, color=FIELD))

    # Вісь часу внизу
    p.append(line(50, 300, 700, 300, color=LINE, sw=2))
    p.append(arrow(690, 300, 715, 300, color=LINE, sw=2))

    # Точки монотонного часу
    p.append(circle(120, 300, 5, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(text(120, 280, "seq=101 · t=1000мс", size=11, color=INK, bold=True))
    p.append(text(120, 325, "Подія A", size=11, color=INK))

    p.append(circle(260, 300, 5, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(text(260, 280, "seq=102 · t=6000мс", size=11, color=INK, bold=True))
    p.append(text(260, 325, "Подія B", size=11, color=INK))

    p.append(circle(430, 300, 5, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(text(430, 280, "seq=103 · t=11000мс", size=11, color=FIELD, bold=True))
    p.append(text(430, 325, "Подія C (dt=+5000мс)", size=11, color=FIELD, bold=True))
    p.append(text(430, 345, "Порядок A → B → C збережено", size=10, color=FIELD))

    p.append(circle(590, 300, 5, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(text(590, 280, "seq=104 · t=16000мс", size=11, color=INK, bold=True))
    p.append(text(590, 325, "Подія D", size=11, color=INK))

    # Зв'язок
    p.append(line(430, 165, 430, 260, color=POS, sw=1.5, dash="4 4"))

    render(os.path.join(IMG, 'clock-dual-time.svg'), W, H, *p,
           title="Розсинхронізація часу: немонотонний астрономічний годинник проти монотонного лічильника")


def fig_reconnect_storm_drain():
    W, H = 760, 430
    p = []

    # Порівняння: Злив без обмеження (Storm) vs Двосмуговий злив (Dual-Lane Rate Limiting)
    cx_left = 195
    p.append(rect(20, 20, 350, 390, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(cx_left, 50, "Некерований злив буфера", size=14, color=POS, bold=True))

    b1, _, _ = textbox(cx_left, 100, "1000 вузлів відновили Wi-Fi\nпісля 24-годинного обриву", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b1)

    b2, _, _ = textbox(cx_left, 185, "Одночасний злив 100% накопичених\nпакетів на максимальній швидкості QoS 1\n[Шторм запитів → Переповнення сокетів]", size=10.5, fill="#fde8e8", stroke=POS, pad=6)
    p.append(b2)

    b3, _, _ = textbox(cx_left, 280, "Колапс брокера:\n- CPU 100%, вичерпання RAM\n- Втрата свіжих real-time телеметрій\n- Тайм-аути ACK і каскадні повтори", size=10.5, fill="#ffffff", stroke=POS, pad=6)
    p.append(b3)

    b4, _, _ = textbox(cx_left, 365, "Результат: каскадна відмова системи", size=11, fill="#fce4ec", stroke=POS, bold=True, pad=6)
    p.append(b4)

    cx_right = 565
    p.append(rect(390, 20, 350, 390, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(cx_right, 50, "Двосмуговий злив із Jitter Backoff", size=14, color=FIELD, bold=True))

    b5, _, _ = textbox(cx_right, 100, "1000 вузлів відновлюють зв'язок\nіз рандомізованою затримкою (Jitter)", size=11, fill="#ffffff", stroke=MUTED, pad=6)
    p.append(b5)

    # Дві смуги
    p.append(rect(405, 145, 320, 115, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(cx_right, 168, "Пріоритетний розподіл трафіку:", size=11, color=FIELD, bold=True))
    p.append(text(cx_right, 192, "🟢 Смуга 1 (Live): 100% свіжі виміри (QoS 0/1)", size=10.5, color=FIELD))
    p.append(text(cx_right, 214, "🔵 Смуга 2 (Replay): обмежений потік з Flash", size=10.5, color=NEG))
    p.append(text(cx_right, 236, "[Token Bucket: макс. 5 пакт/с, пачками по 10]", size=10, color=MUTED, italic=True))

    b7, _, _ = textbox(cx_right, 305, "Брокер працює в штатному режимі:\n- Свіжі дані доходять без затримок\n- Буфер спокійно вичерпується за 30 хв", size=10.5, fill="#ffffff", stroke=FIELD, pad=6)
    p.append(b7)

    b8, _, _ = textbox(cx_right, 365, "Результат: передбачувана самостабілізація", size=11, fill="#e8f8f0", stroke=FIELD, bold=True, pad=6)
    p.append(b8)

    render(os.path.join(IMG, 'reconnect-storm-drain.svg'), W, H, *p,
           title="Відновлення зв'язку після збою: шторм повторів проти керованого двосмугового викачування")


if __name__ == '__main__':
    fig_flash_torn_write()
    fig_network_chaos_matrix()
    fig_clock_dual_time()
    fig_reconnect_storm_drain()
    print("All figures generated successfully.")
