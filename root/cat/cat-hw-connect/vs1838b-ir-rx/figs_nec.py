# -*- coding: utf-8 -*-
"""Фігури до вставки «proj-nec-decode.md» (розбір NEC за таймінгами на OUT).
Окремий файл, щоб не чіпати figs.py теми. Вивід — у той самий ./img/.
Запуск:  python figs_nec.py
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія кадру NEC на виводі OUT (як його бачить декодер) ──────────────
def fig_nec_frame():
    W, H = 1080, 560
    f = [text(W / 2, 30, "Кадр NEC на виводі OUT: активний нуль. Декодер вимірює ДОВЖИНУ провалів і пауз",
              size=15, bold=True)]

    ax0 = 60
    axw = 960
    hi = 130           # рівень спокою (HIGH)
    lo = 200           # активний LOW
    f.append(text(ax0 - 8, hi + 5, "1", size=13, bold=True, color=MUTED, anchor="end"))
    f.append(text(ax0 - 8, lo + 5, "0", size=13, bold=True, color=MUTED, anchor="end"))
    f.append(text(ax0 + axw + 8, hi + 5, "спокій (HIGH)", size=10, color=MUTED, anchor="start"))
    f.append(text(ax0 + axw + 8, lo + 5, "несуча (LOW)", size=10, color=MUTED, anchor="start"))

    # сегменти: (low?, ширина_px, підпис_під, колір_підпису)
    # старт 9мс LOW + 4.5мс HIGH, тоді біти: кожен = короткий LOW(560) + пауза HIGH(560=0 / 1690=1)
    B = 12   # піксель на «одиницю» тривалості (560мкс ≈ 1 умовна одиниця)
    segs = [
        ("L", 9 * B, "9 мс\nстарт", POS),        # 9 мс провал
        ("H", 4.5 * B, "4.5 мс\nпауза", NEG),     # 4.5 мс пауза
        ("L", 1 * B, "", None),                    # burst біта
        ("H", 1 * B, "0", FIELD),                  # пауза → 0
        ("L", 1 * B, "", None),
        ("H", 3 * B, "1", FIELD),                  # пауза → 1
        ("L", 1 * B, "", None),
        ("H", 1 * B, "0", FIELD),
        ("L", 1 * B, "", None),
        ("H", 3 * B, "1", FIELD),
    ]
    x = ax0
    pts = [(ax0, hi)]
    for kind, wpx, lab, col in segs:
        y = lo if kind == "L" else hi
        pts.append((x, y))
        pts.append((x + wpx, y))
        if lab:
            f.append(text(x + wpx / 2, lo + 40 if kind == "L" else hi - 12, lab,
                          size=10, color=col, bold=(col in (POS, NEG))))
        x += wpx
    pts.append((x, hi))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, INK))

    # дужка над стартом
    sx = ax0
    sw_ = (9 + 4.5) * B
    f.append(line(sx, hi - 34, sx + sw_, hi - 34, color=POS, sw=1.4))
    f.append(line(sx, hi - 34, sx, hi - 28, color=POS, sw=1.4))
    f.append(line(sx + sw_, hi - 34, sx + sw_, hi - 28, color=POS, sw=1.4))
    f.append(text(sx + sw_ / 2, hi - 40, "ПРЕАМБУЛА: 9 мс LOW + 4.5 мс HIGH", size=10, bold=True, color=POS))

    # дужка над бітами
    bx0 = ax0 + (9 + 4.5) * B
    bw_ = x - bx0
    f.append(line(bx0, lo + 60, bx0 + bw_, lo + 60, color=FIELD, sw=1.4))
    f.append(line(bx0, lo + 54, bx0, lo + 60, color=FIELD, sw=1.4))
    f.append(line(bx0 + bw_, lo + 54, bx0 + bw_, lo + 60, color=FIELD, sw=1.4))
    f.append(text(bx0 + bw_ / 2, lo + 76, "далі 32 біти: КОЖЕН = LOW 560 мкс + пауза (560 = 0, 1690 = 1)",
                  size=10, bold=True, color=FIELD))

    # виноска: біт вимірюється по ПАУЗІ
    b1, _, _ = textbox(300, 340,
                       "Провал (LOW) у КОЖНОГО біта однаковий — 560 мкс.\n"
                       "Значення несе ПАУЗА після нього:\n"
                       "  560 мкс тиші  → нуль\n"
                       "  1690 мкс тиші → одиниця",
                       size=11, fill="#eaf5ec", stroke=FIELD)
    f.append(b1)

    b2, _, _ = textbox(780, 340,
                       "Вихід ІНВЕРТОВАНИЙ: «є світло» = 0, «тиша» = 1.\n"
                       "Тому старт — це ДОВГИЙ ПРОВАЛ у нуль (9 мс),\n"
                       "а не імпульс угору. Декодер, що чекає фронту\n"
                       "вгору, не побачить нічого.",
                       size=11, fill="#fdecea", stroke=POS)
    f.append(b2)

    b3, _, _ = textbox(W / 2, 470,
                       "Повний кадр = преамбула + 8 біт адреси + 8 біт ~адреси + 8 біт команди + 8 біт ~команди (усе молодшим бітом уперед),\n"
                       "і завершальний короткий LOW 560 мкс. Інверсні байти — це вбудована перевірка: адреса XOR ~адреси має дати 0xFF.",
                       size=11, fill=BG, stroke=INK)
    f.append(b3)

    render(os.path.join(IMG, "nec-frame.svg"), W, H, *f)


# ── 2. Скінченний автомат ручного декодера (на перериванні по спаду) ──────────
def fig_decode_fsm():
    W, H = 1020, 520
    f = [text(W / 2, 30, "Ручний декодер як автомат: кожен спад OUT — крок; вимірюємо час між спадами",
              size=15, bold=True)]

    # чотири стани в ряд
    states = [
        ("IDLE\nчекаємо\nпреамбулу", "#eef1f5", 150, 150),
        ("LEADER\nбачили 9 мс\nпровал", FILL, 400, 150),
        ("BITS\nзбираємо\n32 біти", "#eaf5ec", 650, 150),
        ("DONE\nкадр\nготовий", "#fdecea", 900, 150),
    ]
    cx = []
    for lab, fill, x, y in states:
        f.append(fitbox(x - 80, y - 45, 160, 90, lab, size=12, fill=fill, stroke=INK, bold=True))
        cx.append((x, y))

    # переходи вздовж ряду з підписами про ВИМІРЯНИЙ інтервал
    trans = [
        (0, 1, "провал ≈ 9 мс\n(старт кадру)"),
        (1, 2, "пауза ≈ 4.5 мс\n(це команда)"),
        (2, 3, "зібрано 32-й біт"),
    ]
    for a, b, lab in trans:
        x1 = cx[a][0] + 82
        x2 = cx[b][0] - 82
        y = cx[a][1]
        f.append(arrow(x1, y, x2, y, color=INK, sw=2.0))
        f.append(text((x1 + x2) / 2, y - 18, lab, size=10, color=INK))

    # самопетля на BITS: «ще біт»
    bx, by = cx[2]
    f.append('<path d="M %.0f %.0f q 60 -70 120 0" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (bx - 60, by - 40, FIELD))
    f.append(text(bx, by - 96, "кожен наступний спад: зміряти паузу перед ним →\nкоротка = 0, довга = 1; зсунути в результат", size=10, color=FIELD))

    # гілка «пауза ≈ 2.25 мс» з LEADER → REPEAT (ліворуч униз, підпис зліва — геть від центру)
    lx, ly = cx[1]
    f.append(fitbox(lx - 150, 330, 210, 74, "REPEAT\nкнопку тримають —\nта сама команда", size=11,
                    fill="#fff7e6", stroke="#b7791f", bold=True))
    f.append(arrow(lx - 45, ly + 46, lx - 45, 328, color="#b7791f", sw=1.8))
    f.append(text(lx - 165, (ly + 46 + 328) / 2 + 4, "пауза ≈ 2.25 мс\n(не 4.5) → повтор", size=10, color="#b7791f", anchor="end"))

    # повернення DONE → IDLE (дугою знизу; підпис — під самою DONE, праворуч, НЕ через центр)
    dx, dy = cx[3]
    f.append('<path d="M %.0f %.0f q 0 120 -750 0" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)" stroke-dasharray="4 4"/>'
             % (dx, dy + 46, MUTED))
    f.append(text(dx, dy + 210, "далі: видати команду →\nповернутись у IDLE", size=10, color=MUTED))

    b, _, _ = textbox(W / 2, 460,
                      "Ключ до автомата — годинник micros(): на КОЖЕН спад OUT рахуємо, скільки часу минуло від попереднього спаду.\n"
                      "Довжина цього інтервалу й каже, у якому ми стані: ~13.5 мс — старт даних, ~11.25 мс — повтор, ~1.1 чи ~2.2 мс — біт 0 чи 1.",
                      size=11, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "nec-decode-fsm.svg"), W, H, *f)


if __name__ == "__main__":
    fig_nec_frame()
    fig_decode_fsm()
    print("VS1838B NEC-decode figs done ->", IMG)
