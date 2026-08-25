# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Архітектурна топологія темного запуску ─────────────────────────
def fig_dark_launch_topology():
    W, H = 940, 480
    frags = []

    # Клієнт
    client_box, cw, ch = textbox(110, 180, "Користувач / Клієнт\n(HTTP / gRPC)", size=13, bold=True,
                                 fill="#f3f4f6", stroke=INK, sw=1.6, pad=12)
    frags.append(client_box)

    # Шлюз / Маршрутизатор
    gw_box, gw_w, gw_h = textbox(340, 180, "Шлюз / API Gateway\n(Клонування трафіку)", size=13, bold=True,
                                 fill="#eef4ff", stroke=NEG, sw=2, pad=14)
    frags.append(gw_box)

    # Стрілка Клієнт -> Шлюз
    frags.append(arrow(185, 180, 245, 180, color=INK, sw=1.8))
    frags.append(text(215, 168, "Запит", size=11, color=MUTED))

    # Стрілка Шлюз -> Клієнт (Відповідь v1)
    frags.append(arrow(245, 200, 185, 200, color=FIELD, sw=1.8))
    frags.append(text(215, 218, "Відповідь v1", size=11, color=FIELD, bold=True))

    # Основний сервіс (v1)
    v1_box, v1_w, v1_h = textbox(590, 110, "Основний сервіс v1\n(Перевірена логіка)", size=13, bold=True,
                                 fill="#f6faf7", stroke=FIELD, sw=2, pad=12)
    frags.append(v1_box)

    # Основна база даних
    db1_box, db1_w, db1_h = textbox(820, 110, "Основна БД / Стан\n(Читання + Запис)", size=12, bold=True,
                                   fill="#ffffff", stroke=FIELD, sw=1.5, pad=10)
    frags.append(db1_box)

    # Зв'язок Шлюз -> v1 (синхронний)
    frags.append(arrow(435, 160, 500, 125, color=FIELD, sw=2))
    frags.append(text(460, 132, "Синхронно", size=11, color=FIELD, bold=True))

    # Зв'язок v1 -> БД1
    frags.append(arrow(680, 110, 740, 110, color=FIELD, sw=1.6))

    # Зв'язок v1 -> Шлюз (відповідь)
    frags.append(arrow(500, 140, 435, 175, color=FIELD, sw=1.6))

    # Тіньовий сервіс (v2)
    v2_box, v2_w, v2_h = textbox(590, 270, "Тіньовий сервіс v2\n(Новий код під тестом)", size=13, bold=True,
                                 fill="#fff9e6", stroke="#d97706", sw=2, pad=12)
    frags.append(v2_box)

    # Тіньова ізольована база / Мок
    db2_box, db2_w, db2_h = textbox(820, 270, "Ізольоване середовище\n(Read-only / Sandbox)", size=12, bold=True,
                                   fill="#ffffff", stroke="#d97706", sw=1.5, pad=10)
    frags.append(db2_box)

    # Зв'язок Шлюз -> v2 (асинхронне клонування)
    frags.append(arrow(435, 200, 500, 255, color="#d97706", sw=2))
    frags.append(text(460, 245, "Асинхронний клон", size=11, color="#d97706", bold=True))

    # Зв'язок v2 -> БД2
    frags.append(arrow(680, 270, 730, 270, color="#d97706", sw=1.6))

    # Диференційний компаратор
    comp_box, comp_w, comp_h = textbox(590, 410, "Диференційний компаратор\n(Порівняння відповідей v1 vs v2)", size=13, bold=True,
                                       fill="#eef4ff", stroke=NEG, sw=1.8, pad=12)
    frags.append(comp_box)

    # Зв'язки v1 і v2 до компаратора
    frags.append(line(630, 145, 630, 370, color=MUTED, sw=1.4, dash="3,3"))
    frags.append(line(590, 310, 590, 370, color=MUTED, sw=1.4, dash="3,3"))
    frags.append(text(660, 340, "Результати", size=11, color=MUTED))

    # Моніторинг і логи розбіжностей
    telemetry_box, tel_w, tel_h = textbox(820, 410, "Метрики, логи\nі алерти про розбіжності", size=12, bold=True,
                                          fill="#ffffff", stroke=NEG, sw=1.5, pad=10)
    frags.append(telemetry_box)
    frags.append(arrow(705, 410, 735, 410, color=NEG, sw=1.8))

    render(os.path.join(IMG, 'dark-launch-topology.svg'), W, H, *frags,
           title="Архітектурна топологія темного запуску")


