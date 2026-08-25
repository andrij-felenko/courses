# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми book/programming/operations/parallel-run.
Використовує svgkit: render, textbox, fitbox, line, arrow, text, circle, rect.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_dual_run_architecture():
    """Архітектура паралельного прогону (Parallel Run)."""
    w, h = 940, 520
    frags = []

    # Вхідний потік
    b_in, bw_in, _ = textbox(110, 160, "Бойовий трафік\n(HTTP / gRPC / Події)", size=13, pad=10, fill=FILL, stroke=LINE, bold=True)
    frags.append(b_in)

    # Маршрутизатор / Шлюз
    b_gw, bw_gw, _ = textbox(290, 160, "Шлюз / Ingress Router\n(Dual Dispatcher)", size=13, pad=10, fill="#e8f0fe", stroke=NEG, bold=True)
    frags.append(b_gw)

    frags.append(arrow(110 + bw_in / 2, 160, 290 - bw_gw / 2, 160, color=LINE))

    # Стара система (Master) - зверху
    y_leg = 90
    b_leg, bw_leg, _ = textbox(520, y_leg, "Legacy-система (Master)\nАвторитетне виконання", size=13, pad=10, fill="#fcedec", stroke=POS, bold=True)
    frags.append(b_leg)

    # Нова система (Candidate) - знизу
    y_can = 230
    b_can, bw_can, _ = textbox(520, y_can, "Candidate-система (Shadow)\nТіньове виконання", size=13, pad=10, fill="#eafaf1", stroke=FIELD, bold=True)
    frags.append(b_can)

    # З'єднання від шлюзу до Legacy та Candidate
    frags.append(arrow(290 + bw_gw / 2, 145, 520 - bw_leg / 2, y_leg, color=POS, sw=2.0))
    frags.append(text(380, 95, "Основний потік", size=11, color=POS, bold=True))

    frags.append(arrow(290 + bw_gw / 2, 175, 520 - bw_can / 2, y_can, color=FIELD, sw=2.0))
    frags.append(text(380, 240, "Тіньовий клон (async)", size=11, color=FIELD, bold=True))

    # Сховища та ефекти старої системи
    b_leg_db, bw_leg_db, _ = textbox(780, 65, "Бойова БД (Master)\n(Живий стан)", size=12, pad=8, fill=FILL, stroke=LINE)
    frags.append(b_leg_db)
    frags.append(arrow(520 + bw_leg / 2, 80, 780 - bw_leg_db / 2, 65, color=LINE))

    b_leg_eff, bw_leg_eff, _ = textbox(780, 125, "Зовнішні API / Ефекти\n(Stripe, SMS, Пошта)", size=12, pad=8, fill="#fcedec", stroke=POS)
    frags.append(b_leg_eff)
    frags.append(arrow(520 + bw_leg / 2, 100, 780 - bw_leg_eff / 2, 125, color=POS))

    # Сховища та ефекти нової системи
    b_can_db, bw_can_db, _ = textbox(780, 205, "Shadow БД\n(Ізольований стан)", size=12, pad=8, fill=FILL, stroke=LINE)
    frags.append(b_can_db)
    frags.append(arrow(520 + bw_can / 2, 220, 780 - bw_can_db / 2, 205, color=LINE))

    b_can_eff, bw_can_eff, _ = textbox(780, 265, "Virtual Effect Sink\n(Запис намірів дії)", size=12, pad=8, fill="#eafaf1", stroke=FIELD)
    frags.append(b_can_eff)
    frags.append(arrow(520 + bw_can / 2, 240, 780 - bw_can_eff / 2, 265, color=FIELD))

    # Розділювальна лінія до конвеєра звірки
    frags.append(line(40, 315, w - 40, 315, color=MUTED, sw=1.0, dash="4,4"))
    frags.append(text(200, 332, "АСИНХРОННИЙ КОНВЕЄР ЗВІРКИ (RECONCILIATION)", size=12, color=MUTED, bold=True))

    # Шина подій звірки
    b_bus, bw_bus, _ = textbox(210, 415, "Журнал аудиту / Канал подій\n(Kafka / Stream Buffer)", size=12, pad=10, fill=FILL, stroke=LINE)
    frags.append(b_bus)

    # Пунктирні стрілки збору до шини
    frags.append(arrow(520, y_leg + 25, 270, 385, color=MUTED, sw=1.2))
    frags.append(arrow(520, y_can + 25, 270, 415, color=MUTED, sw=1.2))

    # Звіряч (Reconciliation Engine)
    b_rec, bw_rec, _ = textbox(520, 415, "Звіряч (Reconciliation Engine)\n- Зіставлення за Correlation ID\n- Канонізація та нормалізація\n- Поглиблений Diff стану й виходу", size=12, pad=10, fill="#fef9e7", stroke="#d4ac0d", bold=True)
    frags.append(b_rec)

    frags.append(arrow(210 + bw_bus / 2, 415, 520 - bw_rec / 2, 415, color=LINE, sw=1.8))

    # Результати звірки (Метрики та Алерти)
    b_res, bw_res, _ = textbox(780, 415, "Дашборд і Алерти\n- Mismatch Rate (SLI)\n- Журнал невідповідностей\n- Drift Analysis Report", size=12, pad=10, fill="#e8f0fe", stroke=NEG)
    frags.append(b_res)

    frags.append(arrow(520 + bw_rec / 2, 415, 780 - bw_res / 2, 415, color=NEG, sw=1.8))

    render(os.path.join(OUT_DIR, "dual-run-architecture.svg"), w, h, *frags, title="Архітектура системи подвійного прогону (Parallel Run)")


