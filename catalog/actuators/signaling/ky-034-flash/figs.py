# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-034 — 7-кольоровий миготливий LED».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

R_COL = "#c0392b"   # червоний кристал
G_COL = "#27ae60"   # зелений кристал
B_COL = "#2457d6"   # синій кристал


# ── 1. Внутрішня схема: RGB-LED із вбудованою мікросхемою + струмообмежувальний резистор ──
def fig_ky034_schematic():
    W, H = 960, 500
    f = [text(W / 2, 30, "Що всередині KY-034: RGB-світлодіод із вбудованою мікросхемою-генератором",
              size=15, bold=True)]

    # межа плати
    bx, by, bw, bh = 80, 66, 800, 316
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 22, "плата KY-034", size=11, bold=True, color=MUTED, anchor="start"))

    # шини живлення й землі
    vcc_y = by + 60
    gnd_y = by + bh - 46
    f.append(line(bx + 40, vcc_y, bx + bw - 40, vcc_y, color=POS, sw=2.2))
    f.append(text(bx + 40, vcc_y - 10, "плюс — приходить на штир S (3.3–5 В)", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(bx + 40, gnd_y, bx + bw - 40, gnd_y, color=NEG, sw=2.2))
    f.append(text(bx + 40, gnd_y + 24, "−  (мінус; середній штир повторює його)", size=11, bold=True, color=NEG, anchor="start"))

    chain_x = bx + bw * 0.30    # вертикаль, де стоїть резистор + LED

    # струмообмежувальний резистор від VCC
    f.append(line(chain_x, vcc_y, chain_x, vcc_y + 34, color=INK, sw=1.8))
    f.append(rect(chain_x - 20, vcc_y + 34, 40, 34, fill=BG, stroke=INK, sw=1.7, rx=3))
    f.append(text(chain_x + 30, vcc_y + 55, "R — струмообмежувальний", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(chain_x + 30, vcc_y + 71, "(сотні Ом; бере зайву напругу)", size=9.5, color=MUTED, anchor="start"))
    f.append(line(chain_x, vcc_y + 68, chain_x, vcc_y + 96, color=INK, sw=1.8))

    # корпус світлодіода з мікросхемою — велика рамка
    lx, ly, lw, lh = chain_x - 60, vcc_y + 96, 300, 118
    f.append(rect(lx, ly, lw, lh, fill="#fffdf5", stroke=INK, sw=1.8, rx=12))
    f.append(text(lx + lw / 2, ly + 20, "корпус світлодіода (5 мм)", size=10.5, bold=True, color=MUTED))

    # три кристали
    cy = ly + 52
    for i, (col, lab) in enumerate([(R_COL, "R"), (G_COL, "G"), (B_COL, "B")]):
        cx0 = lx + 34 + i * 30
        f.append(circle(cx0, cy, 9, fill=col, stroke=INK, sw=1.2))
        f.append(text(cx0, cy + 4, lab, size=10, bold=True, color="#ffffff"))
    f.append(text(lx + 34 + 30, cy + 26, "три кристали R·G·B", size=9.5, color=MUTED))

    # мікросхема-генератор поряд із кристалами
    icx, icy, icw, ich = lx + 150, ly + 40, 128, 54
    f.append(rect(icx, icy, icw, ich, fill="#eef1f5", stroke=INK, sw=1.5, rx=6))
    f.append(mtext(icx + icw / 2, icy + 22, ["вбудована мікросхема:", "генератор + лічильник", "+ три струмові ключі"],
                   size=9, color=INK))

    # вихід світлодіода до землі
    f.append(line(lx + lw / 2, ly + lh, lx + lw / 2, gnd_y, color=INK, sw=1.8))
    f.append(line(chain_x, ly, lx + lw / 2, ly, color=INK, sw=1.8))

    # висновок унизу
    b, _, _ = textbox(W / 2, 452,
                      "Увесь «мозок» — усередині корпусу LED: власний генератор сам цокає, лічильник перебирає\n"
                      "комбінації яскравостей R·G·B. Назовні — лише живлення й земля; входу для команд немає.",
                      size=11, fill="#fffdf5", stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "ky034-schematic.svg"), W, H, *f)


# ── 2. Підключення пін-у-пін: плюс на S (живлення або цифровий пін), мінус на GND ──
def fig_ky034_wiring():
    W, H = 940, 440
    f = [text(W / 2, 30, "Підключення KY-034: плюс — на крайній S, мінус — на GND; середній штир зайвий",
              size=14.5, bold=True)]

    # модуль
    mx, my, mw, mh = 70, 96, 250, 210
    f.append(rect(mx, my, mw, mh, fill="#fffdf5", stroke=INK, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 28, "KY-034", size=15, bold=True, color=INK))
    f.append(text(mx + mw / 2, my + 48, "самограйний RGB-вогник", size=10, color=MUTED))
    pads = [("S", POS, my + 92, "плюс сюди"),
            ("середній", MUTED, my + 137, "= мінус, не чіпати"),
            ("−", NEG, my + 182, "мінус")]
    for lab, col, py, sub in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=12, bold=True, color=col, anchor="end"))
        f.append(text(mx + mw - 18, py + 19, sub, size=8.5, color=MUTED, anchor="end"))

    # плата
    bx, by, bw, bh = 610, 96, 260, 210
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("цифровий пін", POS, by + 92, "HIGH — світиться, LOW — згас"),
            ("(не підключати)", MUTED, by + 137, ""),
            ("GND", NEG, by + 182, "земля")]
    for lab, col, py, sub in tgts:
        if lab != "(не підключати)":
            f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=11.5, bold=True, color=col, anchor="start"))
        if sub:
            f.append(text(bx + 16, py + 19, sub, size=8.5, color=MUTED, anchor="start"))

    # дроти: S↔пін, −↔GND (середній НЕ з'єднуємо)
    f.append(line(mx + mw + 6, my + 92, bx - 6, by + 92, color=POS, sw=2.4))
    f.append(line(mx + mw + 6, my + 182, bx - 6, by + 182, color=NEG, sw=2.4))
    # позначка «або прямо на живлення»
    f.append(text((mx + mw + bx) / 2, my + 78, "плюс: на цифровий пін АБО прямо на 3.3–5 В",
                  size=9.5, italic=True, color=POS))

    b, _, _ = textbox(W / 2, 384,
                      "Плюс подаєш на крайній S: прямо на живлення — вогник горить завжди; на цифровий пін —\n"
                      "керуєш лише вмиканням (кольором керувати не можна). Середній штир повторює мінус — його лишаємо.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky034-wiring.svg"), W, H, *f)


