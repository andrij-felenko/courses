# -*- coding: utf-8 -*-
"""Фігури до теми «Активні USB-кабелі».
Імпортує спільний svgkit зі scripts/. Вивід — у ./img/.
Запуск:  python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Згасання частот та відновлення ока (Пасивний vs Редрайвер vs Ретаймер) ──
def fig_attenuation_eye():
    W, H = 840, 500
    parts = []

    # Заголовок зверху
    parts.append(text(W / 2, 28, "Деградація сигналу в кабелі та механізми його відновлення", size=14, bold=True))

    # 4 блоки: Джерело -> Пасивний кабель -> Редрайвер -> Ретаймер
    cols = [
        (115, "1. Вихід передавача", "(чистий Tx сигнал)", "#eaf3ea", FIELD),
        (325, "2. Після 2 м пасивної міді", "(скін-ефект + діелектрик)", "#fdecea", POS),
        (535, "3. Вихід редрайвера", "(аналоговий CTLE-буст)", "#fef7e6", "#d97706"),
        (735, "4. Вихід ретаймера", "(повний реклокінг CDR)", "#eaf0fd", NEG),
    ]

    for cx, title_s, sub_s, bg_col, stroke_col in cols:
        # Заголовок колонки
        parts.append(rect(cx - 95, 50, 190, 42, fill=bg_col, stroke=stroke_col, sw=1.5, rx=6))
        parts.append(text(cx, 68, title_s, size=11, bold=True, color=stroke_col))
        parts.append(text(cx, 84, sub_s, size=9.5, color=MUTED, italic=True))

        # Рамка для осцилограми / ока
        parts.append(rect(cx - 95, 100, 190, 100, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))

    # Стрілки між колонками зверху
    parts.append(arrow(212, 150, 228, 150, color=MUTED, sw=2))
    parts.append(arrow(422, 150, 438, 150, color=MUTED, sw=2))
    parts.append(arrow(632, 150, 648, 150, color=MUTED, sw=2))

    # 1. Джерело: відкрите ідеальне око
    cx1 = 115
    parts.append(line(cx1 - 85, 150, cx1 + 85, 150, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx1, 108, cx1, 192, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx1 - 70, 120, cx1 + 70, 120, color=FIELD, sw=2))
    parts.append(line(cx1 - 70, 180, cx1 + 70, 180, color=FIELD, sw=2))
    parts.append(line(cx1 - 65, 180, cx1 + 65, 120, color=FIELD, sw=2))
    parts.append(line(cx1 - 65, 120, cx1 + 65, 180, color=FIELD, sw=2))
    parts.append(textbox(cx1, 226, "Широке відкрите око · Джитер = 0", size=9.5, fill="#f4fbf5", stroke=FIELD, bold=True, color=FIELD)[0])

    # 2. Пасивний кабель: розмазане закрите око
    cx2 = 325
    parts.append(line(cx2 - 85, 150, cx2 + 85, 150, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx2, 108, cx2, 192, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx2 - 70, 138, cx2 + 70, 138, color=POS, sw=2, dash="2 2"))
    parts.append(line(cx2 - 70, 162, cx2 + 70, 162, color=POS, sw=2, dash="2 2"))
    parts.append(line(cx2 - 65, 166, cx2 + 65, 134, color=POS, sw=2))
    parts.append(line(cx2 - 65, 134, cx2 + 65, 166, color=POS, sw=2))
    parts.append(line(cx2 - 65, 156, cx2 + 65, 144, color=POS, sw=2))
    parts.append(line(cx2 - 65, 144, cx2 + 65, 156, color=POS, sw=2))
    parts.append(textbox(cx2, 226, "ОКО СТУЛЕНО · Висота < 20 мВ", size=9.5, fill="#fdf2f2", stroke=POS, bold=True, color=POS)[0])

    # 3. Редрайвер: підсилена амплітуда, але розмиті фронти
    cx3 = 535
    parts.append(line(cx3 - 85, 150, cx3 + 85, 150, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx3, 108, cx3, 192, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx3 - 70, 122, cx3 + 70, 122, color="#d97706", sw=2.2))
    parts.append(line(cx3 - 70, 178, cx3 + 70, 178, color="#d97706", sw=2.2))
    parts.append(line(cx3 - 65, 178, cx3 + 45, 122, color="#d97706", sw=1.8))
    parts.append(line(cx3 - 45, 178, cx3 + 65, 122, color="#d97706", sw=1.8))
    parts.append(line(cx3 - 65, 122, cx3 + 45, 178, color="#d97706", sw=1.8))
    parts.append(line(cx3 - 45, 122, cx3 + 65, 178, color="#d97706", sw=1.8))
    parts.append(textbox(cx3, 226, "Амплітуда є · Шум і джитер лишились", size=9.5, fill="#fffbeb", stroke="#d97706", bold=True, color="#d97706")[0])

    # 4. Ретаймер: чисте синтезоване око
    cx4 = 735
    parts.append(line(cx4 - 85, 150, cx4 + 85, 150, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx4, 108, cx4, 192, color="#e5e7eb", sw=1, dash="3 3"))
    parts.append(line(cx4 - 70, 120, cx4 + 70, 120, color=NEG, sw=2))
    parts.append(line(cx4 - 70, 180, cx4 + 70, 180, color=NEG, sw=2))
    parts.append(line(cx4 - 65, 180, cx4 + 65, 120, color=NEG, sw=2))
    parts.append(line(cx4 - 65, 120, cx4 + 65, 180, color=NEG, sw=2))
    parts.append(textbox(cx4, 226, "Ідеальне око · Новий такт CDR", size=9.5, fill="#eff6ff", stroke=NEG, bold=True, color=NEG)[0])

    # Нижня частина: порівняльна аналітична панель
    parts.append(rect(20, 260, 800, 226, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    parts.append(text(W / 2, 282, "Порівняння фізичних механізмів обробки сигналу", size=12.5, bold=True))

    rows = [
        ("Властивість", "Пасивний дріт", "Редрайвер (Re-driver)", "Ретаймер (Re-timer)", True),
        ("Принцип дії", "Пряме згасання (R, L, G, C)", "Аналоговий еквалайзер CTLE + VGA", "Повний PHY-рівень: CTLE + CDR + PLL + Tx"),
        ("Амплітуда сигналу", "Згасає (до -25 дБ на 10 ГГц)", "Відновлюється аналоговим бустом", "Генерується наново передавачем Tx"),
        ("Фазовий джитер (jitter)", "Накопичується пропорційно довжині", "НЕ усувається (підсилюється разом із шумом)", "ПОВНІСТЮ скидається новим тактом PLL"),
        ("Затримка (latency)", "Мінімальна (~5 нс/м, швидкість світла)", "Ультранизька (< 100 пс на чип)", "Помітна (10–100 нс на десеріалізацію)"),
        ("Участь у протоколі", "Невидимий (прозорий мідний дріт)", "Невидимий для логіки протоколу", "Адресується в USB4/TB, керує станами живлення"),
    ]

    ry = 302
    for r_idx, r_data in enumerate(rows):
        is_h = len(r_data) == 5
        bg_r = "#e2e8f0" if is_h else ("#ffffff" if r_idx % 2 == 1 else "#f8fafc")
        parts.append(rect(30, ry, 780, 24, fill=bg_r, stroke="#cbd5e1", sw=0.8, rx=3))
        col_w = [140, 180, 220, 240]
        cur_x = 30
        for c_idx, cell_txt in enumerate(r_data[:4]):
            tx = cur_x + col_w[c_idx] / 2
            f_col = INK if not is_h else "#0f172a"
            parts.append(text(tx, ry + 16, cell_txt, size=10 if not is_h else 10.5, bold=is_h, color=f_col))
            cur_x += col_w[c_idx]
        ry += 26

    render(os.path.join(IMG, "attenuation-eye.svg"), W, H, *parts,
           title="Деградація сигналу в кабелі та його відновлення")


# ── 2. Внутрішня анатомія активного кабелю USB-C ──────────────────────────────
def fig_active_cable_anatomy():
    W, H = 840, 470
    parts = []

    parts.append(text(W / 2, 28, "Внутрішня архітектура активного комбінованого кабелю USB-C", size=14, bold=True))

    # Лівий штекер (Штекер А - Джерело / DFP)
    parts.append(rect(20, 50, 250, 390, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    parts.append(rect(30, 60, 230, 32, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(145, 81, "Штекер А (DFP / Host)", size=12, bold=True, color=INK))

    # Компоненти всередині штекера А
    parts.append(fitbox(35, 104, 220, 52, "E-Marker (SOP' контролер)\nІдентифікація, VDO, PD 3.1\nВідповідає на запити хоста", size=10, fill="#eaf3ea", stroke=FIELD, bold=False))
    parts.append(fitbox(35, 166, 220, 64, "Сигнальний процесор (IC)\nРетаймер / Редрайвер або\nОптоелектронний трансивер\n(VCSEL лазер + TIA фотодіод)", size=10, fill="#eff6ff", stroke=NEG, bold=False))
    parts.append(fitbox(35, 240, 220, 52, "Живлення електроніки\nВхід VCONN (3.0–5.5 В)\nStep-Down Buck + LDO (1.0 В, 1.8 В)", size=10, fill="#fef7e6", stroke="#d97706", bold=False))
    parts.append(fitbox(35, 302, 220, 60, "Тепловий розподільник\nМідні термополігони PCB +\nТеплопровідний компаунд штекера", size=10, fill="#fdecea", stroke=POS, bold=False))
    parts.append(fitbox(35, 372, 220, 56, "Контакти роз'єму Type-C\nVBUS, GND, CC1, CC2/VCONN,\nSBU1/2, D+/D-, SSTX1/2, SSRX1/2", size=9.5, fill="#ffffff", stroke=LINE, bold=False))

    # Правий штекер (Штекер B - Приймач / UFP)
    parts.append(rect(570, 50, 250, 390, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    parts.append(rect(580, 60, 230, 32, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(695, 81, "Штекер B (UFP / Device)", size=12, bold=True, color=INK))

    # Компоненти всередині штекера B
    parts.append(fitbox(585, 104, 220, 52, "SOP'' контролер (опція)\nІдентифікація другого кінця\nКанальний статус Plug B", size=10, fill="#eaf3ea", stroke=FIELD, bold=False))
    parts.append(fitbox(585, 166, 220, 64, "Сигнальний процесор (IC)\nРетаймер / Редрайвер або\nОптоелектронний приймач/Tx\n(TIA фотодіод + VCSEL лазер)", size=10, fill="#eff6ff", stroke=NEG, bold=False))
    parts.append(fitbox(585, 240, 220, 52, "Живлення електроніки\nЖивлення від VCONN кабелю\nМісцевий стабілізатор LDO", size=10, fill="#fef7e6", stroke="#d97706", bold=False))
    parts.append(fitbox(585, 302, 220, 60, "Тепловий розподільник\nРозсіювання тепла ретаймера\n(до 1.0–1.5 Вт у тісному об'ємі)", size=10, fill="#fdecea", stroke=POS, bold=False))
    parts.append(fitbox(585, 372, 220, 56, "Контакти роз'єму Type-C\nVBUS, GND, CC, SBU1/2,\nD+/D-, SSTX1/2, SSRX1/2", size=9.5, fill="#ffffff", stroke=LINE, bold=False))

    # Середня частина: Джгут кабелю (Гібридна структура)
    parts.append(rect(290, 75, 260, 345, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(420, 96, "Гібридний джгут кабелю (до 5–50 м)", size=11, bold=True, color=INK))

    cable_lines = [
        ("VBUS (Силова мідь, 5–48 В, до 5 А)", POS, 122),
        ("GND (Земля живлення й зворотний струм)", INK, 156),
        ("CC / VCONN дріт (керування й живлення)", "#d97706", 190),
        ("SBU1 / SBU2 (Sideband службові лінії)", MUTED, 224),
        ("USB 2.0 D+ / D- (екранована вита пара)", FIELD, 258),
        ("Швидкісні лінії SSTX / SSRX (4 пари)", NEG, 304),
        ("• В ACC: мікрокоаксіали з ретаймером", NEG, 332),
        ("• В AOC: оптичні волокна OM3/OM4", NEG, 356),
        ("Загальний металевий екран + обплетення", "#64748b", 394),
    ]

    for lbl, col, ly in cable_lines:
        if "•" in lbl:
            parts.append(text(420, ly, lbl, size=9.5, color=col, italic=True))
        elif "Швидкісні" in lbl:
            parts.append(text(420, ly, lbl, size=10.5, bold=True, color=col))
        else:
            parts.append(line(270, ly, 570, ly, color=col, sw=2))
            parts.append(textbox(420, ly, lbl, size=9.5, fill="#ffffff", stroke=col, bold=False)[0])

    render(os.path.join(IMG, "active-cable-anatomy.svg"), W, H, *parts,
           title="Анатомія активного комбінованого кабелю USB-C")


# ── 3. Розподіл живлення: ізоляція VCONN від VBUS ─────────────────────────────
def fig_vconn_power_routing():
    W, H = 820, 460
    parts = []

    parts.append(text(W / 2, 26, "Топологія живлення активного кабелю: ізоляція шин VCONN та VBUS", size=14, bold=True))

    # Ліва частина - Хост (Host / DFP)
    parts.append(rect(20, 52, 210, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    parts.append(text(125, 76, "Джерело (Host / DFP)", size=12.5, bold=True, color=INK))

    parts.append(fitbox(30, 96, 190, 72, "Силове джерело VBUS\nPD Контракт: 5 В / 9 В /\n15 В / 20 В / 48 В (EPR)\nСтрум до 5 А (до 240 Вт)", size=10, fill="#fdecea", stroke=POS))
    parts.append(fitbox(30, 182, 190, 72, "PD Контролер (CC1)\nПереговори SOP\nBMC кодування 300 кбіт/с\nRp підтяжка", size=10, fill="#eaf3ea", stroke=FIELD))
    parts.append(fitbox(30, 268, 190, 78, "Джерело VCONN (CC2)\nФіксовані 5.0 В (3.0–5.5 В)\nПотужність 1.0–1.5 Вт\nІзольований ключ живлення", size=10, fill="#fef7e6", stroke="#d97706"))
    parts.append(fitbox(30, 360, 190, 70, "Швидкісний PHY Хоста\nTX1/2 та RX1/2\nPCIe / USB4 / DP тунелі", size=10, fill="#eff6ff", stroke=NEG))

    # Права частина - Пристрій (Device / UFP)
    parts.append(rect(590, 52, 210, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    parts.append(text(695, 76, "Приймач (Device / UFP)", size=12.5, bold=True, color=INK))

    parts.append(fitbox(600, 96, 190, 72, "Силовий стік VBUS\nПриймає узгоджену напругу\nЖивить батарею/систему\nПлавне зростання напруги", size=10, fill="#fdecea", stroke=POS))
    parts.append(fitbox(600, 182, 190, 72, "PD Контролер (CC1)\nRd термінація 5.1 кОм\nВідповіді на SOP пакети", size=10, fill="#eaf3ea", stroke=FIELD))
    parts.append(fitbox(600, 268, 190, 78, "Опційний стік VCONN\nМоже живити SOP''\nабо резервне живлення Plug B", size=10, fill="#fef7e6", stroke="#d97706"))
    parts.append(fitbox(600, 360, 190, 70, "Швидкісний PHY Стіка\nTX1/2 та RX1/2\nПриймає відновлений сигнал", size=10, fill="#eff6ff", stroke=NEG))

    # Середня частина - Активний кабель
    parts.append(rect(250, 52, 320, 390, fill="#ffffff", stroke="#64748b", sw=1.8, rx=8))
    parts.append(text(410, 76, "Активний кабель (Plug A + Дріт + Plug B)", size=11.5, bold=True, color=INK))

    # Лінія 1: VBUS - Транзитна
    parts.append(line(220, 132, 600, 132, color=POS, sw=3))
    parts.append(arrow(580, 132, 595, 132, color=POS))
    parts.append(textbox(410, 114, "VBUS (5–48 В): ТРАНЗИТ навантаження пристрою\n(Кабельні чипи НЕ живляться від VBUS!)", size=9.5, fill="#fdecea", stroke=POS, bold=True, color=POS)[0])

    # Лінія 2: CC - Лінія зв'язку
    parts.append(line(220, 218, 600, 218, color=FIELD, sw=2))
    parts.append(arrow(580, 218, 595, 218, color=FIELD))
    parts.append(arrow(240, 218, 225, 218, color=FIELD))
    parts.append(textbox(410, 202, "CC1: PD Пакети SOP (Хост <-> Пристрій)\nта SOP' / SOP'' (Хост <-> Кабельні чипи)", size=9.5, fill="#eaf3ea", stroke=FIELD, bold=True, color=FIELD)[0])

    # Лінія 3: VCONN - Живлення внутрішніх чипів
    parts.append(line(220, 307, 340, 307, color="#d97706", sw=2.5))
    parts.append(arrow(320, 307, 335, 307, color="#d97706"))
    parts.append(line(340, 307, 480, 307, color="#d97706", sw=1.8, dash="3 3"))
    parts.append(line(480, 307, 600, 307, color="#d97706", sw=2.5))

    # Блоки живлення чипів Plug A та Plug B
    parts.append(rect(265, 280, 120, 54, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=4))
    parts.append(text(325, 298, "Plug A Чипи", size=10, bold=True, color="#d97706"))
    parts.append(text(325, 314, "VCONN: 1.0–1.5 Вт", size=9.5, color=INK))

    parts.append(rect(435, 280, 120, 54, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=4))
    parts.append(text(495, 298, "Plug B Чипи", size=10, bold=True, color="#d97706"))
    parts.append(text(495, 314, "VCONN транзит", size=9.5, color=INK))

    # Лінія 4: Швидкісні лінії через Ретаймери
    parts.append(line(220, 395, 265, 395, color=NEG, sw=2))
    parts.append(rect(265, 375, 120, 42, fill="#eff6ff", stroke=NEG, sw=1.4, rx=4))
    parts.append(text(325, 392, "Ретаймер / Оптика А", size=9.5, bold=True, color=NEG))
    parts.append(text(325, 407, "Tx Boost / CDR", size=9.5, color=MUTED))

    parts.append(line(385, 395, 435, 395, color=NEG, sw=2, dash="4 2"))
    parts.append(text(410, 385, "Канал", size=9.5, color=NEG, italic=True))

    parts.append(rect(435, 375, 120, 42, fill="#eff6ff", stroke=NEG, sw=1.4, rx=4))
    parts.append(text(495, 392, "Ретаймер / Оптика В", size=9.5, bold=True, color=NEG))
    parts.append(text(495, 407, "Rx Equalizer / CDR", size=9.5, color=MUTED))
    parts.append(line(555, 395, 600, 395, color=NEG, sw=2))
    parts.append(arrow(585, 395, 595, 395, color=NEG))

    render(os.path.join(IMG, "vconn-power-routing.svg"), W, H, *parts,
           title="Розподіл живлення та ізоляція VCONN від VBUS")


# ── 4. Послідовність опитування E-Marker (SOP' / SOP'') ───────────────────────
def fig_sop_handshake():
    W, H = 800, 440
    parts = []

    parts.append(text(W / 2, 26, "Протокол узгодження активного кабелю: послідовність SOP' / SOP''", size=14, bold=True))

    # Колонки: Хост (DFP), Кабель Plug A (SOP'), Кабель Plug B (SOP''), Пристрій (SOP / UFP)
    hx = 100
    pax = 300
    pbx = 500
    dx = 700

    parts.append(rect(hx - 65, 48, 130, 30, fill="#f8fafc", stroke=LINE, sw=1.5, rx=4))
    parts.append(text(hx, 68, "Хост (DFP)", size=12, bold=True))

    parts.append(rect(pax - 75, 48, 150, 30, fill="#eaf3ea", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(pax, 68, "Plug A (SOP')", size=12, bold=True, color=FIELD))

    parts.append(rect(pbx - 75, 48, 150, 30, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=4))
    parts.append(text(pbx, 68, "Plug B (SOP'')", size=12, bold=True, color="#d97706"))

    parts.append(rect(dx - 65, 48, 130, 30, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    parts.append(text(dx, 68, "Пристрій (SOP)", size=12, bold=True, color=NEG))

    # Вертикальні лінії життя
    for x in [hx, pax, pbx, dx]:
        parts.append(line(x, 78, x, 410, color=MUTED, sw=1.2, dash="3 3"))

    def msg_arrow(y, x1, x2, label, sub, color):
        parts.append(line(x1, y, x2, y, color=color, sw=2))
        if x2 > x1:
            parts.append(arrow(x2 - 16, y, x2, y, color=color))
        else:
            parts.append(arrow(x2 + 16, y, x2, y, color=color))
        parts.append(text((x1 + x2) / 2, y - 8, label, size=10.5, bold=True, color=color))
        if sub:
            parts.append(text((x1 + x2) / 2, y + 12, sub, size=9.5, color=MUTED, italic=True))

    # Крок 1: Ввімкнення VCONN
    parts.append(textbox(hx, 102, "1. Подача VCONN (5 В)", size=9.5, fill="#fef7e6", stroke="#d97706", bold=True, color="#d97706")[0])

    # Крок 2: Запит до Plug A (SOP')
    msg_arrow(138, hx, pax, "SOP': Discover Identity", "Structured VDM запит", FIELD)
    msg_arrow(176, pax, hx, "SOP': Responder VDOs", "Active Cable VDO 2: 40 Gbps, Retimer, 1.5W", FIELD)

    # Крок 3: Запит до Plug B (SOP'')
    msg_arrow(220, hx, pbx, "SOP'': Discover Identity", "Перевірка другого штекера", "#d97706")
    msg_arrow(258, pbx, hx, "SOP'': Responder VDOs", "Active Cable VDO: статус приймача B", "#d97706")

    # Крок 4: Запит до пристрою (SOP)
    msg_arrow(302, hx, dx, "SOP: Source_Capabilities", "Звичайне меню PD для пристрою", NEG)
    msg_arrow(340, dx, hx, "SOP: Request (20 В / 5 А)", "Пристрій знає про кабель на 5 А", NEG)

    # Крок 5: Початок швидкісного Link Training
    b, w, h = textbox(W / 2, 386, "Хост знає параметри кабелю: вмикає живлення ретаймерів через VCONN,\nналаштовує пресети еквалайзера Tx/Rx та запускає USB4 Link Training", size=10, fill="#f8fafc", stroke=LINE, bold=True)
    parts.append(b)

    render(os.path.join(IMG, "sop-prime-handshake.svg"), W, H, *parts,
           title="Послідовність опитування E-Marker SOP' та SOP''")


if __name__ == "__main__":
    fig_attenuation_eye()
    fig_active_cable_anatomy()
    fig_vconn_power_routing()
    fig_sop_handshake()
    print("Всі 4 фігури згенеровано успішно.")
