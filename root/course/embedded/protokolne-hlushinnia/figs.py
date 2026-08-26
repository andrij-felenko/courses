# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. energy-comparison: Силове глушіння проти Протокольного ─────────────────
def fig_energy_comparison():
    W, H = 940, 450
    p = []

    # ── Ліва колонка: Силовий РЕБ (Barrage Jamming) ──
    lx, ly, lw, lh = 50, 75, 395, 325
    p.append(rect(lx, ly, lw, lh, fill="#fdf3f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(lx + lw / 2, ly + 28, "Силове глушіння (Physical / Barrage)", size=13.5, color=POS, bold=True))
    p.append(text(lx + lw / 2, ly + 48, "Ціль: фізичний рівень (PHY)", size=11, color=MUTED))

    # Візуалізація спектра і шуму
    p.append(rect(lx + 20, ly + 68, lw - 40, 105, fill="#ffffff", stroke="#d98880", sw=1, rx=4))
    # Рівень шуму (високий блок)
    p.append(rect(lx + 30, ly + 95, lw - 60, 70, fill="#f9d5d2", stroke="none"))
    p.append(line(lx + 30, ly + 95, lx + lw - 30, ly + 95, color=POS, sw=1.8, dash="4,4"))
    p.append(text(lx + lw / 2, ly + 118, "Шум РЕБ (P_jam >> P_sig)", size=11.5, color=POS, bold=True))
    # Малий корисний сигнал, втоплений у шумі
    p.append(rect(lx + 155, ly + 128, 85, 36, fill="#d4e6f1", stroke=NEG, sw=1.2))
    p.append(text(lx + 197, ly + 150, "Корисний сигнал", size=9.5, color=NEG, bold=True))

    # Характеристики силового
    items_left = [
        "• Потужність передавача: 10 Вт – 1000 Вт",
        "• Робочий цикл (Duty Cycle): 100% (безперервно)",
        "• Смуга: десятки / сотні МГц (розпорошення)",
        "• Помітність: миттєво пеленгується в ефірі",
        "• Енергія на 1 хв глушіння: ~6 000 – 60 000 Дж",
    ]
    yy = ly + 198
    for it in items_left:
        p.append(text(lx + 25, yy, it, size=10.5, color=INK, anchor="start"))
        yy += 21

    # ── Права колонка: Протокольне глушіння (Protocol Jamming) ──
    rx, ry, rw, rh = 495, 75, 395, 325
    p.append(rect(rx, ry, rw, rh, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(rx + rw / 2, ry + 28, "Протокольне глушіння (Smart / Protocol)", size=13.5, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 48, "Ціль: кінцевий автомат протоколу (MAC)", size=11, color=MUTED))

    # Візуалізація коротких імпульсів
    p.append(rect(rx + 20, ry + 68, rw - 40, 105, fill="#ffffff", stroke="#a9dfbf", sw=1, rx=4))
    # Чистий шум каналу
    p.append(line(rx + 30, ry + 160, rx + rw - 30, ry + 160, color="#7dcea0", sw=1.5))
    p.append(text(rx + 35, ry + 152, "Шум ефіру (-95 дБм)", size=9, color=MUTED, anchor="start"))
    # Короткі імпульси Deauth / NAV (рознесені ліворуч)
    p.append(rect(rx + 45, ry + 82, 35, 78, fill="#f5b7b1", stroke=POS, sw=1.2))
    p.append(text(rx + 62, ry + 76, "Deauth", size=9, color=POS, bold=True))
    p.append(rect(rx + 115, ry + 92, 35, 68, fill="#f5b7b1", stroke=POS, sw=1.2))
    p.append(text(rx + 132, ry + 76, "NAV", size=9, color=POS, bold=True))
    # Текст праворуч від імпульсів
    p.append(text(rx + 270, ry + 115, "Канал блоковано логікою", size=11, color=FIELD, bold=True))
    p.append(text(rx + 270, ry + 132, "(вузли чекають самі)", size=10, color=MUTED))

    # Характеристики протокольного
    items_right = [
        "• Потужність передавача: 1 мВт – 20 мВт (чіп MCU)",
        "• Робочий цикл (Duty Cycle): < 0.1% (мікросекунди)",
        "• Смуга: 1 вузький канал протоколу",
        "• Помітність: маскується під штатний трафік",
        "• Енергія на 1 хв глушіння: ~0.005 – 0.05 Дж",
    ]
    yy = ry + 198
    for it in items_right:
        p.append(text(rx + 25, yy, it, size=10.5, color=INK, anchor="start"))
        yy += 21

    # Центральний маркер асиметрії
    p.append(textbox(W / 2, H - 20, "Енергетичний виграш атаки: у 1 000 – 100 000 разів менше споживання", size=11.5, pad=8, fill="#ffffff", stroke=LINE, bold=True)[0])

    render(os.path.join(OUT, "energy-comparison.svg"), W, H, *p,
           title="Силове глушіння (брутфорс спектра) проти Протокольного глушіння (атака логіки)")


# ── 2. deauth-mechanism: Атака деавтентифікації та захист 802.11w PMF ─────────
def fig_deauth_mechanism():
    W, H = 940, 460
    p = []

    # Три колони: Клієнт (STA), Атакуючий (Jammer), Точка доступу (AP)
    x_sta, x_jam, x_ap = 200, 470, 740
    y_top = 65

    # Заголовки учасників
    p.append(textbox(x_sta, y_top, "Клієнт (STA)\nMAC: 00:AA:22", size=11.5, pad=6, fill="#e8f4f8", stroke=NEG, bold=True)[0])
    p.append(textbox(x_jam, y_top, "Атакуючий (Jammer)\nSpoofed Source MAC", size=11.5, pad=6, fill="#fdecea", stroke=POS, bold=True)[0])
    p.append(textbox(x_ap, y_top, "Точка доступу (AP)\nMAC: 00:BB:99", size=11.5, pad=6, fill="#eafaf1", stroke=FIELD, bold=True)[0])

    # Секція 1: Відкритий 802.11 (WPA2 без PMF)
    p.append(rect(40, 115, W - 80, 145, fill="#fefdf9", stroke="#f39c12", sw=1.2, rx=6))
    p.append(text(60, 134, "1. Звичайна мережа 802.11 (WPA2 без 802.11w PMF) — незахищені службові кадри", size=11, color="#b7950b", bold=True, anchor="start"))

    # Лінії життя всередині секції 1
    p.append(line(x_sta, 145, x_sta, 170, color="#bdc3c7", sw=1.5, dash="4,4"))
    p.append(line(x_jam, 145, x_jam, 235, color="#bdc3c7", sw=1.5, dash="4,4"))
    p.append(line(x_ap, 145, x_ap, 235, color="#bdc3c7", sw=1.5, dash="4,4"))

    # Постріл деавтентифікації
    p.append(arrow(x_jam - 20, 170, x_sta + 20, 170, color=POS, sw=2))
    p.append(text((x_jam + x_sta) / 2, 162, "Deauth Frame (Src: AP, Dst: STA, Reason: 7)", size=10, color=POS, bold=True))

    # Скидання стану STA
    p.append(textbox(x_sta, 205, "Миттєвий розрив зв'язку!\nСкидання ключів PTK / стан UNASSOCIATED", size=9.5, pad=5, fill="#fadbd8", stroke=POS)[0])

    # Секція 2: Захищений 802.11w PMF (Protected Management Frames)
    p.append(rect(40, 275, W - 80, 165, fill="#f9fdfa", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(60, 294, "2. Захищена мережа (802.11w PMF / WPA3) — криптографічний захист цілісності кадрів", size=11, color=FIELD, bold=True, anchor="start"))

    # Лінії життя всередині секції 2
    p.append(line(x_sta, 305, x_sta, 325, color="#bdc3c7", sw=1.5, dash="4,4"))
    p.append(line(x_jam, 305, x_jam, 415, color="#bdc3c7", sw=1.5, dash="4,4"))
    p.append(line(x_ap, 305, x_ap, 385, color="#bdc3c7", sw=1.5, dash="4,4"))

    # Підроблений кадр від атакуючого
    p.append(arrow(x_jam - 20, 325, x_sta + 20, 325, color=POS, sw=1.5))
    p.append(text((x_jam + x_sta) / 2, 317, "Spoofed Deauth (без валідного AES-CMAC / BIP)", size=10, color=POS))

    # Перевірка і відкидання
    p.append(textbox(x_sta, 360, "Перевірка AES-CMAC (BIP / IGTK) -> ПОМИЛКА!\nКадр підроблено -> Ігнорування -> Зв'язок збережено", size=9.5, pad=5, fill="#d4efdf", stroke=FIELD, bold=True)[0])

    # SA Query до AP
    p.append(line(x_sta, 385, x_sta, 405, color="#bdc3c7", sw=1.5, dash="4,4"))
    p.append(arrow(x_sta + 20, 405, x_ap - 20, 405, color=NEG, sw=1.5))
    p.append(text((x_sta + x_ap) / 2, 397, "SA Query Request / Response (захищена перевірка стану лінка)", size=9.5, color=NEG))

    render(os.path.join(OUT, "deauth-mechanism.svg"), W, H, *p,
           title="Атака деавтентифікації 802.11 та захист через Protected Management Frames (PMF)")


# ── 3. cca-nav-jamming: Фізичний CCA та Віртуальний NAV ─────────────────────────
def fig_cca_nav_jamming():
    W, H = 940, 450
    p = []

    # ── Ліва частина: Physical CCA Jamming ──
    lx, ly, lw, lh = 45, 75, 410, 345
    p.append(rect(lx, ly, lw, lh, fill="#f8f9f9", stroke=LINE, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 26, "Фізичний рівень: CCA Energy Detect Jamming", size=12.5, color=INK, bold=True))

    # Діаграма рівня сигналу
    dy = ly + 50
    p.append(rect(lx + 20, dy, lw - 40, 115, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=4))
    # Позначки рівнів
    p.append(line(lx + 20, dy + 65, lx + lw - 20, dy + 65, color=POS, sw=1.8, dash="4,4"))
    p.append(text(lx + 30, dy + 57, "Пороговий рівень CCA ED (-82 дБм)", size=9.5, color=POS, anchor="start", bold=True))

    # Слабкий сигнал глушника
    p.append(rect(lx + 30, dy + 42, lw - 60, 23, fill="#fadbd8", stroke=POS, sw=1))
    p.append(text(lx + lw / 2, dy + 54, "Слабка несуча завади (-78 дБм > -82 дБм)", size=10, color=POS, bold=True))

    p.append(line(lx + 20, dy + 100, lx + lw - 20, dy + 100, color=MUTED, sw=1))
    p.append(text(lx + 30, dy + 110, "Рівень теплового шуму (-95 дБм)", size=9, color=MUTED, anchor="start"))

    # Пояснення логіки
    p.append(textbox(lx + lw / 2, ly + 245,
                     "Логіка CSMA/CA:\n"
                     "1. Радіоприймач вимірює RSSI > -82 дБм.\n"
                     "2. Вузол вважає: «Канал зайнятий чужою передачею».\n"
                     "3. Запускається Backoff Timer -> постійне відкладання.\n"
                     "Результат: повне мовчання передавача при нулі корисних даних.",
                     size=10, pad=7, fill="#ffffff", stroke="#e74c3c")[0])

    # ── Права частина: Virtual Carrier Sense (NAV Injection) ──
    rx, ry, rw, rh = 485, 75, 410, 345
    p.append(rect(rx, ry, rw, rh, fill="#f8f9f9", stroke=LINE, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 26, "Віртуальний рівень: NAV / RTS-CTS Stuffing", size=12.5, color=INK, bold=True))

    # Структура кадру з полем Duration
    fy = ry + 50
    p.append(rect(rx + 20, fy, rw - 40, 55, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=4))
    # Поля кадру 802.11
    p.append(rect(rx + 25, fy + 10, 55, 34, fill="#eaeded", stroke="#7f8c8d", sw=1))
    p.append(text(rx + 52, fy + 31, "Frame Ctrl", size=9, color=INK))

    p.append(rect(rx + 85, fy + 10, 110, 34, fill="#fdebd0", stroke="#e67e22", sw=1.8))
    p.append(text(rx + 140, fy + 24, "Duration / ID", size=9.5, color="#d35400", bold=True))
    p.append(text(rx + 140, fy + 38, "= 32 767 мкс", size=9, color="#d35400", bold=True))

    p.append(rect(rx + 200, fy + 10, 80, 34, fill="#eaeded", stroke="#7f8c8d", sw=1))
    p.append(text(rx + 240, fy + 31, "RA / TA MAC", size=9, color=INK))

    p.append(rect(rx + 285, fy + 10, 75, 34, fill="#eaeded", stroke="#7f8c8d", sw=1))
    p.append(text(rx + 322, fy + 31, "FCS / CRC", size=9, color=INK))

    # Пояснення логіки NAV
    p.append(textbox(rx + rw / 2, ry + 185,
                     "Механізм віртуального контролю (NAV):\n"
                     "1. Атакуючий шле фіктивний RTS або Data-кадр.\n"
                     "2. У полі Duration встановлено максимум: 32.7 мс.\n"
                     "3. Усі сусідні вузли блокують таймер NAV на 32.7 мс.\n"
                     "4. Повтор пакета 30 разів/с = 100% блокування.",
                     size=10, pad=7, fill="#ffffff", stroke="#e67e22")[0])

    p.append(textbox(rx + rw / 2, ry + 285,
                     "Протидія: обмеження максимального NAV у прошивці,\n"
                     "ігнорування RTS від неавтентифікованих MAC.",
                     size=9.5, pad=6, fill="#e8f8f5", stroke=FIELD)[0])

    render(os.path.join(OUT, "cca-nav-jamming.svg"), W, H, *p,
           title="Блокування бездротового середовища: фізичний поріг CCA та маніпуляція вектором NAV")


# ── 4. iot-resource-exhaustion: Battery Drain & Resource Flooding ──────────────
def fig_iot_resource_exhaustion():
    W, H = 940, 440
    p = []

    # ── Верхній графік: Нормальний робочий цикл пристрою (Sleep vs Wake) ──
    gx, gy, gw, gh = 60, 75, 820, 145
    p.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(gx + 20, gy + 22, "1. Штатний режим (Duty-Cycled IoT): 99.9% глибокий сон, споживання ~5 мкА", size=11, color=FIELD, bold=True, anchor="start"))

    # Часова шкала струму
    base_y = gy + 115
    p.append(line(gx + 40, base_y, gx + gw - 30, base_y, color=LINE, sw=1.5))
    p.append(text(gx + 30, base_y - 25, "Струм", size=9.5, color=MUTED, anchor="end"))
    p.append(text(gx + gw - 20, base_y + 15, "Час →", size=9.5, color=MUTED))

    # Імпульси передачі
    p.append(line(gx + 40, base_y, gx + 180, base_y, color=FIELD, sw=2))
    p.append(rect(gx + 180, base_y - 50, 18, 50, fill="#a9dfbf", stroke=FIELD, sw=1.5))
    p.append(text(gx + 189, base_y - 55, "TX 15 мА", size=9.5, color=FIELD, bold=True))
    p.append(line(gx + 198, base_y, gx + 450, base_y, color=FIELD, sw=2))
    p.append(rect(gx + 450, base_y - 50, 18, 50, fill="#a9dfbf", stroke=FIELD, sw=1.5))
    p.append(line(gx + 468, base_y, gx + 720, base_y, color=FIELD, sw=2))
    p.append(rect(gx + 720, base_y - 50, 18, 50, fill="#a9dfbf", stroke=FIELD, sw=1.5))
    p.append(text(gx + 320, base_y + 16, "Глибокий сон (Deep Sleep 5 мкА) — Ресурс батареї: 3–5 років", size=10, color=FIELD))

    # ── Нижній графік: Атака виснаження батареї (Flood / Sleep Deprivation) ──
    by = 245
    p.append(rect(gx, by, gw, gh, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(gx + 20, by + 22, "2. Атака виснаження (BLE Adv Flood / LoRa Join Flood / Scan Request): приймач постійно активний", size=11, color=POS, bold=True, anchor="start"))

    base_y2 = by + 115
    p.append(line(gx + 40, base_y2, gx + gw - 30, base_y2, color=LINE, sw=1.5))
    p.append(text(gx + 30, base_y2 - 25, "Струм", size=9.5, color=MUTED, anchor="end"))
    p.append(text(gx + gw - 20, base_y2 + 15, "Час →", size=9.5, color=MUTED))

    # Суцільне споживання струму через постійні переривання
    p.append(rect(gx + 40, base_y2 - 50, gw - 70, 50, fill="#fadbd8", stroke=POS, sw=1.5))
    p.append(text(gx + gw / 2, base_y2 - 25, "Постійне неспання (RX / парсинг / IRQ) ~ 12 – 18 мА безперервно", size=11, color=POS, bold=True))
    p.append(text(gx + gw / 2, base_y2 + 16, "Виснаження батареї CR2032 (220 мАг) за 12–18 годин замість 3 років!", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "iot-resource-exhaustion.svg"), W, H, *p,
           title="Атаки виснаження ресурсів (Sleep Deprivation): перетворення мікроамперного сну на безперервне споживання")


if __name__ == "__main__":
    fig_energy_comparison()
    fig_deauth_mechanism()
    fig_cca_nav_jamming()
    fig_iot_resource_exhaustion()
    print("OK: figures ->", OUT)
