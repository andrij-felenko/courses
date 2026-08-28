# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Катастрофа розсинхронізації фокусу та захист SBO ───────────────
def fig_focus_ambiguity_catastrophe():
    W, H = 840, 430
    frags = []
    frags.append(text(W / 2, 25, "Розсинхронізація фокусу: пряме виконання проти двоетапного SBO",
                      size=15, bold=True))

    # Лівий блок: Пряме виконання (Direct-Operate Trap)
    frags.append(rect(20, 50, 385, 360, fill="#fdf3f2", stroke=POS, sw=1.8))
    frags.append(text(212, 75, "Пряма дія (Direct-Operate) — вразливий пульт", size=13, bold=True, color=POS))
    
    frags.append(fitbox(35, 95, 355, 60,
                        "Оператор дивиться на екран:\n«Дрон #03 сів на майданчик, вимикаю гвинти»",
                        size=11, bold=False, fill="#ffffff", stroke=POS, sw=1.0))
    
    frags.append(fitbox(35, 165, 355, 65,
                        "Прихований стан UI (Stale Focus):\nФокус пульта залишився на Дроні #01 (у повітрі на 40 м)!\nКнопка на пульті: [ ВИМКНУТИ МОТОРИ ]",
                        size=11, bold=False, fill="#feebe8", stroke=POS, sw=1.4))

    frags.append(arrow(212, 240, 212, 275, color=POS, sw=2.0))
    frags.append(text(212, 260, "Один клік без підтвердження цілі", size=10, color=POS, bold=True))

    frags.append(fitbox(35, 285, 355, 110,
                        "Катастрофічний наслідок:\n1. Пакет летить на активний ID (Дрон #01)\n2. Дрон #01 миттєво глушить двигуни в повітрі та падає\n3. Дрон #03 на землі продовжує обертати гвинти\nПовна втрата апарата через когнітивну пастку!",
                        size=11, bold=False, fill="#ffffff", stroke=POS, sw=1.2))

    # Правий блок: Захищений механізм SBO (Select-Before-Operate)
    frags.append(rect(435, 50, 385, 360, fill="#edf7ee", stroke=FIELD, sw=1.8))
    frags.append(text(627, 75, "Select-Before-Operate (SBO) — безпечний контроль", size=13, bold=True, color=FIELD))

    frags.append(fitbox(450, 95, 355, 60,
                        "Крок 1: Явний вибір (Select Target)\nОператор тисне на картку Дрона #03.\nПульт відправляє SELECT(ID: 03) та блокує контекст.",
                        size=11, bold=False, fill="#ffffff", stroke=FIELD, sw=1.0))

    frags.append(fitbox(450, 165, 355, 65,
                        "Крок 2: Візуальне блокування та зворотний зв'язок\nКнопка дії перейменовується: [ ВИМКНУТИ (ДРОН #03) ]\nЗапускається таймер вікна дії (наприклад, 6.0 с).",
                        size=11, bold=False, fill="#e1f5e6", stroke=FIELD, sw=1.4))

    frags.append(arrow(627, 240, 627, 275, color=FIELD, sw=2.0))
    frags.append(text(627, 260, "Крок 3: Виконання в межах вікна (Operate)", size=10, color=FIELD, bold=True))

    frags.append(fitbox(450, 285, 355, 110,
                        "Гарантія безпеки:\n1. Команда валідується з токеном вибору та ID: 03\n2. Дрон #03 зупиняє двигуни на землі\n3. Дрон #01 у повітрі ігнорує чужу команду\n4. Після дії селектор повертається в IDLE.",
                        size=11, bold=False, fill="#ffffff", stroke=FIELD, sw=1.2))

    render(os.path.join(OUT, 'focus-ambiguity-catastrophe.svg'), W, H, *frags)


