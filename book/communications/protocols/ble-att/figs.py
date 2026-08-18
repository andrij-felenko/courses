# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. att-architecture: Клієнт-серверна модель і пласка таблиця атрибутів ─────
def fig_att_architecture():
    W, H = 840, 370
    p = []

    # Клієнт (зліва)
    cx, cy = 130, 180
    cb, cbw, cbh = textbox(cx, cy, "ATT-клієнт\n(Client)", size=13, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.8, min_w=150)
    p.append(cb)
    p.append(text(cx, cy + 34, "Ініціює запити й команди", size=10, color=MUTED))
    p.append(text(cx, cy + 48, "Отримує сповіщення", size=10, color=MUTED))

    # Сервер (справа) — містить базу даних
    sx, sy = 635, 180
    p.append(rect(sx - 175, sy - 150, 350, 300, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(sx, sy - 128, "ATT-сервер (Server)", size=13, color=FIELD, bold=True))
    p.append(text(sx, sy - 110, "База даних атрибутів (Attribute Database)", size=10, color=MUTED))

    # Таблиця атрибутів усередині сервера
    th_y = sy - 84
    p.append(rect(sx - 165, th_y, 330, 24, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(sx - 125, th_y + 16, "Handle", size=10, bold=True, color=FIELD))
    p.append(text(sx - 55, th_y + 16, "UUID", size=10, bold=True, color=FIELD))
    p.append(text(sx + 35, th_y + 16, "Value", size=10, bold=True, color=FIELD))
    p.append(text(sx + 120, th_y + 16, "Permissions", size=10, bold=True, color=FIELD))

    rows = [
        ("0x0001", "0x2800 (Primary Service)", "0x180D (Heart Rate)", "Read Only"),
        ("0x0002", "0x2803 (Characteristic)", "Props: 0x10, Hdl: 0x0003", "Read Only"),
        ("0x0003", "0x2A37 (HR Measurement)", "0x00, 0x48 (72 bpm)", "Notify"),
        ("0x0004", "0x2902 (CCCD)", "0x0001 (Notifications ON)", "Read / Write"),
        ("0x0005", "0x2800 (Primary Service)", "0x180F (Battery Service)", "Read Only"),
        ("0x0006", "0x2803 (Characteristic)", "Props: 0x02, Hdl: 0x0007", "Read Only"),
        ("0x0007", "0x2A19 (Battery Level)", "0x62 (98 %)", "Read / Encrypt"),
    ]

    for i, (hdl, uid, val, perm) in enumerate(rows):
        ry = th_y + 28 + i * 25
        bg_col = "#ffffff" if i % 2 == 0 else "#f4f9f4"
        p.append(rect(sx - 165, ry, 330, 23, fill=bg_col, stroke="#e2e8f0", sw=1, rx=2))
        p.append(text(sx - 125, ry + 15, hdl, size=9, color=INK))
        p.append(text(sx - 55, ry + 15, uid[:12] + "..", size=9, color=INK))
        p.append(text(sx + 35, ry + 15, val[:14] + "..", size=9, color=INK))
        p.append(text(sx + 120, ry + 15, perm, size=9, color=MUTED))

    # Стрілки взаємодії
    p.append(arrow(cx + cbw / 2 + 10, cy - 35, sx - 180, cy - 35, color=NEG, sw=1.8))
    p.append(text((cx + cbw / 2 + sx - 175) / 2, cy - 43, "Запити (Request) / Команди (Command)", size=10, color=NEG, bold=True))

    p.append(arrow(sx - 180, cy + 25, cx + cbw / 2 + 10, cy + 25, color=FIELD, sw=1.8))
    p.append(text((cx + cbw / 2 + sx - 175) / 2, cy + 17, "Відповіді (Response) / Сповіщення (Notification)", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 14, "Атрибут: 16-бітний дескриптор (Handle), тип (UUID), значення (Value) та права доступу (Permissions)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "att-architecture.svg"), W, H, *p,
           title="Клієнт-серверна модель ATT і пласка база атрибутів")


# ── 2. att-pdu-formats: Формат бітів Opcode і типовий кадр PDU ────────────────
def fig_att_pdu_formats():
    W, H = 840, 320
    p = []

    # Верхній блок: Анатомія 1-байтового ATT Opcode
    p.append(text(60, 32, "1. Структура байта Opcode (Command & Auth прапорці):", size=12, bold=True, color=INK, anchor="start"))

    ox = 60
    oy = 52
    cell_h = 38

    # 8 біт: [7] Command, [6] Auth Signature, [5..0] Method
    p.append(rect(ox, oy, 150, cell_h, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(ox + 75, oy + 16, "Біт 7: Command Flag", size=10, bold=True, color=POS))
    p.append(text(ox + 75, oy + 30, "0 = Request/Rsp, 1 = Cmd", size=9, color=MUTED))

    p.append(rect(ox + 158, oy, 170, cell_h, fill="#fff4e6", stroke="#d97706", sw=1.5, rx=4))
    p.append(text(ox + 243, oy + 16, "Біт 6: Auth Signature", size=10, bold=True, color="#d97706"))
    p.append(text(ox + 243, oy + 30, "1 = підписано 12-байт MAC", size=9, color=MUTED))

    p.append(rect(ox + 336, oy, 384, cell_h, fill="#eef4ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(ox + 528, oy + 16, "Біти 5..0: ATT Method (Номер операції)", size=10, bold=True, color=NEG))
    p.append(text(ox + 528, oy + 30, "0x02 = Exchange MTU, 0x0A = Read, 0x12 = Write...", size=9, color=MUTED))

    # Нижній блок: Приклад кадру ATT_WRITE_REQ / ATT_READ_RSP у буфері
    p.append(text(60, 135, "2. Приклад кадру Write Request у буфері каналу L2CAP (CID 0x0004):", size=12, bold=True, color=INK, anchor="start"))

    fy = 155
    # L2CAP Header (4 байти)
    p.append(rect(ox, fy, 155, 48, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    p.append(text(ox + 77, fy + 20, "L2CAP Header (4 B)", size=11, bold=True, color="#334155"))
    p.append(text(ox + 77, fy + 36, "Len (2 B) + CID 0x0004", size=9, color=MUTED))

    # ATT Opcode (1 байт)
    p.append(rect(ox + 162, fy, 115, 48, fill="#eef4ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(ox + 219, fy + 20, "Opcode (1 B)", size=11, bold=True, color=NEG))
    p.append(text(ox + 219, fy + 36, "0x12 (Write Req)", size=9, color=NEG))

    # Attribute Handle (2 байти)
    p.append(rect(ox + 284, fy, 145, 48, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(ox + 356, fy + 20, "Handle (2 B)", size=11, bold=True, color=FIELD))
    p.append(text(ox + 356, fy + 36, "0x0003 (Little-Endian)", size=9, color=FIELD))

    # Attribute Value (0..MTU-3 байтів)
    p.append(rect(ox + 436, fy, 284, 48, fill="#fdf4ff", stroke="#a855f7", sw=1.5, rx=4))
    p.append(text(ox + 578, fy + 20, "Attribute Value (0 .. MTU − 3 B)", size=11, bold=True, color="#9333ea"))
    p.append(text(ox + 578, fy + 36, "Корисне навантаження запису", size=9, color=MUTED))

    # Підсумок розмірів
    p.append(line(ox + 162, fy + 58, ox + 720, fy + 58, color=INK, sw=1.2))
    p.append(line(ox + 162, fy + 54, ox + 162, fy + 62, color=INK, sw=1.2))
    p.append(line(ox + 720, fy + 54, ox + 720, fy + 62, color=INK, sw=1.2))
    p.append(text(ox + 441, fy + 74, "Повний ATT PDU = макс. ATT_MTU (за замовчуванням 23 байти)", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "att-pdu-formats.svg"), W, H, *p,
           title="Формат бітів Opcode та компонування кадрів ATT PDU")


# ── 3. att-operations: 4 основні типи операцій ATT ─────────────────────────────
def fig_att_operations():
    W, H = 840, 380
    p = []

    col_w = 185
    gap = 15
    start_x = 30

    cols = [
        ("1. Request / Response", "#eef4ff", NEG, [
            ("Client → Server", "Read / Write Request"),
            ("Server → Client", "Read / Write Response"),
            ("Блокування", "Тільки 1 активний запит"),
            ("Гарантія", "Підтверджено на рівні ATT"),
        ]),
        ("2. Command (No Rsp)", "#fdf4ff", "#9333ea", [
            ("Client → Server", "Write Without Response"),
            ("Server → Client", "— (відповіді немає)"),
            ("Швидкість", "Не блокує чергу запитів"),
            ("Гарантія", "Тільки CRC Link Layer"),
        ]),
        ("3. Notification", "#eafaf0", FIELD, [
            ("Server → Client", "Handle Value Notification"),
            ("Client → Server", "— (підтвердження нема)"),
            ("Використання", "Потокові дані сенсорів"),
            ("Затримка", "Мінімальна енергія і час"),
        ]),
        ("4. Indication / Cfm", "#fff7ed", "#ea580c", [
            ("Server → Client", "Handle Value Indication"),
            ("Client → Server", "Handle Value Confirm"),
            ("Блокування", "Сервер чекає Confirm"),
            ("Гарантія", "Доставку підтверджено APP"),
        ]),
    ]

    for i, (title, bg, stroke_c, points) in enumerate(cols):
        cx = start_x + i * (col_w + gap)
        p.append(rect(cx, 30, col_w, 310, fill=bg, stroke=stroke_c, sw=1.6, rx=6))
        p.append(text(cx + col_w / 2, 54, title, size=11, bold=True, color=stroke_c))
        p.append(line(cx + 8, 68, cx + col_w - 8, 68, color=stroke_c, sw=1))

        sy = 85
        if i == 0:
            p.append(arrow(cx + 25, sy, cx + col_w - 25, sy + 18, color=stroke_c, sw=1.6))
            p.append(text(cx + col_w / 2, sy + 6, "Request", size=9, bold=True, color=stroke_c))
            p.append(arrow(cx + col_w - 25, sy + 38, cx + 25, sy + 56, color=stroke_c, sw=1.6))
            p.append(text(cx + col_w / 2, sy + 44, "Response", size=9, bold=True, color=stroke_c))
        elif i == 1:
            p.append(arrow(cx + 25, sy + 18, cx + col_w - 25, sy + 36, color=stroke_c, sw=1.6))
            p.append(text(cx + col_w / 2, sy + 24, "Write Command", size=9, bold=True, color=stroke_c))
            p.append(text(cx + col_w / 2, sy + 52, "(Без відповіді)", size=9, italic=True, color=MUTED))
        elif i == 2:
            p.append(arrow(cx + col_w - 25, sy + 18, cx + 25, sy + 36, color=stroke_c, sw=1.6))
            p.append(text(cx + col_w / 2, sy + 24, "Notification", size=9, bold=True, color=stroke_c))
            p.append(text(cx + col_w / 2, sy + 52, "(Без підтвердження)", size=9, italic=True, color=MUTED))
        elif i == 3:
            p.append(arrow(cx + col_w - 25, sy, cx + 25, sy + 18, color=stroke_c, sw=1.6))
            p.append(text(cx + col_w / 2, sy + 6, "Indication", size=9, bold=True, color=stroke_c))
            p.append(arrow(cx + 25, sy + 38, cx + col_w - 25, sy + 56, color=stroke_c, sw=1.6))
            p.append(text(cx + col_w / 2, sy + 44, "Confirmation", size=9, bold=True, color=stroke_c))

        ty = sy + 76
        for lbl, val in points:
            p.append(text(cx + 12, ty, lbl + ":", size=9, bold=True, color=INK, anchor="start"))
            p.append(text(cx + 12, ty + 14, val, size=9, color=MUTED, anchor="start"))
            ty += 34

    p.append(text(W / 2, H - 14, "Чотири патерни передачі даних ATT: баланс між швидкістю, надійністю та блокуванням черги",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "att-operations.svg"), W, H, *p,
           title="Чотири типи операцій протоколу ATT")


# ── 4. mtu-exchange-fragmentation: Процедура обміну MTU та фрагментація ────────
def fig_mtu_exchange_fragmentation():
    W, H = 840, 360
    p = []

    # Ліва половина: Exchange MTU handshake
    p.append(text(210, 30, "1. Процедура узгодження ATT MTU", size=12, bold=True, color=INK))

    cl_x, srv_x = 85, 335
    p.append(line(cl_x, 55, cl_x, 310, color=NEG, sw=1.8))
    p.append(line(srv_x, 55, srv_x, 310, color=FIELD, sw=1.8))
    p.append(text(cl_x, 48, "Клієнт", size=11, bold=True, color=NEG))
    p.append(text(srv_x, 48, "Сервер", size=11, bold=True, color=FIELD))

    # Запит
    p.append(arrow(cl_x, 85, srv_x, 115, color=NEG, sw=1.8))
    p.append(text((cl_x + srv_x) / 2, 92, "Exchange MTU Req (Client_Rx = 512)", size=9, bold=True, color=NEG))

    # Відповідь
    p.append(arrow(srv_x, 145, cl_x, 175, color=FIELD, sw=1.8))
    p.append(text((cl_x + srv_x) / 2, 152, "Exchange MTU Rsp (Server_Rx = 247)", size=9, bold=True, color=FIELD))

    # Результат
    p.append(rect(55, 205, 310, 60, fill="#f4f6f8", stroke=INK, sw=1.2, rx=5))
    p.append(text(210, 226, "Результат узгодження (Negotiated MTU):", size=10, bold=True, color=INK))
    p.append(text(210, 246, "MTU = min(512, 247) = 247 байтів", size=11, bold=True, color=POS))

    # Розділювач
    p.append(line(430, 25, 430, 325, color="#cbd5e1", sw=1.2, dash="4,4"))

    # Права половина: Сегментація L2CAP vs Link Layer Data Length (DLE)
    p.append(text(630, 30, "2. Фрагментація кадру ATT у Link Layer", size=12, bold=True, color=INK))

    rx = 455
    # Великий ATT PDU (247 B)
    p.append(rect(rx, 60, 350, 40, fill="#fdf4ff", stroke="#9333ea", sw=1.5, rx=4))
    p.append(text(rx + 175, 78, "ATT PDU (247 байтів)", size=11, bold=True, color="#9333ea"))
    p.append(text(rx + 175, 92, "1 B Opcode + 2 B Handle + 244 B Payload", size=9, color=MUTED))

    # Фрагментація на пакети LL (DLE = 27 або DLE = 251)
    p.append(arrow(rx + 175, 105, rx + 175, 130, color=MUTED, sw=1.4))
    p.append(text(rx + 175, 122, "Сегментація L2CAP / LL", size=9, color=MUTED))

    # Варіант А: Legacy LL (27 B макс на пакет ефіру)
    p.append(text(rx, 150, "А) Без DLE (LE Data Length = 27 байтів):", size=9, bold=True, color=POS, anchor="start"))
    for k in range(5):
        kx = rx + k * 56
        p.append(rect(kx, 160, 50, 30, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
        p.append(text(kx + 25, 179, "LL #%d" % (k + 1), size=9, color=POS))
    p.append(text(rx + 300, 179, "... (10 пакетів)", size=9, italic=True, color=MUTED))

    # Варіант Б: З DLE (LE Data Length = 251 байт)
    p.append(text(rx, 215, "Б) З DLE (LE Data Length = 251 байт):", size=9, bold=True, color=FIELD, anchor="start"))
    p.append(rect(rx, 228, 350, 34, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(rx + 175, 249, "1 єдиний пакет Link Layer (247 B + 4 B L2CAP Header)", size=9, bold=True, color=FIELD))

    p.append(text(W / 2, H - 14, "Обмін MTU збільшує корисне навантаження; DLE уникає фрагментації в ефірі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "mtu-exchange-fragmentation.svg"), W, H, *p,
           title="Процедура узгодження ATT MTU та фрагментація пакетів")


# ── 5. att-transaction-lock: Послідовне блокування черги запитів ATT ───────────
def fig_att_transaction_lock():
    W, H = 840, 340
    p = []

    # Часова шкала
    ox = 80
    oy = 50
    p.append(arrow(ox, oy, ox + 700, oy, color=INK, sw=1.6))
    p.append(text(ox + 715, oy + 4, "час t", size=11, color=INK, italic=True))

    # Перша транзакція (Успішна)
    t1_s = ox + 40
    t1_e = ox + 190
    p.append(rect(t1_s, oy + 25, 150, 48, fill="#eef4ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text((t1_s + t1_e) / 2, oy + 45, "Read Request #1", size=10, bold=True, color=NEG))
    p.append(text((t1_s + t1_e) / 2, oy + 60, "Очікування відповіді", size=9, color=MUTED))

    p.append(line(t1_s, oy - 6, t1_s, oy + 6, color=INK, sw=1.4))
    p.append(line(t1_e, oy - 6, t1_e, oy + 6, color=INK, sw=1.4))
    p.append(text(t1_e, oy + 92, "Read Response", size=9, bold=True, color=FIELD))
    p.append(arrow(t1_e, oy + 80, t1_e, oy + 12, color=FIELD, sw=1.4))

    # Спроба відправити під час очікування (Заборонено!)
    blk_x = ox + 100
    p.append(rect(blk_x, oy + 110, 180, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(blk_x + 90, oy + 128, "Write Req #2 ЗАБЛОКОВАНО", size=9, bold=True, color=POS))
    p.append(text(blk_x + 90, oy + 142, "Лише 1 Request у польоті!", size=9, color=POS))
    p.append(arrow(blk_x + 90, oy + 110, blk_x + 90, oy + 76, color=POS, sw=1.4))

    # Друга транзакція (Таймаут 30 секунд — критичний збій!)
    t2_s = ox + 260
    t2_e = ox + 550
    p.append(rect(t2_s, oy + 25, 290, 48, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=4))
    p.append(text((t2_s + t2_e) / 2, oy + 45, "Write Request #2 (Сервер завис / мовчить)", size=10, bold=True, color="#ea580c"))
    p.append(text((t2_s + t2_e) / 2, oy + 60, "Таймер транзакції ATT (30.0 с)", size=9, bold=True, color=POS))

    p.append(line(t2_s, oy - 6, t2_s, oy + 6, color=INK, sw=1.4))
    p.append(line(t2_e, oy - 6, t2_e, oy + 6, color=POS, sw=2))

    # Фатальний таймаут
    p.append(rect(t2_e - 30, oy + 100, 190, 52, fill="#fdecea", stroke=POS, sw=1.8, rx=5))
    p.append(text(t2_e + 65, oy + 120, "ATT TIMEOUT (30 s)", size=10, bold=True, color=POS))
    p.append(text(t2_e + 65, oy + 138, "Обов'язковий розрив з'єднання", size=9, color=POS))
    p.append(arrow(t2_e, oy + 10, t2_e, oy + 95, color=POS, sw=1.8))

    # Порівняння: EATT (Bluetooth 5.2)
    p.append(rect(ox + 40, oy + 195, 640, 55, fill="#f8fafc", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(ox + 360, oy + 215, "Рішення в Bluetooth 5.2: Enhanced ATT (EATT)", size=11, bold=True, color=FIELD))
    p.append(text(ox + 360, oy + 233, "Дозволяє паралельні запити через динамічні канали L2CAP (Credit-Based Flow Control)", size=9, color=MUTED))

    p.append(text(W / 2, H - 14, "Сувора черга транзакцій ATT: неповернення Response за 30 с знищує радіоз'єднання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "att-transaction-lock.svg"), W, H, *p,
           title="Послідовне блокування транзакцій ATT і таймаут 30 секунд")


# ── 6. att-vs-gatt-mapping: Зв'язок між GATT-ієрархією і таблицею ATT ─────────
def fig_att_vs_gatt_mapping():
    W, H = 840, 360
    p = []

    # Ліва колонка: Ієрархічне дерево GATT
    gx = 180
    p.append(text(gx, 30, "GATT: Логічне дерево об'єктів", size=12, bold=True, color=NEG))

    # Service Box
    p.append(rect(40, 55, 280, 240, fill="#eef4ff", stroke=NEG, sw=1.6, rx=6))
    p.append(text(gx, 75, "Service: Heart Rate (0x180D)", size=11, bold=True, color=NEG))

    # Characteristic Box
    p.append(rect(55, 95, 250, 185, fill="#ffffff", stroke="#3b82f6", sw=1.4, rx=4))
    p.append(text(gx, 115, "Characteristic: HR Measurement (0x2A37)", size=10, bold=True, color="#1d4ed8"))
    p.append(text(gx, 130, "Властивості: Notify | Значення: [0x00, 0x48]", size=9, color=MUTED))

    # Descriptor Box
    p.append(rect(70, 150, 220, 115, fill="#f8fafc", stroke="#60a5fa", sw=1.2, rx=4))
    p.append(text(gx, 170, "Descriptors (Дескриптори):", size=9, bold=True, color=INK))
    p.append(text(gx, 195, "• CCCD (0x2902) — увімкн. Notify", size=9, color=FIELD))
    p.append(text(gx, 215, "• User Description (0x2901)", size=9, color=MUTED))
    p.append(text(gx, 235, "  «Heart Rate Pulse Sensor»", size=9, italic=True, color=MUTED))

    # Центральна стрілка мапінгу
    p.append(arrow(335, 170, 425, 170, color=POS, sw=2.2))
    p.append(text(380, 155, "Трансляція в", size=9, bold=True, color=POS))
    p.append(text(380, 185, "рядки ATT", size=9, bold=True, color=POS))

    # Права колонка: Пласка таблиця Handle в ATT
    ax = 620
    p.append(text(ax, 30, "ATT: Пласка адресація за Handle (1..N)", size=12, bold=True, color=FIELD))

    rows = [
        ("0x0010", "0x2800 (Primary Service)", "0x180D (Heart Rate Service)"),
        ("0x0011", "0x2803 (Char Declaration)", "Props: 0x10, Handle: 0x0012, UUID: 0x2A37"),
        ("0x0012", "0x2A37 (HR Measurement Value)", "[0x00, 0x48] (72 bpm)"),
        ("0x0013", "0x2902 (Client Char Config)", "0x0001 (Notify Enabled)"),
        ("0x0014", "0x2901 (Char User Description)", "«Heart Rate Pulse Sensor»"),
    ]

    for i, (hdl, uid, val) in enumerate(rows):
        ry = 55 + i * 48
        p.append(rect(440, ry, 360, 42, fill="#eafaf0" if i == 0 or i == 1 else "#ffffff", stroke=FIELD, sw=1.2, rx=4))
        p.append(text(480, ry + 18, "Hdl: " + hdl, size=10, bold=True, color=POS))
        p.append(text(630, ry + 18, "Type: " + uid, size=9, bold=True, color=NEG))
        p.append(text(600, ry + 34, "Val: " + val, size=9, color=MUTED))

    p.append(text(W / 2, H - 14, "GATT є семантичною ієрархією правил над пласкою таблицею 16-бітних дескрипторів ATT",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "att-vs-gatt-mapping.svg"), W, H, *p,
           title="Відображення ієрархії GATT у пласку структуру атрибутів ATT")


if __name__ == "__main__":
    fig_att_architecture()
    fig_att_pdu_formats()
    fig_att_operations()
    fig_mtu_exchange_fragmentation()
    fig_att_transaction_lock()
    fig_att_vs_gatt_mapping()
    print("All figures generated successfully.")
