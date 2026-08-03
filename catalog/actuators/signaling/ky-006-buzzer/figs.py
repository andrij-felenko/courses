# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-006 — пасивний зумер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині: пасивний зумер = гола п'єзопластина, керма немає ──────────────
def fig_inside():
    W, H = 940, 470
    f = [text(W / 2, 30, "Пасивний зумер: гола п'єзопластина без генератора — частоту задаєш ти",
              size=15, bold=True)]

    # ЛІВОРУЧ: активний (для контрасту) — має свій генератор
    ax, ay, aw, ah = 60, 78, 360, 300
    f.append(rect(ax, ay, aw, ah, fill="#f7f9fc", stroke=MUTED, sw=1.6, rx=14))
    f.append(text(ax + aw / 2, ay + 26, "Активний (KY-012) — для порівняння", size=12.5, bold=True, color=MUTED))
    # блок «генератор» + пластина
    gx, gy, gw, gh = ax + 46, ay + 70, 120, 66
    f.append(rect(gx, gy, gw, gh, fill=BG, stroke=INK, sw=1.6, rx=8))
    f.append(text(gx + gw / 2, gy + 26, "генератор", size=10.5, bold=True, color=INK))
    f.append(text(gx + gw / 2, gy + 44, "≈2 кГц усередині", size=9, color=MUTED))
    # п'єзо праворуч від генератора
    pcx = ax + aw - 96
    _piezo(f, pcx, ay + 103, INK)
    f.append(line(gx + gw, gy + gh / 2, pcx - 34, ay + 103, color=INK, sw=1.6))
    # вхід: постійна напруга
    f.append(arrow(ax + 12, gy + gh / 2, gx, gy + gh / 2, color=POS, sw=2.0))
    f.append(text(ax + 8, gy + gh / 2 - 10, "+5 В (постійна)", size=9.5, bold=True, color=POS, anchor="start"))
    b, _, _ = textbox(ax + aw / 2, ay + ah - 34,
                      "подав живлення → сам пищить одним тоном",
                      size=10, fill="#f1f3f5", stroke=MUTED)
    f.append(b)

    # ПРАВОРУЧ: пасивний (KY-006) — тільки пластина
    bx, by, bw, bh = 520, 78, 360, 300
    f.append(rect(bx, by, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=14))
    f.append(text(bx + bw / 2, by + 26, "Пасивний (KY-006) — оце наш", size=12.5, bold=True, color=FIELD))
    # тільки п'єзопластина по центру
    pcx2 = bx + bw / 2 + 40
    _piezo(f, pcx2, by + 130, FIELD)
    f.append(text(pcx2, by + 176, "п'єзопластина", size=9.5, color=MUTED))
    f.append(text(pcx2, by + 190, "(генератора немає)", size=9, color=MUTED))
    # вхід: прямокутні імпульси
    sq_x = bx + 24
    _square(f, sq_x, by + 118, 150, 34, FIELD)
    f.append(arrow(sq_x + 150, by + 130, pcx2 - 34, by + 130, color=FIELD, sw=2.0))
    f.append(text(sq_x, by + 96, "меандр від МК: скільки Гц подав — така й нота", size=9.5, bold=True, color=FIELD, anchor="start"))
    b2, _, _ = textbox(bx + bw / 2, by + bh - 34,
                       "подав постійні 5 В → тиша (пластина зігнулась і застигла)",
                       size=10, fill="#fdecea", stroke=POS)
    f.append(b2)

    render(os.path.join(IMG, "ky006-inside.svg"), W, H, *f)


def _piezo(f, cx, cy, col):
    """Символ п'єзопластини: латунний диск + керамічний шар зверху, два виводи."""
    # латунна основа (широкий тонкий диск) у розрізі — довгий еліпс-смуга
    f.append(rect(cx - 30, cy + 4, 60, 6, fill="#e8c07a", stroke=col, sw=1.4, rx=2))
    # керамічний шар (трохи вужчий) зверху
    f.append(rect(cx - 20, cy - 3, 40, 7, fill="#dfe6ee", stroke=col, sw=1.4, rx=2))
    # виводи
    f.append(line(cx - 24, cy + 10, cx - 24, cy + 26, color=col, sw=1.6))
    f.append(line(cx + 16, cy - 3, cx + 16, cy + 26, color=col, sw=1.6))
    f.append(circle(cx - 24, cy + 26, 2.6, fill=col, stroke=col, sw=1))
    f.append(circle(cx + 16, cy + 26, 2.6, fill=col, stroke=col, sw=1))


def _square(f, x, y, w, h, col):
    """Малює 2.5 періоди меандру в прямокутнику (x,y)-(x+w, y+h). y — верх смуги."""
    lo = y + h
    hi = y
    n = 5           # напівперіодів
    step = w / n
    px = x
    lvl = lo
    f.append(line(x, lo, x + w, lo, color="#e2e6ea", sw=0.8))  # базова лінія
    pts_x = x
    cur = lo
    f.append(line(x, cur, x, cur, color=col, sw=2.2))
    for i in range(n):
        nx = px + step
        # горизонталь
        f.append(line(px, cur, nx, cur, color=col, sw=2.2))
        # фронт (вертикаль), крім останнього
        if i < n - 1:
            nxt = hi if cur == lo else lo
            f.append(line(nx, cur, nx, nxt, color=col, sw=2.2))
            cur = nxt
        px = nx


