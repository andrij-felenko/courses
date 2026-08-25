# -*- coding: utf-8 -*-
"""Фігури до теми «Цілі платформ: Linux, Windows, Android»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Одне дерево — три артефакти ─────────────────────────────────────────
def fig_three_artifacts():
    W, H = 1320, 880
    LABW, COLW, GAP = 250, 320, 24
    X0 = 30
    CX = [X0 + LABW + GAP + i * (COLW + GAP) for i in range(3)]
    frags = []

    # спільне дерево зверху
    top_y, top_h = 62, 54
    frags.append(fitbox(X0, top_y, W - 2 * X0, top_h,
                        "Спільне дерево джерел: один тег, один src/, один CMakeLists.txt",
                        size=17, bold=True, fill="#eef4ff", stroke=NEG))

    head_y, head_h = 136, 44
    heads = ["Linux", "Windows", "Android"]
    for i, hname in enumerate(heads):
        frags.append(fitbox(CX[i], head_y, COLW, head_h, hname, size=17, bold=True,
                            fill="#f0f0f0", stroke=INK))
        frags.append(arrow(CX[i] + COLW / 2, top_y + top_h + 4, CX[i] + COLW / 2, head_y - 6))

    rows = [
        ("Тулчейн",
         "gcc, рідна збірка\nx86-64 або aarch64",
         "MSVC 2022, рідна збірка\nx64 або ARM64",
         "NDK r27c (clang), крос-збірка\nчотири ABI окремо"),
        ("Платформний модуль",
         "cmake/platform/Linux.cmake\n_GNU_SOURCE, RPATH $ORIGIN",
         "Windows.cmake\nNOMINMAX, /bigobj, .rc",
         "Android.cmake\nSDK, дозволи, версійний код"),
        ("Послідовний порт",
         "вузол /dev/ttyUSB0\nправа через групу dialout",
         "COM-порт\nдрайвер за VID/PID",
         "USB host через Java\nдіалог дозволу в користувача"),
        ("GStreamer",
         "пакети дистрибутива\nva, vulkan, qsv",
         "готовий архів + sha256\nd3d11, nvcodec",
         "готовий архів + sha256\nandroidmedia"),
        ("Пакування",
         "linuxdeploy + appimagetool",
         "makensis (NSIS)",
         "androiddeployqt + gradle"),
        ("Артефакт",
         "QGroundControl-x86_64\n.AppImage",
         "QGroundControl-\ninstaller-AMD64.exe",
         "QGroundControl.apk"),
    ]

    y = head_y + head_h + 26
    rh, rgap = 88, 18
    for name, a, b, c in rows:
        frags.append(fitbox(X0, y, LABW, rh, name, size=16, bold=True,
                            fill="#ffffff", stroke=MUTED))
        for i, cell in enumerate((a, b, c)):
            frags.append(fitbox(CX[i], y, COLW, rh, cell, size=14, pad=12))
        y += rh + rgap

    frags.append(text(W / 2, y + 14,
                      "спільним лишається все, крім шести рядків цієї таблиці",
                      size=15, color=MUTED, italic=True))
    render(os.path.join(OUT, 'three-artifacts.svg'), W, H, *frags)


# ── 2. Три шляхи до послідовного порту ─────────────────────────────────────
def fig_serial_paths():
    W, H = 1240, 820
    COLW, GAP = 350, 40
    X0 = 40
    CX = [X0 + i * (COLW + GAP) for i in range(3)]
    frags = []

    top_y, top_h = 56, 58
    frags.append(fitbox(X0, top_y, W - 2 * X0, top_h,
                        "SerialLink викликає QSerialPort — той самий код на всіх платформах",
                        size=17, bold=True, fill="#eef7ee", stroke=FIELD))

    chains = [
        ("Linux", [
            "реалізація QSerialPort\nдля Linux",
            "вузол /dev/ttyUSB0\nправа: група dialout",
            "драйвер ядра\nftdi_sio, cdc_acm",
        ]),
        ("Windows", [
            "реалізація QSerialPort\nдля Windows",
            "ім'я \\\\.\\COM7\nдрайвер за VID/PID",
            "драйвер виробника\nв просторі ядра",
        ]),
        ("Android", [
            "підмінена реалізація\nsrc/Android/qtandroidserialport",
            "AndroidSerial\nміст JNI до Java",
            "QGCUsbSerialManager.java\nдозвіл питають у користувача",
            "Android USB host API\nдоступ до пристрою без вузла /dev",
            "драйвер ядра Linux\nсхований від застосунку",
        ]),
    ]

    bh, bgap = 76, 20
    y_start = top_y + top_h + 46
    bottoms = []
    for i, (name, boxes) in enumerate(chains):
        frags.append(fitbox(CX[i], y_start - 46, COLW, 36, name, size=16, bold=True,
                            fill="#f0f0f0", stroke=INK))
        frags.append(arrow(CX[i] + COLW / 2, top_y + top_h + 4, CX[i] + COLW / 2, y_start - 50))
        y = y_start
        fill = "#fdf3ec" if name == "Android" else FILL
        for b in boxes:
            frags.append(fitbox(CX[i], y, COLW, bh, b, size=14, pad=10, fill=fill))
            y += bh
            if b is not boxes[-1]:
                frags.append(arrow(CX[i] + COLW / 2, y + 2, CX[i] + COLW / 2, y + bgap - 2))
                y += bgap
        bottoms.append(y)

    bar_y = max(bottoms) + 52
    frags.append(fitbox(X0, bar_y, W - 2 * X0, 54,
                        "той самий радіомодем на USB",
                        size=16, bold=True, fill="#eef4ff", stroke=NEG))
    for i in range(3):
        frags.append(arrow(CX[i] + COLW / 2, bottoms[i] + 4, CX[i] + COLW / 2, bar_y - 6))

    render(os.path.join(OUT, 'serial-paths.svg'), W, H, *frags)


# ── 3. Версійний код пакета Android ────────────────────────────────────────
def fig_version_code():
    W, H = 1180, 560
    frags = []

    fields = [
        ("BB", "розрядність\n66 або 34", 170),
        ("M", "старший\nномер", 110),
        ("I", "молодший\nномер", 110),
        ("PP", "латка", 130),
        ("DDD", "номер\nзбірки", 170),
    ]
    total = sum(f[2] for f in fields) + 4 * 16
    x = (W - total) / 2
    top = 130
    xs = []
    for code, cap, w in fields:
        frags.append(fitbox(x, top, w, 62, code, size=22, bold=True,
                            fill="#eef4ff", stroke=NEG))
        frags.append(fitbox(x, top + 74, w, 62, cap, size=13, pad=8,
                            fill="#ffffff", stroke=MUTED))
        xs.append((x, w))
        x += w + 16

    frags.append(text(W / 2, 70, "Версійний код збірки: дев'ять десяткових розрядів",
                      size=18, bold=True))

    rows = [
        ("arm64-v8a", ["66", "5", "0", "03", "007"], "665003007"),
        ("armeabi-v7a", ["34", "5", "0", "03", "007"], "345003007"),
    ]
    y = top + 176
    for name, parts, whole in rows:
        frags.append(fitbox(20, y, 180, 58, name, size=15, bold=True,
                            fill="#f6f6f6", stroke=MUTED))
        for (bx, bw), p in zip(xs, parts):
            frags.append(fitbox(bx, y, bw, 58, p, size=20, bold=True))
        frags.append(fitbox(970, y, 195, 58, "= " + whole, size=16, bold=True,
                            fill="#eef7ee", stroke=FIELD))
        y += 78

    frags.append(text(W / 2, y + 42,
                      "34… завжди менше за 66… — 32-бітний пакет ніколи не перекриє 64-бітний",
                      size=15, color=MUTED, italic=True))
    render(os.path.join(OUT, 'version-code.svg'), W, H, *frags)


# ── 4. Два напрямки мосту JNI (вставка proj-android-serial-bridge) ─────────
def fig_jni_two_directions():
    W, H = 1300, 900
    COLW, GAP = 560, 60
    X0 = 60
    CX = [X0, X0 + COLW + GAP]
    CPP = "#eaf0fd"   # боки C++
    JAV = "#fdf1e4"   # боки Java
    frags = []

    frags.append(text(W / 2, 44, "Міст JNI працює у два боки — і в кожному свій потік",
                      size=19, bold=True))

    heads = ["Униз: C++ кличе Java  (запис у порт)",
             "Угору: Java кличе C++  (прихід байтів)"]
    head_y, head_h = 72, 46
    for i, hname in enumerate(heads):
        frags.append(fitbox(CX[i], head_y, COLW, head_h, hname, size=16, bold=True,
                            fill="#f0f0f0", stroke=INK))

    chains = [
        [("потік лінка (QThread)\nSerialLink → QSerialPort::write()", CPP),
         ("QJniEnvironment\nприєднує цей потік до віртуальної машини\nі дає власний JNIEnv*", CPP),
         ("CallStaticIntMethod\nза кешованим jmethodID і глобальним jclass", CPP),
         ("QGCUsbSerialManager.write(id, data, len, timeout)\nUsbSerialPort → USB host API", JAV),
         ("checkAndClearExceptions()\nвиняток Java не розкрутив стек — він чекає прапорцем", CPP)],
        [("читальний потік Java\nSerialInputOutputManager, пріоритет URGENT_AUDIO", JAV),
         ("onNewData(byte[])\n→ nativeDeviceNewData(token, data)", JAV),
         ("jniDeviceNewData: токен → QSerialPortPrivate\nсталий токен = об'єкт уже знищено, мовчки виходимо", CPP),
         ("копія байтів у _pendingData під мутексом\nпотік лінка сюди ще не заходив", CPP),
         ("QueuedConnection у потік-власник порту\nодин відкладений виклик на пачку, а не на пакет", CPP),
         ("злив у буфер QIODevice → emit readyRead()", CPP)],
    ]

    bh, bgap = 84, 24
    y_start = head_y + head_h + 34
    for i, boxes in enumerate(chains):
        y = y_start
        for j, (txt_, fill) in enumerate(boxes):
            frags.append(fitbox(CX[i], y, COLW, bh, txt_, size=14, pad=14, fill=fill))
            y += bh
            if j < len(boxes) - 1:
                frags.append(arrow(CX[i] + COLW / 2, y + 3, CX[i] + COLW / 2, y + bgap - 3))
                y += bgap

    leg_y = H - 66
    frags.append(fitbox(X0, leg_y, 250, 42, "боки C++", size=14, fill=CPP))
    frags.append(fitbox(X0 + 274, leg_y, 250, 42, "боки Java", size=14, fill=JAV))
    frags.append(text(CX[1] + COLW / 2, leg_y + 26,
                      "межа мов проходить усередині кожного ланцюжка",
                      size=14, color=MUTED, italic=True))
    render(os.path.join(OUT, 'jni-two-directions.svg'), W, H, *frags)


# ── 5. Два незалежні списки: device_filter і ProbeTable ────────────────────
def fig_usb_two_lists():
    W, H = 1280, 620
    LABW, CELLW, GAP = 300, 400, 26
    X0 = 40
    CX = [X0 + LABW + GAP, X0 + LABW + GAP + CELLW + GAP]
    frags = []

    frags.append(text(W / 2, 42, "Дві незалежні перевірки — і лише їх перетин дає робочий порт",
                      size=19, bold=True))

    head_y, head_h = 70, 66
    frags.append(fitbox(X0, head_y, LABW, head_h,
                        "рядки: android/res/xml/device_filter.xml\nстовпці: таблиця QGCUsbSerialProber",
                        size=13, pad=12, fill="#ffffff", stroke=MUTED))
    for i, hname in enumerate(["драйвер для цього VID/PID у таблиці Є",
                               "драйвера для цього VID/PID НЕМА"]):
        frags.append(fitbox(CX[i], head_y, CELLW, head_h, hname, size=15, bold=True,
                            pad=12, fill="#f0f0f0", stroke=INK))

    rows = [
        ("пристрій\nзбігається\nз фільтром",
         [("система сама пропонує запустити станцію,\nдозвіл дають одним дотиком —\nпорт з'являється у списку", "#eaf7ec", FIELD),
          ("станція запустилася від встромляння,\nдозвіл є — а порту в списку НЕМА.\nОсь та сама пастка", "#fdecea", POS)]),
        ("пристрій\nне збігається\nз фільтром",
         [("автозапуску нема; станція сама просить\nдозвіл через requestPermission, і після\n«дозволити» порт з'являється", "#eef4ff", NEG),
          ("пристрій для станції просто невидимий", "#f4f4f4", MUTED)]),
    ]

    y = head_y + head_h + 24
    rh, rgap = 130, 22
    for name, cells in rows:
        frags.append(fitbox(X0, y, LABW, rh, name, size=15, bold=True,
                            pad=14, fill="#ffffff", stroke=MUTED))
        for i, (txt_, fill, stroke) in enumerate(cells):
            frags.append(fitbox(CX[i], y, CELLW, rh, txt_, size=14, pad=16,
                                fill=fill, stroke=stroke))
        y += rh + rgap

    frags.append(fitbox(X0, y + 12, W - 2 * X0, 62,
                        "У стандартній збірці нижнього рядка не існує: фільтр — це <usb-device />, "
                        "тобто «будь-який пристрій»",
                        size=15, pad=14, fill="#eef4ff", stroke=NEG))
    render(os.path.join(OUT, 'usb-two-lists.svg'), W, H, *frags)


# ── 6. Коли яка ручка діє ──────────────────────────────────────────────────
def fig_knob_timing():
    W = 1300
    X0, LABW, GAP = 36, 300, 24
    KNOBW = W - 2 * X0 - LABW - GAP
    KX = X0 + LABW + GAP
    frags = []

    y = 30
    frags.append(fitbox(X0, y, W - 2 * X0, 56,
                        "Ручка діє лише на своєму етапі — і читається рівно один раз",
                        size=18, bold=True, fill="#eef4ff", stroke=NEG))
    y += 56 + 28

    rows = [
        ("Вибір тулчейна\n(до конфігурації)",
         "який саме qt-cmake викликано  ·  CMAKE_TOOLCHAIN_FILE  ·  CMAKE_PREFIX_PATH\n"
         "QT_HOST_PATH  ·  QT_ANDROID_ABIS  ·  ANDROID_NDK, ANDROID_PLATFORM",
         "#fdecea", POS, 108),
        ("Конфігурація",
         "-DQGC_… осідають у кеші теки збірки  ·  .github/build-config.json → QGC_CONFIG_*\n"
         "вибір системних чи завантажених залежностей: QGC_USE_SYSTEM_LIBS, QGC_SYSTEM_LIBS_ONLY",
         "#eef4ff", NEG, 108),
        ("Генерація",
         "властивості цілі QT_ANDROID_* → шаблон AndroidManifest.xml\n"
         "список дозволів  ·  версійний код  ·  qt_import_plugins",
         "#eef4ff", NEG, 100),
        ("Збірка",
         "компіляція під обраний ABI  ·  завантаження архіву GStreamer\n"
         "і звірка sha256 з .github/build-config.json",
         "#f4f6f8", MUTED, 100),
        ("Установлення й пакування",
         "cmake --install → тека payload  ·  QGC_CREATE_APPIMAGE, QGC_BUILD_INSTALLER\n"
         "QGC_CPACK_GENERATOR  ·  ціль qgc-package  ·  кінцеве ім'я артефакту",
         "#eaf7ec", FIELD, 108),
    ]

    for i, (name, knobs, fill, stroke, rh) in enumerate(rows):
        frags.append(fitbox(X0, y, LABW, rh, name, size=16, bold=True,
                            pad=14, fill="#ffffff", stroke=stroke))
        frags.append(fitbox(KX, y, KNOBW, rh, knobs, size=14, pad=16,
                            fill=fill, stroke=stroke))
        y += rh
        if i == 0:
            y += 16
            frags.append(fitbox(X0, y, W - 2 * X0, 52,
                                "Межа неповоротності: ціль прибита до теки збірки. "
                                "Інша платформа або інший ABI — нова тека, а не новий прапорець",
                                size=15, bold=True, pad=12, fill="#fdecea", stroke=POS))
            y += 52 + 16
        else:
            y += 20

    y += 4
    frags.append(fitbox(X0, y, W - 2 * X0, 58,
                        "Прапорець, доданий після першої конфігурації, потребує повторної "
                        "конфігурації тієї самої теки: значення вже лежить у кеші CMake",
                        size=15, pad=14, fill="#ffffff", stroke=MUTED))
    H = y + 58 + 30
    render(os.path.join(OUT, 'knob-timing.svg'), W, H, *frags)


fig_three_artifacts()
fig_serial_paths()
fig_version_code()
fig_jni_two_directions()
fig_usb_two_lists()
fig_knob_timing()
print("ok")
