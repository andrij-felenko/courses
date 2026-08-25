# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «SW-520D — давач нахилу/вібрації».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

BALL = "#9aa0a6"   # металева кулька
BALLE = "#5f6368"


# ── 1. Будова: кулька в трубці замикає/розмикає два контакти залежно від нахилу ─
def fig_inside():
    W, H = 860, 500
    f = [text(W / 2, 30, "Усередині SW-520D: кулька в трубці замикає два контакти або скочується геть",
              size=15, bold=True)]

    # спільні розміри трубки
    tube_w, tube_h = 250, 74
    ball_r = 26

    def tube(cx, cy, tilt_deg, closed, caption):
        """Малює нахилену трубку з кулькою; contacts на 'нижньому' (золотому) кінці."""
        import math
        a = math.radians(tilt_deg)
        ca, sa = math.cos(a), math.sin(a)
        # локальні кути прямокутника трубки (центр у cx,cy)
        def rot(dx, dy):
            return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
        hw, hh = tube_w / 2, tube_h / 2
        p1 = rot(-hw, -hh); p2 = rot(hw, -hh); p3 = rot(hw, hh); p4 = rot(-hw, hh)
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                 'fill="#eef1f4" stroke="%s" stroke-width="1.8"/>'
                 % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], BALLE))
        # два контакти-штирі на ПРАВОМУ кінці (золотий, «trigger end»)
        c_top = rot(hw - 6, -hh + 8); c_bot = rot(hw - 6, hh - 8)
        base_top = rot(hw + 34, -hh + 8); base_bot = rot(hw + 34, hh - 8)
        f.append(line(c_top[0], c_top[1], base_top[0], base_top[1], color="#c8901f", sw=4))
        f.append(line(c_bot[0], c_bot[1], base_bot[0], base_bot[1], color="#c8901f", sw=4))
        # кулька: біля золотого кінця (ON) або скотилась до дальнього (OFF)
        if closed:
            bx, by = rot(hw - ball_r - 6, 0)
        else:
            bx, by = rot(-hw + ball_r + 6, 0)
        f.append(circle(bx, by, ball_r, fill=BALL, stroke=BALLE, sw=1.8))
        # блиск на кульці
        f.append(circle(bx - 7, by - 7, 5, fill="#d6d9dc", stroke="none", sw=0))
        # позначка стану на контактах
        st_x, st_y = rot(hw + 46, 0)
        if closed:
            f.append(text(st_x + 24, st_y - 6, "контакт", size=11, bold=True, color=FIELD, anchor="middle"))
            f.append(text(st_x + 24, st_y + 10, "ЗАМКНЕНО", size=11, bold=True, color=FIELD, anchor="middle"))
        else:
            f.append(text(st_x + 24, st_y - 6, "розрив", size=11, bold=True, color=POS, anchor="middle"))
            f.append(text(st_x + 24, st_y + 10, "РОЗІМКНЕНО", size=11, bold=True, color=POS, anchor="middle"))
        # підпис під трубкою
        f.append(text(cx, cy + 74, caption, size=11, bold=True))
        return (bx, by)

    # горизонтально (золотий кінець донизу трохи) → кулька біля контактів → ON
    tube(240, 140, 6, True, "золотий кінець нижче / рівно + струс → кулька на контактах → ON")
    # нахил до 25° «золотим догори» → кулька скочується геть → OFF
    tube(240, 350, -25, False, "нахил золотим кінцем ДОГОРИ (> ~15°) → кулька скотилась → OFF")

    # права колонка: легенда
    lx = 560
    f.append(rect(lx, 100, 270, 150, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(lx + 135, 126, "що бачить схема", size=12.5, bold=True))
    f.append(circle(lx + 30, 158, 12, fill=BALL, stroke=BALLE, sw=1.6))
    f.append(text(lx + 52, 162, "металева кулька всередині", size=11, anchor="start"))
    f.append(line(lx + 20, 190, lx + 42, 190, color="#c8901f", sw=4))
    f.append(text(lx + 52, 194, "два позолочені контакти", size=11, anchor="start"))
    f.append(text(lx + 20, 224, "ON = кулька перемкнула їх;", size=11, anchor="start", color=FIELD))
    f.append(text(lx + 20, 242, "OFF = скотилась, розрив", size=11, anchor="start", color=POS))

    b, _, _ = textbox(W / 2, 452,
                      "це просто механічний вимикач: пружних електронів немає, є лиш металева кулька й сила тяжіння.\n"
                      "нахил або поштовх зрушує кульку — контакт то з'являється, то зникає. напрямок несиметричний.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Брязкіт контакту: сира кулька дає рвану серію, поріг/дебаунс чистять її ──
def fig_bounce():
    W, H = 860, 470
    f = [text(W / 2, 28, "Струс дає БРЯЗКІТ: кулька дрижить — сирий сигнал рваний, його треба почистити",
              size=15, bold=True)]

    x0, x1 = 90, 800
    lo_v, hi_v = 0, 1

    def frame(y, lab1, lab2, col):
        f.append(line(x0, y, x1, y, color=MUTED, sw=1.0))            # рівень 0
        f.append(line(x0, y - 48, x1, y - 48, color=MUTED, sw=0.6, dash="3,3"))  # рівень 1
        f.append(mtext(x0 - 24, y - 20, [lab1, lab2], size=10.5, color=col, anchor="end", bold=True))
        f.append(text(x1 + 6, y + 4, "0", size=9, color=MUTED, anchor="start"))
        f.append(text(x1 + 6, y - 44, "1", size=9, color=MUTED, anchor="start"))

    # ── сирий сигнал: спокій, потім бурхливий брязкіт під час струсу ──
    yR = 150
    frame(yR, "сирий", "контакт", INK)
    hi = yR - 48
    seg = []
    # спокій до 210: стабільний 0 (розімкнено)
    seg.append((x0, yR)); seg.append((210, yR))
    # брязкіт: швидкі перескоки 0↔1 у зоні струсу (210..470)
    import random
    random.seed(7)
    xx = 210
    lvl = yR
    pts_bounce = []
    while xx < 470:
        step = random.choice([8, 10, 12, 14, 16])
        xx = min(470, xx + step)
        lvl = hi if lvl == yR else yR
        pts_bounce.append((xx, lvl))
    seg.extend(pts_bounce)
    # після струсу — знову спокій 0
    seg.append((470, yR)); seg.append((640, yR))
    # короткий вторинний струс
    seg.append((640, yR))
    xx = 640
    lvl = yR
    while xx < 720:
        xx = min(720, xx + random.choice([9, 11, 13]))
        lvl = hi if lvl == yR else yR
        seg.append((xx, lvl))
    seg.append((720, yR)); seg.append((x1, yR))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join("%.1f,%.1f" % p for p in seg), INK))
    f.append(text(340, yR - 60, "бурхливий брязкіт", size=10.5, bold=True, color=POS))
    f.append(text(680, yR - 60, "ще струс", size=10, color=POS))

    # ── очищений: одне рівне «є вібрація» на весь час брязкоту (після дебаунсу) ──
    yC = 330
    frame(yC, "після", "дебаунсу", FIELD)
    hic = yC - 48
    # два високі плато на час двох струсів
    def plateau(a, b):
        f.append(line(a, yC, a, hic, color=FIELD, sw=2.4))
        f.append(line(a, hic, b, hic, color=FIELD, sw=2.4))
        f.append(line(b, hic, b, yC, color=FIELD, sw=2.4))
    plateau(210, 490)
    plateau(640, 740)
    f.append(text(350, hic - 8, "один чистий імпульс «була вібрація»", size=10.5, bold=True, color=FIELD))
    f.append(text(690, hic - 8, "другий", size=10, color=FIELD))

    b, _, _ = textbox(W / 2, 428,
                      "кожне торкання кульки — це десятки мікроконтактів за мілісекунди (брязкіт). лічити їх напряму —\n"
                      "ловити сотні хибних «спрацювань». дебаунс: побачив перший фронт → тримай стан і не зважай на дрижання N мс.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "bounce.svg"), W, H, *f)


# ── 3. Підключення: підтяжка + вимикач на землю → GPIO (активний нуль) ─────────
def fig_wiring():
    W, H = 820, 470
    f = [text(W / 2, 28, "Підключення: підтяжка тримає «1», кулька замикає на GND → на піні «0»",
              size=15, bold=True)]

    # шина живлення зверху, земля знизу
    vcc_y, gnd_y = 90, 380
    f.append(line(120, vcc_y, 700, vcc_y, color=POS, sw=2.2))
    f.append(text(120, vcc_y - 10, "VCC (3.3 або 5 В)", size=11.5, bold=True, color=POS, anchor="start"))
    f.append(line(120, gnd_y, 700, gnd_y, color=INK, sw=2.2))
    f.append(text(120, gnd_y + 20, "GND", size=11.5, bold=True, color=INK, anchor="start"))

    # резистор підтяжки від VCC до вузла
    node_x = 300
    node_y = 235
    f.append(rect(node_x - 14, vcc_y + 14, 28, 66, fill="#fff6e6", stroke="#c8901f", sw=1.6, rx=4))
    f.append(text(node_x + 42, vcc_y + 40, "R підтяжки", size=10.5, bold=True, color="#8a6410", anchor="start"))
    f.append(text(node_x + 42, vcc_y + 56, "10 кОм", size=10, color=MUTED, anchor="start"))
    f.append(line(node_x, vcc_y + 80, node_x, node_y, color="#c8901f", sw=2))

    # вузол → GPIO (праворуч)
    f.append(circle(node_x, node_y, 4, fill=INK, stroke=INK, sw=1))
    f.append(line(node_x, node_y, 560, node_y, color=NEG, sw=2))

    # SW-520D від вузла до GND
    sw_top = node_y
    f.append(line(node_x, node_y, node_x, node_y + 26, color=INK, sw=2))
    # символ кулькового вимикача: трубка з кулькою
    f.append(rect(node_x - 30, node_y + 26, 60, 40, fill="#eef1f4", stroke=BALLE, sw=1.6, rx=8))
    f.append(circle(node_x - 12, node_y + 46, 11, fill=BALL, stroke=BALLE, sw=1.5))
    f.append(text(node_x + 70, node_y + 40, "SW-520D", size=11, bold=True, anchor="start"))
    f.append(text(node_x + 70, node_y + 56, "(кулька)", size=9.5, color=MUTED, anchor="start"))
    f.append(line(node_x, node_y + 66, node_x, gnd_y, color=INK, sw=2))

    # МК-піни праворуч
    mx, my, mw, mh = 560, 150, 170, 170
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 26, "мікроконтролер", size=12, bold=True))
    f.append(text(mx + mw / 2, my + 44, "(Arduino / ESP32)", size=9.5, color=MUTED))
    # пін GPIO
    f.append(rect(mx - 4, node_y - 11, 8, 22, fill="#fff", stroke=NEG, sw=1.5, rx=2))
    f.append(text(mx + 24, node_y - 16, "GPIO", size=10.5, bold=True, color=NEG, anchor="start"))
    f.append(text(mx + 24, node_y + 2, "вхід", size=9.5, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, 428,
                      "спокій: кулька розімкнена, підтяжка тягне пін до VCC → читаємо «1». струс/нахил: кулька замикає\n"
                      "пін на GND → «0». логіка ІНВЕРСНА (активний нуль). внутрішня INPUT_PULLUP МК замінює зовнішній R.",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Неблокувальний дебаунс за таймером: два вікна часу над одним сигналом ──
def fig_debounce_timer():
    W, H = 919, 470
    f = [text(W / 2, 28, "Неблокувальний дебаунс: перший фронт запускає вікно — дрижання всередині ігнорується",
              size=14.5, bold=True)]

    x0, x1 = 80, 800
    y = 190
    hi = y - 52
    # осі
    f.append(line(x0, y, x1, y, color=MUTED, sw=1.0))
    f.append(line(x0, hi, x1, hi, color=MUTED, sw=0.6, dash="3,3"))
    f.append(text(x0 - 14, y + 4, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(x0 - 14, hi + 4, "1", size=10, color=MUTED, anchor="end"))
    f.append(text(x1 + 8, y - 22, "пін (активний нуль)", size=10, color=INK, anchor="start"))

    # сирий сигнал: спокій 1, потім брязкіт до 0 (подія), потім спокій
    import random
    random.seed(11)
    seg = [(x0, hi), (200, hi)]
    xx = 200
    lvl = hi
    while xx < 360:
        xx = min(360, xx + random.choice([9, 12, 15]))
        lvl = y if lvl == hi else hi
        seg.append((xx, lvl))
    seg.append((360, y)); seg.append((470, y))       # утримується внизу (подія триває)
    # хвіст брязкоту на відпусканні
    xx = 470
    while xx < 560:
        xx = min(560, xx + random.choice([10, 13]))
        lvl = hi if lvl == y else y
        seg.append((xx, lvl))
    seg.append((560, hi)); seg.append((x1, hi))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
             % (" ".join("%.1f,%.1f" % p for p in seg), INK))

    # перший фронт — вертикальна відмітка
    fx = 200
    f.append(line(fx, hi - 22, fx, y + 22, color=POS, sw=1.6, dash="4,3"))
    f.append(text(fx, hi - 30, "перший фронт", size=10.5, bold=True, color=POS))
    f.append(text(fx, hi - 44, "t = 0: приймаємо подію", size=9.5, color=POS))

    # вікно дебаунсу: сіра смуга від першого фронту на DEBOUNCE_MS
    win = 240
    f.append(rect(fx, y + 26, win, 40, fill="#f0eef6", stroke="#8a6bd6", sw=1.4, rx=6))
    f.append(text(fx + win / 2, y + 51, "ВІКНО: ігноруємо пін ~40 мс", size=10.5, bold=True, color="#5b3ea8"))
    f.append(line(fx, y + 26, fx, y + 66, color="#8a6bd6", sw=1.2))
    f.append(line(fx + win, y + 26, fx + win, y + 66, color="#8a6bd6", sw=1.2))

    # програма продовжує крутитись — стрілки «loop не стоїть»
    for lx in (600, 660, 720):
        f.append(arrow(lx, y + 96, lx + 34, y + 96, color=FIELD, sw=1.8))
    f.append(text(660, y + 118, "loop() не блокується — код тим часом працює далі", size=10.5, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 430,
                      "delay() зупиняє ВСЮ програму — так не можна в реальному пристрої. натомість: запам'ятали millis()\n"
                      "першого фронту → приймаємо подію → доки (millis − t0) < 40 мс, пін НЕ читаємо. loop крутиться далі.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "debounce-timer.svg"), W, H, *f)


# ── 5. Опитування проти переривання: хто витрачає, хто спить ─────────────────
def fig_poll_vs_irq():
    W, H = 860, 430
    f = [text(W / 2, 28, "Опитування проти переривання: постійно перевіряти — чи спати й прокинутись від струсу",
              size=14.5, bold=True)]

    colw = 360
    lx, rx = 70, 470
    top = 70
    ch = 250

    # ── ліва панель: опитування (polling) ──
    f.append(rect(lx, top, colw, ch, fill="#fdf3f2", stroke=POS, sw=1.6, rx=12))
    f.append(text(lx + colw / 2, top + 28, "ОПИТУВАННЯ (polling)", size=13, bold=True, color=POS))
    f.append(text(lx + colw / 2, top + 48, "digitalRead у кожному оберті loop()", size=10.5, color=MUTED))
    # смуга завантаження МК — майже суцільна
    by = top + 78
    for i in range(18):
        cx = lx + 26 + i * 18
        f.append(rect(cx, by, 12, 30, fill=POS, stroke="none", sw=0, rx=2))
    f.append(text(lx + colw / 2, by + 58, "МК зайнятий ~весь час", size=11, bold=True, color=POS))
    f.append(text(lx + colw / 2, by + 78, "перевіряє пін мільйони разів на секунду,", size=10, color=INK))
    f.append(text(lx + colw / 2, by + 94, "хоча струс буває раз на хвилину.", size=10, color=INK))
    f.append(text(lx + colw / 2, by + 118, "простіше, але марнує струм — погано на батареї", size=10, bold=True, color=MUTED))

    # ── права панель: переривання (interrupt) ──
    f.append(rect(rx, top, colw, ch, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(rx + colw / 2, top + 28, "ПЕРЕРИВАННЯ (interrupt)", size=13, bold=True, color=FIELD))
    f.append(text(rx + colw / 2, top + 48, "attachInterrupt → апаратура сама будить МК", size=10.5, color=MUTED))
    # смуга — переважно порожня, лиш кілька сплесків у момент струсу
    by = top + 78
    for i in range(18):
        cx = rx + 26 + i * 18
        active = i in (7, 8, 14)
        col = FIELD if active else "#d7e8da"
        f.append(rect(cx, by, 12, 30, fill=col, stroke="none", sw=0, rx=2))
    # блискавка над сплеском
    f.append(text(rx + 26 + 7 * 18 + 6, by - 6, "⚡", size=15, anchor="middle"))
    f.append(text(rx + colw / 2, by + 58, "МК спить, поки кулька мовчить", size=11, bold=True, color=FIELD))
    f.append(text(rx + colw / 2, by + 78, "струс → апаратне переривання → МК", size=10, color=INK))
    f.append(text(rx + colw / 2, by + 94, "прокидається, робить справу, спить знову.", size=10, color=INK))
    f.append(text(rx + colw / 2, by + 118, "складніше (ISR, volatile), зате мала витрата", size=10, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 392,
                      "SW-520D просто смикає пін — байдуже, як його читати. опитування простіше для навчання; переривання\n"
                      "потрібне, коли МК має спати на батареї й прокидатися лише від струсу. код обох — у прошивці нижче.",
                      size=10.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "poll-vs-irq.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_bounce()
    fig_wiring()
    fig_debounce_timer()
    fig_poll_vs_irq()
    print("OK: 5 figures ->", IMG)
