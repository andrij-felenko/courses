# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: один виклик — два повернення ────────────────────────────────────
# Ідея: у ядро входить ОДИН потік виконання, а виходять ДВА однакові процеси,
# і єдина відмінність, яку ядро в них закладає, — значення, що повертає fork().
# Знизу — межа копіювання: що в обох однакове, а що зумисне різне.
def fig_one_call_two_returns():
    W, H = 960, 620
    p = []

    b, bw, bh = textbox(480, 92, "процес-батько    pid 4021", size=15, pad=12,
                        fill="#eef3fb", stroke=NEG, sw=1.6, bold=True)
    p.append(b)
    p.append(arrow(480, 92 + bh / 2 + 4, 480, 158, color=NEG))

    # смуга ядра
    p.append(rect(150, 162, 660, 92, fill="#f4f6f8", stroke=INK, sw=1.6, rx=10))
    p.append(text(480, 190, "ядро: fork()", size=15, color=INK, bold=True))
    p.append(text(480, 214, "новий обліковий запис задачі  ·  копія таблиць сторінок",
                  size=12.5, color=MUTED))
    p.append(text(480, 234, "копія таблиці дескрипторів  ·  новий PID",
                  size=12.5, color=MUTED))

    p.append(arrow(360, 256, 250, 322, color=NEG))
    p.append(arrow(600, 256, 710, 322, color=POS))

    b, bw, bh = textbox(250, 362, "батько    pid 4021\nfork() повернув 4022", size=14, pad=12,
                        fill="#eef3fb", stroke=NEG, sw=1.6)
    p.append(b)
    b, bw, bh = textbox(710, 362, "дитина    pid 4022\nfork() повернув 0", size=14, pad=12,
                        fill="#fdeeec", stroke=POS, sw=1.6)
    p.append(b)

    p.append(text(265, 470, "однакове в обох", size=14, color=FIELD, bold=True))
    p.append(text(695, 470, "різне", size=14, color=POS, bold=True))

    p.append(fitbox(60, 482, 410, 104,
                    ["код · сталі · глобальні · купа · стеки",
                     "таблиця дескрипторів · робочий каталог",
                     "uid/gid · обробники сигналів · ліміти"],
                    size=13, fill="#eef7f0", stroke=FIELD, sw=1.4))
    p.append(fitbox(490, 482, 410, 104,
                    ["PID і PPID · значення, що повернув fork()",
                     "черга сигналів порожня · таймери скинуто",
                     "лічильники часу з нуля · замки не перейшли"],
                    size=13, fill="#fdeeec", stroke=POS, sw=1.4))

    render(os.path.join(OUT, "one-call-two-returns.svg"), W, H, *p,
           title="fork: один виклик, два повернення")


