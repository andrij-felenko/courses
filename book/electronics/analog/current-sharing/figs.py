# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def source_box(cx, cy, eps, r, color):
    """Маленька рамка-джерело: ЕРС + внутрішній опір."""
    b, w, h = textbox(cx, cy, "ЕРС %s\nr = %s" % (eps, r), size=14, pad=11,
                      bold=True, fill="#f4f6f8", stroke=color, sw=2.2)
    return b, w, h


# ── 1. Два джерела під спільним навантаженням ───────────────────────────────
def fig_two_sources():
    W, H = 720, 380
    parts = []
    # два джерела ліворуч (вгорі/внизу), вузол посередині, навантаження праворуч
    top_y, bot_y = 110, 270
    sx = 150
    nx = 430          # спільний вузол
    lx = 600          # навантаження

    b1, w1, h1 = source_box(sx, top_y, "ε₁", "r₁", NEG)
    b2, w2, h2 = source_box(sx, bot_y, "ε₂", "r₂", POS)
    parts += [b1, b2]

    # дроти від джерел до вузла
    parts.append(line(sx + w1 / 2, top_y, nx, top_y, color=LINE, sw=2))
    parts.append(line(sx + w2 / 2, bot_y, nx, bot_y, color=LINE, sw=2))
    parts.append(line(nx, top_y, nx, bot_y, color=LINE, sw=2))
    # вузол
    parts.append(circle(nx, (top_y + bot_y) / 2, 5, fill=INK, stroke=INK))
    parts.append(text(nx + 14, (top_y + bot_y) / 2 - 8, "спільна", size=12, color=MUTED, anchor="start"))
    parts.append(text(nx + 14, (top_y + bot_y) / 2 + 8, "напруга V", size=12, color=MUTED, anchor="start"))

    # навантаження
    parts.append(rect(lx, (top_y + bot_y) / 2 - 36, 54, 72, fill="#eafaf0", stroke=FIELD, sw=2))
    parts.append(text(lx + 27, (top_y + bot_y) / 2 - 6, "наван-", size=12, color=FIELD, bold=True))
    parts.append(text(lx + 27, (top_y + bot_y) / 2 + 10, "таження", size=12, color=FIELD, bold=True))
    parts.append(line(nx, (top_y + bot_y) / 2, lx, (top_y + bot_y) / 2, color=LINE, sw=2))

    # стрілки струмів I1, I2 (товщина натякає на більший струм у меншого r)
    parts.append(arrow(sx + w1 / 2 + 14, top_y - 18, nx - 30, top_y - 18, color=NEG, sw=3.2))
    parts.append(text((sx + nx) / 2, top_y - 26, "I₁ = (ε₁ − V)/r₁", size=13, color=NEG, bold=True))
    parts.append(arrow(sx + w2 / 2 + 14, bot_y + 18, nx - 30, bot_y + 18, color=POS, sw=2.0))
    parts.append(text((sx + nx) / 2, bot_y + 36, "I₂ = (ε₂ − V)/r₂", size=13, color=POS, bold=True))

    # підпис закону поділу
    parts.append(fitbox(nx + 64, (top_y + bot_y) / 2 + 60, 196, 40,
                        "I₁/I₂ = r₂/r₁  (обернено до r)",
                        size=13, fill="#fff8e1", stroke="#d9a400", color="#7a5d00", bold=True))
    return render(os.path.join(OUT, 'two-sources.svg'), W, H, *parts,
                  title="Два джерела на спільне навантаження — спільна напруга, різні струми")


