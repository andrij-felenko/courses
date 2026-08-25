# -*- coding: utf-8 -*-
import sys, os
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


def tb(cx, cy, lines, **kw):
    """textbox + межі рамки (x0, x1, y0, y1)."""
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Імена в каталогах, файл в inode ───────────────────────────────────────
def fig_names_and_inodes():
    W, H = 1000, 600
    p = []

    dir_a, ax0, ax1, ay0, ay1 = tb(180, 150,
                                   ["каталог /home/ann",
                                    "report.txt → 812"],
                                   size=13, fill=BLUE_FILL, stroke=NEG, pad=12)
    dir_b, bx0, bx1, by0, by1 = tb(180, 300,
                                   ["каталог /home/ann/архів",
                                    "звіт → 812"],
                                   size=13, fill=BLUE_FILL, stroke=NEG, pad=12)
    dir_c, cx0, cx1, cy0, cy1 = tb(180, 452,
                                   ["каталог /var/www",
                                    "поточний → 907"],
                                   size=13, fill=BLUE_FILL, stroke=NEG, pad=12)
    p += [dir_a, dir_b, dir_c]

    ino1, i1x0, i1x1, i1y0, i1y1 = tb(530, 225,
                                      ["inode 812",
                                       "тип: звичайний файл",
                                       "імен: 2",
                                       "права, час, розмір",
                                       "покажчики на блоки"],
                                      size=13, fill=GREEN_FILL, stroke=FIELD, pad=14)
    ino2, i2x0, i2x1, i2y0, i2y1 = tb(530, 452,
                                      ["inode 907",
                                       "тип: символьне посилання",
                                       "імен: 1",
                                       "вміст: /home/ann/report.txt"],
                                      size=13, fill=WARM_FILL, stroke=WARM, pad=14)
    p += [ino1, ino2]

    blk, kx0, kx1, ky0, ky1 = tb(860, 225,
                                 ["блоки даних", "(власне вміст)"],
                                 size=13, pad=14)
    p.append(blk)

    p.append(arrow(ax1 + 8, 150, i1x0 - 8, 205))
    p.append(arrow(bx1 + 8, 300, i1x0 - 8, 245))
    p.append(arrow(cx1 + 8, 452, i2x0 - 8, 452))
    p.append(arrow(i1x1 + 8, 225, kx0 - 8, 225))

    note, nx0, nx1, ny0, ny1 = tb(530, 548,
                                  ["вміст посилання — це ТЕКСТ шляху:",
                                   "ядро розбирає його щоразу заново"],
                                  size=12, fill=WARM_FILL, stroke=WARM, pad=12)
    p.append(note)
    p.append(line(530, i2y1 + 6, 530, ny0 - 6, color=WARM, sw=1.6, dash="5,4"))

    render(os.path.join(IMG, 'names-and-inodes.svg'), W, H, *p,
           title="Каталог тримає ім'я, inode тримає файл")


# ── 2. Два лічильники життя файлу ────────────────────────────────────────────
def fig_two_counters():
    W, H = 1020, 520
    p = []

    cols = [
        (150, "open(\"log\", …)", ["імен: 1", "дескрипторів: 1"], "файл живий", GREEN_FILL, FIELD),
        (400, "ln log log2", ["імен: 2", "дескрипторів: 1"], "той самий файл,\nдва імені", GREEN_FILL, FIELD),
        (650, "rm log log2", ["імен: 0", "дескрипторів: 1"], "імені немає,\nдані читаються,\nмісце зайняте", WARM_FILL, WARM),
        (900, "close(fd)", ["імен: 0", "дескрипторів: 0"], "inode і блоки\nзвільнено", RED_FILL, POS),
    ]

    edges = []
    for cx, cmd, counters, verdict, fill, stroke in cols:
        p.append(fitbox(cx - 108, 66, 216, 48, cmd, size=14, bold=True))
        frag, x0, x1, y0, y1 = tb(cx, 200, counters, size=14, pad=14)
        p.append(frag)
        edges.append((x0, x1))
        p.append(fitbox(cx - 108, 288, 216, 84, verdict, size=13, fill=fill, stroke=stroke))

    for i in range(len(cols) - 1):
        p.append(arrow(edges[i][1] + 10, 200, edges[i + 1][0] - 10, 200))

    p.append(fitbox(150, 418, 720, 62,
                    "поки бодай один лічильник більший за нуль — дані живі,\n"
                    "навіть коли жодного імені вже не лишилося",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'two-counters.svg'), W, H, *p,
           title="Файл зникає, коли обидва лічильники дійшли нуля")


