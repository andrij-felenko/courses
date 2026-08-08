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
GREY_FILL = "#eceef1"


def panel(x, y, w, h, title, color, fill):
    """Рамка-панель із заголовковим рядком угорі."""
    out = [rect(x, y, w, h, fill=fill, stroke=color, sw=2.0, rx=10)]
    out.append(text(x + w / 2, y + 28, title, size=16, bold=True, color=color))
    out.append(line(x + 14, y + 42, x + w - 14, y + 42, color=color, sw=1.2))
    return out


# ── 1. Номер inode проти рукоятки ──────────────────────────────────────────
def fig_identity():
    W, H = 1240, 660
    p = []

    px, py, pw, ph = 40, 46, 560, 570
    qx = 640

    p += panel(px, py, pw, ph, "Ключ покажчика — номер inode", POS, RED_FILL)
    p += panel(qx, py, pw, ph, "Ключ покажчика — рукоятка", FIELD, GREEN_FILL)

    bx, bw = px + 26, pw - 52
    cx, cw = qx + 26, pw - 52

    left = [
        ["УЧОРА", "index.log лежить в inode 4711",
         "у покажчику збережено число 4711"],
        ["ЗА НІЧ", "index.log вилучено, inode 4711 звільнено;",
         "новий journal.tmp зайняв той самий 4711"],
        ["СЬОГОДНІ", "програма шукає файл із номером 4711",
         "і знаходить journal.tmp"],
    ]
    right = [
        ["УЧОРА", "index.log лежить в inode 4711, покоління 12",
         "у покажчику збережено 4711 · 12"],
        ["ЗА НІЧ", "index.log вилучено; journal.tmp узяв inode 4711,",
         "і лічильник поколінь піднявся до 13"],
        ["СЬОГОДНІ", "ядро бере inode 4711 і звіряє покоління:",
         "12 у рукоятці ≠ 13 в inode"],
    ]

    def column(x0, w0, stages, color):
        out = []
        y0 = py + 58
        for i, lines in enumerate(stages):
            yy = y0 + i * 118
            out.append(fitbox(x0, yy, w0, 90, lines, size=14,
                              fill=BG, stroke=color, sw=1.6))
            if i < len(stages) - 1:
                out.append(arrow(x0 + w0 / 2, yy + 92, x0 + w0 / 2, yy + 114,
                                 color=color, sw=2))
        return out

    p += column(bx, bw, left, POS)
    p += column(cx, cw, right, FIELD)

    tail_y = py + 58 + 3 * 118 + 8
    p.append(fitbox(bx, tail_y, bw, 104,
                    ["Помилки немає, і бути не може.",
                     "Покажчик мовчки говорить про чужий файл,",
                     "і жодне поле stat цього не викаже."],
                    size=14, fill=RED_FILL, stroke=POS, sw=2, bold=True))
    p.append(fitbox(cx, tail_y, bw, 104,
                    ["ESTALE — «такого файлу тут уже немає».",
                     "Програма дізнається правду одразу",
                     "і перечитує лише те, що справді змінилося."],
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=2, bold=True))

    render(os.path.join(IMG, 'identity-vs-number.svg'), W, H, *p)


