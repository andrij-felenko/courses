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


def panel(x, y, w, h, title, rows, muted_last=True, fill=BLUE_FILL, stroke=NEG):
    """Рамка з заголовком і рядками тексту (моноширинне вирівнювання не потрібне —
    другу колонку ставимо на фіксованому зсуві)."""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8),
           text(x + w / 2, y + 25, title, size=14, bold=True, color=stroke),
           line(x, y + 38, x + w, y + 38, color=stroke, sw=1.2)]
    ty = y + 66
    for i, r in enumerate(rows):
        last = (i == len(rows) - 1)
        color = MUTED if (muted_last and last) else INK
        size = 12 if (muted_last and last) else 13
        if isinstance(r, tuple):
            out.append(text(x + 22, ty, r[0], size=size, anchor="start", color=color))
            out.append(text(x + 250, ty, r[1], size=size, anchor="start", color=POS))
        else:
            out.append(text(x + 22, ty, r, size=size, anchor="start", color=color))
        ty += 30 if not last else 34
    return out


# ── 1. Монтування — правило в пам'яті ядра ──────────────────────────────────
def fig_mount_junction():
    W, H = 1140, 700
    p = []

    p += panel(50, 60, 460, 235, "файлова система кореня — sda2",
               [("/", "inode 2"),
                ("└ etc/", "inode 12"),
                ("└ mnt/", "inode 128"),
                ("      └ old.txt", "inode 129"),
                "номер inode чинний лише всередині цієї ФС"])

    p += panel(630, 60, 460, 235, "файлова система на sdb1",
               [("/", "inode 2"),
                ("└ data/", "inode 11"),
                ("└ log/", "inode 27"),
                ("", ""),
                "номер 2 тут свій — і збігається з чужим"],
               fill=GREEN_FILL, stroke=FIELD)

    # об'єкт монтування
    mx, my, mw, mh = 310, 345, 520, 165
    p.append(rect(mx, my, mw, mh, fill=WARM_FILL, stroke=WARM, sw=2.2, rx=10))
    p.append(text(mx + mw / 2, my + 26, "об'єкт монтування — живе лише в пам'яті ядра",
                  size=13.5, bold=True, color=WARM))
    p.append(line(mx, my + 40, mx + mw, my + 40, color=WARM, sw=1.2))
    fields = ["суперблок:  sdb1, ext4",
              "корінь монтування:  inode 2 файлової системи sdb1",
              "точка:  запис mnt (inode 128) у монтуванні кореня",
              "на носіях від цього не змінено жодного байта"]
    for i, f in enumerate(fields):
        col = MUTED if i == len(fields) - 1 else INK
        p.append(text(mx + 24, my + 70 + i * 28, f, size=12.5 if i == 3 else 13,
                      anchor="start", color=col))

    p.append(arrow(mx + 90, my, 300, 300, color=WARM, sw=2))
    p.append(arrow(mx + mw - 90, my, 850, 300, color=WARM, sw=2))

    # нижній ланцюг розбору шляху
    p.append(text(50, 552, "розбір шляху /mnt/data:", size=14, bold=True, anchor="start"))
    bw, bh, by = 210, 64, 585
    cells = [(45, "/", "sda2, inode 2"),
             (295, "mnt", "sda2, inode 128"),
             (555, "/", "sdb1, inode 2"),
             (815, "data", "sdb1, inode 11")]
    for i, (bx, a, b) in enumerate(cells):
        fill = BLUE_FILL if i < 2 else GREEN_FILL
        stroke = NEG if i < 2 else FIELD
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=stroke, sw=1.6, rx=8))
        p.append(text(bx + bw / 2, by + 26, a, size=14, bold=True))
        p.append(text(bx + bw / 2, by + 47, b, size=11.5, color=MUTED))
    for bx in (255, 515, 775):
        p.append(arrow(bx, by + bh / 2, bx + 38, by + bh / 2, color=INK, sw=2))
    p.append(text(535, 566, "підміна", size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'mount-junction.svg'), W, H, *p,
           title="Монтування: правило в пам'яті, а не запис на носії")


