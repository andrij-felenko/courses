# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

WARM_FILL = "#fff6e5"
WARM = "#b8860b"
BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
GREY_FILL = "#eceff1"


# ── 1. Таблиця злиття: три шари й що з них виходить ─────────────────────────
def fig_merge_table():
    W, H = 1200, 560
    p = []

    col = {"upper": 300, "middle": 460, "lower": 620, "merged": 800}
    notes_x = 900
    head_y = 78
    rows_y = [140, 210, 280, 350, 420]

    p.append(text(60, head_y, "ім'я", size=13, bold=True, anchor="start", color=MUTED))
    p.append(text(col["upper"], head_y, "верхній", size=13, bold=True))
    p.append(text(col["middle"], head_y, "середній", size=13, bold=True))
    p.append(text(col["lower"], head_y, "нижній", size=13, bold=True))
    p.append(text(col["merged"], head_y, "зведений вигляд", size=13, bold=True))
    p.append(text(notes_x, head_y, "чому саме так", size=13, bold=True,
                  anchor="start", color=MUTED))

    p.append(line(703, 52, 703, 452, color=MUTED, sw=1.2, dash="5 4"))

    def cell(cx, cy, lines, fill):
        if lines is None:
            return text(cx, cy + 5, "—", size=15, color=MUTED)
        frag, _, _ = textbox(cx, cy, lines, size=12, pad=9, fill=fill,
                             stroke=MUTED, sw=1.2)
        return frag

    rows = [
        ("a.txt", None, None, ["a.txt"],
         ["a.txt", "з нижнього"], "є лише внизу — видно як є"),
        ("b.txt", None, ["b.txt"], ["b.txt"],
         ["b.txt", "із середнього"], "верхній із наявних перемагає"),
        ("c.txt", ["білило"], None, ["c.txt"],
         None, "білило у верхньому ховає нижній"),
        ("d/", ["d/", "непрозорий"], ["d/"], ["d/"],
         ["d/", "лише верхній вміст"], "непрозорий каталог обриває злиття"),
        ("e.txt", ["e.txt"], None, None,
         ["e.txt", "з верхнього"], "створене вже після монтування"),
    ]

    for (name, up, mid, low, merged, note), y in zip(rows, rows_y):
        p.append(text(60, y + 5, name, size=13, anchor="start"))
        up_fill = RED_FILL if (up and up[0] == "білило") else WARM_FILL
        p.append(cell(col["upper"], y, up, up_fill))
        p.append(cell(col["middle"], y, mid, BLUE_FILL))
        p.append(cell(col["lower"], y, low, GREY_FILL))
        p.append(cell(col["merged"], y, merged,
                      GREEN_FILL if merged else RED_FILL))
        p.append(text(notes_x, y + 5, note, size=12, anchor="start", color=MUTED))

    p.append(text(W / 2, 500,
                  "пошук імені йде зверху вниз і спиняється на першому влучанні "
                  "або на білилі",
                  size=13, color=INK))

    render(os.path.join(IMG, 'merge-table.svg'), W, H, *p,
           title="Три шари й зведений вигляд одного каталогу")


# ── 2. Копіювання вгору через робочий каталог ───────────────────────────────
def fig_copy_up():
    W, H = 1140, 520
    p = []

    p.append(rect(430, 80, 690, 320, fill="#fbfbfd", stroke=WARM, sw=1.4,
                  rx=12))
    p.append(text(775, 372,
                  "workdir і upperdir — на одній файловій системі",
                  size=12, color=WARM))

    def panel(x, title, lines, fill):
        out = [rect(x, 110, 250, 190, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10)]
        out.append(text(x + 125, 138, title, size=13, bold=True))
        frag, _, _ = textbox(x + 125, 215, lines, size=12, pad=10,
                             fill=fill, stroke=MUTED, sw=1.2)
        out.append(frag)
        return out

    p += panel(40, "нижній шар (lowerdir)",
               ["big.log", "4 ГіБ, лише читання"], GREY_FILL)
    p += panel(460, "робочий каталог (workdir)",
               ["#3f1a2c", "тимчасове ім'я"], BLUE_FILL)
    p += panel(850, "верхній шар (upperdir)",
               ["big.log", "копія, змінна"], WARM_FILL)

    p.append(arrow(300, 215, 448, 215))
    p.append(mtext(375, 166, ["1. створити й скопіювати",
                              "вміст, права, час, xattr"], size=11, color=MUTED))

    p.append(arrow(720, 215, 838, 215))
    p.append(mtext(780, 166, ["2. rename()", "у верхній шар"],
                   size=11, color=MUTED))

    p.append(text(W / 2, 440,
                  "3. далі кожне звертання за іменем знаходить верхню копію; "
                  "нижній файл лишається недоторканим",
                  size=13))
    p.append(text(W / 2, 472,
                  "напівскопійований файл ніколи не видно під кінцевим іменем",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'copy-up.svg'), W, H, *p,
           title="Що робить ядро при першому записі у файл нижнього шару")


