# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. cia-triad-embedded: Тріада безпеки у вбудованих системах ────────────────
def fig_cia_triad():
    W, H = 880, 420
    p = []

    # Три колони: Конфіденційність, Цілісність, Автентичність
    # 1. Конфіденційність
    p.append(rect(40, 70, 250, 310, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    p.append(textbox(165, 100, "Конфіденційність\n(Confidentiality)", size=13, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    p.append(rect(55, 145, 220, 70, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(165, 170, "Захист від підглядання", size=12, color=INK, bold=True))
    p.append(text(165, 195, "Шифрування: AES-GCM / CTR", size=11, color=MUTED))
    p.append(fitbox(55, 230, 220, 135, "Загроза:\nпасивне перехоплення\n(SDR, логічний аналізатор\nна шині UART / SPI / RF).\n\nБез неї: дані читає будь-хто.", size=11, pad=6, fill="#f4f6f8", stroke="#d0d7de"))

    # 2. Цілісність
    p.append(rect(315, 70, 250, 310, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=8))
    p.append(textbox(440, 100, "Цілісність\n(Integrity)", size=13, color=FIELD, bold=True, fill="#eef6ef", stroke=FIELD)[0])
    p.append(rect(330, 145, 220, 70, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(440, 170, "Захист від спотворень", size=12, color=INK, bold=True))
    p.append(text(440, 195, "Геш / MAC: SHA-256, Tag", size=11, color=MUTED))
    p.append(fitbox(330, 230, 220, 135, "Загроза:\nспотворення бітів завадою\nабо ін'єкція байтів у пакет.\n\nУвага: CRC ловить шум,\nале безсила проти ворога!", size=11, pad=6, fill="#f4f6f8", stroke="#d0d7de"))

    # 3. Автентичність
    p.append(rect(590, 70, 250, 310, fill="#f8fafc", stroke=POS, sw=1.8, rx=8))
    p.append(textbox(715, 100, "Автентичність\n(Authenticity)", size=13, color=POS, bold=True, fill="#fdecea", stroke=POS)[0])
    p.append(rect(605, 145, 220, 70, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(715, 170, "Підтвердження джерела", size=12, color=INK, bold=True))
    p.append(text(715, 195, "Секретний MAC: HMAC / GMAC", size=11, color=MUTED))
    p.append(fitbox(605, 230, 220, 135, "Загроза:\nпідробка відправника,\nатака повтором (replay).\n\nГоловне в IoT:\nчужий пакет не виконається.", size=11, pad=6, fill="#f4f6f8", stroke="#d0d7de"))

    render(os.path.join(OUT, "cia-triad-embedded.svg"), W, H, *p,
           title="Тріада безпеки (CIA Triad) у вбудованих пристроях")


# ── 2. aes-modes-comparison: Порівняння режимів шифрування ────────────────────
def fig_aes_modes():
    W, H = 940, 480
    p = []

    # 1. ECB (Заборонено)
    p.append(rect(30, 60, 270, 390, fill="#fff5f5", stroke=POS, sw=2.0, rx=8))
    p.append(textbox(165, 88, "ECB Mode (Electronic Codebook)\nЗАБОРОНЕНО", size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)[0])
    p.append(fitbox(45, 125, 240, 48, "Блок 1: [AAAA] → AES(K) → [0x8F9C]\nБлок 2: [AAAA] → AES(K) → [0x8F9C]", size=10, fill="#ffffff", stroke=POS))
    p.append(fitbox(45, 185, 240, 120, "Чому небезпечно:\n• Однаковий відкритий блок\n  дає однаковий шифротекст.\n• Витікає структура даних (Tux).\n• Вразливий до заміни блоків\n  та підміни полів без ключа.", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(45, 318, 240, 115, "Вирок:\nКатегорично заборонено\nдля будь-яких пакетів\nта збереження в пам'яті.", size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # 2. CBC / CTR (Тільки шифрування, без автентичності)
    p.append(rect(335, 60, 270, 390, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    p.append(textbox(470, 88, "CBC / CTR Mode\nТільки шифрування", size=12, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    p.append(fitbox(350, 125, 240, 48, "CTR: Keystream = AES(K, Nonce||Ctr)\nCiphertext = Plaintext ⊕ Keystream", size=10, fill="#ffffff", stroke=NEG))
    p.append(fitbox(350, 185, 240, 120, "Особливості та пастки:\n• CTR: потоковий, швидкий,\n  без падінгу, паралельний.\n• Смертельна пастка CTR:\n  повтор Nonce нищить захист!\n• Немає перевірки цілісності.", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(350, 318, 240, 115, "Вирок:\nЗахищає від підглядання,\nале НЕ захищає від підміни\nбайтів ворогом (Bit-flipping).", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))

    # 3. GCM / CCM (AEAD — Золотий стандарт)
    p.append(rect(640, 60, 270, 390, fill="#f4faf5", stroke=FIELD, sw=2.0, rx=8))
    p.append(textbox(775, 88, "GCM / CCM (AEAD Mode)\nЗолотий стандарт", size=12, color=FIELD, bold=True, fill="#eef6ef", stroke=FIELD)[0])
    p.append(fitbox(655, 125, 240, 48, "Шифрування: AES-CTR\nАвтентифікація: GHASH(C, AAD) → Tag", size=10, fill="#ffffff", stroke=FIELD))
    p.append(fitbox(655, 185, 240, 120, "Переваги AEAD:\n• Одночасне шифрування даних\n  і автентифікація заголовків (AAD).\n• 16-байтний тег автентичності.\n• Підроблений пакет відкидається\n  ДО розшифрування.", size=10, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(655, 318, 240, 115, "Вирок:\nЄдино правильний вибір\nдля радіоканалів, мережі\nта оновлення прошивки.", size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD))

    render(os.path.join(OUT, "aes-modes-comparison.svg"), W, H, *p,
           title="Режими симетричного шифрування AES: від вразливого ECB до AEAD")


# ── 3. hmac-construction: Структура обчислення HMAC ───────────────────────────
def fig_hmac_construction():
    W, H = 900, 420
    p = []

    # Вхідний ключ K
    p.append(textbox(120, 140, "Секретний ключ K\n(довжина ≤ 64 байти)", size=12, bold=True, fill="#fdf0e6", stroke="#c07a2e", color="#9a5a1e")[0])

    # Крок 1: Генерація K ⊕ ipad та K ⊕ opad
    p.append(arrow(210, 120, 270, 100))
    p.append(arrow(210, 160, 270, 260))

    p.append(textbox(340, 100, "K ⊕ ipad\n(ipad = 0x36)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)[0])
    p.append(textbox(340, 260, "K ⊕ opad\n(opad = 0x5C)", size=11, bold=True, fill="#fdecea", stroke=POS, color=POS)[0])

    # Вхідне повідомлення M
    p.append(textbox(340, 170, "Повідомлення M\n(довільна довжина)", size=11, bold=True, fill="#f4f6f8", stroke=MUTED)[0])

    # Конкатенація і внутрішній геш
    p.append(arrow(405, 100, 470, 125))
    p.append(arrow(405, 170, 470, 135))

    p.append(rect(470, 100, 160, 60, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(550, 125, "Внутрішній геш", size=12, color=FIELD, bold=True))
    p.append(text(550, 145, "SHA-256( (K⊕ipad) || M )", size=10, color=INK))

    # Вихід внутрішнього гешу (32 байти)
    p.append(arrow(630, 130, 690, 170))
    p.append(text(660, 140, "32B", size=10, color=MUTED, bold=True))

    # Конкатенація з K ⊕ opad і зовнішній геш
    p.append(arrow(405, 260, 690, 210))

    p.append(rect(690, 160, 170, 80, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(775, 185, "Зовнішній геш", size=12, color=FIELD, bold=True))
    p.append(text(775, 205, "SHA-256( (K⊕opad) || Inner )", size=9, color=INK))
    p.append(text(775, 225, "Захист від Length Extension", size=9, color=FIELD, italic=True))

    # Результат: HMAC
    p.append(arrow(775, 240, 775, 310))
    p.append(textbox(775, 345, "Результат: HMAC-SHA256 (32 байти)\nКод автентичності повідомлення (MAC)", size=12, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD)[0])

    # Пояснювальний текст унизу
    p.append(rect(50, 320, 520, 65, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(310, 342, "Чому не можна просто SHA-256(K || M):", size=11, color=POS, bold=True))
    p.append(text(310, 365, "Простий префіксний геш ламається атакою подовженням (Length Extension Attack).", size=10, color=INK))

    render(os.path.join(OUT, "hmac-construction.svg"), W, H, *p,
           title="Двоетапна конструкція HMAC (RFC 2104) проти атак подовження повідомлення")


# ── 4. trng-entropy-pipeline: Генерація справжніх випадкових чисел ─────────────
def fig_trng_pipeline():
    W, H = 940, 430
    p = []

    # 1. Фізичне джерело шуму
    p.append(rect(30, 80, 180, 240, fill="#ffffff", stroke=NEG, sw=1.8, rx=8))
    p.append(textbox(120, 105, "Фізичне джерело\nшуму (Noise Source)", size=11, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    p.append(fitbox(40, 150, 160, 155, "• Тепловий шум p-n\n  переходу (Zener)\n• Фазовий джитер\n  кільцевих генераторів\n  (Ring Oscillators)\n• Шум внутрішнього АЦП\n• Метастабільність SRAM", size=10, fill="#f8fafc", stroke=MUTED))

    # Стрілка 1 -> 2
    p.append(arrow(210, 200, 260, 200))
    p.append(text(235, 190, "сирий бітпотік", size=9, color=MUTED))

    # 2. Дерандомізатор (Von Neumann)
    p.append(rect(260, 80, 190, 240, fill="#ffffff", stroke=FIELD, sw=1.8, rx=8))
    p.append(textbox(355, 105, "Дерандомізатор\n(Von Neumann)", size=11, color=FIELD, bold=True, fill="#eef6ef", stroke=FIELD)[0])
    p.append(fitbox(270, 150, 170, 155, "Усунення зміщення (Bias):\n• 00 → відкинути\n• 11 → відкинути\n• 01 → вихід 0\n• 10 → вихід 1\n\nРезультат:\nсуворе 50/50 без перекосу", size=10, fill="#f8fafc", stroke=MUTED))

    # Стрілка 2 -> 3
    p.append(arrow(450, 200, 500, 200))
    p.append(text(475, 190, "чисті біти", size=9, color=MUTED))

    # 3. Тести якості на льоту
    p.append(rect(500, 80, 180, 240, fill="#ffffff", stroke="#c07a2e", sw=1.8, rx=8))
    p.append(textbox(590, 105, "Тести якості на льоту\n(NIST SP 800-90B)", size=11, color="#9a5a1e", bold=True, fill="#fdf0e6", stroke="#c07a2e")[0])
    p.append(fitbox(510, 150, 160, 155, "Health Monitoring:\n• Repetition Count Test\n  (захист від зависання)\n• Adaptive Proportion\n  (контроль ентропії)\n\nЗбій → генератор\nблокує вихід і б'є тривогу", size=10, fill="#f8fafc", stroke=MUTED))

    # Стрілка 3 -> 4
    p.append(arrow(680, 200, 730, 200))
    p.append(text(705, 190, "ентропія", size=9, color=MUTED))

    # 4. Ентропійний пул і CSPRNG
    p.append(rect(730, 80, 180, 240, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    p.append(textbox(820, 105, "CSPRNG / DRBG\n(CTR-DRBG / HMAC)", size=11, color=POS, bold=True, fill="#fdecea", stroke=POS)[0])
    p.append(fitbox(740, 150, 160, 155, "Криптостійкий генератор:\n• Періодичний reseed\n• Швидкість: МБ/с\n• Безпечні Nonce,\n  сеансові ключі,\n  сіль та IV", size=10, fill="#f8fafc", stroke=MUTED))

    # Нижній висновок
    p.append(rect(140, 345, 660, 50, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(470, 365, "Категорично заборонено: використовувати libc rand() / lrand48() у криптографії!", size=11, color=POS, bold=True))
    p.append(text(470, 383, "Лінійні генератори (LCG) передбачувані вже після перехоплення 2–3 послідовних чисел.", size=10, color=INK))

    render(os.path.join(OUT, "trng-entropy-pipeline.svg"), W, H, *p,
           title="Тракт апаратного генератора справжніх випадкових чисел (TRNG)")


# ── 5. key-storage-security-levels: Рівні захисту ключів ───────────────────────
def fig_key_storage():
    W, H = 920, 460
    p = []

    # 1. Відкрита Flash / Level 0 (Червоний - небезпека)
    p.append(rect(30, 70, 265, 355, fill="#fff5f5", stroke=POS, sw=2.0, rx=8))
    p.append(textbox(162, 98, "Рівень 0: Відкрита Flash\n(Без захисту)", size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)[0])
    p.append(fitbox(45, 140, 235, 130, "Стан:\n• Ключ зашитий у прошивку:\n  const uint8_t key[] = {...}\n• Порт SWD/JTAG відкритий.\n\nАтака:\nЗчитування дампу через OpenOCD\n/ J-Link за 3 секунди.", size=10, fill="#ffffff", stroke=POS))
    p.append(fitbox(45, 285, 235, 125, "Стійкість:\nНульова.\nБудь-хто з $5 програматором\nвикрадає ключ повністю.", size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # 2. Flash Readout Protection / Level 1-2 (Синій - помірний)
    p.append(rect(325, 70, 265, 355, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    p.append(textbox(457, 98, "Рівень 1/2: Flash RDP\n(STM32 RDP / ESP32 eFuse)", size=12, color=NEG, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    p.append(fitbox(340, 140, 235, 130, "Механізм:\n• RDP 1: Заборона читання SWD,\n  скид у Level 0 стирає Flash.\n• RDP 2: Фізичне випалювання\n  порту JTAG (назавжди).\n• ESP32: Flash Encryption.", size=10, fill="#ffffff", stroke=NEG))
    p.append(fitbox(340, 285, 235, 125, "Стійкість:\nЗахист від логічного аналізу.\nАле RDP 1 вразливий до\nглічінгу живлення (glitching)\nта атак побічними каналами.", size=10, fill="#eaf0fd", stroke=NEG, color=INK))

    # 3. Secure Element (Зелений - максимальний)
    p.append(rect(620, 70, 270, 355, fill="#f4faf5", stroke=FIELD, sw=2.0, rx=8))
    p.append(textbox(755, 98, "Рівень 3: Secure Element\n(ATECC608A / OPTIGA Trust)", size=12, color=FIELD, bold=True, fill="#eef6ef", stroke=FIELD)[0])
    p.append(fitbox(635, 140, 240, 130, "Механізм:\n• Окремий захищений крипточип.\n• Ключ НІКОЛИ не виходить на I2C.\n• Апаратна сітка від decapping.\n• Захист від DPA / DEMA.\n• Виконує крипто всередині.", size=10, fill="#ffffff", stroke=FIELD))
    p.append(fitbox(635, 285, 240, 125, "Стійкість:\nМаксимальна апаратна стійкість\nпроти фізичних лабораторій,\nзондів та мікроскопів.", size=11, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD))

    render(os.path.join(OUT, "key-storage-security-levels.svg"), W, H, *p,
           title="Ієрархія захисту криптографічних ключів у мікроконтролерних системах")


if __name__ == "__main__":
    fig_cia_triad()
    fig_aes_modes()
    fig_hmac_construction()
    fig_trng_pipeline()
    fig_key_storage()
    print("All figures generated successfully.")
