# -*- coding: utf-8 -*-
"""Фігури до теми «Реактивний момент».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.4, head=9):
    """Дуга-стрілка від кута a0 до a1 (градуси, 0°=праворуч, проти год.).
    Наконечник — на кінці a1, дотичний до кола."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    # у SVG y вниз → напрям обходу інвертується; sweep=1 малює за годинниковою на екрані
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    # наконечник: дотична в напрямі руху
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign        # похідна (cos, -sin) на екрані
    ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    # дві щоки наконечника
    back = 2.2
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1,
            px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def prop_blades(cx, cy, r, color, sw=6):
    """Схематичний двоблейдовий гвинт як витягнутий еліпс."""
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'fill-opacity="0.30" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy, r, r * 0.20, color, color, sw / 3))


# ── Фігура 1: реактивний момент на одному роторі ────────────────────────────
def fig_single():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Один ротор: гвинт крутиться сюди — корпус відкидає туди",
                  size=16, bold=True))

    cx, cy = W / 2, 185

    # корпус (широке кільце-рама)
    f.append(circle(cx, cy, 118, fill="#fbfcfe", stroke=MUTED, sw=1.6))
    f.append(text(cx, cy - 100, "рама (корпус)", size=12, color=MUTED))

    # вал і гвинт у центрі
    f.append(circle(cx, cy, 16, fill=FILL, stroke=INK, sw=2))
    f.append(prop_blades(cx, cy, 92, POS))

    # момент двигуна на гвинт — проти годинникової (зелений)
    f.append(arc_arrow(cx, cy, 60, 40, 150, color=FIELD, sw=3.2, head=12))
    f.append(text(cx - 92, cy - 44, "M — двигун крутить", size=13, bold=True,
                  color=FIELD, anchor="start"))
    f.append(text(cx - 92, cy - 28, "гвинт (проти год.)", size=12,
                  color=FIELD, anchor="start"))

    # реактивний момент на корпус — за годинниковою (синій), по зовнішньому колу
    f.append(arc_arrow(cx, cy, 118, 220, 330, color=NEG, sw=3.2, head=12))
    f.append(text(cx + 96, cy + 60, "−M — корпус", size=13, bold=True,
                  color=NEG, anchor="end"))
    f.append(text(cx + 96, cy + 76, "рветься назад (за год.)", size=12,
                  color=NEG, anchor="end"))

    # підсумок
    b, w, h = textbox(cx, H - 18, "на гвинт  +M   ⇄   на корпус  −M    (сума = 0)",
                      size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "single-rotor-reaction.svg"), W, H, *f)


# ── Фігура 2: квадрокоптер — два «+», два «−», моменти гасяться ──────────────
def fig_quad():
    W, H = 720, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Квадрокоптер: діагоналі крутяться навхрест — моменти гасяться",
                  size=16, bold=True))

    cx, cy = W / 2, 210
    arm = 118
    # хрест-рама
    off = arm * 0.707
    corners = [(cx - off, cy - off), (cx + off, cy - off),
               (cx + off, cy + off), (cx - off, cy + off)]
    for (px, py) in corners:
        f.append(line(cx, cy, px, py, color=MUTED, sw=6))
    f.append(circle(cx, cy, 20, fill=FILL, stroke=INK, sw=2))
    f.append(text(cx, cy + 5, "▲", size=15, color=INK))          # ніс — угору-ліворуч? лишаємо центр
    # напрям носа
    f.append(text(cx, cy - 150, "ніс", size=12, color=MUTED))

    # ротори: діагональ ↘↖ — CCW (зелений, +M гвинт → −M реакція за год.),
    #         діагональ ↗↙ — CW  (синій)
    # За домовленістю: показуємо НАПРЯМ ОБЕРТАННЯ гвинта в кожному куті
    #  протилежні кути — однаково; сусідні — навпаки.
    spin = [  # (індекс кута, напрям 'ccw'/'cw')
        (0, 'ccw'), (1, 'cw'), (2, 'ccw'), (3, 'cw')
    ]
    for (i, d) in spin:
        px, py = corners[i]
        col = FIELD if d == 'ccw' else NEG
        f.append(prop_blades(px, py, 52, col))
        f.append(circle(px, py, 9, fill=FILL, stroke=INK, sw=1.6))
        if d == 'ccw':
            f.append(arc_arrow(px, py, 34, 30, 200, color=col, sw=2.6, head=9))
        else:
            f.append(arc_arrow(px, py, 34, 200, 30, color=col, sw=2.6, head=9))
        lbl = "проти год." if d == 'ccw' else "за год."
        ly = py - 66 if py < cy else py + 74
        f.append(text(px, ly, lbl, size=11, bold=True, color=col))

    # легенда напрямів реактивного моменту
    f.append(text(cx, H - 44,
                  "гвинт проти год. → реакція на корпус за год.  (і навпаки)",
                  size=12, color=MUTED))
    b, w, h = textbox(cx, H - 16,
                      "два +M  та  два −M  на корпус  →  сума = 0  (не крутить)",
                      size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "quad-yaw-balance.svg"), W, H, *f)


