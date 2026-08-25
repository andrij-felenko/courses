# -*- coding: utf-8 -*-
"""Фігури до теми «su: перемикання на іншого користувача»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_su_path():
    """Шлях одного запуску su: крок ліворуч, хто його вирішує — праворуч."""
    W, H = 1320, 1000
    f = []

    f.append(text(660, 46, "su - postgres", size=17, bold=True))

    steps = [
        ("exec /bin/su, на файлі біт setuid:\neuid стає 0, ruid лишається вашим",
         "ядро, за бітом на файлі"),
        ("пошук цілі: uid, gid, домівка, оболонка",
         "база облікових записів через getpwnam(),\nне ядро"),
        ("PAM питає пароль ЦІЛІ\n(у root не питають — pam_rootok)",
         "стек /etc/pam.d/su, з тире — su-l"),
        ("fork(): далі йдуть два процеси",
         "батько лишається root — закрити сеанс PAM,\nдочекатися дитини, переслати сигнали"),
        ("setgid і додаткові групи цілі,\nаж ПОТІМ setuid — усі три числа цільові",
         "після setuid прав на це вже немає:\nпорядок незворотний"),
        ("перебудова оточення",
         "обсяг чистки задає тире в командному рядку"),
        ("exec оболонки цілі",
         "argv[0] = «-bash» робить її вхідною"),
    ]

    y = 118
    for i, (step, source) in enumerate(steps):
        fill = "#fdecea" if i == 3 else FILL
        stroke = POS if i == 3 else LINE
        b, _, h = textbox(330, y, step, size=14, min_w=520, fill=fill, stroke=stroke)
        f.append(b)
        b2, _, _ = textbox(1000, y, source, size=13, min_w=560,
                           fill="#eef3fd", stroke=NEG, color=INK)
        f.append(b2)
        if i < len(steps) - 1:
            f.append(arrow(330, y + h / 2 + 6, 330, y + 116 - h / 2 - 6))
        y += 116

    b, _, _ = textbox(660, y + 30,
                      "процес той самий не став іншим — його просто немає:\n"
                      "оболонка цілі є ОКРЕМИМ процесом усередині вашого сеансу",
                      size=14, min_w=880, fill="#eafaf0", stroke=FIELD)
    f.append(b)

    render(os.path.join(OUT, 'su-path.svg'), W, H, *f,
           title="Послідовність одного запуску su і джерело кожного рішення")


def fig_changes_and_leftovers():
    """Що змінюється разом із числами, а що лишається від вашого сеансу."""
    W, H = 1240, 800
    f = []

    b, _, _ = textbox(620, 52, "нова оболонка після su - postgres",
                      size=16, bold=True, min_w=520)
    f.append(b)

    f.append(arrow(620, 86, 320, 128))
    f.append(arrow(620, 86, 920, 128))

    b, _, _ = textbox(320, 156, "змінилося: те, що є числом",
                      size=15, bold=True, min_w=460, fill="#eafaf0", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(920, 156, "лишилося вашим: те, що є сеансом",
                      size=15, bold=True, min_w=460, fill="#fdecea", stroke=POS)
    f.append(b)

    changed = [
        "реальний, діючий і збережений uid",
        "gid і перелік додаткових груп",
        "HOME і SHELL, а з тире —\nще PATH, USER, LOGNAME і поточна тека",
        "усе, що ядро звіряє на доступ\nдо файлів і сигналів",
    ]
    stayed = [
        "керуючий термінал — той самий",
        "сеанс входу — той самий",
        "loginuid для аудиту: незмінний,\nтож журнал і далі знає ваше ім'я",
        "cgroup і сеанс logind — ваші,\nразом з обліком ресурсів",
        "дескриптори 0, 1, 2 — ваш термінал",
        "батьківський su чекає на вихід",
    ]

    y = 240
    for s in changed:
        b, _, h = textbox(320, y, s, size=13, min_w=470)
        f.append(b)
        y += 86

    y = 240
    for s in stayed:
        b, _, h = textbox(920, y, s, size=13, min_w=470)
        f.append(b)
        y += 86

    b, _, _ = textbox(620, 740,
                      "усі пастки теми живуть у правій колонці:\n"
                      "слово «стати» обіцяє її теж, а механізм її не чіпає",
                      size=14, min_w=760, fill="#eef3fd", stroke=NEG)
    f.append(b)

    render(os.path.join(OUT, 'changes-and-leftovers.svg'), W, H, *f,
           title="Що su міняє і що лишає від вашого сеансу")


def fig_identity_order():
    """Три виклики в дитині: правильний порядок і зворотний, зі станом після кожного."""
    W, H = 1400, 900
    f = []

    b, _, _ = textbox(700, 60,
                      "дитина одразу після fork(): ruid 1000 (andrij) · euid 0 · gid 1000 ·"
                      " додаткові групи {1000, 10 wheel}\n"
                      "exec із бітом setuid підняв лише uid — групи й gid лишилися вашими",
                      size=15, min_w=1200, fill="#fdf6e3", stroke=LINE)
    f.append(b)

    f.append(arrow(700, 100, 370, 156))
    f.append(arrow(700, 100, 1030, 156))

    b, _, _ = textbox(370, 186, "групи → gid → uid",
                      size=16, bold=True, min_w=560, fill="#eafaf0", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(1030, 186, "uid першим",
                      size=16, bold=True, min_w=560, fill="#fdecea", stroke=POS)
    f.append(b)

    right = [
        'initgroups("postgres", 999) → 0\nдодаткові групи стали {999}',
        "setgid(999) → 0\nусі три групові числа — 999",
        "setuid(999) → 0\nусі три користувацькі — 999, root зник",
    ]
    wrong = [
        "setuid(999) → 0\nroot зник просто зараз",
        "setgid(999) → -1, EPERM\ngid лишився 1000 — вашим",
        'initgroups("postgres", 999) → -1, EPERM\nдодаткові групи лишилися {1000, 10}',
    ]

    y = 300
    for i in range(3):
        b, _, h = textbox(370, y, right[i], size=14, min_w=560)
        f.append(b)
        b, _, h2 = textbox(1030, y, wrong[i], size=14, min_w=560)
        f.append(b)
        if i < 2:
            f.append(arrow(370, y + h / 2 + 6, 370, y + 130 - h / 2 - 6))
            f.append(arrow(1030, y + h2 / 2 + 6, 1030, y + 130 - h2 / 2 - 6))
        y += 130

    b, _, _ = textbox(370, y + 30,
                      "postgres:postgres, груп більше немає —\n"
                      "рівно та ідентичність, яку дав би справжній вхід",
                      size=14, min_w=560, fill="#eafaf0", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(1030, y + 30,
                      "uid postgres, gid andrij, wheel при собі —\n"
                      "нові файли ваші, доступ по wheel відкритий",
                      size=14, min_w=560, fill="#fdecea", stroke=POS)
    f.append(b)

    b, _, _ = textbox(700, y + 130,
                      "обидві помилки мовчазні: значення повертається, і програма,\n"
                      "яка на нього не подивилася, вважає, що все вдалося",
                      size=14, min_w=900, fill="#eef3fd", stroke=NEG)
    f.append(b)

    render(os.path.join(OUT, 'identity-order.svg'), W, H, *f,
           title="Три виклики зміни ідентичності: правильний порядок і зворотний")


def fig_shell_and_path():
    """Дві драбини вибору: яка оболонка запуститься і який PATH вона дістане."""
    W, H = 1300, 640
    f = []

    b, _, _ = textbox(330, 52, "яку оболонку запустить su",
                      size=16, bold=True, min_w=520, fill="#eafaf0", stroke=FIELD)
    f.append(b)
    b, _, _ = textbox(960, 52, "який PATH дістане нова оболонка",
                      size=16, bold=True, min_w=560, fill="#eef3fd", stroke=NEG)
    f.append(b)

    f.append(text(330, 102, "діє перше правило, що спрацювало", size=13, color=MUTED))
    f.append(text(960, 102, "діє перше правило, що спрацювало", size=13, color=MUTED))

    shells = [
        "--shell SH\n(для не-root ігнорується, якщо оболонки цілі\nнемає в /etc/shells)",
        "$SHELL — тільки коли задано -m / -p\n(та сама умова про /etc/shells)",
        "оболонка цілі з бази облікових записів",
        "/bin/sh",
    ]
    paths = [
        "-m / -p → PATH лишається вашим",
        "- / -l → PATH складається з login.defs",
        "інакше: ALWAYS_SET_PATH=yes → з login.defs,\nні → лишається вашим",
    ]

    y = 170
    for i, s in enumerate(shells):
        b, _, h = textbox(330, y, s, size=13, min_w=540)
        f.append(b)
        if i < len(shells) - 1:
            f.append(arrow(330, y + h / 2 + 6, 330, y + 118 - h / 2 - 6))
        y += 118

    y = 170
    for i, s in enumerate(paths):
        b, _, h = textbox(960, y, s, size=13, min_w=580)
        f.append(b)
        if i < len(paths) - 1:
            f.append(arrow(960, y + h / 2 + 6, 960, y + 118 - h / 2 - 6))
        y += 118

    b, _, _ = textbox(960, 486,
                      "«з login.defs» означає:\n"
                      "ціль root → ENV_SUPATH, а як порожній — ENV_ROOTPATH\n"
                      "будь-яка інша ціль → ENV_PATH",
                      size=13, min_w=580, fill="#f6f2ea", stroke=MUTED)
    f.append(b)

    b, _, _ = textbox(650, 596,
                      "жодна з драбин не питає вашої згоди:\n"
                      "що саме спрацювало, показує тільки echo $PATH і echo $0 всередині",
                      size=14, min_w=900, fill="#f4f6f8", stroke=LINE)
    f.append(b)

    render(os.path.join(OUT, 'su-shell-and-path.svg'), W, H, *f,
           title="Вибір оболонки і вибір PATH у su: два порядки правил")


fig_su_path()
fig_changes_and_leftovers()
fig_identity_order()
fig_shell_and_path()
print("готово")
