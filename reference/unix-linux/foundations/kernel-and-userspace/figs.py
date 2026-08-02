# -*- coding: utf-8 -*-
"""Фігури для теми «Ядро й простір користувача» (довідник Unix і Linux)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_F = "#fdecea"
GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
YEL_F = "#fff5e0"


def box(cx, cy, s, **kw):
    frag, w, h = textbox(cx, cy, s, **kw)
    return frag


# ── 1. Дві половини й три двері між ними ───────────────────────────────────
def fig_two_spaces():
    W, H = 1320, 700
    F = []

    UX, UY, UW, UH = 40, 66, 1240, 210      # смуга простору користувача
    KX, KY, KW, KH = 40, 430, 1240, 190     # смуга ядра

    # ── верхня смуга: багато окремих процесів
    F.append(rect(UX, UY, UW, UH, fill=BG, stroke=MUTED, sw=1.6))
    F.append(text(UX + 20, UY + 30, "ПРОСТІР КОРИСТУВАЧА · рівень 3",
                  size=15, bold=True, anchor="start"))
    F.append(text(UX + 20, UY + 54,
                  "у кожного свій адресний простір · нічого спільного, крім ядра",
                  size=12, color=MUTED, anchor="start"))

    procs = [("оболонка", "PID 2317"), ("вебсервер", "PID 811"),
             ("редактор", "PID 4402"), ("systemd", "PID 1")]
    pw, gap = 258, 40
    x0 = UX + 34
    for i, (name, pid) in enumerate(procs):
        F.append(fitbox(x0 + i * (pw + gap), UY + 84, pw, 92,
                        [name, pid, "власні сторінки пам'яті"], size=13, fill=BLU_F))

    # ── нижня смуга: одне спільне ядро
    F.append(rect(KX, KY, KW, KH, fill=GRN_F, stroke=FIELD, sw=2))
    F.append(text(KX + 20, KY + 32, "ЯДРО · рівень 0", size=15, bold=True, anchor="start"))
    F.append(text(KX + 20, KY + 56,
                  "одне на всю машину · видиме з кожного адресного простору · без свого PID",
                  size=12, color=MUTED, anchor="start"))

    duties = ["планувальник", "таблиці сторінок", "файлові системи",
              "мережевий стек", "драйвери"]
    dw, dgap = 220, 26
    dx = KX + 34
    for i, d in enumerate(duties):
        F.append(fitbox(dx + i * (dw + dgap), KY + 106, dw, 54, d, size=13, fill=BG))

    # ── двері між смугами
    MID = (UY + UH + KY) / 2

    # 1) системний виклик — угору
    F.append(arrow(110, UY + UH + 14, 110, KY - 14, color=POS, sw=2.6))
    F.append(fitbox(150, MID - 40, 300, 80,
                    ["системний виклик", "процес просить —", "і сам чекає всередині ядра"],
                    size=12, fill=YEL_F, stroke=POS))

    # 2) повернення — униз
    F.append(arrow(520, KY - 14, 520, UY + UH + 14, color=NEG, sw=2.6))
    F.append(fitbox(560, MID - 40, 296, 80,
                    ["повернення", "рівень падає назад до 3,", "процес біжить далі"],
                    size=12, fill=BLU_F, stroke=NEG))

    # 3) переривання — збоку
    F.append(fitbox(1108, MID - 34, 176, 68, ["пристрій", "мережева карта,", "диск, таймер"],
                    size=12, fill=FILL))
    F.append(arrow(1196, MID + 40, 1100, KY + 20, color=FIELD, sw=2.6))
    F.append(fitbox(908, MID - 40, 176, 80, ["переривання", "ядро прокидається", "без чийогось прохання"],
                    size=12, fill=GRN_F, stroke=FIELD))

    F.append(fitbox(UX, 646, UW, 44,
                    "Ядро ніде не «крутиться» саме собою: воно або відпрацьовує чиєсь прохання, "
                    "або відповідає на переривання — і в обох випадках повертає керування назад.",
                    size=13, fill=FILL, color=MUTED))

    render(os.path.join(IMG, 'two-spaces.svg'), W, H, *F,
           title="Дві половини системи й три двері між ними")


# ── 2. Рівень привілею й ідентичність — дві незалежні речі ─────────────────
def fig_two_axes():
    W, H = 1300, 560
    F = []

    C = [40, 330, 640, 950]
    CW = [270, 290, 290, 310]
    HY, HH = 62, 56

    heads = ["Хто виконується", "Рівень процесора",
             "Хто перевіряє його права", "Що може зробити напряму"]
    for x, w, s in zip(C, CW, heads):
        F.append(fitbox(x, HY, w, HH, s, size=13, bold=True, fill=BLU_F))

    rows = [
        (["звичайний процес", "uid 1000"],
         "кільце 3", GRN_F,
         "ядро — за uid і бітами прав",
         "лише свою пам'ять;\nусе інше — через прохання"),
        (["процес від root", "uid 0"],
         "кільце 3", GRN_F,
         "ядро — і майже ніколи\nне відмовляє",
         "теж лише свою пам'ять;\nусе інше — через прохання"),
        (["код ядра"],
         "кільце 0", RED_F,
         "ніхто — перевіряти вже нікому",
         "усе: таблиці сторінок,\nрегістри пристроїв, чужу пам'ять"),
    ]

    y, RH = HY + HH + 14, 96
    for who, ring, rfill, judge, can in rows:
        F.append(fitbox(C[0], y, CW[0], RH, who, size=13, bold=True, fill=FILL))
        F.append(fitbox(C[1], y, CW[1], RH, ring, size=15, bold=True, fill=rfill))
        F.append(fitbox(C[2], y, CW[2], RH, judge, size=12, fill=BG))
        F.append(fitbox(C[3], y, CW[3], RH, can, size=12, fill=BG))
        y += RH + 12

    F.append(fitbox(C[0], y + 10, W - 2 * C[0], 92,
                    ["root — не рівень процесора, а число, яке зберігає й перевіряє саме ядро.",
                     "Тому найвищі права в системі не дають жодної зайвої команди процесорові:",
                     "щоб опинитися в кільці 0, root мусить попросити ядро завантажити свій код усередину."],
                    size=13, fill=YEL_F))

    render(os.path.join(IMG, 'two-axes.svg'), W, H, *F,
           title="Права root і рівень привілею — дві різні осі")


# ── 3. Два інтерфейси ядра: один заморожений, другий рухомий ───────────────
def fig_two_contracts():
    W, H = 1300, 620
    F = []

    LX, LW = 40, 260
    TX, TW = 330, 700
    NX, NW = 1060, 210

    F.append(fitbox(LX, 60, LW, 52, "Інтерфейс", size=13, bold=True, fill=BLU_F))
    F.append(fitbox(TX, 60, TW, 52, "Версії ядра", size=13, bold=True, fill=BLU_F))
    F.append(fitbox(NX, 60, NW, 52, "Наслідок", size=13, bold=True, fill=BLU_F))

    vers = ["2.6", "3.x", "4.x", "5.x", "6.x"]
    cw = TW / len(vers)

    # верхня доріжка — зовнішній ABI, суцільна смуга
    Y1, RH = 140, 130
    F.append(fitbox(LX, Y1, LW, RH,
                    ["назовні:", "системні виклики", "й формат їхніх даних"],
                    size=13, bold=True, fill=FILL))
    F.append(rect(TX, Y1 + 30, TW, RH - 50, fill=GRN_F, stroke=FIELD, sw=2))
    for i, v in enumerate(vers):
        F.append(text(TX + i * cw + cw / 2, Y1 + 18, v, size=12, color=MUTED))
    F.append(text(TX + TW / 2, Y1 + RH / 2 + 10,
                  "той самий контракт — двійковий файл 2005 року працює й сьогодні", size=13))
    F.append(fitbox(NX, Y1, NW, RH,
                    ["ядро оновлюють", "під незмінним", "простором користувача"],
                    size=12, fill=GRN_F))

    # нижня доріжка — внутрішній API, розірвана смуга
    Y2 = Y1 + RH + 60
    F.append(fitbox(LX, Y2, LW, RH,
                    ["усередину:", "структури й функції", "для драйверів"],
                    size=13, bold=True, fill=FILL))
    for i, v in enumerate(vers):
        F.append(fitbox(TX + i * cw + 10, Y2 + 30, cw - 20, RH - 50,
                        [v, "інші", "сигнатури"], size=12, fill=RED_F, stroke=POS))
    F.append(text(TX + TW / 2, Y2 + 18,
                  "щовипуску інший — сигнатури міняють без попередження",
                  size=12, color=MUTED))
    F.append(fitbox(NX, Y2, NW, RH,
                    ["драйвер поза деревом", "ядра доводиться", "правити щоразу"],
                    size=12, fill=RED_F))

    F.append(fitbox(LX, Y2 + RH + 40, W - 2 * LX, 76,
                    ["Асиметрія навмисна: за межею — чужі програми, яких ніхто не перезбере,",
                     "усередині — код одного дерева, який перезбирають цілком при кожній зміні."],
                    size=13, fill=YEL_F))

    render(os.path.join(IMG, 'two-contracts.svg'), W, H, *F,
           title="Дві обіцянки ядра: назовні заморожена, усередину — жодної")


# ── 4. Межа та залізо під нею: 1969–1973 (вставка hist-border-origin) ──────
def fig_border_and_iron():
    W, H = 1360, 720
    F = []

    C = [40, 306, 652, 1010]
    CW = [250, 330, 342, 310]
    HY, HH = 62, 56

    heads = ["Машина й роки", "Що вміло залізо",
             "Чим була межа в Unix", "Що могло піти не так"]
    for x, w, s in zip(C, CW, heads):
        F.append(fitbox(x, HY, w, HH, s, size=13, bold=True, fill=BLU_F))

    rows = [
        (["PDP-7", "1969–1970"],
         ["нічого:", "ані режимів процесора,", "ані захисту пам'яті"], RED_F,
         ["домовленість:", "CAL — виклик підпрограми", "крізь комірку 020"],
         ["програма могла вписатися", "просто в ядро —", "і ніхто б не помітив"]),
        (["PDP-11/20", "1970–1971"],
         ["теж нічого:", "«незахищена» —", "слово самого Рітчі"], RED_F,
         ["той самий список викликів,", "уже з іменами шляхів", "та справжнім exec"],
         ["«кожна проба нової програми", "вимагала обережності", "й відваги»"]),
        (["PDP-11/20 + KS11", "приблизно 1972"],
         ["окрема коробка на шині:", "межі й зсув", "для двох сегментів"], YEL_F,
         ["той самий список —", "уперше є чим", "підперти його знизу"],
         ["ядро вціліє,", "але режимів", "усе ще немає"]),
        (["PDP-11/45", "1972–1973"],
         ["три режими в PSW", "+ KT11-C: своя таблиця", "сторінок на кожен режим"], GRN_F,
         ["той самий список —", "тепер крізь", "апаратну пастку"],
         ["межу боронить апаратура,", "а не сумлінність", "того, хто пише код"]),
    ]

    y, RH = HY + HH + 14, 112
    for who, iron, ifill, border, risk in rows:
        F.append(fitbox(C[0], y, CW[0], RH, who, size=14, bold=True, fill=FILL))
        F.append(fitbox(C[1], y, CW[1], RH, iron, size=12, fill=ifill))
        F.append(fitbox(C[2], y, CW[2], RH, border, size=12, fill=BG))
        F.append(fitbox(C[3], y, CW[3], RH, risk, size=12, fill=BG))
        y += RH + 12

    F.append(fitbox(C[0], y + 12, W - 2 * C[0], 78,
                    ["Третій стовпчик за чотири роки не змінився жодного разу.",
                     "Змінювався лише другий — те, чим межу підпирають знизу."],
                    size=14, fill=YEL_F))

    render(os.path.join(IMG, 'border-and-iron.svg'), W, H, *F,
           title="Межа й залізо під нею: від PDP-7 до PDP-11/45")


# ── 5. Три режими PDP-11/45 і двері, що відчиняються лише всередину ────────
def fig_1145_modes():
    W, H = 1340, 690
    F = []

    BX, BW = 350, 570
    BH = 92
    ys = [72, 184, 296]

    bands = [
        (["User — біти 15,14 = 11",
          "HALT заборонено, RESET і SPL машина ігнорує"], BG),
        (["Supervisor — біти 15,14 = 01",
          "у Unix у цьому режимі не виконується ніщо"], YEL_F),
        (["Kernel — біти 15,14 = 00",
          "усі команди, усі вектори пасток лежать тут"], GRN_F),
    ]
    for y, (lines, fill) in zip(ys, bands):
        F.append(fitbox(BX, y, BW, BH, lines, size=13, fill=fill))

    top, bot = ys[0], ys[2] + BH

    # ← назовні: RTT
    F.append(arrow(292, bot, 292, top + 6, color=NEG, sw=2.6))
    F.append(fitbox(40, 168, 230, 130,
                    ["назовні — RTT", "біти режиму", "зовнішній код може", "лише ВСТАНОВИТИ:", "0 → 1"],
                    size=13, fill=BLU_F, stroke=NEG))

    # → усередину: пастка
    F.append(arrow(978, top + 6, 978, bot, color=POS, sw=2.6))
    F.append(fitbox(1000, 168, 300, 130,
                    ["усередину — пастка", "або переривання", "зняти біти (1 → 0)", "здатна тільки апаратура,",
                     "і лише за своїм вектором"],
                    size=13, fill=RED_F, stroke=POS))

    F.append(fitbox(BX, 420, BW, 74,
                    ["Кожен режим має власний R6", "і власний набір регістрів сторінок."],
                    size=13, fill=FILL))

    F.append(fitbox(40, 522, W - 80, 130,
                    ["Unix узяв із трьох рівнів два. Порожній середній не пропав дарма:",
                     "його набір регістрів сторінок ядро вживає як пересувне вікно в чужу пам'ять —",
                     "ставить SISA0 на потрібну сторінку, оголошує режим Supervisor «попереднім»",
                     "і читає крізь нього командами MFPD/MTPD, не виконавши в ньому жодної інструкції."],
                    size=13, fill=YEL_F))

    render(os.path.join(IMG, 'pdp1145-modes.svg'), W, H, *F,
           title="Три режими PDP-11/45: усередину — лише пасткою")


# ── Три долі однієї поганої адреси (вставка proj-border-probe) ─────────────
def fig_three_fates():
    W, H = 1430, 660
    F = []

    AX, AW = 40, 280
    BX, BW = 370, 340
    CX, CW = 760, 340
    DX, DW = 1150, 240
    RH = 110
    rows_y = [95, 245, 395]

    heads = [(AX + AW / 2, "що подали"),
             (BX + BW / 2, "перевірка діапазону"),
             (CX + CW / 2, "що сталося далі"),
             (DX + DW / 2, "чим скінчилося")]
    for cx, s in heads:
        F.append(text(cx, 74, s, size=13, bold=True, color=MUTED))

    rows = [
        (["адреса −4096", "(бік ядра)"],
         ["access_ok: адреса не з нашого боку", "→ відмова одразу"],
         ["копіювання не почалося,", "/dev/null навіть не покликано"],
         ["EFAULT"], BLU_F, YEL_F),
        (["адреса 0x10", "(бік користувача,", "сторінки немає)"],
         ["access_ok: діапазон свій —", "пропущено далі"],
         ["копіювання спіткнулося об збій;", "для цих команд зареєстровано", "адресу відкату"],
         ["EFAULT", "(до /dev/null — 16:", "копіювання не було)"], BLU_F, YEL_F),
        (["*(volatile char*)0x10", "у вашому коді"],
         ["перевірок немає:", "це не системний виклик"],
         ["той самий збій сторінки,", "але відкоту для вашої команди", "ніхто не реєстрував"],
         ["SIGSEGV", "процес мертвий"], RED_F, RED_F),
    ]

    for (a, b, c, d, fill_in, fill_out), y in zip(rows, rows_y):
        stroke_out = POS if fill_out == RED_F else FIELD
        F.append(fitbox(AX, y, AW, RH, a, size=13, fill=fill_in))
        F.append(fitbox(BX, y, BW, RH, b, size=13, fill=BG))
        F.append(fitbox(CX, y, CW, RH, c, size=13, fill=BG))
        F.append(fitbox(DX, y, DW, RH, d, size=13, fill=fill_out, stroke=stroke_out, sw=2))
        F.append(arrow(AX + AW + 8, y + RH / 2, BX - 8, y + RH / 2))
        F.append(arrow(BX + BW + 8, y + RH / 2, CX - 8, y + RH / 2))
        F.append(arrow(CX + CW + 8, y + RH / 2, DX - 8, y + RH / 2))

    F.append(fitbox(40, 530, W - 80, 76,
                    ["Адреса та сама, апаратна подія та сама. Різниця в тому, по який бік межі виконувалася команда,",
                     "що спіткнулася: для команди ядра адресу відкату зареєстровано заздалегідь, для вашої — ні."],
                    size=13, fill=GRN_F, stroke=FIELD))

    render(os.path.join(IMG, 'three-fates.svg'), W, H, *F,
           title="Одна відсутня сторінка, три різні кінцівки")


# ── Хто які перетини межі бачить (вставка proj-border-probe) ───────────────
def fig_who_sees_what():
    W, H = 1400, 620
    F = []

    n, cw, gap = 6, 198, 20
    x0 = 45
    step = cw + gap
    centers = [x0 + i * step + cw / 2 for i in range(n)]

    events = [
        (["execve", "системний виклик"], BLU_F),
        (["збій сторінки", "не системний виклик"], YEL_F),
        (["write", "системний виклик"], BLU_F),
        (["переривання таймера", "не системний виклик"], YEL_F),
        (["clock_gettime", "через vDSO — межі немає"], GRN_F),
        (["exit_group", "системний виклик"], BLU_F),
    ]
    for i, (lines, fill) in enumerate(events):
        F.append(fitbox(x0 + i * step, 56, cw, 70, lines, size=12, fill=fill))
        F.append(line(centers[i], 126, centers[i], 156, color=MUTED, sw=1.4))

    F.append(line(40, 158, W - 40, 158, color=MUTED, sw=1.6))
    F.append(text(45, 182, "час роботи програми →", size=11, color=MUTED, anchor="start"))

    mw, mh = 170, 40
    lanes = [
        ("strace (через ptrace) — рівно системні виклики",
         [("бачить", GRN_F), ("не видно", RED_F), ("бачить", GRN_F),
          ("не видно", RED_F), ("не видно", RED_F), ("бачить", GRN_F)]),
        ("getrusage і time -v — підсумки, а не окремі події",
         [("у підсумку sys", YEL_F), ("лічить окремо", GRN_F), ("у підсумку sys", YEL_F),
          ("не видно", RED_F), ("не видно", RED_F), ("у підсумку sys", YEL_F)]),
        ("perf і ftrace — точки трасування по всьому ядру",
         [("бачить", GRN_F)] * 6),
    ]
    for k, (lane_title, marks) in enumerate(lanes):
        Y = 205 + k * 110
        F.append(rect(40, Y, W - 80, 92, fill=BG, stroke=MUTED, sw=1.4))
        F.append(text(58, Y + 26, lane_title, size=13, bold=True, anchor="start"))
        for i, (s, fill) in enumerate(marks):
            stroke = POS if fill == RED_F else (FIELD if fill == GRN_F else LINE)
            F.append(fitbox(centers[i] - mw / 2, Y + 40, mw, mh, s,
                            size=11, fill=fill, stroke=stroke))

    F.append(fitbox(40, 535, W - 80, 60,
                    ["Вікно трасувальника — не вся межа: сторінкових збоїв і переривань у його виводі немає жодного,",
                     "хоча це такі самі переходи в ядро, як і системний виклик."],
                    size=13, fill=GRN_F, stroke=FIELD))

    render(os.path.join(IMG, 'who-sees-what.svg'), W, H, *F,
           title="Перетини межі та інструменти, що їх помічають")


if __name__ == '__main__':
    fig_two_spaces()
    fig_two_axes()
    fig_two_contracts()
    fig_border_and_iron()
    fig_1145_modes()
    fig_three_fates()
    fig_who_sees_what()
    print("ok:", os.listdir(IMG))
