# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чотири канали одиниці під перевіркою ───────────────────────────
def fig_contract_channels():
    W, H = 1080, 610
    f = []

    test_b, tw, th = textbox(160, 200, "ТЕСТ\n(твої руки)", size=14, bold=True,
                             fill="#eafaf1", stroke=FIELD, sw=2.2, pad=12, min_w=190)
    sut_b, sw_, sh_ = textbox(560, 200, "Одиниця під перевіркою", size=15, bold=True,
                              fill="#fffbea", stroke=INK, sw=2.4, pad=18, min_w=300)
    col_b, cw_, ch_ = textbox(560, 470, "Справжній співавтор\n(база, шлюз, годинник)",
                              size=14, bold=True, fill=FILL, stroke=MUTED, sw=2,
                              pad=12, min_w=340)

    # прямі канали — горизонтально
    f.append(arrow(160 + tw / 2 + 6, 178, 560 - sw_ / 2 - 6, 178, color=FIELD, sw=2.4))
    f.append(text(360, 162, "прямий вхід: аргументи виклику", size=12,
                  italic=True, color=MUTED))
    f.append(arrow(560 - sw_ / 2 - 6, 226, 160 + tw / 2 + 6, 226, color=FIELD, sw=2.4))
    f.append(text(360, 252, "прямий вихід: повернене значення", size=12,
                  italic=True, color=MUTED))

    # непрямі канали — вертикально
    f.append(arrow(490, 200 + sh_ / 2 + 6, 490, 470 - ch_ / 2 - 6, color=POS, sw=2.6))
    f.append(arrow(630, 470 - ch_ / 2 - 6, 630, 200 + sh_ / 2 + 6, color=NEG, sw=2.6))

    out_b, ow, oh = textbox(180, 300, "НЕПРЯМИЙ ВИХІД\nщо одиниця каже світові\n"
                                      "тут ТОЧКА СПОСТЕРЕЖЕННЯ",
                            size=12.5, bold=True, fill="#fdecea", stroke=POS,
                            sw=2, pad=11, min_w=280)
    f.append(line(180 + ow / 2, 300, 490, 300, color=POS, sw=1.4))
    f.append(out_b)

    in_b, iw, ih = textbox(900, 386, "НЕПРЯМИЙ ВХІД\nщо одиниця чує від світу\n"
                                     "тут ТОЧКА КЕРУВАННЯ",
                           size=12.5, bold=True, fill="#eaf0fd", stroke=NEG,
                           sw=2, pad=11, min_w=280)
    f.append(line(630, 386, 900 - iw / 2, 386, color=NEG, sw=1.4))
    f.append(in_b)

    f.append(test_b)
    f.append(sut_b)
    f.append(col_b)

    bot, bw, bh = textbox(560, 560,
                          "Прямі канали тест тримає сам. До непрямих він дістає лише тим,\n"
                          "що підставляє замість співавтора, — дублером.",
                          size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=11)
    f.append(bot)
    render(os.path.join(IMG, 'contract-channels.svg'), W, H, *f,
           title="Чотири канали, якими одиниця обмінюється зі світом")


