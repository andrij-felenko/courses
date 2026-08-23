# -*- coding: utf-8 -*-
"""Фігури до вставки math-field-energy.md
(root/course/embedded/electrostatics-summary — вставка 🧮 «Енергія поля»).

Окремий файл (а не додаток до figs.py теми) навмисно: тему-власника й сусідні
вставки пишуть паралельні агенти, що редагують figs.py — щоб не зіштовхнутися,
фігури цієї вставки живуть окремо. Вивід — у той самий ./img/, стиль — зі svgkit.

Фігури:
  fe-assembly.svg — зношення зарядів з нескінченності по одному: кожен наступний
                    долає поле вже принесених → робота накопичується в суму
  fe-halfarea.svg — чому ½ у ½QV: напруга росте лінійно з зарядом, вкладена робота =
                    площа під прямою = трикутник = ½·Q·V (середня напруга V/2)
  fe-density.svg  — зміна погляду: енергія не «в зарядах», а розлита в полі як
                    u = ½ε₀E² — густіша там, де поле сильніше (зазор конденсатора)
Запуск:  python figs_field_energy.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Зношення зарядів з нескінченності ─────────────────────────────────────
def fig_assembly():
    """Три заряди приносять по черзі з нескінченності. Перший — безкоштовно.
    Кожен наступний долає поле вже поставлених — робота накопичується."""
    W, H = 780, 470
    els = []
    # три «сцени» одна під одною: що вже стоїть і кого несемо
    x_stage = 250          # де формується конфігурація
    y0 = 92
    dy = 118
    # позиції трьох зарядів у кінцевій трійці (трикутник)
    P = [(x_stage - 46, 0), (x_stage + 46, -8), (x_stage + 4, 40)]

    def draw_charge(x, y, faint=False):
        r = 13
        if faint:
            return (circle(x, y, r, fill="#f6eef0", stroke="#e0b4bc", sw=1.5) +
                    text(x, y + 5, "+", size=17, color="#d99aa4", bold=True))
        return plus(x, y, r=r)

    rows = [
        ("1-й заряд", "поля ще нема — приносимо ДАРОМ", "W₁ = 0", 0),
        ("2-й заряд", "долає поле 1-го", "W₂ = k·Q²/r₁₂", 1),
        ("3-й заряд", "долає поле 1-го і 2-го", "W₃ = k·Q²/r₁₃ + k·Q²/r₂₃", 2),
    ]
    for name, why, wf, k in rows:
        cy = y0 + k * dy
        # рамка-етап
        els.append(rect(30, cy - 42, W - 60, 96, fill="#fbfcfe", stroke="#dfe4ea", sw=1.2))
        els.append(text(52, cy - 22, name, size=15, bold=True, anchor="start", color=NEG))
        els.append(text(52, cy + 2, why, size=12.5, anchor="start", color=MUTED))
        els.append(text(52, cy + 34, wf, size=13.5, anchor="start", color=INK))
        # мінісцена праворуч: уже поставлені (яскраві) + той, кого несемо
        sx = 560
        for j in range(k):
            px, py = P[j]
            els.append(draw_charge(sx + (px - x_stage) * 0.9, cy + py * 0.7))
        # той, кого несемо цього кроку — зі стрілкою «з нескінченності»
        if k < 3:
            nx, ny = P[k]
            tx, ty = sx + (nx - x_stage) * 0.9, cy + ny * 0.7
            els.append(arrow(sx + 150, cy - 20, tx + 16, ty - 8, color=FIELD, sw=2))
            els.append(text(sx + 150, cy - 28, "з ∞", size=11.5, color=FIELD, anchor="middle"))
            els.append(draw_charge(tx, ty, faint=(k > 0)))

    # підсумок під усім
    box = fitbox(30, H - 58, W - 60, 44,
                 "Повна енергія системи = сума всіх цих робіт:  W = W₁ + W₂ + W₃ = Σ (пар) = ½ Σ qᵢVᵢ",
                 size=14, bold=True, fill="#eef7f0", stroke=FIELD)
    els.append(box)
    return render(os.path.join(IMG, 'fe-assembly.svg'), W, H, *els,
                  title="Складаємо систему по одному заряду з нескінченності")


# ── 2. Чому ½ у ½QV: площа трикутника ────────────────────────────────────────
def fig_halfarea():
    """Заряджаємо конденсатор: напруга росте лінійно з накопиченим зарядом.
    Вкладена робота = площа під прямою V(q) = трикутник = ½QV."""
    W, H = 720, 460
    els = []
    ox, oy = 100, H - 80        # початок координат
    axw, axh = W - 210, H - 150
    # осі
    els.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    els.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    els.append(text(ox + axw, oy + 26, "заряд на обкладці  q →", size=13, anchor="end"))
    els.append(text(ox - 14, oy - axh + 2, "напруга V", size=13, anchor="end"))

    # пряма V = q/C від (0,0) до (Q,V)
    qx, vy = ox + axw - 40, oy - axh + 30    # кінцева точка (Q, V)
    els.append(line(ox, oy, qx, vy, color=NEG, sw=2.6))
    # заповнений трикутник під прямою — це робота
    tri = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" '
           'fill-opacity="0.16" stroke="none"/>' % (ox, oy, qx, oy, qx, vy, FIELD))
    els.append(tri)
    # позначки Q і V
    els.append(line(qx, oy, qx, oy + 6, color=INK, sw=1.5))
    els.append(text(qx, oy + 24, "Q", size=14, bold=True))
    els.append(line(ox, vy, ox - 6, vy, color=INK, sw=1.5))
    els.append(text(ox - 16, vy + 5, "V", size=14, bold=True, anchor="end"))
    # пунктири до кутової точки
    els.append(line(qx, oy, qx, vy, color=MUTED, sw=1, dash="4 4"))
    els.append(line(ox, vy, qx, vy, color=MUTED, sw=1, dash="4 4"))

    # тонка вертикальна смужка dq (елемент роботи dW = V·dq)
    sqx = ox + (qx - ox) * 0.55
    svy = oy - (oy - vy) * 0.55
    els.append(rect(sqx, svy, 10, oy - svy, fill=POS, stroke="none", sw=0))
    els.append(text(sqx + 5, svy - 8, "dW = V·dq", size=11.5, color=POS, anchor="middle"))

    # підпис прямої
    els.append(text(ox + 40, oy - axh * 0.75, "V = q / C", size=14, color=NEG,
                    anchor="start", bold=True))
    # висновок-рамка праворуч від осі значень (у вільному куті)
    els.append(fitbox(qx - 250, vy - 6, 244, 92,
                      "Робота = площа трикутника\n= ½ · основа · висота\n= ½ · Q · V\n\nсередня напруга — V/2,\nбо росла від 0 до V",
                      size=13, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, 'fe-halfarea.svg'), W, H, *els,
                  title="Звідки ½ у W = ½QV: робота — це площа під V(q)")


# ── 3. Енергія розлита в полі: u = ½ε₀E² ─────────────────────────────────────
def fig_density():
    """Дві обкладки, поле між ними. Енергія не «в зарядах» на металі, а в самому
    полі в зазорі; густіша, де E більше. Праворуч — той самий заряд, ширший зазор:
    поле те саме, але енергії більше, бо об'єм поля більший."""
    W, H = 780, 430
    els = []

    def capacitor(cx, top, bot, gap, shade, label):
        """Малює конденсатор із центром cx; обкладки на ±gap/2, поле заштриховане."""
        pw = 96          # півширина обкладки
        yl = top + 6     # верхня обкладка
        yr = bot - 6     # нижня обкладка
        # верхня «+», нижня «−»
        els.append(rect(cx - pw, yl, 2 * pw, 8, fill=POS, stroke="none", sw=0))
        els.append(rect(cx - pw, yr, 2 * pw, 8, fill=NEG, stroke="none", sw=0))
        els.append(text(cx - pw - 14, yl + 10, "+", size=18, color=POS, bold=True, anchor="end"))
        els.append(text(cx - pw - 14, yr + 8, "−", size=18, color=NEG, bold=True, anchor="end"))
        # заштрихована ділянка поля між обкладками
        els.append(('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                    'fill-opacity="%.2f" stroke="%s" stroke-width="1" '
                    'stroke-dasharray="3 3"/>' % (cx - pw, yl + 8, 2 * pw,
                                                   (yr) - (yl + 8), FIELD, shade, FIELD)))
        # силові лінії вниз
        for f in (-0.62, -0.3, 0, 0.3, 0.62):
            lx = cx + f * pw
            els.append(arrow(lx, yl + 12, lx, yr - 2, color=FIELD, sw=1.5))
        els.append(text(cx, yr + 30, label, size=12.5, anchor="middle", color=INK))

    # ліворуч: вузький зазор
    capacitor(200, 96, 250, 60, 0.28, "вузький зазор — те саме E")
    # праворуч: широкий зазор, той самий E (та сама густина ліній), але більше об'єму
    capacitor(200 + 340, 78, 300, 120, 0.28, "ширший зазор — більше об'єму поля")

    # центральна формула згори
    els.append(text(W / 2, 54, "u = ½ ε₀ E²   [Дж/м³]  —  енергія РОЗЛИТА в полі, а не «в зарядах»",
                    size=15, bold=True, color=INK, anchor="middle"))
    # висновок унизу (два рядки, щоб не дрібнити шрифт)
    els.append(fitbox(40, H - 62, W - 80, 50,
                      "Однакове E → однакова густина u; праворуч поле займає більший об'єм → запасено більше.\n"
                      "Приберіть заряди — поле щезне, і енергія разом із ним.",
                      size=13, fill="#eef7f0", stroke=FIELD))
    return render(os.path.join(IMG, 'fe-density.svg'), W, H, *els,
                  title="Де сидить енергія: у полі, густиною ½ε₀E²")


if __name__ == '__main__':
    fig_assembly()
    fig_halfarea()
    fig_density()
    print("OK:", [f for f in os.listdir(IMG) if f.startswith('fe-')])