# ── 2. Зрівнювальний (циркуляційний) струм за різних ЕРС ─────────────────────
def fig_circulating():
    W, H = 720, 380
    parts = []
    top_y, bot_y = 110, 270
    sx = 150
    nx = 440
    lx = 600

    b1, w1, h1 = source_box(sx, top_y, "ε₁ більша", "r₁", POS)
    b2, w2, h2 = source_box(sx, bot_y, "ε₂ менша", "r₂", NEG)
    parts += [b1, b2]

    parts.append(line(sx + w1 / 2, top_y, nx, top_y, color=LINE, sw=2))
    parts.append(line(sx + w2 / 2, bot_y, nx, bot_y, color=LINE, sw=2))
    parts.append(line(nx, top_y, nx, bot_y, color=LINE, sw=2))
    parts.append(circle(nx, (top_y + bot_y) / 2, 5, fill=INK, stroke=INK))

    # навантаження
    parts.append(rect(lx, (top_y + bot_y) / 2 - 30, 50, 60, fill="#eafaf0", stroke=FIELD, sw=2))
    parts.append(text(lx + 25, (top_y + bot_y) / 2 + 4, "наван-", size=11, color=FIELD, bold=True))
    parts.append(line(nx, (top_y + bot_y) / 2, lx, (top_y + bot_y) / 2, color=LINE, sw=2))

    # головна ідея: зрівнювальний струм по контуру з джерела 1 у джерело 2
    # стрілка вниз по вертикалі вузла — струм "провалюється" у слабше джерело
    parts.append(arrow(nx - 18, top_y + 18, nx - 18, bot_y - 18, color=POS, sw=3.4))
    parts.append(text(nx - 30, (top_y + bot_y) / 2, "зрівнювальний", size=12, color=POS, anchor="end", bold=True))
    parts.append(text(nx - 30, (top_y + bot_y) / 2 + 16, "струм у ε₂", size=12, color=POS, anchor="end"))

    # формула
    parts.append(fitbox(180, 330, 360, 38,
                        "I_зрівн = (ε₁ − ε₂)/(r₁ + r₂)  — тече навіть БЕЗ навантаження",
                        size=13, fill="#fdecea", stroke=POS, color=POS, bold=True))
    parts.append(text(lx + 25, 70, "ε₁ «загарбує» струм", size=12, color=POS, anchor="middle", bold=True))
    return render(os.path.join(OUT, 'circulating.svg'), W, H, *parts,
                  title="Різні ЕРС → зрівнювальний струм і загарбання")


# ── 3. Три способи приборкати поділ ─────────────────────────────────────────
def fig_cures():
    W, H = 740, 360
    parts = []
    col = [150, 440, 645]   # три колонки? зробимо рівномірно
    col = [W * 0.2, W * 0.5, W * 0.8]
    titles = ["Баласт", "Розв'язув. діоди", "Просідання"]
    colors = ["#d9a400", NEG, FIELD]
    descs = [
        "малий R у кожну\nгілку → менша\nчутливість до Δε",
        "діод вістрям до\nвузла → зворотний\nструм неможливий",
        "блок сам знижує\nнапругу зі струмом\n→ сусіди беруть",
    ]
    fills = ["#fff8e1", "#eaf0fd", "#eafaf0"]
    strokes = ["#d9a400", NEG, FIELD]
    inks = ["#7a5d00", NEG, FIELD]
    for cx, t, c, d, fl, st, ik in zip(col, titles, colors, descs, fills, strokes, inks):
        parts.append(text(cx, 70, t, size=15, bold=True, color=ik))
        parts.append(fitbox(cx - 105, 95, 210, 110, d, size=14, fill=fl, stroke=st, color=ik))
    # розділювачі
    parts.append(line(W / 3, 56, W / 3, H - 70, color=MUTED, sw=1, dash="5 5"))
    parts.append(line(2 * W / 3, 56, 2 * W / 3, H - 70, color=MUTED, sw=1, dash="5 5"))
    # нижня смуга-висновок
    parts.append(fitbox(W * 0.5 - 280, H - 56, 560, 38,
                        "Спільне: збільшити ефективний опір гілки або активно підрівняти напруги",
                        size=13, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'cures.svg'), W, H, *parts,
                  title="Як вирівняти поділ струму між джерелами")


