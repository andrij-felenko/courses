# -*- coding: utf-8 -*-
"""Фігури до теми «RTC і реальний час» та її вставок (hist-, math-).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Стаття ───────────────────────────────────────────────────────────────────

def fig_two_clocks():
    W, H = 820, 300
    f = [text(W / 2, 30, "Дві різні «годинники»: секундомір і справжній", size=16, bold=True)]

    # millis — секундомір
    f.append(rect(60, 70, 330, 170, fill="#e9eefb", stroke=NEG, sw=2))
    f.append(text(225, 96, "millis() — секундомір", size=12.5, bold=True, color=NEG))
    f.append(text(225, 120, "рахує від увімкнення:", size=10.5))
    f.append(text(225, 144, "0 → 1 → 2 … мс", size=13, bold=True))
    f.append(text(225, 176, "вимкнули живлення →", size=10.5, color=POS))
    f.append(text(225, 196, "скид у 0, історію стерто", size=11, bold=True, color=POS))
    f.append(text(225, 224, "«скільки я працюю»", size=10, color=MUTED, italic=True))

    # RTC — справжній годинник
    f.append(rect(430, 70, 330, 170, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(595, 96, "RTC — справжній годинник", size=12.5, bold=True, color=FIELD))
    f.append(text(595, 120, "знає календарну дату й час:", size=10.5))
    f.append(text(595, 146, "2026-06-11  14:30:00", size=13, bold=True))
    f.append(text(595, 178, "йде далі навіть уві сні", size=11, bold=True, color=FIELD))
    f.append(text(595, 198, "й переживає вимкнення", size=10.5))
    f.append(text(595, 224, "«котра зараз година у світі»", size=10, color=MUTED, italic=True))

    f.append(fitbox(60, H - 46, W - 120, 34,
                    "millis відповідає «скільки часу працюю»; RTC — «який зараз момент насправді».",
                    size=11.5, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "two-clocks.svg"), W, H, *f)


def fig_epoch():
    W, H = 820, 270
    f = [text(W / 2, 30, "Як машина зберігає час: один великий лічильник (epoch)", size=15.5, bold=True)]

    f.append(rect(70, 84, 300, 80, fill="#fff6e0", stroke="#caa24a", sw=2))
    f.append(text(220, 120, "1 749 645 000", size=21, bold=True, color="#8a6d1a"))
    f.append(text(220, 148, "секунд від 1970-01-01 (UTC)", size=10, color=MUTED))

    f.append(arrow(380, 116, 450, 116, color=INK, sw=2.2))
    f.append(text(415, 104, "переклад", size=9.5, color=MUTED))
    f.append(arrow(450, 140, 380, 140, color=MUTED, sw=2))

    f.append(rect(450, 84, 300, 80, fill="#e9eefb", stroke=NEG, sw=2))
    f.append(text(600, 118, "2026-06-11", size=16, bold=True, color=NEG))
    f.append(text(600, 144, "14:30:00", size=14, bold=True))

    f.append(fitbox(90, H - 64, W - 180, 50,
                    ["Одне число легко зберігати, порівнювати й віднімати (скільки минуло).",
                     "У дату-годинник його переводять лише для показу."],
                    size=11, fill=FILL, stroke=MUTED))
    render(os.path.join(IMG, "epoch.svg"), W, H, *f)


def fig_sleeps():
    W, H = 820, 270
    f = [text(W / 2, 30, "Годинник, що йде уві сні", size=17, bold=True)]

    # сплячий пристрій
    f.append(rect(70, 80, 300, 150, fill="#f0f0f0", stroke=MUTED, sw=2))
    f.append(text(220, 116, "ESP32", size=14, bold=True, color=MUTED))
    f.append(text(220, 142, "спить / знеструмлено", size=11, color=MUTED))
    f.append(text(220, 180, "zzz…", size=14, color=MUTED, italic=True))

    # годинник іде
    f.append(circle(520, 150, 44, fill="#eef6ef", stroke=FIELD, sw=2.4))
    f.append(line(520, 150, 520, 122, color=FIELD, sw=2.6))
    f.append(line(520, 150, 540, 160, color=FIELD, sw=2.6))
    f.append(text(520, 214, "RTC цок-цок…", size=11, bold=True, color=FIELD))

    # батарейка
    f.append(rect(620, 128, 110, 44, fill="#fff6e0", stroke="#caa24a", sw=1.8))
    f.append(text(675, 148, "CR2032", size=11, bold=True, color="#8a6d1a"))
    f.append(text(675, 164, "≈3 мкА", size=9.5, color=MUTED))
    f.append(line(564, 150, 620, 150, color="#caa24a", sw=2))

    f.append(fitbox(70, H - 40, W - 140, 30,
                    "Крихітна батарейка живить лише годинник — і час іде, поки решта спить чи знеструмлена.",
                    size=11.5, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "sleeps.svg"), W, H, *f)


def fig_internal_external():
    W, H = 840, 300
    f = [text(W / 2, 30, "Внутрішній RTC ESP32 проти зовнішнього модуля", size=16, bold=True)]

    # внутрішній
    f.append(rect(60, 70, 360, 180, fill="#fff6e0", stroke="#caa24a", sw=2))
    f.append(text(240, 96, "Внутрішній RTC ESP32", size=12.5, bold=True, color="#8a6d1a"))
    f.append(text(82, 128, "іде в глибокому сні ✓", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(82, 156, "без батарейки → втрачає час", size=11, color=POS, anchor="start"))
    f.append(text(82, 178, "   при повному вимкненні", size=11, color=POS, anchor="start"))
    f.append(text(82, 210, "помітний дрейф ✗", size=11, color=POS, anchor="start"))

    # зовнішній
    f.append(rect(450, 70, 330, 180, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(615, 96, "Зовнішній DS3231", size=12.5, bold=True, color=FIELD))
    f.append(text(470, 128, "власна батарейка → роки ходу ✓", size=10.5, anchor="start"))
    f.append(text(470, 152, "термокомпенсація → ±2 ppm ✓", size=10.5, anchor="start"))
    f.append(text(470, 176, "є alarm-вихід (будить за часом)", size=10.5, anchor="start"))
    f.append(text(470, 200, "трохи деталей і місця — ціна", size=10.5, anchor="start"))

    f.append(fitbox(60, H - 40, W - 120, 30,
                    "Точний, тривкий час — бери зовнішній DS3231; досить пережити сон — вистачить внутрішнього.",
                    size=11, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "internal-external.svg"), W, H, *f)


def fig_drift():
    W, H = 840, 280
    f = [text(W / 2, 30, "Дрейф: кожен годинник бреше потроху", size=17, bold=True)]
    f.append(text(W / 2, 52, "невелика похибка ходу накопичується — час поволі «розходиться» зі справжнім",
                  size=10, color=MUTED, italic=True))

    # лінії істина / дрейф
    f.append(line(90, 140, 760, 140, color=FIELD, sw=2))
    f.append(text(74, 144, "істина", size=9.5, bold=True, color=FIELD, anchor="end"))
    f.append('<polyline points="90,140 760,104" fill="none" stroke="%s" stroke-width="2"/>' % POS)
    f.append(text(774, 104, "дрейф", size=9.5, bold=True, color=POS, anchor="start"))

    f.append(text(W / 2, 180, "дешевий RTC ~20 ppm ≈ 1.7 с/добу ≈ ~1 хв/місяць", size=11))
    f.append(text(W / 2, 202, "DS3231 ~2 ppm ≈ кілька секунд/місяць", size=11, bold=True, color=FIELD))

    f.append(fitbox(150, H - 42, W - 300, 32,
                    "Похибка накопичується з часом — тому годинник час від часу треба звіряти.",
                    size=10.5, fill="#fff6e0", stroke="#caa24a"))
    render(os.path.join(IMG, "drift.svg"), W, H, *f)


def fig_sync():
    W, H = 820, 270
    f = [text(W / 2, 30, "Синхронізація: звіряти з еталоном", size=17, bold=True)]

    f.append(rect(60, 92, 150, 70, fill="#e9eefb", stroke=NEG, sw=2))
    f.append(text(135, 122, "ESP32", size=12, bold=True, color=NEG))
    f.append(text(135, 144, "годинник дрейфнув", size=9, color=POS))

    f.append(arrow(210, 122, 340, 122, color=FIELD, sw=2.4))
    f.append(text(275, 110, "Wi-Fi", size=9.5, bold=True, color=FIELD))

    f.append(rect(340, 92, 200, 70, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(text(440, 120, "NTP-сервер", size=12, bold=True, color=FIELD))
    f.append(text(440, 142, "еталонний UTC", size=9.5, color=MUTED))
    f.append(arrow(540, 150, 210, 150, color=INK, sw=2))

    f.append(text(700, 112, "так само вміють", size=9, color=MUTED))
    f.append(text(700, 130, "GPS і радіосигнал", size=10, bold=True))
    f.append(text(700, 148, "точного часу", size=9, color=MUTED))

    f.append(fitbox(90, H - 58, W - 180, 44,
                    ["↑ повертає точний UTC — накопичений дрейф обнуляється.",
                     "Періодично беремо час із мережі й виставляємо годинник наново."],
                    size=11, fill=FILL, stroke=MUTED))
    render(os.path.join(IMG, "sync.svg"), W, H, *f)


# ── Вставка comp-rtc-module ──────────────────────────────────────────────────

def fig_rtc_module():
    W, H = 820, 300
    f = [text(W / 2, 30, "Зовнішній RTC-модуль: що на платі й що назовні", size=16, bold=True)]

    # плата
    f.append(rect(70, 70, 360, 180, fill="#fbfbff", stroke=INK, sw=1.8))
    f.append(text(250, 92, "плата RTC-модуля", size=11, bold=True, color=MUTED))
    # чип
    f.append(rect(100, 110, 110, 56, fill="#e9eefb", stroke=NEG, sw=1.6))
    f.append(text(155, 134, "чип RTC", size=11, bold=True, color=NEG))
    f.append(text(155, 152, "+ датчик t°", size=9, color=MUTED))
    # кварц
    f.append(rect(100, 184, 110, 40, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(text(155, 202, "кварц", size=10, bold=True, color=FIELD))
    f.append(text(155, 217, "32 768 Гц", size=9.5))
    # батарейка
    f.append(circle(330, 150, 40, fill="#fff6e0", stroke="#caa24a", sw=1.8))
    f.append(text(330, 146, "CR2032", size=10.5, bold=True, color="#8a6d1a"))
    f.append(text(330, 164, "3 В", size=9.5, color=MUTED))
    f.append(text(330, 210, "живить лише годинник", size=9, color=MUTED))

    # виводи назовні
    pins = [("VCC", "3.3 В"), ("GND", "земля"), ("SDA", "дані I²C"),
            ("SCL", "такт I²C"), ("SQW/INT", "будильник")]
    x = 470
    f.append(text(x, 92, "виводи назовні:", size=11, bold=True, anchor="start"))
    for i, (p, d) in enumerate(pins):
        y = 116 + i * 28
        col = MUTED if i == 4 else INK
        f.append(text(x, y, "•", size=12, color=NEG, anchor="start"))
        f.append(text(x + 16, y, p, size=11, bold=True, color=col, anchor="start"))
        f.append(text(x + 110, y, d, size=10, color=MUTED, anchor="start"))
    f.append(text(x, 116 + 4 * 28 + 16, "(SQW/INT — необов'язковий)", size=9, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "rtc-module.svg"), W, H, *f)


# ── Вставка hist-y2k-2038 ────────────────────────────────────────────────────

def fig_y2k():
    W, H = 840, 280
    f = [text(W / 2, 30, "Y2K: дві цифри, що заощадили — і бабахнули", size=16.5, bold=True)]
    f.append(text(W / 2, 52, "рік зберігали двома цифрами заради дорогоцінної пам'яті",
                  size=10, color=MUTED, italic=True))

    f.append(rect(60, 84, 200, 70, fill="#e9eefb", stroke=NEG, sw=1.8))
    f.append(text(160, 114, "рік = «99»", size=14, bold=True, color=NEG))
    f.append(text(160, 136, "(тобто 1999)", size=9.5, color=MUTED))

    f.append(arrow(260, 119, 320, 119, color=INK, sw=2.4))
    f.append(text(290, 107, "2000", size=9, color=INK))

    f.append(rect(320, 84, 210, 70, fill="#fbecec", stroke=POS, sw=1.8))
    f.append(text(425, 112, "рік = «00»", size=14, bold=True, color=POS))
    f.append(text(425, 134, "комп'ютер читає 1900!", size=9.5, bold=True, color=POS))

    f.append(arrow(530, 119, 590, 119, color=POS, sw=2.2))
    f.append(rect(590, 84, 250, 70, fill=FILL, stroke=POS, sw=1.6))
    f.append(text(715, 110, "арифметика дат ламається", size=10, bold=True))
    f.append(text(715, 132, "(вік, тривалості, рахунки)", size=9, color=MUTED))

    f.append(fitbox(60, H - 78, W - 120, 64,
                    ["Скорочення «викинути 19» заощаджувало байти на мільярдах записів —",
                     "і клало бомбу сповільненої дії під 2000-й рік.",
                     "Пам'ять колись була такою дорогою, що дві цифри здавалися ощадливістю."],
                    size=10.5, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "y2k.svg"), W, H, *f)


def fig_y2038():
    W, H = 840, 280
    f = [text(W / 2, 30, "2038: годинник самих машин переповнюється", size=16.5, bold=True)]
    f.append(text(W / 2, 52, "знаковий 32-бітний відлік секунд від 1970 дійде до межі",
                  size=10, color=MUTED, italic=True))

    f.append(rect(70, 84, 250, 70, fill="#eef6ef", stroke=FIELD, sw=1.8))
    f.append(text(195, 112, "2 147 483 647", size=14, bold=True, color=FIELD))
    f.append(text(195, 134, "макс. знакового 32-біт", size=9, color=MUTED))

    f.append(arrow(320, 119, 380, 119, color=POS, sw=2.4))
    f.append(text(350, 106, "+1 с", size=9, color=POS))

    f.append(rect(380, 84, 250, 70, fill="#fbecec", stroke=POS, sw=1.8))
    f.append(text(505, 112, "→ від'ємне число", size=13, bold=True, color=POS))
    f.append(text(505, 134, "стрибок у 13 грудня 1901", size=9.5))

    f.append(fitbox(70, H - 96, W - 140, 50,
                    ["Настане це 19 січня 2038, о 03:14:07 UTC.",
                     "Лік: 64-бітний time_t — переповнення відсувається на ~292 млрд років."],
                    size=11, fill=FILL, stroke=MUTED))
    f.append(fitbox(150, H - 40, W - 300, 30,
                    "Найважче полагодити вбудовані й застарілі 32-бітні системи.",
                    size=10, fill="#fff6e0", stroke="#caa24a"))
    render(os.path.join(IMG, "y2038.svg"), W, H, *f)


def fig_same_bug():
    W, H = 840, 270
    f = [text(W / 2, 30, "Той самий баг — різний масштаб", size=17, bold=True)]

    rows = [("millis()", "32-біт мілісекунди", "переповнення за 49.7 дня"),
            ("Y2K", "рік двома цифрами", "«переповнення» 2000-го року"),
            ("Y2038", "знаковий 32-біт секунд", "переповнення 2038 року")]
    y0 = 64
    for i, (a, b, c) in enumerate(rows):
        y = y0 + i * 52
        f.append(rect(60, y, 720, 42, fill="#fbfbff", stroke=INK, sw=1.3))
        f.append(text(86, y + 26, a, size=12, bold=True, color=NEG, anchor="start"))
        f.append(text(280, y + 26, b, size=10.5, anchor="start"))
        f.append(text(756, y + 26, c, size=9.6, color=MUTED, anchor="end"))

    f.append(fitbox(60, H - 44, W - 120, 32,
                    "Лічильник завжди скінченний. Ліки скрізь одні: достатньо широкий тип і пам'ять про оберт.",
                    size=11, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "same-bug.svg"), W, H, *f)


# ── Вставка math-calendar-math ───────────────────────────────────────────────

def fig_peel():
    W, H = 840, 300
    f = [text(W / 2, 30, "Як з epoch дістати дату: «знімаємо шари»", size=16.5, bold=True)]
    f.append(text(W / 2, 52, "одне число секунд розкручують у дату, знімаючи шар за шаром",
                  size=10, color=MUTED, italic=True))

    f.append(rect(50, 80, 190, 46, fill="#fff6e0", stroke="#caa24a", sw=1.8))
    f.append(text(145, 108, "epoch (секунди)", size=11, bold=True, color="#8a6d1a"))
    f.append(arrow(240, 103, 290, 103, color=INK, sw=2.2))
    f.append(text(265, 91, "÷86400", size=9))

    f.append(rect(290, 78, 230, 50, fill="#e9eefb", stroke=NEG, sw=1.8))
    f.append(text(405, 99, "дні від 1970", size=10.5, bold=True, color=NEG))
    f.append(text(405, 117, "+ залишок: секунди в добі", size=9, color=MUTED))

    f.append(line(405, 126, 405, 158, color=MUTED, sw=2))
    f.append(rect(290, 160, 230, 44, fill="#eef6ef", stroke=FIELD, sw=1.6))
    f.append(text(405, 180, "секунди в добі →", size=9.4))
    f.append(text(405, 196, "години : хвилини : секунди", size=9.4, bold=True, color=FIELD))

    f.append(arrow(520, 103, 565, 103, color=MUTED, sw=2.2))
    f.append(rect(565, 80, 270, 124, fill=FILL, stroke=MUTED, sw=1.4))
    f.append(text(700, 104, "дні від 1970 →", size=10, bold=True))
    f.append(text(700, 128, "− роки (365 або 366)", size=9.4))
    f.append(text(700, 150, "− місяці (28/29/30/31)", size=9.4))
    f.append(text(700, 172, "= рік · місяць · день", size=10, bold=True, color=NEG))
    f.append(text(700, 194, "(високосні — складність)", size=9, color=POS))

    f.append(fitbox(60, H - 64, W - 120, 50,
                    ["Секунди → доби й час доби; доби → роки → місяці → день.",
                     "Зворотне переведення — так само, лише в інший бік."],
                    size=10.5, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "peel.svg"), W, H, *f)


def fig_leap():
    W, H = 840, 300
    f = [text(W / 2, 30, "Високосний рік: правило ÷4, ÷100, ÷400", size=17, bold=True)]

    f.append(rect(70, 64, 700, 92, fill="#fbfbff", stroke=INK, sw=1.6))
    f.append(text(420, 90, "рік ділиться на 4  →  високосний (29 днів у лютому)…",
                  size=11, bold=True, color=FIELD))
    f.append(text(420, 114, "…АЛЕ ділиться на 100  →  НЕ високосний…",
                  size=11, bold=True, color=POS))
    f.append(text(420, 138, "…АЛЕ ділиться на 400  →  таки високосний.",
                  size=11, bold=True, color=FIELD))

    cards = [(90, "2024  (÷4)", "✓ високосний", "#eef6ef", FIELD),
             (330, "1900  (÷100, не ÷400)", "✗ звичайний", "#fbecec", POS),
             (570, "2000  (÷400)", "✓ високосний", "#eef6ef", FIELD)]
    for x, top, bot, fill, col in cards:
        f.append(rect(x, 178, 200, 64, fill=fill, stroke=col, sw=1.8))
        f.append(text(x + 100, 202, top, size=10.5, bold=True))
        f.append(text(x + 100, 226, bot, size=11, bold=True, color=col))

    f.append(fitbox(60, H - 42, W - 120, 32,
                    "Лютий має 29 днів лише у високосний — через це конвертація й заплутана. Пояси й літній час іще гірші.",
                    size=10, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, "leap.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_clocks(); fig_epoch(); fig_sleeps(); fig_internal_external()
    fig_drift(); fig_sync(); fig_rtc_module()
    fig_y2k(); fig_y2038(); fig_same_bug()
    fig_peel(); fig_leap()
    print("OK: 12 фігур у", IMG)
