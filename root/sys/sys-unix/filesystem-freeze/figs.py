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
GRAY_FILL = "#eef1f4"
WARM = "#b8860b"


# ── 1. Сходи заморожування: три бар'єри й скидання між ними ─────────────────
def fig_freeze_levels():
    W, H = 1280, 940
    p = []

    p.append(text(50, 52, "Джерела змін вимикають зовні всередину — бо скидання на носій саме потребує "
                          "роботи файлової системи",
                  size=17, anchor="start", bold=True))

    LX, LW = 50, 250          # назва стану
    MX, MW = 320, 470         # хто ще може змінювати
    RX, RW = 810, 420         # що робимо, ставши на сходинку
    y0, bh, gap = 150, 118, 46

    p.append(fitbox(LX, y0 - 48, LW, 38, "стан суперблока", size=13, bold=True,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.4, color=MUTED))
    p.append(fitbox(MX, y0 - 48, MW, 38, "хто ще здатен змінити том", size=13, bold=True,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.4, color=MUTED))
    p.append(fitbox(RX, y0 - 48, RW, 38, "що ядро робить, ставши сюди", size=13, bold=True,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.4, color=MUTED))

    ROWS = [
        ("SB_UNFROZEN\nзвичайна робота",
         "системні виклики запису\nсторінкові збої запису в mmap\nвнутрішні потоки файлової системи",
         "нічого — том живе\nсвоїм життям",
         GRAY_FILL, MUTED, BG, INK),
        ("SB_FREEZE_WRITE\nперекрито виклики",
         "сторінкові збої запису в mmap\nвнутрішні потоки файлової системи",
         "чекати, поки вийдуть\nписарі, що вже\nвсередині",
         BLUE_FILL, NEG, BLUE_FILL, NEG),
        ("SB_FREEZE_PAGEFAULT\nперекрито збої",
         "внутрішні потоки файлової системи:\nзапис назад, фіксація журналу,\nвідкладене виділення блоків",
         "sync_filesystem():\nззовні писати вже нікому —\nвивозимо все на носій",
         WARM_FILL, WARM, WARM_FILL, WARM),
        ("SB_FREEZE_FS\nперекрито внутрішнє",
         "ніхто",
         "->freeze_fs():\nдописати журнал,\nпозначити суперблок чистим",
         GREEN_FILL, FIELD, GREEN_FILL, FIELD),
    ]

    for i, (state, who, act, sfill, scolor, afill, acolor) in enumerate(ROWS):
        y = y0 + i * (bh + gap)
        p.append(fitbox(LX, y, LW, bh, state, size=14, bold=True,
                        fill=sfill, stroke=scolor, sw=1.8, color=INK))
        p.append(fitbox(MX, y, MW, bh, who, size=13,
                        fill=BG, stroke=INK if i < 3 else FIELD, sw=1.5,
                        color=INK if i < 3 else FIELD, bold=(i == 3)))
        p.append(fitbox(RX, y, RW, bh, act, size=13,
                        fill=afill, stroke=acolor, sw=1.6, color=INK))
        if i < len(ROWS) - 1:
            p.append(arrow(LX + LW / 2, y + bh + 4, LX + LW / 2, y + bh + gap - 4, color=MUTED))

    y_end = y0 + len(ROWS) * (bh + gap)
    p.append(fitbox(LX, y_end + 6, 1180, 66,
                    "На кожній сходинці коло тих, хто ще може щось змінити, звужується; "
                    "скидання на носій одне — між зовнішніми бар'єрами й внутрішнім.\n"
                    "Розморожування знімає бар'єри у зворотному порядку, і черга писарів рушає далі.",
                    size=14, fill=BG, stroke=MUTED, sw=1.5, color=INK))

    render(os.path.join(IMG, 'freeze-levels.svg'), W, H, *p,
           title="Три бар'єри заморожування і скидання між ними")