# ── Фіг. 2: копіювання при записі ───────────────────────────────────────────
# Ідея: fork копіює ТАБЛИЦІ сторінок, а не сторінки. Обидві таблиці ведуть на
# ті самі кадри, усі записи стають «лише для читання»; фізична копія кадру
# з'являється тільки тоді й тільки там, куди хтось записав.
def fig_cow_pagetables():
    W, H = 1000, 960
    p = []

    PAGES = ["A", "B", "C"]
    ROW_TOP = [70, 360, 650]
    EH, EGAP = 40, 46          # висота запису й крок між записами
    PX, PW = 60, 190           # таблиця батька
    FX, FW = 420, 160          # фізичні кадри
    CX, CW = 750, 190          # таблиця дитини

    def entry_y(row, k):
        return ROW_TOP[row] + 86 + k * EGAP

    def table(x, w, row, title, marks, color):
        out = [text(x + w / 2, ROW_TOP[row] + 72, title, size=13, color=color, bold=True)]
        for k, name in enumerate(PAGES):
            y = entry_y(row, k)
            hot = marks[k].endswith("rw") and row > 0
            out.append(fitbox(x, y, w, EH, "%s  →  %s" % (name, marks[k]), size=13,
                              fill="#fdeeec" if hot else "#f4f6f8",
                              stroke=POS if hot else LINE, sw=1.4))
        return out

    def frames(row, extra=None):
        out = [text(FX + FW / 2, ROW_TOP[row] + 72, "фізичні кадри", size=13,
                    color=MUTED, bold=True)]
        for k, name in enumerate(PAGES):
            y = entry_y(row, k)
            out.append(fitbox(FX, y, FW, EH, "кадр " + name, size=13,
                              fill="#eef7f0", stroke=FIELD, sw=1.4))
        if extra is not None:
            y = entry_y(row, extra)
            out.append(fitbox(615, y, 120, EH, "кадр B′", size=13,
                              fill="#fdeeec", stroke=POS, sw=1.6))
        return out

    def stage(row, caption):
        return text(30, ROW_TOP[row] + 34, caption, size=14.5, color=INK,
                    anchor="start", bold=True)

    # ── ряд 1: до fork ──
    p.append(stage(0, "до fork — одна таблиця веде на свої кадри"))
    p.extend(table(PX, PW, 0, "таблиця сторінок батька", ["rw", "rw", "rw"], NEG))
    p.extend(frames(0))
    for k in range(3):
        p.append(arrow(PX + PW + 6, entry_y(0, k) + EH / 2, FX - 6, entry_y(0, k) + EH / 2,
                       color=NEG))
    p.append(text(CX + CW / 2, entry_y(0, 1) + EH / 2 + 5, "дитини ще немає",
                  size=13, color=MUTED, italic=True))

    # ── ряд 2: одразу після fork ──
    p.append(stage(1, "одразу після fork — дві таблиці, ті самі кадри, запис заборонено"))
    p.extend(table(PX, PW, 1, "таблиця сторінок батька", ["ro", "ro", "ro"], NEG))
    p.extend(table(CX, CW, 1, "таблиця сторінок дитини", ["ro", "ro", "ro"], POS))
    p.extend(frames(1))
    for k in range(3):
        y = entry_y(1, k) + EH / 2
        p.append(arrow(PX + PW + 6, y, FX - 6, y, color=NEG))
        p.append(arrow(CX - 6, y, FX + FW + 6, y, color=POS))

    # ── ряд 3: дитина записала в сторінку B ──
    p.append(stage(2, "дитина записала в B — виняток і копія кадру; право запису повернуто лише їй"))
    p.extend(table(PX, PW, 2, "таблиця сторінок батька", ["ro", "ro", "ro"], NEG))
    p.extend(table(CX, CW, 2, "таблиця сторінок дитини", ["ro", "rw", "ro"], POS))
    p.extend(frames(2, extra=1))
    for k in range(3):
        y = entry_y(2, k) + EH / 2
        p.append(arrow(PX + PW + 6, y, FX - 6, y, color=NEG))
        if k == 1:
            p.append(arrow(CX - 6, y, 735 + 6, y, color=POS))
        else:
            p.append(arrow(CX - 6, y, FX + FW + 6, y, color=POS))

    render(os.path.join(OUT, "cow-pagetables.svg"), W, H, *p,
           title="Копіювання при записі: копіюють таблиці, а не пам'ять")


