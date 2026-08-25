# -*- coding: utf-8 -*-
"""Фігури до теми «Малошумний підсилювач (LNA)» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  front-end-place.svg — місце LNA: антена → LNA (перший!) → решта тракту; він ставить підлогу шуму
  why-first.svg       — той самий каскад першим і другим: першим топить шум решти, другим — ні
  three-axes.svg      — три осі LNA: малий шум · достатнє підсилення · лінійність (тиснуть одна на одну)
  blocker.svg         — кволий корисний сигнал поряд із могутнім сусіднім каналом; LNA має не зім'яти його
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _amp(x, cy, w=58, h=52, lbl="LNA", fill=FILL, line=LINE, lblcol=INK, glbl=None):
    """Трикутник-підсилювач вістрям праворуч; повертає список фрагментів."""
    out = ['<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
           % (x, cy - h / 2, x, cy + h / 2, x + w, cy, fill, line)]
    out.append(text(x + w * 0.40, cy + 5, lbl, size=13, bold=True, color=lblcol))
    if glbl:
        out.append(text(x + w * 0.40, cy - h / 2 - 8, glbl, size=11, color=MUTED))
    return out


def front_end_place():
    """Антена → LNA (перший) → змішувач/фільтр/АЦП. LNA бачить сигнал ще крихітним і ставить підлогу шуму."""
    W, H = 740, 320
    p = []
    cy = 130
    # антена
    ax = 60
    p.append(line(ax, cy + 28, ax, cy - 26, color=INK, sw=2))
    p.append(line(ax - 16, cy - 26, ax + 16, cy - 26, color=INK, sw=2))
    p.append(line(ax - 16, cy - 26, ax, cy - 6, color=INK, sw=2))
    p.append(line(ax + 16, cy - 26, ax, cy - 6, color=INK, sw=2))
    p.append(text(ax, cy + 46, "антена", size=12, color=MUTED))
    p.append(text(ax, cy - 44, "кволий сигнал", size=11, color=NEG))
    p.append(arrow(ax, cy + 28, 150, cy + 28, color=INK, sw=2))
    # LNA — перший, виділений
    p += _amp(150, cy + 28, lbl="LNA", fill="#eafaf0", line=FIELD, lblcol=FIELD, glbl="перший каскад")
    p.append(arrow(208, cy + 28, 250, cy + 28, color=INK, sw=2))
    # решта тракту — три простіші блоки
    blocks = [("змішувач", 250), ("фільтр", 370), ("АЦП", 490)]
    for lbl, bx in blocks:
        p.append(rect(bx, cy + 28 - 24, 92, 48, fill=FILL, stroke=LINE, sw=1.5))
        p.append(text(bx + 46, cy + 28 + 5, lbl, size=12))
        if bx < 490:
            p.append(arrow(bx + 92, cy + 28, bx + 120, cy + 28, color=INK, sw=2))
    p.append(arrow(490 + 92, cy + 28, 600, cy + 28, color=INK, sw=2))
    p.append(text(620, cy + 28 + 5, "далі", size=12, color=MUTED, anchor="start"))

    # підлога шуму, яку ставить LNA — пунктирна лінія попід усім трактом
    fy = cy + 92
    p.append(line(120, fy, 660, fy, color=POS, sw=1.6, dash="5 4"))
    p.append(text(120, fy + 16, "шумову підлогу всього тракту ставить ЦЕЙ перший каскад",
                  size=11, color=POS, anchor="start"))

    b, _, _ = textbox(W / 2, 280,
                      "LNA — найперший активний елемент після антени: він бачить сигнал ще крихітним.\n"
                      "Його власний шум лягає на цей сигнал у повну силу — тому каскад має бути найтихіший.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'front-end-place.svg'), W, H, *p,
           title="Місце LNA у тракті: перший каскад після антени ставить підлогу шуму")


def why_first():
    """Той самий шумливий каскад: коли він ДРУГИЙ — його шум поділений на G першого; коли ПЕРШИЙ — ні."""
    W, H = 720, 430
    p = []
    # ── варіант А: LNA першим, шумливий змішувач другим ──
    def chain(y, first_lbl, first_fill, first_line, first_g, second_lbl, note, noisebar_frac, barcol):
        out = []
        x = 70
        out.append(arrow(30, y, x, y, color=INK, sw=2))
        out.append(text(20, y + 5, "вх", size=11, color=MUTED, anchor="end"))
        out += _amp(x, y, lbl=first_lbl, fill=first_fill, line=first_line,
                    lblcol=(first_line if first_line != LINE else INK), glbl=first_g)
        out.append(arrow(x + 58, y, x + 100, y, color=INK, sw=2))
        # другий каскад — завжди той самий шумливий змішувач
        out += _amp(x + 100, y, lbl=second_lbl, fill="#fdecea", line=POS, lblcol=POS, glbl="+шумить")
        out.append(arrow(x + 158, y, x + 200, y, color=INK, sw=2))
        out.append(text(x + 220, y + 5, "вих", size=11, color=MUTED, anchor="start"))
        out.append(text(x + 110, y + 60, note, size=11, color=MUTED))
        # стовпчик: внесок шуму ДРУГОГО каскаду, зведений до входу
        bx = 470
        maxh = 120
        h = max(8, maxh * noisebar_frac)
        fillc = "#eafaf0" if barcol == FIELD else "#fdecea"
        out.append(rect(bx, y + 30 - h, 64, h, fill=fillc, stroke=barcol, sw=2))
        out.append(text(bx + 32, y + 30 - h - 7, "%.0f%%" % (noisebar_frac * 100),
                        size=11, bold=True, color=barcol))
        out.append(text(bx + 130, y + 30 - h / 2 - 6, "шум змішувача", size=11, color=MUTED, anchor="middle"))
        out.append(text(bx + 130, y + 30 - h / 2 + 9, "на вході", size=11, color=MUTED, anchor="middle"))
        return out

    p.append(text(30, 50, "LNA попереду (велике G тихо підсилює):", size=13, bold=True, anchor="start"))
    p += chain(110, "LNA", "#eafaf0", FIELD, "G=25 дБ", "зміш.", "сигнал уже великий — шум змішувача топиться",
               0.05, FIELD)
    p.append(line(40, 200, W - 40, 200, color=MUTED, sw=1, dash="3 3"))
    p.append(text(30, 240, "без LNA (змішувач бачить кволий сигнал першим):", size=13, bold=True, anchor="start"))
    p += chain(300, "зміш.", "#fdecea", POS, "G≈0 дБ", "—", "слабкий сигнал — шум змішувача лягає в повну силу",
               0.92, POS)

    b, _, _ = textbox(W / 2, 405,
                      "Той самий шумливий змішувач. Попереду тихий LNA з великим G — і шум змішувача,\n"
                      "зведений до входу, поділений на цей G майже в нуль. Без LNA він б'є в повну силу.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'why-first.svg'), W, H, *p,
           title="Чому LNA ставлять першим: великим підсиленням він топить шум решти тракту")


def three_axes():
    """Три осі-вимоги LNA, що тиснуть одна на одну: малий шум, достатнє підсилення, лінійність."""
    W, H = 700, 420
    p = []
    cx, cy = 350, 215
    R = 130
    # трикутник вимог
    import math as _m
    pts = []
    labels = [
        ("малий ШУМ", FIELD, "тиша на вході"),
        ("достатнє\nПІДСИЛЕННЯ", NEG, "щоб утопити шум решти"),
        ("ЛІНІЙНІСТЬ", POS, "не зім'яти сильні сусідні канали"),
    ]
    for i in range(3):
        a = -_m.pi / 2 + i * 2 * _m.pi / 3
        pts.append((cx + R * _m.cos(a), cy + R * _m.sin(a)))
    # сторони трикутника
    for i in range(3):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 3]
        p.append(line(x1, y1, x2, y2, color=MUTED, sw=1.6, dash="4 4"))
    # вузли
    for (lbl, col, note), (x, y) in zip(labels, pts):
        fillc = {"#27ae60": "#eafaf0", "#2457d6": "#eaf0fd", "#c0392b": "#fdecea"}[col]
        p.append(circle(x, y, 8, fill=fillc, stroke=col, sw=2))
        # підпис назовні від центра
        dx = (x - cx)
        dy = (y - cy)
        n = _m.hypot(dx, dy)
        ox = x + dx / n * 26
        oy = y + dy / n * 22
        for k, ln in enumerate(lbl.split("\n")):
            p.append(text(ox, oy - 6 + k * 16, ln, size=13, bold=True, color=col))
        p.append(text(ox, oy - 6 + len(lbl.split("\n")) * 16, note, size=10, color=MUTED))
    # центр
    p.append(text(cx, cy - 6, "компроміс", size=13, bold=True, color=INK))
    p.append(text(cx, cy + 12, "LNA", size=13, bold=True, color=INK))
    # стрілки-натяг між вимогами
    p.append(text(cx, cy + 40, "усі три тягнуть транзистор і струм у різні боки", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 392,
                      "LNA не оптимізують за однією величиною. Найнижчий шум, достатнє підсилення\n"
                      "й лінійність борються за той самий транзистор і струм — проєкт LNA є компромісом.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'three-axes.svg'), W, H, *p,
           title="Три вимоги до LNA, що тиснуть одна на одну")


def blocker():
    """Кволий корисний канал поряд із могутнім сусіднім: лінійний LNA не дає сильному зім'яти слабкий."""
    W, H = 700, 360
    p = []
    ox, oy = 80, 270
    axw = 540
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))            # вісь частоти
    p.append(text(ox + axw, oy + 20, "частота", size=12, color=MUTED, anchor="end"))
    p.append(line(ox, oy, ox, 60, color=INK, sw=2))                  # вісь рівня
    p.append(text(ox - 8, 70, "рівень", size=12, color=MUTED, anchor="end"))

    # кволий корисний сигнал
    sx = ox + 120
    p.append(line(sx, oy, sx, oy - 40, color=NEG, sw=3))
    p.append(text(sx, oy - 50, "корисний", size=12, bold=True, color=NEG))
    p.append(text(sx, oy - 34, "(кволий)", size=10, color=NEG))
    # могутній сусідній канал
    bx = ox + 360
    p.append(line(bx, oy, bx, 90, color=POS, sw=3))
    p.append(text(bx, 80, "сусідній канал", size=12, bold=True, color=POS))
    p.append(text(bx, 96, "(могутній)", size=10, color=POS))

    # дужка «динамічний діапазон, який LNA має витримати без спотворень»
    p.append(line(sx - 26, oy - 40, sx - 26, 90, color=MUTED, sw=1.4))
    p.append('<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="1.4" fill="none"/>'
             % (sx - 30, oy - 40, sx - 22, oy - 40, MUTED))
    p.append('<path d="M%.1f %.1f L%.1f %.1f" stroke="%s" stroke-width="1.4" fill="none"/>'
             % (sx - 30, 90, sx - 22, 90, MUTED))
    p.append(text(sx - 34, (oy - 40 + 90) / 2, "діапазон,", size=10, color=MUTED, anchor="end"))
    p.append(text(sx - 34, (oy - 40 + 90) / 2 + 14, "що його LNA", size=10, color=MUTED, anchor="end"))
    p.append(text(sx - 34, (oy - 40 + 90) / 2 + 28, "має витримати", size=10, color=MUTED, anchor="end"))

    b, _, _ = textbox(W / 2, 332,
                      "Антена приносить кволий корисний сигнал ВОДНОЧАС із могутнім сусіднім каналом.\n"
                      "Якщо сильний загне LNA в нелінійність, він породить завади просто на корисному.",
                      size=12, fill="#fbeeee", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'blocker.svg'), W, H, *p,
           title="Чому LNA має бути лінійним: слабкий сигнал поряд із могутнім сусідом")


