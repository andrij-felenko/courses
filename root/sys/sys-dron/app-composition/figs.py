# -*- coding: utf-8 -*-
"""Фігури до теми «З чого складається застосунок: шари й запуск»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def tb(cx, cy, s, **kw):
    body, w, h = textbox(cx, cy, s, **kw)
    return body


def tb_h(s, size=14, pad=10):
    lines = s.split("\n") if isinstance(s, str) else list(s)
    return len(lines) * size * 1.3 + 2 * pad - size * 0.3


def tb_w(s, size=14, pad=10, bold=False, min_w=0):
    lines = s.split("\n") if isinstance(s, str) else list(s)
    return max(min_w, max(text_width(ln, size, bold) for ln in lines) + 2 * pad)


# ── 1. Конвеєр «байт → піксель» ────────────────────────────────────────────
def fig_pipeline():
    W, H = 1120, 850
    CX = 320          # центр колонки станцій
    BOXW = 430        # фіксована ширина станції
    LX = 610          # ліва межа підписів переходів
    frags = []

    stations = [
        "Порт або сокет\nробітник у власному потоці",
        "MAVLinkProtocol\nmavlink_parse_char за каналом",
        "MultiVehicleManager\nsysid → який це апарат",
        "Vehicle\n_handle… розкладає поля кадру",
        "Факти\nчисло + одиниці + межі + назва",
        "QML\nприв'язки перемальовують кадр",
    ]
    edges = [
        ["bytesReceived(link, data)", "перетин межі потоків: сигнал стає", "подією в черзі головного потоку"],
        ["messageReceived(link, msg)", "і окремо vehicleHeartbeatInfo(...)", "для кадрів HEARTBEAT"],
        ["апарат знайдено в списку", "або створено новий Vehicle"],
        ["setRawValue(...) на потрібний факт", "сире значення лягає в модель"],
        ["valueChanged → NOTIFY властивості", "перерахунок прив'язок"],
    ]

    y0, step = 96, 132
    ys = [y0 + i * step for i in range(len(stations))]
    hh = tb_h(stations[0])

    for s, y in zip(stations, ys):
        frags.append(fitbox(CX - BOXW / 2, y - hh / 2, BOXW, hh, s, size=14))

    for i, lab in enumerate(edges):
        ya, yb = ys[i] + hh / 2, ys[i + 1] - hh / 2
        frags.append(arrow(CX, ya + 6, CX, yb - 6))
        mid = (ya + yb) / 2
        top = mid - (len(lab) - 1) * 12 * 1.35 / 2
        frags.append(mtext(LX, top, lab, size=12, color=MUTED, anchor="start", lh=1.35))

    frags.append(text(CX, ys[0] - hh / 2 - 22, "залізо і мілісекунди", size=12,
                      color=MUTED, italic=True))
    frags.append(text(CX, ys[-1] + hh / 2 + 30, "екран і кадри", size=12,
                      color=MUTED, italic=True))
    render(os.path.join(OUT, 'pipeline.svg'), W, H, *frags,
           title="Шлях числа: від байта в дроті до значення на екрані")


# ── 2. Порядок запуску ─────────────────────────────────────────────────────
def fig_startup():
    W, H = 1180, 840
    CX = 290
    BOXW = 470
    LX = 570
    frags = []

    steps = [
        "main(): розбір командного рядка,\nвибір режиму запуску",
        "QGCApplication: імена, QSettings,\nзвірка версії налаштувань",
        "кореневе вікно QML\n(створює плагін ядра)",
        "звук · FollowMe · позиція · NTRIP",
        "LinkManager",
        "VideoManager(mainRootWindow)",
        "JoystickManager",
        "автопідключення каналів",
    ]
    notes = [
        ["спільного стану ще немає зовсім"],
        ["з цієї миті будь-хто далі", "може читати налаштування"],
        ["є поверхня, на якій", "малюватиме відео"],
        ["служби, яким потрібні лише", "налаштування, і нічого більше"],
        ["реєстр каналів готовий,", "але жодного ще не відкрито"],
        ["вимагає вікна — тому", "стоїть після нього"],
        ["джойстик шукає активний апарат,", "апаратів поки нема"],
        ["останнім: щойно канал відкрито,", "у застосунок ринуть байти"],
    ]

    y0, step = 100, 92
    ys = [y0 + i * step for i in range(len(steps))]

    for s, y in zip(steps, ys):
        h = tb_h(s)
        frags.append(fitbox(CX - BOXW / 2, y - h / 2, BOXW, h, s, size=13))

    for i in range(len(steps) - 1):
        ha, hb = tb_h(steps[i]), tb_h(steps[i + 1])
        frags.append(arrow(CX, ys[i] + ha / 2 + 4, CX, ys[i + 1] - hb / 2 - 4))

    for n, y in zip(notes, ys):
        top = y - (len(n) - 1) * 12 * 1.35 / 2
        frags.append(mtext(LX, top, n, size=12, color=MUTED, anchor="start", lh=1.35))

    render(os.path.join(OUT, 'startup.svg'), W, H, *frags,
           title="Порядок запуску: кожен крок додає те, на що спирається наступний")


# ── 3. Стан парсера на кожен канал ─────────────────────────────────────────
def fig_channels():
    W, H = 1100, 420
    frags = []

    # ліва панель — спільний стан
    frags.append(rect(40, 58, 480, 320, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(text(280, 88, "один стан на два джерела", size=14, bold=True, color=POS))
    frags.append(tb(150, 150, "Лінк A", size=13))
    frags.append(tb(150, 232, "Лінк B", size=13))
    frags.append(tb(370, 191, "спільний\nстан кадру", size=13))
    frags.append(arrow(196, 152, 302, 180))
    frags.append(arrow(196, 230, 302, 202))
    frags.append(mtext(370, 296, ["байти двох кадрів злипаються,",
                                  "контрольна сума не сходиться"],
                       size=12, color=POS, lh=1.35))

    # права панель — стан на канал
    frags.append(rect(580, 58, 480, 320, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(text(820, 88, "стан на кожен канал", size=14, bold=True, color=FIELD))
    frags.append(tb(680, 150, "Лінк A", size=13))
    frags.append(tb(680, 232, "Лінк B", size=13))
    frags.append(tb(900, 150, "стан каналу 1", size=13))
    frags.append(tb(900, 232, "стан каналу 2", size=13))
    frags.append(arrow(726, 150, 838, 150))
    frags.append(arrow(726, 232, 838, 232))
    frags.append(mtext(820, 296, ["кожен кадр збирається окремо,",
                                  "джерела не заважають одне одному"],
                       size=12, color=FIELD, lh=1.35))

    render(os.path.join(OUT, 'channels.svg'), W, H, *frags,
           title="Чому кожному з'єднанню потрібен власний номер каналу")


# ── 4. Маятник власності над глобальними об'єктами (вставка hist-toolbox) ───
def fig_toolbox():
    W, H = 1200, 560
    frags = []

    BASE = 400          # рівень нуля
    K = 11.5            # пікселів на один запис у ящику

    def yv(v):
        return BASE - v * K

    pts = [(170, 0), (390, 11), (630, 25), (870, 1), (1050, 0)]
    labels = [
        ["до 2015-10", "ящика нема:", "сінглтони з макросом"],
        ["2015-10-29", "ящик заведено:", "11 менеджерів"],
        ["2019–2021 (v4.x)", "ящик розпух:", "25 записів"],
        ["2024-11, напередодні", "лишився один:", "плагін ядра"],
        ["2024-11-29", "ящика нема:", "X::instance()"],
    ]

    # вісь
    frags.append(line(90, BASE, 1130, BASE, color=MUTED, sw=1.2))
    frags.append(text(90, BASE - 300, "скільки об'єктів тримає ящик", size=12,
                      color=MUTED, anchor="start"))

    # ламана
    for i in range(len(pts) - 1):
        x1, v1 = pts[i]
        x2, v2 = pts[i + 1]
        frags.append(line(x1, yv(v1), x2, yv(v2), color=INK, sw=2.4))

    for (x, v), lab in zip(pts, labels):
        frags.append(circle(x, yv(v), 6, fill=BG, stroke=INK, sw=2.4))
        frags.append(text(x, yv(v) - 16, str(v), size=14, bold=True,
                          color=(FIELD if v == 0 else INK)))
        frags.append(mtext(x, BASE + 32, lab, size=12, color=MUTED, lh=1.4))

    # виноски на два коміти
    frags.append(tb(285, 168, "3433b541 · Don Gagne\n«Remove as many Singletons as possible»",
                    size=13))
    frags.append(arrow(285, 200, 380, yv(11) - 14))

    frags.append(tb(985, 190, "39b1ae11 · Holden Ramsey\n«Convert QGCCorePlugin to Singleton»",
                    size=13))
    frags.append(arrow(985, 222, 885, yv(1) - 20))

    frags.append(text(600, 508,
                      "нуль тут означає не «порожній ящик», а «ящика немає»",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'toolbox-pendulum.svg'), W, H, *frags,
           title="Маятник власності: від сінглтонів до ящика інструментів і назад")


# ── 5. Стискання подій за такт (вставка proj-byte-to-fact) ─────────────────
def fig_tick_compress():
    W, H = 1080, 500
    frags = []

    MARKS = [320 + i * 48 for i in range(10)]

    def panel(y_top, title, color, band_text, result, marks_y, band_y):
        out = [rect(40, y_top, 1000, 180, fill=BG, stroke=MUTED, sw=1.2)]
        out.append(text(64, y_top + 30, title, size=14, bold=True,
                        color=color, anchor="start"))
        out.append(text(560, y_top + 30, "50 кадрів висоти за один такт",
                        size=12, color=MUTED))
        for x in MARKS:
            out.append(circle(x, marks_y, 5, fill=BG, stroke=color, sw=2))
            out.append(arrow(x, marks_y + 8, x, band_y - 4, color=color, sw=1.4))
        out.append(rect(300, band_y, 472, 44, fill=FILL, stroke=color, sw=1.4))
        out.append(text(536, band_y + 27, band_text, size=12))
        out.append(arrow(776, band_y + 22, 852, band_y + 22, color=color))
        out.append(tb(925, band_y + 22, result, size=13))
        return out

    frags += panel(58, "без стискання", POS,
                   "обробник кличеться одразу, 50 разів",
                   "50 перерахунків\nза такт", 128, 168)
    frags += panel(262, "зі стисканням", FIELD,
                   "у черзі один запис — нова заміщає стару",
                   "1 перерахунок\nза такт", 332, 372)

    frags.append(text(540, 472,
                      "стискати вільно лише стан: останнє значення робить попередні непотрібними",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'tick-compress.svg'), W, H, *frags,
           title="Стискання подій: п'ятдесят змін за такт — одне перемальовування")


fig_pipeline()
fig_startup()
fig_channels()
fig_toolbox()
fig_tick_compress()
print("ok")
