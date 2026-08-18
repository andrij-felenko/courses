# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Протокол місій: точки маршруту та транзакції».
Генерує SVG-фігури у теку ./img/ за допомогою спільного модуля scripts/svgkit.py.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Послідовність Stop-and-Wait транзакції завантаження місії ────────
def fig_upload_sequence():
    w, h = 920, 540
    parts = []

    # Дві вертикальні лінії учасників: Станція (GCS) та Автопілот
    x_gcs = 180
    x_ap = 740
    y_top = 70
    y_bot = 490

    # Шапки сутностей
    box_gcs, _, _ = textbox(x_gcs, y_top - 20, "Наземна станція (GCS)\nВідправник / Клієнт",
                            size=13, pad=8, fill="#eef2f7", stroke=NEG, bold=True)
    box_ap, _, _ = textbox(x_ap, y_top - 20, "Автопілот (FCU)\nОтримувач / Сервер",
                           size=13, pad=8, fill="#eef6ef", stroke=FIELD, bold=True)
    parts.extend([box_gcs, box_ap])

    # Лінії життя (жили часу)
    parts.append(line(x_gcs, y_top + 10, x_gcs, y_bot, color="#9ca3af", sw=1.8, dash="4,4"))
    parts.append(line(x_ap, y_top + 10, x_ap, y_bot, color="#9ca3af", sw=1.8, dash="4,4"))

    # Стрілки обміну повідомленнями
    # 1. MISSION_COUNT
    y1 = 120
    parts.append(arrow(x_gcs, y1, x_ap, y1 + 20, color=NEG, sw=2))
    parts.append(text((x_gcs + x_ap) / 2, y1 - 4, "1. MISSION_COUNT (count=3, type=MISSION)",
                      size=12, bold=True, color=NEG))

    # 2. MISSION_REQUEST_INT (seq=0)
    y2 = 175
    parts.append(arrow(x_ap, y2, x_gcs, y2 + 20, color=FIELD, sw=2))
    parts.append(text((x_gcs + x_ap) / 2, y2 - 4, "2. MISSION_REQUEST_INT (seq=0)",
                      size=12, bold=True, color=FIELD))

    # 3. MISSION_ITEM_INT (seq=0)
    y3 = 230
    parts.append(arrow(x_gcs, y3, x_ap, y3 + 20, color=NEG, sw=2))
    parts.append(text((x_gcs + x_ap) / 2, y3 - 4, "3. MISSION_ITEM_INT (seq=0, TAKEOFF)",
                      size=12, bold=True, color=NEG))

    # 4. MISSION_REQUEST_INT (seq=1) - одночасно запит наступного і неявний ACK попереднього
    y4 = 285
    parts.append(arrow(x_ap, y4, x_gcs, y4 + 20, color=FIELD, sw=2))
    parts.append(text((x_gcs + x_ap) / 2, y4 - 4, "4. MISSION_REQUEST_INT (seq=1) [ACK seq 0 + запит seq 1]",
                      size=12, bold=True, color=FIELD))

    # 5. MISSION_ITEM_INT (seq=1) - втрачений пакет або затримка
    y5 = 335
    parts.append(line(x_gcs, y5, (x_gcs + x_ap) / 2 + 30, y5 + 15, color="#e74c3c", sw=2, dash="3,3"))
    parts.append(text((x_gcs + x_ap) / 2 - 20, y5 - 4, "5. MISSION_ITEM_INT (seq=1) [втрачено в ефірі]",
                      size=11, bold=True, color="#c0392b"))
    parts.append(text((x_gcs + x_ap) / 2 + 45, y5 + 18, "✖", size=16, bold=True, color="#c0392b"))

    # Таймаут і повторний запит або повторна посилка
    y6 = 390
    parts.append(arrow(x_ap, y6, x_gcs, y6 + 20, color=FIELD, sw=2))
    parts.append(text((x_gcs + x_ap) / 2, y6 - 4, "6. Повтор: MISSION_REQUEST_INT (seq=1) після таймауту",
                      size=12, bold=True, color=FIELD))

    # 7. MISSION_ITEM_INT (seq=1) успішно
    y7 = 440
    parts.append(arrow(x_gcs, y7, x_ap, y7 + 20, color=NEG, sw=2))
    parts.append(text((x_gcs + x_ap) / 2, y7 - 4, "7. MISSION_ITEM_INT (seq=1, WAYPOINT)",
                      size=12, bold=True, color=NEG))

    # 8. MISSION_ACK
    y8 = 490
    parts.append(arrow(x_ap, y8, x_gcs, y8 + 20, color="#27ae60", sw=2.5))
    parts.append(text((x_gcs + x_ap) / 2, y8 - 4, "8. MISSION_ACK (result=MAV_MISSION_ACCEPTED)",
                      size=13, bold=True, color="#27ae60"))

    render(os.path.join(IMG_DIR, "upload-sequence.svg"), w, h, *parts)


