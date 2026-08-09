# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

WRITTEN = "#dfe8fc"     # уже записано
FREE     = "#ffffff"    # ще порожньо
CONV     = "#e8f4ea"    # звичайна зона
WARM     = "#fff4e0"
WARMLINE = "#b8860b"
COOL     = "#eef2f7"


# ── 1. Простір номерів, поділений на зони ──────────────────────────────────
def fig_zone_layout():
    W, H = 1220, 620
    p = []
    p.append(text(W / 2, 40, "простір логічних номерів, поділений на зони",
                  size=18, bold=True, color=INK))

    BX, BY, BH = 70, 110, 78
    ZW = 178
    NZ = 6
    # частка зони, вже заповнена
    filled = [None, 1.0, 0.55, 0.0, 0.0, 0.0]   # None — звичайна зона

    for i in range(NZ):
        x = BX + i * ZW
        if filled[i] is None:
            p.append(rect(x, BY, ZW - 8, BH, fill=CONV, stroke=FIELD, sw=2, rx=4))
            p.append(text(x + (ZW - 8) / 2, BY + BH / 2 + 5, "звичайна",
                          size=13.5, color=FIELD, bold=True))
        else:
            p.append(rect(x, BY, ZW - 8, BH, fill=FREE, stroke=LINE, sw=1.8, rx=4))
            fw = (ZW - 8) * filled[i]
            if fw > 1:
                p.append(rect(x, BY, fw, BH, fill=WRITTEN, stroke=NEG, sw=1.4, rx=4))
        p.append(text(x + (ZW - 8) / 2, BY - 18, "зона %d" % i, size=13, color=MUTED))

    # вказівник запису в зоні 2
    wp_x = BX + 2 * ZW + (ZW - 8) * 0.55
    p.append(arrow(wp_x, BY + BH + 74, wp_x, BY + BH + 8, color=POS, sw=2.6))
    p.append(textbox(wp_x, BY + BH + 104, ["вказівник запису"], size=13.5,
                     fill=WARM, stroke=POS, sw=2, color=POS, bold=True)[0])

    # підписи станів зон
    labels = [
        (BX + 1 * ZW + (ZW - 8) / 2, "повна"),
        (BX + 2 * ZW + (ZW - 8) / 2, "відкрита"),
        (BX + 4 * ZW + (ZW - 8) / 2, "порожня"),
    ]
    for x, s in labels:
        p.append(text(x, BY + BH + 26, s, size=13, color=MUTED))

    # три правила
    rules = [
        ("новий запис лягає рівно у вказівник —\nні раніше, ні пізніше", NEG),
        ("запис у вже заповнену частину зони\nпристрій відхиляє помилкою", POS),
        ("скидання зони повертає вказівник\nна початок і стирає вміст", FIELD),
    ]
    ry = 330
    for i, (s, col) in enumerate(rules):
        x = 70 + i * 372
        p.append(fitbox(x, ry, 340, 82, s.split("\n"), size=14,
                        fill=COOL, stroke=col, sw=2))

    p.append(fitbox(70, ry + 122, 1084, 78,
                    ["звичайна зона живе за старими правилами: у неї можна писати куди завгодно й скільки завгодно разів;",
                     "послідовна зона — це носій, який показав своє справжнє обмеження замість того, щоб його імітувати"],
                    size=14, fill=WARM, stroke=WARMLINE, sw=2))

    render(os.path.join(IMG, 'zone-layout.svg'), W, H, *p)


