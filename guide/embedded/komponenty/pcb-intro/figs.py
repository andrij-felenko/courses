# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b87333"   # мідь: доріжки, майданчики, стінки отвору
COPDK  = "#8a561f"   # темніший обрис міді
CORE   = "#d8c98a"   # склоепоксидне осердя (FR-4), скол у розрізі
MASK   = "#1f7a4d"   # паяльна маска (зелена)
SILK   = "#f4f6f8"   # шовкографія (білий надпис)
BG_    = "#ffffff"


# ── board-anatomy: розріз двошарової плати — «пиріг» шарів ──────────────────
# Ідея: показати, ЩО таке плата як фізичний предмет у розрізі. Знизу вгору:
# паяльна маска, мідь (доріжка), склоепоксидне осердя, мідь, маска — а згори
# шовкографія. Це головна фігура «що всередині зеленого прямокутника».
def fig_board_anatomy():
    W, H = 760, 430
    p = []
    p.append(text(W/2, 34, "Двошарова плата в розрізі: пиріг із міді та ізолятора", size=15, bold=True))

    bx0, bx1 = 90, 470
    bw = bx1 - bx0
    cx = (bx0 + bx1) / 2

    # координати шарів (згори вниз), товщини навмисно перебільшені для наочності
    y_silk   = 96          # шовкографія (напис) — над верхньою маскою
    y_mask_t = 132; h_mask = 12   # верхня паяльна маска
    y_cu_t   = 144; h_cu   = 16   # верхня мідь
    y_core   = 160; h_core = 96   # осердя FR-4
    y_cu_b   = 256                # нижня мідь
    y_mask_b = 272                # нижня паяльна маска

    def slab(y, h, fill, stroke, sw=1.4):
        return rect(bx0, y, bw, h, fill=fill, stroke=stroke, sw=sw, rx=2)

    # осердя FR-4 (найтовще)
    p.append(slab(y_core, h_core, CORE, "#b8a55f", 1.6))
    # штрихування «скловолокно» всередині осердя
    for i in range(1, 7):
        yy = y_core + i * h_core / 7
        p.append(line(bx0 + 6, yy, bx1 - 6, yy, color="#c7b673", sw=0.8, dash="5 6"))

    # верхня мідь — суцільний шар, з якого лишили доріжки; покажемо як смугу
    p.append(slab(y_cu_t, h_cu, COPPER, COPDK, 1.2))
    # нижня мідь
    p.append(slab(y_cu_b, h_cu, COPPER, COPDK, 1.2))
    # паяльна маска зверху й знизу (тонка, поверх міді)
    p.append(slab(y_mask_t, h_mask, MASK, "#155c3a", 1.0))
    p.append(slab(y_mask_b, h_mask, MASK, "#155c3a", 1.0))

    # шовкографія — білий напис над верхньою маскою
    p.append(rect(cx - 46, y_silk - 15, 92, 22, fill=SILK, stroke="#c9cdd2", sw=1.0, rx=3))
    p.append(text(cx, y_silk + 1, "R12  +5V", size=12, color="#2a2f34", bold=True))

    # --- виноски праворуч: рівномірно рознесена колонка підписів;
    #     ламана лінія веде від краю шару до свого підпису (шари близькі,
    #     тож підписи фануємо по вертикалі, щоб рамки не наповзали) ---
    lx = bx1 + 18          # вертикаль, до якої збігаються лінії-виноски
    box_cx = 642           # спільний центр колонки підписів
    def callout(y_layer, y_box, label, col_txt, col_box):
        frag = [line(bx1 - 4, y_layer, lx, y_layer, color=MUTED, sw=1.0),
                line(lx, y_layer, lx + 14, y_box, color=MUTED, sw=1.0)]
        b, w, h = textbox(box_cx, y_box, label, size=10.5, color=col_txt,
                          fill="#ffffff", stroke=col_box, sw=1.1, pad=6, min_w=152)
        frag.append(b)
        return frag

    # y-центри підписів рознесені рівномірно (крок 30) — не наповзають
    for f in callout(y_silk - 2,            96,  "шовкографія — написи (білі)", "#2a2f34", "#9aa0a6"): p.append(f)
    for f in callout(y_mask_t + h_mask/2,  134,  "паяльна маска — захист", "#155c3a", MASK): p.append(f)
    for f in callout(y_cu_t + h_cu/2,      172,  "мідь: доріжки й майданчики", COPDK, COPPER): p.append(f)
    for f in callout(y_core + h_core/2,    210,  "осердя FR-4 (скло + епоксидка)", "#8a7a2f", "#b8a55f"): p.append(f)
    for f in callout(y_cu_b + h_cu/2,      248,  "мідь нижнього боку", COPDK, COPPER): p.append(f)
    for f in callout(y_mask_b + h_mask/2,  286,  "паяльна маска знизу", "#155c3a", MASK): p.append(f)

    p.append(text(cx, y_mask_b + h_mask + 34,
                  "уся плата ≈ 1.6 мм · осердя набагато товще за мідь і маску",
                  size=11, color=MUTED))
    p.append(text(cx, y_mask_b + h_mask + 52,
                  "мідь ≈ 35 мкм — тонша за волосину", size=11, color=COPDK, bold=True))

    render(os.path.join(OUT, "board-anatomy.svg"), W, H, *p)


