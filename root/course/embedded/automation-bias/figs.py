#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор фігур для теми automation-bias (Автоматизаційна упередженість)."""

import sys
import os

# Підключення svgkit із кореневої теки scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, text, mtext, line, arrow, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_automation_bias_feedback_loop():
    """Фігура 1: Петля деградації пильності та автоматизаційної упередженості."""
    w, h = 880, 520
    frags = []

    # Фон та заголовок секцій
    frags.append(rect(20, 50, 840, 440, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=8))

    # Вузли петлі
    b1, _, _ = textbox(
        440, 100,
        "1. Уявна бездоганність автоматики\n(Тривалий безаварійний період та стабільні звіти системи)",
        size=13, pad=12, fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True
    )
    frags.append(b1)

    b2, _, _ = textbox(
        700, 220,
        "2. Когнітивне розвантаження\n(Автоматика сприймається як авторитет;\nделегування рішень софту)",
        size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5, bold=False
    )
    frags.append(b2)

    b3, _, _ = textbox(
        700, 370,
        "3. Зниження пильності (Vigilance Decrement)\n(Пропуск звірки з первинними датчиками;\nігнорування дрібних аномалій)",
        size=12, pad=10, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, bold=False
    )
    frags.append(b3)

    b4, _, _ = textbox(
        440, 450,
        "4. Помилки упущення (Omission) та дії (Commission)\n(Непомічена тиха відмова або сліпе виконання хибних директив)",
        size=13, pad=12, fill="#fdecea", stroke=POS, sw=1.8, bold=True
    )
    frags.append(b4)

    b5, _, _ = textbox(
        180, 290,
        "5. Атрофія навичок (Out-of-the-Loop)\n(Втрата ментальної моделі процесу;\nнеготовність до ручного перехоплення)",
        size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5, bold=False
    )
    frags.append(b5)

    # З'єднувальні стрілки петлі
    frags.append(arrow(600, 100, 700, 175, color=LINE, sw=1.8))
    frags.append(arrow(700, 270, 700, 320, color=LINE, sw=1.8))
    frags.append(arrow(700, 420, 600, 450, color=POS, sw=2.0))
    frags.append(arrow(280, 450, 180, 345, color=POS, sw=2.0))
    frags.append(arrow(180, 235, 300, 115, color=NEG, sw=1.8))

    # Центральне пояснення
    c_box, _, _ = textbox(
        440, 270,
        "Самопосилювана петля:\nЧим довше система мовчить,\nтим менше оператор перевіряє фізику",
        size=12, pad=10, fill="#ffffff", stroke="#95a5a6", sw=1.2
    )
    frags.append(c_box)

    render(
        os.path.join(IMG_DIR, "automation-bias-feedback-loop.svg"),
        w, h, *frags,
        title="Петля деградації пильності та автоматизаційної упередженості"
    )


def fig_isa_18_2_alarm_state_machine():
    """Фігура 2: Автомат станів життєвого циклу тривоги за стандартом ISA-18.2 / IEC 62682."""
    w, h = 920, 540
    frags = []

    # Фонова рамка
    frags.append(rect(15, 45, 890, 475, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=8))

    # Стани
    s_norm, _, _ = textbox(140, 140, "NORMAL\n(Нормальний стан)", size=13, pad=12, fill="#e8f8f5", stroke=FIELD, sw=2.0, bold=True)
    s_unack, _, _ = textbox(500, 140, "UNACK ALARM\n(Непідтверджена тривога)", size=13, pad=12, fill="#fdecea", stroke=POS, sw=2.0, bold=True)
    s_ack, _, _ = textbox(800, 280, "ACK ALARM\n(Підтверджена активна тривога)", size=13, pad=12, fill="#fef9e7", stroke="#d4ac0d", sw=2.0, bold=True)
    s_rtn, _, _ = textbox(500, 420, "RTN UNACK\n(Повернуто в норму без квитування)", size=13, pad=12, fill="#edf2f7", stroke="#4a5568", sw=1.8, bold=True)
    s_shelv, _, _ = textbox(140, 320, "SHELVED\n(Тимчасово відкладена)", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5, bold=False)
    s_supp, _, _ = textbox(140, 440, "SUPPRESSED\n(Пригнічена логікою режиму)", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5, bold=False)

    frags.extend([s_norm, s_unack, s_ack, s_rtn, s_shelv, s_supp])

    # Переходи
    # Normal -> Unack Alarm
    frags.append(arrow(240, 130, 380, 130, color=POS, sw=1.8))
    frags.append(text(310, 115, "Вихід за межі (Trip)", size=10, color=POS, bold=True))

    # Unack Alarm -> Ack Alarm
    frags.append(arrow(620, 140, 750, 230, color=LINE, sw=1.8))
    frags.append(text(710, 170, "Квитування (Ack)", size=10, color=INK, bold=True))

    # Ack Alarm -> Normal
    frags.append(arrow(750, 310, 230, 160, color=FIELD, sw=1.8))
    frags.append(text(460, 235, "Нормалізація сигналу (Clear)", size=10, color=FIELD, bold=True))

    # Unack Alarm -> RTN Unack
    frags.append(arrow(500, 185, 500, 370, color=MUTED, sw=1.8))
    frags.append(text(510, 280, "Нормалізація до квитування", size=10, color=MUTED, bold=False, anchor="start"))

    # RTN Unack -> Normal
    frags.append(arrow(400, 420, 190, 185, color=FIELD, sw=1.8))
    frags.append(text(270, 350, "Квитування скидання (Ack)", size=10, color=FIELD, bold=True))

    # Normal <-> Shelved
    frags.append(arrow(140, 185, 140, 275, color=MUTED, sw=1.5))
    frags.append(arrow(110, 275, 110, 185, color=MUTED, sw=1.5))
    frags.append(text(125, 235, "Відкласти / Відновити", size=9, color=MUTED))

    # Normal <-> Suppressed
    frags.append(line(70, 140, 40, 140, color=LINE, sw=1.2))
    frags.append(line(40, 140, 40, 440, color=LINE, sw=1.2))
    frags.append(arrow(40, 440, 50, 440, color=LINE, sw=1.2))
    frags.append(text(45, 290, "Зміна стану установки", size=9, color=MUTED, anchor="start"))

    render(
        os.path.join(IMG_DIR, "isa-18-2-alarm-state-machine.svg"),
        w, h, *frags,
        title="Автомат станів життєвого циклу тривоги (ISA-18.2 / IEC 62682)"
    )


