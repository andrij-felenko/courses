# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми Remote ID (ASTM F3411 / Open Drone ID)."""

import os
import sys

# Шлях до спільних помічників svgkit у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_architecture():
    """Архітектура прямої цифрової ідентифікації Remote ID."""
    w, h = 960, 480
    frags = []

    # Заголовок блоків-джерел (БПЛА та Пілот)
    b_drone = fitbox(40, 60, 240, 160, "Безпілотне повітряне судно (БПС)\n- Бортовий GNSS-приймач\n- Політний контролер (FC)\n- Модуль Direct Remote ID\n- ANSI/CTA-2063-A Серійний №", size=13, fill="#edf2f7", stroke="#2b6cb0", bold=True)
    b_gcs = fitbox(40, 270, 240, 150, "Пульт керування (GCS / Pilot)\n- Координати оператора (WGS84)\n- Номер реєстрації EASA/FAA\n- Висота точки зльоту (Home)\n- Телеметричний канал зв'язку", size=13, fill="#edf2f7", stroke="#2b6cb0", bold=True)

    frags.extend([b_drone, b_gcs])

    # Зв'язок між пілотом і дроном
    frags.append(line(160, 270, 160, 220, color="#2b6cb0", sw=2, dash="4,4"))
    frags.append(text(165, 245, "Телеметрія", size=11, color=MUTED, anchor="start", italic=True))

    # Центральний блок: Радіомовлення в ефір (Broadcast Transports)
    b_rf = fitbox(340, 60, 280, 360, "Пряме радіомовлення (Broadcast RF)\n(Без встановлення з'єднання, 1-3 Гц)\n\n• Bluetooth 4 Legacy (0xFFFA)\n  (25-байтні ADV_IND пакети)\n\n• Bluetooth 5 Long Range\n  (Coded PHY S=8, Message Pack)\n\n• Wi-Fi Beacon (2.4 ГГц)\n  (Vendor IE 0xDD, OUI 0xFA0BBC)\n\n• Wi-Fi NAN / Wi-Fi Aware\n  (Action Frame / Social Ch 6, 44)", size=13, fill="#f0fff4", stroke="#27ae60", bold=True)
    frags.append(b_rf)

    # Стрілка від дрона до мовлення
    frags.append(arrow(280, 140, 340, 140, color="#27ae60", sw=2.5))
    frags.append(text(310, 130, "RF ефір", size=11, color="#27ae60", bold=True))

    # Приймачі на землі (Ground Receivers)
    b_rx_phone = fitbox(680, 60, 240, 105, "Смартфон перехожого / пілота\n- Додаток OpenDroneID\n- Wi-Fi / Bluetooth скан\n- Локальна візуалізація карти", size=12, fill="#fefcbf", stroke="#d69e2e", bold=True)
    b_rx_police = fitbox(680, 185, 240, 110, "Служби безпеки та поліція\n- Стаціонарні RF-сенсори\n- Миттєва пеленгація оператора\n- Валідація цифрового підпису", size=12, fill="#fefcbf", stroke="#d69e2e", bold=True)
    b_rx_utm = fitbox(680, 315, 240, 105, "Система U-Space / UTM Radar\n- Злиття з даними транспондерів\n- Моніторинг повітряного простору\n- Виявлення конфліктів трафіку", size=12, fill="#fefcbf", stroke="#d69e2e", bold=True)

    frags.extend([b_rx_phone, b_rx_police, b_rx_utm])

    # Стрілки від мовлення до приймачів
    frags.append(arrow(620, 115, 680, 115, color="#d69e2e", sw=2))
    frags.append(arrow(620, 240, 680, 240, color="#d69e2e", sw=2))
    frags.append(arrow(620, 365, 680, 365, color="#d69e2e", sw=2))

    render(os.path.join(IMG_DIR, "remote-id-architecture.svg"), w, h, *frags, title="Архітектура прямої цифрової ідентифікації Remote ID")


