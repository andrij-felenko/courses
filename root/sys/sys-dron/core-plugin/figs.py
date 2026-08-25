# -*- coding: utf-8 -*-
"""Фігури до теми «Ядрове розширення: головна точка кастомізації»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_substitution():
    W, H = 1040, 500
    f = []
    # спільне тіло застосунку
    f.append(fitbox(170, 52, 700, 60,
                    "Тіло застосунку: усі рішення йдуть через\nQGCCorePlugin::instance()->…",
                    size=17, bold=True))
    f.append(arrow(520, 112, 520, 150))
    # розгалуження часу збірки
    f.append(line(270, 150, 770, 150))
    f.append(text(255, 143, "розвилка на час збірки", size=13, color=MUTED, anchor="end"))
    f.append(arrow(270, 150, 270, 196))
    f.append(arrow(770, 150, 770, 196))

    f.append(fitbox(120, 196, 300, 62,
                    "теки custom/ немає\n(типова збірка)", size=15))
    f.append(fitbox(620, 196, 300, 62,
                    "є тека custom/ →\nQGC_CUSTOM_BUILD", size=15))
    f.append(arrow(270, 258, 270, 300))
    f.append(arrow(770, 258, 770, 300))

    f.append(fitbox(120, 300, 300, 92,
                    "QGCCorePlugin\nтипові відповіді\nна всі запитання", size=15, bold=True))
    f.append(fitbox(620, 300, 300, 92,
                    "CustomPlugin : QGCCorePlugin\nперевизначає лічені\nметоди", size=15,
                    bold=True, stroke=POS, sw=2.2))

    # повернення до типових
    f.append(line(770, 392, 770, 428, dash="6,4"))
    f.append(line(770, 428, 300, 428, dash="6,4"))
    f.append(arrow(300, 428, 270, 400))
    f.append(text(520, 462, "неперевизначене падає в базовий клас", size=14, color=MUTED))
    return render(os.path.join(OUT, 'substitution.svg'), W, H, *f,
                  title="Одне місце виклику — дві збірки")


def fig_hook_kinds():
    W, H = 1120, 510
    f = []
    cols = [(50, 250), (320, 300), (650, 420)]
    head = ["рід гачка", "що дає застосунку", "приклад методу"]
    for (x, w), t in zip(cols, head):
        f.append(fitbox(x, 60, w, 44, t, size=15, bold=True, fill="#eef2f6"))

    rows = [
        ("Прапорець", "готове «так» або «ні»\nпро вигляд і дозвіл",
         "options()->showFirmwareUpgrade()\noptions()->multiVehicleEnabled()"),
        ("Фабрика", "готовий об'єкт потрібного\nтипу замість типового",
         "createVideoReceiver()\ncreateComplexMissionItem()"),
        ("Перехоплення", "право глянути на дані\nй змінити чи спинити",
         "mavlinkMessage() → bool\npreSaveToJson()"),
        ("Підміна імені", "інший файл за тим самим\nадресом ресурсу",
         "перехоплювач URL у QML-рушії\n(значки, екрани)"),
    ]
    y = 122
    for name, gives, api in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], 82, name, size=16, bold=True))
        f.append(fitbox(cols[1][0], y, cols[1][1], 82, gives, size=14))
        f.append(fitbox(cols[2][0], y, cols[2][1], 82, api, size=14, fill="#f8f4ee"))
        y += 94
    return render(os.path.join(OUT, 'hook-kinds.svg'), W, H, *f,
                  title="Чотири роди гачків ядрового розширення")


def fig_message_veto():
    W, H = 1080, 430
    f = []
    f.append(fitbox(40, 90, 190, 70, "Байти\nз каналу", size=15))
    f.append(arrow(230, 125, 272, 125))
    f.append(fitbox(272, 90, 210, 70, "Розбір MAVLink:\nповідомлення", size=15))
    f.append(arrow(482, 125, 524, 125))
    f.append(fitbox(524, 90, 210, 70, "Vehicle бере\nповідомлення", size=15))
    f.append(arrow(734, 125, 776, 125))
    f.append(fitbox(776, 90, 260, 70, "mavlinkMessage()\nу розширенні", size=15,
                    bold=True, stroke=POS, sw=2.2))

    f.append(arrow(906, 160, 906, 262))
    f.append(arrow(830, 162, 600, 262))
    f.append(fitbox(400, 262, 300, 96,
                    "false —\nстандартні обробники\nцього не побачать", size=14, stroke=POS))
    f.append(fitbox(756, 262, 300, 96,
                    "true —\nпараметри, місія,\nтелеметрія як завжди", size=14))
    return render(os.path.join(OUT, 'message-veto.svg'), W, H, *f,
                  title="Гачок на потоці повідомлень апарата")


def fig_build_wiring():
    W, H = 1200, 640
    f = []
    LX, LW = 40, 470
    RX, RW = 690, 470

    f.append(fitbox(LX, 52, LW, 46, "тека custom/ — пишемо ми", size=16, bold=True,
                    fill="#eef2f6"))
    f.append(fitbox(RX, 52, RW, 46, "апстрим — не чіпаємо жодного рядка", size=16,
                    bold=True, fill="#eef2f6"))

    rows = [
        (128,
         "custom/cmake/CustomOverrides.cmake\nset(QGC_APP_NAME \"SkyLark GCS\" … FORCE)",
         "кореневий CMakeLists.txt\nproject(${QGC_APP_NAME} …)",
         "до project()"),
        (256,
         "custom/CMakeLists.txt\nset(CUSTOM_DEFINITIONS\n  QGC_CUSTOM_BUILD  CUSTOMHEADER=…  CUSTOMCLASS=…\n  CACHE INTERNAL)",
         "src/CMakeLists.txt\ntarget_compile_definitions(\n  ${CMAKE_PROJECT_NAME} PRIVATE\n  ${CUSTOM_DEFINITIONS})",
         "через кеш"),
        (384,
         "set(CUSTOM_SOURCES … CACHE INTERNAL)\nset(QGC_RESOURCES … custom.qrc … FORCE)",
         "target_sources(…)\nресурси застосунку",
         "через кеш"),
    ]
    for y, left, right, mark in rows:
        f.append(fitbox(LX, y, LW, 104, left, size=14))
        f.append(fitbox(RX, y, RW, 104, right, size=14))
        f.append(arrow(LX + LW + 12, y + 52, RX - 12, y + 52))
        f.append(text((LX + LW + RX) / 2, y + 40, mark, size=13, color=MUTED))

    f.append(fitbox(180, 520, 840, 92,
                    "src/API/QGCCorePlugin.cc після препроцесора:\n"
                    "#include \"CustomPlugin.h\"      return CustomPlugin::instance();",
                    size=15, bold=True, stroke=POS, sw=2.2, fill="#f8f4ee"))
    f.append(arrow(RX + RW / 2, 488, 700, 520))
    return render(os.path.join(OUT, 'build-wiring.svg'), W, H, *f,
                  title="Куди потрапляє кожне ім'я з теки власної збірки")


def fig_resource_path():
    W, H = 1200, 600
    f = []
    BX, BW = 100, 1000

    f.append(fitbox(BX, 52, BW, 76,
                    "екран просить ресурс за звичайною адресою\n"
                    "qrc:/qml/QGroundControl/FlyView/FlyViewCustomLayer.qml", size=15))
    f.append(arrow(BX + BW / 2, 128, BX + BW / 2, 172))

    f.append(fitbox(BX, 172, BW, 86,
                    "перехоплювач адрес: вставити /Custom одразу після схеми\n"
                    ":/Custom/qml/QGroundControl/FlyView/FlyViewCustomLayer.qml",
                    size=15, bold=True, stroke=POS, sw=2.2))
    f.append(arrow(BX + BW / 2, 258, BX + BW / 2, 302))

    f.append(fitbox(400, 302, 400, 62,
                    "QFile::exists(нова адреса) ?", size=16, bold=True, fill="#eef2f6"))
    f.append(arrow(500, 364, 320, 424))
    f.append(arrow(700, 364, 880, 424))
    f.append(text(370, 402, "так", size=14, color=MUTED))
    f.append(text(830, 402, "ні", size=14, color=MUTED))

    f.append(fitbox(60, 424, 520, 110,
                    "у custom.qrc є псевдонім із цим самим іменем —\n"
                    "віддаємо власну копію, апстримовий файл\n"
                    "лишається в бінарнику незайманим", size=14, stroke=POS))
    f.append(fitbox(620, 424, 520, 110,
                    "власної копії немає —\n"
                    "віддаємо адресу без змін,\n"
                    "завантажиться стандартний екран", size=14))
    return render(os.path.join(OUT, 'resource-path.svg'), W, H, *f,
                  title="Шлях адреси ресурсу крізь перехоплювач")


if __name__ == '__main__':
    print(fig_substitution())
    print(fig_hook_kinds())
    print(fig_message_veto())
    print(fig_build_wiring())
    print(fig_resource_path())
