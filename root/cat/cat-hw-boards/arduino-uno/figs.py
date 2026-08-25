# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Arduino UNO R3 (CH340)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія плати: мозок, USB-перекладач, живлення, ряди виводів ──────────
def fig_anatomy():
    W, H = 860, 560
    f = [text(W / 2, 30, "Arduino UNO — обв'язка навколо мікроконтролера ATmega328P",
              size=16, bold=True)]

    # Контур плати
    bx, by, bw, bh = 60, 60, W - 120, 430
    f.append(rect(bx, by, bw, bh, fill="#eaf3f4", stroke=FIELD, sw=2.2, rx=16))

    # Верхній ряд гнізд — цифрові виводи 0..13 (схематично, ~ = ШІМ)
    top_y = by + 20
    f.append(text(bx + bw / 2, top_y + 4,
                  "цифрові виводи 0…13   (~ = ШІМ: 3 5 6 9 10 11)",
                  size=11.5, bold=True, color=INK))
    # ряд «дірочок»
    nrow = 14
    gx0 = bx + 70
    gx1 = bx + bw - 70
    step = (gx1 - gx0) / (nrow - 1)
    for i in range(nrow):
        cx = gx0 + i * step
        f.append(circle(cx, top_y + 24, 4.5, fill=BG, stroke=INK, sw=1.3))

    # Нижній ряд гнізд — живлення + аналогові
    bot_y = by + bh - 40
    for i in range(nrow):
        cx = gx0 + i * step
        f.append(circle(cx, bot_y, 4.5, fill=BG, stroke=INK, sw=1.3))
    f.append(text(bx + bw * 0.30, bot_y + 22, "живлення: 5V · 3V3 · GND · VIN",
                  size=11, color=INK))
    f.append(text(bx + bw * 0.74, bot_y + 22, "аналогові входи A0…A5",
                  size=11, bold=True, color=INK))

    # USB-рознім (ліворуч, виступає за край)
    usb_y = by + 120
    f.append(rect(bx - 26, usb_y, 40, 56, fill="#cfd6da", stroke=INK, sw=1.6, rx=4))
    f.append(text(bx - 6, usb_y - 8, "USB", size=11, bold=True))

    # Круглий рознім живлення (ліворуч нижче)
    pj_y = by + 300
    f.append(circle(bx - 6, pj_y + 20, 15, fill="#333", stroke=INK, sw=1.6))
    f.append(circle(bx - 6, pj_y + 20, 6, fill=BG, stroke=INK, sw=1.4))
    f.append(text(bx - 6, pj_y - 6, "живлення", size=10, color=MUTED))
    f.append(text(bx - 6, pj_y + 52, "7–12 В", size=9.5, color=MUTED))

    # CH340 — USB-перекладач (біля USB)
    b, cw, ch = textbox(bx + 110, usb_y + 28, "CH340\nUSB → UART",
                        size=11.5, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=10)
    f.append(b)
    # лінія USB → CH340
    f.append(arrow(bx + 14, usb_y + 28, bx + 110 - cw / 2, usb_y + 28, color=POS, sw=2.0))

    # Лінійний стабілізатор (біля живлення)
    b, rw, rh = textbox(bx + 120, pj_y + 20, "стабілізатор\n→ рівні 5 В",
                        size=11.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.8, pad=10)
    f.append(b)
    f.append(arrow(bx + 12, pj_y + 20, bx + 120 - rw / 2, pj_y + 20, color=FIELD, sw=2.0))

    # ATmega328P — центральний чип у панельці
    chx, chy = bx + bw * 0.60, by + bh * 0.46
    chw, chh = 210, 96
    f.append(rect(chx - chw / 2, chy - chh / 2, chw, chh, fill="#20242a", stroke=INK, sw=2, rx=8))
    f.append(text(chx, chy - 8, "ATmega328P", size=15, bold=True, color="#ffffff"))
    f.append(text(chx, chy + 12, "8-біт · 16 МГц · у панельці", size=10.5, color="#c9ccd1"))
    # «ніжки» чипа
    for i in range(7):
        lx = chx - chw / 2 + 22 + i * (chw - 44) / 6
        f.append(line(lx, chy - chh / 2, lx, chy - chh / 2 - 8, color=INK, sw=1.4))
        f.append(line(lx, chy + chh / 2, lx, chy + chh / 2 + 8, color=INK, sw=1.4))

    # CH340 → ATmega: дві лінії UART. Маршрут веду ПОЗА написами:
    # з нижнього краю CH340-рамки праворуч у коридорі y=usb_y+70, тоді вгору-стрілкою у чип.
    ux_v = chx - 34          # вертикаль коридору — правіше за всі рамки й підписи
    uy_h = usb_y + 70        # горизонтальний коридор під CH340-рамкою
    f.append(line(bx + 110, usb_y + 44, bx + 110, uy_h, color=INK, sw=1.6))   # униз від CH340
    f.append(line(bx + 110, uy_h, ux_v, uy_h, color=INK, sw=1.6))             # праворуч у коридорі
    f.append(arrow(ux_v, uy_h, ux_v, chy - chh / 2 - 8, color=INK, sw=1.6))   # вгору-стрілка у чип
    # підпис — під горизонтальним коридором, у чистій зоні (нижче лінії, не на ній)
    f.append(text((bx + 110 + ux_v) / 2, uy_h + 18, "2 лінії UART (RX/TX)",
                  size=10, color=INK, italic=True))

    # стабілізатор → живить чип (5 В): коридор нижчий за всі підписи
    gx_v = chx - 44
    gy_h = chy + chh / 2 + 40
    f.append(line(bx + 120, pj_y + 4, bx + 120, gy_h, color=FIELD, sw=1.6))   # униз від стабілізатора
    f.append(line(bx + 120, gy_h, gx_v, gy_h, color=FIELD, sw=1.6))           # праворуч
    f.append(arrow(gx_v, gy_h, gx_v, chy + chh / 2 + 8, color=FIELD, sw=1.6)) # вгору-стрілка у чип
    # підпис — нижче горизонтального коридору, у чистій зоні
    f.append(text((bx + 120 + gx_v) / 2, gy_h + 18, "5 В живлення",
                  size=10, color=FIELD, italic=True))

    # Вбудований світлодіод на виводі 13 (праворуч угорі, до верхнього ряду)
    led_cx = gx0 + 13 * step
    f.append(circle(led_cx, top_y + 52, 6, fill="#ffd24d", stroke="#b8860b", sw=1.6))
    f.append(text(led_cx + 2, top_y + 78, "LED", size=9, bold=True, color="#8a6d00"))
    f.append(text(led_cx + 2, top_y + 92, "вивід 13", size=8.5, color=MUTED))
    f.append(line(led_cx, top_y + 28, led_cx, top_y + 46, color="#b8860b", sw=1.4))

    return render(os.path.join(IMG, "uno-anatomy.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: кнопка (вивід 2) + світлодіод через резистор (13) ───
def fig_wiring():
    W, H = 820, 500
    f = [text(W / 2, 30, "Розводка: кнопка на вивід 2, світлодіод через резистор на вивід 13",
              size=15, bold=True)]

    # Плата — вертикальна смуга ліворуч зі списком виводів
    bx, by, bw, bh = 60, 70, 190, 380
    f.append(rect(bx, by, bw, bh, fill="#eaf3f4", stroke=FIELD, sw=2.2, rx=12))
    f.append(text(bx + bw / 2, by + 26, "Arduino UNO", size=13, bold=True, color=FIELD))

    # виводи, які використовуємо, як точки на правому краї плати
    def pin(y, label):
        px = bx + bw
        f.append(circle(px, y, 5, fill=BG, stroke=INK, sw=1.5))
        f.append(text(bx + bw - 14, y + 4, label, size=11.5, bold=True, anchor="end"))
        return px

    y_led = by + 90
    y_gnd1 = by + 170
    y_btn = by + 260
    y_gnd2 = by + 330
    p_led = pin(y_led, "13")
    p_gnd1 = pin(y_gnd1, "GND")
    p_btn = pin(y_btn, "2")
    p_gnd2 = pin(y_gnd2, "GND")

    # ── Коло світлодіода: вивід 13 → резистор → LED → GND ──
    # резистор
    rx0 = p_led + 70
    f.append(line(p_led, y_led, rx0, y_led, color=POS, sw=2.2))
    b, rw, rh = textbox(rx0 + 46, y_led, "R 220 Ом", size=11, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.6, pad=8)
    f.append(b)
    # LED
    lx = rx0 + 46 + rw / 2 + 60
    f.append(circle(lx, y_led, 15, fill="#ffd24d", stroke="#b8860b", sw=2))
    f.append(text(lx, y_led - 24, "світлодіод", size=10.5, bold=True, color="#8a6d00"))
    f.append(line(rx0 + 46 + rw / 2, y_led, lx - 15, y_led, color=INK, sw=2.0))
    # LED → GND (вниз і назад до GND-виводу)
    f.append(line(lx, y_led + 15, lx, y_gnd1, color=INK, sw=2.0))
    f.append(line(lx, y_gnd1, p_gnd1, y_gnd1, color=INK, sw=2.0))
    f.append(text((p_led + lx) / 2, y_led + 62, "вивід дає 5 В, резистор тримає струм у безпеці",
                  size=10, color=INK, italic=True))

    # ── Коло кнопки: вивід 2 → кнопка → GND ; підтяжка (вбудована) до 5В ──
    kx = p_btn + 120
    # кнопка як прямокутник із розривом
    ksz = 46
    f.append(rect(kx - ksz / 2, y_btn - 20, ksz, 40, fill=BG, stroke=INK, sw=1.8, rx=6))
    f.append(text(kx, y_btn - 30, "кнопка", size=10.5, bold=True))
    # контакт вивід 2 → кнопка
    f.append(line(p_btn, y_btn, kx - ksz / 2, y_btn, color=NEG, sw=2.2))
    # кнопка → GND
    f.append(line(kx + ksz / 2, y_btn, kx + 110, y_btn, color=INK, sw=2.0))
    f.append(line(kx + 110, y_btn, kx + 110, y_gnd2, color=INK, sw=2.0))
    f.append(line(kx + 110, y_gnd2, p_gnd2, y_gnd2, color=INK, sw=2.0))

    # підпис підтяжки — окремою рамкою, з запасом праворуч унизу
    b, _, _ = textbox(W / 2 + 40, H - 40,
                      "Вбудована підтяжка тримає вивід 2 в «1»; натиск кнопки замикає його на землю → читається «0».",
                      size=11, fill=FILL, stroke=MUTED, sw=1.4, pad=10)
    f.append(b)

    return render(os.path.join(IMG, "uno-wiring.svg"), W, H, *f)


# ── 3. Керування потужним навантаженням через транзистор ─────────────────────
def fig_transistor():
    W, H = 820, 520
    f = [text(W / 2, 30, "Вивід керує силою через транзистор, а не тягне її сам",
              size=15, bold=True)]

    # Спільна земля — горизонтальна шина внизу
    gy = H - 70
    gx0, gx1 = 70, W - 70
    f.append(line(gx0, gy, gx1, gy, color=INK, sw=2.4))
    f.append(text(gx1 - 8, gy + 22, "спільна земля (GND)", size=11, color=INK,
                  anchor="end", italic=True))

    # ── UNO (ліворуч) ──
    ux, uy, uw, uh = 70, 150, 150, 120
    f.append(rect(ux, uy, uw, uh, fill="#eaf3f4", stroke=FIELD, sw=2.2, rx=12))
    f.append(text(ux + uw / 2, uy + 30, "Arduino UNO", size=13, bold=True, color=FIELD))
    f.append(text(ux + uw / 2, uy + 54, "вивід ~9", size=12, bold=True, color=INK))
    f.append(text(ux + uw / 2, uy + 74, "дає ~мА", size=10.5, color=MUTED))
    # земля UNO вниз до шини
    f.append(line(ux + 30, uy + uh, ux + 30, gy, color=INK, sw=1.8))

    # ── Транзистор: коло з трьома виводами (база / колектор / емітер) ──
    tcx, tcy, tr = 470, 300, 34
    f.append(circle(tcx, tcy, tr, fill=BG, stroke=INK, sw=2.2))
    f.append(text(tcx + tr + 10, tcy + 24, "NPN", size=11, bold=True, anchor="start", color=INK))
    # вертикальна «пластина» бази всередині
    f.append(line(tcx - 10, tcy - 20, tcx - 10, tcy + 20, color=INK, sw=2.6))
    # колектор (угору-праворуч) і емітер (униз-праворуч)
    f.append(line(tcx - 10, tcy - 8, tcx + 16, tcy - 24, color=INK, sw=2.0))   # до колектора
    f.append(line(tcx - 10, tcy + 8, tcx + 16, tcy + 24, color=INK, sw=2.0))   # до емітера

    # ── Коло бази: вивід → резистор → база ──
    by_line = tcy
    rx0 = ux + uw + 20
    f.append(line(ux + uw, by_line, rx0, by_line, color=INK, sw=2.0))          # від виводу праворуч
    b, rbw, rbh = textbox(rx0 + 48, by_line, "R база\n≈1 кОм", size=10.5, bold=True,
                          fill="#fdecea", stroke=POS, sw=1.6, pad=8)
    f.append(b)
    f.append(line(rx0 + 48 + rbw / 2, by_line, tcx - 10, by_line, color=INK, sw=2.0))  # до бази
    f.append(text((ux + uw + tcx) / 2 - 6, by_line + 40,
                  "малий струм у базу відмикає транзистор",
                  size=10, color=INK, italic=True))

    # ── Коло сили: +живлення → навантаження → колектор ; емітер → земля ──
    # Навантаження — РОЗРИВ у вертикальній шині живлення (послідовний елемент):
    # лінія доходить до ВЕРХУ рамки, всередині — сама рамка, далі лінія йде від НИЗУ.
    supply_x = tcx + 150            # вертикаль плюсової шини живлення праворуч
    top_y = 120
    node_y = tcy - 60               # вузол «низ навантаження = колектор» (y=240), нижче рамки

    # рамка навантаження — спершу порахуємо її межі, щоб лінії стали до країв, не крізь текст
    load_cy = 200
    b, lw, lh = textbox(supply_x, load_cy, "навантаження\n(мотор / реле)", size=11, bold=True,
                        fill="#eef6ef", stroke=FIELD, sw=1.8, pad=9)
    load_top = load_cy - lh / 2
    load_bot = load_cy + lh / 2

    # плюсова шина: від «+» УНИЗ рівно до верху рамки (не крізь неї)
    f.append(plus(supply_x, top_y - 4, r=10))
    f.append(text(supply_x + 16, top_y - 2, "окреме живлення (напр. 12 В)",
                  size=11, color=POS, anchor="start", bold=True))
    f.append(line(supply_x, top_y + 6, supply_x, load_top, color=POS, sw=2.2))
    f.append(b)                                                   # рамка навантаження
    # від низу рамки вниз до вузла колектора
    f.append(line(supply_x, load_bot, supply_x, node_y, color=INK, sw=2.0))
    # колектор транзистора вгору-праворуч до цього вузла
    f.append(line(tcx + 16, tcy - 24, tcx + 16, node_y, color=INK, sw=2.0))
    f.append(line(tcx + 16, node_y, supply_x, node_y, color=INK, sw=2.0))
    # емітер униз до спільної землі
    f.append(line(tcx + 16, tcy + 24, tcx + 16, gy, color=INK, sw=2.0))

    # ── Діод-гасник поперек навантаження (окрема гілка праворуч) ──
    dx = supply_x + 110             # правіше за рамку й її підпис, чиста колонка
    dtop, dbot = load_top, node_y
    f.append(line(supply_x, dtop, dx, dtop, color=MUTED, sw=1.6))   # від верху рамки праворуч
    f.append(line(dx, dtop, dx, dbot, color=MUTED, sw=1.6))         # вертикаль діода
    f.append(line(dx, dbot, supply_x, dbot, color=MUTED, sw=1.6))   # назад до вузла внизу
    # трикутник діода (катодом угору — до плюса)
    dm = (dtop + dbot) / 2
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="1.8"/>'
             % (dx - 9, dm + 8, dx + 9, dm + 8, dx, dm - 8, MUTED))
    f.append(line(dx - 9, dm - 8, dx + 9, dm - 8, color=MUTED, sw=1.8))          # смужка катода
    f.append(text(dx + 14, dm + 4, "діод-гасник", size=10, color=MUTED, anchor="start", italic=True))

    return render(os.path.join(IMG, "uno-transistor.svg"), W, H, *f)


if __name__ == "__main__":
    fig_anatomy()
    fig_wiring()
    fig_transistor()
    print("OK: uno-anatomy.svg, uno-wiring.svg, uno-transistor.svg")
