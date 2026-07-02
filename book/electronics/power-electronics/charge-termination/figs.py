# -*- coding: utf-8 -*-
"""Фігури до теми «Методи термінації заряду».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Що взагалі означає «повна»: три різні сигнали кінця ───────────────────────
def fig_signals():
    W, H = 780, 420
    f = [text(W / 2, 28, "Три різні сигнали «комірка повна» — за хімією",
              size=16, bold=True)]
    rows = [
        ("Li-ion / LiFePO4", "тримаємо стелю НАПРУГИ,\nловимо спад СТРУМУ",
         "струм у CV впав < C/10", NEG, "#eef3fb"),
        ("NiMH / NiCd", "тримаємо сталий СТРУМ,\nловимо злам НАПРУГИ/ТЕПЛА",
         "−ΔV (пік і спад) або dT/dt", POS, "#fbeee6"),
        ("Свинець", "тримаємо стелю напруги,\nа далі НЕ зупиняємось",
         "переходимо на float (підзаряд)", FIELD, "#e9f7ef"),
    ]
    rh, gap = 92, 18
    bw = 640
    x0 = (W - bw) / 2
    y0 = 66
    for i, (chem, hold, stop, col, fill) in enumerate(rows):
        y = y0 + i * (rh + gap)
        f.append(rect(x0, y, bw, rh, fill=fill, stroke=col, sw=1.8))
        f.append(rect(x0, y, 200, rh, fill="#ffffff", stroke=col, sw=1.8))
        f.append(mtext(x0 + 100, y + rh / 2 - 4, chem, size=14, bold=True, color=col))
        f.append(mtext(x0 + 218, y + 30, hold, size=11.5, color=INK, anchor="start"))
        f.append(text(x0 + 218, y + rh - 16, "стоп: " + stop, size=11.5,
                      color=col, anchor="start", bold=True))
    b, _, _ = textbox(W / 2, 396,
                      "де тримають напругу — стоп за струмом; де тримають струм — стоп за напругою/теплом; свинець узагалі не «стопить»",
                      size=10.5, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "signals.svg"), W, H, *f)


# ── Термінація Li-ion за спадом струму в CV, і чому таймер страхує ────────────
def fig_taper():
    W, H = 760, 430
    f = [text(W / 2, 28, "Li-ion: кінець ловлять за спадом струму в CV",
              size=16, bold=True)]
    ox, oy = 80, 330
    span_x = 600
    top = 78
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 24, "час →", size=11, color=MUTED, anchor="end"))

    xcc = ox + span_x * 0.42
    f.append(line(xcc, top, xcc, oy, color=MUTED, sw=1.0, dash="4,4"))
    f.append(text((ox + xcc) / 2, top - 8, "CC", size=13, bold=True, color=MUTED))
    f.append(text((xcc + ox + span_x) / 2, top - 8, "CV", size=13, bold=True, color=MUTED))

    i_full = oy - 200
    i_c10 = oy - 40           # рівень порога C/10
    # крива струму: плато в CC, експ-спад у CV
    ipts = []
    x_term = None
    for i in range(0, 241):
        t = i / 240.0
        xx = ox + t * span_x
        if xx <= xcc:
            yy = i_full
        else:
            tt = (xx - xcc) / (ox + span_x - xcc)
            yy = oy + (i_full - oy) * math.exp(-3.4 * tt)
        ipts.append((xx, yy))
        if x_term is None and xx > xcc and yy >= i_c10:
            x_term = xx

    # заборонена зона підзаряду після стопу — малюємо ПЕРШОЮ (фон під кривою)
    if x_term:
        f.append(rect(x_term, top + 6, ox + span_x - x_term, oy - top - 6,
                      fill="#fbeee6", stroke="none", sw=0, rx=4))
        f.append(mtext((x_term + ox + span_x) / 2, top + 42,
                       "далі НЕ доливаємо\n(інакше осідання)",
                       size=11, color=POS))
    # поріг C/10
    f.append(line(ox, i_c10, ox + span_x, i_c10, color=NEG, sw=1.1, dash="6,4"))
    f.append(text(ox - 8, i_c10 + 4, "C/10", size=11, color=NEG, anchor="end"))
    # крива струму поверх фону
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in ipts), POS))
    # точка термінації
    if x_term:
        f.append(circle(x_term, i_c10, 5, fill="#ffffff", stroke=INK, sw=2))
        f.append(text(x_term + 8, i_c10 - 10, "СТОП", size=12, bold=True,
                      color=INK, anchor="start"))
    # підпис осі струму
    f.append(text(ox - 8, top + 8, "струм", size=11, color=POS, anchor="end"))

    b, _, _ = textbox(W / 2, 405,
                      "поріг зазвичай C/10 (буває 0.02–0.07C ≈ 92–99% ємності) · паралельно тикає таймер-страховка, якщо струм так і не впав",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "taper.svg"), W, H, *f)


# ── NiMH: пік напруги, −ΔV і злам температури як два незалежні сигнали ────────
def fig_nimh():
    W, H = 820, 440
    f = [text(W / 2, 28, "NiMH: напруга робить пік і осідає (−ΔV), тепло — злам угору",
              size=15, bold=True)]
    ox, oy = 90, 300
    span_x = 640
    top = 70
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 24, "час заряду →", size=11, color=MUTED, anchor="end"))

    # точка повноти — де напруга піка
    xpk = ox + span_x * 0.72

    # крива напруги: поволі росте, гострий пік у xpk, тоді осідає
    vpts = []
    base = oy - 60
    peak = oy - 150
    for i in range(0, 261):
        t = i / 260.0
        xx = ox + t * span_x
        if xx <= xpk:
            tt = (xx - ox) / (xpk - ox)
            yy = base - (base - peak) * (tt ** 1.7)
        else:
            tt = (xx - xpk) / (ox + span_x - xpk)
            yy = peak + (base - peak) * 0.28 * (1 - math.exp(-3.0 * tt))
        vpts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in vpts), NEG))
    f.append(text(ox - 8, top + 20, "напруга", size=11, color=NEG, anchor="end"))

    # крива температури: рівна, тоді різко вгору після повноти
    tpts = []
    tbase = oy - 18
    for i in range(0, 261):
        t = i / 260.0
        xx = ox + t * span_x
        if xx <= xpk:
            yy = tbase - 8 * (xx - ox) / (xpk - ox)
        else:
            tt = (xx - xpk) / (ox + span_x - xpk)
            yy = (tbase - 8) - 120 * (tt ** 1.4)
        tpts.append((xx, max(top + 30, yy)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in tpts), POS))
    f.append(text(ox + span_x - 4, oy - 8, "температура", size=11, color=POS, anchor="end"))

    # вертикаль повноти
    f.append(line(xpk, top + 10, xpk, oy, color=MUTED, sw=1.0, dash="4,4"))
    f.append(text(xpk, top + 4, "повна", size=11.5, bold=True, color=MUTED))
    # маркери піка й спаду
    f.append(circle(xpk, peak, 5, fill="#ffffff", stroke=NEG, sw=2))
    f.append(text(xpk + 10, peak - 6, "пік", size=11, color=NEG, anchor="start"))
    f.append(mtext(xpk + 84, peak + 30, "−ΔV: спад\n5–10 мВ/елем.", size=10.5, color=NEG, anchor="start"))

    b, _, _ = textbox(W / 2, 410,
                      "−ΔV у NiMH слабкий (у NiCd різкіший), тож надійніше ловити dT/dt ≈ 1 °C/хв · таймер і абсолютна межа температури — страховка",
                      size=10, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "nimh.svg"), W, H, *f)


# ── Дзеркало: Li-ion «стоп і спокій» vs Ni/Pb «підзаряд назавжди» ─────────────
def fig_after():
    W, H = 780, 380
    f = [text(W / 2, 28, "Після «повної»: літій зупиняють, Ni/Pb підживлюють",
              size=16, bold=True)]
    # ліва колонка — Li-ion
    lx = 60
    cw = 320
    f.append(rect(lx, 60, cw, 262, fill="#eef3fb", stroke=NEG, sw=1.8))
    f.append(text(lx + cw / 2, 88, "Li-ion / LiFePO4", size=15, bold=True, color=NEG))
    steps_l = [
        "струм у CV впав < C/10 → СТОП",
        "далі струм НЕ подаємо взагалі",
        "напруга сама просіла від\nсаморозряду?",
        "→ перезапустити цикл наново\n(top-off), а не «доливати»",
    ]
    yy = 118
    for i, s in enumerate(steps_l):
        f.append(mtext(lx + 18, yy, s, size=11.5, color=INK, anchor="start"))
        yy += 24 + (14 if "\n" in s else 0)
    f.append(text(lx + cw / 2, 312, "тримати повну під напругою = старіння/осідання",
                  size=10, color=POS, italic=True))

    # права колонка — Ni/Pb
    rx = 400
    f.append(rect(rx, 60, cw, 262, fill="#e9f7ef", stroke=FIELD, sw=1.8))
    f.append(text(rx + cw / 2, 88, "NiMH / NiCd / свинець", size=15, bold=True, color=FIELD))
    steps_r = [
        "спіймали кінець (−ΔV/dT/dt/float)",
        "переходимо на МАЛИЙ підзаряд",
        "trickle (Ni) / float (Pb):\nтече весь час",
        "компенсує саморозряд —\nдля цих хімій це нормально",
    ]
    yy = 118
    for i, s in enumerate(steps_r):
        f.append(mtext(rx + 18, yy, s, size=11.5, color=INK, anchor="start"))
        yy += 24 + (14 if "\n" in s else 0)
    f.append(text(rx + cw / 2, 312, "той самий підзаряд у літії = пошкодження",
                  size=10, color=POS, italic=True))

    render(os.path.join(IMG, "after.svg"), W, H, *f)


# ── ІСТОРІЯ −ΔV: чому те, що чітко на NiCd, розмивається на NiMH ───────────────
def fig_delta_v_compare():
    """Дві криві напруги в одних осях: гострий пік-і-провал NiCd проти
    пологого горбка NiMH. Показує ЧОМУ поріг, налаштований на NiCd, або
    проскакує повноту NiMH, або спрацьовує на випадковому шумі."""
    W, H = 820, 460
    f = [text(W / 2, 28, "Той самий −ΔV: різкий на NiCd, майже зниклий на NiMH",
              size=15, bold=True)]
    ox, oy = 80, 330
    span_x = 660
    top = 70
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 24, "заряд →", size=11, color=MUTED, anchor="end"))
    f.append(mtext(ox - 10, top + 34, "напруга\nна елемент", size=10.5,
                   color=MUTED, anchor="end"))

    xpk = ox + span_x * 0.70          # мить повноти — спільна для обох

    # NiCd: помітний підйом, гострий пік, ВИРАЗНИЙ провал (≈ 5 мВ, тут перебільшено для ока)
    base_c = oy - 70
    peak_c = oy - 170
    drop_c = peak_c + 46             # глибокий провал після піка
    cpts = []
    for i in range(0, 261):
        t = i / 260.0
        xx = ox + t * span_x
        if xx <= xpk:
            tt = (xx - ox) / (xpk - ox)
            yy = base_c - (base_c - peak_c) * (tt ** 1.8)
        else:
            tt = (xx - xpk) / (ox + span_x - xpk)
            yy = peak_c + (drop_c - peak_c) * (1 - math.exp(-4.2 * tt))
        cpts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in cpts), NEG))
    f.append(circle(xpk, peak_c, 4.5, fill="#ffffff", stroke=NEG, sw=2))
    f.append(text(ox + 8, base_c - 6, "NiCd", size=13, bold=True, color=NEG, anchor="start"))
    # стрілка-виноска на провал NiCd
    f.append(line(xpk + 70, peak_c + 6, xpk + 22, drop_c - 4, color=NEG, sw=1.0, dash="3,3"))
    f.append(mtext(xpk + 74, peak_c + 6, "чіткий провал\n≈ 5 мВ — легко\nспіймати",
                   size=10.5, color=NEG, anchor="start"))

    # NiMH: пологіший підйом, ледь помітний горбок, майже плаский «провал»
    base_m = oy - 26
    peak_m = oy - 74
    drop_m = peak_m + 9              # ледь-ледь осідає
    mpts = []
    for i in range(0, 261):
        t = i / 260.0
        xx = ox + t * span_x
        if xx <= xpk:
            tt = (xx - ox) / (xpk - ox)
            yy = base_m - (base_m - peak_m) * (tt ** 1.4)
        else:
            tt = (xx - xpk) / (ox + span_x - xpk)
            yy = peak_m + (drop_m - peak_m) * (1 - math.exp(-2.4 * tt))
        mpts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="1,0"/>'
             % (" ".join("%.1f,%.1f" % p for p in mpts), POS))
    f.append(circle(xpk, peak_m, 4.5, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(ox + 8, base_m - 6, "NiMH", size=13, bold=True, color=POS, anchor="start"))
    f.append(mtext(xpk + 20, peak_m - 16, "ледь горбок\n(< шуму й дрейфу)",
                   size=10.5, color=POS, anchor="start"))

    f.append(line(xpk, top + 10, xpk, oy, color=MUTED, sw=1.0, dash="4,4"))
    f.append(text(xpk, top + 4, "повна", size=11, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 432,
                      "поріг, вивірений на глибокий провал NiCd, на пологому NiMH або проскакує повноту, або ловить випадковий шум",
                      size=10.5, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "nicd-vs-nimh-dv.svg"), W, H, *f)


# ── ІСТОРІЯ −ΔV: одна фізична подія — два сигнали кінця ────────────────────────
def fig_one_event_two_signals():
    """Причинний ланцюг: повнота → кисень рекомбінує (екзотермічно) → нагрів →
    (через від'ємний темп. коеф. ЕРС) напруга падає. −ΔV і dT/dt — дві грані
    ОДНІЄЇ події; тепло первинне, тому dT/dt надійніший."""
    W, H = 820, 400
    f = [text(W / 2, 28, "−ΔV і dT/dt — дві грані однієї події в мить повноти",
              size=15, bold=True)]

    # центральна «подія»
    ecx, ecy, ew, eh = W / 2, 96, 360, 52
    f.append(rect(ecx - ew / 2, ecy - eh / 2, ew, eh, fill="#fff6e6",
                  stroke="#b9770e", sw=1.8, rx=8))
    f.append(mtext(ecx, ecy - 6,
                   "комірка повна → надлишок струму йде не в реакцію,",
                   size=11, color=INK))
    f.append(mtext(ecx, ecy + 11,
                   "а на кисень, що рекомбінує на аноді (ЕКЗОТЕРМІЧНО)",
                   size=11, color=INK, bold=True))

    # спільний вузол «нагрів»
    hcx, hcy = W / 2, 188
    f.append(line(ecx, ecy + eh / 2, hcx, hcy - 24, color="#b9770e", sw=1.8))
    hb, hw, hh = textbox(hcx, hcy, "комірка різко гріється",
                         size=12, bold=True, fill="#fdecea", stroke=POS)
    f.append(hb)

    # ліва гілка — dT/dt (первинний, прямий)
    lx, ly = W / 2 - 200, 300
    f.append(line(hcx - hw / 2, hcy, lx + 90, ly - 34, color=POS, sw=2.2))
    lb, lw, lh = textbox(lx + 90, ly, "dT/dt угору\n(ПРЯМИЙ наслідок тепла)",
                         size=11.5, bold=True, fill="#fdecea", stroke=POS, color=POS)
    f.append(lb)
    f.append(text(lx + 90, ly + 44, "сильний, чіткий сигнал", size=10,
                  color=POS, italic=True))

    # права гілка — −ΔV (вторинний, через тепловий коефіцієнт)
    rx = W / 2 + 200
    f.append(line(hcx + hw / 2, hcy, rx - 90, ly - 34, color=NEG, sw=1.6, dash="5,4"))
    f.append(mtext((hcx + rx) / 2 + 14, hcy + 30,
                   "ЕРС має ВІД'ЄМНИЙ\nтемп. коефіцієнт",
                   size=10, color=NEG, anchor="middle"))
    rb, rw, rh = textbox(rx - 90, ly, "−ΔV: напруга осідає\n(ПОБІЧНИЙ наслідок)",
                         size=11.5, bold=True, fill="#eef3fb", stroke=NEG, color=NEG)
    f.append(rb)
    f.append(text(rx - 90, ly + 44, "слабкий на NiMH — губиться", size=10,
                  color=NEG, italic=True))

    b, _, _ = textbox(W / 2, 372,
                      "тепло первинне; напруга падає лише як його тінь — тому dT/dt переживає перехід на NiMH, а −ΔV ні",
                      size=10.5, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "one-event-two-signals.svg"), W, H, *f)


if __name__ == "__main__":
    fig_signals()
    fig_taper()
    fig_nimh()
    fig_after()
    fig_delta_v_compare()
    fig_one_event_two_signals()
    print("OK: 6 figures ->", IMG)
