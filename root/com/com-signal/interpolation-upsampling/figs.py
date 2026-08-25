# -*- coding: utf-8 -*-
"""Фігури до теми «Інтерполяція (upsampling): вставлення нулів і згладжувальний фільтр».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── допоміжні функції ────────────────────────────────────────────────────────
def stem(x, base, h, color, w=2.5, dot=True):
    out = line(x, base, x, base - h, color=color, sw=w)
    if dot and abs(h) > 0:
        out += circle(x, base - h, 3.0, fill=color, stroke=color, sw=0)
    return out


def axis(x0, x1, y, color=INK, sw=1.6, label=None):
    out = line(x0, y, x1 + 6, y, color=color, sw=sw)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (x1 + 14, y, x1 + 6, y - 4, x1 + 6, y + 4, color))
    if label:
        out += text(x1 + 6, y + 20, label, size=10, color=MUTED, italic=True, anchor="end")
    return out


def blob(xl, xr, base, height_fn, color, opacity=0.5, N=48):
    pts = [(xl, base)]
    for i in range(N + 1):
        t = i / N
        x = xl + (xr - xl) * t
        pts.append((x, base - height_fn(t)))
    pts.append((xr, base))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
            'stroke-width="1.4"/>' % (poly, color, opacity, color))


# ── 1. Канонічний ланцюг інтерполяції ─────────────────────────────────────────
def fig_chain():
    W, H = 790, 210
    f = [text(W / 2, 28, "Інтерполяція — дві дії: вставлення нулів, тоді згладжувальний фільтр",
              size=15, bold=True)]
    ycy = 108

    # вхід
    f.append(text(50, ycy - 2, "x[n]", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(50, ycy + 20, "12 кГц", size=11, color=MUTED, anchor="start"))
    f.append(arrow(100, ycy, 150, ycy, color=INK, sw=1.9))

    # блок ↑L
    b1x, b1w = 152, 96
    f.append(rect(b1x, ycy - 30, b1w, 60, fill="#eef2fb", stroke=NEG, sw=1.8))
    f.append(text(b1x + b1w / 2, ycy + 8, "↑ L", size=24, color=NEG, bold=True))

    f.append(arrow(b1x + b1w + 2, ycy, b1x + b1w + 58, ycy, color=INK, sw=1.9))

    # проміжний сигнал w[m]
    mid_x = b1x + b1w + 30
    f.append(text(mid_x, ycy - 38, "w[m]", size=12, color=MUTED, bold=True, anchor="middle"))

    # блок ФНЧ
    b2x, b2w = b1x + b1w + 60, 210
    f.append(rect(b2x, ycy - 30, b2w, 60, fill="#eaf6ef", stroke=FIELD, sw=1.8))
    f.append(mtext(b2x + b2w / 2, ycy - 4, ["Згладжувальний ФНЧ H(z)", "зріз fs/2L = 6 кГц, підсилення L"],
                   size=12, color=INK))

    f.append(arrow(b2x + b2w + 2, ycy, b2x + b2w + 58, ycy, color=INK, sw=1.9))

    # вихід
    ox = b2x + b2w + 66
    f.append(text(ox, ycy - 2, "y[m]", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(ox, ycy + 20, "48 кГц", size=11, color=MUTED, anchor="start"))

    f.append(text(W / 2, 188,
                  "розширювач вставляє L-1 нулів · фільтр зрізає дзеркальні образи та підсилює сигнал у L разів",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "chain.svg"), W, H, *f)


# ── 2. Вставлення нулів у часовій області ──────────────────────────────────────
def fig_time_domain():
    W, H = 760, 520
    f = [text(W / 2, 28, "Інтерполяція у часі: нульове заповнення та дія ФНЧ",
              size=15, bold=True)]

    x0, x1 = 80, 680
    span = x1 - x0
    L = 4
    N_orig = 6
    dx = span / ((N_orig - 1) * L)

    # вхідні значння (синусоїдна форма)
    vals = [20, 55, 75, 45, 10, -35]

    # Панель A: x[n]
    yA = 120
    f.append(text(x0, yA - 85, "1 · вхідний сигнал x[n] (рідкі відліки)", size=11.5, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yA))
    for i, v in enumerate(vals):
        cx = x0 + i * L * dx
        f.append(stem(cx, yA, v, FIELD, w=3.0))

    # Панель B: w[m] після ↑L (вставлення нулів)
    yB = 270
    f.append(text(x0, yB - 85, "2 · після вставлення L-1 нулів w[m] (L=4)", size=11.5, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yB))
    for i in range((N_orig - 1) * L + 1):
        cx = x0 + i * dx
        if i % L == 0:
            v = vals[i // L]
            f.append(stem(cx, yB, v, FIELD, w=2.5))
        else:
            # нульовий відлік
            f.append(circle(cx, yB, 2.5, fill=POS, stroke=POS, sw=0))

    # Панель C: y[m] після ФНЧ
    yC = 420
    f.append(text(x0, yC - 85, "3 · після згладжувального ФНЧ y[m] (інтерпольована крива)", size=11.5, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yC))

    # плавна інтерполяційна крива
    curve_pts = []
    for i in range((N_orig - 1) * L + 1):
        cx = x0 + i * dx
        t = i / L
        idx = int(t)
        frac = t - idx
        if idx < len(vals) - 1:
            v = vals[idx] * (1 - frac) + vals[idx + 1] * frac
        else:
            v = vals[-1]
        f.append(stem(cx, yC, v, NEG, w=2.0))
        curve_pts.append((cx, yC - v))

    poly_str = " ".join("%.1f,%.1f" % p for p in curve_pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4,3"/>' % (poly_str, FIELD))

    f.append(text(W / 2, 500,
                  "вставлені нулі тримають точні часові позиції · ФНЧ розраховує проміжні значення замість нулів",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "time-domain.svg"), W, H, *f)


# ── 3. Спектральне дзеркалювання у частотній області ──────────────────────────
def fig_spectral_imaging():
    W, H = 760, 480
    f = [text(W / 2, 28, "Спектральне дзеркалювання (spectral imaging) при upsampling (L=4)",
              size=15, bold=True)]

    x0, x1 = 90, 670
    span = x1 - x0
    mid = x0 + span * 0.5

    def main_lobe(t):
        return 65 * math.exp(-((t / 0.18) ** 2))

    # Панель A: вихідний спектр X(exp(j*omega))
    yA = 120
    f.append(text(x0, yA - 70, "1 · вихідний спектр X(e^{jω}): одна корисна смуга у [-π, π]",
                  size=11, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yA, label="ω"))
    f.append(blob(x0 + span * 0.3, x0 + span * 0.7, yA, lambda t: main_lobe((t - 0.5) * 2), FIELD, opacity=0.55))
    f.append(line(mid, yA, mid, yA - 70, color=MUTED, sw=1.2, dash="4,3"))
    f.append(text(x0 + span * 0.3, yA + 18, "-π", size=10, color=MUTED))
    f.append(text(mid, yA + 18, "0", size=10, color=MUTED))
    f.append(text(x0 + span * 0.7, yA + 18, "π", size=10, color=MUTED))

    # Панель B: після ↑L (стискання осі, поява L-1 дзеркальних образів)
    yB = 260
    f.append(text(x0, yB - 70, "2 · після ↑4: вісь стиснулась, з'явилось 3 дзеркальні образи (spectral images)",
                  size=11, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yB, label="ω"))

    # L=4 образів
    subw = span / 4.0
    for k in range(4):
        lx = x0 + k * subw
        rx = lx + subw
        col = FIELD if k == 0 else POS
        opac = 0.55 if k == 0 else 0.35
        f.append(blob(lx + subw * 0.3, lx + subw * 0.7, yB, lambda t: main_lobe((t - 0.5) * 2), col, opacity=opac))
        if k > 0:
            f.append(text(lx + subw * 0.5, yB - 72, "образ", size=9.5, color=POS, bold=True))

    # маска ФНЧ (зелений пунктир зі зрізом π/4)
    cut_rx = x0 + subw * 0.8
    f.append(line(x0, yB - 80, cut_rx, yB - 80, color=FIELD, sw=2.0, dash="5,3"))
    f.append(line(cut_rx, yB - 80, cut_rx + 15, yB, color=FIELD, sw=2.0, dash="5,3"))
    f.append(text(cut_rx + 20, yB - 65, "ФНЧ (зріз π/4, підсилення L)", size=10, color=FIELD, bold=True, anchor="start"))

    # Панель C: після ФНЧ Y(exp(j*omega))
    yC = 400
    f.append(text(x0, yC - 70, "3 · після ФНЧ: дзеркальні образи вилучено, базову смугу відновлено",
                  size=11, color=INK, bold=True, anchor="start"))
    f.append(axis(x0, x1, yC, label="ω"))
    f.append(blob(x0 + subw * 0.3, x0 + subw * 0.7, yC, lambda t: main_lobe((t - 0.5) * 2) * 1.2, FIELD, opacity=0.6))
    f.append(text(x0 + subw * 0.5, yC + 18, "π/4", size=10, color=FIELD, bold=True))
    f.append(text(x1, yC + 18, "π", size=10, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "spectral-imaging.svg"), W, H, *f)


# ── 4. Поліфазна структура інтерполятора ─────────────────────────────────────
def fig_polyphase_interpolator():
    W, H = 800, 310
    f = [text(W / 2, 28, "Поліфазна структура інтерполятора: відсутність множень на нулі",
              size=15, bold=True)]

    y0 = 75
    dy = 52
    L = 4

    # Вхід x[n]
    f.append(text(50, y0 + dy * 1.5, "x[n]", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(50, y0 + dy * 1.5 + 20, "fs", size=11, color=MUTED, anchor="start"))
    f.append(line(90, y0 + dy * 1.5, 140, y0 + dy * 1.5, color=INK, sw=1.8))
    f.append(line(140, y0, 140, y0 + dy * (L - 1), color=INK, sw=1.8))

    # Субфільтри E_p(z)
    sub_x = 180
    sub_w = 170
    for p in range(L):
        cy = y0 + p * dy
        f.append(arrow(140, cy, sub_x, cy, color=INK, sw=1.8))
        f.append(rect(sub_x, cy - 18, sub_w, 36, fill="#eaf6ef", stroke=FIELD, sw=1.6))
        f.append(text(sub_x + sub_w / 2, cy + 5, "Субфільтр E_%d(z)" % p, size=11.5, color=INK, bold=True))
        f.append(line(sub_x + sub_w, cy, sub_x + sub_w + 50, cy, color=INK, sw=1.8))

    # Комутатор (Демультиплексор)
    comm_x = sub_x + sub_w + 60
    f.append(rect(comm_x, y0 - 10, 80, dy * (L - 1) + 20, fill="#eef2fb", stroke=NEG, sw=1.8, rx=6))
    f.append(mtext(comm_x + 40, y0 + dy * 1.5 - 6, ["Комутатор", "(обхід 0..L-1)"], size=11, color=NEG, bold=True))

    # Вихід y[m]
    out_x = comm_x + 140
    f.append(arrow(comm_x + 80, y0 + dy * 1.5, out_x, y0 + dy * 1.5, color=INK, sw=2.0))
    f.append(text(out_x + 10, y0 + dy * 1.5 - 2, "y[m]", size=14, color=INK, bold=True, anchor="start"))
    f.append(text(out_x + 10, y0 + dy * 1.5 + 20, "L · fs", size=11, color=MUTED, anchor="start"))

    f.append(text(W / 2, 288,
                  "кожен поліфазний фільтр обчислюється на НИЗЬКІЙ частоті fs без обчислень з нулями",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "polyphase-interpolator.svg"), W, H, *f)


# ── 5. Шляхетна тотожність для інтерполяції ──────────────────────────────────
def fig_noble_identity_up():
    W, H = 800, 300
    f = [text(W / 2, 30, "Шляхетна тотожність інтерполяції: перенесення фільтра до вставлення нулів",
              size=15, bold=True)]

    def blk(x, y, w, h, lines, stroke, fill, size=12):
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8)
        out += mtext(x + w / 2, y + h / 2 - (len(lines) - 1) * size * 0.65 + size * 0.35,
                     lines, size=size, color=INK)
        return out

    def arr(x1, y, x2):
        return arrow(x1, y, x2, y, color=INK, sw=1.8)

    # ── верхній ланцюг: ↑L → H(z^L) (фільтр на високій частоті L·fs) ──
    yT = 96
    f.append(text(64, yT + 4, "x[n]", size=13, bold=True, anchor="start"))
    f.append(text(64, yT + 23, "fs", size=10.5, color=MUTED, anchor="start"))
    f.append(arr(102, yT, 150))
    f.append(blk(152, yT - 25, 66, 50, ["↑L"], NEG, "#eef2fb", size=16))
    f.append(arr(220, yT, 266))
    f.append(blk(268, yT - 27, 156, 54, ["H(z^L)", "фільтр на L·fs"], POS, "#fdecea"))
    f.append(arr(426, yT, 472))
    f.append(text(478, yT + 4, "y[m]", size=13, bold=True, anchor="start"))
    f.append(text(566, yT + 4, "≈ K·L·fs множень/с", size=11, color=POS, italic=True, anchor="start"))

    f.append(text(W / 2, 156, "≡", size=30, bold=True))

    # ── нижній ланцюг: H(z) → ↑L (фільтр на низькій частоті fs) ──
    yB = 214
    f.append(text(64, yB + 4, "x[n]", size=13, bold=True, anchor="start"))
    f.append(text(64, yB + 23, "fs", size=10.5, color=MUTED, anchor="start"))
    f.append(arr(102, yB, 150))
    f.append(blk(152, yB - 27, 156, 54, ["H(z)", "фільтр на fs"], FIELD, "#eaf6ef"))
    f.append(arr(310, yB, 356))
    f.append(blk(358, yB - 25, 66, 50, ["↑L"], NEG, "#eef2fb", size=16))
    f.append(arr(426, yB, 472))
    f.append(text(478, yB + 4, "y[m]", size=13, bold=True, anchor="start"))
    f.append(text(566, yB + 4, "≈ K·fs множень/с", size=11, color=FIELD, italic=True, anchor="start"))

    f.append(text(W / 2, 286,
                  "обчислення фільтра до розширення зменшує кількість множень у L разів",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "noble-identity-up.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chain()
    fig_time_domain()
    fig_spectral_imaging()
    fig_polyphase_interpolator()
    fig_noble_identity_up()
    print("OK: 5 figures generated into", IMG)
