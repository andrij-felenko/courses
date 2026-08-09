# -*- coding: utf-8 -*-
"""Фігури до теми «Пріоритет вводу-виводу: класи ionice та ioprio_set»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED = "#fdecea"
GRN = "#eaf7ee"
BLU = "#eef2f7"


def fig_ioprio_word():
    """Розкладка числа на поля і три класи як три різні політики."""
    W, H = 1000, 470
    g = []

    g.append(text(500, 34, "одне 16-бітове число — два різні за змістом поля",
                  size=14, bold=True))

    # смуга бітів
    g.append(fitbox(40, 56, 210, 54, "клас", size=14, bold=True, fill=BLU))
    g.append(fitbox(258, 56, 462, 54, "підказка", size=14, bold=True, fill=BG))
    g.append(fitbox(728, 56, 232, 54, "рівень", size=14, bold=True, fill=GRN))

    g.append(fitbox(40, 122, 210, 46, "біти 15–13\n8 значень, вжито 3", size=11))
    g.append(fitbox(258, 122, 462, 46,
                    "біти 12–3 · від ядра 6.5 — обмеження тривалості команди;\n"
                    "порядку обслуговування не змінює", size=11))
    g.append(fitbox(728, 122, 232, 46, "біти 2–0\n0 — найвищий, 7 — найнижчий", size=11))

    g.append(text(500, 204,
                  "клас задає ВИД політики, рівень — частку всередині неї",
                  size=13, bold=True))

    boxes = [
        (40, "IOPRIO_CLASS_RT = 1", "обслуговують першими,\nзавжди й поперед усіх", RED),
        (348, "IOPRIO_CLASS_BE = 2", "звичайна частка черги\nза рівнем 0–7", BLU),
        (656, "IOPRIO_CLASS_IDLE = 3", "лише коли черга порожня;\nрівень тут не діє", GRN),
    ]
    for x, head, body, col in boxes:
        g.append(fitbox(x, 222, 304, 34, head, size=13, bold=True, fill=col))
        g.append(fitbox(x, 258, 304, 62, body, size=12, fill=BG))

    g.append(fitbox(40, 344, 920, 46,
                    "IOPRIO_PRIO_VALUE(2, 7)  =  (2 << 13) | 7  =  16391",
                    size=14, bold=True, fill=BG))

    g.append(fitbox(40, 404, 920, 46,
                    "клас 0 (NONE) — позначка «не задавали»: рівень ядро бере з nice, "
                    "клас вважає best-effort",
                    size=12, fill=GRN))

    render(os.path.join(IMG, 'ioprio-word.svg'), W, H, *g)


def fig_ioprio_path():
    """Шлях числа від потоку до пристрою й три місця втрати."""
    W, H = 1020, 580
    g = []

    g.append(text(510, 34, "куди їде число — і де воно зникає", size=14, bold=True))

    chain = [
        (66, "потік із заданим ioprio"),
        (154, "read(): запит подає\nсам цей потік"),
        (242, "bio несе клас і рівень\nна собі"),
        (330, "планувальник черги\nупорядковує запити"),
        (418, "пристрій"),
    ]
    for y, s in chain:
        g.append(fitbox(40, y, 290, 60, s, size=12, fill=BLU))
    for y in (126, 214, 302, 390):
        g.append(arrow(185, y, 185, y + 28))

    losses = [
        (150, "буферизований запис сюди не заходить: сторінки бруднить ваш потік,\n"
              "а запит подає потік зворотного запису — зі своїм пріоритетом"),
        (238, "device-mapper, RAID, loop, мережеві ФС: запит перекладає потік ядра,\n"
              "і початкове число далі не їде"),
        (326, "планувальник none просто передає запити далі —\n"
              "число не читає ніхто (типово для NVMe)"),
    ]
    for y, s in losses:
        g.append(fitbox(400, y, 580, 68, s, size=12, fill=RED))
        g.append(arrow(396, y + 34, 336, y + 34, color=POS))

    g.append(fitbox(40, 500, 940, 54,
                    "пріоритет діє лише там, де ВОДНОЧАС є затор у черзі "
                    "і планувальник, який число читає",
                    size=13, bold=True, fill=GRN))

    render(os.path.join(IMG, 'ioprio-path.svg'), W, H, *g)


def fig_two_schedulers():
    """Як те саме число читають mq-deadline і BFQ."""
    W, H = 1020, 450
    g = []

    g.append(fitbox(30, 30, 460, 40, "mq-deadline: список на кожен клас",
                    size=13, bold=True, fill=BLU))
    g.append(fitbox(530, 30, 460, 40, "BFQ: черга на кожен процес, рівень — вага",
                    size=13, bold=True, fill=BLU))

    left = [
        ("RT — беруть, поки є", RED),
        ("BE — коли RT порожній", BG),
        ("IDLE — коли порожні обидва", GRN),
    ]
    for i, (s, col) in enumerate(left):
        g.append(fitbox(40, 88 + i * 52, 440, 42, s, size=12, fill=col))

    right = [
        ("процес A · BE рівень 0  →  вага 8", RED),
        ("процес B · BE рівень 4  →  вага 4", BG),
        ("процес C · BE рівень 7  →  вага 1", GRN),
    ]
    for i, (s, col) in enumerate(right):
        g.append(fitbox(540, 88 + i * 52, 440, 42, s, size=12, fill=col))

    g.append(fitbox(40, 256, 440, 96,
                    "рівень усередині класу не розрізняється зовсім;\n"
                    "запобіжник від засухи — prio_aging_expire,\n"
                    "типово 10 с: після нього пускають і нижчих",
                    size=12, fill=BG))
    g.append(fitbox(540, 256, 440, 96,
                    "клас усе одно суворо старший за клас,\n"
                    "а вага ділить смугу всередині класу\n"
                    "в довгій перспективі, а не запит за запитом",
                    size=12, fill=BG))

    g.append(fitbox(40, 376, 940, 50,
                    "ionice -c 2 -n 0 проти -c 2 -n 7: ліворуч різниці немає, "
                    "праворуч вона відчутна",
                    size=13, bold=True, fill=GRN))

    render(os.path.join(IMG, 'two-schedulers.svg'), W, H, *g)


if __name__ == '__main__':
    fig_ioprio_word()
    fig_ioprio_path()
    fig_two_schedulers()
    print("ok")
