#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми wpa-security."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/communications/networks/wpa-security)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_wpa_evolution():
    """Діаграма еволюції стандартів захисту Wi-Fi: від WEP до WPA3."""
    w, h = 960, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Еволюція криптографічного захисту бездротових мереж IEEE 802.11", size=16, bold=True))

    # Стовпчики для 4 етапів: WEP, WPA (TKIP), WPA2 (CCMP), WPA3 (SAE/OWE)
    cols = [
        {
            "x": 30, "w": 210, "year": "1997–1999", "title": "WEP", "sub": "Wired Equivalent Privacy",
            "cipher": "RC4 (потоковий)", "iv": "24 біти (статичний/короткий)", "mic": "CRC-32 (лінійний ICV)",
            "auth": "Відкритий ключ / Shared Key", "status": "Зламаний (FMS, PTW)", "color": "#fdecea", "border": POS
        },
        {
            "x": 265, "w": 210, "year": "2003 (тимчасовий)", "title": "WPA", "sub": "Wi-Fi Protected Access",
            "cipher": "TKIP + RC4 (програмний)", "iv": "48 біт (TSC-лічильник)", "mic": "Michael (64 біти)",
            "auth": "PSK / 802.1X (EAP-TLS)", "status": "Застарілий (Beck-Tews)", "color": "#fef9e7", "border": "#f39c12"
        },
        {
            "x": 500, "w": 210, "year": "2004 (802.11i)", "title": "WPA2", "sub": "Robust Security Network",
            "cipher": "AES-CCMP (CTR + CBC-MAC)", "iv": "48 біт (Packet Number)", "mic": "CBC-MAC (64/128 біт)",
            "auth": "4-Way Handshake (PSK/EAP)", "status": "Вразливий до офлайн/KRACK", "color": "#eaf2f8", "border": NEG
        },
        {
            "x": 735, "w": 200, "year": "2018 (802.11az)", "title": "WPA3", "sub": "Dragonfly SAE & OWE",
            "cipher": "AES-CCMP / GCMP-256", "iv": "48 біт (Packet Number)", "mic": "CBC-MAC / GMAC",
            "auth": "SAE (Dragonfly PAKE) + PFS", "status": "Сучасний стандарт безпеки", "color": "#eafaf1", "border": FIELD
        }
    ]

    for col in cols:
        cx = col["x"]
        cw = col["w"]
        # Верхня плашка з роком і назвою
        frags.append(rect(cx, 55, cw, 400, fill=col["color"], stroke=col["border"], sw=1.8, rx=8))
        frags.append(rect(cx, 55, cw, 42, fill=col["border"], stroke=col["border"], sw=1, rx=6))
        frags.append(text(cx + cw / 2, 75, col["title"], size=16, color="#ffffff", bold=True))
        frags.append(text(cx + cw / 2, 91, col["year"], size=11, color="#ffffff"))

        # Підзаголовок
        frags.append(text(cx + cw / 2, 115, col["sub"], size=11, color=col["border"], bold=True))
        frags.append(line(cx + 10, 126, cx + cw - 10, 126, color=LINE, sw=0.8, dash="2,2"))

        # Блоки параметрів
        y_pos = 145
        params = [
            ("Шифрування:", col["cipher"]),
            ("Вектор / IV:", col["iv"]),
            ("Цілісність (MIC):", col["mic"]),
            ("Автентифікація:", col["auth"]),
            ("Статус безпеки:", col["status"])
        ]
        for label, val in params:
            frags.append(text(cx + 12, y_pos, label, size=11, color=MUTED, anchor="start", bold=True))
            frags.append(text(cx + 12, y_pos + 16, val, size=11, color=INK, anchor="start"))
            y_pos += 44

    return render(os.path.join(IMG_DIR, "wpa-evolution-timeline.svg"), w, h, *frags)


