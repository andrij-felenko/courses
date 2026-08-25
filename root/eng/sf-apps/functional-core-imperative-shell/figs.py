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


# ── Інваріант «нема каналу»: канал до світу проти чистого відображення ──
def fig_channel_invariant():
    W, H = 1020, 560
    frags = []

    # роздільна вертикаль між панелями (у порожньому проміжку)
    frags.append(line(510, 88, 510, 486, color=MUTED, sw=1.2, dash="4 5"))

    # ── ЛІВА панель: функція з КАНАЛОМ до світу ──
    frags.append(text(290, 66, "З КАНАЛОМ до світу", size=15, bold=True, color=POS))

    # коробка-функція
    fx, fw, fy, fh = 180, 220, 110, 270
    frags.append(rect(fx, fy, fw, fh, fill="#fdecea", stroke=POS, sw=2.2, rx=10))
    frags.append(text(290, 145, "decide?()", size=14, bold=True, color=INK))
    frags.append(text(290, 190, "бере вхід", size=12, color=MUTED))
    frags.append(text(290, 230, "db.get(id)", size=12, bold=True, color=POS))
    frags.append(text(290, 270, "рахує", size=12, color=MUTED))
    frags.append(text(290, 310, "повертає", size=12, color=MUTED))

    # світ ліворуч + двобічний канал у проміжку (повз тексти, що стоять при центрі)
    wb, ww, wh = textbox(96, 240, "СВІТ\nбаза", size=12, pad=8, fill="#fff4f2",
                         stroke=POS, sw=1.4, color=POS, bold=True)
    frags.append(wb)
    frags.append(arrow(fx - 2, 222, 96 + ww / 2 + 4, 222, color=POS, sw=1.7))
    frags.append(arrow(96 + ww / 2 + 4, 238, fx - 2, 238, color=POS, sw=1.7))

    anL, _, _ = textbox(290, 425, "недетерміноване\nтреба риштування",
                        size=11, pad=8, fill="#ffffff", stroke=POS, sw=1.5, color=INK, bold=True)
    frags.append(anL)

    # ── ПРАВА панель: чисте відображення, каналу нема ──
    frags.append(text(760, 66, "БЕЗ каналу (чисте)", size=15, bold=True, color=FIELD))

    ib, iw, ih = textbox(760, 108, "вхід: усе принесено (дані)", size=12, pad=8,
                         fill="#f2faf5", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    frags.append(ib)

    gx, gw, gy, gh = 650, 220, 150, 230
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=FIELD, sw=2.4, rx=10))
    frags.append(text(760, 188, "decide()", size=14, bold=True, color=FIELD))
    frags.append(text(760, 228, "лише перетворює вхід", size=12, color=MUTED))
    frags.append(text(760, 262, "нема дотику до світу", size=12, color=MUTED))

    for x in (710, 760, 810):
        frags.append(arrow(x, 128, x, gy - 4, color=FIELD, sw=1.7))
    ob, ow, oh = textbox(760, 415, "рішення (дані)", size=12, pad=8, fill="#f2faf5",
                         stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    frags.append(ob)
    frags.append(arrow(760, gy + gh + 2, 760, 415 - oh / 2 - 4, color=FIELD, sw=1.8))
    anR, _, _ = textbox(760, 470, "детерміноване\nтест таблицею",
                        size=11, pad=8, fill="#ffffff", stroke=FIELD, sw=1.5, color=INK, bold=True)
    frags.append(anR)

    cap, _, _ = textbox(510, H - 28,
                        "Чистоту дає не «нема запису», а нема каналу до світу",
                        size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'channel-invariant.svg'), W, H, *frags,
           title="Інваріант «нема каналу»: читання теж канал")


