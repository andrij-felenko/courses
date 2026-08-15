# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff3"
WARM = "#b8860b"


# ── 1. Три місця в стосі, куди можна вставити шифр ──────────────────────────
def fig_where_crypto_sits():
    W, H = 1360, 700
    p = [text(W / 2, 40, "три місця в стосі, де можна зашифрувати ті самі дані",
              size=17, bold=True, color=INK)]

    COLW, GAP = 400, 60
    X0 = (W - 3 * COLW - 2 * GAP) / 2
    ROWH, ROWG = 58, 22
    TOP = 130

    columns = [
        ("стос поверх файлової системи", [
            ("програма", GREY_FILL, LINE),
            ("шар шифрування поверх ФС", RED_FILL, POS),
            ("звичайна ФС під ним", BLUE_FILL, NEG),
            ("блоковий шар", GREY_FILL, LINE),
            ("носій", GREY_FILL, LINE),
        ], ["бачить файли, але не бачить,",
            "як ФС розкладає їх по блоках;",
            "той самий вміст лежить у пам'яті",
            "двічі — відкритий і зашифрований"]),

        ("усередині файлової системи", [
            ("програма", GREY_FILL, LINE),
            ("сторінковий кеш: відкритий текст", GREEN_FILL, FIELD),
            ("ФС + fscrypt", RED_FILL, POS),
            ("блоковий шар", GREY_FILL, LINE),
            ("носій", GREY_FILL, LINE),
        ], ["знає і файл, і номер блока в ньому;",
            "кеш один, розміри й зсуви ті самі,",
            "ключ можна дати на окреме піддерево",
            "каталогів, а не на весь розділ"]),

        ("під файловою системою", [
            ("програма", GREY_FILL, LINE),
            ("сторінковий кеш", GREY_FILL, LINE),
            ("файлова система", BLUE_FILL, NEG),
            ("dm-crypt", RED_FILL, POS),
            ("носій", GREY_FILL, LINE),
        ], ["бачить лише сектори розділу",
            "й не знає, чий це файл;",
            "ховає геть усе, разом із метаданими,",
            "але ключ один на весь розділ"]),
    ]

    for ci, (head, rows, note) in enumerate(columns):
        x = X0 + ci * (COLW + GAP)
        p.append(mtext(x + COLW / 2, 82, [head], size=15, bold=True, color=INK))
        for ri, (label, fill, stroke) in enumerate(rows):
            y = TOP + ri * (ROWH + ROWG)
            p.append(fitbox(x, y, COLW, ROWH, label, size=14.5,
                            fill=fill, stroke=stroke,
                            sw=2.2 if fill == RED_FILL else 1.3,
                            bold=(fill == RED_FILL)))
            if ri < len(rows) - 1:
                p.append(line(x + COLW / 2, y + ROWH, x + COLW / 2, y + ROWH + ROWG,
                              color=MUTED, sw=1.2))
        p.append(mtext(x + COLW / 2, TOP + 5 * (ROWH + ROWG) + 34, note,
                       size=13.5, color=MUTED))

    return render(os.path.join(IMG, 'where-crypto-sits.svg'), W, H, *p)


