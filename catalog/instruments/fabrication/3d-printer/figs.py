# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: анатомія й рухи декартового принтера ──────────────────────────
def fig_anatomy():
    W, H = 720, 540
    f = []

    # робочий об'єм (куб-каркас) — легка рамка
    # передня грань
    fx, fy, fw, fh = 150, 120, 340, 300
    f.append(rect(fx, fy, fw, fh, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=2))
    # ілюзія глибини — задні лінії
    dx, dy = 60, -46
    for (ax, ay) in [(fx, fy), (fx + fw, fy), (fx, fy + fh), (fx + fw, fy + fh)]:
        f.append(line(ax, ay, ax + dx, ay + dy, color="#c8ccd2", sw=1.2))
    f.append(line(fx + dx, fy + dy, fx + fw + dx, fy + dy, color="#c8ccd2", sw=1.2))
    f.append(line(fx + dx, fy + dy, fx + dx, fy + fh + dy, color="#c8ccd2", sw=1.2))

    # стіл (bed) — рухається по Y (вперед-назад)
    bed_y = fy + fh - 34
    f.append(rect(fx + 24, bed_y, fw - 48, 20, fill="#e9edf2", stroke=LINE, sw=1.6, rx=3))
    f.append(text(fx + fw / 2, bed_y + 44, "стіл (нагрівається)", size=13, color=INK))

    # портал по X (горизонтальна балка вгорі), каретка з друкувальною головою
    gantry_y = fy + 70
    f.append(line(fx + 20, gantry_y, fx + fw - 20, gantry_y, color=LINE, sw=3))
    # каретка + хотенд
    hx = fx + fw / 2 + 40
    f.append(rect(hx - 22, gantry_y - 8, 44, 22, fill="#dfe4ea", stroke=LINE, sw=1.6, rx=3))
    # хотенд (трикутник-сопло) вниз
    noz_y = gantry_y + 46
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#f4d6c4" stroke="%s" stroke-width="1.6"/>'
             % (hx - 12, gantry_y + 14, hx + 12, gantry_y + 14, hx, noz_y, LINE))
    # свіжовикладена лінія на столі під соплом
    f.append(line(fx + 40, bed_y - 2, hx, noz_y + 2, color=POS, sw=2.4))

    # осі руху — стрілки з підписами, розставлені з запасом ПОЗА каркасом
    # X: уздовж портала (голова їздить ліво-право)
    f.append(arrow(hx + 40, gantry_y - 26, hx + 92, gantry_y - 26, color=NEG, sw=2))
    f.append(arrow(hx + 40, gantry_y - 26, hx - 12, gantry_y - 26, color=NEG, sw=2))
    f.append(text(hx + 40, gantry_y - 36, "X — голова", size=13, color=NEG, bold=True))

    # Y: стіл вперед-назад (по глибині) — стрілка вздовж напряму глибини праворуч від куба
    yx = fx + fw + 96
    f.append(arrow(yx, bed_y + 4, yx + 44, bed_y + 4 + dy * 0.7, color=FIELD, sw=2))
    f.append(arrow(yx, bed_y + 4, yx - 6, bed_y + 4 - dy * 0.2, color=FIELD, sw=2))
    f.append(text(yx + 30, bed_y + 40, "Y — стіл", size=13, color=FIELD, bold=True))

    # Z: увесь портал угору-вниз — стрілка ліворуч від куба
    zx = fx - 46
    f.append(arrow(zx, gantry_y + 40, zx, gantry_y - 30, color=POS, sw=2))
    f.append(arrow(zx, gantry_y + 40, zx, gantry_y + 110, color=POS, sw=2))
    f.append(text(zx - 4, gantry_y - 42, "Z — портал", size=13, color=POS, bold=True, anchor="middle"))

    # котушка з філаментом і напрям подачі
    sp_cx, sp_cy = 610, 150
    f.append(circle(sp_cx, sp_cy, 46, fill="#eef1f4", stroke=LINE, sw=1.6))
    f.append(circle(sp_cx, sp_cy, 12, fill=BG, stroke=LINE, sw=1.4))
    f.append(text(sp_cx, sp_cy + 74, "котушка", size=13, color=INK))
    f.append(text(sp_cx, sp_cy + 92, "філаменту", size=13, color=INK))
    # нитка від котушки до голови
    f.append(line(sp_cx - 44, sp_cy + 8, hx + 4, gantry_y - 6, color="#b06a3a", sw=2, dash="5,4"))

    render(os.path.join(OUT, "anatomy.svg"), W, H, *f,
           title="Декартовий 3D-принтер: три осі та що по якій їздить")


