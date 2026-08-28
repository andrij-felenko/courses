# -*- coding: utf-8 -*-
"""Фігури до теми «SIM, IMSI, APN: як пристрій входить у мережу оператора».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори компонентів
AMBER = "#b9770e"     # криптографічні ключі та алгоритми
PURPLE = "#7c3aed"    # сигналізація та сесії (GTP-C / RSP / NAS)
CYAN = "#0891b2"      # ідентифікатори та файлова система
GREEN = "#27ae60"     # тракт передачі даних (GTP-U / IP)
RED_ACC = "#c0392b"   # захищені апаратні зони / Ki

# ── 1. Ієрархічна структура файлової системи смарт-карти UICC ─────────────────
def fig_uicc_file_system():
    W, H = 880, 560
    p = [text(W / 2, 24, "Ієрархічна структура файлової системи UICC (ETSI TS 102 221 / 3GPP TS 31.102)", size=15, bold=True)]

    # Корінь MF (Master File 3F00)
    p.append(rect(340, 50, 200, 50, fill="#f8fafc", stroke=INK, sw=2.0, rx=6))
    p.append(text(440, 72, "MF (Master File)", size=13, bold=True))
    p.append(text(440, 90, "ID: 3F00 (Корінь карти)", size=10.5, color=MUTED))

    # Лінії від MF до піддиректорій і файлів кореня
    p.append(line(440, 100, 440, 125, color=LINE, sw=1.5))
    p.append(line(130, 125, 750, 125, color=LINE, sw=1.5))

    # EF_DIR (2F00) - список застосунків
    p.append(line(130, 125, 130, 150, color=LINE, sw=1.5))
    p.append(rect(50, 150, 160, 65, fill="#f0f9ff", stroke=CYAN, sw=1.5, rx=5))
    p.append(text(130, 172, "EF_DIR (2F00)", size=12, color=CYAN, bold=True))
    p.append(text(130, 190, "Лінійний фіксований", size=10, color=MUTED))
    p.append(text(130, 204, "AID зареєстрованих аплетів", size=9.5, color=INK))

    # EF_ICCID (2FE2) - серійний номер чипа
    p.append(line(310, 125, 310, 150, color=LINE, sw=1.5))
    p.append(rect(230, 150, 160, 65, fill="#f0f9ff", stroke=CYAN, sw=1.5, rx=5))
    p.append(text(310, 172, "EF_ICCID (2FE2)", size=12, color=CYAN, bold=True))
    p.append(text(310, 190, "Прозорий (10 байтів BCD)", size=10, color=MUTED))
    p.append(text(310, 204, "Унікальний номер чипа", size=9.5, color=INK))

    # DF_TELECOM (7F10)
    p.append(line(460, 125, 460, 150, color=LINE, sw=1.5))
    p.append(rect(385, 150, 150, 50, fill="#fdf4ff", stroke=PURPLE, sw=1.5, rx=5))
    p.append(text(460, 172, "DF_TELECOM (7F10)", size=12, color=PURPLE, bold=True))
    p.append(text(460, 190, "Спільні сервіси зв'язку", size=10, color=MUTED))

    # ADF_USIM (Application Dedicated File)
    p.append(line(715, 125, 715, 150, color=LINE, sw=1.5))
    p.append(rect(630, 150, 170, 50, fill="#fefce8", stroke=AMBER, sw=2.0, rx=5))
    p.append(text(715, 172, "ADF_USIM (Аплет)", size=12, color=AMBER, bold=True))
    p.append(text(715, 190, "AID: A0000000871002...", size=9.5, color=MUTED))

    # Підкаталог DF_TELECOM файли: EF_SMS, EF_ADN
    p.append(line(460, 200, 460, 230, color=LINE, sw=1.2))
    p.append(line(410, 230, 510, 230, color=LINE, sw=1.2))
    
    p.append(line(410, 230, 410, 250, color=LINE, sw=1.2))
    p.append(rect(360, 250, 100, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(410, 270, "EF_SMS (6F3C)", size=10.5, bold=True))
    p.append(text(410, 286, "Лінійний фікс.", size=9.5, color=MUTED))
    p.append(text(410, 298, "Сховище SMS", size=9, color=INK))

    p.append(line(510, 230, 510, 250, color=LINE, sw=1.2))
    p.append(rect(470, 250, 100, 55, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(520, 270, "EF_ADN (6F3A)", size=10.5, bold=True))
    p.append(text(520, 286, "Лінійний фікс.", size=9.5, color=MUTED))
    p.append(text(520, 298, "Телефонна книга", size=9, color=INK))

    # Підкаталог ADF_USIM файли: EF_IMSI, EF_LOCI
    p.append(line(715, 200, 715, 230, color=LINE, sw=1.5))
    p.append(line(645, 230, 785, 230, color=LINE, sw=1.5))

    p.append(line(645, 230, 645, 250, color=LINE, sw=1.2))
    p.append(rect(590, 250, 110, 60, fill="#ffffff", stroke=CYAN, sw=1.5, rx=4))
    p.append(text(645, 270, "EF_IMSI (6F07)", size=10.5, color=CYAN, bold=True))
    p.append(text(645, 287, "Прозорий (9 байтів)", size=9, color=MUTED))
    p.append(text(645, 301, "MCC + MNC + MSIN", size=9, color=INK))

    p.append(line(785, 230, 785, 250, color=LINE, sw=1.2))
    p.append(rect(725, 250, 120, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(785, 270, "EF_LOCI (6F7E)", size=10.5, bold=True))
    p.append(text(785, 287, "Прозорий (11 байтів)", size=9, color=MUTED))
    p.append(text(785, 301, "TMSI, LAI, статус", size=9, color=INK))

    # Нижній блок: Захищений апаратний анклав Crypto Engine & Ki
    p.append(rect(30, 340, 820, 195, fill="#fef2f2", stroke=RED_ACC, sw=1.8, rx=8))
    p.append(text(50, 365, "Апаратний захищений криптографічний анклав (Secure Element Hardware Vault)", size=12, color=RED_ACC, bold=True, anchor="start"))

    # Блок закритого ключа Ki
    p.append(rect(60, 385, 220, 130, fill="#ffffff", stroke=RED_ACC, sw=1.5, rx=6))
    p.append(text(170, 412, "Секретний ключ Ki", size=13, color=RED_ACC, bold=True))
    p.append(text(170, 434, "Довжина: 128 / 256 бітів", size=10.5, color=INK))
    p.append(text(170, 456, "Прямий доступ ззовні", size=10, color=MUTED))
    p.append(text(170, 474, "ЗАБОРОНЕНО апаратно", size=10.5, color=RED_ACC, bold=True))
    p.append(text(170, 496, "Захист від DPA / SPA атак", size=9.5, color=MUTED))

    # Стрілка від Ki до обчислювального блоку
    p.append(line(280, 450, 340, 450, color=RED_ACC, sw=2.0))
    p.append(text(310, 440, "Ki", size=11, color=RED_ACC, bold=True))

    # Блок обчислення Milenage / TUAK
    p.append(rect(340, 385, 480, 130, fill="#ffffff", stroke=AMBER, sw=1.5, rx=6))
    p.append(text(580, 412, "Криптографічний процесор 3GPP (Milenage / TUAK / AES-128)", size=12.5, color=AMBER, bold=True))
    p.append(text(580, 435, "Вхідні параметри: RAND (128 біт) + AUTN (SQN ⊕ AK || AMF || MAC-A)", size=10, color=INK))
    p.append(text(580, 457, "Функції: f1 (MAC-A) · f2 (RES) · f3 (CK) · f4 (IK) · f5 (AK)", size=10, color=MUTED))
    p.append(text(580, 480, "Результат обчислення: RES (відповідь мережі), сесійні ключі CK та IK", size=10, color=GREEN, bold=True))
    p.append(text(580, 500, "Перевірка свіжості SQN через внутрішній лічильник карти", size=9.5, color=INK))

    render(os.path.join(IMG, 'uicc-file-system.svg'), W, H, *p)

# ── 2. Взаємна автентифікація 3GPP AKA (Milenage) ─────────────────────────────
def fig_aka_milenage_auth():
    W, H = 880, 520
    p = [text(W / 2, 24, "Процедура взаємної автентифікації 3GPP AKA та генерація ключів", size=15, bold=True)]

    # Стовпчики учасників
    # 1. SIM/USIM
    p.append(rect(30, 50, 150, 45, fill="#fef2f2", stroke=RED_ACC, sw=1.8, rx=6))
    p.append(text(105, 78, "SIM / USIM", size=13, color=RED_ACC, bold=True))
    p.append(line(105, 95, 105, 490, color=MUTED, sw=1.2, dash="4,4"))

    # 2. Мобільний термінал (UE / Modem)
    p.append(rect(230, 50, 150, 45, fill="#f0f9ff", stroke=CYAN, sw=1.8, rx=6))
    p.append(text(305, 78, "UE (Модем / ME)", size=13, color=CYAN, bold=True))
    p.append(line(305, 95, 305, 490, color=MUTED, sw=1.2, dash="4,4"))

    # 3. Мережевий вузол MME / SGSN
    p.append(rect(480, 50, 150, 45, fill="#fdf4ff", stroke=PURPLE, sw=1.8, rx=6))
    p.append(text(555, 78, "MME / SGSN", size=13, color=PURPLE, bold=True))
    p.append(line(555, 95, 555, 490, color=MUTED, sw=1.2, dash="4,4"))

    # 4. Центр автентифікації HSS / AuC
    p.append(rect(700, 50, 150, 45, fill="#fefce8", stroke=AMBER, sw=1.8, rx=6))
    p.append(text(775, 78, "HSS / AuC (Оператор)", size=13, color=AMBER, bold=True))
    p.append(line(775, 95, 775, 490, color=MUTED, sw=1.2, dash="4,4"))

    # Крок 1: Attach Request (IMSI)
    p.append(line(305, 130, 555, 130, color=CYAN, sw=1.8))
    p.append(text(430, 120, "1. Attach Request (IMSI)", size=11, color=CYAN, bold=True))

    # Крок 2: Запит векторів автентифікації
    p.append(line(555, 165, 775, 165, color=PURPLE, sw=1.8))
    p.append(text(665, 155, "2. Send Auth Info (IMSI)", size=10.5, color=PURPLE, bold=True))

    # Блок обчислення вечора в HSS
    p.append(rect(680, 185, 190, 60, fill="#ffffff", stroke=AMBER, sw=1.2, rx=4))
    p.append(text(775, 203, "Генерація вектору AV:", size=10, color=AMBER, bold=True))
    p.append(text(775, 220, "RAND, AUTN = (SQN ⊕ AK || AMF || MAC)", size=9, color=INK))
    p.append(text(775, 236, "XRES, CK, IK (через Ki)", size=9, color=MUTED))

    # Крок 3: Передача вектора MME
    p.append(line(775, 260, 555, 260, color=PURPLE, sw=1.8))
    p.append(text(665, 252, "3. Auth Info Resp (RAND, AUTN, XRES, CK, IK)", size=9.5, color=PURPLE, bold=True))

    # Крок 4: Запит автентифікації до термінала
    p.append(line(555, 290, 305, 290, color=PURPLE, sw=1.8))
    p.append(text(430, 282, "4. Authentication Request (RAND, AUTN)", size=10.5, color=PURPLE, bold=True))

    # Крок 5: Передача APDU до SIM/USIM
    p.append(line(305, 320, 105, 320, color=RED_ACC, sw=1.8))
    p.append(text(205, 312, "5. APDU AUTHENTICATE(RAND, AUTN)", size=9.5, color=RED_ACC, bold=True))

    # Блок перевірки в USIM
    p.append(rect(15, 340, 180, 60, fill="#ffffff", stroke=RED_ACC, sw=1.2, rx=4))
    p.append(text(105, 358, "Перевірка в USIM:", size=10, color=RED_ACC, bold=True))
    p.append(text(105, 374, "1. f1(Ki) -> перевірка MAC-A", size=9, color=INK))
    p.append(text(105, 390, "2. SQN > SQN_max (захист від replay)", size=9, color=MUTED))

    # Крок 6: Відповідь USIM до модема
    p.append(line(105, 415, 305, 415, color=RED_ACC, sw=1.8))
    p.append(text(205, 407, "6. RES, CK, IK", size=10.5, color=GREEN, bold=True))

    # Крок 7: Відповідь модема до MME
    p.append(line(305, 445, 555, 445, color=CYAN, sw=1.8))
    p.append(text(430, 437, "7. Authentication Response (RES)", size=10.5, color=CYAN, bold=True))

    # Блок верифікації в MME
    p.append(rect(460, 460, 190, 40, fill="#f0fdf4", stroke=GREEN, sw=1.5, rx=4))
    p.append(text(555, 477, "RES == XRES ?", size=11, color=GREEN, bold=True))
    p.append(text(555, 492, "Успіх -> взаємна довіра", size=9.5, color=INK))

    render(os.path.join(IMG, 'aka-milenage-auth.svg'), W, H, *p)

# ── 3. Активація PDP-контексту та встановлення тунелів GTP ─────────────────────
def fig_pdp_context_activation():
    W, H = 880, 520
    p = [text(W / 2, 24, "Активація PDP-контексту: сигналізація GTP-C та тракт даних GTP-U", size=15, bold=True)]

    # Зона сигнальної площини (Control Plane)
    p.append(rect(20, 50, 840, 190, fill="#faf5ff", stroke=PURPLE, sw=1.2, rx=8))
    p.append(text(35, 72, "Площина керування (Control Plane): сигналізація NAS / GTP-C", size=11.5, color=PURPLE, bold=True, anchor="start"))

    # Зона площини користувача (User Plane)
    p.append(rect(20, 260, 840, 240, fill="#f0fdf4", stroke=GREEN, sw=1.2, rx=8))
    p.append(text(35, 282, "Площина користувача (User Plane): інкапсуляція GTP-U поверх UDP/IP", size=11.5, color=GREEN, bold=True, anchor="start"))

    # Вузли
    # 1. UE
    p.append(rect(40, 100, 120, 110, fill="#ffffff", stroke=CYAN, sw=1.5, rx=6))
    p.append(text(100, 125, "UE (Модем)", size=12, color=CYAN, bold=True))
    p.append(text(100, 145, "+CGDCONT", size=10, color=MUTED))
    p.append(text(100, 165, "APN: internet", size=10, color=INK))
    p.append(text(100, 185, "+CGACT=1,1", size=10, color=POS, bold=True))

    # 2. eNodeB / gNodeB
    p.append(rect(210, 100, 130, 110, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(275, 125, "eNodeB (Базова сота)", size=11, bold=True))
    p.append(text(275, 150, "RRC сигналізація", size=10, color=MUTED))
    p.append(text(275, 175, "Транзит NAS", size=10, color=INK))

    # 3. MME (Mobility Management Entity)
    p.append(rect(390, 100, 140, 110, fill="#ffffff", stroke=PURPLE, sw=1.5, rx=6))
    p.append(text(460, 125, "MME (Сигналізація)", size=11.5, color=PURPLE, bold=True))
    p.append(text(460, 150, "Обробка APN", size=10, color=MUTED))
    p.append(text(460, 170, "DNS запит APN", size=9.5, color=INK))
    p.append(text(460, 190, "Create Session", size=9.5, color=PURPLE, bold=True))

    # 4. SGW (Serving Gateway)
    p.append(rect(570, 100, 130, 110, fill="#ffffff", stroke=AMBER, sw=1.5, rx=6))
    p.append(text(635, 125, "SGW (Шлюз)", size=12, color=AMBER, bold=True))
    p.append(text(635, 150, "GTP-C транзит", size=10, color=MUTED))
    p.append(text(635, 175, "Якір мобільності", size=9.5, color=INK))

    # 5. PGW / UPF
    p.append(rect(730, 100, 120, 110, fill="#ffffff", stroke=GREEN, sw=2.0, rx=6))
    p.append(text(790, 125, "PGW / UPF", size=12, color=GREEN, bold=True))
    p.append(text(790, 145, "Точка входу APN", size=9.5, color=MUTED))
    p.append(text(790, 165, "Виділення IP / DNS", size=9.5, color=POS, bold=True))
    p.append(text(790, 185, "Тунелювання GTP", size=9.5, color=INK))

    # Сигнальні лінії в Control Plane
    p.append(line(160, 155, 210, 155, color=CYAN, sw=1.5))
    p.append(line(340, 155, 390, 155, color=PURPLE, sw=1.5))
    p.append(line(530, 155, 570, 155, color=PURPLE, sw=1.8, dash="4,3"))
    p.append(text(550, 145, "S11", size=9.5, color=PURPLE, bold=True))
    p.append(line(700, 155, 730, 155, color=PURPLE, sw=1.8, dash="4,3"))
    p.append(text(715, 145, "S5/S8", size=9.5, color=PURPLE, bold=True))

    # User Plane тракт передачі пакетів
    # UE IP стек
    p.append(rect(40, 310, 130, 160, fill="#ffffff", stroke=CYAN, sw=1.5, rx=6))
    p.append(text(105, 335, "UE IP Stack", size=12, color=CYAN, bold=True))
    p.append(text(105, 360, "IP: 10.128.4.15", size=10.5, color=POS, bold=True))
    p.append(text(105, 385, "DNS: 8.8.8.8", size=10, color=MUTED))
    p.append(text(105, 410, "Сирі IP-пакети", size=10, color=INK))
    p.append(text(105, 435, "Без GTP обгортки", size=9.5, color=MUTED))

    # eNodeB тунель
    p.append(rect(220, 310, 140, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(290, 335, "eNodeB", size=12, bold=True))
    p.append(text(290, 360, "Інкапсуляція в GTP-U", size=10, color=MUTED))
    p.append(text(290, 385, "S1-U Тунель", size=10.5, color=GREEN, bold=True))
    p.append(text(290, 410, "TEID: 0x4A12F0", size=10, color=INK))
    p.append(text(290, 435, "UDP порт 2152", size=9.5, color=MUTED))

    # SGW User Plane
    p.append(rect(420, 310, 140, 160, fill="#ffffff", stroke=AMBER, sw=1.5, rx=6))
    p.append(text(490, 335, "SGW (User Plane)", size=12, color=AMBER, bold=True))
    p.append(text(490, 360, "Перекомутація TEID", size=10, color=MUTED))
    p.append(text(490, 385, "S5/S8-U Тунель", size=10.5, color=GREEN, bold=True))
    p.append(text(490, 410, "TEID: 0x9B8811", size=10, color=INK))
    p.append(text(490, 435, "UDP порт 2152", size=9.5, color=MUTED))

    # PGW Gi/SGi Interface
    p.append(rect(620, 310, 120, 160, fill="#ffffff", stroke=GREEN, sw=1.8, rx=6))
    p.append(text(680, 335, "PGW / UPF", size=12, color=GREEN, bold=True))
    p.append(text(680, 360, "Декапсуляція GTP", size=10, color=MUTED))
    p.append(text(680, 385, "NAT / Маршрутизація", size=10, color=INK))
    p.append(text(680, 410, "Інтерфейс SGi / Gi", size=10.5, color=POS, bold=True))
    p.append(text(680, 435, "Політики QoS/QCI", size=9.5, color=MUTED))

    # Зовнішня мережа PDN (Internet / Private VPN)
    p.append(rect(770, 330, 80, 120, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(810, 370, "PDN /", size=11.5, bold=True))
    p.append(text(810, 395, "APN", size=13, color=POS, bold=True))
    p.append(text(810, 420, "Internet", size=10, color=MUTED))

    # Лінії передачі даних
    p.append(line(170, 390, 220, 390, color=CYAN, sw=2.5))
    p.append(line(360, 390, 420, 390, color=GREEN, sw=3.0))
    p.append(line(560, 390, 620, 390, color=GREEN, sw=3.0))
    p.append(line(740, 390, 770, 390, color=POS, sw=2.5))

    render(os.path.join(IMG, 'pdp-context-activation.svg'), W, H, *p)

# ── 4. Архітектура Remote SIM Provisioning (eUICC / eSIM) ─────────────────────
def fig_esim_rsp_architecture():
    W, H = 880, 520
    p = [text(W / 2, 24, "Архітектура дистанційного завантаження профілів eSIM (GSMA SGP.22 RSP)", size=15, bold=True)]

    # Фонова зона хмари оператора / постачальників послуг
    p.append(rect(20, 50, 840, 160, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(35, 72, "Мережева інфраструктура віддаленого керування профілями (Remote Infrastructure)", size=11.5, color=INK, bold=True, anchor="start"))

    # Сервери:
    # 1. SM-DP+
    p.append(rect(40, 90, 230, 105, fill="#ffffff", stroke=AMBER, sw=1.8, rx=6))
    p.append(text(155, 115, "SM-DP+ Сервер", size=13, color=AMBER, bold=True))
    p.append(text(155, 135, "Data Preparation + Secure Routing", size=9.5, color=MUTED))
    p.append(text(155, 155, "Шифрування профілів оператора", size=9.5, color=INK))
    p.append(text(155, 175, "Генерація зв'язки Bound Profile Package", size=9, color=AMBER, bold=True))

    # 2. SM-DS
    p.append(rect(320, 90, 230, 105, fill="#ffffff", stroke=PURPLE, sw=1.8, rx=6))
    p.append(text(435, 115, "SM-DS Сервер", size=13, color=PURPLE, bold=True))
    p.append(text(435, 135, "Discovery Server (GSMA Root)", size=9.5, color=MUTED))
    p.append(text(435, 155, "Повідомлення про наявність профілю", size=9.5, color=INK))
    p.append(text(435, 175, "Реєстрація за EID чипа", size=9.5, color=PURPLE, bold=True))

    # 3. GSMA Root CI
    p.append(rect(600, 90, 240, 105, fill="#ffffff", stroke=RED_ACC, sw=1.8, rx=6))
    p.append(text(720, 115, "GSMA CI (Root PKI)", size=13, color=RED_ACC, bold=True))
    p.append(text(720, 135, "Сертифікаційний центр довіри", size=9.5, color=MUTED))
    p.append(text(720, 155, "Підпис сертифікатів eUICC та SM-DP+", size=9.5, color=INK))
    p.append(text(720, 175, "Захист від підробних серверів", size=9.5, color=RED_ACC, bold=True))

    # Фонова зона клієнтського пристрою
    p.append(rect(20, 230, 840, 270, fill="#f0f9ff", stroke=CYAN, sw=1.5, rx=8))
    p.append(text(35, 252, "Клієнтський пристрій (Device Host) з чипом eUICC", size=11.5, color=CYAN, bold=True, anchor="start"))

    # LPA (Local Profile Assistant)
    p.append(rect(40, 270, 260, 215, fill="#ffffff", stroke=CYAN, sw=1.5, rx=6))
    p.append(text(170, 295, "LPA (Local Profile Assistant)", size=12.5, color=CYAN, bold=True))
    p.append(text(170, 318, "LPD: Profile Download (HTTPS/TLS)", size=10, color=INK))
    p.append(text(170, 340, "LDS: Discovery Service Client", size=10, color=MUTED))
    p.append(text(170, 362, "LUI: User Interface / QR-сканер", size=10, color=INK))
    p.append(text(170, 390, "Комунікація з eUICC через APDU", size=10, color=CYAN, bold=True))
    p.append(text(170, 412, "ES10x інтерфейс з ISD-R", size=9.5, color=MUTED))
    p.append(text(170, 438, "Передача зашифрованого BPP", size=9.5, color=POS))
    p.append(text(170, 460, "Команди Enable / Disable / Delete", size=9.5, color=INK))

    # Чип eUICC
    p.append(rect(340, 270, 500, 215, fill="#ffffff", stroke=RED_ACC, sw=2.0, rx=6))
    p.append(text(590, 295, "eUICC Апаратний чип (Soldered IC / EID)", size=13, color=RED_ACC, bold=True))

    # Внутрішні домени безпеки eUICC
    # ECASD
    p.append(rect(360, 315, 140, 155, fill="#fef2f2", stroke=RED_ACC, sw=1.2, rx=5))
    p.append(text(430, 338, "ECASD", size=11, color=RED_ACC, bold=True))
    p.append(text(430, 358, "Root PKI ключі", size=9.5, color=MUTED))
    p.append(text(430, 378, "Сертифікат eUICC", size=9.5, color=INK))
    p.append(text(430, 398, "Перевірка підпису", size=9.5, color=MUTED))
    p.append(text(430, 418, "сервера SM-DP+", size=9.5, color=RED_ACC, bold=True))
    p.append(text(430, 442, "Крипто-ядро", size=9.5, color=INK))

    # ISD-R
    p.append(rect(515, 315, 145, 155, fill="#fdf4ff", stroke=PURPLE, sw=1.2, rx=5))
    p.append(text(587, 338, "ISD-R", size=11, color=PURPLE, bold=True))
    p.append(text(587, 358, "Root Security Domain", size=9.5, color=MUTED))
    p.append(text(587, 380, "Створення ISD-P", size=9.5, color=INK))
    p.append(text(587, 402, "Керування життєвим", size=9.5, color=MUTED))
    p.append(text(587, 422, "циклом профілів", size=9.5, color=PURPLE, bold=True))
    p.append(text(587, 446, "Розшифрування BPP", size=9.5, color=INK))

    # ISD-P (Профілі)
    p.append(rect(675, 315, 150, 155, fill="#fefce8", stroke=AMBER, sw=1.2, rx=5))
    p.append(text(750, 338, "ISD-P (Профілі)", size=11, color=AMBER, bold=True))
    p.append(text(750, 358, "Профіль Оператора A", size=9.5, color=GREEN, bold=True))
    p.append(text(750, 378, "Профіль Оператора B", size=9.5, color=MUTED))
    p.append(text(750, 400, "Ізольовані файлові", size=9, color=INK))
    p.append(text(750, 418, "системи USIM (Ki, IMSI)", size=9, color=AMBER, bold=True))
    p.append(text(750, 440, "Лише ОДИН активний", size=9.5, color=RED_ACC, bold=True))

    # З'єднувальні лінії
    p.append(line(155, 195, 155, 270, color=AMBER, sw=2.0))
    p.append(text(185, 225, "ES9+ (BPP)", size=9.5, color=AMBER, bold=True))

    p.append(line(300, 390, 360, 390, color=CYAN, sw=2.0))
    p.append(text(330, 380, "ES10", size=9.5, color=CYAN, bold=True))

    render(os.path.join(IMG, 'esim-rsp-architecture.svg'), W, H, *p)

if __name__ == "__main__":
    fig_uicc_file_system()
    fig_aka_milenage_auth()
    fig_pdp_context_activation()
    fig_esim_rsp_architecture()
    print("Всі 4 фігури успішно згенеровано у ./img/")
