# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Потік ескалації примусового оновлення ───────────────────────────
def fig_forced_update_escalation_flow():
    W, H = 1000, 620
    frags = []

    frags.append(text(500, 25, "Контур ескалації примусового оновлення: від сповіщення до дедлайну",
                      size=15, bold=True, color=INK))

    # Колонка 1: Вхідний маніфест і класифікація
    frags.append(rect(40, 60, 260, 150, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    frags.append(text(170, 85, "ВХІДНИЙ МАНІФЕСТ", size=12, bold=True, color=INK))
    frags.append(text(170, 108, "• Рівень терміновості (Urgency)", size=10, color=INK))
    frags.append(text(170, 126, "• Hard Deadline (Unix Timestamp)", size=10, color=INK))
    frags.append(text(170, 144, "• Ліміт відкладень (Max Deferrals)", size=10, color=INK))
    frags.append(text(170, 162, "• Підпис Ed25519 та перелік передумов", size=10, color=MUTED))

    # Стрілка від маніфесту до класифікатора
    frags.append(arrow(170, 210, 170, 255, color=INK, sw=1.8))
    frags.append(text(225, 235, "Оцінка політики", size=9, bold=True, color=INK))

    # Класифікація терміновості
    frags.append(rect(40, 255, 260, 335, fill="#fffbf0", stroke="#d97706", sw=1.8, rx=8))
    frags.append(text(170, 280, "КЛАСИФІКАЦІЯ ТЕРМІНОВОСТІ", size=11, bold=True, color="#b45309"))

    # Гілка 1: Стандартне оновлення
    frags.append(rect(55, 300, 230, 75, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(170, 318, "STANDARD_FEATURE", size=10, bold=True, color=NEG))
    frags.append(text(170, 336, "• Безстрокове або м'яке вікно", size=9, color=INK))
    frags.append(text(170, 354, "• Пріоритет повної згоди власника", size=9, color=MUTED))

    # Гілка 2: Регуляторне / Важливе
    frags.append(rect(55, 385, 230, 85, fill="#fdf4ff", stroke="#a21caf", sw=1.2, rx=6))
    frags.append(text(170, 403, "MANDATORY_COMPLIANCE", size=10, bold=True, color="#a21caf"))
    frags.append(text(170, 421, "• Вікно відкладення: 7-14 діб", size=9, color=INK))
    frags.append(text(170, 439, "• До 5 відкладань користувачем", size=9, color=INK))
    frags.append(text(170, 457, "• Стандарти UN R156 / ENISA", size=9, color=MUTED))

    # Гілка 3: Критичний Zero-Day
    frags.append(rect(55, 480, 230, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(170, 498, "CRITICAL_ZERO_DAY", size=10, bold=True, color=POS))
    frags.append(text(170, 516, "• Жорсткий дедлайн: 2-24 години", size=9, color=INK))
    frags.append(text(170, 534, "• Максимум 1-2 відкладення", size=9, color=INK))
    frags.append(text(170, 552, "• Автоматична ескалація", size=9, color=POS))

    # Колонка 2: Фази взаємодії та відкладення (Центр)
    frags.append(rect(340, 60, 320, 530, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    frags.append(text(500, 85, "ДИНАМІКА ВЗАЄМОДІЇ З ОПЕРАТОРОМ", size=12, bold=True, color=INK))

    # Фаза 1: Інформаційне сповіщення
    frags.append(rect(355, 105, 290, 80, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(500, 125, "Фаза 1: Інформаційне сповіщення", size=10, bold=True, color=FIELD))
    frags.append(text(500, 145, "Діалог: «Доступне оновлення системи»", size=9, color=INK))
    frags.append(text(500, 163, "Кнопки: [Встановити зараз] / [Відкласти на 4 год]", size=9, color=MUTED))

    frags.append(arrow(500, 185, 500, 210, color=INK, sw=1.5))

    # Фаза 2: Попередження зі зворотним відліком
    frags.append(rect(355, 210, 290, 95, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=6))
    frags.append(text(500, 230, "Фаза 2: Попередження з таймером", size=10, bold=True, color="#b45309"))
    frags.append(text(500, 250, "Вичерпано 80% часу або ліміт відмов", size=9, color=INK))
    frags.append(text(500, 268, "Банер у інтерфейсі + звукове сповіщення", size=9, color=INK))
    frags.append(text(500, 286, "Відлік: «Оновлення відбудеться через 30 хв»", size=9, bold=True, color="#b45309"))

    frags.append(arrow(500, 305, 500, 330, color=INK, sw=1.5))

    # Фаза 3: Вичерпання дедлайну (Hard Deadline)
    frags.append(rect(355, 330, 290, 105, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(500, 350, "Фаза 3: Настання жорсткого дедлайну", size=10, bold=True, color=POS))
    frags.append(text(500, 370, "Hard Deadline вичерпано (Time >= T_deadline)", size=9, bold=True, color=INK))
    frags.append(text(500, 388, "Блокування кнопки відхилення (Snooze Disabled)", size=9, color=POS))
    frags.append(text(500, 406, "Запит на вхід у режим підготовки до перезапуску", size=9, color=INK))
    frags.append(text(500, 424, "Перехід до арбітражу фізичної безпеки", size=9, italic=True, color=MUTED))

    frags.append(arrow(500, 435, 500, 460, color=POS, sw=1.8))

    # Фаза 4: Ескалація до примусового виконання
    frags.append(rect(355, 460, 290, 115, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    frags.append(text(500, 480, "Фаза 4: Примусова ініціалізація", size=10, bold=True, color=POS))
    frags.append(text(500, 500, "Встановлення прапорця FORCE_PENDING", size=9, color=INK))
    frags.append(text(500, 518, "Заборона нових призначень та місій", size=9, color=INK))
    frags.append(text(500, 536, "Ізоляція інтерфейсу від ручного скасування", size=9, color=POS))
    frags.append(text(500, 554, "Передача керування диспетчеру Safe Window", size=9, bold=True, color=INK))

    # Колонка 3: Безпечне виконання та арбітраж (Праворуч)
    frags.append(rect(700, 60, 260, 530, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    frags.append(text(830, 85, "БЕЗПЕЧНЕ ВИКОНАННЯ", size=12, bold=True, color=INK))

    # Блок перевірки передумов
    frags.append(rect(715, 110, 230, 130, fill="#eff6ff", stroke=NEG, sw=1.4, rx=6))
    frags.append(text(830, 130, "ШЛЮЗ БЕЗПЕКИ (INTERLOCKS)", size=10, bold=True, color=NEG))
    frags.append(text(830, 150, "• Швидкість руху = 0 км/год", size=9, color=INK))
    frags.append(text(830, 168, "• Стоянкове гальмо = АКТИВНЕ", size=9, color=INK))
    frags.append(text(830, 186, "• Заряд АКБ >= 50% або 220V", size=9, color=INK))
    frags.append(text(830, 204, "• Актуатори знеструмлені", size=9, color=INK))
    frags.append(text(830, 222, "• Drain фонових I/O операцій", size=9, color=MUTED))

    # Стрілка вниз до рішення
    frags.append(arrow(830, 240, 830, 280, color=INK, sw=1.5))

    # Розгалуження стану
    frags.append(rect(715, 280, 230, 110, fill="#fffbeb", stroke="#f59e0b", sw=1.4, rx=6))
    frags.append(text(830, 300, "АРБІТРАЖ СТАНУ", size=10, bold=True, color="#b45309"))
    frags.append(text(830, 320, "Умови не виконані? (Рух / Низький заряд)", size=9, color=INK))
    frags.append(text(830, 338, "→ Відкладення до зупинки (Safety Hold)", size=9, bold=True, color=POS))
    frags.append(text(830, 356, "→ Watchdog безпечного очікування", size=9, color=MUTED))
    frags.append(text(830, 374, "→ Аварійна зупинка місії (Safe Fallback)", size=9, color=POS))

    # Стрілка вниз до успішного виконання
    frags.append(arrow(830, 390, 830, 430, color=FIELD, sw=1.8))
    frags.append(text(895, 410, "Інтерлоки OK", size=9, bold=True, color=FIELD))

    # Фінальний блок: Активація
    frags.append(rect(715, 430, 230, 145, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(830, 450, "АКТИВАЦІЯ ТА РЕСТАРТ", size=10, bold=True, color=FIELD))
    frags.append(text(830, 470, "• Скидання кешів ФС (sync)", size=9, color=INK))
    frags.append(text(830, 488, "• Атомарне перемикання A/B слота", size=9, color=INK))
    frags.append(text(830, 506, "• Увімкнення апаратного Watchdog", size=9, color=INK))
    frags.append(text(830, 524, "• Перезавантаження ядра Linux", size=9, color=INK))
    frags.append(text(830, 542, "• Підтвердження працездатності", size=9, bold=True, color=FIELD))

    # Горизонтальні з'єднувальні стрілки
    frags.append(arrow(300, 515, 355, 515, color=POS, sw=1.8))
    frags.append(arrow(645, 515, 715, 180, color=POS, sw=1.8))

    render(os.path.join(IMG, 'forced-update-escalation-flow.svg'), W, H, *frags,
           title="Потік ескалації примусового оновлення та взаємодії з оператором")


# ── Фігура 2: Перевірка безпечного стану (Safe Execution Window Check) ────────
def fig_safe_execution_window_check():
    W, H = 1000, 580
    frags = []

    frags.append(text(500, 25, "Шлюз фізичної безпеки (Safe Execution Window Interlocks)",
                      size=15, bold=True, color=INK))

    # Лівий блок: Джерела сенсорних даних та статусів
    frags.append(rect(40, 60, 280, 490, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    frags.append(text(180, 85, "ТЕЛЕМЕТРІЯ ТА ДАТЧИКИ БЕЗПЕКИ", size=11, bold=True, color=INK))

    # Сенсор 1: Одометрія та гіроскоп
    frags.append(rect(55, 105, 250, 70, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(180, 125, "1. Кінематика і рух", size=10, bold=True, color=NEG))
    frags.append(text(180, 143, "• Швидкість коліс: 0.00 м/с", size=9, color=INK))
    frags.append(text(180, 161, "• IMU: відсутність лінійного прискорення", size=9, color=MUTED))

    # Сенсор 2: Гальмівна система та трансмісія
    frags.append(rect(55, 185, 250, 70, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(180, 205, "2. Гальма та положення", size=10, bold=True, color=NEG))
    frags.append(text(180, 223, "• Стоянкове гальмо: ЗАБЛОКОВАНО", size=9, color=INK))
    frags.append(text(180, 241, "• Передача: селектор у положенні «PARK»", size=9, color=MUTED))

    # Сенсор 3: Живлення та АКБ
    frags.append(rect(55, 265, 250, 70, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(180, 285, "3. Підсистема живлення (BMS)", size=10, bold=True, color=NEG))
    frags.append(text(180, 303, "• Рівень заряду АКБ >= 50%", size=9, color=INK))
    frags.append(text(180, 321, "• Зовнішнє живлення: ПІДКЛЮЧЕНО / СТАБІЛЬНЕ", size=9, color=MUTED))

    # Сенсор 4: Силові актуатори та реле
    frags.append(rect(55, 345, 250, 70, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(180, 365, "4. Силові актуатори", size=10, bold=True, color=NEG))
    frags.append(text(180, 383, "• Струм сервоприводів: 0.0 А", size=9, color=INK))
    frags.append(text(180, 401, "• Силове реле високої напруги: ВІДКЛЮЧЕНО", size=9, color=MUTED))

    # Сенсор 5: Системний I/O стан
    frags.append(rect(55, 425, 250, 70, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(180, 445, "5. Стан файлової системи та СУБД", size=10, bold=True, color=NEG))
    frags.append(text(180, 463, "• Відсутність відкритих транзакцій SQLite", size=9, color=INK))
    frags.append(text(180, 481, "• Скидання сторінок пам'яті (sync completed)", size=9, color=MUTED))

    frags.append(text(180, 520, "Опитування шини CAN / I2C / sysfs кожні 500 мс", size=9, italic=True, color=MUTED))

    # Центральний блок: Матриця логічного арбітражу (AND-Gate Aggregator)
    frags.append(rect(360, 140, 280, 330, fill="#fffbf0", stroke="#d97706", sw=2.0, rx=8))
    frags.append(text(500, 165, "МАТРИЦЯ АРБІТРАЖУ БЕЗПЕКИ", size=12, bold=True, color="#b45309"))
    frags.append(text(500, 183, "Логічна кон'юнкція умов (Bitwise AND)", size=10, italic=True, color=MUTED))

    frags.append(line(375, 195, 625, 195, color="#d97706", sw=1.0))

    frags.append(text(500, 215, "Інтерлок 1: (Speed == 0) [OK]", size=10, bold=True, color=FIELD))
    frags.append(text(500, 240, "Інтерлок 2: (Brake == ENGAGED) [OK]", size=10, bold=True, color=FIELD))
    frags.append(text(500, 265, "Інтерлок 3: (Battery >= 50%) [OK]", size=10, bold=True, color=FIELD))
    frags.append(text(500, 290, "Інтерлок 4: (Actuators == OFF) [OK]", size=10, bold=True, color=FIELD))
    frags.append(text(500, 315, "Інтерлок 5: (FS_Drain == IDLE) [OK]", size=10, bold=True, color=FIELD))

    frags.append(line(375, 330, 625, 330, color="#d97706", sw=1.0))

    frags.append(text(500, 355, "Результат: Mask == INTERLOCKS_ALL_OK", size=10, bold=True, color=INK))
    frags.append(text(500, 380, "Час утримання безпечного стану:", size=9, color=MUTED))
    frags.append(text(500, 400, "T_hold >= 5.0 с без порушень", size=11, bold=True, color="#b45309"))
    frags.append(text(500, 425, "Watchdog очікування: 1800 с максимум", size=9, italic=True, color=MUTED))
    frags.append(text(500, 445, "Вихід за межі таймауту → Safe Abort", size=9, color=POS))

    # Стрілки від сенсорів до арбітражу
    frags.append(arrow(305, 140, 360, 215, color=NEG, sw=1.4))
    frags.append(arrow(305, 220, 360, 240, color=NEG, sw=1.4))
    frags.append(arrow(305, 300, 360, 265, color=NEG, sw=1.4))
    frags.append(arrow(305, 380, 360, 290, color=NEG, sw=1.4))
    frags.append(arrow(305, 460, 360, 315, color=NEG, sw=1.4))

    # Правий блок 1: Успішна гілка (Дозвіл на оновлення)
    frags.append(rect(680, 80, 280, 180, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(820, 105, "ДОЗВІЛ НА ПЕРЕЗАВАНТАЖЕННЯ", size=11, bold=True, color=FIELD))
    frags.append(text(820, 128, "Статус: SAFE_WINDOW_GRANTED", size=10, bold=True, color=FIELD))
    frags.append(text(820, 150, "1. Захоплення виключного Safety Lock", size=9, color=INK))
    frags.append(text(820, 170, "2. Фіксація стану завантажувача U-Boot", size=9, color=INK))
    frags.append(text(820, 190, "3. Атомарне перемикання розділу boot", size=9, color=INK))
    frags.append(text(820, 210, "4. Виклик reboot(RB_AUTOBOOT)", size=9, bold=True, color=INK))
    frags.append(text(820, 230, "Апаратний перезапуск за 800 мс", size=9, italic=True, color=MUTED))

    # Правий блок 2: Блокувальна гілка (Порушення умов безпеки)
    frags.append(rect(680, 320, 280, 210, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    frags.append(text(820, 345, "ВІДХИЛЕННЯ / ОЧІКУВАННЯ БЕЗПЕКИ", size=11, bold=True, color=POS))
    frags.append(text(820, 368, "Статус: INTERLOCK_VIOLATION", size=10, bold=True, color=POS))
    frags.append(text(820, 390, "Причина: виявлено рух / низький заряд", size=9, color=INK))
    frags.append(text(820, 410, "• Блокування виклику reboot()", size=9, bold=True, color=POS))
    frags.append(text(820, 430, "• Надсилання тривоги на OTA-сервер", size=9, color=INK))
    frags.append(text(820, 450, "• Увімкнення лічильника спроб (Retry Count)", size=9, color=INK))
    frags.append(text(820, 470, "• Якщо дедлайн вичерпано → Запит", size=9, color=INK))
    frags.append(text(820, 490, "  на безпечну парковку обладнання", size=9, bold=True, color=POS))
    frags.append(text(820, 510, "• Пріоритет: збереження життя та майна", size=9, italic=True, color=MUTED))

    # Стрілки з арбітражу на виходи
    frags.append(arrow(640, 220, 680, 160, color=FIELD, sw=1.8))
    frags.append(text(655, 175, "TRUE", size=9, bold=True, color=FIELD))

    frags.append(arrow(640, 380, 680, 410, color=POS, sw=1.8))
    frags.append(text(655, 420, "FALSE", size=9, bold=True, color=POS))

    render(os.path.join(IMG, 'safe-execution-window-check.svg'), W, H, *frags,
           title="Перевірка шлюзу фізичної безпеки перед перезавантаженням")


if __name__ == '__main__':
    fig_forced_update_escalation_flow()
    fig_safe_execution_window_check()
    print("OK: generated 2 figures in", IMG)
