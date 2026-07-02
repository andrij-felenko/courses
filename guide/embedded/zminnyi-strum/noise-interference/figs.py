# -*- coding: utf-8 -*-
"""Фігури до детальної статті «Шум і завади» (версія -d,
guide/embedded/osnovy/noise-interference).

Базова стаття вже пояснює поділ шум/наводка, RMS, SNR. Детальна йде глибше:
спектральна густина (шум на √Гц), механізми наводок як формули, і боротьба
смугою (усереднення, синхронне детектування). Фігури несуть саме цей другий шар.

Фігури:
  spectral-density.svg — густина шуму рівна по частоті; повний шум = eₙ·√B (площа)
  coupling-paths.svg   — три шляхи наводки: ємнісний E, індуктивний B, спільний Z
  lockin-narrowband.svg— синхронне детектування: сигнал на f_c витягають вузькою смугою
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


def fillrect(x, y, w, h, fill, opacity=1.0):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
            'fill-opacity="%.2f"/>' % (x, y, w, h, fill, opacity))


# ── 1. Спектральна густина: шум наповнює смугу ───────────────────────────────
def fig_spectral_density():
    W, H = 740, 420
    els = []
    x0, y0 = 90, 320
    axw, axh = 580, 230
    els.append(line(x0, y0, x0 + axw, y0, color=INK, sw=2))
    els.append(line(x0, y0, x0, y0 - axh, color=INK, sw=2))
    els.append(text(x0 + axw, y0 + 26, "частота f →", size=13, anchor="end"))
    els.append(text(x0 - 6, y0 - axh - 8, "густина шуму eₙ  (нВ/√Гц)", size=13, anchor="start"))

    dens_y = y0 - 130
    # вузька смуга — заповнена площа під густиною
    f1 = x0 + 160
    els.append(fillrect(x0, dens_y, f1 - x0, y0 - dens_y, FIELD, 0.30))
    els.append(line(f1, y0, f1, dens_y, color=FIELD, sw=2, dash="4 3"))
    els.append(text((x0 + f1) / 2, y0 - 46, "вузька", size=13, color=FIELD))
    els.append(text((x0 + f1) / 2, y0 - 28, "смуга B₁", size=13, color=FIELD))
    els.append(text(f1, y0 + 20, "B₁", size=13, color=FIELD))
    # додано смугою — світліша площа праворуч
    f2 = x0 + 500
    els.append(fillrect(f1, dens_y, f2 - f1, y0 - dens_y, POS, 0.16))
    els.append(line(f2, y0, f2, dens_y, color=POS, sw=2, dash="4 3"))
    els.append(text((f1 + f2) / 2, y0 - 150, "додано розширенням смуги", size=13, color=POS))
    els.append(text(f2, y0 + 20, "B₂", size=13, color=POS))
    # рівна лінія густини — поверх площ, щоб було видно
    els.append(line(x0, dens_y, x0 + axw, dens_y, color=NEG, sw=3))
    els.append(text(x0 + axw - 6, dens_y - 12, "eₙ = сталий  (білий шум)", size=13, color=NEG, anchor="end"))

    body, _, _ = textbox((x0 + axw) / 2, 54, "Повний шум = √(площа) = eₙ·√B .   Смугу вчетверо ширше → шум лише вдвічі більший.",
                         size=14, fill="#eef3ff", stroke=NEG)
    els.append(body)
    return render(os.path.join(IMG, 'spectral-density.svg'), W, H, *els,
                  title="Густина шуму: чому шум рахують «на корінь із герца»")


# ── 2. Три шляхи наводки ─────────────────────────────────────────────────────
def fig_coupling():
    W, H = 780, 400
    els = []
    pw, gap = 244, 14
    x = [16, 16 + pw + gap, 16 + 2 * (pw + gap)]
    top, ph = 58, 300
    titles = ["ЄМНІСНА  (поле E)", "ІНДУКТИВНА  (поле B)", "спільний провід  (Z)"]
    tcol = [NEG, FIELD, POS]
    for i in range(3):
        els.append(rect(x[i], top, pw, ph, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
        els.append(text(x[i] + pw / 2, top + 24, titles[i], size=14, color=tcol[i], bold=True))

    # 1) ємнісна: dV/dt через стрій-ємність жене струм у вхід
    ax = x[0]
    agg_y, vic_y = top + 78, top + 172
    els.append(line(ax + 26, agg_y, ax + pw - 26, agg_y, color=POS, sw=3))
    els.append(text(ax + 26, agg_y - 12, "агресор  dV/dt", size=12, color=POS, anchor="start"))
    els.append(line(ax + 26, vic_y, ax + pw - 26, vic_y, color=NEG, sw=3))
    els.append(text(ax + 26, vic_y + 22, "жертва  (вх. Z)", size=12, color=NEG, anchor="start"))
    for cx in (ax + 74, ax + 122, ax + 170):
        els.append(line(cx, agg_y, cx, vic_y, color=MUTED, sw=1, dash="3 3"))
    els.append(text(ax + pw / 2, (agg_y + vic_y) / 2 + 4, "C_стрій", size=12, color=MUTED))
    els.append(text(ax + pw / 2, vic_y + 56, "i = C·dV/dt", size=14, color=INK))
    els.append(text(ax + pw / 2, vic_y + 78, "лік: екран, ↓Z", size=12, color=MUTED))

    # 2) індуктивна: dI/dt агресора наводить ЕРС у контурі площею A
    bx = x[1]
    cy = top + 130
    els.append(circle(bx + 66, cy, 32, fill="none", stroke=POS, sw=3))
    els.append(text(bx + 66, cy + 4, "dI/dt", size=12, color=POS))
    els.append(rect(bx + 128, cy - 32, 76, 64, fill="none", stroke=NEG, sw=3, rx=2))
    els.append(text(bx + 166, cy + 4, "A", size=14, color=NEG))
    for ay in (cy - 18, cy, cy + 18):
        els.append(arrow(bx + 104, ay, bx + 126, ay, color=MUTED, sw=1.4))
    els.append(text(bx + pw / 2, top + ph - 70, "e = M·dI/dt", size=14, color=INK))
    els.append(text(bx + pw / 2, top + ph - 48, "∝ площа контуру A", size=12, color=MUTED))
    els.append(text(bx + pw / 2, top + ph - 26, "лік: скрутка, ↓A", size=12, color=MUTED))

    # 3) спільний провід: зворотний струм на спільному Z_g піднімає V
    gx = x[2]
    railL, railR = gx + 30, gx + pw - 30
    gy = top + 158
    els.append(line(railL, gy, railR, gy, color=MUTED, sw=4))
    els.append(text((railL + railR) / 2, gy + 22, "спільна «земля»  Z_g", size=12, color=MUTED))
    els.append(arrow(railL + 24, gy - 46, railR - 24, gy - 46, color=POS, sw=2.4))
    els.append(text((railL + railR) / 2, gy - 56, "шумний зворотний струм", size=12, color=POS))
    els.append(line(railL + 26, gy, railL + 26, gy - 20, color=NEG, sw=2))
    els.append(line(railR - 26, gy, railR - 26, gy - 20, color=NEG, sw=2))
    els.append(text((railL + railR) / 2, gy + 50, "V_шум = I·Z_g", size=14, color=INK))
    els.append(text((railL + railR) / 2, gy + 72, "лік: одна точка, ↓Z", size=12, color=MUTED))

    return render(os.path.join(IMG, 'coupling-paths.svg'), W, H, *els,
                  title="Три шляхи наводки — три різні ліки")


# ── 3. Синхронне детектування: витягти сигнал вузькою смугою ─────────────────
def fig_lockin():
    W, H = 740, 470
    els = []
    x0, axw = 90, 570

    # ДО: широкий шумовий фон + високий пік сигналу на f_c
    topA, hA = 74, 120
    baseA = topA + hA
    els.append(line(x0, baseA, x0 + axw, baseA, color=INK, sw=2))
    els.append(line(x0, baseA, x0, topA, color=INK, sw=2))
    els.append(text(x0 + axw, baseA + 22, "частота", size=12, anchor="end"))
    els.append(text(x0, topA - 12, "ДО: сигнал тоне в широкому шумі", size=14, color=INK, anchor="start"))
    pts = []
    for k in range(0, axw + 1, 7):
        yy = baseA - 20 - 10 * abs(math.sin(k * 0.7) * math.cos(k * 0.23))
        pts.append((x0 + k, yy))
    els.append(polyline(pts, color=MUTED, sw=1.5))
    els.append(text(x0 + 96, baseA - 44, "шумовий фон", size=12, color=MUTED))
    fc = x0 + 370
    els.append(line(fc, baseA, fc, topA + 6, color=NEG, sw=3))
    els.append(text(fc, topA - 0, "сигнал @ f_c", size=12, color=NEG))

    # середина: множення на опорну + фільтр
    midY = baseA + 54
    body, _, _ = textbox((x0 + axw) / 2, midY, "× опорна на f_c,  потім вузький фільтр НЧ  →  живе лише тонкий шар шуму навколо f_c",
                         size=13, fill="#eef3ff", stroke=NEG)
    els.append(body)

    # ПІСЛЯ: сигнал на 0 Гц, лише вузька смужка шуму
    topB = midY + 62
    hB = 120
    baseB = topB + hB
    els.append(line(x0, baseB, x0 + axw, baseB, color=INK, sw=2))
    els.append(line(x0, baseB, x0, topB, color=INK, sw=2))
    els.append(text(x0 + axw, baseB + 22, "частота", size=12, anchor="end"))
    els.append(text(x0, topB - 12, "ПІСЛЯ: сигнал на 0 Гц, шум — лише вузька смужка", size=14, color=INK, anchor="start"))
    bump = []
    for k in range(0, 96, 5):
        yy = baseB - 16 - 9 * math.exp(-((k - 22) ** 2) / 320.0)
        bump.append((x0 + k, yy))
    els.append(polyline(bump, color=MUTED, sw=1.5))
    els.append(text(x0 + 150, baseB - 40, "Δf вузький", size=12, color=MUTED, anchor="start"))
    els.append(line(x0 + 4, baseB, x0 + 4, topB + 6, color=FIELD, sw=3))
    els.append(text(x0 + 64, topB + 4, "сигнал", size=12, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, 'lockin-narrowband.svg'), W, H, *els,
                  title="Синхронне детектування: вузька смуга навколо сигналу")


# ── 4. Уявний дослід Найквіста: дві рівні R і лінія з тепловими модами ────────
def fig_nyquist_line():
    W, H = 860, 430
    els = []
    # дві коробки-резистори по краях, лінія між ними
    bw, bh = 118, 92
    lx, rx = 40, W - 40 - bw
    cy = 150
    lineY = cy
    x1 = lx + bw
    x2 = rx
    # резистор ліворуч
    els.append(rect(lx, cy - bh / 2, bw, bh, fill="#fdecea", stroke=POS, sw=2))
    els.append(text(lx + bw / 2, cy - 8, "резистор R", size=14, color=POS, bold=True))
    els.append(text(lx + bw / 2, cy + 14, "при T", size=13, color=POS))
    # резистор праворуч
    els.append(rect(rx, cy - bh / 2, bw, bh, fill="#fdecea", stroke=POS, sw=2))
    els.append(text(rx + bw / 2, cy - 8, "резистор R", size=14, color=POS, bold=True))
    els.append(text(rx + bw / 2, cy + 14, "при T", size=13, color=POS))
    # два проводи лінії (верх і низ) — «лінія передачі», опір хвильовий = R
    els.append(line(x1, lineY - 12, x2, lineY - 12, color=INK, sw=2.5))
    els.append(line(x1, lineY + 12, x2, lineY + 12, color=INK, sw=2.5))
    els.append(text((x1 + x2) / 2, lineY - 30, "лінія без втрат, довжина L,  хвильовий опір = R", size=13))
    # стояча хвиля між проводами (кілька мод)
    n = 3
    span = x2 - x1
    pts_up, pts_dn = [], []
    for i in range(0, span + 1, 4):
        ph = math.sin(math.pi * n * i / span)
        pts_up.append((x1 + i, lineY - 2 - 7 * ph))
        pts_dn.append((x1 + i, lineY + 2 + 7 * ph))
    els.append(polyline(pts_up, color=NEG, sw=2))
    els.append(polyline(pts_dn, color=NEG, sw=2))
    # вузли (де хвиля = 0) — короткі риски
    for i in range(0, n + 1):
        xn = x1 + span * i / n
        els.append(line(xn, lineY - 20, xn, lineY + 20, color=MUTED, sw=1, dash="3 3"))
    els.append(text((x1 + x2) / 2, lineY + 40, "стоячі хвилі (моди) — кожна тримає в середньому kT", size=13, color=NEG))

    # рівновага: потоки в обидва боки рівні
    ay = cy + 92
    els.append(arrow(x1 + 30, ay, x2 - 30, ay, color=POS, sw=2.2))
    els.append(arrow(x2 - 30, ay + 22, x1 + 30, ay + 22, color=POS, sw=2.2))
    els.append(text((x1 + x2) / 2, ay - 8, "потужність праворуч", size=12, color=MUTED))
    els.append(text((x1 + x2) / 2, ay + 40, "= потужність ліворуч   (рівновага)", size=12, color=MUTED))

    # підсумкова рамка
    body, _, _ = textbox(W / 2, H - 40,
                         "Число мод у смузі B:  N = 2·L·B / v .   Енергія kT на моду  →  потік від однієї R:  P = k·T·B .",
                         size=14, fill="#eef3ff", stroke=NEG)
    els.append(body)
    return render(os.path.join(IMG, 'nyquist-line.svg'), W, H, *els,
                  title="Уявний дослід Найквіста: рівновага двох резисторів")


# ── 5. Класична густина проти квантової поправки Планка ───────────────────────
def fig_quantum_rolloff():
    W, H = 740, 420
    els = []
    x0, y0 = 84, 330
    axw, axh = 596, 250
    els.append(line(x0, y0, x0 + axw, y0, color=INK, sw=2))
    els.append(line(x0, y0, x0, y0 - axh, color=INK, sw=2))
    els.append(text(x0 + axw, y0 + 26, "частота f →  (лог)", size=13, anchor="end"))
    els.append(text(x0 - 6, y0 - axh - 8, "густина потужності шуму", size=13, anchor="start"))

    # рівень «класики» (4kTR): рівна лінія
    flat = y0 - 150
    els.append(line(x0, flat, x0 + axw, flat, color=NEG, sw=3, dash="6 4"))
    els.append(text(x0 + 8, flat - 12, "класика: 4kTR — рівна на всіх частотах", size=13, color=NEG, anchor="start"))

    # квантова крива: збігається з класикою, тоді валиться після f≈kT/h
    # намалюємо як planck-подібний спад: рівна ділянка, далі різкий загин донизу
    fbreak = x0 + 0.66 * axw
    qpts = []
    for i in range(0, axw + 1, 4):
        x = x0 + i
        if x <= fbreak:
            y = flat
        else:
            t = (x - fbreak) / (x0 + axw - fbreak)  # 0..1
            # експоненційний спад до майже осі
            drop = (y0 - 12 - flat) * (1 - math.exp(-3.2 * t))
            y = flat + drop
        qpts.append((x, y))
    els.append(polyline(qpts, color=POS, sw=3))
    els.append(text(fbreak + 118, flat + 70, "квант: спад після f ≈ kT/h", size=13, color=POS))

    # вертикаль на частоті зламу
    els.append(line(fbreak, y0, fbreak, flat, color=MUTED, sw=1.5, dash="4 3"))
    els.append(text(fbreak, y0 + 20, "f ≈ kT/h", size=12, color=MUTED))
    els.append(text(fbreak, y0 - axh + 6, "~ терагерци при 300 K", size=12, color=MUTED))

    # зона звичайної електроніки — ліворуч, заштрихована легко
    els.append(fillrect(x0, flat - 2, fbreak - x0, y0 - flat + 2, FIELD, 0.10))
    els.append(text((x0 + fbreak) / 2, flat + 60, "уся звичайна електроніка", size=13, color=FIELD))
    els.append(text((x0 + fbreak) / 2, flat + 80, "тут класика точна", size=13, color=FIELD))

    body, _, _ = textbox(W / 2, 54,
                         "4kTR — це низькочастотна межа точнішого закону Планка. До терагерців різниці немає.",
                         size=14, fill="#eef3ff", stroke=NEG)
    els.append(body)
    return render(os.path.join(IMG, 'quantum-rolloff.svg'), W, H, *els,
                  title="Чому 4kTR — це класична межа: квантовий спад Планка")


if __name__ == '__main__':
    fig_spectral_density()
    fig_coupling()
    fig_lockin()
    fig_nyquist_line()
    fig_quantum_rolloff()
    print("OK:", os.listdir(IMG))
