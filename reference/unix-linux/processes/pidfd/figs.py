# -*- coding: utf-8 -*-
"""Фігури до теми «Дескриптор процесу (pidfd)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_what_the_handle_holds():
    """Номер іде через таблицю, дескриптор тримає тотожність напряму."""
    W, H = 1010, 515
    f = []

    # ── Панель А: процес живий ───────────────────────────────────────────
    f.append(text(60, 78, "поки процес живий", size=14, bold=True, anchor="start"))

    b, _, _ = textbox(120, 115, "число 4242", size=13)
    f.append(b)
    b, _, _ = textbox(345, 115, "таблиця номерів", size=13)
    f.append(b)
    b, _, _ = textbox(580, 115, ["тотожність", "(struct pid)"], size=13,
                      fill="#eaf0fd", stroke=NEG)
    f.append(b)
    b, _, _ = textbox(850, 115, ["задача", "(виконання)"], size=13)
    f.append(b)

    f.append(arrow(172, 115, 273, 115))
    f.append(arrow(415, 115, 519, 115))
    f.append(arrow(640, 115, 793, 115))

    b, _, _ = textbox(120, 205, "pidfd 3", size=13, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    f.append(line(160, 205, 580, 205, color=NEG, sw=1.8))
    f.append(arrow(580, 205, 580, 145, color=NEG))

    f.append(line(40, 268, 970, 268, color=MUTED, sw=1, dash="6 5"))

    # ── Панель Б: процес прибрано, число вже чуже ────────────────────────
    f.append(text(60, 318, "після завершення й прибирання", size=14, bold=True, anchor="start"))

    b, _, _ = textbox(120, 358, "число 4242", size=13)
    f.append(b)
    b, _, _ = textbox(345, 358, "таблиця номерів", size=13)
    f.append(b)
    b, _, _ = textbox(580, 358, ["тотожність", "нового процесу"], size=13,
                      fill="#fdecea", stroke=POS)
    f.append(b)
    b, _, _ = textbox(850, 358, "нова задача", size=13)
    f.append(b)

    f.append(arrow(172, 358, 273, 358))
    f.append(arrow(415, 358, 512, 358))
    f.append(arrow(646, 358, 793, 358))

    b, _, _ = textbox(120, 452, "pidfd 3", size=13, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    b, _, _ = textbox(580, 452, ["стара тотожність", "без задачі"], size=13,
                      fill="#f0f2f4", stroke=MUTED)
    f.append(b)
    f.append(arrow(160, 452, 504, 452, color=NEG))
    f.append(arrow(656, 452, 762, 452, color=MUTED))
    f.append(mtext(772, 446, ["дії крізь нього", "дають ESRCH"], size=12,
                   color=POS, anchor="start"))

    render(os.path.join(OUT, 'what-the-handle-holds.svg'), W, H, *f,
           title="Куди веде число і куди — дескриптор")


def fig_four_doors():
    """Чотири способи взяти pidfd і де лишається вікно сумніву."""
    W, H = 1040, 445
    f = []
    x0, x1 = 370, 820
    rows = [
        (115, ["pidfd_open(число)", "з наявного номера"], 530, ["вікно перед", "створенням"]),
        (190, ["clone3(CLONE_PIDFD)", "разом із народженням"], None, ["вікна немає"]),
        (265, ["SO_PEERPIDFD", "ядро як свідок"], None, ["вікна немає"]),
        (340, ["SCM_RIGHTS", "передали сокетом"], None, ["вікна немає"]),
    ]

    f.append(text(x0 + (x1 - x0) / 2, 78, "час →", size=12, color=MUTED))

    for cy, label, split, verdict in rows:
        b, _, _ = textbox(200, cy, label, size=12)
        f.append(b)
        if split:
            f.append(rect(x0, cy - 8, split - x0, 16, fill="#f6c9c2", stroke=POS, sw=1.2, rx=3))
            f.append(rect(split, cy - 8, x1 - split, 16, fill="#cfd9ee", stroke=NEG, sw=1.2, rx=3))
        else:
            f.append(rect(x0, cy - 8, x1 - x0, 16, fill="#cfd9ee", stroke=NEG, sw=1.2, rx=3))
        f.append(mtext(845, cy - 3, verdict, size=12, color=MUTED, anchor="start"))

    # легенда
    f.append(rect(370, 396, 26, 14, fill="#f6c9c2", stroke=POS, sw=1.2, rx=3))
    f.append(text(406, 407, "ім'я ще може застаріти", size=12, anchor="start"))
    f.append(rect(640, 396, 26, 14, fill="#cfd9ee", stroke=NEG, sw=1.2, rx=3))
    f.append(text(676, 407, "значення закріплене", size=12, anchor="start"))

    render(os.path.join(OUT, 'four-doors.svg'), W, H, *f,
           title="Звідки беруться дескриптори і де ще можливе застаріле ім'я")


def fig_handle_lifetime():
    """Три смуги одного проміжку часу: процес, дескриптор, число."""
    W, H = 1010, 405
    f = []
    e1, e2, e3 = 380, 620, 830

    f.append(text(e1, 78, "завершився", size=12, bold=True))
    f.append(text(e2, 78, "прибрано", size=12, bold=True))
    f.append(line(e1, 92, e1, 345, color=MUTED, sw=1.2, dash="6 5"))
    f.append(line(e2, 92, e2, 345, color=MUTED, sw=1.2, dash="6 5"))

    f.append(text(140, 125, "процес", size=13, bold=True, anchor="end"))
    f.append(fitbox(150, 103, 227, 36, "виконується", size=13))
    f.append(fitbox(383, 103, 234, 36, "зомбі", size=13, fill="#fdecea", stroke=POS))
    f.append(fitbox(623, 103, 327, 36, "не існує", size=13, fill="#f0f2f4", stroke=MUTED))

    f.append(text(140, 220, "дескриптор", size=13, bold=True, anchor="end"))
    f.append(fitbox(150, 198, 227, 36, "мовчить", size=13))
    f.append(fitbox(383, 198, 234, 36, "читабельний: EPOLLIN", size=13,
                    fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(623, 198, 327, 36, "EPOLLHUP; чинний, дії дають ESRCH", size=13,
                    fill="#eaf0fd", stroke=NEG))

    f.append(text(140, 315, "число", size=13, bold=True, anchor="end"))
    f.append(fitbox(150, 293, 467, 36, "зайняте", size=13))
    f.append(fitbox(623, 293, 204, 36, "вільне", size=13, fill="#f0f2f4", stroke=MUTED))
    f.append(fitbox(833, 293, 117, 36, "уже інший", size=13, fill="#fdecea", stroke=POS))

    f.append(line(e3, 331, e3, 350, color=MUTED, sw=1.2))
    f.append(text(e3, 368, "число видано новому", size=12, color=MUTED))

    render(os.path.join(OUT, 'handle-lifetime.svg'), W, H, *f,
           title="Що показує дескриптор, поки число вже живе своїм життям")


def fig_two_lineages():
    """Ідея з FreeBSD і поетапне внесення pidfd у Linux."""
    W, H = 1120, 470
    f = []

    b, _, _ = textbox(230, 70, ["FreeBSD 9.0 (січень 2012), Capsicum",
                                "pdfork · pdkill · pdwait4"],
                      size=13, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    f.append(arrow(230, 108, 150, 262, color=NEG))
    f.append(text(430, 78, "мотив — пісочниця, а не гонка", size=12,
                  color=MUTED, anchor="start"))

    b, _, _ = textbox(830, 70, ["Linux, 2015: CLONE_FD / clone4",
                                "відхилено"], size=13, fill=FILL, stroke=MUTED)
    f.append(b)
    f.append(line(830, 108, 830, 150, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(830, 172, "«забагато всього в одному кроці»", size=12,
                  color=MUTED))

    AX = 280
    f.append(line(60, AX, 1060, AX, color=INK, sw=1.8))
    f.append(text(60, AX - 14, "Linux, крок за кроком", size=13, bold=True,
                  anchor="start"))

    steps = [
        (140, "up",   ["5.1 (2019)", "pidfd_send_signal"]),
        (330, "down", ["5.2", "CLONE_PIDFD"]),
        (505, "up",   ["5.3", "pidfd_open"]),
        (665, "down", ["5.4", "waitid(P_PIDFD)"]),
        (835, "up",   ["5.6 (2020)", "pidfd_getfd"]),
        (1000, "down", ["6.9 (2024)", "pidfs, PIDFD_THREAD"]),
    ]
    for x, side, lines in steps:
        f.append(circle(x, AX, 6, fill=INK, stroke=INK))
        if side == "up":
            f.append(line(x, AX - 6, x, AX - 46, color=INK, sw=1.2))
            b, _, _ = textbox(x, AX - 82, lines, size=12)
        else:
            f.append(line(x, AX + 6, x, AX + 46, color=INK, sw=1.2))
            b, _, _ = textbox(x, AX + 82, lines, size=12)
        f.append(b)

    f.append(text(60, 440, "до 5.1 обхід — дескриптор на каталог /proc/<pid>",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'two-lineages.svg'), W, H, *f,
           title="Звідки взялася ідея й якими кроками вона потрапила в Linux")


def fig_info_versioning():
    """Розмір структури, зашитий у номер команди, вирішує, скільки байтів перетне межу."""
    W, H = 1080, 545
    f = []

    f.append(text(60, 70, "struct pidfd_info: що де лежить", size=14, bold=True,
                  anchor="start"))

    y0, hh = 92, 48
    segs = [
        (60, 130, ["mask", "8 Б"], FILL),
        (190, 130, ["cgroupid", "8 Б"], FILL),
        (320, 330, ["pid, tgid, ppid, ruid … fsgid", "11 × 4 Б"], FILL),
        (650, 110, ["exit_code", "4 Б"], "#eaf0fd"),
        (760, 260, ["поля аварійного дампа", "додані пізніше"], "#f0f2f4"),
    ]
    for x, w, lines, fill in segs:
        f.append(rect(x, y0, w, hh, fill=fill))
        f.append(mtext(x + w / 2, y0 + 20, lines, size=12))

    f.append(line(60, 162, 760, 162, color=NEG, sw=1.6))
    f.append(line(60, 156, 60, 168, color=NEG, sw=1.6))
    f.append(line(760, 156, 760, 168, color=NEG, sw=1.6))
    f.append(text(410, 186, "PIDFD_INFO_SIZE_VER0 = 64 байти", size=12, color=NEG))

    def case(ytop, caption, kernel_w, prog_w, note):
        f.append(text(60, ytop, caption, size=13, bold=True, anchor="start"))
        f.append(text(295, ytop + 40, "ядро вміє", size=12, anchor="end"))
        f.append(rect(305, ytop + 26, kernel_w, 20, fill="#cfd9ee", stroke=NEG, sw=1.2, rx=3))
        f.append(text(295, ytop + 76, "програма просить", size=12, anchor="end"))
        f.append(rect(305, ytop + 62, prog_w, 20, fill=FILL, rx=3))
        cut = 305 + min(kernel_w, prog_w)
        f.append(line(cut, ytop + 16, cut, ytop + 92, color=POS, sw=1.4, dash="5 4"))
        f.append(text(305, ytop + 116, note, size=12, color=MUTED, anchor="start"))

    case(250, "ядро старіше за програму", 430, 640,
         "перетне межу лише те, що ядро вміє; решту програма побачить нулями")
    case(400, "ядро новіше за програму", 640, 430,
         "ядро обріже відповідь до розміру, узятого з номера команди")

    render(os.path.join(OUT, 'info-versioning.svg'), W, H, *f,
           title="Чому PIDFD_GET_INFO не ламається між версіями")


fig_what_the_handle_holds()
fig_four_doors()
fig_handle_lifetime()
fig_two_lineages()
fig_info_versioning()
print("готово")


def fig_auth_window():
    """Вікно в наївній перевірці прав і його відсутність у перевірці дескриптором."""
    W, H = 1010, 470
    f = []

    # ── Панель А: наївно, через число ────────────────────────────────────
    f.append(text(50, 78, "наївно: число з сокета — і з ним у /proc",
                  size=14, bold=True, anchor="start"))

    b, _, _ = textbox(140, 135, ["getsockopt(SO_PEERCRED)", "→ число N"], size=12)
    f.append(b)
    b, _, _ = textbox(400, 135, "read /proc/N/cgroup", size=12)
    f.append(b)
    b, _, _ = textbox(650, 135, "read /proc/N/status", size=12)
    f.append(b)
    b, _, _ = textbox(880, 135, "рішення", size=12)
    f.append(b)

    f.append(arrow(232, 135, 322, 135))
    f.append(arrow(478, 135, 572, 135))
    f.append(arrow(728, 135, 843, 135))

    f.append(line(234, 196, 841, 196, color=POS, sw=1.8))
    f.append(line(234, 186, 234, 206, color=POS, sw=1.8))
    f.append(line(841, 186, 841, 206, color=POS, sw=1.8))
    f.append(mtext(537, 230,
                   ["вікно Δ ≈ 23 мкс: ціль названо числом, а не закріплено",
                    "клієнт устигає померти, а число — дістатися новому процесові"],
                   size=12, color=POS))

    f.append(line(40, 278, 970, 278, color=MUTED, sw=1, dash="6 5"))

    # ── Панель Б: надійно, через дескриптор ──────────────────────────────
    f.append(text(50, 315, "надійно: дескриптор із сокета — і питання до нього",
                  size=14, bold=True, anchor="start"))

    b, _, _ = textbox(195, 372, ["getsockopt(SO_PEERPIDFD)", "→ дескриптор"],
                      size=12, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    b, _, _ = textbox(520, 372, ["ioctl(PIDFD_GET_INFO)", "uid, gid, cgroupid"],
                      size=12, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    b, _, _ = textbox(830, 372, "рішення", size=12)
    f.append(b)

    f.append(arrow(290, 372, 435, 372))
    f.append(arrow(605, 372, 793, 372))

    f.append(text(505, 432,
                  "вікна немає: обидва кроки говорять із тим самим закріпленим об'єктом",
                  size=12, color=NEG))

    render(os.path.join(OUT, 'auth-window.svg'), W, H, *f,
           title="Вікно наївної перевірки прав і його відсутність у перевірці дескриптором")


fig_auth_window()