def fig_frame_structure():
    """Структура двійкових кадрів ASTM F3411 та Open Drone ID."""
    w, h = 960, 520
    frags = []

    # Загальний формат одного 25-байтного повідомлення
    b_msg_hdr = fitbox(40, 60, 200, 75, "Байт 0: Заголовок кадру\n- Msg Type (4 біти: 0x0..0xF)\n- Protocol Version (4 біти)", size=12, fill="#e2e8f0", stroke="#4a5568", bold=True)
    b_msg_pld = fitbox(250, 60, 670, 75, "Байти 1..24: Корисне навантаження повідомлення (24 байти фіксованого формату)\n(Дані Basic ID, Location/Vector, Authentication, Self-ID або System Data)", size=12, fill="#ebf8ff", stroke="#3182ce", bold=True)
    frags.extend([b_msg_hdr, b_msg_pld])

    # Типи повідомлень (Message Types)
    y_start = 160
    b_t0 = fitbox(40, y_start, 430, 70, "0x0: Basic ID (Ідентифікатор апарата)\n- ID Type: 1 (ANSI/CTA-2063-A), 2 (CAA), 4 (Session ID)\n- UA Type: Мультиротор, Літак, Гелікоптер (0..15)\n- UAS ID: 20 байтів унікального серійного номера", size=11, fill="#f7fafc", stroke="#4a5568")
    b_t1 = fitbox(490, y_start, 430, 70, "0x1: Location / Vector (Просторові координати)\n- Статус: На землі, У повітрі, Аварія (Emergency)\n- Широта й довгота: int32 (масштаб 1e-7 градуса)\n- Висота WGS84 та барометрична (крок 0.5 м)\n- Швидкість (horiz/vert), курс, точність (HAcc/VAcc)", size=11, fill="#f7fafc", stroke="#4a5568")

    b_t2 = fitbox(40, y_start + 85, 430, 70, "0x2: Authentication (Цифровий підпис)\n- Auth Type: 1 (UAS ID Signature), 2 (Operator Sig)\n- Page Number / Last Page Index (фрагментація)\n- Timestamp: UTC секунди від 01.01.2019\n- Auth Data: 17 байтів фрагмента підпису ECDSA", size=11, fill="#f7fafc", stroke="#4a5568")
    b_t3 = fitbox(490, y_start + 85, 430, 70, "0x3: Self-ID (Текстовий опис місії)\n- Description Type: 0 (Текстовий опис мети польоту)\n- Text: 23 байти ASCII (наприклад, «SEARCH-RESCUE-01»)\n- Застосовується для інформування оточуючих", size=11, fill="#f7fafc", stroke="#4a5568")

    b_t4 = fitbox(40, y_start + 170, 430, 70, "0x4: System Data (Дані оператора й зони)\n- Operator Location Type: 0 (Takeoff), 1 (Live GNSS)\n- Широта й довгота пілота: int32 (1e-7 градуса)\n- Висота пілота WGS84, радіус групи апаратів\n- Класифікація категорії ризику EASA (Open/Specific)", size=11, fill="#f7fafc", stroke="#4a5568")
    b_t5 = fitbox(490, y_start + 170, 430, 70, "0x5: Operator Location (Позиція пілота)\n- Додатковий формат для розширених координат\n- Вектор руху оператора при керуванні в русі\n- Точність визначення позиції пункту керування", size=11, fill="#f7fafc", stroke="#4a5568")

    frags.extend([b_t0, b_t1, b_t2, b_t3, b_t4, b_t5])

    # Message Pack (Тип 0xF)
    b_pack = fitbox(40, y_start + 260, 880, 75, "0xF: Message Pack (Пакет агрегованих повідомлень для BT5 Coded PHY та Wi-Fi Beacon)\n[ Заголовок 0xF0 ] + [ Кількість Msg (1 байт) ] + [ Повідомлення 0 (25Б) ] + [ Повідомлення 1 (25Б) ] + [ Повідомлення 2 (25Б) ] ...\nДозволяє передавати Basic ID + Location + System в одному радіокадрі без втрати синхронізації", size=11, fill="#feebc8", stroke="#dd6b20", bold=True)
    frags.append(b_pack)

    render(os.path.join(IMG_DIR, "astm-f3411-frame-structure.svg"), w, h, *frags, title="Структура двійкових повідомлень ASTM F3411 / Open Drone ID")


def fig_transport_encapsulation():
    """Інкапсуляція Open Drone ID у фізичні радіопротоколи BLE та Wi-Fi."""
    w, h = 960, 490
    frags = []

    # 1. Bluetooth 4.2 Legacy Advertising
    b_ble4_title = fitbox(40, 55, 880, 105, "1. Bluetooth 4.2 Legacy Advertising (Обмеження PDU 31 байт — передача повідомлень по черзі 1 Гц)\n[ PDU Header 2B ] [ AdvA MAC 6B ] [ Flags 3B (0x02, 0x01, 0x06) ] [ Service Data Header 4B (Len 0x1B, Type 0x16, UUID 0xFFFA) ] [ ODID Msg 25B ]\n*Передає почергово: 0x0 (Basic ID), 0x1 (Location), 0x4 (System) щосекунди в окремих рекламних пакетах*", size=11, fill="#ebf8ff", stroke="#3182ce")
    frags.append(b_ble4_title)

    # 2. Bluetooth 5 Extended Advertising (Coded PHY)
    b_ble5_title = fitbox(40, 185, 880, 115, "2. Bluetooth 5.0+ Extended Advertising (Coded PHY S=8 — дальність до 2-3 км, PDU до 254 байтів)\n[ ADV_EXT_IND на Primary Ch ] ---> Вказівник на [ AUX_ADV_IND на Secondary Ch ]\n[ Service Data Header: Type 0x16, UUID 0xFFFA ] [ Message Pack 0xF: Msg Count = 3 ] [ Basic ID 25B ] [ Location 25B ] [ System 25B ]\n*Агрегує всі три ключові повідомлення в один пакет (76 байтів) на далекобійній модуляції*", size=11, fill="#f0fff4", stroke="#27ae60")
    frags.append(b_ble5_title)

    # 3. Wi-Fi Beacon Frame (IEEE 802.11)
    b_wifi_title = fitbox(40, 325, 880, 125, "3. Wi-Fi Beacon Frame (Канал 6, Vendor Specific Information Element 0xDD)\n[ 802.11 MAC Header 24B ] [ Beacon Fixed Params 12B ] [ SSID IE: «RID-xxxxx» або прихований ]\n[ Vendor Specific IE: Element ID 0xDD | Length | OUI: 0xFA-0B-BC (Wi-Fi Alliance) | OUI Type: 0x0D ]\n[ Open Drone ID Message Pack 0xF: Header (1B) | Count (1B) | Basic ID (25B) | Location (25B) | System (25B) ]\n*Сприймається стандартними Wi-Fi адаптерами без необхідності асоціації з точкою доступу*", size=11, fill="#faf5ff", stroke="#805ad5")
    frags.append(b_wifi_title)

    render(os.path.join(IMG_DIR, "rf-transport-encapsulation.svg"), w, h, *frags, title="Інкапсуляція Open Drone ID у кадри Bluetooth та Wi-Fi")