# ── Фігура 3: керований рискання — навмисний дисбаланс моментів ──────────────
def fig_yaw():
    W, H = 720, 300
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Рискання: навмисно розбалансувати моменти", size=16, bold=True))

    # три стани: рівновага / більше «за год.» / поворот корпусу
    xs = [W * 0.20, W * 0.5, W * 0.80]
    cy = 150

    # стан 1 — рівновага
    f.append(text(xs[0], 66, "рівновага", size=13, bold=True))
    f.append(circle(xs[0], cy, 46, fill="#fbfcfe", stroke=MUTED, sw=1.6))
    f.append(arc_arrow(xs[0], cy, 30, 30, 150, color=FIELD, sw=2.4, head=8))
    f.append(arc_arrow(xs[0], cy, 46, 210, 330, color=NEG, sw=2.4, head=8))
    f.append(text(xs[0], cy + 70, "+M = −M", size=12, color=INK))

    # стан 2 — CCW-пара пришвидшена
    f.append(text(xs[1], 66, "прискорити «проти год.»", size=13, bold=True, color=FIELD))
    f.append(circle(xs[1], cy, 46, fill="#fbfcfe", stroke=MUTED, sw=1.6))
    f.append(arc_arrow(xs[1], cy, 30, 20, 200, color=FIELD, sw=3.4, head=11))
    f.append(arc_arrow(xs[1], cy, 46, 220, 320, color=NEG, sw=1.8, head=7))
    f.append(text(xs[1], cy + 70, "надлишок реакції", size=12, color=NEG))

    # стан 3 — корпус повертається
    f.append(text(xs[2], 66, "корпус рискає", size=13, bold=True, color=NEG))
    f.append(circle(xs[2], cy, 46, fill="#fbfcfe", stroke=NEG, sw=2.2))
    f.append(arc_arrow(xs[2], cy, 60, 250, 350, color=NEG, sw=3.6, head=12))
    f.append(text(xs[2], cy + 70, "поворот навколо осі", size=12, color=NEG))

    # стрілки-переходи між станами
    f.append(arrow(xs[0] + 66, cy, xs[1] - 66, cy, color=LINE, sw=1.6))
    f.append(arrow(xs[1] + 66, cy, xs[2] - 66, cy, color=LINE, sw=1.6))
    return render(os.path.join(IMG, "yaw-by-imbalance.svg"), W, H, *f)