# ── 2. Дерево ключів: з чого й що виводять ──────────────────────────────────
def fig_key_tree():
    W, H = 1280, 760
    p = [text(W / 2, 40, "що з чого виводять і що з цього лежить на носії відкрито",
              size=17, bold=True, color=INK)]

    b, bw, bh = textbox(300, 110, ["головний ключ", "16–64 байти, тільки в пам'яті ядра"],
                        size=14.5, fill=RED_FILL, stroke=POS, sw=2.2)
    p.append(b)
    b2, bw2, bh2 = textbox(960, 110, ["nonce файлу", "16 випадкових байтів у xattr inode"],
                           size=14.5, fill=WARM_FILL, stroke=WARM)
    p.append(b2)

    KX, KY = 630, 250
    kb, kbw, kbh = textbox(KX, KY, ["HKDF-SHA512"], size=16, bold=True,
                           fill=BLUE_FILL, stroke=NEG, sw=2, min_w=250)
    p.append(kb)
    p.append(arrow(300, 110 + bh / 2, KX - 90, KY - kbh / 2, color=POS, sw=1.8))
    p.append(arrow(960, 110 + bh2 / 2, KX + 90, KY - kbh / 2, color=WARM, sw=1.8))

    outs = [
        (200, ["ідентифікатор ключа", "16 байтів"],
         ["записаний у політику",
          "ВІДКРИТО: каже, якого",
          "ключа просить файл,",
          "і не каже, який він"]),
        (630, ["ключ файлу", "свій у кожного inode"],
         ["IV = номер блока у файлі;",
          "однаковий IV у різних файлах",
          "нешкідливий, бо ключі різні"]),
        (1060, ["ключ режиму", "один на всю політику"],
         ["для апаратного шифрувальника,",
          "у якого лічені комірки ключів;",
          "IV = номер inode ‖ номер блока"]),
    ]
    OY = 430
    for cx, lbl, note in outs:
        ob, obw, obh = textbox(cx, OY, lbl, size=14.5, fill=GREEN_FILL, stroke=FIELD)
        p.append(ob)
        p.append(arrow(KX, KY + kbh / 2, cx, OY - obh / 2, color=NEG, sw=1.6))
        p.append(mtext(cx, OY + obh / 2 + 34, note, size=13.5, color=MUTED))

    p.append(line(60, 650, W - 60, 650, color=MUTED, sw=1.2, dash="6 5"))
    p.append(mtext(W / 2, 686,
                   ["на носії відкрито лежать: версія політики, ідентифікатор ключа, назви режимів і nonce кожного файлу.",
                    "Самого ключа немає ніде на носії — він з'являється лише в пам'яті ядра, коли його туди подали."],
                   size=14, color=INK))

    return render(os.path.join(IMG, 'key-tree.svg'), W, H, *p)


# ── 3. Той самий каталог у трьох поглядах ───────────────────────────────────
def fig_dir_three_views():
    W, H = 1400, 720
    p = [text(W / 2, 40, "той самий каталог: з ключем, на носії та без ключа",
              size=17, bold=True, color=INK)]

    PW, PGAP = 400, 100
    X0 = (W - 3 * PW - 2 * PGAP) / 2
    PY, PH = 110, 280

    panels = [
        ("що бачить власник", GREEN_FILL, FIELD, [
            ("звіт.pdf", "184 320 Б · 12:31 · uid 1000"),
            ("нотатки.txt", "1 024 Б · 09:04 · uid 1000"),
            ("фото/", "каталог · 08:12 · uid 1000"),
        ]),
        ("що лежить у каталозі на носії", GREY_FILL, LINE, [
            ("9f 2c 41 … (32 байти)", "184 320 Б · 12:31 · uid 1000"),
            ("07 b8 e5 … (32 байти)", "1 024 Б · 09:04 · uid 1000"),
            ("d3 41 aa … (32 байти)", "каталог · 08:12 · uid 1000"),
        ]),
        ("що бачить система без ключа", BLUE_FILL, NEG, [
            ("nyLEwEhVe0RY9c4t…", "184 320 Б · 12:31 · uid 1000"),
            ("Bc7QpS2mKZa1vJx0…", "1 024 Б · 09:04 · uid 1000"),
            ("Tm9rZXlOYW1lXzMx…", "каталог · 08:12 · uid 1000"),
        ]),
    ]

    centers = []
    for pi, (head, fill, stroke, rows) in enumerate(panels):
        x = X0 + pi * (PW + PGAP)
        centers.append(x + PW / 2)
        p.append(rect(x, PY, PW, PH, fill="#ffffff", stroke=stroke, sw=1.8, rx=8))
        p.append(fitbox(x, PY, PW, 46, head, size=14.5, bold=True,
                        fill=fill, stroke=stroke, sw=1.8))
        for ri, (name, meta) in enumerate(rows):
            ry = PY + 60 + ri * 74
            p.append(mtext(x + 20, ry + 16, [name], size=14.5, color=INK, anchor="start"))
            p.append(mtext(x + 20, ry + 40, [meta], size=12.5, color=MUTED, anchor="start"))

    for i in (0, 1):
        x1 = X0 + i * (PW + PGAP) + PW + 14
        x2 = X0 + (i + 1) * (PW + PGAP) - 14
        p.append(arrow(x1, PY + PH / 2, x2, PY + PH / 2, color=POS, sw=2))

    notes = [
        ["ім'я шифрують ключем каталогу", "з тим самим IV — тому пошук",
         "працює простим порівнянням байтів"],
        ["коротші за 16 байтів імена доповнюють", "нулями, решту — до 4, 8, 16 чи 32 байтів,",
         "щоб довжина імені не видавала себе"],
        ["видно й можна: ls, rm, rmdir, stat", "не можна: відкрити, обрізати,",
         "створити, перейменувати — ENOKEY"],
    ]
    for cx, note in zip(centers, notes):
        p.append(mtext(cx, PY + PH + 46, note, size=13.5, color=MUTED))

    p.append(line(70, 610, W - 70, 610, color=MUTED, sw=1.2, dash="6 5"))
    p.append(mtext(W / 2, 648,
                   ["однакове в усіх трьох поглядах: розмір, час, власник, права, число файлів і форма дерева каталогів.",
                    "Шифр ховає вміст файлу й текст імені — і нічого понад те."],
                   size=14, color=INK))

    return render(os.path.join(IMG, 'dir-three-views.svg'), W, H, *p)


