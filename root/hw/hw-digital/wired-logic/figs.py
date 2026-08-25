# -*- coding: utf-8 -*-
"""Фігури до теми «Монтажна логіка».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Підпис фігури несе .md, тож великого заголовка всередині малюнка немає (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ZERO = NEG   # «0» / низький — холодний синій
ONE  = POS   # «1» / високий — гарячий червоний


# ── маленький символ виходу «лише вниз» (open-drain): N-ключ на лінію ────────
def sink(cx, cy, on, label):
    """Квадратик-ключ, що з'єднує лінію (зверху) із землею (знизу).
    on=True — замкнений (тягне вниз); on=False — розімкнений (відпустив)."""
    out = []
    box_c = ONE if on else MUTED
    out.append(rect(cx - 16, cy - 14, 32, 28, fill=BG, stroke=box_c, sw=2, rx=4))
    # «контакт» усередині: риска з'єднана (on) або з розривом (off)
    if on:
        out.append(line(cx, cy - 14, cx, cy + 14, color=ONE, sw=3))
    else:
        out.append(line(cx, cy - 14, cx, cy - 4, color=MUTED, sw=2.4))
        out.append(line(cx, cy + 4, cx, cy + 14, color=MUTED, sw=2.4))
        out.append(line(cx - 7, cy - 4, cx + 7, cy - 4, color=MUTED, sw=2.4))  # розрив
    out.append(text(cx, cy + 30, label, size=12, color=INK))
    out.append(text(cx, cy + 45, "тягне" if on else "відпустив",
                    size=11, color=(ONE if on else MUTED)))
    return "".join(out)


def gnd(cx, cy):
    return (line(cx, cy, cx, cy + 8, color=INK, sw=2) +
            line(cx - 9, cy + 8, cx + 9, cy + 8, color=INK, sw=2) +
            line(cx - 5, cy + 12, cx + 5, cy + 12, color=INK, sw=2) +
            line(cx - 2, cy + 16, cx + 2, cy + 16, color=INK, sw=2))


def rail_top(x1, x2, y, sym, color):
    """Горизонтальна шина рівня sym (\"0\"/\"1\") заданого кольору."""
    return (line(x1, y, x2, y, color=color, sw=3) +
            text(x2 + 22, y + 5, sym, size=18, color=color, bold=True))


# ═══════════════════════════════════════════════════════════════════════════
# 1. Сама ідея: дріт ЯК вентиль. Три open-drain входи на спільній лінії =
#    один вентиль «І», у якого немає корпусу — є лише дріт із підтяжкою.
# ═══════════════════════════════════════════════════════════════════════════
def fig_wire_is_gate():
    W, H = 720, 360
    f = []
    # підтяжка зверху ліворуч
    pux = 110
    f.append(text(pux, 56, "VDD", size=13, color=POS, bold=True))
    f.append(line(pux, 64, pux, 86, color=INK, sw=2))
    # резистор-підтяжка (зиґзаґ)
    zx, zy = pux, 86
    pts = "%d,%d " % (zx, zy)
    for i, dx in enumerate([7, -7, 7, -7, 7, -7, 0]):
        zy += 9
        pts += "%d,%d " % (zx + dx, zy)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, INK))
    f.append(text(pux - 30, 110, "Rp", size=12, color=MUTED, italic=True))
    busy = zy + 6
    # спільна шина
    busx1, busx2 = pux, 560
    f.append(line(pux, busy - 6, pux, busy, color=INK, sw=2))
    f.append(line(busx1, busy, busx2, busy, color=INK, sw=3))
    f.append(text((busx1 + busx2) / 2, busy - 12, "спільна лінія", size=12, color=MUTED))
    # три ключі вниз
    xs = [230, 340, 450]
    states = [False, True, False]   # середній тягне → лінія LOW
    for x, on in zip(xs, states):
        f.append(line(x, busy, x, busy + 26, color=INK, sw=2))
        f.append(sink(x, busy + 40, on, "вихід"))
        f.append(gnd(x, busy + 70))
    # результат на лінії
    res = "0" if any(states) else "1"
    rc = ZERO if res == "0" else ONE
    f.append(circle(busx2 + 22, busy, 13, fill=BG, stroke=rc, sw=2.5))
    f.append(text(busx2 + 22, busy + 5, res, size=16, color=rc, bold=True))
    f.append(text(busx2 + 22, busy + 34, "рівень\nлінії", size=10.5, color=MUTED))
    # права рамка: «це і є вентиль І»
    bx = 610
    body, bw, bh = textbox(bx, 150, "ДРІТ =\nвентиль «І»\nбез корпусу",
                           size=13, bold=True, fill="#eef6ff", stroke=NEG)
    f.append(body)
    f.append(mtext(bx, 218, ["лінія = 1,", "лише коли", "ВСІ відпустили"],
                   size=11, color=INK))
    render(os.path.join(IMG, "wire-is-gate.svg"), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# 2. Дуальність: ТЕ САМЕ залізо — «І» в активно-високій умовності,
#    «АБО» в активно-низькій. Дві колонки, посередині — той самий дріт.
# ═══════════════════════════════════════════════════════════════════════════
def fig_duality():
    W, H = 720, 380
    f = []
    midx = W / 2
    f.append(line(midx, 70, midx, H - 30, color=MUTED, sw=1, dash="5,5"))
    # ── ліва колонка: активно-високий → wired-AND ──
    lx = 175
    f.append(text(lx, 64, "сигнал = ВИСОКИЙ («1»)", size=13, color=POS, bold=True))
    body, bw, bh = textbox(lx, 110, "активно-високий", size=12, fill="#fdecea", stroke=POS)
    f.append(body)
    rows_a = [("усі відпустили (всі «1»)", "лінія = 1", ONE),
              ("хоч хто тягне («0»)", "лінія = 0", ZERO)]
    yy = 165
    for cond, res, c in rows_a:
        f.append(text(lx, yy, cond, size=11, color=INK))
        f.append(text(lx, yy + 18, res, size=12.5, color=c, bold=True))
        yy += 56
    body, bw, bh = textbox(lx, 320, "= монтажне «І»", size=15, bold=True,
                           fill="#eef6ff", stroke=NEG)
    f.append(body)
    # ── права колонка: активно-низький → wired-OR ──
    rx = W - 175
    f.append(text(rx, 64, "сигнал = НИЗЬКИЙ («0»)", size=13, color=NEG, bold=True))
    body, bw, bh = textbox(rx, 110, "активно-низький", size=12, fill="#eaf0fd", stroke=NEG)
    f.append(body)
    rows_o = [("хоч хто активний (тягне)", "лінія активна", ZERO),
              ("усі мовчать", "лінія пасивна", ONE)]
    yy = 165
    for cond, res, c in rows_o:
        f.append(text(rx, yy, cond, size=11, color=INK))
        f.append(text(rx, yy + 18, res, size=12.5, color=c, bold=True))
        yy += 56
    body, bw, bh = textbox(rx, 320, "= монтажне «АБО»", size=15, bold=True,
                           fill="#eafaf0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "duality.svg"), W, H, *f,
           title="Те саме залізо — дві назви")


# ═══════════════════════════════════════════════════════════════════════════
# 3. Застосування: збірна лінія переривань. N давачів, кожен смикає спільний
#    рядок IRQ униз; процесор бачить «комусь треба» одним входом.
# ═══════════════════════════════════════════════════════════════════════════
def fig_irq_collector():
    W, H = 720, 320
    f = []
    # підтяжка + шина IRQ
    busy = 110
    f.append(text(70, 60, "VDD", size=12, color=POS, bold=True))
    f.append(line(70, 68, 70, busy, color=INK, sw=2))
    f.append(text(92, 90, "Rp", size=11, color=MUTED, italic=True))
    busx1, busx2 = 70, 560
    f.append(line(busx1, busy, busx2, busy, color=INK, sw=3))
    f.append(text((busx1 + busx2) / 2, busy - 12, "спільна лінія IRQ  (активний нуль)",
                  size=12, color=MUTED))
    # три давачі вниз; один активний
    xs = [200, 320, 440]
    labels = ["давач A", "давач B", "давач C"]
    states = [False, True, False]
    for x, on, lab in zip(xs, states, labels):
        f.append(line(x, busy, x, busy + 24, color=INK, sw=2))
        f.append(sink(x, busy + 38, on, lab))
        f.append(gnd(x, busy + 68))
    # процесор праворуч читає лінію
    body, bw, bh = textbox(635, busy, "процесор:\nодин вхід", size=12, bold=True,
                           fill="#f4f6f8", stroke=LINE)
    f.append(body)
    f.append(line(busx2, busy, 635 - bw / 2, busy, color=ZERO, sw=3))
    f.append(text((busx2 + 635 - bw / 2) / 2, busy - 10, "0 = «комусь треба»",
                  size=11, color=ZERO, bold=True))
    # підсумок-рамка
    f.append(text(W / 2, H - 28,
                  "Будь-який смикає вниз → процесор будиться. Одна ніжка замість N.",
                  size=12, color=INK))
    render(os.path.join(IMG, "irq-collector.svg"), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# 4. (math-вставка) Дзеркало де Моргана: перекинь КОЖНУ клітинку таблиці «І»
#    (входи й вихід) на протилежний рівень — і дістанеш таблицю «АБО».
#    Це геометричне серце законів: заперечення міняє «І» ⇄ «АБО».
# ═══════════════════════════════════════════════════════════════════════════
def _bit(cx, cy, v):
    """Кружечок-біт: 1 — гарячий, 0 — холодний."""
    c = ONE if v else ZERO
    fill = "#fdecea" if v else "#eaf0fd"
    return (circle(cx, cy, 12, fill=fill, stroke=c, sw=2) +
            text(cx, cy + 5, str(v), size=14, color=c, bold=True))


def _ttable(ox, oy, rows, head, out_head, col_out):
    """Мала таблиця істинності на два входи.
    rows — список (a, b, y); head — (ім'я_a, ім'я_b); out_head — підпис виходу."""
    f = []
    cw = 46          # ширина стовпця
    rh = 34          # висота рядка
    xs = [ox, ox + cw, ox + cw * 2 + 14]   # a, b, y (розрив перед виходом)
    # шапка
    for x, h, c in zip(xs, [head[0], head[1], out_head],
                       [INK, INK, col_out]):
        f.append(text(x, oy, h, size=13, color=c, bold=True))
    # роздільна риска
    f.append(line(ox - 22, oy + 8, xs[2] + 22, oy + 8, color=MUTED, sw=1))
    # вертикальний розрив «входи | вихід»
    f.append(line((xs[1] + xs[2]) / 2, oy - 12, (xs[1] + xs[2]) / 2, oy + 8 + rh * len(rows),
                  color=MUTED, sw=1, dash="3,4"))
    for i, (a, b, y) in enumerate(rows):
        yy = oy + 22 + i * rh
        f.append(_bit(xs[0], yy, a))
        f.append(_bit(xs[1], yy, b))
        f.append(_bit(xs[2], yy, y))
    return "".join(f)


def fig_demorgan_mirror():
    W, H = 720, 380
    f = []
    # ── ліворуч: таблиця «І» (y = a AND b) ──
    and_rows = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)]
    lx = 120
    f.append(text(lx + 45, 60, "«І»:  y = a · b", size=15, color=NEG, bold=True))
    f.append(_ttable(lx, 92, and_rows, ("a", "b"), "y", NEG))
    body, bw, bh = textbox(lx + 45, 330,
                           "висока лише в\nодному рядку — «всі 1»",
                           size=11, fill="#eef6ff", stroke=NEG)
    f.append(body)

    # ── стрілка-дзеркало посередині ──
    mx = W / 2
    f.append(arrow(mx - 44, 150, mx + 44, 150, color=POS, sw=2.4))
    f.append(arrow(mx + 44, 200, mx - 44, 200, color=POS, sw=2.4))
    body, bw, bh = textbox(mx, 118, "перекинь\nкожен біт", size=12, bold=True,
                           fill="#fdecea", stroke=POS)
    f.append(body)
    f.append(mtext(mx, 236, ["0 ⇄ 1", "у входах", "І у виході"],
                   size=11.5, color=POS))

    # ── праворуч: та сама таблиця, кожен біт перевернуто → це «АБО» ──
    #    (0,0,0)→(1,1,1); (0,1,0)→(1,0,1); (1,0,0)→(0,1,1); (1,1,1)→(0,0,0)
    or_rows = [(1, 1, 1), (1, 0, 1), (0, 1, 1), (0, 0, 0)]
    rx = W - 210
    f.append(text(rx + 45, 60, "«АБО»:  y = a + b", size=15, color=FIELD, bold=True))
    f.append(_ttable(rx, 92, or_rows, ("a", "b"), "y", FIELD))
    body, bw, bh = textbox(rx + 45, 330,
                           "низька лише в\nодному рядку — «всі 0»",
                           size=11, fill="#eafaf0", stroke=FIELD)
    f.append(body)

    render(os.path.join(IMG, "demorgan-mirror.svg"), W, H, *f,
           title="Дзеркало де Моргана: «І» перевернуте порядково = «АБО»")


