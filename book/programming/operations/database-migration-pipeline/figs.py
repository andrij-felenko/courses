# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Конвеєр міграцій баз даних у CI/CD ──────────────────────────────
def fig_migration_pipeline_lifecycle():
    W, H = 1000, 560
    frags = []

    # Заголовок
    frags.append(text(500, 25, "Архітектура та фази конвеєра міграцій бази даних у CI/CD",
                      size=15, bold=True, color=INK))

    # Секція 1: CI Linting & Static Analysis
    c1 = rect(30, 60, 280, 200, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8)
    frags.append(c1)
    frags.append(text(170, 85, "1. Статичний аналіз у CI", size=13, bold=True, color=NEG))
    
    b1_1, _, _ = textbox(170, 120, "Парсинг AST та SQL-лінтинг\n(Squawk / Atlas / Custom Rules)",
                         size=10, bold=True, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b1_2, _, _ = textbox(170, 175, "Перевірка блокувань:\n• Заборона важких локів (AccessExclusive)\n• Обов'язковий lock_timeout і defaults",
                         size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b1_3, _, _ = textbox(170, 235, "Результат: Блокування PR при ризику простою",
                         size=9, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.0, pad=5)
    frags.extend([b1_1, b1_2, b1_3])

    # Стрілка 1 -> 2
    frags.append(arrow(310, 160, 360, 160, color=INK, sw=2.0))

    # Секція 2: Тіньове тестування на клоні
    c2 = rect(360, 60, 280, 200, fill="#f8fafc", stroke="#d97706", sw=1.5, rx=8)
    frags.append(c2)
    frags.append(text(500, 85, "2. Тестування на тіньовій БД", size=13, bold=True, color="#d97706"))

    b2_1, _, _ = textbox(500, 120, "Ефемерний клон продакшн-схеми\n(Анонімізований снепшот або Thin Clone)",
                         size=10, bold=True, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b2_2, _, _ = textbox(500, 175, "Прогін міграції (Dry-Run):\n• Вимірювання часу виконання DDL\n• Перевірка ідемпотентності та відкату",
                         size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b2_3, _, _ = textbox(500, 235, "Результат: Верифікація безпеки схеми",
                         size=9, bold=True, fill="#fff9e6", stroke="#d97706", sw=1.0, pad=5)
    frags.extend([b2_1, b2_2, b2_3])

    # Стрілка 2 -> 3
    frags.append(arrow(640, 160, 690, 160, color=INK, sw=2.0))

    # Секція 3: Пре-деплой виконання міграцій (CD Runner)
    c3 = rect(690, 60, 280, 200, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8)
    frags.append(c3)
    frags.append(text(830, 85, "3. Пре-деплой запуск (CD)", size=13, bold=True, color=FIELD))

    b3_1, _, _ = textbox(830, 120, "Ізольований K8s Job / Runner\n(Відокремлений від запуску подів сервісу)",
                         size=10, bold=True, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b3_2, _, _ = textbox(830, 175, "Захоплення Advisory Lock:\n• Захист від паралельного виконання\n• Транзакційне оновлення schema_migrations",
                         size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b3_3, _, _ = textbox(830, 235, "Результат: Схема v2 готова ДО коду v2",
                         size=9, bold=True, fill="#e8f8ed", stroke=FIELD, sw=1.0, pad=5)
    frags.extend([b3_1, b3_2, b3_3])

    # Стрілка вниз 3 -> 4
    frags.append(arrow(830, 260, 830, 310, color=INK, sw=2.0))

    # Нижня частина: Розгортання додатку та фонові задачі
    c4 = rect(480, 310, 490, 210, fill="#faf5ff", stroke="#7c3aed", sw=1.5, rx=8)
    frags.append(c4)
    frags.append(text(725, 335, "4. Розкатка коду додатка (Rolling / Blue-Green)", size=13, bold=True, color="#7c3aed"))

    b4_1, _, _ = textbox(725, 375, "Одночасна робота подів v1 та v2 зі схемою v2\n(Сувора зворотна сумісність: v1 ігнорує нові поля, v2 заповнює обидва)",
                         size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b4_2, _, _ = textbox(725, 430, "Повний перехід трафіку на v2\n(Усі поди v1 успішно виведені з експлуатації)",
                         size=10, bold=True, fill="#ffffff", stroke=FIELD, sw=1.0, pad=6)
    b4_3, _, _ = textbox(725, 485, "Гарантія: Нульовий простій для клієнтів (Zero Downtime)",
                         size=10, bold=True, fill="#ede9fe", stroke="#7c3aed", sw=1.0, pad=5)
    frags.extend([b4_1, b4_2, b4_3])

    # Стрілка вліво 4 -> 5
    frags.append(arrow(480, 415, 370, 415, color=INK, sw=2.0))

    # Секція 5: Пост-деплой асинхронний бекфіл
    c5 = rect(30, 310, 340, 210, fill="#f8fafc", stroke=INK, sw=1.5, rx=8)
    frags.append(c5)
    frags.append(text(200, 335, "5. Пост-деплой та асинхронний бекфіл", size=13, bold=True, color=INK))

    b5_1, _, _ = textbox(200, 375, "Фонові воркери міграції даних:\n• Чанковий бекфіл історичних рядків\n• Адаптивний тротлінг за лагом реплік",
                         size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b5_2, _, _ = textbox(200, 430, "Фінальне прибирання (Contract):\n• Видалення старих колонок у наступному релізі\n• Очищення тригерів та тимчасових таблиць",
                         size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    b5_3, _, _ = textbox(200, 485, "Стан: Чиста нова схема без артефактів",
                         size=9, bold=True, fill="#f1f5f9", stroke=INK, sw=1.0, pad=5)
    frags.extend([b5_1, b5_2, b5_3])

    render(os.path.join(IMG, 'migration-pipeline-lifecycle.svg'), W, H, *frags)


# ── Фігура 2: Expand / Contract (Патерн паралельних змін) ──────────────────────
def fig_expand_contract_phases():
    W, H = 1040, 540
    frags = []

    frags.append(text(520, 25, "Патерн паралельних змін (Expand / Contract) для безпечної еволюції схеми",
                      size=15, bold=True, color=INK))

    phases = [
        ("Фаза 1: РОЗШИРЕННЯ (Expand)", "#eff6ff", NEG, [
            ("DDL: Додавання нової структури", True),
            ("• Додавання колонки (NULL/DEFAULT)", False),
            ("• Створення нової таблиці / індексу", False),
            ("Код додатку: v1 (старий)", True),
            ("• Читання: Стара колонка", False),
            ("• Запис: Стара колонка", False),
            ("Стан: Схема готова, v1 працює", "status")
        ]),
        ("Фаза 2: ПОДВІЙНИЙ ЗАПИС (Dual Write)", "#f0fdf4", FIELD, [
            ("Реліз коду v1.1", True),
            ("• Запис: Стара ТА Нова колонки", False),
            ("• Читання: Стара колонка", False),
            ("Асинхронний бекфіл:", True),
            ("• Фоновий перенос старих записів", False),
            ("• Синхронізація історичних даних", False),
            ("Стан: Дані в обох форматах", "status")
        ]),
        ("Фаза 3: ПЕРЕМИКАННЯ ЧИТАННЯ (Switch)", "#fff9e6", "#d97706", [
            ("Реліз коду v1.2", True),
            ("• Читання: НОВА колонка", False),
            ("• Запис: Нова ТА Стара колонки", False),
            ("Верифікація стабільності:", True),
            ("• Контроль валідності читання", False),
            ("• Миттєвий відкат на старе", False),
            ("Стан: Нова структура основна", "status")
        ]),
        ("Фаза 4: ЗВУЖЕННЯ (Contract)", "#faf5ff", "#7c3aed", [
            ("Реліз коду v2.0 & Cleanup", True),
            ("• Код v2.0: Тільки нова колонка", False),
            ("• Видалення подвійного запису", False),
            ("DDL очищення:", True),
            ("• DROP старого стовпця / таблиці", False),
            ("• Зняття тимчасових тригерів", False),
            ("Стан: Міграцію завершено", "status")
        ])
    ]

    col_w = 230
    col_gap = 20
    start_x = 30

    for i, (p_title, p_bg, p_color, items) in enumerate(phases):
        x = start_x + i * (col_w + col_gap)
        y = 65
        h = 440
        
        # Контейнер фази
        frags.append(rect(x, y, col_w, h, fill=p_bg, stroke=p_color, sw=1.6, rx=8))
        frags.append(text(x + col_w / 2, y + 25, p_title, size=11, bold=True, color=p_color))
        frags.append(line(x + 10, y + 40, x + col_w - 10, y + 40, color=p_color, sw=1.0, dash="3,3"))

        # Пункти
        cur_y = y + 65
        for item_text, item_type in items:
            if item_type is True:
                frags.append(text(x + 12, cur_y, item_text, size=10, bold=True, color=INK, anchor="start"))
                cur_y += 22
            elif item_type == "status":
                s_box, _, _ = textbox(x + col_w / 2, cur_y + 16, item_text, size=10, bold=True,
                                      fill="#ffffff", stroke=p_color, sw=1.2, pad=6, min_w=col_w - 30)
                frags.append(s_box)
                cur_y += 42
            else:
                frags.append(text(x + 16, cur_y, item_text, size=9, bold=False, color=INK, anchor="start"))
                cur_y += 20

        # Стрілка між фазами
        if i < 3:
            frags.append(arrow(x + col_w + 2, y + h / 2, x + col_w + col_gap - 2, y + h / 2, color=INK, sw=1.8))

    render(os.path.join(IMG, 'expand-contract-phases.svg'), W, H, *frags)


# ── Фігура 3: Online Schema Change (OSC) Архітектура ──────────────────────────
def fig_online_schema_change_ghost():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 25, "Внутрішній механізм Online Schema Change (gh-ost / pt-osc)",
                      size=15, bold=True, color=INK))

    # Ліва частина: Основна таблиця БД
    main_tbl = rect(40, 70, 280, 410, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8)
    frags.append(main_tbl)
    frags.append(text(180, 95, "Оригінальна таблиця: users", size=13, bold=True, color=NEG))
    frags.append(text(180, 115, "Живий продакшн-трафік (Read / Write)", size=10, italic=True, color=MUTED))

    m_app, _, _ = textbox(180, 160, "Додаток / Клієнтські запити\n(INSERT / UPDATE / DELETE)",
                          size=11, bold=True, fill="#ffffff", stroke=NEG, sw=1.2, pad=6)
    frags.append(m_app)

    frags.append(arrow(180, 190, 180, 225, color=NEG, sw=1.8))

    m_data, _, _ = textbox(180, 280, "Поточні дані (100 млн рядків)\n• Схема v1\n• Відсутність блокування таблиці\n• Неперервна доступність",
                           size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=8)
    frags.append(m_data)

    m_binlog, _, _ = textbox(180, 420, "Журнал бінарних логів (Binlog / WAL)\nРеплікаційний потік змін у реальному часі",
                             size=10, bold=True, fill="#fff9e6", stroke="#d97706", sw=1.2, pad=6)
    frags.append(m_binlog)

    # Центральна частина: Контролер OSC
    osc_box = rect(360, 70, 280, 410, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8)
    frags.append(osc_box)
    frags.append(text(500, 95, "OSC Контролер (gh-ost)", size=13, bold=True, color=FIELD))
    frags.append(text(500, 115, "Асинхронний оркестратор міграції", size=10, italic=True, color=MUTED))

    o_stream, _, _ = textbox(500, 165, "1. Зчитувач подій (Streamer):\nСлухає binlog і перехоплює нові\nзміни, що надходять у users",
                             size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    o_copy, _, _ = textbox(500, 255, "2. Чанковий копіювальник:\nКопіює існуючі рядкиusersпакетами\n(WHERE id BETWEEN a AND b)",
                           size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    o_throttle, _, _ = textbox(500, 345, "3. Контролер тротлінгу:\nПеревіряє лаг реплік і CPU.\nПризупиняє бекфіл при навантаженні",
                               size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    o_cutover, _, _ = textbox(500, 435, "4. Атомарний Cutover:\nБлокування users на 10 мс,\nRENAME users <-> _users_gho",
                              size=10, bold=True, fill="#e8f8ed", stroke=FIELD, sw=1.2, pad=6)
    frags.extend([o_stream, o_copy, o_throttle, o_cutover])

    # Права частина: Тіньова Ghost-таблиця
    ghost_tbl = rect(680, 70, 280, 410, fill="#faf5ff", stroke="#7c3aed", sw=1.8, rx=8)
    frags.append(ghost_tbl)
    frags.append(text(820, 95, "Ghost-таблиця: _users_gho", size=13, bold=True, color="#7c3aed"))
    frags.append(text(820, 115, "Тіньова структура з новою схемою v2", size=10, italic=True, color=MUTED))

    g_ddl, _, _ = textbox(820, 165, "Створення порожньої таблиці\nта застосування DDL (ALTER TABLE)\nна нульовому обсязі даних",
                          size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    g_apply, _, _ = textbox(820, 260, "Застосування бінарних змін\nта поступове заповнення чанків\nз перетворенням нових полів",
                            size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    g_state, _, _ = textbox(820, 370, "Стан таблиці:\n• 100% даних синхронізовано\n• Нові індекси побудовано\n• Готовність до підміни",
                            size=10, bold=True, fill="#ffffff", stroke="#7c3aed", sw=1.0, pad=6)
    g_final, _, _ = textbox(820, 450, "Після Cutover: Стає новою users",
                            size=10, bold=True, fill="#ede9fe", stroke="#7c3aed", sw=1.2, pad=6)
    frags.extend([g_ddl, g_apply, g_state, g_final])

    # Зв'язки стрілками між компонентами
    # Binlog -> Streamer
    frags.append(arrow(320, 420, 360, 190, color="#d97706", sw=1.8))
    # Streamer -> Ghost Table Apply
    frags.append(arrow(640, 175, 680, 240, color=FIELD, sw=1.8))
    # Data -> Chunker
    frags.append(arrow(320, 280, 360, 260, color=NEG, sw=1.8))
    # Chunker -> Ghost Table
    frags.append(arrow(640, 265, 680, 275, color=FIELD, sw=1.8))
    # Cutover Swap arrow
    frags.append(arrow(500, 465, 820, 465, color="#7c3aed", sw=1.8))

    render(os.path.join(IMG, 'online-schema-change-ghost.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_migration_pipeline_lifecycle()
    fig_expand_contract_phases()
    fig_online_schema_change_ghost()
    print("All figures generated successfully.")