# ── copper-pattern: вигляд згори — «друковані дроти» ────────────────────────
# Ідея: показати, що доріжки — це просто мідь, ЛИШЕНА там, де потрібне
# з'єднання, і зчищена скрізь інде. Тонка сигнальна доріжка, широка силова,
# майданчики під деталь і суцільна заливка (полігон) — усе з однієї фольги.
def fig_copper_pattern():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 30, "Погляд згори: доріжки — це мідь, лишена де треба", size=15, bold=True))

    # тло плати (маска зелена) з «вікнами» голої міді на майданчиках
    bx0, by0, bw, bh = 60, 60, 640, 250
    p.append(rect(bx0, by0, bw, bh, fill="#1f7a4d", stroke="#155c3a", sw=1.6, rx=8))

    def pad(cx, cy, r=12):
        # золотавий майданчик (вікно в масці) з отвором
        return (circle(cx, cy, r, fill=COPPER, stroke=COPDK, sw=1.4) +
                circle(cx, cy, r*0.42, fill="#155c3a", stroke=COPDK, sw=1.0))

    def track(x1, y1, x2, y2, w):
        return line(x1, y1, x2, y2, color=COPPER, sw=w)

    # --- тонка сигнальна доріжка: від майданчика до майданчика, з поворотом ---
    p.append(track(130, 110, 300, 110, 5))
    p.append(track(300, 110, 300, 190, 5))
    p.append(track(300, 190, 430, 190, 5))
    p.append(pad(130, 110)); p.append(pad(430, 190))
    b, _, _ = textbox(232, 86, "тонка сигнальна доріжка", size=10, color="#eafff5",
                      fill="#155c3a", stroke=COPPER, sw=1.0, pad=4)
    p.append(b)

    # --- широка силова доріжка ---
    p.append('<rect x="130" y="238" width="300" height="18" rx="9" fill="%s" stroke="%s" stroke-width="1.4"/>' % (COPPER, COPDK))
    p.append(pad(130, 247, 14)); p.append(pad(430, 247, 14))
    b, _, _ = textbox(280, 285, "широка силова доріжка (більший струм — менший опір)",
                      size=10, color="#eafff5", fill="#155c3a", stroke=COPPER, sw=1.0, pad=4)
    p.append(b)

    # --- суцільна заливка (полігон землі) праворуч ---
    px0, py0, pw, ph = 500, 95, 170, 150
    p.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s" stroke-width="1.4" opacity="0.95"/>' % (px0, py0, pw, ph, COPPER, COPDK))
    # кілька отворів-«зшивок» у полігоні
    for gx in range(px0+26, px0+pw-10, 40):
        for gy in range(py0+26, py0+ph-10, 42):
            p.append(circle(gx, gy, 5, fill="#155c3a", stroke=COPDK, sw=0.9))
    b, _, _ = textbox(px0 + pw/2, py0 + ph + 18, "суцільна заливка міді\n(полігон, напр. земля)",
                      size=10, color=INK, fill="#ffffff", stroke=COPPER, sw=1.1, pad=5)
    p.append(b)

    # підпис знизу: зелене — маска (нема міді), мідне — лишена мідь
    p.append(text(W/2, H - 12,
                  "зелене — маска (мідь зчищено) · мідне/золотисте — мідь, що лишилася провідником",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "copper-pattern.svg"), W, H, *p)


