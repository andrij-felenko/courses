# -*- coding: utf-8 -*-
"""Фігури до теми «sudo: підвищення прав за правилами sudoers»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_rule_anatomy():
    """Рядок sudoers, розкладений на п'ять питань."""
    W, H = 1180, 620
    f = []

    f.append(text(590, 52,
                  "alice   db-*.example.org = (postgres) NOPASSWD: /usr/bin/pg_dump",
                  size=16, bold=True))

    rows = [
        ("alice",            "кому: користувач, %група або +мережева група"),
        ("db-*.example.org", "на яких машинах діє це правило"),
        ("(postgres)",       "від чийого імені виконати (типово root)"),
        ("NOPASSWD:",        "за якої умови: чи потрібен доказ присутності"),
        ("/usr/bin/pg_dump", "що саме дозволено — повний шлях і аргументи"),
    ]

    y = 130
    for token, question in rows:
        b, _, _ = textbox(250, y, token, size=14, bold=True, min_w=340, fill="#eef3fd", stroke=NEG)
        f.append(b)
        f.append(arrow(424, y, 456, y))
        b, _, _ = textbox(800, y, question, size=14, min_w=680)
        f.append(b)
        y += 92

    b, _, _ = textbox(590, 560,
                      "жодного з цих п'яти питань ядро не бачить: воно знає лише числа процесу й біти в inode",
                      size=14, min_w=900, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(OUT, 'rule-anatomy.svg'), W, H, *f,
           title="Правило sudoers і п'ять питань, на які воно відповідає")


def fig_sudo_path():
    """Шлях одного запуску: крок ліворуч, джерело відповіді праворуч."""
    W, H = 1180, 790
    f = []

    steps = [
        ("exec /usr/bin/sudo, біт setuid:\neuid стає 0, ruid лишається вашим",
         "ядро, за бітом на файлі"),
        ("читання /etc/sudoers, режим 0440",
         "файл, доступний лише root"),
        ("пошук правила: виграє останній збіг",
         "звідси беруться повноваження"),
        ("автентифікація прохача через PAM\n(свіжий квиток у /run/sudo/ts пропускає крок)",
         "доказ присутності — від людини"),
        ("перебудова оточення: env_reset, secure_path",
         "білий список із файлу політики"),
        ("ruid, euid і suid стають цільовими",
         "ядро, на прохання самого sudo"),
        ("exec цільової програми",
         "далі sudo вже нічого не вирішує"),
    ]

    y = 80
    for i, (step, source) in enumerate(steps):
        b, _, _ = textbox(520, y, step, size=14, min_w=560)
        f.append(b)
        b, _, _ = textbox(990, y, source, size=13, min_w=340, fill="#f9fafb", stroke=MUTED, color=MUTED)
        f.append(b)
        if i < len(steps) - 1:
            f.append(arrow(520, y + 36, 520, y + 69))
        y += 105

    render(os.path.join(OUT, 'sudo-path.svg'), W, H, *f,
           title="Шлях одного запуску sudo і джерело кожної відповіді")


def fig_granted_vs_reachable():
    """Мета, дозвіл і насправді досяжне — три вкладені області."""
    W, H = 1180, 590
    f = []

    f.append(rect(40, 40, 1100, 490, fill="#fdecea", stroke=POS, sw=2))
    f.append(rect(110, 150, 960, 350, fill="#f4f6f8", stroke=LINE, sw=1.8))
    f.append(rect(190, 270, 800, 210, fill="#e9f7ef", stroke=FIELD, sw=1.8))

    f.append(text(590, 78, "насправді досяжне", size=15, bold=True, color=POS))
    f.append(text(590, 104, "оболонка з !sh у переглядачі · find -exec · копія програми в обхід «!»", size=13))
    f.append(text(590, 128, "тобто повний root", size=13))

    f.append(text(590, 188, "що дозволив рядок правила", size=15, bold=True))
    f.append(text(590, 214, "усе, чого можна домогтися від цієї програми з правами root", size=13))
    f.append(text(590, 238, "разом із усім, що вона запустить далі", size=13))

    f.append(text(590, 320, "що мав на думці адміністратор", size=15, bold=True, color=FIELD))
    f.append(text(590, 350, "перезапустити оцей вебсервер", size=13))
    f.append(text(590, 390, "мета описується метою, а правило — засобом;", size=13))
    f.append(text(590, 414, "проміжок між колами і є ціною цієї підміни", size=13))

    render(os.path.join(OUT, 'granted-vs-reachable.svg'), W, H, *f,
           title="Мета, дозвіл і насправді досяжне")


