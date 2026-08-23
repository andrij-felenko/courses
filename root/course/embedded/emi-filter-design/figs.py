# -*- coding: utf-8 -*-
"""Фігури до теми «Вхідний EMI-фільтр перетворювача»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def comp_box(cx, cy, label, w=86, h=40, fill=FILL, stroke=LINE):
    return fitbox(cx - w / 2, cy - h / 2, w, h, label, size=13, fill=fill, stroke=stroke)


# ── 1. Звідки шум: пульсівний вхідний струм перетворювача ───────────────────
def fig_where_noise():
    W, H = 760, 320
    f = []
    # джерело
    bat = comp_box(80, 150, "джерело\n(батарея)", w=96, h=56)
    f.append(bat)
    # провід від джерела
    f.append(line(128, 150, 250, 150, sw=2))
    f.append(line(128, 200, 600, 200, sw=2))  # зворотний
    # межа фільтра (стіна)
    f.append(line(250, 70, 250, 250, color=FIELD, sw=2.5, dash="7 5"))
    f.append(text(250, 60, "тут стоїть фільтр", size=13, color=FIELD, bold=True))
    # перетворювач (ключ)
    sw = comp_box(440, 150, "імпульсний\nперетворювач\n(ключ)", w=150, h=80, fill="#fff4e6", stroke=POS)
    f.append(sw)
    f.append(line(250, 150, 365, 150, sw=2))
    f.append(line(515, 150, 600, 150, sw=2))
    # навантаження
    f.append(comp_box(660, 150, "наван-\nтаження", w=86, h=56))
    f.append(line(600, 150, 617, 150, sw=2))
    f.append(line(600, 200, 617, 200, sw=2))
    f.append(line(703, 150, 703, 200, sw=2))
    # пульсівний струм усередині перетворювача — рвана лінія над ключем
    bx, by = 388, 96
    pulse = "M%d %d" % (bx, by)
    x = bx
    for i in range(5):
        pulse += " L%d %d L%d %d L%d %d L%d %d" % (x, by - 12, x + 7, by - 12, x + 7, by, x + 15, by)
        x += 15
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pulse, POS))
    f.append(text(530, 92, "струм рветься на шматки", size=11, color=POS, anchor="start"))
    # хвилі завад біжать назад до джерела (нижнім «брудним» проводом)
    for i, xx in enumerate([348, 323, 298]):
        op = 0.9 - i * 0.25
        f.append('<path d="M%d 200 q -10 -14 -20 0 q -10 14 -20 0" fill="none" stroke="%s" stroke-width="2" opacity="%.2f"/>' % (xx, POS, op))
    f.append(arrow(296, 220, 262, 220, color=POS, sw=2))
    f.append(text(360, 240, "завади біжать назад у живлення", size=12, color=POS))
    # підпис боків
    f.append(text(165, 110, "чистий бік", size=12, color=MUTED))
    f.append(text(575, 110, "брудний бік", size=12, color=MUTED))
    render(os.path.join(IMG, "where-noise.svg"), W, H, *f,
           title="Перетворювач ріже струм — і завади тікають назад у живлення")


# ── 2. Диференційний і синфазний шум: два різні шляхи ───────────────────────
def fig_dm_cm():
    W, H = 760, 360
    f = []
    f.append(text(190, 40, "Диференційний (DM)", size=15, bold=True, color=NEG))
    f.append(text(575, 40, "Синфазний (CM)", size=15, bold=True, color=POS))
    f.append(line(380, 60, 380, 330, color=MUTED, sw=1, dash="4 4"))

    # ── DM: струм туди-назад між двома проводами ──
    f.append(line(70, 100, 320, 100, sw=2))   # верхній провід
    f.append(line(70, 200, 320, 200, sw=2))   # нижній провід
    f.append(comp_box(70, 150, "дже-\nрело", w=60, h=120))
    f.append(comp_box(320, 150, "пере-\nтво-\nрювач", w=64, h=120, fill="#fff4e6", stroke=POS))
    # стрілки: туди верхнім, назад нижнім
    f.append(arrow(140, 100, 250, 100, color=NEG, sw=2.4))
    f.append(arrow(250, 200, 140, 200, color=NEG, sw=2.4))
    f.append(text(195, 88, "туди", size=12, color=NEG))
    f.append(text(195, 222, "назад", size=12, color=NEG))
    f.append(mtext(195, 296, "однаковий струм у\nпротилежні боки —\nзамкнена петля", size=12, color=INK))

    # ── CM: струм в обох проводах в один бік, повертається землею ──
    f.append(line(450, 100, 700, 100, sw=2))
    f.append(line(450, 200, 700, 200, sw=2))
    f.append(comp_box(450, 150, "дже-\nрело", w=60, h=120))
    f.append(comp_box(700, 150, "пере-\nтво-\nрювач", w=64, h=120, fill="#fff4e6", stroke=POS))
    f.append(arrow(520, 100, 630, 100, color=POS, sw=2.4))
    f.append(arrow(520, 200, 630, 200, color=POS, sw=2.4))
    # земля
    f.append(line(450, 274, 700, 274, color=FIELD, sw=2))
    f.append(text(470, 266, "земля / корпус", size=11, color=FIELD, anchor="start"))
    # повернення землею
    f.append(line(630, 100, 630, 132, color=POS, sw=2, dash="3 3"))
    f.append(arrow(630, 132, 575, 266, color=POS, sw=2))
    f.append(mtext(540, 150, "повертається\nпаразитною\nємністю крізь\nземлю", size=11, color=POS, anchor="end"))
    f.append(text(575, 320, "обидва проводи — в один бік", size=12, color=INK))
    render(os.path.join(IMG, "dm-cm.svg"), W, H, *f,
           title="Дві природи завад: між проводами і відносно землі")


# ── 3. LC-бар'єр і пастка резонансу ─────────────────────────────────────────
def fig_lc_resonance():
    W, H = 720, 360
    f = []
    ox = 95
    top, bot = 70, 290        # межі поля по Y
    ax_w = 560
    zero = 130                # рівень 0 дБ (вище — послаблення, нижче — підсилення)
    f.append(line(ox, bot, ox + ax_w, bot, sw=1.6))          # вісь X
    f.append(line(ox, top, ox, bot, sw=1.6))                 # вісь Y
    f.append(text(ox + ax_w, bot + 22, "частота (лог)", size=12, anchor="end"))
    # лінія 0 дБ
    f.append(line(ox, zero, ox + ax_w, zero, color=MUTED, sw=1, dash="3 4"))
    f.append(text(ox - 8, zero - 4, "0 дБ", size=11, color=MUTED, anchor="end"))
    f.append(mtext(ox - 8, zero - 48, "↑\nпосла-\nблення", size=11, color=MUTED, anchor="end"))
    f.append(mtext(ox - 8, zero + 22, "↓\nпідсил.", size=11, color=MUTED, anchor="end"))

    pk_x = ox + 165           # положення резонансу f0
    # ідеальний нахил −40 дБ/декаду (LC), пунктир
    f.append(line(pk_x, zero, ox + ax_w, top + 4, color=MUTED, sw=1.6, dash="6 5"))
    f.append(text(ox + 430, top + 70, "ідеал: −40 дБ/декаду", size=12, color=MUTED))
    # реальна (недемпфована) крива: рівна біля 0, гострий пік ВНИЗ на f0, далі вгору-послаблення
    path = "M%d %d L%d %d Q%d %d %d %d Q%d %d %d %d L%d %d" % (
        ox + 8, zero - 4,
        pk_x - 45, zero - 2,
        pk_x - 8, zero, pk_x, bot - 8,        # пік униз = підсилення
        pk_x + 10, zero - 10, pk_x + 60, top + 80,
        ox + ax_w, top + 6)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, POS))
    # демпфована крива (приборкана), зелена — пік ледь нижче 0
    pathd = "M%d %d Q%d %d %d %d Q%d %d %d %d L%d %d" % (
        ox + 8, zero - 4,
        pk_x - 20, zero - 2, pk_x, zero + 18,
        pk_x + 40, zero - 30, pk_x + 90, top + 90,
        ox + ax_w, top + 8)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pathd, FIELD))
    # позначка f0
    f.append(line(pk_x, zero, pk_x, bot, color=POS, sw=0.8, dash="2 3"))
    f.append(text(pk_x, bot + 18, "f₀ (резонанс LC)", size=12, color=POS, bold=True))
    # підписи кривих
    f.append(text(pk_x + 30, bot - 14, "без демпфування:", size=11, color=POS, anchor="start"))
    f.append(text(pk_x + 30, bot, "фільтр ПІДСИЛЮЄ заваду", size=11, color=POS, anchor="start"))
    f.append(text(ox + 350, zero + 40, "з демпфуванням — пік приборкано", size=12, color=FIELD))
    render(os.path.join(IMG, "lc-resonance.svg"), W, H, *f,
           title="LC-фільтр глушить високі частоти — але на резонансі сам підсилює")


# ── 4. Повна схема вхідного фільтра ─────────────────────────────────────────
def fig_full_filter():
    W, H = 780, 320
    f = []
    yt, yb = 110, 210         # верхній / нижній провід
    xL, xR = 60, 720
    f.append(line(xL, yt, xR, yt, sw=2))
    f.append(line(xL, yb, xR, yb, sw=2))
    f.append(comp_box(60, 160, "вхід\n(+/−)", w=58, h=110))
    f.append(comp_box(720, 160, "до пере-\nтворю-\nвача", w=70, h=110, fill="#fff4e6", stroke=POS))

    # 1) запобіжник
    f.append(comp_box(150, yt, "F", w=34, h=22))
    # 2) синфазний дросель (дві обмотки на спільному осерді)
    cmx = 270
    f.append('<rect x="%d" y="%d" width="60" height="120" rx="6" fill="#eafaf1" stroke="%s" stroke-width="1.6"/>' % (cmx - 30, 95, FIELD))
    # дві котушки-завитки
    for yy in (yt, yb):
        f.append('<path d="M%d %d q 8 -14 16 0 q 8 -14 16 0 q 8 -14 16 0" fill="none" stroke="%s" stroke-width="2"/>' % (cmx - 24, yy, INK))
    # осердя — дві риски між обмотками
    f.append(line(cmx - 4, 100, cmx - 4, 220, color=FIELD, sw=1.4))
    f.append(line(cmx + 4, 100, cmx + 4, 220, color=FIELD, sw=1.4))
    f.append(mtext(cmx, 240, "синфазний\nдросель (CM)", size=11, color=FIELD))

    # 3) X-конденсатор (між проводами)
    xc = 430
    f.append(line(xc, yt, xc, yb, color=NEG, sw=1.8))
    f.append('<rect x="%d" y="%d" width="22" height="8" fill="%s"/>' % (xc - 11, 152, NEG))
    f.append('<rect x="%d" y="%d" width="22" height="8" fill="%s"/>' % (xc - 11, 164, NEG))
    f.append(mtext(xc, 250, "X-конд.\n(DM)", size=11, color=NEG))

    # 4) Y-конденсатори до землі (по одному від кожного проводу)
    gy = 280
    f.append(line(xL, gy, xR, gy, color=FIELD, sw=1.8))
    f.append(text(xR - 4, gy + 16, "земля / корпус", size=11, color=FIELD, anchor="end"))
    yA, yB = 560, 630
    f.append(line(yA, yt, yA, gy, color=POS, sw=1.6))
    f.append('<rect x="%d" y="%d" width="8" height="20" fill="%s"/>' % (yA - 4, 175, POS))
    f.append(line(yB, yb, yB, gy, color=POS, sw=1.6))
    f.append('<rect x="%d" y="%d" width="8" height="20" fill="%s"/>' % (yB - 4, 232, POS))
    f.append(mtext(595, 256, "Y-конд.\n(CM)", size=11, color=POS))

    # порядок-стрілка
    f.append(arrow(xL + 4, 75, xR - 60, 75, color=MUTED, sw=1.4))
    f.append(text((xL + xR) / 2, 66, "напрям потужності →", size=11, color=MUTED))
    render(os.path.join(IMG, "full-filter.svg"), W, H, *f,
           title="Повний вхідний фільтр: запобіжник · CM-дросель · X-конд. · Y-конд.")


# ── 5. Класи X і Y на мережевому вході (для вставки про запобіжні конденсатори) ─
def fig_xy_placement():
    W, H = 760, 360
    f = []
    yL, yN = 110, 175          # фаза / нуль
    xIN, xOUT = 70, 700
    # дві лінії живлення
    f.append(line(xIN, yL, xOUT, yL, sw=2))
    f.append(line(xIN, yN, xOUT, yN, sw=2))
    # підписи проводів
    f.append(text(xIN - 4, yL - 8, "фаза (L)", size=12, color=POS, anchor="start"))
    f.append(text(xIN - 4, yN + 18, "нуль (N)", size=12, color=NEG, anchor="start"))
    # вхід від мережі
    f.append(text(xIN - 2, 70, "від мережі ~", size=12, color=MUTED, anchor="start"))
    # споживач праворуч
    f.append(comp_box(700, 142, "до пере-\nтворю-\nвача", w=70, h=110, fill="#fff4e6", stroke=POS))

    # запобіжник першим
    f.append(comp_box(150, yL, "F", w=34, h=22))
    f.append(text(150, yL - 22, "запобіжник", size=10, color=MUTED))

    # ── X-конденсатор: упоперек між фазою і нулем ──
    xc = 300
    f.append(line(xc, yL, xc, yN, color=POS, sw=1.8))
    f.append('<rect x="%d" y="%d" width="24" height="8" fill="%s"/>' % (xc - 12, 134, POS))
    f.append('<rect x="%d" y="%d" width="24" height="8" fill="%s"/>' % (xc - 12, 146, POS))
    f.append(text(xc + 18, 128, "X", size=15, color=POS, bold=True, anchor="start"))
    f.append(mtext(xc, 250, "X-конденсатор\n(лінія-лінія)\nпробій → коротке,\nрве запобіжник", size=11, color=POS))

    # розрядний резистор паралельно X (ліворуч від нього)
    rx = 235
    f.append(line(rx, yL, rx, yN, color=POS, sw=1.4))
    f.append('<rect x="%d" y="%d" width="10" height="34" fill="none" stroke="%s" stroke-width="1.4"/>' % (rx - 5, 125, POS))
    f.append(text(rx - 8, 120, "R розр.", size=10, color=POS, anchor="end"))

    # ── Y-конденсатори: від кожного проводу на захисну землю ──
    gy = 300
    f.append(line(xIN, gy, xOUT, gy, color=FIELD, sw=2))
    f.append(text(xOUT - 4, gy + 18, "захисна земля / корпус (PE)", size=11, color=FIELD, anchor="end"))
    # символ заземлення
    f.append(line(120, gy, 120, gy + 10, color=FIELD, sw=1.6))
    f.append(line(108, gy + 10, 132, gy + 10, color=FIELD, sw=2))
    f.append(line(112, gy + 15, 128, gy + 15, color=FIELD, sw=2))
    f.append(line(116, gy + 20, 124, gy + 20, color=FIELD, sw=2))
    yA, yB = 470, 560
    f.append(line(yA, yL, yA, gy, color=FIELD, sw=1.6))
    f.append('<rect x="%d" y="%d" width="20" height="7" fill="%s"/>' % (yA - 10, 230, FIELD))
    f.append('<rect x="%d" y="%d" width="20" height="7" fill="%s"/>' % (yA - 10, 240, FIELD))
    f.append(line(yB, yN, yB, gy, color=FIELD, sw=1.6))
    f.append('<rect x="%d" y="%d" width="20" height="7" fill="%s"/>' % (yB - 10, 230, FIELD))
    f.append('<rect x="%d" y="%d" width="20" height="7" fill="%s"/>' % (yB - 10, 240, FIELD))
    f.append(text(yB + 16, 200, "Y", size=15, color=FIELD, bold=True, anchor="start"))
    f.append(mtext(515, 332, "Y-конденсатори (лінія-земля) — лише відмова в обрив", size=11, color=FIELD))

    render(os.path.join(IMG, "xy-placement.svg"), W, H, *f,
           title="Класи X і Y на мережевому вході: позиція диктує режим відмови")


if __name__ == "__main__":
    fig_where_noise()
    fig_dm_cm()
    fig_lc_resonance()
    fig_full_filter()
    fig_xy_placement()
    print("OK figures written to", IMG)
