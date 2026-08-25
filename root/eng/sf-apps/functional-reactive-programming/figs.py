# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Поведінка (неперервний час) проти Події (дискретні спалахи) ───────
def fig_behavior_vs_event():
    W, H = 820, 360
    parts = []
    parts.append(text(W / 2, 28, "Два способи опису часу в FRP: Поведінка та Подія", size=16, bold=True))

    xL, xR = 170, 770

    # Верхня половина — Поведінка B(t): неперервне значення в будь-який момент
    y_b_axis = 120
    parts.append(text(85, y_b_axis - 20, "Поведінка B(t)", size=14, bold=True, color=NEG))
    parts.append(text(85, y_b_axis, "B: Час → Значення", size=11, color=MUTED))
    parts.append(text(85, y_b_axis + 18, "(неперервна функція)", size=10, color=MUTED))

    # Вісь часу B
    parts.append(line(xL, y_b_axis, xR, y_b_axis, color=INK, sw=1.5))
    parts.append(arrow(xR - 4, y_b_axis, xR + 10, y_b_axis, color=INK))
    parts.append(text(xR + 22, y_b_axis + 4, "t", size=13, italic=True))

    # Неперервна крива B(t)
    curve_pts = [
        (180, 110), (240, 75), (320, 135), (410, 65), (500, 125), (600, 80), (700, 110), (750, 95)
    ]
    path_d = ["M %d %d" % curve_pts[0]]
    for i in range(1, len(curve_pts)):
        p0 = curve_pts[i - 1]
        p1 = curve_pts[i]
        cx1 = (p0[0] + p1[0]) / 2
        path_d.append("C %d %d, %d %d, %d %d" % (cx1, p0[1], cx1, p1[1], p1[0], p1[1]))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), NEG))

    # Точка виміру в момент t_x
    tx = 445
    ty = 90
    parts.append(line(tx, y_b_axis + 5, tx, ty, color=MUTED, sw=1.2, dash="3,3"))
    parts.append(circle(tx, ty, 5, fill=NEG, stroke=BG, sw=1.5))
    parts.append(text(tx, y_b_axis + 18, "t_x", size=11, color=MUTED))
    parts.append(text(tx + 45, ty - 8, "B(t_x) визначено", size=11, color=NEG, bold=True))

    # Розділювач
    parts.append(line(50, 185, W - 50, 185, color="#e0e0e0", sw=1, dash="4,4"))

    # Нижня половина — Подія E: дискретний потік [(t_i, v_i)]
    y_e_axis = 280
    parts.append(text(85, y_e_axis - 20, "Подія E", size=14, bold=True, color=POS))
    parts.append(text(85, y_e_axis, "E = [(t₀,v₀), (t₁,v₁)...]", size=11, color=MUTED))
    parts.append(text(85, y_e_axis + 18, "(дискретні спалахи)", size=10, color=MUTED))

    # Вісь часу E
    parts.append(line(xL, y_e_axis, xR, y_e_axis, color=INK, sw=1.5))
    parts.append(arrow(xR - 4, y_e_axis, xR + 10, y_e_axis, color=INK))
    parts.append(text(xR + 22, y_e_axis + 4, "t", size=13, italic=True))

    events = [
        (220, "v₀: Клік"),
        (350, "v₁: Клавіша"),
        (520, "v₂: Пакет"),
        (670, "v₃: Клік")
    ]
    for ex, label in events:
        parts.append(line(ex, y_e_axis, ex, y_e_axis - 45, color=POS, sw=2))
        parts.append(arrow(ex, y_e_axis - 35, ex, y_e_axis - 50, color=POS, sw=2))
        parts.append(circle(ex, y_e_axis, 4, fill=POS, stroke=BG, sw=1))
        parts.append(text(ex, y_e_axis - 60, label, size=11, color=POS, bold=True))
        parts.append(text(ex, y_e_axis + 18, "t_%s" % label[1], size=11, color=MUTED))

    render(os.path.join(IMG, "behavior-vs-event.svg"), W, H, *parts)


