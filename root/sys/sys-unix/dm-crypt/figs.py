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


# ── 1. Номер сектора як єдина відмінність ──────────────────────────────────
def fig_sector_tweak():
    W, H = 1320, 640
    p = []

    x_plain, x_mid, x_cipher = 250, 690, 1120

    p.append(text(x_plain, 100, "що просить записати файлова система",
                  size=14, bold=True))
    p.append(text(x_mid, 100, "ціль crypt", size=14, bold=True))
    p.append(text(x_cipher, 100, "що лягає на носій", size=14, bold=True))

    rows = [
        (185, "сектор 1000", "512 байтів нулів", GREEN_FILL,
         "ключ + номер 1000", "9f 21 c4 …", BLUE_FILL),
        (330, "сектор 2000", "512 байтів нулів", GREEN_FILL,
         "ключ + номер 2000", "3b e7 05 …", BLUE_FILL),
        (475, "сектор 2001", "інший вміст", WARM_FILL,
         "ключ + номер 2001", "c8 4a 91 …", WARM_FILL),
    ]

    for y, num, body, fill, mid, ct, cfill in rows:
        fr, w1, h1 = textbox(x_plain, y, [num, body], size=13, pad=13,
                             fill=fill, stroke=LINE)
        p.append(fr)
        fr2, w2, h2 = textbox(x_mid, y, [mid, "→ свій зсув для кожного блока"],
                              size=13, pad=13, fill=GREY_FILL, stroke=MUTED, sw=1.2)
        p.append(fr2)
        fr3, w3, h3 = textbox(x_cipher, y, ["на носії", ct], size=13, pad=13,
                              fill=cfill, stroke=LINE)
        p.append(fr3)
        p.append(arrow(x_plain + w1 / 2, y, x_mid - w2 / 2, y))
        p.append(arrow(x_mid + w2 / 2, y, x_cipher - w3 / 2, y))

    p.append(text(W / 2, 570,
                  "Однаковий вміст у РІЗНИХ секторах дає різні байти: номер сектора входить у перетворення.",
                  size=13, color=MUTED))
    p.append(text(W / 2, 598,
                  "Однаковий вміст у ТОМУ САМОМУ секторі дає ті самі байти — цього шар приховати не може.",
                  size=13, color=POS))

    render(os.path.join(IMG, 'sector-tweak.svg'), W, H, *p,
           title="Сектор шифрується сам, а різницю дає його номер")


# ── 2. Читання й запис коштують по-різному ─────────────────────────────────
def fig_data_path():
    W, H = 1340, 800
    p = []

    lx, rx = 350, 990
    p.append(line(670, 95, 670, 700, color=MUTED, sw=1.2, dash="6 5"))

    p.append(text(lx, 100, "читання", size=15, bold=True))
    p.append(text(rx, 100, "запис", size=15, bold=True))

    ys = [175, 300, 425, 550, 668]

    left = [
        (["bio на читання", "сторінки кеша поки порожні"], GREEN_FILL),
        (["клон указує на ТІ САМІ сторінки", "жодного виділення пам'яті"], BLUE_FILL),
        (["носій заповнив сторінки", "шифротекстом"], GREY_FILL),
        (["розшифрувати на місці,", "у тих самих сторінках"], WARM_FILL),
        (["завершити оригінальний bio"], GREEN_FILL),
    ]

    right = [
        (["bio на запис", "у сторінках — відкритий текст"], GREEN_FILL),
        (["сторінки належать кешу:", "переписувати їх не можна"], RED_FILL),
        (["узяти сторінки з резервного пулу,", "зашифрувати в них"], WARM_FILL),
        (["клон указує на НОВІ сторінки,", "носій пише їх"], BLUE_FILL),
        (["звільнити сторінки,", "завершити оригінал"], GREEN_FILL),
    ]

    def col(x, rows):
        boxes = []
        for cy, (lines, fill) in zip(ys, rows):
            fr, w, h = textbox(x, cy, lines, size=13, pad=13, fill=fill, stroke=LINE)
            p.append(fr)
            boxes.append((cy, h))
        for a, b in zip(boxes, boxes[1:]):
            p.append(arrow(x, a[0] + a[1] / 2, x, b[0] - b[1] / 2))

    col(lx, left)
    col(rx, right)

    p.append(text(lx, 745, "додаткової пам'яті — нуль", size=13, color=MUTED))
    p.append(text(rx, 745, "пам'яті — стільки ж, скільки даних у польоті",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'data-path.svg'), W, H, *p,
           title="Чому запис через шифр дорожчий за читання")


