# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Протокол параметрів: конфігурація та синхронізація».
svgkit імпортуємо зі scripts/, вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: структура кадру PARAM_VALUE та трюк бітового відображення ───────
def fig_param_value_layout():
    W, H = 940, 470
    parts = []

    # Верхній заголовок секції байтів
    y = 90
    h = 60
    x = 40

    cells = [
        ("param_value", "4 байти (float)", "#fff3e0", "#d97706", 180),
        ("param_count", "2 байти (uint16)", "#eaf0fd", NEG, 140),
        ("param_index", "2 байти (uint16)", "#eaf0fd", NEG, 140),
        ("param_id [16]", "16 байтів (ASCII)", "#e9f7ef", FIELD, 240),
        ("param_type", "1 байт", "#f3e8ff", "#7c3aed", 120),
    ]

    xs = []
    for name, sub, fill, col, w in cells:
        parts.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2, rx=6))
        parts.append(text(x + w / 2, y + 26, name, size=13, bold=True, color=col))
        parts.append(text(x + w / 2, y + 46, sub, size=11, color=MUTED))
        xs.append((x, w))
        x += w + 8

    # Дужка під усім корисним навантаженням
    total_w = x - 40 - 8
    parts.append(line(40, y + h + 12, 40 + total_w, y + h + 12, color=INK, sw=1.6))
    parts.append(line(40, y + h + 6, 40, y + h + 12, color=INK, sw=1.6))
    parts.append(line(40 + total_w, y + h + 6, 40 + total_w, y + h + 12, color=INK, sw=1.6))
    parts.append(text(40 + total_w / 2, y + h + 28, "Корисне навантаження повідомлення PARAM_VALUE (#22) — рівно 25 байтів", size=12, color=INK, bold=True))

    # Виноска зліва: як 4 байти float зберігають цілі числа без спотворень (bit-cast)
    box_left = fitbox(40, 210, 410, 220,
                      "Трюк бітового відображення (Bit-cast)\n\n"
                      "Поле param_value передається як 32-бітний IEEE 754 float.\n"
                      "Для цілих типів (UINT32 / INT32) заборонено числове зведення (float)x:\n"
                      "мантиса float має лише 24 біти, що знищує молодші біти цілого.\n\n"
                      "Правило протоколу: сирі 4 байти цілого копіюються в 4 байти float\n"
                      "через memcpy або std::bit_cast без зміни бітів.",
                      size=12, fill="#fffaf0", stroke="#d97706", sw=1.8)
    parts.append(box_left)
    parts.append(arrow(xs[0][0] + xs[0][1] / 2, y + h + 35, 245, 210, color="#d97706", sw=1.6))

    # Виноска справа: безпека рядка param_id та нумерація
    box_right = fitbox(490, 210, 410, 220,
                       "Пастки ідентифікатора та нумерації\n\n"
                       "• param_id: рівно 16 байтів ASCII. Якщо назва має 16 символів,\n"
                       "  нульовий символ '\\0' ВІДСУТНІЙ! Читач зобов'язаний виділити 17 байтів\n"
                       "  і додати кінцевий '\\0' власноруч.\n\n"
                       "• param_index: номер параметра від 0 до param_count - 1.\n"
                       "  Дозволяє ловити пропущені пакети за розривами індексів.",
                       size=12, fill="#f0fdf4", stroke=FIELD, sw=1.8)
    parts.append(box_right)
    parts.append(arrow(xs[3][0] + xs[3][1] / 2, y + h + 35, 695, 210, color=FIELD, sw=1.6))

    render("img/param-value-layout.svg", W, H, *parts,
           title="Структура повідомлення PARAM_VALUE: розташування полів та упаковка даних")


