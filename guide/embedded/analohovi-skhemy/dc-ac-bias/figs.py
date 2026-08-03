# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «DC-зміщення і AC-сигнал у підсилювачі» (guide/embedded/kola).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def node(x, y):
    return '<circle cx="%.1f" cy="%.1f" r="3.0" fill="%s"/>' % (x, y, INK)


def res_v(x, y, h=46, label="", side="right"):
    out = [rect(x - 8, y, 16, h, fill="#eef1f5", stroke=INK, sw=1.5, rx=3)]
    if label:
        if side == "right":
            out.append(text(x + 14, y + h / 2 + 4, label, size=11, anchor="start"))
        else:
            out.append(text(x - 14, y + h / 2 + 4, label, size=11, anchor="end"))
    return "".join(out), y, y + h


def sine(left, right, base, amp, periods, color, sw=2.2, clip_lo=None, clip_hi=None, phase=0.0):
    """Синус від left до right навколо рівня base. Повертає path-фрагмент."""
    pts = []
    N = 140
    for i in range(N + 1):
        t = i / N
        xx = left + t * (right - left)
        yy = base - amp * math.sin(t * 2 * math.pi * periods + phase)
        if clip_lo is not None and yy > clip_lo:
            yy = clip_lo
        if clip_hi is not None and yy < clip_hi:
            yy = clip_hi
        pts.append((xx, yy))
    d = "M" + " L".join("%.1f %.1f" % p for p in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ── фігура 1: DC ставить рівень, AC гойдається довкола нього ──────────────────
def fig_bias_plus_signal():
    W, H = 827, 396
    f = [text(W / 2, 26, "Постійне зміщення ставить рівень спокою, сигнал лише гойдається довкола нього",
              size=15, bold=True)]

    # ── ліва панель: маленький вхідний сигнал на базі ──
    lt, lb = 70, 200
    ll, lr = 60, 330
    base_in = (lt + lb) / 2
    amp_in = 16
    f.append(text((ll + lr) / 2, lt - 12, "вхід (база)", size=12, bold=True))
    # рівень зміщення бази
    f.append(line(ll, base_in, lr, base_in, color=FIELD, sw=1.4, dash="5,4"))
    f.append(text(lr + 6, base_in + 4, "U_b (зміщення)", size=10, color=FIELD, anchor="start"))
    f.append(sine(ll + 8, lr - 90, base_in, amp_in, 2, NEG))
    f.append(text((ll + lr) / 2 - 30, lb + 26, "малий сигнал ±кілька мВ", size=10, color=NEG))

    # стрілка переходу
    f.append(arrow(lr + 70, base_in, lr + 120, base_in, color=INK, sw=2))
    f.append(text(lr + 95, base_in - 10, "×A", size=13, bold=True))
    f.append(text(lr + 95, base_in + 22, "підсилювач", size=10, color=MUTED))

    # ── права панель: великий вихід на колекторі, інвертований, довкола Q ──
    rl, rr = 470, 760
    rtop, rbot = 60, 330
    vcc_y = rtop + 8
    gnd_y = rbot - 8
    q_y = (vcc_y + gnd_y) / 2
    amp_out = (q_y - vcc_y) * 0.78
    f.append(text((rl + rr) / 2, rtop - 12, "вихід (колектор)", size=12, bold=True))
    # рейки
    f.append(line(rl, vcc_y, rr, vcc_y, color=POS, sw=1.4, dash="5,4"))
    f.append(text(rl - 6, vcc_y + 4, "Vcc", size=10, color=POS, anchor="end"))
    f.append(line(rl, gnd_y, rr, gnd_y, color=INK, sw=1.6))
    f.append(text(rl - 6, gnd_y + 4, "0", size=10, anchor="end"))
    # робоча точка Q
    f.append(line(rl, q_y, rr, q_y, color=FIELD, sw=1.6, dash="5,4"))
    f.append(text(rr + 6, q_y + 4, "Q ≈ Vcc/2", size=10, color=FIELD, anchor="start"))
    # вихід — інвертований (phase=pi), велика амплітуда
    f.append(sine(rl + 8, rr - 8, q_y, amp_out, 2, POS, phase=math.pi))
    # позначити розмах
    f.append(line(rr - 40, q_y - amp_out, rr - 40, q_y + amp_out, color=MUTED, sw=1.0, dash="2,3"))
    f.append(text(rr - 34, q_y, "великий розмах", size=10, color=MUTED, anchor="start"))

    # підпис унизу
    note = ("Зміщення (DC) піднімає робочу точку в середину діапазону — туди, звідки є місце гойдатися вгору й вниз.\n"
            "Сигнал (AC) — маленьке коливання довкола цієї точки; підсилювач робить його великим, але рівень спокою лишає на місці.")
    f.append(fitbox(60, gnd_y + 22, 700, 40, note, size=10.5, fill="#f0f7f1", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "bias-plus-signal.svg"), W, H, *f)


# ── фігура 2: суперпозиція — два погляди на одну схему ────────────────────────
def fig_superposition():
    W, H = 820, 440
    f = [text(W / 2, 26, "Одна схема — два окремі розрахунки: спершу постійка (де стоїть Q), потім сигнал (яке підсилення)",
              size=14, bold=True)]

    def stage(ox, title, mode, boxfill, boxstroke):
        # рамка-заголовок
        f.append(fitbox(ox, 56, 320, 30, title, size=12.5, bold=True,
                        fill=boxfill, stroke=boxstroke, color=INK))
        vcc_y = 110
        gnd_y = 360
        bx = ox + 60          # колонка бази
        cx = ox + 210         # колонка колектора
        # рейка Vcc / для AC — теж земля
        rail_col = POS if mode == "dc" else INK
        rail_txt = "Vcc" if mode == "dc" else "Vcc→0 (земля для AC)"
        f.append(line(ox + 20, vcc_y, ox + 300, vcc_y, color=rail_col, sw=2))
        f.append(text(ox + 160, vcc_y - 8, rail_txt, size=10,
                      color=(POS if mode == "dc" else MUTED)))
        f.append(line(ox + 20, gnd_y, ox + 300, gnd_y, color=INK, sw=2))

        # резистори бази (дільник) Rb1 зверху, Rb2 знизу
        sr, t1, b1 = res_v(bx, vcc_y + 14, 50, "Rb1", side="left")
        f.append(sr); f.append(line(bx, vcc_y, bx, t1, color=INK, sw=1.5))
        midb = b1 + 30
        sr, t2, b2 = res_v(bx, midb + 6, 50, "Rb2", side="left")
        f.append(sr)
        f.append(line(bx, b1, bx, midb, color=INK, sw=1.5))
        f.append(line(bx, b2, bx, gnd_y, color=INK, sw=1.5))
        f.append(node(bx, midb))
        # Rc зверху на колекторі
        src, tc, bc = res_v(cx, vcc_y + 14, 60, "Rc", side="right")
        f.append(src); f.append(line(cx, vcc_y, cx, tc, color=INK, sw=1.5))

        # транзистор як кружок із буквою (схематично), емітер на землю
        ty = midb            # рівень бази ≈ рівень символу
        f.append(circle(cx, ty + 36, 16, fill=BG, stroke=INK, sw=1.6))
        f.append(text(cx, ty + 41, "Q", size=12, bold=True))
        # база → транзистор
        f.append(line(bx, midb, cx - 16, ty + 36, color=INK, sw=1.5))
        # колектор-вузол
        f.append(line(cx, bc, cx, ty + 20, color=INK, sw=1.5))
        f.append(node(cx, bc))
        # емітер на землю
        f.append(line(cx, ty + 52, cx, gnd_y, color=INK, sw=1.5))

        if mode == "dc":
            # конденсатори — РОЗРИВ: малюємо «обрізаний» вхід і вихід
            f.append(text(ox - 6, midb, "вхід", size=10, color=MUTED, anchor="end"))
            # розрив на вході (дві планки + хрестик розриву)
            f.append(line(ox - 2, midb, ox + 18, midb, color=INK, sw=1.5))
            f.append(line(ox + 18, midb - 9, ox + 18, midb + 9, color=INK, sw=2.2))
            f.append(line(ox + 30, midb - 9, ox + 30, midb + 9, color=INK, sw=2.2))
            f.append(text(ox + 24, midb - 16, "розрив", size=9, color=MUTED))
            f.append(line(ox + 30, midb, bx, midb, color=INK, sw=1.5))
            # вихід — теж розрив
            f.append(line(cx, bc, cx + 26, bc, color=INK, sw=1.5))
            f.append(line(cx + 26, bc - 9, cx + 26, bc + 9, color=INK, sw=2.2))
            f.append(line(cx + 38, bc - 9, cx + 38, bc + 9, color=INK, sw=2.2))
            # підсумок DC
            f.append(fitbox(ox + 20, gnd_y + 16, 290, 56,
                            "Знаходимо: U_b на базі (дільник),\nструм спокою I_C, напругу на колекторі\nU_C = Vcc − I_C·Rc  →  це робоча точка Q",
                            size=10, fill="#eef1f5", stroke=MUTED, color=INK))
        else:
            # конденсатори — КОРОТКЕ (дріт): сигнал заходить і виходить
            f.append(text(ox - 6, midb, "Vin~", size=10, color=NEG, anchor="end", bold=True))
            f.append(line(ox - 2, midb, bx, midb, color=NEG, sw=1.8))
            # вихід — дріт
            f.append(line(cx, bc, cx + 40, bc, color=POS, sw=1.8))
            f.append(text(cx + 44, bc + 4, "Vout~", size=10, color=POS, anchor="start", bold=True))
            # Rb1, Rb2, Vcc усі «на землі» для AC → паралель
            f.append(text(ox + 160, vcc_y + 8, "для AC верх Rb1 і Rc — на землі", size=9, color=MUTED))
            f.append(fitbox(ox + 20, gnd_y + 16, 290, 56,
                            "Знаходимо: підсилення A ≈ −Rc / r_e,\nвхідний і вихідний опір, смугу.\nРобочу точку тут НЕ чіпаємо.",
                            size=10, fill="#f0f7f1", stroke=FIELD, color=INK))

    stage(40, "1) ПОСТІЙКА (DC): конденсатори — розрив", "dc", "#eef1f5", MUTED)
    f.append(line(W / 2, 60, W / 2, 420, color=MUTED, sw=1.2, dash="4,4"))
    stage(460, "2) ЗМІННА (AC): конденсатори — коротке", "ac", "#f0f7f1", FIELD)

    render(os.path.join(IMG, "superposition.svg"), W, H, *f)


# ── фігура 3: навантажувальна пряма й вибір Q посередині ──────────────────────
def fig_load_line():
    W, H = 760, 360
    f = [text(W / 2, 24, "Чому Q ставлять посередині: симетричний запас угору й униз дає найбільший неспотворений сигнал",
              size=13, bold=True)]

    # осі: X — напруга на колекторі U_CE (0..Vcc), Y — струм колектора I_C
    ox, oy = 95, 290      # початок координат (лівий низ)
    ax_w, ax_h = 540, 230
    f.append(arrow(ox, oy, ox, oy - ax_h - 10, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox + ax_w + 10, oy, color=INK, sw=1.6))
    f.append(text(ox - 10, oy - ax_h - 2, "I_C", size=12, anchor="end", bold=True))
    f.append(text(ox + ax_w + 12, oy + 16, "U_CE", size=12, anchor="start", bold=True))
    f.append(text(ox - 8, oy + 16, "0", size=10, anchor="end"))
    f.append(text(ox + ax_w, oy + 16, "Vcc", size=10, anchor="middle", color=POS))

    x_vcc = ox + ax_w
    y_imax = oy - ax_h

    def online(frac):
        """координати точки навантажувальної прямої за часткою U_CE від 0 до Vcc."""
        return ox + frac * ax_w, oy - (1 - frac) * ax_h

    # навантажувальна пряма від (0, Imax) до (Vcc, 0)
    f.append(line(ox, y_imax, x_vcc, oy, color=MUTED, sw=2.0))
    f.append(text(ox + 138, y_imax + 20, "навантажувальна пряма (Rc)", size=11, color=MUTED))

    def qpoint(frac, color, label, lab_dx):
        qx, qy = online(frac)
        # запас по обидва боки в частках Vcc; розмах = найменший із двох (симетрія)
        sw_frac = min(frac, 1 - frac) * 0.85
        ax_, ay_ = online(frac - sw_frac)   # лівий край коливання (менша U_CE)
        bx_, by_ = online(frac + sw_frac)   # правий край (більша U_CE)
        # жирний відрізок коливання ПРЯМО на навантажувальній прямій
        f.append(line(ax_, ay_, bx_, by_, color=color, sw=5))
        # пунктир-проєкції країв на вісь U_CE — наочно межі розмаху
        f.append(line(ax_, ay_, ax_, oy, color=color, sw=1.0, dash="3,3"))
        f.append(line(bx_, by_, bx_, oy, color=color, sw=1.0, dash="3,3"))
        # сама точка Q
        f.append(circle(qx, qy, 6, fill=color, stroke=INK, sw=1.5))
        f.append(text(qx + lab_dx, qy - 10, label, size=11, bold=True, color=color, anchor="middle"))
        return qx, qy

    # Q зсунуте до Vcc — поганий вибір (малий запас праворуч → ранній зріз)
    qpoint(0.78, POS, "Q зле (біля Vcc)", 40)
    # Q посередині — добрий вибір (рівний великий запас)
    qpoint(0.5, FIELD, "Q добре (середина)", -50)

    # легенда внизу
    f.append(fitbox(ox, oy + 30, 250, 30, "товстий відрізок = розмах сигналу без зрізу",
                    size=10, fill="#f0f7f1", stroke=FIELD, color=INK))
    f.append(fitbox(ox + 290, oy + 30, 250, 30, "зсунута Q → запас затиснутий з одного боку",
                    size=10, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "load-line.svg"), W, H, *f)


# ── фігура 4 (до вставки hist): класи A/B/C — це просто де сидить зміщення ─────
def fig_bias_classes():
    """Три панелі: та сама синусоїда на вході, але рівень зміщення (поріг відсічки)
    сидить у різних місцях → прилад проводить різну частку періоду. Це і є класи."""
    W, H = 976, 340
    f = [text(W / 2, 24, "Класи підсилення — це лише різна висота зміщення: скільки періоду прилад узагалі проводить",
              size=13.5, bold=True)]

    panel_w = 250
    gap = 15
    x0 = 20
    top = 70
    bot = 250
    mid = (top + bot) / 2
    amp = (bot - top) / 2 * 0.92

    def panel(ox, title, thr_frac, sub, tcol):
        # thr_frac: положення порога відсічки в частках амплітуди від середини,
        #   +1 = поріг угорі (проводить лише вершечок), 0 = посередині, -1 = унизу (весь період).
        left = ox + 20
        right = ox + panel_w - 12
        # рамка-заголовок
        f.append(fitbox(ox, 40, panel_w, 24, title, size=12, bold=True,
                        fill="#eef1f5", stroke=tcol, color=INK))
        # вісь часу (нульова лінія сигналу вже НЕ головна — головний поріг)
        thr_y = mid - thr_frac * amp     # рівень порога відсічки (де прилад «оживає»)
        # заштрихована зона провідності (над порогом = прилад відкритий)
        f.append(rect(left, top - 6, right - left, thr_y - (top - 6),
                      fill="#eaf3ec", stroke="none"))
        f.append(line(left, thr_y, right, thr_y, color=FIELD, sw=1.6, dash="5,3"))
        f.append(text(right, thr_y - 5, "поріг", size=9, color=FIELD, anchor="end"))
        # повна вхідна синусоїда (тонка, сіра) — щоб видно, що вхід той самий
        f.append(sine(left, right, mid, amp, 1.5, MUTED, sw=1.3))
        # частина, що ПРОВОДИТЬ (жирна, кольорова) — синус, обрізаний знизу порогом
        f.append(sine(left, right, mid, amp, 1.5, tcol, sw=3.0, clip_lo=thr_y))
        # підпис-частка провідності
        f.append(text(ox + panel_w / 2, bot + 22, sub, size=10.5, color=tcol, bold=True))

    panel(x0,                 "Клас A", -1.0,
          "проводить весь період (360°)", FIELD)
    panel(x0 + panel_w + gap, "Клас B",  0.0,
          "проводить половину (180°)", POS)
    panel(x0 + 2 * (panel_w + gap), "Клас C", 0.45,
          "проводить менше половини (<180°)", NEG)

    note = ("Вхід (сірий) усюди однаковий. Змінюємо тільки одне — рівень зміщення, тобто де стоїть поріг відсічки (зелений пунктир).\n"
            "Опустиш поріг під сигнал — прилад відкритий завжди (клас A, чисто, але марнотратно). Піднімеш до середини — лише півперіод (клас B, "
            "удвічі ощадніше, треба другого в пару). Ще вище — лише вершечки (клас C, найощадніше, для радіопередавачів). Один параметр — уся родина класів.")
    f.append(fitbox(x0, bot + 34, W - 2 * x0, 44, note, size=10, fill="#f6f7f9",
                    stroke=MUTED, color=INK))

    render(os.path.join(IMG, "bias-classes.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bias_plus_signal()
    print("OK: img/bias-plus-signal.svg")
    fig_superposition()
    print("OK: img/superposition.svg")
    fig_load_line()
    print("OK: img/load-line.svg")
    fig_bias_classes()
    print("OK: img/bias-classes.svg")
