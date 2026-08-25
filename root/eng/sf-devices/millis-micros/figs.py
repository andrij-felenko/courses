# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Точний час» (millis/micros зсередини).
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що повертають: час ВІД СТАРТУ, не календарний ─────────────────────────
# Ідея: обидві функції — це показання одного лічильника, що пішов із нуля в
# мить увімкнення; не «котра година», а скільки минуло.
def fig_what_they_return():
    W, H = 900, 340
    P = [text(W / 2, 30, "millis() і micros(): скільки минуло від старту чипа",
              size=17, bold=True)]
    P.append(text(W / 2, 52, "не «котра година», а лічильник, що пішов із нуля при ввімкненні",
                  size=12, color=MUTED, italic=True))

    # вісь часу
    x0, x1, ay = 110, W - 60, 150
    P.append(circle(x0, ay, 7, fill=POS, stroke=POS, sw=0))
    P.append(text(x0, ay - 26, "увімкнення", size=11, color=POS, bold=True))
    P.append(text(x0, ay - 12, "(t = 0)", size=10, color=MUTED))
    P.append(arrow(x0, ay, x1, ay, color=INK, sw=2.2))
    for fx in (0.32, 0.55, 0.78):
        x = x0 + fx * (x1 - x0)
        P.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.3))
    P.append(text(x1 - 28, ay + 22, "час →", size=11, color=INK))

    # дві рамки-функції під віссю
    mx, ux = x0 + 0.30 * (x1 - x0), x0 + 0.62 * (x1 - x0)
    fr, w, h = textbox(mx, ay + 80, "millis()\n= мс від старту", size=12,
                       bold=True, color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=160)
    P.append(fr)
    fr, w, h = textbox(ux, ay + 80, "micros()\n= мкс від старту", size=12,
                       bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, min_w=160)
    P.append(fr)
    P.append(line(mx, ay + 5, mx, ay + 58, color=FIELD, sw=1.2, dash="3,3"))
    P.append(line(ux, ay + 5, ux, ay + 58, color=NEG, sw=1.2, dash="3,3"))

    P.append(text(W / 2, H - 26,
                  "Обидві читають апаратний лічильник і переводять його в мс або мкс.",
                  size=12, bold=True))
    P.append(text(W / 2, H - 8,
                  "Скинеться він лише при перезавантаженні — тоді відлік знову з нуля.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "what-they-return.svg"), W, H, *P)


# ── 2. AVR зсередини: переповнення Timer0 щомілісекунди підіймає ISR ─────────
# Ідея: вузький 8-бітний таймер переповнюється ~раз на мс, ISR робить ms++;
# millis() читає лічильник, micros() домішує поточний TCNT0 (×4 мкс).
def fig_avr_internals():
    W, H = 920, 380
    P = [text(W / 2, 30, "AVR (Uno): Timer0 переповнюється ~щомс і кличе ISR",
              size=17, bold=True)]

    # ліворуч — таймер
    tb, w, h = textbox(170, 130, "Timer0 (8-біт)\nкрок 4 мкс\nпереповнення\n≈ 1.024 мс",
                       size=12, bold=True, fill="#fef7e9", stroke="#b08900", min_w=200)
    P.append(tb)
    # стрілка переповнення → ISR
    P.append(arrow(280, 130, 420, 130, color=POS, sw=2))
    P.append(text(350, 116, "переповнення", size=10.5, color=POS, bold=True))

    # ISR
    ib, w, h = textbox(540, 130, "ISR переповнення:\nms_count++\n(+ дрібна корекція\nза 0.024 мс)",
                       size=12, bold=True, fill="#eaf0fd", stroke=NEG, min_w=230)
    P.append(ib)
    # стрілка ISR → лічильник
    P.append(arrow(540, 175, 540, 235, color=INK, sw=2))

    # глобальний лічильник
    cb, w, h = textbox(540, 270, "ms_count (лічильник мс)", size=12, bold=True,
                       fill="#e9f7ef", stroke=FIELD, min_w=260)
    P.append(cb)

    # millis()/micros() читають
    P.append(arrow(670, 270, 770, 270, color=INK, sw=2))
    rb, w, h = textbox(820, 250, "millis()\n→ ms_count", size=11.5, bold=True,
                       color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=150)
    P.append(rb)
    rb, w, h = textbox(820, 305, "micros()\n→ ms×1000 + TCNT0×4", size=10.5, bold=True,
                       color=NEG, fill="#eaf0fd", stroke=NEG, min_w=190)
    P.append(rb)

    P.append(text(W / 2, H - 16,
                  "Схема працює, та переривання тікає ~1000 разів на секунду — забирає процесор.",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "avr-internals.svg"), W, H, *P)


# ── 3. ESP32 зсередини: широкий лічильник у мкс; читай та поділи ─────────────
# Ідея: 64-бітний апаратний таймер сам лічить мкс; micros() = читання,
# millis() = читання / 1000. Жодного ISR. Та Arduino-обгортка обрізає до 32 біт.
def fig_esp32_internals():
    W, H = 920, 380
    P = [text(W / 2, 30, "ESP32: широкий 64-бітний таймер сам лічить мкс",
              size=17, bold=True)]

    # апаратний лічильник
    hb, w, h = textbox(W / 2, 110,
                       "апаратний системний таймер — 64 біт, лічить мкс безперервно",
                       size=12.5, bold=True, fill="#e9f7ef", stroke=FIELD, min_w=560)
    P.append(hb)

    # дві гілки вниз
    lx, rx = W * 0.30, W * 0.70
    P.append(arrow(W / 2 - 120, 134, lx, 188, color=INK, sw=1.8))
    P.append(arrow(W / 2 + 120, 134, rx, 188, color=INK, sw=1.8))

    fb, w, h = textbox(lx, 215, "micros()\n= просто прочитати", size=12, bold=True,
                       color=NEG, fill="#eaf0fd", stroke=NEG, min_w=210)
    P.append(fb)
    fb, w, h = textbox(rx, 215, "millis()\n= прочитати / 1000", size=12, bold=True,
                       color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=210)
    P.append(fb)

    # застереження про 32-бітну обгортку
    wb, w, h = textbox(W / 2, 305,
                       "Та Arduino-функції віддають 32 біт:\n"
                       "millis() обгортається ~49.7 дня, micros() ~71 хв.\n"
                       "Повні 64 біт — через esp_timer_get_time(). Час порівнюй відніманням.",
                       size=11.5, bold=True, color=POS, fill="#fdecea", stroke=POS, min_w=560)
    P.append(wb)
    render(os.path.join(IMG, "esp32-internals.svg"), W, H, *P)


# ── 4. Роздільність: крок millis() vs micros() (сходинки) ────────────────────
# Ідея: значення росте сходинками; крок millis() — 1 мс (грубо), micros() —
# ~1 мкс (на ESP32), у 1000 разів дрібніше.
def fig_resolution():
    W, H = 920, 380
    P = [text(W / 2, 30, "Роздільність — це крок: millis() по 1 мс, micros() тонше",
              size=17, bold=True)]
    P.append(text(W / 2, 52, "значення міняється сходинками; дрібніший крок ловить коротші проміжки",
                  size=12, color=MUTED, italic=True))

    # грубі сходинки millis()
    P.append(text(70, 120, "millis()", size=11, color=FIELD, bold=True, anchor="start"))
    P.append('<polyline points="90,200 220,200 220,168 350,168 350,136 480,136 '
             '480,104 610,104" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % FIELD)
    P.append(text(155, 216, "крок 1 мс", size=9.5, color=FIELD))

    # дрібні сходинки micros()
    pts = " ".join("%d,%d" % (90 + i * 20, 320 - i * 4) for i in range(27))
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, NEG))
    P.append(text(70, 300, "micros()", size=11, color=NEG, bold=True, anchor="start"))
    P.append(text(340, 336, "крок ~1 мкс — у 1000× дрібніший", size=10, color=NEG, bold=True))

    # бічна підказка вибору
    P.append(rect(645, 110, 250, 130, fill=BG, stroke="#e0e0e0", sw=1.5, rx=10))
    P.append(text(770, 136, "Що обрати:", size=11.5, bold=True))
    P.append(text(662, 162, "• інтервали від мс — millis()", size=10.5, anchor="start"))
    P.append(text(662, 186, "• короткі чи точні — micros()", size=10.5, anchor="start"))
    P.append(text(662, 214, "на Uno крок micros ~4 мкс,", size=10, color=MUTED, anchor="start"))
    P.append(text(672, 230, "на ESP32 ~1 мкс", size=10, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "resolution.svg"), W, H, *P)


# ── 5. Точність = точність кварцу (ppm, дрейф) ───────────────────────────────
# Ідея: лічильник рахує тіки бездоганно; уся похибка йде від кварцу і міряється
# в ppm; на коротких інтервалах непомітна, за дні набігає дрейф.
def fig_accuracy_crystal():
    W, H = 920, 380
    P = [text(W / 2, 30, "Точність дорівнює точності кварцу (а не лічильника)",
              size=17, bold=True)]

    # ланцюг кварц → лічильник → час
    qb, w, h = textbox(160, 120, "кварц\n(біжить/відстає)", size=12, bold=True,
                       fill="#fef7e9", stroke="#b08900", min_w=180)
    P.append(qb)
    P.append(arrow(250, 120, 360, 120, color=INK, sw=2))
    cb, w, h = textbox(460, 120, "лічильник\nрахує тіки точно", size=12, bold=True,
                       fill="#e9f7ef", stroke=FIELD, min_w=190)
    P.append(cb)
    P.append(arrow(560, 120, 670, 120, color=INK, sw=2))
    tb, w, h = textbox(775, 120, "millis()/micros()\nпохибка = похибка кварцу", size=11.5,
                       bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, min_w=230)
    P.append(tb)

    # таблиця дрейфу
    P.append(text(W / 2, 210, "Дрейф у ppm (частинах на мільйон):", size=12.5, bold=True))
    rows = [("±10 ppm", "≈ ±0.86 с/добу", "звичайний кварц"),
            ("±20 ppm", "≈ ±1.73 с/добу", "звичайний кварц"),
            ("±50 ppm", "≈ ±4.32 с/добу", "дешевий кварц")]
    y0, dy = 240, 38
    for i, (a, b, c) in enumerate(rows):
        y = y0 + i * dy
        P.append(text(300, y, a, size=12, bold=True, color=POS, anchor="end"))
        P.append(text(330, y, b, size=12, anchor="start"))
        P.append(text(600, y, c, size=11, color=MUTED, anchor="start"))
    P.append(text(W / 2, H - 14,
                  "На секундах-хвилинах непомітно; за дні набігає. Треба «справжній час» — RTC чи мережа.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "accuracy-crystal.svg"), W, H, *P)


# ── 6. Три прийоми: мітка / інтервал / тайм-аут — усі через віднімання ───────
# Ідея: уся повсякденна робота з часом — три заготовки, і всі стійкі до
# переповнення, бо працюють із РІЗНИЦЕЮ.
def fig_usage():
    W, H = 940, 320
    P = [text(W / 2, 30, "Три прийоми — і всі через віднімання (стійкі до переповнення)",
              size=17, bold=True)]

    cards = [
        ("мітка часу", "t = micros();", "запам'ятати мить", FIELD, "#e9f7ef"),
        ("інтервал", "dt = micros() − t0;", "скільки тривало", NEG, "#eaf0fd"),
        ("тайм-аут", "if (millis() − t0 > LIMIT)", "чи не задовго чекаємо", POS, "#fdecea"),
    ]
    cw, gap = 270, 30
    total = 3 * cw + 2 * gap
    x = (W - total) / 2
    for name, code, sub, col, fill in cards:
        P.append(rect(x, 80, cw, 150, fill=fill, stroke=col, sw=1.8, rx=10))
        P.append(text(x + cw / 2, 112, name, size=14, bold=True, color=col))
        P.append(text(x + cw / 2, 150, code, size=12.5, bold=True, color=INK))
        P.append(text(x + cw / 2, 182, sub, size=11, color=MUTED))
        x += cw + gap

    P.append(text(W / 2, H - 28,
                  "Ключ усюди — РІЗНИЦЯ часів, а не абсолютне значення.",
                  size=12.5, bold=True))
    P.append(text(W / 2, H - 8,
                  "millis()/micros() дешеві — лише читають лічильник, тож клич скільки треба.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "usage.svg"), W, H, *P)


if __name__ == "__main__":
    fig_what_they_return()
    fig_avr_internals()
    fig_esp32_internals()
    fig_resolution()
    fig_accuracy_crystal()
    fig_usage()
    print("OK: 6 figures -> img/")
