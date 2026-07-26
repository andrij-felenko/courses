# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

VIOLET = "#8a5fb0"


def chip(x, y, w, h, s, col=INK, fill=FILL, size=12, bold=True):
    """Маленька підписана клітинка (вихідний блок / ключ)."""
    return fitbox(x, y, w, h, s, size=size, bold=bold, color=col, fill=fill, stroke=col, sw=1.6)


# ══════════════════════════════════════════════════════════════════════════════
# next-bit.svg — тест наступного біта: передбачний генератор vs CSPRNG
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: обидва потоки на вигляд однакові, але лінійний віддає стан із кількох
# виходів (наступний ВІДОМИЙ), а CSPRNG лишає наступний біт чесною монетою.

def fig_next_bit():
    W, H = 780, 380
    p = []
    # ── рядок 1: лінійний генератор ──
    y1 = 92
    lab, lw, lh = textbox(108, y1 + 22, "лінійний\n(LCG · LFSR · MT)", size=12, bold=True,
                          color=NEG, fill="#eef4ff", stroke=NEG, sw=1.8, min_w=150)
    p.append(lab)
    # побачені виходи
    xs = 216
    for i in range(3):
        p.append(chip(xs + i * 58, y1, 50, 44, "x%d" % i, col=NEG, fill="#eef4ff"))
    p.append(arrow(xs + 3 * 58 + 4, y1 + 22, xs + 3 * 58 + 96, y1 + 22, color=INK, sw=2))
    p.append(text(xs + 3 * 58 + 50, y1 - 4, "3 виходи", size=10, color=MUTED, bold=True))
    p.append(text(xs + 3 * 58 + 50, y1 + 46, "→ розв'язати рівняння", size=10, color=MUTED))
    res1, rw1, rh1 = textbox(xs + 3 * 58 + 176, y1 + 22, "наступний біт:\nВІДОМИЙ", size=12,
                             bold=True, color=POS, fill="#fdecea", stroke=POS, sw=2)
    p.append(res1)

    # роздільник
    p.append(line(70, 196, W - 40, 196, color="#d0d4da", sw=1.2, dash="4 4"))

    # ── рядок 2: CSPRNG ──
    y2 = 268
    lab2, lw2, lh2 = textbox(108, y2 + 22, "CSPRNG", size=13, bold=True,
                             color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8, min_w=150)
    p.append(lab2)
    xs2 = 216
    labels = ["b0", "b1", "b2", "…", "bn"]
    for i, s in enumerate(labels):
        fill = "#eafaf0" if s != "…" else BG
        stc = FIELD if s != "…" else "none"
        if s == "…":
            p.append(text(xs2 + i * 46 + 22, y2 + 28, "…", size=18, color=MUTED, bold=True))
        else:
            p.append(chip(xs2 + i * 46, y2, 40, 44, s, col=FIELD, fill="#eafaf0", size=11))
    ax = xs2 + 5 * 46 + 2
    p.append(arrow(ax, y2 + 22, ax + 92, y2 + 22, color=INK, sw=2))
    p.append(text(ax + 46, y2 - 4, "скільки завгодно", size=10, color=MUTED, bold=True))
    p.append(text(ax + 46, y2 + 46, "виходів", size=10, color=MUTED))
    # монета
    cx, cy = ax + 168, y2 + 22
    p.append(circle(cx, cy, 26, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(text(cx, cy + 7, "½", size=20, color=FIELD, bold=True))
    p.append(text(cx, cy + 50, "чесна монета", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "next-bit.svg"), W, H, *p,
           title="Тест наступного біта: ось у чому різниця")


# ══════════════════════════════════════════════════════════════════════════════
# architecture.svg — дві частини: джерело ентропії → розширювач → потік
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: уся непередбачність народжується ліворуч (повільне фізичне джерело),
# праворуч детермінований розширювач лише розмножує її; секрет — стан.

def fig_architecture():
    W, H = 840, 400
    p = []
    # ── джерело ентропії (ліворуч) ──
    src_x, src_y, src_w, src_h = 56, 110, 190, 128
    p.append(rect(src_x, src_y, src_w, src_h, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(text(src_x + src_w / 2, src_y + 26, "Джерело ентропії", size=13, color=NEG, bold=True))
    for i, s in enumerate(["тепловий і дробовий шум", "джитер тактів, RDSEED", "час подій, переривань"]):
        p.append(text(src_x + src_w / 2, src_y + 52 + i * 20, s, size=10, color=INK))
    p.append(text(src_x + src_w / 2, src_y + src_h + 20, "повільно · мало ·", size=10, color=NEG, bold=True))
    p.append(text(src_x + src_w / 2, src_y + src_h + 35, "СПРАВЖНЯ непередбачність", size=10, color=NEG, bold=True))

    # стрілка «зерно»
    a1x = src_x + src_w
    p.append(arrow(a1x + 4, src_y + src_h / 2, a1x + 92, src_y + src_h / 2, color=INK, sw=2.4))
    p.append(text(a1x + 48, src_y + src_h / 2 - 12, "зерно", size=11, color=INK, bold=True))
    p.append(text(a1x + 48, src_y + src_h / 2 + 22, "256 біт", size=10, color=MUTED))

    # ── розширювач (центр) ──
    ex_x, ex_y, ex_w, ex_h = a1x + 96, 96, 240, 156
    p.append(rect(ex_x, ex_y, ex_w, ex_h, fill="#f4f6f8", stroke=INK, sw=2))
    p.append(text(ex_x + ex_w / 2, ex_y + 24, "Детермінований", size=13, color=INK, bold=True))
    p.append(text(ex_x + ex_w / 2, ex_y + 42, "розширювач (DRBG)", size=13, color=INK, bold=True))
    # внутрішній стан — секрет
    st = fitbox(ex_x + 24, ex_y + 58, ex_w - 48, 34, "внутрішній стан", size=11, bold=True,
                color=POS, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(st)
    ow = fitbox(ex_x + 24, ex_y + 100, ex_w - 48, 34, "одностороння функція", size=11, bold=True,
                color=VIOLET, fill="#f3edf9", stroke=VIOLET, sw=1.8)
    p.append(ow)
    # ярлик «секрет»
    p.append(text(ex_x + ex_w / 2, ex_y + ex_h + 20, "СЕКРЕТ — тільки стан", size=11, color=POS, bold=True))

    # стрілка «потік»
    a2x = ex_x + ex_w
    p.append(arrow(a2x + 4, ex_y + ex_h / 2, a2x + 74, ex_y + ex_h / 2, color=INK, sw=2.4))

    # ── вихід (праворуч) ──
    ox = a2x + 80
    oy = ex_y + 20
    for i in range(6):
        yy = oy + i * 22
        p.append(rect(ox, yy, 96, 15, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(ox + 48, oy - 12, "потік виходу", size=12, color=FIELD, bold=True))
    p.append(text(ox + 48, oy + 6 * 22 + 14, "гігабайти · швидко", size=10, color=FIELD, bold=True))

    # нижня стрічка-висновок
    band, bw, bh = textbox(W / 2, 372,
                           "уся непередбачність народжується ліворуч — праворуч вона лише розмножується",
                           size=12, bold=True, color=INK, fill="#fffbe6", stroke="#d98a00", sw=1.6)
    p.append(band)

    render(os.path.join(OUT, "architecture.svg"), W, H, *p,
           title="Дві частини CSPRNG: зібрати ентропію → розтягнути")


# ══════════════════════════════════════════════════════════════════════════════
# forward-secrecy.svg — храповик швидкого стирання ключа
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: ланцюг ключів однобічний; кожен дає вихід + наступний ключ і стирається.
# Захоплення пізнього ключа не дає відкрутити до раніших виходів.

def fig_forward_secrecy():
    W, H = 840, 360
    p = []
    keys = ["K0", "K1", "K2", "K3"]
    kx0, ky = 90, 140
    step = 200
    kw, kh = 96, 52

    for i, k in enumerate(keys):
        x = kx0 + i * step
        captured = (i == 2)
        col = POS if captured else INK
        fill = "#fdecea" if captured else "#f4f6f8"
        p.append(chip(x, ky, kw, kh, k, col=col, fill=fill, size=15))
        # стерто?
        if i < 2:
            p.append(text(x + kw / 2, ky - 12, "стерто ✕", size=11, color=MUTED, bold=True))
        # вихід донизу
        p.append(arrow(x + kw / 2, ky + kh + 2, x + kw / 2, ky + kh + 40, color=FIELD, sw=1.8))
        outb = fitbox(x + kw / 2 - 52, ky + kh + 42, 104, 30, "вихід %d" % i, size=11,
                      bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.5)
        p.append(outb)
        # однобічна стрілка до наступного ключа
        if i < len(keys) - 1:
            sx = x + kw + 2
            ex = x + step - 2
            p.append(arrow(sx, ky + kh / 2, ex, ky + kh / 2, color=INK, sw=2.4))
            p.append(text((sx + ex) / 2, ky + kh / 2 - 12, "одностороннє", size=10, color=INK, bold=True))
            # заборонений зворотний хід
            p.append(text((sx + ex) / 2, ky + kh / 2 + 22, "назад ✕", size=10, color=POS, bold=True))

    # маркер захоплення на K2
    x2 = kx0 + 2 * step
    p.append(text(x2 + kw / 2, ky + kh + 96, "супротивник", size=11, color=POS, bold=True))
    p.append(text(x2 + kw / 2, ky + kh + 112, "захопив стан тут", size=11, color=POS, bold=True))

    # висновок
    band, bw, bh = textbox(W / 2, 40,
                           "захоплення K2 псує лише майбутнє — виходи 0 і 1 уже недосяжні",
                           size=12, bold=True, color=INK, fill="#fffbe6", stroke="#d98a00", sw=1.6)
    p.append(band)

    render(os.path.join(OUT, "forward-secrecy.svg"), W, H, *p,
           title="Храповик стирання ключа: минуле під замком")


# ══════════════════════════════════════════════════════════════════════════════
# reseed.svg — пересів як відновлення після компрометації
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: до пересіву вихід передбачний (стан відомий); підмішування свіжої
# ентропії, якої супротивник не бачив, робить майбутній стан непередбачним.

def fig_reseed():
    W, H = 840, 350
    p = []
    mid = 430

    # ліва зона — скомпрометовано
    p.append(rect(48, 84, mid - 48 - 20, 200, fill="#fdecea", stroke="none", rx=10))
    p.append(text((48 + mid - 20) / 2, 108, "стан відомий супротивнику", size=12, color=POS, bold=True))
    # відомий стан
    sb = fitbox(96, 150, 120, 46, "стан S", size=13, bold=True, color=POS, fill="#fff", stroke=POS, sw=2)
    p.append(sb)
    for i in range(3):
        p.append(rect(240, 150 + i * 18, 110, 12, fill="#fff", stroke=POS, sw=1.2, rx=3))
    p.append(text(295, 230, "вихід передбачний", size=11, color=POS, bold=True))

    # вузол пересіву
    mixx = mid + 6
    p.append(circle(mixx, 173, 30, fill="#f3edf9", stroke=VIOLET, sw=2.4))
    p.append(text(mixx, 168, "Hash", size=13, color=VIOLET, bold=True))
    p.append(text(mixx, 184, "змішати", size=9, color=VIOLET))
    # стрілка стану у вузол
    p.append(arrow(216 + 8, 173, mixx - 32, 173, color=INK, sw=2))
    # свіжа ентропія згори
    ent = fitbox(mixx - 92, 74, 184, 40, "свіжа ентропія\n(супротивник не бачив)", size=10,
                 bold=True, color=NEG, fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(ent)
    p.append(arrow(mixx, 116, mixx, 141, color=NEG, sw=2))

    # права зона — відновлено
    rx0 = mixx + 40
    p.append(rect(rx0, 84, W - rx0 - 40, 200, fill="#eafaf0", stroke="none", rx=10))
    p.append(text((rx0 + W - 40) / 2, 108, "непередбачний знову", size=12, color=FIELD, bold=True))
    sb2 = fitbox(rx0 + 24, 150, 120, 46, "стан S′", size=13, bold=True, color=FIELD, fill="#fff", stroke=FIELD, sw=2)
    p.append(sb2)
    p.append(arrow(mixx + 32, 173, rx0 + 20, 173, color=INK, sw=2))
    for i in range(3):
        p.append(rect(rx0 + 160, 150 + i * 18, 110, 12, fill="#fff", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(rx0 + 215, 230, "вихід закритий", size=11, color=FIELD, bold=True))

    # висновок
    band, bw, bh = textbox(W / 2, 322,
                           "досить, щоб чистим було одне з двох джерел суміші — і майбутнє знову таємне",
                           size=12, bold=True, color=INK, fill="#fffbe6", stroke="#d98a00", sw=1.6)
    p.append(band)

    render(os.path.join(OUT, "reseed.svg"), W, H, *p,
           title="Пересів: відновлення після витоку стану")


# ══════════════════════════════════════════════════════════════════════════════
# fke-layout.svg — розкладка одного виклику generate() (швидке стирання ключа)
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: перший ChaCha-блок ділиться навпіл — перші 32 байти стають майбутнім
# ключем (таємні, не віддаються), решта потоку йде користувачеві; старий ключ
# негайно затирається. Байтовий, кодовий погляд на храповик.

def fig_fke_layout():
    W, H = 900, 372
    p = []
    y, h = 168, 60

    # ── старий ключ K0 ──
    p.append(fitbox(44, y, 108, h, "K₀\nстарий ключ", size=13, bold=True,
                    color=POS, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(44 + 54, y + h + 20, "стерти ✕ негайно", size=11, color=MUTED, bold=True))
    p.append(arrow(44 + 108 + 3, y + h / 2, 186, y + h / 2, color=INK, sw=2.2))

    # ── блокова функція ──
    p.append(fitbox(188, y - 2, 118, h + 4, "ChaCha20\nблокова ф-я", size=12, bold=True,
                    color=VIOLET, fill="#f3edf9", stroke=VIOLET, sw=2))
    p.append(arrow(188 + 118 + 3, y + h / 2, 349, y + h / 2, color=INK, sw=2.2))

    # ── потік: блок 0 ділиться навпіл, далі цілі блоки виходу ──
    x0, hw = 352, 66
    # блок 0, ліва половина — майбутній ключ
    p.append(rect(x0, y, hw, h, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(x0 + hw / 2, y + h / 2 - 3, "K₁", size=15, color=POS, bold=True))
    p.append(text(x0 + hw / 2, y + h / 2 + 15, "32 Б", size=10, color=MUTED))
    # блок 0, права половина — вихід
    p.append(rect(x0 + hw, y, hw, h, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(x0 + hw + hw / 2, y + h / 2 + 4, "вихід", size=12, color=FIELD, bold=True))
    # блоки 1, 2 — цілком у вихід (64 Б = дві половини)
    bw = hw * 2
    for i in range(2):
        bx = x0 + bw + i * bw
        p.append(rect(bx, y, bw, h, fill="#eafaf0", stroke=FIELD, sw=2))
        p.append(text(bx + bw / 2, y + h / 2 + 4, "вихід", size=12, color=FIELD, bold=True))
    p.append(text(x0 + bw + 2 * bw + 18, y + h / 2 + 7, "…", size=22, color=MUTED, bold=True))

    # підписи блоків
    for s, bx, w in [("блок 0", x0, bw), ("блок 1", x0 + bw, bw), ("блок 2", x0 + 2 * bw, bw)]:
        p.append(text(bx + w / 2, y + h + 18, s, size=10, color=MUTED))

    # K1 → ключ наступного виклику (стрілка вгору + рамка)
    kx = x0 + hw / 2
    p.append(arrow(kx, y - 3, kx, y - 40, color=POS, sw=2))
    nb, nbw, nbh = textbox(kx + 8, y - 56, "→ ключ наступного виклику", size=11,
                           bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6)
    p.append(nb)

    # дужка виходу
    ox0, ox1 = x0 + hw, x0 + bw + 2 * bw
    p.append(line(ox0, y + h + 30, ox1, y + h + 30, color=FIELD, sw=2.2))
    p.append(text((ox0 + ox1) / 2, y + h + 48, "випадковий вихід цього виклику",
                  size=11, color=FIELD, bold=True))

    # висновок унизу
    band, bw2, bh2 = textbox(W / 2, 352,
                             "перші 32 байти потоку — таємний майбутній ключ; усе інше віддають користувачеві",
                             size=12, bold=True, color=INK, fill="#fffbe6", stroke="#d98a00", sw=1.6)
    p.append(band)

    render(os.path.join(OUT, "fke-layout.svg"), W, H, *p,
           title="Розкладка одного виклику generate()")


# ══════════════════════════════════════════════════════════════════════════════
# hybrid-ladder.svg — гібридна драбина H0..Hl для теореми Яо (вставка math)
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: межа між виходом генератора (зелене) і шумом (синє) сунеться на один біт;
# кінці — G(s) проти Uₗ; сусіди різняться рівно в одному біті → передбачник.

def fig_hybrid_ladder():
    W, H = 900, 508
    p = []
    l = 5
    cw, ch, gap = 54, 42, 8
    x0 = 258
    y0 = 96
    rh = 56
    p.append(text(W / 2, 52, "зелена клітинка — біт із G(s)     ·     синя — свіжий шум r",
                  size=12, color=MUTED, bold=True))
    # рядки H0..Hl: у Hᵢ перші i клітинок зелені (з генератора), решта сині (шум)
    for i in range(l + 1):
        ry = y0 + i * rh
        p.append(text(x0 - 24, ry + ch / 2 + 5, "H%d" % i, size=15, color=INK, bold=True, anchor="end"))
        for j in range(l):
            cx = x0 + j * (cw + gap)
            if j < i:
                p.append(chip(cx, ry, cw, ch, "y", col=FIELD, fill="#eafaf0", size=13))
            else:
                p.append(chip(cx, ry, cw, ch, "r", col=NEG, fill="#eef4ff", size=13))
    right = x0 + l * (cw + gap) + 20
    p.append(text(right, y0 + ch / 2 + 5, "= Uₗ   чистий шум", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(right, y0 + l * rh + ch / 2 + 5, "= G(s)   вихід генератора", size=12, color=FIELD, bold=True, anchor="start"))
    # підсвітити перехід H2 → H3, відмінна клітинка — позиція j=2 (біт 3)
    hj = 2
    for i in (2, 3):
        ry = y0 + i * rh
        cx = x0 + hj * (cw + gap)
        p.append(rect(cx - 4, ry - 4, cw + 8, ch + 8, fill="none", stroke=POS, sw=2.6, rx=9))
    # анотація праворуч від рядків 2–3
    ay = y0 + 2 * rh + ch / 2 + rh / 2
    note, nw, nh = textbox(right + 138, ay, "різняться лише в біті 3\n→ розрізнити Hᵢ від Hᵢ₊₁\n= вгадати наступний біт",
                           size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(note)
    p.append(arrow(x0 + hj * (cw + gap) + cw + 6, ay, right + 138 - nw / 2 - 4, ay, color=POS, sw=1.8))
    # телескоп-висновок унизу
    band, bw, bh = textbox(W / 2, H - 32,
                           "ε = δ₀ + δ₁ + … + δₗ₋₁   (щілини між сусідніми Hᵢ)     ⟹     якась щілина  δᵢ ≥ ε ∕ l",
                           size=12, bold=True, color=INK, fill="#fffbe6", stroke="#d98a00", sw=1.6)
    p.append(band)
    render(os.path.join(OUT, "hybrid-ladder.svg"), W, H, *p,
           title="Гібридна драбина: від шуму до генератора біт за бітом")


# ══════════════════════════════════════════════════════════════════════════════
# min-entropy.svg — мін-ентропія vs Шеннонова (вставка math)
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: пік маси ½ на відомому рядку робить Шеннонову оманливо високою (усереднює
# по хвості), а мін-ентропію — чесною (1 біт = вгадати з ім-стю ½).

def fig_minentropy():
    W, H = 880, 470
    p = []
    base = 348
    left = 118
    # осі
    p.append(arrow(left, base, W - 56, base, color=INK, sw=1.8))
    p.append(arrow(left, base, left, 92, color=INK, sw=1.8))
    p.append(text(W - 56, base + 24, "можливі зерна", size=11, color=MUTED, anchor="end"))
    p.append(text(left - 6, 100, "ймовірність", size=11, color=MUTED, anchor="start"))
    # пік — маса ½ на 0^128
    sx, sw_, stop = left + 30, 66, 122
    p.append(rect(sx, stop, sw_, base - stop, fill="#fdecea", stroke=POS, sw=2.4))
    p.append(text(sx + sw_ / 2, stop - 12, "½", size=20, color=POS, bold=True))
    p.append(text(sx + sw_ / 2, base + 20, "0¹²⁸", size=12, color=POS, bold=True))
    p.append(text(sx + sw_ / 2, base + 36, "відомий рядок", size=10, color=MUTED))
    # хвіст — 2^128−1 рівноймовірних, кожен ≈ 2^−129
    tx0 = sx + sw_ + 46
    n = 30
    tw = (W - 76 - tx0) / n
    for k in range(n):
        bx = tx0 + k * tw
        p.append(rect(bx, base - 9, tw * 0.68, 9, fill="#eef4ff", stroke=NEG, sw=1.0))
    p.append(text((tx0 + W - 76) / 2, base - 22, "2¹²⁸ − 1 рівноймовірних рядків, кожен ≈ 2⁻¹²⁹",
                  size=11, color=NEG, bold=True))
    p.append(text((tx0 + W - 76) / 2, base + 20, "довгий низький хвіст (сумарна маса ½)", size=10, color=MUTED))
    # мітка мін-ентропії
    hb, hbw, hbh = textbox(430, 150, "H∞ = − log₂ ½ = 1 біт\n(найгірший випадок — те, у що б'є супротивник)",
                           size=11, bold=True, color=POS, fill=BG, stroke=POS, sw=1.8)
    p.append(hb)
    p.append(arrow(sx + sw_ + 4, stop + 26, 430 - hbw / 2 - 4, 150, color=POS, sw=1.6))
    # мітка Шеннонової
    sb, sbw, sbh = textbox(W / 2 + 70, 258, "H(X) ≈ 65 біт   (Шеннонова, середнє)\nоманливо високе — усереднення тоне в хвості",
                           size=11, bold=True, color=NEG, fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(sb)
    # висновок
    band, bw, bh = textbox(W / 2, H - 26,
                           "Шеннон усереднює й тоне в хвості; мін-ентропія бачить пік — рівно те, у що б'є супротивник",
                           size=12, bold=True, color=INK, fill="#fffbe6", stroke="#d98a00", sw=1.6)
    p.append(band)
    render(os.path.join(OUT, "min-entropy.svg"), W, H, *p,
           title="Мін-ентропія vs Шеннонова: чому середнє бреше про зерно")


# ══════════════════════════════════════════════════════════════════════════════
# timeline-disasters.svg — дві нитки історії: конструкції визрівають ↑, катастрофи ↓
# ══════════════════════════════════════════════════════════════════════════════
# Ідея: над віссю часу теорія й конструкції поволі визрівають (синє — означення,
# зелене — інженерні схеми), під віссю практика раз по раз падає (червоне).
# Кожне падіння штовхало вгору наступну конструкцію.

def fig_timeline_disasters():
    W, H = 1440, 436
    ax_y = 218
    x0, step = 190, 115
    p = []

    # вісь часу
    p.append(arrow(44, ax_y, W - 34, ax_y, color=INK, sw=2.4))
    p.append(text(W - 62, ax_y - 12, "час", size=12, color=MUTED, bold=True, italic=True))

    # яруси (щоб сусідні картки не накладалися по горизонталі)
    A_FAR, A_NEAR = 78, 168     # над віссю
    B_NEAR, B_FAR = 268, 358    # під віссю

    def event(i, y, lines, col, fill):
        x = x0 + i * step
        if y < ax_y:
            p.append(line(x, y + 31, x, ax_y, color=col, sw=1.5, dash="3 3"))
        else:
            p.append(line(x, ax_y, x, y - 31, color=col, sw=1.5, dash="3 3"))
        p.append(circle(x, ax_y, 4.5, fill=col, stroke=col, sw=1))
        box, bw, bh = textbox(x, y, "\n".join(lines), size=12, bold=True,
                              color=col, fill=fill, stroke=col, sw=1.8, pad=9)
        p.append(box)

    BLUE, GREEN, RED = "#eef4ff", "#eafaf0", "#fdecea"

    # ── теорія / конструкції (над віссю) ──
    event(0,  A_NEAR, ["1982", "Означення", "Блюм · Мікалі · Яо"], NEG,   BLUE)
    event(1,  A_FAR,  ["1986", "Доказовий ідеал", "Блюм–Блюм–Шуб"], NEG,  BLUE)
    event(3,  A_NEAR, ["1999", "Yarrow"], FIELD, GREEN)
    event(4,  A_FAR,  ["2003", "Fortuna"], FIELD, GREEN)
    event(7,  A_NEAR, ["2008", "ChaCha20", "Бернстайн"], FIELD, GREEN)
    event(10, A_FAR,  ["2014", "arc4random", "→ ChaCha20"], FIELD, GREEN)

    # ── катастрофи (під віссю) ──
    event(2,  B_NEAR, ["1995", "Netscape", "ентропію вгадали"], POS, RED)
    event(5,  B_FAR,  ["2007", "Dual_EC", "задні двері"], POS, RED)
    event(6,  B_NEAR, ["2008", "Debian", "2¹⁵ ключів"], POS, RED)
    event(8,  B_FAR,  ["2010", "PlayStation 3", "сталий номер"], POS, RED)
    event(9,  B_NEAR, ["2013", "Android", "крали біткоїни"], POS, RED)

    # підписи ниток у лівому жолобі
    lab_top, _, _ = textbox(80, A_FAR, "конструкції\nвизрівають ↑", size=12, bold=True,
                            color=FIELD, fill=BG, stroke=FIELD, sw=1.6, pad=8)
    p.append(lab_top)
    lab_bot, _, _ = textbox(80, B_FAR, "катастрофи\n↓ навчають", size=12, bold=True,
                            color=POS, fill=BG, stroke=POS, sw=1.6, pad=8)
    p.append(lab_bot)

    render(os.path.join(OUT, "timeline-disasters.svg"), W, H, *p,
           title="Дві нитки історії випадковості: конструкції визрівають, катастрофи навчають")


if __name__ == "__main__":
    fig_next_bit()
    fig_architecture()
    fig_forward_secrecy()
    fig_reseed()
    fig_fke_layout()
    fig_hybrid_ladder()
    fig_minentropy()
    fig_timeline_disasters()
    print("OK: figures written to", OUT)
