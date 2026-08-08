# -*- coding: utf-8 -*-
"""Фігури до теми «setuid, setgid і підвищення прав»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_raise_at_exec():
    """Що змінює біт підвищення при exec — і що переходить незмінним."""
    W, H = 1200, 560
    f = []

    b, _, _ = textbox(180, 165,
                      "процес до exec\n"
                      "ruid  1000\n"
                      "euid  1000\n"
                      "suid  1000",
                      size=14, min_w=260)
    f.append(b)

    b, _, _ = textbox(600, 165,
                      "/usr/bin/passwd\n"
                      "-rwsr-xr-x   root   root\n"
                      "біт set-user-ID стоїть",
                      size=14, fill="#fdecea", stroke=POS)
    f.append(b)

    b, _, _ = textbox(1005, 165,
                      "той самий процес після exec\n"
                      "ruid  1000   не змінився\n"
                      "euid  0      узято у власника файлу\n"
                      "suid  0      копія нового діючого",
                      size=14, fill="#eef3fd", stroke=NEG)
    f.append(b)

    f.append(arrow(320, 165, 448, 165))
    f.append(arrow(752, 165, 838, 165))

    f.append(fitbox(70, 300, 1060, 118,
                    "через exec переходить незмінним усе інше:\n"
                    "argv (включно з argv[0] і порожнім) · оточення: PATH, IFS, TZ, LOCPATH · відкриті дескриптори\n"
                    "робочий каталог · umask · обмеження ресурсів · маска сигналів · додаткові групи",
                    size=14, fill="#f7f9fc"))

    b, _, _ = textbox(600, 480,
                      "усе, що в цій смузі, склав той, хто програму запустив",
                      size=14, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(OUT, 'raise-at-exec.svg'), W, H, *f,
           title="Що змінює біт set-user-ID під час exec")


def fig_secure_exec():
    """Межа безпечного виконання: хто що прибирає з успадкованого оточення."""
    W, H = 1220, 640
    f = []

    f.append(text(240, 56, "обирає той, хто запускає", size=15, bold=True))
    rows = [
        "argv, включно з argv[0] і порожнім",
        "оточення: PATH, IFS, TZ, LOCPATH",
        "дескриптори 0, 1, 2 і залишені відкритими",
        "робочий каталог і umask",
        "обмеження ресурсів, зокрема RLIMIT_FSIZE",
        "маска й диспозиції сигналів",
    ]
    y = 90
    for r in rows:
        f.append(fitbox(45, y, 390, 52, r, size=13, fill="#f4f6f8"))
        y += 68

    f.append(line(480, 90, 480, 500, color=MUTED, sw=1.6, dash="6 6"))
    b, _, _ = textbox(480, 560, "межа: exec файлу\nз бітом підвищення", size=13,
                      fill="#f7f9fc", stroke=MUTED)
    f.append(b)

    f.append(fitbox(530, 90, 650, 190,
                    "прибирає ядро й бібліотека, бо інакше зламало б будь-яку програму\n"
                    "AT_SECURE = 1: LD_PRELOAD, LD_LIBRARY_PATH, LD_AUDIT ігноруються\n"
                    "закриті 0, 1, 2 ядро відкриває на /dev/null\n"
                    "дамп не пишеться, ptrace не приєднається\n"
                    "процес уже під трасуванням — підвищення не робиться взагалі",
                    size=13, fill="#eef3fd", stroke=NEG))

    f.append(fitbox(530, 320, 650, 190,
                    "лишається на совісті самої програми\n"
                    "PATH перед запуском будь-якої дочірньої команди\n"
                    "IFS перед system() і popen()\n"
                    "зайві успадковані дескриптори й робочий каталог\n"
                    "довжина та вміст кожного аргументу",
                    size=13, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'secure-exec.svg'), W, H, *f,
           title="Що з успадкованого оточення знімає система, а що лишає програмі")


def fig_setgid_dir():
    """S_ISGID на каталозі: звідки новий запис бере групу."""
    W, H = 1180, 540
    f = []

    f.append(text(280, 52, "каталог без S_ISGID", size=15, bold=True))
    f.append(text(870, 52, "каталог із S_ISGID", size=15, bold=True))

    b, _, _ = textbox(280, 115, "тека proj/\ndrwxrwx---   root   devs", size=13, min_w=300)
    f.append(b)
    b, _, _ = textbox(870, 115, "тека proj/\ndrwxrws---   root   devs", size=13,
                      min_w=300, fill="#eef3fd", stroke=NEG)
    f.append(b)

    f.append(arrow(280, 145, 280, 232))
    f.append(arrow(870, 145, 870, 232))

    b, _, _ = textbox(280, 268, "новий файл\nгрупа = egid того, хто створив\n(alice)", size=13)
    f.append(b)
    b, _, _ = textbox(870, 268, "новий файл\nгрупа = група каталогу\n(devs)", size=13,
                      fill="#eef3fd", stroke=NEG)
    f.append(b)

    f.append(arrow(870, 320, 870, 372))
    b, _, _ = textbox(870, 408, "новий підкаталог\nгрупа devs і сам біт S_ISGID", size=13,
                      fill="#eef3fd", stroke=NEG)
    f.append(b)

    b, _, _ = textbox(280, 408, "сусід із групи devs\nцього файлу не прочитає", size=13,
                      fill="#fdecea", stroke=POS)
    f.append(b)

    b, _, _ = textbox(590, 508,
                      "біт не роздає прав — він вирішує, звідки взяти групу новоствореного",
                      size=13, fill="#f7f9fc")
    f.append(b)

    render(os.path.join(OUT, 'setgid-dir.svg'), W, H, *f,
           title="Успадкування групи в каталозі з бітом set-group-ID")


def fig_toctou_access():
    """Чому перевірка access() перед open() нічого не доводить."""
    W, H = 1240, 620
    f = []

    f.append(text(300, 50, "помічник, euid 0", size=15, bold=True))
    f.append(text(950, 50, "нападник, uid 1000", size=15, bold=True))

    f.append(line(625, 80, 625, 500, color=MUTED, sw=1.6, dash="6 6"))
    f.append(text(625, 545, "час", size=13, color=MUTED))
    f.append(arrow(625, 500, 625, 522, color=MUTED))

    b, _, _ = textbox(300, 140,
                      "access(\"/tmp/u/out.log\", W_OK)\n"
                      "перевірка йде за ruid 1000\n"
                      "файл справді ваш — «так»",
                      size=13, min_w=420, fill="#f7f9fc")
    f.append(b)

    b, _, _ = textbox(950, 290,
                      "unlink(\"/tmp/u/out.log\")\n"
                      "symlink(\"/etc/shadow\", \"/tmp/u/out.log\")\n"
                      "ім'я лишилося те саме — веде вже не туди",
                      size=13, min_w=420, fill="#fdecea", stroke=POS)
    f.append(b)

    b, _, _ = textbox(300, 440,
                      "open(\"/tmp/u/out.log\", O_WRONLY)\n"
                      "відкриття йде за euid 0\n"
                      "відкрився /etc/shadow",
                      size=13, min_w=420, fill="#fdecea", stroke=POS)
    f.append(b)

    f.append(fitbox(120, 570, 1000, 44,
                    "перевіряли ім'я, а відкрили об'єкт — і між двома викликами це вже різні речі",
                    size=13, fill="#f7f9fc"))

    render(os.path.join(OUT, 'toctou-access.svg'), W, H, *f,
           title="Гонка між access() і open() у setuid-помічнику")


if __name__ == '__main__':
    fig_raise_at_exec()
    fig_secure_exec()
    fig_setgid_dir()
    fig_toctou_access()
    print("ok")