# ── via-types: перехідний отвір — розріз і три види в стеку ─────────────────
# Ідея: розкрити ключове поняття назви. Ліворуч — що таке via фізично:
# просвердлений отвір із металізованою стінкою, що з'єднує мідь двох боків.
# Праворуч — три види у 4-шаровому стеку: наскрізний, глухий, захований.
def fig_via_types():
    W, H = 780, 400
    p = []
    p.append(text(W/2, 30, "Перехідний отвір (via): міст між шарами міді", size=15, bold=True))

    # ---------- ліва половина: розріз одного via ----------
    lx0, lx1 = 60, 300
    lcx = (lx0 + lx1) / 2
    ytop, ybot = 90, 250
    p.append(text(lcx, 66, "що це фізично", size=12, bold=True, color=INK))
    # тіло плати (осердя)
    p.append(rect(lx0, ytop, lx1 - lx0, ybot - ytop, fill=CORE, stroke="#b8a55f", sw=1.5, rx=3))
    # верхня й нижня мідь
    p.append(rect(lx0, ytop - 12, lx1 - lx0, 12, fill=COPPER, stroke=COPDK, sw=1.1, rx=1))
    p.append(rect(lx0, ybot, lx1 - lx0, 12, fill=COPPER, stroke=COPDK, sw=1.1, rx=1))
    # отвір: порожнина в центрі з металізованою стінкою (два «стовпчики» міді)
    hw = 30
    holeL = lcx - hw/2
    holeR = lcx + hw/2
    wall = 6
    # стінки-металізація
    p.append(rect(holeL, ytop - 12, wall, (ybot + 12) - (ytop - 12), fill=COPPER, stroke=COPDK, sw=1.1, rx=1))
    p.append(rect(holeR - wall, ytop - 12, wall, (ybot + 12) - (ytop - 12), fill=COPPER, stroke=COPDK, sw=1.1, rx=1))
    # порожнеча між стінками
    p.append(rect(holeL + wall, ytop - 12, hw - 2*wall, (ybot + 12) - (ytop - 12), fill=BG_, stroke="none", sw=0))
    # майданчики (кільця) навколо отвору згори й знизу
    p.append(rect(lcx - hw/2 - 14, ytop - 12, hw + 28, 12, fill=COPPER, stroke=COPDK, sw=1.1, rx=1))
    p.append(rect(lcx - hw/2 - 14, ybot, hw + 28, 12, fill=COPPER, stroke=COPDK, sw=1.1, rx=1))

    # виноски
    p.append(line(holeL + wall/2, ytop + 40, lx0 + 24, ytop + 40, color=MUTED, sw=1.0))
    b, _, _ = textbox(lx0 - 6, ytop + 40, "мідна\nстінка", size=10, color=COPDK,
                      fill="#ffffff", stroke=COPPER, sw=1.0, pad=5)
    p.append(b)
    p.append(line(lcx, (ytop+ybot)/2, lx1 + 10, (ytop+ybot)/2, color=MUTED, sw=1.0, dash="3 3"))
    b, _, _ = textbox(lx1 + 60, (ytop+ybot)/2, "порожній\nпросвердл.\nканал", size=10, color=MUTED,
                      fill="#ffffff", stroke=MUTED, sw=1.0, pad=5)
    p.append(b)
    p.append(text(lcx, ybot + 42, "свердло робить діру,", size=10.5, color=MUTED))
    p.append(text(lcx, ybot + 58, "гальваніка вкриває стінку міддю", size=10.5, color=COPDK, bold=True))

    # роздільник
    p.append(line(W/2, 60, W/2, H - 20, color="#d0d4d8", sw=1.4, dash="6 5"))

    # ---------- права половина: три види у 4-шаровому стеку ----------
    rx0, rx1 = 420, 740
    rcx = (rx0 + rx1) / 2
    p.append(text(rcx, 66, "три види у 4 шарах", size=12, bold=True, color=INK))
    # 4 мідні шари L1..L4 як горизонтальні смуги
    sx0, sx1 = 430, 730
    sw_ = sx1 - sx0
    ys = [96, 138, 180, 222]   # L1..L4
    lh = 9
    names = ["L1", "L2", "L3", "L4"]
    # осердя-фон між шарами
    p.append(rect(sx0, ys[0], sw_, ys[3] - ys[0] + lh, fill=CORE, stroke="#b8a55f", sw=1.3, rx=3))
    for i, yy in enumerate(ys):
        p.append(rect(sx0, yy, sw_, lh, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
        p.append(text(sx0 - 16, yy + lh, names[i], size=10, color=MUTED))

    def vpad(cx, y):
        return rect(cx - 12, y - 2, 24, lh + 4, fill=COPPER, stroke=COPDK, sw=1.0, rx=1)
    def vbarrel(cx, ya, yb):
        return rect(cx - 5, ya, 10, yb - ya, fill=COPPER, stroke=COPDK, sw=1.0, rx=1)

    # наскрізний (through): L1..L4
    tx = sx0 + 55
    p.append(vbarrel(tx, ys[0], ys[3] + lh))
    p.append(vpad(tx, ys[0])); p.append(vpad(tx, ys[3]))
    b, _, _ = textbox(tx, ys[3] + 40, "наскрізний\n(усі шари)", size=9.5, color=INK,
                      fill="#ffffff", stroke=COPPER, sw=1.0, pad=4)
    p.append(b)

    # глухий (blind): L1..L2 (від поверхні всередину)
    bx = sx0 + 150
    p.append(vbarrel(bx, ys[0], ys[1] + lh))
    p.append(vpad(bx, ys[0]))
    b, _, _ = textbox(bx, ys[3] + 40, "глухий\n(поверхня→\nвсередину)", size=9.5, color=INK,
                      fill="#ffffff", stroke=COPPER, sw=1.0, pad=4)
    p.append(b)

    # захований (buried): L2..L3 (лише всередині)
    ux = sx0 + 245
    p.append(vbarrel(ux, ys[1], ys[2] + lh))
    b, _, _ = textbox(ux, ys[3] + 40, "захований\n(лише\nвсередині)", size=9.5, color=INK,
                      fill="#ffffff", stroke=COPPER, sw=1.0, pad=4)
    p.append(b)

    render(os.path.join(OUT, "via-types.svg"), W, H, *p)


# ── (вставка math-trace-impedance) кольори для сигналу/поля ──────────────────
SIG   = "#c0392b"   # доріжка/провідник сигналу (гарячий)
WAVE  = "#2457d6"   # хвиля напруги
GND   = "#444a52"   # опорна земля


# ── rlgc-ladder: доріжка = ланцюжок LC-ланок (звідки √(L/C)) ─────────────────
# Ідея вставки: доріжка не «дріт», а лінія передачі. Розрізаємо її на короткі
# шматочки; кожен має послідовну індуктивність ΔL і шунтову ємність ΔC на
# землю. Нескінченний ланцюжок таких ланок і дає хвильовий опір √(L'/C').
def fig_rlgc_ladder():
    W, H = 780, 340
    p = []
    p.append(text(W/2, 30, "Доріжка як ланцюжок LC-ланок: звідки береться Z₀", size=15, bold=True))

    # верх: фізична доріжка над суцільною землею, поділена на шматочки Δx
    tx0, tx1 = 70, 710
    ty = 78
    gy = 116
    p.append(rect(tx0, ty - 5, tx1 - tx0, 10, fill=SIG, stroke="#8a2b1f", sw=1.2, rx=3))   # доріжка
    p.append(rect(tx0, gy, tx1 - tx0, 10, fill=GND, stroke="#2c3138", sw=1.2, rx=2))       # земля
    p.append(text((tx0+tx1)/2, ty - 12, "доріжка (сигнал)", size=10.5, color=SIG, bold=True))
    p.append(text((tx0+tx1)/2, gy + 24, "суцільна земля під нею (зворотний шлях струму)", size=10.5, color=GND))
    # поділ на шматочки Δx
    for i in range(1, 6):
        xx = tx0 + i * (tx1 - tx0) / 6
        p.append(line(xx, ty - 5, xx, ty + 5, color="#ffffff", sw=1.2))
    # дужка Δx над одним шматочком
    xa = tx0 + 2*(tx1-tx0)/6
    xb = tx0 + 3*(tx1-tx0)/6
    p.append(line(xa, 52, xb, 52, color=MUTED, sw=1.0))
    p.append(line(xa, 52, xa, 60, color=MUTED, sw=1.0))
    p.append(line(xb, 52, xb, 60, color=MUTED, sw=1.0))
    p.append(text((xa+xb)/2, 48, "Δx", size=11, color=MUTED, italic=True))

    # низ: еквівалентна LC-драбина
    ey = 210          # верхня рейка (сигнал)
    eg = 288          # нижня рейка (земля)
    ex0, ex1 = 70, 710
    p.append(text((ex0+ex1)/2, 168, "кожен шматочок Δx → послідовна ΔL і шунтова ΔC", size=12, bold=True, color=INK))
    p.append(line(ex0, eg, ex1, eg, color=GND, sw=2.4))           # рейка землі
    # чотири LC-ланки: котушка на верхній рейці, конденсатор униз на землю
    nseg = 4
    seg = (ex1 - ex0 - 40) / nseg
    x = ex0 + 20
    def coil(x1, x2, y):
        # проста «котушка»: кілька дужок
        n = 4; step = (x2 - x1) / n; f = []
        for k in range(n):
            cx = x1 + step*(k+0.5)
            f.append('<path d="M %.1f %.1f q %.1f -14 %.1f 0" fill="none" stroke="%s" stroke-width="2"/>'
                     % (x1+step*k, y, step/2, step, WAVE))
        return "".join(f)
    def cap(cx, y1, y2):
        # конденсатор: дві пластини між рейками
        my = (y1+y2)/2
        return (line(cx, y1, cx, my-5, color=INK, sw=1.6) +
                line(cx-11, my-5, cx+11, my-5, color=INK, sw=2.2) +
                line(cx-11, my+2, cx+11, my+2, color=INK, sw=2.2) +
                line(cx, my+2, cx, y2, color=INK, sw=1.6))
    prevx = ex0
    for s in range(nseg):
        x1 = ex0 + 20 + s*seg
        x2 = x1 + seg*0.55
        node = x1 + seg*0.72
        p.append(coil(x1, x2, ey))
        p.append(line(x2, ey, x1+seg, ey, color=INK, sw=1.6))    # рейка далі
        if s == 0:
            p.append(line(ex0, ey, x1, ey, color=INK, sw=1.6))
        p.append(cap(node, ey, eg))
        p.append(circle(node, ey, 2.4, fill=INK, stroke=INK, sw=1))
        if s == 1:
            b,_,_ = textbox((x1+x2)/2, ey - 26, "ΔL", size=11, color=WAVE, fill="#eaf0fd", stroke=WAVE, sw=1.1, pad=4)
            p.append(b)
            b,_,_ = textbox(node + 46, (ey+eg)/2, "ΔC", size=11, color=INK, fill="#ffffff", stroke=INK, sw=1.1, pad=4)
            p.append(b)
    # вхід зліва: сюди «дивиться» хвиля і бачить Z₀
    p.append(arrow(ex0 - 2, ey, ex0 + 16, ey, color=SIG, sw=2.0))
    b,_,_ = textbox(ex0 + 4, ey - 30, "хвиля бачить\nтут Z₀ = √(L′/C′)", size=10.5, color=SIG,
                    fill="#fdecea", stroke=SIG, sw=1.1, pad=5)
    p.append(b)
    p.append(text((ex0+ex1)/2, H - 12,
                  "L′, C′ — на одиницю довжини; ланок нескінченно багато, ланка нескінченно мала",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "rlgc-ladder.svg"), W, H, *p)


# ── microstrip-xsec: розріз мікросмужки — поле в FR-4 і в повітрі ────────────
# Ідея: робоча геометрія Z₀. Смужка шириною W на висоті h над суцільною землею;
# силові лінії йдуть і крізь FR-4, і крізь повітря — тому «ефективна» εr десь
# посередині. Це пояснює, ЧОМУ у формулу входить εeff, а не голе εr.
def fig_microstrip_xsec():
    W, H = 820, 370
    p = []
    p.append(text(W/2, 30, "Мікросмужка в розрізі: поле ділиться між FR-4 і повітрям", size=15, bold=True))

    # малюнок тримаємо ЛІВОРУЧ (до x≈540), висновок — окремим стовпчиком праворуч,
    # щоб рамки й лінії не наповзали одна на одну
    cx = 300
    core_x0, core_w = 120, 380
    core_y, core_h = 168, 108
    p.append(rect(core_x0, core_y, core_w, core_h, fill=CORE, stroke="#b8a55f", sw=1.5, rx=3))
    for i in range(1, 5):
        yy = core_y + i*core_h/5
        p.append(line(core_x0+8, yy, core_x0+core_w-8, yy, color="#c7b673", sw=0.8, dash="5 6"))
    # земля — суцільна мідь під осердям
    gy = core_y + core_h
    p.append(rect(core_x0, gy, core_w, 12, fill=COPPER, stroke=COPDK, sw=1.2, rx=1))
    # смужка-провідник зверху осердя
    strip_w = 80
    strip_y = core_y - 12
    p.append(rect(cx - strip_w/2, strip_y, strip_w, 12, fill=SIG, stroke="#8a2b1f", sw=1.3, rx=2))
    # зонні підписи — з КРАЮ, не на полі
    p.append(text(core_x0 + 60, core_y - 30, "повітря (εr ≈ 1)", size=10.5, color=MUTED))
    # підпис FR-4 — праворуч від пучка поля, у чистій частині осердя
    p.append(text(core_x0 + core_w - 66, core_y + core_h/2 + 4, "FR-4 (εr ≈ 4.3)", size=11.5, color="#8a7a2f", bold=True))

    # силові лінії поля: центральні — прямо вниз крізь FR-4; крайові дуги — крізь повітря
    for dx in (-24, -10, 10, 24):
        p.append(line(cx+dx, strip_y+12, cx+dx*0.5, gy, color=WAVE, sw=1.3))
    for sgn in (-1, 1):
        x0 = cx + sgn*strip_w/2
        p.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="4 4"/>'
                 % (x0, strip_y+6, x0+sgn*58, strip_y-4, x0+sgn*76, gy-28, x0+sgn*48, gy, WAVE))
    # підпис «поле» — ліворуч від пучка ліній, у порожнечі (без виноски-різака)
    p.append(text(core_x0 + 40, strip_y + 52, "поле", size=10.5, color=WAVE, bold=True, anchor="middle"))

    # розмір W (над смужкою)
    p.append(line(cx - strip_w/2, strip_y - 14, cx + strip_w/2, strip_y - 14, color=INK, sw=1.2))
    p.append(text(cx, strip_y - 18, "W", size=12, color=INK, bold=True))
    # розмір h (ліворуч від осердя)
    hx = core_x0 - 22
    p.append(line(hx, strip_y+6, hx, gy, color=INK, sw=1.2))
    p.append(line(hx-4, strip_y+6, hx+4, strip_y+6, color=INK, sw=1.2))
    p.append(line(hx-4, gy, hx+4, gy, color=INK, sw=1.2))
    p.append(text(hx - 12, (strip_y+gy)/2 + 4, "h", size=12, color=INK, bold=True, anchor="middle"))
    # підпис землі
    p.append(text(cx, gy + 30, "суцільна земля", size=11, color=COPDK, bold=True))

    # роздільник і висновок ПРАВОРУЧ, в чистому полі
    p.append(line(560, 60, 560, H - 26, color="#d0d4d8", sw=1.2, dash="6 5"))
    b, bw, bh = textbox(688, 150,
                        "частина поля — у FR-4,\nчастина — у повітрі →\nεeff десь ПОСЕРЕДИНІ:\n1 < εeff < εr",
                        size=10.5, color=INK, fill="#f4f6f8", stroke=MUTED, sw=1.2, pad=8)
    p.append(b)
    b2, _, _ = textbox(688, 250,
                       "ширше W →\nбільша ємність →\nменший Z₀",
                       size=10.5, color=SIG, fill="#fdecea", stroke=SIG, sw=1.2, pad=8)
    p.append(b2)

    render(os.path.join(OUT, "microstrip-xsec.svg"), W, H, *p)


# ── reflection-boundary: відбиття від неузгодженого кінця (Γ) ────────────────
# Ідея: падаюча хвиля на стику Z₀|Z_L ділиться на пройдену й відбиту; частка
# відбитого — Γ = (Z_L−Z₀)/(Z_L+Z₀). Три канонічні випадки: відкрито (+1),
# узгоджено (0), коротко (−1). Це фізика, з якої росте «навіщо 50 Ω і термінація».
def fig_reflection_boundary():
    W, H = 780, 380
    p = []
    p.append(text(W/2, 30, "Відбиття від кінця: скільки хвилі вертає, вирішує Γ", size=15, bold=True))

    # горизонтальна лінія передачі з Z₀, стик праворуч
    lx0, lx1 = 70, 470
    ly = 120
    p.append(line(lx0, ly, lx1, ly, color=INK, sw=2.6))
    p.append(text((lx0+lx1)/2, ly - 40, "лінія  Z₀ = 50 Ω", size=12, color=INK, bold=True))
    # падаюча хвиля →
    p.append(arrow(lx0+30, ly - 16, lx0+150, ly - 16, color=SIG, sw=2.2))
    p.append(text(lx0+90, ly - 22, "падаюча", size=10.5, color=SIG, bold=True))
    # відбита хвиля ←
    p.append(arrow(lx1-30, ly + 20, lx1-150, ly + 20, color=WAVE, sw=2.2))
    p.append(text(lx1-92, ly + 34, "відбита = Γ·падаюча", size=10.5, color=WAVE, bold=True))
    # стик і навантаження Z_L
    p.append(line(lx1, ly - 34, lx1, ly + 34, color=MUTED, sw=1.4, dash="5 4"))
    p.append(rect(lx1, ly - 22, 46, 44, fill="#f4f6f8", stroke=INK, sw=1.4, rx=4))
    p.append(text(lx1+23, ly + 5, "Z_L", size=12, color=INK, bold=True))
    # формула Γ під стиком
    b,_,_ = textbox((lx0+lx1)/2, ly + 74, "Γ = (Z_L − Z₀) / (Z_L + Z₀)", size=13, color=INK,
                    fill="#ffffff", stroke=INK, sw=1.3, pad=7)
    p.append(b)

    # три випадки праворуч — стовпчик карток
    rx = 560
    cases = [
        ("Z_L → ∞  (відкрито)",  "Γ = +1",  "уся хвиля назад,\nтой самий знак", POS, "#fdecea"),
        ("Z_L = Z₀  (узгоджено)", "Γ = 0",   "нічого не вертає —\nвся енергія пройшла", FIELD, "#eafaf0"),
        ("Z_L = 0  (коротко)",   "Γ = −1",  "уся хвиля назад,\nоберт. знак", NEG, "#eaf0fd"),
    ]
    cy = 92
    for title_, gam, note, col, bg in cases:
        p.append(text(rx, cy, title_, size=11, color=INK, bold=True, anchor="start"))
        b,_,_ = textbox(rx + 150, cy + 22, gam, size=13, color=col, fill=bg, stroke=col, sw=1.3, pad=6)
        p.append(b)
        p.append(mtext(rx, cy + 40, note, size=10, color=MUTED, anchor="start"))
        cy += 92

    p.append(text(W/2, H - 12,
                  "Γ = 0 (узгоджено) — жодного відлуння; будь-яке неузгодження вертає частину назад",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "reflection-boundary.svg"), W, H, *p)


if __name__ == "__main__":
    fig_board_anatomy()
    fig_copper_pattern()
    fig_via_types()
    fig_rlgc_ladder()
    fig_microstrip_xsec()
    fig_reflection_boundary()
    print("figs done:", os.listdir(OUT))
