# -*- coding: utf-8 -*-
"""Фігури до теми «eventfd і futex»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def lost_wakeup():
    W, H = 780, 440
    xa, xb = 205, 565
    body = ""
    b, _, _ = textbox(xa, 40, "Споживач", bold=True, min_w=170)
    body += b
    b, _, _ = textbox(xb, 40, "Виробник", bold=True, min_w=170)
    body += b
    body += line(xa, 68, xa, 410, color=MUTED, dash="5,5")
    body += line(xb, 68, xb, 410, color=MUTED, dash="5,5")

    b, _, _ = textbox(xa, 115, "перевіряє: даних нема")
    body += b
    b, _, _ = textbox(xb, 180, "кладе дані")
    body += b
    b, wb, _ = textbox(xb, 250, "будить того, хто спить")
    body += b

    body += arrow(xb - wb / 2 - 6, 262, xa + 100, 262, color=POS)
    body += text((xa + 100 + xb - wb / 2) / 2, 246, "а нікого ще нема", size=13, color=POS)

    b, _, _ = textbox(xa, 325, "аж тепер засинає")
    body += b
    b, _, _ = textbox(xa, 395, "спить, хоча дані вже є",
                      fill="#fdecea", stroke=POS, color=POS, bold=True)
    body += b
    render(os.path.join(OUT, 'lost-wakeup.svg'), W, H, body)


def futex_paths():
    W, H = 880, 440
    xl, xr = 235, 645
    body = ""
    b, _, _ = textbox(xl, 42, "Немає суперечки", bold=True, min_w=230)
    body += b
    b, _, _ = textbox(xr, 42, "Є суперечка", bold=True, min_w=230)
    body += b

    b, _, _ = textbox(xl, 120, "CAS 0 → 1 вдався")
    body += b
    body += arrow(xl, 146, xl, 176)
    b, _, _ = textbox(xl, 202, "замок узято, працюємо")
    body += b

    b, _, _ = textbox(xr, 120, "CAS 0 → 1 не вдався")
    body += b
    body += arrow(xr, 146, xr, 176)
    b, _, _ = textbox(xr, 202, "futex(&lock, FUTEX_WAIT, 2)")
    body += b

    body += line(20, 268, 860, 268, color=NEG, sw=2, dash="8,6")
    body += text(96, 260, "межа ядра", size=13, color=NEG, bold=True)

    body += arrow(xr, 228, xr, 316, color=NEG)

    b, _, _ = textbox(xl, 350, "ядро про цей замок\nнічого не знає",
                      color=MUTED, stroke=MUTED)
    body += b
    b, _, _ = textbox(xr, 350, "черга очікування в кошику\nхеш-таблиці за ключем адреси",
                      fill="#eaf0fd", stroke=NEG)
    body += b
    render(os.path.join(OUT, 'futex-paths.svg'), W, H, body)


def eventfd_join():
    W, H = 860, 400
    xs, xe, xr = 135, 435, 720
    body = ""
    b, _, _ = textbox(xs, 80, "сокет клієнта", min_w=200)
    body += b
    b, _, _ = textbox(xs, 150, "слухаючий сокет", min_w=200)
    body += b
    b, we, he = textbox(xs, 232, "eventfd\nлічильник = 3",
                        fill="#eafaf1", stroke=FIELD, bold=True, min_w=200)
    body += b

    body += rect(xe - 92, 60, 184, 210, fill="#f4f6f8")
    body += mtext(xe, 150, ["epoll_wait()", "одне очікування", "на всі джерела"], size=15)

    body += arrow(xs + 102, 80, xe - 96, 110)
    body += arrow(xs + 102, 150, xe - 96, 150)
    body += arrow(xs + 102, 232, xe - 96, 205)

    body += arrow(xe + 96, 165, xr - 118, 165)
    b, _, _ = textbox(xr, 165, "список готових\nджерел", min_w=230)
    body += b

    b, _, _ = textbox(xs, 345, "робочий потік:\nwrite(efd, 1)", stroke=FIELD)
    body += b
    body += arrow(xs, 315, xs, 232 + he / 2 + 6, color=FIELD)
    render(os.path.join(OUT, 'eventfd-join.svg'), W, H, body)


def mutex_states():
    W, H = 1140, 520
    cx = 580
    y1, y0, y2 = 90, 250, 410
    xl, xr = 262, 890
    ad, au = 540, 620          # смуги стрілок «униз» і «вгору»
    body = ""

    b, _, _ = textbox(cx, y1, "1 · взято, охочих нема", bold=True, min_w=300)
    body += b
    b, _, _ = textbox(cx, y0, "0 · вільно", bold=True, min_w=300,
                      fill="#eafaf1", stroke=FIELD, color=FIELD)
    body += b
    b, _, _ = textbox(cx, y2, "2 · взято, є ті, хто чекає", bold=True, min_w=300,
                      fill="#fdecea", stroke=POS, color=POS)
    body += b

    # 1 → 0 (відпуск без пробудження) і 0 → 1 (швидке взяття)
    body += arrow(ad, 113, ad, 227, color=FIELD)
    body += arrow(au, 227, au, 113, color=FIELD)
    b, _, _ = textbox(xl, 170, "unlock: обмін →0, дав 1",
                      min_w=280, stroke=FIELD, color=FIELD)
    body += b
    b, _, _ = textbox(xr, 170, "lock: CAS 0→1",
                      min_w=280, stroke=FIELD, color=FIELD)
    body += b

    # 0 → 2 (розбуджений бере) і 2 → 0 (відпуск із пробудженням)
    body += arrow(ad, 273, ad, 387, color=FIELD)
    body += arrow(au, 387, au, 273, color=POS)
    b, _, _ = textbox(xl, 330, "розбуджений бере: CAS 0→2",
                      min_w=280, stroke=FIELD, color=FIELD)
    body += b
    b, _, _ = textbox(xr, 330, "unlock: обмін дав 2 → FUTEX_WAKE",
                      min_w=280, stroke=POS, color=POS)
    body += b

    # 1 → 2 обхідним шляхом ліворуч
    body += line(430, y1, 100, y1, color=POS)
    body += line(100, y1, 100, y2, color=POS)
    body += arrow(100, y2, 426, y2, color=POS)
    b, _, _ = textbox(xl, 470, "другий охочий позначає слово:\nCAS 1→2, далі FUTEX_WAIT",
                      min_w=280, stroke=POS, color=POS)
    body += b

    b, _, _ = textbox(xr, 470, "червоним — переходи, після яких\nіде системний виклик",
                      min_w=280, stroke=MUTED, color=MUTED)
    body += b
    render(os.path.join(OUT, 'mutex-states.svg'), W, H, body)


lost_wakeup()
futex_paths()
eventfd_join()
mutex_states()
print("ok")
