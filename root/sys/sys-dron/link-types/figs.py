# -*- coding: utf-8 -*-
"""Фігури до теми «Типи каналів» довідника QGroundControl."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

BAND = "#eef2f6"
SOFT = "#ffffff"
EDGE = "#98a6b4"


# ───────────────────────────── 1. Шов ────────────────────────────────────────
def fig_seam():
    W, H = 1240, 700
    f = []

    # верхня зона — однакова для всіх каналів
    f.append(rect(30, 56, 1180, 226, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(70, 84, "вище шва різниці немає", size=14, bold=True, anchor="start"))

    f.append(fitbox(300, 100, 640, 54, "Vehicle · параметри · план місії · карта · відео",
                    size=14, fill=SOFT))
    f.append(fitbox(300, 196, 640, 60,
                    "MAVLinkProtocol: mavlink_parse_char(канал, байт)\nсвій стан розбору на кожен канал",
                    size=13, fill=SOFT))
    f.append(arrow(620, 196, 620, 158))
    f.append(text(646, 180, "повідомлення", size=12, color=MUTED, anchor="start"))

    # шов
    f.append(line(30, 320, 1210, 320, color=LINE, sw=2.4, dash="9,6"))
    f.append(text(70, 312, "ШОВ: LinkInterface", size=15, bold=True, anchor="start"))
    f.append(arrow(430, 320, 430, 262))
    f.append(text(452, 296, "bytesReceived — масив байтів угору", size=12, color=NEG, anchor="start"))
    f.append(arrow(880, 262, 880, 320))
    f.append(text(858, 296, "writeBytesThreadSafe — байти вниз", size=12, color=POS, anchor="end"))

    # нижня зона — усе різне
    f.append(text(70, 360, "нижче шва спільного немає нічого", size=14, bold=True, anchor="start"))

    boxes = [
        (40, "серійний порт", "імені пристрою\nдодає ОС", "байти йдуть\nдовільними шматками"),
        (285, "сокет UDP", "адреси нема,\nдоки хтось не озветься", "датаграма приходить\nцілою або ніяк"),
        (530, "сокет TCP", "справжнє з'єднання\nз рукостисканням", "потік без утрат,\nале з очікуванням"),
        (775, "Bluetooth", "спарення робить ОС,\nне застосунок", "класичний — потік,\nBLE — шматки по 20 Б"),
        (1020, "файл логу", "джерело — диск,\nа не радіо", "ті самі байти\nза мітками часу"),
    ]
    for x, name, a, b in boxes:
        f.append(rect(x, 396, 180, 232, fill=SOFT, stroke=EDGE, sw=1.6, rx=10))
        f.append(text(x + 90, 426, name, size=14, bold=True))
        f.append(mtext(x + 90, 466, a.split("\n"), size=11, color=MUTED))
        f.append(line(x + 20, 512, x + 160, 512, color="#d0d8e0", sw=1.2))
        f.append(mtext(x + 90, 546, b.split("\n"), size=11))
        f.append(arrow(x + 90, 396, x + 90, 372))

    f.append(text(620, 672,
                  "кожне з'єднання дістає власний канал розбору й власну нитку — тому байти двох каналів ніколи не змішуються",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'seam.svg'), W, H, *f,
           title="Канал для застосунку — це труба байтів із двома кінцями")


# ─────────────────────── 2. Три швидкості серійного шляху ────────────────────
def fig_serial():
    W, H = 1300, 640
    f = []

    y = 150
    chain = [
        (40, 200, "польотний\nконтролер", "UART на платі"),
        (300, 190, "радіомодуль\nна борту", "серійний бік"),
        (560, 190, "радіомодуль\nна столі", "серійний бік"),
        (820, 200, "міст USB↔UART\nу тому ж корпусі", "перетворювач"),
        (1080, 180, "вузол пристрою\nв системі", "COM7, ttyUSB0"),
    ]
    for x, w, name, sub in chain:
        f.append(rect(x, y, w, 96, fill=SOFT, stroke=EDGE, sw=1.6, rx=10))
        f.append(mtext(x + w / 2, y + 34, name.split("\n"), size=13, bold=True))
        f.append(text(x + w / 2, y + 80, sub, size=11, color=MUTED))

    f.append(arrow(240, y + 48, 300, y + 48))
    f.append(arrow(750, y + 48, 820, y + 48))
    f.append(arrow(1020, y + 48, 1080, y + 48))

    # ефір
    f.append(line(490, y + 48, 560, y + 48, color=NEG, sw=2, dash="6,5"))
    f.append(text(525, y - 14, "ефір", size=12, color=NEG))

    # три смуги швидкостей
    bands = [
        (40, 450, "швидкість №1: UART борту",
         "її узгоджують прошивка й радіомодуль;\nстанція про неї нічого не знає", NEG),
        (520, 380, "швидкість №2: темп ефіру",
         "задана в самому радіомодулі;\nвона й обмежує реальний потік", FIELD),
        (930, 330, "швидкість №3: та, що в діалозі",
         "стосується ЛИШЕ останнього стрибка:\nміст USB↔UART ↔ застосунок", POS),
    ]
    for x, w, head, body, col in bands:
        f.append(rect(x, 330, w, 108, fill=SOFT, stroke=col, sw=1.8, rx=10))
        f.append(text(x + w / 2, 358, head, size=13, bold=True, color=col))
        f.append(mtext(x + w / 2, 386, body.split("\n"), size=11.5))

    f.append(line(140, 246, 140, 330, color=NEG, sw=1.4, dash="4,4"))
    f.append(line(655, 246, 655, 330, color=FIELD, sw=1.4, dash="4,4"))
    f.append(line(1095, 246, 1095, 330, color=POS, sw=1.4, dash="4,4"))

    # окрема гілка: пряме USB
    f.append(rect(40, 490, 560, 108, fill=BAND, stroke=EDGE, sw=1.6, rx=10))
    f.append(text(320, 520, "пряме USB до плати", size=13, bold=True))
    f.append(mtext(320, 548, ["плата показує себе як віртуальний серійний порт;",
                              "число в полі швидкості нічого не змінює"], size=11.5))

    f.append(rect(660, 490, 600, 108, fill=BAND, stroke=EDGE, sw=1.6, rx=10))
    f.append(text(960, 520, "не збігається швидкість №3", size=13, bold=True, color=POS))
    f.append(mtext(960, 548, ["помилки не буде: у порту немає рукостискання —",
                              "просто на вхід посиплеться сміття, і серцебиття не з'явиться"], size=11.5))

    render(os.path.join(OUT, 'serial-speeds.svg'), W, H, *f,
           title="Серійний шлях: три різні швидкості, і в діалозі станції задають лише одну")


# ─────────────────────── 3. UDP: список цілей наповнює апарат ────────────────
def fig_udp():
    W, H = 1200, 690
    f = []

    # станція
    f.append(rect(60, 96, 300, 130, fill=SOFT, stroke=EDGE, sw=1.8, rx=10))
    f.append(text(210, 128, "станція", size=15, bold=True))
    f.append(mtext(210, 156, ["сокет прив'язано до порту 14550",
                              "список цілей поки порожній"], size=12))

    # апарат
    f.append(rect(840, 96, 300, 130, fill=SOFT, stroke=EDGE, sw=1.8, rx=10))
    f.append(text(990, 128, "апарат або міст на борту", size=14, bold=True))
    f.append(mtext(990, 156, ["шле серцебиття «кудись»,",
                              "джерело 192.168.1.50:14555"], size=12))

    # крок 1
    f.append(arrow(840, 190, 370, 190))
    f.append(text(605, 172, "перша датаграма приходить сама", size=12, color=NEG))

    f.append(rect(60, 262, 1080, 92, fill=BAND, stroke=EDGE, sw=1.6, rx=10))
    f.append(text(600, 294, "станція дивиться, ХТО прислав, і додає це джерело у список цілей сеансу", size=13, bold=True))
    f.append(text(600, 330, "жодного налаштування для цього не потрібно — адресу приніс сам пакет", size=12, color=MUTED))

    # крок 2
    f.append(arrow(370, 410, 840, 410))
    f.append(text(605, 392, "тепер станція має куди слати команди", size=12, color=FIELD))
    f.append(rect(560, 424, 90, 44, fill=SOFT, stroke=EDGE, sw=1.4, rx=8))
    f.append(text(605, 452, "NAT", size=13, bold=True))
    f.append(text(605, 494, "маршрутизатор пропускає відповідь, бо з'єднання почав апарат", size=12, color=MUTED))

    # зворотний випадок
    f.append(rect(60, 540, 520, 120, fill=SOFT, stroke=POS, sw=1.8, rx=10))
    f.append(text(320, 570, "ціль задано вручну, апарат мовчить", size=13, bold=True, color=POS))
    f.append(mtext(320, 598, ["станція показує «з'єднано» — сокет же відкрито,",
                              "а датаграми йдуть у порожнечу"], size=11.5))

    f.append(rect(620, 540, 520, 120, fill=SOFT, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(880, 570, "озвався ще хтось третій", size=13, bold=True, color=FIELD))
    f.append(mtext(880, 598, ["його джерело теж потрапить у список,",
                              "і копія кожної команди піде й туди"], size=11.5))

    render(os.path.join(OUT, 'udp-targets.svg'), W, H, *f,
           title="UDP: адресата станція не налаштовує, а дізнається з першого ж пакета")


# ─────────────────────── 4. TCP проти UDP на втратах ─────────────────────────
def fig_stall():
    W, H = 1240, 560
    f = []

    xs = [x for x in range(360, 361 + 80 * 8, 80)]

    # TCP
    f.append(fitbox(40, 96, 280, 76, "TCP\nвтрачений сегмент №3", size=14, bold=True, fill=BAND))
    f.append(text(180, 200, "відправлено", size=12, color=MUTED))
    f.append(line(340, 130, 1200, 130, color=LINE, sw=1.4))
    for i, x in enumerate(xs[:8]):
        col = POS if i == 2 else NEG
        f.append(line(x, 116, x, 144, color=col, sw=2.4))
        f.append(text(x, 108, str(i + 1), size=11, color=col))

    f.append(text(180, 246, "показано на екрані", size=12, color=MUTED))
    f.append(line(340, 240, 510, 240, color=LINE, sw=1.4))
    f.append(line(840, 240, 1200, 240, color=LINE, sw=1.4))
    for i, x in enumerate(xs[:2]):
        f.append(line(x, 226, x, 254, color=NEG, sw=2.4))
        f.append(text(x, 218, str(i + 1), size=11, color=NEG))
    f.append(rect(510, 216, 330, 48, fill="#fdecea", stroke=POS, sw=1.4, rx=8))
    f.append(text(675, 246, "черга стоїть: чекаємо на повтор №3", size=12, color=POS))
    for i, x in enumerate([880, 916, 952, 988, 1024, 1060]):
        f.append(line(x, 226, x, 254, color=NEG, sw=2.4))
        f.append(text(x, 218, str(i + 3), size=11, color=NEG))
    f.append(mtext(1150, 292, ["усе дійшло — але шість кадрів стану",
                               "старші за поточний, і приїхали разом"], size=12, anchor="end"))

    # UDP
    f.append(fitbox(40, 386, 280, 76, "UDP\nвтрачена датаграма №3", size=14, bold=True, fill=BAND))
    f.append(text(180, 490, "показано на екрані", size=12, color=MUTED))
    f.append(line(340, 424, 1200, 424, color=LINE, sw=1.4))
    for i, x in enumerate(xs[:8]):
        if i == 2:
            f.append(text(x, 430, "×", size=18, color=POS, bold=True))
        else:
            f.append(line(x, 410, x, 438, color=NEG, sw=2.4))
            f.append(text(x, 402, str(i + 1), size=11, color=NEG))
    f.append(text(770, 492, "у номерах дірка, лічильник утрат росте — решта показів свіжі", size=12))

    render(os.path.join(OUT, 'stall-vs-gap.svg'), W, H, *f,
           title="Та сама втрата: TCP платить свіжістю, UDP — повнотою")


# ─────────────────────── 5. Bluetooth: два різні пристрої ────────────────────
def fig_bt():
    W, H = 1160, 520
    f = []

    f.append(rect(50, 90, 500, 380, fill=SOFT, stroke=EDGE, sw=1.8, rx=12))
    f.append(text(300, 126, "класичний режим", size=16, bold=True))
    f.append(text(300, 152, "профіль послідовного порту", size=12, color=MUTED))
    f.append(fitbox(90, 180, 420, 66, "стек ОС видає сокет, що поводиться\nяк відкритий серійний порт", size=12.5, fill=BAND))
    f.append(fitbox(90, 266, 420, 66, "потік байтів без меж — рівно те,\nчого чекає розбирач", size=12.5, fill=BAND))
    f.append(fitbox(90, 352, 420, 88, "спарення робить система;\nзастосунок лише вибирає пристрій\nзі списку знайдених", size=12.5, fill=BAND))

    f.append(rect(610, 90, 500, 380, fill=SOFT, stroke=EDGE, sw=1.8, rx=12))
    f.append(text(860, 126, "режим малого споживання", size=16, bold=True))
    f.append(text(860, 152, "характеристики й сповіщення", size=12, color=MUTED))
    f.append(fitbox(650, 180, 420, 66, "потоку немає взагалі: є запис\nі сповіщення про зміну значення", size=12.5, fill=BAND))
    f.append(fitbox(650, 266, 420, 66, "кожна порція обмежена розміром пакета —\nдесятки, зрідка дві сотні байтів", size=12.5, fill=BAND))
    f.append(fitbox(650, 352, 420, 88, "труба байтів складається зі шматків\nвже в застосунку; пропускна здатність\nу рази менша", size=12.5, fill=BAND))

    render(os.path.join(OUT, 'bluetooth-modes.svg'), W, H, *f,
           title="Під одним іменем «Bluetooth» ховаються два несхожі канали")


# ───────── 6. Датаграма ≠ повідомлення (до вставки proj-udp-endpoint) ────────
def fig_datagram_frames():
    W, H = 1280, 720
    f = []

    # три датаграми, що прийшли трьома викликами recvfrom
    f.append(text(70, 82, "три виклики recvfrom — три датаграми", size=14, bold=True, anchor="start"))

    dg = [
        (70,  250, "датаграма 1 · 21 Б", [("HEARTBEAT", 250)]),
        (360, 560, "датаграма 2 · 112 Б", [("ATTITUDE", 190), ("VFR_HUD", 160), ("GLOBAL_POSITION_INT", 210)]),
        (960, 250, "датаграма 3 · 40 Б", [("LOCAL_POSITION_NED", 250)]),
    ]
    for x, w, cap, frames in dg:
        f.append(rect(x, 100, w, 92, fill=BAND, stroke=EDGE, sw=1.8, rx=10))
        f.append(text(x + w / 2, 216, cap, size=12, color=MUTED))
        fx = x
        for k, (name, fw) in enumerate(frames):
            if k:
                f.append(line(fx, 100, fx, 192, color=EDGE, sw=1.6, dash="5,4"))
            f.append(text(fx + 14, 130, "0xFD", size=11, color=POS, anchor="start", bold=True))
            f.append(text(fx + fw / 2, 156, name, size=11.5, anchor="middle"))
            f.append(text(fx + fw / 2, 178, "кадр MAVLink", size=10.5, color=MUTED, anchor="middle"))
            fx += fw

    for x, w, _, _ in dg:
        f.append(arrow(x + w / 2, 226, x + w / 2, 276))

    # байтовий цикл
    f.append(rect(70, 286, 1140, 104, fill=SOFT, stroke=INK, sw=2.0, rx=10))
    f.append(text(640, 320, "for (i = 0; i < n; ++i)  mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &st);",
                  size=14, bold=True))
    f.append(text(640, 352, "межі датаграм циклу не потрібні: початок кадру розбирач знаходить сам —",
                  size=12, color=MUTED))
    f.append(text(640, 372, "за стартовим байтом, полем довжини й контрольною сумою", size=12, color=MUTED))

    f.append(arrow(640, 390, 640, 424))

    # вихід — п'ять повідомлень
    f.append(text(70, 418, "на виході — п'ять повідомлень, і жодне не знає, з якої датаграми прийшло",
                  size=13, bold=True, anchor="start"))
    outs = ["HEARTBEAT", "ATTITUDE", "VFR_HUD", "GLOBAL_POSITION_INT", "LOCAL_POSITION_NED"]
    ox = 70
    for name in outs:
        w = 226
        f.append(rect(ox, 434, w, 46, fill="#eaf6ee", stroke=FIELD, sw=1.6, rx=8))
        f.append(fitbox(ox, 434, w, 46, name, size=12, fill="#eaf6ee", stroke=FIELD, sw=1.6, rx=8))
        ox += w + 2

    # дві пастки внизу
    f.append(rect(70, 522, 556, 158, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(348, 552, "буфер на 280 байтів — «розмір одного кадру»", size=13.5, bold=True, color=POS))
    f.append(fitbox(96, 570, 504, 92,
                    "recvfrom бере скільки влізло, решту датаграми ядро ВИКИДАЄ.\n"
                    "Наступний байт у циклі — початок уже іншої датаграми,\n"
                    "тож обірваний кадр з'їдає й сусідній: суцільні помилки CRC.",
                    size=12, fill="#fdecea", stroke="#f5c6c0", sw=1.0))

    f.append(rect(654, 522, 556, 158, fill="#eaf6ee", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(932, 552, "буфер на десятки кілобайтів", size=13.5, bold=True, color=FIELD))
    f.append(fitbox(680, 570, 504, 92,
                    "Датаграма влазить цілою за будь-якого склеювання.\n"
                    "Верхня межа однієї датаграми IPv4 — 65507 байтів,\n"
                    "тож 64 КБ закривають випадок назавжди.",
                    size=12, fill="#eaf6ee", stroke="#bfe3cc", sw=1.0))

    render(os.path.join(OUT, 'datagram-frames.svg'), W, H, *f,
           title="Одна датаграма може везти нуль меж і кілька повідомлень")


# ───────── 7. Лічильник розривів — свій на кожного відправника ───────────────
def fig_seq_gaps():
    W, H = 1240, 660
    f = []

    # потік, що прийшов
    f.append(text(70, 82, "порядок, у якому кадри вийшли з розбирача", size=14, bold=True, anchor="start"))
    stream = [
        ("sys 1 · comp 1", "seq 41", NEG),
        ("sys 1 · comp 100", "seq 7", POS),
        ("sys 1 · comp 1", "seq 42", NEG),
        ("sys 1 · comp 1", "seq 44", NEG),
        ("sys 1 · comp 100", "seq 8", POS),
    ]
    sx = 70
    for who, sq, col in stream:
        f.append(rect(sx, 100, 210, 74, fill=SOFT, stroke=col, sw=1.8, rx=8))
        f.append(text(sx + 105, 126, who, size=12, color=col, bold=True))
        f.append(text(sx + 105, 152, sq, size=13))
        if sx < 900:
            f.append(arrow(sx + 214, 137, sx + 224, 137, color=MUTED, sw=1.4))
        sx += 234

    # ліворуч — один спільний лічильник
    f.append(rect(70, 220, 556, 296, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(348, 252, "один лічильник на канал", size=15, bold=True, color=POS))
    f.append(fitbox(96, 270, 504, 44, "очікуваний номер один на всіх, хто говорить у сокет",
                    size=12, fill="#fdecea", stroke="#f5c6c0", sw=1.0))
    rows_bad = [
        ("41 при очікуваному 41", "розрив 0", MUTED),
        ("7 при очікуваному 42", "розрив 221", POS),
        ("42 при очікуваному 8", "розрив 34", POS),
        ("44 при очікуваному 43", "розрив 1", MUTED),
        ("8 при очікуваному 45", "розрив 219", POS),
    ]
    ry = 326
    for a, b, col in rows_bad:
        f.append(text(112, ry, a, size=12, anchor="start"))
        f.append(text(584, ry, b, size=12, color=col, bold=(col == POS), anchor="end"))
        ry += 30
    f.append(line(112, 464, 584, 464, color="#f5c6c0", sw=1.2))
    f.append(text(112, 492, "разом «утрачено» 475 з 5 отриманих", size=13, bold=True, color=POS, anchor="start"))

    # праворуч — табличка на кожного відправника
    f.append(rect(654, 220, 556, 296, fill="#eaf6ee", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(932, 252, "свій лічильник на пару (sysid, compid)", size=15, bold=True, color=FIELD))
    f.append(fitbox(680, 270, 504, 44, "ключ у таблиці — той, хто підписався у кадрі",
                    size=12, fill="#eaf6ee", stroke="#bfe3cc", sw=1.0))
    rows_ok = [
        ("comp 1: 41 — перший, беремо за відлік", "—", MUTED),
        ("comp 100: 7 — перший, беремо за відлік", "—", MUTED),
        ("comp 1: 42 при очікуваному 42", "розрив 0", MUTED),
        ("comp 1: 44 при очікуваному 43", "розрив 1", FIELD),
        ("comp 100: 8 при очікуваному 8", "розрив 0", MUTED),
    ]
    ry = 326
    for a, b, col in rows_ok:
        f.append(text(696, ry, a, size=12, anchor="start"))
        f.append(text(1168, ry, b, size=12, color=col, bold=(col == FIELD), anchor="end"))
        ry += 30
    f.append(line(696, 464, 1168, 464, color="#bfe3cc", sw=1.2))
    f.append(text(696, 492, "разом утрачено 1 — стільки й було", size=13, bold=True, color=FIELD, anchor="start"))

    # арифметика згортання
    f.append(rect(70, 548, 1140, 84, fill=BAND, stroke=EDGE, sw=1.6, rx=10))
    f.append(text(640, 580, "розрив = (uint8_t)(seq − очікуваний)", size=15, bold=True))
    f.append(text(640, 608,
                  "віднімання у восьми бітах згортається саме: очікували 0, прийшов 255 → 255 утрат; "
                  "очікували 0, прийшов 0 → 0",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'seq-gaps.svg'), W, H, *f,
           title="Номери послідовності незалежні в кожного відправника")


# ═══ Фігури до вставки comp-serial-adapters ══════════════════════════════════

# ───────── 8. Три конструкції моста між платою й портом ──────────────────────
def fig_adapters():
    W, H = 1320, 790
    f = []

    # ── ряд A: вбудований у мікроконтролер USB ───────────────────────────────
    f.append(rect(30, 70, 1260, 200, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(50, 112, "вбудований USB", size=14, bold=True, anchor="start"))
    f.append(text(50, 136, "плата говорить по USB сама", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(260, 125, 200, 90, "мікроконтролер:\nUSB-периферія\nвсередині нього", size=12, fill=SOFT))
    f.append(arrow(464, 170, 504, 170))
    f.append(text(484, 156, "USB", size=11, color=MUTED))
    f.append(fitbox(510, 125, 210, 90, "драйвер класу —\nодин на всі\nтакі пристрої", size=12, fill=SOFT))
    f.append(arrow(724, 170, 764, 170))
    f.append(fitbox(770, 125, 200, 90, "вузол з іменем\nза класом:\nttyACM, usbmodem", size=12, fill=SOFT))
    f.append(fitbox(1000, 118, 270, 104,
                    "число швидкості нікуди\nне доходить: справжнього\nUART за портом немає",
                    size=11.5, fill="#fdecea", stroke=POS))

    # ── ряд B: окрема мікросхема-міст ────────────────────────────────────────
    f.append(rect(30, 300, 1260, 200, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(50, 342, "окремий міст", size=14, bold=True, anchor="start"))
    f.append(text(50, 366, "мікросхема поруч із МК", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(250, 355, 160, 90, "мікроконтролер", size=12, fill=SOFT))
    f.append(arrow(414, 400, 446, 400))
    f.append(text(430, 386, "UART", size=11, color=MUTED))
    f.append(fitbox(450, 355, 160, 90, "мікросхема-міст\nUSB↔UART", size=12, fill=SOFT))
    f.append(arrow(614, 400, 646, 400))
    f.append(text(630, 386, "USB", size=11, color=MUTED))
    f.append(fitbox(650, 355, 190, 90, "драйвер під саме\nцю модель мосту", size=12, fill=SOFT))
    f.append(arrow(844, 400, 876, 400))
    f.append(fitbox(880, 355, 170, 90, "вузол ttyUSB,\nusbserial", size=12, fill=SOFT))
    f.append(fitbox(1070, 348, 200, 104,
                    "число швидкості\nпрограмує дільник —\nмусить збігатися",
                    size=11.5, fill="#eaf0fd", stroke=NEG))

    # ── ряд C: радіомодуль — міст в одному корпусі з радіо ───────────────────
    f.append(rect(30, 530, 1260, 200, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(50, 572, "радіомодуль", size=14, bold=True, anchor="start"))
    f.append(text(50, 596, "міст і радіо в одному", size=11, color=MUTED, anchor="start"))
    f.append(text(50, 620, "корпусі", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(250, 585, 130, 90, "контролер\nборту", size=11.5, fill=SOFT))
    f.append(arrow(384, 630, 408, 630))
    f.append(text(396, 574, "UART", size=10.5, color=MUTED))
    f.append(fitbox(412, 585, 120, 90, "радіо\nборту", size=11.5, fill=SOFT))
    f.append(line(536, 630, 594, 630, color=MUTED, sw=2, dash="6,5"))
    f.append(text(565, 574, "ефір", size=10.5, color=MUTED))
    f.append(fitbox(598, 585, 120, 90, "радіо\nземлі", size=11.5, fill=SOFT))
    f.append(arrow(722, 630, 750, 630))
    f.append(fitbox(754, 585, 190, 90, "міст USB↔UART\nу тому ж корпусі", size=11.5, fill=SOFT))
    f.append(arrow(948, 630, 976, 630))
    f.append(fitbox(980, 585, 160, 90, "вузол ttyUSB", size=11.5, fill=SOFT))
    f.append(fitbox(1160, 578, 115, 104, "швидкість —\nмосту,\nа не борту", size=11, fill="#eaf0fd", stroke=NEG))

    f.append(text(660, 766,
                  "функція в усіх трьох однакова; різняться драйвер, ім'я вузла й те, чи означає щось число швидкості",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, 'adapter-classes.svg'), W, H, *f,
           title="Три конструкції одного й того самого перекладача з USB на UART")


# ───────── 9. DTR і перезавантаження плати при відкритті порту ───────────────
def fig_dtr():
    W, H = 1240, 580
    f = []

    # ── варіант із справжніми виводами ───────────────────────────────────────
    f.append(rect(60, 66, 1120, 244, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(90, 96, "міст із справжніми виводами", size=14, bold=True, anchor="start"))

    steps = [
        (80, "застосунок\nвідкриває порт"),
        (300, "лінія DTR переходить\nу стверджений стан"),
        (520, "конденсатор пропускає\nтільки фронт: короткий\nімпульс на вхід скидання"),
        (740, "плата перезавантажується\nі стартує з завантажувача"),
        (960, "прошивка оживає,\nперші байти йдуть\nіз затримкою"),
    ]
    for x, s in steps:
        f.append(fitbox(x, 112, 200, 96, s, size=11.5, fill=SOFT))
        f.append(arrow(x + 100, 210, x + 100, 264))
        f.append(circle(x + 100, 272, 5, fill=SOFT, stroke=LINE, sw=1.6))
    f.append(line(80, 272, 1160, 272, color=LINE, sw=2))
    f.append(text(620, 298, "порт лише відкрили — а весь стан плати вже скинуто", size=12.5, color=POS))

    # ── варіант із вбудованим USB ────────────────────────────────────────────
    f.append(rect(60, 330, 1120, 210, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(90, 360, "вбудований USB: цих виводів фізично немає", size=14, bold=True, anchor="start"))

    f.append(fitbox(80, 378, 300, 140, "DTR і RTS доходять\nдо плати як керуючий\nзапит — і тільки", size=12, fill=SOFT))
    f.append(arrow(384, 420, 474, 410))
    f.append(arrow(384, 474, 474, 484))
    f.append(fitbox(478, 378, 340, 66, "прошивка запит ігнорує", size=12, fill=SOFT))
    f.append(fitbox(478, 452, 340, 66, "прошивка тлумачить умовне число\nшвидкості як «іди в завантажувач»", size=11.5, fill=SOFT))
    f.append(arrow(822, 411, 854, 411))
    f.append(arrow(822, 485, 854, 485))
    f.append(fitbox(858, 378, 300, 66, "відкриття порту безпечне", size=12, fill="#eaf6ee", stroke=FIELD))
    f.append(fitbox(858, 452, 300, 66, "плата пішла в завантажувач", size=12, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'dtr-reset.svg'), W, H, *f,
           title="Дві лінії, якими не передають даних, — і дві різні долі плати")


# ───────── 10. Апаратне керування потоком на радіомодулі ─────────────────────
def fig_flow():
    W, H = 1200, 520
    f = []

    f.append(rect(50, 66, 560, 430, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(330, 96, "без апаратного керування потоком", size=14, bold=True))
    f.append(fitbox(80, 112, 500, 58, "у модуль ллється 5760 байтів/с", size=12.5, fill=SOFT))
    f.append(arrow(330, 174, 330, 198))
    f.append(fitbox(80, 202, 500, 58, "ефір виносить у рази менше — буфер повний", size=12.5, fill=SOFT))
    f.append(arrow(330, 264, 330, 288))
    f.append(fitbox(80, 292, 500, 58, "зайві байти зникають мовчки", size=12.5, fill="#fdecea", stroke=POS))
    f.append(arrow(330, 354, 330, 378))
    f.append(fitbox(80, 382, 500, 96,
                    "нагорі: биті контрольні суми й дірки\nв номерах — схоже на «поганий зв'язок»,\nхоча антена й потужність ні до чого",
                    size=12, fill=SOFT))

    f.append(rect(610, 66, 560, 430, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(890, 96, "з апаратним керуванням потоком", size=14, bold=True))
    f.append(fitbox(640, 112, 500, 58, "буфер модуля заповнився до порога", size=12.5, fill=SOFT))
    f.append(arrow(890, 174, 890, 198))
    f.append(fitbox(640, 202, 500, 58, "модуль знімає готовність на своєму виводі", size=12.5, fill=SOFT))
    f.append(arrow(890, 264, 890, 288))
    f.append(fitbox(640, 292, 500, 58, "передавач зупиняється між кадрами", size=12.5, fill="#eaf6ee", stroke=FIELD))
    f.append(arrow(890, 354, 890, 378))
    f.append(fitbox(640, 382, 500, 96,
                    "байти не губляться, лише чекають;\nале якщо дріт заведено з одного боку,\nчекання стає вічним і не піде жоден байт",
                    size=12, fill=SOFT))

    render(os.path.join(OUT, 'flow-control-radio.svg'), W, H, *f,
           title="Куди діваються байти, коли серійний вхід швидший за ефір")


# ─────────────── 11. Шлях байтів крізь контракт (до вставки api) ─────────────
def fig_write_path():
    W, H = 1360, 810
    f = []

    # підписи ниток
    f.append(text(450, 44, "головна нитка застосунку", size=14, bold=True, color=MUTED))
    f.append(text(1105, 44, "нитка каналу — лише вона торкається порту",
                 size=14, bold=True, color=MUTED))
    f.append(line(860, 62, 860, 782, color=LINE, sw=2.2, dash="10,7"))

    # ── панель 1: відправлення ──────────────────────────────────────────────
    f.append(rect(30, 72, 1300, 312, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(58, 106, "ВНИЗ — відправлення байтів", size=15, bold=True, anchor="start"))

    f.append(fitbox(55, 152, 215, 140,
                    "підсистема застосунку\n\nVehicle · параметри\nплан місії", size=13, fill=SOFT))
    f.append(fitbox(330, 152, 225, 140,
                    "writeBytesThreadSafe()\n\nготове\nв базовому класі", size=13, fill=SOFT))
    f.append(fitbox(615, 152, 225, 140,
                    "_writeBytes()\n\nВІРТУАЛЬНЕ\nтіло пише нащадок", size=13, fill="#fdecea",
                    stroke=POS, sw=2))
    f.append(fitbox(920, 152, 215, 140,
                    "writeData()\n\nслот робітника", size=13, fill=SOFT))
    f.append(fitbox(1190, 152, 125, 140, "порт\nсокет", size=13, fill=SOFT))

    for x1, x2 in ((270, 330), (555, 615), (840, 920), (1135, 1190)):
        f.append(arrow(x1, 222, x2, 222, color=POS))
    f.append(text(300, 330, "з будь-якої нитки", size=11, color=MUTED))
    f.append(text(585, 330, "Qt::AutoConnection", size=11, color=MUTED))
    f.append(text(880, 330, "Qt::QueuedConnection", size=11, color=MUTED))
    f.append(text(1162, 330, "запис", size=11, color=MUTED))

    # ── панель 2: приймання ─────────────────────────────────────────────────
    f.append(rect(30, 424, 1300, 312, fill=BAND, stroke=EDGE, sw=1.6, rx=12))
    f.append(text(58, 458, "ВГОРУ — прийняті байти", size=15, bold=True, anchor="start"))

    f.append(fitbox(1190, 504, 125, 140, "порт\nсокет", size=13, fill=SOFT))
    f.append(fitbox(920, 504, 215, 140,
                    "dataReceived()\n\nсигнал робітника", size=13, fill=SOFT))
    f.append(fitbox(615, 504, 225, 140,
                    "_onDataReceived()\n\nобробник нащадка", size=13, fill=SOFT))
    f.append(fitbox(330, 504, 225, 140,
                    "bytesReceived()\n\nсигнал каналу", size=13, fill=SOFT))
    f.append(fitbox(55, 504, 215, 140,
                    "MAVLinkProtocol\n\nрозбирач байт за байтом", size=13, fill=SOFT))

    for x1, x2 in ((1190, 1135), (920, 840), (615, 555), (330, 270)):
        f.append(arrow(x1, 574, x2, 574, color=NEG))
    f.append(text(1162, 682, "readAll", size=11, color=MUTED))
    f.append(text(880, 682, "черга через межу нитки", size=11, color=MUTED))
    f.append(text(585, 682, "прямий виклик", size=11, color=MUTED))
    f.append(text(300, 682, "масив байтів", size=11, color=MUTED))

    f.append(text(680, 782,
                  "обидва обов'язкові методи роботи з байтами — лише перекидачі через межу нитки",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'write-path.svg'), W, H, *f,
           title="Куди в контракті каналу лягає кожен обов'язковий метод")


fig_seam()
fig_serial()
fig_udp()
fig_stall()
fig_bt()
fig_datagram_frames()
fig_seq_gaps()
fig_adapters()
fig_dtr()
fig_flow()
fig_write_path()
print("ok")
