# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чому вимір «плаває» — спільний рівень росте з кожною коміркою ──
def fig_common_mode():
    W, H = 760, 430
    parts = []

    # шкала потенціалів зліва (від землі знизу до верху пакета)
    x_rail = 150
    y_bot, y_top = 380, 90
    parts.append(line(x_rail, y_bot, x_rail, y_top, color=INK, sw=2))
    parts.append(text(x_rail, y_bot + 26, "GND (0 В)", size=13, color=NEG, anchor="middle"))

    # чотири комірки в стосі; вузли між ними — з ростучим потенціалом
    n = 4
    vcell = 3.7
    dy = (y_bot - y_top) / n
    for i in range(n):
        yb = y_bot - i * dy
        yt = y_bot - (i + 1) * dy
        cx = x_rail
        # комірка як прямокутник на «рейці»
        parts.append(rect(cx - 26, yt + 8, 52, yb - yt - 16, fill="#eef7f0", stroke=FIELD, sw=1.8))
        parts.append(text(cx, (yt + yb) / 2 + 5, "%.1f В" % vcell, size=12, color=INK))
        # вузол-точка виміру
        parts.append(circle(cx, yt, 4, fill=INK, stroke=INK))
        v_node = vcell * (i + 1)
        parts.append(text(cx + 40, yt + 4, "%.1f В" % v_node, size=12, color=MUTED, anchor="start"))

    # підпис нижнього вузла
    parts.append(circle(x_rail, y_bot, 4, fill=INK, stroke=INK))

    # права колонка: те, що чип має витягти — саме 3.7, попри рівень під ним
    x_meas = 470
    fb, fw, fh = textbox(x_meas + 120, 130,
                         "Верхня комірка:\nсама вона — 3.7 В,\nале «висить» на 11.1 В",
                         size=13, fill="#fff6ea", stroke=POS, color=INK)
    parts.append(fb)
    fb, fw, fh = textbox(x_meas + 120, 330,
                         "Нижня комірка:\nті самі 3.7 В,\nале майже на землі",
                         size=13, fill="#eef7f0", stroke=FIELD, color=INK)
    parts.append(fb)

    # стрілки від відповідних комірок до пояснень
    parts.append(arrow(x_rail + 30, y_top + dy / 2, x_meas + 20, 130, color=POS, sw=1.6))
    parts.append(arrow(x_rail + 30, y_bot - dy / 2, x_meas + 20, 330, color=FIELD, sw=1.6))

    # заголовок-ідея
    parts.append(text(W / 2, 40, "Спільний рівень (common-mode) росте з кожною коміркою",
                      size=15, bold=True))
    parts.append(text(W / 2, 60, "а виміряти треба різницю 3.7 В на кожній — однаково точно",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'common-mode.svg'), W, H, *parts)


