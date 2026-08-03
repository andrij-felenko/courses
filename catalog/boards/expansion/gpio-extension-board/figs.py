# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «GPIO Extension Board для Raspberry Pi».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що робить плата: пасивний подовжувач гребінки на макетку ────────────────
def fig_what_it_does():
    W, H = 860, 360
    f = [text(W / 2, 30, "Плата нічого не змінює — лише виводить 40 пінів гребінки на макетку",
              size=15, bold=True)]

    # Pi ліворуч
    px, py, pw, ph = 40, 90, 150, 150
    f.append(rect(px, py, pw, ph, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(px + pw / 2, py + 34, "Raspberry Pi", size=12.5, bold=True))
    f.append(text(px + pw / 2, py + 56, "гребінка 40 пінів", size=10, color=MUTED))
    f.append(text(px + pw / 2, py + 74, "(2×20)", size=10, color=MUTED))
    # гребінка як два ряди крапок
    for r in range(2):
        for c in range(10):
            f.append(circle(px + 24 + c * 10.5, py + 100 + r * 14, 2.6, fill="#c9a227", stroke=MUTED, sw=0.8))

    # шлейф
    ax1 = px + pw
    ax2 = 330
    for k in range(6):
        yy = py + 46 + k * 18
        f.append(line(ax1, yy, ax2, yy, color="#b0b6be", sw=2.0))
    f.append(line(ax1, py + 40, ax2, py + 40, color=POS, sw=3.0))   # червона смуга = пін 1
    f.append(text((ax1 + ax2) / 2, py + 30, "40-жильний шлейф", size=10, color=INK, bold=True))
    f.append(text((ax1 + ax2) / 2, py + 168, "червона смуга = пін 1", size=9.5, color=POS, italic=True))

    # Плата-розширення (T) у центрі-праворуч
    bx, by, bw, bh = 340, 96, 170, 138
    f.append(rect(bx, by, bw, bh, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=10))
    f.append(text(bx + bw / 2, by + 30, "GPIO-плата", size=12.5, bold=True, color=FIELD))
    f.append(text(bx + bw / 2, by + 50, "(тільки надписані", size=9.5, color=MUTED))
    f.append(text(bx + bw / 2, by + 65, "штирі, без розуму)", size=9.5, color=MUTED))
    # надписані штирі рядком
    labs = ["3V3", "5V", "G", "2", "3", "4", "17", "27"]
    for i, lb in enumerate(labs):
        xx = bx + 20 + i * 18.5
        f.append(line(xx, by + 96, xx, by + 120, color=INK, sw=1.6))
        f.append(text(xx, by + 132, lb, size=9, color=INK))

    # макетка праворуч
    mx, my, mw, mh = 545, 96, 285, 200
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(mx + mw / 2, my + 24, "макетна плата", size=12, bold=True, color=MUTED))
    # центральна канавка + ряди дірок
    f.append(line(mx + 20, my + mh / 2, mx + mw - 20, my + mh / 2, color="#c7ccd2", sw=6))
    for row, yy in enumerate([my + 60, my + 78, my + 118, my + 136]):
        for c in range(16):
            f.append(circle(mx + 26 + c * 16, yy, 2.4, fill=BG, stroke="#c7ccd2", sw=0.8))
    f.append(text(mx + mw / 2, my + mh - 14, "плата сидить верхи на канавці", size=9.5, color=INK, italic=True))

    # стрілка плата→макетка
    f.append(arrow(bx + bw, by + bh / 2, mx, my + mh / 2 - 4, color=INK, sw=2.0))

    b, _, _ = textbox(W / 2, 344,
                      "жодного стабілізатора, жодного буфера — рівні й напруги на штирях ті самі, що на гребінці Pi",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "what-it-does.svg"), W, H, *f)


