# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. multi-bearer-arch: Багатоканальне резервування під глушінням ───────────
def fig_multi_bearer_arch():
    W, H = 940, 480
    p = []

    # Фон і розділювальні зони
    p.append(rect(20, 20, 900, 440, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Станція керування (GCS)
    p.append(rect(40, 50, 240, 380, fill="#f6f8fa", stroke=LINE, sw=1.5, rx=6))
    p.append(text(160, 80, "Наземна станція (GCS)", size=15, color=INK, bold=True))
    
    # Блоки GCS
    p.append(rect(60, 110, 200, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(160, 132, "Диспетчер лінків (Arbiter)", size=12, color=INK, bold=True))
    p.append(text(160, 148, "Менеджер пріоритетів QoS", size=10, color=MUTED))

    p.append(rect(60, 190, 200, 65, fill="#e9eefb", stroke=NEG, sw=1.5, rx=4))
    p.append(text(160, 212, "Основний трансивер", size=12, color=NEG, bold=True))
    p.append(text(160, 230, "2.4 ГГц Wi-Fi / 5.8 ГГц OFDM", size=10, color=INK))
    p.append(text(160, 246, "Відео (HD) + Повна телеметрія", size=9, color=MUTED))

    p.append(rect(60, 285, 200, 65, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(160, 307, "Резервний трансивер", size=12, color=FIELD, bold=True))
    p.append(text(160, 325, "868 / 915 МГц FSK / LoRa", size=10, color=INK))
    p.append(text(160, 341, "Критичні команди + Статус", size=9, color=MUTED))

    p.append(rect(60, 375, 200, 35, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(160, 397, "Пульт / Навігаційний софт", size=11, color=INK))

    # Зв'язки всередині GCS (акуратні відрізки між блоками)
    p.append(line(160, 160, 160, 190, color=LINE, sw=1.2))
    p.append(line(160, 255, 160, 285, color=LINE, sw=1.2))
    p.append(line(160, 350, 160, 375, color=LINE, sw=1.2))

    # Автономний вузол (БПЛА / Робот)
    p.append(rect(660, 50, 240, 380, fill="#f6f8fa", stroke=LINE, sw=1.5, rx=6))
    p.append(text(780, 80, "Бортовий комп'ютер БПЛА", size=15, color=INK, bold=True))

    p.append(rect(680, 110, 200, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(780, 132, "Диспетчер лінків (Arbiter)", size=12, color=INK, bold=True))
    p.append(text(780, 148, "Оцінка PER, RSSI, RTT", size=10, color=MUTED))

    p.append(rect(680, 190, 200, 65, fill="#e9eefb", stroke=NEG, sw=1.5, rx=4))
    p.append(text(780, 212, "Основний трансивер", size=12, color=NEG, bold=True))
    p.append(text(780, 230, "2.4 ГГц / 5.8 ГГц SDR / PHY", size=10, color=INK))
    p.append(text(780, 246, "Потік камер + Сенсорні дані", size=9, color=MUTED))

    p.append(rect(680, 285, 200, 65, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(780, 307, "Резервний трансивер", size=12, color=FIELD, bold=True))
    p.append(text(780, 325, "Sub-GHz SX1262 / CC1101", size=10, color=INK))
    p.append(text(780, 341, "Вузькосмуговий канал керування", size=9, color=MUTED))

    p.append(rect(680, 375, 200, 35, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(780, 397, "Автопілот (Політний контролер)", size=11, color=INK))

    # Зв'язки всередині БПЛА
    p.append(line(780, 160, 780, 190, color=LINE, sw=1.2))
    p.append(line(780, 255, 780, 285, color=LINE, sw=1.2))
    p.append(line(780, 350, 780, 375, color=LINE, sw=1.2))

    # Простір між ними (Радіоефір)
    # 1. Основний канал (заглушений)
    p.append(line(260, 222, 680, 222, color=NEG, sw=2, dash="6,4"))
    p.append(text(470, 212, "Основний лінк (2.4/5.8 ГГц, 10–50 Мбіт/с)", size=11, color=NEG, bold=True))
    
    # Знак глушіння основного каналу
    p.append(rect(410, 235, 120, 38, fill="#fdf0e6", stroke=POS, sw=1.5, rx=4))
    p.append(text(470, 252, "РЕБ: 2.4/5.8 ГГц", size=10, color=POS, bold=True))
    p.append(text(470, 266, "Завада J/S > 30 дБ (БЛОК)", size=9, color=POS))
    p.append(line(370, 222, 405, 250, color=POS, sw=1.5))
    p.append(line(570, 222, 535, 250, color=POS, sw=1.5))

    # 2. Резервний канал (проходить)
    p.append(line(260, 317, 680, 317, color=FIELD, sw=2.5))
    p.append(text(470, 307, "Резервний лінк (Sub-GHz, 1–50 кбіт/с, LoRa/FSK)", size=11, color=FIELD, bold=True))
    
    # Пояснення успішного проходження
    p.append(rect(390, 335, 160, 38, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(470, 352, "План Б: Живий лінк", size=10, color=FIELD, bold=True))
    p.append(text(470, 366, "Чутливість -135 дБм (OK)", size=9, color=INK))

    render(os.path.join(OUT, "multi-bearer-arch.svg"), W, H, *p,
           title="Архітектура багатоканального резервування лінка")


# ── 2. rf-frontend-coexistence: Співіснування та РЧ-комутація ───────────────
def fig_rf_frontend_coexistence():
    W, H = 940, 440
    p = []

    p.append(rect(20, 20, 900, 400, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # МК / Хост
    p.append(rect(40, 140, 130, 180, fill="#f6f8fa", stroke=LINE, sw=1.5, rx=6))
    p.append(text(105, 175, "Хост МК", size=14, color=INK, bold=True))
    p.append(text(105, 195, "(STM32 / ESP32)", size=10, color=MUTED))
    p.append(text(105, 235, "GPIO перемикання", size=9, color=INK))
    p.append(text(105, 255, "SPI / UART шини", size=9, color=INK))
    p.append(text(105, 275, "Логіка арбітражу", size=9, color=INK))

    # Трансивер 1 (868 МГц)
    p.append(rect(220, 80, 150, 90, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(295, 105, "Sub-GHz SX1262", size=12, color=FIELD, bold=True))
    p.append(text(295, 125, "868 / 915 МГц (+22 дБм)", size=10, color=INK))
    p.append(text(295, 145, "TX/RX порт", size=9, color=MUTED))

    # Трансивер 2 (2.4 ГГц)
    p.append(rect(220, 270, 150, 90, fill="#e9eefb", stroke=NEG, sw=1.5, rx=4))
    p.append(text(295, 295, "2.4 GHz PHY / SoC", size=12, color=NEG, bold=True))
    p.append(text(295, 315, "2400–2483 МГц (+20 дБм)", size=10, color=INK))
    p.append(text(295, 335, "TX/RX порт", size=9, color=MUTED))

    # З'єднання від МК
    p.append(line(170, 125, 220, 125, color=LINE, sw=1.5))
    p.append(text(195, 118, "SPI", size=9, color=MUTED))
    p.append(line(170, 315, 220, 315, color=LINE, sw=1.5))
    p.append(text(195, 308, "SDIO", size=9, color=MUTED))

    # Фільтрація 868 МГц (Смуговий SAW + ФНЧ)
    p.append(rect(420, 80, 130, 90, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(485, 105, "Смуговий SAW", size=11, color=INK, bold=True))
    p.append(text(485, 125, "863–870 МГц", size=10, color=FIELD))
    p.append(text(485, 145, "Подавлення 3-ї", size=9, color=POS, bold=True))
    p.append(text(485, 158, "гармоніки > 45 дБ", size=9, color=POS))
    p.append(line(370, 125, 420, 125, color=FIELD, sw=2))

    # Фільтрація 2.4 ГГц (Смуговий керамічний фільтр)
    p.append(rect(420, 270, 130, 90, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(485, 295, "Керамічний BPF", size=11, color=INK, bold=True))
    p.append(text(485, 315, "2400–2500 МГц", size=10, color=NEG))
    p.append(text(485, 338, "Захист LNA від", size=9, color=MUTED))
    p.append(text(485, 350, "блокування Sub-GHz", size=9, color=MUTED))
    p.append(line(370, 315, 420, 315, color=NEG, sw=2))

    # РЧ-Комутатор (RF SPDT Switch)
    p.append(rect(600, 175, 130, 110, fill="#fdf0e6", stroke="#c07a2e", sw=1.5, rx=6))
    p.append(text(665, 200, "RF SPDT Switch", size=12, color="#c07a2e", bold=True))
    p.append(text(665, 220, "PE4259 / SKY13317", size=9, color=INK))
    p.append(text(665, 240, "Ізоляція > 35 дБ", size=9, color=MUTED))
    p.append(text(665, 258, "Втрати < 0.5 дБ", size=9, color=MUTED))
    p.append(text(665, 274, "Час перемикання < 2 мкс", size=9, color=FIELD, bold=True))

    # З'єднання до RF Switch
    p.append(line(550, 125, 600, 195, color=FIELD, sw=1.8))
    p.append(line(550, 315, 600, 265, color=NEG, sw=1.8))

    # Керування перемикачем від МК
    p.append(line(170, 230, 600, 230, color=POS, sw=1.2, dash="4,4"))
    p.append(text(385, 222, "CTRL (GPIO: 0 = 868 МГц, 1 = 2.4 ГГц)", size=9, color=POS, bold=True))

    # Антена / Диплексер
    p.append(rect(780, 205, 120, 50, fill="#f6f8fa", stroke=LINE, sw=1.5, rx=4))
    p.append(text(840, 228, "Дводіапазонна", size=11, color=INK, bold=True))
    p.append(text(840, 244, "антена (Dual-Band)", size=10, color=MUTED))
    p.append(line(730, 230, 780, 230, color=LINE, sw=2))

    render(os.path.join(OUT, "rf-frontend-coexistence.svg"), W, H, *p,
           title="Апаратна комутація РЧ-трактів та захист від інтермодуляції")


# ── 3. relay-geometry-and-mesh: Естафетна ретрансляція ───────────────────────
def fig_relay_geometry_and_mesh():
    W, H = 940, 460
    p = []

    p.append(rect(20, 20, 900, 420, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Рельєф місцевості (Пагорб/Завада)
    p.append('<path d="M 20 400 Q 300 400 440 280 Q 520 200 580 280 Q 700 400 920 400 L 920 440 L 20 440 Z" fill="#eef1f5" stroke="#cbd5e1" stroke-width="1.5"/>')
    p.append(text(510, 320, "Пагорб / Рельєф / Будівлі", size=12, color=MUTED, italic=True))
    p.append(text(510, 340, "Перекриття прямої видимості (LOS)", size=10, color=POS))

    # Наземний пункт керування (GCS)
    p.append(rect(50, 320, 140, 65, fill="#f6f8fa", stroke=LINE, sw=1.5, rx=4))
    p.append(text(120, 342, "Наземний пункт (GCS)", size=11, color=INK, bold=True))
    p.append(text(120, 360, "Висота h = 2 м", size=10, color=MUTED))
    p.append(text(120, 374, "Вузол 0 (Джерело)", size=9, color=FIELD))

    # Наземний комплекс РЕБ біля перешкоди
    p.append(rect(320, 340, 120, 50, fill="#fdf0e6", stroke=POS, sw=1.5, rx=4))
    p.append(text(380, 360, "Наземний РЕБ", size=10, color=POS, bold=True))
    p.append(text(380, 376, "Купол завад 2.4G", size=9, color=POS))

    # Прямий шлях (заблокований)
    p.append(line(190, 340, 750, 340, color=POS, sw=1.5, dash="4,4"))
    p.append(text(470, 245, "Прямий лінк заблоковано рельєфом та РЕБ ✖", size=10, color=POS, bold=True))

    # Дрон-ретранслятор (Airborne Relay)
    p.append(rect(400, 50, 180, 75, fill="#e9eefb", stroke=NEG, sw=1.8, rx=6))
    p.append(text(490, 75, "Дрон-ретранслятор", size=13, color=NEG, bold=True))
    p.append(text(490, 95, "Висота H = 300 м (Пряма видимість)", size=10, color=INK))
    p.append(text(490, 112, "Вузол 1 (Store & Forward / Mesh)", size=9, color=MUTED))

    # Цільовий дрон у низині
    p.append(rect(740, 320, 150, 65, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(815, 342, "Цільовий БПЛА / Робот", size=11, color=FIELD, bold=True))
    p.append(text(815, 360, "Висота h = 30 м у низині", size=10, color=INK))
    p.append(text(815, 374, "Вузол 2 (Приймач)", size=9, color=MUTED))

    # Естафетні промені зв'язку
    # Плече 1: GCS -> Relay
    p.append(line(170, 320, 420, 125, color=FIELD, sw=2.2))
    p.append(text(260, 210, "Плече 1 (Up-link)", size=11, color=FIELD, bold=True))
    p.append(text(260, 226, "Зона Френеля вільна", size=9, color=MUTED))
    p.append(text(260, 240, "SNR = +22 дБ", size=9, color=FIELD))

    # Плече 2: Relay -> Target UAV
    p.append(line(560, 125, 770, 320, color=FIELD, sw=2.2))
    p.append(text(710, 210, "Плече 2 (Down-link)", size=11, color=FIELD, bold=True))
    p.append(text(710, 226, "Обхід купола завад згори", size=9, color=MUTED))
    p.append(text(710, 240, "SNR = +18 дБ", size=9, color=FIELD))

    # Додатковий mesh-вузол
    p.append(rect(730, 80, 140, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(800, 102, "Сусідній БПЛА (Вузол 3)", size=10, color=INK, bold=True))
    p.append(text(800, 120, "Альтернативний ретранслятор", size=9, color=MUTED))
    p.append(line(580, 87, 730, 100, color=MUTED, sw=1.2, dash="3,3"))
    p.append(line(800, 135, 815, 320, color=MUTED, sw=1.2, dash="3,3"))

    render(os.path.join(OUT, "relay-geometry-and-mesh.svg"), W, H, *p,
           title="Геометрія естафетної ретрансляції та обхід тіньових зон РЕБ")


# ── 4. arbiter-state-machine: Автомат станів диспетчера лінків ───────────────
def fig_arbiter_state_machine():
    W, H = 940, 480
    p = []

    p.append(rect(20, 20, 900, 440, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Стан 1: PRIMARY_HEALTHY
    p.append(rect(50, 80, 220, 100, fill="#e9eefb", stroke=NEG, sw=2, rx=6))
    p.append(text(160, 110, "1. PRIMARY_ACTIVE", size=13, color=NEG, bold=True))
    p.append(text(160, 130, "Швидкісний канал 2.4/5.8 ГГц", size=10, color=INK))
    p.append(text(160, 146, "Відео HD 1080p + Телеметрія", size=9, color=MUTED))
    p.append(text(160, 162, "PER < 5%, RTT < 30 мс", size=9, color=FIELD, bold=True))

    # Стан 2: PRIMARY_DEGRADED
    p.append(rect(360, 80, 220, 100, fill="#fdf0e6", stroke="#c07a2e", sw=2, rx=6))
    p.append(text(470, 110, "2. PRIMARY_DEGRADED", size=13, color="#c07a2e", bold=True))
    p.append(text(470, 130, "Початок глушіння або затухання", size=10, color=INK))
    p.append(text(470, 146, "Стиснення: відео 360p, FEC ×2", size=9, color=MUTED))
    p.append(text(470, 162, "5% ≤ PER < 25%, RSSI падає", size=9, color="#c07a2e", bold=True))

    # Стан 3: FALLBACK_ACTIVE
    p.append(rect(670, 80, 220, 100, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    p.append(text(780, 110, "3. FALLBACK_ACTIVE", size=13, color=FIELD, bold=True))
    p.append(text(780, 130, "Резервний Sub-GHz LoRa/FSK", size=10, color=INK))
    p.append(text(780, 146, "Відео вимкнено, лише MAVLink", size=9, color=MUTED))
    p.append(text(780, 162, "Критичне керування втримано", size=9, color=FIELD, bold=True))

    # Стан 4: RECOVERY_EVALUATION
    p.append(rect(510, 290, 230, 100, fill="#f6f8fa", stroke=LINE, sw=1.8, rx=6))
    p.append(text(625, 320, "4. RECOVERY_EVAL (Гістерезис)", size=12, color=INK, bold=True))
    p.append(text(625, 340, "Перевірка стабільності Primary", size=10, color=MUTED))
    p.append(text(625, 356, "Таймер утримання: 5000 мс", size=9, color=INK))
    p.append(text(625, 372, "Потрібно: 50 пакетів без втрат", size=9, color=FIELD))

    # Стан 5: EMERGENCY_AUTONOMY
    p.append(rect(140, 290, 230, 100, fill="#fdf0e6", stroke=POS, sw=2, rx=6))
    p.append(text(255, 320, "5. EMERGENCY_AUTONOMY", size=12, color=POS, bold=True))
    p.append(text(255, 340, "Усі канали зв'язку заглушено", size=10, color=INK))
    p.append(text(255, 356, "Failsafe: Набір висоти / RTH", size=9, color=POS, bold=True))
    p.append(text(255, 372, "Інерціальна автономія без GNSS", size=9, color=MUTED))

    # Переходи між станами зі стрілками й умовами
    # 1 -> 2
    p.append(line(270, 120, 360, 120, color=LINE, sw=1.5))
    p.append(text(315, 110, "PER > 5%", size=9, color=POS))

    # 2 -> 1
    p.append(line(360, 145, 270, 145, color=LINE, sw=1.5))
    p.append(text(315, 160, "PER < 2%", size=9, color=FIELD))

    # 2 -> 3
    p.append(line(580, 120, 670, 120, color=POS, sw=1.8))
    p.append(text(625, 110, "PER > 25% / 5 втрат", size=9, color=POS, bold=True))

    # 3 -> 4
    p.append(line(780, 180, 680, 290, color=FIELD, sw=1.5))
    p.append(text(760, 240, "Primary знову чути", size=9, color=FIELD))

    # 4 -> 1
    p.append(line(510, 330, 220, 180, color=FIELD, sw=1.8))
    p.append(text(330, 240, "Успіх гістерезису (5 с стабільності)", size=9, color=FIELD, bold=True))

    # 4 -> 3
    p.append(line(680, 290, 750, 180, color=POS, sw=1.2, dash="3,3"))
    p.append(text(685, 230, "Зрив тесту", size=9, color=POS))

    # 3 -> 5
    p.append(line(710, 180, 340, 290, color=POS, sw=2))
    p.append(text(500, 270, "Втрата Sub-GHz > 3000 мс (Повний обрив)", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "arbiter-state-machine.svg"), W, H, *p,
           title="Автомат станів динамічного арбітражу радіоканалів")


# ── 5. scoring-hysteresis: Часова діаграма арбітражу та гістерезис ────────────
def fig_scoring_hysteresis():
    W, H = 940, 450
    p = []

    p.append(rect(20, 20, 900, 410, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    x0, y0 = 90, 350
    xw, yh = 790, 240

    # Сітка та порогові лінії
    for pct, lab in [(1.0, "100%"), (0.75, "75%"), (0.5, "50%"), (0.25, "25%"), (0.0, "0%")]:
        yy = y0 - pct * yh
        p.append(line(x0, yy, x0 + xw, yy, color="#e5e7eb", sw=1))
        p.append(text(x0 - 10, yy + 4, lab, size=9, color=MUTED, anchor="end"))

    # Осі
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh - 20, color=INK, sw=1.8))
    p.append(text(x0 + xw, y0 + 22, "Час (секунди) →", size=10, color=MUTED, anchor="end"))
    p.append(text(x0 - 10, y0 - yh - 12, "Оцінка якості лінка (Link Score)", size=10, color=INK, anchor="start", bold=True))

    # Пороги перемикання
    # Поріг перемикання вниз (Failover threshold = 35%)
    y_down = y0 - 0.35 * yh
    p.append(line(x0, y_down, x0 + xw, y_down, color=POS, sw=1.5, dash="5,4"))
    p.append(text(x0 + xw - 10, y_down - 6, "Поріг аварійного перемикання (Failover ≤ 35%)", size=9, color=POS, anchor="end", bold=True))

    # Поріг повернення назад (Recovery threshold = 75%)
    y_up = y0 - 0.75 * yh
    p.append(line(x0, y_up, x0 + xw, y_up, color=FIELD, sw=1.5, dash="5,4"))
    p.append(text(x0 + xw - 10, y_up - 6, "Поріг повернення на Primary (Recovery ≥ 75%)", size=9, color=FIELD, anchor="end", bold=True))

    # Графік 1: Primary Link Score (2.4 ГГц) - падає під РЕБ, потім відновлюється
    pts_prim = [
        (0, 0.92), (1.5, 0.90), (2.5, 0.78), (3.2, 0.55), (3.8, 0.28), (4.2, 0.12),
        (6.0, 0.10), (7.5, 0.15), (8.5, 0.65), (9.2, 0.82), (10.5, 0.85), (12.0, 0.88), (14.0, 0.92)
    ]
    t_max = 14.0
    def tx(t): return x0 + (t / t_max) * xw
    def ty(s): return y0 - s * yh

    svg_prim = " ".join("%.1f,%.1f" % (tx(t), ty(s)) for t, s in pts_prim)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (svg_prim, NEG))

    # Графік 2: Fallback Link Score (868 МГц LoRa) - стабільний ~80%
    pts_fall = [
        (0, 0.80), (3.0, 0.78), (4.0, 0.75), (6.0, 0.77), (8.0, 0.76), (11.0, 0.79), (14.0, 0.80)
    ]
    svg_fall = " ".join("%.1f,%.1f" % (tx(t), ty(s)) for t, s in pts_fall)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,3"/>' % (svg_fall, FIELD))

    # Позначки подій на часовій осі
    # 1. Подія: Стрибок РЕБ (t=3.8s, перетин 35%)
    x_switch_down = tx(3.7)
    p.append(line(x_switch_down, y0, x_switch_down, y0 - yh, color=POS, sw=1.5, dash="2,2"))
    p.append(circle(x_switch_down, ty(0.35), 5, fill=POS, stroke="#ffffff", sw=2))
    p.append(rect(x_switch_down - 65, y0 - yh - 15, 130, 32, fill="#fdf0e6", stroke=POS, sw=1.2, rx=4))
    p.append(text(x_switch_down, y0 - yh - 2, "Миттєвий перехід", size=9, color=POS, bold=True))
    p.append(text(x_switch_down, y0 - yh + 10, "на Fallback (200 мс)", size=9, color=POS))

    # 2. Подія: Інтервал гістерезису (t=9.0s..13.0s)
    x_recov_start = tx(9.0)
    x_recov_end = tx(13.0)
    p.append(line(x_recov_start, y0, x_recov_start, y0 - yh + 15, color=FIELD, sw=1.2, dash="3,3"))
    p.append(line(x_recov_end, y0, x_recov_end, y0 - yh - 15, color=FIELD, sw=1.5, dash="2,2"))
    
    # Інтервальна стрілка гістерезису
    p.append(line(x_recov_start, y0 - yh + 20, x_recov_end, y0 - yh + 20, color=FIELD, sw=1.8))
    p.append(line(x_recov_start, y0 - yh + 14, x_recov_start, y0 - yh + 26, color=FIELD, sw=1.8))
    p.append(line(x_recov_end, y0 - yh + 14, x_recov_end, y0 - yh + 26, color=FIELD, sw=1.8))
    p.append(text((x_recov_start + x_recov_end) / 2, y0 - yh + 14, "Таймер гістерезису: 4.0 с", size=9, color=FIELD, bold=True))

    # 3. Подія: Повернення на Primary (t=13.0s)
    p.append(circle(x_recov_end, ty(0.90), 5, fill=FIELD, stroke="#ffffff", sw=2))
    p.append(rect(x_recov_end - 60, y0 - yh - 15, 120, 32, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x_recov_end, y0 - yh - 2, "Повернення на", size=9, color=FIELD, bold=True))
    p.append(text(x_recov_end, y0 - yh + 10, "Primary (Відео ON)", size=9, color=FIELD))

    # Легенда
    p.append(rect(x0 + 20, y0 + 10, 340, 24, fill="#ffffff", stroke="#d0d7de", sw=1, rx=3))
    p.append(line(x0 + 30, y0 + 22, x0 + 55, y0 + 22, color=NEG, sw=2.5))
    p.append(text(x0 + 60, y0 + 25, "Основний (2.4G)", size=9, color=INK, anchor="start"))
    p.append(line(x0 + 160, y0 + 22, x0 + 185, y0 + 22, color=FIELD, sw=2.2, dash="4,3"))
    p.append(text(x0 + 190, y0 + 25, "Резервний (868M LoRa)", size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "scoring-hysteresis.svg"), W, H, *p,
           title="Динаміка оцінки якості лінка, поріг аварії та гістерезис відновлення")


if __name__ == "__main__":
    fig_multi_bearer_arch()
    fig_rf_frontend_coexistence()
    fig_relay_geometry_and_mesh()
    fig_arbiter_state_machine()
    fig_scoring_hysteresis()
    print("All 5 figures generated successfully.")
