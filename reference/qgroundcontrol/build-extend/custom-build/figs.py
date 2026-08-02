# -*- coding: utf-8 -*-
"""Фігури до теми «Власна збірка: набір функцій і бренд»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_config_order():
    W, H = 1260, 780
    LX, LW = 60, 600
    NX, NW = 760, 440
    f = []

    steps = [
        ("cmake/CustomOptions.cmake\nтипові значення всіх ручок лягають у кеш",
         "set(… CACHE …) без FORCE означає\n«поклади, якщо ще немає»", False),
        ("перевірка: чи є тека custom/\nякщо є — QGC_CUSTOM_BUILD = ON",
         "окремого прапорця немає:\nперемикачем є сама наявність теки", False),
        ("custom/cmake/CustomOverrides.cmake\nвиробник перезаписує потрібні ручки",
         "значення вже лежать у кеші,\nтому кожен рядок закінчується FORCE", True),
        ("project(${QGC_APP_NAME} …)\nоголошення проєкту",
         "ім'я вже виробникове —\nтаким буде й ім'я цілі, і файлу", False),
        ("add_subdirectory(custom)  →  add_subdirectory(src)\nвласний код і ресурси вливаються в головну ціль",
         "переліки джерел і визначень\nїдуть через кешовані змінні", False),
    ]

    y = 78
    BH, GAP = 96, 44
    for i, (main, note, hot) in enumerate(steps):
        kw = dict(size=16)
        if hot:
            kw.update(bold=True, stroke=POS, sw=2.2, fill="#f8f4ee")
        f.append(fitbox(LX, y, LW, BH, main, **kw))
        f.append(fitbox(NX, y, NW, BH, note, size=14, color=MUTED, fill="#ffffff"))
        f.append(line(LX + LW + 16, y + BH / 2, NX - 16, y + BH / 2,
                      color=MUTED, sw=1.2, dash="4,5"))
        if i < len(steps) - 1:
            f.append(arrow(LX + LW / 2, y + BH, LX + LW / 2, y + BH + GAP))
        y += BH + GAP

    f.append(text(LX + LW / 2, 52, "порядок виконання конфігурації", size=15, color=MUTED))
    return render(os.path.join(OUT, 'config-order.svg'), W, H, *f,
                  title="Чому перезапис спрацьовує саме тут")


def fig_stack_layers():
    W, H = 1320, 620
    cols = [(40, 210), (280, 330), (640, 330), (1000, 280)]
    head = ["шар підтримки", "що це насправді", "перемикач збірки", "що зникає з бінарника"]
    f = []
    for (x, w), t in zip(cols, head):
        f.append(fitbox(x, 62, w, 52, t, size=15, bold=True, fill="#eef2f6"))

    rows = [
        ("Діалект",
         "набір повідомлень,\nзгенерований з XML-опису",
         "QGC_DISABLE_APM_MAVLINK\n→ QGC_NO_ARDUPILOT_DIALECT",
         "структури, ідентифікатори\nй код розбору повідомлень"),
        ("Плагін",
         "клас поведінки: назви режимів,\nперейменування параметрів",
         "QGC_DISABLE_APM_PLUGIN",
         "весь код поведінки\nцього польотного стеку"),
        ("Фабрика",
         "той, хто за типом автопілота\nвирішує, який плагін створити",
         "QGC_DISABLE_APM_PLUGIN_FACTORY\nQGC_DISABLE_PX4_PLUGIN_FACTORY",
         "лише право вибору;\nсам плагін лишається"),
    ]
    y = 134
    RH = 110
    for name, what, opt, gone in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], RH, name, size=17, bold=True))
        f.append(fitbox(cols[1][0], y, cols[1][1], RH, what, size=14))
        f.append(fitbox(cols[2][0], y, cols[2][1], RH, opt, size=13, fill="#f8f4ee"))
        f.append(fitbox(cols[3][0], y, cols[3][1], RH, gone, size=14))
        y += RH + 16

    f.append(fitbox(40, y + 14, 1240, 78,
                    "приклад в апстримі: три перемикачі APM увімкнено, плюс вимкнено фабрику PX4 —\n"
                    "плагін PX4 лишається у збірці, але створює його вже виробникова фабрика",
                    size=15, bold=True, stroke=POS, sw=2.2, fill="#f8f4ee"))
    return render(os.path.join(OUT, 'stack-layers.svg'), W, H, *f,
                  title="Три шари підтримки польотного стеку й що забирає кожен перемикач")


def fig_identity_fields():
    W, H = 1300, 640
    LX, LW = 50, 380
    RX, RW = 620, 630
    f = []

    rows = [
        (74, 132,
         "QGC_APP_NAME\n«ім'я застосунку»",
         "ім'я цілі CMake  →  виконуваний файл і пакет\n"
         "ім'я застосунку  →  тека, де лежать налаштування\n"
         "у щоденній збірці до нього додається « Daily»",
         True),
        (238, 92,
         "QGC_ORG_NAME\nQGC_ORG_DOMAIN",
         "організація й домен  →  друга половина шляху\n"
         "до файлу налаштувань, яку бачить система",
         False),
        (362, 106,
         "QGC_PACKAGE_NAME\n«ідентифікатор пакета»",
         "пакет Android  ·  пакунок macOS  ·  запис .desktop\n"
         "той самий ідентифікатор — застосунки не стануть поруч,\n"
         "а магазин відмовить у завантаженні",
         False),
        (500, 100,
         "QGC_SETTINGS_VERSION\n«версія схеми ключів»",
         "число не збіглося з тим, що у файлі  →  settings.clear()\n"
         "і повідомлення користувачеві про скидання налаштувань",
         False),
    ]
    for y, h, left, right, hot in rows:
        kw = dict(size=15, bold=True)
        if hot:
            kw.update(stroke=POS, sw=2.2, fill="#f8f4ee")
        f.append(fitbox(LX, y, LW, h, left, **kw))
        f.append(fitbox(RX, y, RW, h, right, size=14))
        f.append(arrow(LX + LW + 14, y + h / 2, RX - 14, y + h / 2))

    return render(os.path.join(OUT, 'identity-fields.svg'), W, H, *f,
                  title="Чотири поля ідентичності й куди кожне доїжджає")


def fig_override_windows():
    """До вставки api-custom-overrides.md: які ручки взагалі піддаються FORCE."""
    W, H = 1300, 610
    cols = [(40, 390), (460, 380), (880, 380)]
    f = []

    heads = [
        "1 · прочитано ДО теки виробника",
        "2 · вікно перевизначення",
        "3 · обчислено ПІСЛЯ",
    ]
    bodies = [
        "QGC_CUSTOM_DIR\n\n"
        "саме за нею кореневий файл\n"
        "шукає теку виробника —\n"
        "і робить це раніше, ніж\n"
        "виконає include(CustomOverrides)",

        "усі ручки, оголошені в\n"
        "cmake/CustomOptions.cmake:\n\n"
        "ідентичність · набір функцій ·\n"
        "шляхи артефактів платформ",

        "QGC_APP_VERSION\n"
        "QGC_APP_VERSION_STR\n"
        "QGC_APP_DATE · QGC_GIT_HASH\n\n"
        "їх ставить include(Git)\n"
        "звичайним set() — уже\n"
        "після вашого файлу",
    ]
    verdicts = [
        ("перевизначенню не піддається:\nзадається лише з командного рядка", False),
        ("set(… CACHE <ТИП> … FORCE) діє —\nі перебиває навіть -D… у виклику", True),
        ("звичайна змінна затінює кеш:\nверсію задають теги git", False),
    ]

    HY, HH = 70, 58
    BY, BH = 148, 178
    VY, VH = 348, 92
    for (x, w), h in zip(cols, heads):
        f.append(fitbox(x, HY, w, HH, h, size=17, bold=True, fill="#eef2f6"))
    for (x, w), b in zip(cols, bodies):
        f.append(fitbox(x, BY, w, BH, b, size=15))
    for (x, w), (v, hot) in zip(cols, verdicts):
        kw = dict(size=14, bold=True)
        if hot:
            kw.update(stroke=POS, sw=2.2, fill="#f8f4ee")
        f.append(fitbox(x, VY, w, VH, v, **kw))

    mid = BY + BH / 2
    f.append(arrow(cols[0][0] + cols[0][1] + 4, mid, cols[1][0] - 4, mid))
    f.append(arrow(cols[1][0] + cols[1][1] + 4, mid, cols[2][0] - 4, mid))

    f.append(text(W / 2, 36, "коли яка змінна набуває значення під час конфігурації",
                  size=16, color=MUTED))
    f.append(fitbox(40, 472, 1220, 104,
                    "похідне типове значення — знімок, а не посилання:\n"
                    "QGC_MACOS_BUNDLE_ID і QGC_ANDROID_PACKAGE_NAME взяли ${QGC_PACKAGE_NAME} ще з апстримовим значенням,\n"
                    "тому перевизначення QGC_PACKAGE_NAME їх уже не змінює — кожне задається окремим рядком",
                    size=15, bold=True, stroke=POS, sw=2.2, fill="#f8f4ee"))
    return render(os.path.join(OUT, 'override-windows.svg'), W, H, *f,
                  title="Три вікна: що піддається перевизначенню, а що ні")


def fig_overlay_placement():
    """До вставки proj-custom-overlay-repo.md: чому теку не можна тримати поза деревом."""
    W, H = 1360, 750
    f = []

    f.append(fitbox(300, 62, 760, 128,
                    "кореневий CMakeLists.txt апстриму\n"
                    "if(IS_DIRECTORY \"${CMAKE_SOURCE_DIR}/${QGC_CUSTOM_DIR}\")  …  include(CustomOverrides)\n"
                    "if(QGC_CUSTOM_BUILD)   add_subdirectory(\"${QGC_CUSTOM_DIR}\")",
                    size=15, bold=True, fill="#eef2f6"))

    LX, LW = 60, 590
    RX, RW = 710, 590

    f.append(fitbox(LX, 236, LW, 54,
                    "✓  тека всередині дерева джерел",
                    size=17, bold=True, fill="#eef7ef"))
    f.append(fitbox(RX, 236, RW, 54,
                    "✗  -DQGC_CUSTOM_DIR=../custom",
                    size=17, bold=True, stroke=POS, sw=2.2, fill="#fdecea"))

    f.append(arrow(680, 190, LX + LW / 2, 230))
    f.append(arrow(680, 190, RX + RW / 2, 230))

    left = [
        "IS_DIRECTORY — так",
        "CMAKE_MODULE_PATH — доповнено",
        "include(CustomOverrides) — виконано",
        "add_subdirectory — тека під коренем, приймає",
    ]
    right = [
        "IS_DIRECTORY — так, шлях справді існує",
        "CMAKE_MODULE_PATH — доповнено",
        "include(CustomOverrides) — виконано",
        "add_subdirectory — ПОМИЛКА конфігурації",
    ]
    y = 310
    RH = 56
    for i, (l, r) in enumerate(zip(left, right)):
        last = (i == len(left) - 1)
        f.append(fitbox(LX, y, LW, RH, l, size=15,
                        fill="#eef7ef" if last else FILL))
        kw = dict(size=15)
        if last:
            kw.update(bold=True, stroke=POS, sw=2.2, fill="#fdecea")
        f.append(fitbox(RX, y, RW, RH, r, **kw))
        y += RH + 12

    f.append(fitbox(60, y + 20, 1240, 92,
                    "«not given a binary directory … is not a subdirectory of»\n"
                    "три кроки з чотирьох спрацювали — тому підозра падає на що завгодно, крім шляху",
                    size=16, bold=True, stroke=POS, sw=2.2, fill="#f8f4ee"))

    return render(os.path.join(OUT, 'overlay-placement.svg'), W, H, *f,
                  title="Дві згадки теки в конфігурації висувають різні вимоги до шляху")


def fig_overlay_shapes():
    """До вставки proj-custom-overlay-repo.md: дві форми репозиторію поруч."""
    W, H = 1420, 1050
    LX, LW = 50, 640
    RX, RW = 730, 640
    f = []

    f.append(fitbox(LX, 58, LW, 52, "форк: ваша тека всередині чужого репозиторію",
                    size=17, bold=True, fill="#eef2f6"))
    f.append(fitbox(RX, 58, RW, 52, "накладка: чужий репозиторій підмодулем усередині вашого",
                    size=17, bold=True, fill="#eef2f6"))

    tree_l = ("my-qgroundcontrol/         форк усього апстриму\n"
              "├── custom/                ваше\n"
              "├── custom-example/        апстримове\n"
              "├── src/ cmake/ android/ deploy/\n"
              "├── .github/workflows/     апстримові\n"
              "└── CMakeLists.txt         апстримовий")
    tree_r = ("my-gcs/                    ваш репозиторій\n"
              "├── custom/                ваше\n"
              "├── upstream/qgroundcontrol/   підмодуль на тезі\n"
              "├── scripts/overlay.sh  scripts/bump-upstream.sh\n"
              "├── upstream-watch.txt  options.snapshot\n"
              "└── .github/workflows/build.yml")
    f.append(fitbox(LX, 130, LW, 176, tree_l, size=15))
    f.append(fitbox(RX, 130, RW, 176, tree_r, size=15))

    rows = [
        ("що показує git log --oneline",
         "ваші коміти впереміш із тисячами чужих;\nбез « -- custom/ » журнал не читається",
         "лише ваші коміти;\nчужа історія лежить окремо, у підмодулі",
         100),
        ("як виглядає оновлення",
         "git merge upstream/master —\nтисячі чужих комітів у вашу гілку",
         "один рядок в індексі:\n-Subproject commit 9f3c1ad…\n+Subproject commit 4b81e02…",
         112),
        ("що доводиться робити перед конфігурацією",
         "нічого: тека вже під коренем дерева",
         "накладання: посилання на машині розробника,\nкопія в CI",
         92),
        ("де проходить межа дисципліни",
         "чужі файли поруч і відкриті на запис —\nправку «лише один рядок» ніщо не зупиняє",
         "чужі файли в підмодулі — правка там\nодразу видно й не потрапляє у ваш коміт",
         100),
    ]

    y = 344
    for cap, l, r, h in rows:
        f.append(text(W / 2, y - 10, cap, size=15, color=MUTED))
        f.append(fitbox(LX, y, LW, h, l, size=15))
        f.append(fitbox(RX, y, RW, h, r, size=15, fill="#eef7ef"))
        y += h + 46

    f.append(fitbox(50, y - 16, 1320, 84,
                    "спільне для обох форм: на момент конфігурації тека виробника\n"
                    "мусить фізично лежати всередині дерева джерел апстриму",
                    size=16, bold=True, stroke=POS, sw=2.2, fill="#f8f4ee"))

    return render(os.path.join(OUT, 'overlay-shapes.svg'), W, H, *f,
                  title="Дві форми репозиторію виробникової збірки й рахунок до кожної")


if __name__ == '__main__':
    print(fig_config_order())
    print(fig_stack_layers())
    print(fig_identity_fields())
    print(fig_override_windows())
    print(fig_overlay_placement())
    print(fig_overlay_shapes())
