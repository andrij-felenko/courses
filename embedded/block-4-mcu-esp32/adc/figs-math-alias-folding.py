# -*- coding: utf-8 -*-
"""
Фігури до математичної вставки «Аліасинг у числах» (ch26-s5-m-alias-folding.md).
Дві фігури:
  fig-26-5m-1-folding-map.svg  — карта згортання (trикутна / sawtooth функція)
  fig-26-5m-2-51hz-trace.svg   — числовий трас прикладу 51 Гц → 1 Гц

Залежності: тільки стандартна бібліотека Python + спільний svgkit.
Запуск: python figs-ch26-s5-m-alias-folding.py
Вивід: ./img/
"""

import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


def save_svg(name, w, h, *frags, title=None):
    path = os.path.join(OUT, name)
    render(path, w, h, *frags, title=title)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.5m.1 — Карта згортання: функція alias(f) = трикутна хвиля
# ═══════════════════════════════════════════════════════════════════════════════

def fig_folding_map():
    """
    Карта згортання: по горизонталі вхідна частота f від 0 до 2·fs,
    по вертикалі — аліас(f). Трикутна (sawtooth / zigzag) хвиля:
    0→fs/2→0→fs/2→0. Пунктиром показано приклад f=700, fs=1000 → 300.
    """
    W, H = 760, 420
    frags = []

    # ── Осьові параметри ────────────────────────────────────────────────────
    fs = 1000           # умовна fs у ГЦ (позначки нормовані)
    Xmin, Xmax = 0, 2 * fs
    Ymin, Ymax = 0, fs / 2   # вісь Y: 0..fs/2

    ox, oy = 80, 360    # нижній-лівий кут осей
    aw = 620            # ширина осі X
    ah = 280            # висота осі Y

    def xp(f):
        return ox + (f - Xmin) / (Xmax - Xmin) * aw

    def yp(a):
        return oy - (a - Ymin) / (Ymax - Ymin) * ah

    # ── Сітка і осі ─────────────────────────────────────────────────────────
    # горизонтальна пунктирна лінія на fs/2
    frags.append(line(ox, yp(fs / 2), ox + aw, yp(fs / 2),
                      color=MUTED, sw=1.0, dash="4,4"))

    # вертикальні пунктирні на fs, 2fs
    for xval in [fs, 2 * fs]:
        frags.append(line(xp(xval), oy, xp(xval), yp(fs / 2),
                          color=MUTED, sw=1.0, dash="4,4"))

    # осі
    frags.append(line(ox, oy, ox + aw + 20, oy, color=INK, sw=1.8))   # X
    frags.append(line(ox, oy, ox, yp(Ymax) - 15, color=INK, sw=1.8))  # Y

    # стрілки осей
    frags.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.8))
    frags.append(arrow(ox, yp(Ymax) - 5, ox, yp(Ymax) - 20, color=INK, sw=1.8))

    # ── Підписи осей ─────────────────────────────────────────────────────────
    # X: 0, fs/2, fs, 3fs/2, 2fs
    x_marks = [(0, "0"), (fs / 2, "fs/2"), (fs, "fs"), (3 * fs / 2, "3fs/2"), (2 * fs, "2fs")]
    for fval, lbl in x_marks:
        xpos = xp(fval)
        frags.append(line(xpos, oy - 4, xpos, oy + 4, color=INK, sw=1.4))
        frags.append(text(xpos, oy + 18, lbl, size=12, color=INK, anchor="middle"))

    # Y: 0, fs/2
    for aval, lbl in [(0, "0"), (fs / 2, "fs/2")]:
        ypos = yp(aval)
        frags.append(line(ox - 4, ypos, ox + 4, ypos, color=INK, sw=1.4))
        frags.append(text(ox - 8, ypos + 4, lbl, size=12, color=INK, anchor="end"))

    # підписи назв осей
    frags.append(text(ox + aw + 22, oy + 4, "f", size=14, color=INK, anchor="start",
                      italic=True))
    frags.append(text(ox - 10, yp(Ymax) - 22, "аліас(f)", size=12, color=INK,
                      anchor="middle"))

    # ── Sawtooth-крива alias(f) = fs/2 − |(f mod fs) − fs/2| ───────────────
    pts = []
    N = 400
    for i in range(N + 1):
        f = Xmin + (Xmax - Xmin) * i / N
        fmod = math.fmod(f, fs)
        alias = fs / 2 - abs(fmod - fs / 2)
        pts.append((xp(f), yp(alias)))
    # побудуємо як polyline
    pts_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    frags.append(f'<polyline points="{pts_str}" fill="none" stroke="{NEG}" '
                 f'stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')

    # ── Приклад: f=700, fs=1000 → alias=300 (пунктирна вертикаль + горизонталь) ─
    f_ex, alias_ex = 700, 300
    xex, yex = xp(f_ex), yp(alias_ex)

    frags.append(line(xex, oy, xex, yex, color=POS, sw=1.4, dash="5,4"))
    frags.append(line(ox, yex, xex, yex, color=POS, sw=1.4, dash="5,4"))

    # крапка на кривій
    frags.append(circle(xex, yex, 5.5, fill=POS, stroke=POS, sw=1))

    # мітки прикладу
    frags.append(text(xex + 6, oy + 18, "700", size=11, color=POS, anchor="start"))
    frags.append(text(ox - 8, yex + 4, "300", size=11, color=POS, anchor="end"))

    # рамка з поясненням
    box_txt, bw, bh = "f=700, fs=1000\nk=round(700/1000)=1\nalias=|700−1000|=300", 200, 58
    bx, by = xex + 18, yex - 42
    frags.append(rect(bx, by, bw, bh, fill=FILL, stroke=POS, sw=1.2, rx=7))
    for i, ln in enumerate(box_txt.split("\n")):
        frags.append(text(bx + bw / 2, by + 15 + i * 16, ln,
                          size=11, color=INK, anchor="middle"))

    # ── Підпис «Найквіст fs/2» ───────────────────────────────────────────────
    nyq_y = yp(fs / 2)
    tb, tbw, tbh = textbox(ox + aw - 90, nyq_y - 16, "Найквіст = fs/2",
                           size=11, fill=FILL, stroke=MUTED)
    frags.append(tb)

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 28, "Карта згортання: alias(f) — трикутна функція частоти",
                      size=16, color=INK, anchor="middle", bold=True))
    frags.append(text(W / 2, 46, "кожна точка вище fs/2 має «двійника» нижче — звідси невиправність аліаса",
                      size=11, color=MUTED, anchor="middle"))

    save_svg("fig-26-5m-1-folding-map.svg", W, H, *frags)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.5m.2 — Числовий трас прикладу: 51 Гц → 1 Гц