def fig_cutover_phases():
    """Етапи міграції під час паралельного прогону."""
    w, h = 940, 460
    frags = []

    phases = [
        ("Фаза 0: Shadow Replay", "Тільки читання\nРеплікація історії\nНульовий ризик", "#f4f6f8", LINE),
        ("Фаза 1: Dual Run (Legacy Master)", "Legacy = Master\nCandidate = Shadow\nБезперервна звірка", "#fcedec", POS),
        ("Фаза 2: Inverted Dual Run", "Candidate = Master\nLegacy = Shadow\nМиттєвий відкіт живий", "#eafaf1", FIELD),
        ("Фаза 3: Single Master", "Candidate = Єдиний актив\nLegacy = Холодний архів\nЗвірку зупинено", "#e8f0fe", NEG),
        ("Фаза 4: Decommission", "Демонтаж швів\nВидалення Legacy\nЧиста архітектура", "#f4f6f8", LINE),
    ]

    col_w = 160
    spacing = 22
    start_x = 45

    for i, (title_p, desc_p, fill_c, stroke_c) in enumerate(phases):
        cx = start_x + i * (col_w + spacing) + col_w / 2
        cy = 130
        b_box, bw, bh = textbox(cx, cy, f"{title_p}\n\n{desc_p}", size=12, pad=10, fill=fill_c, stroke=stroke_c, min_w=col_w, bold=False)
        frags.append(b_box)

        # Стрілка між фазами
        if i < len(phases) - 1:
            arrow_x1 = cx + col_w / 2
            arrow_x2 = arrow_x1 + spacing
            frags.append(arrow(arrow_x1, cy, arrow_x2, cy, color=MUTED, sw=2.0))

    # Смуга профілю ризику та авторитетності
    frags.append(line(start_x, 230, w - start_x, 230, color=LINE, sw=1.2))

    # Таблиця атрибутів фаз
    row_y = [270, 330, 390]
    headers = [
        "Авторитетне джерело правди:",
        "Зовнішні побічні ефекти:",
        "Вартість відкату (Rollback):"
    ]

    for y, h_text in zip(row_y, headers):
        frags.append(text(start_x + 10, y, h_text, size=12, anchor="start", bold=True, color=INK))

    values = [
        # Авторитетне джерело
        ["Legacy DB", "Legacy DB (Master)", "Candidate DB (Master)", "Candidate DB", "Candidate DB"],
        # Побічні ефекти
        ["Лише Legacy", "Legacy справжні / Нові у Sink", "Candidate справжні / Старі у Sink", "Лише Candidate", "Лише Candidate"],
        # Вартість відкату
        ["Нульова (секунди)", "Нульова (поворот прапорця)", "Низька (зворотна реплікація)", "Середня (відновлення з бекапу)", "Неможливий (код видалено)"]
    ]

    for r_idx, (y, val_row) in enumerate(zip(row_y, values)):
        for c_idx, val in enumerate(val_row):
            cx = start_x + c_idx * (col_w + spacing) + col_w / 2
            c_color = INK
            if r_idx == 2:
                if c_idx <= 1:
                    c_color = FIELD
                elif c_idx == 2:
                    c_color = "#d4ac0d"
                else:
                    c_color = POS
            frags.append(text(cx, y + 20, val, size=11, anchor="middle", color=c_color, bold=(r_idx == 2)))

    render(os.path.join(OUT_DIR, "cutover-phases.svg"), w, h, *frags, title="П'ять етапів міграції критичної системи через Parallel Run")


