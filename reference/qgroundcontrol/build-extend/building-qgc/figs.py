# -*- coding: utf-8 -*-
"""Фігури до теми «Збірка QGroundControl: залежності й кроки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

HEAD_FILL = "#eef2f6"
WARM_FILL = "#f8f4ee"


def fig_three_kinds():
    """Три роди залежностей і критерій межі."""
    W, H = 1260, 680
    f = []
    cols = [(40, 380), (440, 380), (840, 380)]

    heads = ["ПРИНЕСЕНЕ РУКАМИ", "ПРИТЯГНУТЕ ЗБІРКОЮ", "ПОРОДЖЕНЕ ЗБІРКОЮ"]
    for (x, w), t in zip(cols, heads):
        f.append(fitbox(x, 58, w, 52, t, size=17, bold=True, fill=HEAD_FILL))

    items = [
        "Qt потрібної версії\nз потрібними модулями\n\n"
        "компілятор, CMake ≥ 3.25,\nNinja, Python ≥ 3.10\n\n"
        "системні бібліотеки:\nspeech-dispatcher, SDL2",

        "опис протоколу MAVLink\nза прибитим комітом\n\n"
        "готовий SDK GStreamer\nіз перевіркою суми\n\n"
        "дрібніші залежності\nчерез CPM",

        "дерево заголовків MAVLink\nіз XML-описів\n\n"
        "перелічення протоколу\nдля C++ і для QML\n\n"
        "рядок версії застосунку\nзі стану репозиторію",
    ]
    for (x, w), t in zip(cols, items):
        f.append(fitbox(x, 128, w, 216, t, size=15))

    why = [
        "надто дороге, щоб добувати\nщоразу: гігабайти й години.\n"
        "Збірка тільки перевіряє\nнаявність і зупиняється",

        "версія прямо міняє поведінку,\nтож проєкт мусить обрати її сам —\n"
        "і може принести за хвилини",

        "цілком виводиться з джерела,\nтож тримати похідне в репозиторії\n"
        "означало б комітити тисячі\nфайлів, яких ніхто не перегляне",
    ]
    for (x, w), t in zip(cols, why):
        f.append(fitbox(x, 364, w, 134, t, size=14, fill=WARM_FILL))

    f.append(fitbox(70, 528, 1120, 110,
                    "КРИТЕРІЙ МЕЖІ\n"
                    "притягують те, версію чого проєкт мусить контролювати сам і що дешево принести;\n"
                    "приносять руками те, що проєкт контролювати не в змозі або що надто дороге;\n"
                    "породжують те, що є похідним від уже наявного джерела",
                    size=16, bold=True, stroke=POS, sw=2.2))
    return render(os.path.join(OUT, 'three-kinds.svg'), W, H, *f,
                  title="Три роди того, від чого залежить збірка")


def fig_pipeline():
    """Стадії збірки і типова поламка кожної."""
    W, H = 1220, 800
    f = []
    LX, LW = 60, 470
    RX, RW = 620, 540

    f.append(text(LX + LW / 2, 56, "стадія — і що вона робить", size=15, bold=True))
    f.append(text(RX + RW / 2, 56, "як упізнати саме її у виводі", size=15, bold=True))

    rows = [
        ("Клон джерел",
         "дерево без підмодулів;\nбез історії git — без версії"),
        ("Системні залежності",
         "«не знайдено пакет» під час\nвстановлення, а не збірки"),
        ("Пошук Qt і компілятора",
         "Could not find … \"Qt6Location\"\nверсія Qt поза діапазоном"),
        ("Добування залежностей",
         "не вдалося клонувати MAVLink;\nне збіглася сума архіву SDK"),
        ("Кодогенерація",
         "немає mavlink_msg_*.h;\nтрасування Python у виводі"),
        ("Компіляція й лінкування",
         "попередження як помилка (WERROR);\nпроцес убито при лінкуванні"),
    ]

    y = 76
    STEP = 116
    for i, (left, right) in enumerate(rows):
        f.append(fitbox(LX, y, LW, 84, left, size=17, bold=True))
        f.append(fitbox(RX, y, RW, 84, right, size=14, fill=WARM_FILL))
        f.append(line(LX + LW + 14, y + 42, RX - 14, y + 42, color=MUTED, dash="5,5"))
        if i < len(rows) - 1:
            f.append(arrow(LX + LW / 2, y + 84, LX + LW / 2, y + STEP - 4))
        y += STEP

    f.append(fitbox(180, 736, 860, 48,
                    "кожна стадія спирається на завершену попередню — звідси й порядок кроків",
                    size=15, bold=True, fill=HEAD_FILL))
    return render(os.path.join(OUT, 'pipeline.svg'), W, H, *f,
                  title="Стадії збірки застосунку і властиві їм поламки")


def fig_config_single_source():
    """Один файл конфігурації — три споживачі."""
    W, H = 1200, 620
    f = []

    f.append(fitbox(300, 58, 600, 156,
                    ".github/build-config.json\n\n"
                    "qt: 6.11.1, мінімум 6.11.0, перелік модулів\n"
                    "android: platform 36, min_sdk 28, NDK r27c\n"
                    "gstreamer: 1.28.4, мінімум 1.20.0\n"
                    "build: cmake_minimum_version 3.25",
                    size=16, bold=True, stroke=POS, sw=2.2, fill=WARM_FILL))

    f.append(arrow(600, 214, 600, 256))
    f.append(line(210, 256, 990, 256))
    for cx in (210, 600, 990):
        f.append(arrow(cx, 256, cx, 306))

    consumers = [
        (60, "install_qt.py\n\nставить на машину\nрозробника саме ту\nверсію й ті модулі"),
        (450, "робочі процеси CI\n\nставлять те саме\nна складальний\nагент"),
        (840, "CustomOptions.cmake\n\nQGC_QT_MINIMUM_VERSION\nQGC_QT_MAXIMUM_VERSION\nі решта опцій"),
    ]
    for x, t in consumers:
        f.append(fitbox(x, 306, 300, 154, t, size=15))

    f.append(fitbox(120, 496, 960, 96,
                    "число написане один раз — тож неможлива класична розбіжність,\n"
                    "коли CI зелений, а на машині розробника не конфігурується",
                    size=16, bold=True, fill=HEAD_FILL))
    return render(os.path.join(OUT, 'config-single-source.svg'), W, H, *f,
                  title="Одне джерело істини про версії")


def fig_mavgen_determinism():
    """Недетермінований генератор знецінює кеш компілятора."""
    W, H = 1220, 640
    f = []
    LX, LW = 50, 520
    RX, RW = 650, 520

    f.append(fitbox(LX, 56, LW, 50, "засіл хешування випадковий",
                    size=17, bold=True, fill=HEAD_FILL))
    f.append(fitbox(RX, 56, RW, 50, "засіл прибито, генератор пропатчено",
                    size=17, bold=True, fill=HEAD_FILL))

    rows = [
        ("той самий XML-опис протоколу",
         "той самий XML-опис протоколу"),
        ("константа в заголовку щоразу інша",
         "константа в заголовку та сама"),
        ("вміст заголовка змінився —\nключ кешу компілятора інший",
         "вміст заголовка не змінився —\nключ кешу компілятора той самий"),
    ]
    y = 124
    STEP = 106
    for left, right in rows:
        f.append(fitbox(LX, y, LW, 72, left, size=15))
        f.append(fitbox(RX, y, RW, 72, right, size=15))
        f.append(arrow(LX + LW / 2, y + 72, LX + LW / 2, y + STEP - 4))
        f.append(arrow(RX + RW / 2, y + 72, RX + RW / 2, y + STEP - 4))
        y += STEP

    f.append(fitbox(LX, y, LW, 96,
                    "жодного влучання в кеш\n"
                    "кожна конфігурація = повна перезбірка",
                    size=16, bold=True, stroke=POS, sw=2.2, fill=WARM_FILL))
    f.append(fitbox(RX, y, RW, 96,
                    "кеш влучає\n"
                    "перезбирається лише справді змінене",
                    size=16, bold=True, stroke=FIELD, sw=2.2))

    f.append(text(W / 2, y + 138,
                  "правило: генератор коду мусить бути функцією від свого входу",
                  size=16, bold=True, color=MUTED))
    return render(os.path.join(OUT, 'mavgen-determinism.svg'), W, H, *f,
                  title="Чому детермінізм кодогенерації коштує окремого патча")


def fig_options_precedence():
    """Хто перемагає, коли одна опція названа в кількох місцях."""
    W, H = 1300, 830
    f = []
    LX, LW = 50, 500
    RX, RW = 630, 620

    f.append(text(LX + LW / 2, 52, "звідки береться значення", size=16, bold=True))
    f.append(text(RX + RW / 2, 52, "чи перебиває вже встановлене", size=16, bold=True))

    rows = [
        ("cmake/CustomOptions.cmake\noption() і set(… CACHE …)",
         "запише значення, ЛИШЕ якщо в кеші\nще немає запису з таким іменем"),
        ("числа з .github/build-config.json",
         "ті самі set(… CACHE …) — просто\nчисло приїхало з одного JSON"),
        ("cacheVariables пресета\nі -D у командному рядку",
         "потрапляють у кеш ДО читання CMakeLists,\nтож типове значення вже не спрацює"),
        ("CMakeCache.txt\nвід попередньої конфігурації",
         "запис уже існує — типове значення\nне застосується більше ніколи"),
        ("custom/cmake/CustomOverrides.cmake",
         "set(… CACHE … FORCE) читається останнім —\nперебиває навіть ваш -D"),
    ]

    y = 76
    STEP = 128
    for i, (left, right) in enumerate(rows):
        f.append(fitbox(LX, y, LW, 92, left, size=16, bold=True))
        f.append(fitbox(RX, y, RW, 92, right, size=14, fill=WARM_FILL))
        f.append(line(LX + LW + 16, y + 46, RX - 16, y + 46, color=MUTED, dash="5,5"))
        if i < len(rows) - 1:
            f.append(arrow(LX + LW / 2, y + 92, LX + LW / 2, y + STEP - 6))
        y += STEP

    f.append(fitbox(90, y + 12, 1120, 96,
                    "прибрати -D з рядка НЕ означає повернути типове значення:\n"
                    "запис лишається в кеші, поки його не стерти — cmake -B build -U ІМʼЯ",
                    size=16, bold=True, stroke=POS, sw=2.2, fill=HEAD_FILL))
    return render(os.path.join(OUT, 'options-precedence.svg'), W, H, *f,
                  title="Порядок, у якому встановлюється значення опції збірки")


def fig_qmake_to_cmake_timeline():
    """Хронологія переходу збірки з qmake на CMake (вставка hist-qmake-to-cmake)."""
    W, H = 1400, 1090
    f = []
    DX, DW = 40, 210
    EX, EW = 280, 640
    TX, TW = 950, 410

    f.append(text(DX + DW / 2, 54, "коли", size=16, bold=True))
    f.append(text(EX + EW / 2, 54, "що сталося", size=16, bold=True))
    f.append(text(TX + TW / 2, 54, "слід у репозиторії", size=16, bold=True))

    rows = [
        ("вересень –\nжовтень 2018",
         "Деніел Аґар подає «initial cmake support» (PR #6862)",
         "поруч із qgroundcontrol.pro\nз'являється CMakeLists.txt"),
        ("2018 – 2023",
         "дві системи живуть поруч; головна — qmake",
         ".pro важить 49 КБ,\nCMakeLists.txt — близько 6 КБ"),
        ("30 листопада 2023",
         "вийшла лінія 4.3 на Qt 5; того ж дня Сергій Лісовенко\nвідкриває «Adopt cmake to Qt6 build» (PR #10884)",
         "порт на Qt 6 із самого початку\nйде через CMake, не через .pro"),
        ("1 травня 2024",
         "Голден Ремзі заводить issue #11436\n«Custom Build Implementation for CMake»",
         "механізм custom/ під CMake\nще не працює"),
        ("10 травня 2024",
         "PR #11517 вимикає юніт-тести на qmake\nіз формулюванням «build tool is deprecated»",
         "qmake офіційно названо застарілим"),
        ("11 червня 2024",
         "вийшла лінія 4.4 — остання на Qt 5",
         "у корені ще обидва файли:\nі .pro, і CMakeLists.txt"),
        ("15 серпня 2024",
         "PR #11735 «Remove Deprecated QMake Build System» злито",
         "qgroundcontrol.pro зник;\n.gitmodules свідомо лишили"),
        ("16 січня 2025",
         "PR #12333 «CMake: Add CPM» злито (закриває issue #11725)",
         "з'явився механізм добування\nзалежностей на етапі конфігурації"),
        ("28 червня 2025",
         "PR #13037 переводить останній підмодуль на CPM",
         ".gitmodules зник із master"),
        ("11 липня 2025",
         "стабільна 5.0.6",
         "перша стабільна лінія,\nяка збирається лише CMake"),
    ]

    y = 76
    STEP = 88
    for i, (when, what, trace) in enumerate(rows):
        f.append(fitbox(DX, y, DW, 70, when, size=15, bold=True, fill=HEAD_FILL))
        f.append(fitbox(EX, y, EW, 70, what, size=15))
        f.append(fitbox(TX, y, TW, 70, trace, size=14, fill=WARM_FILL))
        if i < len(rows) - 1:
            f.append(arrow(DX + DW / 2, y + 70, DX + DW / 2, y + STEP - 4))
        y += STEP

    f.append(fitbox(150, y + 14, 1100, 90,
                    "перехід тривав майже сім років і не мав однієї дати:\n"
                    "спершу друга система з'явилася поруч, потім стала головною,\n"
                    "і аж наприкінці зникла перша",
                    size=16, bold=True, stroke=POS, sw=2.2, fill=HEAD_FILL))
    return render(os.path.join(OUT, 'qmake-to-cmake-timeline.svg'), W, H, *f,
                  title="Хронологія переходу збірки QGroundControl з qmake на CMake")


def fig_field_reorder():
    """Порядок полів HEARTBEAT в XML і в дротовій розкладці."""
    W, H = 1200, 620
    f = []

    LX, RX, BW = 60, 700, 440
    f.append(fitbox(LX, 58, BW, 46, "ПОРЯДОК В XML", size=17, bold=True, fill=HEAD_FILL))
    f.append(fitbox(RX, 58, BW, 46, "ДРОТОВИЙ ПОРЯДОК: сортування за розміром",
                    size=17, bold=True, fill=HEAD_FILL))

    left = [
        ("uint8_t   type", "1 Б"),
        ("uint8_t   autopilot", "1 Б"),
        ("uint8_t   base_mode", "1 Б"),
        ("uint32_t  custom_mode", "4 Б"),
        ("uint8_t   system_status", "1 Б"),
        ("uint8_t   mavlink_version", "1 Б"),
    ]
    right = [
        ("зміщення 0", "uint32_t  custom_mode"),
        ("зміщення 4", "uint8_t   type"),
        ("зміщення 5", "uint8_t   autopilot"),
        ("зміщення 6", "uint8_t   base_mode"),
        ("зміщення 7", "uint8_t   system_status"),
        ("зміщення 8", "uint8_t   mavlink_version"),
    ]
    # ліва позиція -> права позиція
    link = {0: 1, 1: 2, 2: 3, 3: 0, 4: 4, 5: 5}

    Y0, STEP, BH = 130, 62, 48
    for i, (name, size) in enumerate(left):
        y = Y0 + i * STEP
        hot = (i == 3)
        f.append(fitbox(LX, y, BW - 90, BH, name, size=16,
                        stroke=(FIELD if hot else LINE), sw=(2.4 if hot else 1.5)))
        f.append(fitbox(LX + BW - 80, y, 80, BH, size, size=15, fill=WARM_FILL))

    for i, (ofs, name) in enumerate(right):
        y = Y0 + i * STEP
        hot = (i == 0)
        f.append(fitbox(RX, y, 130, BH, ofs, size=14, fill=WARM_FILL))
        f.append(fitbox(RX + 140, y, BW - 140, BH, name, size=16,
                        stroke=(FIELD if hot else LINE), sw=(2.4 if hot else 1.5)))

    for i, j in link.items():
        y1 = Y0 + i * STEP + BH / 2
        y2 = Y0 + j * STEP + BH / 2
        hot = (i == 3)
        f.append(arrow(LX + BW + 6, y1, RX - 6, y2,
                       color=(FIELD if hot else MUTED), sw=(2.4 if hot else 1.3)))

    f.append(fitbox(60, 520, 1080, 76,
                    "сортування стійке: поля однакового розміру лишаються в порядку XML\n"
                    "розширення MAVLink 2 не сортують — їх дописують у хвіст\n"
                    "CRC_EXTRA рахують саме за правою колонкою",
                    size=15, bold=True, stroke=POS, sw=2.2, fill=HEAD_FILL))

    return render(os.path.join(OUT, 'field-reorder.svg'), W, H, *f,
                  title="HEARTBEAT: як генератор переставляє поля перед виписуванням структури")


def fig_codegen_chain():
    """Ланцюг кодогенерації MAVLink у збірці QGroundControl."""
    W, H = 1280, 780
    f = []

    LX, LW = 60, 470
    f.append(fitbox(LX, 64, LW, 86,
                    "message_definitions/v1.0/all.xml\n"
                    "+ ланцюг <include>: common, minimal, standard, …",
                    size=16, fill=WARM_FILL))
    f.append(arrow(LX + LW / 2, 150, LX + LW / 2, 196))

    f.append(fitbox(LX, 200, LW, 78,
                    "mavgen  --lang=C  --wire-protocol=2.0\n"
                    "PYTHONHASHSEED=0",
                    size=16, bold=True, fill=HEAD_FILL))
    f.append(arrow(LX + LW / 2, 278, LX + LW / 2, 324))

    f.append(fitbox(LX, 328, LW, 190,
                    "include/mavlink/\n"
                    "сталі файли: protocol.h, mavlink_types.h, checksum.h\n"
                    "all/   common/   minimal/   ardupilotmega/   …\n"
                    "<діалект>.h — таблиці CRC і перелічення\n"
                    "mavlink_msg_*.h — структура, пакувальник, CRC_EXTRA",
                    size=15))

    RX, RW = 720, 500
    f.append(fitbox(RX, 328, RW, 118,
                    "mavlink_enums.py\n"
                    "читає ЗГЕНЕРОВАНІ заголовки\n"
                    "→ MAVLinkEnums.h + обгортка для QML",
                    size=16, fill=HEAD_FILL))
    f.append(fitbox(RX, 500, RW, 118,
                    "mavlink_instance_fields.py\n"
                    "читає XML НАПРЯМУ\n"
                    "→ MAVLinkInstanceFields.h",
                    size=16, fill=HEAD_FILL))

    f.append(arrow(LX + LW + 6, 387, RX - 6, 387))

    CORR = 625
    f.append(line(LX + LW + 6, 107, CORR, 107, color=NEG, sw=1.8))
    f.append(line(CORR, 107, CORR, 559, color=NEG, sw=1.8))
    f.append(arrow(CORR, 559, RX - 6, 559, color=NEG, sw=1.8))

    f.append(fitbox(60, 640, 1160, 100,
                    "позначка instance=\"true\" до C-заголовків не доходить —\n"
                    "тому один генератор бере готовий вихід mavgen, а другий вертається до першоджерела\n"
                    "обидва пишуть файл лише за зміни вмісту, щоб не запускати перезбірку дарма",
                    size=15, bold=True, stroke=POS, sw=2.2, fill=WARM_FILL))

    return render(os.path.join(OUT, 'codegen-chain.svg'), W, H, *f,
                  title="Ланцюг кодогенерації: від XML-опису до заголовків, які включає станція")


def fig_custom_before_after():
    """Тека взірцевої вендорської збірки до переходу й після (вставка hist-qmake-to-cmake)."""
    W, H = 1340, 800
    f = []
    LX, LW = 50, 600
    RX, RW = 700, 590

    f.append(fitbox(LX, 40, LW, 54, "custom-example у гілці 4.4 (qmake)",
                    size=17, bold=True, fill=HEAD_FILL))
    f.append(fitbox(RX, 40, RW, 54, "custom-example у master (CMake)",
                    size=17, bold=True, fill=HEAD_FILL))

    old_own = ("СВОЄ\n"
               "custom.pri — 2 636 Б\n"
               "custom_deploy.pri — 243 Б\n"
               "custom.qrc — 2 338 Б")
    old_copy = ("КОПІЇ АПСТРИМУ В ДЕРЕВІ ФОРКА\n"
                "qgroundcontrol.qrc — 35 894 Б\n"
                "qgcresources.qrc — 7 137 Б\n"
                "InstrumentValueIcons.qrc — 26 194 Б")
    old_tool = ("ЩОБ КОПІЇ НЕ ВІДСТАВАЛИ\n"
                "qgroundcontrol.exclusion — 123 Б\n"
                "qgcresources.exclusion — 82 Б\n"
                "updateqrc.py — 1 166 Б\n"
                "updateinstrumentqrc.py — 574 Б")

    new_own = ("СВОЄ\n"
               "CMakeLists.txt — 6 588 Б\n"
               "custom.qrc — 2 139 Б\n"
               "тека cmake/ з власними модулями")
    new_copy = "КОПІЇ АПСТРИМУ\nнемає"
    new_tool = "ІНСТРУМЕНТИ ПЕРЕГЕНЕРАЦІЇ\nнемає"

    f.append(fitbox(LX, 112, LW, 112, old_own, size=15))
    f.append(fitbox(LX, 240, LW, 128, old_copy, size=15, fill=WARM_FILL, stroke=POS, sw=2.2))
    f.append(fitbox(LX, 384, LW, 144, old_tool, size=15, fill=WARM_FILL, stroke=POS, sw=2.2))

    f.append(fitbox(RX, 112, RW, 112, new_own, size=15))
    f.append(fitbox(RX, 240, RW, 128, new_copy, size=16, bold=True, stroke=FIELD, sw=2.4))
    f.append(fitbox(RX, 384, RW, 144, new_tool, size=16, bold=True, stroke=FIELD, sw=2.4))

    f.append(fitbox(LX, 548, LW, 120,
                    "після кожного оновлення апстриму вендор\n"
                    "прогонить скрипт і комітить перегенеровані копії:\n"
                    "69 КБ чужого переліку ресурсів у власному дереві",
                    size=15, bold=True, fill=HEAD_FILL))
    f.append(fitbox(RX, 548, RW, 120,
                    "перелік ресурсів апстриму лишається в апстримі;\n"
                    "тека підключається як підпроєкт,\n"
                    "а свої файли лише додаються до цілі",
                    size=15, bold=True, fill=HEAD_FILL))

    f.append(fitbox(190, 692, 960, 80,
                    "різниця не в кількості файлів, а в тому,\n"
                    "чи мусить форк тримати копію чужого рішення",
                    size=16, bold=True, stroke=POS, sw=2.2))

    return render(os.path.join(OUT, 'custom-before-after.svg'), W, H, *f,
                  title="Тека вендорської збірки до переходу на CMake і після нього")


if __name__ == '__main__':
    print(fig_three_kinds())
    print(fig_pipeline())
    print(fig_config_single_source())
    print(fig_mavgen_determinism())
    print(fig_options_precedence())
    print(fig_qmake_to_cmake_timeline())
    print(fig_field_reorder())
    print(fig_codegen_chain())
    print(fig_custom_before_after())
