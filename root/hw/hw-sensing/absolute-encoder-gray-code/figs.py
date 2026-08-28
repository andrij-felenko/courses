# -*- coding: utf-8 -*-
"""Фігури до теми «Абсолютний енкодер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Будова кодового диска й оптичного тракту ─────────────────────────────
def fig_code_disc():
    W, H = 840, 460
    f = [text(W / 2, 28, "Будова оптичного абсолютного енкодера: кодовий диск і оптичний тракт", size=15, bold=True)]

    # --- Ліва частина: Кодовий диск з доріжками коду Грея ---
    cx, cy = 200, 245
    r_hub = 24
    r_tracks = [46, 72, 98, 124, 150]  # 4 доріжки коду Грея: T0(зовні, LSB)..T3(всередині, MSB)
    
    f.append(text(cx, 62, "Кодовий диск (4-бітний код Грея)", size=13, bold=True))
    f.append(circle(cx, cy, r_tracks[-1] + 6, fill="#fdfefe", stroke=INK, sw=1.8))
    
    # 4-бітні сектори коду Грея (16 секторів)
    # Таблиця 4-бітного коду Грея:
    gray_table = [
        0b0000, 0b0001, 0b0011, 0b0010,
        0b0110, 0b0111, 0b0101, 0b0100,
        0b1100, 0b1101, 0b1111, 0b1110,
        0b1010, 0b1011, 0b1001, 0b1000
    ]
    
    n_sectors = 16
    for s in range(n_sectors):
        g = gray_table[s]
        a0 = math.radians(s * 360.0 / n_sectors - 90)
        a1 = math.radians((s + 1) * 360.0 / n_sectors - 90)
        for bit in range(4):
            # bit 0 = LSB (зовнішня доріжка r_tracks[3]..r_tracks[4]), bit 3 = MSB (внутрішня r_tracks[0]..r_tracks[1])
            is_opaque = (g >> bit) & 1
            r_in = r_tracks[3 - bit]
            r_out = r_tracks[3 - bit + 1]
            
            fill_color = "#2c3e50" if is_opaque else "#ffffff"
            x0o, y0o = cx + r_out * math.cos(a0), cy + r_out * math.sin(a0)
            x1o, y1o = cx + r_out * math.cos(a1), cy + r_out * math.sin(a1)
            x1i, y1i = cx + r_in * math.cos(a1), cy + r_in * math.sin(a1)
            x0i, y0i = cx + r_in * math.cos(a0), cy + r_in * math.sin(a0)
            
            d = ("M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 0 %.1f %.1f Z"
                 % (x0o, y0o, r_out, r_out, x1o, y1o, x1i, y1i, r_in, r_in, x0i, y0i))
            f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.7"/>' % (d, fill_color, MUTED))

    # Центральна маточина та вал
    f.append(circle(cx, cy, r_hub, fill="#d8dde4", stroke=INK, sw=1.5))
    f.append(circle(cx, cy, 8, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 4, "вал", size=10, color=BG, bold=True))

    # Радіальна лінія зчитування (вгору від центру)
    f.append(line(cx, cy - r_tracks[-1] - 12, cx, cy - r_hub + 4, color=POS, sw=2.2, dash="4 2"))
    f.append(text(cx + 8, cy - r_tracks[-1] - 18, "лінія зчитування", size=11, color=POS, bold=True, anchor="start"))

    # Стрілка обертання
    f.append('<path d="M%.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (cx + 162, cy - 24, 162, 162, cx + 162, cy + 24, FIELD))
    f.append(text(cx + 172, cy + 4, "оберт", size=11, color=FIELD, bold=True, anchor="start"))
    f.append(text(cx, cy + r_tracks[-1] + 28, "16 унікальних кутових секторів (по 22.5°)", size=11, color=MUTED))

    # --- Права частина: Оптичний тракт у розрізі ---
    rx = 460
    f.append(text(rx + 180, 62, "Оптична система (розріз радіальної лінії)", size=13, bold=True))

    # 1. Джерело випромінювання (LED / лазерний діод)
    b_led, _, _ = textbox(rx + 180, 95, "Інфрачервоний випромінювач (LED / VCSEL)", size=11, fill="#fdf3e2", stroke="#b8801f", color="#8a5f12", bold=True)
    f.append(b_led)

    # 2. Коліматорна лінза
    f.append('<path d="M%d %d Q%d %d %d %d Q%d %d %d %d Z" fill="#e8f4f8" stroke="%s" stroke-width="1.4"/>'
             % (rx + 60, 142, rx + 180, 156, rx + 300, 142, rx + 180, 128, rx + 60, 142, NEG))
    f.append(text(rx + 180, 146, "Коліматорна лінза (паралельний пучок)", size=10.5, color=NEG, bold=True))

    # Промені світла від лінзи до диска
    for ray_x in [rx + 80, rx + 130, rx + 180, rx + 230, rx + 280]:
        f.append(line(ray_x, 156, ray_x, 210, color="#f39c12", sw=1.6, dash="3 3"))

    # 3. Кодовий диск у розрізі (скло + хром)
    f.append(rect(rx + 50, 212, 260, 18, fill="#ffffff", stroke=INK, sw=1.4, rx=2))
    # Сектори (прозорі та непрозорі)
    # b3(MSB): темний, b2: світлий, b1: темний, b0(LSB): світлий -> приклад коду 1010
    f.append(rect(rx + 75, 212, 45, 18, fill="#2c3e50", stroke="none"))
    f.append(rect(rx + 175, 212, 45, 18, fill="#2c3e50", stroke="none"))
    f.append(text(rx + 180, 245, "Рухомий кодовий диск (скло / хромові мітки)", size=10.5, color=INK, bold=True))

    # 4. Нерухома діафрагма / маска (reticle)
    f.append(rect(rx + 50, 266, 260, 8, fill="#95a5a6", stroke=LINE, sw=1.2, rx=1))
    # Прорізи маски
    for slit_x in [rx + 90, rx + 140, rx + 190, rx + 240]:
        f.append(rect(slit_x - 3, 266, 6, 8, fill="#ffffff", stroke="none"))
    f.append(text(rx + 180, 288, "Нерухома щілинна маска (растр)", size=10, color=MUTED))

    # 5. Фотоприймальна матриця (Opto-ASIC)
    f.append(rect(rx + 50, 305, 260, 48, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(rx + 180, 323, "Фотоприймальна матриця (Opto-ASIC)", size=11, color="#1e7a43", bold=True))
    
    # 4 фотодіоди
    pd_labels = ["b3 (MSB)", "b2", "b1", "b0 (LSB)"]
    pd_vals = ["1", "0", "1", "0"]
    for idx, px_val in enumerate([rx + 90, rx + 140, rx + 190, rx + 240]):
        f.append(circle(px_val, 338, 7, fill="#ffffff", stroke=FIELD, sw=1.2))
        f.append(text(px_val, 342, pd_vals[idx], size=9.5, color="#1e7a43", bold=True))
        f.append(text(px_val, 368, pd_labels[idx], size=9.5, color=MUTED))

    # Стрілка вниз до виходу даних
    f.append(arrow(rx + 180, 382, rx + 180, 412, color=INK, sw=1.8))
    b_out, _, _ = textbox(rx + 180, 428, "Паралельний або послідовний вихід: 1010₂", size=11, fill="#eef2f8", stroke=NEG, color=NEG, bold=True)
    f.append(b_out)

    render(os.path.join(IMG, "fig-code-disc.svg"), W, H, *f)


# ── 2. Кодовий стрибок: прямий двійковий vs код Грея ────────────────────────
def fig_binary_vs_gray():
    W, H = 840, 490
    f = [text(W / 2, 26, "Кодовий стрибок при зміні кількох бітів у двійковому коді проти коду Грея", size=15, bold=True)]

    # --- Ліва колонка: Прямий двійковий код (катастрофічний стрибок) ---
    lx = 215
    f.append(rect(30, 52, 370, 416, fill="#fdf7f7", stroke=POS, sw=1.4, rx=6))
    f.append(text(lx, 74, "Прямий двійковий код: 7 (0111₂) → 8 (1000₂)", size=12.5, color=POS, bold=True))
    f.append(text(lx, 94, "Перемикаються всі 4 біти одночасно", size=10.5, color=MUTED))

    # Часова діаграма 4 бітів двійкового коду
    t_start, t_end = 65, 365
    t_trans = 215
    y_bits = [135, 175, 215, 255]
    bit_names = ["b3 (MSB): 0 → 1", "b2: 1 → 0", "b1: 1 → 0", "b0 (LSB): 1 → 0"]
    
    # Ідеальні рівні vs реальний оптичний дрейф/перегин
    # Нехай b3 перемикається раніше, ніж спадають b2, b1, b0 через перекіс лінійки фотодіодів
    skew = 18  # ширина зони перекосу в px
    
    for i in range(4):
        f.append(text(75, y_bits[i] - 6, bit_names[i], size=9.5, color=INK, anchor="start"))
        f.append(line(t_start, y_bits[i], t_end, y_bits[i], color="#dcdde1", sw=1))
        
        if i == 0: # b3: 0 -> 1 раніше (на t_trans - skew/2)
            p = "M %d %d L %d %d L %d %d L %d %d" % (t_start, y_bits[i], t_trans - skew//2, y_bits[i], t_trans - skew//2, y_bits[i] - 18, t_end, y_bits[i] - 18)
        else:      # b2, b1, b0: 1 -> 0 пізніше (на t_trans + skew/2)
            p = "M %d %d L %d %d L %d %d L %d %d" % (t_start, y_bits[i] - 18, t_trans + skew//2, y_bits[i] - 18, t_trans + skew//2, y_bits[i], t_end, y_bits[i])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (p, INK))

    # Підсвітка зони невизначеності (glitch window)
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="rgba(231, 76, 60, 0.22)" stroke="%s" stroke-width="1" stroke-dasharray="2 2"/>'
             % (t_trans - skew//2, 110, skew, 160, POS))
    f.append(text(t_trans, 290, "Зона перекосу (Δt / Δx)", size=10, color=POS, bold=True))

    # Результуючий вихід: 7 -> 15 (ХИБНИЙ СПЛЕСК) -> 8
    f.append(line(t_start, 350, t_end, 350, color=MUTED, sw=1))
    p_pos = ("M %d %d L %d %d L %d %d L %d %d L %d %d L %d %d" 
             % (t_start, 360, t_trans - skew//2, 360, t_trans - skew//2, 315, t_trans + skew//2, 315, t_trans + skew//2, 354, t_end, 354))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (p_pos, POS))
    f.append(text(120, 380, "Позиція: 7", size=11, color=INK, bold=True))
    f.append(text(t_trans, 308, "15 (1111₂)!", size=12, color=POS, bold=True))
    f.append(text(310, 380, "Позиція: 8", size=11, color=INK, bold=True))
    f.append(text(lx, 442, "У сервоприводі: ударний стрибок моменту й струму", size=10.5, color=POS))

    # --- Права колонка: Код Грея (бездоганний плавний перехід) ---
    rx = 625
    f.append(rect(440, 52, 370, 416, fill="#f4faf5", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(rx, 74, "Код Грея: 7 (0100_G) → 8 (1100_G)", size=12.5, color="#1e7a43", bold=True))
    f.append(text(rx, 94, "Змінюється рівно ОДИН біт (b3)", size=10.5, color=MUTED))

    # Часова діаграма 4 бітів коду Грея
    gt_start, gt_end = 475, 775
    gt_trans = 625
    
    g_bit_names = ["b3: 0 → 1 (єдина зміна)", "b2: 1 → 1 (без змін)", "b1: 0 → 0 (без змін)", "b0: 0 → 0 (без змін)"]
    
    for i in range(4):
        f.append(text(485, y_bits[i] - 6, g_bit_names[i], size=9.5, color=INK, anchor="start"))
        f.append(line(gt_start, y_bits[i], gt_end, y_bits[i], color="#dcdde1", sw=1))
        
        if i == 0: # b3: 0 -> 1 на gt_trans
            p = "M %d %d L %d %d L %d %d L %d %d" % (gt_start, y_bits[i], gt_trans, y_bits[i], gt_trans, y_bits[i] - 18, gt_end, y_bits[i] - 18)
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p, FIELD))
        elif i == 1: # b2: 1 постійно
            f.append(line(gt_start, y_bits[i] - 18, gt_end, y_bits[i] - 18, color=INK, sw=2))
        else: # b1, b0: 0 постійно
            f.append(line(gt_start, y_bits[i], gt_end, y_bits[i], color=INK, sw=2))

    f.append(text(gt_trans, 290, "Одинарний перехід: нульова невизначеність", size=10, color="#1e7a43", bold=True))

    # Результуюча позиція
    f.append(line(gt_start, 350, gt_end, 350, color=MUTED, sw=1))
    p_gpos = "M %d %d L %d %d L %d %d L %d %d" % (gt_start, 360, gt_trans, 360, gt_trans, 354, gt_end, 354)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (p_gpos, FIELD))
    f.append(text(530, 380, "Позиція: 7 (0100_G)", size=11, color=INK, bold=True))
    f.append(text(720, 380, "Позиція: 8 (1100_G)", size=11, color=INK, bold=True))
    f.append(text(rx, 442, "Монотонний крок на ±1 квант за будь-яких умов", size=10.5, color="#1e7a43", bold=True))

    render(os.path.join(IMG, "fig-binary-vs-gray.svg"), W, H, *f)


# ── 3. Багатооборотні енкодери: Редуктор vs Давач Віганда ───────────────────
def fig_multiturn_principles():
    W, H = 840, 450
    f = [text(W / 2, 26, "Механізми лічби повних обертів у багатооборотних (Multi-Turn) енкодерах", size=15, bold=True)]

    # --- Ліва панель: Механічний прецизійний редуктор ---
    lx = 215
    f.append(rect(30, 52, 370, 378, fill="#fdfefe", stroke=LINE, sw=1.4, rx=6))
    f.append(text(lx, 76, "Механічний редуктор (Gear Train)", size=13, bold=True))
    f.append(text(lx, 96, "Каскад прецизійних шестерень і вторинних дисків", size=10.5, color=MUTED))

    # Головний вал + диск (1:1)
    f.append(circle(110, 160, 42, fill="#eef2f8", stroke=NEG, sw=1.8))
    f.append(circle(110, 160, 14, fill="#d8dde4", stroke=INK, sw=1.2))
    f.append(text(110, 164, "1:1", size=10, bold=True, color=NEG))
    f.append(text(110, 218, "Головний диск (кути 0..360°)", size=9.5, color=INK))

    # Ступінь 1 (16:1)
    f.append(circle(225, 160, 32, fill="#fdf3e2", stroke="#b8801f", sw=1.6))
    f.append(circle(225, 160, 10, fill="#d8dde4", stroke=INK, sw=1.2))
    f.append(text(225, 164, "16:1", size=9.5, bold=True, color="#b8801f"))
    f.append(text(225, 206, "Диск 1 (1..16 об.)", size=9.5, color=INK))

    # Ступінь 2 (256:1)
    f.append(circle(325, 160, 24, fill="#eef6ef", stroke=FIELD, sw=1.5))
    f.append(circle(325, 160, 8, fill="#d8dde4", stroke=INK, sw=1.2))
    f.append(text(325, 164, "256:1", size=9.5, bold=True, color=FIELD))
    f.append(text(325, 198, "Диск 2 (..4096)", size=9.5, color=INK))

    # Зачеплення шестерень
    f.append(line(152, 160, 193, 160, color=MUTED, sw=2, dash="2 2"))
    f.append(line(257, 160, 301, 160, color=MUTED, sw=2, dash="2 2"))

    # Опис властивостей редуктора
    b_gear_desc, _, _ = textbox(lx, 275, 
        "• Чисто механічне збереження положення\n"
        "• Працює без живлення та батарейки\n"
        "• Недоліки: знос зубців, люфт, габарити,\n"
        "  вразливість до сильної вібрації", 
        size=10.5, pad=8, fill=FILL, stroke=MUTED, color=INK)
    f.append(b_gear_desc)
    f.append(text(lx, 408, "До 4096 або 65536 обертів механічної пам'яті", size=10.5, color=NEG, bold=True))

    # --- Права панель: Електронний лічильник з давачем Віганда ---
    rx = 625
    f.append(rect(440, 52, 370, 378, fill="#fdfefe", stroke=LINE, sw=1.4, rx=6))
    f.append(text(rx, 76, "Давач Віганда (Wiegand Energy Harvesting)", size=13, bold=True))
    f.append(text(rx, 96, "Генерація енергії та лічба обертів без батареї", size=10.5, color=MUTED))

    # Схема давача Віганда: Обертовий магніт N/S -> Дріт Віганда з котушкою
    f.append(rect(475, 135, 50, 48, fill="#fee2e2", stroke=POS, sw=1.4, rx=3))
    f.append(text(500, 152, "N", size=12, color=POS, bold=True))
    f.append(text(500, 172, "S", size=12, color=NEG, bold=True))
    f.append(text(500, 200, "Магніт вала", size=9.5, color=INK))

    # Магнітне поле
    f.append(arrow(530, 159, 565, 159, color=POS, sw=1.8))

    # Дріт Віганда з котушкою
    f.append(rect(570, 142, 70, 34, fill="#f4f6f8", stroke="#d35400", sw=1.5, rx=2))
    f.append(line(575, 159, 635, 159, color="#d35400", sw=4)) # сам дріт
    # Витки котушки
    for wx in range(582, 630, 7):
        f.append(line(wx, 142, wx + 4, 176, color="#e67e22", sw=1.6))
    f.append(text(605, 200, "Дріт + котушка", size=9.5, color="#d35400", bold=True))

    # Стрілка енергетичного імпульсу
    f.append(arrow(645, 159, 680, 159, color=FIELD, sw=2))

    # Мікросхема лічильника (FRAM + логіка)
    f.append(rect(685, 130, 105, 58, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(737, 148, "Енергонезалежний", size=9.5, color="#1e7a43"))
    f.append(text(737, 162, "лічильник (FRAM)", size=9.5, color="#1e7a43", bold=True))
    f.append(text(737, 176, "живлення від імпульсу", size=9.5, color=MUTED))

    # Опис властивостей Віганда
    b_wiegand_desc, _, _ = textbox(rx, 275,
        "• Ефект Баркгаузена: стрибок намагніченості\n"
        "• Генерує імпульс ~3-5 В навіть при 0.01 об/хв\n"
        "• Енергії вистачає на запис оберту у FRAM\n"
        "• Немає механічного зносу, необмежений ресурс",
        size=10.5, pad=8, fill=FILL, stroke=MUTED, color=INK)
    f.append(b_wiegand_desc)
    f.append(text(rx, 408, "Повна відсутність батарейки й редуктора", size=10.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "fig-multiturn-principles.svg"), W, H, *f)


# ── 4. Цифрові інтерфейси: SSI vs BiSS-C ────────────────────────────────────
def fig_serial_protocols():
    W, H = 840, 480
    f = [text(W / 2, 26, "Промислові послідовні інтерфейси абсолютних енкодерів: SSI та BiSS-C", size=15, bold=True)]

    # --- Верхня секція: SSI (Synchronous Serial Interface) ---
    f.append(rect(30, 52, 780, 185, fill="#fdfefe", stroke=LINE, sw=1.4, rx=6))
    f.append(text(80, 74, "SSI (Synchronous Serial Interface)", size=13, bold=True, anchor="start"))
    f.append(text(790, 74, "Простий односпрямований потік (RS-422, такти Master)", size=10.5, color=MUTED, anchor="end"))

    # Тактовий сигнал SSI (CLK)
    f.append(text(45, 114, "CLK", size=11, bold=True, color=NEG, anchor="start"))
    f.append(line(95, 120, 785, 120, color="#dcdde1", sw=1))
    
    # 13 тактів + пауза таймауту tm
    clk_x = 100
    clk_step = 36
    p_clk = "M %d %d" % (clk_x, 102)
    for k in range(13):
        p_clk += " L %d %d L %d %d L %d %d L %d %d" % (
            clk_x + k * clk_step, 102,
            clk_x + k * clk_step + 6, 120,
            clk_x + k * clk_step + 18, 120,
            clk_x + k * clk_step + 24, 102
        )
    p_clk += " L %d %d" % (clk_x + 13 * clk_step + 100, 102)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (p_clk, NEG))

    # Лінія даних SSI (DATA)
    f.append(text(45, 164, "DATA", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(line(95, 170, 785, 170, color="#dcdde1", sw=1))
    
    # Комірки даних
    ssi_bits = ["MSB", "b11", "b10", "b9", "b8", "b7", "b6", "b5", "b4", "b3", "b2", "b1", "LSB"]
    for k in range(13):
        bx = clk_x + k * clk_step + 18
        f.append(rect(bx, 150, clk_step - 2, 22, fill="#eef6ef", stroke=FIELD, sw=1, rx=2))
        f.append(text(bx + (clk_step - 2)/2, 165, ssi_bits[k], size=9.5, color="#1e7a43", bold=True))

    # Зона таймауту tm
    tm_x = clk_x + 13 * clk_step + 18
    f.append(rect(tm_x, 150, 95, 22, fill="#fdf3e2", stroke="#b8801f", sw=1, rx=2))
    f.append(text(tm_x + 47, 165, "tm (10..30 мкс)", size=9.5, color="#8a5f12", bold=True))
    f.append(text(tm_x + 47, 192, "Фіксація нової позиції", size=9.5, color=MUTED))

    f.append(text(280, 214, "Перший спадний фронт CLK фіксує кут; далі біти коду Грея висуваються старшим бітом (MSB)", size=10, color=INK))

    # --- Нижня секція: BiSS-C (Continuous Mode) ---
    f.append(rect(30, 252, 780, 210, fill="#fdfefe", stroke=LINE, sw=1.4, rx=6))
    f.append(text(80, 274, "BiSS-C (Bidirectional Synchronous Serial - Continuous)", size=13, bold=True, anchor="start"))
    f.append(text(790, 274, "Двонаправлений ізохронний протокол (до 10 Мбіт/с, CRC, стан давача)", size=10.5, color=MUTED, anchor="end"))

    # Тактовий сигнал BiSS-C (MA)
    f.append(text(45, 314, "MA", size=11, bold=True, color=NEG, anchor="start"))
    f.append(line(95, 320, 785, 320, color="#dcdde1", sw=1))
    
    p_ma = "M %d %d" % (clk_x, 302)
    for k in range(16):
        p_ma += " L %d %d L %d %d L %d %d L %d %d" % (
            clk_x + k * clk_step, 302,
            clk_x + k * clk_step + 6, 320,
            clk_x + k * clk_step + 18, 320,
            clk_x + k * clk_step + 24, 302
        )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (p_ma, NEG))

    # Лінія даних BiSS-C (SLO)
    f.append(text(45, 364, "SLO", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(line(95, 370, 785, 370, color="#dcdde1", sw=1))

    # Кадр BiSS-C: Ack, Start('1'), CDS('0'), Position(10-bit), Error('1'), Warning('1'), CRC6
    slo_blocks = [
        ("Ack", 28, "#e8eaed", MUTED),
        ("Start", 36, "#fdf3e2", "#b8801f"),
        ("CDS", 28, "#e8f4f8", NEG),
        ("Position Data (MSB..LSB)", 180, "#eef6ef", FIELD),
        ("E", 20, "#fee2e2", POS),
        ("W", 20, "#fef3c7", "#d97706"),
        ("CRC6", 48, "#f3e8ff", "#7c3aed"),
        ("Timeout", 50, "#fdf3e2", "#b8801f")
    ]

    cur_bx = clk_x
    for name, bw, fill_c, strk_c in slo_blocks:
        f.append(rect(cur_bx, 350, bw - 2, 24, fill=fill_c, stroke=strk_c, sw=1.2, rx=2))
        f.append(text(cur_bx + (bw - 2)/2, 366, name, size=9.5, color=strk_c if strk_c != MUTED else INK, bold=True))
        cur_bx += bw

    # Пояснення полів BiSS-C
    f.append(text(clk_x + 18, 400, "Ack: 0 поки обробка", size=9.5, color=MUTED, anchor="start"))
    f.append(text(clk_x + 95, 400, "Start + CDS: синхронізація та біт управління", size=9.5, color=NEG, anchor="start"))
    f.append(text(clk_x + 360, 400, "E/W: статус помилки й попередження", size=9.5, color=POS, anchor="start"))
    f.append(text(clk_x + 550, 400, "CRC6: поліном x⁶+x¹+1", size=9.5, color="#7c3aed", anchor="start"))

    f.append(text(420, 444, "Кожен кадр містить повний абсолютний кут, апаратну самодіагностику (E/W) та 100% захист CRC", size=10, color="#1e7a43", bold=True))

    render(os.path.join(IMG, "fig-serial-protocols.svg"), W, H, *f)


if __name__ == "__main__":
    fig_code_disc()
    fig_binary_vs_gray()
    fig_multiturn_principles()
    fig_serial_protocols()
    print("Всі фігури згенеровано успішно.")
