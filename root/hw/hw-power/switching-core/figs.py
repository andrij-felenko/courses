# -*- coding: utf-8 -*-
"""Фігури для теми «ключ + котушка: принцип усіх топологій».
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід — у ./img/.
Імена файлів — slug-only, без номерів і без «Рис.» (підписи — у .md)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_core():
    """Незвідне ядро: ключ рубає вхід, котушка (зелена) переносить енергію,
    конденсатор тримає вихід. Уся мережа ключів лише по черзі під'єднує
    котушку до двох різних напруг."""
    W, H = 760, 360
    frags = []
    y = 175
    # вхід
    frags.append(plus(70, y - 18))
    frags.append(text(70, y + 22, "Vвх", size=13, color=MUTED))
    frags.append(line(70, y, 150, y, color=INK, sw=2))
    # ключ
    b, w, h = textbox(195, y, "ключ", size=15, bold=True, fill="#fdecea", stroke=POS, min_w=86)
    frags.append(b)
    frags.append(text(195, y + 44, "рубає на імпульси", size=11, color=MUTED))
    frags.append(line(238, y, 300, y, color=INK, sw=2))
    # котушка — серце
    b, w, h = textbox(345, y, "котушка", size=15, bold=True, fill="#eaf7ee", stroke=FIELD, min_w=110)
    frags.append(b)
    frags.append(text(345, y + 44, "переносить енергію", size=11, color=FIELD, bold=True))
    frags.append(line(400, y, 470, y, color=INK, sw=2))
    # вузол
    frags.append(circle(470, y, 4, fill=INK, stroke=INK))
    # конденсатор
    b, w, h = textbox(525, y, "конд.", size=15, bold=True, fill="#eaf0fd", stroke=NEG, min_w=86)
    frags.append(b)
    frags.append(text(525, y + 44, "тримає вихід", size=11, color=MUTED))
    frags.append(line(470, y, 470, y + 70, color=INK, sw=2))
    frags.append(line(470, y + 70, 525, y + 70, color=INK, sw=2))  # до низу конд.
    # вихід
    frags.append(line(525, y, 660, y, color=INK, sw=2))
    frags.append(text(645, y - 14, "Vвих", size=13, color=MUTED))
    frags.append(circle(660, y, 4, fill=INK, stroke=INK))
    frags.append(line(660, y, 660, y + 70, color=INK, sw=2))
    frags.append(line(525, y + 70, 660, y + 70, color=INK, sw=2))  # спільна земля
    frags.append(line(70, y - 6, 70, y + 70, color=INK, sw=2))
    frags.append(line(70, y + 70, 470, y + 70, color=INK, sw=2))
    # підпис-висновок
    frags.append(fitbox(70, 300, 620, 40,
        "Топології (buck, boost, buck-boost) різняться лише тим, ДО ЯКИХ двох напруг "
        "мережа ключів по черзі під'єднує котушку.", size=12, fill="#eef8ef", stroke=FIELD))
    return render(os.path.join(OUT, "core.svg"), W, H, *frags)


def fig_inductor():
    """Дві властивості котушки: стала напруга наганяє струм лінійно (нахил Vл/L);
    енергія живе в магнітному полі (½LI²). Аналогія — маховик."""
    W, H = 760, 360
    frags = []
    # ── ліворуч: V стала → i лінійно ──
    L1x = 70
    frags.append(text(L1x + 130, 70, "стала V → струм лінійно", size=13, bold=True))
    ax, ay0, ay1, axw = L1x + 30, 290, 110, 230
    frags.append(line(ax, ay0, ax, ay1, color=INK, sw=1.8))          # вісь i
    frags.append(line(ax, 250, ax + axw, 250, color=INK, sw=1.8))    # вісь t
    frags.append(text(ax - 10, 120, "iл", size=12, color=INK, anchor="end"))
    frags.append(text(ax + axw, 268, "t", size=12, color=INK))
    frags.append(line(ax, 250, ax + axw - 10, 140, color=FIELD, sw=3))  # лінійний ріст
    frags.append(text(ax + 150, 165, "нахил Vл/L", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(line(ax, 305, ax + axw - 10, 305, color=POS, sw=2, dash="5,4"))
    frags.append(text(ax + 100, 322, "стала напруга Vл", size=11, color=POS))
    # ── праворуч: енергія в полі ──
    R1x = 430
    frags.append(text(R1x + 140, 70, "енергія в магнітному полі", size=13, bold=True))
    bx, by0, by1, bxw = R1x + 30, 290, 110, 230
    frags.append(line(bx, by0, bx, by1, color=INK, sw=1.8))
    frags.append(line(bx, 250, bx + bxw, 250, color=INK, sw=1.8))
    frags.append(text(bx - 10, 120, "E", size=12, color=INK, anchor="end"))
    frags.append(text(bx + bxw, 268, "I", size=12, color=INK))
    # парабола E=½LI²
    pts = []
    for k in range(0, 51):
        ii = k / 50.0
        px = bx + ii * (bxw - 12)
        py = 250 - (ii * ii) * 138
        pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), FIELD))
    frags.append(text(bx + 120, 150, "½·L·I²", size=13, color=FIELD, bold=True, anchor="start"))
    # підпис-аналогія
    frags.append(fitbox(40, 305, 680, 42,
        "Аналогія — маховик: струм як швидкість обертання, миттєво не змінити; "
        "енергію можна запасти й повернути.",
        size=13, fill=FILL, stroke=MUTED))
    return render(os.path.join(OUT, "inductor.svg"), W, H, *frags)


def fig_phases():
    """Універсальний ритм: фаза ВКЛ — котушка під +Von, струм росте; фаза ВИКЛ —
    струм не уривається, тече через діод під −Voff, спадає."""
    W, H = 760, 340
    frags = []

    def cell(x0, title, vlabel, vcolor, arrow_up, note):
        f = []
        f.append(textbox(x0 + 150, 70, title, size=14, bold=True, min_w=200)[0])
        y = 150
        f.append(plus(x0 + 30, y) if arrow_up else minus(x0 + 30, y))
        f.append(line(x0 + 40, y, x0 + 110, y, color=INK, sw=2))
        b, w, h = textbox(x0 + 150, y, "котушка", size=13, bold=True,
                          fill="#eaf7ee", stroke=FIELD, min_w=88)
        f.append(b)
        f.append(line(x0 + 194, y, x0 + 264, y, color=INK, sw=2))
        f.append(text(x0 + 150, y - 34, vlabel, size=13, color=vcolor, bold=True))
        # стрілка струму
        ar = arrow(x0 + 70, y + 42, x0 + 230, y + 42, color=vcolor, sw=2.4)
        f.append(ar)
        f.append(text(x0 + 150, y + 64, "струм " + ("росте" if arrow_up else "спадає"),
                      size=12, color=vcolor, bold=True))
        f.append(fitbox(x0 + 15, 248, 290, 56, note, size=12,
                        fill=("#fdecea" if arrow_up else "#eaf0fd"),
                        stroke=(POS if arrow_up else NEG)))
        return f

    frags += cell(40, "Фаза ВКЛ (ключ замкнено)", "+Von", POS, True,
                  "Котушка під напругою\nодного знаку —\nзапасає енергію.")
    frags += cell(420, "Фаза ВИКЛ (ключ розімкнено)", "−Voff", NEG, False,
                  "Струм не уривається:\nтече через діод під\nпротилежним знаком —\nкотушка віддає запас.")
    return render(os.path.join(OUT, "phases.svg"), W, H, *frags)


def fig_volt_second():
    """Центральний закон. Угорі — напруга на котушці: вузький високий +Von і широкий
    низький −Voff, зелена площа = червона. Унизу — струм-трикутник, що повертається
    до того самого рівня (Δi=0)."""
    W, H = 760, 470
    frags = []
    L, R = 90, 700
    # ── напруга ──
    base = 150
    top, bot = 96, 210
    frags.append(line(L, 230, L, 86, color=INK, sw=1.8))
    frags.append(line(L, base, R, base, color=INK, sw=1.8))
    frags.append(text(L - 12, 96, "Vл", size=12, color=INK, anchor="end"))
    frags.append(text(R, base + 4, "t", size=12, color=INK))
    xa, xb, xc = L, 250, 480   # межі фаз (вузький + / широкий −) у двох циклах
    # цикл 1
    frags.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#cdeed4"/>' % (xa, base, xa, top, xb, top, xb, base))
    frags.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#f6d2cd"/>' % (xb, base, xb, bot, xc, bot, xc, base))
    frags.append(line((xa + xb) // 2, base, (xa + xb) // 2, top, color=NEG, sw=0))
    frags.append(text((xa + xb) // 2, top - 8, "+Von", size=12, color=FIELD, bold=True))
    frags.append(text((xa + xb) // 2, base - 8, "D·T", size=10, color=FIELD))
    frags.append(text((xb + xc) // 2, bot + 16, "−Voff", size=12, color=POS, bold=True))
    frags.append(text((xb + xc) // 2, base + 14, "(1−D)·T", size=10, color=POS))
    # контур напруги (2 цикли)
    xc2, xd2 = 510, 690
    frags.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#cdeed4"/>' % (xc, base, xc, top, xc2, top, xc2, base))
    frags.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#f6d2cd"/>' % (xc2, base, xc2, bot, xd2, bot, xd2, base))
    poly = "%d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d" % (
        xa, top, xb, top, xb, bot, xc, bot, xc, top, xc2, top, xc2, bot, xd2, bot, xd2, base)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (poly, INK))
    # рамка-висновок напруги
    frags.append(fitbox(L, 50, R - L, 30,
        "сталий режим:  площа(+) = площа(−)   ⇒   Von·D·T = Voff·(1−D)·T   ⇒   середня Vл = 0",
        size=12.5, fill="#f6f6f6", stroke=MUTED, bold=True))
    # ── струм ──
    iy = 430
    frags.append(line(L, 470, L, 350, color=INK, sw=1.8))
    frags.append(line(L, iy, R, iy, color=INK, sw=1.8))
    frags.append(text(L - 12, 360, "iл", size=12, color=INK, anchor="end"))
    frags.append(text(R, iy + 4, "t", size=12, color=INK))
    tpts = [(xa, iy - 16), (xb, iy - 64), (xc, iy - 16), (xc2, iy - 64), (xd2, iy - 16)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>'
                 % (" ".join("%d,%d" % p for p in tpts), "#b5763a"))
    frags.append(line(L, iy - 16, R - 20, iy - 16, color=MUTED, sw=1.3, dash="5,5"))
    frags.append(text(R - 24, iy - 22, "той самий рівень щоцикл (Δi = 0)", size=11, color=MUTED, anchor="end", italic=True))
    return render(os.path.join(OUT, "volt-second.svg"), W, H, *frags)


def fig_runaway():
    """Збалансований режим (угорі): струм гойдається навколо сталого середнього.
    Незбалансований (унизу): середній струм повзе вгору щоцикл — до насичення."""
    W, H = 760, 380
    frags = []
    L, R = 90, 700
    # ── збалансований ──
    y0 = 130
    frags.append(line(L, 165, L, 70, color=INK, sw=1.6))
    frags.append(line(L, y0, R, y0, color=INK, sw=1.6))
    frags.append(text(L - 12, 80, "iл", size=12, color=INK, anchor="end"))
    pts = []
    x = L
    for k in range(8):
        pts.append((x, y0 + (8 if k % 2 == 0 else -28)))
        x += (R - L) / 8.0
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join("%.0f,%.0f" % p for p in pts), FIELD))
    frags.append(line(L, y0 - 10, R, y0 - 10, color=MUTED, sw=1.2, dash="5,5"))
    frags.append(text(R - 6, 78, "збалансований: середній струм сталий — перетворювач «стоїть»",
                      size=11.5, color=FIELD, anchor="end", bold=True))
    # ── незбалансований ──
    y1 = 320
    frags.append(line(L, 360, L, 220, color=INK, sw=1.6))
    frags.append(line(L, y1, R, y1, color=INK, sw=1.6))
    frags.append(text(L - 12, 230, "iл", size=12, color=INK, anchor="end"))
    pts = []
    x = L
    rise = 0
    for k in range(8):
        pts.append((x, y1 - rise + (0 if k % 2 == 0 else -26)))
        if k % 2 == 1:
            rise += 18
        x += (R - L) / 8.0
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join("%.0f,%.0f" % p for p in pts), POS))
    # лінія середнього, що повзе
    frags.append(arrow(L + 20, y1 - 8, R - 40, y1 - 90, color=POS, sw=1.8))
    frags.append(text(R - 6, 230, "незбалансований: середній струм повзе вгору щоцикл → насичення, ключ згорає",
                      size=11.5, color=POS, anchor="end", bold=True))
    return render(os.path.join(OUT, "runaway.svg"), W, H, *frags)


def fig_topologies():
    """Вольт-секундний баланс — спільний ключ: ним відмикається buck (Vвих=D·Vвх),
    тим самим ключем — boost і buck-boost (інша розкладка тих самих деталей)."""
    W, H = 760, 330
    frags = []
    # ключ у центрі
    b, w, h = textbox(380, 90, "вольт-секундний баланс\nVon·tвкл = Voff·tвикл", size=14, bold=True,
                      fill="#eaf7ee", stroke=FIELD, min_w=320)
    frags.append(b)
    frags.append(text(380, 140, "один закон", size=11, color=FIELD, bold=True))
    boxes = [
        (170, "buck", "Vвих = D·Vвх"),
        (380, "boost", "Vвих = Vвх/(1−D)"),
        (590, "buck-boost", "Vвих = Vвх·D/(1−D)"),
    ]
    for cx, name, formula in boxes:
        frags.append(arrow(380, 116, cx, 218, color=MUTED, sw=1.6))
        b, w, h = textbox(cx, 245, name, size=14, bold=True, min_w=130)
        frags.append(b)
        frags.append(text(cx, 290, formula, size=12, color=INK))
    frags.append(text(380, 315, "інша розкладка тих самих деталей — закон той самий",
                      size=11.5, color=MUTED, italic=True))
    return render(os.path.join(OUT, "topologies.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_core()
    fig_inductor()
    fig_phases()
    fig_volt_second()
    fig_runaway()
    fig_topologies()
    print("figs written to", OUT)
