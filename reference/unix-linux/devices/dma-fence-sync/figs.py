# -*- coding: utf-8 -*-
"""Фігури до теми «dma-fence і sync_file: хто каже, що буфер готовий»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_fence_states():
    """Один перехід стану — і три різні способи його дочекатися."""
    W, H = 1060, 430
    f = []

    # ── панель самої огорожі ──────────────────────────────────────────────
    f.append(rect(36, 50, 480, 330, fill="#fbfcfd", stroke="#c3c9d1", sw=1.4, rx=10))
    f.append(text(60, 82, "Огорожа (dma_fence)", size=14, bold=True, anchor="start"))

    f.append(fitbox(60, 100, 170, 54, "не спрацювала", size=13))
    f.append(arrow(240, 127, 316, 127, color=POS))
    f.append(text(278, 112, "падає раз", size=11, color=POS))
    f.append(fitbox(322, 100, 170, 54, "спрацювала", size=13,
                    fill="#eaf7ee", stroke=FIELD))

    f.append(text(60, 190, "назад дороги немає: нова порція роботи — нова огорожа",
                 size=12, color=MUTED, anchor="start"))
    f.append(text(60, 232, "контекст — з якої апаратної черги вона вийшла",
                 size=12, anchor="start"))
    f.append(text(60, 262, "номер — місце в цій черзі, звідси й порядок",
                 size=12, anchor="start"))
    f.append(text(60, 292, "помилка — позначка всередині; стан однаково «спрацювала»",
                 size=12, anchor="start"))
    f.append(text(60, 322, "лічильник посилань — живе, доки дивиться хоч хтось",
                 size=12, anchor="start"))

    # ── три спостерігачі ──────────────────────────────────────────────────
    watchers = [
        (70,  "потік у ядрі засинає до сигналу", "дорого: потік стоїть"),
        (185, "зворотний виклик у мить падіння", "дешево: нікому не чекати"),
        (300, "черга команд пристрою чекає сама", "найдешевше: без процесора"),
    ]
    for y, what, price in watchers:
        f.append(fitbox(660, y, 370, 46, what, size=13))
        f.append(text(1030, y + 68, price, size=11, color=MUTED, anchor="end"))
        f.append(arrow(524, y + 23, 654, y + 23))

    render(os.path.join(IMG, 'fence-states.svg'), W, H, *f)


def fig_implicit_vs_explicit():
    """Та сама трійця пристроїв: спершу огорожі сховані в буфері, потім — у руках програми."""
    W, H = 1060, 540
    f = []

    CAM, GPU, DSP = 300, 540, 780
    BW = 190

    def devices(y):
        f.append(fitbox(CAM, y, BW, 54, "камера", size=13))
        f.append(fitbox(GPU, y, BW, 54, "обчислювач", size=13))
        f.append(fitbox(DSP, y, BW, 54, "дисплей", size=13))
        f.append(arrow(CAM + BW + 6, y + 27, GPU - 6, y + 27))
        f.append(arrow(GPU + BW + 6, y + 27, DSP - 6, y + 27))

    # ── смуга 1: неявна ───────────────────────────────────────────────────
    f.append(text(40, 116, "Неявна", size=14, bold=True, anchor="start"))
    f.append(text(40, 140, "програма огорож", size=12, color=MUTED, anchor="start"))
    f.append(text(40, 158, "не бачить зовсім", size=12, color=MUTED, anchor="start"))

    devices(96)
    for cx in (CAM + BW / 2, GPU + BW / 2, DSP + BW / 2):
        f.append(line(cx, 152, cx, 194, color=MUTED, sw=1.2, dash="5,5"))
    f.append(fitbox(300, 196, 670, 48,
                    "буфер: огорожі лежать усередині, драйвери читають їх самі",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    f.append(line(36, 290, 1024, 290, color="#c3c9d1", sw=1.2, dash="8,6"))

    # ── смуга 2: явна ─────────────────────────────────────────────────────
    f.append(text(40, 424, "Явна", size=14, bold=True, anchor="start"))
    f.append(text(40, 448, "програма розкладає", size=12, color=MUTED, anchor="start"))
    f.append(text(40, 466, "дескриптори сама", size=12, color=MUTED, anchor="start"))

    f.append(fitbox(300, 330, 670, 48,
                    "простір користувача: тримає дескриптори огорож і вирішує, хто кого чекає",
                    size=13, fill="#dceffe", stroke=NEG))
    devices(410)

    up = CAM + BW / 2
    f.append(arrow(up, 406, up, 382, color=NEG))
    f.append(text(up + 10, 398, "вихідна", size=11, color=NEG, anchor="start"))

    up = GPU + BW / 2
    f.append(arrow(up, 382, up, 406, color=NEG))
    f.append(text(up + 10, 398, "вхідна", size=11, color=NEG, anchor="start"))

    up = DSP + BW / 2
    f.append(arrow(up, 382, up, 406, color=NEG))
    f.append(text(up + 10, 398, "вхідна", size=11, color=NEG, anchor="start"))

    f.append(text(40, 512,
                  "Пристрої в обох смугах роблять те саме; різниця лише в тому, хто вирішує, на що чекати.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'implicit-vs-explicit.svg'), W, H, *f)


def fig_dma_resv_rule():
    """Список огорож із позначками призначення й два правила очікування."""
    W, H = 1020, 440
    f = []

    f.append(rect(36, 48, 440, 336, fill="#fbfcfd", stroke="#c3c9d1", sw=1.4, rx=10))
    f.append(text(60, 80, "Резервація буфера", size=14, bold=True, anchor="start"))

    rows = [
        (100, "службова — ядро переносить буфер", "#eef2ff", NEG),
        (168, "запис — камера заповнює кадр", "#fdecea", POS),
        (236, "читання — обчислювач читає", "#eaf7ee", FIELD),
        (300, "читання — дисплей виводить", "#eaf7ee", FIELD),
    ]
    for y, label, fill, stroke in rows:
        f.append(fitbox(60, y, 392, 52, label, size=13, fill=fill, stroke=stroke))

    f.append(fitbox(560, 96, 420, 96,
                    "Збираюся читати\nчекаю на записувачів і на службові",
                    size=13, fill="#eaf7ee", stroke=FIELD))
    f.append(fitbox(560, 240, 420, 96,
                    "Збираюся писати\nчекаю на всіх без винятку",
                    size=13, fill="#fdecea", stroke=POS))

    f.append(text(36, 418,
                  "Позначка призначення — обіцянка на майбутнє: що власник огорожі збирається робити з буфером.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'dma-resv-rule.svg'), W, H, *f)


def fig_fence_lineage():
    """Родовід огорож: що саме входило в ядро й у якому випуску."""
    W, H = 1120, 470
    f = []

    X_YEAR = 60          # ліва колонка: рік і випуск ядра
    X_LINE = 250         # вертикальна вісь часу
    X_EVENT = 300        # права колонка: подія

    f.append(line(X_LINE, 70, X_LINE, 420, color=MUTED, sw=2))

    rows = [
        (100, "2013", "Linux 3.10",
         "Android sync framework у staging: sync_pt, sync_timeline, sync_fence (Ерік Ґіллінґ, Google)"),
        (172, "2014", "Linux 3.17",
         "struct fence — спільне ядро огорож, вісімнадцята редакція патча (Мартен Ланкгорст)"),
        (244, "2016", "Linux 4.7",
         "sync_file виходить зі staging у drivers/dma-buf (Ґуставо Падован)"),
        (316, "2016", "Linux 4.10",
         "fence → dma_fence (Кріс Вілсон); явні огорожі в атомарному API DRM"),
        (388, "2022", "Linux 6.0",
         "вивантаження й завантаження огорожі на дескрипторі dma-buf (Джейсон Екстранд)"),
    ]

    for y, year, rel, what in rows:
        f.append(text(X_YEAR, y - 6, year, size=16, bold=True, anchor="start"))
        f.append(text(X_YEAR, y + 16, rel, size=12, color=MUTED, anchor="start"))
        f.append(circle(X_LINE, y, 8, fill=BG, stroke=MUTED, sw=2))
        f.append(fitbox(X_EVENT, y - 27, 780, 54, what, size=13))

    f.append(text(X_YEAR, 445,
                  "Дати — за git ядра: поява файлів у теґах випусків і дати авторства патчів.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'fence-lineage.svg'), W, H, *f)


def fig_sw_sync_run():
    """Хід досліду на sw_sync: два дескриптори, злитий, і мить пробудження."""
    W, H = 1080, 440
    f = []

    T1, T2, T3, T4, T5 = 260, 380, 520, 700, 880
    X0, X1 = 220, 1020
    GREY = ("#f1f2f4", MUTED)
    GREEN = ("#eaf7ee", FIELD)

    bars = [
        (100, "fd A — огорожа шкали A", T1, T4),
        (172, "fd B — огорожа шкали B", T2, T5),
        (244, "злитий fd (A + B)",      T3, T5),
    ]
    for y, label, born, falls in bars:
        f.append(text(36, y + 30, label, size=12, anchor="start"))
        f.append(fitbox(born, y, falls - born, 46,
                        "не спрацювала: poll() тримає", size=12,
                        fill=GREY[0], stroke=GREY[1], color=MUTED))
        f.append(fitbox(falls, y, X1 - falls, 46, "POLLIN", size=12,
                        fill=GREEN[0], stroke=GREEN[1]))

    f.append(line(X0, 368, X1, 368, color=INK, sw=1.4))
    events = [
        (T1, "CREATE_FENCE\nA, value 5"),
        (T2, "CREATE_FENCE\nB, value 3"),
        (T3, "SYNC_IOC\n_MERGE"),
        (T4, "INC шкали A\nна 5"),
        (T5, "INC шкали B\nна 3"),
    ]
    for x, label in events:
        f.append(line(x, 300, x, 366, color=MUTED, sw=1.2, dash="4 4"))
        f.append(mtext(x, 388, label, size=11, color=MUTED))

    f.append(text(36, 428,
                  "Дві шкали — два контексти, тому в злитому дескрипторі дві огорожі; "
                  "дві огорожі однієї шкали злиття згорнуло б в одну.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'sw-sync-run.svg'), W, H, *f)


if __name__ == '__main__':
    fig_fence_states()
    fig_implicit_vs_explicit()
    fig_dma_resv_rule()
    fig_fence_lineage()
    fig_sw_sync_run()
    print("ok")
