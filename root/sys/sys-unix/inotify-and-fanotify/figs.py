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
GREY_FILL = "#f1f3f5"
WARM = "#b8860b"


# ── 1. Де саме стоїть гачок сповіщення ──────────────────────────────────────
def fig_hook_in_vfs():
    W, H = 1320, 900
    p = []

    CX, CW = 380, 420           # центральна колона «шари ядра»
    RX, RW = 900, 380           # права колона «підписники»

    p.append(text(CX + CW / 2, 44, "шлях звичайної зміни файлу", size=17, bold=True, color=MUTED))
    p.append(text(RX + RW / 2, 44, "хто про неї дізнається", size=17, bold=True, color=MUTED))

    # центральна колона
    layers = [
        (80, "процес простору користувача", ["write(fd, ...)  ·  rename()  ·  unlink()"], BLUE_FILL, NEG),
        (230, "спільний шар VFS", ["розбір шляху, dentry, inode,", "перевірка прав — однакові для всіх ФС"], WARM_FILL, WARM),
        (420, "конкретна файлова система", ["ext4  ·  XFS  ·  Btrfs  ·  tmpfs"], GREEN_FILL, FIELD),
        (560, "блоковий пристрій", ["сектори на носії"], GREY_FILL, MUTED),
    ]
    for y, title, body, fill, stroke in layers:
        h = 56 + 26 * len(body)
        p.append(rect(CX, y, CW, h, fill=fill, stroke=stroke, sw=2, rx=9))
        p.append(text(CX + CW / 2, y + 30, title, size=16, bold=True, color=stroke))
        for i, ln in enumerate(body):
            p.append(text(CX + CW / 2, y + 58 + 24 * i, ln, size=14, color=INK))

    # межа виклику
    p.append(line(CX - 300, 196, CX + CW + 40, 196, color=POS, sw=1.6, dash="7 6"))
    p.append(text(CX - 296, 188, "межа виклику до ядра", size=13, anchor="start", color=POS))

    # стрілки вниз по колоні
    p.append(arrow(CX + CW / 2, 162, CX + CW / 2, 224, color=INK, sw=2))
    p.append(arrow(CX + CW / 2, 340, CX + CW / 2, 414, color=INK, sw=2))
    p.append(arrow(CX + CW / 2, 502, CX + CW / 2, 554, color=INK, sw=2))

    # гачок
    HX, HY, HW, HH = CX + CW + 60, 258, 250, 66
    p.append(fitbox(HX, HY, HW, HH, ["гачок fsnotify", "у спільному коді VFS"],
                    size=15, bold=True, fill=RED_FILL, stroke=POS, sw=2.4, color=POS))
    p.append(arrow(CX + CW + 6, HY + HH / 2, HX - 8, HY + HH / 2, color=POS, sw=2.2))

    # права колона: дві групи
    p.append(fitbox(RX, 400, RW, 86, ["черга групи inotify", "події з іменем відносно каталогу"],
                    size=15, fill=BLUE_FILL, stroke=NEG, sw=2, color=INK))
    p.append(fitbox(RX, 530, RW, 86, ["черга групи fanotify", "події з дескриптором або ручкою"],
                    size=15, fill=GREEN_FILL, stroke=FIELD, sw=2, color=INK))
    # до inotify — навскіс; до fanotify — вниз ЛІВІШЕ за рамки, щоб не перетнути напис
    p.append(arrow(960, HY + HH + 8, 1000, 394, color=POS, sw=2))
    p.append(line(880, HY + HH, 880, 573, color=POS, sw=2))
    p.append(arrow(880, 573, RX - 8, 573, color=POS, sw=2))

    p.append(text(RX + RW / 2, 672, "обидві черги підписник читає звичайним read(),",
                  size=15, color=INK))
    p.append(text(RX + RW / 2, 696, "як будь-який інший дескриптор", size=15, color=INK))

    # два шляхи повз гачок
    p.append(fitbox(30, 430, 300, 84, ["інший клієнт NFS змінив файл", "на сервері — цей VFS", "запиту не бачив"],
                    size=14, fill="#ffffff", stroke=MUTED, sw=1.6, color=MUTED))
    p.append(arrow(334, 472, CX - 8, 472, color=MUTED, sw=1.8))

    p.append(fitbox(30, 596, 300, 84, ["запис просто в /dev/sda", "повз файлову систему —", "гачок нижче не сягає"],
                    size=14, fill="#ffffff", stroke=MUTED, sw=1.6, color=MUTED))
    p.append(arrow(334, 638, CX - 8, 638, color=MUTED, sw=1.8))

    p.append(fitbox(30, 790, 1240, 62,
                    ["видно рівно те, що пройшло через VFS цього ядра — ні байтом більше"],
                    size=17, bold=True, fill=WARM_FILL, stroke=WARM, sw=2.2, color=INK))

    render(os.path.join(IMG, 'hook-in-vfs.svg'), W, H, *p)