# ── Фігура 4: матриця змішувача X-рами — знаки внеску кожного мотора ─────────
def fig_mixer_matrix():
    W, H = 720, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Матриця змішувача X-рами: знак внеску кожного мотора",
                  size=16, bold=True))

    # ── Ліворуч: маленька X-рама, де сидить який мотор і куди крутиться ──
    fx, fy = 128, 210
    arm = 74
    off = arm * 0.707
    # екран: перед = вгору, ніс між m2 (перед-право) і m4 (перед-ліво).
    #   m1 зад-право CCW · m2 перед-право CW · m3 зад-ліво CW · m4 перед-ліво CCW
    layout = [
        (1, fx + off, fy + off, 'ccw'),   # m1 зад-право
        (2, fx + off, fy - off, 'cw'),    # m2 перед-право
        (3, fx - off, fy + off, 'cw'),    # m3 зад-ліво
        (4, fx - off, fy - off, 'ccw'),   # m4 перед-ліво
    ]
    # промені рами
    for (_, px, py, _s) in layout:
        f.append(line(fx, fy, px, py, color=MUTED, sw=5))
    # ніс
    f.append(line(fx, fy, fx, fy - arm - 20, color=INK, sw=2))
    f.append(text(fx, fy - arm - 28, "ніс", size=11, color=MUTED))
    f.append(circle(fx, fy, 13, fill=FILL, stroke=INK, sw=1.8))
    for (n, px, py, s) in layout:
        col = FIELD if s == 'ccw' else NEG
        f.append(prop_blades(px, py, 30, col))
        f.append(circle(px, py, 15, fill=BG, stroke=col, sw=2))
        f.append(text(px, py + 5, "m%d" % n, size=12, bold=True, color=col))
        # крихітна дуга напряму
        if s == 'ccw':
            f.append(arc_arrow(px, py, 22, 40, 180, color=col, sw=1.8, head=6))
        else:
            f.append(arc_arrow(px, py, 22, 180, 40, color=col, sw=1.8, head=6))
    f.append(text(fx, fy + arm + 40, "зелений — проти год. (CCW)", size=10, color=FIELD))
    f.append(text(fx, fy + arm + 56, "синій — за год. (CW)", size=10, color=NEG))

    # ── Праворуч: таблиця знаків 4×4 ──
    cols = ["throttle", "roll", "pitch", "yaw"]
    # знаки за таблицею статті (m1..m4):
    signs = [
        [+1, -1, +1, +1],   # m1
        [+1, -1, -1, -1],   # m2
        [+1, +1, +1, -1],   # m3
        [+1, +1, -1, +1],   # m4
    ]
    gx0 = 292           # ліва межа сітки
    gy0 = 78            # верх (рядок заголовків)
    cw = 88             # ширина стовпця
    rh = 62             # висота рядка
    row_lbl_w = 42      # ширина колонки з підписами m1..m4

    # заголовки стовпців
    for j, c in enumerate(cols):
        cxj = gx0 + row_lbl_w + j * cw + cw / 2
        f.append(text(cxj, gy0 + 6, c, size=13, bold=True, color=INK))
    # рамка тіла таблиці
    body_x = gx0 + row_lbl_w
    body_y = gy0 + 20
    f.append(rect(body_x, body_y, 4 * cw, 4 * rh, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=8))
    # вертикальні лінії між стовпцями
    for j in range(1, 4):
        xx = body_x + j * cw
        f.append(line(xx, body_y, xx, body_y + 4 * rh, color="#e3e7ee", sw=1))
    # горизонтальні лінії між рядками
    for i in range(1, 4):
        yy = body_y + i * rh
        f.append(line(body_x, yy, body_x + 4 * cw, yy, color="#e3e7ee", sw=1))

    # підписи рядків + знаки
    spin_of = {1: 'ccw', 2: 'cw', 3: 'cw', 4: 'ccw'}
    for i in range(4):
        n = i + 1
        cyr = body_y + i * rh + rh / 2
        col_lbl = FIELD if spin_of[n] == 'ccw' else NEG
        f.append(text(gx0 + row_lbl_w / 2, cyr + 5, "m%d" % n, size=13, bold=True, color=col_lbl))
        for j in range(4):
            cxj = body_x + j * cw + cw / 2
            if signs[i][j] > 0:
                f.append(plus(cxj, cyr, r=13))
            else:
                f.append(minus(cxj, cyr, r=13))

    # підказки під таблицею (по центру тіла — щоб не вилазити за край)
    body_cx = body_x + 4 * cw / 2
    f.append(text(body_cx, body_y + 4 * rh + 22,
                  "throttle — усім «+»    ·    yaw — знак = напрям гвинта",
                  size=10, color=MUTED))
    return render(os.path.join(IMG, "mixer-matrix.svg"), W, H, *f)


