# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. pd-layer-stack: Архітектурний стек USB PD ──────────────────────────────
def fig_pd_layer_stack():
    W, H = 760, 410
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    cols = [
        ("Джерело (Source / DFP)", 190, "#2457d6"),
        ("Стік (Sink / UFP)", 570, "#c0392b")
    ]

    layers = [
        ("Менеджер політики пристрою (DPM)", "Тепловий режим, загальний бюджет живлення системи, батарея", 60, 50, "#f8fafc", "#475569"),
        ("Рушій політики (Policy Engine)", "Стани переговорів, оцінка запитів, переходи між ролями", 126, 50, "#f1f5f9", "#334155"),
        ("Рівень протоколу (Protocol Layer)", "Формування заголовків, MessageID, квитування GoodCRC, таймери", 192, 54, "#e2e8f0", "#1e293b"),
        ("Фізичний рівень (PHY Layer)", "Кодування BMC, маркери SOP*, розрахунок CRC-32, лінія CC", 262, 54, "#cbd5e1", "#0f172a")
    ]

    for title, cx, col in cols:
        p.append(rect(cx - 165, 24, 330, 308, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        p.append(text(cx, 44, title, size=13, color=col, bold=True))

        for l_title, l_desc, y, h, fill, stroke in layers:
            p.append(rect(cx - 155, y, 310, h, fill=fill, stroke=stroke, sw=1.2, rx=4))
            p.append(text(cx, y + 18, l_title, size=11, color=INK, bold=True))
            p.append(text(cx, y + 36, l_desc, size=9.5, color=MUTED))

    # Взаємодія між стеками
    p.append(arrow(345, 289, 415, 289, color=FIELD, sw=2.5))
    p.append(arrow(415, 289, 345, 289, color=FIELD, sw=2.5))
    p.append(text(380, 274, "Лінія CC (BMC)", size=10, color=FIELD, bold=True))

    p.append(line(345, 219, 415, 219, color="#64748b", sw=1.5, dash="4,4"))
    p.append(text(380, 210, "Повідомлення PD", size=9.5, color="#64748b", italic=True))

    b, _, _ = textbox(W / 2, 370,
                      "Рівень протоколу гарантує доставку повідомлень (GoodCRC, таймери, повтори),\n"
                      "тоді як рушій політики (PE) вирішує, чи погоджуватися на запитаний профіль живлення.",
                      size=11, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, pad=8)
    p.append(b)

    render(os.path.join(OUT, "pd-layer-stack.svg"), W, H, *p,
           title="Архітектурний стек рівнів USB Power Delivery")


# ── 2. pd-packet-format: Структура пакета та заголовка PD ─────────────────────
def fig_pd_packet_format():
    W, H = 760, 440
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    p.append(text(W / 2, 32, "Повна структура кадру USB PD на фізичній лінії CC", size=13, color=INK, bold=True))

    frame_blocks = [
        (25, 48, 100, 46, "Преамбула", "64 біти 0-1", "#f1f5f9", LINE),
        (130, 48, 95, 46, "SOP*", "4 K-коди", "#fee2e2", POS),
        (230, 48, 140, 46, "Заголовок (Header)", "16 бітів (2 Байти)", "#dbeafe", NEG),
        (375, 48, 175, 46, "Корисне навантаження", "0..7 об'єктів (0..28 Б) / Ext", "#fef3c7", "#d97706"),
        (555, 48, 110, 46, "CRC-32", "32 біти (4 Байти)", "#dcfce7", FIELD),
        (670, 48, 65, 46, "EOP", "1 K-код", "#f1f5f9", LINE),
    ]

    for x, y, w, h, title, sub, fill, stroke in frame_blocks:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=4))
        p.append(text(x + w / 2, y + 18, title, size=11, color=INK, bold=True))
        p.append(text(x + w / 2, y + 34, sub, size=9.5, color=MUTED))

    # Розгортка 16-бітного Message Header
    p.append(line(300, 94, 300, 122, color=NEG, sw=1.5, dash="3,3"))
    p.append(rect(25, 124, 710, 82, fill="#eff6ff", stroke=NEG, sw=1.6, rx=6))
    p.append(text(W / 2, 142, "Бітова структура 16-бітного Message Header", size=12, color=NEG, bold=True))

    hdr_fields = [
        (35, 154, 55, 44, "Ext", "Bit 15", "#bfdbfe"),
        (94, 154, 110, 44, "Num Data Objs", "Bits 14..12", "#bfdbfe"),
        (208, 154, 100, 44, "MessageID", "Bits 11..9 (0..7)", "#93c5fd"),
        (312, 154, 90, 44, "Port Power", "Bit 8 (Snk/Src)", "#bfdbfe"),
        (406, 154, 95, 44, "Spec Rev", "Bits 7..6 (PD 3.0)", "#bfdbfe"),
        (505, 154, 85, 44, "Port Data", "Bit 5 (UFP/DFP)", "#bfdbfe"),
        (594, 154, 131, 44, "Message Type", "Bits 4..0 (Тип)", "#93c5fd"),
    ]

    for x, y, w, h, title, sub, fill in hdr_fields:
        p.append(rect(x, y, w, h, fill=fill, stroke=NEG, sw=1.2, rx=3))
        p.append(text(x + w / 2, y + 17, title, size=10, color=INK, bold=True))
        p.append(text(x + w / 2, y + 33, sub, size=9.5, color=MUTED))

    # Розгортка 16-бітного Extended Message Header (якщо Ext = 1)
    p.append(rect(25, 220, 710, 80, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(W / 2, 238, "Розширений заголовок Extended Message Header (якщо Ext = 1, дані до 260 Байт)", size=12, color="#d97706", bold=True))

    ext_fields = [
        (35, 250, 85, 42, "Chunked", "Bit 15 (0/1)", "#fde68a"),
        (124, 250, 120, 42, "Chunk Number", "Bits 14..11 (0..15)", "#fde68a"),
        (248, 250, 110, 42, "Request Chunk", "Bit 10 (Запит)", "#fde68a"),
        (362, 250, 80, 42, "Резерв", "Bit 9 (0)", "#fef3c7"),
        (446, 250, 279, 42, "Data Size (Розмір даних у байтах)", "Bits 8..0 (0..260 байтів у повному повідомленні)", "#fde68a"),
    ]

    for x, y, w, h, title, sub, fill in ext_fields:
        p.append(rect(x, y, w, h, fill=fill, stroke="#d97706", sw=1.2, rx=3))
        p.append(text(x + w / 2, y + 17, title, size=10, color=INK, bold=True))
        p.append(text(x + w / 2, y + 33, sub, size=9.5, color=MUTED))

    rules = [
        "Num Data Objects = 0 → Керівне повідомлення (Control Message: GoodCRC, Accept, Reject, Wait, Soft_Reset тощо)",
        "Num Data Objects = 1..7 (Ext = 0) → Повідомлення даних (Data Message: Source_Capabilities, Request, BIST, VDM)",
        "Ext = 1 → Розширене повідомлення (Extended Message: дані до 260 байт, chunked фрагментація по 26 байт)"
    ]
    for i, r_text in enumerate(rules):
        p.append(text(40, 325 + i * 22, "•  " + r_text, size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "pd-packet-format.svg"), W, H, *p,
           title="Формат пакета та заголовків USB Power Delivery 3.1")


# ── 3. goodcrc-arq: Механізм квитування GoodCRC та таймери ───────────────────
def fig_goodcrc_arq():
    W, H = 760, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    tx_x, rx_x = 180, 580
    p.append(text(tx_x, 34, "Передавач (Transmitter)", size=12, color=NEG, bold=True))
    p.append(text(rx_x, 34, "Приймач (Receiver)", size=12, color=POS, bold=True))

    p.append(line(tx_x, 48, tx_x, 370, color=LINE, sw=1.5))
    p.append(line(rx_x, 48, rx_x, 370, color=LINE, sw=1.5))

    p.append(text(380, 58, "Успішна транзакція: валідний CRC та своєчасний GoodCRC", size=10.5, color=FIELD, bold=True))

    # TX -> RX
    p.append(arrow(tx_x, 75, rx_x, 105, color=NEG, sw=2))
    p.append(text(380, 82, "Повідомлення (MessageID = 0, CRC OK)", size=10, color=NEG, bold=True))

    # CRCReceiveTimer
    p.append(line(tx_x - 15, 75, tx_x - 15, 135, color="#d97706", sw=2))
    p.append(text(tx_x - 70, 105, "CRCReceiveTimer\n(0.9..1.1 мс)", size=9.5, color="#d97706", bold=True))

    # tTransmitSOP
    p.append(line(rx_x + 15, 105, rx_x + 15, 125, color=FIELD, sw=2))
    p.append(text(rx_x + 65, 115, "tTransmitSOP\n(< 195 мкс)", size=9.5, color=FIELD))

    # RX -> TX GoodCRC
    p.append(arrow(rx_x, 125, tx_x, 155, color=FIELD, sw=2))
    p.append(text(380, 132, "GoodCRC (MessageID = 0)", size=10, color=FIELD, bold=True))

    p.append(circle(tx_x, 155, 4, fill=FIELD, stroke=FIELD))
    p.append(text(tx_x - 75, 158, "Таймер зупинено\nMsgID := 1", size=9.5, color=FIELD, bold=True))

    p.append(line(30, 185, 730, 185, color="#e2e8f0", sw=1.2, dash="4,4"))

    # Повтор (Retry)
    p.append(text(380, 202, "Збій CRC або втрата: спрацьовує таймаут та повторна спроба (Retry)", size=10.5, color=POS, bold=True))

    p.append(arrow(tx_x, 220, rx_x - 40, 245, color=NEG, sw=2))
    p.append(text(360, 224, "Повідомлення (MessageID = 1)", size=10, color=NEG))
    p.append(text(rx_x - 30, 248, "✖ Збій CRC", size=10, color=POS, bold=True))

    p.append(line(tx_x - 15, 220, tx_x - 15, 290, color=POS, sw=2))
    p.append(text(tx_x - 70, 255, "CRCReceiveTimer\nВИЧЕРПАНО", size=9.5, color=POS, bold=True))

    p.append(arrow(tx_x, 295, rx_x, 325, color="#d97706", sw=2))
    p.append(text(380, 302, "Повтор Retry #1 (MessageID = 1 той самий!)", size=10, color="#d97706", bold=True))

    p.append(arrow(rx_x, 335, tx_x, 365, color=FIELD, sw=2))
    p.append(text(380, 342, "GoodCRC (MessageID = 1)", size=10, color=FIELD, bold=True))

    b, _, _ = textbox(W / 2, 395,
                      "Квитування GoodCRC відбувається виключно на рівні протоколу (PHY/Protocol Layer).\n"
                      "Якщо після nRetryCount (2 повтори, 3 спроби) GoodCRC не отримано — ініціюється Soft_Reset або Hard_Reset.",
                      size=10, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, pad=6)
    p.append(b)

    render(os.path.join(OUT, "goodcrc-arq.svg"), W, H, *p,
           title="Механізм квитування GoodCRC, таймери та повторні спроби")


# ── 4. power-negotiation-flow: Повний діалог узгодження контракту ──────────────
def fig_power_negotiation_flow():
    W, H = 760, 450
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    src_x, snk_x = 180, 580
    p.append(text(src_x, 32, "Джерело (Source / Живлення)", size=12, color=NEG, bold=True))
    p.append(text(snk_x, 32, "Стік (Sink / Споживач)", size=12, color=POS, bold=True))

    p.append(line(src_x, 44, src_x, 400, color=LINE, sw=1.5))
    p.append(line(snk_x, 44, snk_x, 400, color=LINE, sw=1.5))

    steps = [
        (60, "Source_Capabilities (меню 5V, 9V, 15V, 20V)", src_x, snk_x, NEG, "MsgID=0"),
        (85, "GoodCRC", snk_x, src_x, FIELD, "MsgID=0"),
        (120, "Request (Вибір профілю 20V / 3A)", snk_x, src_x, POS, "MsgID=0"),
        (145, "GoodCRC", src_x, snk_x, FIELD, "MsgID=0"),
        (180, "Accept (Згода джерела)", src_x, snk_x, NEG, "MsgID=1"),
        (205, "GoodCRC", snk_x, src_x, FIELD, "MsgID=1"),
        (305, "PS_RDY (Джерело стабілізувало 20V на VBUS)", src_x, snk_x, NEG, "MsgID=2"),
        (330, "GoodCRC", snk_x, src_x, FIELD, "MsgID=2"),
    ]

    for y, label, x1, x2, col, mid in steps:
        p.append(arrow(x1, y, x2, y + 16, color=col, sw=1.8))
        mid_x = (x1 + x2) / 2
        p.append(text(mid_x, y + 6, label, size=10, color=col, bold=True))
        p.append(text(x1 - 38 if x1 < x2 else x1 + 38, y + 8, mid, size=9.5, color=MUTED))

    # Фаза зміни напруги (Ramp) між Accept та PS_RDY
    p.append(rect(src_x - 90, 230, 180, 58, fill="#fef3c7", stroke="#d97706", sw=1.3, rx=4))
    p.append(text(src_x, 248, "Перебудова VBUS", size=10, color="#d97706", bold=True))
    p.append(text(src_x, 264, "5 В ➔ 20 В (tPSTransition)", size=9.5, color=INK))
    p.append(text(src_x, 278, "Стік тримає струм ≤ 2.5 Вт", size=9.5, color=MUTED))

    # Стік вмикає навантаження після PS_RDY
    p.append(rect(snk_x - 90, 350, 180, 42, fill="#dcfce7", stroke=FIELD, sw=1.3, rx=4))
    p.append(text(snk_x, 366, "Контракт 20 В активний", size=10, color=FIELD, bold=True))
    p.append(text(snk_x, 382, "Вмикання повного навантаження", size=9.5, color=INK))

    render(os.path.join(OUT, "power-negotiation-flow.svg"), W, H, *p,
           title="Повний діалог узгодження контракту живлення USB PD")


# ── 5. role-swap-sequence: Зміна ролей (PR_Swap, DR_Swap, VCONN_Swap) ─────────
def fig_role_swap_sequence():
    W, H = 760, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    p1_x, p2_x = 180, 580
    p.append(text(p1_x, 32, "Порт 1 (Початковий Стік / DFP)", size=11, color=POS, bold=True))
    p.append(text(p2_x, 32, "Порт 2 (Початкове Джерело / UFP)", size=11, color=NEG, bold=True))

    p.append(line(p1_x, 44, p1_x, 375, color=LINE, sw=1.5))
    p.append(line(p2_x, 44, p2_x, 375, color=LINE, sw=1.5))

    p.append(text(380, 48, "Послідовність зміни ролі живлення (PR_Swap)", size=11, color=INK, bold=True))

    steps = [
        (65, "PR_Swap (Запит зміни ролі живлення)", p1_x, p2_x, POS),
        (85, "GoodCRC", p2_x, p1_x, FIELD),
        (110, "Accept (Згода на зміну ролі)", p2_x, p1_x, NEG),
        (130, "GoodCRC", p1_x, p2_x, FIELD),
        (210, "PS_RDY (Порт 2 зняв VBUS і став Стіком)", p2_x, p1_x, NEG),
        (230, "GoodCRC", p1_x, p2_x, FIELD),
        (305, "PS_RDY (Порт 1 подав 5V VBUS і став Джерелом)", p1_x, p2_x, POS),
        (325, "GoodCRC", p2_x, p1_x, FIELD),
    ]

    for y, label, x1, x2, col in steps:
        p.append(arrow(x1, y, x2, y + 14, color=col, sw=1.6))
        mid_x = (x1 + x2) / 2
        p.append(text(mid_x, y + 6, label, size=10, color=col, bold=True))

    # Анотації
    p.append(rect(p2_x - 85, 145, 170, 46, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(p2_x, 162, "Порт 2 вимикає VBUS", size=9.5, color=POS, bold=True))
    p.append(text(p2_x, 178, "VBUS опускається до vSafe0V", size=9.5, color=MUTED))

    p.append(rect(p1_x - 85, 245, 170, 46, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(p1_x, 262, "Порт 1 вмикає VBUS (5V)", size=9.5, color=NEG, bold=True))
    p.append(text(p1_x, 278, "Стає новим Джерелом (Source)", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 392,
                      "PR_Swap міняє напрямок живлення без втрати USB з'єднання. "
                      "DR_Swap міняє ролі даних (DFP ↔ UFP), а VCONN_Swap передає живлення кабелю.",
                      size=10, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, pad=6)
    p.append(b)

    render(os.path.join(OUT, "role-swap-sequence.svg"), W, H, *p,
           title="Послідовність зміни ролей живлення PR_Swap")


# ── 6. soft-vs-hard-reset: Порівняння Soft_Reset та Hard_Reset ────────────────
def fig_soft_vs_hard_reset():
    W, H = 760, 390
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    cols = [
        ("Програмне скидання (Soft_Reset)", 195, "#2563eb", [
            ("Рівень виконання", "Рівень протоколу (Protocol Layer)", INK),
            ("Сигналізація", "Керівне повідомлення (Control Message)", INK),
            ("Вплив на VBUS", "ЖОДНОГО: контракт і напруга зберігаються", FIELD),
            ("Що скидається", "MessageID лічильники (в 0), стан автоматів", INK),
            ("Відповідь партнера", "Обов'язкове повідомлення Accept", INK),
            ("Швидкість", "Швидке відновлення (~десятків мс)", INK),
        ]),
        ("Апаратне скидання (Hard_Reset)", 565, "#dc2626", [
            ("Рівень виконання", "Фізичний рівень (PHY Layer K-коди)", INK),
            ("Сигналізація", "Спеціальна K-послідовність RST-1 / RST-2", INK),
            ("Вплив на VBUS", "ПОВНЕ ЗНЯТТЯ: обвал до 0 В (vSafe0V)", POS),
            ("Що скидається", "Повний стан порту, повернення до 5 В", INK),
            ("Відповідь партнера", "Немає повідомлення, реакція залізом", INK),
            ("Швидкість", "Тривале перезавантаження (до 1000 мс)", INK),
        ])
    ]

    for title, cx, col, rows in cols:
        p.append(rect(cx - 170, 30, 340, 300, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        p.append(text(cx, 54, title, size=12, color=col, bold=True))

        for i, (k, val, vcol) in enumerate(rows):
            y = 85 + i * 40
            p.append(rect(cx - 160, y, 320, 34, fill="#f8fafc", stroke="#e2e8f0", sw=1.1, rx=3))
            p.append(text(cx - 150, y + 14, k + ":", size=9.5, color=MUTED, anchor="start", bold=True))
            p.append(text(cx - 150, y + 26, val, size=9.5, color=vcol, anchor="start", bold=(vcol != INK)))

    b, _, _ = textbox(W / 2, 360,
                      "Soft_Reset відновлює синхронізацію протоколу без знеструмлення пристрою.\n"
                      "Hard_Reset — аварійний важіль фізичного скидання живлення до vSafe0V при фатальних збоях.",
                      size=10.5, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, pad=6)
    p.append(b)

    render(os.path.join(OUT, "soft-vs-hard-reset.svg"), W, H, *p,
           title="Порівняння рівнів відновлення: Soft_Reset проти Hard_Reset")


def main():
    fig_pd_layer_stack()
    fig_pd_packet_format()
    fig_goodcrc_arq()
    fig_power_negotiation_flow()
    fig_role_swap_sequence()
    fig_soft_vs_hard_reset()
    print("Всі 6 фігур згенеровано успішно.")

if __name__ == "__main__":
    main()
