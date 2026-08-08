# -*- coding: utf-8 -*-
"""Фігури до теми «io_uring: кільця подань і завершень»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_two_rings():
    """Два кільця у спільній пам'яті: хто рухає голову, а хто — хвіст."""
    W, H = 900, 400
    g = []

    # смуги «хто з якого боку»
    g.append(fitbox(20, 20, 860, 42, "програма (простір користувача)",
                    size=14, bold=True, fill="#eef2f7"))
    g.append(fitbox(20, 330, 860, 42, "ядро", size=14, bold=True, fill="#eef2f7"))

    # панель спільної пам'яті
    g.append(rect(40, 140, 830, 100, fill="#fbfcfd", stroke=MUTED, sw=1.2))

    # назви кілець
    g.append(text(120, 162, "кільце подань SQ", size=13, bold=True))
    g.append(text(740, 162, "кільце завершень CQ", size=13, bold=True))

    # комірки
    sq = ["#7", "#8", "", "", ""]
    cq = ["#3", "#5", "", "", ""]
    for i, s in enumerate(sq):
        x = 60 + i * 72
        g.append(fitbox(x, 176, 66, 44, s, size=13,
                        fill="#eef2f7" if s else BG))
    for i, s in enumerate(cq):
        x = 480 + i * 72
        g.append(fitbox(x, 176, 66, 44, s, size=13,
                        fill="#eaf7ee" if s else BG))

    # програма: пише в хвіст SQ (комірка 2), читає з голови CQ (комірка 0)
    g.append(arrow(237, 64, 237, 174))
    g.append(text(250, 95, "кладе SQE, посуває хвіст", size=12, anchor="start"))
    g.append(arrow(513, 174, 513, 64))
    g.append(text(502, 125, "забирає CQE, посуває голову", size=12, anchor="end"))

    # ядро: читає з голови SQ (комірка 0), пише в хвіст CQ (комірка 2)
    g.append(arrow(93, 222, 93, 328))
    g.append(text(106, 272, "ядро бере від голови", size=12, anchor="start"))
    g.append(arrow(657, 328, 657, 222))
    g.append(text(644, 272, "ядро дописує в хвіст", size=12, anchor="end"))

    render(os.path.join(IMG, 'two-rings.svg'), W, H, *g)


def fig_three_fates():
    """Три долі поданого SQE всередині ядра."""
    W, H = 920, 310
    g = []

    g.append(text(120, 42, "стан операції", size=12, bold=True))
    g.append(text(400, 42, "що робить ядро", size=12, bold=True))
    g.append(text(745, 42, "коли з'явиться CQE", size=12, bold=True))

    rows = [
        (60, "дані вже готові",
         "виконує на місці, у контексті виклику",
         "ще до повернення\nз io_uring_enter", "#eaf7ee"),
        (140, "сокет ще без даних",
         "ставить чекання в чергу\nочікування цього сокета",
         "коли драйвер\nрозбудить чергу", "#eef2f7"),
        (220, "операція таки заблокує\n(читання повз кеш)",
         "віддає робітникові io-wq —\nспить потік ядра, не ваш",
         "коли робітник\nдочитає", "#fdecea"),
    ]
    for y, a, b, c, col in rows:
        cy = y + 31
        g.append(fitbox(30, y, 180, 62, a, size=12, fill=col))
        g.append(fitbox(230, y, 340, 62, b, size=12))
        g.append(fitbox(600, y, 290, 62, c, size=12))
        g.append(arrow(212, cy, 226, cy))
        g.append(arrow(572, cy, 596, cy))

    render(os.path.join(IMG, 'three-fates.svg'), W, H, *g)


def fig_buffer_ownership():
    """Кому належить буфер: read() проти io_uring."""
    W, H = 820, 320
    g = []

    g.append(text(40, 68, "read()", size=13, anchor="start", bold=True))
    g.append(line(220, 64, 440, 64, color=POS, sw=1.4))
    g.append(text(330, 54, "ядро тримає буфер", size=12, color=POS))
    g.append(fitbox(40, 80, 160, 44, "буфер готовий", size=12))
    g.append(fitbox(220, 80, 220, 44, "read(): ядро пише в буфер", size=12, fill="#fdecea"))
    g.append(fitbox(460, 80, 200, 44, "повернувся — буфер ваш", size=12, fill="#eaf7ee"))

    g.append(text(40, 188, "io_uring", size=13, anchor="start", bold=True))
    g.append(line(220, 184, 700, 184, color=POS, sw=1.4))
    g.append(text(460, 174, "ядро тримає буфер увесь цей час", size=12, color=POS))
    g.append(fitbox(40, 200, 160, 44, "буфер готовий", size=12))
    g.append(fitbox(220, 200, 150, 44, "SQE подано", size=12, fill="#fdecea"))
    g.append(fitbox(390, 200, 210, 44, "потік робить інше", size=12, fill="#fdecea"))
    g.append(fitbox(620, 200, 160, 44, "прийшов CQE", size=12, fill="#eaf7ee"))

    g.append(fitbox(40, 262, 740, 42,
                    "звільнити або перевикористати буфер раніше за CQE — "
                    "це запис ядра в чужу пам'ять", size=12, fill="#fdecea"))

    render(os.path.join(IMG, 'buffer-ownership.svg'), W, H, *g)


