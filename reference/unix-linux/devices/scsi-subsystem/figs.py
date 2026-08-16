# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE = "#eaf0fd"
GREEN = "#eaf6ef"
WARM = "#fff6e5"
RED = "#fdecea"
GREY = "#eceff1"


# ── 1. Три яруси драйверів ──────────────────────────────────────────────────
def fig_layers():
    W, H = 1260, 740
    p = []
    cx = 630

    def band_label(y, s):
        p.append(text(cx, y, s, size=16, bold=True))

    def gap_arrows(y1, y2, label=None):
        p.append(arrow(cx - 85, y1, cx - 85, y2))
        p.append(arrow(cx + 85, y2, cx + 85, y1))
        if label:
            p.append(text(cx - 125, (y1 + y2) / 2 + 5, "команда (CDB)",
                          size=13, anchor="end", color=MUTED))
            p.append(text(cx + 125, (y1 + y2) / 2 + 5, "статус + сенс-дані",
                          size=13, anchor="start", color=MUTED))

    # ── верхній ярус
    band_label(58, "Верхній ярус — що це за пристрій")
    tops = [("sd", "диски"), ("sr", "приводи"), ("st", "стрічка"),
            ("ses", "корпус"), ("sg", "наскрізний")]
    xs = [250, 440, 630, 820, 1010]
    h_top = 0
    for x, (name, what) in zip(xs, tops):
        f, w, h = textbox(x, 120, [name, what], size=13, pad=12,
                          fill=BLUE, stroke=LINE, min_w=110)
        p.append(f)
        h_top = h
    y_top_bot = 120 + h_top / 2

    gap_arrows(y_top_bot + 10, 246, label=True)

    # ── середній ярус
    band_label(288, "Середній ярус — як влаштована команда")
    f, w_mid, h_mid = textbox(cx, 360,
                              ["scsi_mod",
                               "черга команд і її глибина · повтори · строки очікування",
                               "виявлення пристроїв · обробник помилок"],
                              size=14, pad=18, fill=WARM, stroke=LINE, min_w=900)
    p.append(f)

    gap_arrows(360 + h_mid / 2 + 10, 450)

    # ── нижній ярус
    band_label(492, "Нижній ярус — як донести байти")
    lows = [["SAS"], ["Fibre", "Channel"], ["iSCSI"], ["USB", "(UAS)"],
            ["libata", "→ SATA"]]
    xs2 = [230, 430, 630, 830, 1030]
    h_low = 0
    for x, lines in zip(xs2, lows):
        f, w, h = textbox(x, 552, lines, size=13, pad=12,
                          fill=GREEN, stroke=LINE, min_w=130)
        p.append(f)
        h_low = h

    gap_arrows(552 + h_low / 2 + 10, 632)

    f, w_d, h_d = textbox(cx, 668, ["носій"], size=15, pad=14,
                          fill=GREY, stroke=LINE, bold=True, min_w=200)
    p.append(f)

    p.append(text(cx, 726,
                  "адреса пристрою — контролер : канал : ціль : логічна одиниця,   напр. 6:0:0:0",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'scsi-layers.svg'), W, H, *p,
           title="Три яруси драйверів SCSI у Linux")


