# -*- coding: utf-8 -*-
"""Фігури до теми «PWM-розширювач».
  pwm-expander.md          →  block.svg     (тонка шина → багато вільних ШІМ-каналів)
                              compare.svg   (лічильник проти порогів ON/OFF → імпульс + фаза)
                              stagger.svg   (однакова шпаруватість, рознесені фази → рівніший струм)
  hist-grayscale-driver.md →  lineage.svg   (родовід: спільна ідея ШІМ → важка й легка гілки)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: тонка шина всередині розгортається в 16 незалежних ШІМ ─────────
def fig_block():
    W, H = 760, 330
    f = []

    # МК зліва
    f.append(rect(40, 120, 150, 90, fill="#eef2f5", stroke=INK, sw=1.8))
    f.append(text(115, 155, "МК", size=14, color=INK, bold=True))
    f.append(text(115, 178, "2–3 таймери", size=10, color=MUTED))

    # тонка шина
    f.append(arrow(190, 165, 296, 165, color=INK, sw=2))
    f.append(text(243, 150, "I²C · 2 дроти", size=11, color=FIELD))

    # тіло розширювача
    ex, ey, ew, eh = 300, 55, 210, 235
    f.append(rect(ex, ey, ew, eh, fill=BG, stroke=INK, sw=1.9))
    f.append(text(ex + ew / 2, ey + 26, "PWM-розширювач", size=13, color=INK, bold=True))

    # усередині: генератор → дільник → спільний лічильник
    body, w, h = textbox(ex + ew / 2, ey + 62, "генератор 25 МГц", size=10.5, pad=7)
    f.append(body)
    f.append(arrow(ex + ew / 2, ey + 62 + h / 2, ex + ew / 2, ey + 96, color=INK, sw=1.6))
    body, w, h = textbox(ex + ew / 2, ey + 112, "дільник → спільна fшім", size=10.5, pad=7)
    f.append(body)
    f.append(arrow(ex + ew / 2, ey + 112 + h / 2, ex + ew / 2, ey + 146, color=INK, sw=1.6))
    body, w, h = textbox(ex + ew / 2, ey + 162, "лічильник 0…4095", size=10.5, pad=7)
    f.append(body)

    # 16 виходів віялом
    outs = [(85, "канал 0"), (140, "канал 1"), (200, "…"), (255, "канал 15")]
    for (y, lab) in outs:
        f.append(arrow(ex + ew, y, ex + ew + 90, y, color=INK, sw=1.8))
        f.append(text(ex + ew + 96, y + 4, lab, size=11, color=INK, anchor="start"))

    f.append(text(660, 300, "16 незалежних ШІМ", size=11, color=MUTED))

    render(os.path.join(IMG, "block.svg"), W, H, *f,
           title="Одна тонка шина — усередині 16 самостійних ШІМ")


# ── Фігура 2: як із лічильника й двох порогів народжується імпульс ──────────
def fig_compare():
    W, H = 760, 340
    f = []
    x0, x1 = 80, 700
    span = x1 - x0
    half = span / 2

    # верх: пилка лічильника 0..4095, два періоди
    yb, yt = 120, 45
    f.append(line(x0, yb, x0 + half, yt, color=INK, sw=2))
    f.append(line(x0 + half, yb, x0 + half, yt, color=MUTED, sw=1.2))
    f.append(line(x0 + half, yb, x1, yt, color=INK, sw=2))
    f.append(line(x0, yb, x1, yb, color=MUTED, sw=1.2))
    f.append(text(x0, 34, "лічильник біжить 0 → 4095, і знову", size=11, color=MUTED, anchor="start"))

    # пороги ON і OFF у першому періоді
    xon = x0 + span * 0.10
    xoff = x0 + span * 0.30
    f.append(line(xon, yt - 4, xon, 300, color=POS, sw=1.4, dash="4,3"))
    f.append(line(xoff, yt - 4, xoff, 300, color=NEG, sw=1.4, dash="4,3"))
    f.append(text(xon, 138, "ON", size=11, color=POS, bold=True))
    f.append(text(xoff, 138, "OFF", size=11, color=NEG, bold=True))

    # низ: вихідний імпульс (ВИСОКО між ON і OFF), два періоди
    yh, yl = 210, 262
    xon2, xoff2 = xon + half, xoff + half
    seq = [(x0, yl), (xon, yl), (xon, yh), (xoff, yh), (xoff, yl),
           (xon2, yl), (xon2, yh), (xoff2, yh), (xoff2, yl), (x1, yl)]
    for i in range(len(seq) - 1):
        (ax, ay), (bx, by) = seq[i], seq[i + 1]
        col = POS if (ay == yh or by == yh) and ax == bx and ay != by else INK
        # вертикальні фронти малюємо кольором, горизонтальні — чорним
        col = INK
        f.append(line(ax, ay, bx, by, color=col, sw=2))
    f.append(text(x0, 300, "вихід: ВИСОКО між ON і OFF — це шпаруватість", size=11, color=MUTED, anchor="start"))

    # підказка про фазу
    body, w, h = textbox(x0 + span * 0.72, 168, "зсунути пару ON/OFF → зсув фази",
                         size=11, pad=8, fill="#e7f5ea", stroke=FIELD, sw=1.4)
    f.append(body)

    render(os.path.join(IMG, "compare.svg"), W, H, *f,
           title="Порогова пара ON/OFF на спільному лічильнику робить імпульс")


# ── Фігура 3: однакова шпаруватість, рознесені фази → рівніший струм ────────
def fig_stagger():
    W, H = 760, 340
    f = []
    x0, x1 = 150, 700
    span = x1 - x0
    duty = 0.25 * span

    rows = [("канал 0", 0.00), ("канал 1", 0.25), ("канал 2", 0.50), ("канал 3", 0.75)]
    for i, (lab, ph) in enumerate(rows):
        y = 55 + i * 52
        yl, yh = y + 30, y
        f.append(text(30, y + 18, lab, size=11, color=INK, anchor="start"))
        start = x0 + ph * span
        end = start + duty
        if end <= x1:
            f.append(line(x0, yl, start, yl, color=INK, sw=2))
            f.append(line(start, yl, start, yh, color=POS, sw=2))
            f.append(line(start, yh, end, yh, color=POS, sw=2))
            f.append(line(end, yh, end, yl, color=INK, sw=2))
            f.append(line(end, yl, x1, yl, color=INK, sw=2))
        else:
            wrap = x0 + (end - x1)
            f.append(line(x0, yh, wrap, yh, color=POS, sw=2))          # хвіст із попереднього періоду
            f.append(line(wrap, yh, wrap, yl, color=INK, sw=2))
            f.append(line(wrap, yl, start, yl, color=INK, sw=2))
            f.append(line(start, yl, start, yh, color=POS, sw=2))
            f.append(line(start, yh, x1, yh, color=POS, sw=2))

    # рамка одного періоду
    f.append(line(x0, 40, x0, 268, color=MUTED, sw=1.2, dash="3,3"))
    f.append(line(x1, 40, x1, 268, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(x0, 285, "один період ШІМ", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(150, 300, 500, 30,
                    "Однакова шпаруватість, старти рознесені фазою — пік сумарного струму розмазується.",
                    size=11, pad=8))

    render(os.path.join(IMG, "stagger.svg"), W, H, *f,
           title="Рознести фази — і одночасних фронтів не буде")


# ── Фігура 4 (до hist-вставки): родовід драйверів яскравості ─────────────────
def fig_lineage():
    W, H = 760, 430
    f = []
    cx = W / 2

    # спільний корінь угорі
    root, rw, rh = textbox(cx, 52, "спільна ідея: ШІМ-яскравість\nза СТАЛОГО струму",
                           size=11.5, pad=10, fill="#e7f5ea", stroke=FIELD, sw=1.6, bold=True)
    f.append(root)

    # роздвоєння: дві похилі лінії до заголовків гілок
    lx, rx = 205, 555
    f.append(line(cx, 52 + rh / 2, lx, 118, color=INK, sw=1.6))
    f.append(line(cx, 52 + rh / 2, rx, 118, color=INK, sw=1.6))

    # заголовки гілок
    hl, hlw, hlh = textbox(lx, 138, "ВАЖКА · сталий струм\nTI · SPI-подібний",
                           size=10.5, pad=8, fill="#fdecea", stroke=POS, sw=1.5, bold=True)
    f.append(hl)
    hr, hrw, hrh = textbox(rx, 138, "ЛЕГКА · лише час\nNXP/Philips · I²C",
                           size=10.5, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.5, bold=True)
    f.append(hr)

    # вузли лівої гілки (важка): предок-димер угорі спільний, тоді TLC
    left = [
        (185, "PCA9531  (2002)", "8 біт · I²C · пращур-димер", MUTED),
        (255, "TLC5940  (2004)", "16× сталий струм · 4096 · dot·64 · ланцюг", POS),
    ]
    # вузли правої гілки (легка)
    right = [
        (185, "PCA9633  (NXP)", "4× · 8 біт · Fm+ · свій ШІМ", NEG),
        (255, "PCA9685  (~2008)", "16× · 4096 · I²C · ключі (без струму)", NEG),
    ]

    def node(xc, yc, title, sub, col):
        w = max(text_width(title, 11, True), text_width(sub, 9)) + 22
        h = 40
        f.append(rect(xc - w / 2, yc - h / 2, w, h, fill=BG, stroke=col, sw=1.6))
        f.append(text(xc, yc - 4, title, size=11, color=INK, bold=True))
        f.append(text(xc, yc + 12, sub, size=9, color=MUTED))
        return w, h

    # з'єднання заголовок→вузол1→вузол2 у кожній гілці
    for (xc, items) in ((lx, left), (rx, right)):
        prev_y = 138 + hlh / 2
        for (yc, title, sub, col) in items:
            f.append(line(xc, prev_y, xc, yc - 20, color=MUTED, sw=1.3))
            node(xc, yc, title, sub, col)
            prev_y = yc + 20

    # горизонтальна стрілка «спадкоємність» усередині гілки (2002→2004 / →2008)
    f.append(text(lx, 300, "нарощування: струм + грейскейл + калібрування", size=9.5, color=MUTED))
    f.append(text(rx, 300, "нарощування: канали + розрядність + швидкість", size=9.5, color=MUTED))

    # нижній підсумок: хто відповідає за струм
    f.append(fitbox(70, 340, 300, 62,
                    "ВАЖКА гілка бере на себе СТРУМ:\nсама тримає й вирівнює діоди.",
                    size=11, pad=9, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(fitbox(390, 340, 300, 62,
                    "ЛЕГКА гілка бере на себе лише ЧАС:\nшпаруватість дешево, струм — ваш.",
                    size=11, pad=9, fill="#eaf0fd", stroke=NEG, sw=1.5))

    render(os.path.join(IMG, "lineage.svg"), W, H, *f,
           title="Один корінь — дві гілки: хто відповідає за струм")


if __name__ == "__main__":
    fig_block()
    fig_compare()
    fig_stagger()
    fig_lineage()
    print("figs: block.svg, compare.svg, stagger.svg, lineage.svg -> ./img/")
