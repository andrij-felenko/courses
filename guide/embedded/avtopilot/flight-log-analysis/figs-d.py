# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ статті «Аналіз логів польоту/поїздки»
(guide/embedded/avtopilot/flight-log-analysis, файл flight-log-analysis-d.md).
Чистий Python, без залежностей; svgkit — зі scripts/ (не переписувати)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Помилка стеження розкладена: DesRoll проти Roll — фазове відставання τ і
#    перерегулювання; знизу — сама помилка e=Des−Act. Показує, ЯК за формою
#    кривих читати надлишок D (пилка) чи брак P (відставання).
# ─────────────────────────────────────────────────────────────────────────────
def fig_tracking_error():
    W, H = 960, 560
    frags = [text(W / 2, 40, "Задане проти виміряного: що каже сама форма кривих", size=13, color=MUTED)]

    ox, oy = 90, 250            # вісь верхнього графіка (нульова лінія крену)
    aw, ah = 780, 150
    # рамка верхнього графіка
    frags.append(line(ox, oy - ah, ox, oy + ah * 0.55, color=INK, sw=1.6))   # Y
    frags.append(line(ox, oy, ox + aw, oy, color="#c9ccd1", sw=1.0))          # нуль
    frags.append(text(ox - 58, oy - ah + 6, "крен", size=12, color=INK))
    frags.append(text(ox - 58, oy - ah + 22, "°", size=12, color=MUTED))

    # Задана крива: різкий крок-запит (трапеція вгору й тримати)
    N = 200
    def des_val(k):
        # 0 до 30, крок біля t≈0.22, плато 20°
        x = k / N
        if x < 0.22:
            return 0.0
        return 20.0
    # Виміряна крива: із фазовим відставанням + перерегулюванням + затуханням
    def act_val(k):
        x = k / N
        if x < 0.22:
            return 0.0
        t = (x - 0.22) * 9.0            # локальний час після кроку
        # реакція другого порядку: підйом + затухаюче коливання
        env = 1 - math.exp(-1.6 * t)
        osc = 0.32 * math.exp(-1.1 * t) * math.sin(4.2 * t)
        return 20.0 * (env + osc)

    def to_xy(k, v):
        return ox + aw * (k / N), oy - v * (ah / 26.0)

    # намалювати задану (сходинка) синім штрихом
    dpts = [to_xy(k, des_val(k)) for k in range(N + 1)]
    dpath = "M %.1f %.1f " % dpts[0] + " ".join("L %.1f %.1f" % p for p in dpts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6 4"/>' % (dpath, NEG))
    # виміряна суцільним червоним
    apts = [to_xy(k, act_val(k)) for k in range(N + 1)]
    apath = "M %.1f %.1f " % apts[0] + " ".join("L %.1f %.1f" % p for p in apts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (apath, POS))

    # легенда
    frags.append(line(ox + 250, oy - ah + 4, ox + 280, oy - ah + 4, color=NEG, sw=2.0, dash="6 4"))
    frags.append(text(ox + 350, oy - ah + 8, "DesRoll — що автопілот хотів", size=12, color=NEG, anchor="middle"))
    frags.append(line(ox + 250, oy - ah + 24, ox + 280, oy - ah + 24, color=POS, sw=2.4))
    frags.append(text(ox + 344, oy - ah + 28, "Roll — що вийшло насправді", size=12, color=POS, anchor="middle"))

    # позначити фазове відставання τ між кроком і половиною реакції
    x_step = ox + aw * 0.22
    x_half = ox + aw * 0.305
    frags.append(line(x_step, oy + 8, x_step, oy - ah * 0.9, color=MUTED, sw=1.0, dash="2 3"))
    frags.append(line(x_half, oy + 8, x_half, oy - ah * 0.55, color=MUTED, sw=1.0, dash="2 3"))
    frags.append(line(x_step, oy + 30, x_half, oy + 30, color=INK, sw=1.4))
    frags.append(text((x_step + x_half) / 2, oy + 26, "τ", size=13, color=INK, bold=True))
    frags.append(text((x_step + x_half) / 2 + 44, oy + 34, "відставання (фаза)", size=11, color=MUTED, italic=True))

    # позначити перерегулювання (перший горб понад плато)
    peak_k = int(N * 0.40)
    px, py = to_xy(peak_k, act_val(peak_k))
    plat_y = oy - 20.0 * (ah / 26.0)
    frags.append(line(px, py, px, plat_y, color=FIELD, sw=1.2))
    frags.append(text(px + 92, py - 4, "перерегулювання", size=11, color=FIELD, bold=True))
    frags.append(text(px + 92, py + 12, "(перескок за ціль)", size=11, color=MUTED, italic=True))

    # ── Нижній графік: помилка e = Des − Act ─────────────────────────────────
    ey = oy + ah * 0.55 + 120
    frags.append(line(ox, ey - 70, ox, ey + 70, color=INK, sw=1.6))       # Y
    frags.append(line(ox, ey, ox + aw, ey, color="#c9ccd1", sw=1.0))       # нуль
    frags.append(text(ox - 58, ey - 40, "помилка", size=12, color=INK))
    frags.append(text(ox - 58, ey - 24, "e = Des−Act", size=11, color=MUTED))
    escale = 70.0 / 22.0
    epts = []
    for k in range(N + 1):
        e = des_val(k) - act_val(k)
        e = max(-21, min(21, e))
        epts.append((ox + aw * (k / N), ey - e * escale))
    epath = "M %.1f %.1f " % epts[0] + " ".join("L %.1f %.1f" % p for p in epts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (epath, INK))
    frags.append(text(ox + aw * 0.24, ey - 62, "стрибок помилки в мить запиту", size=11, color=MUTED, italic=True))
    frags.append(text(ox + aw * 0.52, ey + 40, "затухаючі коливання помилки — слід D-члена й інерції", size=11, color=MUTED, italic=True))

    # висновок
    frags.append(text(W / 2, H - 20,
                      "Відставання τ росте, коли P замалий (в'яле); коливання помилки густішають, коли D завеликий (пиляє). Форма кривої — це діагноз.",
                      size=11, color=INK, bold=True))
    render(os.path.join(IMG, 'tracking-error.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Ворота нововведення EKF: innovation (нев'язка) проти дозволеної межі
#    gate·σ; квадрат-відношення тесту SP/SV/SM перетинає 1 → відкид виміру →
#    перемикання смуги (lane). Показує, ЩО означають числа NKF/XKF.
# ─────────────────────────────────────────────────────────────────────────────
def fig_ekf_gate():
    W, H = 960, 500
    frags = [text(W / 2, 40, "Ворота нововведення: коли автопілот перестає вірити давачу", size=13, color=MUTED)]

    ox, oy = 95, 330
    aw, ah = 500, 240
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))          # X — час
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))          # Y
    frags.append(text(ox + aw / 2, oy + 36, "час →", size=12, color=INK))
    frags.append(text(ox - 66, oy - ah + 8, "квадрат", size=12, color=INK))
    frags.append(text(ox - 66, oy - ah + 24, "тест-", size=12, color=INK))
    frags.append(text(ox - 66, oy - ah + 40, "відношення", size=12, color=MUTED))

    # межа =1
    y1 = oy - ah * 0.62
    frags.append(line(ox, y1, ox + aw, y1, color=POS, sw=1.6, dash="6 4"))
    frags.append(text(ox + aw + 6, y1 + 4, "= 1", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(ox + aw - 6, y1 - 8, "поріг воріт (gate·σ)", size=11, color=POS, italic=True, anchor="end"))
    # рівень «типово в польоті <0.3»
    y03 = oy - ah * 0.19
    frags.append(line(ox, y03, ox + aw, y03, color=FIELD, sw=1.0, dash="2 3"))
    frags.append(text(ox + aw + 6, y03 + 4, "≈0.3", size=11, color=FIELD, anchor="start"))
    frags.append(text(ox + 8, y03 - 6, "здорові дані", size=11, color=FIELD, italic=True, anchor="start"))

    # крива тест-відношення: тихо низько, тоді стрибок GPS вище 1, тоді спад
    N = 160
    def ratio(k):
        x = k / N
        base = 0.18 + 0.06 * math.sin(x * 14)
        # сплеск біля x≈0.55 (стрибок GPS), перевал за 1
        d = (x - 0.55) / 0.05
        spike = 1.35 * math.exp(-d * d)
        return base + spike
    pts = []
    for k in range(N + 1):
        r = ratio(k)
        yy = oy - (ah * 0.62) * (r / 1.0)          # 1.0 припадає на y1
        yy = max(oy - ah + 6, yy)
        pts.append((ox + aw * (k / N), yy))
    path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, NEG))
    frags.append(text(ox + aw * 0.55, oy - ah - 2, "стрибок GPS", size=11, color=INK, bold=True))
    frags.append(text(ox + aw * 0.55, oy - ah + 14, "нев'язка злітає", size=10, color=MUTED, italic=True))

    # зона «вимір відкинуто»
    xa = ox + aw * 0.47
    xb = ox + aw * 0.63
    frags.append(rect(xa, oy - ah + 4, xb - xa, ah - 4, fill="#fbeceb", stroke="none"))
    frags.append(text((xa + xb) / 2, oy - 12, "вимір\nвідкинуто", size=10, color=POS, bold=True, anchor="middle"))
    # перемалювати криву поверх заливки
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, NEG))

    # ── Права панель: формула тест-відношення й наслідок ──────────────────────
    px = 660
    b1, w1, h1 = textbox(px + 130, 150,
                         "квадрат тест-відношення",
                         size=13, bold=True, pad=10, min_w=250, stroke=INK, fill="#f4f6f8")
    frags.append(b1)
    b2 = fitbox(px, 178, 260, 62,
                "R² = ( нев'язка / (gate · √variance) )²",
                size=12, pad=8, stroke=NEG, fill="#eaf0fd")
    frags.append(b2)
    for i, ln in enumerate([
        "нев'язка = вимір − прогноз",
        "variance = невпевненість оцінки",
        "gate = скільки σ дозволено (EK3_*_I_GATE)",
    ]):
        frags.append(text(px + 6, 262 + i * 22, "• " + ln, size=11, color=INK, anchor="start"))

    b3, w3, h3 = textbox(px + 130, 356, "R² < 1  →  вимір ПРИЙНЯТО", size=12, bold=True, pad=8,
                         min_w=250, stroke=FIELD, fill="#eafaf0")
    frags.append(b3)
    b4, w4, h4 = textbox(px + 130, 392, "R² > 1  →  вимір ВІДКИНУТО", size=12, bold=True, pad=8,
                         min_w=250, stroke=POS, fill="#fbeceb")
    frags.append(b4)
    frags.append(text(px + 130, 432, "довго > 1 по кількох давачах", size=11, color=MUTED, italic=True))
    frags.append(text(px + 130, 448, "→ зміна смуги (lane) або EKF failsafe", size=11, color=INK, bold=True))

    render(os.path.join(IMG, 'ekf-gate.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Спектр до/після фільтра + межа Найквіста: пакетний семплер 1 кГц → стеля
#    500 Гц; гармонійний вирізувач прибирає основну частоту моторів і гармоніки;
#    аліасинг згортає надто високу частоту вниз, якщо семплувати рідше.
# ─────────────────────────────────────────────────────────────────────────────
def fig_notch_nyquist():
    W, H = 980, 520
    frags = [text(W / 2, 40, "Спектр до й після вирізувача; чому стеля — половина частоти семплування", size=13, color=MUTED)]

    ox, oy = 90, 340
    aw, ah = 800, 250
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))          # X
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))          # Y
    frags.append(text(ox + aw / 2, oy + 40, "частота, Гц →", size=12, color=INK))
    frags.append(text(ox - 66, oy - ah / 2, "сила", size=12, color=INK))
    frags.append(text(ox - 66, oy - ah / 2 + 16, "тряски", size=12, color=INK))

    # вісь частот: 0..500 Гц (Найквіст), мітки
    fmax = 500.0
    def fx(hz):
        return ox + aw * (hz / fmax)
    for hz in [0, 100, 200, 300, 400, 500]:
        x = fx(hz)
        frags.append(line(x, oy, x, oy + 6, color=INK))
        frags.append(text(x, oy + 22, str(hz), size=11, color=MUTED))

    # Найквіст-межа при 500 Гц
    frags.append(line(fx(500), oy, fx(500), oy - ah, color=POS, sw=1.6, dash="5 4"))
    frags.append(text(fx(500) - 4, oy - ah + 4, "Найквіст 500 Гц", size=11, color=POS, bold=True, anchor="end"))
    frags.append(text(fx(500) - 4, oy - ah + 20, "(семпл 1 кГц ÷ 2)", size=10, color=MUTED, italic=True, anchor="end"))

    # основна частота моторів і дві гармоніки
    f0 = 132.0
    harms = [f0, 2 * f0, 3 * f0]
    def spectrum(hz, notched):
        floor = 16 + 6 * math.sin(hz / 40.0)
        val = floor
        for i, hf in enumerate(harms):
            amp = [150, 70, 40][i]
            d = (hz - hf) / 6.0
            peak = amp * math.exp(-d * d)
            if notched:
                # вузька яма на кожній гармоніці
                dn = (hz - hf) / 7.0
                peak *= (1 - 0.92 * math.exp(-dn * dn))
            val += peak
        return val

    # крива ДО фільтра (сірий заповнений контур зверху)
    def curve(notched, color, sw, dash=None):
        pts = []
        hz = 0.0
        step = fmax / 300.0
        while hz <= fmax:
            v = spectrum(hz, notched)
            v = min(v, ah - 6)
            pts.append((fx(hz), oy - v))
            hz += step
        p = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % q for q in pts[1:])
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (p, color, sw, d)

    frags.append(curve(False, MUTED, 1.6, dash="4 3"))   # до фільтра
    frags.append(curve(True, NEG, 2.4))                  # після фільтра

    # підписати гармоніки й ями
    labels = ["осн. ~132 Гц", "2-га гармоніка", "3-тя"]
    for i, hf in enumerate(harms):
        x = fx(hf)
        frags.append(line(x, oy - 6, x, oy - ah * 0.75, color=FIELD, sw=1.0, dash="2 3"))
        frags.append(text(x, oy - ah * 0.78 - i * 0, labels[i], size=10, color=FIELD, bold=True))
    # легенда кривих
    frags.append(line(ox + 300, oy - ah + 10, ox + 330, oy - ah + 10, color=MUTED, sw=1.6, dash="4 3"))
    frags.append(text(ox + 300 + 120, oy - ah + 14, "до вирізувача (сирий гіро)", size=11, color=MUTED, anchor="middle"))
    frags.append(line(ox + 300, oy - ah + 30, ox + 330, oy - ah + 30, color=NEG, sw=2.4))
    frags.append(text(ox + 300 + 128, oy - ah + 34, "після вирізувача (ями на гармоніках)", size=11, color=NEG, anchor="middle"))

    # ── Аліасинг: 700 Гц згортається у 300 Гц, якщо семпл 1 кГц ──────────────
    b, bw, bh = textbox(W / 2, oy + 74,
                        "Аліасинг: реальна тряска 700 Гц при семплі 1 кГц з'явиться в спектрі як 300 Гц (700 → |1000−700| = 300).\n"
                        "Тому семплюють ШВИДКО (≥ вдвічі за найвищу цікаву частоту) і фільтрують ДО семплування — інакше привид не відрізниш від правди.",
                        size=11, pad=10, stroke=INK, fill="#f4f6f8")
    frags.append(b)
    render(os.path.join(IMG, 'notch-nyquist.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_tracking_error()
    fig_ekf_gate()
    fig_notch_nyquist()
    print("OK detailed figs written to", IMG)
