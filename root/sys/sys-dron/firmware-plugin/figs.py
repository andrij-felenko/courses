# -*- coding: utf-8 -*-
"""Фігури до теми «Плагін прошивки: як станція ховає різницю між автопілотами»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_plugin_choice():
    """Від полів HEARTBEAT до єдиного об'єкта плагіна."""
    W, H = 1180, 700
    f = []

    # 1. Джерело — heartbeat
    f.append(fitbox(340, 50, 500, 62,
                    "HEARTBEAT від апарата\nполя autopilot та type", size=16, bold=True))
    f.append(arrow(470, 112, 300, 154))
    f.append(arrow(710, 112, 880, 154))

    # 2. Дві осі згортання
    f.append(fitbox(90, 154, 420, 96,
                    "autopilot  →  клас прошивки\nPX4  ·  ArduPilot  ·  Generic", size=15))
    f.append(fitbox(670, 154, 420, 96,
                    "type  →  клас апарата\nMultiRotor · FixedWing · VTOL\nRoverBoat · Sub · Generic", size=15))

    f.append(arrow(300, 250, 470, 300))
    f.append(arrow(880, 250, 710, 300))

    # 3. Менеджер
    f.append(fitbox(340, 300, 500, 68,
                    "FirmwarePluginManager\nfirmwarePluginForAutopilot(…)", size=16, bold=True))
    f.append(arrow(590, 368, 590, 414))

    # 4. Реєстр фабрик
    f.append(fitbox(230, 414, 720, 92,
                    "реєстр фабрик — кожна записалася сама, до main()\n"
                    "PX4FirmwarePluginFactory      APMFirmwarePluginFactory      фабрика виробника",
                    size=14, fill="#eef2f6"))

    f.append(arrow(430, 506, 300, 566))
    f.append(arrow(750, 506, 890, 566))
    f.append(text(300, 546, "фабрика знайшлася", size=13, color=MUTED))
    f.append(text(905, 546, "жодна не підійшла", size=13, color=MUTED))

    # 5. Результат
    f.append(fitbox(60, 566, 480, 104,
                    "ArduCopterFirmwarePlugin\nєдиний примірник на клас,\nспільний для всіх таких апаратів",
                    size=15, bold=True, stroke=POS, sw=2.2))
    f.append(fitbox(650, 566, 480, 104,
                    "GenericFirmwarePlugin\nтелеметрія видна,\nкерування польотом недоступне",
                    size=15))

    return render(os.path.join(OUT, 'plugin-choice.svg'), W, H, *f,
                  title="Від першого повідомлення до плагіна прошивки")


def fig_shared_instance():
    """Один плагін на багато апаратів; персональний стан — на апараті."""
    W, H = 1180, 640
    f = []

    # три апарати
    xs = [60, 430, 800]
    names = ["Vehicle  id 1", "Vehicle  id 2", "Vehicle  id 3"]
    for x, n in zip(xs, names):
        f.append(fitbox(x, 70, 320, 60, n, size=16, bold=True))
    # персональний стан під кожним
    for x in xs:
        f.append(line(x + 160, 130, x + 160, 176, dash="5,4"))
        f.append(fitbox(x, 176, 320, 84,
                        "FirmwarePluginInstanceData\nщо цей борт відповів\nна вже надіслані команди",
                        size=13, fill="#f8f4ee"))

    f.append(text(40, 332, "усі три тримають вказівник на один об'єкт",
                  size=14, color=MUTED, anchor="start"))

    # стрілки до спільного плагіна
    for x in xs:
        f.append(arrow(x + 160, 260, 590, 344))

    f.append(fitbox(250, 344, 680, 96,
                    "ArduCopterFirmwarePlugin — один примірник\n"
                    "таблиця режимів · маска вмінь · послідовності дій",
                    size=16, bold=True, stroke=POS, sw=2.2))

    f.append(arrow(590, 440, 590, 486))
    f.append(fitbox(170, 486, 840, 118,
                    "власних полів під апарат у плагіні немає — тому кожен метод бере Vehicle:\n"
                    "QStringList flightModes(Vehicle *vehicle) const;\n"
                    "bool isCapable(const Vehicle *vehicle, FirmwareCapabilities caps) const;",
                    size=14, fill="#eef2f6"))

    return render(os.path.join(OUT, 'shared-instance.svg'), W, H, *f,
                  title="Спільне знання про діалект, персональний стан на апараті")


