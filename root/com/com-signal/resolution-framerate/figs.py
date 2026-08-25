# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Роздільність — розмір сітки пікселів (VGA→4K) ─────────────────────────
def fig_resolution():
    W, H = 960, 470
    frags = []
    # Вкладені прямокутники роздільностей у спільному масштабі (4K = база).
    base_x, base_y = 60, 70
    sc = 0.105  # px-фігури на піксель кадру
    tiers = [
        ("4K · 3840×2160 · ~8.3 Мпк", 3840, 2160, "#cbd5e1"),
        ("Full HD · 1920×1080 · ~2 Мпк", 1920, 1080, "#9fb3c8"),
        ("HD 720p · 1280×720", 1280, 720, "#6b7f99"),
        ("VGA · 640×480 · ~0.3 Мпк", 640, 480, "#1a1a1a"),
    ]
    for label, w, h, col in tiers:
        rw, rh = w * sc, h * sc
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                     'fill="none" stroke="%s" stroke-width="2"/>'
                     % (base_x, base_y, rw, rh, col))
    # підписи рівнів — праворуч від кожної рамки, по верхньому краю
    ys = [base_y + 12]
    frags.append(text(base_x + 3840 * sc + 12, base_y + 14, tiers[0][0], size=13,
                      color="#475569", anchor="start"))
    frags.append(text(base_x + 1920 * sc + 12, base_y + 1080 * sc - 6, tiers[1][0],
                      size=13, color="#475569", anchor="start"))
    frags.append(text(base_x + 1280 * sc + 12, base_y + 720 * sc - 6, tiers[2][0],
                      size=12, color="#334155", anchor="start"))
    frags.append(text(base_x + 12, base_y + 480 * sc + 18, tiers[3][0],
                      size=12, color=INK, anchor="start", bold=True))

    # Праворуч: груба «А» з кількох пікселів vs чітка «А»
    gx = 660
    frags.append(text(gx + 95, 70, "та сама літера «А»", size=13, color=MUTED))
    # груба: сітка 5×6 великих пікселів
    cell = 17
    grid = [
        "00100",
        "01010",
        "01010",
        "11111",
        "10001",
        "10001",
    ]
    bx, by = gx, 90
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            fill = "#1a1a1a" if ch == "1" else "#eef2f6"
            frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                         'fill="%s" stroke="#cbd5e1" stroke-width="0.5"/>'
                         % (bx + c * cell, by + r * cell, cell, cell, fill))
    frags.append(text(bx + cell * 2.5, by + cell * 6 + 18, "мало пікселів", size=12, color=MUTED))
    # чітка: гладка «А» гліфом
    frags.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="118" '
                 'fill="#1a1a1a" text-anchor="middle">А</text>'
                 % (gx + 200, by + 100, FONT))
    frags.append(text(gx + 200, by + cell * 6 + 18, "багато пікселів", size=12, color=MUTED))
    frags.append('<line x1="%.1f" y1="110" x2="%.1f" y2="110" stroke="%s" '
                 'stroke-width="1.8" marker-end="url(#arrow)"/>' % (gx + 105, gx + 150, FIELD))

    # нижній рядок-висновок
    frags.append(text(W / 2, H - 16, "Більше пікселів → дрібніші деталі, але більше даних "
                      "і (на малому сенсорі) менше світла на піксель",
                      size=13, color=INK))
    render(os.path.join(OUT, "resolution-grid.svg"), W, H, *frags,
           title="Роздільність — це розмір сітки пікселів")


# ── 2. Частота кадрів — рух зі застиглих знімків ─────────────────────────────
def fig_framerate():
    W, H = 960, 430
    frags = []
    # Стрічка з 6 кадрів: м'яч рухається зліва направо й по дузі
    n = 6
    fx, fy = 70, 80
    fw, fh = 120, 96
    gap = 16
    positions = [(0.30, 0.70), (0.42, 0.48), (0.52, 0.34), (0.60, 0.34),
                 (0.70, 0.48), (0.82, 0.70)]
    for i in range(n):
        x = fx + i * (fw + gap)
        frags.append(rect(x, fy, fw, fh, fill="#fbfcfd", stroke="#cbd5e1", sw=1.2, rx=4))
        px, py = positions[i]
        frags.append(circle(x + fw * px, fy + fh * py, 11, fill="#d98a00", stroke="#a96b00", sw=1.5))
        frags.append(text(x + fw / 2, fy + fh + 16, "кадр %d" % (i + 1), size=11, color=MUTED))
    # дужка «показано швидко → рух»
    cy = fy + fh + 54
    frags.append(text(W / 2, cy + 4, "показані понад ~20 разів на секунду → око зливає в рух",
                      size=13, color=INK, bold=True))

    # сходинка fps: 24 / 30 / 60
    sy = cy + 36
    steps = [("24 fps", "кіно", 70), ("30 fps", "відео", 140), ("60 fps", "плавно / низька затримка", 210)]
    base = sy + 90
    bx = 150
    bw = 150
    for i, (lab, sub, hgt) in enumerate(steps):
        x = bx + i * (bw + 30)
        frags.append(rect(x, base - hgt * 0.42, bw, hgt * 0.42, fill=FILL, stroke=LINE, sw=1.3))
        frags.append(text(x + bw / 2, base - hgt * 0.42 - 8, lab, size=14, color=INK, bold=True))
        frags.append(text(x + bw / 2, base + 18, sub, size=12, color=MUTED))
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>'
                 % (bx - 18, base + 2, bx + 3 * bw + 60 + 4, base + 2, MUTED))
    frags.append(text(bx + 3 * bw / 2 + 90, base + 40,
                      "більше fps → плавніше й свіжіший кадр, але стільки ж разів більше даних",
                      size=12, color=INK))
    render(os.path.join(OUT, "framerate.svg"), W, H, *frags,
           title="Відео — це швидкі знімки поспіль")


