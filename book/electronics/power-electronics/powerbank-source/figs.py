# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── sink-to-source: роль джерела — дзеркало ролі споживача ─────────────────────
# Ідея: ті самі механізми (резистор на CC, VBUS, PD-розмова), лише сторони
# помінялися місцями — споживач, що вішав Rd, тепер вішає Rp і сам живить.

def fig_sink_to_source():
    W, H = 900, 360
    p = []
    mid = W / 2
    p.append(line(mid, 56, mid, 300, color="#d7d7d7", sw=1.4, dash="6 5"))

    # ── ліворуч: наш пристрій БЕРЕ (sink) ──
    p.append(text(225, 78, "Досі: пристрій БЕРЕ", size=13, color=FIELD, bold=True))
    p.append(fitbox(85, 108, 110, 64, "джерело\n(Rp)", size=11, fill="#fdecea",
                    stroke=POS, sw=1.8, bold=True, color=POS))
    p.append(fitbox(320, 108, 120, 64, "наш пристрій\nRd · бере", size=11, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(arrow(195, 140, 318, 140, color=POS, sw=2.4))
    p.append(text(256, 130, "VBUS →", size=10, color=POS, bold=True))
    p.append(text(225, 210, "вішає Rd, просить, споживає", size=11, color=INK))

    # ── праворуч: наш пристрій ДАЄ (source) ──
    p.append(text(675, 78, "Тепер: пристрій ДАЄ", size=13, color=POS, bold=True))
    p.append(fitbox(525, 108, 124, 64, "наш пристрій\nRp · живить", size=11, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(fitbox(770, 108, 110, 64, "споживач\n(Rd)", size=11, fill="#eaf0fd",
                    stroke=NEG, sw=1.8, bold=True, color=NEG))
    p.append(arrow(649, 140, 768, 140, color=POS, sw=2.4))
    p.append(text(708, 130, "VBUS →", size=10, color=POS, bold=True))
    p.append(text(675, 210, "вішає Rp, дає 5 В, у PD відповідає як джерело", size=10.5, color=INK))

    # ── нижня смуга-висновок ──
    box, bw, bh = textbox(mid, 280, "Щоб давати живлення, пристрій бере дзеркальну роль: підтяжка Rp замість Rd,\n"
                          "сам виставляє 5 В на VBUS, а схоче PD — відповідає меню профілів. Інший бік тієї ж розмови.",
                          size=11, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, pad=12)
    p.append(box)

    render(os.path.join(OUT, "sink-to-source.svg"), W, H, *p,
           title="Перевертаємо роль: від споживача до джерела")


# ── otg-boost: однокоміркова батарея нижча за 5 В → потрібен підвищувач ────────
# Ідея: ланцюжок батарея → boost → VBUS → чужий пристрій; підкреслено, що
# 3.0–4.2 В комірки завжди нижчі за 5 В, тож boost обов'язковий.

def fig_otg_boost():
    W, H = 900, 360
    p = []

    p.append(fitbox(70, 116, 150, 92, "батарея 1S\n3.0–4.2 В\n(нижче за 5 В)", size=11,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(arrow(220, 162, 296, 162, color=INK, sw=2.2))
    p.append(fitbox(300, 116, 150, 92, "BOOST ↑\nпідвищувач", size=12,
                    fill="#fdf6e3", stroke="#c89a2b", sw=2, bold=True, color="#a07d1f"))
    p.append(arrow(450, 162, 526, 162, color=POS, sw=2.4))
    p.append(fitbox(530, 116, 130, 92, "VBUS\n5 В", size=14,
                    fill="#fdecea", stroke=POS, sw=1.8, bold=True, color=POS))
    p.append(arrow(660, 162, 716, 162, color=POS, sw=2.2))
    p.append(fitbox(720, 116, 110, 92, "чужий\nпристрій\n(заряджаємо)", size=10.5,
                    fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True, color=NEG))

    p.append(text(W / 2, 250, "Одна літієва комірка дає 3.0–4.2 В — менше за потрібні 5 В на VBUS.",
                  size=11.5, color=INK))
    p.append(text(W / 2, 272, "Тому джерело з однокоміркової батареї обов'язково містить підвищувач до 5 В.",
                  size=11.5, color=INK))

    box, bw, bh = textbox(W / 2, 318, "Цей режим історично звали OTG (on-the-go) — коли пристрій із простого споживача\n"
                          "стає тим, хто сам живить периферію. Суть проста: щоб віддавати 5 В від однієї комірки, її напругу треба підняти.",
                          size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, pad=11)
    p.append(box)

    render(os.path.join(OUT, "otg-boost.svg"), W, H, *p,
           title="Павербанк: підняти батарею до 5 В")


# ── dual-role: той самий порт і бере, і дає (DRP + power-role swap) ────────────
# Ідея: дві сходинки дворольовості — DRP вирішує роль на під'єднанні,
# а PD power-role swap міняє її вже під час роботи, без перетикання кабелю.

def fig_dual_role():
    W, H = 920, 400
    p = []

    # DRP
    p.append(rect(50, 64, 380, 150, fill="#fbfbf8", stroke=INK, sw=1.6, rx=12))
    p.append(text(240, 90, "DRP: чергує Rp ↔ Rd", size=12, color=INK, bold=True))
    p.append(fitbox(95, 116, 110, 40, "Rp (даю)", size=10.5, fill="#fdecea",
                    stroke=POS, sw=1.6, bold=True, color=POS))
    p.append(text(240, 142, "↔", size=20, color=INK, bold=True))
    p.append(fitbox(275, 116, 110, 40, "Rd (беру)", size=10.5, fill="#eafaf0",
                    stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(text(240, 190, "поки не вирішать, хто кому джерело", size=10, color=INK))

    # PD power-role swap
    p.append(rect(490, 64, 380, 150, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=12))
    p.append(text(680, 90, "PD power-role swap", size=12, color=NEG, bold=True))
    p.append(text(680, 110, "ролі міняються без перетикання", size=10, color=INK))
    p.append(fitbox(520, 128, 130, 48, "був споживач\n(брав)", size=10, fill="#eafaf0",
                    stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(arrow(650, 152, 706, 152, color=INK, sw=2))
    p.append(fitbox(708, 128, 130, 48, "став джерело\n(дає)", size=10, fill="#fdecea",
                    stroke=POS, sw=1.6, bold=True, color=POS))

    # приклад: ноутбук
    p.append(rect(120, 246, 680, 92, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=12))
    p.append(text(460, 272, "Приклад: ноутбук", size=12, color=INK, bold=True))
    p.append(text(460, 296, "спершу сам заряджається від доку (споживач) →", size=11, color=INK))
    p.append(text(460, 318, "тоді тим самим кабелем живить телефон (джерело): роль помінялась по PD, дріт не чіпали",
                  size=10.5, color=INK))

    box, bw, bh = textbox(460, 372, "Дворольовий порт корисний скрізь, де пристрій то бере, то віддає — ноутбук, павербанк, телефон із периферією.",
                          size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.4, color=INK, pad=10)
    p.append(box)

    render(os.path.join(OUT, "dual-role.svg"), W, H, *p,
           title="Дворольовість: той самий порт і бере, і дає")


# ── power-path: живити систему й заряджати батарею окремо ──────────────────────
# Ідея: наївна схема (USB→батарея→система) гине з мертвою батареєю; power path
# веде дві лінії — вхід просто в систему й вхід у батарею — тож старт миттєвий.

def fig_power_path():
    W, H = 920, 440
    p = []

    # наївна схема
    p.append(rect(45, 56, 840, 112, fill="#fdf3f2", stroke=POS, sw=1.5, rx=12))
    p.append(text(75, 80, "Наївно: USB → заряд → батарея → система", size=12, color=POS, bold=True, anchor="start"))
    p.append(fitbox(85, 98, 92, 44, "USB", size=10.5, fill=BG, stroke="#c89a2b", sw=1.6, bold=True, color="#a07d1f"))
    p.append(arrow(177, 120, 223, 120, color=INK, sw=1.8))
    p.append(fitbox(225, 98, 112, 44, "батарея", size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True, color=FIELD))
    p.append(arrow(337, 120, 383, 120, color=INK, sw=1.8))
    p.append(fitbox(385, 98, 112, 44, "система", size=10.5, fill="#eaf0fd", stroke=NEG, sw=1.6, bold=True, color=NEG))
    p.append(text(700, 112, "мертва батарея →", size=11, color=POS, bold=True))
    p.append(text(700, 132, "система не стартує", size=10.5, color=INK))

    # power path
    p.append(rect(45, 188, 840, 196, fill="#f1faf3", stroke=FIELD, sw=1.6, rx=12))
    p.append(text(75, 212, "Power path: вузол годує систему напряму, а батарею заряджає окремо",
                  size=12, color=FIELD, bold=True, anchor="start"))
    p.append(fitbox(85, 244, 92, 50, "USB", size=10.5, fill=BG, stroke="#c89a2b", sw=1.8, bold=True, color="#a07d1f"))
    p.append(arrow(177, 269, 243, 269, color=POS, sw=2.4))
    p.append(fitbox(245, 242, 130, 56, "вузол\npower path", size=10.5, fill="#fbfbf8", stroke=INK, sw=2, bold=True))
    p.append(arrow(375, 256, 463, 236, color=POS, sw=2.4))
    p.append(fitbox(465, 212, 130, 48, "система\nпрацює одразу", size=10, fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True, color=NEG))
    p.append(arrow(375, 284, 463, 312, color=FIELD, sw=2.4))
    p.append(fitbox(465, 298, 130, 48, "батарея\nзаряд залишком", size=10, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True, color=FIELD))
    p.append(text(715, 256, "мертва / відсутня батарея —", size=10.5, color=FIELD, bold=True))
    p.append(text(715, 276, "пристрій усе одно вмикається", size=10, color=INK))
    p.append(text(715, 300, "(батарея = буфер, не єдиний шлях)", size=9.5, color=MUTED))

    render(os.path.join(OUT, "power-path.svg"), W, H, *p,
           title="Power path: живити систему й заряджати батарею окремо")


# ── load-sharing: система в пріоритеті, батарея бере залишок ───────────────────
# Ідея: вхідний струм обмежений; у спокої ділиться (система+заряд), а на пік
# батарея доливає струм до входу й тримає просадку VBUS.

def fig_load_sharing():
    W, H = 900, 340
    p = []

    # звичайний режим
    p.append(rect(55, 64, 380, 150, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=12))
    p.append(text(245, 90, "Звичайно: вистачає на все", size=12, color=FIELD, bold=True))
    p.append(text(245, 114, "Iвх = Iсист + Iбат(заряд)", size=13, color=INK, bold=True))
    p.append(rect(90, 134, 310, 30, fill=BG, stroke=MUTED, sw=1.4, rx=6))
    p.append(rect(90, 134, 175, 30, fill="#cfe8d6", stroke=FIELD, sw=0, rx=6))
    p.append(text(177, 154, "система", size=10, color=INK, bold=True))
    p.append(rect(265, 134, 135, 30, fill="#dfeefb", stroke=NEG, sw=0, rx=6))
    p.append(text(332, 154, "заряд батареї", size=9.5, color=INK))
    p.append(text(245, 192, "вхідний ліміт ділиться: систему годуємо першою", size=10, color=INK))

    # піковий режим
    p.append(rect(465, 64, 380, 150, fill="#fdf6e3", stroke="#c89a2b", sw=1.6, rx=12))
    p.append(text(655, 90, "Пік: системі треба більше за вхід", size=12, color="#a07d1f", bold=True))
    p.append(text(655, 114, "Iсист = Iвх + Iбат(розряд)", size=13, color=INK, bold=True))
    p.append(rect(500, 134, 310, 30, fill=BG, stroke=MUTED, sw=1.4, rx=6))
    p.append(rect(500, 134, 195, 30, fill="#dfeefb", stroke=NEG, sw=0, rx=6))
    p.append(text(597, 154, "із входу", size=9.5, color=INK))
    p.append(rect(695, 134, 115, 30, fill="#f6e0c8", stroke="#c89a2b", sw=0, rx=6))
    p.append(text(752, 154, "+ батарея", size=9.5, color=INK))
    p.append(text(655, 192, "батарея допомагає входу — тримає просадку", size=10, color=INK))

    box, bw, bh = textbox(W / 2, 268, "Вхідний струм обмежений тим, що дозволив порт. Розумний вузол стежить за цим лімітом:\n"
                          "не дає сумарному споживанню просадити VBUS, а коли системі замало — підмішує струм батареї.\n"
                          "Це і є динамічний розподіл (load sharing) у power path.",
                          size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.5, color=INK, pad=12)
    p.append(box)

    render(os.path.join(OUT, "load-sharing.svg"), W, H, *p,
           title="Розподіл струму: система в пріоритеті, батарея — із залишку")


# ── good-source: чотири обов'язки джерела ─────────────────────────────────────
# Ідея: чотири картки-запобіжники, кожна на свій ризик — чесність про струм,
# захист виходу, зворотний струм, безпечна зміна ролі.

def fig_good_source():
    W, H = 940, 360
    p = []
    cards = [
        (40,  "Не бреши про струм",   "рекламуй (Rp/PDO)\nлише те, що\nреально витягнеш", FIELD),
        (278, "Обмеж струм і КЗ",     "захист від\nперевантаження й\nкороткого на виході", NEG),
        (516, "Стережи зворотний",    "не дай чужій вищій\nнапрузі затекти\nназад у батарею", POS),
        (754, "Міняй роль безпечно",  "при swap спершу\nзняти живлення,\nтоді перемикати", "#a07d1f"),
    ]
    for x, head, body, col in cards:
        p.append(rect(x, 64, 160, 184, fill=BG, stroke=col, sw=2, rx=12))
        p.append(fitbox(x + 6, 78, 148, 34, head, size=10.5, fill=BG, stroke="none", sw=0, bold=True, color=col))
        p.append(line(x + 18, 116, x + 142, 116, color="#e0e0e0", sw=1))
        p.append(mtext(x + 80, 144, body, size=9.5, color=INK))
        p.append(text(x + 80, 224, "✔", size=18, color=col, bold=True))

    box, bw, bh = textbox(W / 2, 300, "Джерело несе відповідальність: воно вирішує, скільки дати, і мусить пережити жадібний\n"
                          "чи несправний споживач — коротке замикання, перевантаження, спробу зворотного живлення.",
                          size=10.5, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, pad=11)
    p.append(box)

    render(os.path.join(OUT, "good-source.svg"), W, H, *p,
           title="Бути добрим джерелом: чотири запобіжники")


# ── comp-power-path: три силові ключі на системній шині SYS ────────────────────
# Ідея: вхід, батарея й система — три окремі виводи; усе сходиться на SYS через
# три ключі (вхід→SYS, SYS→батарея, батарея→SYS), якими керує контролер.

def fig_comp_power_path():
    W, H = 900, 380
    p = []

    # три зовнішні виводи + центральна шина SYS
    p.append(fitbox(60, 150, 120, 64, "ВХІД\n(USB)", size=11, fill=BG,
                    stroke="#c89a2b", sw=1.8, bold=True, color="#a07d1f"))
    sysx = 400
    p.append(rect(sysx - 70, 120, 140, 124, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    p.append(text(sysx, 110, "системна шина SYS", size=11, color=NEG, bold=True))
    p.append(fitbox(720, 80, 120, 56, "система", size=11, fill="#eaf0fd",
                    stroke=NEG, sw=1.8, bold=True, color=NEG))
    p.append(fitbox(720, 232, 120, 56, "батарея 1S", size=11, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True, color=FIELD))

    # ключ вхід → SYS
    p.append(arrow(180, 182, sysx - 72, 182, color=POS, sw=2.4))
    p.append(text(282, 172, "ключ → SYS", size=9.5, color=POS, bold=True))

    # SYS → система (живлення системи)
    p.append(arrow(sysx + 70, 150, 718, 110, color=POS, sw=2.4))
    p.append(text(600, 128, "SYS → система", size=9.5, color=POS, bold=True))

    # SYS → батарея (заряд залишком)
    p.append(arrow(sysx + 70, 210, 718, 252, color=FIELD, sw=2.2))
    p.append(text(600, 238, "заряд залишком", size=9.5, color=FIELD, bold=True))

    # батарея → SYS (розряд/допомога) — зворотна стрілка нижче
    p.append(arrow(718, 276, sysx + 60, 276, color="#a07d1f", sw=2.2))
    p.append(line(sysx + 60, 276, sysx + 60, 246, color="#a07d1f", sw=2.2))
    p.append(text(560, 296, "батарея → SYS (коли входу нема / на піку)", size=9.5, color="#a07d1f", bold=True))

    box, bw, bh = textbox(W / 2, 344, "Три виводи замість двох. Контролер тримає пріоритет: спершу нагодувати систему із входу,\n"
                          "тоді заряджати батарею залишком, а на піку — підмішати батарею до входу. Батарея = буфер.",
                          size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.5, color=INK, pad=11)
    p.append(box)

    render(os.path.join(OUT, "comp-power-path.svg"), W, H, *p,
           title="Усередині power-path-зарядки: три ключі на шині SYS")


if __name__ == "__main__":
    fig_sink_to_source()
    fig_otg_boost()
    fig_dual_role()
    fig_power_path()
    fig_load_sharing()
    fig_good_source()
    fig_comp_power_path()
    print("OK: figures written to", OUT)
