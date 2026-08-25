# -*- coding: utf-8 -*-
"""Фігури до теми «Graceful degradation як ПЕРВИННА стратегія»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"
COOL = "#eaf0fd"
GOOD = "#e8f6ee"
WARN = "#fef9e7"


# ── 1. Порівняння: бінарне урвище проти плавної деградації ────────────────────
def cliff_vs_degradation():
    W, H = 1100, 520
    f = []

    f.append(fitbox(40, 25, 1020, 50,
                    "РЕАКЦІЯ СИСТЕМИ НА ПЕРЕВАНТАЖЕННЯ: КРУТЕ УРВИЩЕ ПРОТИ КЕРОВАНОЇ ДЕГРАДАЦІЇ",
                    size=14, bold=True, fill=COOL))

    x0, y0 = 120.0, 420.0
    w_chart, h_chart = 400.0, 280.0

    # ── Лівий графік: Бінарне урвище (Cliff failure)
    f.append(rect(60, 95, 460, 395, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(290, 125, "Традиційний підхід: «все або нічого»", size=13.5, bold=True, color=POS))
    
    # Осі
    f.append(arrow(x0, y0, x0 + w_chart - 20, y0, color=LINE, sw=1.5))
    f.append(arrow(x0, y0, x0, y0 - h_chart + 20, color=LINE, sw=1.5))
    f.append(text(x0 + w_chart - 20, y0 + 25, "Навантаження (RPS)", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 15, y0 - h_chart + 30, "Корисність (%)", size=11, color=MUTED, anchor="end"))

    # Крива урвища: 100% до порогу, потім вертикальний обвал
    x_knee = x0 + 220.0
    y_top = y0 - 200.0
    f.append(line(x0, y_top, x_knee, y_top, color=FIELD, sw=3.0))
    f.append(line(x_knee, y_top, x_knee + 25, y0, color=POS, sw=3.0))
    f.append(line(x_knee + 25, y0, x0 + w_chart - 40, y0, color=POS, sw=3.0))
    
    # Позначки
    f.append(line(x_knee, y0, x_knee, y_top, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(x_knee, y0 + 18, "Номінальна межа", size=10.5, color=MUTED, anchor="middle"))
    
    # Розміщуємо блок лівіше від урвища, щоб лінія не перетинала текст
    f.append(fitbox(75, 260, 220, 70,
                    "КРУТЕ УРВИЩЕ (CLIFF)\n1 відмова з 20 сервісів →\nпомилка 500 для 100% клієнтів",
                    size=10.5, bold=True, fill=WARM, stroke=POS))

    # ── Правий графік: Керована деградація (Graceful Degradation)
    x0_r = 580.0
    f.append(rect(540, 95, 500, 395, fill="#ffffff", stroke=MUTED, sw=1.2))
    f.append(text(790, 125, "Первинна стратегія: спектр корисності", size=13.5, bold=True, color=FIELD))

    # Осі
    f.append(arrow(x0_r, y0, x0_r + w_chart - 20, y0, color=LINE, sw=1.5))
    f.append(arrow(x0_r, y0, x0_r, y0 - h_chart + 20, color=LINE, sw=1.5))
    f.append(text(x0_r + w_chart - 20, y0 + 25, "Навантаження (RPS)", size=11, color=MUTED, anchor="end"))
    f.append(text(x0_r - 15, y0 - h_chart + 30, "Корисність (%)", size=11, color=MUTED, anchor="end"))

    # Ступінчаста деградація: 100% -> Tier-2 off -> Tier-1 off -> Core Tier-0 alive
    x_k1 = x0_r + 120.0
    x_k2 = x0_r + 200.0
    x_k3 = x0_r + 280.0
    
    y_l1 = y_top + 45.0
    y_l2 = y_top + 105.0
    y_l3 = y_top + 155.0

    f.append(line(x0_r, y_top, x_k1, y_top, color=FIELD, sw=3.0))
    f.append(line(x_k1, y_top, x_k1 + 20, y_l1, color=FIELD, sw=2.5))
    f.append(line(x_k1 + 20, y_l1, x_k2, y_l1, color="#2980b9", sw=2.5))
    f.append(line(x_k2, y_l1, x_k2 + 20, y_l2, color="#2980b9", sw=2.0))
    f.append(line(x_k2 + 20, y_l2, x_k3, y_l2, color="#d35400", sw=2.0))
    f.append(line(x_k3, y_l2, x_k3 + 20, y_l3, color="#d35400", sw=2.0))
    f.append(line(x_k3 + 20, y_l3, x0_r + w_chart - 40, y_l3, color=POS, sw=2.0))

    # Сектори
    f.append(text(x_k1 - 40, y_top - 12, "Повний режим (100%)", size=10, color=FIELD, bold=True))
    f.append(text(x_k2 - 30, y_l1 - 10, "−Tier-2 (відгуки)", size=9.5, color="#2980b9"))
    f.append(text(x_k3 - 30, y_l2 - 10, "−Tier-1 (кеш)", size=9.5, color="#d35400"))
    f.append(text(x0_r + w_chart - 80, y_l3 - 10, "Tier-0 (ядро)", size=9.5, color=POS, bold=True))

    f.append(fitbox(560, 310, 290, 65,
                    "ПЛАВНЕ СПOVZANNYA (GRACEFUL)\nКритичний бізнес-процес живе\nнавіть при 3× перевантаженні",
                    size=10.5, bold=True, fill=GOOD, stroke=FIELD))

    render(os.path.join(OUT, 'cliff-vs-degradation.svg'), W, H, *f)


# ── 2. Дерево залежностей за рівнями критичності ──────────────────────────────
def tiered_dependency_tree():
    W, H = 1060, 500
    f = []

    f.append(fitbox(40, 20, 980, 48,
                    "ІЄРАРХІЯ ЗАЛЕЖНОСТЕЙ ТА ІЗОЛЯЦІЯ РІВНІВ ОБСЛУГОВУВАННЯ (TIERING)",
                    size=14, bold=True, fill=COOL))

    # Клієнт / Gateway
    f.append(fitbox(400, 90, 260, 50, "API Gateway / Агрегатор\nРозподіл наскрізного бюджету часу",
                    size=12.5, bold=True, fill=FILL, stroke=LINE))

    # Ліва гілка: Tier-0 (Жорстка залежність)
    f.append(arrow(450, 140, 180, 195, color=POS, sw=2.0))
    f.append(fitbox(60, 195, 240, 75,
                    "Tier-0: Критичне ядро (Hard)\nПлатіжний шлюз / Замовлення\nFail-closed: відмова зупиняє процес",
                    size=11.5, bold=True, fill=WARM, stroke=POS))

    f.append(arrow(180, 270, 180, 335, color=POS, sw=1.8))
    f.append(fitbox(60, 335, 240, 65,
                    "Транзакційна БД (ACID)\nОбов'язковий синхронний запис\nРезервування: синхронна репліка",
                    size=11, fill=FILL, stroke=LINE))

    # Центральна гілка: Tier-1 (М'яка бізнес-залежність)
    f.append(arrow(530, 140, 530, 195, color="#2980b9", sw=2.0))
    f.append(fitbox(410, 195, 240, 75,
                    "Tier-1: Бізнес-логіка (Soft)\nКаталог цін та наявність на складі\nФолбек: локальний реплікований кеш",
                    size=11.5, bold=True, fill=COOL, stroke="#2980b9"))

    f.append(arrow(530, 270, 530, 335, color="#2980b9", sw=1.8))
    f.append(fitbox(410, 335, 240, 65,
                    "Служба цін + L2-кеш\nПри збої: ціна з локального кешу\nпрапорець `is_stale: true`",
                    size=11, fill=FILL, stroke=LINE))

    # Права гілка: Tier-2 (Допоміжна декоративна залежність)
    f.append(arrow(610, 140, 860, 195, color=FIELD, sw=2.0))
    f.append(fitbox(740, 195, 260, 75,
                    "Tier-2: Допоміжний сервіс (Soft)\nML-рекомендації та персоналізація\nФолбек: статичний детермінований топ",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD))

    f.append(arrow(870, 270, 870, 335, color=FIELD, sw=1.8))
    f.append(fitbox(740, 335, 260, 65,
                    "Рекомендаційна ML-модель\nПри затримці > 40 мс: скидання,\nповернення дефолтного бестселера",
                    size=11, fill=FILL, stroke=LINE))

    # Підсумок знизу
    f.append(fitbox(60, 425, 940, 55,
                    "ПРАВИЛО ІЗОЛЯЦІЇ: збій або затримка у правій гілці (Tier-2) чи центральній (Tier-1)\nніколи не блокують і не уповільнюють ліву гілку (Tier-0). Відповідь агрегатора формується завжди.",
                    size=12, bold=True, fill=WARN, stroke="#d35400"))

    render(os.path.join(OUT, 'tiered-dependency-tree.svg'), W, H, *f)


# ── 3. Часова шкала бюджету дедлайну та відсікання ────────────────────────────
def latency_budget_timeline():
    W, H = 1080, 480
    f = []

    f.append(fitbox(40, 20, 1000, 48,
                    "РОЗПОДІЛ НАВАНТАЖЕННЯ І ДЕДЛАЙНІВ ПРИ ПАРАЛЕЛЬНОМУ SCATTER-GATHER",
                    size=14, bold=True, fill=COOL))

    x_start = 140.0
    x_end = 980.0
    y_axis = 105.0

    # Загальна шкала часу
    f.append(arrow(x_start, y_axis, x_end, y_axis, color=LINE, sw=2.0))
    f.append(text(x_end, y_axis - 10, "Час (мс)", size=12, color=MUTED, anchor="end"))

    # Позначки часу на осі
    t_0 = x_start
    t_40 = x_start + 240.0
    t_80 = x_start + 480.0
    t_120 = x_start + 720.0

    for tx, lbl in [(t_0, "0 мс\n(Старт)"), (t_40, "40 мс\n(Поріг Tier-2)"),
                    (t_80, "80 мс\n(Поріг Tier-1)"), (t_120, "120 мс\n(Hard Deadline)")]:
        f.append(line(tx, y_axis - 6, tx, y_axis + 6, color=LINE, sw=1.5))
        f.append(mtext(tx, y_axis + 22, lbl, size=11, color=INK, anchor="middle"))

    # Вертикаль жорсткого дедлайну
    f.append(line(t_120, y_axis, t_120, 410, color=POS, sw=1.8, dash="5,5"))
    f.append(text(t_120 + 8, 400, "ЖОРСТКИЙ ДЕДЛАЙН КЛІЄНТА (120 мс)", size=11, color=POS, bold=True, anchor="start"))

    # Доріжка 1: Tier-0 (Швидка відповідь)
    y1 = 180.0
    f.append(fitbox(30, y1 - 18, 90, 36, "Tier-0", size=11.5, bold=True, fill=WARM, stroke=POS))
    f.append(rect(t_0, y1 - 15, 180, 30, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(text(t_0 + 90, y1 + 4, "Служба замовлень (30 мс) ✓", size=11, color=FIELD, bold=True))

    # Доріжка 2: Tier-1 (Повільна відповідь -> деградація на фолбек)
    y2 = 250.0
    f.append(fitbox(30, y2 - 18, 90, 36, "Tier-1", size=11.5, bold=True, fill=COOL, stroke="#2980b9"))
    f.append(rect(t_0, y2 - 15, 480, 30, fill=WARN, stroke="#d35400", sw=1.5, rx=4))
    f.append(text(t_0 + 190, y2 + 4, "Служба цін (RPC підвисла на 80 мс...)", size=11, color="#d35400"))
    f.append(rect(t_80, y2 - 15, 80, 30, fill=GOOD, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(t_80 + 40, y2 + 4, "Кеш ✓", size=11, color=FIELD, bold=True))

    # Доріжка 3: Tier-2 (Таймаут -> негайне відсікання)
    y3 = 320.0
    f.append(fitbox(30, y3 - 18, 90, 36, "Tier-2", size=11.5, bold=True, fill=GOOD, stroke=FIELD))
    f.append(rect(t_0, y3 - 15, 240, 30, fill=WARM, stroke=POS, sw=1.5, rx=4))
    f.append(text(t_0 + 120, y3 + 4, "ML-рекомендації (таймаут 40 мс) ✗", size=10.5, color=POS))
    f.append(rect(t_40, y3 - 15, 60, 30, fill=COOL, stroke="#2980b9", sw=1.5, rx=4))
    f.append(text(t_40 + 30, y3 + 4, "Топ ✓", size=10.5, color="#2980b9", bold=True))

    # Підсумок агрегатора
    y4 = 390.0
    f.append(fitbox(30, y4 - 18, 90, 36, "Агрегатор", size=11.5, bold=True, fill=FILL, stroke=LINE))
    f.append(rect(t_0, y4 - 15, 580, 30, fill=GOOD, stroke=FIELD, sw=2.0, rx=4))
    f.append(text(t_0 + 290, y4 + 4, "Збір деградованої відповіді завершено на 95 мс (до ліміту 120 мс) ✓",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'latency-budget-timeline.svg'), W, H, *f)


# ── 4. Пастка важкого фолбеку проти легкого O(1) ──────────────────────────────
def fallback_cost_antipattern():
    W, H = 1060, 480
    f = []

    f.append(fitbox(40, 20, 980, 48,
                    "АНТИПАТЕРН «ВАЖКИЙ ФОЛБЕК» ПРОТИ ДЕТЕРМІНОВАНОГО ДЕГРАДОВАНОГО ШЛЯХУ",
                    size=14, bold=True, fill=COOL))

    # Ліва колонка: Антипатерн (Важкий фолбек)
    f.append(rect(50, 85, 460, 370, fill="#ffffff", stroke=POS, sw=1.6))
    f.append(fitbox(70, 100, 420, 40, "АНТИПАТЕРН: ВАЖКИЙ ФОЛБЕК", size=13, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(70, 155, 420, 55,
                    "Основний шлях (L1 Cache Hit):\nЧас виконання: 2 мс | Використання CPU: 0.1%\n10 000 RPS обробляються легко",
                    size=11, fill=GOOD, stroke=FIELD))

    f.append(arrow(280, 210, 280, 240, color=POS, sw=2))
    f.append(text(290, 230, "Збій кешу / навантаження", size=10.5, color=POS, bold=True))

    f.append(fitbox(70, 240, 420, 95,
                    "Фолбек (Холодний запит у реляційну БД без індексу):\n• Час виконання: 850 мс (у 400× довше!)\n• Створює 50 МБ алокацій у пам'яті\n• Виснажує пул з'єднань пулу БД",
                    size=11, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(70, 350, 420, 85,
                    "НАСЛІДОК: МЕТАСТАБІЛЬНА АВАРІЯ\nФолбек споживає більше ресурсів, ніж нормальний шлях.\nСистема входить у смертельну спіраль і падає наглухо.",
                    size=11.5, bold=True, fill=WARM, stroke=POS))

    # Права колонка: Правильний патерн (Легкий детермінований фолбек)
    f.append(rect(550, 85, 460, 370, fill="#ffffff", stroke=FIELD, sw=1.6))
    f.append(fitbox(570, 100, 420, 40, "ПРАВИЛО: COST(FALLBACK) <= COST(PRIMARY) / 10", size=13, bold=True, fill=GOOD, stroke=FIELD))

    f.append(fitbox(570, 155, 420, 55,
                    "Основний шлях (Розподілений ML-пошук):\nЧас виконання: 35 мс | 100% точність скорингу\nВимагає 4 мережевих виклики",
                    size=11, fill=COOL, stroke=LINE))

    f.append(arrow(780, 210, 780, 240, color=FIELD, sw=2))
    f.append(text(790, 230, "Вичерпано дедлайн / збій вузла", size=10.5, color=FIELD, bold=True))

    f.append(fitbox(570, 240, 420, 95,
                    "Детермінований фолбек (Static / Local O(1)):\n• Час виконання: 0.05 мс (миттєве повернення)\n• 0 алокацій (повертає статичний `std::span`)\n• 0 викликів по мережі",
                    size=11, bold=True, fill=GOOD, stroke=FIELD))

    f.append(fitbox(570, 350, 420, 85,
                    "НАСЛІДОК: РОЗВАНТАЖЕННЯ СИСТЕМИ\nПри перевантаженні фолбек знижує споживання CPU в 700 разів.\nКластер миттєво стабілізується.",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD))

    render(os.path.join(OUT, 'fallback-cost-antipattern.svg'), W, H, *f)


# ── 5. Життєвий цикл деградованої відповіді та UI-узгодження ──────────────────
def degraded_response_lifecycle():
    W, H = 1080, 490
    f = []

    f.append(fitbox(40, 20, 1000, 48,
                    "ЖИТТЄВИЙ ЦИКЛ ДЕГРАДОВАНОЇ ВІДПОВІДІ: ВІД СЕРВЕРНИХ МЕТАДАНИХ ДО КЛІЄНТСЬКОГО UI",
                    size=14, bold=True, fill=COOL))

    # Крок 1: Виявлення відмови в бекенді
    f.append(fitbox(60, 90, 270, 95,
                    "1. Бекенд-агрегатор\n• Вичерпано дедлайн Tier-2\n• Підстановка фолбеку\n• Встановлення прапорців:\n  `degraded: true`,\n  `stale_fields: [\"price\"]`",
                    size=11.5, fill=COOL, stroke=LINE))

    f.append(arrow(330, 137, 410, 137, color=LINE, sw=2))

    # Крок 2: Формування конверта (Envelope Protocol)
    f.append(fitbox(410, 90, 290, 95,
                    "2. Протокольний конверт\n• HTTP 200 OK (частковий успіх)\n• Заголовки:\n  `X-Degraded: Tier-1,Tier-2`\n• Тіло містить корисні дані Tier-0\n  та метадані деградації",
                    size=11.5, bold=True, fill=WARN, stroke="#d35400"))

    f.append(arrow(700, 137, 780, 137, color=LINE, sw=2))

    # Крок 3: Інтерпретація клієнтом (Web / Mobile App)
    f.append(fitbox(780, 90, 250, 95,
                    "3. Клієнтська логіка\n• Перевірка `degraded` статусу\n• Відсікання порожніх віджетів\n• Відображення індикатора\n  «Ціна оновлюється...»",
                    size=11.5, fill=GOOD, stroke=FIELD))

    # Нижній блок: Рендеринг інтерфейсу
    f.append(fitbox(60, 220, 970, 40, "ВІДОБРАЖЕННЯ НА ЕКРАНІ КОРИСТУВАЧА (UI DEGRADATION PATTERNS)",
                    size=13, bold=True, fill=COOL))

    # Лівий екран: Нормальний стан
    f.append(rect(90, 275, 420, 190, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(300, 300, "100% Повний режим (Зелений статус)", size=12, bold=True, color=FIELD))
    f.append(rect(110, 315, 380, 35, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text(300, 337, "Кнопка «Купити» + Точна ціна в реальному часі", size=11, color=FIELD))
    f.append(rect(110, 360, 380, 40, fill=COOL, stroke="#2980b9", sw=1.2))
    f.append(text(300, 385, "Персональні рекомендації на основі AI", size=11, color="#2980b9"))
    f.append(rect(110, 410, 380, 35, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(text(300, 432, "Живі відгуки та лічильник переглядів", size=11, color=MUTED))

    # Правий екран: Деградований стан
    f.append(rect(570, 275, 420, 190, fill="#ffffff", stroke="#d35400", sw=1.5, rx=6))
    f.append(text(780, 300, "Деградований режим (Штатний бекенд-стрес)", size=12, bold=True, color="#d35400"))
    f.append(rect(590, 315, 380, 35, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text(780, 337, "Кнопка «Купити» працює! (Tier-0 збережено)", size=11, color=FIELD, bold=True))
    f.append(rect(590, 360, 380, 40, fill=WARN, stroke="#d35400", sw=1.2))
    f.append(text(780, 385, "Популярні товари (статичний кеш) замість AI", size=11, color="#d35400"))
    f.append(rect(590, 410, 380, 35, fill="#f0f0f0", stroke=MUTED, sw=1.2))
    f.append(text(780, 432, "[Блок відгуків тимчасово приховано]", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, 'degraded-response-lifecycle.svg'), W, H, *f)


cliff_vs_degradation()
tiered_dependency_tree()
latency_budget_timeline()
fallback_cost_antipattern()
degraded_response_lifecycle()
print("готово:", ", ".join(sorted(os.listdir(OUT))))
