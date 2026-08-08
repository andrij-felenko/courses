# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARM   = "#fdecea"
COOL   = "#eaf0fd"
GREENF = "#eafaf0"
PALE   = "#f4f6f8"


# ── 1. Простір ядра: де адреса — арифметика, а де — запис у таблиці ──────────
def fig_kernel_map():
    W, H = 1320, 780
    p = []

    p.append(fitbox(60, 40, 1200, 56,
                    "ВЕРХНЯ ПОЛОВИНА АДРЕС — простір ядра (x86-64, чотири рівні таблиць)",
                    size=16, fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))

    rows = [
        ("ffff888000000000",
         "пряме відображення\nвсієї фізичної пам'яті", "64 ТіБ",
         "адреса = фізична + стала\nсуцільні адреси ⇒ суцільні кадри",
         NEG, COOL),
        ("ffffc90000000000",
         "область vmalloc\nта ioremap", "32 ТіБ",
         "у кожної сторінки власний запис у таблиці\nсуцільні адреси ⇒ кадри будь-де",
         FIELD, GREENF),
        ("ffffea0000000000",
         "карта описів кадрів\n(vmemmap)", "1 ТіБ",
         "по одній структурі на кожен кадр пам'яті",
         MUTED, PALE),
        ("ffffffff80000000",
         "код і дані\nсамого ядра", "512 МіБ",
         "кладеться при завантаженні й далі не рухається",
         MUTED, PALE),
        ("ffffffffa0000000",
         "область завантажених\nмодулів", "1520 МіБ",
         "код модуля близько до коду ядра —\nщоб виклики влазили в короткий стрибок",
         MUTED, PALE),
    ]

    y = 128
    for addr, name, size, rule, accent, fillc in rows:
        p.append(fitbox(60, y, 250, 96, addr, size=13,
                        fill=SOFT, stroke=accent, sw=1.4, color=accent, bold=True))
        p.append(fitbox(326, y, 300, 96, name, size=14,
                        fill=fillc, stroke=accent, sw=1.8, color=INK, bold=True))
        p.append(fitbox(642, y, 140, 96, size, size=15,
                        fill=SOFT, stroke=accent, sw=1.4, color=accent, bold=True))
        p.append(fitbox(798, y, 462, 96, rule, size=13,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        y += 112

    p.append(fitbox(60, 692, 1200, 62,
                    "стала різниця тримається лише в першому рядку — саме вона й робить там\n"
                    "суцільність адрес рівнозначною суцільності кадрів",
                    size=14, fill=WARM, stroke=POS, sw=1.6, color=INK))

    render(os.path.join(OUT, "kernel-address-map.svg"), W, H, *p)


# ── 2. Ті самі кадри, два різні набори адрес ─────────────────────────────────
def fig_two_paths():
    W, H = 1400, 840
    p = []

    p.append(fitbox(70, 34, 1260, 50,
                    "ЧОТИРИ КАДРИ, РОЗКИДАНІ ПО ПАМ'ЯТІ, — І ДВА СПОСОБИ ДО НИХ ЗВЕРНУТИСЯ",
                    size=16, fill=PALE, stroke=INK, sw=1.6, color=INK, bold=True))

    frames = list(range(12, 24))
    ours = {13: 0, 16: 1, 20: 2, 22: 3}
    x0, cw, gap = 84, 100, 6

    def fx(i):
        return x0 + i * (cw + gap)

    # адреси прямого відображення — рівно над своїми кадрами
    p.append(text(700, 118, "адреси прямого відображення: кожна над своїм кадром, бо різниця стала",
                  size=13, color=NEG))
    for i, k in enumerate(frames):
        mine = k in ours
        p.append(fitbox(fx(i), 132, cw, 62, "…%X000" % (k,), size=12,
                        fill=(COOL if mine else "#ffffff"),
                        stroke=(NEG if mine else MUTED), sw=(2.0 if mine else 1.0),
                        color=(NEG if mine else MUTED), bold=mine))

    # фізичні кадри
    p.append(text(700, 246, "фізична пам'ять машини: наші чотири кадри стоять там, де знайшлися",
                  size=13, color=INK))
    for i, k in enumerate(frames):
        mine = k in ours
        p.append(fitbox(fx(i), 260, cw, 78,
                        ("кадр %d" % k) if mine else str(k), size=12,
                        fill=(WARM if mine else PALE),
                        stroke=(POS if mine else MUTED), sw=(2.0 if mine else 1.0),
                        color=(POS if mine else MUTED), bold=mine))

    # адреси vmalloc — суцільні
    vx0, vw, vgap = 320, 150, 8
    for j in range(4):
        x = vx0 + j * (vw + vgap)
        p.append(fitbox(x, 566, vw, 82, "vm + %d КіБ" % (j * 4), size=13,
                        fill=GREENF, stroke=FIELD, sw=2.0, color=FIELD, bold=True))
    gx = vx0 + 4 * (vw + vgap)
    p.append(fitbox(gx, 566, vw, 82, "сторожова\nсторінка", size=12,
                    fill="#ffffff", stroke=POS, sw=2.0, color=POS, bold=True))

    # зшивання: стрілки вгору, у свій кадр
    for k, j in ours.items():
        i = frames.index(k)
        p.append(arrow(vx0 + j * (vw + vgap) + vw / 2, 562,
                       fx(i) + cw / 2, 344, color=FIELD, sw=1.8))

    p.append(text(700, 700, "адреси vmalloc: чотири сторінки поспіль, зшиті записами таблиць ядра",
                  size=13, color=FIELD))

    p.append(fitbox(70, 726, 1260, 82,
                    "той самий кадр видно за двома різними адресами одночасно;\n"
                    "від адреси vmalloc фізичну не порахувати відніманням — її треба спитати в таблиці",
                    size=14, fill=SOFT, stroke=INK, sw=1.5, color=INK))

    render(os.path.join(OUT, "two-paths.svg"), W, H, *p)


# ── 3. Чому звільнення відкладають ──────────────────────────────────────────
def fig_lazy_purge():
    W, H = 1360, 820
    p = []

    p.append(fitbox(70, 34, 560, 54, "ЯКБИ ЧИСТИЛИ ОДРАЗУ", size=15,
                    fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))
    p.append(fitbox(730, 34, 560, 54, "ЯК РОБИТЬ ЯДРО", size=15,
                    fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    names = ["звільнили A", "звільнили B", "звільнили C"]

    # ліва колонка
    for j, nm in enumerate(names):
        x = 70 + j * 190
        p.append(fitbox(x, 116, 170, 52, nm, size=13,
                        fill=PALE, stroke=MUTED, sw=1.4, color=INK))
        p.append(arrow(x + 85, 172, x + 85, 208, color=POS, sw=1.6))
        p.append(fitbox(x, 212, 170, 86, "переривання\nна всі ядра\nі чекати", size=12,
                        fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))

    p.append(fitbox(70, 336, 560, 66,
                    "три зупинки всієї машини на три звільнення", size=14,
                    fill=SOFT, stroke=POS, sw=1.5, color=INK))
    p.append(fitbox(70, 430, 560, 88,
                    "а звільнень у ядрі — тисячі за секунду,\n"
                    "і кожна зупинка тим довша, чим більше ядер",
                    size=13, fill=SOFT, stroke=MUTED, sw=1.2, color=MUTED))

    # права колонка
    for j, nm in enumerate(names):
        x = 730 + j * 190
        p.append(fitbox(x, 116, 170, 52, nm, size=13,
                        fill=PALE, stroke=MUTED, sw=1.4, color=INK))
        p.append(arrow(x + 85, 172, 1010, 208, color=FIELD, sw=1.6))

    p.append(fitbox(730, 212, 560, 74,
                    "у список відкладених: записи ще стоять,\nадреси нікому не віддають",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.8, color=INK))
    p.append(arrow(1010, 290, 1010, 322, color=FIELD, sw=1.6))
    p.append(fitbox(730, 326, 560, 62,
                    "відкладених сторінок стало більше за поріг",
                    size=13, fill=SOFT, stroke=FIELD, sw=1.4, color=INK))
    p.append(arrow(1010, 392, 1010, 424, color=FIELD, sw=1.6))
    p.append(fitbox(730, 428, 560, 90,
                    "ОДНЕ переривання на всі ядра —\nразом на весь накопичений діапазон",
                    size=14, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))
    p.append(arrow(1010, 522, 1010, 554, color=FIELD, sw=1.6))
    p.append(fitbox(730, 558, 560, 62,
                    "аж тепер адреси повертаються у вільне дерево",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    p.append(fitbox(70, 664, 1220, 92,
                    "звідси видима дивина: після звільнення область vmalloc ще якийсь час\n"
                    "виглядає зайнятою, а пам'ять не повертається в лічильники —\n"
                    "чекає, поки набереться на одну спільну розсилку",
                    size=14, fill=SOFT, stroke=INK, sw=1.5, color=INK))

    render(os.path.join(OUT, "lazy-purge.svg"), W, H, *p)


# ── 4. Три стіни, у які впиралася область ───────────────────────────────────
def fig_three_walls():
    W, H = 1420, 900
    p = []

    p.append(fitbox(60, 34, 1300, 54,
                    "ЧОТИРИ ПОВОРОТИ В ІСТОРІЇ ОБЛАСТІ — І ЩОРАЗУ ІНША НЕСТАЧА",
                    size=16, fill=PALE, stroke=INK, sw=1.6, color=INK, bold=True))

    cols = [(60, 150), (226, 300), (542, 420), (978, 382)]
    heads = ["КОЛИ", "У ЩО ВПЕРЛОСЯ", "ЩО ЗРОБИЛИ", "ЧИМ ЗАПЛАТИЛИ"]
    for (x, w), h in zip(cols, heads):
        p.append(fitbox(x, 108, w, 48, h, size=13,
                        fill=COOL, stroke=NEG, sw=1.4, color=NEG, bold=True))

    rows = [
        ("2008\nядро 2.6.28",
         "кожен vunmap — широкомовне\nпереривання на всі ядра,\nі все це під одним глобальним\nзамком на запис",
         "дерево зайнятих ділянок,\nвідкладена спільна очистка,\nзапас адрес на кожному ядрі\nдля дрібних відображень",
         "звільнена адреса\nповертається не одразу",
         POS, WARM),
        ("2019\nядро 5.2",
         "пошук вільного місця —\nпрохід списком зайнятих\nділянок від початку області",
         "окреме дерево вільних\nпроміжків: у кожному вузлі\nнайбільший вільний розмір\nу його піддереві",
         "друга структура, яку треба\nтримати в злагоді з першою",
         FIELD, GREENF),
        ("2021\nядро 5.13",
         "виділення вже дешеве,\nа кожне звернення платить:\nодна сторінка — один запис\nу TLB",
         "виділення від розміру великої\nсторінки пробує лягти нею\nй відкочується на звичайні",
         "там, де сторінкам потрібні\nрізні права, вимкнено",
         NEG, COOL),
        ("32 біти\nдо кінця епохи",
         "адрес просто мало:\nтипово 128 МіБ на всю\nобласть у цілій системі",
         "параметр завантаження\nvmalloc= розширює область",
         "рівно стільки ж віднімається\nв прямого відображення",
         MUTED, PALE),
    ]

    y = 170
    for when, wall, fix, cost, accent, fillc in rows:
        p.append(fitbox(cols[0][0], y, cols[0][1], 128, when, size=13,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(fitbox(cols[1][0], y, cols[1][1], 128, wall, size=12,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        p.append(fitbox(cols[2][0], y, cols[2][1], 128, fix, size=12,
                        fill=SOFT, stroke=accent, sw=1.5, color=INK))
        p.append(fitbox(cols[3][0], y, cols[3][1], 128, cost, size=12,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=MUTED))
        y += 144

    p.append(fitbox(60, 752, 1300, 110,
                    "перші два переписування прибирали час, що з'їдало саме керування областю;\n"
                    "третє прибирало час, який область відбирала в усього іншого коду через TLB;\n"
                    "а четвертий рядок алгоритмічної відповіді не мав узагалі — адрес не додати кмітливістю",
                    size=14, fill=SOFT, stroke=INK, sw=1.5, color=INK))

    render(os.path.join(OUT, "three-walls.svg"), W, H, *p)


# ── 5. Анатомія рядка /proc/vmallocinfo ─────────────────────────────────────
def fig_vmallocinfo_line():
    W, H = 1420, 1060
    p = []

    p.append(fitbox(60, 34, 1300, 50,
                    "ОДИН РЯДОК /proc/vmallocinfo — І ЩО З КОЖНОГО ПОЛЯ МОЖНА ВЗЯТИ",
                    size=16, fill=PALE, stroke=INK, sw=1.6, color=INK, bold=True))

    p.append(fitbox(60, 100, 1300, 56,
                    "0xffffc90019a00000-0xffffc9001a201000  8392704 "
                    "acme_ring_grow+0x8f/0x1e0 [acme_capture] pages=2048 vmalloc N0=2048",
                    size=14, fill=SOFT, stroke=NEG, sw=1.6, color=NEG))

    heads = [(60, 300, "ПОЛЕ"), (376, 330, "ЩО ЦЕ"), (722, 638, "ЩО З НИМ РОБИТИ")]
    for x, w, h in heads:
        p.append(fitbox(x, 172, w, 42, h, size=13,
                        fill=COOL, stroke=NEG, sw=1.4, color=NEG, bold=True))

    rows = [
        ("0xffffc90019a00000-\n0xffffc9001a201000",
         "початок і кінець\nадресного сліду",
         "друкуються через %pK — при kptr_restrict замість них нулі;\n"
         "тільки на них тримається пошук вільних проміжків",
         NEG, COOL),
        ("8392704",
         "той самий слід\nу байтах",
         "звичайне число, не %pK — підсумки за викликачами\n"
         "переживають затирання адрес і рахуються завжди",
         FIELD, GREENF),
        ("acme_ring_grow+0x8f/0x1e0",
         "хто просив: символ,\nзміщення, розмір функції",
         "при групуванні зміщення прибираємо — інакше кожна точка\n"
         "виклику стане окремим власником і жоден рядок не набере ваги",
         POS, WARM),
        ("[acme_capture]",
         "модуль, з якого\nвикликали",
         "буває не завжди; коли є — найкоротший шлях до винного",
         POS, WARM),
        ("pages=2048",
         "кадрів під даними",
         "слід рівно на одну сторінку більший — за кінцем ділянки\n"
         "стоїть сторожова; у рядків ioremap цього поля немає взагалі",
         FIELD, GREENF),
        ("vmalloc",
         "яким шляхом\nузято ділянку",
         "буває ще vmap, ioremap, user, vpages, dma-coherent",
         MUTED, PALE),
        ("N0=2048",
         "скільки кадрів\nз якого вузла NUMA",
         "з'являється лише на ядрах, зібраних із підтримкою NUMA",
         MUTED, PALE),
    ]

    y = 228
    for field, what, howto, accent, fillc in rows:
        p.append(fitbox(60, y, 300, 92, field, size=13,
                        fill=SOFT, stroke=accent, sw=1.5, color=accent, bold=True))
        p.append(fitbox(376, y, 330, 92, what, size=13,
                        fill=fillc, stroke=accent, sw=1.6, color=INK, bold=True))
        p.append(fitbox(722, y, 638, 92, howto, size=12,
                        fill=SOFT, stroke=MUTED, sw=1.2, color=INK))
        y += 104

    p.append(fitbox(60, 964, 1300, 74,
                    "ще дві форми рядка викликача не мають узагалі: «vm_map_ram» — дрібні відображення\n"
                    "із запасу свого ядра процесора, «unpurged vm_area» — уже звільнене, ще не вичищене",
                    size=14, fill=WARM, stroke=POS, sw=1.6, color=INK))

    render(os.path.join(OUT, "vmallocinfo-line.svg"), W, H, *p)


# ── 6. Найбільший вільний шматок: що зробити з рядками перед виміром ─────────
def fig_largest_gap():
    W, H = 1420, 880
    p = []

    def badge(cx, cy, n, color):
        return (circle(cx, cy, 16, fill="#ffffff", stroke=color, sw=2.2) +
                text(cx, cy + 5, str(n), size=15, color=color, bold=True))

    p.append(fitbox(60, 30, 1300, 50,
                    "НАЙБІЛЬШИЙ ВІЛЬНИЙ ШМАТОК: ЩО ТРЕБА ЗРОБИТИ З РЯДКАМИ, ПЕРШ НІЖ МІРЯТИ",
                    size=16, fill=PALE, stroke=INK, sw=1.6, color=INK, bold=True))

    p.append(text(710, 116, "у файлі рядки за адресою НЕ впорядковані",
                  size=14, color=POS, bold=True))
    heap = [(72, 300, "вузол 0:\nсвої ділянки за зростанням", COOL, NEG),
            (392, 300, "вузол 1:\nзнову з початку області", COOL, NEG),
            (712, 300, "вузол 2:\nі так далі", COOL, NEG),
            (1032, 316, "хвіст файлу:\nunpurged vm_area", WARM, POS)]
    for x, w, s, fillc, accent in heap:
        p.append(fitbox(x, 132, w, 68, s, size=12,
                        fill=fillc, stroke=accent, sw=1.6, color=INK))

    p.append(arrow(710, 206, 710, 240, color=FIELD, sw=1.8))
    p.append(fitbox(470, 244, 480, 46, "qsort за початковою адресою", size=14,
                    fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    # вісь адрес
    ax_y = 402
    p.append(text(120, 350, "нижчі адреси", size=12, color=MUTED, anchor="start"))
    p.append(line(96, ax_y + 74, 1164, ax_y + 74, color=MUTED, sw=2))

    busy = [(100, 130, "зайнято"), (270, 80, ""), (386, 140, ""),
            (700, 66, ""), (950, 54, "")]
    for x, w, s in busy:
        p.append(fitbox(x, ax_y, w, 60, s, size=12,
                        fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    # звільнене, ще не вичищене — теж зайняте
    p.append(fitbox(810, ax_y, 110, 60, "", size=12,
                    fill=WARM, stroke=POS, sw=2.2, color=POS))

    # вільний хвіст
    p.append(fitbox(1004, ax_y, 160, 60, "вільно", size=12,
                    fill=GREENF, stroke=FIELD, sw=1.6, color=FIELD, bold=True))
    p.append(line(1164, ax_y + 30, 1226, ax_y + 30, color=MUTED, sw=2, dash="7,7"))
    p.append(text(1195, ax_y - 14, "≈ 60 ТіБ", size=12, color=MUTED))
    p.append(fitbox(1226, ax_y, 134, 60, "область\nмодулів", size=12,
                    fill=PALE, stroke=MUTED, sw=1.6, color=MUTED, bold=True))

    p.append(badge(613, ax_y - 26, 1, FIELD))
    p.append(badge(865, ax_y - 26, 2, POS))
    p.append(badge(1084, ax_y - 26, 3, FIELD))
    p.append(badge(1293, ax_y - 26, 4, MUTED))

    legend = [
        (70, 1, FIELD, GREENF,
         "найбільша дірка між сусідніми зайнятими діапазонами —\n"
         "те число, у яке має влізти наступний великий запит"),
        (390, 2, POS, WARM,
         "звільнене, ще не вичищене: кадри вже віддано,\n"
         "а адреси ще нікому не належать — рахуємо як зайняте"),
        (710, 3, FIELD, GREENF,
         "вільний хвіст до кінця області: довжину беремо\n"
         "з рядка VmallocTotal у /proc/meminfo — у файлі кінця не видно"),
        (1030, 4, MUTED, PALE,
         "ділянки з області модулів: між двома областями\n"
         "не дірка, а чужі адреси — з підрахунку геть"),
    ]
    for x, n, accent, fillc, s in legend:
        p.append(badge(x + 150, 542, n, accent))
        p.append(fitbox(x, 572, 300, 124, s, size=12,
                        fill=fillc, stroke=accent, sw=1.6, color=INK))

    p.append(fitbox(70, 726, 1260, 96,
                    "три перші пастки роблять із правильного числа занижене, четверта — завищене;\n"
                    "усі чотири виправляються до того, як програма взагалі почне віднімати адреси",
                    size=14, fill=SOFT, stroke=INK, sw=1.5, color=INK))

    render(os.path.join(OUT, "vmalloc-largest-gap.svg"), W, H, *p)


# ── 7. Хто володіє сторінками після кожного з трьох контрактів ──────────────
def fig_vmap_ownership():
    W, H = 1440, 900
    p = []

    p.append(fitbox(60, 34, 1320, 50,
                    "ТРИ КОНТРАКТИ: ХТО ВЗЯВ КАДРИ, ХТО ЇХ ПОВЕРНЕ",
                    size=16, fill=PALE, stroke=INK, sw=1.6, color=INK, bold=True))

    cols = [(60, 420), (510, 420), (960, 420)]
    calls = [
        ("vmalloc(size)\n→ vfree(p)", NEG, COOL),
        ("vmap(pages, n, 0, prot)\n→ vunmap(p)", FIELD, GREENF),
        ("vmap(pages, n,\n    VM_MAP_PUT_PAGES, prot)\n→ vfree(p)", POS, WARM),
    ]
    for (x, w), (s, accent, fillc) in zip(cols, calls):
        p.append(fitbox(x, 104, w, 86, s, size=14,
                        fill=fillc, stroke=accent, sw=2.0, color=accent, bold=True))

    # хто дав кадри
    p.append(text(80, 232, "хто взяв кадри в розподільника:", size=13,
                  color=MUTED, anchor="start"))
    givers = [
        ("ядро — усередині виклику", NEG, COOL),
        ("ВИ — заздалегідь, самі", FIELD, GREENF),
        ("ВИ — заздалегідь, самі", POS, WARM),
    ]
    for (x, w), (s, accent, fillc) in zip(cols, givers):
        p.append(fitbox(x, 250, w, 62, s, size=14,
                        fill=fillc, stroke=accent, sw=1.6, color=INK, bold=True))

    # що робить парний виклик
    p.append(text(80, 358, "що робить парний виклик:", size=13,
                  color=MUTED, anchor="start"))
    undo = [
        ("знімає записи таблиць,\nповертає адреси\nі ВІДДАЄ КАДРИ", NEG, COOL),
        ("знімає записи таблиць\nі повертає адреси —\nі більше нічого", FIELD, GREENF),
        ("знімає записи таблиць,\nзнімає по посиланню з кожної\nсторінки, звільняє масив pages", POS, WARM),
    ]
    for (x, w), (s, accent, fillc) in zip(cols, undo):
        p.append(fitbox(x, 376, w, 108, s, size=13,
                        fill=SOFT, stroke=accent, sw=1.6, color=INK))

    for (x, w) in cols:
        p.append(arrow(x + w / 2, 492, x + w / 2, 534, color=MUTED, sw=1.6))

    # підсумок: що лишилося у вас на руках
    p.append(text(80, 560, "що лишається на ваших руках:", size=13,
                  color=MUTED, anchor="start"))
    left = [
        ("нічого — пам'ять повернуто", NEG, COOL, "#ffffff"),
        ("КАДРИ, і віддати їх\nмусите ви самі", POS, WARM, WARM),
        ("нічого — пам'ять повернуто", POS, WARM, "#ffffff"),
    ]
    for (x, w), (s, accent, fillc, bg) in zip(cols, left):
        p.append(fitbox(x, 578, w, 84, s, size=14,
                        fill=bg, stroke=accent, sw=2.0, color=accent, bold=True))

    p.append(fitbox(60, 696, 1320, 76,
                    "забутий крок у середньому стовпці — найтихіший витік у ядрі:\n"
                    "покажчик уже недійсний, ділянки в /proc/vmallocinfo уже немає,\n"
                    "а кадри лишаються зайнятими до перезавантаження",
                    size=14, fill=WARM, stroke=POS, sw=1.8, color=INK))

    p.append(fitbox(60, 792, 1320, 76,
                    "умова правого стовпця: масив pages мусить бути з kmalloc або vmalloc —\n"
                    "його звільнить vfree; масив на стеку чи статичний дає пошкодження купи",
                    size=14, fill=SOFT, stroke=INK, sw=1.5, color=INK))

    render(os.path.join(OUT, "vmap-ownership.svg"), W, H, *p)


fig_kernel_map()
fig_two_paths()
fig_lazy_purge()
fig_three_walls()
fig_vmallocinfo_line()
fig_largest_gap()
fig_vmap_ownership()
print("ok")
