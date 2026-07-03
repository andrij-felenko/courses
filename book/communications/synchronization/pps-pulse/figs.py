# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: імпульс = фаза (коли), повідомлення = мітка (котра) ────────────
def fig_edge_vs_message():
    W, H = 760, 320
    parts = []
    parts.append(text(W/2, 26, "Дві половини часу: фронт каже КОЛИ, дані кажуть КОТРА секунда", size=16, bold=True))

    # вісь часу
    ax_y = 150
    x0, x1 = 60, 700
    parts.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=1.5))
    parts.append(text(x1+4, ax_y+4, "t", size=13, color=MUTED, anchor="start"))

    # три секундні межі — вузькі гострі імпульси
    ticks = [150, 370, 590]
    labels = ["12:00:00", "12:00:01", "12:00:02"]
    pw = 10          # ширина імпульсу
    ph = 60          # висота
    for i, tx in enumerate(ticks):
        # прямокутний імпульс (фронт угору)
        parts.append(line(tx, ax_y, tx, ax_y-ph, color=POS, sw=3))
        parts.append(line(tx, ax_y-ph, tx+pw, ax_y-ph, color=POS, sw=3))
        parts.append(line(tx+pw, ax_y-ph, tx+pw, ax_y, color=POS, sw=3))
        # позначка «фронт»
        parts.append(circle(tx, ax_y-ph, 4, fill=BG, stroke=POS, sw=2))
        # мітка UTC-секунди, що приїжджає ПОВІЛЬНИМ повідомленням
        b = fitbox(tx-52, ax_y+22, 104, 30, labels[i], size=13, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
        parts.append(b)
        # стрілка від повідомлення до фронту
        parts.append(line(tx, ax_y+22, tx, ax_y+8, color=NEG, sw=1.3, dash="3 3"))

    # підписи ролей
    b1, w1, h1 = textbox(150, ax_y-ph-34, "фронт: гострий, точний до наносекунд", size=12.5,
                         fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b1)
    b2, w2, h2 = textbox(370, ax_y+72, "мітка UTC: повільна, точна до цілої секунди", size=12.5,
                         fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(b2)

    # «одна секунда» між фронтами
    parts.append(line(ticks[0], ax_y-ph-8, ticks[1], ax_y-ph-8, color=MUTED, sw=1.2, dash="4 3"))
    parts.append(text((ticks[0]+ticks[1])/2, ax_y-ph-14, "рівно 1 с", size=12, color=MUTED))

    render(os.path.join(IMG, "edge-vs-message.svg"), W, H, *parts)


# ── Фігура 2: квантування — фронт «прилипає» до найближчого такту ───────────
def fig_quantization():
    W, H = 760, 340
    parts = []
    parts.append(text(W/2, 26, "Квантування: фронт лягає на найближчий такт свого кварцу", size=16, bold=True))

    ax_y = 150
    x0, x1 = 70, 690
    parts.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=1.4))

    # такти внутрішнього кварцу (сітка)
    step = 62
    n = 10
    tick_xs = [x0 + 10 + i*step for i in range(n)]
    for tx in tick_xs:
        parts.append(line(tx, ax_y-8, tx, ax_y+8, color=MUTED, sw=1.4))
    parts.append(text(x0+10, ax_y+26, "такти кварцу приймача (напр., 20 нс кожен)", size=12, color=MUTED, anchor="start"))

    # «істинний» момент UTC-секунди — між тактами
    true_x = tick_xs[5] + 26
    parts.append(line(true_x, ax_y-96, true_x, ax_y+14, color=FIELD, sw=2.4, dash="5 3"))
    tb, tw, th = textbox(true_x+2, ax_y-112, "істинна межа секунди", size=12.5,
                         fill=BG, stroke=FIELD, color=FIELD, bold=True)
    parts.append(tb)

    # фактичний фронт — прилипає до найближчого такту ЛІВОРУЧ
    snap_x = tick_xs[5]
    parts.append(line(snap_x, ax_y, snap_x, ax_y-70, color=POS, sw=3))
    parts.append(line(snap_x, ax_y-70, snap_x+9, ax_y-70, color=POS, sw=3))
    parts.append(line(snap_x+9, ax_y-70, snap_x+9, ax_y, color=POS, sw=3))
    parts.append(circle(snap_x, ax_y-70, 4, fill=BG, stroke=POS, sw=2))
    pb, pw, ph = textbox(snap_x-70, ax_y-92, "виданий фронт", size=12.5,
                         fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(pb)

    # «дірка» між істиною і фронтом = помилка квантування q
    parts.append(line(snap_x, ax_y+40, true_x, ax_y+40, color=INK, sw=1.6))
    parts.append(line(snap_x, ax_y+34, snap_x, ax_y+46, color=INK, sw=1.6))
    parts.append(line(true_x, ax_y+34, true_x, ax_y+46, color=INK, sw=1.6))
    qb, qw, qh = textbox((snap_x+true_x)/2, ax_y+66, "q — помилка квантування (її повідомляє UBX-TIM-TP)",
                         size=12, fill=FILL, stroke=LINE, color=INK)
    parts.append(qb)

    render(os.path.join(IMG, "quantization.svg"), W, H, *parts)


# ── Фігура 3: один PPS зшиває два давачі на спільну шкалу ────────────────────
def fig_common_timeline():
    W, H = 760, 340
    parts = []
    parts.append(text(W/2, 26, "Один фронт — спільний нуль для всіх давачів", size=16, bold=True))

    # спільна лінія часу з фронтом-нулем
    ax_y = 268
    x0, x1 = 70, 690
    parts.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=1.4))
    zero_x = 150
    parts.append(line(zero_x, ax_y-14, zero_x, ax_y+10, color=POS, sw=3))
    parts.append(circle(zero_x, ax_y-14, 4, fill=BG, stroke=POS, sw=2))
    zb, zw, zh = textbox(zero_x, ax_y+34, "фронт PPS = t0", size=12.5,
                         fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(zb)

    # два давачі, кожен зі своєю подією, вимірюємо Δt від фронта
    def sensor(cy, name, ev_x, dt_txt, col):
        b, bw, bh = textbox(x0+44, cy, name, size=13, fill=FILL, stroke=col, color=col, bold=True)
        parts.append(b)
        parts.append(line(x0+44+bw/2, cy, x1, cy, color=MUTED, sw=1.1))
        # подія
        parts.append(circle(ev_x, cy, 6, fill=BG, stroke=col, sw=2.4))
        parts.append(text(ev_x, cy-14, "подія", size=11.5, color=col))
        # вертикаль події вниз до спільної лінії
        parts.append(line(ev_x, cy+7, ev_x, ax_y-2, color=col, sw=1.2, dash="4 3"))
        # вимір Δt від нуля
        parts.append(line(zero_x, ax_y-40, ev_x, ax_y-40, color=col, sw=1.5))
        parts.append(text((zero_x+ev_x)/2, ax_y-46, dt_txt, size=12, color=col, bold=True))

    sensor(92,  "IMU (1 кГц)",        360, "Δt = 0.412 с", NEG)
    sensor(168, "камера (30 к/с)",    520, "Δt = 0.688 с", FIELD)

    # пояснення внизу праворуч
    eb = fitbox(430, 56, 250, 44,
                "кожна подія має спільний нуль → кадри можна злити без зсуву",
                size=12, fill="#f4f6f8", stroke=LINE, color=INK)
    parts.append(eb)

    render(os.path.join(IMG, "common-timeline.svg"), W, H, *parts)


# ── Фігура 4 (для hist-вставки): родовід секундного імпульсу ─────────────────
def fig_pps_lineage():
    W, H = 820, 360
    parts = []
    parts.append(text(W/2, 26, "Родовід секундного імпульсу: та сама ідея, дедалі дешевше", size=16, bold=True))

    # горизонтальна вісь-стрічка часу
    ax_y = 150
    x0, x1 = 60, 770
    parts.append(line(x0, ax_y, x1, ax_y, color=MUTED, sw=2))
    parts.append(text(x1+2, ax_y+4, "час", size=12, color=MUTED, anchor="start"))

    # віхи: (x, рік, підпис, що саме несе секунду, колір)
    miles = [
        (120, "1833", "часовий м'яч\n(Ґрінвіч)", "падіння кулі — межа полудня очима", FIELD),
        (270, "1852", "телеграфний\nсигнал часу", "секундні поштовхи дротом", NEG),
        (430, "1910", "радіосигнал\nчасу (Ейфель)", "гострі позначки секунд ефіром", NEG),
        (585, "1964", "цезієвий\nеталон", "фронт 1PPS із передньої панелі", POS),
        (730, "1980-ті", "GNSS-модуль", "вивід TIMEPULSE у кожного", POS),
    ]
    for mx, yr, name, carry, col in miles:
        # точка на осі + вертикальна риска-фронт (символ гострого імпульсу)
        parts.append(line(mx, ax_y, mx, ax_y-34, color=col, sw=3))
        parts.append(line(mx, ax_y-34, mx+7, ax_y-34, color=col, sw=3))
        parts.append(line(mx+7, ax_y-34, mx+7, ax_y, color=col, sw=3))
        parts.append(circle(mx, ax_y-34, 3.5, fill=BG, stroke=col, sw=1.8))
        # рік над віхою
        parts.append(text(mx, ax_y-44, yr, size=13, color=col, bold=True))
        # назва під віхою (рамка)
        nb, nw, nh = textbox(mx, ax_y+34, name, size=11.5, fill=BG, stroke=col, color=col, bold=True)
        parts.append(nb)

    # спільний підпис-стрічка внизу: що незмінне
    b = fitbox(90, 300, 640, 40,
               "Незмінне ядро: одна секундна межа — одним різким сигналом по власному шляху, окремо від «котра це секунда».",
               size=12.5, fill=FILL, stroke=LINE, color=INK)
    parts.append(b)

    render(os.path.join(IMG, "pps-lineage.svg"), W, H, *parts)


# ── Фігура (для proj-вставки): зшивати фронт із TIM-TP за номером ─────────────
def fig_pairing():
    W, H = 760, 360
    parts = []
    parts.append(text(W/2, 26, "Зшивати фронт із TIM-TP за номером, а не «за останнім»", size=16, bold=True))

    x0, x1 = 60, 700

    # Верхня доріжка: апаратні фронти (input capture) — гострі, вчасні
    y_edge = 100
    parts.append(line(x0, y_edge, x1, y_edge, color=MUTED, sw=1.4))
    lb, lw, lh = textbox(x0+96, y_edge-40, "фронти PPS (input capture)", size=12.5,
                         fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(lb)
    edges = [(150, "N"), (350, "N+1"), (550, "N+2")]
    ex = {}
    for tx, lab in edges:
        parts.append(line(tx, y_edge, tx, y_edge-24, color=POS, sw=3))
        parts.append(circle(tx, y_edge-24, 4, fill=BG, stroke=POS, sw=2))
        parts.append(text(tx, y_edge+18, "фронт "+lab, size=11.5, color=POS))
        ex[lab] = tx

    # Нижня доріжка: повідомлення TIM-TP приходять ПІЗНІШЕ за свій фронт
    y_msg = 252
    parts.append(line(x0, y_msg, x1, y_msg, color=MUTED, sw=1.4))
    mb, mw, mh = textbox(x0+96, y_msg+40, "TIM-TP по UART (з відставанням)", size=12.5,
                         fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(mb)
    # повідомлення «про N» доповзає аж після фронту N+1 — ось де пастка
    msgs = [(300, "про N"), (500, "про N+1")]
    mxx = {}
    for tx, lab in msgs:
        parts.append(rect(tx-34, y_msg-15, 68, 30, fill="#eaf0fd", stroke=NEG, sw=1.6))
        parts.append(text(tx, y_msg+4, lab, size=11, color=NEG, bold=True))
        mxx[lab] = tx

    # ПРАВИЛЬНО (зелене): «про N» → фронт N, «про N+1» → фронт N+1 (за номером)
    parts.append(line(mxx["про N"],   y_msg-15, ex["N"],   y_edge+8, color=FIELD, sw=2.0))
    parts.append(line(mxx["про N+1"], y_msg-15, ex["N+1"], y_edge+8, color=FIELD, sw=2.0))
    gb, gw, gh = textbox(150, (y_edge+y_msg)/2 - 4, "за номером —\nвірно", size=12,
                         fill=BG, stroke=FIELD, color=FIELD, bold=True)
    parts.append(gb)

    # ХИБНО (червоний пунктир): «за останнім» схопило б найсвіжіший фронт N+1
    parts.append(line(mxx["про N"], y_msg-15, ex["N+1"], y_edge+8, color=POS, sw=1.6, dash="4 3"))
    xb, xw, xh = textbox(560, (y_edge+y_msg)/2 - 4, "«за останнім» →\nзсув на 1 секунду", size=11.5,
                         fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(xb)

    render(os.path.join(IMG, "pairing.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_edge_vs_message()
    fig_quantization()
    fig_common_timeline()
    fig_pps_lineage()
    fig_pairing()
    print("ok")
