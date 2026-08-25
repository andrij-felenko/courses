# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

WARM = "#e67e22"   # тепла заливка


def res_zig(x1, y, x2, color=INK, sw=2.2, n=6, amp=7):
    """Зиґзаґ-резистор між (x1,y) і (x2,y) — символ теплового/електричного опору."""
    seg = (x2 - x1) / (n + 1)
    pts = ["%.1f,%.1f" % (x1, y), "%.1f,%.1f" % (x1 + seg / 2, y)]
    for i in range(n):
        yy = y - amp if i % 2 == 0 else y + amp
        pts.append("%.1f,%.1f" % (x1 + seg / 2 + seg * (i + 0.5), yy))
    pts.append("%.1f,%.1f" % (x2 - seg / 2, y))
    pts.append("%.1f,%.1f" % (x2, y))
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (" ".join(pts), color, sw)


def cap_sym(cx, y1, y2, color=INK, sw=2.2, w=22):
    """Конденсатор (дві пластини) вертикально від y1 (провід) до заземлення y2."""
    ymid = (y1 + y2) / 2
    out = [line(cx, y1, cx, ymid - 5, color=color, sw=sw)]
    out.append(line(cx - w / 2, ymid - 5, cx + w / 2, ymid - 5, color=color, sw=sw + 0.6))
    out.append(line(cx - w / 2, ymid + 5, cx + w / 2, ymid + 5, color=color, sw=sw + 0.6))
    out.append(line(cx, ymid + 5, cx, y2, color=color, sw=sw))
    return "".join(out)


def ground(cx, y, color=INK):
    out = [line(cx, y, cx, y + 8, color=color, sw=2)]
    for i, ww in enumerate((22, 14, 6)):
        out.append(line(cx - ww / 2, y + 8 + i * 5, cx + ww / 2, y + 8 + i * 5, color=color, sw=2))
    return "".join(out)


# ── Фігура 1: теплова RC-модель ↔ електрична RC ─────────────────────────────
def fig_thermal_rc():
    W, H = 780, 400
    frags = [text(W / 2, 28, "Батарея як теплове RC-коло: та сама математика, інші одиниці", size=16, bold=True)]

    def panel(ox, title, accent, labels):
        pw, ph = 350, 300
        oy = 54
        frags.append(rect(ox, oy, pw, ph, fill=BG, stroke=MUTED, sw=1.4, rx=10))
        frags.append(text(ox + pw / 2, oy + 24, title, size=13.5, bold=True, color=accent))

        src_x = ox + 58
        node_y = oy + 96
        res_y = node_y
        node_x = ox + 150
        amb_y = oy + 232

        # джерело (струм/потужність) — коло зі стрілкою вгору
        frags.append(circle(src_x, (node_y + amb_y) / 2, 26, fill="#fff7ed", stroke=accent, sw=2))
        frags.append(arrow(src_x, (node_y + amb_y) / 2 + 14, src_x, (node_y + amb_y) / 2 - 14, color=accent, sw=2.2))
        frags.append(mtext(src_x, oy + ph - 26, labels['src'].split("\n"), size=10.5, color=accent, bold=True))

        # провід угору від джерела до вузла
        frags.append(line(src_x, (node_y + amb_y) / 2 - 26, src_x, node_y, color=INK, sw=2))
        frags.append(line(src_x, node_y, node_x, node_y, color=INK, sw=2))
        frags.append(circle(node_x, node_y, 3.2, fill=INK, stroke=INK, sw=1))

        # опір праворуч від вузла до «амбієнта»
        frags.append(res_zig(node_x, node_y, node_x + 120, color=accent, sw=2.4))
        frags.append(text(node_x + 60, node_y - 16, labels['res'], size=11, color=accent, bold=True))
        frags.append(line(node_x + 120, node_y, node_x + 120, amb_y, color=INK, sw=2))

        # ємність від вузла вниз до амбієнта
        frags.append(cap_sym(node_x, node_y, amb_y - 4, color=accent, sw=2.2))
        frags.append(text(node_x + 40, (node_y + amb_y) / 2 + 4, labels['cap'], size=11, color=accent, bold=True, anchor="start"))

        # нижня шина «амбієнт»
        frags.append(line(src_x, (node_y + amb_y) / 2 + 26, src_x, amb_y, color=INK, sw=2))
        frags.append(line(src_x, amb_y, node_x + 120, amb_y, color=INK, sw=2))
        frags.append(ground((src_x + node_x + 120) / 2, amb_y, color=MUTED))
        frags.append(text((src_x + node_x + 120) / 2, amb_y + 34, labels['gnd'], size=10.5, color=MUTED, italic=True))

    panel(24, "Теплова модель батареї", WARM, {
        'src': "P = I²·R\nтепловий\nпотік [Вт]",
        'res': "Rθ [°C/Вт]",
        'cap': "Cθ [Дж/°C]",
        'gnd': "температура довкілля Tₐ",
    })
    panel(W - 24 - 350, "Електричне RC-коло", NEG, {
        'src': "I\nструм\n[А]",
        'res': "R [Ом]",
        'cap': "C [Ф]",
        'gnd': "опорна напруга",
    })

    # знак відповідності
    frags.append(text(W / 2, 210, "≡", size=40, color=MUTED, bold=True))
    render(os.path.join(IMG, 'thermal-rc.svg'), W, H, *frags)


