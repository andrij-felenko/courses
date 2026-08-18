# -*- coding: utf-8 -*-
"""Фігури до теми «Кадр Ethernet».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія кадру Ethernet II ──────────────────────────────────────────
def fig_ethernet_frame_anatomy():
    """Повна структура кадру Ethernet II на фізичному рівні:
    IFG, преамбула, SFD, заголовки MAC, EtherType, корисне навантаження, FCS."""
    W, H = 840, 420
    f = [text(W / 2, 28, "Анатомія кадру Ethernet II (DIX) на фізичному дроті", size=16, bold=True)]

    # Фізичний рівень (L1 framing): IFG + Preamble + SFD
    f.append(rect(30, 60, 240, 110, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=6))
    f.append(text(150, 80, "Фізичний рівень (L1) — синхронізація", size=11, bold=True, color=MUTED, anchor="middle"))

    # IFG
    f.append(fitbox(40, 95, 75, 60, "IFG\n(інтервал)\n12 байтів\n(96 бітів)", size=10,
                    fill="#eef2f7", stroke=MUTED, sw=1.1))
    # Preamble
    f.append(fitbox(120, 95, 90, 60, "Преамбула\n7 байтів\n0xAA (10101010)", size=10,
                    fill="#eef2f7", stroke=MUTED, sw=1.1))
    # SFD
    f.append(fitbox(215, 95, 45, 60, "SFD\n1 байт\n0xAB", size=10,
                    fill="#fff3cd", stroke="#e67e22", sw=1.3, bold=True))

    # Канальний рівень (L2 Frame): Dst MAC, Src MAC, EtherType, Payload, FCS
    f.append(rect(280, 60, 530, 110, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    f.append(text(545, 80, "Канальний кадр (L2 Frame) — від 64 до 1518 байтів", size=12, bold=True, color=NEG, anchor="middle"))

    # Dst MAC
    f.append(fitbox(290, 95, 95, 60, "MAC отримувача\n(Destination)\n6 байтів", size=10,
                    fill=BG, stroke=NEG, sw=1.2, bold=True))
    # Src MAC
    f.append(fitbox(390, 95, 95, 60, "MAC джерела\n(Source)\n6 байтів", size=10,
                    fill=BG, stroke=NEG, sw=1.2, bold=True))
    # EtherType
    f.append(fitbox(490, 95, 80, 60, "EtherType\n2 байти\n(>= 0x0600)", size=10,
                    fill="#eafaf0", stroke=FIELD, sw=1.2, bold=True))
    # Payload & Pad
    f.append(fitbox(575, 95, 160, 60, "Корисні дані (Payload)\n46 – 1500 байтів\n(IPv4, IPv6, ARP...)\n+ Padding якщо < 46 Б", size=10,
                    fill="#fffdf0", stroke="#d4ac0d", sw=1.2))
    # FCS
    f.append(fitbox(740, 95, 60, 60, "FCS / CRC\n4 байти\nCRC-32", size=10,
                    fill="#fdecea", stroke=POS, sw=1.2, bold=True))

    # Пояснення знизу
    # Блок 1: Порядок байтів і бітів
    f.append(rect(30, 195, 380, 195, fill=BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(220, 220, "Порядок передачі та бітові прапори", size=13, bold=True, color=INK, anchor="middle"))
    f.append(mtext(45, 245, [
        "• Байти йдуть зліва направо: Dst MAC → Src MAC → EtherType.",
        "• Усередині кожного байта біти передаються LSB-first (молодшим уперед).",
        "• Перший переданий біт Dst MAC — прапор I/G (Unicast / Multicast).",
        "• Другий переданий біт Dst MAC — прапор U/L (Universal / Local MAC).",
        "• FCS (CRC-32) накриває весь L2-кадр (Dst MAC ... Payload/Pad)."
    ], size=11, anchor="start", color=INK, lh=1.45))

    # Блок 2: Межі розмірів кадру
    f.append(rect(430, 195, 380, 195, fill=BG, stroke=LINE, sw=1.2, rx=6))
    f.append(text(620, 220, "Розміри та обмеження (MTU = 1500)", size=13, bold=True, color=INK, anchor="middle"))
    f.append(mtext(445, 245, [
        "• Мінімальний L2-кадр: 6 + 6 + 2 + 46 (Pad) + 4 = 64 байти.",
        "• Кадр менший за 64 байти вважається Runt/уламком колізії.",
        "• Максимальний стандартний L2-кадр: 14 (заголовок) + 1500 + 4 = 1518 байтів.",
        "• З тегом 802.1Q VLAN: заголовок 18 байтів → максимум 1522 байти.",
        "• Фізична довжина на дроті: L2-кадр + 8 Б (преамбула/SFD) + 12 Б (IFG)."
    ], size=11, anchor="start", color=INK, lh=1.45))

    render(os.path.join(IMG, "ethernet-frame-anatomy.svg"), W, H, *f)


# ── 2. Порівняння Ethernet II vs IEEE 802.3 ────────────────────────────────
def fig_dix_vs_8023():
    """Порівняння Ethernet II (EtherType) та IEEE 802.3 (Length + LLC/SNAP).
    Поріг 1536 (0x0600) як демаркаційна лінія між довжиною та протоколом."""
    W, H = 840, 420
    f = [text(W / 2, 28, "Ethernet II (DIX) проти IEEE 802.3 LLC/SNAP", size=16, bold=True)]

    # Ethernet II
    f.append(rect(30, 60, 780, 115, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(45, 82, "Ethernet II (DIX) — стандарт de facto інтернету", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(fitbox(45, 98, 110, 55, "Dst MAC\n6 байтів", size=11, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(160, 98, 110, 55, "Src MAC\n6 байтів", size=11, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(275, 98, 145, 55, "EtherType >= 0x0600\n2 байти (0x0800 IPv4,\n0x86DD IPv6, 0x0806 ARP)", size=10,
                    fill="#eafaf0", stroke=FIELD, sw=1.3, bold=True))
    f.append(fitbox(425, 98, 290, 55, "IP-пакет / корисні дані (Payload)\n46 – 1500 байтів (пряме вкладення без оверхеду)", size=10,
                    fill="#fffdf0", stroke="#d4ac0d", sw=1.1))
    f.append(fitbox(720, 98, 80, 55, "FCS (CRC32)\n4 байти", size=11, fill=BG, stroke=POS, sw=1.1))

    # IEEE 802.3 + 802.2 LLC + SNAP
    f.append(rect(30, 195, 780, 125, fill="#fdfaf4", stroke="#e67e22", sw=1.5, rx=6))
    f.append(text(45, 217, "IEEE 802.3 + LLC (802.2) + SNAP — складний стек OSI", size=13, bold=True, color="#e67e22", anchor="start"))
    f.append(fitbox(45, 233, 90, 65, "Dst MAC\n6 байтів", size=10, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(140, 233, 90, 65, "Src MAC\n6 байтів", size=10, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(235, 233, 95, 65, "Length <= 1500\n2 байти (<= 0x05DC)\nдовжина LLC+Data", size=9,
                    fill="#fef5e7", stroke="#e67e22", sw=1.2, bold=True))
    f.append(fitbox(335, 233, 115, 65, "LLC (802.2) 3Б\nDSAP (0xAA)\nSSAP (0xAA)\nCtrl (0x03)", size=9,
                    fill="#ebf5fb", stroke="#2980b9", sw=1.1))
    f.append(fitbox(455, 233, 125, 65, "SNAP 5Б\nOUI (3Б = 0x000000)\nEtherType (2Б = 0x0800)", size=9,
                    fill="#ebf5fb", stroke="#2980b9", sw=1.1))
    f.append(fitbox(585, 233, 130, 65, "Корисні дані\nдо 1492 байтів\n(мінус 8Б LLC/SNAP)", size=9,
                    fill="#fffdf0", stroke="#d4ac0d", sw=1.1))
    f.append(fitbox(720, 233, 80, 65, "FCS (CRC32)\n4 байти", size=10, fill=BG, stroke=POS, sw=1.1))

    # Демонстрація розмежувального правила
    f.append(rect(30, 340, 780, 65, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(W / 2, 360, "Правило демаркації поля Type/Length (RFC 894 / IEEE 802.3x):", size=12, bold=True, anchor="middle"))
    f.append(text(W / 2, 385, "Значення <= 1500 (0x05DC) інтерпретується як ДОВЖИНА  |  Значення >= 1536 (0x0600) інтерпретується як ETHERTYPE",
                  size=11, bold=True, color=POS, anchor="middle"))

    render(os.path.join(IMG, "dix-vs-8023.svg"), W, H, *f)


# ── 3. Тегування IEEE 802.1Q ────────────────────────────────────────────────
def fig_vlan_8021q_tag():
    """Структура 4-байтового тега 802.1Q (TPID + TCI: PCP, DEI, VID)."""
    W, H = 820, 410
    f = [text(W / 2, 28, "Вставка та структура тега IEEE 802.1Q (VLAN & QoS)", size=16, bold=True)]

    # Загальний вигляд кадру з 802.1Q тегом
    f.append(rect(30, 55, 760, 85, fill="#f4f6f8", stroke=LINE, sw=1.3, rx=6))
    f.append(text(410, 75, "Кадр Ethernet із вставленим тегом 802.1Q (розмір зростає на 4 байти)", size=12, bold=True, color=INK, anchor="middle"))

    f.append(fitbox(40, 88, 100, 42, "Dst MAC (6B)", size=10, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(145, 88, 100, 42, "Src MAC (6B)", size=10, fill=BG, stroke=NEG, sw=1.1))
    f.append(fitbox(250, 88, 140, 42, "802.1Q Tag (4B)\nTPID + TCI", size=10, fill="#fdecea", stroke=POS, sw=1.5, bold=True))
    f.append(fitbox(395, 88, 100, 42, "EtherType (2B)\n(напр. 0x0800)", size=10, fill="#eafaf0", stroke=FIELD, sw=1.1))
    f.append(fitbox(500, 88, 205, 42, "Payload (42–1500B)", size=10, fill="#fffdf0", stroke="#d4ac0d", sw=1.1))
    f.append(fitbox(710, 88, 70, 42, "FCS (4B)", size=10, fill=BG, stroke=POS, sw=1.1))

    # Збільшена схема 4 байтів тега
    f.append(rect(30, 160, 760, 235, fill=BG, stroke=POS, sw=1.6, rx=6))
    f.append(text(410, 185, "Детальна розкладка 32 бітів тега 802.1Q", size=14, bold=True, color=POS, anchor="middle"))

    # TPID (16 бітів)
    f.append(rect(50, 205, 270, 65, fill="#ebf5fb", stroke="#2980b9", sw=1.3, rx=4))
    f.append(text(185, 230, "TPID (16 бітів)", size=12, bold=True, color="#2980b9", anchor="middle"))
    f.append(text(185, 252, "0x8100 (Tag Protocol Identifier)", size=11, color=INK, anchor="middle"))

    # TCI (16 бітів): PCP, DEI, VID
    f.append(rect(330, 205, 440, 65, fill="#fef9e7", stroke="#d4ac0d", sw=1.3, rx=4))
    f.append(text(550, 222, "TCI — Tag Control Information (16 бітів)", size=12, bold=True, color="#b7950b", anchor="middle"))

    # PCP
    f.append(fitbox(340, 235, 110, 30, "PCP (3 біти)\nПріоритет QoS", size=9, fill=BG, stroke="#d4ac0d", sw=1.1, bold=True))
    # DEI
    f.append(fitbox(455, 235, 75, 30, "DEI (1 біт)\nСкидання", size=9, fill=BG, stroke="#d4ac0d", sw=1.1, bold=True))
    # VID
    f.append(fitbox(535, 235, 225, 30, "VID — VLAN Identifier (12 бітів: 1 – 4094)", size=9, fill=BG, stroke="#d4ac0d", sw=1.1, bold=True))

    # Опис полів
    f.append(mtext(50, 295, [
        "• TPID (16 бітів) = 0x8100: сигналізує комутатору, що заголовок містить тег VLAN.",
        "• PCP (3 біти, 802.1p): 8 класів трафіку від 0 (Best Effort) до 7 (Мережеве керування/голос).",
        "• DEI / CFI (1 біт): Drop Eligible Indicator — дозвіл дропати кадр першим при перевантаженні каналу.",
        "• VID (12 бітів): номер віртуальної мережі. 0 = пріоритет без VLAN, 1 = default VLAN, 4095 = reserved."
    ], size=11, anchor="start", color=INK, lh=1.45))

    render(os.path.join(IMG, "vlan-8021q-tag.svg"), W, H, *f)


# ── 4. Мінімальний розмір кадру 64 байти й Slot Time ────────────────────────
def fig_min_frame_slot_time():
    """Фізична причина мінімального розміру 64 байти (512 біт-часів) у CSMA/CD:
    час поширення сигналу туди й назад (RTT) у максимальному колізійному домені."""
    W, H = 820, 420
    f = [text(W / 2, 28, "Чому мінімальний кадр рівно 64 байти (512 біт-часів)", size=16, bold=True)]

    # Станція A ліворуч, Станція B праворуч
    f.append(rect(40, 60, 150, 65, fill="#ebf5fb", stroke=NEG, sw=1.4, rx=6))
    f.append(text(115, 88, "Вузол A", size=13, bold=True, color=NEG, anchor="middle"))
    f.append(text(115, 110, "початок передачі t=0", size=10, color=MUTED, anchor="middle"))

    f.append(rect(630, 60, 150, 65, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(705, 88, "Вузол B", size=13, bold=True, color=POS, anchor="middle"))
    f.append(text(705, 110, "передача перед t=T_prop", size=10, color=MUTED, anchor="middle"))

    # Дріт між ними (коаксіал 10BASE5 довжиною до 2.5 км з повторювачами)
    f.append(line(190, 92, 630, 92, color=LINE, sw=3))
    f.append(text(410, 80, "Спільний кабель Ethernet (максимальний домен: час поширення T_prop ≈ 25.6 мкс)", size=10, color=MUTED, anchor="middle"))

    # Хвиля передачі від A до B
    f.append(arrow(190, 140, 580, 140, color=NEG, sw=2))
    f.append(text(380, 132, "Хвиля сигналу A рухається праворуч (t = 0 → T_prop)", size=11, color=NEG, anchor="middle"))

    # Колізія біля вузла B
    f.append(circle(600, 140, 14, fill="#fff3cd", stroke=POS, sw=2))
    f.append(text(600, 145, "⚡", size=14, color=POS, anchor="middle"))
    f.append(text(600, 170, "Колізія при t ≈ T_prop", size=10, bold=True, color=POS, anchor="middle"))

    # Хвиля колізії повертається до A
    f.append(arrow(580, 195, 200, 195, color=POS, sw=2))
    f.append(text(390, 187, "Хвиля зіткнення (Jam-сигнал) повертається до A (t = 2 · T_prop ≈ 51.2 мкс)", size=11, color=POS, anchor="middle"))

    # Пояснювальний висновок
    f.append(rect(40, 230, 740, 170, fill="#f4fbf7", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(410, 255, "Правило виявлення колізії (Slot Time = 512 біт-часів = 64 байти):", size=13, bold=True, color=FIELD, anchor="middle"))
    f.append(mtext(60, 280, [
        "1. Передавач A ПОВИНЕН продовжувати передачу кадру, доки хвиля колізії не повернеться назад (2 · T_prop).",
        "2. Якщо кадр надто короткий (< 64 Б), A закінчить передачу ДО приходу відлуння колізії і вважатиме її успішною!",
        "3. 51.2 мкс на 10 Мбіт/с = рівно 512 бітів = 64 байти (Slot Time).",
        "4. Навіть у сучасному Full-Duplex комутованому Ethernet, де колізій немає, ліміт 64 байти збережено",
        "   для сумісності стандартів, конвеєрів ASIC і лічильників помилок (Runt frames)."
    ], size=11, anchor="start", color=INK, lh=1.45))

    render(os.path.join(IMG, "min-frame-slot-time.svg"), W, H, *f)


# ── 5. Ефективність Jumbo Frames ───────────────────────────────────────────
def fig_jumbo_frame_efficiency():
    """Порівняння накладних витрат стандартних MTU 1500 проти Jumbo Frames MTU 9000."""
    W, H = 820, 400
    f = [text(W / 2, 28, "Ефективність Jumbo Frames: зменшення накладних витрат L1/L2 і CPU", size=16, bold=True)]

    # Стандартний MTU 1500 (6 кадрів)
    f.append(rect(30, 55, 760, 145, fill="#fdfaf4", stroke="#e67e22", sw=1.4, rx=6))
    f.append(text(45, 75, "Стандартний MTU 1500: передача 9000 байтів даних = 6 кадрів", size=12, bold=True, color="#e67e22", anchor="start"))

    for i in range(6):
        x = 45 + i * 125
        f.append(rect(x, 90, 118, 50, fill=BG, stroke=MUTED, sw=1.1, rx=4))
        f.append(text(x + 59, 108, f"Кадр #{i+1} (1500 Б)", size=10, bold=True, anchor="middle"))
        f.append(text(x + 59, 126, "Оверхед: 38 Б L1/L2", size=9, color=POS, anchor="middle"))

    f.append(mtext(45, 160, [
        "Сумарний оверхед L1/L2/L3 на 9000 Б даних: 6 × 38 Б (L1/L2) + 6 × 40 Б (IP+TCP) = 468 байтів.",
        "Навантаження на ОС: 6 переривань NIC, 6 дескрипторів кілець DMA, 6 обчислень заголовків."
    ], size=10, anchor="start", color=INK, lh=1.35))

    # Jumbo Frame MTU 9000 (1 кадр)
    f.append(rect(30, 215, 760, 170, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(45, 235, "Jumbo Frame MTU 9000: передача 9000 байтів даних = 1 кадр", size=12, bold=True, color=FIELD, anchor="start"))

    f.append(rect(45, 250, 730, 50, fill=BG, stroke=FIELD, sw=1.3, rx=4))
    f.append(text(410, 270, "Єдиний Jumbo Frame (9000 байтів корисного навантаження)", size=12, bold=True, color=FIELD, anchor="middle"))
    f.append(text(410, 288, "Оверхед: 38 Б L1/L2 + 40 Б (IP+TCP) = лише 78 байтів (економія 83% оверхеду!)", size=10, color=INK, anchor="middle"))

    f.append(mtext(45, 320, [
        "• Пропускна здатність: зменшення кількості пакетів у 6 разів (з 812 000 до 135 000 на 10 GbE лінку).",
        "• CPU overhead: 1 апаратне переривання замість 6, менше перемикань контексту ядра.",
        "• Обмеження: вимагає однакової підтримки на ВСІХ комутаторах і NIC локального L2-сегмента!"
    ], size=10, anchor="start", color=INK, lh=1.35))

    render(os.path.join(IMG, "jumbo-frame-efficiency.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ethernet_frame_anatomy()
    fig_dix_vs_8023()
    fig_vlan_8021q_tag()
    fig_min_frame_slot_time()
    fig_jumbo_frame_efficiency()
    print("All figures generated successfully.")
