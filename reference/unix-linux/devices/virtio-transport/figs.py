# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. Анатомія розділеної віртчерги ────────────────────────────────────────
def fig_split_virtqueue():
    W, H = 1500, 980
    p = []
    cx = 560
    nx = 1220

    p.append(text(cx, 46, "СПІЛЬНА ПАМ'ЯТЬ ГОСТЯ", size=15, bold=True))
    p.append(text(cx, 70, "зелене пише лише драйвер · тепле пише лише пристрій",
                  size=12, color=MUTED))

    # доступне кільце
    avail, wa, ha = textbox(cx, 165,
                            ["ДОСТУПНЕ КІЛЬЦЕ",
                             "flags │ idx = 5 │ ring[] = 0, 4, 9, 2, 6"],
                            size=13, pad=15, fill=GREEN_FILL, stroke=LINE, sw=1.6)
    p.append(avail)

    # таблиця дескрипторів
    p.append(text(cx, 300, "ТАБЛИЦЯ ДЕСКРИПТОРІВ — один запит це ланцюг ланок",
                  size=13, bold=True))
    xs = [270, 560, 850]
    rows = [
        ["#6  addr = 0x3f21000", "len = 12", "flags = NEXT", "next = 7"],
        ["#7  addr = 0x3f8a200", "len = 1500", "flags = WRITE|NEXT", "next = 9"],
        ["#9  addr = 0x3f8c000", "len = 1", "flags = WRITE", "next = —"],
    ]
    dgeo = []
    for x, lines in zip(xs, rows):
        frag, w, h = textbox(x, 420, lines, size=12.5, pad=13,
                             fill=GREY_FILL, stroke=LINE, sw=1.5)
        p.append(frag)
        dgeo.append((x, w, h))
    for (x1, w1, _), (x2, w2, _) in zip(dgeo, dgeo[1:]):
        p.append(arrow(x1 + w1 / 2 + 8, 420, x2 - w2 / 2 - 8, 420))

    # ужите кільце
    used, wu, hu = textbox(cx, 620,
                           ["УЖИТЕ КІЛЬЦЕ",
                            "flags │ idx = 3 │ ring[] = { id = 6, len = 1513 }, …"],
                           size=13, pad=15, fill=WARM_FILL, stroke=LINE, sw=1.6)
    p.append(used)

    # лінія до таблиці розбита на два відрізки, щоб обійти напис заголовка
    # таблиці (він лежить рівно на шляху cx, y≈300) — не перетинаємо текст лінією
    title_top = 300 - 13 * 0.72 - 5
    title_bot = 300 + 13 * 0.16 + 5
    p.append(line(cx, 165 + ha / 2 + 10, cx, title_top, color=LINE, sw=1.8))
    p.append(arrow(cx, title_bot, cx, 420 - dgeo[1][2] / 2 - 40))
    p.append(arrow(cx, 420 + dgeo[1][2] / 2 + 12, cx, 620 - hu / 2 - 10))

    def note(y, lines, fill=GREY_FILL, anchor_w=0):
        frag, nw, _ = textbox(nx, y, lines, size=12.5, pad=13, fill=fill,
                              stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(cx + anchor_w / 2 + 14, y, nx - nw / 2 - 14, y,
                      color=MUTED, sw=1.1, dash="5 4"))

    note(165, ["idx драйвер піднімає ОСТАННІМ:",
               "поки число не зросло,",
               "ланцюга для пристрою не існує"], GREEN_FILL, wa)
    note(420, ["прапорець WRITE каже,",
               "кому належить право писати",
               "саме в цей буфер"], GREY_FILL, dgeo[1][1])
    note(620, ["len — скільки байтів пристрій",
               "справді записав; id — номер",
               "голови ланцюга, а не позиція"], WARM_FILL, wu)

    frag, _, _ = textbox(cx, 790,
                         ["Індекси вільно ростуть і обертаються на 2¹⁶ —",
                          "жодна сторона ніколи не править чуже поле."],
                         size=12.5, pad=13, fill=BLUE_FILL, stroke=FIELD, sw=1.3)
    p.append(frag)

    frag, _, _ = textbox(cx + 190, 900,
                         ["Межу перетинають лише дві події: «кік» від драйвера в регістр сповіщення",
                          "і переривання від пристрою. Дані нікуди не копіюються — обидва працюють на місці."],
                         size=12.5, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'split-virtqueue.svg'), W, H, *p,
           title="Три області розділеної віртчерги і хто в яку пише")


