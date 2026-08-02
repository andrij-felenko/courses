# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

HOT = "#fdecea"      # світло-червона заливка (потрібні дані)
COOL = "#eaf0fd"     # світло-синя заливка
OFF = "#e9ecef"      # вимкнена доріжка


def poly(pts, color=INK, sw=2.4, dash=None):
    """Ламана (для кривих на графіках): список точок [(x, y), …]."""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


# ── Фігура 1: чотири скалярні команди проти однієї векторної ────────────────
def fig_lanes():
    W, H = 940, 480
    f = []

    # --- лівий бік: скалярно ---
    f.append(text(240, 62, "Скалярний код", size=16, bold=True))
    f.append(text(240, 84, "чотири команди — чотири рази повна ціна", size=12, color=MUTED))

    cw, ch = 56, 40
    for i in range(4):
        y = 112 + i * 62
        f.append(rect(70, y, cw, ch, fill=HOT, stroke=POS, sw=1.3, rx=5))
        f.append(text(70 + cw / 2, y + 26, "a%d" % i, size=13, bold=True))
        f.append(text(140, y + 26, "+", size=15, bold=True, color=POS))
        f.append(rect(154, y, cw, ch, fill=COOL, stroke=NEG, sw=1.3, rx=5))
        f.append(text(154 + cw / 2, y + 26, "b%d" % i, size=13, bold=True))
        f.append(text(224, y + 26, "=", size=15, bold=True))
        f.append(rect(238, y, cw, ch, fill=FILL, stroke=LINE, sw=1.3, rx=5))
        f.append(text(238 + cw / 2, y + 26, "c%d" % i, size=13, bold=True))
        f.append(text(316, y + 26, "команда %d" % (i + 1), size=12, color=MUTED, anchor="start"))

    f.append(text(240, 404, "плата за команду: ×4", size=13, color=POS, bold=True))

    # --- розділювач ---
    f.append(line(465, 100, 465, 420, color=MUTED, sw=1.2, dash="6 6"))

    # --- правий бік: вектор ---
    f.append(text(700, 62, "Векторна команда", size=16, bold=True))
    f.append(text(700, 84, "один регістр — чотири числа в доріжках", size=12, color=MUTED))

    vw, vh = 80, 46
    x0 = 540

    def reg(y, label, names, fill, stroke):
        out = [text(x0, y - 10, label, size=12, color=MUTED, anchor="start")]
        for i, nm in enumerate(names):
            out.append(rect(x0 + i * vw, y, vw, vh, fill=fill, stroke=stroke, sw=1.4, rx=5))
            out.append(text(x0 + i * vw + vw / 2, y + 29, nm, size=14, bold=True))
        return out

    f += reg(126, "регістр A (128 біт)", ["a0", "a1", "a2", "a3"], HOT, POS)
    f.append(text(700, 200, "+", size=18, bold=True, color=POS))
    f += reg(224, "регістр B", ["b0", "b1", "b2", "b3"], COOL, NEG)
    f.append(text(700, 298, "=", size=18, bold=True))
    f += reg(322, "регістр C", ["c0", "c1", "c2", "c3"], FILL, LINE)

    f.append(text(700, 404, "плата за команду: ×1", size=13, color=FIELD, bold=True))

    render(os.path.join(IMG, "one-instruction-many-lanes.svg"), W, H, *f)


