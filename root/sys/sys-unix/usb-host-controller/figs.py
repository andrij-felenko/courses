# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"
GREY_FILL = "#eeeeee"


# ── 1. Кільце TRB і біт циклу ───────────────────────────────────────────────
def fig_ring_and_cycle():
    W, H = 1330, 530
    p = []

    cells = [
        ("Normal\nC=1", GREY_FILL, MUTED),
        ("Normal\nC=1", GREEN_FILL, FIELD),
        ("Normal\nC=1", GREEN_FILL, FIELD),
        ("Normal\nC=1", GREEN_FILL, FIELD),
        ("Normal IOC\nC=1", GREEN_FILL, FIELD),
        ("торішнє\nC=0", RED_FILL, POS),
        ("торішнє\nC=0", RED_FILL, POS),
        ("Link TC\nC=1", BLUE_FILL, NEG),
    ]
    x0, cw, step = 60, 140, 152
    for i, (s, f, st) in enumerate(cells):
        p.append(fitbox(x0 + i * step, 140, cw, 90, s, size=14, fill=f, stroke=st))

    p.append(text(282, 95, "тут іде контролер", size=14, bold=True))
    p.append(arrow(282, 104, 282, 136))
    p.append(text(890, 95, "сюди пише драйвер", size=14, bold=True))
    p.append(arrow(890, 104, 890, 136))

    # повернення кільця
    p.append(line(1264, 185, 1300, 185))
    p.append(line(1300, 185, 1300, 300))
    p.append(line(1300, 300, 30, 300))
    p.append(line(30, 300, 30, 185))
    p.append(arrow(30, 185, 58, 185))

    p.append(text(60, 332,
                  "Link TRB із бітом Toggle Cycle вертає на початок і перевертає очікуваний біт",
                  size=14, color=MUTED, anchor="start"))

    p.append(fitbox(60, 380, 580, 120,
                    "контролер іде вперед, поки біт циклу в комірці\n"
                    "збігається з тим, чого він чекає цього кола;\n"
                    "не збігся — кільце для нього порожнє, він спиняється",
                    size=14, fill=FILL, stroke=LINE))
    p.append(fitbox(690, 380, 580, 120,
                    "драйвер заповнює тіло TRB, а біт циклу пише\n"
                    "ОСТАННІМ, після бар'єра запису: інакше контролер\n"
                    "устигне побачити недописану комірку як чинну",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'ring-and-cycle.svg'), W, H, *p)


