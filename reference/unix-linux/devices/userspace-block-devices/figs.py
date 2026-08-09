# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


def column(p, cx, y0, steps, gap=26, note_gap=24, size=13):
    """Вертикальний ланцюг рамок; під кожною — необов'язкова примітка курсивом.
    steps: список (рядки, заливка, примітка|None). Повертає нижню координату."""
    y = y0
    prev_bottom = None
    for lines, fill, note in steps:
        frag, w, h = textbox(cx, y + 0, lines, size=size, pad=14, fill=fill,
                             stroke=LINE, sw=1.5)
        top = y - h / 2
        if prev_bottom is not None:
            p.append(arrow(cx, prev_bottom + 8, cx, top - 8))
        p.append(frag)
        bottom = y + h / 2
        if note:
            nl = note if isinstance(note, list) else [note]
            for i, ln in enumerate(nl):
                p.append(text(cx, bottom + note_gap + i * 17, ln, size=11.5,
                              color=MUTED, italic=True))
            bottom += note_gap + (len(nl) - 1) * 17 + 6
        prev_bottom = bottom
        y = bottom + gap + 34
    return prev_bottom


# ── 1. Що мусить перетнути межу «ядро ↔ процес» і скільки це важить ─────────
def fig_crossing():
    W, H = 1180, 640
    p = []
    bx = 560                       # сама межа

    p.append(line(bx, 78, bx, 560, color=MUTED, sw=2, dash="8 6"))
    p.append(text(300, 62, "ядро: блоковий шар і драйвер", size=15, bold=True))
    p.append(text(840, 62, "процес-сервер", size=15, bold=True))

    rows = [
        (150, "→", "з'явився запит із тегом N", "≈ 0 байтів\n(саме число тега)", GREEN_FILL),
        (255, "→", "опис: операція, сектор, довжина", "32 байти\nсталого розміру", GREEN_FILL),
        (375, "↔", "корисні дані запиту", "від 512 байтів\nдо мегабайтів", RED_FILL),
        (500, "←", "вердикт: код завершення", "≈ 8 байтів", GREEN_FILL),
    ]
    for y, direction, what, weight, fill in rows:
        if direction in ("→", "↔"):
            p.append(arrow(bx - 150, y, bx + 150, y))
        if direction in ("←", "↔"):
            p.append(arrow(bx + 150, y + (18 if direction == "↔" else 0),
                           bx - 150, y + (18 if direction == "↔" else 0)))
        p.append(text(bx, y - 20, what, size=13.5))
        frag, w, h = textbox(985, y + 4, weight, size=12, pad=11, fill=fill,
                             stroke=MUTED, sw=1.2)
        p.append(frag)

    p.append(text(bx, 600,
                  "Три з чотирьох — десятки байтів. Канал платить за четверте і за кількість переходів межі.",
                  size=13, bold=True))
    render(os.path.join(IMG, 'crossing.svg'), W, H, *p,
           title="Що мусить перетнути межу ядро-процес на кожен запит")


