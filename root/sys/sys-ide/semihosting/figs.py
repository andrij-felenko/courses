# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── call: один виклик семіхостингу — хто що робить ────────────────────────────
# Ідея: показати, що "виклик" — це halt ядра, читання r0/r1 хостом, виконання
# на ПК і повернення в r0. Ядро весь цей час стоїть — звідси й повільність.

def fig_call():
    W, H = 860, 440
    p = []
    # дві доріжки: прошивка (ліворуч) і хост (праворуч)
    lx, rx = 70, 560
    lw, rw = 230, 230
    top = 70
    p.append(text(lx + lw / 2, top - 14, "Прошивка (ядро ARM)", size=13, color=NEG, bold=True))
    p.append(text(rx + rw / 2, top - 14, "Хост (ПК) через зонд", size=13, color="#e67e22", bold=True))

    bh, vg = 46, 22
    # кроки прошивки
    L = [
        ("r0 = 0x04  (SYS_WRITE0)", "#eaf0fd"),
        ("r1 = &\"temp=25\\0\"", "#eaf0fd"),
        ("BKPT 0xAB  → ядро СТОЇТЬ", "#fdecea"),
    ]
    y = top
    lc = []
    for s, fill in L:
        p.append(fitbox(lx, y, lw, bh, s, size=11, fill=fill, stroke=NEG, sw=1.5, color=INK, bold=True))
        lc.append(y)
        y += bh + vg
    # ядро стоїть — пунктир під час обробки хостом
    halt_y0 = y
    p.append(line(lx + lw / 2, lc[2] + bh, lx + lw / 2, halt_y0 + 96, color=MUTED, sw=2.0, dash="3,5"))
    p.append(text(lx + lw / 2, halt_y0 + 54, "ядро завмерле", size=10, color=MUTED, italic=True))
    p.append(text(lx + lw / 2, halt_y0 + 72, "(такти йдуть марно)", size=9, color=MUTED, italic=True))
    # відновлення
    res_y = halt_y0 + 110
    p.append(fitbox(lx, res_y, lw, bh, "r0 = код результату\nядро біжить далі", size=11,
                    fill="#d5e8d4", stroke=FIELD, sw=1.5, color=INK, bold=True))

    # кроки хоста
    R = [
        ("зонд бачить halt", "#fff8e1"),
        ("читає r0 → яка операція;\nr1 → де аргументи", "#fff8e1"),
        ("виконує на ПК:\nдрукує рядок у консоль", "#fff8e1"),
        ("кладе результат у r0,\nзнімає halt", "#fff8e1"),
    ]
    y = top + bh + vg  # хост вступає після BKPT
    rc = []
    for s, fill in R:
        p.append(fitbox(rx, y, rw, bh, s, size=10, fill=fill, stroke="#e67e22", sw=1.5, color=INK))
        rc.append(y)
        y += bh + vg

    # стрілки прошивка → хост (BKPT будить хост) і хост → прошивка (resume)
    p.append(arrow(lx + lw + 2, lc[2] + bh / 2, rx - 2, rc[0] + bh / 2, color="#e67e22", sw=1.8))
    p.append(text((lx + lw + rx) / 2, lc[2] + bh / 2 - 8, "halt", size=9, color="#e67e22"))
    p.append(arrow(rx - 2, rc[3] + bh / 2, lx + lw + 2, res_y + bh / 2, color=FIELD, sw=1.8))
    p.append(text((lx + lw + rx) / 2, res_y + bh / 2 - 8, "resume", size=9, color=FIELD))

    render(os.path.join(OUT, "call.svg"), W, H, *p,
           title="Один виклик: BKPT 0xAB спиняє ядро, хост робить роботу, ядро біжить далі")


# ── enable: ланцюг увімкнення з обох боків ───────────────────────────────────
# Ідея: семіхостинг працює, лише коли ОБИДВА боки налаштовані — тулчейн (rdimon)
# і хост (monitor arm semihosting enable). Порядок на старті критичний.