# ── 2. Стеження живе на inode, а не на імені ────────────────────────────────
def fig_watch_follows_inode():
    W, H = 1300, 720
    p = []

    p.append(text(300, 46, "до збереження", size=18, bold=True, color=MUTED))
    p.append(text(1000, 46, "після rename()", size=18, bold=True, color=MUTED))
    p.append(line(650, 70, 650, 620, color=MUTED, sw=1.4, dash="8 7"))

    def panel(x0, entries, objects):
        out = []
        out.append(fitbox(x0, 90, 460, 52, ["каталог /etc"], size=16, bold=True,
                          fill=GREY_FILL, stroke=MUTED, sw=1.8, color=INK))
        y = 162
        for name, target, col in entries:
            out.append(rect(x0, y, 460, 46, fill="#ffffff", stroke=col, sw=1.8, rx=6))
            out.append(text(x0 + 18, y + 30, name, size=15, anchor="start", color=INK))
            out.append(text(x0 + 442, y + 30, target, size=15, anchor="end", color=col, bold=True))
            y += 60
        for oy, title, body, fill, stroke in objects:
            out.append(rect(x0, oy, 460, 96, fill=fill, stroke=stroke, sw=2, rx=9))
            out.append(text(x0 + 230, oy + 30, title, size=16, bold=True, color=stroke))
            out.append(text(x0 + 230, oy + 58, body[0], size=14, color=INK))
            out.append(text(x0 + 230, oy + 82, body[1], size=14, color=INK))
        return out

    p += panel(60, [("app.conf", "inode 42", NEG)],
               [(320, "inode 42", ["вміст: стара версія", "імен на нього: 1"], BLUE_FILL, NEG)])
    p.append(fitbox(60, 460, 460, 62, ["wd = 1 стежить за inode 42"],
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2.2, color=INK))
    p.append(arrow(290, 454, 290, 424, color=FIELD, sw=2))

    p += panel(760, [("app.conf", "inode 77", POS)],
               [(320, "inode 77 — новий об'єкт", ["вміст: те, що ви зберегли", "стеження на ньому немає"], RED_FILL, POS),
                (450, "inode 42 — без імен", ["лічильник імен: 0", "живе лише поки є стеження"], GREY_FILL, MUTED)])
    p.append(fitbox(760, 578, 460, 62, ["wd = 1 усе ще стежить за inode 42"],
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2.2, color=INK))
    p.append(arrow(990, 572, 990, 552, color=FIELD, sw=2))

    p.append(arrow(534, 210, 748, 210, color=INK, sw=2.4))
    p.append(text(641, 178, "редактор пише app.conf.tmp,", size=14, color=INK))
    p.append(text(641, 156, "потім rename() поверх імені", size=14, color=INK))

    p.append(fitbox(60, 660, 1160, 56,
                    ["шлях розібрано один раз, під час підписки; далі стеження прив'язане до об'єкта, а ім'я вільне піти"],
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=2.2, color=INK))

    render(os.path.join(IMG, 'watch-follows-inode.svg'), W, H, *p)


# ── 3. Дві форми покриття ───────────────────────────────────────────────────
def fig_coverage_shapes():
    W, H = 1340, 780
    p = []

    p.append(text(340, 46, "inotify: підписка на кожен об'єкт", size=18, bold=True, color=NEG))
    p.append(text(1000, 46, "fanotify: одна позначка на ФС", size=18, bold=True, color=FIELD))
    p.append(line(670, 70, 670, 560, color=MUTED, sw=1.4, dash="8 7"))

    tree = [(0, "/srv/app"), (1, "src"), (2, "ui"), (1, "node_modules"), (2, "left-pad"), (1, "build")]

    def draw_tree(x0, badge_each, tint):
        out = []
        y = 110
        if tint:
            out.append(rect(x0 - 24, 86, 520, 340, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=12))
        for depth, name in tree:
            bx = x0 + depth * 52
            out.append(rect(bx, y, 250, 40, fill="#ffffff", stroke=MUTED, sw=1.5, rx=6))
            out.append(text(bx + 16, y + 26, name, size=15, anchor="start", color=INK))
            if badge_each:
                out.append(circle(bx + 276, y + 20, 15, fill=BLUE_FILL, stroke=NEG, sw=2))
                out.append(text(bx + 276, y + 25, "w", size=14, color=NEG, bold=True))
            y += 54
        return out

    p += draw_tree(80, True, False)
    p += draw_tree(760, False, True)
    p.append(circle(1236, 116, 22, fill=GREEN_FILL, stroke=FIELD, sw=2.6))
    p.append(text(1236, 122, "M", size=17, color=FIELD, bold=True))
    p.append(text(1236, 162, "одна", size=14, color=FIELD))
    p.append(text(1236, 182, "позначка", size=14, color=FIELD))

    left = ["пам'ять зростає з кількістю каталогів",
            "новий підкаталог треба доглянути вручну",
            "між читанням каталогу й підпискою є щілина",
            "подія несе ІМ'Я всередині каталогу"]
    right = ["пам'ять стала, скільки б не було файлів",
             "усе створене далі покрито одразу",
             "щілини немає — покриття не перелічує об'єктів",
             "подія несе ОБ'ЄКТ: дескриптор або ручку"]

    y = 470
    for a, b in zip(left, right):
        p.append(fitbox(80, y, 540, 46, [a], size=14, fill=BLUE_FILL, stroke=NEG, sw=1.5, color=INK))
        p.append(fitbox(720, y, 540, 46, [b], size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.5, color=INK))
        y += 58

    p.append(fitbox(80, 712, 1180, 54,
                    ["імені за одну позначку не дістати задарма: широке покриття платить утратою назви"],
                    size=16, bold=True, fill=WARM_FILL, stroke=WARM, sw=2.2, color=INK))

    render(os.path.join(IMG, 'coverage-shapes.svg'), W, H, *p)