def fig_auth_paging():
    """Механізм фрагментації та перевірки цифрового підпису (Authentication Paging)."""
    w, h = 960, 460
    frags = []

    # Вихідний блок цифрового підпису
    b_full_sig = fitbox(40, 60, 880, 80, "Повний криптографічний блок автентифікації (72 байти)\n[ Auth Type 1B: ECDSA P-256 ] [ Timestamp 4B: UTC Unix ] [ UAS ID Hash / Key ID 4B ] [ Цифровий підпис R (32B) + S (32B) = 64B ]\n*Підписує хеш SHA-256 від поточних координат (Location), серійного номера (Basic ID) та часової мітки*", size=12, fill="#feebc8", stroke="#dd6b20", bold=True)
    frags.append(b_full_sig)

    # Фрагментація на сторінки Type 0x2
    p0 = fitbox(40, 180, 205, 100, "Сторінка 0 (Page 0/3)\n- Hdr: Type 0x2, Ver 1\n- Auth Type: 1 (ECDSA)\n- Page: 0, LastPage: 3\n- Length: 72 байти\n- Timestamp: 4 байти\n- Дані підпису: 13 байтів", size=10, fill="#edf2f7", stroke="#4a5568")
    p1 = fitbox(265, 180, 205, 100, "Сторінка 1 (Page 1/3)\n- Hdr: Type 0x2, Ver 1\n- Auth Type: 1 (ECDSA)\n- Page: 1, LastPage: 3\n- Дані підпису: 23 байти\n  (продовження R/S)", size=10, fill="#edf2f7", stroke="#4a5568")
    p2 = fitbox(490, 180, 205, 100, "Сторінка 2 (Page 2/3)\n- Hdr: Type 0x2, Ver 1\n- Auth Type: 1 (ECDSA)\n- Page: 2, LastPage: 3\n- Дані підпису: 23 байти\n  (продовження R/S)", size=10, fill="#edf2f7", stroke="#4a5568")
    p3 = fitbox(715, 180, 205, 100, "Сторінка 3 (Page 3/3)\n- Hdr: Type 0x2, Ver 1\n- Auth Type: 1 (ECDSA)\n- Page: 3, LastPage: 3\n- Дані підпису: 13 байтів\n  (залишок + Key ID)", size=10, fill="#edf2f7", stroke="#4a5568")

    frags.extend([p0, p1, p2, p3])

    # Стрілки фрагментації
    frags.append(arrow(142, 140, 142, 180, color="#dd6b20", sw=1.8))
    frags.append(arrow(367, 140, 367, 180, color="#dd6b20", sw=1.8))
    frags.append(arrow(592, 140, 592, 180, color="#dd6b20", sw=1.8))
    frags.append(arrow(817, 140, 817, 180, color="#dd6b20", sw=1.8))

    # Блок валідації на приймачі
    b_verify = fitbox(40, 320, 880, 95, "Верифікація на приймачі (Receiver Authentication Pipeline)\n1. Буферизація сторінок 0..3 протягом вікна трансляції (1-2 секунди) -> Збирання єдиного блоку 72 байти\n2. Перевірка свіжості часової мітки (Δt < 1.0 с відносно Location Timestamp) для захисту від Replay Attack\n3. Отримання публічного ключа виробника/регулятора за Key ID -> Перевірка підпису ECDSA P-256 / SHA-256", size=11, fill="#f0fff4", stroke="#27ae60", bold=True)
    frags.append(b_verify)

    render(os.path.join(IMG_DIR, "auth-signature-paging.svg"), w, h, *frags, title="Фрагментація та верифікація повідомлень автентифікації (Authentication Paging)")


if __name__ == "__main__":
    fig_architecture()
    fig_frame_structure()
    fig_transport_encapsulation()
    fig_auth_paging()
    print("Всі SVG-фігури для Remote ID успішно згенеровано.")
