# -*- coding: utf-8 -*-
"""Фігури до кроку «Методи вимірювання частоти».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Два дзеркальні методи: рахуємо події в часі / час між подіями ────────
def fig_two_methods():
    W, H = 760, 430
    f = []

    # роздільник
    f.append(line(W / 2, 60, W / 2, H - 20, color="#dddddd", sw=1.5, dash="5 5"))

    # ── ЛІВО: прямий рахунок (gate time) ──
    f.append(text(190, 58, "Прямий рахунок", size=15, bold=True))
    f.append(text(190, 76, "лічимо ПОДІЇ за відоме вікно", size=11, color=MUTED))

    # вхідні імпульси (часто) на лінії y0
    y0 = 150
    f.append(line(40, y0, 350, y0, color="#cccccc", sw=1))
    n_pulses = 9
    x_start, x_end = 60, 330
    for i in range(n_pulses):
        x = x_start + (x_end - x_start) * i / (n_pulses - 1)
        f.append(line(x, y0, x, y0 - 26, color=NEG, sw=2))
        f.append(line(x, y0 - 26, x + 6, y0 - 26, color=NEG, sw=2))
        f.append(line(x + 6, y0 - 26, x + 6, y0, color=NEG, sw=2))
    f.append(text(40, y0 + 20, "вхідний сигнал (швидкий)", size=10, color=MUTED, anchor="start"))

    # вікно gate
    gy = 230
    f.append(rect(x_start - 4, gy, (x_end - x_start) + 10, 34, fill="#eef9f0",
                  stroke=FIELD, sw=2, rx=4))
    f.append(text(190, gy + 22, "вікно T (від опорного годинника)", size=11,
                  color=FIELD, bold=True))
    # стрілка довжини вікна
    f.append(line(x_start - 4, gy - 8, x_end + 6, gy - 8, color=FIELD, sw=1.5))
    f.append(text(190, gy - 14, "рівно T = 1 с", size=10, color=FIELD))

    f.append(fitbox(55, 300, 270, 44, "N подій за T  →  f = N / T",
                    size=15, fill=FILL, bold=True))
    f.append(text(190, 372, "точно на ВИСОКІЙ частоті", size=12, color=INK))
    f.append(text(190, 392, "(подій багато → ±1 майже не важить)", size=10, color=MUTED))

    # ── ПРАВО: вимірювання періоду (reciprocal) ──
    f.append(text(575, 58, "Вимірювання періоду", size=15, bold=True))
    f.append(text(575, 76, "лічимо ЧАС між двома подіями", size=11, color=MUTED))

    # дві вхідні події (рідко) на лінії
    f.append(line(420, y0, 740, y0, color="#cccccc", sw=1))
    ex1, ex2 = 470, 690
    for x in (ex1, ex2):
        f.append(line(x, y0, x, y0 - 26, color=NEG, sw=2))
        f.append(line(x, y0 - 26, x + 6, y0 - 26, color=NEG, sw=2))
        f.append(line(x + 6, y0 - 26, x + 6, y0, color=NEG, sw=2))
    f.append(text(420, y0 + 20, "вхідний сигнал (повільний)", size=10, color=MUTED, anchor="start"))
    # позначка одного періоду
    f.append(line(ex1, y0 - 40, ex2, y0 - 40, color=POS, sw=1.5))
    f.append(text((ex1 + ex2) / 2, y0 - 46, "один період T_сиг", size=10, color=POS))

    # швидкі тики опорного годинника всередині періоду
    ty = 210
    f.append(text(420, ty - 14, "тики опорного годинника f_ref:", size=10, color=MUTED, anchor="start"))
    n_ticks = 22
    for i in range(n_ticks):
        x = ex1 + (ex2 - ex1) * i / (n_ticks - 1)
        f.append(line(x, ty, x, ty + 16, color=FIELD, sw=1.4))
    f.append(text((ex1 + ex2) / 2, ty + 36, "порахували M тиків", size=11, color=FIELD, bold=True))

    f.append(fitbox(440, 300, 270, 44, "T_сиг = M / f_ref  →  f = 1 / T_сиг",
                    size=14, fill=FILL, bold=True))
    f.append(text(575, 372, "точно на НИЗЬКІЙ частоті", size=12, color=INK))
    f.append(text(575, 392, "(на один період вкладається багато тиків)", size=10, color=MUTED))

    return render(os.path.join(IMG, "two-methods.svg"), W, H, *f,
                  title="Два дзеркальні методи: рахувати події чи рахувати час")


# ── 2. Відносна похибка двох методів і перетин (де перемикатися) ────────────
def fig_crossover():
    W, H = 720, 440
    ox, oy = 80, 360
    pw, ph = 580, 290
    f = []

    # осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=2))
    f.append(text(ox + pw, oy + 30, "частота сигналу (лог) →", size=12,
                  anchor="end", color=MUTED))
    f.append(text(ox - 4, oy - ph - 6, "відносна похибка", size=12, anchor="middle", color=MUTED))
    f.append(text(ox - 4, oy - ph + 12, "(лог)", size=10, anchor="middle", color=MUTED))

    # допоміжна функція координат (логарифмічні осі, схематично)
    def X(t):  # t у [0,1] вздовж осі частот
        return ox + t * pw
    def Y(v):  # v у [0,1], більше = вища похибка (вгору)
        return oy - v * (ph - 20)

    # Прямий рахунок: похибка ~1/f при сталому T → спадає з частотою
    pts_count = []
    for i in range(81):
        t = i / 80
        v = 0.92 - 0.92 * t        # лінія вниз (у лог-лог так і виглядає 1/f)
        pts_count.append((t, max(0.05, v)))
    path = "M " + " L ".join("%.1f %.1f" % (X(t), Y(v)) for t, v in pts_count)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path, NEG))
    f.append(text(X(0.10), Y(0.86) - 8, "прямий рахунок", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(X(0.10), Y(0.86) + 10, "(похибка ≈ 1 / (f·T))", size=10, color=NEG, anchor="start"))

    # Вимірювання періоду: похибка ~f при сталому f_ref → росте з частотою
    pts_per = []
    for i in range(81):
        t = i / 80
        v = 0.05 + 0.87 * t
        pts_per.append((t, min(0.92, v)))
    path2 = "M " + " L ".join("%.1f %.1f" % (X(t), Y(v)) for t, v in pts_per)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path2, POS))
    f.append(text(X(0.90), Y(0.86) - 6, "вимір. періоду", size=12, color=POS, bold=True, anchor="end"))
    f.append(text(X(0.90), Y(0.86) + 12, "(похибка ≈ f / f_ref)", size=10, color=POS, anchor="end"))

    # точка перетину
    tc = 0.5
    vc = 0.05 + 0.87 * tc  # ≈ 0.485
    f.append(line(X(tc), oy, X(tc), Y(vc), color=MUTED, sw=1.3, dash="4 4"))
    f.append(circle(X(tc), Y(vc), 6, fill=INK, stroke=BG, sw=2))
    f.append(text(X(tc), oy + 18, "f_перетину", size=12, color=INK, bold=True))
    f.append(text(X(tc) + 10, Y(vc) - 10, "тут похибки рівні", size=11, color=INK, anchor="start"))

    # реципрокний метод — горизонтальна лінія сталої похибки
    vr = 0.20
    f.append(line(ox, Y(vr), ox + pw, Y(vr), color=FIELD, sw=2.5, dash="8 4"))
    f.append(text(ox + pw - 4, Y(vr) - 8, "реципрокний рахунок — стала похибка скрізь",
                  size=12, color=FIELD, bold=True, anchor="end"))

    # стрілки «обирай нижчу криву»
    f.append(text(X(0.5), oy - ph + 6, "на кожній частоті бери метод із меншою похибкою",
                  size=11, color=MUTED))

    return render(os.path.join(IMG, "crossover.svg"), W, H, *f,
                  title="Чому метод залежить від частоти — і де вони рівні")


# ── 3. Реципрокний рахунок: вікно «прилипає» до фронтів сигналу ─────────────
def fig_reciprocal():
    W, H = 740, 380
    f = []

    f.append(text(W / 2, 56, "Хитрість: вікно вирівнюємо по фронтах вхідного сигналу", size=14, bold=True))

    # вхідний сигнал — меандр (рідкі фронти)
    ys = 120
    f.append(text(40, ys - 24, "вхідний сигнал", size=11, color=NEG, anchor="start", bold=True))
    edges = [90, 230, 370, 510, 650]   # фронти
    # намалюємо меандр по фронтах
    lvl = ys
    prev = 60
    up = True
    seg = []
    xs = [60] + edges + [700]
    y_hi, y_lo = ys - 22, ys
    cur = y_hi
    path = "M %d %d" % (60, cur)
    for e in edges:
        path += " L %d %d" % (e, cur)
        cur = y_lo if cur == y_hi else y_hi
        path += " L %d %d" % (e, cur)
    path += " L %d %d" % (700, cur)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path, NEG))

    # вікно gate — від першого до останнього ВРАХОВАНОГО фронту
    g1, g2 = edges[0], edges[-1]
    gy = 175
    f.append(rect(g1, gy, g2 - g1, 26, fill="#eef9f0", stroke=FIELD, sw=2, rx=4))
    f.append(text((g1 + g2) / 2, gy + 18, "ворота: ціле число періодів сигналу", size=11,
                  color=FIELD, bold=True))
    # вертикалі від фронтів до воріт
    for e in (g1, g2):
        f.append(line(e, ys, e, gy, color=FIELD, sw=1.2, dash="3 3"))

    # лічильник входу
    f.append(text(40, gy + 50, "лічильник входу:", size=11, anchor="start", color=NEG))
    f.append(text(230, gy + 50, "N_сиг = 4 цілих періоди", size=11, anchor="start", color=NEG, bold=True))

    # тики опорного годинника
    ty = 255
    f.append(text(40, ty - 12, "опорний годинник f_ref (швидкий)", size=11, anchor="start", color=FIELD))
    n_ticks = 40
    for i in range(n_ticks):
        x = 60 + (700 - 60) * i / (n_ticks - 1)
        in_gate = g1 <= x <= g2
        f.append(line(x, ty, x, ty + 14, color=(FIELD if in_gate else "#cccccc"),
                      sw=1.4 if in_gate else 1))
    f.append(text(40, ty + 40, "лічильник часу:", size=11, anchor="start", color=FIELD))
    f.append(text(230, ty + 40, "M_ref тиків за ті самі ворота", size=11, anchor="start",
                  color=FIELD, bold=True))

    # підсумкова формула
    f.append(fitbox(180, 320, 380, 44,
                    "f = N_сиг · f_ref / M_ref   (ділимо два лічильники)",
                    size=14, fill=FILL, bold=True))

    return render(os.path.join(IMG, "reciprocal.svg"), W, H, *f,
                  title="Реципрокний рахунок: два лічильники за спільні ворота")


# ── 4. Звідки ±1: фаза воріт на кінцях не вирівняна з подіями ────────────────
def fig_pm_one_origin():
    """Геометричне джерело ±1: ворота не знають, де подія, тож на КОЖНОМУ
    краю губиться/додається до однієї цілої події. Для math-вставки."""
    W, H = 740, 360
    f = []

    f.append(text(W / 2, 50, "Чому ±1 неминучий: краї воріт падають МІЖ подіями", size=15, bold=True))

    # лінія подій (рівномірна решітка), ворота довільної фази зверху
    y0 = 170
    f.append(line(40, y0, 700, y0, color="#cccccc", sw=1))
    f.append(text(40, y0 + 26, "події (фронти), крок = один період", size=10,
                  color=MUTED, anchor="start"))

    # рівномірні події
    ev0, step = 92, 76
    n_ev = 9
    ev_x = [ev0 + i * step for i in range(n_ev)]
    for x in ev_x:
        f.append(line(x, y0, x, y0 - 30, color=NEG, sw=2))
        f.append(circle(x, y0 - 30, 3.2, fill=NEG, stroke=NEG, sw=1))

    # ворота: відкрилися ПІСЛЯ події k, закрилися ПЕРЕД подією m — фаза довільна
    gA = ev_x[1] + 0.42 * step          # лівий край між подіями 1 і 2
    gB = ev_x[7] + 0.30 * step          # правий край між подіями 7 і 8
    gy = 96
    f.append(rect(gA, gy, gB - gA, 30, fill="#eef9f0", stroke=FIELD, sw=2, rx=4))
    f.append(text((gA + gB) / 2, gy + 20, "ворота тривалістю T (фаза довільна)",
                  size=11, color=FIELD, bold=True))
    for gx in (gA, gB):
        f.append(line(gx, gy + 30, gx, y0, color=FIELD, sw=1.3, dash="3 3"))

    # підсвітити «спірні» події біля кожного краю
    for x, lab, dx in ((ev_x[1], "ця ледь ЗА воротами?", 0), (ev_x[7], "ця ще ВСЕРЕДИНІ?", 0)):
        f.append(circle(x, y0 - 30, 7, fill="none", stroke=POS, sw=2))
    f.append(text(ev_x[1], y0 - 46, "лівий край: рахувати чи ні?", size=9.5,
                  color=POS, anchor="middle"))
    f.append(text(ev_x[7], y0 - 46, "правий край: рахувати чи ні?", size=9.5,
                  color=POS, anchor="middle"))

    # дробова частина періоду, що «не вмістилась»
    f.append(line(ev_x[1], y0 + 8, gA, y0 + 8, color=POS, sw=2))
    f.append(text((ev_x[1] + gA) / 2, y0 + 20, "φ₁", size=11, color=POS, anchor="middle", italic=True))
    f.append(line(ev_x[7], y0 + 8, gB, y0 + 8, color=POS, sw=2))
    f.append(text((ev_x[7] + gB) / 2, y0 + 20, "φ₂", size=11, color=POS, anchor="middle", italic=True))

    # підсумок
    f.append(fitbox(150, 280, 440, 56,
                    "лічильник дає ціле число → дробові хвости φ₁, φ₂ на двох "
                    "краях\nразом дають невизначеність ровно ±1 події",
                    size=12, fill=FILL, bold=False))

    return render(os.path.join(IMG, "pm-one-origin.svg"), W, H, *f,
                  title="Геометричне джерело похибки ±1 відлік")


# ── 5. Історія: від прямого рахунку (1952) до реципрокного (1974) ────────────
def fig_history_arc():
    """Для hist-вставки. Дві віхи HP і ЧОМУ між ними 22 роки: прямий рахунок
    блискучий на радіочастоті, але сліпне на низькій; реципрокний обертає
    задачу й тримає однакову роздільність на всьому діапазоні."""
    W, H = 760, 430
    f = []

    # вісь часу
    ax_y = 96
    f.append(line(70, ax_y, W - 40, ax_y, color=INK, sw=2))
    for yr, t in (("1952", 0.0), ("1974", 1.0)):
        x = 100 + t * (W - 160)
        f.append(line(x, ax_y - 6, x, ax_y + 6, color=INK, sw=2))
        f.append(text(x, ax_y - 14, yr, size=14, color=INK, bold=True))
    f.append(text(W - 40, ax_y + 20, "час →", size=11, color=MUTED, anchor="end"))

    # ── ЛІВО: HP 524A, прямий рахунок ──
    x0 = 100
    box1 = textbox(x0 + 70, 160, "HP 524A · прямий рахунок", size=12, bold=True,
                   fill="#eef2ff", stroke=NEG, color=NEG)
    f.append(box1[0])
    f.append(text(x0 + 70, 200, "масштабовані швидкі імпульси", size=10.5, color=MUTED))
    f.append(text(x0 + 70, 216, "→ повільний накопичувач", size=10.5, color=MUTED))
    f.append(text(x0 + 70, 232, "вибірна часова база", size=10.5, color=MUTED))
    # сильна сторона / слабка
    f.append(text(x0 + 70, 264, "радіостанція за ~1 с", size=11, color=FIELD, bold=True))
    f.append(text(x0 + 70, 280, "(а було ~10 хв)", size=10, color=FIELD))
    f.append(text(x0 + 70, 312, "АЛЕ на низькій частоті", size=11, color=POS, bold=True))
    f.append(text(x0 + 70, 328, "подій замало → число грубшає", size=10, color=POS))

    # ── ПРАВО: HP 5345A, реципрокний рахунок ──
    x1 = W - 240
    box2 = textbox(x1 + 70, 160, "HP 5345A · реципрокний", size=12, bold=True,
                   fill="#eafaf0", stroke=FIELD, color=FIELD)
    f.append(box2[0])
    f.append(text(x1 + 70, 200, "міряє ПЕРІОД і обертає його", size=10.5, color=MUTED))
    f.append(text(x1 + 70, 216, "50 мкГц … 500 МГц", size=10.5, color=MUTED))
    f.append(text(x1 + 70, 232, "9 розрядів на всьому діапазоні", size=10.5, color=MUTED))
    f.append(text(x1 + 70, 264, "1 Гц за 1 с — навіть унизу", size=11, color=FIELD, bold=True))
    f.append(text(x1 + 70, 280, "(низькі частоти РОЗВ'ЯЗАНО)", size=10, color=FIELD))

    # стрілка переходу з підписом-проблемою
    f.append(arrow(x0 + 150, 160, x1 - 12, 160, color=INK, sw=2))
    gap = textbox((x0 + x1 + 140) / 2, 118,
                  "22 роки: як НЕ втратити роздільність унизу?",
                  size=11, bold=True, fill="#fff8e1", stroke="#b8860b", color="#7a5c00")
    f.append(gap[0])

    # нижній підсумок
    f.append(fitbox(120, 364, W - 240, 46,
                    "та сама рівність f = 1/T — спершу прочитана «рахуй події», "
                    "згодом «міряй період і обертай»",
                    size=12, fill=FILL, bold=False))

    return render(os.path.join(IMG, "history-arc.svg"), W, H, *f,
                  title="Дві віхи HP: чому реципрокний рахунок чекав 22 роки")


if __name__ == "__main__":
    fig_two_methods()
    fig_crossover()
    fig_reciprocal()
    fig_pm_one_origin()
    fig_history_arc()
    print("OK: 5 figures written to", IMG)
