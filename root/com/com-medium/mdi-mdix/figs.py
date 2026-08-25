# -*- coding: utf-8 -*-
"""Фігури до теми «MDI/MDI-X і авто-погодження».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Розпайка контактів MDI проти MDI-X та типи кабелів ────────────────────
def fig_mdi_vs_mdix_wiring():
    W, H = 940, 560
    f = [text(W / 2, 26, "Розпайка фізичних інтерфейсів Ethernet: MDI проти MDI-X", size=16, bold=True)]
    f.append(text(W / 2, 46, "Призначення контактів 8P8C (RJ45) та з'єднання прямим і перехресним кабелем для 10/100BASE-TX",
                  size=11.5, color=MUTED, italic=True))

    # Ліва колонка: Таблиця розпайки портів
    x_tab = 30
    w_tab = 290
    f.append(rect(x_tab, 70, w_tab, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(x_tab + w_tab / 2, 92, "Призначення контактів (10/100M)", size=13, bold=True, color=INK))

    headers = [("Контакт", 40), ("MDI (NIC)", 125), ("MDI-X (Switch)", 215)]
    y_h = 120
    f.append(rect(x_tab + 10, y_h - 14, w_tab - 20, 24, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=3))
    for h_name, h_x in headers:
        f.append(text(x_tab + h_x, y_h + 3, h_name, size=11, bold=True, color=INK))

    pins_data = [
        ("1", "TX+ (Передавання +)", "RX+ (Прийом +)", POS, NEG),
        ("2", "TX− (Передавання −)", "RX− (Прийом −)", POS, NEG),
        ("3", "RX+ (Прийом +)", "TX+ (Передавання +)", NEG, POS),
        ("4", "Не використовується", "Не використовується", MUTED, MUTED),
        ("5", "Не використовується", "Не використовується", MUTED, MUTED),
        ("6", "RX− (Прийом −)", "TX− (Передавання −)", NEG, POS),
        ("7", "Не використовується", "Не використовується", MUTED, MUTED),
        ("8", "Не використовується", "Не використовується", MUTED, MUTED),
    ]

    for i, (p_num, mdi_sig, mdix_sig, c_mdi, c_mdix) in enumerate(pins_data):
        yp = 150 + i * 40
        is_active = p_num in ["1", "2", "3", "6"]
        row_bg = "#ffffff" if i % 2 == 0 else "#f1f5f9"
        if is_active:
            row_bg = "#fef2f2" if p_num in ["1", "2"] else "#eff6ff"
        f.append(rect(x_tab + 10, yp - 14, w_tab - 20, 36, fill=row_bg, stroke="#e2e8f0", sw=1.0, rx=3))
        f.append(text(x_tab + 40, yp + 9, "Pin " + p_num, size=11, bold=True, color=INK))
        f.append(text(x_tab + 125, yp + 4, mdi_sig.split(" ")[0], size=11, bold=True, color=c_mdi))
        f.append(text(x_tab + 125, yp + 16, mdi_sig.split(" ")[1] if len(mdi_sig.split(" ")) > 1 else "", size=9.0, color=MUTED))
        f.append(text(x_tab + 215, yp + 4, mdix_sig.split(" ")[0], size=11, bold=True, color=c_mdix))
        f.append(text(x_tab + 215, yp + 16, mdix_sig.split(" ")[1] if len(mdix_sig.split(" ")) > 1 else "", size=9.0, color=MUTED))

    f.append(text(x_tab + w_tab / 2, 495, "1000BASE-T (Gigabit) використовує", size=10, bold=True, color=INK))
    f.append(text(x_tab + w_tab / 2, 512, "усі 4 пари двонаправлено (BI_DA..DB)", size=9.5, color=MUTED))

    # Права верхня секція: Прямий кабель (Straight-Through: NIC -> Switch)
    x_right = 345
    w_right = 565
    f.append(rect(x_right, 70, w_right, 220, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(x_right + 15, 92, "1. З'єднання комп'ютер — комутатор: Прямий кабель (Straight-Through)", size=12.5, bold=True, color=INK, anchor="start"))
    f.append(text(x_right + 15, 108, "MDI (ПК) з'єднується з MDI-X (комутатор). Обидва кінці обтиснуті за єдиним стандартом (T568B).", size=10.5, color=MUTED, anchor="start"))

    # Блоки ПК і Комутатора
    y_s = 145
    f.append(textbox(x_right + 70, y_s + 40, "Комп'ютер (NIC)\nПорт MDI\nTX: 1-2 | RX: 3-6", size=10.5, bold=True, fill="#fff1f2", stroke=POS)[0])
    f.append(textbox(x_right + w_right - 75, y_s + 40, "Комутатор (Switch)\nПорт MDI-X\nRX: 1-2 | TX: 3-6", size=10.5, bold=True, fill="#f0fdf4", stroke=FIELD)[0])

    # Лінії прямого кабелю
    x_l = x_right + 140
    x_r = x_right + w_right - 150
    # TX (1,2) -> RX (1,2)
    f.append(arrow(x_l, y_s + 20, x_r, y_s + 20, color=POS, sw=2.0))
    f.append(text((x_l + x_r) / 2, y_s + 13, "Пара 1-2: Передавання TX (ПК) ──► Прийом RX (Комутатор)", size=10, bold=True, color=POS))
    # RX (3,6) <- TX (3,6)
    f.append(arrow(x_r, y_s + 60, x_l, y_s + 60, color=NEG, sw=2.0))
    f.append(text((x_l + x_r) / 2, y_s + 53, "Пара 3-6: Прийом RX (ПК) ◄── Передавання TX (Комутатор)", size=10, bold=True, color=NEG))

    # Права нижня секція: Кросоверний кабель (Crossover: NIC -> NIC або Switch -> Switch)
    y_c_box = 305
    f.append(rect(x_right, y_c_box, w_right, 225, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(x_right + 15, y_c_box + 22, "2. З'єднання однотипних портів: Перехресний кабель (Crossover)", size=12.5, bold=True, color=INK, anchor="start"))
    f.append(text(x_right + 15, y_c_box + 38, "MDI — MDI (або MDI-X — MDI-X). Один кінець — T568A, другий — T568B (перехрещує пари 1-2 та 3-6).", size=10.5, color=MUTED, anchor="start"))

    y_c = y_c_box + 70
    f.append(textbox(x_right + 70, y_c + 40, "Комп'ютер A (NIC)\nПорт MDI\nTX: 1-2 | RX: 3-6", size=10.5, bold=True, fill="#fff1f2", stroke=POS)[0])
    f.append(textbox(x_right + w_right - 75, y_c + 40, "Комп'ютер B (NIC)\nПорт MDI\nTX: 1-2 | RX: 3-6", size=10.5, bold=True, fill="#fff1f2", stroke=POS)[0])

    # Схрещені лінії
    f.append(line(x_l, y_c + 20, x_l + 70, y_c + 20, color=POS, sw=2.0))
    f.append(line(x_l + 70, y_c + 20, x_r - 70, y_c + 60, color=POS, sw=2.0))
    f.append(arrow(x_r - 70, y_c + 60, x_r, y_c + 60, color=POS, sw=2.0))
    f.append(text((x_l + x_r) / 2 + 10, y_c + 32, "TX (1-2) переходить на RX (3-6)", size=9.5, bold=True, color=POS))

    f.append(line(x_r, y_c + 20, x_r - 70, y_c + 20, color=NEG, sw=2.0))
    f.append(line(x_r - 70, y_c + 20, x_l + 70, y_c + 60, color=NEG, sw=2.0))
    f.append(arrow(x_l + 70, y_c + 60, x_l, y_c + 60, color=NEG, sw=2.0))
    f.append(text((x_l + x_r) / 2 - 10, y_c + 75, "RX (3-6) приймає від TX (1-2)", size=9.5, bold=True, color=NEG))

    return render(os.path.join(IMG, "mdi-vs-mdix-wiring.svg"), W, H, *f)


# ── 2. Архітектура та робота Auto-MDIX ────────────────────────────────────────
def fig_auto_mdix_switching():
    W, H = 940, 520
    f = [text(W / 2, 26, "Внутрішня архітектура та автомат станів Auto-MDIX", size=16, bold=True)]
    f.append(text(W / 2, 46, "Електронна матриця перемикання пар у PHY та алгоритм псевдовипадкового таймера для уникнення взаємного блокування",
                  size=11.5, color=MUTED, italic=True))

    # Ліва частина: Електронний кросбар у мікросхемі PHY
    x_phy = 30
    w_phy = 430
    f.append(rect(x_phy, 70, w_phy, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(x_phy + w_phy / 2, 95, "Апаратний матричний перемикач PHY", size=13, bold=True, color=INK))

    # Роз'єм RJ45 (зсунуто вправо, щоб поміститися всередині x_phy..x_phy+w_phy)
    f.append(textbox(x_phy + 65, 180, "RJ45\nПара 1-2\n(Контакти 1,2)", size=9.5, bold=True, fill="#e2e8f0", stroke="#94a3b8")[0])
    f.append(textbox(x_phy + 65, 360, "RJ45\nПара 3-6\n(Контакти 3,6)", size=9.5, bold=True, fill="#e2e8f0", stroke="#94a3b8")[0])

    # Кросбар перемикач
    f.append(rect(x_phy + 130, 130, 150, 300, fill="#ffffff", stroke="#6366f1", sw=1.8, rx=5))
    f.append(text(x_phy + 205, 150, "Аналоговий кросбар", size=11, bold=True, color="#4338ca"))
    f.append(text(x_phy + 205, 168, "Керується логікою Auto-MDIX", size=9.5, color=MUTED))

    # Внутрішні блоки PHY (TX Драйвер та RX Підсилювач/Детектор)
    f.append(textbox(x_phy + 355, 200, "TX Драйвер\n(Передавач PHY)\nFLP / 100M / 1G", size=9.5, bold=True, fill="#fef2f2", stroke=POS)[0])
    f.append(textbox(x_phy + 355, 330, "RX Підсилювач\nта енергодетектор\n(Приймач PHY)", size=9.5, bold=True, fill="#eff6ff", stroke=NEG)[0])

    # Доріжки кросбару
    f.append(line(x_phy + 115, 180, x_phy + 145, 180, color=LINE, sw=1.8))
    f.append(line(x_phy + 115, 360, x_phy + 145, 360, color=LINE, sw=1.8))

    # Перемикачі всередині
    f.append(circle(x_phy + 145, 180, 3.5, fill=LINE, stroke=LINE))
    f.append(circle(x_phy + 145, 360, 3.5, fill=LINE, stroke=LINE))

    # Контакти прямого та перехресного режиму
    f.append(circle(x_phy + 240, 200, 3.5, fill=POS, stroke=POS))
    f.append(circle(x_phy + 240, 330, 3.5, fill=NEG, stroke=NEG))

    # Прямий шлях (суцільний)
    f.append(line(x_phy + 145, 180, x_phy + 236, 199, color=POS, sw=2.2))
    f.append(line(x_phy + 145, 360, x_phy + 236, 331, color=NEG, sw=2.2))
    f.append(arrow(x_phy + 240, 200, x_phy + 300, 200, color=POS, sw=1.8))
    f.append(arrow(x_phy + 240, 330, x_phy + 300, 330, color=NEG, sw=1.8))

    # Перехресний шлях (пунктир)
    f.append(line(x_phy + 145, 180, x_phy + 236, 325, color=NEG, sw=1.5, dash="4,4"))
    f.append(line(x_phy + 145, 360, x_phy + 236, 205, color=POS, sw=1.5, dash="4,4"))

    f.append(text(x_phy + 205, 400, "— Прямий режим (MDI)", size=9.5, bold=True, color=LINE))
    f.append(text(x_phy + 205, 416, "┈┈ Перехресний (MDI-X)", size=9.5, bold=True, color=MUTED))

    # Права частина: Алгоритм випадкового таймера розв'язання колізій
    x_alg = 480
    w_alg = 430
    f.append(rect(x_alg, 70, w_alg, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(x_alg + w_alg / 2, 95, "Алгоритм розв'язання колізії Auto-MDIX", size=13, bold=True, color=INK))

    # Блоки алгоритму
    cx_alg = x_alg + w_alg / 2
    y_b1 = 125
    f.append(textbox(cx_alg - 40, y_b1 + 20, "1. Початковий стан: MDI (прямий режим)\nПередача на 1-2, прослуховування на 3-6", size=10, bold=True, fill="#ffffff", stroke="#94a3b8")[0])

    y_b2 = y_b1 + 75
    f.append(arrow(cx_alg - 40, y_b1 + 45, cx_alg - 40, y_b2, color=LINE, sw=1.5))
    f.append(textbox(cx_alg - 40, y_b2 + 20, "2. Перевірка: чи є сигнал на парі 3-6?\n(Енергія FLP/NLP або 100M несучої)", size=10, bold=True, fill="#fffbeb", stroke="#f59e0b")[0])

    # Гілка ТАК -> Лінк
    f.append(arrow(cx_alg + 85, y_b2 + 20, cx_alg + 125, y_b2 + 20, color=FIELD, sw=1.5))
    f.append(text(cx_alg + 105, y_b2 + 13, "ТАК", size=9.5, bold=True, color=FIELD))
    f.append(textbox(x_alg + w_alg - 55, y_b2 + 20, "Фіксація!\nЛінк піднято", size=9.5, bold=True, fill="#f0fdf4", stroke=FIELD)[0])

    # Гілка НІ -> Таймер
    y_b3 = y_b2 + 80
    f.append(arrow(cx_alg - 40, y_b2 + 45, cx_alg - 40, y_b3, color=LINE, sw=1.5))
    f.append(text(cx_alg - 15, y_b2 + 60, "НІ (таймаут)", size=9.5, color=POS))
    f.append(textbox(cx_alg - 40, y_b3 + 25, "3. Випадковий таймер T_sample\n62 мс ± 16 мс (псевдовипадкове число LFSR)\nЗапобігає синхронному перемиканню кінців", size=9.5, bold=True, fill="#fef2f2", stroke=POS)[0])

    y_b4 = y_b3 + 85
    f.append(arrow(cx_alg - 40, y_b3 + 55, cx_alg - 40, y_b4, color=LINE, sw=1.5))
    f.append(textbox(cx_alg - 40, y_b4 + 20, "4. Інверсія: перемикання MDI ↔ MDI-X\nTX переходить на 3-6, RX — на 1-2", size=9.5, bold=True, fill="#ffffff", stroke="#6366f1")[0])

    # Петля зворотного зв'язку
    f.append(line(cx_alg - 180, y_b4 + 20, x_alg + 15, y_b4 + 20, color=MUTED, sw=1.2))
    f.append(line(x_alg + 15, y_b4 + 20, x_alg + 15, y_b2 + 20, color=MUTED, sw=1.2))
    f.append(arrow(x_alg + 15, y_b2 + 20, cx_alg - 165, y_b2 + 20, color=MUTED, sw=1.2))

    return render(os.path.join(IMG, "auto-mdix-switching.svg"), W, H, *f)


# ── 3. Структура пачки FLP та Base Page ───────────────────────────────────────
def fig_flp_burst_encoding():
    W, H = 940, 560
    f = [text(W / 2, 26, "Імпульсна пачка FLP (Fast Link Pulse) та сторінка Base Page", size=16, bold=True)]
    f.append(text(W / 2, 46, "Сумісність із 10BASE-T NLP та часове кодування 16-бітного слова погодження можливостей (IEEE 802.3u)",
                  size=11.5, color=MUTED, italic=True))

    # Верхня часова діаграма
    x0, y_time = 50, 80
    w_diag = 840
    f.append(rect(x0, y_time, w_diag, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(x0 + 15, y_time + 22, "Часова діаграма пачки FLP (інтервал передачі — кожні 16 ± 8 мс)", size=12.5, bold=True, color=INK, anchor="start"))

    # Базова лінія напруги
    y_sig = y_time + 100
    f.append(line(x0 + 30, y_sig, x0 + w_diag - 30, y_sig, color="#cbd5e1", sw=1.5))

    # Малюємо тактові (Clock) та інформаційні (Data) імпульси
    t_start = x0 + 60
    dx_clk = 45

    # 17 тактових імпульсів, чергуються з бітами
    sample_bits = [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0] # 16 бітів
    for i in range(17):
        cx = t_start + i * dx_clk
        # Clock pulse (червоний/синій короткий сплеск 100 нс)
        f.append(line(cx, y_sig, cx, y_sig - 35, color=POS, sw=2.2))
        f.append(circle(cx, y_sig - 35, 2.5, fill=POS, stroke=POS))
        f.append(text(cx, y_sig - 43, "C" + str(i + 1), size=9.0, bold=True, color=POS))

        # Data pulse між C_i та C_{i+1}
        if i < 16:
            dx = cx + dx_clk / 2
            bit_val = sample_bits[i]
            if bit_val == 1:
                # Є імпульс даних
                f.append(line(dx, y_sig, dx, y_sig - 24, color=NEG, sw=1.8))
                f.append(circle(dx, y_sig - 24, 2.0, fill=NEG, stroke=NEG))
                f.append(text(dx, y_sig - 30, "D" + str(i) + "=1", size=9.0, bold=True, color=NEG))
            else:
                # Немає імпульсу (0)
                f.append(text(dx, y_sig + 15, "0", size=9.5, color=MUTED))

    # Розмірні стрілки для часових інтервалів
    y_dim = y_sig + 40
    c1_x = t_start
    c2_x = t_start + dx_clk
    f.append(line(c1_x, y_dim, c2_x, y_dim, color=LINE, sw=1.2))
    f.append(line(c1_x, y_sig + 10, c1_x, y_dim + 6, color="#94a3b8", sw=1.0))
    f.append(line(c2_x, y_sig + 10, c2_x, y_dim + 6, color="#94a3b8", sw=1.0))
    f.append(text((c1_x + c2_x) / 2, y_dim + 14, "T_clk = 125 мкс", size=9.5, bold=True, color=INK))

    d1_x = t_start + dx_clk / 2
    f.append(text(d1_x + 8, y_dim - 18, "62.5 мкс", size=9.0, color=MUTED))

    f.append(text(x0 + w_diag - 120, y_time + 40, "Пачка FLP: 2.1 мс\n(17 тактів + до 16 бітів)", size=10, bold=True, color=INK))

    # Нижня частина: Формат 16-бітної сторінки Base Page
    y_bp = 275
    f.append(rect(x0, y_bp, w_diag, 260, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(x0 + 15, y_bp + 22, "Формат 16-бітного слова Base Page (IEEE 802.3 Clause 28)", size=12.5, bold=True, color=INK, anchor="start"))

    # Сітка бітів Base Page (розрахована так, щоб уміститися в w_diag - 30 = 810)
    fields = [
        ("D0..D4 (5 бітів)", "Поле селектора\n00001 = IEEE 802.3", "#eff6ff", NEG, 135),
        ("D5..D12 (8 бітів)", "Технологічні можливості\n10/100M, Pause", "#fef2f2", POS, 340),
        ("D13 (1 біт)", "Remote Fault\nАварія", "#fffbeb", "#d97706", 100),
        ("D14 (1 біт)", "ACK\nПідтвердження", "#f0fdf4", FIELD, 115),
        ("D15 (1 біт)", "Next Page\nНаступна", "#f5f3ff", "#7c3aed", 100),
    ]

    bx_cur = x0 + 15
    y_f = y_bp + 45
    for f_title, f_desc, f_bg, f_color, f_w in fields:
        f.append(rect(bx_cur, y_f, f_w, 42, fill=f_bg, stroke=f_color, sw=1.4, rx=4))
        f.append(text(bx_cur + f_w / 2, y_f + 18, f_title, size=10.5, bold=True, color=f_color))
        f.append(text(bx_cur + f_w / 2, y_f + 32, f_desc.split("\n")[0], size=9.0, color=INK))
        bx_cur += f_w + 5

    # Розшифровка бітів Technology Ability Field
    y_tech = y_bp + 105
    f.append(rect(x0 + 15, y_tech, w_diag - 30, 140, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    f.append(text(x0 + 30, y_tech + 18, "Деталізація розрядів Technology Ability Field (D5..D12):", size=11, bold=True, color=INK, anchor="start"))

    tech_bits = [
        ("D5", "10BASE-T Half Duplex (HD)"),
        ("D6", "10BASE-T Full Duplex (FD)"),
        ("D7", "100BASE-TX Half Duplex (HD)"),
        ("D8", "100BASE-TX Full Duplex (FD)"),
        ("D9", "100BASE-T4 (4 пари Cat3)"),
        ("D10", "PAUSE (симетричний потік керування 802.3x)"),
        ("D11", "Asymmetric PAUSE (асиметричний потік)"),
        ("D12", "Зарезервовано для розширень стандарту"),
    ]

    for idx, (b_name, b_desc) in enumerate(tech_bits):
        col = idx // 4
        row = idx % 4
        px = x0 + 30 + col * 400
        py = y_tech + 42 + row * 24
        f.append(rect(px, py - 12, 35, 20, fill="#fee2e2", stroke=POS, sw=1.0, rx=3))
        f.append(text(px + 17.5, py + 2, b_name, size=9.5, bold=True, color=POS))
        f.append(text(px + 45, py + 2, b_desc, size=10, color=INK, anchor="start"))

    return render(os.path.join(IMG, "flp-burst-encoding.svg"), W, H, *f)


# ── 4. Механізм розсинхронізації дуплексу (Duplex Mismatch) ────────────────────
def fig_duplex_mismatch_collision():
    W, H = 940, 560
    f = [text(W / 2, 26, "Механізм та наслідки розсинхронізації дуплексу (Duplex Mismatch)", size=16, bold=True)]
    f.append(text(W / 2, 46, "Чому виникають пізні колізії (Late Collisions), втрачаються кадри і колапсує пропускна здатність TCP",
                  size=11.5, color=MUTED, italic=True))

    x0, y0 = 40, 75
    w_box = 860

    # Заголовок вузлів
    f.append(textbox(x0 + 130, y0 + 25, "Вузол A: Full Duplex (FD)\n(Примусово або комутатор)\nCSMA/CD ВИМКНЕНО\nПередає будь-коли!", size=10.5, bold=True, fill="#eff6ff", stroke=NEG)[0])
    f.append(textbox(x0 + w_box - 130, y0 + 25, "Вузол B: Half Duplex (HD)\n(Внаслідок Parallel Detection)\nCSMA/CD УВІМКНЕНО\nСлухає колізії (RX+TX)", size=10.5, bold=True, fill="#fff1f2", stroke=POS)[0])

    # Часова шкала (Timeline) зверху вниз
    tl_x_a = x0 + 130
    tl_x_b = x0 + w_box - 130
    tl_y_start = y0 + 75
    tl_y_end = y0 + 440

    f.append(line(tl_x_a, tl_y_start, tl_x_a, tl_y_end, color=NEG, sw=2.0))
    f.append(line(tl_x_b, tl_y_start, tl_x_b, tl_y_end, color=POS, sw=2.0))

    # Крок 1: Вузол B починає передавання кадру (лінія чиста)
    t1 = tl_y_start + 30
    f.append(text(tl_x_b + 15, t1, "1. Вузол B перевіряє лінію (вільно) і починає передачу кадру", size=10, bold=True, color=POS, anchor="start"))
    f.append(arrow(tl_x_b, t1 + 10, tl_x_a + 20, t1 + 45, color=POS, sw=2.0))
    f.append(text((tl_x_a + tl_x_b) / 2, t1 + 20, "Кадр від B ──► (передано 64 байти / вікно колізії минуло)", size=9.5, color=POS))

    # Крок 2: Вузол A хоче передати кадр. У FD він НЕ слухає лінію!
    t2 = t1 + 65
    f.append(text(tl_x_a - 15, t2, "2. Вузол A отримує пакет від ОС і починає передачу!", size=10, bold=True, color=NEG, anchor="end"))
    f.append(text(tl_x_a - 15, t2 + 14, "(Full Duplex не виконує Carrier Sense)", size=9, color=MUTED, anchor="end"))
    f.append(arrow(tl_x_a, t2 + 10, tl_x_b - 20, t2 + 45, color=NEG, sw=2.0))

    # Крок 3: Колізія на боці вузла B
    t3 = t2 + 55
    col_x = tl_x_b - 50
    f.append(circle(col_x, t3, 14, fill="#fee2e2", stroke=POS, sw=2.0))
    f.append(text(col_x, t3 + 4, "💥", size=14))
    f.append(text(col_x + 25, t3 - 4, "3. КОЛІЗІЯ на вузлі B!", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(col_x + 25, t3 + 12, "Сталася після передачі 64 байтів (Late Collision)", size=9.5, bold=True, color=POS, anchor="start"))

    # Крок 4: Наслідки для MAC та TCP
    t4 = t3 + 60
    f.append(textbox(W / 2, t4 + 30, "Катастрофічні наслідки Duplex Mismatch на мережевих рівнях:\n"
                                     "• Half Duplex (B) фіксує Late Collision: MAC НЕ ПОВТОРЮЄ передачу (кадр викидається);\n"
                                     "• Full Duplex (A) отримує понівечений фрагмент: викидає через помилку FCS / CRC;\n"
                                     "• Ping (ICMP) проходить (1 пакет/с, нульова ймовірність колізії), але потік TCP гине:\n"
                                     "  втрати пакетів ACK викликають таймаути RTO, вікно згортається до 1 MSS, швидкість падає до нуля!",
                     size=10, bold=False, fill="#fffbeb", stroke="#f59e0b")[0])

    return render(os.path.join(IMG, "duplex-mismatch-collision.svg"), W, H, *f)


if __name__ == "__main__":
    fig_mdi_vs_mdix_wiring()
    fig_auto_mdix_switching()
    fig_flp_burst_encoding()
    fig_duplex_mismatch_collision()
    print("All figures generated successfully.")
