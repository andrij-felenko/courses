# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми pauza-zmina-i-prodovzhennia-misii-na-khodu."""

import os
import sys

# Підключення svgkit із scripts/ (чотири рівні вгору від теми: sys-dron -> sys -> root -> repo_root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_pause_mechanics():
    """Фігура 1: Геометрія паузи, гальмування та фіксації точки зависання."""
    W, H = 760, 420
    frags = []

    # Фон-підкладка
    frags.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", sw=1, rx=8))

    # Точки сегмента
    w_prev_x, w_prev_y = 70, 310
    w_curr_x, w_curr_y = 690, 110

    # Лінія запланованого маршруту
    frags.append(line(w_prev_x, w_prev_y, w_curr_x, w_curr_y, color="#9ca3af", sw=2, dash="6,6"))

    # Положення при отриманні команди Pause (T_pause)
    p_cmd_x, p_cmd_y = 250, 251
    # Траєкторія гальмування та знесення вітром до точки Hold
    p_hold_x, p_hold_y = 380, 275
    # Проекція точки Hold на лінію маршруту
    p_proj_x, p_proj_y = 425, 195

    # Початковий політ до точки Pause
    frags.append(line(w_prev_x, w_prev_y, p_cmd_x, p_cmd_y, color=NEG, sw=3))

    # Дуга гальмування та дрейфу вітру
    frags.append(
        f'<path d="M {p_cmd_x} {p_cmd_y} Q {p_cmd_x + 50} {p_cmd_y + 15} {p_hold_x} {p_hold_y}" '
        f'fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="5,4"/>'
    )

    # Коло утримання позиції (Loiter/Hold circle)
    r_hold = 40
    frags.append(circle(p_hold_x, p_hold_y, r_hold, fill="#fef2f2", stroke=POS, sw=1.5))
    frags.append(circle(p_hold_x, p_hold_y, 4, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(text(p_hold_x, p_hold_y + 18, "P_hold", size=12, color=POS, bold=True))

    # Ортоганальна проекція на вихідний трек
    frags.append(line(p_hold_x, p_hold_y, p_proj_x, p_proj_y, color="#7c3aed", sw=1.8, dash="4,4"))
    frags.append(circle(p_proj_x, p_proj_y, 4, fill="#7c3aed", stroke="#ffffff", sw=1.5))
    frags.append(text(p_proj_x + 15, p_proj_y - 10, "P_proj", size=11, color="#7c3aed", bold=True))

    # Позначення cross-track відхилення d_xtrack
    tb_xtrack, _, _ = textbox(340, 220, "d_xtrack", size=10, fill="#f5f3ff", stroke="#7c3aed", pad=4)
    frags.append(tb_xtrack)

    # Залишкова дистанція до цілі d_rem
    frags.append(arrow(p_proj_x + 10, p_proj_y - 3, w_curr_x - 15, w_curr_y + 6, color=FIELD, sw=2))
    tb_drem, _, _ = textbox(570, 135, "Залишкова дистанція: d_rem = ||W_k − P_proj||", size=10, fill="#f0fdf4", stroke=FIELD, pad=5)
    frags.append(tb_drem)

    # Стрілка вітру
    frags.append(arrow(260, 365, 330, 365, color="#64748b", sw=2))
    frags.append(text(295, 385, "Вітровий знос (Wind Drift)", size=10, color="#64748b", italic=True))

    # Точки W_k-1 та W_k
    frags.append(circle(w_prev_x, w_prev_y, 6, fill=INK, stroke="#ffffff", sw=2))
    frags.append(text(w_prev_x, w_prev_y + 20, "W_k−1", size=12, color=INK, bold=True))

    frags.append(circle(w_curr_x, w_curr_y, 7, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(text(w_curr_x, w_curr_y - 15, "W_k (Активна ціль)", size=12, color=NEG, bold=True))

    # Позначення події Pause
    frags.append(circle(p_cmd_x, p_cmd_y, 5, fill=POS, stroke="#ffffff", sw=1.5))
    tb_pause, _, _ = textbox(190, 205, "Команда PAUSE\n(T_pause, v = v_0)", size=10, fill="#fff5f5", stroke=POS, pad=5)
    frags.append(tb_pause)

    # Інформаційна плашка вгорі
    tb_info, _, _ = textbox(
        W / 2, 42,
        "Фіксація навігаційного контексту: індекс k, залишкова дистанція d_rem та перехід у Loiter/Hold",
        size=11, fill="#ffffff", stroke="#cbd5e1", pad=6
    )
    frags.append(tb_info)

    render(os.path.join(OUT, "pause-mechanics-and-hold-geometry.svg"), W, H, *frags)


def fig_atomic_tail_swap():
    """Фігура 2: Архітектура подвійної буферизації та атомарної заміни хвоста місії."""
    W, H = 760, 430
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=8))

    # Заголовок зверху
    tb_header, _, _ = textbox(W / 2, 35, "Архітектура подвійної буферизації (Double Buffering) для заміни хвоста місії", size=12, fill="#f8fafc", stroke="#94a3b8", pad=6, bold=True)
    frags.append(tb_header)

    # Ліва колонка: Контур зв'язку / фоновий потік (Staging Buffer)
    col_w = 295
    left_x = 25
    right_x = 440

    frags.append(rect(left_x, 65, col_w, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(left_x + col_w / 2, 88, "Потік зв'язку (MAVLink Ingestion)", size=12, color=INK, bold=True))

    tb_stage_box, _, _ = textbox(left_x + col_w / 2, 130, "Буфер очікування (Staging Buffer B)\n(Запис нових точок W_k ... W_M')", size=11, fill="#fefce8", stroke="#ca8a04", pad=6)
    frags.append(tb_stage_box)

    # Елементи Staging
    items_stage = ["W_0..W_k-1 (Виконані/Спільні)", "W_k' (Нова активна точка)", "W_k+1' (Новий обхід перешкоди)", "W_k+2' (Точка злиття з планом)"]
    for idx, it in enumerate(items_stage):
        sy = 185 + idx * 36
        frags.append(rect(left_x + 20, sy - 14, col_w - 40, 28, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
        color = FIELD if idx > 0 else MUTED
        frags.append(text(left_x + col_w / 2, sy + 4, it, size=10, color=color, bold=(idx > 0)))

    tb_val, _, _ = textbox(left_x + col_w / 2, 365, "Валідація: CRC, межі геозони,\nвисота рельєфу, зв'язність", size=10, fill="#eff6ff", stroke=NEG, pad=5)
    frags.append(tb_val)

    # Центральна зона перемикання (Commit / Pointer Swap)
    cx = W / 2
    tb_swap, _, _ = textbox(cx, 215, "SeqLock /\nAtomic Swap", size=10, fill="#fdf4ff", stroke="#c084fc", pad=6, bold=True, color="#7e22ce")
    frags.append(tb_swap)

    frags.append(arrow(left_x + col_w + 5, 215, cx - 48, 215, color="#7e22ce", sw=1.8))
    frags.append(arrow(cx + 48, 215, right_x - 5, 215, color="#7e22ce", sw=1.8))

    # Права колонка: Контур навігації високої частоти (Active Buffer)
    frags.append(rect(right_x, 65, col_w, 345, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(right_x + col_w / 2, 88, "Навігаційний контур (50-100 Hz)", size=12, color=INK, bold=True))

    tb_act_box, _, _ = textbox(right_x + col_w / 2, 130, "Активний буфер (Active Buffer A)\n(Виконується автопілотом прямо зараз)", size=11, fill="#ffffff", stroke=FIELD, pad=6)
    frags.append(tb_act_box)

    items_active = ["W_0..W_k-1 (Пройдені сегменти)", "W_k (Поточний вектор наведення)", "W_k+1 (Старий запланований шлях)", "W_k+2 (Старий сегмент)"]
    for idx, it in enumerate(items_active):
        sy = 185 + idx * 36
        frags.append(rect(right_x + 20, sy - 14, col_w - 40, 28, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
        color = NEG if idx == 1 else (MUTED if idx == 0 else POS)
        frags.append(text(right_x + col_w / 2, sy + 4, it, size=10, color=color, bold=(idx == 1)))

    tb_exec, _, _ = textbox(right_x + col_w / 2, 365, "Атомарне читання без блокування:\nнульова затримка в контурі стабілізації", size=10, fill="#ffffff", stroke=FIELD, pad=5)
    frags.append(tb_exec)

    render(os.path.join(OUT, "atomic-tail-swap-double-buffering.svg"), W, H, *frags)


def fig_smooth_rejoin():
    """Фігура 3: Кінематика та траєкторія плавного відновлення польоту (Resume Mission)."""
    W, H = 760, 420
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", sw=1, rx=8))

    # Вихідний сегмент
    w_prev_x, w_prev_y = 60, 330
    w_curr_x, w_curr_y = 700, 90

    frags.append(line(w_prev_x, w_prev_y, w_curr_x, w_curr_y, color="#9ca3af", sw=2, dash="5,5"))

    # Положення дрона у точці Loiter (зі зміщенням)
    p_loit_x, p_loit_y = 170, 350
    # Проекція точки Loiter
    p_proj_x, p_proj_y = 195, 278

    frags.append(circle(p_loit_x, p_loit_y, 6, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(p_loit_x - 5, p_loit_y + 22, "P_loiter (Hold)", size=11, color=POS, bold=True))

    frags.append(line(p_loit_x, p_loit_y, p_proj_x, p_proj_y, color="#7c3aed", sw=1.5, dash="3,3"))
    frags.append(circle(p_proj_x, p_proj_y, 4, fill="#7c3aed", stroke="#ffffff", sw=1.5))
    frags.append(text(p_proj_x + 10, p_proj_y + 16, "P_proj", size=10, color="#7c3aed"))

    # Точка сходження (Intercept Point)
    p_int_x, p_int_y = 440, 187
    frags.append(circle(p_int_x, p_int_y, 5, fill=FIELD, stroke="#ffffff", sw=2))
    frags.append(text(p_int_x + 10, p_int_y - 12, "Точка сходження (P_int)", size=11, color=FIELD, bold=True))

    # Відрізок L_lookahead
    frags.append(line(p_proj_x, p_proj_y, p_int_x, p_int_y, color=FIELD, sw=2))
    tb_lla, _, _ = textbox(315, 220, "L_lookahead", size=10, fill="#f0fdf4", stroke=FIELD, pad=4)
    frags.append(tb_lla)

    # 1. Погана траєкторія: прямий різкий ривок на W_k (Direct-to-WP)
    frags.append(line(p_loit_x, p_loit_y, w_curr_x, w_curr_y, color="#fca5a5", sw=1.8, dash="4,4"))
    tb_bad, _, _ = textbox(470, 275, "Прямий політ на ціль (Direct-to-WP):\nзрізання кута, вихід за межі коридору", size=10, fill="#fff5f5", stroke=POS, pad=5)
    frags.append(tb_bad)

    # 2. Правильна траєкторія: плавний S-подібний вхід у коридор
    rejoin_path = (
        f'<path d="M {p_loit_x} {p_loit_y} C {p_loit_x + 80} {p_loit_y - 30} '
        f'{p_int_x - 90} {p_int_y + 60} {p_int_x} {p_int_y} L {w_curr_x} {w_curr_y}" '
        f'fill="none" stroke="{FIELD}" stroke-width="3"/>'
    )
    frags.append(rejoin_path)

    # Кут перехоплення chi_int
    frags.append(line(p_loit_x, p_loit_y, p_loit_x + 70, p_loit_y - 45, color="#2563eb", sw=1.5, dash="3,3"))
    tb_ang, _, _ = textbox(250, 315, "Кут перехоплення:\nchi_int <= chi_max", size=10, fill="#eff6ff", stroke=NEG, pad=4)
    frags.append(tb_ang)

    # Точки W_prev та W_curr
    frags.append(circle(w_prev_x, w_prev_y, 6, fill=INK, stroke="#ffffff", sw=2))
    frags.append(text(w_prev_x, w_prev_y + 18, "W_k−1", size=12, color=INK, bold=True))

    frags.append(circle(w_curr_x, w_curr_y, 7, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(text(w_curr_x, w_curr_y - 15, "W_k (Ціль)", size=12, color=NEG, bold=True))

    # Інформаційна плашка зверху
    tb_top, _, _ = textbox(
        W / 2, 40,
        "Відновлення місії: S-подібне сходження з обмеженням ривка та бічного прискорення a_lat = v² / R <= a_max",
        size=11, fill="#ffffff", stroke="#cbd5e1", pad=6
    )
    frags.append(tb_top)

    render(os.path.join(OUT, "smooth-rejoin-trajectory-profile.svg"), W, H, *frags)


def fig_active_wp_race():
    """Фігура 4: Гонка станів при оновленні активної точки та алгоритм арбітражу."""
    W, H = 760, 420
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=8))

    # Заголовок
    tb_head, _, _ = textbox(W / 2, 35, "Арбітраж оновлення активної точки: запобігання гонці станів (Race Condition)", size=12, fill="#f8fafc", stroke="#94a3b8", pad=6, bold=True)
    frags.append(tb_head)

    # Таймлайн зверху вниз
    # Дві паралельні лінії часу: Зв'язок (MAVLink) та Навігаційний контур
    t1_x = 180
    t2_x = 580

    frags.append(text(t1_x, 70, "Потік MAVLink / GCS", size=12, color=INK, bold=True))
    frags.append(text(t2_x, 70, "Навігаційний автомат (Nav FSM)", size=12, color=INK, bold=True))

    frags.append(line(t1_x, 85, t1_x, 390, color="#94a3b8", sw=2))
    frags.append(line(t2_x, 85, t2_x, 390, color="#94a3b8", sw=2))

    # Крок 1: Дрон наближається до W_k
    frags.append(circle(t2_x, 115, 5, fill=NEG, stroke="#ffffff", sw=1.5))
    tb_e1, _, _ = textbox(t2_x + 95, 115, "d <= R_acc (Вхід у кулю цілі)", size=10, fill="#eff6ff", stroke=NEG, pad=4)
    frags.append(tb_e1)

    # Крок 2: Приходить пакет оновлення точок хвоста (і самої W_k)
    frags.append(circle(t1_x, 145, 5, fill=POS, stroke="#ffffff", sw=1.5))
    tb_e2, _, _ = textbox(t1_x - 90, 145, "MAVLink: заміна W_k\nна нові координати", size=10, fill="#fff5f5", stroke=POS, pad=4)
    frags.append(tb_e2)

    # Стрілка конфлікту (конкурентний доступ)
    frags.append(arrow(t1_x, 175, t2_x, 175, color=POS, sw=2))
    tb_conflict, _, _ = textbox(W / 2, 175, "КОНФЛІКТ: спроба оновити\nактивну точку під час прольоту!", size=10, fill="#fef2f2", stroke=POS, pad=5, bold=True)
    frags.append(tb_conflict)

    # Крок 3: Nav FSM перемикає seq++
    frags.append(circle(t2_x, 235, 5, fill=NEG, stroke="#ffffff", sw=1.5))
    tb_e3, _, _ = textbox(t2_x + 90, 235, "Інкремент: seq = k + 1\n(Перехід до наступної)", size=10, fill="#eff6ff", stroke=NEG, pad=4)
    frags.append(tb_e3)

    # Крок 4: Захисний механізм (Active Waypoint Guard)
    frags.append(rect(W / 2 - 170, 275, 340, 115, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(W / 2, 298, "Захисний протокол (Active Waypoint Guard)", size=11, color=FIELD, bold=True))

    guard_rules = [
        "1. Якщо d <= R_acc: блокування заміни W_k до завершення дії",
        "2. Якщо заміна критична: автоперехід у LOITER_IN_PLACE",
        "3. Валідація: якщо нова точка позаду вектора — скидання інтеграторів",
        "4. Атомарний комміт нового списку зі збереженням фази польоту",
    ]
    for i, rule in enumerate(guard_rules):
        frags.append(text(W / 2, 322 + i * 18, rule, size=9.5, color=INK))

    render(os.path.join(OUT, "active-waypoint-race-and-resolution.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_pause_mechanics()
    fig_atomic_tail_swap()
    fig_smooth_rejoin()
    fig_active_wp_race()
    print("Всі 4 фігури успішно згенеровано у", OUT)
