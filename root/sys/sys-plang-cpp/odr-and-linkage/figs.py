# -*- coding: utf-8 -*-
"""Фігури до теми «Правило одного визначення й зв'язування імен»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Горизонти компілятора й лінкера ──────────────────────────────────────
def fig_horizons():
    W, H = 1060, 570
    f = []

    LX, RX, CW = 70, 630, 360

    # рамка «горизонт компілятора» довкола лівої колонки
    fx1, fy1, fx2, fy2 = 46, 50, 454, 352
    for a, b, c, d in ((fx1, fy1, fx2, fy1), (fx2, fy1, fx2, fy2),
                       (fx2, fy2, fx1, fy2), (fx1, fy2, fx1, fy1)):
        f.append(line(a, b, c, d, color=MUTED, sw=1.2, dash="6 5"))
    f.append(text(250, 34, "горизонт компілятора — одна одиниця трансляції",
                  size=12, color=MUTED))

    f.append(fitbox(LX, 70, CW, 100,
                    "config.cpp\n#include \"packet.hpp\"\n(текст заголовка вклеєно сюди)",
                    size=13))
    f.append(fitbox(RX, 70, CW, 100,
                    "render.cpp\n#include \"packet.hpp\"\n(текст заголовка вклеєно сюди)",
                    size=13))

    f.append(arrow(LX + CW / 2, 176, LX + CW / 2, 214))
    f.append(arrow(RX + CW / 2, 176, RX + CW / 2, 214))

    f.append(fitbox(LX, 220, CW, 108,
                    "config.o\n_ZNK6Packet4sizeEv — визначено тут\n"
                    "_Z4sendRK6Packet — потрібне ззовні", size=12))
    f.append(fitbox(RX, 220, CW, 108,
                    "render.o\n_ZNK6Packet4sizeEv — визначено тут\n"
                    "_Z4sendRK6Packet — визначено тут", size=12))

    f.append(arrow(LX + CW / 2, 334, LX + CW / 2, 380))
    f.append(arrow(RX + CW / 2, 334, RX + CW / 2, 380))

    f.append(text(530, 362, "горизонт лінкера — уся програма, але самі імена",
                  size=12, color=MUTED))

    f.append(fitbox(70, 386, 920, 72,
                    "лінкер: зіставляє однакові рядки-імена й підставляє адреси",
                    size=15, bold=True, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(70, 478, 920, 62,
                    "ні тіл функцій, ні полів Packet у таблиці немає — порівнювати нема чого",
                    size=13, color=MUTED, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'horizons.svg'), W, H, *f,
           title="Що бачить компілятор і що бачить лінкер")


# ── 2. Сягання імені: чотири рівні зв'язування ──────────────────────────────
def fig_linkage_reach():
    W, H = 1000, 520
    f = []

    f.append(text(500, 42, "як далеко ім'я позначає ТУ САМУ сутність",
                  size=13, color=MUTED))

    rows = [
        (76,  "без зв'язування\nзмінна в тілі функції",
         140, "блок", FILL, MUTED),
        (176, "внутрішнє\nstatic · безіменний простір імен · const",
         300, "одна одиниця трансляції", "#eaf0fd", NEG),
        (276, "модульне (C++20)\nоголошене в модулі, не експортоване",
         460, "усі одиниці одного модуля", "#eef6ee", FIELD),
        (376, "зовнішнє\nзвичайна функція · extern-змінна · клас",
         620, "уся програма — тут діє «рівно одне визначення»", "#fff7e6", POS),
    ]
    for y, label, bw, bar, fill, stroke in rows:
        f.append(fitbox(40, y, 250, 76, label, size=12))
        f.append(fitbox(320, y, bw, 76, bar, size=12, fill=fill, stroke=stroke))

    f.append(fitbox(40, 460, 900, 46,
                    "ширина смуги — коло оголошень, у якому однакове ім'я означає один об'єкт",
                    size=12, color=MUTED, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'linkage-reach.svg'), W, H, *f,
           title="Чотири рівні зв'язування")


# ── 3. Злиття однойменних злитних символів ──────────────────────────────────
def fig_comdat_merge():
    W, H = 1020, 520
    f = []

    cols = [
        (40,  "config.o\nзібрано з -DWITH_TIMESTAMP\nтіло: return 16;\n"
              "символ _ZNK6Packet4sizeEv", "#fff7e6", POS),
        (370, "render.o\nзібрано без прапорця\nтіло: return 8;\n"
              "символ _ZNK6Packet4sizeEv", FILL, LINE),
        (700, "log.o\nзібрано без прапорця\nтіло: return 8;\n"
              "символ _ZNK6Packet4sizeEv", FILL, LINE),
    ]
    for x, s, fill, stroke in cols:
        f.append(fitbox(x, 64, 280, 112, s, size=12, fill=fill, stroke=stroke))
        f.append(arrow(x + 140, 180, x + 140, 226))

    f.append(fitbox(40, 232, 940, 76,
                    "лінкер: імена збігаються — лишає ОДНУ копію, решту викидає; тіла не звіряє",
                    size=15, bold=True, fill="#eaf0fd", stroke=NEG))

    f.append(arrow(510, 314, 510, 358))

    f.append(fitbox(190, 364, 640, 82,
                    "у програмі лишилося одне тіло: return 16;\n"
                    "render.o й log.o рахують крок масиву як 8, а дістають 16",
                    size=13, fill="#fdecea", stroke=POS))

    f.append(fitbox(40, 464, 940, 44,
                    "збірка чиста: попереджень немає ні від компілятора, ні від лінкера",
                    size=12, color=MUTED, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'comdat-merge.svg'), W, H, *f,
           title="Однойменні злитні символи лінкер зводить до одного")


# ── 4. Розбіжний крок обходу масиву ─────────────────────────────────────────
def fig_stride_break():
    W, H = 1040, 434
    X0, BW = 70, 28          # ліва межа й ширина одного байта
    f = []

    def bx(k):               # координата зсуву k байтів
        return X0 + BW * k

    f.append(text(X0, 62, "config.cpp — з -DWITH_TIMESTAMP: sizeof(Packet) = 16",
                  size=13, anchor="start"))
    for k in (0, 8, 16, 24, 32):
        f.append(text(bx(k), 92, str(k), size=11, color=MUTED))

    for base in (0, 16):     # два записи по 16 байтів
        f.append(fitbox(bx(base), 102, BW * 4, 62, "id", size=13))
        f.append(fitbox(bx(base + 4), 102, BW * 4, 62, "len", size=13))
        f.append(fitbox(bx(base + 8), 102, BW * 8, 62, "ts", size=13,
                        fill="#fff7e6", stroke=POS))
    f.append(text(bx(8), 186, "запис 0 — 16 байтів", size=11, color=MUTED))
    f.append(text(bx(24), 186, "запис 1 — 16 байтів", size=11, color=MUTED))

    f.append(text(X0, 216, "render.cpp — без прапорця: sizeof(Packet) = 8",
                  size=13, anchor="start"))
    for base, bad in ((0, False), (8, True), (16, False), (24, True)):
        fill = "#fdecea" if bad else FILL
        stroke = POS if bad else LINE
        f.append(fitbox(bx(base), 226, BW * 4, 56, "id", size=13,
                        fill=fill, stroke=stroke))
        f.append(fitbox(bx(base + 4), 226, BW * 4, 56, "len", size=13,
                        fill=fill, stroke=stroke))

    vals = [(0,  "id = 0\nlen = 100", False),
            (8,  "id = -807049216\nlen = 395", True),
            (16, "id = 1\nlen = 101", False),
            (24, "id = -807049215\nlen = 395", True)]
    for base, s, bad in vals:
        f.append(fitbox(bx(base), 292, BW * 8, 54, s, size=12,
                        fill="#fdecea" if bad else BG,
                        stroke=POS if bad else MUTED))

    f.append(fitbox(X0, 366, BW * 32, 48,
                    "читач лишається в межах виділеної памʼяті — "
                    "ні падіння, ні скарги санітайзера",
                    size=12, color=MUTED, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'stride-break.svg'), W, H, *f,
           title="Розбіжний крок обходу масиву")


if __name__ == '__main__':
    fig_horizons()
    fig_linkage_reach()
    fig_comdat_merge()
    fig_stride_break()
    print("ok")