# ── Фігура 2: Автомат станів SBO і тайм-аут знешкодження ─────────────────────
def fig_sbo_fsm_timing():
    W, H = 840, 410
    frags = []
    frags.append(text(W / 2, 25, "Скінченний автомат стану транзакції Select-Before-Operate",
                      size=15, bold=True))

    # Стани FSM
    y_states = 110
    # Стан 1: IDLE / UNARMED
    frags.append(rect(40, y_states, 190, 90, fill="#f4f6f8", stroke=INK, sw=1.8))
    frags.append(text(135, y_states + 32, "IDLE / UNARMED", size=13, bold=True, color=INK))
    frags.append(text(135, y_states + 55, "Ціль не обрана", size=11, color=MUTED))
    frags.append(text(135, y_states + 73, "Дії заблоковані", size=10, color=MUTED))

    # Стан 2: SELECTING
    frags.append(rect(320, y_states, 200, 90, fill="#fdf7e7", stroke="#d98324", sw=1.8))
    frags.append(text(420, y_states + 32, "SELECTING", size=13, bold=True, color="#d98324"))
    frags.append(text(420, y_states + 55, "Очікування Select-Ack", size=11, color=INK))
    frags.append(text(420, y_states + 73, "Перевірка зв'язку та ID", size=10, color=MUTED))

    # Стан 3: ARMED (Target Locked)
    frags.append(rect(600, y_states, 200, 90, fill="#edf7ee", stroke=FIELD, sw=2.0))
    frags.append(text(700, y_states + 32, "ARMED / LOCKED", size=13, bold=True, color=FIELD))
    frags.append(text(700, y_states + 55, "Контекст цілі активний", size=11, color=INK))
    frags.append(text(700, y_states + 73, "Таймер T_arm цокає", size=10, color=FIELD, bold=True))

    # Стан 4: EXECUTING (Нижній)
    frags.append(rect(320, 280, 200, 85, fill="#e8f0fe", stroke=NEG, sw=1.8))
    frags.append(text(420, 310, "EXECUTING / COMMITTED", size=13, bold=True, color=NEG))
    frags.append(text(420, 332, "Operate Request відправлено", size=11, color=INK))
    frags.append(text(420, 350, "Очікування статусу дії", size=10, color=MUTED))

    # Переходи (Стрілки)
    # IDLE -> SELECTING
    frags.append(arrow(230, y_states + 35, 320, y_states + 35, color=INK, sw=1.5))
    frags.append(text(275, y_states + 25, "Вибір ID", size=10, bold=True))

    # SELECTING -> ARMED
    frags.append(arrow(520, y_states + 35, 600, y_states + 35, color=FIELD, sw=1.8))
    frags.append(text(560, y_states + 25, "Ack + Token", size=10, bold=True, color=FIELD))

    # SELECTING -> IDLE (Відмова або Nack)
    frags.append(arrow(320, y_states + 65, 230, y_states + 65, color=POS, sw=1.5))
    frags.append(text(275, y_states + 80, "Nack / Err", size=10, color=POS, bold=True))

    # ARMED -> EXECUTING (Натискання кнопки дії)
    frags.append(arrow(700, y_states + 90, 700, 320, color=NEG, sw=1.8))
    frags.append(arrow(700, 320, 520, 320, color=NEG, sw=1.8))
    frags.append(text(745, 210, "Operate (ID+Token)", size=10, color=NEG, bold=True))

    # ARMED -> IDLE (Timeout / Скасування)
    frags.append(line(700, y_states, 700, 60, color=POS, sw=1.5))
    frags.append(line(700, 60, 135, 60, color=POS, sw=1.5))
    frags.append(arrow(135, 60, 135, y_states, color=POS, sw=1.5))
    frags.append(text(420, 50, "Тайм-аут вибору (T_arm вичерпано) АБО команда Cancel", size=10, color=POS, bold=True))

    # EXECUTING -> IDLE (Завершення або помилка)
    frags.append(arrow(320, 320, 135, 320, color=INK, sw=1.5))
    frags.append(arrow(135, 320, 135, y_states + 90, color=INK, sw=1.5))
    frags.append(text(225, 310, "Звіт виконання", size=10, bold=True))
    frags.append(text(225, 335, "Авто-скидання в IDLE", size=10, color=MUTED))

    render(os.path.join(OUT, 'sbo-fsm-timing.svg'), W, H, *frags)