# ── 4. Родовід файлового шифрування: кожен крок лікує ваду попереднього ─────
def fig_encryption_lineage():
    rows = [
        (["2006 · eCryptfs, ядро 2.6.19", "шифр стосом ПОВЕРХ готової ФС"], GREY_FILL,
         ["той самий вміст осідає в пам'яті двічі — відкритий зверху,",
          "зашифрований знизу; у кожному файлі власний заголовок,",
          "зашифроване ім'я довшає на третину"]),
        (["2015 · шифрування ext4, ядро 4.1", "шифр УСЕРЕДИНІ файлової системи"], BLUE_FILL,
         ["подвійного кешу більше немає: сторінку шифрують у тимчасовий",
          "буфер дорогою на носій. Але код лежав у fs/ext4 і був лише її —",
          "f2fs мусив би переписати те саме в себе"]),
        (["2016 · fs/crypto, ядро 4.6", "спільний код для ext4, f2fs і решти"], BLUE_FILL,
         ["одна підсистема на всі файлові системи. Ключі все ще v1:",
          "головний ключ шукають у зв'язках процесу за описовим",
          "дескриптором, ключ файлу виводять AES-128-ECB під nonce"]),
        (["2016 · Android 7.0, FBE", "сховища DE (до входу) і CE (після)"], GREEN_FILL,
         ["телефон завантажується до робочого стану, поки дані власника",
          "ще замкнені, — того, чого один ключ на весь розділ дати не міг.",
          "З Android 10 нові пристрої зобов'язані так робити"]),
        (["2019 · Adiantum, ядро 5.0", "режим для процесорів без AES"], WARM_FILL,
         ["на дешевому ARM Cortex-A7 AES-256-XTS з'їдав надто багато:",
          "Adiantum на блоках 4096 байтів шифрує вчетверо, а розшифровує",
          "вп'ятеро швидше — шифрування перестало бути платною опцією"]),
        (["2019 · політики v2, ядро 5.4", "HKDF-SHA512 і зв'язка ключів ФС"], GREEN_FILL,
         ["ключ кладуть у зв'язку самої файлової системи й упізнають за",
          "16-байтовим ідентифікатором, теж виведеним KDF: підсунути",
          "чужий ключ уже не вийде, а прибрати свій — вийде напевно"]),
    ]

    W = 1500
    TOP, STEP = 118, 152
    BOXX, BOXW, BOXH = 70, 470, 100
    NOTEX = 620
    H = TOP + (len(rows) - 1) * STEP + BOXH + 46

    p = [text(W / 2, 44, "родовід файлового шифрування в Linux: кожен крок — відповідь на ваду попереднього",
              size=17, bold=True, color=INK),
         text(NOTEX, 86, "що з цього вийшло і що лишалося болючим",
              size=13.5, bold=True, color=MUTED, anchor="start")]

    for i, (label, fill, note) in enumerate(rows):
        y = TOP + i * STEP
        p.append(fitbox(BOXX, y, BOXW, BOXH, label, size=15, bold=True, fill=fill))
        ny = y + BOXH / 2 - (len(note) - 1) * 13.5 * 1.3 / 2 + 5
        p.append(mtext(NOTEX, ny, note, size=13.5, color=INK, anchor="start"))
        if i + 1 < len(rows):
            p.append(arrow(BOXX + BOXW / 2, y + BOXH + 6,
                           BOXX + BOXW / 2, y + STEP - 6, color=NEG, sw=2))

    return render(os.path.join(IMG, 'encryption-lineage.svg'), W, H, *p)