# ── 4. Подія після дії проти події перед дією ───────────────────────────────
def fig_permission_timeline():
    W, H = 1300, 700
    p = []

    LX, LW = 240, 900

    def lane(y, who, color):
        out = [text(LX - 26, y + 6, who, size=15, anchor="end", bold=True, color=color),
               line(LX, y, LX + LW, y, color=MUTED, sw=1.4)]
        return out

    def tick(x, y, label, color, above=True):
        dy = -20 if above else 34
        return [line(x, y - 9, x, y + 9, color=color, sw=2.4),
                text(x, y + dy, label, size=13, color=color)]

    # верхній випадок — inotify
    p.append(fitbox(LX, 60, LW, 44, ["inotify: гачок спрацьовує, коли справу вже зроблено"],
                    size=16, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2, color=INK))
    p += lane(180, "актор", INK)
    p += tick(330, 180, "write() ", INK)
    p += tick(560, 180, "дані у сторінковому кеші", INK, above=False)
    p += tick(760, 180, "write() повернувся", INK)
    p += lane(290, "підписник", NEG)
    p += tick(900, 290, "подія прочитана з черги", NEG, above=False)
    p.append(arrow(560, 196, 890, 278, color=NEG, sw=1.8))
    p.append(fitbox(940, 150, 320, 90, ["до цієї миті актор уже пішов —", "лишається тільки дізнатися", "про минуле"],
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.6, color=INK))

    # нижній випадок — fanotify
    p.append(fitbox(LX, 400, LW, 44, ["fanotify: подія-дозвіл спиняє актора всередині виклику"],
                    size=16, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2, color=INK))
    p += lane(520, "актор", INK)
    p += tick(330, 520, "open() ", INK)
    p += tick(880, 520, "open() повернув fd", INK)
    p.append(rect(340, 506, 528, 28, fill=RED_FILL, stroke=POS, sw=2, rx=6))
    p.append(text(604, 526, "заблокований у ядрі", size=14, color=POS, bold=True))
    p += lane(630, "підписник", FIELD)
    p += tick(430, 630, "подія FAN_OPEN_PERM", FIELD, above=False)
    p += tick(790, 630, "write(FAN_ALLOW)", FIELD, above=False)
    p.append(arrow(348, 534, 424, 618, color=POS, sw=1.8))
    p.append(arrow(796, 618, 872, 534, color=FIELD, sw=1.8))
    p.append(fitbox(940, 590, 320, 90, ["скільки думає підписник —", "стільки стоїть актор;", "мовчання = зупинка системи"],
                    size=14, fill=GREY_FILL, stroke=MUTED, sw=1.6, color=INK))

    render(os.path.join(IMG, 'permission-timeline.svg'), W, H, *p)