# ── Фігура 2: карта дублерів за двома осями ──────────────────────────────────
def fig_double_map():
    W, H = 1200, 700
    f = []

    gx, gy = 320, 160          # ліво-верх сітки
    cw, chh = 285, 145         # клітинка
    cols = [gx, gx + cw + 8, gx + 2 * (cw + 8)]
    rows = [gy, gy + chh + 8, gy + 2 * (chh + 8)]

    f.append(text(W / 2, 42, "Дублер — це відповідь на два незалежні питання",
                  size=16, bold=True))

    # заголовок осі X
    f.append(text(gx + 1.5 * cw + 8, 78,
                  "чи КЕРУЄ тест тим, що одиниця чує  →",
                  size=13, bold=True, color=NEG))
    heads = ["дубль нічого\nне відповідає",
             "готова відповідь,\nяку задав тест",
             "справжня логіка,\nтільки спрощена"]
    for x, hd in zip(cols, heads):
        f.append(fitbox(x, 96, cw, 52, hd, size=12.5, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.6, pad=8))

    # заголовок осі Y (кут сітки) + підписи рядків
    f.append(fitbox(50, 96, 250, 52, "↑ чи ДАЄ ПОБАЧИТИ,\nщо одиниця каже",
                    size=12.5, bold=True, fill="#fdecea", stroke=POS, sw=1.6, pad=8))
    ylabels = ["несе очікування\nНАПЕРЕД —\nсудить себе сам",
               "записує виклики —\nзвіряєш їх ти\nПІСЛЯ дії",
               "не дивиться,\nкого й з чим кликали"]
    for y, yl in zip(rows, ylabels):
        f.append(fitbox(50, y + 20, 250, chh - 40, yl, size=12.5, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.6, pad=8))

    # нижній рядок — три дублери, що нічого не спостерігають
    bottom = [("ПУСТУШКА\n(dummy)", "аби заповнити\nпорожній параметр"),
              ("ЗАГЛУШКА\n(stub)", "подає одиниці\nзаготований вхід"),
              ("ФЕЙК\n(fake)", "робоча реалізація\nна спрощеній основі")]
    for x, (name, role) in zip(cols, bottom):
        f.append(rect(x, rows[2], cw, chh, fill="#f7fbff", stroke=NEG, sw=1.8))
        f.append(fitbox(x + 14, rows[2] + 14, cw - 28, 48, name, size=14, bold=True,
                        fill=BG, stroke=NEG, sw=1.5, pad=6))
        f.append(fitbox(x + 14, rows[2] + 74, cw - 28, 54, role, size=12,
                        fill=BG, stroke=MUTED, sw=1.2, pad=6))

    # два верхні рядки — шпигун і мок, що розтягуються на дві колонки
    span_w = 2 * cw + 8
    spans = [(rows[0], "МОК (mock)",
              "Очікування задані до дії; сам валить тест,\n"
              "щойно виклик не той або зайвий."),
             (rows[1], "ШПИГУН (spy)",
              "Мовчки веде журнал викликів;\nвирок виносиш ти після дії.")]
    for y, name, role in spans:
        f.append(rect(cols[0], y, span_w, chh, fill="#fff8f7", stroke=POS, sw=1.8))
        f.append(fitbox(cols[0] + 16, y + 16, span_w - 32, 46, name, size=14.5,
                        bold=True, fill=BG, stroke=POS, sw=1.5, pad=6))
        f.append(fitbox(cols[0] + 16, y + 74, span_w - 32, 54, role, size=12.5,
                        fill=BG, stroke=MUTED, sw=1.2, pad=7))

    # права колонка вгорі — клітинки без усталеної назви
    f.append(fitbox(cols[2], rows[0], cw, 2 * chh + 8,
                    "Ці дві клітинки теж\nтрапляються: фейк,\nщо веде журнал\nвикликів.\n\n"
                    "Усталеної назви їм\nне дали — важить\nне назва, а дві осі.",
                    size=12, fill="#f6f6f6", stroke=MUTED, sw=1.4, pad=10))

    bot, bw, bh = textbox(W / 2, 640,
                          "Питання не «який дубль модніший», а: чи треба керувати тим, що одиниця чує,\n"
                          "і чи треба бачити те, що вона каже.",
                          size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=11)
    f.append(bot)
    render(os.path.join(IMG, 'double-map.svg'), W, H, *f, title=None)


