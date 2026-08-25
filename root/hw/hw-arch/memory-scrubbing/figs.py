# -*- coding: utf-8 -*-
"""Фігури до теми «Memory scrubbing: фоновий ремонт пам'яті».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b9770e"   # виправний / контроль (тепле)
GOOD  = "#1e874b"   # чисте, полагоджене


def word_cells(x0, y0, cw, ch, flips):
    """8 клітинок слова; індекси у flips — перекинуті (червоні)."""
    out = []
    for i in range(8):
        x = x0 + i * (cw + 2)
        if i in flips:
            out.append(rect(x, y0, cw, ch, fill="#fdeceb", stroke=POS, sw=1.6, rx=2))
            out.append(text(x + cw / 2, y0 + ch * 0.72, "1", size=13, color=POS, bold=True))
        else:
            out.append(rect(x, y0, cw, ch, fill="#eaf0fd", stroke=NEG, sw=1.0, rx=2))
    return out, x0 + 8 * (cw + 2) - 2


# ── 1. Латентна помилка як бомба з годинником; очищення її знешкоджує ──────────
def fig_timebomb():
    W, H = 900, 470
    f = [text(W / 2, 30, "Латентна помилка — бомба з годинником, і як її знешкоджує очищення",
              size=16, bold=True)]
    f.append(text(W / 2, 52, "перший виправний збій висить у слові й чекає на пару; що коротше він живе, то безпечніше",
                  size=11, color=MUTED, italic=True))

    cw, ch = 20, 26
    axL, axR = 250, 850     # часова вісь
    # ── ВЕРХНІЙ рядок: без очищення ──
    yb = 108
    f.append(text(40, yb - 6, "БЕЗ очищення", size=13, color=POS, bold=True, anchor="start"))
    f.append(line(axL, yb + 40, axR, yb + 40, color=MUTED, sw=1.2))
    f.append(text(axR, yb + 58, "час →", size=10.5, color=MUTED, anchor="end"))
    # стан 1: чисте
    cells, _ = word_cells(40, yb + 24, cw, ch, [])
    f.extend(cells)
    f.append(text(120, yb + 78, "слово чисте", size=10, color=MUTED))
    # подія A: перший збій
    ax = 330
    f.append(line(ax, yb + 20, ax, yb + 40, color=POS, sw=1.4, dash="3 3"))
    f.append(text(ax, yb + 14, "1-й збій", size=10.5, color=POS, bold=True))
    cellsA, endA = word_cells(ax - 92, yb + 46, cw, ch, [3])
    f.extend(cellsA)
    f.append(text(ax - 4, yb + 92, "виправний — але висить місяцями", size=10, color=AMBER, anchor="middle"))
    # подія B: другий збій
    bx = 690
    f.append(line(bx, yb + 20, bx, yb + 40, color=POS, sw=1.4, dash="3 3"))
    f.append(text(bx, yb + 14, "2-й збій", size=10.5, color=POS, bold=True))
    cellsB, endB = word_cells(bx - 92, yb + 46, cw, ch, [3, 6])
    f.extend(cellsB)
    f.append(fitbox(bx + 24, yb + 46, 150, 30, "НЕВИПРАВНА\nпомилка", size=11, color=POS, bold=True,
                    fill="#fdeceb", stroke=POS, sw=1.8))

    # ── НИЖНІЙ рядок: з очищенням ──
    yb2 = 300
    f.append(text(40, yb2 - 6, "З очищенням", size=13, color=GOOD, bold=True, anchor="start"))
    f.append(line(axL, yb2 + 40, axR, yb2 + 40, color=MUTED, sw=1.2))
    f.append(text(axR, yb2 + 58, "час →", size=10.5, color=MUTED, anchor="end"))
    cells0, _ = word_cells(40, yb2 + 24, cw, ch, [])
    f.extend(cells0)
    f.append(text(120, yb2 + 78, "слово чисте", size=10, color=MUTED))
    # подія A: перший збій
    f.append(line(ax, yb2 + 20, ax, yb2 + 40, color=POS, sw=1.4, dash="3 3"))
    f.append(text(ax, yb2 + 14, "1-й збій", size=10.5, color=POS, bold=True))
    cellsA2, _ = word_cells(ax - 92, yb2 + 46, cw, ch, [3])
    f.extend(cellsA2)
    # прохід очищення
    sx = 520
    f.append(line(sx, yb2 + 20, sx, yb2 + 40, color=GOOD, sw=1.8))
    f.append(text(sx, yb2 + 14, "прохід очищення", size=10.5, color=GOOD, bold=True))
    cellsS, _ = word_cells(sx - 84, yb2 + 46, cw, ch, [])
    f.extend(cellsS)
    f.append(text(sx - 4, yb2 + 92, "прочитав, виправив, записав назад → чисте", size=10, color=GOOD, anchor="middle"))
    # подія B: другий збій — на чисте слово
    f.append(line(bx, yb2 + 20, bx, yb2 + 40, color=POS, sw=1.4, dash="3 3"))
    f.append(text(bx, yb2 + 14, "2-й збій", size=10.5, color=POS, bold=True))
    cellsB2, _ = word_cells(bx - 92, yb2 + 46, cw, ch, [6])
    f.extend(cellsB2)
    f.append(fitbox(bx + 24, yb2 + 46, 150, 30, "знову лише 1\n→ ВИПРАВНА", size=11, color=GOOD, bold=True,
                    fill="#e9f7ef", stroke=GOOD, sw=1.8))

    f.append(text(W / 2, 448,
                  "очищення не робить код сильнішим — воно не дає двом поодиноким збоям зустрітися в одному слові",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "latent-timebomb.svg"), W, H, *f)


# ── 2. Регенерація зберігає значення (з помилкою), очищення виправляє ──────────
def fig_refresh_vs_scrub():
    W, H = 907, 430
    f = [text(W / 2, 30, "Регенерація — не очищення: одна тримає заряд, друга тримає правду",
              size=16, bold=True)]
    f.append(text(W / 2, 52, "обидва цикли читають слово й пишуть назад — різниця в тому, що робиться МІЖ цим",
                  size=11, color=MUTED, italic=True))

    cw, ch = 22, 30

    def cycle(y, title, col, corrects):
        out = [text(60, y + 4, title, size=13.5, color=col, bold=True, anchor="start")]
        # слово-вхід з перекинутим бітом
        cells, endx = word_cells(60, y + 20, cw, ch, [4])
        out.extend(cells)
        out.append(text(60 + 4 * (cw + 2) + cw / 2, y + 68, "перекинутий біт", size=9.5, color=POS))
        # стрілка → зчитування
        out.append(arrow(endx + 10, y + 35, endx + 46, y + 35, color=INK, sw=1.8))
        # блок «між»
        bx = endx + 56
        if corrects:
            out.append(fitbox(bx, y + 12, 220, 46, "код виправлення:\nзвіряє з контролем, лагодить біт",
                              size=11, color=GOOD, bold=True, fill="#e9f7ef", stroke=GOOD, sw=1.8))
        else:
            out.append(fitbox(bx, y + 12, 220, 46, "лише підсилювач зчитування:\nщо намацав, те й віддає",
                              size=11, color=AMBER, bold=True, fill="#fdf3e0", stroke=AMBER, sw=1.8))
        # стрілка → запис назад
        out.append(arrow(bx + 230, y + 35, bx + 266, y + 35, color=INK, sw=1.8))
        # слово-вихід
        ox = bx + 276
        flips = [] if corrects else [4]
        cells2, oend = word_cells(ox, y + 20, cw, ch, flips)
        out.extend(cells2)
        if corrects:
            out.append(text(oend + 12, y + 40, "✓ полагоджено", size=11.5, color=GOOD, bold=True, anchor="start"))
        else:
            out.append(text(oend + 12, y + 40, "✗ помилка лишилась", size=11.5, color=POS, bold=True, anchor="start"))
        return out

    f.extend(cycle(120, "РЕГЕНЕРАЦІЯ (refresh): підновлює заряд", AMBER, corrects=False))
    f.append(line(50, 232, W - 50, 232, color="#e0e0e0", sw=1.2))
    f.extend(cycle(272, "ОЧИЩЕННЯ (scrub): відновлює значення", GOOD, corrects=True))

    f.append(text(W / 2, 400,
                  "тому пам'ять може справно регенеруватися роками й усе одно накопичувати латентні помилки",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "refresh-vs-scrub.svg"), W, H, *f)


# ── 3. Патрульне (фоновий обхід усього) проти очищення на вимогу ───────────────
def fig_patrol_vs_demand():
    W, H = 880, 440
    f = [text(W / 2, 30, "Два різновиди: патрульне прочісує все, на вимогу лагодить те, чого торкнулись",
              size=15.5, bold=True)]

    # спільна смуга пам'яті
    x0, cw, n = 70, 46, 15
    def mem_strip(y, hot=None, scanned=None, fixed=None, label=""):
        out = [text(60, y - 8, label, size=12.5, bold=True, anchor="start")]
        for i in range(n):
            x = x0 + i * (cw + 4)
            fill, stroke, sw = "#eaf0fd", NEG, 1.0
            if scanned is not None and i < scanned:
                fill, stroke, sw = "#e9f7ef", GOOD, 1.2   # уже пройдено
            if fixed is not None and i == fixed:
                fill, stroke, sw = "#e9f7ef", GOOD, 2.0
            if hot is not None and i == hot:
                fill, stroke, sw = "#fdeceb", POS, 2.0
            out.append(rect(x, y, cw, 40, fill=fill, stroke=stroke, sw=sw, rx=4))
        return out

    # ── патрульне ──
    yp = 96
    f.extend(mem_strip(yp, scanned=8, label="Патрульне — фоновий обхід УСІЄЇ пам'яті адреса за адресою"))
    cur = x0 + 8 * (cw + 4) + cw / 2
    f.append(line(cur, yp - 4, cur, yp + 44, color=GOOD, sw=2.4))
    f.append(arrow(cur - 30, yp + 62, cur + 26, yp + 62, color=GOOD, sw=2))
    f.append(text(cur - 2, yp + 80, "курсор іде далі", size=10.5, color=GOOD))
    f.append(text(x0 + 3.5 * (cw + 4), yp + 62, "уже почищено", size=10, color=GOOD))
    f.append(text(x0 + 12 * (cw + 4), yp + 62, "черга попереду", size=10, color=MUTED))
    f.append(text(60, yp + 108, "дістає навіть ХОЛОДНІ слова, до яких програма не звертається роками — гарантований повний прохід за заданий час",
                  size=10.5, color=MUTED, anchor="start", italic=True))

    f.append(line(50, yp + 132, W - 50, yp + 132, color="#e0e0e0", sw=1.2))

    # ── на вимогу ──
    yd = 290
    f.extend(mem_strip(yd, hot=6, fixed=6, label="На вимогу — лише там, де ЗВИЧАЙНЕ читання знайшло виправний збій"))
    hx = x0 + 6 * (cw + 4) + cw / 2
    f.append(arrow(hx, yd - 30, hx, yd - 6, color=INK, sw=2))
    f.append(text(hx, yd - 36, "звичайне читання програми", size=10.5, color=INK, bold=True))
    f.append(text(hx, yd + 62, "знайшло збій → одразу запис назад полагодженого", size=10.5, color=GOOD, bold=True))
    f.append(text(60, yd + 92, "дешево (слово й так прочитали), але лагодить лише ГАРЯЧІ дані, до яких торкнулись — холодні лишає патрулю",
                  size=10.5, color=MUTED, anchor="start", italic=True))

    f.append(text(W / 2, yd + 128, "разом вони покривають і холодні дані (патруль), і гарячі (вимога)",
                  size=11, color=INK, italic=True))
    render(os.path.join(IMG, "patrol-vs-demand.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки math-scrub-race.md
# ══════════════════════════════════════════════════════════════════════════════

# ── 4. Вікно експозиції: той самий потік збоїв, два різні присуди ─────────────
def fig_scrub_window():
    W, H = 940, 500
    f = [text(W / 2, 32, "Вікно експозиції: той самий потік збоїв — два різні присуди",
              size=16, bold=True)]
    f.append(text(W / 2, 54, "одне слово, ті самі шість влучань у ті самі моменти; різниця лише в тому, чи хтось прибирає між ними",
                  size=11, color=MUTED, italic=True))

    axL, axR = 120, 880
    span = axR - axL
    hits = [0.08, 0.25, 0.42, 0.58, 0.75, 0.90]      # моменти влучань (частка місії)
    hx = [axL + h * span for h in hits]

    def tick(x, y, color, label=None):
        out = [line(x, y - 20, x, y, color=color, sw=2.0)]
        out.append(circle(x, y - 26, 5.5, fill="#fdeceb", stroke=color, sw=2.0))
        if label:
            out.append(text(x, y - 40, label, size=10, color=color, bold=True))
        return out

    # ── ВЕРХНІЙ рядок: без очищення ──
    yb = 148
    f.append(text(axL, yb - 78, "БЕЗ очищення — вікно дорівнює всьому часу роботи",
                  size=13, color=POS, bold=True, anchor="start"))
    f.append(line(axL, yb, axR, yb, color=MUTED, sw=1.4))
    f.append(text(axR + 4, yb + 5, "час →", size=10.5, color=MUTED, anchor="start"))
    for i, x in enumerate(hx):
        f.extend(tick(x, yb, POS))
    # дужка вікна
    f.append(line(axL, yb + 24, axR, yb + 24, color=POS, sw=1.4, dash="5 4"))
    f.append(line(axL, yb + 18, axL, yb + 30, color=POS, sw=1.4))
    f.append(line(axR, yb + 18, axR, yb + 30, color=POS, sw=1.4))
    f.append(text((axL + axR) / 2, yb + 44, "одне вікно на всю місію — збої НІКОЛИ не прибирають, вони просто накопичуються",
                  size=11, color=POS, bold=True))
    # фатальна пара
    f.append(line(hx[0], yb - 52, hx[1], yb - 52, color=POS, sw=2.4))
    f.append(text((hx[0] + hx[1]) / 2, yb - 60, "ця пара вбиває", size=11, color=POS, bold=True))
    f.append(text(hx[1] + 26, yb - 26, "← слово мертве вже тут: два збої співіснують", size=11, color=POS,
                  bold=True, anchor="start"))

    f.append(line(50, 246, W - 50, 246, color="#e0e0e0", sw=1.2))

    # ── НИЖНІЙ рядок: з очищенням ──
    ys = 350
    f.append(text(axL, ys - 78, "З очищенням — вікно вкорочене до періоду проходу T",
                  size=13, color=GOOD, bold=True, anchor="start"))
    f.append(line(axL, ys, axR, ys, color=MUTED, sw=1.4))
    f.append(text(axR + 4, ys + 5, "час →", size=10.5, color=MUTED, anchor="start"))
    # межі проходів
    edges = [axL + k / 6.0 * span for k in range(7)]
    for e in edges:
        f.append(line(e, ys - 46, e, ys + 22, color=GOOD, sw=1.4, dash="4 3"))
    for k in range(6):
        mid = (edges[k] + edges[k + 1]) / 2
        f.append(text(mid, ys + 38, "T", size=11, color=GOOD, bold=True))
    for x in hx:
        f.extend(tick(x, ys, POS))
    for e in edges[1:]:
        f.append(circle(e, ys, 4.5, fill=GOOD, stroke=GOOD, sw=1.2))
    f.append(text(axL, ys - 58, "прохід очищення обнуляє слово на кожній межі ↓",
                  size=10.5, color=GOOD, bold=True, anchor="start"))
    f.append(text((axL + axR) / 2, ys + 66,
                  "кожен збій самотній у своєму вікні — код виправляє його, прохід стирає; жодна пара не зустрілась",
                  size=11, color=GOOD, bold=True))

    f.append(text(W / 2, H - 22,
                  "Фізика однакова: шість збоїв, ті самі моменти. Фатальна лише пара В ОДНОМУ вікні — тому ризик тягне не λ, а λ·(довжина вікна).",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "scrub-window.svg"), W, H, *f)


# ── 5. Квадрат проти прямої: очищення міняє ФОРМУ кривої ──────────────────────
def fig_quadratic_vs_linear():
    import math
    W, H = 900, 600
    f = [text(W / 2, 32, "Очищення міняє не сталу, а ФОРМУ кривої ризику",
              size=16, bold=True)]
    f.append(text(W / 2, 54, "32 ГіБ ECC-пам'яті, 1000 FIT/Мбіт; обидві осі логарифмічні",
                  size=11, color=MUTED, italic=True))

    # поле графіка
    gx0, gx1 = 150, 830          # log10(t): 0 … 5
    gy0, gy1 = 470, 100          # log10(P): −12 (низ) … 0 (верх)

    def px(L):
        return gx0 + L / 5.0 * (gx1 - gx0)

    def py(L):
        return gy0 + (L + 12.0) / 12.0 * (gy1 - gy0)

    # осі + короткі засічки (СУЦІЛЬНОЇ сітки немає: лінії не сміють різати написи)
    f.append(line(gx0, gy0, gx1, gy0, color=INK, sw=1.6))
    f.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.6))
    for d in range(0, 6):
        f.append(line(px(d), gy0, px(d), gy0 - 6, color=INK, sw=1.2))
    for d in range(-12, 1, 2):
        f.append(line(gx0, py(d), gx0 + 6, py(d), color=INK, sw=1.2))

    # підписи осей
    xlab = {0: "1 год", 1: "10 год", 2: "100 год", 3: "1000 год", 4: "10⁴ год", 5: "10⁵ год"}
    for d in range(0, 6):
        f.append(text(px(d), gy0 + 20, xlab[d], size=10.5, color=MUTED))
    f.append(text((gx0 + gx1) / 2, gy0 + 44, "час роботи t (логарифм)", size=12, color=INK, bold=True))
    ylab = {-12: "10⁻¹²", -10: "10⁻¹⁰", -8: "10⁻⁸", -6: "10⁻⁶", -4: "10⁻⁴", -2: "10⁻²", 0: "10⁰"}
    for d in range(-12, 1, 2):
        f.append(text(gx0 - 12, py(d) + 4, ylab[d], size=10.5, color=MUTED, anchor="end"))
    f.append(text(gx0 - 50, gy1 - 12, "P(невиправна) на всю пам'ять", size=12, color=INK,
                  bold=True, anchor="start"))

    # криві:  без очищення  log P = −10.953 + 2L ;  з очищенням  log P = −9.573 + L
    A, B = -10.953, -9.573
    f.append(line(px(0), py(A), px(5), py(A + 10), color=POS, sw=2.6))
    f.append(line(px(0), py(B), px(5), py(B + 5), color=GOOD, sw=2.6))

    # ── точка перетину t = T = 24 год (напис у порожньому верхньому-лівому куті) ──
    LT = math.log10(24.0)
    xT, yT = px(LT), py(A + 2 * LT)
    f.append(circle(xT, yT, 5.5, fill=BG, stroke=INK, sw=2.0))
    f.append(line(300, 196, xT - 4, yT - 8, color=INK, sw=1.2))
    f.append(mtext(180, 158, ["криві сходяться при t = T = 24 год:",
                              "до першого проходу очищення",
                              "ще нічого не купило"],
                   size=10.5, color=INK, anchor="start", lh=1.25))

    # ── вертикальний розрив на 6 місяцях ──
    L6 = math.log10(4320.0)
    x6, y_ns, y_s = px(L6), py(A + 2 * L6), py(B + L6)
    f.append(line(x6, gy0, x6, y_s, color=MUTED, sw=1.2, dash="4 3"))
    f.append(arrow(x6, y_s - 3, x6, y_ns + 3, color=INK, sw=2.0))
    f.append(arrow(x6, y_ns + 3, x6, y_s - 3, color=INK, sw=2.0))
    f.append(text(x6 + 9, (y_ns + y_s) / 2 + 4, "×180 = t / T", size=11, color=AMBER,
                  bold=True, anchor="start"))
    f.append(text(x6, gy0 + 20, "6 місяців", size=9.5, color=INK, bold=True))

    # ── підписи кривих (у порожніх зонах: над червоною, під зеленою) ──
    f.append(text(730, 137, "нахил 2 — ризик РОЗГАНЯЄТЬСЯ", size=10.5, color=POS,
                  anchor="end", italic=True))
    f.append(text(730, 155, "без очищення:  P ∝ t²", size=12.5, color=POS, bold=True, anchor="end"))
    f.append(text(620, 345, "з очищенням:  P ∝ T·t", size=12.5, color=GOOD, bold=True, anchor="end"))
    f.append(text(620, 363, "нахил 1 — стала небезпека", size=10.5, color=GOOD,
                  anchor="end", italic=True))

    f.append(text(W / 2, 552,
                  "Без очищення вікно росте разом із місією — тому крива квадратична й задирається.",
                  size=11.5, color=INK, italic=True))
    f.append(text(W / 2, 574,
                  "Очищення підрізає вікно до сталої T — крива стає прямою, а розрив шириться як t/T.",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "quadratic-vs-linear.svg"), W, H, *f)


# ── 6. Драбина MTTF: коротше вікно проти сильнішого коду ──────────────────────
def fig_mttf_ladder():
    import math
    W, H = 960, 470
    f = [text(W / 2, 32, "Що дешевше купує надійність — сильніший код чи коротше вікно",
              size=16, bold=True)]
    f.append(text(W / 2, 54, "середній час до невиправної помилки, 32 ГіБ ECC-пам'яті, 1000 FIT/Мбіт",
                  size=11, color=MUTED, italic=True))

    bx0, bx1 = 330, 900          # log10(років): 1 … 8
    LY0, LY1 = 1.0, 8.0

    def bx(L):
        return bx0 + (L - LY0) / (LY1 - LY0) * (bx1 - bx0)

    rows = [
        ("SECDED, без очищення",        "8 контрольних бітів (+12.5%)",      30.3,      1.48, POS),
        ("DEC-TED, без очищення",       "15 бітів (+23%), декод у кілька тактів", 1582.0, 3.20, AMBER),
        ("SECDED + очищення T = 24 год", "0 зайвих бітів — лише розклад",     427000.0,  5.63, GOOD),
        ("SECDED + очищення T = 1 год",  "0 зайвих бітів — лише розклад",     1.03e7,    7.01, GOOD),
    ]

    # сітка декад
    for d in range(1, 9):
        x = bx(d)
        f.append(line(x, 96, x, 380, color="#ececec", sw=1.0))
        f.append(text(x, 398, "10%s років" % ("¹" if d == 1 else "²" if d == 2 else "³" if d == 3 else
                                              "⁴" if d == 4 else "⁵" if d == 5 else "⁶" if d == 6 else
                                              "⁷" if d == 7 else "⁸"),
                      size=10, color=MUTED))
    f.append(line(bx0, 96, bx0, 380, color=INK, sw=1.6))

    y = 128
    for name, cost, val, L, col in rows:
        f.append(text(bx0 - 16, y + 5, name, size=12, color=INK, bold=True, anchor="end"))
        f.append(text(bx0 - 16, y + 23, cost, size=10, color=MUTED, anchor="end", italic=True))
        f.append(rect(bx0, y - 10, bx(L) - bx0, 30, fill=col, stroke=col, sw=1.0, rx=3))
        lab = ("%.0f років" % val) if val < 1e4 else ("%.0f тис. років" % (val / 1e3) if val < 1e6
                                                      else "%.1f млн років" % (val / 1e6))
        f.append(text(bx(L) + 12, y + 9, lab, size=12, color=col, bold=True, anchor="start"))
        y += 64

    # порівняльні дужки
    f.append(text(W / 2, 424,
                  "Сильніший код: +23% бітів, повільніше читання — і лише ×52.   Коротше вікно: нуль бітів, сама лише регулярність — ×14 000.",
                  size=12, color=INK, bold=True))
    f.append(text(W / 2, 446,
                  "Очищене SECDED переганяє неочищене DEC-TED у 270 разів — і не коштує жодного біта.",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "mttf-ladder.svg"), W, H, *f)


def _ok_mark(cx, cy):
    return (circle(cx, cy, 13, fill="#e8f6ee", stroke=GOOD, sw=2) +
            text(cx, cy + 5, "✓", size=15, color=GOOD, bold=True))


def _stop_mark(cx, cy):
    return (line(cx, cy - 34, cx, cy - 17, color=POS, sw=6) +
            line(cx, cy + 17, cx, cy + 34, color=POS, sw=6) +
            circle(cx, cy, 13, fill="#fdeceb", stroke=POS, sw=2) +
            text(cx, cy + 5, "✗", size=14, color=POS, bold=True))


# ── 7. Три бар'єри між читанням у коді й логікою ECC ──────────────────────────
def fig_read_barriers():
    W, H = 1000, 566
    f = [text(W / 2, 30, "Три бар'єри між читанням у коді й логікою ECC", size=16, bold=True)]
    f.append(text(W / 2, 52, "слово перевіряється лише тоді, коли його справді віддає SRAM — а туди ще треба дійти",
                  size=11, color=MUTED, italic=True))

    BY0, BH, BW = 76, 420, 150
    bands = [(265, "1. КОМПІЛЯТОР", "викидає читання,", "чий результат не вжито"),
             (445, "2. КЕШ", "влучання віддає копію,", "не турбуючи SRAM"),
             (625, "3. ЛОГІКА ECC", "звіряє гранулу", "з контрольними бітами")]
    for bx, name, d1, d2 in bands:
        f.append(rect(bx, BY0, BW, BH, fill="#f7f8fa", stroke="#d8dce3", sw=1.2, rx=8))
        f.append(text(bx + BW / 2, BY0 + 26, name, size=12, bold=True))
        f.append(text(bx + BW / 2, BY0 + 46, d1, size=10, color=MUTED))
        f.append(text(bx + BW / 2, BY0 + 62, d2, size=10, color=MUTED))

    # права колонка — сама пам'ять
    SX, SW_ = 815, 165
    f.append(rect(SX, BY0, SW_, BH, fill="#fbfcfd", stroke=NEG, sw=1.6, rx=8))
    f.append(text(SX + SW_ / 2, BY0 + 26, "SRAM", size=12, bold=True, color=NEG))
    f.append(text(SX + SW_ / 2, BY0 + 46, "комірки + біти ECC", size=10, color=MUTED))

    rows = [(210, "НАЇВНО", ["uint64_t x = ram[i];", "результат нікуди не йде"], 0),
            (320, "VOLATILE, АЛЕ КЕШОВАНО", ["(void)*(volatile uint64_t *)a;", "рядок уже лежить у кеші"], 1),
            (430, "ЯК ТРЕБА", ["скинути рядок кешу, тоді", "(void)*(volatile uint64_t *)a;"], 2)]
    verdicts = ["ВИКИНУТО", "ВЛУЧАННЯ В КЕШ", "ЧИТАННЯ ДІЙШЛО"]
    hints = ["у бінарнику читання нема", "до SRAM запит не пішов", "гранулу перевірено"]

    for y, tag, code, reach in rows:
        col = GOOD if reach == 2 else POS
        f.append(text(20, y - 40, tag, size=11, color=col, bold=True, anchor="start"))
        f.append(fitbox(20, y - 28, 225, 56, "\n".join(code), size=11, pad=7,
                        fill="#ffffff", stroke=MUTED, sw=1.2))
        # шлях крізь бар'єри
        prev = 248
        for k in range(3):
            bx = bands[k][0]
            cx = bx + BW / 2
            if k < reach or reach == 2:
                f.append(arrow(prev, y, cx - 16, y, color=GOOD, sw=1.8))
                f.append(_ok_mark(cx, y))
                prev = cx + 16
            else:
                f.append(arrow(prev, y, cx - 18, y, color=POS, sw=1.8))
                f.append(_stop_mark(cx, y))
                f.append(text(cx, y + 56, verdicts[reach], size=11, color=POS, bold=True))
                f.append(text(cx, y + 72, hints[reach], size=10, color=MUTED))
                prev = None
                break
        if prev is not None:
            f.append(arrow(prev, y, SX - 8, y, color=GOOD, sw=1.8))
            cells, _ = word_cells(SX + 16, y - 13, 15, 26, [4])
            f.extend(cells)
            f.append(text(SX + SW_ / 2, y + 40, verdicts[2], size=11, color=GOOD, bold=True))
            f.append(text(SX + SW_ / 2, y + 56, hints[2], size=10, color=MUTED))

    f.append(text(W / 2, 522,
                  "Наївне читання не переживає навіть компілятора. Volatile-читання компілятор лишає — та кеш віддає копію,",
                  size=11.5, color=INK))
    f.append(text(W / 2, 542,
                  "і SRAM про запит не дізнається. Лише скинутий рядок змушує пам'ять віддати справжнє слово — тоді ECC його й перевірить.",
                  size=11.5, color=INK))
    render(os.path.join(IMG, "scrub-read-barriers.svg"), W, H, *f)


# ── 8. Бюджет тіка: та сама праця, різна затримка ────────────────────────────
def fig_tick_budget():
    W, H = 1000, 496
    f = [text(W / 2, 30, "Одна робота, дві затримки: навіщо очищення нарізають на тіки", size=16, bold=True)]
    f.append(text(W / 2, 52, "вікно у 8 мс із життя системи: тік таймера — 1 мс, ядро — 200 МГц, повний прохід — за 60 с",
                  size=11, color=MUTED, italic=True))

    x0, slot, n = 140, 88, 8
    xe = x0 + n * slot

    def timeline(y, label, col):
        g = [text(20, y - 46, label, size=12, color=col, bold=True, anchor="start")]
        for i in range(n):
            x = x0 + i * slot
            g.append(rect(x, y - 28, slot, 56, fill="#fbfbfc", stroke="#e2e5ea", sw=1.0, rx=3))
            g.append(line(x, y - 44, x, y - 31, color=MUTED, sw=1.0, dash="2 3"))
            g.append(text(x + slot / 2, y + 52, "тік %d" % (i + 1), size=10, color=MUTED))
        g.append(line(xe, y - 44, xe, y - 31, color=MUTED, sw=1.0, dash="2 3"))
        return g

    # ── ВЕРХ: одним махом ──
    y1 = 148
    f.extend(timeline(y1, "ОДНИМ МАХОМ", POS))
    f.append(rect(x0 + 5, y1 - 22, 34, 44, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
    lump_w = 3.3 * slot
    f.append(rect(x0 + 44, y1 - 22, lump_w, 44, fill="#fdeceb", stroke=POS, sw=1.8, rx=3))
    f.append(text(x0 + 44 + lump_w / 2, y1 + 4, "очищення все за раз — 3.3 мс", size=11.5, color=POS, bold=True))
    f.append(text(x0 + 2.4 * slot, y1 + 76, "три тіки поспіль застосунок не дістав процесора — керування зірвано",
                  size=10.5, color=POS, anchor="middle"))
    f.append(text(940, y1 - 12, "найгірша", size=10, color=MUTED))
    f.append(text(940, y1 + 6, "пауза", size=10, color=MUTED))
    f.append(text(940, y1 + 26, "3.3 мс", size=13, color=POS, bold=True))

    # ── НИЗ: по бюджету на тік ──
    y2 = 306
    f.extend(timeline(y2, "ПО БЮДЖЕТУ НА ТІК", GOOD))
    for i in range(n):
        x = x0 + i * slot
        f.append(rect(x + 5, y2 - 22, 34, 44, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
        f.append(rect(x + 44, y2 - 22, 3, 44, fill="#fdeceb", stroke=POS, sw=1.2, rx=1))
    f.append(text(x0 + 3.6 * slot, y2 + 76, "червоні волосини між блоками — і є очищення: 55 нс на тік, кожен тік устигає все",
                  size=10.5, color=INK, anchor="middle"))
    f.append(text(940, y2 - 12, "найгірша", size=10, color=MUTED))
    f.append(text(940, y2 + 6, "пауза", size=10, color=MUTED))
    f.append(text(940, y2 + 26, "55 нс", size=13, color=GOOD, bold=True))

    # легенда
    f.append(rect(140, 398, 16, 14, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
    f.append(text(164, 410, "робота застосунку", size=10.5, color=MUTED, anchor="start"))
    f.append(rect(300, 398, 16, 14, fill="#fdeceb", stroke=POS, sw=1.2, rx=2))
    f.append(text(324, 410, "робота очищення", size=10.5, color=MUTED, anchor="start"))

    f.append(text(W / 2, 452,
                  "Праця однакова: 65536 гранул ≈ 0.66 млн тактів ≈ 3.3 мс на прохід, тобто 0.0055% ядра. Обидва варіанти доходять до кінця рівно за 60 с.",
                  size=11.5, color=INK))
    f.append(text(W / 2, 474,
                  "Нарізка на тіки не економить ані такту — вона лише не дає всій цій праці прилетіти одним ударом.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "scrub-tick-budget.svg"), W, H, *f)


if __name__ == "__main__":
    fig_timebomb()
    fig_refresh_vs_scrub()
    fig_patrol_vs_demand()
    fig_scrub_window()
    fig_quadratic_vs_linear()
    fig_mttf_ladder()
    fig_read_barriers()
    fig_tick_budget()
    print("OK: 8 figures ->", IMG)
