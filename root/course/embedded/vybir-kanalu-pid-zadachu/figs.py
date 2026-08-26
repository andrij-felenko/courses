# -*- coding: utf-8 -*-
"""Фігури до статті «Вибір каналу під задачу» (root/course/embedded/vybir-kanalu-pid-zadachu).
Запуск: python figs.py  -> створює SVG у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

def _tint(c):
    m = {
        POS: "#fbe7e4",
        NEG: "#e6ecfb",
        FIELD: "#e4f4ea",
        "#b8860b": "#f6efdb",
        "#7d3c98": "#efe6f4",
        "#d35400": "#fbeee6"
    }
    return m.get(c, "#f4f6f8")


# ── 1. Простір критеріїв: компроміс характеристик технологій ──────────────────
def fig_criteria_tradeoff():
    W, H = 820, 480
    f = [text(W / 2, 28, "Простір компромісів: три головні сімейства бездротових каналів", 16, INK, "middle", bold=True)]

    # 3 великі колонки-картки
    cards = [
        ("Локальні мережі (Short-Range)", "BLE · Wi-Fi · 802.15.4 · ESP-NOW", NEG, 50,
         [("Радіус дії", "10–100 м (у межах будівлі)"),
          ("Швидкість", "250 кбіт/с — 150+ Мбіт/с"),
          ("Затримка", "1–10 мс (інтерактивна)"),
          ("Енергія на біт", "Мінімальна (нДж/біт)"),
          ("CAPEX / OPEX", "Низький модуль / Без абонплати"),
          ("Головне обмеження", "Локальна інфраструктура (шлюз)")]),

        ("Неліцензовані та стільникові LPWAN", "LoRaWAN · Sigfox · NB-IoT · LTE-M", FIELD, 305,
         [("Радіус дії", "2–15+ км (місто, підвали, поля)"),
          ("Швидкість", "100 біт/с — 250 кбіт/с"),
          ("Затримка", "Секунди — хвилини (сон)"),
          ("Енергія на біт", "Висока на біт, низька на сесію"),
          ("CAPEX / OPEX", "LoRa: шлюз / NB: $0.5–2/міс SIM"),
          ("Головне обмеження", "Duty cycle 1% / Тонкий потік")]),

        ("Швидкісні стільникові канали", "LTE Cat-1 · LTE Cat-4", "#7d3c98", 560,
         [("Радіус дії", "Кілометри (покриття оператора)"),
          ("Швидкість", "10–150 Мбіт/с (потік/відео)"),
          ("Затримка", "20–50 мс (мобільна IP-мережа)"),
          ("Енергія на біт", "Помірна, але високі піки (1–2 А)"),
          ("CAPEX / OPEX", "$10–25 модуль / $3–15/міс SIM"),
          ("Головне обмеження", "Потребує мережі або АКБ >2 Аг")])
    ]

    card_w = 230
    card_h = 380
    top_y = 65

    for title, sub, col, x, rows in cards:
        # заголовок картки
        f.append(rect(x, top_y, card_w, card_h, fill=_tint(col), stroke=col, sw=1.8, rx=8))
        f.append(rect(x, top_y, card_w, 56, fill=col, stroke=col, sw=1.8, rx=8))
        f.append(rect(x, top_y + 40, card_w, 16, fill=col, stroke=col, sw=0, rx=0))
        f.append(text(x + card_w / 2, top_y + 22, title, 11.5, "#ffffff", "middle", bold=True))
        f.append(text(x + card_w / 2, top_y + 42, sub, 9.5, "#f0f4f8", "middle"))

        # параметри
        ry = top_y + 68
        for label, val in rows:
            f.append(text(x + 10, ry + 12, label, 10, col, "start", bold=True))
            f.append(text(x + 10, ry + 28, val, 9.5, INK, "start"))
            ry += 42
            f.append(line(x + 8, ry, x + card_w - 8, ry, color="#dde3ea", sw=0.8))
            ry += 8

    f.append(fitbox(50, top_y + card_h + 12, 740, 32,
                    "Жоден канал не поєднує гігабітну швидкість, 10-кілометровий радіус, нульову абонплату та 10 років роботи від дискової батарейки.\n"
                    "Інженерний вибір — це завжди обмін менш важливого параметра на критично необхідний.",
                    size=10, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    render(os.path.join(IMG, "criteria-tradeoff.svg"), W, H + 40, *f)


# ── 2. Профілі струму транзакцій різних технологій ────────────────────────────
def fig_power_profiles():
    W, H = 840, 470
    f = [text(W / 2, 26, "Струмовий профіль сеансу зв'язку: де витрачається енергія батареї", 16, INK, "middle", bold=True)]

    profiles = [
        ("BLE 5.0 (Швидкий сплеск)", NEG, 50, 70,
         "Сеанс: 2–5 мс · Пік: 15 мА · Сон: 1.5 мкА · Енергія: ~0.1 мДж",
         [(0, 0), (20, 0), (25, 40), (45, 40), (50, 0), (220, 0)]),

        ("LoRaWAN EU868 SF10/12 (Довгий ефір)", FIELD, 50, 190,
         "Сеанс: 1.5 с (Airtime) + вікна RX1/RX2 · Пік: 40 мА · Енергія: ~180 мДж",
         [(0, 0), (15, 0), (20, 55), (110, 55), (115, 5), (145, 5), (150, 35), (160, 35), (165, 5), (190, 5), (195, 35), (205, 35), (210, 0), (220, 0)]),

        ("NB-IoT / LTE-M у режимі PSM (Синхронізація + Передача)", "#7d3c98", 50, 310,
         "Сеанс: 1.2–3.5 с · Піки: 220–500 мА · Сон PSM: 3 мкА · Енергія: ~450 мДж",
         [(0, 0), (10, 0), (15, 30), (35, 30), (40, 75), (45, 20), (55, 80), (60, 20), (75, 75), (85, 25), (130, 25), (135, 0), (220, 0)])
    ]

    for title, col, ox, oy, desc, pts in profiles:
        f.append(text(ox, oy - 8, title, 12.5, col, "start", bold=True))
        f.append(text(ox + 420, oy - 8, desc, 10, MUTED, "start"))

        gx, gy = ox, oy + 8
        gw, gh = 740, 65
        f.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=4))

        svg_pts = []
        for px, py in pts:
            sx = gx + 15 + (px / 220.0) * (gw - 30)
            sy = gy + gh - 6 - (py / 85.0) * (gh - 14)
            svg_pts.append((sx, sy))

        path_d = ["M %.1f %.1f" % svg_pts[0]]
        for pt in svg_pts[1:]:
            path_d.append("L %.1f %.1f" % pt)

        poly_d = list(path_d)
        poly_d.append("L %.1f %.1f" % (svg_pts[-1][0], gy + gh - 6))
        poly_d.append("L %.1f %.1f" % (svg_pts[0][0], gy + gh - 6))
        poly_d.append("Z")
        f.append('<path d="%s" fill="%s" opacity="0.25"/>' % (" ".join(poly_d), col))
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(path_d), col))

    f.append(fitbox(50, 420, 740, 36,
                    "У стільникових модулях та LoRaWAN витрати енергії визначаються не стільки передачею байтів, скільки супутніми фазами:\n"
                    "пробудження синтезатора, підтримання синхронізації соти, очікування вікон прийому (RX) та засинання.",
                    size=10, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    render(os.path.join(IMG, "power-profiles-comparison.svg"), W, H, *f)


# ── 3. Профілі трафіку та технологічні відповідності ──────────────────────────
def fig_traffic_patterns():
    W, H = 840, 450
    f = [text(W / 2, 28, "Класифікація трафіку пристроїв та оптимальний вибір інтерфейсу", 16, INK, "middle", bold=True)]

    patterns = [
        ("1. Неперервний потік", "Continuous Streaming", POS, 50, 70,
         "Обсяг: мегабайти / гігабайти\n"
         "Затримка: <50–100 мс (жорстка)\n"
         "Характер: потокове відео/аудіо, RTK-навігація, високочастотна телеметрія 50–100 Гц\n"
         "Живлення: стаціонарна мережа або АКБ із щоденною підзарядкою",
         "Wi-Fi (802.11ax/ac/n)\nLTE Cat-1 / Cat-4\nEthernet"),

        ("2. Періодична телеметрія", "Periodic Reporting", FIELD, 50, 190,
         "Обсяг: 10–200 байтів\n"
         "Період: 1 раз на 15 хв — 1 раз на добу\n"
         "Характер: лічильники води/газу/тепла, метеостанції, агромоніторинг ґрунту\n"
         "Живлення: автономна батарея LiSOCl2 / LiMnO2 на 5–10 років",
         "LoRaWAN (Class A)\nNB-IoT (PSM)\nSigfox (12 B)\nBLE Beacon"),

        ("3. Подійно-аварійний трафік", "Event-Driven & Reactive", "#7d3c98", 50, 310,
         "Обсяг: 10–50 байтів на тривогу\n"
         "Затримка: критична (<1–3 с на доставку сигналу)\n"
         "Характер: датчики відкриття дверей/люків, пожежна тривога, витік газу, SOS-кнопки\n"
         "Живлення: батарея або мережа + резервний акумулятор",
         "LTE-M / NB-IoT\nLoRaWAN (переривання)\nZigbee / Thread\nESP-NOW")
    ]

    for title, eng, col, ox, oy, desc, rec in patterns:
        f.append(rect(ox, oy, 740, 105, fill="#fbfcfd", stroke="#dde3ea", sw=1.2, rx=6))
        f.append(rect(ox, oy, 6, 105, fill=col, stroke=col, sw=0, rx=0))

        f.append(text(ox + 20, oy + 24, title, 13, col, "start", bold=True))
        f.append(text(ox + 20, oy + 42, "(%s)" % eng, 9.5, MUTED, "start"))

        f.append(fitbox(ox + 180, oy + 8, 380, 88, desc, size=10, fill="#fbfcfd", stroke="#fbfcfd", color=INK))

        f.append(rect(ox + 575, oy + 8, 150, 88, fill=_tint(col), stroke=col, sw=1.4, rx=6))
        f.append(text(ox + 650, oy + 24, "Оптимальний вибір:", 9.5, col, "middle", bold=True))
        f.append(fitbox(ox + 580, oy + 32, 140, 58, rec, size=10, fill=_tint(col), stroke=_tint(col), color=INK, bold=True))

    render(os.path.join(IMG, "traffic-patterns.svg"), W, H, *f)


# ── 4. Дерево прийняття рішень (Decision Tree) ─────────────────────────────────
def fig_decision_tree():
    W, H = 840, 520
    f = [text(W / 2, 26, "Інженерне дерево вибору бездротового інтерфейсу для пристрою", 16, INK, "middle", bold=True)]

    # Корінь
    root_x, root_y = 420, 60
    f.append(rect(root_x - 140, root_y - 18, 280, 36, fill="#eef2f7", stroke=INK, sw=1.8, rx=6))
    f.append(text(root_x, root_y + 5, "Яка потрібна дальність зв'язку?", 12, INK, "middle", bold=True))

    # Гілка 1: Локальна (<100 м)
    l1_x, l1_y = 180, 140
    f.append(arrow(root_x - 70, root_y + 18, l1_x, l1_y - 18, color=NEG, sw=1.6))
    f.append(text(250, 100, "< 100 м (локально)", 10, NEG, "middle", bold=True))

    f.append(rect(l1_x - 120, l1_y - 16, 240, 32, fill=_tint(NEG), stroke=NEG, sw=1.5, rx=6))
    f.append(text(l1_x, l1_y + 4, "Який профіль швидкості/даних?", 11, NEG, "middle", bold=True))

    # Локальні листки
    # Wi-Fi
    f.append(arrow(l1_x - 50, l1_y + 16, 75, 230, color=NEG, sw=1.2))
    f.append(text(75, 195, ">1 Мбіт/с / IP", 9.5, MUTED, "middle"))
    f.append(rect(15, 230, 120, 50, fill="#fbfcfd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(75, 250, "Wi-Fi (802.11)", 11, NEG, "middle", bold=True))
    f.append(text(75, 268, "Потік, 220 В / АКБ", 9, MUTED, "middle"))

    # BLE
    f.append(arrow(l1_x, l1_y + 16, 180, 230, color=NEG, sw=1.2))
    f.append(text(180, 195, "Смартфон / нДж", 9.5, MUTED, "middle"))
    f.append(rect(125, 230, 110, 50, fill="#fbfcfd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(180, 250, "BLE 5.x", 11, NEG, "middle", bold=True))
    f.append(text(180, 268, "Дискова CR2032", 9, MUTED, "middle"))

    # Zigbee / Thread / ESP-NOW
    f.append(arrow(l1_x + 60, l1_y + 16, 290, 230, color=NEG, sw=1.2))
    f.append(text(290, 195, "Mesh / p2p", 9.5, MUTED, "middle"))
    f.append(rect(235, 230, 120, 50, fill="#fbfcfd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(295, 250, "Thread / Zigbee", 11, NEG, "middle", bold=True))
    f.append(text(295, 268, "Розумний дім / Mesh", 9, MUTED, "middle"))

    # Гілка 2: Велика дальність (>1 км, Wide Area)
    r1_x, r1_y = 620, 140
    f.append(arrow(root_x + 70, root_y + 18, r1_x, r1_y - 18, color=FIELD, sw=1.6))
    f.append(text(580, 100, "> 1 км (Wide Area)", 10, FIELD, "middle", bold=True))

    f.append(rect(r1_x - 130, r1_y - 16, 260, 32, fill=_tint(FIELD), stroke=FIELD, sw=1.5, rx=6))
    f.append(text(r1_x, r1_y + 4, "Яка потрібна швидкість і потік?", 11, FIELD, "middle", bold=True))

    # LPWAN sub-branch
    lp_x, lp_y = 510, 235
    f.append(arrow(r1_x - 50, r1_y + 16, lp_x, lp_y - 16, color=FIELD, sw=1.4))
    f.append(text(490, 195, "< 10 кбіт/с (рідко)", 9.5, FIELD, "middle", bold=True))

    f.append(rect(lp_x - 110, lp_y - 16, 220, 32, fill=_tint(FIELD), stroke=FIELD, sw=1.4, rx=6))
    f.append(text(lp_x, lp_y + 4, "Чи є оператор / бюджет OPEX?", 10.5, FIELD, "middle", bold=True))

    # LoRaWAN
    f.append(arrow(lp_x - 50, lp_y + 16, 430, 325, color=FIELD, sw=1.2))
    f.append(text(415, 290, "Своя мережа ($0)", 9, MUTED, "middle"))
    f.append(rect(370, 325, 120, 52, fill="#fbfcfd", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(430, 345, "LoRaWAN", 11, FIELD, "middle", bold=True))
    f.append(text(430, 363, "10 років батареї", 9, MUTED, "middle"))

    # NB-IoT / LTE-M
    f.append(arrow(lp_x + 50, lp_y + 16, 560, 325, color=FIELD, sw=1.2))
    f.append(text(575, 290, "SIM оператора", 9, MUTED, "middle"))
    f.append(rect(500, 325, 125, 52, fill="#fbfcfd", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(562, 345, "NB-IoT / LTE-M", 11, FIELD, "middle", bold=True))
    f.append(text(562, 363, "PSM, соти без шлюзу", 9, MUTED, "middle"))

    # Cellular High Speed
    cell_x, cell_y = 730, 235
    f.append(arrow(r1_x + 50, r1_y + 16, cell_x, cell_y - 16, color="#7d3c98", sw=1.4))
    f.append(text(730, 195, "> 1 Мбіт/с (відео/потік)", 9.5, "#7d3c98", "middle", bold=True))

    f.append(rect(650, 325, 160, 52, fill="#fbfcfd", stroke="#7d3c98", sw=1.5, rx=6))
    f.append(text(730, 345, "LTE Cat-1 / Cat-4", 11, "#7d3c98", "middle", bold=True))
    f.append(text(730, 363, "Постійний IP / 220 В / АКБ", 9, MUTED, "middle"))

    f.append(fitbox(50, 425, 740, 46,
                    "Ключове правило архітектора вбудованих систем: спочатку визначається профіль трафіку й енергетичний ліміт,\n"
                    "і лише потім — фізичний радіус і конкретна мікросхема трансивера.",
                    size=10.5, fill="#fbfcfd", stroke="#dde3ea", color=INK, bold=True))

    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


if __name__ == "__main__":
    fig_criteria_tradeoff()
    fig_power_profiles()
    fig_traffic_patterns()
    fig_decision_tree()
    print("OK: figures generated in", IMG)