# ── 2. Дві дороги до inode ─────────────────────────────────────────────────
def fig_two_roads():
    W, H = 1240, 800
    p = []

    px, py, pw, ph = 40, 46, 550, 600
    qx = 650

    p += panel(px, py, pw, ph, "Дорога через шлях", NEG, BLUE_FILL)
    p += panel(qx, py, pw, ph, "Дорога через рукоятку", FIELD, GREEN_FILL)

    steps = ["корінь /",
             "var — потрібен біт x",
             "spool — потрібен біт x",
             "reports — потрібен біт x",
             "out.log — знайдено ім'я"]
    sx, sw = px + 100, pw - 200
    for i, s in enumerate(steps):
        yy = py + 62 + i * 70
        p.append(fitbox(sx, yy, sw, 48, [s], size=14, fill=BG, stroke=NEG, sw=1.5))
        p.append(arrow(sx + sw / 2, yy + 50, sx + sw / 2, yy + 68, color=NEG, sw=2))

    inode_y = py + 62 + 5 * 70
    p.append(fitbox(sx, inode_y, sw, 50, ["inode 4711"], size=15,
                    fill=WARM_FILL, stroke=INK, sw=2, bold=True))
    p.append(fitbox(px + 24, inode_y + 88, pw - 48, 78,
                    ["П'ять кроків — чотири перевірки прав.",
                     "Без права входу в каталог файл недосяжний."],
                    size=14, fill=BG, stroke=NEG, sw=1.5))

    qw = pw - 120
    p.append(fitbox(qx + 60, py + 78, qw, 74,
                    ["дескриптор будь-чого на цій файловій системі",
                     "→ обрано, у якій ФС шукати"],
                    size=14, fill=BG, stroke=FIELD, sw=1.5))
    p.append(fitbox(qx + 60, py + 186, qw, 74,
                    ["рукоятка 4711 · покоління 12",
                     "→ обрано inode усередині цієї ФС"],
                    size=14, fill=BG, stroke=FIELD, sw=1.5))
    p.append(arrow(qx + pw / 2, py + 264, qx + pw / 2, inode_y - 12,
                   color=FIELD, sw=2))
    p.append(fitbox(qx + 60, inode_y, qw, 50, ["inode 4711"], size=15,
                    fill=WARM_FILL, stroke=INK, sw=2, bold=True))
    p.append(fitbox(qx + 24, inode_y + 88, pw - 48, 78,
                    ["Каталогів на дорозі немає —",
                     "отже, немає й жодної перевірки біта x."],
                    size=14, fill=BG, stroke=FIELD, sw=1.5))

    p.append(fitbox(px, py + ph + 30, qx + pw - px, 90,
                    ["Саме тому open_by_handle_at відкрито лише носіям повноваження CAP_DAC_READ_SEARCH:",
                     "воно одним махом заміняє всі перевірки, які дорога через шлях робила крок за кроком."],
                    size=15, fill=RED_FILL, stroke=POS, sw=2, bold=True))

    render(os.path.join(IMG, 'two-roads.svg'), W, H, *p)