# ── Приховані входи (годинник/випадковість/ідентифікатор) і їх підняття ──
def fig_hidden_inputs():
    W, H = 900, 620
    frags = []

    # ── ВЕРХ: «чиста» на вигляд функція таємно читає світ ──
    frags.append(text(450, 60, "виглядає чистою — таємно читає світ", size=15, bold=True, color=POS))

    chips = [("now()", 270), ("random()", 450), ("uuid()", 630)]
    for lab, x in chips:
        ch, cw, chh = textbox(x, 110, lab, size=12, pad=7, fill="#fff4f2",
                              stroke=POS, sw=1.4, color=POS, bold=True, min_w=92)
        frags.append(ch)

    frags.append(rect(300, 180, 300, 100, fill="#fdecea", stroke=POS, sw=2.2, rx=10))
    frags.append(text(450, 215, "isExpired(session)", size=14, bold=True, color=INK))
    frags.append(text(450, 245, "виглядає чистою", size=12, color=MUTED))

    lands = [360, 450, 540]
    for (lab, x), lx in zip(chips, lands):
        frags.append(arrow(x, 128, lx, 178, color=POS, sw=1.7))

    an1, _, _ = textbox(450, 322, "прихований вхід: час · ентропія · лічильник → недетермінована",
                        size=11, pad=8, fill="#ffffff", stroke=POS, sw=1.4, color=INK, bold=True)
    frags.append(an1)

    frags.append(line(120, 362, 780, 362, color=MUTED, sw=1.2, dash="4 5"))

    # ── НИЗ: підняли приховані входи в аргументи ──
    frags.append(text(450, 400, "підняли у аргументи — чисте", size=15, bold=True, color=FIELD))

    frags.append(rect(120, 440, 220, 100, fill="#fdecea", stroke=POS, sw=2.0, rx=10))
    frags.append(text(230, 472, "ОБОЛОНКА", size=13, bold=True, color=POS))
    frags.append(text(230, 498, "читає годинник раз", size=11, color=MUTED))
    frags.append(text(230, 522, "now · seed · id", size=11, bold=True, color=INK))

    frags.append(rect(520, 440, 300, 100, fill="#ffffff", stroke=FIELD, sw=2.4, rx=10))
    frags.append(text(670, 478, "isExpired(session, now)", size=13, bold=True, color=FIELD))
    frags.append(text(670, 508, "чисте ядро", size=11, color=MUTED))

    lb, lw2, lh2 = textbox(430, 462, "аргументи-дані", size=11, pad=6, fill="#f2faf5",
                           stroke=FIELD, sw=1.3, color=FIELD, bold=True)
    frags.append(lb)
    frags.append(arrow(340, 505, 518, 505, color=FIELD, sw=1.9))

    cap, _, _ = textbox(450, H - 26,
                        "Годинник, кубик і лічильник читає лише оболонка — раз",
                        size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'hidden-inputs.svg'), W, H, *frags,
           title="Приховані входи: підняти у аргументи")


# ── Один план — багато тлумачів ──
def fig_many_interpreters():
    W, H = 1080, 580
    frags = []

    cx = 540
    # ядро
    frags.append(rect(cx - 80, 70, 160, 60, fill="#ffffff", stroke=FIELD, sw=2.4, rx=10))
    frags.append(text(cx, 98, "ЯДРО", size=13, bold=True, color=FIELD))
    frags.append(text(cx, 118, "decide()", size=12, color=MUTED))
    frags.append(arrow(cx, 130, cx, 156, color=FIELD, sw=2.0))

    # план
    frags.append(rect(cx - 150, 160, 300, 80, fill="#f2faf5", stroke=FIELD, sw=2.0, rx=10))
    frags.append(text(cx, 192, "ПЛАН (дані)", size=14, bold=True, color=FIELD))
    frags.append(text(cx, 218, "[опис, опис, …]", size=12, color=INK))

    # чотири тлумачі
    boxes = [
        (170, "виконавець", "реальні дії", POS, "#fdecea"),
        (430, "сухий прогін", "лише друк", NEG, "#eef4ff"),
        (690, "аудит-журнал", "слід у лог", MUTED, "#f4f6f8"),
        (950, "оцінка", "вартості", FIELD, "#f2faf5"),
    ]
    for bx, t1, t2, col, fill in boxes:
        frags.append(rect(bx - 110, 380, 220, 90, fill=fill, stroke=col, sw=2.0, rx=10))
        frags.append(text(bx, 418, t1, size=13, bold=True, color=col))
        frags.append(text(bx, 444, t2, size=11, color=MUTED))
        frags.append(arrow(cx, 242, bx, 376, color=col, sw=1.7))

    cap, _, _ = textbox(cx, H - 26,
                        "Один план — багато тлумачів; ядро не змінюється жодним рядком",
                        size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'many-interpreters.svg'), W, H, *frags,
           title="Один план, багато тлумачів")