# ── Фігура 2: П'ять етапів міграції за прапорцями ────────────────────────────
def fig_migration_stages():
    W, H = 940, 420
    frags = []

    stages = [
        ("Етап 0", "Тихий деплой", "Прапорець 0%\nКод у проді,\nале вимкнений", "#6b7280"),
        ("Етап 1", "Темний запуск", "0% для людей\n10% → 100% клону\nтрафіку в тіні", "#d97706"),
        ("Етап 2", "Звірка даних", "Диференційне\nпорівняння відповідей,\nвиправлення багів", NEG),
        ("Етап 3", "Канарка", "1% → 25% → 50%\nживого трафіку\nна новий сервіс", FIELD),
        ("Етап 4", "100% і очищення", "100% трафіку,\nвидалення старого\nкоду і прапорця", POS),
    ]

    col_w = W / len(stages)
    for i, (stage_num, title_text, desc, col) in enumerate(stages):
        cx = i * col_w + col_w / 2
        cy = 130

        # Номер і назва етапу
        hb, hw, hh = textbox(cx, cy, f"{stage_num}\n{title_text}", size=13, bold=True,
                             fill="#ffffff", stroke=col, sw=2, pad=10, min_w=150)
        frags.append(hb)

        # Опис під блоком
        db, dw, dh = textbox(cx, cy + 110, desc, size=11, bold=False,
                             fill="#f8fafc", stroke=col, sw=1.2, pad=10, min_w=150)
        frags.append(db)

        # Стрілка між блоками етапів
        if i < len(stages) - 1:
            frags.append(arrow(cx + hw / 2 + 5, cy, cx + col_w - hw / 2 - 5, cy, color=MUTED, sw=2))

    # Нижня стрілка прогресу ризику і зрілості
    frags.append(rect(60, 320, W - 120, 50, fill="#f4f6f8", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(W / 2, 342, "Поступове зниження невизначеності: від нульового ризику для користувачів до перевіреного релізу",
                      size=12, bold=True, color=INK))
    frags.append(arrow(100, 358, W - 100, 358, color=FIELD, sw=2))

    render(os.path.join(IMG, 'migration-stages.svg'), W, H, *frags,
           title="П'ять етапів безпечної міграції за допомогою прапорців функцій")


# ── Фігура 3: Конвеєр диференційного тестування ──────────────────────────────
def fig_differential_testing_pipeline():
    W, H = 940, 440
    frags = []

    # Вхідні дані v1 і v2
    b_v1, _, _ = textbox(130, 120, "Відповідь v1 (Control)\nJSON / DTO / Record", size=12, bold=True,
                         fill="#f6faf7", stroke=FIELD, sw=1.8, pad=10)
    b_v2, _, _ = textbox(130, 260, "Відповідь v2 (Candidate)\nJSON / DTO / Record", size=12, bold=True,
                         fill="#fff9e6", stroke="#d97706", sw=1.8, pad=10)
    frags.append(b_v1)
    frags.append(b_v2)

    # Блок нормалізації та маскування
    norm_box, nw, nh = textbox(410, 190, "Нормалізатор і маска шуму\n• Ігнорування timestamp\n• Маскування random/UUID\n• Канонічне сортування ключів\n• Округлення float (ε-похибка)",
                               size=12, bold=False, fill="#eef4ff", stroke=NEG, sw=2, pad=14, min_w=220)
    frags.append(norm_box)

    frags.append(arrow(220, 120, 290, 160, color=FIELD, sw=1.6))
    frags.append(arrow(220, 260, 290, 220, color="#d97706", sw=1.6))

    # Блок глибокого порівняння
    comp_box, cw, ch = textbox(670, 190, "Глибокий компаратор\n(Побайтова / попольна звірка)", size=13, bold=True,
                               fill="#ffffff", stroke=INK, sw=2, pad=12)
    frags.append(comp_box)

    frags.append(arrow(530, 190, 580, 190, color=INK, sw=1.8))
    frags.append(text(555, 175, "Канонічні DTO", size=10, color=MUTED))

    # Результат 1: Збіг
    frags.append(arrow(750, 160, 810, 110, color=FIELD, sw=2))
    match_box, _, _ = textbox(870, 110, "Збіг (Match)\nІнкремент метрики успіху", size=11, bold=True,
                              fill="#f6faf7", stroke=FIELD, sw=1.6, pad=8)
    frags.append(match_box)

    # Результат 2: Розбіжність
    frags.append(arrow(750, 220, 810, 270, color=POS, sw=2))
    mismatch_box, _, _ = textbox(870, 270, "Розбіжність (Mismatch)\nСтруктурований Diff у логи,\nалерт і трасування", size=11, bold=True,
                                 fill="#fdf2f2", stroke=POS, sw=1.6, pad=8)
    frags.append(mismatch_box)

    # Нижній напис-інваріант
    frags.append(fitbox(150, 360, 640, 44, "Користувач завжди отримує v1; жоден збій компаратора чи v2 не впливає на клієнта",
                        size=12, fill="#f8fafc", stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'differential-testing-pipeline.svg'), W, H, *frags,
           title="Конвеєр диференційного тестування відповідей")


if __name__ == '__main__':
    fig_dark_launch_topology()
    fig_migration_stages()
    fig_differential_testing_pipeline()
    print("Усі фігури згенеровано успішно.")
