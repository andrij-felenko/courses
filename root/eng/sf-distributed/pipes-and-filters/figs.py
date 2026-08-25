# -*- coding: utf-8 -*-
"""Фігури для теми «Канали та фільтри». Вивід — ./img/*.svg"""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"
GRAY_F  = "#f8f9fa"
PURPLE_F = "#f3e8fd"

# ── 1. direct-vs-pipeline: монолітний виклик проти каналів і фільтрів ─────────
def fig_direct_vs_pipeline():
    W, H = 1000, 420
    f = []

    # Ліва половина: Монолітний моноблок або прямий каскадний RPC
    f.append(rect(15, 15, 470, 390, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(250, 42, "Монолітний ланцюг: жорстке зчеплення кроків", size=13, bold=True, color=POS))

    # Великий монолітний блок
    f.append(rect(45, 75, 410, 265, fill=RED_F, stroke=POS, sw=1.5, rx=6))
    f.append(text(250, 102, "Єдиний монолітний процес / Тісний синхронний RPC", size=11.5, bold=True, color=POS))

    steps = [
        ("Крок 1: Декодування пакета", 135),
        ("Крок 2: Валідація бізнес-схеми", 175),
        ("Крок 3: Збагачення даними (SQL)", 215),
        ("Крок 4: Розрахунок скорингу (CPU)", 255),
        ("Крок 5: Запис у базу даних", 295)
    ]
    for lbl, y in steps:
        b, _, _ = textbox(250, y, lbl, size=11, min_w=340, pad=5, fill="#ffffff", stroke=POS, sw=1)
        f.append(b)

    # Стрілка помилки на кроці 3
    f.append(circle(400, 215, 10, fill=POS, stroke=POS))
    f.append(text(400, 219, "✕", size=11, color="#ffffff", bold=True))
    f.append(text(250, 375, "✗ Збій чи зависання на одному кроці блокує всю транзакцію і потік", size=10.5, color=POS, italic=True))

    # Права половина: Архітектура Канали та Фільтри (Pipes & Filters)
    f.append(rect(515, 15, 470, 390, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(750, 42, "Канали та фільтри: незалежні вузли й буфери", size=13, bold=True, color=FIELD))

    # Вузли конвеєра: Вхід -> Канал 1 -> Фільтр 1 -> Канал 2 -> Фільтр 2 -> Канал 3 -> Фільтр 3 -> Вихід
    pipeline_items = [
        ("Фільтр 1\nДекодер", 575, 130),
        ("Фільтр 2\nВалідатор", 750, 130),
        ("Фільтр 3\nЗбагачувач", 925, 130),
        ("Фільтр 4\nСкоринг", 925, 270),
        ("Фільтр 5\nПерсистенція", 750, 270)
    ]

    for lbl, x, y in pipeline_items:
        b, _, _ = textbox(x, y, lbl, size=10.5, bold=True, min_w=95, pad=6, fill=BLUE_F, stroke=NEG, sw=1.5)
        f.append(b)

    # Канали між фільтрами (Pipes)
    # 1 -> 2
    f.append(textbox(662, 130, "Канал 1\n[Буфер]", size=9, min_w=60, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(623, 130, 632, 130, color=FIELD, sw=1.4))
    f.append(arrow(692, 130, 702, 130, color=FIELD, sw=1.4))

    # 2 -> 3
    f.append(textbox(837, 130, "Канал 2\n[Буфер]", size=9, min_w=60, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(798, 130, 807, 130, color=FIELD, sw=1.4))
    f.append(arrow(867, 130, 877, 130, color=FIELD, sw=1.4))

    # 3 -> 4 (вниз)
    f.append(textbox(925, 200, "Канал 3\n[Буфер]", size=9, min_w=65, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(925, 155, 925, 180, color=FIELD, sw=1.4))
    f.append(arrow(925, 220, 925, 245, color=FIELD, sw=1.4))

    # 4 -> 5 (вліво)
    f.append(textbox(837, 270, "Канал 4\n[Буфер]", size=9, min_w=60, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(877, 270, 867, 270, color=FIELD, sw=1.4))
    f.append(arrow(807, 270, 798, 270, color=FIELD, sw=1.4))

    # Фінал
    f.append(textbox(595, 270, "Вихідний\nприймач", size=10, min_w=80, pad=5, fill=PURPLE_F, stroke="#8e44ad")[0])
    f.append(arrow(702, 270, 635, 270, color="#8e44ad", sw=1.4))

    f.append(text(750, 375, "✓ Фільтри ізольовані; канали згладжують спалахи навантаження", size=10.5, color=FIELD, italic=True))

    render(out("direct-vs-pipeline.svg"), W, H, *f,
           title="Монолітний ланцюг обробки проти архітектури каналів і фільтрів")


# ── 2. pipeline-topology-variants: типові топології конвеєра ──────────────────
def fig_pipeline_topology_variants():
    W, H = 1000, 560
    f = []

    f.append(rect(10, 10, 980, 540, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Топологічні варіації патерну «Канали та фільтри»", size=14, bold=True))

    # 4 квадранти
    # 1. Лінійний конвеєр (Linear Pipeline)
    f.append(rect(25, 55, 465, 230, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(257, 77, "1. Лінійний конвеєр (Linear Pipeline)", size=12, bold=True, color=INK))
    f.append(textbox(75, 130, "Вхід", size=10, min_w=50, pad=4, fill="#ffffff", stroke=LINE)[0])
    f.append(arrow(100, 130, 120, 130, color=LINE))
    f.append(textbox(150, 130, "Фільтр A", size=10, min_w=60, pad=5, fill=BLUE_F, stroke=NEG)[0])
    f.append(arrow(180, 130, 200, 130, color=FIELD))
    f.append(textbox(235, 130, "Канал 1", size=9, min_w=55, pad=3, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(263, 130, 283, 130, color=FIELD))
    f.append(textbox(315, 130, "Фільтр B", size=10, min_w=60, pad=5, fill=BLUE_F, stroke=NEG)[0])
    f.append(arrow(345, 130, 365, 130, color=FIELD))
    f.append(textbox(400, 130, "Канал 2", size=9, min_w=55, pad=3, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(428, 130, 448, 130, color=LINE))
    f.append(text(257, 200, "Послідовна односпрямована обробка даних крок за кроком.", size=10, color=MUTED))
    f.append(text(257, 220, "Найпростіша форма: кожен фільтр виконує одну мутацію.", size=10, color=MUTED))

    # 2. Паралельне масштабування вузького місця (Parallel Stage / Competing Workers)
    f.append(rect(510, 55, 465, 230, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(742, 77, "2. Паралельне масштабування стадії (Worker Pool)", size=12, bold=True, color=INK))
    f.append(textbox(555, 130, "Фільтр A", size=10, min_w=55, pad=4, fill=BLUE_F, stroke=NEG)[0])
    f.append(arrow(583, 130, 605, 130, color=FIELD))
    f.append(textbox(645, 130, "Спільна\nчерга", size=9, min_w=60, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    # Стрілки на 3 паралельні воркери
    f.append(arrow(675, 130, 715, 100, color=NEG))
    f.append(arrow(675, 130, 715, 130, color=NEG))
    f.append(arrow(675, 130, 715, 160, color=NEG))
    f.append(textbox(760, 100, "Фільтр B (Воркер 1)", size=9, min_w=95, pad=3, fill=WARN_F, stroke="#d35400")[0])
    f.append(textbox(760, 130, "Фільтр B (Воркер 2)", size=9, min_w=95, pad=3, fill=WARN_F, stroke="#d35400")[0])
    f.append(textbox(760, 160, "Фільтр B (Воркер 3)", size=9, min_w=95, pad=3, fill=WARN_F, stroke="#d35400")[0])
    f.append(arrow(808, 100, 845, 130, color=FIELD))
    f.append(arrow(808, 130, 845, 130, color=FIELD))
    f.append(arrow(808, 160, 845, 130, color=FIELD))
    f.append(textbox(895, 130, "Канал 2", size=9, min_w=55, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(text(742, 210, "Горизонтальне розмноження важкого вузла (Competing Consumers)", size=10, color=MUTED))
    f.append(text(742, 230, "для усунення вузького місця конвеєра.", size=10, color=MUTED))

    # 3. Відгалуження та аудит (Tee / Wire Tap)
    f.append(rect(25, 300, 465, 230, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(257, 322, "3. Пасивне відгалуження (Tee / Wire Tap)", size=12, bold=True, color=INK))
    f.append(textbox(85, 375, "Фільтр 1", size=10, min_w=60, pad=4, fill=BLUE_F, stroke=NEG)[0])
    f.append(arrow(115, 375, 155, 375, color=LINE))
    # Вузол розгалуження Tee
    f.append(circle(165, 375, 6, fill=INK, stroke=INK))
    f.append(arrow(165, 375, 230, 375, color=FIELD))
    f.append(textbox(280, 375, "Канал основний", size=9.5, min_w=85, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(arrow(323, 375, 365, 375, color=FIELD))
    f.append(textbox(415, 375, "Фільтр 2", size=10, min_w=60, pad=4, fill=BLUE_F, stroke=NEG)[0])
    # Відгалуження вниз
    f.append(arrow(165, 375, 165, 440, color="#8e44ad", sw=1.4))
    f.append(textbox(165, 465, "Канал аудиту\n[Wire Tap]", size=9, min_w=80, pad=4, fill=PURPLE_F, stroke="#8e44ad")[0])
    f.append(arrow(205, 465, 250, 465, color="#8e44ad"))
    f.append(textbox(325, 465, "Сервіс метрик / SIEM", size=9.5, min_w=110, pad=4, fill="#ffffff", stroke="#8e44ad")[0])
    f.append(text(257, 510, "Неінвазивне копіювання потоку без впливу на основний конвеєр.", size=10, color=MUTED))

    # 4. Розділення та злиття (Splitter & Aggregator / Fork-Join)
    f.append(rect(510, 300, 465, 230, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(742, 322, "4. Розділення та злиття (Fork-Join Pipeline)", size=12, bold=True, color=INK))
    f.append(textbox(565, 375, "Спліттер\n(Splitter)", size=9.5, min_w=65, pad=4, fill=BLUE_F, stroke=NEG)[0])
    # Дві гілки
    f.append(arrow(598, 365, 635, 345, color=FIELD))
    f.append(arrow(598, 385, 635, 405, color=FIELD))
    f.append(textbox(685, 345, "Фільтр Аудіо", size=9, min_w=75, pad=3, fill=WARN_F, stroke="#d35400")[0])
    f.append(textbox(685, 405, "Фільтр Відео", size=9, min_w=75, pad=3, fill=WARN_F, stroke="#d35400")[0])
    f.append(arrow(723, 345, 760, 365, color=FIELD))
    f.append(arrow(723, 405, 760, 385, color=FIELD))
    f.append(textbox(805, 375, "Агрегатор\n(Join)", size=9.5, min_w=65, pad=4, fill=BLUE_F, stroke=NEG)[0])
    f.append(arrow(838, 375, 875, 375, color=LINE))
    f.append(textbox(920, 375, "Фінал", size=10, min_w=45, pad=4, fill=GREEN_F, stroke=FIELD)[0])
    f.append(text(742, 475, "Розподіл складеного повідомлення на незалежні потоки", size=10, color=MUTED))
    f.append(text(742, 495, "із наступним корельованим збиранням результату.", size=10, color=MUTED))

    render(out("pipeline-topology-variants.svg"), W, H, *f,
           title="Архітектурні варіації та топології каналів і фільтрів")


# ── 3. backpressure-queue-dynamics: протитиск у конвеєрі ──────────────────────
def fig_backpressure_queue_dynamics():
    W, H = 1000, 440
    f = []

    # Верхній сценарій: Обмежена черга з активним протитиском (Bounded Buffer + Backpressure)
    f.append(rect(15, 15, 970, 195, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 38, "Обмежений канал (Bounded Buffer): стабільність через активний протитиск", size=12.5, bold=True, color=FIELD))

    # Генератор
    f.append(textbox(110, 95, "Швидкий фільтр\n(Виробник)\nλ = 10 000 msg/s", size=10, min_w=120, pad=5, fill=BLUE_F, stroke=NEG)[0])

    # Стрілка на чергу
    f.append(arrow(170, 95, 230, 95, color=NEG, sw=1.8))

    # Обмежена черга
    f.append(rect(240, 60, 220, 70, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(350, 80, "Буфер каналу [Limit: 1000]", size=10, bold=True))
    # Слоти в буфері
    for i in range(7):
        fill_c = POS if i >= 4 else GREEN_F
        f.append(rect(255 + i * 27, 92, 22, 26, fill=fill_c, stroke=LINE, sw=1))
    f.append(text(350, 126, "Заповнено: 85% (High Watermark)", size=9.5, color=POS, bold=True))

    # Сигнал протитиску назад
    f.append(arrow(240, 145, 150, 145, color=POS, sw=1.8))
    f.append(text(195, 160, "← Сигнал призупинення (PAUSE / TCP Window = 0)", size=9.5, color=POS, bold=True))

    # Стрілка на споживача
    f.append(arrow(460, 95, 520, 95, color=FIELD, sw=1.5))

    # Повільний споживач
    f.append(textbox(600, 95, "Повільний фільтр\n(Споживач)\nμ = 2 000 msg/s", size=10, min_w=120, pad=5, fill=WARN_F, stroke="#d35400")[0])

    # Висновок верхнього блоку
    f.append(rect(740, 65, 225, 75, fill=GREEN_F, stroke=FIELD, sw=1, rx=4))
    f.append(text(852, 85, "Результат захисту:", size=10, bold=True, color=FIELD))
    f.append(text(852, 105, "• Фіксоване споживання RAM", size=9.5, color=INK))
    f.append(text(852, 123, "• Прогнозована затримка", size=9.5, color=INK))

    # Нижній сценарій: Необмежена черга без протитиску (Unbounded Buffer -> OOM)
    f.append(rect(15, 225, 970, 195, fill=GRAY_F, stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 248, "Необмежений канал (Unbounded Buffer): ілюзія буферизації та колапс пам'яті", size=12.5, bold=True, color=POS))

    f.append(textbox(110, 310, "Швидкий фільтр\n(Виробник)\nλ = 10 000 msg/s", size=10, min_w=120, pad=5, fill=BLUE_F, stroke=NEG)[0])
    f.append(arrow(170, 310, 230, 310, color=POS, sw=2))

    # Величезна роздута черга
    f.append(rect(240, 275, 260, 75, fill=RED_F, stroke=POS, sw=1.8, rx=4))
    f.append(text(370, 298, "Необмежена черга [Limit: ∞]", size=10.5, bold=True, color=POS))
    f.append(text(370, 318, "5 000 000 повідомлень у черзі...", size=9.5, color=POS))
    f.append(text(370, 336, "Затримка: > 40 хвилин | RAM: 18 GB", size=9.5, color=POS, bold=True))

    f.append(arrow(500, 310, 560, 310, color=LINE, sw=1.2))

    f.append(textbox(640, 310, "Повільний фільтр\n(Споживач)\nμ = 2 000 msg/s", size=10, min_w=120, pad=5, fill=WARN_F, stroke="#d35400")[0])

    # Наслідки нижнього блоку
    f.append(rect(770, 280, 195, 85, fill=RED_F, stroke=POS, sw=1, rx=4))
    f.append(text(867, 302, "Катастрофічний фінал:", size=10, bold=True, color=POS))
    f.append(text(867, 322, "• Out Of Memory (OOM Killer)", size=9.5, color=POS))
    f.append(text(867, 338, "• Деградація GC pauses", size=9.5, color=POS))
    f.append(text(867, 354, "• Втрата актуальності даних", size=9.5, color=POS))

    render(out("backpressure-queue-dynamics.svg"), W, H, *f,
           title="Динаміка протитиску та управління буферами в каналах")


# ── 4. stage-failure-recovery: ізоляція збоїв та обробка помилок ──────────────
def fig_stage_failure_recovery():
    W, H = 1000, 420
    f = []

    f.append(rect(10, 10, 980, 400, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Ізоляція збоїв та обробка отруйних повідомлень у розподіленому конвеєрі", size=14, bold=True))

    # Схема послідовності
    # Фільтр 1 (Успіх) -> Канал 1 -> Фільтр 2 (Збій/Помилка) -> DLQ або Повтор -> Канал 2 -> Фільтр 3
    f.append(textbox(100, 130, "Фільтр 1\n(Десеріалізатор)", size=10.5, min_w=110, pad=6, fill=GREEN_F, stroke=FIELD)[0])
    f.append(text(100, 180, "✓ ACK у вхідний канал", size=9.5, color=FIELD, bold=True))

    f.append(arrow(155, 130, 240, 130, color=FIELD, sw=1.5))
    f.append(textbox(280, 130, "Канал 1\n(Черга 1)", size=10, min_w=75, pad=5, fill=BLUE_F, stroke=NEG)[0])

    f.append(arrow(318, 130, 405, 130, color=NEG, sw=1.5))

    # Проблемний Фільтр 2
    f.append(textbox(470, 130, "Фільтр 2\n(Валідатор схеми)", size=10.5, min_w=115, pad=6, fill=WARN_F, stroke="#d35400", sw=1.8)[0])
    f.append(text(470, 80, "⚠ Отруйне повідомлення (Poison Pill)", size=9.5, color=POS, bold=True))

    # Варіанти реакції Фільтра 2:
    # 1. Успіх (штатний шлях далі)
    f.append(arrow(528, 130, 645, 130, color=FIELD, sw=1.4))
    f.append(text(585, 118, "Валідно", size=9.5, color=FIELD, bold=True))
    f.append(textbox(685, 130, "Канал 2\n(Черга 2)", size=10, min_w=75, pad=5, fill=BLUE_F, stroke=NEG)[0])
    f.append(arrow(723, 130, 805, 130, color=FIELD, sw=1.4))
    f.append(textbox(870, 130, "Фільтр 3\n(Персистенція)", size=10.5, min_w=110, pad=6, fill=GREEN_F, stroke=FIELD)[0])

    # 2. Помилка: локальний ретрай
    f.append(rect(390, 220, 160, 65, fill=GRAY_F, stroke=MUTED, sw=1, rx=4))
    f.append(text(470, 240, "Локальний повтор (Retry)", size=9.5, bold=True))
    f.append(text(470, 258, "Експоненційне уповільнення\n(3 спроби)", size=9.5, color=MUTED))
    f.append(arrow(440, 165, 440, 220, color=MUTED, sw=1.2))
    f.append(arrow(500, 220, 500, 165, color=MUTED, sw=1.2))

    # 3. Вичерпано спроби -> Мертва черга (DLQ)
    f.append(arrow(470, 285, 470, 330, color=POS, sw=1.8))
    f.append(textbox(470, 360, "МЕРТВА ЧЕРГА (DLQ)\nІзоляція для ручного аналізу", size=10, min_w=200, pad=6, fill=RED_F, stroke=POS, sw=1.5)[0])

    # Зворотний ACK при скиданні в DLQ
    f.append(arrow(370, 360, 280, 165, color=POS, sw=1.2))
    f.append(text(285, 270, "ACK з Каналу 1 після запису в DLQ\n(конвеєр не блокується)", size=9.5, color=POS, bold=True))

    f.append(text(500, 400, "Конвеєр продовжує обробляти здоровий потік, тоді як збійні пакети ізолюються в DLQ.", size=10.5, color=FIELD, italic=True))

    render(out("stage-failure-recovery.svg"), W, H, *f,
           title="Ізоляція збоїв та маршрутизація відмов у конвеєрі")


if __name__ == "__main__":
    fig_direct_vs_pipeline()
    fig_pipeline_topology_variants()
    fig_backpressure_queue_dynamics()
    fig_stage_failure_recovery()
    print("All figures generated successfully.")