# ── 2. Як народжується звук: меандр гне пластину, вона штовхає повітря ─────────────
def fig_sound():
    W, H = 940, 430
    f = [text(W / 2, 30, "Звук з нічого: кожен перепад напруги згинає диск, диск штовхає повітря",
              size=15, bold=True)]

    # три кадри-стани диска: спокій / напруга «+» (вигин угору) / напруга «0» (назад)
    def disc(cx, cy, bend, col, cap, sub):
        # опора-корпус
        f.append(rect(cx - 46, cy + 14, 92, 10, fill="#f1f3f5", stroke=MUTED, sw=1.4, rx=3))
        # диск як дуга (bend: 0 плаский, + угору, - вниз)
        d = bend
        path = "M {} {} Q {} {} {} {}".format(cx - 40, cy, cx, cy - d, cx + 40, cy)
        f.append('<path d="{}" fill="none" stroke="{}" stroke-width="3"/>'.format(path, col))
        # виводи
        f.append(line(cx - 40, cy, cx - 40, cy + 14, color=MUTED, sw=1.4))
        f.append(line(cx + 40, cy, cx + 40, cy + 14, color=MUTED, sw=1.4))
        f.append(text(cx, cy + 48, cap, size=11, bold=True, color=col))
        f.append(text(cx, cy + 65, sub, size=9, color=MUTED))

    y = 150
    disc(180, y, 0,  MUTED, "0 В — спокій", "диск плаский")
    disc(430, y, 26, POS,   "+5 В", "вигнувся вгору → штовхнув повітря")
    disc(680, y, 0,  INK,   "знову 0 В", "розпрямився → відсмоктав повітря")

    # стрілки-переходи
    f.append(arrow(255, y, 350, y, color=INK, sw=1.8))
    f.append(arrow(505, y, 600, y, color=INK, sw=1.8))
    f.append(text(302, y - 12, "фронт ↑", size=9, color=INK))
    f.append(text(552, y - 12, "фронт ↓", size=9, color=INK))

    # хвильки повітря над «+5В» кадром
    for k, r in enumerate((16, 26, 36)):
        f.append('<path d="M {} {} A {} {} 0 0 1 {} {}" fill="none" stroke="{}" stroke-width="1.4" opacity="{}"/>'
                 .format(430 - r, y - 30, r, r, 430 + r, y - 30, POS, 0.8 - k * 0.2))

    b, _, _ = textbox(W / 2, 340,
                      "Повторюй перепади 440 разів на секунду — повітря колихнеться 440 разів за секунду: чуєш ноту «ля».\n"
                      "Швидше перепади — вищий тон, повільніше — нижчий. Гучність — коло механічного резонансу пластини (≈2 кГц).",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky006-sound.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: KY-006 ↔ мікроконтролер ─────────────────────────────
def fig_wiring():
    W, H = 940, 470
    f = [text(W / 2, 28, "Підключення KY-006: два дроти працюють — сигнал і земля, середній не чіпаємо",
              size=15, bold=True)]

    # Модуль ліворуч
    mx, my, mw, mh = 80, 96, 260, 250
    f.append(rect(mx, my, mw, mh, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 30, "KY-006", size=16, bold=True, color=FIELD))
    f.append(text(mx + mw / 2, my + 50, "пасивний зумер", size=10, color=MUTED))
    # п'єзо-іконка в центрі
    _piezo(f, mx + mw / 2, my + 92, INK)

    SIG = NEG   # сигнальний дріт — синій, щоб відрізнявся від зеленого корпусу
    pads = [("S", SIG, my + 150), ("+", POS, my + 190), ("−", INK, my + 230)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=14, bold=True, color=col, anchor="end"))
    f.append(text(mx + mw - 18, my + 172, "(середній = +, тут зайвий)", size=9, color=MUTED, anchor="end"))

    # Плата праворуч
    bx, by, bw, bh = 620, 96, 240, 250
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 30, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("D8", SIG, my + 150, "будь-який ШІМ / tone-пін"),
            ("(не треба)", MUTED, my + 190, "S уже живить пластину"),
            ("GND", INK, my + 230, "земля")]
    for lab, col, py, sub in tgts:
        if lab != "(не треба)":
            f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    # два робочі дроти (S і −), середній лишаємо
    f.append(line(mx + mw + 6, my + 150, bx - 6, my + 150, color=SIG, sw=2.4))
    f.append(line(mx + mw + 6, my + 230, bx - 6, my + 230, color=INK, sw=2.4))
    # середній — обірваний пунктир у нікуди
    f.append(line(mx + mw + 6, my + 190, mx + mw + 60, my + 190, color=MUTED, sw=1.6, dash="4,4"))
    f.append(text(mx + mw + 66, my + 194, "×", size=14, bold=True, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 410,
                      "Пасивний зумер пищить від слабкого струму, тож S на невеликому корпусі можна вести прямо на пін МК.\n"
                      "Голосніше або від 5 В — між пін і зумер став транзистор-ключ (напр. NPN + резистор на базу).",
                      size=10.5, fill="#fdf6ec", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky006-wiring.svg"), W, H, *f)


# ── 4. Блокувальний delay проти неблокувального плеєра за millis ───────────────────
def fig_nonblocking():
    W, H = 940, 500
    f = [text(W / 2, 30, "Мелодія й loop() водночас: delay морозить усе, millis лишає цикл вільним",
              size=15, bold=True)]

    # спільна вісь часу
    t0, t1 = 150, 860          # ліва/права межа шкали часу
    span = t1 - t0
    ticks = [("нота 1", 0.0), ("нота 2", 0.28), ("нота 3", 0.56), ("пауза", 0.84), ("", 1.0)]
    beats = [0.0, 0.28, 0.56, 0.84, 1.0]

    def timeline_y(y, label, col):
        f.append(text(t0 - 14, y + 4, label, size=11, bold=True, color=col, anchor="end"))
        f.append(line(t0, y, t1, y, color=MUTED, sw=1.2))
        for b in beats:
            x = t0 + b * span
            f.append(line(x, y - 5, x, y + 5, color=MUTED, sw=1.0))

    # ── ВЕРХНЯ смуга: блокувальний варіант (tone + delay) ──
    yb = 120
    f.append(rect(60, yb - 46, 820, 150, fill="#fdecea", stroke=POS, sw=1.6, rx=12))
    f.append(text(70, yb - 26, "delay(dur): loop() застряг у кожній ноті", size=12.5, bold=True, color=POS, anchor="start"))
    timeline_y(yb + 20, "зумер", POS)
    # кольорові відрізки нот на таймлайні зумера
    seg = [(0.0, 0.26, "мі"), (0.30, 0.26, "фа"), (0.60, 0.22, "соль")]
    for a, w, nm in seg:
        f.append(rect(t0 + a * span, yb + 20 - 9, w * span, 18, fill=POS, stroke=POS, sw=1, rx=3))
        f.append(text(t0 + (a + w / 2) * span, yb + 20 + 4, nm, size=9.5, bold=True, color=BG))
    # рядок «інша робота» — суцільно заморожено
    f.append(text(t0 - 14, yb + 62, "loop()", size=11, bold=True, color=MUTED, anchor="end"))
    f.append(rect(t0, yb + 62 - 9, span, 18, fill="#f1d0cc", stroke=POS, sw=1.0, rx=3, ))
    f.append(text(t0 + span / 2, yb + 62 + 4, "заморожено — кнопки й давачі не опитуються", size=9.5, bold=True, color=POS))

    # ── НИЖНЯ смуга: неблокувальний варіант (millis) ──
    yn = 320
    f.append(rect(60, yn - 46, 820, 170, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=12))
    f.append(text(70, yn - 26, "millis(): нота міняється сама, loop() крутиться далі", size=12.5, bold=True, color=FIELD, anchor="start"))
    timeline_y(yn + 20, "зумер", FIELD)
    for a, w, nm in seg:
        f.append(rect(t0 + a * span, yn + 20 - 9, w * span, 18, fill=FIELD, stroke=FIELD, sw=1, rx=3))
        f.append(text(t0 + (a + w / 2) * span, yn + 20 + 4, nm, size=9.5, bold=True, color=BG))
    # рядок «інша робота» — часті проходи loop() (густі рисочки)
    f.append(text(t0 - 14, yn + 62, "loop()", size=11, bold=True, color=INK, anchor="end"))
    f.append(line(t0, yn + 62, t1, yn + 62, color=MUTED, sw=1.0))
    x = t0
    while x <= t1:
        f.append(line(x, yn + 62 - 7, x, yn + 62 + 7, color=FIELD, sw=1.4))
        x += 18
    f.append(text(t0 + span / 2, yn + 86, "кожен виток читає кнопки й давачі — звук іде фоном", size=9.5, bold=True, color=FIELD))
    # позначка «момент зміни ноти = коли millis() перевалив за межу»
    xm = t0 + 0.30 * span
    f.append(line(xm, yn - 6, xm, yn + 34, color=INK, sw=1.2, dash="3,3"))
    f.append(text(xm, yn - 12, "millis() ≥ межі → наступна нота", size=9, color=INK))

    b, _, _ = textbox(W / 2, yn + 150,
                      "Той самий мотив звучить однаково. Різниця не в звуці, а в тім, що робить процесор МІЖ нотами:\n"
                      "з delay він стоїть, з millis — вільно проходить loop() тисячі разів і встигає на все інше.",
                      size=10.5, fill=FILL, stroke=MUTED)
    f.append(b)

    render(os.path.join(IMG, "ky006-nonblocking.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_sound()
    fig_wiring()
    fig_nonblocking()
    print("KY-006 figs done ->", IMG)
