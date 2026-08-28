# -*- coding: utf-8 -*-
"""Фігури для теми «Ціна однієї ітерації заліза» (tsina-odniiei-iteratsii-zaliza).
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

# Кольорова палітра підрозділів виробництва
EDA_COLOR = "#0284c7"      # блакитний (CAD / Проєктування)
DFM_COLOR = "#d97706"      # бурштиновий (DFM / Перевірка)
FAB_COLOR = "#7c3aed"      # фіолетовий (Виробництво PCB)
SMT_COLOR = "#059669"      # смарагдовий (Монтаж SMT)
BRING_COLOR = "#2563eb"    # синій (Bring-up / Налагодження)
WARN_COLOR = "#dc2626"     # червоний (Помилка / Перезамовлення)
CARD_BG = "#ffffff"


def fig_iteration_pipeline():
    """1. iteration-pipeline.svg — Повний виробничий ланцюжок ітерації заліза та петля помилки."""
    W, H = 880, 500
    parts = []

    # Загальне полотно
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(W / 2, 34, "Виробничий ланцюжок апаратної ітерації друкованої плати (PCB Cycle)", size=15, color=INK, bold=True))

    # Етапи у верхньому ряду (5 блоків)
    steps = [
        ("1. CAD Експорт", "Gerber X2, BOM,\nCPL Pick & Place,\nNetlist, DRC", EDA_COLOR, "#e0f2fe"),
        ("2. DFM / CAM", "Перевірка зазорів,\nпаяльної маски,\nінженерні EQ", DFM_COLOR, "#fef3c7"),
        ("3. PCB Фабрикація", "Травлення міді, свердління,\nметалізація PTH, маска,\nфінішне покриття (ENIG)", FAB_COLOR, "#ede9fe"),
        ("4. SMT Монтаж", "Трафарет, паяльна паста,\nPick-and-Place автомат,\nоплавлення в печі, AOI", SMT_COLOR, "#d1fae5"),
        ("5. Bring-up", "Опір ліній живлення,\nперше ввімкнення, JTAG,\nперевірка периферії", BRING_COLOR, "#dbeafe"),
    ]

    bw, bh = 150, 115
    start_x, y_step = 25, 65
    gap_x = 24

    for i, (title, desc, stroke_c, bg_c) in enumerate(steps):
        x = start_x + i * (bw + gap_x)
        parts.append(rect(x, y_step, bw, bh, fill=bg_c, stroke=stroke_c, sw=1.8, rx=6))
        parts.append(text(x + bw / 2, y_step + 22, title, size=11, color=stroke_c, bold=True))
        parts.append(line(x + 10, y_step + 32, x + bw - 10, y_step + 32, color=stroke_c, sw=1.0))
        parts.append(mtext(x + bw / 2, y_step + 50, desc, size=10, color=INK, lh=1.35))

        # Стрілка між кроками
        if i < len(steps) - 1:
            arrow_x1 = x + bw + 2
            arrow_x2 = arrow_x1 + gap_x - 4
            parts.append(arrow(arrow_x1, y_step + bh / 2, arrow_x2, y_step + bh / 2, color="#64748b", sw=1.5))

    # Нижня частина: Розгалуження після Bring-up
    # Успіх (зелений блок праворуч)
    pass_x, pass_y = 660, 245
    pass_w, pass_h = 190, 100
    parts.append(rect(pass_x, pass_y, pass_w, pass_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=6))
    parts.append(text(pass_x + pass_w / 2, pass_y + 24, "УСПІХ (Плата працює)", size=11, color=FIELD, bold=True))
    parts.append(mtext(pass_x + pass_w / 2, pass_y + 50, "Розробка прошивки,\nінтеграційні тести,\nпідготовка до серії", size=10, color=INK, lh=1.35))

    # Стрілка вниз від Step 5 до блоку Успіху
    step5_cx = start_x + 4 * (bw + gap_x) + bw / 2  # 721 + 75 = 796
    parts.append(arrow(step5_cx, y_step + bh + 2, pass_x + pass_w / 2, pass_y - 2, color=FIELD, sw=2))
    parts.append(text(step5_cx + 12, 215, "Тести пройдено", size=10, color=FIELD, bold=True, anchor="start"))

    # Фатальна помилка (червона петля перезамовлення)
    fail_x, fail_y = 25, 245
    fail_w, fail_h = 590, 100
    parts.append(rect(fail_x, fail_y, fail_w, fail_h, fill="#fef2f2", stroke=WARN_COLOR, sw=2, rx=6))
    parts.append(text(fail_x + fail_w / 2, fail_y + 22, "КРИТИЧНА АПАРАТНА ПОМИЛКА (Неправильний футпрінт, замикання у внутрішніх шарах)", size=10.5, color=WARN_COLOR, bold=True))
    parts.append(mtext(fail_x + fail_w / 2, fail_y + 46, "• Затримка проєкту: 14–28 днів (перевиправлення CAD, очікування нової ревізії Rev B)\n• Фінансові втрати: списання зіпсованих компонентів, повторна оплата підготовки SMT, доставка\n• Простій команди: розробники прошивки заблоковані через відсутність робочого заліза", size=9.5, color=INK, lh=1.35))

    # Стрілка від Step 5 до червоної зони
    step5_left_x = start_x + 4 * (bw + gap_x) + 20  # 741
    parts.append(line(step5_left_x, y_step + bh + 2, step5_left_x, 210, color=WARN_COLOR, sw=1.8))
    parts.append(line(step5_left_x, 210, fail_x + fail_w - 50, 210, color=WARN_COLOR, sw=1.8))
    parts.append(arrow(fail_x + fail_w - 50, 210, fail_x + fail_w - 50, fail_y - 2, color=WARN_COLOR, sw=1.8))
    parts.append(text(fail_x + fail_w - 60, 202, "Критичний дефект", size=10, color=WARN_COLOR, bold=True, anchor="end"))

    # Зворотна стрілка перезамовлення з червоної зони назад у CAD
    parts.append(line(fail_x + 80, fail_y, fail_x + 80, 210, color=WARN_COLOR, sw=1.8, dash="4,4"))
    parts.append(line(fail_x + 80, 210, start_x + bw / 2, 210, color=WARN_COLOR, sw=1.8, dash="4,4"))
    parts.append(arrow(start_x + bw / 2, 210, start_x + bw / 2, y_step + bh + 2, color=WARN_COLOR, sw=1.8))
    parts.append(text(fail_x + 90, 200, "Перевипуск ревізії (+2..4 тижні)", size=9.5, color=WARN_COLOR, bold=True, anchor="start"))

    # Альтернатива: Локальне виправлення (bodge/surgery)
    bodge_x, bodge_y = 25, 375
    parts.append(rect(bodge_x, bodge_y, 825, 95, fill="#eff6ff", stroke=EDA_COLOR, sw=1.5, rx=6))
    parts.append(text(bodge_x + 412, bodge_y + 24, "Альтернатива: Лабораторна «хірургія» (Різання доріжок + Перемички + Dead-Bug)", size=11, color=EDA_COLOR, bold=True))
    parts.append(mtext(bodge_x + 412, bodge_y + 50, "Дозволяє відновити базові функції за 1–4 години та продовжити розробку вбудованого ПЗ,\nпоки виправлена ревізія друкується й монтується у фоновому режимі.", size=10, color=INK, lh=1.35))

    render(out("iteration-pipeline.svg"), W, H, *parts)


def fig_turnaround_comparison():
    """2. turnaround-comparison.svg — Графік витрат часу та фінансів при різних стратегіях ітерації."""
    W, H = 880, 480
    parts = []

    # Загальне полотно
    parts.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(W / 2, 34, "Порівняння сценаріїв подолання апаратної помилки: Час і Фінанси", size=15, color=INK, bold=True))

    # Сценарій 1: Стандартне перезамовлення плат (Повний цикл)
    y1 = 65
    parts.append(rect(25, y1, 830, 115, fill="#fff1f2", stroke=WARN_COLOR, sw=1.5, rx=6))
    parts.append(text(40, y1 + 22, "Сценарій А: Повне стандартне перезамовлення (Rev B)", size=12, color=WARN_COLOR, bold=True, anchor="start"))
    parts.append(text(835, y1 + 22, "Час: 18–25 днів | Вартість: $1500–$4000*", size=10.5, color=WARN_COLOR, bold=True, anchor="end"))

    # Шкала прогресу Сценарію А
    parts.append(rect(40, y1 + 38, 120, 30, fill="#fda4af", stroke=WARN_COLOR, sw=1))
    parts.append(text(100, y1 + 57, "CAD + DFM (2 дні)", size=9.5, color=INK, bold=True))

    parts.append(rect(160, y1 + 38, 180, 30, fill="#f43f5e", stroke=WARN_COLOR, sw=1))
    parts.append(text(250, y1 + 57, "Fab PCB (4-5 днів)", size=9.5, color="#ffffff", bold=True))

    parts.append(rect(340, y1 + 38, 200, 30, fill="#e11d48", stroke=WARN_COLOR, sw=1))
    parts.append(text(440, y1 + 57, "SMT + Логістика (5-7 днів)", size=9.5, color="#ffffff", bold=True))

    parts.append(rect(540, y1 + 38, 180, 30, fill="#be123c", stroke=WARN_COLOR, sw=1))
    parts.append(text(630, y1 + 57, "Доставка (4-6 днів)", size=9.5, color="#ffffff", bold=True))

    parts.append(rect(720, y1 + 38, 110, 30, fill="#9f1239", stroke=WARN_COLOR, sw=1))
    parts.append(text(775, y1 + 57, "Bring-up (2 дні)", size=9.5, color="#ffffff", bold=True))

    parts.append(text(40, y1 + 98, "*Враховано прямі витрати на фабрикацію + ціну простою команди розробників під час блокування.", size=9.5, color=MUTED, anchor="start"))

    # Сценарій 2: Терміновий запуск (Fast-turn + Express)
    y2 = 200
    parts.append(rect(25, y2, 830, 115, fill="#fefce8", stroke=DFM_COLOR, sw=1.5, rx=6))
    parts.append(text(40, y2 + 22, "Сценарій Б: Прискорене перезамовлення (Fast-turn Fab + Express Courier)", size=12, color=DFM_COLOR, bold=True, anchor="start"))
    parts.append(text(835, y2 + 22, "Час: 6–8 днів | Вартість: $800–$1800", size=10.5, color=DFM_COLOR, bold=True, anchor="end"))

    # Шкала прогресу Сценарію Б
    parts.append(rect(40, y2 + 38, 80, 30, fill="#fde047", stroke=DFM_COLOR, sw=1))
    parts.append(text(80, y2 + 57, "CAD (1 д)", size=9.5, color=INK, bold=True))

    parts.append(rect(120, y2 + 38, 140, 30, fill="#eab308", stroke=DFM_COLOR, sw=1))
    parts.append(text(190, y2 + 57, "24h/48h Fab ($$$)", size=9.5, color=INK, bold=True))

    parts.append(rect(260, y2 + 38, 150, 30, fill="#ca8a04", stroke=DFM_COLOR, sw=1))
    parts.append(text(335, y2 + 57, "Швидкий SMT (2 д)", size=9.5, color="#ffffff", bold=True))

    parts.append(rect(410, y2 + 38, 140, 30, fill="#a16207", stroke=DFM_COLOR, sw=1))
    parts.append(text(480, y2 + 57, "DHL/FedEx (2-3 д)", size=9.5, color="#ffffff", bold=True))

    parts.append(rect(550, y2 + 38, 90, 30, fill="#713f12", stroke=DFM_COLOR, sw=1))
    parts.append(text(595, y2 + 57, "Bring-up (1 д)", size=9.5, color="#ffffff", bold=True))

    parts.append(text(40, y2 + 98, "Плата за терміновість (Rush fee) збільшує вартість фабрикації у 2–4 рази, але суттєво рятує дедлайн.", size=9.5, color=MUTED, anchor="start"))

    # Сценарій 3: Лабораторне виправлення перемичками (Bodge wire surgery)
    y3 = 335
    parts.append(rect(25, y3, 830, 115, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(40, y3 + 22, "Сценарій В: Лабораторний ремонт (Trace Cut + Bodge Wire + Dead Bug)", size=12, color=FIELD, bold=True, anchor="start"))
    parts.append(text(835, y3 + 22, "Час: 2–6 годин | Прямі витрати: ~$0", size=10.5, color=FIELD, bold=True, anchor="end"))

    # Шкала прогресу Сценарію В
    parts.append(rect(40, y3 + 38, 160, 30, fill="#86efac", stroke=FIELD, sw=1))
    parts.append(text(120, y3 + 57, "Аналіз схеми (1 год)", size=9.5, color=INK, bold=True))

    parts.append(rect(200, y3 + 38, 180, 30, fill="#22c55e", stroke=FIELD, sw=1))
    parts.append(text(290, y3 + 57, "Різання + Пайка (2-3 год)", size=9.5, color="#ffffff", bold=True))

    parts.append(rect(380, y3 + 38, 150, 30, fill="#15803d", stroke=FIELD, sw=1))
    parts.append(text(455, y3 + 57, "Перевірка тестером (1 год)", size=9.5, color="#ffffff", bold=True))

    parts.append(rect(530, y3 + 38, 300, 30, fill="#166534", stroke=FIELD, sw=1))
    parts.append(text(680, y3 + 57, "РОЗРОБКА ПРОШИВКИ ТРИВАЄ БЕЗ ЗУПИНКИ!", size=9.5, color="#ffffff", bold=True))

    parts.append(text(40, y3 + 98, "Дозволяє команді писати код драйверів вже сьогодні, доки виправлена версія плати виготовляється штатно.", size=9.5, color=MUTED, anchor="start"))

    render(out("turnaround-comparison.svg"), W, H, *parts)


def fig_hardware_surgery_anatomy():
    """3. hardware-surgery-anatomy.svg — Анатомія технік ручного виправлення друкованих плат."""
    W, H = 880, 430
    parts = []

    # Загальне полотно
    parts.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(W / 2, 34, "Анатомія технік швидкого апаратного виправлення (Hardware Rework)", size=15, color=INK, bold=True))

    card_w, card_h = 265, 350
    y_card = 60

    # Картка 1: Різання доріжки (Trace Cutting)
    x1 = 25
    parts.append(rect(x1, y_card, card_w, card_h, fill=CARD_BG, stroke=WARN_COLOR, sw=1.5, rx=6))
    parts.append(rect(x1, y_card, card_w, 32, fill="#fee2e2", stroke=WARN_COLOR, sw=1.2, rx=6))
    parts.append(text(x1 + card_w / 2, y_card + 21, "1. Різання доріжки (Trace Cut)", size=11, color=WARN_COLOR, bold=True))

    # Схематичний рисунок різання доріжки
    diag_y = y_card + 45
    parts.append(rect(x1 + 15, diag_y, card_w - 30, 105, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    # Зелена плата
    parts.append(rect(x1 + 25, diag_y + 15, card_w - 50, 75, fill="#15803d", stroke="#166534", sw=1, rx=2))
    # Мідна доріжка з розрізом
    parts.append(rect(x1 + 40, diag_y + 46, 65, 14, fill="#d97706", stroke="#b45309", sw=1))
    parts.append(rect(x1 + 145, diag_y + 46, 65, 14, fill="#d97706", stroke="#b45309", sw=1))
    # Зона вилученої міді
    parts.append(rect(x1 + 107, diag_y + 42, 36, 22, fill="#fef2f2", stroke=WARN_COLOR, sw=1.5))
    parts.append(line(x1 + 117, diag_y + 36, x1 + 117, diag_y + 70, color=WARN_COLOR, sw=1.5))
    parts.append(line(x1 + 133, diag_y + 36, x1 + 133, diag_y + 70, color=WARN_COLOR, sw=1.5))
    parts.append(text(x1 + card_w / 2, diag_y + 96, "Подвійний різ + знятий острівець міді", size=9.5, color=WARN_COLOR, bold=True))

    tcut_desc = [
        "• Подвійний різ скальпелем #11",
        "• Вилучення міді між різами (0.5 мм)",
        "• Запобігає замиканню стружкою",
        "• Перевірка мегаомметром на розрив",
        "• Фіксація лаком або УФ-маскою"
    ]
    for i, t in enumerate(tcut_desc):
        parts.append(text(x1 + 15, y_card + 175 + i * 32, t, size=10, color=INK, anchor="start"))

    # Картка 2: Перемичка емальованим дротом (Bodge Wire)
    x2 = 305
    parts.append(rect(x2, y_card, card_w, card_h, fill=CARD_BG, stroke=EDA_COLOR, sw=1.5, rx=6))
    parts.append(rect(x2, y_card, card_w, 32, fill="#e0f2fe", stroke=EDA_COLOR, sw=1.2, rx=6))
    parts.append(text(x2 + card_w / 2, y_card + 21, "2. Перемичка (Bodge Wire)", size=11, color=EDA_COLOR, bold=True))

    # Схематичний рисунок перемички
    parts.append(rect(x2 + 15, diag_y, card_w - 30, 105, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    parts.append(rect(x2 + 25, diag_y + 15, card_w - 50, 75, fill="#15803d", stroke="#166534", sw=1, rx=2))
    # Контактні майданчики (Vias / Pads)
    parts.append(circle(x2 + 55, diag_y + 53, 10, fill="#d97706", stroke="#b45309", sw=1.2))
    parts.append(circle(x2 + 55, diag_y + 53, 4, fill="#1e293b", stroke="#0f172a", sw=1))
    parts.append(circle(x2 + 195, diag_y + 53, 10, fill="#d97706", stroke="#b45309", sw=1.2))
    parts.append(circle(x2 + 195, diag_y + 53, 4, fill="#1e293b", stroke="#0f172a", sw=1))
    # Емальований тонкий дріт з краплею УФ-маски
    parts.append(line(x2 + 55, diag_y + 53, x2 + 125, diag_y + 38, color="#dc2626", sw=2))
    parts.append(line(x2 + 125, diag_y + 38, x2 + 195, diag_y + 53, color="#dc2626", sw=2))
    # Крапля УФ-клею
    parts.append(circle(x2 + 125, diag_y + 38, 12, fill="#38bdf8", stroke="#0284c7", sw=1.5))
    parts.append(text(x2 + card_w / 2, diag_y + 96, "0.1 мм емальдріт + крапля УФ-клею", size=9.5, color=EDA_COLOR, bold=True))

    bodge_desc = [
        "• Мідний дріт ПЕВ/Kynar 30 AWG (0.1 мм)",
        "• Зачищення перехідного отвору (Via)",
        "• Пайка тонким мікрожалом (J-тип)",
        "• Фіксація УФ-маскою проти вібрацій",
        "• Виправлення RX/TX або шин даних"
    ]
    for i, t in enumerate(bodge_desc):
        parts.append(text(x2 + 15, y_card + 175 + i * 32, t, size=10, color=INK, anchor="start"))

    # Картка 3: Dead-Bug та Tombstone монтаж
    x3 = 585
    parts.append(rect(x3, y_card, card_w, card_h, fill=CARD_BG, stroke=SMT_COLOR, sw=1.5, rx=6))
    parts.append(rect(x3, y_card, card_w, 32, fill="#d1fae5", stroke=SMT_COLOR, sw=1.2, rx=6))
    parts.append(text(x3 + card_w / 2, y_card + 21, "3. «Dead Bug» та «Tombstone»", size=11, color=SMT_COLOR, bold=True))

    # Схематичний рисунок Dead-Bug / Tombstone
    parts.append(rect(x3 + 15, diag_y, card_w - 30, 105, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    parts.append(rect(x3 + 25, diag_y + 15, card_w - 50, 75, fill="#15803d", stroke="#166534", sw=1, rx=2))
    # Мікросхема догори дриґом (корпус SOIC)
    parts.append(rect(x3 + 90, diag_y + 42, 55, 30, fill="#1e293b", stroke="#0f172a", sw=1.2, rx=2))
    # Ніжки догори
    for pin_i in range(4):
        px = x3 + 97 + pin_i * 12
        parts.append(line(px, diag_y + 42, px, diag_y + 30, color="#94a3b8", sw=1.8))
        parts.append(circle(px, diag_y + 30, 2.5, fill="#dc2626", stroke="#991b1b", sw=1))
    # Резистор «на попа» (Tombstone)
    parts.append(rect(x3 + 180, diag_y + 36, 14, 28, fill="#d97706", stroke="#78350f", sw=1.2))
    parts.append(circle(x3 + 187, diag_y + 36, 3, fill="#cbd5e1", stroke="#475569", sw=1))
    parts.append(text(x3 + card_w / 2, diag_y + 96, "Чип догори лапками + резистор на попа", size=9.5, color=SMT_COLOR, bold=True))

    dead_desc = [
        "• Чип перевернутий догори ніжками",
        "• Приклеєний на каптоновий скотч",
        "• Розведення пінів дротяними джгутами",
        "• Резистор/конденсатор піднятий дибки",
        "• Порятунок інвертованого розведення IC"
    ]
    for i, t in enumerate(dead_desc):
        parts.append(text(x3 + 15, y_card + 175 + i * 32, t, size=10, color=INK, anchor="start"))

    render(out("hardware-surgery-anatomy.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_iteration_pipeline()
    fig_turnaround_comparison()
    fig_hardware_surgery_anatomy()
    print("Усі 3 фігури успішно згенеровано у ./img/")
