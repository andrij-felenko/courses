# -*- coding: utf-8 -*-
"""Фігури до статті «R-2R лесенка» (book/electronics/analog/r2r-ladder).
Три фігури:
  ladder.svg   — топологія: горизонталь із R, до кожного вузла 2R-«щабель» на ключ (Vref або земля)
  collapse.svg — ЧОМУ працює: рекурсивне згортання 2R∥2R = R, отже опір завжди R
  weights.svg  — суперпозиція: кожен біт додає рівно вдвічі менший внесок (двійкові ваги)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def res_h(x, y, w, label, lab_size=12, lab_dy=-12):
    """Горизонтальний резистор-зигзаг із підписом зверху."""
    n = 6
    seg = w / (n + 1.0)
    pts = [(x, y)]
    cx = x + seg
    up = True
    for i in range(n):
        pts.append((cx, y - 7 if up else y + 7))
        up = not up
        cx += seg
    pts.append((x + w, y))
    d = " ".join(("M%.1f %.1f" % p) if i == 0 else ("L%.1f %.1f" % p)
                 for i, p in enumerate(pts))
    out = '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, INK)
    if label:
        out += text(x + w / 2, y + lab_dy, label, size=lab_size, color=INK, bold=True)
    return out


def res_v(x, y, h, label, lab_side="right"):
    """Вертикальний резистор-зигзаг із підписом збоку."""
    n = 6
    seg = h / (n + 1.0)
    pts = [(x, y)]
    cy = y + seg
    right = True
    for i in range(n):
        pts.append((x + 7 if right else x - 7, cy))
        right = not right
        cy += seg
    pts.append((x, y + h))
    d = " ".join(("M%.1f %.1f" % p) if i == 0 else ("L%.1f %.1f" % p)
                 for i, p in enumerate(pts))
    out = '<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, INK)
    if label:
        lx = x + 15 if lab_side == "right" else x - 15
        an = "start" if lab_side == "right" else "end"
        out += text(lx, y + h / 2 + 4, label, size=12, color=INK, anchor=an, bold=True)
    return out


def gnd(cx, y):
    return (line(cx, y, cx, y + 6, color=INK, sw=1.6) +
            line(cx - 10, y + 6, cx + 10, y + 6, color=INK, sw=2.2) +
            line(cx - 6, y + 10, cx + 6, y + 10, color=INK, sw=1.8) +
            line(cx - 2, y + 14, cx + 2, y + 14, color=INK, sw=1.6))


def dot(cx, cy, r=3.2):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, INK)


def sw_bit(cx, y_top, label, state):
    """Перемикач біта: спільний вивід зверху (до 2R), кидається на Vref або землю.
    state=1 → до Vref (червоний), state=0 → до землі (синій)."""
    out = []
    # точка перемикача
    out.append(dot(cx, y_top))
    if state == 1:
        out.append(line(cx, y_top, cx + 14, y_top + 20, color=POS, sw=2.4))   # до Vref
        out.append(line(cx + 14, y_top + 20, cx + 14, y_top + 34, color=POS, sw=1.8))
        out.append(text(cx + 14, y_top + 48, "Vref", size=10, color=POS, bold=True))
        out.append(line(cx - 14, y_top + 20, cx - 14, y_top + 34, color=MUTED, sw=1.2, dash="3,3"))
        out.append(gnd(cx - 14, y_top + 34))
    else:
        out.append(line(cx, y_top, cx - 14, y_top + 20, color=NEG, sw=2.4))    # до землі
        out.append(line(cx - 14, y_top + 20, cx - 14, y_top + 34, color=NEG, sw=1.8))
        out.append(gnd(cx - 14, y_top + 34))
        out.append(line(cx + 14, y_top + 20, cx + 14, y_top + 34, color=MUTED, sw=1.2, dash="3,3"))
        out.append(text(cx + 14, y_top + 48, "Vref", size=10, color=MUTED))
    out.append(text(cx, y_top - 8, label, size=11, color=INK, bold=True))
    return "".join(out)


# ── Фігура 1: топологія лесенки ─────────────────────────────────────────────
def fig_ladder():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 28, "Лесенка R-2R: дві номінали, на біт — один «щабель» 2R", size=15, bold=True))

    y = 130                      # горизонтальна шина
    x0 = 90
    step = 130
    nbits = 4
    bits = [1, 0, 1, 1]          # приклад коду 1011
    labels = ["b3 (старший)", "b2", "b1", "b0 (молодший)"]
    nodes = [x0 + i * step for i in range(nbits)]

    # лівий «термінатор» 2R на землю
    f.append(line(x0 - 55, y, x0, y, color=INK, sw=1.8))
    f.append(res_v(x0 - 55, y, 70, "2R", lab_side="left"))
    f.append(gnd(x0 - 55, y + 70))
    f.append(text(x0 - 55, y - 18, "кінцевий", size=10, color=MUTED))

    # горизонтальні R між вузлами
    for i in range(nbits - 1):
        f.append(res_h(nodes[i], y, step, "R"))

    # вихідний вузол праворуч (старший біт)
    xout = nodes[-1]
    f.append(line(xout, y, xout + 70, y, color=INK, sw=1.8))
    f.append(dot(xout + 70, y))
    f.append(text(xout + 78, y - 8, "Vout", size=13, color=FIELD, anchor="start", bold=True))
    f.append(text(xout + 78, y + 12, "(до буфера)", size=10, color=MUTED, anchor="start"))

    # вертикальні 2R-щаблі + ключі
    for i in range(nbits):
        nx = nodes[i]
        f.append(dot(nx, y))
        f.append(res_v(nx, y, 60, "2R"))
        f.append(sw_bit(nx, y + 60, labels[i], bits[i]))

    # підпис під фігурою-логіка
    note = ("Між сусідніми вузлами — горизонтальний R; від кожного вузла вниз — 2R на ключ біта. "
            "Праворуч (старший біт) знімаємо Vout, ліворуч лесенку замикає кінцевий 2R на землю. "
            "Усього два номінали — R і 2R.")
    f.append(fitbox(40, 360, W - 80, 52, note, size=12, fill="#f8fafc", stroke=MUTED))
    return render(os.path.join(IMG, 'ladder.svg'), W, H, *f)


# ── Фігура 2: рекурсивне згортання ──────────────────────────────────────────
def two_r_to_gnd(cx, y, label, lab_side="left"):
    """Вертикальний 2R від вузла (cx,y) до землі."""
    return res_v(cx, y, 58, label, lab_side=lab_side) + gnd(cx, y + 58)


def fig_collapse():
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 28, "Чому опір лесенки завжди R: 2R ∥ 2R = R, і так щабель за щаблем", size=15, bold=True))

    ytop = 110          # рівень шини в кожному кадрі
    cap_y = 78          # підпис кадру

    # ── Кадр 1: найдальший кінець — два 2R паралельно ──
    f.append(text(135, cap_y, "крок 1: кінець лесенки", size=12, color=MUTED, bold=True))
    f.append(dot(135, ytop))
    f.append(two_r_to_gnd(105, ytop, "2R", lab_side="left"))
    f.append(two_r_to_gnd(165, ytop, "2R", lab_side="right"))
    f.append(line(105, ytop, 165, ytop, color=INK, sw=1.8))
    bx, _, _ = textbox(135, 240, "2R ∥ 2R = R", size=13, color=FIELD, bold=True, fill="#eafaf1", stroke=FIELD)
    f.append(bx)
    f.append(mtext(135, 278, "кінцевий щабель і сусідній\n2R стоять паралельно", size=10, color=MUTED))
    f.append(arrow(228, 150, 268, 150, color=INK, sw=2))

    # ── Кадр 2: цей R + горизонтальний R = 2R, знову паралельно 2R ──
    f.append(text(400, cap_y, "крок 2: наступний вузол", size=12, color=MUTED, bold=True))
    nx = 430
    f.append(dot(nx, ytop))
    # горизонтальний R, що веде від попереднього (згорнутого) вузла
    f.append(res_h(nx - 90, ytop, 90, "R"))
    f.append(line(nx - 90, ytop, nx - 90, ytop + 14, color=INK, sw=1.4, dash="3,3"))
    f.append(mtext(nx - 90, ytop + 30, "сюди вже\nзгорнуто R", size=9, color=MUTED))
    # 2R-щабель цього вузла
    f.append(two_r_to_gnd(nx, ytop, "2R", lab_side="right"))
    bx2, _, _ = textbox(395, 240, "(R+R) ∥ 2R = R", size=13, color=FIELD, bold=True, fill="#eafaf1", stroke=FIELD)
    f.append(bx2)
    f.append(mtext(395, 278, "R згортки + R лінії = 2R,\nі знову паралель із 2R", size=10, color=MUTED))
    f.append(arrow(548, 150, 588, 150, color=INK, sw=2))

    # ── Кадр 3: висновок ──
    f.append(text(650, cap_y, "висновок", size=12, color=MUTED, bold=True))
    f.append(fitbox(600, 100, 100, 86,
                    "З будь-якого\nвузла вглиб —\nзавжди рівно R",
                    size=12, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))
    f.append(mtext(650, 232, "тому Rвих = R\nі НЕ залежить\nвід коду", size=11, color=INK, bold=True))

    note = ("Лесенка самоподібна: 2R ∥ 2R = R; цей R плюс горизонтальний R = 2R, який знову паралелиться "
            "з черговим 2R — і знову R. Картина згортається сама в себе, тож вихідний опір дорівнює R за "
            "будь-якого числа біт.")
    f.append(fitbox(40, 338, W - 80, 46, note, size=12, fill="#f8fafc", stroke=MUTED))
    return render(os.path.join(IMG, 'collapse.svg'), W, H, *f)


# ── Фігура 3: двійкові ваги (суперпозиція) ──────────────────────────────────
def fig_weights():
    W, H = 700, 380
    f = []
    f.append(text(W / 2, 28, "Внесок кожного біта вдвічі менший за сусіда — це і є двійкові ваги", size=15, bold=True))

    base_y = 300
    x0 = 110
    bw = 90
    gap = 40
    # 4 біти: внесок старшого = Vref/2, далі /4, /8, /16
    weights = ["Vref/2", "Vref/4", "Vref/8", "Vref/16"]
    heights = [220, 110, 55, 27]
    labels = ["b3", "b2", "b1", "b0"]
    vals = ["×8", "×4", "×2", "×1"]
    for i in range(4):
        bx = x0 + i * (bw + gap)
        h = heights[i]
        f.append(rect(bx, base_y - h, bw, h, fill="#eaf0fd" if i % 2 else "#fdecea",
                      stroke=NEG if i % 2 else POS, sw=1.6, rx=4))
        f.append(text(bx + bw / 2, base_y - h - 10, weights[i], size=12, color=INK, bold=True))
        f.append(text(bx + bw / 2, base_y + 18, labels[i], size=12, color=INK, bold=True))
        f.append(text(bx + bw / 2, base_y + 34, vals[i], size=11, color=MUTED))
        if i < 3:
            f.append(text(bx + bw + gap / 2, base_y - heights[i + 1] - 4, "½", size=14, color=FIELD, bold=True))

    f.append(line(x0 - 20, base_y, x0 + 4 * (bw + gap) - gap + 20, base_y, color=INK, sw=2))

    note = ("Один увімкнений біт дає на вихід рівно свою «вагу»: старший — Vref/2, далі Vref/4, Vref/8… "
            "щоразу вдвічі менше. Кола лінійні, тож повний вихід — сума ввімкнених ваг: Vout = Vref · код / 2ᴺ.")
    f.append(fitbox(40, 318, W - 80, 46, note, size=12, fill="#f8fafc", stroke=MUTED))
    return render(os.path.join(IMG, 'weights.svg'), W, H, *f)


# ── Фігура 4: рекурсія опору (для вставки math-ladder-thevenin) ──────────────
def fig_recursion():
    """Індуктивний крок: з вузла k углиб видно R; через горизонтальний R це 2R,
    у вузлі k+1 паралель із 2R знову дає R. Інваріант R відтворює себе."""
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 28, "Рекурсія опору: інваріант R відтворює сам себе щаблем за щаблем", size=15, bold=True))

    ytop = 120

    # ── Лівий блок: «з вузла k видно R» (база/гіпотеза) ──
    f.append(text(120, 78, "вузол k: видно R", size=12, color=MUTED, bold=True))
    f.append(dot(120, ytop))
    f.append(res_v(120, ytop, 70, "R", lab_side="left"))
    f.append(gnd(120, ytop + 70))
    f.append(mtext(120, ytop + 100, "уся внутрішня частина\nз бітами на землі = R", size=10, color=MUTED))
    f.append(arrow(186, ytop, 250, ytop, color=INK, sw=2))

    # ── Середній блок: + горизонтальний R = 2R ──
    nx = 350
    f.append(text(nx, 78, "+ горизонтальний R = 2R", size=12, color=MUTED, bold=True))
    f.append(res_h(nx - 90, ytop, 90, "R"))
    f.append(dot(nx, ytop))
    bx, _, _ = textbox(nx, ytop + 70, "R + R = 2R", size=13, color=FIELD, bold=True, fill="#eafaf1", stroke=FIELD)
    f.append(bx)
    f.append(arrow(nx + 60, ytop, nx + 124, ytop, color=INK, sw=2))

    # ── Правий блок: у вузлі k+1 паралель із 2R → знову R ──
    rx = nx + 200
    f.append(text(rx, 78, "вузол k+1: 2R ∥ 2R = R", size=12, color=MUTED, bold=True))
    f.append(dot(rx, ytop))
    f.append(res_v(rx, ytop, 70, "2R", lab_side="right"))
    f.append(gnd(rx, ytop + 70))
    # «гілка 2R» зліва (накопичена 2R) як підпис
    f.append(line(rx - 36, ytop, rx, ytop, color=INK, sw=1.6, dash="4,3"))
    f.append(text(rx - 36, ytop - 8, "2R", size=11, color=MUTED, anchor="end"))
    f.append(fitbox(rx - 52, ytop + 96, 130, 40, "знову рівно R", size=12,
                    fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))

    note = ("Гіпотеза: з вузла k углиб драбини видно R. Через горизонтальний R це стає 2R, а у вузлі k+1 "
            "паралель із вертикальним 2R знову дає рівно R. Інваріант відтворює себе, тож із будь-якого "
            "вузла видно R, а вихідний опір лесенки дорівнює R незалежно від коду.")
    f.append(fitbox(40, 300, W - 80, 46, note, size=12, fill="#f8fafc", stroke=MUTED))
    return render(os.path.join(IMG, 'recursion.svg'), W, H, *f)


# ── Фігура 5: часова лінія появи R-2R (для вставки hist-gordon-epsco) ─────────
def fig_history():
    """Ланцюжок ланок: PCM-ідея 1937 → мережа Сміта 1953 → Datrac 1954 →
    патент 1955/1963. Показує, що R-2R склали кілька внесків, не один."""
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 28, "Як складалися ланки R-2R: від ідеї до робочої машини", size=15, bold=True))

    axis_y = 150
    x0, x1 = 60, W - 60
    f.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=2))
    f.append(arrow(x1 - 30, axis_y, x1, axis_y, color=MUTED, sw=2))

    # 4 віхи: (x, рік, заголовок, рядки-під, колір, підпис зверху чи знизу)
    miles = [
        (140, "1937", "PCM",      "ідея кодувати\nголос числами\n(Алек Рівз)",        MUTED, "up"),
        (310, "1953", "мережа",   "опис і перевага\nдрабинної R-2R\n(Б. Д. Сміт)",     FIELD, "down"),
        (480, "1954", "Datrac",   "перша робоча\nструмова R/2R,\nоцифрував звук\n(EPSCO)", POS, "up"),
        (650, "1955→63", "патент", "пристрій із R/2R\nприоритет 1955,\nвидано 1963\n(Гордон,\nТаламбірас)", INK, "down"),
    ]
    for x, yr, title, sub, col, side in miles:
        f.append(dot(x, axis_y, r=5))
        # рік — на осі
        ybadge = axis_y - 22 if side == "up" else axis_y + 30
        f.append(text(x, ybadge, yr, size=13, color=col, bold=True))
        if side == "up":
            f.append(line(x, axis_y, x, axis_y - 40, color=col, sw=1.4, dash="3,3"))
            f.append(text(x, axis_y - 52, title, size=13, color=col, bold=True))
            f.append(mtext(x, axis_y - 96, sub, size=9.5, color=INK, lh=1.3))
        else:
            f.append(line(x, axis_y, x, axis_y + 44, color=col, sw=1.4, dash="3,3"))
            f.append(text(x, axis_y + 60, title, size=13, color=col, bold=True))
            f.append(mtext(x, axis_y + 78, sub, size=9.5, color=INK, lh=1.3))

    note = ("Чотири різні внески, не один винахід: ідея (PCM), обґрунтування переваги драбини для двійкового "
            "декодування (Сміт), перша робоча струмова R/2R у серійному АЦП (Datrac), формальний пристрій "
            "у патенті. Жодна ланка не «винайшла R-2R сама-одна».")
    f.append(fitbox(40, 300, W - 80, 46, note, size=12, fill="#f8fafc", stroke=MUTED))
    return render(os.path.join(IMG, 'history.svg'), W, H, *f)


# ── Фігура 6: петля послідовних наближень із R/2R-ЦАП (для вставки hist) ──────
def fig_sar_loop():
    """Серце Datrac: компаратор + регістр SAR + внутрішній R/2R-ЦАП, що з
    пробного коду робить пробну напругу. Двійковий пошук, 11 кроків."""
    W, H = 740, 380
    f = []
    f.append(text(W / 2, 28, "Серце Datrac: петля послідовних наближень із лесенкою всередині", size=15, bold=True))

    def block(x, y, w, h, label_lines, fill, stroke):
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=6)
        out += mtext(x + w / 2, y + h / 2 - (len(label_lines) - 1) * 7 + 4,
                     label_lines, size=11.5, color=INK, bold=True, lh=1.25)
        return out

    midy = 150
    # вхід (S/H) ліворуч
    f.append(text(70, midy - 36, "вхід", size=11, color=MUTED, bold=True))
    f.append(block(30, midy - 22, 90, 50, ["вибірка-\nзберігання", "(S/H)"], "#fef6e7", "#d99a2b"))
    f.append(arrow(120, midy + 3, 175, midy + 3, color=INK, sw=2))
    f.append(text(148, midy - 6, "Vвх", size=10, color=MUTED))

    # компаратор (трикутник)
    cx0 = 175
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
             % (cx0, midy - 26, cx0, midy + 32, cx0 + 64, midy + 3, NEG))
    f.append(text(cx0 + 22, midy + 7, "⊳", size=18, color=NEG, bold=True))
    f.append(text(cx0 + 30, midy - 34, "компаратор", size=10.5, color=NEG, bold=True))
    f.append(text(cx0 + 30, midy + 50, "більше/менше?", size=9.5, color=MUTED))

    # від компаратора → регістр SAR (праворуч-угору)
    f.append(arrow(cx0 + 64, midy + 3, 470, midy + 3, color=INK, sw=2))
    f.append(block(470, midy - 30, 120, 66, ["регістр SAR", "уточнює 1 біт", "за крок"], "#eafaf1", FIELD))

    # вихід коду праворуч
    f.append(arrow(590, midy + 3, 660, midy + 3, color=INK, sw=2))
    f.append(text(700, midy - 2, "код", size=12, color=FIELD, bold=True))
    f.append(text(700, midy + 16, "11 біт", size=10, color=MUTED))

    # зворотна гілка: регістр → R/2R-ЦАП → назад на (−) компаратора
    dac_y = midy + 120
    f.append(block(430, dac_y - 26, 200, 52,
                   ["внутрішній ЦАП на драбині R/2R", "пробний код → пробна напруга"],
                   "#fdecea", POS))
    # регістр вниз у ЦАП
    f.append(line(530, midy + 36, 530, dac_y - 26, color=INK, sw=1.8))
    f.append(arrow(530, dac_y - 30, 530, dac_y - 26, color=INK, sw=1.8))
    f.append(text(545, (midy + 36 + dac_y - 26) / 2, "пробний код", size=9.5, color=MUTED, anchor="start"))
    # ЦАП вліво й угору на (−) компаратора
    f.append(line(430, dac_y, 207, dac_y, color=POS, sw=2))
    f.append(line(207, dac_y, 207, midy + 32, color=POS, sw=2))
    f.append(arrow(207, midy + 40, 207, midy + 32, color=POS, sw=2))
    f.append(text(300, dac_y + 16, "пробна напруга Vпр (важки на терезах)", size=10, color=POS, anchor="middle"))

    note = ("Vвх порівнюють із пробною Vпр, яку ЦАП на драбині R/2R будує з пробного коду. Компаратор каже\n"
            "«більше/менше», регістр уточнює один біт за крок (старший → молодший), 11 кроків — і код готовий.\n"
            "Той внутрішній R/2R-ЦАП — і є наша лесенка, уперше в робочій машині.")
    f.append(fitbox(40, 312, W - 80, 60, note, size=12, fill="#f8fafc", stroke=MUTED))
    return render(os.path.join(IMG, 'sar-loop.svg'), W, H, *f)


if __name__ == "__main__":
    print(fig_ladder())
    print(fig_collapse())
    print(fig_weights())
    print(fig_recursion())
    print(fig_history())
    print(fig_sar_loop())