# ── 3. Один механізм, два входи ────────────────────────────────────────────
def fig_two_doors():
    W, H = 1220, 640
    p = []

    p.append(fitbox(70, 40, 440, 86,
                    ["клієнт NFS шле рукоятку в кожному запиті,",
                     "сервер мусить із байтів дістати файл"],
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(710, 40, 440, 86,
                    ["програма кличе name_to_handle_at,",
                     "а згодом open_by_handle_at"],
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    p.append(arrow(290, 130, 400, 186, color=NEG, sw=2))
    p.append(arrow(930, 130, 820, 186, color=FIELD, sw=2))

    mx, my, mw, mh = 340, 190, 540, 150
    p.append(rect(mx, my, mw, mh, fill=WARM_FILL, stroke=INK, sw=2, rx=10))
    p.append(text(mx + mw / 2, my + 28, "VFS: таблиця export_operations",
                  size=16, bold=True, color=INK))
    p.append(fitbox(mx + 20, my + 44, mw - 40, 44,
                    ["encode_fh: знайдений файл → непрозорі байти"],
                    size=13, fill=BG, stroke=INK, sw=1.2))
    p.append(fitbox(mx + 20, my + 94, mw - 40, 44,
                    ["fh_to_dentry: байти → знову той самий файл"],
                    size=13, fill=BG, stroke=INK, sw=1.2))

    p.append(arrow(mx + mw / 2, my + mh + 4, mx + mw / 2, my + mh + 44,
                   color=INK, sw=2))
    p.append(fitbox(mx, my + mh + 48, mw, 56,
                    ["драйвер файлової системи: ext4 · XFS · Btrfs"],
                    size=14, fill=GREY_FILL, stroke=INK, sw=1.5))
    p.append(arrow(mx + mw / 2, my + mh + 108, mx + mw / 2, my + mh + 148,
                   color=INK, sw=2))
    p.append(fitbox(mx, my + mh + 152, mw, 56,
                    ["inode 4711 · покоління 12"],
                    size=15, fill=BG, stroke=INK, sw=2, bold=True))

    p.append(fitbox(40, 380, 260, 150,
                    ["procfs і sysfs таблиці",
                     "не мають узагалі:",
                     "їхні об'єкти живуть,",
                     "поки живе процес",
                     "чи пристрій."],
                    size=13, fill=RED_FILL, stroke=POS, sw=1.6))
    p.append(fitbox(920, 380, 260, 150,
                    ["Дехто вміє закодувати,",
                     "але не вміє розкодувати:",
                     "рукоятка тоді годиться",
                     "як посвідчення,",
                     "але не як ключ."],
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.6))

    render(os.path.join(IMG, 'two-doors.svg'), W, H, *p)


# ── 4. Будова структури й узгодження розміру ───────────────────────────────
def fig_handle_struct():
    W, H = 1260, 700
    p = []

    px, py, pw, ph = 40, 40, 560, 600
    qx = 660

    p += panel(px, py, pw, ph, "struct file_handle у пам'яті", NEG, BLUE_FILL)
    p += panel(qx, py, pw, ph, "Розмір узгоджують у два виклики", FIELD, GREEN_FILL)

    bx, bw = px + 26, pw - 52
    p.append(fitbox(bx, 108, bw, 96,
                    ["handle_bytes — unsigned int, 4 байти",
                     "[in] скільки місця під байти дав виклик",
                     "[out] скільки насправді треба або зайнято"],
                    size=14, fill=BG, stroke=NEG, sw=1.6))
    p.append(fitbox(bx, 220, bw, 96,
                    ["handle_type — int, 4 байти",
                     "[out] як саме файлова система закодувала;",
                     "молодші 8 бітів — від ФС, старші 16 — від ядра"],
                    size=14, fill=BG, stroke=NEG, sw=1.6))
    p.append(fitbox(bx, 332, bw, 96,
                    ["f_handle[] — рівно handle_bytes байтів",
                     "[out] непрозорі байти рукоятки;",
                     "довжина завжди кратна чотирьом"],
                    size=14, fill=BG, stroke=NEG, sw=1.6))
    p.append(fitbox(bx, 444, bw, 110,
                    ["Хвіст гнучкий: sizeof(struct file_handle) = 8,",
                     "і самої рукоятки в ці 8 байтів не входить.",
                     "malloc(sizeof *fh + MAX_HANDLE_SZ) = 8 + 128 = 136",
                     "вистачає за будь-якої файлової системи."],
                    size=14, fill=WARM_FILL, stroke=INK, sw=1.6))
    p.append(fitbox(bx, 566, bw, 64,
                    ["handle_bytes понад MAX_HANDLE_SZ — це EINVAL,",
                     "а не «стільки, скільки влізе»."],
                    size=14, fill=RED_FILL, stroke=POS, sw=1.6))

    cx, cw = qx + 26, pw - 52
    p.append(fitbox(cx, 108, cw, 76,
                    ["виклик 1: handle_bytes = 0"],
                    size=15, fill=BG, stroke=FIELD, sw=1.8, bold=True))
    p.append(arrow(cx + cw / 2, 186, cx + cw / 2, 206, color=FIELD, sw=2))
    p.append(fitbox(cx, 208, cw, 86,
                    ["−1, errno = EOVERFLOW,",
                     "handle_bytes := 12 — стільки треба"],
                    size=14, fill=WARM_FILL, stroke=INK, sw=1.6))
    p.append(arrow(cx + cw / 2, 296, cx + cw / 2, 316, color=FIELD, sw=2))
    p.append(fitbox(cx, 318, cw, 76,
                    ["виділити sizeof *fh + 12 байтів",
                     "і покласти handle_bytes = 12"],
                    size=14, fill=BG, stroke=FIELD, sw=1.6))
    p.append(arrow(cx + cw / 2, 396, cx + cw / 2, 416, color=FIELD, sw=2))
    p.append(fitbox(cx, 418, cw, 86,
                    ["виклик 2: повертає 0 —",
                     "байти й handle_type на місці"],
                    size=15, fill=BG, stroke=FIELD, sw=1.8, bold=True))
    p.append(fitbox(cx, 522, cw, 108,
                    ["Пастка: EOVERFLOW, а handle_bytes не зріс —",
                     "для цього імені рукоятки немає взагалі.",
                     "Повторювати з більшим буфером марно."],
                    size=14, fill=RED_FILL, stroke=POS, sw=1.8))

    render(os.path.join(IMG, 'handle-struct.svg'), W, H, *p)


# ── Другий прохід покажчика: три різні відповіді ───────────────────────────
def fig_check_flow():
    W, H = 1260, 880
    p = []

    cx, cw = 60, 430
    steps = [
        (50, 84, ["Рядок покажчика:",
                  "UUID · handle_type · байти рукоятки · сума · шлях"], MUTED, GREY_FILL),
        (172, 84, ["Знайти чинне монтування з цим UUID:",
                   "/proc/self/mountinfo + /dev/disk/by-uuid"], INK, BG),
        (294, 84, ["name_to_handle_at(збережений шлях):",
                   "чия рукоятка зараз під цим іменем?"], INK, BG),
        (416, 76, ["той самий handle_type і ті самі байти?"], INK, WARM_FILL),
        (560, 92, ["ні, або шляху вже немає →",
                   "open_by_handle_at(mount_fd, рукоятка)"], INK, WARM_FILL),
    ]
    for i, (yy, hh, lines, color, fill) in enumerate(steps):
        p.append(fitbox(cx, yy, cw, hh, lines, size=14,
                        fill=fill, stroke=color, sw=1.8))
        if i < len(steps) - 1:
            ny = steps[i + 1][0]
            p.append(arrow(cx + cw / 2, yy + hh + 4, cx + cw / 2, ny - 6,
                           color=color, sw=2))

    ox, ow = 730, 470
    outs = [
        (396, 96, ["так → ФАЙЛ НА МІСЦІ",
                   "лишилося звірити контрольну суму"], FIELD, GREEN_FILL,
         (496, 454), (720, 444)),
        (520, 96, ["успіх → ФАЙЛ ПЕРЕЙМЕНОВАНО",
                   "новий шлях — readlink /proc/self/fd/N",
                   "(підказка, а не обіцянка)"], NEG, BLUE_FILL,
         (496, 590), (720, 568)),
        (640, 80, ["ESTALE → ФАЙЛА БІЛЬШЕ НЕМАЄ",
                   "рядок можна виписати з покажчика"], POS, RED_FILL,
         (496, 610), (720, 680)),
        (744, 96, ["EPERM → бракує CAP_DAC_READ_SEARCH",
                   "EOPNOTSUPP → ФС рукояток не вміє",
                   "обидва рази — відкіт на звичайний обхід"], MUTED, GREY_FILL,
         (496, 630), (720, 792)),
    ]
    for yy, hh, lines, color, fill, a, b in outs:
        p.append(arrow(a[0], a[1], b[0], b[1], color=color, sw=2))
        p.append(fitbox(ox, yy, ow, hh, lines, size=14,
                        fill=fill, stroke=color, sw=1.8, bold=True))

    render(os.path.join(IMG, 'check-flow.svg'), W, H, *p)


fig_identity()
fig_two_roads()
fig_two_doors()
fig_handle_struct()
fig_check_flow()
print("ok")