# ── 5. Порядок обходу: де щілина і чим вона обертається ─────────────────────
def fig_walk_order_gap():
    W, H = 1300, 660
    p = []

    def half(y0, title, tfill, tstroke, left_call, right_call,
             band_fill, band_stroke, band_lines):
        q = []
        q.append(fitbox(60, y0, 1180, 44, [title],
                        size=17, bold=True, fill=tfill, stroke=tstroke, sw=2, color=INK))
        yb = y0 + 84                      # верх смуги
        BH = 96
        yc = yb + BH / 2                  # вісь часу
        q.append(text(240, yb - 16, left_call, size=16, bold=True, color=tstroke))
        q.append(text(1000, yb - 16, right_call, size=16, bold=True, color=tstroke))
        q.append(line(120, yc, 236, yc, color=INK, sw=2))
        q.append(arrow(1004, yc, 1130, yc, color=INK, sw=2))
        q.append(text(1160, yc + 6, "час", size=14, anchor="start", color=MUTED))
        q.append(fitbox(240, yb, 760, BH, band_lines,
                        size=16, fill=band_fill, stroke=band_stroke, sw=2.4, color=INK))
        return q

    p += half(56, "спершу читаємо каталог, потім вішаємо стеження",
              RED_FILL, POS, "readdir(d)", "inotify_add_watch(d)",
              RED_FILL, POS,
              ["у цю мить хтось створив d/x",
               "у переліку його не було  ·  події не буде",
               "втрачено назавжди"])

    p += half(316, "спершу вішаємо стеження, потім читаємо каталог",
              GREEN_FILL, FIELD, "inotify_add_watch(d)", "readdir(d)",
              GREEN_FILL, FIELD,
              ["у цю мить хтось створив d/x",
               "подія Є  ·  у переліку теж Є",
               "дублікат, але не втрата"])

    p.append(fitbox(60, 574, 1180, 52,
                    ["щілина є в обох випадках — порядок міняє не її наявність, а її ціну"],
                    size=17, bold=True, fill=WARM_FILL, stroke=WARM, sw=2, color=INK))

    render(os.path.join(IMG, 'walk-order-gap.svg'), W, H, *p)


# ── 6. Карта wd → шлях: повний рядок проти ланки на батька ──────────────────
def fig_wd_path_map():
    W, H = 1360, 650
    p = []

    p.append(fitbox(60, 50, 1240, 46,
                    ["у /srv/app перейменували src → lib: одна пара MOVED_FROM / MOVED_TO"],
                    size=17, bold=True, fill=WARM_FILL, stroke=WARM, sw=2, color=INK))

    RH = 40
    Y0 = 156

    def row(x, y, widths, cells, fills, size=15, bold=False):
        q = []
        cx = x
        for w, s, f in zip(widths, cells, fills):
            q.append(fitbox(cx, y, w, RH, [s], size=size, pad=10,
                            fill=f, stroke=MUTED, sw=1.4, color=INK, bold=bold, rx=4))
            cx += w
        return q

    # ── ліва таблиця: повні рядки ──
    p.append(text(340, 132, "карта wd → повний рядок", size=17, bold=True, color=POS))
    LW = [110, 470]
    p += row(60, Y0, LW, ["wd", "збережений шлях"], [GREY_FILL, GREY_FILL], bold=True)
    left = [("1", "/srv/app", GREY_FILL),
            ("2", "/srv/app/src", RED_FILL),
            ("3", "/srv/app/src/ui", RED_FILL),
            ("4", "/srv/app/src/ui/img", RED_FILL)]
    for i, (wd, s, f) in enumerate(left):
        p += row(60, Y0 + RH * (i + 1), LW, [wd, s], [f, f])
    p.append(fitbox(60, Y0 + RH * 5 + 22, 580, 112,
                    ["недійсні всі рядки з переписаним префіксом —",
                     "три з чотирьох; знайти їх можна лише",
                     "перебравши всю таблицю до кінця"],
                    size=15, fill=RED_FILL, stroke=POS, sw=2, color=INK))

    # ── права таблиця: ланка на батька ──
    p.append(text(1000, 132, "карта wd → (батько, ім'я)", size=17, bold=True, color=FIELD))
    RW = [100, 120, 360]
    p += row(720, Y0, RW, ["wd", "батько", "ім'я"],
             [GREY_FILL] * 3, bold=True)
    right = [("1", "—", "/srv/app", GREY_FILL),
             ("2", "1", "src → lib", GREEN_FILL),
             ("3", "2", "ui", GREY_FILL),
             ("4", "3", "img", GREY_FILL)]
    for i, (wd, par, nm, f) in enumerate(right):
        p += row(720, Y0 + RH * (i + 1), RW, [wd, par, nm], [f, f, f])
    p.append(fitbox(720, Y0 + RH * 5 + 22, 580, 112,
                    ["ім'я лежить окремо від батька —",
                     "перейменування міняє одну комірку,",
                     "шляхи гілки не зберігалися ніде"],
                    size=15, fill=GREEN_FILL, stroke=FIELD, sw=2, color=INK))

    p.append(fitbox(60, 556, 1240, 52,
                    ["повний шлях будують на вимогу, підйомом до кореня"],
                    size=17, bold=True, fill=BLUE_FILL, stroke=NEG, sw=2, color=INK))

    render(os.path.join(IMG, 'wd-path-map.svg'), W, H, *p)


fig_hook_in_vfs()
fig_watch_follows_inode()
fig_coverage_shapes()
fig_permission_timeline()
fig_walk_order_gap()
fig_wd_path_map()
print("ok")