# ── Фігури до історичної вставки (hist-cryo-lna) ────────────────────────────

def hist_timeline():
    """Падіння шумової температури вхідного каскаду крізь покоління: мазер/парамп → GaAs FET → HEMT → InP HEMT."""
    W, H = 760, 380
    p = []
    ox, oy = 90, 300        # початок осей
    axw, axh = 590, 230
    # вісь часу
    p.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))
    p.append(text(ox + axw, oy + 22, "роки", size=12, color=MUTED, anchor="end"))
    # вісь «шумова температура» (нижче — краще)
    p.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))
    p.append(text(ox - 10, oy - axh + 4, "шумова T", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - axh + 20, "(нижче — краще)", size=10, color=MUTED, anchor="end"))

    # стовпчики поколінь: (підпис, рік-підпис, частка висоти 0..1 за відносним шумом, колір)
    cols = [
        ("мазер /\nпарамп.", "1960-ті", 0.92, MUTED, "примхливі,\nвузька смуга"),
        ("охолодж.\nGaAs FET", "1980", 0.55, NEG, "Вайнреб:\nширше, стійко"),
        ("HEMT\n(GaAs)", "1980-ті", 0.30, FIELD, "2DEG —\nрізко тихіше"),
        ("InP\nHEMT", "сьогодні", 0.10, POS, "частки\nкельвіна"),
    ]
    n = len(cols)
    bw = 78
    gap = (axw - 70 - n * bw) / (n - 1)
    for i, (lbl, yr, frac, col, note) in enumerate(cols):
        bx = ox + 40 + i * (bw + gap)
        bh = axh * frac
        fillc = {MUTED: "#eef0f2", NEG: "#eaf0fd", FIELD: "#eafaf0", POS: "#fdecea"}[col]
        p.append(rect(bx, oy - bh, bw, bh, fill=fillc, stroke=col, sw=1.8))
        # назва покоління всередині/над стовпчиком
        for k, ln in enumerate(lbl.split("\n")):
            p.append(text(bx + bw / 2, oy - bh + 18 + k * 15, ln, size=12, bold=True, color=col))
        # рік під віссю
        p.append(text(bx + bw / 2, oy + 20, yr, size=11, color=INK))
        # коротка нота під роком
        for k, ln in enumerate(note.split("\n")):
            p.append(text(bx + bw / 2, oy + 38 + k * 13, ln, size=9, color=MUTED))

    # стрілка-напрям «усе тихіше»
    p.append(arrow(ox + 40 + bw / 2, oy - axh * 0.92 - 18,
                   ox + 40 + 3 * (bw + gap) + bw / 2, oy - axh * 0.10 - 18,
                   color=INK, sw=1.4))
    p.append(text((ox + 40 + bw / 2 + ox + 40 + 3 * (bw + gap) + bw / 2) / 2,
                  oy - axh - 6, "кожне покоління — тихіший вхід", size=11, color=INK))
    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *p,
           title="Шумова підлога вхідного каскаду крізь покоління")


