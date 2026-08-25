# -*- coding: utf-8 -*-
"""Фігури до теми «Готовність проти завершення: дві моделі вводу-виводу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_two_questions():
    """Хто виконує копіювання і скільки разів перетинається межа ядра."""
    W, H = 1000, 430
    g = []

    # ── смуга «готовність» ─────────────────────────────────────────────
    g.append(text(30, 40, "готовність", size=15, anchor="start", bold=True, color=NEG))
    g.append(text(30, 60, "«коли можна?»", size=12, anchor="start", color=MUTED))

    g.append(fitbox(210, 30, 176, 62, "epoll_wait()\nпотік спить", size=12, fill=FILL))
    g.append(fitbox(402, 30, 176, 62, "подія:\nfd 7 читабельний", size=12, fill="#eef2f7"))
    g.append(fitbox(594, 30, 190, 62, "read(7, buf, 4096)\nкопіює цей виклик", size=12,
                    fill="#fdecea", stroke=POS))
    g.append(fitbox(800, 30, 172, 62, "1300 байтів\nуже в buf", size=12,
                    fill="#eaf7ee", stroke=FIELD))

    for x0, x1 in ((386, 402), (578, 594), (784, 800)):
        g.append(arrow(x0, 61, x1, 61, color=MUTED, sw=1.4))

    g.append(fitbox(210, 104, 762, 34,
                    "два входи в ядро на одну прочитану порцію: спитати про стан і забрати дані",
                    size=12, fill="#f7f3e8", stroke=MUTED))

    # ── смуга «завершення» ─────────────────────────────────────────────
    g.append(text(30, 210, "завершення", size=15, anchor="start", bold=True, color=FIELD))
    g.append(text(30, 230, "«зроби і скажи»", size=12, anchor="start", color=MUTED))

    g.append(fitbox(210, 200, 176, 62, "подання:\nread(7, buf, #17)", size=12, fill=FILL))
    g.append(fitbox(402, 200, 176, 62, "програма зайнята\nіншими справами", size=12,
                    fill="#eef2f7"))
    g.append(fitbox(594, 200, 190, 62, "ядро копіює само,\nколи дані прийшли", size=12,
                    fill="#fdecea", stroke=POS))
    g.append(fitbox(800, 200, 172, 62, "подія #17:\n1300, дані в buf", size=12,
                    fill="#eaf7ee", stroke=FIELD))

    for x0, x1 in ((386, 402), (578, 594), (784, 800)):
        g.append(arrow(x0, 231, x1, 231, color=MUTED, sw=1.4))

    g.append(fitbox(210, 274, 762, 34,
                    "один вхід у ядро на подання, а результат забирають зі спільної пам'яті",
                    size=12, fill="#f7f3e8", stroke=MUTED))

    # ── підсумок ───────────────────────────────────────────────────────
    g.append(fitbox(30, 336, 942, 66,
                    "різниця не в тому, хто швидший, а в тому, ХТО ВИКОНУЄ ПЕРЕНЕСЕННЯ БАЙТІВ:\n"
                    "у першій моделі — сама програма, окремим викликом; у другій — ядро, "
                    "у момент, який програма не обирає",
                    size=13, fill="#eef2f7", stroke=NEG))

    render(os.path.join(IMG, 'two-questions.svg'), W, H, *g,
           title="Два різні запитання до ядра")


def fig_buffer_ownership():
    """Кому належить буфер у кожен момент і де лежить небезпечна ділянка."""
    W, H = 1000, 400
    g = []

    AX, AW = 250, 700          # вісь часу

    g.append(text(AX + AW / 2, 26, "час →", size=12, color=MUTED))

    # ── готовність ─────────────────────────────────────────────────────
    g.append(fitbox(24, 44, 200, 66, "готовність\nбуфер віддають\nна мить виклику",
                    size=12, fill=FILL, stroke=NEG))
    g.append(fitbox(AX, 44, 300, 66, "буфер вільний:\nможна звільнити, віддати іншому",
                    size=12, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(AX + 310, 44, 110, 66, "read()", size=12, fill="#fdecea", stroke=POS))
    g.append(fitbox(AX + 430, 44, 270, 66, "буфер знову вільний:\nдані вже прочитані",
                    size=12, fill="#eaf7ee", stroke=FIELD))
    g.append(mtext(AX + 365, 130, ["ядро торкається буфера", "лічені мікросекунди"],
                   size=11, color=MUTED))

    # ── завершення ─────────────────────────────────────────────────────
    g.append(fitbox(24, 200, 200, 66, "завершення\nбуфер позичають\nна всю операцію",
                    size=12, fill=FILL, stroke=FIELD))
    g.append(fitbox(AX, 200, 150, 66, "буфер\nвільний", size=12, fill="#eaf7ee", stroke=FIELD))
    g.append(fitbox(AX + 160, 200, 400, 66,
                    "буфер належить ядру: не звільняти, не перезаписувати,\n"
                    "дескриптор не закривати", size=12, fill="#fdecea", stroke=POS))
    g.append(fitbox(AX + 570, 200, 130, 66, "буфер\nповернуто", size=12,
                    fill="#eaf7ee", stroke=FIELD))

    g.append(text(AX + 170, 186, "подання", size=11, anchor="start", color=MUTED))
    g.append(text(AX + 550, 186, "подія завершення", size=11, anchor="end", color=MUTED))
    g.append(arrow(AX + 165, 190, AX + 165, 198, color=MUTED, sw=1.2))
    g.append(arrow(AX + 555, 190, AX + 555, 198, color=MUTED, sw=1.2))

    g.append(fitbox(24, 300, 946, 74,
                    "звідси вся арифметика пам'яті: у першій моделі одного буфера "
                    "вистачає на всі з'єднання потоку,\n"
                    "у другій потрібен окремий буфер на кожну операцію, що зараз у польоті",
                    size=13, fill="#eef2f7", stroke=NEG))

    render(os.path.join(IMG, 'buffer-ownership.svg'), W, H, *g,
           title="Кому належить буфер у кожен момент")


def fig_readiness_coverage():
    """Де готовність узагалі має що повідомляти, а де такого стану немає."""
    W, H = 1010, 430
    g = []

    g.append(text(250, 30, "є стан «поки нічого немає»", size=14, bold=True, color=FIELD))
    g.append(text(760, 30, "такого стану не існує", size=14, bold=True, color=POS))

    has = [
        "сокет: буфер прийому буває порожній",
        "канал і FIFO",
        "термінал і послідовний порт",
        "eventfd, timerfd, signalfd, inotify",
    ]
    hasnt = [
        "звичайний файл: він «готовий» завжди,\nа читання все одно чекає на носій",
        "блоковий пристрій",
        "сторінковий збій на відображеному файлі",
        "open, stat, rename — операції над метаданими",
        "розв'язання доменного імені",
    ]

    y = 58
    for s in has:
        g.append(fitbox(30, y, 430, 54, s, size=12, fill="#eaf7ee", stroke=FIELD))
        y += 64

    y = 58
    for s in hasnt:
        g.append(fitbox(530, y, 450, 54, s, size=12, fill="#fdecea", stroke=POS))
        y += 64

    g.append(fitbox(30, 356, 950, 60,
                    "модель завершення покриває обидва стовпці, бо ставить ядру не питання "
                    "«чи можна вже»,\nа замовлення «зроби» — на яке відповідь є завжди",
                    size=13, fill="#eef2f7", stroke=NEG))

    render(os.path.join(IMG, 'readiness-coverage.svg'), W, H, *g,
           title="Де готовність має що повідомляти")


if __name__ == '__main__':
    fig_two_questions()
    fig_buffer_ownership()
    fig_readiness_coverage()
    print("ok")
