# -*- coding: utf-8 -*-
"""Фігури до теми «Архітектура десктопного застосунку: шари, потоки, стан»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Дві доріжки й дві передачі ──────────────────────────────────────────
def lanes_handoff():
    W, H = 1060, 680
    f = []

    # доріжка «потік інтерфейсу»
    f.append(rect(40, 60, 340, 560, fill="#eef2f7", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(210, 92, "ПОТІК ІНТЕРФЕЙСУ", size=16, bold=True))

    f.append(fitbox(62, 112, 296, 48, "Черга подій", size=14))
    f.append(arrow(210, 160, 210, 182))
    f.append(fitbox(62, 182, 296, 62, "Цикл: дістати подію →\nвикликати обробник", size=13))
    f.append(arrow(210, 244, 210, 266))
    f.append(fitbox(62, 266, 296, 62, "Обробник: коротко,\nбез блокувань", size=13))
    f.append(arrow(210, 328, 210, 350))
    f.append(fitbox(62, 350, 296, 84, "СТАН (модель)\nміняється лише тут",
                    size=14, stroke=FIELD, sw=2.2, fill="#eaf7ef"))
    f.append(arrow(210, 434, 210, 456))
    f.append(fitbox(62, 456, 296, 62, "Відмальовка кадру:\nчитає знімок стану", size=13))

    # доріжка «робочі потоки»
    f.append(rect(680, 60, 340, 560, fill="#eef2f7", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(850, 92, "РОБОЧІ ПОТОКИ", size=16, bold=True))

    f.append(fitbox(702, 130, 296, 72, "Виконавець:\nдиск · мережа · обчислення", size=13))
    f.append(fitbox(702, 232, 296, 62, "Може блокуватися\nскільки треба", size=13))
    f.append(fitbox(702, 330, 296, 72, "Не має ні віджетів,\nні доступу до стану",
                    size=13, stroke=POS, sw=2.2, color=POS, fill="#fdecea"))
    f.append(fitbox(702, 440, 296, 72, "Доповідає лише\nподією в чергу", size=13))

    # передача вниз: завдання
    f.append(text(530, 214, "завдання + копія входу", size=13))
    f.append(text(530, 234, "+ ознака скасування", size=13))
    f.append(arrow(384, 258, 676, 258))

    # передача вгору: результат
    f.append(arrow(676, 358, 384, 358))
    f.append(text(530, 386, "результат — подія в чергу", size=13))
    f.append(text(530, 406, "застосує потік інтерфейсу", size=13))

    # заборонений канал
    f.append(line(676, 470, 566, 470, color=POS, sw=2.2, dash="7 5"))
    f.append(arrow(494, 470, 384, 470, color=POS, sw=2.2))
    f.append(circle(530, 470, 19, fill="#fdecea", stroke=POS, sw=2.4))
    f.append(text(530, 477, "✕", size=20, color=POS, bold=True))
    f.append(text(530, 512, "пряме чіпання віджетів", size=13, color=POS))
    f.append(text(530, 532, "чи стану — заборонено", size=13, color=POS))

    render(os.path.join(OUT, 'lanes-handoff.svg'), W, H, *f)


# ── 2. Бюджет кадру: блокуючий обробник проти передачі ─────────────────────
def frame_budget():
    W, H = 1120, 520
    X0, X1 = 200.0, 1040.0          # 0 … 500 мс
    PX = (X1 - X0) / 500.0          # px на мілісекунду
    FRAME = 16.7                    # мс на кадр при 60 Гц
    f = []

    def ticks(y, blocked=None):
        out = []
        t = 0.0
        while t <= 500.0:
            x = X0 + t * PX
            bad = blocked and blocked[0] <= t <= blocked[1]
            if bad:
                out.append(line(x, y - 12, x, y, color=POS, sw=2, dash="3 3"))
            else:
                out.append(line(x, y - 12, x, y, color=FIELD, sw=3))
            t += FRAME
        return "".join(out)

    # ── верхня доріжка: усе в обробнику
    f.append(mtext(100, 182, ["Без передачі:", "усе в обробнику"], size=13, color=MUTED))
    f.append(line(X0, 190, X1, 190, color=INK, sw=1.5))
    f.append(ticks(190, blocked=(20, 420)))
    bx0, bx1 = X0 + 20 * PX, X0 + 420 * PX
    f.append(fitbox(bx0, 124, bx1 - bx0, 44,
                    "обробник читає файл: 400 мс — цикл подій стоїть",
                    size=14, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(620, 226, "24 кадри поспіль не з'являються", size=13, color=POS))

    # ── нижня доріжка: робота віддана виконавцеві
    f.append(mtext(100, 372, ["З передачею", "у виконавця"], size=13, color=MUTED))
    f.append(line(X0, 380, X1, 380, color=INK, sw=1.5))
    f.append(ticks(380))
    f.append(rect(bx0, 330, 22, 28, fill="#eaf7ef", stroke=FIELD, sw=2))
    f.append(text(bx0 + 34, 349, "2 мс: віддав завдання", size=12, anchor="start"))
    f.append(rect(bx1, 330, 24, 28, fill="#eaf7ef", stroke=FIELD, sw=2))
    f.append(text(bx1 + 36, 349, "1 мс: застосував", size=12, anchor="start"))
    f.append(fitbox(bx0, 412, bx1 - bx0, 40,
                    "виконавець у своєму потоці: ті самі 400 мс",
                    size=14, fill="#eef2f7", stroke=MUTED, sw=1.5))

    f.append(text(620, 490, "зелена риска — кадр намальовано, червона — пропущено",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'frame-budget.svg'), W, H, *f)


# ── 3. Замок на моделі проти незмінних знімків ─────────────────────────────
def snapshot_vs_lock():
    W, H = 1100, 520
    f = []

    # ліва панель: спільна модель під замком
    f.append(rect(40, 60, 490, 420, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(285, 92, "Спільна модель під замком", size=15, bold=True))
    f.append(fitbox(70, 120, 190, 62, "Виконавець\nтримає замок 50 мс",
                    size=12, stroke=POS, sw=2, fill="#fdecea"))
    f.append(fitbox(310, 120, 190, 62, "Відмальовка\nчекає на замок",
                    size=12, stroke=MUTED, sw=1.6))
    f.append(arrow(165, 184, 232, 246))
    f.append(arrow(405, 184, 338, 246))
    f.append(fitbox(170, 248, 230, 84, "МОДЕЛЬ\nполе за полем під замками",
                    size=12, stroke=LINE, sw=2, fill="#eef2f7"))
    f.append(text(285, 380, "три пропущені кадри —", size=12, color=POS))
    f.append(text(285, 402, "і напівзмінений стан на екрані", size=12, color=POS))

    # права панель: незмінні знімки
    f.append(rect(570, 60, 490, 420, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(text(815, 92, "Незмінні знімки", size=15, bold=True))
    f.append(fitbox(600, 120, 180, 62, "Відмальовка\nмалює з v1",
                    size=12, stroke=MUTED, sw=1.6))
    f.append(fitbox(860, 120, 180, 62, "Модель публікує v2\nодним записом",
                    size=12, stroke=FIELD, sw=2, fill="#eaf7ef"))
    f.append(arrow(690, 184, 680, 240))
    f.append(arrow(950, 184, 958, 240))
    f.append(fitbox(605, 242, 150, 50, "знімок v1", size=13, stroke=MUTED, sw=1.6))
    f.append(fitbox(883, 242, 150, 50, "знімок v2", size=13, stroke=FIELD, sw=2))
    f.append(arrow(690, 296, 762, 332))
    f.append(arrow(950, 296, 878, 332))
    f.append(fitbox(760, 334, 120, 56, "спільне\nнутро", size=12,
                    fill="#eaf7ef", stroke=FIELD, sw=1.8))
    f.append(text(815, 424, "ніхто нікого не чекає,", size=12, color=FIELD))
    f.append(text(815, 446, "напівзмінених станів не буває", size=12, color=FIELD))

    render(os.path.join(OUT, 'snapshot-vs-lock.svg'), W, H, *f)


# ── 4. Три яруси часу життя стану ──────────────────────────────────────────
def state_tiers():
    W, H = 1120, 570
    f = []
    cols = [(40, 210), (270, 290), (580, 210), (810, 270)]
    heads = ["Ярус і строк життя", "Що там живе", "Хто пише", "Плутанина ярусів дає"]
    for (x, w), h in zip(cols, heads):
        f.append(text(x + w / 2, 62, h, size=14, bold=True, color=MUTED))

    rows = [
        (90, FIELD, "#eaf7ef",
         "ЕФЕМЕРНИЙ\nживе, доки живе вікно",
         "прокрутка, виділення,\nнаведення миші,\nнедонабраний текст",
         "саме подання",
         "потрапив у документ —\nфайл «змінюється»\nвід самого перегляду"),
        (250, NEG, "#eaf0fd",
         "СЕАНСОВИЙ\nживе, доки живе процес",
         "документ, стек скасування,\nпідключення, кеш",
         "модель —\nєдиний власник",
         "правда осіла у віджеті —\nдві копії розходяться"),
        (410, POS, "#fdecea",
         "ТРИВКИЙ\nпереживає перезапуск",
         "налаштування, файл на диску,\nкопія на сервері",
         "виконавець:\nце ввід-вивід",
         "запис із потоку інтерфейсу —\nзаморозка на кожному\nзбереженні"),
    ]
    for y, col, bg, c1, c2, c3, c4 in rows:
        cells = (c1, c2, c3, c4)
        for (x, w), s in zip(cols, cells):
            first = s is c1
            f.append(fitbox(x, y, w, 130, s, size=13,
                            fill=bg if first else FILL,
                            stroke=col if first else MUTED,
                            sw=2.2 if first else 1.4,
                            color=INK))

    render(os.path.join(OUT, 'state-tiers.svg'), W, H, *f)


# ── 5. Покоління: чому скасування не заміняє лічильника (вставка proj) ─────
def generation_race():
    W, H = 1180, 760
    f = []

    # колонки
    T_X, T_W = 24, 116
    UI_X, UI_W = 158, 352
    A_X, A_W = 534, 300
    B_X, B_W = 858, 298

    f.append(text(W / 2, 34, "Відповідь, що спізнилася: лічильник поколінь ловить те, "
                             "чого скасування вже не встигло", size=17, bold=True))

    for x, w, name, col in ((UI_X, UI_W, "ПОТІК ІНТЕРФЕЙСУ", FIELD),
                            (A_X, A_W, "ВИКОНАВЕЦЬ A  («ки»)", MUTED),
                            (B_X, B_W, "ВИКОНАВЕЦЬ B  («київ»)", MUTED)):
        f.append(fitbox(x, 58, w, 40, name, size=14, bold=True,
                        fill="#eef2f7", stroke=col, sw=2.0))
    f.append(fitbox(T_X, 58, T_W, 40, "ЧАС", size=14, bold=True,
                    fill="#eef2f7", stroke=MUTED, sw=2.0))

    # (час, колонка, текст, рамка, заливка)
    rows = [
        (0,   "ui", "gen_ = 1 · токен₁\nсубміт запиту «ки»", FIELD, "#eaf7ef"),
        (380, "a",  "знайшов.\nтокен₁ ще не зупинено →\nui_.post(gen = 1)", MUTED, FILL),
        (390, "ui", "людина дописала «їв»:\ngen_ = 2 · токен₁.request_stop()\n"
                    "субміт запиту «київ»", FIELD, "#eaf7ef"),
        (400, "ui", "цикл дістав post(gen = 1)\n1 ≠ 2 → ВІДПОВІДЬ ВИКИНУТО", POS, "#fdecea"),
        (600, "b",  "знайшов →\nui_.post(gen = 2)", MUTED, FILL),
        (610, "ui", "2 == 2 → publish(знімок)\n+ repaint()", FIELD, "#eaf7ef"),
    ]
    geom = {"ui": (UI_X, UI_W), "a": (A_X, A_W), "b": (B_X, B_W)}

    y = 122
    STEP, BH = 86, 74
    placed = {}
    for t, who, s, col, bg in rows:
        x, w = geom[who]
        f.append(fitbox(T_X, y + 16, T_W, 42, "%d мс" % t, size=14, bold=True,
                        fill=BG, stroke=MUTED, sw=1.4))
        f.append(fitbox(x, y, w, BH, s, size=13, fill=bg, stroke=col, sw=2.0))
        placed[(t, who)] = (x, w, y)
        # пунктирна нитка життя — лише в тих колонках, де в цьому рядку рамки НЕМА
        for other, (ox, ow) in geom.items():
            if other != who:
                f.append(line(ox + ow / 2, y - 6, ox + ow / 2, y + BH + 6,
                              color=MUTED, sw=1.2, dash="5 6"))
        y += STEP

    # стрілки передачі
    def hand(t_from, who_from, t_to, who_to, color=LINE):
        x1, w1, y1 = placed[(t_from, who_from)]
        x2, w2, y2 = placed[(t_to, who_to)]
        if x1 < x2:
            f.append(arrow(x1 + w1 + 6, y1 + BH / 2, x2 - 6, y2 + BH / 2, color=color))
        else:
            f.append(arrow(x1 - 6, y1 + BH / 2, x2 + w2 + 6, y2 + BH / 2, color=color))

    hand(0, "ui", 380, "a")            # субміт A
    hand(380, "a", 400, "ui", POS)     # відповідь A летить у чергу
    hand(390, "ui", 600, "b")          # субміт B
    hand(600, "b", 610, "ui", FIELD)   # відповідь B

    # підсумкові рамки
    f.append(fitbox(24, 654, 556, 84,
                    "ЛІЧИЛЬНИК — коректність.\n"
                    "Він єдиний ловить відповідь, яка вже лежала\n"
                    "в черзі, коли питання змінилося.",
                    size=13, fill="#eaf7ef", stroke=FIELD, sw=2.2))
    f.append(fitbox(600, 654, 556, 84,
                    "СКАСУВАННЯ — економія.\n"
                    "Устигни request_stop() до 380 мс — A вийшов би\n"
                    "на безпечній точці й не рахував би решту.",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=2.2))

    render(os.path.join(OUT, 'generation-race.svg'), W, H, *f)


# ── 6. Де в кістяку живуть замки (вставка proj) ────────────────────────────
def where_locks_live():
    W, H = 1180, 760
    f = []
    f.append(text(W / 2, 34, "Замки переїхали з даних на канали", size=17, bold=True))

    BW, BH = 300, 78
    GAP = 44
    x0 = 40

    def row(y, cells):
        x = x0
        prev = None
        for s, col, bg, sw in cells:
            f.append(fitbox(x, y, BW, BH, s, size=13, fill=bg, stroke=col, sw=sw))
            if prev is not None:
                f.append(arrow(prev, y + BH / 2, x - 8, y + BH / 2))
            prev = x + BW
            x += BW + GAP

    row(76, [("ПОТІК ІНТЕРФЕЙСУ\non_query_changed(): знімок + gen", FIELD, "#eaf7ef", 2.2),
             ("м'ютекс Pool::m_\nвзято лише на push у чергу", POS, "#fdecea", 2.4),
             ("ВИКОНАВЕЦЬ\ngrep() — робота ПОЗА замком", MUTED, FILL, 1.6)])

    row(206, [("ВИКОНАВЕЦЬ\nui_.post(результат, gen)", MUTED, FILL, 1.6),
              ("м'ютекс UiQueue::m_\nвзято лише на push у чергу", POS, "#fdecea", 2.4),
              ("ПОТІК ІНТЕРФЕЙСУ\nswap пачки, виклики ПОЗА замком", FIELD, "#eaf7ef", 2.2)])

    row(336, [("ПОТІК ІНТЕРФЕЙСУ\nзвірив gen, зібрав нову версію", FIELD, "#eaf7ef", 2.2),
              ("publish()\n1 атомарний запис покажчика", NEG, "#eaf0fd", 2.4),
              ("МОДЕЛЬ І ВІДМАЛЬОВКА\nзамків: 0", FIELD, "#eaf7ef", 2.6)])

    # три властивості, з яких випливає відсутність дедлоку
    f.append(text(W / 2, 476, "Три властивості цих двох замків — і чому дедлок неможливий",
                  size=15, bold=True))
    notes = [
        ("O(1) під замком", "Під замком — тільки push або swap черги.\n"
                            "Ні читання файлу, ні обчислення, ні\nвиклику чужого коду."),
        ("Робота — поза замком", "job() і fn() викликають, уже віддавши\n"
                                 "замок. Інакше потік тримав би замок\nпули й брав замок черги."),
        ("Жодного вкладення", "Ніхто ніколи не тримає обидва замки\n"
                              "одночасно. Цикл очікування вимагає\nдвох — тож його нема з чого скласти."),
    ]
    x = x0
    for head, body in notes:
        f.append(fitbox(x, 502, BW, 44, head, size=15, bold=True,
                        fill="#eef2f7", stroke=MUTED, sw=2.0))
        f.append(fitbox(x, 552, BW, 106, body, size=13, fill=BG, stroke=MUTED, sw=1.4))
        x += BW + GAP

    f.append(fitbox(x0, 678, 3 * BW + 2 * GAP, 56,
                    "Замок на моделі тримали б десятки мілісекунд і в невизначеному порядку. "
                    "Ці два — десятки наносекунд і поодинці.",
                    size=14, fill="#eaf7ef", stroke=FIELD, sw=2.2))

    render(os.path.join(OUT, 'where-locks-live.svg'), W, H, *f)


# ── 7. Розклад травневої нотатки 1979 року (вставка hist) ──────────────────
def mvc_1979_planning():
    W, H = 1180, 700
    f = []

    f.append(text(150, 62, "РІЧ", size=15, bold=True, color=MUTED))
    f.append(text(435, 62, "МОДЕЛЬ", size=15, bold=True, color=MUTED))
    f.append(text(775, 62, "ПОДАННЯ", size=15, bold=True, color=MUTED))
    f.append(text(1050, 62, "ЛЮДИНА Й КОМАНДИ", size=15, bold=True, color=MUTED))

    # річ — поза машиною
    f.append(fitbox(40, 250, 220, 130,
                    "сам проєкт:\nміст, платформа,\nплан робіт\n(поза машиною)",
                    size=13, stroke=MUTED, sw=1.6))
    f.append(mtext(150, 424, ["модель мусить відбивати",
                              "річ один-до-одного —",
                              "як її бачить власник"], size=12, color=MUTED))

    # модель
    f.append(arrow(264, 310, 306, 310))
    f.append(fitbox(310, 240, 250, 140,
                    "NetworkModel\n+ Activity\n\nусі поняття —\nодного рівня задачі",
                    size=13, stroke=FIELD, sw=2.2, fill="#eaf7ef"))

    # подання
    views = ["Список мереж", "Список робіт", "Атрибути роботи (текст)",
             "Мережева діаграма", "Діаграма Ґанта", "Крива ресурсів"]
    ys = [110, 180, 250, 320, 390, 460]
    for s, y in zip(views, ys):
        f.append(fitbox(640, y, 270, 58, s, size=13, stroke=MUTED, sw=1.6))

    # подання → модель, спільним хребтом
    f.append(line(605, 139, 605, 489, color=LINE, sw=1.5))
    for y in ys:
        f.append(line(640, y + 29, 605, y + 29, color=LINE, sw=1.5))
    f.append(arrow(605, 310, 564, 310))
    f.append(mtext(435, 176, ["подання питають модель",
                              "її ж мовою"], size=12, color=MUTED))

    # людина й редактор
    f.append(fitbox(960, 90, 180, 52, "ЛЮДИНА", size=14, stroke=MUTED, sw=1.6))
    f.append(arrow(1050, 144, 1050, 176))
    f.append(fitbox(960, 180, 180, 340,
                    "РЕДАКТОР\n\nставить подання\nна екран,\nузгоджує їх,\nдає меню",
                    size=13, stroke=NEG, sw=2.2, fill="#eaf0fd"))

    # редактор → подання
    f.append(line(958, 350, 935, 350, color=NEG, sw=1.8))
    f.append(line(935, 139, 935, 489, color=NEG, sw=1.8))
    for y in ys:
        f.append(arrow(935, y + 29, 914, y + 29, color=NEG, sw=1.8))
    f.append(mtext(1050, 562, ["команда виділення —",
                               "всім поданням одразу"], size=12, color=NEG))

    render(os.path.join(OUT, 'mvc-1979-planning.svg'), W, H, *f)


# ── 8. Розклад 1979 року проти бібліотеки Smalltalk-80 (вставка hist) ──────
def mvc_1979_vs_1980():
    W, H = 1160, 560
    f = []

    f.append(rect(40, 56, 520, 490, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))
    f.append(rect(600, 56, 520, 490, fill="#fbfbfc", stroke=MUTED, sw=1.5, rx=10))

    # ліва панель: нотатки 1979
    f.append(text(300, 84, "1979 · нотатки Реєнскауґа", size=15, bold=True))
    f.append(fitbox(200, 110, 200, 46, "ЛЮДИНА", size=13, stroke=MUTED, sw=1.6))
    f.append(arrow(300, 158, 300, 182))
    f.append(fitbox(150, 184, 300, 62, "КОНТРОЛЕР\n(редактор травневої нотатки)",
                    size=13, stroke=NEG, sw=2.2, fill="#eaf0fd"))
    for x in (70, 220, 370):
        f.append(fitbox(x, 298, 130, 56, "Подання", size=13, stroke=MUTED, sw=1.6))
    f.append(arrow(300, 248, 137, 294, color=NEG, sw=1.8))
    f.append(arrow(300, 248, 285, 294, color=NEG, sw=1.8))
    f.append(arrow(300, 248, 433, 294, color=NEG, sw=1.8))
    f.append(fitbox(180, 410, 240, 64, "МОДЕЛЬ", size=14,
                    stroke=FIELD, sw=2.2, fill="#eaf7ef"))
    f.append(arrow(135, 356, 262, 406))
    f.append(arrow(285, 356, 296, 406))
    f.append(arrow(435, 356, 338, 406))
    f.append(mtext(300, 504, ["контролер один: він розставляє подання",
                              "й тримає спільне виділення"], size=12, color=NEG))

    # права панель: бібліотека Smalltalk-80
    f.append(text(860, 84, "1980 · бібліотека Smalltalk-80", size=15, bold=True))
    f.append(fitbox(690, 100, 340, 44, "координаторові місця не лишилось",
                    size=13, stroke=POS, sw=2, fill="#fdecea", color=POS))
    for x in (620, 785, 950):
        f.append(rect(x, 170, 150, 122, fill="#f4f6f8", stroke=MUTED, sw=1.5))
        f.append(fitbox(x + 8, 180, 134, 46, "Подання", size=13,
                        stroke=MUTED, sw=1.6))
        f.append(fitbox(x + 8, 234, 134, 46, "Контролер", size=13,
                        stroke=NEG, sw=2, fill="#eaf0fd"))
    f.append(fitbox(740, 410, 240, 64, "МОДЕЛЬ", size=14,
                    stroke=FIELD, sw=2.2, fill="#eaf7ef"))
    f.append(arrow(695, 294, 800, 406))
    f.append(arrow(860, 294, 860, 406))
    f.append(arrow(1025, 294, 920, 406))
    f.append(mtext(860, 504, ["у кожного подання свій контролер вводу;",
                              "спільне виділення тримати нікому"], size=12, color=POS))

    render(os.path.join(OUT, 'mvc-1979-vs-1980.svg'), W, H, *f)


if __name__ == '__main__':
    lanes_handoff()
    frame_budget()
    snapshot_vs_lock()
    state_tiers()
    generation_race()
    where_locks_live()
    mvc_1979_planning()
    mvc_1979_vs_1980()
    print("ok:", sorted(os.listdir(OUT)))