# ── 2. Рукостискання драйвера з пристроєм ───────────────────────────────────
def fig_handshake():
    W, H = 1380, 980
    p = []
    cx = 400
    nx = 1010

    steps = [
        (70, ["скидання: status = 0"], GREY_FILL),
        (185, ["status |= ACKNOWLEDGE", "ядро побачило пристрій і впізнало його тип"], BLUE_FILL),
        (315, ["status |= DRIVER", "знайшовся драйвер, який береться його вести"], BLUE_FILL),
        (455, ["драйвер читає біти можливостей пристрою",
               "й записує назад ту підмножину, яку підтримує сам"], GREEN_FILL),
        (600, ["status |= FEATURES_OK", "і драйвер одразу перечитує status"], GREEN_FILL),
        (735, ["налаштування віртчерг:",
               "розмір і адреси трьох областей кожної черги"], WARM_FILL),
        (870, ["status |= DRIVER_OK", "з цієї миті пристрій має право читати кільця"], WARM_FILL),
    ]
    geo = []
    for y, lines, fill in steps:
        frag, w, h = textbox(cx, y, lines, size=13, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)
        geo.append((y, w, h))
    for (y1, _, h1), (y2, _, h2) in zip(geo, geo[1:]):
        p.append(arrow(cx, y1 + h1 / 2 + 10, cx, y2 - h2 / 2 - 10))

    def note(idx, lines, fill=GREY_FILL):
        y, w, _ = geo[idx]
        frag, nw, _ = textbox(nx, y, lines, size=12.5, pad=13, fill=fill,
                              stroke=MUTED, sw=1.2)
        p.append(frag)
        p.append(line(cx + w / 2 + 14, y, nx - nw / 2 - 14, y,
                      color=MUTED, sw=1.1, dash="5 4"))

    note(3, ["перетин двох списків і є контракт;",
             "після нього жодна сторона не має права",
             "ані додати можливість, ані відібрати"])
    note(4, ["якщо біт не втримався — пристрій",
             "не годен обслуговувати такий набір;",
             "драйверові лишається status |= FAILED"], RED_FILL)
    note(5, ["розкладка кілець залежить від",
             "узгоджених бітів — тому черги",
             "налаштовують ПІСЛЯ, а не до"])
    note(6, ["до цієї миті пристрій зобов'язаний",
             "вдавати, що кілець не бачить"])

    render(os.path.join(IMG, 'handshake.svg'), W, H, *p,
           title="Порядок кроків, якими драйвер приводить пристрій virtio до роботи")


# ── 3. Розділена черга проти упакованої ─────────────────────────────────────
def fig_packed_ring():
    W, H = 1420, 820
    p = []
    lx, rx = 370, 1030

    p.append(text(lx, 50, "РОЗДІЛЕНА ЧЕРГА", size=15, bold=True))
    p.append(text(rx, 50, "УПАКОВАНА ЧЕРГА", size=15, bold=True))
    p.append(line(700, 75, 700, 640, color=MUTED, sw=1.4, dash="7 6"))

    for y, lines, fill in [
        (135, ["таблиця дескрипторів", "addr · len · flags · next"], GREY_FILL),
        (255, ["доступне кільце", "flags · idx · ring[]"], GREEN_FILL),
        (375, ["ужите кільце", "flags · idx · ring[] з пар { id, len }"], WARM_FILL),
    ]:
        frag, _, _ = textbox(lx, y, lines, size=12.5, pad=13, fill=fill,
                             stroke=LINE, sw=1.5)
        p.append(frag)

    frag, _, _ = textbox(lx, 520,
                         ["Щоб узяти один запит, споживач чіпає",
                          "три різні області — до трьох рядків кешу,",
                          "і всі три ходять між процесорами."],
                         size=12.5, pad=13, fill=RED_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    rows = [
        (135, "#0  addr · len · id = 6 · flags: AVAIL", GREEN_FILL),
        (215, "#1  addr · len · id = 6 · flags: AVAIL", GREEN_FILL),
        (295, "#2  addr · len · id = 4 · flags: USED", WARM_FILL),
        (375, "#3  addr · len · id = —  · flags: —", GREY_FILL),
    ]
    for y, s, fill in rows:
        frag, _, _ = textbox(rx, y, [s], size=12.5, pad=12, fill=fill,
                             stroke=LINE, sw=1.4)
        p.append(frag)

    frag, _, _ = textbox(rx, 520,
                         ["Одна область, 16 байтів на дескриптор —",
                          "чотири в рядок кешу. Чий зараз запис,",
                          "кажуть два біти прапорців проти",
                          "лічильника обороту кільця."],
                         size=12.5, pad=13, fill=BLUE_FILL, stroke=FIELD, sw=1.2)
    p.append(frag)

    frag, _, _ = textbox(700, 700,
                         ["Обидві розкладки описують той самий обмін — міняється лише те,",
                          "скільки пам'яті доводиться перегнати між ядрами процесора на один запит."],
                         size=12.5, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'packed-ring.svg'), W, H, *p,
           title="Розкладка розділеної та упакованої віртчерги")


