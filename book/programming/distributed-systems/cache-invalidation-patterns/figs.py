# -*- coding: utf-8 -*-
"""Фігури теми «Патерни інвалідації». Вивід — ./img/*.svg"""
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

# ── 1. tag-based-invalidation: Інвертований індекс тегів та групове очищення ───
def fig_tag_based_invalidation():
    W, H = 1020, 480
    f = []

    # Ліва колонка: Подія мутації сутності
    x_evt = 110
    y_evt = 240
    f.append(fitbox(x_evt - 80, y_evt - 55, 160, 110,
                    "Мутація в БД:\nЗміна товару #42\n(нова ціна / опис)",
                    size=12, bold=True, fill=GREEN_F, stroke=FIELD, sw=2))

    # Стрілка від мутації до тегу
    f.append(arrow(x_evt + 80, y_evt, 280, y_evt, color=POS, sw=2))
    f.append(textbox(235, y_evt - 18, "PURGE", size=10, bold=True, fill=RED_F, stroke=POS, pad=4)[0])

    # Середня колонка: Інвертований індекс тегів
    x_tag = 360
    f.append(fitbox(x_tag - 80, 50, 160, 40, "Індекс тегів", size=12, bold=True, fill=FILL, stroke=LINE))

    y_t1 = 130
    y_t2 = 240
    y_t3 = 350

    f.append(fitbox(x_tag - 80, y_t1 - 25, 160, 50, "Тег: `brand:apple`", size=11, bold=True, fill=FILL, stroke=MUTED))
    f.append(fitbox(x_tag - 80, y_t2 - 25, 160, 50, "Тег: `item:42`\n(ЦІЛЬОВА ІНВАЛІДАЦІЯ)", size=11, bold=True, fill=RED_F, stroke=POS, sw=2))
    f.append(fitbox(x_tag - 80, y_t3 - 25, 160, 50, "Тег: `cat:laptops`", size=11, bold=True, fill=FILL, stroke=MUTED))

    # Права колонка: Кешовані сторінки / ключі
    x_keys = 800
    y_k1 = 90
    y_k2 = 180
    y_k3 = 270
    y_k4 = 360

    f.append(fitbox(x_keys - 160, y_k1 - 22, 320, 44, "GET `/product/42` (картка товару)", size=11, bold=True, fill=RED_F, stroke=POS))
    f.append(fitbox(x_keys - 160, y_k2 - 22, 320, 44, "GET `/catalog/laptops?p=1` (видача)", size=11, bold=True, fill=RED_F, stroke=POS))
    f.append(fitbox(x_keys - 160, y_k3 - 22, 320, 44, "GET `/api/cart/user:101` (кошик)", size=11, bold=True, fill=RED_F, stroke=POS))
    f.append(fitbox(x_keys - 160, y_k4 - 22, 320, 44, "GET `/product/99` (інший товар)", size=11, bold=True, fill=BLUE_F, stroke=NEG))

    # Зв'язки між цільовим тегом `item:42` та ключами
    f.append(arrow(x_tag + 80, y_t2 - 15, x_keys - 160, y_k1, color=POS, sw=1.8))
    f.append(arrow(x_tag + 80, y_t2, x_keys - 160, y_k2, color=POS, sw=1.8))
    f.append(arrow(x_tag + 80, y_t2 + 15, x_keys - 160, y_k3, color=POS, sw=1.8))

    # Зв'язки нейтральних тегів (пунктир)
    f.append(line(x_tag + 80, y_t1, x_keys - 160, y_k1, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(x_tag + 80, y_t3, x_keys - 160, y_k2, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(x_tag + 80, y_t1, x_keys - 160, y_k4, color=MUTED, sw=1.2, dash="3,3"))

    # Підсумок унизу
    f.append(fitbox(60, 420, 900, 42,
                    "Інвертований індекс транслює інвалідацію однієї сутності в одночасне видалення всіх пов'язаних ключів.",
                    size=12, fill=FILL, stroke=LINE, pad=6))

    render(out("tag-based-invalidation.svg"), W, H, *f,
           title="Інвертований індекс тегів (Surrogate Keys) для групової інвалідації")


# ── 2. version-generation-invalidation: Інвалідація версійними епохами ─────────
def fig_version_generation_invalidation():
    W, H = 1020, 470
    f = []

    # Ліва панель: Лічильник версій (Версійне дерево)
    x_ver = 200
    f.append(fitbox(x_ver - 120, 50, 240, 42, "Глобальний лічильник епохи", size=12, bold=True, fill=FILL, stroke=LINE))

    # Стан лічильника до і після
    f.append(fitbox(x_ver - 110, 130, 220, 60, "Попередня епоха:\n`gen:tenant_42 = 1`", size=12, bold=True, fill=BLUE_F, stroke=NEG))
    f.append(arrow(x_ver, 190, x_ver, 260, color=POS, sw=2.5))
    f.append(textbox(x_ver + 60, 225, "INCR (O(1))", size=10, bold=True, fill=RED_F, stroke=POS, pad=4)[0])
    f.append(fitbox(x_ver - 110, 260, 220, 60, "Нова актуальна епоха:\n`gen:tenant_42 = 2`", size=12, bold=True, fill=GREEN_F, stroke=FIELD, sw=2))

    # Права панель: Простір ключів у кеші
    x_cache = 680
    f.append(fitbox(x_cache - 240, 50, 480, 42, "Сховище ключів (Redis / Memcached)", size=12, bold=True, fill=FILL, stroke=LINE))

    # Старі ключі (покинуті в пам'яті, недосяжні)
    f.append(fitbox(x_cache - 230, 120, 460, 80,
                    "Ключі епохи v1 (Миттєво застаріли, стануть CACHE_MISS):\n"
                    "• `t42:v1:user:1` | `t42:v1:orders` | `t42:v1:settings`\n"
                    "Стан: Не видаляються фізично, звільняться за природним TTL / LRU",
                    size=10, fill=RED_F, stroke=POS, pad=6))

    # Нові ключі (епоха v2)
    f.append(fitbox(x_cache - 230, 250, 460, 80,
                    "Ключі епохи v2 (Свіжі записи після промаху й оновлення):\n"
                    "• `t42:v2:user:1` | `t42:v2:orders` | `t42:v2:settings`\n"
                    "Стан: Усі наступні читачі автоматично формують запити з префіксом v2",
                    size=10, fill=GREEN_F, stroke=FIELD, sw=1.5, pad=6))

    # Стрілки маршрутизації ключів
    f.append(line(x_ver + 110, 160, x_cache - 230, 160, color=MUTED, sw=1.5, dash="4,4"))
    f.append(arrow(x_ver + 110, 290, x_cache - 230, 290, color=FIELD, sw=2))

    # Підсумок унизу
    f.append(fitbox(60, 395, 900, 45,
                    "Інкремент одного лічильника версії за O(1) робить мільйони ключів недосяжними без сканування пам'яті.",
                    size=12, fill=FILL, stroke=LINE, pad=6))

    render(out("version-generation-invalidation.svg"), W, H, *f,
           title="Інвалідація простору імен через версійні епохи (Generation Bumping)")


# ── 3. cdc-log-invalidation: Конвеєр інвалідації на базі CDC ──────────────────
def fig_cdc_log_invalidation():
    W, H = 1020, 460
    f = []

    # 4 послідовні блоки конвеєра: База даних (WAL) -> CDC конектор -> Черга подій -> Споживач інвалідації -> Кеш
    y_box = 180

    x1 = 120
    x2 = 330
    x3 = 540
    x4 = 750
    x5 = 930

    # 1. БД + WAL
    f.append(fitbox(x1 - 80, y_box - 50, 160, 100,
                    "Первинна БД\n(PostgreSQL / MySQL)\n\nCOMMIT → WAL",
                    size=11, bold=True, fill=GREEN_F, stroke=FIELD, sw=2))

    # 2. CDC Engine
    f.append(fitbox(x2 - 70, y_box - 45, 140, 90,
                    "CDC-агент\n(Debezium / Canal)\n\nЧитає журнал WAL",
                    size=11, bold=True, fill=FILL, stroke=LINE))

    # 3. Message Broker
    f.append(fitbox(x3 - 70, y_box - 45, 140, 90,
                    "Брокер подій\n(Kafka / Redis Stream)\n\nТопік: `db-changes`",
                    size=11, bold=True, fill=BLUE_F, stroke=NEG))

    # 4. Invalidation Worker
    f.append(fitbox(x4 - 70, y_box - 45, 140, 90,
                    "Воркер інвалідації\n\nМапінг таблиць\nу ключі / теги",
                    size=11, bold=True, fill=WARN_F, stroke=POS))

    # 5. Кеш
    f.append(fitbox(x5 - 55, y_box - 45, 110, 90,
                    "Кеш\n(Redis / CDN)\n\n`DEL key`\n`PURGE tag`",
                    size=11, bold=True, fill=RED_F, stroke=POS, sw=2))

    # Стрілки між етапами
    f.append(arrow(x1 + 80, y_box, x2 - 70, y_box, color=FIELD, sw=2))
    f.append(textbox((x1 + 80 + x2 - 70) / 2, y_box - 16, "LSN / Binlog", size=9, pad=3)[0])

    f.append(arrow(x2 + 70, y_box, x3 - 70, y_box, color=LINE, sw=2))
    f.append(textbox((x2 + 70 + x3 - 70) / 2, y_box - 16, "JSON / Avro", size=9, pad=3)[0])

    f.append(arrow(x3 + 70, y_box, x4 - 70, y_box, color=NEG, sw=2))
    f.append(textbox((x3 + 70 + x4 - 70) / 2, y_box - 16, "Асинхронно", size=9, pad=3)[0])

    f.append(arrow(x4 + 70, y_box, x5 - 55, y_box, color=POS, sw=2))
    f.append(textbox((x4 + 70 + x5 - 55) / 2, y_box - 16, "Purge", size=9, bold=True, pad=3)[0])

    # Блок переваг внизу
    f.append(fitbox(60, 360, 900, 60,
                    "Переваги CDC-інвалідації:\n"
                    "1. Повне усунення проблеми подвійного запису (Dual-Write) — джерелом правди є журнал транзакцій.\n"
                    "2. Застосунок звільняється від оркестрації кешу: відкат або збій транзакції не призводить до розсинхронізації.",
                    size=11, fill=FILL, stroke=LINE, pad=6))

    render(out("cdc-log-invalidation.svg"), W, H, *f,
           title="Конвеєр інвалідації на основі захоплення змін даних (CDC / Log Tailing)")


# ── 4. delayed-double-delete: Відкладене подвійне видалення ─────────────────────
def fig_delayed_double_delete():
    W, H = 1020, 480
    f = []

    # 4 актори: Клієнт-записувач, Майстер БД, Репліка БД, Кеш
    x_w = 120
    x_m = 380
    x_r = 640
    x_c = 900

    f.append(fitbox(x_w - 60, 50, 120, 38, "Записувач", size=12, bold=True, fill=FILL, stroke=LINE))
    f.append(fitbox(x_m - 60, 50, 120, 38, "Майстер БД", size=12, bold=True, fill=GREEN_F, stroke=FIELD))
    f.append(fitbox(x_r - 60, 50, 120, 38, "Репліка БД", size=12, bold=True, fill=FILL, stroke=MUTED))
    f.append(fitbox(x_c - 60, 50, 120, 38, "Кеш (Redis)", size=12, bold=True, fill=BLUE_F, stroke=NEG))

    # Вертикальні лінії
    y_top = 88
    y_bot = 420
    for x in (x_w, x_m, x_r, x_c):
        f.append(line(x, y_top, x, y_bot, color=MUTED, sw=1.2, dash="4,4"))

    # Крок 1: Перше видалення з кешу
    y1 = 120
    f.append(arrow(x_w, y1, x_c, y1, color=POS, sw=1.8))
    f.append(textbox(510, y1 - 15, "1. Перше видалення: `DEL key`", size=10, bold=True, pad=4, fill=RED_F, stroke=POS)[0])

    # Крок 2: Запис у Майстер
    y2 = 170
    f.append(arrow(x_w, y2, x_m, y2, color=FIELD, sw=2))
    f.append(textbox((x_w + x_m) / 2, y2 - 15, "2. UPDATE v₂ (commit)", size=10, bold=True, pad=4, fill=GREEN_F, stroke=FIELD)[0])

    # Крок 3: Реплікація на репліку (з затримкою!)
    y3_start = 180
    y3_end = 320
    f.append(arrow(x_m, y3_start, x_r, y3_end, color=MUTED, sw=1.8))
    f.append(textbox((x_m + x_r) / 2 + 10, 240, "Реплікаційний лаг (Δt_lag)", size=10, pad=3)[0])

    # Небезпечний момент: паралельний читач читає зі старої репліки й повертає старе v1 у кеш
    y_race = 270
    f.append(fitbox(670, y_race - 18, 200, 36, "Паралельний читач:\nчитає зі старої репліки v₁ → кеш!",
                    size=9, bold=True, fill=RED_F, stroke=POS))

    # Крок 4: Відкладене друге видалення після паузи (T_delay > Δt_lag)
    y4 = 370
    f.append(arrow(x_w, y4, x_c, y4, color=FIELD, sw=2.2))
    f.append(textbox(510, y4 - 15, "3. Друге видалення (через T_delay): `DEL key` (зачищає отруєний стан)",
                     size=10, bold=True, pad=4, fill=GREEN_F, stroke=FIELD)[0])

    # Пояснення знизу
    f.append(fitbox(60, 435, 900, 36,
                    "Відкладене повторне видалення гарантує зачистку кешу навіть якщо запізнілий читач підтягнув дані з відсталої репліки.",
                    size=11, fill=FILL, stroke=LINE, pad=4))

    render(out("delayed-double-delete.svg"), W, H, *f,
           title="Відкладене подвійне видалення (Delayed Double-Delete) для компенсації лагу реплікації")


if __name__ == "__main__":
    fig_tag_based_invalidation()
    fig_version_generation_invalidation()
    fig_cdc_log_invalidation()
    fig_delayed_double_delete()
    print("All figures generated successfully.")
