# -*- coding: utf-8 -*-
import sys, os

# '..' 4 levels up to reach scripts/ from root/course/embedded/skhovyshche-i-zapyty-do-noho
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. storage-models: Таблиця стану проти сховища часових рядів ───────────────
def fig_storage_models():
    W, H = 960, 480
    p = []

    # Заголовок лівої колонки: Таблиця поточного стану
    p.append(fitbox(30, 20, 430, 440, "", fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(245, 50, "Таблиця поточного стану (Device State)", size=15, color=INK, bold=True))
    p.append(text(245, 72, "Мутабельний знімок: 1 пристрій = 1 рядок", size=11, color=MUTED))

    # Схема таблиці device_state
    tbl_left = [
        ("device_id (PK)", "last_seen", "temp", "relay", "fw_ver"),
        ("node-001", "12:40:02", "21.4", "ON", "v2.1.0"),
        ("node-002", "12:39:58", "19.8", "OFF", "v2.0.4"),
        ("node-003", "12:40:01", "24.1", "ON", "v2.1.0"),
        ("...", "...", "...", "...", "..."),
        ("node-500", "12:39:45", "20.2", "OFF", "v2.1.0"),
    ]
    
    y_t = 95
    row_h = 24
    col_w = [105, 75, 55, 60, 75]
    for row_idx, row in enumerate(tbl_left):
        x_c = 45
        is_hdr = (row_idx == 0)
        bg_col = "#e2e8f0" if is_hdr else ("#ffffff" if row_idx % 2 == 1 else "#f1f5f9")
        for c_idx, val in enumerate(row):
            w_c = col_w[c_idx]
            p.append(rect(x_c, y_t + row_idx * row_h, w_c, row_h, fill=bg_col, stroke="#cbd5e1", sw=1, rx=0))
            p.append(text(x_c + w_c / 2, y_t + row_idx * row_h + 16, val, size=10, color=INK, bold=is_hdr))
            x_c += w_c

    # Характеристики зліва
    p.append(textbox(245, 275, "Операція: INSERT ... ON CONFLICT DO UPDATE (UPSERT)\nОбсяг: O(N) рядків = рівно 500 записів для 500 вузлів\nДоступ: швидкий пошук за PK за < 1 мс\nСценарій: «Який стан парку прямо зараз? Хто офлайн?»", size=11, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2, min_w=390)[0])
    p.append(textbox(245, 395, "Чому не зберігає історію:\nКожен новий відлік перезаписує старий.\nСпроба зберігати історію через UPDATE утворює мертві\nкортежі (dead tuples) і руйнує B-дерево.", size=10, pad=8, fill="#fff1f2", stroke=POS, sw=1.2, color=POS, min_w=390)[0])

    # Заголовок правої колонки: Сховище часових рядів
    p.append(fitbox(490, 20, 440, 440, "", fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(710, 50, "Сховище часових рядів (TSDB / Chunks)", size=15, color=INK, bold=True))
    p.append(text(710, 72, "Апендиксний лог незмінних фактів за часом", size=11, color=MUTED))

    # Схема таблиці telemetry_raw / chunks
    tbl_right = [
        ("time (Timestamp)", "device_id", "temp", "humidity", "volts"),
        ("12:40:00.120", "node-001", "21.4", "45.2", "3.28"),
        ("12:40:00.125", "node-002", "19.8", "51.0", "3.15"),
        ("12:40:02.122", "node-001", "21.4", "45.1", "3.28"),
        ("12:40:02.130", "node-003", "24.1", "42.0", "3.30"),
        ("... 650 млн рядків на місяць ...", "", "", "", ""),
    ]
    y_t = 95
    col_w_r = [115, 80, 55, 65, 55]
    for row_idx, row in enumerate(tbl_right):
        x_c = 505
        is_hdr = (row_idx == 0)
        is_last = (row_idx == 5)
        bg_col = "#e2e8f0" if is_hdr else ("#ffffff" if row_idx % 2 == 1 else "#f1f5f9")
        if is_last:
            p.append(rect(x_c, y_t + row_idx * row_h, sum(col_w_r), row_h, fill="#e0f2fe", stroke="#7dd3fc", sw=1, rx=0))
            p.append(text(x_c + sum(col_w_r) / 2, y_t + row_idx * row_h + 16, row[0], size=10, color=NEG, bold=True))
        else:
            for c_idx, val in enumerate(row):
                w_c = col_w_r[c_idx]
                p.append(rect(x_c, y_t + row_idx * row_h, w_c, row_h, fill=bg_col, stroke="#cbd5e1", sw=1, rx=0))
                p.append(text(x_c + w_c / 2, y_t + row_idx * row_h + 16, val, size=10, color=INK, bold=is_hdr))
                x_c += w_c

    # Характеристики справа
    p.append(textbox(710, 275, "Операція: пакетний INSERT / COPY (тільки додавання)\nОбсяг: O(N · T) = мільйони рядків, гігабайти даних\nДоступ: діапазонні вибірки [T_start, T_end] за індексом\nСценарій: «Дай графік температури node-001 за 30 днів»", size=11, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2, min_w=400)[0])
    p.append(textbox(710, 395, "Чому не шукає поточний стан:\nЗапит «який останній стан усіх вузлів» змушений сканувати\nмільйони точок через SELECT DISTINCT ON, що кладе диск\nна 100% I/O і триває десятки секунд.", size=10, pad=8, fill="#fef3c7", stroke="#d97706", sw=1.2, color="#92400e", min_w=400)[0])

    render(os.path.join(OUT, "storage-models.svg"), W, H, *p)


# ── 2. time-partitioning-rollups: Партиціонування та піраміда Rollups ─────────
def fig_time_partitioning_rollups():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 28, "Часове партиціонування (Chunks) та багаторівневі агрегати (Rollups)", size=16, color=INK, bold=True))

    # Верхня частина: Чанки та Partition Pruning
    p.append(fitbox(30, 50, 900, 165, "", fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(50, 75, "Фізичні чанки на диску (розбиття за часом, наприклад 1 доба):", size=12, color=INK, bold=True, anchor="start"))

    # Чанки
    chunks = [
        ("Чанк #1 (10 травня)", "Старий чанк (стиснутий)\n21.6 млн точок (95 МБ)", "#f1f5f9", "#94a3b8", False),
        ("Чанк #2 (11 травня)", "Цільовий чанк вибірки\nПопадає в діапазон WHERE", "#dbeafe", NEG, True),
        ("Чанк #3 (12 травня)", "Поточний гарячий чанк\nВідкритий для активного запису", "#dcfce7", FIELD, False),
    ]

    for i, (title, desc, fill_c, stroke_c, active) in enumerate(chunks):
        cx = 175 + i * 290
        p.append(rect(cx - 130, 95, 260, 75, fill=fill_c, stroke=stroke_c, sw=2 if active else 1.2, rx=6))
        p.append(text(cx, 118, title, size=12, color=INK, bold=True))
        p.append(mtext(cx, 140, desc, size=10, color=MUTED, lh=1.25))

    # Стрілка запиту з відсіканням
    p.append(textbox(465, 195, "Запит: SELECT * WHERE time >= '2026-05-11 00:00' AND time < '2026-05-11 23:59'\nПланувальник робить Partition Pruning: Чанк #1 і Чанк #3 повністю пропускаються без читання з диска!", size=10, pad=6, fill="#eff6ff", stroke=NEG, sw=1, color=NEG, min_w=860)[0])

    # Нижня частина: Піраміда Rollups та Retention
    p.append(fitbox(30, 230, 900, 230, "", fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(50, 255, "Піраміда утримання (Retention) та безшовні агрегати (Continuous Aggregates):", size=12, color=INK, bold=True, anchor="start"))

    tiers = [
        ("Рівень 0: Сирі дані (Raw)", "1 відлік / 2 сек", "7 днів", "DROP CHUNK (O(1) без DELETE)", "#fee2e2", POS),
        ("Рівень 1: 1-хвилинні бакети", "avg, min, max, count", "30 днів", "Зменшення обсягу в 30 разів", "#fed7aa", "#ea580c"),
        ("Рівень 2: 1-годинні бакети", "avg, min, max, count", "1 рік", "Зменшення обсягу в 1800 разів", "#fef08a", "#ca8a04"),
        ("Рівень 3: 1-добові бакети", "avg, min, max, count", "5 років", "1 рядок на пристрій на добу", "#bbf7d0", FIELD),
    ]

    y_tier = 275
    for i, (name, res, ret, effect, fill_c, stroke_c) in enumerate(tiers):
        y_pos = y_tier + i * 36
        p.append(rect(50, y_pos, 220, 30, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        p.append(text(160, y_pos + 19, name, size=11, color=INK, bold=True))

        p.append(rect(280, y_pos, 160, 30, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        p.append(text(360, y_pos + 19, res, size=10, color=INK))

        p.append(rect(450, y_pos, 120, 30, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        p.append(text(510, y_pos + 19, "Зберігання: " + ret, size=10, color=INK, bold=True))

        p.append(rect(580, y_pos, 330, 30, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        p.append(text(745, y_pos + 19, effect, size=10, color=MUTED))

    p.append(textbox(480, 435, "Автоматичне видалення: старі сирі чанки викидаються через системний виклик файлової системи за 1 мс.\nАгрегати залишаються в окремих матеріалізованих таблицях, забезпечуючи миттєві річні графіки.", size=10, pad=6, fill="#ffffff", stroke="#94a3b8", sw=1, min_w=860)[0])

    render(os.path.join(OUT, "time-partitioning-rollups.svg"), W, H, *p)


# ── 3. downsampling-lttb: Збереження піків LTTB проти зрізання середнім ─────────
def fig_downsampling_lttb():
    W, H = 960, 490
    p = []

    p.append(text(W / 2, 26, "Проріджування для графіків: просте середнє (AVG) проти LTTB", size=16, color=INK, bold=True))

    # Верхній графік: Сирий сигнал з аварійним спайком
    p.append(fitbox(30, 50, 435, 190, "", fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(50, 72, "1. Сирий сигнал (10 000 точок): аварійний сплеск температури", size=11, color=INK, bold=True, anchor="start"))
    p.append(line(50, 195, 440, 195, color="#cbd5e1", sw=1.2)) # вісь X
    p.append(line(50, 85, 50, 195, color="#cbd5e1", sw=1.2))   # вісь Y

    # Малювання форми сирого сигналу: плато 20C, раптовий спайк до 85C на x=240, плато 20C
    raw_pts = [
        (50, 175), (80, 174), (110, 176), (140, 174), (170, 175), (200, 174),
        (220, 175), (235, 170), (240, 95), (245, 170), (260, 175), (290, 174),
        (320, 176), (350, 175), (380, 174), (410, 175), (440, 175)
    ]
    pts_str = " ".join("%.1f,%.1f" % pt for pt in raw_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pts_str, INK))
    p.append(circle(240, 95, 4, fill=POS, stroke=POS, sw=1))
    p.append(text(240, 85, "Пік: 85 °C (тривав 5 с)", size=10, color=POS, bold=True))
    p.append(text(55, 170, "20 °C", size=9, color=MUTED, anchor="start"))

    # Нижній лівий графік: Просте середнє (AVG) у бакетах
    p.append(fitbox(30, 255, 435, 215, "", fill="#fff1f2", stroke=POS, sw=1.2, rx=6))
    p.append(text(50, 277, "2. Наївне середнє за бакетами (Bucket AVG): ПІК ЗРІЗАНО!", size=11, color=POS, bold=True, anchor="start"))
    p.append(line(50, 400, 440, 400, color="#cbd5e1", sw=1.2))
    p.append(line(50, 290, 50, 400, color="#cbd5e1", sw=1.2))

    # Середнє згладжує вузький спайк: спайк 85C тривалістю 5с у бакеті 1 хв дає середнє (20*55 + 85*5)/60 = 25.4C
    avg_pts = [
        (50, 380), (115, 380), (180, 380), (245, 365), (310, 380), (375, 380), (440, 380)
    ]
    pts_avg_str = " ".join("%.1f,%.1f" % pt for pt in avg_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4 2"/>' % (pts_avg_str, POS))
    for pt in avg_pts:
        p.append(circle(pt[0], pt[1], 4, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(245, 355, "Середнє бакета: лише 25.4 °C", size=10, color=POS, bold=True))
    p.append(text(245, 430, "Катастрофа: аварійний перегрів розчинився в середньому,\nінженер бачить плаский нормальний графік і пропускає збій.", size=10, color=POS))

    # Права колонка: LTTB алгоритм
    p.append(fitbox(485, 50, 445, 420, "", fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(505, 75, "3. Алгоритм LTTB (Largest Triangle Three Buckets)", size=13, color=FIELD, bold=True, anchor="start"))

    p.append(line(505, 235, 895, 235, color="#cbd5e1", sw=1.2))
    p.append(line(505, 115, 505, 235, color="#cbd5e1", sw=1.2))

    # LTTB вибирає точку з максимальною площею трикутника: зберігає точний екстремум 85C!
    lttb_pts = [
        (505, 215), (570, 215), (635, 215), (700, 125), (765, 215), (830, 215), (895, 215)
    ]
    pts_lttb_str = " ".join("%.1f,%.1f" % pt for pt in lttb_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts_lttb_str, FIELD))
    for pt in lttb_pts:
        p.append(circle(pt[0], pt[1], 4, fill="#ffffff", stroke=FIELD, sw=2))
    p.append(circle(700, 125, 5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(700, 115, "LTTB зафіксував пік: 85.0 °C!", size=11, color=FIELD, bold=True))

    # Геометрична суть LTTB
    p.append(textbox(705, 310, "Принцип роботи LTTB:\n1. Діапазон ділиться на K бакетів за кількістю пікселів екрана.\n2. Для кожного бакета вибирається точка, яка утворює трикутник\n   найбільшої площі з вибраною точкою попереднього бакета\n   та середньою точкою наступного.\n3. Результат: екстремуми та форма зберігаються ідеально.", size=10, pad=8, fill="#ffffff", stroke="#86efac", sw=1, min_w=415)[0])

    p.append(textbox(705, 415, "Висновок для дашбордів:\nДля 1200 px екрана LTTB зменшує 1 000 000 сирих точок\nдо 1200 точок за 15 мс без втрати жодного піку чи аномалії.", size=10, pad=6, fill="#dcfce7", stroke=FIELD, sw=1, color="#14532d", bold=True, min_w=415)[0])

    render(os.path.join(OUT, "downsampling-lttb.svg"), W, H, *p)


def main():
    fig_storage_models()
    fig_time_partitioning_rollups()
    fig_downsampling_lttb()
    print("Figures generated successfully in", OUT)


if __name__ == "__main__":
    main()
