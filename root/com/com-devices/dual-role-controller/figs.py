# -*- coding: utf-8 -*-
"""Фігури до теми «Контролер дворольового порту».
Імпортує спільний svgkit зі scripts/ (НЕ переписувати тут). Вивід — у ./img/.
Запуск:  python figs.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

SRC = POS             # джерело — гарячий
SINK = FIELD          # стік — зелений


# ── 1. Один порт — два напрями ───────────────────────────────────────────────
def fig_two_directions():
    W, H = 820, 340
    parts = []
    # центральний порт
    px, py, pw, ph = 330, 120, 160, 80
    parts.append(rect(px, py, pw, ph, fill="#eef2f7", stroke=INK, sw=2))
    parts.append(text(px + pw / 2, py + 34, "USB-C порт", size=15, bold=True))
    parts.append(text(px + pw / 2, py + 58, "(шина VBUS)", size=12, color=MUTED))

    # лівий блок — зарядка (ми стік)
    lx, ly, lw, lh = 40, 120, 150, 80
    parts.append(rect(lx, ly, lw, lh, fill="#eaf3ea", stroke=SINK, sw=2))
    parts.append(text(lx + lw / 2, ly + 34, "чуже джерело", size=13, bold=True, color=SINK))
    parts.append(text(lx + lw / 2, ly + 56, "(зарядка, док)", size=11, color=MUTED))
    # зелена стрілка: живлення В порт (ми споживаємо)
    parts.append(arrow(lx + lw + 6, 148, px - 6, 148, color=SINK, sw=3))
    parts.append(text((lx + lw + px) / 2, 132, "як СТІК: споживаю", size=12, color=SINK, bold=True))

    # правий блок — телефон (ми джерело)
    rx, ry, rw, rh = 630, 120, 150, 80
    parts.append(rect(rx, ry, rw, rh, fill="#fdecea", stroke=SRC, sw=2))
    parts.append(text(rx + rw / 2, ry + 34, "чужий пристрій", size=13, bold=True, color=SRC))
    parts.append(text(rx + rw / 2, ry + 56, "(телефон)", size=11, color=MUTED))
    # червона стрілка: живлення З порту (ми даємо)
    parts.append(arrow(px + pw + 6, 172, rx - 6, 172, color=SRC, sw=3))
    parts.append(text((px + pw + rx) / 2, 196, "як ДЖЕРЕЛО: жену", size=12, color=SRC, bold=True))

    # підсумок
    b, w, h = textbox(W / 2, 285,
                      ["Той самий VBUS — то ВХІД (споживаю чужу напругу), то ВИХІД (жену свою).",
                       "Контролер вирішує напрям і кидає силові ключі — але по черзі, НІКОЛИ разом."],
                      size=12, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "two-directions.svg"), W, H, *parts,
           title="Дворольовий порт: одна шина VBUS у два напрями")


# ── 2. Чергування Rp/Rd на CC, поки не відповість партнер ────────────────────
def fig_drp_toggle():
    W, H = 820, 360
    parts = []
    yHi, yLo = 120, 210          # Rp зверху, Rd знизу
    x_start, x_attach, x_end = 130, 470, 700
    # square wave: чергування до під'єднання
    pts = [(x_start, yLo)]
    x = x_start
    lvl = yLo
    seg = 55
    while x < x_attach - seg:
        pts.append((x, yHi if lvl == yLo else yLo))   # вертикальний фронт
        lvl = yHi if lvl == yLo else yLo
        x += seg
        pts.append((x, lvl))
    # під'єднання: застигаємо на Rp (стали джерелом)
    pts.append((x, yHi))
    pts.append((x_attach, yHi))
    pts.append((x_end, yHi))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
                 'stroke-linejoin="round"/>' % (poly, NEG))
    # рівневі напрямні
    parts.append(line(x_start, yHi, x_end, yHi, color=MUTED, sw=1, dash="3 5"))
    parts.append(line(x_start, yLo, x_end, yLo, color=MUTED, sw=1, dash="3 5"))
    parts.append(text(x_start - 14, yHi + 5, "Rp", size=14, bold=True, color=SRC, anchor="end"))
    parts.append(text(x_start - 14, yLo + 5, "Rd", size=14, bold=True, color=SINK, anchor="end"))
    parts.append(text(W / 2, 72, "«буду джерелом?»  Rp  ↔  Rd  «буду стоком?»", size=12.5,
                      color=MUTED, italic=True))
    # дужка періоду tDRP
    xa, xb = x_start + seg, x_start + 3 * seg
    parts.append(line(xa, 96, xb, 96, color=INK, sw=1.3))
    parts.append(line(xa, 92, xa, 100, color=INK, sw=1.3))
    parts.append(line(xb, 92, xb, 100, color=INK, sw=1.3))
    parts.append(text((xa + xb) / 2, 88, "період ~50–100 мс", size=11, color=INK))
    # момент під'єднання
    parts.append(line(x - 0.5 * seg, 108, x - 0.5 * seg, 250, color=MUTED, sw=1.2, dash="4 3"))
    parts.append(text(x - 0.5 * seg, 268, "партнер під'єднався", size=11, color=MUTED, italic=True))
    # застигла роль
    parts.append(text((x_attach + x_end) / 2, yHi - 14,
                      "тримає Rp → я ДЖЕРЕЛО", size=12.5, bold=True, color=SRC))
    # підсумок
    b, w, h = textbox(W / 2, 315,
                      ["Дворольовий контролер гойдає CC Rp↔Rd, поки партнер не відповість;",
                       "чий рівень застиг — той і задав роль.",
                       "Вподобання Try.SRC/Try.SNK схиляє пару в бажаний бік."],
                      size=11.5, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "drp-toggle.svg"), W, H, *parts,
           title="Розв'язання ролі: чергування Rp/Rd на лінії CC")


# ── 3. Двонапрямний ключ VBUS з інтерлоком ───────────────────────────────────
def fig_vbus_switch():
    W, H = 860, 400
    parts = []
    yline = 175
    # ліворуч: наша внутрішня шина (для ролі джерела)
    parts.append(rect(30, 145, 150, 62, fill="#fdecea", stroke=SRC, sw=1.8))
    parts.append(text(105, 170, "внутрішня шина", size=12, bold=True, color=SRC))
    parts.append(text(105, 190, "(перетворювач)", size=10.5, color=MUTED))
    # праворуч: наша система (для ролі стоку)
    parts.append(rect(680, 145, 150, 62, fill="#eaf3ea", stroke=SINK, sw=1.8))
    parts.append(text(755, 170, "наша система", size=12, bold=True, color=SINK))
    parts.append(text(755, 190, "(вхід зарядника)", size=10.5, color=MUTED))
    # центральний вузол VBUS
    vx = 430
    parts.append(line(vx, 120, vx, 250, color=INK, sw=4))
    parts.append(text(vx + 20, 108, "VBUS", size=14, bold=True, anchor="start"))
    # до партнера (роз'єм)
    parts.append(arrow(vx, 120, vx, 74, color=INK, sw=2))
    parts.append(text(vx, 64, "до партнера (роз'єм)", size=11, color=MUTED))

    # ключ-джерело (ліва половина) — пара back-to-back
    def switch_box(cx, label, color):
        bw, bh = 96, 50
        parts.append(rect(cx - bw / 2, yline - bh / 2, bw, bh, fill="#ffffff", stroke=color, sw=2))
        # два позначки транзисторів спина-до-спини
        parts.append(text(cx, yline - 3, "⊣⊢", size=16, bold=True, color=color))
        parts.append(text(cx, yline + 15, label, size=10.5, color=color, bold=True))
    # дроти
    parts.append(line(180, yline, 262, yline, color=INK, sw=2.5))
    switch_box(310, "ключ-джерело", SRC)
    parts.append(line(358, yline, vx, yline, color=INK, sw=2.5))
    parts.append(line(vx, yline, 550, yline, color=INK, sw=2.5))
    switch_box(598, "ключ-стік", SINK)
    parts.append(line(646, yline, 680, yline, color=INK, sw=2.5))

    # стрілки напряму струму
    parts.append(arrow(200, 140, 400, 140, color=SRC, sw=2.4))
    parts.append(text(300, 128, "струм у режимі ДЖЕРЕЛА", size=11, color=SRC, bold=True))
    parts.append(arrow(460, 210, 660, 210, color=SINK, sw=2.4))
    parts.append(text(560, 228, "струм у режимі СТОКА", size=11, color=SINK, bold=True))

    # підписи «пара back-to-back»
    parts.append(text(310, yline + 42, "пара спина-до-спини", size=10, color=MUTED))
    parts.append(text(598, yline + 42, "пара спина-до-спини", size=10, color=MUTED))

    # інтерлок
    b, w, h = textbox(W / 2, 300,
                      ["ІНТЕРЛОК: ключ-джерело і ключ-стік НІКОЛИ не відкриті разом —",
                       "інакше вхід замкне на вихід (наскрізний струм). Спершу закрий обидва, витримай мертвий час, тоді відкрий один."],
                      size=11.5, fill="#fdf6e3", stroke="#b7791f", bold=False)
    parts.append(b)
    b2, w2, h2 = textbox(W / 2, 356,
                         "Кожен бік — ПАРА транзисторів: у закритому стані їхні body-діоди дивляться назустріч і глушать струм в обидва боки.",
                         size=11, fill="#f4f6f8")
    parts.append(b2)
    render(os.path.join(IMG, "vbus-switch.svg"), W, H, *parts,
           title="Двонапрямний ключ VBUS: два боки на одному вузлі")


# ── 4. Зміна ролі живлення: VBUS у часі, передача через нуль ──────────────────
def fig_role_swap():
    W, H = 820, 380
    parts = []
    x0, xN = 80, 760
    y0 = 270           # рівень 0 В
    y5 = 150           # рівень ~5 В
    ysafe = 250        # vSafe0V (~0.8 В) — трохи над нулем
    # осі
    parts.append(line(x0, y0, xN, y0, color=INK, sw=1.5))
    parts.append(line(x0, y0, x0, 90, color=INK, sw=1.5))
    parts.append(text(x0 - 12, 100, "VBUS", size=11, color=MUTED, anchor="end"))
    parts.append(text(xN - 6, y0 + 22, "час →", size=11, color=MUTED, anchor="end"))
    # лінія vSafe0V
    parts.append(line(x0, ysafe, xN, ysafe, color=MUTED, sw=1, dash="5 4"))
    parts.append(text(xN - 6, ysafe - 6, "vSafe0V (<0.8 В)", size=10.5, color=MUTED, anchor="end"))

    # сегменти профілю
    xa, xb, xc, xd, xe = 240, 330, 430, 520, xN - 20
    # A: старе джерело тримає 5 В
    parts.append(line(x0 + 10, y5, xa, y5, color=SRC, sw=3.2))
    # B: спад (зціджування) від 5 В до vSafe0V
    pts = []
    for i in range(0, 51):
        t = i / 50.0
        xx = xa + (xb - xa) * t
        yy = y5 + (ysafe - y5) * (1 - math.exp(-3.2 * t)) / (1 - math.exp(-3.2))
        pts.append("%.1f,%.1f" % (xx, yy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
                 'stroke-linecap="round"/>' % (" ".join(pts), SRC))
    # C: проміжок — обидва off (біля нуля)
    parts.append(line(xb, ysafe, xc, ysafe, color=INK, sw=2.4))
    # D: підйом нового джерела до 5 В
    pts2 = []
    for i in range(0, 51):
        t = i / 50.0
        xx = xc + (xd - xc) * t
        yy = ysafe + (y5 - ysafe) * t
        pts2.append("%.1f,%.1f" % (xx, yy))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" '
                 'stroke-linecap="round"/>' % (" ".join(pts2), SINK))
    # E: нове джерело тримає 5 В (vSafe5V)
    parts.append(line(xd, y5, xe, y5, color=SINK, sw=3.2))

    # маркер узгодження
    parts.append(line(xa, 128, xa, y0, color=MUTED, sw=1.1, dash="4 3"))
    parts.append(text(xa, 120, "PD: PR_Swap узгоджено", size=10.5, color=MUTED))
    # підписи фаз
    parts.append(text((x0 + xa) / 2, y5 - 12, "старе джерело: 5 В", size=11, color=SRC, bold=True))
    parts.append(text(xb + 8, 200, "старе off,", size=10.5, color=SRC, anchor="start"))
    parts.append(text(xb + 8, 214, "зціджує VBUS", size=10.5, color=SRC, anchor="start"))
    parts.append(text((xb + xc) / 2, ysafe + 20, "обидва off", size=10.5, color=INK))
    parts.append(text(xd - 6, 196, "нове джерело", size=10.5, color=SINK, anchor="end"))
    parts.append(text(xd - 6, 210, "вмикається", size=10.5, color=SINK, anchor="end"))
    parts.append(text((xd + xe) / 2, y5 - 12, "vSafe5V — роль помінялась", size=11, color=SINK, bold=True))

    # підсумок
    b, w, h = textbox(W / 2, 330,
                      ["Передача через нуль: доки старі вольти не зійдуть до vSafe0V,",
                       "нове джерело не вмикають — так два джерела не зіштовхуються на VBUS."],
                      size=11.5, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "role-swap.svg"), W, H, *parts,
           title="Зміна ролі живлення (PR_Swap): VBUS у часі")


# ── 5. Хронологія: від піна ID до PR_Swap (для hist-вставки) ─────────────────
def fig_otg_timeline():
    W, H = 1060, 360
    parts = []
    ax_y = 158
    x0, x1 = 70, 990
    parts.append(arrow(x0, ax_y, x1, ax_y, color=INK, sw=2.5))
    parts.append(text(x1 - 4, ax_y - 12, "час →", size=11, color=MUTED, anchor="end"))

    nodes = [
        (160, "2001", ["OTG-доповнення", "до USB 2.0", "пін ID + HNP/SRP"], MUTED),
        (410, "2012", ["USB PD 1.0", "сигнал FSK", "по шині VBUS"], MUTED),
        (620, "2013", ["анонс USB-C", "Promoter Group:", "Intel, HP, MS, TI"], NEG),
        (840, "2014", ["USB-C 1.0", "Rp/Rd на CC", "PD 2.0: BMC по CC"], SINK),
    ]
    for nx, year, lines, col in nodes:
        parts.append(circle(nx, ax_y, 8, fill="#ffffff", stroke=col, sw=2.5))
        parts.append(text(nx, ax_y - 24, year, size=16, bold=True, color=INK))
        b, w, h = textbox(nx, ax_y + 74, lines, size=11.5, fill=FILL, stroke=col, sw=1.3)
        parts.append(b)

    # підсумкова стрічка внизу
    b, w, h = textbox(W / 2, 322,
                      ["Дуга: кабель вирішує роль (2001) → резистор на CC вирішує роль (2014)",
                       "→ PD міняє саме РОЛЬ ЖИВЛЕННЯ наживо (PR_Swap)."],
                      size=12, fill="#fdf6e3", stroke="#b7791f")
    parts.append(b)
    render(os.path.join(IMG, "otg-typec-timeline.svg"), W, H, *parts,
           title="Тринадцять років: від піна ID до живої зміни ролі")


# ── 6. Кабель вирішує vs резистор вирішує ────────────────────────────────────
def fig_id_vs_cc():
    W, H = 960, 470
    parts = []
    # ліва панель — старий світ (жорсткий), права — новий (гнучкий)
    lpx, rpx, py, pw, ph = 30, 500, 60, 430, 300
    parts.append(rect(lpx, py, pw, ph, fill="#fdf3f2", stroke=SRC, sw=2))
    parts.append(rect(rpx, py, pw, ph, fill="#f2faf4", stroke=SINK, sw=2))
    parts.append(text(lpx + pw / 2, py + 30, "До USB-C: вирішує КАБЕЛЬ", size=15,
                      bold=True, color=SRC))
    parts.append(text(rpx + pw / 2, py + 30, "USB-C: вирішує РЕЗИСТОР", size=15,
                      bold=True, color=SINK))

    def bullets(px, rows):
        y = py + 55
        for lines in rows:
            parts.append(fitbox(px + 16, y, pw - 32, 58, lines, size=12,
                                 fill="#ffffff", stroke=MUTED, sw=1.0))
            y += 70

    bullets(lpx, [
        ["Штекер mini-A заземляє пін ID →", "я A-пристрій: і хост, і джерело VBUS."],
        ["HNP міняє лише РОЛЬ ДАНИХ", "(хост ↔ периферія) — живлення ніколи."],
        ["Напрям живлення приварено до штекера:", "A-пристрій годує весь сеанс."],
    ])
    bullets(rpx, [
        ["Rp (вгору) = «можу бути джерелом»,", "Rd (вниз) = «можу бути стоком»."],
        ["Резистор перемикають ПРОГРАМНО →", "порт DRP чергує Rp ↔ Rd."],
        ["PD додає PR_Swap: РОЛЬ ЖИВЛЕННЯ", "міняється наживо, без перетику кабелю."],
    ])

    # підсумкова стрічка
    b, w, h = textbox(W / 2, 435,
                      "Від «кабель вирішує роль — і назавжди» до «порт вирішує сам і може передумати на ходу».",
                      size=12.5, fill="#f4f6f8")
    parts.append(b)
    render(os.path.join(IMG, "id-pin-vs-cc-resistor.svg"), W, H, *parts,
           title="Хто оголошує роль: приварений пін vs перемикний резистор")


# ── 7. Блок-схема мікросхеми DRP/TCPC: внутрішні блоки й піни ─────────────────
def fig_comp_block():
    W, H = 960, 480
    p = []
    cx0, cy0, cw, ch = 310, 66, 340, 360
    p.append(rect(cx0, cy0, cw, ch, fill="#eef2f7", stroke=INK, sw=2))
    p.append(text(cx0 + cw / 2, cy0 + 26, "Мікросхема DRP / TCPC", size=15, bold=True))
    bx, bw = cx0 + 18, cw - 36
    blocks = [
        "CC-аналог: Rp / Rd / Ra + компаратори",
        "PD-PHY: BMC-кодек · CRC · RX/TX-буфери",
        "VBUS-АЦП + пороги й тривоги",
        "Керування ключами: джерело · стік · розряд",
        "VCONN-ключ (+ струмовий захист)",
        "Реєстри · I²C-ціль · ALERT",
        "LDO · POR · мертва батарея (Rd)",
    ]
    by, bh, gap = cy0 + 44, 40, 6
    for i, s in enumerate(blocks):
        y = by + i * (bh + gap)
        p.append(fitbox(bx, y, bw, bh, s, size=12, fill="#ffffff", stroke=MUTED, sw=1.4))
    # ліворуч — до роз'єму
    lb, _, _ = textbox(150, 150, ["До роз'єму USB-C:", "CC1 · CC2", "VBUS-sense"],
                       size=11.5, fill="#fdf0ee", stroke=POS)
    p.append(lb)
    p.append(line(224, 150, cx0, 150, color=MUTED, sw=1.5))
    # праворуч — до хоста
    rb, _, _ = textbox(818, 150, ["До хоста (I²C):", "SDA · SCL · ALERT", "ADDR · EN · RST_N"],
                       size=11.5, fill="#eef2f7", stroke=NEG)
    p.append(rb)
    p.append(line(cx0 + cw, 150, 712, 150, color=MUTED, sw=1.5))
    # праворуч-низ — живлення
    pb, _, _ = textbox(818, 300, ["Живлення:", "VDD (завжди-увімк.)", "GND"],
                       size=11.5, fill="#f4f6f8", stroke=MUTED)
    p.append(pb)
    p.append(line(cx0 + cw, 300, 726, 300, color=MUTED, sw=1.5))
    # низ — до силових ключів
    bb, _, _ = textbox(480, 456, "До силових ключів: GATE_SRC · GATE_SNK · DISCH · VCONN",
                       size=11.5, fill="#eafaf0", stroke=FIELD)
    p.append(bb)
    p.append(line(480, cy0 + ch, 480, 438, color=MUTED, sw=1.5))
    render(os.path.join(IMG, "comp-block-diagram.svg"), W, H, *p,
           title="Що всередині: блоки й піни DRP/TCPC-контролера")


# ── 8. Типова обв'язка: що висить на пінах ───────────────────────────────────
def fig_comp_app():
    W, H = 960, 440
    p = []
    # роз'єм
    p.append(rect(40, 150, 96, 150, fill="#eef2f7", stroke=INK, sw=1.8))
    p.append(text(88, 214, "роз'єм", size=12, bold=True))
    p.append(text(88, 234, "USB-C", size=12, bold=True))
    # чип
    chx, chy, chw, chh = 360, 150, 180, 150
    p.append(rect(chx, chy, chw, chh, fill="#eef2f7", stroke=INK, sw=2))
    p.append(text(chx + chw / 2, chy + chh / 2, "DRP / TCPC", size=14, bold=True))
    # CC1/CC2
    p.append(line(136, 190, chx, 190, color=INK, sw=2))
    p.append(text(250, 181, "CC1", size=11, color=MUTED))
    p.append(line(136, 224, chx, 224, color=INK, sw=2))
    p.append(text(250, 215, "CC2", size=11, color=MUTED))
    # ключі VBUS зверху
    p.append(rect(600, 56, 176, 76, fill="#fdf0ee", stroke=POS, sw=1.8))
    p.append(text(688, 84, "ключі VBUS", size=12.5, bold=True, color=POS))
    p.append(text(688, 106, "пари back-to-back", size=10.5, color=MUTED))
    # VBUS від роз'єму нагору до ключів (обхід повз підписи CC1/CC2 на x=250)
    p.append(line(136, 286, 288, 286, color=INK, sw=2.4))
    p.append(line(288, 286, 288, 94, color=INK, sw=2.4))
    p.append(line(288, 94, 600, 94, color=INK, sw=2.4))
    p.append(text(390, 85, "VBUS", size=11, color=MUTED))
    # гейти від чипа
    p.append(arrow(chx + chw, 172, 640, 132, color=FIELD, sw=1.8))
    p.append(text(596, 116, "гейт-виводи", size=10.5, color=FIELD))
    # вихід ключів у шину/систему
    p.append(rect(820, 56, 116, 76, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(878, 86, "внутр. шина", size=10.5, bold=True, color=FIELD))
    p.append(text(878, 106, "↔ система", size=10.5, color=MUTED))
    p.append(arrow(776, 94, 820, 94, color=INK, sw=2))
    # хост
    p.append(rect(600, 208, 176, 92, fill="#eef2f7", stroke=NEG, sw=1.8))
    p.append(text(688, 240, "хост (MCU)", size=12.5, bold=True, color=NEG))
    p.append(text(688, 262, "TCPM у ПЗ", size=10.5, color=MUTED))
    p.append(arrow(chx + chw, 238, 600, 238, color=NEG, sw=1.8))
    p.append(text(556, 229, "SDA·SCL", size=10, color=NEG))
    p.append(arrow(600, 278, chx + chw, 278, color=NEG, sw=1.6))
    p.append(text(560, 295, "ALERT", size=10, color=NEG))
    p.append(text(556, 200, "↑ підтяжки до VIO", size=10, color=MUTED))
    # живлення
    p.append(arrow(300, 372, chx + 40, chy + chh, color=MUTED, sw=1.8))
    b, _, _ = textbox(196, 380, ["VDD — від завжди-увімкненої шини",
                                 "(щоб Rd жив і при мертвій батареї)"], size=10.5, fill="#f4f6f8")
    p.append(b)
    render(os.path.join(IMG, "comp-app-circuit.svg"), W, H, *p,
           title="Типова обв'язка DRP/TCPC-контролера")


# ── 9. Межа TCPCI: TCPM (хост) ↔ реєстри ↔ TCPC (чип) ─────────────────────────
def fig_comp_tcpci():
    W, H = 900, 430
    p = []
    # TCPM
    p.append(rect(56, 88, 300, 214, fill="#eef2f7", stroke=NEG, sw=2))
    p.append(text(206, 114, "TCPM — керівник порту", size=14, bold=True, color=NEG))
    p.append(text(206, 134, "(у хості, програмно)", size=11, color=MUTED))
    for i, s in enumerate(["політика живлення", "машина станів Type-C / PD",
                           "движок політики (ПЗ хоста)"]):
        p.append(text(206, 168 + i * 26, "• " + s, size=11.5, color=INK))
    # TCPC
    p.append(rect(544, 88, 300, 214, fill="#eef2f7", stroke=POS, sw=2))
    p.append(text(694, 114, "TCPC — контролер порту", size=14, bold=True, color=POS))
    p.append(text(694, 134, "(мікросхема)", size=11, color=MUTED))
    for i, s in enumerate(["CC-аналог + PD-PHY", "ключі VBUS / VCONN",
                           "реєстри + ALERT"]):
        p.append(text(694, 168 + i * 26, "• " + s, size=11.5, color=INK))
    # межа
    p.append(line(450, 68, 450, 322, color=INK, sw=1.4, dash="6 5"))
    p.append(text(450, 58, "TCPCI: реєстри по I²C + ALERT", size=12, bold=True))
    # стрілки в проміжку
    p.append(arrow(356, 162, 544, 162, color=NEG, sw=2))
    p.append(text(450, 152, "пише →", size=10.5, color=NEG, bold=True))
    p.append(arrow(544, 208, 356, 208, color=POS, sw=2))
    p.append(text(450, 198, "читає ←", size=10.5, color=POS, bold=True))
    p.append(arrow(544, 254, 356, 254, color=INK, sw=2))
    p.append(text(450, 244, "ALERT ←", size=10.5, color=INK, bold=True))
    # легенда
    leg, _, _ = textbox(450, 366, [
        "пише: ROLE_CONTROL · COMMAND · POWER_CONTROL · TRANSMIT",
        "читає: CC_STATUS · POWER_STATUS · FAULT_STATUS · VBUS_VOLTAGE · RX",
        "ALERT: сталася подія — прокинься й прочитай, що змінилось",
    ], size=11, fill="#f4f6f8")
    p.append(leg)
    render(os.path.join(IMG, "comp-tcpci-split.svg"), W, H, *p,
           title="Межа TCPCI: де кінчається чип і починається хост")


# ═══ Фігури до вставки «Машина станів DRP і зміни ролі» ═══════════════════════
SM_GRN = "#eaf3ea"    # світло-зелене тло станів-стоків
SM_RED = "#fdecea"    # світло-червоне тло станів-джерел


def _sm_node(cx, cy, w, h, lines, fill, stroke, sw=2.0, tsize=13):
    """Прямокутний вузол-стан із центрованим (багаторядковим) підписом."""
    if isinstance(lines, str):
        lines = [lines]
    out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=sw, rx=9)
    ty = cy - (len(lines) - 1) * tsize * 1.25 / 2 + tsize * 0.35
    out += mtext(cx, ty, lines, size=tsize, color=INK, bold=True, lh=1.25)
    return out


def _sm_bpt(cx, cy, w, h, dx, dy, gap=6):
    """Точка на межі рамки в напрямі (dx,dy) — щоб стрілка торкалась краю, не центру."""
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2 + gap) / abs(dx) if dx else 1e9
    sy = (h / 2 + gap) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def _sm_edge(a, b, color=INK, sw=2.0):
    """Стрілка від межі вузла a до межі вузла b."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    dx, dy = bx - ax, by - ay
    x1, y1 = _sm_bpt(ax, ay, aw, ah, dx, dy)
    x2, y2 = _sm_bpt(bx, by, bw, bh, -dx, -dy)
    return arrow(x1, y1, x2, y2, color=color, sw=sw)


