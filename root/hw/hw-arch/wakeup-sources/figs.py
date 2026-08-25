# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Джерела пробудження» та вставки comp-wake-hw.
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Запуск:  python figs.py   → пише SVG у ./img/"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори чотирьох джерел, узгоджені з палітрою svgkit
TMR = ("#fdf2e9", "#e67e22")   # таймер
EXT = ("#e8f8f7", "#1a7a73")   # GPIO / ext
TCH = ("#f5eef8", "#8e44ad")   # дотик
ULP = ("#eafaf1", "#27ae60")   # ULP


# ── Карта чотирьох джерел навколо сплячого чипа і їхня ціна ───────────────────
# Серце статті: кожне джерело тримає щось живим уві сні й додає до струму.
# Таймер — підлога deep-sleep (≈10 мкА); touch і ULP помітно дорожчі.
def fig_wakeup_sources():
    W, H = 760, 390
    f = [text(W / 2, 26, "Чотири джерела пробудження з deep-sleep і їхня ціна", size=16, bold=True)]

    # сплячий чип у центрі
    cx, cy = 380, 185
    f.append(rect(cx - 68, cy - 32, 136, 64, fill="#d6eaf8", stroke=NEG, sw=2.5))
    f.append(mtext(cx, cy - 4, ["Сплячий чип", "(deep-sleep)"], size=14, color=NEG, bold=True))

    # чотири джерела по кутах: (підпис, що тримає живим + струм, опис, кольори, координати, бік)
    src = [
        ("① ТАЙМЕР\n(RTC timer)",   "RTC-таймер  ≈10 мкА",   "Давач раз на N хв",   TMR, (145, 95),  "L"),
        ("② GPIO / ext\n(ext0/ext1)", "RTC-GPIO  +1–5 мкА",   "Кнопка, INT давача",  EXT, (615, 95),  "R"),
        ("③ ДОТИК\n(touch pad)",     "Ємнісний сканер  +~150 мкА", "Кнопка без механіки", TCH, (145, 270), "L"),
        ("④ ULP\n(co-processor)",    "ULP + RTC-АЦП  +~100 мкА", "Поріг сигналу в сні", ULP, (615, 270), "R"),
    ]
    for name, cost, desc, (fill, stroke), (bx, by), side in src:
        f.append(rect(bx - 56, by - 24, 112, 48, fill=fill, stroke=stroke, sw=2.0))
        f.append(mtext(bx, by - 6, name.split("\n"), size=12, color=stroke, bold=True))
        f.append(text(bx, by + 46, cost, size=10, color=stroke))
        f.append(text(bx, by + 60, desc, size=10, color=MUTED))
        # стрілка від джерела до чипа
        tx = cx - 70 if side == "L" else cx + 70
        ty = cy - 30 if by < cy else cy + 30
        f.append(arrow(bx, by, tx, ty, color=stroke, sw=1.8))

    box, bw, bh = textbox(W / 2, H - 22,
                          "Можна ввімкнути кілька джерел разом; після пробудження прошивка питає ПРИЧИНУ — esp_sleep_get_wakeup_cause()",
                          size=11, pad=8, fill="#f0f0f0", stroke=MUTED, sw=1.2)
    f.append(box)
    render(os.path.join(IMG, "wakeup-sources.svg"), W, H, *f)


