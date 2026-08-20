# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'Thundering herd / cache stampede і lock/coalescing'."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / перевантаження / лавина промахів
COOL = "#eaf0fd"   # клієнти / нормальний запит / мережа
GOOD = "#e8f6ee"   # успіх / захист / свіжі дані
ACCENT = "#fef9e7" # проміжний стан / блокування / очікування


# ── 1. Анатомія навали на кеш (Cache Stampede) ─────────────────────────────
def fig_stampede_anatomy():
    W, H = 1180, 560
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "Анатомія навали на кеш: перевантаження джерела внаслідок одночасного промаху",
                    size=13, bold=True, fill=COOL))

    # Ліва колонка: Клієнтський трафік та вичерпання TTL
    f.append(rect(40, 80, 330, 450, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 95, 300, 34, "1. Вхідний потік запитів", size=11, bold=True, fill=COOL, stroke=LINE))
    
    f.append(fitbox(55, 140, 300, 40, "Гарячий ключ: product:7821\nІнтенсивність: λ = 5000 запитів/с", size=10.5, fill=COOL, stroke=LINE))
    f.append(fitbox(55, 190, 300, 55, "Кеш (TTL = 60 с)\nЧас t = 60.000 с: термін дії вичерпано!\nУсі 5000 потоків фіксують ПРОМАХ", size=10, fill=WARM, stroke=POS))
    
    f.append(arrow(205, 250, 205, 280, color=POS, sw=2.0))
    f.append(fitbox(55, 285, 300, 95, "Вікно вразливості (δ = 200 мс):\nЗа час обчислення одного запиту\nнадходить 1000 паралельних промахів.\nЖоден не чекає на сусіда!", size=10, fill=WARM, stroke=POS))
    
    f.append(fitbox(55, 390, 300, 125, "Наслідки для клієнтів:\n• Затримка зростає: 5 мс → 15 000 мс\n• Спрацьовує клієнтський таймаут 2 с\n• Шторм повторних спроб (Retry Storm)\n• Клієнти лавиноподібно добивають сервіс", size=9.5, fill=WARM, stroke=POS))

    # Середня колонка: Вплив на базу даних
    f.append(rect(390, 80, 380, 450, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(405, 95, 350, 34, "2. Колапс джерела даних (СУБД)", size=11, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(405, 140, 350, 55, "Пул з'єднань СУБД (Max = 100):\n1000 потоків одночасно штурмують базу\nЧерга з'єднань миттєво переповнена", size=10, fill=WARM, stroke=POS))
    
    f.append(fitbox(405, 205, 350, 60, "CPU & Диск:\n• Завантаження CPU: 100%\n• Перемикання контекстів ядра: > 500k/s\n• Черга дискового вводу/виводу: переповнена", size=10, fill=WARM, stroke=POS))

    f.append(fitbox(405, 275, 350, 55, "Конкуренція за блокування:\nСотні ідентичних SQL-запитів блокують\nрядки та сторінки в Buffer Pool", size=10, fill=WARM, stroke=POS))

    f.append(fitbox(405, 340, 350, 175, "Метастабільна відмова (Metastable Failure):\n• База не встигає відповісти за час таймауту.\n• Відповіді викидаються в нікуди, бо клієнт відпав.\n• Кеш ніколи не заповнюється свіжим значенням.\n• Навіть при спаданні трафіку система не виходить\n  зі стану перевантаження без ручного втручання.", size=10, fill=WARM, stroke=POS))

    # Права колонка: Рішення та вектори захисту
    f.append(rect(790, 80, 350, 450, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(805, 95, 320, 34, "3. Класифікація методів захисту", size=11, bold=True, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 140, 320, 80, "А. Блокування (Lock / Mutex):\nТільки один потік іде до бази,\nінші чекають у черзі або сплять.\nРозподілений замок у Redis.", size=10, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 230, 320, 80, "Б. Об'єднання запитів (Coalescing):\nОдин рейс на всі паралельні запити.\nРезультат розсилається підписникам.\nSingle-Flight у пам'яті процесу.", size=10, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 320, 320, 85, "В. Раннє оновлення (XFetch / Soft TTL):\nЙмовірнісний або фоновий розрахунок\nДО настання фізичного вичерпання TTL.\nКлієнт завжди отримує відповідь з пам'яті.", size=10, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 415, 320, 100, "Г. Дезсинхронізація (TTL Jitter):\nДодавання випадкового шуму до TTL,\nщоб запобігти масовому одночасному\nзгорянню тисяч споріднених ключів.", size=10, fill=GOOD, stroke=FIELD))

    # Стрілки взаємодії
    f.append(arrow(370, 210, 390, 210, color=POS, sw=2.0))
    f.append(arrow(770, 210, 790, 210, color=FIELD, sw=2.0))

    render(os.path.join(OUT, "stampede-anatomy.svg"), W, H, *f)


# ── 2. Матриця стратегій захисту від навали на кеш ────────────────────────
def fig_defense_strategies_matrix():
    W, H = 1180, 620
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "Порівняння архітектурних патернів захисту від навали на кеш",
                    size=13, bold=True, fill=COOL))

    # 4 квадранти
    # 1. Замок (Distributed Lock)
    f.append(rect(40, 80, 535, 250, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 92, 505, 30, "1. Блокування (Distributed Lock / Mutex)", size=11, bold=True, fill=ACCENT, stroke=LINE))
    f.append(fitbox(55, 128, 505, 55, "Механізм: Перший потік захоплює замок у Redis (SETNX),\nобчислює дані та оновлює кеш. Решта очікують.", size=10, fill=FILL, stroke=MUTED))
    f.append(fitbox(55, 188, 505, 42, "Плюси: База отримує строго 1 запит; захищає весь кластер.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(55, 235, 505, 85, "Мінуси: Потоки блокуються; ризик збою власника замка\n(потрібен ліз-таймаут); сплеск запитів до Redis під час\nактивного опитування статусу (Spin-lock).", size=9.5, fill=WARM, stroke=POS))

    # 2. Об'єднання запитів (Request Coalescing / Single-Flight)
    f.append(rect(605, 80, 535, 250, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(620, 92, 505, 30, "2. Об'єднання запитів (Single-Flight)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(620, 128, 505, 55, "Механізм: Внутрішньопроцесний реєстр активних викликів.\nЛідер ініціює операцію, усі паралельні потоки ділять Promise.", size=10, fill=FILL, stroke=MUTED))
    f.append(fitbox(620, 188, 505, 42, "Плюси: Нульовий оверхед на зовнішні блокування; надшвидко.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(620, 235, 505, 85, "Мінуси: Діє лише в межах одного процесу (при 50 серверах\nпіде 50 запитів); зависання лідера блокує всіх підписників\nрейсу без таймаутів очікування.", size=9.5, fill=WARM, stroke=POS))

    # 3. М'який TTL (Stale-While-Revalidate)
    f.append(rect(40, 345, 535, 250, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 357, 505, 30, "3. М'який термін життя (Stale-While-Revalidate)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(55, 393, 505, 55, "Механізм: Два пороги: Soft TTL (застарівання) та Hard TTL.\nКлієнт миттєво отримує застаріле значення з пам'яті.", size=10, fill=FILL, stroke=MUTED))
    f.append(fitbox(55, 453, 505, 42, "Плюси: Клієнти ніколи не чекають базу; затримка P99 мінімальна.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(55, 500, 505, 85, "Мінуси: Клієнт короткий час бачить трохи застарілі дані;\nпотрібен асинхронний фоновий воркер або черга\nдля оновлення даних у сховищі.", size=9.5, fill=WARM, stroke=POS))

    # 4. Імовірнісне раннє оновлення (XFetch)
    f.append(rect(605, 345, 535, 250, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(620, 357, 505, 30, "4. Імовірнісне раннє оновлення (XFetch)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(620, 393, 505, 55, "Механізм: Чим ближче час до вичерпання TTL і чим важчий\nрозрахунок, тим вищий шанс фонового оновлення читачем.", size=10, fill=FILL, stroke=MUTED))
    f.append(fitbox(620, 453, 505, 42, "Плюси: Відсутність замків; автоматична адаптація до потоку.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(620, 500, 505, 85, "Мінуси: Потребує збереження часу розрахунку (дельта)\nпоруч із кешованим об'єктом у сховищі Redis;\nвимагає точного вимірювання затримок.", size=9.5, fill=WARM, stroke=POS))

    render(os.path.join(OUT, "defense-strategies-matrix.svg"), W, H, *f)


# ── 3. Графік імовірності раннього оновлення XFetch ────────────────────────
def fig_xfetch_curve():
    W, H = 1180, 520
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "Імовірнісна динаміка XFetch: плавне зростання шансу оновлення перед вичерпанням TTL",
                    size=13, bold=True, fill=COOL))

    # Область графіка
    gx, gy, gw, gh = 100, 100, 980, 320
    f.append(rect(gx, gy, gw, gh, fill=FILL, stroke=MUTED, sw=1.2))

    # Осі координат
    f.append(line(gx + 60, gy + gh - 40, gx + gw - 40, gy + gh - 40, color=LINE, sw=1.5)) # Вісь X (Час)
    f.append(line(gx + 60, gy + gh - 40, gx + 60, gy + 30, color=LINE, sw=1.5))          # Вісь Y (P)

    # Підписи осей
    f.append(text(gx + gw - 30, gy + gh - 35, "Час (t)", size=11, bold=True, anchor="start", color=INK))
    f.append(text(gx + 50, gy + 20, "Ймовірність оновлення P(t)", size=11, bold=True, anchor="middle", color=INK))

    # Позначки Y
    f.append(text(gx + 45, gy + gh - 40, "0.0", size=10, color=MUTED, anchor="end"))
    f.append(text(gx + 45, gy + gh - 160, "0.5", size=10, color=MUTED, anchor="end"))
    f.append(text(gx + 45, gy + 50, "1.0", size=10, color=MUTED, anchor="end"))
    f.append(line(gx + 55, gy + gh - 160, gx + gw - 40, gy + gh - 160, color=MUTED, sw=1.0, dash="4,4"))
    f.append(line(gx + 55, gy + 50, gx + gw - 40, gy + 50, color=MUTED, sw=1.0, dash="4,4"))

    # Позначки X
    f.append(text(gx + 120, gy + gh - 20, "t = 0 (Свіжий кеш)", size=10, color=MUTED))
    f.append(text(gx + 500, gy + gh - 20, "t = TTL − 3·β·δ (Початок зони ризику)", size=10, color=MUTED))
    f.append(text(gx + 780, gy + gh - 20, "t = TTL − β·δ", size=10, color=MUTED))
    f.append(text(gx + 920, gy + gh - 20, "t = TTL (Hard Expiry)", size=10, bold=True, color=POS))

    f.append(line(gx + 920, gy + gh - 40, gx + 920, gy + 40, color=POS, sw=1.5, dash="4,4"))

    # Крива XFetch: експоненційне зростання
    points = []
    for x_val in range(gx + 60, gx + 925, 20):
        if x_val < gx + 450:
            y_val = gy + gh - 40
        else:
            prog = (x_val - (gx + 450)) / (470.0)
            prob = (prog ** 3.5)
            y_val = (gy + gh - 40) - prob * ((gy + gh - 40) - (gy + 50))
        points.append((x_val, y_val))

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        f.append(line(x1, y1, x2, y2, color=FIELD, sw=2.5))

    f.append(fitbox(gx + 120, gy + 50, 360, 110,
                    "Формула XFetch:\nnow − δ · β · ln(rand(0,1)) > expiry\n\n• δ (delta) — тривалість розрахунку\n• β (beta) > 0 — коефіцієнт агресивності\n• rand(0,1) — рівномірне випадкове число",
                    size=10, fill=ACCENT, stroke=LINE))

    f.append(fitbox(40, 440, 1100, 65,
                    "Ключова властивість XFetch: при високому потоці запитів (λ) хоча б один випадковий читач гарантовано запустить фоновий розрахунок ще ДО настання моменту вичерпання TTL. У момент t = TTL у кеші вже лежить свіже значення, і промах на рівні 0%.",
                    size=10.5, fill=GOOD, stroke=FIELD))

    render(os.path.join(OUT, "xfetch-probability-curve.svg"), W, H, *f)


# ── 4. Багаторівнева архітектура комбінованого захисту ──────────────────────
def fig_tiered_cache_defense():
    W, H = 1180, 580
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "Багаторівнева архітектура захисту: від Edge-проксі до ядра бази даних",
                    size=13, bold=True, fill=COOL))

    # Рівень 1: Вхідний трафік та Edge / Gateway
    f.append(rect(40, 80, 250, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 95, 220, 34, "Рівень 1: Edge / Шлюз (Nginx)", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(fitbox(55, 140, 220, 70, "Вхідний потік:\n10 000 паралельних запитів\nвід клієнтів", size=10, fill=COOL, stroke=LINE))
    f.append(fitbox(55, 230, 220, 130, "Edge Coalescing:\n• proxy_cache_lock on;\n• proxy_cache_use_stale\n  updating timeout;\nЗлиття тисяч однакових\nHTTP-запитів в 1", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(55, 380, 220, 150, "Результат Edge:\nЗ 10 000 запитів до бекенду\nпроходить лише 1 запит на\nкожну edge-ноду. Решта\nотримують застарілий кеш.", size=10, fill=GOOD, stroke=FIELD))

    # Рівень 2: Бекенд-сервіс (Single-Flight + L1 RAM Cache)
    f.append(rect(320, 80, 270, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(335, 95, 240, 34, "Рівень 2: Бекенд (L1 & Flight)", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(fitbox(335, 140, 240, 70, "L1 Локальний кеш:\nIn-Memory LRU з Soft TTL\n(Stale-While-Revalidate)", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(335, 230, 240, 130, "Single-Flight Coalescing:\nВнутрішньопроцесний реєстр.\nУсі паралельні потоки ділять\nодин Promise / Future.", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(335, 380, 240, 150, "Результат Бекенду:\nУсі потоки інстансу\nдедуплікуються. Навіть при\nпромаху L1 в мережу йде\nрівно 1 виклик від інстансу.", size=10, fill=GOOD, stroke=FIELD))

    # Рівень 3: Розподілений кеш (Redis L2 + XFetch)
    f.append(rect(620, 80, 250, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(635, 95, 220, 34, "Рівень 3: Розподілений L2", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(fitbox(635, 140, 220, 70, "Redis / Memcached:\nЗбереження об'єкта разом\nіз часом обчислення (дельта)", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(635, 230, 220, 130, "Алгоритм XFetch & Jitter:\nЙмовірнісне оновлення до\nвичерпання TTL + випадковий\nрозкид строків життя", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(635, 380, 220, 150, "Результат L2:\n99.99% запитів обслуговуються\nбез промахів. Промахи\nтрапляються лише при\nхолодному старті.", size=10, fill=GOOD, stroke=FIELD))

    # Рівень 4: База даних та Розподілений замок
    f.append(rect(900, 80, 240, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(915, 95, 210, 34, "Рівень 4: Джерело (СУБД)", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(915, 140, 210, 70, "Розподілений Mutex:\nSETNX lock:product:7821\nз автопродовженням лізу", size=10, fill=ACCENT, stroke=LINE))
    f.append(fitbox(915, 230, 210, 130, "Основна СУБД:\nВиконує РІВНО 1 важкий\nSQL-запит на весь кластер!\nCPU < 5%", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(915, 380, 210, 150, "Підсумок надійності:\nКластер витримує будь-яке\nпікове навантаження без\nперевантаження бази та\nкаскадних збоїв.", size=10, fill=GOOD, stroke=FIELD))

    # З'єднувальні стрілки зверху між колонками (в нейтральній зоні y=180)
    f.append(arrow(290, 175, 320, 175, color=LINE, sw=1.8))
    f.append(arrow(590, 175, 620, 175, color=LINE, sw=1.8))
    f.append(arrow(870, 175, 900, 175, color=FIELD, sw=1.8))

    render(os.path.join(OUT, "defense-strategies-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stampede_anatomy()
    fig_defense_strategies_matrix()
    fig_xfetch_curve()
    fig_tiered_cache_defense()
    print("All figures successfully generated in ./img/")
