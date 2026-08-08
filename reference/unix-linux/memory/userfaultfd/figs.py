# -*- coding: utf-8 -*-
"""Фігури до теми «userfaultfd» (reference/unix-linux/memory)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

COLD = "#eaf0fd"   # те, що робить ядро/апаратура
WARM = "#fdf3e6"   # те, що вирішує програма
HEAD = "#eef2f7"


# ── 1. Кругообіг одного збою ────────────────────────────────────────────────
def fig_loop():
    W, H = 1340, 560
    frags = []

    bw, bh = 296, 128
    gap = 44
    x0 = 30
    ytop, ybot = 96, 336

    top = [
        ("1  Звернення за адресою",
         "запису в таблиці сторінок\nнемає — інструкція спиняється", COLD),
        ("2  Керування в ядрі",
         "ядро бачить: ділянку зареєстровано,\nотже, звичайний шлях не для неї", COLD),
        ("3  Повідомлення в чергу",
         "адресу й ознаку «читання чи запис»\nкладуть у чергу дескриптора", COLD),
        ("4  Винуватця вкладено спати",
         "дескриптор став читабельним —\nнаглядач прокидається на poll", COLD),
    ]
    bottom = [
        ("7  Інструкція наново",
         "та сама інструкція виконується\nвдруге — і цього разу успішно", COLD),
        ("6  UFFDIO_COPY",
         "ядро заповнює кадр, вписує запис\nу таблицю й будить винуватця", COLD),
        ("5  Наглядач бере вміст",
         "мережа, файл, генератор —\nджерело знає тільки програма", WARM),
    ]

    def put(items, y):
        xs = []
        for i, (title, body, fill) in enumerate(items):
            x = x0 + i * (bw + gap)
            xs.append(x)
            frags.append(rect(x, y, bw, bh, fill=fill, stroke=LINE))
            frags.append(mtext(x + bw / 2, y + 34, [title], size=16, bold=True))
            frags.append(mtext(x + bw / 2, y + 66, body.split("\n"), size=14, color=INK))
        return xs

    xs_top = put(top, ytop)
    xs_bot = put(bottom, ybot)

    # стрілки в верхньому ряду: зліва направо
    for i in range(3):
        x1 = xs_top[i] + bw + 6
        x2 = xs_top[i + 1] - 6
        frags.append(arrow(x1, ytop + bh / 2, x2, ytop + bh / 2))
    # стрілки в нижньому ряду: справа наліво
    for i in range(2):
        x1 = xs_bot[i + 1] - 6
        x2 = xs_bot[i] + bw + 6
        frags.append(arrow(x1, ybot + bh / 2, x2, ybot + bh / 2))
    # перехід із верхнього ряду в нижній (праворуч)
    xr = xs_top[3] + bw / 2
    frags.append(arrow(xr, ytop + bh + 6, xr, ybot - 6))
    # повернення з нижнього ряду вгору (ліворуч)
    xl = xs_bot[0] + bw / 2
    frags.append(arrow(xl, ybot - 6, xl, ytop + bh + 6))

    # підписи смуг
    frags.append(text(x0, 58, "Робить апаратура й ядро — без участи програми",
                      size=15, color=MUTED, anchor="start", bold=True))
    frags.append(text(x0, ybot + bh + 46,
                      "Крок 5 — єдине місце, де рішення ухвалює програма",
                      size=15, color=MUTED, anchor="start", bold=True))

    render(os.path.join(OUT, 'uffd-loop.svg'), W, H, *frags,
           title="Кругообіг одного сторінкового збою через userfaultfd")


# ── 2. Дві дії лишають щілину, одна — ні ────────────────────────────────────
def fig_atomic():
    W, H = 1180, 520
    frags = []

    lx, lw = 34, 300          # ліва колонка з назвою способу
    tx0 = 366                 # початок часової осі
    tx1 = 1140

    def panel(y, name, marks, gap_span, note, note_color):
        frags.append(fitbox(lx, y - 34, lw, 68, name, size=16, bold=True, fill=HEAD))
        # вісь часу
        frags.append(arrow(tx0, y, tx1, y))
        frags.append(text(tx1, y + 34, "час", size=14, color=MUTED, anchor="end"))
        # заштрихована щілина
        if gap_span:
            gx1, gx2 = gap_span
            frags.append(rect(gx1, y - 62, gx2 - gx1, 124, fill="#fdecea",
                              stroke=POS, sw=1.5, rx=4))
        for mx, label, below in marks:
            frags.append(line(mx, y - 16, mx, y + 16, color=INK, sw=2))
            frags.append(mtext(mx, y - 34, label.split("\n"), size=14, bold=True))
            if below:
                frags.append(mtext(mx, y + 46, below.split("\n"), size=13, color=MUTED))
        if note:
            frags.append(mtext((tx0 + tx1) / 2, y + 96, note.split("\n"),
                               size=15, color=note_color, bold=True))

    panel(140, "mprotect,\nа потім запис руками",
          [(560, "mprotect:\nправа відкрито", None),
           (900, "дані вписано", None)],
          (560, 900),
          "у цій смузі другий потік читає з ділянки нулі —\nі не спотикається, бо права вже відкрито",
          POS)

    panel(390, "UFFDIO_COPY",
          [(730, "кадр заповнено й запис\nу таблиці з'явився разом", None)],
          None,
          "проміжного стану немає: доти кожен, хто звернеться,\nпросто спотикається й чекає в тій самій черзі",
          FIELD)

    render(os.path.join(OUT, 'atomic-fill.svg'), W, H, *frags,
           title="Заповнення сторінки: дві дії проти однієї")


# ── 3. Три режими реєстрації ────────────────────────────────────────────────
def fig_modes():
    W, H = 1300, 470
    frags = []

    cols = [(30, 210), (256, 330), (610, 330), (964, 306)]
    heads = ["Режим реєстрації", "Стан сторінки перед збоєм",
             "Про що приходить повідомлення", "Чим збій закривають"]

    hy, hh = 44, 56
    for (x, w), t in zip(cols, heads):
        frags.append(fitbox(x, hy, w, hh, t, size=15, bold=True, fill=HEAD))

    rows = [
        ("MISSING\n(з 4.3)",
         "фізичного кадру немає,\nзапису в таблиці немає",
         "за цією адресою\nще нічого не лежить",
         "UFFDIO_COPY\nабо UFFDIO_ZEROPAGE",
         FILL, LINE),
        ("WP\n(з 5.7)",
         "кадр є, запис є,\nале дозвіл на запис знято",
         "у цю сторінку\nщойно спробували писати",
         "UFFDIO_WRITEPROTECT\n(зняти захист)",
         "#fdf3e6", POS),
        ("MINOR\n(з 5.13 / 5.14)",
         "кадр уже в кеші сторінок,\nбракує лише запису",
         "вміст готовий,\nвідображення ще нема",
         "UFFDIO_CONTINUE\n(відобразити наявне)",
         "#eaf0fd", NEG),
    ]

    y = 124
    rh, gap = 96, 20
    for mode, before, message, resolve, fill, stroke in rows:
        for (x, w), t, big in zip(cols, [mode, before, message, resolve],
                                  [True, False, False, False]):
            frags.append(fitbox(x, y, w, rh, t, size=16 if big else 14,
                                bold=big, fill=fill, stroke=stroke))
        y += rh + gap

    render(os.path.join(OUT, 'uffd-modes.svg'), W, H, *frags,
           title="Три режими: різні питання про ту саму сторінку")


# ── 4. Розкладка struct uffd_msg по байтах (до довідки інтерфейсу) ──────────
def fig_msg():
    lab_w, lab_x = 292, 40
    x0 = lab_x + lab_w + 30       # де починається байт 0
    bw = 34                       # ширина одного байта
    W = x0 + 32 * bw + 44
    rh, gap = 76, 18
    y0 = 128
    frags = []

    def bx(off):
        return x0 + off * bw

    frags.append(text(lab_x, y0 - 58, "Зміщення в байтах від початку повідомлення",
                      size=15, color=MUTED, anchor="start", bold=True))
    for off in range(0, 33, 4):
        frags.append(line(bx(off), y0 - 32, bx(off), y0 - 12, color=MUTED, sw=1))
        frags.append(text(bx(off), y0 - 38, str(off), size=13, color=MUTED))

    rows = []

    def row(y, label, label_fill, fields):
        frags.append(fitbox(lab_x, y, lab_w, rh, label, size=15, bold=True,
                            fill=label_fill))
        for off, n, name, fill in fields:
            frags.append(fitbox(bx(off), y, n * bw, rh, name, size=14,
                                fill=fill, rx=3))
        rows.append(y)

    y = y0
    row(y, "Спільний заголовок\n(є в кожному повідомленні)", HEAD,
        [(0, 8, "event — 1 байт,\nдалі 7 байтів заповнювача", "#eef2f7"),
         (8, 24, "arg — об'єднання на 24 байти:\nяку саме половину читати, каже event", FILL)])

    y += rh + gap + 16
    row(y, "event = UFFD_EVENT_PAGEFAULT\n(0x12)", WARM,
        [(8, 8, "arg.pagefault.flags\nWRITE · WP · MINOR", WARM),
         (16, 8, "arg.pagefault.address\nадреса, на якій спинилися", WARM),
         (24, 4, "feat.ptid\n(з THREAD_ID)", "#fdf9f2"),
         (28, 4, "—", "#f7f7f7")])

    y += rh + gap
    row(y, "event = UFFD_EVENT_FORK\n(0x13)", COLD,
        [(8, 4, "arg.fork.ufd", COLD),
         (12, 20, "—  решта байтів не заповнена", "#f7f7f7")])

    y += rh + gap
    row(y, "event = UFFD_EVENT_REMAP\n(0x14)", COLD,
        [(8, 8, "arg.remap.from\nстара адреса", COLD),
         (16, 8, "arg.remap.to\nнова адреса", COLD),
         (24, 8, "arg.remap.len\nдовжина", COLD)])

    y += rh + gap
    row(y, "event = UFFD_EVENT_REMOVE (0x15)\nі UFFD_EVENT_UNMAP (0x16)", COLD,
        [(8, 8, "arg.remove.start", COLD),
         (16, 8, "arg.remove.end\nмежа за останнім байтом", COLD),
         (24, 8, "—", "#f7f7f7")])

    # межа заголовка й об'єднання — наскрізь усіма рядками
    frags.append(line(bx(8), y0 - 8, bx(8), y + rh + 12,
                      color=MUTED, sw=1.5, dash="5,5"))

    H = y + rh + 76
    frags.append(text(lab_x, H - 26,
                      "Структура запакована (__packed): у read() віддають рівно 32 байти, "
                      "і цілу кількість повідомлень за раз.",
                      size=14, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'uffd-msg-layout.svg'), W, H, *frags,
           title="Розкладка struct uffd_msg: спільний заголовок і об'єднання")


# ── 5. Стани об'єкта: що дозволено на кожному кроці ─────────────────────────
def fig_states():
    W, H = 1380, 620
    frags = []

    bw, bh = 372, 104
    xs = [38, 504, 970]
    ytop = 118

    states = [
        ("Створено", "userfaultfd(2)\nабо USERFAULTFD_IOC_NEW", HEAD),
        ("Версію узгоджено", "після UFFDIO_API:\nвідомі features й ioctls", COLD),
        ("Діапазон під наглядом", "після UFFDIO_REGISTER:\nчерга наповнюється", WARM),
    ]
    for x, (name, sub, fill) in zip(xs, states):
        frags.append(rect(x, ytop, bw, bh, fill=fill, stroke=LINE))
        frags.append(mtext(x + bw / 2, ytop + 38, [name], size=19, bold=True))
        frags.append(mtext(x + bw / 2, ytop + 66, sub.split("\n"), size=14, color=MUTED))

    for i in range(2):
        x1 = xs[i] + bw + 8
        x2 = xs[i + 1] - 8
        frags.append(arrow(x1, ytop + bh / 2, x2, ytop + bh / 2))
        frags.append(mtext((x1 + x2) / 2, ytop + bh / 2 - 22,
                           ["UFFDIO_API" if i == 0 else "UFFDIO_REGISTER"],
                           size=14, bold=True, color=NEG))

    # що дозволено в кожному стані
    ay, ah = 282, 158
    allowed = [
        "Дозволено лише UFFDIO_API.\n\nБудь-який інший ioctl і навіть read()\nдають EINVAL — об'єкт ще не ввімкнено.",
        "UFFDIO_REGISTER, UFFDIO_UNREGISTER.\n\nПовторний UFFDIO_API — EINVAL,\nі поле api ядро затирає нулем.",
        "Те, що ядро дозволило в reg.ioctls:\nCOPY · ZEROPAGE · WAKE · WRITEPROTECT\nCONTINUE · POISON · MOVE.\nread() віддає uffd_msg.",
    ]
    for x, t in zip(xs, allowed):
        frags.append(fitbox(x, ay, bw, ah, t, size=14, fill=FILL))

    frags.append(text(38, ay - 22, "Що приймає ioctl у цьому стані",
                      size=15, color=MUTED, anchor="start", bold=True))

    # смуга з правилом порядку
    ny = ay + ah + 46
    frags.append(fitbox(38, ny, W - 76, 84,
                        "Порядок обов'язковий і незворотний: features узгоджують ДО першого повідомлення, "
                        "бо ввімкнені можливості змінюють сам потік подій у черзі —\n"
                        "наглядач, який не просив EVENT_FORK, прочитає таке повідомлення як зіпсоване.",
                        size=15, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'uffd-states.svg'), W, H, *frags,
           title="Стани об'єкта userfaultfd і дозволені на кожному кроці операції")


# ── 6. Розклад одного кола в часі (до вставки proj-uffd-lazy-region) ────────
def fig_round_time():
    W, H = 1270, 520
    frags = []

    T0, T1 = 300.0, 1180.0          # t = 0 і t = 28.6 мкс
    k = (T1 - T0) / 28.6

    def X(t):
        return T0 + t * k

    y_vic, h_vic = 90, 58
    y_ker, h_ker = 186, 44
    y_wat, h_wat = 282, 58

    # ── потік-винуватець ───────────────────────────────────────────────
    frags.append(text(30, y_vic + h_vic / 2 + 5, "потік-винуватець",
                      size=15, bold=True, anchor="start"))
    frags.append(fitbox(200, y_vic, 100, h_vic, "звернення\nза адресою",
                        size=12, fill=WARM))
    frags.append(fitbox(T0, y_vic, T1 - T0, h_vic,
                        "спить у ядрі — 26.5 мкс непереривного сну",
                        size=15, fill="#eeeeee"))
    frags.append(fitbox(T1, y_vic, 90, h_vic, "інструкція\nнаново",
                        size=12, fill=WARM))

    # ── ядро й планувальник ────────────────────────────────────────────
    frags.append(text(30, y_ker + h_ker / 2 + 5, "ядро",
                      size=15, bold=True, anchor="start"))
    frags.append(rect(T0, y_ker, T1 - T0, h_ker, fill="#fafbfc"))
    frags.append(fitbox(T0, y_ker, X(2.1) - T0, h_ker, "2.1", size=13, fill=COLD))
    frags.append(fitbox(X(26.5), y_ker, T1 - X(26.5), h_ker, "2.1", size=13, fill=COLD))
    frags.append(text((X(2.1) + X(26.5)) / 2, y_ker + h_ker / 2 + 5,
                      "розбудити наглядача (2.1) · розбудити винуватця (2.1) — більше ядро тут нічого не робить",
                      size=14, color=MUTED))

    # ── потік-наглядач ─────────────────────────────────────────────────
    frags.append(text(30, y_wat + h_wat / 2 + 5, "потік-наглядач",
                      size=15, bold=True, anchor="start"))
    frags.append(fitbox(200, y_wat, X(2.1) - 200, h_wat, "спить у poll",
                        size=13, fill="#eeeeee"))
    frags.append(fitbox(X(2.1), y_wat, X(21.9) - X(2.1), h_wat,
                        "вироблення вмісту: 16 сторінок · 19.8 мкс",
                        size=15, fill=WARM))
    frags.append(fitbox(X(21.9), y_wat, X(26.5) - X(21.9), h_wat,
                        "UFFDIO_COPY\n4.6 мкс", size=13, fill=COLD))
    frags.append(fitbox(X(26.5), y_wat, 90, h_wat, "назад\nу poll", size=12,
                        fill="#eeeeee"))

    # ── дужка «повне коло» ─────────────────────────────────────────────
    yb = 378
    frags.append(line(T0, yb - 10, T0, yb))
    frags.append(line(T1, yb - 10, T1, yb))
    frags.append(line(T0, yb, T1, yb))
    frags.append(text((T0 + T1) / 2, yb + 26,
                      "повне коло, що його бачить винуватець — 28.6 мкс", size=16, bold=True))

    frags.append(fitbox(200, 428, 990, 68,
                        "Механізмові з цих 28.6 мкс належать 4.2 — два перепланування.\n"
                        "Решта — робота, яку програма робила б у будь-якому разі.",
                        size=15, fill="#fdecea", stroke=POS))

    render(os.path.join(OUT, 'uffd-round-time.svg'), W, H, *frags,
           title="Куди йде час одного кола: пакет із 16 сторінок")


if __name__ == '__main__':
    fig_loop()
    fig_atomic()
    fig_modes()
    fig_msg()
    fig_states()
    fig_round_time()
    print("ok")
