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


# ── 1. Довгий рядок проти закріпленої точки відліку ──────────────────────────
def fig_anchor_vs_path():
    W, H = 1180, 700
    p = []

    p.append(fitbox(40, 60, 300, 54, "виклик №1: перевірка", size=15,
                    fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(40, 128, 300, 54, "виклик №2: дія", size=15,
                    fill=BLUE_FILL, stroke=NEG, bold=True))

    # верхній ряд: обхід рядка, два прогони
    xs = [400, 570, 740, 910]
    names = ["var", "spool", "reports", "ana"]
    for i, (x, nm) in enumerate(zip(xs, names)):
        p.append(fitbox(x, 60, 140, 54, nm, size=15, fill=FILL, stroke=LINE))
        if i:
            p.append(arrow(xs[i - 1] + 140, 87, x - 4, 87))
    p.append(arrow(344, 87, 396, 87))

    for i, (x, nm) in enumerate(zip(xs, names)):
        fill = RED_FILL if i == 3 else FILL
        stroke = POS if i == 3 else LINE
        lbl = nm + " → /etc" if i == 3 else nm
        p.append(fitbox(x, 128, 140, 54, lbl, size=15, fill=fill, stroke=stroke))
        if i:
            p.append(arrow(xs[i - 1] + 140, 155, x - 4, 155))
    p.append(arrow(344, 155, 396, 155))

    p.append(fitbox(1064, 60, 96, 54, "той\nкаталог", size=12,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(1064, 128, 96, 54, "інший\nкаталог", size=12,
                    fill=RED_FILL, stroke=POS))
    p.append(arrow(1054, 87, 1060, 87))
    p.append(arrow(1054, 155, 1060, 155))

    p.append(fitbox(400, 220, 760, 62,
                    "між двома прогонами один запис у каталозі переписали —\n"
                    "і той самий рядок закінчився в іншому місці",
                    size=15, fill=RED_FILL, stroke=POS))

    p.append(line(40, 330, 1140, 330, color=MUTED, dash="7 6"))

    # нижній ряд: дескриптор як точка відліку
    p.append(fitbox(40, 396, 300, 54, "виклик з дескриптором", size=15,
                    fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(fitbox(400, 380, 300, 86,
                    "dirfd — уже відкритий каталог\n"
                    "живе в таблиці процесу\n"
                    "ззовні його не переписати",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(344, 423, 396, 423))

    p.append(fitbox(760, 396, 180, 54, "одне ім'я", size=15,
                    fill=FILL, stroke=LINE))
    p.append(arrow(704, 423, 756, 423))

    p.append(fitbox(1000, 396, 160, 54, "потрібний\nоб'єкт", size=13,
                    fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(944, 423, 996, 423))

    p.append(fitbox(400, 512, 760, 62,
                    "переписати можна лише цей один запис —\n"
                    "і саме на нього дивиться O_NOFOLLOW",
                    size=15, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(120, 612, 940, 62,
                    "щілин у виклику стільки, скільки складників ядро проходить за нього:\n"
                    "чотири згори — одна знизу",
                    size=15, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'anchor-vs-path.svg'), W, H, *p,
           title="Той самий рядок і закріплена точка відліку")


# ── 2. Правило читання аргументів усієї родини ───────────────────────────────
def fig_dirfd_rule():
    W, H = 1140, 760
    p = []

    p.append(fitbox(390, 60, 360, 62, "виклик(dirfd, шлях, …, flags)", size=16,
                    fill=BLUE_FILL, stroke=NEG, bold=True))

    p.append(fitbox(390, 168, 360, 56, "шлях починається з «/»?", size=15,
                    fill=WARM_FILL, stroke=WARM))
    p.append(arrow(570, 122, 570, 164))

    p.append(fitbox(40, 268, 300, 84,
                    "так: dirfd ігнорують\nвідлік — корінь процесу",
                    size=14, fill=FILL, stroke=LINE))
    p.append(line(390, 196, 190, 196))
    p.append(arrow(190, 196, 190, 264))

    p.append(fitbox(390, 278, 360, 56, "dirfd == AT_FDCWD?", size=15,
                    fill=WARM_FILL, stroke=WARM))
    p.append(arrow(570, 224, 570, 274))

    p.append(fitbox(40, 420, 300, 84,
                    "так: відлік — поточний\nробочий каталог процесу",
                    size=14, fill=FILL, stroke=LINE))
    p.append(line(390, 306, 190, 306))
    p.append(arrow(190, 306, 190, 416))

    p.append(fitbox(390, 396, 360, 84,
                    "ні: dirfd — відкритий каталог\nвідлік — саме він",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(570, 334, 570, 392))

    p.append(fitbox(800, 268, 300, 84,
                    "dirfd — не дескриптор\nEBADF",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(fitbox(800, 420, 300, 84,
                    "дескриптор є, але це\nне каталог — ENOTDIR",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(arrow(754, 424, 796, 320))
    p.append(arrow(754, 448, 796, 462))

    p.append(fitbox(390, 548, 360, 84,
                    "шлях порожній + AT_EMPTY_PATH:\nдіяти над самим dirfd",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(570, 480, 570, 544))

    p.append(fitbox(150, 676, 840, 62,
                    "одне правило на всю родину: openat, fstatat, unlinkat, renameat,\n"
                    "fchownat, linkat, mkdirat, symlinkat, readlinkat, utimensat, execveat",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'dirfd-rule.svg'), W, H, *p,
           title="Як читається перший аргумент")


# ── 3. Багатоскладниковий шлях проти спуску по одному імені ──────────────────
def fig_walk_down():
    W, H = 1200, 720
    p = []

    p.append(fitbox(60, 62, 480, 58, "один виклик з довгим рядком", size=16,
                    fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(660, 62, 480, 58, "спуск по одному складнику", size=16,
                    fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(60, 152, 480, 58,
                    'openat(d, "logs/2026/out.txt", O_RDONLY)',
                    size=14, fill=FILL, stroke=LINE))

    left_steps = [
        (236, 'ядро шукає "logs" у d', GREEN_FILL, FIELD),
        (316, 'ядро шукає "2026" — поза контролем', RED_FILL, POS),
        (396, 'ядро шукає "out.txt" — поза контролем', RED_FILL, POS),
    ]
    for y, lbl, fill, stroke in left_steps:
        p.append(fitbox(60, y, 480, 58, lbl, size=14, fill=fill, stroke=stroke))
    p.append(arrow(300, 210, 300, 232))
    p.append(arrow(300, 294, 300, 312))
    p.append(arrow(300, 374, 300, 392))

    p.append(fitbox(60, 486, 480, 84,
                    "програма не бачила жодного з трьох кроків:\n"
                    "підміна середнього складника проходить непоміченою",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(arrow(300, 454, 300, 482))

    right_steps = [
        (152, 'openat(d, "logs", O_DIRECTORY|O_NOFOLLOW)'),
        (236, 'openat(d1, "2026", O_DIRECTORY|O_NOFOLLOW)'),
        (316, 'openat(d2, "out.txt", O_RDONLY|O_NOFOLLOW)'),
    ]
    for y, lbl in right_steps:
        p.append(fitbox(660, y, 480, 58, lbl, size=13, fill=FILL, stroke=LINE))
    p.append(arrow(900, 210, 900, 232))
    p.append(arrow(900, 294, 900, 312))

    p.append(fitbox(660, 396, 480, 84,
                    "після кожного кроку — або дескриптор,\n"
                    "або ELOOP (посилання) чи ENOTDIR (не каталог)",
                    size=14, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(900, 374, 900, 392))

    p.append(fitbox(660, 508, 480, 62,
                    "рішення «йти далі» ухвалює програма,\n"
                    "і воно ухвалюється тричі",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(900, 480, 900, 504))

    p.append(fitbox(140, 632, 920, 62,
                    "O_NOFOLLOW стосується лише ОСТАННЬОГО складника — тому в довгому рядку від нього\n"
                    "мало користі, а в однокомпонентному він накриває весь шлях",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'walk-down.svg'), W, H, *p,
           title="Чому дескриптор сам по собі ще не гарантія")


# ── 4. Дороги назовні й прапорці resolve, що їх перекривають ─────────────────
def fig_resolve_flags():
    W, H = 1160, 760
    p = []

    p.append(fitbox(430, 60, 300, 78,
                    "каталог-якір (dirfd)\nвідлік розбору шляху",
                    size=15, fill=GREEN_FILL, stroke=FIELD, bold=True))

    ways = [
        (40, '"/etc/passwd"\nабсолютний шлях\nігнорує якір', "RESOLVE_BENEATH\nRESOLVE_IN_ROOT"),
        (330, '"../../etc"\nдві крапки виводять\nугору з піддерева', "RESOLVE_BENEATH\nRESOLVE_IN_ROOT"),
        (620, 'посилання вбік\nу будь-якому\nскладнику', "RESOLVE_NO_SYMLINKS"),
        (910, 'точка монтування\nусередині\nпіддерева', "RESOLVE_NO_XDEV"),
    ]
    for x, way, flag in ways:
        p.append(fitbox(x, 210, 210, 108, way, size=13, fill=RED_FILL, stroke=POS))
        p.append(fitbox(x, 390, 210, 92, flag, size=12, fill=BLUE_FILL, stroke=NEG))
        p.append(arrow(x + 105, 322, x + 105, 386))

    p.append(arrow(500, 142, 180, 204))
    p.append(arrow(540, 142, 450, 204))
    p.append(arrow(620, 142, 710, 204))
    p.append(arrow(660, 142, 980, 204))

    p.append(fitbox(180, 540, 800, 92,
                    "перевіряє сам обхід усередині ядра, а не код поруч із ним:\n"
                    "правило діє на КОЖНОМУ складнику, і обійти його рядком не вийде",
                    size=15, fill=GREEN_FILL, stroke=FIELD))
    for x in (145, 435, 725, 1015):
        p.append(arrow(x, 486, x, 536))

    p.append(fitbox(180, 672, 800, 62,
                    "невідомий або суперечливий біт — це EINVAL, а не мовчазне ігнорування:\n"
                    "програма дізнається про брак захисту від ядра, а не від зловмисника",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'resolve-flags.svg'), W, H, *p,
           title="openat2: чотири дороги назовні й чим їх закривають")


# ── 5. Три приходи родини *at (для історичної вставки) ───────────────────────
def fig_at_timeline():
    W, H = 1180, 1130
    p = []

    X_AXIS = 250          # вертикальна вісь часу
    X_BOX = 300           # ліва межа карток подій
    W_BOX = 840

    rows = [
        ("act", "ДІЯ ПЕРША — двері у простір розширених атрибутів", WARM_FILL, WARM),
        ("2002", "Solaris 9: openat з прапорцем O_XATTR і обгортка attropen.\n"
                 "Дескриптор каталогу тут — точка входу в атрибути, не захист від гонки",
         WARM_FILL, WARM),
        ("act", "ДІЯ ДРУГА — той самий важіль, але вже проти гонок", BLUE_FILL, NEG),
        ("2005", "Solaris 10: повний набір — fstatat, unlinkat, renameat,\n"
                 "fchownat, futimesat і решта; мотив названо прямо: гонка",
         BLUE_FILL, NEG),
        ("2006", "березень: Linux 2.6.16 і glibc 2.4 — справжні виклики ядра\n"
                 "замість колишніх обхідних трюків у бібліотеці",
         BLUE_FILL, NEG),
        ("2008", "POSIX.1-2008 (IEEE Std 1003.1-2008): набір стає обов'язковим",
         GREEN_FILL, FIELD),
        ("2008–15", "BSD підхоплюють: DragonFly і FreeBSD 2008–09 (openat — FreeBSD 8.0),\n"
                    "OpenBSD 2011, NetBSD і macOS — середина 2010-х",
         GREEN_FILL, FIELD),
        ("act", "ДІЯ ТРЕТЯ — якоря замало, і атрибути повертаються", RED_FILL, POS),
        ("2020", "Linux 5.6: openat2 (Алекса Сараї, SUSE) — прапорці RESOLVE_*,\n"
                 "бо «..», абсолютні шляхи, посилання й монтування лишалися відчиненими",
         RED_FILL, POS),
        ("2021", "5.11 — заборонено пару RESOLVE_BENEATH|RESOLVE_IN_ROOT;\n"
                 "5.12 — додано RESOLVE_CACHED; перший споживач у просторі користувача — LXC",
         RED_FILL, POS),
        ("2025", "січень, Linux 6.13: setxattrat, getxattrat, listxattrat, removexattrat —\n"
                 "мотив знову атрибути: геть обхід через /proc/self/fd",
         WARM_FILL, WARM),
    ]

    y = 50
    dots = []
    for kind, txt, fill, stroke in rows:
        if kind == "act":
            p.append(fitbox(X_BOX - 250, y, W_BOX + 250, 46, txt, size=17,
                            fill=fill, stroke=stroke, bold=True))
            y += 46 + 22
            continue
        h = 66
        p.append(fitbox(X_BOX, y, W_BOX, h, txt, size=15, fill=fill, stroke=stroke))
        cy = y + h / 2
        p.append(text(X_AXIS - 42, cy + 6, kind, size=17, bold=True, anchor="end"))
        dots.append((cy, stroke))
        y += h + 20

    y_top, y_bot = dots[0][0], dots[-1][0]
    p.insert(0, line(X_AXIS, y_top - 30, X_AXIS, y_bot + 30, color=LINE, sw=2))
    for cy, stroke in dots:
        p.append(circle(X_AXIS, cy, 8, fill="#ffffff", stroke=stroke, sw=2.5))
        p.append(line(X_AXIS + 9, cy, X_BOX - 4, cy, color=LINE, sw=1.2, dash="4 4"))

    render(os.path.join(IMG, 'at-timeline.svg'), W, H, *p,
           title="Три приходи родини *at: атрибути → гонки → знову атрибути")


# ── 6. Простір бітів AT_* і зіткнення на 0x200 (для api-довідки) ─────────────
def fig_at_bits():
    W, H = 1240, 700
    p = []

    p.append(fitbox(130, 40, 980, 50,
                    "усі прапорці AT_* живуть в одному цілому аргументі flags",
                    size=16, fill=BLUE_FILL, stroke=NEG, bold=True))

    cols = [
        ("0x100", "AT_SYMLINK_\nNOFOLLOW", FILL, LINE),
        ("0x200", "AT_EACCESS\nAT_REMOVEDIR\nAT_HANDLE_FID", RED_FILL, POS),
        ("0x400", "AT_SYMLINK_\nFOLLOW", FILL, LINE),
        ("0x800", "AT_NO_\nAUTOMOUNT", FILL, LINE),
        ("0x1000", "AT_EMPTY_\nPATH", FILL, LINE),
        ("0x2000\n0x4000", "AT_STATX_*\nодне двобітове\nполе", WARM_FILL, WARM),
        ("0x8000", "AT_RECURSIVE\nродина монту-\nвання, не ця", FILL, MUTED),
    ]

    x0, w, gap = 40, 156, 12
    centers = []
    for i, (val, nm, fill, stroke) in enumerate(cols):
        x = x0 + i * (w + gap)
        centers.append(x + w / 2)
        p.append(fitbox(x, 126, w, 60, val, size=15,
                        fill=fill, stroke=stroke, bold=True))
        p.append(fitbox(x, 200, w, 116, nm, size=12, fill=fill, stroke=stroke))

    p.append(fitbox(40, 396, 540, 122,
                    "той самий біт 0x200 читається за іменем виклику:\n"
                    "faccessat — брати чинні (effective) UID і GID\n"
                    "unlinkat — знімати каталог, а не файл\n"
                    "name_to_handle_at — ідентифікатор лише для порівняння",
                    size=13, fill=RED_FILL, stroke=POS))
    p.append(arrow(centers[1], 320, 300, 392))

    p.append(fitbox(660, 396, 540, 122,
                    "0x2000 і 0x4000 — не два незалежні прапорці,\n"
                    "а двобітове поле AT_STATX_SYNC_TYPE:\n"
                    "рівно одне зі значень за раз,\n"
                    "обидва біти разом — EINVAL",
                    size=13, fill=WARM_FILL, stroke=WARM))
    p.append(arrow(centers[5], 320, 930, 392))

    p.append(fitbox(140, 580, 960, 84,
                    "кожен виклик приймає свою підмножину бітів, а не весь набір:\n"
                    "зайвий біт — це EINVAL, тож «прапорець існує» й «цей виклик його бере» —\n"
                    "різні запитання",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'at-bits.svg'), W, H, *p,
           title="Простір бітів AT_*: одне число на всю родину")


if __name__ == "__main__":
    fig_anchor_vs_path()
    fig_dirfd_rule()
    fig_walk_down()
    fig_resolve_flags()
    fig_at_timeline()
    fig_at_bits()
    print("ok")
