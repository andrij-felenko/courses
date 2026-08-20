# -*- coding: utf-8 -*-
"""Генератор схем для теми «Дизайн ключів і гарячі ключі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / перевантаження / гарячий стан
COOL = "#eaf0fd"   # холодний / нейтральний / нормальний стан
GOOD = "#e8f6ee"   # баланс / успіх / оптимізація
ACCENT = "#fef9e7" # підсвічування / буфер / метадані

# ── 1. Анатомія та структура ключа кешування ────────────────────────────────
def fig_key_structure():
    W, H = 1080, 520
    f = []

    f.append(fitbox(40, 20, 1000, 42,
                    "Анатомія ключа кешу: ієрархічний простір імен, хеш-теги та накладні витрати пам'яті",
                    size=14, bold=True, fill=COOL))

    # Складові частини ключа
    f.append(rect(40, 78, 1000, 190, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(60, 92, 960, 30, "Канонічна структура рядка ключа: service:tenant:entity:id:{slot}:v2:hash", size=12, bold=True, fill=ACCENT))

    # Сегменти
    f.append(fitbox(60, 136, 115, 62, "Префікс сервісу\n\norders", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(text(182, 167, ":", size=18, bold=True, color=MUTED))

    f.append(fitbox(190, 136, 120, 62, "Орендар (Tenant)\n\nua_corp", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(text(317, 167, ":", size=18, bold=True, color=MUTED))

    f.append(fitbox(325, 136, 120, 62, "Сутність\n\ninvoice", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(text(452, 167, ":", size=18, bold=True, color=MUTED))

    f.append(fitbox(460, 136, 120, 62, "Ідентифікатор\n\n849201", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(text(587, 167, ":", size=18, bold=True, color=MUTED))

    f.append(fitbox(595, 136, 150, 62, "Хеш-тег слота\n\n{shard_group_A}", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(text(752, 167, ":", size=18, bold=True, color=MUTED))

    f.append(fitbox(760, 136, 115, 62, "Версія схеми\n\nv2", size=11, bold=True, fill=WARM, stroke=POS))
    f.append(text(882, 167, ":", size=18, bold=True, color=MUTED))

    f.append(fitbox(890, 136, 130, 62, "Фільтр-хеш\n\nx7a9f4c1", size=11, bold=True, fill=ACCENT, stroke=LINE))

    f.append(fitbox(60, 210, 960, 46, "Призначення сегментів: ізоляція орендарів запобігає витоку даних між клієнтами; версія v2 унеможливлює збої десеріалізації;\nхеш-тег {..} закріплює зв'язані сутності за одним слотом Redis; компактний хеш замінює довгі параметри запиту.", size=10, fill=FILL, stroke=MUTED))

    # Накладні витрати пам'яті в Redis
    f.append(rect(40, 282, 1000, 218, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(60, 296, 960, 28, "Накладні витрати пам'яті Redis на кожен ключ у хеш-таблиці (dictEntry)", size=12, bold=True, fill=COOL))

    f.append(fitbox(60, 336, 220, 110, "dictEntry (24 байти)\n\n• *key (8 байтів)\n• *val (8 байтів)\n• *next (8 байтів)\nВирівнювання jemalloc: 32 Б", size=10, fill=WARM, stroke=POS))

    f.append(arrow(280, 370, 320, 370, color=LINE, sw=1.5))
    f.append(arrow(280, 420, 320, 420, color=LINE, sw=1.5))

    f.append(fitbox(320, 336, 290, 60, "robj ключа (16 байтів)\n\ntype(4b) + encoding(4b) + lru(24b)\nrefcount(4B) + *ptr(8B)", size=10, fill=ACCENT, stroke=LINE))

    f.append(fitbox(320, 404, 290, 60, "robj значення (16 байтів)\n\nМетадані об'єкта та вказівник на дані\nВирівнювання jemalloc: 16 Б", size=10, fill=ACCENT, stroke=LINE))

    f.append(arrow(610, 366, 650, 366, color=LINE, sw=1.5))

    f.append(fitbox(650, 336, 370, 145, "SDS заголовок + рядок ключа (sdshdr8)\n\nlen(1B) + alloc(1B) + flags(1B) + buf[] + null(1B)\n\nДовгий ключ (120 Б) -> виділення jemalloc 160 Б\nКомпактний ключ (24 Б) -> виділення jemalloc 32 Б\nЕкономія на 50 млн ключів: 50M * 128 Б = 6.4 ГБ RAM!", size=10, bold=False, fill=GOOD, stroke=FIELD))

    return render(os.path.join(OUT, 'key-structure-namespace.svg'), W, H, *f)


# ── 2. Дисбаланс кластера через гарячий ключ ────────────────────────────────
def fig_hotkey_imbalance():
    W, H = 1080, 560
    f = []

    f.append(fitbox(40, 20, 1000, 42,
                    "Криза гарячого ключа: деградація шардованого кластера при нерівномірному трафіку",
                    size=14, bold=True, fill=COOL))

    # Ліва частина: Вхідний потік
    f.append(rect(40, 78, 300, 460, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 92, 270, 32, "Клієнтський трафік (100k req/s)", size=11, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(55, 136, 270, 65, "95 000 req/s (95%)\nГарячий ключ: product:flash_deal\n(Розподіл Ціпфа: alpha = 1.3)", size=10, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(55, 215, 270, 50, "5 000 req/s (5%)\nМільйони звичайних ключів\n(Холодний хвіст запитів)", size=10, fill=COOL, stroke=LINE))

    f.append(fitbox(55, 280, 270, 120, "Шардування за хешем:\nSlot = CRC16(key) mod 16384\n\nproduct:flash_deal\n  -> Slot 12431 -> Вузол 14\n\nУвесь трафік 95k req/s б'є\nв ОДИН фізичний сокет!", size=10, fill=ACCENT, stroke=LINE))

    f.append(fitbox(55, 415, 270, 110, "Каскадний ефект:\n1. 100% CPU на Вузлі 14\n2. Затримка: 1мс -> 4000мс\n3. Таймаут клієнтів і повтори\n4. Відмова репліки після фейловера", size=10, fill=WARM, stroke=POS))

    # Права частина: Стан вузлів кластера
    f.append(rect(360, 78, 680, 460, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(375, 92, 650, 32, "Стан 64 вузлів кластера Redis: тотальний перекіс навантаження", size=11, bold=True, fill=COOL))

    # Стрілки від трафіку до вузлів
    f.append(arrow(325, 168, 385, 175, color=POS, sw=3.0))
    f.append(arrow(325, 240, 385, 330, color=FIELD, sw=1.2))
    f.append(arrow(325, 240, 385, 430, color=FIELD, sw=1.2))

    # Вузол 14 (Гарячий)
    f.append(rect(385, 136, 630, 125, fill=WARM, stroke=POS, sw=2.0))
    f.append(fitbox(400, 148, 600, 26, "ВУЗОЛ 14 (Слоти 12000..12500) — КРИТИЧНЕ ПЕРЕВАНТАЖЕННЯ", size=11, bold=True, fill=WARM, color=POS))
    f.append(fitbox(400, 180, 185, 70, "Навантаження:\n95 000 req/s\n\nCPU: 100% (1 core)", size=10, bold=True, fill=BG, stroke=POS))
    f.append(fitbox(595, 180, 200, 70, "Мережевий буфер:\nЧерга TCP заповнена\nДропи пакетів SYN", size=10, fill=BG, stroke=POS))
    f.append(fitbox(805, 180, 195, 70, "Затримка P99:\n> 4500 мс\n(Крах сервісу)", size=10, bold=True, fill=BG, color=POS, stroke=POS))

    # Інші вузли (Холодні)
    f.append(rect(385, 280, 630, 100, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(fitbox(400, 292, 600, 24, "ВУЗЛИ 1..13 (Слоти 0..11999) — НЕДОЗАВАНТАЖЕНІ", size=10, bold=True, fill=GOOD))
    f.append(fitbox(400, 322, 185, 48, "Навантаження: ~80 req/s\nCPU: 1.5%", size=10, fill=BG, stroke=FIELD))
    f.append(fitbox(595, 322, 200, 48, "Мережа: 0.1% смуги\nЧерга: 0 запитів", size=10, fill=BG, stroke=FIELD))
    f.append(fitbox(805, 322, 195, 48, "Затримка P99: 0.6 мс\n(Ресурс простоює)", size=10, fill=BG, stroke=FIELD))

    f.append(rect(385, 395, 630, 100, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(fitbox(400, 407, 600, 24, "ВУЗЛИ 15..64 (Слоти 12501..16383) — НЕДОЗАВАНТАЖЕНІ", size=10, bold=True, fill=GOOD))
    f.append(fitbox(400, 437, 185, 48, "Навантаження: ~75 req/s\nCPU: 1.2%", size=10, fill=BG, stroke=FIELD))
    f.append(fitbox(595, 437, 200, 48, "Мережа: 0.1% смуги\nЧерга: 0 запитів", size=10, fill=BG, stroke=FIELD))
    f.append(fitbox(805, 437, 195, 48, "Затримка P99: 0.5 мс\n(Ресурс простоює)", size=10, fill=BG, stroke=FIELD))

    f.append(fitbox(385, 505, 630, 24, "Висновок: масштабування кластера додаванням вузлів НЕ вирішує проблему гарячого ключа!", size=10, bold=True, fill=ACCENT))

    return render(os.path.join(OUT, 'hotkey-cluster-imbalance.svg'), W, H, *f)


# ── 3. Розщеплення ключів (Key Salting / Sharding) ───────────────────────────
def fig_key_salting():
    W, H = 1080, 540
    f = []

    f.append(fitbox(40, 20, 1000, 42,
                    "Розщеплення гарячого ключа (Key Salting): паралелізація читання через рандомізацію суфікса",
                    size=14, bold=True, fill=COOL))

    # Верхній блок: Шлях запису (Write Path)
    f.append(rect(40, 78, 1000, 195, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(60, 90, 960, 28, "ШЛЯХ ЗАПИСУ (Write Path): Розмноження запису на K копій (Fan-out Write, K = 4)", size=11, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(60, 130, 170, 75, "Сервіс-продюсер\n\nОновлення товару\nproduct:9901", size=10, bold=True, fill=COOL, stroke=LINE))

    f.append(arrow(230, 167, 300, 167, color=POS, sw=2.0))

    f.append(fitbox(300, 130, 190, 75, "Генератор копій (Salter)\n\nФормує ключі з суфіксом:\nkey#0, key#1, key#2, key#3", size=10, fill=ACCENT, stroke=LINE))

    for idx, (slot, node, y_pos) in enumerate([(3102, 3, 126), (7840, 15, 156), (11950, 31, 186), (15400, 58, 216)]):
        f.append(arrow(490, 167, 560, y_pos + 10, color=POS, sw=1.3))
        f.append(fitbox(560, y_pos, 460, 24, f"MSET product:9901#{idx} -> Slot {slot} -> Вузол {node} кластера", size=9.5, fill=GOOD, stroke=FIELD))

    f.append(fitbox(60, 218, 430, 44, "Ціна запису: K-кратне зростання трафіку запису та обсягу пам'яті.\nЗастосовується виключно для ключів із переважанням читання (Read-Heavy).", size=9.5, fill=FILL, stroke=MUTED))

    # Нижній блок: Шлях читання (Read Path)
    f.append(rect(40, 290, 1000, 230, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(60, 302, 960, 28, "ШЛЯХ ЧИТАННЯ (Read Path): Рівномірний псевдовипадковий розподіл клієнтських запитів", size=11, bold=True, fill=GOOD, stroke=FIELD))

    f.append(fitbox(60, 342, 170, 100, "100 000 клієнтів\n\nПаралельні запити\nproduct:9901\n(без солі)", size=10, bold=True, fill=COOL, stroke=LINE))

    f.append(arrow(230, 392, 300, 392, color=FIELD, sw=2.0))

    f.append(fitbox(300, 342, 190, 100, "Клієнтський роутер\n\nСіль = rand(0, K-1)\n\nОбирає один із\n4 розщеплених ключів", size=10, fill=ACCENT, stroke=LINE))

    for idx, (slot, node, y_pos) in enumerate([(3102, 3, 340), (7840, 15, 375), (11950, 31, 410), (15400, 58, 445)]):
        f.append(arrow(490, 392, 560, y_pos + 12, color=FIELD, sw=1.6))
        f.append(fitbox(560, y_pos, 460, 28, f"25 000 req/s -> GET product:9901#{idx} (Slot {slot}, Вузол {node}) — CPU 24%", size=10, fill=GOOD, stroke=FIELD))

    f.append(fitbox(60, 482, 960, 28, "Результат: пікове навантаження на один вузол зменшено рівно в K разів (з 100k до 25k req/s). Кластер збалансовано.", size=10.5, bold=True, fill=ACCENT))

    return render(os.path.join(OUT, 'key-salting-read-write.svg'), W, H, *f)


# ── 4. Дворівневий кеш L1/L2 з інвалідацією ──────────────────────────────────
def fig_two_tier_cache():
    W, H = 1080, 560
    f = []

    f.append(fitbox(40, 20, 1000, 42,
                    "Дворівневе кешування L1/L2: захист від гарячих ключів через локальну пам'ять та шину інвалідації",
                    size=14, bold=True, fill=COOL))

    # Рівень L1: Застосунки (Near-Cache)
    f.append(rect(40, 78, 620, 330, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 90, 590, 28, "РІВЕНЬ L1: Вузли застосунку (Локальний In-Process кеш, RAM)", size=11, bold=True, fill=COOL))

    # Інстанс 1
    f.append(rect(55, 130, 280, 175, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(fitbox(65, 140, 260, 24, "App Instance #1 (Node.js / Go / C++)", size=10, bold=True, fill=GOOD))
    f.append(fitbox(65, 170, 260, 50, "Локальний кеш L1 (TinyLFU / LRU)\nproduct:9901 (TTL = 3 сек)\nПопадання: 99.8% звернень", size=9.5, fill=BG, stroke=FIELD))
    f.append(fitbox(65, 226, 260, 68, "Heavy Hitter Detector:\nCount-Min Sketch фіксує сплеск\nі автоматично підтягує ключ в L1", size=9, fill=ACCENT, stroke=LINE))

    # Інстанс 2
    f.append(rect(365, 130, 280, 175, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(fitbox(375, 140, 260, 24, "App Instance #2 (Node.js / Go / C++)", size=10, bold=True, fill=GOOD))
    f.append(fitbox(375, 170, 260, 50, "Локальний кеш L1 (TinyLFU / LRU)\nproduct:9901 (TTL = 3 сек)\nПопадання: 99.8% звернень", size=9.5, fill=BG, stroke=FIELD))
    f.append(fitbox(375, 226, 260, 68, "Підписка на інвалідацію:\nRedis RESP3 Tracking / Pub-Sub\nСлухає сигнал скидання L1", size=9, fill=ACCENT, stroke=LINE))

    f.append(fitbox(55, 320, 590, 75, "Переваги L1:\n• Нульова мережева затримка (RAM lookup: < 50 наносекунд);\n• Повне розвантаження віддаленого кластера від мільйонів однакових GET-запитів;\n• Single-Flight усередині процесу блокує паралельні виходи в мережу при промаху.", size=9.5, fill=FILL, stroke=MUTED))

    # Рівень L2: Розподілений кластер
    f.append(rect(690, 78, 350, 330, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(705, 90, 320, 28, "РІВЕНЬ L2: Кластер Redis / Dragonfly", size=11, bold=True, fill=COOL))

    f.append(fitbox(705, 130, 320, 75, "Redis Cluster Shards\n\nЗберігає персистентний кеш\n(TTL = 1..24 години)\nОтримує лише 0.2% запитів (L1 miss)", size=10, fill=GOOD, stroke=FIELD))

    f.append(fitbox(705, 220, 320, 85, "Шина інвалідації (RESP3 / PubSub)\n\nПри зміні ціни товару надсилає:\nINVALIDATE product:9901\nусім підключеним інстансам L1", size=10, fill=WARM, stroke=POS))

    f.append(fitbox(705, 320, 320, 75, "Основна База Даних (RDBMS/NoSQL)\n\nНадійно захищена двома шарами кешу;\nКількість звернень знижена до одиниць.", size=9.5, fill=COOL, stroke=LINE))

    # Зв'язки між L1 та L2
    f.append(arrow(335, 195, 705, 160, color=LINE, sw=1.4))
    f.append(text(510, 168, "L1 Miss (0.2%)", size=9.5, color=MUTED))

    f.append(arrow(705, 260, 345, 260, color=POS, sw=1.6))
    f.append(text(510, 250, "RESP3 Invalidate", size=9.5, color=POS, bold=True))

    # Обхідна лінія від Redis до БД праворуч від блоку інвалідації
    f.append(line(1025, 167, 1040, 167, color=LINE, sw=1.3))
    f.append(line(1040, 167, 1040, 357, color=LINE, sw=1.3))
    f.append(arrow(1040, 357, 1025, 357, color=LINE, sw=1.3))
    f.append(text(1045, 260, "L2 miss", size=9.5, color=MUTED, anchor="start"))

    # Нижній блок: Синтез
    f.append(rect(40, 425, 1000, 115, fill=ACCENT, stroke=MUTED, sw=1.2))
    f.append(fitbox(60, 438, 960, 90, "Стратегія захисту: комбінація Count-Min Sketch + L1 Near-Cache + RESP3 Tracking\n1. Детектор Heavy Hitters виявляє зростання популярності ключа за ковзне вікно (наприклад, 100 мс);\n2. Ключ миттєво кешується в локальній пам'яті процесу (L1) кожного інстансу вебсервера;\n3. Мережевий трафік до кластера L2 падає на 99.9%, унеможливлюючи відмову вузлів Redis;\n4. У разі модифікації даних шина інвалідації миттєво очищує L1, зберігаючи високу узгодженість.", size=10, fill=ACCENT))

    return render(os.path.join(OUT, 'two-tier-l1-l2-invalidation.svg'), W, H, *f)


def main():
    fig_key_structure()
    fig_hotkey_imbalance()
    fig_key_salting()
    fig_two_tier_cache()
    print("Усі 4 фігури успішно згенеровано.")

if __name__ == "__main__":
    main()
