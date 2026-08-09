# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

WRITTEN = "#dfe8fc"     # уже записано
FREE    = "#ffffff"     # ще порожньо
CONV    = "#e8f4ea"     # звичайна зона
DEAD    = "#ececec"     # хвіст за місткістю
WARM    = "#fff4e0"
WARMLINE = "#b8860b"
COOL    = "#eef2f7"


# ── 1. Звіт про зони → дерево файлів ───────────────────────────────────────
def fig_device_to_tree():
    W, H = 1300, 700
    p = []
    p.append(text(W / 2, 40, "усе, що zonefs робить на монтуванні: один звіт про зони — і дерево файлів",
                  size=18, bold=True, color=INK))

    LX, RX = 60, 760
    BW, BH = 470, 62
    Y0, STEP = 120, 84

    p.append(text(LX + BW / 2, Y0 - 30, "пристрій про себе розповів", size=15, bold=True, color=MUTED))
    p.append(text(RX + BW / 2, Y0 - 30, "що видно в точці монтування", size=15, bold=True, color=MUTED))

    rows = [
        ("зона 0 — звичайна, тут суперблок", CONV, MUTED,
         "назовні не показана взагалі", DEAD, MUTED, False),
        ("зона 1 — звичайна, 256 МіБ", CONV, FIELD,
         "cnv/0   розмір 268435456", CONV, FIELD, True),
        ("зона 2 — послідовна, вказівник 0", FREE, NEG,
         "seq/0   розмір 0", FREE, NEG, True),
        ("зона 3 — послідовна, вказівник 8192", WRITTEN, NEG,
         "seq/1   розмір 8192", WRITTEN, NEG, True),
        ("зона 4 — послідовна, повна", WRITTEN, POS,
         "seq/2   розмір 268435456", WRITTEN, POS, True),
    ]

    for i, (ls, lf, lc, rs, rf, rc, joined) in enumerate(rows):
        y = Y0 + i * STEP
        p.append(fitbox(LX, y, BW, BH, [ls], size=14.5, fill=lf, stroke=lc, sw=2))
        p.append(fitbox(RX, y, BW, BH, [rs], size=14.5, fill=rf, stroke=rc, sw=2))
        if joined:
            p.append(arrow(LX + BW + 14, y + BH / 2, RX - 14, y + BH / 2, color=rc, sw=2.2))
        else:
            p.append(line(LX + BW + 14, y + BH / 2, RX - 14, y + BH / 2,
                          color=MUTED, sw=1.6, dash="7,6"))

    # три тотожності
    notes = [
        "ім'я файлу — це порядковий\nномер зони серед свого ґатунку",
        "розмір файлу — це положення\nвказівника запису в зоні",
        "st_blocks — це місткість зони,\nтобто найбільший розмір файлу",
    ]
    ny = Y0 + len(rows) * STEP + 30
    for i, s in enumerate(notes):
        p.append(fitbox(60 + i * 400, ny, 380, 86, s.split("\n"), size=14,
                        fill=COOL, stroke=NEG, sw=2))

    p.append(fitbox(60, ny + 116, 1180, 62,
                    ["на носій при цьому не пішло жодного запису: єдині метадані zonefs — незмінний суперблок у нульовому секторі"],
                    size=14.5, fill=WARM, stroke=WARMLINE, sw=2))

    render(os.path.join(IMG, 'device-to-tree.svg'), W, H, *p)


