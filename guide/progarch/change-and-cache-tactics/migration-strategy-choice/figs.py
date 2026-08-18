# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір стратегії зміни живої системи»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_migration_taxonomy_matrix():
    """Матриця вибору стратегії міграції за ризиком та вимогами до SLA."""
    W, H = 960, 520
    frags = []

    # Фон матриці
    frags.append(rect(100, 50, 780, 400, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))

    # Осі матриці
    frags.append(line(490, 50, 490, 450, color=MUTED, sw=1.5, dash="6,4"))
    frags.append(line(100, 250, 880, 250, color=MUTED, sw=1.5, dash="6,4"))

    # Підписи осей
    frags.append(text(490, 25, "Вимоги до SLA / Недопустимість простою (Downtime Tolerance)", size=13, bold=True, color=INK))
    frags.append(text(490, 480, "Складність стану та ризик втрати даних (State & Financial Risk) →", size=13, bold=True, color=INK))

    # Квадрант 1: Expand-Contract (Низький ризик стану / Високий SLA)
    frags.append(rect(120, 70, 340, 160, fill="#e8f4f8", stroke="#1b6ec2", sw=1.8, rx=8))
    frags.append(text(290, 95, "Expand-Contract", size=15, bold=True, color="#1b6ec2"))
    frags.append(text(290, 118, "Паралельна зміна схем БД та API", size=11, color=INK))
    frags.append(line(140, 130, 440, 130, color="#1b6ec2", sw=1, dash="4,4"))
    frags.append(text(290, 150, "• Локальні зміни контрактів", size=11, color=INK))
    frags.append(text(290, 170, "• Нульовий downtime схеми", size=11, color=INK))
    frags.append(text(290, 190, "• Багатоетапний деплой", size=11, color=MUTED))

    # Квадрант 2: Parallel Run (Високий ризик стану / Високий SLA)
    frags.append(rect(510, 70, 340, 160, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    frags.append(text(680, 95, "Parallel Run (Dual Run)", size=15, bold=True, color=POS))
    frags.append(text(680, 118, "Паралельне виконання 100% трафіку", size=11, color=INK))
    frags.append(line(530, 130, 830, 130, color=POS, sw=1, dash="4,4"))
    frags.append(text(680, 150, "• Фінансові обчислення, білінг", size=11, color=INK))
    frags.append(text(680, 170, "• Звіряння виходів у реальному часі", size=11, color=INK))
    frags.append(text(680, 190, "• Висока ціна подвійної інфраструктури", size=11, color=MUTED))

    # Квадрант 3: Strangler Fig (Еволюційна витісняюча міграція)
    frags.append(rect(120, 270, 340, 160, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(290, 295, "Strangler Fig", size=15, bold=True, color=FIELD))
    frags.append(text(290, 318, "Покрокове витіснення моноліту", size=11, color=INK))
    frags.append(line(140, 330, 440, 330, color=FIELD, sw=1, dash="4,4"))
    frags.append(text(290, 350, "• Перехоплення на периметрі API", size=11, color=INK))
    frags.append(text(290, 370, "• Заміна сервіс за сервісом", size=11, color=INK))
    frags.append(text(290, 390, "• Без ризику Big Bang релізу", size=11, color=MUTED))

    # Квадрант 4: Dark Launch (Перевірка продуктивності та навантаження)
    frags.append(rect(510, 270, 340, 160, fill="#fff8e1", stroke="#d97706", sw=1.8, rx=8))
    frags.append(text(680, 295, "Dark Launch (Shadow)", size=15, bold=True, color="#d97706"))
    frags.append(text(680, 318, "Тіньовий трафік без впливу на відповідь", size=11, color=INK))
    frags.append(line(530, 330, 830, 330, color="#d97706", sw=1, dash="4,4"))
    frags.append(text(680, 350, "• Валідація latency та TPS", size=11, color=INK))
    frags.append(text(680, 370, "• Ізоляція побічних ефектів", size=11, color=INK))
    frags.append(text(680, 390, "• 0% впливу на користувача", size=11, color=MUTED))

    render(os.path.join(IMG, "migration-taxonomy-matrix.svg"), W, H, *frags,
           title="Матриця вибору стратегії міграції за ризиком та вимогами до SLA")


def fig_strangler_fig_evolution():
    """Еволюційне витіснення моноліту за патерном Strangler Fig."""
    W, H = 960, 480
    frags = []

    stages = [
        ("Етап 1: Моноліт", "100% трафіку у моноліт", "#fdecea", POS, [
            ("API Gateway", "#ffffff", INK),
            ("Моноліт (Всі домени)", "#f8d7da", POS),
        ]),
        ("Етап 2: Виділення 1-го сервісу", "Витіснення /orders", "#fff3cd", "#d97706", [
            ("API Gateway (Router)", "#ffffff", INK),
            ("Мікросервіс Замовлень", "#d1e7dd", FIELD),
            ("Моноліт (Решта доменів)", "#f8d7da", POS),
        ]),
        ("Етап 3: Зріла сітка", "80% доменів винесено", "#eafaf0", FIELD, [
            ("API Gateway (Router)", "#ffffff", INK),
            ("Сервіси: Order, User, Pay", "#d1e7dd", FIELD),
            ("Моноліт (Ядро/Залишок)", "#f8d7da", POS),
        ]),
        ("Етап 4: Фінал", "Моноліт вимкнено", "#e8f4f8", "#1b6ec2", [
            ("API Gateway (Router)", "#ffffff", INK),
            ("Повна мікросервісна сітка", "#cff4fc", "#1b6ec2"),
            ("Моноліт: DECOMMISSIONED", "#e2e3e5", MUTED),
        ]),
    ]

    box_w = 210
    gap = 25
    x_start = 25
    y_top = 40

    for i, (st_title, st_desc, bg_col, border_col, items) in enumerate(stages):
        x = x_start + i * (box_w + gap)

        frags.append(rect(x, y_top, box_w, 400, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(x + box_w / 2, y_top + 25, st_title, size=13, bold=True, color=border_col))
        frags.append(text(x + box_w / 2, y_top + 45, st_desc, size=10, color=MUTED))
        frags.append(line(x + 15, y_top + 60, x + box_w - 15, y_top + 60, color=border_col, sw=1, dash="4,4"))

        y_item = y_top + 80
        for it_name, it_fill, it_color in items:
            frags.append(rect(x + 15, y_item, box_w - 30, 75, fill=it_fill, stroke=it_color, sw=1.2, rx=6))
            frags.append(mtext(x + box_w / 2, y_item + 25, it_name.split("\n"), size=11, bold=True, color=it_color))
            y_item += 95

        if i < len(stages) - 1:
            frags.append(arrow(x + box_w, y_top + 200, x + box_w + gap, y_top + 200, color=border_col, sw=2.0))

    render(os.path.join(IMG, "strangler-fig-evolution.svg"), W, H, *frags,
           title="Еволюційне витіснення моноліту за патерном Strangler Fig")


def fig_dark_launch_and_parallel_run():
    """Порівняння темного запуску (Dark Launch) та паралельного виконання (Parallel Run)."""
    W, H = 960, 480
    frags = []

    # ── Блок 1: Dark Launch ──
    frags.append(rect(30, 40, 435, 410, fill="#fffdf5", stroke="#d97706", sw=1.8, rx=8))
    frags.append(text(247, 70, "Dark Launch (Shadow Traffic)", size=15, bold=True, color="#d97706"))
    frags.append(text(247, 90, "Асинхронне дублювання трафіку без ризику для SLA", size=10, color=MUTED))
    frags.append(line(50, 105, 445, 105, color="#d97706", sw=1, dash="4,4"))

    frags.append(rect(50, 130, 110, 50, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(105, 160, "Запит клієнта", size=11, bold=True, color=INK))

    frags.append(rect(200, 130, 100, 50, fill="#fdf6e3", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(250, 160, "Shadow Router", size=11, bold=True, color="#d97706"))

    frags.append(arrow(160, 155, 200, 155, color=INK, sw=1.5))

    # Основний шлях (Sync)
    frags.append(arrow(300, 155, 340, 155, color=FIELD, sw=2.0))
    frags.append(rect(340, 130, 110, 50, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(395, 153, "Стара система", size=11, bold=True, color=FIELD))
    frags.append(text(395, 170, "(Відповідь клієнту)", size=9, color=FIELD))

    # Тіньовий шлях (Async Mirror)
    frags.append(arrow(250, 180, 250, 260, color="#d97706", sw=1.8))
    frags.append(text(275, 220, "Shadow Copy", size=10, bold=True, color="#d97706"))

    frags.append(rect(180, 260, 140, 55, fill="#fff3cd", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(250, 283, "Нова система", size=11, bold=True, color="#d97706"))
    frags.append(text(250, 300, "(Тестовий екземпляр)", size=9, color=MUTED))

    frags.append(arrow(250, 315, 250, 360, color=MUTED, sw=1.5))
    frags.append(rect(170, 360, 160, 55, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(250, 383, "Відповідь відкидається", size=11, bold=True, color=MUTED))
    frags.append(text(250, 400, "Запис метрик / Latency", size=9, color=MUTED))


    # ── Блок 2: Parallel Run ──
    frags.append(rect(495, 40, 435, 410, fill="#fef8f8", stroke=POS, sw=1.8, rx=8))
    frags.append(text(712, 70, "Parallel Run (Dual Run)", size=15, bold=True, color=POS))
    frags.append(text(712, 90, "Паралельне виконання з порівнянням результатів", size=10, color=MUTED))
    frags.append(line(515, 105, 910, 105, color=POS, sw=1, dash="4,4"))

    frags.append(rect(515, 130, 100, 50, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    frags.append(text(565, 160, "Запит клієнта", size=11, bold=True, color=INK))

    frags.append(rect(640, 130, 95, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(687, 160, "Dual Router", size=11, bold=True, color=POS))

    frags.append(arrow(615, 155, 640, 155, color=INK, sw=1.5))

    # Розгалуження на Стару та Нову системи (по горизонталі)
    # Стара (v1) ліворуч, Нова (v2) праворуч
    frags.append(arrow(687, 180, 600, 240, color=FIELD, sw=1.5))
    frags.append(rect(535, 240, 130, 45, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(600, 267, "Стара система (v1)", size=11, bold=True, color=FIELD))

    frags.append(arrow(687, 180, 775, 240, color=POS, sw=1.5))
    frags.append(rect(710, 240, 130, 45, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    frags.append(text(775, 267, "Нова система (v2)", size=11, bold=True, color=POS))

    # Сходження на Reconciler
    frags.append(arrow(600, 285, 687, 330, color=FIELD, sw=1.5))
    frags.append(arrow(775, 285, 687, 330, color=POS, sw=1.5))

    frags.append(rect(612, 330, 150, 50, fill="#fff3cd", stroke=POS, sw=1.5, rx=6))
    frags.append(text(687, 352, "Reconciler Engine", size=11, bold=True, color=POS))
    frags.append(text(687, 368, "Звіряння розбіжностей", size=10, color=INK))

    frags.append(arrow(687, 380, 687, 405, color=POS, sw=1.5))
    frags.append(rect(602, 405, 170, 35, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(687, 427, "Алерт при незбігу виходів", size=10, bold=True, color=POS))

    render(os.path.join(IMG, "dark-launch-and-parallel-run.svg"), W, H, *frags,
           title="Порівняння темного запуску (Dark Launch) та паралельного виконання (Parallel Run)")


def fig_expand_contract_lifecycle():
    """П'ять фаз життєвого циклу Expand-Contract для бази даних та API."""
    W, H = 960, 440
    frags = []

    phases = [
        ("1. Base State", "Схема v1", "Читання й запис лише в старих полях", "#eef2f7", INK),
        ("2. Expand", "Додано v2", "Нові колонки додано в БД (nullable)", "#e8f4f8", "#1b6ec2"),
        ("3. Dual-Write", "Подвійний запис", "Код пише у v1 і v2, бекфілл даних", "#fff3cd", "#d97706"),
        ("4. Read Switch", "Перемикання", "Код читає з v2, фолбек на v1", "#eafaf0", FIELD),
        ("5. Contract", "Очищення", "Видалено v1, міграцію завершено", "#fdecea", POS),
    ]

    box_w = 160
    gap = 25
    x_start = 20
    y_top = 50

    for i, (p_title, p_sub, p_desc, bg_col, border_col) in enumerate(phases):
        x = x_start + i * (box_w + gap)

        frags.append(rect(x, y_top, box_w, 330, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(x + box_w / 2, y_top + 30, p_title, size=13, bold=True, color=border_col))
        frags.append(text(x + box_w / 2, y_top + 55, p_sub, size=11, bold=True, color=INK))
        frags.append(line(x + 10, y_top + 75, x + box_w - 10, y_top + 75, color=border_col, sw=1, dash="4,4"))

        frags.append(mtext(x + box_w / 2, y_top + 120, p_desc.split("\n"), size=10, color=INK))

        # Візуалізація стану поля
        frags.append(rect(x + 15, y_top + 220, box_w - 30, 80, fill="#ffffff", stroke=border_col, sw=1.2, rx=6))
        if i == 0:
            frags.append(text(x + box_w / 2, y_top + 265, "[ v1_col ]", size=12, bold=True, color=INK))
        elif i == 1:
            frags.append(text(x + box_w / 2, y_top + 253, "[ v1_col ]", size=11, color=INK))
            frags.append(text(x + box_w / 2, y_top + 278, "+ [ v2_col ]", size=11, bold=True, color="#1b6ec2"))
        elif i == 2:
            frags.append(text(x + box_w / 2, y_top + 253, "Write -> v1", size=10, color=MUTED))
            frags.append(text(x + box_w / 2, y_top + 278, "Write -> v2", size=10, bold=True, color="#d97706"))
        elif i == 3:
            frags.append(text(x + box_w / 2, y_top + 253, "Read <- v2", size=11, bold=True, color=FIELD))
            frags.append(text(x + box_w / 2, y_top + 278, "(fallback v1)", size=9, color=MUTED))
        elif i == 4:
            frags.append(text(x + box_w / 2, y_top + 265, "[ v2_col ]", size=12, bold=True, color=POS))

        if i < len(phases) - 1:
            frags.append(arrow(x + box_w, y_top + 165, x + box_w + gap, y_top + 165, color=border_col, sw=2.0))

    render(os.path.join(IMG, "expand-contract-lifecycle.svg"), W, H, *frags,
           title="П'ять фаз життєвого циклу Expand-Contract для бази даних та API")


if __name__ == "__main__":
    fig_migration_taxonomy_matrix()
    fig_strangler_fig_evolution()
    fig_dark_launch_and_parallel_run()
    fig_expand_contract_lifecycle()
    print("Всі 4 фігури згенеровано успішно.")
