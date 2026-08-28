# -*- coding: utf-8 -*-
"""Фігури для теми «Коли своєї плати робити не треба» (koly-svoiei-platy-robyty-ne-treba).
Генерує SVG у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox,
    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG
)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Кольорова палітра для фінансово-інженерних діаграм
COTS_COLOR = "#d97706"    # бурштиновий / готовий блок (швидкий, вища змінна ціна)
CUSTOM_COLOR = "#2563eb"  # синій / власна плата (NRE, низька ціна одиниці)
DANGER_COLOR = "#dc2626"  # червоний / зона збитків, ризик
SUCCESS_COLOR = "#16a34a" # зелений / окупність, прибуток
CARD_BG = "#ffffff"


def fig_cots_vs_custom_tradeoff():
    """1. cots-vs-custom-tradeoff.svg — Графік сукупної вартості (TCO) та точка беззбитковості."""
    W, H = 840, 500
    parts = []

    # Загальний фон
    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 36, "Сукупні витрати (TCO): Готовий COTS-блок проти власної плати", size=15, color=INK, bold=True))

    ox, oy = 90, 410
    gw, gh = 700, 320

    # Сітка та осі
    parts.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))  # вісь X
    parts.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))  # вісь Y

    # Підписи осей
    parts.append(text(ox + gw - 20, oy + 28, "Тираж N (штук)", size=12, color=INK, bold=True))
    parts.append(text(ox - 45, oy - gh + 15, "Сукупні витрати ($)", size=12, color=INK, bold=True))

    x_bep = ox + 233
    y_bep = oy - 160

    # Зони виграшу (заливка трикутників)
    # Зона збитків власної плати (ліворуч від BEP)
    poly_loss = f"M {ox},{oy - 5} L {x_bep},{y_bep} L {ox},{oy - 133} Z"
    parts.append(f'<path d="{poly_loss}" fill="#fee2e2" opacity="0.6"/>')

    # Зона економії власної плати (праворуч від BEP)
    poly_profit = f"M {x_bep},{y_bep} L {ox + 460},{oy - 320} L {ox + 460},{oy - 187} Z"
    parts.append(f'<path d="{poly_profit}" fill="#dcfce7" opacity="0.6"/>')

    # Пунктири сітки
    parts.append(line(ox, y_bep, x_bep, y_bep, color="#94a3b8", sw=1.2, dash="4,4"))
    parts.append(line(x_bep, oy, x_bep, y_bep, color="#94a3b8", sw=1.2, dash="4,4"))

    # Позначки на осях
    parts.append(text(x_bep, oy + 18, "N_bep ≈ 180–220 шт", size=11, color=POS, bold=True))
    parts.append(text(ox - 8, y_bep + 4, "$60k", size=10, color=MUTED, anchor="end"))
    parts.append(text(ox - 8, oy - 133 + 4, "NRE власні ($50k)", size=10, color=CUSTOM_COLOR, anchor="end", bold=True))
    parts.append(text(ox - 8, oy - 5 + 4, "NRE COTS ($2k)", size=10, color=COTS_COLOR, anchor="end"))

    # Лінія COTS (крутий нахил: висока ціна одиниці $300, низькі NRE $2k)
    parts.append(line(ox, oy - 5, ox + 460, oy - 320, color=COTS_COLOR, sw=3))
    parts.append(text(ox + 350, oy - 275, "COTS: $2k NRE + N × $300", size=12, color=COTS_COLOR, bold=True))

    # Лінія власної плати (пологий нахил: низька ціна одиниці $50, високі NRE $50k)
    parts.append(line(ox, oy - 133, ox + gw, oy - 213, color=CUSTOM_COLOR, sw=3))
    parts.append(text(ox + gw - 30, oy - 225, "Власна плата: $50k NRE + N × $50", size=12, color=CUSTOM_COLOR, bold=True, anchor="end"))

    # Точка перетину
    parts.append(circle(x_bep, y_bep, 6, fill=CARD_BG, stroke=POS, sw=2.5))
    parts.append(text(x_bep + 15, y_bep - 12, "Точка беззбитковості (Break-even)", size=11, color=POS, bold=True, anchor="start"))

    # Пояснювальні картки для зон
    parts.append(rect(ox + 20, oy - 95, 170, 50, fill="#ffffff", stroke=DANGER_COLOR, sw=1.2, rx=6))
    parts.append(text(ox + 105, oy - 78, "ЗОНА ЗБИТКІВ ВЛАСНОЇ ПЛАТИ", size=9, color=DANGER_COLOR, bold=True))
    parts.append(text(ox + 105, oy - 62, "COTS вигідніший (N < N_bep)", size=9, color=MUTED))

    parts.append(rect(ox + 330, oy - 140, 200, 50, fill="#ffffff", stroke=SUCCESS_COLOR, sw=1.2, rx=6))
    parts.append(text(ox + 430, oy - 123, "ЗОНА ЕКОНОМІЇ ВЛАСНОЇ ПЛАТИ", size=9, color=SUCCESS_COLOR, bold=True))
    parts.append(text(ox + 430, oy - 107, "Серія окупає R&D (N > N_bep)", size=9, color=MUTED))

    # Пояснювальна смужка внизу
    parts.append(rect(ox + 10, oy + 42, gw - 20, 32, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(text(ox + gw / 2, oy + 62, "Формула: N_bep = (NRE_custom − NRE_cots) / (Ціна_cots − BOM_custom)  →  чим менший тираж, тим сильніший COTS", size=11, color=INK, bold=True))

    return render(out("cots-vs-custom-tradeoff.svg"), W, H, "".join(parts))


def fig_iceberg_hidden_costs():
    """2. iceberg-hidden-costs.svg — Айсберг прихованих витрат власної плати."""
    W, H = 840, 540
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 34, "Айсберг витрат власної розробки заліза проти уявного BOM", size=15, color=INK, bold=True))

    # Фон води (підводна частина)
    water_y = 135
    water_h = 350
    parts.append(rect(25, water_y, W - 50, water_h, fill="#f0fdfa", stroke="#5eead4", sw=1, rx=6))

    # Лінія поверхні води
    parts.append(line(25, water_y, W - 25, water_y, color="#0d9488", sw=2.5, dash="6,4"))
    parts.append(text(W - 40, water_y - 8, "Поверхня води (видима частина)", size=11, color="#0d9488", bold=True, anchor="end"))

    # 1. Над водою: Видимий BOM (10-15% реальної вартості)
    top_x, top_y, top_w, top_h = 160, 55, 520, 68
    parts.append(rect(top_x, top_y, top_w, top_h, fill="#fef3c7", stroke=COTS_COLOR, sw=2, rx=8))
    parts.append(text(top_x + top_w / 2, top_y + 22, "Видима собівартість (BOM у кошику дистриб'ютора)", size=13, color=COTS_COLOR, bold=True))
    parts.append(text(top_x + top_w / 2, top_y + 42, "Сума мікросхем, резисторів, роз'ємів та склотекстоліту ($15–$45 на плату)", size=11, color=INK))
    parts.append(text(top_x + top_w / 2, top_y + 58, "«Ми зробимо це за $30 замість купувати ПЛК за $350!» — класична інженерна пастка", size=10, color=POS, italic=True))

    # 2. Під водою: Реальні приховані витрати (85-90% реальної вартості)
    blocks = [
        {"x": 45, "y": 150, "w": 360, "h": 95, "title": "1. Інженерні людино-години (NRE)",
         "items": ["• Схемотехніка, топологія 4-6 шарів ($15k–$35k)", "• Моделювання цілісності сигналів та живлення", "• Розробка низькорівневого BSP та драйверів"], "bg": "#ffffff", "bc": "#0284c7"},

        {"x": 435, "y": 150, "w": 360, "h": 95, "title": "2. Ітерації заліза (Rev A → Rev B → Rev C)",
         "items": ["• 2–3 повторні замовлення плат і SMD-монтажу", "• Помилки strapping-пінів, перегрів LDO, шум АЦП", "• Затримка проєкту на 3–6 місяців через перезамовлення"], "bg": "#ffffff", "bc": "#dc2626"},

        {"x": 45, "y": 258, "w": 360, "h": 95, "title": "3. Тестувальна інфраструктура (Test Jigs)",
         "items": ["• Проектування стенда з pogo-голками ($3k–$8k)", "• ПЗ автоматизованого вихідного контролю", "• Калібрувальне обладнання та HIL-стенди"], "bg": "#ffffff", "bc": "#7c3aed"},

        {"x": 435, "y": 258, "w": 360, "h": 95, "title": "4. Сертифікація та лабораторії",
         "items": ["• Випробування EMC/EMI в безлунній камері (CE/FCC)", "• Електробезпека LVD, кліматичні тести (-40..+85 °C)", "• Ризик повторної спроби ($8k–$25k за кожну сесію)"], "bg": "#ffffff", "bc": "#ea580c"},

        {"x": 45, "y": 366, "w": 360, "h": 105, "title": "5. Ланцюжок постачання (Supply Chain)",
         "items": ["• EOL / NRND статус компонентів через 6 місяців", "• Мінімальні партії замовлення (MOQ 3000 шт котушки)", "• Заморожений капітал і ризик контрафакту"], "bg": "#ffffff", "bc": "#059669"},

        {"x": 435, "y": 366, "w": 360, "h": 105, "title": "6. Польові відмови та рекламації",
         "items": ["• Відсутність перевіреної часом статистики MTBF", "• Виїзд сервісного техніка в поле ($300–$800 за виклик)", "• Проти 2-хвилинної заміни COTS-блоку на DIN-рейці"], "bg": "#ffffff", "bc": "#b91c1c"}
    ]

    for b in blocks:
        parts.append(rect(b["x"], b["y"], b["w"], b["h"], fill=b["bg"], stroke=b["bc"], sw=1.5, rx=6))
        parts.append(text(b["x"] + 15, b["y"] + 20, b["title"], size=12, color=b["bc"], bold=True, anchor="start"))
        for idx, itm in enumerate(b["items"]):
            parts.append(text(b["x"] + 15, b["y"] + 42 + idx * 18, itm, size=10, color=INK, anchor="start"))

    # Підсумок у нижній плашці (поза межами водної рамки)
    parts.append(rect(45, 495, W - 90, 28, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(W / 2, 513, "Реальна ціна власної плати = BOM + (NRE + Тести + Сертифікація + Ризики) / Тираж", size=10, color=INK, bold=True))

    return render(out("iceberg-hidden-costs.svg"), W, H, "".join(parts))


def fig_decision_matrix():
    """3. decision-matrix.svg — Дерево інженерного вибору архітектури."""
    W, H = 840, 520
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 34, "Дерево інженерного вибору: Готовий COTS → Модуль/SoM → Власна плата", size=15, color=INK, bold=True))

    # Блоки дерева
    # Корінь: Нова апаратна потреба
    parts.append(rect(310, 55, 220, 45, fill="#f1f5f9", stroke=LINE, sw=1.8, rx=6))
    parts.append(text(420, 75, "Новий пристрій / вузол", size=12, color=INK, bold=True))
    parts.append(text(420, 90, "Аналіз вимог та обмежень", size=10, color=MUTED))

    # Стрілка 1 вниз
    parts.append(arrow(420, 100, 420, 130, color=LINE, sw=1.8))

    # Питання 1: Тираж < 200 шт АБО Time-to-Market < 3 міс?
    q1_x, q1_y, q1_w, q1_h = 240, 130, 360, 55
    parts.append(rect(q1_x, q1_y, q1_w, q1_h, fill="#fffbeb", stroke=COTS_COLOR, sw=1.8, rx=8))
    parts.append(text(420, 152, "Тираж < 200 шт/рік АБО", size=12, color=COTS_COLOR, bold=True))
    parts.append(text(420, 170, "термін виходу Time-to-Market < 3 місяців?", size=11, color=INK))

    # Гілка ТАК -> Вправо -> COTS
    parts.append(arrow(600, 157, 670, 157, color=COTS_COLOR, sw=2))
    parts.append(text(635, 147, "ТАК", size=11, color=POS, bold=True))

    parts.append(rect(670, 130, 145, 55, fill="#fef3c7", stroke=COTS_COLOR, sw=2, rx=6))
    parts.append(text(742, 152, "ГОТОВИЙ COTS", size=12, color=COTS_COLOR, bold=True))
    parts.append(text(742, 170, "ПЛК, DIN, смарт-давач", size=10, color=MUTED))

    # Гілка НІ -> Вниз -> Питання 2
    parts.append(arrow(420, 185, 420, 225, color=LINE, sw=1.8))
    parts.append(text(435, 205, "НІ", size=11, color=NEG, bold=True))

    # Питання 2: Потрібна специфічна сертифікація (ATEX, SIL, ISO 13849, Medical)?
    q2_x, q2_y, q2_w, q2_h = 240, 225, 360, 55
    parts.append(rect(q2_x, q2_y, q2_w, q2_h, fill="#fffbeb", stroke=COTS_COLOR, sw=1.8, rx=8))
    parts.append(text(420, 247, "Сувора безпека / сертифікація?", size=12, color=COTS_COLOR, bold=True))
    parts.append(text(420, 265, "ATEX/IECEx, SIL-2/3, ISO 13849, Medical MDR", size=10, color=INK))

    # Гілка ТАК -> Вправо -> Сертифікований промисловий модуль
    parts.append(arrow(600, 252, 670, 252, color=COTS_COLOR, sw=2))
    parts.append(text(635, 242, "ТАК", size=11, color=POS, bold=True))

    parts.append(rect(670, 225, 145, 55, fill="#fef3c7", stroke=COTS_COLOR, sw=2, rx=6))
    parts.append(text(742, 247, "СЕРТИФІКОВАНИЙ COTS", size=11, color=COTS_COLOR, bold=True))
    parts.append(text(742, 265, "Економія $50k+ на тестах", size=10, color=MUTED))

    # Гілка НІ -> Вниз -> Питання 3
    parts.append(arrow(420, 280, 420, 320, color=LINE, sw=1.8))
    parts.append(text(435, 300, "НІ", size=11, color=NEG, bold=True))

    # Питання 3: Чи є жорсткі обмеження габаритів / струму або складна ОС (Linux / Wi-Fi)?
    q3_x, q3_y, q3_w, q3_h = 220, 320, 400, 55
    parts.append(rect(q3_x, q3_y, q3_w, q3_h, fill="#eff6ff", stroke=CUSTOM_COLOR, sw=1.8, rx=8))
    parts.append(text(420, 342, "Складна система (Linux / RF / SoM)", size=12, color=CUSTOM_COLOR, bold=True))
    parts.append(text(420, 360, "при тиражі 200–2000 шт/рік?", size=11, color=INK))

    # Гілка ТАК -> Вліво -> Плата-носій + готовий SoM
    parts.append(arrow(220, 347, 160, 347, color=CUSTOM_COLOR, sw=2))
    parts.append(text(190, 337, "ТАК", size=11, color=POS, bold=True))

    parts.append(rect(15, 320, 145, 55, fill="#dbeafe", stroke=CUSTOM_COLOR, sw=2, rx=6))
    parts.append(text(87, 342, "ГІБРИД: SoM + НОСІЙ", size=11, color=CUSTOM_COLOR, bold=True))
    parts.append(text(87, 360, "CM4 / ESP32 + 2 шари", size=10, color=MUTED))

    # Гілка НІ -> Вниз -> Питання 4 (Масовий тираж)
    parts.append(arrow(420, 375, 420, 415, color=LINE, sw=1.8))
    parts.append(text(435, 395, "НІ", size=11, color=NEG, bold=True))

    # Результат: Повністю власна плата (Chip-down)
    parts.append(rect(230, 415, 380, 60, fill="#dcfce7", stroke=SUCCESS_COLOR, sw=2, rx=8))
    parts.append(text(420, 438, "ПОВНІСТЮ ВЛАСНА ПЛАТА (Chip-down)", size=13, color=SUCCESS_COLOR, bold=True))
    parts.append(text(420, 458, "Масовий тираж (>2000–5000 шт), унікальний формфактор або фронтенд", size=10, color=INK))

    # Довідкова рамка ліворуч унизу
    parts.append(rect(15, 415, 195, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    parts.append(text(112, 438, "Правило тверезості:", size=11, color=INK, bold=True))
    parts.append(text(112, 458, "«Не винаходь колесо, якщо", size=10, color=MUTED))
    parts.append(text(112, 470, "його вже сертифікували»", size=10, color=MUTED))

    return render(out("decision-matrix.svg"), W, H, "".join(parts))


def fig_cost_of_delay():
    """4. cost-of-delay.svg — Графік втраченої вигоди через затримку виходу на ринок (Cost of Delay)."""
    W, H = 840, 460
    parts = []

    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    parts.append(text(W / 2, 34, "Ціна затримки (Cost of Delay): Запуск на COTS проти затягнутої власної розробки", size=15, color=INK, bold=True))

    ox, oy = 80, 380
    gw, gh = 710, 290

    # Осі
    parts.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    parts.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    parts.append(text(ox + gw - 20, oy + 25, "Час (місяці)", size=11, color=INK, bold=True))
    parts.append(text(ox - 35, oy - gh + 15, "Чистий грошовий потік / виручка ($)", size=11, color=INK, bold=True))

    # Мітки часу на осі X (кожні 2 місяці: 0, 2, 4, 6, 8, 10, 12, 14, 16, 18)
    for m_idx in range(0, 19, 2):
        pos_x = ox + m_idx * (gw / 18)
        parts.append(line(pos_x, oy - 4, pos_x, oy + 4, color=LINE, sw=1.5))
        parts.append(text(pos_x, oy + 18, f"М{m_idx}", size=10, color=MUTED))

    # 1. Сценарій COTS: старт М0, вихід на ринок М2.
    cots_pts = [
        (ox, oy),
        (ox + 2 * (gw / 18), oy - 10),    # М2: реліз
        (ox + 4 * (gw / 18), oy - 60),    # М4: перші клієнти
        (ox + 8 * (gw / 18), oy - 160),   # М8: ріст
        (ox + 12 * (gw / 18), oy - 230),  # М12: зрілість
        (ox + 18 * (gw / 18), oy - 270)   # М18: стабільний потік
    ]

    # 2. Сценарій власної плати: старт М0, розробка, ревізії A, B, сертифікація -> реліз аж на М11.
    custom_pts = [
        (ox, oy),
        (ox + 3 * (gw / 18), oy + 35),    # М3: витрати NRE Rev A
        (ox + 6 * (gw / 18), oy + 55),    # М6: витрати NRE Rev B + тести
        (ox + 9 * (gw / 18), oy + 40),    # М9: сертифікація
        (ox + 11 * (gw / 18), oy),        # М11: реліз (вихід у 0)
        (ox + 14 * (gw / 18), oy - 110),  # М14: початок продажів
        (ox + 18 * (gw / 18), oy - 240)   # М18: наздоганяння
    ]

    # Зона втраченої виручки (Cost of Delay) між М2 та М18
    poly_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in cots_pts)
    poly_d += " L " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in reversed(custom_pts))
    poly_d += " Z"
    parts.append(f'<path d="{poly_d}" fill="#fee2e2" opacity="0.5"/>')

    # Малюємо лінії
    cots_line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in cots_pts)
    parts.append(f'<path d="{cots_line_d}" fill="none" stroke="{COTS_COLOR}" stroke-width="3"/>')

    custom_line_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in custom_pts)
    parts.append(f'<path d="{custom_line_d}" fill="none" stroke="{CUSTOM_COLOR}" stroke-width="3"/>')

    # Позначки релізів
    parts.append(circle(ox + 2 * (gw / 18), oy - 10, 5, fill=COTS_COLOR, stroke=CARD_BG, sw=2))
    parts.append(text(ox + 2 * (gw / 18) + 8, oy - 22, "Реліз на COTS (М2)", size=10, color=COTS_COLOR, bold=True, anchor="start"))

    parts.append(circle(ox + 11 * (gw / 18), oy, 5, fill=CUSTOM_COLOR, stroke=CARD_BG, sw=2))
    parts.append(text(ox + 11 * (gw / 18) + 8, oy + 18, "Реліз власної плати (М11)", size=10, color=CUSTOM_COLOR, bold=True, anchor="start"))

    # Текст у зоні втраченої вигоди
    parts.append(rect(ox + 200, oy - 145, 230, 50, fill="#ffffff", stroke=DANGER_COLOR, sw=1.2, rx=6))
    parts.append(text(ox + 315, oy - 128, "ВТРАЧЕНА ВИГОДА (Cost of Delay)", size=11, color=DANGER_COLOR, bold=True))
    parts.append(text(ox + 315, oy - 110, "9 місяців відсутності продажів та клієнтів", size=9, color=MUTED))

    # Пояснювальний блок знизу
    parts.append(rect(ox + 20, oy + 42, gw - 40, 28, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(ox + gw / 2, oy + 60, "Економія $50 на собівартості плати не має сенсу, якщо компанія втратила ринкове вікно і річну виручку від клієнтів", size=10, color=INK, bold=True))

    return render(out("cost-of-delay.svg"), W, H, "".join(parts))


def main():
    fig_cots_vs_custom_tradeoff()
    fig_iceberg_hidden_costs()
    fig_decision_matrix()
    fig_cost_of_delay()
    print("Усі 4 фігури згенеровано успішно в img/")


if __name__ == "__main__":
    main()
