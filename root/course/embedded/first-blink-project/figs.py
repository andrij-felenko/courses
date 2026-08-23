# -*- coding: utf-8 -*-
"""Фігури до теми «Перший проєкт: світлодіод блимає»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_anatomy():
    """Часова діаграма блимання: рівень ніжки в часі + чотири кроки циклу."""
    W, H = 760, 320
    f = []
    f.append(text(W/2, 26, "Що робить цикл блимання", size=17, bold=True))

    # осі часу
    x0, x1 = 70, 700
    yhi, ylo = 90, 170       # рівні HIGH / LOW на графіку
    f.append(text(40, yhi + 5, "HIGH", size=11, color=MUTED, anchor="end"))
    f.append(text(40, ylo + 5, "LOW", size=11, color=MUTED, anchor="end"))
    f.append(line(x0, ylo + 12, x1, ylo + 12, color=MUTED, sw=1))
    f.append(text(x1, ylo + 28, "час →", size=11, color=MUTED, anchor="end"))

    # прямокутний сигнал: HIGH 200, LOW 200, ...
    seg = (x1 - x0) / 4.0
    pts = []
    lvl = yhi
    xx = x0
    pts.append((xx, lvl))
    for i in range(4):
        xx2 = xx + seg
        pts.append((xx2, lvl))          # горизонталь
        nlvl = ylo if lvl == yhi else yhi
        pts.append((xx2, nlvl))          # фронт
        lvl = nlvl
        xx = xx2
    for i in range(len(pts) - 1):
        x1p, y1p = pts[i]
        x2p, y2p = pts[i + 1]
        f.append(line(x1p, y1p, x2p, y2p, color=NEG, sw=2.5))

    # підписи двох інтервалів
    f.append(line(x0, yhi - 12, x0 + seg, yhi - 12, color=POS, sw=1))
    f.append(text(x0 + seg/2, yhi - 18, "delay(200) — світить", size=11, color=POS))
    f.append(line(x0 + seg, ylo + 24, x0 + 2*seg, ylo + 24, color=MUTED, sw=1))
    f.append(text(x0 + 1.5*seg, ylo + 40, "delay(200) — темно", size=11, color=MUTED))

    # чотири кроки циклу внизу
    steps = ["HIGH\n(увімкнути)", "чекати\n200 мс", "LOW\n(вимкнути)", "чекати\n200 мс"]
    cols = [FILL, "#eaf0fd", FILL, "#eaf0fd"]
    bw, bh = 140, 52
    cy = 258
    xs = [130, 300, 470, 640]
    for i, (s, col) in enumerate(zip(steps, cols)):
        f.append(fitbox(xs[i] - bw/2, cy - bh/2, bw, bh, s, size=12, fill=col))
        if i < 3:
            f.append(arrow(xs[i] + bw/2 + 4, cy, xs[i+1] - bw/2 - 4, cy))
    # петля назад
    f.append(line(xs[3], cy + bh/2, xs[3], cy + bh/2 + 22, color=LINE, sw=1.5))
    f.append(line(xs[3], cy + bh/2 + 22, xs[0], cy + bh/2 + 22, color=LINE, sw=1.5))
    f.append(arrow(xs[0], cy + bh/2 + 22, xs[0], cy + bh/2 + 4))
    f.append(text(W/2, cy + bh/2 + 38, "loop() повторює нескінченно", size=11, color=MUTED))

    render(os.path.join(IMG, 'anatomy.svg'), W, H, *f)


def fig_wiring():
    """Підключення: ніжка GPIO → резистор → анод LED → катод → GND."""
    W, H = 720, 260
    f = []
    f.append(text(W/2, 26, "Як під'єднати світлодіод до ніжки", size=17, bold=True))

    y = 140
    # блок чипа зліва
    f.append(rect(50, y - 45, 120, 90, fill=FILL))
    f.append(text(110, y - 18, "ESP32", size=14, bold=True))
    f.append(mtext(110, y + 6, "ніжка\nGPIO2", size=11, color=MUTED))
    px = 170                      # вихід ніжки
    f.append(circle(px, y, 4, fill=INK, stroke=INK))

    # дріт до резистора
    rx = 300
    f.append(line(px, y, rx - 30, y, color=INK, sw=2))
    # резистор (зигзаг)
    zz = []
    zx = rx - 30
    step = 12
    up = True
    zz.append((zx, y))
    for i in range(6):
        zx += step
        zz.append((zx, y - 10 if up else y + 10))
        up = not up
    zz.append((zx, y))
    for i in range(len(zz) - 1):
        f.append(line(zz[i][0], zz[i][1], zz[i+1][0], zz[i+1][1], color=INK, sw=2))
    f.append(text(rx + 6, y - 24, "R = 270 Ом", size=12, bold=True))
    f.append(text(rx + 6, y - 40, "обмежувач струму", size=10, color=MUTED))

    # дріт до LED (трикутник + риска = діод)
    lx = zz[-1][0] + 60
    f.append(line(zz[-1][0], y, lx - 18, y, color=INK, sw=2))
    # анод-трикутник вказує в бік катода (вправо)
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (lx - 18, y - 14, lx - 18, y + 14, lx, y, FIELD, INK))
    f.append(line(lx, y - 14, lx, y + 14, color=INK, sw=2.5))     # катодна риска
    # стрілки світла
    f.append(line(lx + 4, y - 16, lx + 16, y - 28, color=POS, sw=1.5))
    f.append(line(lx + 12, y - 16, lx + 24, y - 28, color=POS, sw=1.5))
    f.append(text(lx + 2, y + 32, "LED", size=12, bold=True))
    f.append(text(lx - 30, y + 32, "анод +", size=10, color=MUTED, anchor="end"))
    f.append(text(lx + 40, y + 32, "катод −", size=10, color=MUTED))

    # дріт до GND
    gx = lx + 90
    f.append(line(lx, y, gx, y, color=INK, sw=2))
    f.append(line(gx, y, gx, y + 30, color=INK, sw=2))
    # символ землі
    for i, wdt in enumerate((26, 16, 8)):
        yy = y + 30 + i * 6
        f.append(line(gx - wdt/2, yy, gx + wdt/2, yy, color=INK, sw=2))
    f.append(text(gx, y + 66, "GND", size=11, color=MUTED))

    f.append(text(W/2, H - 14,
                  "струм тече: ніжка HIGH → резистор → LED (анод→катод) → GND",
                  size=11, color=MUTED))
    render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


def fig_stack():
    """Ланцюг від рядка коду до світла: код → фреймворк → регістр → каскад → LED."""
    W, H = 720, 340
    f = []
    f.append(text(W/2, 26, "Від рядка коду до світла", size=17, bold=True))

    rows = [
        ("digitalWrite(2, HIGH)",  "ваш код: намір «ніжка 2 — увімкнути»",       FILL),
        ("бібліотека Arduino",     "знаходить регістр і біт за номером піна",     "#eaf0fd"),
        ("GPIO_OUT біт 2 = 1",     "запис числа у відому адресу пам'яті",          "#eafaf1"),
        ("push-pull каскад",       "приєднує ніжку до +3.3 В",                     FILL),
        ("струм крізь LED",        "світлодіод світиться",                         "#fdecea"),
    ]
    bw, bh = 520, 44
    x = (W - bw) / 2
    y = 56
    gap = 14
    for i, (main, sub, col) in enumerate(rows):
        yy = y + i * (bh + gap)
        f.append(rect(x, yy, bw, bh, fill=col))
        f.append(text(x + 16, yy + bh/2 - 2, main, size=14, bold=True, anchor="start"))
        f.append(text(x + 16, yy + bh/2 + 16, sub, size=11, color=MUTED, anchor="start"))
        if i < len(rows) - 1:
            f.append(arrow(W/2, yy + bh + 1, W/2, yy + bh + gap - 1))

    render(os.path.join(IMG, 'stack.svg'), W, H, *f)


def fig_debug():
    """Дерево діагностики: LED не блимає → де саме розірвано ланцюг."""
    W, H = 760, 360
    f = []
    f.append(text(W/2, 26, "LED не блимає: де шукати", size=17, bold=True))

    # корінь
    f.append(fitbox(W/2 - 130, 46, 260, 40, "Чи залилася прошивка?\n(esptool: «Hash verified»)", size=12, fill=FILL))

    # гілка НІ
    f.append(arrow(W/2 - 60, 86, 200, 120))
    f.append(text(150, 104, "ні", size=11, color=POS, bold=True))
    f.append(fitbox(60, 122, 280, 48,
                    "проблема заливання, не коду:\nпорт, режим завантаження, кабель",
                    size=11, fill="#fdecea"))

    # гілка ТАК
    f.append(arrow(W/2 + 60, 86, 560, 120))
    f.append(text(600, 104, "так", size=11, color=FIELD, bold=True))
    f.append(fitbox(430, 122, 280, 40, "Той самий пін у коді й у залізі?", size=12, fill=FILL))

    # від «той самий пін» — ні
    f.append(arrow(490, 162, 350, 200))
    f.append(text(410, 182, "ні", size=11, color=POS, bold=True))
    f.append(fitbox(180, 202, 300, 48,
                    "код пише в GPIO2, а LED на іншій ніжці —\nабо на платі взагалі немає LED",
                    size=11, fill="#fdecea"))

    # від «той самий пін» — так
    f.append(arrow(600, 162, 640, 200))
    f.append(text(630, 182, "так", size=11, color=FIELD, bold=True))
    f.append(fitbox(500, 202, 240, 40, "Полярність і резистор?", size=12, fill=FILL))

    # низ — типові дрібниці
    f.append(arrow(620, 242, 620, 276))
    f.append(fitbox(360, 278, 380, 56,
                    "перевернутий LED (катод/анод), забутий чи завеликий\n"
                    "резистор, кепський контакт на макетці, згорілий LED",
                    size=11, fill="#fdecea"))

    render(os.path.join(IMG, 'debug.svg'), W, H, *f)


def fig_nonblocking():
    """Дві стрічки часу: delay() замикає процесор vs патерн millis() лишає вільним."""
    W, H = 760, 340
    f = []
    f.append(text(W/2, 26, "Один оберт блимання: delay() vs millis()", size=17, bold=True))

    x0, x1 = 150, 720
    span = x1 - x0            # 400 мс на всю ширину
    mid = x0 + span / 2       # мітка перемикання на 200 мс

    def tmark(x, label):
        f.append(line(x, 52, x, 300, color=MUTED, sw=1, dash="4,4"))
        f.append(text(x, 46, label, size=10, color=MUTED))

    tmark(x0, "0 мс")
    tmark(mid, "200 мс: перемкнути")
    tmark(x1, "400 мс")

    # --- стрічка 1: delay() ---
    y1 = 96
    bh = 30
    f.append(text(x0 - 12, y1 + bh/2 + 4, "delay()", size=12, bold=True, color=POS, anchor="end"))
    # суцільні смуги — процесор замкнений
    f.append(rect(x0, y1, mid - x0, bh, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(rect(mid, y1, x1 - mid, bh, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text((x0 + mid) / 2, y1 + bh/2 + 4, "процесор СТОЇТЬ", size=10, color=POS))
    f.append(text((mid + x1) / 2, y1 + bh/2 + 4, "процесор СТОЇТЬ", size=10, color=POS))
    f.append(text(x0, y1 + bh + 18, "між перемиканнями нічого більше не встигає", size=10, color=MUTED, anchor="start"))

    # --- стрічка 2: millis() ---
    y2 = 190
    f.append(text(x0 - 12, y2 + bh/2 + 4, "millis()", size=12, bold=True, color=FIELD, anchor="end"))
    # тонка вільна стрічка
    f.append(rect(x0, y2, span, bh, fill="#eafaf1", stroke=FIELD, sw=1.5))
    f.append(text(mid, y2 + bh/2 + 4, "процесор ВІЛЬНИЙ — між справами зиркає на годинник", size=10, color=FIELD))
    # тички «поглядів на годинник» уздовж вільної стрічки
    gx = x0 + 20
    while gx < x1 - 10:
        f.append(line(gx, y2 + bh, gx, y2 + bh + 6, color=FIELD, sw=1))
        gx += 34
    # інші справи, що вміщаються у вільний час
    f.append(fitbox(x0 + 24, y2 + bh + 14, 150, 30, "опитати давач", size=10, fill=FILL))
    f.append(fitbox(mid + 24, y2 + bh + 14, 150, 30, "прочитати кнопку", size=10, fill=FILL))

    # спільний підпис-висновок
    f.append(text(W/2, H - 14,
                  "перемикання — в ті самі моменти; різниця в тому, що робить процесор МІЖ ними",
                  size=11, color=MUTED))

    render(os.path.join(IMG, 'nonblocking.svg'), W, H, *f)


if __name__ == '__main__':
    fig_anatomy()
    fig_wiring()
    fig_stack()
    fig_debug()
    fig_nonblocking()
    print("OK: 5 figs ->", IMG)