# ── 10. Граф станів під'єднання (з детуром Try.SRC) ──────────────────────────
def fig_state_graph():
    W, H = 1040, 720
    p = []
    # вузли: (cx, cy, w, h)
    U   = (140, 360, 196, 92)
    AWK = (410, 150, 182, 58)
    ASK = (896, 150, 182, 70)
    TWK = (656, 250, 174, 56)
    TSR = (656, 374, 162, 56)
    AWS = (410, 586, 182, 58)
    ASS = (896, 586, 182, 70)

    # ребра першими, щоб вузли лягли поверх кінців стрілок
    p.append(_sm_edge(U, AWK))
    p.append(_sm_edge(U, AWS))
    p.append(_sm_edge(AWK, ASK))
    p.append(_sm_edge(AWS, ASS))
    p.append(_sm_edge(AWK, TSR, color=POS))
    p.append(_sm_edge(TSR, ASS, color=POS))
    p.append(_sm_edge(TSR, TWK, color=POS))
    p.append(_sm_edge(TWK, ASK))
    # PR_Swap — двобічний пунктир між двома Attached
    p.append(line(896, 188, 896, 548, color=MUTED, sw=1.8, dash="6 5"))
    p.append(arrow(896, 202, 896, 188, color=MUTED, sw=1.8))
    p.append(arrow(896, 534, 896, 548, color=MUTED, sw=1.8))

    # написи на ребрах (короткі; повний сенс — у прозі)
    p.append(mtext(292, 250, ["бачу", "джерело"], size=11, color=MUTED, lh=1.15))
    p.append(mtext(292, 468, ["бачу", "стік"], size=11, color=MUTED, lh=1.15))
    p.append(text(653, 137, "tCCDebounce", size=11, color=MUTED))
    p.append(text(653, 607, "tCCDebounce", size=11, color=MUTED))
    p.append(text(486, 243, "Try.SRC", size=11, color=POS, bold=True))
    p.append(mtext(812, 452, ["партнер Rd", "→ виграв"], size=10.5, color=POS, anchor="start", lh=1.15))
    p.append(text(674, 318, "tDRPTry", size=10.5, color=POS, anchor="start"))
    p.append(text(742, 191, "VBUS", size=11, color=MUTED))
    p.append(text(915, 372, "PR_Swap", size=11, color=MUTED, anchor="start"))

    # вузли
    p.append(_sm_node(*U, ["Unattached", "гойдалка Rp↔Rd", "tDRP 50–100 мс"], FILL, INK))
    p.append(_sm_node(*AWK, ["AttachWait.SNK"], SM_GRN, FIELD))
    p.append(_sm_node(*ASK, ["Attached.SNK", "СТІК"], SM_GRN, FIELD))
    p.append(_sm_node(*AWS, ["AttachWait.SRC"], SM_RED, POS))
    p.append(_sm_node(*ASS, ["Attached.SRC", "ДЖЕРЕЛО"], SM_RED, POS))
    p.append(_sm_node(*TWK, ["TryWait.SNK"], SM_GRN, FIELD))
    p.append(_sm_node(*TSR, ["Try.SRC"], SM_RED, POS, sw=2.8))

    # легенда й примітка про від'єднання
    lb, _, _ = textbox(184, 108, ["зелене — стік", "червоне — джерело"],
                       size=10.5, fill="#f4f6f8", color=MUTED)
    p.append(lb)
    db, _, _ = textbox(430, 686,
                       "Від будь-якого Attached.* від'єднання (CC=Open ≥ tPDDebounce або зникнення VBUS) → назад в Unattached.",
                       size=11, fill="#f4f6f8")
    p.append(db)

    render(os.path.join(IMG, "state-graph.svg"), W, H, *p,
           title="Граф станів під'єднання Type-C: розв'язання ролі й детур Try.SRC")


