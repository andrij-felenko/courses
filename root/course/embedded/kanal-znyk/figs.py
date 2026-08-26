# -*- coding: utf-8 -*-
"""Фігури до теми «Канал зник: що робити давачу (буфер, проріджування, скидання)».
Запуск: python figs.py  → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Енергетичний розгін: наївний пошук vs Backoff з джитером
# ─────────────────────────────────────────────────────────────────────────────
def fig_backoff_energy():
    f = []
    W, H = 840, 480
    f.append(text(W / 2, 26, "Енергетична ціна відновлення: наївний пошук проти експоненційного відкату",
                  size=16, bold=True))

    # Панель 1: Наївні спроби з постійним кроком (ліворуч)
    P1_X, P1_Y, P1_W, P1_H = 30, 55, 375, 395
    f.append(rect(P1_X, P1_Y, P1_W, P1_H, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(P1_X + P1_W / 2, P1_Y + 24, "Наївний повтор (кожні 10 с)", size=14, bold=True, color=POS))

    # Графік струму наївного варіанта
    GX1, GY1, GW1, GH1 = P1_X + 25, P1_Y + 130, 325, 110
    f.append(line(GX1, GY1 + GH1, GX1 + GW1, GY1 + GH1, color=LINE, sw=1.5))
    f.append(line(GX1, GY1, GX1, GY1 + GH1, color=LINE, sw=1.5))
    f.append(text(GX1 - 6, GY1 + 10, "120 мА", size=10, color=MUTED, anchor="end"))
    f.append(text(GX1 - 6, GY1 + GH1 - 4, "15 мкА", size=10, color=MUTED, anchor="end"))
    f.append(text(GX1 + GW1, GY1 + GH1 + 18, "Час (хвилини) →", size=10, color=MUTED, anchor="end"))

    # Імпульси струму наївного варіанта
    for i in range(5):
        bx = GX1 + 20 + i * 60
        f.append(rect(bx, GY1 + 10, 24, GH1 - 10, fill=POS, stroke=POS, sw=1, rx=2))
        f.append(text(bx + 12, GY1 + GH1 - 15, "TX", size=10, color="#ffffff", bold=True))

    tb1, _, _ = textbox(P1_X + P1_W / 2, P1_Y + 70,
                        "Пошук мережі: 4 с @ 120 мА\nСон між спробами: 6 с @ 15 мкА\nСередній струм I_avg ≈ 48 мА",
                        size=11.5, pad=6, fill="#ffffff", stroke=POS)
    f.append(tb1)

    tb1_bot, _, _ = textbox(P1_X + P1_W / 2, P1_Y + 325,
                            "Батарея 2400 мА·год (ER14505):\nВисадка в нуль за 50 годин (2 доби)!\nРезультат: мертвий вузол у полі.",
                            size=12, pad=8, fill="#ffffff", stroke=POS, bold=False, color=POS)
    f.append(tb1_bot)

    # Панель 2: Exponential Backoff + Jitter (праворуч)
    P2_X, P2_Y, P2_W, P2_H = 435, 55, 375, 395
    f.append(rect(P2_X, P2_Y, P2_W, P2_H, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(P2_X + P2_W / 2, P2_Y + 24, "Експоненційний відкат із джитером", size=14, bold=True, color=FIELD))

    # Графік струму відкату
    GX2, GY2, GW2, GH2 = P2_X + 25, P2_Y + 130, 325, 110
    f.append(line(GX2, GY2 + GH2, GX2 + GW2, GY2 + GH2, color=LINE, sw=1.5))
    f.append(line(GX2, GY2, GX2, GY2 + GH2, color=LINE, sw=1.5))
    f.append(text(GX2 - 6, GY2 + 10, "120 мА", size=10, color=MUTED, anchor="end"))
    f.append(text(GX2 - 6, GY2 + GH2 - 4, "15 мкА", size=10, color=MUTED, anchor="end"))
    f.append(text(GX2 + GW2, GY2 + GH2 + 18, "Час (години) →", size=10, color=MUTED, anchor="end"))

    # Імпульси струму зі зростаючими інтервалами
    offsets = [15, 50, 105, 195, 290]
    for idx, bx in enumerate(offsets):
        f.append(rect(GX2 + bx, GY2 + 10, 18, GH2 - 10, fill=FIELD, stroke=FIELD, sw=1, rx=2))
        f.append(text(GX2 + bx + 9, GY2 + GH2 - 15, "TX", size=9.5, color="#ffffff", bold=True))

    # Підписи інтервалів
    f.append(text(GX2 + 35, GY2 + GH2 - 40, "10с", size=10, color=MUTED))
    f.append(text(GX2 + 80, GY2 + GH2 - 40, "30с", size=10, color=MUTED))
    f.append(text(GX2 + 152, GY2 + GH2 - 40, "2хв", size=10, color=MUTED))
    f.append(text(GX2 + 245, GY2 + GH2 - 40, "15хв", size=10, color=MUTED))

    tb2, _, _ = textbox(P2_X + P2_W / 2, P2_Y + 70,
                        "Інтервал зростає: 10с → 30с → 2хв → 15хв → 1год\nВипадковий зсув (Full Jitter) усуває шторм колізій\nСередній струм I_avg ≈ 35 мкА",
                        size=11.5, pad=6, fill="#ffffff", stroke=FIELD)
    f.append(tb2)

    tb2_bot, _, _ = textbox(P2_X + P2_W / 2, P2_Y + 325,
                            "Батарея 2400 мА·год (ER14505):\nАвтономність збережено: понад 4 роки!\nДані накопичуються у Flash-буфері.",
                            size=12, pad=8, fill="#ffffff", stroke=FIELD, bold=False, color=FIELD)
    f.append(tb2_bot)

    render(os.path.join(OUT, "backoff-energy-drain.svg"), W, H, *f)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Кільцевий буфер на секторах NOR Flash та Erase-Ahead
# ─────────────────────────────────────────────────────────────────────────────
def fig_flash_ring_buffer():
    f = []
    W, H = 840, 530
    f.append(text(W / 2, 26, "Організація секторного кільцевого буфера Flash та атомарний коміт",
                  size=16, bold=True))

    # Сектори кільця
    SECTORS = [
        ("Сектор 0", "Підтверджено\n(вільний)", FILL, LINE),
        ("Сектор 1", "Tail: чекає\nвідправки", "#fff3cd", "#d39e00"),
        ("Сектор 2", "Архів\n(заповнений)", "#e8f4f8", NEG),
        ("Сектор 3", "Архів\n(заповнений)", "#e8f4f8", NEG),
        ("Сектор 4", "Head: активний\nдозапис", "#d4edda", FIELD),
        ("Сектор 5", "Erase-Ahead\n(стертий 0xFF)", "#f8d7da", POS),
        ("Сектор 6", "Вільний\n(стертий 0xFF)", FILL, LINE),
        ("Сектор 7", "Вільний\n(стертий 0xFF)", FILL, LINE),
    ]

    SX, SY, SW, SH = 30, 65, 92, 120
    for i, (name, role, fill_c, strk_c) in enumerate(SECTORS):
        x = SX + i * 98
        f.append(rect(x, SY, SW, SH, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        f.append(text(x + SW / 2, SY + 20, name, size=12, bold=True, color=INK))
        f.append(mtext(x + SW / 2, SY + 55, role, size=10.5, color=strk_c if strk_c != LINE else MUTED))
        f.append(text(x + SW / 2, SY + 105, "4096 B", size=9.5, color=MUTED))

    # Покажчики Head, Tail, Erase-Ahead
    f.append(arrow(SX + 1 * 98 + SW / 2, SY + SH + 35, SX + 1 * 98 + SW / 2, SY + SH + 4, color="#d39e00", sw=2))
    f.append(text(SX + 1 * 98 + SW / 2, SY + SH + 48, "TAIL (Хвіст)", size=11, bold=True, color="#d39e00"))

    f.append(arrow(SX + 4 * 98 + SW / 2, SY + SH + 35, SX + 4 * 98 + SW / 2, SY + SH + 4, color=FIELD, sw=2))
    f.append(text(SX + 4 * 98 + SW / 2, SY + SH + 48, "HEAD (Голова)", size=11, bold=True, color=FIELD))

    f.append(arrow(SX + 5 * 98 + SW / 2, SY + SH + 35, SX + 5 * 98 + SW / 2, SY + SH + 4, color=POS, sw=2))
    f.append(text(SX + 5 * 98 + SW / 2, SY + SH + 48, "Erase-Ahead", size=11, bold=True, color=POS))

    # Нижня частина: Формат кадру та механізм коміту
    FY = 265
    f.append(rect(25, FY, 790, 245, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(25 + 790 / 2, FY + 24, "Структура запису вимірювання та захист від раптового знеструмлення",
                  size=13.5, bold=True, color=INK))

    FIELDS = [
        ("Magic", "2B\n0xA55A", 55),
        ("SeqNum", "4B\n#10428", 70),
        ("Timestamp", "4B\nUnix epoch", 80),
        ("Flags", "2B\nClass/Tier", 65),
        ("Length", "2B\nLen = N", 65),
        ("Payload Data", "N Bytes\n[ADC/Sensors]", 160),
        ("CRC32", "4B\nIEEE 802.3", 75),
        ("Commit Token", "4B\n0xAA55AA55", 105),
    ]

    FX = 45
    for fname, fdesc, fw in FIELDS:
        f.append(rect(FX, FY + 45, fw, 60, fill="#edf2f7", stroke="#4a5568", sw=1.2, rx=4))
        f.append(text(FX + fw / 2, FY + 65, fname, size=10.5, bold=True, color=INK))
        f.append(mtext(FX + fw / 2, FY + 85, fdesc, size=9.5, color=MUTED))
        FX += fw + 6

    # Пояснення коміту
    tb_comm, _, _ = textbox(25 + 790 / 2, FY + 175,
                            "1. Дозапис кадру: записуються всі поля, крім Commit Token (у флеші лишається 0xFFFFFFFF).\n"
                            "2. Перевірка цілісності: MCU зчитує записаний кадр і звіряє CRC32.\n"
                            "3. Фіксація (Commit): слово Commit Token програмується в 0xAA55AA55 (перехід 1 → 0 без стирання).\n"
                            "Якщо живлення зникло посеред запису — токен лишається 0xFF, і під час старту пошкоджений запис ігнорується.",
                            size=11, pad=8, fill="#ffffff", stroke=MUTED)
    f.append(tb_comm)

    render(os.path.join(OUT, "flash-ring-buffer.svg"), W, H, *f)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Стратегії деградації при переповненні буфера
# ─────────────────────────────────────────────────────────────────────────────
def fig_buffer_decimation_tiers():
    import math
    f = []
    W, H = 840, 500
    f.append(text(W / 2, 26, "Багаторівнева деградація буфера при тривалому офлайні",
                  size=16, bold=True))

    # Стовпчик заповнення пам'яті (шкала ліворуч)
    BAR_X, BAR_Y, BAR_W, BAR_H = 35, 60, 50, 400
    f.append(rect(BAR_X, BAR_Y, BAR_W, BAR_H, fill="#edf2f7", stroke=LINE, sw=1.5, rx=6))

    # Рівні шкали
    # 0..70% (зелений, 280px)
    f.append(rect(BAR_X, BAR_Y + 120, BAR_W, 280, fill="#d4edda", stroke="none", rx=0))
    # 70..90% (жовтий, 80px)
    f.append(rect(BAR_X, BAR_Y + 40, BAR_W, 80, fill="#fff3cd", stroke="none", rx=0))
    # 90..100% (червоний, 40px)
    f.append(rect(BAR_X, BAR_Y + 40, BAR_W, 40, fill="#f8d7da", stroke="none", rx=0))
    f.append(rect(BAR_X, BAR_Y, BAR_W, BAR_H, fill="none", stroke=LINE, sw=1.5, rx=6))

    f.append(text(BAR_X + BAR_W / 2, BAR_Y + 25, "100%", size=10, bold=True, color=POS))
    f.append(text(BAR_X + BAR_W / 2, BAR_Y + 55, "90%", size=10, bold=True, color="#856404"))
    f.append(text(BAR_X + BAR_W / 2, BAR_Y + 135, "70%", size=10, bold=True, color=FIELD))
    f.append(text(BAR_X + BAR_W / 2, BAR_Y + BAR_H - 10, "0%", size=10, bold=True, color=MUTED))

    # 3 блоки політик праворуч
    PANEL_X, PANEL_W = 105, 700

    # Рівень 1: Нормальний режим (0..70%)
    L1_Y, L1_H = 290, 170
    f.append(rect(PANEL_X, L1_Y, PANEL_W, L1_H, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(PANEL_X + 15, L1_Y + 24, "Рівень 1 (Заповнення 0..70%): Повний сирий запис (Raw 1:1)",
                  size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(PANEL_X + 15, L1_Y + 46, "Збереження кожного відліку з повною частотою (наприклад, 10 Гц від IMU/тиску).",
                  size=11, color=INK, anchor="start"))

    # Схематичний сигнал рівня 1 (щільні точки)
    GX1, GY1, GW1, GH1 = PANEL_X + 20, L1_Y + 60, 660, 95
    f.append(rect(GX1, GY1, GW1, GH1, fill="#ffffff", stroke="#cbd5e0", sw=1, rx=4))
    points_1 = [(GX1 + 15 + i * 16, GY1 + 45 - 30 * math.sin(i * 0.4)) for i in range(40)]
    for px, py in points_1:
        f.append(circle(px, py, 2.8, fill=FIELD, stroke=FIELD))
    for i in range(len(points_1) - 1):
        f.append(line(points_1[i][0], points_1[i][1], points_1[i+1][0], points_1[i+1][1], color=FIELD, sw=1))
    f.append(text(GX1 + GW1 - 10, GY1 + 20, "100% вибірок збережено (Δt = 100 мс)", size=10, color=MUTED, anchor="end"))

    # Рівень 2: Проріджування зі збереженням піків (70..90%)
    L2_Y, L2_H = 150, 130
    f.append(rect(PANEL_X, L2_Y, PANEL_W, L2_H, fill="#fffdf5", stroke="#d39e00", sw=1.5, rx=6))
    f.append(text(PANEL_X + 15, L2_Y + 22, "Рівень 2 (Заповнення 70..90%): Проріджування (Decimation Δt → 4Δt)",
                  size=13, bold=True, color="#d39e00", anchor="start"))
    f.append(text(PANEL_X + 15, L2_Y + 42, "Видалення проміжних відліків із обов'язковим утриманням Min/Max огинаючої.",
                  size=11, color=INK, anchor="start"))

    GX2, GY2, GW2, GH2 = PANEL_X + 20, L2_Y + 52, 660, 68
    f.append(rect(GX2, GY2, GW2, GH2, fill="#ffffff", stroke="#cbd5e0", sw=1, rx=4))
    points_2 = [(GX1 + 15 + i * 64, GY1 + 45 - 30 * math.sin(i * 1.6)) for i in range(10)]
    for px, py in points_2:
        f.append(circle(px, GY2 + 34 - (GY1 + 45 - py) * 0.7, 3.5, fill="#d39e00", stroke="#d39e00"))
    for i in range(len(points_2) - 1):
        f.append(line(points_2[i][0], GY2 + 34 - (GY1 + 45 - points_2[i][1]) * 0.7,
                      points_2[i+1][0], GY2 + 34 - (GY1 + 45 - points_2[i+1][1]) * 0.7, color="#d39e00", sw=1.5, dash="4,3"))
    f.append(text(GX2 + GW2 - 10, GY2 + 18, "Збережено лише екстремуми та кожен 4-й відлік (економія 75%)", size=10, color=MUTED, anchor="end"))

    # Рівень 3: Статистична агрегація та захист аварій (90..100%)
    L3_Y, L3_H = 60, 82
    f.append(rect(PANEL_X, L3_Y, PANEL_W, L3_H, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    f.append(text(PANEL_X + 15, L3_Y + 20, "Рівень 3 (Заповнення > 90%): Статистичні зведення + Захист аномалій",
                  size=13, bold=True, color=POS, anchor="start"))
    f.append(text(PANEL_X + 15, L3_Y + 40, "Потік згортається у погодинні кортежі [T_start, N, Min, Max, Avg, Variance].",
                  size=11, color=INK, anchor="start"))
    f.append(text(PANEL_X + 15, L3_Y + 60, "Критичні події (тривоги, аварії датчика) мають прапорець NEVER_EVICT і не стираються ніколи.",
                  size=10.5, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "buffer-decimation-tiers.svg"), W, H, *f)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Відновлення каналу: пакетна реплікація (Bulk Batch Sync)
# ─────────────────────────────────────────────────────────────────────────────
def fig_bulk_sync_flow():
    f = []
    W, H = 840, 520
    f.append(text(W / 2, 26, "Протокол відновлення: пріоритет живого статусу та пакетне вивантаження архіву",
                  size=16, bold=True))

    # Стовпці учасників: Давач (ліворуч) та Шлюз / Хмара (праворуч)
    NODE_X, SVR_X = 180, 660
    TOP_Y, BOT_Y = 60, 480

    f.append(line(NODE_X, TOP_Y + 30, NODE_X, BOT_Y, color=MUTED, sw=1.5, dash="5,4"))
    f.append(line(SVR_X, TOP_Y + 30, SVR_X, BOT_Y, color=MUTED, sw=1.5, dash="5,4"))

    # Блоки учасників
    tb_node, _, _ = textbox(NODE_X, TOP_Y + 15, "Автономний давач\n(Flash Ring Buffer)", size=12, pad=6, fill="#e8f4f8", stroke=NEG, bold=True)
    f.append(tb_node)

    tb_svr, _, _ = textbox(SVR_X, TOP_Y + 15, "Хмарний сервер / Шлюз\n(Time-Series Database)", size=12, pad=6, fill="#f4faf6", stroke=FIELD, bold=True)
    f.append(tb_svr)

    # 1. Подія: Лінк відновився
    Y1 = 120
    f.append(rect(NODE_X - 100, Y1 - 12, 200, 24, fill="#fff3cd", stroke="#d39e00", sw=1, rx=4))
    f.append(text(NODE_X, Y1 + 4, "Канал з'явився (LINK_UP)", size=11, bold=True, color="#856404"))

    # 2. Відправка свіжого статусу (Live Telemetry)
    Y2 = 160
    f.append(arrow(NODE_X, Y2, SVR_X, Y2 + 20, color=FIELD, sw=2))
    f.append(text((NODE_X + SVR_X) / 2, Y2 + 2, "1. Свіжий статус (Live Now, Seq=2500)", size=11, bold=True, color=FIELD))
    f.append(text((NODE_X + SVR_X) / 2, Y2 + 16, "Оператор негайно бачить поточний стан", size=9.5, color=MUTED))

    # 3. Сервер підтверджує і замовляє історію
    Y3 = 205
    f.append(arrow(SVR_X, Y3, NODE_X, Y3 + 20, color=LINE, sw=1.5))
    f.append(text((NODE_X + SVR_X) / 2, Y3 + 2, "2. ACK(Live) + Sync Request: [Last_Known_Seq=1200]", size=10.5, color=INK))

    # 4. Вивантаження пакету архіву (Bulk Batch)
    Y4 = 255
    f.append(arrow(NODE_X, Y4, SVR_X, Y4 + 25, color=NEG, sw=2))
    f.append(text((NODE_X + SVR_X) / 2, Y4 + 2, "3. Пакет архіву #1: Кадри [Seq 1201..1216] (16 записів)", size=11, bold=True, color=NEG))
    f.append(text((NODE_X + SVR_X) / 2, Y4 + 18, "Зчитування з сектора Tail, одне мережеве корисне навантаження", size=9.5, color=MUTED))

    # 5. Сервер надсилає Block ACK з бітовою маскою
    Y5 = 310
    f.append(arrow(SVR_X, Y5, NODE_X, Y5 + 20, color=LINE, sw=1.5))
    f.append(text((NODE_X + SVR_X) / 2, Y5 + 2, "4. Block ACK: [AckSeq=1216, Bitmask=0xFFFF (все прийнято)]", size=10.5, color=INK))

    # 6. Зсув Tail у Flash
    Y6 = 355
    f.append(rect(NODE_X - 110, Y6 - 12, 220, 24, fill="#d4edda", stroke=FIELD, sw=1, rx=4))
    f.append(text(NODE_X, Y6 + 4, "Tail зсунуто вперед на 16 записів", size=10.5, bold=True, color=FIELD))

    # 7. Чергування: знову свіжий статус, тоді наступний пакет історії
    Y7 = 400
    f.append(arrow(NODE_X, Y7, SVR_X, Y7 + 20, color=FIELD, sw=1.8))
    f.append(text((NODE_X + SVR_X) / 2, Y7 + 2, "5. Свіжий статус (Live Now, Seq=2501)", size=10.5, bold=True, color=FIELD))

    Y8 = 445
    f.append(arrow(NODE_X, Y8, SVR_X, Y8 + 20, color=NEG, sw=1.8))
    f.append(text((NODE_X + SVR_X) / 2, Y8 + 2, "6. Пакет архіву #2: Кадри [Seq 1217..1232]", size=10.5, bold=True, color=NEG))

    render(os.path.join(OUT, "bulk-sync-flow.svg"), W, H, *f)

if __name__ == "__main__":
    fig_backoff_energy()
    fig_flash_ring_buffer()
    fig_buffer_decimation_tiers()
    fig_bulk_sync_flow()
    print("All figures generated successfully in ./img/")
