# -*- coding: utf-8 -*-
"""Фігури до теми «Канали й іменовані канали»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_pipe_ring():
    """Кільце сторінок: де голова, де хвіст і де кожен кінець засинає."""
    W, H = 960, 372
    g = []

    X0, CW, CH, CY = 64, 48, 58, 96
    N, FILLED = 16, 6

    for i in range(N):
        x = X0 + i * CW
        fill = "#eef2f7" if i < FILLED else BG
        g.append(rect(x, CY, CW, CH, fill=fill, stroke=LINE, sw=1.2, rx=2))

    g.append(text(X0, 44, "хвіст: звідси забирає read()",
                  size=12, anchor="start", color=NEG))
    g.append(arrow(X0, 54, X0, CY - 4, color=NEG, sw=1.4))

    XW = X0 + FILLED * CW
    g.append(text(XW + 12, 44, "голова: сюди кладе write()",
                  size=12, anchor="start", color=POS))
    g.append(arrow(XW, 54, XW, CY - 4, color=POS, sw=1.4))

    g.append(text(X0 + FILLED * CW / 2, CY + CH + 20,
                  "дані", size=12, color=MUTED))
    g.append(text(XW + (N - FILLED) * CW / 2, CY + CH + 20,
                  "вільне місце", size=12, color=MUTED))

    XE = X0 + N * CW
    g.append(line(XE, CY + CH, XE, CY + CH + 42, color=MUTED, sw=1.2, dash="4,4"))
    g.append(line(XE, CY + CH + 42, X0, CY + CH + 42, color=MUTED, sw=1.2, dash="4,4"))
    g.append(arrow(X0, CY + CH + 42, X0, CY + CH + 4, color=MUTED, sw=1.2))
    g.append(text(X0 + N * CW / 2, CY + CH + 62,
                  "за останньою сторінкою знову перша: 16 сторінок по 4096 Б = 65536 Б",
                  size=12, color=MUTED))

    g.append(fitbox(64, 236, 396, 58,
                    "кільце повне —\nwrite() засинає, доки читач не забере",
                    size=13, fill="#fdecea", stroke=POS))
    g.append(fitbox(496, 236, 396, 58,
                    "кільце порожнє —\nread() засинає, доки записувач не покладе",
                    size=13, fill="#eef2f7", stroke=NEG))

    g.append(fitbox(64, 306, 828, 46,
                    "обидві зупинки виникають самі, зі скінченности буфера — "
                    "швидка ланка конвеєра сповільнюється до темпу повільної",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    render(os.path.join(IMG, 'pipe-ring.svg'), W, H, *g,
           title="Кільце сторінок каналу й дві точки засинання")


def fig_pipeline_wiring():
    """Що робить оболонка з дескрипторами, збираючи ls | wc -l."""
    W, H = 980, 396
    g = []

    g.append(fitbox(30, 26, 920, 46,
                    "pipe(fd) створює один об'єкт із двома кінцями; після двох fork "
                    "на кожен кінець існує по три дескриптори —\n"
                    "по одному в оболонці та в кожній дитині",
                    size=13, fill="#eef2f7", stroke=MUTED))

    C1, W1 = 30, 176
    C2, W2 = 218, 340
    C3, W3 = 570, 380

    for x, w, s in ((C1, W1, "процес"),
                    (C2, W2, "що ставить на місце стандартного потоку"),
                    (C3, W3, "які копії закриває")):
        g.append(fitbox(x, 92, w, 42, s, size=13, bold=True, fill="#f7f3e8"))

    rows = [
        (146, "ls", "dup2(fd[1], 1)\nвивід іде в канал",
         "fd[0] і fd[1] — обидві успадковані копії"),
        (212, "wc -l", "dup2(fd[0], 0)\nввід іде з каналу",
         "fd[0] і fd[1] — обидві успадковані копії"),
        (278, "оболонка", "нічого не читає й не пише",
         "fd[0] і fd[1] — інакше кінців на запис\nлишиться один назавжди"),
    ]
    for y, a, b, c in rows:
        g.append(fitbox(C1, y, W1, 56, a, size=13))
        g.append(fitbox(C2, y, W2, 56, b, size=12))
        g.append(fitbox(C3, y, W3, 56, c, size=12, fill="#eef2f7"))

    g.append(fitbox(30, 344, 920, 46,
                    "жодна з двох програм не змінена й не знає про канал: "
                    "обидві просто працюють із дескрипторами 0 і 1",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    render(os.path.join(IMG, 'pipeline-wiring.svg'), W, H, *g,
           title="Як оболонка зшиває ls | wc -l")


def fig_refcount_ends():
    """Два лічильники відкритих кінців і наслідки їхнього обнулення."""
    W, H = 960, 356
    g = []

    g.append(fitbox(40, 26, 880, 42,
                    "поки обидва лічильники більші за нуль: read() чекає на дані, "
                    "write() чекає на місце",
                    size=13, fill="#f7f3e8", stroke=MUTED))

    g.append(fitbox(40, 92, 420, 46, "кінців на запис лишилося 0",
                    size=14, bold=True, fill="#eef2f7", stroke=NEG))
    g.append(arrow(250, 142, 250, 168, color=NEG, sw=1.6))
    g.append(fitbox(40, 172, 420, 48, "read() повертає 0 — кінець даних",
                    size=13, fill=BG, stroke=NEG))
    g.append(fitbox(40, 232, 420, 62,
                    "не тому, що записувач попрощався,\n"
                    "а тому, що написати вже фізично нема кому",
                    size=12, fill="#eef2f7"))

    g.append(fitbox(500, 92, 420, 46, "кінців на читання лишилося 0",
                    size=14, bold=True, fill="#fdecea", stroke=POS))
    g.append(arrow(710, 142, 710, 168, color=POS, sw=1.6))
    g.append(fitbox(500, 172, 420, 48,
                    "SIGPIPE записувачеві; якщо ігнорується — write() = −1, EPIPE",
                    size=12, fill=BG, stroke=POS))
    g.append(fitbox(500, 232, 420, 62,
                    "не тому, що читач попрощався,\n"
                    "а тому, що написані байти нема кому забрати",
                    size=12, fill="#fdecea"))

    g.append(fitbox(40, 306, 880, 44,
                    "лічильники рахують описи в УСІХ процесах системи — "
                    "успадкована й забута копія рахується теж",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    render(os.path.join(IMG, 'refcount-ends.svg'), W, H, *g,
           title="Кінець даних і SIGPIPE як два лічильники")


def fig_fifo_open():
    """Відкриття іменованого каналу: п'ять способів і п'ять різних відповідей."""
    W, H = 1000, 424
    g = []

    C1, W1 = 30, 336
    C2, W2 = 378, 250
    C3, W3 = 640, 330

    for x, w, s in ((C1, W1, "як відкривають FIFO"),
                    (C2, W2, "що робить open()"),
                    (C3, W3, "чому саме так")):
        g.append(fitbox(x, 26, w, 42, s, size=13, bold=True, fill="#f7f3e8"))

    rows = [
        (80, "open(шлях, O_RDONLY)", "блокує",
         "чекає, доки хтось відкриє на запис", "#eef2f7"),
        (146, "open(шлях, O_WRONLY)", "блокує",
         "чекає, доки хтось відкриє на читання", "#eef2f7"),
        (212, "open(шлях, O_RDONLY | O_NONBLOCK)", "вдається негайно",
         "читач без пари нікому не шкодить —\nвін просто нічого не прочитає", "#eaf7ee"),
        (278, "open(шлях, O_WRONLY | O_NONBLOCK)", "−1, errno = ENXIO",
         "прийняти байти, яких гарантовано\nніхто не забере, ядро не дає", "#fdecea"),
        (344, "open(шлях, O_RDWR)", "вдається негайно",
         "Linux дозволяє, POSIX не визначає;\nкінець даних не настане ніколи", "#f7f3e8"),
    ]
    for y, a, b, c, fill in rows:
        g.append(fitbox(C1, y, W1, 58, a, size=12))
        g.append(fitbox(C2, y, W2, 58, b, size=12, fill=fill))
        g.append(fitbox(C3, y, W3, 58, c, size=11, fill="#eef2f7"))

    render(os.path.join(IMG, 'fifo-open.svg'), W, H, *g,
           title="Відкриття іменованого каналу і його відповіді")


def fig_close_accounting():
    """Лічильник кінців на запис у часі: правильна збірка і та сама з забутим close."""
    W, H = 960, 400
    g = []

    LX = 20
    AX, AW = 232, 348
    BX, BW = 596, 344

    g.append(fitbox(AX, 48, AW, 36, "як має бути", size=13, bold=True, fill="#eaf7ee"))
    g.append(fitbox(BX, 48, BW, 36, "без close(pfd[1]) у батька", size=13, bold=True,
                    fill="#fdecea"))

    rows = [
        ("1 · після pipe()",
         "тримає: батько", "кінців на запис: 1", BG,
         "тримає: батько", "кінців на запис: 1", BG),
        ("2 · після двох fork()",
         "тримають: батько, ls, wc", "кінців на запис: 3", BG,
         "тримають: батько, ls, wc", "кінців на запис: 3", BG),
        ("3 · після close-ів",
         "тримає: лише ls", "кінців на запис: 1", "#eef2f7",
         "тримають: ls і батько", "кінців на запис: 2", "#f7f3e8"),
        ("4 · ls завершився",
         "не тримає ніхто", "кінців: 0 → wc дістає read() == 0", "#eaf7ee",
         "тримає батько", "кінців: 1 → wc спить у read() назавжди", "#fdecea"),
    ]

    y = 96
    for lab, a1, a2, af, b1, b2, bf in rows:
        g.append(text(LX, y + 36, lab, size=12, anchor="start", color=MUTED))
        g.append(fitbox(AX, y, AW, 62, a1 + "\n" + a2, size=12, fill=af))
        g.append(fitbox(BX, y, BW, 62, b1 + "\n" + b2, size=12, fill=bf))
        y += 72

    render(os.path.join(IMG, 'close-accounting.svg'), W, H, *g,
           title="Скільки кінців на запис лишилося відкритими")


if __name__ == '__main__':
    fig_pipe_ring()
    fig_pipeline_wiring()
    fig_refcount_ends()
    fig_fifo_open()
    fig_close_accounting()
    print("ok")