# ── 3. Ланцюг від пароля до майстер-ключа ──────────────────────────────────
def fig_luks_chain():
    W, H = 1360, 900
    p = []

    cx, ax = 400, 1010
    link_x0, link_x1 = 660, 830

    steps = [
        (110, ["пароль користувача"], GREEN_FILL,
         ["його можна змінити,", "не чіпаючи жодного сектора даних"]),
        (250, ["Argon2id: сіль, час і пам'ять",
               "узяті з опису слота"], WARM_FILL,
         ["повільно й на сотні мегабайтів пам'яті —", "щоб перебір коштував дорого"]),
        (390, ["ключ слота"], BLUE_FILL,
         ["живе лише кілька мілісекунд,", "на диску його немає"]),
        (530, ["розшифрувати матеріал слота", "і згорнути смуги назад"], WARM_FILL,
         ["матеріал роздутий у 4000 смуг:", "затерта частина губить ключ назавжди"]),
        (670, ["майстер-ключ, 512 бітів"], RED_FILL,
         ["узятий із джерела випадковості", "один раз, при створенні тому"]),
        (800, ["рядок таблиці dm-crypt", "або кільце ключів ядра"], GREY_FILL,
         ["далі заголовок не потрібен —", "працює вже сама ціль"]),
    ]

    boxes = []
    for y, lines, fill, note in steps:
        fr, w, h = textbox(cx, y, lines, size=13, pad=14, fill=fill, stroke=LINE)
        p.append(fr)
        nfr, nw, nh = textbox(ax, y, note, size=12, pad=12, fill="#ffffff",
                              stroke=MUTED, sw=1.1)
        p.append(nfr)
        p.append(line(link_x0, y, link_x1, y, color=MUTED, sw=1.1, dash="5 4"))
        boxes.append((y, h))

    for a, b in zip(boxes, boxes[1:]):
        p.append(arrow(cx, a[0] + a[1] / 2, cx, b[0] - b[1] / 2))

    p.append(text(105, 372, "слотів вісім,", size=12, color=MUTED, anchor="start"))
    p.append(text(105, 394, "у LUKS2 — тридцять два;", size=12, color=MUTED, anchor="start"))
    p.append(text(105, 416, "кожен веде до того", size=12, color=MUTED, anchor="start"))
    p.append(text(105, 438, "самого майстер-ключа", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'luks-chain.svg'), W, H, *p,
           title="Пароль не шифрує дані: він лише відмикає майстер-ключ")


