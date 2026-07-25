# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_where_time_goes():
    """Час зосереджений у кількох рядках; зусилля розлите по всіх. Показує,
    чому рівномірна оптимізація промахує повз справжнє вузьке місце."""
    W, H = 760, 430
    frags = []
    frags.append(text(W/2, 30, "Куди йде час виконання проти куди йдуть зусилля", size=17, bold=True))

    # Дві колонки: ліворуч — де час; праворуч — куди зазвичай ллють зусилля.
    col_w = 150
    left_x = 150
    right_x = 560
    base_y = 360          # нижня лінія стовпчиків
    max_h = 250           # максимальна висота

    # Ліворуч: реальний розподіл часу — один модуль з'їдає майже все.
    # (частки часу за модулями)
    time_share = [0.90, 0.05, 0.03, 0.02]
    labels = ["Гарячий\nцикл", "Розбір", "Лог", "Старт"]
    n = len(time_share)
    slot = col_w / n
    bw = slot * 0.66
    frags.append(text(left_x, 70, "Де насправді час", size=14, bold=True, color=POS))
    for i, sh in enumerate(time_share):
        h = max_h * sh
        x = left_x - col_w/2 + i*slot + (slot-bw)/2
        y = base_y - h
        col = POS if i == 0 else MUTED
        fill = "#fdecea" if i == 0 else FILL
        frags.append(rect(x, y, bw, h, fill=fill, stroke=col, sw=1.8))
        pct = "%d%%" % round(sh*100)
        frags.append(text(x+bw/2, y-8, pct, size=12, bold=(i == 0), color=col))
        frags.append(mtext(x+bw/2, base_y+18, labels[i].split("\n"), size=10, color=MUTED, lh=1.15))

    # Праворуч: куди ллються зусилля без вимірювання — порівну на все.
    eff_share = [0.25, 0.25, 0.25, 0.25]
    frags.append(mtext(right_x, 70, ["Куди без вимірювання", "ллються зусилля"], size=14, bold=True, color=NEG, lh=1.15))
    for i, sh in enumerate(eff_share):
        h = max_h * sh
        x = right_x - col_w/2 + i*slot + (slot-bw)/2
        y = base_y - h
        frags.append(rect(x, y, bw, h, fill="#eaf0fd", stroke=NEG, sw=1.6))
        frags.append(text(x+bw/2, y-8, "25%", size=11, color=NEG))
        frags.append(mtext(x+bw/2, base_y+18, labels[i].split("\n"), size=10, color=MUTED, lh=1.15))

    # спільна базова лінія
    frags.append(line(left_x-col_w/2-10, base_y, left_x+col_w/2+10, base_y, color=INK, sw=1.5))
    frags.append(line(right_x-col_w/2-10, base_y, right_x+col_w/2+10, base_y, color=INK, sw=1.5))

    # Підпис-стрілка між колонками: промах.
    box, bw2, bh2 = textbox(W/2, 200, "Зусилля\nне туди", size=12, bold=True,
                            color=INK, fill="#fff8e1", stroke="#e0a800", pad=9)
    frags.append(box)
    frags.append(line(left_x+col_w/2+14, 200, W/2-bw2/2-6, 200, color="#e0a800", sw=1.6, dash="5,4"))
    frags.append(line(W/2+bw2/2+6, 200, right_x-col_w/2-14, 200, color="#e0a800", sw=1.6, dash="5,4"))

    render(os.path.join(IMG, "where-time-goes.svg"), W, H, *frags)


def fig_loop():
    """Дисциплінований цикл (вимір → знайти гаряче → правити те → знову вимір)
    проти петлі-пастки (вгадав → правив усе → повільно + складно)."""
    W, H = 780, 340
    frags = []
    frags.append(text(W/2, 28, "Дисциплінований цикл проти передчасної петлі", size=17, bold=True))

    # Верхній ряд — правильний цикл, зелений.
    cy1 = 120
    steps = ["Виміряй", "Знайди\nгаряче", "Правь\nЛИШЕ те", "Виміряй\nзнову"]
    xs = [140, 320, 500, 680]
    for i, (x, s) in enumerate(zip(xs, steps)):
        b, bw, bh = textbox(x, cy1, s, size=12, bold=True, color=INK,
                            fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10, min_w=110)
        frags.append(b)
    for i in range(len(xs)-1):
        frags.append(arrow(xs[i]+58, cy1, xs[i+1]-58, cy1, color=FIELD, sw=2))
    # зворотна дуга «повторюй»
    frags.append(line(xs[-1], cy1+34, xs[-1], cy1+58, color=FIELD, sw=1.8))
    frags.append(line(xs[-1], cy1+58, xs[0], cy1+58, color=FIELD, sw=1.8))
    frags.append(arrow(xs[0], cy1+58, xs[0], cy1+34, color=FIELD, sw=1.8))
    frags.append(text(W/2, cy1+74, "повторюй, поки повільно там, де це видно користувачеві", size=11, color=FIELD))

    # Нижній ряд — пастка, червоний.
    cy2 = 258
    steps2 = ["Вгадай\nвузьке місце", "Ускладни\nУСЕ", "Повільно + важко\nчитати й міняти"]
    xs2 = [180, 400, 640]
    for x, s in zip(xs2, steps2):
        b, bw, bh = textbox(x, cy2, s, size=12, bold=True, color=INK,
                            fill="#fdecea", stroke=POS, sw=1.8, pad=10, min_w=120)
        frags.append(b)
    frags.append(arrow(xs2[0]+72, cy2, xs2[1]-64, cy2, color=POS, sw=2))
    frags.append(arrow(xs2[1]+64, cy2, xs2[2]-96, cy2, color=POS, sw=2))
    frags.append(text(W/2, cy2+52, "код-борг лишається назавжди, пришвидшення — часто нуль", size=11, color=POS))

    render(os.path.join(IMG, "optimize-loop.svg"), W, H, *frags)