# ── 2. Два транспорти для тієї самої межі ──────────────────────────────────
def fig_two_paths():
    W, H = 1340, 1000
    p = []
    lx, rx = 340, 1000

    p.append(text(lx, 46, "NBD: межа — сокет", size=16, bold=True))
    p.append(text(rx, 46, "ublk: межа — спільна пам'ять і кільце", size=16, bold=True))
    p.append(line(670, 70, 670, 940, color=MUTED, sw=1.2, dash="6 6"))

    left = [
        (["запит у черзі blk-mq", "до /dev/nbd0"], BLUE_FILL, None),
        (["драйвер nbd складає", "28-байтовий заголовок"], WARM_FILL,
         "дані запиту копіюються в буфери сокета"),
        (["мережевий стек", "(навіть якщо це петля 127.0.0.1)"], GREY_FILL,
         ["сегментація, контрольні суми,", "черги передавання"]),
        (["сервер: read() заголовка,", "read() даних"], GREEN_FILL,
         "друга копія — уже в пам'ять сервера"),
        (["обслуговування", "і write() відповіді"], GREEN_FILL,
         "щонайменше три системні виклики на запит"),
    ]
    right = [
        (["запит у черзі blk-mq", "до /dev/ublkb0, тег N"], BLUE_FILL, None),
        (["драйвер ublk заповнює", "слот N спільної ділянки"], WARM_FILL,
         "опис не пересилається — він уже видимий серверові"),
        (["завершується заздалегідь", "подана команда FETCH"], WARM_FILL,
         "сповіщення = запис у кільце завершень"),
        (["сервер читає слот N", "просто з пам'яті"], GREEN_FILL,
         "жодного системного виклику на здобуття опису"),
        (["обслуговування", "і COMMIT_AND_FETCH"], GREEN_FILL,
         ["одна операція одразу віддає результат", "і знову озброює слот"]),
    ]

    column(p, lx, 130, left)
    column(p, rx, 130, right)

    frag, w, h = textbox(lx, 930, ["дані: дві копії", "плюс шлях крізь мережевий стек"],
                         size=12.5, pad=12, fill=RED_FILL, stroke=POS, sw=1.4)
    p.append(frag)
    frag, w, h = textbox(rx, 930, ["дані: одна копія,", "а з ядра 6.15 — жодної"],
                         size=12.5, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    p.append(frag)

    render(os.path.join(IMG, 'two-paths.svg'), W, H, *p,
           title="Шлях одного запиту через NBD і через ublk")


# ── 3. Тег як індекс слота: цикл FETCH → COMMIT_AND_FETCH ──────────────────
def fig_ublk_cycle():
    W, H = 1300, 760
    p = []

    # ліворуч — ядро
    frag, w, h = textbox(180, 300, ["blk-mq видав запит", "теґ 2 у черзі 0"],
                         size=13, pad=14, fill=BLUE_FILL)
    p.append(frag)

    # посередині — масив слотів
    ax, ay, aw, ah = 430, 150, 380, 300
    p.append(rect(ax - 18, ay - 66, aw + 36, ah + 92, fill="#ffffff",
                  stroke=MUTED, sw=1.4, rx=10))
    p.append(mtext(ax + aw / 2, ay - 40,
                   ["спільна ділянка: mmap(/dev/ublkc0)",
                    "масив ublksrv_io_desc, індекс = (черга, теґ)"],
                   size=12.5, color=MUTED))
    slots = [
        ("слот 0 — вільний", GREY_FILL),
        ("слот 1 — вільний", GREY_FILL),
        ("слот 2 — READ, сектор 4096, 32 КіБ", WARM_FILL),
        ("слот 3 — вільний", GREY_FILL),
    ]
    sh = 60
    for i, (s, fill) in enumerate(slots):
        p.append(fitbox(ax, ay + i * (sh + 15), aw, sh, s, size=12.5, pad=12, fill=fill))
    p.append(arrow(330, 300, ax - 26, ay + 2 * (sh + 15) + sh / 2))

    # праворуч — сервер і кільце
    frag, w, h = textbox(1090, 175, ["потік черги 0", "з власним io_uring"],
                         size=13, pad=14, fill=GREEN_FILL)
    p.append(frag)
    frag, w, h = textbox(1090, 330, ["кільце завершень:", "прийшов теґ 2"],
                         size=12.5, pad=13, fill=WARM_FILL)
    p.append(frag)
    frag, w, h = textbox(1090, 490, ["обслуговування:", "звідки взяти ці 32 КіБ"],
                         size=12.5, pad=13, fill=GREEN_FILL)
    p.append(frag)
    frag, w, h = textbox(1090, 645, ["кільце подання:", "COMMIT_AND_FETCH, теґ 2"],
                         size=12.5, pad=13, fill=WARM_FILL)
    p.append(frag)

    p.append(arrow(1090, 220, 1090, 292))
    p.append(arrow(1090, 372, 1090, 450))
    p.append(arrow(1090, 532, 1090, 604))

    # читання слота без системного виклику
    p.append(line(ax + aw + 22, ay + 2 * (sh + 15) + sh / 2, 940, 490,
                  color=MUTED, sw=1.3, dash="5 4"))
    p.append(mtext(700, 545, ["читання слота — звичайне",
                              "звертання до пам'яті"],
                   size=12, color=MUTED))

    # замикання циклу
    p.append(text(650, 705, "COMMIT_AND_FETCH одним рухом віддає результат і знову озброює слот 2",
                  size=13, bold=True))
    p.append(line(940, 645, 250, 645, color=FIELD, sw=1.6, dash="7 5"))
    p.append(arrow(250, 645, 180, 360, color=FIELD))

    render(os.path.join(IMG, 'ublk-cycle.svg'), W, H, *p,
           title="Теґ запиту як індекс слота і цикл fetch-commit")


# ── 4. Порядок запуску сервера: що існує після кожного кроку ────────────────
def fig_startup_order():
    W, H = 1280, 800
    p = []
    lx = 340          # центр колонки кроків
    rx = 720          # початок колонки «що вже існує»

    p.append(text(lx, 46, "що робить сервер", size=15, bold=True))
    p.append(text(rx + 210, 46, "що після цього існує в системі", size=15, bold=True))
    p.append(line(rx - 40, 66, rx - 40, 742, color=MUTED, sw=1.4, dash="8 6"))

    steps = [
        (["відкрити /dev/ublk-control,", "кільце з IORING_SETUP_SQE128"], GREY_FILL,
         ["ще нічого;", "керуюча команда — 32 байти, у звичайний SQE не влазить"]),
        (["ADD_DEV:", "одна черга, глибина 64"], BLUE_FILL,
         ["з'явився символьний /dev/ublkc0;",
          "ядро вписало номер пристрою назад у структуру"]),
        (["SET_PARAMS:", "ємність, логічний блок, кеш"], BLUE_FILL,
         ["геометрія оголошена;",
          "не оголосив кеш — FLUSH не прийде ніколи"]),
        (["відкрити /dev/ublkc0, mmap описів,", "буфери на кожен тег"], GREEN_FILL,
         ["канал є: 64 комірки по 32 байти;",
          "пам'ять під дані виділена наперед і закріплена"]),
        (["FETCH_REQ на всі 64 теги,", "один submit"], WARM_FILL,
         ["кожен тег озброєний, лічильник ядра повний;",
          "цей потік став власником черги"]),
        (["START_DEV(pid цього процесу)"], BLUE_FILL,
         ["з'явився блоковий /dev/ublkb0;",
          "звідси приходить перший запит"]),
    ]

    y = 110
    prev_bottom = None
    for lines, fill, notes in steps:
        frag, w, h = textbox(lx, y, lines, size=13, pad=14, fill=fill)
        if prev_bottom is not None:
            p.append(arrow(lx, prev_bottom + 6, lx, y - h / 2 - 6))
        p.append(frag)
        for i, ln in enumerate(notes):
            p.append(text(rx, y - 9 + i * 20, ln, size=12.5, color=MUTED,
                          anchor="start", italic=True))
        p.append(line(lx + w / 2 + 10, y, rx - 46, y, color=MUTED, sw=1.1,
                      dash="4 4"))
        prev_bottom = y + h / 2
        y = prev_bottom + 62 + 34

    # чому саме такий порядок
    p.append(line(lx - 118, 592, lx - 118, 690, color=FIELD, sw=2))
    p.append(arrow(lx - 118, 690, lx - 118, 700, color=FIELD))
    p.append(mtext(lx - 260, 628, ["START_DEV не поверне", "керування, доки всі теги",
                                   "не озброєні"],
                   size=12.5, color=FIELD))

    render(os.path.join(IMG, 'startup-order.svg'), W, H, *p,
           title="Порядок запуску сервера ublk і що існує після кожного кроку")


fig_crossing()
fig_two_paths()
fig_ublk_cycle()
fig_startup_order()
print("ok")