# ── 4. Дві граматики опису шифру (для api-вставки) ─────────────────────────
def fig_cipher_spec():
    W, H = 1120, 620
    p = []

    x0 = 70
    SZ, RSZ, PAD, GAP = 16, 12, 14, 34

    def seg_w(lit, role):
        return max(text_width(lit, SZ, True), text_width(role, RSZ)) + 2 * PAD

    def band(y_cap, y_row, caption, segs, sep="-"):
        p.append(text(x0, y_cap, caption, size=13, color=MUTED, anchor="start"))
        x = x0
        for i, (lit, role, fill) in enumerate(segs):
            w = seg_w(lit, role)
            h = 74
            p.append(rect(x, y_row - h / 2, w, h, fill=fill, stroke=LINE))
            p.append(text(x + w / 2, y_row - 6, lit, size=SZ, bold=True))
            p.append(text(x + w / 2, y_row + 20, role, size=RSZ, color=MUTED))
            x += w
            if i < len(segs) - 1:
                p.append(text(x + GAP / 2, y_row + 5, sep, size=20, color=MUTED))
                x += GAP

    band(96, 150, "класична форма:  cipher[:keycount]-chainmode-ivmode[:ivopts]",
         [("aes", "алгоритм", GREEN_FILL),
          ("xts", "режим зчеплення", BLUE_FILL),
          ("plain64", "режим нумерації IV", WARM_FILL)])

    band(246, 300, "форма capi:  ім'я з криптопідсистеми ядра — цілком, із дужками",
         [("capi:xts(aes)", "алгоритм і режим одним іменем", GREEN_FILL),
          ("plain64", "режим нумерації IV", WARM_FILL)])

    band(396, 450, "capi: з автентифікацією — вимагає ще й integrity:<байти>:aead",
         [("capi:authenc(hmac(sha256),xts(aes))", "шифр разом із кодом автентичності",
           GREEN_FILL),
          ("random", "IV лежить у метаданих сектора", RED_FILL)])

    p.append(text(x0, 545,
                  "Роль сегмента визначає позиція, а не назва: останній сегмент — завжди режим нумерації IV.",
                  size=13, color=MUTED, anchor="start"))
    p.append(text(x0, 573,
                  "Двокрапка всередині сегмента — його власний параметр: :keycount у першому, :ivopts в останньому.",
                  size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'cipher-spec.svg'), W, H, *p,
           title="Опис шифру в рядку таблиці: дві форми запису, ті самі ролі")


# ── 5. Місце і зміна розходяться (для proj-вставки) ────────────────────────
def fig_two_coordinates():
    W, H = 1420, 760
    p = []

    top_x, top_y = 700, 105
    lx, rx = 375, 1035

    tfr, tw, th = textbox(top_x, top_y,
                          ["запит: записати сектор 100",
                           "у /dev/mapper/byhand"],
                          size=14, pad=15, fill=GREEN_FILL, stroke=LINE)
    p.append(tfr)

    left = [
        (255, ["МІСЦЕ", "де саме лягають байти"], GREY_FILL),
        (390, ["+ зсув із таблиці: 2048", "(сектори, віддані під заголовок)"], WARM_FILL),
        (525, ["сектор 2148 у /dev/loop0", "= байт 1 099 776 у disk.img"], BLUE_FILL),
    ]
    right = [
        (255, ["ЗМІНА (tweak)", "чим цей сектор відрізняється"], GREY_FILL),
        (390, ["+ iv_offset із таблиці: 0", "(зсув заголовка сюди НЕ входить)"], WARM_FILL),
        (525, ["IV plain64 = 100", "64 00 00 00 00 00 00 00 і ще вісім нулів"], RED_FILL),
    ]

    def col(x, rows):
        boxes = []
        for cy, lines, fill in rows:
            fr, w, h = textbox(x, cy, lines, size=13, pad=14, fill=fill, stroke=LINE)
            p.append(fr)
            boxes.append((cy, h, w))
        for a, b in zip(boxes, boxes[1:]):
            p.append(arrow(x, a[0] + a[1] / 2, x, b[0] - b[1] / 2))
        return boxes

    lb = col(lx, left)
    rb = col(rx, right)

    p.append(arrow(top_x - 70, top_y + th / 2, lx + 70, lb[0][0] - lb[0][1] / 2))
    p.append(arrow(top_x + 70, top_y + th / 2, rx - 70, rb[0][0] - rb[0][1] / 2))

    bfr, bw, bh = textbox(top_x, 680,
                          ["місце 2148 і зміна 100 — два різні числа з одного запиту;",
                           "сплутати їх означає взяти правильні байти й неправильний ключ"],
                          size=13, pad=15, fill="#ffffff", stroke=MUTED, sw=1.2)
    p.append(bfr)
    p.append(arrow(lx, lb[2][0] + lb[2][1] / 2, top_x - 110, 680 - bh / 2))
    p.append(arrow(rx, rb[2][0] + rb[2][1] / 2, top_x + 110, 680 - bh / 2))

    render(os.path.join(IMG, 'two-coordinates.svg'), W, H, *p,
           title="Один запит — дві незалежні координати")


if __name__ == '__main__':
    fig_sector_tweak()
    fig_data_path()
    fig_luks_chain()
    fig_cipher_spec()
    fig_two_coordinates()
    print("ok")