# ── Фіг. 3: дескриптори після fork ──────────────────────────────────────────
# Ідея: fork копіює ТАБЛИЦЮ дескрипторів (покажчики), але не опис відкритого
# файлу. Тому позиція в файлі лишається одна на двох — і запис одного посуває
# курсор іншому.
def fig_fd_table_share():
    W, H = 900, 620
    p = []

    def fdtable(x, title, color, fill):
        out = [rect(x, 78, 250, 226, fill="#ffffff", stroke=color, sw=1.6, rx=10),
               text(x + 125, 104, title, size=14, color=color, bold=True)]
        rows = ["0  →  термінал", "1  →  out.txt", "2  →  термінал", "3  →  сокет"]
        for k, s in enumerate(rows):
            y = 118 + k * 44
            hot = (k == 1)
            out.append(fitbox(x + 12, y, 226, 36, s, size=13,
                              fill=fill if hot else "#f4f6f8",
                              stroke=color if hot else "#c8ced6", sw=1.5 if hot else 1.1))
        return out

    p.extend(fdtable(50, "таблиця дескрипторів батька", NEG, "#eef3fb"))
    p.extend(fdtable(600, "таблиця дескрипторів дитини", POS, "#fdeeec"))

    # спільний опис відкритого файлу
    p.append(rect(290, 372, 320, 96, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(450, 400, "опис відкритого файлу", size=14, color=INK, bold=True))
    p.append(text(450, 424, "позиція: 4096", size=13, color=INK))
    p.append(text(450, 446, "режим: O_WRONLY   прапорці: O_APPEND", size=12, color=MUTED))

    p.append(arrow(300, 180, 340, 366, color=NEG))
    p.append(arrow(600, 180, 560, 366, color=POS))

    p.append(arrow(450, 470, 450, 512, color=FIELD))
    b, bw, bh = textbox(450, 546, "inode файлу out.txt", size=13.5, pad=11,
                        fill="#f4f6f8", stroke=INK, sw=1.4)
    p.append(b)

    p.append(fitbox(40, 348, 230, 74,
                    ["копіюється покажчик,", "а не сам опис файлу"],
                    size=13, fill="#ffffff", stroke="#c8ced6", sw=1.2))
    p.append(fitbox(630, 348, 230, 74,
                    ["запис одного посуває", "позицію й другому"],
                    size=13, fill="#ffffff", stroke="#c8ced6", sw=1.2))

    render(os.path.join(OUT, "fd-table-share.svg"), W, H, *p,
           title="Після fork дескриптори різні, опис файлу — спільний")


# ── Фіг. 4 (вставка hist): віхи ─────────────────────────────────────────────
# Ідея: ім'я, перша реалізація й семантика копіювання прийшли з РІЗНИХ місць.
# Вертикальна вісь — щоб довгі підписи мали простір і не тулилися боками.
def fig_hist_timeline():
    W, H = 1000, 900
    p = []

    AX = 250                      # вісь часу
    TOP, BOT = 70, 850
    p.append(line(AX, TOP, AX, BOT, color=MUTED, sw=2.2))

    marks = [
        ("1963", "Мелвін Конвей, «A Multiprocessor System Design»",
         ["термін: розвилка (fork) і злиття (join)",
          "теорія багатопроцесорності, не ОС"], NEG),
        ("1964–65", "Project GENIE, SDS 930 (Берклі)",
         ["перша реалізація fork — Пітер Дойч",
          "дитина ДІЛИТЬ простір із батьком"], NEG),
        ("1969", "Unix на PDP-7 — Кен Томпсон",
         ["копія всього процесу через своп",
          "27 рядків асемблера"], POS),
        ("1971", "TENEX на PDP-10 (BBN)",
         ["той самий родовід, є сторінкова пам'ять",
          "fork знову НЕ копіює простору"], NEG),
        ("1974", "Рітчі й Томпсон, CACM",
         ["«по суті такий, як у Берклі»",
          "— спогад, що розходиться з документами"], MUTED),
        ("1979", "Рітчі, «The Evolution of…»; vfork у 3BSD",
         ["визнано: прижився через легкість",
          "реалізації; ціну вже обходять"], POS),
        ("2019", "HotOS: «A fork() in the road»",
         ["привілеї, ціна, відмови пам'яті",
          "заклик вважати fork застарілим"], POS),
    ]

    STEP = (BOT - TOP - 40) / (len(marks) - 1)
    for i, (year, head, body, color) in enumerate(marks):
        y = TOP + 30 + i * STEP
        p.append(circle(AX, y, 9, fill="#ffffff", stroke=color, sw=2.4))
        p.append(text(AX - 26, y + 5, year, size=14.5, color=color,
                      anchor="end", bold=True))
        p.append(fitbox(AX + 30, y - 42, 640, 84, [head] + body, size=13.5,
                        fill="#f4f6f8", stroke="#c8ced6", sw=1.2))

    render(os.path.join(OUT, "hist-fork-timeline.svg"), W, H, *p,
           title="Віхи: звідки прийшли ім'я, реалізація й семантика fork")


# ── Фіг. 5 (вставка hist): три різні контракти під одним іменем ─────────────
# Ідея: слово fork у Genie, у PDP-7-ному Unix і в сучасному POSIX означає три
# різні угоди про пам'ять дитини. Копіювання — не суть виклику, а середина.
def fig_hist_three_forks():
    W, H = 1020, 700
    p = []

    COLS = [
        ("Genie / SDS 940", "1964–65",
         ["дитина ДІЛИТЬ адресний", "простір із батьком", "(або дістає інший набір", "блоків пам'яті)"],
         "копії простору немає й не було", NEG, "#eef3fb"),
        ("Unix на PDP-7", "1969",
         ["дитина дістає ПОВНУ", "копію простору —", "образ батька пишуть", "у ділянку свопінгу"],
         "машина без апарата віртуальної пам'яті", POS, "#fdeeec"),
        ("POSIX сьогодні", "від 1980-х",
         ["копія — СЕМАНТИЧНА:", "таблиці сторінок спільні,", "кадр копіюють лише", "при першому записі"],
         "копіювання при записі приховує ціну", FIELD, "#eef7f0"),
    ]

    CW, GAP = 300, 30
    X0 = (W - (3 * CW + 2 * GAP)) / 2
    for i, (name, when, body, foot, color, fill) in enumerate(COLS):
        x = X0 + i * (CW + GAP)
        p.append(rect(x, 92, CW, 452, fill="#ffffff", stroke=color, sw=1.8, rx=12))
        p.append(text(x + CW / 2, 126, name, size=15, color=color, bold=True))
        p.append(text(x + CW / 2, 150, when, size=13, color=MUTED))
        p.append(fitbox(x + 18, 176, CW - 36, 132, body, size=13.5,
                        fill=fill, stroke=color, sw=1.3))
        p.append(text(x + CW / 2, 344, "що спричинило форму", size=12.5,
                      color=MUTED, bold=True))
        p.append(fitbox(x + 18, 360, CW - 36, 78, foot, size=13,
                        fill="#f4f6f8", stroke="#c8ced6", sw=1.2))
        p.append(text(x + CW / 2, 470, "ціна виклику", size=12.5, color=MUTED, bold=True))
        cost = ["майже стала", "росте з обсягом пам'яті", "росте з КІЛЬКІСТЮ відображень"][i]
        p.append(fitbox(x + 18, 484, CW - 36, 44, cost, size=13,
                        fill="#ffffff", stroke=color, sw=1.3))

    p.append(text(W / 2, 50, "Одне ім'я — три різні угоди про пам'ять дитини",
                  size=16, color=INK, bold=True))
    p.append(fitbox(X0, 578, 3 * CW + 2 * GAP, 76,
                    ["Копіювання адресного простору успадковане не від ідеї розвилки, а від однієї машини:",
                     "PDP-7 не мав апарата віртуальної пам'яті, тож «зробити копію» вже вміли — через своп."],
                    size=13.5, fill="#f4f6f8", stroke=INK, sw=1.4))

    render(os.path.join(OUT, "hist-three-forks.svg"), W, H, *p,
           title="Genie, PDP-7, POSIX: три контракти під іменем fork")


fig_one_call_two_returns()
# ── Фіг. proj-1: затримка fork від обсягу відображеної пам'яті ──────────────
# Ідея: вимір дає ПРЯМУ, і нахил її — це 8 байтів запису таблиці на кожні
# 4 КіБ пам'яті. Дві інші прямі майже нульові, але з різних причин: незачеплену
# пам'ять ядро не копіює взагалі, а великі сторінки зменшують кількість записів.
def fig_fork_latency_vs_size():
    W, H = 1000, 600
    p = []

    X0, X1 = 130.0, 930.0        # вісь обсягу: 0…8 ГіБ
    YB, YT = 460.0, 130.0        # вісь часу: 0…8 мс (YB — низ)

    def px(gib):
        return X0 + gib / 8.0 * (X1 - X0)

    def py(ms):
        return YB - ms / 8.0 * (YB - YT)

    # осі
    p.append(line(X0, YB, X1 + 14, YB, color=INK, sw=1.8))
    p.append(line(X0, YB, X0, YT - 12, color=INK, sw=1.8))
    for g in (2, 4, 6, 8):
        p.append(line(px(g), YB, px(g), YB + 6, color=INK, sw=1.4))
        p.append(text(px(g), YB + 24, str(g), size=13, color=MUTED))
    for m in (2, 4, 6, 8):
        p.append(line(X0 - 6, py(m), X0, py(m), color=INK, sw=1.4))
        p.append(text(X0 - 12, py(m) + 4.5, str(m), size=13, color=MUTED, anchor="end"))
    p.append(text(px(4), YB + 52, "обсяг відображеної пам'яті, ГіБ", size=14, color=INK))
    p.append(text(X0 - 4, YT - 24, "затримка fork, мс", size=14, color=INK, anchor="start"))

    # пряма: зачеплено, звичайні сторінки 4 КіБ
    p.append(line(px(0), py(0.15), px(8), py(7.35), color=NEG, sw=2.6))
    # майже нульові прямі
    p.append(line(px(0), py(0.16), px(8), py(0.17), color=POS, sw=2.2, dash="7 5"))
    p.append(line(px(0), py(0.05), px(8), py(0.05), color=MUTED, sw=2.2, dash="3 4"))

    p.append(fitbox(150, 152, 384, 70,
                    ["зачеплено, звичайні сторінки 4 КіБ:",
                     "пряма з нахилом ≈ 0.9 мс на ГіБ",
                     "8 Б таблиці на кожні 4 КіБ = 1/512"],
                    size=13, fill="#eef3fb", stroke=NEG, sw=1.5))
    p.append(arrow(468, 224, 556, 292, color=NEG, sw=1.6))

    p.append(fitbox(468, 352, 474, 76,
                    ["обидві плоскі прямі — з РІЗНИХ причин:",
                     "пам'ять лише відображено → таблиць ядро не копіює",
                     "зачеплено великими сторінками → записів у 512 разів менше"],
                    size=13, fill="#fdeeec", stroke=POS, sw=1.5))
    p.append(arrow(700, 428, 700, 448, color=POS, sw=1.6))

    render(os.path.join(OUT, "fork-latency-vs-size.svg"), W, H, *p,
           title="Затримка fork росте прямо пропорційно до відображеної пам'яті")


# ── Фіг. proj-2: що показує smaps_rollup у батька до й після fork ───────────
# Ідея: Rss не ворухнеться в жодному переході. Рухається лише поділ «спільна /
# власна»: fork робить усі сторінки спільними, а кожен запис батька викуповує
# свою сторінку назад. Саме приріст Private_Dirty і є ціною копіювання.
def fig_cow_smaps_states():
    W, H = 1000, 640
    p = []

    BW = 150.0                     # ширина стовпця
    YB, YT = 460.0, 140.0          # низ і верх стовпця: 320 px = 512 МіБ
    K = (YB - YT) / 512.0

    BLUE_F, RED_F = "#dbe6fb", "#fbe0dc"

    # легенда
    p.append(rect(286, 50, 20, 15, fill=BLUE_F, stroke=NEG, sw=1.5, rx=3))
    p.append(text(314, 63, "Private_Dirty — власна сторінка", size=13,
                  color=INK, anchor="start"))
    p.append(rect(578, 50, 20, 15, fill=RED_F, stroke=POS, sw=1.5, rx=3))
    p.append(text(606, 63, "Shared_Dirty — спільна", size=13, color=INK, anchor="start"))

    STATES = [
        (200.0, "до fork", 512, 0, 512),
        (500.0, "одразу після fork\n(дитина ще жива)", 0, 512, 256),
        (800.0, "батько записав\nу 64 МіБ", 64, 448, 288),
    ]
    for cx, name, priv, shar, pss in STATES:
        b, bw, bh = textbox(cx, 100, name, size=13.5, pad=9,
                            fill="#ffffff", stroke="#c8ced6", sw=1.3)
        p.append(b)
        if shar:
            p.append(rect(cx - BW / 2, YT, BW, shar * K, fill=RED_F, stroke=POS, sw=1.6, rx=4))
        if priv:
            p.append(rect(cx - BW / 2, YB - priv * K, BW, priv * K,
                          fill=BLUE_F, stroke=NEG, sw=1.6, rx=4))
        yp = YB - pss * K
        p.append(line(cx - BW / 2 - 10, yp, cx + BW / 2 + 10, yp,
                      color=FIELD, sw=2.0, dash="6 4"))
        p.append(text(cx + BW / 2 + 16, yp + 4.5, "Pss", size=12.5,
                      color=FIELD, anchor="start", bold=True))
        p.append(fitbox(cx - 130, 492, 260, 106,
                        ["Rss  512 МіБ",
                         "Pss  %d МіБ" % pss,
                         "Private_Dirty  %d МіБ" % priv,
                         "Shared_Dirty  %d МіБ" % shar],
                        size=13, fill="#f4f6f8", stroke="#c8ced6", sw=1.2))

    p.append(text(W / 2, 622,
                  "Rss однаковий у всіх трьох станах — рухається лише поділ на власне й спільне",
                  size=13.5, color=MUTED))

    render(os.path.join(OUT, "cow-smaps-states.svg"), W, H, *p,
           title="Ділянка на 512 МіБ очима /proc/self/smaps_rollup")


fig_cow_pagetables()
fig_fd_table_share()
fig_hist_timeline()
fig_hist_three_forks()
fig_fork_latency_vs_size()
fig_cow_smaps_states()
print("готово:", OUT)