def fig_situation_awareness_levels():
    """Фігура 3: Три рівні ситуаційної обізнаності (SA, Endsley) та точки відмови."""
    w, h = 900, 500
    frags = []

    frags.append(rect(15, 45, 870, 435, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=8))

    # 3 Колонки рівнів SA
    col_w = 260
    c1_x, c2_x, c3_x = 40, 320, 600

    # Рівень 1
    frags.append(rect(c1_x, 90, col_w, 280, fill="#f4f6f8", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(c1_x + col_w / 2, 120, "Рівень 1: Сприйняття", size=14, color=INK, bold=True))
    frags.append(text(c1_x + col_w / 2, 140, "(Perception)", size=12, color=MUTED, italic=True))
    t1 = ("• Первинні сенсорні дані\n"
          "• Індикатори панелі приладів\n"
          "• Статус лінка та систем\n"
          "• Зчитування числових значень")
    frags.append(mtext(c1_x + 15, 175, t1, size=11, color=INK, anchor="start", lh=1.4))

    # Вразливість Р1
    v1, _, _ = textbox(c1_x + col_w / 2, 420, "Вразливість до автоматизації:\nСенсорне перевантаження,\nпропуск дрейфу сигналів", size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.2)
    frags.append(v1)
    frags.append(arrow(c1_x + col_w / 2, 370, c1_x + col_w / 2, 390, color=POS, sw=1.5))

    # Рівень 2
    frags.append(rect(c2_x, 90, col_w, 280, fill="#f4f6f8", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(c2_x + col_w / 2, 120, "Рівень 2: Осмислення", size=14, color=INK, bold=True))
    frags.append(text(c2_x + col_w / 2, 140, "(Comprehension)", size=12, color=MUTED, italic=True))
    t2 = ("• Інтеграція показів у модель\n"
          "• Розуміння фізики процесу\n"
          "• Виявлення суперечностей датчиків\n"
          "• Оцінка поточного режиму роботи")
    frags.append(mtext(c2_x + 15, 175, t2, size=11, color=INK, anchor="start", lh=1.4))

    # Вразливість Р2
    v2, _, _ = textbox(c2_x + col_w / 2, 420, "Вразливість до автоматизації:\nКогнітивне тунелювання,\nсліпа довіра до зелених плашок", size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.2)
    frags.append(v2)
    frags.append(arrow(c2_x + col_w / 2, 370, c2_x + col_w / 2, 390, color=POS, sw=1.5))

    # Рівень 3
    frags.append(rect(c3_x, 90, col_w, 280, fill="#f4f6f8", stroke="#bdc3c7", sw=1.5, rx=6))
    frags.append(text(c3_x + col_w / 2, 120, "Рівень 3: Прогнозування", size=14, color=INK, bold=True))
    frags.append(text(c3_x + col_w / 2, 140, "(Projection)", size=12, color=MUTED, italic=True))
    t3 = ("• Екстраполяція траєкторії\n"
          "• Оцінка залишку часу та енергії\n"
          "• Передбачення розвитку аварії\n"
          "• Планування ручного втручання")
    frags.append(mtext(c3_x + 15, 175, t3, size=11, color=INK, anchor="start", lh=1.4))

    # Вразливість Р3
    v3, _, _ = textbox(c3_x + col_w / 2, 420, "Вразливість до автоматизації:\nФеномен Out-of-the-Loop,\nнеготовність до збою алгоритму", size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.2)
    frags.append(v3)
    frags.append(arrow(c3_x + col_w / 2, 370, c3_x + col_w / 2, 390, color=POS, sw=1.5))

    # Стрілки між рівнями
    frags.append(arrow(c1_x + col_w, 220, c2_x, 220, color=LINE, sw=2.0))
    frags.append(arrow(c2_x + col_w, 220, c3_x, 220, color=LINE, sw=2.0))

    render(
        os.path.join(IMG_DIR, "situation-awareness-levels.svg"),
        w, h, *frags,
        title="Три рівні ситуаційної обізнаності (Endsley) та точки відмови автоматизації"
    )


def fig_hmi_confidence_display():
    """Фігура 4: Візуалізація даних: оманлива надточність проти довірчих інтервалів."""
    w, h = 900, 460
    frags = []

    frags.append(rect(15, 45, 870, 395, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=8))

    panel_w = 400
    p1_x, p2_x = 35, 465

    # Ліва панель: Поганий дизайн
    frags.append(rect(p1_x, 80, panel_w, 335, fill="#fff5f5", stroke="#feb2b2", sw=1.5, rx=6))
    frags.append(text(p1_x + panel_w / 2, 110, "Оманлива надточність (Naive HMI)", size=14, color=POS, bold=True))

    # Елементи лівої панелі
    e1, _, _ = textbox(p1_x + panel_w / 2, 165, "Напруга батареї:\n14.285714 V\n(Шум АЦП 0.4 В приховано за 6 знаками)", size=12, pad=8, fill="#ffffff", stroke="#cbd5e0", sw=1.0)
    e2, _, _ = textbox(p1_x + panel_w / 2, 255, "GPS Позиція:\nLAT: 50.450100 N, LON: 30.523400 E\nСтатус: [OK] ЗЕЛЕНИЙ\n(HDOP=4.8 та спуфінг не відображені)", size=12, pad=8, fill="#ffffff", stroke="#cbd5e0", sw=1.0)
    e3, _, _ = textbox(p1_x + panel_w / 2, 345, "Наслідок: Хибне відчуття безпеки,\nпропуск деградації сенсорів", size=12, pad=8, fill="#fdecea", stroke=POS, sw=1.5, bold=True)

    frags.extend([e1, e2, e3])

    # Права панель: Ергономічний дизайн
    frags.append(rect(p2_x, 80, panel_w, 335, fill="#f0fff4", stroke="#9ae6b4", sw=1.5, rx=6))
    frags.append(text(p2_x + panel_w / 2, 110, "Калібрована довіра (ISA-101 / IEC)", size=14, color=FIELD, bold=True))

    # Елементи правої панелі
    r1, _, _ = textbox(p2_x + panel_w / 2, 165, "Напруга батареї:\n14.3 ± 0.3 V  [Довірчий інтервал 95%]\nЯкість сигналу: В нормі (SNR 32 dB)", size=12, pad=8, fill="#ffffff", stroke="#cbd5e0", sw=1.0)
    r2, _, _ = textbox(p2_x + panel_w / 2, 255, "Навігація (Фільтр EKF):\nРадіус невизначеності: σ = ±14.5 м\nДостовірність: 64% [AMBER УВАГА]\n(Розбіжність GNSS та одометрії!)", size=12, pad=8, fill="#ffffff", stroke="#cbd5e0", sw=1.0)
    r3, _, _ = textbox(p2_x + panel_w / 2, 345, "Наслідок: Оператор бачить сумнівність\nданих і своєчасно перевіряє літак", size=12, pad=8, fill="#e8f8f5", stroke=FIELD, sw=1.5, bold=True)

    frags.extend([r1, r2, r3])

    render(
        os.path.join(IMG_DIR, "hmi-confidence-display.svg"),
        w, h, *frags,
        title="Візуалізація сенсорних даних: надточність проти довірчих інтервалів"
    )


if __name__ == "__main__":
    fig_automation_bias_feedback_loop()
    fig_isa_18_2_alarm_state_machine()
    fig_situation_awareness_levels()
    fig_hmi_confidence_display()
    print("Всі фігури згенеровано успішно.")