# ── 3. Сирий потік — пожежний шланг даних ────────────────────────────────────
def fig_firehose():
    W, H = 960, 440
    frags = []
    # Формула вгорі
    box, bw, bh = textbox(W / 2, 70,
                          "потік = ширина × висота × канали × біти × кадри/с",
                          size=16, bold=True, fill="#eef6ef", stroke=FIELD, pad=14)
    frags.append(box)

    # Дві колонки-приклади з «товстою трубою» проти «тонкої труби»
    def example(cx, top, title, val_big, val_small, col):
        out = []
        out.append(text(cx, top, title, size=15, color=INK, bold=True))
        out.append(text(cx, top + 24, val_big, size=20, color=col, bold=True))
        out.append(text(cx, top + 44, val_small, size=13, color=MUTED))
        return out

    frags += example(280, 150, "1080p · 30 fps · 8 біт RGB", "≈ 1.5 Гбіт/с", "≈ 187 МБ щосекунди", "#a96b00")
    frags += example(680, 150, "4K · 60 fps · 8 біт RGB", "≈ 12 Гбіт/с", "≈ 1.5 ГБ щосекунди", POS)

    # Шкала-порівняння труб (логічна, не точна): сире vs канали
    by = 250
    bars = [
        ("сире 4K60", 900, POS),
        ("сире 1080p30", 470, "#a96b00"),
        ("SD-картка (сотні МБ/с)", 95, FIELD),
        ("радіоканал FPV (Мбіт/с)", 14, NEG),
    ]
    bx = 320
    rowh = 34
    maxw = 560
    scale = maxw / 900.0
    for i, (lab, v, col) in enumerate(bars):
        y = by + i * rowh
        frags.append(text(bx - 12, y + 15, lab, size=12, color=INK, anchor="end"))
        frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="20" rx="3" '
                     'fill="%s"/>' % (bx, y, max(4, v * scale), col))
    frags.append(text(W / 2, H - 16,
                      "Сире відео в тисячі разів більше за канал чи картку → передати як є неможливо, звідси стиснення",
                      size=13, color=INK, bold=True))
    render(os.path.join(OUT, "firehose.svg"), W, H, *frags,
           title="Сирий потік — пожежний шланг даних")


# ── 4. Компроміс: за все платиться бітами ────────────────────────────────────
def fig_tradeoff():
    W, H = 960, 430
    frags = []
    # Ліворуч — «хочемо більше», праворуч — «платимо», стрілка між ними
    lb, lbw, lbh = textbox(220, 150,
                           "ХОЧЕМО БІЛЬШЕ\nроздільності\nкадрів/с\nглибини біта",
                           size=14, bold=True, fill="#eef6ef", stroke=FIELD, pad=16)
    frags.append(lb)
    rb, rbw, rbh = textbox(740, 150,
                           "ПЛАТИМО\nсмугою каналу\nпам'яттю · обчисленнями\nзатримкою · батареєю",
                           size=14, bold=True, fill="#fdeeec", stroke=POS, pad=16)
    frags.append(rb)
    frags.append('<line x1="335" y1="150" x2="615" y2="150" stroke="%s" '
                 'stroke-width="2.4" marker-end="url(#arrow)"/>' % LINE)
    frags.append(text(W / 2, 138, "за кожен зайвий біт", size=12, color=MUTED))

    # Унизу — дві задачі з різним вибором
    cards = [
        (255, "FPV (ти летиш у відео)",
         ["над усе — низька затримка", "й плавність, а не мегапікселі",
          "краще чітке 720p без лагу,", "ніж 4K із запізненням"], NEG),
        (705, "Машинне бачення",
         ["баланс роздільності й fps", "з бортовим обчислювачем:",
          "забагато даних — не", "встигне обробити кадр"], FIELD),
    ]
    for cx, head, lines, col in cards:
        bx, by, bw, bh = cx - 195, 250, 390, 130
        frags.append(rect(bx, by, bw, bh, fill="#fbfcfd", stroke=col, sw=1.6))
        frags.append(text(cx, by + 26, head, size=14, color=INK, bold=True))
        for i, ln in enumerate(lines):
            frags.append(text(cx, by + 52 + i * 19, ln, size=12.5, color="#334155"))
    frags.append(text(W / 2, H - 14, "А сирий потік однаково стискають",
                      size=13, color=INK, bold=True))
    render(os.path.join(OUT, "tradeoff.svg"), W, H, *frags,
           title="За все платиться бітами")


if __name__ == "__main__":
    fig_resolution()
    fig_framerate()
    fig_firehose()
    fig_tradeoff()
    print("done: resolution-grid, framerate, firehose, tradeoff")
