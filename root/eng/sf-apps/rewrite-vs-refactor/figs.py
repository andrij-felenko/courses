# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_step_vs_chasm():
    """Ліворуч: рефакторинг — сходинки малих зелених кроків, система працює на кожному.
       Праворуч: переписування — прірва між «старе працює» і «нове працює»."""
    W, H = 860, 460
    frags = []

    # -- Ліва половина: сходинки --
    lx = 60
    frags.append(text(215, 60, "Рефакторинг: сходинки", size=16, bold=True, color=FIELD))
    frags.append(text(215, 82, "робоча система на кожному кроці", size=12, color=MUTED))

    # сходинки, що піднімаються зліва направо
    steps = 4
    base_y = 400
    step_w = 66
    step_h = 46
    for i in range(steps):
        x = lx + i * step_w
        y = base_y - i * step_h
        frags.append(rect(x, y, step_w - 8, step_h - 6, fill="#eaf7ef", stroke=FIELD, sw=2))
        # зелена галочка «система жива на цьому кроці»
        frags.append(text(x + (step_w - 8) / 2, y + (step_h - 6) / 2 + 5, "✓", size=18, bold=True, color=FIELD))
    # висхідна стрілка вздовж сходинок
    frags.append(arrow(lx - 8, base_y + step_h - 6, lx + steps * step_w - 6, base_y - (steps - 1) * step_h - 2, color=INK, sw=1.8))
    frags.append(text(lx + 6, base_y + 40, "малі зворотні кроки, тести зелені", size=11, color=INK, anchor="start"))

    # роздільна вертикаль
    frags.append(line(430, 45, 430, 420, color=MUTED, sw=1.2, dash="5,5"))

    # -- Права половина: прірва --
    frags.append(text(645, 60, "Переписування: прірва", size=16, bold=True, color=POS))
    frags.append(text(645, 82, "робочого продукту немає під час прірви", size=12, color=MUTED))

    # платформа «старе працює»
    b1, w1, h1 = textbox(540, 150, "старе\nпрацює", size=13, bold=True,
                         fill="#eef1f5", stroke=INK, sw=1.8)
    frags.append(b1)
    # платформа «нове працює»
    b2, w2, h2 = textbox(760, 150, "нове\nпрацює", size=13, bold=True,
                         fill="#eaf7ef", stroke=FIELD, sw=1.8)
    frags.append(b2)

    # прірва між ними — заштрихована западина
    gx1, gx2 = 540 + w1 / 2, 760 - w2 / 2
    gy = 200
    frags.append(line(gx1, gy, gx1, 330, color=INK, sw=1.6))
    frags.append(line(gx2, gy, gx2, 330, color=INK, sw=1.6))
    # хвиляста «яма»
    frags.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
                 % (gx1, gy, (gx1 + gx2) / 2, 360, gx2, gy,
                    (gx1 + gx2) / 2, 300, gx1, gy, POS))
    frags.append(text((gx1 + gx2) / 2, 270, "ПРІРВА", size=15, bold=True, color=POS))
    frags.append(text((gx1 + gx2) / 2, 292, "продукту немає", size=11, color=POS))

    # ризикований стрибок через прірву
    frags.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="7,5" marker-end="url(#arrow)"/>'
                 % (gx1, 185, (gx1 + gx2) / 2, 120, gx2, 185, POS))
    frags.append(text((gx1 + gx2) / 2, 108, "ризикований стрибок", size=11, color=POS))

    render(os.path.join(IMG, 'step-vs-chasm.svg'), W, H, *frags)


def fig_bigbang_vs_strangler():
    """Вгорі: big-bang — заморозка + прірва + одномоментний перескок.
       Внизу: поступова заміна — стара звужується, нова росте, продукт живий."""
    W, H = 860, 470
    frags = []

    # ── ВГОРІ: big-bang ──
    frags.append(text(W / 2, 46, "Big-bang: заморозити старе й перескочити прірву", size=15, bold=True, color=POS))
    ty = 90
    # смуга «старе заморожене»
    frags.append(rect(60, ty, 300, 40, fill="#eef1f5", stroke=INK, sw=1.6))
    frags.append(text(210, ty + 25, "старе заморожене (нічого нового)", size=12, color=INK))
    # прірва
    frags.append(rect(360, ty, 180, 40, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(450, ty + 25, "прірва", size=12, bold=True, color=POS))
    # нове
    frags.append(rect(540, ty, 260, 40, fill="#eaf7ef", stroke=FIELD, sw=1.6))
    frags.append(text(670, ty + 25, "нове одразу все", size=12, color=INK))
    # одномоментний перескок
    frags.append('<path d="M535 %.1f Q 540 %.1f 545 %.1f" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>'
                 % (ty + 60, ty + 90, ty + 60, POS))
    frags.append(text(540, ty + 78, "перемикання одним вибухом", size=11, color=POS, anchor="middle"))

    # роздільник
    frags.append(line(60, 205, 800, 205, color=MUTED, sw=1.0, dash="4,4"))

    # ── ВНИЗУ: поступова заміна ──
    frags.append(text(W / 2, 250, "Поступова заміна: нове росте поряд, продукт живий щокроку", size=15, bold=True, color=FIELD))

    cols = 5
    col_w = 128
    x0 = 70
    top = 290
    band_h = 120
    labels = ["старт", "крок", "крок", "крок", "готово"]
    for i in range(cols):
        x = x0 + i * col_w
        frac_new = i / (cols - 1)          # частка нового росте 0 → 1
        h_new = int(band_h * frac_new)
        h_old = band_h - h_new
        # старе (згори вниз спадає)
        if h_old > 4:
            frags.append(rect(x, top, col_w - 24, h_old, fill="#eef1f5", stroke=INK, sw=1.4))
        # нове (знизу росте)
        if h_new > 4:
            frags.append(rect(x, top + h_old, col_w - 24, h_new, fill="#eaf7ef", stroke=FIELD, sw=1.4))
        frags.append(text(x + (col_w - 24) / 2, top + band_h + 20, labels[i], size=11, color=MUTED))
        frags.append(text(x + (col_w - 24) / 2, top + band_h + 38, "✓ живе", size=11, color=FIELD, bold=True))

    # підписи смуг — праворуч, з запасом, повз колонки
    frags.append(text(x0 + 6, top - 10, "старе", size=12, color=INK, anchor="start"))
    frags.append(text(x0 + cols * col_w - 30, top - 10, "нове", size=12, color=FIELD, anchor="end", bold=True))

    render(os.path.join(IMG, 'bigbang-vs-strangler.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_step_vs_chasm()
    fig_bigbang_vs_strangler()
    print("ok: figures written to", IMG)
