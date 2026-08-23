# -*- coding: utf-8 -*-
"""Фігури теми «Фільтр Калмана». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def _gauss(mu, sigma, x):
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def _curve(mu, sigma, lo, hi, X, Ybase, Yamp, n=160):
    """Точки дзвону Гаусса в екранних координатах (нормований на 1 у піку)."""
    pts = []
    for i in range(n + 1):
        x = lo + (hi - lo) * i / n
        g = _gauss(mu, sigma, x)
        pts.append((X(x), Ybase - Yamp * g))
    return pts


# ── Фігура 1: корекція = добуток двох дзвонів ────────────────────────────────
# Передбачення (широкий синій дзвін) і вимір (червоний). Нова оцінка — їхній
# ДОБУТОК (зелений): лежить МІЖ ними, ближче до впевненішого, і ВУЖЧА за обидва.
# Це й є суть кроку «виправ» у Калмані — перемноження двох Гауссів.
def fig_fuse_gaussians():
    W, H = 720, 360
    L, R = 60, 690
    B = 300
    parts = []

    lo, hi = 0.0, 10.0
    def X(v):
        return L + (R - L) * (v - lo) / (hi - lo)

    # осі
    parts.append(line(L, B, R, B, color=MUTED, sw=1.5))
    parts.append(text((L + R) / 2, B + 28, "оцінювана величина (напр. кут)  →",
                      size=12, color=MUTED))

    # передбачення — широке (невпевнене), вимір — вужче (точніший давач)
    mu_p, s_p = 3.8, 1.7
    mu_z, s_z = 6.6, 1.05
    amp = 200

    # добуток двох Гауссів — теж Гаусс: дисперсії складаються як «паралельні опори»
    var_p, var_z = s_p ** 2, s_z ** 2
    var_n = 1.0 / (1.0 / var_p + 1.0 / var_z)
    s_n = math.sqrt(var_n)
    mu_n = var_n * (mu_p / var_p + mu_z / var_z)

    def draw(mu, s, color, sw, dash=None):
        pts = _curve(mu, s, lo, hi, X, B, amp)
        path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                     % (path, color, sw, d))

    draw(mu_p, s_p, NEG, 2.4, dash="7 5")
    draw(mu_z, s_z, POS, 2.4, dash="7 5")
    draw(mu_n, s_n, FIELD, 3.0)

    # вертикалі-піки
    for mu, color in ((mu_p, NEG), (mu_z, POS), (mu_n, FIELD)):
        g = 1.0
        parts.append(line(X(mu), B, X(mu), B - amp * g, color=color, sw=1, dash="2 4"))

    # підписи
    parts.append(text(X(mu_p), B - amp - 8, "передбачення", size=12, color=NEG))
    parts.append(text(X(mu_p), B - amp + 12, "(широке — мало довіри)", size=10, color=NEG))
    parts.append(text(X(mu_z), B - amp - 8, "вимір давача", size=12, color=POS))
    parts.append(text(X(mu_z), B - amp + 12, "(вужче — точніше)", size=10, color=POS))
    parts.append(text(X(mu_n) - 4, B - amp * _gauss(mu_n, s_n, mu_n) - 12,
                      "нова оцінка", size=13, color=FIELD, bold=True))

    # стрілка: нова оцінка ВУЖЧА за обидві
    parts.append(text((L + R) / 2, 36,
                      "добуток двох дзвонів — вужчий за кожен: знаємо ТОЧНІШЕ, ніж кожне джерело окремо",
                      size=12, color=INK))

    render(os.path.join(IMG, "fuse-gaussians.svg"), W, H, *parts,
           title="Виправ = перемнож передбачення на вимір")


# ── Фігура 2: підсилення Калмана як повзунок довіри ──────────────────────────
# K — одне число від 0 до 1, що його фільтр РАХУЄ САМ щотакту. Ліворуч (K→0):
# вимір шумний / модель певна — майже не рухаємось. Праворуч (K→1): вимір
# точний / модель непевна — стрибаємо до виміру. Формула знизу.
def fig_gain_slider():
    W, H = 720, 330
    L, R = 90, 630
    yb = 150
    parts = []

    # смуга-повзунок
    parts.append(line(L, yb, R, yb, color=MUTED, sw=3))
    parts.append(circle(L, yb, 6, fill=NEG, stroke=NEG, sw=1))
    parts.append(circle(R, yb, 6, fill=POS, stroke=POS, sw=1))
    # бігунок десь усередині
    kx = L + (R - L) * 0.42
    parts.append(circle(kx, yb, 12, fill=FIELD, stroke=INK, sw=2))
    parts.append(text(kx, yb - 22, "K", size=16, bold=True, color=FIELD))
    parts.append(text(kx, yb + 30, "фільтр рахує сам", size=11, color=FIELD))

    # кінці
    parts.append(text(L, yb - 22, "K = 0", size=14, bold=True, color=NEG))
    parts.append(text(R, yb - 22, "K = 1", size=14, bold=True, color=POS))

    # пояснення кінців — рамки
    parts.append(fitbox(30, 190, 300, 86,
                 "K → 0: ВІРИМО ПЕРЕДБАЧЕННЮ.\nВимір шумний АБО модель\nвпевнена → майже не\nрухаємо оцінку.",
                 size=12, fill="#eaf0fd", stroke=NEG))
    parts.append(fitbox(390, 190, 300, 86,
                 "K → 1: ВІРИМО ВИМІРУ.\nВимір точний АБО модель\nрозпливлась → стрибаємо\nдо показу давача.",
                 size=12, fill="#fdecea", stroke=POS))

    # формула підсилення
    parts.append(text(W / 2, 300,
                      "K = непевність передбачення / (непевність передбачення + шум виміру)",
                      size=13, color=INK))

    render(os.path.join(IMG, "gain-slider.svg"), W, H, *parts,
           title="Підсилення Калмана: повзунок довіри, що рухається сам")


# ── Фігура 3: цикл непевності ────────────────────────────────────────────────
# Стан фільтра — оцінка + її непевність (ширина дзвону). ПЕРЕДБАЧ розширює
# дзвін (модель додає шум), ВИПРАВ звужує (вимір додає знання). Замкнене
# коло, де ширина дихає: росте на передбаченні, спадає на корекції.
def fig_uncertainty_cycle():
    W, H = 720, 360
    cx, cy = 360, 195
    parts = []

    # чотири вузли по колу
    nodes = [
        (360, 70,  "СТАН\nоцінка x̂ + непевність P", FIELD),
        (600, 195, "ПЕРЕДБАЧ\nx̂ ← модель(x̂)\nP ← P + Q  (росте)", NEG),
        (360, 320, "ВИМІР z\nприйшов з давача\nшум R", POS),
        (120, 195, "ВИПРАВ\nx̂ ← x̂ + K·(z − x̂)\nP ← (1−K)·P  (спадає)", FIELD),
    ]
    boxes = []
    for (x, y, s, col) in nodes:
        b = fitbox(x - 105, y - 34, 210, 68, s, size=11.5, bold=True,
                   fill="#ffffff", stroke=col)
        parts.append(b)
        boxes.append((x, y))

    # стрілки по колу за годинниковою
    def ring(a, b, color):
        (x1, y1), (x2, y2) = boxes[a], boxes[b]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx, sy = x1 + ux * 112, y1 + uy * 44
        ex, ey = x2 - ux * 112, y2 - uy * 44
        parts.append(arrow(sx, sy, ex, ey, color=color, sw=2.0))

    ring(0, 1, MUTED)
    ring(1, 2, MUTED)
    ring(2, 3, MUTED)
    ring(3, 0, MUTED)

    # підписи дихання непевності біля відповідних дуг
    parts.append(text(545, 110, "P росте", size=12, color=NEG, bold=True))
    parts.append(text(175, 110, "P спадає", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "uncertainty-cycle.svg"), W, H, *parts,
           title="Цикл Калмана: непевність дихає — росте, тоді спадає")


# ── Фігура 4: дві змінні стану — величина і її сталий зсув ───────────────────
# Скалярний фільтр оцінює одну величину. Та сама модель з ДРУГОЮ змінною —
# повільним зсувом нуля давача (bias) — сама його ловить і віднімає, бо зсув
# рухається інакше, ніж корисний сигнал. Показуємо два «треки» стану.
def fig_two_states():
    W, H = 720, 360
    parts = []

    # ліворуч — один стан, праворуч — два стани
    parts.append(fitbox(40, 70, 280, 120,
                 "ОДНА ЗМІННА\n\nx̂ — оцінка величини\nP — її непевність\n\n"
                 "сталий зсув давача\nпотрапляє ПРЯМО в x̂\n→ оцінка зміщена",
                 size=12.5, fill="#fdecea", stroke=POS, bold=False))

    parts.append(fitbox(400, 70, 280, 120,
                 "ДВІ ЗМІННІ\n\nx̂ — оцінка величини\nb̂ — оцінка зсуву нуля\nP — матриця 2×2\n\n"
                 "фільтр САМ ділить вимір\nна сигнал і зсув",
                 size=12.5, fill="#eaf6ee", stroke=FIELD, bold=False))

    # стрілка переходу
    parts.append(arrow(326, 130, 394, 130, color=INK, sw=2.2))
    parts.append(text(360, 118, "+b̂", size=13, bold=True, color=FIELD))

    # знизу — модель руху двох змінних
    parts.append(text(W / 2, 232, "модель руху двох змінних за такт:", size=13, bold=True, color=INK))
    parts.append(fitbox(120, 250, 480, 80,
                 "величина дрейфує:   x ← x          (+ шум процесу Qx — великий)\n"
                 "зсув майже сталий:  b ← b          (+ шум процесу Qb — крихітний)\n"
                 "вимір бачить суму:  z = (x + b) + шум R",
                 size=12, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG, "two-states.svg"), W, H, *parts,
           title="Друга змінна стану: онлайн-оцінка зсуву нуля (bias)")


# ── Фігура 5: ворота за нев'язкою + сторожа розходження ──────────────────────
# Кожен вимір спершу проходить ВОРОТА: якщо нев'язка |z−x̂| більша за кілька
# сигм очікуваного розкиду — це викид, корекцію пропускаємо. Якщо ж нев'язка
# ЗАВЖДИ в один бік — фільтр розходиться, треба бити на сполох.
def fig_innovation_gate():
    W, H = 720, 380
    parts = []

    # вхід
    parts.append(textbox(105, 60, "вимір z", size=13, bold=True, fill="#fff", stroke=INK)[0])

    # обчислення нев'язки
    parts.append(fitbox(30, 110, 150, 64,
                 "нев'язка\ny = z − x̂\nрозкид S = P + R",
                 size=12, fill="#f4f6f8", stroke=MUTED, bold=False))
    parts.append(arrow(105, 78, 105, 108, color=INK, sw=2))

    # ромб-ворота
    cx, cy = 105, 230
    hw = 90
    parts.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
                 'fill="#fff7e6" stroke="%s" stroke-width="2"/>'
                 % (cx, cy - 46, cx + hw, cy, cx, cy + 46, cx - hw, cy, INK))
    parts.append(mtext(cx, cy - 6, ["y² < g²·S ?", "(g ≈ 3 сигми)"], size=11.5, bold=True))
    parts.append(arrow(105, 174, 105, cy - 46, color=INK, sw=2))

    # гілка ТАК → корекція
    parts.append(arrow(cx + hw, 230, 250, 230, color=FIELD, sw=2.2))
    parts.append(text(222, 218, "так", size=12, bold=True, color=FIELD))
    parts.append(fitbox(250, 198, 230, 64,
                 "КОРЕКЦІЯ\nx̂ ← x̂ + K·y\nP ← (1−K)·P",
                 size=12, fill="#eaf6ee", stroke=FIELD, bold=False))

    # гілка НІ → відкинути викид
    parts.append(arrow(105, 276, 105, 312, color=POS, sw=2.2))
    parts.append(text(135, 298, "ні — викид", size=12, bold=True, color=POS))
    parts.append(fitbox(30, 312, 230, 56,
                 "ПРОПУСТИТИ вимір\n(корекції немає, лише\nросте P далі)",
                 size=11.5, fill="#fdecea", stroke=POS, bold=False))

    # сторожа розходження — окремий блок праворуч-знизу
    parts.append(fitbox(250, 290, 450, 78,
                 "СТОРОЖА РОЗХОДЖЕННЯ: стеж за нев'язкою y у часі.\n"
                 "y скаче навколо нуля → фільтр здоровий.\n"
                 "y стало в один бік або |y| росте → Q/R погані, фільтр повзе геть.",
                 size=11.5, fill="#eef2ff", stroke=NEG, bold=False))

    render(os.path.join(IMG, "innovation-gate.svg"), W, H, *parts,
           title="Захист: ворота на викид + сторожа за нев'язкою")


# ── Фігура: дисперсія оцінки P(K) — парабола з мінімумом (вставка math) ───────
# P(K) = (1−K)²·P⁻ + K²·R. Доданок передбачення спадає з K, доданок виміру
# росте; їхня сума — парабола вітками вгору з єдиним мінімумом при
# K* = P⁻/(P⁻+R). Саме абсциса дна — оптимальне підсилення Калмана.
def fig_gain_parabola():
    W, H = 720, 410
    L, Rx = 80, 660
    T, B = 60, 312
    parts = []

    Pm = 0.6   # P⁻ (непевність передбачення)
    Rr = 0.4   # R  (шум виміру)
    Kstar = Pm / (Pm + Rr)

    def term_pred(K):
        return (1 - K) ** 2 * Pm

    def term_meas(K):
        return K ** 2 * Rr

    def total(K):
        return term_pred(K) + term_meas(K)

    ymax = max(term_pred(0), term_meas(1), total(0), total(1)) * 1.14

    def X(k):
        return L + (Rx - L) * k

    def Y(v):
        return B - (B - T) * (v / ymax)

    # осі
    parts.append(line(L, B, Rx, B, color=MUTED, sw=1.5))
    parts.append(line(L, B, L, T, color=MUTED, sw=1.5))
    parts.append(text((L + Rx) / 2, B + 34,
                      "підсилення K   (0 = вірю собі · 1 = вірю давачу)  →",
                      size=12, color=MUTED))
    parts.append(text(L - 6, T - 14, "дисперсія похибки оцінки  P",
                      size=12, color=MUTED, anchor="start"))
    for k, lab in ((0.0, "0"), (1.0, "1")):
        parts.append(line(X(k), B, X(k), B + 5, color=MUTED, sw=1.2))
        parts.append(text(X(k), B + 20, lab, size=11, color=MUTED))

    def curve(fn, color, sw, dash=None, n=120):
        pts = [(X(i / n), Y(fn(i / n))) for i in range(n + 1)]
        path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                     % (path, color, sw, d))

    curve(term_pred, NEG, 2.0, dash="7 5")
    curve(term_meas, POS, 2.0, dash="7 5")
    curve(total, FIELD, 3.0)

    # вертикаль у мінімумі + точка дна
    ymin = total(Kstar)
    parts.append(line(X(Kstar), B, X(Kstar), Y(ymin), color=INK, sw=1.2, dash="3 4"))
    parts.append(circle(X(Kstar), Y(ymin), 6, fill=FIELD, stroke=INK, sw=2))

    # підписи кривих
    parts.append(text(X(0.06), Y(term_pred(0.06)) - 10,
                      "(1−K)²·P⁻", size=12, color=NEG, anchor="start"))
    parts.append(text(X(0.10), Y(term_pred(0.10)) + 16,
                      "довіра моделі", size=10, color=NEG, anchor="start"))
    parts.append(text(X(0.94), Y(term_meas(0.94)) - 10,
                      "K²·R", size=12, color=POS, anchor="end"))
    parts.append(text(X(0.88), Y(term_meas(0.88)) + 16,
                      "довіра давачу", size=10, color=POS, anchor="end"))
    parts.append(text(X(0.5), Y(total(0.5)) - 14,
                      "сума  P(K)", size=13, color=FIELD, bold=True))

    # підпис оптимуму під віссю
    parts.append(fitbox(X(Kstar) - 100, B + 46, 200, 44,
                 "мінімум похибки\nK* = P⁻ / (P⁻ + R)",
                 size=12.5, bold=True, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, "gain-parabola.svg"), W, H, *parts,
           title="Підсилення Калмана = дно параболи похибки")


if __name__ == "__main__":
    fig_fuse_gaussians()
    fig_gain_slider()
    fig_uncertainty_cycle()
    fig_two_states()
    fig_innovation_gate()
    fig_gain_parabola()
    print("OK: 6 figures ->", IMG)
