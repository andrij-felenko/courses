# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. config-anatomy: анатомія конфігураційного параметра ─────────────────────
def fig_config_anatomy():
    W, H = 940, 500
    p = []

    # Ліва колонка: Метадані дескриптора параметра (Flash ROM)
    p.append(rect(40, 55, 420, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    p.append(text(250, 82, "Статичний дескриптор у Flash (const schema)", size=13, bold=True, color=NEG))

    p.append(fitbox(60, 100, 380, 46, "Ключ (Key ID & Name):\n0x1004 / \"telemetry_interval_s\"", size=11, fill="#e9eefb", stroke=NEG, bold=True))
    p.append(fitbox(60, 156, 380, 46, "Тип даних (Type Tag):\nTYPE_UINT32 (4 байти, беззнакове ціле)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(60, 212, 380, 54, "Межі значень (Validation Bounds):\nmin = 1 c,  max = 86400 c (24 год)", size=11, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(60, 276, 380, 46, "Типове значення (Default Fallback):\ndefault_val = 60 c (1 вимір на хвилину)", size=11, fill="#fdfaf3", stroke="#c07a2e"))
    p.append(fitbox(60, 332, 380, 46, "Прапорці доступу (Flags):\nFLAG_REBOOT_REQ | FLAG_RUNTIME_READ", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(60, 388, 380, 72, "Реляційні правила (Cross-field):\ntelemetry_interval_s <= ping_timeout_s / 2\n(захист від хибного спрацювання watchdog зв'язку)", size=10.5, fill="#fdeded", stroke=POS, bold=True))

    # Права колонка: Стан параметра в оперативній та Flash-пам'яті
    p.append(rect(480, 55, 420, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    p.append(text(690, 82, "Шари зберігання та виконання в runtime", size=13, bold=True, color=FIELD))

    p.append(fitbox(500, 100, 380, 60, "Активна робоча копія (RAM Active Slot):\nuint32_t val = 30; // використовується підсистемами\nШвидкий прямий доступ за 1 такт CPU без Flash read", size=10.5, fill="#eef6ef", stroke=FIELD, bold=True))
    
    p.append(fitbox(500, 170, 380, 60, "Кандидат на випробуванні (RAM Candidate):\nuint32_t candidate_val = 10; // Trial Run 60s\nПідлягає відкату у разі збою мережевого лінка", size=10.5, fill="#e9eefb", stroke=NEG, bold=True))

    p.append(fitbox(500, 240, 380, 75, "Енергонезалежна копія у Flash NVS:\nЗміщення: offset 0x0024 у блоці конфігурації\nЗахист цілісності: охоплений єдиною CRC32\nВерсія схеми: Schema v2 (збережено при міграції)", size=10.5, fill="#ffffff", stroke="#64748b"))

    p.append(fitbox(500, 325, 380, 135, "Поведінка при пошкодженні комірки Flash:\n1. Виявлення розбіжності CRC32 блоку\n2. Зчитування резервного слота (Slot B Ping-Pong)\n3. При тотальній відмові — підстановка default_val = 60\n4. Фіксація аварійної події у системному журналі", size=10, fill="#fdfaf3", stroke="#d97706"))

    render(os.path.join(OUT, "config-anatomy.svg"), W, H, *p,
           title="Анатомія параметра конфігурації: метадані, діапазони, пам'ять і зв'язки")


# ── 2. trial-run-fsm: скінченний автомат Trial Run та безпечного відкату ────────
def fig_trial_run_fsm():
    W, H = 940, 580
    p = []

    # Стан 1: ACTIVE (Штатний робочий режим)
    p.append(fitbox(40, 75, 230, 115, "1. CONFIG_ACTIVE\nШтатна конфігурація\n\n• Працює стабільний профіль\n• Зв'язок із сервером активний\n• Flash містить валідний слот", size=10.5, fill="#eef6ef", stroke=FIELD, bold=True))

    # Стан 2: STAGED (Валідація та підготовка)
    p.append(fitbox(355, 75, 230, 115, "2. CONFIG_STAGED\nОтримано кандидата\n\n• Перевірка синтаксису і меж\n• Крос-валідація залежностей\n• Резервування RAM під відкат", size=10.5, fill="#e9eefb", stroke=NEG, bold=True))

    # Стан 3: TRIAL_RUNNING (Випробувальний період)
    p.append(fitbox(670, 75, 230, 115, "3. TRIAL_RUNNING\nВипробувальний режим\n\n• Застосовано кандидата\n• Запущено таймер trial = 60 c\n• Спроба підключення до лінка", size=10.5, fill="#fdfaf3", stroke="#d97706", bold=True))

    # Стан 4: COMMITTED (Фіксація успіху)
    p.append(fitbox(670, 310, 230, 115, "4. CONFIG_COMMITTED\nУспішна фіксація\n\n• Хмарний handshake пройдено\n• Запис у Flash NVS (новий Seq)\n• Кандидат стає ACTIVE", size=10.5, fill="#eef6ef", stroke=FIELD, bold=True))

    # Стан 5: ROLLBACK (Аварійний відкат)
    p.append(fitbox(355, 310, 230, 115, "5. CONFIG_ROLLBACK\nАвтоматичний відкат\n\n• Відновлення старого профілю\n• Переініціалізація радіомодуля\n• Звіт на сервер про помилку", size=10.5, fill="#fdeded", stroke=POS, bold=True))

    # Стрілки переходів
    # 1 -> 2 (Отримано нову конфігурацію)
    p.append(line(270, 132, 355, 132, color=NEG, sw=2))
    p.append('<polygon points="355,132 347,128 347,136" fill="%s"/>' % NEG)
    p.append(text(312, 118, "Rx Config", size=10, bold=True, color=NEG))

    # 2 -> 3 (Валідація OK -> Запуск Trial)
    p.append(line(585, 132, 670, 132, color=NEG, sw=2))
    p.append('<polygon points="670,132 662,128 662,136" fill="%s"/>' % NEG)
    p.append(text(627, 118, "Valid: OK", size=10, bold=True, color=FIELD))

    # 2 -> 1 (Валідація Failed -> Відхилення)
    p.append(line(470, 75, 470, 48, color=POS, sw=1.8, dash="3,3"))
    p.append(line(470, 48, 155, 48, color=POS, sw=1.8, dash="3,3"))
    p.append(line(155, 48, 155, 75, color=POS, sw=1.8, dash="3,3"))
    p.append('<polygon points="155,75 151,67 159,67" fill="%s"/>' % POS)
    p.append(text(312, 42, "Помилка валідації: відхилити запит", size=9.5, bold=True, color=POS))

    # 3 -> 4 (Зв'язок підтверджено -> Commit)
    p.append(line(785, 190, 785, 310, color=FIELD, sw=2))
    p.append('<polygon points="785,310 781,302 789,302" fill="%s"/>' % FIELD)
    p.append(text(845, 245, "Handshake OK\nта підтвердження", size=10, bold=True, color=FIELD))

    # 3 -> 5 (Таймаут 60 с / Watchdog / Reboot)
    p.append(line(670, 185, 545, 310, color=POS, sw=2))
    p.append('<polygon points="545,310 548,300 556,307" fill="%s"/>' % POS)
    p.append(text(635, 270, "Таймаут 60 с / Збій лінка", size=10, bold=True, color=POS))

    # 4 -> 1 (Повернення до штатного режиму: обхід знизу)
    p.append(line(785, 425, 785, 455, color=FIELD, sw=1.8, dash="4,4"))
    p.append(line(785, 455, 155, 455, color=FIELD, sw=1.8, dash="4,4"))
    p.append(line(155, 455, 155, 190, color=FIELD, sw=1.8, dash="4,4"))
    p.append('<polygon points="155,190 151,198 159,198" fill="%s"/>' % FIELD)
    p.append(text(470, 444, "Новий стан зафіксовано у Flash (Commit завершено)", size=10, color=FIELD, bold=True))

    # 5 -> 1 (Відновлення завершено)
    p.append(line(355, 367, 155, 367, color=POS, sw=1.8, dash="3,3"))
    p.append(line(155, 367, 155, 190, color=POS, sw=1.8, dash="3,3"))
    p.append('<polygon points="155,190 151,198 159,198" fill="%s"/>' % POS)
    p.append(text(255, 355, "Відкат до старого профілю", size=10, color=POS, bold=True))

    # Пояснювальний блок унизу
    p.append(fitbox(40, 490, 860, 65, "Принцип відмовостійкості: Якщо пристрій зависає або перезавантажується під час випробувального режиму (Trial),\nзавантажувач та модуль конфігурації бачать незавершений прапорець випробування і миттєво повертають останній відомий справний профіль.", size=10, fill="#ffffff", stroke="#cbd5e1"))

    render(os.path.join(OUT, "trial-run-fsm.svg"), W, H, *p,
           title="Автомат безпечного застосування конфігурації (Trial Run & Safe Rollback)")


# ── 3. flash-schema-migration: еволюція та міграція схеми конфігурації ──────────
def fig_flash_schema_migration():
    W, H = 940, 500
    p = []

    # Схема v1.0 (24 байти)
    p.append(rect(40, 60, 245, 335, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    p.append(text(162, 85, "Схема v1 (FW v1.0.0)", size=12, bold=True, color=INK))
    p.append(fitbox(55, 105, 215, 32, "Header: Magic='CFG1', Ver=1", size=10, fill="#e9eefb", stroke=NEG))
    p.append(fitbox(55, 145, 215, 32, "wifi_ssid [32B]", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(55, 185, 215, 32, "wifi_pass [64B]", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(55, 225, 215, 32, "server_ip [4B] (IPv4 raw)", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(55, 265, 215, 32, "report_interval_s [4B]", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(55, 320, 215, 34, "CRC32 (v1 Payload)", size=10, fill="#fdfaf3", stroke="#c07a2e", bold=True))

    # Мігратор v1 -> v2
    p.append(line(285, 210, 345, 210, color=FIELD, sw=2))
    p.append('<polygon points="345,210 337,206 337,214" fill="%s"/>' % FIELD)
    p.append(text(315, 195, "v1 -> v2", size=9.5, bold=True, color=FIELD))

    # Схема v2.0 (Додано поля MQTT)
    p.append(rect(345, 60, 245, 335, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    p.append(text(467, 85, "Схема v2 (FW v1.2.0)", size=12, bold=True, color=FIELD))
    p.append(fitbox(360, 105, 215, 32, "Header: Magic='CFG1', Ver=2", size=10, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(360, 145, 215, 32, "wifi_ssid, wifi_pass (копія)", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(360, 185, 215, 32, "server_ip, report_interval", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(360, 225, 215, 32, "+ mqtt_port = 8883 (дефолт)", size=10, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(360, 265, 215, 32, "+ qos_level = 1 (дефолт)", size=10, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(360, 320, 215, 34, "CRC32 (v2 Payload)", size=10, fill="#fdfaf3", stroke="#c07a2e", bold=True))

    # Мігратор v2 -> v3
    p.append(line(590, 210, 650, 210, color=FIELD, sw=2))
    p.append('<polygon points="650,210 642,206 642,214" fill="%s"/>' % FIELD)
    p.append(text(620, 195, "v2 -> v3", size=9.5, bold=True, color=FIELD))

    # Схема v3.0 (Перехід на Hostname та TLS)
    p.append(rect(650, 60, 250, 335, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    p.append(text(775, 85, "Схема v3 (FW v2.0.0)", size=12, bold=True, color=NEG))
    p.append(fitbox(665, 105, 220, 32, "Header: Magic='CFG1', Ver=3", size=10, fill="#e9eefb", stroke=NEG, bold=True))
    p.append(fitbox(665, 145, 220, 32, "wifi_credentials (копія)", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(665, 185, 220, 32, "+ hostname [64B] (конвертовано)", size=10, fill="#e9eefb", stroke=NEG, bold=True))
    p.append(fitbox(665, 225, 220, 32, "+ tls_enabled = true (дефолт)", size=10, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(665, 265, 220, 32, "+ telemetry_profile [8B]", size=10, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(665, 320, 220, 34, "CRC32 (v3 Payload)", size=10, fill="#fdfaf3", stroke="#c07a2e", bold=True))

    # Нижній статусний блок
    p.append(fitbox(40, 410, 860, 65, "Правило безпечної міграції: Нова прошивка ніколи не виконує Factory Reset наосліп.\nВона покроково піднімає версію старої структури через ланцюжок чистих міграторів, додаючи нові поля з безпечними дефолтами\nі гарантуючи повне збереження унікальних калібрувань давачів та облікових даних зв'язку.", size=10, fill="#ffffff", stroke="#cbd5e1"))

    render(os.path.join(OUT, "flash-schema-migration.svg"), W, H, *p,
           title="Послідовна міграція схеми конфігурації у Flash: v1 -> v2 -> v3")


# ── 4. config-memory-slots: організація пам'яті Flash Ping-Pong ─────────────────
def fig_config_memory_slots():
    W, H = 940, 480
    p = []

    # Слот A (Сектор 0, Flash 4 KB)
    p.append(rect(40, 60, 420, 285, fill="#eef6ef", stroke=FIELD, sw=1.8))
    p.append(text(250, 85, "Slot A (Flash Sector 0, 4 KB) — [ACTIVE]", size=12.5, bold=True, color=FIELD))
    p.append(fitbox(60, 105, 380, 32, "Magic: 0x43464731 ('CFG1') | Version: 3", size=10, fill="#ffffff", stroke=FIELD))
    p.append(fitbox(60, 145, 380, 32, "Sequence Number: 142 (Новіший за Slot B)", size=10, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(60, 185, 380, 40, "Payload Data (Структура конфігурації):\nWi-Fi, MQTT, TLS, Calibrations, Timers (256 байтів)", size=9.5, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(60, 235, 380, 32, "CRC32 Checksum: 0xA73F9012 (Valid)", size=10, fill="#ffffff", stroke=FIELD, bold=True))
    p.append(fitbox(60, 275, 380, 46, "Стан слота: ВАЛІДНИЙ ТА АКТИВНИЙ\nЗавантажувач обирає цей слот під час старту ядра", size=9.5, fill="#ffffff", stroke=FIELD))

    # Слот B (Сектор 1, Flash 4 KB)
    p.append(rect(480, 60, 420, 285, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    p.append(text(690, 85, "Slot B (Flash Sector 1, 4 KB) — [BACKUP / STANDBY]", size=12.5, bold=True, color=MUTED))
    p.append(fitbox(500, 105, 380, 32, "Magic: 0x43464731 ('CFG1') | Version: 3", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(500, 145, 380, 32, "Sequence Number: 141 (Попередній робочий стан)", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(500, 185, 380, 40, "Payload Data (Попередня робоча конфігурація):\nWi-Fi, MQTT, TLS, Calibrations, Timers (256 байтів)", size=9.5, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(500, 235, 380, 32, "CRC32 Checksum: 0x51E2B844 (Valid)", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(500, 275, 380, 46, "Стан слота: РЕЗЕРВНИЙ (STANDBY)\nНаступний запис атомарно стирає та перезаписує цей сектор", size=9.5, fill="#ffffff", stroke=MUTED))

    # Нижній інформаційний блок процесу перезапису
    p.append(fitbox(40, 365, 860, 95, "Алгоритм атомарного оновлення (Ping-Pong Switch):\n1. Нова конфігурація записується у неактивний слот (Slot B) із номером Sequence = 142 + 1 = 143;\n2. Рахується та записується підсумкова CRC32. Доки запис не завершено, Slot A залишається повністю цілим і робочим;\n3. При знеструмленні під час запису Slot B матиме биту CRC32, і система прозоро продовжить роботу зі Slot A.", size=10, fill="#fdfaf3", stroke="#d97706"))

    render(os.path.join(OUT, "config-memory-slots.svg"), W, H, *p,
           title="Дводіапазонна організація Flash (Ping-Pong Slots) для конфігурації")


if __name__ == "__main__":
    fig_config_anatomy()
    fig_trial_run_fsm()
    fig_flash_schema_migration()
    fig_config_memory_slots()
    print("All figures generated successfully.")