# ── Фігура 2: блок-схема монітора комірок ───────────────────────────────────
def fig_block():
    W, H = 900, 470
    parts = []

    # ліворуч — стос комірок (входи виміру)
    x_stack = 70
    y0 = 100
    ch = 60
    labels = ["C4", "C3", "C2", "C1"]
    node_ys = []
    for i, lb in enumerate(labels):
        yt = y0 + i * ch
        parts.append(rect(x_stack, yt, 50, ch - 12, fill="#eef7f0", stroke=FIELD, sw=1.6))
        parts.append(text(x_stack + 25, yt + (ch - 12) / 2 + 5, lb, size=13, color=INK))
        node_ys.append(yt)
    node_ys.append(y0 + len(labels) * ch)  # нижній вузол
    # виводи входів у мультиплексор
    x_mux = 250
    for yt in node_ys:
        parts.append(line(x_stack + 50, yt, x_mux, yt, color=LINE, sw=1.3))

    # балансувальні ключі на кожній комірці (маленькі FET+R між вузлами)
    for i in range(len(labels)):
        ytop = node_ys[i]
        ybot = node_ys[i + 1]
        xb = x_stack + 90
        my = (ytop + ybot) / 2
        parts.append(line(x_stack + 50, ytop, xb, ytop, color=POS, sw=1.1))
        parts.append(line(x_stack + 50, ybot, xb, ybot, color=POS, sw=1.1))
        parts.append(rect(xb - 8, my - 9, 16, 18, fill="#fdecea", stroke=POS, sw=1.4, rx=3))
        parts.append(line(xb, ytop, xb, my - 9, color=POS, sw=1.1))
        parts.append(line(xb, my + 9, xb, ybot, color=POS, sw=1.1))
    parts.append(text(x_stack + 90, y0 - 16, "баланс-ключі", size=11, color=POS))

    # мультиплексор
    mux_y, mux_h = y0 - 6, len(labels) * ch + 6
    parts.append(fitbox(x_mux, mux_y, 70, mux_h, "MUX\n(вибір\nкомірки)",
                        size=12, fill=FILL, stroke=LINE))

    # зсув рівнів
    x_ls = x_mux + 95
    parts.append(fitbox(x_ls, mux_y + 30, 90, 80, "Зсув рівнів\n(до землі\nчипа)",
                        size=12, fill=FILL, stroke=LINE))
    parts.append(arrow(x_mux + 70, mux_y + mux_h / 2, x_ls, mux_y + 70, color=LINE, sw=1.6))

    # АЦП + опора
    x_adc = x_ls + 120
    parts.append(fitbox(x_adc, mux_y + 10, 110, 60, "16-біт\nΔΣ-АЦП",
                        size=13, fill="#eaf0fd", stroke=NEG, sw=1.8))
    parts.append(fitbox(x_adc, mux_y + 90, 110, 46, "Опорна\nнапруга",
                        size=12, fill=FILL, stroke=LINE))
    parts.append(arrow(x_ls + 90, mux_y + 70, x_adc, mux_y + 40, color=LINE, sw=1.6))
    parts.append(line(x_adc + 55, mux_y + 90, x_adc + 55, mux_y + 70, color=LINE, sw=1.3))

    # цифрове ядро + інтерфейс
    x_dig = x_adc + 130
    parts.append(fitbox(x_dig, mux_y + 20, 120, 90,
                        "Логіка,\nрегістри,\nінтерфейс до\nхоста",
                        size=12, fill=FILL, stroke=LINE))
    parts.append(arrow(x_adc + 110, mux_y + 40, x_dig, mux_y + 65, color=LINE, sw=1.6))

    # до хоста
    parts.append(arrow(x_dig + 120, mux_y + 65, x_dig + 175, mux_y + 65, color=INK, sw=1.8))
    fb, fw, fh = textbox(x_dig + 205, mux_y + 65, "Хост-МК\n(ізольовано)",
                         size=12, fill="#f2f2f2", stroke=INK)
    parts.append(fb)

    parts.append(text(W / 2, 40, "Що всередині монітора комірок", size=16, bold=True))
    parts.append(text(W / 2, 60,
                      "один точний АЦП + опора обходять усі комірки через мультиплексор; кожна має свій баланс-ключ",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'block.svg'), W, H, *parts)


# ── Фігура 3: каскад (daisy-chain) — багато AFE на один хост ─────────────────
def fig_daisy():
    W, H = 780, 430
    parts = []

    # три AFE один над одним, кожен зі своєю групою комірок; спільний рівень росте
    x_afe = 300
    afe_w, afe_h = 200, 90
    ys = [300, 190, 80]
    ranges = ["комірки 1–12\n(0…44 В)", "комірки 13–24\n(44…89 В)", "комірки 25–36\n(89…133 В)"]
    for i, (y, r) in enumerate(zip(ys, ranges)):
        parts.append(fitbox(x_afe, y, afe_w, afe_h, "AFE #%d\n%s" % (i + 1, r),
                            size=13, fill="#eef7f0", stroke=FIELD, sw=1.8))
        # зображення групи комірок ліворуч
        gx = x_afe - 110
        parts.append(rect(gx, y + 12, 80, afe_h - 24, fill="#eef7f0", stroke=FIELD, sw=1.4))
        parts.append(text(gx + 40, y + afe_h / 2 + 4, "≈12 комірок", size=11, color=INK))
        parts.append(line(gx + 80, y + afe_h / 2, x_afe, y + afe_h / 2, color=LINE, sw=1.4))

    # ізольовані ланки між AFE (вертикальний каскад)
    for i in range(len(ys) - 1):
        y_lo = ys[i]
        y_hi = ys[i + 1]
        xm = x_afe + afe_w / 2
        parts.append(line(xm, y_hi + afe_h, xm, y_lo, color=NEG, sw=2, dash="5,4"))
        parts.append(text(xm + 70, (y_hi + afe_h + y_lo) / 2 + 4,
                          "ізольована ланка", size=11, color=NEG, anchor="start"))

    # єдина ланка вниз до хоста
    y_bottom = ys[0] + afe_h
    xm = x_afe + afe_w / 2
    parts.append(line(xm, y_bottom, xm, y_bottom + 20, color=NEG, sw=2, dash="5,4"))
    parts.append(line(xm, y_bottom + 20, 140, y_bottom + 20, color=NEG, sw=2, dash="5,4"))
    fb, fw, fh = textbox(140, y_bottom + 20 - 22, "Хост-МК\n(на рівні землі)",
                         size=12, fill="#f2f2f2", stroke=INK)
    parts.append(fb)

    parts.append(text(W / 2, 36, "Каскад: кожен AFE стереже свою групу, усі — на один хост",
                      size=15, bold=True))
    parts.append(text(W / 2, 55,
                      "ізольовані ланки перетинають зростання потенціалу; хост лишається біля землі",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'daisy-chain.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_common_mode()
    fig_block()
    fig_daisy()
    print('figures written to', IMG)
