# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми Чужі реєстри й членства (IEEE OUI, USB-IF, Bluetooth SIG, Wi-Fi Alliance)."""

import os
import sys

# Шлях до спільних помічників svgkit у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_hardware_ecosystem():
    """Чотири стовпи комерційних ідентифікаторів та членств апаратного продукту."""
    w, h = 980, 500
    frags = []

    # Заголовок / опис верхнього рівня
    frags.append(text(w / 2, 32, "Екосистема ідентифікаторів та членств апаратного продукту", size=16, bold=True))

    # Стовпець 1: IEEE RA (MAC / OUI)
    c1_hdr = fitbox(30, 60, 215, 60, "IEEE-RA (Реєстратор)\nIEEE Registration Authority", size=12, fill="#e2e8f0", stroke="#4a5568", bold=True)
    c1_body = fitbox(30, 130, 215, 220, "Простір адрес MAC / EUI\n\n• MA-L (24 біти OUI, 16.7M)\n• MA-M (28 бітів, 1.04M)\n• MA-S (36 бітів, 4096)\n• Company ID (CID)\n\nЮридичний статус:\nОдноразова купівля блоку\nу власність (без роялті)", size=11, fill="#f7fafc", stroke="#4a5568")
    c1_ftr = fitbox(30, 360, 215, 90, "Призначення:\nУнікальність у L2-мережах\n(Ethernet, Wi-Fi, BLE)\nЗапобігання ARP-колапсу", size=11, fill="#edf2f7", stroke="#2b6cb0")
    frags.extend([c1_hdr, c1_body, c1_ftr])

    # Стовпець 2: USB-IF (VID / PID)
    c2_hdr = fitbox(265, 60, 215, 60, "USB-IF (Консорціум)\nUSB Implementers Forum", size=12, fill="#e2e8f0", stroke="#4a5568", bold=True)
    c2_body = fitbox(265, 130, 215, 220, "Дескриптори USB\n\n• Vendor ID (16 бітів, 65k PID)\n• Нечлен: $6,000 разово\n• Членство: $5,000 / рік\n• Logo Admin: $3,500 / 2 роки\n\nСубліцензування:\nЗаборонено третьою стороною;\nдозвіл від вендорів кремнію", size=11, fill="#f7fafc", stroke="#4a5568")
    c2_ftr = fitbox(265, 360, 215, 90, "Призначення:\nМонтування драйверів ОС\n(WHQL, udev, CDC, HID)\nПраво на знак USB Trident", size=11, fill="#edf2f7", stroke="#2b6cb0")
    frags.extend([c2_hdr, c2_body, c2_ftr])

    # Стовпець 3: Bluetooth SIG (QDID / DID)
    c3_hdr = fitbox(500, 60, 215, 60, "Bluetooth SIG (Альянс)\nSpecial Interest Group", size=12, fill="#e2e8f0", stroke="#4a5568", bold=True)
    c3_body = fitbox(500, 130, 215, 220, "Кваліфікація та лістинг\n\n• Adopter Member ($0/рік)\n• Associate ($7.5k–$35k/рік)\n• Declaration Fee: $9,600\n  (або $2,500 за IIP стартапу)\n• QDID (дизайн) + DID (виріб)\n\nВимога:\nОбов'язковий лістинг виробу", size=11, fill="#f7fafc", stroke="#4a5568")
    c3_ftr = fitbox(500, 360, 215, 90, "Призначення:\nЛіцензія на патенти PRLA\nі торговельну марку Bluetooth\n(захист від арешту митницею)", size=11, fill="#edf2f7", stroke="#2b6cb0")
    frags.extend([c3_hdr, c3_body, c3_ftr])

    # Стовпець 4: Wi-Fi Alliance (WFA Certified)
    c4_hdr = fitbox(735, 60, 215, 60, "Wi-Fi Alliance (Торг. марка)\nWi-Fi Alliance (WFA)", size=12, fill="#e2e8f0", stroke="#4a5568", bold=True)
    c4_body = fitbox(735, 130, 215, 220, "Маркетинг і логотипи\n\n• Членство: $5.8k–$38.5k/рік\n• Тести в лабораторії ATL\n• Wi-Fi CERTIFIED 6 / WPA3\n• Passpoint / Agile Multiband\n\nIEEE 802.11 vs WFA:\nСтандарт відкритий (IEEE),\nлоготип приватний (WFA)", size=11, fill="#f7fafc", stroke="#4a5568")
    c4_ftr = fitbox(735, 360, 215, 90, "Призначення:\nДопуск до тендерів операторів,\nкорпоративних RFP та право\nнанесення логотипів Wi-Fi", size=11, fill="#edf2f7", stroke="#2b6cb0")
    frags.extend([c4_hdr, c4_body, c4_ftr])

    render(os.path.join(IMG_DIR, "hardware-identity-ecosystem.svg"), w, h, *frags)


