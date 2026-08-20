# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. decomposition-comparison: процедурний поділ vs поділ за Парнасом ──────────
def fig_decomposition_comparison():
    W, H = 840, 450
    p = []

    midx = 420
    p.append(line(midx, 46, midx, 416, color=MUTED, sw=1.2, dash="5 4"))

    # Ліва колонка — Процедурний розклад
    p.append(text(210, 60, "Процедурний розклад (за блок-схемою)", size=14, color=POS, bold=True))
    p.append(text(210, 78, "Модулі = кроки виконання в часі", size=11, color=MUTED, italic=True))

    steps = ["Ввід даних", "Зсув рядків", "Сортування", "Вивід результату"]
    sy = 106
    for i, s in enumerate(steps):
        bx, bw, bh = 210, 160, 36
        p.append(fitbox(bx - bw / 2, sy, bw, bh, s, size=11, fill="#fdecea", stroke=POS, sw=1.6))
        if i < len(steps) - 1:
            p.append(arrow(bx, sy + bh, bx, sy + bh + 16, color=POS, sw=1.5))
        sy += 52

    # Спільні дані внизу зліва
    p.append(fitbox(70, 320, 280, 52,
                    "Спільна пам'ять / таблиця зміщень\n(всі модулі знають точне розміщення масиву)",
                    size=10, fill="#fdedec", stroke=POS, sw=1.8))
    # Стрілки залежностей до спільного сховища
    p.append(arrow(130, 142, 110, 320, color=POS, sw=1.2))
    p.append(arrow(130, 194, 150, 320, color=POS, sw=1.2))
    p.append(arrow(290, 246, 270, 320, color=POS, sw=1.2))
    p.append(arrow(290, 298, 310, 320, color=POS, sw=1.2))

    p.append(text(210, 400, "Зміна формату масиву ламає всі 4 модулі", size=11, color=POS, bold=True))

    # Права колонка — Розклад за Парнасом
    p.append(text(630, 60, "Розклад за Парнасом (за таємницями)", size=14, color=FIELD, bold=True))
    p.append(text(630, 78, "Модулі = приховані проєктні рішення", size=11, color=MUTED, italic=True))

    # Сховище — центральний захищений модуль
    p.append(fitbox(500, 106, 260, 56,
                    "Модуль «Сховище рядків»\n(ТАЄМНИЦЯ: формат масиву, вирівнювання, байти)",
                    size=10, fill="#e8f5e9", stroke=FIELD, sw=2.0))

    clients = [
        ("Модуль зсувів\n(ТАЄМНИЦЯ: формули зсуву)", 480, 196, 140, 46),
        ("Модуль упорядкування\n(ТАЄМНИЦЯ: алгоритм сортування)", 640, 196, 150, 46),
        ("Модуль вводу\n(ТАЄМНИЦЯ: читання)", 480, 276, 140, 46),
        ("Модуль виводу\n(ТАЄМНИЦЯ: формат)", 640, 276, 150, 46),
    ]

    for label, cx, cy, bw, bh in clients:
        p.append(fitbox(cx - bw / 2, cy, bw, bh, label, size=10, fill="#f4f6f8", stroke=INK, sw=1.5))

    # Стрілки через публічний контракт
    p.append(arrow(480, 196, 540, 162, color=FIELD, sw=1.5))
    p.append(arrow(640, 196, 620, 162, color=FIELD, sw=1.5))
    p.append(arrow(480, 276, 480, 242, color=MUTED, sw=1.3))
    p.append(arrow(640, 276, 640, 242, color=MUTED, sw=1.3))

    p.append(fitbox(500, 344, 260, 40,
                    "Публічний контракт операцій: get_char(), line_cnt()\n(клієнти не знають про масив нічого)",
                    size=9, fill="#eaf0fd", stroke=NEG, sw=1.4))

    p.append(text(630, 410, "Зміна формату сховища замкнена в 1 модулі", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "decomposition-comparison.svg"), W, H, *p,
           title="Два підходи до декомпозиції: крок конвеєра проти прихованого рішення")