# ── RTC-GPIO проти звичайних GPIO: хто будить з deep-sleep ────────────────────
# Практична пастка розведення: лише RTC-GPIO зберігають здатність будити;
# номери пінів — з документації ESP32 (0, 2, 4, 12–15, 25–27, 32–39).
def fig_rtc_gpio_pins():
    W, H = 680, 348
    f = [text(W / 2, 26, "RTC-GPIO будять з deep-sleep; решта пінів у deep-sleep мертва", size=15, bold=True)]

    # ліва колонка — RTC-GPIO (можуть будити)
    f.append(rect(30, 48, 280, 46, fill="#eafaf1", stroke=FIELD, sw=2.5))
    f.append(text(170, 76, "RTC-GPIO (можуть будити)", size=13, color=FIELD, bold=True))
    left = ["GPIO0, GPIO2, GPIO4", "GPIO12–15", "GPIO25–27", "GPIO32–39",
            "(це RTC_GPIO-домен ESP32)"]
    y = 104
    for s in left:
        f.append(rect(30, y, 280, 28, fill="#eafaf1", stroke=FIELD, sw=1.2))
        f.append(text(170, y + 19, s, size=11, color=INK))
        y += 32
    f.append(rect(30, y + 4, 280, 32, fill="#eafaf1", stroke=FIELD, sw=2.0))
    f.append(text(170, y + 25, "INT давача → мусить бути тут!", size=12, color=FIELD, bold=True))

    # роздільник
    f.append(line(340, 42, 340, 320, color=MUTED, sw=1.5, dash="6,4"))

    # права колонка — звичайні GPIO (мертві)
    f.append(rect(360, 48, 280, 46, fill="#fdecea", stroke=POS, sw=2.5))
    f.append(text(500, 76, "Звичайні GPIO — мертві в deep-sleep", size=12, color=POS, bold=True))
    right = ["GPIO5–11 (SPI-флеш)", "GPIO16–24", "GPIO28–31", "...більшість пінів",
             "логіка периферії знеструмлена"]
    y = 104
    for s in right:
        f.append(rect(360, y, 280, 28, fill="#fdecea", stroke=POS, sw=1.2))
        f.append(text(500, y + 19, s, size=11, color=MUTED))
        y += 32
    f.append(rect(360, y + 4, 280, 32, fill="#fdecea", stroke=POS, sw=2.0))
    f.append(text(500, y + 25, "INT сюди — не прокинешся!", size=12, color=POS, bold=True))

    render(os.path.join(IMG, "rtc-gpio-pins.svg"), W, H, *f)


# ═════════════════════════════════════════════════════════════════════════════
#  Фігури вставки comp-wake-hw (🔌)
# ═════════════════════════════════════════════════════════════════════════════

# ── Родина зовнішніх помічників сну: де сидить кожен між батареєю і вузлом ─────
def fig_wake_hw_family():
    W, H = 800, 380
    f = [text(W / 2, 26, "Три зовнішні помічники сну: де сидить кожен у колі живлення", size=15, bold=True)]

    # батарея ліворуч
    bx, by = 60, H / 2 - 28
    f.append(rect(bx, by, 92, 56, fill="#d6eaf8", stroke=NEG, sw=2.5))
    f.append(mtext(bx + 46, by + 23, ["Батарея", "3.7 В"], size=12, color=NEG, bold=True))

    # шина живлення
    f.append(line(bx + 92, H / 2, 250, H / 2, color=FIELD, sw=3))

    # 1) кнопка-защіпка тримає живлення самого ESP32
    f.append(rect(250, H / 2 - 70, 150, 46, fill="#fdecea", stroke=POS, sw=2.0))
    f.append(mtext(325, H / 2 - 52, ["③ Кнопка-защіпка", "рве живлення ESP32 → 0"], size=11, color=POS, bold=True))
    f.append(arrow(325, H / 2 - 24, 325, H / 2 - 6, color=POS, sw=1.8))

    # ESP32 у центрі
    ex, ey = 250, H / 2 - 4
    f.append(rect(ex, ey, 150, 60, fill="#f8f9fa", stroke=INK, sw=2))
    f.append(text(ex + 75, ey + 25, "ESP32", size=14, color=INK, bold=True))
    f.append(text(ex + 75, ey + 44, "(спить найглибше)", size=10, color=MUTED))

    # 1) RTC з alarm-виходом смикає wake-пін
    f.append(rect(470, 70, 150, 56, fill="#eafaf1", stroke=FIELD, sw=2.0))
    f.append(mtext(545, 92, ["① RTC + alarm", "wake за розкладом", "мкА / нА"], size=11, color=FIELD, bold=True))
    f.append(arrow(470, 98, ex + 152, ey + 12, color=FIELD, sw=1.8))
    f.append(text(450, 92, "I²C", size=9, color=MUTED))

    # 2) load switch вимикає живлення цілому вузлу
    f.append(line(ex + 150, ey + 40, 470, ey + 40, color=FIELD, sw=2.5))
    f.append(rect(470, ey + 18, 150, 44, fill="#fdf2e9", stroke="#e67e22", sw=2.0))
    f.append(mtext(545, ey + 36, ["② Load switch", "вимикає вузол → 0"], size=11, color="#e67e22", bold=True))
    f.append(line(620, ey + 40, 660, ey + 40, color="#e67e22", sw=2.5))
    f.append(rect(660, ey + 18, 110, 44, fill="#f1f3f5", stroke=MUTED, sw=1.5))
    f.append(mtext(715, ey + 36, ["давач / SD /", "радіо"], size=10, color=MUTED))
    f.append(arrow(545, ey + 18, 545, ey + 6, color="#e67e22", sw=1.6))
    f.append(text(545, ey + 4, "EN ← GPIO", size=9, color="#e67e22"))

    box, bw, bh = textbox(W / 2, H - 22,
                          "Земля спільна — керують лише плюсом. RTC будить за часом; load switch гасить вузол; защіпка гасить весь ESP32",
                          size=11, pad=8, fill="#f0f0f0", stroke=MUTED, sw=1.2)
    f.append(box)
    render(os.path.join(IMG, "wake-hw-family.svg"), W, H, *f)


