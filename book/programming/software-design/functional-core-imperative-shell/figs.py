# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Потік у три смуги: оболонка приносить → ядро вирішує → оболонка виносить ──
def fig_core_shell_flow():
    W, H = 940, 640
    frags = []

    cx = W / 2

    # смуги (фон): верх оболонка, середина ядро, низ оболонка
    band_l, band_r = 210, 730
    frags.append(rect(band_l, 70,  band_r - band_l, 120, fill="#fdecea", stroke=POS,   sw=1.6, rx=12))
    frags.append(rect(band_l, 250, band_r - band_l, 150, fill="#f2faf5", stroke=FIELD, sw=2.0, rx=12))
    frags.append(rect(band_l, 460, band_r - band_l, 120, fill="#fdecea", stroke=POS,   sw=1.6, rx=12))

    # підписи смуг — ліворуч від смуг, у порожньому полі
    frags.append(text(band_l - 96, 118, "ОБОЛОНКА", size=13, bold=True, color=POS))
    frags.append(text(band_l - 96, 136, "приносить", size=12, color=POS))
    frags.append(text(band_l - 96, 322, "ЯДРО", size=13, bold=True, color=FIELD))
    frags.append(text(band_l - 96, 340, "вирішує", size=12, color=FIELD))
    frags.append(text(band_l - 96, 508, "ОБОЛОНКА", size=13, bold=True, color=POS))
    frags.append(text(band_l - 96, 526, "виносить", size=12, color=POS))

    # ── верхня смуга: джерела даних → всередину ──
    srcs = ["база", "конфіг", "ввід"]
    sx = [300, 470, 640]
    for x, lab in zip(sx, srcs):
        tb, tw, th = textbox(x, 118, lab, size=12, pad=8, fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
        frags.append(tb)

    # ── ядро: чиста функція ──
    kw_, kh = 260, 96
    kx, ky = cx - kw_ / 2, 277
    frags.append(rect(kx, ky, kw_, kh, fill="#ffffff", stroke=FIELD, sw=2.4, rx=10))
    frags.append(text(cx, ky + 34, "чиста функція", size=15, bold=True, color=FIELD))
    frags.append(text(cx, ky + 60, "той самий вхід → той самий вихід", size=11, color=MUTED))
    frags.append(text(cx, ky + 78, "жодних дотиків до світу", size=11, color=MUTED))

    # стрілки згори: від джерел вниз у ядро (вхід). Кінці зміщені так, щоб жодна
    # стрілка не лягала на текст-анотацію (та стоїть у власній рамці ліворуч у полі).
    land = [-70, 0, 70]
    for x, dx in zip(sx, land):
        frags.append(arrow(x, 138, cx + dx, ky - 6, color=POS, sw=1.9))
    an1, aw1, ah1 = textbox(126, 226, "весь потрібний\nвхід — наперед",
                            size=11, pad=7, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK, bold=True)
    frags.append(an1)

    # ── нижня смуга: цілі ефектів ──
    outs = ["запис у базу", "надіслати лист"]
    ox = [385, 555]
    for x, lab in zip(ox, outs):
        tb, tw, th = textbox(x, 508, lab, size=12, pad=8, fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
        frags.append(tb)

    # стрілки з ядра вниз до цілей (вихід — виконання рішення)
    oland = [-55, 55]
    for x, dx in zip(ox, oland):
        frags.append(arrow(cx + dx, ky + kh + 6, x, 486, color=POS, sw=1.9))
    an2, aw2, ah2 = textbox(126, 430, "рішення ядра —\nвиконати",
                            size=11, pad=7, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK, bold=True)
    frags.append(an2)

    # нижній підпис-висновок у власній рамці
    cap, cw, ch = textbox(cx, H - 32,
                          "Керування тече вниз рівно раз: зібрати вхід · вирішити · виконати",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'core-shell-flow.svg'), W, H, *frags,
           title="Оболонка приносить, ядро вирішує, оболонка виносить")


# ── Куди чіпляються моки: переплетена функція проти плану ефектів ──
def fig_where_mocks_attach():
    W, H = 960, 620
    frags = []

    # заголовки двох колонок (у своєму полі, з запасом)
    frags.append(text(250, 62, "ДО: усе в одній функції", size=15, bold=True, color=POS))
    frags.append(text(710, 62, "ПІСЛЯ: ядро повертає план", size=15, bold=True, color=FIELD))

    # роздільна вертикаль по центру
    frags.append(line(W / 2, 80, W / 2, H - 40, color=MUTED, sw=1.2, dash="4 5"))

    # ── ЛІВА колонка: одна коробка-функція, три моки чіпляються ──
    lx, lw = 150, 200
    ly, lh = 150, 300
    frags.append(rect(lx, ly, lw, lh, fill="#fdecea", stroke=POS, sw=2.2, rx=10))
    frags.append(text(lx + lw / 2, ly + 34, "handleTx()", size=14, bold=True, color=INK))
    rows = ["читає базу", "рахує рішення", "пише в базу", "шле лист"]
    for i, r in enumerate(rows):
        yy = ly + 74 + i * 46
        frags.append(text(lx + lw / 2, yy, r, size=12, color=MUTED))

    # моки причеплені зліва до рядків-дій
    mock_rows = [0, 2, 3]  # база-читання, база-запис, лист
    mock_labels = ["мок БД", "мок БД", "мок пошти"]
    for ri, ml in zip(mock_rows, mock_labels):
        yy = ly + 74 + ri * 46 - 6
        tb, tw, th = textbox(58, yy, ml, size=11, pad=6, fill="#fff4f2",
                             stroke=POS, sw=1.4, color=POS)
        frags.append(tb)
        frags.append(arrow(58 + tw / 2 + 4, yy, lx - 4, yy, color=POS, sw=1.6))

    capL, cwL, chL = textbox(lx + lw / 2, ly + lh + 42,
                             "3 моки, щоб перевірити\nодне правило",
                             size=11, pad=8, fill="#ffffff", stroke=POS, sw=1.5, color=INK, bold=True)
    frags.append(capL)

    # ── ПРАВА колонка: ядро → план (дані) → оболонка ──
    rx0 = 600
    kw_, kh = 210, 78
    kx, ky = rx0, 150
    frags.append(rect(kx, ky, kw_, kh, fill="#ffffff", stroke=FIELD, sw=2.4, rx=10))
    frags.append(text(kx + kw_ / 2, ky + 32, "decide()", size=14, bold=True, color=FIELD))
    frags.append(text(kx + kw_ / 2, ky + 56, "чиста функція", size=11, color=MUTED))

    # план (дані) — коробка-список
    pw, ph = 210, 96
    px, py = rx0, 300
    frags.append(rect(px, py, pw, ph, fill="#f2faf5", stroke=FIELD, sw=1.8, rx=10))
    frags.append(text(px + pw / 2, py + 26, "ПЛАН (дані)", size=12, bold=True, color=FIELD))
    frags.append(text(px + pw / 2, py + 48, "• запис у базу", size=11, color=INK))
    frags.append(text(px + pw / 2, py + 68, "• надіслати лист", size=11, color=INK))
    frags.append(arrow(kx + kw_ / 2, ky + kh + 4, px + pw / 2, py - 4, color=FIELD, sw=2.0))

    # оболонка-виконавець
    sw_, sh = 210, 66
    sx, sy = rx0, 470
    frags.append(rect(sx, sy, sw_, sh, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    frags.append(text(sx + sw_ / 2, sy + 28, "run(plan)", size=13, bold=True, color=POS))
    frags.append(text(sx + sw_ / 2, sy + 48, "виконує описи", size=11, color=MUTED))
    frags.append(arrow(px + pw / 2, py + ph + 4, sx + sw_ / 2, sy - 4, color=POS, sw=2.0))

    # анотація праворуч: тест ядра дивиться на план, нуль моків
    an, aw, ah = textbox(850, 348, "тест ядра\nзвіряє список.\nнуль моків",
                         size=11, pad=8, fill="#ffffff", stroke=FIELD, sw=1.5, color=INK, bold=True)
    frags.append(an)
    frags.append(arrow(px + pw + 4, py + ph / 2, 850 - aw / 2 - 4, py + ph / 2, color=FIELD, sw=1.6))

    render(os.path.join(IMG, 'mocks-before-after.svg'), W, H, *frags,
           title="Куди чіпляються моки: переплетена функція проти плану ефектів")


# ── Сендвіч читати→вирішити→діяти, повторений шарами ──
def fig_sandwich():
    W, H = 900, 560
    frags = []

    cx = W / 2
    band_w = 360
    bx = cx - band_w / 2
    steps = [
        ("ЧИТАТИ", "оболонка бере рахунок", POS, "#fdecea"),
        ("ВИРІШИТИ", "ядро: чи можна зняти", FIELD, "#f2faf5"),
        ("ДІЯТИ", "оболонка знімає кошти", POS, "#fdecea"),
        ("ЧИТАТИ", "оболонка бере результат", POS, "#fdecea"),
        ("ВИРІШИТИ", "ядро: що робити далі", FIELD, "#f2faf5"),
        ("ДІЯТИ", "оболонка шле звіт", POS, "#fdecea"),
    ]
    top = 70
    bh = 62
    gap = 14
    y = top
    centers = []
    for (title, sub, col, fill) in steps:
        frags.append(rect(bx, y, band_w, bh, fill=fill, stroke=col, sw=1.8, rx=9))
        frags.append(text(bx + 96, y + bh / 2 + 5, title, size=13, bold=True, color=col))
        frags.append(text(bx + 236, y + bh / 2 + 5, sub, size=11, color=INK))
        centers.append(y + bh / 2)
        y += bh + gap

    # стрілки вниз між смугами (у вузькому проміжку праворуч, повз написи)
    ax = bx + band_w + 26
    for i in range(len(steps) - 1):
        frags.append(arrow(ax, centers[i] + 2, ax, centers[i + 1] - 2, color=MUTED, sw=1.6))

    # ліворуч — підписи, що зелені смуги лишаються чистими
    frags.append(text(bx - 150, centers[1], "чисте", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(bx - 150, centers[1] + 18, "ядро", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(bx - 150, centers[4], "чисте", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(bx - 150, centers[4] + 18, "ядро", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(line(bx - 60, centers[1], bx - 4, centers[1], color=FIELD, sw=1.4))
    frags.append(line(bx - 60, centers[4], bx - 4, centers[4], color=FIELD, sw=1.4))

    # праворуч — підпис, що кожен зелений шматок чистий окремо
    an, aw, ah = textbox(W - 120, centers[2] + (centers[3] - centers[2]) / 2,
                         "кожен шар ядра\nчистий окремо",
                         size=11, pad=8, fill="#ffffff", stroke=FIELD, sw=1.4, color=INK, bold=True)
    frags.append(an)

    cap, cw, ch = textbox(cx, H - 30,
                          "Форма не ламається — вона повторюється шарами",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'sandwich-layers.svg'), W, H, *frags,
           title="Сендвіч: читати · вирішити · діяти — повторено шарами")


# ── Нитка спадкоємства для вставки hist-boundaries-bernhardt ──
def fig_boundaries_lineage():
    W, H = 980, 720
    frags = []

    cx = 320            # вісь ліворуч, щоб праворуч лишилося поле під підписи
    box_w = 300

    # ── дальній кінець: функційна традиція ──
    y0 = 66
    frags.append(rect(cx - box_w / 2, y0, box_w, 96, fill="#f2faf5", stroke=FIELD, sw=2.2, rx=12))
    frags.append(text(cx, y0 + 30, "функційна традиція", size=15, bold=True, color=FIELD))
    frags.append(text(cx, y0 + 54, "тип IO в Haskell · «Out of the Tar Pit» 2006", size=11, color=MUTED))
    frags.append(text(cx, y0 + 76, "чиста серцевина, брудний край", size=11, color=INK))
    an0, _, _ = textbox(cx + box_w / 2 + 160, y0 + 48,
                        "думка ДАВНЯ\nй колективна",
                        size=12, pad=8, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK, bold=True)
    frags.append(an0)

    # ── об'єктний родич: порти й перехідники ──
    y1 = 226
    frags.append(rect(cx - box_w / 2, y1, box_w, 96, fill="#eef4ff", stroke=NEG, sw=2.2, rx=12))
    frags.append(text(cx, y1 + 30, "порти й перехідники", size=15, bold=True, color=NEG))
    frags.append(text(cx, y1 + 54, "Алістер Кокберн · визрів 1990-ті", size=11, color=MUTED))
    frags.append(text(cx, y1 + 76, "письмово 2005 · межа — інтерфейс", size=11, color=INK))

    frags.append(arrow(cx, y0 + 96, cx, y1 - 6, color=INK, sw=1.8))

    # ── ближній кінець: три віхи 2012, Бернгардт ──
    y2 = 396
    band_h = 252
    frags.append(rect(cx - box_w / 2 - 26, y2, box_w + 52, band_h,
                      fill="#fdf6ee", stroke=POS, sw=2.0, rx=14))
    frags.append(text(cx, y2 + 28, "Гері Бернгардт · 2012", size=15, bold=True, color=POS))
    frags.append(text(cx, y2 + 48, "дав давній формі НАЗВУ", size=11, color=INK))

    frags.append(arrow(cx, y1 + 96, cx, y2 - 6, color=INK, sw=1.8))

    # три віхи-рядки всередині: chip з місяцем + опис праворуч від нього
    steps = [
        ("березень", "«Fast Test, Slow Test» — біль ізоляції"),
        ("липень",   "скринкаст — ВИКУТО назву"),
        ("листопад", "доповідь «Boundaries» — рознесла світом"),
    ]
    left = cx - box_w / 2 - 8
    sy = y2 + 78
    for lab, desc in steps:
        chip, cw, _ = textbox(left + 52, sy, lab,
                              size=11, pad=6, fill="#fff4f2", stroke=POS, sw=1.3,
                              color=POS, bold=True, min_w=92)
        frags.append(chip)
        frags.append(text(left + 104, sy + 4, desc, size=11, color=INK, anchor="start"))
        sy += 54

    # підпис-висновок праворуч у полі
    an2, _, _ = textbox(cx + box_w / 2 + 160, y2 + band_h / 2,
                        "ідею НІХТО не\nвинайшов одним рухом;\nвлучне ім'я — один\nбатько, один рік",
                        size=12, pad=9, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK, bold=True)
    frags.append(an2)

    render(os.path.join(IMG, 'boundaries-lineage.svg'), W, H, *frags,
           title="Нитка: давня форма → об'єктний родич → назва 2012")


if __name__ == "__main__":
    fig_core_shell_flow()
    fig_where_mocks_attach()
    fig_sandwich()
    fig_boundaries_lineage()
    print("figures written to", IMG)
