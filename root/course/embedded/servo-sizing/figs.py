# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір сервопривода: момент, швидкість, маса» (курс embedded/drony).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Момент = сила × плече; навантаження проти запасу ──────────────────────
def fig_torque():
    """Серво крутить качалку довжиною r; на кінці — навантаження F (від потоку
    на кермі). Потрібний момент = F·r. Поряд — стовпчики: момент навантаження
    і паспортний момент серво з запасом, щоб видно було «з головою / впритул»."""
    W, H = 760, 380
    f = [text(W / 2, 28, "Момент серво має перебороти момент навантаження", size=17, bold=True)]

    # — ліворуч: качалка з силою на кінці —
    cx, cy = 200, 200
    f.append(circle(cx, cy, 30, fill="#eef2f7", stroke=LINE, sw=2))          # корпус серво (вал)
    f.append(text(cx, cy + 5, "вал", size=12, color=MUTED))
    arm_len = 120
    ax, ay = cx + arm_len, cy - 50                                            # кінець качалки
    f.append(line(cx, cy, ax, ay, color=INK, sw=6))                          # качалка
    f.append(text((cx + ax) / 2 - 8, (cy + ay) / 2 - 10, "плече r", size=13, italic=True, color=NEG))
    # сила навантаження на кінці качалки (вниз)
    f.append(arrow(ax, ay, ax, ay + 70, color=POS, sw=3))
    f.append(text(ax + 14, ay + 45, "F", size=15, bold=True, color=POS))
    f.append(text(ax + 14, ay + 64, "(потік на кермі)", size=11, color=MUTED))
    # формула
    bx = fitbox(70, 300, 260, 50, "момент = F · r\n[Н·м] = [Н] · [м]", size=14, bold=True)
    f.append(bx)

    # — праворуч: два стовпчики порівняння —
    base_x, base_y = 480, 300
    bw = 70
    # навантаження
    load_h = 90
    f.append(rect(base_x, base_y - load_h, bw, load_h, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(base_x + bw / 2, base_y + 18, "момент", size=12))
    f.append(text(base_x + bw / 2, base_y + 33, "навантаження", size=12))
    f.append(text(base_x + bw / 2, base_y - load_h - 8, "F·r", size=13, bold=True, color=POS))
    # серво з запасом
    sx = base_x + 140
    serv_h = 170
    f.append(rect(sx, base_y - serv_h, bw, serv_h, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(sx + bw / 2, base_y + 18, "момент", size=12))
    f.append(text(sx + bw / 2, base_y + 33, "серво (паспорт)", size=12))
    f.append(text(sx + bw / 2, base_y - serv_h - 8, "stall", size=13, bold=True, color=FIELD))
    # дужка запасу
    f.append(line(sx + bw + 14, base_y - serv_h, sx + bw + 14, base_y - load_h, color=MUTED, sw=1.5, dash="4 3"))
    f.append(text(sx + bw + 22, base_y - (serv_h + load_h) / 2 + 2, "запас", size=12, color=MUTED, anchor="start"))
    f.append(text(sx + bw + 22, base_y - (serv_h + load_h) / 2 + 18, "(×2…3)", size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'torque.svg'), W, H, *f)


# ── 2. Компроміс момент ↔ швидкість на одному моторі ────────────────────────
def fig_tradeoff():
    """Один і той самий мотор: вибравши передачу/серво на більший момент,
    втрачаєш швидкість, і навпаки. Спадна крива «момент проти швидкості» з
    двома робочими точками: «силове» серво й «швидке» серво."""
    W, H = 760, 380
    f = [text(W / 2, 28, "Той самий двигун: момент і швидкість — обмінюються", size=17, bold=True)]

    # осі
    ox, oy = 110, 320               # початок координат
    axw, axh = 560, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=2))         # вісь швидкості →
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=2))         # вісь моменту ↑
    f.append(text(ox + axw - 4, oy + 26, "швидкість (°/с)  →", size=13, anchor="end"))
    f.append(text(ox - 18, oy - axh + 6, "момент", size=13, anchor="end"))
    f.append(text(ox - 18, oy - axh + 22, "(кг·см)", size=12, anchor="end", color=MUTED))

    # спадна крива момент=k/швидкість (гіпербола-подібна), у px
    pts = []
    for i in range(0, 101):
        sp = 0.08 + i / 100.0 * 0.92                # 0.08..1.0 від діапазону швидкості
        tq = 1.0 / (sp + 0.25) - 0.2               # спадна
        px = ox + sp * axw
        py = oy - max(0.05, tq) / 3.6 * axh
        pts.append((px, py))
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path, NEG))

    # дві робочі точки
    # силове серво: низька швидкість, високий момент
    p1 = pts[18]
    f.append(circle(p1[0], p1[1], 7, fill="#fdecea", stroke=POS, sw=2.5))
    f.append(text(p1[0] + 12, p1[1] - 6, "силове серво", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(p1[0] + 12, p1[1] + 12, "великий момент, повільне", size=11, color=MUTED, anchor="start"))
    # швидке серво
    p2 = pts[82]
    f.append(circle(p2[0], p2[1], 7, fill="#eaf0fd", stroke=NEG, sw=2.5))
    f.append(text(p2[0] - 12, p2[1] - 10, "швидке серво", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(p2[0] - 12, p2[1] + 8, "малий момент, прудке", size=11, color=MUTED, anchor="end"))

    f.append(text(W / 2, 360, "Передача чи модель, що додає моменту, забирає швидкість — добуток приблизно сталий.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'tradeoff.svg'), W, H, *f)


# ── 3. Трикутник вибору: момент / швидкість / маса ──────────────────────────
def fig_triangle():
    """Три вимоги тягнуть у різні боки: більший момент і вища швидкість — це
    важче й ненажерливіше серво; легше серво поступається тим і тим. Вибираєш
    під задачу, бо все одразу по максимуму не буває."""
    W, H = 720, 420
    f = [text(W / 2, 30, "Три вимоги, що тягнуть у різні боки", size=17, bold=True)]

    # вершини трикутника
    cx, cy, R = 360, 250, 150
    top = (cx, cy - R)
    left = (cx - R * 0.87, cy + R * 0.5)
    right = (cx + R * 0.87, cy + R * 0.5)
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#f4f6f8" stroke="%s" stroke-width="2"/>'
             % (top[0], top[1], left[0], left[1], right[0], right[1], LINE))

    # вершини-вимоги
    b1 = fitbox(top[0] - 70, top[1] - 56, 140, 46, "МОМЕНТ\nперебороти потік", size=13, bold=True,
                fill="#fdecea", stroke=POS)
    f.append(b1)
    b2 = fitbox(left[0] - 100, left[1] + 10, 150, 46, "ШВИДКІСТЬ\nвстигнути за командою", size=13, bold=True,
                fill="#eaf0fd", stroke=NEG)
    f.append(b2)
    b3 = fitbox(right[0] - 50, right[1] + 10, 150, 46, "МАСА й струм\nбюджет апарата", size=13, bold=True,
                fill="#eafaf1", stroke=FIELD)
    f.append(b3)

    # підписи на сторонах — конфлікти
    f.append(text((top[0] + left[0]) / 2 - 70, (top[1] + left[1]) / 2, "більше обох", size=12, color=MUTED))
    f.append(text((top[0] + left[0]) / 2 - 70, (top[1] + left[1]) / 2 + 16, "= важче", size=12, color=MUTED))
    f.append(text((top[0] + right[0]) / 2 + 70, (top[1] + right[1]) / 2, "сильніше", size=12, color=MUTED))
    f.append(text((top[0] + right[0]) / 2 + 70, (top[1] + right[1]) / 2 + 16, "= ненажерливіше", size=12, color=MUTED))
    f.append(text(cx, right[1] + 70, "легше серво — поступається і моментом, і швидкістю", size=12, color=MUTED))

    f.append(text(cx, cy + 2, "вибір —", size=13, bold=True))
    f.append(text(cx, cy + 20, "під задачу", size=13, bold=True))

    render(os.path.join(IMG, 'triangle.svg'), W, H, *f)


# ── 4. Динамічний тиск: стовп повітря за секунду, V заходить двічі ───────────
def fig_dynamic_pressure():
    """За секунду на поверхню S налітає стовп повітря довжиною V (маса ρ·V·S);
    він гальмує й тисне. Швидкість входить двічі: у кількість повітря і в
    імпульс кожної порції — звідси q = ½·ρ·V²."""
    W, H = 760, 360
    f = [text(W / 2, 28, "Чому сила на кермі росте з квадратом швидкості", size=17, bold=True)]

    # поверхня (площинка) праворуч
    surf_x = 560
    f.append(line(surf_x, 90, surf_x, 280, color=INK, sw=6))
    f.append(text(surf_x + 16, 190, "поверхня", size=12, color=MUTED, anchor="start"))
    f.append(text(surf_x + 16, 206, "площею S", size=12, color=MUTED, anchor="start"))

    # стовп повітря, що налітає за секунду
    col_x0, col_x1 = 150, surf_x
    col_y0, col_y1 = 110, 260
    f.append(rect(col_x0, col_y0, col_x1 - col_x0, col_y1 - col_y0,
                  fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text((col_x0 + col_x1) / 2, (col_y0 + col_y1) / 2 - 6,
                  "стовп повітря за секунду", size=13, color=NEG))
    f.append(text((col_x0 + col_x1) / 2, (col_y0 + col_y1) / 2 + 14,
                  "маса = ρ · V · S", size=14, bold=True, color=NEG))

    # довжина стовпа = V (стрілка-розмір унизу)
    f.append(arrow(col_x0, 290, col_x1, 290, color=MUTED, sw=1.5))
    f.append(arrow(col_x1, 290, col_x0, 290, color=MUTED, sw=1.5))
    f.append(text((col_x0 + col_x1) / 2, 308, "довжина = V (швидкість)", size=12, color=MUTED))

    # напрям руху
    f.append(arrow(70, 185, 140, 185, color=POS, sw=3))
    f.append(text(70, 168, "V", size=15, bold=True, color=POS, anchor="start"))

    # формула-висновок
    bx = fitbox(250, 322, 280, 34, "V двічі  →  q = ½·ρ·V²", size=15, bold=True,
                fill="#fdecea", stroke=POS)
    f.append(bx)

    render(os.path.join(IMG, 'dynamic-pressure.svg'), W, H, *f)


# ── 5. Ланцюг важелів: момент на завісі → сила в тязі → момент на валу серво ─
def fig_linkage():
    """H на осі керма через кабанчик (плече r_горн) дає силу F у тязі; та сама
    F на качалці серво (плече r_кач) дає момент M = H·(r_кач/r_горн). Відношення
    плечей — передавальне число."""
    W, H = 780, 380
    f = [text(W / 2, 28, "Як момент на завісі доходить до вала серво", size=17, bold=True)]

    # — кермо (праворуч): вісь завіси + кабанчик —
    hx, hy = 600, 220                                  # вісь завіси
    f.append(circle(hx, hy, 10, fill="#eef2f7", stroke=LINE, sw=2))
    f.append(text(hx + 4, hy + 60, "вісь завіси", size=12, color=MUTED, anchor="middle"))
    # площина керма (за завісою)
    f.append(line(hx, hy, hx + 90, hy + 40, color=INK, sw=5))
    f.append(text(hx + 70, hy + 60, "кермо", size=12, color=MUTED))
    # кабанчик угору
    horn_x, horn_y = hx, hy - 70
    f.append(line(hx, hy, horn_x, horn_y, color=POS, sw=4))
    f.append(text(horn_x + 8, (hy + horn_y) / 2, "r_горн", size=12, italic=True, color=POS, anchor="start"))
    # момент H на завісі (дужка)
    f.append(text(hx + 30, hy - 6, "H", size=15, bold=True, color=POS))

    # — серво (ліворуч): вал + качалка —
    sx, sy = 180, 220
    f.append(circle(sx, sy, 26, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(sx, sy + 4, "серво", size=12, color=MUTED))
    arm_x, arm_y = sx, sy - 80
    f.append(line(sx, sy, arm_x, arm_y, color=FIELD, sw=4))
    f.append(text(arm_x - 8, (sy + arm_y) / 2, "r_кач", size=12, italic=True, color=FIELD, anchor="end"))
    f.append(text(sx + 34, sy - 6, "M", size=15, bold=True, color=FIELD, anchor="start"))

    # — тяга між кінцем качалки й кабанчиком —
    f.append(line(arm_x, arm_y, horn_x, horn_y, color=INK, sw=3))
    f.append(text((arm_x + horn_x) / 2, arm_y - 12, "тяга, сила F", size=13, bold=True))

    # формула знизу
    bx = fitbox(250, 322, 280, 40, "M_серво = H · (r_кач / r_горн)", size=15, bold=True)
    f.append(bx)
    f.append(text(W / 2, 372, "Відношення плечей — передавальне число: момент проти ходу керма.",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'linkage.svg'), W, H, *f)


# ── 6. Часова стрічка кілограм-сили (вставка hist-kgf-cm) ────────────────────
def fig_kgf_history():
    """Життя кілограм-сили крізь три епохи: XIX ст. (сила = вага, g залежить
    від місця) → 1901 фіксація g₀=9.80665, технічна система МКГСС → 1960 СІ й
    ньютон, але кг·см виживає в RC-серво. Точний місток 1 кгс = 9.80665 Н."""
    W, H = 860, 440
    f = [text(W / 2, 30, "Кілограм-сила: одиниця, що пережила реформу СІ", size=17, bold=True)]

    # головна вісь часу
    ax0, ax1, ay = 60, 800, 160
    f.append(arrow(ax0, ay, ax1, ay, color=INK, sw=2.5))
    f.append(text(ax1, ay - 14, "час →", size=13, anchor="end", color=MUTED))

    # три фази-смуги під віссю (заливки кольорами епох)
    bands = [
        (60,  255, "#eaf0fd", NEG,   "XIX ст. — доСІ"),
        (300, 515, "#eafaf1", FIELD, "1901 — технічна система"),
        (560, 800, "#fdecea", POS,   "1960 — реформа СІ"),
    ]
    for x0, x1, fill, stroke, cap in bands:
        f.append(rect(x0, ay + 20, x1 - x0, 30, fill=fill, stroke=stroke, sw=1.5, rx=8))
        f.append(text((x0 + x1) / 2, ay + 40, cap, size=12, bold=True, color=stroke))

    # ключові віхи на осі (вузол + рік + підпис над/під)
    def milestone(x, year, lines, up=True, color=INK):
        out = [circle(x, ay, 6, fill="#ffffff", stroke=color, sw=2.5)]
        if up:
            out.append(text(x, ay - 58, year, size=14, bold=True, color=color))
            out.append(line(x, ay - 50, x, ay - 8, color=color, sw=1.2, dash="3 3"))
            yy = ay - 92
        else:
            out.append(text(x, ay + 74, year, size=14, bold=True, color=color))
            out.append(line(x, ay + 8, x, ay + 66, color=color, sw=1.2, dash="3 3"))
            yy = ay + 94
        for i, ln in enumerate(lines):
            out.append(text(x, yy + i * 16, ln, size=11, color=MUTED))
        return out

    f += milestone(150, "XIX ст.", ["сила = вага,", "g залежить від місця"], up=True,  color=NEG)
    f += milestone(360, "1901",    ["3-тя CGPM фіксує", "g₀ = 9.80665 м/с²"], up=True,  color=FIELD)
    f += milestone(460, "МКГСС",   ["сила — база,", "маса — похідна ≈9.81 кг"], up=False, color=FIELD)
    f += milestone(620, "1960",    ["СІ: ньютон —", "одиниця сили"],          up=True,  color=POS)
    f += milestone(740, "донині",  ["кг·см виживає", "в RC-серво"],           up=False, color=POS)

    # точний місток між епохами — рамка внизу
    f.append(fitbox(W / 2 - 180, 392, 360, 40,
                    "точний місток між епохами:  1 кгс = 9.80665 Н",
                    size=14, bold=True, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'kgf-history.svg'), W, H, *f)


if __name__ == "__main__":
    fig_torque()
    fig_tradeoff()
    fig_triangle()
    fig_dynamic_pressure()
    fig_linkage()
    fig_kgf_history()
    print("OK: torque, tradeoff, triangle, dynamic-pressure, linkage, kgf-history ->", IMG)