# ── Застарілий знімок і вікно TOCTOU між планом і виконанням ──
def fig_stale_snapshot():
    W, H = 1040, 470
    frags = []

    steps = [
        (145, "оболонка читає", "версія = 5", POS, "#fdecea"),
        (399, "ЯДРО вирішує", "план на v5", FIELD, "#f2faf5"),
        (653, "оболонка пише", "«якщо ще v5»", POS, "#fdecea"),
        (907, "конфлікт →", "перечитати, повторити", POS, "#fdecea"),
    ]
    by, bh, bw = 200, 80, 230
    for cxn, t1, t2, col, fill in steps:
        frags.append(rect(cxn - bw / 2, by, bw, bh, fill=fill, stroke=col, sw=2.0, rx=10))
        frags.append(text(cxn, by + 32, t1, size=13, bold=True, color=col))
        frags.append(text(cxn, by + 56, t2, size=11, color=INK))

    # короткі стрілки між кроками, у проміжках
    for i in range(len(steps) - 1):
        x1 = steps[i][0] + bw / 2
        x2 = steps[i + 1][0] - bw / 2
        frags.append(arrow(x1 + 2, by + bh / 2, x2 - 2, by + bh / 2, color=MUTED, sw=1.6))

    # чужа транзакція згори, у проміжок між box2 і box3
    co, cw, chh = textbox(526, 92, "чужа транзакція\nверсія = 6", size=11, pad=8,
                          fill="#eef4ff", stroke=NEG, sw=1.6, color=NEG, bold=True)
    frags.append(co)
    frags.append(arrow(526, 92 + chh / 2 + 2, 526, by - 6, color=NEG, sw=1.8))

    # дужка «ВІКНО» під box2..box3
    wx1, wx2, wy = 399, 653, 300
    frags.append(line(wx1, wy, wx2, wy, color=INK, sw=1.5))
    frags.append(line(wx1, wy - 8, wx1, wy, color=INK, sw=1.5))
    frags.append(line(wx2, wy - 8, wx2, wy, color=INK, sw=1.5))
    wl, _, _ = textbox((wx1 + wx2) / 2, 332, "ВІКНО (TOCTOU): знімок застаріває",
                       size=11, pad=7, fill="#ffffff", stroke=MUTED, sw=1.3, color=INK, bold=True)
    frags.append(wl)

    cap, _, _ = textbox(520, H - 24,
                        "Оптимістична версія закриває вікно: пиши умовно, на конфлікті перечитай",
                        size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'stale-snapshot.svg'), W, H, *frags,
           title="Вікно між планом і дією: застарілий знімок")


