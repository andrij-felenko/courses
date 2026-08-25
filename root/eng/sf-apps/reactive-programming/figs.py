# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: pull (тягну) проти push (штовхають) ───────────────────────────
def fig_pull_vs_push():
    W, H = 760, 340
    parts = []
    parts.append(text(W / 2, 28, "Хто керує моментом: споживач тягне чи джерело штовхає", size=16, bold=True))

    # ліва половина — PULL
    parts.append(text(190, 62, "PULL — я тягну", size=15, bold=True, color=NEG))
    b1, w1, h1 = textbox(190, 120, "мій код", size=13, min_w=150)
    parts.append(b1)
    b2, w2, h2 = textbox(190, 235, "джерело\n(база, файл, масив)", size=12, min_w=180)
    parts.append(b2)
    # стрілка запиту вниз, дані вгору
    parts.append(arrow(160, 148, 160, 205, color=NEG))
    parts.append(text(120, 180, "хочу", size=11, color=NEG, anchor="middle"))
    parts.append(arrow(220, 205, 220, 148, color=INK))
    parts.append(text(258, 180, "ось", size=11, color=INK, anchor="middle"))
    parts.append(text(190, 285, "момент обирає споживач:", size=11, color=MUTED))
    parts.append(text(190, 302, "коли готовий — питаю наступне", size=11, color=MUTED))

    # роздільник
    parts.append(line(W / 2, 50, W / 2, H - 20, color="#cccccc", sw=1, dash="5,5"))

    # права половина — PUSH
    parts.append(text(570, 62, "PUSH — мене штовхають", size=15, bold=True, color=POS))
    d1, dw1, dh1 = textbox(570, 120, "джерело\n(кліки, датчик, ціни)", size=12, min_w=180)
    parts.append(d1)
    d2, dw2, dh2 = textbox(570, 235, "мій код (реагує)", size=13, min_w=170)
    parts.append(d2)
    # три стрілки-порції штовхаються вниз
    for dx, lbl in ((530, "1"), (570, "2"), (610, "3")):
        parts.append(arrow(dx, 148, dx, 205, color=POS))
    parts.append(text(680, 178, "значення", size=11, color=POS, anchor="middle"))
    parts.append(text(680, 193, "коли з'явилось", size=11, color=POS, anchor="middle"))
    parts.append(text(570, 285, "момент обирає джерело:", size=11, color=MUTED))
    parts.append(text(570, 302, "з'явилось — тримай, реагуй", size=11, color=MUTED))

    render(os.path.join(IMG, "pull-vs-push.svg"), W, H, *parts)


# ── Фігура 2: мармурова діаграма — filter, потім map над потоком ─────────────
def fig_marbles():
    W, H = 780, 330
    parts = []
    parts.append(text(W / 2, 28, "Оператори перетворюють увесь потік, а не одне значення", size=16, bold=True))

    xL, xR = 150, 720          # початок і кінець осей часу
    rows_y = [90, 175, 260]

    # три осі часу
    for y in rows_y:
        parts.append(line(xL, y, xR + 10, y, color=INK, sw=1.6))
        parts.append(arrow(xR - 4, y, xR + 12, y, color=INK))

    # підписи ліворуч від осей
    parts.append(text(xL - 60, rows_y[0] + 5, "джерело", size=12, anchor="middle", color=MUTED))
    parts.append(text(xL - 60, rows_y[1] + 5, "filter(>2)", size=12, anchor="middle", color=NEG))
    parts.append(text(xL - 60, rows_y[2] + 5, "map(×10)", size=12, anchor="middle", color=POS))

    def marble(cx, cy, label, fill, stroke):
        return circle(cx, cy, 17, fill=fill, stroke=stroke, sw=2) + \
               text(cx, cy + 5, label, size=13, bold=True, color=stroke)

    # джерело: 1 3 2 5 у часі
    src = [(210, "1"), (330, "3"), (450, "2"), (600, "5")]
    for cx, v in src:
        parts.append(marble(cx, rows_y[0], v, "#eef1f4", INK))

    # filter(>2): лишаються 3 і 5 на тих самих моментах; 1 і 2 відсіяно (примарні)
    for cx, v in src:
        if int(v) > 2:
            parts.append(marble(cx, rows_y[1], v, "#eaf0fd", NEG))
        else:
            parts.append(circle(cx, rows_y[1], 17, fill="#ffffff", stroke="#cccccc", sw=1.4))
            parts.append(text(cx, rows_y[1] + 5, v, size=13, color="#cccccc"))
    # вертикальні тонкі зв'язки, щоб видно було збіг моментів
    for cx, v in src:
        parts.append(line(cx, rows_y[0] + 17, cx, rows_y[1] - 17, color="#dddddd", sw=1, dash="3,3"))

    # map(×10): 3→30, 5→50 на тих самих моментах
    for cx, v in src:
        if int(v) > 2:
            parts.append(marble(cx, rows_y[2], str(int(v) * 10), "#fdecea", POS))
            parts.append(line(cx, rows_y[1] + 17, cx, rows_y[2] - 17, color="#dddddd", sw=1, dash="3,3"))

    render(os.path.join(IMG, "marbles.svg"), W, H, *parts)


