# -*- coding: utf-8 -*-
"""Фігури до статті «Кільцевий генератор»
(book/electronics/digital/ring-oscillator).

Кут статті — сам генератор як явище: непарне кільце інверторів, що не має
стабільної точки й самозбуджується; його частота, роздвоєний характер
(та сама чутливість — вада для годинника, дар для датчика) і тремтіння як
джерело випадковості.

Фігури:
  loop.svg     — кільце інверторів без стабільної точки; хвиля перемикань біжить по колу
  waveform.svg — рівень одного вузла в часі: меандр; період T = 2·N·tpd (звідки множник 2)
  pvt.svg      — одна чутливість, два боки: частота пливе від процесу/напруги/температури
  jitter.svg   — тремтіння фронтів → відлік проти опори → випадкові біти (джерело ентропії)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальний символ: інвертор (трикутник вершиною вправо + кружок-інверсія) ──
def inv(cx, cy, w=34, h=30, color=INK):
    x0 = cx - w / 2
    top, bot = cy - h / 2, cy + h / 2
    tipx = cx + w / 2 - 6
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#ffffff" '
           'stroke="%s" stroke-width="1.8"/>' % (x0, top, x0, bot, tipx, cy, color)]
    out.append(circle(tipx + 4, cy, 4, fill="#ffffff", stroke=color, sw=1.8))
    nodes = {"in": (x0, cy), "out": (tipx + 8, cy)}
    return "".join(out), nodes


# ════════════════════════════════════════════════════════════════════════════
# 1. loop.svg — кільце інверторів: нема стабільної точки, хвиля біжить по колу
# ════════════════════════════════════════════════════════════════════════════
def fig_loop():
    W, H = 660, 400
    f = []
    f.append(text(W / 2, 30, "Непарне кільце інверторів не має стабільної точки", size=15, bold=True))
    f.append(text(W / 2, 50, "у якому б рівні не завмер вузол — петля його перевертає й виштовхує", size=11, color=MUTED))

    cx, cy, R = W / 2, 220, 118
    Ninv = 5
    # розташуємо 5 інверторів по колу
    ang0 = -math.pi / 2
    pos = []
    for k in range(Ninv):
        a = ang0 + k * 2 * math.pi / Ninv
        pos.append((cx + R * math.cos(a), cy + R * math.sin(a), a))

    # з'єднання по колу (дуги-хорди) — від out одного до in наступного
    for k in range(Ninv):
        x1, y1, a1 = pos[k]
        x2, y2, a2 = pos[(k + 1) % Ninv]
        # проста лінія-хорда з невеликим зсувом-стрілкою
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        col = FIELD if k < 3 else MUTED
        f.append(line(x1, y1, x2, y2, color=INK, sw=1.6))
    # інвертори поверх ліній
    for k, (x, y, a) in enumerate(pos):
        s, _ = inv(x, y, color=INK)
        f.append(s)

    # хвиля перемикань — три «гарячі» стрілки вздовж кола (напрям обходу)
    for k in range(3):
        x1, y1, _ = pos[k]
        x2, y2, _ = pos[(k + 1) % Ninv]
        # стрілка на 65% відрізка
        ax_, ay_ = x1 + (x2 - x1) * 0.72, y1 + (y2 - y1) * 0.72
        bx_, by_ = x1 + (x2 - x1) * 0.5, y1 + (y2 - y1) * 0.5
        f.append(arrow(bx_, by_, ax_, ay_, color=POS, sw=2.2))
    f.append(text(cx, cy, "хвиля біжить", size=11, color=POS, bold=True))
    f.append(text(cx, cy + 16, "по колу", size=11, color=POS, bold=True))

    # позначки рівнів на кількох вузлах — по черзі 1/0 (демонструє інверсію)
    labels = ["1", "0", "1", "0", "1"]
    for (x, y, a), lv in zip(pos, labels):
        # зсув мітки назовні від центра
        lx = x + 30 * math.cos(a)
        ly = y + 30 * math.sin(a) + 4
        col = POS if lv == "1" else NEG
        f.append(text(lx, ly, lv, size=13, color=col, bold=True))

    # підпис-висновок
    bb, _, _ = textbox(cx, 372,
                       "5 інверторів у колі: обійшовши кільце, рівень вертається ПРОТИЛЕЖНИМ —\n"
                       "суперечність, тож коло вічно перекидається. Це й є самозбудження.",
                       size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(bb)
    render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. waveform.svg — рівень одного вузла: меандр; період = два оббіги кільця
# ════════════════════════════════════════════════════════════════════════════
def fig_waveform():
    W, H = 680, 320
    f = []
    f.append(text(W / 2, 30, "Один період — це два оббіги кільця", size=15, bold=True))
    f.append(text(W / 2, 50, "фронт мусить двічі обійти N вентилів, щоб вузол вернувся в той самий рівень", size=11, color=MUTED))

    ax, ay = 70, 190          # початок осі часу, рівень «0»
    hi = ay - 70              # рівень «1»
    span = 520
    # меандр: два повні періоди
    x = ax
    lvl = hi
    seg = span / 8.0          # 4 переходи на період × 2 періоди = 8 піврівнів
    pts = [(ax, hi)]
    cur = hi
    xs = ax
    seq = [hi, ay, hi, ay, hi, ay, hi, ay]   # рівні на кожному відрізку
    path = ["M %.1f %.1f" % (ax, hi)]
    xx = ax
    prev = hi
    for i, lv in enumerate(seq):
        if lv != prev:
            path.append("L %.1f %.1f" % (xx, lv))     # вертикальний фронт
        path.append("L %.1f %.1f" % (xx + seg, lv))   # горизонтальна поличка
        xx += seg
        prev = lv
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(path), INK))

    # осі-пунктири рівнів
    f.append(line(ax - 6, hi, ax + span, hi, color=MUTED, sw=0.8, dash="3 4"))
    f.append(line(ax - 6, ay, ax + span, ay, color=MUTED, sw=0.8, dash="3 4"))
    f.append(text(ax - 12, hi + 4, "1", size=12, color=POS, bold=True, anchor="end"))
    f.append(text(ax - 12, ay + 4, "0", size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(ax - 40, (hi + ay) / 2, "рівень", size=11, color=MUTED, anchor="middle"))
    f.append(text(ax - 40, (hi + ay) / 2 + 15, "вузла", size=11, color=MUTED, anchor="middle"))

    # позначити один півперіод = один оббіг = N·tpd
    x0 = ax
    x1 = ax + 2 * seg
    x2 = ax + 4 * seg
    f.append(line(x0, hi - 22, x1, hi - 22, color=FIELD, sw=1.6))
    f.append(line(x0, hi - 26, x0, hi - 18, color=FIELD, sw=1.6))
    f.append(line(x1, hi - 26, x1, hi - 18, color=FIELD, sw=1.6))
    f.append(text((x0 + x1) / 2, hi - 28, "оббіг = N·tpd", size=11, color=FIELD, bold=True))

    f.append(line(x1, ay + 24, x2, ay + 24, color=POS, sw=1.6))
    f.append(line(x1, ay + 20, x1, ay + 28, color=POS, sw=1.6))
    f.append(line(x2, ay + 20, x2, ay + 28, color=POS, sw=1.6))
    f.append(text((x1 + x2) / 2, ay + 40, "ще оббіг = N·tpd", size=11, color=POS, bold=True))

    # повний період T
    f.append(line(x0, hi - 46, x2, hi - 46, color=INK, sw=1.8))
    f.append(arrow(x0 + 6, hi - 46, x0, hi - 46, color=INK, sw=1.8))
    f.append(arrow(x2 - 6, hi - 46, x2, hi - 46, color=INK, sw=1.8))
    f.append(text((x0 + x2) / 2, hi - 52, "період  T = 2·N·tpd", size=12, color=INK, bold=True))

    # вісь часу
    f.append(arrow(ax, ay + 60, ax + span, ay + 60, color=INK, sw=1.4))
    f.append(text(ax + span, ay + 74, "час", size=11, color=MUTED, anchor="end"))
    render(os.path.join(IMG, "waveform.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. pvt.svg — одна чутливість, два боки: частота пливе від P/V/T
# ════════════════════════════════════════════════════════════════════════════
def fig_pvt():
    W, H = 700, 372
    f = []
    f.append(text(W / 2, 30, "Та сама чутливість: вада для годинника — дар для датчика", size=15, bold=True))
    f.append(text(W / 2, 50, "швидкість вентиля залежить від температури й напруги, тож частота кільця пливе за ними", size=11, color=MUTED))

    # ── ліва панель: частота ↓ з температурою ──
    ax, ay = 80, 250
    aw, ah = 220, 150
    f.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.4))
    f.append(arrow(ax, ay, ax, ay - ah, color=INK, sw=1.4))
    f.append(text(ax + aw, ay + 18, "температура →", size=11, color=MUTED, anchor="end"))
    f.append(text(ax - 8, ay - ah, "частота", size=11, color=MUTED, anchor="end"))
    # спадна крива f(T)
    pts = []
    for i in range(0, 101, 4):
        t = i / 100.0
        val = 1.0 - 0.55 * t
        px = ax + 8 + t * (aw - 20)
        py = ay - 12 - val * (ah - 30)
        pts.append((px, py))
    f.append('<path d="M ' + " L ".join("%.1f %.1f" % p for p in pts) + '" fill="none" stroke="%s" stroke-width="2.6"/>' % NEG)
    f.append(text(ax + aw / 2 + 20, ay - ah + 6, "гарячіше → повільніше", size=11, color=NEG, bold=True))

    # ── права панель: частота ↑ з напругою ──
    bx, by = 400, 250
    bw, bh = 220, 150
    f.append(arrow(bx, by, bx + bw, by, color=INK, sw=1.4))
    f.append(arrow(bx, by, bx, by - bh, color=INK, sw=1.4))
    f.append(text(bx + bw, by + 18, "живлення →", size=11, color=MUTED, anchor="end"))
    f.append(text(bx - 8, by - bh, "частота", size=11, color=MUTED, anchor="end"))
    pts2 = []
    for i in range(0, 101, 4):
        t = i / 100.0
        val = 0.25 + 0.65 * t
        px = bx + 8 + t * (bw - 20)
        py = by - 12 - val * (bh - 30)
        pts2.append((px, py))
    f.append('<path d="M ' + " L ".join("%.1f %.1f" % p for p in pts2) + '" fill="none" stroke="%s" stroke-width="2.6"/>' % POS)
    f.append(text(bx + bw / 2 - 6, by - bh + 6, "вище живлення → швидше", size=11, color=POS, bold=True))

    # нижня рамка-висновок
    bb, _, _ = textbox(W / 2, 332,
                       "Для тактового джерела ця плавучість — біда (частота «дихає»).\n"
                       "Для вбудованого датчика — навпаки дар: чип сам себе міряє.",
                       size=11, color=INK, fill=FILL, stroke=MUTED)
    f.append(bb)
    render(os.path.join(IMG, "pvt.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. jitter.svg — тремтіння фронтів → відлік проти опори → випадкові біти
# ════════════════════════════════════════════════════════════════════════════
def fig_jitter():
    W, H = 680, 360
    f = []
    f.append(text(W / 2, 30, "Тремтіння фронтів — джерело чесної випадковості", size=15, bold=True))
    f.append(text(W / 2, 50, "тепловий шум зсуває кожен фронт трохи раніше/пізніше; вибірка ловить цей хаос", size=11, color=MUTED))

    # верхній сигнал — швидке кільце з розмитими (тремтливими) фронтами
    ax, ay = 70, 130
    span = 480
    hi = ay - 34
    seg = span / 12.0
    # ідеальні фронти + випадковий зсув
    import random
    random.seed(7)
    path = ["M %.1f %.1f" % (ax, hi)]
    prev = hi
    xx = ax
    ghost = []           # де «мав би» бути фронт (пунктир)
    for i in range(12):
        lv = hi if i % 2 == 0 else ay
        jit = (random.random() - 0.5) * 10
        fx = xx + jit
        if lv != prev:
            path.append("L %.1f %.1f" % (fx, prev))
            path.append("L %.1f %.1f" % (fx, lv))
            ghost.append((xx, lv, prev))
        path.append("L %.1f %.1f" % (xx + seg, lv))
        prev = lv
        xx += seg
    # пунктирні «ідеальні» фронти
    for gx, lv, pr in ghost:
        f.append(line(gx, ay - 40, gx, ay + 6, color=MUTED, sw=0.7, dash="2 4"))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(path), INK))
    f.append(text(ax - 12, (hi + ay) / 2 + 4, "кільце", size=11, color=MUTED, anchor="end"))
    f.append(text(ax + span - 30, ay - 46, "фронти «гуляють» довкола сітки", size=11, color=POS, bold=True, anchor="end"))

    # моменти вибірки — вертикальні лінії від опорного (повільного) годинника
    sy0 = ay + 40
    sy1 = ay + 100
    samp_x = [ax + 1.6 * seg, ax + 4.9 * seg, ax + 8.1 * seg, ax + 11.0 * seg]
    bits = ["1", "0", "0", "1"]
    for sx, b in zip(samp_x, bits):
        f.append(line(sx, ay + 8, sx, sy1, color=FIELD, sw=1.2, dash="4 3"))
        col = POS if b == "1" else NEG
        f.append(circle(sx, sy1 + 18, 12, fill="#ffffff", stroke=col, sw=1.8))
        f.append(text(sx, sy1 + 22, b, size=13, color=col, bold=True))
    f.append(text(ax - 12, sy1 + 22, "біти", size=11, color=MUTED, anchor="end"))
    f.append(text(samp_x[0] - 4, ay + 30, "повільна опора тикає рівномірно й «фотографує» рівень", size=10.5, color=FIELD, anchor="start"))

    bb, _, _ = textbox(W / 2, 336,
                       "Куди саме впав фронт у мить вибірки — вирішує тепловий шум, а він непередбачуваний.\n"
                       "Тож ланцюжок бітів — справді випадковий, а не порахований формулою.",
                       size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(bb)
    render(os.path.join(IMG, "jitter.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop()
    fig_waveform()
    fig_pvt()
    fig_jitter()
    print("OK: 4 фігури у", IMG)