# ── Приклади проти властивості: обрані точки проти закону над усім простором ──
def fig_examples_vs_property():
    W, H = 1000, 600
    frags = []

    # поле входів — майже все баг-зона
    fx, fy, fw, fh = 90, 96, 520, 396
    frags.append(rect(fx, fy, fw, fh, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    frags.append(text(fx + fw / 2, fy + 26, "простір входів (total, n)", size=13, bold=True, color=POS))

    # осі-натяки поза полем
    frags.append(text(fx + fw / 2, fy + fh + 28, "n (на скільки ділимо) →", size=11, color=MUTED))
    frags.append(text(fx - 40, fy + fh / 2, "total", size=11, color=MUTED, anchor="middle"))

    # безпечні «круглі» точки (total кратне n) — зелені плюсики, розсіяні зрідка
    safe = [(150, 440), (150, 300), (150, 170), (250, 440), (250, 190),
            (355, 320), (460, 440), (460, 180), (545, 300)]
    for (sx, sy) in safe:
        frags.append(plus(sx, sy, r=6))

    # приклади, обрані людиною, сидять на безпечних точках — сині крапки
    for (ex_x, ex_y) in [(150, 440), (250, 440), (150, 300), (355, 320), (460, 440)]:
        frags.append(circle(ex_x, ex_y, 7, fill=NEG, stroke="#ffffff", sw=1.5))

    # 10^4 випадкових — червоні крапки скрізь (детерміновано розкладені LCG-ом)
    seedv = 7
    rnd = []
    for _ in range(48):
        seedv = (seedv * 1103515245 + 12345) & 0x7fffffff
        rx = fx + 22 + (seedv % (fw - 44))
        seedv = (seedv * 1103515245 + 12345) & 0x7fffffff
        ry = fy + 46 + (seedv % (fh - 74))
        rnd.append((rx, ry))
    for (rx, ry) in rnd:
        frags.append(circle(rx, ry, 3.2, fill=POS, stroke="#7a2018", sw=0.8))
    # перший контрприклад — обведена крапка
    frags.append(circle(rnd[5][0], rnd[5][1], 9, fill="none", stroke=INK, sw=2.0))

    # ЛЕГЕНДА праворуч, окрема колонка
    lx = 810
    b1, _, _ = textbox(lx, 168, "сині — приклади,\nобрані людиною:\nкруглі 100/2, 100/4…\n(в безпечних точках)",
                       size=11, pad=9, fill="#eef4ff", stroke=NEG, sw=1.5, color=INK, bold=True)
    frags.append(b1)
    b2, _, _ = textbox(lx, 316, "червоні — 10⁴\nвипадкових: розсіяні\nскрізь, майже всі\nв баг-зоні",
                       size=11, pad=9, fill="#fff4f2", stroke=POS, sw=1.5, color=INK, bold=True)
    frags.append(b2)
    b3, _, _ = textbox(lx, 448, "обведена — перший\nконтрприклад прогону",
                       size=11, pad=9, fill="#ffffff", stroke=INK, sw=1.4, color=INK, bold=True)
    frags.append(b3)

    cap, _, _ = textbox(W / 2, H - 24,
                        "Людина обирає «круглі» приклади — рідкі безпечні точки; випадковий прогін засіває весь простір і одразу влучає в баг",
                        size=11, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'examples-vs-property.svg'), W, H, *frags,
           title="Приклади проти властивості: точки проти закону")


# ── Звуження: від випадкового провалу до найменшого контрприкладу ──
def fig_shrinking_funnel():
    W, H = 900, 620
    frags = []

    cx = 330
    steps = [
        ("total = 73 982,  n = 7", 300, POS,   "#fdecea", False),
        ("total = 4 021,  n = 7",  250, POS,   "#fdecea", False),
        ("total = 58,  n = 3",     200, POS,   "#fdecea", False),
        ("total = 8,  n = 3",      168, POS,   "#fdecea", False),
        ("total = 1,  n = 2",      150, FIELD, "#eafaf0", True),
    ]
    y = 84
    gap = 92
    bh = 50
    centers = []
    for (label, w, col, fill, hi) in steps:
        sw = 2.6 if hi else 1.8
        frags.append(rect(cx - w / 2, y, w, bh, fill=fill, stroke=col, sw=sw, rx=10))
        frags.append(text(cx, y + bh / 2 + 5, label, size=14, bold=hi, color=INK))
        centers.append((y, y + bh))
        y += gap

    # стрілки вниз між чипами (у проміжках, повз написи)
    for i in range(len(steps) - 1):
        frags.append(arrow(cx, centers[i][1] + 4, cx, centers[i + 1][0] - 4, color=MUTED, sw=1.8))

    # права дужка «звуження» вздовж усіх кроків
    bx = 520
    top_y, bot_y = centers[0][0] + 8, centers[-1][1] - 8
    frags.append(line(bx, top_y, bx, bot_y, color=INK, sw=1.5))
    frags.append(line(bx, top_y, bx - 10, top_y, color=INK, sw=1.5))
    frags.append(line(bx, bot_y, bx - 10, bot_y, color=INK, sw=1.5))
    an, _, _ = textbox(660, (top_y + bot_y) / 2,
                       "звуження:\nщоразу МЕНШИЙ\nвхід, що ВСЕ ЩЕ\nламає закон",
                       size=11, pad=9, fill="#ffffff", stroke=INK, sw=1.4, color=INK, bold=True)
    frags.append(an)

    # ліворуч — верхня й нижня примітки, у власних рамках
    l1, _, _ = textbox(120, centers[0][0] + bh / 2, "перший провал:\nвипадковий,\nвеликий",
                       size=11, pad=8, fill="#fff4f2", stroke=POS, sw=1.4, color=INK, bold=True)
    frags.append(l1)
    l2, _, _ = textbox(120, centers[-1][0] + bh / 2, "найменший —\nйого й друкує\nтест",
                       size=11, pad=8, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, bold=True)
    frags.append(l2)

    cap, _, _ = textbox(W / 2, H - 26,
                        "Звуження зводить величезний випадковий контрприклад до найменшого входу, що досі валить закон — відтворювано за зерном",
                        size=11, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'shrinking-funnel.svg'), W, H, *frags,
           title="Звуження: від випадкового провалу до найменшого контрприкладу")


