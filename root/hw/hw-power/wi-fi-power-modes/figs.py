# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Режими енергоощадності Wi-Fi».
Використовує svgkit зі scripts/ (імпорт, без копіювання).
Генерує SVG-файли в теці img/.
"""
import sys, os
TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(TOPIC_DIR)
sys.path.insert(0, os.path.join(TOPIC_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

# ── 1. Ієрархія апаратних станів сну Wi-Fi SoC ──────────────────────────────
def fig_wifi_sleep_states():
    W, H = 840, 490
    parts = []

    # Заголовок / шапка таблиці-схеми
    parts.append(text(W / 2, 28, "Апаратні стани енергоспоживання типового Wi-Fi SoC", size=15, bold=True))

    col_w = 188
    gap = 12
    start_x = 24
    y_top = 52
    card_h = 375

    states = [
        {
            "name": "Active (TX / RX)",
            "sub": "Повна активність",
            "curr": "80 – 280 мА",
            "bg": "#fdecea",
            "border": POS,
            "badge_col": POS,
            "domains": [
                ("RF PA / LNA / Синтез", True),
                ("Baseband DSP (OFDM)", True),
                ("CPU ядра (80–240 МГц)", True),
                ("SRAM пам'ять (активна)", True),
                ("RTC / Slow domain", True),
            ],
            "wake": "0 мкс (активний)",
            "desc": "Передача радіоімпульсу або прийом кадрів з ефіру."
        },
        {
            "name": "Modem-Sleep",
            "sub": "Вимкнене радіо",
            "curr": "15 – 30 мА",
            "bg": "#fef9e7",
            "border": "#f39c12",
            "badge_col": "#d35400",
            "domains": [
                ("RF PA / LNA / Синтез", False),
                ("Baseband DSP (OFDM)", False),
                ("CPU ядра (80–240 МГц)", True),
                ("SRAM пам'ять (активна)", True),
                ("RTC / Slow domain", True),
            ],
            "wake": "~1 – 3 мс (PLL lock)",
            "desc": "Обчислення CPU під час паузи між сеансами зв'язку."
        },
        {
            "name": "Light-Sleep",
            "sub": "Тактове блокування",
            "curr": "0.8 – 2.5 мА",
            "bg": "#eafaf1",
            "border": FIELD,
            "badge_col": FIELD,
            "domains": [
                ("RF PA / LNA / Синтез", False),
                ("Baseband DSP (OFDM)", False),
                ("CPU ядра (тактування off)", False),
                ("SRAM ретенція (живлення)", True),
                ("RTC / Slow domain", True),
            ],
            "wake": "~0.5 – 1.5 мс",
            "desc": "Збереження повного стану RTOS і ключів Wi-Fi асоціації."
        },
        {
            "name": "Deep-Sleep",
            "sub": "Глибокий сон (RTC)",
            "curr": "5 – 20 мкА",
            "bg": "#ebf5fb",
            "border": NEG,
            "badge_col": NEG,
            "domains": [
                ("RF PA / LNA / Синтез", False),
                ("Baseband DSP (OFDM)", False),
                ("CPU ядра (power-gated)", False),
                ("SRAM основна (off)", False),
                ("RTC domain (32 кГц)", True),
            ],
            "wake": "~15 – 35 мс (Boot)",
            "desc": "Вимкнено все, крім RTC-таймера та RTC-пам'яті стану."
        },
    ]

    for i, st in enumerate(states):
        cx = start_x + i * (col_w + gap) + col_w / 2
        card_x = start_x + i * (col_w + gap)

        # Фонова картка
        parts.append(rect(card_x, y_top, col_w, card_h, fill=st["bg"], stroke=st["border"], sw=2.0, rx=8))

        # Назва стану
        parts.append(text(cx, y_top + 24, st["name"], size=13, bold=True, color=st["badge_col"]))
        parts.append(text(cx, y_top + 40, st["sub"], size=11, color=MUTED))

        # Струм (великий бейдж)
        b, _, _ = textbox(cx, y_top + 70, st["curr"], size=13, bold=True, fill="#ffffff", stroke=st["badge_col"], color=st["badge_col"], min_w=140)
        parts.append(b)

        # Розділювач
        parts.append(line(card_x + 10, y_top + 98, card_x + col_w - 10, y_top + 98, color=st["border"], sw=1.0, dash="3,3"))

        # Живлення доменів
        parts.append(text(card_x + 12, y_top + 116, "Живлення підсистем:", size=10, bold=True, color=INK, anchor="start"))
        for d_idx, (dom_name, is_on) in enumerate(st["domains"]):
            dy = y_top + 136 + d_idx * 27
            dot_col = FIELD if is_on else MUTED
            dot_txt = "ON" if is_on else "OFF"
            # Маленький індикатор
            parts.append(rect(card_x + 10, dy - 10, 30, 18, fill="#ffffff" if is_on else "#e5e7eb", stroke=dot_col, sw=1.2, rx=3))
            parts.append(text(card_x + 25, dy + 3, dot_txt, size=9, bold=True, color=dot_col))
            # Назва підсистеми
            parts.append(text(card_x + 46, dy + 3, dom_name, size=9, color=INK if is_on else MUTED, anchor="start"))

        # Час пробудження
        parts.append(line(card_x + 10, y_top + 280, card_x + col_w - 10, y_top + 280, color=st["border"], sw=1.0, dash="3,3"))
        parts.append(text(card_x + 12, y_top + 298, "Час пробудження:", size=10, bold=True, color=INK, anchor="start"))
        parts.append(text(card_x + 12, y_top + 314, st["wake"], size=10, color=st["badge_col"], bold=True, anchor="start"))

        # Опис призначення
        parts.append(text(card_x + 12, y_top + 338, "Призначення:", size=10, bold=True, color=INK, anchor="start"))
        desc_lines = [st["desc"][:27], st["desc"][27:]] if len(st["desc"]) > 27 else [st["desc"]]
        for dl_idx, dline in enumerate(desc_lines):
            parts.append(text(card_x + 12, y_top + 352 + dl_idx * 14, dline.strip(), size=9, color=MUTED, anchor="start"))

    # Нижній висновок
    box, _, _ = textbox(W / 2, 458, "Глибина сну вимагає компромісу між мікроамперами споживання та енергією виходу зі стану", size=11, fill="#f4f6f8", stroke=LINE)
    parts.append(box)

    render("img/wifi-sleep-states.svg", W, H, *parts, title="Апаратні стани сну Wi-Fi SoC")


# ── 2. Протокольні механізми (Legacy PS-Poll vs U-APSD vs Wi-Fi 6 TWT) ───────
def fig_protocol_ps_mechanisms():
    W, H = 840, 520
    parts = []

    parts.append(text(W / 2, 26, "Еволюція протоколів енергоощадності IEEE 802.11", size=15, bold=True))

    schemes = [
        {
            "title": "1. Legacy PS-Poll (IEEE 802.11-1997 / 802.11b/g)",
            "y": 50,
            "h": 128,
            "badge": "Покадрове опитування (високі накладні витрати)",
            "badge_col": POS,
            "draw": "pspoll"
        },
        {
            "title": "2. WMM U-APSD (IEEE 802.11e / Wi-Fi 4/5)",
            "y": 196,
            "h": 128,
            "badge": "Пакетне вивантаження за тригером (QoS потоки)",
            "badge_col": "#e67e22",
            "draw": "uapsd"
        },
        {
            "title": "3. Target Wake Time — TWT (IEEE 802.11ax / Wi-Fi 6)",
            "y": 342,
            "h": 136,
            "badge": "Детермінований розклад без прослуховування маяків",
            "badge_col": FIELD,
            "draw": "twt"
        }
    ]

    for sc in schemes:
        y0 = sc["y"]
        h0 = sc["h"]
        parts.append(rect(20, y0, W - 40, h0, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
        parts.append(text(34, y0 + 20, sc["title"], size=12, bold=True, color=INK, anchor="start"))
        b, _, _ = textbox(W - 220, y0 + 18, sc["badge"], size=10, fill="#f8f9fa", stroke=sc["badge_col"], color=sc["badge_col"], bold=True)
        parts.append(b)

        axis_y = y0 + 80
        parts.append(line(40, axis_y, W - 50, axis_y, color=LINE, sw=1.2))
        parts[-1] = parts[-1].replace("/>", ' marker-end="url(#arrow)"/>')
        parts.append(text(W - 40, axis_y + 4, "t", size=11, bold=True, color=LINE, anchor="start"))

        if sc["draw"] == "pspoll":
            parts.append(rect(45, axis_y - 8, 75, 16, fill="#dbeafe", stroke=NEG, sw=1.0, rx=2))
            parts.append(text(82, axis_y + 4, "Сон (Doze)", size=9, color=NEG))

            parts.append(rect(125, axis_y - 24, 48, 48, fill="#fde68a", stroke="#d97706", sw=1.5, rx=3))
            parts.append(text(149, axis_y - 4, "Beacon", size=9, bold=True, color="#92400e"))
            parts.append(text(149, axis_y + 10, "TIM=1", size=9, color="#92400e"))

            parts.append(rect(178, axis_y - 14, 44, 28, fill="#fee2e2", stroke=POS, sw=1.0, rx=2))
            parts.append(text(200, axis_y + 4, "Backoff", size=9, color=POS))

            parts.append(rect(227, axis_y - 26, 52, 52, fill="#fecaca", stroke=POS, sw=1.5, rx=3))
            parts.append(text(253, axis_y - 4, "PS-Poll", size=9, bold=True, color=POS))
            parts.append(text(253, axis_y + 10, "(TX)", size=9, color=POS))

            parts.append(rect(284, axis_y - 16, 34, 32, fill="#e5e7eb", stroke=MUTED, sw=1.0, rx=2))
            parts.append(text(301, axis_y + 4, "ACK", size=9, color=INK))

            parts.append(rect(323, axis_y - 28, 68, 56, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
            parts.append(text(357, axis_y - 6, "Data 1", size=9, bold=True, color=FIELD))
            parts.append(text(357, axis_y + 8, "More=1", size=9, color=FIELD))

            parts.append(rect(396, axis_y - 16, 34, 32, fill="#fee2e2", stroke=POS, sw=1.0, rx=2))
            parts.append(text(413, axis_y + 4, "ACK", size=9, color=POS))

            parts.append(rect(435, axis_y - 14, 44, 28, fill="#fee2e2", stroke=POS, sw=1.0, rx=2))
            parts.append(text(457, axis_y + 4, "Backoff", size=9, color=POS))

            parts.append(rect(484, axis_y - 26, 52, 52, fill="#fecaca", stroke=POS, sw=1.5, rx=3))
            parts.append(text(510, axis_y - 4, "PS-Poll", size=9, bold=True, color=POS))
            parts.append(text(510, axis_y + 10, "(TX)", size=9, color=POS))

            parts.append(rect(541, axis_y - 28, 68, 56, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
            parts.append(text(575, axis_y - 6, "Data 2", size=9, bold=True, color=FIELD))
            parts.append(text(575, axis_y + 8, "More=0", size=9, color=FIELD))

            parts.append(rect(614, axis_y - 16, 34, 32, fill="#fee2e2", stroke=POS, sw=1.0, rx=2))
            parts.append(text(631, axis_y + 4, "ACK", size=9, color=POS))

            parts.append(rect(653, axis_y - 8, 110, 16, fill="#dbeafe", stroke=NEG, sw=1.0, rx=2))
            parts.append(text(708, axis_y + 4, "Сон до DTIM", size=9, color=NEG))

        elif sc["draw"] == "uapsd":
            parts.append(rect(45, axis_y - 8, 110, 16, fill="#dbeafe", stroke=NEG, sw=1.0, rx=2))
            parts.append(text(100, axis_y + 4, "Сон за графіком", size=9, color=NEG))

            parts.append(rect(160, axis_y - 28, 78, 56, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=3))
            parts.append(text(199, axis_y - 6, "Trigger Frame", size=9, bold=True, color="#c2410c"))
            parts.append(text(199, axis_y + 8, "QoS Data / Null", size=9, color="#c2410c"))

            parts.append(line(242, axis_y - 15, 242, axis_y + 15, color=MUTED, sw=1.0, dash="2,2"))

            parts.append(rect(248, axis_y - 28, 72, 56, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
            parts.append(text(284, axis_y - 6, "Data Frame 1", size=9, bold=True, color=FIELD))
            parts.append(text(284, axis_y + 8, "EOSP = 0", size=9, color=FIELD))

            parts.append(rect(325, axis_y - 28, 72, 56, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
            parts.append(text(361, axis_y - 6, "Data Frame 2", size=9, bold=True, color=FIELD))
            parts.append(text(361, axis_y + 8, "EOSP = 1 (Кінець)", size=9, color=FIELD))

            parts.append(rect(402, axis_y - 18, 58, 36, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
            parts.append(text(431, axis_y + 4, "Block ACK", size=9, bold=True, color=POS))

            parts.append(rect(465, axis_y - 8, 280, 16, fill="#dbeafe", stroke=NEG, sw=1.0, rx=2))
            parts.append(text(605, axis_y + 4, "Миттєвий перехід у сон (без очікування та опитування)", size=9, color=NEG))

        elif sc["draw"] == "twt":
            parts.append(rect(45, axis_y - 8, 205, 16, fill="#dbeafe", stroke=NEG, sw=1.5, rx=2))
            parts.append(text(147, axis_y + 4, "Глибокий сон (години / доби, маяки off)", size=9, bold=True, color=NEG))

            parts.append(line(255, y0 + 35, 255, axis_y + 40, color=POS, sw=1.8, dash="4,3"))
            parts.append(text(255, y0 + 46, "TWT Start", size=9, bold=True, color=POS))

            parts.append(rect(260, axis_y - 30, 95, 60, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
            parts.append(text(307, axis_y - 8, "TWT SP (OFDMA)", size=9, bold=True, color="#92400e"))
            parts.append(text(307, axis_y + 8, "Паралельний RX/TX", size=9, color="#92400e"))

            parts.append(line(360, y0 + 35, 360, axis_y + 40, color=POS, sw=1.8, dash="4,3"))
            parts.append(text(360, y0 + 46, "TWT End", size=9, bold=True, color=POS))

            parts.append(rect(370, axis_y - 8, 380, 16, fill="#dbeafe", stroke=NEG, sw=1.5, rx=2))
            parts.append(text(560, axis_y + 4, "Глибокий сон до наступного TWT SP (нульові колізії)", size=9, bold=True, color=NEG))

    box, _, _ = textbox(W / 2, 498, "Wi-Fi 6 TWT перетворює Wi-Fi з випадкового доступу CSMA/CA на детермінований розклад", size=11, fill="#eafaf1", stroke=FIELD)
    parts.append(box)

    render("img/protocol-ps-mechanisms.svg", W, H, *parts, title="Протокольні механізми енергоощадності Wi-Fi")


# ── 3. Холодний старт проти Fast Reconnect (Час і заряд) ────────────────────
def fig_fast_reconnect_vs_cold_boot():
    W, H = 840, 440
    parts = []

    parts.append(text(W / 2, 26, "Ціна пробудження: Повне підключення проти Fast Reconnect", size=15, bold=True))

    y1 = 52
    h1 = 160
    parts.append(rect(20, y1, W - 40, h1, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    parts.append(text(35, y1 + 22, "1. Повне повторне підключення (Cold Boot):  t_актив ≈ 1800 – 3500 мс,  Q ≈ 220 мКл", size=12, bold=True, color=POS, anchor="start"))

    # Фази холодного старту (загальна ширина = 750px)
    phases_cold = [
        ("Boot / RF Cal", 100, "#fed7aa", "#c2410c", "30–80 мс"),
        ("13-Ch Scan", 150, "#fecaca", "#dc2626", "150–400 мс"),
        ("Auth/Assoc", 85, "#fde68a", "#d97706", "30–60 мс"),
        ("WPA 4-Way", 120, "#e9d5ff", "#9333ea", "50–120 мс"),
        ("DHCP + ARP", 220, "#fbcfe8", "#db2777", "1000–2500 мс"),
        ("Data", 65, "#bbf7d0", FIELD, "15–30 мс")
    ]

    cur_x = 35
    bar_y = y1 + 55
    bar_h = 50
    for name, w_box, bg_c, str_c, duration in phases_cold:
        parts.append(rect(cur_x, bar_y, w_box, bar_h, fill=bg_c, stroke=str_c, sw=1.2, rx=4))
        parts.append(text(cur_x + w_box / 2, bar_y + 20, name, size=10, bold=True, color=str_c))
        parts.append(text(cur_x + w_box / 2, bar_y + 38, duration, size=9, color=INK))
        cur_x += w_box + 4

    b_cold, _, _ = textbox(W / 2, y1 + 135, "До 90% всієї енергії сеансу спалюється на очікування відповідей DHCP та сканування ефіру", size=10, fill="#ffffff", stroke=POS, color=POS)
    parts.append(b_cold)

    y2 = 226
    h2 = 160
    parts.append(rect(20, y2, W - 40, h2, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(35, y2 + 22, "2. Fast Reconnect (Кеш BSSID/каналу + PMKSA + статична IP / кеш лізингу):  t_актив ≈ 45 – 85 мс,  Q ≈ 6.5 мКл", size=12, bold=True, color=FIELD, anchor="start"))

    phases_fast = [
        ("RTC Wake & Init", 170, "#dbeafe", NEG, "3–8 мс"),
        ("Direct Ch Assoc (PMKSA)", 280, "#e0e7ff", "#4338ca", "25–45 мс (без сканування!)"),
        ("Cached IP / Data Send", 280, "#bbf7d0", FIELD, "15–30 мс (без DHCP!)"),
    ]

    cur_x2 = 35
    bar_y2 = y2 + 55
    for name, w_box, bg_c, str_c, duration in phases_fast:
        parts.append(rect(cur_x2, bar_y2, w_box, bar_h, fill=bg_c, stroke=str_c, sw=1.2, rx=4))
        parts.append(text(cur_x2 + w_box / 2, bar_y2 + 20, name, size=10, bold=True, color=str_c))
        parts.append(text(cur_x2 + w_box / 2, bar_y2 + 38, duration, size=9, color=INK))
        cur_x2 += w_box + 12

    b_fast, _, _ = textbox(W / 2, y2 + 135, "Енерговитрати скорочуються у 30–35 разів завдяки усуненню сканування каналів і протоколу DHCP", size=10, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b_fast)

    box, _, _ = textbox(W / 2, 412, "Для батарейних вузлів обов'язкове кешування каналу, BSSID, PMKSA та статична конфігурація IP", size=11, fill="#f4f6f8", stroke=LINE)
    parts.append(box)

    render("img/fast-reconnect-vs-cold-boot.svg", W, H, *parts, title="Cold Boot проти Fast Reconnect")


# ── 4. DTIM інтервали та поправка на дрейф RTC ──────────────────────────────
def fig_dtim_listen_interval():
    W, H = 820, 460
    parts = []

    parts.append(text(W / 2, 26, "Вплив періоду DTIM та дрейфу RTC на профіль споживання", size=15, bold=True))

    rows = [
        {
            "name": "DTIM = 1 (Період ~102.4 мс)",
            "y": 55,
            "desc": "Прокидання на кожен маяк. Мінімальна затримка, максимальний струм прослуховування (~3.5–5 мА).",
            "beacons": [0, 1, 2, 3, 4, 5],
            "guard": 6,
            "col": POS
        },
        {
            "name": "DTIM = 3 (Період ~307.2 мс)",
            "y": 175,
            "desc": "Прокидання на кожен 3-й маяк. Оптимальний баланс для побутових датчиків (~1.2–1.8 мА).",
            "beacons": [0, 3],
            "guard": 10,
            "col": "#d97706"
        },
        {
            "name": "DTIM = 10 (Період ~1024 мс)",
            "y": 295,
            "desc": "Прокидання раз на секунду. Низький струм (~0.3–0.6 мА), але вимагає більшого захисного інтервалу t_guard.",
            "beacons": [0],
            "guard": 18,
            "col": FIELD
        }
    ]

    for r_data in rows:
        y0 = r_data["y"]
        parts.append(rect(20, y0, W - 40, 105, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
        parts.append(text(35, y0 + 18, r_data["name"], size=12, bold=True, color=r_data["col"], anchor="start"))
        parts.append(text(35, y0 + 34, r_data["desc"], size=9, color=MUTED, anchor="start"))

        axis_y = y0 + 72
        parts.append(line(40, axis_y, W - 50, axis_y, color=LINE, sw=1.0))
        parts[-1] = parts[-1].replace("/>", ' marker-end="url(#arrow)"/>')

        step_x = 110
        base_x = 70
        for b_idx in range(6):
            bx = base_x + b_idx * step_x
            is_dtim = b_idx in r_data["beacons"]

            parts.append(line(bx, axis_y - 25, bx, axis_y + 15, color="#f59e0b", sw=1.2, dash="2,2"))
            parts.append(text(bx, axis_y - 28, "B%d" % b_idx, size=9, color="#b45309"))

            if is_dtim:
                gw = r_data["guard"]
                parts.append(rect(bx - gw, axis_y - 18, gw, 18, fill="#fed7aa", stroke="#ea580c", sw=1.0, rx=2))
                parts.append(rect(bx, axis_y - 18, 24, 18, fill="#fecaca", stroke=POS, sw=1.0, rx=2))
                parts.append(text(bx - gw / 2, axis_y - 6, "tg", size=9, color="#c2410c"))
                parts.append(text(bx + 12, axis_y - 6, "RX", size=9, bold=True, color=POS))
            else:
                parts.append(rect(bx - 30, axis_y - 6, 60, 10, fill="#dbeafe", stroke=NEG, sw=0.5, rx=2))

    box, _, _ = textbox(W / 2, 428, "Формула захисного інтервалу:  t_guard = 2 · Δf_ppm · T_dtim + t_settle  (компенсує дрейф кварцу 32.768 кГц)", size=10, fill="#f4f6f8", stroke=LINE, color=INK, bold=True)
    parts.append(box)

    render("img/dtim-listen-interval.svg", W, H, *parts, title="DTIM інтервали та захисний час")


if __name__ == "__main__":
    fig_wifi_sleep_states()
    fig_protocol_ps_mechanisms()
    fig_fast_reconnect_vs_cold_boot()
    fig_dtim_listen_interval()
    print("OK: generated 4 svg figures in img/")
