# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
WARM = "#b8860b"


# ── 1. Спектр оболонок: від мінімального POSIX до розширених діалектів ───────
def fig_shell_dialect_spectrum():
    W, H = 1100, 520
    p = []

    p.append(fitbox(50, 20, 1000, 48,
                    "Спектр оболонок Unix: співвідношення строгості POSIX, швидкості та розширень",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    cols = [
        ("Канонічний стандарт",
         "IEEE 1003.1 (POSIX sh)\nСпецифікація Shell Command Language",
         "Мінімальне спільне ядро всіх систем.\n"
         "• Жодних масивів, [[ ]], local, зрізів\n"
         "• Гарантія роботи на будь-якому Unix\n"
         "• Мета: максимальна переносність",
         GREEN_FILL, FIELD),
        ("Швидкісні системні sh",
         "Dash, BusyBox Ash, Almquist sh\nТиповий /bin/sh у Debian/Ubuntu, Alpine",
         "Легковагі інтерпретатори для init/скриптів.\n"
         "• В 3–4 рази швидший старт за Bash\n"
         "• Суворе дотримання стандарту POSIX\n"
         "• Миттєво ламаються на башизмах",
         BLUE_FILL, NEG),
        ("Системні BSD оболонки",
         "FreeBSD sh, OpenBSD pdksh, NetBSD sh\nБазовий userland BSD систем",
         "Оболонки нащадків Almquist та KornShell.\n"
         "• POSIX з локальними розширеннями\n"
         "• Відсутні розширення GNU Coreutils\n"
         "• /bin/sh не має багатьох фіч Bash",
         WARM_FILL, WARM),
        ("Розширені командні",
         "GNU Bash 5.x, Zsh, Ksh93, macOS Bash 3.2\nІнтерактивні оболонки розробника",
         "Багатий синтаксис та зручності для CLI.\n"
         "• Масиви, regex =~, [[ ]], <(proc)\n"
         "• Повільніший запуск (overhead ~10ms)\n"
         "• Непереносні поза власним бінарником",
         RED_FILL, POS),
    ]

    CW = 230
    GAP = 22
    X0 = 55
    Y0 = 85

    for i, (cat, title, desc, fill, stroke) in enumerate(cols):
        x = X0 + i * (CW + GAP)
        p.append(fitbox(x, Y0, CW, 38, cat, size=13, fill=fill, stroke=stroke, bold=True))
        p.append(fitbox(x, Y0 + 46, CW, 54, title, size=12, fill=BG, stroke=stroke, bold=True))
        p.append(fitbox(x, Y0 + 108, CW, 200, desc, size=12, fill=FILL, stroke=MUTED))

    # Стрілка знизу — спектр швидкості та портативності
    p.append(rect(55, 415, 1000, 75, fill=BG, stroke=LINE))
    p.append(fitbox(65, 423, 480, 58,
                    "Лівий край: Максимальна переносність, миттєвий запуск (initramfs, CI, контейнери),\n"
                    "суворий POSIX синтаксис, виявлення помилок статичними лінтерами",
                    size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(565, 423, 480, 58,
                    "Правий край: Інтерактивна зручність, розширені структури даних,\n"
                    "прив'язка до конкретної версії інтерпретатора (Shebang: #!/usr/bin/env bash)",
                    size=12, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'shell-dialect-spectrum.svg'), W, H, *p)


# ── 2. Заміна типових башизмів на безпечні POSIX конструкції ─────────────────
def fig_bashism_replacement_patterns():
    W, H = 1100, 560
    p = []

    p.append(fitbox(50, 20, 1000, 46,
                    "Архітектурна заміна башизмів на переносні еквіваленти POSIX sh",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    headers = [
        (55, 300, "Башизм (Bash-специфічний синтаксис)"),
        (375, 400, "Переносний еквівалент POSIX sh"),
        (795, 250, "Чому це працює безпечно"),
    ]
    for x, w, title in headers:
        p.append(fitbox(x, 78, w, 32, title, size=13, fill=FILL, stroke=LINE, bold=True))

    rows = [
        ("[[ $a == $b && $c =~ ^[0-9]+$ ]]\nРозширений test, regex, оператор ==",
         "[ \"$a\" = \"$b\" ] && case \"$c\" in\n    ''|*[!0-9]*) false ;; *) true ;; esac\nКвотований [ ] та зіставлення case",
         "[ — звичайна утиліта, потребує лапок;\ncase замінює regex без розширень",
         RED_FILL, GREEN_FILL),
        ("diff <(cmd1) <(cmd2)\nПідстановка процесів через /dev/fd/N",
         "mkfifo /tmp/p1 /tmp/p2\ncmd1 > /tmp/p1 & cmd2 > /tmp/p2 &\ndiff /tmp/p1 /tmp/p2; rm /tmp/p1 /tmp/p2",
         "Явний FIFO канал стандартизований\nі працює без підтримки /dev/fd",
         RED_FILL, GREEN_FILL),
        ("local var=$(command)\nКлючове слово local + присвоєння",
         "var=$(command)\n( subshell: var=$(command); do_work )\nРоздільне присвоєння або субшел",
         "local var=$(cmd) затирає $? команди;\nsubshell гарантує повну ізоляцію",
         RED_FILL, GREEN_FILL),
        ("arr=(\"a b\" \"c\"); echo \"${arr[0]}\"\nІндексовані масиви",
         "set -- \"a b\" \"c\"; echo \"$1\"\nfor item in \"$@\"; do ... done\nПозиційні параметри як єдиний масив",
         "\"$@\" зберігає елементи з пробілами\nі є стандартом у кожному sh",
         RED_FILL, GREEN_FILL),
        ("${var:0:4} або ${var//foo/bar}\nЗрізи підрядків та підстановка",
         "echo \"$var\" | cut -c 1-4\necho \"$var\" | sed 's/foo/bar/g'\nСтандартні фільтри тексту",
         "${var#pre} та ${var%suf} у sh;\nрешта операцій — через sed/cut/awk",
         RED_FILL, GREEN_FILL),
    ]

    Y0 = 120
    RH = 78
    GAP = 8

    for i, (bash, posix, why, bfill, pfill) in enumerate(rows):
        y = Y0 + i * (RH + GAP)
        p.append(fitbox(55, y, 300, RH, bash, size=11.5, fill=bfill, stroke=POS))
        p.append(fitbox(375, y, 400, RH, posix, size=11.5, fill=pfill, stroke=FIELD))
        p.append(fitbox(795, y, 250, RH, why, size=11.5, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, 'bashism-replacement-patterns.svg'), W, H, *p)


# ── 3. Розбіжності утиліт: GNU Coreutils проти BSD Userland ───────────────────
def fig_gnu_vs_bsd_utilities_matrix():
    W, H = 1100, 520
    p = []

    p.append(fitbox(50, 20, 1000, 46,
                    "Розбіжності системних утиліт: GNU Coreutils проти BSD / macOS Userland",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    headers = [
        (55, 120, "Утиліта"),
        (190, 260, "Діалект GNU (Linux)"),
        (465, 260, "Діалект BSD (macOS / FreeBSD)"),
        (740, 305, "Гарантовано переносний патерн"),
    ]
    for x, w, title in headers:
        p.append(fitbox(x, 76, w, 32, title, size=13, fill=FILL, stroke=LINE, bold=True))

    rows = [
        ("sed -i\n(In-place)",
         "sed -i 's/a/b/g' file\nСуфікс бекапу необов'язковий",
         "sed -i '' 's/a/b/g' file\nВимагає явний суфікс (хоч '')",
         "sed 's/a/b/g' file > f.tmp && mv f.tmp file\nабо: sed -i.bak 's/a/b/g' file && rm file.bak",
         BLUE_FILL, WARM_FILL, GREEN_FILL),
        ("date\n(Timestamp)",
         "date -d \"@1700000000\"\ndate -d \"+1 day\"",
         "date -r 1700000000\ndate -v+1d -j -f \"%Y-%m-%d\"",
         "date +%s  (поточний Epoch)\nСкладні обчислення часу — через awk / C",
         BLUE_FILL, WARM_FILL, GREEN_FILL),
        ("grep\n(Regex)",
         "grep -P '\\d+\\s+\\w+'\nPerl-сумісні вирази (PCRE)",
         "grep -E '[0-9]+[[:space:]]+[a-zA-Z_]+'\n-P відсутній або ламає прапорці",
         "grep -E (Extended POSIX Regex)\nКласи символів [[:space:]], [[:digit:]]",
         BLUE_FILL, WARM_FILL, GREEN_FILL),
        ("find\n(Traversal)",
         "find . -maxdepth 1 -delete\nРозширення GNU",
         "find . -depth 1 -delete\nПрапорці різняться",
         "find . -name '*.tmp' -exec rm -f {} +\nОбмеження глибини — через -prune",
         BLUE_FILL, WARM_FILL, GREEN_FILL),
        ("which vs\ncommand",
         "which tool  (зовнішня утиліта)\nРізні коди помилок",
         "which tool  (csh/sh скрипт)\nЧасто повертає 0 навіть при 404",
         "command -v tool >/dev/null 2>&1\nВбудована перевірка POSIX у кожному sh",
         BLUE_FILL, WARM_FILL, GREEN_FILL),
    ]

    Y0 = 118
    RH = 70
    GAP = 8

    for i, (tool, gnu, bsd, port, gfill, bfill, pfill) in enumerate(rows):
        y = Y0 + i * (RH + GAP)
        p.append(fitbox(55, y, 120, RH, tool, size=12, fill=FILL, stroke=LINE, bold=True))
        p.append(fitbox(190, y, 260, RH, gnu, size=11.5, fill=gfill, stroke=NEG))
        p.append(fitbox(465, y, 260, RH, bsd, size=11.5, fill=bfill, stroke=WARM))
        p.append(fitbox(740, y, 305, RH, port, size=11.5, fill=pfill, stroke=FIELD))

    render(os.path.join(IMG, 'gnu-vs-bsd-utilities-matrix.svg'), W, H, *p)


if __name__ == '__main__':
    fig_shell_dialect_spectrum()
    fig_bashism_replacement_patterns()
    fig_gnu_vs_bsd_utilities_matrix()
    print("All figures generated successfully.")