# ── Риштування: площа N·D проти лінії N (для math-isolation-economics) ──
def fig_isolation_lattice():
    W, H = 1000, 560
    frags = []

    Nrows = 5   # правила N
    Ncols = 4   # залежності D
    cw, ch = 58, 30
    gy = 152
    byb = gy + Nrows * ch + 18

    # ── ЛІВА панель: сітка N×D мок-клітин ──
    frags.append(text(320, 66, "ПЕРЕПЛЕТЕНО: риштування = N · D", size=15, bold=True, color=POS))
    gx = 250
    deps = ["БД", "пошта", "журнал", "банк"]
    for j, d in enumerate(deps):
        frags.append(text(gx + j * cw + cw / 2, gy - 12, d, size=11, color=POS))
    for i in range(Nrows):
        frags.append(text(gx - 18, gy + i * ch + ch / 2 + 4, "пр.%d" % (i + 1),
                          size=10, color=MUTED, anchor="end"))
        for j in range(Ncols):
            frags.append(rect(gx + j * cw, gy + i * ch, cw, ch,
                              fill="#fdecea", stroke=POS, sw=1.0, rx=2))
    bx1, bx2 = gx, gx + Ncols * cw
    frags.append(line(bx1, byb, bx2, byb, color=INK, sw=1.4))
    frags.append(line(bx1, byb - 7, bx1, byb, color=INK, sw=1.4))
    frags.append(line(bx2, byb - 7, bx2, byb, color=INK, sw=1.4))
    capL, _, _ = textbox((bx1 + bx2) / 2, byb + 30, "мок на кожну залежність\nкожного правила — площа",
                         size=11, pad=8, fill="#ffffff", stroke=POS, sw=1.4, color=INK, bold=True)
    frags.append(capL)

    # роздільна вертикаль у порожньому проміжку
    frags.append(line(W / 2 + 30, 88, W / 2 + 30, H - 76, color=MUTED, sw=1.2, dash="4 5"))

    # ── ПРАВА панель: стовпчик N звірок, нуль мок-колонок ──
    frags.append(text(760, 66, "ЧИСТЕ ЯДРО: риштування = N", size=15, bold=True, color=FIELD))
    ox = 732
    frags.append(text(ox + cw / 2, gy - 12, "0 залежностей", size=11, color=FIELD))
    for i in range(Nrows):
        frags.append(rect(ox, gy + i * ch, cw, ch, fill="#f2faf5", stroke=FIELD, sw=1.2, rx=2))
        frags.append(text(ox - 18, gy + i * ch + ch / 2 + 4, "пр.%d" % (i + 1),
                          size=10, color=MUTED, anchor="end"))
    frags.append(line(ox, byb, ox + cw, byb, color=INK, sw=1.4))
    frags.append(line(ox, byb - 7, ox, byb, color=INK, sw=1.4))
    frags.append(line(ox + cw, byb - 7, ox + cw, byb, color=INK, sw=1.4))
    capR, _, _ = textbox(ox + cw / 2, byb + 30, "одна звірка списку\nна правило — лінія",
                         size=11, pad=8, fill="#ffffff", stroke=FIELD, sw=1.4, color=INK, bold=True)
    frags.append(capR)

    render(os.path.join(IMG, 'isolation-lattice.svg'), W, H, *frags,
           title="Риштування: площа N·D проти лінії N")


# ── Ширина покриття: шанс упіймати ваду проти числа входів ──
def fig_coverage_curve():
    import math
    W, H = 960, 540
    frags = []
    phi = 1e-4
    px0, px1 = 175, 835
    py0, py1 = 450, 96

    def xpix(k):  # k = log10(n), 1..6
        return px0 + (k - 1) / 5.0 * (px1 - px0)

    def ypix(p):
        return py0 - p * (py0 - py1)

    # осі
    frags.append(line(px0, py0, px1, py0, color=INK, sw=1.6))
    frags.append(line(px0, py0, px0, py1, color=INK, sw=1.6))

    sup = {1: "10¹", 2: "10²", 3: "10³", 4: "10⁴", 5: "10⁵", 6: "10⁶"}
    for k in range(1, 7):
        x = xpix(k)
        frags.append(line(x, py0, x, py0 + 7, color=INK, sw=1.2))   # засічка на осі
        frags.append(text(x, py0 + 24, sup[k], size=12, color=MUTED))
    for p, lab in [(0.0, "0"), (0.5, "50%"), (1.0, "100%")]:
        y = ypix(p)
        frags.append(line(px0 - 6, y, px0, y, color=INK, sw=1.2))   # засічка ліворуч
        frags.append(text(px0 - 14, y + 4, lab, size=11, color=MUTED, anchor="end"))

    # крива p = 1 − e^(−n·φ)
    pts = []
    kk = 1.0
    while kk <= 6.0001:
        p = 1 - math.exp(-(10 ** kk) * phi)
        pts.append("%.1f,%.1f" % (xpix(kk), ypix(p)))
        kk += 0.2
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pts), FIELD))

    # маркер «приклади» n=10²
    pe = 1 - math.exp(-(10 ** 2) * phi)
    frags.append(circle(xpix(2), ypix(pe), 5.5, fill=POS, stroke=POS, sw=1))
    # маркер «властивості» n=10⁵
    pp = 1 - math.exp(-(10 ** 5) * phi)
    frags.append(circle(xpix(5), ypix(pp), 5.5, fill=FIELD, stroke=FIELD, sw=1))

    anE, _, _ = textbox(xpix(2) + 8, 176, "приклади зі стендом\n~10² входів → ~1 %",
                        size=11, pad=8, fill="#ffffff", stroke=POS, sw=1.5, color=INK, bold=True)
    frags.append(anE)
    anP, _, _ = textbox(xpix(5) - 8, 322, "властивості над ядром\n~10⁵ входів → ~100 %",
                        size=11, pad=8, fill="#ffffff", stroke=FIELD, sw=1.5, color=INK, bold=True)
    frags.append(anP)

    frags.append(text(px0 + 4, py1 - 12, "шанс упіймати ваду", size=12, color=INK, anchor="start"))
    frags.append(text((px0 + px1) / 2, H - 30, "число перевірених входів n  (лог-шкала)",
                      size=12, color=INK))

    render(os.path.join(IMG, 'coverage-curve.svg'), W, H, *frags,
           title="Та сама вада φ = 10⁻⁴: 10² входів ловлять 1 %, 10⁵ — майже напевно")


