# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми «Де в пристрої лежить ключ»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_flash_vulnerabilities():
    """Фігура 1: Чому відкритий Flash вразливий до викрадення секретів."""
    w, h = 860, 420
    frags = []

    frags.append(text(430, 24, "Поверхня атак на відкритий Flash і незахищену пам'ять", size=16, bold=True))

    # Лівий блок: Зовнішній Flash (SPI/QSPI)
    b1 = rect(30, 50, 240, 340, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    b1 += text(150, 75, "Зовнішній Flash (SPI / QSPI)", size=13, bold=True, color=POS)
    b1 += rect(50, 95, 200, 50, fill="#fdecea", stroke=POS, sw=1.2, rx=4)
    b1 += mtext(150, 116, ["SOIC-8 / WSON-8", "Кліпса або перехоплювач"], size=11, bold=True, color=POS)
    
    b1 += rect(50, 160, 200, 65, fill=FILL, stroke=LINE, sw=1, rx=4)
    b1 += mtext(150, 180, ["Пасивне прослуховування", "Логічний аналізатор читає", "ключ під час завантаження"], size=11, color=INK)

    b1 += rect(50, 240, 200, 65, fill=FILL, stroke=LINE, sw=1, rx=4)
    b1 += mtext(150, 260, ["Прямий дамп пам'яті", "Зчитування програматором", "CH341A або flashrom"], size=11, color=INK)

    b1 += rect(50, 320, 200, 55, fill="#fdecea", stroke=POS, sw=1, rx=4)
    b1 += mtext(150, 342, ["Висновок: відкриті доріжки", "не захищають секрети"], size=11, bold=True, color=POS)
    frags.append(b1)

    # Центральний блок: Внутрішній Flash MCU
    b2 = rect(310, 50, 240, 340, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    b2 += text(430, 75, "Внутрішній Flash MCU", size=13, bold=True, color=NEG)
    b2 += rect(330, 95, 200, 50, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4)
    b2 += mtext(430, 116, ["SWD / JTAG порти", "Налагоджувальний інтерфейс"], size=11, bold=True, color=NEG)

    b2 += rect(330, 160, 200, 65, fill=FILL, stroke=LINE, sw=1, rx=4)
    b2 += mtext(430, 180, ["Обхід Readout Protection", "Зняття захисту (RDP1)", "через команди стирання"], size=11, color=INK)

    b2 += rect(330, 240, 200, 65, fill=FILL, stroke=LINE, sw=1, rx=4)
    b2 += mtext(430, 260, ["Ін'єкція збоїв (Glitching)", "Voltage / Clock імпульс", "скидає перевірку бітів"], size=11, color=INK)

    b2 += rect(330, 320, 200, 55, fill="#eaf0fd", stroke=NEG, sw=1, rx=4)
    b2 += mtext(430, 342, ["Висновок: програмні біти", "вразливі до збоїв живлення"], size=11, bold=True, color=NEG)
    frags.append(b2)

    # Правий блок: Оперативна пам'ять (RAM)
    b3 = rect(590, 50, 240, 340, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8)
    b3 += text(710, 75, "Оперативна пам'ять (RAM)", size=13, bold=True, color=INK)
    b3 += rect(610, 95, 200, 50, fill=FILL, stroke=LINE, sw=1.2, rx=4)
    b3 += mtext(710, 116, ["Розгортання ключа в RAM", "Для програмної криптографії"], size=11, bold=True, color=INK)

    b3 += rect(610, 160, 200, 65, fill=FILL, stroke=LINE, sw=1, rx=4)
    b3 += mtext(710, 180, ["Атака холодного старту", "Охолодження чипа азотом", "і залишкові заряди SRAM"], size=11, color=INK)

    b3 += rect(610, 240, 200, 65, fill=FILL, stroke=LINE, sw=1, rx=4)
    b3 += mtext(710, 260, ["Дампи після помилок", "Витік ключа через стек", "або залишок у буфері heap"], size=11, color=INK)

    b3 += rect(610, 320, 200, 55, fill="#fdecea", stroke=POS, sw=1, rx=4)
    b3 += mtext(710, 342, ["Висновок: ключ у RAM", "легко виявити в дампах"], size=11, bold=True, color=POS)
    frags.append(b3)

    render(os.path.join(IMG_DIR, "flash-vulnerabilities.svg"), w, h, *frags)


def fig_efuse_silicon_isolation():
    """Фігура 2: eFuse — апаратне випалювання та ізоляція шини від CPU."""
    w, h = 860, 400
    frags = []

    frags.append(text(430, 24, "Апаратна eFuse-пам'ять: ізоляція ключа від системної шини CPU", size=16, bold=True))

    # Ліва частина: Фізика перемички
    frags.append(rect(30, 50, 260, 330, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(160, 75, "Фізика eFuse / Anti-Fuse", size=13, bold=True))

    frags.append(rect(50, 95, 220, 65, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(160, 118, ["Стан 0: Ціла перемичка", "Низький опір (R ≈ 50 Ом)", "Струм вільно тече"], size=11))

    frags.append(rect(50, 175, 220, 70, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(mtext(160, 198, ["Імпульс випалювання", "Високий струм / VDDQ 2.5V", "Електроміграція розриває міст"], size=11, bold=True, color=POS))

    frags.append(rect(50, 260, 220, 65, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    frags.append(mtext(160, 283, ["Стан 1: Розірваний міст", "Високий опір (R > 100 кОм)", "Незворотний стан у кремнії"], size=11, color=NEG))

    frags.append(text(160, 355, "Зміна стану одноразова й вічна", size=11, italic=True, color=MUTED))

    # Права частина: Схема ізоляції шин
    frags.append(rect(320, 50, 510, 330, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(575, 75, "Схема апаратного доступу та апаратних заборон", size=13, bold=True))

    # Масив eFuse блоків
    frags.append(rect(350, 110, 140, 160, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    frags.append(mtext(420, 135, ["Масив eFuse", "Блок 0: MAC / Конфіг", "Блок 1: Ключ Flash", "Блок 2: Ключ SecureBoot", "Блок 3: Ключ HMAC"], size=11, bold=True))

    # Криптографічний акселератор
    frags.append(rect(660, 100, 150, 80, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    frags.append(mtext(735, 135, ["Апаратний AES /", "Flash Decryption", "Акселератор"], size=12, bold=True, color=FIELD))

    # Процесорне ядро (CPU)
    frags.append(rect(660, 230, 150, 80, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(mtext(735, 265, ["Процесор (CPU)", "Системна шина", "AHB / AXI"], size=12, bold=True, color=POS))

    # Лінія від eFuse до Crypto: пряма шина
    frags.append(arrow(490, 140, 660, 140, color=FIELD, sw=2.5))
    frags.append(rect(505, 115, 140, 24, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
    frags.append(text(575, 132, "Ключ напряму в залізо", size=10, bold=True, color=FIELD))

    # Лінія від eFuse до CPU: апаратне блокування
    frags.append(line(490, 240, 560, 240, color=POS, sw=1.8, dash="4,4"))
    frags.append(rect(560, 225, 30, 30, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(575, 245, "✕", size=18, bold=True, color=POS))
    frags.append(arrow(590, 240, 660, 240, color=POS, sw=1.8))

    frags.append(rect(510, 275, 130, 35, fill="#ffffff", stroke=POS, sw=1, rx=3))
    frags.append(mtext(575, 290, ["Read Disable біт", "CPU читає лише 0x00"], size=10, color=POS))

    frags.append(text(575, 355, "Ключ працює в шифраторі, але процесор не може його зчитати", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "efuse-silicon-isolation.svg"), w, h, *frags)


def fig_secure_element_architecture():
    """Фігура 3: Архітектура Secure Element (Zero-Leakage крипточип)."""
    w, h = 860, 420
    frags = []

    frags.append(text(430, 24, "Архітектура Secure Element: апаратна ізоляція та захист кристала", size=16, bold=True))

    # Великий блок чіпа
    frags.append(rect(30, 50, 800, 350, fill="#fdfefe", stroke=LINE, sw=2, rx=10))
    frags.append(text(430, 75, "Захищений кристал Secure Element (наприклад, ATECC608 / NXP SE050)", size=14, bold=True))

    # Активний захисний екран (Active Shield Mesh) - контур
    frags.append(rect(45, 90, 770, 295, fill="#fafbfc", stroke=POS, sw=1.5, rx=8))
    frags.append(text(430, 110, "Активна сітка металізації (Active Shield): розрив або замикання спричиняє миттєве самознищення", size=11, bold=True, color=POS))

    # Ліва колонка: Інтерфейс і керування
    frags.append(rect(65, 130, 210, 235, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(170, 155, "Шинний інтерфейс", size=12, bold=True))

    frags.append(rect(80, 175, 180, 50, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(170, 197, ["I2C / SPI контролер", "Wake-up детектор", "Перевірка CRC16"], size=10))

    frags.append(rect(80, 240, 180, 50, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(170, 262, ["Командний процесор", "Перевірка прав доступу", "Контролер слотів"], size=10))

    frags.append(rect(80, 305, 180, 45, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(mtext(170, 325, ["Детектори збоїв:", "Напруга, світло, такти"], size=10, bold=True, color=POS))

    # Центральна колонка: Криптографічні ядра та генератор ентропії
    frags.append(rect(300, 130, 250, 235, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(425, 155, "Апаратні криптоакселератори", size=12, bold=True, color=FIELD))

    frags.append(rect(315, 175, 220, 50, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(425, 197, ["ECDSA / Ed25519 ядро", "Асиметричний підпис і ECDH"], size=11, bold=True, color=FIELD))

    frags.append(rect(315, 235, 220, 45, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(425, 257, ["SHA-256 / AES-128 ядро", "Симетрична автентифікація"], size=10))

    frags.append(rect(315, 290, 220, 60, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(425, 310, ["Апаратний TRNG +", "Маскування струму від DPA", "(генератор шуму живлення)"], size=10, bold=True, color=FIELD))

    # Права колонка: Захищене сховище ключів (EEPROM/Flash)
    frags.append(rect(575, 130, 220, 235, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(685, 155, "Захищений масив EEPROM", size=12, bold=True, color=NEG))

    frags.append(rect(590, 175, 190, 40, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(mtext(685, 195, ["Слот 0: Приватний ключ ECC", "Locked / Не читається"], size=10, bold=True, color=NEG))

    frags.append(rect(590, 225, 190, 40, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(mtext(685, 245, ["Слот 1..7: Симетричні ключі", "AES / HMAC секрети"], size=10))

    frags.append(rect(590, 275, 190, 40, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(mtext(685, 295, ["Слот 8..15: Сертифікати", "Публічні ключі, дані"], size=10))

    frags.append(rect(590, 325, 190, 30, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    frags.append(text(685, 345, "Шифрування шин пам'яті", size=10, italic=True))

    # Внутрішні стрілки взаємодії
    frags.append(arrow(275, 200, 315, 200, color=LINE, sw=1.5))
    frags.append(arrow(575, 200, 535, 200, color=NEG, sw=2))

    render(os.path.join(IMG_DIR, "secure-element-architecture.svg"), w, h, *frags)


def fig_puf_entropy_reconstruction():
    """Фігура 4: Фізично неклоновані функції (PUF) та Fuzzy Extractor."""
    w, h = 860, 420
    frags = []

    frags.append(text(430, 24, "Фізично неклоновані функції (PUF): генерація ключа без зберігання", size=16, bold=True))

    # Верхній блок: Фізика дефектів кремнію (SRAM клітинка)
    frags.append(rect(30, 50, 800, 120, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(430, 72, "Фізичне джерело: унікальні нанодефекти виготовлення кремнієвої пластини", size=13, bold=True))

    frags.append(rect(50, 90, 220, 65, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(160, 112, ["Комірка SRAM #0", "Транзистор A сильніший", "Старт стабільно в '0'"], size=10))

    frags.append(rect(320, 90, 220, 65, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(430, 112, ["Комірка SRAM #1", "Транзистор B сильніший", "Старт стабільно в '1'"], size=10))

    frags.append(rect(590, 90, 220, 65, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(mtext(700, 112, ["Комірка SRAM #N (шумна)", "Температурний дрейф", "Старт у '0' або '1' (~1-3%)"], size=10, color=POS))

    # Нижня частина: Дві фази Fuzzy Extractor
    # Ліва колонка: Фаза реєстрації (Enrollment) на заводі
    frags.append(rect(30, 190, 385, 210, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(222, 215, "1. Фаза реєстрації (Enrollment, один раз)", size=13, bold=True, color=NEG))

    frags.append(rect(50, 235, 345, 45, fill="#eaf0fd", stroke=NEG, sw=1, rx=4))
    frags.append(mtext(222, 255, ["Зняття початкового відбитка PUF (R_0)", "Генерація криптографічного ключа K"], size=11, color=NEG))

    frags.append(arrow(222, 280, 222, 305, color=LINE, sw=1.5))

    frags.append(rect(50, 305, 345, 55, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(222, 325, ["Обчислення допоміжних даних (Helper Data W)", "Код виправлення помилок (BCH / Reed-Muller)", "W = Syndrome(R_0, K)"], size=10))

    frags.append(text(222, 382, "Helper Data не розкриває ключ і лежить у відкритому Flash", size=10, italic=True, color=MUTED))

    # Права колонка: Фаза відновлення (Reconstruction) при кожному старті
    frags.append(rect(445, 190, 385, 210, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(637, 215, "2. Фаза відновлення (Reconstruction, щоразу)", size=13, bold=True, color=FIELD))

    frags.append(rect(465, 235, 345, 45, fill="#f4f6f8", stroke=LINE, sw=1, rx=4))
    frags.append(mtext(637, 255, ["Подача живлення → Зашумлений відбиток R'", "Читання Helper Data W з Flash пам'яті"], size=11))

    frags.append(arrow(637, 280, 637, 305, color=FIELD, sw=1.5))

    frags.append(rect(465, 305, 345, 55, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    frags.append(mtext(637, 325, ["Корекція помилок алгоритмом декодування:", "K = Decode(R', W) → Точний ідентичний ключ", "Ключ живе тільки в регістрах під час роботи"], size=10, bold=True, color=FIELD))

    frags.append(text(637, 382, "При вимкненні живлення ключ безслідно зникає", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "puf-entropy-reconstruction.svg"), w, h, *frags)


def fig_secure_element_protocol_flow():
    """Фігура 5: Протокол взаємодії MCU з Secure Element по I2C."""
    w, h = 860, 430
    frags = []

    frags.append(text(430, 24, "Протокол взаємодії: виконання цифрового підпису без передачі ключа", size=16, bold=True))

    # Лінія хоста (MCU) та чіпа (ATECC608)
    frags.append(rect(80, 50, 220, 45, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(190, 78, "Головний контролер (MCU)", size=13, bold=True, color=NEG))
    frags.append(line(190, 95, 190, 410, color=NEG, sw=1.5, dash="4,4"))

    frags.append(rect(560, 50, 220, 45, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(670, 78, "Secure Element (ATECC608)", size=13, bold=True, color=FIELD))
    frags.append(line(670, 95, 670, 240, color=FIELD, sw=1.5, dash="4,4"))
    frags.append(line(670, 295, 670, 410, color=FIELD, sw=1.5, dash="4,4"))

    # Крок 1: Wake Pulse
    frags.append(arrow(190, 125, 670, 125, color=LINE, sw=1.8))
    frags.append(rect(310, 110, 240, 28, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(430, 128, "1. Wake Pulse (SDA low > 60 мкс)", size=11, bold=True))

    frags.append(arrow(670, 160, 190, 160, color=LINE, sw=1.8))
    frags.append(rect(330, 147, 200, 26, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(430, 164, "Відповідь Ready (0x11)", size=11, italic=True))

    # Крок 2: Відправка кадру команди Sign
    frags.append(arrow(190, 205, 670, 205, color=NEG, sw=2))
    frags.append(rect(260, 190, 340, 30, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(mtext(430, 210, ["2. Команда Sign: [Len][Op=0x41][Slot=0][Digest 32B][CRC16]"], size=10, bold=True, color=NEG))

    # Крок 3: Обчислення всередині Secure Element
    frags.append(rect(590, 240, 160, 55, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(mtext(670, 260, ["3. Обчислення ECDSA", "Ключ береться зі слота", "t_EXEC ≈ 60-110 мс"], size=10, bold=True, color=POS))

    # Крок 4: Читання підпису
    frags.append(arrow(670, 320, 190, 320, color=FIELD, sw=2))
    frags.append(rect(270, 305, 320, 30, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    frags.append(mtext(430, 325, ["4. Відповідь: [Len=67][Підпис R, S (64 байти)][CRC16]"], size=10, bold=True, color=FIELD))

    # Крок 5: Sleep
    frags.append(arrow(190, 365, 670, 365, color=LINE, sw=1.5))
    frags.append(rect(320, 352, 220, 26, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(430, 369, "5. Sleep Token (0x01) → Сон (I < 150 нА)", size=10))

    frags.append(text(430, 405, "Приватний ключ жодного разу не перетинав фізичну шину зв'язку", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "secure-element-protocol-flow.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_flash_vulnerabilities()
    fig_efuse_silicon_isolation()
    fig_secure_element_architecture()
    fig_puf_entropy_reconstruction()
    fig_secure_element_protocol_flow()
    print("Всі 5 фігур успішно згенеровано.")
