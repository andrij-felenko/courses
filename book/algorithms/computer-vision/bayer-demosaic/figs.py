# -*- coding: utf-8 -*-
"""Фігури до теми «Демозаїка».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори фільтрів понад палітру svgkit (насичені, як на сенсорі)
R = "#cc2c20"      # червоний фільтр
G = "#1f9d4d"      # зелений фільтр
B = "#2457d6"      # синій фільтр (= NEG)
GRAY = "#9aa0a6"   # «лише яскравість», без кольору
PURPLE = "#7c3aed" # повний колір (R+G+B зведені)


def cell(x, y, s, color, label=None, lsize=12, lcolor="#ffffff"):
    """Кольорова клітинка фільтра з опційною літерою всередині."""
    out = rect(x, y, s, s, fill=color, stroke=BG, sw=1.4, rx=4)
    if label:
        out += text(x + s / 2, y + s / 2 + lsize * 0.36, label, size=lsize,
                    color=lcolor, bold=True)
    return out


# ── 1. Піксель сліпий до кольору → дамо йому скельце ──────────────────────────
# Ідея: сам піксель лічить усі фотони (лише яскравість, сірий); кольорове
# скельце згори пропускає тільки свою смугу — і піксель починає міряти колір.
def fig_colorblind():
    W, H = 720, 360
    f = [text(W / 2, 28, "Колір додає фільтр, не сам піксель", size=16, bold=True)]

    # ЛІВОРУЧ: без фільтра — усе світло, на виході лише яскравість (сіра)
    f.append(text(180, 70, "БЕЗ фільтра", size=13, color=MUTED, bold=True))
    for dx, c in ((-26, R), (0, G), (26, B)):
        f.append(arrow(180 + dx, 92, 180 + dx * 0.7, 132, color=c, sw=2.0))
    f.append(rect(140, 134, 80, 56, fill=GRAY, stroke=INK, sw=1.8, rx=4))
    f.append(text(180, 166, "усе світло", size=10.5, color="#ffffff", bold=True))
    f.append(rect(140, 206, 80, 40, fill=GRAY, stroke=INK, sw=1.6, rx=4))
    f.append(text(180, 224, "яскравість", size=10, color="#ffffff", bold=True))
    f.append(text(180, 239, "(колір ?)", size=9, color="#ffffff"))
    f.append(arrow(180, 192, 180, 204, color=INK, sw=1.6))

    # ПРАВОРУЧ: три пікселі, кожен зі своїм скельцем
    f.append(text(500, 70, "ЗІ скельцем", size=13, color=MUTED, bold=True))
    cols = ((400, R, "R", "червоне"), (500, G, "G", "зелене"), (600, B, "B", "синє"))
    for cx, c, lab, word in cols:
        # три промені падають, фільтр пропускає лише свій
        for dx, cc in ((-22, R), (0, G), (22, B)):
            faded = cc if cc == c else "#d7dbe0"
            f.append(line(cx + dx, 92, cx + dx * 0.6, 122, color=faded, sw=2.0,
                          dash=None if cc == c else "2,3"))
        f.append(rect(cx - 28, 122, 56, 16, fill=c, stroke=INK, sw=1.4, rx=3))   # скельце
        f.append(text(cx, 134, "скельце", size=9, color="#ffffff", bold=True))
        f.append(rect(cx - 26, 150, 52, 48, fill=GRAY, stroke=INK, sw=1.6, rx=4))  # піксель
        f.append(text(cx, 178, "піксель", size=9.5, color="#ffffff"))
        f.append(arrow(cx, 200, cx, 214, color=c, sw=1.8))
        f.append(rect(cx - 26, 216, 52, 30, fill=c, stroke=INK, sw=1.4, rx=4))
        f.append(text(cx, 235, lab, size=13, color="#ffffff", bold=True))

    f.append(text(W / 2, 300, "Без фільтра піксель ловить усе світло й знає лише яскравість.",
                  size=12, color=MUTED))
    f.append(text(W / 2, 320, "Кольорове скельце згори пропускає тільки свою смугу — і кожен піксель міряє СВІЙ колір.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "colorblind.svg"), W, H, *f)


# ── 2. Баєрівська мозаїка RGGB ───────────────────────────────────────────────
# Ідея: повторюваний квадрат R G / G B по всій матриці; зеленого вдвічі більше,
# бо око бере з нього найбільше різкості (яскравість).
def fig_bayer():
    W, H = 720, 430
    f = [text(W / 2, 28, "Баєрівська мозаїка: квадрат R G / G B по всій сітці", size=16, bold=True)]

    s = 34
    nx, ny = 8, 6
    gx = (W - nx * s) / 2
    gy = 56
    # патерн RGGB: парний рядок R,G,R,G…; непарний G,B,G,B…
    for r in range(ny):
        for c in range(nx):
            if r % 2 == 0:
                col = R if c % 2 == 0 else G
            else:
                col = G if c % 2 == 0 else B
            f.append(cell(gx + c * s, gy + r * s, s, col))

    # виділити один квадрат 2×2 рамкою
    f.append(rect(gx - 2, gy - 2, 2 * s + 4, 2 * s + 4, fill="none", stroke=INK, sw=2.6, rx=3))
    f.append(text(gx + s, gy + 2 * s + 18, "квадрат 2×2", size=10, color=INK, bold=True, anchor="middle"))

    # пропорції під сіткою — три рядки-смуги
    by = gy + ny * s + 30
    f.append(text(W / 2, by, "Скільки кожного фільтра на сенсорі:", size=12, bold=True))
    bars = ((G, "зелений", 50, 220), (R, "червоний", 25, 110), (B, "синій", 25, 110))
    rowy = by + 14
    for col, lab, pct, wlen in bars:
        f.append(rect(180, rowy, wlen, 20, fill=col, stroke=INK, sw=1.2, rx=3))
        f.append(text(180 + wlen + 8, rowy + 14, "%s — %d%%" % (lab, pct), size=11,
                      color=INK, anchor="start"))
        rowy += 26

    f.append(text(W / 2, H - 26, "Зеленого вдвічі більше (50%): з нього око бере найбільше різкості — яскравість.",
                  size=11.5, color=MUTED))
    f.append(text(W / 2, H - 10, "Червоного й синього по 25% — вони несуть тонший відтінок (колірність), до якого око м'якше.",
                  size=11.5, color=MUTED))
    render(os.path.join(IMG, "bayer-mosaic.svg"), W, H, *f)


# ── 3. Демозаїка: одна складова виміряна, дві — з сусідів ─────────────────────
# Ідея: червоний піксель знає лише R; зелене й синє інтерполюють із сусідів,
# щоб у кожній точці став повний R+G+B.
def fig_demosaic():
    W, H = 720, 360
    f = [text(W / 2, 28, "Демозаїка: одну складову виміряно, дві — з сусідів", size=16, bold=True)]

    s = 46
    gx, gy = 150, 70
    # сітка 3×3 з центром-червоним: рядки R,G,R / G,B,G / R,G,R
    grid = [[R, G, R], [G, B, G], [R, G, R]]
    for r in range(3):
        for c in range(3):
            f.append(cell(gx + c * s, gy + r * s, s, grid[r][c]))
    cx0 = gx + s + s / 2
    cy0 = gy + s + s / 2
    # рамка центру + підпис «лише R»
    f.append(rect(gx + s - 2, gy + s - 2, s + 4, s + 4, fill="none", stroke=INK, sw=2.8, rx=4))
    f.append(text(cx0, gy - 10, "цей піксель: лише R", size=11, color=R, bold=True))

    # стрілки від сусідів-зелених і сусідів-синіх до центру
    for dx, dy, col in ((0, -s, G), (-s, 0, G), (0, s, G), (s, 0, G)):
        f.append(line(cx0 + dx, cy0 + dy, cx0 + dx * 0.32, cy0 + dy * 0.32,
                      color=col, sw=1.8, dash="3,2"))
    for dx, dy in ((-s, -s), (s, -s), (-s, s), (s, s)):
        f.append(line(cx0 + dx, cy0 + dy, cx0 + dx * 0.32, cy0 + dy * 0.32,
                      color=B, sw=1.8, dash="3,2"))
    f.append(text(cx0, gy + 3 * s + 20, "позичає G і B у сусідів", size=10, color=MUTED))

    # стрілка «демозаїка» до картки повного кольору
    ax = gx + 3 * s + 12
    f.append(arrow(ax, cy0, ax + 56, cy0, color=INK, sw=2.0))
    f.append(text(ax + 28, cy0 - 10, "демозаїка", size=9.5, color=MUTED))
    bx = ax + 64
    f.append(rect(bx, cy0 - 52, 150, 104, fill=PURPLE, stroke=INK, sw=1.8, rx=6))
    f.append(text(bx + 75, cy0 - 30, "повний колір", size=12, color="#ffffff", bold=True))
    f.append(text(bx + 16, cy0 - 6, "R — виміряно", size=10.5, color="#ffffff", anchor="start"))
    f.append(text(bx + 16, cy0 + 14, "G — вгадано", size=10.5, color="#ffffff", anchor="start"))
    f.append(text(bx + 16, cy0 + 34, "B — вгадано", size=10.5, color="#ffffff", anchor="start"))

    f.append(text(W / 2, H - 26, "У сирій мозаїці кожна точка має лише одну складову; демозаїка інтерполює дві відсутні з сусідів.",
                  size=12, color=MUTED))
    f.append(text(W / 2, H - 10, "На виході — повноколірний кадр, де в кожному пікселі є R, G і B. Але дві з трьох — обчислена гадка.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "demosaic.svg"), W, H, *f)


# ── 4. Ціна: артефакти на тонких деталях + що таке RAW ───────────────────────
# Ідея: на чітких смужках інтерполяція схибить → несправжній колір, муар;
# RAW — це сира мозаїка до демозаїки (найбільше «чесних» даних).
def fig_artifacts():
    W, H = 720, 360
    f = [text(W / 2, 28, "Ціна вгадування: артефакти й нижча кольорова роздільність", size=16, bold=True)]

    # ЛІВОРУЧ: справжні чорно-білі смужки
    f.append(text(180, 64, "справжня деталь", size=12, color=INK, bold=True))
    f.append(text(180, 80, "(тонкі смужки)", size=10, color=MUTED))
    bx, by, bw, bh = 110, 92, 18, 110
    for i in range(8):
        col = INK if i % 2 == 0 else "#f0f1f3"
        f.append(rect(bx + i * bw, by, bw, bh, fill=col, stroke="none", sw=0))
    f.append(rect(bx, by, 8 * bw, bh, fill="none", stroke=INK, sw=1.4))

    # стрілка
    f.append(arrow(bx + 8 * bw + 8, by + bh / 2, bx + 8 * bw + 48, by + bh / 2, color=INK, sw=2.0))
    f.append(text(bx + 8 * bw + 28, by + bh / 2 - 10, "демозаїка", size=9.5, color=MUTED))

    # ПРАВОРУЧ: ті самі смужки беруться хибним кольором (муар / «застібка»)
    f.append(text(500, 64, "після демозаїки", size=12, color=INK, bold=True))
    f.append(text(500, 80, "(несправжній колір, муар)", size=10, color=MUTED))
    fx = bx + 8 * bw + 56
    fake = [INK, "#f0f1f3", R, "#f0f1f3", G, "#f0f1f3", B, "#f0f1f3"]
    for i in range(8):
        f.append(rect(fx + i * bw, by, bw, bh, fill=fake[i], stroke="none", sw=0))
    f.append(rect(fx, by, 8 * bw, bh, fill="none", stroke=INK, sw=1.4))
    f.append(text(fx + 4 * bw, by + bh + 18, "колір, якого в сцені не було", size=10,
                  color=POS, bold=True))

    # рамка про RAW (явні рядки, щоб шрифт лишився читабельним)
    ry = 248
    box = fitbox(80, ry, W - 160, 60,
                 "RAW — сира мозаїка ДО демозаїки: одна складова на піксель, найбільше «чесних» даних\n"
                 "(кадр ще треба «проявити»). JPEG із камери — уже ПІСЛЯ демозаїки й обробки.",
                 size=12, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    f.append(text(W / 2, H - 16, "«12 МП» = 6 млн зелених точок + по 3 млн червоних і синіх; решту кольору домальовано.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "artifacts.svg"), W, H, *f)


# ── 5. Решітки дискретизації RGGB і межа Найквіста (math-вставка) ─────────────
# Ідея: зелене стоїть квінконсом (вдвічі густіше) → ширша зона Найквіста;
# червоне й синє — рідка квадратна решітка → вузька зона, раніший aliasing.
def fig_sampling_lattice():
    W, H = 720, 470
    f = [text(W / 2, 26, "Решітки дискретизації: зелене густіше → ширша зона Найквіста",
              size=16, bold=True)]

    # ── ЛІВОРУЧ: реальні позиції відліків (квінконс G vs квадрат R) ──
    f.append(text(190, 56, "де стоять відліки (крок пікселя d)", size=12, color=INK, bold=True))
    s = 26
    gx, gy = 70, 70
    n = 8
    for r in range(n):
        for c in range(n):
            cx = gx + c * s
            cy = gy + r * s
            # світла підкладка-сітка пікселів
            f.append(circle(cx, cy, 2.2, fill="#d7dbe0", stroke="none", sw=0))
            if (r + c) % 2 == 0:                      # зелені — квінконс (шахівниця)
                f.append(circle(cx, cy, 5.2, fill=G, stroke=BG, sw=1.0))
            elif r % 2 == 1 and c % 2 == 1:           # сині
                f.append(circle(cx, cy, 5.2, fill=B, stroke=BG, sw=1.0))
            else:                                      # червоні
                f.append(circle(cx, cy, 5.2, fill=R, stroke=BG, sw=1.0))
    yb = gy + n * s + 6
    f.append(text(gx + n * s / 2 - 13, yb + 12,
                  "зелене — по діагоналі (квінконс), удвічі густіше за R чи B",
                  size=10, color=MUTED))

    # ── ПРАВОРУЧ: зони Найквіста у частотній площині (fx,fy) ──
    f.append(text(515, 56, "зона Найквіста (частоти fx,fy)", size=12, color=INK, bold=True))
    ox, oy = 515, 210                                  # центр осей
    L = 120
    f.append(line(ox - L, oy, ox + L, oy, color=INK, sw=1.4))
    f.append(line(ox, oy - L, ox, oy + L, color=INK, sw=1.4))
    f.append(text(ox + L + 8, oy + 4, "fx", size=11, color=INK, anchor="start"))
    f.append(text(ox + 6, oy - L - 4, "fy", size=11, color=INK))
    # квадрат R/B: межа ±1/(2d)  (рідка решітка з кроком 2d → менша зона)
    q = 56
    f.append(rect(ox - q, oy - q, 2 * q, 2 * q, fill="none", stroke=R, sw=2.2, rx=2))
    f.append(text(ox + q - 2, oy - q - 6, "R, B: ±1/(4d)", size=10, color=R, anchor="end"))
    # ромб зеленого: квінконс дає більшу (повернену) зону Найквіста
    d = 96
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
             'fill="none" stroke="%s" stroke-width="2.4"/>'
             % (ox, oy - d, ox + d, oy, ox, oy + d, ox - d, oy, G))
    f.append(text(ox, oy - d - 8, "G (квінконс): ширша", size=10, color=G, bold=True))

    # підсумкова рамка
    box = fitbox(70, 396, W - 140, 56,
                 "Що рідша решітка каналу, то вужча його зона Найквіста — і то нижча частота, на якій\n"
                 "деталь уже не відрізнити від хибної (aliasing). У зеленого зона ширша, тож муар у ньому пізніший.",
                 size=12, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "sampling-lattice.svg"), W, H, *f)


# ── 6. Спектр RGGB: накладання копій → муар без AA-фільтра (-d, фіг. b) ───────
# Ідея: дискретизація тиражує спектр сцени копіями на вузлах решітки; де копії
# заходять одна в одну, високі частоти «складаються» в низькі — це муар.
def fig_aliasing_spectrum():
    W, H = 720, 430
    f = [text(W / 2, 26, "Чому муар неминучий: копії спектра накладаються", size=16, bold=True)]

    def band(cx, title, col, rep, baserad, reprad):
        out = [text(cx, 70, title, size=12, color=col, bold=True)]
        oy = 150
        # осі
        out.append(line(cx - 78, oy, cx + 78, oy, color=INK, sw=1.1))
        out.append(line(cx, oy - 70, cx, oy + 12, color=INK, sw=1.1))
        # центральна копія спектра сцени (базова смуга)
        out.append(circle(cx, oy - 22, baserad, fill=col, stroke="none", sw=0))
        # копії-репліки на вузлах решітки (праворуч/ліворуч); що рідша решітка — то ближче копії
        for k in (-1, 1):
            ccx = cx + k * rep
            faded = col.replace("#", "#")
            out.append(circle(ccx, oy - 22, reprad, fill=col, stroke="none", sw=0))
            out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.30" stroke="none"/>'
                       % (ccx, oy - 22, reprad, col))
        out.append(text(cx, oy + 28, "копії на кроці решітки", size=9.5, color=MUTED))
        return out

    # зелене: копії далеко (густа решітка) — майже не перекриваються
    f += band(170, "зелене (густа решітка)", G, True, 22, 48)
    f.append(text(170, 196, "копії далеко → перекриття мале", size=10, color=POS, bold=True))
    # червоне/синє: копії близько (рідка решітка) — заходять у базову смугу
    f += band(420, "червоне / синє (рідка)", R, True, 22, 30)
    f.append(text(420, 196, "копії близько → перекриття є", size=10, color=POS, bold=True))
    # зона перекриття праворуч позначена
    f.append(text(610, 70, "перекриття = aliasing", size=12, color=INK, bold=True))
    oy = 150
    f.append(circle(600, oy - 22, 26, fill=B, stroke="none", sw=0))
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.35" stroke="none"/>'
             % (628, oy - 22, 26, R))
    f.append(circle(628, oy - 22, 26, fill="none", stroke=INK, sw=1.0))
    f.append(text(614, oy + 28, "тут частоти", size=9.5, color=MUTED))
    f.append(text(614, oy + 42, "складаються", size=9.5, color=MUTED))

    box = fitbox(70, 250, W - 140, 92,
                 "Дискретизація тиражує спектр сцени копіями на вузлах решітки каналу. Де копія сусіда\n"
                 "залазить у базову смугу, висока частота сцени стає НЕВІДРІЗНЕННОЮ від низької —\n"
                 "у кадрі вона проступає хвилями (муар). Рідша решітка R/B ставить копії ближче, тож\n"
                 "складаються вони раніше. AA-фільтр (легке оптичне розмиття) зрізає верхні частоти ще\n"
                 "до сенсора — щоб накладатися вже не було чому.",
                 size=11.5, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "aliasing-spectrum.svg"), W, H, *f)


# ── 7. Градієнтно-коригована інтерполяція: вибір напряму (-d, фіг. a) ─────────
# Ідея: рахуємо горизонтальний і вертикальний градієнт; інтерполюємо вздовж
# меншого (вздовж краю), а не впоперек — звідси вага напряму.
def fig_gradient_weight():
    W, H = 720, 430
    f = [text(W / 2, 26, "Градієнтно-коригована інтерполяція: уздовж краю, не впоперек",
              size=16, bold=True)]

    # центральний піксель і чотири сусіди-хрест
    cx, cy = 200, 150
    s = 52
    f.append(circle(cx, cy, 16, fill=GRAY, stroke=INK, sw=1.6))
    f.append(text(cx, cy + 4, "?", size=15, color="#ffffff", bold=True))
    nb = ((0, -s, "↑"), (0, s, "↓"), (-s, 0, "←"), (s, 0, "→"))
    for dx, dy, _ in nb:
        f.append(circle(cx + dx, cy + dy, 13, fill=G, stroke=INK, sw=1.2))
    # горизонтальний градієнт ΔH (ліво-право), вертикальний ΔV (верх-низ)
    f.append(line(cx - s, cy, cx + s, cy, color=R, sw=2.0, dash="4,3"))
    f.append(text(cx, cy - s - 18, "ΔV = |верх − низ|", size=10.5, color=NEG, bold=True))
    f.append(line(cx, cy - s, cx, cy + s, color=NEG, sw=2.0, dash="4,3"))
    f.append(text(cx, cy + s + 28, "ΔH = |ліво − право|", size=10.5, color=R, bold=True))

    # блок-схема рішення праворуч
    bx = 430
    b1 = fitbox(bx, 70, 230, 40, "порахувати ΔH і ΔV", size=12, fill=FILL, stroke=INK, color=INK, bold=True)
    f.append(b1)
    f.append(arrow(bx + 115, 110, bx + 115, 134, color=INK, sw=1.8))
    # ромб умови
    dy0 = 160
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (bx + 115, dy0 - 26, bx + 210, dy0, bx + 115, dy0 + 26, bx + 20, dy0, FILL, INK))
    f.append(text(bx + 115, dy0 + 4, "ΔH < ΔV ?", size=11.5, color=INK, bold=True))
    # дві гілки
    f.append(arrow(bx + 30, dy0 + 14, bx - 20, dy0 + 52, color=INK, sw=1.6))
    f.append(text(bx - 28, dy0 + 40, "так", size=10, color=POS, anchor="end", bold=True))
    f.append(arrow(bx + 200, dy0 + 14, bx + 250, dy0 + 52, color=INK, sw=1.6))
    f.append(text(bx + 256, dy0 + 40, "ні", size=10, color=POS, anchor="start", bold=True))
    yb = dy0 + 56
    lb = fitbox(bx - 120, yb, 175, 56,
                "край горизонтальний:\nбрати ліво+право\n(вага → горизонталі)",
                size=10.5, fill="#eaf0fd", stroke=NEG, color=INK)
    f.append(lb)
    rb = fitbox(bx + 80, yb, 175, 56,
                "край вертикальний:\nбрати верх+низ\n(вага → вертикалі)",
                size=10.5, fill="#fdecea", stroke=R, color=INK)
    f.append(rb)

    box = fitbox(70, 332, W - 140, 64,
                 "Замість сліпого середнього чотирьох сусідів зважуємо їх ОБЕРНЕНО до градієнта в кожному\n"
                 "напрямі: де перепад малий (уздовж краю) — вага більша, де великий (упоперек) — менша.\n"
                 "Так інтерполяція не «перестрибує» різку межу, і «застібка» на контурах майже зникає.",
                 size=12, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "gradient-weight.svg"), W, H, *f)


# ── 8. AHD: два буфери (H і V) + вибір за гомогенністю в Lab (-d) ─────────────
# Ідея: інтерполюємо ВЕСЬ кадр двічі — по горизонталі й по вертикалі; потім у
# кожному пікселі лишаємо той варіант, чиє около однорідніше в Lab.
def fig_ahd_hv_select():
    W, H = 720, 410
    f = [text(W / 2, 26, "AHD: два буфери, вибір попіксельно за однорідністю в Lab",
              size=16, bold=True)]

    # сирий кадр ліворуч
    raw = fitbox(60, 96, 120, 60, "сира\nмозаїка\nRGGB", size=12, fill=FILL, stroke=INK, color=INK, bold=True)
    f.append(raw)
    # дві гілки інтерполяції
    f.append(arrow(182, 112, 232, 84, color=INK, sw=1.8))
    f.append(arrow(182, 140, 232, 168, color=INK, sw=1.8))
    hbuf = fitbox(234, 60, 158, 48, "буфер H\n(лише горизонталь)", size=11,
                  fill="#fdecea", stroke=R, color=INK, bold=True)
    vbuf = fitbox(234, 150, 158, 48, "буфер V\n(лише вертикаль)", size=11,
                  fill="#eaf0fd", stroke=NEG, color=INK, bold=True)
    f.append(hbuf)
    f.append(vbuf)
    # переклад у Lab + метрика гомогенності
    f.append(arrow(394, 84, 436, 110, color=INK, sw=1.6))
    f.append(arrow(394, 174, 436, 148, color=INK, sw=1.6))
    lab = fitbox(438, 100, 170, 58,
                 "перевести в Lab,\nзміряти однорідність\nоколу для H і для V",
                 size=10.5, fill=FILL, stroke=INK, color=INK)
    f.append(lab)
    # вибір
    f.append(arrow(610, 128, 638, 128, color=INK, sw=1.8))
    pick = fitbox(600, 170, 116, 54, "лишити\nоднорідніший", size=11,
                  fill="#e8f6ee", stroke=FIELD, color=INK, bold=True)
    f.append(pick)
    f.append(text(658, 150, "піксель", size=9.5, color=MUTED))

    box = fitbox(60, 250, W - 120, 92,
                 "Замість одного компромісного напряму AHD інтерполює кадр ДВІЧІ — окремо по горизонталі\n"
                 "(буфер H) і по вертикалі (буфер V). Тоді для кожного пікселя дивиться, у якому з двох\n"
                 "варіантів сусідство однорідніше за кольором у перцептивному просторі Lab: різкий край,\n"
                 "перетятий упоперек, дає рвані стрибки кольору (низька однорідність), а вздовж — гладко.\n"
                 "Лишаємо локально гладший варіант. Звідси менше і «застібки», і хибного кольору на діагоналях.",
                 size=11.5, fill=FILL, stroke=MUTED, color=INK)
    f.append(box)
    render(os.path.join(IMG, "ahd-hv-select.svg"), W, H, *f)


if __name__ == "__main__":
    fig_colorblind()
    fig_bayer()
    fig_demosaic()
    fig_artifacts()
    fig_sampling_lattice()
    fig_aliasing_spectrum()
    fig_gradient_weight()
    fig_ahd_hv_select()
    print("OK: 8 SVG у", IMG)
