# -*- coding: utf-8 -*-
"""Фігури до статті «Режими DCM і CCM у flyback-перетворювачі»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1. Струм у ДВОХ обмотках: DCM (порожній осердя) vs CCM (з поличкою) ─
def fig_windings():
    W, H = 820, 470
    f = []
    # дві панелі одна над одною: DCM зверху, CCM знизу
    ox = 90
    aw = 660
    per = aw / 3.4          # ширина одного циклу
    def panel(oy, title, mode):
        yy = []
        base = oy               # рівень нуля
        top = oy - 92           # стеля піка
        # осі
        f.append(line(ox, base, ox + aw, base, color=INK, sw=1.6))
        f.append(text(ox - 8, base + 4, "0", size=12, color=MUTED, anchor="end"))
        f.append(text(ox - 60, base - 46, title, size=14, bold=True, anchor="start"))
        # два з половиною цикли
        peak = 78
        floor = 30              # «поличка» — залишковий струм у CCM
        x = ox + 6
        cyc = 0
        while x + per <= ox + aw and cyc < 3:
            Ton = per * 0.45
            Toff = per * 0.40
            # PRIMARY (наростає у ВКЛ) — червоний
            if mode == 'DCM':
                # первинна: 0 → пік за Ton
                f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                         % (x, base, x + Ton, base - peak, POS))
                # вторинна (пунктир, синій): пік*n → 0 за Toff, потім мертва пауза
                f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="1 0"/>'
                         % (x + Ton, base - peak, x + Ton + Toff, base, NEG))
                # мертва пауза: жирний нуль
                xd0 = x + Ton + Toff
                xd1 = x + per
                f.append(line(xd0, base, xd1, base, color="#b45309", sw=3.4))
            else:  # CCM
                # первинна: floor → пік (трапеція) за Ton
                f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                         % (x, base - floor, x + Ton, base - peak, POS))
                # вторинна: пік → floor за Toff (не доходить нуля)
                f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                         % (x + Ton, base - peak, x + Ton + Toff, base - floor, NEG))
                # наступний цикл продовжує з floor
                f.append(line(x + Ton + Toff, base - floor, x + per, base - floor, color=NEG, sw=1, dash="2 3"))
            x += per
            cyc += 1
        # позначки ВКЛ/ВИКЛ на першому циклі
        x0 = ox + 6
        f.append(line(x0, top - 4, x0 + per * 0.45, top - 4, color=POS, sw=2))
        f.append(text(x0 + per * 0.22, top - 10, "ВКЛ", size=11, color=POS))
        f.append(line(x0 + per * 0.45, top - 4, x0 + per * 0.85, top - 4, color=NEG, sw=2))
        f.append(text(x0 + per * 0.65, top - 10, "ВИКЛ", size=11, color=NEG))
        if mode == 'DCM':
            f.append(text(x0 + per * 1.05, top - 10, "мертва", size=11, color="#b45309", anchor="start"))
        # підпис-висновок панелі праворуч
        return

    panel(190, "DCM: осердя порожніє щоцикл", 'DCM')
    panel(430, "CCM: лишається залишковий потік", 'CCM')

    # легенда струмів
    lx = ox + aw - 250
    f.append(line(lx, 66, lx + 26, 66, color=POS, sw=3))
    f.append(text(lx + 32, 70, "струм первинної (ВКЛ)", size=12, color=POS, anchor="start"))
    f.append(line(lx, 88, lx + 26, 88, color=NEG, sw=3))
    f.append(text(lx + 32, 92, "струм вторинної (ВИКЛ)", size=12, color=NEG, anchor="start"))

    # висновкові рамки
    b, bw, bh = textbox(ox + aw - 150, 250,
                        ["дно = 0:", "нема залишку,", "пік ВИЩИЙ"],
                        size=11, fill="#fff7ed", stroke="#b45309", color="#b45309")
    f.append(b)
    b, bw, bh = textbox(ox + aw - 150, 400,
                        ["дно ≠ 0:", "є поличка,", "пік НИЖЧИЙ"],
                        size=11, fill="#eaf7ef", stroke=FIELD, color=FIELD)
    f.append(b)

    render(os.path.join(IMG, 'windings.svg'), W, H, *f,
           title="Струм у первинній і вторинній: DCM порожнить осердя, CCM лишає поличку")


# ── Фігура 2. Одна ручка навантаження веде flyback через три режими ──────────
def fig_modes_map():
    W, H = 760, 380
    f = []
    ox, oy = 80, 300
    aw, ah = 600, 235
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(text(ox + aw - 4, oy + 26, "струм навантаження (потужність) →", size=13, anchor="end"))
    f.append(text(ox + 4, oy - ah + 2, "піковий струм осердя", size=12, anchor="start", color=MUTED))
    # дві межі
    xb1 = ox + aw * 0.30      # DCM/BCM
    xb2 = ox + aw * 0.34      # BCM/CCM (майже поруч — BCM тонка лінія)
    # зони
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdf0ee" opacity="0.55"/>'
             % (ox, oy - ah, xb1 - ox, ah))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eaf7ef" opacity="0.55"/>'
             % (xb2, oy - ah, ox + aw - xb2, ah))
    f.append(text((ox + xb1) / 2, oy - ah + 22, "DCM", size=15, bold=True, color=POS))
    f.append(text((ox + xb1) / 2, oy - ah + 40, "легке навант.", size=10, color=MUTED))
    f.append(text((xb2 + ox + aw) / 2, oy - ah + 22, "CCM", size=15, bold=True, color=FIELD))
    f.append(text((xb2 + ox + aw) / 2, oy - ah + 40, "важке навант.", size=10, color=MUTED))
    # BCM — тонка межа
    f.append(line((xb1 + xb2) / 2, oy, (xb1 + xb2) / 2, oy - ah, color="#b45309", sw=2, dash="5 4"))
    f.append(text((xb1 + xb2) / 2, oy - ah - 6, "BCM", size=12, bold=True, color="#b45309"))
    # крива пікового струму: у DCM росте як √P, у CCM майже лінійно з поличкою
    pts = []
    N = 80
    for k in range(N + 1):
        t = k / float(N)
        x = ox + t * aw
        if x < xb2:
            # DCM: пік ~ √потужності (крутіший ліворуч)
            frac = (x - ox) / (xb2 - ox)
            y = oy - (ah * 0.55) * math.sqrt(max(frac, 0))
        else:
            frac = (x - xb2) / (ox + aw - xb2)
            y = oy - (ah * 0.55) - (ah * 0.32) * frac
        pts.append((x, y))
    d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, INK))
    f.append(text(ox + aw * 0.14, oy - 40, "пік ~ √P", size=11, color=POS, anchor="middle"))
    f.append(text(ox + aw * 0.72, oy - ah + 78, "пік майже лінійний", size=11, color=FIELD, anchor="middle"))
    render(os.path.join(IMG, 'modes-map.svg'), W, H, *f,
           title="Та сама ручка навантаження веде flyback через DCM → BCM → CCM")


# ── Фігура 3. RHP-нуль: чому CCM-петля тисне газ, а машина спершу гальмує ─────
def fig_rhp():
    W, H = 780, 400
    f = []
    ox, oy = 70, 250
    aw, ah = 640, 170
    # часова вісь
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(text(ox + aw - 4, oy + 24, "час після раптового росту навантаження →", size=12, anchor="end"))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(text(ox + 6, oy - ah + 4, "вихідна напруга", size=12, anchor="start", color=MUTED))
    # рівень уставки (угорі)
    yset = oy - ah * 0.78
    f.append(line(ox, yset, ox + aw, yset, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(ox + aw - 4, yset - 6, "уставка", size=11, color=MUTED, anchor="end"))
    # момент, коли контролер підняв D
    xk = ox + aw * 0.18
    f.append(line(xk, oy, xk, oy - ah, color=FIELD, sw=1.3, dash="3 3"))
    f.append(text(xk, oy - ah - 8, "контролер підняв D", size=11, color=FIELD, anchor="middle"))
    # крива виходу: тримається уставки → провалюється ВНИЗ (RHP) → підіймається назад
    dip_amp = ah * 0.42
    pts = []
    N = 120
    ymin_dip = yset
    for k in range(N + 1):
        t = k / float(N)
        x = ox + t * aw
        if x < xk:
            y = yset
        else:
            tt = (x - xk) / (ox + aw - xk)
            # провал углиб (додатний → більший y → нижче), тоді повільне відновлення
            dip = math.sin(min(tt, 0.5) * math.pi) * dip_amp if tt < 0.5 else 0
            rec = (1 - math.exp(-(tt - 0.35) * 5)) * dip_amp if tt >= 0.35 else 0
            y = yset + dip - rec
            if y < yset: y = yset
            ymin_dip = max(ymin_dip, y)
        pts.append((x, y))
    d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, POS))
    # позначка «спершу вниз» — праворуч від западини, у вільній смузі
    xdip = ox + aw * 0.44
    f.append(text(xdip, yset + dip_amp * 0.55, "спершу ГЛИБШЕ вниз", size=12, color=POS, anchor="start"))
    f.append(text(xdip, yset + dip_amp * 0.55 + 16, "(нуль правої півплощини)", size=10, color=MUTED, anchor="start"))
    f.append(text(ox + aw * 0.82, yset + 16, "аж потім вгору", size=12, color=FIELD, anchor="middle"))
    # рамка-суть — під усім графіком, окремим рядком
    b, bw, bh = textbox(W / 2, H - 30,
                        "«додай D» на мить ЗАБИРАЄ енергію з виходу → петлю CCM тримають повільною",
                        size=12, fill="#fff7ed", stroke="#b45309", color="#b45309")
    f.append(b)
    render(os.path.join(IMG, 'rhp.svg'), W, H, *f,
           title="Нуль правої півплощини CCM: підняв шпаруватість — вихід спершу просів")


# ═══ Фігури до 🧮-вставки «Математика режимів flyback» (math-flyback-modes.md) ═══

# ── Фігура A. Енергетичний баланс DCM: чому в коефіцієнті передачі з'являється КОРІНЬ ─
def fig_energy_balance():
    W, H = 820, 430
    f = []
    # Ліворуч: трикутник струму (½LI²), праворуч: вихід (Vout²/R). Між ними — «=».
    ox, oy = 70, 300          # початок координат лівого графіка
    aw, ah = 300, 210
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.7))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.7))
    f.append(text(ox + aw - 2, oy + 22, "час", size=12, anchor="end", color=MUTED))
    f.append(text(ox - 6, oy - ah + 4, "струм первинної", size=12, anchor="start", color=MUTED))
    # трикутник наростання 0 → Iпік за D·T, тоді спад (пунктир) — DCM
    xpk = ox + aw * 0.42
    ypk = oy - ah * 0.82
    f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (ox, oy, xpk, ypk, POS))
    f.append(line(ox, ypk, xpk, ypk, color=MUTED, sw=1, dash="3 3"))
    f.append(text(ox - 6, ypk + 4, "Iпік", size=12, anchor="end", color=POS))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" opacity="0.16"/>'
             % (ox, oy, xpk, ypk, xpk, oy, POS))
    xdn = ox + aw * 0.80
    f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 4"/>'
             % (xpk, ypk, xdn, oy, NEG))
    f.append(line(xdn, oy, ox + aw, oy, color="#b45309", sw=3))
    f.append(text(ox + aw * 0.13, oy - ah * 0.30, "нахил = Vвх/Lм", size=11, color=POS, anchor="start"))
    b, bw, bh = textbox(ox + aw / 2, oy + 70,
                        ["Eвх = ½·Lм·Iпік²", "Iпік = Vвх·D/(Lм·f)"],
                        size=13, fill="#fdf0ee", stroke=POS, color=POS)
    f.append(b)
    f.append(text(ox + aw / 2, oy - ah - 14, "ВХІД: енергія ~ Iпік²  (квадрат!)",
                  size=13, bold=True, color=POS))
    f.append(text(W / 2, oy - ah * 0.35, "=", size=44, bold=True, color=INK))
    f.append(text(W / 2, oy - ah * 0.35 + 30, "за цикл", size=11, color=MUTED))
    ox2 = 470
    aw2 = 280
    f.append(arrow(ox2, oy, ox2 + aw2, oy, color=INK, sw=1.7))
    f.append(arrow(ox2, oy, ox2, oy - ah, color=INK, sw=1.7))
    f.append(text(ox2 + aw2 - 2, oy + 22, "час", size=12, anchor="end", color=MUTED))
    f.append(text(ox2 - 6, oy - ah + 4, "потужність у R", size=12, anchor="start", color=FIELD))
    ypw = oy - ah * 0.55
    f.append(line(ox2, ypw, ox2 + aw2, ypw, color=FIELD, sw=2.8))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.16"/>'
             % (ox2, ypw, aw2, oy - ypw, FIELD))
    f.append(text(ox2 - 6, ypw + 4, "Vвих²/R", size=12, anchor="end", color=FIELD))
    b, bw, bh = textbox(ox2 + aw2 / 2, oy + 70,
                        ["Eвих = (Vвих²/R)·T"],
                        size=13, fill="#eaf7ef", stroke=FIELD, color=FIELD)
    f.append(b)
    f.append(text(ox2 + aw2 / 2, oy - ah - 14, "ВИХІД: енергія ~ Vвих²",
                  size=13, bold=True, color=FIELD))
    b, bw, bh = textbox(W / 2, H - 26,
                        "½·Vвх²·D²/(Lм·f²) = Vвих²/(R·f)   →   узяли корінь   →   M = D·√( R/(2·Lм·f) )",
                        size=13, fill=FILL, stroke=INK, color=INK, bold=False)
    f.append(b)
    render(os.path.join(IMG, 'energy-balance.svg'), W, H, *f,
           title="Чому в коефіцієнті передачі DCM корінь: квадрат струму = квадрат напруги")


# ── Фігура B. Геометрія компенсації нахилом: множник збурення −Sf/Sn ──────────
def fig_slope_comp():
    W, H = 820, 440
    f = []
    ox, oy = 70, 300
    aw, ah = 680, 210
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.7))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.7))
    f.append(text(ox + aw - 2, oy + 22, "час →", size=12, anchor="end", color=MUTED))
    f.append(text(ox - 6, oy - ah + 4, "струм осердя", size=12, anchor="start", color=MUTED))
    yIp = oy - ah * 0.86
    f.append(line(ox, yIp, ox + aw, yIp, color=NEG, sw=1.6, dash="6 4"))
    f.append(text(ox + aw - 4, yIp - 6, "межа Ip (фіксована)", size=11, color=NEG, anchor="end"))
    # Явна геометрія: задаємо x-позиції прямо, y рахуємо від них. Нічого за межі.
    y0 = oy - ah * 0.28                      # номінальний рівень полички
    dpert = ah * 0.16                        # збурення Δ0 (старт ВИЩЕ норми)
    yA = y0 - dpert
    xA = ox + aw * 0.14
    w_on_nom = aw * 0.24
    w_period = aw * 0.62
    Sn = (y0 - yIp) / w_on_nom               # on-slope (px/px)
    Sf = Sn * 1.15                           # крутіший спад → наочніше перекидання (лишає місце під рамку)
    xhitN = xA + w_on_nom
    xoffN = xA + w_period
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.5" stroke-dasharray="4 4"/>'
             % (xA, y0, xhitN, yIp, xoffN, y0, MUTED))
    f.append(text(xhitN + 4, yIp + 16, "номінал", size=10, color=MUTED, anchor="start"))
    f.append(line(xA - 4, y0, xoffN + 60, y0, color=MUTED, sw=1, dash="2 3"))
    w_on_pert = (yA - yIp) / Sn
    xhitP = xA + w_on_pert
    f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (xA, yA, xhitP, yIp, POS))
    xoffP = xA + w_period
    yend = yIp + Sf * (xoffP - xhitP)
    f.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (xhitP, yIp, xoffP, yend, NEG))
    f.append(line(xA, y0, xA, yA, color=POS, sw=1.6))
    f.append(text(xA - 8, (y0 + yA) / 2 + 4, "Δ₀", size=14, color=POS, anchor="end", bold=True))
    f.append(line(xoffP, y0, xoffP, yend, color=NEG, sw=1.6))
    f.append(text(xoffP + 8, (y0 + yend) / 2 + 4, "Δ₁", size=14, color=NEG, anchor="start", bold=True))
    f.append(text(xA + w_on_pert * 0.5 - 24, (yA + yIp) / 2 - 4, "Sn", size=12, color=POS, anchor="end", bold=True))
    f.append(text(xhitP + (xoffP - xhitP) * 0.45, yIp + Sf * (xoffP - xhitP) * 0.45 - 8, "Sf", size=12, color=NEG, anchor="start", bold=True))
    b, bw, bh = textbox(ox + aw * 0.76, oy - ah * 0.72,
                        ["БЕЗ компенсації:", "Δ₁/Δ₀ = − Sf/Sn = − D/(1−D)", "|множник| > 1  при  D > 0.5"],
                        size=12, fill="#fff7ed", stroke="#b45309", color="#b45309")
    f.append(b)
    b, bw, bh = textbox(W / 2, H - 26,
                        "лік — додати штучний нахил Se:  |Δ₁/Δ₀| = |Sf−Se|/(Sn+Se) ≤ 1  ⟹  Se ≥ 0.5·Sf",
                        size=13, fill="#eaf7ef", stroke=FIELD, color=FIELD)
    f.append(b)
    render(os.path.join(IMG, 'slope-comp.svg'), W, H, *f,
           title="Геометрія субгармоніки: збурена поличка перекидається з множником −Sf/Sn")


if __name__ == '__main__':
    fig_windings()
    fig_modes_map()
    fig_rhp()
    fig_energy_balance()
    fig_slope_comp()
    print("figures written to", IMG)
