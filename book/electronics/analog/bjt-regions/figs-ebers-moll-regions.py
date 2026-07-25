# -*- coding: utf-8 -*-
"""Фігури до математичної вставки «Модель Еберса–Молла» (math-ebers-moll.md).
Запуск:  python figs-math-ebers-moll.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def diode(x1, y1, x2, y2, sw=2.0, color=INK, flip=False):
    """Символ діода вздовж відрізка (x1,y1)->(x2,y2), трикутник вказує напрям провідності.
    Тільки горизонтальні/вертикальні відрізки. flip=True перевертає трикутник."""
    out = []
    s = 9
    if abs(y2 - y1) < 1:                     # горизонтальний
        mx = (x1 + x2) / 2
        d = 1 if (x2 > x1) != flip else -1
        out.append(line(x1, y1, mx - d * s, y1, color=color, sw=sw))
        out.append(line(mx + d * s, y1, x2, y1, color=color, sw=sw))
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="%.1f"/>'
                   % (mx - d * s, y1 - s, mx - d * s, y1 + s, mx + d * s, y1, color, sw))
        out.append(line(mx + d * s, y1 - s - 1, mx + d * s, y1 + s + 1, color=color, sw=sw + 0.4))  # планка катода
    else:                                     # вертикальний
        my = (y1 + y2) / 2
        d = 1 if (y2 > y1) != flip else -1
        out.append(line(x1, y1, x1, my - d * s, color=color, sw=sw))
        out.append(line(x1, my + d * s, x1, y2, color=color, sw=sw))
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" stroke-width="%.1f"/>'
                   % (x1 - s, my - d * s, x1 + s, my - d * s, x1, my + d * s, color, sw))
        out.append(line(x1 - s - 1, my + d * s, x1 + s + 1, my + d * s, color=color, sw=sw + 0.4))
    return "".join(out)


def cur_source(cx, cy, r=17, color=INK):
    """Символ джерела струму — коло з двома дотичними стрілками (ромбик усередині)."""
    out = [circle(cx, cy, r, fill=BG, stroke=color, sw=1.8)]
    out.append(line(cx, cy - r + 4, cx, cy + r - 4, color=color, sw=1.6))
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
               % (cx - 4, cy - r + 9, cx, cy - r + 4, cx + 4, cy - r + 9, color))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Ядро моделі: два зустрічні діоди зі спільною базою + керовані джерела αF·I, αR·I
# ─────────────────────────────────────────────────────────────────────────────
def fig_model():
    W, H = 780, 430
    f = [text(W / 2, 28, "Модель Еберса–Молла: два зустрічні діоди зі спільним керуванням (NPN)",
              size=15, bold=True)]

    ex, cx = 120, 660          # емітерний і колекторний вивід
    bx = 390                   # база (посередині)
    mid_y = 190                # рівень діодів
    b_y = 330                  # рівень бази

    # вузол-база (спільна точка обох переходів)
    f.append(circle(bx, mid_y, 4, fill=INK, stroke=INK))
    f.append(line(bx, mid_y, bx, b_y, color=INK, sw=1.8))
    f.append(line(bx - 26, b_y, bx + 26, b_y, color=INK, sw=1.8))
    f.append(text(bx, b_y + 22, "B (база)", size=12, bold=True))
    f.append(text(bx, b_y + 40, "спільний керувальний вузол", size=10, color=MUTED))

    # ── лівий перехід: база–емітер (діод IES), провідність від бази до емітера при прямому зсуві ──
    f.append(diode(bx - 20, mid_y, ex + 40, mid_y, color=NEG))
    f.append(line(ex, mid_y, ex + 40, mid_y, color=INK, sw=1.8))
    f.append(circle(ex, mid_y, 4, fill=INK, stroke=INK))
    f.append(line(ex, mid_y, ex, mid_y + 70, color=INK, sw=1.8))
    f.append(text(ex, mid_y + 92, "E (емітер)", size=12, bold=True))
    f.append(text((bx - 20 + ex + 40) / 2, mid_y - 16, "перехід Б–Е", size=11, color=NEG))
    f.append(text((bx - 20 + ex + 40) / 2, mid_y - 32, "діод I_ES", size=10, color=MUTED))

    # ── правий перехід: база–колектор (діод ICS) ──
    f.append(diode(bx + 20, mid_y, cx - 40, mid_y, color=POS))
    f.append(line(cx - 40, mid_y, cx, mid_y, color=INK, sw=1.8))
    f.append(circle(cx, mid_y, 4, fill=INK, stroke=INK))
    f.append(line(cx, mid_y, cx, mid_y + 70, color=INK, sw=1.8))
    f.append(text(cx, mid_y + 92, "C (колектор)", size=12, bold=True))
    f.append(text((bx + 20 + cx - 40) / 2, mid_y - 16, "перехід Б–К", size=11, color=POS))
    f.append(text((bx + 20 + cx - 40) / 2, mid_y - 32, "діод I_CS", size=10, color=MUTED))

    # ── керовані джерела: перенесення αF струму Б–Е у колектор і αR — назад в емітер ──
    src_y = mid_y - 78
    f.append(cur_source(cx - 90, src_y, color=POS))
    f.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (ex + 90, mid_y - 6, (ex + cx) / 2, src_y - 34, cx - 90 - 20, src_y, POS))
    f.append(text(cx - 90, src_y - 26, "αF · I_F", size=11, color=POS, bold=True))
    f.append(text(cx - 90, src_y - 42, "перенесення в колектор", size=9, color=MUTED))

    f.append(cur_source(ex + 90, src_y + 130, color=NEG))
    f.append(text(ex + 90, src_y + 130 + 34, "αR · I_R", size=11, color=NEG, bold=True))
    f.append(text(ex + 90, src_y + 130 + 50, "зворотне перенесення", size=9, color=MUTED))

    # підпис-суть унизу
    note = ("Кожен перехід — звичайний діод (I_F на Б–Е, I_R на Б–К). Але вони НЕ незалежні:\n"
            "частка αF прямого струму «протікає» в колектор, частка αR зворотного — назад в емітер.\n"
            "Це зв'язування двох діодів і робить транзистор транзистором, а не парою окремих діодів.")
    f.append(fitbox(90, 372, 600, 50, note, size=11, fill="#f4f6f8", stroke=MUTED, color=INK))

    render(os.path.join(IMG, "em-model.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Чотири режими як 2×2 карта станів двох переходів
# ─────────────────────────────────────────────────────────────────────────────
def fig_regions():
    W, H = 760, 470
    f = [text(W / 2, 28, "Чотири режими = чотири комбінації станів двох переходів",
              size=15, bold=True)]

    # осі підписів
    gx, gy = 210, 90           # верхній лівий кут сітки
    cw, ch = 250, 150          # клітинка
    f.append(text(gx + cw / 2, gy - 22, "перехід Б–Е закритий", size=12, color=NEG, bold=True))
    f.append(text(gx + cw + cw / 2, gy - 22, "перехід Б–Е відкритий", size=12, color=POS, bold=True))
    f.append(text(gx - 16, gy + ch / 2, "Б–К", size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(gx - 16, gy + ch / 2 + 16, "закритий", size=11, color=NEG, anchor="end"))
    f.append(text(gx - 16, gy + ch + ch / 2, "Б–К", size=12, color=POS, bold=True, anchor="end"))
    f.append(text(gx - 16, gy + ch + ch / 2 + 16, "відкритий", size=11, color=POS, anchor="end"))

    cells = [
        # (col, row, назва, колір-рамки, заливка, рядки)
        (0, 0, "ВІДСІЧКА", MUTED, "#f4f6f8",
         ["обидва закриті", "Ic ≈ 0, кран перекрито", "ключ РОЗІМКНЕНО"]),
        (1, 0, "АКТИВНИЙ", FIELD, "#eef7f0",
         ["Б–Е відкр., Б–К закр.", "Ic ≈ βF · Ib", "підсилювач / лінійна зона"]),
        (0, 1, "ІНВЕРСНИЙ", MUTED, "#f4f6f8",
         ["ролі E й C помінялись", "працює αR (мале!)", "на практиці уникають"]),
        (1, 1, "НАСИЧЕННЯ", POS, "#fdecea",
         ["обидва ВІДКРИТІ", "Vce(sat) мала", "ключ ЗАМКНЕНО"]),
    ]
    for col, row, name, col_stroke, fill, rows in cells:
        x = gx + col * cw
        y = gy + row * ch
        f.append(rect(x, y, cw - 12, ch - 12, fill=fill, stroke=col_stroke, sw=2.0, rx=8))
        f.append(text(x + (cw - 12) / 2, y + 30, name, size=15, bold=True, color=col_stroke if col_stroke != MUTED else INK))
        for i, r in enumerate(rows):
            f.append(text(x + (cw - 12) / 2, y + 58 + i * 22, r, size=11, color=INK))

    note = ("Транзистор — не «один прилад із режимами», а ДВА переходи, кожен просто відкритий чи закритий.\n"
            "Режим — це лише яка з чотирьох комбінацій зараз. Ключ живе по діагоналі: відсічка ↔ насичення.")
    f.append(fitbox(90, gy + 2 * ch + 18, 580, 46, note, size=11, fill="#f4f6f8", stroke=MUTED, color=INK))

    render(os.path.join(IMG, "em-regions.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Vce(sat) від коефіцієнта перезаливу: спадна віддача + доданок rc·Ic на струмі
# ─────────────────────────────────────────────────────────────────────────────
def fig_vcesat():
    import math
    W, H = 780, 460
    f = [text(W / 2, 28, "Vce(sat) від глибини насичення: спадна віддача + внесок опору тіла",
              size=15, bold=True)]

    ox, oy = 100, 380
    ax_w, ax_h = 600, 300
    f.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w - 4, oy + 28, "коефіцієнт перезаливу ODF →", size=12, anchor="end"))
    f.append(text(ox - 8, oy - ax_h + 4, "Vce(sat)", size=12, anchor="end"))

    # осьові позначки ODF
    for i, odf in enumerate([1, 2, 5, 10, 20]):
        xx = ox + (ax_w - 40) * (math.log(odf) / math.log(20))
        f.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.4))
        f.append(text(xx, oy + 20, str(odf), size=10, color=MUTED))

    def y_of(v, vmax=0.55):
        return oy - (ax_h - 30) * (v / vmax)

    # крива 1: «ідеальна» логарифмічна складова Vce = VT ln(...) — падає й кладеться
    pts = []
    for k in range(0, 201):
        odf = 1 + (20 - 1) * (k / 200.0)
        xx = ox + (ax_w - 40) * (math.log(odf) / math.log(20))
        # логарифмічна складова: спадає з ODF, кладеться
        v_log = 0.026 * math.log((1 + 0.0) )  # placeholder, замінюємо нижче
        v_log = 0.30 * (math.log(21 - odf + 1) / math.log(21))  # монотонно спадна, кладеться
        pts.append((xx, y_of(v_log)))
    d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, FIELD))
    f.append(text(pts[70][0] + 6, pts[70][1] - 10, "логарифмічна складова VT·ln(…)", size=11, color=FIELD, anchor="start"))
    f.append(text(pts[150][0], pts[150][1] - 10, "спадна віддача →", size=10, color=MUTED, anchor="start"))

    # крива 2: повна Vce(sat) = логарифм + rc·Ic (сталий доданок на даному струмі підіймає підлогу)
    floor = 0.10                      # rc·Ic — сталий доданок на фіксованому Ic
    pts2 = []
    for k in range(0, 201):
        odf = 1 + (20 - 1) * (k / 200.0)
        xx = ox + (ax_w - 40) * (math.log(odf) / math.log(20))
        v_log = 0.30 * (math.log(21 - odf + 1) / math.log(21))
        pts2.append((xx, y_of(v_log + floor)))
    d2 = "M " + " L ".join("%.1f %.1f" % p for p in pts2)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d2, POS))
    f.append(text(pts2[40][0] + 6, pts2[40][1] - 8, "повна Vce(sat) = VT·ln(…) + rc·Ic", size=11, color=POS, anchor="start"))

    # лінія «підлоги» rc·Ic
    yf = y_of(floor)
    f.append(line(ox, yf, ox + ax_w - 30, yf, color=MUTED, sw=1.3, dash="5 4"))
    f.append(text(ox + ax_w - 34, yf - 6, "підлога rc·Ic (росте зі струмом)", size=10, color=MUTED, anchor="end"))

    # позначки режимів по ODF
    x1 = ox + (ax_w - 40) * (math.log(1) / math.log(20))
    f.append(text(x1 + 8, oy - ax_h + 24, "ODF≈1: край насичення,", size=10, color=INK, anchor="start"))
    f.append(text(x1 + 8, oy - ax_h + 40, "Vce ще велика", size=10, color=INK, anchor="start"))
    xg = ox + (ax_w - 40) * (math.log(8) / math.log(20))
    f.append(line(xg, oy, xg, oy - ax_h + 50, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(xg + 6, oy - ax_h + 66, "ODF 3…10: глибоке", size=10, color=MUTED, anchor="start"))
    f.append(text(xg + 6, oy - ax_h + 82, "насичення (робоча зона)", size=10, color=MUTED, anchor="start"))

    note = ("Перший десяток відсотків перезаливу прибирає більшість напруги — далі крива кладеться (зелена).\n"
            "Опір тіла колектора rc додає СТАЛИЙ на даному струмі доданок rc·Ic — він і не дає Vce(sat) впасти в нуль,\n"
            "і на великому Ic починає домінувати. Ось чому даташит дає Vce(sat) ЗАВЖДИ при конкретному Ic.")
    f.append(fitbox(90, 402, 600, 50, note, size=10.5, fill="#f4f6f8", stroke=MUTED, color=INK))

    render(os.path.join(IMG, "em-vcesat-odf.svg"), W, H, *f)


if __name__ == "__main__":
    fig_model()
    fig_regions()
    fig_vcesat()
    print("OK: em-model.svg, em-regions.svg, em-vcesat-odf.svg")
