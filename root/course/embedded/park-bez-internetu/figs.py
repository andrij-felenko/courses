# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми «Парк без інтернету: технік, USB, шлюз, ретрансляція»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми: root/course/embedded/park-bez-internetu)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_offline_distribution_channels():
    """Фігура 1: Три фізичні канали поширення оновлень в ізольованому парку."""
    w, h = 900, 430
    frags = []

    frags.append(text(450, 24, "Три канали доставки оновлень в ізольованому від інтернету парку", size=16, bold=True))

    # Канал 1: Фізичний USB / Носій (Sneakernet)
    b1 = rect(25, 55, 270, 350, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    b1 += text(160, 80, "1. Фізичний носій (Sneakernet)", size=13, bold=True, color=POS)
    
    b1 += rect(45, 100, 230, 52, fill="#fdecea", stroke=POS, sw=1.2, rx=4)
    b1 += mtext(160, 120, ["USB-накопичувач / SD-карта", "Апаратний крипто-токен"], size=11, bold=True, color=POS)

    b1 += rect(45, 162, 230, 75, fill=FILL, stroke=LINE, sw=1, rx=4)
    b1 += mtext(160, 180, ["Механіка доставки:", "Технік обходить кожен пристрій,", "вставляє носій, Bootloader", "перевіряє підпис і шиє Flash"], size=10.5, color=INK)

    b1 += rect(45, 247, 230, 75, fill=FILL, stroke=LINE, sw=1, rx=4)
    b1 += mtext(160, 265, ["Зворотний канал (аудит):", "Запис підписаної квитанції", "та чорної скриньки на той", "самий носій для звіту в HQ"], size=10.5, color=INK)

    b1 += rect(45, 332, 230, 58, fill="#fdecea", stroke=POS, sw=1, rx=4)
    b1 += mtext(160, 350, ["Застосування: критичні SCADA,", "підстанції, суворий Air-Gap", "із нульовим радіовипромінюванням"], size=10, bold=True, color=POS)
    frags.append(b1)

    # Канал 2: Польовий сервісний шлюз
    b2 = rect(315, 55, 270, 350, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    b2 += text(450, 80, "2. Сервісний шлюз (Gateway)", size=13, bold=True, color=NEG)
    
    b2 += rect(335, 100, 230, 52, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4)
    b2 += mtext(450, 120, ["Планшет техніка / Оптична голівка", "BLE / Wi-Fi AP / RS-485 шина"], size=11, bold=True, color=NEG)

    b2 += rect(335, 162, 230, 75, fill=FILL, stroke=LINE, sw=1, rx=4)
    b2 += mtext(450, 180, ["Механіка доставки:", "Точкове бездротове або оптичне", "підключення до герметичного вузла,", "потоковий трансфер чанками"], size=10.5, color=INK)

    b2 += rect(335, 247, 230, 75, fill=FILL, stroke=LINE, sw=1, rx=4)
    b2 += mtext(450, 265, ["Зворотний канал (аудит):", "Вивантаження діагностичного логу", "через сесійний протокол,", "валідація життєвих показників"], size=10.5, color=INK)

    b2 += rect(335, 332, 230, 58, fill="#eaf0fd", stroke=NEG, sw=1, rx=4)
    b2 += mtext(450, 350, ["Застосування: лічильники газу/води,", "шафи автоматики, об'єкти", "без розбирання корпусу"], size=10, bold=True, color=NEG)
    frags.append(b2)

    # Канал 3: Mesh-ретрансляція (Gossip)
    b3 = rect(605, 55, 270, 350, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    b3 += text(740, 80, "3. Mesh-ретрансляція (Gossip)", size=13, bold=True, color=FIELD)
    
    b3 += rect(625, 100, 230, 52, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4)
    b3 += mtext(740, 120, ["Однорангова RF-мережа", "Sub-1GHz / Thread / BLE Mesh"], size=11, bold=True, color=FIELD)

    b3 += rect(625, 162, 230, 75, fill=FILL, stroke=LINE, sw=1, rx=4)
    b3 += mtext(740, 180, ["Механіка доставки:", "Оновлення одного вузла-насіння,", "епідемічне поширення чанків", "між сусідами за бітовими масками"], size=10.5, color=INK)

    b3 += rect(625, 247, 230, 75, fill=FILL, stroke=LINE, sw=1, rx=4)
    b3 += mtext(740, 265, ["Зворотний канал (аудит):", "Хвильове повернення квитанцій", "до шлюзу або насіннєвого вузла", "разом із вектором версій"], size=10.5, color=INK)

    b3 += rect(625, 332, 230, 58, fill="#eafaf1", stroke=FIELD, sw=1, rx=4)
    b3 += mtext(740, 350, ["Застосування: вуличне освітлення,", "сільськогосподарські датчики,", "важкодоступні сенсорні мережі"], size=10, bold=True, color=FIELD)
    frags.append(b3)

    render(os.path.join(IMG_DIR, "offline-distribution-channels.svg"), w, h, *frags)


def fig_secure_usb_update_flow():
    """Фігура 2: Поетапна перевірка та прошивка з USB-носія зі зворотним аудитом."""
    w, h = 900, 440
    frags = []

    frags.append(text(450, 24, "Конвеєр безпечного USB-оновлення: поетапна валідація та зворотний аудит", size=16, bold=True))

    # Зліва: USB носій
    frags.append(rect(25, 55, 200, 360, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(125, 80, "USB-накопичувач", size=13, bold=True, color=POS))
    
    frags.append(rect(40, 100, 170, 70, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(mtext(125, 122, ["Криптопакет .upkg", "Заголовок + Маніфест", "+ Підпис Ed25519"], size=10.5, bold=True, color=POS))

    frags.append(rect(40, 185, 170, 80, fill=FILL, stroke=LINE, sw=1, rx=4))
    frags.append(mtext(125, 208, ["Тіло прошивки", "Чанки по 4 КБ", "+ Хеш-дерево Меркла"], size=10.5, color=INK))

    frags.append(rect(40, 280, 170, 115, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    frags.append(mtext(125, 305, ["Каталог /AUDIT_LOGS/", "← Квитанція успіху", "← Зліпок стану (Dump)", "← Підпис пристрою"], size=10.5, bold=True, color=FIELD))

    # Посередині: Процес верифікації в MCU
    frags.append(rect(265, 55, 340, 360, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(435, 80, "Контролер пристрою (MCU)", size=13, bold=True, color=NEG))

    frags.append(rect(285, 100, 300, 45, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(435, 120, ["1. Перевірка Target_ID та Monotonic Counter", "(Захист від підміни заліза та Rollback-атак)"], size=10, bold=True))

    frags.append(rect(285, 155, 300, 45, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(mtext(435, 175, ["2. Валідація цифрового підпису заголовка", "(Публічний ключ випалено в eFuse / Boot ROM)"], size=10, color=NEG))

    frags.append(rect(285, 210, 300, 50, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(435, 230, ["3. Потоковий запис чанків у неактивний Slot B", "(Перевірка SHA-256 кожного чанка на льоту)"], size=10))

    frags.append(rect(285, 270, 300, 45, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(mtext(435, 290, ["4. Підсумковий SHA-256 цілого образу Slot B", "та перемикання прапорця завантажувача"], size=10, color=NEG))

    frags.append(rect(285, 325, 300, 75, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    frags.append(mtext(435, 345, ["5. Пробний старт Watchdog-контрольований:", "Підтвердження стабільності → оновлення eFuse,", "генерація криптографічної квитанції на USB"], size=9.5, bold=True, color=FIELD))

    # Справа: Flash пам'ять пристрою
    frags.append(rect(645, 55, 230, 360, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(760, 80, "Flash-пам'ять пристрою", size=13, bold=True))

    frags.append(rect(665, 100, 190, 60, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    frags.append(mtext(760, 125, ["Bootloader + eFuse", "Корінь довіри, ключі,", "лічильник версій"], size=10.5, bold=True))

    frags.append(rect(665, 175, 190, 95, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(mtext(760, 205, ["Слот A (Поточна ОС v1.2)", "Активна прошивка,", "працює під час прошивки"], size=10.5, color=NEG))

    frags.append(rect(665, 285, 190, 115, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(mtext(760, 325, ["Слот B (Нова ОС v1.3)", "Сюди стрімиться образ;", "у разі збою живлення", "Слот A лишається цілим!"], size=10, bold=True, color=POS))

    # Стрілки взаємодії
    frags.append(arrow(225, 135, 285, 135, color=POS, sw=1.5))
    frags.append(arrow(585, 235, 665, 235, color=NEG, sw=1.5))
    frags.append(arrow(285, 365, 225, 365, color=FIELD, sw=1.5))

    render(os.path.join(IMG_DIR, "secure-usb-update-flow.svg"), w, h, *frags)


def fig_field_gateway_state_machine():
    """Фігура 3: Автомат станів сервісного шлюзу та надійного потокового обміну."""
    w, h = 900, 420
    frags = []

    frags.append(text(450, 24, "Автомат станів польового сервісного шлюзу (BLE / Оптичний канал / RS-485)", size=16, bold=True))

    # Стани зліва направо
    # Стан 1: Очікування / Рукостискання
    s1 = rect(30, 70, 180, 110, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    s1 += text(120, 95, "1. DISCOVERY / AUTH", size=11.5, bold=True, color=INK)
    s1 += line(40, 105, 200, 105, color=LINE, sw=1)
    s1 += mtext(120, 125, ["Виявлення пристрою,", "Challenge-Response", "взаємна автентифікація", "та узгодження сесії"], size=9.5, color=MUTED)
    frags.append(s1)

    # Стан 2: Узгодження маніфесту
    s2 = rect(250, 70, 180, 110, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    s2 += text(340, 95, "2. MANIFEST NEGOTIATE", size=11.5, bold=True, color=NEG)
    s2 += line(260, 105, 420, 105, color=NEG, sw=1)
    s2 += mtext(340, 125, ["Передача версії, розміру,", "розміру чанка (256B..4KB),", "перевірка заряду батареї", "та готовності Flash B"], size=9.5, color=MUTED)
    frags.append(s2)

    # Стан 3: Віконний трансфер чанків
    s3 = rect(470, 70, 180, 110, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    s3 += text(560, 95, "3. CHUNK STREAMING", size=11.5, bold=True, color=POS)
    s3 += line(480, 105, 640, 105, color=POS, sw=1)
    s3 += mtext(560, 125, ["Потокове надсилання", "ковзним вікном (Window),", "CRC32 на кожен чанк,", "довідправка втрачених"], size=9.5, color=MUTED)
    frags.append(s3)

    # Стан 4: Верифікація та коміт
    s4 = rect(690, 70, 180, 110, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    s4 += text(780, 95, "4. VERIFY & COMMIT", size=11.5, bold=True, color=FIELD)
    s4 += line(700, 105, 860, 105, color=FIELD, sw=1)
    s4 += mtext(780, 125, ["Повна SHA-256 звірка,", "підпис образу Ed25519,", "активація прапорця пробного", "старту в NVS"], size=9.5, color=MUTED)
    frags.append(s4)

    # Стрілки прямі
    frags.append(arrow(210, 125, 250, 125, color=LINE, sw=1.5))
    frags.append(arrow(430, 125, 470, 125, color=NEG, sw=1.5))
    frags.append(arrow(650, 125, 690, 125, color=POS, sw=1.5))

    # Нижній ряд: Стан 5 (Пробний запуск і зворотний звіт) та Обробка помилок
    s5 = rect(470, 240, 400, 150, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=8)
    s5 += text(670, 268, "5. POST-BOOT VALIDATION & AUDIT EXTRACTION", size=12, bold=True, color=FIELD)
    s5 += line(485, 280, 855, 280, color=FIELD, sw=1)
    s5 += mtext(670, 305, ["• Перезавантаження MCU у нову версію під наглядом апаратного Watchdog", "• Самотестування периферії: датчики, живлення, криптомодуль", "• Успіх: фіксація слота як основного, скидання таймера відкату", "• Генерація підписаної квитанції та передача діагностики на шлюз техніка"], size=10, color=INK)
    frags.append(s5)

    # Обробка обриву та збою
    sfail = rect(30, 240, 380, 150, fill="#fdecea", stroke=POS, sw=1.5, rx=8)
    sfail += text(220, 268, "ОБРОБКА ОБРИВУ ЗВ'ЯЗКУ ТА ВІДКАТУ", size=12, bold=True, color=POS)
    sfail += line(45, 280, 395, 280, color=POS, sw=1)
    sfail += mtext(220, 305, ["• Обрив шлюзу під час передачі: контролер зберігає бітову маску,", "  при повторному підключенні докачуються лише відсутні чанки (Resumable)", "• Збій після прошивки: Watchdog не отримує підтвердження і через 30 с", "  Bootloader автоматично повертає завантаження зі слота A"], size=10, color=INK)
    frags.append(sfail)

    # Стрілки переходу до фіналу та відкату
    frags.append(arrow(780, 180, 780, 240, color=FIELD, sw=1.5))
    frags.append(arrow(560, 180, 380, 240, color=POS, sw=1.5))

    render(os.path.join(IMG_DIR, "field-gateway-state-machine.svg"), w, h, *frags)


def fig_mesh_gossip_chunking():
    """Фігура 4: Епідемічне поширення чанків у бездротовій Mesh-мережі з бітовими масками."""
    w, h = 900, 430
    frags = []

    frags.append(text(450, 24, "Механіка Gossip-протоколу: бітові маски, антиентропія та дерево Меркла", size=16, bold=True))

    # Лівий блок: Структура утилізації прошивки
    frags.append(rect(25, 55, 260, 350, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(155, 80, "Розбиття прошивки на чанки", size=12.5, bold=True))

    frags.append(rect(45, 100, 220, 50, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    frags.append(mtext(155, 120, ["Образ прошивки v2.0 (256 КБ)", "1024 чанки по 256 байтів"], size=10, bold=True, color=NEG))

    frags.append(rect(45, 160, 220, 110, fill=FILL, stroke=LINE, sw=1, rx=4))
    frags.append(mtext(155, 180, ["Бітова маска володіння:", "uint8_t bitmask[128];", "1 біт = 1 наявний чанк", "", "Приклад: [1 1 1 0 1 0 0 1 ...]", "Вузол миттєво знає, чого бракує"], size=10, color=INK))

    frags.append(rect(45, 280, 220, 110, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(mtext(155, 300, ["Дерево хешів Меркла:", "Корінь підписано Ed25519;", "кожен чанк містить хеш-доказ.", "Отруєний чанк відкидається", "негайно, без чекання всього файлу!"], size=9.5, bold=True, color=POS))

    # Центральний і правий блок: Вузли Mesh мережі
    frags.append(rect(310, 55, 565, 350, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(592, 80, "Епідемічне поширення (Anti-Entropy Exchange) між вузлами", size=13, bold=True, color=FIELD))

    # Вузол-Насіння (Seed Node)
    n0 = rect(330, 110, 160, 110, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6)
    n0 += text(410, 132, "Вузол 0 (Seed / Шлюз)", size=11, bold=True, color=FIELD)
    n0 += line(340, 142, 480, 142, color=FIELD, sw=1)
    n0 += mtext(410, 162, ["Отримав від техніка", "Маска: 100% (11111111)", "Статус: ГОТОВИЙ"], size=9.5, color=INK)
    frags.append(n0)

    # Вузол 1 (Hop 1)
    n1 = rect(540, 110, 150, 110, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6)
    n1 += text(615, 132, "Вузол 1 (Hop 1)", size=11, bold=True, color=NEG)
    n1 += line(550, 142, 680, 142, color=NEG, sw=1)
    n1 += mtext(615, 162, ["Завантажує від Вузла 0", "Маска: 65% (11110011)", "Запитує чанки #4, #5"], size=9.5, color=INK)
    frags.append(n1)

    # Вузол 2 (Hop 2)
    n2 = rect(720, 260, 140, 110, fill="#fdecea", stroke=POS, sw=1.5, rx=6)
    n2 += text(790, 282, "Вузол 3 (Hop 3)", size=11, bold=True, color=POS)
    n2 += line(730, 292, 850, 292, color=POS, sw=1)
    n2 += mtext(790, 312, ["Спить 95% часу", "Маска: 10% (10000000)", "Синхронізація у вікні"], size=9.5, color=INK)
    frags.append(n2)

    # Вузол 3 (Hop 2)
    n3 = rect(540, 260, 150, 110, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6)
    n3 += text(615, 282, "Вузол 2 (Hop 2)", size=11, bold=True, color=INK)
    n3 += line(550, 292, 680, 292, color=LINE, sw=1)
    n3 += mtext(615, 312, ["Завантажує від Вузла 1", "Маска: 30% (11000000)", "Ділиться чанком #1 з #3"], size=9.5, color=INK)
    frags.append(n3)

    # Стрілки Gossip обміну
    frags.append(arrow(490, 155, 540, 155, color=FIELD, sw=1.5))
    frags.append(arrow(615, 220, 615, 260, color=NEG, sw=1.5))
    frags.append(arrow(690, 315, 720, 315, color=LINE, sw=1.5))

    # Нижній інформаційний блок про Trickle Timer
    frags.append(rect(330, 260, 180, 110, fill="#fdfefe", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(420, 285, ["Алгоритм Trickle (RFC 6206):", "При консенсусі таймер", "експоненційно росте (тиша),", "новий чанк скидає таймер", "до мінімуму (швидкий сплеск)"], size=9, color=MUTED))

    render(os.path.join(IMG_DIR, "mesh-gossip-chunking.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_offline_distribution_channels()
    fig_secure_usb_update_flow()
    fig_field_gateway_state_machine()
    fig_mesh_gossip_chunking()
    print("Усі 4 фігури успішно згенеровано у %s" % IMG_DIR)
