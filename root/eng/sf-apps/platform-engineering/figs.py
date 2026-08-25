# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def vbar(cx, top, bottom, label, fill, stroke, color, w=40):
    """Вертикальна смуга з поверненим на 90° підписом усередині."""
    x = cx - w / 2
    h = bottom - top
    out = rect(x, top, w, h, fill=fill, stroke=stroke, sw=2, rx=6)
    midy = (top + bottom) / 2
    out += ('<g transform="rotate(90 %g %g)">' % (cx, midy)) + \
           text(cx, midy + 4, label, size=12.5, color=color, bold=True) + "</g>"
    return out


def fig_paved():
    """Ліворуч — кожна команда сама тягне свою криву стежку до інфраструктури
    (дублювання, різнобій). Праворуч — одна вимощена дорога, якою йдуть усі."""
    W, H = 780, 380
    frags = []
    frags.append(text(180, 40, "Без платформи", size=16, bold=True, color=POS))
    frags.append(text(590, 40, "Вимощена дорога", size=16, bold=True, color=FIELD))
    frags.append(line(390, 56, 390, H - 24, color=MUTED, sw=1, dash="5,5"))

    ys = [90, 155, 220, 285]

    # ── ліворуч: 4 команди, кожна своя крива стежка до спільної інфраструктури
    infra = vbar(350, 70, H - 30, "хмара · CI · секрети · логи",
                 "#f0e6f6", "#8e44ad", "#6b4a86", w=40)
    for i, ty in enumerate(ys):
        b, bw, bh = textbox(80, ty, "Команда %s" % "ABCD"[i], size=12, pad=8,
                            fill="#fdecea", stroke=POS)
        frags.append(b)
        midx = 205 + (i % 2) * 45
        midy = ty + (16 if i % 2 else -16)
        frags.append(line(80 + bw / 2, ty, midx, midy, color=POS, sw=1.6))
        frags.append(arrow(midx, midy, 330, ys[(i + 1) % 4] - 8, color=POS, sw=1.6))
    frags.append(infra)

    # ── праворуч: 4 команди → один вузол → рівна дорога → брама платформи
    gate = vbar(710, 70, H - 30, "Платформа: одна брама",
                "#e8f6ee", FIELD, "#1e7a45", w=44)
    knot_x, knot_y = 590, (ys[0] + ys[-1]) / 2
    for i, ty in enumerate(ys):
        b, bw, bh = textbox(485, ty, "Команда %s" % "ABCD"[i], size=12, pad=8,
                            fill="#e8f6ee", stroke=FIELD)
        frags.append(b)
        frags.append(line(485 + bw / 2, ty, knot_x, knot_y, color=FIELD, sw=1.6))
    frags.append(circle(knot_x, knot_y, 7, fill=FIELD, stroke=FIELD))
    frags.append(arrow(knot_x + 7, knot_y, 688, knot_y, color=FIELD, sw=2.6))
    frags.append(gate)

    render(os.path.join(IMG, 'paved-road.svg'), W, H, *frags)


def fig_product_loop():
    """Платформа як продукт: команди-споживачі, петля зворотного зв'язку,
    і те, ЩО платформа знімає — когнітивне навантаження продуктових команд."""
    W, H = 720, 430
    frags = []
    cx = W / 2

    # верх: продуктові команди (споживачі)
    b1, w1, h1 = textbox(cx, 70, "Продуктові команди\n(внутрішні «клієнти»)",
                         size=13, pad=12, fill="#eaf0fd", stroke=NEG, bold=False)
    frags.append(b1)

    # низ: платформна команда (постачальник)
    b2, w2, h2 = textbox(cx, 360, "Платформна команда\n(будує продукт-платформу)",
                         size=13, pad=12, fill="#e8f6ee", stroke=FIELD, bold=False)
    frags.append(b2)

    # ліва дуга вниз: «потреби, тертя, запити»
    frags.append(arrow(cx - w1 / 2 - 6, 90, cx - w2 / 2 - 6, 344, color=NEG, sw=2))
    lb = textbox(150, 215, "потреби й тертя\n(що болить)", size=12, pad=9,
                 fill=BG, stroke=NEG, color=NEG)
    frags.append(lb[0])

    # права дуга вгору: «самообслуга: golden path, шаблони, API»
    frags.append(arrow(cx + w2 / 2 + 6, 344, cx + w1 / 2 + 6, 90, color=FIELD, sw=2))
    rb = textbox(W - 150, 215, "самообслуга:\ngolden path · API\n· шаблони",
                 size=12, pad=9, fill=BG, stroke=FIELD, color="#1e7a45")
    frags.append(rb[0])

    # центр: що знімається — когнітивне навантаження
    core = fitbox(cx - 92, 200, 184, 60,
                  "знімає\nкогнітивне навантаження", size=12.5, pad=8,
                  fill="#fff7e6", stroke="#b9770e", color="#7a4e07", bold=True)
    frags.append(core)

    render(os.path.join(IMG, 'product-loop.svg'), W, H, *frags)