def fig_amdahl_two_bets():
    """Дві однакові «години праці» на терезах закону Амдала: удар у холодну
    частку p≈0.05 (стеля 1.05×, борг лишається) проти удару в гарячу p≈0.8
    (стеля 2.78×, виміряно ~4.8×). Та сама праця — різна віддача, бо різне p."""
    W, H = 820, 520
    frags = []
    frags.append(text(W/2, 30, "Та сама година праці на різних частках часу", size=17, bold=True))

    # Спільна геометрія двох панелей. Стрічка = час тіла циклу (100%).
    bar_x = 70            # лівий край стрічки часу
    bar_w = 300          # ширина стрічки
    bar_h = 44
    box_cx = bar_x + bar_w + 44 + 118    # центр рамки стелі праворуч
    panels = [
        # (центр Y стрічки, підпис, частка p, колір, стеля, вимір, нотатка)
        (185, "Наосліп: розгортання б'є в НАКЛАДНІ циклу",
         0.05, POS, "стеля 1.05×", None, "борг лишається, виграш ≈ 0"),
        (390, "За виміром: множення на обернене б'є в ПОДІЛ",
         0.80, FIELD, "стеля 2.78×", "виміряно ~4.8×", "борг мінімальний"),
    ]

    for (cy, caption, p, hot_col, ceil_txt, meas_txt, note) in panels:
        hot_w = bar_w * p
        y = cy - bar_h/2
        # «удар праці»: підпис і коротка стрілка СТОЯТЬ ВИЩЕ за підпис панелі,
        # у чистому просторі — тіп лягає на верх стрічки, нікого не перетинаючи.
        hx = bar_x + hot_w/2
        frags.append(text(hx, cy - bar_h/2 - 44, "година праці", size=11, bold=True, color=hot_col))
        frags.append(arrow(hx, cy - bar_h/2 - 38, hx, y - 2, color=hot_col, sw=2.4))
        # Підпис панелі — праворуч від стрілки-удару, щоб не накластися.
        frags.append(text(bar_x + 96, cy - bar_h/2 - 14, caption, size=13, bold=True,
                          color=INK, anchor="start"))
        # Стрічка часу: холодна решта (світла) + гаряча частка (виділена).
        frags.append(rect(bar_x, y, bar_w, bar_h, fill=FILL, stroke=MUTED, sw=1.4))
        fill_hot = "#fdecea" if hot_col == POS else "#eafaf1"
        frags.append(rect(bar_x, y, hot_w, bar_h, fill=fill_hot, stroke=hot_col, sw=2.2))
        # Напис частки p: усередині широкої частки, або праворуч від вузького сливера
        # (у холодній зоні), щоб не потрапити під стрілку-удар над ним.
        p_lbl = "p ≈ %.2f" % p
        if hot_w > 78:
            frags.append(text(bar_x + hot_w/2, cy + 5, p_lbl, size=13, bold=True, color=hot_col))
        else:
            frags.append(text(bar_x + hot_w + 8, cy + 5, p_lbl, size=12, bold=True,
                              color=hot_col, anchor="start"))
        # Підпис «решту часу праця не чіпає» — у холодній частині, коли є місце
        # і коли p-напис не сидить там само (тобто лише для широкого гарячого).
        if (bar_w - hot_w) > 150 and hot_w > 78:
            rest_cx = bar_x + hot_w + (bar_w - hot_w)/2
            frags.append(text(rest_cx, cy + 5, "решту часу праця не чіпає", size=11, color=MUTED))
        # Рамка стелі Амдала праворуч.
        parts = [ceil_txt] + ([meas_txt] if meas_txt else []) + [note]
        b, bw, bh = textbox(box_cx, cy, "\n".join(parts), size=12,
                            bold=False, color=INK,
                            fill=("#fff8e1" if hot_col == POS else "#eafaf1"),
                            stroke=("#e0a800" if hot_col == POS else FIELD),
                            sw=1.8, pad=10, min_w=224)
        # Стрілка від стрічки до рамки стелі (обидва кінці в порожньому просторі).
        frags.append(arrow(bar_x + bar_w + 5, cy, box_cx - bw/2 - 6, cy, color=hot_col, sw=2))
        frags.append(b)

    # Формула-нагадування внизу.
    b, bw, bh = textbox(W/2, 480, "S = 1 / ((1 − p) + p/s)   —   мале p ⇒ стеля притиснута до 1",
                        size=13, bold=True, color=INK, fill="#eef2f7", stroke=MUTED, sw=1.4, pad=10)
    frags.append(b)

    render(os.path.join(IMG, "amdahl-two-bets.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_where_time_goes()
    fig_loop()
    fig_amdahl_two_bets()
    print("figs written to", IMG)