# ── Фігура 2: розкладка AoS проти SoA ───────────────────────────────────────
def fig_aos_soa():
    W, H = 980, 440
    f = []
    cw, ch = 54, 44
    x0 = 62

    def strip(y, names, hot_idx):
        out = []
        for i, nm in enumerate(names):
            hot = i in hot_idx
            out.append(rect(x0 + i * cw, y, cw, ch,
                            fill=HOT if hot else FILL,
                            stroke=POS if hot else LINE, sw=1.3, rx=4))
            out.append(text(x0 + i * cw + cw / 2, y + 28, nm, size=12,
                            bold=hot, color=INK if hot else MUTED))
        return out

    def bracket(y, n_cells, label, color):
        x1, x2 = x0, x0 + n_cells * cw
        out = [line(x1, y, x2, y, color=color, sw=2),
               line(x1, y - 8, x1, y + 4, color=color, sw=2),
               line(x2, y - 8, x2, y + 4, color=color, sw=2),
               text((x1 + x2) / 2, y + 26, label, size=13, color=color, bold=True)]
        return out

    # AoS
    f.append(text(x0, 54, "Масив структур (AoS): x, y, z, mass кожної частинки лежать поруч",
                  size=14, bold=True, anchor="start"))
    aos = []
    for p in range(4):
        aos += ["x%d" % p, "y%d" % p, "z%d" % p, "m%d" % p]
    f += strip(72, aos, {0, 4, 8, 12})
    f += bracket(132, 8, "одне 32-байтове завантаження: 8 чисел, потрібні — 2", POS)

    # SoA
    f.append(text(x0, 254, "Структура масивів (SoA): усі x лежать суцільно",
                  size=14, bold=True, anchor="start"))
    soa = ["x%d" % i for i in range(8)] + ["y%d" % i for i in range(8)]
    f += strip(272, soa, set(range(8)))
    f += bracket(332, 8, "одне 32-байтове завантаження: 8 чисел, потрібні — усі 8", FIELD)

    render(os.path.join(IMG, "aos-soa.svg"), W, H, *f)


# ── Фігура 3: хвіст циклу — скалярний і замаскований ────────────────────────
def fig_tail():
    W, H = 930, 450
    f = []
    cw, ch = 56, 42
    x0 = 96

    f.append(text(60, 52, "Масив із 10 елементів, ширина вектора — 4",
                  size=14, bold=True, anchor="start"))
    for i in range(10):
        hot = i >= 8
        f.append(rect(x0 + i * cw, 74, cw, ch, fill=HOT if hot else COOL,
                      stroke=POS if hot else NEG, sw=1.3, rx=4))
        f.append(text(x0 + i * cw + cw / 2, 74 + 27, str(i), size=13, bold=True))

    def bracket(i1, i2, y, label, color):
        x1, x2 = x0 + i1 * cw, x0 + (i2 + 1) * cw
        return [line(x1, y, x2, y, color=color, sw=2),
                line(x1, y - 8, x1, y + 4, color=color, sw=2),
                line(x2, y - 8, x2, y + 4, color=color, sw=2),
                text((x1 + x2) / 2, y + 24, label, size=12, color=color, bold=True)]

    f += bracket(0, 3, 132, "ітерація 1", NEG)
    f += bracket(4, 7, 132, "ітерація 2", NEG)
    f += bracket(8, 9, 132, "лишилось 2", POS)

    # варіант А — скалярний хвіст
    f.append(text(60, 226, "Хвіст скалярно: дві окремі ітерації по одному елементу",
                  size=14, bold=True, anchor="start"))
    for k, i in enumerate((8, 9)):
        x = x0 + i * cw
        f.append(rect(x, 246, cw, ch, fill=HOT, stroke=POS, sw=1.3, rx=4))
        f.append(text(x + cw / 2, 246 + 27, str(i), size=13, bold=True))
    f.append(text(x0 + 10 * cw + 20, 246 + 27, "дві команди", size=12, color=MUTED, anchor="start"))

    # варіант Б — маска
    f.append(text(60, 342, "Замаскована ітерація: одна команда, дві доріжки вимкнено",
                  size=14, bold=True, anchor="start"))
    labels = [("8", True), ("9", True), ("—", False), ("—", False)]
    for k, (nm, on) in enumerate(labels):
        x = x0 + (8 + k) * cw
        f.append(rect(x, 362, cw, ch, fill=HOT if on else OFF,
                      stroke=POS if on else MUTED, sw=1.3, rx=4))
        f.append(text(x + cw / 2, 362 + 27, nm, size=13, bold=True,
                      color=INK if on else MUTED))
    f.append(text(x0 + 12 * cw + 20, 362 + 18, "одна команда", size=12, color=MUTED, anchor="start"))
    f.append(text(x0 + 12 * cw + 20, 362 + 38, "маска: 1 1 0 0", size=12, color=FIELD,
                  bold=True, anchor="start"))

    render(os.path.join(IMG, "tail-and-mask.svg"), W, H, *f)