# ── 11. Драбина повідомлень PR_Swap (передача через нуль) ────────────────────
def fig_prswap_ladder():
    W, H = 980, 580
    p = []
    Lx, Rx = 250, 650
    mid = (Lx + Rx) / 2
    top, bot = 92, 515

    p.append(_sm_node(Lx, 66, 224, 50, ["Старе ДЖЕРЕЛО", "(стане стоком)"], SM_RED, POS, tsize=12.5))
    p.append(_sm_node(Rx, 66, 224, 50, ["Старий СТІК", "(стане джерелом)"], SM_GRN, FIELD, tsize=12.5))
    # пунктирні часові осі — з розривами повз рамки вузлів, що лежать на цій же вертикалі
    p.append(line(Lx, top, Lx, 223, color=MUTED, sw=1.3, dash="4 5"))
    p.append(line(Lx, 300, Lx, bot, color=MUTED, sw=1.3, dash="4 5"))
    p.append(line(Rx, top, Rx, 365, color=MUTED, sw=1.3, dash="4 5"))
    p.append(line(Rx, 442, Rx, bot, color=MUTED, sw=1.3, dash="4 5"))
    p.append(text(mid, 112, "VBUS = 5 В (від старого джерела)", size=10.5, color=MUTED))

    def msg(y, l2r, label, color=INK):
        a, b = (Lx + 5, Rx - 5) if l2r else (Rx - 5, Lx + 5)
        p.append(arrow(a, y, b, y, color=color, sw=2.2))
        p.append(text(mid, y - 10, label, size=12, color=color, bold=True))

    msg(135, True,  "PR_Swap  «міняймось»", NEG)
    msg(185, False, "Accept  (+ GoodCRC)", FIELD)

    p.append(_sm_node(Lx, 250, 214, 54, ["VBUS off · зціджую", "→ vSafe0V"], SM_RED, POS, tsize=12))
    p.append(text(Lx, 292, "за ≤ tSrcTransition (25–35 мс)", size=10.5, color=MUTED))

    msg(325, True, "PS_RDY  «я вимкнувся»", POS)

    p.append(_sm_node(Rx, 392, 214, 54, ["піднімаю VBUS", "→ vSafe5V"], SM_GRN, FIELD, tsize=12))
    p.append(text(Rx, 434, "пауза ≥ tSwapSourceStart", size=10.5, color=MUTED))

    msg(462, False, "PS_RDY  «я джерело»", FIELD)

    # брекет PSSourceOffTimer: правий чекає PS_RDY від старого джерела
    bx = 772
    p.append(line(bx, 185, bx, 325, color=INK, sw=1.4))
    p.append(line(bx - 6, 185, bx + 6, 185, color=INK, sw=1.4))
    p.append(line(bx - 6, 325, bx + 6, 325, color=INK, sw=1.4))
    p.append(mtext(bx + 12, 232, ["PSSourceOffTimer", "750–920 мс", "таймаут →", "ErrorRecovery"],
                   size=10.5, color=INK, anchor="start", lh=1.3))

    rb, _, _ = textbox(mid, 500, "Ролі помінялись — кабель не чіпали.",
                       size=12, fill="#eef7ee", stroke=FIELD, bold=True)
    p.append(rb)

    render(os.path.join(IMG, "prswap-ladder.svg"), W, H, *p,
           title="PR_Swap: драбина повідомлень і передача VBUS через нуль")


if __name__ == "__main__":
    fig_two_directions()
    fig_drp_toggle()
    fig_vbus_switch()
    fig_role_swap()
    fig_otg_timeline()
    fig_id_vs_cc()
    fig_comp_block()
    fig_comp_app()
    fig_comp_tcpci()
    fig_state_graph()
    fig_prswap_ladder()
    print("done")