# ── Фігура 2: синхронізація дерева параметрів та відновлення втрат ────────────
def fig_param_tree_download():
    W, H = 940, 520
    parts = []

    lx, rx = 200, W - 200
    top = 70

    # Шапки учасників
    parts.append(rect(lx - 120, top - 36, 240, 32, fill="#eef2f7", stroke=INK, sw=2, rx=6))
    parts.append(text(lx, top - 15, "Наземна станція (GCS)", size=13, bold=True))

    parts.append(rect(rx - 100, top - 36, 200, 32, fill="#eef2f7", stroke=INK, sw=2, rx=6))
    parts.append(text(rx, top - 15, "Автопілот (Борт)", size=13, bold=True))

    # Лінії життя
    parts.append(line(lx, top, lx, H - 30, color=MUTED, sw=1.2, dash="3,5"))
    parts.append(line(rx, top, rx, H - 30, color=MUTED, sw=1.2, dash="3,5"))

    # 1. Запит повного списку
    y1 = top + 35
    parts.append(arrow(lx, y1, rx, y1 + 20, color=INK, sw=2))
    parts.append(text(lx + 20, y1 + 3, "PARAM_REQUEST_LIST (#21)", size=12, color=INK, bold=True, anchor="start"))

    # 2. Потік відповідей
    y2 = y1 + 45
    # packet 0 (ok)
    parts.append(arrow(rx, y2, lx, y2 + 18, color=FIELD, sw=1.8))
    parts.append(text(rx - 20, y2 + 3, "PARAM_VALUE (idx=0, count=4, 'SYS_ID')", size=11, color=FIELD, anchor="end"))

    # packet 1 (lost!)
    y3 = y2 + 35
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="3,4"/>'
                 % (rx, y3, (lx + rx) / 2 - 30, y3 + 18, POS))
    parts.append(text(rx - 20, y3 + 3, "PARAM_VALUE (idx=1, count=4, 'PILOT_THR_FILT')", size=11, color=POS, anchor="end"))
    parts.append(text((lx + rx) / 2 - 20, y3 + 26, "✗ втрачено в радіоефірі", size=11, color=POS, bold=True, anchor="start"))

    # packet 2 (ok)
    y4 = y3 + 42
    parts.append(arrow(rx, y4, lx, y4 + 18, color=FIELD, sw=1.8))
    parts.append(text(rx - 20, y4 + 3, "PARAM_VALUE (idx=2, count=4, 'BATT_CAPACITY')", size=11, color=FIELD, anchor="end"))

    # packet 3 (ok)
    y5 = y4 + 35
    parts.append(arrow(rx, y5, lx, y5 + 18, color=FIELD, sw=1.8))
    parts.append(text(rx - 20, y5 + 3, "PARAM_VALUE (idx=3, count=4, 'RTL_ALT')", size=11, color=FIELD, anchor="end"))

    # Блок аналізу дірок на GCS
    y_detect = y5 + 35
    box_gcs = fitbox(lx - 160, y_detect, 220, 64,
                     "GCS аналізує бітову маску:\nотримано [0, 2, 3], бракує [1]\n→ таймаут потоку вичерпано",
                     size=11, fill="#fff6e5", stroke="#d97706", sw=1.5)
    parts.append(box_gcs)

    # 3. Точковий дозапит за індексом
    y6 = y_detect + 75
    parts.append(arrow(lx, y6, rx, y6 + 20, color=NEG, sw=2))
    parts.append(text(lx + 20, y6 + 3, "PARAM_REQUEST_READ (param_index=1)", size=12, color=NEG, bold=True, anchor="start"))

    # 4. Повторна відповідь
    y7 = y6 + 45
    parts.append(arrow(rx, y7, lx, y7 + 20, color=FIELD, sw=2))
    parts.append(text(rx - 20, y7 + 3, "PARAM_VALUE (idx=1, count=4, 'PILOT_THR_FILT')", size=11, color=FIELD, bold=True, anchor="end"))

    # Фінальний статус
    y_fin = y7 + 35
    parts.append(rect(lx - 140, y_fin, 280, 28, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(lx, y_fin + 18, "✓ Всі 4 параметри отримано: СИНХРОНІЗОВАНО", size=11, color=FIELD, bold=True))

    render("img/param-tree-download.svg", W, H, *parts,
           title="Синхронізація дерева параметрів: виявлення та закриття прогалин (Missing Indices)")


# ── Фігура 3: зміна параметра та надійне підтвердження (PARAM_SET) ────────────
def fig_param_set_ack():
    W, H = 940, 480
    parts = []

    lx, rx = 200, W - 200
    top = 70

    # Шапки
    parts.append(rect(lx - 120, top - 36, 240, 32, fill="#eef2f7", stroke=INK, sw=2, rx=6))
    parts.append(text(lx, top - 15, "Наземна станція (GCS)", size=13, bold=True))

    parts.append(rect(rx - 100, top - 36, 200, 32, fill="#eef2f7", stroke=INK, sw=2, rx=6))
    parts.append(text(rx, top - 15, "Автопілот (Борт)", size=13, bold=True))

    parts.append(line(lx, top, lx, H - 30, color=MUTED, sw=1.2, dash="3,5"))
    parts.append(line(rx, top, rx, H - 30, color=MUTED, sw=1.2, dash="3,5"))

    # 1. PARAM_SET
    y1 = top + 35
    parts.append(arrow(lx, y1, rx, y1 + 22, color=INK, sw=2))
    parts.append(text(lx + 20, y1 + 3, "PARAM_SET (id='RTL_ALT', val=30.0f, type=REAL32)", size=12, color=INK, bold=True, anchor="start"))

    # Дії на борту
    y_act = y1 + 35
    box_ap = fitbox(rx - 60, y_act, 220, 60,
                    "Перевірка діапазону (10..100)\nЗапис у RAM та Flash/FRAM\nОновлення хешу конфігурації",
                    size=11, fill="#f3e8ff", stroke="#7c3aed", sw=1.5)
    parts.append(box_ap)

    # 2. Відповідь PARAM_VALUE губиться
    y2 = y_act + 75
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="3,4"/>'
                 % (rx, y2, (lx + rx) / 2 - 30, y2 + 18, POS))
    parts.append(text(rx - 20, y2 + 3, "PARAM_VALUE (id='RTL_ALT', val=30.0f)", size=11, color=POS, anchor="end"))
    parts.append(text((lx + rx) / 2 - 20, y2 + 25, "✗ втрачено радіомодемом", size=11, color=POS, bold=True, anchor="start"))

    # 3. Станція фіксує таймаут
    y_to = y2 + 45
    box_to = fitbox(lx - 150, y_to, 200, 50,
                    "Таймаут очікування (1000 мс)\nПідтвердження не надійшло\n→ повторна спроба (Retry 1/3)",
                    size=11, fill="#fff6e5", stroke="#d97706", sw=1.5)
    parts.append(box_to)

    # 4. Повторний PARAM_SET
    y3 = y_to + 65
    parts.append(arrow(lx, y3, rx, y3 + 22, color="#d97706", sw=2))
    parts.append(text(lx + 20, y3 + 3, "PARAM_SET (id='RTL_ALT', val=30.0f) [Повтор]", size=12, color="#d97706", bold=True, anchor="start"))

    # 5. Успішне підтвердження
    y4 = y3 + 45
    parts.append(arrow(rx, y4, lx, y4 + 22, color=FIELD, sw=2))
    parts.append(text(rx - 20, y4 + 3, "PARAM_VALUE (id='RTL_ALT', val=30.0f) [Броадкаст усім GCS]", size=12, color=FIELD, bold=True, anchor="end"))

    # Фіксація на GCS
    y_commit = y4 + 35
    parts.append(rect(lx - 130, y_commit, 260, 28, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(lx, y_commit + 18, "✓ Значення підтверджено: інтерфейс оновлено", size=11, color=FIELD, bold=True))

    render("img/param-set-ack.svg", W, H, *parts,
           title="Цикл запису параметра (PARAM_SET): гарантована доставка та обробка втрати луни")


# ── Фігура 4: прискорення синхронізації через хешування (Param Hash / CRC) ─────
def fig_param_hash_sync():
    W, H = 940, 460
    parts = []

    # Верхній блок: порівняння двох підходів
    # Ліва колонка: Класичний підхід (Full Download)
    parts.append(rect(50, 80, 400, 340, fill="#fffaf0", stroke="#d97706", sw=2, rx=8))
    parts.append(text(250, 110, "Класичний обмін без хешу", size=14, bold=True, color="#d97706"))
    parts.append(text(250, 132, "Передача кожного параметра щоразу", size=11, color=MUTED))

    classic_lines = [
        "1. GCS шле PARAM_REQUEST_LIST",
        "2. Автопілот шле 2000 пакетів PARAM_VALUE",
        "3. Обсяг даних: 2000 × 37 байтів ≈ 74 кБ",
        "4. Швидкість каналу: 57.6 кбіт/с (≈ 5 кБ/с)",
        "5. Затримка старту: 15–20 СЕКУНД",
        "6. Ризик: втрата 10–20% пакетів у повітрі,",
        "   тривалий цикл дозапиту дірок",
    ]
    yy = 165
    for cln in classic_lines:
        parts.append(text(75, yy, cln, size=12, color=INK, anchor="start"))
        yy += 24

    parts.append(rect(75, 360, 350, 40, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    parts.append(text(250, 385, "✗ Високе навантаження радіоканалу", size=12, color=POS, bold=True))

    # Права колонка: Хешований кеш (Param Hash / CRC32)
    parts.append(rect(490, 80, 400, 340, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    parts.append(text(690, 110, "Оптимізація: Хеш конфігурації", size=14, bold=True, color=FIELD))
    parts.append(text(690, 132, "Локальний кеш GCS + перевірка CRC", size=11, color=MUTED))

    hash_lines = [
        "1. GCS шле запит хешу (PARAM_HASH)",
        "2. Борт рахує CRC32 таблиці параметрів",
        "3. Борт повертає 4-байтовий хеш",
        "4. Порівняння з локальним кешем на диску:",
        "   • Хеш збігся: параметри ідентичні!",
        "     → Завантаження НЕ потрібне (0 мс)",
        "   • Хеш інший: зміна конфігурації",
        "     → Завантаження лише за потреби",
    ]
    yy = 165
    for hln in hash_lines:
        bold_flag = "Хеш збігся" in hln
        col = FIELD if bold_flag else INK
        parts.append(text(515, yy, hln, size=12, color=col, bold=bold_flag, anchor="start"))
        yy += 24

    parts.append(rect(515, 360, 350, 40, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(690, 385, "✓ Миттєва готовність до польоту (< 50 мс)", size=12, color=FIELD, bold=True))

    render("img/param-hash-sync.svg", W, H, *parts,
           title="Порівняння: повне вичитування дерева параметрів проти валідації через хеш (CRC)")


if __name__ == "__main__":
    fig_param_value_layout()
    fig_param_tree_download()
    fig_param_set_ack()
    fig_param_hash_sync()
    print("All figures generated successfully.")