# ── Фігура 4: дві стелі — пам'ять і арифметика ──────────────────────────────
def fig_roofline():
    W, H = 920, 560
    f = []
    x_l, x_r = 130, 830
    y_b, y_t = 470, 110

    VEC_Y = 160          # векторна стеля
    SCA_Y = 310          # скалярна стеля
    slope = (y_b - VEC_Y) / 300.0   # похила пряма: спад на 310 px за 300 px по x

    def diag_y(x):
        return y_b - (x - x_l) * slope

    knee_vec = x_l + (y_b - VEC_Y) / slope
    knee_sca = x_l + (y_b - SCA_Y) / slope

    # осі
    f.append(arrow(x_l, y_b, x_r + 30, y_b, color=INK, sw=1.6))
    f.append(arrow(x_l, y_b, x_l, y_t - 20, color=INK, sw=1.6))
    f.append(text(x_l - 8, y_t - 30, "швидкість, елементів за секунду", size=13,
                  color=MUTED, anchor="start"))
    f.append(text(470, 522, "арифметична інтенсивність — дій на принесений байт",
                  size=13, color=MUTED))
    f.append(text(150, 498, "мало дій на байт", size=12, color=MUTED, anchor="start"))
    f.append(text(820, 498, "багато дій на байт", size=12, color=MUTED, anchor="end"))

    # похила межа пам'яті (спільна для обох версій)
    f.append(line(x_l, y_b, knee_vec, VEC_Y, color=NEG, sw=2.4))
    f.append(mtext(255, 148, ["межа пропускної", "здатності пам'яті"], size=13, color=NEG, bold=True))

    # стелі
    f.append(line(knee_vec, VEC_Y, x_r, VEC_Y, color=POS, sw=2.4))
    f.append(text(x_r, VEC_Y - 14, "векторна стеля (8 доріжок)", size=13, color=POS,
                  bold=True, anchor="end"))
    f.append(line(knee_sca, SCA_Y, x_r, SCA_Y, color=INK, sw=2.2, dash="7 5"))
    f.append(text(x_r, SCA_Y - 14, "скалярна стеля", size=13, color=INK, bold=True, anchor="end"))

    # точка А — цикл, обмежений пам'яттю
    xa = 196
    f.append(circle(xa, diag_y(xa), 6, fill=BG, stroke=NEG, sw=2.4))
    f.append(mtext(xa + 22, 424, ["c[i] = a[i] + b[i]", "обидві версії тут — виграшу немає"],
                   size=12, color=INK, anchor="start"))

    # точка Б — цикл, обмежений арифметикою
    xb = 660
    f.append(line(xb, VEC_Y, xb, SCA_Y, color=MUTED, sw=1.4, dash="5 5"))
    f.append(circle(xb, VEC_Y, 6, fill=BG, stroke=POS, sw=2.4))
    f.append(circle(xb, SCA_Y, 6, fill=BG, stroke=INK, sw=2.4))
    f.append(text(xb + 16, 240, "різниця у ширині", size=12, color=FIELD,
                  bold=True, anchor="start"))
    f.append(text(xb, SCA_Y + 34, "дані вже в кеші: рахунку багато, підвозу мало",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "roofline-simd.svg"), W, H, *f)


