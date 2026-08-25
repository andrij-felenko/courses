# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GEN = "#eef4ff"   # згенерований код
REAL = "#eaf6ef"  # справжні об'єкти
PAD = "#fdecea"   # заповнювач / втрата


# ── 1. Шлях одного виклику: де саме народжується ілюзія ──────────────────────
def fig_call_path():
    W, H = 1060, 550
    p = []

    p.append(text(250, 52, "Процес клієнта", size=15, bold=True))
    p.append(text(810, 52, "Процес сервера", size=15, bold=True))
    p.append(text(530, 62, "межа машин", size=12, color=MUTED))
    p.append(line(530, 74, 530, 300, color=MUTED, sw=1.4, dash="6 6"))

    CX, SX, BW, BH = 70, 630, 360, 56
    rows = [85, 165, 245, 325]

    client = [
        ("код клієнта\nacc->withdraw(50)", REAL, FIELD),
        ("стаб, згенерований з IDL\nвиклик стає повідомленням", GEN, NEG),
        ("ORB клієнта\nз'єднання, таймаути, помилки", FILL, LINE),
        ("сокет TCP", "#f0f0f0", LINE),
    ]
    server = [
        ("сервант — справжній об'єкт\nзвичайний метод класу", REAL, FIELD),
        ("скелет, згенерований з IDL\nповідомлення стає викликом", GEN, NEG),
        ("адаптер об'єктів (POA)\nключ об'єкта → потрібний сервант", FILL, LINE),
        ("сокет TCP", "#f0f0f0", LINE),
    ]

    for i, (s, f, st) in enumerate(client):
        p.append(fitbox(CX, rows[i], BW, BH, s, size=13.5, fill=f, stroke=st, sw=1.7))
    for i, (s, f, st) in enumerate(server):
        p.append(fitbox(SX, rows[i], BW, BH, s, size=13.5, fill=f, stroke=st, sw=1.7))

    # клієнт — згори вниз
    for i in range(3):
        y1 = rows[i] + BH + 2
        y2 = rows[i + 1] - 4
        p.append(arrow(CX + BW / 2, y1, CX + BW / 2, y2, color=NEG, sw=2))
    # сервер — знизу вгору
    for i in range(3, 0, -1):
        y1 = rows[i] - 4
        y2 = rows[i - 1] + BH + 2
        p.append(arrow(SX + BW / 2, y1, SX + BW / 2, y2, color=FIELD, sw=2))

    # провід
    p.append(text(530, 314, "запит: GIOP Request", size=12.5, bold=True))
    p.append(arrow(436, 341, 624, 341, color=INK, sw=2))
    p.append(arrow(624, 367, 436, 367, color=MUTED, sw=2))
    p.append(text(530, 400, "відповідь: GIOP Reply", size=12.5, bold=True, color=MUTED))

    p.append(fitbox(70, 448, 920, 74,
                    "Ілюзія народжується рівно на двох стиках: стаб перетворює виклик на повідомлення,"
                    "\nскелет перетворює повідомлення на виклик. Усе, що лежить між ними, —"
                    "\nзвичайна ненадійна мережа, і жоден із цих двох стиків її не скасовує.",
                    size=13.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    render(os.path.join(IMG, 'call-path.svg'), W, H, *p,
           title="Шлях одного виклику через брокер")


# ── 2. Байти в проводі: заголовок GIOP і вирівнювання CDR ────────────────────
def fig_wire_bytes():
    W, H = 1040, 490
    p = []

    # ── заголовок: 12 клітинок по байту ──
    cw, n = 78, 12
    x0 = (W - cw * n) / 2
    ry, rh = 150, 52

    lbl, lw, lh = textbox(559, 92, "прапорці: біт 0 — чий порядок байтів",
                          size=12.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6, pad=9)
    p.append(lbl)
    p.append(arrow(559, 92 + lh / 2 + 2, 559, ry - 4, color="#b58900", sw=1.8))

    cells = ["G", "I", "O", "P", "1", "2", "прап.", "тип"]
    for i, s in enumerate(cells):
        p.append(fitbox(x0 + i * cw, ry, cw, rh, s, size=15, bold=True))
    p.append(fitbox(x0 + 8 * cw, ry, cw * 4, rh, "розмір тіла", size=15, bold=True))

    for i in range(n):
        p.append(text(x0 + i * cw + cw / 2, ry + rh + 20, str(i), size=11, color=MUTED))

    p.append(text(W / 2, ry + rh + 48,
                  "заголовок GIOP — рівно 12 байтів у кожному повідомленні",
                  size=13.5, bold=True))

    # ── тіло: блоки пропорційно до розміру ──
    by, bh = 308, 62
    blocks = [
        ("запит №\n4 Б", 100, FILL, LINE),
        ("чи ждати\n1 Б", 62, FILL, LINE),
        ("заповн.\n3 Б", 72, PAD, POS),
        ("довжина\n4 Б", 92, FILL, LINE),
        ("ключ об'єкта\n8 Б", 112, FILL, LINE),
        ("заповн.\n2 Б", 66, PAD, POS),
        ("довжина + «withdraw»\n13 Б", 172, FILL, LINE),
        ("заповн.\n3 Б", 70, PAD, POS),
        ("контексти\n4 Б", 96, FILL, LINE),
        ("сума = 50\n4 Б", 100, REAL, FIELD),
    ]
    total = sum(b[1] for b in blocks)
    bx = (W - total) / 2
    p.append(text(W / 2, by - 18, "тіло запиту в CDR: acc->withdraw(50)", size=14, bold=True))
    for s, w, f, st in blocks:
        p.append(fitbox(bx, by, w, bh, s, size=13, fill=f, stroke=st, sw=1.6))
        bx += w

    p.append(fitbox(60, by + bh + 26, 920, 62,
                    "Жодного тега поля: ЩО саме читати, приймач знає лише з того самого IDL."
                    "\nДодав поле в структуру — старий приймач мовчки прочитає сміття.",
                    size=13.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    render(os.path.join(IMG, 'wire-bytes.svg'), W, H, *p,
           title="Що саме летить проводом")


# ── 3. IOR: посилання, яке носить у собі адресу ──────────────────────────────
def fig_ior():
    W, H = 1040, 500
    p = []

    p.append(rect(60, 70, 490, 332, fill="#fafbfc", stroke=LINE, sw=1.8))
    p.append(text(305, 96, "IOR — рядок, який можна віддати будь-кому", size=13.5, bold=True))
    p.append(fitbox(80, 112, 450, 50, "тип: IDL:bank/Account:1.0", size=13.5))
    p.append(fitbox(80, 176, 450, 62,
                    "профіль IIOP №1\nхост a.bank · порт 8402 · ключ 0x7f2c…",
                    size=13, fill=GEN, stroke=NEG, sw=1.6))
    p.append(fitbox(80, 250, 450, 62,
                    "профіль IIOP №2\nхост b.bank · порт 8402 · ключ 0x7f2c…",
                    size=13, fill=GEN, stroke=NEG, sw=1.6))
    p.append(fitbox(80, 324, 450, 50, "компоненти: кодування, політики, TLS", size=13))

    p.append(fitbox(720, 158, 260, 62, "сервер A\nадаптер тримає об'єкт",
                    size=13, fill=REAL, stroke=FIELD, sw=1.6))
    p.append(fitbox(720, 264, 260, 62, "сервер B\nтой самий ключ, запасний вузол",
                    size=13, fill=FILL, stroke=LINE, sw=1.6))

    p.append(arrow(556, 208, 714, 190, color=FIELD, sw=2))
    p.append(arrow(556, 284, 714, 296, color=MUTED, sw=2))
    p.append(text(632, 146, "спершу — сюди", size=12, bold=True, color=FIELD))
    p.append(text(632, 344, "як A мовчить — клієнт бере B", size=12, bold=True, color=MUTED))

    p.append(fitbox(60, 420, 920, 56,
                    "Ключ об'єкта непрозорий для клієнта: його зміст розуміє лише той адаптер, що видав посилання.",
                    size=13.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    render(os.path.join(IMG, 'ior.svg'), W, H, *p,
           title="Посилання на віддалений об'єкт")


# ── 4. Три способи, якими виклик не вдається — і однакова тиша ───────────────
def xmark(cx, cy, r=9, color=POS):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=3) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=3))


def fig_partial_failure():
    W, H = 1040, 440
    p = []
    panels = [
        (25, "запит не дійшов", "нічого не сталося\nCOMPLETED_NO", None, False),
        (370, "відповідь загубилася", "зроблено, клієнт не знає\nCOMPLETED_MAYBE", "списано 50", True),
        (715, "сервер упав під час роботи", "зроблено чи ні — невідомо\nCOMPLETED_MAYBE", "почав і впав", False),
    ]

    for idx, (px, title, verdict, work, reply_lost) in enumerate(panels):
        p.append(rect(px, 58, 300, 336, fill="#fbfbfc", stroke="#d8d8dc", sw=1.2))
        p.append(fitbox(px + 12, 70, 276, 46, title, size=13.5, bold=True,
                        fill=FILL, stroke=LINE, sw=1.5))

        clx, srx = px + 80, px + 220
        p.append(text(clx, 140, "клієнт", size=12, bold=True))
        p.append(text(srx, 140, "сервер", size=12, bold=True))
        p.append(line(clx, 150, clx, 300, color=MUTED, sw=1.4, dash="5 5"))

        if work:
            p.append(line(srx, 150, srx, 199, color=MUTED, sw=1.4, dash="5 5"))
            p.append(line(srx, 251, srx, 300, color=MUTED, sw=1.4, dash="5 5"))
            p.append(fitbox(px + 166, 203, 108, 44, work, size=12,
                            fill=REAL if idx == 1 else PAD,
                            stroke=FIELD if idx == 1 else POS, sw=1.6))
        else:
            p.append(line(srx, 150, srx, 300, color=MUTED, sw=1.4, dash="5 5"))

        p.append(text(px + 150, 167, "запит", size=11.5, color=MUTED))
        if idx == 0:
            p.append(arrow(clx, 187, px + 156, 187, color=INK, sw=2))
            p.append(xmark(px + 174, 187))
        else:
            p.append(arrow(clx, 187, srx - 4, 187, color=INK, sw=2))

        if idx == 1:
            p.append(text(px + 150, 252, "відповідь", size=11.5, color=MUTED))
            p.append(arrow(srx, 274, px + 166, 274, color=INK, sw=2))
            p.append(xmark(px + 146, 274))
        elif idx == 2:
            p.append(text(px + 150, 278, "тиша", size=12, bold=True, color=POS))
        else:
            p.append(text(px + 150, 278, "тиша", size=12, bold=True, color=POS))

        p.append(fitbox(px + 12, 312, 276, 68, verdict, size=13,
                        fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    p.append(text(W / 2, 420, "клієнт в усіх трьох випадках бачить те саме — тишу",
                  size=13.5, bold=True))

    render(os.path.join(IMG, 'partial-failure.svg'), W, H, *p,
           title="Три різні світи, один вигляд ззовні")


# ── 5. Дамп справжнього запиту мініатюрного брокера ─────────────────────────
def fig_mini_dump():
    W, H = 1040, 566
    p = []
    HDR = "#eef1f5"
    RID = "#f4f6f8"
    KEYC = "#eaf0fd"
    OPC = "#f5edfb"
    OPS = "#7b52ab"

    dump = [
        0x4d, 0x4f, 0x52, 0x42, 0x01, 0x00, 0x01, 0x00,
        0x24, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x08, 0x00, 0x00, 0x00, 0x7b, 0x1c, 0xf3, 0x5a,
        0x01, 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00,
        0x77, 0x69, 0x74, 0x68, 0x64, 0x72, 0x61, 0x77,
        0x00, 0x00, 0x00, 0x00, 0x32, 0x00, 0x00, 0x00,
    ]

    def colour(off):
        if off < 12:
            return HDR, LINE
        if off < 16:
            return RID, LINE
        if off < 28:
            return KEYC, NEG
        if off < 41:
            return OPC, OPS
        if off < 44:
            return PAD, POS
        return REAL, FIELD

    p.append(text(W / 2, 58, "acc->withdraw(50) — сорок вісім байтів, що йдуть у сокет",
                  size=13.5, color=MUTED))

    cw, ch, gap = 84, 44, 8
    x0, y0 = 184, 88
    for off, b in enumerate(dump):
        r, c = divmod(off, 8)
        f, st = colour(off)
        p.append(fitbox(x0 + c * cw, y0 + r * (ch + gap), cw, ch, "%02x" % b,
                        size=15, bold=True, fill=f, stroke=st, sw=1.4))
    for r in range(6):
        p.append(text(x0 - 22, y0 + r * (ch + gap) + ch / 2 + 5, "%02X" % (r * 8),
                      size=12, color=MUTED, anchor="end"))

    ly = y0 + 6 * (ch + gap) + 14
    legend = [
        ("заголовок\n12 Б", HDR, LINE),
        ("номер запиту\n4 Б", RID, LINE),
        ("ключ об'єкта\n4 + 8 Б", KEYC, NEG),
        ("назва операції\n4 + 9 Б", OPC, OPS),
        ("заповнювач\n3 Б", PAD, POS),
        ("аргумент 50\n4 Б", REAL, FIELD),
    ]
    lw = 152
    lx = (W - lw * len(legend)) / 2
    for i, (s, f, st) in enumerate(legend):
        p.append(fitbox(lx + i * lw + 4, ly, lw - 8, 48, s, size=12.5, fill=f, stroke=st, sw=1.5))

    p.append(fitbox(70, ly + 62, 900, 58,
                    "Чотири байти корисного аргументу, три байти чистого заповнювача"
                    "\nі сорок один байт на те, КОМУ і ЩО саме сказати.",
                    size=13.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    render(os.path.join(IMG, 'mini-request-dump.svg'), W, H, *p,
           title="Дамп запиту мініатюрного брокера")


# ── 6. Потік TCP не має меж повідомлень ─────────────────────────────────────
def fig_mini_partial_read():
    W, H = 1040, 482
    p = []
    x0, scale = 180, 10.0

    p.append(text(W / 2, 62, "що ми поклали у два send()", size=13.5, bold=True))
    msgs = [("запит: 48 Б", 48, REAL, FIELD), ("відповідь: 20 Б", 20, GEN, NEG)]
    bx = x0
    for s, n, f, st in msgs:
        p.append(fitbox(bx, 78, n * scale, 54, s, size=13, fill=f, stroke=st, sw=1.7))
        bx += n * scale

    bound = x0 + 48 * scale
    p.append(line(bound, 74, bound, 262, color=POS, sw=1.8, dash="6 5"))
    p.append(text(bound + 96, 156, "межа повідомлень", size=12, bold=True, color=POS))

    p.append(text(W / 2, 190, "що чотири рази повернув recv()", size=13.5, bold=True))
    chunks = [7, 30, 25, 6]
    bx = x0
    for n in chunks:
        p.append(fitbox(bx, 206, n * scale, 54, "%d Б" % n, size=13,
                        fill=FILL, stroke=LINE, sw=1.7))
        bx += n * scale

    p.append(fitbox(60, 296, 440, 96,
                    "наївно: одне recv() — одне повідомлення"
                    "\nперший виклик віддав 7 байтів, і розбір"
                    "\nпочинається з половини заголовка",
                    size=13, fill=PAD, stroke=POS, sw=1.7))
    p.append(fitbox(540, 296, 440, 96,
                    "правильно: read_n(12) → узяти розмір тіла"
                    "\n→ read_n(розмір) у той самий буфер"
                    "\nповідомлення збереться з будь-яких шматків",
                    size=13, fill=REAL, stroke=FIELD, sw=1.7))

    p.append(text(W / 2, 434, "recv() віддає стільки байтів, скільки вже прийшло, — не стільки, скільки треба",
                  size=13.5, bold=True))

    render(os.path.join(IMG, 'mini-partial-read.svg'), W, H, *p,
           title="Чому читання доводиться складати руками")


# ── 7. Хроніка: що ухвалювала OMG і що тим часом робив ринок ────────────────
def fig_timeline():
    W, H = 1060, 866
    p = []

    SPINE = 372
    LX, LW = 30, 300      # ліва колонка: рішення консорціуму
    RX, RW = 414, 612     # права колонка: те, що діялося без нього
    Y0, PITCH, BH = 112, 58, 44

    rows = [
        ("1989", "засновано OMG\nодинадцять компаній-засновниць", ""),
        ("1991", "CORBA 1.0 (жовтень)\nлише C; спільного проводу нема", ""),
        ("1992", "", "Orbix — перший комерційний брокер (IONA, Дублін)"),
        ("1996", "CORBA 2.0 (серпень)\nGIOP/IIOP: брокери нарешті сумісні",
                 "DCOM: Microsoft іде власним шляхом"),
        ("1997", "", "Borland купує Visigenic (VisiBroker); IONA виходить на NASDAQ"),
        ("1998", "CORBA 2.2 (лютий)\nPOA замість старого адаптера", ""),
        ("2000", "", "SOAP і веб-сервіси: виклик іде туди, куди пускає мережа"),
        ("2002", "CORBA 3.0 (липень)\nкомпонентна модель CCM",
                 "AT&T Labs Cambridge закривають — omniORB стає незалежним"),
        ("2004", "OMG ухвалює DDS\nне виклик об'єкта, а публікація даних", ""),
        ("2006", "", "Michi Henning: «The Rise and Fall of CORBA»"),
        ("2018", "", "Java 11 викидає CORBA із платформи (JEP 320)"),
        ("2021", "CORBA 3.4 (лютий)\nстандарт живий і досі", ""),
    ]

    p.append(text(LX + LW / 2, 72, "що ухвалював консорціум", size=14, bold=True))
    p.append(text(SPINE, 72, "рік", size=13, bold=True, color=MUTED))
    p.append(text(RX + RW / 2, 72, "що тим часом діялося на ринку", size=14, bold=True))

    y_last = Y0 + (len(rows) - 1) * PITCH
    p.append(line(SPINE, 90, SPINE, y_last + 34, color=MUTED, sw=1.6))

    late = {"2006", "2018"}
    for i, (year, left, right) in enumerate(rows):
        cy = Y0 + i * PITCH
        if left:
            p.append(fitbox(LX, cy - BH / 2, LW, BH, left, size=12.5,
                            fill=GEN, stroke=NEG, sw=1.6))
        if right:
            f, st = (PAD, POS) if year in late else (FILL, LINE)
            p.append(fitbox(RX, cy - BH / 2, RW, BH, right, size=12.5,
                            fill=f, stroke=st, sw=1.6))
        p.append(circle(SPINE, cy, 25, fill=BG, stroke=MUTED, sw=1.6))
        p.append(text(SPINE, cy + 4.5, year, size=12.5, bold=True, color=MUTED))

    p.append(fitbox(30, y_last + 48, 996, 62,
                    "П'ять років між першою версією і спільним форматом повідомлень —"
                    "\nстільки часу брокери різних виробників не могли обмінятися жодним байтом.",
                    size=13.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    render(os.path.join(IMG, 'corba-timeline.svg'), W, H, *p,
           title="Хроніка CORBA: стандарт і ринок")


# ── 8. Трійка _ptr / _var / _out: хто з них власник ────────────────────────
def fig_var_lifecycle():
    W, H = 1060, 590
    p = []

    cols = [
        (40, "A_ptr",
         "сире посилання\nне звільняє нічого само\nпорівнювати == не можна",
         PAD, POS),
        (370, "A_var",
         "обгортка з деструктором\nrelease() на виході з області\nin() inout() out() _retn()",
         REAL, FIELD),
        (700, "A_out",
         "тип лише для out-параметра\nзвільняє попереднє значення\nперед тим, як покласти нове",
         GEN, NEG),
    ]
    for x, name, body, fill, stroke in cols:
        p.append(text(x + 160, 58, name, size=15.5, bold=True))
        p.append(fitbox(x, 70, 320, 86, body, size=13, fill=fill, stroke=stroke, sw=1.7))

    p.append(text(W / 2, 196, "що робить присвоєння", size=15, bold=True))

    rows = [
        ("A_var v(p);", "переймає власність p — release зробить тільки v", REAL, FIELD),
        ("A_var v2(v);", "_duplicate — два незалежні власники, два release", GEN, NEG),
        ("A_ptr q = v;", "звуження без копії — власником лишається v", FILL, LINE),
        ("A_ptr r = v._retn();", "v віддає власність назовні й стає порожнім", PAD, POS),
    ]
    ry = 214
    for code, effect, fill, stroke in rows:
        p.append(fitbox(40, ry, 380, 56, code, size=14, fill=FILL, stroke=LINE, sw=1.6))
        p.append(arrow(430, ry + 28, 468, ry + 28, color=MUTED, sw=1.8))
        p.append(fitbox(478, ry, 542, 56, effect, size=13.5, fill=fill, stroke=stroke, sw=1.7))
        ry += 68

    p.append(fitbox(40, 500, 980, 66,
                    "Конструктор від сирого _ptr переймає власність, конструктор від іншого _var — дублює."
                    "\nЦі два рядки виглядають однаково, а роблять протилежне: звідси і подвійні звільнення, і витоки.",
                    size=13.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    render(os.path.join(IMG, 'var-lifecycle.svg'), W, H, *p,
           title="Посилання на об'єкт: три типи й одна власність")


# ── 9. Хто виділяє пам'ять і хто її звільняє ────────────────────────────────
def fig_cpp_ownership():
    W, H = 1080, 616
    p = []

    p.append(text(265, 62, "у клієнта — того, хто кличе", size=15, bold=True))
    p.append(text(815, 62, "у серванта — того, кого кличуть", size=15, bold=True))

    LX, RX, BW, BH = 50, 600, 430, 104

    bands = [
        (84, "in",
         "in — const char* / const S&\nпам'ять виділив клієнт\nвін же звільняє її після виклику",
         "сервант лише читає\nне звільняє нічого\nхоче зберегти — копіює сам",
         NEG, "→"),
        (224, "inout",
         "inout — char*&, S&\nрядок мусить бути зі string_alloc\nне літерал і не масив у стеку",
         "сервант може звільнити старий\nі покласти новий указник\nдовжина не обмежена вхідною",
         MUTED, "↔"),
        (364, "out і повернення",
         "out / повернення — char*&, S*&, S*\nклієнт отримує чужу пам'ять\nі мусить звільнити її сам —\nнавіть коли сервант у тому ж процесі",
         "сервант виділяє й віддає власність\nразом зі значенням\nнульовий указник повертати не можна",
         FIELD, "←"),
    ]

    for y, tag, left, right, color, kind in bands:
        p.append(fitbox(LX, y, BW, BH, left, size=13, fill=FILL, stroke=LINE, sw=1.7))
        p.append(fitbox(RX, y, BW, BH, right, size=13, fill=REAL, stroke=FIELD, sw=1.7))
        if kind == "↔":
            p.append(text(540, y + 34, tag, size=13, bold=True, color=color))
            p.append(arrow(492, y + 54, 588, y + 54, color=color, sw=2))
            p.append(arrow(588, y + 76, 492, y + 76, color=color, sw=2))
        else:
            p.append(text(540, y + 42, tag, size=13, bold=True, color=color))
            if kind == "→":
                p.append(arrow(492, y + 64, 588, y + 64, color=color, sw=2))
            else:
                p.append(arrow(588, y + 64, 492, y + 64, color=color, sw=2))

    p.append(fitbox(50, 502, 980, 84,
                    "Власність завжди рухається в бік значення: хто отримав дані змінної довжини — той і звільняє."
                    "\nКлієнт мусить звільнити повернене навіть тоді, коли сервант живе в тому самому процесі, —"
                    "\nінакше локальний і віддалений виклики поводилися б по-різному, і переїзд об'єкта ламав би код.",
                    size=13.5, fill="#fffdf3", stroke="#d8c98a", sw=1.6))

    render(os.path.join(IMG, 'cpp-ownership.svg'), W, H, *p,
           title="Хто виділяє пам'ять і хто її звільняє")


fig_call_path()
fig_wire_bytes()
fig_ior()
fig_partial_failure()
fig_mini_dump()
fig_mini_partial_read()
fig_timeline()
fig_var_lifecycle()
fig_cpp_ownership()
print("ok")
