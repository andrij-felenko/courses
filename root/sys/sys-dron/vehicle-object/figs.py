# -*- coding: utf-8 -*-
"""Фігури до теми «Vehicle: модель апарата всередині застосунку»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def tb(cx, cy, s, **kw):
    return textbox(cx, cy, s, **kw)[0]


# ─────────────────────────────────────────────────────────────────────────────
# 1. Шлях одного повідомлення: від байтів у порту до сигналу зміни
# ─────────────────────────────────────────────────────────────────────────────
def fig_message_path():
    W, H = 1080, 760
    f = []

    # ліва колонка — те, що відбувається ПОЗА Vehicle
    left_x = 175
    stages = [
        (110, "Робоча нитка порту\nчитає байти"),
        (200, "LinkInterface\nbytesReceived(link, data)"),
        (295, "MAVLinkProtocol\nбайти → mavlink_message_t"),
        (390, "сигнал messageReceived\n(link, message)"),
    ]
    for y, s in stages:
        f.append(tb(left_x, y, s, size=13))
    for i in range(len(stages) - 1):
        y1 = stages[i][0] + 26
        y2 = stages[i + 1][0] - 26
        f.append(arrow(left_x, y1, left_x, y2))

    # права рамка — сам Vehicle
    bx, by, bw, bh = 350, 60, 690, 620
    f.append(rect(bx, by, bw, bh, fill="#ffffff", sw=2.0, rx=10))
    f.append(text(bx + bw / 2, by + 34, "Vehicle — один об'єкт на апарат (sysid = 1)",
                  size=15, bold=True))

    steps = [
        "1. фільтр: message.sysid == 1",
        "2. VehicleLinkManager: облік каналів і heartbeat",
        "3. лічильники: втрати пакетів за message.seq",
        "4. FirmwarePlugin::adjustIncomingMavlinkMessage",
        "5. QGCCorePlugin::mavlinkMessage — вендорський гак",
        "6. менеджери: параметри, FTP, місія, Remote ID",
        "7. усі FactGroup::handleMessage",
        "8. власний switch: HEARTBEAT, GLOBAL_POSITION_INT…",
    ]
    sx = bx + bw / 2
    y0, step = 160, 66
    for i, s in enumerate(steps):
        f.append(tb(sx, y0 + i * step, s, size=13, min_w=430))
    for i in range(len(steps) - 1):
        f.append(arrow(sx, y0 + i * step + 18, sx, y0 + (i + 1) * step - 18))

    # вхід у Vehicle
    f.append(arrow(left_x + 130, 390, bx - 8, 390))

    # вихід на екран
    f.append(arrow(sx, by + bh + 4, sx, 700))
    f.append(tb(sx, 726, "Fact / Q_PROPERTY → сигнал зміни → прив'язка на екрані",
                size=13, fill="#eef6ef", stroke=FIELD, bold=True))

    render(os.path.join(IMG, 'message-path.svg'), W, H, *f,
           title="Шлях одного повідомлення до екрана")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Три шари всередині Vehicle
# ─────────────────────────────────────────────────────────────────────────────
def fig_anatomy():
    W, H = 1080, 500
    f = []

    panels = [
        (40, "Власний стан", "#eef4fb", NEG, [
            "Vehicle сам є FactGroup:",
            "roll · pitch · heading",
            "altitudeRelative · altitudeAMSL",
            "groundSpeed · climbRate",
            "distanceToHome · timeToHome",
            "",
            "плюс ~19 вкладених груп:",
            "gps · battery · wind · vibration",
            "esc · terrain · efi · generator",
        ]),
        (390, "Протокольні менеджери", "#fbf4ee", POS, [
            "ParameterManager",
            "MissionManager",
            "GeoFenceManager",
            "RallyPointManager",
            "VehicleLinkManager",
            "ComponentInformationManager",
            "FTPManager · RemoteIDManager",
            "MavCommandQueue",
            "InitialConnectStateMachine",
        ]),
        (740, "Змінна частина", "#eef6ef", FIELD, [
            "FirmwarePlugin — різниця прошивок:",
            "назви режимів польоту",
            "правки вхідних повідомлень",
            "зліт · посадка · повернення",
            "",
            "AutoPilotPlugin — склад",
            "екрана налаштувань",
            "",
            "QGCCorePlugin — вендорські гаки",
        ]),
    ]

    pw, py, ph = 300, 70, 400
    for px, title, fill, stroke, items in panels:
        f.append(rect(px, py, pw, ph, fill=fill, stroke=stroke, sw=2.0, rx=10))
        f.append(text(px + pw / 2, py + 32, title, size=15, bold=True, color=stroke))
        y = py + 74
        for it in items:
            if it:
                fs = fit_font(it, pw - 24, 13)
                f.append(text(px + pw / 2, y, it, size=fs, color=INK))
            y += 34

    render(os.path.join(IMG, 'vehicle-anatomy.svg'), W, H, *f,
           title="Що тримає в собі Vehicle")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Стримування потоку сигналів: 50 Гц на вході, 10 Гц на виході
# ─────────────────────────────────────────────────────────────────────────────
def fig_throttle():
    W, H = 1020, 440
    f = []

    x0, x1 = 110, 910          # 0…400 мс, 2 px на мілісекунду
    px_per_ms = (x1 - x0) / 400.0

    # верхня вісь — повідомлення
    y_top = 130
    f.append(text(x0, y_top - 44, "ATTITUDE приходить кожні 20 мс — 50 разів на секунду",
                  size=14, anchor="start", bold=True))
    f.append(line(x0, y_top, x1, y_top, color=MUTED, sw=1.5))
    for ms in range(0, 401, 20):
        x = x0 + ms * px_per_ms
        f.append(line(x, y_top - 16, x, y_top, color=NEG, sw=2.5))

    # нижня вісь — сигнали
    y_bot = 330
    f.append(line(x0, y_bot, x1, y_bot, color=MUTED, sw=1.5))
    for ms in range(0, 401, 100):
        x = x0 + ms * px_per_ms
        f.append(line(x, y_bot, x, y_bot + 16, color=POS, sw=2.5))
    for ms in range(0, 401, 100):
        x = x0 + ms * px_per_ms
        f.append(text(x, y_bot + 40, "%d мс" % ms, size=12, color=MUTED))
    f.append(text(x0, y_bot + 78, "valueChanged — раз на 100 мс, за таймером FactGroup",
                  size=14, anchor="start", bold=True))

    # середина — механізм
    f.append(tb(W / 2, 230,
                "Fact::setRawValue оновлює значення щоразу,\n"
                "а сигнал лише зводить прапорець _deferredValueChangeSignal;\n"
                "таймер групи раз на 100 мс висилає відкладені сигнали",
                size=13, fill="#fffbea", stroke="#b8860b"))

    render(os.path.join(IMG, 'fact-throttle.svg'), W, H, *f,
           title="Чому екран не захлинається телеметрією")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Життєвий цикл: народження, дорослішання, смерть
# ─────────────────────────────────────────────────────────────────────────────
def fig_lifecycle():
    W, H = 1120, 470
    f = []

    # народження
    f.append(tb(190, 92, "HEARTBEAT від невідомого sysid", size=13))
    f.append(tb(560, 92, "перевірки: compid, тип, sysid ≠ 0", size=13))
    f.append(tb(920, 92, "new Vehicle(link, sysid, …)", size=13))
    f.append(arrow(330, 92, 415, 92))
    f.append(arrow(707, 92, 792, 92))

    # дорослішання
    f.append(text(W / 2, 172, "InitialConnectStateMachine — вісім станів, кожен із таймаутом",
                  size=13, bold=True, color=MUTED))
    states = ["версія\nавтопілота", "стандартні\nрежими", "інформація\nпро вузли",
              "параметри", "місія", "геозона", "точки\nзбору", "готово"]
    n = len(states)
    m, gap = 40, 14
    bwid = (W - 2 * m - gap * (n - 1)) / n
    ytop, bhh = 196, 62
    for i, s in enumerate(states):
        x = m + i * (bwid + gap)
        col = "#eef6ef" if i == n - 1 else FILL
        f.append(fitbox(x, ytop, bwid, bhh, s, size=13, fill=col,
                        stroke=FIELD if i == n - 1 else LINE))
        if i < n - 1:
            f.append(arrow(x + bwid + 1, ytop + bhh / 2, x + bwid + gap - 1, ytop + bhh / 2))
    f.append(arrow(920, 118, 920, 190))

    # смерть
    f.append(tb(300, 390, "3.5 с без heartbeat на каналі →\nзв'язок утрачено", size=13,
                fill="#fbeeee", stroke=POS))
    f.append(tb(830, 390, "зник останній канал →\nvehicleRemoved, об'єкт гине", size=13,
                fill="#fbeeee", stroke=POS))
    f.append(arrow(300, 268, 300, 356))
    f.append(arrow(430, 390, 690, 390))

    render(os.path.join(IMG, 'vehicle-lifecycle.svg'), W, H, *f,
           title="Життєвий цикл об'єкта Vehicle")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Вставка proj: дорога нового значення і місця, де воно тихо зникає
# ─────────────────────────────────────────────────────────────────────────────
def fig_new_fact_seams():
    W, H = 1140, 780
    f = []

    f.append(text(300, 62, "дорога нового значення", size=15, bold=True))
    f.append(text(845, 62, "де воно тихо зникає", size=15, bold=True, color=POS))

    road = [
        (115, "WINCH_STATUS від борту\nline_length = 12.4 (float, метри)"),
        (230, "_handleWinchStatus:\nmavlink_msg_winch_status_decode(...)"),
        (345, "lineLength()->setRawValue(12.4)"),
        (460, "метадані з WinchFact.json:\nunits «m» · decimalPlaces 2"),
        (575, "таймер групи: раз на 1000 мс —\nvalueChanged"),
        (690, "QML: winch.lineLength.valueString\n«12.40» плюс units «m» або «ft»"),
    ]
    for y, s in road:
        f.append(tb(300, y, s, size=13, min_w=430))
    for i in range(len(road) - 1):
        f.append(arrow(300, road[i][0] + 32, 300, road[i + 1][0] - 32))

    notes = [
        (115, "Борт не шле WINCH_STATUS — і жодного сліду ніде.\n"
              "Попросити: MAV_CMD_SET_MESSAGE_INTERVAL"),
        (365, "Ім'я факту не збіглося з ключем «name» у JSON:\n"
              "метадані не приліпилися, попередження НЕМАЄ —\n"
              "число без одиниць і з довгим хвостом"),
        (485, "Файл JSON не внесено в JSON_FILES:\n"
              "«Internal Error» у журналі — і вся група\n"
              "лишилася без метаданих"),
        (605, "Період 0 замість 1000 — сигнал на кожен кадр;\n"
              "потрібна кожна зміна — setLiveUpdates(true)"),
        (715, "Ім'я групи або перша літера факту розійшлися:\n"
              "«Unknown Fact» у журналі, порожнє поле на екрані"),
    ]
    for y, s in notes:
        f.append(tb(845, y, s, size=12, min_w=470, fill="#fbeeee", stroke=POS))

    for y1, y2 in ((115, 115), (365, 365), (475, 485), (590, 605), (700, 715)):
        f.append(arrow(520, y1, 604, y2, color=POS))

    render(os.path.join(IMG, 'new-fact-seams.svg'), W, H, *f,
           title="Дорога нового значення й місця мовчазної втрати")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Вставка proj: два місця, де можна зареєструвати власну групу фактів
# ─────────────────────────────────────────────────────────────────────────────
def fig_registration_routes():
    W, H = 1140, 570
    f = []

    panels = [
        (40, "Правка Vehicle", "#eef4fb", NEG, [
            "Vehicle.h — член _winchFactGroup",
            "Vehicle.h — Q_PROPERTY winch",
            "Vehicle.h — рядок «winch» у полях імен",
            "Vehicle.cc — new + _addFactGroup",
            "",
            "З екрана: _activeVehicle.winch.lineLength",
            "",
            "Ціна: чотири правки в чужих файлах,",
            "конфлікт при кожному оновленні апстриму",
            "Доречно: повідомлення СПІЛЬНОГО набору,",
            "зміна піде в апстрим",
        ]),
        (620, "FirmwarePlugin::factGroups()", "#eef6ef", FIELD, [
            "свій плагін прошивки повертає карту",
            "{ «winch» → примірник групи }",
            "Vehicle сам покличе _addFactGroup",
            "у файлах апстриму — жодної правки",
            "",
            "З екрана: getFactGroup(«winch»)",
            "",
            "Ціна: Q_PROPERTY немає,",
            "звертання лише за іменем",
            "Доречно: повідомлення свого діалекту,",
            "власна збірка",
        ]),
    ]

    pw, py, ph = 480, 60, 400
    for px, title, fill, stroke, items in panels:
        f.append(rect(px, py, pw, ph, fill=fill, stroke=stroke, sw=2.0, rx=10))
        f.append(text(px + pw / 2, py + 30, title, size=15, bold=True, color=stroke))
        y = py + 66
        for it in items:
            if it:
                fs = fit_font(it, pw - 28, 13)
                f.append(text(px + pw / 2, y, it, size=fs, color=INK))
            y += 30

    f.append(tb(W / 2, 520,
                "У панелі значень група з'явиться однаково за обома шляхами:\n"
                "список будується з factGroupNames(), а не з переліку в коді екрана",
                size=13, fill="#fffbea", stroke="#b8860b"))
    f.append(arrow(280, 464, 470, 494, color=MUTED))
    f.append(arrow(860, 464, 670, 494, color=MUTED))

    render(os.path.join(IMG, 'factgroup-registration.svg'), W, H, *f,
           title="Два місця реєстрації власної групи фактів")


if __name__ == '__main__':
    fig_message_path()
    fig_anatomy()
    fig_throttle()
    fig_lifecycle()
    fig_new_fact_seams()
    fig_registration_routes()
    print("ok")
