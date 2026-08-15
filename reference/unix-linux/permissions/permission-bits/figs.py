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


# ── 1. Слово режиму: що в ньому лежить і як воно розпадається на розряди ─────
def fig_mode_word():
    W, H = 1180, 660
    p = []

    p.append(fitbox(50, 190, 250, 96,
                    "тип об'єкта\nставиться при створенні\nchmod його не змінює",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(text(175, 165, "не належить правам", size=13, color=MUTED))

    groups = [
        (345, "спеціальні", ["s", "s", "t"], "0", "setuid · setgid · sticky", WARM_FILL, WARM),
        (555, "власник", ["r", "w", "x"], "7", "збіг за fsuid", GREEN_FILL, FIELD),
        (765, "група", ["r", "w", "x"], "5", "збіг за fsgid\nчи додатковою групою", BLUE_FILL, NEG),
        (975, "решта", ["r", "w", "x"], "4", "коли не збіглося нічого", FILL, LINE),
    ]

    CW, GAP = 54, 12
    for gx, head, letters, digit, note, fill, stroke in groups:
        gw = 3 * CW + 2 * GAP
        p.append(text(gx + gw / 2, 165, head, size=14, bold=True))
        for i, ch in enumerate(letters):
            p.append(fitbox(gx + i * (CW + GAP), 190, CW, 66, ch,
                            size=22, fill=fill, stroke=stroke, bold=True))
        p.append(text(gx + gw / 2, 322, digit, size=30, bold=True, color=stroke))
        p.append(fitbox(gx - 8, 350, gw + 16, 74, note, size=12, fill=BG, stroke=MUTED))

    p.append(text(175, 322, "—", size=26, color=MUTED))

    p.append(fitbox(50, 60, 1080, 74,
                    "st_mode — одне ціле число: старші біти кажуть, ЩО це за об'єкт,\n"
                    "молодші дванадцять — що з ним вільно робити",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    p.append(fitbox(345, 460, 785, 62,
                    "чотири вісімкові розряди: 0754",
                    size=17, fill=FILL, stroke=LINE, bold=True))

    p.append(fitbox(50, 556, 1080, 74,
                    "кожен розряд — сума 4 (r) + 2 (w) + 1 (x) своєї трійки;\n"
                    "перший розряд опускають, коли спеціальні біти порожні: 0754 і 754 — те саме",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'mode-word.svg'), W, H, *p,
           title="Слово режиму: тип, спеціальні біти й три трійки")


# ── 2. Ті самі три букви для файлу і для каталогу ────────────────────────────
def fig_file_vs_dir():
    W, H = 1220, 700
    p = []

    p.append(fitbox(150, 60, 480, 62, "звичайний файл — послідовність байтів",
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(690, 60, 480, 62, "каталог — таблиця «ім'я → номер inode»",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))

    rows = [
        ("r", "прочитати байти вмісту",
         "перелічити імена з таблиці —\nсамі імена, без метаданих"),
        ("w", "змінити байти:\nдописати, урізати, перезаписати",
         "змінити таблицю:\nстворити, прибрати\nчи перейменувати запис"),
        ("x", "виконати як програму —\nобраз читає саме ядро",
         "скористатися таблицею для пошуку:\nпройти крізь цей каталог\nу середині шляху"),
    ]

    y = 156
    for letter, left, right in rows:
        p.append(fitbox(50, y + 14, 76, 70, letter, size=26, bold=True,
                        fill=WARM_FILL, stroke=WARM))
        p.append(fitbox(150, y, 480, 98, left, size=14))
        p.append(fitbox(690, y, 480, 98, right, size=14))
        y += 128

    p.append(fitbox(50, 546, 1120, 68,
                    "прибрати файл — це правка таблиці КАТАЛОГУ; прав самого файлу при цьому не питають,\n"
                    "тому в теці, куди вам вільно писати, ви приберете й чужий файл із режимом 000",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(fitbox(50, 630, 1120, 52,
                    "звідси біт t на спільних теках: звідти прибирає лише власник запису, власник теки або привілейований процес",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'file-vs-dir.svg'), W, H, *p,
           title="r, w, x для файлу і для каталогу")


# ── 3. Драбина перевірки: перше «так» обирає клас ────────────────────────────
def fig_check_ladder():
    W, H = 1100, 940
    p = []

    LX, LW = 60, 440
    RX, RW = 560, 480

    p.append(fitbox(LX, 50, 980, 86,
                    "процес просить дію над об'єктом; хто просить — fsuid, fsgid і додаткові групи\n"
                    "питання йдуть згори вниз, і перше «так» обирає клас остаточно",
                    size=14, bold=True, fill=FILL, stroke=LINE))

    steps = [
        (176, 72, "fsuid збігається з власником файлу?",
         "так → трійка власника, і тільки вона", GREEN_FILL, FIELD),
        (284, 86, "fsgid або одна з додаткових груп\nзбігається з групою файлу?",
         "так → трійка групи, і тільки вона", BLUE_FILL, NEG),
        (406, 64, "не збіглося нічого",
         "трійка «решта»", FILL, LINE),
    ]
    for y, h, q, ans, fill, stroke in steps:
        p.append(fitbox(LX, y, LW, h, q, size=14))
        p.append(fitbox(RX, y, RW, h, ans, size=14, fill=fill, stroke=stroke))
        p.append(arrow(LX + LW + 6, y + h / 2, RX - 8, y + h / 2))

    p.append(arrow(280, 248, 280, 280))
    p.append(arrow(280, 370, 280, 402))

    p.append(fitbox(LX, 512, LW, 72, "у вибраній трійці стоять усі\nпотрібні букви?", size=14))
    p.append(fitbox(RX, 512, RW, 72, "так → дозволено", size=15, bold=True,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(LX + LW + 6, 548, RX - 8, 548))
    p.append(arrow(280, 470, 280, 508))

    p.append(fitbox(LX, 626, LW, 86,
                    "ні → чи має процес\nCAP_DAC_OVERRIDE або CAP_DAC_READ_SEARCH?", size=13))
    p.append(fitbox(RX, 626, RW, 86,
                    "так → дозволено; виконання —\nлише коли стоїть хоч один біт x",
                    size=14, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(LX + LW + 6, 669, RX - 8, 669))
    p.append(arrow(280, 584, 280, 622))

    p.append(fitbox(LX, 760, LW, 64, "ні → EACCES", size=16, bold=True,
                    fill=RED_FILL, stroke=POS))
    p.append(arrow(280, 712, 280, 756))

    p.append(fitbox(RX, 744, RW, 150,
                    "----rw----   alice   devs   secret.txt\n"
                    "процес: fsuid=alice, групи alice і devs\n"
                    "перше «так» — власник\n"
                    "трійка власника порожня\n"
                    "права групи вже ніхто не питає  →  EACCES",
                    size=13, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'check-ladder.svg'), W, H, *p,
           title="Перевірка прав: перше «так» обирає клас")


# ── 4. Як слово режиму росло від шести бітів до дванадцяти ──────────────────
def fig_bits_timeline():
    W, H = 1300, 900
    p = []

    C1X, C1W = 50, 310
    C2X, C2W = 382, 440
    C3X, C3W = 844, 406

    p.append(fitbox(C1X, 50, C1W, 56, "коли й де", size=14, bold=True,
                    fill=FILL, stroke=LINE))
    p.append(fitbox(C2X, 50, C2W, 56, "що стояло в слові режиму", size=14, bold=True,
                    fill=FILL, stroke=LINE))
    p.append(fitbox(C3X, 50, C3W, 56, "що це змінило", size=14, bold=True,
                    fill=FILL, stroke=LINE))

    rows = [
        ("1-ше видання Unix\n3.11.1971\nтой самий набір ще в 3-му,\nлютий 1973",
         "шість бітів\n01 запис не-власником\n02 читання не-власником\n04 запис власником\n10 читання власником\n20 «виконуваний»\n40 set-UID",
         "класів два: власник і всі інші\nгрупи немає зовсім\n«виконуваний» — ознака файлу,\nа не право чийогось класу",
         FILL, LINE, 218),
        ("4-те видання\nсторінка man 20.08.1973\nвидання — листопад 1973",
         "одинадцять бітів\n4000 set-UID · 2000 set-GID\n0400 0200 0100 — власник\n0070 — група\n0007 — решта",
         "з'явився клас групи\nі окремий біт x на кожен клас\nшість бітів замінено дев'яткою\nразом із двома спеціальними",
         GREEN_FILL, FIELD, 182),
        ("5-те видання\nчервень 1974",
         "додано 01000\nISVTX у заголовку inode.h",
         "образ програми лишається у свопі\nпісля виходу — повторний запуск\nне перечитує файл із диска",
         WARM_FILL, WARM, 146),
        ("4.3BSD\nsticky(8), 26.05.1986",
         "той самий 01000,\nале поставлений на каталозі",
         "запис у спільній теці прибирає\nчи перейменовує лише власник файлу,\nвласник теки або суперкористувач",
         BLUE_FILL, NEG, 146),
    ]

    y = 132
    for when, what, why, fill, stroke, h in rows:
        p.append(fitbox(C1X, y, C1W, h, when, size=13, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(C2X, y, C2W, h, what, size=13, fill=BG, stroke=stroke))
        p.append(fitbox(C3X, y, C3W, h, why, size=13, fill=BG, stroke=MUTED))
        y += h + 30

    p.append(fitbox(C1X, y, C3X + C3W - C1X, 62,
                    "назва «sticky» лишилася від першої ролі, хоч від самої ролі в сучасних системах не зосталося нічого",
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'bits-timeline.svg'), W, H, *p,
           title="Як слово режиму росло від шести бітів до дванадцяти")


# ── 5. Один open — чотири рішення: x на кожному каталозі, потім трійка файлу ─
def fig_prefix_walk():
    W, H = 1240, 790
    p = []

    XS, CW, GAP = 50, 260, 30
    cols = [XS + i * (CW + GAP) for i in range(4)]

    p.append(fitbox(XS, 50, 4 * CW + 3 * GAP, 80,
                    "щоб прочитати /home/alice/secret.txt, ядро ухвалює не одне рішення,\n"
                    "а чотири: по одному на кожен каталог префікса плюс одне на сам файл",
                    size=15, bold=True, fill=FILL, stroke=LINE))

    data = [
        ("/", "потрібен x\nзайти й шукати ім'я", "drwxr-xr-x\nroot · root",
         "клас: решта", "трійка r-x — x є\nйдемо далі", BLUE_FILL, NEG),
        ("home", "потрібен x\nзайти й шукати ім'я", "drwxr-xr-x\nroot · root",
         "клас: решта", "трійка r-x — x є\nйдемо далі", BLUE_FILL, NEG),
        ("alice", "потрібен x\nзайти й шукати ім'я", "drwx------\nalice · alice",
         "клас: власник", "трійка rwx — x є\nйдемо далі", GREEN_FILL, FIELD),
        ("secret.txt", "потрібно r\nвласне дія", "----rw----\nalice · devs",
         "клас: власник", "трійка власника порожня\nEACCES", RED_FILL, POS),
    ]

    for x, (name, need, mode, cls, verdict, fill, stroke) in zip(cols, data):
        p.append(fitbox(x, 165, CW, 62, name, size=17, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(x, 257, CW, 66, need, size=13, fill=BG, stroke=MUTED))
        p.append(fitbox(x, 353, CW, 66, mode, size=14, fill=FILL, stroke=LINE))
        p.append(fitbox(x, 449, CW, 54, cls, size=14, bold=True, fill=BG, stroke=stroke))
        p.append(fitbox(x, 533, CW, 76, verdict, size=13, fill=fill, stroke=stroke))

    for i in range(3):
        p.append(arrow(cols[i] + CW + 4, 196, cols[i + 1] - 6, 196))

    p.append(fitbox(XS, 649, 4 * CW + 3 * GAP, 96,
                    "у каталозі з префікса нічого не читають — у ньому лише шукають одне ім'я,\n"
                    "тому потрібен саме x, а не r; права самого файлу питають останніми,\n"
                    "і лише вони відмовляють тому, хто пройшов увесь шлях",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'prefix-walk.svg'), W, H, *p,
           title="Обхід префікса шляху: x на кожному каталозі, потім трійка на цілі")


fig_mode_word()
fig_file_vs_dir()
fig_check_ladder()
fig_bits_timeline()
fig_prefix_walk()
print("ok")