# ── 2. Чотири вироки над невдалою командою ──────────────────────────────────
def fig_disposition():
    W, H = 1400, 700
    p = []

    p.append(text(700, 58, "Невдала команда: від причини до вироку",
                  size=17, bold=True))

    rows = [
        (["BUSY   ·   TASK SET FULL",
          "пристрій справний, але захлинувся"], WARM,
         ["назад у чергу",
          "чекати звичайним порядком;",
          "надалі посилати менше команд"], WARM),
        (["NOT READY   ·   пристрій готується",
          "диск розкручується, масив збирається"], BLUE,
         ["повторити",
          "поки не вичерпано дозволені спроби",
          "(для диска — типово п'ять)"], BLUE),
        (["MEDIUM ERROR   ·   непоправне читання",
          "ILLEGAL REQUEST   ·   RESERVATION CONFLICT"], RED,
         ["віддати нагору",
          "повтор нічого не змінить —",
          "це помилка вводу-виводу"], RED),
        (["мовчання   ·   таймер сплив   ·   DID_TIME_OUT",
          "сенс-даних немає взагалі"], GREY,
         ["до обробника помилок",
          "скасувати команду,",
          "а не вийде — скидати"], GREY),
    ]

    y = 150
    for left, lcol, right, rcol in rows:
        fl, wl, hl = textbox(360, y, left, size=13, pad=15,
                             fill=lcol, stroke=LINE, min_w=520)
        fr, wr, hr = textbox(1080, y, right, size=13, pad=15,
                             fill=rcol, stroke=LINE, min_w=420)
        p.append(fl)
        p.append(fr)
        p.append(arrow(360 + wl / 2 + 14, y, 1080 - wr / 2 - 14, y))
        y += 140

    p.append(text(700, 660,
                  "вирішує одна функція ядра — scsi_decide_disposition",
                  size=14, color=MUTED))

    render(os.path.join(IMG, 'disposition.svg'), W, H, *p,
           title="Чотири вироки над невдалою командою SCSI")


# ── 3. Від строку очікування до драбини скидань ─────────────────────────────
def fig_eh_timeline():
    W, H = 1260, 810
    p = []

    ax = 250
    bx = 310
    bw = 890

    rows = [
        ("0 с", ["контролерові віддано команду, таймер пішов"], GREY),
        ("30 с", ["строк очікування сплив — відповіді немає"], WARM),
        ("одразу", ["ядро просить контролер скасувати саме цю команду",
                    "решта команд адаптера працює далі"], BLUE),
        ("скасовано", ["команда тихо йде на повтор — ніхто нічого не помітив"], GREEN),
        ("не скасовано", ["доля команди невідома: пристрій може прокинутися",
                          "й записати в буфер, уже відданий іншому"], RED),
        ("пауза", ["обробник чекає, доки решта команд адаптера завершиться",
                   "або впаде за власним таймером — це і є та зупинка,",
                   "яку видно на здорових дисках того самого контролера"], RED),
        ("драбина", ["сенс-дані → START STOP UNIT → скидання логічної одиниці →",
                     "цілі → шини → контролера → пристрій вимкнено"], WARM),
    ]

    y = 82
    for label, lines, col in rows:
        h = 40 + (len(lines) - 1) * 24
        cy = y + h / 2
        p.append(text(ax - 34, cy + 5, label, size=14, anchor="end", bold=True))
        p.append(circle(ax, cy, 7, fill="#ffffff", stroke=LINE, sw=2))
        p.append(fitbox(bx, y, bw, h, lines, size=14, fill=col, stroke=LINE))
        y += h + 36

    p.insert(0, line(ax, 70, ax, y - 30, color=LINE, sw=2))

    render(os.path.join(IMG, 'eh-timeline.svg'), W, H, *p,
           title="Що відбувається, коли пристрій замовк")