# ── 2. secret-and-interface: анатомія модуля за Парнасом ────────────────────────
def fig_secret_and_interface():
    W, H = 840, 440
    p = []

    # Зовнішня рамка клієнтського середовища
    p.append(rect(40, 52, 760, 360, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(160, 74, "КЛІЄНТСЬКИЙ КОД (Зовнішній світ)", size=12, color=MUTED, bold=True))

    # Модуль за Парнасом
    mx, my, mw, mh = 260, 96, 520, 300
    p.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=FIELD, sw=2.2, rx=8))
    p.append(text(mx + mw / 2, my + 24, "МОДУЛЬ ЗА ПАРНАСОМ", size=14, color=FIELD, bold=True))

    # Бар'єр інтерфейсу (верхня смуга капсули)
    p.append(rect(mx + 16, my + 42, mw - 32, 64, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(mx + mw / 2, my + 60, "ПУБЛІЧНИЙ ІНТЕРФЕЙС / КОНТРАКТ", size=12, color=NEG, bold=True))
    p.append(text(mx + mw / 2, my + 82, "Неповні типи · Сигнатури функцій · Передумови/постумови · Коди помилок",
                  size=10, color=INK))

    # Внутрішня захищена зона (Таємниця)
    p.append(rect(mx + 16, my + 118, mw - 32, 166, fill="#fdfefe", stroke=POS, sw=1.8, rx=6))
    p.append(text(mx + mw / 2, my + 138, "ТАЄМНИЦЯ МОДУЛЯ (Secret)", size=13, color=POS, bold=True))

    secrets = [
        "1. Структура пам'яті: двозв'язний список, динамічний вектор, бітова маска",
        "2. Апаратні регістри: біти керування, адреси MMIO, часові затримки",
        "3. Алгоритмічні евристики: політика витіснення кешу (LRU/LFU), швидке сортування",
        "4. Формати протоколів: бінарні заголовки, вирівнювання, порядок байтів (endianness)",
        "5. Управління ресурсами: м'ютекси, пули дескрипторів, динамічна алокація",
    ]
    sy = my + 160
    for s in secrets:
        p.append(text(mx + 30, sy, s, size=10, color=INK, anchor="start"))
        sy += 22

    # Стрілки запитів від клієнта через інтерфейсний бар'єр
    p.append(arrow(90, 150, mx + 16, 150, color=NEG, sw=1.8))
    p.append(text(150, 142, "виклик API", size=10, color=NEG, bold=True))

    p.append(arrow(90, 200, mx + 16, 200, color=NEG, sw=1.8))
    p.append(text(150, 192, "запит послуги", size=10, color=NEG, bold=True))

    p.append(arrow(mx + 16, 250, 90, 250, color=FIELD, sw=1.8))
    p.append(text(150, 242, "результат / статус", size=10, color=FIELD, bold=True))

    # Червоний щит/хрест доступу до таємниці напряму
    p.append(line(80, 310, 230, 310, color=POS, sw=1.6, dash="4 3"))
    p.append(line(220, 300, 240, 320, color=POS, sw=2.2))
    p.append(line(240, 300, 220, 320, color=POS, sw=2.2))
    p.append(text(150, 330, "прямий доступ заборонено", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "secret-and-interface.svg"), W, H, *p,
           title="Анатомія модуля за Парнасом: таємниця за інтерфейсним бар'єром")


# ── 3. change-impact: радіус ураження змін ──────────────────────────────────────
def fig_change_impact():
    W, H = 840, 440
    p = []

    midx = 420
    p.append(line(midx, 48, midx, 412, color=MUTED, sw=1.2, dash="5 4"))

    # Ліворуч: Процедурний витік — катастрофа змін
    p.append(text(210, 60, "Витік представлення (без бар'єра)", size=13, color=POS, bold=True))
    p.append(text(210, 78, "Зміна 1 деталі породжує ланцюгову реакцію", size=10, color=MUTED, italic=True))

    p.append(fitbox(80, 100, 260, 44, "Зміна: заміна статичного масиву на хеш-таблицю", size=10, fill="#fdecea", stroke=POS, sw=1.8))

    # Стрілка розгалуження (деревоподібний розвід без перетинань)
    p.append(line(210, 144, 210, 158, color=POS, sw=1.4))
    p.append(line(70, 158, 70, 340, color=POS, sw=1.4))
    p.append(line(70, 158, 210, 158, color=POS, sw=1.4))

    impacted = [
        ("Модуль парсингу (переписати доступ)", 90, 172, 240, 32),
        ("Модуль фільтрації (переписати індекси)", 90, 218, 240, 32),
        ("Модуль збереження (переписати серіалізацію)", 90, 264, 240, 32),
        ("Модуль візуалізації (переписати ітератор)", 90, 310, 240, 32),
    ]
    for lbl, x, y, w, h in impacted:
        p.append(fitbox(x, y, w, h, lbl, size=10, fill="#fdecea", stroke=POS, sw=1.4))
        p.append(arrow(70, y + h / 2, x, y + h / 2, color=POS, sw=1.4))

    p.append(fitbox(80, 368, 260, 34, "Радіус ураження = 100% системи (4 модулі зламано)", size=10, fill="#fadbd8", stroke=POS, sw=1.6))

    # Праворуч: Приховування інформації — повна локалізація
    p.append(text(630, 60, "Приховування інформації (з бар'єром)", size=13, color=FIELD, bold=True))
    p.append(text(630, 78, "Зміна повністю локалізована всередині модуля", size=10, color=MUTED, italic=True))

    p.append(fitbox(500, 100, 260, 44, "Зміна: заміна статичного масиву на хеш-таблицю", size=10, fill="#eaf0fd", stroke=NEG, sw=1.8))

    p.append(fitbox(500, 168, 260, 52,
                    "Модуль сховища (оновлено внутрішній код)\nКонтракт: get_item(), count() — НЕ ЗМІНИВСЯ",
                    size=10, fill="#e8f5e9", stroke=FIELD, sw=2.0))
    p.append(arrow(630, 144, 630, 168, color=FIELD, sw=1.8))

    clients_ok = [
        ("Модуль парсингу (без змін, той самий API)", 510, 252, 240, 30),
        ("Модуль фільтрації (без змін, той самий API)", 510, 292, 240, 30),
        ("Модуль збереження (без змін, той самий API)", 510, 332, 240, 30),
    ]
    for lbl, x, y, w, h in clients_ok:
        p.append(fitbox(x, y, w, h, lbl, size=10, fill="#f4f6f8", stroke=MUTED, sw=1.2))

    p.append(line(500, 236, 760, 236, color=FIELD, sw=2.0))
    p.append(text(630, 246, "НЕПРОНИКНИЙ БАР'ЄР КОНТРАКТУ", size=9, color=FIELD, bold=True))

    p.append(fitbox(500, 374, 260, 34, "Радіус ураження = 1 модуль (клієнти не перекомпільовуються)", size=10, fill="#d4efdf", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "change-impact.svg"), W, H, *p,
           title="Радіус ураження змін: процедурний витік проти приховування інформації")


# ── 4. opaque-boundary: компіляційний бар'єр та неповні типи ────────────────────
def fig_opaque_boundary():
    W, H = 840, 420
    p = []

    midx = 420
    p.append(line(midx, 48, midx, 396, color=MUTED, sw=1.4, dash="6 4"))
    p.append(text(midx, 36, "КОМПІЛЯЦІЙНИЙ БАР'ЄР (ABI Firewall)", size=11, color=NEG, bold=True))

    # Ліва частина — Клієнтська одиниця трансляції
    p.append(rect(40, 56, 350, 330, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(text(215, 78, "Клієнтський файл (client.c / main.cpp)", size=12, color=INK, bold=True))

    p.append(fitbox(56, 96, 318, 64,
                    "Публічний заголовок (sensor.h):\n"
                    "typedef struct sensor sensor_t;  /* неповний тип */\n"
                    "sensor_t* sensor_create(uint8_t id);\n"
                    "int sensor_read(sensor_t *s, float *out);",
                    size=10, fill="#eaf0fd", stroke=NEG, sw=1.6))

    p.append(fitbox(56, 176, 318, 90,
                    "Клієнтський код:\n"
                    "sensor_t *s = sensor_create(1);\n"
                    "float val = 0.0f;\n"
                    "sensor_read(s, &val);\n"
                    "/* sizeof(struct sensor) невідомий! */\n"
                    "/* s->raw_reg — ПОМИЛКА КОМПІЛЯЦІЇ */",
                    size=10, fill="#f4f6f8", stroke=INK, sw=1.3))

    p.append(fitbox(56, 282, 318, 88,
                    "Що знає компілятор клієнта:\n"
                    "• Розмір покажчика (4 або 8 байтів)\n"
                    "• Сигнатури публічних функцій\n"
                    "• Жодного зміщення внутрішніх полів!",
                    size=10, fill="#e8f8f5", stroke=FIELD, sw=1.4))

    # Права частина — Одиниця трансляції реалізації
    p.append(rect(450, 56, 350, 330, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(text(625, 78, "Файл реалізації (sensor.c / sensor.cpp)", size=12, color=INK, bold=True))

    p.append(fitbox(466, 96, 318, 120,
                    "Повне визначення структури (лише в .c):\n"
                    "struct sensor {\n"
                    "    uint8_t   bus_id;\n"
                    "    uint16_t  calibration_raw[16];\n"
                    "    float     last_temperature;\n"
                    "    uint32_t  error_flags;\n"
                    "    void      *bus_handle;\n"
                    "};",
                    size=10, fill="#fef9e7", stroke="#c07000", sw=1.6))

    p.append(fitbox(466, 230, 318, 70,
                    "Внутрішня реалізація:\n"
                    "• sensor_create: виділяє пам'ять під повну структуру\n"
                    "• sensor_read: читає калібрування, рахує формулу\n"
                    "• приватні допоміжні функції: static inline",
                    size=10, fill="#f4f6f8", stroke=INK, sw=1.3))

    p.append(fitbox(466, 314, 318, 56,
                    "Перевага ABI:\n"
                    "Зміна полів struct sensor не вимагає перекомпіляції client.o!",
                    size=10, fill="#d4efdf", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "opaque-boundary.svg"), W, H, *p,
           title="Компіляційний бар'єр: непрозорий покажчик (Opaque Pointer)")


if __name__ == "__main__":
    fig_decomposition_comparison()
    fig_secret_and_interface()
    fig_change_impact()
    fig_opaque_boundary()
    print("Всі фігури згенеровано успішно.")