# ── Фігура 3: протитиск — швидке джерело, повільний споживач, сигнал попиту ──
def fig_backpressure():
    W, H = 760, 320
    parts = []
    parts.append(text(W / 2, 28, "Протитиск: споживач замовляє стільки, скільки подужає", size=16, bold=True))

    # джерело зліва, споживач справа
    src, sw_, sh = textbox(140, 150, "джерело\nшвидке", size=13, min_w=150, stroke=POS)
    parts.append(src)
    con, cw, ch = textbox(620, 150, "споживач\nповільний", size=13, min_w=150, stroke=NEG)
    parts.append(con)

    # верхня стрілка: попит "дай 3" тече ВІД споживача ДО джерела
    parts.append(arrow(560, 108, 220, 108, color=NEG, sw=2))
    parts.append(text(390, 96, "request(3) — попит: «дай 3»", size=12, color=NEG, bold=True))

    # нижня стрілка: рівно 3 значення течуть ВІД джерела ДО споживача
    parts.append(arrow(220, 192, 560, 192, color=POS, sw=2))
    for i, dx in enumerate((300, 390, 480)):
        parts.append(circle(dx, 192, 12, fill="#fdecea", stroke=POS, sw=1.8))
    parts.append(text(390, 232, "тече рівно 3 — не більше", size=12, color=POS, bold=True))

    # підпис-висновок унизу
    parts.append(text(W / 2, 285, "джерело не має права штовхнути четверте, поки споживач не попросить ще",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "backpressure.svg"), W, H, *parts)


# ── Фігура 4 (вставка hist): дві лінії сходяться в спільний контракт ─────────
def fig_two_lines_history():
    W, H = 900, 430
    parts = []
    parts.append(text(W / 2, 30, "Дві лінії, один контракт: як склали request(n)", size=17, bold=True))

    # спільна вісь років унизу
    axis_y = 372
    x0, x1 = 90, 830
    parts.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=1.4))
    years = [(2009, 150), (2013, 380), (2015, 560), (2017, 760)]
    for yr, xx in years:
        parts.append(line(xx, axis_y - 5, xx, axis_y + 5, color=MUTED, sw=1.4))
        parts.append(text(xx, axis_y + 22, str(yr), size=12, color=MUTED, bold=True))

    # ── верхня доріжка: Rx / ReactiveX ──
    ry = 105
    parts.append(text(x0 - 20, ry - 34, "Лінія Rx / ReactiveX", size=13, bold=True,
                      color=POS, anchor="start"))
    b, w, h = textbox(150, ry, "Rx.NET\nMicrosoft, 2009", size=12, min_w=150, stroke=POS)
    parts.append(b)
    b, w, h = textbox(365, ry, "RxJava\nNetflix, 2013", size=12, min_w=150, stroke=POS)
    parts.append(b)
    b, w, h = textbox(575, ry, "RxJS та інші\nмови", size=12, min_w=150, stroke=POS)
    parts.append(b)
    parts.append(arrow(226, ry, 289, ry, color=POS))
    parts.append(arrow(441, ry, 499, ry, color=POS))

    # ── нижня доріжка: Reactive Streams ──
    sy = 235
    parts.append(text(x0 - 20, sy + 44, "Лінія Reactive Streams", size=13, bold=True,
                      color=NEG, anchor="start"))
    b, w, h = textbox(380, sy, "ініціатива\nNetflix · Pivotal · Typesafe\nкінець 2013", size=12,
                      min_w=250, stroke=NEG)
    parts.append(b)
    b, w, h = textbox(645, sy, "v1.0.0\nAPI · специфікація · TCK\n30 квітня 2015", size=12,
                      min_w=250, stroke=NEG)
    parts.append(b)
    parts.append(arrow(507, sy, 517, sy, color=NEG))

    # ── точка сходження: спільний контракт request(n) → JDK 9 Flow ──
    cx, cy = 762, 170
    b, w, h = textbox(cx, cy, "спільний контракт\nrequest(n)", size=13, min_w=170,
                      stroke=FIELD, bold=True)
    parts.append(b)
    # від верхньої лінії (RxJS-блок) вниз у контракт
    parts.append(arrow(651, ry + 22, cx - 30, cy - h / 2, color=MUTED))
    # від нижньої лінії (1.0.0-блок) угору в контракт
    parts.append(arrow(700, sy - 26, cx - 20, cy + h / 2, color=MUTED))
    # контракт → JDK 9 Flow
    b2, w2, h2 = textbox(cx, 300, "JDK 9: Flow\nDoug Lea, JEP-266, 2017", size=12, min_w=170,
                         stroke=FIELD)
    parts.append(b2)
    parts.append(arrow(cx, cy + h / 2, cx, 300 - h2 / 2, color=FIELD, sw=2))

    render(os.path.join(IMG, "two-lines-history.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_pull_vs_push()
    fig_marbles()
    fig_backpressure()
    fig_two_lines_history()
    print("figures written to", IMG)
