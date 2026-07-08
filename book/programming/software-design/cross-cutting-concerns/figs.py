# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_scatter_tangle():
    """Ліворуч: концерн (логування) розмазаний по кожному методу — переплетення й розпорошення.
    Праворуч: той самий концерн зібрано в одне місце (зріз), методи чисті."""
    W, H = 760, 430
    frags = []
    frags.append(text(W/2, 30, "Один концерн — два способи його розмістити", size=17, bold=True))

    # ── Ліва панель: розпорошено + переплетено ──
    lx = 40
    frags.append(text(lx + 150, 62, "Розпорошено й переплетено", size=14, bold=True, color=POS))
    methods = ["saveOrder()", "deleteUser()", "makePayment()"]
    my = 90
    for m in methods:
        # рамка методу
        frags.append(rect(lx, my, 300, 78, fill=BG, stroke=LINE, sw=1.5))
        frags.append(text(lx + 12, my + 20, m, size=12, bold=True, anchor="start", color=INK))
        # рядки: червоні — чужий концерн, сірі — своя справа
        frags.append(text(lx + 24, my + 40, "log(\"in\")   // логування", size=11, anchor="start", color=POS))
        frags.append(text(lx + 24, my + 56, "…своя робота…", size=11, anchor="start", color=MUTED))
        frags.append(text(lx + 24, my + 72, "log(\"out\")  // логування", size=11, anchor="start", color=POS))
        my += 96

    # ── Права панель: зібрано в один зріз ──
    rx = 430
    frags.append(text(rx + 150, 62, "Зібрано в один зріз", size=14, bold=True, color=FIELD))
    my = 90
    for m in methods:
        frags.append(rect(rx, my, 300, 44, fill=BG, stroke=LINE, sw=1.5))
        frags.append(text(rx + 12, my + 20, m, size=12, bold=True, anchor="start", color=INK))
        frags.append(text(rx + 24, my + 37, "…лише своя робота…", size=11, anchor="start", color=MUTED))
        my += 62
    # один зріз-обгортка знизу
    by = my + 8
    b, bw, bh = textbox(rx + 150, by + 22, "один аспект: log(before) → метод → log(after)",
                        size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=2, color=FIELD)
    frags.append(b)
    # стрілки від зрізу до кожного методу
    for i in range(3):
        frags.append(line(rx + 150, by + 22 - bh/2, rx + 150, 90 + i*62 + 44,
                          color=FIELD, sw=1.2, dash="4,4"))

    render(os.path.join(IMG, 'scatter-vs-aspect.svg'), W, H, *frags)


def fig_crosscut_layers():
    """Горизонтальні шари застосунку + вертикальні концерни, що ріжуть усі шари наскрізь —
    ось звідки назва «наскрізний зріз»."""
    W, H = 720, 400
    frags = []
    frags.append(text(W/2, 30, "Чому «наскрізний»: концерн ріже всі шари", size=17, bold=True))

    # горизонтальні шари
    layers = ["Веб / контролери", "Служби / застосунок", "Домен / правила", "Сховище / БД"]
    lx, lw = 60, 420
    ly = 70
    lh = 58
    gap = 12
    for name in layers:
        frags.append(rect(lx, ly, lw, lh, fill=FILL, stroke=LINE, sw=1.5))
        frags.append(text(lx + 16, ly + lh/2 + 5, name, size=13, bold=True, anchor="start", color=INK))
        ly += lh + gap

    total_h = 4 * lh + 3 * gap
    top = 70
    bottom = top + total_h

    # вертикальні концерни — напівпрозорі смуги, що перетинають усі шари
    concerns = [("Логування", 300, POS), ("Транзакції", 380, NEG), ("Безпека", 460, FIELD)]
    for label, cx, col in concerns:
        frags.append('<rect x="%.1f" y="%.1f" width="34" height="%.1f" rx="6" fill="%s" '
                     'fill-opacity="0.14" stroke="%s" stroke-width="1.5"/>'
                     % (cx - 17, top - 6, total_h + 12, col, col))
    # підписи концернів — під смугами, з запасом, щоб не накладались
    ylab = bottom + 26
    for label, cx, col in concerns:
        frags.append(text(cx, ylab, label, size=12, bold=True, color=col))

    # підказка збоку
    b, bw, bh = textbox(lx + lw + 95, top + total_h/2 - 30,
                        "кожен шар мусив би\nсам робити те саме",
                        size=11, color=MUTED, fill=BG, stroke=MUTED, sw=1.2)
    frags.append(b)

    render(os.path.join(IMG, 'crosscut-layers.svg'), W, H, *frags)


def fig_aop_timeline():
    """Хронологія народження АОП: метаоб'єктні протоколи (1991) → стаття ECOOP 1997
    зі словником aspect/tangling/scattering → AspectJ 2001 (pointcut/advice) →
    розхід у каркаси (Spring AOP 2004). Вісь зверху, усі картки одним рядом під нею —
    без накладань."""
    W, H = 820, 340
    frags = []
    frags.append(text(W / 2, 32, "Народження аспектів: від метаоб'єктів до каркасів",
                      size=16, bold=True))

    # горизонтальна вісь часу — угорі, щоб усі картки лягли одним рядом нижче
    ax0, ax1 = 60, 740
    ay = 78
    frags.append(line(ax0, ay, ax1, ay, color=LINE, sw=2))
    frags.append(arrow(ax1 - 2, ay, ax1 + 18, ay, color=LINE, sw=2))

    # рівні центри карток із великими проміжками (крок 190 > ширини картки 176 → без накладань)
    xs = [110, 300, 490, 680]
    milestones = [
        (xs[0], "1991", "Метаоб'єктні протоколи",
         "Кічалес та ін.: мова,\nщо переналаштовує\nсаму себе", FIELD),
        (xs[1], "1997", "Стаття ECOOP",
         "aspect · cross-cut\ntangling · scattering\nweaving · join point", POS),
        (xs[2], "2001", "AspectJ",
         "аспекти як синтаксис\nJava: pointcut · advice", NEG),
        (xs[3], "2004", "Каркаси",
         "Spring proxy-AOP,\nдекоратори,\nmiddleware", MUTED),
    ]
    cw, ch = 176, 104
    card_top = ay + 46          # верх картки — з відступом від осі під рік і ніжку
    for x, year, head, body, col in milestones:
        # крапка на осі
        frags.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s" stroke="%s" '
                     'stroke-width="2"/>' % (x, ay, BG, col))
        frags.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (x, ay, col))
        # ніжка від осі до картки (не перетинає жодного напису — йде в проміжку)
        frags.append(line(x, ay + 8, x, card_top, color=col, sw=1, dash="3,3"))
        # рік — праворуч від ніжки, над карткою, щоб ніжка його не різала
        frags.append(text(x + 22, ay + 24, year, size=13, bold=True, color=col))
        # картка: заголовок жирний + тіло, фіксований розмір із запасом
        frags.append(fitbox(x - cw / 2, card_top, cw, ch, head + "\n" + body,
                            size=10.5, fill=BG, stroke=col, sw=1.5, color=INK))

    render(os.path.join(IMG, 'aop-timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_scatter_tangle()
    fig_crosscut_layers()
    fig_aop_timeline()
    print("figures written")
