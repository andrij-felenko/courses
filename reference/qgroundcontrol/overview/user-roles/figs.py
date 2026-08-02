# -*- coding: utf-8 -*-
"""Фігури до теми «Три користувачі станції: пілот, налаштувальник, розробник»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Два екрани: під погляд і під пошук ───────────────────────────────────
def two_screens():
    W, H = 1120, 620
    f = []

    # ЛІВА панель — політний екран
    lx, ly, lw, lh = 50, 80, 470, 430
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=LINE, sw=2))
    f.append(text(lx + lw / 2, ly - 34, "Політ: екран під ОДИН погляд", size=17, bold=True))
    f.append(text(lx + lw / 2, ly - 12, "рука зайнята, очі — на апараті", size=13, color=MUTED))

    # смуга стану згори
    f.append(fitbox(lx + 16, ly + 16, lw - 32, 46, "стан одним рядком: режим · батарея · GPS · канал",
                    size=13, fill="#eef2f7"))
    # карта / відео
    f.append(fitbox(lx + 16, ly + 78, 290, 210, "карта або відео", size=15, fill="#f4f6f8"))
    # прилади
    f.append(fitbox(lx + 318, ly + 78, 136, 100, "авіагоризонт", size=13, fill="#eef2f7"))
    f.append(fitbox(lx + 318, ly + 188, 136, 100, "висота\nшвидкість\nвідстань", size=13, fill="#eef2f7"))
    # смуга дій
    f.append(fitbox(lx + 16, ly + 304, 138, 68, "Зліт", size=15, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(lx + 168, ly + 304, 138, 68, "Додому", size=15, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(lx + 320, ly + 304, 134, 68, "Пауза", size=15, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(lx + 16, ly + 384, 438, 32, "кожну з них — ПРОВЕСТИ пальцем, а не торкнутись",
                    size=13, fill="#ffffff", stroke=POS))

    # ПРАВА панель — екран налаштування
    rx, ry, rw, rh = 600, 80, 470, 430
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=LINE, sw=2))
    f.append(text(rx + rw / 2, ry - 34, "Налаштування: екран під ПОШУК", size=17, bold=True))
    f.append(text(rx + rw / 2, ry - 12, "апарат на столі, часу вдосталь", size=13, color=MUTED))

    pages = ["Прошивка", "Рама", "Сенсори", "Пульт", "Режими",
             "Живлення", "Мотори", "Безпека", "Тюнінг", "…"]
    for i, p in enumerate(pages):
        f.append(fitbox(rx + 16, ry + 18 + i * 38, 150, 32, p, size=13,
                        fill="#eef2f7" if i % 2 == 0 else "#f8fafc"))

    f.append(fitbox(rx + 182, ry + 18, 272, 32, "пошук: BATT_", size=13, fill="#ffffff"))
    rows = ["BATT_CAPACITY", "BATT_LOW_VOLT", "BATT_CRIT_VOLT", "BATT_N_CELLS",
            "BATT_V_DIV", "BATT_A_PER_V", "BATT_SOURCE"]
    for i, r in enumerate(rows):
        f.append(fitbox(rx + 182, ry + 60 + i * 38, 272, 32, r, size=12, fill="#f8fafc"))
    f.append(fitbox(rx + 182, ry + 326, 272, 90,
                    "…і так сотні рядків:\nповна таблиця параметрів\nяк остання інстанція",
                    size=13, fill="#eef2f7"))

    f.append(text(W / 2, H - 26,
                  "той самий бінарник — два взаємно несумісні набори вимог",
                  size=15, bold=True))
    render(os.path.join(OUT, 'two-screens.svg'), W, H, *f)


# ── 2. День апарата: моменти, а не облікові записи ──────────────────────────
def day_and_roles():
    W, H = 1180, 560
    f = []
    f.append(text(W / 2, 40, "Розділення йде за МОМЕНТОМ роботи, а не за людиною", size=18, bold=True))

    cols = [
        ("Стіл", "апарат роззброєний,\nгвинти зняті, USB", "Налаштування", "налаштувальник"),
        ("Підготовка", "маршрут, висоти,\nгеозона, точка збору", "План", "налаштувальник\nабо пілот"),
        ("Політ", "апарат у повітрі,\nрішення за секунди", "Політ", "пілот"),
        ("Після", "журнали, повідомлення,\nграфіки величин", "Розбір", "налаштувальник\nабо розробник"),
    ]
    x0, cw, gap = 60, 250, 32
    ytop, ybody, ybot = 90, 160, 330

    for i, (name, what, view, who) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(fitbox(x, ytop, cw, 46, name, size=17, bold=True, fill="#eef2f7"))
        f.append(fitbox(x, ybody, cw, 96, what, size=13, fill="#ffffff"))
        f.append(fitbox(x, ybody + 118, cw, 44, "екран: " + view, size=14, bold=True,
                        fill="#eaf0fd", stroke=NEG))
        f.append(fitbox(x, ybot, cw, 76, who, size=14, fill="#f4f6f8", stroke=FIELD))
        if i < len(cols) - 1:
            f.append(arrow(x + cw + 4, ytop + 23, x + cw + gap - 4, ytop + 23))

    # зворотний зв'язок: розбір → стіл
    yb = ybot + 118
    f.append(line(x0 + 3 * (cw + gap) + cw / 2, ybot + 76, x0 + 3 * (cw + gap) + cw / 2, yb, sw=1.8))
    f.append(line(x0 + 3 * (cw + gap) + cw / 2, yb, x0 + cw / 2, yb, sw=1.8))
    f.append(arrow(x0 + cw / 2, yb, x0 + cw / 2, ybot + 80))
    f.append(text(W / 2, yb + 26, "побачене в журналі повертає апарат на стіл", size=14, color=MUTED))

    f.append(text(W / 2, H - 28,
                  "у застосунку немає ні входу, ні облікових записів: та сама людина буває всіма трьома за один день",
                  size=15, bold=True))
    render(os.path.join(OUT, 'day-and-roles.svg'), W, H, *f)


# ── 3. Четверо воріт між кодом і пальцем ────────────────────────────────────
def four_gates():
    W, H = 1140, 740
    f = []
    f.append(text(W / 2, 36, "Четверо воріт між елементом у коді й виконаною дією", size=18, bold=True))

    gx, gw = 60, 430
    lx, lw = 560, 520
    f.append(text(gx + gw / 2, 70, "ворота", size=14, bold=True, color=MUTED))
    f.append(text(lx + lw / 2, 70, "яку саме помилку вони ловлять", size=14, bold=True, color=MUTED))
    y = 92
    rows = [
        ("Елемент існує у вихідному коді", None, "#f4f6f8", LINE),
        ("1. Збірка: чи ввімкнено його\nу ЦЬОМУ застосунку",
         "хибний набір можливостей для цієї\nаудиторії — вирішує розробник збірки",
         "#eef2f7", NEG),
        ("2. Поглиблений режим: чи відкрито\nшар налаштувальника",
         "блукання поза межами своєї ролі —\nпілот у сторінках, яких не розуміє",
         "#eef2f7", NEG),
        ("3. Стан: чи має дія сенс\nсаме зараз",
         "дія неможлива або небезпечна в цьому\nстані — апарат зброєний, борт не на USB",
         "#eef2f7", FIELD),
        ("4. Намір: жест, який шум\nне відтворює",
         "випадковий дотик, поштовх, крапля\nдощу на екрані",
         "#fdecea", POS),
        ("Команда пішла на апарат", None, "#f4f6f8", LINE),
    ]
    heights = [50, 74, 74, 74, 74, 50]

    for i, ((label, catch, fill, stroke), h) in enumerate(zip(rows, heights)):
        f.append(fitbox(gx, y, gw, h, label, size=14, bold=(catch is None), fill=fill, stroke=stroke))
        if catch:
            f.append(fitbox(lx, y, lw, h, catch, size=13, fill="#ffffff", stroke=MUTED))
        if i < len(rows) - 1:
            f.append(arrow(gx + gw / 2, y + h + 4, gx + gw / 2, y + h + 30))
        y += h + 34

    f.append(text(W / 2, y + 22,
                  "жодні з них не замінюють інших: кожні відповідають на своє питання",
                  size=15, bold=True))
    render(os.path.join(OUT, 'four-gates.svg'), W, H, *f)


# ── 4. [вставка api] Шлях від QML-виразу до віртуального методу ─────────────
def api_options_graph():
    W, H = 1180, 640
    f = []
    f.append(text(W / 2, 38, "Шлях від QML-виразу до віртуального методу C++", size=18, bold=True))
    f.append(text(250, 80, "як це пишеться в QML", size=14, bold=True, color=MUTED))
    f.append(text(820, 80, "що за цим стоїть у C++", size=14, bold=True, color=MUTED))

    # ряд 1 — ядрове розширення
    f.append(fitbox(60, 100, 380, 170,
                    "QGroundControl.corePlugin\n\n.showAdvancedUI\n.showAdvancedUIMessage\n.analyzePages",
                    size=14, fill="#f8fafc"))
    f.append(fitbox(520, 100, 600, 170,
                    "QGCCorePlugin — твоя похідна\n\n"
                    "showAdvancedUI() · showAdvancedUIMessage()\n"
                    "overrideSettingsGroupVisibility(QString)\n"
                    "adjustSettingMetaData(...) · analyzePages()",
                    size=14, fill="#eef2f7", stroke=NEG))
    f.append(arrow(444, 185, 514, 185))

    # ряд 2 — набір можливостей
    f.append(fitbox(60, 310, 380, 140,
                    "QGroundControl.corePlugin\n.options\n\n.showFirmwareUpgrade\n.missionWaypointsOnly",
                    size=14, fill="#f8fafc"))
    f.append(fitbox(520, 310, 600, 140,
                    "QGCOptions — 27 властивостей\n\n"
                    "віртуальні bool / QString / QUrl-геттери\n"
                    "з готовим значенням за замовчуванням",
                    size=14, fill="#eef2f7", stroke=NEG))
    f.append(arrow(444, 380, 514, 380))
    f.append(arrow(820, 272, 820, 306))
    f.append(text(884, 294, "options()", size=13, color=MUTED, anchor="start"))

    # ряд 3 — політний вид
    f.append(fitbox(60, 490, 380, 110,
                    "…corePlugin.options.flyView\n\n.guidedBarShowOrbit",
                    size=14, fill="#f8fafc"))
    f.append(fitbox(520, 490, 600, 110,
                    "QGCFlyViewOptions — 6 властивостей\nлише про політний вид",
                    size=14, fill="#eef2f7", stroke=NEG))
    f.append(arrow(444, 545, 514, 545))
    f.append(arrow(820, 452, 820, 486))
    f.append(text(884, 474, "flyViewOptions()", size=13, color=MUTED, anchor="start"))

    f.append(text(W / 2, 626,
                  "властивість зветься flyView, а геттер — flyViewOptions(): імена навмисно різні",
                  size=14, bold=True))
    render(os.path.join(OUT, 'api-options-graph.svg'), W, H, *f)


# ── 5. [вставка api] CONSTANT проти NOTIFY ─────────────────────────────────
def api_constant_vs_notify():
    W, H = 1180, 580
    f = []
    f.append(text(W / 2, 36, "CONSTANT чи NOTIFY: чому половина перемикачів не діє після старту",
                  size=18, bold=True))
    f.append(mtext(620, 76, "подія: showAdvancedUI стає true\n(п'ять натисків по кнопці)",
                   size=13, color=MUTED))
    f.append(line(620, 116, 620, 496, color=MUTED, sw=2, dash="7 6"))

    # смуга 1 — CONSTANT
    f.append(fitbox(40, 140, 280, 130,
                    "CONSTANT\n\nshowInstrumentPanel\nshowMapScale\ncombineSettingsAndSetup\n"
                    "guidedActionsRequireRCRSSI",
                    size=13, fill="#eef2f7"))
    f.append(fitbox(340, 140, 260, 130,
                    "QML читає значення\nодин раз — коли\nбудує прив'язку",
                    size=13, fill="#ffffff"))
    f.append(fitbox(660, 140, 480, 130,
                    "сигналу немає — прив'язка не переобчислюється:\n"
                    "елемент лишається таким, яким був на старті",
                    size=13, fill="#fdecea", stroke=POS))

    # смуга 2 — NOTIFY
    f.append(fitbox(40, 330, 280, 130,
                    "NOTIFY\n\nshowFirmwareUpgrade\nshowSensorCalibration*\nmissionWaypointsOnly\n"
                    "guidedBarShowOrbit",
                    size=13, fill="#eef2f7"))
    f.append(fitbox(340, 330, 260, 130,
                    "QML читає значення\nі підписується\nна сигнал зміни",
                    size=13, fill="#ffffff"))
    f.append(fitbox(660, 330, 480, 130,
                    "твій emit …Changed → прив'язка переобчислюється:\n"
                    "елемент з'являється або зникає на льоту",
                    size=13, fill="#eaf0fd", stroke=NEG))

    f.append(arrow(340, 492, 1140, 492))
    f.append(text(760, 514, "час роботи застосунку", size=13, color=MUTED))
    f.append(text(W / 2, 556,
                  "CONSTANT — обіцянка QML, що значення ніколи не зміниться",
                  size=15, bold=True))
    render(os.path.join(OUT, 'api-constant-vs-notify.svg'), W, H, *f)


# ── 6. Чотири ворота в коді: механізм і наслідок (вставка proj) ─────────────
def proj_four_gates_code():
    W, H = 1380, 700
    f = []

    cols = [(40, 230), (290, 360), (670, 250), (940, 400)]
    heads = ["Ворота", "Механізм у коді", "Де живе", "Наслідок для елемента"]
    for (x, w), t in zip(cols, heads):
        f.append(fitbox(x, 56, w, 40, t, size=15, bold=True, fill="#e6ebf2"))

    rows = [
        (["1 · ЗБІРКА", "чи передбачено", "для цієї аудиторії"],
         ["власний геттер на", "CustomOptions", "(Q_PROPERTY, CONSTANT)"],
         ["C++, CustomPlugin.h", "вирішує компілятор"],
         ["visible = false", "елемента НЕМА:", "у застосунку не існує"],
         "#fdecea", POS),
        (["2 · РОЛЬ", "чи людина зараз", "налаштувальник"],
         ["corePlugin.showAdvancedUI", "(NOTIFY; у власній збірці", "стартує з false)"],
         ["QML-прив'язка", "у FlyViewCustomLayer"],
         ["visible = true", "елемент З'ЯВЛЯЄТЬСЯ", "після ввімкнення режиму"],
         "#fdecea", POS),
        (["3 · СТАН", "чи дія має сенс", "саме зараз"],
         ["activeVehicle", "  ? !activeVehicle.armed", "  : false"],
         ["QML-прив'язка", "до об'єкта апарата"],
         ["enabled = false", "елемент ВИДНО, але він", "сірий, і поруч причина"],
         "#eef2f7", LINE),
        (["4 · НАМІР", "чи ти справді", "цього хотів"],
         ["SliderSwitch.onAccept", "сигнал лише після", "повного проведення"],
         ["QML, штатний елемент", "QGroundControl.Controls"],
         ["виклик C++, який звіряє", "ворота 1-3 ще раз", "і шле команду на борт"],
         "#eaf0fd", NEG),
    ]

    y = 115
    for c1, c2, c3, c4, fill4, st4 in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], 120, "\n".join(c1), size=13, fill="#f8fafc"))
        f.append(fitbox(cols[1][0], y, cols[1][1], 120, "\n".join(c2), size=13, fill="#ffffff"))
        f.append(fitbox(cols[2][0], y, cols[2][1], 120, "\n".join(c3), size=13, fill="#ffffff"))
        f.append(fitbox(cols[3][0], y, cols[3][1], 120, "\n".join(c4), size=13, fill=fill4, stroke=st4))
        y += 134

    f.append(text(W / 2, 668,
                  "перші двоє воріт ховають · треті блокують і пояснюють · четверті питають",
                  size=15, bold=True))
    render(os.path.join(OUT, 'proj-four-gates-code.svg'), W, H, *f,
           title="Чотири ворота: чим вмикається кожне і що бачить людина")


# ── 7. Три рівні: ховає / відмовляє / забороняє (вставка proj) ──────────────
def proj_three_layers():
    W, H = 1120, 640
    f = []

    bands = [
        (100, "Рівень 1 · QML — ХОВАЄ",
         ["ловить: випадкове блукання оператора не тим екраном",
          "не ловить: жодного виклику поза цим файлом"], "#eef2f7", LINE),
        (270, "Рівень 2 · C++ Q_INVOKABLE — ВІДМОВЛЯЄ",
         ["ловить: чужий виклик із QML і власну забуту умову",
          "не ловить: нічого, що йде повз цей застосунок"], "#eaf0fd", NEG),
        (440, "Рівень 3 · автопілот — ЗАБОРОНЯЄ",
         ["ловить: усе, бо перевіряє стан у себе, а не вірить на слово",
          "MAV_CMD_PREFLIGHT_STORAGE у польоті → COMMAND_ACK: DENIED"], "#e8f6ee", FIELD),
    ]

    for y, head, body, fill, st in bands:
        f.append(rect(60, y, 620, 120, fill=fill, stroke=st, sw=2))
        f.append(text(370, y + 34, head, size=16, bold=True))
        f.append(mtext(370, y + 64, body, size=13, color=INK))

    f.append(text(370, 76, "оператор власної збірки", size=14, color=MUTED))
    f.append(arrow(370, 82, 370, 96))
    f.append(arrow(370, 224, 370, 266))
    f.append(arrow(370, 394, 370, 436))

    f.append(fitbox(760, 180, 320, 110,
                    "інша станція,\nконсоль до борту,\nвласний скрипт",
                    size=14, fill="#fff6e5", stroke=MUTED))
    f.append(line(1040, 292, 1040, 500, color=MUTED, sw=2, dash="6,4"))
    f.append(arrow(1040, 500, 690, 500, color=MUTED))
    f.append(text(865, 484, "обходить обидва рівні станції", size=13, color=MUTED))

    f.append(text(W / 2, 604,
                  "забороняє лише той, хто перевіряє в себе, а не той, кого просять",
                  size=15, bold=True))
    render(os.path.join(OUT, 'proj-three-layers.svg'), W, H, *f,
           title="Три рівні між кнопкою і виконаною командою")


two_screens()
day_and_roles()
four_gates()
api_options_graph()
api_constant_vs_notify()
proj_four_gates_code()
proj_three_layers()
print("ok")