# ── 2. Вікно заморожування в часі ───────────────────────────────────────────
def fig_freeze_window():
    W, H = 1300, 720
    p = []

    p.append(text(50, 50, "Вікно заморожування: наявні писарі добігають, нові стають у чергу, "
                          "знімок падає в тишу",
                  size=17, anchor="start", bold=True))

    AX0, AX1 = 90, 1240
    FREEZE_X, THAW_X = 420, 900
    BASE = 560

    # смуга вікна
    p.append(rect(FREEZE_X, 112, THAW_X - FREEZE_X, BASE - 112 + 30,
                  fill="#f7fbf8", stroke=FIELD, sw=1.6, rx=8))
    p.append(text((FREEZE_X + THAW_X) / 2, 138, "вікно заморожування", size=15, bold=True, color=FIELD))

    # смуги писарів
    LANES = [
        (190, "писар A", 150, 470, RED_FILL, POS,
         "зайшов до бар'єра — його дочекалися"),
        (250, "писар B", 150, 505, RED_FILL, POS,
         "довга транзакція — саме вона задає довжину чекання"),
        (310, "писар C", 560, THAW_X, GRAY_FILL, MUTED,
         "прийшов у вікно — спить непереривно до відтавання"),
        (370, "писар D", 780, THAW_X, GRAY_FILL, MUTED,
         "те саме: жодного запису у вікні не проходить"),
    ]
    for y, name, x_from, x_to, fill, color, note in LANES:
        p.append(text(80, y + 5, name, size=13, anchor="end", bold=True, color=MUTED))
        p.append(rect(x_from, y - 13, x_to - x_from, 26, fill=fill, stroke=color, sw=1.5, rx=5))
        p.append(text(x_to + 14, y + 5, note, size=12, anchor="start", color=color))

    # смуга роботи ядра
    p.append(text(80, 445, "ядро", size=13, anchor="end", bold=True, color=MUTED))
    STAGES = [
        (FREEZE_X, 110, "бар'єри", BLUE_FILL, NEG),
        (FREEZE_X + 110, 140, "скидання на носій", WARM_FILL, WARM),
        (FREEZE_X + 250, 120, "журнал дописано,\nсуперблок чистий", GREEN_FILL, FIELD),
    ]
    for x_from, w, label, fill, color in STAGES:
        p.append(fitbox(x_from, 418, w, 54, label, size=12, fill=fill, stroke=color, sw=1.5))
    p.append(text(845, 449, "тиша", size=12, color=MUTED))

    # вісь часу
    p.append(line(AX0, BASE, AX1, BASE, color=INK, sw=1.8))
    p.append(text(AX1, BASE + 26, "час", size=13, anchor="end", color=MUTED))

    for x, label, color in [(FREEZE_X, "FIFREEZE", NEG), (THAW_X, "FITHAW", NEG)]:
        p.append(line(x, 112, x, BASE + 8, color=color, sw=2, dash="6 5"))
        p.append(text(x, BASE + 30, label, size=14, bold=True, color=color))

    SNAP = 800
    p.append(line(SNAP, 150, SNAP, BASE + 8, color=POS, sw=2.4, dash="3 4"))
    p.append(circle(SNAP, 176, 15, fill=RED_FILL, stroke=POS, sw=2))
    p.append(text(SNAP, 181, "S", size=14, bold=True, color=POS))
    p.append(text(SNAP, BASE + 30, "мить знімка", size=14, bold=True, color=POS))

    p.append(fitbox(90, BASE + 60, 560, 78,
                    "Поза вікном знімок ловить середину операції:\n"
                    "монтування копії йде через відтворення журналу.",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.6))
    p.append(fitbox(680, BASE + 60, 560, 78,
                    "У вікні на носії немає нічого недописаного:\n"
                    "копія монтується як охайно розмонтований том.",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.6))

    render(os.path.join(IMG, 'freeze-window.svg'), W, H, *p,
           title="Вікно заморожування: хто добігає, хто чекає, куди падає знімок")