def fig_bottleneck():
    """Пастка: платформа з обов'язковим квитком через людину стає вузьким
    горлом. Праворуч — самообслуга масштабується без черги."""
    W, H = 740, 300
    frags = []
    frags.append(text(185, 40, "Платформа-вузьке горло", size=15, bold=True, color=POS))
    frags.append(text(560, 40, "Платформа-самообслуга", size=15, bold=True, color=FIELD))
    frags.append(line(375, 58, 375, H - 24, color=MUTED, sw=1, dash="5,5"))

    # ліворуч: 4 команди -> єдиний «квиток до людини» -> черга
    human_x, human_y = 300, 165
    hb, hw, hh = textbox(human_x, human_y, "ручний\nтікет", size=12, pad=10,
                         fill="#fdecea", stroke=POS, bold=True)
    for i in range(4):
        ty = 90 + i * 45
        b, bw, bh = textbox(85, ty, "К%d" % (i + 1), size=12, pad=9,
                            fill="#fdecea", stroke=POS)
        frags.append(b)
        frags.append(arrow(85 + bw / 2, ty, human_x - hw / 2, human_y - 30 + i * 20,
                          color=POS, sw=1.6))
    frags.append(hb)
    frags.append(text(human_x, human_y + hh / 2 + 22, "усі чекають у черзі",
                     size=12, color=POS))

    # праворуч: 4 команди -> кожна прямо в API (без людини)
    api_x = 640
    frags.append(vbar(api_x, 72, 258, "self-service API",
                     "#e8f6ee", FIELD, "#1e7a45", w=48))
    for i in range(4):
        ty = 90 + i * 45
        b, bw, bh = textbox(470, ty, "К%d" % (i + 1), size=12, pad=9,
                            fill="#e8f6ee", stroke=FIELD)
        frags.append(b)
        frags.append(arrow(470 + bw / 2, ty, api_x - 26, ty, color=FIELD, sw=1.8))

    render(os.path.join(IMG, 'bottleneck.svg'), W, H, *frags)


def fig_gate_check():
    """Сторож на в'їзді: над зібраною прошивкою — три гілки.
    Кличе platform_boot → на дорозі (пройшла). Має OFF_ROAD-позначку →
    свідомий з'їзд (пройшла + запис у лог). Ні того, ні того →
    мовчазний обхід (складання падає). Ключ: дві верхні гілки — OK."""
    W, H = 820, 470
    frags = []

    # ── джерело: зібрана прошивка (.elf), яку читає сторож ──
    src, sw_, sh_ = textbox(155, 235, ".elf\n(зібрана\nпрошивка)", size=13, pad=12,
                            fill="#eef1f6", stroke=MUTED, bold=True)
    frags.append(src)
    src_r = 155 + sw_ / 2

    # ── сторож-ромб (умовна перевірка) ──
    gx, gy = 355, 235
    gate = fitbox(gx - 78, gy - 34, 156, 68,
                  "сторож:\nчитає символи", size=13, pad=8,
                  fill="#fff7e6", stroke="#b9770e", color="#7a4e07", bold=True)
    frags.append(arrow(src_r, gy, gx - 82, gy, color=MUTED, sw=2))
    frags.append(gate)

    # рівні виходів трьох гілок
    y_top, y_mid, y_bot = 90, 235, 385
    branch_x = gx + 90            # звідки розходяться стрілки
    label_x = 545                 # де стоять підписи-умови гілок
    box_cx = 715                  # де стоять картки-вироки

    # гілка 1 (верх): кличе platform_boot → на дорозі, ПРОЙШЛА
    frags.append(arrow(branch_x, gy - 18, label_x - 96, y_top + 4, color=FIELD, sw=1.9))
    l1 = textbox(label_x, y_top, "кличе\nplatform_boot", size=11.5, pad=8,
                 fill=BG, stroke=FIELD, color="#1e7a45")
    frags.append(l1[0])
    v1, v1w, _ = textbox(box_cx, y_top, "OK — на дорозі", size=12.5, pad=11,
                         fill="#e8f6ee", stroke=FIELD, color="#1e7a45", bold=True)
    frags.append(arrow(label_x + l1[1] / 2, y_top, box_cx - v1w / 2 - 4, y_top,
                       color=FIELD, sw=1.9))
    frags.append(v1)

    # гілка 2 (середина): має OFF_ROAD → свідомий з'їзд, ПРОЙШЛА + лог
    frags.append(arrow(branch_x, gy, label_x - 118, y_mid, color=NEG, sw=1.9))
    l2 = textbox(label_x, y_mid, "має позначку\nOFF_ROAD", size=11.5, pad=8,
                 fill=BG, stroke=NEG, color=NEG)
    frags.append(l2[0])
    v2, v2w, _ = textbox(box_cx, y_mid, "OK — свідомий\nз'їзд (у лог)", size=12.5, pad=11,
                         fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    frags.append(arrow(label_x + l2[1] / 2, y_mid, box_cx - v2w / 2 - 4, y_mid,
                       color=NEG, sw=1.9))
    frags.append(v2)

    # гілка 3 (низ): ні того, ні того → мовчазний обхід, ПАДАЄ
    frags.append(arrow(branch_x, gy + 18, label_x - 96, y_bot - 4, color=POS, sw=1.9))
    l3 = textbox(label_x, y_bot, "ні того,\nні того", size=11.5, pad=8,
                 fill=BG, stroke=POS, color=POS)
    frags.append(l3[0])
    v3, v3w, _ = textbox(box_cx, y_bot, "FAIL — мовчазний\nобхід, збірка падає",
                         size=12.5, pad=11, fill="#fdecea", stroke=POS,
                         color=POS, bold=True)
    frags.append(arrow(label_x + l3[1] / 2, y_bot, box_cx - v3w / 2 - 4, y_bot,
                       color=POS, sw=1.9))
    frags.append(v3)

    render(os.path.join(IMG, 'gate-check.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_paved()
    fig_product_loop()
    fig_bottleneck()
    fig_gate_check()
    print("ok")
