# -*- coding: utf-8 -*-
"""Фігури до теми «Базові одиниці СІ».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: основні → похідні одиниці ──────────────────────────────────────
def fig_base_derived():
    W, H = 880, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Похідні одиниці — самі лише добутки й частки основних",
                  size=17, bold=True))

    # ── верхня смуга: похідні ──
    f.append(text(W / 2, 62, "ПОХІДНІ  (приклади)", size=12, color=MUTED, bold=True))
    derived = [
        ("м/с", "швидкість"),
        ("Н = кг·м/с²", "сила"),
        ("Дж = кг·м²/с²", "енергія"),
        ("Вт = кг·м²/с³", "потужність"),
        ("Па = кг/(м·с²)", "тиск"),
    ]
    n = len(derived)
    dw, gap = 150, 12
    total = n * dw + (n - 1) * gap
    x0 = (W - total) / 2
    dy, dh = 78, 62
    for i, (u, lab) in enumerate(derived):
        x = x0 + i * (dw + gap)
        f.append(fitbox(x, dy, dw, dh, u + "\n" + lab, size=14, pad=8,
                        fill="#eef6ef", stroke=FIELD, sw=1.4, color=INK, bold=True))

    # ── стрілка «будуються з» ──
    cx = W / 2
    f.append(arrow(cx, 258, cx, 156, color=INK, sw=3.2))
    b, w, h = textbox(cx + 132, 208, "будуються\nз основних", size=13, pad=9,
                      fill=FILL, stroke=LINE, sw=1.2, bold=False)
    f.append(b)

    # ── нижня смуга: сім основних ──
    f.append(text(W / 2, 292, "СІМ ОСНОВНИХ ОДИНИЦЬ", size=12, color=MUTED, bold=True))
    base = [("м", 1), ("кг", 1), ("с", 1), ("А", 0), ("К", 0), ("моль", 0), ("кд", 0)]
    bw, bgap = 96, 14
    tot2 = len(base) * bw + (len(base) - 1) * bgap
    bx0 = (W - tot2) / 2
    by, bh = 306, 52
    for i, (u, mech) in enumerate(base):
        x = bx0 + i * (bw + bgap)
        fill = "#eef6ef" if mech else "#eef2fb"
        stroke = FIELD if mech else NEG
        f.append(fitbox(x, by, bw, bh, u, size=18, pad=6,
                        fill=fill, stroke=stroke, sw=1.8, color=INK, bold=True))

    f.append(text(W / 2, H - 16,
                  "м · кг · с — уся механіка;   А · К · моль · кд — електрика, тепло, речовина, світло",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "base-derived-tree.svg"), W, H, *f)


# ── Фігура 2: сім сталих закріплюють сім одиниць ─────────────────────────────
def fig_constants():
    W, H = 900, 590
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Кожну одиницю закріплено точним значенням сталої природи",
                  size=17, bold=True))

    # заголовки колонок
    f.append(text(255, 66, "СТАЛА ПРИРОДИ (точне значення)", size=12, color=MUTED, bold=True))
    f.append(text(735, 66, "ЗАКРІПЛЮЄ ОДИНИЦЮ", size=12, color=MUTED, bold=True))

    rows = [
        ("Δν_Cs = 9192631770 Гц", "частота цезію-133", "секунда   с"),
        ("c = 299792458 м/с", "швидкість світла", "метр   м"),
        ("h = 6.62607015×10⁻³⁴ Дж·с", "стала Планка", "кілограм   кг"),
        ("e = 1.602176634×10⁻¹⁹ Кл", "заряд електрона", "ампер   А"),
        ("k = 1.380649×10⁻²³ Дж/К", "стала Больцмана", "кельвін   К"),
        ("Nₐ = 6.02214076×10²³ 1/моль", "стала Авогадро", "моль   моль"),
        ("K_cd = 683 лм/Вт", "світлова віддача", "кандела   кд"),
    ]
    lx, lw = 44, 430
    rx_, rw = 616, 244
    y0, rh, step = 84, 56, 64
    for i, (val, sub, unit) in enumerate(rows):
        y = y0 + i * step
        # ліва рамка — стала
        f.append(fitbox(lx, y, lw, rh, val + "\n" + sub, size=14, pad=9,
                        fill=FILL, stroke=LINE, sw=1.3, color=INK, bold=True))
        # стрілка
        f.append(arrow(lx + lw + 12, y + rh / 2, rx_ - 12, y + rh / 2, color=INK, sw=2.4))
        # права рамка — одиниця
        f.append(fitbox(rx_, y, rw, rh, unit, size=16, pad=8,
                        fill="#eef6ef", stroke=FIELD, sw=1.6, color=INK, bold=True))

    # нижня примітка — каскад
    b, w, h = textbox(W / 2, H - 30,
                      "Одиниці спираються одна на одну:  секунда → метр (через c) → кілограм (через h)",
                      size=14, pad=11, fill="#eef2fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "constants-to-units.svg"), W, H, *f)


# ── Фігура 3: метр крізь історію ─────────────────────────────────────────────
def fig_metre_timeline():
    W, H = 1040, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Метр: від розміру планети до сталої природи",
                  size=18, bold=True))

    spine_y = 118
    f.append(line(110, spine_y, 930, spine_y, color=MUTED, sw=2.4))

    nodes = [
        (160, "1793", INK, "1/10 000 000 чверті\nземного меридіана", "розмір планети", MUTED),
        (400, "1889", INK, "платино-іридієвий\nеталон-брусок", "предмет у сейфі", MUTED),
        (640, "1960", FIELD, "1 650 763.73 довжини\nхвилі криптону-86", "явище природи", FIELD),
        (880, "1983", NEG, "шлях світла за\n1/299792458 секунди", "стала природи", NEG),
    ]
    box_w, box_h = 214, 96
    for x, yr, col, desc, tag, tagcol in nodes:
        # вузол на осі
        f.append(circle(x, spine_y, 9, fill="#f4f6f8", stroke=col, sw=2.6))
        # рік над віссю
        f.append(text(x, spine_y - 22, yr, size=16, bold=True, color=col))
        # конектор вниз
        f.append(line(x, spine_y + 9, x, spine_y + 44, color=col, sw=1.6))
        # рамка-опис
        by = spine_y + 44
        tint = "#eef6ef" if col == FIELD else ("#eef2fb" if col == NEG else FILL)
        f.append(fitbox(x - box_w / 2, by, box_w, box_h, desc, size=14, pad=10,
                        fill=tint, stroke=col, sw=1.4, color=INK))
        # тег під рамкою
        f.append(text(x, by + box_h + 22, tag, size=13, bold=True, color=tagcol))

    # нижня вісь напряму
    ay = H - 40
    f.append(arrow(150, ay, 900, ay, color=INK, sw=2.0))
    f.append(text(150, ay - 12, "прив'язана до конкретного предмета", size=12,
                  color=MUTED, anchor="start"))
    f.append(text(900, ay - 12, "прив'язана до універсальної сталої", size=12,
                  color=MUTED, anchor="end"))
    return render(os.path.join(IMG, "metre-timeline.svg"), W, H, *f)


# ── Фігура 4 (вставка math): показники з розмірностей — маятник ──────────────
def fig_dim_pendulum():
    W, H = 800, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Розмірності пришпилюють показники: маятник",
                  size=18, bold=True))

    b, w, h = textbox(W / 2, 80, "T = C · ℓᵃ · mᵇ · gᶜ        (шукаємо a, b, c)",
                      size=16, pad=11, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)

    f.append(text(W / 2, 126,
                  "де [ℓ]=L,  [m]=M,  [g]=L·T⁻²  — і показники мусять збігтися:",
                  size=14, color=MUTED))

    rows = [
        "M :   0 = b            →   b = 0     (маса випадає)",
        "T :   1 = −2c          →   c = −½",
        "L :   0 = a + c        →   a = +½",
    ]
    rw = 660
    rx = (W - rw) / 2
    ry, rh, step = 152, 54, 66
    for i, r in enumerate(rows):
        y = ry + i * step
        tint = "#eef2fb" if i == 0 else FILL
        stroke = NEG if i == 0 else LINE
        f.append(fitbox(rx, y, rw, rh, r, size=17, pad=12,
                        fill=tint, stroke=stroke, sw=1.3, color=INK, bold=(i == 0)))

    b2, w2, h2 = textbox(W / 2, H - 44, "T = C · √( ℓ / g )", size=22, pad=14,
                         fill="#eef6ef", stroke=FIELD, sw=1.8, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "dim-pendulum-exponents.svg"), W, H, *f)


# ── Фігура 5 (вставка math): скільки безрозмірних груп — теорема π ────────────
def fig_dim_pi_count():
    W, H = 940, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Скільки безрозмірних комбінацій — стільки й невизначеності",
                  size=18, bold=True))

    panels = [
        (40, "Маятник:  T, ℓ, m, g", FIELD,
         ["величин із розмірністю   n = 4",
          "базових розмірностей     k = 3",
          "",
          "n − k = 1  безрозмірна група",
          "π₁ = T·√(g/ℓ) = стала"],
         "T = √(ℓ/g) · стала", "#eef6ef", FIELD),
        (490, "Додаємо амплітуду θ (безрозмірна)", NEG,
         ["π₁ = T·√(g/ℓ)      π₂ = θ",
          "груп тепер дві",
          "",
          "2 групи → π₁ = f(π₂)",
          "f — розмірностям не видна"],
         "T = √(ℓ/g) · f(θ)", "#eef2fb", NEG),
    ]
    pw, ph = 410, 300
    for x0, ttl, stroke, lines, concl, ctint, cstroke in panels:
        f.append(rect(x0, 66, pw, ph, fill="#fbfcfd", stroke=stroke, sw=1.4, rx=10))
        f.append(fitbox(x0 + 20, 82, pw - 40, 42, ttl, size=16, pad=8,
                        fill=FILL, stroke=stroke, sw=1.2, color=INK, bold=True))
        ly = 160
        for ln in lines:
            if ln == "":
                ly += 16
                continue
            big = ln.startswith("n − k") or ln.startswith("2 групи")
            f.append(text(x0 + pw / 2, ly, ln, size=17 if big else 15,
                          bold=big, color=INK if big else MUTED))
            ly += 34
        b, w, h = textbox(x0 + pw / 2, 66 + ph - 34, concl, size=18, pad=12,
                          fill=ctint, stroke=cstroke, sw=1.7, bold=True)
        f.append(b)

    f.append(text(W / 2, H - 14,
                  "одна група → відповідь з точністю до сталої;   більше груп → невизначена функція",
                  size=13, color=MUTED))
    return render(os.path.join(IMG, "dim-pi-count.svg"), W, H, *f)


# ── Фігура 6 (вставка hist): меридіанна дуга Дюнкерк — Барселона ──────────────
def fig_meridian_arc():
    W, H = 860, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Меридіанна дуга Дюнкерк — Барселона, з якої постав метр",
                  size=17, bold=True))

    sx = 326                                  # лінія меридіана
    y_dun, y_par, y_rod, y_bar = 86, 179, 375, 503
    y_top, y_bot, y45 = 78, 515, 346

    # компас
    f.append(text(sx, 66, "Пн", size=13, color=MUTED, bold=True))
    f.append(text(sx, 532, "Пд", size=13, color=MUTED, bold=True))

    # сам меридіан
    f.append(line(sx, y_top, sx, y_bot, color=MUTED, sw=1.9))

    # ланцюг трикутників (легкий зигзаг збоку)
    zys = [86, 132, 178, 224, 270, 316, 362, 408, 454, 503]
    zpts = [(302 if i % 2 == 0 else 350, y) for i, y in enumerate(zys)]
    for a, b in zip(zpts, zpts[1:]):
        f.append(line(a[0], a[1], b[0], b[1], color="#9aa3ad", sw=1.1))

    # ── ліворуч: дужки й підписи двох ділянок ──
    br = 250
    f.append(line(br, y_dun, br, y_rod, color=INK, sw=1.6))          # Деламбр (північ)
    f.append(line(br, y_dun, br + 12, y_dun, color=INK, sw=1.6))
    f.append(line(br, y_rod, br + 12, y_rod, color=INK, sw=1.6))
    b1, _, _ = textbox(150, 210, "Деламбр\nДюнкерк → Родез\n≈ 742 км",
                       size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b1)
    f.append(line(br, y_rod, br, y_bar, color=INK, sw=1.6))          # Мешен (південь)
    f.append(line(br, y_bar, br + 12, y_bar, color=INK, sw=1.6))
    b2, _, _ = textbox(150, 452, "Мешен\nРодез → Барселона\n≈ 333 км",
                       size=13, pad=10, fill="#eef2fb", stroke=NEG, sw=1.4, bold=True)
    f.append(b2)

    # ── лінія 45° (середина дуги) ──
    f.append(line(262, y45, 470, y45, color=FIELD, sw=1.6, dash="6 4"))
    f.append(mtext(478, y45 - 6, ["45° пн.ш.", "середина дуги"],
                   size=12, color=FIELD, anchor="start", bold=True))

    # ── вузли-міста на меридіані ──
    cities = [
        (y_dun, "Дюнкерк", "51° пн.ш., біля моря"),
        (y_par, "Париж", "меридіан через Обсерваторію"),
        (y_rod, "Родез", "стик двох ділянок"),
        (y_bar, "Барселона", "41° пн.ш., біля моря"),
    ]
    for y, name, sub in cities:
        f.append(circle(sx, y, 7, fill="#f4f6f8", stroke=INK, sw=2.2))
        f.append(text(366, y - 3, name, size=15, color=INK, anchor="start", bold=True))
        f.append(text(366, y + 15, sub, size=12, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "meridian-arc.svg"), W, H, *f)


# ── Фігура 7 (вставка proj): де ловиться сплутана одиниця ─────────────────────
def fig_unit_catch():
    W, H = 1040, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Де спиняється сплутана одиниця — залежно від підходу",
                  size=17, bold=True))

    # рубежі-заголовки + короткі позначки під ними
    f.append(text(205, 66, "написано", size=12, color=MUTED, bold=True))
    f.append(text(430, 66, "КОМПІЛЯЦІЯ", size=12, color=MUTED, bold=True))
    f.append(text(650, 66, "ВИКОНАННЯ (у польоті)", size=12, color=MUTED, bold=True))
    f.append(text(897, 66, "НАСЛІДОК", size=12, color=MUTED, bold=True))
    for x in (430, 650):
        f.append(line(x, 74, x, 92, color=MUTED, sw=1.2, dash="3,3"))

    xs, ox, ow = 205, 772, 252
    rows = [
        (155, POS,   "#fdecea", "голий double\n(без одиниці)",           None, None,
         "Марс: періапсида 57 км\nзамість 226 — зонд згоряє"),
        (255, NEG,   "#eaf0fd", "pint · одиниця в даних\n(рантайм)",      650,  "DimensionalityError",
         "спіймано —\nале вже в польоті"),
        (355, FIELD, "#eef6ef", "одиниця в типі\n(newtype / показники)",  430,  "не компілюється",
         "спинено до запуску —\nправка за секунди"),
    ]
    for yc, col, tint, appr, wx, wlab, outc in rows:
        # ліворуч — підхід
        f.append(fitbox(14, yc - 30, 188, 60, appr, size=13, pad=8,
                        fill=FILL, stroke=col, sw=1.6, color=INK, bold=True))
        if wx is None:                                                   # без стіни — до кінця
            f.append(arrow(xs, yc, ox - 10, yc, color=col, sw=3.0))
        else:                                                            # стіна на рубежі лову
            f.append(arrow(xs, yc, wx, yc, color=col, sw=3.0))
            f.append(rect(wx - 4, yc - 24, 8, 48, fill=col, stroke=col, sw=0, rx=2))
            b, w, h = textbox(wx, yc - 46, wlab, size=12, pad=7,
                              fill=tint, stroke=col, sw=1.2, bold=True, color=INK)
            f.append(b)
            f.append(line(wx + 6, yc, ox - 10, yc, color=col, sw=1.4, dash="4,4"))
        # праворуч — наслідок
        f.append(fitbox(ox, yc - 30, ow, 60, outc, size=13, pad=9,
                        fill=tint, stroke=col, sw=1.7, color=INK, bold=True))

    f.append(text(W / 2, H - 16,
                  "Що раніший рубіж лову — то дешевша ціна помилки.",
                  size=13, color=MUTED))
    return render(os.path.join(IMG, "unit-catch.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_base_derived(), fig_constants(), fig_metre_timeline(),
          fig_dim_pendulum(), fig_dim_pi_count(), fig_meridian_arc(),
          fig_unit_catch()]
    print("written:")
    for p in ps:
        print("  ", p)
