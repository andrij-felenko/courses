# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_FILL, WARN_STROKE = "#fff6e0", "#caa24a"
GOOD_FILL, GOOD_STROKE = "#eef6ef", FIELD
NEW_FILL, NEW_STROKE = "#eaf0fd", NEG
ERR_FILL, ERR_STROKE = "#fdecea", POS


# ── 1. Піраміда ярусів зберігання ─────────────────────────────────────────────
def fig_storage_tier_pyramid():
    W, H = 820, 480
    p = []

    # Загальна рамка
    p.append(rect(10, 10, 800, 460, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(410, 35, "Ієрархія ярусів зберігання даних: вартість, латентність та обсяг", size=15, color=INK, bold=True))

    # Стовпчик ліворуч: Стрілка вартості та латентності
    p.append(rect(25, 60, 140, 390, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=6))
    p.append(text(95, 82, "Характеристики", size=12, color=MUTED, bold=True))
    p.append(arrow(95, 110, 95, 420, color=MUTED, sw=1.5))
    p.append(text(95, 125, "Латентність зростає", size=10, color=POS, bold=True))
    p.append(text(95, 140, "від нс до годин", size=10, color=MUTED))
    p.append(text(95, 375, "Вартість падає", size=10, color=FIELD, bold=True))
    p.append(text(95, 390, "від $3 до $0.001/ГБ", size=10, color=MUTED))
    p.append(text(95, 405, "Обсяг зростає (ПБ/ЕБ)", size=10, color=INK))

    # Яруси (Трапеції / Блоки піраміди)
    tiers = [
        {
            "name": "Гарячий ярус (Hot Tier): DRAM / PMEM / NVMe SSD",
            "desc": "Активні транзакції OLTP, кеші, свіжий WAL, робочі набори",
            "lat": "Латентність: < 100 мкс",
            "cost": "Ціна: $0.20 – $3.00 / ГБ·міс",
            "y": 60, "h": 85, "fill": "#fdecea", "stroke": POS, "c_name": POS
        },
        {
            "name": "Теплий ярус (Warm Tier): SATA SSD / Nearline HDD / S3 Standard",
            "desc": "Свіжі аналітичні чанки, логи за 7–30 днів, помірне читання",
            "lat": "Латентність: 1 – 20 мс",
            "cost": "Ціна: $0.02 – $0.08 / ГБ·міс",
            "y": 155, "h": 85, "fill": "#fff6e0", "stroke": "#d4a72c", "c_name": "#b07d0a"
        },
        {
            "name": "Холодний ярус (Cold Tier): S3 Infrequent Access / ZFS zstd",
            "desc": "Історичні партиції, квартальні звіти, запити раз на місяць",
            "lat": "Латентність: 50 – 250 мс",
            "cost": "Ціна: $0.01 – $0.015 / ГБ·міс",
            "y": 250, "h": 85, "fill": "#eaf0fd", "stroke": NEG, "c_name": NEG
        },
        {
            "name": "Архівний ярус (Archive / Deep Cold): S3 Glacier / LTO Tape",
            "desc": "Регуляторний аудит (GDPR/SEC), катастрофічні бекапи (DR)",
            "lat": "Латентність: 3 хвилини – 12 годин",
            "cost": "Ціна: $0.00099 – $0.004 / ГБ·міс",
            "y": 345, "h": 105, "fill": "#f0f4f8", "stroke": "#57606a", "c_name": "#24292f"
        }
    ]

    for t in tiers:
        p.append(rect(180, t["y"], 615, t["h"], fill=t["fill"], stroke=t["stroke"], sw=1.4, rx=6))
        p.append(text(195, t["y"] + 24, t["name"], size=13, color=t["c_name"], bold=True, anchor="start"))
        p.append(text(195, t["y"] + 46, t["desc"], size=11, color=INK, anchor="start"))
        p.append(text(195, t["y"] + 68, t["lat"], size=11, color=MUTED, bold=True, anchor="start"))
        p.append(text(540, t["y"] + 68, t["cost"], size=11, color=MUTED, bold=True, anchor="start"))
        if t["h"] > 90:
            p.append(text(195, t["y"] + 90, "Штрафи: плата за розморожування (Retrieval Fee) та обов'язковий мінімальний строк утримання", size=10, color=POS, italic=True, anchor="start"))

    return render(os.path.join(OUT, "storage-tier-pyramid.svg"), W, H, *p)


# ── 2. Конвеєр міграції чанків та життєвий цикл ───────────────────────────────
def fig_chunk_migration_lifecycle():
    W, H = 840, 430
    p = []

    p.append(rect(10, 10, 820, 410, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(420, 34, "Конвеєр витіснення й міграції блоків даних між ярусами", size=15, color=INK, bold=True))

    # Крок 1: Запис у гарячий ярус
    b1, _, _ = textbox(110, 105, "1. Запис у Hot (NVMe)\nНовий чанк у пам'яті;\nактивне читання/запис;\nS(t) = 1.0 (гарячий)", size=11, color=INK, fill="#fdecea", stroke=POS, sw=1.3, pad=8)
    p.append(b1)
    p.append(arrow(185, 105, 235, 105, color=MUTED, sw=1.5))

    # Крок 2: Оцінка температури та тригер
    b2, _, _ = textbox(320, 105, "2. Охолодження й тригер\nЗгасання звернень S(t);\nHigh Watermark > 85%;\nВибір кандидата LRU", size=11, color=INK, fill="#fff6e0", stroke="#d4a72c", sw=1.3, pad=8)
    p.append(b2)
    p.append(arrow(405, 105, 455, 105, color=MUTED, sw=1.5))

    # Крок 3: Пакування та стиснення
    b3, _, _ = textbox(540, 105, "3. Пакування й компресія\nКонсолідація дрібних рядків;\nКолонковий Parquet / zstd;\nОбчислення хешу BLAKE3", size=11, color=INK, fill="#eaf0fd", stroke=NEG, sw=1.3, pad=8)
    p.append(b3)
    p.append(arrow(625, 105, 675, 105, color=MUTED, sw=1.5))

    # Крок 4: Скидання у Cold
    b4, _, _ = textbox(735, 105, "4. Запис у Warm/Cold\nАсинхронний PUT у S3;\nОчікування 200 OK;\nВерифікація контрольної суми", size=10, color=INK, fill="#f0f4f8", stroke="#57606a", sw=1.3, pad=6)
    p.append(b4)

    # Зворотний перехід униз (стрілка вниз від кроку 4 до кроку 5)
    p.append(arrow(735, 160, 735, 220, color=MUTED, sw=1.5))

    # Крок 5: Атомарне перемикання покажчика метаданих
    b5, _, _ = textbox(735, 275, "5. Атомарний CAS метаданих\nПідміна адреси блоку в каталозі;\nСтатус: MIGRATED;\nПаралельні читачі бачать новий ярус", size=10, color=FIELD, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.4, bold=True, pad=6)
    p.append(b5)
    p.append(arrow(650, 275, 595, 275, color=FIELD, sw=1.5))

    # Крок 6: Звільнення Hot блоку (TRIM)
    b6, _, _ = textbox(470, 275, "6. Звільнення Hot блоку\nВиклик blkdiscard / unmap на NVMe;\nЗниження зайнятості нижче\nLow Watermark (< 70%)", size=11, color=INK, fill="#f6f8fa", stroke="#d0d7de", sw=1.2, pad=8)
    p.append(b6)
    p.append(arrow(345, 275, 290, 275, color=MUTED, sw=1.5))

    # Крок 7: Завершення строку або стирання
    b7, _, _ = textbox(170, 275, "7. Сплив TTL / WORM Lock\nПеревірка Legal Hold;\nОстаточне видалення об'єкта\nабо крипто-шредінг ключа", size=11, color=POS, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.3, bold=True, pad=8)
    p.append(b7)

    # Нижня інформаційна плашка
    p.append(rect(30, 350, 780, 55, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=6))
    p.append(text(420, 372, "Гарантія безперервності читання: під час кроків 2–4 запити спрямовуються на Hot-ярус;", size=11, color=INK))
    p.append(text(420, 392, "після фіксації кроку 5 запити прозоро перенаправляються на Warm/Cold ярус через шлюз читання.", size=11, color=MUTED))

    return render(os.path.join(OUT, "chunk-migration-lifecycle.svg"), W, H, *p)


# ── 3. Крива згасання доступу та штрафна зона читання ─────────────────────────
def fig_rehydration_and_cost_trap():
    W, H = 820, 440
    p = []

    p.append(rect(10, 10, 800, 420, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(410, 34, "Крива звернень за віком даних та пастка передчасного архівування", size=15, color=INK, bold=True))

    # Графік ліворуч: Степенний закон звернень P(t) ~ t^(-alpha)
    p.append(rect(30, 65, 360, 345, fill="#fafbfc", stroke="#e1e4e8", sw=1.0, rx=6))
    p.append(text(210, 90, "Ймовірність звернення P(t) vs Вік даних", size=12, color=INK, bold=True))

    # Осі графіка
    p.append(line(70, 350, 360, 350, color=LINE, sw=1.5))
    p.append(line(70, 350, 70, 115, color=LINE, sw=1.5))
    p.append(text(360, 368, "Час (дні)", size=10, color=MUTED, anchor="end"))
    p.append(text(65, 110, "IOPS", size=10, color=MUTED, anchor="end"))

    # Крива згасання (гіпербола)
    curve_pts = "M 75 130 Q 100 280 150 320 T 350 345"
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" />' % (curve_pts, POS))

    # Зони на графіку
    p.append(rect(75, 120, 60, 230, fill="#fef2f0", stroke="#f5c2c7", sw=1.0, rx=0))
    p.append(text(105, 230, "Hot", size=11, color=POS, bold=True))
    p.append(text(105, 245, "0–14 дн", size=9, color=POS))

    p.append(rect(135, 250, 75, 100, fill="#fffbf0", stroke="#d4a72c", sw=1.0, rx=0))
    p.append(text(172, 290, "Warm", size=11, color="#b07d0a", bold=True))
    p.append(text(172, 305, "15–90 дн", size=9, color="#b07d0a"))

    p.append(rect(210, 310, 140, 40, fill="#f0f4fd", stroke=NEG, sw=1.0, rx=0))
    p.append(text(280, 330, "Cold / Archive (> 90 дн)", size=10, color=NEG, bold=True))

    # Панель праворуч: Штрафна пастка передчасного архівування
    p.append(rect(410, 65, 380, 345, fill="#fffaf9", stroke="#f5c2c7", sw=1.0, rx=6))
    p.append(text(600, 90, "Пастка витрат (Retrieval Penalty Trap)", size=12, color=POS, bold=True))

    c1, _, _ = textbox(600, 145, "Помилка: передчасне витіснення в Glacier\nДані скинуто в архів заради економії на зберіганні,\nале аналітичні запити продовжують сканувати партиції", size=10, color=INK, fill="#ffffff", stroke="#f5c2c7", sw=1.1, pad=6)
    p.append(c1)

    c2, _, _ = textbox(600, 235, "Структура фінансових втрат:\n1. Плата за розморожування ($0.03 – $0.05 / ГБ)\n2. Плата за запити відновлення (Restore Requests)\n3. Штраф за раннє видалення (< 90 / 180 днів)", size=10, color=POS, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.2, bold=True, pad=6)
    p.append(c2)

    c3, _, _ = textbox(600, 340, "Правило точки окупності t*:\nЕкономія на зберіганні перевищує вартість міграції\nй читання лише за умови: частота звернень < f_crit\nі тривалість зберігання > T_min_tier", size=10, color=FIELD, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.2, bold=True, pad=6)
    p.append(c3)

    return render(os.path.join(OUT, "rehydration-and-cost-trap.svg"), W, H, *p)


if __name__ == "__main__":
    fig_storage_tier_pyramid()
    fig_chunk_migration_lifecycle()
    fig_rehydration_and_cost_trap()
    print("Усі фігури згенеровано успішно.")
