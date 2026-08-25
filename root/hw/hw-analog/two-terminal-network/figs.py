# -*- coding: utf-8 -*-
"""Фігури до статті «Двополюсна мережа» (book/electronics/analog/two-terminal-network).
Фігури статті:
  port.svg   — означення: чорна скриня з однією парою затискачів; умова порту (i в = i з)
  iv.svg     — повний опис двополюсника = його ВАХ; пряма (лінійний) vs крива (діод);
               перетини осей = напруга холостого ходу й струм короткого замикання
  equiv.svg  — та сама пряма ⇒ два рівноправні еквіваленти за тими самими затискачами
Фігури вставки math-linear-iv.md:
  super.svg  — суперпозиція: афінна пряма u(i) = сума однорідної частини (−R·i, крізь нуль)
               і сталого зсуву (U хх); дві мінідіаграми додаються у третю
  duality.svg— одна пряма, два прочитання: u(i) = U хх − R·i  ⇄  i(u) = I кз − u/R;
               перетини осей і зв'язок нахилів (−R та −1/R)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ─────────────────────────────────────────────────────────
def term(cx, cy, r=6):
    """Затискач — порожнє коло на провіднику."""
    return circle(cx, cy, r, fill=BG, stroke=INK, sw=2)


def battery(cx, cy, h=34):
    """Символ джерела ЕРС (батарея): довга/коротка риски, вертикально."""
    out = [line(cx, cy - h / 2, cx, cy - 6, color=INK, sw=2),
           line(cx - 12, cy - 6, cx + 12, cy - 6, color=INK, sw=3),   # +  довга
           line(cx - 6,  cy + 2, cx + 6,  cy + 2, color=INK, sw=6),   # −  коротка/товста
           line(cx, cy + 2, cx, cy + h / 2, color=INK, sw=2)]
    return "".join(out)


def res(cx, cy, h=40, label=None, lab_dx=18):
    """Резистор — прямокутник на вертикальному проводі."""
    w = 16
    out = [line(cx, cy - h / 2, cx, cy - 12, color=INK, sw=2),
           rect(cx - w / 2, cy - 12, w, 24, fill=BG, stroke=INK, sw=2, rx=2),
           line(cx, cy + 12, cx, cy + h / 2, color=INK, sw=2)]
    if label:
        out.append(text(cx + lab_dx, cy + 4, label, size=13, color=INK))
    return "".join(out)


def isrc(cx, cy, r=15):
    """Символ джерела струму — коло зі стрілкою вгору."""
    out = [circle(cx, cy, r, fill=BG, stroke=INK, sw=2),
           line(cx, cy + r - 3, cx, cy - r + 5, color=INK, sw=2),
           line(cx - 4, cy - r + 9, cx, cy - r + 4, color=INK, sw=2),
           line(cx + 4, cy - r + 9, cx, cy - r + 4, color=INK, sw=2)]
    return "".join(out)


# ── Фігура 1: означення порту ────────────────────────────────────────────────
def fig_port():
    W, H = 640, 320
    bx, by, bw, bh = 250, 95, 150, 130           # «чорна скриня»
    p = [rect(bx, by, bw, bh, fill="#1f2937", stroke=INK, sw=2, rx=10)]
    p.append(text(bx + bw / 2, by + bh / 2 - 6, "будь-яке", size=15, color="#f4f6f8"))
    p.append(text(bx + bw / 2, by + bh / 2 + 14, "коло всередині", size=15, color="#f4f6f8"))

    tx = bx + bw                                  # права грань — там обидва затискачі
    ya, yb = by + 32, by + bh - 32
    # верхній провід (затискач A)
    p.append(line(tx, ya, tx + 120, ya, color=INK, sw=2))
    p.append(term(tx + 120, ya))
    p.append(text(tx + 134, ya + 5, "A", size=15, bold=True))
    # нижній провід (затискач B)
    p.append(line(tx, yb, tx + 120, yb, color=INK, sw=2))
    p.append(term(tx + 120, yb))
    p.append(text(tx + 134, yb + 5, "B", size=15, bold=True))

    # струм: входить у A, виходить із B — однаковий
    p.append(arrow(tx + 50, ya - 16, tx + 92, ya - 16, color=POS, sw=2.2))
    p.append(text(tx + 70, ya - 24, "i", size=15, color=POS, italic=True, bold=True))
    p.append(arrow(tx + 92, yb + 16, tx + 50, yb + 16, color=POS, sw=2.2))
    p.append(text(tx + 70, yb + 30, "i", size=15, color=POS, italic=True, bold=True))

    # напруга на парі затискачів
    p.append(line(tx + 78, ya + 6, tx + 78, yb - 6, color=NEG, sw=1.6, dash="4 4"))
    p.append(text(tx + 90, (ya + yb) / 2 + 5, "u", size=15, color=NEG, italic=True, bold=True))

    # умова порту — рамка-пояснення
    cap, cw, ch = textbox(150, 250, "умова порту:\nскільки струму ввійшло в A,\nстільки вийшло з B",
                          size=12, fill="#eaf0fd", stroke=NEG, color=INK)
    p.append(cap)
    # ліва грань — лишаємо «глуху», щоб показати: назовні видно лише одну пару
    p.append(text(bx - 8, by + bh / 2 + 4, "решта схеми", size=11, color=MUTED, anchor="end"))
    p.append(text(bx - 8, by + bh / 2 + 20, "захована", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'port.svg'), W, H, "".join(p),
           title="Двополюсник: назовні видно лише одну пару затискачів")


# ── Фігура 2: ВАХ = повний опис ──────────────────────────────────────────────
def fig_iv():
    W, H = 660, 380
    ox, oy = 130, 300                             # початок осей (нуль)
    ax_w, ax_h = 440, 230
    p = []
    # осі
    p.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))      # i →
    p.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))      # u ↑
    p.append(text(ox + ax_w - 6, oy + 22, "струм  i", size=13, color=INK, anchor="end"))
    p.append(text(ox - 10, oy - ax_h + 6, "напруга u", size=13, color=INK, anchor="end"))

    # лінійний двополюсник — пряма від (0, Uoc) до (Isc, 0)
    Uoc_y = oy - ax_h + 30                         # точка на осі u
    Isc_x = ox + ax_w - 60                         # точка на осі i
    p.append(line(ox, Uoc_y, Isc_x, oy, color=POS, sw=2.6))
    p.append(text((ox + Isc_x) / 2 + 18, (Uoc_y + oy) / 2 - 10, "лінійний", size=13, color=POS, bold=True))

    # перетини осей
    p.append(circle(ox, Uoc_y, 4, fill=POS, stroke=POS))
    p.append(line(ox - 6, Uoc_y, ox + 6, Uoc_y, color=NEG, sw=1.4, dash="3 3"))
    cap1, _, _ = textbox(ox - 64, Uoc_y, "U хх\n(холостий хід)", size=11,
                         fill="#eaf0fd", stroke=NEG, color=INK)
    p.append(cap1)
    p.append(circle(Isc_x, oy, 4, fill=POS, stroke=POS))
    cap2, _, _ = textbox(Isc_x, oy + 34, "I кз\n(коротке замикання)", size=11,
                         fill="#eaf0fd", stroke=NEG, color=INK)
    p.append(cap2)

    # нахил = опір
    p.append(text((ox + Isc_x) / 2 - 40, (Uoc_y + oy) / 2 + 40,
                  "нахил = R", size=12, color=MUTED))

    # нелінійний двополюсник — крива (діод): майже плоско, тоді різко вгору
    import math
    pts = []
    for k in range(0, 61):
        ii = k / 60.0
        # експонентна «коліно»-крива, нормована в межі вікна
        uu = 0.78 * (1 - math.exp(-ii * 3.0)) / (1 - math.exp(-3.0))
        x = ox + ii * (Isc_x - ox) * 0.92
        y = oy - uu * (oy - Uoc_y) * 0.96
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), FIELD))
    p.append(text(Isc_x - 70, Uoc_y + 30, "нелінійний", size=13, color=FIELD, bold=True))
    p.append(text(Isc_x - 70, Uoc_y + 47, "(діод)", size=11, color=FIELD))

    render(os.path.join(IMG, 'iv.svg'), W, H, "".join(p),
           title="Повний опис двополюсника — його ВАХ (струм проти напруги)")


# ── Фігура 3: одна пряма — два еквіваленти ───────────────────────────────────
def fig_equiv():
    W, H = 680, 300

    # ── Тевенін: ЕРС + послідовний опір ──
    tx = 130
    ty0, ty1 = 70, 230
    p = []
    p.append(text(tx, 44, "Тевенін", size=15, bold=True, color=POS))
    # вертикальна гілка: верх → резистор → джерело → низ
    p.append(line(tx, ty0, tx, ty0 + 18, color=INK, sw=2))
    p.append(res(tx, ty0 + 40, h=44, label="R", lab_dx=16))
    p.append(battery(tx, ty0 + 92))
    p.append(line(tx, ty0 + 110, tx, ty1, color=INK, sw=2))
    p.append(text(tx - 18, ty0 + 96, "U", size=13, color=INK, anchor="end"))
    # затискачі праворуч
    p.append(line(tx, ty0, tx + 70, ty0, color=INK, sw=2)); p.append(term(tx + 70, ty0)); p.append(text(tx + 84, ty0 + 5, "A", size=13, bold=True))
    p.append(line(tx, ty1, tx + 70, ty1, color=INK, sw=2)); p.append(term(tx + 70, ty1)); p.append(text(tx + 84, ty1 + 5, "B", size=13, bold=True))

    # ── Нортон: джерело струму ∥ опір ──
    nx = 470
    p.append(text(nx, 44, "Нортон", size=15, bold=True, color=FIELD))
    # ліва гілка — джерело струму
    p.append(line(nx, ty0, nx, ty0 + 50, color=INK, sw=2))
    p.append(isrc(nx, ty0 + 80))
    p.append(line(nx, ty0 + 110, nx, ty1, color=INK, sw=2))
    p.append(text(nx - 22, ty0 + 84, "I", size=13, color=INK, anchor="end"))
    # права гілка — паралельний опір
    rx = nx + 64
    p.append(line(nx, ty0, rx, ty0, color=INK, sw=2))
    p.append(line(nx, ty1, rx, ty1, color=INK, sw=2))
    p.append(res(rx, (ty0 + ty1) / 2, h=ty1 - ty0 - 24, label="R", lab_dx=16))
    # затискачі праворуч
    tx2 = rx
    p.append(line(tx2, ty0, tx2 + 70, ty0, color=INK, sw=2)); p.append(term(tx2 + 70, ty0)); p.append(text(tx2 + 84, ty0 + 5, "A", size=13, bold=True))
    p.append(line(tx2, ty1, tx2 + 70, ty1, color=INK, sw=2)); p.append(term(tx2 + 70, ty1)); p.append(text(tx2 + 84, ty1 + 5, "B", size=13, bold=True))

    # знак рівності між схемами
    p.append(text((tx + 84 + nx) / 2 + 6, (ty0 + ty1) / 2 + 6, "≡", size=30, color=MUTED, bold=True))
    # підпис унизу
    cap, _, _ = textbox(W / 2, 282, "за затискачами A–B обидва дають ту саму пряму ВАХ — їх не розрізнити ззовні",
                        size=11, fill=FILL, stroke=LINE, color=INK)
    p.append(cap)

    render(os.path.join(IMG, 'equiv.svg'), W, H, "".join(p),
           title="Та сама пряма — два рівноправні записи лінійного двополюсника")


# ── Фігура 4 (вставка): суперпозиція ⇒ афінна пряма ───────────────────────────
def fig_super():
    """Дві причини на порту складаються: однорідний відгук на струм (пряма крізь нуль)
    плюс сталий внесок внутрішніх джерел (горизонталь U хх) = повна ВАХ u(i)."""
    W, H = 760, 340
    p = []

    def mini(ox, oy, aw, ah, draw, sub):
        """Маленькі осі (i вправо, u вгору) з нулем у (ox, oy) і власним малюнком."""
        out = [arrow(ox, oy, ox + aw, oy, color=INK, sw=1.5),
               arrow(ox, oy, ox, oy - ah, color=INK, sw=1.5),
               text(ox + aw - 2, oy + 16, "i", size=12, italic=True, color=INK, anchor="end"),
               text(ox - 6, oy - ah + 4, "u", size=12, italic=True, color=INK, anchor="end")]
        out.append(draw(ox, oy, aw, ah))
        out.append(text(ox + aw / 2, oy + 36, sub, size=12, color=MUTED))
        return "".join(out)

    aw, ah = 140, 108
    y0 = 96
    U = 0.62 * ah          # висота U хх на осі u (у пікселях від нуля)
    span = aw - 24         # горизонтальний хід, де пряма перетинає вісь i

    # (1) однорідна частина: u = −R·i  — пряма крізь нуль, що спадає під вісь
    def homo(ox, oy, aw, ah):
        # від нуля (i=0, u=0) вниз: за Δi=span спад на U (той самий нахил, що в (3))
        return (line(ox, oy, ox + span, oy + U, color=POS, sw=2.4) +
                circle(ox, oy, 3.5, fill=INK, stroke=INK) +
                text(ox + span - 6, oy + U + 14, "−R·i", size=12, color=POS, bold=True, anchor="end"))

    # (2) сталий зсув: u = U хх — горизонталь на висоті U
    def offs(ox, oy, aw, ah):
        yb = oy - U
        return (line(ox, yb, ox + aw - 12, yb, color=NEG, sw=2.4) +
                line(ox - 5, yb, ox + 5, yb, color=NEG, sw=1.4, dash="3 3") +
                text(ox - 8, yb + 4, "U хх", size=12, color=NEG, anchor="end", bold=True))

    # (3) сума: u = U хх − R·i — афінна пряма від (0, U хх) до (I кз, 0)
    def full(ox, oy, aw, ah):
        yb = oy - U                               # перетин осі u — U хх
        x_zero = ox + span                        # перетин осі i — I кз (у тому ж span)
        out = [line(ox, yb, x_zero, oy, color=FIELD, sw=2.8),
               circle(ox, yb, 4, fill=FIELD, stroke=FIELD),
               line(ox - 5, yb, ox + 5, yb, color=NEG, sw=1.3, dash="3 3"),
               text(ox - 8, yb + 4, "U хх", size=11, color=NEG, anchor="end"),
               circle(x_zero, oy, 4, fill=FIELD, stroke=FIELD),
               text(x_zero + 4, oy + 15, "I кз", size=11, color=FIELD, anchor="middle")]
        return "".join(out)

    gap = 56
    x1 = 56
    x2 = x1 + aw + gap
    x3 = x2 + aw + gap
    p.append(mini(x1, y0 + ah, aw, ah, homo, "відгук на струм i\n(джерела вимкнено)"))
    p.append(mini(x2, y0 + ah, aw, ah, offs, "внесок джерел\n(струм i = 0)"))
    p.append(mini(x3, y0 + ah, aw, ah, full, "повна ВАХ"))

    # знаки «+» і «=» між діаграмами
    midy = y0 + ah - ah * 0.30
    p.append(text(x1 + aw + gap / 2, midy, "+", size=26, color=MUTED, bold=True))
    p.append(text(x2 + aw + gap / 2, midy, "=", size=26, color=MUTED, bold=True))

    # формула-підсумок унизу
    cap, _, _ = textbox(W / 2, 306, "u(i) = (−R·i) + U хх",
                        size=14, fill=FILL, stroke="#7c3aed", color=INK, bold=True)
    p.append(cap)
    p.append(text(W / 2, 332, "однорідна частина (крізь нуль) плюс сталий зсув",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'super.svg'), W, H, "".join(p),
           title="Лінійність розкладає ВАХ на дві складові, що додаються")


# ── Фігура 5 (вставка): одна пряма — два прочитання (двоїстість) ───────────────
def fig_duality():
    """Та сама пряма, прочитана як u(i) і як i(u): два перетини осей (U хх та I кз)
    і два «нахили» (−R та −1/R) — це одна геометрична річ."""
    W, H = 660, 380
    ox, oy = 150, 300
    aw, ah = 430, 230
    p = []
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    p.append(text(ox + aw - 6, oy + 22, "струм  i", size=13, color=INK, anchor="end"))
    p.append(text(ox - 10, oy - ah + 6, "напруга u", size=13, color=INK, anchor="end"))

    Uoc_y = oy - ah + 28          # точка U хх на осі u
    Isc_x = ox + aw - 70          # точка I кз на осі i
    p.append(line(ox, Uoc_y, Isc_x, oy, color="#7c3aed", sw=2.8))

    # перетин осі u — U хх (читаємо як u при i=0)
    p.append(circle(ox, Uoc_y, 4.5, fill="#7c3aed", stroke="#7c3aed"))
    cap1, _, _ = textbox(ox - 60, Uoc_y, "U хх\n(i = 0)", size=11,
                         fill="#eaf0fd", stroke=NEG, color=INK)
    p.append(cap1)
    # перетин осі i — I кз (читаємо як i при u=0)
    p.append(circle(Isc_x, oy, 4.5, fill="#7c3aed", stroke="#7c3aed"))
    cap2, _, _ = textbox(Isc_x, oy + 34, "I кз\n(u = 0)", size=11,
                         fill="#eaf0fd", stroke=NEG, color=INK)
    p.append(cap2)

    # трикутник нахилу — Δu / Δi = −R
    mx, my = ox + (Isc_x - ox) * 0.30, Uoc_y + (oy - Uoc_y) * 0.30
    dx = 90
    slope = (oy - Uoc_y) / (Isc_x - ox)   # |нахил| у пікс
    p.append(line(mx, my, mx + dx, my, color=MUTED, sw=1.4, dash="4 3"))
    p.append(line(mx + dx, my, mx + dx, my + slope * dx, color=MUTED, sw=1.4, dash="4 3"))
    p.append(text(mx + dx / 2, my - 8, "Δi", size=11, color=MUTED))
    p.append(text(mx + dx + 22, my + slope * dx / 2, "Δu", size=11, color=MUTED))

    # дві підписи-прочитання
    b1, _, _ = textbox(ox + aw * 0.62, oy - ah * 0.78,
                       "як u(i):  u = U хх − R·i\nнахил = −R", size=12,
                       fill="#f3eefe", stroke="#7c3aed", color=INK)
    p.append(b1)
    b2, _, _ = textbox(ox + aw * 0.62, oy - ah * 0.40,
                       "як i(u):  i = I кз − u/R\nнахил = −1/R", size=12,
                       fill="#f3eefe", stroke="#7c3aed", color=INK)
    p.append(b2)

    # зв'язок інтерсептів
    cap3, _, _ = textbox(W / 2, 352, "одна пряма  ⇒  U хх = I кз · R  (закон Ома на тому самому R)",
                         size=12, fill=FILL, stroke=LINE, color=INK)
    p.append(cap3)

    render(os.path.join(IMG, 'duality.svg'), W, H, "".join(p),
           title="Одна пряма ВАХ — два рівноправні прочитання")


if __name__ == "__main__":
    fig_port()
    fig_iv()
    fig_equiv()
    fig_super()
    fig_duality()
    print("OK: port.svg, iv.svg, equiv.svg, super.svg, duality.svg")