def fig_mac_address_structure():
    """Двійкова анатомія адрес EUI-48 / EUI-64 та префіксів IEEE OUI."""
    w, h = 980, 470
    frags = []

    frags.append(text(w / 2, 30, "Анатомія адреси EUI-48 (MAC) та рівні розподілу IEEE-RA", size=15, bold=True))

    # Верхній рівень: 48 бітів (6 байтів)
    b_oui_hdr = fitbox(40, 60, 440, 45, "Старші 24..36 бітів: Префікс організації (IEEE-RA OUI)", size=12, fill="#ebf8ff", stroke="#3182ce", bold=True)
    b_dev_hdr = fitbox(500, 60, 440, 45, "Молодші 12..24 біти: Серійний номер пристрою (Extension / Device ID)", size=12, fill="#f0fff4", stroke="#27ae60", bold=True)
    frags.extend([b_oui_hdr, b_dev_hdr])

    # Байти в шістнадцятковому виді
    y_bytes = 120
    b_b0 = fitbox(40, y_bytes, 135, 45, "Байт 0 (Octet 1)\n[ b7 .. b1 | b0 ]", size=11, fill="#feebc8", stroke="#dd6b20", bold=True)
    b_b1 = fitbox(190, y_bytes, 135, 45, "Байт 1 (Octet 2)\n[ 8 бітів ]", size=11, fill="#feebc8", stroke="#dd6b20")
    b_b2 = fitbox(345, y_bytes, 135, 45, "Байт 2 (Octet 3)\n[ 8 бітів ]", size=11, fill="#feebc8", stroke="#dd6b20")
    b_b3 = fitbox(500, y_bytes, 135, 45, "Байт 3 (Octet 4)\n[ 8 бітів ]", size=11, fill="#c6f6d5", stroke="#38a169")
    b_b4 = fitbox(655, y_bytes, 135, 45, "Байт 4 (Octet 5)\n[ 8 бітів ]", size=11, fill="#c6f6d5", stroke="#38a169")
    b_b5 = fitbox(805, y_bytes, 135, 45, "Байт 5 (Octet 6)\n[ 8 бітів ]", size=11, fill="#c6f6d5", stroke="#38a169")
    frags.extend([b_b0, b_b1, b_b2, b_b3, b_b4, b_b5])

    # Збільшення першого байта: біти I/G та U/L
    b_bits_panel = fitbox(40, 185, 440, 125, "Анатомія Байта 0 (Least Significant Bit транслюється першим):\n\n• Біт 0 (I/G — Individual/Group):\n  0 = Unicast (індивідуальна адреса пристрою)\n  1 = Multicast / Broadcast (групова адреса)\n\n• Біт 1 (U/L — Universal/Local):\n  0 = Universally Administered (офіційно видана IEEE OUI)\n  1 = Locally Administered (LAA, локальна рандомізація)", size=11, fill="#fffaf0", stroke="#dd6b20")
    frags.append(b_bits_panel)

    # Категорії блоків IEEE MA-L, MA-M, MA-S
    b_ma_l = fitbox(500, 185, 440, 38, "MA-L (Large, $3,255): 24 біти префікс → 16,777,216 адрес (2^24)", size=11, fill="#edf2f7", stroke="#4a5568", bold=True)
    b_ma_m = fitbox(500, 230, 440, 38, "MA-M (Medium, $1,860): 28 бітів префікс → 1,048,576 адрес (2^20)", size=11, fill="#edf2f7", stroke="#4a5568", bold=True)
    b_ma_s = fitbox(500, 275, 440, 38, "MA-S (Small, $805): 36 бітів префікс → 4,096 адрес (2^12)", size=11, fill="#edf2f7", stroke="#4a5568", bold=True)
    frags.extend([b_ma_l, b_ma_m, b_ma_s])

    # Нижній блок: EUI-64 перетворення
    b_eui64 = fitbox(40, 330, 900, 115, "Конвертація EUI-48 в EUI-64 (для IPv6 SLAAC та Zigbee/Thread IEEE 802.15.4):\n1. Адреса EUI-48 ділиться навпіл: [Байт 0..2 (OUI)] та [Байт 3..5 (Device ID)].\n2. Посередині вставляється фіксоване 16-бітне значення 0xFFFE.\n3. У першому байті інвертується біт U/L (Modified EUI-64 format для IPv6 Interface Identifier).\nПриклад: 00:1A:2B : 3C:4D:5E → 00:1A:2B : FF:FE : 3C:4D:5E → IPv6 ID: 021A:2BFF:FE3C:4D5E", size=11, fill="#f7fafc", stroke="#2b6cb0")
    frags.append(b_eui64)

    render(os.path.join(IMG_DIR, "ieee-mac-address-structure.svg"), w, h, *frags)