# ── Фігура 2: Кінцевий автомат клієнта завантаження (FSM) ─────────────────────
def fig_fsm_states():
    w, h = 940, 480
    parts = []

    # Вузли стану (States)
    # 1. IDLE (Спокій)
    b_idle, _, _ = textbox(130, 240, "IDLE\n(Очікування задачі)",
                           size=13, pad=12, fill="#f4f6f8", stroke=LINE, sw=2, bold=True)
    # 2. SEND_COUNT
    b_cnt, _, _ = textbox(400, 110, "SEND_COUNT\n(Анонс кількості пунктів)",
                          size=13, pad=12, fill="#eef2f7", stroke=NEG, sw=2, bold=True)
    # 3. WAIT_REQ
    b_req, _, _ = textbox(730, 110, "WAIT_REQUEST\n(Очікування MISSION_REQUEST_INT)",
                          size=13, pad=12, fill="#e9f7ef", stroke=FIELD, sw=2, bold=True)
    # 4. WAIT_ACK
    b_ack, _, _ = textbox(730, 360, "WAIT_ACK\n(Очікування підтвердження)",
                          size=13, pad=12, fill="#fff6e5", stroke="#b7791f", sw=2, bold=True)
    # 5. ERROR / CANCEL
    b_err, _, _ = textbox(400, 360, "CANCELLED / ERROR\n(Скасування транзакції)",
                          size=13, pad=12, fill="#fdecea", stroke=POS, sw=2, bold=True)

    parts.extend([b_idle, b_cnt, b_req, b_ack, b_err])

    # Переходи (Transitions)
    # IDLE -> SEND_COUNT
    parts.append(arrow(190, 210, 300, 140, color=LINE, sw=1.8))
    parts.append(text(210, 155, "Старт завантаження\nшлемо MISSION_COUNT", size=11, color=INK, anchor="start"))

    # SEND_COUNT -> WAIT_REQUEST
    parts.append(arrow(500, 110, 600, 110, color=LINE, sw=1.8))
    parts.append(text(550, 95, "Очікуємо seq=0", size=11, color=INK))

    # WAIT_REQUEST (петля надсилання пунктів)
    # Якщо seq < count - 1 -> шлемо MISSION_ITEM_INT і лишаємося чекати seq+1
    parts.append(arrow(780, 70, 680, 70, color=FIELD, sw=1.8))
    parts.append(text(730, 50, "Отримано REQUEST(seq < N-1)\nшлемо ITEM(seq), чекаємо seq+1",
                      size=10.5, color=FIELD))

    # WAIT_REQUEST -> WAIT_ACK (коли передано останній пункт seq == count-1)
    parts.append(arrow(730, 160, 730, 310, color=LINE, sw=1.8))
    parts.append(text(740, 235, "Отримано REQUEST(N-1)\nшлемо останній ITEM(N-1)",
                      size=11, color=INK, anchor="start"))

    # WAIT_ACK -> IDLE (Успіх)
    parts.append(arrow(630, 370, 200, 260, color=FIELD, sw=2))
    parts.append(text(430, 280, "Отримано MISSION_ACK(ACCEPTED) → Успіх!",
                      size=12, bold=True, color=FIELD))

    # WAIT_REQUEST / WAIT_ACK -> ERROR (Таймаут вичерпано або помилка)
    parts.append(arrow(730, 145, 490, 340, color=POS, sw=1.6))
    parts.append(arrow(670, 380, 510, 370, color=POS, sw=1.6))
    parts.append(text(570, 410, "Таймаут > MAX_RETRIES або MAV_MISSION_ERROR",
                      size=11, color=POS))

    # ERROR -> IDLE
    parts.append(arrow(310, 345, 180, 270, color=LINE, sw=1.8))
    parts.append(text(210, 335, "MISSION_ACK(CANCELLED)\nОчищення буфера", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "fsm-states.svg"), w, h, *parts)