# ── 2. Контракт файлу послідовної зони ─────────────────────────────────────
def fig_seq_file_contract():
    W, H = 1300, 810
    p = []
    p.append(text(W / 2, 40, "файл послідовної зони: єдина точка, куди приймуть запис",
                  size=18, bold=True, color=INK))

    SX, SY, SH = 90, 300, 92
    W1 = 300        # уже записано
    W2 = 520        # вільна частина зони
    W3 = 200        # хвіст за місткістю
    wp = SX + W1            # вказівник запису
    cap = SX + W1 + W2      # місткість зони

    p.append(rect(SX, SY, W1, SH, fill=WRITTEN, stroke=NEG, sw=2.2, rx=4))
    p.append(rect(wp, SY, W2, SH, fill=FREE, stroke=LINE, sw=1.8, rx=4))
    p.append(rect(cap, SY, W3, SH, fill=DEAD, stroke=MUTED, sw=1.6, rx=4))

    p.append(text(SX + W1 / 2, SY + SH / 2 + 5, "записані дані", size=14.5, color=INK))
    p.append(text(wp + W2 / 2, SY + SH / 2 + 5, "вільна частина зони", size=14.5, color=MUTED))
    p.append(text(cap + W3 / 2, SY + SH / 2 + 5, "порожнеча", size=14, color=MUTED))

    # ── над смугою: дозволений запис і заборонена зона за місткістю
    p.append(fitbox(wp - 190, 140, 380, 66,
                    ["запис за цим зміщенням —", "єдиний, який приймуть"], size=14.5,
                    fill="#e8f4ea", stroke=FIELD, sw=2.2))
    p.append(arrow(wp, 210, wp, SY - 6, color=FIELD, sw=2.8))

    p.append(fitbox(cap - 190, 140, 380, 66,
                    ["будь-яке звертання за", "місткістю зони — EFBIG"], size=14.5,
                    fill="#fdecea", stroke=POS, sw=2.2))
    p.append(line(cap + 30, 210, cap + 30, SY - 6, color=POS, sw=2, dash="6,5"))

    # ── під смугою: дві позначки
    for x, s in ((wp, "вказівник запису = розмір файлу"),
                 (cap, "місткість зони = st_blocks · 512")):
        p.append(line(x, SY + SH + 2, x, SY + SH + 28, color=MUTED, sw=1.4, dash="4,4"))
        p.append(fitbox(x - 175, SY + SH + 30, 350, 56, [s], size=14,
                        fill="#ffffff", stroke=MUTED, sw=1.8))

    # ── три наслідки контракту
    ry = SY + SH + 116
    consequences = [
        ("запис за будь-яким іншим\nзміщенням — EINVAL", POS, "#fdecea"),
        ("читання за розміром —\nзвичайний кінець файлу", NEG, COOL),
        ("успішний запис зсуває\nвказівник, а з ним і розмір", FIELD, "#e8f4ea"),
    ]
    for i, (s, col, fill) in enumerate(consequences):
        p.append(fitbox(90 + i * 380, ry, 360, 78, s.split("\n"), size=14,
                        fill=fill, stroke=col, sw=2))

    # ── два дозволені скорочення
    ty = ry + 108
    p.append(fitbox(90, ty, 550, 92,
                    ["ftruncate до 0 — скидання зони:",
                     "вміст стерто фізично, вказівник на початку"],
                    size=14.5, fill=WARM, stroke=WARMLINE, sw=2.2))
    p.append(fitbox(700, ty, 550, 92,
                    ["ftruncate до місткости — завершення зони:",
                     "дописувати нікуди, розмір дорівнює місткості"],
                    size=14.5, fill=WARM, stroke=WARMLINE, sw=2.2))

    p.append(fitbox(90, ty + 118, 1160, 58,
                    ["інших значень скорочення немає: обидва дозволені — це команди до самого носія, а не правка обліку"],
                    size=14.5, fill=COOL, stroke=NEG, sw=2))

    render(os.path.join(IMG, 'seq-file-contract.svg'), W, H, *p)


# ── 3. Ворота, крізь які проходить запис (для проєктної вставки) ───────────
def fig_write_gates():
    W, H = 1340, 1130
    p = []
    p.append(text(W / 2, 42, "що ядро перевіряє в записі у файл zonefs і в якому порядку",
                  size=18, bold=True, color=INK))

    GX, GW, GH = 90, 540, 78
    EX, EW = 790, 470
    Y0, STEP = 108, 114

    rows = [
        ("зміщення ≥ місткості зони?",
         "EFBIG — перша ж перевірка,\nще до розбору режиму запису", POS, "#fdecea"),
        ("запис без O_DIRECT у файл\nпослідовної зони?",
         "EIO — прямий запис тут обов'язковий", POS, "#fdecea"),
        ("O_APPEND у файлі\nзвичайної зони?",
         "EINVAL — вказівника запису там немає", POS, "#fdecea"),
        ("довжина перетинає місткість зони?",
         "довжину підрізають:\nвийде КОРОТКИЙ запис, а не помилка", WARMLINE, WARM),
        ("зміщення й довжина кратні\nst_blksize?",
         "EINVAL — вимога прямого вводу-виводу", POS, "#fdecea"),
        ("зміщення дорівнює\nрозмірові файлу?",
         "EINVAL — той самий код, інша причина", POS, "#fdecea"),
        ("запит іде на пристрій",
         "неповний результат перетворюють на EIO", POS, "#fdecea"),
    ]

    for i, (g, e, col, fill) in enumerate(rows):
        y = Y0 + i * STEP
        last = (i == len(rows) - 1)
        gcol = FIELD if last else NEG
        gfill = "#e8f4ea" if last else COOL
        p.append(fitbox(GX, y, GW, GH, g.split("\n"), size=15,
                        fill=gfill, stroke=gcol, sw=2.2))
        p.append(fitbox(EX, y, EW, GH, e.split("\n"), size=14.5,
                        fill=fill, stroke=col, sw=2.2))
        p.append(arrow(GX + GW + 16, y + GH / 2, EX - 16, y + GH / 2, color=col, sw=2.4))
        if not last:
            p.append(arrow(GX + GW / 2, y + GH + 4, GX + GW / 2, y + STEP - 4,
                           color=FIELD, sw=2.4))

    p.append(text(GX + GW / 2, Y0 + len(rows) * STEP - 16,
                  "ліворуч — шлях, яким запит іде далі", size=13.5, color=MUTED))

    p.append(fitbox(GX, Y0 + len(rows) * STEP + 6, EX + EW - GX, 74,
                    ["після невдалого запису вказівник у пам'яті ядра вже зсунуто наперед —",
                     "розмір файлу правлять, перепитавши стан зони в самого пристрою"],
                    size=14.5, fill=WARM, stroke=WARMLINE, sw=2.2))

    render(os.path.join(IMG, 'write-gates.svg'), W, H, *p)


if __name__ == "__main__":
    fig_device_to_tree()
    fig_seq_file_contract()
    fig_write_gates()
    print("done")
