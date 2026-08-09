# -*- coding: utf-8 -*-
"""Фігури до теми «DRM і KMS: модель графічного пристрою в ядрі»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_scanout_window():
    """Скільки часу дає пауза між кадрами і що ядро встигає в ній зробити."""
    W, H = 1020, 470
    f = []

    # ── верх: один період кадру в справжніх пропорціях ────────────────────
    x0, x1 = 60, 900
    bar_y, bar_h = 70, 46
    act_w = int((16.0 / 16.667) * (x1 - x0))      # видима частина
    act_end = x0 + act_w

    f.append(rect(x0, bar_y, act_w, bar_h, fill="#dceffe", stroke=NEG, sw=1.5))
    f.append(rect(act_end, bar_y, x1 - act_end, bar_h, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text((x0 + act_end) / 2, bar_y + 29,
                  "розгортка 1080 видимих рядків — 16.0 мс", size=13))

    # виноска на вузьку паузу
    f.append(line((act_end + x1) / 2, bar_y + bar_h, (act_end + x1) / 2, bar_y + bar_h + 34,
                  color=POS, sw=1.4))
    f.append(text((act_end + x1) / 2, bar_y + bar_h + 52,
                  "пауза 45 рядків — 0.667 мс", size=13, color=POS))

    f.append(text(x0, bar_y - 16, "один період кадру при 60 Гц — 16.67 мс",
                  size=13, color=MUTED, anchor="start"))

    # ── низ: збільшена пауза ──────────────────────────────────────────────
    zx0, zx1 = 120, 900
    zy = 258
    f.append(rect(zx0, zy, zx1 - zx0, 60, fill="#fdecea", stroke=POS, sw=1.5))

    # промені збільшення
    f.append(line(act_end, bar_y + bar_h + 62, zx0, zy, color=MUTED, sw=1.1, dash="5,5"))
    f.append(line(x1, bar_y + bar_h + 62, zx1, zy, color=MUTED, sw=1.1, dash="5,5"))
    f.append(text((zx0 + zx1) / 2, zy - 18,
                  "та сама пауза, збільшена: усе, що встигне ядро, побачить наступний кадр",
                  size=13, color=MUTED))

    marks = [
        (215, "переривання"),
        (500, "запис нової адреси"),
        (790, "подія на дескрипторі"),
    ]
    for mx, lab in marks:
        f.append(circle(mx, zy + 30, 9, fill=BG, stroke=POS, sw=2))
        f.append(text(mx, zy + 82, lab, size=12, color=INK))
    f.append(arrow(224, zy + 30, 491, zy + 30, color=POS))
    f.append(arrow(509, zy + 30, 781, zy + 30, color=POS))

    f.append(text(60, 408,
                  "Апаратура читає адресу буфера один раз на кадр — на початку. Перезаписати її треба саме тут:",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(60, 432,
                  "раніше — і піввисоти екрана покаже старий буфер, а піввисоти новий; пізніше — зміна чекатиме ще 16.67 мс.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'scanout-window.svg'), W, H, *f)


def fig_object_chain():
    """П'ять сутностей KMS і обмеження, через які це граф, а не конвеєр."""
    W, H = 1060, 620
    f = []

    boxes = [
        (30, "Буфер кадру", ["пам'ять із пікселями:", "формат, крок, ручки"]),
        (235, "Плоскість", ["один вхід мікшера:", "основна, курсор, накладка"]),
        (440, "CRTC", ["розгортка й тайминг:", "одна незалежна картинка"]),
        (645, "Кодер", ["потік пікселів стає", "сигналом свого типу"]),
        (850, "Роз'єм", ["гніздо: підключено чи ні,", "EDID, перелік режимів"]),
    ]
    bw = 180
    for bx, name, caption in boxes:
        f.append(fitbox(bx, 60, bw, 46, name, size=14, bold=True))
        f.append(mtext(bx + bw / 2, 128, caption, size=11.5, color=MUTED, lh=1.5))

    for i in range(len(boxes) - 1):
        x_from = boxes[i][0] + bw
        x_to = boxes[i + 1][0]
        f.append(arrow(x_from + 4, 83, x_to - 4, 83))

    f.append(text(30, 34, "Шлях одного пікселя: кожна ланка — окремий ресурс кристала",
                  size=13, color=MUTED, anchor="start"))

    # ── нижня половина: обмеження ─────────────────────────────────────────
    f.append(text(30, 250, "Ланки не з'єднуються довільно: кожна знає, з ким їй дозволено працювати",
                  size=13, color=MUTED, anchor="start"))

    crtc = [(300, "CRTC 0"), (420, "CRTC 1")]
    conn = [(290, "HDMI"), (410, "DisplayPort"), (530, "eDP панелі")]

    for cy, name in crtc:
        f.append(fitbox(60, cy, 190, 50, name, size=13, bold=True,
                        fill="#dceffe", stroke=NEG))
    for cy, name in conn:
        f.append(fitbox(760, cy, 220, 50, name, size=13, bold=True,
                        fill="#eafaf1", stroke=FIELD))

    enc = [(290, "TMDS"), (410, "DP"), (530, "DSI")]
    for cy, name in enc:
        f.append(fitbox(470, cy, 150, 50, name, size=12))
        f.append(arrow(624, cy + 25, 756, cy + 25, color=MUTED))

    links = [(300, 290), (300, 410), (420, 410), (420, 530)]
    for cy, ey in links:
        f.append(line(254, cy + 25, 466, ey + 25, color=NEG, sw=1.4))

    f.append(text(30, 606,
                  "Два двигуни розгортки на три гнізда: одночасно — щонайбільше дві незалежні картинки, "
                  "і не в будь-якому поєднанні.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'object-chain.svg'), W, H, *f)


def fig_atomic_vs_sequential():
    """Чому перевірка й застосування мають бути одним викликом."""
    W, H = 1020, 520
    f = []

    # ── послідовно ────────────────────────────────────────────────────────
    f.append(text(30, 48, "Послідовно: кожен виклик застосовується сам по собі",
                  size=14, bold=True, anchor="start"))

    steps = [
        (30, "SETCRTC", "новий режим"),
        (370, "SETPLANE", "накладка на весь екран"),
        (710, "PAGE_FLIP", "нова адреса буфера"),
    ]
    for sx, name, what in steps:
        f.append(fitbox(sx, 74, 280, 50, name, size=13, bold=True))
        f.append(text(sx + 140, 146, what, size=12, color=MUTED))

    f.append(arrow(316, 99, 366, 99))
    f.append(arrow(656, 99, 706, 99))

    f.append(circle(170, 186, 10, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(circle(510, 186, 10, fill="#fdecea", stroke=POS, sw=2))
    f.append(circle(850, 186, 10, fill="#eafaf1", stroke=FIELD, sw=2))

    f.append(text(510, 222, "смуги пам'яті не вистачає саме тут",
                  size=12, color=POS))
    f.append(text(30, 254,
                  "Драйвер відмовляє посеред шляху — режим уже змінено, плоскість ні. Спитати наперед нема як.",
                  size=12, color=MUTED, anchor="start"))

    # ── атомарно ──────────────────────────────────────────────────────────
    f.append(text(30, 318, "Атомарно: увесь бажаний стан приїздить одним списком",
                  size=14, bold=True, anchor="start"))

    f.append(fitbox(30, 344, 400, 84,
                    "DRM_IOCTL_MODE_ATOMIC", size=13, bold=True,
                    fill="#dceffe", stroke=NEG))
    f.append(text(230, 448, "пари «об'єкт · властивість · значення»", size=12, color=MUTED))

    f.append(arrow(438, 372, 560, 372, color=FIELD))
    f.append(fitbox(566, 350, 420, 44, "TEST_ONLY: так чи ні, нічого не змінено",
                    size=12, fill="#eafaf1", stroke=FIELD))

    f.append(arrow(438, 410, 560, 410, color=NEG))
    f.append(fitbox(566, 388, 420, 44, "застосувати цілком, на найближчій паузі",
                    size=12, fill="#dceffe", stroke=NEG))

    f.append(text(566, 470, "Проміжного стану не існує: або новий кадр увесь, або старий увесь.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'atomic-vs-sequential.svg'), W, H, *f)


def fig_ums_vs_kms_owners():
    """Хто програмує регістри розгортки до KMS і після нього."""
    W, H = 1040, 440
    f = []

    f.append(line(505, 18, 505, 420, color=MUTED, sw=1.2, dash="5,5"))

    # ── ліворуч: простір користувача виставляє режим ──────────────────────
    f.append(text(250, 32, "До 2009: режим виставляє простір користувача",
                  size=13, bold=True))

    f.append(fitbox(60, 56, 185, 46, "X-сервер, права root", size=12))
    f.append(fitbox(258, 56, 182, 46, "консоль ядра", size=12))

    f.append(arrow(152, 102, 152, 146, color=POS))
    f.append(arrow(349, 102, 349, 146, color=POS))

    f.append(fitbox(60, 150, 380, 48,
                    "спільного розпорядника немає",
                    size=13, bold=True, fill="#fdecea", stroke=POS))

    f.append(arrow(250, 198, 250, 240, color=POS))
    f.append(fitbox(60, 244, 380, 46, "регістри розгортки чипа", size=13))

    f.append(fitbox(60, 314, 380, 100,
                    "сервер упав — консоль мертва · паніку нема куди "
                    "вивести · перемикання екранів перевиставляє режим "
                    "наосліп", size=12, fill="#fdecea", stroke=POS))

    # ── праворуч: режим виставляє ядро ────────────────────────────────────
    f.append(text(785, 32, "Від 2.6.29: режим виставляє ядро", size=13, bold=True))

    f.append(fitbox(566, 56, 200, 46, "композитор, звичайні права", size=12))
    f.append(fitbox(790, 56, 200, 46, "консоль ядра", size=12))

    f.append(arrow(666, 102, 720, 146, color=NEG))
    f.append(arrow(890, 102, 850, 146, color=NEG))

    f.append(fitbox(566, 150, 424, 48, "DRM/KMS — єдиний господар регістрів",
                    size=13, bold=True, fill="#dceffe", stroke=NEG))

    f.append(arrow(778, 198, 778, 240, color=NEG))
    f.append(fitbox(566, 244, 424, 46, "регістри розгортки чипа", size=13))

    f.append(fitbox(566, 314, 424, 100,
                    "падіння композитора не міняє режиму · паніка "
                    "видима на екрані · перемикання екранів без "
                    "перевиставляння", size=12, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG, 'ums-vs-kms-owners.svg'), W, H, *f)


def fig_possible_crtcs_mask():
    """Маска дозволених CRTC індексує МАСИВ, а не номери об'єктів."""
    W, H = 980, 430
    f = []

    cols = [360, 520, 680]          # ліві краї трьох стовпців
    cw = 130
    ids = ["CRTC id 41", "CRTC id 52", "CRTC id 63"]
    bits = ["0", "1", "0"]
    pick = 1                        # який біт увімкнено

    # ── ряд 1: масив res->crtcs[] ─────────────────────────────────────────
    for i, x in enumerate(cols):
        f.append(text(x + cw / 2, 76, "індекс %d" % i, size=12, color=MUTED))
        hot = (i == pick)
        f.append(fitbox(x, 88, cw, 58, ids[i], size=14, bold=hot,
                        fill="#eafaf1" if hot else FILL,
                        stroke=FIELD if hot else LINE))
    f.append(text(55, 122, "res->crtcs[] — як ядро віддало", size=13,
                  color=MUTED, anchor="start"))

    # ── ряд 2: біти маски, рівно під своїми клітинками ────────────────────
    for i, x in enumerate(cols):
        hot = (i == pick)
        f.append(line(x + cw / 2, 146, x + cw / 2, 186,
                      color=FIELD if hot else MUTED, sw=2 if hot else 1.2,
                      dash=None if hot else "4 4"))
        f.append(fitbox(x, 186, cw, 44, bits[i], size=16, bold=hot,
                        fill="#eafaf1" if hot else FILL,
                        stroke=FIELD if hot else LINE,
                        color=FIELD if hot else MUTED))
    f.append(text(55, 213, "possible_crtcs = 0b010", size=13,
                  color=MUTED, anchor="start"))

    # ── висновок ──────────────────────────────────────────────────────────
    f.append(arrow(cols[pick] + cw / 2, 232, cols[pick] + cw / 2, 276, color=FIELD))
    f.append(fitbox(400, 278, 250, 50, "CRTC_ID = 52", size=15, bold=True,
                    fill="#eafaf1", stroke=FIELD))

    f.append(fitbox(55, 358, 870, 52,
                    "Біт 1 означає crtcs[1]. Шукати об'єкт із номером 1 — "
                    "типова помилка: маска нумерує позиції, а не об'єкти.",
                    size=13, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'possible-crtcs-mask.svg'), W, H, *f)


def fig_flip_loop():
    """Один оберт циклу кадру і дві помилки, що з нього випадають."""
    W, H = 1000, 400
    f = []

    bw, bh, by = 180, 74, 118
    xs = [55, 270, 485, 700]
    steps = ["малюємо в буфер,\nякого нема на екрані",
             "ATOMIC: FB_ID → цей буфер\n+ PAGE_FLIP_EVENT",
             "poll(fd) — спимо,\nпоки триває кадр",
             "read: FLIP_COMPLETE,\nбуфери міняються ролями"]
    for x, s in zip(xs, steps):
        f.append(fitbox(x, by, bw, bh, s, size=12.5))
    for x in xs[:-1]:
        f.append(arrow(x + bw + 4, by + bh / 2, x + bw + 31, by + bh / 2, color=NEG))

    # зворотний хід: з останнього кроку назад у перший
    rx, lx, ry = xs[3] + bw / 2, xs[0] + bw / 2, by + bh + 46
    f.append(line(rx, by + bh, rx, ry, color=NEG, sw=1.6))
    f.append(line(rx, ry, lx, ry, color=NEG, sw=1.6))
    f.append(arrow(lx, ry, lx, by + bh + 3, color=NEG))
    f.append(text((rx + lx) / 2, ry + 20, "наступний кадр", size=12, color=MUTED))

    # дві пастки, що ростуть саме з цього циклу
    f.append(fitbox(55, 292, 400, 66,
                    "малювати в той буфер, що на екрані —\n"
                    "верх кадру старий, низ уже новий",
                    size=12.5, fill="#fdecea", stroke=POS))
    f.append(fitbox(490, 292, 400, 66,
                    "надіслати наступний запит, не дочекавшись\n"
                    "події про попередній — EBUSY",
                    size=12.5, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'flip-loop.svg'), W, H, *f)


if __name__ == '__main__':
    fig_scanout_window()
    fig_object_chain()
    fig_atomic_vs_sequential()
    fig_ums_vs_kms_owners()
    fig_possible_crtcs_mask()
    fig_flip_loop()
    print("ok")