# ── 3. Три рівні узгодженості копії ─────────────────────────────────────────
def fig_consistency_levels():
    W, H = 1260, 700
    p = []

    p.append(text(46, 50, "Заморожування піднімає копію на один рівень — і рівно на один",
                  size=17, anchor="start", bold=True))

    COLS = [
        (46, "знімок без заморожування", POS, RED_FILL,
         "у польоті:\nсторінки в кеші, запити в черзі,\nтранзакція журналу відкрита",
         "монтування з відтворенням\nжурналу; частина щойно\nзаписаних файлів порожня",
         "рівносильно знеструмленню"),
        (450, "знімок у вікні заморожування", WARM, WARM_FILL,
         "на носії:\nжодного недописаного запису,\nсуперблок позначено чистим",
         "монтується без відтворення;\nструктура тому несуперечлива,\nфайли цілі як на момент вікна",
         "узгоджено на рівні файлової системи"),
        (854, "заморожування + гачок застосунку", FIELD, GREEN_FILL,
         "перед бар'єрами застосунок\nдовів свій стан до контрольної\nточки й скинув його у файли",
         "копія стартує без власного\nвідновлення; інваріанти, розкладені\nпо кількох файлах, сходяться",
         "узгоджено на рівні застосунку"),
    ]

    for x0, name, color, fill, on_disk, on_restore, verdict in COLS:
        p.append(rect(x0, 86, 360, 510, fill=BG, stroke=color, sw=1.8, rx=10))
        p.append(fitbox(x0, 86, 360, 62, name, size=14, bold=True,
                        fill=fill, stroke=color, sw=1.8, color=color, rx=10))
        p.append(text(x0 + 180, 178, "що лишається на пристрої", size=12, color=MUTED))
        p.append(fitbox(x0 + 18, 190, 324, 108, on_disk, size=13, fill=GRAY_FILL, stroke=MUTED, sw=1.4))
        p.append(text(x0 + 180, 328, "що буде при відновленні", size=12, color=MUTED))
        p.append(fitbox(x0 + 18, 340, 324, 118, on_restore, size=13, fill=fill, stroke=color, sw=1.6))
        p.append(fitbox(x0 + 18, 492, 324, 76, verdict, size=13, bold=True,
                        fill=BG, stroke=color, sw=2, color=color, rx=14))

    p.append(text(46, 650, "Файлова система не знає, які інваріанти застосунок розклав по своїх файлах, — "
                           "тому останній крок вона зробити не може, лише дати для нього тиху мить.",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'consistency-levels.svg'), W, H, *p,
           title="Три рівні узгодженості копії тому")


