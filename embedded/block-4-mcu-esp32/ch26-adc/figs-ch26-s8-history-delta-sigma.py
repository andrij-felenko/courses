# -*- coding: utf-8 -*-
"""
Фігури для 📜 Історія до теми 4.8.8 — «Дельта-сигма: як грубий 1-бітний компаратор
навчили бачити на 24 біти».
Файл вставки: ch26-s8-history-delta-sigma.md

Рис. 4.8.8i.1 — Стрічка-лінія народження дельта-сигми крізь країни й десятиліття
Рис. 4.8.8i.2 — Дельта-модуляція → переставити інтегратор → дельта-сигма (блок-схема)

Запуск: python figs-ch26-s8-history-delta-sigma.py
Вивід:  ./img/fig-26-8i-1-lineage.svg
        ./img/fig-26-8i-2-delta-to-deltasigma.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.8.8i.1 — Стрічка часу народження дельта-сигми
# ─────────────────────────────────────────────────────────────────────────────
def fig1_lineage():
    W, H = 980, 460

    frags = []

    # Заголовок
    frags.append(text(W / 2, 30, "Дельта-сигма народжувалася ~36 років і в кількох країнах", 17, INK, "middle", bold=True))
    frags.append(text(W / 2, 52, "перемогла не перша ідея, а та архітектура, що зібрала чужі шматки в робочу систему", 11, MUTED, "middle"))

    # Вісь часу — горизонтальна лінія
    X0, X1, Y_AXIS = 60, 920, 200
    frags.append(line(X0, Y_AXIS, X1, Y_AXIS, color=MUTED, sw=2.5))
    # Стрілка вправо
    frags.append(arrow(X1 - 2, Y_AXIS, X1, Y_AXIS, color=MUTED, sw=2.5))

    # Мітки подій: (рік, підпис-вузол [багаторядковий], підпис-внесок, вище/нижче)
    events = [
        (1946, "1946\nITT, Франція",   "Делорен, Ван Мірло,\nДержавич — патент\nдельта-модуляції\n(французьке бюро)", "above"),
        (1952, "1952\nPhilips, НЛ",    "де Ягер:\nперший строгий\nаналіз і межі\nдельта-модуляції",                  "below"),
        (1954, "1954\nBell Labs, США", "Катлер:\nзворотний зв'язок\nнавколо грубого\nквантувача\n(зерно «сигми»)",   "above"),
        (1962, "1962\nТокіо, Японія",  "Іносе, Ясуда,\nМуракамі:\nфорвардний інтегратор\n+ назва Δ-Σ",              "below"),
        (1985, "~1980-ті\nКМОН-хвиля", "Switched-capacitor\nінтегратори — цифрова\nреінкарнація\nдельта-сигми",     "above"),
        (2010, "Сьогодні",             "24-бітний АЦП\nна вашій платі:\nADS1115, ADS1232,\nΔΣ-клас",                 "below"),
    ]

    # Розмістити вузли рівномірно вздовж осі
    year_min, year_max = 1940, 2020
    def xpos(yr):
        return X0 + (yr - year_min) / (year_max - year_min) * (X1 - X0 - 20)

    # Кольори вузлів по країнах
    country_colors = {
        "above": "#e8f4fd",
        "below": "#fff8e1",
    }
    node_strokes = ["#1f47b5", "#27ae60", "#c0392b", "#e67e22", "#8e44ad", "#2c3e50"]

    for i, (yr, label, contrib, side) in enumerate(events):
        xp = xpos(yr)
        nc = node_strokes[i]
        # Вертикальна ніжка від осі до вузла
        if side == "above":
            y_node = Y_AXIS - 95
            frags.append(line(xp, Y_AXIS - 6, xp, y_node + 30, color=nc, sw=1.5, dash="4,3"))
        else:
            y_node = Y_AXIS + 95
            frags.append(line(xp, Y_AXIS + 6, xp, y_node - 30, color=nc, sw=1.5, dash="4,3"))

        # Крапка на осі
        frags.append(circle(xp, Y_AXIS, 7, fill=nc, stroke=nc, sw=2))

        # Вузол — рамка з датою та країною
        tb, tw, th = textbox(xp, y_node if side == "above" else y_node,
                             label, size=11, pad=7,
                             fill="#f0f4ff" if side == "above" else "#fffbea",
                             stroke=nc, sw=1.8, bold=True)
        frags.append(tb)

        # Внесок — дрібний текст під/над рамкою
        gap = 10
        if side == "above":
            ty = y_node + th / 2 + gap + 10
        else:
            ty = y_node - th / 2 - gap - 30

        contrib_lines = contrib.split("\n")
        line_h = 14
        for j, cl in enumerate(contrib_lines):
            frags.append(text(xp, ty + j * line_h, cl, size=10, color=INK, anchor="middle"))

    # Підпис осі — «1940» «2020»
    frags.append(text(X0 + 4, Y_AXIS + 22, "1940", size=10, color=MUTED, anchor="middle"))
    frags.append(text(X1 - 10, Y_AXIS + 22, "2020+", size=10, color=MUTED, anchor="middle"))

    # Висновок внизу
    concl = "Перемогла не перша ідея — перемогла та, що вдало зібрала чужі шматки (дельту Делорена + петлю Катлера + інтегратор Іносе) в один кремній."
    tb2, tw2, th2 = textbox(W / 2, H - 30, concl, size=10, pad=10,
                            fill="#f0f7f0", stroke=FIELD, sw=1.5, color=INK)
    frags.append(tb2)

    render(os.path.join(OUT, "fig-26-8i-1-lineage.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.8.8i.2 — Дві блок-схеми: дельта-модуляція → дельта-сигма
# ─────────────────────────────────────────────────────────────────────────────
def fig2_delta_to_deltasigma():
    W, H = 960, 420

    frags = []

    # Заголовок
    frags.append(text(W / 2, 30, "Що зробили в Токіо 1962-го: переставити інтегратор уперед", 17, INK, "middle", bold=True))
    frags.append(text(W / 2, 52, "один крок — і зникає перевантаження нахилом, з'являється формування шуму й сенс обох літер назви", 10.5, MUTED, "middle"))

    # ── Ліва половина: класична дельта-модуляція ─────────────────────────────
    LX = 240   # центр лівої схеми
    col_head_y = 80
    frags.append(text(LX, col_head_y, "Класична дельта-модуляція", 14, INK, "middle", bold=True))
    frags.append(text(LX, col_head_y + 18, "(Делорен, 1946; де Ягер, 1952)", 10, MUTED, "middle"))

    # Позначення блоків (зверху вниз, зліва направо у петлі)
    # Вузол різниці Δ (кружок)
    nd_x, nd_y = LX - 90, 180
    frags.append(circle(nd_x, nd_y, 18, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(nd_x, nd_y + 6, "Δ", size=18, color=NEG, anchor="middle", bold=True))
    frags.append(text(nd_x, nd_y + 28, "вузол\nрізниці", size=9, color=MUTED, anchor="middle"))

    # 1-бітний квантувач/компаратор
    qx, qy = LX + 30, 180
    tb_q, tw_q, th_q = textbox(qx, qy, "1-бітний\nквантувач\n(компаратор)", size=11, pad=10,
                                fill="#fdecea", stroke=POS, sw=2)
    frags.append(tb_q)
    frags.append(text(qx, qy + th_q / 2 + 14, "виходить ±1 кожен такт", size=9, color=MUTED, anchor="middle"))

    # Стрілка від Δ до квантувача
    frags.append(arrow(nd_x + 18, nd_y, qx - tw_q / 2, qy, color=NEG, sw=1.8))

    # Вихід — бітовий потік праворуч
    out_x = LX + 165
    frags.append(text(out_x, nd_y - 16, "1-бітний", size=10, color=INK, anchor="start"))
    frags.append(text(out_x, nd_y - 2, "потік", size=10, color=INK, anchor="start"))
    frags.append(arrow(qx + tw_q / 2, qy, out_x + 30, qy, color=POS, sw=1.8))

    # Петля зворотного зв'язку: інтегратор У ПЕТЛІ (під квантувачем)
    int_x, int_y = LX - 30, 295
    tb_i, tw_i, th_i = textbox(int_x, int_y, "Інтегратор Σ\n(у петлі ЗЗ)", size=11, pad=10,
                                fill="#fff8e1", stroke="#e67e22", sw=2)
    frags.append(tb_i)
    frags.append(text(int_x, int_y + th_i / 2 + 14, "накопичує похибку", size=9, color=MUTED, anchor="middle"))

    # Лінії петлі зворотного зв'язку
    # Від виходу квантувача вниз → до інтегратора
    frags.append(line(qx + tw_q / 2 - 10, qy + th_q / 2, qx + tw_q / 2 - 10, int_y - th_i / 2 - 2, color=MUTED, sw=1.5, dash="5,3"))
    frags.append(arrow(qx + tw_q / 2 - 10, int_y - th_i / 2 - 2, int_x + tw_i / 2, int_y, color=MUTED, sw=1.5))
    # Від інтегратора вліво → до вузла різниці
    frags.append(arrow(int_x - tw_i / 2, int_y, nd_x, nd_y + 18, color=MUTED, sw=1.5))

    # Вхідний сигнал
    frags.append(arrow(nd_x - 60, nd_y, nd_x - 18, nd_y, color=INK, sw=1.8))
    frags.append(text(nd_x - 80, nd_y - 8, "x(t)", size=12, color=INK, anchor="middle", bold=True))

    # Підпис «кодує НАХИЛ сигналу»
    frags.append(text(LX, H - 30, "кодує нахил (швидкість зміни) сигналу", size=10, color=MUTED, anchor="middle"))
    frags.append(text(LX, H - 16, "⚠ перевантаження нахилом при швидких сигналах", size=10, color=POS, anchor="middle"))

    # ── Центральна стрілка-перехід ───────────────────────────────────────────
    MX = 480
    frags.append(arrow(MX - 38, 200, MX + 38, 200, color=FIELD, sw=3.5))
    frags.append(text(MX, 190, "переставити", size=11, color=FIELD, anchor="middle", bold=True))
    frags.append(text(MX, 218, "інтегратор", size=11, color=FIELD, anchor="middle", bold=True))
    frags.append(text(MX, 235, "уперед", size=11, color=FIELD, anchor="middle", bold=True))
    frags.append(text(MX, 258, "Іносе, Ясуда,", size=9, color=MUTED, anchor="middle"))
    frags.append(text(MX, 271, "Муракамі, 1962", size=9, color=MUTED, anchor="middle"))

    # ── Права половина: дельта-сигма ─────────────────────────────────────────
    RX = 720   # центр правої схеми
    frags.append(text(RX, col_head_y, "Дельта-сигма (Δ-Σ)", 14, INK, "middle", bold=True))
    frags.append(text(RX, col_head_y + 18, "(Іносе / Ясуда / Муракамі, Токіо, 1962)", 10, MUTED, "middle"))

    # Інтегратор Σ — УПЕРЕД, у прямому тракті
    int2_x, int2_y = RX - 70, 180
    tb_i2, tw_i2, th_i2 = textbox(int2_x, int2_y, "Σ\nінтегратор", size=13, pad=12,
                                   fill="#eef6ef", stroke=FIELD, sw=2.5, bold=True)
    frags.append(tb_i2)
    frags.append(text(int2_x, int2_y + th_i2 / 2 + 14, "у прямому тракті!", size=9, color=FIELD, anchor="middle", bold=True))

    # Вхідний сигнал до Σ
    frags.append(arrow(RX - 70 - tw_i2 / 2 - 50, int2_y, RX - 70 - tw_i2 / 2, int2_y, color=INK, sw=1.8))
    frags.append(text(RX - 70 - tw_i2 / 2 - 60, int2_y - 8, "x(t)", size=12, color=INK, anchor="middle", bold=True))

    # 1-бітний квантувач після Σ
    q2x, q2y = RX + 100, 180
    tb_q2, tw_q2, th_q2 = textbox(q2x, q2y, "1-бітний\nквантувач\n(Δ)", size=11, pad=10,
                                   fill="#fdecea", stroke=POS, sw=2)
    frags.append(tb_q2)
    frags.append(text(q2x, q2y + th_q2 / 2 + 14, "та сама 1-бітна логіка", size=9, color=MUTED, anchor="middle"))

    # Стрілка від Σ до квантувача
    frags.append(arrow(int2_x + tw_i2 / 2, int2_y, q2x - tw_q2 / 2, q2y, color=FIELD, sw=1.8))

    # Вихід — бітовий потік
    out2_x = RX + 210
    frags.append(text(out2_x, q2y - 16, "1-бітний", size=10, color=INK, anchor="start"))
    frags.append(text(out2_x, q2y - 2, "потік", size=10, color=INK, anchor="start"))
    frags.append(arrow(q2x + tw_q2 / 2, q2y, out2_x + 30, q2y, color=POS, sw=1.8))

    # Петля ЗЗ (проста, від виходу квантувача назад до входу Σ)
    fb_y = 310
    # лінія вниз від квантувача
    frags.append(line(q2x, q2y + th_q2 / 2, q2x, fb_y, color=MUTED, sw=1.5, dash="5,3"))
    # лінія ліворуч до входу Σ
    frags.append(line(q2x, fb_y, int2_x - tw_i2 / 2 - 20, fb_y, color=MUTED, sw=1.5, dash="5,3"))
    # стрілка вгору до входу інтегратора (зворотній зв'язок)
    frags.append(arrow(int2_x - tw_i2 / 2 - 20, fb_y, int2_x - tw_i2 / 2 - 20, int2_y + 10, color=MUTED, sw=1.5))
    frags.append(text(int2_x - tw_i2 / 2 - 52, (int2_y + fb_y) / 2, "ЗЗ", size=10, color=MUTED, anchor="middle"))

    # Підпис «кодує САМ сигнал»
    frags.append(text(RX, H - 30, "кодує сам сигнал (не нахил)", size=10, color=FIELD, anchor="middle", bold=True))
    frags.append(text(RX, H - 16, "шум виштовхується у високі частоти → усередненням → 24 біти", size=10, color=FIELD, anchor="middle"))

    # Підпис сенсу літер
    letter_y = 360
    tb_l, _, _ = textbox(RX, letter_y,
                         "Δ = різниця (спадок Делорена/Катлера)\nΣ = доданий форвардний інтегратор",
                         size=11, pad=10, fill="#f4eafb", stroke=MUTED, sw=1.5)
    frags.append(tb_l)

    render(os.path.join(OUT, "fig-26-8i-2-delta-to-deltasigma.svg"), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig1_lineage()
    fig2_delta_to_deltasigma()
    print("Готово: fig-26-8i-1-lineage.svg, fig-26-8i-2-delta-to-deltasigma.svg")