# ── Фігура 3: зазор вірності — що доводить зелений тест ──────────────────────
def fig_fidelity_gap():
    W, H = 1180, 610
    f = []
    f.append(text(W / 2, 40, "Зелений тест із дублем доводить рівно одне",
                  size=16, bold=True))

    # ── ліва половина: перенесення висновку
    f.append(rect(50, 78, 570, 140, fill="#f0fbf4", stroke="#cfeadd", sw=1.4, rx=14))
    f.append(text(335, 104, "Що показав зелений тест", size=14, bold=True, color=FIELD))
    u1, uw, uh = textbox(180, 172, "одиниця", size=13.5, bold=True,
                         fill="#fffbea", stroke=INK, sw=2, pad=11, min_w=180)
    d1, dw, dh = textbox(470, 172, "ДУБЛЬ D", size=13.5, bold=True,
                         fill=FILL, stroke=FIELD, sw=2.2, pad=11, min_w=180)
    f.append(arrow(180 + uw / 2 + 4, 172, 470 - dw / 2 - 4, 172, color=FIELD, sw=2.2))
    f += [u1, d1]

    f.append(rect(50, 300, 570, 140, fill="#f2f6ff", stroke="#d5e0f7", sw=1.4, rx=14))
    f.append(text(335, 326, "Що тобі потрібно в бою", size=14, bold=True, color=NEG))
    u2, uw2, uh2 = textbox(180, 394, "одиниця", size=13.5, bold=True,
                           fill="#fffbea", stroke=INK, sw=2, pad=11, min_w=180)
    r2, rw2, rh2 = textbox(470, 394, "СПРАВЖНІЙ R", size=13.5, bold=True,
                           fill=FILL, stroke=NEG, sw=2.2, pad=11, min_w=180)
    f.append(arrow(180 + uw2 / 2 + 4, 394, 470 - rw2 / 2 - 4, 394, color=NEG, sw=2.2))
    f += [u2, r2]

    f.append(arrow(335, 226, 335, 292, color=MUTED, sw=2.4))
    j1, jw, jh = textbox(140, 259, "перенесення\nвисновку", size=11.5, bold=True,
                         fill=BG, stroke=MUTED, sw=1.4, pad=9)
    f.append(j1)
    j2, jw2, jh2 = textbox(492, 259,
                           "законне ЛИШЕ якщо D тримає\nтой самий контракт, що R,\n"
                           "у частині, якою одиниця користується",
                           size=11.5, bold=True, fill="#fbfbfb", stroke=INK, sw=1.5, pad=9)
    f.append(j2)

    # ── права половина: чим зазор проривається
    f.append(text(910, 104, "Чим зазор вірності проривається", size=14, bold=True, color=POS))
    gaps = ["Дубль не вміє падати —\nгілку помилки тест ніби перевіряє, а насправді ні",
            "Дубль дозволяє те, чого справжній не дозволить:\nунікальність, транзакцію, порядок",
            "Справжній змінився —\nдубль лишився вчорашнім",
            "Дубль на ЧУЖОМУ кодує лише\nтвій здогад про чужий контракт"]
    gy0 = 128
    for i, g in enumerate(gaps):
        f.append(fitbox(660, gy0 + i * 66, 470, 56, g, size=12,
                        fill="#fff8f7", stroke=POS, sw=1.5, pad=8))

    f.append(fitbox(660, 412, 470, 92,
                    "Стягує зазор один хід: той самий набір перевірок\n"
                    "ганяють і на дублі, і на справжньому.\n"
                    "Це контрактний тест — єдине, що вміє сказати,\n"
                    "що дубль іще не збрехав.",
                    size=12.5, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10))

    bot, bw, bh = textbox(W / 2, 560,
                          "Тест із дублем показує: одиниця працює з ДУБЛЕМ. "
                          "Про справжнього він мовчить.",
                          size=13.5, bold=True, fill="#fbfbfb", stroke=INK, sw=1.8, pad=11)
    f.append(bot)
    render(os.path.join(IMG, 'fidelity-gap.svg'), W, H, *f, title=None)


# ── Фігура 4 (вставка hist): як розповзалося слово «мок» ────────────────────
def fig_mock_word_timeline():
    W, H = 1240, 900
    f = []
    f.append(text(W / 2, 40, "Прийом стояв на місці — слово поїхало", size=17, bold=True))

    axis_x = 214
    top, bot_y = 92, 726
    f.append(line(axis_x, top, axis_x, bot_y, color=MUTED, sw=3))

    steps = [
        ("червень\n2000", NEG,
         "XP2000, Кальярі (Сардинія): доповідь «Endo-Testing»",
         "Мок — підміна, що НЕСЕ В СОБІ очікування й судить сама,\n"
         "просто в мить неправильного виклику."),
        ("2001", NEG,
         "EasyMock: мок більше не пишуть руками",
         "Динамічний заступник під інтерфейс, режим «запис — відтворення».\n"
         "Ціна створення дубля падає майже до нуля."),
        ("липень\n2004", MUTED,
         "Фаулер, «Mocks Aren't Stubs»",
         "Дві школи розведені: класична звіряє стан,\n"
         "мокістська — взаємодію. Слово вже потребує тлумача."),
        ("жовтень\n2004", NEG,
         "OOPSLA, Ванкувер: «Mock Roles, not Objects»",
         "Самі автори друкують, що назва невдала: суть не в підміні,\n"
         "а у відкритті вузьких ролей. З'являється jMock."),
        ("2007", MUTED,
         "Мезарош, xUnit Test Patterns",
         "Спільне ім'я для всіх підмін — тестовий дублер.\n"
         "Мок стає однією з п'яти назв, а не парасолькою."),
        ("2008", POS,
         "Mockito, а слідом gMock",
         "mock() дає дубля даром. Роль вирішує вже не назва об'єкта,\n"
         "а те, чи покликав ти verify() наприкінці."),
    ]

    y = 118
    bx, bw = 268, 936
    for label, col, head, body in steps:
        bh = 92
        f.append(circle(axis_x, y + bh / 2, 9, fill=BG, stroke=col, sw=3))
        f.append(line(axis_x + 10, y + bh / 2, bx - 6, y + bh / 2, color=col, sw=1.6))
        f.append(mtext(112, y + bh / 2 - (label.count("\n")) * 7 + 5, label,
                       size=13, bold=True, color=MUTED))
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=1.8, rx=8))
        f.append(fitbox(bx + 14, y + 10, bw - 28, 30, head,
                        size=14, bold=True, fill=FILL, stroke=col, sw=1.3, pad=8))
        f.append(fitbox(bx + 14, y + 46, bw - 28, 36, body,
                        size=12.5, fill=BG, stroke=MUTED, sw=1.1, pad=7))
        y += bh + 14

    f.append(fitbox(60, 760, 560, 100,
                    "ЩО МАЛИ НА УВАЗІ АВТОРИ\n\n"
                    "Спосіб вести проєктування: тест називає роль,\n"
                    "якої одиниця потребує, — і роль стає вузьким інтерфейсом.",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8, pad=12))
    f.append(fitbox(640, 760, 540, 100,
                    "ЩО СЛОВО ОЗНАЧАЄ ТЕПЕР\n\n"
                    "Будь-яка підміна в тесті, зроблена бібліотекою, —\n"
                    "незалежно від того, яку роль вона насправді грає.",
                    size=13, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=12))

    render(os.path.join(IMG, 'mock-word-timeline.svg'), W, H, *f, title=None)


