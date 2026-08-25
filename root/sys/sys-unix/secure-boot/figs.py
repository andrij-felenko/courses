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
GREY_FILL = "#eceff1"


def tb(cx, cy, lines, **kw):
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Чотири сховища прошивки ─────────────────────────────────────────────
def fig_key_stores():
    W, H = 1520, 640
    p = []

    c1x, c1w = 40, 300
    c2x, c2w = 372, 452
    c3x, c3w = 856, 300
    c4x, c4w = 1188, 292

    p.append(text(c1x + c1w / 2, 74, "сховище", size=15, bold=True))
    p.append(text(c2x + c2w / 2, 74, "що в ньому лежить", size=15, bold=True))
    p.append(text(c3x + c3w / 2, 74, "хто може змінити", size=15, bold=True))
    p.append(text(c4x + c4w / 2, 74, "коли працює", size=15, bold=True))

    rows = [
        ("PK\nключ платформи",
         "один ключ власника машини",
         "лише той, хто тримає\nчинний PK",
         "лише при зміні KEK",
         GREEN_FILL),
        ("KEK\nключі обміну",
         "список тих, кому власник дозволив\nправити бази довіри",
         "підпис ключем PK",
         "лише при зміні db і dbx",
         BLUE_FILL),
        ("db\nбаза дозволених",
         "сертифікати й хеші файлів,\nяким вірять при запуску",
         "підпис одним із KEK",
         "при кожному запуску\nEFI-програми",
         BLUE_FILL),
        ("dbx\nбаза заборонених",
         "хеші й сертифікати, які відкликано\nчерез знайдені вади",
         "підпис одним із KEK",
         "при кожному запуску;\nпереважає над db",
         RED_FILL),
    ]

    y = 96
    rh, gap = 96, 16
    for name, what, who, when, fill in rows:
        p.append(fitbox(c1x, y, c1w, rh, name, size=15, bold=True, fill=fill))
        p.append(fitbox(c2x, y, c2w, rh, what, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(fitbox(c3x, y, c3w, rh, who, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        p.append(fitbox(c4x, y, c4w, rh, when, size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
        y += rh + gap

    frag, _, _, _, _ = tb(W / 2, y + 54,
                          "Окремо стоїть MOK: це список ключів власника, яким завідує не прошивка, а shim.\n"
                          "Прошивка про нього не знає — тому й вносять туди ключ не з системи, а з екрана MokManager.",
                          size=13, fill=WARM_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'key-stores.svg'), W, H, *p)


# ── 2. Прямий шлях і обхід через shim ──────────────────────────────────────
def fig_shim_detour():
    W, H = 1420, 620
    p = []

    p.append(text(W / 2, 66, "хто перевіряє підпис ядра", size=17, bold=True))

    # верхній ряд: прямий шлях
    y1 = 176
    p.append(text(60, y1 - 62, "власні ключі в прошивці", size=15, bold=True, anchor="start"))
    fr, ax0, ax1, _, _ = tb(210, y1, ["прошивка"], size=14, fill=BLUE_FILL, stroke=NEG, min_w=230)
    p.append(fr)
    fr, bx0, bx1, _, _ = tb(700, y1, ["ядро, підписане", "ключем господаря"], size=14,
                            fill=GREEN_FILL, stroke=FIELD, min_w=300)
    p.append(fr)
    p.append(arrow(ax1 + 14, y1, bx0 - 14, y1))
    p.append(text((ax1 + bx0) / 2, y1 - 30, "звіряє з db", size=13, color=MUTED))
    p.append(text(1180, y1 - 24, "ланок дві;", size=13, color=MUTED))
    p.append(text(1180, y1 + 4, "але ключ треба внести", size=13, color=MUTED))
    p.append(text(1180, y1 + 32, "в прошивку самому", size=13, color=MUTED))

    # нижній ряд: обхід через shim
    y2 = 400
    p.append(text(60, y2 - 92, "магазинна машина", size=15, bold=True, anchor="start"))
    fr, cx0, cx1, _, _ = tb(210, y2, ["прошивка"], size=14, fill=BLUE_FILL, stroke=NEG, min_w=230)
    p.append(fr)
    fr, dx0, dx1, _, _ = tb(640, y2, ["shim", "підписаний стороннім", "засвідчувачем"], size=14,
                            fill=WARM_FILL, stroke=POS, min_w=300)
    p.append(fr)
    fr, ex0, ex1, _, _ = tb(1120, y2, ["ядро, підписане", "ключем дистрибутива", "або ключем із MOK"],
                            size=14, fill=GREEN_FILL, stroke=FIELD, min_w=330)
    p.append(fr)
    p.append(arrow(cx1 + 14, y2, dx0 - 14, y2))
    p.append(text((cx1 + dx0) / 2, y2 - 30, "звіряє з db", size=13, color=MUTED))
    p.append(arrow(dx1 + 14, y2, ex0 - 14, y2))
    p.append(text((dx1 + ex0) / 2, y2 - 30, "звіряє власним", size=13, color=MUTED))
    p.append(text((dx1 + ex0) / 2, y2 - 6, "списком ключів", size=13, color=MUTED))

    frag, _, _, _, _ = tb(W / 2, 540,
                          "У db на магазинній машині лежить чужий сертифікат — тож єдиний спосіб стартувати "
                          "без правки прошивки\n"
                          "це мати одну ланку, підписану ним, і всю решту довіри тримати вже всередині неї.",
                          size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'shim-detour.svg'), W, H, *p)


# ── 3. Відкликання: хеші проти поколінь ────────────────────────────────────
def fig_revocation():
    W, H = 1420, 620
    p = []

    lx, rx, pw, py, ph = 40, 740, 640, 96, 400
    p.append(rect(lx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(rect(rx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    p.append(text(lx + pw / 2, 74, "заборона за хешем (dbx)", size=16, bold=True))
    p.append(text(rx + pw / 2, 74, "заборона за поколінням (SBAT)", size=16, bold=True))

    # ліва панель: список хешів
    p.append(fitbox(lx + 40, 130, 560, 66,
                    "один запис на кожен поганий файл",
                    size=14, bold=True, fill=RED_FILL))
    items = [
        "хеш образу GRUB дистрибутива A, версія 2.04",
        "хеш образу GRUB дистрибутива A, версія 2.06",
        "хеш образу GRUB дистрибутива B, версія 2.04",
        "…і так далі — близько 150 записів на одну ваду",
    ]
    yy = 216
    for s in items:
        p.append(fitbox(lx + 40, yy, 560, 46, s, size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))
        yy += 56

    # права панель: покоління
    p.append(fitbox(rx + 40, 130, 560, 66,
                    "один рядок на весь компонент",
                    size=14, bold=True, fill=GREEN_FILL))
    p.append(fitbox(rx + 40, 216, 560, 66,
                    "усередині кожної збірки: «grub, покоління 4»",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(fitbox(rx + 40, 298, 560, 66,
                    "у змінній машини: «grub — не нижче 4»",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))
    p.append(fitbox(rx + 40, 380, 560, 66,
                    "усі старіші збірки всіх дистрибутивів відпадають разом",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    p.append(text(lx + pw / 2, 460, "перевіряє прошивка · оновлюють через прошивку", size=13, color=MUTED))
    p.append(text(rx + pw / 2, 470, "перевіряє shim · оновлюють пакунком", size=13, color=MUTED))

    frag, _, _, _, _ = tb(W / 2, 552,
                          "У прошивці типово близько 32 кБ під усі змінні — а одна подія 2020 року з'їла "
                          "приблизно 10 кБ.\n"
                          "Саме скінченність цієї пам'яті, а не складність криптографії, змусила шукати "
                          "інший спосіб відкликання.",
                          size=13, fill=WARM_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'revocation.svg'), W, H, *p)


# ── 4. Байтова розкладка бази підписів ─────────────────────────────────────
def fig_siglist_layout():
    W, H = 1480, 600
    p = []

    p.append(text(W / 2, 50, "як база db лежить у файлі efivarfs", size=17, bold=True))

    # ряд 1: файл цілком
    p.append(text(40, 96, "файл цілком", size=14, bold=True, anchor="start"))
    y1, h1 = 112, 70
    p.append(fitbox(40, y1, 170, h1, "атрибути\n4 байти", size=13, fill=WARM_FILL, stroke=POS, sw=1.4))
    p.append(fitbox(222, y1, 420, h1, "EFI_SIGNATURE_LIST №0", size=13, fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(654, y1, 420, h1, "EFI_SIGNATURE_LIST №1", size=13, fill=BLUE_FILL, stroke=NEG, sw=1.4))
    p.append(fitbox(1086, y1, 344, h1, "…до кінця файлу", size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    # ряд 2: один список
    p.append(text(40, 228, "один EFI_SIGNATURE_LIST — розгорнуто", size=14, bold=True, anchor="start"))
    y2, h2 = 244, 76
    cells2 = [
        (40, 250, "SignatureType\n16 Б — GUID типу", BLUE_FILL),
        (300, 190, "SignatureListSize\n4 Б", "#ffffff"),
        (500, 210, "SignatureHeaderSize\n4 Б", "#ffffff"),
        (720, 180, "SignatureSize\n4 Б", "#ffffff"),
        (910, 240, "SignatureHeader\n0 Б для чинних типів", GREY_FILL),
        (1160, 120, "запис 0", GREEN_FILL),
        (1290, 140, "запис 1 …", GREEN_FILL),
    ]
    for x, w, s, fill in cells2:
        p.append(fitbox(x, y2, w, h2, s, size=13, fill=fill, stroke=MUTED, sw=1.2))

    # ряд 3: один запис
    p.append(text(40, 366, "один запис (EFI_SIGNATURE_DATA) — розгорнуто", size=14, bold=True, anchor="start"))
    y3, h3 = 382, 76
    p.append(fitbox(290, y3, 380, h3, "SignatureOwner\n16 Б — GUID того, хто вніс",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.4))
    p.append(fitbox(682, y3, 500, h3, "SignatureData\nDER-сертифікат або 32 байти SHA-256",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.4))

    frag, _, _, _, _ = tb(W / 2, 528,
                          "Усі записи одного списку однакового розміру — тому їх кількість не обходять, "
                          "а рахують:\n"
                          "(SignatureListSize − 28 − SignatureHeaderSize) ÷ SignatureSize,   де 28 = 16 + 4 + 4 + 4.",
                          size=13, fill=WARM_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'siglist-layout.svg'), W, H, *p)


# ── 5. Режим налаштування й робочий режим ──────────────────────────────────
def fig_setup_mode():
    W, H = 1420, 670
    p = []

    p.append(text(W / 2, 58, "два режими прошивки — і двері між ними", size=17, bold=True))

    lx, rx, pw = 40, 860, 520
    py, ph = 96, 330
    p.append(rect(lx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(rect(rx, py, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))

    p.append(fitbox(lx + 24, 118, pw - 48, 62,
                    "режим налаштування\nPK порожній", size=15, bold=True, fill=GREEN_FILL))
    p.append(fitbox(lx + 24, 194, pw - 48, 68,
                    "db, KEK і dbx приймають\nбудь-який запис без підпису",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(fitbox(lx + 24, 276, pw - 48, 68,
                    "саме тут кладуть усі списки —\nіншої такої нагоди не буде",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(fitbox(lx + 24, 358, pw - 48, 54,
                    "увійти — лише з меню прошивки",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    p.append(fitbox(rx + 24, 118, pw - 48, 62,
                    "робочий режим\nPK встановлено", size=15, bold=True, fill=BLUE_FILL))
    p.append(fitbox(rx + 24, 194, pw - 48, 68,
                    "запис приймають лише як .auth,\nпідписаний рівнем вище",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(fitbox(rx + 24, 276, pw - 48, 68,
                    "db і KEK — підписом KEK або PK,\nсам PK — лише чинним PK",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))
    p.append(fitbox(rx + 24, 358, pw - 48, 54,
                    "вийти — лише стерши PK з меню",
                    size=13, fill=GREY_FILL, stroke=MUTED, sw=1.2))

    p.append(arrow(576, 240, 844, 240))
    p.append(text(710, 212, "вносимо PK", size=13, color=MUTED))
    p.append(arrow(844, 320, 576, 320, color=MUTED))
    p.append(text(710, 352, "стираємо PK з меню", size=13, color=MUTED))

    p.append(text(W / 2, 478, "порядок внесення, поки машина в режимі налаштування",
                  size=15, bold=True))

    steps = [
        (190, "dbx\nчужі заборони", GREY_FILL, MUTED),
        (470, "db\nчуже + своє", BLUE_FILL, MUTED),
        (750, "KEK\nчуже + своє", BLUE_FILL, MUTED),
        (1030, "PK\nлише своє", WARM_FILL, POS),
    ]
    for bx, label, fill, stroke in steps:
        p.append(fitbox(bx, 502, 200, 64, label, size=14, bold=True,
                        fill=fill, stroke=stroke, sw=1.4))
    for ax in (398, 678, 958):
        p.append(arrow(ax, 534, ax + 64, 534))

    frag, _, _, _, _ = tb(W / 2, 618,
                          "Поки PK порожній, кожен із цих записів безкоштовний.\n"
                          "Щойно ліг PK — прошивка вимагає підпис навіть від того, хто його щойно поставив.",
                          size=13, fill=WARM_FILL, stroke=MUTED, sw=1.2)
    p.append(frag)

    render(os.path.join(IMG, 'setup-mode.svg'), W, H, *p)


fig_key_stores()
fig_shim_detour()
fig_revocation()
fig_siglist_layout()
fig_setup_mode()
print("ok")