# ── 4. Чутливість поділу гасне зі зростанням R_б ────────────────────────────
def fig_sensitivity():
    """|ΔI| перекосу спадає як 1/(r+R_б) — гіпербола, що швидко осідає."""
    W, H = 720, 400
    parts = []
    # осі
    ox, oy = 110, 320          # початок координат
    aw, ah = 540, 250          # довжина осей
    parts.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=2))         # X: R_б
    parts.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=2))         # Y: |ΔI|
    parts.append(text(ox + aw, oy + 24, "R_б (опір баласту)", size=13, color=INK, anchor="end"))
    parts.append(text(ox - 14, oy - ah + 4, "перекіс |ΔI|", size=13, color=INK, anchor="end"))

    # крива |ΔI| = Δε / (r + R_б);  візьмемо Δε=1 (умовно), r мале
    r = 0.05
    Rmax = 0.6
    import math
    pts = []
    N = 120
    top = ah - 20             # піксельна висота кривої при R_б=0
    # масштаб: при R_б=0 значення 1/r; нормуємо так, щоб воно лягло на top
    base = 1.0 / r
    for i in range(N + 1):
        Rb = Rmax * i / N
        val = 1.0 / (r + Rb)
        px = ox + aw * (Rb / Rmax)
        py = oy - top * (val / base)
        pts.append((px, py))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # позначка «без баласту» — висока точка
    parts.append(circle(pts[0][0], pts[0][1], 5, fill=POS, stroke=POS))
    parts.append(text(ox + 8, pts[0][1] - 8, "без баласту: великий перекіс", size=12, color=POS, anchor="start", bold=True))

    # пунктир до точки R_б ≈ 4r (де знаменник у 5 разів більший)
    Rb_sel = 4 * r
    val_sel = 1.0 / (r + Rb_sel)
    sx = ox + aw * (Rb_sel / Rmax)
    sy = oy - top * (val_sel / base)
    parts.append(line(sx, oy, sx, sy, color=MUTED, sw=1, dash="4 4"))
    parts.append(line(ox, sy, sx, sy, color=MUTED, sw=1, dash="4 4"))
    parts.append(circle(sx, sy, 5, fill=FIELD, stroke=FIELD))
    parts.append(text(sx + 10, sy + 4, "R_б = 4r → перекіс уп'ятеро менший", size=12, color=FIELD, anchor="start", bold=True))

    # формула чутливості
    parts.append(fitbox(ox + aw - 250, oy - ah - 6, 250, 40,
                        "dI/dε = 1/(r + R_б)",
                        size=15, fill="#fdecea", stroke=POS, color=POS, bold=True))
    return render(os.path.join(OUT, 'sensitivity.svg'), W, H, *parts,
                  title="Баласт збільшує знаменник — і гасить перекіс струму")


# ── 5. Компроміс: рівність поліпшується, втрати ростуть ──────────────────────
def fig_tradeoff():
    """Дві протилежні криві: перекіс ↓, втрати P=I²R_б ↑ — між ними «золота» зона."""
    W, H = 720, 410
    parts = []
    ox, oy = 110, 320
    aw, ah = 520, 250
    parts.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=2))
    parts.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=2))
    parts.append(text(ox + aw, oy + 24, "R_б →", size=13, color=INK, anchor="end"))

    import math
    r = 0.05
    Rmax = 0.6
    N = 120
    top = ah - 30
    base_skew = 1.0 / r
    pts_skew, pts_loss = [], []
    for i in range(N + 1):
        Rb = Rmax * i / N
        px = ox + aw * (Rb / Rmax)
        skew = 1.0 / (r + Rb)                  # перекіс ~ спадна
        py_s = oy - top * (skew / base_skew)
        pts_skew.append((px, py_s))
        loss = Rb                              # P = I²·R_б ~ зростає лінійно (I≈const)
        py_l = oy - top * (loss / Rmax)
        pts_loss.append((px, py_l))
    ds = "M %.1f %.1f " % pts_skew[0] + " ".join("L %.1f %.1f" % p for p in pts_skew[1:])
    dl = "M %.1f %.1f " % pts_loss[0] + " ".join("L %.1f %.1f" % p for p in pts_loss[1:])
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ds, POS))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dl, NEG))

    parts.append(text(ox + 150, pts_skew[30][1] - 12, "перекіс струму (хочемо ↓)", size=12, color=POS, anchor="start", bold=True))
    parts.append(text(ox + 250, pts_loss[95][1] - 10, "втрати I²R_б (хочемо ↓)", size=12, color=NEG, anchor="start", bold=True))

    # «золота» зона — там, де перекіс уже малий, а втрати ще терпимі
    gx1 = ox + aw * (3 * r / Rmax)
    gx2 = ox + aw * (8 * r / Rmax)
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" opacity="0.12"/>'
                 % (gx1, oy - ah, gx2 - gx1, ah))
    parts.append(text((gx1 + gx2) / 2, oy - ah - 8, "розумний R_б", size=13, color=FIELD, bold=True))
    parts.append(text((gx1 + gx2) / 2, oy - ah + 12, "(кілька r)", size=11, color=FIELD))

    parts.append(fitbox(ox + 30, oy + 42, aw - 60, 34,
                        "Бери R_б якнайменшим, аби лиш приборкати перекіс",
                        size=14, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'tradeoff.svg'), W, H, *parts,
                  title="Вибір R_б: рівність поділу проти втрат потужності")