# ── Фігура 5 (до hist-tail-rotor): п'ять способів прибрати реактивний момент ──
def fig_configs():
    """Порівняння антимоментних схем: усі гасять той самий момент, різна ціна.
    Зелений — обертання «проти год.» (реакція на корпус за год.);
    синій — «за год.». Де напрями парні — моменти гасяться."""
    W, H = 760, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26,
                  "П'ять способів прибрати той самий реактивний момент",
                  size=17, bold=True))

    def rotor(px, py, r, spin, sw=2.0):
        col = FIELD if spin == 'ccw' else NEG
        out = prop_blades(px, py, r, col)
        out += circle(px, py, max(5, r * 0.16), fill=FILL, stroke=INK, sw=1.4)
        rr = r * 0.62
        if spin == 'ccw':
            out += arc_arrow(px, py, rr, 35, 200, color=col, sw=1.8, head=7)
        else:
            out += arc_arrow(px, py, rr, 200, 35, color=col, sw=1.8, head=7)
        return out

    # сітка панелей 2×3 (остання клітинка — легенда)
    PW, PH = 240, 190
    x0, y0 = 12, 44
    gx, gy = 8, 8
    cells = [(x0 + (PW + gx) * (i % 3), y0 + (PH + gy) * (i // 3)) for i in range(6)]

    def panel(i, title):
        cx, cy = cells[i]
        f.append(rect(cx, cy, PW, PH, fill="#fbfcfe", stroke=MUTED, sw=1.3, rx=8))
        f.append(text(cx + PW / 2, cy + 22, title, size=13, bold=True))
        return cx + PW / 2, cy + PH / 2 + 8

    # 1) один + хвіст
    mx, my = panel(0, "один + хвіст")
    f.append(line(mx, my, mx + 96, my, color=MUTED, sw=5))          # хвостова балка
    f.append(rotor(mx, my, 40, 'ccw'))                              # несний
    f.append(prop_blades(mx + 96, my, 15, NEG))                     # хвостовий (бічний)
    f.append(circle(mx + 96, my, 5, fill=FILL, stroke=INK, sw=1.2))
    f.append(text(mx + 96, my - 24, "хвіст", size=10, color=NEG))
    f.append(text(mx, my + 66, "момент гасить бічна тяга", size=10, color=MUTED))

    # 2) співвісна
    mx, my = panel(1, "співвісна")
    f.append(rotor(mx, my, 44, 'ccw'))
    f.append(rotor(mx, my, 30, 'cw'))
    f.append(text(mx, my + 66, "два ротори на спільній осі", size=10, color=MUTED))

    # 3) тандемна
    mx, my = panel(2, "тандемна")
    f.append(line(mx - 60, my, mx + 60, my, color=MUTED, sw=5))
    f.append(rotor(mx - 60, my, 34, 'ccw'))
    f.append(rotor(mx + 60, my, 34, 'cw'))
    f.append(text(mx, my + 66, "спереду й ззаду", size=10, color=MUTED))

    # 4) поперечна
    mx, my = panel(3, "поперечна")
    f.append(line(mx - 62, my, mx + 62, my, color=MUTED, sw=5))
    f.append(rotor(mx - 62, my, 34, 'ccw'))
    f.append(rotor(mx + 62, my, 34, 'cw'))
    f.append(text(mx - 62, my + 60, "ліво", size=10, color=MUTED))
    f.append(text(mx + 62, my + 60, "право", size=10, color=MUTED))

    # 5) многороторна (квадро)
    mx, my = panel(4, "многороторна")
    off = 52
    corners = [(-off, -off, 'ccw'), (off, -off, 'cw'),
               (off, off, 'ccw'), (-off, off, 'cw')]
    for (dx, dy, s) in corners:
        f.append(line(mx, my, mx + dx, my + dy, color=MUTED, sw=4))
    for (dx, dy, s) in corners:
        f.append(rotor(mx + dx, my + dy, 24, s))
    f.append(text(mx, my + 66, "чотири навхрест + мозок", size=10, color=MUTED))

    # 6) легенда
    cx, cy = cells[5]
    f.append(rect(cx, cy, PW, PH, fill="#f6f8fc", stroke=MUTED, sw=1.3, rx=8))
    f.append(text(cx + PW / 2, cy + 24, "як читати", size=13, bold=True))
    f.append(prop_blades(cx + 34, cy + 58, 22, FIELD))
    f.append(text(cx + 64, cy + 62, "гвинт проти год.", size=11, color=FIELD, anchor="start"))
    f.append(prop_blades(cx + 34, cy + 92, 22, NEG))
    f.append(text(cx + 64, cy + 96, "гвинт за год.", size=11, color=NEG, anchor="start"))
    b, w, h = textbox(cx + PW / 2, cy + 150,
                      "парні напрями →\nмоменти в сумі 0",
                      size=11, pad=7, fill=BG, stroke=FIELD, sw=1.2, bold=True)
    f.append(b)

    return render(os.path.join(IMG, "antitorque-configs.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_single(), fig_quad(), fig_yaw(), fig_mixer_matrix(), fig_configs()]
    print("written:")
    for p in ps:
        print("  ", p)