# ── Фігура 3: Інтерфейсна ергономіка фокусу цілі ─────────────────────────────
def fig_ui_target_focus_lock():
    W, H = 840, 420
    frags = []
    frags.append(text(W / 2, 25, "Ергономіка пульта: явний фокус, динамічний текст кнопок та таймер",
                      size=15, bold=True))

    # Панель вибору апаратів зліва
    frags.append(rect(25, 55, 360, 345, fill="#f8fafc", stroke=LINE, sw=1.5))
    frags.append(text(205, 80, "Список апаратів групи (Fleet Roster)", size=13, bold=True))

    # Картка 1: Неактивний апарат
    frags.append(rect(40, 100, 330, 60, fill="#ffffff", stroke="#d1d5db", sw=1.2))
    frags.append(text(60, 125, "ALPHA-01 (ID: 0x01)", size=12, bold=True, anchor="start"))
    frags.append(text(60, 145, "Статус: У повітрі | Батарея: 82% | 42 м", size=10, color=MUTED, anchor="start"))
    frags.append(text(345, 135, "Знято фокус", size=10, color=MUTED, anchor="end"))

    # Картка 2: Активно обраний апарат (Жирна рамка, колір)
    frags.append(rect(40, 175, 330, 75, fill="#eefaf1", stroke=FIELD, sw=2.5))
    frags.append(text(60, 203, "ALPHA-02 (ID: 0x02) [ЗАБЛОКОВАНО]", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(text(60, 225, "Статус: Готовий до посадки | Батарея: 24%", size=10, color=INK, anchor="start"))
    frags.append(text(60, 240, "Токен блокування: 0x7F4A (Залишилось: 4.8 с)", size=10, color=FIELD, bold=True, anchor="start"))

    # Картка 3: Інший апарат
    frags.append(rect(40, 265, 330, 60, fill="#ffffff", stroke="#d1d5db", sw=1.2))
    frags.append(text(60, 290, "ALPHA-03 (ID: 0x03)", size=12, bold=True, anchor="start"))
    frags.append(text(60, 310, "Статус: Очікування на базі | Батарея: 99%", size=10, color=MUTED, anchor="start"))

    # Панель команд справа (Контекстні кнопки)
    frags.append(rect(415, 55, 400, 345, fill="#ffffff", stroke=FIELD, sw=2.0))
    frags.append(text(615, 80, "Панель дій [ Ціль: ALPHA-02 ]", size=14, bold=True, color=FIELD))

    # Індикатор блокування та таймер
    frags.append(rect(435, 100, 360, 45, fill="#edf7ee", stroke=FIELD, sw=1.2))
    frags.append(text(615, 120, "ФОКУС АКТИВНИЙ: ALPHA-02 (ID: 0x02)", size=12, bold=True, color=FIELD))
    frags.append(text(615, 137, "Вікно дії закриється через: [ 04.8 с ]", size=10, color=POS, bold=True))

    # Кнопки з динамічним ім'ям цілі
    frags.append(rect(435, 160, 360, 50, fill="#fdf2f0", stroke=POS, sw=1.8))
    frags.append(text(615, 185, "АВАРІЙНА ПОСАДКА [ ALPHA-02 ]", size=12, bold=True, color=POS))
    frags.append(text(615, 202, "Дія застосується ТІЛЬКИ до вузла 0x02", size=9, color=POS))

    frags.append(rect(435, 225, 360, 50, fill="#fef8e8", stroke="#d98324", sw=1.6))
    frags.append(text(615, 250, "ПОВЕРНЕННЯ ДОДОМУ [ ALPHA-02 ]", size=12, bold=True, color="#d98324"))
    frags.append(text(615, 267, "Формування маршруту RTL для ID 0x02", size=9, color="#d98324"))

    frags.append(rect(435, 290, 360, 45, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    frags.append(text(615, 317, "СКАСУВАТИ ВИБІР (DESELECT)", size=11, bold=True, color=MUTED))

    frags.append(fitbox(435, 345, 360, 45,
                        "Вимога безпеки UI:\nЖодних абстрактних кнопок без імені цілі в момент дії!",
                        size=10, bold=False, fill="#fff9db", stroke="#d98324", sw=1.2))

    render(os.path.join(OUT, 'ui-target-focus-lock.svg'), W, H, *frags)


# ── Фігура 4: Фільтрація одноадресних та широкомовних пакетів на борту ───────
def fig_unicast_vs_broadcast_filtering():
    W, H = 840, 400
    frags = []
    frags.append(text(W / 2, 25, "Конвеєр фільтрації пакетів у радіомережі на борту апарата",
                      size=15, bold=True))

    # Вхідний радіоканал
    frags.append(rect(20, 60, 160, 310, fill="#f0f4f8", stroke=NEG, sw=1.6))
    frags.append(text(100, 85, "Радіоефір / Mesh", size=13, bold=True, color=NEG))
    frags.append(fitbox(30, 110, 140, 100,
                        "Вхідний пакет:\n• Target ID\n• Command Code\n• SBO Token\n• Seq & CRC",
                        size=10, fill="#ffffff", stroke=NEG, sw=1.0))
    frags.append(fitbox(30, 225, 140, 125,
                        "Типи адресації:\n1. Unicast (0x02)\n2. Broadcast (0xFF)\n3. Group (0x80)",
                        size=10, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Рівень 1: Перевірка адреси (Target ID Matcher)
    frags.append(rect(220, 60, 175, 310, fill="#fdf8e8", stroke="#d98324", sw=1.6))
    frags.append(text(307, 85, "Рівень 1: Адреса", size=13, bold=True, color="#d98324"))
    frags.append(fitbox(230, 110, 155, 110,
                        "Перевірка Target ID:\n\nTarget == MY_ID (0x02)?\n──► ПРОПУСТИТИ\n\nTarget == 0xFF (Broadcast)?\n──► ПЕРЕВІРКА КРИТИЧНОСТІ",
                        size=10, fill="#ffffff", stroke="#d98324", sw=1.0))
    frags.append(fitbox(230, 235, 155, 115,
                        "Фільтр Broadcast:\nКритична дія (Arm/Cut/Reboot)\nна адресу 0xFF:\n──► ВІДХИЛИТИ!\n(Security Drop)",
                        size=10, fill="#feebe8", stroke=POS, sw=1.4))

    # Рівень 2: Перевірка стану SBO (SBO Security Gate)
    frags.append(rect(435, 60, 185, 310, fill="#edf7ee", stroke=FIELD, sw=1.6))
    frags.append(text(527, 85, "Рівень 2: SBO Gate", size=13, bold=True, color=FIELD))
    frags.append(fitbox(445, 110, 165, 120,
                        "Перевірка селектора:\n1. Чи борт у стані ARMED?\n2. Чи дійсний SBO Token?\n3. Чи не сплив тайм-аут T_arm?\n4. Чи збігається тип дії?",
                        size=10, fill="#ffffff", stroke=FIELD, sw=1.0))
    frags.append(fitbox(445, 245, 165, 105,
                        "Невідповідність:\n• Не обрано (Unarmed)\n• Токен застарів\n──► ВІДХИЛИТИ\n(NACK: ERR_SBO_EXPIRED)",
                        size=10, fill="#feebe8", stroke=POS, sw=1.4))

    # Рівень 3: Виконавчий модуль (Actuator Execution)
    frags.append(rect(660, 60, 160, 310, fill="#f4f6f8", stroke=INK, sw=1.8))
    frags.append(text(740, 85, "Виконання", size=13, bold=True, color=INK))
    frags.append(fitbox(670, 110, 140, 110,
                        "Безпечна дія:\n• Силовий розрив\n• Зупинка моторів\n• Зміна польотного режиму\n• Скидання селектора",
                        size=10, fill="#e8f8f0", stroke=FIELD, sw=1.4))
    frags.append(fitbox(670, 235, 140, 115,
                        "Звіт статусу:\nФормування телеметрії:\n• Action ACK\n• New State\n• Execution Timestamp",
                        size=10, fill="#ffffff", stroke=INK, sw=1.0))

    # З'єднувальні стрілки
    frags.append(arrow(180, 165, 220, 165, color=INK, sw=1.5))
    frags.append(arrow(395, 165, 435, 165, color=FIELD, sw=1.8))
    frags.append(arrow(620, 165, 660, 165, color=FIELD, sw=1.8))

    render(os.path.join(OUT, 'unicast-vs-broadcast-filtering.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_focus_ambiguity_catastrophe()
    fig_sbo_fsm_timing()
    fig_ui_target_focus_lock()
    fig_unicast_vs_broadcast_filtering()
    print("All figures generated successfully.")
