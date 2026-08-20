# -*- coding: utf-8 -*-
"""Фігури теми «Кеш вводить друге джерело правди (ціна)». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#eaf0fd"
WARN_F  = "#fff3cd"

# ── 1. dual-source-divergence: розходження двох джерел правди у часі ─────────
def fig_dual_source_divergence():
    W, H = 1000, 420
    f = []

    # Лінії часу для трьох акторів: Клієнт, Кеш, БД
    y_cli = 90
    y_cache = 190
    y_db = 290

    # Підписи акторів ліворуч
    b, _, _ = textbox(90, y_cli, "Клієнти\n(Читач / Записувач)", size=12, bold=True, min_w=140, pad=8)
    f.append(b)
    b, _, _ = textbox(90, y_cache, "Кеш\n(Похідний стан)", size=12, bold=True, min_w=140, pad=8, fill=BLUE_F, stroke=NEG)
    f.append(b)
    b, _, _ = textbox(90, y_db, "База даних\n(Канонічна правда)", size=12, bold=True, min_w=140, pad=8, fill=GREEN_F, stroke=FIELD)
    f.append(b)

    # Горизонтальні осі часу
    x_start = 180
    x_end = 940
    f.append(arrow(x_start, y_cli, x_end, y_cli, color=MUTED, sw=1.5))
    f.append(arrow(x_start, y_cache, x_end, y_cache, color=MUTED, sw=1.5))
    f.append(arrow(x_start, y_db, x_end, y_db, color=MUTED, sw=1.5))
    f.append(text(x_end + 20, y_cli + 4, "Час", size=12, italic=True, color=MUTED))

    # Подія 1: Запис у БД (t0)
    t0 = 280
    f.append(arrow(t0, y_cli + 16, t0, y_db - 16, color=FIELD, sw=2))
    f.append(textbox(t0, y_db + 40, "t₀: Запис v₂\n(успішний commit)", size=11, bold=True, pad=6)[0])
    f.append(textbox(t0, y_cli - 30, "Записувач: PUT v₂", size=11, pad=5)[0])

    # Зона розходження між t0 і t2 на лінії кеша
    t1 = 510
    t2 = 750

    # Фонова плашка вікна неузгодженості
    f.append(rect(t0, y_cache - 24, t2 - t0, 48, fill=RED_F, stroke=POS, sw=1.5, rx=4))
    f.append(text((t0 + t2) / 2, y_cache + 4, "Кеш містить старе v₁ (неузгодженість)", size=12, color=POS, bold=True))

    # Подія 2: Читання кеша (t1) — брудне читання
    f.append(arrow(t1, y_cli + 16, t1, y_cache - 24, color=POS, sw=2))
    f.append(textbox(t1, y_cli - 30, "Читач: GET key", size=11, pad=5)[0])
    f.append(arrow(t1 + 10, y_cache - 24, t1 + 10, y_cli + 16, color=POS, sw=2))
    f.append(textbox(t1 + 20, (y_cli + y_cache) / 2, "Відповідь: v₁ ✗\n(застарілі дані)", size=11, bold=True, pad=6, fill=RED_F, stroke=POS)[0])

    # Подія 3: Інвалідація (t2)
    f.append(arrow(t2, y_cli + 16, t2, y_cache - 24, color=NEG, sw=2))
    f.append(textbox(t2, y_cli - 30, "Інвалідація: DEL key", size=11, pad=5)[0])
    f.append(textbox(t2, y_cache + 40, "t₂: Ключ видалено\n(кеш очищено)", size=11, bold=True, pad=6)[0])

    # Позначення вікна розходження Δt знизу
    f.append(line(t0, 370, t2, 370, color=POS, sw=2))
    f.append(line(t0, 362, t0, 378, color=POS, sw=2))
    f.append(line(t2, 362, t2, 378, color=POS, sw=2))
    f.append(text((t0 + t2) / 2, 395, "Вікно застарілості Δt = t₂ − t₀ (два джерела правди розійшлися)",
                  size=13, color=POS, bold=True))

    render(out("dual-source-divergence.svg"), W, H, *f,
           title="Часова шкала розходження канонічної БД та похідного кешу")


# ── 2. stale-read-race: гонка читача й записувача (примарний запис) ──────────
def fig_stale_read_race():
    W, H = 1000, 520
    f = []

    # 4 вертикальні доріжки: Читач (C1), Записувач (C2), Кеш, БД
    x_c1 = 140
    x_cache = 380
    x_db = 640
    x_c2 = 880

    f.append(fitbox(x_c1 - 70, 55, 140, 42, "Читач (C1)", size=13, bold=True, fill=FILL, stroke=LINE))
    f.append(fitbox(x_cache - 70, 55, 140, 42, "Кеш", size=13, bold=True, fill=BLUE_F, stroke=NEG))
    f.append(fitbox(x_db - 70, 55, 140, 42, "База даних", size=13, bold=True, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(x_c2 - 70, 55, 140, 42, "Записувач (C2)", size=13, bold=True, fill=FILL, stroke=LINE))

    # Вертикальні лінії життя
    y_top = 100
    y_bot = 460
    for x in (x_c1, x_cache, x_db, x_c2):
        f.append(line(x, y_top, x, y_bot, color=MUTED, sw=1.2, dash="4,4"))

    # Крок 1: C1 звертається в кеш -> промах
    y1 = 130
    f.append(arrow(x_c1, y1, x_cache, y1, color=LINE, sw=1.8))
    f.append(textbox((x_c1 + x_cache) / 2, y1 - 16, "1. GET key (промах)", size=11, pad=4)[0])

    # Крок 2: C1 читає з БД старе значення v1 (але зависає на мережі / GC)
    y2 = 180
    f.append(arrow(x_c1, y2, x_db, y2, color=LINE, sw=1.8))
    f.append(textbox((x_c1 + x_db) / 2, y2 - 16, "2. SELECT -> отримав v₁ (затримка обробки)", size=11, pad=4)[0])

    # Крок 3: C2 оновлює БД новим значенням v2
    y3 = 240
    f.append(arrow(x_c2, y3, x_db, y3, color=FIELD, sw=2))
    f.append(textbox((x_db + x_c2) / 2, y3 - 16, "3. UPDATE key = v₂ (commit)", size=11, bold=True, pad=4, fill=GREEN_F, stroke=FIELD)[0])

    # Крок 4: C2 інвалідує кеш
    y4 = 295
    f.append(arrow(x_c2, y4, x_cache, y4, color=NEG, sw=2))
    f.append(textbox((x_cache + x_c2) / 2 + 30, y4 - 16, "4. DELETE key (інвалідація)", size=11, bold=True, pad=4, fill=BLUE_F, stroke=NEG)[0])

    # Крок 5: C1 прокидається й записує старе v1 назад у кеш!
    y5 = 370
    f.append(arrow(x_c1, y5, x_cache, y5, color=POS, sw=2.5))
    f.append(textbox((x_c1 + x_cache) / 2, y5 - 18, "5. SET key = v₁ (запізнілий запис!)", size=11, bold=True, pad=5, fill=RED_F, stroke=POS)[0])

    # Підсумок катастрофи внизу
    f.append(fitbox(100, 425, 800, 50,
                    "Результат: у БД лежить актуальне v₂, а в кеш назавжди записано застаріле v₁ (примарний запис).\n"
                    "Усі наступні читачі отримують хибні дані, поки не настане примусовий TTL або новий запис.",
                    size=12, bold=True, fill=RED_F, stroke=POS, sw=2, pad=8))

    render(out("stale-read-race.svg"), W, H, *f,
           title="Гонка застарілого запису: як старий стан отруює кеш після інвалідації")


# ── 3. dependency-fanout: каскад інвалідації та граф залежностей ─────────────
def fig_dependency_fanout():
    W, H = 1000, 440
    f = []

    # Зліва: Первинна сутність
    x_root = 150
    y_root = 210
    f.append(fitbox(x_root - 90, y_root - 35, 180, 70,
                    "Таблиця `products`\n(зміна ціни товару #42)",
                    size=12, bold=True, fill=GREEN_F, stroke=FIELD, sw=2))

    # Середній рівень: Прямі та складені кеші
    x_m = 470
    y_m1 = 80
    y_m2 = 165
    y_m3 = 255
    y_m4 = 340

    f.append(fitbox(x_m - 120, y_m1 - 25, 240, 50, "Кеш картки товару\n`product:42:details`", size=11, bold=True, fill=RED_F, stroke=POS))
    f.append(fitbox(x_m - 120, y_m2 - 25, 240, 50, "Кеш категорії з фільтрами\n`category:electronics:page:1`", size=11, bold=True, fill=RED_F, stroke=POS))
    f.append(fitbox(x_m - 120, y_m3 - 25, 240, 50, "Кошики користувачів\n`user:*:cart_summary`", size=11, bold=True, fill=RED_F, stroke=POS))
    f.append(fitbox(x_m - 120, y_m4 - 25, 240, 50, "Пошуковий індекс / автокомпліт\n`search:prefix:laptop`", size=11, bold=True, fill=RED_F, stroke=POS))

    # Стрілки від кореня до середнього рівня
    f.append(arrow(x_root + 90, y_root - 15, x_m - 120, y_m1 + 5, color=POS, sw=1.8))
    f.append(arrow(x_root + 90, y_root - 5, x_m - 120, y_m2, color=POS, sw=1.8))
    f.append(arrow(x_root + 90, y_root + 5, x_m - 120, y_m3, color=POS, sw=1.8))
    f.append(arrow(x_root + 90, y_root + 15, x_m - 120, y_m4 - 5, color=POS, sw=1.8))

    # Правий рівень: Агрегати верхнього рівня
    x_r = 820
    y_r1 = 120
    y_r2 = 300

    f.append(fitbox(x_r - 110, y_r1 - 30, 220, 60, "Головна сторінка\n(блок «Хіти продажу»)\n`landing:top_deals`", size=11, bold=True, fill=WARN_F, stroke=POS))
    f.append(fitbox(x_r - 110, y_r2 - 30, 220, 60, "Аналітичний звіт\n(денний оборот та маржа)\n`report:daily_revenue`", size=11, bold=True, fill=WARN_F, stroke=POS))

    # Стрілки від середнього до правого
    f.append(arrow(x_m + 120, y_m1, x_r - 110, y_r1 - 10, color=POS, sw=1.5))
    f.append(arrow(x_m + 120, y_m2, x_r - 110, y_r1 + 10, color=POS, sw=1.5))
    f.append(arrow(x_m + 120, y_m3, x_r - 110, y_r2, color=POS, sw=1.5))

    # Підпис проблеми знизу
    f.append(text(W / 2, 405, "Дилема інвалідації: точкове очищення вимагає графа залежностей; очищення за шаблоном руйнує весь кеш.",
                  size=12, italic=True, color=MUTED))

    render(out("dependency-fanout.svg"), W, H, *f,
           title="Віяло залежностей: зміна однієї сутності руйнує дерево похідних кешів")


# ── 4. thundering-herd-lock: захист від лавинного навантаження (stampede) ───
def fig_thundering_herd_lock():
    W, H = 1040, 490
    f = []

    # Ліва колонка: Без захисту (колапс БД)
    w_col = 460
    f.append(fitbox(30, 55, w_col, 390, "", fill=FILL, stroke=LINE))
    f.append(text(30 + w_col / 2, 80, "Без захисту: інвалідація гарячого ключа", size=13, bold=True, color=POS))

    f.append(textbox(30 + w_col / 2, 115, "Гарячий ключ інвалідовано (DEL)", size=11, bold=True, fill=RED_F, stroke=POS, pad=6)[0])

    # 4 клієнти роблять паралельний запит
    for i in range(4):
        y_c = 165 + i * 40
        f.append(textbox(90, y_c, f"Клієнт #{i+1}", size=10, pad=4)[0])
        f.append(arrow(135, y_c, 270, 310, color=POS, sw=1.5))

    f.append(fitbox(270, 310, 190, 90, "База даних:\n1000 паралельних запитів\n💥 Перевантаження / збій",
                    size=11, bold=True, fill=RED_F, stroke=POS, sw=2, pad=6))

    # Права колонка: З координацією (Mutex / Single-Flight / Lease)
    x_r = 530
    f.append(fitbox(x_r, 55, w_col, 390, "", fill=FILL, stroke=LINE))
    f.append(text(x_r + w_col / 2, 80, "З координацією: блокування або ліза", size=13, bold=True, color=FIELD))

    f.append(textbox(x_r + w_col / 2, 115, "Гарячий ключ інвалідовано (DEL)", size=11, bold=True, fill=BLUE_F, stroke=NEG, pad=6)[0])

    # Клієнт 1 бере лізу/замок
    f.append(textbox(x_r + 70, 165, "Клієнт #1", size=10, bold=True, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(textbox(x_r + 200, 165, "Взяв замок / лізу", size=10, bold=True, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(x_r + 110, 165, x_r + 140, 165, color=FIELD, sw=1.5))
    f.append(arrow(x_r + 265, 165, x_r + 340, 310, color=FIELD, sw=2))

    # Клієнти 2..4 чекають або отримують stale-while-revalidate
    for i in range(1, 4):
        y_c = 165 + i * 40
        f.append(textbox(x_r + 70, y_c, f"Клієнт #{i+1}", size=10, pad=4)[0])
        f.append(line(x_r + 110, y_c, x_r + 175, 260, color=MUTED, sw=1.2, dash="3,3"))

    f.append(fitbox(x_r + 175, 235, 140, 50, "Очікують на замок\nабо беруть старе v₁", size=10, fill=WARN_F, stroke=POS, pad=4))

    f.append(fitbox(x_r + 250, 310, 190, 90, "База даних:\nРівно 1 запит на обчислення\n✓ Стабільне навантаження",
                    size=11, bold=True, fill=GREEN_F, stroke=FIELD, sw=2, pad=6))

    f.append(text(W / 2, 465, "Захист від лавини ізолює первинне джерело правди від шквалу промахів під час скидання кешу.",
                  size=12, italic=True, color=MUTED))

    render(out("thundering-herd-lock.svg"), W, H, *f,
           title="Лавина запитів (Cache Stampede) проти координації оновлення (Single-Flight)")


if __name__ == "__main__":
    fig_dual_source_divergence()
    fig_stale_read_race()
    fig_dependency_fanout()
    fig_thundering_herd_lock()
    print("All figures generated successfully.")