# ── Фігура 2: розріз хотенда (гаряча/холодна зона) ───────────────────────────
def fig_hotend():
    W, H = 640, 560
    f = []

    cx = 250          # вісь хотенда
    top = 90
    # холодний кінець: радіатор із ребрами
    hs_w, hs_h = 96, 120
    f.append(rect(cx - hs_w / 2, top, hs_w, hs_h, fill="#e8ecf1", stroke=LINE, sw=1.6, rx=4))
    for i in range(5):
        yy = top + 16 + i * 22
        f.append(line(cx - hs_w / 2, yy, cx + hs_w / 2, yy, color=MUTED, sw=1.2))
    # тепловідвідний вентилятор — збоку
    f.append(rect(cx - hs_w / 2 - 60, top + 24, 46, 70, fill="#eef1f4", stroke=LINE, sw=1.5, rx=6))
    f.append(text(cx - hs_w / 2 - 37, top + 62, "◊", size=22, color=MUTED))
    f.append(arrow(cx - hs_w / 2 - 12, top + 40, cx - hs_w / 2 + 6, top + 40, color=NEG, sw=1.8))
    f.append(arrow(cx - hs_w / 2 - 12, top + 78, cx - hs_w / 2 + 6, top + 78, color=NEG, sw=1.8))

    # горло (heat-break) — тонка шийка
    hb_top = top + hs_h
    hb_h = 46
    f.append(rect(cx - 10, hb_top, 20, hb_h, fill="#d7dbe0", stroke=LINE, sw=1.6, rx=2))

    # нагрівальний блок
    blk_top = hb_top + hb_h
    blk_w, blk_h = 92, 66
    f.append(rect(cx - blk_w / 2, blk_top, blk_w, blk_h, fill="#f6d0be", stroke=LINE, sw=1.8, rx=4))
    # картридж-нагрівач (циліндр у блоці)
    f.append(rect(cx - blk_w / 2 + 8, blk_top + 20, 24, 26, fill="#f2b199", stroke=POS, sw=1.6, rx=8))
    # термістор (кулька-давач)
    f.append(circle(cx + blk_w / 2 - 16, blk_top + 33, 9, fill="#fff3d6", stroke="#b8860b", sw=1.6))

    # сопло — конус донизу
    noz_top = blk_top + blk_h
    noz_y = noz_top + 40
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" '
             'fill="#f2b199" stroke="%s" stroke-width="1.8"/>'
             % (cx - 30, noz_top, cx + 30, noz_top, cx + 5, noz_y, cx - 5, noz_y, LINE))

    # філамент: твердий згори (у горлі), розплав у блоці, вихід ниткою
    f.append(rect(cx - 4, top - 34, 8, 34 + hs_h + hb_h + 8, fill="#b06a3a", stroke="none"))  # тверда нитка
    f.append(rect(cx - 4, blk_top + 8, 8, blk_h - 4, fill="#d98a52", stroke="none"))            # розплав
    f.append(line(cx, noz_y, cx, noz_y + 34, color="#d98a52", sw=3))                            # тонка нитка на виході
    f.append(text(cx, top - 42, "філамент (твердий)", size=13, color="#8a5a30"))

    # межа «холодно / гаряче» — пунктир упоперек горла
    f.append(line(cx - 120, hb_top + hb_h * 0.5, cx + 120, hb_top + hb_h * 0.5,
                  color=POS, sw=1.4, dash="6,4"))

    # ── підписи праворуч, кожен зі своєю лінією-вказівником, з ЗАПАСОМ ──
    lx = 430
    def label(y, txt, color=INK, to=None):
        box, w, h = textbox(lx + 90, y, txt, size=12.5, color=color, pad=8, min_w=170)
        f.append(box)
        if to is not None:
            f.append(line(lx + 90 - w / 2, y, to[0], to[1], color=MUTED, sw=1.1))
    label(top + 40, "Холодний кінець:\nрадіатор + вентилятор", to=(cx + hs_w / 2, top + 40))
    label(hb_top + 12, "Горло (тонке):\nмежа тепла", color=POS, to=(cx + 10, hb_top + 12))
    label(blk_top + 6, "Нагрівач у блоці", color=POS, to=(cx + blk_w / 2, blk_top + 10))
    label(blk_top + 44, "Термістор:\nміряє температуру", color="#8a6d0b", to=(cx + blk_w / 2 - 8, blk_top + 33))
    label(noz_y - 2, "Сопло 0.4 мм:\nвихід розплаву", to=(cx + 8, noz_y - 6))

    # підписи зон ліворуч
    f.append(text(120, top + 70, "холодно", size=12.5, color=NEG, bold=True))
    f.append(text(120, blk_top + 40, "гаряче", size=12.5, color=POS, bold=True))

    render(os.path.join(OUT, "hotend.svg"), W, H, *f,
           title="Розріз хотенда: де нитка твердне, де плавиться")