# ── 3. Дескриптор і відображення прив'язані до справжнього файлу ────────────
def fig_stale_fd():
    W, H = 1120, 530
    p = []

    def box(cx, cy, lines, fill, stroke=MUTED):
        frag, _, _ = textbox(cx, cy, lines, size=12, pad=10, fill=fill,
                             stroke=stroke, sw=1.3)
        return frag

    p.append(box(170, 280, ["процес А", "fd, відкритий до копіювання"], BLUE_FILL))
    p.append(box(560, 160, ["нижній inode", "оригінал у шарі lower"], GREY_FILL))
    p.append(box(560, 400, ["верхній inode", "копія в шарі upper"], WARM_FILL))
    p.append(box(940, 280, ["спільне відображення", "MAP_SHARED того ж файлу"],
                 GREEN_FILL))

    p.append(arrow(280, 262, 452, 178))
    p.append(text(366, 148, "1. спершу читання — звідси", size=11, color=MUTED))

    p.append(arrow(280, 298, 452, 382))
    p.append(text(366, 452,
                  "2. після копіювання ядро перечіпляє читання на верхню копію",
                  size=11, color=MUTED))

    p.append(arrow(870, 262, 674, 180, color=POS))
    p.append(text(770, 322, "сторінки лишаються з нижнього файлу",
                  size=11, color=POS))

    p.append(text(W / 2, 496,
                  "дескриптор і відображення прив'язані до справжнього файлу, "
                  "а не до імені",
                  size=13))

    render(os.path.join(IMG, 'stale-fd.svg'), W, H, *p,
           title="Куди веде вже відкритий дескриптор після копіювання вгору")


# ── 4. Анатомія рядка шарів: двокрапки й порядок ────────────────────────────
def fig_layer_string():
    W, H = 1240, 720
    p = []

    # ---- рядок опції ----
    p.append(text(60, 96, "lowerdir=", size=15, bold=True, anchor="start",
                  color=MUTED))

    seg = [("/l1", BLUE_FILL), ("/l2", BLUE_FILL), ("/l3", BLUE_FILL),
           ("/d1", GREY_FILL), ("/d2", GREY_FILL)]
    cx = [250, 400, 550, 760, 940]
    for (name, fill), x in zip(seg, cx):
        frag, _, _ = textbox(x, 90, name, size=15, pad=14, fill=fill,
                             stroke=MUTED, sw=1.4, min_w=110)
        p.append(frag)

    p.append(text(325, 96, ":", size=22, bold=True, color=INK))
    p.append(text(475, 96, ":", size=22, bold=True, color=INK))
    p.append(text(655, 96, "::", size=22, bold=True, color=POS))
    p.append(text(850, 96, "::", size=22, bold=True, color=POS))

    p.append(text(655, 140, "подвійна двокрапка", size=11, color=POS))
    p.append(text(655, 158, "відкриває шари-лише-дані", size=11, color=POS))

    p.append(arrow(600, 196, 600, 232, color=MUTED))
    p.append(text(600, 216, "лівіше — вище", size=12, anchor="start",
                  color=MUTED))

    # ---- стос шарів ----
    BW, BH = 230, 46
    bx = 270
    rows = [
        ("upperdir=/u", WARM_FILL, WARM,
         "усі зміни, білило, непрозорість"),
        ("/l1", BLUE_FILL, MUTED, "пошук імені спиняється на першому влучанні"),
        ("/l2", BLUE_FILL, MUTED, "каталоги зливаються з усіх цих шарів"),
        ("/l3", BLUE_FILL, MUTED, "останній шар, де шукають за іменем"),
    ]
    y = 272
    for label, fill, stroke, note in rows:
        p.append(fitbox(bx - BW / 2, y - BH / 2, BW, BH, label, size=15,
                        fill=fill, stroke=stroke, sw=1.5))
        p.append(text(bx + BW / 2 + 28, y + 5, note, size=12, anchor="start"))
        y += 60

    p.append(line(90, y - 24, 1160, y - 24, color=POS, sw=1.6, dash="7 5"))
    p.append(text(96, y - 4, "межа злиття імен: нижче ядро імен не шукає",
                  size=12, anchor="start", color=POS))

    y += 24
    for label in ("/d1", "/d2"):
        p.append(fitbox(bx - BW / 2, y - BH / 2, BW, BH, label, size=15,
                        fill=GREY_FILL, stroke=MUTED, sw=1.5))
        y += 60

    p.append(text(bx + BW / 2 + 28, y - 96,
                  "шари-лише-дані: імен звідси не видно;", size=12,
                  anchor="start"))
    p.append(text(bx + BW / 2 + 28, y - 76,
                  "до вмісту веде лише metacopy-файл", size=12, anchor="start"))
    p.append(text(bx + BW / 2 + 28, y - 56,
                  "з абсолютним redirect у верхньому шарі", size=12,
                  anchor="start"))

    p.append(text(W / 2, y + 16,
                  "upperdir і workdir у рядок lowerdir не входять — це окремі опції",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'layer-string.svg'), W, H, *p,
           title="Рядок шарів: що означає кожна двокрапка")


