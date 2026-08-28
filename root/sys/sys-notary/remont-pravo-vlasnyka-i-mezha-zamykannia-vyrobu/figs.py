# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, text, mtext, textbox, fitbox, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_right_to_repair_spectrum():
    """Спектр замикання виробу: від відкритої ремонтопридатності до монопольного контролю."""
    w, h = 940, 480
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Спектр архітектур ремонтопридатності: від відкритого дизайну до вендорного замикання", size=15, bold=True))

    col_w = 280
    col_gap = 20
    top_y = 55
    col_h = 395

    # 1. Відкрита модульність (Open Modular)
    x1 = 30
    frags.append(rect(x1, top_y, col_w, col_h, fill="#f4fbf7", stroke=FIELD, sw=2, rx=8))
    frags.append(rect(x1, top_y, col_w, 42, fill="#e1f5eb", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(x1 + col_w / 2, top_y + 26, "1. Відкрита модульність", size=14, color=FIELD, bold=True))

    items1 = [
        ("Доступність деталей", "Вільний ринок, стандартні\nтипорозміри, відкритий продаж"),
        ("Сервісні інструменти", "Загальнодоступний інструмент,\nвідкриті схеми та мануали"),
        ("Автентифікація", "Відкриті шини (I2C/SPI),\nвідсутність криптоприв'язки"),
        ("Поведінка при заміні", "Повна функціональність одразу,\nбез сповіщень та обмежень"),
        ("Нормативний статус", "Повна відповідність директивам\nEU Ecodesign & Right to Repair"),
    ]
    cur_y = top_y + 55
    for title, desc in items1:
        frags.append(fitbox(x1 + 10, cur_y, col_w - 20, 60, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#c3e6d5", bold=False))
        cur_y += 66

    # 2. Градуйована безпека (Graded Trust & Safety)
    x2 = x1 + col_w + col_gap
    frags.append(rect(x2, top_y, col_w, col_h, fill="#f4f8fe", stroke=NEG, sw=2, rx=8))
    frags.append(rect(x2, top_y, col_w, 42, fill="#e2edfd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(x2 + col_w / 2, top_y + 26, "2. Градуйована безпека", size=14, color=NEG, bold=True))

    items2 = [
        ("Доступність деталей", "Оригінальні та кваліфіковані\nсумісні сторонні модулі"),
        ("Сервісні інструменти", "Локальна діагностика на пристрої,\nвідкриті API перекалібрування"),
        ("Автентифікація", "On-device Attestation, відкриті\nсертифікати, локальний журнал"),
        ("Поведінка при заміні", "Безпечний режим для сторонніх АКБ,\nінформування без деградацій"),
        ("Нормативний статус", "Баланс безпеки та прав власника,\nвідповідає California SB 244"),
    ]
    cur_y = top_y + 55
    for title, desc in items2:
        frags.append(fitbox(x2 + 10, cur_y, col_w - 20, 60, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#c8ddfa", bold=False))
        cur_y += 66

    # 3. Монопольне замикання (Vendor Lock-in / Parts Pairing)
    x3 = x2 + col_w + col_gap
    frags.append(rect(x3, top_y, col_w, col_h, fill="#fef6f5", stroke=POS, sw=2, rx=8))
    frags.append(rect(x3, top_y, col_w, 42, fill="#fde6e4", stroke=POS, sw=1.5, rx=8))
    frags.append(text(x3 + col_w / 2, top_y + 26, "3. Вендорне замикання", size=14, color=POS, bold=True))

    items3 = [
        ("Доступність деталей", "Ексклюзивно в авторизованих АСЦ,\nзаборона сторонніх ланцюгів"),
        ("Сервісні інструменти", "Закритий пропрієтарний софт,\nобов'язковий хмарний логін"),
        ("Автентифікація", "Parts Pairing: прив'язка серійника\nдо CPU через хмару вендора"),
        ("Поведінка при заміні", "Limp mode / soft-lock (вимикання\nTrueTone, автояскравості, Face ID)"),
        ("Нормативний статус", "Антиконкурентні обмеження,\nпідпадає під санкції FTC та ЄС"),
    ]
    cur_y = top_y + 55
    for title, desc in items3:
        frags.append(fitbox(x3 + 10, cur_y, col_w - 20, 60, f"{title}\n{desc}", size=11, pad=4, fill="#ffffff", stroke="#f8c9c4", bold=False))
        cur_y += 66

    frags.append(text(w / 2, h - 12, "Перехід зліва направо: зростання контролю виробника ціною обмеження права власності та довговічності виробу", size=11, color=MUTED, italic=True))

    out_path = os.path.join(OUT_DIR, "right-to-repair-spectrum.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_component_pairing_handshake():
    """Послідовність криптографічного рукостискання хост-контролера та змінного модуля."""
    w, h = 940, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Криптографічний протокол автентифікації та калібрування змінного модуля", size=15, bold=True))

    # Стовпчики учасників
    h_x = 150     # Хост-контролер / Secure Enclave
    m_x = 790     # Змінний модуль / Secure Element

    # Заголовні блоки учасників
    frags.append(fitbox(h_x - 120, 50, 240, 48, "Головний процесор (Host SoC)\nSecure Enclave / TPM", size=12, pad=4, fill="#e8f0fe", stroke=NEG, bold=True))
    frags.append(fitbox(m_x - 120, 50, 240, 48, "Змінний вузол (Дисплей / BMS)\nSecure Element / EEPROM", size=12, pad=4, fill="#fef3e6", stroke="#d97706", bold=True))

    # Вертикальні лінії життя (Lifelines)
    line_top = 98
    line_bot = 465
    frags.append(line(h_x, line_top, h_x, line_bot, color=MUTED, sw=1.5, dash="4 4"))
    frags.append(line(m_x, line_top, m_x, line_bot, color=MUTED, sw=1.5, dash="4 4"))

    # Покрокові повідомлення та дії
    steps = [
        # Крок 1: Запит дескриптора
        (130, "L2R", "1. CMD_READ_DESCRIPTOR (Запит UUID та типу вузла)", "#333333"),
        # Крок 2: Відповідь дескриптором
        (175, "R2L", "2. PartDescriptor { Type, UID, VendorID, MaxLimits }", "#333333"),
        # Крок 3: Генерація та надсилання Nonce
        (220, "L2R", "3. CMD_AUTH_CHALLENGE { Nonce: 32 байти випадкових даних }", NEG),
        # Дія на модулі: підпис
        (265, "ACTION_R", "Обчислення підпису: ECDSA_Sign(PrivKey, Nonce || UID || Calib)", "#d97706"),
        # Крок 4: Відповідь з підписом
        (310, "R2L", "4. AuthResponse { Signature, CertChain, CalibrationData }", "#d97706"),
        # Дія на хості: перевірка
        (355, "ACTION_L", "Верифікація підпису через Root CA / On-device Attestation", NEG),
        # Крок 5: Результат перевірки та рішення
        (405, "DECISION", "5. Оцінка політики безпеки та призначення робочого профілю", FIELD),
    ]

    for y, kind, msg, col in steps:
        if kind == "L2R":
            frags.append(arrow(h_x, y, m_x, y, color=col, sw=1.8))
            frags.append(fitbox(w / 2 - 200, y - 22, 400, 20, msg, size=11, pad=2, fill="#ffffff", stroke="#d1d5db", color=col, bold=True))
        elif kind == "R2L":
            frags.append(arrow(m_x, y, h_x, y, color=col, sw=1.8))
            frags.append(fitbox(w / 2 - 200, y - 22, 400, 20, msg, size=11, pad=2, fill="#ffffff", stroke="#d1d5db", color=col, bold=True))
        elif kind == "ACTION_R":
            frags.append(rect(m_x - 130, y - 16, 260, 32, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=4))
            frags.append(text(m_x, y + 5, msg, size=10, color="#92400e", bold=True))
        elif kind == "ACTION_L":
            frags.append(rect(h_x - 130, y - 16, 260, 32, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
            frags.append(text(h_x, y + 5, msg, size=10, color="#1e40af", bold=True))
        elif kind == "DECISION":
            frags.append(rect(120, y - 18, 700, 54, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
            frags.append(text(w / 2, y - 2, msg, size=11, color=FIELD, bold=True))
            frags.append(text(w / 2, y + 16, "OEM: Повний режим + калібрування  |  Сумісний: Безпечний ліміт + лог  |  Підробка: Безпечний режим (Safe Fallback)", size=10, color=INK))

    frags.append(text(w / 2, h - 12, "Криптографічний протокол гарантує цілісність даних і захист від підробок без блокування пристрою при заміні вузла", size=11, color=MUTED, italic=True))

    out_path = os.path.join(OUT_DIR, "component-pairing-handshake.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_right_to_repair_spectrum()
    fig_component_pairing_handshake()