# ── 6. Перенесення на емітерні/стокові резистори ────────────────────────────
def fig_emitter_ballast():
    """Два паралельні транзистори з R_E: місцевий зворотний зв'язок вирівнює струми."""
    W, H = 720, 380
    parts = []
    rail_y = 70
    base_y = 200
    re_y = 280
    sink_y = 340
    qx = [240, 480]            # два транзистори
    labels = ["Q1 (гарячіший)", "Q2"]
    cols = [POS, NEG]

    # верхня шина (колектор/сток, спільна)
    parts.append(line(150, rail_y, 600, rail_y, color=LINE, sw=2.5))
    parts.append(text(150, rail_y - 10, "спільний колектор / +V", size=12, color=MUTED, anchor="start"))
    # спільна база/затвор
    parts.append(line(150, base_y, 600, base_y, color=LINE, sw=2))
    parts.append(text(150, base_y - 8, "спільна база / затвор", size=12, color=MUTED, anchor="start"))

    for x, lab, c in zip(qx, labels, cols):
        # транзистор — кружок-символ
        parts.append(circle(x, (rail_y + base_y) / 2 + 10, 26, fill="#f4f6f8", stroke=c, sw=2.4))
        parts.append(text(x, (rail_y + base_y) / 2 + 15, "Q", size=15, color=c, bold=True))
        # колектор угору
        parts.append(line(x, rail_y, x, (rail_y + base_y) / 2 - 16, color=c, sw=2.2))
        # база — від спільної шини
        parts.append(line(x - 40, base_y, x - 26, (rail_y + base_y) / 2 + 10, color=LINE, sw=1.8))
        # емітер униз до R_E
        parts.append(line(x, (rail_y + base_y) / 2 + 36, x, re_y, color=c, sw=2.2))
        # R_E
        b, bw, bh = textbox(x, re_y + 22, "R_E", size=13, pad=8, bold=True,
                            fill="#fff8e1", stroke="#d9a400")
        parts.append(b)
        parts.append(line(x, re_y + 22 + bh / 2, x, sink_y, color=c, sw=2.2))
        parts.append(text(x, (rail_y + base_y) / 2 + 56, lab, size=11, color=c, bold=True))

    # спільний емітерний вузол (земля/навантаження)
    parts.append(line(qx[0], sink_y, qx[1], sink_y, color=LINE, sw=2.5))
    parts.append(text((qx[0] + qx[1]) / 2, sink_y + 20, "спільний емітер / навантаження", size=12, color=MUTED))

    # ідея зворотного зв'язку — підпис біля Q1
    parts.append(fitbox(548, re_y - 36, 162, 86,
                        "Q1 бере більше струму\n→ більший спад I·R_E\n→ менша напруга на\nпереході → струм осідає",
                        size=11, fill="#fdecea", stroke=POS, color=POS))
    parts.append(fitbox(150, sink_y - 96, 200, 40,
                        "ΔI_перекосу ≈ ΔV_BE / R_E",
                        size=14, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    return render(os.path.join(OUT, 'emitter-ballast.svg'), W, H, *parts,
                  title="Емітерні резистори: місцевий зворотний зв'язок ділить струм")


def diode_symbol(cx, cy, color, sw=2.4, s=14):
    """Символ діода: трикутник вістрям праворуч + катодна риска. Струм тече зліва направо."""
    parts = []
    parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (cx - s, cy - s, cx - s, cy + s, cx + s, cy, color, sw))
    parts.append(line(cx + s, cy - s, cx + s, cy + s, color=color, sw=sw))   # катодна риска
    return "".join(parts)


# ── 7. Гілка діодного АБО у трьох виконаннях (вставка comp-diode-or) ─────────
def fig_diode_or():
    W, H = 760, 420
    parts = []
    rows = [120, 230, 340]
    titles = ["Звичайний діод", "Шотткі", "Активний ідеальний діод"]
    drops = ["спад ≈ 0.7 В", "спад ≈ 0.4 В", "спад ≈ десятки мВ"]
    cols = ["#c0392b", "#d9a400", FIELD]
    sx = 150          # вхід (джерело)
    cx_dev = 380      # клапан
    bx = 600          # спільна шина

    # спільна шина праворуч (вертикаль) + навантаження
    parts.append(line(bx, rows[0] - 22, bx, rows[2] + 22, color=INK, sw=3))
    parts.append(text(bx + 12, rows[0] - 30, "спільна", size=12, color=MUTED, anchor="start"))
    parts.append(text(bx + 12, rows[0] - 16, "шина", size=12, color=MUTED, anchor="start"))
    parts.append(rect(bx + 40, (rows[0] + rows[2]) / 2 - 28, 92, 56, fill="#eafaf0", stroke=FIELD, sw=2))
    parts.append(text(bx + 86, (rows[0] + rows[2]) / 2 + 5, "наван-", size=12, color=FIELD, bold=True))
    parts.append(line(bx, (rows[0] + rows[2]) / 2, bx + 40, (rows[0] + rows[2]) / 2, color=INK, sw=3))

    for y, t, d, c in zip(rows, titles, drops, cols):
        # вхід-джерело
        parts.append(text(sx - 6, y + 4, "вхід", size=12, color=c, anchor="end", bold=True))
        parts.append(line(sx, y, cx_dev - 30, y, color=LINE, sw=2))
        parts.append(arrow(sx + 10, y, sx + 78, y, color=c, sw=2.6))
        # клапан
        if y == rows[2]:
            parts.append(rect(cx_dev - 30, y - 18, 60, 36, fill="#eafaf0", stroke=c, sw=2.4))
            parts.append(text(cx_dev, y + 4, "MOSFET", size=11, color=c, bold=True))
        else:
            parts.append(diode_symbol(cx_dev, y, c))
        parts.append(line(cx_dev + 30, y, bx, y, color=LINE, sw=2))
        # підпис ряду
        parts.append(text(cx_dev, y - 30, t, size=13, color=c, bold=True))
        parts.append(text(cx_dev, y + 36, d, size=12, color=c))

    # нижня плашка-висновок
    parts.append(fitbox(W * 0.5 - 305, H - 50, 610, 36,
                        "Усі троє: струм лише У шину (→), зворотний блокують. Різниця — у прямому спаді.",
                        size=13, fill="#f4f6f8", stroke=LINE, color=INK))
    return render(os.path.join(OUT, 'diode-or.svg'), W, H, *parts,
                  title="Діодне АБО: одна гілка у трьох поколіннях клапана")


if __name__ == '__main__':
    fig_two_sources()
    fig_circulating()
    fig_cures()
    fig_sensitivity()
    fig_tradeoff()
    fig_emitter_ballast()
    fig_diode_or()
    print('figs done')