def fig_enable():
    W, H = 820, 320
    p = []
    colw, gap = 250, 30
    x0 = 35
    top = 66
    # два стовпці: бік прошивки / бік хоста
    cols = [
        ("Бік прошивки (тулчейн)", NEG, "#eaf0fd", [
            "--specs=rdimon.specs",
            "-lc -lrdimon",
            "initialise_monitor_handles();",
            "printf() → SYS_WRITE0",
        ]),
        ("Бік хоста (OpenOCD/GDB)", "#e67e22", "#fff8e1", [
            "(gdb) monitor arm",
            "      semihosting enable",
            "ловить BKPT 0xAB,",
            "виконує операцію на ПК",
        ]),
    ]
    rh = 38
    x = x0
    for head, col, fill, rows in cols:
        p.append(rect(x, top, colw, 30, fill=col, stroke=col, sw=1.5, rx=6))
        p.append(text(x + colw / 2, top + 20, head, size=fit_font(head, colw - 12, 13, True),
                      color="#ffffff", bold=True))
        ry = top + 38
        for r in rows:
            p.append(fitbox(x, ry, colw, rh, r, size=11, fill=fill, stroke=col, sw=1.0, color=INK))
            ry += rh + 6
        x += colw + gap

    # центральна звʼязка: обидва боки мусять збігтися
    midx = x0 + colw + gap / 2
    p.append(text(midx, top + 100, "+", size=30, color=INK, bold=True))

    # попередження про порядок старту
    msg = "Порядок на старті: спершу 'enable' на хості, тоді initialise_monitor_handles() — інакше HardFault"
    box, bw, bh = textbox(W / 2, 280, msg, size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS, pad=12)
    p.append(box)

    render(os.path.join(OUT, "enable.svg"), W, H, *p,
           title="Семіхостинг вмикають з ДВОХ боків: тулчейн і хост")


# ── compare: коли семіхостинг, коли UART, коли RTT ───────────────────────────
# Ідея: три способи дістати текст із прошивки на стіл, за двома осями —
# чи спиняє ядро і чи потрібен зонд. Семіхостинг = найповільніший, але без UART.

def fig_compare():
    W, H = 980, 360
    p = []
    rows = [
        ("Семіхостинг", "BKPT 0xAB", "спиняє ядро\nна КОЖЕН виклик",
         "лише зонд\n(без UART-дроту)", "десятки мс\nна виклик", "#fdecea", POS),
        ("UART\n(Serial.print)", "буфер +\nпереривання", "ядро майже\nне чіпає",
         "дріт UART\n(або USB-CDC)", "десятки мкс\nна символ", "#d5e8d4", FIELD),
        ("RTT / ITM", "запис у\nбуфер RAM", "ядро майже\nне чіпає",
         "той самий зонд,\nфонове читання", "одиниці мкс\nна виклик", "#eaf0fd", NEG),
    ]
    # таблиця
    cols_x = [30, 210, 380, 560, 770]
    headw = [170, 160, 170, 200, 180]
    heads = ["Спосіб", "Механізм", "Вплив на ядро", "Що треба", "Швидкість"]
    top = 60
    hh = 34
    for i, h in enumerate(heads):
        p.append(rect(cols_x[i], top, headw[i], hh, fill=INK, stroke=INK, sw=1.0, rx=4))
        p.append(text(cols_x[i] + headw[i] / 2, top + 22, h,
                      size=fit_font(h, headw[i] - 8, 12, True), color="#ffffff", bold=True))
    rh = 72
    y = top + hh + 8
    for name, mech, core, need, speed, fill, col in rows:
        cells = [name, mech, core, need, speed]
        for i, c in enumerate(cells):
            bold = (i == 0)
            cc = col if i == 0 else INK
            p.append(fitbox(cols_x[i], y, headw[i], rh, c, size=11, fill=fill, stroke=col,
                            sw=1.2, color=cc, bold=bold))
        y += rh + 8

    render(os.path.join(OUT, "compare.svg"), W, H, *p,
           title="Текст із прошивки на стіл: семіхостинг проти UART і RTT")


if __name__ == "__main__":
    fig_call()
    fig_enable()
    fig_compare()
    print("OK: figures written to", OUT)