# ── 4. Мова лишається, дріт міняється ───────────────────────────────────────
def fig_timeline():
    W, H = 1420, 660
    p = []
    xs = [200, 445, 690, 935, 1180]
    spine_y = 320

    p.append(text(710, 60, "Мова лишається, дріт міняється", size=17, bold=True))

    p.append(text(710, 108, "як складався словник", size=14, color=MUTED))
    top = [
        (["1979–1981", "SASI", "Shugart Associates"], BLUE),
        (["жовтень 1981", "спільна подача", "Shugart і NCR"], BLUE),
        (["червень 1986", "ANSI X3.131", "SCSI-1"], WARM),
        (["1996", "SAM: команди окремо", "від транспорту"], WARM),
        (["2003", "SPI-5 — остання мідь", "жодного пристрою"], RED),
    ]
    h_top = 0
    for x, (lines, col) in zip(xs, top):
        f, w, h = textbox(x, 178, lines, size=13, pad=13,
                          fill=col, stroke=LINE, min_w=208)
        p.append(f)
        h_top = h
    for x in xs:
        p.append(line(x, 178 + h_top / 2 + 8, x, spine_y - 36, color=LINE, sw=1.2))

    p.append(arrow(120, spine_y, 1300, spine_y, sw=2.4))
    p.append(text(710, spine_y - 22, "той самий блок опису команди (CDB)",
                  size=14, bold=True))

    p.append(text(710, 372, "транспорти, що успадкували ті самі CDB",
                  size=14, color=MUTED))
    low = [
        ["FCP", "оптика, 1996"],
        ["USB BOT", "флешка, 1999"],
        ["iSCSI", "TCP/IP, 2004"],
        ["SAS", "серійна мідь, 2004"],
        ["UAS", "черга по USB, 2010"],
    ]
    h_low = 0
    for x, lines in zip(xs, low):
        f, w, h = textbox(x, 490, lines, size=13, pad=13,
                          fill=GREEN, stroke=LINE, min_w=208)
        p.append(f)
        h_low = h
    for x in xs:
        p.append(line(x, spine_y + 72, x, 490 - h_low / 2 - 8, color=LINE, sw=1.2))

    p.append(text(710, 600,
                  "хронологія рядів незалежна: верхній ряд — редакції мови, нижній — дроти",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'scsi-timeline.svg'), W, H, *p,
           title="Від SASI до SCSI: мова й транспорти")


# ── 5. Скільки байтів сенс-буфера справді ваші (для вставки proj) ───────────
def fig_sense_extent():
    W, H = 1300, 470
    p = []
    CUT = 780

    p.append(text(650, 46, "Скільки байтів сенс-буфера справді ваші",
                  size=17, bold=True))
    p.append(text(650, 86,
                  "буфер, який дав виклик — у ядра це 96 байтів на кожну команду",
                  size=13, color=MUTED))

    p.append(fitbox(110, 104, CUT - 110, 56,
                    ["заповнено пристроєм: 8 + байт 7 (додаткова довжина)"],
                    size=14, fill=GREEN))
    p.append(fitbox(CUT, 104, 1200 - CUT, 56,
                    ["решта — сміття від попередньої команди"],
                    size=14, fill=GREY))

    p.append(text(110, 276, "ланцюг описувачів у форматі 0x72 / 0x73",
                  size=14, bold=True, anchor="start"))

    p.append(fitbox(110, 300, 180, 74, ["шапка — 8 байтів"],
                    size=13, fill=BLUE))
    p.append(arrow(290, 337, 320, 337))
    p.append(fitbox(320, 300, 250, 74,
                    ["тип 0x00 · довж. 0x0A", "номер блока, 8 байтів"],
                    size=13, fill=GREEN))
    p.append(arrow(570, 337, 600, 337))
    p.append(fitbox(600, 300, 180, 74, ["тип 0x05", "довж. 0x02"],
                    size=13, fill=GREEN))
    p.append(arrow(CUT, 337, 810, 337))
    p.append(fitbox(810, 300, 300, 74,
                    ["тип 0x0C · довж. 0x1E", "обіцяє 32 байти, яких немає"],
                    size=13, fill=RED))

    p.append(line(CUT, 100, CUT, 400, color=LINE, sw=1.6, dash="6,5"))

    p.append(text(110, 432, "крок до наступного описувача = 2 + байт довжини",
                  size=13, color=MUTED, anchor="start"))
    p.append(text(810, 432, "далі читати не можна",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'sense-extent.svg'), W, H, *p,
           title="Дві довжини сенс-буфера й ланцюг описувачів")


if __name__ == '__main__':
    fig_layers()
    fig_disposition()
    fig_eh_timeline()
    fig_timeline()
    fig_sense_extent()
    print("ok")
