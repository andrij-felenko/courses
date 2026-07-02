# -*- coding: utf-8 -*-
"""Фігури до теми «Драйвер LED: стабілізатор струму для світлодіодів».
  led-driver.md →  iv-drive.svg       (експонента ВАХ: чому напругою керувати не можна)
                   driver-ladder.svg  (три родини драйверів: баласт → лінійний → імпульсний)
                   sink-loop.svg      (активне джерело струму: петля I = Vref/Rset)
  proj-pwm-led-current.md →
                   gamma-curve.svg    (лінійна шкала vs гамма-скоригована — сприйняття ока)
                   boost-dim-min.svg  (ШІМ-димінг проти інерції котушки: min on-time)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні примітиви ──────────────────────────────────────────────────────
def gnd(cx, y):
    return "".join([line(cx, y, cx, y + 6, color=INK, sw=1.8),
                    line(cx - 12, y + 6, cx + 12, y + 6, color=INK, sw=2.4),
                    line(cx - 7, y + 11, cx + 7, y + 11, color=INK, sw=2.0),
                    line(cx - 3, y + 16, cx + 3, y + 16, color=INK, sw=1.8)])


def led(cx, cy, s=13, color=INK):
    """Символ світлодіода (трикутник + риска + дві стрілочки світла)."""
    out = [line(cx, cy - s, cx, cy - s, color=color)]  # placeholder
    out = []
    # трикутник вершиною вниз
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" '
               'stroke="%s" stroke-width="1.8"/>' % (cx - s, cy - s, cx + s, cy - s, cx, cy + s, color))
    out.append(line(cx - s, cy + s, cx + s, cy + s, color=color, sw=2.2))  # катодна риска
    # промінці
    for dx in (0.5, 1.1):
        ox, oy = cx + s * 0.6, cy - s * 0.5
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                   'stroke-width="1.4" marker-end="url(#arrow)"/>'
                   % (ox + dx * 6, oy - dx * 3, ox + dx * 6 + 10, oy - dx * 3 - 7, POS))
    return "".join(out)


def resistor(x, y1, y2, color=INK):
    """Вертикальний резистор (пилка) між y1 і y2 на вертикалі x."""
    n, out, span = 6, [], (y2 - y1)
    step = span / n
    out.append(line(x, y1, x, y1 + step * 0.4, color=color, sw=1.8))
    px, py = x, y1 + step * 0.4
    for i in range(n):
        nx = x + (7 if i % 2 == 0 else -7)
        ny = py + step
        if i == n - 1:
            nx = x
        out.append(line(px, py, nx, ny, color=color, sw=1.8))
        px, py = nx, ny
    out.append(line(x, py, x, y2, color=color, sw=1.8))
    return "".join(out)


# ============================================================================
# 1. iv-drive.svg — експонента ВАХ: керування напругою нестабільне, струмом — так
# ============================================================================
def fig_iv():
    W, H = 720, 400
    # осі графіка ВАХ
    ox, oy = 90, 300      # початок координат (лівий-нижній)
    axw, axh = 300, 230   # довжина осей
    frags = [text(W / 2, 26, "Чому яскравість тримають струмом, а не напругою", size=17, bold=True)]

    # осі
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))       # I (вгору)
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))       # V (вправо)
    frags.append(text(ox - 12, oy - axh + 4, "I", size=14, bold=True, color=INK, anchor="end"))
    frags.append(text(ox + axw + 4, oy + 4, "V", size=14, bold=True, color=INK, anchor="start"))
    frags.append(text(ox + axw / 2, oy + 34, "напруга на світлодіоді V_f", size=12, color=MUTED))

    # експонента: I ~ exp((V - Von)/n)
    Von = 0.55   # частка axw, де «коліно»
    pts = []
    for i in range(0, 101):
        vv = i / 100.0                        # 0..1 по осі напруги
        cur = math.exp((vv - Von) * 9.0) - math.exp(-Von * 9.0)
        if cur < 0:
            cur = 0
        pts.append((vv, cur))
    cmax = pts[-1][1]
    path = []
    for vv, cur in pts:
        px = ox + vv * axw
        py = oy - (cur / cmax) * axh
        path.append(("M" if not path else "L") + "%.1f %.1f" % (px, py))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(path), INK))

    # робоча точка на ~0.80 напруги
    def at_v(vfrac):
        cur = math.exp((vfrac - Von) * 9.0) - math.exp(-Von * 9.0)
        return ox + vfrac * axw, oy - (cur / cmax) * axh

    v0 = 0.80
    x0, y0 = at_v(v0)
    # маленький зсув напруги dV -> великий зсув струму
    dv = 0.05
    x1, y1 = at_v(v0 + dv)
    # вертикальні/горизонтальні пунктири для dV і dI
    frags.append(line(x0, oy, x0, y0, color=NEG, sw=1.4, dash="4 3"))
    frags.append(line(x1, oy, x1, y1, color=NEG, sw=1.4, dash="4 3"))
    frags.append(line(ox, y0, x0, y0, color=POS, sw=1.4, dash="4 3"))
    frags.append(line(ox, y1, x1, y1, color=POS, sw=1.4, dash="4 3"))
    frags.append(circle(x0, y0, 4, fill=INK, stroke=INK))
    frags.append(circle(x1, y1, 4, fill=POS, stroke=POS))

    # брекети dV (малий) і dI (великий)
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                 % (x0, oy + 14, x1, oy + 14, NEG))
    frags.append(text((x0 + x1) / 2, oy + 30, "+0.1 В", size=11, color=NEG, bold=True))
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                 % (ox - 16, y0, ox - 16, y1, POS))
    frags.append(text(ox - 22, (y0 + y1) / 2 + 4, "×2 струм", size=11, color=POS, bold=True, anchor="end"))

    # ── права колонка: два способи керувати ──
    cx = 470
    b1, w1, h1 = textbox(cx + 110, 120,
                         "Задаємо НАПРУГУ\n(фіксовані ≈3.2 В)\n\nнагрів → V_f падає →\nструм росте → нагрів…\n⇒ тепловий розгін",
                         size=12, fill="#fdecea", stroke=POS, sw=1.8, color=INK)
    frags.append(b1)
    b2, w2, h2 = textbox(cx + 110, 275,
                         "Задаємо СТРУМ\n(джерело струму)\n\nV_f поплив — драйвер\nсам підкрутить напругу\n⇒ робоча точка стоїть",
                         size=12, fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK)
    frags.append(b2)

    render(os.path.join(IMG, 'iv-drive.svg'), W, H, *frags)


# ============================================================================
# 2. driver-ladder.svg — три родини драйверів і що вони роблять із «зайвим»
# ============================================================================
def fig_ladder():
    W, H = 760, 420
    frags = [text(W / 2, 26, "Три родини драйверів: як задають струм і куди дівають надлишок", size=16, bold=True)]

    colw = 230
    xs = [20, 265, 510]
    top = 56
    boxh = 300

    titles = ["Баластний резистор", "Лінійне джерело струму", "Імпульсне джерело струму"]
    sub = ["найпростіше", "стабільно, але гріє", "стабільно й ощадно"]
    colors = [MUTED, NEG, FIELD]

    for i, x in enumerate(xs):
        frags.append(rect(x, top, colw, boxh, fill=BG, stroke=colors[i], sw=2))
        frags.append(text(x + colw / 2, top + 24, titles[i], size=13, bold=True, color=INK))
        frags.append(text(x + colw / 2, top + 42, sub[i], size=11, color=colors[i], italic=True))

    # ── колонка 1: резистор + LED, надлишок = тепло на R ──
    x = xs[0] + colw / 2
    frags.append(text(x, top + 70, "V+", size=11, color=INK))
    frags.append(line(x, top + 76, x, top + 96, color=INK, sw=1.8))
    frags.append(resistor(x, top + 96, top + 156))
    frags.append(line(x, top + 156, x, top + 172, color=INK, sw=1.8))
    frags.append(led(x, top + 190))
    frags.append(line(x, top + 203, x, top + 220, color=INK, sw=1.8))
    frags.append(gnd(x, top + 220))
    frags.append(fitbox(xs[0] + 16, top + 250, colw - 32, 40,
                        "струм = (V+ − V_f)/R\nнадлишок → тепло на R",
                        size=11, fill="#f4f6f8", stroke=MUTED))

    # ── колонка 2: транзистор-регулятор + Rset, надлишок = тепло на транзисторі ──
    x = xs[1] + colw / 2
    frags.append(text(x, top + 70, "V+", size=11, color=INK))
    frags.append(line(x, top + 76, x, top + 92, color=INK, sw=1.8))
    frags.append(led(x, top + 110))
    frags.append(line(x, top + 123, x, top + 140, color=INK, sw=1.8))
    # транзистор як регульований опір — прямокутник із стрілкою керування
    frags.append(rect(x - 22, top + 140, 44, 30, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(x, top + 159, "рег.", size=10, color=NEG, bold=True))
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" marker-end="url(#arrow)"/>'
                 % (x - 55, top + 155, x - 24, top + 155, NEG))
    frags.append(text(x - 58, top + 145, "петля", size=9, color=NEG, anchor="end"))
    frags.append(line(x, top + 170, x, top + 184, color=INK, sw=1.8))
    frags.append(resistor(x, top + 184, top + 214))
    frags.append(text(x + 16, top + 202, "Rset", size=10, color=NEG))
    frags.append(line(x, top + 214, x, top + 224, color=INK, sw=1.8))
    frags.append(gnd(x, top + 224))
    frags.append(fitbox(xs[1] + 16, top + 250, colw - 32, 40,
                        "I = V_ref / Rset  (стабільно)\nнадлишок → тепло на «рег.»",
                        size=11, fill="#eaf0fd", stroke=NEG))

    # ── колонка 3: імпульсний блок ──
    x = xs[2] + colw / 2
    frags.append(text(x, top + 70, "V+", size=11, color=INK))
    frags.append(line(x, top + 76, x, top + 92, color=INK, sw=1.8))
    frags.append(rect(x - 40, top + 92, 80, 40, fill="#eafaf0", stroke=FIELD, sw=1.8))
    frags.append(mtext(x, top + 109, ["L, ключ,", "діод"], size=10, color=INK))
    frags.append(line(x, top + 132, x, top + 148, color=INK, sw=1.8))
    frags.append(led(x, top + 166))
    frags.append(line(x, top + 179, x, top + 196, color=INK, sw=1.8))
    frags.append(resistor(x, top + 196, top + 222))
    frags.append(text(x + 16, top + 212, "Rset", size=10, color=FIELD))
    frags.append(line(x, top + 222, x, top + 230, color=INK, sw=1.8))
    frags.append(gnd(x, top + 230))
    # петля ЗЗ назад у блок
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" marker-end="url(#arrow)"/>'
                 % (x + 30, top + 205, x + 52, top + 205, FIELD))
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                 % (x + 52, top + 205, x + 52, top + 112, x + 40, top + 112, FIELD))
    frags.append(fitbox(xs[2] + 16, top + 250, colw - 32, 40,
                        "I = V_ref / Rset  (стабільно)\nнадлишок не гріє — рециклюється",
                        size=11, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, 'driver-ladder.svg'), W, H, *frags)


# ============================================================================
# 3. sink-loop.svg — активне джерело струму: петля тримає I = Vref/Rset
# ============================================================================
def fig_sink():
    W, H = 720, 380
    frags = [text(W / 2, 26, "Активне джерело струму: петля тримає спад на Rset рівним V_ref", size=15, bold=True)]

    # верхня шина V+
    railx1, railx2, raily = 120, 600, 70
    frags.append(text(railx1 - 22, raily + 4, "V+", size=13, bold=True, color=INK))
    frags.append(line(railx1, raily, railx2, raily, color=INK, sw=2))

    # гілка навантаження: LED зверху вниз до транзистора
    lx = 250
    frags.append(line(lx, raily, lx, raily + 26, color=INK, sw=1.8))
    frags.append(led(lx, raily + 44))
    frags.append(line(lx, raily + 57, lx, raily + 78, color=INK, sw=1.8))

    # транзистор (NPN-регулятор): колектор зверху, емітер знизу, база — від ОП
    tx, ty = lx, raily + 100
    frags.append(circle(tx, ty, 22, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(line(tx, raily + 78, tx, ty - 14, color=INK, sw=1.8))          # колектор
    frags.append(line(tx - 14, ty - 8, tx - 14, ty + 8, color=INK, sw=2.4))      # база-пластина
    frags.append(line(tx - 22, ty, tx - 14, ty, color=INK, sw=1.8))             # база-вивід
    frags.append(line(tx - 14, ty - 6, tx + 2, ty - 14, color=INK, sw=1.8))     # к колектору
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (tx - 14, ty + 6, tx + 2, ty + 16, INK))                      # емітер (стрілка)
    frags.append(text(tx + 30, ty + 4, "рег.", size=10, color=NEG, bold=True))

    # емітер -> Rset -> земля; вузол sense
    sy = ty + 30
    frags.append(line(tx + 1, ty + 15, tx + 1, sy, color=INK, sw=1.8))
    sense_y = sy
    frags.append(circle(tx + 1, sense_y, 3, fill=POS, stroke=POS))
    frags.append(text(tx + 40, sense_y + 4, "вузол sense", size=10, color=POS))
    frags.append(resistor(tx + 1, sense_y, sense_y + 40))
    frags.append(text(tx + 20, sense_y + 22, "Rset", size=11, color=INK, bold=True))
    frags.append(line(tx + 1, sense_y + 40, tx + 1, sense_y + 52, color=INK, sw=1.8))
    frags.append(gnd(tx + 1, sense_y + 52))

    # операційний підсилювач (трикутник) праворуч
    ax, ayc = 470, ty + 6
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#fff" stroke="%s" stroke-width="1.8"/>'
                 % (ax, ayc - 30, ax, ayc + 30, ax + 56, ayc, INK))
    frags.append(text(ax + 20, ayc + 5, "×", size=16, color=INK, bold=True))
    frags.append(text(ax + 12, ayc - 14, "−", size=15, color=NEG, bold=True))
    frags.append(text(ax + 12, ayc + 22, "+", size=15, color=POS, bold=True))
    frags.append(text(ax + 26, ayc - 40, "підсилювач помилки", size=10, color=MUTED))

    # V_ref на «+» вхід
    frags.append(line(ax - 60, ayc + 18, ax, ayc + 18, color=INK, sw=1.6))
    frags.append(circle(ax - 78, ayc + 18, 16, fill="#eafaf0", stroke=FIELD, sw=1.8))
    frags.append(mtext(ax - 78, ayc + 15, ["V", "ref"], size=9, color=FIELD, bold=True))

    # sense -> «−» вхід (довга лінія від вузла sense)
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (tx + 1, sense_y, ax - 30, sense_y, ax - 30, ayc - 18, POS))
    frags.append(line(ax - 30, ayc - 18, ax, ayc - 18, color=POS, sw=1.6))

    # вихід ОП -> база транзистора (керування): обходимо Rset знизу-зліва
    outb_y = 300
    basex = tx - 22
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (ax + 56, ayc, 560, ayc, 560, outb_y, 180, outb_y, 180, ty, NEG))
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (180, ty, basex, ty, NEG))
    frags.append(text(566, outb_y - 6, "керує базою", size=10, color=NEG, anchor="start"))

    # підсумкова формула
    fb, fw, fh = textbox(W / 2, 350,
                         "рівновага:  V(sense) = V_ref   ⇒   I_LED = V_ref / Rset",
                         size=13, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True)
    frags.append(fb)

    render(os.path.join(IMG, 'sink-loop.svg'), W, H, *frags)


# ============================================================================
# 4. gamma-curve.svg — лінійна шкала duty проти гамма-скоригованої
# ============================================================================
def fig_gamma():
    W, H = 720, 400
    ox, oy = 90, 330          # початок координат (лівий-нижній)
    axw, axh = 320, 270
    frags = [text(W / 2, 26, "Гамма-корекція: лінійно на око, а не на шпаруватість", size=16, bold=True)]

    # осі
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    frags.append(text(ox + axw / 2, oy + 30, "положення повзунка (0…100 %)", size=12, color=MUTED))
    frags.append(text(ox - 46, oy - axh + 4, "шпаруватість", size=11, color=MUTED, anchor="start"))
    frags.append(text(ox - 46, oy - axh + 18, "ШІМ (duty)", size=11, color=MUTED, anchor="start"))

    # діагональ = лінійна шкала (duty = положення)
    frags.append(line(ox, oy, ox + axw, oy - axh, color=NEG, sw=2.4, dash="6 4"))
    # гамма-крива: duty = pos^2.2
    pts = []
    for i in range(0, 101):
        p = i / 100.0
        d = p ** 2.2
        pts.append((ox + p * axw, oy - d * axh))
    path = "".join([("M" if k == 0 else "L") + "%.1f %.1f" % xy for k, xy in enumerate(pts)])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path, FIELD))

    # позначки: рівні кроки положення дають РІВНІ на око кроки яскравості
    for p in (0.25, 0.5, 0.75):
        d = p ** 2.2
        px = ox + p * axw
        py = oy - d * axh
        frags.append(circle(px, py, 4, fill=FIELD, stroke=FIELD))
        frags.append(line(px, oy, px, oy + 5, color=INK, sw=1.4))
        frags.append(text(px, oy + 18, "%d%%" % int(p * 100), size=10, color=MUTED))
        # горизонтальна пунктирна до осі duty
        frags.append(line(ox, py, px, py, color=FIELD, sw=1.0, dash="3 3"))
        frags.append(text(ox - 6, py + 4, "%d" % int(d * 100), size=9, color=FIELD, anchor="end"))

    # підписи кривих
    frags.append(text(ox + axw - 6, oy - axh + 16, "лінійна duty", size=11, color=NEG, anchor="end", bold=True))
    frags.append(text(ox + axw - 6, oy - 40, "гамма γ≈2.2", size=11, color=FIELD, anchor="end", bold=True))

    # пояснювальна рамка
    frags.append(fitbox(ox + axw + 14, oy - axh, W - (ox + axw + 14) - 14, 150,
                        "Око бачить яскравість\nлогарифмічно. Рівні кроки\nповзунка треба гнути\nв duty ∝ pos^γ, інакше\nвесь «рух» яскравості\nтисне в перші відсотки.",
                        size=11, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, 'gamma-curve.svg'), W, H, *frags)


# ============================================================================
# 5. boost-dim-min.svg — ШІМ-димінг проти інерції котушки boost-драйвера
# ============================================================================
def fig_boostdim():
    W, H = 760, 420
    frags = [text(W / 2, 24, "ШІМ-димінг boost-драйвера: котушка не встигає за коротким імпульсом", size=15, bold=True)]

    left = 70
    axw = 620
    # три доріжки: EN (ШІМ), струм котушки при ДОВГОМУ імпульсі, при КОРОТКОМУ
    def track(y, label):
        frags.append(text(left - 8, y, label, size=11, color=INK, anchor="end", bold=True))
        frags.append(line(left, y, left + axw, y, color=MUTED, sw=1.0))

    # ── доріжка 1: сигнал EN (ШІМ-димінг) ──
    y1 = 90
    frags.append(text(left - 8, y1 - 24, "EN (ШІМ)", size=11, color=INK, anchor="end", bold=True))
    amp = 26
    # довгий імпульс, потім короткий
    def pulse(x0, w, y, up=amp):
        return [line(x0, y, x0, y - up, color=NEG, sw=2),
                line(x0, y - up, x0 + w, y - up, color=NEG, sw=2),
                line(x0 + w, y - up, x0 + w, y, color=NEG, sw=2)]
    base1 = y1
    frags.append(line(left, base1, left + axw, base1, color=MUTED, sw=1.0))
    frags += pulse(left + 40, 150, base1)
    frags += pulse(left + 360, 26, base1)      # короткий імпульс
    frags.append(text(left + 40 + 75, base1 - amp - 6, "довгий on", size=10, color=NEG))
    frags.append(text(left + 360 + 13, base1 - amp - 6, "короткий on", size=10, color=POS))

    # ── доріжка 2: струм котушки (реакція) ──
    y2 = 250
    frags.append(text(left - 8, y2 - 70, "струм", size=11, color=INK, anchor="end", bold=True))
    frags.append(text(left - 8, y2 - 56, "у нитці", size=11, color=INK, anchor="end", bold=True))
    frags.append(line(left, y2, left + axw, y2, color=MUTED, sw=1.0))
    Itgt = 70   # рівень номінального струму (вгору = менше y)
    frags.append(line(left, y2 - Itgt, left + axw, y2 - Itgt, color=MUTED, sw=1.0, dash="4 3"))
    frags.append(text(left + axw, y2 - Itgt - 4, "I_ном", size=10, color=MUTED, anchor="end"))

    # довгий імпульс: струм лінійно наростає кілька циклів, доходить до I_ном, тримається, спадає
    def ramp_path(x0, w, reach, y0=y2, level=Itgt, up_cycles=90):
        """Наростання струму котушки: пилчастий підйом до reach·level за up_cycles, тримання, спад."""
        seg = []
        # наростання (пилка на тлі загального тренду)
        n = 8
        peak = reach * level
        for k in range(n + 1):
            fx = x0 + (up_cycles) * (k / n)
            fy = y0 - peak * (k / n)
            seg.append((fx, fy))
        return seg, x0 + up_cycles, peak

    # ДОВГИЙ: доходить до повного I_ном
    segL, endL, peakL = ramp_path(left + 40, 150, 1.0, up_cycles=95)
    # тримання на I_ном до кінця імпульсу
    holdx = left + 40 + 150
    ptsL = segL + [(holdx, y2 - peakL)] + [(holdx, y2), ]
    pathL = "".join([("M" if k == 0 else "L") + "%.1f %.1f" % xy for k, xy in enumerate(ptsL)])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pathL, FIELD))
    frags.append(text(left + 40 + 70, y2 - peakL - 8, "встиг набрати повний струм", size=10, color=FIELD))

    # КОРОТКИЙ: імпульс скінчився РАНІШЕ, ніж струм доріс — маленький горбик
    x0s = left + 360
    reachS = 0.32
    peakS = reachS * Itgt
    ptsS = [(x0s, y2), (x0s + 26, y2 - peakS), (x0s + 46, y2)]
    pathS = "M%.1f %.1f L%.1f %.1f L%.1f %.1f" % (ptsS[0][0], ptsS[0][1], ptsS[1][0], ptsS[1][1], ptsS[2][0], ptsS[2][1])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pathS, POS))
    frags.append(text(x0s + 20, y2 - peakS - 8, "не встиг —", size=10, color=POS))
    frags.append(text(x0s + 20, y2 - peakS + 6, "яскравість нелінійна", size=10, color=POS))

    # висновкова рамка
    frags.append(fitbox(left, 320, axw, 66,
                        "Струм у нитці набирається за кілька циклів ключа (котушка інерційна). Поки on-час довгий за цей розбіг —\n"
                        "усе гаразд. Коротший за нього імпульс дає не повний струм: яскравість перестає бути пропорційна duty,\n"
                        "а на самому дні димінг просто зникає. Це і є мінімальний on-time — підлога глибини димінгу boost-драйвера.",
                        size=11, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, 'boost-dim-min.svg'), W, H, *frags)


# ============================================================================
# 6. haitz-law.svg — закон Гайтца: ціна ÷10/декаду vs ефективність росте (лог-осі)
#    (для вставки hist-solid-state-lighting.md)
# ============================================================================
def fig_haitz():
    import math as _m
    W, H = 760, 440
    ox, oy = 104, 350         # початок координат (лівий-нижній)
    axw, axh = 552, 282       # довжина осей
    frags = [text(W / 2, 26, "Закон Гайтца: ціна падає, світло росте", size=17, bold=True)]

    years = [1970, 1980, 1990, 2000, 2010, 2020]

    def xof(yr):
        return ox + axw * (yr - years[0]) / (years[-1] - years[0])

    # 6 декад по вертикалі (кожна поділка = ×10)
    DEC = 6
    def yof(level):                      # level 0 (низ) .. DEC (верх)
        return oy - axh * level / DEC

    # горизонтальна сітка (декади)
    for lv in range(DEC + 1):
        y = yof(lv)
        frags.append(line(ox, y, ox + axw, y, color="#e5e8ec", sw=1.0))

    # осі поверх сітки
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))       # вертикальна (лог)
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))       # роки
    for yr in years:
        x = xof(yr)
        frags.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        frags.append(text(x, oy + 22, str(yr), size=12, color=MUTED))

    # ── Ціна за люмен: ÷10 щодесятиліття (5 декад спаду 1970→2020) ──
    price_pts = [(xof(yr), yof(5.0 - 5.0 * (yr - 1970) / 50.0)) for yr in years]
    dpath = "M%.1f %.1f " % price_pts[0] + " ".join("L%.1f %.1f" % p for p in price_pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dpath, POS))
    for p in price_pts:
        frags.append(circle(p[0], p[1], 4, fill=POS, stroke=POS))

    # ── Ефективність (лм/Вт): росте; перетин 100 ~2010, 200 ~2020 ──
    eff = {1970: 0.1, 1980: 1, 1990: 5, 2000: 25, 2010: 100, 2020: 200}
    lo, span = _m.log10(0.1), _m.log10(300) - _m.log10(0.1)
    def eyof(yr):
        return yof(DEC * (_m.log10(eff[yr]) - lo) / span)
    eff_pts = [(xof(yr), eyof(yr)) for yr in years]
    epath = "M%.1f %.1f " % eff_pts[0] + " ".join("L%.1f %.1f" % p for p in eff_pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (epath, NEG))
    for p in eff_pts:
        frags.append(circle(p[0], p[1], 4, fill=NEG, stroke=NEG))
    frags.append(text(xof(2010), eyof(2010) + 20, "100 лм/Вт", size=11, color=NEG, bold=True))
    frags.append(text(xof(2020) - 6, eyof(2020) - 12, "200 лм/Вт", size=11, color=NEG,
                      bold=True, anchor="end"))

    # підпис вертикальної осі (повернений)
    frags.append('<text transform="rotate(-90 %.1f %.1f)" x="%.1f" y="%.1f" '
                 'font-family="%s" font-size="12" fill="%s" text-anchor="middle">'
                 'лог-шкала (кожна поділка = ×10)</text>'
                 % (ox - 58, oy - axh / 2, ox - 58, oy - axh / 2, FONT, MUTED))

    # легенда-плашки біля кривих
    b1, _w1, _h1 = textbox(xof(1985), yof(5.35), "ціна за люмен: ÷10 щодесятиліття",
                           size=12, color=POS, stroke=POS, fill="#fdecea")
    frags.append(b1)
    b2, _w2, _h2 = textbox(xof(1990), yof(0.62), "ефективність (лм/Вт): вгору",
                           size=12, color=NEG, stroke=NEG, fill="#eaf0fd")
    frags.append(b2)

    frags.append(text(ox + axw / 2, oy + 42,
                      "роки  ·  «LED-аналог закону Мура»", size=12, color=MUTED))
    render(os.path.join(IMG, 'haitz-law.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_iv()
    fig_ladder()
    fig_sink()
    fig_gamma()
    fig_boostdim()
    fig_haitz()
    print("OK: iv-drive.svg, driver-ladder.svg, sink-loop.svg, gamma-curve.svg, boost-dim-min.svg, haitz-law.svg")