# ── 2. Що лежить у пам'яті, а що в регістрах ────────────────────────────────
def fig_memory_map():
    W, H = 1360, 830
    p = []

    p.append(text(340, 40, "оперативна пам'ять — спільна", size=15, bold=True))
    p.append(text(1060, 40, "регістри контролера — MMIO", size=15, bold=True))

    p.append(fitbox(60, 60, 560, 76,
                    "DCBAA\nмасив вказівників на контексти пристроїв",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(340, 136, 340, 174))

    p.append(fitbox(60, 176, 560, 120,
                    "Device Context слота\n"
                    "Slot Context: швидкість, маршрут через хаби, порт\n"
                    "Endpoint Context 1…31: тип, розмір пакета, інтервал",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(340, 296, 340, 334))

    p.append(fitbox(60, 336, 560, 90,
                    "кільце передач кінцевої точки\nсвоє на кожну ввімкнену кінцеву точку",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(60, 470, 560, 80,
                    "командне кільце: драйвер → контролер",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(60, 590, 560, 90,
                    "кільце подій і таблиця ERST\nконтролер → драйвер",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(820, 60, 480, 110,
                    "Operational\nDCBAAP · CRCR · USBCMD · PORTSC",
                    size=14, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(820, 250, 480, 90,
                    "Doorbell Array\nпо регістру на кожен слот",
                    size=14, fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(820, 560, 480, 110,
                    "Runtime\nERSTBA · ERDP · IMOD",
                    size=14, fill=WARM_FILL, stroke=WARM))

    p.append(text(719, 266, "запис у дзвінок", size=13, bold=True))
    p.append(arrow(624, 285, 814, 285))

    p.append(text(719, 601, "події через DMA", size=13, bold=True))
    p.append(arrow(814, 620, 626, 620))

    p.append(fitbox(60, 720, 1240, 76,
                    "Драйвер лише готує структури в пам'яті й один раз тисне дзвінок.\n"
                    "Далі контролер читає кільця сам через DMA, а назад пише події — "
                    "процесор не бере участі в жодній окремій транзакції.",
                    size=14, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'memory-map.svg'), W, H, *p)


# ── 3. Поділ мікрокадру між періодичним і рештою ────────────────────────────
def fig_microframe_budget():
    W, H = 1330, 520
    p = []

    top, bottom = 120, 340          # 220 px  ↔  7500 байтів
    per_byte = (bottom - top) / 7500.0
    cap_y = top + 6000 * per_byte   # стеля періодичних, 80 %

    p.append(text(300, 80, "кадр 1 мс = вісім мікрокадрів по 125 мкс",
                  size=15, bold=True, anchor="start"))

    x0, cw, step = 300, 110, 116
    for i in range(8):
        x = x0 + i * step
        p.append(rect(x, top, cw, 3072 * per_byte, fill=GREEN_FILL, stroke=FIELD, rx=2))
        p.append(rect(x, top + 3072 * per_byte, cw, 3072 * per_byte,
                      fill=RED_FILL, stroke=POS, rx=2))
        p.append(rect(x, top + 6144 * per_byte, cw, bottom - (top + 6144 * per_byte),
                      fill=GREY_FILL, stroke=MUTED, rx=2))
        p.append(text(x + cw / 2, 366, str(i + 1), size=13, color=MUTED))

    p.append(line(292, cap_y, 1240, cap_y, color=POS, sw=2, dash="8 6"))

    p.append(text(285, top + 5, "7500 Б — увесь мікрокадр", size=13, color=MUTED, anchor="end"))
    p.append(text(285, cap_y + 5, "6000 Б — стеля періодичних", size=13, color=POS, anchor="end"))
    p.append(text(285, bottom + 5, "0", size=13, color=MUTED, anchor="end"))

    p.append(fitbox(60, 410, 380, 76,
                    "ізохронна камера\n3072 Б на мікрокадр",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(470, 410, 400, 76,
                    "друга така сама камера\nразом 6144 Б — стеля пробита",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(fitbox(900, 410, 380, 76,
                    "bulk і control\nберуть те, що лишилось",
                    size=14, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'microframe-budget.svg'), W, H, *p)


# ── 4. Чотири регістрові простори і як їх знайти ────────────────────────────
def fig_register_spaces():
    W, H = 1400, 700
    p = []

    p.append(text(60, 46, "BAR0 контролера — одна суцільна область MMIO; де починається кожен "
                          "простір, каже сам контролер", size=15, bold=True, anchor="start"))

    # ліворуч — Capability
    p.append(fitbox(60, 90, 420, 300, "", fill=WARM_FILL, stroke=WARM))
    p.append(text(270, 118, "Capability  (BAR0 + 0x00)", size=15, bold=True))

    rows = [
        ("0x00", "CAPLENGTH · HCIVERSION"),
        ("0x04", "HCSPARAMS1 — слоти, переривачі, порти"),
        ("0x08", "HCSPARAMS2 — ERST Max, scratchpad"),
        ("0x0C", "HCSPARAMS3 — затримки виходу U1/U2"),
        ("0x10", "HCCPARAMS1 — AC64, CSZ, xECP"),
        ("0x14", "DBOFF"),
        ("0x18", "RTSOFF"),
    ]
    for i, (off, name) in enumerate(rows):
        y = 140 + i * 34
        p.append(text(80, y, off, size=13, color=MUTED, anchor="start"))
        p.append(text(146, y, name, size=13, anchor="start"))

    # праворуч — три простори
    p.append(fitbox(760, 90, 580, 120,
                    "Operational  (BAR0 + CAPLENGTH)\n"
                    "USBCMD · USBSTS · CRCR · DCBAAP · CONFIG\n"
                    "PORTSC — від +0x400, по 16 байтів на порт",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(760, 250, 580, 120,
                    "Runtime  (BAR0 + RTSOFF)\n"
                    "MFINDEX за +0x00, набори переривачів від +0x20\n"
                    "IMAN · IMOD · ERSTSZ · ERSTBA · ERDP, по 32 байти",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(760, 410, 580, 120,
                    "Doorbell  (BAR0 + DBOFF)\n"
                    "по 32-бітовому регістру на слот\n"
                    "DB0 — командне кільце, DB1…DBn — пристрої",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(arrow(500, 150, 754, 150))
    p.append(text(627, 138, "CAPLENGTH", size=13, color=MUTED))

    p.append(line(500, 344, 620, 344))
    p.append(line(620, 344, 620, 310))
    p.append(arrow(620, 310, 754, 310))
    p.append(text(660, 366, "RTSOFF", size=13, color=MUTED, anchor="start"))

    p.append(line(500, 310, 560, 310))
    p.append(line(560, 310, 560, 470))
    p.append(arrow(560, 470, 754, 470))
    p.append(text(600, 496, "DBOFF", size=13, color=MUTED, anchor="start"))

    p.append(fitbox(60, 580, 1280, 76,
                    "Жодне зміщення не зашите в драйвер: він читає CAPLENGTH, DBOFF і RTSOFF "
                    "із Capability й лише тоді знає адреси решти.\n"
                    "Тому та сама реалізація однаково працює з контролером на PCIe і з блоком, "
                    "вбудованим у систему на кристалі.",
                    size=14, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'register-spaces.svg'), W, H, *p)


# ── 5. Розкладка TRB ────────────────────────────────────────────────────────
def fig_trb_fields():
    W, H = 1400, 560
    p = []

    p.append(text(60, 46, "TRB — рівно 16 байтів: чотири 32-бітові слова, little-endian",
                  size=15, bold=True, anchor="start"))

    p.append(fitbox(60, 76, 620, 86,
                    "Parameter — слова 0 і 1 (64 біти)\n"
                    "адреса буфера · 8 байтів SETUP · вказівник на TRB",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(700, 76, 300, 86,
                    "Status — слово 2\nдовжина, TD Size, переривач",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(1020, 76, 320, 86,
                    "Control — слово 3\nтип, прапорці, біт циклу",
                    size=14, fill=WARM_FILL, stroke=WARM))

    p.append(text(60, 214, "Слово 2 у передавальному TRB", size=14, bold=True, anchor="start"))
    p.append(fitbox(60, 232, 420, 52, "довжина буфера — біти 16:0",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(500, 232, 380, 52, "TD Size — біти 21:17",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(900, 232, 440, 52, "Interrupter Target — біти 31:22",
                    size=13, fill=BLUE_FILL, stroke=NEG))

    p.append(text(60, 340, "Слово 3, молодші біти (нумерація зростає праворуч)",
                  size=14, bold=True, anchor="start"))

    bits = [("C", "0"), ("ENT", "1"), ("ISP", "2"), ("NS", "3"), ("CH", "4"),
            ("IOC", "5"), ("IDT", "6"), ("—", "7"), ("—", "8"), ("BEI", "9")]
    x0, cw, gap = 60, 74, 6
    for i, (nm, bt) in enumerate(bits):
        x = x0 + i * (cw + gap)
        p.append(fitbox(x, 360, cw, 50, nm, size=13, fill=WARM_FILL, stroke=WARM))
        p.append(text(x + cw / 2, 428, bt, size=12, color=MUTED))

    xt = x0 + 10 * (cw + gap)
    p.append(fitbox(xt, 360, 240, 50, "TRB Type — 15:10", size=13,
                    fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(xt + 260, 360, 300, 50, "31:16 — за типом TRB", size=13,
                    fill=GREY_FILL, stroke=MUTED))

    p.append(fitbox(60, 470, 1280, 60,
                    "Біт C драйвер пише ОСТАННІМ: доти комірка для контролера — чуже сміття "
                    "з попереднього кола.",
                    size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'trb-fields.svg'), W, H, *p)


# ── 6. Input Context і нумерація DCI ────────────────────────────────────────
def fig_input_context():
    W, H = 1400, 560
    p = []

    p.append(text(60, 46, "Input Context: маска ліворуч, вміст праворуч — контролер бере "
                          "лише позначені шматки", size=15, bold=True, anchor="start"))

    boxes = [
        ("Input Control\nDrop · Add", GREY_FILL, MUTED, "—"),
        ("Slot Context", BLUE_FILL, NEG, "0"),
        ("EP0 Control", GREEN_FILL, FIELD, "1"),
        ("EP1 OUT", GREEN_FILL, FIELD, "2"),
        ("EP1 IN", GREEN_FILL, FIELD, "3"),
        ("…", GREY_FILL, MUTED, "…"),
        ("EP15 IN", GREEN_FILL, FIELD, "31"),
    ]
    x0, bw, gap = 60, 172, 12
    for i, (nm, f, st, dci) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        p.append(fitbox(x, 170, bw, 84, nm, size=13, fill=f, stroke=st))
        p.append(text(x + bw / 2, 288, "DCI " + dci, size=13, color=MUTED))

    # біти масок над блоками
    p.append(text(60, 130, "біти маски", size=12, color=MUTED, anchor="start"))
    for i, lbl in enumerate(["", "A0", "A1", "A2", "A3", "…", "A31"]):
        if not lbl:
            continue
        x = x0 + i * (bw + gap) + bw / 2
        p.append(text(x, 130, lbl, size=13, bold=True))
        p.append(arrow(x, 138, x, 166))

    p.append(fitbox(60, 340, 620, 100,
                    "DCI = 2 × номер кінцевої точки + 1, якщо напрям IN\n"
                    "керуюча EP0 — завжди DCI 1, Slot Context — DCI 0",
                    size=14, fill=FILL, stroke=LINE))
    p.append(fitbox(720, 340, 620, 100,
                    "Drop-біти D0 і D1 зарезервовані: слот і керуючу точку\n"
                    "прибрати не можна, поки живий сам пристрій",
                    size=14, fill=WARM_FILL, stroke=WARM))

    p.append(fitbox(60, 470, 1280, 60,
                    "Контролер копіює позначені шматки у свій Device Context сам — "
                    "драйвер туди не пише ніколи.",
                    size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'input-context.svg'), W, H, *p)


# ── Ціна однієї транзакції у своєму бюджеті ─────────────────────────────────
def fig_transaction_cost():
    W, H = 1360, 620
    p = []

    p.append(text(60, 58, "Ціна однієї транзакції у своєму бюджеті",
                  size=17, bold=True, anchor="start"))
    p.append(text(60, 88, "смуга — увесь бюджет; заповнене — те, що з'їдає одна транзакція",
                  size=13, color=MUTED, anchor="start"))

    x0, bw, bh = 420, 760, 44
    rows = [
        (150, ["низька 1.5 Мбіт/с · interrupt IN 8 Б", "бюджет — кадр 1000 мкс"],
         1000.0, 65.7, 43.3, 8.9, ["118 мкс", "11.8 % кадру"]),
        (250, ["повна 12 Мбіт/с · ізохронна OUT 192 Б", "бюджет — кадр 1000 мкс"],
         1000.0, 7.3, 128.3, 21.6, ["157 мкс", "15.7 % кадру"]),
        (350, ["повна 12 Мбіт/с · ізохронна IN 1023 Б", "бюджет — кадр 1000 мкс"],
         1000.0, 8.3, 683.7, 114.2, ["806 мкс", "80.6 % кадру"]),
        (450, ["висока 480 Мбіт/с · ізохронна IN 1024 Б", "бюджет — мікрокадр 125 мкс"],
         125.0, 0.64, 17.07, 2.84, ["20.6 мкс", "16.4 % мікрокадру"]),
    ]

    for y, label, budget, over, data, stuff, right in rows:
        p.append(mtext(400, y + 15, label, size=13, anchor="end"))
        p.append(rect(x0, y, bw, bh, fill="#ffffff", stroke=MUTED, sw=1.2))
        cur = x0
        for val, f, s in ((over, WARM_FILL, WARM), (data, GREEN_FILL, FIELD),
                          (stuff, RED_FILL, POS)):
            p.append(rect(cur, y, bw * val / budget, bh, fill=f, stroke=s, sw=1.2, rx=2))
            cur += bw * val / budget
        p.append(mtext(1200, y + 15, right, size=13, anchor="start"))

    ly = 552
    for lx, f, s, cap in ((420, WARM_FILL, WARM, "службові байти транзакції"),
                          (700, GREEN_FILL, FIELD, "корисні дані"),
                          (880, RED_FILL, POS, "надбавка бітстафінгу (до 7/6)")):
        p.append(rect(lx, ly - 13, 22, 16, fill=f, stroke=s, sw=1.2, rx=2))
        p.append(text(lx + 28, ly, cap, size=13, anchor="start"))

    render(os.path.join(IMG, 'transaction-cost.svg'), W, H, *p)


# ── Split-транзакція крізь транслятор ───────────────────────────────────────
def fig_split_budget():
    W, H = 1360, 600
    p = []

    p.append(text(60, 55, "Повношвидкісна ізохронна транзакція 512 Б крізь транслятор",
                  size=17, bold=True, anchor="start"))

    x0, cw, step = 250, 126, 132
    cx = [x0 + i * step + cw / 2 for i in range(8)]
    for i in range(8):
        p.append(text(cx[i], 104, "мкф %d" % i, size=13, color=MUTED))

    hs = {0: ("S", WARM_FILL, WARM)}
    for i in range(2, 7):
        hs[i] = ("C", BLUE_FILL, NEG)
    for i in range(8):
        s, f, st = hs.get(i, ("", "#ffffff", MUTED))
        p.append(rect(x0 + i * step, 120, cw, 64, fill=f, stroke=st, sw=1.2))
        if s:
            p.append(text(cx[i], 161, s, size=20, bold=True, color=st))

    tt = {1: "187.5 Б", 2: "187.5 Б", 3: "187.5 Б", 4: "44.5 Б"}
    for i in range(8):
        s = tt.get(i)
        f, st = (GREEN_FILL, FIELD) if s else ("#ffffff", MUTED)
        p.append(rect(x0 + i * step, 225, cw, 64, fill=f, stroke=st, sw=1.2))
        if s:
            p.append(text(cx[i], 262, s, size=14))

    for i, v in enumerate([125, 125, 125, 125, 125, 125, 30, 0]):
        f, st = (GREY_FILL, MUTED) if i < 6 else (RED_FILL, POS)
        p.append(rect(x0 + i * step, 330, cw, 50, fill=f, stroke=st, sw=1.2))
        p.append(text(cx[i], 361, str(v), size=15, bold=True, color=st))

    p.append(mtext(235, 146, ["висока шина", "480 Мбіт/с"], size=13, anchor="end"))
    p.append(mtext(235, 251, ["конвеєр транслятора", "187.5 Б за мікрокадр"],
                   size=13, anchor="end"))
    p.append(mtext(235, 351, ["бюджет FS-боку", "мкс на мікрокадр"], size=13, anchor="end"))

    p.append(text(250, 410,
                  "хвіст кадру порожній: повношвидкісна робота мусить скінчитися до межі кадру",
                  size=13, color=MUTED, anchor="start"))

    p.append(fitbox(60, 434, 610, 116,
                    "512 · 7/6 + службові ≈ 607 Б «сирого» часу\n"
                    "607 / 187.5 = 3.24 → чотири мікрокадри конвеєра,\n"
                    "плюс один на невирівняний хвіст → 5 complete-split",
                    size=14, fill=FILL, stroke=LINE))
    p.append(fitbox(710, 434, 590, 116,
                    "з високої шини Linux списує 31 блок протоколу\n"
                    "і 94 блоки даних: 125 · 4 = 500 Б за мікрокадр,\n"
                    "тобто 32 Мбіт/с — майже втричі більше за 12 Мбіт/с",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'split-budget.svg'), W, H, *p)


fig_ring_and_cycle()
fig_memory_map()
fig_microframe_budget()
fig_register_spaces()
fig_trb_fields()
fig_input_context()
fig_transaction_cost()
fig_split_budget()
print("ok")
