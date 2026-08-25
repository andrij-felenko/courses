# -*- coding: utf-8 -*-
"""Фігури до теми «Гарантії безпеки винятків: базова, сильна, nothrow»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Приховані виходи з функції ──────────────────────────────────────────
def fig_throw_points():
    W, H = 980, 380
    f = []

    f.append(rect(40, 52, 470, 262, fill="#f8f9fb", stroke=MUTED, sw=1))
    code = [
        (84,  "void Widget::reset(const std::string& name) {"),
        (114, "    delete impl_;"),
        (144, "    impl_ = nullptr;"),
        (174, "    impl_ = new Impl(name);"),
        (204, "    log_.push_back(name);"),
        (234, "    ready_ = true;"),
        (264, "}"),
    ]
    for y, s in code:
        f.append(text(58, y, s, size=13, anchor="start"))

    f.append(arrow(516, 172, 552, 146, color=POS))
    f.append(arrow(516, 206, 552, 232, color=POS))

    f.append(fitbox(556, 106, 384, 78,
                    "new може кинути bad_alloc\n→ impl_ лишився nullptr,\nа ready_ усе ще каже «готовий»",
                    size=12, fill="#fdecea", stroke=POS))
    f.append(fitbox(556, 196, 384, 78,
                    "push_back може кинути bad_alloc\n→ реалізація вже нова,\nа журнал про неї не знає",
                    size=12, fill="#fdecea", stroke=POS))

    f.append(text(490, 348,
                  "жодного витоку пам'яті немає — зламано інваріант «ready_ означає, що impl_ дійсний»",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'throw-points.svg'), W, H, *f,
           title="У тексті один вихід із функції, насправді — три")


# ── 2. Що правда після винятку і що з цим можна зробити ────────────────────
def fig_levels():
    W, H = 1000, 476
    f = []

    C1X, C1W = 40, 190
    C2X, C2W = 240, 350
    C3X, C3W = 600, 360

    f.append(fitbox(C1X, 52, C1W, 38, "рівень", size=13,
                    fill="#eceff3", color=MUTED, bold=True))
    f.append(fitbox(C2X, 52, C2W, 38, "що правда після винятку", size=13,
                    fill="#eceff3", color=MUTED, bold=True))
    f.append(fitbox(C3X, 52, C3W, 38, "що дозволено тому, хто викликав", size=13,
                    fill="#eceff3", color=MUTED, bold=True))

    rows = [
        (98, "жодної", "#fdecea", POS,
         "нічого не відомо: можливі витік ресурсу,\nзламаний інваріант, подвійне звільнення",
         "нічого безпечного — навіть знищити\nоб'єкт може виявитися фатальним"),
        (180, "базова", "#f4f6f8", LINE,
         "ресурси не втрачені, інваріанти класу тримаються,\nале яке саме значення всередині — не сказано",
         "знищити, присвоїти нове, викликати\nоперації без передумов"),
        (262, "сильна", "#eaf0fd", NEG,
         "або операція сталася вся,\nабо стан такий самий, як був до виклику",
         "повторити ту саму спробу\nна тому самому об'єкті"),
        (344, "nothrow", "#e8f6ee", FIELD,
         "операція завершилася успіхом;\nвинятку звідси не буває взагалі",
         "покластися на неї в чужому відкаті\nй у деструкторі"),
    ]
    RH = 74
    for y, name, fill, stroke, what, allowed in rows:
        f.append(fitbox(C1X, y, C1W, RH, name, size=15, fill=fill, stroke=stroke, bold=True))
        f.append(fitbox(C2X, y, C2W, RH, what, size=12, fill="#fbfcfd"))
        f.append(fitbox(C3X, y, C3W, RH, allowed, size=12, fill="#fbfcfd"))

    f.append(text(500, 452,
                  "наступний рівень — не «акуратніше написано», а інша обіцянка й інша ціна",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'levels.svg'), W, H, *f,
           title="Чотири різні відповіді на питання «що лишилося після винятку»")


# ── 3. Лінія фіксації — устрій сильної гарантії ────────────────────────────
def fig_commit_line():
    W, H = 980, 412
    f = []

    f.append(text(490, 54, "лінія фіксації", size=13, color=POS, bold=True))
    f.append(line(490, 66, 490, 352, color=POS, sw=2, dash="7 5"))

    f.append(text(250, 92, "до неї — працюємо збоку", size=14, bold=True))
    f.append(text(730, 92, "після неї — робимо видимим", size=14, bold=True))

    f.append(fitbox(50, 104, 400, 108,
                    "усе, що здатне кинути:\nвиділення пам'яті, копії рядків,\nпобудова нового вмісту —\nу тимчасовому об'єкті збоку",
                    size=12.5))
    f.append(fitbox(530, 104, 400, 108,
                    "усе, що кинути не здатне:\nобмін вказівниками, присвоєння чисел,\nswap, помічений noexcept —\nнад справжнім об'єктом",
                    size=12.5))

    f.append(arrow(250, 216, 250, 246))
    f.append(arrow(730, 216, 730, 246))

    f.append(fitbox(50, 248, 400, 86,
                    "виняток тут: видимий об'єкт\nне змінювався ані на біт,\nвідкочувати нічого",
                    size=12.5, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(530, 248, 400, 86,
                    "виняток тут неможливий за побудовою —\nінакше об'єкт застряг би\nміж двома станами",
                    size=12.5, fill="#eaf0fd", stroke=NEG))

    f.append(text(490, 386,
                  "сильна гарантія існує рівно там, де фіксацію вдається скласти з операцій, які не кидають",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'commit-line.svg'), W, H, *f,
           title="Устрій сильної гарантії: спершу все ризиковане, потім безризикова фіксація")


# ── 4. Чому сильна гарантія не складається сама собою ──────────────────────
def fig_compose():
    W, H = 960, 396
    f = []

    f.append(fitbox(40, 74, 250, 64, "крок 1: списати з A\nсильна гарантія", size=12.5))
    f.append(arrow(294, 106, 332, 106))
    f.append(fitbox(336, 74, 250, 64, "крок 2: зарахувати на B\nсильна гарантія", size=12.5))
    f.append(arrow(590, 106, 628, 106, color=POS))
    f.append(fitbox(632, 74, 250, 64, "виняток", size=15,
                    fill="#fdecea", stroke=POS, bold=True))

    f.append(arrow(757, 142, 757, 172))
    f.append(fitbox(500, 174, 382, 76,
                    "крок 2 відкотив сам себе,\nа крок 1 уже стався —\nразом це лише базова гарантія",
                    size=12.5, fill="#fdecea", stroke=POS))

    f.append(line(40, 274, 920, 274, color=MUTED, sw=1, dash="6 5"))

    f.append(fitbox(40, 296, 400, 76,
                    "щоб склалося в сильну, потрібен\nвідкат кроку 1, який сам\nне має права кинути",
                    size=12.5, fill="#e8f6ee", stroke=FIELD))
    f.append(arrow(446, 334, 494, 334))
    f.append(fitbox(500, 296, 382, 76,
                    "охоронець області: деструктор\nповертає списане, якщо до кінця\nтак і не дійшли",
                    size=12.5, fill="#e8f6ee", stroke=FIELD))

    render(os.path.join(OUT, 'compose.svg'), W, H, *f,
           title="Дві сильні операції поспіль дають лише базову")


# ── 5. Шлях від виклику Каргіла до тексту стандарту (вставка hist) ─────────
def fig_history_line():
    W, H = 1020, 470
    f = []

    Y = 120
    f.append(line(60, Y, 960, Y, color=MUTED, sw=2))

    marks = [
        (140, "жовтень 1993", "Девід Рід, колонка\nв «C++ Report»:\nвинятки — це добре"),
        (330, "лист.–груд. 1994", "Том Каргіл, «Exception\nHandling: A False Sense\nof Security» — розбір Stack<T>\nі відкритий виклик"),
        (560, "1997", "Дейв Абрагамс і Ґреґ Колвін,\nдокументи комітету N1075,\nN1086, N1114; серія\nГерба Саттера в «C++ Report»"),
        (790, "27.04–01.05.1998", "Дагштульський семінар\nз узагальненого програмування:\n«Exception-Safety in Generic\nComponents» (Springer, 2000)"),
    ]
    fills = ["#eceff3", "#fdecea", "#e8f0fd", "#e8f6ee"]
    strokes = [MUTED, POS, NEG, FIELD]

    for i, (x, when, what) in enumerate(marks):
        f.append(circle(x, Y, 8, fill=strokes[i], stroke=strokes[i]))
        f.append(text(x, Y - 26, when, size=13, bold=True))
        f.append(line(x, Y + 10, x, Y + 40, color=MUTED, sw=1, dash="4 4"))
        f.append(fitbox(x - 105, Y + 44, 210, 118, what,
                        size=11.5, fill=fills[i], stroke=strokes[i]))

    f.append(fitbox(60, 320, 900, 46,
                    "ідея (щось не так) → формулювання (три рівні) → текст стандарту ISO/IEC 14882:1998",
                    size=13, fill="#f8f9fb", stroke=MUTED))

    f.append(text(510, 410,
                  "терміни «basic», «strong», «nothrow» живуть у літературі; сам стандарт розписує",
                  size=12, color=MUTED))
    f.append(text(510, 430,
                  "ті самі обіцянки для кожної операції окремо, здебільшого не називаючи їх",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'history-line.svg'), W, H, *f,
           title="Від колонки 1993 року до формулювань стандарту")


# ── 6. Прочісування точок кидання зовнішнім циклом (вставка proj) ──────────
def fig_throw_sweep():
    W, H = 990, 432
    f = []

    LX, LW = 40, 106
    GX, CW = 160, 90
    NX, NW = 722, 248
    HDRY = 60
    ROWY0, RH, GAP = 92, 42, 6

    f.append(fitbox(LX, HDRY, LW, 28, "прогін", size=12,
                    fill="#eceff3", color=MUTED, bold=True))
    heads = ["точка 1", "точка 2", "точка 3", "точка 4", "точка 5", "кінець"]
    for j, hd in enumerate(heads):
        f.append(fitbox(GX + j * CW, HDRY, CW - 8, 28, hd, size=11,
                        fill="#eceff3", color=MUTED, bold=True))
    f.append(fitbox(NX, HDRY, NW, 28, "що з цього виходить", size=12,
                    fill="#eceff3", color=MUTED, bold=True))

    for i in range(6):                       # i = 0..5  →  N = i+1
        y = ROWY0 + i * (RH + GAP)
        f.append(fitbox(LX, y, LW, RH, "N = %d" % (i + 1), size=13, bold=True))
        for j in range(6):
            x = GX + j * CW
            if i == 5 or j < i:
                f.append(fitbox(x, y, CW - 8, RH, "пройдено", size=10,
                                fill="#e8f6ee", stroke=FIELD))
            elif j == i:
                f.append(fitbox(x, y, CW - 8, RH, "кинуло", size=11,
                                fill="#fdecea", stroke=POS, bold=True))
            else:
                f.append(fitbox(x, y, CW - 8, RH, "не дійшли", size=10,
                                fill="#f7f8fa", stroke="#d5d9de", color=MUTED))

    f.append(fitbox(NX, ROWY0, NW, 5 * RH + 4 * GAP,
                    "виняток вилетів —\nодразу три перевірки:\n\nлічильники обліку\nінваріант об'єкта\nзнімок стану до виклику",
                    size=12, fill="#fdecea", stroke=POS))
    f.append(fitbox(NX, ROWY0 + 5 * (RH + GAP), NW, RH,
                    "винятку немає → цикл спинено", size=12,
                    fill="#e8f6ee", stroke=FIELD))

    f.append(text(W / 2, 412,
                  "скільки в операції точок кидання, наперед не знає ніхто — цикл спиняється сам",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'throw-sweep.svg'), W, H, *f,
           title="Зовнішній цикл проганяє операцію стільки разів, скільки в ній точок кидання")


# ── 7. Три перевірки й що ловить кожна (вставка proj) ──────────────────────
def fig_three_checks():
    W, H = 1000, 424
    f = []

    C1X, C1W = 40, 244
    C2X, C2W = 296, 330
    C3X, C3W = 638, 322

    f.append(fitbox(C1X, 54, C1W, 34, "перевірка", size=13,
                    fill="#eceff3", color=MUTED, bold=True))
    f.append(fitbox(C2X, 54, C2W, 34, "що вона міряє", size=13,
                    fill="#eceff3", color=MUTED, bold=True))
    f.append(fitbox(C3X, 54, C3W, 34, "що ловить лише вона", size=13,
                    fill="#eceff3", color=MUTED, bold=True))

    rows = [
        (96, "лічильники обліку", "#e8f6ee", FIELD,
         "збудовано мінус знищено,\nвиділено мінус звільнено —\nобидві пари сходяться в нуль",
         "витік елемента чи блоку\nі подвійне знищення\n(лічильник іде в мінус)"),
        (190, "предикат інваріанта", "#eaf0fd", NEG,
         "твердження, яке клас\nобіцяє про себе назовні,\nпитають після винятку",
         "зламаний інваріант при\nбездоганно чистих лічильниках —\nнайтихіший з дефектів"),
        (284, "порівняння зі знімком", "#fdecea", POS,
         "стан після невдачі\nдорівнює копії, знятій\nдо самого виклику",
         "втрату сильної гарантії:\nоперація лишила слід там,\nде обіцяла не лишати"),
    ]
    RH = 84
    for y, name, fill, stroke, what, catches in rows:
        f.append(fitbox(C1X, y, C1W, RH, name, size=13,
                        fill=fill, stroke=stroke, bold=True))
        f.append(fitbox(C2X, y, C2W, RH, what, size=12, fill="#fbfcfd"))
        f.append(fitbox(C3X, y, C3W, RH, catches, size=12, fill="#fbfcfd"))

    f.append(text(W / 2, 402,
                  "жодна з трьох не заміняє двох інших: вони ловлять різні способи все зіпсувати",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'three-checks.svg'), W, H, *f,
           title="Що саме перевіряють після кожного винятку")


if __name__ == '__main__':
    fig_throw_points()
    fig_levels()
    fig_commit_line()
    fig_compose()
    fig_history_line()
    fig_throw_sweep()
    fig_three_checks()
    print("ok")