# ── 3. Спектр кольорових LED: самограйний (KY-034) vs керований RGB vs адресований ──
def fig_led_spectrum():
    W, H = 980, 470
    f = [text(W / 2, 30, "Три різновиди кольорового світлодіода: чим більше керування — тим більше дротів і коду",
              size=14, bold=True)]

    col_w = 300
    xs = [30, 340, 650]
    top = 66
    box_h = 300

    cards = [
        (R_COL, "САМОГРАЙНИЙ  (KY-034)", "#fffdf5", [
            "2 робочі ноги: плюс + мінус",
            "мікросхема ВСЕРЕДИНІ LED",
            "візерунок зашитий на заводі",
            "код: лише ввімк / вимк",
            "колір — НЕ керується",
        ]),
        (G_COL, "КЕРОВАНИЙ RGB  (KY-016)", "#f5fbf7", [
            "4 ноги: R · G · B · спільна",
            "яскравістю кожного каналу",
            "керуєш САМ через ШІМ МК",
            "код: будь-який колір",
            "3 ноги ШІМ на один LED",
        ]),
        (B_COL, "АДРЕСОВАНИЙ  (WS2812…)", "#f4f7fd", [
            "3 ноги: дані · живлення · GND",
            "кожному пікселю — код кольору",
            "по цифровій шині (протокол)",
            "код: точний колір, каскад",
            "сотні пікселів на один пін",
        ]),
    ]

    for x0, (col, title, fill, rows) in zip(xs, cards):
        f.append(rect(x0, top, col_w, box_h, fill=fill, stroke=col, sw=2.2, rx=12))
        f.append(rect(x0, top, col_w, 34, fill=col, stroke=col, sw=0, rx=12))
        f.append(text(x0 + col_w / 2, top + 23, title, size=11.5, bold=True, color="#ffffff"))
        yy = top + 62
        for r in rows:
            f.append(circle(x0 + 22, yy - 4, 3.2, fill=col, stroke=col, sw=1))
            f.append(text(x0 + 36, yy, r, size=10.5, color=INK, anchor="start"))
            yy += 34
        # маркер складності керування знизу картки
        f.append(text(x0 + col_w / 2, top + box_h - 16,
                      "керування кольором: " + ("немає" if col == R_COL else ("повне, вручну" if col == G_COL else "повне, по шині")),
                      size=9.5, italic=True, color=MUTED))

    # стрілка «зростає керованість →» під картками
    f.append(arrow(xs[0] + 40, top + box_h + 34, xs[2] + col_w - 40, top + box_h + 34, color=INK, sw=2.0))
    f.append(text(W / 2, top + box_h + 28, "більше керування кольором  →  більше дротів і коду", size=11, bold=True, color=INK))

    render(os.path.join(IMG, "led-spectrum.svg"), W, H, *f)


