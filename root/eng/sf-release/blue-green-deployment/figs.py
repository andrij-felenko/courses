# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Топологія синьо-зеленого розгортання та перемикання трафіку ──────
def fig_blue_green_architecture_topology():
    W, H = 1000, 560
    frags = []

    # Заголовок
    frags.append(text(500, 25, "Топологія синьо-зеленого розгортання: атомарне перемикання L7-маршрутизатора",
                      size=15, bold=True, color=INK))

    # Клієнти
    client_box, cw, ch = textbox(500, 70, "Вхідний клієнтський трафік\n(HTTP/2, gRPC, REST, WebSockets)",
                                 size=12, bold=True, fill="#f8fafc", stroke=INK, sw=1.5, pad=8)
    frags.append(client_box)

    # Стрілка від клієнтів до роутера
    frags.append(arrow(500, 95, 500, 130, color=INK, sw=2.0))

    # L7 Роутер / Балансувальник
    router_box, rw, rh = textbox(500, 165, "L7 Балансувальник / Маршрутизатор (Envoy / NGINX / ALB)\nАтомарне перемикання активного цільового пулу за 1 мс",
                                 size=12, bold=True, fill="#fff9e6", stroke="#d97706", sw=1.8, pad=10)
    frags.append(router_box)

    # Ліва колонка: Синій (Blue) - Поточний активний
    blue_bg = rect(50, 230, 420, 190, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8)
    frags.append(blue_bg)
    frags.append(text(260, 255, "СИНЄ СЕРЕДОВИЩЕ (BLUE) — Версія v1", size=13, bold=True, color=NEG))
    frags.append(text(260, 275, "Поточний робочий продакшн (Active)", size=11, italic=True, color=MUTED))

    b_pod1, _, _ = textbox(150, 325, "Вузол 1 (v1)\n[Active]", size=11, bold=True, fill="#ffffff", stroke=NEG, sw=1.2, pad=6)
    b_pod2, _, _ = textbox(260, 325, "Вузол 2 (v1)\n[Active]", size=11, bold=True, fill="#ffffff", stroke=NEG, sw=1.2, pad=6)
    b_pod3, _, _ = textbox(370, 325, "Вузол 3 (v1)\n[Active]", size=11, bold=True, fill="#ffffff", stroke=NEG, sw=1.2, pad=6)
    frags.append(b_pod1)
    frags.append(b_pod2)
    frags.append(b_pod3)

    b_status, _, _ = textbox(260, 385, "Трафік до світчу: 100% | Після світчу: 0% (Standby Soak)\nМиттєвий відкат O(1) у разі аномалії на v2",
                             size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    frags.append(b_status)

    # Права колонка: Зелений (Green) - Нова версія
    green_bg = rect(530, 230, 420, 190, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8)
    frags.append(green_bg)
    frags.append(text(740, 255, "ЗЕЛЕНЕ СЕРЕДОВИЩЕ (GREEN) — Версія v2", size=13, bold=True, color=FIELD))
    frags.append(text(740, 275, "Новий реліз (Staging / Warmup / Target)", size=11, italic=True, color=MUTED))

    g_pod1, _, _ = textbox(630, 325, "Вузол 1 (v2)\n[Warmup]", size=11, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2, pad=6)
    g_pod2, _, _ = textbox(740, 325, "Вузол 2 (v2)\n[Warmup]", size=11, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2, pad=6)
    g_pod3, _, _ = textbox(850, 325, "Вузол 3 (v2)\n[Warmup]", size=11, bold=True, fill="#ffffff", stroke=FIELD, sw=1.2, pad=6)
    frags.append(g_pod1)
    frags.append(g_pod2)
    frags.append(g_pod3)

    g_status, _, _ = textbox(740, 385, "До світчу: 0% живого трафіку + синтетичні смоук-тести\nПісля світчу: 100% живого трафіку",
                             size=10, bold=False, fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    frags.append(g_status)

    # Стрілки маршрутизації від роутера
    # Лінія до Blue (суцільна, активна)
    frags.append(arrow(430, 195, 260, 230, color=NEG, sw=2.2))
    frags.append(text(310, 205, "100% трафіку (до)", size=11, bold=True, color=NEG))

    # Лінія до Green (пунктирна, перемикання)
    frags.append(line(570, 195, 740, 230, color=FIELD, sw=2.2, dash="5,4"))
    frags.append(text(690, 205, "100% трафіку (після світчу)", size=11, bold=True, color=FIELD))

    # Спільний шар стану (База даних, кеші, черги)
    db_bg = rect(180, 460, 640, 75, fill="#faf5ff", stroke="#7e22ce", sw=1.8, rx=8)
    frags.append(db_bg)
    frags.append(text(500, 485, "СПІЛЬНЕ ДЖЕРЕЛО СТАНУ (СУБД / Kafka / Redis)", size=12, bold=True, color="#7e22ce"))
    frags.append(text(500, 508, "Вимога: схема бази даних зобов'язана одночасно підтримувати версії v1 та v2 (Expand-Contract)",
                      size=10, italic=True, color=INK))

    # Зв'язки середовищ із базою даних
    frags.append(arrow(260, 420, 340, 460, color=NEG, sw=1.5))
    frags.append(arrow(740, 420, 660, 460, color=FIELD, sw=1.5))

    render(os.path.join(IMG, 'blue-green-architecture-topology.svg'), W, H, *frags,
           title="Архітектурна топологія синьо-зеленого розгортання")


# ── Фігура 2: Фази міграції схеми бази даних (Expand-Contract) ────────────────
def fig_database_expand_contract_phases():
    W, H = 1020, 530
    frags = []

    frags.append(text(510, 25, "Міграція схеми бази даних за патерном Expand-Contract (Паралельна зміна)",
                      size=15, bold=True, color=INK))

    col_w = 220
    gap = 20
    left_m = 35
    top_y = 55

    phases = [
        ("1. Початковий стан", "Base State (v1)", [
            ("Застосунок v1", "Активний (100%)", "#eff6ff", NEG),
            ("Застосунок v2", "Відсутній", "#f3f4f6", MUTED),
            ("Схема БД", "Колонка: full_name", "#faf5ff", "#7e22ce"),
            ("Читання/Запис", "v1 читає/пише full_name", "#ffffff", INK),
        ], "Базовий стан:\nєдина активна версія,\nнемає змін схеми."),

        ("2. Розширення", "Phase 1: Expand", [
            ("Застосунок v1", "Активний (100%)", "#eff6ff", NEG),
            ("Застосунок v2", "Розгортання у Green", "#f0fdf4", FIELD),
            ("Схема БД", "Додано: first_name,\nlast_name (NULLable)", "#faf5ff", "#7e22ce"),
            ("Синхронізація", "Тригер / Dual-write\nдублює дані у нові поля", "#fff9e6", "#d97706"),
        ], "Фаза Expand:\nдодано нові поля без NOT NULL.\nv1 і v2 сумісні."),

        ("3. Перемикання", "Phase 2: Cutover", [
            ("Застосунок v1", "Standby (0% трафіку)", "#eff6ff", MUTED),
            ("Застосунок v2", "Активний у Green (100%)", "#f0fdf4", FIELD),
            ("Схема БД", "first_name, last_name\n+ full_name (legacy)", "#faf5ff", "#7e22ce"),
            ("Читання/Запис", "v2 читає/пише нові поля,\nfull_name заповнюється", "#ffffff", INK),
        ], "Фаза Cutover:\nтрафік на v2.\nЯкщо треба відкат —\nv1 прочитає старі поля."),

        ("4. Звуження", "Phase 3: Contract", [
            ("Застосунок v1", "Знищено / вимкнено", "#fee2e2", "#b91c1c"),
            ("Застосунок v2", "Стабільний продакшн", "#f0fdf4", FIELD),
            ("Схема БД", "Видалено: full_name\nДодано NOT NULL", "#faf5ff", "#7e22ce"),
            ("Чистий стан", "Лише нові структури,\nвідкат на v1 неможливий", "#ffffff", INK),
        ], "Фаза Contract:\nстарий код знято з чергування.\nВидалення реліквій."),
    ]

    for idx, (title, sub, items, summary) in enumerate(phases):
        cx = left_m + idx * (col_w + gap) + col_w / 2
        cy = top_y

        hdr, _, _ = textbox(cx, cy + 20, f"{title}\n({sub})", size=12, bold=True,
                            fill="#f8fafc", stroke=INK, sw=1.6, pad=8)
        frags.append(hdr)

        curr_y = cy + 70
        for item_title, item_desc, bg_col, border_col in items:
            ibox, _, _ = textbox(cx, curr_y + 28, f"{item_title}\n{item_desc}", size=10.5, bold=True,
                                 fill=bg_col, stroke=border_col, sw=1.3, pad=6)
            frags.append(ibox)
            curr_y += 65

        sbox, _, _ = textbox(cx, curr_y + 40, summary, size=10, bold=False,
                             fill="#ffffff", stroke=MUTED, sw=1.1, pad=8)
        frags.append(sbox)

    render(os.path.join(IMG, 'database-expand-contract-phases.svg'), W, H, *frags,
           title="Життєвий цикл міграції бази даних за патерном Expand-Contract")


# ── Фігура 3: Часова шкала дренажу з'єднань і перемикання ─────────────────────
def fig_connection_draining_sequence():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 25, "Хронологія дренажу з'єднань при перемиканні трафіку Blue -> Green",
                      size=15, bold=True, color=INK))

    # Горизонтальна часова вісь
    frags.append(arrow(80, 80, 930, 80, color=INK, sw=2.0))
    frags.append(text(940, 85, "Час (t)", size=12, bold=True, color=INK, anchor="start"))

    time_points = [
        (140, "t0: Старт Green", "Green (v2) піднято\nСинтетичні тести"),
        (380, "t1: Світч L7", "Роутер направляє\nнові запити на Green"),
        (620, "t2: Вікно Drain", "Blue дообробляє\nактивні TCP/HTTP-сесії"),
        (860, "t3: Soak / Standby", "Blue спить без трафіку\nГотовий до відкоту O(1)"),
    ]

    for tx, tlabel, tdesc in time_points:
        frags.append(line(tx, 70, tx, 90, color=INK, sw=2.0))
        frags.append(text(tx, 60, tlabel, size=11, bold=True, color=INK))
        frags.append(textbox(tx, 125, tdesc, size=10, bold=False, fill="#f8fafc", stroke=MUTED, sw=1.0, pad=6)[0])

    # Дорожки (Swimlanes) для компонентів
    lanes = [
        ("L7 Балансувальник\n(Envoy / Ingress)", 195, [
            (80, 380, "Маршрутизація на Blue (100%)", "#eff6ff", NEG),
            (380, 920, "Маршрутизація на Green (100%) [HTTP/2 GOAWAY для Blue]", "#f0fdf4", FIELD),
        ]),
        ("Синє середовище\n(Blue v1 - Legacy)", 285, [
            (80, 380, "Повний обробіток запитів клієнтів", "#eff6ff", NEG),
            (380, 620, "Drain: обробка активних In-flight запитів (без прийому нових)", "#fff9e6", "#d97706"),
            (620, 920, "Standby Soak: нуль трафіку, збереження процесу в пам'яті для відкату", "#f8fafc", MUTED),
        ]),
        ("Зелене середовище\n(Green v2 - Target)", 385, [
            (80, 380, "Прогрів JIT, пулів БД, кешів + валідація зондами здоров'я", "#f8fafc", MUTED),
            (380, 920, "Прийом 100% живого трафіку клієнтів під контролем SLI/SLO метрик", "#f0fdf4", FIELD),
        ]),
    ]

    for lname, ly, blocks in lanes:
        l_box, _, _ = textbox(130, ly, lname, size=11, bold=True, fill="#f3f4f6", stroke=INK, sw=1.4, pad=6)
        frags.append(l_box)

        for bx1, bx2, btext, bfill, bstroke in blocks:
            bw = bx2 - bx1
            bh = 50
            brect = rect(bx1 + 100, ly - bh/2, bw, bh, fill=bfill, stroke=bstroke, sw=1.4, rx=6)
            frags.append(brect)
            # Текст всередині блоку
            t_cx = bx1 + 100 + bw / 2
            t_box = text(t_cx, ly + 4, fit_font(btext, bw - 16, 10.5, True),
                         size=fit_font(btext, bw - 16, 10.5, True), bold=True, color=INK)
            frags.append(t_box)

    render(os.path.join(IMG, 'connection-draining-sequence.svg'), W, H, *frags,
           title="Хронологія дренажу з'єднань і перемикання Blue-Green")


