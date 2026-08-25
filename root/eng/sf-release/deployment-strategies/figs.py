# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Порівняння 4 стратегій ─────────────────────────────────────────
def fig_deployment_strategies_comparison():
    W, H = 960, 520
    frags = []

    col_w = 215
    col_gap = 15
    left_m = 30
    top_m = 40

    strategies = [
        ("Перестворення", "Recreate / Big Bang", [
            ("Час t0", "v1 [100%]", "#eef4ff", INK),
            ("Час t1", "ПРОСТІЙ [0%]", "#fee2e2", "#b91c1c"),
            ("Час t2", "v2 [100%]", "#f6faf7", FIELD),
        ], "Ресурси: 1.0x (без надлишку)\nПростій: Є (повна пауза)\nРадіус ураження: 100%\nВідкіт: Повільний (новий деплой)"),

        ("Почергове", "Rolling Update", [
            ("Час t0", "v1: 100% | v2: 0%", "#eef4ff", INK),
            ("Час t1", "v1: 50%  | v2: 50%", "#fff9e6", "#d97706"),
            ("Час t2", "v1: 0%   | v2: 100%", "#f6faf7", FIELD),
        ], "Ресурси: 1.0x + maxSurge\nПростій: Немає (0 завалів)\nРадіус ураження: Поступовий\nВідкіт: Поступовий O(N)"),

        ("Синьо-зелене", "Blue / Green", [
            ("Час t0", "Синій (v1): 100% живий\nЗелений (v2): 0% стендбай", "#eef4ff", INK),
            ("Час t1", "Перемикання роутера\n(миттєвий світч L7)", "#fff9e6", "#d97706"),
            ("Час t2", "Синій (v1): 0% стендбай\nЗелений (v2): 100% живий", "#f6faf7", FIELD),
        ], "Ресурси: 2.0x (подвійний парк)\nПростій: Немає (миттєвий)\nРадіус ураження: 100% одразу\nВідкіт: Миттєвий O(1)"),

        ("Канаркове", "Canary / Progressive", [
            ("Час t0", "v1: 95% | v2: 5% (тест)", "#fff9e6", "#d97706"),
            ("Час t1", "Метрики OK → 25% → 50%", "#fff9e6", "#d97706"),
            ("Час t2", "v1: 0%  | v2: 100% фінал", "#f6faf7", FIELD),
        ], "Ресурси: 1.0x + канарка\nПростій: Немає (плавний рух)\nРадіус ураження: Мінімальний (5%)\nВідкіт: Автоматичний за SLA"),
    ]

    for idx, (title, sub, stages, summary) in enumerate(strategies):
        cx = left_m + idx * (col_w + col_gap) + col_w / 2
        cy = top_m

        hdr_box, hw, hh = textbox(cx, cy + 20, f"{title}\n({sub})", size=13, bold=True,
                                  fill="#f3f4f6", stroke=INK, sw=1.8, pad=10)
        frags.append(hdr_box)

        curr_y = cy + 70
        for st_name, st_desc, bg_col, border_col in stages:
            st_box, sw_b, sh_b = textbox(cx, curr_y + 35, f"{st_name}\n{st_desc}", size=11, bold=True,
                                         fill=bg_col, stroke=border_col, sw=1.5, pad=8)
            frags.append(st_box)
            curr_y += 75

        sum_box, sum_w, sum_h = textbox(cx, curr_y + 60, summary, size=11, bold=False,
                                        fill="#ffffff", stroke=MUTED, sw=1.2, pad=10)
        frags.append(sum_box)

    render(os.path.join(IMG, 'deployment-strategies-comparison.svg'), W, H, *frags,
           title="Порівняння чотирьох фундаментальних стратегій розгортання")