# ── Фігура 3: принцип — тверде в, розплав вниз, шар за шаром ─────────────────
def fig_layers():
    W, H = 700, 430
    f = []

    # ліворуч: одна викладена лінія в розрізі (тверде входить → розплав виходить)
    lx = 190
    top = 90
    # подавальні шестерні (два кола) штовхають нитку
    f.append(circle(lx - 18, top, 16, fill="#eef1f4", stroke=LINE, sw=1.6))
    f.append(circle(lx + 18, top, 16, fill="#eef1f4", stroke=LINE, sw=1.6))
    f.append(arrow(lx, top - 44, lx, top - 18, color=INK, sw=2))
    f.append(text(lx, top - 52, "нитка твердою входить", size=12.5, color="#8a5a30"))
    # шлях нитки крізь сопло
    f.append(rect(lx - 4, top + 16, 8, 70, fill="#b06a3a", stroke="none"))
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" '
             'fill="#f2b199" stroke="%s" stroke-width="1.6"/>'
             % (lx - 22, top + 86, lx + 22, top + 86, lx + 5, top + 120, lx - 5, top + 120, LINE))
    # викладені смужки під соплом (кілька шарів)
    bead_y0 = top + 150
    for r in range(3):
        yy = bead_y0 - r * 12
        f.append(rect(lx - 70, yy, 140, 11, fill="#d98a52", stroke="#b06a3a", sw=1.0, rx=5))
    # поточна смужка тягнеться від сопла
    f.append(line(lx, top + 120, lx + 60, bead_y0 + 5, color="#d98a52", sw=5))
    f.append(text(lx, bead_y0 + 44, "розплав лягає смужкою", size=12.5, color="#8a5a30"))
    f.append(text(lx, bead_y0 + 62, "і одразу застигає", size=12.5, color=INK))

    # праворуч: об'єкт як стос шарів + думка «модель ріжуть на шари»
    rx = 500
    ry0 = 300
    f.append(text(rx, 76, "деталь = стос тонких шарів", size=13.5, color=INK, bold=True))
    n = 11
    for i in range(n):
        yy = ry0 - i * 18
        # ширина шарів імітує форму (трохи ваза)
        half = 70 - abs(i - n / 2) * 3
        f.append(rect(rx - half, yy, 2 * half, 15, fill="#e9edf2", stroke=LINE, sw=1.2, rx=3))
    # стрілка «висота Z росте»
    f.append(arrow(rx + 108, ry0 + 12, rx + 108, ry0 - n * 18 + 6, color=POS, sw=2))
    f.append(text(rx + 150, ry0 - n * 9, "Z росте:", size=12.5, color=POS, bold=True))
    f.append(text(rx + 150, ry0 - n * 9 + 18, "шар за шаром", size=12.5, color=POS))

    render(os.path.join(OUT, "layers.svg"), W, H, *f,
           title="Пошарове вирощування: тверде — в, розплав — униз, шар — на шар")


