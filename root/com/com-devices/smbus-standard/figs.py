# -*- coding: utf-8 -*-
"""Генератор векторних схем для теми smbus."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, FILL, INK, LINE, MUTED, POS, NEG, FIELD, BG,
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
        '    <marker id="arrow-neg" viewBox="0 0 10 10" refX="7" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        '      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n'
        '    </marker>\n'
        '  </defs>\n' % (LINE, NEG)
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


# ── 1. smbus-system-topology.svg ───────────────────────────────────────────────
def fig_system_topology():
    w, h = 920, 420
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    # Живлення та резистори підтяжки вгорі
    p.append(rect(40, 20, 840, 45, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(460, 45, "Системна лінія живлення VDD (+3.3 В / +5.0 В)", size=13, color=INK, bold=True))

    # Резистори підтяжки
    r_coords = [
        (260, "R_p (SCL)", NEG),
        (460, "R_p (SDA)", FIELD),
        (660, "R_p (ALERT#)", POS)
    ]
    for x, lbl, col in r_coords:
        p.append(line(x, 65, x, 85, color=LINE, sw=1.5))
        p.append(rect(x - 18, 85, 36, 30, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
        p.append(text(x, 104, "R_p", size=11, color="#b45309", bold=True))
        p.append(line(x, 115, x, 140, color=LINE, sw=1.5))
        p.append(text(x + 8, 130, lbl, size=10, color=col, anchor="start", bold=True))

    # Горизонтальні шини
    # SCL
    p.append(line(100, 145, 870, 145, color=NEG, sw=2.5))
    p.append(text(90, 149, "SCL", size=13, color=NEG, bold=True, anchor="end"))
    # SDA
    p.append(line(100, 180, 870, 180, color=FIELD, sw=2.5))
    p.append(text(90, 184, "SDA", size=13, color=FIELD, bold=True, anchor="end"))
    # SMBALERT#
    p.append(line(100, 215, 870, 215, color=POS, sw=2.5))
    p.append(text(90, 219, "SMBALERT#", size=11.5, color=POS, bold=True, anchor="end"))

    # Вузли з'єднання з шинами
    p.append(circle(260, 145, 3.5, fill=NEG, stroke=NEG))
    p.append(circle(460, 180, 3.5, fill=FIELD, stroke=FIELD))
    p.append(circle(660, 215, 3.5, fill=POS, stroke=POS))

    # Пристрої знизу
    devs = [
        ("SMBus Host Controller\n(PCH / EC / BMC)\n[Керування та опитування]", 160, 330, 200, 95, "#eff6ff", "#3b82f6"),
        ("Smart Battery (SBS)\nГазовий лічильник bq40z50\n[Заряд, струм, ємність]", 390, 330, 190, 95, "#f0fdf4", "#22c55e"),
        ("Термодавач LM75 / TMP75\nМоніторинг температури CPU\n[Пороги спрацювання OS/ALERT#]", 615, 330, 200, 95, "#fef2f2", "#ef4444"),
        ("PMBus VRM / POL\nДжерело живлення\n[Телеметрія струму]", 815, 330, 150, 95, "#faf5ff", "#a855f7")
    ]

    for title, cx, cy, bw, bh, fcol, scol in devs:
        tb, _, _ = textbox(cx, cy, title, size=11, pad=8, fill=fcol, stroke=scol, sw=1.5, min_w=bw)
        p.append(tb)

    # Вертикальні з'єднання до пристроїв
    # Host: SCL, SDA, SMBALERT# (вхід)
    p.append(line(120, 145, 120, 282, color=NEG, sw=1.5))
    p.append(circle(120, 145, 3, fill=NEG, stroke=NEG))
    p.append(line(160, 180, 160, 282, color=FIELD, sw=1.5))
    p.append(circle(160, 180, 3, fill=FIELD, stroke=FIELD))
    p.append(line(200, 215, 200, 282, color=POS, sw=1.5))
    p.append(circle(200, 215, 3, fill=POS, stroke=POS))

    # Smart Battery: SCL, SDA, SMBALERT#
    p.append(line(350, 145, 350, 282, color=NEG, sw=1.5))
    p.append(circle(350, 145, 3, fill=NEG, stroke=NEG))
    p.append(line(390, 180, 390, 282, color=FIELD, sw=1.5))
    p.append(circle(390, 180, 3, fill=FIELD, stroke=FIELD))
    p.append(line(430, 215, 430, 282, color=POS, sw=1.5))
    p.append(circle(430, 215, 3, fill=POS, stroke=POS))

    # Temp Sensor: SCL, SDA, SMBALERT#
    p.append(line(575, 145, 575, 282, color=NEG, sw=1.5))
    p.append(circle(575, 145, 3, fill=NEG, stroke=NEG))
    p.append(line(615, 180, 615, 282, color=FIELD, sw=1.5))
    p.append(circle(615, 180, 3, fill=FIELD, stroke=FIELD))
    p.append(line(655, 215, 655, 282, color=POS, sw=1.5))
    p.append(circle(655, 215, 3, fill=POS, stroke=POS))

    # PMBus VRM: SCL, SDA, SMBALERT#
    p.append(line(780, 145, 780, 282, color=NEG, sw=1.5))
    p.append(circle(780, 145, 3, fill=NEG, stroke=NEG))
    p.append(line(815, 180, 815, 282, color=FIELD, sw=1.5))
    p.append(circle(815, 180, 3, fill=FIELD, stroke=FIELD))
    p.append(line(850, 215, 850, 282, color=POS, sw=1.5))
    p.append(circle(850, 215, 3, fill=POS, stroke=POS))

    save("smbus-system-topology.svg", w, h, p)


# ── 2. smbus-timing-timeout.svg ───────────────────────────────────────────────
def fig_timing_timeout():
    w, h = 880, 340
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    # Заголовок часової шкали
    p.append(text(60, 40, "SCL", size=14, color=NEG, bold=True, anchor="start"))
    p.append(text(60, 140, "SDA", size=14, color=FIELD, bold=True, anchor="start"))

    # Рівні сигналів SCL (нормальні імпульси -> застрягання в нулі -> таймаут -> скидання)
    # Нормальні імпульси: 0-250px
    p.append(line(120, 40, 160, 40, color=NEG, sw=2))      # High
    p.append(line(160, 40, 160, 80, color=NEG, sw=2))      # Fall
    p.append(line(160, 80, 200, 80, color=NEG, sw=2))      # Low
    p.append(line(200, 80, 200, 40, color=NEG, sw=2))      # Rise
    p.append(line(200, 40, 240, 40, color=NEG, sw=2))      # High
    p.append(line(240, 40, 240, 80, color=NEG, sw=2))      # Fall
    # Зависання в нулі від x=240 до x=660
    p.append(line(240, 80, 660, 80, color=POS, sw=2.5))    # Low stuck!
    # Відновлення: підтяжка до High на x=660
    p.append(line(660, 80, 680, 40, color=NEG, sw=2, dash="3,3")) # Rise back via R_pullup
    p.append(line(680, 40, 840, 40, color=NEG, sw=2))      # High idle

    # Лінія SDA (утримується веденим у нулі, а потім відпускається в Hi-Z)
    p.append(line(120, 140, 180, 140, color=FIELD, sw=2))
    p.append(line(180, 140, 180, 180, color=FIELD, sw=2))
    p.append(line(180, 180, 660, 180, color=POS, sw=2.5))  # Slave holds 0
    p.append(line(660, 180, 680, 140, color=FIELD, sw=2, dash="3,3")) # Released to Hi-Z
    p.append(line(680, 140, 840, 140, color=FIELD, sw=2))  # High idle

    # Інтервал таймауту t_TIMEOUT
    p.append(line(240, 20, 240, 210, color=MUTED, sw=1, dash="4,4"))
    p.append(line(660, 20, 660, 210, color=MUTED, sw=1, dash="4,4"))

    # Стрілка вимірювання інтервалу (розділена, щоб не перетинати рамку напису)
    p.append(arrow(350, 105, 240, 105, color=POS, sw=1.8))
    p.append(arrow(550, 105, 660, 105, color=POS, sw=1.8))
    p.append(rect(360, 92, 180, 26, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(text(450, 110, "t_TIMEOUT = 25–35 мс", size=11, color=POS, bold=True))

    # Позначення подій знизу
    ev1, _, _ = textbox(240, 260, "Збій веденого:\nутримання лінії SCL/SDA\nу стані логічного 0", size=11, pad=6, fill="#fff7ed", stroke="#f97316", sw=1.2)
    ev2, _, _ = textbox(660, 260, "Апаратне скидання:\nкінцевий автомат скидається,\nтранзистори в Hi-Z", size=11, pad=6, fill="#eff6ff", stroke="#3b82f6", sw=1.2)
    ev3, _, _ = textbox(760, 130, "Шина вільна (IDLE)\nХост відновлює обмін", size=10.5, pad=6, fill="#f0fdf4", stroke="#22c55e", sw=1.2)

    p.append(ev1)
    p.append(ev2)
    p.append(ev3)

    save("smbus-timing-timeout.svg", w, h, p)


# ── 3. ara-arbitration-sequence.svg ───────────────────────────────────────────
def fig_ara_arbitration():
    w, h = 900, 380
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    # 1. Спадання SMBALERT#
    p.append(text(50, 45, "SMBALERT#", size=12.5, color=POS, bold=True, anchor="start"))
    p.append(line(160, 30, 220, 30, color=POS, sw=2))
    p.append(line(220, 30, 220, 60, color=POS, sw=2))
    p.append(line(220, 60, 720, 60, color=POS, sw=2))
    p.append(line(720, 60, 740, 30, color=POS, sw=2, dash="3,3"))
    p.append(line(740, 30, 860, 30, color=POS, sw=2))

    # Пояснення спаду
    p.append(text(220, 85, "Подія у веденого:\nпереривання ALERT# -> 0", size=10, color=POS, bold=True, anchor="middle"))

    # 2. Транзакція Хоста до ARA
    p.append(text(50, 140, "Транзакція\nХоста (SDA)", size=12.5, color=INK, bold=True, anchor="start"))

    # Блоки транзакції
    blocks = [
        ("S", 230, 35, "#fee2e2", "#ef4444", "СТАРТ"),
        ("ARA Адреса: 0001 100b (0x0C)", 325, 155, "#dbeafe", "#3b82f6", "Адреса сповіщення"),
        ("Rd (1)", 420, 35, "#fef3c7", "#d97706", "Читання"),
        ("ACK", 455, 35, "#dcfce7", "#22c55e", "Підтвердження"),
        ("Фаза Арбітражу (Адреса веденого 7-біт)", 595, 245, "#f3e8ff", "#a855f7", "Ведені передають свою адресу"),
        ("NACK", 735, 35, "#fee2e2", "#ef4444", "Хост завершує"),
        ("P", 770, 35, "#fee2e2", "#ef4444", "СТОП")
    ]

    for lbl, cx, bw, fcol, scol, note in blocks:
        p.append(rect(cx - bw / 2, 120, bw, 36, fill=fcol, stroke=scol, sw=1.5, rx=4))
        p.append(text(cx, 143, lbl, size=10.5, color=INK, bold=True))

    # 3. Розбір арбітражу між двома веденими
    p.append(rect(50, 195, 800, 165, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(70, 218, "Арбітраж за схемою «Монтажне АБО» (Wired-AND) на лінії SDA під час фази адреси веденого:", size=11.5, color=INK, bold=True, anchor="start"))

    # Ведений A (адреса 0x18 = 0011 000b)
    p.append(text(70, 250, "Ведений A (0x18 = 0001 1000b):", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(320, 250, "0   0   0   1   1   0   0   0   (Перемагає: утримує 0 на 4-му біті)", size=11, color=NEG, anchor="start"))

    # Ведений B (адреса 0x48 = 0100 1000b)
    p.append(text(70, 280, "Ведений B (0x48 = 0100 1000b):", size=11, color="#b45309", bold=True, anchor="start"))
    p.append(text(320, 280, "0   1   0   0   1   0   0   0   (Програє на 2-му біті: хотів 1, побачив 0 -> відпускає шину)", size=11, color="#b45309", anchor="start"))

    # Підсумок
    p.append(text(70, 315, "Результат:", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(145, 315, "Хост зчитує 0x18. Ведений A скидає свій ALERT#. Ведений B продовжує утримувати ALERT# для наступного ARA.", size=10.5, color=INK, anchor="start"))

    save("ara-arbitration-sequence.svg", w, h, p)


# ── 4. pec-packet-format.svg ──────────────────────────────────────────────────
def fig_pec_packet():
    w, h = 900, 320
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    p.append(text(450, 35, "Структура транзакції SMBus Write Word із контрольним байтом PEC", size=14, color=INK, bold=True))

    # Кадри транзакції
    frames = [
        ("S", 70, 30, "#fee2e2", "#ef4444"),
        ("Slave Addr + Wr", 150, 110, "#dbeafe", "#3b82f6"),
        ("A", 220, 26, "#dcfce7", "#22c55e"),
        ("Command Code", 300, 115, "#fef3c7", "#d97706"),
        ("A", 370, 26, "#dcfce7", "#22c55e"),
        ("Data Low (D0–D7)", 460, 130, "#e0e7ff", "#6366f1"),
        ("A", 540, 26, "#dcfce7", "#22c55e"),
        ("Data High (D8–D15)", 635, 140, "#e0e7ff", "#6366f1"),
        ("A", 720, 26, "#dcfce7", "#22c55e"),
        ("PEC (CRC-8)", 785, 90, "#fce7f3", "#ec4899"),
        ("A", 845, 26, "#dcfce7", "#22c55e"),
        ("P", 875, 26, "#fee2e2", "#ef4444")
    ]

    for lbl, cx, bw, fcol, scol in frames:
        p.append(rect(cx - bw / 2, 70, bw, 38, fill=fcol, stroke=scol, sw=1.5, rx=4))
        p.append(text(cx, 94, lbl, size=10, color=INK, bold=True))

    # Дужка полінома CRC-8
    p.append(line(95, 130, 95, 145, color="#db2777", sw=1.5))
    p.append(line(95, 145, 740, 145, color="#db2777", sw=1.5))
    p.append(line(740, 145, 740, 130, color="#db2777", sw=1.5))
    p.append(arrow(740, 145, 785, 115, color="#db2777", sw=1.5))

    p.append(text(420, 168, "Обчислення CRC-8 (поліном C(x) = x⁸ + x² + x + 1, ініціалізація 0x00)", size=11, color="#db2777", bold=True))

    # Інформаційний блок про властивості PEC
    p.append(rect(50, 195, 800, 105, fill="#fdf2f8", stroke="#f472b6", sw=1.2, rx=6))
    p.append(text(70, 220, "Ключові правила функціонування PEC (Packet Error Checking):", size=11.5, color="#9d174d", bold=True, anchor="start"))
    p.append(text(70, 245, "1. Поліном CRC-8: x⁸ + x² + x + 1 (позначення 0x07 або 0x107). Початковий залишок — 0x00.", size=10.5, color=INK, anchor="start"))
    p.append(text(70, 268, "2. Охоплення: всі байти від стартового біта (адреса, біти R/W, код команди, лічильник кількості та дані).", size=10.5, color=INK, anchor="start"))
    p.append(text(70, 290, "3. Обробка помилки: якщо ведений виявляє невідповідність PEC при записі, він генерує NACK і відкидає дані.", size=10.5, color=INK, anchor="start"))

    save("pec-packet-format.svg", w, h, p)


# ── 5. sbs-smart-battery-model.svg ────────────────────────────────────────────
def fig_sbs_model():
    w, h = 900, 360
    p = []
    p.append(rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0, rx=0))

    p.append(text(450, 32, "Архітектура взаємодії компонентів Smart Battery System (SBS)", size=14, color=INK, bold=True))

    # Три головні блоки
    # 1. Smart Battery Host
    tb1, _, _ = textbox(170, 140, "Smart Battery Host\n(Embedded Controller / ACPI OS)\n\n• Зчитує стан заряду\n• Моніторить залишкову ємність\n• Керує профілями споживання", size=11, pad=10, fill="#eff6ff", stroke="#3b82f6", sw=1.5, min_w=240)
    # 2. Smart Battery
    tb2, _, _ = textbox(450, 140, "Smart Battery\n(bq40z50 / BQ78350 BMS)\n\n• Вимірює напругу, струм, темп.\n• Обчислює State of Charge (SoC)\n• Надсилає ChargingCurrent/Voltage", size=11, pad=10, fill="#f0fdf4", stroke="#22c55e", sw=1.5, min_w=240)
    # 3. Smart Battery Charger
    tb3, _, _ = textbox(730, 140, "Smart Battery Charger\n(Керований перетворювач DC-DC)\n\n• Приймає параметри струму\n• Формує профіль CC/CV\n• Вимикає заряд при тривозі", size=11, pad=10, fill="#fff7ed", stroke="#f97316", sw=1.5, min_w=240)

    p.append(tb1)
    p.append(tb2)
    p.append(tb3)

    # Зв'язки між блоками по SMBus
    # Host <-> Battery
    p.append(arrow(295, 120, 325, 120, color=NEG, sw=1.8))
    p.append(arrow(325, 140, 295, 140, color=FIELD, sw=1.8))
    p.append(text(310, 105, "SMBus", size=10, color=MUTED, bold=True))

    # Battery -> Charger (Master mode / Broadcast)
    p.append(arrow(575, 120, 605, 120, color=POS, sw=1.8))
    p.append(arrow(605, 140, 575, 140, color=FIELD, sw=1.8))
    p.append(text(590, 105, "SMBus", size=10, color=MUTED, bold=True))

    # Силові лінії живлення знизу
    p.append(rect(60, 245, 780, 90, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(80, 268, "Ключовий принцип концепції SBS (Smart Battery System):", size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(80, 292, "1. Інтелект зосереджено в акумуляторі: хімічні властивості, алгоритми балансування та деградація відомі самій батареї.", size=10.5, color=INK, anchor="start"))
    p.append(text(80, 315, "2. Зарядний пристрій є «виконавцем»: він не має жорстких прошитих профілів, а динамічно отримує цільові значення струму й напруги по SMBus.", size=10.5, color=INK, anchor="start"))

    save("sbs-smart-battery-model.svg", w, h, p)


def main():
    fig_system_topology()
    fig_timing_timeout()
    fig_ara_arbitration()
    fig_pec_packet()
    fig_sbs_model()

if __name__ == "__main__":
    main()