# ── Фігура 2: Rolling update детальна анатомія ────────────────────────────────
def fig_rolling_update_surge_unavailable():
    W, H = 1020, 460
    frags = []

    frags.append(text(510, 25, "Анатомія Rolling Update: Баланс між maxSurge та maxUnavailable",
                      size=14, bold=True, color=INK))

    steps = [
        ("Крок 0: Базовий стан\n(4 репліки v1)", 80, [
            ("Подік 1 (v1)", "#eef4ff", INK),
            ("Подік 2 (v1)", "#eef4ff", INK),
            ("Подік 3 (v1)", "#eef4ff", INK),
            ("Подік 4 (v1)", "#eef4ff", INK),
        ], "Ємність: 4/4\n(100% v1)"),

        ("Крок 1: maxSurge=1\n(Створення буфера)", 175, [
            ("Подік 1 (v1)", "#eef4ff", INK),
            ("Подік 2 (v1)", "#eef4ff", INK),
            ("Подік 3 (v1)", "#eef4ff", INK),
            ("Подік 4 (v1)", "#eef4ff", INK),
            ("Подік 5 (v2 [ініт])", "#fff9e6", "#d97706"),
        ], "Ємність: 4 живих\n+ 1 прогрів"),

        ("Крок 2: Readiness OK\n(Drain старого v1)", 270, [
            ("Подік 1 (v1 [Drain])", "#fee2e2", "#b91c1c"),
            ("Подік 2 (v1)", "#eef4ff", INK),
            ("Подік 3 (v1)", "#eef4ff", INK),
            ("Подік 4 (v1)", "#eef4ff", INK),
            ("Подік 5 (v2 [Active])", "#f6faf7", FIELD),
        ], "Трафік іде на v2,\nv1 вимикається"),

        ("Крок 3: Фінал\n(Повне оновлення)", 365, [
            ("Подік 1 (v2)", "#f6faf7", FIELD),
            ("Подік 2 (v2)", "#f6faf7", FIELD),
            ("Подік 3 (v2)", "#f6faf7", FIELD),
            ("Подік 4 (v2)", "#f6faf7", FIELD),
        ], "Ємність: 4/4\n(100% v2)"),
    ]

    for step_title, y_pos, pods, status_str in steps:
        lbl_box, lw, lh = textbox(120, y_pos, step_title, size=11, bold=True,
                                  fill="#f3f4f6", stroke=INK, sw=1.4, pad=8)
        frags.append(lbl_box)

        start_x = 280
        for p_idx, (p_name, fill_c, strk_c) in enumerate(pods):
            px = start_x + p_idx * 115
            p_box, pw, ph = textbox(px, y_pos, p_name, size=10, bold=True,
                                    fill=fill_c, stroke=strk_c, sw=1.4, pad=6)
            frags.append(p_box)

        stat_box, sw, sh = textbox(910, y_pos, status_str, size=11, bold=False,
                                   fill="#ffffff", stroke=MUTED, sw=1.2, pad=6)
        frags.append(stat_box)

    render(os.path.join(IMG, 'rolling-update-surge-unavailable.svg'), W, H, *frags,
           title="Анатомія почергового оновлення")


