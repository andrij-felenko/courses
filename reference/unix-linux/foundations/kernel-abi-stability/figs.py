# -*- coding: utf-8 -*-
"""Фігури до теми «Не ламати простір користувача»: сталість ABI ядра."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL = "#fdecea"
GREY_FILL = "#f4f6f8"


# ── 1. Чотири виходи: працюють для бібліотеки, не працюють для ядра ─────────
def fig_no_escape():
    W, H = 1000, 500
    C1X, C1W = 40, 260          # спосіб
    C2X, C2W = 320, 320         # бібліотека
    C3X, C3W = 660, 300         # ядро
    HDY, HDH = 52, 44
    ROWY, ROWH, GAP = 112, 78, 14
    f = []

    f.append(fitbox(C1X, HDY, C1W, HDH, "Спосіб пережити зміну",
                    size=15, bold=True, fill=GREY_FILL, stroke=MUTED))
    f.append(fitbox(C2X, HDY, C2W, HDH, "Бібліотека простору користувача",
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(C3X, HDY, C3W, HDH, "Ядро",
                    size=15, bold=True, fill=RED_FILL, stroke=POS))

    rows = [
        ("Поставити дві версії\nпоруч",
         "libfoo.so.2 і libfoo.so.3\nспокійно лежать разом",
         "на машині виконується\nрівно одне ядро"),
        ("Позначити в бінарнику,\nяку версію він хоче",
         "версіонування символів:\nмітка в кожному файлі",
         "бінарник кладе номер\nвиклику в регістр — і все"),
        ("Перезібрати всіх,\nхто залежить",
         "дистрибутив володіє\nвихідними текстами",
         "чужу, закриту, покинуту\nпрограму не перезбере ніхто"),
        ("Утекти від залежності",
         "злінкувати статично\nй нести з собою",
         "системного виклику\nстатикою не заміниш"),
    ]
    for i, (a, b, c) in enumerate(rows):
        y = ROWY + i * (ROWH + GAP)
        f.append(fitbox(C1X, y, C1W, ROWH, a, size=14, bold=True))
        f.append(fitbox(C2X, y, C2W, ROWH, b, size=14,
                        fill=GREEN_FILL, stroke=FIELD))
        f.append(fitbox(C3X, y, C3W, ROWH, c, size=14,
                        fill=RED_FILL, stroke=POS))

    f.append(fitbox(C1X, 448, C3X + C3W - C1X, 40,
                    "лишається єдиний вихід: не міняти того, що вже випущено",
                    size=15, bold=True, color=POS, fill=BG, stroke=POS))

    render(os.path.join(IMG, 'no-escape.svg'), W, H, *f,
           title="Чотири способи пережити несумісну зміну — і жодного в ядра")


# ── 2. Дві умови розширюваності ────────────────────────────────────────────
def fig_extension_protocol():
    W, H = 1000, 640
    f = []

    # ── панель А: невідомий біт прапорців ──
    f.append(rect(30, 48, W - 60, 226, fill=BG, stroke=MUTED, sw=1.2))
    f.append(fitbox(50, 62, 300, 40, "Невідомий біт прапорців",
                    size=15, bold=True, fill=GREY_FILL, stroke=MUTED))

    f.append(fitbox(50, 122, 240, 62,
                    "програма передала біт,\nякого ядро не знає", size=14))
    f.append(arrow(290, 153, 348, 122))
    f.append(arrow(290, 153, 348, 216))

    f.append(fitbox(352, 96, 250, 54, "ядро мовчки ігнорує",
                    size=14, bold=True, fill=RED_FILL, stroke=POS))
    f.append(fitbox(624, 96, 340, 54,
                    "біт мертвий назавжди: успіх нічого не означає",
                    size=13, fill=BG, stroke=POS))
    f.append(arrow(606, 123, 620, 123))

    f.append(fitbox(352, 190, 250, 54, "ядро відкидає з EINVAL",
                    size=14, bold=True, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(624, 190, 340, 54,
                    "біт можна наповнити сенсом пізніше",
                    size=13, fill=BG, stroke=FIELD))
    f.append(arrow(606, 217, 620, 217))

    # ── панель Б: структура з полем розміру ──
    f.append(rect(30, 300, W - 60, 306, fill=BG, stroke=MUTED, sw=1.2))
    f.append(fitbox(50, 314, 420, 40,
                    "Структура, перше поле якої — її розмір",
                    size=15, bold=True, fill=GREY_FILL, stroke=MUTED))
    f.append(fitbox(500, 314, 464, 40,
                    "нуль у новому полі означає типову поведінку",
                    size=14, color=MUTED, fill=BG, stroke=MUTED, sw=1.0))

    cases = [
        ("usize < ksize", "програма старша за ядро",
         "ядро доповнює хвіст нулями", "виклик працює", GREEN_FILL, FIELD),
        ("usize = ksize", "розміри збіглися",
         "копіювати як є", "виклик працює", GREEN_FILL, FIELD),
        ("usize > ksize", "програма новіша за ядро",
         "хвіст нульовий → працює,\nненульовий → E2BIG", "мовчати не можна",
         RED_FILL, POS),
    ]
    for i, (head, sub, act, res, fill, stroke) in enumerate(cases):
        x = 50 + i * 306
        f.append(fitbox(x, 372, 288, 44, head, size=15, bold=True,
                        fill=fill, stroke=stroke))
        f.append(fitbox(x, 424, 288, 44, sub, size=13, color=MUTED,
                        fill=BG, stroke=MUTED, sw=1.0))
        f.append(fitbox(x, 476, 288, 60, act, size=13))
        f.append(fitbox(x, 546, 288, 44, res, size=14, bold=True,
                        fill=fill, stroke=stroke))

    render(os.path.join(IMG, 'extension-protocol.svg'), W, H, *f,
           title="Розширювати можна лише те, що не мовчить про невідоме")


# ── 3. Драбина прибирання інтерфейсу ───────────────────────────────────────
def fig_removal_funnel():
    W, H = 1020, 500
    SX, SW = 30, 250            # колонка стадій
    COLS = [(300, 226), (546, 226), (792, 198)]
    HDY, HDH = 52, 46
    ROWY, ROWH, GAP = 116, 74, 12
    f = []

    f.append(fitbox(SX, HDY, SW, HDH, "Стадія",
                    size=15, bold=True, fill=GREY_FILL, stroke=MUTED))
    heads = ["виклик sysctl", "формат a.out", "сторінка vsyscall"]
    for (x, w), h in zip(COLS, heads):
        f.append(fitbox(x, HDY, w, HDH, h, size=15, bold=True,
                        fill=GREY_FILL, stroke=MUTED))

    rows = [
        ("Оголосити застарілим",
         [("замінений на /proc/sys", GREEN_FILL, FIELD),
          ("ELF від 1995 року", GREEN_FILL, FIELD),
          ("оголошено легасі", GREEN_FILL, FIELD)]),
        ("Виміряти: чи хтось лишився",
         [("нікого: вимкнений\nу конфігураціях", GREEN_FILL, FIELD),
          ("один: інструменти\nдля Atari Jaguar", RED_FILL, POS),
          ("є: старі статичні\nбінарники", RED_FILL, POS)]),
        ("Дати заміну тим, хто лишився",
         [("не знадобилася", GREY_FILL, MUTED),
          ("обгортка на ELF,\nперевірена автором", GREEN_FILL, FIELD),
          ("vDSO є, але старого\nне перезібрати", RED_FILL, POS)]),
        ("Прибрати",
         [("ядро 5.5", GREEN_FILL, FIELD),
          ("ядро 5.19, x86", GREEN_FILL, FIELD),
          ("не прибрано:\nvsyscall=emulate", RED_FILL, POS)]),
    ]
    for i, (stage, cells) in enumerate(rows):
        y = ROWY + i * (ROWH + GAP)
        f.append(fitbox(SX, y, SW, ROWH, stage, size=14, bold=True))
        for (x, w), (txt, fill, stroke) in zip(COLS, cells):
            f.append(fitbox(x, y, w, ROWH, txt, size=13,
                            fill=fill, stroke=stroke))

    f.append(fitbox(SX, 460, COLS[2][0] + COLS[2][1] - SX, 34,
                    "прибирають не за строком, а за доведеною відсутністю користувачів",
                    size=14, bold=True, color=MUTED, fill=BG, stroke=MUTED, sw=1.0))

    render(os.path.join(IMG, 'removal-funnel.svg'), W, H, *f,
           title="Драбина прибирання інтерфейсу і три реальні шляхи по ній")


# ── 4. Як правило твердішало (вставка hist) ────────────────────────────────
def fig_rule_timeline():
    DX, DW = 40, 250            # колонка дати
    EX, EW = 320, 660           # колонка події
    ROWY, ROWH, GAP = 108, 70, 12
    W = EX + EW + 40
    f = []

    f.append(fitbox(DX, 46, DW, 44, "Коли", size=15, bold=True,
                    fill=GREY_FILL, stroke=MUTED))
    f.append(fitbox(EX, 46, EW, 44, "Що сталося з правилом", size=15,
                    bold=True, fill=GREY_FILL, stroke=MUTED))

    rows = [
        ("1991 — 2003", "Правила немає: ламати можна\nв непарній гілці розробки",
         GREY_FILL, MUTED),
        ("липень 2004", "Гілки розробки більше не буде —\nкожен випуск іде просто до людей",
         RED_FILL, POS),
        ("грудень 2005", "Сварка про udev: правило\nвимовлено вголос уперше",
         GREEN_FILL, FIELD),
        ("2005 — 2006", "Спроби записати наперед:\nграфік прибирання, тека ABI",
         GREY_FILL, MUTED),
        ("жовтень 2012", "Межу переносять у include/uapi:\nобіцянка дістає адресу",
         GREEN_FILL, FIELD),
        ("2012", "Графік прибирання видалено:\nсхема наперед не працює",
         RED_FILL, POS),
        ("грудень 2012", "«WE DO NOT BREAK USERSPACE!» —\nправило стає гаслом",
         GREEN_FILL, FIELD),
        ("2020 — 2022", "Трекер, бот і текст у дереві:\nгасло дістає процедуру",
         GREEN_FILL, FIELD),
    ]
    for i, (when, what, fill, stroke) in enumerate(rows):
        y = ROWY + i * (ROWH + GAP)
        f.append(fitbox(DX, y, DW, ROWH, when, size=14, bold=True))
        f.append(fitbox(EX, y, EW, ROWH, what, size=14,
                        fill=fill, stroke=stroke))

    H = ROWY + len(rows) * (ROWH + GAP) + 40
    render(os.path.join(IMG, 'rule-timeline.svg'), W, H, *f,
           title="Як правило «не ламати простір користувача» твердішало")


# ── 5. Що чим пробувати і з чим це плутають (вставка proj) ─────────────────
def fig_probe_answers():
    W, H = 1180, 706
    C1X, C1W = 30, 230
    C2X, C2W = 270, 340
    C3X, C3W = 620, 200
    C4X, C4W = 830, 320
    HDY, HDH = 48, 48
    ROWY, ROWH, GAP = 112, 76, 12
    f = []

    heads = [
        (C1X, C1W, "Що саме питаємо"),
        (C2X, C2W, "Чим пробувати, не лишаючи слідів"),
        (C3X, C3W, "«Немає» звучить як"),
        (C4X, C4W, "Легко сплутати з"),
    ]
    for x, w, h in heads:
        f.append(fitbox(x, HDY, w, HDH, h, size=15, bold=True,
                        fill=GREY_FILL, stroke=MUTED))

    rows = [
        ("чи є цей виклик\nу ядрі взагалі",
         "syscall(__NR_openat2, -1, \"\", NULL, 0)\nусі аргументи навмисно негодящі",
         "ENOSYS", "ENOSYS від seccomp-фільтра\nу контейнері", GREEN_FILL, FIELD),
        ("чи знає ядро\nцей біт прапорців",
         "memfd_create(NULL,\nMFD_CLOEXEC | MFD_HUGETLB)",
         "EINVAL", "EINVAL через будь-який\nінший негодящий аргумент",
         GREEN_FILL, FIELD),
        ("чи знає ядро\nце поле структури",
         "передати свій sizeof і нулі\nв усьому, крім потрібного поля",
         "E2BIG", "EFAULT на поганому\nвказівнику структури",
         GREEN_FILL, FIELD),
        ("чи є ця підсистема",
         "statfs(\"/sys/fs/cgroup\")\nабо open() потрібного файлу",
         "ENOENT,\nінший f_type",
         "/proc чи /sys узагалі\nне змонтовано", GREY_FILL, MUTED),
        ("чи вміє це саме\nця файлова система",
         "тільки справжня дія\nна справжніх дескрипторах",
         "EOPNOTSUPP,\nEXDEV",
         "відповідь не глобальна:\nкешувати її не можна", RED_FILL, POS),
        ("чи дозволено це мені",
         "це питання не про можливість,\nа про права",
         "EPERM,\nEACCES",
         "«ядро старе» — насправді\n«вам сюди не можна»", RED_FILL, POS),
    ]
    for i, (a, b, c, d, fill, stroke) in enumerate(rows):
        y = ROWY + i * (ROWH + GAP)
        f.append(fitbox(C1X, y, C1W, ROWH, a, size=14, bold=True))
        f.append(fitbox(C2X, y, C2W, ROWH, b, size=13,
                        fill=BG, stroke=MUTED, sw=1.0))
        f.append(fitbox(C3X, y, C3W, ROWH, c, size=14, bold=True,
                        fill=fill, stroke=stroke))
        f.append(fitbox(C4X, y, C4W, ROWH, d, size=13,
                        fill=fill, stroke=stroke))

    f.append(fitbox(C1X, 654, C4X + C4W - C1X, 38,
                    "висновок «є» всюди звучить однаково: прилетіло будь-що, крім свого коду «немає»",
                    size=14, bold=True, color=MUTED, fill=BG, stroke=MUTED, sw=1.0))

    render(os.path.join(IMG, 'probe-answers.svg'), W, H, *f,
           title="Кожне покоління інтерфейсу має власний код «мене тут немає»")


# ── 6. Три області кешування проби (вставка proj) ──────────────────────────
def fig_probe_cache_scope():
    W, H = 1030, 452
    COLS = [(30, 300), (365, 300), (700, 300)]
    f = []

    heads = [
        ("Спитати один раз", GREEN_FILL, FIELD),
        ("Перепитати після зміни контексту", GREY_FILL, MUTED),
        ("Не кешувати ніколи", RED_FILL, POS),
    ]
    for (x, w), (h, fill, stroke) in zip(COLS, heads):
        f.append(fitbox(x, 44, w, 50, h, size=15, bold=True,
                        fill=fill, stroke=stroke))

    band = [
        ("Від чого залежить відповідь",
         ["тільки від коду ядра,\nяке зараз виконується",
          "від фільтрів і прав\nсамого процесу",
          "від файлу, файлової системи\nчи конкретного пристрою"]),
        ("Приклад",
         ["чи є openat2;\nчи знають MFD_HUGETLB",
          "seccomp, накладений після старту;\nскинуті можливості; зміна uid",
          "copy_file_range між різними ФС;\nioctl конкретного драйвера"]),
        ("Коли відповідь застаріває",
         ["поки процес живий — ніколи",
          "після seccomp, setuid,\nвходу в чужий простір імен",
          "щоразу: EOPNOTSUPP і EXDEV\nобробляють на місці виклику"]),
    ]
    y = 108
    for label, cells in band:
        f.append(text(30, y + 18, label, size=13, bold=True,
                      color=MUTED, anchor="start"))
        y += 30
        for (x, w), txt in zip(COLS, cells):
            f.append(fitbox(x, y, w, 62, txt, size=13))
        y += 76

    f.append(fitbox(30, 398, 970, 36,
                    "кеш проби — це твердження про ядро; усе, що залежить від об'єкта чи прав, твердженням про ядро не є",
                    size=14, bold=True, fill=BG, stroke=MUTED, sw=1.0))

    render(os.path.join(IMG, 'probe-cache-scope.svg'), W, H, *f,
           title="Що з відповіді проби можна запам'ятати, а що ні")


if __name__ == '__main__':
    fig_no_escape()
    fig_extension_protocol()
    fig_removal_funnel()
    fig_rule_timeline()
    fig_probe_answers()
    fig_probe_cache_scope()
    print('ok')