# ═══════════════════════════════════════════════════════════════════════════
# 5. (math-вставка) Той самий дріт, дві полярності. Заперечення = риска над
#    сигналом. Активно-високо читаємо a·b·c (усі 1); активно-низько — беремо
#    доповнення входів і виходу, і за де Морганом це стає a̅+b̅+c̅ («хоч хто»).
# ═══════════════════════════════════════════════════════════════════════════
def fig_bar_flip():
    W, H = 720, 300
    f = []
    midx = W / 2
    f.append(line(midx, 66, midx, H - 26, color=MUTED, sw=1, dash="5,5"))

    # ліва половина — активно-високий погляд
    lx = midx / 2 + 10
    f.append(text(lx, 58, "активно-високо", size=13, color=POS, bold=True))
    f.append(text(lx, 82, "«сигнал = 1»", size=11, color=MUTED))
    body, bw, bh = textbox(lx, 130, "L = a · b · c", size=18, bold=True,
                           fill="#fdecea", stroke=POS)
    f.append(body)
    f.append(mtext(lx, 188, ["лінія висока ⟺", "усі входи = 1", "(монтажне «І»)"],
                   size=11.5, color=INK))

    # права половина — активно-низький погляд (доповнення всього)
    rx = midx + midx / 2 - 10
    f.append(text(rx, 58, "активно-низько", size=13, color=NEG, bold=True))
    f.append(text(rx, 82, "«сигнал = 0», беремо L̅", size=11, color=MUTED))
    # риска над кожним символом через overline-tspan неможлива просто; беремо ¬
    body, bw, bh = textbox(rx, 130, "L̅ = a̅ + b̅ + c̅", size=18, bold=True,
                           fill="#eaf0fd", stroke=NEG)
    f.append(body)
    f.append(mtext(rx, 188, ["активна ⟺", "хоч один вхід тягне", "(монтажне «АБО»)"],
                   size=11.5, color=INK))

    # низ: підпис-закон
    f.append(text(midx, H - 34,
                  "заперечи все — і «·» стає «+»:  (a·b·c)̅  =  a̅ + b̅ + c̅   (де Морган)",
                  size=12.5, color=INK, bold=True))
    render(os.path.join(IMG, "bar-flip.svg"), W, H, *f,
           title="Один дріт, два погляди — заперечення міняє «·» на «+»")


if __name__ == "__main__":
    fig_wire_is_gate()
    fig_duality()
    fig_irq_collector()
    fig_demorgan_mirror()
    fig_bar_flip()
    print("OK: 5 фігур у", IMG)