def fig_reconciliation_window():
    """Схема ковзного вікна узгодження (Sliding Reconciliation Window)."""
    w, h = 920, 430
    frags = []

    # Часова вісь Legacy
    frags.append(text(130, 75, "Потік Legacy (T1):", size=13, anchor="end", bold=True, color=POS))
    frags.append(arrow(150, 70, 850, 70, color=POS, sw=2.0))
    frags.append(text(860, 75, "Час (t)", size=11, anchor="start", color=MUTED))

    # Подія Legacy
    frags.append(circle(290, 70, 10, fill=POS, stroke=LINE))
    frags.append(text(290, 50, "Подія A (Legacy)", size=11, bold=True))
    frags.append(text(290, 95, "t = 10.02s | ID: ord_981", size=10, color=MUTED))

    # Часова вісь Candidate
    frags.append(text(130, 175, "Потік Candidate (T2):", size=13, anchor="end", bold=True, color=FIELD))
    frags.append(arrow(150, 170, 850, 170, color=FIELD, sw=2.0))
    frags.append(text(860, 175, "Час (t)", size=11, anchor="start", color=MUTED))

    # Подія Candidate (із затримкою)
    frags.append(circle(460, 170, 10, fill=FIELD, stroke=LINE))
    frags.append(text(460, 150, "Подія A (Candidate)", size=11, bold=True))
    frags.append(text(460, 195, "t = 10.38s | ID: ord_981", size=10, color=MUTED))

    # Часовий зсув (Skew)
    frags.append(line(290, 70, 290, 230, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(line(460, 170, 460, 230, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(arrow(290, 220, 460, 220, color=MUTED, sw=1.2))
    frags.append(arrow(460, 220, 290, 220, color=MUTED, sw=1.2))
    frags.append(text(375, 212, "Часовий зсув (Skew Δt = 360ms)", size=11, color=INK, bold=True))

    # Ковзне вікно буфера
    frags.append(rect(230, 245, 460, 50, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=6))
    frags.append(text(460, 275, "Ковзне вікно очікування кореляції (Window W = 2.0s)", size=12, bold=True, color=INK))

    # Блок звірки
    b_diff, bw_diff, _ = textbox(460, 365, "Нормалізатор і Deep Diff\n1. Вилучення UUID / міток часу\n2. Сортування списків / JSON\n3. Перевірка бізнес-полів і балансу", size=12, pad=10, fill=FILL, stroke=LINE, bold=False)
    frags.append(b_diff)

    frags.append(arrow(460, 295, 460, 365 - 35, color=LINE, sw=1.5))

    # Вихід звірки
    b_ok, bw_ok, _ = textbox(770, 345, "Статус: Match (Збіг)\nSLI: OK", size=11, pad=8, fill="#eafaf1", stroke=FIELD, bold=True)
    frags.append(b_ok)
    frags.append(arrow(460 + bw_diff / 2, 355, 770 - bw_ok / 2, 345, color=FIELD, sw=1.5))

    b_err, bw_err, _ = textbox(770, 390, "Статус: Drift Mismatch\nЛог розбіжності + Алерт", size=11, pad=8, fill="#fcedec", stroke=POS, bold=True)
    frags.append(b_err)
    frags.append(arrow(460 + bw_diff / 2, 375, 770 - bw_err / 2, 390, color=POS, sw=1.5))

    render(os.path.join(OUT_DIR, "reconciliation-window.svg"), w, h, *frags, title="Ковзне вікно зіставлення та звірки асинхронних результатів")


if __name__ == "__main__":
    fig_dual_run_architecture()
    fig_cutover_phases()
    fig_reconciliation_window()
    print("Згенеровано 3 фігури в img/")
