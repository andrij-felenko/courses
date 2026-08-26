# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def path(d, color=LINE, fill="none", sw=1.5, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"{dash_attr}/>'


# ── 1. five-step-flow.svg ───────────────────────────────────────────────────
def fig_five_step_flow():
    W, H = 840, 240
    p = []

    p.append(text(W / 2, 22, "П'ятиетапний алгоритм діагностики мікросхеми", size=15, color=INK, bold=True))

    steps = [
        ("1. Живлення та GND", "VDD на виводах\nПульсації, просадки\nDecoupling 100 нФ", "#eff6ff", "#3b82f6"),
        ("2. Скидання та EN", "Рівні nRST, SHDN, CE\nПороги скидання POR\nВисячі входи (float)", "#fef3c7", "#d97706"),
        ("3. Фізика шини", "Підтяжка I2C 2.2k-4.7k\nSPI MOSI/MISO/CS\nРівні напруг 3.3V/5V", "#f0fdf4", "#16a34a"),
        ("4. Адресація та скан", "Зсув 7-біт vs 8-біт\nПіни AD0/ADDR\nI2C Bus Scanner", "#faf5ff", "#8b5cf6"),
        ("5. Осцилограф / ЛА", "Декодування кадрів\nACK/NACK на 9 такті\nРозблокування шини", "#fef2f2", "#dc2626"),
    ]

    bw = 142
    bh = 135
    start_x = 24
    y = 52

    for i, (title, body, bg_col, border_col) in enumerate(steps):
        bx = start_x + i * (bw + 20)
        p.append(rect(bx, y, bw, bh, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        p.append(text(bx + bw / 2, y + 26, title, size=11, color=INK, bold=True))
        p.append(line(bx + 10, y + 36, bx + bw - 10, y + 36, color=border_col, sw=1.0))
        
        lines = body.split("\n")
        for j, l in enumerate(lines):
            p.append(text(bx + bw / 2, y + 58 + j * 24, l, size=9.5, color="#374151"))

        if i < len(steps) - 1:
            arr_x = bx + bw + 2
            arr_y = y + bh / 2
            p.append(arrow(arr_x, arr_y, arr_x + 16, arr_y, color=MUTED, sw=1.8))

    p.append(text(W / 2, 215, "Кожен наступний крок має сенс лише після підтвердження справності попереднього", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "five-step-flow.svg"), W, H, *p)


# ── 2. power-and-reset-traps.svg ───────────────────────────────────────────
def fig_power_reset_traps():
    W, H = 820, 310
    p = []

    p.append(text(210, 22, "Пастка живлення: Мультиметр vs Осцилограф", size=12.5, color=INK, bold=True))
    p.append(text(620, 22, "Пастка скидання: Порядок наростання напруги", size=12.5, color=INK, bold=True))
    p.append(line(415, 15, 415, 290, color=MUTED, sw=1.0, dash="4 4"))

    # Ліва панель: Живлення
    p.append(rect(20, 40, 375, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    
    # Графік напруги
    p.append(line(50, 210, 370, 210, color=INK, sw=1.2)) # вісь X (t)
    p.append(line(50, 70, 50, 210, color=INK, sw=1.2))  # вісь Y (V)
    p.append(text(360, 225, "Час (t)", size=10, color=MUTED))
    p.append(text(35, 75, "3.3V", size=10, color=MUTED, anchor="end"))
    p.append(text(35, 140, "2.7V", size=10, color=POS, anchor="end"))
    p.append(text(35, 210, "0V", size=10, color=MUTED, anchor="end"))

    # Лінія порогу BOD
    p.append(line(50, 135, 370, 135, color=POS, sw=1.0, dash="4 3"))
    p.append(text(285, 127, "Поріг BOD (2.7V)", size=9.5, color=POS))

    # Сигнал осцилографа з просадкою
    scope_path = "M 50 85 L 140 85 Q 165 85 175 165 Q 185 85 210 85 L 365 85"
    p.append(path(scope_path, color=NEG, fill="none", sw=2.2))
    p.append(text(185, 185, "Просадка до 2.1V (імпульс 5 мкс)", size=9.5, color=POS, bold=True))
    p.append(arrow(185, 172, 176, 160, color=POS, sw=1.2))

    # Покази мультиметра
    p.append(line(50, 85, 370, 85, color=FIELD, sw=1.4, dash="6 3"))
    p.append(text(110, 72, "Мультиметр: 3.30V (середнє)", size=9.5, color=FIELD, bold=True))

    p.append(text(205, 262, "Мультиметр не бачить коротких просадок, які викликають скидання", size=9.5, color=INK))

    # Права панель: Скидання
    p.append(rect(430, 40, 370, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))

    p.append(line(460, 210, 780, 210, color=INK, sw=1.2)) # вісь X
    p.append(line(460, 70, 460, 210, color=INK, sw=1.2))  # вісь Y
    p.append(text(770, 225, "Час (t)", size=10, color=MUTED))

    # Повільне наростання VDD
    p.append(path("M 460 210 Q 550 195 640 85 L 775 85", color=NEG, fill="none", sw=2.0))
    p.append(text(725, 75, "VDD (повільний пуск)", size=9.5, color=NEG, bold=True))

    # Попереднє відпускання RESET
    p.append(path("M 460 210 L 515 210 L 525 85 L 775 85", color=POS, fill="none", sw=1.8))
    p.append(text(540, 102, "nRST відпущено", size=9.5, color=POS, bold=True))

    # Критична зона
    p.append(rect(525, 85, 115, 125, fill="rgba(220, 38, 38, 0.08)", stroke=POS, sw=1.0))
    p.append(text(582, 135, "VDD < 2.7V при nRST=1", size=9.5, color=POS, bold=True))
    p.append(text(582, 155, "(Зависання логіки)", size=9.5, color=POS, bold=True))

    p.append(text(615, 262, "nRST має відпускатися лише ПІСЛЯ стабілізації VDD", size=9.5, color=INK))

    render(os.path.join(OUT, "power-and-reset-traps.svg"), W, H, *p)


# ── 3. i2c-address-shift.svg ────────────────────────────────────────────────
def fig_i2c_address_shift():
    W, H = 820, 290
    p = []

    p.append(text(W / 2, 22, "Анатомія адреси I2C: 7-бітний ідентифікатор проти 8-бітного кадру", size=14, color=INK, bold=True))

    # Верхній блок: 7-бітна адреса в даташиті (наприклад 0x68 для MPU6050 або DS3231)
    p.append(text(60, 60, "7-бітна адреса пристрою (0x68 = 0b1101000):", size=10.5, color=INK, bold=True, anchor="start"))
    
    # 7 бітів
    bits_7 = ["1", "1", "0", "1", "0", "0", "0"]
    labels_7 = ["A6", "A5", "A4", "A3", "A2", "A1", "A0"]
    start_x = 420
    cell_w = 46
    cell_h = 36
    y1 = 42

    for i in range(7):
        cx = start_x + i * cell_w
        p.append(rect(cx, y1, cell_w, cell_h, fill="#eff6ff", stroke="#3b82f6", sw=1.2))
        p.append(text(cx + cell_w / 2, y1 + 18, bits_7[i], size=12, color=INK, bold=True))
        p.append(text(cx + cell_w / 2, y1 + 30, labels_7[i], size=9.5, color=MUTED))

    # Стрілка зсуву вліво на 1 біт
    p.append(arrow(start_x + 3.5 * cell_w, y1 + cell_h + 4, start_x + 3.5 * cell_w, y1 + cell_h + 34, color=FIELD, sw=2.0))
    p.append(text(start_x + 3.5 * cell_w + 105, y1 + cell_h + 22, "Зсув вліво на 1 біт: (addr << 1) | R/W", size=10, color=FIELD, bold=True))

    # Нижній блок: 8-бітний кадр на шині (Write: 0xD0, Read: 0xD1)
    y2 = 122
    p.append(text(60, y2 + 22, "8-бітний байт на шині SDA:", size=10.5, color=INK, bold=True, anchor="start"))

    start_x8 = start_x - cell_w
    for i in range(7):
        cx = start_x8 + i * cell_w
        p.append(rect(cx, y2, cell_w, cell_h, fill="#eff6ff", stroke="#3b82f6", sw=1.2))
        p.append(text(cx + cell_w / 2, y2 + 18, bits_7[i], size=12, color=INK, bold=True))
        p.append(text(cx + cell_w / 2, y2 + 30, labels_7[i], size=9.5, color=MUTED))

    # 8-й біт (R/W)
    cx_rw = start_x8 + 7 * cell_w
    p.append(rect(cx_rw, y2, cell_w, cell_h, fill="#fef2f2", stroke=POS, sw=1.5))
    p.append(text(cx_rw + cell_w / 2, y2 + 18, "0 / 1", size=11, color=POS, bold=True))
    p.append(text(cx_rw + cell_w / 2, y2 + 30, "R/W", size=9.5, color=POS, bold=True))

    # Пояснення байтів
    p.append(text(start_x8 + 4 * cell_w, y2 + 54, "Запис (Write): 0xD0 (0b11010000)  |  Читання (Read): 0xD1 (0b11010001)", size=10, color="#1e293b", bold=True))

    # Блок типової помилки
    p.append(rect(40, 195, 740, 75, fill="#fff1f2", stroke="#f43f5e", sw=1.2, rx=6))
    p.append(text(60, 218, "⚠️ Головна пастка адресації (Double-Shift Error):", size=10.5, color="#be123c", bold=True, anchor="start"))
    p.append(text(60, 238, "Якщо передати 8-бітне значення 0xD0 у функцію HAL / Wire, яка очікує 7-бітну адресу,", size=9.5, color="#4c0519", anchor="start"))
    p.append(text(60, 256, "бібліотека повторно виконає (0xD0 << 1) = 0x1A0 → на шину піде 0xA0 (пристрій 0x50), отримавши NACK!", size=9.5, color="#4c0519", bold=True, anchor="start"))

    render(os.path.join(OUT, "i2c-address-shift.svg"), W, H, *p)


# ── 4. i2c-ack-nack-scope.svg ───────────────────────────────────────────────
def fig_i2c_ack_nack_scope():
    W, H = 840, 310
    p = []

    p.append(text(W / 2, 22, "Осцилограма шини I2C: 9-й такт (ACK проти NACK) та форма фронтів", size=14, color=INK, bold=True))

    # Секція А: ACK проти NACK
    p.append(text(50, 48, "SCL", size=11, color="#6b21a8", bold=True, anchor="start"))
    p.append(text(50, 108, "SDA (ACK)", size=10, color="#15803d", bold=True, anchor="start"))
    p.append(text(50, 168, "SDA (NACK)", size=10, color=POS, bold=True, anchor="start"))

    # SCL 9 тактів
    scl_x0 = 130
    tw = 32
    h_high = 40
    h_low = 65

    # START
    scl_d = ["M", str(scl_x0), str(h_high), "L", str(scl_x0 + 15), str(h_high)]
    cur_x = scl_x0 + 15
    for k in range(9):
        scl_d.extend(["L", str(cur_x), str(h_low), "L", str(cur_x + tw/2), str(h_low),
                      "L", str(cur_x + tw/2), str(h_high), "L", str(cur_x + tw), str(h_high)])
        p.append(text(cur_x + tw * 0.75, h_high - 8, str(k + 1), size=9.5, color="#6b21a8"))
        cur_x += tw

    p.append(path(" ".join(scl_d), color="#9333ea", fill="none", sw=2.0))

    # SDA (ACK)
    sda_ack_d = ["M", str(scl_x0), str(h_high + 60), "L", str(scl_x0 + 8), str(h_high + 60),
                 "L", str(scl_x0 + 8), str(h_low + 60), "L", str(cur_x - tw), str(h_low + 60),
                 "L", str(cur_x - tw), str(h_low + 60), "L", str(cur_x), str(h_low + 60)] # Slave pulls LOW at 9th
    p.append(path(" ".join(sda_ack_d), color="#16a34a", fill="none", sw=2.0))

    # Маркер ACK
    p.append(rect(cur_x - tw + 2, h_high + 50, tw - 4, 32, fill="rgba(34, 197, 94, 0.12)", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(cur_x - tw/2, h_high + 70, "ACK=0", size=9.5, color="#15803d", bold=True))

    # SDA (NACK)
    sda_nack_d = ["M", str(scl_x0), str(h_high + 120), "L", str(scl_x0 + 8), str(h_high + 120),
                  "L", str(scl_x0 + 8), str(h_low + 120), "L", str(cur_x - tw), str(h_low + 120),
                  "L", str(cur_x - tw), str(h_high + 120), "L", str(cur_x), str(h_high + 120)] # Master releases, stays HIGH
    p.append(path(" ".join(sda_nack_d), color=POS, fill="none", sw=2.0))

    # Маркер NACK
    p.append(rect(cur_x - tw + 2, h_high + 110, tw - 4, 32, fill="rgba(239, 68, 68, 0.12)", stroke=POS, sw=1.2, rx=4))
    p.append(text(cur_x - tw/2, h_high + 130, "NACK=1", size=9.5, color=POS, bold=True))

    # Вертикальна лінія 9-го такту
    p.append(line(cur_x - tw, 30, cur_x - tw, 205, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(cur_x - tw/2, 218, "9-й такт (відповідь веденого)", size=9.5, color=MUTED))

    # Права секція: Проблема підтяжки (RC фронти)
    rx0 = 500
    p.append(rect(rx0, 42, 315, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(rx0 + 157, 62, "Спотворення форми фронтів (Pull-Up)", size=10.5, color=INK, bold=True))

    # Правильний фронт (Rp = 2.2k)
    p.append(path("M 525 125 L 565 125 L 568 85 L 635 85 L 637 125 L 665 125", color="#16a34a", fill="none", sw=1.8))
    p.append(text(675, 95, "Норма (2.2k-4.7k): tr < 300 нс", size=9.5, color="#16a34a", bold=True, anchor="start"))

    # Завалений фронт (Rp = 50k внутрішня)
    p.append(path("M 525 185 L 565 185 Q 585 180 635 152 L 637 185 L 665 185", color=POS, fill="none", sw=1.8))
    p.append(text(675, 165, "Слабкий Pull-Up: tr > 1500 нс", size=9.5, color=POS, bold=True, anchor="start"))

    # Пояснення знизу
    p.append(rect(50, 240, 740, 52, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=5))
    p.append(text(420, 260, "Якщо чип не відповідає, на 9-му такті SDA залишається у '1' через резистор підтяжки.", size=9.5, color=INK, bold=True))
    p.append(text(420, 278, "Осцилограф дозволяє відрізнити повну тишу від 'заваленого' фронту через відсутність зовнішнього резистора.", size=9.5, color="#475569"))

    render(os.path.join(OUT, "i2c-ack-nack-scope.svg"), W, H, *p)


# ── 5. i2c-bus-lockup-recovery.svg ──────────────────────────────────────────
def fig_i2c_bus_lockup_recovery():
    W, H = 820, 270
    p = []

    p.append(text(W / 2, 22, "Зависання шини I2C (SDA у нулі) та процедура апаратного виведення (Bus Recovery)", size=13.5, color=INK, bold=True))

    # Сценарій: Slave затиснув SDA
    p.append(rect(30, 42, 760, 68, fill="#fef2f2", stroke="#f87171", sw=1.2, rx=6))
    p.append(text(45, 64, "1. Причина глухого кута (Deadlock):", size=10.5, color="#991b1b", bold=True, anchor="start"))
    p.append(text(45, 84, "Мікроконтролер перезавантажився посеред читання байта, коли чип передавав '0' і тримав SDA притиснутим до землі.", size=9.5, color="#7f1d1d", anchor="start"))
    p.append(text(45, 100, "Майстер не може згенерувати умову START або STOP, оскільки лінія SDA заблокована веденим у стані LOW.", size=9.5, color="#7f1d1d", bold=True, anchor="start"))

    # Покроковий алгоритм відновлення
    y_rec = 125
    rec_steps = [
        ("Крок 1: Реконфігурація", "Перевести SCL у GPIO Output\nПеревести SDA у GPIO Input", "#eff6ff", "#3b82f6"),
        ("Крок 2: 9 тактових імпульсів", "Подати до 9 імпульсів на SCL\nВедений довиштовхує свій байт", "#fef3c7", "#d97706"),
        ("Крок 3: Перевірка SDA", "SDA звільнено веденим і\nпідтягнуто до '1' через Pull-Up", "#f0fdf4", "#16a34a"),
        ("Крок 4: Умова STOP", "Сформувати перехід SDA 0→1\nпри високому рівні на SCL", "#faf5ff", "#8b5cf6")
    ]

    bw = 175
    bh = 115
    sx = 35

    for i, (stitle, sdesc, sbg, sstroke) in enumerate(rec_steps):
        bx = sx + i * (bw + 16)
        p.append(rect(bx, y_rec, bw, bh, fill=sbg, stroke=sstroke, sw=1.3, rx=6))
        p.append(text(bx + bw / 2, y_rec + 24, stitle, size=10, color=INK, bold=True))
        p.append(line(bx + 10, y_rec + 34, bx + bw - 10, y_rec + 34, color=sstroke, sw=1.0))
        
        lines = sdesc.split("\n")
        for j, l in enumerate(lines):
            p.append(text(bx + bw / 2, y_rec + 58 + j * 22, l, size=9.5, color="#374151"))

        if i < len(rec_steps) - 1:
            arr_x = bx + bw + 1
            arr_y = y_rec + bh / 2
            p.append(arrow(arr_x, arr_y, arr_x + 13, arr_y, color=MUTED, sw=1.5))

    render(os.path.join(OUT, "i2c-bus-lockup-recovery.svg"), W, H, *p)


if __name__ == "__main__":
    fig_five_step_flow()
    fig_power_reset_traps()
    fig_i2c_address_shift()
    fig_i2c_ack_nack_scope()
    fig_i2c_bus_lockup_recovery()
    print("All figures generated successfully.")