# ── Фігура 4 (hist): дві дороги настільного друку сходяться у 2009 ───────────
def fig_two_roads():
    W, H = 860, 470
    f = []

    # Вертикальна вісь часу — роки ліворуч; дві смуги-дороги праворуч від неї.
    x_axis = 120
    y_top, y_bot = 88, 410
    f.append(line(x_axis, y_top - 10, x_axis, y_bot + 10, color=MUTED, sw=1.4))

    years = [1989, 1992, 2005, 2006, 2009, 2010, 2012]
    def y_of(year):
        # рівномірно за ПОРЯДКОМ подій (не за масштабом років), щоб не тиснути
        i = years.index(year)
        return y_top + i * (y_bot - y_top) / (len(years) - 1)
    for yr in years:
        yy = y_of(yr)
        f.append(line(x_axis - 5, yy, x_axis + 5, yy, color=MUTED, sw=1.3))
        f.append(text(x_axis - 16, yy + 5, str(yr), size=13, color=INK, bold=True, anchor="end"))

    # ── ліва дорога: закрита (Stratasys) ──
    lx = 300
    f.append(text(lx, y_top - 34, "Закрита дорога", size=14, color=POS, bold=True))
    f.append(text(lx, y_top - 17, "Stratasys / FDM™", size=12.5, color=MUTED))
    f.append(line(lx, y_of(1989), lx, y_of(2009), color=POS, sw=3))
    # застигла після 2009 (пунктир — марка лишається, монополія падає)
    f.append(line(lx, y_of(2009), lx, y_of(2012), color=POS, sw=1.6, dash="5,5"))

    def lnode(year, txt, side="left"):
        yy = y_of(year)
        f.append(circle(lx, yy, 6, fill=BG, stroke=POS, sw=2))
        box, w, h = textbox(lx - 92, yy, txt, size=11.5, color=INK, pad=7, min_w=150)
        f.append(box)
        f.append(line(lx - 6, yy, lx - 92 + w / 2, yy, color=MUTED, sw=1.0))
    lnode(1989, "Крамп подає патент\nна FDM; засновано\nStratasys")
    lnode(1992, "патент US 5,121,329\nвидано — 20 років\nмонополії")

    # ── права дорога: відкрита (RepRap) ──
    rx = 560
    f.append(text(rx, y_top - 34, "Відкрита дорога", size=14, color=FIELD, bold=True))
    f.append(text(rx, y_top - 17, "RepRap / FFF", size=12.5, color=MUTED))
    f.append(line(rx, y_of(2005), rx, y_of(2012), color=FIELD, sw=3))

    def rnode(year, txt):
        yy = y_of(year)
        f.append(circle(rx, yy, 6, fill=BG, stroke=FIELD, sw=2))
        box, w, h = textbox(rx + 96, yy, txt, size=11.5, color=INK, pad=7, min_w=170)
        f.append(box)
        f.append(line(rx + 6, yy, rx + 96 - w / 2, yy, color=MUTED, sw=1.0))
    rnode(2005, "Бойєр стартує RepRap\nу Баті; вигадано\nвільну назву FFF")
    rnode(2006, "перша самокопія:\nпринтер друкує\nсвою деталь")
    rnode(2010, "Prusa i3 (Průša)\nна базі Mendel —\nмасовий стандарт")
    rnode(2012, "MakerBot, Ultimaker,\nPrusa: ціна з десятків\nтисяч → сотні $")

    # ── вузол сходження 2009: патент падає ──
    ym = y_of(2009)
    f.append(line(lx, ym, rx, ym, color=INK, sw=1.4, dash="2,4"))
    box, w, h = textbox((lx + rx) / 2, ym - 30, "2009: патент FDM спливає —\nбудувати може будь-хто",
                        size=12, color=POS, bold=True, pad=8, fill="#fdecea", stroke=POS, min_w=250)
    f.append(box)

    render(os.path.join(OUT, "two-roads.svg"), W, H, *f,
           title="Дві дороги настільного друку: закрита й відкрита сходяться у 2009")