def fig_mode_roundtrip():
    """Двобічний переклад режиму й дві таблиці поруч."""
    W, H = 1240, 720
    f = []

    # верхній ряд: показ
    f.append(fitbox(60, 62, 300, 76, "HEARTBEAT:\nbase_mode, custom_mode", size=15))
    f.append(arrow(360, 100, 452, 100))
    f.append(fitbox(452, 62, 336, 76, "таблиця плагіна\nчисло  →  ім'я", size=15,
                    bold=True, stroke=POS, sw=2.2))
    f.append(arrow(788, 100, 880, 100))
    f.append(fitbox(880, 62, 300, 76, "напис у рядку стану\n«Повернення додому»", size=15))

    # нижній ряд: вибір
    f.append(fitbox(60, 190, 300, 76, "SET_MODE у канал\nдо апарата", size=15))
    f.append(arrow(452, 228, 360, 228))
    f.append(fitbox(452, 190, 336, 76, "таблиця плагіна\nім'я  →  число", size=15,
                    bold=True, stroke=POS, sw=2.2))
    f.append(arrow(880, 228, 788, 228))
    f.append(fitbox(880, 190, 300, 76, "пілот вибрав режим\nзі списку на екрані", size=15))

    # підтвердження
    f.append(line(210, 138, 210, 190, dash="6,4"))
    f.append(text(620, 300, "підтвердження на SET_MODE не передбачено —"
                            " результат перевіряють за наступними HEARTBEAT",
                  size=14, color=MUTED))

    # дві таблиці
    f.append(fitbox(90, 356, 480, 46, "ArduCopter", size=16, bold=True, fill="#eef2f6"))
    f.append(fitbox(670, 356, 480, 46, "PX4  (мультикоптер)", size=16, bold=True, fill="#eef2f6"))

    left = [("Stabilize", "0"), ("Auto", "3"), ("Guided", "4"),
            ("RTL", "6"), ("Land", "9")]
    right = [("Manual", "0x00010000"), ("Mission", "0x04040000"), ("Hold", "0x03040000"),
             ("Return", "0x05040000"), ("Land", "0x06040000")]

    y = 416
    for (ln, lv), (rn, rv) in zip(left, right):
        f.append(fitbox(90, y, 250, 52, ln, size=15))
        f.append(fitbox(348, y, 222, 52, lv, size=15, fill="#f8f4ee"))
        f.append(fitbox(670, y, 250, 52, rn, size=15))
        f.append(fitbox(928, y, 222, 52, rv, size=15, fill="#f8f4ee"))
        y += 60

    return render(os.path.join(OUT, 'mode-roundtrip.svg'), W, H, *f,
                  title="Словник режимів працює в обидва боки")


def fig_difference_kinds():
    """П'ять родів різниці між автопілотами."""
    W, H = 1320, 660
    f = []

    cols = [(40, 300), (356, 360), (732, 548)]
    head = ["що саме різне", "приклад у плагіні", "чим озветься помилка"]
    for (x, w), t in zip(cols, head):
        f.append(fitbox(x, 60, w, 46, t, size=15, bold=True, fill="#eef2f6"))

    rows = [
        ("Ім'я й номер\nрежиму",
         "flightMode(base, custom)\nsetFlightMode(name, …)",
         "на екрані Custom:0x1f замість імені,\nабо апарат іде не в той режим"),
        ("Набір дозволених\nдій",
         "isCapable(vehicle, caps)",
         "кнопка є, а апарат мовчить —\nпілот бачить це вже в польоті"),
        ("Послідовність\nкроків дії",
         "guidedModeTakeoff(vehicle, alt)\npauseVehicle(vehicle)",
         "команда прийнята, а зльоту немає,\nбо режим був не той"),
        ("Форма самих\nповідомлень",
         "adjustIncomingMavlinkMessage()\nadjustOutgoingMavlinkMessage…()",
         "ціле 100 читається як 1120403456;\nповернений false ковтає повідомлення"),
        ("Метадані й імена\nміж версіями",
         "loadParameterMetaData()\nparamNameRemapMajorVersionMap()",
         "збережений файл параметрів\nне лягає на нову прошивку"),
    ]

    y = 122
    for what, api, cost in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], 92, what, size=15, bold=True))
        f.append(fitbox(cols[1][0], y, cols[1][1], 92, api, size=13, fill="#f8f4ee"))
        f.append(fitbox(cols[2][0], y, cols[2][1], 92, cost, size=13))
        y += 104

    return render(os.path.join(OUT, 'difference-kinds.svg'), W, H, *f,
                  title="П'ять родів різниці, які збирає плагін прошивки")