# ── Фігура 5 (вставка hist): дві лінії векторних машин на одній шкалі ───────
def fig_two_lineages():
    W, H = 1240, 600
    AX = 310                      # рівень осі часу
    X0, Y0, S = 70.0, 1960.0, 17.0

    def X(year):
        return X0 + (year - Y0) * S

    f = []
    f.append(text(W / 2, 28, "Дві лінії векторних машин на одній шкалі часу",
                  size=17, bold=True))

    # вісь часу з поділками по десять років
    f.append(line(X0, AX, 1180, AX, color=INK, sw=2.0))
    for y in range(1960, 2030, 10):
        f.append(line(X(y), AX - 6, X(y), AX + 6, color=MUTED, sw=1.2))
    f.append(arrow(1180, AX, 1202, AX, color=INK, sw=2.0))
    f.append(text(1208, AX + 5, "час", size=12, color=MUTED, anchor="start"))
    f.append(text(X0, AX + 26, "поділка — десять років", size=11,
                  color=MUTED, anchor="start"))

    # ── лінія перша: велетні (над віссю) ───────────────────────────────
    f.append(text(X0, 56, "ЛІНІЯ ПЕРША: велетні — уся машина є вектором",
                  size=15, bold=True, color=NEG, anchor="start"))

    top = [
        (1962, 84,  "1962 · SOLOMON (Слотнік, Westinghouse) — фінансування спинено"),
        (1966, 116, "1966 · Флінн називає клас SIMD; Burroughs дістає контракт"),
        (1972, 148, "1972 · ILLIAC IV — квадрант із 64 ПЕ їде в NASA Ames"),
        (1974, 180, "1974 · CDC STAR-100 — вектори пам'ять→пам'ять"),
        (1976, 212, "1976 · Cray-1 — вектори в регістрах, є регістр довжини VL"),
    ]
    for year, ty, label in top:
        x = X(year)
        f.append(line(x, AX - 8, x, ty + 6, color=NEG, sw=1.2, dash="4 4"))
        f.append(circle(x, AX, 5.5, fill=BG, stroke=NEG, sw=2.2))
        f.append(text(x + 10, ty, label, size=13, color=INK, anchor="start"))

    # ── лінія друга: пакетний SIMD (під віссю) ─────────────────────────
    f.append(text(X0, 356, "ЛІНІЯ ДРУГА: пакетний SIMD у масовому процесорі",
                  size=15, bold=True, color=POS, anchor="start"))

    bot = [
        (1994, 392, "HP MAX (1994) — SIMD у настільному процесорі заради MPEG"),
        (1997, 426, "Intel MMX (1997) — 64 біти, регістри позичені в x87"),
        (1999, 460, "SSE (Pentium III, 1999) · AltiVec (PowerPC G4) — 128 біт"),
        (2005, 494, "ARM NEON (ARMv7, Cortex-A8, 2005) — вектор у телефоні"),
        (2011, 528, "AVX (Sandy Bridge, 2011) — 256 біт"),
        (2016, 562, "AVX-512 (Xeon Phi Knights Landing, 2016) — 512 біт"),
    ]
    for year, ty, label in bot:
        x = X(year)
        f.append(line(x, AX + 8, x, ty - 6, color=POS, sw=1.2, dash="4 4"))
        f.append(circle(x, AX, 5.5, fill=BG, stroke=POS, sw=2.2))
        f.append(text(x - 10, ty, label, size=13, color=INK, anchor="end"))

    # ── сходження: змінна довжина ──────────────────────────────────────
    xa, xb = X(2016), X(2021)
    f.append(line(xa, 282, xb, 282, color=FIELD, sw=2.4))
    f.append(line(xa, 282, xa, 294, color=FIELD, sw=2.4))
    f.append(line(xb, 282, xb, 294, color=FIELD, sw=2.4))
    box, bw, bh = textbox(1060, 250,
                          "SVE (2016) · RVV 1.0 (2021)\n"
                          "довжина вектора — знову в машині, а не в коді",
                          size=13, fill="#eafaf0", stroke=FIELD, sw=2.0, bold=False)
    f.append(box)
    f.append(line(1060, 250 + bh / 2, 1060, 282, color=FIELD, sw=1.6))

    render(os.path.join(IMG, "simd-two-lineages.svg"), W, H, *f)


