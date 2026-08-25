# -*- coding: utf-8 -*-
"""Фігури до теми «Число Рейнольдса».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def sup10(exp):
    """'10' зі степенем через unicode-надрядкові (для підписів осі)."""
    m = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
         "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "10" + "".join(m[c] for c in str(exp))


# ── Фігура 1: число Рейнольдса як відношення двох сил ────────────────────────
def fig_two_forces():
    W, H = 820, 495
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Число Рейнольдса — відношення двох сил", size=18, bold=True))

    # ── дріб:  Re = (інерційна) / (в'язка) = ρvL/μ ──
    f.append(text(150, 158, "Re", size=26, bold=True, italic=True, anchor="middle"))
    f.append(text(196, 158, "=", size=26, anchor="middle"))
    # чисельник (інерційна, червоне)
    b, w, h = textbox(415, 116, "інерційна  ≈  ρ·v²·L²", size=15, pad=11,
                      fill="#fdecea", stroke=POS, sw=1.5, bold=True)
    f.append(b)
    # риска дробу
    f.append(line(238, 150, 592, 150, color=INK, sw=2.2))
    # знаменник (в'язка, синє)
    b, w, h = textbox(415, 184, "в'язка  ≈  μ·v·L", size=15, pad=11,
                      fill="#eef1fb", stroke=NEG, sw=1.5, bold=True)
    f.append(b)
    # результат
    f.append(text(614, 158, "=  ρ·v·L / μ", size=22, bold=True, anchor="start"))
    f.append(text(W / 2, 232, "інерція плодить вихори · в'язкість згладжує в шари",
                  size=13, color=MUTED))

    # ── два панелі: ламінарний ↔ турбулентний ──
    # лівий: мале Re — шари
    f.append(rect(100, 262, 290, 168, fill="#f6f9ff", stroke=NEG, sw=1.4))
    f.append(text(245, 288, "мале Re: в'язкість перемагає", size=13, bold=True, color=NEG))
    for i in range(5):
        yy = 312 + i * 15
        f.append(line(126, yy, 364, yy, color=NEG, sw=2.6))
    f.append(text(245, 414, "ламінарний — рівні шари", size=12, color=MUTED))

    # правий: велике Re — вихори
    f.append(rect(430, 262, 290, 168, fill="#fff6f4", stroke=POS, sw=1.4))
    f.append(text(575, 288, "велике Re: інерція перемагає", size=13, bold=True, color=POS))
    eddies = [(486, 330, 16), (534, 358, 13), (512, 388, 11),
              (582, 332, 14), (626, 360, 17), (664, 386, 12), (610, 392, 10)]
    for (cx, cy, r) in eddies:
        f.append(circle(cx, cy, r, fill="none", stroke=POS, sw=2.0))
        # маленький «хвостик» завитка
        f.append(polyline([(cx + r, cy), (cx + r + 7, cy - 5)], color=POS, sw=2.0))
    f.append(text(575, 414, "турбулентний — вихори", size=12, color=MUTED))

    # ── нижня вісь «Re зростає» ──
    f.append(varrow(150, 462, 690, 462, color=INK, sw=2.0, head=12))
    f.append(text(150, 481, "мале Re", size=12, color=NEG, anchor="middle", bold=True))
    f.append(text(690, 481, "велике Re", size=12, color=POS, anchor="middle", bold=True))
    f.append(text(420, 481, "число Рейнольдса зростає  →", size=12, color=MUTED))
    return render(os.path.join(IMG, "two-forces.svg"), W, H, *f)


# ── Фігура 2: дослід Рейнольдса — барвник у трубі ────────────────────────────
def fig_laminar_turbulent():
    W, H = 840, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дослід Рейнольдса: цівка барвника у скляній трубі", size=18, bold=True))

    def tube(y0):
        return rect(110, y0, 620, 66, fill="#fbfdff", stroke=INK, sw=1.8)

    # верхня труба — ламінарна нитка
    ytop = 82
    f.append(tube(ytop))
    cyt = ytop + 33
    f.append(varrow(52, cyt, 106, cyt, color=POS, sw=2.4, head=9))
    f.append(text(70, cyt - 12, "барвник", size=11, color=POS, anchor="middle"))
    f.append(line(112, cyt, 728, cyt, color=POS, sw=3.2))
    f.append(text(420, ytop + 96, "ламінарний — нитка ціла  (Re < 2300)",
                  size=14, bold=True, color=NEG))

    # нижня труба — турбулентний зрив
    ybot = 236
    f.append(tube(ybot))
    cyb = ybot + 33
    xbreak = 430
    f.append(line(112, cyb, xbreak, cyb, color=POS, sw=3.2))
    # точка переходу — вертикальний пунктир
    f.append(line(xbreak, ybot - 4, xbreak, ybot + 70, color=MUTED, sw=1.5, dash="5 4"))
    f.append(text(xbreak, ybot - 12, "точка переходу", size=11, color=MUTED))
    # зрив у вихори: кілька хвиль зі зростанням амплітуди
    for k, ph in enumerate((0.0, 2.1, 4.2, 1.0)):
        pts = []
        for i in range(61):
            t = i / 60.0
            x = xbreak + (728 - xbreak) * t
            amp = 3 + 24 * t
            y = cyb + amp * math.sin(9 * t + ph) * (0.6 + 0.4 * (k % 2))
            y = max(ybot + 6, min(ybot + 60, y))
            pts.append((x, y))
        f.append(polyline(pts, color=POS, sw=2.0))
    f.append(text(420, ybot + 96, "турбулентний — нитка зривається у вихори  (Re > 4000)",
                  size=14, bold=True, color=POS))

    # підсумок
    b, w, h = textbox(W / 2, H - 26,
                      "Перемикає не швидкість сама по собі, а комбінація  Re = ρ·v·L / μ",
                      size=13, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "laminar-turbulent.svg"), W, H, *f)


# ── Фігура 3: драбина чисел Рейнольдса в природі ─────────────────────────────
def fig_reynolds_ladder():
    W, H = 940, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Число Рейнольдса в природі — десяток порядків", size=18, bold=True))
    f.append(text(W / 2, 52, "ліворуч править в'язкість (лад), праворуч — інерція (хаос)",
                  size=12, color=MUTED))

    ox, xr = 95, 880
    axy = 210
    dec0, dec1 = -5, 9                 # межі осі: 10⁻⁵ … 10⁹
    span = float(dec1 - dec0)

    def px(Re):
        return ox + (math.log10(Re) - dec0) / span * (xr - ox)

    # смуги режимів (за спиною осі)
    f.append(rect(px(1e-5), 88, px(1e2) - px(1e-5), 214, fill="#eef1fb", stroke='none', sw=0, rx=0))
    f.append(rect(px(1e2), 88, px(1e4) - px(1e2), 214, fill="#fdf0e4", stroke='none', sw=0, rx=0))
    f.append(rect(px(1e4), 88, px(1e9) - px(1e4), 214, fill="#fbe4e0", stroke='none', sw=0, rx=0))

    # підписи зон
    f.append(text((px(1e-5) + px(1e2)) / 2, 108, "ламінарний світ (в'язкість)",
                  size=13, bold=True, color=NEG))
    f.append(text((px(1e4) + px(1e9)) / 2, 108, "турбулентний світ (інерція)",
                  size=13, bold=True, color=POS))
    f.append(text((px(1e2) + px(1e4)) / 2, 108, "перехід", size=12, bold=True, color="#b5651d"))
    f.append(text((px(1e2) + px(1e4)) / 2, 300, "поріг залежить", size=10, color="#b5651d"))
    f.append(text((px(1e2) + px(1e4)) / 2, 314, "від форми", size=10, color="#b5651d"))

    # вісь + позначки декад
    f.append(varrow(ox, axy, xr + 20, axy, color=INK, sw=1.8, head=11))
    for d in range(dec0, dec1 + 1, 2):
        x = px(10.0 ** d)
        f.append(line(x, axy, x, axy + 6, color=INK, sw=1.4))
        f.append(text(x, axy + 22, sup10(d), size=12, color=MUTED))
    f.append(text(xr + 20, axy - 10, "Re", size=13, bold=True, italic=True, anchor="start"))

    # маркери: (Re, назва, підпис-значення)
    marks = [
        (3e-5, "бактерія",     "~3·" + sup10(-5)),
        (1e-2, "сперматозоїд", "~" + sup10(-2)),
        (1e2,  "летюча комаха", "~" + sup10(2)),
        (5e4,  "риба",         "~5·" + sup10(4)),
        (4e6,  "плавець",      "~4·" + sup10(6)),
        (3e7,  "літак",        "~3·" + sup10(7)),
        (3e8,  "кит",          "~3·" + sup10(8)),
    ]
    for i, (Re, name, val) in enumerate(marks):
        x = px(Re)
        zone = NEG if Re < 1e2 else (POS if Re >= 1e4 else "#b5651d")
        f.append(circle(x, axy, 6, fill=zone, stroke=BG, sw=1.5))
        vy = 188 if i % 2 == 0 else 170          # значення над віссю (у два рівні)
        ny = 250 if i % 2 == 0 else 272          # назва під віссю (у два рівні)
        f.append(text(x, vy, val, size=11, color=MUTED))
        f.append(text(x, ny, name, size=12, bold=True))
    return render(os.path.join(IMG, "reynolds-ladder.svg"), W, H, *f)


# ── Фігура 4: часова стрічка — троє людей, одне число ────────────────────────
def fig_timeline():
    W, H = 900, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Одне число — три внески за 57 років", size=18, bold=True))
    f.append(text(W / 2, 58, "група (Стокс) → дослід і поріг (Рейнольдс) → назва (Зоммерфельд)",
                  size=13, color=MUTED))

    axy = 150
    f.append(varrow(80, axy, 846, axy, color=INK, sw=2.0, head=12))
    f.append(text(806, 138, "час →", size=11, color=MUTED, anchor="middle"))

    nodes = [
        (210, "1851", NEG, "#eef1fb",
         ["Джордж Стокс", "G. G. Stokes", "ірландець · Кембридж",
          "ідея: група ρ·v·L/μ", "з аналізу маятника"]),
        (470, "1883", FIELD, "#eafaf1",
         ["Осборн Рейнольдс", "O. Reynolds", "нар. Белфаст · Манчестер",
          "дослід у скляній трубі", "→ поріг переходу"]),
        (730, "1908", POS, "#fdecea",
         ["Арнольд Зоммерфельд", "A. Sommerfeld", "німець · конгрес у Римі",
          "дає назву", "«число Рейнольдса»"]),
    ]
    for (x, year, col, tint, lines) in nodes:
        f.append(text(x, 108, year, size=22, color=col, bold=True))
        b, w, h = textbox(x, 254, lines, size=12, pad=9, fill=tint, stroke=col, sw=1.6)
        top = 254 - h / 2
        f.append(line(x, 160, x, top, color=col, sw=1.6))
        f.append(circle(x, axy, 10, fill=col, stroke=BG, sw=2.5))
        f.append(b)

    b, w, h = textbox(W / 2, 366,
                      "Закон епонімії Стіглера: відкриття рідко зветься іменем першовідкривача",
                      size=13, pad=11, fill="#f4f6f8", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "reynolds-timeline.svg"), W, H, *f)


# ── Фігура 5: знерозмірнення НС — Re як єдиний коефіцієнт (для math-вставки) ──
def fig_nondim_terms():
    W, H = 880, 424
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Знерозмірнення Нав'є–Стокса: Re як єдиний коефіцієнт",
                  size=18, bold=True))

    cols = [(60, 300), (380, 220), (620, 200)]      # (x, width)
    ccx = [x + w / 2 for (x, w) in cols]

    # шапка
    hy, hh = 60, 40
    for (x, w), lab in zip(cols, ["член Нав'є–Стокса", "масштаб (порядок)", "÷ (ρv²/L)"]):
        f.append(rect(x, hy, w, hh, fill="#eef1f5", stroke=LINE, sw=1.3, rx=6))
        f.append(text(x + w / 2, hy + hh / 2 + 5, lab, size=13, bold=True, color=MUTED))

    rows = [
        ("інерція:  ρ(u·∇)u", "ρv²/L", "1", False),
        ("тиск:  ∇p", "ρv²/L", "1", False),
        ("в'язкість:  μ∇²u", "μv/L²", "1/Re", True),
    ]
    ry, rh, gap = 110, 50, 8
    for i, (a, b, c, hot) in enumerate(rows):
        y = ry + i * (rh + gap)
        f.append(rect(cols[0][0], y, cols[0][1], rh, fill=BG, stroke=LINE, sw=1.2, rx=6))
        f.append(text(ccx[0], y + rh / 2 + 5, a, size=15, bold=True))
        f.append(rect(cols[1][0], y, cols[1][1], rh, fill=BG, stroke=LINE, sw=1.2, rx=6))
        f.append(text(ccx[1], y + rh / 2 + 6, b, size=17, bold=True))
        fill3 = "#fff6f4" if hot else BG
        st3 = POS if hot else LINE
        f.append(rect(cols[2][0], y, cols[2][1], rh, fill=fill3, stroke=st3,
                      sw=(1.9 if hot else 1.2), rx=6))
        f.append(text(ccx[2], y + rh / 2 + 6, c, size=(19 if hot else 17), bold=True,
                      color=(POS if hot else INK), italic=hot))

    by = ry + 3 * (rh + gap) + 24
    b, w, h = textbox(W / 2, by,
                      "ділимо все на  ρv²/L  →  перед в'язким лишається  μ/(ρvL) = 1/Re",
                      size=14, pad=12, fill="#eef6ef", stroke=FIELD, sw=1.5, bold=True)
    f.append(b)
    f.append(text(W / 2, by + 40, "єдиний параметр керує всім розв'язком", size=12, color=MUTED))
    return render(os.path.join(IMG, "nondim-terms.svg"), W, H, *f)


# ── Фігура 6: два шляхи до Re сходяться (для math-вставки) ────────────────────
def fig_two_roads():
    W, H = 900, 442
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Два шляхи до одного числа Рейнольдса", size=18, bold=True))

    # лівий панель — оцінка
    lx, rx0, py, pw, ph = 55, 485, 66, 360, 186
    f.append(rect(lx, py, pw, ph, fill="#f6f9ff", stroke=NEG, sw=1.5))
    lcx = lx + pw / 2
    f.append(text(lcx, py + 28, "оцінка порядку величини", size=15, bold=True, color=NEG))
    f.append(text(lcx, py + 66, "сила інерції ≈ ρ·v²·L²", size=15))
    f.append(text(lcx, py + 98, "сила в'язкості ≈ μ·v·L", size=15))
    f.append(line(lx + 26, py + 118, lx + pw - 26, py + 118, color=MUTED, sw=1.3))
    f.append(text(lcx, py + 150, "інерція / в'язкість", size=13, color=MUTED))
    f.append(text(lcx, py + 172, "= ρvL/μ = Re", size=17, bold=True, color=NEG))

    # правий панель — знерозмірнення
    f.append(rect(rx0, py, pw, ph, fill="#fff6f4", stroke=POS, sw=1.5))
    rcx = rx0 + pw / 2
    f.append(text(rcx, py + 28, "знерозмірнення Нав'є–Стокса", size=15, bold=True, color=POS))
    f.append(text(rcx, py + 66, "Du*/Dt* = −∇*p* + (1/Re)∇*²u*", size=14, bold=True))
    f.append(text(rcx, py + 100, "коефіцієнт при в'язкому члені", size=13, color=MUTED))
    f.append(line(rx0 + 26, py + 118, rx0 + pw - 26, py + 118, color=MUTED, sw=1.3))
    f.append(text(rcx, py + 150, "= μ/(ρvL)", size=13, color=MUTED))
    f.append(text(rcx, py + 172, "= 1/Re", size=17, bold=True, color=POS))

    # стрілки, що сходяться до банера
    f.append(varrow(lcx + 40, py + ph + 4, 432, 342, color=INK, sw=2.0, head=11))
    f.append(varrow(rcx - 40, py + ph + 4, 468, 342, color=INK, sw=2.0, head=11))

    b, w, h = textbox(W / 2, 366,
                      "той самий дріб  Re = ρvL/μ  керує всім потоком",
                      size=15, pad=12, fill="#eef6ef", stroke=FIELD, sw=1.5, bold=True)
    f.append(b)
    f.append(text(W / 2, 410,
                  "оцінка дає Re, знерозмірнення — обернене 1/Re: те саме відношення тих самих двох членів",
                  size=12, color=MUTED))
    return render(os.path.join(IMG, "two-roads.svg"), W, H, *f)


# ── Фігура: конвеєр калькулятора — вхід → Re → режим → втрати (для proj-вставки) ─
def fig_calc_flow():
    W, H = 940, 636
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Калькулятор течії в трубі: вхід → Re → режим → втрати",
                  size=17, bold=True))
    cx = W / 2

    # вхід
    b, w, h = textbox(cx, 72, "вхід:   ρ · v · D · μ · L · ε", size=14, pad=12,
                      fill="#eef6ef", stroke=FIELD, sw=1.6, bold=True)
    f.append(b)
    f.append(varrow(cx, 72 + h / 2, cx, 72 + h / 2 + 24, color=INK, sw=2.0, head=11))

    # Re
    yre = 72 + h / 2 + 24 + 24
    b, w, h = textbox(cx, yre, "Re = ρ·v·D / μ      ( D — ДІАМЕТР, не радіус )",
                      size=15, pad=12, fill=FILL, stroke=INK, sw=1.9, bold=True)
    f.append(b)
    re_bot = yre + h / 2
    f.append(text(cx, re_bot + 20, "порівняти Re з порогами круглої труби", size=12, color=MUTED))

    # розводка на три колонки
    colx = [178, cx, 762]
    fork_y = re_bot + 34
    branch_top = fork_y + 26
    for x in colx:
        f.append(line(cx, fork_y, x, branch_top - 4, color=INK, sw=1.7))
        f.append(head_at(x, branch_top - 2, 0, 1, INK, 9))

    # режим
    reg = [("Re < 2300", "ламінарний", "#eef1fb", NEG),
           ("2300 … 4000", "перехідний", "#fdf0e4", "#b5651d"),
           ("Re > 4000", "турбулентний", "#fbe4e0", POS)]
    reg_cy = branch_top + 26
    reg_bot = 0
    for x, (r1, r2, fill, col) in zip(colx, reg):
        b, bw, bh = textbox(x, reg_cy, r1 + "\n" + r2, size=13, pad=10,
                            fill=fill, stroke=col, sw=1.6, bold=True, color=col)
        f.append(b)
        reg_bot = reg_cy + bh / 2
        f.append(varrow(x, reg_bot, x, reg_bot + 30, color=INK, sw=1.7, head=9))

    # коефіцієнт тертя
    frm_cy = reg_bot + 30 + 34
    frm = [("f = 64 / Re", "точно — з Пуазейля", NEG, "#eef1fb"),
           ("f = Гааланд", "як турбулент + флаг", "#b5651d", "#fdf0e4"),
           ("f = Гааланд(Re, ε/D)", "наближення Коулбрука", POS, "#fbe4e0")]
    frm_bot = 0
    for x, (t1, t2, col, fill) in zip(colx, frm):
        b, bw, bh = textbox(x, frm_cy, t1 + "\n" + t2, size=12.5, pad=10,
                            fill=fill, stroke=col, sw=1.5, bold=True, color=INK)
        f.append(b)
        frm_bot = frm_cy + bh / 2

    # злиття → Δp
    merge_arr = frm_bot + 30
    for x in colx:
        f.append(line(x, frm_bot, cx, merge_arr - 4, color=INK, sw=1.6))
    f.append(head_at(cx, merge_arr - 2, 0, 1, INK, 9))
    dp_cy = merge_arr + 24
    b, w, h = textbox(cx, dp_cy, "Δp = f · (L / D) · (ρ·v² / 2)       ← Дарсі–Вайсбах",
                      size=14, pad=12, fill="#eef6ef", stroke=FIELD, sw=1.7, bold=True)
    f.append(b)
    dp_bot = dp_cy + h / 2
    f.append(text(cx, dp_bot + 18, "ρ·v²/2 — динамічний тиск потоку", size=11, color=MUTED))
    f.append(varrow(cx, dp_bot + 28, cx, dp_bot + 52, color=INK, sw=1.9, head=11))
    b, w, h = textbox(cx, dp_bot + 74, "вихід:   режим · f · Δp · напір h = Δp/(ρg)",
                      size=13, pad=11, fill=BG, stroke=INK, sw=1.6, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "calc-flow.svg"), W, H, *f)


# ── Фігура: коефіцієнт тертя проти Re (спрощена діаграма Муді, для proj-вставки) ─
def fig_friction_curve():
    W, H = 900, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Коефіцієнт тертя проти Re — дві різні формули, розрив між ними",
                  size=16, bold=True))

    L, R, T, Bt = 120, 830, 82, 452
    xd0, xd1 = 2, 7
    fmax, fmin = 0.8, 0.007
    ly0, ly1 = math.log10(fmax), math.log10(fmin)

    def px(Re): return L + (math.log10(Re) - xd0) / (xd1 - xd0) * (R - L)
    def py(fr): return T + (ly0 - math.log10(fr)) / (ly0 - ly1) * (Bt - T)

    # сітка
    for d in range(xd0, xd1 + 1):
        x = px(10.0 ** d)
        f.append(line(x, T, x, Bt, color="#e9ebee", sw=1.0))
        f.append(text(x, Bt + 22, sup10(d), size=12, color=MUTED))
    for fv in (0.01, 0.02, 0.05, 0.1, 0.2, 0.5):
        y = py(fv)
        f.append(line(L, y, R, y, color="#e9ebee", sw=1.0))
        f.append(text(L - 12, y + 4, ("%.2f" % fv).rstrip('0').rstrip('.'),
                      size=11, color=MUTED, anchor="end"))
    f.append(rect(L, T, R - L, Bt - T, fill="none", stroke=INK, sw=1.6))
    f.append(text((L + R) / 2, Bt + 44, "число Рейнольдса  Re", size=13, color=INK))
    f.append(text(L - 34, T - 18, "f", size=15, color=INK, anchor="start", bold=True, italic=True))

    # перехідна смуга
    xa, xb = px(2300), px(4000)
    f.append(rect(xa, T, xb - xa, Bt - T, fill="#fdf0e4", stroke='none', sw=0, rx=0))
    f.append(text((xa + xb) / 2, T - 6, "перехід", size=11, color="#b5651d", bold=True))

    # ламінарна пряма f = 64/Re
    lam = [(px(Re), py(64.0 / Re)) for Re in (100, 150, 220, 330, 500, 800, 1200, 1800, 2300)]
    f.append(polyline(lam, color=NEG, sw=3.0))
    f.append(text(px(250), py(64 / 250) - 12, "ламінар  f = 64/Re",
                  size=12, color=NEG, anchor="start", bold=True))

    # турбулентні криві Гааланда, дві шорсткості
    def haal(Re, rr):
        return (1.0 / (-1.8 * math.log10((rr / 3.7) ** 1.11 + 6.9 / Re))) ** 2

    for rr, col, lab, labx, dy in ((1e-6, POS, "гладка труба (ε/D → 0)", 3.2e6, -14),
                                   (1e-2, "#7a1f14", "шорстка  ε/D = 0.01", 3.2e6, 22)):
        pts = []
        Re = 4000.0
        while Re <= 1e7:
            pts.append((px(Re), py(haal(Re, rr))))
            Re *= 1.14
        f.append(polyline(pts, color=col, sw=3.0))
        f.append(text(px(labx), py(haal(labx, rr)) + dy, lab, size=11, color=col,
                      anchor="middle", bold=True))

    # точка прикладу: вода Re=15000, f≈0.028
    xe, ye = px(15000), py(haal(15000, 1e-4))
    f.append(circle(xe, ye, 6, fill=FIELD, stroke=BG, sw=1.6))
    f.append(text(xe, ye + 22, "вода в крані  (Re≈15000, f≈0.028)",
                  size=11, color=FIELD, anchor="middle", bold=True))
    return render(os.path.join(IMG, "friction-curve.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_two_forces(), fig_laminar_turbulent(), fig_reynolds_ladder(), fig_timeline(),
          fig_nondim_terms(), fig_two_roads(), fig_calc_flow(), fig_friction_curve()]
    print("written:")
    for p in ps:
        print("  ", p)