# ── 4. Три задачі навколо одного вікна (до вставки proj-freeze-window) ──────
def fig_watchdog_timeline():
    W, H = 1280, 680
    p = []

    p.append(text(40, 46,
                  "Сторож зводять ДО бар'єра: інакше він не покриває ні саме заморожування, "
                  "ні смерть основного процесу",
                  size=16, anchor="start", bold=True))

    AX0, AX1 = 200, 1180
    ARM_X, FRZ_X, FRZ_END = 230, 360, 470
    THAW_X, THAW_END, DL_X = 830, 880, 1080
    BASE = 430
    LBL = 185

    p.append(text((FRZ_X + THAW_END) / 2, 96,
                  "вікно: файлова система зупинена", size=14, bold=True, color=FIELD))

    # 1. основний процес
    p.append(text(LBL, 152, "основний процес", size=13, anchor="end", bold=True, color=MUTED))
    p.append(fitbox(240, 133, 112, 32, "syncfs()", size=12,
                    fill=GRAY_FILL, stroke=MUTED, sw=1.4))
    p.append(fitbox(FRZ_X, 133, FRZ_END - FRZ_X, 32, "FIFREEZE", size=12, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.6, color=NEG))
    p.append(fitbox(FRZ_END, 133, THAW_X - FRZ_END, 32, "утримання: тут роблять знімок",
                    size=12, fill=WARM_FILL, stroke=WARM, sw=1.5))
    p.append(fitbox(THAW_X, 133, THAW_END - THAW_X, 32, "FITHAW", size=11, bold=True,
                    fill=BLUE_FILL, stroke=NEG, sw=1.6, color=NEG))

    # 2. сторож
    p.append(text(LBL, 237, "сторож", size=13, anchor="end", bold=True, color=MUTED))
    p.append(fitbox(ARM_X, 218, THAW_END - ARM_X, 32,
                    "сон із дескриптором, відкритим заздалегідь", size=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(line(THAW_END, 234, DL_X, 234, color=MUTED, sw=1.6, dash="6 5"))
    p.append(text((THAW_END + DL_X) / 2, 208, "невитрачений запас", size=11, color=MUTED))
    p.append(circle(THAW_END + 6, 234, 9, fill=BG, stroke=POS, sw=2))
    p.append(text(DL_X, 258, "дедлайн", size=12, color=MUTED))

    # 3. писар
    p.append(text(LBL, 322, "писар", size=13, anchor="end", bold=True, color=MUTED))
    p.append(fitbox(AX0, 303, FRZ_X - AX0, 32, "write() ≈ 0.1 мс", size=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.5))
    p.append(fitbox(FRZ_X, 303, THAW_END - FRZ_X, 32,
                    "стан D: непереривний сон, kill -9 не діє", size=12,
                    fill=RED_FILL, stroke=POS, sw=1.6, color=POS))
    p.append(fitbox(THAW_END, 303, AX1 - THAW_END, 32, "той самий write() віддає", size=12,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    # дужка вікна
    p.append(line(FRZ_X, 372, THAW_END, 372, color=WARM, sw=2))
    p.append(line(FRZ_X, 366, FRZ_X, 378, color=WARM, sw=2))
    p.append(line(THAW_END, 366, THAW_END, 378, color=WARM, sw=2))
    p.append(text((FRZ_X + THAW_END) / 2, 394,
                  "довжина вікна = FIFREEZE + утримання + FITHAW", size=13, bold=True, color=WARM))

    # вісь часу
    p.append(line(AX0, BASE, AX1, BASE, color=INK, sw=1.8))
    p.append(text(AX1, BASE + 26, "час", size=13, anchor="end", color=MUTED))
    for x, lab, col in [(ARM_X, "таймер", FIELD), (FRZ_X, "FIFREEZE", NEG),
                        (THAW_END, "FITHAW", NEG)]:
        p.append(line(x, 92, x, BASE + 8, color=col, sw=1.8, dash="5 5"))
        p.append(text(x, BASE + 26, lab, size=13, bold=True, color=col))

    # три пояснення знизу
    NOTES = [
        (40, NEG, BLUE_FILL,
         "Таймер, зведений після ioctl, не покриває самого заморожування:\n"
         "на брудному кеші воно триває секунди, а на цій ділянці процес\n"
         "уже може загинути з підвішеною файловою системою."),
        (450, FIELD, GREEN_FILL,
         "Сторож — окремий процес із власним дескриптором. Він відтає\n"
         "незалежно від долі основної логіки й не пише у вікні нічого:\n"
         "спершу FITHAW, і лише потім повідомлення."),
        (860, POS, RED_FILL,
         "Писар усередині вікна не «повільний», а зупинений. Він не бачить\n"
         "помилки й не переривається сигналом — його write() просто\n"
         "віддає керування через усю довжину вікна."),
    ]
    for x0, col, fill, s in NOTES:
        p.append(fitbox(x0, 500, 380, 118, s, size=12,
                        fill=fill, stroke=col, sw=1.5, color=INK))

    p.append(text(40, 652,
                  "Три задачі, три ролі: одна тримає вікно, друга гарантує вихід із нього, "
                  "третя називає його ціну числом.",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'watchdog-timeline.svg'), W, H, *p,
           title="Три задачі навколо одного вікна заморожування")


if __name__ == '__main__':
    fig_freeze_levels()
    fig_freeze_window()
    fig_consistency_levels()
    fig_watchdog_timeline()
    print("ok")