# ── Фігура 2: експоненційний вихід на усталену температуру, стала часу τ ─────
def fig_time_constant():
    W, H = 760, 400
    frags = [text(W / 2, 26, "Розігрів — це заряд теплової ємності: T(t) виходить на плато за сталу часу τ", size=15, bold=True)]

    L, R = 78, W - 40
    T, B = 58, 320
    Ta = B - 30          # рівень довкілля
    Tss = T + 40         # усталений перегрів
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(line(L, T - 6, L, B, color=INK, sw=2))
    frags.append(arrow(R - 2, B, R + 10, B, color=INK, sw=2))
    frags.append(text(R + 6, B + 22, "час", size=11, color=MUTED, italic=True, anchor="end"))
    frags.append(text(L - 8, T + 2, "T", size=13, color=INK, anchor="end", bold=True))

    # довкілля й усталений рівень
    frags.append(line(L, Ta, R, Ta, color=MUTED, sw=1.4, dash="5,4"))
    frags.append(text(R - 4, Ta - 6, "Tₐ  (довкілля)", size=11, color=MUTED, anchor="end", italic=True))
    frags.append(line(L, Tss, R, Tss, color=WARM, sw=1.4, dash="5,4"))
    frags.append(text(R - 4, Tss - 7, "Tₐ + P·Rθ  (усталений перегрів)", size=11, color=WARM, anchor="end", bold=True))

    # крива насичення T(t) = Tss - (Tss-Ta)·e^(-t/τ)
    span = R - L
    tau_px = span * 0.28
    pts = []
    for i in range(0, 201):
        x = L + span * i / 200.0
        tt = (x - L) / tau_px
        y = Tss + (Ta - Tss) * math.exp(-tt)
        pts.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), POS))

    # позначка τ: на t=τ пройдено 63% шляху
    xtau = L + tau_px
    y63 = Tss + (Ta - Tss) * math.exp(-1)
    frags.append(line(xtau, B, xtau, y63, color=NEG, sw=1.4, dash="4,3"))
    frags.append(line(L, y63, xtau, y63, color=NEG, sw=1.4, dash="4,3"))
    frags.append(circle(xtau, y63, 4, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(xtau, B + 20, "τ = Rθ·Cθ", size=12, color=NEG, bold=True))
    frags.append(text(L + 6, y63 - 8, "63% перегріву", size=10.5, color=NEG, anchor="start"))

    # дотична на старті → нахил P/Cθ
    frags.append(text(L + 30, Ta - 12, "нахил на старті = P/Cθ", size=10.5, color=INK, anchor="start", italic=True))
    frags.append(line(L, Ta, L + tau_px, Tss, color=INK, sw=1.2, dash="2,3"))

    render(os.path.join(IMG, 'time-constant.svg'), W, H, *frags)


# ── Фігура 3: два джерела тепла — I²R (незворотне) і ентропійне (зворотне) ────
def fig_heat_sources():
    W, H = 760, 380
    frags = [text(W / 2, 26, "Скільки тепла: незворотне I²R (завжди грає) і ентропійне (може й холодити)", size=14.5, bold=True)]

    L, R = 70, W - 250
    T, B = 60, 300
    frags.append(line(L, B, R, B, color=INK, sw=2))
    frags.append(line(L, T - 6, L, B, color=INK, sw=2))
    frags.append(arrow(R - 2, B, R + 10, B, color=INK, sw=2))
    frags.append(text(R + 8, B + 20, "струм I", size=11, color=MUTED, italic=True, anchor="end"))
    frags.append(text(L - 8, T + 4, "P", size=13, color=INK, anchor="end", bold=True))
    frags.append(line(L - 4, (T + B) / 2, R, (T + B) / 2, color=MUTED, sw=1, dash="4,3"))
    frags.append(text(L + 4, (T + B) / 2 - 5, "0", size=10, color=MUTED, anchor="start"))

    span = R - L
    # I²R — парабола (завжди додатна)
    pts = []
    for i in range(0, 121):
        x = L + span * i / 120.0
        frac = i / 120.0
        y = (T + B) / 2 - (frac ** 2) * ((B - T) / 2 - 14)
        pts.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), POS))
    frags.append(text(R - 10, T + 26, "I²·R  (незворотне, тільки гріє)", size=11.5, color=POS, bold=True, anchor="end"))

    # ентропійне — майже лінійне, може бути й від'ємне (нижче нуля)
    pts2 = []
    for i in range(0, 121):
        x = L + span * i / 120.0
        frac = i / 120.0
        y = (T + B) / 2 + frac * 40   # трохи нижче нуля → охолодження
        pts2.append("%.1f,%.1f" % (x, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="6,4"/>' % (" ".join(pts2), NEG))
    frags.append(text(R - 10, (T + B) / 2 + 54, "ентропійне  (±, знак від хімії й напряму)", size=11, color=NEG, anchor="end"))

    # пояснювальна колонка праворуч
    bx = R + 24
    frags.append(fitbox(bx, 66, 200, 92,
                        "I²·R\nзавжди > 0, росте\nяк КВАДРАТ струму.\nПодвоїв струм —\nучетверо більше тепла.",
                        size=11, fill="#fdecea", stroke=POS, sw=1.4, rx=8, color="#7a271a"))
    frags.append(fitbox(bx, 172, 200, 96,
                        "ентропійне\n= I·T·(dUocv/dT).\nЛінійне по I, знак\nміняється — при розряді\nчасто гріє, при заряді\nбуває й холодить.",
                        size=10.5, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=8, color="#1e3a8a"))
    frags.append(text(bx + 100, 292, "на великому струмі\nкерує I²·R", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'heat-sources.svg'), W, H, *frags)


# ── Фігура 4: чому центральна комірка найгарячіша + позитивний зв'язок ───────
def fig_pack_gradient():
    W, H = 780, 380
    frags = [text(W / 2, 26, "У пакеті внутрішня комірка найгарячіша, а нагрів сам себе підганяє", size=15, bold=True)]

    # ЛІВА: розріз пакета 3×3, температурна мапа
    ox, oy = 40, 60
    cell = 52
    gap = 8
    frags.append(text(ox + (3 * cell + 2 * gap) / 2, oy + 6, "розріз пакета (вид згори)", size=12, bold=True, color=INK))
    # температура за «манхеттенською» відстанню від центру
    heat_col = {0: ("#c0392b", "#ffffff"), 1: ("#e67e22", "#ffffff"), 2: ("#f1c40f", INK)}
    for r in range(3):
        for c in range(3):
            x = ox + c * (cell + gap)
            y = oy + 18 + r * (cell + gap)
            d = abs(r - 1) + abs(c - 1)  # 0 центр, 1 бік, 2 кут
            fill, tc = heat_col[d]
            frags.append(circle(x + cell / 2, y + cell / 2, cell / 2, fill=fill, stroke=INK, sw=1.6))
            if d == 0:
                frags.append(text(x + cell / 2, y + cell / 2 + 4, "гаряче", size=10, color=tc, bold=True))
    # легенда
    ly = oy + 18 + 3 * (cell + gap) + 18
    for i, (d, lab) in enumerate([(0, "центр: тепло нікуди не тікає"),
                                  (1, "бік: один шлях назовні"),
                                  (2, "кут: два шляхи, найхолодніший")]):
        fill = heat_col[d][0]
        frags.append(circle(ox + 10, ly + i * 20, 7, fill=fill, stroke=INK, sw=1.2))
        frags.append(text(ox + 24, ly + i * 20 + 4, lab, size=10.5, color=INK, anchor="start"))

    # ПРАВА: петля позитивного зворотного зв'язку
    rx = 430
    frags.append(text(rx + 150, oy + 6, "петля розгону", size=12, bold=True, color=POS))
    cyc = [
        (rx + 150, oy + 40, "температура ↑"),
        (rx + 268, oy + 150, "реакції швидші,\nRвн-струм гріє більше"),
        (rx + 150, oy + 250, "тепловиділення ↑"),
        (rx + 32, oy + 150, "тепло не встигає\nпіти назовні"),
    ]
    cx0, cy0 = rx + 150, oy + 145
    for (cx, cy, lab) in cyc:
        frags.append(fitbox(cx - 82, cy - 26, 164, 52, lab, size=11, fill="#fdecea",
                            stroke=POS, sw=1.5, rx=8, color="#7a271a", bold=True))
    # стрілки по колу
    import math as _m
    seq = [(cyc[0], cyc[1]), (cyc[1], cyc[2]), (cyc[2], cyc[3]), (cyc[3], cyc[0])]
    for (a, b) in seq:
        ax, ay = a[0], a[1]
        bx2, by = b[0], b[1]
        vx, vy = bx2 - ax, by - ay
        d = _m.hypot(vx, vy)
        ux, uy = vx / d, vy / d
        frags.append(arrow(ax + ux * 42, ay + uy * 30, bx2 - ux * 44, by - uy * 30, color=POS, sw=2))
    frags.append(text(cx0, cy0 + 4, "розгін", size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'pack-gradient.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_thermal_rc()
    fig_time_constant()
    fig_heat_sources()
    fig_pack_gradient()
    print("ok")