def fig_bluetooth_paths():
    """Шляхи кваліфікації Bluetooth SIG: спадкування готових QDID проти BQTF тестування."""
    w, h = 980, 480
    frags = []

    frags.append(text(w / 2, 30, "Шляхи кваліфікації продукту в Bluetooth SIG Launch Studio", size=15, bold=True))

    # Вихідна точка: Рішення щодо архітектури заліза
    b_start = fitbox(360, 60, 260, 60, "Вибір бездротової архітектури\n(Bluetooth Core Specification)", size=12, fill="#e2e8f0", stroke="#4a5568", bold=True)
    frags.append(b_start)

    # Ліва гілка: Готовий модуль (Path A)
    b_mod = fitbox(40, 150, 420, 80, "Шлях А: Інтеграція готового RF-модуля\n(Nordic, Espressif, Telink, Silicon Labs)\n\n• Модуль уже має готові QDID (Controller + Host + RF-PHY)\n• Антена та RF-розводка не змінюються", size=11, fill="#f0fff4", stroke="#27ae60", bold=True)
    b_mod_flow = fitbox(40, 255, 420, 95, "Кваліфікація без повторного тестування:\n1. Підписання угоди Adopter Member ($0)\n2. Створення Declaration у Launch Studio\n3. Посилання на наявні QDID постачальника\n4. Оплата Declaration Fee ($9,600 або $2,500 IIP)\n5. Отримання унікального Declaration ID (DID)", size=11, fill="#f7fafc", stroke="#27ae60")
    frags.extend([b_mod, b_mod_flow])

    # Права гілка: Власний дизайн / Chip-down (Path B)
    b_chip = fitbox(520, 150, 420, 80, "Шлях Б: Власний дизайн Chip-down / Нова антена\n(Розведення трансивера на спільній платі)\n\n• Зміна топології друкованої плати або П-контуру узгодження\n• Інтеграція власної друкованої антени (PCB trace)", size=11, fill="#fffaf0", stroke="#dd6b20", bold=True)
    b_chip_flow = fitbox(520, 255, 420, 95, "Повна кваліфікація з тестуванням:\n1. Випробування RF-PHY у лабораторії BQTF ($5k–$15k)\n2. Заповнення форм ICS / IXIT у Launch Studio\n3. Реєстрація нового Qualified Design (новий QDID)\n4. Оплата Declaration Fee ($9,600 або $4,800 Associate)\n5. Отримання DID та лістинг кінцевого продукту", size=11, fill="#f7fafc", stroke="#dd6b20")
    frags.extend([b_chip, b_chip_flow])

    # Стрілки від вибору до шляхів
    frags.append(arrow(430, 120, 250, 150, color="#27ae60", sw=2))
    frags.append(arrow(550, 120, 730, 150, color="#dd6b20", sw=2))

    # Нижній спільний результат
    b_res = fitbox(40, 380, 900, 70, "Юридичний результат: Офіційне право на маркування\n- Внесення моделі до публічної бази сертифікованих пристроїв Bluetooth SIG\n- Право нанесення торговельної марки Bluetooth® та B-логотипу на корпус, пакування та софт\n- Повний захист від арешту партії митними органами США (CBP) та ЄС за порушення прав інтелектуальної власності", size=11, fill="#ebf8ff", stroke="#3182ce", bold=True)
    frags.append(b_res)

    frags.append(arrow(250, 350, 250, 380, color="#27ae60", sw=2))
    frags.append(arrow(730, 350, 730, 380, color="#dd6b20", sw=2))

    render(os.path.join(IMG_DIR, "bluetooth-sig-qualification-paths.svg"), w, h, *frags)