# ── Фігура (proj-gcode): розбір рядка G-коду на слово-адреси ─────────────────
def fig_gword():
    W, H = 760, 440
    f = []

    words = [
        ("G1", "команда:\nрух по прямій", NEG),
        ("X80", "куди по X\n(мм)", INK),
        ("Y20", "куди по Y\n(мм)", INK),
        ("Z0.2", "висота шару\n(мм)", INK),
        ("E5", "видати нитки\n(мм)", "#b06a3a"),
        ("F1200", "швидкість\n(мм/хв)", FIELD),
    ]
    x0 = 30
    colw = (W - 2 * x0) / len(words)
    row_y = 96
    for i, (w, desc, col) in enumerate(words):
        cx = x0 + colw * (i + 0.5)
        bw = 92
        f.append(rect(cx - bw / 2, row_y - 22, bw, 40, fill="#eef2f7", stroke=LINE, sw=1.6, rx=5))
        f.append(text(cx, row_y + 5, w, size=19, color=col, bold=True))
        f.append(line(cx, row_y + 20, cx, row_y + 62, color=MUTED, sw=1.1))
        box, bwd, bhd = textbox(cx, row_y + 96, desc, size=11.5, color=col, pad=6, min_w=colw - 16)
        f.append(box)

    key_y = 296
    f.append(text(W / 2, key_y, "Кожне слово = літера-адреса + число-значення",
                  size=15, color=INK, bold=True))
    lines = [
        "G / M — що робити (G — рух; M — усе інше: нагрів, вентилятор, режими)",
        "X Y Z — координати сопла у просторі, у міліметрах",
        "E — скільки міліметрів нитки згодувати подавачу дорогою",
        "F — задана швидкість руху (мм/хв); тримається до наступної зміни",
    ]
    for i, ln in enumerate(lines):
        f.append(text(W / 2, key_y + 32 + i * 25, ln, size=13, color=INK))

    render(os.path.join(OUT, "gword.svg"), W, H, *f,
           title="Як прочитати рядок G-коду руками")


# ── Фігура (proj-gcode): absolute vs relative extrusion ─────────────────────
def fig_extrude_mode():
    W, H = 760, 380
    f = []

    seg = ["+5 мм", "+5 мм", "+5 мм"]
    xs = [210, 380, 550]
    baseline = 150

    f.append(text(W / 2, 58, "Три однакові дії «видай ще 5 мм нитки»",
                  size=15, color=INK, bold=True))

    # нитка як короткі відрізки МІЖ порціями (не крізь написи в блоках)
    f.append(line(xs[0] - 60, baseline, xs[0] - 42, baseline, color="#b06a3a", sw=2))
    for i in range(len(xs) - 1):
        f.append(line(xs[i] + 42, baseline, xs[i + 1] - 42, baseline, color="#b06a3a", sw=2))
    f.append(line(xs[-1] + 42, baseline, xs[-1] + 60, baseline, color="#b06a3a", sw=2))
    for i, xc in enumerate(xs):
        f.append(rect(xc - 42, baseline - 15, 84, 30, fill="#f6e3d4", stroke="#b06a3a", sw=1.5, rx=4))
        f.append(text(xc, baseline + 6, seg[i], size=14, color="#8a5a30", bold=True))

    # підписи рядків — ліворуч у ВЛАСНІЙ колонці (x<160), щоб не перетинати стовпці E
    ya = 240
    f.append(text(70, ya + 5, "M82 →", size=15, color=NEG, bold=True, anchor="start"))
    f.append(text(W / 2, 200, "M82 — абсолютна подача: E = усього від нуля",
                  size=13, color=NEG, bold=True))
    abs_vals = ["E5", "E10", "E15"]
    for i, xc in enumerate(xs):
        box, bw, bh = textbox(xc, ya, abs_vals[i], size=14, color=NEG, pad=8, min_w=72)
        f.append(box)

    yr = 316
    f.append(text(70, yr + 5, "M83 →", size=15, color=FIELD, bold=True, anchor="start"))
    f.append(text(W / 2, 288, "M83 — відносна подача: E = скільки додати",
                  size=13, color=FIELD, bold=True))
    rel_vals = ["E5", "E5", "E5"]
    for i, xc in enumerate(xs):
        box, bw, bh = textbox(xc, yr, rel_vals[i], size=14, color=FIELD, pad=8, min_w=72)
        f.append(box)

    render(os.path.join(OUT, "extrude-mode.svg"), W, H, *f,
           title="Одна подача — два різні числа E")


if __name__ == "__main__":
    fig_anatomy()
    fig_hotend()
    fig_layers()
    fig_two_roads()
    fig_gword()
    fig_extrude_mode()
    print("figures written to", OUT)
