# -*- coding: utf-8 -*-
"""Фігури для теми «Ключі захисту пам'яті: PKU і PKRU» (довідник Unix і Linux)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
RED_F = "#fdecea"
YEL_F = "#fff5e0"


# ── 1. Два джерела прав: таблиця сторінок і регістр ────────────────────────
def fig_two_sources():
    W, H = 1300, 700
    F = []

    F.append(text(W / 2, 34, "Кожне звернення до пам'яті звіряють ДВІЧІ", size=18, bold=True))

    # ліворуч — звернення
    b, bw, bh = textbox(170, 130, ["звернення до пам'яті", "за адресою 0x7f…c000"],
                        size=15, fill=BLU_F, pad=14)
    F.append(b)

    # верхня гілка: запис таблиці сторінок
    F.append(rect(430, 78, 470, 122, fill=FILL))
    F.append(text(665, 104, "запис таблиці сторінок (на цю сторінку)", size=15, bold=True))
    F.append(fitbox(455, 122, 120, 58, "R/W = 1\nдозволено\nписати", size=12, fill=GRN_F))
    F.append(fitbox(595, 122, 120, 58, "U/S = 1\nсторінка\nкористувача", size=12, fill=GRN_F))
    F.append(fitbox(735, 122, 140, 58, "ключ = 3\nбіти 62…59", size=12, fill=YEL_F))

    # нижня гілка: PKRU
    F.append(rect(430, 262, 470, 122, fill=FILL))
    F.append(text(665, 288, "регістр PKRU (свій у кожного потоку)", size=15, bold=True))
    F.append(fitbox(455, 306, 190, 58, "для ключа 3:  AD = 0\nдоступ дозволено", size=12, fill=GRN_F))
    F.append(fitbox(665, 306, 210, 58, "для ключа 3:  WD = 1\nзапис ЗАБОРОНЕНО", size=12, fill=RED_F))

    F.append(arrow(285, 118, 425, 100))
    F.append(arrow(285, 150, 425, 292))

    # злиття
    F.append(arrow(905, 138, 1000, 210))
    F.append(arrow(905, 322, 1000, 250))
    b, bw, bh = textbox(1130, 230, ["чинні права:", "читати — можна", "писати — не можна"],
                        size=15, fill=YEL_F, pad=14)
    F.append(b)

    # наслідок
    F.append(line(120, 440, 1230, 440, color=MUTED, dash="6 6"))
    F.append(text(675, 476, "що станеться зі спробою записати", size=16, bold=True))

    steps = [
        (255, "MMU бачить\nWD = 1"),
        (555, "збій сторінки,\nу коді помилки\nвиставлено біт 5"),
        (855, "ядро бачить біт 5\nі не шукає\nсторінку далі"),
        (1145, "SIGSEGV,\nsi_code = SEGV_PKUERR,\nsi_pkey = 3"),
    ]
    for i, (cx, s) in enumerate(steps):
        b, bw, bh = textbox(cx, 570, s, size=13,
                            fill=RED_F if i == 3 else FILL, pad=12)
        F.append(b)
        if i:
            F.append(arrow(steps[i - 1][0] + 105, 570, cx - 118, 570))

    F.append(text(675, 662,
                  "ключ лише ЗВУЖУЄ те, що дозволив запис таблиці: скинути WD і дописати в сторінку без R/W не вийде",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, 'two-sources.svg'), W, H, *F)


# ── 2. Дві дороги до зміни прав ────────────────────────────────────────────
def fig_two_roads():
    W, H = 1340, 640
    F = []

    F.append(text(W / 2, 34, "Зробити ділянку записуваною на мить: дві дороги", size=18, bold=True))

    # ── верхня доріжка: mprotect
    F.append(text(70, 92, "mprotect", size=16, bold=True, anchor="start"))
    F.append(text(70, 116, "через ядро", size=13, color=MUTED, anchor="start"))

    lane_y = 150
    seq = [
        (300, 150, "вхід у ядро"),
        (470, 190, "розсічення ділянки\nу дереві VMA"),
        (680, 200, "правка N записів\nтаблиці сторінок"),
        (900, 250, "IPI на всі ядра,\nде живе цей процес,\nі скидання TLB"),
        (1180, 150, "повернення"),
    ]
    prev = None
    for cx, bw, s in seq:
        F.append(fitbox(cx - bw / 2, lane_y, bw, 78, s, size=13, fill=BLU_F))
        if prev is not None:
            F.append(arrow(prev, lane_y + 39, cx - bw / 2 - 8, lane_y + 39))
        prev = cx + bw / 2 + 8
    F.append(line(225, 258, 1255, 258, color=NEG, sw=2))
    F.append(text(740, 288, "одиниці — десятки мікросекунд, і всі ці мікросекунди сторінка "
                            "записувана для КОЖНОГО потоку процесу", size=14, color=NEG))

    F.append(line(70, 330, 1270, 330, color=MUTED, dash="6 6"))

    # ── нижня доріжка: WRPKRU
    F.append(text(70, 396, "WRPKRU", size=16, bold=True, anchor="start"))
    F.append(text(70, 420, "без ядра", size=13, color=MUTED, anchor="start"))

    lane2 = 430
    F.append(fitbox(225, lane2, 190, 78, "одна команда:\nнове значення PKRU", size=13, fill=GRN_F))
    F.append(line(225, 538, 445, 538, color=FIELD, sw=3))
    F.append(text(740, 570, "десятки тактів; таблиця сторінок не змінилася, тож скидати TLB нема чого, "
                            "а права змінилися лише в цього потоку", size=14, color=FIELD))

    F.append(text(1150, 470, "решта доріжки —", size=13, color=MUTED))
    F.append(text(1150, 492, "порожня", size=13, color=MUTED))

    render(os.path.join(IMG, 'two-roads.svg'), W, H, *F)


# ── 3. PKRU: уся мапа прав в одному регістрі ───────────────────────────────
def fig_pkru_layout():
    W, H = 1380, 500
    F = []

    F.append(text(W / 2, 36, "PKRU: права на всі шістнадцять ключів у 32 бітах", size=18, bold=True))

    x0, y0 = 60, 118
    cw, ch = 39, 56
    # приклад: ключ 0 — усе можна; 1 — доступ заборонено; 2 — лише читання; решта — заборона доступу
    vals = {}
    for k in range(16):
        if k == 0:
            vals[k] = (0, 0)
        elif k == 2:
            vals[k] = (0, 1)   # AD=0, WD=1
        else:
            vals[k] = (1, 0)   # AD=1

    F.append(text(x0 - 8, y0 - 44, "номер ключа", size=13, color=MUTED, anchor="start"))
    for k in range(16):
        gx = x0 + (15 - k) * 2 * cw
        F.append(rect(gx, y0, 2 * cw, ch, fill="#ffffff"))
        ad, wd = vals[k]
        F.append(rect(gx, y0, cw, ch, fill=RED_F if wd else GRN_F, sw=1))
        F.append(rect(gx + cw, y0, cw, ch, fill=RED_F if ad else GRN_F, sw=1))
        F.append(text(gx + cw / 2, y0 + 35, str(wd), size=16, bold=True))
        F.append(text(gx + cw + cw / 2, y0 + 35, str(ad), size=16, bold=True))
        F.append(text(gx + cw, y0 - 16, str(k), size=13, color=MUTED))

    F.append(text(x0 + 16 * 2 * cw + 14, y0 + 22, "біт 1", size=11, color=MUTED, anchor="start"))
    F.append(text(x0 - 14, y0 + 22, "біт 31", size=11, color=MUTED, anchor="end"))
    F.append(text(x0 + 16 * cw, y0 + ch + 26,
                  "на кожен ключ — два біти: WD (заборонити запис) і AD (заборонити доступ)",
                  size=14))

    # пояснення прикладу
    notes = [
        (300, GRN_F, "ключ 0\nдефолтний: 00\nусе дозволено"),
        (700, RED_F, "ключ 2 → 10\nWD = 1: читати можна,\nписати не можна"),
        (1110, RED_F, "ключі 1 і 3…15 → 01\nAD = 1: сторінка\nнедоторканна"),
    ]
    for cx, fill, s in notes:
        b, bw, bh = textbox(cx, 300, s, size=14, fill=fill, pad=14)
        F.append(b)

    F.append(text(W / 2, 400,
                  "Уся мапа прав процесу вміщується в один регістр — тому її заміна коштує одну команду.",
                  size=15))
    F.append(text(W / 2, 434,
                  "Номер ключа лежить не тут, а в записі таблиці сторінок: регістр каже «що можна групі», "
                  "таблиця — «до якої групи належить сторінка».",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'pkru-layout.svg'), W, H, *F)


# ── 4. Хроніка ідеї «ключ на сторінці, права в регістрі» ──────────────────
def fig_key_timeline():
    W, H = 1320, 640
    F = []

    F.append(text(W / 2, 40, "Одна конструкція, дві різні задачі за півстоліття", size=18, bold=True))

    hx = [70, 250, 700]
    hw = [170, 440, 550]
    heads = ["коли", "де втілено", "навіщо ключ саме там"]
    for x, w, h in zip(hx, hw, heads):
        F.append(fitbox(x, 72, w, 46, h, size=15, fill=FILL))

    rows = [
        ("1964", "IBM System/360: ключ на блок 2 КіБ",
         "іншої ізоляції немає — ключ і Є захист розділів", RED_F),
        ("1970-і й далі", "System/370 → z/Architecture",
         "ключі живуть у лінійці мейнфреймів донині", YEL_F),
        ("1980–90-і", "домени пам'яті ARM (регістр DACR)",
         "16 доменів на одну таблицю; в AArch64 їх прибрали", YEL_F),
        ("1990-і", "PA-RISC та Itanium: ключі доступу",
         "уперше межі ВСЕРЕДИНІ одного адресного простору", YEL_F),
        ("2016 / 2017", "Intel PKU: регістр PKRU",
         "Linux 4.6 і 4.9; залізо — Xeon Skylake-SP", GRN_F),
        ("2018", "POWER: регістр AMR (Linux 4.16)",
         "ті самі виклики pkey_* на іншій архітектурі", GRN_F),
        ("2022 / 2024", "arm64 POE: регістр POR_EL0",
         "Armv8.9; Linux 6.12 — і права на виконання теж", GRN_F),
    ]
    y = 132
    for when, where, why, fill in rows:
        F.append(fitbox(hx[0], y, hw[0], 56, when, size=14, fill=fill))
        F.append(fitbox(hx[1], y, hw[1], 56, where, size=14, fill=FILL))
        F.append(fitbox(hx[2], y, hw[2], 56, why, size=13, fill=FILL))
        y += 66

    F.append(text(W / 2, 610,
                  "Червоне — ключ замість ізоляції. Зелене — ключ як дешевий спосіб міняти вже наявну ізоляцію.",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'key-timeline.svg'), W, H, *F)


# ── 5. Довідка: біти ключа в записі таблиці та в коді помилки ─────────────
def fig_pte_and_error_code():
    W, H = 1420, 690
    F = []

    F.append(text(W / 2, 38, "Два бітових поля, якими механізм заявляє про себе апаратно",
                  size=18, bold=True))

    # ── запис таблиці сторінок
    F.append(text(80, 92, "запис таблиці сторінок, 64 біти", size=15, bold=True, anchor="start"))

    x0, y0, h = 80, 116, 76
    segs = [
        (100, "63\nNX", RED_F),
        (250, "62…59\nномер ключа", YEL_F),
        (200, "58…52\nвільні для ядра", FILL),
        (400, "51…12\nномер фізичного кадру", BLU_F),
        (310, "11…0\nP · R/W · U/S · A · D", GRN_F),
    ]
    x = x0
    for w, s, fill in segs:
        F.append(fitbox(x, y0, w, h, s, size=13, fill=fill))
        x += w

    F.append(text(455, y0 + h + 32,
                  "маска ключа  =  0x7800000000000000", size=14, bold=True))
    F.append(text(455, y0 + h + 58,
                  "ключ = (запис >> 59) & 0xF   ·   правиться лише через pkey_mprotect",
                  size=13, color=MUTED))

    F.append(line(80, 300, 1340, 300, color=MUTED, dash="6 6"))

    # ── код помилки збою сторінки
    F.append(text(80, 352, "код помилки збою сторінки (#PF), молодші біти",
                  size=15, bold=True, anchor="start"))

    bx, by, bw, bh = 80, 376, 175, 74
    bits = [
        ("6\nSHSTK", FILL),
        ("5\nPK", RED_F),
        ("4\nINSTR", FILL),
        ("3\nRSVD", FILL),
        ("2\nUSER", FILL),
        ("1\nWRITE", FILL),
        ("0\nPROT", FILL),
    ]
    for i, (s, fill) in enumerate(bits):
        F.append(fitbox(bx + i * bw, by, bw - 8, bh, s, size=13, fill=fill))

    # виноска на біт 5
    pk_cx = bx + 1 * bw + (bw - 8) / 2
    F.append(arrow(pk_cx, by + bh + 6, pk_cx, 500))
    b, _, _ = textbox(pk_cx + 250, 546,
                      ["PK = 1 — сторінка на місці й права ділянки її дозволяють,",
                       "звернення заборонив ключ; ядро не шукає сторінку далі"],
                      size=14, fill=RED_F, pad=14)
    F.append(b)

    F.append(text(W / 2, 640,
                  "Ядро перекладає цей біт у si_code = SEGV_PKUERR, а номер ключа зі "
                  "запису таблиці кладе в si_pkey.",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'pte-and-error-code.svg'), W, H, *F)


# ── 6. Стенд виміру: кому доводиться дізнаватися про зміну прав ────────────
def fig_bench_rig():
    W, H = 1360, 660
    F = []

    # ліворуч — вимірювальне ядро
    F.append(rect(60, 80, 340, 300, fill=BLU_F))
    F.append(text(230, 112, "ядро CPU 0", size=16, bold=True))
    F.append(text(230, 136, "вимірювальний потік", size=13, color=MUTED))
    F.append(fitbox(88, 158, 284, 66, "mprotect(base, len, …)", size=14, fill=FILL))
    F.append(fitbox(88, 268, 284, 66, "pkey_set(key, …)", size=14, fill=FILL))

    # верхня дорога: у ядро ОС і далі на всі ядра
    F.append(arrow(376, 191, 486, 168))
    F.append(rect(490, 118, 250, 108, fill=YEL_F))
    F.append(fitbox(506, 134, 218, 76,
                    "ядро ОС:\nправка записів таблиці\nі розсилка скидань", size=13,
                    fill=YEL_F, stroke=YEL_F, sw=0))

    cpus = [
        (880, 96, "CPU 1 · сусід читає ту саму пам'ять"),
        (880, 168, "CPU 2 · сусід читає ту саму пам'ять"),
        (880, 240, "CPU 3 · сусід читає ту саму пам'ять"),
        (880, 312, "…  ·  ще пʼятеро таких самих"),
    ]
    for x, y, s in cpus:
        F.append(fitbox(x, y, 420, 56, s, size=13, fill=RED_F))
        F.append(arrow(746, 172, x - 6, y + 28))

    F.append(text(812, 66, "переривання на КОЖНЕ ядро, де процес нещодавно був",
                  size=14, bold=True, color=POS))
    F.append(text(1090, 400,
                  "і ядро ОС чекає, поки кожне з них підтвердить скидання",
                  size=14, color=MUTED))

    # нижня дорога: нікуди не виходить
    F.append(arrow(376, 301, 486, 301))
    F.append(rect(490, 268, 250, 66, fill=GRN_F))
    F.append(fitbox(506, 280, 218, 42, "регістр PKRU ядра CPU 0", size=13,
                    fill=GRN_F, stroke=GRN_F, sw=0))
    F.append(text(490, 366, "нікуди не виходить: ані ядро ОС, ані сусідні ядра про це не знають",
                  size=14, color=FIELD, anchor="start"))

    # що змінюємо / що ні
    F.append(line(60, 430, 1300, 430, color=MUTED, dash="6 6"))
    F.append(fitbox(60, 458, 600, 150,
                    "ЗМІНЮЄМО тільки дві речі\n"
                    "розмір ділянки:  1 сторінка  ↔  1024 сторінки\n"
                    "сусіди на інших ядрах:  0  ↔  8", size=15, fill=YEL_F))
    F.append(fitbox(700, 458, 600, 150,
                    "УСЕ решта однакове\n"
                    "той самий один запис у пам'ять між «відчинити» й «зачинити»\n"
                    "той самий цикл, та сама машина, той самий прогін", size=15, fill=GRN_F))

    render(os.path.join(IMG, 'bench-rig.svg'), W, H, *F,
           title="Ціна зміни прав — це робота, яку мусять зробити ІНШІ ядра")


# ── 7. Форма результату: одна лінія пласка, друга росте ────────────────────
def fig_cost_shape():
    import math
    W, H = 1280, 700
    F = []

    X0, X1 = 230, 1180
    Y0, Y1 = 130, 540          # Y0 — верх (100 мкс), Y1 — низ (10 нс)

    def ypos(ns):
        return Y1 - (math.log10(ns) - 1.0) / 4.0 * (Y1 - Y0)

    # вісь і поділки
    F.append(line(X0, Y0 - 20, X0, Y1 + 10, color=INK, sw=2))
    for v, s in [(10, "10 нс"), (100, "100 нс"), (1000, "1 мкс"),
                 (10000, "10 мкс"), (100000, "100 мкс")]:
        y = ypos(v)
        F.append(line(X0, y, X1, y, color=MUTED, dash="4 8", sw=1))
        F.append(text(X0 - 18, y + 5, s, size=14, color=MUTED, anchor="end"))

    cols = [
        (350, "1 сторінка", "без сусідів", 800.0, 22.0),
        (620, "1024 сторінки", "без сусідів", 3500.0, 22.0),
        (890, "1 сторінка", "8 сусідів", 4000.0, 23.0),
        (1120, "1024 сторінки", "8 сусідів", 9000.0, 24.0),
    ]

    for x, a, b, _mp, _pk in cols:
        F.append(mtext(x, Y1 + 44, [a, b], size=14, color=INK))

    mp_pts = [(x, ypos(mp)) for x, _, _, mp, _ in cols]
    pk_pts = [(x, ypos(pk)) for x, _, _, _, pk in cols]

    for pts, color in ((mp_pts, POS), (pk_pts, NEG)):
        for i in range(len(pts) - 1):
            F.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          color=color, sw=3))
        for x, y in pts:
            F.append(circle(x, y, 8, fill=color, stroke=color))

    F.append(text(350, ypos(800) - 26, "пара mprotect", size=15, bold=True, color=POS))
    F.append(text(350, ypos(22) + 34, "пара pkey_set", size=15, bold=True, color=NEG))

    F.append(text(W / 2, 634,
                  "Абсолютні числа на вашій машині будуть інші. Незмінне одне: нижня лінія пласка.",
                  size=15, color=MUTED))

    render(os.path.join(IMG, 'cost-shape.svg'), W, H, *F,
           title="Форма результату (порядок величини, не обіцянка)")


if __name__ == '__main__':
    fig_two_sources()
    fig_two_roads()
    fig_pkru_layout()
    fig_key_timeline()
    fig_pte_and_error_code()
    fig_bench_rig()
    fig_cost_shape()
    print("ok")
