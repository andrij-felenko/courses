# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdf2ee"
COOL = "#eef2fd"
LEAF = "#eaf7ef"
PAPER = "#f7f8fa"


# ── 1. Стан процесу: три шари, і в кожному є числа, які мусять збігтися ───────
def fig_state_graph():
    W, H = 1120, 720
    p = []

    p.append(fitbox(40, 30, 1040, 40,
                    "«Стан процесу» лежить у трьох різних місцях — і скопіювати вміст замало",
                    size=15, fill=PAPER, stroke=INK, sw=1.8, color=INK, bold=True))

    cols = [
        (40, "У самій задачі", NEG, COOL,
         ["регістри й точка виконання",
          "маска й черга сигналів",
          "PID · PPID · PGID · SID",
          "UID, GID, можливості",
          "ліміти ресурсів (rlimit)"]),
        (400, "Структури, на які\nзадача посилається", FIELD, LEAF,
         ["mm_struct — карта пам'яті",
          "files_struct — таблиця fd",
          "sighand — диспозиції",
          "fs_struct — корінь і cwd",
          "nsproxy — простори імен"]),
        (760, "Об'єкти ядра\nза дескрипторами", POS, WARM,
         ["опис відкритого файлу:\nзміщення й прапорці",
          "канал: вміст буфера",
          "сокет: черги й номери\nпослідовності TCP",
          "epoll: набір цілей",
          "таймер: залишок до спрацювання"]),
    ]

    for x0, head, accent, fill, rows in cols:
        p.append(fitbox(x0, 92, 320, 58, head, size=14, fill=fill,
                        stroke=accent, sw=1.8, color=accent, bold=True))
        y = 172
        for r in rows:
            n = r.count("\n") + 1
            hgt = 46 if n == 1 else 62
            p.append(fitbox(x0 + 10, y, 300, hgt, r, size=12,
                            fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
            y += hgt + 12

    p.append(arrow(366, 121, 396, 121, color=MUTED, sw=1.8))
    p.append(arrow(726, 121, 756, 121, color=MUTED, sw=1.8))

    p.append(fitbox(40, 566, 1040, 44,
                    "ВМІСТ — байти сторінок, буферів, черг: його можна прочитати й записати назад",
                    size=13, fill=LEAF, stroke=FIELD, sw=1.8, color=INK, bold=True))
    p.append(fitbox(40, 622, 1040, 44,
                    "ІДЕНТИЧНІСТЬ — число 4711 як PID, число 7 як номер дескриптора, адреса 0x7f… як місце відображення",
                    size=13, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(text(W / 2, 700,
                  "вміст копіюється тривіально; уся складність знімка — у другому рядку",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "state-graph.svg"), W, H, *p,
           title="Три шари стану процесу і різниця між вмістом та ідентичністю")


# ── 2. Паразитний код: чотири стани адресного простору жертви ─────────────────
def fig_parasite():
    W, H = 1160, 700
    p = []

    p.append(fitbox(40, 26, 1080, 38,
                    "Щоб виконати системний виклик У КОНТЕКСТІ жертви, знімач тимчасово селиться в її пам'яті",
                    size=14, fill=PAPER, stroke=INK, sw=1.8, color=INK, bold=True))

    heads = [
        "1. Задача біжить",
        "2. PTRACE_SEIZE\nі підміна кількох байтів",
        "3. Паразит на місці",
        "4. Після команди FINI",
    ]
    notes = [
        "звичайний адресний\nпростір: код, дані,\nкупа, стеки потоків",
        "у точці, де стоїть\nлічильник команд,\nтимчасово лежить\nінструкція syscall —\nнею роблять mmap",
        "у виділену ділянку\nзалито PIE-блоб;\nвін виконує виклики\nвід імені задачі\nй віддає результат\nу сокет знімача",
        "паразит зробив\nrt_sigreturn: регістри\nвзято з підробленого\nсигнального фрейму,\nділянку розмаповано —\nслідів не лишилося",
    ]
    accents = [MUTED, NEG, POS, FIELD]

    x0 = 46
    colw = 250
    gap = 22
    for i in range(4):
        x = x0 + i * (colw + gap)
        p.append(fitbox(x, 82, colw, 52, heads[i], size=13, fill="#ffffff",
                        stroke=accents[i], sw=1.8, color=accents[i], bold=True))

        blocks = [("код програми", "#ffffff"),
                  ("дані й купа", "#ffffff"),
                  ("стеки потоків", "#ffffff")]
        y = 152
        for name, fill in blocks:
            hl = "#ffffff"
            if i == 1 and name == "код програми":
                hl = COOL
            p.append(fitbox(x + 12, y, colw - 24, 44, name, size=11,
                            fill=hl, stroke=MUTED, sw=1.2, color=INK))
            y += 52

        if i == 1:
            p.append(fitbox(x + 12, y + 6, colw - 24, 44,
                            "тут: 2 байти → syscall", size=11,
                            fill=COOL, stroke=NEG, sw=1.6, color=NEG, bold=True))
        elif i == 2:
            p.append(fitbox(x + 12, y + 6, colw - 24, 44,
                            "паразитна ділянка", size=11,
                            fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))
        else:
            p.append(fitbox(x + 12, y + 6, colw - 24, 44, "(нічого зайвого)", size=11,
                            fill=PAPER, stroke=MUTED, sw=1.2, color=MUTED))

        p.append(fitbox(x, 372, colw, 130, notes[i], size=11,
                        fill=PAPER, stroke=MUTED, sw=1.2, color=INK))

        if i < 3:
            ax = x + colw + 4
            p.append(arrow(ax, 250, ax + gap - 8, 250, color=INK, sw=1.7))

    p.append(fitbox(46, 526, 1068, 46,
                    "Ззовні знімач дістає лише те, що ядро погодилося показати у /proc; решту доводиться питати зсередини",
                    size=13, fill=LEAF, stroke=FIELD, sw=1.8, color=INK, bold=True))
    p.append(fitbox(46, 588, 1068, 46,
                    "Зсередини можна: перебрати диспозиції сигналів, зняти таймери, вивантажити пам'ять через vmsplice у канал",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.4, color=INK))

    p.append(text(W / 2, 668,
                  "паразит нічого не змінює в задачі — він лише позичає її контекст і йде",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "parasite.svg"), W, H, *p,
           title="Паразитний код: як знімач виконує виклики від імені чужої задачі")


# ── 3. Відновлення: процес-відновлювач перетворюється на жертву ───────────────
def fig_restore_morph():
    W, H = 1120, 660
    p = []

    p.append(fitbox(40, 26, 1040, 38,
                    "Відновлювач сидить у ТОМУ САМОМУ адресному просторі, який має стерти",
                    size=14, fill=PAPER, stroke=INK, sw=1.8, color=INK, bold=True))

    stages = [
        ("Крок 1. Заготовка", NEG, COOL,
         ["код і дані criu",
          "образи, прочитані з диска",
          "сторінки жертви — поки що\nпокладені НЕ на свої адреси"],
         "процес уже має правильний\nPID, дескриптори й простори імен,\nале чужий вміст пам'яті"),
        ("Крок 2. Острівець", POS, WARM,
         ["блоб-відновлювач\nна вільній адресі",
          "маленький стек блоба",
          "список того, що\nтреба перекласти"],
         "керування стрибає в блоб —\nтепер можна розмаповувати\nвсе інше, зокрема сам criu"),
        ("Крок 3. Жертва", FIELD, LEAF,
         ["код програми на своїй адресі",
          "дані, купа, стеки —\nна своїх адресах",
          "блоб знімає себе останнім"],
         "rt_sigreturn з підробленого фрейму\nставить регістри — задача продовжує\nз тієї самої інструкції"),
    ]

    x0 = 46
    colw = 330
    gap = 26
    for i, (head, accent, fill, rows, note) in enumerate(stages):
        x = x0 + i * (colw + gap)
        p.append(fitbox(x, 84, colw, 44, head, size=14, fill=fill,
                        stroke=accent, sw=1.8, color=accent, bold=True))
        y = 146
        for r in rows:
            n = r.count("\n") + 1
            hgt = 46 if n == 1 else 66
            p.append(fitbox(x + 14, y, colw - 28, hgt, r, size=12,
                            fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
            y += hgt + 12
        p.append(fitbox(x, 386, colw, 92, note, size=11,
                        fill=PAPER, stroke=accent, sw=1.3, color=INK))
        if i < 2:
            ax = x + colw + 5
            p.append(arrow(ax, 250, ax + gap - 10, 250, color=INK, sw=1.8))

    p.append(fitbox(46, 508, 1028, 48,
                    "Порядок вимушений: розмапувати власний код можна тільки з коду, який лежить деінде",
                    size=13, fill="#ffffff", stroke=INK, sw=1.6, color=INK, bold=True))
    p.append(fitbox(46, 570, 1028, 44,
                    "Саме тому блоб пишуть позиційно-незалежним і без жодного звертання до бібліотек",
                    size=12, fill=PAPER, stroke=MUTED, sw=1.2, color=INK))

    p.append(text(W / 2, 640,
                  "відновлення — не запуск програми, а заміщення одного процесу іншим зсередини",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "restore-morph.svg"), W, H, *p,
           title="Три кроки відновлення: заготовка, блоб-острівець, готова задача")


# ── 4. Три стратегії перенесення і довжина паузи ──────────────────────────────
def fig_migration_strategies():
    W, H = 1120, 560
    p = []

    p.append(fitbox(40, 26, 1040, 38,
                    "Знімок завжди коштує паузи — питання лише, скільки роботи в неї зігнати",
                    size=14, fill=PAPER, stroke=INK, sw=1.8, color=INK, bold=True))

    LX = 40
    TX = 300          # де починається шкала часу
    TW = 700
    rows = [
        ("Зупинити й скопіювати", [
            ("робота", 0.00, 0.22, "#ffffff", MUTED),
            ("ПАУЗА: знімок і передача всієї пам'яті", 0.22, 0.80, WARM, POS),
            ("робота", 0.80, 1.00, "#ffffff", MUTED),
        ], "проста, але пауза дорівнює обсягу пам'яті, поділеному на смугу"),
        ("Копіювати наперед", [
            ("робота + ітерації копіювання", 0.00, 0.62, LEAF, FIELD),
            ("пауза: дозбір бруду", 0.62, 0.74, WARM, POS),
            ("робота", 0.74, 1.00, "#ffffff", MUTED),
        ], "пауза мала, доки задача бруднить сторінки повільніше, ніж їх устигає передати мережа"),
        ("Копіювати навздогін", [
            ("робота", 0.00, 0.34, "#ffffff", MUTED),
            ("пауза", 0.34, 0.40, WARM, POS),
            ("робота на новій машині: сторінки підтягують за збоями", 0.40, 1.00, COOL, NEG),
        ], "пауза найкоротша, зате перші хвилини задача працює повільніше"),
    ]

    y = 106
    for name, segs, note in rows:
        p.append(fitbox(LX, y, 240, 54, name, size=13, fill="#ffffff",
                        stroke=INK, sw=1.5, color=INK, bold=True))
        for label, a, b, fill, stroke in segs:
            x = TX + TW * a
            w = TW * (b - a)
            p.append(fitbox(x, y + 6, w, 42, label, size=11, fill=fill,
                            stroke=stroke, sw=1.5, color=INK))
        p.append(fitbox(LX, y + 66, 1040, 34, note, size=11,
                        fill=PAPER, stroke=MUTED, sw=1.1, color=MUTED))
        y += 124

    p.append(line(TX, 486, TX + TW, 486, color=INK, sw=1.5))
    p.append(arrow(TX + TW - 30, 486, TX + TW + 20, 486, color=INK, sw=1.5))
    p.append(text(TX + TW / 2, 512, "час", size=12, color=INK))

    p.append(text(W / 2, 542,
                  "пауза — це відрізок, протягом якого задача не виконала жодної інструкції",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "migration-strategies.svg"), W, H, *p,
           title="Три стратегії перенесення живої задачі та довжина паузи в кожній")


# ── 5. Ін'єкція syscall: чотири зліпки регістрів і слова коду ─────────────────
def fig_inject_sequence():
    W, H = 1200, 620
    p = []

    p.append(fitbox(40, 26, 1120, 38,
                    "Один системний виклик руками жертви — і точне повернення в початковий стан",
                    size=14, fill=PAPER, stroke=INK, sw=1.8, color=INK, bold=True))

    cols = [
        ("1. Зберегли", NEG, COOL, "55 48 89 e5 …",
         "rip = 0x…4e5a", "rax = (байдуже)",
         "зліпок регістрів\nвідкладено окремо"),
        ("2. Підмінили", POS, WARM, "0f 05 89 e5 …",
         "rip = 0x…4e5a", "rax = 39 (getpid)",
         "перші 2 байти —\nінструкція syscall"),
        ("3. Крок", FIELD, LEAF, "0f 05 89 e5 …",
         "rip = 0x…4e5c", "rax = 4711 (=PID)",
         "syscall виконано,\nрезультат у rax"),
        ("4. Повернули", MUTED, "#ffffff", "55 48 89 e5 …",
         "rip = 0x…4e5a", "rax = (як було)",
         "байти й регістри —\nточно як до втручання"),
    ]

    x0 = 46
    colw = 268
    gap = 16
    for i, (head, accent, fill, word, rrip, rrax, note) in enumerate(cols):
        x = x0 + i * (colw + gap)
        p.append(fitbox(x, 84, colw, 44, head, size=14, fill=fill,
                        stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(x + 12, 146, colw - 24, 34, "слово за rip:", size=11,
                        fill=PAPER, stroke=MUTED, sw=1.1, color=MUTED))
        p.append(fitbox(x + 12, 184, colw - 24, 44, word, size=13,
                        fill="#ffffff", stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(fitbox(x + 12, 240, colw - 24, 40, rrip, size=12,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(x + 12, 288, colw - 24, 40, rrax, size=12,
                        fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(x, 344, colw, 72, note, size=11,
                        fill=PAPER, stroke=accent, sw=1.3, color=INK))
        if i < 3:
            ax = x + colw + 1
            p.append(arrow(ax, 206, ax + gap - 2, 206, color=INK, sw=1.7))

    p.append(fitbox(46, 442, 1108, 44,
                    "Симетрія повна: кожній дії ліворуч відповідає рівно зворотна праворуч — стан 4 дорівнює стану 1",
                    size=13, fill=LEAF, stroke=FIELD, sw=1.7, color=INK, bold=True))
    p.append(fitbox(46, 500, 1108, 44,
                    "getpid() повернув номер САМОЇ жертви (4711) — доказ, що виклик стався в її контексті, не в нашому",
                    size=12, fill="#ffffff", stroke=MUTED, sw=1.3, color=INK))

    p.append(text(W / 2, 578,
                  "жодного сліду: та сама інструкція, ті самі регістри, задача біжить далі",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "inject-sequence.svg"), W, H, *p,
           title="Ін'єкція одного syscall: зберегти → підмінити → крок → повернути")


# ── 6. Інструкція системного виклику: x86-64 проти arm64 ──────────────────────
def fig_syscall_isa():
    W, H = 1140, 520
    p = []

    p.append(fitbox(40, 26, 1060, 38,
                    "Прийом той самий, але інструкція, її довжина й регістри — архітектурні",
                    size=14, fill=PAPER, stroke=INK, sw=1.8, color=INK, bold=True))

    panels = [
        ("x86-64", NEG, COOL, "syscall", "0f 05", "2 байти",
         "довжина команд змінна;\nrip може стояти за будь-якою\nадресою — міняємо лише 2 байти",
         ["номер виклику → rax",
          "аргументи → rdi rsi rdx r10 r8 r9",
          "результат ← rax"]),
        ("arm64", POS, WARM, "svc #0", "01 00 00 d4", "4 байти",
         "команди фіксовані по 4 байти;\npc завжди кратний 4 —\nміняємо ціле 4-байтове слово",
         ["номер виклику → x8",
          "аргументи → x0 x1 x2 x3 x4 x5",
          "результат ← x0"]),
    ]

    x0 = 60
    colw = 480
    gap = 60
    for i, (head, accent, fill, mn, by, length, note, regs) in enumerate(panels):
        x = x0 + i * (colw + gap)
        p.append(fitbox(x, 84, colw, 46, head, size=16, fill=fill,
                        stroke=accent, sw=2, color=accent, bold=True))
        p.append(fitbox(x + 16, 148, 176, 54, mn, size=17,
                        fill="#ffffff", stroke=accent, sw=1.8, color=INK, bold=True))
        p.append(fitbox(x + 204, 148, colw - 220, 54, by + "   (" + length + ")",
                        size=14, fill="#ffffff", stroke=MUTED, sw=1.4, color=INK, bold=True))
        p.append(fitbox(x + 16, 214, colw - 32, 76, note, size=12,
                        fill=PAPER, stroke=accent, sw=1.3, color=INK))
        y = 302
        for r in regs:
            p.append(fitbox(x + 16, y, colw - 32, 40, r, size=12,
                            fill="#ffffff", stroke=MUTED, sw=1.2, color=INK))
            y += 48

    p.append(text(W / 2, 500,
                  "той самий алгоритм зберегти → підмінити → крок → повернути; різняться лише байти й імена регістрів",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "syscall-isa.svg"), W, H, *p,
           title="Інструкція системного виклику: x86-64 (2 байти) проти arm64 (4 байти)")


# ── 7. Пауза за ітераціями попереднього копіювання (лог-шкала) ────────────────
def fig_precopy_residual():
    import math
    W, H = 1180, 600
    p = []

    ORANGE = "#d97706"

    PX0, PX1 = 170.0, 880.0          # межі поля побудови по горизонталі
    PY0, PY1 = 100.0, 470.0          # по вертикалі: 100 с угорі, 0.01 с унизу
    NMAX = 24
    DEC = (PY1 - PY0) / 4.0          # пікселів на десятковий порядок

    W0, BW, COST = 40.0, 1.1, 0.1    # ГіБ · ГіБ/с · с накладних на раунд
    P0 = W0 / BW                     # пауза без жодної ітерації

    def xf(n):
        return PX0 + (PX1 - PX0) * n / NMAX

    def yf(sec):
        return PY0 + (2.0 - math.log10(sec)) * DEC

    for d in (2, 1, 0, -1, -2):
        y = PY0 + (2 - d) * DEC
        p.append(line(PX0, y, PX1, y, color="#e2e5ea", sw=1.0))
    for n in range(0, NMAX + 1, 4):
        p.append(line(xf(n), PY0, xf(n), PY1, color="#eef0f3", sw=1.0))

    p.append(line(PX0, PY0, PX0, PY1, color=INK, sw=1.6))
    p.append(line(PX0, PY1, PX1, PY1, color=INK, sw=1.6))

    for d, lab in ((2, "100 с"), (1, "10 с"), (0, "1 с"), (-1, "0.1 с"), (-2, "0.01 с")):
        y = PY0 + (2 - d) * DEC
        p.append(line(PX0 - 7, y, PX0, y, color=INK, sw=1.4))
        p.append(text(PX0 - 14, y + 4, lab, size=12, color=INK, anchor="end"))
    for n in range(0, NMAX + 1, 4):
        p.append(line(xf(n), PY1, xf(n), PY1 + 7, color=INK, sw=1.4))
        p.append(text(xf(n), PY1 + 26, str(n), size=12, color=INK))

    p.append(text((PX0 + PX1) / 2, PY1 + 54, "номер ітерації n", size=13, color=INK))
    p.append(text(PX0 + 6, PY0 - 16, "пауза Wₙ / B", size=13, color=INK, anchor="start"))

    yt = yf(0.3)                     # ціль 300 мс
    p.append(line(PX0, yt, PX1, yt, color=MUTED, sw=1.6, dash="7 5"))

    for rho, col in ((0.25, NEG), (0.50, FIELD), (0.80, ORANGE), (0.95, POS)):
        # межа окупності раунду: далі виграш менший за сталі накладні COST
        nstop = math.ceil(math.log(COST * BW / (W0 * (1 - rho))) / math.log(rho))
        pts = []
        for n in range(0, min(nstop, NMAX) + 1):
            sec = P0 * rho ** n
            if sec < 0.01:
                break
            pts.append((xf(n), yf(sec)))
        for i in range(len(pts) - 1):
            p.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          color=col, sw=2.6))
        if nstop <= NMAX and P0 * rho ** nstop >= 0.01:
            p.append(circle(xf(nstop), yf(P0 * rho ** nstop), 6.5,
                            fill=col, stroke="#ffffff", sw=2.0))

    LX, LW = 906.0, 250.0
    ly = 116.0
    for lab, col in (("ρ = 0.25 — 5 раундів, 0.036 с", NEG),
                     ("ρ = 0.50 — 8 раундів, 0.14 с", FIELD),
                     ("ρ = 0.80 — 20 раундів, 0.42 с", ORANGE),
                     ("ρ = 0.95 — 57 раундів, 1.95 с", POS)):
        p.append(fitbox(LX, ly, LW, 44, lab, size=12, fill="#ffffff",
                        stroke=col, sw=1.8, color=col, bold=True))
        ly += 54
    p.append(fitbox(LX, ly + 8, LW, 56,
                    "штрихова лінія — ціль 0.3 с\n● — де раунд перестає окупатися",
                    size=11, fill=PAPER, stroke=MUTED, sw=1.2, color=INK))

    p.append(text(W / 2, 566,
                  "опустити паузу вдесятеро коштує сталої кількості раундів — "
                  "і що ближче ρ до одиниці, то ця кількість більша",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "precopy-residual.svg"), W, H, *p,
           title="Пауза за номером ітерації: 40 ГіБ, смуга 1.1 ГіБ/с, накладні раунду 0.1 с")


# ── 8. Відображення Wₙ → Wₙ₊₁ і його нерухома точка ──────────────────────────
def fig_precopy_fixed_point():
    import math
    W, H = 1180, 640
    p = []

    S = 8.0            # ГіБ — слід записів
    WMAX = 10.0
    PY0, PY1 = 120.0, 480.0

    def panel(px0, px1, rho, head, note, note_color):
        out = []

        def xf(w):
            return px0 + (px1 - px0) * w / WMAX

        def yf(w):
            return PY1 - (PY1 - PY0) * w / WMAX

        def phi(w):
            return S * (1.0 - math.exp(-rho * w / S))

        out.append(fitbox(px0 - 4, 48, (px1 - px0) + 8, 38, head, size=13,
                          fill=PAPER, stroke=INK, sw=1.6, color=INK, bold=True))

        out.append(line(px0, PY0, px0, PY1, color=INK, sw=1.6))
        out.append(line(px0, PY1, px1, PY1, color=INK, sw=1.6))
        for g in range(0, 11, 2):
            out.append(line(xf(g), PY1, xf(g), PY1 + 7, color=INK, sw=1.4))
            out.append(text(xf(g), PY1 + 26, str(g), size=12, color=INK))
            out.append(line(px0 - 7, yf(g), px0, yf(g), color=INK, sw=1.4))
            out.append(text(px0 - 13, yf(g) + 4, str(g), size=12, color=INK, anchor="end"))

        out.append(line(xf(0), yf(0), xf(WMAX), yf(WMAX), color=MUTED, sw=1.6, dash="6 5"))

        N = 90
        pts = [(xf(WMAX * i / N), yf(phi(WMAX * i / N))) for i in range(N + 1)]
        for i in range(N):
            out.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                            color=NEG, sw=2.6))

        w = WMAX                                   # павутинка від W = 10 ГіБ
        for _ in range(6):
            nxt = phi(w)
            out.append(line(xf(w), yf(w), xf(w), yf(nxt), color=POS, sw=1.6))
            out.append(line(xf(w), yf(nxt), xf(nxt), yf(nxt), color=POS, sw=1.6))
            w = nxt

        if rho > 1:
            wf = 0.5
            for _ in range(3000):
                wf = phi(wf)
            out.append(circle(xf(wf), yf(wf), 7.0, fill=POS, stroke="#ffffff", sw=2.2))

        out.append(fitbox(xf(0.5), yf(9.7), (px1 - px0) * 0.66, 62, note, size=11,
                          fill="#ffffff", stroke=note_color, sw=1.6, color=INK))
        return out

    p += panel(130.0, 540.0, 0.6,
               "ρ = 0.6: крива всюди нижче діагоналі",
               "нерухома точка одна — нуль;\nзалишок сходить до нього\nз будь-якого початку",
               FIELD)
    p += panel(700.0, 1110.0, 2.0,
               "ρ = 2.0: крива перетинає діагональ",
               "нуль став відштовхувальним;\nзалишок сідає на W* = 6.37 ГіБ\nі далі не меншає",
               POS)

    p.append(text(335, PY1 + 54, "Wₙ, ГіБ", size=13, color=INK))
    p.append(text(905, PY1 + 54, "Wₙ, ГіБ", size=13, color=INK))
    p.append(text(136, PY0 - 8, "Wₙ₊₁, ГіБ", size=13, color=INK, anchor="start"))
    p.append(text(706, PY0 - 8, "Wₙ₊₁, ГіБ", size=13, color=INK, anchor="start"))

    p.append(text(W / 2, 606,
                  "нахил кривої в нулі дорівнює ρ — саме він, а не вигляд кривої вдалині, "
                  "вирішує, чи дійде залишок до нуля",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "precopy-fixed-point.svg"), W, H, *p,
           title="Wₙ₊₁ = S·(1 − e^(−ρ·Wₙ/S)): те саме відображення за двох значень ρ")


fig_state_graph()
fig_parasite()
fig_restore_morph()
fig_migration_strategies()
fig_inject_sequence()
fig_syscall_isa()
fig_precopy_residual()
fig_precopy_fixed_point()
print("ok")


# ── Поверхня ядра: коли яку однобічність закривали ────────────────────────────
def fig_kernel_surface_grid():
    W, H = 1240, 736

    LX, LW = 30, 158            # стовпчик підписів рядків
    CX, CW, CGAP = 200, 245, 8  # стовпчики епох
    HY, HH = 62, 46             # шапка стовпчиків
    RY, RH, RGAP = 126, 108, 10

    eras = [
        ("3.1 – 3.5\n2011 – 2012", WARM),
        ("3.8 – 3.18\n2013 – 2014", PAPER),
        ("4.3 – 4.16\n2015 – 2018", COOL),
        ("5.5 – 5.13\n2020 – 2021", LEAF),
    ]

    rows = [
        ("Пам'ять", [
            "map_files/ (3.3)\nPR_SET_MM (3.3)",
            "clear_refs = 4 (3.11)\nPR_SET_MM_MAP (3.18)",
            "userfaultfd (4.3)\nнекооперативний (4.11)",
            "—",
        ]),
        ("Дескриптори\nй черги", [
            "kcmp (3.5)",
            "fdinfo за типом (3.8)\nmnt_id (3.15)\ntimerfd у fdinfo (3.17)",
            "PTRACE_SECCOMP_\nGET_FILTER (4.4)\nKCMP_EPOLL_TFD (4.13)",
            "—",
        ]),
        ("Ідентичність\nі дерево", [
            "ns_last_pid (3.3)\nchildren (3.5)\nPR_GET_TID_ADDRESS (3.5)",
            "—",
            "ARCH_MAP_VDSO_* (4.9)",
            "clone3 set_tid (5.5)\nPTRACE_GET_RSEQ_\nCONFIGURATION (5.13)",
        ]),
        ("Мережа", [
            "TCP_REPAIR (3.5)\nTCP_REPAIR_QUEUE\nTCP_QUEUE_SEQ\nTCP_REPAIR_OPTIONS",
            "—",
            "TCP_REPAIR_WINDOW (4.8)",
            "—",
        ]),
        ("Заморозка,\nчас і права", [
            "PTRACE_SEIZE (3.1 / 3.4)\nPTRACE_INTERRUPT",
            "PTRACE_PEEKSIGINFO (3.10)\nPTRACE_GETSIGMASK (3.11)",
            "—",
            "простір імен часу (5.6)\nCAP_CHECKPOINT_\nRESTORE (5.9)",
        ]),
    ]

    p = []

    for i, (label, fill) in enumerate(eras):
        x = CX + i * (CW + CGAP)
        p.append(fitbox(x, HY, CW, HH, label, size=13, fill=fill,
                        stroke=INK, sw=1.6, color=INK, bold=True))

    for j, (name, cells) in enumerate(rows):
        y = RY + j * (RH + RGAP)
        p.append(fitbox(LX, y, LW, RH, name, size=13, fill="#ffffff",
                        stroke=INK, sw=1.6, color=INK, bold=True))
        for i, cell in enumerate(cells):
            x = CX + i * (CW + CGAP)
            empty = (cell == "—")
            p.append(fitbox(x, y, CW, RH, cell, size=11,
                            fill="#ffffff" if empty else eras[i][1],
                            stroke=MUTED if empty else LINE,
                            sw=1.0 if empty else 1.4,
                            color=MUTED if empty else INK))

    p.append(text(W / 2, RY + 5 * (RH + RGAP) + 26,
                  "щільність зліва — це 2012 рік: більшу частину поверхні добудували за півтора року",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "kernel-surface-grid.svg"), W, H, *p,
           title="Добудови інтерфейсу ядра заради знімка: що коли з'явилося")


fig_kernel_surface_grid()
