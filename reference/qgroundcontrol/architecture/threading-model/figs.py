# -*- coding: utf-8 -*-
"""Фігури до теми «Модель потоків» довідника QGroundControl."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

BAND = "#eef2f6"
SOFT = "#ffffff"


# ───────────────────────────── 1. Шлях байта ─────────────────────────────────
def fig_path():
    W, H = 1200, 600
    f = []

    # смуги ниток
    f.append(rect(16, 56, 1168, 104, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(rect(16, 222, 1168, 190, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(rect(16, 470, 1168, 104, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))

    f.append(fitbox(32, 84, 140, 48, "нитка\nканалу", size=14, bold=True, fill=SOFT))
    f.append(fitbox(32, 283, 140, 68, "головна\nнитка", size=14, bold=True, fill=SOFT))
    f.append(fitbox(32, 498, 140, 48, "нитка\nвідмальовки", size=13, bold=True, fill=SOFT))

    # нитка каналу
    f.append(fitbox(200, 76, 230, 64, "readyRead у порту\n_port->readAll()", size=13, fill=SOFT))
    f.append(fitbox(470, 76, 230, 64, "emit dataReceived\n(масив байтів)", size=13, fill=SOFT))
    f.append(arrow(430, 108, 470, 108))

    # перехід межі 1
    f.append(arrow(585, 140, 585, 237))
    f.append(mtext(612, 178, ["межа ниток: подія лягає в чергу",
                              "байти копіюються, виклик асинхронний"],
                   size=12, color=MUTED, anchor="start"))

    # головна нитка, ряд A
    f.append(fitbox(430, 241, 270, 58, "SerialLink::_onDataReceived\n→ emit bytesReceived", size=12, fill=SOFT))
    f.append(fitbox(740, 241, 320, 58, "MAVLinkProtocol::receiveBytes\nmavlink_parse_char(канал, байт)", size=12, fill=SOFT))
    f.append(arrow(700, 270, 740, 270))

    # головна нитка, ряд B
    f.append(fitbox(740, 333, 320, 58, "Vehicle::_mavlinkMessageReceived\n→ запис у факти", size=12, fill=SOFT))
    f.append(fitbox(380, 333, 320, 58, "Fact::valueChanged\n→ прив'язки QML → запит кадру", size=12, fill=SOFT))
    f.append(arrow(900, 299, 900, 333))
    f.append(arrow(740, 362, 700, 362))

    # перехід межі 2
    f.append(arrow(540, 391, 540, 487))
    f.append(mtext(520, 424, ["межа ниток: коротка зустріч —",
                              "головна нитка стоїть під час синхронізації"],
                   size=12, color=MUTED, anchor="end"))

    # нитка відмальовки
    f.append(fitbox(380, 490, 320, 64, "синхронізація сцени\n(головна нитка чекає)", size=13, fill=SOFT))
    f.append(fitbox(740, 490, 320, 64, "малювання й показ кадру\n(паралельно з головною)", size=13, fill=SOFT))
    f.append(arrow(700, 522, 740, 522))

    render(os.path.join(OUT, 'byte-to-pixel.svg'), W, H, *f,
           title="Шлях байта: дві межі ниток на всьому маршруті")


# ───────────────────────────── 2. Карта ниток ────────────────────────────────
def fig_map():
    W, H = 1180, 620
    f = []

    # головна нитка
    f.append(rect(420, 110, 340, 430, fill=BAND, stroke="#98a6b4", sw=2, rx=12))
    f.append(text(590, 148, "ГОЛОВНА НИТКА", size=15, bold=True))
    chips = ["LinkManager — облік каналів",
             "MAVLinkProtocol — розбір",
             "Vehicle — стан апаратів",
             "FactSystem — факти й параметри",
             "план місії та геозона",
             "рушій QML і прив'язки"]
    y = 170
    for c in chips:
        f.append(fitbox(440, y, 300, 40, c, size=12, fill=SOFT))
        y += 50
    f.append(text(590, 500, "весь стан — тут, по черзі, без замків", size=12, color=MUTED))

    # ліві супутники
    f.append(fitbox(30, 140, 330, 90,
                    "нитки каналів — по одній на з'єднання\nволодіють портом або сокетом\nчерез межу: сирі байти",
                    size=12, fill=SOFT))
    f.append(fitbox(30, 290, 330, 90,
                    "нитка відтворення логу\nчитає файл за мітками часу\nчерез межу: ті самі сирі байти",
                    size=12, fill=SOFT))
    f.append(fitbox(30, 440, 330, 90,
                    "нитка кешу тайлів\nволодіє базою SQLite\nчерез межу: задачі й готові тайли",
                    size=12, fill=SOFT))
    f.append(arrow(360, 185, 420, 185))
    f.append(arrow(360, 335, 420, 335))
    f.append(arrow(360, 485, 420, 485))

    # праві супутники
    f.append(fitbox(820, 140, 330, 90,
                    "нитка відмальовки\nволодіє сценою й GPU\nчерез межу: копія сцени в синхронізації",
                    size=12, fill=SOFT))
    f.append(fitbox(820, 290, 330, 90,
                    "нитки GStreamer\nволодіють конвеєром відео\nчерез межу: майже нічого",
                    size=12, fill=SOFT))
    f.append(arrow(760, 185, 820, 185))
    f.append(arrow(760, 335, 820, 335))
    f.append(arrow(985, 290, 985, 234))
    f.append(text(1000, 268, "кадри", size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'thread-map.svg'), W, H, *f,
           title="Карта ниток: нитка тут володіє ресурсом, а не роботою")


# ─────────────────────── 3. Затримка проти втрати ────────────────────────────
def fig_lag_vs_loss():
    W, H = 1120, 460
    f = []

    # рядок A
    f.append(fitbox(20, 118, 250, 64, "черга подій виросла:\nголовна нитка стояла", size=13, bold=True, fill=BAND))
    f.append(text(690, 100, "головна нитка стоїть ≈300 мс", size=12, color=POS))
    f.append(rect(560, 112, 260, 76, fill="#fdecea", stroke=POS, sw=1.4, rx=8))
    f.append(line(320, 150, 1090, 150, color=LINE, sw=1.4))
    x = 340
    while x <= 1080:
        f.append(line(x, 136, x, 164, color=NEG, sw=2))
        x += 40
    f.append(text(320, 216, "жодного пакета не втрачено — після паузи покази стрибком наздоганяють поточний стан",
                  size=12, anchor="start"))

    # рядок B
    f.append(fitbox(20, 298, 250, 64, "кадри загубив канал:\nдірки в номерах", size=13, bold=True, fill=BAND))
    f.append(line(320, 330, 1090, 330, color=LINE, sw=1.4))
    gaps = {600, 640, 680, 880}
    x = 340
    while x <= 1080:
        if x in gaps:
            f.append(text(x, 322, "×", size=17, color=POS, bold=True))
        else:
            f.append(line(x, 316, x, 344, color=NEG, sw=2))
        x += 40
    f.append(text(320, 396, "у номерах послідовності дірки — лічильник втрат росте, наздоганяння не буде",
                  size=12, anchor="start"))

    render(os.path.join(OUT, 'lag-vs-loss.svg'), W, H, *f,
           title="Два схожі симптоми з різними причинами")


# ───────────────── 4. Як розв'язується тип з'єднання (вставка api) ───────────
def fig_connection():
    W, H = 1400, 600
    f = []

    f.append(fitbox(550, 46, 300, 50, "emit сигнал у нитці T",
                    size=14, bold=True, fill=SOFT))
    f.append(arrow(700, 96, 700, 122))
    f.append(fitbox(520, 122, 360, 48, "оголошений у connect() тип з'єднання",
                    size=13, fill=BAND))

    cols = [20, 370, 720, 1070]
    cx = [x + 155 for x in cols]

    f.append(line(700, 170, 700, 190))
    f.append(line(cx[0], 190, cx[3], 190))
    for c in cx:
        f.append(arrow(c, 190, c, 210))

    heads = ["Qt::AutoConnection (0)",
             "Qt::DirectConnection (1)",
             "Qt::QueuedConnection (2)",
             "Qt::BlockingQueuedConnection (3)"]
    for x, h in zip(cols, heads):
        f.append(fitbox(x, 210, 310, 46, h, size=13, bold=True, fill=SOFT))

    mid = ["порівняти нитку отримувача\nз ниткою, що ВИПУСТИЛА сигнал;\nрішення — на кожному emit",
           "звичайний виклик по стеку\nв нитці, що випустила сигнал;\nвідправник чекає завершення",
           "аргументи копіюються в подію,\nподія лягає в чергу отримувача;\nвідправник вертається одразу",
           "подія лягає в чергу отримувача,\nвідправник СТОЇТЬ,\nпоки обробник не завершиться"]
    for x, c, m in zip(cols, cx, mid):
        f.append(arrow(c, 256, c, 290))
        f.append(fitbox(x, 290, 310, 96, m, size=12, fill=SOFT))

    tail = ["нитки збіглися → як Direct,\nрізні → як Queued;\nвласного механізму не має",
            "через межу — це чужа нитка\nв даних отримувача,\nі Qt не скаржиться взагалі",
            "потрібен цикл подій у отримувача;\nтипи аргументів — зареєстровані\nв метасистемі Qt",
            "отримувач у тій самій нитці —\nдедлок; Qt друкує попередження\nі все одно блокується"]
    for x, c, t in zip(cols, cx, tail):
        f.append(arrow(c, 386, c, 420))
        f.append(fitbox(x, 420, 310, 100, t, size=12, fill=BAND))

    f.append(text(700, 562,
                  "Нитку обробника визначає ОТРИМУВАЧ — той, хто випустив сигнал, на неї не впливає.",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'connection-resolution.svg'), W, H, *f,
           title="Хто вирішує, у якій нитці виконається обробник")


# ───────────── Порядок згортання каналу (до вставки proj-link-worker) ────────
def fig_shutdown():
    W, H = 1160, 600
    f = []

    f.append(text(120, 54, "нитка", size=13, bold=True))
    f.append(text(490, 54, "крок згортання", size=13, bold=True))
    f.append(text(955, 54, "що станеться, якщо пропустити", size=13, bold=True))

    rows = [
        ("ГОЛОВНА",
         "1 · invokeMethod(_worker, \"closeSocket\",\nQt::BlockingQueuedConnection)",
         "робітник читатиме сокет,\nякого вже нема"),
        ("РОБІТНИК",
         "2 · closeSocket(): socket->close(), delete socket\nресурс віддано там само, де відкритий",
         "дескриптор лишається відкритим,\nпорт зайнято до кінця процесу"),
        ("ГОЛОВНА",
         "3 · _thread->quit() — цикл подій виходить з exec()",
         "нитка крутиться далі,\nа wait() ніколи не поверне true"),
        ("РОБІТНИК",
         "4 · finished → deleteLater(_worker):\nоб'єкт гине у своїй нитці",
         "витік або знищення об'єкта\nз чужої нитки"),
        ("ГОЛОВНА",
         "5 · _thread->wait(2000) — чекаємо на зупинку",
         "знищення живого QThread —\nгарантована аварія"),
    ]

    y = 66
    for who, step, risk in rows:
        chip = "#e8eef8" if who == "ГОЛОВНА" else "#eef6ec"
        f.append(fitbox(40, y, 160, 62, who, size=12, bold=True, fill=chip))
        f.append(fitbox(220, y, 540, 62, step, size=12, fill=SOFT))
        f.append(fitbox(790, y, 330, 62, risk, size=11, fill=BAND))
        if y < 400:
            f.append(arrow(490, y + 62, 490, y + 84))
        y += 84

    f.append(fitbox(40, 494, 1080, 76,
                    "Єдиний блокувальний перехід у всій схемі — крок 1, і тільки в бік робітника.\n"
                    "Якщо робітник у цю саму мить блокувально покличе головну нитку,\n"
                    "обидві чекатимуть одна одну назавжди.",
                    size=12.5, fill="#fdecea"))

    render(os.path.join(OUT, 'shutdown-order.svg'), W, H, *f,
           title="Згортання каналу: п'ять кроків у жорсткому порядку")


# ──────── Що саме міряє кожен лічильник (до вставки proj-link-worker) ────────
def fig_probes():
    W, H = 1180, 580
    f = []

    # смуга робітника
    f.append(rect(30, 58, 1120, 112, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(fitbox(46, 80, 150, 68, "нитка\nканалу", size=13, bold=True, fill=SOFT))
    f.append(fitbox(230, 78, 290, 72,
                    "читання пачки з сокета\nstamp = monoNs()", size=12, fill=SOFT))
    f.append(fitbox(560, 78, 250, 72,
                    "emitted++\nemit chunkReceived", size=12, fill=SOFT))
    f.append(arrow(524, 114, 556, 114))
    f.append(mtext(980, 106, ["робітник нікого не чекає —", "одразу читає далі"],
                   size=12, color=MUTED))

    # смуга черги
    f.append(rect(30, 190, 1120, 126, fill="#fdf6e8", stroke="#d9c58f", sw=1.2, rx=10))
    f.append(fitbox(46, 214, 150, 78, "черга\nголовної\nнитки", size=12, bold=True, fill=SOFT))
    f.append(fitbox(230, 208, 420, 50, "residence = monoNs() − stamp", size=13, fill=SOFT))
    f.append(fitbox(690, 208, 420, 50, "inFlight = emitted − delivered", size=13, fill=SOFT))
    f.append(text(440, 288, "скільки цей шматок пролежав у черзі", size=12, color=MUTED))
    f.append(text(900, 288, "скільки таких лежить просто зараз", size=12, color=MUTED))

    # смуга циклу подій
    f.append(rect(30, 336, 1120, 156, fill=BAND, stroke="#c8d2dc", sw=1.2, rx=10))
    f.append(fitbox(46, 378, 150, 72, "цикл подій\nголовної\nнитки", size=12, bold=True, fill=SOFT))
    f.append(rect(230, 380, 130, 34, fill=SOFT, stroke=LINE, sw=1.2, rx=4))
    f.append(text(295, 402, "чекає", size=12))
    f.append(rect(360, 380, 430, 34, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    f.append(text(575, 402, "прогін: події одна за одною", size=12))
    f.append(rect(790, 380, 120, 34, fill=SOFT, stroke=LINE, sw=1.2, rx=4))
    f.append(text(850, 402, "чекає", size=12))
    f.append(rect(910, 380, 200, 34, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    f.append(text(1010, 402, "прогін", size=12))
    f.append(text(364, 370, "awake", size=11, color=MUTED, anchor="start"))
    f.append(text(786, 370, "aboutToBlock", size=11, color=MUTED, anchor="end"))
    f.append(line(360, 432, 790, 432, color=POS, sw=1.6))
    f.append(line(360, 426, 360, 438, color=POS, sw=1.6))
    f.append(line(790, 426, 790, 438, color=POS, sw=1.6))
    f.append(text(575, 456, "longestBusy — найдовший безперервний прогін", size=12))
    f.append(text(575, 478, "усе це в головній нитці, тому лічильники тут звичайні, без атомарних",
                  size=11.5, color=MUTED))

    f.append(fitbox(30, 508, 1120, 58,
                    "inFlight росте разом із longestBusy → стала головна нитка.\n"
                    "inFlight ≈ 0, residence мала, а свіжих даних нема → мовчить канал.",
                    size=12.5, fill="#eef7ee"))

    render(os.path.join(OUT, 'probe-anatomy.svg'), W, H, *f,
           title="Три числа й три різні проміжки, які вони міряють")


fig_path()
fig_map()
fig_lag_vs_loss()
fig_connection()
fig_shutdown()
fig_probes()
print("ok")