# ── Фігура (вставка proj-cpp-doubles): два шви на одному вузлі й їх ціна ────
def fig_seams_two_costs():
    W, H = 1300, 830
    f = []
    f.append(text(W / 2, 42, "Один текст sendFrame — два шви, дві різні програми",
                  size=17, bold=True))

    top, tw, th = textbox(W / 2, 104,
                          "template <class Transport>   —   ОДИН текст у заголовку\n"
                          "Uplink<Transport>::sendFrame(frame)",
                          size=14, bold=True, fill="#fffbea", stroke=INK, sw=2.2,
                          pad=14, min_w=780)
    f.append(top)

    LX, RX, CW = 60, 700, 540

    # ── заголовки стовпців
    f.append(fitbox(LX, 168, CW, 62,
                    "Transport = ITransport\nШОВ У ТАБЛИЦІ ВІРТУАЛЬНИХ МЕТОДІВ",
                    size=14, bold=True, fill="#eaf0fd", stroke=NEG, sw=2.2, pad=10))
    f.append(fitbox(RX, 168, CW, 62,
                    "Transport = UdpTransport | FakeTransport | SpyTransport\n"
                    "ШОВ У ТИПІ (шаблонний параметр)",
                    size=14, bold=True, fill="#eafaf1", stroke=FIELD, sw=2.2, pad=10))

    # ── механіка
    f.append(fitbox(LX, 252, CW, 132,
                    "ціль виклику знаходять у РАНТАЙМІ:\n"
                    "\n"
                    "mov  rax, [rdi]          ; vptr об'єкта\n"
                    "call [rax + 16]          ; слот send",
                    size=13.5, fill=BG, stroke=MUTED, sw=1.6, pad=12))
    f.append(fitbox(RX, 252, CW, 132,
                    "ціль відома КОМПІЛЯТОРОВІ; на кожен тип\n"
                    "постає окрема копія функції:\n"
                    "\n"
                    "sendFrame⟨Udp⟩   sendFrame⟨Fake⟩   sendFrame⟨Spy⟩",
                    size=13.5, fill=BG, stroke=MUTED, sw=1.6, pad=12))

    # ── головний наслідок
    f.append(fitbox(LX, 400, CW, 82,
                    "тіло send лишається окремою функцією —\n"
                    "компілятор не бачить, куди веде стрибок",
                    size=13.5, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=10))
    f.append(fitbox(RX, 400, CW, 82,
                    "mtu() згортається в константу,\n"
                    "тіло send зливається з циклом",
                    size=13.5, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10))

    # ── ціна
    f.append(fitbox(LX, 500, CW, 190,
                    "+  підміна в РАНТАЙМІ: транспорт із конфіга\n"
                    "+  одна копія коду на всі транспорти\n"
                    "+  реалізація ховається в .cpp\n"
                    "−  немає вбудовування й згортання констант\n"
                    "−  промах предиктора — перезапуск конвеєра\n"
                    "−  дубль МУСИТЬ успадкувати ITransport",
                    size=13.5, fill="#f7fbff", stroke=NEG, sw=1.8, pad=14))
    f.append(fitbox(RX, 500, CW, 190,
                    "+  прямий виклик, вбудовування, згортання\n"
                    "+  дублеві досить мати методи потрібної форми\n"
                    "+  можна обійтися без віртуальних викликів зовсім\n"
                    "−  окрема копія коду на КОЖЕН тип: тиск на кеш\n"
                    "−  реалізація в заголовку: масова перезбірка\n"
                    "−  підміни в рантаймі немає взагалі",
                    size=13.5, fill="#f4fbf7", stroke=FIELD, sw=1.8, pad=14))

    bot, bw, bh = textbox(W / 2, 762,
                          "Дублер живе там, де шов. Який шов прорізали — такі й вимоги до дубля:\n"
                          "підтип ITransport ліворуч, просто потрібна форма методів праворуч.",
                          size=13.5, bold=True, fill="#fbfbfb", stroke=INK, sw=1.8, pad=12)
    f.append(bot)
    render(os.path.join(IMG, 'seams-two-costs.svg'), W, H, *f, title=None)