# ── Фігура 3: Порівняння роздільної здатності float32 vs int32 ─────────────────
def fig_coord_precision():
    w, h = 920, 460
    parts = []

    # Ліва половина: 32-бітний float (IEEE 754)
    x_left = 240
    parts.append(text(x_left, 50, "Одинарна точність: float32 (IEEE 754)", size=15, bold=True, color=POS))
    parts.append(text(x_left, 75, "24 біти мантиси (~7 десяткових знаків) → крок сітки ~1.2…2.4 м",
                      size=12, color=MUTED))

    # Сітка з великим кроком (float)
    grid_y = 110
    grid_w, grid_h = 360, 240
    gx0 = x_left - grid_w / 2
    parts.append(rect(gx0, grid_y, grid_w, grid_h, fill="#fffaf9", stroke="#f5c6cb", sw=1.5, rx=6))

    step_fl = 80
    for ix in range(int(grid_w / step_fl) + 1):
        xx = gx0 + ix * step_fl
        parts.append(line(xx, grid_y, xx, grid_y + grid_h, color="#f5c6cb", sw=1, dash="3,3"))
    for iy in range(int(grid_h / step_fl) + 1):
        yy = grid_y + iy * step_fl
        parts.append(line(gx0, yy, gx0 + grid_w, yy, color="#f5c6cb", sw=1, dash="3,3"))

    # Посадкова платформа 1x1 м і ціль
    cx_f = gx0 + 140
    cy_f = grid_y + 110
    parts.append(rect(cx_f - 25, cy_f - 25, 50, 50, fill="#e2e3e5", stroke=LINE, sw=1.5, rx=3))
    parts.append(text(cx_f, cy_f + 4, "Майданчик (1×1 м)", size=9.5, color=INK))

    # Вузли сітки float32 (перескакують через майданчик)
    parts.append(circle(gx0 + 80, grid_y + 80, 5, fill=POS, stroke=POS))
    parts.append(circle(gx0 + 160, grid_y + 80, 5, fill=POS, stroke=POS))
    parts.append(circle(gx0 + 160, grid_y + 160, 5, fill=POS, stroke=POS))
    parts.append(circle(gx0 + 80, grid_y + 160, 5, fill=POS, stroke=POS))
    parts.append(text(gx0 + 160, grid_y + 65, "Вузол сітки float", size=10, bold=True, color=POS))

    # Пояснення під лівою частиною
    box_fl, _, _ = textbox(x_left, 400,
                           "Неможливо вказати точку всередині майданчика!\nПохибка квантування дискретної сітки перевищує ціль.",
                           size=11.5, pad=8, fill="#fdecea", stroke=POS)
    parts.append(box_fl)

    # Права половина: int32 (10⁻⁷ градуса)
    x_right = 680
    parts.append(text(x_right, 50, "Фіксована кома: int32 (10⁻⁷ deg)", size=15, bold=True, color=FIELD))
    parts.append(text(x_right, 75, "32-бітне ціле число → крок сітки рівно ~1.11 см",
                      size=12, color=MUTED))

    # Сітка з надзвичайно дрібним кроком (int32)
    rx0 = x_right - grid_w / 2
    parts.append(rect(rx0, grid_y, grid_w, grid_h, fill="#f6fcf8", stroke="#c3e6cb", sw=1.5, rx=6))

    step_int = 16
    for ix in range(int(grid_w / step_int) + 1):
        xx = rx0 + ix * step_int
        parts.append(line(xx, grid_y, xx, grid_y + grid_h, color="#d4edda", sw=0.8))
    for iy in range(int(grid_h / step_int) + 1):
        yy = grid_y + iy * step_int
        parts.append(line(rx0, yy, rx0 + grid_w, yy, color="#d4edda", sw=0.8))

    # Майданчик у правій частині
    cx_i = rx0 + 140
    cy_i = grid_y + 110
    parts.append(rect(cx_i - 25, cy_i - 25, 50, 50, fill="#d1e7dd", stroke=FIELD, sw=1.8, rx=3))
    parts.append(text(cx_i, cy_i + 4, "Майданчик (1×1 м)", size=9.5, color=FIELD, bold=True))
    parts.append(circle(cx_i, cy_i, 3.5, fill=FIELD, stroke=FIELD))
    parts.append(text(cx_i + 35, cy_i - 12, "Ціль (±1 см)", size=10, bold=True, color=FIELD))

    # Пояснення під правою частиною
    box_int, _, _ = textbox(x_right, 400,
                            "Ідеальне позиціонування для RTK GNSS і посадки:\nдискретність 1.1 см дозволяє точне утримання коридору.",
                            size=11.5, pad=8, fill="#e9f7ef", stroke=FIELD)
    parts.append(box_int)

    render(os.path.join(IMG_DIR, "coord-precision.svg"), w, h, *parts)


if __name__ == '__main__':
    fig_upload_sequence()
    fig_fsm_states()
    fig_coord_precision()
    print("Всі фігури згенеровано успішно.")