# ── Кнопка-защіпка (soft-latch): натиск вмикає, ESP32 сам тримає, зняття гасить ─
def fig_wake_hw_soft_latch():
    W, H = 760, 400
    f = [text(W / 2, 26, "Кнопка-защіпка живлення: пристрій вимикає сам себе в нуль", size=15, bold=True)]

    # живлення згори
    f.append(text(80, 72, "+VBAT", size=13, color=POS, bold=True))
    f.append(line(80, 80, 80, 130, color=POS, sw=3))
    f.append(line(80, 90, 360, 90, color=POS, sw=3))

    # P-MOSFET у верхньому плечі
    f.append(rect(330, 110, 110, 60, fill="#fdf2e9", stroke="#e67e22", sw=2.0))
    f.append(mtext(385, 132, ["P-MOSFET", "(верхнє плече)"], size=11, color="#e67e22", bold=True))
    f.append(line(385, 90, 385, 110, color=POS, sw=3))

    # вихід живлення на ESP32
    f.append(line(385, 170, 385, 210, color=FIELD, sw=3))
    f.append(rect(310, 210, 150, 64, fill="#f8f9fa", stroke=INK, sw=2))
    f.append(text(385, 234, "ESP32", size=14, color=INK, bold=True))
    f.append(text(385, 254, "VDD", size=10, color=MUTED))

    # кнопка ліворуч: на мить відкриває MOSFET
    f.append(rect(90, 120, 150, 44, fill="#eafaf1", stroke=FIELD, sw=2.0))
    f.append(mtext(165, 138, ["КНОПКА", "натиск на мить"], size=11, color=FIELD, bold=True))
    f.append(arrow(240, 135, 328, 135, color=FIELD, sw=1.8))
    f.append(text(284, 126, "вмикає", size=9, color=FIELD))

    # HOLD: GPIO утримує затвор
    f.append(rect(470, 120, 170, 44, fill="#d6eaf8", stroke=NEG, sw=2.0))
    f.append(mtext(555, 138, ["HOLD = GPIO OUT", "першим рядком HIGH"], size=11, color=NEG, bold=True))
    f.append(arrow(470, 140, 442, 140, color=NEG, sw=1.8))
    f.append(text(456, 156, "тримає", size=9, color=NEG))
    f.append(line(555, 164, 555, 222, color=NEG, sw=1.6, dash="4,3"))
    f.append(arrow(555, 222, 462, 234, color=NEG, sw=1.4))

    # KEY-READ: та сама кнопка читається як вхід
    f.append(rect(470, 240, 170, 44, fill="#f5eef8", stroke="#8e44ad", sw=2.0))
    f.append(mtext(555, 258, ["KEY-READ = GPIO IN", "команда «вимкнись»"], size=11, color="#8e44ad", bold=True))
    f.append(arrow(470, 262, 462, 256, color="#8e44ad", sw=1.4))

    box, bw, bh = textbox(W / 2, H - 30,
                          ["HOLD=HIGH першим рядком — інакше відпустять кнопку і чип згасне на старті.",
                           "HOLD=LOW рве живлення: струм = 0, повний cold-boot при наступному ввімкненні."],
                          size=11, pad=9, fill="#fff3cd", stroke="#e67e22", sw=1.5, bold=True)
    f.append(box)
    render(os.path.join(IMG, "wake-hw-soft-latch.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wakeup_sources()
    fig_rtc_gpio_pins()
    fig_wake_hw_family()
    fig_wake_hw_soft_latch()
    print("OK: wakeup-sources, rtc-gpio-pins, wake-hw-family, wake-hw-soft-latch")