# ── 5. Розрив жорсткого посилання й що з ним робить index=on ────────────────
def fig_hardlink_index():
    W, H = 1240, 590
    p = []

    def name_box(cx, s):
        frag, _, _ = textbox(cx, 175, s, size=13, pad=11, fill=BLUE_FILL,
                             stroke=MUTED, sw=1.3, min_w=76)
        return frag

    def inode_box(cx, lines, fill):
        frag, _, _ = textbox(cx, 300, lines, size=12, pad=11, fill=fill,
                             stroke=MUTED, sw=1.3)
        return frag

    panels = [
        (20,  "до першого запису", "обидва імені — з нижнього шару",
         ["одне тіло, два імені —",
          "рівно так, як лежить у нижньому шарі"]),
        (420, "після запису в h1, index=off", "копію ніхто не пов'язав з тілом",
         ["два різні файли й різний вміст:",
          "зміна крізь h1 не видна крізь h2"]),
        (820, "після запису в h1, index=on", "покажчик у робочому каталозі",
         ["пошук h2 знаходить ту саму копію",
          "через покажчик — посилання ціле"]),
    ]

    for px, title, sub, caption in panels:
        p.append(rect(px, 70, 380, 430, fill="#fbfbfd", stroke=MUTED, sw=1.2,
                      rx=12))
        p.append(text(px + 190, 100, title, size=13, bold=True))
        p.append(text(px + 190, 122, sub, size=11, color=MUTED))
        p.append(name_box(px + 105, "h1"))
        p.append(name_box(px + 275, "h2"))
        p.append(mtext(px + 190, 392, caption, size=11, color=MUTED))

    # панель 1 — одне нижнє тіло
    p.append(inode_box(210, ["нижній inode 17", "nlink = 2"], GREY_FILL))
    p.append(arrow(125, 196, 178, 272))
    p.append(arrow(295, 196, 242, 272))

    # панель 2 — тіла роз'їхалися
    p.append(inode_box(515, ["верхній inode 91", "nlink = 1"], WARM_FILL))
    p.append(inode_box(705, ["нижній inode 17", "nlink = 2"], GREY_FILL))
    p.append(arrow(525, 196, 518, 272))
    p.append(arrow(695, 196, 702, 272))

    # панель 3 — покажчик тримає тіло одним
    p.append(inode_box(1010, ["верхній inode 91", "nlink = 2"], WARM_FILL))
    p.append(arrow(925, 196, 978, 272))
    p.append(arrow(1095, 196, 1042, 272))
    frag, _, _ = textbox(1010, 425, ["work/index/<дескриптор>",
                                     "теж жорстке посилання на копію"],
                         size=11, pad=10, fill=GREEN_FILL, stroke=FIELD, sw=1.3)
    p.append(frag)
    p.append(arrow(1010, 398, 1010, 330, color=FIELD))

    p.append(text(W / 2, 550,
                  "покажчик коштує накопиченим станом: він прив'язаний саме до "
                  "цих нижніх шарів і без них бреше",
                  size=13, color=INK))

    render(os.path.join(IMG, 'hardlink-index.svg'), W, H, *p,
           title="Копіювання вгору розриває жорстке посилання; index=on його рятує")


if __name__ == '__main__':
    fig_merge_table()
    fig_copy_up()
    fig_stale_fd()
    fig_layer_string()
    fig_hardlink_index()
    print("ok")