# ── 5. Три стани ключа й переходи між ними ──────────────────────────────────
def fig_key_lifecycle():
    W, H = 1420, 700
    p = [text(W / 2, 40, "три стани ключа у файловій системі й переходи між ними",
              size=17, bold=True, color=INK)]

    CY = 230
    states = [
        (235, ["FSCRYPT_KEY_STATUS_ABSENT · 1", "ключа у файловій системі немає"],
         GREY_FILL, LINE,
         ["відкрити чи створити файл під цим ключем —",
          "ENOKEY; ls, stat, rm працюють і без нього"]),
        (700, ["FSCRYPT_KEY_STATUS_PRESENT · 2", "ключ у пам'яті файлової системи"],
         GREEN_FILL, FIELD,
         ["user_count — скільки користувачів його заявили;",
          "REMOVE_KEY від одного з кількох знімає лише",
          "його заявку: 0 з прапорцем OTHER_USERS,",
          "стан лишається PRESENT"]),
        (1180, ["FSCRYPT_KEY_STATUS_INCOMPLETELY_REMOVED · 3",
                "секрет затерто, частина файлів ще відкрита"],
         WARM_FILL, WARM,
         ["нові відкриття вже дають ENOKEY,",
          "а ключі вже відкритих файлів ядро",
          "не забирає — вони дочитають своє"]),
    ]

    edges = {}
    for cx, lbl, fill, stroke, note in states:
        b, bw, bh = textbox(cx, CY, lbl, size=14, fill=fill, stroke=stroke, sw=2)
        p.append(b)
        edges[cx] = (cx - bw / 2, cx + bw / 2, CY - bh / 2, CY + bh / 2)
        p.append(mtext(cx, 486, note, size=13, color=MUTED, lh=1.35))

    aL, aR, aT, aB = edges[235]
    pL, pR, pT, pB = edges[700]
    iL, iR, iT, iB = edges[1180]

    p.append(arrow(aR + 10, CY, pL - 10, CY, color=FIELD, sw=2))
    p.append(mtext((aR + pL) / 2, 148,
                   ["FS_IOC_ADD_ENCRYPTION_KEY", "user_count: 0 → 1"],
                   size=13, color=INK))

    p.append(arrow(pR + 10, CY, iL - 10, CY, color=WARM, sw=2))
    p.append(mtext((pR + iL) / 2, 148,
                   ["REMOVE_KEY від останнього користувача,",
                    "коли якісь файли ще відкриті → FILES_BUSY"],
                   size=13, color=INK))

    p.append(line(700, pB, 700, 350, color=NEG, sw=2))
    p.append(line(700, 350, 235, 350, color=NEG, sw=2))
    p.append(arrow(235, 350, 235, aB + 6, color=NEG, sw=2))
    p.append(mtext(467, 320,
                   ["REMOVE_KEY від останнього користувача, коли жоден файл не відкрито:",
                    "секрет затерто, кеші імен і сторінок скинуто, повернено 0 без прапорців"],
                   size=13, color=NEG))

    p.append(line(1180, iB, 1180, 424, color=WARM, sw=2))
    p.append(line(1180, 424, 62, 424, color=WARM, sw=2))
    p.append(line(62, 424, 62, CY, color=WARM, sw=2))
    p.append(arrow(62, CY, aL - 10, CY, color=WARM, sw=2))
    p.append(mtext(680, 400,
                   ["закрити ті файли й повторити REMOVE_KEY — саме воно не довершиться"],
                   size=13, color=WARM))

    p.append(line(70, 578, W - 70, 578, color=MUTED, sw=1.2, dash="6 5"))
    p.append(mtext(W / 2, 614,
                   ["FS_IOC_GET_ENCRYPTION_KEY_STATUS читає цей стан і не потребує жодних прав:",
                    "відсутній ключ він показує станом ABSENT, а не помилкою ENOKEY."],
                   size=14, color=INK))

    return render(os.path.join(IMG, 'key-lifecycle.svg'), W, H, *p)


