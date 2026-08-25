# -*- coding: utf-8 -*-
"""Фігури до теми «Екосистема МК».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit (шари стосу — різні кольори)
BLUE   = "#1a5276"   # спільнота / документація
TEAL   = "#117a65"   # приклади й бібліотеки
PURPLE = "#7d3c98"   # SDK / контракт
GOLD   = "#d68910"   # HAL / драйвери


# ── 1. Стос шарів екосистеми: чип А (повний) проти чипа Б (голий) ─────────────
def fig_ecosystem_stack():
    W, H = 820, 430
    f = [text(W / 2, 26, "Що купуєш разом із чипом: шари над кремнієм", size=15, bold=True)]

    # підписи колонок
    f.append(text(280, 60, "Чіп А — з екосистемою", size=13, color=TEAL, bold=True))
    f.append(text(670, 60, "Чіп Б — голий", size=13, color=POS, bold=True))

    layers = [
        ("Спільнота й документація", "#d6eaf8", BLUE),
        ("Приклади й бібліотеки",    "#d1f2eb", TEAL),
        ("SDK / фреймворк",          "#f0e6fa", PURPLE),
        ("HAL / драйвери",           "#fef9e7", GOLD),
    ]
    y = 74
    bh = 56
    for label, fill, col in layers:
        # чип А — повний шар
        f.append(rect(80, y, 400, bh, fill=fill, stroke=col, sw=2.0, rx=4))
        f.append(text(280, y + bh / 2 + 5, label, size=13, color=col, bold=True))
        # чип Б — шар відсутній
        f.append(rect(540, y, 260, bh, fill="#f5f5f5", stroke=MUTED, sw=1.0, rx=4))
        f.append(text(670, y + bh / 2 + 5, "— відсутній —", size=12, color=MUTED))
        y += bh + 6

    # голий чип — спільний фундамент обом
    f.append(rect(80, y, 400, bh, fill=FILL, stroke=MUTED, sw=2.0, rx=4))
    f.append(text(280, y + bh / 2 + 5, "Чіп (залізо)", size=13, color=MUTED, bold=True))
    f.append(rect(540, y, 260, bh, fill=FILL, stroke=MUTED, sw=2.0, rx=4))
    f.append(text(670, y + bh / 2 + 5, "Чіп (залізо)", size=13, color=MUTED, bold=True))

    f.append(text(W / 2, H - 12,
                  "шари над чипом — і є реальна цінність платформи; гарне залізо без них — тупик",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "ecosystem-stack.svg"), W, H, *f)


# ── 2. МГц проти людино-днів: швидший чіп — довша дорога ──────────────────────
def fig_mhz_vs_days():
    W, H = 760, 380
    f = [text(W / 2, 26, "Швидший чіп — довша дорога до прототипу", size=15, bold=True)]

    base = 320          # рівень осі
    top = 70            # стеля стовпчиків
    span = base - top

    # три пари стовпчиків: такти / час до прототипу / ризик
    groups = [
        ("Тактова частота", [("Чіп А", 0.75, TEAL, "180 МГц"),
                             ("Чіп Б", 1.0, POS, "240 МГц")]),
        ("Час до прототипу", [("Чіп А", 0.14, TEAL, "~3 дні"),
                              ("Чіп Б", 1.0, POS, "~22 дні")]),
        ("Ризик не дійти", [("Чіп А", 0.22, TEAL, "низький"),
                            ("Чіп Б", 0.92, POS, "високий")]),
    ]
    gx = 70
    gw = 210            # ширина групи
    bw = 62
    for gtitle, bars in groups:
        # вісь під групою
        f.append(line(gx - 6, base, gx + gw - 40, base, color=MUTED, sw=1.0))
        bx = gx
        for blab, frac, col, val in bars:
            h = span * frac
            fill = "#d1f2eb" if col == TEAL else "#fce8e8"
            f.append(rect(bx, base - h, bw, h, fill=fill, stroke=col, sw=2.0, rx=3))
            f.append(text(bx + bw / 2, base - h - 10, val, size=11, color=col, bold=True))
            f.append(text(bx + bw / 2, base + 18, blab, size=10, color=MUTED))
            bx += bw + 16
        f.append(mtext(gx + (gw - 56) / 2, base + 40, gtitle, size=11, color=INK))
        gx += gw + 30

    # позначка, де Б «виграє»
    f.append(text(70 + 62 + 8 + 31, top + 4, "← лише тут Б попереду",
                  size=10, color=MUTED, anchor="start", italic=True))

    f.append(text(W / 2, H - 10,
                  "такти — єдина вісь, де потужніший чіп попереду; час і ризик вирішує екосистема",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "mhz-vs-days.svg"), W, H, *f)


# ── 3. HAL як вузька «талія» (до вставки proj-portability) ────────────────────
# Широка логіка зверху → вузький контракт hal.h → три реалізації під чипи.
def fig_hal_waist():
    W, H = 860, 520
    f = [text(W / 2, 26, "HAL як вузька «талія» між логікою і різними чипами", size=15, bold=True)]

    # верх — прикладна логіка (широкий блок)
    f.append(rect(80, 50, 700, 90, fill="#d6eaf8", stroke=BLUE, sw=2.5, rx=10))
    f.append(text(430, 76, "Прикладна логіка (app.cpp)", size=14, color=BLUE, bold=True))
    f.append(text(430, 98, "стан · таймінги · протокол — пишеться раз", size=12, color=BLUE))
    f.append(text(430, 120, "не містить жодного #include <Arduino.h> чи IDF-заголовка",
                  size=11, color=MUTED))

    # чотири стрілки вниз до контракту (підписані функціями)
    for cx, fn in ((170, "hal_gpio_write()"), (330, "hal_uart_puts()"),
                   (510, "hal_delay_ms()"), (670, "hal_millis()")):
        f.append(line(cx, 140, cx, 193, color=PURPLE, sw=1.8, dash=None))
        f.append('<line x1="%.1f" y1="140" x2="%.1f" y2="193" stroke="%s" stroke-width="1.8" '
                 'marker-end="url(#arrow)"/>' % (cx, cx, PURPLE))
        f.append(text(cx, 160, fn, size=9, color=PURPLE))

    # вузька шийка — контракт
    f.append(rect(220, 215, 420, 62, fill="#e8daef", stroke=PURPLE, sw=3.0, rx=8))
    f.append(text(430, 240, "hal.h — стабільний контракт", size=14, color=PURPLE, bold=True))
    f.append(text(430, 261, "однаковий для всіх чипів · шар абстракції заліза", size=11, color=PURPLE))

    # анотація: препроцесор обирає одну гілку
    f.append(text(648, 300, "препроцесор обирає одну гілку при збірці",
                  size=10, color=POS, anchor="end", italic=True))

    # три стрілки від контракту вниз до реалізацій
    for tx in (185, 430, 675):
        f.append('<line x1="430" y1="277" x2="%.1f" y2="305" stroke="%s" stroke-width="1.8" '
                 'marker-end="url(#arrow)"/>' % (tx, PURPLE))

    # три реалізації під чипи
    impls = [
        (80, "hal_esp32.cpp", "#if defined(ARDUINO_ARCH_ESP32)",
         ["digitalWrite(pin, on?HIGH:LOW)", "Serial.print(s)", "delay(ms)", "return millis()"],
         "Arduino ESP32 API", "#d5f5e3", TEAL),
        (325, "hal_avr.cpp", "#if defined(__AVR__)",
         ["PORTB |=  (1<<pin)  // запис 1", "PORTB &= ~(1<<pin)  // запис 0",
          "UDR0 = *s++  // байт у UART", "_delay_ms(ms)"],
         "голий регістровий AVR", "#fef9e7", GOLD),
        (570, "hal_stm32.cpp", "#if defined(ARDUINO_ARCH_STM32)",
         ["HAL_GPIO_WritePin(...)", "HAL_UART_Transmit(...)", "HAL_Delay(ms)", "HAL_GetTick()"],
         "ST вендорський HAL", "#d6eaf8", BLUE),
    ]
    for x, fname, guard, body, note, fill, col in impls:
        f.append(rect(x, 310, 210, 155, fill=fill, stroke=col, sw=2.0, rx=8))
        f.append(text(x + 105, 330, fname, size=12, color=col, bold=True))
        f.append(fitbox(x + 8, 342, 194, 22, guard, size=9, fill=BG, stroke=col, sw=1.0, rx=3))
        yy = 384
        for ln in body:
            f.append(text(x + 105, yy, ln, size=9, color=col))
            yy += 16
        f.append(text(x + 105, 452, note, size=9, color=MUTED, italic=True))

    f.append(text(W / 2, 508,
                  "широке зверху й знизу, вузьке посередині: зміна чипа чіпає лише нижній ярус",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "hal-waist.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ecosystem_stack()
    fig_mhz_vs_days()
    fig_hal_waist()
    print("OK: 3 figures ->", IMG)
