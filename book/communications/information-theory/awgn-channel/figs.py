# -*- coding: utf-8 -*-
"""Фігури до теми «Канал AWGN» (awgn-channel).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Модель каналу: r = s + n (адитивність) ─────────────────────────────────
# Ідея, яку важко передати прозою: увесь канал AWGN — це один суматор, що додає
# до сигналу незалежний шум. Показати блок-схему очима.
def fig_channel_model():
    W, H = 720, 320
    f = []
    ymid = 129

    # передавач
    f.append(rect(55, 95, 140, 68, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(125, 124, "Передавач", 13, INK, "middle", bold=True))
    f.append(text(125, 150, "s(t)", 13, NEG, "middle", bold=True))

    # ліва лінія s(t) → суматор
    f.append(arrow(196, ymid, 356, ymid, color=INK, sw=2))
    f.append(text(272, 118, "s(t)", 11, NEG, "middle", bold=True))

    # суматор
    f.append(plus(378, ymid, 17))

    # джерело шуму знизу
    f.append(rect(298, 232, 160, 46, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    f.append(text(378, 261, "Шум  n(t)", 13, POS, "middle", bold=True))
    f.append(arrow(378, 230, 378, 150, color=POS, sw=2))
    f.append(text(400, 196, "n(t)", 11, POS, "start", bold=True))

    # права лінія → приймач
    f.append(arrow(399, ymid, 513, ymid, color=INK, sw=2))
    f.append(text(456, 118, "r(t)", 11, FIELD, "middle", bold=True))

    # приймач
    f.append(rect(515, 95, 152, 68, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(591, 124, "Приймач", 13, INK, "middle", bold=True))
    f.append(text(591, 150, "r = s + n", 13, FIELD, "middle", bold=True))

    # підсумкова смуга
    f.append(fitbox(55, 288, 612, 26,
                    "шум n(t) не залежить від того, що передали — той самий поверх будь-якого сигналу",
                    size=12, fill="#f4f6f8", stroke=LINE, color=INK))
    render(os.path.join(IMG, "channel-model.svg"), W, H, *f,
           title="Модель каналу AWGN: до сигналу додається шум")


# ── 2. Гаусів розподіл напруги шуму ───────────────────────────────────────────
# Ідея: мале тремтіння часте, великий сплеск рідкісний; ширину задає σ, і саме
# рідкісний хвіст за ±3σ псує біт.
def fig_gaussian():
    W, H = 720, 380
    ox, oy = 90, 320
    aw = 560
    xc = ox + aw / 2.0
    sig = 68.0
    peak = 228.0
    f = []

    def by(x):
        return oy - peak * math.exp(-((x - xc) / sig) ** 2 / 2.0)

    # вісь
    f.append(line(ox - 12, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw + 6, oy, ox + aw + 22, oy, color=INK, sw=1.6))
    f.append(text(ox + aw + 12, oy + 22, "напруга шуму", 11, INK, "end", bold=True))

    # дзвін
    pts = []
    x = xc - 3.35 * sig
    while x <= xc + 3.35 * sig:
        pts.append("%.1f,%.1f" % (x, by(x)))
        x += 3.0
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # пунктирні вертикалі й підписи ±kσ
    labels = [(-3, "−3σ"), (-2, "−2σ"), (-1, "−σ"), (0, "0"),
              (1, "σ"), (2, "2σ"), (3, "3σ")]
    for k, lab in labels:
        xk = xc + k * sig
        if k in (-1, 1, -3, 3):
            f.append(line(xk, oy, xk, by(xk), color="#c7d0da", sw=1.3, dash="4 4"))
        f.append(line(xk, oy, xk, oy + 6, color=INK, sw=1.2))
        f.append(text(xk, oy + 22, lab, 11, MUTED, "middle"))

    # центральна виноска (над піком, під заголовком)
    f.append(mtext(xc, 60, ["найчастіше — дрібне", "тремтіння в межах ±σ"], 11, MUTED))

    # виноска на правий хвіст
    f.append(mtext(590, 150, ["рідкісний великий сплеск —", "саме він перекидає біт"],
                   11, POS, anchor="middle"))
    f.append(arrow(560, 170, 520, by(520) - 6, color=POS, sw=1.8))

    render(os.path.join(IMG, "gaussian.svg"), W, H, *f,
           title="Гаусів шум: мале тремтіння часте, великий сплеск рідкісний")


# ── 3. Білий спектр: пласка щільність, шум у смузі = N₀·B ──────────────────────
# Ідея: щільність однакова на всіх частотах (як усі кольори в білому світлі);
# потужність шуму в каналі — це площа під нею в межах смуги.
def fig_white_spectrum():
    W, H = 720, 350
    ox, oy = 90, 262
    aw, ah = 560, 168
    y_flat = oy - 116
    f = []

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw + 6, oy, ox + aw + 22, oy, color=INK, sw=1.6))
    f.append(text(ox + aw + 14, oy + 22, "частота", 11, INK, "end", bold=True))
    f.append(line(ox, oy + 4, ox, oy - ah - 6, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 20, color=INK, sw=1.6))
    f.append(text(ox - 6, oy - ah - 8, "щільність потужності", 11, INK, "start", bold=True))

    # заштрихована смуга B (площа = потужність шуму в смузі)
    bx0, bx1 = ox + 210, ox + 370
    f.append(rect(bx0, y_flat, bx1 - bx0, oy - y_flat, fill="#eef6ef",
                  stroke=FIELD, sw=1.6, rx=0))
    f.append(text((bx0 + bx1) / 2, oy + 22, "смуга B", 11.5, FIELD, "middle", bold=True))
    f.append(mtext((bx0 + bx1) / 2, y_flat + 44, ["N = N₀·B", "шум у смузі"],
                   11.5, INK))

    # пласка щільність
    f.append(line(ox, y_flat, ox + aw, y_flat, color=NEG, sw=3))
    f.append(text(ox + aw - 6, y_flat - 12, "N₀/2 — те саме на кожній частоті",
                  12, NEG, "end", bold=True))

    # аналогія + застереження
    f.append(fitbox(60, 292, 600, 44,
                    "Як біле світло містить усі кольори порівну — білий шум має всі частоти\n"
                    "порівну. Пласким навіки він бути не може (нескінченна потужність); "
                    "насправді плаский у всій смузі, яку ми вживаємо.",
                    size=11, fill="#f4f6f8", stroke=LINE, color=INK))
    render(os.path.join(IMG, "white-spectrum.svg"), W, H, *f,
           title="Білий шум: однакова щільність потужності на всіх частотах")


# ── 4. Сузір'я: символ у гаусовій хмарі, помилка на межі рішення ───────────────
# Ідея: кожен символ шум розмиває в дзвін; там, де хвости налазять за межу
# рішення, приймач помиляється. Це мікроскопічне походження BER.
def fig_constellation():
    W, H = 720, 360
    oy = 250
    xs0, xs1 = 250.0, 490.0
    xb = (xs0 + xs1) / 2.0
    sig = 58.0
    peak = 150.0
    f = []

    def by(x, xcn):
        return oy - peak * math.exp(-((x - xcn) / sig) ** 2 / 2.0)

    # вісь
    f.append(line(80, oy, 662, oy, color=INK, sw=1.6))
    f.append(arrow(650, oy, 668, oy, color=INK, sw=1.6))

    # заштриховані хвости-помилки біля межі (площа під дзвоном за межею)
    def tail_poly(x_a, x_b, xcn):
        p = []
        x = x_a
        while x <= x_b:
            p.append("%.1f,%.1f" % (x, by(x, xcn)))
            x += 3.0
        p.append("%.1f,%.1f" % (x_b, oy))
        p.append("%.1f,%.1f" % (x_a, oy))
        return ('<polygon points="%s" fill="%s" fill-opacity="0.35" stroke="none"/>'
                % (" ".join(p), POS))
    f.append(tail_poly(xb - 70, xb, xs1))   # хвіст символу 1 ліворуч від межі
    f.append(tail_poly(xb, xb + 70, xs0))   # хвіст символу 0 праворуч від межі

    # дзвони
    for xcn, col in [(xs0, NEG), (xs1, FIELD)]:
        pts = []
        x = xcn - 3.1 * sig
        while x <= xcn + 3.1 * sig:
            pts.append("%.1f,%.1f" % (x, by(x, xcn)))
            x += 2.5
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), col))

    # точки-символи на осі
    f.append(circle(xs0, oy, 5.5, fill=NEG, stroke=NEG, sw=0))
    f.append(circle(xs1, oy, 5.5, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(xs0, oy + 24, "символ 0", 11.5, NEG, "middle", bold=True))
    f.append(text(xs1, oy + 24, "символ 1", 11.5, FIELD, "middle", bold=True))

    # межа рішення
    f.append(line(xb, oy + 8, xb, 92, color=INK, sw=1.6, dash="5 4"))
    f.append(text(xb, 82, "межа рішення", 11.5, INK, "middle", bold=True))

    # виноска на перекриття
    f.append(arrow(xb + 96, 214, xb + 20, 236, color=POS, sw=1.7))
    f.append(mtext(xb + 150, 210,
                   ["хвости налазять за межу:", "точку кидає до сусіда — помилка"],
                   10.5, POS, anchor="middle"))

    render(os.path.join(IMG, "constellation.svg"), W, H, *f,
           title="Чому шум псує біт: символ у гаусовій хмарі")


# ── 5. Крива BER(Eb/N0): вимір симуляції лягає на теоретичну Q-криву ───────────
# Ідея (для вставки-симуляції): емпіричні точки Монте-Карло сідають ТОЧНО на
# теоретичну «водоспадну» криву Q(√(2·Eb/N0)); а наївний фіксований N при
# високому SNR дає 0 помилок — точка провалюється (пастка «замало відліків»).
def fig_ber_curve():
    W, H = 780, 430
    ox, oy = 100, 340
    aw, ah = 570, 268
    y_top = oy - ah
    dec = ah / 6.0                       # висота однієї декади (10⁰…10⁻⁶)
    f = []

    def X(d):                            # Eb/N0 у дБ → x
        return ox + d / 10.0 * aw

    def Y(b):                            # BER → y (лог-шкала, 10⁰ угорі)
        return y_top + (-math.log10(b)) * dec

    def q(x):
        return 0.5 * math.erfc(x / math.sqrt(2.0))

    # сітка декад + підписи ліворуч
    decs = ["10⁰", "10⁻¹", "10⁻²", "10⁻³", "10⁻⁴", "10⁻⁵", "10⁻⁶"]
    for i, lab in enumerate(decs):
        y = y_top + i * dec
        f.append(line(ox, y, ox + aw, y, color="#e3e7ec", sw=1.2))
        f.append(text(ox - 12, y + 4, lab, 11, MUTED, "end"))

    # осі
    f.append(line(ox, y_top - 6, ox, oy + 6, color=INK, sw=1.6))
    f.append(line(ox, oy, ox + aw + 8, oy, color=INK, sw=1.6))
    for d in range(0, 11, 2):
        f.append(line(X(d), oy, X(d), oy + 6, color=INK, sw=1.3))
        f.append(text(X(d), oy + 22, str(d), 11, MUTED, "middle"))
    f.append(text(ox + aw / 2, oy + 42, "Eb/N₀,  дБ", 12, INK, "middle", bold=True))
    f.append(text(ox - 12, y_top - 16, "BER — частка збитих бітів", 12, INK, "start", bold=True))

    # теоретична крива Q(√(2·Eb/N0))
    pts = []
    d = 0.0
    while d <= 10.0001:
        pts.append("%.1f,%.1f" % (X(d), Y(q(math.sqrt(2 * 10 ** (d / 10.0))))))
        d += 0.2
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # виміряні точки Монте-Карло (лягають на криву)
    for d in range(0, 10):
        f.append(circle(X(d), Y(q(math.sqrt(2 * 10 ** (d / 10.0)))), 4.5,
                        fill=BG, stroke=FIELD, sw=2.2))

    # пастка: наївні фіксовані 10⁴ відліки → 0 помилок при високому SNR
    for d in (9, 10):
        f.append(text(X(d), oy - 4, "×", 18, POS, "middle", bold=True))
    f.append(arrow(372, 286, X(9) - 8, oy - 12, color=POS, sw=1.7))

    # легенда (у верхньому лівому куті — крива там висока, місце вільне)
    lx, ly = ox + 60, y_top + 8
    f.append(line(lx, ly, lx + 34, ly, color=NEG, sw=2.8))
    f.append(text(lx + 42, ly + 4, "теорія  Q(√(2·Eb/N₀))", 11.5, INK, "start"))
    f.append(circle(lx + 12, ly + 24, 4.5, fill=BG, stroke=FIELD, sw=2.2))
    f.append(text(lx + 42, ly + 28, "виміряно симуляцією (BPSK і QPSK збігаються)",
                  11.5, INK, "start"))

    # пояснення пастки — у вільному трикутнику знизу-ліворуч
    f.append(fitbox(120, 250, 250, 50,
                    "фіксовані 10⁴ відліків: при 9–10 дБ\n"
                    "жодної помилки — точка провалюється",
                    size=11, fill="#fdecea", stroke=POS, color=POS))

    render(os.path.join(IMG, "ber-curve.svg"), W, H, *f,
           title="Крива BER(Eb/N₀): вимір симуляції на теоретичній Q-кривій")


# ── 6. Пара Вінера–Хінчина: дельта-автокореляція ⟷ плаский спектр ─────────────
# Ідея (суто математична, важко прозою): «білий» = нульова пам'ять у часі
# (R(τ)=0 при τ≠0 — дельта в нулі) І плаский спектр — це одне й те саме,
# зв'язане перетворенням Фур'є. Два обличчя одного факту.
def fig_math_wk():
    W, H = 760, 330
    oy = 225
    f = []

    # ── ліва панель: автокореляція R(τ) ──
    ox1, aw1 = 70, 240
    xc1 = ox1 + aw1 / 2.0
    f.append(line(ox1 - 10, oy, ox1 + aw1 + 14, oy, color=INK, sw=1.6))
    f.append(arrow(ox1 + aw1 + 6, oy, ox1 + aw1 + 22, oy, color=INK, sw=1.6))
    f.append(text(ox1 + aw1 + 16, oy + 22, "τ", 13, INK, "middle", italic=True))
    f.append(text(ox1 - 8, oy - 132, "R(τ)", 12, INK, "start", bold=True))
    f.append(arrow(xc1, oy, xc1, oy - 120, color=NEG, sw=3))
    f.append(text(xc1, oy - 130, "(N₀/2)·δ(τ)", 12, NEG, "middle", bold=True))
    f.append(text(xc1, oy + 22, "0", 11, MUTED, "middle"))
    f.append(mtext(xc1 + 16, oy - 34, ["пам'ять нульова:", "R(τ)=0 при τ≠0"],
                   10.5, MUTED, anchor="start"))

    # ── подвійна стрілка «Фур'є» ──
    f.append(arrow(324, oy - 76, 398, oy - 76, color=INK, sw=1.8))
    f.append(arrow(398, oy - 60, 324, oy - 60, color=INK, sw=1.8))
    f.append(text(361, oy - 88, "Фур'є", 11.5, INK, "middle", bold=True))

    # ── права панель: спектральна щільність S(f) ──
    ox2, aw2 = 430, 250
    xc2 = ox2 + aw2 / 2.0
    yflat = oy - 80
    f.append(line(ox2 - 10, oy, ox2 + aw2 + 14, oy, color=INK, sw=1.6))
    f.append(arrow(ox2 + aw2 + 6, oy, ox2 + aw2 + 22, oy, color=INK, sw=1.6))
    f.append(text(ox2 + aw2 + 16, oy + 22, "f", 13, INK, "middle", italic=True))
    f.append(text(ox2 - 8, oy - 132, "S(f)", 12, INK, "start", bold=True))
    f.append(line(xc2, oy, xc2, oy - 4, color=INK, sw=1.2))
    f.append(text(xc2, oy + 22, "0", 11, MUTED, "middle"))
    f.append(line(ox2, yflat, ox2 + aw2, yflat, color=NEG, sw=3))
    f.append(text(ox2 + aw2 - 4, yflat - 12, "N₀/2 — на всіх частотах",
                  11.5, NEG, "end", bold=True))

    render(os.path.join(IMG, "wiener-khinchin.svg"), W, H, *f,
           title="Білий шум: дельта-автокореляція ⟷ плаский спектр")


# ── 7. Двобічна N₀/2 проти однобічної N₀ — той самий N₀·B ─────────────────────
# Ідея: множник ½ у двобічній щільності — бухгалтерія від'ємних частот.
# Згорни від'ємну половину спектра на додатну — дістанеш N₀; а потужність
# у смузі (площа під щільністю) в обох записах однакова: N₀·B.
def fig_math_twosided():
    W, H = 760, 510
    f = []
    ox, aw = 90, 560
    xc = ox + aw / 2.0
    bpix = 140

    # ── верхня панель: двобічна ──
    oy1, h1 = 160, 56
    f.append(text(xc, 58, "двобічна щільність (0 у центрі, від −∞ до +∞)",
                  12, INK, "middle", bold=True))
    f.append(rect(xc - bpix, oy1 - h1, 2 * bpix, h1, fill="#eef6ef",
                  stroke=FIELD, sw=1.4, rx=0))
    f.append(line(ox, oy1 - h1, ox + aw, oy1 - h1, color=NEG, sw=2.6))
    f.append(line(ox - 10, oy1, ox + aw + 14, oy1, color=INK, sw=1.6))
    f.append(arrow(ox + aw + 6, oy1, ox + aw + 22, oy1, color=INK, sw=1.6))
    f.append(text(ox + aw + 16, oy1 + 22, "f", 13, INK, "middle", italic=True))
    f.append(text(ox + 6, oy1 - h1 - 10, "N₀/2", 12, NEG, "start", bold=True))
    f.append(text(xc - bpix, oy1 + 20, "−B", 11, FIELD, "middle", bold=True))
    f.append(text(xc, oy1 + 20, "0", 11, MUTED, "middle"))
    f.append(text(xc + bpix, oy1 + 20, "+B", 11, FIELD, "middle", bold=True))
    f.append(text(xc, oy1 + 42, "площа = (N₀/2)·2B = N₀·B", 11.5, INK, "middle"))

    # ── нижня панель: однобічна ──
    oy2, h2 = 400, 112
    bx = ox + 2 * bpix   # B у пікселях від 0 (той самий масштаб, що вгорі)
    f.append(text(ox + 230, 258, "однобічна щільність (лише f ≥ 0)",
                  12, INK, "middle", bold=True))
    f.append(rect(ox, oy2 - h2, bx - ox, h2, fill="#eef6ef",
                  stroke=FIELD, sw=1.4, rx=0))
    f.append(line(ox, oy2 - h2, ox + aw, oy2 - h2, color=NEG, sw=2.6))
    f.append(line(ox - 10, oy2, ox + aw + 14, oy2, color=INK, sw=1.6))
    f.append(arrow(ox + aw + 6, oy2, ox + aw + 22, oy2, color=INK, sw=1.6))
    f.append(text(ox + aw + 16, oy2 + 22, "f", 13, INK, "middle", italic=True))
    f.append(text(ox + 6, oy2 - h2 - 10, "N₀", 12, NEG, "start", bold=True))
    f.append(text(ox, oy2 + 20, "0", 11, MUTED, "middle"))
    f.append(text(bx, oy2 + 20, "B", 11, FIELD, "middle", bold=True))
    f.append(text((ox + bx) / 2, oy2 + 42, "площа = N₀·B", 11.5, INK, "middle"))

    f.append(fitbox(70, 462, 620, 40,
                    "Та сама потужність N₀·B. Множник ½ двобічної точно гаситься,\n"
                    "коли від'ємні частоти згортають на додатні при переході до однобічної.",
                    size=11, fill="#f4f6f8", stroke=LINE, color=INK))
    render(os.path.join(IMG, "twosided-onesided.svg"), W, H, *f,
           title="Двобічна N₀/2 vs однобічна N₀ — та сама потужність N₀·B")


# ── 8. Q-функція: площа хвоста за межею рішення ────────────────────────────────
# Ідея: ймовірність помилки — це ПЛОЩА хвоста дзвона, що перелазить за межу.
# Аргумент d/2σ — це піввідстань між символами, зміряна в одиницях σ.
def fig_math_qfunc():
    W, H = 720, 370
    ox, oy = 90, 292
    aw = 540
    xc = ox + 200.0
    sig = 62.0
    peak = 205.0
    m = 1.6            # ілюстративне d/2σ
    x0 = xc + m * sig
    f = []

    def by(x):
        return oy - peak * math.exp(-((x - xc) / sig) ** 2 / 2.0)

    # вісь
    f.append(line(ox - 12, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw + 6, oy, ox + aw + 22, oy, color=INK, sw=1.6))
    f.append(text(ox + aw + 10, oy + 24, "напруга (в одиницях σ)", 11, INK, "end", bold=True))

    # заштрихований хвіст від межі x0
    p = []
    x = x0
    while x <= xc + 3.4 * sig:
        p.append("%.1f,%.1f" % (x, by(x)))
        x += 2.5
    p.append("%.1f,%.1f" % (xc + 3.4 * sig, oy))
    p.append("%.1f,%.1f" % (x0, oy))
    f.append('<polygon points="%s" fill="%s" fill-opacity="0.38" stroke="none"/>'
             % (" ".join(p), POS))

    # дзвін
    pts = []
    x = xc - 3.4 * sig
    while x <= xc + 3.4 * sig:
        pts.append("%.1f,%.1f" % (x, by(x)))
        x += 2.5
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # центр (символ / середнє)
    f.append(line(xc, oy, xc, by(xc), color="#c7d0da", sw=1.3, dash="4 4"))
    f.append(text(xc, oy + 24, "0", 11, MUTED, "middle"))

    # межа рішення
    f.append(line(x0, oy, x0, by(x0) - 4, color=INK, sw=1.6, dash="5 4"))
    f.append(text(x0, oy + 24, "межа рішення", 11, INK, "middle", bold=True))

    # розмах d/2 від центру до межі
    f.append(arrow(xc, oy - 8, x0, oy - 8, color=MUTED, sw=1.3))
    f.append(arrow(x0, oy - 8, xc, oy - 8, color=MUTED, sw=1.3))
    f.append(text((xc + x0) / 2, oy - 12, "d/2", 10.5, MUTED, "middle"))

    # виноска на хвіст
    f.append(arrow(x0 + 150, 138, x0 + 26, by(x0 + 34), color=POS, sw=1.8))
    f.append(mtext(x0 + 150, 108, ["площа хвоста = Q(d/2σ)", "= ймовірність помилки"],
                   11, POS, anchor="middle"))

    render(os.path.join(IMG, "q-function.svg"), W, H, *f,
           title="Q-функція: площа хвоста за межею — це ймовірність помилки")


# ── 9. Паралельні долі Джонсона і Найквіста (історична вставка) ────────────────
# Ідея, яку проза лише називає, а око схоплює миттю: два життєписи збігаються
# віха до віхи — Швеція, еміграція, Пн. Дакота й Єль (той самий 1917), Bell,
# і врешті дві статті 1928-го. Дві доріжки; збіги — червоні зв'язки.
def fig_parallel_lives():
    W, H = 880, 400
    yJ, yN = 150, 300                      # доріжки: Джонсон угорі, Найквіст унизу
    cols = [120, 280, 440, 600, 760]
    stages = ["родом зі Швеції", "еміграція в США", "докторат у Єлі",
              "Bell System", "статті 1928"]
    J = [["Дж. Джонсон", "Гетеборг, 1887"], ["до США", "1904"], ["1917"],
         ["Bell Labs", "1925"], ["дослід", "1928"]]
    Nq = [["Г. Найквіст", "Нільсбю, 1889"], ["до США", "1907"], ["1917"],
          ["AT&T → Bell", "1934"], ["теорія", "1928"]]
    hi = {2, 4}                            # колонки-збіги: Єль-1917 і статті-1928
    f = []

    # доріжки життя
    f.append(line(95, yJ, 785, yJ, color="#c7d0da", sw=2.4))
    f.append(line(95, yN, 785, yN, color="#c7d0da", sw=2.4))

    for i, cx in enumerate(cols):
        col_hi = i in hi
        cc = POS if col_hi else "#c7d0da"
        dash = None if col_hi else "4 5"
        sw = 2.0 if col_hi else 1.4
        # вертикальний зв'язок між доріжками, з розривом під назву етапу
        f.append(line(cx, yJ + 16, cx, 214, color=cc, sw=sw, dash=dash))
        f.append(line(cx, 246, cx, yN - 16, color=cc, sw=sw, dash=dash))
        # назва етапу — у розриві між доріжками
        f.append(text(cx, 234, stages[i], 12, MUTED, "middle", bold=True))
        # вузли на доріжках
        f.append(circle(cx, yJ, 7, fill=NEG, stroke=NEG, sw=0))
        f.append(circle(cx, yN, 7, fill=FIELD, stroke=FIELD, sw=0))
        # підпис Джонсона — над доріжкою (нижній рядок біля вузла)
        topJ = 112 - (len(J[i]) - 1) * 12 * 1.3
        f.append(mtext(cx, topJ, J[i], 12, NEG, "middle", bold=(i == 0)))
        # підпис Найквіста — під доріжкою (верхній рядок біля вузла)
        f.append(mtext(cx, 332, Nq[i], 12, FIELD, "middle", bold=(i == 0)))

    render(os.path.join(IMG, "parallel-lives.svg"), W, H, *f,
           title="Дві майже однакові долі")


if __name__ == "__main__":
    fig_channel_model()
    fig_gaussian()
    fig_white_spectrum()
    fig_constellation()
    fig_ber_curve()
    fig_math_wk()
    fig_math_twosided()
    fig_math_qfunc()
    fig_parallel_lives()
    print("OK: figures written to", IMG)