# ── Фігура 6 (вставка hist): та сама дія — п'ять записів ────────────────────
def fig_isa_treadmill():
    W, H = 1000, 470
    C1X, C1W = 60, 230
    C2X, C2W = 310, 390
    C3X, C3W = 720, 220

    f = []
    f.append(text(W / 2, 28, "Та сама дія — п'ять різних записів", size=17, bold=True))

    f.append(text(C1X + C1W / 2, 62, "набір і рік", size=12, color=MUTED, bold=True))
    f.append(text(C2X + C2W / 2, 62, "як пишеться додавання 16-бітових чисел",
                  size=12, color=MUTED, bold=True))
    f.append(text(C3X + C3W / 2, 62, "ширина", size=12, color=MUTED, bold=True))

    rows = [
        ("MMX · 1997",     "paddw mm0, mm1",             "64 біти",   False),
        ("SSE2 · 2000",    "paddw xmm0, xmm1",           "128 біт",   False),
        ("AVX2 · 2013",    "vpaddw ymm0, ymm1, ymm2",    "256 біт",   False),
        ("AVX-512 · 2016", "vpaddw zmm0, zmm1, zmm2",    "512 біт",   False),
        ("SVE · 2016",     "add z0.h, p0/m, z0.h, z1.h", "обирає машина", True),
    ]

    y, h, gap = 80, 46, 10
    for name, code, width, hot in rows:
        fill1 = "#eafaf0" if hot else FILL
        edge = FIELD if hot else LINE
        f.append(fitbox(C1X, y, C1W, h, name, size=14, bold=True,
                        fill=fill1, stroke=edge, sw=1.6))
        f.append(fitbox(C2X, y, C2W, h, code, size=14,
                        fill=BG, stroke=edge, sw=1.6))
        f.append(fitbox(C3X, y, C3W, h, width, size=14,
                        fill=fill1, stroke=edge, sw=1.6))
        y += h + gap

    note, nw, nh = textbox(W / 2, 400,
                           "чотири верхні рядки — один і той самий цикл, перезібраний під кожне покоління\n"
                           "нижній — той самий двійковий код на будь-якій ширині",
                           size=13, fill=FILL, stroke=MUTED, sw=1.4)
    f.append(note)

    render(os.path.join(IMG, "simd-isa-treadmill.svg"), W, H, *f)