# ── 2. Пастка орієнтації шлейфа: пін 1 до піна 1, інакше дзеркало ──────────────
def fig_orientation():
    W, H = 820, 430
    f = [text(W / 2, 30, "Головна пастка: розверни шлейф — і вся розводка стане дзеркальною",
              size=15, bold=True)]

    def header(px, py, correct):
        # заголовок панелі
        cw = 330
        col = FIELD if correct else POS
        fill = "#eef6ef" if correct else "#fdecea"
        f.append(rect(px, py, cw, 300, fill=fill, stroke=col, sw=1.9, rx=10))
        title = "Правильно: пін 1 ↔ пін 1" if correct else "Помилка: шлейф розвернуто"
        f.append(text(px + cw / 2, py + 26, title, size=13, bold=True, color=col))

        # червона смуга шлейфа — угорі, у власній чистій смузі
        stripe_y = py + 52
        f.append(line(px + 24, stripe_y, px + cw - 24, stripe_y, color=POS, sw=3))
        side = "лівий край" if correct else "правий край"
        f.append(text(px + cw / 2, stripe_y - 8, "червона смуга шлейфа — " + side, size=9.5, color=POS, bold=True))

        # два ряди гребінки з номерами; пін 1 позначено
        gx = px + 66
        gy = py + 118
        step = 40
        f.append(text(px + cw / 2, gy - 30, "гребінка Pi (перші 5 пар)", size=9.5, color=MUTED))
        for c in range(5):
            xx = gx + c * step
            odd = 2 * c + 1     # верх — непарні 1..9
            even = 2 * c + 2    # низ — парні 2..10
            f.append(circle(xx, gy, 8.5, fill=BG, stroke=INK, sw=1.4))
            f.append(circle(xx, gy + 34, 8.5, fill=BG, stroke=INK, sw=1.4))
            f.append(text(xx + 15, gy + 4, str(odd), size=9, color=INK, anchor="start"))
            f.append(text(xx + 15, gy + 38, str(even), size=9, color=INK, anchor="start"))

        # де опиниться «пін 1 шлейфа» (короткий вертикальний зв'язок, поза номерами)
        mark_x = gx if correct else gx + 4 * step
        f.append(circle(mark_x, gy, 8.5, fill="#fdecea", stroke=POS, sw=2.6))
        f.append(line(mark_x, stripe_y + 4, mark_x, gy - 9, color=POS, sw=1.8, dash="4,3"))

        # підсумок панелі — унизу, з запасом
        if correct:
            f.append(text(px + cw / 2, py + 214, "смуга біля кута плати —", size=10.5, color=INK))
            f.append(text(px + cw / 2, py + 234, "3V3 там, де очікуєш;", size=10.5, color=INK))
            f.append(text(px + cw / 2, py + 258, "надписи на платі правдиві", size=10.5, color=FIELD, italic=True))
        else:
            f.append(text(px + cw / 2, py + 214, "5V там, де мав бути 3V3;", size=10.5, color=INK))
            f.append(text(px + cw / 2, py + 234, "живлення в давач навпаки —", size=10.5, color=INK))
            f.append(text(px + cw / 2, py + 258, "у кращому разі не працює", size=10.5, color=POS, italic=True))

    header(40, 60, True)
    header(450, 60, False)

    b, _, _ = textbox(W / 2, 410,
                      "надписи на платі правдиві ЛИШЕ при правильній орієнтації — інакше вони брешуть, а плата мовчки живить не туди",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "orientation-trap.svg"), W, H, *f)


# ── 3. Ланцюг: надпис на платі = число в коді = зсув лінії в libgpiod ──────────
def fig_label_to_code():
    W, H = 860, 380
    f = [text(W / 2, 30, "Надпис на штирі = число в коді = зсув лінії в ядрі — коли шлейф не розвернуто",
              size=14.5, bold=True)]

    # три ланки ланцюга, зліва направо, з широкими проміжками
    def link(cx, top, title, big, sub, col, fill):
        w, h = 220, 108
        f.append(rect(cx - w / 2, top, w, h, fill=fill, stroke=col, sw=1.9, rx=10))
        f.append(text(cx, top + 24, title, size=11, color=MUTED))
        f.append(text(cx, top + 62, big, size=26, color=col, bold=True))
        f.append(text(cx, top + 92, sub, size=10, color=INK))

    ty = 70
    link(150, ty, "надпис на платі", "GPIO17", "те, що читаєш очима", INK, "#eef6ef")
    link(430, ty, "число в коді", "17", "LED_LINE = 17", NEG, "#eaf0fd")
    link(710, ty, "зсув лінії чипа", "offset 17", "gpiochip0, лінія 17", FIELD, "#eef6ef")

    f.append(arrow(150 + 110, ty + 54, 430 - 110, ty + 54, color=INK, sw=2.2))
    f.append(arrow(430 + 110, ty + 54, 710 - 110, ty + 54, color=INK, sw=2.2))
    f.append(text(370, ty + 44, "=", size=22, color=MUTED, bold=True))
    f.append(text(650, ty + 44, "=", size=22, color=MUTED, bold=True))

    # знизу — фізичний штир окремо, збоку, як «інше число»
    f.append(rect(150 - 118, 218, 236, 66, fill="#fdecea", stroke=POS, sw=1.7, rx=9))
    f.append(text(150, 240, "фізичний штир на гребінці", size=10.5, color=POS, bold=True))
    f.append(text(150, 262, "№ 11 — ІНШЕ число, у код НЕ йде", size=10, color=INK))
    f.append(line(108, 178, 108, 218, color=POS, sw=1.6, dash="4,3"))
    f.append(text(150, 202, "не плутати з", size=9, color=POS, italic=True))

    # перевірка залізом
    f.append(rect(430 - 130, 218, 400, 66, fill=FILL, stroke=LINE, sw=1.6, rx=9))
    f.append(text(430 + 70, 240, "перевір ще до коду:", size=10.5, color=INK, bold=True))
    f.append(text(430 + 70, 262, "gpioset gpiochip0 17=1   →  штир GPIO17 має ожити",
                  size=10, color=INK))

    b, _, _ = textbox(W / 2, 344,
                      "розвернений шлейф РОЗРИВАЄ цей ланцюг: надпис лишається GPIO17, а фізично під ним уже інша лінія",
                      size=11, fill="#fdecea", stroke=POS, color=INK)
    f.append(b)
    render(os.path.join(IMG, "label-to-code.svg"), W, H, *f)


