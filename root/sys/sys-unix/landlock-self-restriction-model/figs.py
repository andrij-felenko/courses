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
GREY_FILL = "#eeeeee"


# ── 1. Домен як стос шарів ──────────────────────────────────────────────────
def fig_layers():
    W, H = 1420, 900
    p = []

    p.append(text(360, 70, "життя процесу", size=17, bold=True, color=MUTED))

    steps = [
        ("процес стартує", "домен порожній", GREY_FILL, MUTED),
        ("landlock_restrict_self(A)", "домен = шар A", BLUE_FILL, NEG),
        ("fork() → нащадок", "домен = шар A", BLUE_FILL, NEG),
        ("execve() → інша програма", "домен = шар A", BLUE_FILL, NEG),
        ("landlock_restrict_self(B)", "домен = шар A і шар B", GREEN_FILL, FIELD),
    ]
    y = 110
    for i, (act, dom, fill, stroke) in enumerate(steps):
        p.append(fitbox(60, y, 350, 78, act, size=15, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(430, y, 260, 78, dom, size=14, fill=BG, stroke=MUTED))
        if i < len(steps) - 1:
            p.append(arrow(235, y + 78, 235, y + 132))
        y += 132

    p.append(fitbox(60, 770, 630, 76,
                    "жодного виклику, що знімає шар, не існує —\n"
                    "домен тільки росте, і росте не більше ніж до 16 шарів",
                    size=14, fill=WARM_FILL, stroke=WARM))

    # ── права колонка: як судять одну спробу ──
    p.append(text(1060, 70, "як судять одну спробу", size=17, bold=True, color=MUTED))

    p.append(fitbox(770, 110, 580, 78,
                    "відкрити /etc/passwd на читання", size=16, bold=True,
                    fill=FILL, stroke=LINE))
    p.append(arrow(1060, 188, 1060, 242))

    p.append(fitbox(770, 242, 580, 100,
                    "шар A: обробляє READ_FILE,\n"
                    "правило на /etc дає READ_FILE → «так»",
                    size=14, fill=GREEN_FILL, stroke=FIELD))
    p.append(arrow(1060, 342, 1060, 396))

    p.append(fitbox(770, 396, 580, 100,
                    "шар B: обробляє READ_FILE,\n"
                    "жодне його правило /etc не накриває → «ні»",
                    size=14, fill=RED_FILL, stroke=POS))
    p.append(arrow(1060, 496, 1060, 550))

    p.append(fitbox(770, 550, 580, 78, "open() повертає EACCES",
                    size=16, bold=True, fill=RED_FILL, stroke=POS))

    p.append(fitbox(770, 664, 580, 182,
                    "правило зведення шарів:\n"
                    "дозволено ⟺ дозволили ВСІ шари\n"
                    " \n"
                    "шар, який цього права не обробляє,\n"
                    "у голосуванні не бере участі —\n"
                    "він про нього нічого не оголошував",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'layers.svg'), W, H, *p)


# ── 2. Правило висить на об'єкті, а не на рядку ─────────────────────────────
def fig_rule_on_object():
    W, H = 1460, 880
    p = []

    p.append(text(400, 62, "дерево каталогів і правила на ньому", size=17, bold=True, color=MUTED))

    # дерево
    nodes = [
        (60, 100, 300, 62, "/", GREY_FILL, MUTED, ""),
        (140, 200, 300, 62, "home", GREY_FILL, MUTED, ""),
        (220, 300, 300, 62, "user", GREY_FILL, MUTED, ""),
        (300, 400, 300, 62, ".ssh", GREY_FILL, MUTED, ""),
        (300, 500, 300, 62, "proj", GREEN_FILL, FIELD, "правило"),
        (380, 600, 300, 62, "src", GREY_FILL, MUTED, ""),
        (460, 700, 300, 62, "main.c", GREY_FILL, MUTED, ""),
    ]
    for x, y, w, h, nm, fill, stroke, tag in nodes:
        p.append(fitbox(x, y, w, h, nm, size=16, bold=True, fill=fill, stroke=stroke))
        if tag:
            p.append(fitbox(x + 320, y, 200, 62, tag, size=14, bold=True,
                            fill=GREEN_FILL, stroke=FIELD, color=FIELD))

    # ребра дерева (від низу батька до лівого краю дитини)
    edges = [(60, 162, 140, 200), (140, 262, 220, 300), (220, 362, 300, 400),
             (220, 362, 300, 500), (300, 562, 380, 600), (380, 662, 460, 700)]
    for x1, y1, x2, y2 in edges:
        p.append(line(x1 + 30, y1, x1 + 30, y2 + 31, color=MUTED))
        p.append(line(x1 + 30, y2 + 31, x2, y2 + 31, color=MUTED))

    p.append(fitbox(60, 790, 700, 62,
                    "правило дали, відкривши каталог proj і передавши його дескриптор",
                    size=14, fill=FILL, stroke=LINE))

    # ── правий стовпець ──
    p.append(text(1110, 62, "як це працює на перевірці", size=17, bold=True, color=MUTED))

    p.append(fitbox(820, 100, 580, 130,
                    "обхід іде від файла ВГОРУ:\n"
                    "main.c — правила нема, src — нема,\n"
                    "proj — є і дає READ_FILE → дозволено",
                    size=14, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(820, 264, 580, 152,
                    "правило прив'язане до самого об'єкта,\n"
                    "а не до рядка «/home/user/proj»:\n"
                    "інший шлях, що веде в той самий каталог —\n"
                    "жорстке посилання, символьне, друге\n"
                    "монтування — дає рівно ті самі права",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(820, 450, 580, 178,
                    "пастка: правила бувають ЛИШЕ дозвільні\n"
                    " \n"
                    "дали правило на home — і «заборонити»\n"
                    "нижче .ssh уже нічим: обхід угору дійде\n"
                    "до home, знайде дозвіл і на тому спиниться",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(fitbox(820, 662, 580, 190,
                    "звідси спосіб користування:\n"
                    "перелічують те, що ДОЗВОЛЕНО,\n"
                    "і перелічують якнайглибше —\n"
                    "правило на proj замість правила на home,\n"
                    "бо виняток із дозволу вирізати нічим",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'rule-on-object.svg'), W, H, *p)


# ── 3. Три стани права й узгодження версії ABI ──────────────────────────────
def fig_handled_and_abi():
    W, H = 1480, 820
    p = []

    p.append(text(430, 62, "три стани одного права доступу", size=17, bold=True, color=MUTED))

    rows = [
        ("оголошене в handled_access_fs,\nі якесь правило його дає",
         "дозволене там, куди дістає правило,\nі заборонене всюди інде", GREEN_FILL, FIELD),
        ("оголошене в handled_access_fs,\nале правил на нього нема",
         "заборонене скрізь без винятку", RED_FILL, POS),
        ("не оголошене в handled_access_fs",
         "Landlock його не судить узагалі —\nлишаються самі класичні права", GREY_FILL, MUTED),
    ]
    y = 110
    for left, right, fill, stroke in rows:
        p.append(fitbox(60, y, 400, 150, left, size=14, bold=True, fill=fill, stroke=stroke))
        p.append(arrow(470, y + 75, 530, y + 75))
        p.append(fitbox(540, y, 380, 150, right, size=14, fill=BG, stroke=stroke))
        y += 190

    p.append(fitbox(60, 690, 860, 96,
                    "оголосити право — це взяти за нього відповідальність:\n"
                    "усе оголошене типово заборонене, і лише правила щось повертають",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))

    # ── права колонка: сходинки узгодження ──
    p.append(text(1200, 62, "узгодження з ядром, яке трапилося", size=17, bold=True, color=MUTED))

    p.append(fitbox(990, 110, 420, 100,
                    "abi = landlock_create_ruleset(\n  NULL, 0, ...VERSION)",
                    size=14, bold=True, fill=FILL, stroke=LINE))
    p.append(arrow(1200, 210, 1200, 254))

    ladder = [
        ("abi < 1", "Landlock нема або вимкнено", GREY_FILL, MUTED),
        ("abi < 2", "прибрати REFER із набору", WARM_FILL, WARM),
        ("abi < 3", "прибрати TRUNCATE", WARM_FILL, WARM),
        ("abi < 5", "прибрати IOCTL_DEV", WARM_FILL, WARM),
    ]
    y = 254
    for cond, act, fill, stroke in ladder:
        p.append(fitbox(990, y, 150, 80, cond, size=14, bold=True, fill=BG, stroke=stroke))
        p.append(fitbox(1155, y, 255, 80, act, size=13, fill=fill, stroke=stroke))
        y += 100

    p.append(fitbox(990, 664, 420, 122,
                    "без цих сходинок старе ядро\n"
                    "поверне EINVAL на невідоме право —\n"
                    "і пісочниці не буде взагалі жодної",
                    size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'handled-and-abi.svg'), W, H, *p)


# ── 4. Що насправді відкриває один execvp ───────────────────────────────────
def fig_exec_chain():
    W, H = 1500, 840
    p = []

    p.append(text(310, 62, "що відкриває один execvp(\"cat\", …)",
                  size=17, bold=True, color=MUTED))

    chain = [
        ("оболонка знайшла cat по PATH\nі покликала execvp", "—", GREY_FILL, MUTED),
        ("ядро відкриває /usr/bin/cat",
         "EXECUTE\n+ READ_FILE", BLUE_FILL, NEG),
        ("у ELF записаний інтерпретатор —\nядро відкриває і /lib64/ld-linux…",
         "EXECUTE\n+ READ_FILE", BLUE_FILL, NEG),
        ("ld.so відкриває /etc/ld.so.cache",
         "READ_FILE\n(є запасний шлях)", GREY_FILL, MUTED),
        ("ld.so відкриває libc.so.6\nу /usr/lib",
         "READ_FILE", GREEN_FILL, FIELD),
        ("аж тепер починається main()", "—", GREY_FILL, MUTED),
    ]
    y = 106
    for i, (act, need, fill, stroke) in enumerate(chain):
        p.append(fitbox(60, y, 430, 84, act, size=14, bold=True, fill=fill, stroke=stroke))
        p.append(fitbox(520, y, 220, 84, need, size=13, fill=BG, stroke=stroke))
        if i < len(chain) - 1:
            p.append(arrow(275, y + 84, 275, y + 122))
        y += 122

    # ── права колонка: чим це обертається ──
    p.append(text(1120, 62, "чим обертається забутий каталог",
                  size=17, bold=True, color=MUTED))

    p.append(fitbox(800, 106, 640, 152,
                    "нема правила на /lib64:\n"
                    "execve падає ще ДО першого рядка програми —\n"
                    "«cannot execute: Permission denied»,\n"
                    "бо інтерпретатора не вдалося відкрити",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(fitbox(800, 290, 640, 152,
                    "нема правила на /usr/lib:\n"
                    "програма таки стартує й гине пізніше —\n"
                    "«libc.so.6: cannot open shared object file:\n"
                    "Permission denied», код виходу 127",
                    size=14, fill=RED_FILL, stroke=POS))

    p.append(fitbox(800, 474, 640, 170,
                    "бібліотеки відкривають ЗВИЧАЙНИМ читанням,\n"
                    "тож їм досить READ_FILE\n"
                    " \n"
                    "EXECUTE потрібне лише там, звідки запускає\n"
                    "саме ядро: програма та її інтерпретатор",
                    size=14, fill=BLUE_FILL, stroke=NEG))

    p.append(fitbox(800, 676, 640, 128,
                    "діагностика:\n"
                    "strace -f -e trace=openat ./sandbox …\n"
                    "показує рівно те відкриття, що впало",
                    size=14, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'exec-chain.svg'), W, H, *p)


fig_layers()
fig_rule_on_object()
fig_handled_and_abi()
fig_exec_chain()
print("ok")


# ── 4. Як мінявся задум: від eBPF до власних викликів ───────────────────────
def fig_design_turn():
    W, H = 1360, 900
    p = []

    rows = [
        ("v1", "березень 2016",
         "гачки LSM плюс програми eBPF: правило — програма,\n"
         "яку ядро питає перед доступом", GREY_FILL, MUTED),
        ("v2", "серпень 2016",
         "додано прив'язку до cgroups: політика накривала\n"
         "цілу групу процесів, а не лише того, хто просив", GREY_FILL, MUTED),
        ("v8", "лютий 2018",
         "спроба навчити правила говорити про шляхи файлів,\n"
         "а не лише про окремі відкриті об'єкти", GREY_FILL, MUTED),
        ("v10", "липень 2019",
         "набір латок різко скорочують, щоб рецензентам\n"
         "було що дочитати до кінця", GREY_FILL, MUTED),
        ("v14", "лютий 2020",
         "ПОВОРОТ: eBPF прибрано зовсім; натомість набори правил\n"
         "на дескрипторах і один власний системний виклик", WARM_FILL, WARM),
        ("v21", "жовтень 2020",
         "єдиний виклик-мультиплексор розбито\n"
         "на три окремі системні виклики", BLUE_FILL, NEG),
        ("v34", "квітень 2021",
         "прийнято в основне дерево; вийшло з ядром 5.13\n"
         "у червні 2021 року", GREEN_FILL, FIELD),
    ]

    top, pitch, rh = 80, 112, 96
    for i, (ver, when, what, fill, stroke) in enumerate(rows):
        y = top + i * pitch
        p.append(fitbox(320, y, 180, rh, ver + "\n" + when, size=15, bold=True,
                        fill=BG, stroke=stroke))
        p.append(fitbox(524, y, 796, rh, what, size=14, fill=fill, stroke=stroke))

    p.append(fitbox(40, top, 250, 4 * pitch - (pitch - rh),
                    "доба eBPF\n\nправило пишуть як програму\nдля перевіряльника ядра",
                    size=15, bold=True, fill=GREY_FILL, stroke=MUTED))
    p.append(fitbox(40, top + 4 * pitch, 250, rh,
                    "рік перегляду задуму", size=15, bold=True,
                    fill=WARM_FILL, stroke=WARM))
    p.append(fitbox(40, top + 5 * pitch, 250, 2 * pitch - (pitch - rh),
                    "доба власних викликів\n\nправило — запис у наборі,\nякий ядро розуміє саме",
                    size=15, bold=True, fill=BLUE_FILL, stroke=NEG))

    render(os.path.join(IMG, 'design-turn.svg'), W, H, *p)


fig_design_turn()
