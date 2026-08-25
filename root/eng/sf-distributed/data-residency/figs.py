# -*- coding: utf-8 -*-
"""Фігури теми «Резидентність даних, GDPR та географічне шардування». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Палітра кольорів
C_BLUE_BG    = "#eaf2fd"
C_BLUE_BRD   = "#2457d6"
C_GREEN_BG   = "#e8f8f0"
C_GREEN_BRD  = "#27ae60"
C_AMBER_BG   = "#fef9e7"
C_AMBER_BRD  = "#d35400"
C_PURPLE_BG  = "#f3e8fd"
C_PURPLE_BRD = "#8e44ad"
C_GRAY_BG    = "#f4f6f8"
C_GRAY_BRD   = "#6b7280"
C_RED_BG     = "#fdecea"
C_RED_BRD    = "#c0392b"


# ── 1. geo-sharding-topology: Архітектура географічного шардування та суверенних юрисдикцій ──
def fig_geo_sharding_topology():
    W, H = 1000, 540
    f = []

    # Верхній рівень: Клієнти та Глобальний маршрутизатор
    f.append(rect(40, 45, 920, 65, fill=C_GRAY_BG, stroke=C_GRAY_BRD, sw=1.5, rx=8))
    f.append(text(500, 70, "Глобальний рівень маршрутизації (GeoDNS + Anycast L4 / L7 Global API Gateway)", size=14, bold=True, color=INK))
    f.append(text(500, 92, "Визначення регіону користувача за JWT / Session Claim або IP GeoIP -> скеровування запиту у відповідний юрисдикційний шлюз", size=11, color=MUTED))

    # Три суверенні зони (колонки)
    # Зона 1: ЄС (GDPR)
    f.append(rect(40, 140, 290, 360, fill="#f8fafc", stroke=C_BLUE_BRD, sw=2, rx=8))
    f.append(rect(40, 140, 290, 36, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.5, rx=8))
    f.append(text(185, 163, "Юрисдикція ЄС (GDPR / BDSG)", size=13, bold=True, color=C_BLUE_BRD))

    f.append(rect(55, 190, 260, 80, fill="#ffffff", stroke=C_BLUE_BRD, sw=1.2, rx=6))
    f.append(text(185, 212, "Шард P_EU (eu-central-1)", size=12, bold=True, color=INK))
    f.append(text(185, 232, "Ключ: (country='DE', tenant_id)", size=11, color=MUTED))
    f.append(text(185, 252, "Дані PII та фінанси резидентів ЄС", size=11, color=C_BLUE_BRD))

    f.append(rect(55, 285, 260, 95, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.2, rx=6))
    f.append(text(185, 307, "Консенсусна група Raft (EU)", size=12, bold=True, color=INK))
    f.append(text(185, 327, "Вузол 1 (Лідер) - Франкфурт", size=10, color=INK))
    f.append(text(185, 345, "Вузол 2 (Фоловер) - Париж", size=10, color=INK))
    f.append(text(185, 363, "Вузол 3 (Фоловер) - Дублін", size=10, color=INK))

    f.append(rect(55, 395, 260, 85, fill="#ffffff", stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(185, 417, "Локальний KMS / HSM (FIPS 140-2)", size=11, bold=True, color=INK))
    f.append(text(185, 437, "Ключі шифрування не залишають ЄС", size=10, color=MUTED))
    f.append(text(185, 457, "Захист від дії US CLOUD Act", size=10, color=C_GREEN_BRD))

    # Зона 2: США (CCPA / HIPAA)
    f.append(rect(355, 140, 290, 360, fill="#f8fafc", stroke=C_GREEN_BRD, sw=2, rx=8))
    f.append(rect(355, 140, 290, 36, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=8))
    f.append(text(500, 163, "Юрисдикція США (CCPA / HIPAA)", size=13, bold=True, color=C_GREEN_BRD))

    f.append(rect(370, 190, 260, 80, fill="#ffffff", stroke=C_GREEN_BRD, sw=1.2, rx=6))
    f.append(text(500, 212, "Шард P_US (us-east-1)", size=12, bold=True, color=INK))
    f.append(text(500, 232, "Ключ: (country='US', tenant_id)", size=11, color=MUTED))
    f.append(text(500, 252, "Дані резидентів Північної Америки", size=11, color=C_GREEN_BRD))

    f.append(rect(370, 285, 260, 95, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.2, rx=6))
    f.append(text(500, 307, "Консенсусна група Raft (US)", size=12, bold=True, color=INK))
    f.append(text(500, 327, "Вузол 1 (Лідер) - Вірджинія", size=10, color=INK))
    f.append(text(500, 345, "Вузол 2 (Фоловер) - Огайо", size=10, color=INK))
    f.append(text(500, 363, "Вузол 3 (Фоловер) - Орегон", size=10, color=INK))

    f.append(rect(370, 395, 260, 85, fill="#ffffff", stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(500, 417, "Локальний KMS (US Region)", size=11, bold=True, color=INK))
    f.append(text(500, 437, "Керування доступом за IAM ролями", size=10, color=MUTED))
    f.append(text(500, 457, "Сумісність із SOC2 / HIPAA", size=10, color=MUTED))

    # Зона 3: Азійсько-Тихоокеанський регіон
    f.append(rect(670, 140, 290, 360, fill="#f8fafc", stroke=C_AMBER_BRD, sw=2, rx=8))
    f.append(rect(670, 140, 290, 36, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=1.5, rx=8))
    f.append(text(815, 163, "Юрисдикція APAC (Сінгапур / Токіо)", size=13, bold=True, color=C_AMBER_BRD))

    f.append(rect(685, 190, 260, 80, fill="#ffffff", stroke=C_AMBER_BRD, sw=1.2, rx=6))
    f.append(text(815, 212, "Шард P_APAC (ap-southeast-1)", size=12, bold=True, color=INK))
    f.append(text(815, 232, "Ключ: (country='SG', tenant_id)", size=11, color=MUTED))
    f.append(text(815, 252, "Дані резидентів APAC регіону", size=11, color=C_AMBER_BRD))

    f.append(rect(685, 285, 260, 95, fill=C_AMBER_BG, stroke=C_AMBER_BRD, sw=1.2, rx=6))
    f.append(text(815, 307, "Консенсусна група Raft (APAC)", size=12, bold=True, color=INK))
    f.append(text(815, 327, "Вузол 1 (Лідер) - Сінгапур", size=10, color=INK))
    f.append(text(815, 345, "Вузол 2 (Фоловер) - Токіо", size=10, color=INK))
    f.append(text(815, 363, "Вузол 3 (Фоловер) - Сідней", size=10, color=INK))

    f.append(rect(685, 395, 260, 85, fill="#ffffff", stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(815, 417, "Локальний KMS (APAC)", size=11, bold=True, color=INK))
    f.append(text(815, 437, "Сумісність із PDPA / APPI", size=10, color=MUTED))
    f.append(text(815, 457, "Ізоляція ключів у регіоні", size=10, color=MUTED))

    # Маршрутизуючі стрілки зверху вниз
    f.append(arrow(185, 110, 185, 138, color=C_BLUE_BRD, sw=2))
    f.append(arrow(500, 110, 500, 138, color=C_GREEN_BRD, sw=2))
    f.append(arrow(815, 110, 815, 138, color=C_AMBER_BRD, sw=2))

    render(out("geo-sharding-topology.svg"), W, H, *f, title="Архітектура географічного шардування та ізоляції кворумів")


# ── 2. tokenization-enclave-pattern: Анклав токенізації та псевдонімізації ──
def fig_tokenization_enclave_pattern():
    W, H = 980, 480
    f = []

    # Лівий блок: Суверенний анклав ЄС
    f.append(rect(30, 45, 430, 400, fill="#f8fafc", stroke=C_BLUE_BRD, sw=2, rx=8))
    f.append(rect(30, 45, 430, 36, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.5, rx=8))
    f.append(text(245, 68, "Суверенний анклав даних ЄС (GDPR Safe Zone)", size=13, bold=True, color=C_BLUE_BRD))

    f.append(rect(45, 95, 400, 75, fill="#ffffff", stroke=C_BLUE_BRD, sw=1.2, rx=6))
    f.append(text(245, 118, "Вхідний шлюз API ЄС (TLS Termination)", size=12, bold=True, color=INK))
    f.append(text(245, 138, "Отримання сирого PII: {name: 'Hans', iban: 'DE89...', email: '...'} ", size=10, color=MUTED))
    f.append(text(245, 155, "Пакет обробляється виключно в оперативній пам'яті вузла у Франкфурті", size=10, color=C_BLUE_BRD))

    f.append(rect(45, 185, 400, 130, fill=C_BLUE_BG, stroke=C_BLUE_BRD, sw=1.2, rx=6))
    f.append(text(245, 208, "Сховище токенів (Token Vault) & Локальний HSM", size=12, bold=True, color=INK))
    f.append(text(245, 230, "1. Збереження сирого PII у локальну зашифровану БД ЄС", size=10, color=INK))
    f.append(text(245, 250, "2. Генерація криптографічного токена UUIDv4: tok_9f8a41c2", size=10, color=C_PURPLE_BRD))
    f.append(text(245, 270, "3. Збереження відображення: tok_9f8a41c2 <-> Hans / IBAN", size=10, color=INK))
    f.append(text(245, 290, "4. Захист ключа шифрування у європейському HSM", size=10, color=C_GREEN_BRD))

    f.append(rect(45, 330, 400, 95, fill="#ffffff", stroke=C_GREEN_BRD, sw=1.2, rx=6))
    f.append(text(245, 353, "Формування знеособленого пейлоаду", size=12, bold=True, color=INK))
    f.append(text(245, 375, "Трансформація: PII вилучено, підставлено токен tok_9f8a41c2", size=10, color=MUTED))
    f.append(text(245, 395, "Пейлоад готовий до законної транскордонної передачі", size=10, color=C_GREEN_BRD))

    # Стрілка транскордонного експорту
    f.append(arrow(465, 377, 515, 377, color=C_PURPLE_BRD, sw=2.5))
    f.append(text(490, 360, "Експорт", size=11, bold=True, color=C_PURPLE_BRD))
    f.append(text(490, 400, "(Без PII)", size=10, color=MUTED))

    # Правий блок: Глобальна аналітика та центральна система (США / Глобальна хмара)
    f.append(rect(520, 45, 430, 400, fill="#f8fafc", stroke=C_PURPLE_BRD, sw=2, rx=8))
    f.append(rect(520, 45, 430, 36, fill=C_PURPLE_BG, stroke=C_PURPLE_BRD, sw=1.5, rx=8))
    f.append(text(735, 68, "Центральна аналітика / ML-контур (Global / US Cloud)", size=13, bold=True, color=C_PURPLE_BRD))

    f.append(rect(535, 95, 400, 100, fill="#ffffff", stroke=C_PURPLE_BRD, sw=1.2, rx=6))
    f.append(text(735, 118, "Знеособлена подія (Pseudonymized Event)", size=12, bold=True, color=INK))
    f.append(text(735, 140, "{ user_token: 'tok_9f8a41c2', amount: 149.99, currency: 'EUR',", size=10, color=MUTED))
    f.append(text(735, 158, "  category: 'electronics', timestamp: 1740000000 }", size=10, color=MUTED))
    f.append(text(735, 178, "Жодних персональних даних: ім'я, адреса та IBAN відсутні", size=10, color=C_GREEN_BRD))

    f.append(rect(535, 210, 400, 105, fill=C_PURPLE_BG, stroke=C_PURPLE_BRD, sw=1.2, rx=6))
    f.append(text(735, 233, "Аналітичний Data Lakehouse / DWH (ClickHouse/Snowflake)", size=12, bold=True, color=INK))
    f.append(text(735, 255, "Побудова глобальних звітів, когортного аналізу та фрод-моделей", size=10, color=INK))
    f.append(text(735, 275, "Повна відповідність GDPR: відсутність транскордонного витоку PII", size=10, color=C_GREEN_BRD))
    f.append(text(735, 295, "Звітність не підпадає під штрафи ст. 83(5) GDPR", size=10, color=MUTED))

    f.append(rect(535, 330, 400, 95, fill="#ffffff", stroke=C_GRAY_BRD, sw=1, rx=6))
    f.append(text(735, 353, "Зворотна де-токенізація (Лише за санкціонованим запитом)", size=11, bold=True, color=INK))
    f.append(text(735, 375, "Виклик захищеного шлюзу ЄС через mTLS з аудитом доступу", size=10, color=MUTED))
    f.append(text(735, 395, "Доступ дозволено лише локальному оператору підтримки в ЄС", size=10, color=C_BLUE_BRD))

    render(out("tokenization-enclave-pattern.svg"), W, H, *f, title="Архітектурний патерн токенізації та захищеного регіонального анклаву")


# ── 3. cross-border-query-federation: Федеративні запити та Push-down агрегація ──
def fig_cross_border_query_federation():
    W, H = 980, 500
    f = []

    # Верхня частина: Наївний підхід (Порушення та повільність)
    f.append(rect(30, 45, 920, 195, fill=C_RED_BG, stroke=C_RED_BRD, sw=1.5, rx=8))
    f.append(text(490, 68, "НАЇВНИЙ ПІДХІД: Транскордонний запит рядків (Порушення GDPR + Латентність)", size=13, bold=True, color=C_RED_BRD))

    f.append(rect(50, 85, 260, 65, fill="#ffffff", stroke=C_RED_BRD, sw=1, rx=6))
    f.append(text(180, 107, "Центральний клієнт (США)", size=12, bold=True, color=INK))
    f.append(text(180, 127, "SELECT * FROM users WHERE active=1", size=10, color=MUTED))

    f.append(rect(670, 85, 260, 65, fill="#ffffff", stroke=C_RED_BRD, sw=1, rx=6))
    f.append(text(800, 107, "Шард банку ЄС (Франкфурт)", size=12, bold=True, color=INK))
    f.append(text(800, 127, "500 000 сирих рядків із PII", size=10, color=C_RED_BRD))

    f.append(arrow(315, 110, 665, 110, color=C_RED_BRD, sw=2))
    f.append(text(490, 100, "1. Запит через океан (120 мс)", size=11, color=INK))

    f.append(arrow(665, 130, 315, 130, color=C_RED_BRD, sw=2))
    f.append(text(490, 150, "2. Передача 500 000 незашифрованих записів PII у США (НЕЗАКОННО)", size=11, bold=True, color=C_RED_BRD))

    f.append(rect(50, 160, 880, 65, fill="#ffffff", stroke=C_RED_BRD, sw=1, rx=6))
    f.append(text(490, 182, "Наслідки: Пряме порушення Розділу V GDPR (Штраф до 20 млн євро або 4% річного обороту),", size=11, bold=True, color=C_RED_BRD))
    f.append(text(490, 204, "перевантаження WAN-каналів, латентність запиту понад 15-30 секунд.", size=11, color=INK))

    # Нижня частина: Федеративна Push-Down агрегація (Законно та швидко)
    f.append(rect(30, 255, 920, 220, fill=C_GREEN_BG, stroke=C_GREEN_BRD, sw=1.5, rx=8))
    f.append(text(490, 278, "ПРАВИЛЬНИЙ ПІДХІД: Федеративна Push-Down агрегація та диференційна приватність", size=13, bold=True, color=C_GREEN_BRD))

    f.append(rect(50, 295, 250, 75, fill="#ffffff", stroke=C_GREEN_BRD, sw=1.2, rx=6))
    f.append(text(175, 318, "Глобальний координатор", size=12, bold=True, color=INK))
    f.append(text(175, 338, "SELECT tier, COUNT(*), SUM(rev)", size=10, color=MUTED))
    f.append(text(175, 355, "Розсилка агрегаційного запиту", size=10, color=C_GREEN_BRD))

    f.append(rect(370, 295, 260, 75, fill="#ffffff", stroke=C_BLUE_BRD, sw=1.2, rx=6))
    f.append(text(500, 318, "Локальний двигун Шарда ЄС", size=12, bold=True, color=INK))
    f.append(text(500, 338, "1. Локальний Map: COUNT(*), SUM()", size=10, color=INK))
    f.append(text(500, 355, "2. Фільтр k-анонімності (k >= 5)", size=10, color=C_BLUE_BRD))

    f.append(rect(690, 295, 240, 75, fill="#ffffff", stroke=C_AMBER_BRD, sw=1.2, rx=6))
    f.append(text(810, 318, "Локальний двигун Шарда США", size=12, bold=True, color=INK))
    f.append(text(810, 338, "1. Локальний Map: COUNT(*), SUM()", size=10, color=INK))
    f.append(text(810, 355, "2. Фільтр k-анонімності (k >= 5)", size=10, color=C_AMBER_BRD))

    f.append(arrow(305, 325, 365, 325, color=LINE, sw=1.5))
    f.append(arrow(305, 350, 685, 350, color=LINE, sw=1.5))

    f.append(rect(50, 385, 880, 75, fill="#ffffff", stroke=C_GREEN_BRD, sw=1, rx=6))
    f.append(text(490, 408, "Фінальний Reduce на координаторі: Злиття числових агрегатів без жодного байта PII.", size=11, bold=True, color=INK))
    f.append(text(490, 428, "Переваги: 100% відповідність GDPR Art. 44-49, мінімальний трафік (кілька кілобайтів замість гігабайтів),", size=10, color=C_GREEN_BRD))
    f.append(text(490, 446, "час відповіді запиту p99 < 300 мс замість десятків секунд.", size=10, color=MUTED))

    render(out("cross-border-query-federation.svg"), W, H, *f, title="Федеративне виконання запитів та захист від транскордонного витоку даних")


if __name__ == '__main__':
    fig_geo_sharding_topology()
    fig_tokenization_enclave_pattern()
    fig_cross_border_query_federation()
    print("Всі фігури успішно згенеровано у ./img/")