# ═══════════════════════════════════════════════════════════════════════════════

def fig_51hz_trace():
    """
    Числова вісь 0..100 Гц, позначки fs=50 і Найквіст=25.
    Стрілки: 51 Гц → 1 Гц (|51−50|), 49 Гц → 1 Гц (|49−50|).
    Нижня вставка: часовий трас — 51-Гц синус + відліки (fs=50) + 1-Гц обвідна.
    """
    W, H = 760, 450
    frags = []

    # ── Верхня панель: вісь частот ──────────────────────────────────────────
    ox, oy = 60, 130    # початок осі
    aw = 640            # ширина осі (0..100 Гц)

    def xf(freq):
        return ox + freq / 100 * aw

    # ── Вісь X ───────────────────────────────────────────────────────────────
    frags.append(line(ox, oy, ox + aw + 20, oy, color=INK, sw=1.8))
    frags.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.8))

    # мітки 0, 25, 50, 75, 100
    for f, lbl in [(0, "0"), (25, "25"), (50, "50 (fs)"), (75, "75"), (100, "100 Гц")]:
        xpos = xf(f)
        frags.append(line(xpos, oy - 5, xpos, oy + 5, color=INK, sw=1.4))
        col_lbl = NEG if f == 25 else (POS if f == 50 else INK)
        frags.append(text(xpos, oy + 18, lbl, size=11, color=col_lbl, anchor="middle"))

    # пунктир на Найквісті (25 Гц)
    frags.append(line(xf(25), oy - 60, xf(25), oy + 5, color=NEG, sw=1.2, dash="4,4"))
    tb_nyq, _, _ = textbox(xf(25), oy - 72, "Найквіст\n= 25 Гц",
                           size=10, fill=FILL, stroke=NEG)
    frags.append(tb_nyq)

    # ── Точки 51 Гц, 49 Гц і цільова 1 Гц ────────────────────────────────────
    y51 = oy - 44   # рівень точок-джерел
    y1  = oy + 4    # рівень на осі (1 Гц ≈ там же)

    for freq, col, lbl in [(49, MUTED, "49 Гц"), (51, POS, "51 Гц")]:
        xpos = xf(freq)
        frags.append(circle(xpos, y51, 6, fill=col, stroke=col, sw=1))
        frags.append(text(xpos, y51 - 12, lbl, size=12, color=col,
                          anchor="middle", bold=True))

    # точка-результат 1 Гц
    x1 = xf(1)
    frags.append(circle(x1, oy - 4, 7, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(x1, oy - 18, "1 Гц", size=12, color=FIELD,
                      anchor="middle", bold=True))

    # стрілки дуга → 1 Гц: для 51 Гц
    # намалюємо дугу як приблизну квадратичну безьє
    x51 = xf(51)
    frags.append(f'<path d="M{x51:.1f},{y51:.1f} Q{xf(26):.1f},{oy - 70:.1f} {x1:.1f},{oy - 4:.1f}" '
                 f'fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="5,3" '
                 f'marker-end="url(#arrow)"/>')
    # підпис на дузі
    frags.append(text(xf(30), oy - 72, "|51−50|=1", size=10, color=POS, anchor="middle"))

    # стрілка від 49 Гц → 1 Гц
    x49 = xf(49)
    frags.append(f'<path d="M{x49:.1f},{y51:.1f} Q{xf(25):.1f},{oy - 56:.1f} {x1:.1f},{oy - 4:.1f}" '
                 f'fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5,3" '
                 f'marker-end="url(#arrow)"/>')
    frags.append(text(xf(22), oy - 57, "|49−50|=1", size=10, color=MUTED, anchor="middle"))

    # рамка-висновок
    tb_sum, _, _ = textbox(W / 2, 170,
                           "51 Гц і 49 Гц нерозрізнянні від 1 Гц —\nтри входи, один аліас",
                           size=11, fill=FILL, stroke=INK)
    frags.append(tb_sum)

    # ── Нижня вставка: часовий трас ──────────────────────────────────────────
    # Панель
    px0, px1 = 56, W - 40
    py0 = 210   # верх вставки
    py1 = H - 26
    ph  = py1 - py0

    frags.append(rect(px0, py0, px1 - px0, ph, fill=FILL, stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(W / 2, py0 + 16, "Часовий трас: відліки fs=50 по 51-Гц синусу проступають 1-Гц обвідною",
                      size=11, color=INK, anchor="middle", bold=True))

    # Параметри сигналів
    fs_t  = 50          # відліків/с
    f_sig = 51          # Гц
    f_al  = 1           # Гц — обвідна (аліас)
    T     = 2.0         # секунди показу
    n_pts = 300         # точки неперервного сигналу

    # Область малювання сигналу
    tx0, tx1 = px0 + 30, px1 - 20
    ty_mid = py0 + ph // 2 + 8
    ty_amp = (ph - 50) / 2 - 8  # амплітуда у пікселях

    def tx(t): return tx0 + (t / T) * (tx1 - tx0)
    def ty(a): return ty_mid - a * ty_amp

    # Неперервний 51-Гц синус (тонка сіра лінія)
    sig_pts = []
    for i in range(n_pts + 1):
        t = T * i / n_pts
        a = math.sin(2 * math.pi * f_sig * t)
        sig_pts.append((tx(t), ty(a)))
    pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in sig_pts)
    frags.append(f'<polyline points="{pts_str}" fill="none" stroke="{MUTED}" '
                 f'stroke-width="1.2" stroke-dasharray="2,2"/>')

    # 1-Гц обвідна (яскравіша, суцільна)
    env_pts = []
    for i in range(n_pts + 1):
        t = T * i / n_pts
        a = math.sin(2 * math.pi * f_al * t)
        env_pts.append((tx(t), ty(a)))
    pts_str2 = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in env_pts)
    frags.append(f'<polyline points="{pts_str2}" fill="none" stroke="{FIELD}" '
                 f'stroke-width="2.4"/>')

    # Відліки (кружки на 51-Гц синусі у моменти n/fs)
    n_samp = int(T * fs_t)
    for n in range(n_samp + 1):
        t_s = n / fs_t
        if t_s > T:
            break
        a_s = math.sin(2 * math.pi * f_sig * t_s)
        xs, ys = tx(t_s), ty(a_s)
        frags.append(circle(xs, ys, 4, fill=NEG, stroke=NEG, sw=1))

    # Вісь часу (горизонталь по середині)
    frags.append(line(tx0, ty_mid, tx1, ty_mid, color=MUTED, sw=1.0, dash="3,3"))

    # Підписи
    frags.append(text(tx0, ty_mid - ty_amp - 6, "51-Гц синус (сірий пунктир)",
                      size=9, color=MUTED, anchor="start"))
    frags.append(text(tx0, ty_mid + ty_amp + 14, "1-Гц обвідна — хвиля-привид (зелена)",
                      size=9, color=FIELD, anchor="start"))
    frags.append(text(tx1 - 4, ty_mid - ty_amp - 6, "відліки fs=50 (сині кружки)",
                      size=9, color=NEG, anchor="end"))

    # ── Заголовок фігури ──────────────────────────────────────────────────────
    frags.append(text(W / 2, 22, "Трас прикладу: 51 Гц і 49 Гц → обидва дають аліас 1 Гц",
                      size=16, color=INK, anchor="middle", bold=True))
    frags.append(text(W / 2, 42, "три різних входи — один виход; аліас невиправний",
                      size=11, color=MUTED, anchor="middle"))

    save_svg("fig-26-5m-2-51hz-trace.svg", W, H, *frags)


# ── Точка входу ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_folding_map()
    fig_51hz_trace()
    print("done.")
