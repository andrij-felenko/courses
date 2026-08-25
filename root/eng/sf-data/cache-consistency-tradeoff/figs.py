# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'Свіжість проти навантаження' (cache-consistency-tradeoff)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_tradeoff_frontier():
    """Крива компромісу: Вікно застарілості даних (Δt) проти навантаження на БД."""
    W, H = 880, 520
    parts = []

    # Заголовок
    parts.append(text(W / 2, 28, "Компроміс між свіжістю даних та навантаженням на джерело правди", size=16, bold=True))

    # Вісь X та Y
    ox, oy = 90, 450
    axis_w, axis_h = 740, 380
    parts.append(arrow(ox, oy, ox + axis_w, oy, color=LINE, sw=2))
    parts.append(arrow(ox, oy, ox, oy - axis_h, color=LINE, sw=2))

    parts.append(text(ox + axis_w - 20, oy + 26, "Вікно застарілості даних (Δt / толерантність до stale reads) →", size=12, bold=True, color=INK, anchor="end"))
    parts.append(text(ox + 15, oy - axis_h + 15, "Навантаження на БД / Латентність мутацій ↑", size=12, bold=True, color=INK, anchor="start"))

    # Крива компромісу (гіперболічний профіль)
    curve_pts = [
        (ox + 40, oy - 330),
        (ox + 70, oy - 240),
        (ox + 130, oy - 160),
        (ox + 230, oy - 95),
        (ox + 380, oy - 55),
        (ox + 540, oy - 30),
        (ox + 680, oy - 15)
    ]
    path_d = f"M {curve_pts[0][0]} {curve_pts[0][1]} Q {ox + 120} {oy - 95}, {curve_pts[-1][0]} {curve_pts[-1][1]}"
    parts.append(f'<path d="{path_d}" fill="none" stroke="{NEG}" stroke-width="3.5"/>')

    # Точки стратегій на кривій
    # Точка 1: Синхронний 2PC / Write-Through
    p1_x, p1_y = ox + 50, oy - 290
    parts.append(circle(p1_x, p1_y, 6, fill=POS, stroke="#ffffff", sw=2))
    b1, bw1, bh1 = textbox(p1_x + 160, p1_y - 20, "Сувора узгодженість (2PC / Synchronous)\nΔt = 0 · Максимальне навантаження БД\nВисока латентність запису, блокування", size=11, pad=6, fill="#fdecea", stroke=POS)
    parts.append(b1)
    parts.append(line(p1_x + 6, p1_y - 3, p1_x + 160 - bw1 / 2, p1_y - 15, color=POS, sw=1.5))

    # Точка 2: Інвалідація через CDC / Pub-Sub
    p2_x, p2_y = ox + 155, oy - 140
    parts.append(circle(p2_x, p2_y, 6, fill="#d97706", stroke="#ffffff", sw=2))
    b2, bw2, bh2 = textbox(p2_x + 120, p2_y - 75, "Event-driven інвалідація (CDC / Pub-Sub)\nΔt ≈ 10-100 мс · Середнє навантаження\nРизик гонок оновлення та stampede", size=11, pad=6, fill="#fef3c7", stroke="#d97706")
    parts.append(b2)
    parts.append(line(p2_x + 4, p2_y - 6, p2_x + 120 - bw2 / 2, p2_y - 55, color="#d97706", sw=1.5))

    # Точка 3: Оптимальний фронтир (XFetch / SWR + Singleflight)
    p3_x, p3_y = ox + 360, oy - 60
    parts.append(circle(p3_x, p3_y, 7, fill=FIELD, stroke="#ffffff", sw=2))
    b3, bw3, bh3 = textbox(p3_x + 110, p3_y - 80, "Оптимальний фронтир (XFetch / SWR)\nКерована застарілість (Δt = секунди)\nНуль лавин (0 stampede), захист БД", size=11, pad=6, fill="#e8f8f0", stroke=FIELD, bold=True)
    parts.append(b3)
    parts.append(line(p3_x + 4, p3_y - 6, p3_x + 110 - bw3 / 2, p3_y - 60, color=FIELD, sw=1.5))

    # Точка 4: Пасивний довгий TTL
    p4_x, p4_y = ox + 610, oy - 22
    parts.append(circle(p4_x, p4_y, 6, fill=NEG, stroke="#ffffff", sw=2))
    b4, bw4, bh4 = textbox(p4_x + 10, p4_y - 70, "Довгий пасивний TTL\nΔt = хвилини або години\nМінімальний тиск на БД, застарілий кеш", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    parts.append(b4)
    parts.append(line(p4_x - 4, p4_y - 6, p4_x + 10 - bw4 / 2, p4_y - 50, color=NEG, sw=1.5))

    render(os.path.join(OUT, "tradeoff-frontier.svg"), W, H, *parts)


def fig_stampede_vs_xfetch():
    """Порівняння чотирьох реакцій на закінчення TTL при 10 000 зап/с."""
    W, H = 920, 530
    parts = []

    parts.append(text(W / 2, 26, "Чотири реакції системи на вичерпання TTL під високим навантаженням", size=16, bold=True))

    row_h = 104
    y_start = 50

    tracks = [
        ("1. Наївний пасивний TTL", "#fdecea", POS, "Лавина запитів у БД (Cache Stampede)"),
        ("2. Захист замком (Singleflight)", "#fef3c7", "#d97706", "1 запит у БД; решта чекає на замку"),
        ("3. Stale-While-Revalidate (SWR)", "#eaf0fd", NEG, "Миттєвий stale-кеш; фонове оновлення"),
        ("4. Раннє оновлення (XFetch)", "#e8f8f0", FIELD, "Оновлення ДО кінця TTL; 0 затримок")
    ]

    for idx, (title, bg_col, stroke_col, desc) in enumerate(tracks):
        ry = y_start + idx * (row_h + 10)
        parts.append(rect(20, ry, W - 40, row_h, fill=bg_col, stroke=stroke_col, sw=1.5, rx=6))
        parts.append(text(35, ry + 22, title, size=13, bold=True, color=stroke_col, anchor="start"))
        parts.append(text(35, ry + 40, desc, size=11, color=MUTED, anchor="start"))

        # Шкала часу в правій частині
        tx0 = 360
        tx_end = W - 40
        parts.append(line(tx0, ry + 78, tx_end, ry + 78, color=LINE, sw=1.5))
        parts.append(text(tx_end + 5, ry + 82, "t", size=11, italic=True, anchor="start"))

        # Позначка закінчення TTL
        t_exp = tx0 + 200
        parts.append(line(t_exp, ry + 15, t_exp, ry + 95, color="#9ca3af", sw=1.5, dash="3,3"))
        parts.append(text(t_exp, ry + 12, "TTL закінчився", size=10, color=MUTED, anchor="middle"))

        if idx == 0:
            # Наївний TTL: шквал червоних стрілок після t_exp
            for offset in [10, 25, 40, 55, 70, 85, 100, 115]:
                parts.append(arrow(t_exp + offset, ry + 78, t_exp + offset, ry + 98, color=POS, sw=1.5))
            b, _, _ = textbox(t_exp + 70, ry + 42, "500+ одночасних запитів у БД!\nПеревантаження connection pool", size=10, pad=4, fill="#ffffff", stroke=POS)
            parts.append(b)

        elif idx == 1:
            # Singleflight: 1 зелена стрілка в БД, решта чекає
            parts.append(arrow(t_exp + 10, ry + 78, t_exp + 10, ry + 98, color=FIELD, sw=2))
            parts.append(text(t_exp + 10, ry + 99, "1 в БД", size=9, bold=True, color=FIELD, anchor="middle"))
            # Горизонтальна лінія очікування
            parts.append(line(t_exp + 20, ry + 64, t_exp + 120, ry + 64, color="#d97706", sw=2, dash="2,2"))
            b, _, _ = textbox(t_exp + 75, ry + 40, "499 клієнтів чекають (Latency ↑)", size=10, pad=4, fill="#ffffff", stroke="#d97706")
            parts.append(b)

        elif idx == 2:
            # SWR: миттєве повернення stale, фонове оновлення
            parts.append(arrow(t_exp + 10, ry + 78, t_exp + 10, ry + 98, color=NEG, sw=2))
            parts.append(text(t_exp + 10, ry + 99, "Фон", size=9, color=NEG, anchor="middle"))
            b, _, _ = textbox(t_exp + 80, ry + 42, "Читачі отримують stale-копію (0 ms)\nКеш оновлюється у фоні", size=10, pad=4, fill="#ffffff", stroke=NEG)
            parts.append(b)

        elif idx == 3:
            # XFetch: оновлення стається ДО t_exp
            t_early = t_exp - 80
            parts.append(arrow(t_early, ry + 78, t_early, ry + 98, color=FIELD, sw=2))
            parts.append(text(t_early, ry + 99, "Ранній fetch", size=9, bold=True, color=FIELD, anchor="middle"))
            b, _, _ = textbox(t_early - 70, ry + 42, "XFetch спрацював заздалегідь\nКеш свіжий ДО вичерпання TTL!", size=10, pad=4, fill="#ffffff", stroke=FIELD, bold=True)
            parts.append(b)

    render(os.path.join(OUT, "stampede-vs-xfetch.svg"), W, H, *parts)

    render(os.path.join(OUT, "stampede-vs-xfetch.svg"), W, H, *parts)


def fig_lease_token_race():
    """Діаграма послідовності: гонка інвалідації кешу та захист через Lease Token."""
    W, H = 840, 460
    parts = []

    parts.append(text(W / 2, 24, "Гонка інвалідації кешу та захист від отруєння через Lease Token", size=16, bold=True))

    # Стовпці / Учасники
    cols = [
        ("Клієнт 1 (Читач)", 110),
        ("Клієнт 2 (Письменник)", 330),
        ("Кеш (Redis / Memcache)", 550),
        ("База даних (Source of Truth)", 740)
    ]

    for name, cx in cols:
        b, bw, bh = textbox(cx, 60, name, size=12, pad=6, fill="#f4f6f8", stroke=LINE, bold=True)
        parts.append(b)
        parts.append(line(cx, 60 + bh / 2, cx, 430, color="#9ca3af", sw=1.5, dash="4,4"))

    # Послідовність подій
    # 1. Клієнт 1 читає з кешу -> MISS + Lease Token
    y1 = 110
    parts.append(arrow(110, y1, 550, y1, color=LINE, sw=1.5))
    parts.append(text(330, y1 - 8, "1. Get(key) → Cache MISS", size=11, anchor="middle"))

    y2 = 135
    parts.append(arrow(550, y2, 110, y2, color=FIELD, sw=1.5))
    parts.append(text(330, y2 - 8, "2. Відповідь: NULL + Lease Token (0x8F4A)", size=11, color=FIELD, bold=True, anchor="middle"))

    # 2. Клієнт 1 іде в БД (повільний запит)
    y3 = 170
    parts.append(arrow(110, y3, 740, y3, color=LINE, sw=1.5))
    parts.append(text(425, y3 - 8, "3. Query DB (значення V1 = 100) — повільне читання...", size=11, anchor="middle"))

    # 3. Клієнт 2 оновлює БД і інвалідує кеш
    y4 = 215
    parts.append(arrow(330, y4, 740, y4, color=POS, sw=1.8))
    parts.append(text(535, y4 - 8, "4. Update DB (V2 = 80)", size=11, color=POS, bold=True, anchor="middle"))

    y5 = 245
    parts.append(arrow(330, y5, 550, y5, color=POS, sw=1.8))
    parts.append(text(440, y5 - 8, "5. Invalidate(key) → скасування лізи 0x8F4A!", size=11, color=POS, bold=True, anchor="middle"))

    # 4. Кеш інвалідує ключ і скасовує токен 0x8F4A
    b_inv, _, _ = textbox(550, 280, "Ключ вилучено\nТокен 0x8F4A анульовано", size=10, pad=4, fill="#fdecea", stroke=POS)
    parts.append(b_inv)

    # 5. Повільний Клієнт 1 повертається і намагається записати застаріле V1
    y6 = 330
    parts.append(arrow(110, y6, 550, y6, color=LINE, sw=1.5))
    parts.append(text(330, y6 - 8, "6. Set(key, V1=100, Lease=0x8F4A)", size=11, anchor="middle"))

    # 6. Кеш відхиляє запис!
    y7 = 370
    parts.append(arrow(550, y7, 110, y7, color=POS, sw=2))
    parts.append(text(330, y7 - 8, "7. REJECTED: токен 0x8F4A недійсний! Кеш захищено.", size=11, color=POS, bold=True, anchor="middle"))

    b_res, _, _ = textbox(425, 415, "Без токена лізи старе значення V1=100 перезаписало б кеш назавжди!\nЗавдяки Lease Token застарілий запис відкинуто.", size=11, pad=6, fill="#e8f8f0", stroke=FIELD, bold=True)
    parts.append(b_res)

    render(os.path.join(OUT, "lease-token-race.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_tradeoff_frontier()
    fig_stampede_vs_xfetch()
    fig_lease_token_race()
    print("Всі 3 фігури згенеровано успішно!")