def fig_mmap_layout():
    """Три відображення кільця: яке зміщення що відкриває."""
    W, H = 940, 430
    g = []

    cols = [
        (30, 250, "#eef2f7",
         "IORING_OFF_SQ_RING\n0",
         ["head, tail — лічильники",
          "ring_mask, ring_entries",
          "flags — NEED_WAKEUP тощо",
          "dropped — відкинуті SQE",
          "array[] — індекси в масив SQE"]),
        (345, 250, "#eaf7ee",
         "IORING_OFF_CQ_RING\n0x8000000",
         ["head, tail — лічильники",
          "ring_mask, ring_entries",
          "overflow — скільки переповнень",
          "flags",
          "cqes[] — самі CQE, по 16 Б"]),
        (660, 250, "#fdf3e6",
         "IORING_OFF_SQES\n0x10000000",
         ["sqes[] — самі SQE, по 64 Б",
          "(зі SQE128 — по 128 Б)",
          "не кільце, а масив:",
          "комірку обирає програма,",
          "кільце зберігає лише індекс"]),
    ]

    for x, w, col, head, rows in cols:
        g.append(fitbox(x, 26, w, 54, head, size=13, bold=True, fill=col))
        for i, r in enumerate(rows):
            g.append(fitbox(x, 100 + i * 46, w, 40, r, size=12))

    g.append(fitbox(30, 330, 880, 66,
                    "IORING_FEAT_SINGLE_MMAP (ядро 5.4): перші два відображення роблять "
                    "ОДНИМ mmap — на більший із двох розмірів;\n"
                    "зміщення полів усередині відображення дає ядро в p.sq_off і p.cq_off",
                    size=12, fill="#fbfcfd"))

    render(os.path.join(IMG, 'mmap-layout.svg'), W, H, *g)


def fig_provided_buffer_life():
    """Життя одного наданого буфера в ехо-сервері."""
    W, H = 980, 350
    g = []

    g.append(text(490, 44, "життя одного буфера з групи наданих",
                  size=13, bold=True))

    xs = [20, 215, 410, 605, 800]
    bw, bh, by = 160, 78, 128
    stages = [
        ("у кільці наданих:\nвільний", "#eaf7ee"),
        ("ядро само взяло\nйого під recv", "#fdecea"),
        ("CQE приніс дані\nй номер flags >> 16", "#fdecea"),
        ("send читає з нього,\nдоки left > 0", "#fdecea"),
        ("buf_ring_add:\nповернули в кільце", "#eaf7ee"),
    ]
    for x, (s, col) in zip(xs, stages):
        g.append(fitbox(x, by, bw, bh, s, size=12, fill=col))
    for x in xs[:-1]:
        g.append(arrow(x + bw + 6, by + bh / 2, x + bw + 48, by + bh / 2))

    g.append(line(215, 108, 765, 108, color=POS, sw=1.6))
    g.append(text(490, 96, "увесь цей час буфер належить ядру", size=12, color=POS))

    g.append(fitbox(20, 236, 940, 44,
                    "повернути буфер раніше за CQE від send — це віддати ядру пам'ять, "
                    "у яку воно ще пише", size=12, fill="#fdecea"))
    g.append(fitbox(20, 292, 940, 44,
                    "res = −ENOBUFS означає, що вільного буфера не було: "
                    "recv не відбувся, з'єднання чекає на чужий повернений буфер",
                    size=12, fill="#eef2f7"))

    render(os.path.join(IMG, 'provided-buffer-life.svg'), W, H, *g)


def fig_send_ordering():
    """Чому на з'єднання тримають рівно одну операцію в польоті."""
    W, H = 920, 300
    g = []

    g.append(text(460, 36, "порядок байтів у відповіді залежить від того, "
                           "скільки send у польоті", size=13, bold=True))

    g.append(fitbox(20, 62, 250, 70,
                    "два recv підряд —\nдва send подано разом", size=12, fill="#fdecea"))
    g.append(arrow(276, 97, 314, 97))
    g.append(fitbox(320, 62, 270, 70,
                    "ядро виконує їх незалежно:\nдругий може випередити перший",
                    size=12))
    g.append(arrow(596, 97, 634, 97))
    g.append(fitbox(640, 62, 260, 70,
                    "на дроті «CDAB» —\nехо зіпсовано", size=12, fill="#fdecea"))

    g.append(fitbox(20, 162, 250, 70,
                    "один recv, один send:\nнаступний — лише після CQE",
                    size=12, fill="#eaf7ee"))
    g.append(arrow(276, 197, 314, 197))
    g.append(fitbox(320, 162, 270, 70,
                    "у польоті завжди рівно\nодна операція на з'єднання", size=12))
    g.append(arrow(596, 197, 634, 197))
    g.append(fitbox(640, 162, 260, 70,
                    "на дроті «ABCD» —\nпорядок збережено", size=12, fill="#eaf7ee"))

    g.append(fitbox(20, 250, 880, 40,
                    "паралельність кільця дає кількість з'єднань, "
                    "а не кількість операцій на одному з'єднанні",
                    size=12, fill="#eef2f7"))

    render(os.path.join(IMG, 'send-ordering.svg'), W, H, *g)


if __name__ == '__main__':
    fig_two_rings()
    fig_three_fates()
    fig_buffer_ownership()
    fig_mmap_layout()
    fig_provided_buffer_life()
    fig_send_ordering()
    print("ok")
