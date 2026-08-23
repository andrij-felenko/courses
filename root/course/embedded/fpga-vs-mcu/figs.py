# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Акценти таблиці: синій = мікроконтролер, зелений = FPGA, зелена заливка = тут явно сильніший.
MCU  = "#2457d6"
FPGA = "#1f8a3b"
WIN  = "#eef7ee"   # клітинка, де сторона виграє


# ── criteria: де виграє МК, а де FPGA — по осях, без переможця за всіма ────────
# Ідея: розподіл ролей, а не змагання. Кожен рядок — вісь; зелена заливка
# показує, чия це вотчина. Жодна колонка не зафарбована суцільно.

def fig_criteria():
    W, H = 760, 392
    rows = [
        # критерій,                  МК,                    win_mcu, FPGA,                   win_fpga
        ("Справжня паралельність",   "ні (одне ядро по черзі)",   False, "так (схема на канал)",   True),
        ("Затримка реакції",         "такти + джитер",            False, "наносекунди, стало",     True),
        ("Складна послідовна логіка","легко (код, бібліотеки)",   True,  "громіздко й дорого",     False),
        ("Поріг входу",              "низький, години",           True,  "крутий, тижні",          False),
        ("Ціна простої задачі",      "копійки, один чип",         True,  "дорожче + обв'язка",     False),
        ("Енергія на ват логіки",    "залежить від режиму",       False, "часто ефективніша",      True),
    ]
    cx0, cw0 = 24, 196          # колонка «критерій»
    cx1, cw1 = 226, 256         # колонка МК
    cx2, cw2 = 488, 248         # колонка FPGA
    top, rh = 64, 50
    p = [text(W/2, 30, "Де виграє мікроконтролер, а де FPGA", size=17, bold=True),
         text(W/2, 50, "не «що краще», а «що пасує задачі» — у кожного є своя вотчина",
              size=11.5, color=MUTED, italic=True)]

    # шапка
    p.append(rect(cx0, top, cw0, 28, fill="#eef0f4", stroke=INK, sw=1.3))
    p.append(text(cx0+12, top+19, "критерій", size=12, anchor="start", bold=True))
    p.append(rect(cx1, top, cw1, 28, fill="#eef0f4", stroke=MCU, sw=1.3))
    p.append(text(cx1+cw1/2, top+19, "мікроконтролер", size=12, color=MCU, bold=True))
    p.append(rect(cx2, top, cw2, 28, fill="#eef0f4", stroke=FPGA, sw=1.3))
    p.append(text(cx2+cw2/2, top+19, "FPGA", size=12, color=FPGA, bold=True))

    y = top + 32
    for crit, mcu, wmcu, fpga, wfpga in rows:
        p.append(rect(cx0, y, cw0, rh, fill="#fafafa", stroke=INK, sw=1.1))
        p.append(fitbox(cx0, y, cw0, rh, crit, size=11, pad=8, fill="none",
                        stroke="none", bold=True))
        p.append(fitbox(cx1, y, cw1, rh, mcu, size=10.5, pad=8,
                        fill=(WIN if wmcu else "#ffffff"), stroke=MCU, sw=1.1,
                        bold=wmcu))
        p.append(fitbox(cx2, y, cw2, rh, fpga, size=10.5, pad=8,
                        fill=(WIN if wfpga else "#ffffff"), stroke=FPGA, sw=1.1,
                        bold=wfpga))
        y += rh

    p.append(text(W/2, y+22, "Зелена клітинка — сторона, що тут явно сильніша.",
                  size=11, bold=True))
    p.append(text(W/2, y+38, "Жодна колонка не виграє скрізь — вибір диктує конкретна задача.",
                  size=10.5, color=MUTED))
    render(os.path.join(OUT, "criteria.svg"), W, max(H, y+50), *p)


# ── latency: порядки величин однієї осі — затримка «вхід → вихід» ──────────────
# Ідея: довжина смуги = порядок затримки. Видно, що FPGA не на відсотки, а в рази
# швидша; але мікросекунд МК часто досить — це теж сказано.