# ── 4. Карта чотирьох задач на макетці: які підписані точки бере кожна ─────────
def fig_four_tasks():
    W, H = 880, 430
    f = [text(W / 2, 30, "Чотири задачі — чотири набори підписаних точок, усі беруться з тієї самої плати",
              size=14, bold=True)]

    def card(x, y, title, col, rows, verify):
        w, h = 200, 250
        fill = "#f4f8f5"
        f.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.9, rx=10))
        f.append(text(x + w / 2, y + 26, title, size=12.5, bold=True, color=col))
        yy = y + 52
        for lab, note in rows:
            f.append(rect(x + 16, yy - 13, 52, 22, fill=BG, stroke=INK, sw=1.3, rx=4))
            f.append(text(x + 16 + 26, yy + 3, lab, size=10.5, color=INK, bold=True))
            f.append(text(x + 78, yy + 3, note, size=9.5, color=MUTED, anchor="start"))
            yy += 30
        # рядок перевірки — унизу картки, з запасом
        f.append(line(x + 14, y + h - 52, x + w - 14, y + h - 52, color="#d7dbe0", sw=1.2))
        f.append(text(x + w / 2, y + h - 34, "перевірка залізом:", size=9, color=MUTED))
        f.append(text(x + w / 2, y + h - 16, verify, size=9, color=FIELD, italic=True))

    card(30, 62, "1 · світлодіод", NEG,
         [("GPIO17", "вихід"), ("GND", "катод"), ("330 Ω", "послідовно")],
         "gpioset gpiochip0 17=1")
    card(248, 62, "2 · кнопка", FIELD,
         [("GPIO27", "вхід+pull-up"), ("GND", "друга нога"), ("—", "резистор не треба")],
         "gpioget gpiochip0 27")
    card(466, 62, "3 · I²C-давач", INK,
         [("3V3", "живлення"), ("GND", "земля"), ("SDA", "GPIO2"), ("SCL", "GPIO3")],
         "i2cdetect -y 1")
    card(684, 62, "4 · SPI", POS,
         [("MOSI", "GPIO10"), ("MISO", "GPIO9"), ("SCLK", "GPIO11"), ("CE0", "GPIO8")],
         "ls /dev/spidev0.0")

    b, _, _ = textbox(W / 2, 344,
                      "усі точки підписані на платі — беремо їх напряму, без відлічування штирів на голій гребінці",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    b2, _, _ = textbox(W / 2, 402,
                       "!  3V3 — так, 5V — ніколи: живлення давача й РІВЕНЬ його сигналу в бік Pi — два різні питання",
                       size=11, fill="#fdecea", stroke=POS, color=INK, bold=False)
    f.append(b2)
    render(os.path.join(IMG, "four-tasks.svg"), W, H, *f)


if __name__ == "__main__":
    fig_what_it_does()
    fig_orientation()
    fig_label_to_code()
    fig_four_tasks()
    print("OK: 4 figures ->", IMG)