# ── 3. Розбір шляху крізь символьне посилання ────────────────────────────────
def fig_symlink_walk():
    W, H = 620, 690
    p = []

    steps = [
        ('/', "корінь", FILL, LINE),
        ('var', "каталог", FILL, LINE),
        ('log', "каталог", FILL, LINE),
        ('app', "СИМВОЛЬНЕ ПОСИЛАННЯ\nвміст: ../../srv/logs/app", WARM_FILL, WARM),
        ('', "підстановка: далі шлях читається\nвід /var/log/ → /srv/logs/app", BLUE_FILL, NEG),
        ('today.log', "знайдено inode файлу", GREEN_FILL, FIELD),
    ]

    y = 92
    for name, note, fill, stroke in steps:
        label = (name + " — " + note) if name else note
        p.append(fitbox(60, y, 500, 62, label, size=13, fill=fill, stroke=stroke))
        if y < 92 + 5 * 88:
            p.append(arrow(310, y + 62 + 4, 310, y + 88 - 4))
        y += 88

    p.append(fitbox(60, 612, 500, 46,
                    "кожен перехід за посиланням додає одиницю до ліміту 40; цикл дає ELOOP",
                    size=12, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'symlink-walk.svg'), W, H, *p,
           title="Ядро йде шляхом покомпонентно")


# ── 4. Вікно збою між двома записами ─────────────────────────────────────────
def fig_crash_window():
    W, H = 1000, 560
    p = []

    rows = [
        (110, "спершу — запис\nімені в каталог",
         "лічильник менший за кількість імен:\nперший rm звільнить блоки\nз-під живого імені — руйнація", RED_FILL, POS),
        (270, "спершу — збільшити\nлічильник імен",
         "лічильник більший за кількість імен:\nмісце не звільниться,\nале дані цілі", WARM_FILL, WARM),
    ]

    for y, act, res, fill, stroke in rows:
        p.append(fitbox(50, y, 230, 80, act, size=13))
        p.append(arrow(292, y + 40, 348, y + 40))
        p.append(fitbox(360, y, 160, 80, "збій\nживлення", size=13, fill=RED_FILL, stroke=POS))
        p.append(arrow(532, y + 40, 588, y + 40))
        p.append(fitbox(600, y - 6, 360, 92, res, size=12, fill=fill, stroke=stroke))

    p.append(fitbox(180, 430, 640, 80,
                    "журнал: обидва записи — одна транзакція,\n"
                    "тож після збою є або обидва, або жодного",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'crash-window.svg'), W, H, *p,
           title="Одне жорстке посилання — два записи на диск")


