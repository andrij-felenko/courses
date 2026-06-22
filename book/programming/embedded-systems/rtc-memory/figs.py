# -*- coding: utf-8 -*-
"""Фігури до теми «RTC-пам'ять».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

DIE = ("#fdecea", "#c0392b")   # гине — гаряче/червоне
LIVE = ("#eafaf1", "#27ae60")   # живе — зелене (RTC-домен)


# ── Що переживає deep-sleep: SRAM гине, RTC-домен живе ───────────────────────
def fig_what_survives():
    W, H = 720, 360
    title = "Що переживає deep-sleep: SRAM гине, RTC-пам'ять живе"

    die = ["Звичайна SRAM (~520 КБ)", "Регістри периферії", "Стан Wi-Fi / BLE",
           "Усі глобальні змінні", "Стек, купа, стан задач"]
    live = ["RTC SLOW пам'ять (~8 КБ)", "RTC FAST пам'ять (~8 КБ)", "RTC-таймер / будильник",
            "RTC-GPIO (підмножина)", "ULP-співпроцесор"]

    f = [text(W / 2, 26, title, size=17, bold=True)]
    top, rh = 45, 34
    # шапки колонок
    f.append(rect(20, top, 310, 46, fill=DIE[0], stroke=DIE[1], sw=2.5))
    f.append(text(175, top + 28, "ГИНЕ в deep-sleep", size=14, color=DIE[1], bold=True))
    f.append(rect(380, top, 310, 46, fill=LIVE[0], stroke=LIVE[1], sw=2.5))
    f.append(text(535, top + 28, "ЖИВЕ в deep-sleep (RTC-домен)", size=13, color=LIVE[1], bold=True))
    # рядки
    ry = top + 60
    for i, (d, l) in enumerate(zip(die, live)):
        y = ry + i * (rh + 4)
        f.append(rect(20, y, 310, rh, fill=DIE[0], stroke=DIE[1], sw=1.2))
        f.append(text(175, y + 21, d, size=12))
        f.append(rect(380, y, 310, rh, fill=LIVE[0], stroke=LIVE[1], sw=1.2))
        f.append(text(535, y + 21, l, size=12))
    # підсумкові смужки
    by = ry + len(die) * (rh + 4) + 6
    f.append(rect(20, by, 310, 36, fill=DIE[0], stroke=DIE[1], sw=2.0))
    f.append(text(175, by + 22, "→ після пробудження = старт із app_main()", size=11, color=DIE[1], bold=True))
    f.append(rect(380, by, 310, 36, fill=LIVE[0], stroke=LIVE[1], sw=2.0))
    f.append(text(535, by + 22, "RTC_DATA_ATTR → кладемо «спомин» сюди", size=12, color=LIVE[1], bold=True))
    # розділова лінія
    f.append(line(360, top, 360, by + 36, color=MUTED, sw=1.5, dash="6,4"))
    render(os.path.join(IMG, "what-survives-deepsleep.svg"), W, H, *f)


# ── Патерн пробудження: серія реінкарнацій, зшитих RTC-пам'яттю ──────────────
def fig_wake_flow():
    W, H = 680, 500
    title = "Патерн пробудження: серія коротких реінкарнацій, зшитих RTC-пам'яттю"

    cx = 340
    f = [text(W / 2, 26, title, size=16, bold=True)]

    box, bw, bh = textbox(cx, 55, "boot → app_main()", size=13, fill="#f0f0f0",
                          stroke=LINE, sw=2.0, bold=True)
    f.append(box)
    f.append(arrow(cx, 55 + bh / 2, cx, 110, sw=2.0))

    f.append(fitbox(cx - 114, 110, 228, 50, "esp_sleep_get_wakeup_cause()\n(дізнатись причину)",
                    size=13, color=NEG, fill="#d6eaf8", stroke=NEG, sw=2.0))
    f.append(arrow(cx, 160, cx, 193, sw=2.0))

    # ромб «зі сну?»
    f.append('<polygon points="%d,196 %d,218 %d,240 %d,218" fill="#fef9e7" stroke="#f39c12" stroke-width="2"/>'
             % (cx, cx + 90, cx, cx - 90))
    f.append(text(cx, 223, "зі сну?", size=13, color="#e67e22", bold=True))

    # гілка ТАК — вниз
    f.append(text(cx + 10, 258, "ТАК", size=12, color=LIVE[1], anchor="start", bold=True))
    f.append(arrow(cx, 240, cx, 272, color=LIVE[1], sw=2.0))
    f.append(fitbox(cx - 103, 275, 206, 50, "Читати RTC-стан\n(лічильник, виміри, стан)",
                    size=13, color=LIVE[1], fill=LIVE[0], stroke=LIVE[1], sw=2.0))
    f.append(arrow(cx, 325, cx, 358, color=LIVE[1], sw=2.0))
    f.append(fitbox(cx - 92, 361, 184, 50, "Доробити роботу\n(передати, якщо треба)",
                    size=13, color=LIVE[1], fill=LIVE[0], stroke=LIVE[1], sw=2.0))
    f.append(arrow(cx, 411, cx, 444, color=LIVE[1], sw=2.0))
    f.append(fitbox(cx - 107, 447, 214, 50, "Оновити RTC-стан\n→ esp_deep_sleep_start()",
                    size=13, color=NEG, fill="#d6eaf8", stroke=NEG, sw=2.0, bold=True))

    # кільце «наступне прокидання»
    f.append(line(520, 472, 520, 40, color=LIVE[1], sw=1.8))
    f.append(line(520, 40, 412, 40, color=LIVE[1], sw=1.8))
    f.append(arrow(412, 40, 408, 44, color=LIVE[1], sw=1.8))
    f.append(mtext(528, 250, "наступне\nпрокидання", size=10, color=LIVE[1], anchor="start"))

    # гілка НІ — ліворуч
    f.append(text(cx - 100, 213, "НІ", size=12, color=POS, anchor="end", bold=True))
    f.append(arrow(cx - 90, 218, 200, 218, color=POS, sw=2.0))
    f.append(fitbox(40, 196, 160, 44, "Холодний старт:\nініт RTC-стану з нуля",
                    size=12, color=POS, fill=POS and DIE[0], stroke=POS, sw=2.0))

    render(os.path.join(IMG, "wake-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_what_survives()
    fig_wake_flow()
    print("OK: what-survives-deepsleep.svg, wake-flow.svg")