# ── 4. Родовід самограйного LED: від зовнішнього флешера до автомата в корпусі ──
def fig_flasher_timeline():
    W, H = 1000, 560
    f = [text(W / 2, 30, "Родовід самограйного кольорового світлодіода: як автомат переселявся в корпус LED",
              size=14.5, bold=True)]

    # горизонтальна вісь часу
    ax0, ax1, ay = 90, 910, 92
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=2.2))
    f.append(text(ax1 + 4, ay + 5, "час", size=11, bold=True, color=MUTED, anchor="start"))

    # чотири віхи: (частка 0..1 по осі, рік, заголовок, колір-акцент)
    marks = [
        (0.06, "1975", "LM3909", POS),
        (0.34, "кін. 1970-х", "флешер У КОРПУСІ", "#b8860b"),
        (0.63, "1990–2000-і", "RGB-самограй", FIELD),
        (0.90, "2013", "WS2812", NEG),
    ]
    for frac, yr, ttl, col in marks:
        x = ax0 + (ax1 - ax0) * frac
        f.append(line(x, ay - 8, x, ay + 8, color=col, sw=2.4))
        f.append(circle(x, ay, 5, fill=BG, stroke=col, sw=2.4))
        f.append(text(x, ay - 18, yr, size=11.5, bold=True, color=col))
        f.append(text(x, ay - 34, ttl, size=10.5, bold=True, color=INK))

    # картки-описи під кожною віхою (широкі, з запасом, щоб текст не накладався)
    cw, ch = 214, 356
    top = 140
    xs = [30, 268, 512, 756]
    cards = [
        (POS, "#fdecea", [
            "National Semiconductor,",
            "монолітний флешер.",
            "Автомат — окрема",
            "мікросхема (8 ніжок).",
            "Ще НЕ в корпусі LED:",
            "поряд треба LED,",
            "конденсатор, батарея.",
            "Один колір, миготіння.",
        ]),
        ("#b8860b", "#fffaf0", [
            "Здешевлення КМОН.",
            "Крихітний автомат",
            "переїхав ПІД лінзу",
            "самого світлодіода.",
            "Зовні — дві ноги,",
            "як у звичайного LED.",
            "Один колір; це предок",
            "самограйного вогника.",
        ]),
        (FIELD, "#f0faf3", [
            "Три кристали R·G·B",
            "+ генератор + лічильник",
            "+ струмові ключі —",
            "усе в одному корпусі.",
            "Сам перебирає ~7",
            "кольорів по колу.",
            "Копійки; масово: іграшки,",
            "гірлянди, набори (KY-034).",
        ]),
        (NEG, "#eaf0fd", [
            "WorldSemi: у корпус",
            "додано ВХІД ДАНИХ.",
            "Кожному пікселю —",
            "24-бітний код кольору",
            "по одному дроту;",
            "решту передає далі.",
            "Це вже НЕ самограй:",
            "керований, каскадований.",
        ]),
    ]
    for x0, (col, fill, rows) in zip(xs, cards):
        # вертикальний повідець від осі до картки
        cx = x0 + cw / 2
        f.append(line(cx, ay + 8, cx, top, color=col, sw=1.4, dash="3,3"))
        f.append(rect(x0, top, cw, ch, fill=fill, stroke=col, sw=2.0, rx=12))
        yy = top + 30
        for r in rows:
            f.append(text(x0 + 14, yy, r, size=10.5, color=INK, anchor="start"))
            yy += 26
        # мітка «самограй / керований»
        tag = "самограй" if col in (POS, "#b8860b", FIELD) else "керований по шині"
        f.append(text(cx, top + ch - 14, tag, size=9.5, italic=True, color=MUTED))

    # підсумковий рядок унизу
    b, _, _ = textbox(W / 2, 542,
                      "Ліворуч направо автомат дешевшає й переселяється в корпус LED (частка 1–3 — самограй, нуль команд).\n"
                      "Праворуч — інша гілка: WS2812 лишає автомат у корпусі, але додає вхід даних — і це вже керований піксель.",
                      size=10.5, fill="#f7f9fc", stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "flasher-timeline.svg"), W, H, *f)