# ── 5. Хто розгортає останній компонент шляху (вставка api-) ─────────────────
def fig_follow_matrix():
    W, H = 1060, 540
    p = []

    p.append(fitbox(30, 60, 490, 66,
                    "префікс шляху:   /var/log/\n"
                    "посилання розгортаються ЗАВЖДИ, у кожному виклику",
                    size=13, fill=BLUE_FILL, stroke=NEG))
    p.append(fitbox(560, 60, 470, 66,
                    "останній компонент:   app\n"
                    "поведінка залежить від виклику й прапорців",
                    size=13, fill=WARM_FILL, stroke=WARM))
    p.append(line(795, 130, 795, 164, color=WARM, sw=1.6, dash="5,4"))

    cols = [
        (30, "завжди йде за посиланням", GREEN_FILL, FIELD,
         ["stat",
          "open, openat (без O_NOFOLLOW)",
          "chdir, chroot",
          "chmod, chown, truncate",
          "execve",
          "opendir, access"]),
        (370, "ніколи не йде за ним", RED_FILL, POS,
         ["lstat",
          "readlink",
          "unlink, rmdir",
          "rename",
          "symlink (кладе саме тут)",
          "link (Linux, від 2.0)",
          "lchown, lsetxattr, lgetxattr"]),
        (710, "вирішує прапорець", BLUE_FILL, NEG,
         ["fstatat, statx",
          "AT_SYMLINK_NOFOLLOW",
          "linkat",
          "AT_SYMLINK_FOLLOW",
          "open, openat",
          "O_NOFOLLOW, O_PATH",
          "fchownat, utimensat"]),
    ]

    for x, head, fill, stroke, items in cols:
        p.append(fitbox(x, 176, 320, 46, head, size=14, bold=True,
                        fill=fill, stroke=stroke))
        p.append(fitbox(x, 232, 320, 174, items, size=13))

    p.append(fitbox(30, 428, 1000, 78,
                    "кінцева скісна риска дорівнює додаванню «/.»: вона примусово розгортає "
                    "останній компонент\n"
                    "і вимагає, щоб там був каталог — тому lstat(\"посилання/\") "
                    "розповідає вже про ціль, а не про посилання",
                    size=13, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'follow-matrix.svg'), W, H, *p,
           title="Останній компонент шляху: хто його розгортає")


# ── 6. Коли саме існує ім'я (вставка proj-) ──────────────────────────────────
def fig_name_window():
    W, H = 1030, 400
    p = []

    step = 240
    xs = [60 + i * step for i in range(4)]
    bw, bh = 190, 56

    p.append(text(W / 2, 62,
                  "класичний прийом: створити ім'я й одразу від'єднати",
                  size=14, bold=True))
    lane1 = [
        ("open(O_CREAT)\nім'я з'явилося", WARM_FILL, WARM),
        ("unlink\nімені вже немає", FILL, LINE),
        ("запис даних\nдоки живий дескриптор", FILL, LINE),
        ("close\nблоки звільнено", GREEN_FILL, FIELD),
    ]
    for x, (label, fill, stroke) in zip(xs, lane1):
        p.append(fitbox(x, 78, bw, bh, label, size=13, fill=fill, stroke=stroke))
    for i in range(3):
        p.append(arrow(xs[i] + bw + 8, 78 + bh / 2, xs[i + 1] - 8, 78 + bh / 2))

    p.append(line(155, 136, 155, 146, color=POS, sw=1.6, dash="5,4"))
    p.append(fitbox(60, 148, 430, 46,
                    "поки ім'я існує, чужий процес\n"
                    "встигає його відкрити або підмінити",
                    size=13, fill=RED_FILL, stroke=POS))

    p.append(text(W / 2, 232,
                  "O_TMPFILE: ім'я дають наприкінці",
                  size=14, bold=True))
    lane2 = [
        ("open(dir, O_TMPFILE)\ninode без імені", FILL, LINE),
        ("запис даних\nімені все ще немає", FILL, LINE),
        ("fsync\nдані на носії", FILL, LINE),
        ("linkat(/proc/self/fd/N)\nім'я з'являється", GREEN_FILL, FIELD),
    ]
    for x, (label, fill, stroke) in zip(xs, lane2):
        p.append(fitbox(x, 248, bw, bh, label, size=13, fill=fill, stroke=stroke))
    for i in range(3):
        p.append(arrow(xs[i] + bw + 8, 248 + bh / 2, xs[i + 1] - 8, 248 + bh / 2))

    p.append(line(875, 306, 875, 316, color=FIELD, sw=1.6, dash="5,4"))
    p.append(fitbox(600, 318, 380, 46,
                    "ім'я з'являється лише тут —\n"
                    "одразу разом із повним вмістом",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'name-window.svg'), W, H, *p,
           title="Скільки часу файл прожив під іменем")


if __name__ == '__main__':
    fig_names_and_inodes()
    fig_two_counters()
    fig_symlink_walk()
    fig_crash_window()
    fig_follow_matrix()
    fig_name_window()
    print("ok")