# ── 2. Дерево монтувань ─────────────────────────────────────────────────────
def fig_mount_tree():
    W, H = 1160, 665
    p = []

    def node(x, y, head, rows, stroke=NEG, fill=BLUE_FILL):
        w, h = 310, 120
        out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8),
               text(x + w / 2, y + 25, head, size=13.5, bold=True, color=stroke),
               line(x, y + 36, x + w, y + 36, color=stroke, sw=1.1)]
        for i, r in enumerate(rows):
            out.append(text(x + 18, y + 62 + i * 25, r, size=12.5, anchor="start"))
        return out

    p += node(425, 60, "монтування 25",
              ["суперблок: sda2 (ext4)", "корінь монтування: /", "точка: корінь простору імен"])
    p += node(40, 265, "монтування 31",
              ["суперблок: sda3 (ext4)", "корінь монтування: /", "точка: /home"])
    p += node(425, 265, "монтування 44",
              ["суперблок: sdb1 (vfat)", "корінь монтування: /", "точка: /mnt/usb"])
    p += node(810, 265, "монтування 52 — прив'язка",
              ["суперблок: sda3 (той самий)", "корінь монтування: /ann/pub", "точка: /srv/pub"],
              stroke=POS, fill=RED_FILL)

    for cx in (195, 580, 965):
        p.append(arrow(580, 180, cx, 265, color=INK, sw=1.8))

    p.append(rect(120, 475, 300, 66, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(270, 502, "суперблок sda3", size=13.5, bold=True, color=FIELD))
    p.append(text(270, 524, "один примірник файлової системи", size=11.5, color=MUTED))

    p.append(rect(660, 475, 250, 66, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(785, 502, "суперблок sdb1", size=13.5, bold=True, color=FIELD))
    p.append(text(785, 524, "флешка у порту", size=11.5, color=MUTED))

    p.append(arrow(195, 385, 250, 475, color=FIELD, sw=1.6))
    p.append(arrow(580, 385, 730, 475, color=FIELD, sw=1.6))
    p.append(arrow(950, 385, 380, 475, color=POS, sw=1.6))

    p.append(text(W / 2, 590, "Два монтування можуть дивитися на один суперблок:",
                  size=13, color=INK))
    p.append(text(W / 2, 614, "прив'язка не копіює дані, а додає другий вхід у ту саму ФС",
                  size=13, color=INK))

    render(os.path.join(IMG, 'mount-tree.svg'), W, H, *p,
           title="Дерево монтувань: вузли — не каталоги, а монтування")


# ── 3. Поширення подій монтування ───────────────────────────────────────────
def fig_propagation():
    W, H = 1080, 580
    p = []

    rows = [
        (140, "спільне\n(shared)", "простір А\nмонтуємо /mnt/usb", "простір Б\nмонтування з'явилося", "both",
         "подія йде в обидва боки"),
        (300, "підлегле\n(slave)", "господар\nмонтуємо /mnt/usb", "підлеглий\nмонтування з'явилося", "one",
         "чути господаря, назад не йде"),
        (460, "приватне\n(private)", "простір А\nмонтуємо /mnt/usb", "простір Б\nнічого не сталося", "none",
         "подія лишається вдома"),
    ]

    for y, tag, a, b, mode, cap in rows:
        body, w, h = textbox(115, y, tag, size=13, bold=True, pad=12,
                             fill=WARM_FILL, stroke=WARM, sw=1.8, min_w=170)
        p.append(body)
        ba, wa, ha = textbox(360, y, a, size=12.5, pad=12, fill=BLUE_FILL, stroke=NEG, sw=1.8, min_w=250)
        p.append(ba)
        bb, wb, hb = textbox(870, y, b, size=12.5, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.8, min_w=250)
        p.append(bb)

        x1, x2 = 500, 740
        if mode == "both":
            p.append(arrow(x1, y - 14, x2, y - 14, color=INK, sw=2))
            p.append(arrow(x2, y + 14, x1, y + 14, color=INK, sw=2))
        elif mode == "one":
            p.append(arrow(x1, y, x2, y, color=INK, sw=2))
        else:
            p.append(line(x1 + 90, y - 20, x1 + 130, y + 20, color=POS, sw=3))
            p.append(line(x1 + 130, y - 20, x1 + 90, y + 20, color=POS, sw=3))
        p.append(text(620, y - 52, cap, size=12, color=MUTED))

    render(os.path.join(IMG, 'mount-propagation.svg'), W, H, *p,
           title="Куди йде подія монтування між просторами імен")


# ── 4. Рядок mountinfo поле за полем (вставка api-) ─────────────────────────
def fig_mountinfo_line():
    W, H = 1270, 545
    p = []
    X0 = 40
    GAP = 12
    BH = 58

    def row(y, cells):
        x = X0
        for n, val, label, fill, stroke in cells:
            w = val[1]
            p.append(text(x + w / 2, y - 13, n, size=12, bold=True, color=MUTED))
            p.append(fitbox(x, y, w, BH, val[0], size=15, pad=10,
                            fill=fill, stroke=stroke, sw=1.8, rx=8))
            p.append(text(x + w / 2, y + BH + 22, label, size=11.5, color=MUTED))
            x += w + GAP
        return x

    r1 = [
        ("1", ("36", 110), "ID монтування", BLUE_FILL, NEG),
        ("2", ("25", 110), "ID батька", BLUE_FILL, NEG),
        ("3", ("8:3", 100), "major:minor", BLUE_FILL, NEG),
        ("4", ("/ann/pub", 170), "корінь монтування", GREEN_FILL, FIELD),
        ("5", ("/srv/pub", 170), "точка монтування", GREEN_FILL, FIELD),
        ("6", ("rw,relatime", 190), "прапорці монтування", GREEN_FILL, FIELD),
        ("7", ("shared:12 master:7", 300), "необов'язкові: 0…4 поля", WARM_FILL, WARM),
    ]
    row(115, r1)

    r2 = [
        ("8", ("-", 70), "роздільник", RED_FILL, POS),
        ("9", ("ext4", 130), "тип ФС[.підтип]", BLUE_FILL, NEG),
        ("10", ("/dev/sda3", 190), "джерело", BLUE_FILL, NEG),
        ("11", ("ro,seclabel", 210), "прапорці суперблока", BLUE_FILL, NEG),
    ]
    xend = row(285, r2)

    nx = xend + 46
    p.append(fitbox(nx, 279, W - nx - 40, 70,
                    "Розбирати рядок треба ВІД роздільника:\n"
                    "поля 9–11 читаємо після «-», бо скільки\n"
                    "полів стоїть перед ним — заздалегідь невідомо",
                    size=13, pad=12, fill=FILL, stroke=MUTED, sw=1.4, rx=8))

    p.append(fitbox(X0, 420, W - 2 * X0, 78,
                    "У полях 4, 5 і 10 пробіл, табуляція, перевід рядка й зворотна скісна риска\n"
                    "записані вісімковим кодом: \\040  \\011  \\012  \\134 — розбір мусить їх розгортати",
                    size=14, pad=14, fill=WARM_FILL, stroke=WARM, sw=1.8, rx=8))

    render(os.path.join(IMG, 'mountinfo-line.svg'), W, H, *p,
           title="Рядок /proc/self/mountinfo поле за полем")


# ── 5. Порядок викликів нового набору 5.2 (вставка api-) ────────────────────
def fig_mount_api_chain():
    W, H = 1180, 856
    p = []
    cols = [(40, 380), (450, 330), (810, 330)]
    heads = ["створити новий примірник ФС",
             "узяти вже наявне піддерево",
             "перенастроїти змонтоване"]
    steps = [
        [("fsopen(\"ext4\", 0)", "→ fd контексту файлової системи"),
         ("fsconfig(SET_STRING, \"source\", \"/dev/sdb1\", 0)",
          "fsconfig(SET_FLAG, \"ro\", NULL, 0)",
          "кожен параметр окремо — і окрема помилка"),
         ("fsconfig(CMD_CREATE, NULL, NULL, 0)", "→ суперблок створено"),
         ("fsmount(fd, 0, MOUNT_ATTR_NODEV)", "→ fd відокремленого монтування"),
         ("move_mount(mfd, \"\", AT_FDCWD, \"/mnt\",",
          "           MOVE_MOUNT_F_EMPTY_PATH)", "→ монтування стало в дерево")],
        [("open_tree(AT_FDCWD, \"/data\",", "  OPEN_TREE_CLONE | AT_RECURSIVE)",
          "→ fd відокремленої копії"),
         ("mount_setattr(fd, \"\", AT_EMPTY_PATH,", "              &attr, sizeof attr)",
          "за потреби: ro, idmap, поширення"),
         ("move_mount(fd, \"\", AT_FDCWD,", "           \"/srv/data\", F_EMPTY_PATH)")],
        [("fspick(AT_FDCWD, \"/data\",", "       FSPICK_NO_AUTOMOUNT)",
          "→ fd контексту наявної ФС"),
         ("fsconfig(SET_FLAG, \"noatime\", NULL, 0)", "міняємо параметр"),
         ("fsconfig(CMD_RECONFIGURE, NULL, NULL, 0)", "≈ mount(2) з MS_REMOUNT")],
    ]
    fills = [(BLUE_FILL, NEG), (GREEN_FILL, FIELD), (WARM_FILL, WARM)]

    BH, GAPV, Y0 = 88, 34, 150
    for (x, w), head, chain, (fill, stroke) in zip(cols, heads, steps, fills):
        p.append(fitbox(x, 60, w, 52, head, size=14, bold=True, pad=12,
                        fill=fill, stroke=stroke, sw=2, rx=8))
        y = Y0
        for i, body in enumerate(chain):
            p.append(fitbox(x, y, w, BH, list(body), size=12.5, pad=12,
                            fill=FILL, stroke=stroke, sw=1.6, rx=8))
            if i < len(chain) - 1:
                p.append(arrow(x + w / 2, y + BH, x + w / 2, y + BH + GAPV,
                               color=stroke, sw=2))
            y += BH + GAPV
        p.append(arrow(x + w / 2, 112, x + w / 2, Y0, color=stroke, sw=2))

    p.append(fitbox(40, 758, W - 80, 66,
                    "Кожен крок віддає файловий дескриптор: монтування існує як річ у руках\n"
                    "ще до того, як у нього з'явилося місце в дереві — і навіть в іншому просторі імен",
                    size=13.5, pad=14, fill=FILL, stroke=MUTED, sw=1.4, rx=8))

    render(os.path.join(IMG, 'mount-api-chain.svg'), W, H, *p,
           title="Порядок викликів нового набору монтування (Linux 5.2)")


# ── 6. Обхід дерева проти найдовшого збігу по стовпчику точок ───────────────
def fig_mountinfo_walk():
    W, H = 1260, 730
    p = []

    p.append(text(340, 62, "дерево, зібране за парою «ідентифікатор — батько»",
                  size=14, bold=True, color=MUTED))
    p.append(text(1000, 62, "обхід, як його робить ядро", size=14, bold=True, color=MUTED))

    def box(cx, cy, lines, fill=BLUE_FILL, stroke=NEG):
        b, w, h = textbox(cx, cy, lines, size=12.5, pad=11, fill=fill, stroke=stroke,
                          sw=1.8, rx=8)
        p.append(b)
        return cx, cy, w, h

    ax, ay, aw, ah = box(340, 105, "монтування 28 — точка /\next4 /dev/sda2")
    bx, by, bw, bh = box(340, 250, "монтування 44 — точка /mnt/usb\n"
                                   "vfat /dev/sdb1 · відносна точка: mnt/usb")
    cx_, cy_, cw_, ch_ = box(190, 415, "монтування 61 — точка /mnt/usb\n"
                                       "tmpfs · відносна точка: сам корінь 44",
                             fill=GREEN_FILL, stroke=FIELD)
    dx, dy, dw, dh = box(560, 415, "монтування 70 — точка /mnt/usb/photos\n"
                                   "tmpfs · відносна точка: photos",
                         fill=RED_FILL, stroke=POS)

    p.append(arrow(ax, ay + ah / 2 + 3, bx, by - bh / 2 - 3, color=INK, sw=2))
    p.append(arrow(bx - 60, by + bh / 2 + 3, cx_ + 30, cy_ - ch_ / 2 - 3, color=INK, sw=2))
    p.append(arrow(bx + 60, by + bh / 2 + 3, dx - 30, dy - dh / 2 - 3, color=INK, sw=2))
    p.append(text(560, 415 + dh / 2 + 26, "недосяжне: 61 накрило точку /mnt/usb",
                  size=12, color=POS))

    steps = [
        "старт: монтування 28, позиція /",
        "крок mnt → 28:/mnt, дитини тут немає",
        "крок usb → 28:/mnt/usb, тут дитина 44",
        "у 44 позиція /, а на корені 44 стоїть 61",
        "крок photos → 61:/photos, дітей немає",
    ]
    sy = 105
    prev = None
    for i, s in enumerate(steps):
        fill = GREEN_FILL if i == len(steps) - 1 else FILL
        stroke = FIELD if i == len(steps) - 1 else LINE
        b, w, h = textbox(1000, sy, s, size=12.5, pad=11, fill=fill, stroke=stroke,
                          sw=1.8, rx=8)
        p.append(b)
        if prev is not None:
            p.append(arrow(1000, prev + 3, 1000, sy - h / 2 - 3, color=MUTED, sw=1.8))
        prev = sy + h / 2
        sy += 82

    p.append(line(60, 560, W - 60, 560, color=MUTED, sw=1.2, dash="6,5"))

    b, w, h = textbox(340, 640, "найдовший збіг по стовпчику точок дає 70\n"
                                "але в цю точку вже не потрапити",
                      size=13, pad=13, fill=RED_FILL, stroke=POS, sw=2, rx=8)
    p.append(b)
    b, w, h = textbox(930, 640, "обхід дерева дає 61, а всередині ФС — /photos\n"
                                "саме туди й потрапить open()",
                      size=13, pad=13, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8)
    p.append(b)

    render(os.path.join(IMG, 'mountinfo-walk.svg'), W, H, *p,
           title="Шлях /mnt/usb/photos: чому найдовший збіг дає не ту відповідь")


# ── 7. Зняття екранування: чому один прохід, а не низка замін ───────────────
def fig_mountinfo_unescape():
    W, H = 1020, 560
    p = []

    def cells(cx, cy, chars, stroke=LINE, fill=FILL, cw=38, gap=7, size=17):
        n = len(chars)
        total = n * cw + (n - 1) * gap
        x = cx - total / 2
        out = []
        for ch in chars:
            out.append(rect(x, cy - cw / 2, cw, cw, fill=fill, stroke=stroke, sw=1.8, rx=5))
            out.append(text(x + cw / 2, cy + size * 0.36, ch, size=size, bold=True, color=stroke))
            x += cw + gap
        return out

    p.append(text(510, 78, "справжнє ім'я каталогу — шість символів", size=13, color=MUTED))
    p += cells(510, 118, ["a", "\\", "0", "4", "0", "b"], stroke=NEG, fill=BLUE_FILL)

    p.append(arrow(510, 148, 510, 178, color=INK, sw=2))
    p.append(text(510, 205, "ядро екранує сам зворотний слеш — у файлі стоїть рядок",
                  size=13, color=MUTED))
    b, w, h = textbox(510, 243, "a\\134040b", size=17, pad=12, fill=WARM_FILL,
                      stroke=WARM, sw=2, rx=6, bold=True, color=WARM)
    p.append(b)

    p.append(arrow(470, 243 + h / 2 + 3, 300, 318, color=POS, sw=2))
    p.append(arrow(550, 243 + h / 2 + 3, 720, 318, color=FIELD, sw=2))

    b, w, h = textbox(280, 360, "спершу замінити \\134 на слеш,\n"
                                "потім \\040 на пробіл",
                      size=12.5, pad=12, fill=RED_FILL, stroke=POS, sw=1.8, rx=8)
    p.append(b)
    b, w, h = textbox(740, 360, "один прохід зліва направо: побачив слеш —\n"
                                "узяв рівно три вісімкові цифри\n"
                                "й пішов далі з наступного символу",
                      size=12.5, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=8)
    p.append(b)

    p += cells(280, 460, ["a", "␣", "b"], stroke=POS, fill=RED_FILL)
    p += cells(740, 460, ["a", "\\", "0", "4", "0", "b"], stroke=FIELD, fill=GREEN_FILL)

    p.append(text(280, 512, "три символи — ім'я зіпсовано", size=12.5, color=POS))
    p.append(text(740, 512, "шість символів — ім'я відновлено", size=12.5, color=FIELD))

    render(os.path.join(IMG, 'mountinfo-unescape.svg'), W, H, *p,
           title="Порядок замін має значення, порядок проходу — ні")


fig_mount_junction()
fig_mount_tree()
fig_propagation()
fig_mountinfo_line()
fig_mount_api_chain()
fig_mountinfo_walk()
fig_mountinfo_unescape()
print("ok")