def fig_wrapper_gate():
    """Обгортка: що приходить ззовні і що з цього доходить до execve."""
    W, H = 1180, 720
    f = []

    f.append(text(285, 66, "що надходить ззовні", size=15, bold=True, color=POS))
    f.append(text(865, 66, "що з цим робить обгортка", size=15, bold=True))

    rows = [
        ("порожній argv: argc == 0",
         "argc звіряється до першого звертання до argv"),
        ("зайві слова після дії",
         "приймаємо рівно один аргумент, решта — відмова"),
        ("слово, якого немає в таблиці",
         "словник закритий: збіг або відмова, третього нема"),
        ("оточення прохача",
         "дитині складаємо власне, а не чистимо успадковане"),
        ("дескриптори з номерами 3 і вище",
         "закриті; 0, 1 і 2 гарантовано відкриті"),
        ("бажання підказати шлях",
         "шлях сталий і абсолютний, execve без оболонки"),
    ]

    y = 128
    for left, right in rows:
        b, _, _ = textbox(285, y, left, size=13, min_w=420,
                          fill="#fdecea", stroke=POS)
        f.append(b)
        f.append(arrow(505, y, 573, y))
        b, _, _ = textbox(865, y, right, size=13, min_w=560)
        f.append(b)
        y += 84

    b, _, _ = textbox(590, 648,
                      "командний рядок дитини склали МИ:\nжоден його байт не прийшов ззовні",
                      size=14, min_w=760, fill="#e9f7ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(OUT, 'wrapper-gate.svg'), W, H, *f,
           title="Вузька обгортка: усе зовнішнє відсіюється до exec")


def fig_scan_order():
    """Порядок розбору: @includedir розкривається на місці, виграє останній збіг."""
    W, H = 1240, 760
    f = []

    f.append(text(390, 45, "порядок, у якому парсер бачить рядки", size=14, bold=True))
    f.append(text(985, 45, "прохання: ivan → systemctl restart nginx", size=14, bold=True))

    f.append(arrow(26, 92, 26, 640))

    rows = [
        ("/etc/sudoers, рядок 12\n%wheel ALL = (ALL:ALL) ALL",
         "ivan не в wheel — не збіг", FILL, MUTED),
        ("/etc/sudoers, рядок 20\n@includedir /etc/sudoers.d",
         "каталог розкривається ТУТ,\nа не в кінці файлу", "#eef3fd", NEG),
        ("sudoers.d/10-deploy\nivan ALL = NOPASSWD: /usr/bin/systemctl restart nginx",
         "збіг ①: без пароля", FILL, INK),
        ("sudoers.d/50-lock\nivan ALL = (ALL) ALL",
         "збіг ② — ВИГРАЄ: з паролем", "#fdecea", POS),
        ("sudoers.d/90-audit.bak\nivan ALL = NOPASSWD: ALL",
         "пропущено: крапка в імені —\nінакше виграв би цей", "#f9fafb", MUTED),
        ("/etc/sudoers, рядок 21\nDefaults timestamp_timeout=0",
         "діє, хоч і стоїть після каталогу", FILL, INK),
    ]

    y = 118
    for left, right, bg, ink in rows:
        b, _, _ = textbox(390, y, left, size=13, min_w=680, fill=bg, stroke=ink)
        f.append(b)
        b, _, _ = textbox(985, y, right, size=13, min_w=420,
                          fill="#ffffff", stroke=MUTED, color=ink)
        f.append(b)
        y += 100

    b, _, _ = textbox(590, 700,
                      "усередині каталогу файли беруться в лексичному порядку імен — тому їх і нумерують;\n"
                      "виграє ОСТАННІЙ збіг, а не найточніший: рядок-виняток над загальним рядком не діє",
                      size=13, min_w=940, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(OUT, 'scan-order.svg'), W, H, *f,
           title="Порядок розбору sudoers: включення на місці, перемагає останній збіг")


if __name__ == '__main__':
    fig_rule_anatomy()
    fig_sudo_path()
    fig_granted_vs_reachable()
    fig_wrapper_gate()
    fig_scan_order()
    print("ok")
