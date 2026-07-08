# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Життя об'єкта: без пулу (створити-знищити щоразу) проти з пулом (коло) ─────
def fig_borrow_return():
    W, H = 1120, 760
    frags = []

    # роздільна лінія між верхом і низом
    frags.append(line(60, 300, W - 60, 300, color="#d0d5db", sw=1.2, dash="7,7"))

    # ═══════════ ВЕРХ: БЕЗ ПУЛУ ═══════════
    frags.append(text(W / 2, 42, "Без пулу — кожне використання платить за народження",
                      size=16, bold=True, color=POS))

    # три однакові цикли створити→попрацювати→знищити, поряд
    cyc_cx = [W * 0.22, W * 0.5, W * 0.78]
    cy_top = 96
    step_labels = ["створити", "попрацювати", "знищити"]
    step_notes = ["ДОРОГО", "", "викинути"]
    step_cols = [POS, INK, MUTED]
    for k, ccx in enumerate(cyc_cx):
        frags.append(text(ccx, cy_top - 8, "використання %d" % (k + 1),
                          size=11.5, color=MUTED))
        prev_bottom = None
        for i, (lab, note, col) in enumerate(zip(step_labels, step_notes, step_cols)):
            by = cy_top + 18 + i * 62
            label = lab if not note else "%s (%s)" % (lab, note)
            b, bw, bh = textbox(ccx, by, label, size=12, bold=(i == 0),
                                fill=("#fdecea" if i == 0 else FILL),
                                stroke=col, sw=1.5, min_w=176)
            frags.append(b)
            if prev_bottom is not None:
                frags.append(arrow(ccx, prev_bottom, ccx, by - bh / 2 - 2,
                                   color=LINE, sw=1.4))
            prev_bottom = by + bh / 2
    frags.append(text(W / 2, 288, "…і так знову, і знову — кожен цикл оплачує дороге створення",
                      size=12, color=INK))

    # ═══════════ НИЗ: З ПУЛОМ ═══════════
    frags.append(text(W / 2, 342, "З пулом — народження раз, далі об'єкт кружляє між станами",
                      size=16, bold=True, color=FIELD))

    # пул-контейнер ліворуч із трьома об'єктами (стан: вільний/зайнятий)
    pool_x, pool_y, pool_w, pool_h = 90, 396, 300, 250
    frags.append(rect(pool_x, pool_y, pool_w, pool_h, fill="#f4fbf7",
                      stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(pool_x + pool_w / 2, pool_y + 26, "ПУЛ",
                      size=14, bold=True, color=FIELD))
    frags.append(text(pool_x + pool_w / 2, pool_y + 46,
                      "створені раз, на старті", size=11, color=MUTED))
    slots = [("об'єкт A — вільний", FIELD, "#e8f6ee"),
             ("об'єкт B — зайнятий", POS, "#fdecea"),
             ("об'єкт C — вільний", FIELD, "#e8f6ee")]
    for i, (lab, col, fill) in enumerate(slots):
        sy = pool_y + 92 + i * 50
        b, _, _ = textbox(pool_x + pool_w / 2, sy, lab, size=12,
                          fill=fill, stroke=col, sw=1.4, min_w=250)
        frags.append(b)

    # праворуч — клієнт, і коло позичити→працювати→повернути
    cli_x = W * 0.72
    ring_top = 402
    # три стани клієнта
    steps = [("acquire()  ← позичив", NEG, "#eaf0fd"),
             ("працює з об'єктом", INK, FILL),
             ("release()  ← повернув", FIELD, "#e8f6ee")]
    ys = []
    for i, (lab, col, fill) in enumerate(steps):
        sy = ring_top + i * 74
        ys.append(sy)
        b, bw, bh = textbox(cli_x, sy, lab, size=12.5, bold=True,
                            fill=fill, stroke=col, sw=1.6, min_w=250)
        frags.append(b)
        if i > 0:
            frags.append(arrow(cli_x, ys[i - 1] + bh / 2 + 2, cli_x, sy - bh / 2 - 2,
                               color=LINE, sw=1.5))

    # стрілка "acquire" від пулу до клієнта і "release" назад — по краях, повз написи
    ax_out = pool_x + pool_w
    frags.append(arrow(ax_out + 4, ring_top, cli_x - 132, ring_top,
                       color=NEG, sw=1.7))
    frags.append(text((ax_out + cli_x - 132) / 2, ring_top - 12,
                      "дай вільний", size=11, color=NEG))
    frags.append(arrow(cli_x - 132, ys[2], ax_out + 4, ys[2],
                       color=FIELD, sw=1.7))
    frags.append(text((ax_out + cli_x - 132) / 2, ys[2] + 20,
                      "поклади назад", size=11, color=FIELD))

    # замикання кола: від release угору до acquire (наступний користувач)
    loop_x = cli_x + 172
    frags.append(line(cli_x + 132, ys[2], loop_x, ys[2], color=MUTED, sw=1.4))
    frags.append(line(loop_x, ys[2], loop_x, ring_top, color=MUTED, sw=1.4))
    frags.append(arrow(loop_x, ring_top, cli_x + 132, ring_top, color=MUTED, sw=1.4))
    frags.append(text(loop_x + 8, (ring_top + ys[2]) / 2, "той самий",
                      size=10.5, color=MUTED, anchor="start"))
    frags.append(text(loop_x + 8, (ring_top + ys[2]) / 2 + 15, "об'єкт —",
                      size=10.5, color=MUTED, anchor="start"))
    frags.append(text(loop_x + 8, (ring_top + ys[2]) / 2 + 30, "наступному",
                      size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'borrow-return.svg'), W, H, *frags)


# ── Часова смуга: як пул із практики визрів у названий патерн і назад ─────────
def fig_timeline():
    W, H = 1180, 560
    frags = []

    # горизонтальна вісь часу
    axis_y = 300
    x0, x1 = 90, W - 60
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    frags.append(arrow(x1 - 2, axis_y, x1 + 2, axis_y, color=INK, sw=2))
    frags.append(text(x1 + 6, axis_y + 26, "час", size=12, color=MUTED, anchor="end"))

    # роки й позиції на осі (рівномірно розкидані з запасом між написами)
    marks = [
        (1994, 0.10, "up",
         ["«Банда чотирьох»", "23 патерни —", "пулу серед них НЕМА"],
         POS, "#fdecea"),
        (1999, 0.34, "down",
         ["JDBC 2.0 Optional Package:", "пул з'єднань —", "у стандарті мови"],
         FIELD, "#e8f6ee"),
        (2002, 0.58, "up",
         ["Kircher і Jain, «Pooling»", "(EuroPLoP, с. 497–510):", "пул описано як патерн"],
         NEG, "#eaf0fd"),
        (2005, 0.86, "down",
         ["Goetz і Bloch:", "«пулити все» — міф;", "лише важкі ресурси"],
         "#8e44ad", "#f3e9f7"),
    ]

    for year, t, side, lines, col, fill in marks:
        cx = x0 + t * (x1 - x0)
        # вузол на осі
        frags.append(circle(cx, axis_y, 8, fill=fill, stroke=col, sw=2.4))
        # рік — біля осі, з протилежного боку від картки
        yr_dy = 40 if side == "up" else -28
        frags.append(text(cx, axis_y + yr_dy, str(year), size=17, bold=True, color=col))
        # картка-опис — вгору або вниз, повз вісь (висоту знаємо з рядків)
        nlines = len(lines)
        bh = nlines * 12.5 * 1.3 + 2 * 10 - 12.5 * 0.3
        if side == "up":
            box_cy = axis_y - 78 - bh / 2
            conn_y2 = box_cy + bh / 2
        else:
            box_cy = axis_y + 88 + bh / 2
            conn_y2 = box_cy - bh / 2
        b, _, _ = textbox(cx, box_cy, "\n".join(lines), size=12.5, bold=False,
                          fill=fill, stroke=col, sw=1.6, min_w=246)
        frags.append(b)
        # тонка ніжка від вузла до картки
        stem_y1 = axis_y - 8 if side == "up" else axis_y + 8
        frags.append(line(cx, stem_y1, cx, conn_y2, color=col, sw=1.3, dash="4,4"))

    # підпис-дуга: практика → назва → розворот поради
    frags.append(text(W / 2, 40,
                      "Пул жив у практиці задовго до назви — і назву дістав уже після сумнівів",
                      size=15, bold=True, color=INK))
    frags.append(text(W / 2, H - 26,
                      "з інженерії продуктивності (бази, сервери) → у каталог патернів → назад до «міряй, не вір»",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_borrow_return()
    fig_timeline()
    print("figs done")