# ── Фігура 2: Ромбоподібна залежність і глітч (Diamond Glitch) ───────────────
def fig_diamond_glitch():
    W, H = 820, 390
    parts = []
    parts.append(text(W / 2, 26, "Ромбоподібна залежність: наївний push проти топологічного оновлення", size=15, bold=True))

    # Ліворуч: граф ромба
    parts.append(text(190, 60, "Граф залежностей", size=14, bold=True, color=INK))

    b_a, _, _ = textbox(190, 105, "A: Джерело (x = 1)", size=12, min_w=150, fill="#f4f6f8", stroke=INK)
    parts.append(b_a)

    b_b, _, _ = textbox(110, 200, "B = x + 1", size=12, min_w=100, fill="#eaf0fd", stroke=NEG)
    parts.append(b_b)

    b_c, _, _ = textbox(270, 200, "C = x · 2", size=12, min_w=100, fill="#eaf0fd", stroke=NEG)
    parts.append(b_c)

    b_d, _, _ = textbox(190, 305, "D = B + C", size=12, min_w=140, fill="#fdecea", stroke=POS)
    parts.append(b_d)

    parts.append(arrow(170, 125, 125, 180, color=INK))
    parts.append(arrow(210, 125, 255, 180, color=INK))
    parts.append(arrow(125, 220, 170, 285, color=INK))
    parts.append(arrow(255, 220, 210, 285, color=INK))

    # Розділювач
    parts.append(line(370, 48, 370, H - 20, color="#dddddd", sw=1, dash="4,4"))

    # Праворуч: порівняння двох підходів при x: 1 → 2
    parts.append(text(595, 60, "Поведінка при зміні x з 1 на 2", size=14, bold=True, color=INK))

    # Наївний Push
    parts.append(text(400, 100, "1. Наївний Push (виникає глітч):", size=12, bold=True, color=POS, anchor="start"))
    steps_naive = [
        "• A оновлюється: x = 2",
        "• Сповіщення йде гілкою B: B = 2 + 1 = 3",
        "• B одразу смикає D (поки C ще старе! C = 2):",
        "  → D = 3 + 2 = 5  [НЕКОРЕКТНИЙ ТИМЧАСОВИЙ СТАН: ГЛІТЧ]",
        "• Сповіщення нарешті доходить до C: C = 2 · 2 = 4",
        "• C смикає D вдруге: D = 3 + 4 = 7"
    ]
    for i, st in enumerate(steps_naive):
        clr = POS if "ГЛІТЧ" in st else INK
        bld = True if "ГЛІТЧ" in st else False
        parts.append(text(405, 125 + i * 20, st, size=11, color=clr, anchor="start", bold=bld))

    # Топологічне / Синхронне оновлення
    parts.append(text(400, 260, "2. Топологічне оновлення (Glitch Freedom):", size=12, bold=True, color=FIELD, anchor="start"))
    steps_topo = [
        "• Рівень 0: A оновлюється (x = 2)",
        "• Рівень 1: одночасно обчислюються B = 3 і C = 4",
        "• Рівень 2: D обчислюється один раз із узгодженими входами:",
        "  → D = 3 + 4 = 7  [Транзакційно, 0 глітчів]"
    ]
    for i, st in enumerate(steps_topo):
        clr = FIELD if "Транзакційно" in st else INK
        bld = True if "Транзакційно" in st else False
        parts.append(text(405, 285 + i * 20, st, size=11, color=clr, anchor="start", bold=bld))

    render(os.path.join(IMG, "diamond-glitch.svg"), W, H, *parts)


