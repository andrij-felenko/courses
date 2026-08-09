# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. Що прибивання забороняє, а що ні ─────────────────────────────────────
def fig_what_is_forbidden():
    W, H = 1400, 840
    p = []

    XE, WE = 40, 300
    XV, WV = 366, 330
    XW, WW = 722, 638

    p.append(fitbox(XE, 52, WE, 46, "подія", size=13.5,
                    fill=PALE, stroke=MUTED, sw=1.4, color=MUTED, bold=True))
    p.append(fitbox(XV, 52, WV, 46, "що з прибитою сторінкою", size=13.5,
                    fill=PALE, stroke=MUTED, sw=1.4, color=MUTED, bold=True))
    p.append(fitbox(XW, 52, WW, 46, "чому саме так", size=13.5,
                    fill=PALE, stroke=MUTED, sw=1.4, color=MUTED, bold=True))

    rows = [
        ("Витіснення у своп", "ЗАБОРОНЕНО", FIELD, GREENF,
         "сторінка лежить у списку, якого\nзбирач не переглядає взагалі"),
        ("Викидання файлової\nсторінки з кешу", "ЗАБОРОНЕНО", FIELD, GREENF,
         "той самий список і та сама причина:\nзабирати нема кому"),
        ("Ущільнення пам'яті", "ДОЗВОЛЕНО", POS, WARM,
         "вміст переносять в інший кадр;\nадреса чинна, але буде дрібний збій"),
        ("munmap ділянки\nабо exec", "ПРИБИВАННЯ ЗНИКАЄ", NEG, COOL,
         "воно живе на ділянці простору,\nа не на самій сторінці"),
        ("fork", "ДИТИНА БЕЗ НЬОГО", NEG, COOL,
         "нащадок дістає ті самі сторінки,\nале ділянку без ознаки прибиття"),
        ("Присипляння на диск", "НЕ ЗАВАДИТЬ", POS, WARM,
         "образ усієї пам'яті пише ядро,\nі жодні прапорці його не спиняють"),
        ("Аварійний дамп\nі ptrace", "НЕ ЗАВАДИТЬ", POS, WARM,
         "вміст лягає у файл або в чужий буфер;\nвід дампа рятує окремо MADV_DONTDUMP"),
    ]

    y = 118
    for event, verdict, accent, fillc, why in rows:
        p.append(fitbox(XE, y, WE, 76, event, size=12.5,
                        fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(XV, y, WV, 76, verdict, size=13,
                        fill=fillc, stroke=accent, sw=1.7, color=accent, bold=True))
        p.append(fitbox(XW, y, WW, 76, why, size=12.5,
                        fill="#fff", stroke=MUTED, sw=1.2, color=INK))
        y += 90

    p.append(fitbox(40, y + 14, 1320, 84,
                    "прибивання забирає в ядра рівно одну свободу — віддати кадр комусь іншому;\n"
                    "усе решта, що рухає сторінку або копіює її вміст назовні, лишається чинним",
                    size=13.5, fill=WARM, stroke=POS, sw=1.7, color=INK))

    return render(os.path.join(OUT, "what-locking-forbids.svg"), W, H, *p,
                  title="Що прибивання пам'яті забороняє, а чого не забороняє")


# ── 2. Дві половини прибивання й MLOCK_ONFAULT ──────────────────────────────
def fig_two_halves():
    W, H = 1300, 700
    p = []

    cols = [
        (60, "звичайне відображення", MUTED, PALE,
         "нічого не робимо\nзаздалегідь",
         "з'являються за першим\nзвертанням — збій і диск",
         "ядро забирає їх,\nколи стане тісно",
         "нуль пам'яті наперед,\nчас відповіді непередбачний"),
        (450, "mlock / mlockall", FIELD, GREENF,
         "ОБИДВІ половини:\nпривести й тримати",
         "ядро вганяє їх у пам'ять\nпрямо у виклику",
         "лишаються, доки\nне знімеш прибивання",
         "уся ділянка займає\nпам'ять і межу відразу"),
        (840, "MLOCK_ONFAULT", NEG, COOL,
         "ЛИШЕ друга половина:\nтільки тримати",
         "з'являться, як і раніше,\nза першим звертанням",
         "щойно з'явилася —\nбільше не піде",
         "платимо тільки за те,\nчого справді торкнулися"),
    ]

    labels = ["що робить виклик", "відсутні сторінки", "присутні сторінки", "ціна"]
    ys = [180, 292, 404, 516]

    for x, name, accent, fillc, a, b, c, d in cols:
        p.append(fitbox(x, 96, 350, 54, name, size=14,
                        fill=fillc, stroke=accent, sw=1.8, color=accent, bold=True))
        for y, txt in zip(ys, (a, b, c, d)):
            p.append(fitbox(x, y, 350, 88, txt, size=12.5,
                            fill=SOFT if txt is a else "#fff",
                            stroke=accent, sw=1.3, color=INK))

    for y, lab in zip(ys, labels):
        p.append(text(1268, y + 50, lab, size=12.5, color=MUTED, anchor="end"))

    p.append(fitbox(60, 40, 1130, 42,
                    "велике розріджене відображення: сторінок мільйон, торкнеться програма тисячі",
                    size=13, fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))
    p.append(fitbox(60, 620, 1130, 62,
                    "MLOCK_ONFAULT — це рівно mlock без першої половини: він нічого не вганяє в пам'ять,\n"
                    "а лише позначає ділянку, щоб усе, що в ній з'явиться, звідти вже не пішло",
                    size=13.5, fill=COOL, stroke=NEG, sw=1.7, color=INK))

    return render(os.path.join(OUT, "two-halves-onfault.svg"), W, H, *p,
                  title="Дві половини прибивання і навіщо знадобилася лише друга")


# ── 3. Окремий список замість прапорця ──────────────────────────────────────
def fig_unevictable_list():
    W, H = 1300, 660
    p = []

    p.append(fitbox(60, 44, 1180, 48,
                    "збирач шукає, що звільнити, — і мусить перебирати списки сторінок",
                    size=14, fill=PALE, stroke=MUTED, sw=1.4, color=INK, bold=True))

    p.append(fitbox(60, 132, 240, 78, "збирач\n(vmscan)", size=14,
                    fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))

    lists = [
        (430, 132, "активний список", FIELD, GREENF, "переглядається"),
        (430, 246, "неактивний список", FIELD, GREENF, "переглядається"),
        (430, 384, "список невитіснюваних", NEG, COOL, "не переглядається ніколи"),
    ]
    for x, y, name, accent, fillc, note in lists:
        p.append(fitbox(x, y, 420, 78, name, size=13.5,
                        fill=fillc, stroke=accent, sw=1.7, color=accent, bold=True))
        p.append(text(880, y + 46, note, size=12.5, color=MUTED, anchor="start"))

    p.append(arrow(304, 168, 424, 168, POS))
    p.append(arrow(304, 178, 424, 282, POS))
    p.append(line(304, 190, 424, 418, MUTED, sw=1.6, dash="6,5"))
    p.append(text(348, 330, "×", size=26, color=NEG, bold=True))

    p.append(fitbox(60, 486, 560, 74,
                    "варіант «просто пропускати прибиті»:\nсписки повні, а знайти в них нічого",
                    size=12.5, fill="#fff", stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(680, 486, 560, 74,
                    "варіант «винести їх геть зі списків»:\nперебирати лишається тільки корисне",
                    size=12.5, fill=GREENF, stroke=FIELD, sw=1.6, color=INK))

    p.append(fitbox(60, 578, 1180, 58,
                    "саме тому прибиття — не прапорець, який перевіряють у циклі, а перенесення сторінки в інший список",
                    size=13, fill=SOFT, stroke=MUTED, sw=1.2, color=MUTED))

    return render(os.path.join(OUT, "unevictable-list.svg"), W, H, *p,
                  title="Чому прибиті сторінки виносять в окремий список, а не позначають прапорцем")


# ── 4. Спільна межа прибитої пам'яті ────────────────────────────────────────
def fig_shared_budget():
    W, H = 1300, 610
    p = []

    p.append(fitbox(70, 44, 1160, 52,
                    "RLIMIT_MEMLOCK — одна межа на процес, у яку вміщується все одразу",
                    size=14.5, fill=PALE, stroke=MUTED, sw=1.5, color=INK, bold=True))

    users = [
        (70, "mlock, mlockall", "пам'ять, прибита\nсамою програмою"),
        (365, "SHM_LOCK", "прибита ділянка\nспільної пам'яті"),
        (660, "io_uring", "зареєстровані буфери\nі кільця"),
        (955, "довгі закріплення", "сторінки, віддані\nпристроєві під DMA"),
    ]
    for x, name, what in users:
        p.append(fitbox(x, 136, 275, 50, name, size=13,
                        fill=COOL, stroke=NEG, sw=1.6, color=NEG, bold=True))
        p.append(fitbox(x, 200, 275, 74, what, size=12,
                        fill="#fff", stroke=MUTED, sw=1.2, color=INK))
        p.append(arrow(x + 137, 278, x + 137, 316, NEG))

    p.append(fitbox(70, 316, 1160, 54, "спільний рахунок прибитих байтів", size=14,
                    fill=GREENF, stroke=FIELD, sw=1.8, color=INK, bold=True))

    p.append(fitbox(70, 400, 560, 82,
                    "64 КіБ — стеля з 2008 року,\nпіднята заради ключів у GnuPG: 16 сторінок",
                    size=12.5, fill=SOFT, stroke=MUTED, sw=1.3, color=INK))
    p.append(fitbox(670, 400, 560, 82,
                    "8 МіБ — з ядра 5.16 (грудень 2021),\nбо в 16 сторінок не влазить жодне кільце",
                    size=12.5, fill=WARM, stroke=POS, sw=1.6, color=INK))

    p.append(fitbox(70, 502, 1160, 78,
                    "межу вважають витраченою всі чотири споживачі разом, тож бібліотека, що зареєструвала буфери,\n"
                    "мовчки з'їдає запас у програми, яка планувала прибити свої ключі",
                    size=13, fill="#fff", stroke=POS, sw=1.5, color=INK))

    return render(os.path.join(OUT, "shared-memlock-budget.svg"), W, H, *p,
                  title="Одна межа прибитої пам'яті на чотирьох різних споживачів")


# ── 5. Що прослизає повз самотній mlockall (вставка proj-realtime-preamble) ──
def fig_what_slips_past():
    W, H = 1280, 578
    p = []

    X1, W1 = 40, 300
    X2, W2 = 356, 430
    X3, W3 = 802, 430

    p.append(fitbox(X1, 52, W1, 44, "звідки візьметься сторінка", size=13,
                    fill=PALE, stroke=MUTED, sw=1.4, color=MUTED, bold=True))
    p.append(fitbox(X2, 52, W2, 44, "чому mlockall її не покрив", size=13,
                    fill=PALE, stroke=MUTED, sw=1.4, color=MUTED, bold=True))
    p.append(fitbox(X3, 52, W3, 44, "крок кістяка, що це закриває", size=13,
                    fill=PALE, stroke=MUTED, sw=1.4, color=MUTED, bold=True))

    rows = [
        ("Стек нижче вершини",
         "цих сторінок ще немає у відображенні:\nстек росте вниз лише за потребою",
         "спуск у локальний масив\nіз ЗАПИСОМ у кожну сторінку"),
        ("Купа після free()",
         "розподільник зсуває верх купи вниз,\nа великі шматки й зовсім віддає",
         "M_TRIM_THRESHOLD −1, M_MMAP_MAX 0\nплюс одноразовий обхід обсягу"),
        ("Стек нового потоку",
         "MCL_FUTURE прибиває його при створенні —\nразом із цілими 8 МіБ межі",
         "явний розмір стека потоку\nі піднята межа прибитої пам'яті"),
        ("Арена нового потоку",
         "glibc заводить потокові власну купу,\nякої розігрів не торкався",
         "M_ARENA_MAX 1, а розігрів стека\nповторити в кожному потоці"),
    ]

    y = 116
    for name, why, fix in rows:
        p.append(fitbox(X1, y, W1, 92, name, size=13.5,
                        fill=COOL, stroke=NEG, sw=1.6, color=INK, bold=True))
        p.append(fitbox(X2, y, W2, 92, why, size=12.5,
                        fill=WARM, stroke=POS, sw=1.4, color=INK))
        p.append(fitbox(X3, y, W3, 92, fix, size=12.5,
                        fill=GREENF, stroke=FIELD, sw=1.4, color=INK))
        y += 104

    return render(os.path.join(OUT, "what-slips-past-mlockall.svg"), W, H, *p,
                  title="Чотири джерела сторінок, які приходять уже після mlockall")


# ── 6. Форма хвоста: найгірший випадок з прибиванням і без ───────────────────
def fig_worst_case_tail():
    W, H = 1280, 622
    p = []

    X0, DW = 110, 124            # початок осі й ширина однієї смуги-декади
    DEC = ["10 нс", "100 нс", "1 мкс", "10 мкс", "100 мкс", "1 мс", "10 мс"]
    SCALE = 32.0                 # пікселів на одиницю логарифмічної висоти

    def panel(label, base_y, bars, tint, edge, verdict):
        q = [fitbox(X0, base_y - 200, 640, 40, label, size=13.5,
                    fill=PALE, stroke=MUTED, sw=1.3, color=INK, bold=True)]
        q.append(line(X0 - 10, base_y, X0 + 7 * DW + 10, base_y, color=MUTED, sw=1.6))
        for k, v in enumerate(bars):
            cx = X0 + k * DW + DW / 2
            if v <= 0:
                continue
            bh = v * SCALE
            q.append(rect(cx - 44, base_y - bh, 88, bh,
                          fill=tint, stroke=edge, sw=1.5, rx=3))
        for k, name in enumerate(DEC):
            cx = X0 + k * DW + DW / 2
            q.append(text(cx, base_y + 22, name, size=12.5, color=MUTED))
        q.append(fitbox(1000, base_y - 128, 230, 76, verdict, size=13,
                        fill=tint, stroke=edge, sw=1.8, color=INK, bold=True))
        return q

    p += panel("без прибивання — висота смуги росте з кількістю звертань",
               262,
               [0, 5.0, 3.0, 1.5, 1.0, 2.0, 1.2],
               WARM, POS,
               "найгірше:\nодиниці мілісекунд")

    p += panel("з прибиванням і розігрівом — той самий код, та сама машина",
               530,
               [0, 5.0, 3.2, 1.2, 0.3, 0, 0],
               GREENF, FIELD,
               "найгірше:\nдесятки мікросекунд")

    return render(os.path.join(OUT, "worst-case-tail.svg"), W, H, *p,
                  title="Середина розподілу не рухається — зникає його хвіст")


if __name__ == "__main__":
    print(fig_what_is_forbidden())
    print(fig_two_halves())
    print(fig_unevictable_list())
    print(fig_shared_budget())
    print(fig_what_slips_past())
    print(fig_worst_case_tail())
