# -*- coding: utf-8 -*-
"""Генератор векторних схем для теми smbus-protocol."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, FILL, INK, LINE, MUTED, POS, NEG, FIELD,
    arrow, circle, esc, fitbox, line, mtext, rect, text, textbox
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

def render(w, h, elements):
    """Скласти SVG-документ з маркером для стрілок."""
    defs = (
        '  <defs>\n'
        '    <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        '      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n'
        '    </marker>\n'
        '  </defs>\n' % LINE
    )
    body = "\n".join(elements)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
        '%s%s\n</svg>' % (w, h, w, h, defs, body)
    )

def save(fname, w, h, el):
    path = os.path.join(OUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(render(w, h, el))
    print(f"Згенеровано: {fname} ({w}x{h})")


# ── 1. smbus-architecture.svg ────────────────────────────────────────────────
def fig_architecture():
    w, h = 880, 360
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    # Живлення та резистори підтяжки вгорі
    p.append(rect(30, 20, 820, 50, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(440, 42, "Шина живлення VDD (+3.3 В / +5.0 В)", size=13, color=INK, bold=True))
    
    # 3 резистори підтяжки
    r_x = [270, 450, 630]
    labels_r = ["R_pullup (SCL)", "R_pullup (SDA)", "R_pullup (ALERT#)"]
    for x, lbl in zip(r_x, labels_r):
        p.append(line(x, 70, x, 85, color=LINE, sw=1.5))
        p.append(rect(x - 18, 85, 36, 32, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
        p.append(text(x, 105, "R_p", size=11, color="#b45309", bold=True))
        p.append(line(x, 117, x, 140, color=LINE, sw=1.5))
        p.append(text(x + 5, 130, lbl, size=9.5, color=MUTED, anchor="start"))

    # Горизонтальні сигнальні шини
    # SCL
    p.append(line(110, 145, 840, 145, color=NEG, sw=2.5))
    p.append(text(100, 149, "SCL", size=13, color=NEG, bold=True, anchor="end"))
    # SDA
    p.append(line(110, 175, 840, 175, color=FIELD, sw=2.5))
    p.append(text(100, 179, "SDA", size=13, color=FIELD, bold=True, anchor="end"))
    # SMBALERT#
    p.append(line(110, 205, 840, 205, color=POS, sw=2.5))
    p.append(text(100, 209, "SMBALERT#", size=11.5, color=POS, bold=True, anchor="end"))

    # Вузли з'єднання з шинами
    p.append(circle(270, 145, 3.5, fill=NEG, stroke=NEG))
    p.append(circle(450, 175, 3.5, fill=FIELD, stroke=FIELD))
    p.append(circle(630, 205, 3.5, fill=POS, stroke=POS))

    # Пристрої знизу
    devices = [
        ("SMBus Host Controller\n(Південний міст / PCH / MCU)", 180, 280, 200, 70, "#eff6ff", "#3b82f6"),
        ("Smart Battery\n(SBS Газовий лічильник / BMS)", 410, 280, 180, 70, "#f0fdf4", "#22c55e"),
        ("Термодавач LM75\n(Моніторинг температури CPU)", 605, 280, 170, 70, "#fef2f2", "#ef4444"),
        ("VRM / PMBus\n(ШІМ живлення ядра)", 780, 280, 130, 70, "#faf5ff", "#a855f7")
    ]

    for title, cx, cy, bw, bh, fcol, scol in devices:
        bx = cx - bw / 2
        by = cy - bh / 2
        p.append(fitbox(bx, by, bw, bh, title, size=11.5, bold=True, fill=fcol, stroke=scol, sw=1.5, pad=6))
        
        # Відводи до шин
        p.append(circle(cx - 25, 145, 2.5, fill=NEG, stroke=NEG))
        p.append(line(cx - 25, 145, cx - 25, by, color=NEG, sw=1.5))
        
        p.append(circle(cx, 175, 2.5, fill=FIELD, stroke=FIELD))
        p.append(line(cx, 175, cx, by, color=FIELD, sw=1.5))

        if cx != 780:  # VRM без SMBALERT
            p.append(circle(cx + 25, 205, 2.5, fill=POS, stroke=POS))
            p.append(line(cx + 25, 205, cx + 25, by, color=POS, sw=1.5))

    save("smbus-architecture.svg", w, h, p)


# ── 2. voltage-timing-comparison.svg ─────────────────────────────────────────
def fig_comparison():
    w, h = 820, 370
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    # Заголовок блоків
    p.append(fitbox(40, 20, 350, 40, "Стандарт I2C (Philips / NXP)", size=14, bold=True, fill="#f1f5f9", stroke="#94a3b8"))
    p.append(fitbox(430, 20, 350, 40, "Специфікація SMBus 2.0 / 3.0 (Intel / SBS)", size=14, bold=True, fill="#eff6ff", stroke="#3b82f6"))

    # Блок I2C: Напруги та Таймінги
    p.append(rect(40, 75, 350, 275, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))
    p.append(text(215, 100, "Фізичні та часові параметри I2C", size=12.5, bold=True, color=INK))
    
    i2c_rows = [
        ("Рівні напруги:", "Відносні до VDD"),
        ("  V_IL (логічний 0):", "≤ 0.3 · VDD  (0.99 В при 3.3 В)"),
        ("  V_IH (логічна 1):", "≥ 0.7 · VDD  (2.31 В при 3.3 В)"),
        ("Тайм-аут SCL:", "Відсутній (дозволено DC / 0 Гц)"),
        ("Мін. частота f_MIN:", "0 кГц (необмежене утримання)"),
        ("Макс. частота f_MAX:", "100 кГц / 400 кГц / 1 МГц / 3.4 МГц"),
        ("Струм підтяжки:", "до 3.0 мА (V_OL = 0.4 В)"),
        ("Контроль помилок:", "Лише біт ACK/NACK (без CRC)"),
        ("Переривання:", "Немає окремої лінії в стандарті")
    ]
    for i, (k, v) in enumerate(i2c_rows):
        y = 125 + i * 23
        p.append(text(55, y, k, size=11, bold=True, color="#475569", anchor="start"))
        p.append(text(180, y, v, size=11, color=INK, anchor="start"))

    # Блок SMBus: Напруги та Таймінги
    p.append(rect(430, 75, 350, 275, fill="#f8fafc", stroke="#bfdbfe", sw=1.5, rx=8))
    p.append(text(605, 100, "Жорсткі обмеження SMBus", size=12.5, bold=True, color="#1d4ed8"))

    smbus_rows = [
        ("Рівні напруги:", "Фіксовані пороги (SMBus 2.0)"),
        ("  V_IL (логічний 0):", "≤ 0.8 В (фіксовано для 3–5 В)"),
        ("  V_IH (логічна 1):", "≥ 2.1 В (фіксовано для 3–5 В)"),
        ("Тайм-аут t_TIMEOUT:", "25–35 мс (апаратне скидання шини)"),
        ("Мін. частота f_MIN:", "10 кГц (заборона зависань)"),
        ("Макс. частота f_MAX:", "100 кГц (SMBus 2.0) / 1 МГц (3.0)"),
        ("Струм драйвера:", "350 мкА – 4 мА (енергоощадність)"),
        ("Контроль помилок:", "Обов'язковий PEC (CRC-8 x⁸+x²+x+1)"),
        ("Переривання:", "Лінія SMBALERT# + опитування ARA")
    ]
    for i, (k, v) in enumerate(smbus_rows):
        y = 125 + i * 23
        p.append(text(445, y, k, size=11, bold=True, color="#1e40af", anchor="start"))
        p.append(text(585, y, v, size=11, color=INK, anchor="start"))

    save("voltage-timing-comparison.svg", w, h, p)


# ── 3. protocols-overview.svg ────────────────────────────────────────────────
def fig_protocols():
    w, h = 880, 460
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    p.append(text(440, 25, "Стандартизовані формати транзакцій SMBus", size=14, bold=True, color=INK))

    # Легенда
    p.append(rect(30, 40, 820, 64, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    
    leg_row1 = [
        ("S", 24, "Старт", "#fef08a", "#ca8a04", 45),
        ("Sr", 26, "Повторний старт", "#fed7aa", "#ea580c", 195),
        ("Addr", 46, "Адреса веденого", "#dbeafe", "#2563eb", 410),
        ("Cmd", 42, "Код команди", "#e0e7ff", "#4f46e5", 640)
    ]
    for tag, rw, desc, fcol, scol, lx in leg_row1:
        p.append(rect(lx, 46, rw, 20, fill=fcol, stroke=scol, sw=1, rx=3))
        p.append(text(lx + rw / 2, 60, tag, size=10, bold=True, color=INK))
        p.append(text(lx + rw + 8, 60, desc, size=10.5, color=MUTED, anchor="start"))

    leg_row2 = [
        ("Data", 42, "Байт даних", "#dcfce7", "#16a34a", 45),
        ("Count", 50, "Лічильник N", "#fde047", "#ca8a04", 230),
        ("A / N", 42, "ACK (0) / NACK (1)", "#f1f5f9", "#64748b", 430),
        ("P", 24, "Стоп", "#fee2e2", "#dc2626", 670)
    ]
    for tag, rw, desc, fcol, scol, lx in leg_row2:
        p.append(rect(lx, 74, rw, 20, fill=fcol, stroke=scol, sw=1, rx=3))
        p.append(text(lx + rw / 2, 88, tag, size=10, bold=True, color=INK))
        p.append(text(lx + rw + 8, 88, desc, size=10.5, color=MUTED, anchor="start"))

    def draw_packet(y, name, cells):
        p.append(text(35, y + 15, name, size=11.5, bold=True, color=INK, anchor="start"))
        cx = 245
        for tag, wcell, fcol, scol in cells:
            p.append(rect(cx, y, wcell, 24, fill=fcol, stroke=scol, sw=1.2, rx=3))
            p.append(text(cx + wcell / 2, y + 16, tag, size=10, bold=True, color=INK))
            cx += wcell + 3

    # 1. Quick Command
    draw_packet(118, "Quick Command:", [
        ("S", 22, "#fef08a", "#ca8a04"),
        ("Slave Addr + R/W", 130, "#dbeafe", "#2563eb"),
        ("A", 22, "#f1f5f9", "#64748b"),
        ("P", 22, "#fee2e2", "#dc2626")
    ])

    # 2. Write Byte
    draw_packet(158, "Write Byte:", [
        ("S", 22, "#fef08a", "#ca8a04"),
        ("Slave Addr + W", 110, "#dbeafe", "#2563eb"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("Command Code", 110, "#e0e7ff", "#4f46e5"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("Data Byte", 85, "#dcfce7", "#16a34a"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("P", 22, "#fee2e2", "#dc2626")
    ])

    # 3. Read Word
    draw_packet(198, "Read Word:", [
        ("S", 20, "#fef08a", "#ca8a04"),
        ("Addr + W", 65, "#dbeafe", "#2563eb"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("Command", 75, "#e0e7ff", "#4f46e5"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("Sr", 22, "#fed7aa", "#ea580c"),
        ("Addr + R", 65, "#dbeafe", "#2563eb"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("DataLow", 70, "#dcfce7", "#16a34a"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("DataHigh", 70, "#dcfce7", "#16a34a"),
        ("N", 18, "#fee2e2", "#dc2626"),
        ("P", 20, "#fee2e2", "#dc2626")
    ])

    # 4. Process Call
    draw_packet(238, "Process Call:", [
        ("S", 18, "#fef08a", "#ca8a04"),
        ("Addr+W", 55, "#dbeafe", "#2563eb"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("Cmd", 45, "#e0e7ff", "#4f46e5"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("WrLow", 55, "#dcfce7", "#16a34a"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("WrHigh", 55, "#dcfce7", "#16a34a"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("Sr", 20, "#fed7aa", "#ea580c"),
        ("Addr+R", 55, "#dbeafe", "#2563eb"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("RdLow", 55, "#dcfce7", "#16a34a"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("RdHigh", 55, "#dcfce7", "#16a34a"),
        ("N", 16, "#fee2e2", "#dc2626"),
        ("P", 18, "#fee2e2", "#dc2626")
    ])

    # 5. Block Write (з Byte Count N)
    draw_packet(278, "Block Write (N байт):", [
        ("S", 20, "#fef08a", "#ca8a04"),
        ("Addr + W", 65, "#dbeafe", "#2563eb"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("Command", 75, "#e0e7ff", "#4f46e5"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("Count N", 65, "#fde047", "#ca8a04"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("Data 1", 55, "#dcfce7", "#16a34a"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("...", 35, "#f8fafc", "#94a3b8"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("Data N", 55, "#dcfce7", "#16a34a"),
        ("A", 18, "#f1f5f9", "#64748b"),
        ("P", 20, "#fee2e2", "#dc2626")
    ])

    # 6. Block Read
    draw_packet(318, "Block Read:", [
        ("S", 18, "#fef08a", "#ca8a04"),
        ("Addr+W", 55, "#dbeafe", "#2563eb"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("Cmd", 45, "#e0e7ff", "#4f46e5"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("Sr", 20, "#fed7aa", "#ea580c"),
        ("Addr+R", 55, "#dbeafe", "#2563eb"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("Count N", 60, "#fde047", "#ca8a04"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("Data 1", 50, "#dcfce7", "#16a34a"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("...", 30, "#f8fafc", "#94a3b8"),
        ("A", 16, "#f1f5f9", "#64748b"),
        ("Data N", 50, "#dcfce7", "#16a34a"),
        ("N", 16, "#fee2e2", "#dc2626"),
        ("P", 18, "#fee2e2", "#dc2626")
    ])

    # Пояснення внизу
    p.append(rect(30, 370, 820, 68, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(440, 394, "Усі багатобайтові дані передаються у форматі Little-Endian: спочатку молодший байт (DataLow), потім старший (DataHigh).", size=11, color=INK))
    p.append(text(440, 418, "Поле Byte Count явно вказує довжину блоку (від 1 до 32 байтів у SMBus 2.0 / до 255 у 3.0), що дозволяє пряму роботу з DMA.", size=11, color="#2563eb"))

    save("protocols-overview.svg", w, h, p)


# ── 4. pec-crc8-packet.svg ───────────────────────────────────────────────────
def fig_pec():
    w, h = 820, 330
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    p.append(text(410, 25, "Контроль цілісності транзакції: байт PEC (Packet Error Checking)", size=14, bold=True, color=INK))

    # Кадр Write Word з PEC
    y_pkt = 65
    cx = 50
    cells = [
        ("S", 25, "#fef08a", "#ca8a04"),
        ("Slave Addr + W (0x5A)", 140, "#dbeafe", "#2563eb"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("Cmd (0x06)", 80, "#e0e7ff", "#4f46e5"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("DataLow (0x12)", 100, "#dcfce7", "#16a34a"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("DataHigh (0x34)", 105, "#dcfce7", "#16a34a"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("PEC CRC-8 (0x4E)", 125, "#fce7f3", "#db2777"),
        ("A", 20, "#f1f5f9", "#64748b"),
        ("P", 25, "#fee2e2", "#dc2626")
    ]

    for tag, wcell, fcol, scol in cells:
        p.append(rect(cx, y_pkt, wcell, 30, fill=fcol, stroke=scol, sw=1.5, rx=4))
        p.append(text(cx + wcell / 2, y_pkt + 20, tag, size=10.5, bold=True, color=INK))
        cx += wcell + 2

    # Охоплення CRC дужкою/стрілками
    p.append(line(77, 105, 77, 125, color="#db2777", sw=1.5))
    p.append(line(77, 125, 620, 125, color="#db2777", sw=1.5))
    p.append(line(620, 105, 620, 125, color="#db2777", sw=1.5))
    p.append(arrow(350, 125, 350, 145, color="#db2777", sw=1.8))

    # Блок обчислювача CRC
    p.append(rect(180, 150, 460, 80, fill="#fdf2f8", stroke="#f472b6", sw=1.5, rx=8))
    p.append(text(410, 172, "Апаратний або програмний поліном CRC-8", size=12.5, bold=True, color="#9d174d"))
    p.append(text(410, 194, "Поліном: C(x) = x⁸ + x² + x¹ + 1   (двійкове 100000111b = 0x107 / 0x07)", size=11, bold=True, color=INK))
    p.append(text(410, 214, "Початкове значення залишку: 0x00 · Вхідний потік: адреси, команди, дані", size=10.5, color=MUTED))

    # Стрілка від обчислювача до байта PEC
    p.append(arrow(550, 150, 640, 100, color="#db2777", sw=1.8))

    # Текстовий блок знизу
    p.append(rect(50, 245, 720, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(410, 268, "• При читанні з Repeated START адреса веденого з бітом R (0x5B) повторно входить до потоку CRC!", size=10.5, bold=True, color="#b91c1c"))
    p.append(text(410, 287, "• Якщо ведений отримує некоректний PEC при записі, він зобов'язаний виставити NACK і відкинути дані.", size=10.5, color=INK))
    p.append(text(410, 303, "• Якщо хост фіксує невідповідність PEC при читанні, транзакція відкидається без пошкодження стану ОС.", size=10.5, color=INK))

    save("pec-crc8-packet.svg", w, h, p)


# ── 5. smbalert-ara-arbitration.svg ──────────────────────────────────────────
def fig_smbalert():
    w, h = 820, 380
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    p.append(text(410, 25, "Протокол сповіщення хоста: лінія SMBALERT# та арбітраж ARA", size=14, bold=True, color=INK))

    # 4 послідовні кроки
    steps = [
        ("Крок 1: Аварійне переривання веденого", [
            "Давач заряду (адреса 0x16) фіксує перегрів або падіння напруги.",
            "Давач притягує лінію SMBALERT# до нуля (активний рівень 0 В).",
            "Хост фіксує спадний фронт на вході зовнішнього переривання."
        ], "#eff6ff", "#3b82f6"),
        ("Крок 2: Запит відповіді на тривогу (ARA)", [
            "Хост надсилає загальний широкомовний запит:",
            "START → Alert Response Address (0001 100b = 0x0C) + R (байт 0x19).",
            "Усі пристрої з активним SMBALERT# слухають цю адресу і готують відповідь."
        ], "#f0fdf4", "#22c55e"),
        ("Крок 3: Побітовий арбітраж на шині SDA", [
            "Кожен збуджений ведений передає власну 7-бітну адресу на лінію SDA.",
            "Пристрій з найменшою адресою (наприклад, 0x16 проти 0x48) перемагає,",
            "оскільки його нульові біти домінують над одиницями суперників."
        ], "#fefce8", "#eab308"),
        ("Крок 4: Завершення та зняття сигналу", [
            "Хост надсилає ACK переможцю та дізнається точну адресу винуватця (0x16).",
            "Переможець відпускає лінію SMBALERT#.",
            "Якщо SMBALERT# лишається низьким, хост повторює читання ARA для інших."
        ], "#fdf2f8", "#ec4899")
    ]

    col_w = 360
    col_h = 145
    positions = [
        (40, 50),
        (420, 50),
        (40, 210),
        (420, 210)
    ]

    for (x, y), (title, lines_text, fcol, scol) in zip(positions, steps):
        p.append(rect(x, y, col_w, col_h, fill=fcol, stroke=scol, sw=1.5, rx=6))
        p.append(text(x + col_w / 2, y + 22, title, size=11.5, bold=True, color=INK))
        for idx, ln in enumerate(lines_text):
            p.append(text(x + 12, y + 50 + idx * 24, "• " + ln, size=10, color=INK, anchor="start"))

    # Стрілки переходу між кроками
    p.append(arrow(220, 195, 220, 210, color=MUTED, sw=1.5))
    p.append(arrow(400, 120, 420, 120, color=MUTED, sw=1.5))
    p.append(arrow(600, 195, 600, 210, color=MUTED, sw=1.5))

    save("smbalert-ara-arbitration.svg", w, h, p)


if __name__ == "__main__":
    fig_architecture()
    fig_comparison()
    fig_protocols()
    fig_pec()
    fig_smbalert()
