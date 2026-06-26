# -*- coding: utf-8 -*-
"""Фігури до теми «Запас підсилення і запас фази».
Три фігури:
  margins-bode.svg   — діаграма Боде підсилення в контурі з позначеними запасами
  loop-flip.svg      — як −180° додаткового зсуву перетворює від'ємний ЗЗ на додатний
  step-pm.svg        — перехідна характеристика за різного запасу фази
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Діаграма Боде підсилення в контурі з запасами ─────────────────────────
def fig_margins_bode():
    W, H = 720, 470
    # дві панелі: верх — величина (дБ), низ — фаза (°)
    Lx, Rx = 90, 660            # межі осі частот (логарифмічна, умовна)
    topY0, topY1 = 60, 215      # панель величини
    botY0, botY1 = 270, 420     # панель фази

    def fx(t):                  # t у [0,1] → x
        return Lx + t * (Rx - Lx)

    # величина: спадає рівно (−20 дБ/дек), перетин 0 дБ у t=0.62
    magTop, magBot = 60.0, -30.0   # дБ-діапазон панелі
    def magY(db):
        return topY1 - (db - magBot) / (magTop - magBot) * (topY1 - topY0)
    # пряма: db(t) = 60 - 90*t  → 0 дБ при t≈0.6667
    def db_of(t):
        return 60.0 - 90.0 * t
    t_gc = 60.0 / 90.0          # перетин 0 дБ (gain crossover)

    # фаза: від -45° сповзає до -200°, проходить -180° у t=0.80
    phTop, phBot = -10.0, -210.0
    def phY(ph):
        return botY0 + (phTop - ph) / (phTop - phBot) * (botY1 - botY0)
    def ph_of(t):
        # плавний спад: -45 на старті, -180 при t=0.80, далі нижче
        return -45.0 - 165.0 * (t ** 1.7)
    # знайти t, де фаза = -180
    t_pc = (135.0 / 165.0) ** (1.0 / 1.7)

    frags = []

    # — панель величини —
    frags.append(rect(Lx, topY0, Rx - Lx, topY1 - topY0, fill="#fbfcfd", stroke=MUTED, sw=1))
    frags.append(text((Lx + Rx) / 2, topY0 - 16, "Підсилення в контурі |Aβ|", size=14, bold=True))
    # сітка дБ
    for db in (60, 40, 20, 0, -20):
        y = magY(db)
        frags.append(line(Lx, y, Rx, y, color="#e3e7eb", sw=1))
        frags.append(text(Lx - 8, y + 4, "%d" % db, size=11, color=MUTED, anchor="end"))
    frags.append(text(Lx - 8, topY0 - 4, "дБ", size=11, color=MUTED, anchor="end"))
    # лінія 0 дБ виразніша
    frags.append(line(Lx, magY(0), Rx, magY(0), color=INK, sw=1.4, dash="2,3"))
    # крива величини
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        pts.append("%.1f,%.1f" % (fx(t), magY(db_of(t))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), NEG))
    # вертикаль gain crossover
    frags.append(line(fx(t_gc), topY0, fx(t_gc), botY1, color=FIELD, sw=1.4, dash="4,3"))
    # вертикаль phase crossover
    frags.append(line(fx(t_pc), topY0, fx(t_pc), botY1, color=POS, sw=1.4, dash="4,3"))

    # запас підсилення: на панелі величини, у t_pc від кривої до 0 дБ
    gm_db = db_of(t_pc)         # від'ємне (крива нижче 0 дБ)
    yA = magY(gm_db); yB = magY(0)
    frags.append(line(fx(t_pc), yA, fx(t_pc), yB, color=POS, sw=3))
    frags.append(arrow(fx(t_pc), yB, fx(t_pc), yA, color=POS, sw=2))
    b, bw, bh = textbox(fx(t_pc) + 4, (yA + yB) / 2, "запас\nпідсилення",
                        size=11, color=POS, stroke=POS, fill="#fdecea", pad=6)
    # зсунути рамку праворуч від лінії
    frags.append(b)

    # — панель фази —
    frags.append(rect(Lx, botY0, Rx - Lx, botY1 - botY0, fill="#fbfcfd", stroke=MUTED, sw=1))
    frags.append(text((Lx + Rx) / 2, botY0 - 10, "Зсув фази в контурі", size=14, bold=True))
    for ph in (0, -45, -90, -135, -180):
        y = phY(ph)
        frags.append(line(Lx, y, Rx, y, color="#e3e7eb", sw=1))
        frags.append(text(Lx - 8, y + 4, "%d°" % ph, size=11, color=MUTED, anchor="end"))
    # лінія -180 виразна
    frags.append(line(Lx, phY(-180), Rx, phY(-180), color=INK, sw=1.4, dash="2,3"))
    # крива фази
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        pts.append("%.1f,%.1f" % (fx(t), phY(ph_of(t))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), NEG))

    # запас фази: на панелі фази, у t_gc від кривої до -180
    pm_ph = ph_of(t_gc)        # напр. ~ -120°
    yA = phY(pm_ph); yB = phY(-180)
    frags.append(line(fx(t_gc), yA, fx(t_gc), yB, color=FIELD, sw=3))
    frags.append(arrow(fx(t_gc), yB, fx(t_gc), yA, color=FIELD, sw=2))
    b, bw, bh = textbox(fx(t_gc) - 4 - 44, (yA + yB) / 2 + 8, "запас\nфази",
                        size=11, color=FIELD, stroke=FIELD, fill="#eafaf0", pad=6)
    frags.append(b)

    # підписи частот-перетинів
    frags.append(text(fx(t_gc), botY1 + 18, "тут |Aβ| = 1 (0 дБ)", size=10.5,
                      color=FIELD, anchor="middle"))
    frags.append(text(fx(t_pc), botY1 + 33, "тут фаза = −180°", size=10.5,
                      color=POS, anchor="middle"))
    frags.append(text(Rx, botY1 + 18, "частота →", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "margins-bode.svg"), W, H, *frags)


# ── 2. Як −180° перевертає знак зворотного зв'язку ───────────────────────────
def fig_loop_flip():
    W, H = 720, 320
    frags = []
    frags.append(text(W / 2, 28, "Чому додаткові −180° роблять зв'язок небезпечним",
                      size=15, bold=True))

    def block(cx, cy, label, sub=None):
        b, w, h = textbox(cx, cy, label, size=12.5, bold=True, min_w=92, pad=10,
                          fill="#eef2ff", stroke=NEG)
        out = b
        if sub:
            out += text(cx, cy + h / 2 + 16, sub, size=10.5, color=MUTED)
        return out, w, h

    # верхній рядок: задумано — від'ємний ЗЗ
    yTop = 95
    frags.append(text(W / 2, 62, "Задумано: зворотний сигнал ПРОТИДІЄ (низькі частоти)",
                      size=12, color=FIELD, bold=True))
    s1, _, _ = block(150, yTop, "підсилювач")
    s2, _, _ = block(360, yTop, "коло ЗЗ  β")
    frags += [s1, s2]
    frags.append(arrow(205, yTop, 312, yTop, color=INK, sw=2))
    # суматор зліва
    frags.append(circle(70, yTop, 16, fill="#f4f6f8", stroke=INK, sw=1.6))
    frags.append(text(70, yTop + 5, "−", size=18, color=NEG, bold=True))
    frags.append(arrow(86, yTop, 104, yTop, color=INK, sw=2))
    frags.append(arrow(408, yTop, 408, yTop - 34, color=INK, sw=2))   # вгору
    frags.append(line(408, yTop - 34, 70, yTop - 34, color=INK, sw=2))
    frags.append(line(70, yTop - 34, 70, yTop - 16, color=INK, sw=2))
    frags.append(text(240, yTop - 42, "повертається у протифазі → гасить", size=10.5,
                      color=FIELD, anchor="middle"))

    # нижній рядок: на частоті, де кола додали ще -180°
    yBot = 235
    frags.append(text(W / 2, 158, "На частоті, де кола додали ще −180° зсуву:",
                      size=12, color=POS, bold=True))
    s3, _, _ = block(150, yBot, "підсилювач")
    s4, _, _ = block(360, yBot, "+(−180°)", )
    frags += [s3, s4]
    frags.append(arrow(205, yBot, 312, yBot, color=INK, sw=2))
    frags.append(circle(70, yBot, 16, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text(70, yBot + 5, "−", size=18, color=NEG, bold=True))
    frags.append(arrow(86, yBot, 104, yBot, color=INK, sw=2))
    frags.append(arrow(408, yBot, 408, yBot + 34, color=POS, sw=2))
    frags.append(line(408, yBot + 34, 70, yBot + 34, color=POS, sw=2))
    frags.append(line(70, yBot + 34, 70, yBot + 16, color=POS, sw=2))
    frags.append(text(240, yBot + 50, "повертається У ФАЗІ → підсилює (лавина)",
                      size=10.5, color=POS, anchor="middle"))

    # права колонка — підсумок
    b, w, h = fitbox(495, 80, 200, 150,
                     "Знак «−» дає 180°.\nЩе −180° від затримок\nу колі = разом 360°,\n"
                     "тобто 0°: сигнал\nповертається У ФАЗІ.\n\nЯкщо там |Aβ| ще ≥ 1 —\n"
                     "коло саме себе\nрозгойдує: ГЕНЕРАЦІЯ.",
                     size=11, fill="#fff8f0", stroke=POS), 0, 0
    frags.append(b)

    render(os.path.join(IMG, "loop-flip.svg"), W, H, *frags)


# ── 3. Перехідна характеристика за різного запасу фази ───────────────────────
def fig_step_pm():
    W, H = 720, 360
    x0, x1 = 80, 660
    y0, y1 = 70, 300
    frags = []
    frags.append(text(W / 2, 30, "Запас фази видно в перехідній характеристиці", size=15, bold=True))

    # осі
    frags.append(line(x0, y1, x1, y1, color=INK, sw=1.6))       # час
    frags.append(line(x0, y0 - 6, x0, y1, color=INK, sw=1.6))   # вихід
    frags.append(text(x1, y1 + 18, "час →", size=11, color=MUTED, anchor="end"))
    frags.append(text(x0 - 10, y0 + 2, "вихід", size=11, color=MUTED, anchor="end"))
    # рівень «задано» = 1.0
    yset = y0 + (y1 - y0) * 0.32
    frags.append(line(x0, yset, x1, yset, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(x1 - 4, yset - 6, "задано", size=10.5, color=MUTED, anchor="end"))

    T = x1 - x0
    def yval(v):   # v: 0..~1.7 → екран
        return y1 - (v / 1.7) * (y1 - y0)

    import math as m
    def damped(tt, zeta, wn):
        # нормована перехідна характеристика 2-го порядку
        if zeta >= 1:
            return 1 - m.exp(-wn * tt) * (1 + wn * tt)
        wd = wn * m.sqrt(1 - zeta * zeta)
        phi = m.acos(zeta)
        return 1 - (m.exp(-zeta * wn * tt) / m.sqrt(1 - zeta * zeta)) * m.sin(wd * tt + phi)

    curves = [
        (0.16, "#c0392b", "малий запас (~20°): дзвенить, ледь не генерує"),
        (0.45, "#e08a00", "середній (~45°): один невеликий викид"),
        (0.85, "#27ae60", "великий (~70°): майже без викиду, чисто"),
    ]
    wn = 9.0
    legy = y0 + 4
    for zeta, col, lab in curves:
        pts = []
        for i in range(0, 241):
            tt = i / 240.0 * 1.5
            v = damped(tt, zeta, wn)
            xx = x0 + (tt / 1.5) * T
            pts.append("%.1f,%.1f" % (xx, yval(v)))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                     % (" ".join(pts), col))
        frags.append(circle(x0 + 250, legy, 5, fill=col, stroke=col, sw=1))
        frags.append(text(x0 + 262, legy + 4, lab, size=11, color=INK, anchor="start"))
        legy += 20

    render(os.path.join(IMG, "step-pm.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_margins_bode()
    fig_loop_flip()
    fig_step_pm()
    print("OK: figs written to", IMG)
