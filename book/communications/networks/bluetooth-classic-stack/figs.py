# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── stack_architecture: Архітектура стека Bluetooth Classic ───────────────────
def fig_stack_architecture():
    W, H = 840, 560
    p = []

    # Фон Host (верх)
    p.append(rect(40, 50, 760, 220, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(60, 75, "ПРОСТІР ХОСТА (HOST / ОС / Стек додатків)", size=13, color="#1e293b", bold=True, anchor="start"))

    # Рівні Host
    p.append(fitbox(60, 95, 230, 44, "Профілі застосунків\n(SPP, A2DP, HID, HFP)", size=11, bold=True, fill="#eff6ff", stroke="#3b82f6"))
    p.append(fitbox(310, 95, 220, 44, "Служби виявлення\n(SDP Сервер / Клієнт)", size=11, bold=True, fill="#eff6ff", stroke="#3b82f6"))
    p.append(fitbox(550, 95, 230, 44, "Аудіо / Дані потоку\n(AVDTP, AVCTP, BNEP)", size=11, bold=True, fill="#eff6ff", stroke="#3b82f6"))

    # RFCOMM
    p.append(fitbox(60, 147, 230, 36, "RFCOMM (Емуляція RS-232)", size=11, bold=True, fill="#f1f5f9", stroke="#64748b"))

    # L2CAP
    p.append(fitbox(60, 191, 720, 48, "L2CAP (Logical Link Control and Adaptation Protocol)\nМультиплексування каналів (CID) · Сегментація та збирання (SAR) · Керування потоком (ERTM)", size=11, bold=True, fill="#f0fdf4", stroke="#22c55e"))

    # Межа HCI
    p.append(line(40, 285, 800, 285, color="#dc2626", sw=2.5, dash="6,4"))
    p.append(rect(270, 271, 300, 28, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=4))
    p.append(text(420, 290, "Інтерфейс HCI (UART H4 / USB / SDIO)", size=12, color="#991b1b", bold=True))

    # Фон Controller (низ)
    p.append(rect(40, 310, 760, 210, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(60, 335, "ПРОСТІР КОНТРОЛЕРА (CONTROLLER / Чіп / Firmware)", size=13, color="#1e293b", bold=True, anchor="start"))

    # Рівні Controller
    p.append(fitbox(60, 350, 350, 42, "HCI Firmware Driver\nБуфери команд та ACL-пакетів", size=11, bold=True, fill="#fef3c7", stroke="#d97706"))
    p.append(fitbox(430, 350, 350, 42, "LMP (Link Manager Protocol)\nУправління з'єднанням, безпека, режими", size=11, bold=True, fill="#fef3c7", stroke="#d97706"))

    p.append(fitbox(60, 400, 720, 48, "Baseband & Link Controller\nTDD-таймінг (слоти 625 мкс) · Топологія Piconet/Scatternet · Пакети DH/DM · ARQ/FEC", size=11, bold=True, fill="#f5f3ff", stroke="#8b5cf6"))

    p.append(fitbox(60, 456, 720, 48, "Радіочастотний рівень (RF PHY)\n2.4 ГГц ISM · FHSS (1600 стрибків/с, 79 каналів) · GFSK (1 Мбіт/с), π/4-DQPSK (2 Мбіт/с), 8DPSK (3 Мбіт/с)", size=11, bold=True, fill="#fdf2f8", stroke="#db2777"))

    render(os.path.join(OUT, "stack-architecture.svg"), W, H, *p,
           title="Архітектура стека Bluetooth BR/EDR та межа HCI")


# ── fhss_slots: Таймінг слотів FHSS та TDD ─────────────────────────────────────
def fig_fhss_slots():
    W, H = 820, 340
    p = []

    # Часова вісь
    p.append(arrow(50, 240, 785, 240, color=LINE, sw=1.8))
    p.append(text(780, 260, "Час t", size=12, color=MUTED, bold=True))

    # 6 слотів по 110 px
    x0 = 60
    sw = 110
    slots = [
        ("Слот 2k", "Master → Slave", "Частота f(k)", "#eff6ff", "#3b82f6", "1-слотовий пакет DH1 (Master TX)"),
        ("Слот 2k+1", "Slave → Master", "Частота f(k+1)", "#f0fdf4", "#22c55e", "Відповідь / ACK (Slave TX)"),
        ("Слот 2k+2", "Master → Slave", "Частота f(k+2)", "#eff6ff", "#3b82f6", "DH3: початок 3-слотового пакету"),
        ("Слот 2k+3", "Частота f(k+2)", "Частота не змінюється", "#fef3c7", "#d97706", "DH3: продовження передачі"),
        ("Слот 2k+4", "Частота f(k+2)", "до кінця пакету", "#fef3c7", "#d97706", "DH3: завершення передачі"),
        ("Слот 2k+5", "Slave → Master", "Частота f(k+5)", "#f0fdf4", "#22c55e", "Відповідь на DH3 (Slave TX)"),
    ]

    for i, (sname, who, freq, bg_col, br_col, desc) in enumerate(slots):
        sx = x0 + i * sw
        # Вертикальні межі слотів
        p.append(line(sx, 70, sx, 245, color="#cbd5e1", sw=1.2, dash="3,3"))
        # Верхній маркер слота
        p.append(text(sx + sw/2, 60, sname, size=11, color=INK, bold=True))
        p.append(text(sx + sw/2, 75, "625 мкс", size=10, color=MUTED))

        # Блок активності
        if i in [0, 1]:
            # 1-слотовий пакет (активність 366 мкс + 259 мкс синтезатор)
            pw = sw * (366.0 / 625.0)
            p.append(rect(sx + 2, 95, pw, 70, fill=bg_col, stroke=br_col, sw=1.5, rx=4))
            p.append(text(sx + 2 + pw/2, 125, who, size=10, color=INK, bold=True))
            p.append(text(sx + 2 + pw/2, 145, freq, size=9, color=MUTED))
            # Захисний інтервал
            gw = sw - pw - 4
            p.append(rect(sx + 2 + pw, 95, gw, 70, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=2))
            p.append(text(sx + 2 + pw + gw/2, 135, "Синтез\n259 мкс", size=9, color="#64748b"))
        elif i == 2:
            # 3-слотовий пакет DH3 (покриває слоти 2, 3, 4)
            pw3 = sw * 3 * (1622.0 / 1875.0)
            p.append(rect(sx + 2, 95, pw3, 70, fill=bg_col, stroke=br_col, sw=1.8, rx=4))
            p.append(text(sx + sw*1.5, 125, "Master TX: 3-слотовий пакет DH3 (1622 мкс передачі)", size=11, color=INK, bold=True))
            p.append(text(sx + sw*1.5, 145, "Фіксована частота f(k+2) на всі 3 слоти · Наступний стрибок на f(k+5)", size=10, color="#9a3412"))
            # Захисний інтервал наприкінці 4-го слота
            gw3 = (sw * 3) - pw3 - 4
            p.append(rect(sx + 2 + pw3, 95, gw3, 70, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=2))
            p.append(text(sx + 2 + pw3 + gw3/2, 135, "253 мкс", size=9, color="#64748b"))
        elif i == 5:
            # Відповідь Slave після DH3
            pw = sw * (366.0 / 625.0)
            p.append(rect(sx + 2, 95, pw, 70, fill=bg_col, stroke=br_col, sw=1.5, rx=4))
            p.append(text(sx + 2 + pw/2, 125, who, size=10, color=INK, bold=True))
            p.append(text(sx + 2 + pw/2, 145, freq, size=9, color=MUTED))
            gw = sw - pw - 4
            p.append(rect(sx + 2 + pw, 95, gw, 70, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=2))

    # Права межа останнього слота
    p.append(line(x0 + 6 * sw, 70, x0 + 6 * sw, 245, color="#cbd5e1", sw=1.2, dash="3,3"))

    # Підписи
    p.append(text(W/2, 205, "TDD (Time Division Duplex): Master передає у парних слотах (2k), Slave відповідає у непарних (2k+1)", size=11, color=INK, bold=True))
    p.append(text(W/2, 285, "Швидкість стрибків: 1600 стрибків/с (1 слот = 625 мкс). Багатослотові пакети не змінюють частоту всередині пакета.", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fhss-slots.svg"), W, H, *p,
           title="Часовий розподіл слотів FHSS та дуплекс TDD")


# ── piconet_scatternet: Топологія Piconet та Scatternet ────────────────────────
def fig_piconet_scatternet():
    W, H = 820, 360
    p = []

    # Контур Piconet 1 (ліворуч)
    p.append(circle(250, 180, 140, fill="#f0f9ff", stroke="#0284c7", sw=1.8))
    p.append(text(170, 70, "Piconet 1 (Канал частот f₁)", size=13, color="#0369a1", bold=True))

    # Контур Piconet 2 (праворуч)
    p.append(circle(570, 180, 140, fill="#f0fdf4", stroke="#16a34a", sw=1.8))
    p.append(text(650, 70, "Piconet 2 (Канал частот f₂)", size=13, color="#15803d", bold=True))

    # Вузли Piconet 1
    # Master 1
    p.append(circle(200, 180, 26, fill="#0284c7", stroke="#0369a1", sw=2))
    p.append(text(200, 185, "M₁", size=14, color="#ffffff", bold=True))
    p.append(text(200, 218, "Master 1", size=10, color="#0369a1", bold=True))

    # Slaves Piconet 1
    p.append(circle(160, 115, 20, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    p.append(text(160, 120, "S₁", size=11, color="#0369a1", bold=True))
    p.append(line(190, 160, 170, 130, color="#0284c7", sw=1.5))

    p.append(circle(150, 245, 20, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    p.append(text(150, 250, "S₂", size=11, color="#0369a1", bold=True))
    p.append(line(185, 195, 165, 230, color="#0284c7", sw=1.5))

    p.append(circle(260, 265, 20, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    p.append(text(260, 270, "S₃", size=11, color="#0369a1", bold=True))
    p.append(line(215, 200, 248, 248, color="#0284c7", sw=1.5))

    # Вузли Piconet 2
    # Master 2
    p.append(circle(620, 180, 26, fill="#16a34a", stroke="#15803d", sw=2))
    p.append(text(620, 185, "M₂", size=14, color="#ffffff", bold=True))
    p.append(text(620, 218, "Master 2", size=10, color="#15803d", bold=True))

    # Slaves Piconet 2
    p.append(circle(660, 115, 20, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    p.append(text(660, 120, "S₄", size=11, color="#15803d", bold=True))
    p.append(line(630, 160, 650, 130, color="#16a34a", sw=1.5))

    p.append(circle(670, 245, 20, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    p.append(text(670, 250, "S₅", size=11, color="#15803d", bold=True))
    p.append(line(635, 195, 655, 230, color="#16a34a", sw=1.5))

    # Міст (Bridge Node B)
    p.append(circle(410, 180, 26, fill="#fef3c7", stroke="#d97706", sw=2.2))
    p.append(text(410, 185, "B", size=14, color="#92400e", bold=True))
    p.append(text(410, 218, "Міст (Bridge)", size=10, color="#92400e", bold=True))
    p.append(text(410, 232, "Slave в P₁ / Slave в P₂", size=9, color=MUTED))

    # Зв'язки моста
    p.append(line(226, 180, 384, 180, color="#0284c7", sw=2, dash="4,3"))
    p.append(line(436, 180, 594, 180, color="#16a34a", sw=2, dash="4,3"))

    # Пояснення внизу
    p.append(text(W/2, 330, "Scatternet об'єднує пікомережі через вузол-міст (Bridge), що почергово перемикає тактові частоти та канали FHSS", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "piconet-scatternet.svg"), W, H, *p,
           title="Топологія Piconet (1 Master + до 7 Slaves) та Scatternet")


# ── packet_format: Структура пакетів Baseband та ACL ───────────────────────────
def fig_packet_format():
    W, H = 840, 340
    p = []

    # Загальна структура пакета Baseband (Верхній рівень)
    p.append(text(50, 60, "Загальна структура пакета Baseband (BR):", size=12, color=INK, bold=True, anchor="start"))

    # Access Code (72 біти)
    p.append(rect(50, 75, 180, 48, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    p.append(text(140, 95, "Access Code", size=11, color="#1e40af", bold=True))
    p.append(text(140, 112, "72 біти (Синхронізація)", size=9, color=MUTED))

    # Packet Header (54 біти)
    p.append(rect(235, 75, 230, 48, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(text(350, 95, "Packet Header", size=11, color="#92400e", bold=True))
    p.append(text(350, 112, "54 біти (18 корисних бітів + FEC 1/3)", size=9, color=MUTED))

    # Payload (0..2745 бітів)
    p.append(rect(470, 75, 320, 48, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=4))
    p.append(text(630, 95, "Payload (Корисне навантаження)", size=11, color="#166534", bold=True))
    p.append(text(630, 112, "0 – 2745 бітів (Залежно від типу DH1..5 / DM1..5)", size=9, color=MUTED))

    # Деталізація Packet Header (Середній рівень)
    p.append(text(50, 155, "Поля заголовка Packet Header (18 бітів до кодування FEC 1/3):", size=12, color=INK, bold=True, anchor="start"))

    h_fields = [
        ("LT_ADDR", "3 б", 60, "#fee2e2", "#ef4444"),
        ("TYPE", "4 б", 75, "#fef3c7", "#f59e0b"),
        ("FLOW", "1 б", 50, "#e0e7ff", "#6366f1"),
        ("ARQN", "1 б", 50, "#f0fdf4", "#22c55e"),
        ("SEQN", "1 б", 50, "#fce7f3", "#ec4899"),
        ("HEC (CRC)", "8 б", 95, "#f1f5f9", "#64748b"),
    ]
    hx = 50
    for name, bits, fw, fcol, bcol in h_fields:
        p.append(rect(hx, 170, fw, 42, fill=fcol, stroke=bcol, sw=1.2, rx=3))
        p.append(text(hx + fw/2, 188, name, size=10, color=INK, bold=True))
        p.append(text(hx + fw/2, 203, bits, size=9, color=MUTED))
        hx += fw + 6

    p.append(text(hx + 10, 195, "× 3 (Потрійне повторення) = 54 біти", size=11, color="#991b1b", bold=True, anchor="start"))

    # Деталізація ACL Payload (Нижній рівень)
    p.append(text(50, 245, "Структура корисного навантаження ACL (Payload):", size=12, color=INK, bold=True, anchor="start"))

    p.append(rect(50, 260, 140, 44, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    p.append(text(120, 278, "Payload Header", size=10, color="#92400e", bold=True))
    p.append(text(120, 294, "1–2 байти (L_CH, Length)", size=9, color=MUTED))

    p.append(rect(196, 260, 460, 44, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=3))
    p.append(text(426, 278, "Дані вищих рівнів (L2CAP PDU)", size=10, color="#166534", bold=True))
    p.append(text(426, 294, "Сегменти L2CAP або кадрів вищих протоколів", size=9, color=MUTED))

    p.append(rect(662, 260, 128, 44, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=3))
    p.append(text(726, 278, "CRC-16", size=10, color="#991b1b", bold=True))
    p.append(text(726, 294, "2 байти (Для DM/DH)", size=9, color=MUTED))

    render(os.path.join(OUT, "packet-format.svg"), W, H, *p,
           title="Формат пакетів Baseband, заголовок кадру та Payload")


# ── l2cap_sar: Мультиплексування та сегментація L2CAP ─────────────────────────
def fig_l2cap_sar():
    W, H = 840, 360
    p = []

    # Верхній рівень: Великий L2CAP PDU
    p.append(text(50, 55, "1. L2CAP SDU від протоколу вищого рівня (наприклад, RFCOMM / SDP):", size=11, color=INK, bold=True, anchor="start"))

    p.append(rect(50, 70, 120, 44, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    p.append(text(110, 88, "L2CAP Header", size=10, color="#92400e", bold=True))
    p.append(text(110, 104, "Length + CID (4B)", size=9, color=MUTED))

    p.append(rect(175, 70, 560, 44, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=4))
    p.append(text(455, 88, "Корисні дані протоколу вищого рівня (SDU, наприклад 1000 байтів)", size=11, color="#166534", bold=True))
    p.append(text(455, 104, "Цілісний блок даних до сегментації", size=9, color=MUTED))

    # Стрілки сегментації
    p.append(arrow(200, 120, 140, 155, color="#64748b", sw=1.5))
    p.append(arrow(450, 120, 420, 155, color="#64748b", sw=1.5))
    p.append(arrow(680, 120, 700, 155, color="#64748b", sw=1.5))
    p.append(text(W/2, 140, "Сегментація SAR на рівні L2CAP під MTU Baseband", size=11, color="#0369a1", bold=True))

    # Нижній рівень: Фрагменти ACL для HCI та Baseband
    p.append(text(50, 170, "2. Фрагментовані ACL Data пакети (передаються через HCI до контролера):", size=11, color=INK, bold=True, anchor="start"))

    # Фрагмент 1 (Start fragment: PB = 0b10)
    p.append(rect(50, 185, 230, 80, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    p.append(rect(55, 190, 80, 30, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=2))
    p.append(text(95, 210, "HCI ACL Hdr\nPB=0b10 (Start)", size=9, color="#92400e", bold=True))
    p.append(rect(140, 190, 60, 30, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=2))
    p.append(text(170, 210, "L2CAP Hdr\n(Len, CID)", size=9, color="#92400e", bold=True))
    p.append(rect(55, 225, 220, 34, fill="#f0fdf4", stroke="#22c55e", sw=1.0, rx=2))
    p.append(text(165, 245, "Сегмент даних #1 (335 байтів)", size=9, color="#166534", bold=True))

    # Фрагмент 2 (Continuing fragment: PB = 0b01)
    p.append(rect(305, 185, 230, 80, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    p.append(rect(310, 190, 110, 30, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=2))
    p.append(text(365, 210, "HCI ACL Hdr\nPB=0b01 (Continuation)", size=9, color="#92400e", bold=True))
    p.append(rect(310, 225, 220, 34, fill="#f0fdf4", stroke="#22c55e", sw=1.0, rx=2))
    p.append(text(420, 245, "Сегмент даних #2 (339 байтів)", size=9, color="#166534", bold=True))

    # Фрагмент 3 (Continuing fragment: PB = 0b01)
    p.append(rect(560, 185, 230, 80, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    p.append(rect(565, 190, 110, 30, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=2))
    p.append(text(620, 210, "HCI ACL Hdr\nPB=0b01 (Continuation)", size=9, color="#92400e", bold=True))
    p.append(rect(565, 225, 220, 34, fill="#f0fdf4", stroke="#22c55e", sw=1.0, rx=2))
    p.append(text(675, 245, "Сегмент даних #3 (326 байтів)", size=9, color="#166534", bold=True))

    # Підсумок
    p.append(text(W/2, 290, "Приймач збирає фрагменти за індикатором PB (Packet Boundary) та передає повний SDU на відповідний канал CID", size=11, color=INK, bold=True))
    p.append(text(W/2, 330, "CID 0x0001 = SDP · CID 0x0002 = Signaling · CID 0x0040+ = Динамічні канали застосунків (RFCOMM, AVDTP)", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "l2cap-sar.svg"), W, H, *p,
           title="Сегментація та збирання (SAR) і маршрутизація каналів (CID) у L2CAP")


if __name__ == "__main__":
    fig_stack_architecture()
    fig_fhss_slots()
    fig_piconet_scatternet()
    fig_packet_format()
    fig_l2cap_sar()
    print("All figures generated successfully.")
