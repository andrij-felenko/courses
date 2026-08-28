# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. permissive-vs-inhibit-timeline: Допуск (Permissive) проти Заборони (Inhibit) ──
def fig_permissive_vs_inhibit():
    W, H = 780, 390
    p = []

    # Заголовок блоків
    p.append(rect(40, 50, 340, 280, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(rect(400, 50, 340, 280, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))

    p.append(text(210, 78, "Умова допуску (Permissive)", size=14, bold=True, color=NEG))
    p.append(text(570, 78, "Захисне блокування (Inhibit)", size=14, bold=True, color=POS))

    p.append(text(210, 98, "Перевірка ПЕРЕД стартом (Entry Gate)", size=11, color=MUTED, italic=True))
    p.append(text(570, 98, "Перевірка ПІД ЧАС роботи (Safety Guard)", size=11, color=MUTED, italic=True))

    # Ліва частина: Permissive
    # Блок IDLE
    b1, _, _ = textbox(110, 150, "СТАН: IDLE\n(Очікування)", size=11, fill="#ffffff", stroke=LINE, sw=1.5)
    p.append(b1)

    # Стрілка з ромбом перевірки
    p.append(arrow(170, 150, 215, 150, color=LINE, sw=1.5))
    
    # Блок умови
    p.append(rect(220, 125, 140, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    p.append(mtext(290, 143, "Всі умови = 1?\n(тиск, кришка, живлення)", size=10, color=NEG, bold=True))

    # Стрілка до RUN
    p.append(arrow(290, 175, 290, 220, color=FIELD, sw=1.8))
    p.append(text(325, 200, "ТАК (дозвіл)", size=10, color=FIELD, bold=True))

    b2, _, _ = textbox(290, 255, "СТАН: RUNNING\n(Виконання дії)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(b2)

    # Відхилення старту
    p.append(arrow(290, 125, 290, 106, color=POS, sw=1.5))
    p.append(line(290, 106, 110, 106, color=POS, sw=1.5, dash="3 2"))
    p.append(arrow(110, 106, 110, 125, color=POS, sw=1.5))
    p.append(text(200, 118, "НІ: старт заблоковано", size=10, color=POS))

    # Нижня плашка для лівої частини
    p.append(rect(55, 290, 310, 30, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(210, 310, "Захищає від: передчасного або небезпечного пуску", size=10, color=INK))

    # Права частина: Inhibit
    b3, _, _ = textbox(470, 150, "СТАН: RUNNING\n(Нормальний рух)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.5)
    p.append(b3)

    # Стрілка до моніторингу
    p.append(arrow(530, 150, 575, 150, color=LINE, sw=1.5))

    # Блок перевірки інваріанту
    p.append(rect(580, 125, 140, 50, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(mtext(650, 143, "Аварійний сигнал?\n(E-Stop, обрив, двері)", size=10, color=POS, bold=True))

    # Гілка аварії
    p.append(arrow(650, 175, 650, 220, color=POS, sw=2))
    p.append(text(690, 200, "ТАК (трип)", size=10, color=POS, bold=True))

    b4, _, _ = textbox(650, 255, "СТАН: SAFE_STOP\n(Аварійний зрив)", size=11, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(b4)

    # Петля норми
    p.append(line(720, 150, 735, 150, color=FIELD, sw=1.5))
    p.append(line(735, 150, 735, 112, color=FIELD, sw=1.5))
    p.append(line(735, 112, 470, 112, color=FIELD, sw=1.5))
    p.append(arrow(470, 112, 470, 125, color=FIELD, sw=1.5))
    p.append(text(600, 120, "НІ: продовження циклу", size=10, color=FIELD))

    # Нижня плашка для правої частини
    p.append(rect(415, 290, 310, 30, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(570, 310, "Захищає від: розвитку катастрофи під час процесу", size=10, color=INK))

    # Підсумкова плашка
    box, _, _ = textbox(W / 2, 358, "Permissive дає дозвіл на зміну стану (Gate), Inhibit примусово повертає в безпечний стан (Trip).", size=11, bold=True, fill="#fff3cd", stroke="#c07000", sw=1.5)
    p.append(box)

    render(os.path.join(OUT, "permissive-vs-inhibit-timeline.svg"), W, H, *p,
           title="Розділення ролей: умова допуску (Permissive) та захисне блокування (Inhibit)")


# ── 2. hardware-interlock-layers: Багаторівневий захист (Програма + Залізо) ──
def fig_hardware_interlock():
    W, H = 780, 390
    p = []

    # Верхній блок: Логічний рівень (Прошивка МК)
    p.append(rect(40, 50, 700, 125, fill="#f4f8ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(140, 75, "Програмний рівень (Firmware / MCU)", size=12, bold=True, color=NEG))

    # Компоненти МК
    p.append(rect(60, 95, 160, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(140, 120, "Опитування сенсорів\n(фільтр + антидребезг)", size=10, color=INK))

    p.append(arrow(220, 125, 260, 125, color=LINE, sw=1.5))

    p.append(rect(260, 95, 180, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(350, 120, "Матриця блокувань\n(FSM Interlock Logic)", size=10, color=INK))

    p.append(arrow(440, 125, 480, 125, color=LINE, sw=1.5))

    p.append(rect(480, 95, 140, 60, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(mtext(550, 120, "Керувальний вихід\n(GPIO / PWM Out)", size=10, color=FIELD, bold=True))

    p.append(rect(630, 95, 95, 60, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(mtext(677, 120, "Генератор\nPulse Heartbeat", size=9, color=POS))

    # Нижній блок: Фізичний апаратний бар'єр
    p.append(rect(40, 200, 700, 140, fill="#fff9f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(150, 225, "Апаратний рівень (Hardware Safety Loop)", size=12, bold=True, color=POS))

    # Джерело живлення актуатора
    p.append(rect(60, 245, 120, 65, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(120, 272, "Силове живлення\n(+24V / +400V)", size=10, color=INK, bold=True))

    # Послідовний ланцюг кінцевиків
    p.append(arrow(180, 275, 220, 275, color=LINE, sw=1.8))

    # Контакт дверцят
    p.append(rect(220, 250, 100, 50, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(mtext(270, 270, "Кінцевик дверцят\n(NC контакт)", size=9, color=POS))

    p.append(arrow(320, 275, 360, 275, color=LINE, sw=1.8))

    # Кнопка E-Stop
    p.append(rect(360, 250, 100, 50, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(mtext(410, 270, "Грибок E-Stop\n(NC контакт)", size=9, color=POS))

    p.append(arrow(460, 275, 500, 275, color=LINE, sw=1.8))

    # Реле безпеки / STO драйвер
    p.append(rect(500, 245, 110, 65, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(mtext(555, 272, "Реле безпеки /\nВхід STO драйвера", size=9, color=INK, bold=True))

    # Зв'язок МК виходу та актуатора через апаратне реле
    p.append(arrow(610, 275, 645, 275, color=FIELD, sw=2))

    # Виконавчий вузол (Мотор / Нагрівач)
    p.append(rect(645, 245, 85, 65, fill="#eafaf0", stroke=FIELD, sw=2, rx=4))
    p.append(mtext(687, 272, "Актуатор\n(Мотор)", size=10, color=FIELD, bold=True))

    # Вертикальні стрілки взаємодії
    # Керувальний сигнал з МК йде на силовий ключ лише при замкненому STO
    p.append(line(550, 155, 550, 245, color=MUTED, sw=1.5, dash="4 3"))
    p.append(line(677, 155, 580, 245, color=POS, sw=1.5, dash="3 2"))
    p.append(arrow(582, 240, 580, 245, color=POS, sw=1.5))

    # Пояснювальний текст
    p.append(text(W / 2, 365, "Фізичний розрив кола знеструмлює актуатор навіть при зависанні або збої прошивки.", size=11, bold=True, color=POS))

    render(os.path.join(OUT, "hardware-interlock-layers.svg"), W, H, *p,
           title="Багаторівнева архітектура: програмна логіка та незалежний апаратний контур")


# ── 3. interlock-matrix-and-deadlock: Матриця умов та виявлення глухих кутів ──
def fig_matrix_and_deadlock():
    W, H = 780, 390
    p = []

    # Ліва панель: Матриця причин і наслідків (Interlock Matrix)
    p.append(rect(35, 50, 380, 280, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(225, 75, "Матриця умов (Interlock Matrix)", size=13, bold=True, color=INK))

    # Таблиця
    top = 95
    p.append(rect(45, top, 360, 28, fill="#e2e8f0", stroke=MUTED, sw=1, rx=3))
    p.append(text(105, top + 18, "Цільова дія", size=10, bold=True))
    p.append(text(215, top + 18, "Permissive (маска)", size=10, bold=True, color=NEG))
    p.append(text(335, top + 18, "Inhibit (маска)", size=10, bold=True, color=POS))

    rows_data = [
        ("Пуск помпи",   "Тиск OK ∧ Рівень OK", "Перегрів ∨ Сухий хід"),
        ("Відкриття люка", "Тиск = 0 ∧ Стоп мотора", "Рух барабана ∨ T > 40°C"),
        ("Увімкн. ТЕНу", "Потік води ∧ Заповнено", "Люк відкритий ∨ Стійка"),
        ("Обертання",    "Замок люка ∧ Змазка OK", "E-Stop ∨ Вібрація > max"),
    ]

    for i, (act, perm, inh) in enumerate(rows_data):
        y = top + 32 + i * 36
        bg_col = "#ffffff" if i % 2 == 0 else "#f1f5f9"
        p.append(rect(45, y, 360, 32, fill=bg_col, stroke=MUTED, sw=0.8, rx=3))
        p.append(text(105, y + 20, act, size=10, bold=True))
        p.append(text(215, y + 20, perm, size=9, color=NEG))
        p.append(text(335, y + 20, inh, size=9, color=POS))

    p.append(text(225, 275, "Обчислення за 1 такт через бітові маски:", size=10, bold=True, color=INK))
    p.append(text(225, 298, "(Sensors & ReqMask) == ReqMask  &&  (Sensors & InhMask) == 0", size=9, color=NEG))

    # Права панель: Аналіз глухих кутів (Deadlock Cycle)
    p.append(rect(435, 50, 310, 280, fill="#fff9f5", stroke=POS, sw=1.2, rx=8))
    p.append(text(590, 75, "Аналіз глухих кутів (Deadlock Graph)", size=13, bold=True, color=POS))

    # Граф залежностей: Вузол А і Вузол Б
    p.append(rect(460, 115, 110, 55, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(mtext(515, 140, "Підсистема А\n(Нагнітач)", size=10, color=INK, bold=True))

    p.append(rect(615, 115, 110, 55, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(mtext(670, 140, "Підсистема Б\n(Клапан скиду)", size=10, color=INK, bold=True))

    # Стрілки циклу взаємного очікування
    # Верхня дуга: А чекає, поки Б перейде в IDLE
    p.append(arrow(545, 115, 635, 115, color=POS, sw=1.8))
    p.append(text(590, 105, "чекає: Б == IDLE", size=9, color=POS, bold=True))

    # Нижня дуга: Б чекає, поки А відкриє потік
    p.append(arrow(640, 170, 550, 170, color=POS, sw=1.8))
    p.append(text(590, 185, "чекає: А == ACTIVE", size=9, color=POS, bold=True))

    # Знак тупика
    p.append(rect(470, 210, 240, 55, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(mtext(590, 235, "ЦИКЛ БЛОКУВАННЯ (DEADLOCK)\nЖоден стан не може змінитись!", size=10, color=POS, bold=True))

    p.append(text(590, 290, "Лікування: тайм-аут деградації", size=10, bold=True, color=FIELD))
    p.append(text(590, 310, "або ієрархія пріоритетів станів", size=9, color=MUTED))

    # Підсумковий текст
    box, _, _ = textbox(W / 2, 358, "Матриця блокувань дозволяє миттєву перевірку умов, а топологічний аналіз графа усуває взаємні тупики.", size=11, bold=True, fill="#fff3cd", stroke="#c07000", sw=1.5)
    p.append(box)

    render(os.path.join(OUT, "interlock-matrix-and-deadlock.svg"), W, H, *p,
           title="Матриця блокувань та виявлення циклічних глухих кутів у системі умов")


if __name__ == "__main__":
    fig_permissive_vs_inhibit()
    fig_hardware_interlock()
    fig_matrix_and_deadlock()
    print("All figures generated successfully.")