# ── 4. Що саме звів Расселл: 2007 проти 2008 ────────────────────────────────
def fig_driver_zoo():
    W, H = 1560, 800
    p = []
    lx, rx = 400, 1160

    p.append(text(lx, 44, "2007: кожен гіпервізор зі своїм набором", size=16, bold=True))
    p.append(text(lx, 72, "три ролі пристрою на п'ять світів — і жодного спільного рядка",
                  size=12.5, color=MUTED))

    zoo = ["Xen", "KVM", "IBM System p/z", "User Mode Linux", "lguest"]
    y = 140
    for name in zoo:
        frag, _, _ = textbox(lx, y,
                             [name + ":  блоковий · мережевий · консоль"],
                             size=13, pad=13, fill=RED_FILL, stroke=LINE, sw=1.3)
        p.append(frag)
        y += 74

    frag, _, _ = textbox(lx, y + 22,
                         ["Спільного між ними — самі лише наміри.",
                          "Кожен виправлений баг лікує один світ із шести."],
                         size=12.5, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    p.append(line(770, 30, 770, 760, color=MUTED, sw=1.2, dash="7,7"))

    p.append(text(rx, 44, "2008: одна шина, тонкий прошарок під низом", size=16, bold=True))
    p.append(text(rx, 72, "драйвер пише в пам'ять, транспорт лише дзвонить у двері",
                  size=12.5, color=MUTED))

    tops = [(960, "virtio_net"), (1160, "virtio_blk"), (1360, "virtio_console")]
    for x, name in tops:
        frag, _, _ = textbox(x, 145, [name], size=13.5, pad=14,
                             fill=GREEN_FILL, stroke=LINE, sw=1.4)
        p.append(frag)
        p.append(arrow(x, 178, x, 232))

    core, _, _ = textbox(rx, 285,
                         ["ЯДРО virtio  —  віртчерги й vring",
                          "буфери, оповіщення, узгодження можливостей"],
                         size=13.5, pad=16, fill=BLUE_FILL, stroke=LINE, sw=1.7)
    p.append(core)
    p.append(arrow(rx, 345, rx, 405))

    tr, _, _ = textbox(rx, 480,
                       ["ТРАНСПОРТ — усе, що залежить від гіпервізора",
                        "lguest · virtio_pci · канальні пристрої s390 · MMIO",
                        "знайти пристрій, дати регістри, донести дзвінок"],
                       size=13, pad=16, fill=WARM_FILL, stroke=LINE, sw=1.5)
    p.append(tr)

    frag, _, _ = textbox(rx, 630,
                         ["Новий гіпервізор коштує один транспорт,",
                          "а не три драйвери; виправлення в ядрі virtio",
                          "дістається всім світам одночасно."],
                         size=12.5, pad=14, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'driver-zoo.svg'), W, H, *p,
           title="Від набору драйверів на гіпервізор до однієї шини з транспортами")