# ── Щабель затримки: τ_cpu проти τ_io — і множник входів за той самий бюджет ──
def fig_latency_ladder():
    import math
    W, H = 1000, 470
    frags = []
    ax0, ax1 = 118, 900
    axy = 250
    span = 8.2

    def xL(ns):
        return ax0 + math.log10(ns) / span * (ax1 - ax0)

    frags.append(line(ax0, axy, ax1, axy, color=INK, sw=1.8))
    rungs = [
        (1,         "L1 / регістр", "~1 нс",   FIELD, True),
        (100,       "ОЗП",          "~100 нс", FIELD, False),
        (16000,     "SSD",          "~16 мкс", MUTED, True),
        (500000,    "датацентр",    "~0.5 мс", POS,   False),
        (10000000,  "диск (seek)",  "~10 мс",  POS,   True),
        (150000000, "материки",     "~150 мс", POS,   False),
    ]
    for ns, name, val, col, above in rungs:
        x = xL(ns)
        frags.append(line(x, axy - 7, x, axy + 7, color=col, sw=2.0))
        frags.append(circle(x, axy, 4, fill=col, stroke=col, sw=1))
        yy = axy - 56 if above else axy + 30
        tb, _, _ = textbox(x, yy, name + "\n" + val, size=10, pad=6,
                           fill="#ffffff", stroke=col, sw=1.3, color=INK, bold=True)
        frags.append(tb)

    frags.append(text(xL(6), axy + 96, "чистий тест ≈ τ_cpu", size=12, bold=True, color=FIELD))
    frags.append(text(xL(4500000), axy + 96, "тест зі світом ≈ τ_io", size=12, bold=True, color=POS))

    b1, b2 = xL(100), xL(500000)
    by = axy - 118
    frags.append(line(b1, by, b2, by, color=INK, sw=1.4))
    frags.append(line(b1, by, b1, by + 9, color=INK, sw=1.4))
    frags.append(line(b2, by, b2, by + 9, color=INK, sw=1.4))
    br, _, _ = textbox((b1 + b2) / 2, by - 16, "τ_io / τ_cpu ≈ 10³ … 10⁶",
                       size=12, pad=8, fill="#eef4ff", stroke=INK, sw=1.4, bold=True)
    frags.append(br)

    cap, _, _ = textbox(W / 2, H - 26,
                        "За той самий бюджет часу входів більше рівно в τ_io/τ_cpu разів",
                        size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'latency-ladder.svg'), W, H, *frags,
           title="Щабель затримки: чисте обчислення проти дотику до світу")


if __name__ == "__main__":
    fig_core_shell_flow()
    fig_where_mocks_attach()
    fig_sandwich()
    fig_boundaries_lineage()
    fig_channel_invariant()
    fig_hidden_inputs()
    fig_many_interpreters()
    fig_stale_snapshot()
    fig_examples_vs_property()
    fig_shrinking_funnel()
    fig_isolation_lattice()
    fig_coverage_curve()
    fig_latency_ladder()
    print("figures written to", IMG)