def fig_custom_plugin_seam():
    """Шлях файлу власного плагіна в бінарник — і як він звідти зникає."""
    W, H = 1300, 780
    f = []

    LX, RX, CW = 60, 700, 540
    lc, rc = LX + CW // 2, RX + CW // 2

    f.append(fitbox(LX, 50, CW, 52, "як фабрика потрапляє в реєстр",
                    size=17, bold=True, fill="#eef2f6"))
    f.append(fitbox(RX, 50, CW, 52, "як вона звідти тихо зникає",
                    size=17, bold=True, fill="#eef2f6"))

    left = [
        "custom/CMakeLists.txt\nlist(APPEND CUSTOM_SOURCES …)",
        "апстрим: target_sources(QGroundControl …)\nфайл компілюється просто в застосунок",
        "об'єктний код у виконуваному файлі\nразом з ініціалізацією глобальних об'єктів",
        "до main(): конструктор глобального об'єкта\nвписує фабрику в реєстр",
    ]
    right = [
        "add_library(sokil_plugin STATIC …)\ntarget_link_libraries(… sokil_plugin)",
        "архів об'єктних файлів — компонувальник\nбере з нього тільки потрібні",
        "на SokilFirmwarePluginFactory_instance\nне посилається жоден символ",
        "об'єктний файл у бінарник не потрапляє —\nані помилки, ані попередження",
    ]

    y = 132
    for l, r in zip(left, right):
        f.append(fitbox(LX, y, CW, 96, l, size=14))
        f.append(fitbox(RX, y, CW, 96, r, size=14))
        f.append(arrow(lc, y + 96, lc, y + 128))
        f.append(arrow(rc, y + 96, rc, y + 128))
        y += 128

    f.append(fitbox(LX, y, CW, 108,
                    "апарат із autopilot = 21\nдістає SokilFirmwarePlugin:\nрежими, вміння, дії",
                    size=15, bold=True, stroke=POS, sw=2.2))
    f.append(fitbox(RX, y, CW, 108,
                    "реєстр без нашої фабрики\nапарат дістає загальний плагін:\nсама телеметрія, кнопки мертві",
                    size=15, fill="#f8f4ee"))

    return render(os.path.join(OUT, 'custom-plugin-seam.svg'), W, H, *f,
                  title="Реєстрація тримається на об'єкті, на який ніхто не посилається")


def fig_takeoff_timeline():
    """Скільки часу блокує одне натискання кнопки зльоту."""
    W, H = 1300, 620
    f = []

    X0, X1 = 150, 1150
    span = X1 - X0                      # 5400 мс
    xa = X0 + int(span * 3900 / 5400)   # межа між зміною режиму й вмиканням моторів

    f.append(fitbox(X0, 60, xa - X0 - 6, 110,
                    "крок 3 · _setFlightModeAndValidate\n3 спроби × 13 перевірок × 100 мс\n= 3900 мс",
                    size=15, bold=True, stroke=POS, sw=2.2))
    f.append(fitbox(xa + 6, 60, X1 - xa - 6, 110,
                    "крок 4 · _armVehicleAndValidate\n15 × 100 мс\n= 1500 мс",
                    size=14, bold=True, stroke=POS, sw=2.2))

    # вісь часу
    f.append(line(X0, 214, X1, 214, sw=2))
    for ms in (1000, 2000, 3000, 4000, 5000):
        x = X0 + int(span * ms / 5400)
        f.append(line(x, 208, x, 220))
        f.append(text(x, 244, str(ms // 1000), size=13, color=MUTED))
    f.append(text((X0 + X1) // 2, 274, "секунди від натискання кнопки",
                  size=13, color=MUTED))

    # позначки миттєвих кроків
    f.append(line(X0, 220, X0, 292, dash="5,4"))
    f.append(fitbox(40, 292, 220, 82,
                    "кроки 1–2\nперевірки стану борту\nй висоти — миттєво", size=13))
    f.append(line(X1, 220, X1, 292, dash="5,4"))
    f.append(fitbox(1040, 292, 220, 82,
                    "крок 5\nMAV_CMD_NAV_TAKEOFF\nіде в канал", size=13))

    f.append(fitbox(300, 420, 700, 90,
                    "увесь цей час метод крутить цикл очікування в потоці інтерфейсу\n"
                    "й викликає processEvents() — вікно живе і приймає нові натискання",
                    size=15, fill="#f8f4ee"))
    f.append(fitbox(300, 528, 700, 56,
                    "тому guidedModeTakeoff потребує захисту від повторного входу",
                    size=15))

    return render(os.path.join(OUT, 'takeoff-timeline.svg'), W, H, *f,
                  title="Одне натискання — до 5.4 секунди в потоці інтерфейсу")


if __name__ == '__main__':
    print(fig_plugin_choice())
    print(fig_shared_instance())
    print(fig_mode_roundtrip())
    print(fig_difference_kinds())
    print(fig_custom_plugin_seam())
    print(fig_takeoff_timeline())
