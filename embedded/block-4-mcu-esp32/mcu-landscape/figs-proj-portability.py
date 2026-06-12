# -*- coding: utf-8 -*-
"""
Фігури для вставки r11-s7-a-portability.md
(⚙️ Один код — різні МК: HAL-шар і умовна компіляція)

Запуск: python figs-r11-s7-a-portability.py
Вивід: ./img/fig-r11-s7a-1-hal-waist.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Кольори для HAL-теми ──────────────────────────────────────────────────────
APP_COL   = "#1a5276"   # прикладна логіка — синя
APP_FILL  = "#d6eaf8"
HAL_COL   = "#7d3c98"   # HAL-контракт — фіолетовий
HAL_FILL  = "#e8daef"
ESP_COL   = "#1e8449"   # ESP32-гілка — зелена
ESP_FILL  = "#d5f5e3"
AVR_COL   = "#d68910"   # AVR-гілка — помаранчева
AVR_FILL  = "#fef9e7"
STM_COL   = "#1a5276"   # STM32-гілка — синя
STM_FILL  = "#d6eaf8"
PREP_COL  = "#c0392b"   # препроцесор-стрілка — червона


def fig1_hal_waist():
    W, H = 860, 520
    parts = []

    # ── Заголовок ────────────────────────────────────────────────────────────
    parts.append(text(W // 2, 26,
                      "Рис. 4.11.7a.1  HAL як вузька «талія» між логікою і різними чипами",
                      size=14, bold=True))

    # ═══════════════════════════════════════════════════════════════════════════
    # ВЕРХНІЙ ЯРУС: Прикладна логіка (широкий блок)
    # ═══════════════════════════════════════════════════════════════════════════
    app_x, app_y, app_w, app_h = 80, 50, 700, 90
    parts.append(rect(app_x, app_y, app_w, app_h,
                      fill=APP_FILL, stroke=APP_COL, sw=2.5, rx=10))
    parts.append(text(app_x + app_w / 2, app_y + 24,
                      "Прикладна логіка (app.cpp)",
                      size=14, bold=True, color=APP_COL))
    parts.append(text(app_x + app_w / 2, app_y + 44,
                      "стан · таймінги · протокол — пишеться РАЗ",
                      size=12, color=APP_COL))
    parts.append(text(app_x + app_w / 2, app_y + 66,
                      "не містить жодного #include <Arduino.h> чи IDF-заголовка",
                      size=11, color=MUTED))

    # ═══════════════════════════════════════════════════════════════════════════
    # СТРІЛКИ ВНИЗ від логіки до HAL (4 функції)
    # ═══════════════════════════════════════════════════════════════════════════
    fn_labels = [
        "hal_gpio_write()",
        "hal_uart_puts()",
        "hal_delay_ms()",
        "hal_millis()",
    ]
    fn_xs = [170, 330, 510, 670]
    arrow_top_y = app_y + app_h
    arrow_bot_y = 215

    for fx, lbl in zip(fn_xs, fn_labels):
        parts.append(arrow(fx, arrow_top_y, fx, arrow_bot_y - 22, color=HAL_COL, sw=1.8))
        # мітка функції вздовж стрілки
        parts.append(text(fx, arrow_top_y + 18, lbl, size=9, color=HAL_COL, anchor="middle"))

    # ═══════════════════════════════════════════════════════════════════════════
    # «ТАЛІЯ» — контракт hal.h (вузький центральний блок)
    # ═══════════════════════════════════════════════════════════════════════════
    hal_cx = W / 2
    hal_y, hal_h = 215, 62
    hal_w = 420
    hal_x = hal_cx - hal_w / 2
    parts.append(rect(hal_x, hal_y, hal_w, hal_h,
                      fill=HAL_FILL, stroke=HAL_COL, sw=3, rx=8))
    parts.append(text(hal_cx, hal_y + 22,
                      "hal.h — стабільний контракт",
                      size=14, bold=True, color=HAL_COL))
    parts.append(text(hal_cx, hal_y + 43,
                      "однаковий для ВСІХ чипів · Hardware Abstraction Layer",
                      size=11, color=HAL_COL))

    # Бічна стрілка «препроцесор обирає одну гілку»
    prep_x = hal_x + hal_w + 12
    prep_mid_y = hal_y + hal_h / 2
    # горизонтальна лінія праворуч від HAL
    parts.append(line(prep_x, prep_mid_y, prep_x + 60, prep_mid_y,
                      color=PREP_COL, sw=2.0, dash="5 3"))
    # вертикальна вниз до нижнього ярусу
    bot_branch_y = 355
    parts.append(line(prep_x + 60, prep_mid_y, prep_x + 60, bot_branch_y,
                      color=PREP_COL, sw=2.0, dash="5 3"))
    # горизонтальна ліворуч до нижнього ярусу
    parts.append(line(prep_x + 60, bot_branch_y, prep_x, bot_branch_y,
                      color=PREP_COL, sw=2.0, dash="5 3"))
    # мітка «препроцесор»
    parts.append(text(prep_x + 62, prep_mid_y - 10,
                      "препроцесор обирає", size=10, color=PREP_COL, anchor="start"))
    parts.append(text(prep_x + 62, prep_mid_y + 6,
                      "рівно одну гілку", size=10, color=PREP_COL, anchor="start"))
    parts.append(text(prep_x + 62, prep_mid_y + 22,
                      "при збірці", size=10, color=PREP_COL, anchor="start"))

    # ═══════════════════════════════════════════════════════════════════════════
    # СТРІЛКИ ВНИЗ від HAL до реалізацій
    # ═══════════════════════════════════════════════════════════════════════════
    col_xs = [185, 430, 675]
    hal_bot_y = hal_y + hal_h

    for cx in col_xs:
        parts.append(arrow(hal_cx, hal_bot_y, cx, 305, color=HAL_COL, sw=1.8))

    # ═══════════════════════════════════════════════════════════════════════════
    # НИЖНІЙ ЯРУС: три реалізації-колонки
    # ═══════════════════════════════════════════════════════════════════════════
    col_w = 210
    col_h = 155
    col_y = 310

    # ── ESP32 ────────────────────────────────────────────────────────────────
    esp_x = col_xs[0] - col_w / 2
    parts.append(rect(esp_x, col_y, col_w, col_h,
                      fill=ESP_FILL, stroke=ESP_COL, sw=2, rx=8))
    parts.append(text(col_xs[0], col_y + 20,
                      "hal_esp32.cpp", size=12, bold=True, color=ESP_COL))
    # макрос — виділений рамкою
    parts.append(fitbox(esp_x + 8, col_y + 32, col_w - 16, 22,
                        "#if defined(ARDUINO_ARCH_ESP32)",
                        size=9, fill="#c8f7d8", stroke=ESP_COL, sw=1, rx=3))
    parts.append(text(col_xs[0], col_y + 74,
                      "digitalWrite(pin, on?HIGH:LOW)", size=9, color=ESP_COL))
    parts.append(text(col_xs[0], col_y + 90,
                      "Serial.print(s)", size=9, color=ESP_COL))
    parts.append(text(col_xs[0], col_y + 106,
                      "delay(ms)", size=9, color=ESP_COL))
    parts.append(text(col_xs[0], col_y + 122,
                      "return millis()", size=9, color=ESP_COL))
    parts.append(text(col_xs[0], col_y + 142,
                      "Arduino ESP32 API", size=9, color=MUTED, italic=True))

    # ── AVR ──────────────────────────────────────────────────────────────────
    avr_x = col_xs[1] - col_w / 2
    parts.append(rect(avr_x, col_y, col_w, col_h,
                      fill=AVR_FILL, stroke=AVR_COL, sw=2, rx=8))
    parts.append(text(col_xs[1], col_y + 20,
                      "hal_avr.cpp", size=12, bold=True, color=AVR_COL))
    parts.append(fitbox(avr_x + 8, col_y + 32, col_w - 16, 22,
                        "#if defined(__AVR__)",
                        size=9, fill="#fde8b0", stroke=AVR_COL, sw=1, rx=3))
    parts.append(text(col_xs[1], col_y + 68,
                      "PORTB |= (1<<pin);  // write 1", size=9, color=AVR_COL))
    parts.append(text(col_xs[1], col_y + 82,
                      "PORTB &= ~(1<<pin); // write 0", size=9, color=AVR_COL))
    parts.append(text(col_xs[1], col_y + 98,
                      "UART0->DR = *s++; ...", size=9, color=AVR_COL))
    parts.append(text(col_xs[1], col_y + 114,
                      "_delay_ms(ms)", size=9, color=AVR_COL))
    parts.append(text(col_xs[1], col_y + 130,
                      "timer0_millis counter", size=9, color=AVR_COL))
    parts.append(text(col_xs[1], col_y + 146,
                      "голий регістровий AVR", size=9, color=MUTED, italic=True))

    # ── STM32 ────────────────────────────────────────────────────────────────
    stm_x = col_xs[2] - col_w / 2
    parts.append(rect(stm_x, col_y, col_w, col_h,
                      fill=STM_FILL, stroke=STM_COL, sw=2, rx=8))
    parts.append(text(col_xs[2], col_y + 20,
                      "hal_stm32.cpp", size=12, bold=True, color=STM_COL))
    parts.append(fitbox(stm_x + 8, col_y + 32, col_w - 16, 22,
                        "#if defined(ARDUINO_ARCH_STM32)",
                        size=9, fill="#c8d8f0", stroke=STM_COL, sw=1, rx=3))
    parts.append(text(col_xs[2], col_y + 74,
                      "HAL_GPIO_WritePin(...)", size=9, color=STM_COL))
    parts.append(text(col_xs[2], col_y + 90,
                      "HAL_UART_Transmit(...)", size=9, color=STM_COL))
    parts.append(text(col_xs[2], col_y + 106,
                      "HAL_Delay(ms)", size=9, color=STM_COL))
    parts.append(text(col_xs[2], col_y + 122,
                      "HAL_GetTick()", size=9, color=STM_COL))
    parts.append(text(col_xs[2], col_y + 142,
                      "ST вендорський HAL (§4.11.4)", size=9, color=MUTED, italic=True))

    # ── Висновок-підпис унизу ────────────────────────────────────────────────
    cap = ("Широке зверху й знизу, вузьке посередині: зміна чипа чіпає лише нижній ярус — "
           "верхній (app.cpp) незмінний.")
    parts.append(text(W // 2, H - 8, cap, size=10, color=MUTED))

    render(os.path.join(OUT, "fig-r11-s7a-1-hal-waist.svg"), W, H, *parts)
    print("OK fig-r11-s7a-1-hal-waist.svg")


if __name__ == "__main__":
    fig1_hal_waist()
    print("Done: SVG figure saved to ./img/")