# ── Фігура 3: Blue-Green розгортання ──────────────────────────────────────────
def fig_blue_green_traffic_switch():
    W, H = 960, 480
    frags = []

    cli_box, cw, ch = textbox(120, 240, "Клієнти / Інтернет\n(100% Трафіку)", size=13, bold=True,
                              fill="#f3f4f6", stroke=INK, sw=1.8, pad=12)
    frags.append(cli_box)

    lb_box, lbw, lbh = textbox(360, 240, "Маршрутизатор / L7 Proxy\n(Селектор активного пулу)", size=13, bold=True,
                               fill="#eef4ff", stroke=NEG, sw=2.0, pad=14)
    frags.append(lb_box)

    frags.append(arrow(190, 240, 265, 240, color=INK, sw=2.0))
    frags.append(text(228, 225, "HTTPS", size=11, color=MUTED))

    blue_box, bw, bh = textbox(630, 130, "СИНЄ СЕРЕДОВИЩЕ (Active v1)\nПовний пул серверів / контейнерів\nОбробляє 100% живого трафіку", size=12, bold=True,
                               fill="#eef4ff", stroke=INK, sw=2.0, pad=12)
    frags.append(blue_box)

    green_box, gw, gh = textbox(630, 350, "ЗЕЛЕНЕ СЕРЕДОВИЩЕ (Stage / v2)\nІдентичний пул нової версії v2\nПрогрів кешів і smoke-тести", size=12, bold=True,
                                fill="#f6faf7", stroke=FIELD, sw=2.0, pad=12)
    frags.append(green_box)

    frags.append(arrow(455, 210, 520, 150, color=INK, sw=2.2))
    frags.append(text(465, 165, "Поточний трафік (100%)", size=11, color=INK, bold=True))

    frags.append(arrow(455, 270, 520, 330, color=FIELD, sw=2.2))
    frags.append(text(465, 315, "Миттєве перемикання", size=11, color=FIELD, bold=True))

    db_box, dbw, dbh = textbox(870, 240, "Спільна База Даних\n(Сумісна схема: Expand & Contract)\nТранзакційний стан", size=11, bold=True,
                               fill="#ffffff", stroke=MUTED, sw=1.8, pad=10)
    frags.append(db_box)

    frags.append(arrow(740, 140, 800, 210, color=INK, sw=1.6))
    frags.append(arrow(740, 340, 800, 270, color=FIELD, sw=1.6))

    render(os.path.join(IMG, 'blue-green-traffic-switch.svg'), W, H, *frags,
           title="Топологія синьо-зеленого розгортання")


# ── Фігура 4: Кільце автоматизованого аналізу канаркового випуску ─────────────
def fig_canary_analysis_loop():
    W, H = 960, 480
    frags = []

    b1, w1, h1 = textbox(170, 120, "1. Зріз трафіку\n(Canary Weight 5% → 20%)", size=12, bold=True,
                         fill="#fff9e6", stroke="#d97706", sw=1.8, pad=12)
    frags.append(b1)

    b2, w2, h2 = textbox(480, 120, "2. Збір SLI-метрик\n(HTTP 5xx помилки, p99 затримка,\nCPU/пам'ять, бізнес-конверсія)", size=12, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.8, pad=12)
    frags.append(b2)

    b3, w3, h3 = textbox(790, 120, "3. Статистичний арбітраж\n(Порівняння baseline vs canary,\nтест Манна-Вітні, поріг помилок)", size=12, bold=True,
                         fill="#f3f4f6", stroke=INK, sw=1.8, pad=12)
    frags.append(b3)

    frags.append(arrow(265, 120, 365, 120, color=INK, sw=1.8))
    frags.append(arrow(595, 120, 685, 120, color=INK, sw=1.8))

    b_fail, wf, hf = textbox(300, 350, "Рішення: Аварійний відкіт (Rollback)\n• Вага канарки → 0%\n• Активація сповіщення черговому\n• Радіус ураження обмежено 5%", size=12, bold=True,
                             fill="#fee2e2", stroke="#b91c1c", sw=2.0, pad=12)
    frags.append(b_fail)

    b_pass, wp, hp = textbox(660, 350, "Рішення: Крок промоції (Promotion)\n• Збільшення ваги (наприклад, +25%)\n• При досягненні 100% — фіналізація\n• Версія v2 стає новим baseline", size=12, bold=True,
                             fill="#f6faf7", stroke=FIELD, sw=2.0, pad=12)
    frags.append(b_pass)

    frags.append(arrow(740, 165, 390, 305, color="#b91c1c", sw=2.0))
    frags.append(text(510, 230, "Помилки > Порогу (Fail)", size=11, color="#b91c1c", bold=True))

    frags.append(arrow(810, 165, 710, 305, color=FIELD, sw=2.0))
    frags.append(text(780, 240, "Метрики в нормі (Pass)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, 'canary-analysis-loop.svg'), W, H, *frags,
           title="Кільце автоматизованого аналізу канаркового випуску")


if __name__ == '__main__':
    fig_deployment_strategies_comparison()
    fig_rolling_update_surge_unavailable()
    fig_blue_green_traffic_switch()
    fig_canary_analysis_loop()
    print("All figures generated successfully.")