# ── 2. Стани зони й два ліміти ─────────────────────────────────────────────
def fig_zone_states():
    W, H = 1280, 640
    p = []
    p.append(text(W / 2, 40, "стани зони: чому пристрій узагалі їх розрізняє",
                  size=18, bold=True, color=INK))

    NODE = dict(size=15, bold=True, pad=14, sw=2.2, min_w=170)
    ye, yc = 190, 400

    empty = textbox(160, ye, ["ПОРОЖНЯ"], fill="#ffffff", stroke=MUTED, color=MUTED, **NODE)
    openz = textbox(520, ye, ["ВІДКРИТА"], fill=WARM, stroke=POS, color=POS, **NODE)
    fullz = textbox(880, ye, ["ПОВНА"], fill=WRITTEN, stroke=NEG, color=NEG, **NODE)
    closz = textbox(520, yc, ["ЗАКРИТА"], fill=COOL, stroke=LINE, color=INK, **NODE)
    for b in (empty, openz, fullz, closz):
        p.append(b[0])

    hw = NODE["min_w"] / 2

    # порожня → відкрита
    p.append(arrow(160 + hw + 6, ye, 520 - hw - 6, ye, color=INK, sw=2.2))
    p.append(text(340, ye - 26, "перший запис", size=13.5, color=INK))
    p.append(text(340, ye - 6, "або команда «відкрити»", size=12.5, color=MUTED))

    # відкрита → повна
    p.append(arrow(520 + hw + 6, ye, 880 - hw - 6, ye, color=INK, sw=2.2))
    p.append(text(700, ye - 26, "запис дійшов кінця", size=13.5, color=INK))
    p.append(text(700, ye - 6, "або команда «завершити»", size=12.5, color=MUTED))

    # відкрита ↔ закрита
    p.append(arrow(492, ye + 34, 492, yc - 34, color=INK, sw=2.2))
    p.append(arrow(548, yc - 34, 548, ye + 34, color=INK, sw=2.2))
    p.append(text(590, ye + 88, "«закрити» — пристрій", size=13, color=MUTED, anchor="start"))
    p.append(text(590, ye + 108, "забирає свій буфер назад", size=13, color=MUTED, anchor="start"))
    p.append(text(240, ye + 88, "новий запис — буфер", size=13, color=MUTED, anchor="start"))
    p.append(text(240, ye + 108, "доводиться видавати знову", size=13, color=MUTED, anchor="start"))

    # скидання: знизу назад у порожню
    yb = 530
    p.append(line(880, yc - 60, 880, yb, color=FIELD, sw=2.2))
    p.append(line(880, yb, 160, yb, color=FIELD, sw=2.2))
    p.append(arrow(160, yb, 160, ye + 34, color=FIELD, sw=2.2))
    p.append(text(520, yb + 24, "«скинути» — єдиний спосіб знову писати в ту саму зону",
                  size=14, color=FIELD, bold=True))

    # два ліміти
    p.append(fitbox(1010, 140, 240, 96,
                    ["відкритих зон", "не більше ніж", "max_open_zones"],
                    size=13.5, fill=WARM, stroke=POS, sw=2))
    p.append(fitbox(1010, 268, 240, 116,
                    ["відкритих плюс закритих", "не більше ніж",
                     "max_active_zones", "(звідси й другий ліміт)"],
                    size=13.5, fill=COOL, stroke=NEG, sw=2))

    render(os.path.join(IMG, 'zone-states.svg'), W, H, *p)


# ── 3. Хто стежить за порядком: три відповіді ──────────────────────────────
def fig_order_guard():
    W, H = 1280, 690
    p = []
    p.append(text(W / 2, 40, "чотири записи в одну зону: хто не дасть їм переплутатися",
                  size=18, bold=True, color=INK))

    rows = [
        ("замок зони в планувальнику",
         "ядра 4.10 – 6.9",
         1, "три інші чекають і тримають талони черги", POS),
        ("затички запису в блоковому шарі",
         "ядра 6.10 і новіші",
         1, "три інші чекають, але талонів не тримають", WARMLINE),
        ("дозапис у зону (zone append)",
         "команда самого пристрою",
         4, "усі чотири в польоті; адресу назве пристрій", FIELD),
    ]

    LX, RY0, RH = 60, 110, 190
    for r, (title_s, sub_s, inflight, note, col) in enumerate(rows):
        y = RY0 + r * RH
        p.append(fitbox(LX, y, 300, 74, [title_s, sub_s], size=14,
                        fill=COOL, stroke=col, sw=2.2, bold=False))

        # чотири запити
        for i in range(4):
            x = 410 + i * 78
            live = i < inflight
            p.append(rect(x, y + 8, 60, 44,
                          fill=WRITTEN if live else "#ffffff",
                          stroke=col if live else MUTED,
                          sw=2 if live else 1.3, rx=4))
            p.append(text(x + 30, y + 36, "W%d" % (i + 1), size=13,
                          color=INK if live else MUTED, bold=live))

        # стрілка до пристрою
        p.append(arrow(410 + inflight * 78 - 12, y + 30, 900, y + 30, color=col, sw=2.4))
        p.append(fitbox(910, y + 4, 150, 52, ["пристрій"], size=14,
                        fill="#ffffff", stroke=LINE, sw=2))

        p.append(text(410, y + 92, note, size=13.5, color=MUTED, anchor="start"))

    p.append(fitbox(60, RY0 + 3 * RH + 6, 1160, 84,
                    ["перші дві відповіді бережуть порядок тим, що душать паралельність;",
                     "третя знімає саме питання порядку — і тим повертає паралельність назад"],
                    size=14.5, fill=WARM, stroke=WARMLINE, sw=2))

    render(os.path.join(IMG, 'order-guard.svg'), W, H, *p)


if __name__ == "__main__":
    fig_zone_layout()
    fig_zone_states()
    fig_order_guard()
    print("done")
