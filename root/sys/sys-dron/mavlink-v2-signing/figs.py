# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми mavlink-v2-signing (MAVLink v2 і підпис повідомлень)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_signing_frame_anatomy():
    """Фігура 1: Анатомія кадру MAVLink v2 із 13-байтовим трейлером підпису."""
    W, H = 840, 460
    p = []

    # Загальний фон
    p.append(rect(15, 15, 810, 430, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Структура кадру MAVLink v2 із криптографічним трейлером підпису", size=13, color=INK, bold=True))

    # Верхній блок: Поля кадру на дроті
    p.append(rect(25, 55, 790, 120, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    p.append(text(420, 74, "Кадр MAVLink v2 на фізичному рівні (максимальний розмір до 280 байтів)", size=11, color=MUTED, bold=True))

    # Поля кадру
    # Header (10 B)
    p.append(rect(35, 90, 38, 55, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(mtext(54, 112, "STX\n0xFD", size=9.5, color=POS, bold=True))

    p.append(rect(76, 90, 38, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(95, 112, "LEN\n0..255", size=9.5, color=INK, bold=True))

    # INCOMPAT FLAGS - highlighted
    p.append(rect(117, 90, 68, 55, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    p.append(mtext(151, 110, "INCOMPAT\n0x01 (SIGN)", size=9.5, color=POS, bold=True))

    p.append(rect(188, 90, 52, 55, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(mtext(214, 112, "COMPAT\nflags", size=9.5, color=MUTED, bold=True))

    p.append(rect(243, 90, 38, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(262, 112, "SEQ\n0..255", size=9.5, color=INK, bold=True))

    p.append(rect(284, 90, 38, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(303, 112, "SYS\nid", size=9.5, color=INK, bold=True))

    p.append(rect(325, 90, 38, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(344, 112, "COMP\nid", size=9.5, color=INK, bold=True))

    p.append(rect(366, 90, 56, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(394, 112, "MSG ID\n24 біти", size=9.5, color=INK, bold=True))

    # PAYLOAD
    p.append(rect(425, 90, 135, 55, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(mtext(492, 112, "PAYLOAD (0..255 B)\nZero-trimmed дані", size=9.5, color=FIELD, bold=True))

    # CRC
    p.append(rect(563, 90, 48, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(587, 112, "CRC\n2 B", size=9.5, color=INK, bold=True))

    # SIGNATURE TRAILER (13 B)
    p.append(rect(614, 90, 192, 55, fill="#eff6ff", stroke=NEG, sw=1.8, rx=4))
    p.append(text(710, 106, "SIGNATURE TRAILER (13 B)", size=10, color=NEG, bold=True))

    # Subfields of trailer
    p.append(rect(618, 116, 42, 24, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(639, 132, "Link 1B", size=9, color=NEG, bold=True))

    p.append(rect(663, 116, 68, 24, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(697, 132, "Time 48-bit", size=9, color=NEG, bold=True))

    p.append(rect(734, 116, 68, 24, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(768, 132, "Sig 48-bit", size=9, color=NEG, bold=True))

    # Нижній блок: Алгоритм обчислення підпису
    p.append(rect(25, 190, 790, 240, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    p.append(text(420, 212, "Схема розрахунку підпису (Prefix SHA-256 з обтинанням до 48 бітів)", size=12, color=INK, bold=True))

    # Вхідний масив для хешування
    p.append(rect(35, 230, 770, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(420, 246, "Вхідний потік байтів для хеш-функції SHA-256 (розмір: 32 + 10 + LEN + 2 + 1 + 6 = 51 + LEN байтів)", size=10, color=MUTED, bold=True))

    p.append(rect(45, 256, 135, 26, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    p.append(text(112, 273, "Secret Key (32 B)", size=9.5, color="#92400e", bold=True))

    p.append(rect(185, 256, 130, 26, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
    p.append(text(250, 273, "Header (10 B кадру)", size=9.5, color=INK))

    p.append(rect(320, 256, 135, 26, fill="#f0fdf4", stroke=FIELD, sw=1.0, rx=3))
    p.append(text(387, 273, "Payload (LEN байтів)", size=9.5, color=FIELD))

    p.append(rect(460, 256, 80, 26, fill="#ffffff", stroke=LINE, sw=1.0, rx=3))
    p.append(text(500, 273, "CRC-16 (2 B)", size=9.5, color=INK))

    p.append(rect(545, 256, 95, 26, fill="#eff6ff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(592, 273, "Link ID (1 B)", size=9.5, color=NEG, bold=True))

    p.append(rect(645, 256, 150, 26, fill="#eff6ff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(720, 273, "Timestamp 48-bit (6 B)", size=9.5, color=NEG, bold=True))

    # Стрілка вниз до SHA-256
    p.append(arrow(420, 292, 420, 324, color=LINE, sw=1.8))
    p.append(text(435, 312, "SHA-256", size=10.5, color=MUTED, anchor="start", bold=True))

    # Блок результату SHA-256
    p.append(rect(140, 326, 560, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(420, 344, "Повний дайджест SHA-256: 32 байти (256 бітів криптографічного хешу)", size=10.5, color=INK, bold=True))

    p.append(rect(155, 350, 160, 18, fill="#eff6ff", stroke=NEG, sw=1.2, rx=2))
    p.append(text(235, 363, "Перші 6 байтів (48 бітів)", size=9.5, color=NEG, bold=True))

    p.append(rect(320, 350, 365, 18, fill="#f4f6f8", stroke=MUTED, sw=0.8, rx=2))
    p.append(text(502, 363, "Решта 26 байтів відкидаються (економія радіоканалу)", size=9, color=MUTED))

    # Стрілка до поля підпису
    p.append(arrow(235, 372, 235, 396, color=NEG, sw=1.8))
    p.append(text(248, 388, "Записується у Signature Hash", size=10, color=NEG, anchor="start", bold=True))

    p.append(rect(35, 398, 770, 24, fill="#eff6ff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(420, 414, "Результат: 13 додаткових байтів у кінці пакета гарантують автентичність і захист від підробок", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "signing-frame-anatomy.svg"), W, H, *p)


def fig_signing_verification_flow():
    """Фігура 2: Послідовність перевірки та валідації підписаного пакета приймачем."""
    W, H = 840, 430
    p = []

    p.append(rect(15, 15, 810, 400, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Конвеєр перевірки вхідного підписаного пакета MAVLink v2", size=13, color=INK, bold=True))

    # Крок 1: Отримання кадру
    p.append(rect(35, 60, 220, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(145, 80, "1. Парсинг кадру v2", size=11, color=INK, bold=True))
    p.append(mtext(145, 98, "Перевірка STX == 0xFD\nАналіз incompat_flags", size=9.5, color=MUTED))

    p.append(arrow(255, 95, 295, 95, color=LINE, sw=1.5))

    # Крок 2: Перевірка прапорця SIGNED
    p.append(rect(295, 60, 250, 70, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(420, 80, "2. incompat_flags & 0x01?", size=11, color=POS, bold=True))
    p.append(mtext(420, 98, "Біт 0x01: пакет підписано\nОчікується 13 байтів трейлера", size=9.5, color=INK))

    p.append(arrow(545, 95, 585, 95, color=LINE, sw=1.5))

    # Крок 3: Перевірка CRC
    p.append(rect(585, 60, 220, 70, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(695, 80, "3. Валідація CRC-16", size=11, color=FIELD, bold=True))
    p.append(mtext(695, 98, "CRC з урахуванням CRC_EXTRA\nНе збіглася -> Drop", size=9.5, color=MUTED))

    # Стрілка вниз до Кроку 4
    p.append(arrow(695, 130, 695, 165, color=LINE, sw=1.5))

    # Крок 4: Пошук потоку за (sysid, compid, link_id)
    p.append(rect(540, 165, 265, 80, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(672, 185, "4. Пошук потоку (Stream Table)", size=11, color=NEG, bold=True))
    p.append(mtext(672, 205, "Ключ: (sysid, compid, link_id)\nОтримання last_timestamp для\nцього конкретного лінку", size=9.5, color=INK))

    p.append(arrow(540, 205, 490, 205, color=LINE, sw=1.5))

    # Крок 5: Перевірка монотонності таймстемпу (Replay Check)
    p.append(rect(220, 165, 270, 80, fill="#fff5f5", stroke=POS, sw=1.8, rx=6))
    p.append(text(355, 185, "5. Перевірка Replay-атаки", size=11, color=POS, bold=True))
    p.append(mtext(355, 205, "incoming_ts > stream.last_ts?\nНі (ts <= last_ts) -> ВІДХИЛИТИ!\nТак -> Перевірка хешу", size=9.5, color=POS, bold=True))

    p.append(arrow(220, 205, 170, 205, color=LINE, sw=1.5))

    # Крок 6: Обчислення SHA-256
    p.append(rect(35, 165, 135, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(102, 185, "6. SHA-256", size=11, color=INK, bold=True))
    p.append(mtext(102, 205, "Хеш(Key + Пакет)\nОбтинання до\nперших 48 бітів", size=9.5, color=MUTED))

    # Стрілка вниз до Кроку 7
    p.append(arrow(102, 245, 102, 280, color=LINE, sw=1.5))

    # Крок 7: Порівняння підпису
    p.append(rect(35, 280, 360, 75, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    p.append(text(215, 302, "7. Порівняння computed_sig == incoming_sig", size=11, color=INK, bold=True))
    p.append(mtext(215, 322, "Постійний час виконання (Constant-time compare)\nЗбіглося -> Валідний автентичний пакет\nРозбіжність -> Відкинути як підробку!", size=9.5, color=MUTED))

    p.append(arrow(395, 317, 450, 317, color=FIELD, sw=1.8))

    # Крок 8: Фіксація стану та доставка
    p.append(rect(450, 280, 355, 75, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(627, 302, "8. Оновлення стану та виконання", size=11, color=FIELD, bold=True))
    p.append(mtext(627, 322, "stream.last_timestamp = incoming_ts\nПередача корисного навантаження в обробник команд\nБезпечне виконання на борту апарата", size=9.5, color=FIELD, bold=True))

    # Підсумок знизу
    p.append(rect(35, 370, 770, 32, fill="#f8fafc", stroke=LINE, sw=1.0, rx=4))
    p.append(text(420, 390, "Жодна підроблена чи повторно надіслана команда не потрапляє в логіку керування польотом", size=10, color=INK, italic=True))

    render(os.path.join(OUT, "signing-verification-flow.svg"), W, H, *p)


def fig_replay_attack_defense():
    """Фігура 3: Механізм відбиття Replay-атаки за допомогою монотонного таймстемпу."""
    W, H = 840, 430
    p = []

    p.append(rect(15, 15, 810, 400, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Відбиття Replay-атаки (повторного відтворення) у MAVLink v2", size=13, color=INK, bold=True))

    # Три колоночні ролі: Легітимна станція (GCS), Ефір / Зловмисник, Бортовий автопілот (FC)
    p.append(rect(35, 55, 210, 40, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(140, 80, "Наземна станція (GCS)", size=11, color=NEG, bold=True))

    p.append(rect(315, 55, 210, 40, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(420, 80, "Зловмисник (Sniffer / MITM)", size=11, color=POS, bold=True))

    p.append(rect(595, 55, 210, 40, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(700, 80, "Автопілот (PX4 / ArduPilot)", size=11, color=FIELD, bold=True))

    # Вертикальні пунктирні сегменти ліній життя (розміщені у проміжках між блоками, щоб не перетинати текст)
    # Станція (x=140)
    p.append(line(140, 95, 140, 115, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(140, 160, 140, 370, color=MUTED, sw=1.2, dash="4,3"))

    # Зловмисник (x=420)
    p.append(line(420, 95, 420, 245, color=POS, sw=1.2, dash="4,3"))
    p.append(line(420, 290, 420, 320, color=POS, sw=1.2, dash="4,3"))
    p.append(line(420, 365, 420, 370, color=POS, sw=1.2, dash="4,3"))

    # Автопілот (x=700)
    p.append(line(700, 95, 700, 125, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(700, 175, 700, 190, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(700, 230, 700, 255, color=MUTED, sw=1.2, dash="4,3"))
    p.append(line(700, 305, 700, 330, color=MUTED, sw=1.2, dash="4,3"))

    # Подія 1: Легітимна відправка в момент t1
    p.append(rect(45, 115, 190, 45, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(mtext(140, 132, "t1: COMMAND_DISARM\nts = 100 000, sig = S1", size=9.5, color=NEG, bold=True))

    p.append(arrow(140, 145, 690, 145, color=NEG, sw=1.5))
    p.append(text(420, 138, "Перехоплення пакету в радіоефірі", size=9.5, color=POS))

    p.append(rect(605, 125, 190, 50, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=3))
    p.append(mtext(700, 145, "ts (100k) > last_ts (0)\nПрийнято! last_ts = 100k", size=9.5, color=FIELD, bold=True))

    # Часовий проміжок (польотні команди продовжуються)
    p.append(rect(605, 190, 190, 40, fill="#ffffff", stroke=MUTED, sw=1.0, rx=3))
    p.append(mtext(700, 208, "Обмін телеметрією польоту\nlast_ts зростає до 500 000", size=9.5, color=MUTED))

    # Подія 2: Спроба повтору старого пакету в момент t2
    p.append(rect(325, 245, 190, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(mtext(420, 262, "t2: REPLAY старого кадру!\nts = 100 000, sig = S1", size=9.5, color=POS, bold=True))

    p.append(arrow(420, 275, 690, 275, color=POS, sw=1.8))

    p.append(rect(605, 255, 190, 50, fill="#fef2f2", stroke=POS, sw=1.8, rx=3))
    p.append(mtext(700, 275, "ts (100k) <= last_ts (500k)\nВІДХИЛЕНО! (Replay drop)", size=9.5, color=POS, bold=True))

    # Подія 3: Спроба підробки таймстемпу без знання ключа
    p.append(rect(325, 320, 190, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(mtext(420, 338, "Спроба: змінити ts на 550k\nsig лишається старим S1", size=9.5, color=POS, bold=True))

    p.append(arrow(420, 350, 690, 350, color=POS, sw=1.8))

    p.append(rect(605, 330, 190, 50, fill="#fef2f2", stroke=POS, sw=1.8, rx=3))
    p.append(mtext(700, 350, "computed_sig != S1\nВІДХИЛЕНО! (Invalid Hash)", size=9.5, color=POS, bold=True))

    # Пояснення знизу
    p.append(rect(35, 385, 770, 22, fill="#f8fafc", stroke=LINE, sw=1.0, rx=3))
    p.append(text(420, 400, "Без знання 256-бітного спільного ключа неможливо оновити ні таймстемп, ні корисні дані кадру", size=9.5, color=INK, bold=True))

    render(os.path.join(OUT, "replay-attack-defense.svg"), W, H, *p)


def fig_multi_link_timestamp():
    """Фігура 4: Розділення потоків за Link ID у багатоканальних системах зв'язку."""
    W, H = 840, 410
    p = []

    p.append(rect(15, 15, 810, 380, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Роль поля Link ID: запобігання хибним блокуванням у мульти-лінк архітектурі", size=13, color=INK, bold=True))

    # Ліва частина: Джерела зв'язку
    p.append(rect(35, 65, 230, 95, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(150, 88, "Лінк 0: Радіомодем (RF)", size=11, color=NEG, bold=True))
    p.append(mtext(150, 110, "Швидкість: 57600 бод\nЗатримка: 30..80 мс\nЧастота: 10 Гц", size=9.5, color=INK))

    p.append(rect(35, 185, 230, 95, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(150, 208, "Лінк 1: Супутній ПК (SBC)", size=11, color=FIELD, bold=True))
    p.append(mtext(150, 230, "Швидкість: 100 Мбіт (Ethernet/UDP)\nЗатримка: < 1 мс\nЧастота: 200 Гц", size=9.5, color=INK))

    # Стрілки до центрального вузла
    p.append(arrow(265, 112, 330, 150, color=NEG, sw=1.8))
    p.append(text(300, 122, "Link 0", size=9.5, color=NEG, bold=True))

    p.append(arrow(265, 232, 330, 190, color=FIELD, sw=1.8))
    p.append(text(300, 222, "Link 1", size=9.5, color=FIELD, bold=True))

    # Центральний вузол: Бортовий автопілот
    p.append(rect(330, 65, 475, 235, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(567, 88, "Бортовий автопілот: Таблиця стану потоків підпису", size=11.5, color=INK, bold=True))

    # Таблиця потоків
    p.append(rect(350, 105, 435, 75, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    p.append(mtext(567, 128, "Слот потоку Link 0 (Радіоканал):\nsysid: 255, compid: 190, link_id: 0\nlast_timestamp: 100 250 (повільний приріст через затримку)", size=9.5, color=NEG, bold=True))

    p.append(rect(350, 195, 435, 75, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(mtext(567, 218, "Слот потоку Link 1 (Ethernet SBC):\nsysid: 1, compid: 191, link_id: 1\nlast_timestamp: 850 400 (стрімкий приріст на 200 Гц)", size=9.5, color=FIELD, bold=True))

    # Нижня частина: Порівняння без Link ID та з Link ID
    p.append(rect(35, 310, 375, 70, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(222, 330, "Без поля Link ID (Спільний таймстемп):", size=10, color=POS, bold=True))
    p.append(mtext(222, 350, "Пакет із SBC оновлює час до 850k;\nПакет із повільного радіо (100k) блокується\nяк хибна 'replay-атака'!", size=9.5, color=INK))

    p.append(rect(430, 310, 375, 70, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(617, 330, "З полем Link ID (Ізольовані потоки):", size=10, color=FIELD, bold=True))
    p.append(mtext(617, 350, "Кожен фізичний канал має власний незалежний\nлічильник монотонного часу;\nОбидва лінки працюють паралельно й захищено.", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "multi-link-timestamp.svg"), W, H, *p)


if __name__ == "__main__":
    fig_signing_frame_anatomy()
    fig_signing_verification_flow()
    fig_replay_attack_defense()
    fig_multi_link_timestamp()
    print("Всі 4 SVG-фігури успішно згенеровано.")
