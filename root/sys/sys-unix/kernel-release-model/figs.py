# -*- coding: utf-8 -*-
"""Фігури до теми «Модель випусків ядра: вікно злиття, -rc і стабільні гілки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eaf7ef"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"
GREY_FILL = "#f4f6f8"


# ── 1. Цикл у часі: вікно злиття, -rc, випуск ──────────────────────────────
def fig_cycle():
    W, H = 1080, 520
    BY, BH = 195, 70            # смуга циклу
    f = []

    # linux-next над вікном
    f.append(fitbox(80, 80, 420, 56,
                    "linux-next: підсистеми зводять докупи щодня,\nзадовго до вікна",
                    size=14, fill=BLUE_FILL, stroke=NEG))
    f.append(arrow(180, 136, 180, 191))

    # смуга циклу
    f.append(fitbox(80, BY, 200, BH, "Вікно злиття\n≈ 2 тижні",
                    size=15, bold=True, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(280, BY, 550, BH,
                    "Стабілізація ≈ 7 тижнів:\nприймають тільки виправлення",
                    size=15, fill=GREY_FILL, stroke=MUTED))
    f.append(fitbox(830, BY, 90, BH, "Випуск\nтег v7.1",
                    size=13, bold=True, fill=RED_FILL, stroke=POS))
    f.append(fitbox(920, BY, 120, BH, "вікно 7.2",
                    size=13, bold=True, fill=GREEN_FILL, stroke=FIELD))

    # кандидати
    step = 550.0 / 7
    for i in range(7):
        cx = 280 + step * (i + 0.5)
        f.append(fitbox(cx - 25, 280, 50, 32, "rc%d" % (i + 1),
                        size=12, fill=BG, stroke=MUTED))
    f.append(text(555, 348,
                  "щотижня, зазвичай у неділю; що ближче до кінця, то суворіший добір",
                  size=13, color=MUTED))

    # стабільна гілка від випуску
    f.append(arrow(875, 267, 812, 392))
    f.append(fitbox(620, 393, 380, 60,
                    "Стабільна гілка: 7.1.1, 7.1.2, 7.1.3 …\nтільки виправлення, нічого нового",
                    size=13, fill=GREY_FILL, stroke=LINE))

    # легенда
    f.append(fitbox(80, 393, 250, 26, "зелене — вливають нове",
                    size=12, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(80, 427, 250, 26, "сіре — тільки лагодять",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'cycle.svg'), W, H, *f,
           title="Один цикл ядра: дві фази того самого дерева")


# ── 2. Шлях однієї латки ───────────────────────────────────────────────────
def fig_patch_path():
    W, H = 960, 740
    CX = 340
    f = []

    steps = [
        (80,  "Автор латки", BG, LINE, False),
        (175, "Дерево супровідника підсистеми", GREY_FILL, LINE, False),
        (270, "linux-next\n(щоденне складання)", BLUE_FILL, NEG, False),
        (365, "mainline — головне дерево", GREEN_FILL, FIELD, True),
        (460, "Випуск: тег v7.1", RED_FILL, POS, True),
        (555, "Стабільна гілка 7.1.z", GREY_FILL, LINE, False),
        (650, "Ядро вашого дистрибутива", BG, LINE, False),
    ]
    for cy, label, fill, stroke, bold in steps:
        frag, w, h = textbox(CX, cy, label, size=15, pad=14,
                             fill=fill, stroke=stroke, bold=bold, min_w=300)
        f.append(frag)

    for cy, _, _, _, _ in steps[:-1]:
        f.append(arrow(CX, cy + 30, CX, cy + 65))

    notes = [
        (127, "рецензія, підпис Signed-off-by"),
        (222, "щодня, задовго до вікна"),
        (317, "тільки у вікні злиття"),
        (412, "після семи тижнів -rc"),
        (500, "Cc: stable, до 100 рядків"),
        (602, "плюс власні латки дистрибутива"),
    ]
    for y, s in notes:
        f.append(text(600, y, s, size=12, color=MUTED, anchor="start", italic=True))

    # LTS — збоку від стабільної гілки
    f.append(arrow(500, 555, 634, 555))
    f.append(fitbox(636, 530, 280, 50,
                    "раз на рік гілку оголошують\nдовгостроковою: роки, а не тижні",
                    size=12, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'patch-path.svg'), W, H, *f,
           title="Шлях латки: кожна стрілка — чиясь порука за зміну")


# ── 3. Тривалість гілок у роках ────────────────────────────────────────────
def fig_branch_lifetimes():
    W, H = 1080, 530
    X0, Y0 = 140.0, 2020.0
    PX = 98.9                    # пікселів на рік

    def x(t):
        return X0 + (t - Y0) * PX

    f = []

    # mainline: часті дрібні випуски
    f.append(text(140, 70, "mainline: новий випуск кожні 9–10 тижнів",
                  size=13, color=MUTED, anchor="start"))
    f.append(arrow(140, 92, 800, 92, color=MUTED, sw=1.4))
    t = 2020.0
    while t < 2026.6:
        f.append(line(x(t), 84, x(t), 100, color=MUTED, sw=1.2))
        t += 0.185

    # довгострокові гілки
    f.append(text(140, 132, "довгострокові гілки (LTS)",
                  size=13, color=MUTED, anchor="start"))
    bars = [
        (150, 2020.95, 2026.95, "5.10 · груд. 2020 → груд. 2026"),
        (190, 2021.83, 2026.95, "5.15 · жовт. 2021 → груд. 2026"),
        (230, 2022.94, 2027.95, "6.1 · груд. 2022 → груд. 2027"),
        (270, 2023.83, 2027.95, "6.6 · жовт. 2023 → груд. 2027"),
        (310, 2024.88, 2028.95, "6.12 · лист. 2024 → груд. 2028"),
        (350, 2025.92, 2028.95, "6.18 · лист. 2025 → груд. 2028"),
    ]
    for y, a, b, label in bars:
        f.append(fitbox(x(a), y, x(b) - x(a), 26, label,
                        size=12, pad=10, fill=GREEN_FILL, stroke=FIELD))

    # звичайні стабільні гілки — короткі
    for i in range(5):
        f.append(rect(600 + i * 40, 400, 20, 26, fill=GREY_FILL, stroke=MUTED))
    f.append(text(600, 452,
                  "звичайні стабільні гілки: кожна живе близько трьох місяців",
                  size=12, color=MUTED, anchor="start"))

    # вісь років
    f.append(line(140, 470, 1035, 470, color=LINE, sw=1.4))
    for yr in range(2020, 2030):
        f.append(line(x(yr), 470, x(yr), 478, color=LINE, sw=1.2))
        f.append(text(x(yr), 496, str(yr), size=12, color=MUTED))

    render(os.path.join(IMG, 'branch-lifetimes.svg'), W, H, *f,
           title="Дві шкали часу: рух mainline і нерухомі точки LTS")


# ── 4. Історія: дві гілки й перехід до одного дерева ───────────────────────
def fig_two_branches():
    W, H = 1240, 430
    X0, Y0 = 120.0, 2001.0
    PX = 130.0

    def x(t):
        return X0 + (t - Y0) * PX

    f = []

    f.append(text(120, 52, "дві лінії: у парній живуть, у непарній розробляють",
                  size=13, color=MUTED, anchor="start"))
    f.append(fitbox(x(2001.01), 66, x(2004.0) - x(2001.01), 34,
                    "2.4 · стабільна для користувачів",
                    size=13, fill=GREY_FILL, stroke=MUTED))
    f.append(fitbox(x(2001.90), 110, x(2003.53) - x(2001.90), 34,
                    "2.5 · лінія розробки",
                    size=13, fill=RED_FILL, stroke=POS))

    f.append(text(120, 178, "одне дерево: розділяють не код, а час",
                  size=13, color=MUTED, anchor="start"))
    f.append(fitbox(x(2003.96), 192, x(2009.0) - x(2003.96), 34,
                    "2.6 · і розробка, і продукт",
                    size=13, bold=True, fill=GREEN_FILL, stroke=FIELD))

    # позначки на осі віх
    f.append(line(120, 254, 1160, 254, color=LINE, sw=1.2))
    for t, label in [(2004.55, "лип. 2004"), (2005.17, "берез. 2005"),
                     (2008.11, "лют. 2008")]:
        f.append(circle(x(t), 254, 5, fill=FIELD, stroke=FIELD))
        f.append(text(x(t), 246, label, size=11, color=MUTED))

    cards = [
        (120, "лип. 2004 · Оттава\nвирішено не відкривати 2.7"),
        (470, "берез. 2005 · 2.6.11.1\nнароджується стабільна гілка"),
        (820, "лют. 2008 · linux-next\nінтеграцію переносять до вікна"),
    ]
    for cx, label in cards:
        f.append(fitbox(cx, 274, 320, 56, label, size=13,
                        fill=BLUE_FILL, stroke=NEG))

    # вісь років
    f.append(line(120, 366, 1160, 366, color=LINE, sw=1.4))
    for yr in range(2001, 2010):
        f.append(line(x(yr), 366, x(yr), 374, color=LINE, sw=1.2))
        f.append(text(x(yr), 392, str(yr), size=12, color=MUTED))

    render(os.path.join(IMG, 'two-branches.svg'), W, H, *f,
           title="Від двох гілок до одного дерева: 2001–2008")


# ── 5. Складання рядка версії (до довідки api-release-metadata) ────────────
def fig_version_string():
    W, H = 1140, 660
    f = []

    segs = [
        ("7", 62, GREEN_FILL, FIELD),
        (".2", 62, GREEN_FILL, FIELD),
        (".0", 62, GREEN_FILL, FIELD),
        ("-rc6", 92, GREEN_FILL, FIELD),
        ("-myfix", 112, GREY_FILL, MUTED),
        ("-custom", 124, GREY_FILL, MUTED),
        ("-00042-g4a1b2c3d4e5f-dirty", 300, BLUE_FILL, NEG),
    ]
    total = float(sum(w for _, w, _, _ in segs))
    LX = (W - total) / 2.0
    BY, BH = 74, 58

    x = LX
    for i, (s, w, fill, stroke) in enumerate(segs):
        f.append(fitbox(x, BY, w, BH, s, size=16, pad=9,
                        fill=fill, stroke=stroke, bold=True))
        f.append(text(x + w / 2.0, BY - 12, str(i + 1), size=12, color=MUTED))
        x += w

    f.append(arrow(W / 2.0, BY + BH + 4, W / 2.0, BY + BH + 26))
    f.append(fitbox(LX, 162, total, 44,
                    "include/config/kernel.release → UTS_RELEASE у include/generated/utsrelease.h",
                    size=14, fill=BG, stroke=LINE))
    f.append(arrow(W / 2.0, 208, W / 2.0, 228))
    f.append(fitbox(LX, 230, total, 44,
                    "uname -r   ·   /proc/sys/kernel/osrelease   ·   початок /proc/version",
                    size=14, fill=GREY_FILL, stroke=LINE))

    f.append(text(LX, 314, "Звідки береться кожна ділянка:",
                  size=15, bold=True, anchor="start"))

    rows = [
        (GREEN_FILL, FIELD, "VERSION — головний номер; перший рядок Makefile"),
        (GREEN_FILL, FIELD, "PATCHLEVEL — другий номер; другий рядок Makefile"),
        (GREEN_FILL, FIELD, "SUBLEVEL — лічильник стабільної гілки; у mainline завжди 0"),
        (GREEN_FILL, FIELD, "EXTRAVERSION — «-rc6» протягом циклу, порожній у випуску"),
        (GREY_FILL, MUTED, "файли localversion* — спершу з теки збірки, потім з теки дерева"),
        (GREY_FILL, MUTED, "CONFIG_LOCALVERSION із .config, далі LOCALVERSION= у команді make"),
        (BLUE_FILL, NEG, "scm_version — комітів від тега, 12 знаків хеша, «-dirty» за незбережені зміни"),
    ]
    y = 350
    for i, (fill, stroke, s) in enumerate(rows):
        f.append(circle(LX + 14, y, 13, fill=fill, stroke=stroke, sw=1.6))
        f.append(text(LX + 14, y + 5, str(i + 1), size=12, bold=True))
        f.append(text(LX + 40, y + 5, s, size=14, anchor="start"))
        y += 44

    render(os.path.join(IMG, 'version-string.svg'), W, H, *f,
           title="Рядок версії: сім джерел, зчеплених підряд")


# ── 6. Один фікс — три різні коміти (до вправи proj-where-is-my-fix) ───────
def fig_fix_identity():
    W, H = 1120, 470
    CA, WA = 40, 190
    CB, WB = 240, 180
    CC, WC = 430, 430
    CD, WD = 870, 210
    f = []

    f.append(text(CA + WA / 2, 82, "гілка", size=13, color=MUTED, bold=True))
    f.append(text(CB + WB / 2, 82, "хеш коміту", size=13, color=MUTED, bold=True))
    f.append(text(CC + WC / 2, 82, "рядок у тілі, який в'яже з оригіналом",
                  size=13, color=MUTED, bold=True))
    f.append(text(CD + WD / 2, 82, "перший тег", size=13, color=MUTED, bold=True))

    rows = [
        (104, "mainline", "9f4a1c2b7e33", RED_FILL, POS,
         "— оригінал, в'язати нема з чим", "v6.13"),
        (186, "linux-6.12.y", "a71c02e5d418", BLUE_FILL, NEG,
         "«commit 9f4a1c2b7e33…7c41 upstream.»", "v6.12.7"),
        (268, "linux-6.6.y", "c30b91d7f5a2", BLUE_FILL, NEG,
         "«[ Upstream commit 9f4a1c2b7e33…7c41 ]»", "v6.6.71"),
    ]
    for y, branch, sha, fill, stroke, body, tag in rows:
        f.append(fitbox(CA, y, WA, 72, branch, size=14, bold=True,
                        fill=GREY_FILL, stroke=LINE))
        f.append(fitbox(CB, y, WB, 72, sha, size=14, fill=fill, stroke=stroke))
        f.append(fitbox(CC, y, WC, 72, body, size=13, fill=BG, stroke=MUTED))
        f.append(fitbox(CD, y, WD, 72, tag, size=14, bold=True,
                        fill=BG, stroke=MUTED))

    f.append(fitbox(40, 356, 1040, 76,
                    "git tag --contains 9f4a1c2b7e33 назве лише v6.13 і новіші: два нижні рядки — інші об'єкти з іншими хешами.\n"
                    "Єдине, що в'яже їх з оригіналом, — його повний 40-символьний хеш у тексті повідомлення. Отже, шукати треба текстом.",
                    size=13, fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'proj-fix-identity.svg'), W, H, *f,
           title="Те саме виправлення під трьома різними хешами")


# ── 7. Смуга уражених випусків (до вправи proj-where-is-my-fix) ────────────
def fig_affected_range():
    W, H = 1080, 350
    f = []

    releases = [(160, "6.0"), (300, "6.1"), (440, "6.6"),
                (600, "6.12"), (760, "6.13"), (900, "6.14")]

    f.append(fitbox(120, 166, 180, 30, "вади ще нема",
                    size=12, fill=GREEN_FILL, stroke=FIELD))
    f.append(fitbox(300, 166, 460, 30, "уражені: від 6.1 до 6.12 включно",
                    size=13, fill=RED_FILL, stroke=POS))
    f.append(fitbox(760, 166, 220, 30, "полагоджено",
                    size=13, fill=GREEN_FILL, stroke=FIELD))

    f.append(line(120, 210, 980, 210, color=LINE, sw=1.6))
    for x, label in releases:
        f.append(line(x, 204, x, 216, color=LINE, sw=1.2))
        f.append(text(x, 236, label, size=12, color=MUTED))

    f.append(fitbox(180, 78, 300, 52,
                    "Fixes: 4d1e6a08c9b2 —\nвада приїхала у 6.1",
                    size=12, fill=BG, stroke=POS))
    f.append(line(300, 132, 300, 164, color=POS, sw=1.4))

    f.append(fitbox(600, 78, 320, 52,
                    "виправлення 9f4a1c2b7e33 —\nmainline 6.13",
                    size=12, fill=BG, stroke=FIELD))
    f.append(line(760, 132, 760, 164, color=FIELD, sw=1.4))

    f.append(text(120, 272, "живі гілки всередині смуги — кожну перевіряти окремо:",
                  size=12, color=MUTED, anchor="start"))
    for x, name in [(120, "linux-6.1.y"), (290, "linux-6.6.y"), (460, "linux-6.12.y")]:
        f.append(fitbox(x, 288, 155, 30, name, size=12,
                        fill=GREY_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'proj-affected-range.svg'), W, H, *f,
           title="Смуга уражених випусків: від коміту з Fixes: до виправлення")


if __name__ == '__main__':
    fig_cycle()
    fig_patch_path()
    fig_branch_lifetimes()
    fig_two_branches()
    fig_version_string()
    fig_fix_identity()
    fig_affected_range()
    print("готово:", os.listdir(IMG))