# ── Фігура (вставка proj-cpp-doubles): контрактний набір на дві смуги ───────
def fig_contract_suite_lanes():
    W, H = 1240, 690
    f = []
    f.append(text(W / 2, 42, "Один набір тверджень — стільки смуг, скільки реалізацій",
                  size=17, bold=True))

    LX, LW = 55, 480
    RX, RW = 690, 500

    f.append(fitbox(LX, 92, LW, 64,
                    "НАБІР ТВЕРДЖЕНЬ ПРО КОНТРАКТ ТРАНСПОРТУ\n"
                    "TYPED_TEST_SUITE_P — один текст",
                    size=13.5, bold=True, fill="#fffbea", stroke=INK, sw=2.2, pad=10))
    f.append(fitbox(LX, 174, LW, 190,
                    "•  mtu() більший за нуль\n"
                    "•  шматок рівно на MTU приймається\n"
                    "•  шматок понад MTU — Fatal\n"
                    "•  поки ніхто не вичитує, транспорт\n"
                    "    зрештою відповідає WouldBlock",
                    size=13.5, fill=BG, stroke=MUTED, sw=1.6, pad=14))
    f.append(fitbox(LX, 382, LW, 78,
                    "тіла торкаються ЛИШЕ mtu() і send() —\n"
                    "тому компілюються для БУДЬ-ЯКОЇ реалізації",
                    size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=10))

    f.append(arrow(LX + LW + 14, 205, RX - 14, 172, color=FIELD, sw=2.6))
    f.append(arrow(LX + LW + 14, 300, RX - 14, 342, color=NEG, sw=2.6))

    f.append(fitbox(RX, 118, RW, 108,
                    "ШВИДКА СМУГА\n"
                    "INSTANTIATE_TYPED_TEST_SUITE_P⟨FakeTransport⟩\n"
                    "кожен коміт · мілісекунди · без мережі",
                    size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2.2, pad=12))
    f.append(fitbox(RX, 288, RW, 108,
                    "ПОВІЛЬНА СМУГА\n"
                    "INSTANTIATE_TYPED_TEST_SUITE_P⟨UdpLoopback⟩\n"
                    "нічний прогін · справжній сокет",
                    size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2.2, pad=12))
    f.append(fitbox(RX, 428, RW, 112,
                    "Червона повільна при зеленій швидкій\n"
                    "означає рівно одне: фейк збрехав\n"
                    "саме в цьому рядку контракту.",
                    size=13, bold=True, fill="#fdecea", stroke=POS, sw=1.8, pad=12))

    bot, bw, bh = textbox(W / 2, 626,
                          "Без повільної смуги фейк тихо старіє — а разом із ним\n"
                          "старіють усі швидкі тести, що на ньому стоять.",
                          size=13.5, bold=True, fill="#fbfbfb", stroke=INK, sw=1.8, pad=12)
    f.append(bot)
    render(os.path.join(IMG, 'contract-suite-two-lanes.svg'), W, H, *f, title=None)


if __name__ == "__main__":
    fig_contract_channels()
    fig_double_map()
    fig_fidelity_gap()
    fig_mock_word_timeline()
    fig_seams_two_costs()
    fig_contract_suite_lanes()
    print("figures written to", IMG)
