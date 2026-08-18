# -*- coding: utf-8 -*-
"""Фігури до теми «Kerberos: квитки й автентифікація в мережі»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT_BLUE = "#eef3fb"
SOFT_YELLOW = "#fdf8e8"
SOFT_GREEN = "#eafaf1"
SOFT_RED = "#fdedec"
BORDER_BLUE = "#b8d0ee"
BORDER_YELLOW = "#e8d39c"
BORDER_GREEN = "#a9dfbf"
BORDER_RED = "#f5b7b1"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Архітектура Kerberos: Клієнт, KDC (AS + TGS) та Сервер
# ─────────────────────────────────────────────────────────────────────────────
def fig_kdc_architecture():
    W, H = 1000, 560
    f = []

    # Заголовок
    f.append(text(500, 36, "Архітектура Kerberos: довірена третя сторона (KDC) та розподіл ключів", size=15, bold=True))

    # KDC Realm Box
    f.append(rect(340, 70, 620, 460, fill="#fcfcfc", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(360, 95, "Область автентифікації Kerberos (Realm: EXAMPLE.ORG)", size=12, color=MUTED, bold=True, anchor="start"))

    # Client Box
    c_box, _, _ = textbox(170, 240,
                          "Клієнт (Principal)\n"
                          "alice@EXAMPLE.ORG\n\n"
                          "Довгостроковий секрет:\n"
                          "Ключ пароля користувача (K_c)\n"
                          "Отримує: TGT та сервісні квитки",
                          size=12, pad=14, fill=SOFT_BLUE, stroke=BORDER_BLUE, bold=False)
    f.append(c_box)

    # KDC Container Box
    f.append(rect(370, 120, 270, 390, fill="#fafafa", stroke=LINE, sw=1.5, rx=8))
    f.append(text(505, 145, "Key Distribution Center (KDC)", size=13, bold=True))
    f.append(text(505, 165, "Спільна база даних секретів облікових записів", size=11, color=MUTED))

    # KDC Sub-service: AS
    as_box, _, _ = textbox(505, 230,
                           "Authentication Service (AS)\n"
                           "• Перевіряє первинний вхід (пароль)\n"
                           "• Видає квиток TGT\n"
                           "• Генерує сесійний ключ K_{c,tgs}",
                           size=11, pad=10, fill=SOFT_YELLOW, stroke=BORDER_YELLOW)
    f.append(as_box)

    # KDC Sub-service: TGS
    tgs_box, _, _ = textbox(505, 360,
                            "Ticket Granting Service (TGS)\n"
                            "• Перевіряє наданий квиток TGT\n"
                            "• Видає сервісний квиток (ST)\n"
                            "• Генерує сервісний ключ K_{c,s}",
                            size=11, pad=10, fill=SOFT_YELLOW, stroke=BORDER_YELLOW)
    f.append(tgs_box)

    # KDC Master key storage note
    f.append(text(505, 480, "Володіє ключами: K_c, K_{tgs}, K_s", size=11, color=POS, bold=True))

    # Application Server Box
    s_box, _, _ = textbox(810, 360,
                          "Цільовий сервер (Service)\n"
                          "cifs/fs.example.org\n\n"
                          "Довгостроковий секрет:\n"
                          "Ключ служби (K_s)\n"
                          "Не має зв'язку з KDC у рантаймі!",
                          size=12, pad=14, fill=SOFT_GREEN, stroke=BORDER_GREEN)
    f.append(s_box)

    # Connecting Arrows
    f.append(arrow(275, 220, 395, 220, color=INK, sw=1.5))
    f.append(text(335, 210, "1. AS-REQ", size=10, color=INK, bold=True))

    f.append(arrow(395, 245, 275, 245, color=POS, sw=1.5))
    f.append(text(335, 260, "2. AS-REP (TGT)", size=10, color=POS, bold=True))

    f.append(arrow(275, 345, 395, 345, color=INK, sw=1.5))
    f.append(text(335, 335, "3. TGS-REQ", size=10, color=INK, bold=True))

    f.append(arrow(395, 370, 275, 370, color=POS, sw=1.5))
    f.append(text(335, 385, "4. TGS-REP (ST)", size=10, color=POS, bold=True))

    f.append(arrow(275, 440, 690, 440, color=FIELD, sw=1.8))
    f.append(text(480, 430, "5. AP-REQ (ST + Authenticator) ──→ 6. AP-REP", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'kdc-architecture.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Триетапний протокол отримання доступу: 6 повідомлень
# ─────────────────────────────────────────────────────────────────────────────
def fig_three_leg_exchange():
    W, H = 1060, 720
    f = []

    f.append(text(530, 32, "Триетапний обмін повідомленнями Kerberos v5 (6 кроків)", size=15, bold=True))

    # Lifelines
    xc, xas, xtgs, xs = 100, 380, 680, 960
    top, bot = 80, 680

    for x, name, sub in ((xc, "Клієнт", "Alice"), (xas, "KDC / AS", "Автентифікація"),
                         (xtgs, "KDC / TGS", "Видача квитків"), (xs, "Сервер", "Resource")):
        b, _, _ = textbox(x, top, f"{name}\n{sub}", size=11, pad=6, fill=FILL, stroke=LINE, bold=True)
        f.append(b)
        f.append(line(x, top + 26, x, bot, color=MUTED, sw=1.2, dash="4,4"))

    # Stage 1: AS Exchange
    f.append(rect(40, 135, 980, 160, fill="#fbfcfd", stroke="#e0e6ed", sw=1.0, rx=6))
    f.append(text(60, 155, "Етап 1: Первинна автентифікація (отримання TGT)", size=11, color=MUTED, bold=True, anchor="start"))

    f.append(arrow(xc, 185, xas, 185, color=INK))
    f.append(text(240, 175, "1. KRB_AS_REQ: {alice, krbtgt/EXAMPLE.ORG, Nonce_1, PA-ENC-TIMESTAMP_{K_c}}", size=10, color=INK))

    f.append(arrow(xas, 245, xc, 245, color=POS))
    f.append(text(240, 235, "2. KRB_AS_REP: Enc_{K_c}{K_{c,tgs}, Nonce_1, час} + TGT: Enc_{K_{tgs}}{alice, K_{c,tgs}, час}", size=10, color=POS))

    # Stage 2: TGS Exchange
    f.append(rect(40, 315, 980, 160, fill="#fbfcfd", stroke="#e0e6ed", sw=1.0, rx=6))
    f.append(text(60, 335, "Етап 2: Отримання сервісного квитка на конкретну службу", size=11, color=MUTED, bold=True, anchor="start"))

    f.append(arrow(xc, 365, xtgs, 365, color=INK))
    f.append(text(390, 355, "3. KRB_TGS_REQ: {cifs/fs, Nonce_2, TGT, Authenticator: Enc_{K_{c,tgs}}{alice, ctime}}", size=10, color=INK))

    f.append(arrow(xtgs, 425, xc, 425, color=POS))
    f.append(text(390, 415, "4. KRB_TGS_REP: Enc_{K_{c,tgs}}{K_{c,s}, Nonce_2, час} + ST: Enc_{K_s}{alice, K_{c,s}, PAC, час}", size=10, color=POS))

    # Stage 3: AP Exchange
    f.append(rect(40, 495, 980, 160, fill="#fbfcfd", stroke="#e0e6ed", sw=1.0, rx=6))
    f.append(text(60, 515, "Етап 3: Доступ до сервера та взаємна автентифікація", size=11, color=MUTED, bold=True, anchor="start"))

    f.append(arrow(xc, 545, xs, 545, color=FIELD, sw=1.8))
    f.append(text(530, 535, "5. KRB_AP_REQ: {ST: Enc_{K_s}{alice, K_{c,s}, PAC}, Authenticator: Enc_{K_{c,s}}{alice, ctime, [subkey]}}", size=10, color=FIELD))

    f.append(arrow(xs, 605, xc, 605, color=FIELD, sw=1.8))
    f.append(text(530, 595, "6. KRB_AP_REP: Enc_{K_{c,s}}{ctime, [subkey]} (доказ клієнту, що сервер знає K_{c,s})", size=10, color=FIELD))

    render(os.path.join(OUT, 'three-leg-exchange.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Анатомія двох жетонів: Квиток (Ticket) проти Автентифікатора (Authenticator)
# ─────────────────────────────────────────────────────────────────────────────
def fig_ticket_authenticator_anatomy():
    W, H = 1040, 520
    f = []

    f.append(text(520, 32, "Анатомія криптографічних жетонів: Ticket проти Authenticator", size=15, bold=True))

    # Left: Ticket
    f.append(rect(40, 65, 460, 430, fill="#fdfefe", stroke=BORDER_BLUE, sw=1.5, rx=8))
    f.append(rect(40, 65, 460, 42, fill=SOFT_BLUE, stroke=BORDER_BLUE, sw=1.5, rx=8))
    f.append(text(270, 92, "КВИТОК (Ticket / EncTicketPart)", size=13, color=INK, bold=True))

    t_items = [
        ("Зашифровано ключем:", "K_s (ключ служби) або K_{tgs} (для TGT)", POS),
        ("Хто створює:", "Виключно KDC (AS або TGS)", INK),
        ("Час життя:", "Довготривалий (типово 8–10 годин)", INK),
        ("Призначення:", "Багаторазовий пропуск до ресурсу", INK),
        ("Вміст поля EncPart:", "• flags (пересилка, відновлення)\n"
                               "• key (сесійний ключ K_{c,s})\n"
                               "• crealm / cname (ім'я клієнта)\n"
                               "• authtime, starttime, endtime\n"
                               "• caddr (дозволені IP-адреси)\n"
                               "• authorization-data (MS-PAC)", INK)
    ]

    y = 135
    for label, val, col in t_items:
        f.append(text(55, y, label, size=11, color=MUTED, bold=True, anchor="start"))
        if "\n" in val:
            lines = val.split("\n")
            for i, ln in enumerate(lines):
                f.append(text(65, y + 18 + i * 16, ln, size=11, color=col, anchor="start"))
            y += 24 + len(lines) * 16
        else:
            f.append(text(210, y, val, size=11, color=col, bold=True, anchor="start"))
            y += 36

    # Right: Authenticator
    f.append(rect(540, 65, 460, 430, fill="#fdfefe", stroke=BORDER_YELLOW, sw=1.5, rx=8))
    f.append(rect(540, 65, 460, 42, fill=SOFT_YELLOW, stroke=BORDER_YELLOW, sw=1.5, rx=8))
    f.append(text(770, 92, "АВТЕНТИФІКАТОР (Authenticator)", size=13, color=INK, bold=True))

    a_items = [
        ("Зашифровано ключем:", "K_{c,s} (сесійний ключ з квитка)", FIELD),
        ("Хто створює:", "Клієнт (Alice) на кожен запит", INK),
        ("Час життя:", "Одноразовий (вікно валідності ±5 хв)", INK),
        ("Призначення:", "Доказ володіння сесійним ключем", INK),
        ("Вміст повідомлення:", "• authenticator-vno (версія: 5)\n"
                               "• crealm / cname (ім'я клієнта)\n"
                               "• cksum (контрольна сума тіла запиту)\n"
                               "• cusec + ctime (мітка мікросекунд)\n"
                               "• subkey (опційний ключ підвибірки)\n"
                               "• seq-number (початковий номер)", INK)
    ]

    y = 135
    for label, val, col in a_items:
        f.append(text(555, y, label, size=11, color=MUTED, bold=True, anchor="start"))
        if "\n" in val:
            lines = val.split("\n")
            for i, ln in enumerate(lines):
                f.append(text(565, y + 18 + i * 16, ln, size=11, color=col, anchor="start"))
            y += 24 + len(lines) * 16
        else:
            f.append(text(710, y, val, size=11, color=col, bold=True, anchor="start"))
            y += 36

    render(os.path.join(OUT, 'ticket-authenticator-anatomy.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Захист від повтору: часове вікно (Clock Skew) та Replay Cache
# ─────────────────────────────────────────────────────────────────────────────
def fig_replay_cache_skew():
    W, H = 1020, 490
    f = []

    f.append(text(510, 32, "Захист від Replay-атак: часове вікно та кеш автентифікаторів", size=15, bold=True))

    # Window bounds background (above axis)
    f.append(rect(290, 75, 440, 50, fill="#e8f8f5", stroke=BORDER_GREEN, sw=1.5, rx=4))
    f.append(text(510, 105, "Допустиме вікно розсинхронізації (Clock Skew Window: ±5 хв)", size=11, color=FIELD, bold=True))

    # Time axis
    f.append(line(80, 150, 940, 150, color=LINE, sw=2.0))
    f.append(arrow(920, 150, 960, 150, color=LINE, sw=2.0))
    f.append(text(955, 175, "Час (t)", size=12, color=MUTED))

    # Server Time Center
    f.append(line(510, 130, 510, 170, color=POS, sw=2.5))
    f.append(circle(510, 150, 5, fill=POS, stroke=POS))
    f.append(text(510, 185, "Час сервера (T_server)", size=12, color=POS, bold=True))

    # Window boundary ticks on axis
    f.append(line(290, 135, 290, 165, color=FIELD, sw=2.0))
    f.append(line(730, 135, 730, 165, color=FIELD, sw=2.0))

    f.append(text(290, 185, "T_server - 5 хв", size=11, color=FIELD, bold=True))
    f.append(text(730, 185, "T_server + 5 хв", size=11, color=FIELD, bold=True))

    # Rejected zones (positioned well away from axis lines)
    f.append(text(180, 110, "Застарілий запит (Replay)\nВІДХИЛЯЄТЬСЯ\n(KRB_AP_ERR_SKEW)", size=10, color=POS, bold=True))
    f.append(text(840, 110, "Запит «з майбутнього»\nВІДХИЛЯЄТЬСЯ\n(KRB_AP_ERR_SKEW)", size=10, color=POS, bold=True))

    # Replay Cache Decision Process
    f.append(rect(80, 240, 860, 220, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(100, 265, "Алгоритм перевірки автентифікатора у серверному кеші повторів (Replay Cache)", size=12, bold=True, anchor="start"))

    b1, _, _ = textbox(210, 340,
                       "1. Отримано Authenticator\n"
                       "ctime = 14:02:15.123456\n"
                       "cname = alice@REALM",
                       size=11, pad=8, fill=SOFT_BLUE, stroke=BORDER_BLUE)
    f.append(b1)

    f.append(arrow(315, 340, 395, 340, color=INK, sw=1.5))

    b2, _, _ = textbox(510, 340,
                       "2. Пошук запису в кеші:\n"
                       "Хеш (cname, ctime, cusec)\n"
                       "Чи був такий запис?",
                       size=11, pad=8, fill=SOFT_YELLOW, stroke=BORDER_YELLOW)
    f.append(b2)

    f.append(arrow(625, 315, 735, 290, color=POS, sw=1.5))
    f.append(text(680, 290, "ТАК (знайдено)", size=10, color=POS, bold=True))
    b_no, _, _ = textbox(820, 290, "ВІДХИЛИТИ ЗАПИТ!\nKRB_AP_ERR_REPEAT\n(Зафіксовано Replay)", size=10, pad=6, fill=SOFT_RED, stroke=BORDER_RED, bold=True)
    f.append(b_no)

    f.append(arrow(625, 365, 735, 390, color=FIELD, sw=1.5))
    f.append(text(680, 395, "НІ (перший раз)", size=10, color=FIELD, bold=True))
    b_yes, _, _ = textbox(820, 390, "ПРИЙНЯТИ ЗАПИТ\nЗаписати в Replay Cache\nз TTL = 5 хвилин", size=10, pad=6, fill=SOFT_GREEN, stroke=BORDER_GREEN, bold=True)
    f.append(b_yes)

    render(os.path.join(OUT, 'replay-cache-skew.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Інтеграція з Active Directory: структура та підписи MS-PAC
# ─────────────────────────────────────────────────────────────────────────────
def fig_pac_validation_chain():
    W, H = 1040, 540
    f = []

    f.append(text(520, 32, "Структура привілеїв Active Directory: Microsoft PAC та ланцюг підписів", size=15, bold=True))

    # Service Ticket Outer Box
    f.append(rect(40, 65, 960, 450, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(60, 95, "Service Ticket (зашифрований ключем служби K_s)", size=13, bold=True, anchor="start"))
    f.append(text(60, 115, "Містить cname, session_key K_{c,s}, timestamps та розширення Authorization-Data:", size=11, color=MUTED, anchor="start"))

    # MS-PAC Box inside Ticket
    f.append(rect(70, 135, 900, 360, fill="#f9fbfd", stroke=BORDER_BLUE, sw=1.5, rx=6))
    f.append(rect(70, 135, 900, 36, fill=SOFT_BLUE, stroke=BORDER_BLUE, sw=1.5, rx=6))
    f.append(text(520, 160, "MS-PAC (Privilege Attribute Certificate) — структура привілеїв користувача", size=12, bold=True))

    # PAC Components
    # 1. Validation Info
    b_info, _, _ = textbox(300, 260,
                           "KERB_VALIDATION_INFO (Дані авторизації)\n\n"
                           "• User SID (ідентифікатор користувача)\n"
                           "• Primary Group RID (основна група)\n"
                           "• Group SIDs (усі доменні групи, вкл. Domain Admins)\n"
                           "• UserAccountControl (прапорці стану обліковки)\n"
                           "• Resource Group SIDs (локальні групи ресурсів)",
                           size=11, pad=10, fill="#ffffff", stroke=BORDER_BLUE)
    f.append(b_info)

    # 2. Server Signature
    b_ssig, _, _ = textbox(730, 235,
                           "1. Підпис сервера (PAC_SERVER_CHECKSUM)\n\n"
                           "HMAC-SHA1-96 / HMAC-MD5 на ключі служби K_s\n"
                           "Захищає: підтверджує цілісність KERB_VALIDATION_INFO.\n"
                           "Хто перевіряє: Цільовий сервер при обробці AP-REQ.",
                           size=11, pad=10, fill=SOFT_YELLOW, stroke=BORDER_YELLOW)
    f.append(b_ssig)

    # 3. KDC Signature
    b_ksig, _, _ = textbox(730, 380,
                           "2. Підпис KDC (PAC_PRIVSVR_CHECKSUM)\n\n"
                           "HMAC на секретному ключі KDC (K_{tgs} / krbtgt)\n"
                           "Захищає: запобігає підробці привілеїв самим сервером!\n"
                           "Сервер не може підробити собі права адміна.",
                           size=11, pad=10, fill=SOFT_RED, stroke=BORDER_RED)
    f.append(b_ksig)

    # Arrows linking data to signatures
    f.append(arrow(515, 235, 545, 235, color=POS, sw=1.5))
    f.append(arrow(515, 380, 545, 380, color=POS, sw=1.5))

    f.append(text(520, 480, "Сервер перевіряє власний підпис; для перевірки KDC-підпису може виконати RPC-виклик NetrLogonSamLogon до контролера домену", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'pac-validation-chain.svg'), W, H, *f)


def main():
    fig_kdc_architecture()
    fig_three_leg_exchange()
    fig_ticket_authenticator_anatomy()
    fig_replay_cache_skew()
    fig_pac_validation_chain()
    print("Всі фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