# ── 5. Байтова карта ділянки (вставка proj-ring-walk) ───────────────────────
def fig_ring_walk_layout():
    W, H = 1320, 820
    p = []
    cx = 760
    ox = 330          # права межа підписів зі зсувами

    p.append(text(cx, 62, "одна ділянка mmap; початок вирівняно на сторінку, "
                          "тож вимога «16» задоволена сама собою",
                  size=13, color=MUTED))

    rows = [
        (150, "+0",
         ["ТАБЛИЦЯ ДЕСКРИПТОРІВ  —  16 Б × 8 ланок = 128 Б",
          "вирівнювання 16 · заповнює драйвер, читає пристрій"],
         GREY_FILL),
        (290, "+128",
         ["ДОСТУПНЕ КІЛЬЦЕ  —  6 + 2×8 = 22 Б",
          "вирівнювання 2 · flags, idx, ring[8] пише драйвер",
          "used_event — останні 2 Б — пише ПРИСТРІЙ"],
         GREEN_FILL),
        (430, "+150",
         ["ПОРОЖНЄ МІСЦЕ  —  42 Б",
          "щоб ужите кільце почалося зі свого рядка кешу"],
         GREY_FILL),
        (570, "+192",
         ["УЖИТЕ КІЛЬЦЕ  —  6 + 8×8 = 70 Б",
          "специфікація вимагає 4, беремо 64 · flags, idx, ring[8] пише пристрій",
          "avail_event — останні 2 Б — пише ДРАЙВЕР"],
         WARM_FILL),
        (720, "+320",
         ["ПУЛ БУФЕРІВ  —  самі дані",
          "адреси в дескрипторах — зсуви від початку ділянки, не покажчики"],
         BLUE_FILL),
    ]

    for y, off, lines, fill in rows:
        frag, w, h = textbox(cx, y, lines, size=13, pad=16,
                             fill=fill, stroke=LINE, sw=1.5, min_w=880)
        p.append(frag)
        p.append(text(ox, y + 5, off, size=14, bold=True, anchor="end"))

    render(os.path.join(IMG, 'ring-walk-layout.svg'), W, H, *p,
           title="Розкладка віртчерги на 8 ланок: зсуви, розміри, вирівнювання")


# ── 6. Загублене пробудження (вставка proj-ring-walk) ───────────────────────
def fig_ring_walk_lost_wakeup():
    W, H = 1440, 800
    p = []
    lx, rx = 400, 1040

    head_l, _, _ = textbox(lx, 110, ["ДРАЙВЕР  (виробник)"], size=14, bold=True,
                           pad=14, fill=GREEN_FILL, stroke=LINE, sw=1.6, min_w=460)
    head_r, _, _ = textbox(rx, 110, ["ПРИСТРІЙ  (споживач)"], size=14, bold=True,
                           pad=14, fill=WARM_FILL, stroke=LINE, sw=1.6, min_w=460)
    p.append(head_l)
    p.append(head_r)

    steps = [
        (lx, 250, ["1 · store  avail->idx = 5",
                   "додав роботу в чергу"], GREY_FILL),
        (rx, 250, ["1 · store  used->avail_event = 5",
                   "«розбуди мене, коли дійдеш до 5»"], GREY_FILL),
        (lx, 420, ["2 · load  used->avail_event",
                   "бачить старе 9  →  «ще не час»",
                   "кіку немає"], RED_FILL),
        (rx, 420, ["2 · load  avail->idx",
                   "бачить старе 4  →  «порожньо»",
                   "засинає на read(kickfd)"], RED_FILL),
    ]
    for x, y, lines, fill in steps:
        frag, _, _ = textbox(x, y, lines, size=13, pad=15,
                             fill=fill, stroke=LINE, sw=1.5, min_w=460)
        p.append(frag)

    p.append(arrow(lx, 305, lx, 358))
    p.append(arrow(rx, 305, rx, 358))
    p.append(line(720, 155, 720, 490, color=MUTED, sw=1.2, dash="7 6"))

    tail, _, _ = textbox(720, 620,
                         ["Кожен читає стан, що передував чужому запису — і обидва сплять,",
                          "а запит лишається в черзі назавжди.",
                          "Рятує лише повний бар'єр «запис → читання» з ОБОХ боків:",
                          "atomic_thread_fence(memory_order_seq_cst) перед перевіркою позначки.",
                          "Бар'єра запису чи читання тут замало — вони цієї пари не впорядковують."],
                         size=13, pad=18, fill=BLUE_FILL, stroke=LINE, sw=1.5)
    p.append(tail)

    render(os.path.join(IMG, 'ring-walk-lost-wakeup.svg'), W, H, *p,
           title="Чому перед читанням позначки потрібен саме повний бар'єр")


if __name__ == '__main__':
    fig_split_virtqueue()
    fig_handshake()
    fig_packed_ring()
    fig_driver_zoo()
    fig_ring_walk_layout()
    fig_ring_walk_lost_wakeup()
    print("ok")