def fig_cost_compliance_matrix():
    """Економічна стратегія: вартість ідентифікаторів залежно від обсягу серії."""
    w, h = 980, 480
    frags = []

    frags.append(text(w / 2, 30, "Матриця витрат на ідентифікатори та членства за фазами виробництва", size=15, bold=True))

    # Фаза 1: Прототип та R&D (< 100 шт)
    f1_hdr = fitbox(30, 60, 290, 45, "Фаза 1: Прототип та R&D (< 100 шт)", size=12, fill="#edf2f7", stroke="#4a5568", bold=True)
    f1_body = fitbox(30, 115, 290, 250, "Оптимізація витрат: $0 .. $100\n\n• MAC-адреси:\n  Вбудовані унікальні ID чипа\n  (ESP32 MAC, STM32 UID)\n  або EEPROM 24AA02E48 ($0.30/шт)\n\n• USB VID/PID:\n  Субліцензія вендора (ST/Microchip)\n  або open-source pid.codes\n\n• Bluetooth / Wi-Fi:\n  Внутрішнє тестування, без лістингу,\n  без публічного використання знаків", size=11, fill="#f7fafc", stroke="#4a5568")
    frags.extend([f1_hdr, f1_body])

    # Фаза 2: Пілотна серія (500 .. 5,000 шт)
    f2_hdr = fitbox(345, 60, 290, 45, "Фаза 2: Пілотна комерція (500 .. 5k шт)", size=12, fill="#feebc8", stroke="#dd6b20", bold=True)
    f2_body = fitbox(345, 115, 290, 250, "Оптимізація витрат: $3,305 .. $9,305\n\n• MAC-адреси:\n  Купівля блоку IEEE MA-S ($805)\n  (4,096 унікальних EUI-48)\n\n• USB VID/PID:\n  Субліцензований PID вендора ($0)\n  або власний USB VID ($6,000)\n\n• Bluetooth SIG:\n  Adopter ($0) + IIP Declaration ($2,500)\n  зі спадкуванням QDID модуля\n\n• Wi-Fi:\n  Маркування IEEE 802.11 ($0)", size=11, fill="#fffaf0", stroke="#dd6b20")
    frags.extend([f2_hdr, f2_body])

    # Фаза 3: Масове виробництво (> 50,000 шт)
    f3_hdr = fitbox(660, 60, 290, 45, "Фаза 3: Масштаб (> 50,000 шт)", size=12, fill="#c6f6d5", stroke="#27ae60", bold=True)
    f3_body = fitbox(660, 115, 290, 250, "Повний стек відповідності: ~$25,000+\n\n• MAC-адреси:\n  Купівля блоку IEEE MA-L ($3,255)\n  (16.7M унікальних адрес)\n\n• USB VID/PID:\n  Власний USB-IF VID ($6,000)\n  + логотипна угода ($3,500)\n\n• Bluetooth SIG:\n  Associate Member ($7.5k/рік)\n  + Declaration Fee ($4,800/модель)\n\n• Wi-Fi Alliance:\n  Implementer ($5.8k/рік) + ATL сертифікація", size=11, fill="#f0fff4", stroke="#27ae60")
    frags.extend([f3_hdr, f3_body])

    # Підсумок вартості на 1 виріб
    f_sum = fitbox(30, 385, 920, 65, "Економіка на одиницю продукції (Unit Cost):\n- При тиражі 1,000 шт ідентифікатори додають ~$3.30 до собівартості кожного виробу.\n- При тиражі 100,000 шт повний юридичний стек ідентифікаторів коштує менше $0.25 на один пристрій.", size=11, fill="#ebf8ff", stroke="#3182ce", bold=True)
    frags.append(f_sum)

    render(os.path.join(IMG_DIR, "cost-and-compliance-matrix.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_hardware_ecosystem()
    fig_mac_address_structure()
    fig_bluetooth_paths()
    fig_cost_compliance_matrix()
    print("All figures generated successfully.")
