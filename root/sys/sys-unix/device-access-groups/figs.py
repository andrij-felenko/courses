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


# ── 1. Два незалежні ланцюги, що сходяться в одному порівнянні ───────────────
def fig_access_chain():
    W, H = 1280, 940
    p = []

    LX, LW = 60, 520
    RX, RW = 700, 520

    p.append(fitbox(LX, 50, LW, 58, "бік пристрою", size=16, bold=True,
                    fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(RX, 50, RW, 58, "бік людини", size=16, bold=True,
                    fill=GREEN_FILL, stroke=FIELD))

    left = [
        (140, 74, "перехідник устромили в роз'єм;\nядро створює пристрій і повідомляє udev"),
        (250, 74, "udev перебирає правила й знаходить те,\nяке збіглося з цим пристроєм"),
        (360, 74, "правило каже, чим має стати вузол:\nGROUP=\"dialout\"   MODE=\"0660\""),
        (470, 96, "у /dev виникає вузол ttyUSB0\nвласник root · група 20 · режим crw-rw----"),
    ]
    right = [
        (140, 74, "адміністратор один раз:\nusermod -aG dialout andrij"),
        (250, 74, "у файлі /etc/group з'являється рядок\ndialout:x:20:andrij"),
        (360, 74, "при вході login збирає перелік груп\nі кладе його в процес сеансу"),
        (470, 96, "процес несе знімок списку\n[1000, 20, ...] — і передає його нащадкам"),
    ]

    for y, h, s in left:
        p.append(fitbox(LX, y, LW, h, s, size=13, fill=BG, stroke=NEG))
    for y, h, s in right:
        p.append(fitbox(RX, y, RW, h, s, size=13, fill=BG, stroke=FIELD))

    for y0, h0, _ in left[:-1]:
        p.append(arrow(LX + LW / 2, y0 + h0 + 4, LX + LW / 2, y0 + h0 + 32))
    for y0, h0, _ in right[:-1]:
        p.append(arrow(RX + RW / 2, y0 + h0 + 4, RX + RW / 2, y0 + h0 + 32))

    p.append(arrow(LX + LW / 2, 570, LX + LW / 2, 616))
    p.append(arrow(RX + RW / 2, 570, RX + RW / 2, 616))

    p.append(fitbox(LX, 622, RX + RW - LX, 76,
                    "процес просить open(\"/dev/ttyUSB0\", O_RDWR) — і аж тепер два числа вперше зустрічаються",
                    size=15, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(LX, 726, RX + RW - LX, 116,
                    "fsuid збігається з root?                                   ні\n"
                    "число 20 є серед додаткових груп процесу?    так   →   клас «група», трійка rw\n"
                    "у трійці стоять і r, і w                                     →   дозволено",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(LX, 862, RX + RW - LX, 62,
                    "спільне в обох ланцюгів рівно одне — число 20; правило udev не знає про людину,\n"
                    "а /etc/group не знає про пристрій, якого ще не встромили",
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'access-chain.svg'), W, H, *p,
           title="Два ланцюги, що сходяться в одному порівнянні чисел")


# ── 2. Що насправді відмикає число групи ────────────────────────────────────
def fig_group_scope():
    W, H = 1420, 780
    p = []

    C1X, C1W = 50, 210
    C2X, C2W = 286, 340
    C3X, C3W = 652, 470
    C4X, C4W = 1148, 222

    heads = [(C1X, C1W, "група"), (C2X, C2W, "на які вузли правило\nштампує це число"),
             (C3X, C3W, "що це відмикає насправді"), (C4X, C4W, "чим це є за вагою")]
    for x, w, s in heads:
        p.append(fitbox(x, 50, w, 64, s, size=13, bold=True, fill=FILL, stroke=LINE))

    rows = [
        ("dialout\nна Arch — uucp",
         "усі послідовні порти:\nttyUSB*, ttyACM*, ttyS*",
         "прошити будь-яку підключену плату;\nговорити з ttyS0, а це на сервері\nчасто консоль самої машини",
         "широко, але\nв межах портів",
         BLUE_FILL, NEG, 108),
        ("video",
         "усі /dev/video*\nі вузли відеокарти",
         "кадри з кожної камери машини,\nбез жодного натяку для того,\nкого знімають",
         "широко",
         BLUE_FILL, NEG, 108),
        ("input",
         "усі /dev/input/event*",
         "читати кожне натискання клавіші\nв системі — зокрема пароль,\nнабраний у чужому сеансі",
         "фактично root",
         RED_FILL, POS, 108),
        ("disk",
         "блокові пристрої цілком:\nsda, nvme0n1",
         "писати блоки повз файлову систему:\nпідмінити будь-який файл, змінити\nбудь-які права, покласти setuid-root",
         "це root,\nназваний інакше",
         RED_FILL, POS, 116),
    ]

    y = 138
    for g, nodes, what, weight, fill, stroke, h in rows:
        p.append(fitbox(C1X, y, C1W, h, g, size=14, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(C2X, y, C2W, h, nodes, size=13, fill=BG, stroke=MUTED))
        p.append(fitbox(C3X, y, C3W, h, what, size=13, fill=BG, stroke=MUTED))
        p.append(fitbox(C4X, y, C4W, h, weight, size=13, bold=True, fill=fill, stroke=stroke))
        y += h + 26

    p.append(fitbox(C1X, y + 10, C4X + C4W - C1X, 78,
                    "перевірка прав файлової системи живе НАД блоковим пристроєм —\n"
                    "тому той, кому дозволено писати в /dev/sda, просто проходить під нею,\n"
                    "і жоден режим на жодному файлі його не спинить",
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'group-scope.svg'), W, H, *p,
           title="Число групи відмикає клас вузлів, а не один пристрій")


# ── 3. Список груп — знімок, і ось коли він оновлюється ─────────────────────
def fig_snapshot_timeline():
    W, H = 1240, 800
    p = []

    XL, XW = 60, 700
    RX, RW = 800, 380

    p.append(fitbox(XL, 46, XW, 58,
                    "що відбувається з переліком груп у часі",
                    size=15, bold=True, fill=FILL, stroke=LINE))

    steps = [
        ("вхід у систему", "login читає /etc/group і кладе перелік\nу процес сеансу: [1000]",
         GREEN_FILL, FIELD, 80),
        ("sudo usermod -aG dialout andrij", "змінився ФАЙЛ на диску; жоден\nз працюючих процесів його не перечитує",
         WARM_FILL, WARM, 80),
        ("у старому терміналі", "id показує [1000]\nopen(\"/dev/ttyUSB0\") → EACCES",
         RED_FILL, POS, 80),
        ("новий вхід — або newgrp dialout", "перелік збирають наново: [1000, 20]",
         GREEN_FILL, FIELD, 68),
        ("у новій оболонці", "id показує [1000, 20]\nopen(\"/dev/ttyUSB0\") → дозволено",
         GREEN_FILL, FIELD, 80),
    ]

    y = 132
    for label, what, fill, stroke, h in steps:
        p.append(fitbox(XL, y, 300, h, label, size=13, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(XL + 320, y, XW - 320, h, what, size=13, fill=BG, stroke=MUTED))
        y += h + 42

    yy = 132
    for _, _, _, _, h in steps[:-1]:
        p.append(arrow(XL + 150, yy + h + 4, XL + 150, yy + h + 38))
        yy += h + 42

    p.append(fitbox(RX, 132, RW, 190,
                    "чому нова вкладка термінала\nзазвичай не допомагає\n\n"
                    "вона відгалужується від процесу\nграфічного сеансу, а той тримає\nстарий знімок і копіює його\nусім своїм нащадкам",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(fitbox(RX, 352, RW, 176,
                    "newgrp і sg — маленькі програми\nз бітом set-user-ID\n\n"
                    "вони звіряються з базою облікових\nзаписів самі й запускають оболонку\nз наново зібраним переліком",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(XL, 700, RX + RW - XL, 76,
                    "перелік груп ніколи не «оновлюється» — він лише створюється наново разом із процесом;\n"
                    "тому порада «перелогінься» стосується не звички, а єдиного каналу, яким число туди потрапляє",
                    size=14, bold=True, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'snapshot-timeline.svg'), W, H, *p,
           title="Перелік груп як знімок і момент його перезбирання")


fig_access_chain()
fig_group_scope()
fig_snapshot_timeline()
print("ok")