# ── Фігура: ланцюжок залежностей — один акумулятор проти восьми ─────────────
def fig_fma_chains():
    W, H = 1000, 700
    X0, CW = 210, 54          # вісь тактів: 0..12
    f = []

    def X(c):
        return X0 + c * CW

    def grid(ytop, ybot, ynum):
        out = []
        for c in range(13):
            out.append(line(X(c), ytop, X(c), ybot, color="#dfe3e8", sw=1.0))
            out.append(text(X(c), ynum, str(c), size=12, color=MUTED))
        return out

    # ── панель А: один акумулятор ──────────────────────────────────────
    f.append(text(40, 48, "Один акумулятор", size=15, bold=True, anchor="start"))
    f.append(text(40, 70, "кожна FMA чекає результату попередньої",
                 size=12, color=MUTED, anchor="start"))
    f.append(text(960, 48, "темп: одна FMA на чотири такти", size=13, bold=True,
                 color=POS, anchor="end"))

    f += grid(88, 196, 216)
    for k in range(3):
        y = 94 + k * 36
        f.append(rect(X(4 * k), y, 4 * CW, 28, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
        f.append(text(200, y + 19, "FMA №%d" % (k + 1), size=13, anchor="end"))
        if k < 2:
            f.append(arrow(X(4 * k + 4) - 4, y + 28, X(4 * k + 4) - 4, y + 36))

    f.append(line(40, 250, 960, 250, color=MUTED, sw=1.2, dash="6 6"))

    # ── панель Б: вісім акумуляторів ───────────────────────────────────
    f.append(text(40, 286, "Вісім акумуляторів", size=15, bold=True, anchor="start"))
    f.append(text(40, 308, "сусідні FMA незалежні — щотакту стартують дві",
                 size=12, color=MUTED, anchor="start"))
    f.append(text(960, 286, "темп: дві FMA щотакту — увосьмеро більше", size=13,
                 bold=True, color=FIELD, anchor="end"))

    f += grid(322, 622, 642)
    for j in range(16):
        y = 326 + j * 18
        acc = j % 8
        hot = (acc == 0)
        f.append(rect(X(j // 2), y, 4 * CW, 14,
                      fill="#fdecea" if hot else "#eaf0fd",
                      stroke=POS if hot else NEG, sw=1.2, rx=3))
        f.append(text(200, y + 11, "acc%d" % acc, size=11,
                      color=POS if hot else INK, bold=hot, anchor="end"))

    f.append(text(X(6), 672, "такти", size=13, color=MUTED))

    render(os.path.join(IMG, "fma-chains.svg"), W, H, *f)


# ── Фігура: як вісім акумуляторів зводяться в одне число ────────────────────
def fig_hsum_tree():
    W, H = 940, 588
    f = []
    BX, BW, GAP = 130, 82, 14        # 8 колонок: 130 … 884
    PITCH = BW + GAP                 # 96

    # ── крок 1: дерево векторних додавань ──────────────────────────────
    f.append(text(W / 2, 44, "Крок 1 — скласти вісім акумуляторів в один вектор",
                 size=15, bold=True))
    f.append(text(W / 2, 66, "звичайні векторні додавання: 8 → 4 → 2 → 1",
                 size=12, color=MUTED))

    LY = [86, 158, 230, 302]
    BH = 38

    for j in range(8):
        f.append(fitbox(BX + j * PITCH, LY[0], BW, BH, "acc%d" % j,
                        size=13, fill="#eaf0fd", stroke=NEG, sw=1.4))
    for i in range(4):
        f.append(fitbox(BX + i * 2 * PITCH, LY[1], BW + PITCH, BH,
                        "acc%d+acc%d" % (2 * i, 2 * i + 1),
                        size=13, fill=FILL, stroke=LINE, sw=1.4))
    for i in range(2):
        f.append(fitbox(BX + i * 4 * PITCH, LY[2], BW + 3 * PITCH, BH,
                        "acc%d…acc%d" % (4 * i, 4 * i + 3),
                        size=13, fill=FILL, stroke=LINE, sw=1.4))
    f.append(fitbox(BX, LY[3], BW + 7 * PITCH, BH,
                    "один вектор — вісім часткових сум",
                    size=14, bold=True, fill="#fdecea", stroke=POS, sw=1.6))

    for j in range(8):
        f.append(arrow(BX + j * PITCH + BW / 2, LY[0] + BH + 2,
                       BX + j * PITCH + BW / 2, LY[1] - 4))
    for i in range(4):
        cx = BX + i * 2 * PITCH + (BW + PITCH) / 2
        f.append(arrow(cx, LY[1] + BH + 2, cx, LY[2] - 4))
    for i in range(2):
        cx = BX + i * 4 * PITCH + (BW + 3 * PITCH) / 2
        f.append(arrow(cx, LY[2] + BH + 2, cx, LY[3] - 4))

    for lab, y in (("8 регістрів", LY[0]), ("4", LY[1]), ("2", LY[2]), ("1", LY[3])):
        f.append(text(116, y + 24, lab, size=12, color=MUTED, anchor="end"))

    f.append(line(40, 362, 900, 362, color=MUTED, sw=1.2, dash="6 6"))

    # ── крок 2: складання доріжок усередині регістра ───────────────────
    f.append(text(W / 2, 394, "Крок 2 — скласти вісім доріжок усередині регістра",
                 size=15, bold=True))
    f.append(text(W / 2, 416, "зсунути половину регістра, додати — і так тричі",
                 size=12, color=MUTED))

    CY, CH, CWD, CG = 436, 40, 40, 4

    def group(x0, cnt, labels=None, fill="#eaf0fd", stroke=NEG):
        out = []
        for k in range(cnt):
            x = x0 + k * (CWD + CG)
            if labels:
                out.append(fitbox(x, CY, CWD, CH, labels[k], size=12,
                                  fill=fill, stroke=stroke, sw=1.3, pad=3))
            else:
                out.append(rect(x, CY, CWD, CH, fill=fill, stroke=stroke, sw=1.3, rx=4))
        return out, x0 + cnt * CWD + (cnt - 1) * CG

    g, e1 = group(50, 8, ["s%d" % k for k in range(8)])
    f.extend(g)
    g, e2 = group(440, 4)
    f.extend(g)
    g, e3 = group(654, 2)
    f.extend(g)
    f.append(fitbox(780, CY, CWD, CH, "s", size=15, bold=True,
                    fill="#fdecea", stroke=POS, sw=1.6, pad=3))

    for a, b in ((e1, 440), (e2, 654), (e3, 780)):
        f.append(arrow(a + 8, CY + CH / 2, b - 6, CY + CH / 2))

    for cx, lab in ((224, "8 доріжок"), (526, "4"), (696, "2"), (800, "1 = результат")):
        f.append(text(cx, CY + CH + 26, lab, size=12, color=MUTED))

    f.append(mtext(W / 2, 538,
                   ["Зсуви й додавання всередині регістра порушують незалежність доріжок і тому повільні —",
                    "але їх рівно три на весь цикл, тож на мільйоні елементів їхня ціна не помітна."],
                   size=12, color=MUTED))

    render(os.path.join(IMG, "hsum-tree.svg"), W, H, *f)


# ── Фігура 9 (вставка math): стеля Амдала як функція ширини вектора ─────────
def fig_amdahl_width():
    W_C, H_C = 880, 580
    x_l, x_r = 130, 690
    y_b, y_t = 480, 110
    f = []

    def X(w):
        return x_l + (x_r - x_l) * math.log(w, 2) / 6.0

    def Y(s):
        return y_b - (y_b - y_t) * math.log(s) / math.log(20.0)

    def S(frac, w):
        return 1.0 / ((1 - frac) + frac / w)

    # осі
    f.append(arrow(x_l, y_b, x_r + 34, y_b, color=INK, sw=1.6))
    f.append(arrow(x_l, y_b, x_l, y_t - 40, color=INK, sw=1.6))
    f.append(text(142, 96, "прискорення всієї програми", size=13,
                  color=MUTED, anchor="start"))
    f.append(text((x_l + x_r) / 2, 534,
                  "ширина вектора W — скільки елементів бере одна команда",
                  size=13, color=MUTED))

    for s in (1, 2, 5, 10, 20):
        f.append(line(x_l - 5, Y(s), x_l, Y(s), color=INK, sw=1.4))
        f.append(text(x_l - 10, Y(s) + 4, "×%d" % s, size=12, color=MUTED, anchor="end"))
    for w in (1, 2, 4, 8, 16, 32, 64):
        f.append(line(X(w), y_b, X(w), y_b + 5, color=INK, sw=1.4))
        f.append(text(X(w), y_b + 22, str(w), size=12, color=MUTED))

    curves = ((0.95, POS, "f = 0.95"), (0.80, FIELD, "f = 0.80"), (0.50, NEG, "f = 0.50"))

    # стелі 1/(1−f)
    for frac, col, _ in curves:
        f.append(line(x_l, Y(1 / (1 - frac)), x_r, Y(1 / (1 - frac)),
                      color=col, sw=1.4, dash="6 5"))
    f.append(text(142, 132, "штрихові — стелі 1/(1−f): їх не перетнути за жодної ширини",
                  size=12, color=MUTED, anchor="start"))

    # криві
    for frac, col, lab in curves:
        pts = []
        for i in range(0, 61):
            w = 2.0 ** (6.0 * i / 60.0)
            pts.append((X(w), Y(S(frac, w))))
        f.append(poly(pts, color=col, sw=2.6))
        f.append(text(x_r + 12, Y(S(frac, 64)) + 4, lab, size=13, color=col,
                      bold=True, anchor="start"))

    render(os.path.join(IMG, "amdahl-width.svg"), W_C, H_C, *f)


# ── Фігура 10 (вставка math): злам прискорення за арифметичною інтенсивністю ─
def fig_vectorization_knee():
    W_C, H_C = 880, 600
    x_l, x_r = 130, 750
    y_ax = 500
    f = []

    def X(r):
        return x_l + (x_r - x_l) * (math.log10(r) + 1.0) / 3.0

    def Y(s):
        return 470 - 110 * math.log(s, 2)

    # осі
    f.append(arrow(x_l, y_ax, x_r + 34, y_ax, color=INK, sw=1.6))
    f.append(arrow(x_l, y_ax, x_l, 100, color=INK, sw=1.6))
    f.append(text(142, 88, "у скільки разів векторна версія швидша за скалярну",
                  size=13, color=MUTED, anchor="start"))
    f.append(text((x_l + x_r) / 2, 560,
                  "арифметична інтенсивність у частках точки зламу: I / I*",
                  size=13, color=MUTED))

    for s in (1, 2, 4, 8):
        f.append(line(x_l - 5, Y(s), x_l, Y(s), color=INK, sw=1.4))
        f.append(text(x_l - 10, Y(s) + 4, "×%d" % s, size=12, color=MUTED, anchor="end"))
    for r, lab in ((0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        f.append(line(X(r), y_ax, X(r), y_ax + 5, color=INK, sw=1.4))
        f.append(text(X(r), y_ax + 22, lab, size=12, color=MUTED))

    # вертикальні орієнтири на зламах
    f.append(line(X(1), Y(1), X(1), y_ax, color=MUTED, sw=1.3, dash="5 5"))
    f.append(text(X(1), 455, "I*", size=13, color=MUTED, bold=True))
    f.append(line(X(8), Y(8), X(8), y_ax, color=MUTED, sw=1.3, dash="5 5"))
    f.append(text(X(8), 130, "W·I*", size=13, color=MUTED, bold=True))

    # сама крива S = min(W, max(1, I/I*))
    f.append(poly([(X(0.1), Y(1)), (X(1), Y(1)), (X(8), Y(8)), (X(100), Y(8))],
                  color=POS, sw=2.8))

    # п'ять циклів із розрахунку
    loops = (
        (0.12, 1.00, "наївне множення матриць", "×1.0", (146.4, 452), "middle"),
        (1.04, 1.04, "c[i] = a[i] + b[i]", "×1.04", (356, 489), "middle"),
        (2.08, 2.08, "скалярний добуток із RAM", "×2.1", (420, 374), "start"),
        (8.00, 8.00, "скалярний добуток із L1", "×8", (538, 172), "start"),
        (54.5, 8.00, "блокове множення, b ≈ 52", "×8", (700, 168), "middle"),
    )
    for i, (r, s, _n, _v, (lx, ly), anc) in enumerate(loops, start=1):
        f.append(circle(X(r), Y(s), 5.5, fill=BG, stroke=POS, sw=2.4))
        f.append(text(lx, ly, str(i), size=13, color=INK, bold=True, anchor=anc))

    # легенда
    f.append(rect(150, 152, 250, 168, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(275, 174, "п'ять циклів із розрахунку", size=11, color=MUTED, bold=True))
    for i, (_r, _s, name, val, _p, _a) in enumerate(loops, start=1):
        y = 202 + (i - 1) * 26
        f.append(text(163, y, str(i), size=11, color=INK, bold=True, anchor="start"))
        f.append(text(180, y, name, size=11, color=INK, anchor="start"))
        f.append(text(385, y, val, size=11, color=POS, bold=True, anchor="end"))

    render(os.path.join(IMG, "vectorization-knee.svg"), W_C, H_C, *f)


fig_lanes()
fig_aos_soa()
fig_tail()
fig_roofline()
fig_two_lineages()
fig_isa_treadmill()
fig_fma_chains()
fig_hsum_tree()
fig_amdahl_width()
fig_vectorization_knee()
print("ok")