def fig_latency():
    W, H = 908, 450
    bx, bw = 230, 500           # ліва межа смуг і максимальна ширина
    p = [text(W/2, 30, "Затримка «вхід змінився -> вихід відреагував»", size=17, bold=True),
         text(W/2, 50, "груба ілюстрація порядків — конкретика залежить від задачі",
              size=11.5, color=MUTED, italic=True)]

    bars = [
        ("МК: опитування в циклі", MCU, 1.00, "сотні нс–мкс: поки дійде черга"),
        ("МК: переривання",        MCU, 0.58, "десятки–сотні тактів на вхід у обробник"),
        ("FPGA: пряма логіка",     FPGA, 0.12, "одиниці–десятки нс: крізь кілька вентилів"),
    ]
    y = 96
    for label, col, frac, note in bars:
        fill = "#eef7ee" if col == FPGA else "#f3f5fd"
        p.append(text(bx-14, y+24, label, size=11.5, color=col, anchor="end", bold=True))
        p.append(rect(bx, y, bw*frac, 38, fill=fill, stroke=col, sw=1.8))
        p.append(text(bx+bw*frac+12, y+24, note, size=10, anchor="start"))
        y += 76

    # вісь напряму
    p.append(line(bx, y+4, bx+bw, y+4, color=MUTED, sw=1.4, dash="4 3"))
    p.append(arrow(bx, y+4, bx+bw, y+4, color=MUTED, sw=1.4))
    p.append(text(bx, y+22, "-> більша затримка", size=10, color=MUTED, anchor="start", italic=True))

    box = fitbox(40, y+34, W-80, 60,
                 "Коли важать саме наносекунди (швидке керування, захист, обробка фронтів) — "
                 "FPGA виграє з великим відривом.",
                 size=11.5, pad=10, fill="#f4f7f4", stroke=FPGA, sw=1.7, bold=True)
    p.append(box)
    p.append(text(W/2, y+108, "Досить «зреагувати за мікросекунди» — мікроконтролера вистачає, і він простіший.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "latency.svg"), W, y+126, *p)


# ── decision: дерево розвилок МК / FPGA / обидва разом ─────────────────────────
# Ідея: кожна гілка веде до інструмента під конкретні вимоги; переможця за
# замовчуванням немає. Стартова розвилка — паралельність/наносекунди.

def fig_decision():
    W, H = 760, 470
    p = [text(W/2, 30, "Дерево рішень: МК, FPGA чи обидва разом", size=17, bold=True),
         text(W/2, 50, "кілька запитань, що зазвичай вирішують справу — не догма, а здоровий глузд",
              size=11.5, color=MUTED, italic=True)]

    # коренева розвилка
    rxw, rxh = 320, 48
    rx, ry = W/2 - rxw/2, 70
    p.append(rect(rx, ry, rxw, rxh, fill="#eef0f4", stroke=INK, sw=1.8))
    p.append(mtext(W/2, ry+20, ["Жорстка паралельність", "або реакція за наносекунди?"],
                   size=11, bold=True))

    # ── ліва гілка «ні» → друга розвилка → МК
    p.append(arrow(rx+30, ry+rxh, 175, 150, color=MCU, sw=2))
    p.append(text(225, ry+rxh+24, "ні", size=11, color=MCU, bold=True))
    p.append(rect(45, 150, 260, 48, fill="#eef0f4", stroke=INK, sw=1.8))
    p.append(mtext(175, 170, ["потік даних уміщується", "в одне ядро по тактах?"],
                   size=11, bold=True))
    p.append(arrow(175, 198, 175, 244, color=FPGA, sw=2))
    p.append(text(191, 224, "так", size=10, color=FPGA, anchor="start", bold=True))
    p.append(rect(65, 244, 220, 48, fill="#f3f5fd", stroke=MCU, sw=1.8))
    p.append(text(175, 266, "МІКРОКОНТРОЛЕР", size=11.5, bold=True))
    p.append(text(175, 283, "дешево, швидко в розробці", size=9.5, color=MUTED, italic=True))

    # ── права гілка «так» → друга розвилка → softcore / чиста FPGA
    p.append(arrow(rx+rxw-30, ry+rxh, 585, 150, color=FPGA, sw=2))
    p.append(text(535, ry+rxh+24, "так", size=11, color=FPGA, bold=True))
    p.append(rect(455, 150, 270, 48, fill="#eef0f4", stroke=INK, sw=1.8))
    p.append(mtext(590, 170, ["багато складної послідовної", "логіки / меню / мережі теж?"],
                   size=11, bold=True))
    # так → softcore
    p.append(arrow(590, 198, 590, 244, color=POS, sw=2))
    p.append(text(606, 224, "так", size=10, color=POS, anchor="start", bold=True))
    p.append(rect(470, 244, 240, 48, fill="#fdf1ec", stroke=POS, sw=1.8))
    p.append(text(590, 266, "FPGA + ядро всередині", size=11, bold=True))
    p.append(text(590, 283, "softcore поряд зі схемою", size=9.5, color=MUTED, italic=True))
    # ні → чиста FPGA
    p.append(line(470, 174, 360, 244, color=FPGA, sw=1.7, dash="4 3"))
    p.append(arrow(415, 209, 360, 244, color=FPGA, sw=1.7))
    p.append(text(430, 206, "ні", size=10, color=FPGA, bold=True))
    p.append(rect(255, 330, 210, 48, fill="#eef7ee", stroke=FPGA, sw=1.8))
    p.append(text(360, 352, "чиста FPGA", size=11.5, bold=True))
    p.append(text(360, 369, "паралельність і таймінг у залізі", size=9.5, color=MUTED, italic=True))
    # стрілка від другої правої розвилки до чистої FPGA
    p.append(arrow(360, 292, 360, 330, color=FPGA, sw=1.5))

    box = fitbox(40, 398, W-80, 60,
                 "У дереві немає переможця за замовчуванням: кожна гілка веде до інструмента "
                 "під конкретні вимоги задачі.",
                 size=11.5, pad=10, fill="#f4f7f4", stroke=FPGA, sw=1.7, bold=True)
    p.append(box)
    render(os.path.join(OUT, "decision.svg"), W, 470, *p)


if __name__ == "__main__":
    fig_criteria()
    fig_latency()
    fig_decision()
    print("figs done")
