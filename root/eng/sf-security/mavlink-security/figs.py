# -*- coding: utf-8 -*-
"""Фігури до теми «Безпека MAVLink»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
PAPER = "#ffffff"
CARD_BG = "#f8fafc"


def box(cx, cy, s, size=13, fill=FILL, bold=False, stroke=LINE):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold, stroke=stroke)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Модель загроз для каналу зв'язку БПЛА
# ─────────────────────────────────────────────────────────────────────────────
def fig_threat_landscape():
    W, H = 1200, 720
    f = []

    # Заголовок
    f.append(text(600, 40, "Модель загроз для відкритого каналу телеметрії та керування БПЛА",
                  size=16, bold=True))

    # Легітимні вузли
    gcs, gw, gh = box(180, 140, "Наземна станція керування (GCS)\nОператор / QGroundControl / Mission Planner\nSysID: 255, CompID: 190",
                      size=12, fill=SOFT, stroke="#9bb5db", bold=True)
    uav, uw, uh = box(1020, 140, "Бортовий автопілот (UAV)\nПольотний контролер / PX4 / ArduPilot\nSysID: 1, CompID: 1",
                      size=12, fill=SOFT, stroke="#9bb5db", bold=True)
    f += [gcs, uav]

    # Легітимний радіоканал
    f.append(line(180 + gw + 10, 140, 1020 - uw - 10, 140, color=FIELD, sw=2.5))
    f.append(text(600, 120, "Відкритий радіоефір (UART / 433/915 МГц / Wi-Fi / UDP)",
                  size=12, color=FIELD, bold=True))

    # Зловмисник
    att, aw, ah = box(600, 310, "Зловмисник у зоні дії радіоефіру\nSDR-трансивер / Спрямована антена / Потужний передавач",
                      size=13, fill=WARM, stroke=POS, bold=True)
    f.append(att)

    # Загрози
    threats = [
        (180, 480, "1. Підробка команд (Spoofing)",
         "Ін'єкція кадру COMMAND_LONG:\n"
         "наказ DISARM, зміна польотного\n"
         "режиму на ручний, скидання корисного\n"
         "навантаження без відома оператора.\n"
         "Захист: підпис MAVLink 2."),
        (460, 480, "2. Атака повтору (Replay)",
         "Запис легітимного кадру в ефірі\n"
         "й повторна трансляція у критичний\n"
         "момент місії (наприклад, посадка).\n"
         "CRC збігається, seq переповнюється.\n"
         "Захист: 48-бітний Timestamp."),
        (740, 480, "3. Перехоплення (Eavesdropping)",
         "Пасивне слухання координат дрона\n"
         "(GLOBAL_POSITION_INT), точок місії,\n"
         "пеленгація позиції оператора.\n"
         "Підпис це НЕ закриває!\n"
         "Захист: тунельне шифрування."),
        (1020, 480, "4. Підміна місії / параметрів",
         "Модифікація польотного завдання\n"
         "(MISSION_ITEM_INT) або порогів\n"
         "аварійних режимів (PARAM_SET).\n"
         "Перенаправлення в чужу зону.\n"
         "Захист: перевірка HMAC + CRC_EXTRA."),
    ]

    f.append(arrow(600, 310 - ah - 5, 600, 145, color=POS, sw=2))

    for x, y, title, desc in threats:
        tb, tw, th = box(x, y - 45, title, size=12, fill=WARM, stroke=POS, bold=True)
        db, dw, dh = box(x, y + 55, desc, size=11, fill=PAPER, stroke="#cbd5e1")
        f += [tb, db]
        f.append(arrow(600, 310 + ah + 5, x, y - 45 - th - 5, color=MUTED, sw=1.2))

    # Нижній висновок
    res, _, _ = box(600, 675,
                    "MAVLink 2 Signing гарантує цілісність та автентичність, відбиваючи підробку й повтор.\n"
                    "Конфіденційність ефіру досягається накладанням канального або тунельного шифрування (WireGuard / AES-GCM).",
                    size=12, fill=CARD_BG, stroke="#94a3b8")
    f.append(res)

    render(os.path.join(OUT, 'threat-landscape.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Анатомія кадру MAVLink 2 з підписом
# ─────────────────────────────────────────────────────────────────────────────
def fig_signing_frame():
    W, H = 1200, 780
    f = []

    f.append(text(600, 35, "Структура кадру MAVLink 2 з 13-байтним трейлером криптографічного підпису",
                  size=16, bold=True))

    # Схема кадру
    # 1. Header (10B), 2. Payload (0..255B), 3. Checksum (2B), 4. Signature Trailer (13B)
    f.append(rect(40, 70, 1120, 110, fill=PAPER, stroke="#cbd5e1", sw=1.5, rx=8))

    # Блоки кадру
    b_hdr, _, _ = box(190, 115, "Заголовок MAVLink 2 (10 байтів)\nSTX(0xFD) · LEN · Incompat(0x01) · Compat\nSeq · SysID · CompID · MsgID(3B)",
                      size=11, fill=SOFT, stroke="#9bb5db", bold=True)
    b_pay, _, _ = box(520, 115, "Корисне навантаження Payload\n(LEN байтів, 0..255)\nДані повідомлення після Zero-Trimming",
                      size=11, fill=SOFT, stroke="#9bb5db", bold=True)
    b_crc, _, _ = box(790, 115, "Контрольна сума CRC-16\n(2 байти, Little-Endian)\nCRC-16/MCRF4XX + CRC_EXTRA",
                      size=11, fill=WARM, stroke="#e6d3b3", bold=True)
    b_sig, _, _ = box(1010, 115, "Трейлер підпису (13 байтів)\nLink ID (1B) · Timestamp (6B)\nSignature Hash (6B)",
                      size=11, fill="#fbeae8", stroke=POS, bold=True)
    f += [b_hdr, b_pay, b_crc, b_sig]

    # Розгортання 13-байтового трейлера
    f.append(text(600, 220, "Деталізація 13-байтового трейлера підпису (Signature Trailer):",
                  size=14, bold=True))

    t_link, _, _ = box(230, 280, "Поле 1: Link ID (1 байт)\nЗначення: 0 .. 255\nІдентифікатор фізичного каналу\n(UART1, UART2, UDP, SPI)",
                       size=11, fill=PAPER, stroke="#94a3b8")
    t_time, _, _ = box(600, 280, "Поле 2: Timestamp (6 байтів / 48 бітів LE)\nЧас у одиницях по 10 мкс від 00:00:00 UTC 01.01.2015\nСтрого монотонний лічильник (діапазон 89.2 року, до 2104 р.)\nЗахист від атак повторного відтворення (Replay Protection)",
                       size=11, fill=PAPER, stroke="#94a3b8")
    t_hash, _, _ = box(1010, 280, "Поле 3: Signature (6 байтів / 48 бітів)\nПерші 6 байтів дайджесту SHA-256\nКриптографічний доказ володіння ключем\nЙмовірність підбору: 1 / 2⁴⁸ ≈ 3.55 × 10⁻¹⁵",
                       size=11, fill="#fbeae8", stroke=POS)
    f += [t_link, t_time, t_hash]

    # Алгоритм обчислення SHA-256
    f.append(text(600, 375, "Формування вхідного масиву для розрахунку префіксного гешу SHA-256:",
                  size=14, bold=True))

    in_data, _, _ = box(600, 445,
                        "Вхідні дані для SHA-256 = [ Спільний секретний ключ (32 байти) ]\n"
                        "                         + [ Заголовок MAVLink 2 (10 байтів) ]\n"
                        "                         + [ Корисне навантаження Payload (LEN байтів) ]\n"
                        "                         + [ Контрольна сума CRC-16 (2 байти) ]\n"
                        "                         + [ Link ID (1 байт) ] + [ Timestamp (6 байтів) ]",
                        size=11, fill=WARM, stroke="#e6d3b3", bold=True)
    f.append(in_data)

    f.append(arrow(600, 485, 600, 520, color=MUTED, sw=2))

    sha_blk, _, _ = box(600, 560,
                        "Обчислення повнорозмірного SHA-256 (32 байти / 256 бітів)\n"
                        "digest = SHA256( Key || Header || Payload || CRC16 || Link_ID || Timestamp )",
                        size=12, fill=SOFT, stroke="#9bb5db", bold=True)
    f.append(sha_blk)

    f.append(arrow(600, 600, 600, 635, color=MUTED, sw=2))

    trunc, _, _ = box(600, 680,
                      "Обрізання дайджесту: беруться рівно перші 6 байтів (байти 0..5)\n"
                      "signature = digest[0..5]  →  записуються у байти 7..12 трейлера підпису.\n"
                      "Решта 26 байтів відкидаються для мінімізації накладних витрат у радіоефірі.",
                      size=11, fill=CARD_BG, stroke=FIELD)
    f.append(trunc)

    render(os.path.join(OUT, 'mavlink-signing-frame.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Конвеєр перевірки та логіка захисту від Replay-атак
# ─────────────────────────────────────────────────────────────────────────────
def fig_replay_protection():
    W, H = 1200, 740
    f = []

    f.append(text(600, 35, "Конвеєр приймача: поетапна валідація кадру та відбиття Replay-атак",
                  size=16, bold=True))

    steps = [
        (150, 110, "1. Прийом і кадрування",
         "Перевірка STX == 0xFD.\n"
         "Якщо incompat_flags & 0x01 == 1,\n"
         "кадр має 13-байтний трейлер.\n"
         "Розмір = 10 + LEN + 2 + 13 B."),
        (450, 110, "2. Перевірка CRC-16",
         "Розрахунок контрольної суми\n"
         "CRC-16/MCRF4XX з CRC_EXTRA.\n"
         "Якщо CRC хибна — відкинути!\n"
         "(Економія ресурсів процесора)."),
        (750, 110, "3. Пошук у таблиці потоків",
         "Витягнення триплету:\n"
         "(sysid, compid, link_id).\n"
         "Пошук відповідного потоку в\n"
         "mavlink_signing_streams_t."),
        (1050, 110, "4. Перевірка Timestamp",
         "Умова монотонності:\n"
         "incoming_ts > stream.last_ts\n"
         "Якщо incoming_ts <= last_ts —\n"
         "ВІДХИЛИТИ! (Replay-атака)."),
    ]

    for x, y, title, desc in steps:
        tb, _, _ = box(x, y, title, size=12, fill=SOFT, stroke="#9bb5db", bold=True)
        db, _, _ = box(x, y + 80, desc, size=11, fill=PAPER, stroke="#cbd5e1")
        f += [tb, db]
        if x < 1050:
            f.append(arrow(x + 115, y + 40, x + 185, y + 40, color=MUTED, sw=1.5))

    # Нижні етапи: перевірка криптографії та результат
    f.append(arrow(1050, 240, 1050, 290, color=MUTED, sw=2))

    v_hash, _, _ = box(800, 360,
                       "5. Розрахунок та звірка SHA-256 за сталий час\n"
                       "Обчислення digest = SHA256( Key || Packet_Bytes || link_id || timestamp )\n"
                       "Порівняння digest[0..5] із полем signature через constant-time memcmp().\n"
                       "Якщо байти не збіглися — ВІДХИЛИТИ! (Спроба підробки або чужий ключ).",
                       size=11, fill=WARM, stroke="#e6d3b3", bold=True)
    f.append(v_hash)
    f.append(arrow(1050, 290, 800 + 260, 360, color=MUTED, sw=1.5))

    f.append(arrow(800, 420, 800, 470, color=FIELD, sw=2))

    v_ok, _, _ = box(800, 530,
                     "6. Успішна валідація та фіксація стану\n"
                     "• Оновлення таймстемпу потоку: stream.last_timestamp = incoming_timestamp\n"
                     "• Передача корисного навантаження в диспетчер команд або модуль навігації\n"
                     "• Кадр визнано повністю легітимним та автентичним.",
                     size=11, fill=SOFT, stroke=FIELD, bold=True)
    f.append(v_ok)

    # Приклад колізії без Link ID
    col_box, _, _ = box(280, 450,
                        "Чому необхідне поле Link ID:\n\n"
                        "• Канал 0 (Радіомодем): затримка 50 мс, частота 10 Гц, TS = 120 000\n"
                        "• Канал 1 (Бортовий UDP): затримка 1 мс, частота 200 Гц, TS = 450 000\n\n"
                        "Без Link ID пакети з повільного радіоканалу мали б менший TS\n"
                        "і помилково відкидалися б автопілотом як replay-атака!\n"
                        "Окремий облік часу на кожен Link ID ізолює канали.",
                        size=11, fill=PAPER, stroke="#94a3b8")
    f.append(col_box)

    # Підсумок внизу
    ft, _, _ = box(600, 680,
                   "Перевірка часу відсікає replay-атаки ще до гешування, а постійний час звірки усуває витоки через таймінги.",
                   size=12, fill=CARD_BG, stroke="#94a3b8")
    f.append(ft)

    render(os.path.join(OUT, 'replay-protection-logic.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Багаторівневий захист: ешелонування безпеки каналу (Defense-in-Depth)
# ─────────────────────────────────────────────────────────────────────────────
def fig_defense_layers():
    W, H = 1200, 720
    f = []

    f.append(text(600, 35, "Багаторівнева архітектура захисту безпілотних систем зв'язку",
                  size=16, bold=True))

    layers = [
        (600, 130, "Рівень 3: Політики додатків та фільтрація трафіку (Application Layer)",
         "• Вибіркова фільтрація mavlink_accept_unsigned_t: відкрита телеметрія проти суворих команд.\n"
         "• Захист критичних команд: заборона непідписаних PARAM_SET, COMMAND_LONG, MISSION_ITEM_INT.\n"
         "• Безпечне зберігання ключів: крипточіпи ATECC608A, FRAM, блокування логування ключів (MAV_CMD_LOGGING_STOP).",
         SOFT, "#9bb5db"),
        (600, 310, "Рівень 2: Наскрізна автентичність повідомлень (End-to-End MAVLink Signing)",
         "• 13-байтний трейлер підпису MAVLink 2 (Link ID + 48-бітний Timestamp + 48-бітний SHA-256 MAC).\n"
         "• Наскрізний захист крізь проміжні ретранслятори, шлюзи та роутери (mavlink-router, mavproxy).\n"
         "• Гарантія цілісності й автентичності кожного пакета навіть у несегментованій або відкритій мережі.",
         WARM, "#e6d3b3"),
        (600, 490, "Рівень 1: Канальне та тунельне шифрування (Link / Transport Layer Encryption)",
         "• Захист конфіденційності всього радіоефіру: унеможливлення перехоплення координат та відео.\n"
         "• Апаратне шифрування радіомодемів: AES-128/256-CCM / AES-GCM (RFD900x, Microhard, Silvus, Doodle Labs).\n"
         "• Мережеві тунелі для IP-модемів: WireGuard / IPsec (ESP-GCM) / тунелювання повідомлень MAVLINK_MSG_ID_TUNNEL.",
         "#fbeae8", POS),
    ]

    for cx, cy, title, body, fill, stroke in layers:
        tb, _, th = box(cx, cy - 35, title, size=13, fill=fill, stroke=stroke, bold=True)
        bb, _, bh = box(cx, cy + 35, body, size=11, fill=PAPER, stroke="#cbd5e1")
        f += [tb, bb]

    f.append(arrow(600, 410, 600, 380, color=MUTED, sw=2))
    f.append(arrow(600, 230, 600, 200, color=MUTED, sw=2))

    summary, _, _ = box(600, 660,
                        "Поєднання канального шифрування (конфіденційність ефіру) та двійкового підпису MAVLink (наскрізна автентичність)\n"
                        "створює стійку ешелоновану систему: компрометація одного рівня не призводить до втрати контролю над дроном.",
                        size=12, fill=CARD_BG, stroke=FIELD)
    f.append(summary)

    render(os.path.join(OUT, 'defense-in-depth-layers.svg'), W, H, *f)


if __name__ == '__main__':
    fig_threat_landscape()
    fig_signing_frame()
    fig_replay_protection()
    fig_defense_layers()
    print("ok")
