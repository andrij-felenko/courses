# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

LASER = "#c0392b"   # промінь
ECHO  = "#2457d6"   # відлуння / прийом
GOOD  = "#27ae60"   # перевага
DOT   = "#1f8a3b"   # точка хмари


# ── 1. Проблема: один промінь = одна точка ────────────────────────────────────
# Ідея: далекомір дає ОДНЕ число; щоб вийшла сцена, промінь треба навести скрізь.
def fig_scan_problem():
    W, H = 720, 330
    f = []
    # давач ліворуч
    f.append(rect(40, H/2 - 28, 70, 56, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(75, H/2 + 5, "давач", size=13, bold=True))
    # один промінь до однієї точки на стіні
    wall_x = 560
    f.append(line(40, 30, wall_x, 30, color=MUTED, sw=1, dash="4 4"))   # верх стіни
    f.append(line(40, H-30, wall_x, H-30, color=MUTED, sw=1, dash="4 4"))
    f.append(rect(wall_x, 40, 16, H-80, fill="#eceff3", stroke=INK, sw=1.5))
    f.append(text(wall_x + 8, 28, "сцена", size=12, color=MUTED))
    # активний промінь у центр
    cy = H/2
    f.append(arrow(110, cy, wall_x - 2, cy, color=LASER, sw=2.4))
    f.append(circle(wall_x - 2, cy, 5, fill=DOT, stroke=DOT, sw=1))
    f.append(text(330, cy - 12, "один промінь", size=13, color=LASER, bold=True))
    f.append(text(330, cy + 22, "→ одне число: відстань", size=12, color=MUTED))
    # привиди інших напрямків, куди треба ще влучити
    for dy in (-90, -45, 45, 90):
        f.append(line(110, cy, wall_x - 2, cy + dy, color=MUTED, sw=1, dash="2 5"))
        f.append(circle(wall_x - 2, cy + dy, 4, fill=BG, stroke=MUTED, sw=1.3))
    b, w, h = textbox(330, H - 26, "щоб вийшла 3D-картина — навести промінь у тисячі напрямків", size=12, color=INK, fill="#fff8e1", stroke="#e0a800")
    f.append(b)
    return render(os.path.join(OUT, "scan-problem.svg"), W, H, *f,
                  title="Серце LiDAR — не вимір, а наведення")


# ── 2. Чотири архітектури: як саме повертають промінь ─────────────────────────
def fig_architectures():
    W, H = 760, 470
    f = []
    # дерево: механічний | твердотільний (MEMS, OPA, flash)
    f.append(text(W/2, 30, "Як промінь обходить сцену", size=15, bold=True))
    # верхній вузол
    f.append(text(W/2, 58, "обертати щось ваговите  vs  жодного руху", size=12, color=MUTED))

    col_w, gap = 168, 18
    x0 = (W - (4*col_w + 3*gap)) / 2
    top = 86
    boxh = 56
    cols = [
        ("Механічний", "мотор крутить\nдзеркало / голову", LASER, False),
        ("MEMS-дзеркало", "мікродзеркало\nхитається", "#8e44ad", True),
        ("Фазована\nрешітка (OPA)", "фаза випромінювачів\nкерує променем", ECHO, True),
        ("Flash", "спалах на всю сцену,\nматриця ловить", GOOD, True),
    ]
    for i, (name, how, col, solid) in enumerate(cols):
        x = x0 + i*(col_w+gap)
        f.append(fitbox(x, top, col_w, boxh, name, size=14, bold=True,
                        fill="#f4f6f8", stroke=col, sw=2.2, color=col))
        f.append(fitbox(x, top+boxh+8, col_w, 46, how, size=11, color=INK,
                        fill=BG, stroke=MUTED, sw=1.2))
        tag = "твердотільний" if solid else "є рухомі частини"
        tc = GOOD if solid else MUTED
        f.append(text(x + col_w/2, top+boxh+8+46+18, tag, size=11, color=tc, bold=solid))

    # — нижче маленькі піктограми принципу —
    py = 300
    # механічний: коло зі стрілкою-обертанням і промінь
    cx = x0 + col_w/2
    f.append(circle(cx, py+34, 26, fill=BG, stroke=LASER, sw=2))
    f.append(arrow(cx+18, py+12, cx+30, py+30, color=LASER, sw=1.8))
    f.append(line(cx, py+34, cx+58, py+10, color=LASER, sw=2))
    f.append(line(cx, py+34, cx+58, py+58, color=LASER, sw=2, dash="3 3"))

    # MEMS: маленьке дзеркало під кутом, дві позиції
    cx = x0 + (col_w+gap) + col_w/2
    f.append(line(cx-14, py+44, cx+14, py+24, color="#8e44ad", sw=4))   # дзеркало
    f.append(line(cx-14, py+40, cx+14, py+34, color="#8e44ad", sw=2, dash="3 3"))
    f.append(arrow(cx, py+34, cx+60, py+6, color="#8e44ad", sw=1.8))
    f.append(arrow(cx, py+34, cx+60, py+58, color="#8e44ad", sw=1.8, ))

    # OPA: ряд випромінювачів, фронт під кутом
    cx = x0 + 2*(col_w+gap) + col_w/2
    for k in range(5):
        yy = py + 12 + k*11
        f.append(circle(cx-46, yy, 3.2, fill=ECHO, stroke=ECHO, sw=1))
    f.append(line(cx-30, py+10, cx+50, py+22, color=ECHO, sw=2))        # нахилений фронт
    f.append(line(cx-30, py+30, cx+50, py+42, color=ECHO, sw=2))
    f.append(arrow(cx+10, py+34, cx+58, py+18, color=ECHO, sw=1.8))

    # flash: широкий конус на матрицю
    cx = x0 + 3*(col_w+gap) + col_w/2
    f.append(line(cx-40, py+34, cx+52, py+8, color=GOOD, sw=1.6))
    f.append(line(cx-40, py+34, cx+52, py+60, color=GOOD, sw=1.6))
    f.append(line(cx-40, py+34, cx+52, py+34, color=GOOD, sw=1.2, dash="3 3"))
    for r in range(4):
        for c in range(3):
            f.append(rect(cx+34+c*7, py+18+r*8, 6, 7, fill="#eef7ee", stroke=GOOD, sw=0.8, rx=1))

    b, w, h = textbox(W/2, H-26, "ліворуч — груба механіка, що крутиться; праворуч — дедалі більше на кристалі, без руху",
                      size=12, color=INK, fill=FILL, stroke=LINE)
    f.append(b)
    return render(os.path.join(OUT, "architectures.svg"), W, H, *f)


# ── 3. Друга вісь: ЩО міряємо — імпульс vs ЛЧМ-хвиля ──────────────────────────
def fig_tof_vs_fmcw():
    W, H = 740, 380
    f = []
    f.append(text(W/2, 28, "Дві мови далекоміра: засічка часу vs частота биття", size=14, bold=True))

    midx = W/2
    f.append(line(midx, 50, midx, H-40, color=MUTED, sw=1, dash="5 5"))

    # ── ліворуч: імпульсний ToF ──
    lx = 40
    f.append(text(180, 64, "Імпульсний ToF", size=13, bold=True, color=LASER))
    base = 150
    f.append(line(lx, base, 340, base, color=MUTED, sw=1))           # вісь часу
    f.append(text(340, base+16, "час", size=11, color=MUTED, anchor="end"))
    # вузький пік — посилка
    f.append(line(lx+30, base, lx+30, base-50, color=LASER, sw=2.4))
    f.append(line(lx+28, base-50, lx+32, base-50, color=LASER, sw=2.4))
    f.append(text(lx+30, base-58, "пуск", size=10, color=LASER))
    # вузький пік — відлуння, пізніше
    f.append(line(lx+210, base, lx+210, base-34, color=ECHO, sw=2.4))
    f.append(line(lx+208, base-34, lx+212, base-34, color=ECHO, sw=2.4))
    f.append(text(lx+210, base-42, "відлуння", size=10, color=ECHO))
    # Δt
    f.append(line(lx+30, base+22, lx+210, base+22, color=INK, sw=1.2))
    f.append(text(lx+120, base+38, "Δt → відстань", size=12, bold=True))
    f.append(fitbox(60, base+70, 240, 40, "коротка потужна посилка;\nточність = гострота таймера",
                    size=11, color=INK, fill=BG, stroke=MUTED, sw=1.2))

    # ── праворуч: FMCW ──
    rx = midx + 30
    f.append(text(midx+200, 64, "FMCW (ЛЧМ)", size=13, bold=True, color=GOOD))
    base2 = 150
    # дві похилі лінії частоти (передана й прийнята зі зсувом)
    f.append(line(rx, base2, rx+250, base2-70, color=LASER, sw=2.2))       # передана: частота росте
    f.append(line(rx+34, base2, rx+284, base2-70, color=ECHO, sw=2.2, dash="5 4"))  # прийнята: зсунута
    f.append(text(rx+250, base2-76, "f передана", size=10, color=LASER, anchor="end"))
    f.append(text(rx+288, base2-50, "прийнята", size=10, color=ECHO, anchor="start"))
    # вертикальний проміжок = beat
    f.append(line(rx+170, base2-47, rx+170, base2-23, color=INK, sw=1.4))
    f.append(text(rx+178, base2-30, "f_beat", size=11, bold=True, anchor="start"))
    f.append(line(rx, base2, rx+300, base2, color=MUTED, sw=1))
    f.append(text(rx+300, base2+16, "час", size=11, color=MUTED, anchor="end"))
    f.append(fitbox(midx+60, base2+70, 250, 40, "стала хвиля з «розчерком» частоти;\nбиття дає відстань + швидкість",
                    size=11, color=INK, fill="#eef7ee", stroke=GOOD, sw=1.4))
    return render(os.path.join(OUT, "tof-vs-fmcw.svg"), W, H, *f)


# ── 4. Порівняння архітектур (мапа вибору) ────────────────────────────────────
def fig_chooser():
    W, H = 780, 360
    rows = [
        # критерій,            механічний,        MEMS,            OPA,             flash
        ("Дальність",          "велика",          "середня",       "перспективна",  "мала"),
        ("Поле зору",          "360° навколо",    "сектор",        "сектор",        "широкий кадр"),
        ("Рухомі частини",     "мотор+дзеркало",  "мікродзеркало", "немає",         "немає"),
        ("Швидкість/кадр",     "обмежує оберт",   "швидко",        "дуже швидко",   "миттєвий кадр"),
        ("Зрілість",           "перевірена",      "масова",        "лабораторна",   "нішева"),
        ("Ціна за точку",      "висока",          "помірна",       "обіцяє низьку", "низька зблизька"),
    ]
    cols = ["", "Механічний", "MEMS", "OPA", "Flash"]
    nrow, ncol = len(rows)+1, len(cols)
    x0, y0 = 24, 50
    cw = [168, 152, 132, 152, 150]
    rh = 42
    f = [text(W/2, 30, "Архітектури поряд: що чим платить", size=15, bold=True)]
    # заголовок
    cx = x0
    for j, c in enumerate(cols):
        fill = "#eef2f7" if j == 0 else "#e8eef6"
        f.append(rect(cx, y0, cw[j], rh, fill=fill, stroke=INK, sw=1.3, rx=4))
        f.append(fitbox(cx, y0, cw[j], rh, c, size=12, bold=True, fill="none", stroke="none", color=INK))
        cx += cw[j]
    # рядки
    for i, row in enumerate(rows):
        ry = y0 + (i+1)*rh
        cx = x0
        for j, cell in enumerate(row):
            if j == 0:
                f.append(rect(cx, ry, cw[j], rh, fill="#f4f6f8", stroke=INK, sw=1.1, rx=4))
                f.append(fitbox(cx, ry, cw[j], rh, cell, size=11, bold=True, fill="none", stroke="none", color=INK))
            else:
                f.append(rect(cx, ry, cw[j], rh, fill=BG, stroke="#cfd6df", sw=1, rx=4))
                f.append(fitbox(cx+2, ry, cw[j]-4, rh, cell, size=10, fill="none", stroke="none", color=INK))
            cx += cw[j]
    return render(os.path.join(OUT, "chooser.svg"), W, H, *f)


# ── 5. Геометрія розчерку: чому беат = нахил × затримка (вставка math) ─────────
# Показуємо передану й прийняту пилку частоти; затримка τ зсуває прийняту вправо,
# а вертикальний проміжок між ними — стала частота биття. Підпис прямо до подібних
# трикутників: f_beat / τ = B / T.
def fig_chirp_geometry():
    W, H = 760, 430
    f = []
    f.append(text(W/2, 28, "Розчерк частоти: беат — це нахил, помножений на затримку", size=15, bold=True))

    # осі
    ox, oy = 70, H - 70          # початок координат
    axw, axh = 600, 280
    f.append(arrow(ox, oy, ox + axw, oy, color=MUTED, sw=1.4))      # час →
    f.append(arrow(ox, oy, ox, oy - axh, color=MUTED, sw=1.4))      # частота ↑
    f.append(text(ox + axw, oy + 22, "час t", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - axh + 4, "частота", size=12, color=MUTED, anchor="end"))

    # передана пилка (один розчерк): від f0 угору на B за час T
    t0, T = 90, 380              # початок і тривалість розчерку (в px по осі t)
    Bpx = 230                    # B у px по осі f
    f0y = oy - 30                # рівень f0
    txa = ox + t0
    txb = ox + t0 + T
    f.append(line(txa, f0y, txb, f0y - Bpx, color=LASER, sw=2.6))           # передана
    f.append(text(txb + 4, f0y - Bpx - 6, "передана", size=11, color=LASER, anchor="start", bold=True))

    # прийнята: та сама пилка, зсунута вправо на τ
    tau = 70                     # затримка в px
    f.append(line(txa + tau, f0y, txb + tau, f0y - Bpx, color=ECHO, sw=2.6, dash="6 5"))  # прийнята
    f.append(text(txb + tau + 4, f0y - Bpx + 16, "відлуння (зсув на τ)", size=11, color=ECHO, anchor="start", bold=True))

    # позначка τ на осі часу
    f.append(line(txa, oy, txa, f0y, color=MUTED, sw=1, dash="3 3"))
    f.append(line(txa + tau, oy, txa + tau, f0y, color=MUTED, sw=1, dash="3 3"))
    f.append(line(txa, oy - 12, txa + tau, oy - 12, color=INK, sw=1.3))
    f.append(text(txa + tau/2, oy - 18, "τ = 2d/c", size=12, bold=True))

    # f_beat — вертикальний проміжок між лініями в середині розчерку
    midt = txa + tau + 150
    # передана в момент midt
    frac1 = (midt - txa) / T
    yT = f0y - Bpx * frac1
    frac2 = (midt - (txa + tau)) / T
    yR = f0y - Bpx * frac2
    f.append(line(midt, yT, midt, yR, color="#c0392b", sw=2.6))
    f.append(text(midt + 8, (yT + yR)/2 + 4, "f_beat", size=12, bold=True, anchor="start", color="#c0392b"))

    # великий трикутник нахилу: уся ширина T і вся висота B
    f.append(line(txa, f0y, txb, f0y, color=MUTED, sw=1, dash="2 4"))            # горизонт основи
    f.append(line(txb, f0y, txb, f0y - Bpx, color=GOOD, sw=1.6, dash="4 3"))     # висота B
    f.append(text(txb + 4, f0y + 16, "T", size=12, color=GOOD, bold=True, anchor="start"))
    f.append(text(txb - 16, f0y - Bpx/2, "B", size=12, color=GOOD, bold=True, anchor="end"))

    b, w, h = textbox(W/2, H - 22,
                      "однакові трикутники:  f_beat / τ = B / T  ⇒  f_beat = (B/T)·(2d/c)",
                      size=12, bold=True, color=INK, fill="#fff8e1", stroke="#e0a800")
    f.append(b)
    return render(os.path.join(OUT, "chirp-geometry.svg"), W, H, *f)


# ── 6. Трикутний розчерк: як Допплер розщеплює беат на два (вставка math) ──────
# Угору й униз — два беати; рух цілі однаково зсуває обидва, відстань їх однаково
# піднімає; сума й різниця розв'язують відстань і швидкість.
def fig_triangle_doppler():
    W, H = 760, 420
    f = []
    f.append(text(W/2, 28, "Трикутний розчерк: дві частоти биття розплутують дальність і швидкість", size=14, bold=True))

    ox, oy = 70, 250
    axw = 620
    f.append(arrow(ox, oy, ox + axw, oy, color=MUTED, sw=1.4))
    f.append(arrow(ox, oy, ox, oy - 180, color=MUTED, sw=1.4))
    f.append(text(ox + axw, oy + 22, "час t", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - 176, "частота", size=12, color=MUTED, anchor="end"))

    # передана: трикутник угору-вниз
    base = oy - 24
    peak = oy - 150
    x1, x2, x3 = ox + 60, ox + 60 + 220, ox + 60 + 440
    f.append(line(x1, base, x2, peak, color=LASER, sw=2.6))   # вгору
    f.append(line(x2, peak, x3, base, color=LASER, sw=2.6))   # вниз
    f.append(text((x1+x2)/2 - 30, (base+peak)/2 - 6, "розчерк ↑", size=11, color=LASER, bold=True))
    f.append(text((x2+x3)/2 + 30, (base+peak)/2 - 6, "розчерк ↓", size=11, color=LASER, bold=True))

    # прийнята: та сама форма, зсунута вправо (затримка) і вгору (Допплер)
    dt = 26   # часовий зсув (дальність)
    dv = 14   # частотний зсув угору (рух назустріч)
    f.append(line(x1+dt, base-dv, x2+dt, peak-dv, color=ECHO, sw=2.4, dash="6 5"))
    f.append(line(x2+dt, peak-dv, x3+dt, base-dv, color=ECHO, sw=2.4, dash="6 5"))
    f.append(text(x3+dt+4, base-dv-4, "відлуння", size=11, color=ECHO, bold=True, anchor="start"))

    # беат на висхідній ділянці (менший) і на спадній (більший)
    mu = (x1 + x2) / 2 + 40       # точка виміру на висхідній
    yT_u = base + (peak-base)*((mu-x1)/(x2-x1))
    yR_u = (base-dv) + (peak-base)*((mu-(x1+dt))/(x2-x1))
    f.append(line(mu, yT_u, mu, yR_u, color="#27ae60", sw=2.6))
    f.append(text(mu - 6, (yT_u+yR_u)/2, "f_up", size=11, bold=True, anchor="end", color="#27ae60"))

    md = (x2 + x3) / 2 + 40       # точка виміру на спадній
    yT_d = peak + (base-peak)*((md-x2)/(x3-x2))
    yR_d = (peak-dv) + (base-peak)*((md-(x2+dt))/(x3-x2))
    f.append(line(md, yT_d, md, yR_d, color="#8e44ad", sw=2.6))
    f.append(text(md + 6, (yT_d+yR_d)/2, "f_down", size=11, bold=True, anchor="start", color="#8e44ad"))

    # дві формули-висновки праворуч-внизу
    f.append(fitbox(ox + 30, oy + 50, 320, 56,
                    "відстань:  f_R = (f_up + f_down) / 2\n→ півсума прибирає Допплер",
                    size=12, color=INK, fill="#eef7ee", stroke=GOOD, sw=1.4))
    f.append(fitbox(ox + 370, oy + 50, 320, 56,
                    "швидкість:  f_D = (f_down − f_up) / 2\n→ піврізниця прибирає дальність",
                    size=12, color=INK, fill="#f3eefb", stroke="#8e44ad", sw=1.4))
    return render(os.path.join(OUT, "triangle-doppler.svg"), W, H, *f)


# ── 7. Сходи підсилення: PIN → APD → SPAD (лінійний vs Гейгер) ────────────────
# Вставка comp-lidar-photodetector: де живе кожен клас на шкалі підсилення
# і чому за Vbr поведінка стрибком міняється з «лінійної» на «двійкову».
def fig_gain_ladder():
    W, H = 740, 410
    f = [text(W/2, 28, "Внутрішнє підсилення: три класи приймача", size=15, bold=True)]

    x0, x1 = 70, W - 40
    yb = H - 70
    f.append(arrow(x0, yb, x1, yb, color=MUTED, sw=1.6))
    f.append(text(x1, yb + 22, "зворотне зміщення →", size=11, color=MUTED, anchor="end"))
    f.append(arrow(x0, yb, x0, 70, color=MUTED, sw=1.6))
    f.append(text(x0 - 6, 78, "M (підсилення)", size=11, color=MUTED, anchor="start"))

    vbr = x0 + (x1 - x0) * 0.64
    f.append(line(vbr, 72, vbr, yb, color=POS, sw=1.4, dash="5 5"))
    f.append(text(vbr, 64, "напруга пробою Vbr", size=11, color=POS, bold=True))

    # PIN: M=1, плоско низько
    y_pin = yb - 24
    f.append(line(x0 + 10, y_pin, vbr - 110, y_pin, color=NEG, sw=2.6))
    f.append(text(x0 + 14, y_pin - 10, "PIN-фотодіод: M = 1", size=12, color=NEG, bold=True))
    f.append(text(x0 + 14, y_pin + 18, "без внутрішнього підсилення", size=10, color=MUTED))

    # APD: плавно росте до ~сотень, до Vbr
    pts = [(vbr - 150, yb - 40), (vbr - 95, yb - 70), (vbr - 45, yb - 120), (vbr - 8, yb - 178)]
    for a, b in zip(pts, pts[1:]):
        f.append(line(a[0], a[1], b[0], b[1], color="#8e44ad", sw=2.6))
    f.append(text(vbr - 168, yb - 168, "APD (лінійний):", size=12, color="#8e44ad", bold=True, anchor="start"))
    f.append(text(vbr - 168, yb - 150, "M ≈ 10…кілька×100", size=10, color="#8e44ad", anchor="start"))

    # SPAD: стрибок за Vbr на 10^5–10^6
    f.append(line(vbr + 4, yb - 178, vbr + 4, 96, color=POS, sw=3))
    f.append(circle(vbr + 4, 96, 5, fill=POS, stroke=POS, sw=1))
    f.append(fitbox(vbr + 20, 86, 210, 58,
                    "SPAD (Гейгер):\nM ≈ 10⁵…10⁶ — лавина не\nгасне сама, вихід двійковий",
                    size=11, color=INK, fill="#fdecea", stroke=POS, sw=1.6))

    b, w, h = textbox(W/2, H - 24,
                      "нижче Vbr — лінійне множення; вище — самопідтримна лавина: один фотон дає повний імпульс",
                      size=11, color=INK, fill=FILL, stroke=LINE)
    f.append(b)
    return render(os.path.join(OUT, "gain-ladder.svg"), W, H, *f)


# ── 8. Динамічний діапазон: крихта відлуння на п'єдесталі дня + засліплення ────
def fig_dynamic_range():
    import math
    W, H = 740, 380
    f = [text(W/2, 26, "Що бачить приймач: крихта відлуння на тлі дня", size=15, bold=True)]

    base = H - 70
    x0, x1 = 60, W - 40
    f.append(line(x0, base, x1, base, color=MUTED, sw=1.4))
    f.append(text(x1, base + 20, "час", size=11, color=MUTED, anchor="end"))
    f.append(arrow(x0, base, x0, 58, color=MUTED, sw=1.4))
    f.append(text(x0 - 6, 64, "струм приймача", size=11, color=MUTED, anchor="start"))

    # п'єдестал денного світла (постійна засвітка)
    ped = base - 150
    f.append(rect(x0 + 2, ped, x1 - x0 - 4, base - ped, fill="#fff3cd", stroke="#e0a800", sw=1.2, rx=2))
    f.append(text(x0 + 14, ped + 26, "постійний струм від сонця", size=11, color="#8a6d00", bold=True, anchor="start"))
    f.append(text(x0 + 14, ped + 44, "(засвітка часто в тисячі разів сильніша за відлуння)", size=10, color="#8a6d00", anchor="start"))

    # сильне відлуння від близької цілі (зашкалює)
    xn = x0 + 150
    f.append(rect(xn, 66, 26, base - 66, fill="#d6e0ff", stroke=NEG, sw=1.6, rx=2))
    f.append(text(xn + 13, 58, "близька ціль", size=10, color=NEG, bold=True, anchor="middle"))
    f.append(text(xn + 13, base + 18, "зашкал", size=10, color=POS, anchor="middle"))

    # шумова доріжка поверх п'єдесталу
    pr = []
    for i in range(64):
        xx = x0 + 4 + i * (x1 - x0 - 8) / 63
        yy = ped - 3 + 5 * math.sin(i * 1.7) * (0.5 + 0.5 * math.cos(i * 0.6))
        pr.append((xx, yy))
    for a, b in zip(pr, pr[1:]):
        f.append(line(a[0], a[1], b[0], b[1], color="#b07a00", sw=0.8))

    # жалюгідна крихта від далекої цілі — ледь над п'єдесталом
    xf = x0 + 380
    f.append(rect(xf, ped - 20, 22, 20, fill="#d6e0ff", stroke=NEG, sw=1.6, rx=2))
    f.append(text(xf + 11, ped - 28, "далека ціль", size=10, color=NEG, bold=True, anchor="middle"))
    f.append(arrow(xf + 80, ped - 10, xf + 24, ped - 10, color=INK, sw=1.4))
    f.append(text(xf + 86, ped - 6, "крихта врівень із шумом", size=10, color=INK, anchor="start"))

    b, w, h = textbox(W/2, H - 22,
                      "близька ціль топить приймач у зашкал, далека дає крихту врівень із шумом — обидва краї тисне один вузол",
                      size=11, color=INK, fill=FILL, stroke=LINE)
    f.append(b)
    return render(os.path.join(OUT, "dynamic-range.svg"), W, H, *f)


# ── 9. Мертвий час і afterpulsing у SPAD ─────────────────────────────────────
def fig_afterpulse():
    import math
    W, H = 740, 360
    f = [text(W/2, 26, "Життя SPAD у часі: лавина, гасіння, мертвий час", size=15, bold=True)]

    base = H - 96
    x0, x1 = 60, W - 40
    f.append(line(x0, base, x1, base, color=MUTED, sw=1.4))
    f.append(text(x1, base + 20, "час", size=11, color=MUTED, anchor="end"))

    def avalanche(xc, h, col=NEG):
        out = [line(xc, base, xc, base - h, color=col, sw=2.6)]
        prev = (xc, base - h)
        for k in range(1, 26):
            xx = xc + k * 2.4
            yy = base - h * math.exp(-k / 7.0)
            out.append(line(prev[0], prev[1], xx, yy, color=col, sw=2.0))
            prev = (xx, yy)
        return out, prev[0]

    # 1) корисний фотон
    seg, xend = avalanche(x0 + 40, 120)
    f += seg
    f.append(text(x0 + 40, base - 130, "фотон → лавина", size=11, color=NEG, bold=True, anchor="middle"))

    # мертвий час (hold-off)
    dx0, dx1 = xend, xend + 120
    f.append(rect(dx0, base - 30, dx1 - dx0, 30, fill="#ececec", stroke=MUTED, sw=1, rx=2))
    f.append(text((dx0 + dx1) / 2, base - 38, "мертвий час (hold-off)", size=10, color=MUTED, anchor="middle"))
    f.append(text((dx0 + dx1) / 2, base + 16, "осліплий: фотонів не бачить", size=9, color=MUTED, anchor="middle"))

    # 2) afterpulse — менший імпульс одразу після відновлення, БЕЗ фотона
    seg2, xend2 = avalanche(dx1 + 12, 70, col=POS)
    f += seg2
    f.append(text(dx1 + 12, base - 82, "afterpulse", size=11, color=POS, bold=True, anchor="middle"))
    f.append(text(dx1 + 12, base - 66, "(без фотона)", size=9, color=POS, anchor="middle"))

    # 3) темновий імпульс — ще пізніше, теж без світла
    seg3, _ = avalanche(dx1 + 250, 100, col="#8e44ad")
    f += seg3
    f.append(text(dx1 + 250, base - 112, "темновий імпульс", size=11, color="#8e44ad", bold=True, anchor="middle"))
    f.append(text(dx1 + 250, base - 96, "(тепло / тунелювання)", size=9, color="#8e44ad", anchor="middle"))

    b, w, h = textbox(W/2, H - 22,
                      "корисний фотон і два самозванці: afterpulse від застряглого носія й темновий імпульс від тепла",
                      size=11, color=INK, fill=FILL, stroke=LINE)
    f.append(b)
    return render(os.path.join(OUT, "afterpulse.svg"), W, H, *f)


if __name__ == "__main__":
    fig_scan_problem()
    fig_architectures()
    fig_tof_vs_fmcw()
    fig_chooser()
    fig_chirp_geometry()
    fig_triangle_doppler()
    fig_gain_ladder()
    fig_dynamic_range()
    fig_afterpulse()
    print("OK: 9 figs")