def hist_2deg():
    """Чому HEMT тихий: домішки-донори рознесені з каналом, тож електрони течуть, не натикаючись на них."""
    W, H = 760, 360
    p = []
    # ── ліворуч: звичайний легований канал (донори ПОРЯД з електронами) ──
    lx, ly, lw, lh = 60, 90, 290, 150
    p.append(rect(lx, ly, lw, lh, fill="#fbeeee", stroke=POS, sw=1.6))
    p.append(text(lx + lw / 2, ly - 14, "звичайний легований канал", size=13, bold=True, color=POS))
    # донори (+) усередині каналу + електрони, що натикаються
    import random as _r
    _r.seed(7)
    donors = [(lx + 30 + i * 36, ly + 40) for i in range(7)]
    for dx, dy in donors:
        p.append(plus(dx, dy, r=7))
    # ламана траєкторія електрона — натикається на донори
    path = "M%.1f %.1f" % (lx + 12, ly + 110)
    xs = [lx + 12, lx + 55, lx + 95, lx + 140, lx + 185, lx + 230, lx + 275]
    ysn = [ly + 110, ly + 70, ly + 120, ly + 75, ly + 118, ly + 72, ly + 110]
    for xx, yy in zip(xs[1:], ysn[1:]):
        path += " L%.1f %.1f" % (xx, yy)
    p.append('<path d="%s" stroke="%s" stroke-width="2" fill="none"/>' % (path, NEG))
    p.append(minus(xs[0], ysn[0], r=7))
    p.append(text(lx + lw / 2, ly + lh + 22, "електрон натикається на донори →", size=11, color=POS))
    p.append(text(lx + lw / 2, ly + lh + 38, "розсіюється, шумить", size=11, bold=True, color=POS))

    # ── праворуч: HEMT — донори в окремому шарі, канал чистий (2DEG) ──
    rx, ry, rw, rh = 410, 90, 290, 150
    # верхній шар: легований AlGaAs (донори тут)
    p.append(rect(rx, ry, rw, 46, fill="#fdf0e8", stroke=MUTED, sw=1.4))
    p.append(text(rx + rw / 2, ry + 16, "легований AlGaAs — донори тут", size=10, color=MUTED))
    for i in range(7):
        p.append(plus(rx + 30 + i * 36, ry + 32, r=6))
    # нижній шар: чистий GaAs з 2DEG під межею
    p.append(rect(rx, ry + 46, rw, rh - 46, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(rx + rw / 2, ry + 70, "чистий GaAs (без домішок)", size=10, color=FIELD))
    # шар 2DEG — тонка смуга під межею
    gy = ry + 92
    p.append(line(rx + 8, gy, rx + rw - 8, gy, color=FIELD, sw=2, dash="3 3"))
    p.append(text(rx + rw / 2, gy + 16, "2DEG: електрони течуть тут", size=10, color=FIELD))
    # пряма траєкторія електрона — нічого не заважає
    p.append(arrow(rx + 14, gy - 6, rx + rw - 14, gy - 6, color=NEG, sw=2.2))
    p.append(minus(rx + 14, gy - 6, r=6))
    p.append(text(rx + rw / 2, ry + rh + 22, "донори в іншому шарі — електрон летить вільно →", size=11, color=FIELD))
    p.append(text(rx + rw / 2, ry + rh + 38, "майже не розсіюється, тихо", size=11, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 332,
                      "Уся хитрість HEMT: донори, що віддають електрони, винесені в ОКРЕМИЙ шар, осторонь каналу.\n"
                      "Електрони течуть у чистому шарі, не натикаючись на заряджені домішки, — тому шумлять менше.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'hist-2deg.svg'), W, H, *p,
           title="Чому HEMT тихий: рознести донори й канал")


if __name__ == '__main__':
    front_end_place()
    why_first()
    three_axes()
    blocker()
    hist_timeline()
    hist_2deg()
    print("OK: 6 figures ->", OUT)
