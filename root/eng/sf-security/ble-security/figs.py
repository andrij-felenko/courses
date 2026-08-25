# -*- coding: utf-8 -*-
"""Генератор фігур для теми ble-security (Безпека й спарювання BLE)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. smp-stack-position: положення SMP та апаратного шифрування у стеку BLE ──
def fig_smp_stack_position():
    W, H = 840, 480
    p = []

    # Верхній рівень: Застосунок
    app_b, _, _ = textbox(420, 40, "Рівень застосунку (Application)\nПрофілі безпеки, бізнес-логіка, взаємодія з користувачем (PIN / Numeric Comparison)",
                          size=11, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.4, bold=False, min_w=760)
    p.append(app_b)

    # Рівень хоста
    p.append(text(420, 95, "Рівень хоста (Host — стек протоколів мікроконтролера)", size=12, color=MUTED, bold=True))

    # GAP / GATT
    gap_b, _, _ = textbox(170, 170, "GAP / GATT\n• Визначення рівнів безпеки\n• Запит зв'язку Security Request\n• Реєстрація IO-можливостей",
                          size=10, pad=10, fill="#ffffff", stroke=MUTED, sw=1.2, bold=False, min_w=240)
    p.append(gap_b)

    # SMP (акцент)
    smp_b, _, _ = textbox(440, 170, "Security Manager (SMP)\n• Протокол спарювання (Legacy / LESC)\n• Обмін ключами ECDH P-256\n• Генерація LTK, IRK, CSRK\n• Перевірка захисту від MITM",
                          size=10, pad=10, fill="#eafaf0", stroke=FIELD, sw=2.0, bold=False, min_w=250)
    p.append(smp_b)

    # L2CAP
    l2cap_b, _, _ = textbox(710, 170, "L2CAP\nКанальний рівень хоста\nФіксований канал CID 0x0006\n(SMP Channel)",
                            size=10, pad=10, fill="#ffffff", stroke=MUTED, sw=1.2, bold=False, min_w=230)
    p.append(l2cap_b)

    # Стрілки взаємодії на хості
    p.append(arrow(295, 170, 310, 170, color=MUTED, sw=1.5))
    p.append(arrow(570, 170, 590, 170, color=FIELD, sw=1.8))

    # Інтерфейс HCI
    p.append(line(40, 260, 800, 260, color=LINE, sw=1.8, dash="6,4"))
    p.append(text(420, 252, "HCI (Host Controller Interface) — передача сесійних ключів LTK/SKD/IV у контролер", size=10, color=MUTED, italic=True))

    # Рівень контролера
    p.append(text(420, 285, "Рівень контролера (Controller — радіотракт та апаратний криптопроцесор)", size=12, color=MUTED, bold=True))

    # Link Layer + AES CCM
    ll_b, _, _ = textbox(240, 370, "Link Layer (LL)\n• Протокол керування шифруванням LLCP\n• Кадри LL_ENC_REQ / LL_ENC_RSP\n• Лічильник пакетів для Nonce\n• Відновлення зв'язку (Bonding)",
                         size=10, pad=10, fill="#eef4ff", stroke=NEG, sw=1.5, bold=False, min_w=360)
    p.append(ll_b)

    aes_b, _, _ = textbox(620, 370, "Апаратний блок AES-128 CCM\n• Потокове шифрування корисного навантаження\n• Обчислення 4-байтного коду автентичності MIC\n• Захист від підміни та повторення кадрів",
                          size=10, pad=10, fill="#fdf2e9", stroke=POS, sw=1.8, bold=False, min_w=360)
    p.append(aes_b)

    p.append(arrow(425, 370, 435, 370, color=POS, sw=1.8))

    render(os.path.join(OUT, "smp-stack-position.svg"), W, H, *p,
           title="Архітектура безпеки BLE: положення SMP та апаратного шифрування")


# ── 2. pairing-phases: три фази процедури спарювання BLE ─────────────────────
def fig_pairing_phases():
    W, H = 840, 500
    p = []

    # Фаза 1: Узгодження
    p.append(rect(30, 20, 780, 130, fill="#f4f8fb", stroke=NEG, sw=1.5, rx=6))
    p.append(text(50, 45, "Фаза 1: Узгодження параметрів безпеки (Pairing Feature Exchange)", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(50, 70, "• Ініціатор надсилає Pairing Request, відповідач повертає Pairing Response (L2CAP CID 0x0006)", size=10, color=INK, anchor="start"))
    p.append(text(50, 92, "• Обмін прапорцями: IO Capabilities, OOB Data Flag, AuthReq (Bonding, MITM, Secure Connections SC)", size=10, color=INK, anchor="start"))
    p.append(text(50, 114, "• Вибір криптографічного протоколу (Legacy або LESC) та моделі асоціації (Just Works / Passkey / NumComp / OOB)", size=10, color=INK, anchor="start"))
    p.append(text(50, 136, "• Узгодження розміру ключа шифрування (від 7 до 16 байтів)", size=10, color=MUTED, anchor="start"))

    p.append(arrow(420, 150, 420, 175, color=LINE, sw=2.0))

    # Фаза 2: Автентифікація
    p.append(rect(30, 175, 780, 165, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(50, 200, "Фаза 2: Автентифікація та генерація сесійних ключів шифрування", size=12, color=FIELD, bold=True, anchor="start"))
    
    # Розгалуження Legacy vs LESC всередині фази 2
    leg_box, _, _ = textbox(225, 265, "LE Legacy Pairing\n• Введення TK (Temporary Key 0..999999)\n• Обмін випадковими числами Mrand / Srand\n• Генерація STK = s1(TK, Srand, Mrand)\n• Нестійкий до пасивного перехоплення!",
                            size=9.5, pad=6, fill="#ffffff", stroke=POS, sw=1.4, min_w=350)
    p.append(leg_box)

    lesc_box, _, _ = textbox(615, 265, "LE Secure Connections (LESC)\n• Генерація пар ключів ECDH P-256\n• Обмін публічними ключами PKa, PKb\n• Обчислення DHKey = ECDH(SK, PK_peer)\n• Виведення LTK = f5(DHKey, ...) без передачі в ефір!",
                             size=9.5, pad=6, fill="#ffffff", stroke=FIELD, sw=1.6, min_w=370)
    p.append(lesc_box)

    p.append(arrow(420, 340, 420, 365, color=LINE, sw=2.0))

    # Фаза 3: Розподіл ключів
    p.append(rect(30, 365, 780, 115, fill="#fdfaf3", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(50, 390, "Фаза 3: Трансляція та збереження довгострокових ключів (Key Distribution / Bonding)", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(50, 415, "• Виконується виключно в уже зашифрованому каналі канального рівня (Link Layer Encryption)", size=10, color=INK, anchor="start"))
    p.append(text(50, 437, "• Розподіл IRK (Identity Resolving Key) — для генерації та резолвінгу приватних адрес RPA", size=10, color=INK, anchor="start"))
    p.append(text(50, 459, "• Розподіл CSRK (Connection Signature Resolving Key) — для підпису даних ATT без шифрування сесії", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "pairing-phases.svg"), W, H, *p,
           title="Три послідовні фази процедури спарювання в протоколі SMP")


# ── 3. association-matrix: матриця вибору моделі асоціації за IO Capabilities ─
def fig_association_matrix():
    W, H = 840, 450
    p = []

    # Заголовок таблиці
    p.append(text(420, 25, "Матриця вибору моделі асоціації (за відсутності OOB та прапорці MITM=1)", size=13, color=INK, bold=True))

    cols = ["Відповідач →\nІніціатор ↓", "Display\nOnly", "Display\nYesNo", "Keyboard\nOnly", "NoInput\nNoOutput", "Keyboard\nDisplay"]
    x_positions = [40, 180, 310, 440, 570, 700]
    widths = [135, 125, 125, 125, 125, 125]

    # Рядки
    rows_data = [
        ("Display Only", ["Just Works", "Just Works", "Passkey Entry\n(Resp inputs)", "Just Works", "Passkey Entry\n(Resp inputs)"]),
        ("Display YesNo", ["Just Works", "Numeric Comp*\n(Just Works Leg)", "Passkey Entry\n(Resp inputs)", "Just Works", "Numeric Comp*\n(Passkey Leg)"]),
        ("Keyboard Only", ["Passkey Entry\n(Init inputs)", "Passkey Entry\n(Init inputs)", "Passkey Entry\n(Both input)", "Just Works", "Passkey Entry\n(Init inputs)"]),
        ("NoInput NoOutput", ["Just Works", "Just Works", "Just Works", "Just Works", "Just Works"]),
        ("Keyboard Display", ["Passkey Entry\n(Init inputs)", "Numeric Comp*\n(Resp inputs Leg)", "Passkey Entry\n(Resp inputs)", "Just Works", "Numeric Comp*\n(Passkey Leg)"])
    ]

    # Малюємо сітку колонок заголовка
    y_h = 50
    for i in range(6):
        w_cell = widths[i]
        x_cell = x_positions[i]
        p.append(rect(x_cell, y_h, w_cell, 45, fill="#edf2f7", stroke=LINE, sw=1.0))
        lines = cols[i].split("\n")
        if len(lines) == 1:
            p.append(text(x_cell + w_cell/2, y_h + 26, lines[0], size=10, bold=True))
        else:
            p.append(text(x_cell + w_cell/2, y_h + 18, lines[0], size=9.5, bold=True))
            p.append(text(x_cell + w_cell/2, y_h + 34, lines[1], size=9.5, bold=True))

    # Заповнюємо рядки
    for r_idx, (r_name, r_vals) in enumerate(rows_data):
        y_r = y_h + 45 + r_idx * 58
        # Назва рядка
        p.append(rect(x_positions[0], y_r, widths[0], 58, fill="#edf2f7", stroke=LINE, sw=1.0))
        p.append(text(x_positions[0] + widths[0]/2, y_r + 32, r_name, size=9.5, bold=True))

        for c_idx, val in enumerate(r_vals):
            x_c = x_positions[c_idx + 1]
            w_c = widths[c_idx + 1]
            
            # Колір заливки залежно від моделі
            if "Numeric Comp" in val:
                f_color = "#eafaf0"  # зелений (LESC захищений)
                b_color = FIELD
            elif "Passkey" in val:
                f_color = "#eef4ff"  # синій (PIN)
                b_color = NEG
            else:
                f_color = "#fdf2e9"  # помаранчевий (Just Works без MITM)
                b_color = POS

            p.append(rect(x_c, y_r, w_c, 58, fill=f_color, stroke=b_color, sw=1.0))
            lines = val.split("\n")
            if len(lines) == 1:
                p.append(text(x_c + w_c/2, y_r + 32, lines[0], size=9.5, bold=True, color=b_color))
            else:
                p.append(text(x_c + w_c/2, y_r + 24, lines[0], size=9.5, bold=True, color=b_color))
                p.append(text(x_c + w_c/2, y_r + 42, lines[1], size=9.0, color=MUTED))

    # Виноска знизу
    p.append(text(420, 405, "* Модель Numeric Comparison підтримується лише в LE Secure Connections (Bluetooth 4.2+).", size=9.5, color=INK, italic=True))
    p.append(text(420, 425, "У LE Legacy Pairing відповідна комбінація апаратури деградує до Just Works або Passkey Entry.", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "association-matrix.svg"), W, H, *p,
           title="Матриця вибору моделі асоціації BLE SMP за можливостями вводу-виводу")


# ── 4. legacy-vs-lesc-crypto: криптографічне порівняння Legacy та LESC ────────
def fig_legacy_vs_lesc_crypto():
    W, H = 840, 480
    p = []

    # Заголовок
    p.append(text(420, 25, "Порівняння криптографічних конвеєрів генерації ключів BLE", size=13, color=INK, bold=True))

    # Ліва колонка: Legacy Pairing
    p.append(rect(30, 45, 375, 415, fill="#fffaf8", stroke=POS, sw=1.5, rx=6))
    p.append(text(217, 72, "LE Legacy Pairing (Bluetooth 4.0/4.1)", size=11, color=POS, bold=True))

    leg_t, _, _ = textbox(217, 120, "1. Тимчасовий ключ TK (128 біт)\n• Just Works: TK = 0\n• Passkey: TK = PIN (000000..999999)\n• OOB: передача через зовнішній канал",
                          size=9.5, pad=6, fill="#ffffff", stroke=MUTED, sw=1.0, min_w=340)
    p.append(leg_t)

    p.append(arrow(217, 155, 217, 175, color=POS, sw=1.4))

    leg_c, _, _ = textbox(217, 210, "2. Підтвердження автентичності (c1)\n• Mconfirm = c1(TK, Mrand, PairingCmds, ...)\n• Sconfirm = c1(TK, Srand, PairingCmds, ...)\n• Обмін Mconfirm, Sconfirm, Mrand, Srand в ефірі",
                          size=9.5, pad=6, fill="#ffffff", stroke=MUTED, sw=1.0, min_w=340)
    p.append(leg_c)

    p.append(arrow(217, 250, 217, 270, color=POS, sw=1.4))

    leg_s, _, _ = textbox(217, 305, "3. Обчислення короткострокового ключа (s1)\nSTK = s1(TK, Srand, Mrand) = AES-128_TK(Srand || Mrand)\n• STK використовується для шифрування каналу Link Layer",
                          size=9.5, pad=6, fill="#ffffff", stroke=MUTED, sw=1.0, min_w=340)
    p.append(leg_s)

    p.append(arrow(217, 345, 217, 365, color=POS, sw=1.4))

    leg_w, _, _ = textbox(217, 405, "4. Розподіл LTK (Phase 3)\n• LTK генерується і передається через радіоефір,\n  зашифрований за допомогою STK.\n⚠ Вразливий до повного зламу при перехопленні!",
                          size=9.5, pad=6, fill="#feebe8", stroke=POS, sw=1.4, bold=True, min_w=340)
    p.append(leg_w)


    # Права колонка: LE Secure Connections (LESC)
    p.append(rect(435, 45, 375, 415, fill="#f6fcf8", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(622, 72, "LE Secure Connections (Bluetooth 4.2+)", size=11, color=FIELD, bold=True))

    lesc_t, _, _ = textbox(622, 120, "1. Протокол Діффі-Геллмана ECDH P-256\n• Кожен генерує пару (SK_a, PK_a) та (SK_b, PK_b)\n• Відкритий обмін публічними ключами PK_a, PKb\n• Спільний секрет: DHKey = ECDH(SK_local, PK_peer)",
                           size=9.5, pad=6, fill="#ffffff", stroke=MUTED, sw=1.0, min_w=340)
    p.append(lesc_t)

    p.append(arrow(622, 155, 622, 175, color=FIELD, sw=1.4))

    lesc_c, _, _ = textbox(622, 210, "2. Автентифікація через AES-CMAC (f4 / g2)\n• f4(PK_a, PK_b, Na, Nb) — підтвердження\n• g2(PK_a, PK_b, Na, Nb) mod 10^6 — 6-значний код\n  для перевірки Numeric Comparison на дисплеях",
                           size=9.5, pad=6, fill="#ffffff", stroke=MUTED, sw=1.0, min_w=340)
    p.append(lesc_c)

    p.append(arrow(622, 250, 622, 270, color=FIELD, sw=1.4))

    lesc_s, _, _ = textbox(622, 305, "3. Генерація ключів через f5 (KDF)\n(MacKey, LTK) = f5(DHKey, Na, Nb, AddrA, AddrB)\n• MacKey використовується для перевірки f6 (DHKey Check)\n• LTK генерується повністю автономно на обох вузлах!",
                           size=9.5, pad=6, fill="#ffffff", stroke=MUTED, sw=1.0, min_w=340)
    p.append(lesc_s)

    p.append(arrow(622, 345, 622, 365, color=FIELD, sw=1.4))

    lesc_w, _, _ = textbox(622, 405, "4. Довгостроковий ключ LTK готовий\n• LTK НІКОЛИ не передається радіоефіром!\n• Стійкий проти пасивного підслуховування\n• Захист від MITM за наявності дисплея або OOB",
                           size=9.5, pad=6, fill="#eafaf0", stroke=FIELD, sw=1.4, bold=True, min_w=340)
    p.append(lesc_w)

    render(os.path.join(OUT, "legacy-vs-lesc-crypto.svg"), W, H, *p,
           title="Криптографічні конвеєри генерації ключів: Legacy проти LESC")


# ── 5. ll-aes-ccm-encryption: шифрування кадрів Link Layer через AES-128 CCM ──
def fig_ll_aes_ccm_encryption():
    W, H = 840, 460
    p = []

    p.append(text(420, 25, "Конвеєр автентифікованого шифрування AES-128 CCM на канальному рівні (Link Layer)", size=12, color=INK, bold=True))

    # Вхідні блоки зверху
    p.append(rect(40, 55, 220, 80, fill="#f0f4f8", stroke=MUTED, sw=1.2, rx=5))
    p.append(text(150, 75, "Заголовок PDU (16 біт)", size=10, bold=True))
    p.append(text(150, 95, "LLID, NESN, SN, MD, Length", size=9.5, color=MUTED))
    p.append(text(150, 115, "Додаткові автентифіковані дані (AAD)", size=9.0, color=NEG))

    p.append(rect(290, 55, 260, 80, fill="#fdfaf3", stroke=MUTED, sw=1.2, rx=5))
    p.append(text(420, 75, "Корисне навантаження PDU", size=10, bold=True))
    p.append(text(420, 95, "Дані L2CAP / ATT / SMP (Plaintext)", size=9.5, color=MUTED))
    p.append(text(420, 115, "Довжина: від 0 до 251 байта (DLE)", size=9.0, color=INK))

    p.append(rect(580, 55, 220, 80, fill="#fbf2ea", stroke=POS, sw=1.2, rx=5))
    p.append(text(690, 75, "13-байтний Nonce", size=10, bold=True, color=POS))
    p.append(text(690, 95, "• Packet Counter (39 біт)", size=9.5, color=INK))
    p.append(text(690, 115, "• Direction bit (1 біт) + IV (64 біти)", size=9.0, color=INK))

    # Стрілки до блоку AES-CCM
    p.append(arrow(150, 135, 280, 205, color=NEG, sw=1.5))
    p.append(arrow(420, 135, 420, 205, color=INK, sw=1.5))
    p.append(arrow(690, 135, 560, 205, color=POS, sw=1.5))

    # Блок шифрування AES-CCM
    p.append(rect(240, 205, 360, 110, fill="#eef4ff", stroke=NEG, sw=2.0, rx=8))
    p.append(text(420, 230, "Апаратне ядро AES-128 CCM", size=12, color=NEG, bold=True))
    p.append(text(420, 255, "Сесійний ключ шифрування: Session Key (SK = 128 біт)", size=10, color=INK, bold=True))
    p.append(text(420, 278, "• CBC-MAC: обчислення цілісності за AAD + Plaintext", size=9.5, color=MUTED))
    p.append(text(420, 298, "• CTR Mode: потокове шифрування корисного навантаження", size=9.5, color=MUTED))

    # Стрілки до вихідного PDU
    p.append(arrow(340, 315, 260, 365, color=INK, sw=1.6))
    p.append(arrow(500, 315, 580, 365, color=FIELD, sw=1.8))

    # Вихідний зашифрований пакет
    p.append(rect(40, 365, 760, 80, fill="#f0fff4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(420, 385, "Зашифрований канальний пакет в ефірі (Encrypted Data Physical Channel PDU)", size=11, color=FIELD, bold=True))

    # Частини кадру внизу
    p.append(rect(60, 400, 160, 32, fill="#ffffff", stroke=MUTED, sw=1.0))
    p.append(text(140, 420, "Заголовок PDU (16 біт)", size=9.5))

    p.append(rect(230, 400, 360, 32, fill="#eef4ff", stroke=NEG, sw=1.2))
    p.append(text(410, 420, "Зашифроване навантаження (Encrypted Payload)", size=9.5, color=NEG, bold=True))

    p.append(rect(600, 400, 180, 32, fill="#eafaf0", stroke=FIELD, sw=1.5))
    p.append(text(690, 420, "MIC: Код автентичності (4 байти)", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "ll-aes-ccm-encryption.svg"), W, H, *p,
           title="Структура та конвеєр шифрування AES-128 CCM канального рівня BLE")


def main():
    fig_smp_stack_position()
    fig_pairing_phases()
    fig_association_matrix()
    fig_legacy_vs_lesc_crypto()
    fig_ll_aes_ccm_encryption()
    print("All figures generated successfully in", OUT)


if __name__ == "__main__":
    main()
