# -*- coding: utf-8 -*-
"""Фігури до теми «Рух між точками доступу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Хронологія класичного роумінгу (Handover Latency) ─────────────────────
def fig_legacy_roaming_breakdown():
    """Показує послідовність етапів класичного перепідключення між AP
    і часовий розрив передачі даних (150–500 мс)."""
    W, H = 820, 360
    f = [text(W / 2, 28, "Хронологія класичного роумінгу без розширень (Legacy Handover)", size=16, bold=True)]

    # Шкала часу вгорі
    f.append(line(50, 65, 770, 65, color=LINE, sw=1.8))
    f.append(arrow(750, 65, 780, 65, color=LINE, sw=1.8))
    f.append(text(760, 52, "Час (мс)", size=11, bold=True, color=MUTED, anchor="end"))

    # Блоки етапів
    stages = [
        (50, 110, "1. Тригер RSSI", "Сигнал < -75 dBm\nВтрата beacon-кадрів", MUTED, "#f4f6f8"),
        (165, 230, "2. Повне сканування", "Active/Passive скан 36 каналів\nЕфір зайнятий зондуванням\nБлекаут: 150–400 мс", POS, "#fdecea"),
        (400, 100, "3. 802.11 Auth", "Open System Auth\nReq / Resp\n5–15 мс", NEG, "#eef3ff"),
        (505, 110, "4. Reassociation", "Reassoc Req / Resp\nПеререєстрація на AP2\n10–25 мс", NEG, "#eef3ff"),
        (620, 150, "5. 4-Way Handshake", "WPA2/WPA3 генерація PTK\n(EAPOL 1/4..4/4)\n40–120 мс", POS, "#fff3e0"),
    ]

    for sx, bw, title_s, desc_s, border_col, bg_col in stages:
        f.append(rect(sx, 85, bw, 135, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        f.append(text(sx + bw / 2, 108, title_s, size=12, bold=True, color=border_col))
        f.append(mtext(sx + bw / 2, 130, desc_s, size=10.5, color=INK, lh=1.25))

    # Смуга блекауту зв'язку
    f.append(rect(165, 235, 605, 48, fill="#ffebee", stroke=POS, sw=1.5, rx=4))
    f.append(text(467, 255, "ПОВНА ЗУПИНКА ПЕРЕДАЧІ КОРИСНИХ ДАНИХ (БЛЕКАУТ: 200–550 мс)", size=12, bold=True, color=POS))
    f.append(text(467, 272, "Втрата пакетів голосового зв'язку (VoIP), зупинка відеотрансляцій, затримка TCP ACK", size=10, color=MUTED))

    # L2 Gratuitous ARP блок внизу
    f.append(rect(50, 300, 720, 38, fill="#eafaf0", stroke=FIELD, sw=1.3, rx=4))
    f.append(text(410, 324, "Завершення: відправка Gratuitous ARP для негайного оновлення таблиці комутації (CAM) свіча L2", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "legacy-roaming-breakdown.svg"), W, H, *f)


# ── 2. Тріада протоколів 802.11k, 802.11v, 802.11r ─────────────────────────
def fig_kvr_trio_interaction():
    """Спільна робота протоколів оптимізації роумінгу:
    11k дає інформацію про сусідів, 11v скеровує клієнта, 11r прискорює ключ."""
    W, H = 820, 380
    f = [text(W / 2, 28, "Тріада оптимізації безшовного роумінгу: 802.11k / 802.11v / 802.11r", size=16, bold=True)]

    cols = [
        (40, 230, "802.11k (RRM)", "Радіовимірювання", NEG, "#eef3ff",
         "ЗАПИТАННЯ: КУДИ ПЕРЕХОДИТИ?\n\n• AP надсилає Neighbor Report\n• Список BSSID та їхніх каналів\n• Станція сканує 2–3 канали\nзамість усіх 36\n• Час сканування: < 25 мс"),
        (295, 230, "802.11v (BTM)", "Керування BSS-переходом", FIELD, "#eafaf0",
         "ЗАПИТАННЯ: КОЛИ ТА ЧОМУ?\n\n• AP надсилає BSS Transition Req\n• Балансування клієнтів між AP\n• Переведення на 5/6 ГГц смуги\n• Попередження про вимкнення AP\n• Усунення «липких» клієнтів"),
        (550, 230, "802.11r (FT)", "Швидкий перехід (Fast BSS)", POS, "#fdecea",
         "ЗАПИТАННЯ: ЯК БЕЗ ЗАТРИМКИ?\n\n• Дворівнева ієрархія ключів\n• PMK-R0 (домен) → PMK-R1 (AP)\n• Без повного 4-Way Handshake\n• Over-the-Air або Over-the-DS\n• Затримка хендоверу: < 30 мс")
    ]

    for x, w, title_s, sub_s, col, bg_col, body_txt in cols:
        f.append(rect(x, 55, w, 235, fill=bg_col, stroke=col, sw=1.6, rx=8))
        f.append(text(x + w / 2, 78, title_s, size=13, bold=True, color=col))
        f.append(text(x + w / 2, 95, sub_s, size=11, color=MUTED))
        f.append(line(x + 15, 105, x + w - 15, 105, color=col, sw=1, dash="3 3"))
        f.append(mtext(x + 20, 122, body_txt, size=10.5, color=INK, anchor="start", lh=1.3))

    # Спільний підсумок унизу
    f.append(rect(40, 305, 740, 52, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=6))
    f.append(text(410, 326, "Спільний ефект: 11k знаходить кандидата + 11v вчасно надсилає команду + 11r перемикає ключ", size=11.5, bold=True, color=INK))
    f.append(text(410, 344, "Сумарна затримка падає з 400 мс до < 30 мс — непомітно для людського слуху в реальному часі", size=10.5, color=FIELD))

    render(os.path.join(IMG, "kvr-trio-interaction.svg"), W, H, *f)


# ── 3. Ієрархія ключів 802.11r (Fast BSS Transition) ─────────────────────────
def fig_ft_key_hierarchy():
    """Дворівневе дерево ключів FT: MSK -> PMK-R0 -> PMK-R1 -> PTK."""
    W, H = 800, 420
    f = [text(W / 2, 28, "Ієрархія ключів 802.11r (FT Key Hierarchy)", size=16, bold=True)]

    # Рівень 0: Початкова автентифікація
    f.append(rect(W / 2 - 170, 55, 340, 55, fill="#eef3ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(W / 2, 76, "MSK (Master Session Key) / PMK", size=12.5, bold=True, color=NEG))
    f.append(text(W / 2, 95, "Отримується при первинному вході (WPA2/WPA3-Enterprise або PSK)", size=10, color=MUTED))

    # Стрілка вниз до PMK-R0
    f.append(arrow(W / 2, 110, W / 2, 135, color=NEG, sw=1.6))

    # Рівень 1: PMK-R0 (Mobility Domain)
    f.append(rect(W / 2 - 200, 135, 400, 60, fill="#fff7e6", stroke=POS, sw=1.6, rx=6))
    f.append(text(W / 2, 156, "PMK-R0 (First-level Key)", size=13, bold=True, color=POS))
    f.append(text(W / 2, 173, "PMK-R0 = KDF(PMK, SSID, MDID, R0KH-ID, STA-MAC)", size=10, color=INK))
    f.append(text(W / 2, 187, "Зберігається на ключовому контролері R0KH у домені мобільності MDID", size=9.5, color=MUTED))

    # Розгалуження до AP1 та AP2 (PMK-R1)
    f.append(line(W / 2, 195, W / 2, 215, color=POS, sw=1.5))
    f.append(line(210, 215, 590, 215, color=POS, sw=1.5))
    f.append(arrow(210, 215, 210, 240, color=POS, sw=1.5))
    f.append(arrow(590, 215, 590, 240, color=POS, sw=1.5))

    # Блоки PMK-R1 для двох AP
    f.append(rect(60, 240, 300, 65, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(210, 261, "PMK-R1 (для Точки Доступу 1)", size=11.5, bold=True, color=FIELD))
    f.append(text(210, 278, "PMK-R1 = KDF(PMK-R0, R1KH-ID_AP1, STA-MAC)", size=9.5, color=INK))
    f.append(text(210, 293, "R1KH-ID = BSSID_AP1 (зберігається локально на AP1)", size=9, color=MUTED))

    f.append(rect(440, 240, 300, 65, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(590, 261, "PMK-R1 (для Точки Доступу 2)", size=11.5, bold=True, color=FIELD))
    f.append(text(590, 278, "PMK-R1 = KDF(PMK-R0, R1KH-ID_AP2, STA-MAC)", size=9.5, color=INK))
    f.append(text(590, 293, "R1KH-ID = BSSID_AP2 (зберігається локально на AP2)", size=9, color=MUTED))

    # Стрілки вниз до PTK
    f.append(arrow(210, 305, 210, 330, color=FIELD, sw=1.5))
    f.append(arrow(590, 305, 590, 330, color=FIELD, sw=1.5))

    # Блоки PTK
    f.append(rect(75, 330, 270, 55, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=6))
    f.append(text(210, 350, "PTK (Сесійний ключ AP1 ↔ STA)", size=11, bold=True, color=INK))
    f.append(text(210, 367, "KDF(PMK-R1, SNonce, ANonce, MACs)", size=9.5, color=MUTED))

    f.append(rect(455, 330, 270, 55, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=6))
    f.append(text(590, 350, "PTK (Сесійний ключ AP2 ↔ STA)", size=11, bold=True, color=INK))
    f.append(text(590, 367, "Миттєвий розрахунок під час 2 кадрів FT Reassoc!", size=9.5, bold=True, color=POS))

    f.append(text(W / 2, 408, "Клієнт і нова AP самостійно обчислюють однаковий PTK без виклику RADIUS-сервера", size=10.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "ft-key-hierarchy.svg"), W, H, *f)


# ── 4. Over-the-Air проти Over-the-DS у 802.11r ──────────────────────────────
def fig_ft_air_vs_ds():
    """Порівняння двох методів виконання Fast BSS Transition:
    через прямий ефір нової AP чи через тунелювання по дротовому DS."""
    W, H = 820, 380
    f = [text(W / 2, 28, "Два режими Fast Transition: Over-the-Air проти Over-the-DS", size=16, bold=True)]

    # Ліва колонка: Over-the-Air
    f.append(rect(40, 55, 350, 295, fill="#fbfcff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(215, 78, "FT Over-the-Air (Прямий ефір)", size=13, bold=True, color=NEG))
    f.append(text(215, 96, "Клієнт перемикає радіо на канал Target AP", size=10, color=MUTED))

    # Схема кроків Over-the-Air
    ota_steps = [
        ("1. STA залишає Current AP", "Перемикання синтезатора на цільовий канал", NEG),
        ("2. FT Auth Request → Target AP", "Передача SNonce та MDIE напряму по радіо", INK),
        ("3. FT Auth Response ← Target AP", "Target AP надсилає ANonce та підтвердження", INK),
        ("4. FT Reassociation Req / Resp", "Фінальне узгодження PTK та шифрування каналу", FIELD),
    ]
    for i, (st_t, st_d, st_c) in enumerate(ota_steps):
        sy = 115 + i * 52
        f.append(rect(55, sy, 320, 44, fill="#ffffff", stroke=st_c, sw=1.1, rx=4))
        f.append(text(215, sy + 17, st_t, size=10.5, bold=True, color=st_c))
        f.append(text(215, sy + 33, st_d, size=9.5, color=MUTED))

    # Права колонка: Over-the-DS
    f.append(rect(430, 55, 350, 295, fill="#fdfbf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(605, 78, "FT Over-the-DS (Через мережу DS)", size=13, bold=True, color=POS))
    f.append(text(605, 96, "Попереднє узгодження через робочий лінк", size=10, color=MUTED))

    # Схема кроків Over-the-DS
    ods_steps = [
        ("1. FT Action Request → Current AP", "STA залишається на старому радіоканалі", INK),
        ("2. Тунелювання через дріт (DS)", "Current AP пересилає запит до Target AP по LAN", POS),
        ("3. FT Action Response ← Current AP", "Відповідь Target AP повертається через старий лінк", INK),
        ("4. Миттєвий перехід на новий канал", "Лише 1 пара кадрів: FT Reassociation Req/Resp", FIELD),
    ]
    for i, (st_t, st_d, st_c) in enumerate(ods_steps):
        sy = 115 + i * 52
        f.append(rect(445, sy, 320, 44, fill="#ffffff", stroke=st_c, sw=1.1, rx=4))
        f.append(text(605, sy + 17, st_t, size=10.5, bold=True, color=st_c))
        f.append(text(605, sy + 33, st_d, size=9.5, color=MUTED))

    f.append(text(W / 2, 368, "Over-the-DS усуває паузу на радіосканування: передача даних не переривається до моменту реасоціації", size=10.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "ft-air-vs-ds.svg"), W, H, *f)


# ── 5. Скінченний автомат роумінгу на SoC (ESP32) ───────────────────────────
def fig_embedded_roaming_fsm():
    """Скінченний автомат клієнтського роумінгу для вбудованих мікроконтролерів."""
    W, H = 820, 400
    f = [text(W / 2, 28, "Скінченний автомат клієнтського роумінгу (Embedded Wi-Fi SoC)", size=16, bold=True)]

    # Стан 1: Підключено (Моніторинг)
    f.append(rect(50, 75, 210, 80, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(155, 98, "1. CONNECTED", size=12.5, bold=True, color=FIELD))
    f.append(mtext(155, 118, "Фільтрація RSSI (EWMA)\nМоніторинг Beacon Loss", size=10, color=INK))

    # Стрілка 1 -> 2
    f.append(arrow(260, 115, 310, 115, color=LINE, sw=1.5))
    f.append(text(285, 103, "RSSI < -75", size=9.5, bold=True, color=POS))

    # Стан 2: Прицільне сканування
    f.append(rect(310, 75, 210, 80, fill="#eef3ff", stroke=NEG, sw=1.6, rx=8))
    f.append(text(415, 98, "2. TARGETED_SCAN", size=12.5, bold=True, color=NEG))
    f.append(mtext(415, 118, "Скан каналів 802.11k\nабо фоновий скан", size=10, color=INK))

    # Стрілка 2 -> 3
    f.append(arrow(520, 115, 570, 115, color=LINE, sw=1.5))
    f.append(text(545, 103, "Знайдено", size=9.5, bold=True, color=MUTED))

    # Стан 3: Оцінка кандидатів (Гістерезис)
    f.append(rect(570, 75, 200, 80, fill="#fff7e6", stroke=POS, sw=1.6, rx=8))
    f.append(text(670, 98, "3. EVALUATE", size=12.5, bold=True, color=POS))
    f.append(mtext(670, 118, "Перевірка умови:\nRSSI_кандидат > RSSI_пот + Δ", size=9.5, color=INK))

    # Стрілка 3 -> 4 (Вниз)
    f.append(arrow(670, 155, 670, 235, color=LINE, sw=1.5))
    f.append(text(725, 195, "Δ > 6 dBm", size=10, bold=True, color=FIELD))

    # Зворотна петля 3 -> 1 зверху (Назад, якщо кандидат не кращий)
    f.append(line(670, 75, 670, 48, color=MUTED, sw=1.2, dash="3 3"))
    f.append(line(670, 48, 155, 48, color=MUTED, sw=1.2, dash="3 3"))
    f.append(arrow(155, 48, 155, 75, color=MUTED, sw=1.2))
    f.append(text(415, 42, "Δ ≤ 6 dBm (залишаємося на старій AP, усунення пінг-понгу)", size=9.5, color=MUTED))

    # Стан 4: Виконання Хендоверу
    f.append(rect(570, 235, 200, 80, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(670, 258, "4. HANDOVER (FT/Reassoc)", size=12, bold=True, color=POS))
    f.append(mtext(670, 278, "802.11r швидкий перехід\nабо Fast Reassociation", size=9.5, color=INK))

    # Стан 5: Оновлення L2 та Відновлення
    f.append(rect(310, 235, 210, 80, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(415, 258, "5. POST_HANDOVER", size=12.5, bold=True, color=FIELD))
    f.append(mtext(415, 278, "Відправка Gratuitous ARP\nПеревірка IP / DHCP", size=10, color=INK))

    # Стрілка 4 -> 5
    f.append(arrow(570, 275, 520, 275, color=FIELD, sw=1.5))
    f.append(text(545, 263, "Успіх", size=9.5, bold=True, color=FIELD))

    # Лінія 5 -> 1 (Огинає зліва між боксами)
    f.append(line(310, 275, 280, 275, color=FIELD, sw=1.5))
    f.append(line(280, 275, 280, 195, color=FIELD, sw=1.5))
    f.append(line(280, 195, 155, 195, color=FIELD, sw=1.5))
    f.append(arrow(155, 195, 155, 155, color=FIELD, sw=1.5))
    f.append(text(215, 185, "Канал активний", size=9.5, bold=True, color=FIELD))

    # Аварійний стан при втраті зв'язку
    f.append(rect(50, 235, 210, 80, fill="#ffebee", stroke=POS, sw=1.4, rx=8))
    f.append(text(155, 258, "DISCONNECTED (Fail)", size=11.5, bold=True, color=POS))
    f.append(mtext(155, 278, "Beacon Timeout\nПовний скан усіх каналів", size=9.5, color=MUTED))

    # Стрілка 1 -> Fail
    f.append(arrow(85, 155, 85, 235, color=POS, sw=1.3))
    f.append(text(60, 195, "Втрата AP", size=9.5, color=POS))

    f.append(text(W / 2, 385, "Гістерезис за рівнем сигналу (ΔRSSI) та таймер затримки запобігають нескінченним перемиканням між точками", size=10.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "embedded-roaming-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_legacy_roaming_breakdown()
    fig_kvr_trio_interaction()
    fig_ft_key_hierarchy()
    fig_ft_air_vs_ds()
    fig_embedded_roaming_fsm()
    print("Всі фігури згенеровано успішно.")
