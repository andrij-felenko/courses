# -*- coding: utf-8 -*-
"""Фігури до теми «Zero-downtime міграції даних».

Генерує 4 SVG діаграми:
1. expand-contract-phases.svg      — Фази життєвого циклу Expand/Contract без зупинки сервісу
2. dual-write-backfill-race.svg   — Стан перегонів між фоновим Backfill і Dual-Write та умовне збереження
3. cdc-stream-migration.svg       — Міграція через CDC (Change Data Capture) із читанням журналу транзакцій
4. reversible-cutover-matrix.svg  — Двонаправлена реплікація та безпечне перемикання з можливістю відкату
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # збій / гонка / старі дані
COOL = "#eaf0fd"   # нейтральне / схема / сховище
GOOD = "#e8f6ee"   # успіх / новий стан / узгодженість
WARN = "#fef9e7"   # проміжне / черга / CDC


# ── 1. Фази Expand/Contract ──────────────────────────────────────────────────
def fig_expand_contract_phases():
    W, H = 1280, 680
    f = []

    f.append(fitbox(40, 20, 1200, 42,
                    "ЖИТТЄВИЙ ЦИКЛ ПАТЕРНУ EXPAND / CONTRACT ДЛЯ МІГРАЦІЇ БЕЗ ПРОСТОЮ",
                    size=14, bold=True, fill=COOL))

    phases = [
        ("ФАЗА 1: EXPAND", "Розширення схеми",
         "• Створення нових таблиць\n• Неблокуюче DDL\n  (NULL / CONCURRENTLY)\n• Старий код діє без змін",
         COOL, LINE),
        ("ФАЗА 2: DUAL-WRITE", "Подвійний запис",
         "• Запис у дві схеми\n• Джерело правди:\n  СТАРА база даних\n• Читання лише зі старої",
         WARN, LINE),
        ("ФАЗА 3: BACKFILL", "Фоновий бекфіл",
         "• Порційне копіювання\n• Захист від перезапису\n  новіших мутацій\n• Дроселювання за лагом",
         WARN, LINE),
        ("ФАЗА 4: VERIFY", "Тіньова звірка",
         "• Dark read / звірка 100%\n• Асинхронний порівнювач\n  контрольних сум\n• Усунення розходжень",
         GOOD, FIELD),
        ("ФАЗА 5: CUTOVER", "Перемикання",
         "• Читання з НОВОЇ бази\n• НОВА база — Master\n• Reverse-синхронізація\n  на випадок відкату",
         GOOD, FIELD),
        ("ФАЗА 6: CONTRACT", "Стягування",
         "• Зупинка запису в стару\n• Видалення старих полів\n  та таблиць у базі\n• Спрощення коду сервісу",
         COOL, LINE)
    ]

    col_w = 186.0
    gap = 16.0
    start_x = 40.0
    box_y = 80.0
    box_h = 320.0

    for i, (title, sub, body, bg_col, stroke_col) in enumerate(phases):
        bx = start_x + i * (col_w + gap)
        f.append(rect(bx, box_y, col_w, box_h, fill=bg_col, stroke=stroke_col, sw=1.5, rx=6))
        f.append(fitbox(bx + 6, box_y + 8, col_w - 12, 34, title, size=11, bold=True, fill="#ffffff", stroke=stroke_col, sw=1.0))
        f.append(fitbox(bx + 6, box_y + 46, col_w - 12, 24, sub, size=10.5, bold=True, fill=bg_col, stroke=MUTED, sw=0.8))
        f.append(fitbox(bx + 8, box_y + 76, col_w - 16, 230, body, size=10.5, bold=False, fill="#ffffff", stroke=MUTED, sw=0.8))

        if i < 5:
            # Стрілка між фазами
            f.append(arrow(bx + col_w + 1, box_y + 160, bx + col_w + gap - 1, box_y + 160, color=LINE, sw=1.8))

    # Нижній блок: гарантії та сумісність
    f.append(rect(40, 420, 1200, 190, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(55, 435, 1170, 32,
                    "КЛЮЧОВИЙ ПРИНЦИП: ДВОСТОРОННЯ СУМІСНІСТЬ (N-1 ТА N+1 РЕЛІЗИ ЗАСТОСУНКУ)",
                    size=12.5, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    f.append(fitbox(55, 475, 570, 120,
                    "ЗВОРОТНА СУМІСНІСТЬ (Backward Compatibility):\n\n"
                    "• Нова версія застосунку (N+1) вміє читати і писати стару схему\n"
                    "• Будь-яке розширення схеми є опційним (nullable або default)\n"
                    "• Відсутність збоїв під час канареечного розгортання",
                    size=11, bold=False, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(645, 475, 580, 120,
                    "ПРЯМА СУМІСНІСТЬ (Forward Compatibility):\n\n"
                    "• Стара версія застосунку (N) ігнорує нові поля і продовжує роботу\n"
                    "• Безпечний відкат бінарників застосунку без відкату міграцій БД\n"
                    "• Відсутність блокуючих монолітних вікон оновлення",
                    size=11, bold=False, fill=GOOD, stroke=FIELD, sw=1.2))

    f.append(fitbox(40, 625, 1200, 40,
                    "Правило нульового простою: База даних завжди повинна бути готова прийняти як попередню, так і наступну версію коду.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'expand-contract-phases.svg'), W, H, *f)


# ── 2. Гонка Dual-Write проти Backfill ────────────────────────────────────────
def fig_dual_write_backfill_race():
    W, H = 1200, 640
    f = []

    f.append(fitbox(40, 20, 1120, 42,
                    "ГОНКА ДАНИХ: ЗАТИРАННЯ ЖИВИХ МУТАЦІЙ ФОНОВИМ БЕКФІЛОМ ТА ЇЇ ЗАПОБІГАННЯ",
                    size=14, bold=True, fill=WARM))

    # Ліва колонка: Проблема (Затирання)
    lx = 40.0
    ly = 75.0
    lw = 545.0
    lh = 540.0
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(fitbox(lx + 15, ly + 15, lw - 30, 36,
                    "НЕБЕЗПЕЧНИЙ СЦЕНАРІЙ: Наївний несинхронізований Upsert",
                    size=12, bold=True, fill=WARM, stroke=POS, sw=1.2))

    timeline_bad = [
        ("t1: Бекфіл читає рядок", "SELECT * FROM users WHERE id=42\nОтримано: status='ACTIVE', email='old@ua' (v1)", COOL),
        ("t2: Живий користувач змінює стан", "App: UPDATE users SET email='new@ua', v=2\nDual-Write пише email='new@ua' у нову БД", GOOD),
        ("t3: Нова БД вже має свіжі дані", "Нова БД: id=42, email='new@ua', version=2", GOOD),
        ("t4: Бекфіл добігає до запису", "Бекфіл виконує: INSERT INTO new_users ...\nON CONFLICT DO UPDATE SET email='old@ua'", WARM),
        ("КАТАСТРОФА: ВТРАТА ОНОВЛЕННЯ", "Свіже значення 'new@ua' затерто старим 'old@ua'.\nДані розійшлися, користувач втратив зміну.", WARM)
    ]

    ty = ly + 60.0
    for title, desc, col in timeline_bad:
        f.append(rect(lx + 20, ty, lw - 40, 78, fill=col, stroke=LINE, sw=1.0, rx=4))
        f.append(fitbox(lx + 30, ty + 6, lw - 60, 24, title, size=11, bold=True, fill=col, stroke=col))
        f.append(fitbox(lx + 30, ty + 30, lw - 60, 42, desc, size=10, bold=False, fill=col, stroke=col))
        ty += 88.0

    # Права колонка: Рішення (Умовний запис за версією / LSN)
    rx_col = 615.0
    ry = 75.0
    rw = 545.0
    rh = 540.0
    f.append(rect(rx_col, ry, rw, rh, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(fitbox(rx_col + 15, ry + 15, rw - 30, 36,
                    "НАДІЙНИЙ СЦЕНАРІЙ: Умовний запис (Optimistic Locking / Version Check)",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    timeline_good = [
        ("t1: Бекфіл читає зріз із версією", "SELECT id, email, updated_at FROM users WHERE id=42\nОтримано: v1, updated_at=10:00:00", COOL),
        ("t2: Живий користувач змінює стан", "Dual-Write пише в нову БД:\nemail='new@ua', updated_at=10:00:05 (v2)", GOOD),
        ("t3: Нова БД оновлена до v2", "Нова БД: id=42, email='new@ua', updated_at=10:00:05", GOOD),
        ("t4: Бекфіл робить УМОВНИЙ запис", "INSERT INTO new_users ... VALUES (42, 'old@ua', '10:00:00')\nON CONFLICT (id) DO UPDATE SET email=EXCLUDED.email\nWHERE new_users.updated_at <= EXCLUDED.updated_at;", WARN),
        ("РЕЗУЛЬТАТ: ЗАХИСТ ВІД ЗАТИРАННЯ", "Умова WHERE не виконується (10:00:05 > 10:00:00).\nЗапис бекфілу ігнорується, свіжий стан v2 збережено!", GOOD)
    ]

    ty = ry + 60.0
    for title, desc, col in timeline_good:
        f.append(rect(rx_col + 20, ty, rw - 40, 78, fill=col, stroke=LINE, sw=1.0, rx=4))
        f.append(fitbox(rx_col + 30, ty + 6, rw - 60, 24, title, size=11, bold=True, fill=col, stroke=col))
        f.append(fitbox(rx_col + 30, ty + 30, rw - 60, 42, desc, size=10, bold=False, fill=col, stroke=col))
        ty += 88.0

    render(os.path.join(OUT, 'dual-write-backfill-race.svg'), W, H, *f)


# ── 3. Конвеєр CDC-міграції ──────────────────────────────────────────────────
def fig_cdc_stream_migration():
    W, H = 1180, 620
    f = []

    f.append(fitbox(40, 20, 1100, 42,
                    "КОНВЕЄР МІГРАЦІЇ НА ОСНОВІ CHANGE DATA CAPTURE (CDC) ТА ЖУРНАЛУ ТРАНЗАКЦІЙ",
                    size=14, bold=True, fill=COOL))

    # Джерело: Primary DB
    f.append(rect(40, 90, 260, 400, fill=COOL, stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(55, 105, 230, 36, "ПЕРВИННЕ СХОВИЩЕ\n(Source Database)", size=12, bold=True, fill="#ffffff", stroke=LINE, sw=1.2))

    f.append(fitbox(55, 160, 230, 70, "Таблиці даних\n(Row Storage)\nЖиві OLTP транзакції", size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))
    f.append(arrow(170, 235, 170, 275, color=LINE, sw=1.8))
    f.append(fitbox(55, 280, 230, 90, "Журнал випереджального запису\n(WAL / Binary Log)\nПослідовний потік мутацій\nіз номерами LSN", size=11, bold=True, fill=WARN, stroke=LINE, sw=1.2))

    f.append(fitbox(55, 390, 230, 80, "Початковий знімок (Snapshot)\nLSN = 18452000\nФіксована точка відліку", size=10.5, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Стрілки від первинної бази
    f.append(arrow(300, 325, 370, 325, color=LINE, sw=2))
    f.append(fitbox(305, 298, 60, 22, "CDC потік", size=10, bold=True, fill="#ffffff", stroke="#ffffff"))

    f.append(arrow(300, 430, 370, 430, color=LINE, sw=2))
    f.append(fitbox(305, 403, 60, 22, "Snapshot", size=10, bold=True, fill="#ffffff", stroke="#ffffff"))

    # Посередник: CDC Engine / Broker
    f.append(rect(370, 90, 400, 400, fill=WARN, stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(385, 105, 370, 36, "РУШІЙ МІГРАЦІЇ ТА ОБРОБКИ ПОТОКУ\n(Debezium / Kafka / Custom Consumer)", size=12, bold=True, fill="#ffffff", stroke=LINE, sw=1.2))

    f.append(fitbox(385, 160, 370, 95, "1. Буфер подій та упорядкування:\n• Збереження монотонності за LSN\n• Розпаралелювання за ключем шардування\n• Дедуплікація повторів", size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    f.append(fitbox(385, 275, 370, 95, "2. Трансформація схеми (Schema Mapping):\n• Перетворення типів (JSON -> Колонки)\n• Денормалізація / розщеплення полів\n• Додавання метаданих версії", size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    f.append(fitbox(385, 390, 370, 85, "3. Дроселювання (Backpressure Control):\n• Моніторинг відставання цільової бази\n• Автоматичне регулювання швидкості", size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    # Стрілка від рушія до цільової бази
    f.append(arrow(770, 290, 840, 290, color=FIELD, sw=2))
    f.append(fitbox(775, 265, 60, 22, "Apply", size=10.5, bold=True, fill="#ffffff", stroke="#ffffff"))

    # Цільова база
    f.append(rect(840, 90, 300, 400, fill=GOOD, stroke=FIELD, sw=1.5, rx=8))
    f.append(fitbox(855, 105, 270, 36, "ЦІЛЬОВЕ СХОВИЩЕ\n(Target Database)", size=12, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2))

    f.append(fitbox(855, 160, 270, 95, "Нова схема даних\n• Оптимізовані індекси\n• Нова топологія (кластер)\n• Готовність до навантаження", size=11, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0))

    f.append(fitbox(855, 275, 270, 95, "Ідемпотентне застосування:\n• UPSERT за первинним ключем\n• Ігнорування LSN < last_applied\n• Постійний нагін відставання", size=11, bold=False, fill="#ffffff", stroke=FIELD, sw=1.0))

    f.append(fitbox(855, 390, 270, 85, "Метрики відставання (Lag):\nLag = LSN_source - LSN_target\nКоли Lag -> 0 => Перемикання!", size=11, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Підсумок внизу
    f.append(fitbox(40, 515, 1100, 75,
                    "ПЕРЕВАГА CDC: Нульове навантаження на OLTP-рушій запитів (читання йде з бінарного журналу диска).\n"
                    "Постійний потік змін гарантує, що цільове сховище наздожене первинне навіть за мільйонів операцій запису на секунду.",
                    size=11.5, bold=True, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, 'cdc-stream-migration.svg'), W, H, *f)


# ── 4. Матриця перемикання та відкату ─────────────────────────────────────────
def fig_reversible_cutover_matrix():
    W, H = 1180, 640
    f = []

    f.append(fitbox(40, 20, 1100, 42,
                    "АРХІТЕКТУРА БЕЗПЕЧНОГО ПЕРЕМИКАННЯ: ДВОНАПРАВЛЕНА СИНХРОНІЗАЦІЯ І ВІДКАТ",
                    size=14, bold=True, fill=COOL))

    # Схема перемикання зверху
    f.append(rect(40, 80, 1100, 260, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(55, 95, 1070, 30, "ПЕРІОД ПЕРЕМИКАННЯ (CUTOVER WINDOW) ІЗ ЗАХИСТОМ ВІД ВТРАТИ ДАНИХ", size=12, bold=True, fill=COOL, stroke=MUTED, sw=1.0))

    # Клієнти / Роутер
    f.append(fitbox(60, 150, 180, 120, "КЛІЄНТСЬКИЙ ТРАФІК\n\nДинамічний роутер /\nFeature Flag:\n• Read: New DB (100%)\n• Write: New DB (100%)", size=11, bold=True, fill=COOL, stroke=LINE, sw=1.2))

    f.append(arrow(240, 210, 320, 210, color=LINE, sw=2))

    # Нова БД (Master)
    f.append(fitbox(320, 140, 260, 140, "НОВА БАЗА ДАНИХ\n(Active Primary)\n\n• Обслуговує 100% запитів\n• Генерує події мутацій\n• Джерело правди", size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.8))

    # Стрілка реверсної синхронізації
    f.append(arrow(580, 190, 780, 190, color=POS, sw=2.5))
    f.append(fitbox(595, 145, 170, 40, "ЗВОРОТНА РЕПЛІКАЦІЯ\n(Reverse CDC Stream)", size=10.5, bold=True, fill=WARM, stroke=POS, sw=1.2))

    # Стара БД (Standby Shadow)
    f.append(fitbox(780, 140, 260, 140, "СТАРА БАЗА ДАНИХ\n(Passive Standby)\n\n• Отримує всі нові записи\n• Підтримується в актуальному стані\n• Готова до миттєвого повернення", size=11.5, bold=True, fill=WARN, stroke=MUTED, sw=1.5))

    # Нижня частина: Порівняльна матриця дій
    f.append(rect(40, 360, 535, 250, fill=GOOD, stroke=FIELD, sw=1.5, rx=8))
    f.append(fitbox(55, 375, 505, 32, "СЦЕНАРІЙ УСПІХУ: ЗАВЕРШЕННЯ МІГРАЦІЇ", size=12, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2))
    f.append(fitbox(55, 415, 505, 180,
                    "1. Цільова база стабільно працює під повним навантаженням (24–72 год)\n"
                    "2. Метрики затримок, помилок і навантаження CPU в межах норми\n"
                    "3. Зворотна реплікація вимикається\n"
                    "4. Стара база даних переводиться в режим Read-Only і архівується\n"
                    "5. Стара схема остаточно видаляється (Contract phase)\n"
                    "6. Міграція успішно закрита без жодної секунди простою",
                    size=10.5, bold=False, fill="#ffffff", stroke=FIELD, sw=1.0))

    f.append(rect(605, 360, 535, 250, fill=WARM, stroke=POS, sw=1.5, rx=8))
    f.append(fitbox(620, 375, 505, 32, "АВАРІЙНИЙ СЦЕНАРІЙ: БЕЗПЕЧНИЙ ВІДКАТ (ROLLBACK)", size=12, bold=True, fill="#ffffff", stroke=POS, sw=1.2))
    f.append(fitbox(620, 415, 505, 180,
                    "1. У новій базі виявлено приховану деградацію / некоректну логіку\n"
                    "2. Роутер миттєво перемикає Feature Flag назад на Стару базу\n"
                    "3. Завдяки зворотній синхронізації стара база містить ВСІ транзакції,\n"
                    "   що відбулися за час роботи нової бази!\n"
                    "4. ЖОДЕН запис клієнта не втрачено (Zero Data Loss)\n"
                    "5. Сервіс продовжує роботу, команда спокійно виправляє дефект",
                    size=10.5, bold=False, fill="#ffffff", stroke=POS, sw=1.0))

    render(os.path.join(OUT, 'reversible-cutover-matrix.svg'), W, H, *f)


if __name__ == '__main__':
    fig_expand_contract_phases()
    fig_dual_write_backfill_race()
    fig_cdc_stream_migration()
    fig_reversible_cutover_matrix()
    print("Zero-downtime migration figures generated successfully.")