# ── Фігура 3: Двоетапний алгоритм Push-Pull (Signals) ─────────────────────────
def fig_push_pull_signals():
    W, H = 820, 360
    parts = []
    parts.append(text(W / 2, 26, "Двоетапне поширення в сигналах: Push (брудні мітки) → Pull (чисте обчислення)", size=15, bold=True))

    # Ліва колонка: Фаза 1 — Push Dirty
    parts.append(text(210, 62, "Фаза 1: Push (позначення Dirty)", size=13, bold=True, color=POS))
    parts.append(text(210, 82, "Джерело змінилося → мітки вниз без обчислень", size=11, color=MUTED))

    b1, _, _ = textbox(210, 130, "Сигнал A (Змінено)", size=11, min_w=150, fill="#fdecea", stroke=POS)
    parts.append(b1)

    b2, _, _ = textbox(130, 220, "Обчислення B\n[STALE / DIRTY]", size=11, min_w=120, fill="#fff3e0", stroke="#e67e22")
    parts.append(b2)

    b3, _, _ = textbox(290, 220, "Обчислення C\n[STALE / DIRTY]", size=11, min_w=120, fill="#fff3e0", stroke="#e67e22")
    parts.append(b3)

    b4, _, _ = textbox(210, 310, "Ефект / View D\n[STALE / DIRTY]", size=11, min_w=140, fill="#fff3e0", stroke="#e67e22")
    parts.append(b4)

    parts.append(arrow(185, 150, 145, 195, color=POS))
    parts.append(arrow(235, 150, 275, 195, color=POS))
    parts.append(arrow(145, 245, 185, 290, color=POS))
    parts.append(arrow(275, 245, 235, 290, color=POS))

    # Розділювач
    parts.append(line(W / 2, 50, W / 2, H - 20, color="#dddddd", sw=1, dash="4,4"))

    # Права колонка: Фаза 2 — Pull Clean
    parts.append(text(610, 62, "Фаза 2: Pull (ліниве/впорядковане зчитування)", size=13, bold=True, color=FIELD))
    parts.append(text(610, 82, "Обчислення за топологічним рангом або запитом", size=11, color=MUTED))

    p1, _, _ = textbox(610, 130, "Сигнал A (нове значення)", size=11, min_w=150, fill="#e8f8f5", stroke=FIELD)
    parts.append(p1)

    p2, _, _ = textbox(530, 220, "Обчислення B\n[CLEAN: оновлено]", size=11, min_w=120, fill="#e8f8f5", stroke=FIELD)
    parts.append(p2)

    p3, _, _ = textbox(690, 220, "Обчислення C\n[CLEAN: оновлено]", size=11, min_w=120, fill="#e8f8f5", stroke=FIELD)
    parts.append(p3)

    p4, _, _ = textbox(610, 310, "Ефект / View D\n[Зчитує B і C рівно 1 раз]", size=11, min_w=160, fill="#eaf0fd", stroke=NEG)
    parts.append(p4)

    # Стрілки запиту вгору
    parts.append(arrow(585, 290, 545, 245, color=NEG))
    parts.append(arrow(635, 290, 675, 245, color=NEG))
    parts.append(arrow(545, 195, 585, 150, color=FIELD))
    parts.append(arrow(675, 195, 635, 150, color=FIELD))

    render(os.path.join(IMG, "push-pull-signals.svg"), W, H, *parts)


# ── Фігура 4: Композиція комбінаторів FRP ──────────────────────────────────────
def fig_frp_combinators():
    W, H = 820, 320
    parts = []
    parts.append(text(W / 2, 26, "Функціональні комбінатори: міст між неперервним часом і подіями", size=15, bold=True))

    # Лівий блок: Джерело Подій E (кліки)
    b_ev, _, _ = textbox(130, 90, "Подія E\n(Кліки миші)", size=12, min_w=130, fill="#fdecea", stroke=POS)
    parts.append(b_ev)

    # Верхній блок: Неперервна Поведінка B (координати миші)
    b_beh, _, _ = textbox(130, 220, "Поведінка B\n(Координати миші B(t))", size=12, min_w=160, fill="#eaf0fd", stroke=NEG)
    parts.append(b_beh)

    # Центр: Комбінатор sample
    b_sample, _, _ = textbox(360, 155, "sample / snapshot\n(Зріз B у моменти E)", size=12, min_w=160, fill="#f4f6f8", stroke=INK)
    parts.append(b_sample)

    parts.append(arrow(200, 105, 275, 140, color=POS))
    parts.append(text(225, 110, "момент", size=10, color=POS))

    parts.append(arrow(215, 205, 275, 170, color=NEG))
    parts.append(text(230, 200, "значення", size=10, color=NEG))

    # Праворуч: Комбінатор foldp / scan
    b_foldp, _, _ = textbox(580, 155, "foldp / scan (+)\n(Накопичення стану)", size=12, min_w=150, fill="#f4f6f8", stroke=INK)
    parts.append(b_foldp)

    parts.append(arrow(445, 155, 500, 155, color=INK))
    parts.append(text(472, 142, "E(x, y)", size=10, color=INK))

    # Вихід: Результуюча Поведінка (траєкторія/стан)
    b_out, _, _ = textbox(735, 155, "Нова Поведінка B_out\n(Поточний стан моделі)", size=12, min_w=150, fill="#e8f8f5", stroke=FIELD)
    parts.append(b_out)

    parts.append(arrow(660, 155, 700, 155, color=FIELD))

    # Пояснювальний підпис унизу
    parts.append(text(W / 2, 290, "sample бере неперервні дані в моменти спалахів, а foldp перетворює спалахи назад у тривалий стан", size=11, color=MUTED))

    render(os.path.join(IMG, "frp-combinators-flow.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_behavior_vs_event()
    fig_diamond_glitch()
    fig_push_pull_signals()
    fig_frp_combinators()
    print("All figures generated successfully.")
