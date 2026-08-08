# -*- coding: utf-8 -*-
"""Фігури до теми «Асинхронний ввід-вивід ядра: io_submit і його межі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_aio_ring():
    """Асиметрія: подання коштує виклику, забирання — ні."""
    W, H = 980, 450
    g = []

    g.append(fitbox(20, 16, 940, 38, "програма (простір користувача)",
                    size=14, bold=True, fill="#eef2f7"))
    g.append(fitbox(20, 300, 940, 38, "ядро",
                    size=14, bold=True, fill="#eef2f7"))

    # ліва колонка — подання
    g.append(fitbox(30, 76, 250, 44, "масив iocb у пам'яті процесу", size=12))
    g.append(arrow(155, 126, 155, 156))
    g.append(fitbox(30, 160, 250, 56,
                    "io_submit(): перехід межі\nй копіювання в ядро",
                    size=12, fill="#fdecea"))
    g.append(arrow(155, 222, 155, 296))
    g.append(text(172, 250, "подання завжди", size=12, anchor="start"))
    g.append(text(172, 268, "коштує виклику", size=12, anchor="start"))

    # права колонка — кільце завершень
    g.append(text(650, 148, "кільце завершень у спільній пам'яті",
                  size=13, bold=True))
    cells = ["res, data", "res, data", "res, data", "", "", ""]
    for i, s in enumerate(cells):
        x = 372 + i * 94
        g.append(fitbox(x, 162, 88, 50, s, size=12,
                        fill="#eaf7ee" if s else BG))

    g.append(arrow(416, 86, 416, 158))
    g.append(text(436, 96, "програма забирає з голови", size=12, anchor="start"))
    g.append(text(436, 114, "і посуває head — без виклику", size=12, anchor="start"))

    g.append(arrow(698, 292, 698, 218))
    g.append(text(716, 252, "ядро дописує в хвіст", size=12, anchor="start"))
    g.append(text(716, 270, "і посуває tail", size=12, anchor="start"))

    # підписи-висновки під смугою ядра
    g.append(fitbox(30, 356, 280, 76,
                    "забрати завершення можна\nпростим читанням пам'яті,\nбез io_getevents",
                    size=12, fill="#eaf7ee"))
    g.append(fitbox(346, 356, 614, 76,
                    "magic = 0xa10a10a1 підтверджує формат кільця;\n"
                    "aio_context_t — це адреса самого відображення",
                    size=12, fill="#fbfcfd"))

    render(os.path.join(IMG, 'aio-ring.svg'), W, H, *g)


def fig_submit_path():
    """Три ділянки шляху подання і те, де він засинає."""
    W, H = 980, 400
    g = []

    g.append(text(490, 36,
                  "io_submit(): робота відбувається на вашому потоці, не в черзі",
                  size=13, bold=True))

    stages = [
        (20, "шлях файлової системи\n(кеш сторінок або метадані)", "#eef2f7"),
        (340, "блоковий шар\n(слот у черзі пристрою)", "#eef2f7"),
        (660, "передано контролеру:\nповернуто -EIOCBQUEUED", "#eaf7ee"),
    ]
    for x, s, col in stages:
        g.append(fitbox(x, 70, 270, 60, s, size=12, fill=col))
    g.append(arrow(294, 100, 336, 100))
    g.append(arrow(614, 100, 656, 100))

    g.append(arrow(155, 134, 155, 172))
    g.append(fitbox(20, 176, 270, 96,
                    "спить, якщо:\n"
                    "потрібної сторінки немає в кеші;\n"
                    "брудних сторінок дійшло до межі;\n"
                    "вузол дерева екстентів не в пам'яті",
                    size=12, fill="#fdecea"))

    g.append(arrow(475, 134, 475, 172))
    g.append(fitbox(340, 176, 270, 96,
                    "спить, якщо:\n"
                    "вільного слоту в черзі\n"
                    "пристрою немає — чекає,\n"
                    "доки хтось звільнить",
                    size=12, fill="#fdecea"))

    g.append(fitbox(660, 176, 270, 96,
                    "лише дійшовши сюди,\n"
                    "виклик повертається,\n"
                    "не дочекавшись даних",
                    size=12, fill="#eaf7ee"))

    g.append(fitbox(20, 306, 910, 62,
                    "усе, що ліворуч від правої колонки, — синхронне: доки потік спить там, "
                    "він нічого не подає,\n"
                    "тож фактична глибина черги дорівнює темпу подання, помноженому на затримку носія",
                    size=12, fill="#eef2f7"))

    render(os.path.join(IMG, 'submit-path.svg'), W, H, *g)


def fig_abi_layout():
    """Побайтова розкладка трьох структур ABI (до вставки про інтерфейс)."""
    W, H = 900, 636
    ROWH = 34
    GREEN, RED, GRAY = "#eaf7ee", "#fdecea", "#eef2f7"
    g = []

    def bytemap(x, y, w, rows):
        out, off = [], 0
        for r in rows:
            out.append(text(x - 14, y + ROWH / 2 + 4, str(off),
                            size=11, color=MUTED, anchor="end"))
            cx = x
            for label, n, fill in r:
                cw = w * n / 8.0
                out.append(fitbox(cx, y, cw, ROWH, label,
                                  size=11, pad=8, fill=fill, rx=3))
                cx += cw
            y += ROWH
            off += 8
        return out, y

    g.append(text(60, 34, "struct iocb — 64 байти, те, що подають",
                  size=13, bold=True, anchor="start"))
    part, _ = bytemap(60, 46, 640, [
        [("aio_data — мітка, повертається незміненою", 8, GREEN)],
        [("aio_key", 4, GRAY), ("aio_rw_flags (RWF_*)", 4, FILL)],
        [("aio_lio_opcode", 2, FILL), ("aio_reqprio", 2, FILL),
         ("aio_fildes", 4, FILL)],
        [("aio_buf", 8, FILL)],
        [("aio_nbytes", 8, FILL)],
        [("aio_offset", 8, FILL)],
        [("aio_reserved2 — нуль", 8, RED)],
        [("aio_flags", 4, FILL), ("aio_resfd", 4, FILL)],
    ])
    g += part

    g.append(text(60, 352, "struct io_event — 32 байти",
                  size=13, bold=True, anchor="start"))
    part, _ = bytemap(60, 364, 360, [
        [("data — мітка з iocb", 8, GREEN)],
        [("obj — адреса того iocb", 8, FILL)],
        [("res — байти або −errno", 8, GREEN)],
        [("res2 — нуль", 8, FILL)],
    ])
    g += part

    g.append(text(524, 352, "struct aio_ring — заголовок кільця",
                  size=13, bold=True, anchor="start"))
    part, _ = bytemap(524, 364, 340, [
        [("id", 4, GRAY), ("nr", 4, FILL)],
        [("head", 4, FILL), ("tail", 4, FILL)],
        [("magic", 4, GREEN), ("compat_features", 4, FILL)],
        [("incompat_features", 4, FILL), ("header_length", 4, FILL)],
        [("io_events[] — nr комірок", 8, GREEN)],
    ])
    g += part

    g.append(fitbox(60, 560, 804, 56,
                    "розміри й зміщення полів заморожені разом з рештою ABI;\n"
                    "початок io_events[] беруть із header_length, а не з припущення",
                    size=12, fill="#fbfcfd"))

    render(os.path.join(IMG, 'abi-layout.svg'), W, H, *g)


def fig_depth_curve():
    """Форма результату вимірювання: прямий росте з глибиною, буферизований — ні."""
    W, H = 960, 500
    g = []

    X0, X1 = 140, 890
    YTOP, YB = 60, 360
    y12k, y100k, y400k = 340, 202, 110

    g.append(text(140, 44, "операцій за секунду (шкала логарифмічна)",
                  size=12, bold=True, anchor="start"))
    g.append(line(X0, YTOP, X0, YB))
    g.append(line(X0, YB, X1, YB))
    g.append(line(X0, y400k, 870, y400k, color=MUTED, sw=1.2, dash="6,5"))
    g.append(text(505, 94,
                  "стеля носія: більше запитів уже не дають більшого темпу",
                  size=12, color=MUTED))

    g.append(text(128, y12k + 4, "12 500", size=12, color=MUTED, anchor="end"))
    g.append(text(128, y100k + 4, "100 000", size=12, color=MUTED, anchor="end"))
    g.append(text(128, 94, "400 000", size=12, color=MUTED, anchor="end"))

    g.append('<polyline points="180,%d 480,%d 800,%d" fill="none" '
             'stroke="%s" stroke-width="2.6"/>' % (y12k, y100k, y400k, POS))
    g.append('<polyline points="180,%d 480,336 800,332" fill="none" '
             'stroke="%s" stroke-width="2.6"/>' % (y12k, NEG))
    for x, y in ((180, y12k), (480, y100k), (800, y400k)):
        g.append(circle(x, y, 5, fill=POS, stroke=POS))
    for x, y in ((480, 336), (800, 332)):
        g.append(circle(x, y, 5, fill=NEG, stroke=NEG))

    for d, x in ((1, 180), (8, 480), (64, 800)):
        g.append(line(x, YB, x, YB + 6))
        g.append(text(x, YB + 24, str(d), size=12))
    g.append(text(505, 412, "глибина черги (запитів у польоті)",
                  size=12, bold=True))

    g.append(fitbox(168, 116, 300, 64,
                    "з O_DIRECT: вісім запитів у польоті\n"
                    "дають приблизно ввосьмеро більший темп",
                    size=12, fill="#fdecea"))
    g.append(text(628, 308, "без O_DIRECT", size=12, color=NEG, bold=True))
    g.append(fitbox(120, 430, 740, 52,
                    "без O_DIRECT подання виконує роботу саме, тож глибина існує лише "
                    "на папері —\nусі три числа сходяться в одне",
                    size=12, fill="#eaf7ee"))

    render(os.path.join(IMG, 'depth-curve.svg'), W, H, *g)


if __name__ == '__main__':
    fig_aio_ring()
    fig_submit_path()
    fig_abi_layout()
    fig_depth_curve()
    print("ok")