# ── 5. Межа струму піна: один вогник прямо з піна vs багато через транзистор ──
def fig_ky034_current():
    W, H = 980, 480
    f = [text(W / 2, 30, "Межа струму піна: один вогник — прямо з піна; багато — через транзистор-ключ",
              size=14, bold=True)]

    # ── ліва панель: один LED прямо на піні ──
    lx0 = 40
    f.append(rect(lx0, 62, 420, 344, fill="#f5fbf7", stroke=FIELD, sw=2.0, rx=12))
    f.append(rect(lx0, 62, 420, 32, fill=FIELD, stroke=FIELD, sw=0, rx=12))
    f.append(text(lx0 + 210, 84, "ОДИН вогник — прямо з піна (ОК)", size=12, bold=True, color="#ffffff"))

    # пін МК зліва
    pinx = lx0 + 62
    f.append(rect(pinx - 46, 150, 92, 42, fill=BG, stroke=INK, sw=1.6, rx=6))
    f.append(mtext(pinx, 166, ["цифровий", "пін МК"], size=9.5, color=INK))
    # дріт від піна до модуля
    modx = lx0 + 300
    f.append(line(pinx + 46, 171, modx - 62, 171, color=POS, sw=2.4))
    f.append(text((pinx + 46 + modx - 62) / 2, 160, "≈ 10 мА", size=10, bold=True, color=POS))
    # модуль KY-034
    f.append(rect(modx - 62, 138, 120, 66, fill="#fffdf5", stroke=INK, sw=1.8, rx=10))
    f.append(text(modx - 2, 162, "KY-034", size=12, bold=True, color=INK))
    f.append(text(modx - 2, 182, "один LED", size=9, color=MUTED))
    # земля назад
    f.append(line(modx - 2, 204, modx - 2, 248, color=NEG, sw=2.0))
    f.append(line(modx - 2, 248, pinx, 248, color=NEG, sw=2.0))
    f.append(line(pinx, 248, pinx, 192, color=NEG, sw=2.0))
    f.append(text(lx0 + 214, 266, "GND", size=9.5, bold=True, color=NEG))

    b, _, _ = textbox(lx0 + 210, 348,
                      "10 мА добре вкладається у 20 мА, що вивід\n"
                      "віддає надійно. Транзистор не потрібен.",
                      size=10.5, fill=BG, stroke=FIELD)
    f.append(b)

    # ── права панель: багато LED через транзистор ──
    rx0 = 520
    f.append(rect(rx0, 62, 420, 344, fill="#fdecea", stroke=POS, sw=2.0, rx=12))
    f.append(rect(rx0, 62, 420, 32, fill=POS, stroke=POS, sw=0, rx=12))
    f.append(text(rx0 + 210, 84, "БАГАТО вогників — через транзистор", size=12, bold=True, color="#ffffff"))

    # окреме живлення згори
    vcc_y = 130
    f.append(line(rx0 + 46, vcc_y, rx0 + 374, vcc_y, color=POS, sw=2.2))
    f.append(text(rx0 + 210, vcc_y - 8, "окреме живлення (+)", size=10, bold=True, color=POS))

    # гірлянда модулів від живлення до спільної шини колектора
    chainx = rx0 + 250
    for i in range(3):
        cxm = rx0 + 96 + i * 52
        f.append(line(cxm, vcc_y, cxm, vcc_y + 18, color=POS, sw=1.6))
        f.append(rect(cxm - 19, vcc_y + 18, 38, 32, fill="#fffdf5", stroke=INK, sw=1.4, rx=5))
        f.append(text(cxm, vcc_y + 38, "LED", size=8.5, color=INK))
        f.append(line(cxm, vcc_y + 50, cxm, vcc_y + 68, color=INK, sw=1.6))
    f.append(text(rx0 + 148, vcc_y + 88, "…десяток вогників = 100 мА+", size=9.5, bold=True, color=INK))
    # спільна шина колектора
    f.append(line(rx0 + 77, vcc_y + 68, rx0 + 200, vcc_y + 68, color=INK, sw=1.8))
    f.append(line(chainx, vcc_y + 68, chainx, vcc_y + 100, color=INK, sw=1.8))

    # транзистор (спрощено — коло з підписом «T»)
    tx, ty = chainx, vcc_y + 126
    f.append(circle(tx, ty, 26, fill=BG, stroke=INK, sw=1.8))
    f.append(text(tx, ty + 5, "T", size=15, bold=True, color=INK))
    f.append(text(tx + 42, ty - 4, "транзистор-", size=9.5, color=MUTED, anchor="start"))
    f.append(text(tx + 42, ty + 11, "ключ", size=9.5, color=MUTED, anchor="start"))

    # база від піна МК
    pinx2 = rx0 + 60
    f.append(rect(pinx2 - 42, ty - 21, 84, 42, fill=BG, stroke=INK, sw=1.6, rx=6))
    f.append(mtext(pinx2, ty - 5, ["цифровий", "пін МК"], size=9, color=INK))
    f.append(line(pinx2 + 42, ty, tx - 26, ty, color=POS, sw=2.0))
    f.append(text((pinx2 + 42 + tx - 26) / 2, ty - 8, "малий струм у базу", size=8.5, bold=True, color=POS))

    # емітер на спільну землю
    f.append(line(tx, ty + 26, tx, ty + 54, color=NEG, sw=1.8))
    f.append(line(rx0 + 46, ty + 54, rx0 + 374, ty + 54, color=NEG, sw=2.0))
    f.append(text(rx0 + 210, ty + 72, "спільна GND (живлення + МК + емітер)", size=9, bold=True, color=NEG))

    # ── стрічка-висновок унизу на всю ширину ──
    b2, _, _ = textbox(W / 2, 456,
                       "Код НЕ міняється: так само digitalWrite на пін. Різниця лише в залізі за піном — "
                       "прямий LED чи ключ на гірлянду.",
                       size=10.5, fill="#fffdf5", stroke=INK, min_w=760)
    f.append(b2)

    render(os.path.join(IMG, "ky034-current.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ky034_schematic()
    fig_ky034_wiring()
    fig_led_spectrum()
    fig_flasher_timeline()
    fig_ky034_current()
    print("KY-034 figs done ->", IMG)
