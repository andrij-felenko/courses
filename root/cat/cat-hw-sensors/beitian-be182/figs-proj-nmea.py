# -*- coding: utf-8 -*-
"""Фігури вставки «proj-nmea-parse» (catalog/connect/gnss/beitian-be182).
Окремий скрипт, щоб НЕ чіпати авторський figs.py; пише у той самий ./img/.
Запуск: python figs-proj-nmea.py → ./img/parse-*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура A: конвеєр парсера ────────────────────────────────────────────────
# Потік байтів з UART → збирач рядків (від '$' до кінця рядка) → перевірка
# контрольної суми (гейт: сміття вилітає) → розбір полів GGA → переклад
# ddmm.mmmm у десяткові градуси → чисті lat/lon. Кожна ланка — окрема
# коробка, стрілки ведуть праворуч; «браковані» рядки скидаються вниз.
def fig_pipe():
    W, H = 900, 340
    p = []

    y = 150            # осьова лінія конвеєра
    boxh = 66
    # координати центрів п'яти ланок, з широкими проміжками під стрілки
    xs = [120, 315, 505, 690, 845]

    stages = [
        (xs[0], "БАЙТИ\nз UART", "…$GNGGA,12…\n38400 біт/с", MUTED),
        (xs[1], "ЗБИРАЧ\nрядків", "від «$»\nдо кінця рядка", INK),
        (xs[2], "КОНТРОЛЬНА\nсума", "XOR збігся?", NEG),
        (xs[3], "РОЗБІР\nполів GGA", "час · lat · lon\nfix · супутники", INK),
        (xs[4], "ddmm →\nградуси", "49.0521°\n2.5095°", FIELD),
    ]

    # спершу з'єднання, щоб коробки лягли зверху
    for i in range(len(xs) - 1):
        # ширина коробок різна; ведемо від правого краю до лівого краю наступної
        p.append(arrow(xs[i] + 66, y, xs[i + 1] - 66, y, color=LINE, sw=1.8))

    # коробки-ланки (textbox сам підганяє ширину під найдовший рядок)
    for cx, head, sub, col in stages:
        body, bw, bh = textbox(cx, y - 8, head, size=13, pad=10,
                               fill="#fbfcfd", stroke=col, sw=1.6, bold=True, min_w=104)
        p.append(body)
        # підпис-приклад ПІД коробкою, у своїй колонці, з відступом
        p.append(text(cx, y + boxh / 2 + 26, sub.split("\n")[0], 10, MUTED, "middle"))
        if "\n" in sub:
            p.append(text(cx, y + boxh / 2 + 40, sub.split("\n")[1], 10, MUTED, "middle"))

    # «браковані» рядки з гейта контрольної суми — стрілка ВБІК-униз від ПРАВОГО
    # краю коробки (не через власний підпис «XOR збігся?»), у сміттєве відро
    gx = xs[2]
    p.append(arrow(gx + 60, y + 12, gx + 138, y + 78, color=POS, sw=1.6))
    p.append(text(gx + 150, y + 92, "не збігся →", 11, POS, "middle"))
    p.append(text(gx + 150, y + 107, "викинути рядок", 11, POS, "middle"))

    render(os.path.join(IMG, "parse-pipe.svg"), W, H, *p,
           title="Що робить парсер: від сирих байтів до десяткових координат")


# ── Фігура B: розклад поля ddmm.mmmm ─────────────────────────────────────────
# Поле широти «4807.038» ділиться на градуси (усе, крім двох цифр перед
# крапкою) і хвилини (решта). Показуємо межу й формулу переведення.
def fig_ddmm():
    W, H = 760, 300
    p = []

    # велике поле-рядок по центру зверху, моноширинно розставлене по символах
    field = "4 8 0 7 . 0 3 8"
    chars = ["4", "8", "0", "7", ".", "0", "3", "8"]
    x0 = 250          # ліва межа першого символу
    step = 34         # крок між центрами символів
    top = 92
    cx_of = lambda i: x0 + i * step

    # підкладки-клітинки під групами: градуси (0,1) і хвилини (2..7)
    deg_l = cx_of(0) - step / 2 + 3
    deg_r = cx_of(1) + step / 2 - 3
    min_l = cx_of(2) - step / 2 + 3
    min_r = cx_of(7) + step / 2 - 3
    p.append(rect(deg_l, top - 26, deg_r - deg_l, 52, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    p.append(rect(min_l, top - 26, min_r - min_l, 52, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=6))

    for i, ch in enumerate(chars):
        p.append(text(cx_of(i), top + 8, ch, 24, INK, "middle", bold=True))

    # підписи груп ПІД клітинками, кожен по центру своєї групи, з відступом
    p.append(text((deg_l + deg_r) / 2, top + 46, "градуси", 13, NEG, "middle", bold=True))
    p.append(text((deg_l + deg_r) / 2, top + 63, "= 48", 12, NEG, "middle"))
    p.append(text((min_l + min_r) / 2, top + 46, "хвилини", 13, FIELD, "middle", bold=True))
    p.append(text((min_l + min_r) / 2, top + 63, "= 07.038", 12, FIELD, "middle"))

    # межа: дві цифри перед крапкою — це градуси; підпис межі зверху
    bx = (cx_of(1) + cx_of(2)) / 2
    p.append(line(bx, top - 40, bx, top + 30, color=POS, sw=1.8, dash="4,4"))
    p.append(text(bx, top - 48, "межа: дві цифри перед крапкою", 11, POS, "middle"))

    # формула переведення — окремим блоком нижче, з великим відступом
    fbody = fitbox(200, 214, 360, 56,
                   "десяткові = 48 + 07.038 / 60 = 48.1173°",
                   size=15, pad=12, fill="#fbfcfd", stroke=INK, sw=1.5)
    p.append(fbody)
    p.append(text(W / 2, 288, "хвилини ділимо на 60 і додаємо до градусів", 11, MUTED, "middle"))

    render(os.path.join(IMG, "parse-ddmm.svg"), W, H, *p,
           title="Формат NMEA: «градуси+хвилини» ddmm.mmmm, а не десяткові")


fig_pipe()
fig_ddmm()
print("Done. SVG in", IMG)
