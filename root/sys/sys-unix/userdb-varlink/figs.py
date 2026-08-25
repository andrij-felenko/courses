# -*- coding: utf-8 -*-
"""Фігури до теми «userdb: облікові записи як записи JSON через Varlink»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_record_sections():
    """Секції запису: хто бачить і де секція живе."""
    W, H = 1280, 590
    f = []

    # колонки
    c1x, c1w = 60, 300
    c2x, c2w = 380, 430
    c3x, c3w = 830, 390
    hy, rh = 74, 58
    top = 116

    f.append(fitbox(c1x, hy, c1w, 40, "секція запису", size=15, bold=True,
                    fill="#eef3fd", stroke=NEG))
    f.append(fitbox(c2x, hy, c2w, 40, "хто її бачить", size=15, bold=True,
                    fill="#eef3fd", stroke=NEG))
    f.append(fitbox(c3x, hy, c3w, 40, "де вона живе", size=15, bold=True,
                    fill="#eef3fd", stroke=NEG))

    rows = [
        ("regular",    "будь-хто",                          "у записі, під підписом",  "#eafaf0"),
        ("privileged", "власник або привілейований процес",  "у записі, під підписом",  "#eafaf0"),
        ("perMachine", "будь-хто",                          "у записі, під підписом",  "#eafaf0"),
        ("signature",  "будь-хто",                          "у записі",                "#f4f6f8"),
        ("binding",    "тільки ця машина",                  "дописує машина, без підпису", "#fdf4e8"),
        ("status",     "будь-хто",                          "тільки в пам'яті",        "#fdf4e8"),
        ("secret",     "ніхто: живе лише в дорозі",         "ніде не зберігається",    "#fdecea"),
    ]
    for i, (name, who, where, tint) in enumerate(rows):
        y = top + i * rh
        f.append(fitbox(c1x, y, c1w, rh - 8, name, size=15, bold=True, fill=tint))
        f.append(fitbox(c2x, y, c2w, rh - 8, who, size=14, fill="#ffffff"))
        f.append(fitbox(c3x, y, c3w, rh - 8, where, size=14, fill="#ffffff"))

    return render(os.path.join(OUT, 'record-sections.svg'), W, H,
                  *f, title="Обліковий запис як об'єкт: сім секцій із різними правилами")


def fig_socket_directory():
    """Клієнт питає всі сокети теки одразу."""
    W, H = 1400, 700
    f = []

    # клієнт
    b, _, _ = textbox(190, 350, ["клієнт", "userdbctl, nss-systemd,", "будь-яка програма"],
                      size=14, fill="#eef3fd", stroke=NEG, min_w=280)
    f.append(b)

    # тека сокетів
    dirx, diry, dirw, dirh = 530, 120, 420, 500
    f.append(rect(dirx, diry, dirw, dirh, fill="#fbfcfe", stroke=MUTED, sw=1.5))
    f.append(text(dirx + dirw / 2, diry - 18, "/run/systemd/userdb/", size=15, bold=True))

    services = [
        ("io.systemd.NameServiceSwitch", "#ffffff"),
        ("io.systemd.DynamicUser", "#ffffff"),
        ("io.systemd.Home", "#ffffff"),
        ("io.systemd.DropIn", "#ffffff"),
        ("io.systemd.Multiplexer", "#eafaf0"),
    ]
    ys = [175, 265, 355, 445, 555]
    for (name, fill), y in zip(services, ys):
        f.append(fitbox(dirx + 25, y - 24, dirw - 50, 48, name, size=14, fill=fill))
        f.append(arrow(310, 350, dirx + 18, y))

    f.append(text(dirx + dirw / 2, 610, "той самий обхід, зроблений за клієнта",
                  size=13, color=MUTED))

    # праворуч: дві різні невдачі
    nx = 1180
    f.append(text(nx, 250, "дві невдачі — два імені", size=15, bold=True))
    f.append(text(nx, 292, "немає такого запису", size=13, color=MUTED))
    f.append(text(nx, 316, "NoRecordFound", size=14, color=NEG, bold=True))
    f.append(text(nx, 372, "не зміг спитати", size=13, color=MUTED))
    f.append(text(nx, 396, "ServiceNotAvailable", size=14, color=POS, bold=True))

    return render(os.path.join(OUT, 'socket-directory.svg'), W, H,
                  *f, title="Список джерел — це вміст теки, і питають усіх одразу")


def fig_two_bridges():
    """Два мости між класичною базою й записами JSON."""
    W, H = 1240, 470
    f = []

    b, _, _ = textbox(230, 235, ["класичний бік", "getpwnam(), /etc/passwd,", "модулі NSS"],
                      size=15, fill="#f4f6f8", min_w=340)
    f.append(b)
    b, _, _ = textbox(1010, 235, ["новий бік", "записи JSON,", "сокети userdb"],
                      size=15, fill="#eafaf0", stroke=FIELD, min_w=340)
    f.append(b)

    f.append(arrow(410, 165, 830, 165, color=NEG))
    f.append(text(620, 132, "nss-systemd", size=15, bold=True, color=NEG))
    f.append(text(620, 108, "класична програма бачить нові записи", size=13, color=MUTED))

    f.append(arrow(830, 305, 410, 305, color=FIELD))
    f.append(text(620, 340, "io.systemd.NameServiceSwitch", size=15, bold=True, color=FIELD))
    f.append(text(620, 364, "новий клієнт бачить класичні записи", size=13, color=MUTED))

    f.append(text(620, 428, "жоден міст не віддає того, що вже є на іншому боці",
                  size=13, color=MUTED))

    return render(os.path.join(OUT, 'two-bridges.svg'), W, H,
                  *f, title="Перехід без дня переходу: два мости назустріч")


def fig_ipc_timeline():
    """Вставка hist: дві дороги — відхилене ядром і прижите в просторі користувача."""
    W, H = 1420, 580
    BW, BH = 250, 62
    AXIS = 300
    f = []

    f.append(line(60, AXIS, 1380, AXIS, color=MUTED, sw=2))

    f.append(text(60, 62, "спроби перенести шину в ядро — жодна не дійшла",
                 size=15, color=POS, anchor="start", bold=True))
    f.append(text(60, 552, "Varlink і його тихий прихід у systemd",
                 size=15, color=FIELD, anchor="start", bold=True))

    kernel = [
        (130, 0, "березень 2013", "kdbus: шину — в ядро"),
        (330, 1, "квітень 2015", "pull request відхилено"),
        (500, 0, "жовтень 2016", "bus1: з нуля, теж мимо"),
    ]
    user = [
        (640, 0, "18 грудня 2017", "оголошено Varlink"),
        (850, 1, "березень 2020 · v245", "userdbd і homed"),
        (990, 0, "липень 2021 · v249", "io.systemd.DropIn"),
        (1150, 1, "грудень 2023 · v255", "varlinkctl"),
        (1290, 0, "грудень 2024 · v257", "sd-varlink як публічний API"),
    ]

    for x, row, when, what in kernel:
        cy = 200 if row == 0 else 118
        f.append(line(x, AXIS - 6, x, cy + BH / 2, color=POS, sw=1.2, dash="4 4"))
        f.append(circle(x, AXIS, 6, fill=POS, stroke=POS))
        f.append(fitbox(x - BW / 2, cy - BH / 2, BW, BH, [when, what],
                        size=14, fill="#fdecea", stroke=POS, color=INK))

    for x, row, when, what in user:
        cy = 400 if row == 0 else 482
        f.append(line(x, AXIS + 6, x, cy - BH / 2, color=FIELD, sw=1.2, dash="4 4"))
        f.append(circle(x, AXIS, 6, fill=FIELD, stroke=FIELD))
        f.append(fitbox(x - BW / 2, cy - BH / 2, BW, BH, [when, what],
                        size=14, fill="#eafaf0", stroke=FIELD, color=INK))

    return render(os.path.join(OUT, 'ipc-timeline.svg'), W, H,
                  *f, title="Дві дороги до раннього IPC: одна в ядро, друга повз нього")


def fig_request_life():
    """Життя одного з'єднання у власній службі userdb."""
    W, H = 1400, 640
    f = []

    b, _, _ = textbox(190, 320, ["клієнт", "connect() до файлу-сокета,",
                                 "один об'єкт JSON і нульовий байт"],
                      size=14, fill="#eef3fd", stroke=NEG, min_w=300)
    f.append(b)
    f.append(arrow(345, 320, 452, 320))

    f.append(rect(460, 100, 450, 450, fill="#fbfcfe", stroke=MUTED, sw=1.5))
    f.append(text(685, 82, "служба: один сокет, три перевірки", size=15, bold=True))

    steps = [
        (175, ["getsockopt(SO_PEERCRED)", "→ засвідчений UID співрозмовника"]),
        (300, ["service збігається з іменем сокета?", "інакше BadService"]),
        (425, ["userName · uid · перелік", "інакше NoRecordFound"]),
    ]
    for cy, lines in steps:
        b, _, _ = textbox(685, cy, lines, size=14, fill="#ffffff", min_w=400)
        f.append(b)
    f.append(arrow(685, 202, 685, 272))
    f.append(arrow(685, 328, 685, 397))
    f.append(text(685, 505, "усе — з пам'яті, жодного очікування", size=13, color=MUTED))

    outs = [
        (175, ["одна помилка", "error: …BadService"], "#fdecea", POS),
        (300, ["один запис", "record + incomplete"], "#eafaf0", FIELD),
        (440, ["перелік на more", "кожна відповідь — continues: true,",
               "остання — без нього"], "#eafaf0", FIELD),
    ]
    for cy, lines, tint, edge in outs:
        b, _, _ = textbox(1160, cy, lines, size=14, fill=tint, stroke=edge, min_w=400)
        f.append(b)
        f.append(arrow(915, cy, 953, cy))

    f.append(text(700, 600, "з'єднання живе рівно один запит: прочитали, відповіли, закрили",
                  size=13, color=MUTED))

    return render(os.path.join(OUT, 'request-life.svg'), W, H,
                  *f, title="Одне з'єднання у власній службі userdb")


if __name__ == '__main__':
    print(fig_record_sections())
    print(fig_socket_directory())
    print(fig_two_bridges())
    print(fig_request_life())
    print(fig_ipc_timeline())
