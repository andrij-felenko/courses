# -*- coding: utf-8 -*-
"""Генератор діаграм для теми NetLabel і CIPSO: мітки безпеки на мережевих пакетах."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

def build_netlabel_architecture(out_path):
    w, h = 900, 560
    frags = []

    # Background canvas card
    frags.append(rect(15, 45, 870, 500, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))

    # Zone 1: Userspace
    frags.append(rect(35, 65, 830, 85, fill="#f0f6fc", stroke="#388bfd", sw=1.5, rx=6))
    frags.append(text(450, 85, "ПРОСТІР КОРИСТУВАЧА (USERSPACE)", size=12, color="#0969da", bold=True))
    frags.append(fitbox(55, 95, 230, 42, "netlabelctl\nутиліта конфігурації", size=12, fill="#ffffff", stroke="#0969da", bold=True))
    frags.append(fitbox(335, 95, 230, 42, "Generic Netlink API\nNETLBL_NLTYPE_* сім'ї", size=12, fill="#ffffff", stroke="#0969da", bold=True))
    frags.append(fitbox(615, 95, 230, 42, "MLS демони / сокети\nпроцеси з MLS-рівнями", size=12, fill="#ffffff", stroke="#0969da", bold=True))

    # Netlink Arrow down
    frags.append(arrow(170, 137, 170, 175, color="#0969da", sw=2))
    frags.append(arrow(730, 137, 730, 175, color="#0969da", sw=2))

    # Zone 2: Kernel NetLabel Core
    frags.append(rect(35, 175, 400, 200, fill="#f6f8fa", stroke="#57606a", sw=1.5, rx=6))
    frags.append(text(235, 195, "ЯДРО: ПІДСИСТЕМА NETLABEL (net/netlabel)", size=12, color="#24292f", bold=True))
    frags.append(fitbox(50, 210, 175, 55, "Таблиця доменів\nnetlbl_domhsh_*\n(селектори IP/хостів)", size=11, fill="#ffffff", stroke="#57606a"))
    frags.append(fitbox(240, 210, 180, 55, "Рушій DOI (CIPSO/CALIPSO)\nтрансляція MLS ↔ опції\n(чутливість, категорії)", size=11, fill="#ffffff", stroke="#57606a"))
    frags.append(fitbox(50, 280, 175, 55, "Статичні мітки\nnetlbl_unlabeled\n(unlbl fallback хости)", size=11, fill="#ffffff", stroke="#57606a"))
    frags.append(fitbox(240, 280, 180, 55, "Кеш міток (Fast-Path)\nnetlbl_cache_*\n(хеш опцій → SECID)", size=11, fill="#ffffff", stroke="#57606a"))
    frags.append(text(235, 358, "Структура зв'язку: struct netlbl_lsm_secattr", size=11, color="#57606a", bold=True))

    # Zone 3: LSM Subsystem (SELinux / Smack)
    frags.append(rect(465, 175, 400, 200, fill="#fdf8f6", stroke="#bc4c00", sw=1.5, rx=6))
    frags.append(text(665, 195, "МОДУЛІ БЕЗПЕКИ LSM (SELinux / Smack)", size=12, color="#bc4c00", bold=True))
    frags.append(fitbox(480, 210, 180, 55, "SELinux MLS двигун\ns0:c0.c1023 ↔ рівні\nsid_to_secattr()", size=11, fill="#ffffff", stroke="#bc4c00"))
    frags.append(fitbox(670, 210, 180, 55, "Smack маркування\nмітки-рядки ↔ CIPSO\nsmackfs/cipso2", size=11, fill="#ffffff", stroke="#bc4c00"))
    frags.append(fitbox(480, 280, 180, 55, "Гачки сокетів\nsocket_post_create\nsock_rcv_skb, csk_clone", size=11, fill="#ffffff", stroke="#bc4c00"))
    frags.append(fitbox(670, 280, 180, 55, "AVC кеш дозволів\nперевірка політики\npeer { recv } / send", size=11, fill="#ffffff", stroke="#bc4c00"))
    frags.append(text(665, 358, "secattr_to_sid() / sid_to_secattr()", size=11, color="#bc4c00", bold=True))

    # Bi-directional Arrow between NetLabel and LSM
    frags.append(arrow(435, 275, 465, 275, color="#bc4c00", sw=2))
    frags.append(arrow(465, 275, 435, 275, color="#bc4c00", sw=2))

    # Zone 4: TCP/IP Network Stack & Wire
    frags.append(rect(35, 400, 830, 130, fill="#f0fff4", stroke="#1a7f37", sw=1.5, rx=6))
    frags.append(text(450, 420, "МЕРЕЖЕВИЙ СТЕК ЯДРА ТА ДАНІ В КАНАЛІ ЗВ'ЯЗКУ", size=12, color="#1a7f37", bold=True))
    frags.append(fitbox(55, 435, 230, 80, "Структури сокетів\nstruct sock, inet_sock\ninet_sk(sk)->opt\n(збережені IP опції сокета)", size=11, fill="#ffffff", stroke="#1a7f37"))
    frags.append(fitbox(335, 435, 230, 80, "Буфери пакетів sk_buff\nIPv4 Option 134 (0x86 CIPSO)\nIPv6 Option 0x07 (CALIPSO)\nконтроль у postroute / forward", size=11, fill="#ffffff", stroke="#1a7f37"))
    frags.append(fitbox(615, 435, 230, 80, "secmark vs NetLabel\nsecmark: внутрішній маркер xtables\nNetLabel: явні мітки в заголовку\nдля міжхостової передачі", size=11, fill="#ffffff", stroke="#1a7f37"))

    # Connections between NetLabel/LSM and Network Stack
    frags.append(arrow(170, 375, 170, 435, color="#1a7f37", sw=2))
    frags.append(arrow(450, 375, 450, 435, color="#1a7f37", sw=2))
    frags.append(arrow(730, 375, 730, 435, color="#1a7f37", sw=2))

    return render(out_path, w, h, *frags, title="Архітектура підсистеми NetLabel та її інтеграція з LSM")

def build_cipso_packet_format(out_path):
    w, h = 900, 580
    frags = []

    # Card background
    frags.append(rect(15, 45, 870, 520, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))

    # --- Section A: IPv4 CIPSO (FIPS 188 / RFC 791 Option 134) ---
    frags.append(rect(30, 60, 840, 240, fill="#f6f8fa", stroke="#0969da", sw=1.5, rx=6))
    frags.append(text(450, 80, "IPv4 CIPSO: COMMERCIAL IP SECURITY OPTION (Опція IP 134 / 0x86)", size=13, color="#0969da", bold=True))

    # Option Header row
    frags.append(fitbox(45, 95, 120, 40, "Option Type\n0x86 (134)", size=11, fill="#ddf4ff", stroke="#0969da", bold=True))
    frags.append(fitbox(170, 95, 120, 40, "Option Length\n(загальна довжина)", size=11, fill="#ddf4ff", stroke="#0969da"))
    frags.append(fitbox(295, 95, 260, 40, "CIPSO DOI (32 біти / 4 байти)\nідентифікатор домену інтерпретації", size=11, fill="#ddf4ff", stroke="#0969da", bold=True))
    frags.append(fitbox(560, 95, 295, 40, "Послідовність тегів CIPSO (Tag 1 / Tag 2 / Tag 5)\nдо заповнення загальної довжини опції", size=11, fill="#f0fff4", stroke="#1a7f37", bold=True))

    # CIPSO Tag 1: Bitmapped Categories
    frags.append(rect(45, 145, 795, 42, fill="#ffffff", stroke="#1a7f37", sw=1.2, rx=4))
    frags.append(fitbox(50, 148, 95, 36, "Tag Type\n1 (бітовий)", size=10, fill="#f0fff4", stroke="#1a7f37", bold=True))
    frags.append(fitbox(150, 148, 90, 36, "Tag Length\n(4 + N байтів)", size=10, fill="#f0fff4", stroke="#1a7f37"))
    frags.append(fitbox(245, 148, 90, 36, "Alignment\n0x00 (вирівн.)", size=10, fill="#f0fff4", stroke="#1a7f37"))
    frags.append(fitbox(340, 148, 140, 36, "Sensitivity Level\n(0..255, 8 бітів)", size=10, fill="#ffebe9", stroke="#cf222e", bold=True))
    frags.append(fitbox(485, 148, 350, 36, "Category Bitmap (бітова маска категорій: біт i = категорія i)\nдо 30 байтів (240 категорій на тег у FIPS 188)", size=10, fill="#ffffff", stroke="#1a7f37"))

    # CIPSO Tag 2: Enumerated Categories
    frags.append(rect(45, 195, 795, 42, fill="#ffffff", stroke="#57606a", sw=1.2, rx=4))
    frags.append(fitbox(50, 198, 95, 36, "Tag Type\n2 (перелік)", size=10, fill="#f6f8fa", stroke="#57606a", bold=True))
    frags.append(fitbox(150, 198, 90, 36, "Tag Length\n(4 + 2*K байт)", size=10, fill="#f6f8fa", stroke="#57606a"))
    frags.append(fitbox(245, 198, 90, 36, "Alignment\n0x00 (вирівн.)", size=10, fill="#f6f8fa", stroke="#57606a"))
    frags.append(fitbox(340, 198, 140, 36, "Sensitivity Level\n(0..255, 8 бітів)", size=10, fill="#ffebe9", stroke="#cf222e", bold=True))
    frags.append(fitbox(485, 198, 350, 36, "Array of 16-bit Category Integers [Cat#1, Cat#2, ...]\nмасив числових ідентифікаторів активних категорій", size=10, fill="#ffffff", stroke="#57606a"))

    # CIPSO Tag 5: Range Categories
    frags.append(rect(45, 245, 795, 42, fill="#ffffff", stroke="#8250df", sw=1.2, rx=4))
    frags.append(fitbox(50, 248, 95, 36, "Tag Type\n5 (діапазони)", size=10, fill="#fbefff", stroke="#8250df", bold=True))
    frags.append(fitbox(150, 248, 90, 36, "Tag Length\n(4 + 4*R байт)", size=10, fill="#fbefff", stroke="#8250df"))
    frags.append(fitbox(245, 248, 90, 36, "Alignment\n0x00 (вирівн.)", size=10, fill="#fbefff", stroke="#8250df"))
    frags.append(fitbox(340, 248, 140, 36, "Sensitivity Level\n(0..255, 8 бітів)", size=10, fill="#ffebe9", stroke="#cf222e", bold=True))
    frags.append(fitbox(485, 248, 350, 36, "Pairs of 16-bit Category Ranges: [Start_1..End_1], [Start_2..End_2]\nкомпактне кодування послідовних груп категорій", size=10, fill="#ffffff", stroke="#8250df"))

    # --- Section B: IPv6 CALIPSO (RFC 5570 Option 0x07) ---
    frags.append(rect(30, 315, 840, 235, fill="#fdf8f6", stroke="#bc4c00", sw=1.5, rx=6))
    frags.append(text(450, 335, "IPv6 CALIPSO: COMMON ARCHITECTURE LABEL IPv6 SECURITY OPTION (RFC 5570)", size=13, color="#bc4c00", bold=True))
    frags.append(text(450, 355, "Розміщується в заголовку Hop-by-Hop або Destination Options (IPPROTO_HOPOPTS / DSTOPTS)", size=11, color="#57606a"))

    # CALIPSO fields
    frags.append(fitbox(45, 375, 120, 50, "Option Type\n0x07\n(CALIPSO opt)", size=10, fill="#fff8c5", stroke="#9a6700", bold=True))
    frags.append(fitbox(170, 375, 120, 50, "Opt Data Len\n(довжина даних\nв октетах)", size=10, fill="#fff8c5", stroke="#9a6700"))
    frags.append(fitbox(295, 375, 260, 50, "CALIPSO DOI (32 біти / 4 байти)\nDomain of Interpretation\nідентифікатор політики безпеки", size=10, fill="#fff8c5", stroke="#9a6700", bold=True))
    frags.append(fitbox(560, 375, 285, 50, "CALIPSO Sensitivity Level (8 бітів)\nієрархічний рівень MLS (0..255)\nUnclassified / Secret / TopSecret", size=10, fill="#ffebe9", stroke="#cf222e", bold=True))

    frags.append(fitbox(45, 435, 245, 50, "CALIPSO Checksum (16 бітів)\nконтрольна сума RFC 1071\n(перевірка цілісності опції)", size=10, fill="#f0fff4", stroke="#1a7f37", bold=True))
    frags.append(fitbox(295, 435, 550, 50, "Compartment Bitmap (змінна довжина, кратна 32 бітам / 4 байтам)\nбітова маска неієрархічних категорій / компартментів безпеки\n(пряме зіставлення з категоріями SELinux MLS c0..c1023)", size=10, fill="#ffffff", stroke="#bc4c00"))

    # Comparison footer notes
    frags.append(rect(45, 495, 800, 42, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))
    frags.append(text(445, 520, "CIPSO (IPv4) вимагає переобчислення IP Header Checksum; CALIPSO (IPv6) має власну контрольну суму", size=11, color="#24292f", bold=True))

    return render(out_path, w, h, *frags, title="Формати заголовків міток безпеки: IPv4 CIPSO та IPv6 CALIPSO")

def build_packet_flow_lsm_hooks(out_path):
    w, h = 900, 580
    frags = []

    # Card background
    frags.append(rect(15, 45, 870, 520, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))

    # --- Left Column: Outbound Transmission Path (TX) ---
    frags.append(rect(30, 60, 410, 410, fill="#f0f6fc", stroke="#0969da", sw=1.5, rx=6))
    frags.append(text(235, 85, "ВИХІДНИЙ ШЛЯХ (TX: ВІДПРАВКА ПАКЕТА)", size=12, color="#0969da", bold=True))

    frags.append(fitbox(50, 105, 370, 48, "1. Процес створює сокет socket()\nLSM hook: security_socket_post_create()\nПризначення MLS-контексту процесу сокету (s1:c2)", size=10, fill="#ffffff", stroke="#0969da"))
    frags.append(arrow(235, 153, 235, 172, color="#0969da", sw=2))

    frags.append(fitbox(50, 172, 370, 50, "2. NetLabel формує опції IP для сокета\nnetlbl_sock_setattr() → cipso_v4_sock_setattr()\nГенерація CIPSO опції в inet_sk(sk)->opt", size=10, fill="#ffffff", stroke="#0969da"))
    frags.append(arrow(235, 222, 235, 242, color="#0969da", sw=2))

    frags.append(fitbox(50, 242, 370, 50, "3. Системний виклик sendmsg() / connect()\nПобудова sk_buff, копіювання IP опцій\nСтворення пакета з CIPSO Option 134 у заголовку", size=10, fill="#ffffff", stroke="#0969da"))
    frags.append(arrow(235, 292, 235, 312, color="#0969da", sw=2))

    frags.append(fitbox(50, 312, 370, 50, "4. Маршрутизація та фільтрація\nLSM hook: selinux_ip_postroute(skb)\nПеревірка дозволу відправки для мітки пакета", size=10, fill="#ffffff", stroke="#0969da"))
    frags.append(arrow(235, 362, 235, 382, color="#0969da", sw=2))

    frags.append(fitbox(50, 382, 370, 50, "5. Передача в драйвер мережевої карти (NIC TX)\nПакет виходить у мережу з явним CIPSO тегом\n(без шифрування, прозорий для MLS маршрутизаторів)", size=10, fill="#e6ffed", stroke="#1a7f37", bold=True))

    # --- Right Column: Inbound Reception Path (RX) ---
    frags.append(rect(460, 60, 410, 410, fill="#fdf8f6", stroke="#bc4c00", sw=1.5, rx=6))
    frags.append(text(665, 85, "ВХІДНИЙ ШЛЯХ (RX: ПРИЙОМ ТА ПЕРЕВІРКА)", size=12, color="#bc4c00", bold=True))

    frags.append(fitbox(480, 105, 370, 48, "1. Прийом пакета з мережевої карти (NIC RX)\nМережевий стек: ip_rcv() → ip_options_compile()\nВиявлення IP Option 134 (CIPSO) або Option 0x07", size=10, fill="#ffffff", stroke="#bc4c00"))
    frags.append(arrow(665, 153, 665, 172, color="#bc4c00", sw=2))

    frags.append(fitbox(480, 172, 370, 50, "2. Розбір мітки NetLabel в ядрі\ncipso_v4_sock_getattr() або netlbl_cache_lookup()\nТрансляція DOI + чутливість + теги → netlbl_lsm_secattr", size=10, fill="#ffffff", stroke="#bc4c00"))
    frags.append(arrow(665, 222, 665, 242, color="#bc4c00", sw=2))

    frags.append(fitbox(480, 242, 370, 50, "3. Трансляція атрибутів у LSM SECID\nLSM hook: security_netlbl_secattr_to_sid()\nОтримання SECID вхідного пакета (напр. s1:c2)", size=10, fill="#ffffff", stroke="#bc4c00"))
    frags.append(arrow(665, 292, 665, 312, color="#bc4c00", sw=2))

    frags.append(fitbox(480, 312, 370, 50, "4. Перевірка доступу до сокета (LSM Hook)\nsecurity_sock_rcv_skb(sk, skb)\nMLS dominance check: рівень сокета ≥ рівень пакета", size=10, fill="#ffebe9", stroke="#cf222e", bold=True))
    frags.append(arrow(665, 362, 665, 382, color="#bc4c00", sw=2))

    frags.append(fitbox(480, 382, 370, 50, "5. Доставка процесу & SO_PEERSEC\nrecvmsg() отримує дані payload\ngetsockopt(SO_PEERSEC) повертає MLS-контекст відправника", size=10, fill="#e6ffed", stroke="#1a7f37", bold=True))

    # Bottom cable box outside columns
    frags.append(line(235, 432, 235, 490, color="#1a7f37", sw=2))
    frags.append(line(235, 490, 665, 490, color="#1a7f37", sw=2))
    frags.append(arrow(665, 490, 665, 432, color="#1a7f37", sw=2))
    frags.append(rect(340, 475, 220, 30, fill="#ffffff", stroke="#1a7f37", sw=1.5, rx=4))
    frags.append(text(450, 495, "Фізична мережа / лінія зв'язку", size=11, color="#1a7f37", bold=True))

    return render(out_path, w, h, *frags, title="Життєвий цикл пакета: точки виклику LSM гачків та NetLabel")

def render_all():
    topic_dir = os.path.dirname(__file__)
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    fig1 = os.path.join(img_dir, "netlabel-architecture.svg")
    fig2 = os.path.join(img_dir, "cipso-calipso-packet-format.svg")
    fig3 = os.path.join(img_dir, "packet-flow-lsm-hooks.svg")

    build_netlabel_architecture(fig1)
    build_cipso_packet_format(fig2)
    build_packet_flow_lsm_hooks(fig3)
    print("All figures successfully rendered.")

if __name__ == "__main__":
    render_all()