# ── 6. Точні байти на вході HKDF-SHA512 ────────────────────────────────────
def fig_hkdf_bytes():
    W, H = 1320, 800
    p = [text(W / 2, 40, "HKDF-SHA512 так, як його рахує ядро: точні байти на вході",
              size=17, bold=True, color=INK)]

    # ── крок 1: extract ────────────────────────────────────────────────────
    p.append(text(60, 92, "крок 1 · extract", size=15, bold=True,
                  color=INK, anchor="start"))
    p.append(fitbox(60, 108, 330, 66, "ключ HMAC — 64 нульові байти",
                    size=14.5, fill=GREY_FILL))
    p.append(text(225, 194, "солі немає, отже сіль = нулі", size=13, color=MUTED))
    p.append(fitbox(430, 108, 380, 66, "повідомлення — головний ключ, 16…64 Б",
                    size=14.5, fill=WARM_FILL))
    p.append(text(620, 194, "приходить ЗЗОВНІ, ядро його не віддає", size=13, color=MUTED))
    p.append(arrow(820, 141, 890, 141, color=NEG, sw=2))
    p.append(fitbox(900, 108, 330, 66, "PRK — 64 байти", size=15,
                    bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2.2))
    p.append(text(1065, 194, "далі служить ключем HMAC", size=13, color=MUTED))

    # ── крок 2: expand ─────────────────────────────────────────────────────
    p.append(text(60, 262, "крок 2 · expand", size=15, bold=True,
                  color=INK, anchor="start"))
    p.append(text(60, 288, "ключ HMAC — PRK; повідомлення складають так, зліва направо:",
                  size=13.5, color=MUTED, anchor="start"))

    cells = [
        (260, ["T(i−1) — 64 Б", "лише з другої ітерації"], GREY_FILL),
        (250, ["«fscrypt\\0»", "8 Б: сім літер і нуль"], WARM_FILL),
        (170, ["контекст", "1 байт"], RED_FILL),
        (220, ["info", "0 або 16 байтів"], BLUE_FILL),
        (250, ["лічильник", "1 байт, з одиниці"], GREY_FILL),
    ]
    STRIPY, STRIPH = 312, 82
    x = (W - sum(c[0] for c in cells)) / 2
    for w, lines, fill in cells:
        p.append(rect(x, STRIPY, w, STRIPH, fill=fill, sw=1.6, rx=4))
        p.append(mtext(x + w / 2, STRIPY + 32, lines, size=13.5, color=INK))
        x += w

    p.append(arrow(W / 2, STRIPY + STRIPH + 8, W / 2, STRIPY + STRIPH + 52,
                   color=NEG, sw=2))
    p.append(fitbox(W / 2 - 300, STRIPY + STRIPH + 58, 600, 56,
                    "вихід — 64 Б за ітерацію; беруть стільки, скільки треба",
                    size=14.5, fill=GREEN_FILL, stroke=FIELD, sw=2))

    # ── два вживання ───────────────────────────────────────────────────────
    COLS = [(70, 160, "контекст"), (250, 300, "info"),
            (580, 250, "скільки взяти"), (890, 360, "що вийшло")]
    HEADY, ROWY, ROWH, ROWG = 545, 566, 70, 26

    p.append(text(60, 522, "два вживання цієї самої формули", size=15,
                  bold=True, color=INK, anchor="start"))
    for cx, cw, head in COLS:
        p.append(text(cx + cw / 2, HEADY, head, size=13, bold=True, color=MUTED))

    rows = [
        (["1"], ["порожній"], ["16 байтів"],
         ["ідентифікатор ключа —", "лежить у політиці відкрито"], BLUE_FILL),
        (["2"], ["nonce файлу, 16 Б"], ["64 Б для AES-256-XTS"],
         ["ключ цього inode —", "не показує ніхто й ніде"], RED_FILL),
    ]
    for i, (c1, c2, c3, c4, fill) in enumerate(rows):
        y = ROWY + i * (ROWH + ROWG)
        for (cx, cw, _), lines in zip(COLS, (c1, c2, c3, c4)):
            p.append(rect(cx, y, cw, ROWH, fill=fill, sw=1.5))
            p.append(mtext(cx + cw / 2, y + ROWH / 2 - (len(lines) - 1) * 9 + 5,
                           lines, size=13.5, color=INK,
                           bold=(cw == 160)))

    p.append(mtext(W / 2, 738,
                   ["Номери контекстів у заголовках для простору користувача не експортовані —",
                    "їх переписують до себе. Помилка в будь-якій клітинці дає правдоподібний чужий ключ."],
                   size=13.5, color=MUTED))

    return render(os.path.join(IMG, 'hkdf-bytes.svg'), W, H, *p)


if __name__ == '__main__':
    for f in (fig_where_crypto_sits, fig_key_tree, fig_dir_three_views,
              fig_encryption_lineage, fig_key_lifecycle, fig_hkdf_bytes):
        print(f())