# ── Фігура 4: Скінченний автомат Argo Rollouts Blue-Green ──────────────────────
def fig_argo_rollouts_bluegreen_flow():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 25, "Скінченний автомат Blue-Green розгортання в Argo Rollouts",
                      size=15, bold=True, color=INK))

    states = [
        (130, 110, "1. Ініціалізація Green\n(Provisioning)", "Створення нового ReplicaSet\nМасштабування реплік до 100%", "#f8fafc", INK),
        (370, 110, "2. Зондування Preview\n(Smoke & Warmup)", "Спрямування тестового трафіку\nна preview-service; прогрів кешу", "#fff9e6", "#d97706"),
        (630, 110, "3. Pre-Promotion аналіз\n(SLI Verification)", "Перевірка частоти помилок,\nзатримок та метрик Prometheus", "#eff6ff", NEG),
        (870, 110, "4. Просування (Promoted)\n(Active Switch)", "Active Service переключає\nселектор на новий ReplicaSet", "#f0fdf4", FIELD),

        (870, 310, "5. Період вистоювання\n(scaleDownDelay / Soak)", "Старий ReplicaSet активний\nв режимі очікування відкату", "#fff9e6", "#d97706"),
        (500, 310, "6. Фінал або Відкат\n(Decommission / Rollback)", "Успіх: scaleDown старого до 0\nАномалія: миттєвий відкат селектора", "#faf5ff", "#7e22ce"),
    ]

    for sx, sy, stitle, sdesc, sfill, sstroke in states:
        sbox, _, _ = textbox(sx, sy, f"{stitle}\n{sdesc}", size=11, bold=True,
                             fill=sfill, stroke=sstroke, sw=1.6, pad=8)
        frags.append(sbox)

    # Стрілки між станами
    frags.append(arrow(210, 110, 280, 110, color=INK, sw=2.0))
    frags.append(arrow(460, 110, 540, 110, color=INK, sw=2.0))
    frags.append(arrow(720, 110, 780, 110, color=INK, sw=2.0))
    frags.append(arrow(870, 160, 870, 250, color=INK, sw=2.0))
    frags.append(arrow(780, 310, 620, 310, color=INK, sw=2.0))

    # Стрілка аварійного відкату від аналізу до фіналу
    frags.append(arrow(630, 160, 530, 250, color=POS, sw=2.0))
    frags.append(text(625, 210, "Провал SLI (Аварійний Stop)", size=10, bold=True, color=POS))

    render(os.path.join(IMG, 'argo-rollouts-bluegreen-flow.svg'), W, H, *frags,
           title="Скінченний автомат життєвого циклу Argo Rollouts Blue-Green")


if __name__ == '__main__':
    fig_blue_green_architecture_topology()
    fig_database_expand_contract_phases()
    fig_connection_draining_sequence()
    fig_argo_rollouts_bluegreen_flow()
    print("All figures generated successfully.")