def fig_wpa2_handshake():
    """Діаграма чотириетапного рукостискання (4-Way Handshake) WPA2."""
    w, h = 960, 560
    frags = []

    frags.append(text(w / 2, 26, "Чотириетапне рукостискання WPA2-PSK (4-Way Handshake)", size=16, bold=True))

    # Стовпчик Клієнта (Supplicant / STA) та Точки Доступу (Authenticator / AP)
    sta_x = 180
    ap_x = 780

    # Шапки сутностей
    box_sta, _, _ = textbox(sta_x, 70, "Клієнт (STA)\nSupplicant\nMAC: SPA", size=13, pad=8, fill="#eaf2f8", stroke=NEG)
    box_ap, _, _ = textbox(ap_x, 70, "Точка доступу (AP)\nAuthenticator\nMAC: AA", size=13, pad=8, fill="#fef9e7", stroke="#f39c12")
    frags.extend([box_sta, box_ap])

    # Вертикальні часові лінії
    frags.append(line(sta_x, 105, sta_x, 525, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(ap_x, 105, ap_x, 525, color=MUTED, sw=1.5, dash="4,4"))

    # Початковий стан: спільний PMK = PBKDF2(Passphrase, SSID)
    frags.append(rect(w / 2 - 190, 115, 380, 30, fill=FILL, stroke=LINE, sw=1, rx=5))
    frags.append(text(w / 2, 134, "Попередній спільний ключ: PMK = PBKDF2(Пароль, SSID, 4096)", size=11, bold=True))

    # Повідомлення 1: AP -> STA (ANonce)
    m1_y = 175
    frags.append(arrow(ap_x, m1_y, sta_x, m1_y, color=LINE, sw=1.8))
    frags.append(rect(w / 2 - 160, m1_y - 20, 320, 34, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(w / 2, m1_y - 5, "M1: EAPOL-Key [ANonce, Key Replay Ctr = 1]", size=11, bold=True))
    frags.append(text(w / 2, m1_y + 9, "AP генерує псевдовипадкове число ANonce", size=10, color=MUTED))

    # Обчислення на боці STA
    c1_y = 230
    box_calc_sta = fitbox(40, c1_y - 20, 240, 48, "STA генерує SNonce\nPTK = PRF-512(PMK, AA, SPA, ANonce, SNonce)\nPTK = KCK(128) || KEK(128) || TK(128)", size=10, pad=4, fill="#eafaf1", stroke=FIELD)
    frags.append(box_calc_sta)

    # Повідомлення 2: STA -> AP (SNonce + MIC)
    m2_y = 290
    frags.append(arrow(sta_x, m2_y, ap_x, m2_y, color=LINE, sw=1.8))
    frags.append(rect(w / 2 - 180, m2_y - 20, 360, 34, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(w / 2, m2_y - 5, "M2: EAPOL-Key [SNonce, RSN-IE, MIC (через KCK)]", size=11, bold=True, color=POS))
    frags.append(text(w / 2, m2_y + 9, "STA доводить знання PMK; мішень офлайн-атак!", size=10, color=POS))

    # Обчислення на боці AP
    c2_y = 345
    box_calc_ap = fitbox(680, c2_y - 20, 240, 44, "AP обчислює PTK\nПеревіряє EAPOL-MIC через KCK\nГенерує груповий ключ GTK", size=10, pad=4, fill="#eafaf1", stroke=FIELD)
    frags.append(box_calc_ap)

    # Повідомлення 3: AP -> STA (ANonce + MIC + Encrypted GTK + Install Flag)
    m3_y = 405
    frags.append(arrow(ap_x, m3_y, sta_x, m3_y, color=LINE, sw=1.8))
    frags.append(rect(w / 2 - 190, m3_y - 20, 380, 34, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(w / 2, m3_y - 5, "M3: EAPOL-Key [ANonce, MIC, Enc(KEK, GTK), Install=1]", size=11, bold=True))
    frags.append(text(w / 2, m3_y + 9, "Наказ встановити PTK/GTK; вразливий до KRACK повторів", size=10, color=MUTED))

    # Повідомлення 4: STA -> AP (MIC Ack)
    m4_y = 470
    frags.append(arrow(sta_x, m4_y, ap_x, m4_y, color=LINE, sw=1.8))
    frags.append(rect(w / 2 - 160, m4_y - 20, 320, 34, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(w / 2, m4_y - 5, "M4: EAPOL-Key [Key Replay Ctr, MIC]", size=11, bold=True))
    frags.append(text(w / 2, m4_y + 9, "Підтвердження завершення: перехід на CCMP", size=10, color=FIELD))

    # Підсумок захищеного каналу
    frags.append(rect(sta_x + 30, 508, (ap_x - sta_x) - 60, 26, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(w / 2, 525, "Канал встановлено: кадри шифруються AES-CCMP через сеансовий ключ TK", size=11, color=FIELD, bold=True))

    return render(os.path.join(IMG_DIR, "wpa2-4way-handshake.svg"), w, h, *frags)


def fig_ccmp_architecture():
    """Архітектура протоколу CCMP: поєднання AES-CTR та AES-CBC-MAC."""
    w, h = 960, 490
    frags = []

    frags.append(text(w / 2, 26, "Архітектура шифрування та автентифікації кадрів IEEE 802.11i CCMP", size=16, bold=True))

    # Вхідні блоки ліворуч: Заголовок кадру (AAD) та Відкритий текст (Payload)
    frags.append(rect(30, 60, 260, 90, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(160, 82, "Заголовок кадру MAC (AAD)", size=13, bold=True))
    frags.append(text(160, 102, "Адреси A1, A2, A3 + SC + QC", size=11, color=MUTED))
    frags.append(text(160, 122, "Передається відкрито, захищений MIC", size=10, color=POS))

    frags.append(rect(30, 180, 260, 90, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(160, 202, "Корисне навантаження (MSDU / Data)", size=13, bold=True))
    frags.append(text(160, 222, "Мережевий пакет (IPv4/IPv6, TCP/UDP)", size=11, color=MUTED))
    frags.append(text(160, 242, "Потребує шифрування та контролю цілісності", size=10, color=NEG))

    frags.append(rect(30, 300, 260, 90, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(160, 322, "Криптографічний контекст", size=13, bold=True))
    frags.append(text(160, 342, "Сеансовий ключ: TK (128 біт)", size=11, color=INK))
    frags.append(text(160, 362, "Лічильник: PN (Packet Number, 48 біт)", size=11, color=FIELD, bold=True))

    # Центральні процеси: CBC-MAC (зверху) та CTR (знизу)
    # CBC-MAC блок
    frags.append(rect(360, 60, 270, 140, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(495, 84, "Обчислення автентифікації (CBC-MAC)", size=13, bold=True))
    frags.append(text(495, 106, "1. Формування блоку B₀ з Nonce (PN, A2, Pri)", size=10, color=MUTED))
    frags.append(text(495, 126, "2. Ланцюгове шифрування AAD + Payload", size=10, color=MUTED))
    frags.append(text(495, 146, "3. Обчислення залишкового вектору T", size=10, color=MUTED))
    frags.append(text(495, 168, "Результат: 64/128-бітний код MIC", size=11, color=POS, bold=True))

    # Стрілки до CBC-MAC
    frags.append(arrow(290, 105, 360, 105, color=LINE, sw=1.5))
    frags.append(arrow(290, 200, 360, 150, color=LINE, sw=1.5))
    frags.append(arrow(290, 330, 360, 175, color=LINE, sw=1.5))

    # CTR режим блок
    frags.append(rect(360, 240, 270, 150, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(495, 264, "Шифрування даних (CTR Mode)", size=13, bold=True))
    frags.append(text(495, 286, "Блок лічильника: A₀ = Flag || Nonce || i", size=10, color=MUTED))
    frags.append(text(495, 306, "Криптографічна гама: Sᵢ = AES(TK, Aᵢ)", size=11, color=INK))
    frags.append(text(495, 328, "Шифротекст: Cᵢ = Dataᵢ ⊕ Sᵢ", size=11, bold=True))
    frags.append(text(495, 350, "Шифрування MIC: Зашифрований MIC = T ⊕ S₀", size=10, color=POS))

    # Стрілки до CTR
    frags.append(arrow(290, 235, 360, 300, color=LINE, sw=1.5))
    frags.append(arrow(290, 360, 360, 350, color=LINE, sw=1.5))
    frags.append(arrow(495, 200, 495, 240, color=LINE, sw=1.5))

    # Результуючий MPDU праворуч
    frags.append(rect(690, 60, 240, 330, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(810, 86, "Сформований кадр MPDU", size=13, bold=True))

    # Поля сформованого кадру
    frags.append(rect(710, 105, 200, 40, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=4))
    frags.append(text(810, 130, "MAC Header (відкритий)", size=11, bold=True))

    frags.append(rect(710, 155, 200, 45, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(810, 175, "CCMP Header (8 байтів)", size=11, bold=True))
    frags.append(text(810, 192, "PN0..PN5 + Key ID + ExtIV", size=9, color=MUTED))

    frags.append(rect(710, 210, 200, 70, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(810, 235, "Encrypted Data", size=11, bold=True, color=NEG))
    frags.append(text(810, 255, "Зашифровані байти MSDU", size=10, color=MUTED))
    frags.append(text(810, 270, "Режим AES-128-CTR", size=9, color=MUTED))

    frags.append(rect(710, 290, 200, 40, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(810, 310, "MIC (8 байтів)", size=11, bold=True, color=POS))
    frags.append(text(810, 324, "Зашифрований CBC-MAC", size=9, color=MUTED))

    frags.append(rect(710, 340, 200, 35, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(810, 362, "FCS (CRC-32, 4 байти)", size=10, color=MUTED))

    frags.append(arrow(630, 315, 690, 315, color=LINE, sw=1.5))

    # Нижній висновок
    frags.append(text(w / 2, 430, "PN захищає від атак повторного відтворення (Replay Attack): кадр з PN ≤ PN_останній відкидається приймачем", size=11, color=FIELD, bold=True))
    frags.append(text(w / 2, 455, "CBC-MAC гарантує автентичність заголовка й даних, а CTR унеможливлює розкриття корисного навантаження", size=11, color=MUTED))

    return render(os.path.join(IMG_DIR, "ccmp-architecture.svg"), w, h, *frags)


def fig_sae_dragonfly():
    """Діаграма протоколу автентифікації WPA3 SAE (Dragonfly Handshake)."""
    w, h = 960, 540
    frags = []

    frags.append(text(w / 2, 26, "Протокол автентифікації WPA3 SAE (Dragonfly Key Exchange)", size=16, bold=True))

    sta_x = 180
    ap_x = 780

    box_sta, _, _ = textbox(sta_x, 70, "Клієнт (STA)\nПароль: pwd, MAC: STA_MAC", size=12, pad=6, fill="#eaf2f8", stroke=NEG)
    box_ap, _, _ = textbox(ap_x, 70, "Точка доступу (AP)\nПароль: pwd, MAC: AP_MAC", size=12, pad=6, fill="#fef9e7", stroke="#f39c12")
    frags.extend([box_sta, box_ap])

    frags.append(line(sta_x, 105, sta_x, 500, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(ap_x, 105, ap_x, 500, color=MUTED, sw=1.5, dash="4,4"))

    # Фаза 0: Виведення точки PWE
    frags.append(rect(w / 2 - 240, 110, 480, 45, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(w / 2, 128, "Фаза 0: Виведення елемента пароля (PWE) на еліптичній кривій", size=11, bold=True))
    frags.append(text(w / 2, 146, "PWE = HashToCurve(pwd, STA_MAC, AP_MAC)  [Точка кривої NIST P-256]", size=10, color=NEG))

    # Фаза 1: Обмін Commit
    m1_y = 190
    frags.append(rect(40, m1_y - 20, 230, 48, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(155, m1_y - 4, "STA генерує r_A, m_A ∈ [1, q-1]", size=10))
    frags.append(text(155, m1_y + 10, "scalar_A = (r_A + m_A) mod q", size=10, bold=True))
    frags.append(text(155, m1_y + 22, "Element_A = -(m_A · PWE)", size=10, bold=True))

    frags.append(rect(690, m1_y - 20, 230, 48, fill="#eafaf1", stroke=FIELD, sw=1, rx=4))
    frags.append(text(805, m1_y - 4, "AP генерує r_B, m_B ∈ [1, q-1]", size=10))
    frags.append(text(805, m1_y + 10, "scalar_B = (r_B + m_B) mod q", size=10, bold=True))
    frags.append(text(805, m1_y + 22, "Element_B = -(m_B · PWE)", size=10, bold=True))

    c1_y = 265
    frags.append(arrow(sta_x, c1_y - 12, ap_x, c1_y - 12, color=NEG, sw=1.8))
    frags.append(arrow(ap_x, c1_y + 12, sta_x, c1_y + 12, color="#f39c12", sw=1.8))
    frags.append(rect(w / 2 - 170, c1_y - 20, 340, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    frags.append(text(w / 2, c1_y - 4, "SAE Commit: (scalar_A, Element_A) ⇄ (scalar_B, Element_B)", size=11, bold=True))
    frags.append(text(w / 2, c1_y + 12, "Пасивний слухач не може перевірити пароль офлайн!", size=10, color=POS, bold=True))

    # Обчислення спільного секрету K
    k_y = 330
    frags.append(rect(w / 2 - 260, k_y - 22, 520, 46, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(w / 2, k_y - 4, "Взаємне обчислення спільної точки: K = r_A · r_B · PWE", size=12, color=FIELD, bold=True))
    frags.append(text(w / 2, k_y + 14, "STA: K = r_A · (scalar_B · PWE + Element_B)   |   AP: K = r_B · (scalar_A · PWE + Element_A)", size=10, color=INK))

    # Фаза 2: Обмін Confirm
    conf_y = 405
    frags.append(arrow(sta_x, conf_y - 10, ap_x, conf_y - 10, color=NEG, sw=1.5))
    frags.append(arrow(ap_x, conf_y + 10, sta_x, conf_y + 10, color="#f39c12", sw=1.5))
    frags.append(rect(w / 2 - 200, conf_y - 20, 400, 38, fill="#ffffff", stroke=LINE, sw=1, rx=5))
    frags.append(text(w / 2, conf_y - 4, "SAE Confirm: Confirm_A ⇄ Confirm_B", size=11, bold=True))
    frags.append(text(w / 2, conf_y + 10, "Confirm = SHA-256(K_x || send-confirm || scalar || Element)", size=10, color=MUTED))

    # Підсумок
    frags.append(rect(w / 2 - 270, 460, 540, 52, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(w / 2, 480, "PMK = KDF(K_x, 'SAE PMK', ...) ──► Перехід до 4-Way Handshake", size=11, bold=True))
    frags.append(text(w / 2, 500, "Властивість PFS (Perfect Forward Secrecy): компрометація пароля не розкриває старі сесії", size=10, color=FIELD, bold=True))

    return render(os.path.join(IMG_DIR, "sae-dragonfly-exchange.svg"), w, h, *frags)


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower().startswith("utf"):
        pass
    else:
        sys.stdout.reconfigure(encoding="utf-8")
    print("Генерація діаграм для wpa-security...")
    f1 = fig_wpa_evolution()
    print("  + " + os.path.basename(f1))
    f2 = fig_wpa2_handshake()
    print("  + " + os.path.basename(f2))
    f3 = fig_ccmp_architecture()
    print("  + " + os.path.basename(f3))
    f4 = fig_sae_dragonfly()
    print("  + " + os.path.basename(f4))
    print("Успішно згенеровано 4 діаграми.")


if __name__ == "__main__":
    main()
