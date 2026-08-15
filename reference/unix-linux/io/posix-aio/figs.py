# -*- coding: utf-8 -*-
"""Фігури до теми «POSIX AIO: стандартний інтерфейс aio_*»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_request_life():
    """Життя одного запиту: чия пам'ять зайнята і як дізнаються про кінець."""
    W, H = 1020, 470
    g = []

    # ── смуга подій ────────────────────────────────────────────────────
    boxes = [
        (40, 220, "aio_read(&cb)\nповертається одразу"),
        (290, 210, "aio_error(&cb)\n= EINPROGRESS"),
        (530, 220, "операція скінчилась\nдесь усередині"),
        (790, 190, "aio_return(&cb)\nрезультат і звільнення"),
    ]
    for x, w, s in boxes:
        g.append(fitbox(x, 62, w, 62, s, size=13, fill=FILL))
    for x0, x1 in ((260, 290), (500, 530), (750, 790)):
        g.append(arrow(x0, 93, x1, 93, color=MUTED, sw=1.6))

    # ── смуга власності пам'яті ────────────────────────────────────────
    g.append(fitbox(40, 152, 940, 60,
                    "увесь цей час aiocb, буфер і дескриптор належать реалізації:\n"
                    "не звільняти, не перезаписувати, не закривати, не подавати вдруге",
                    size=13, fill="#fdecea", stroke=POS))

    # ── три способи дізнатися ──────────────────────────────────────────
    g.append(text(40, 254, "три способи дізнатися, що запит скінчився",
                 size=14, anchor="start", bold=True, color=NEG))

    ways = [
        (40, 296, "опитування",
         "aio_error() у циклі:\nпросто, але марно\nпалить процесор"),
        (356, 296, "чекання",
         "aio_suspend(list, n, t):\nсон до першого\nзавершення зі списку"),
        (672, 308, "сповіщення",
         "aio_sigevent:\nсигнал або виклик\nфункції в новому потоці"),
    ]
    for x, w, head, body in ways:
        g.append(fitbox(x, 272, w, 32, head, size=13, fill="#eef2f7", stroke=NEG, bold=True))
        g.append(fitbox(x, 312, w, 78, body, size=12, fill=FILL))

    g.append(fitbox(40, 404, 940, 40,
                    "результат бере лише aio_return, і лише один раз: не забрати — лишити запит незакритим",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    render(os.path.join(IMG, 'request-life.svg'), W, H, *g,
           title="Один запит aio: від подання до забирання результату")


def fig_glibc_inside():
    """Що насправді стоїть за aio_read у Linux: черги дескрипторів і пул потоків."""
    W, H = 1040, 500
    g = []

    g.append(fitbox(40, 60, 220, 96,
                    "програма\n64 виклики aio_read()\nна три дескриптори",
                    size=13, fill="#eef2f7", stroke=NEG))

    rows = [
        (72,  "черга дескриптора 3\n60 запитів"),
        (152, "черга дескриптора 4\n3 запити"),
        (232, "черга дескриптора 7\n1 запит"),
    ]
    for y, s in rows:
        g.append(fitbox(330, y, 250, 58, s, size=12, fill=FILL))

    workers = [
        (72,  "робітник 1\npread(3, …) спить"),
        (152, "робітник 2\npread(4, …) спить"),
        (232, "робітник 3\npread(7, …) спить"),
    ]
    for y, s in workers:
        g.append(fitbox(690, y, 250, 58, s, size=12, fill="#f7f3e8", stroke=MUTED))

    for y in (101, 181, 261):
        g.append(arrow(580, y, 690, y, color=MUTED, sw=1.6))
    g.append(arrow(260, 108, 330, 101, color=MUTED, sw=1.6))
    g.append(arrow(260, 118, 330, 181, color=MUTED, sw=1.6))
    g.append(arrow(260, 128, 330, 261, color=MUTED, sw=1.6))

    g.append(fitbox(40, 320, 460, 66,
                    "запити одного дескриптора виконує\nодин робітник, суворо по черзі",
                    size=13, fill="#fdecea", stroke=POS))
    g.append(fitbox(540, 320, 460, 66,
                    "пул за замовчуванням — 20 потоків;\n21-й запит просто чекає, помилки немає",
                    size=13, fill="#fdecea", stroke=POS))

    g.append(fitbox(40, 410, 960, 48,
                    "системного виклику aio_read у Linux не існує: під сподом звичайні pread, pwrite і fsync",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    render(os.path.join(IMG, 'glibc-inside.svg'), W, H, *g,
           title="Фасад aio_* у Linux: черги за дескрипторами й пул потоків у glibc")


if __name__ == '__main__':
    fig_request_life()
    fig_glibc_inside()
    print("ok")
