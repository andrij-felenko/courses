# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

AIRC = "#eaf2fb"   # заливка «стовпа повітря» / потоку
BLADE = "#dfe6ee"  # заливка перерізу лопаті


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 1 — гвинт як шуруп: за один оберт лопать проходить крок P уздовж осі.
# Геометричний крок (скільки мала б пройти) проти дійсного просування; різниця
# посередині — ковзання (slip). Показує ЧОМУ «крок» вимірюють у міліметрах.
# ═══════════════════════════════════════════════════════════════════════════
def fig_pitch():
    W, H = 720, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Крок гвинта: за один оберт — просування вздовж осі',
                  16, INK, 'middle', bold=True))

    # вісь обертання — горизонтальна стрілка вперед
    ax_y = 175
    x0 = 90
    f.append(line(x0, ax_y, W - 40, ax_y, color=MUTED, sw=1.4, dash='4,4'))
    f.append(text(W - 44, ax_y - 10, 'вісь, напрям польоту →', 11, MUTED, 'end'))

    # гелікоїд: точка на радіусі r обертається й одночасно повзе вперед.
    # Малюємо як синусоїду по y (обертання) з лінійним зсувом по x (просування).
    r_px = 62                 # видимий радіус кола обертання
    turns = 1.0               # рівно один оберт → крок
    P_px = 300                # геометричний крок у пікселях (скільки мало б пройти)
    n = 120
    pts_geom = []
    for i in range(n + 1):
        t = i / n * turns
        x = x0 + t * P_px
        y = ax_y - r_px * math.cos(2 * math.pi * t)
        pts_geom.append((x, y))
    d = 'M ' + ' L '.join('%.1f %.1f' % (px, py) for px, py in pts_geom)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, POS))
    # позначки початку й кінця витка
    f.append(circle(pts_geom[0][0], pts_geom[0][1], 4, fill=POS, stroke=POS, sw=1))
    f.append(circle(pts_geom[-1][0], pts_geom[-1][1], 4, fill=POS, stroke=POS, sw=1))
    f.append(text(x0 - 6, pts_geom[0][1] - 6, 'лопать', 11, POS, 'end'))

    # межі одного витка — вертикальні мітки
    xg0 = x0
    xg1 = x0 + P_px
    for xg in (xg0, xg1):
        f.append(line(xg, ax_y - r_px - 14, xg, ax_y + r_px + 14, color=INK, sw=1))
    # розмір геометричного кроку
    f.append(line(xg0, ax_y + r_px + 30, xg1, ax_y + r_px + 30, color=INK, sw=1.4))
    f.append(text((xg0 + xg1) / 2, ax_y + r_px + 24,
                  'геометричний крок P (за 1 оберт)', 12, INK, 'middle', bold=True))

    # дійсне просування — коротше на ковзання
    xe1 = x0 + P_px * 0.78
    f.append(line(xg0, ax_y - r_px - 30, xe1, ax_y - r_px - 30, color=FIELD, sw=2.4))
    f.append(text((xg0 + xe1) / 2, ax_y - r_px - 36,
                  'дійсне просування (ефективний крок)', 11, FIELD, 'middle', bold=True))
    # ковзання — залишок
    f.append(line(xe1, ax_y - r_px - 30, xg1, ax_y - r_px - 30, color=POS, sw=2.4, dash='3,3'))
    f.append(text((xe1 + xg1) / 2, ax_y - r_px - 36, 'ковзання', 10, POS, 'middle', bold=True))

    render(os.path.join(IMG, 'pitch.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 2 — ЧОМУ лопать скручена: біля вала колова швидкість мала, на кінці —
# велика, а швидкість польоту та сама. Трикутник швидкостей у трьох перерізах;
# кут набігання потоку падає від комля до кінця → лопать треба скрутити так,
# щоб місцевий кут атаки лишався добрим. Показує причину «twist».
# ═══════════════════════════════════════════════════════════════════════════
def fig_twist():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Чому лопать скручена: трикутник швидкостей уздовж радіуса',
                  16, INK, 'middle', bold=True))

    V0 = 46          # швидкість польоту (однакова для всіх перерізів) — пікселі
    stations = [
        (150, 0.35, 'комель  (r малий)'),
        (370, 0.70, 'середина'),
        (590, 1.00, 'кінець  (r великий)'),
    ]
    base_y = 250
    for cx, frac, cap in stations:
        Ur = 120 * frac        # колова швидкість ωr — росте з радіусом
        # горизонталь — колова швидкість ωr (напрям обертання, вбік)
        f.append(arrow(cx, base_y, cx + Ur, base_y, color=NEG, sw=2.4))
        f.append(text(cx + Ur / 2, base_y + 18, 'ωr', 12, NEG, 'middle', bold=True))
        # вертикаль — швидкість польоту V0 (уперед, угору на схемі): однакова всюди
        f.append(arrow(cx, base_y, cx, base_y - V0, color=POS, sw=2.4))
        f.append(text(cx - 12, base_y - V0 / 2, 'V₀', 12, POS, 'end', bold=True))
        # результівний набігний потік — гіпотенуза
        f.append(arrow(cx, base_y, cx + Ur, base_y - V0, color=FIELD, sw=2.6))
        # кут потоку φ від площини обертання
        phi = math.degrees(math.atan2(V0, Ur))
        f.append(text(cx + Ur + 6, base_y - V0 - 4, 'φ=%.0f°' % phi, 11, FIELD, 'start', bold=True))
        f.append(text(cx + Ur * 0.5, base_y - V0 * 0.5 - 8, 'потік', 10, FIELD, 'middle'))
        # підпис перерізу
        f.append(text(cx + Ur / 2, H - 46, cap, 12, INK, 'middle', bold=True))

    f.append(text(W / 2, H - 20,
                  'колова швидкість ωr росте від комля до кінця, а V₀ та сама → кут φ падає; '
                  'щоб кут атаки лишався добрим, лопать скручують сильніше біля вала',
                  11, MUTED, 'middle'))
    render(os.path.join(IMG, 'twist.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 3 — два погляди на той самий гвинт:
#   ліворуч — диск, що жбурляє стовп повітря назад (теорія імпульсу): тяга = темп
#             зміни імпульсу повітря;
#   праворуч — переріз лопаті як маленьке крило: набігний потік дає піднімальну
#             силу L і опір D; проєкція вперед — тяга, проєкція вбік — момент.
# ═══════════════════════════════════════════════════════════════════════════
def fig_two_views():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Два погляди на той самий гвинт', 16, INK, 'middle', bold=True))

    # ── ЛІВОРУЧ: диск жбурляє повітря ──────────────────────────────────────
    dxc, dyc = 175, 195
    # стовп повітря, що звужується назад (контракція струменя)
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" '
             'stroke-width="1.2"/>' % (dxc, dyc - 70, dxc, dyc + 70,
                                       dxc + 150, dyc + 48, dxc + 150, dyc - 48,
                                       AIRC, MUTED))
    # сам диск (гвинт з ребра)
    f.append(line(dxc, dyc - 72, dxc, dyc + 72, color=INK, sw=5))
    f.append(text(dxc, dyc - 84, 'диск (гвинт)', 12, INK, 'middle', bold=True))
    # повітря входить повільно, виходить швидко
    f.append(arrow(dxc - 92, dyc - 40, dxc - 30, dyc - 40, color=NEG, sw=2))
    f.append(arrow(dxc - 92, dyc + 40, dxc - 30, dyc + 40, color=NEG, sw=2))
    f.append(text(dxc - 100, dyc - 54, 'повітря входить (повільно)', 10, NEG, 'start'))
    for oy in (-30, 0, 30):
        f.append(arrow(dxc + 60, dyc + oy, dxc + 150, dyc + oy, color=POS, sw=2.6))
    f.append(text(dxc + 105, dyc + 62, 'жбурнуте назад (швидко)', 10, POS, 'middle'))
    # реакція — тяга вперед
    f.append(arrow(dxc, dyc, dxc - 70, dyc, color=FIELD, sw=3))
    f.append(text(dxc - 40, dyc - 8, 'тяга', 12, FIELD, 'middle', bold=True))
    f.append(text(dxc + 20, H - 46, 'теорія імпульсу', 13, INK, 'middle', bold=True))
    f.append(text(dxc + 20, H - 28, 'тяга = темп зміни імпульсу повітря', 10, MUTED, 'middle'))

    # ── ПРАВОРУЧ: переріз лопаті — маленьке крило ───────────────────────────
    bx, by = 520, 190
    # хорда перерізу під кутом (профіль крила спрощено — нахилений овал)
    chord = 120
    ang = math.radians(22)     # кут установки перерізу
    hx = chord / 2 * math.cos(ang)
    hy = chord / 2 * math.sin(ang)
    # профіль як тонкий нахилений «човник»
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f Z" '
             'fill="%s" stroke="%s" stroke-width="1.6"/>' % (
                 bx - hx, by + hy,
                 bx, by - 20, bx + hx, by - hy,
                 bx, by + 8, bx - hx, by + hy,
                 BLADE, INK))
    f.append(text(bx + hx + 6, by - hy, 'переріз лопаті', 11, INK, 'start'))
    # набігний потік — знизу-ззаду
    wx, wy = bx - 96, by + 60
    f.append(arrow(wx, wy, bx - hx * 0.2, by + hy * 0.2, color=MUTED, sw=2))
    f.append(text(wx - 4, wy + 12, 'набігний потік', 10, MUTED, 'start'))
    # піднімальна сила L — перпендикулярно потоку (вгору-вперед)
    f.append(arrow(bx, by, bx - 6, by - 78, color=FIELD, sw=2.6))
    f.append(text(bx - 8, by - 86, 'L', 13, FIELD, 'end', bold=True))
    # опір D — уздовж потоку
    f.append(arrow(bx, by, bx + 40, by + 48, color=POS, sw=2.2))
    f.append(text(bx + 46, by + 52, 'D', 12, POS, 'start', bold=True))
    # розклад: тяга вперед (уліво) і сила на момент (вбік/угору схеми)
    f.append(line(bx - 150, by, bx + 60, by, color=MUTED, sw=1, dash='4,4'))
    f.append(arrow(bx, by + 96, bx - 70, by + 96, color=NEG, sw=2.4))
    f.append(text(bx - 74, by + 92, 'тяга (проєкція вперед)', 10, NEG, 'end'))
    f.append(text(bx + 20, H - 46, 'теорія елемента лопаті', 13, INK, 'middle', bold=True))
    f.append(text(bx + 20, H - 28, 'кожен переріз — маленьке крило', 10, MUTED, 'middle'))

    render(os.path.join(IMG, 'two-views.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 4 (для вставки math-blade-element) — трикутник швидкостей перерізу
# з ІНДУКОВАНИМИ швидкостями. Осьова V₀(1+a) і колова ωr(1−a′) складають
# результівну W під кутом φ; хорда під кутом установки β; кут атаки α = β − φ.
# L перпендикулярна W, D уздовж W; їхні проєкції на вісь і на площину дають
# dT і dQ. Це серце BEMT — де зшиваються дві теорії.
# ═══════════════════════════════════════════════════════════════════════════
def fig_bemt_triangle():
    W, H = 720, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Трикутник швидкостей перерізу з індукованими поправками',
                  16, INK, 'middle', bold=True))

    # Площина обертання — горизонталь; вісь гвинта — вертикаль (угору = вперед).
    ox, oy = 210, 300           # вершина трикутника швидкостей (носок хорди)
    Ux = 300                    # колова складова ωr(1−a′) — управо вздовж площини
    Vy = 165                    # осьова складова V₀(1+a) — угору вздовж осі

    # осі-орієнтири
    f.append(line(ox - 30, oy, ox + Ux + 40, oy, color=MUTED, sw=1, dash='5,4'))
    f.append(text(ox + Ux + 44, oy + 4, 'площина обертання', 11, MUTED, 'start'))
    f.append(line(ox, oy + 30, ox, oy - Vy - 40, color=MUTED, sw=1, dash='5,4'))
    f.append(text(ox + 4, oy - Vy - 44, 'вісь (уперед)', 11, MUTED, 'start'))

    # колова складова (управо) — ωr, зменшена на (1−a')
    f.append(arrow(ox, oy, ox + Ux, oy, color=NEG, sw=2.6))
    f.append(text(ox + Ux / 2, oy + 20, 'ωr(1 − a′)', 13, NEG, 'middle', bold=True))
    # осьова складова (угору) — V₀, збільшена на (1+a)
    f.append(arrow(ox, oy, ox, oy - Vy, color=POS, sw=2.6))
    f.append(text(ox - 10, oy - Vy / 2, 'V₀(1 + a)', 13, POS, 'end', bold=True))
    # результівний потік W — гіпотенуза (з початку в кут)
    f.append(arrow(ox, oy, ox + Ux, oy - Vy, color=FIELD, sw=2.8))
    f.append(text(ox + Ux + 6, oy - Vy - 6, 'W', 14, FIELD, 'start', bold=True))
    f.append(text(ox + Ux * 0.55, oy - Vy * 0.55 - 8, 'набігний потік', 10, FIELD, 'middle'))

    # кут φ між W і площиною обертання
    phi = math.degrees(math.atan2(Vy, Ux))
    f.append(text(ox + Ux * 0.42, oy - 12, 'φ', 13, FIELD, 'middle', bold=True))

    # ── хорда перерізу під кутом установки β (β > φ, різниця = кут атаки α) ──
    beta = math.radians(phi + 9)     # кут установки трохи більший за φ
    cl = 150
    cx2 = ox + cl * math.cos(beta)
    cy2 = oy - cl * math.sin(beta)
    f.append(line(ox, oy, cx2, cy2, color=INK, sw=4))
    f.append(text(cx2 + 6, cy2 - 4, 'хорда (кут β)', 11, INK, 'start', bold=True))
    # дуга кута атаки α між хордою і W — підпис (у клині біля вершини)
    f.append(text(ox + 92, oy - 96, 'α = β − φ', 12, INK, 'start', bold=True))

    # ── сили в точці ~2/3 хорди: L ⟂ W, D ∥ W ──
    px, py = ox + cl * 0.62 * math.cos(beta), oy - cl * 0.62 * math.sin(beta)
    # напрям W (одиничний), напрям L = поворот W на +90° (проти год.)
    wxn, wyn = math.cos(math.radians(phi)), -math.sin(math.radians(phi))
    Llen, Dlen = 92, 40
    # L перпендикуляр до W (поворот (wx,wy)→(wy,−wx) в екранних координатах — «уперед-угору»)
    lxn, lyn = wyn, -wxn
    f.append(arrow(px, py, px + Llen * lxn, py + Llen * lyn, color=FIELD, sw=2.6))
    f.append(text(px + Llen * lxn - 6, py + Llen * lyn - 6, 'L', 13, FIELD, 'end', bold=True))
    # D уздовж W (назад по потоку, тобто у напрям −W від носка): малюємо вперед по W
    f.append(arrow(px, py, px + Dlen * wxn, py + Dlen * wyn, color=POS, sw=2.4))
    f.append(text(px + Dlen * wxn + 6, py + Dlen * wyn + 4, 'D', 12, POS, 'start', bold=True))

    # підпис-висновок
    f.append(mtext(W / 2, H - 40,
                   ['осьова проєкція (L cos φ − D sin φ) → тяга dT;',
                    'колова проєкція (L sin φ + D cos φ)·r → момент dQ'],
                   11, MUTED, 'middle'))
    render(os.path.join(IMG, 'bemt-triangle.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 5 (для вставки) — кільцевий струмок (annulus) радіуса r, товщини dr:
# саме на ньому зшиваються дві теорії. Ліворуч — кільце на диску; праворуч —
# баланс: імпульс каже, скільки повітря протягнуто (a, a'), елемент лопаті —
# яку силу дають лопаті в цьому кільці. Рівність двох виразів = замикання.
# ═══════════════════════════════════════════════════════════════════════════
def fig_annulus():
    W, H = 720, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Кільцевий струмок: де зшиваються дві теорії',
                  16, INK, 'middle', bold=True))

    # ── ЛІВОРУЧ: диск гвинта з виділеним кільцем радіуса r, товщини dr ──
    cx, cy, R = 175, 185, 105
    f.append(circle(cx, cy, R, fill=BG, stroke=INK, sw=1.6))
    f.append(circle(cx, cy, 10, fill=INK, stroke=INK, sw=1))     # маточина
    # виділене кільце
    r_in, r_out = 66, 80
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 1 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="%.1f"/>' % (cx + r_in, cy, r_in, r_in,
                                                    cx + r_in - 0.01, cy, FIELD, 2))
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 1 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="%.1f"/>' % (cx + r_out, cy, r_out, r_out,
                                                    cx + r_out - 0.01, cy, FIELD, 2))
    # заливка кільця сектором для наочності
    f.append('<path d="M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f Z" '
             'fill="%s" stroke="none" opacity="0.5"/>' % (
                 cx + r_in * math.cos(math.radians(-35)), cy + r_in * math.sin(math.radians(-35)),
                 cx + r_out * math.cos(math.radians(-35)), cy + r_out * math.sin(math.radians(-35)),
                 r_out, r_out,
                 cx + r_out * math.cos(math.radians(35)), cy + r_out * math.sin(math.radians(35)),
                 "#d8efe0"))
    # радіус r і товщина dr
    f.append(arrow(cx, cy, cx + r_out * math.cos(math.radians(-8)),
                   cy + r_out * math.sin(math.radians(-8)), color=INK, sw=1.6))
    f.append(text(cx + 40, cy - 8, 'r', 13, INK, 'middle', bold=True))
    f.append(text(cx + r_out + 6, cy + 30, 'dr', 12, FIELD, 'start', bold=True))
    f.append(text(cx, cy + R + 24, 'диск гвинта, кільце (r, dr)', 12, INK, 'middle', bold=True))

    # ── ПРАВОРУЧ: два вирази однієї сили на кільці, між ними знак рівності ──
    bx = 400
    top, w_box, h_box = 70, 300, 78
    b1 = fitbox(bx, top, w_box, h_box,
                'ІМПУЛЬС\nскільки повітря протягнуто крізь кільце\n→ дає a, a′ через dT, dQ',
                12, fill="#eaf0fd", stroke=NEG, bold=False)
    f.append(b1)
    f.append(text(bx + w_box / 2, top + h_box + 26, '=', 26, INK, 'middle', bold=True))
    b2 = fitbox(bx, top + h_box + 40, w_box, h_box,
                'ЕЛЕМЕНТ ЛОПАТІ\nяку силу дають лопаті в цьому кільці\n→ через L, D, кути φ, β',
                12, fill="#eafaf0", stroke=FIELD, bold=False)
    f.append(b2)
    f.append(mtext(bx + w_box / 2, top + 2 * h_box + 96,
                   ['прирівняли обидва вирази на КОЖНОМУ кільці',
                    '→ рівняння на a, a′ (розв’язуємо ітерацією)'],
                   11, MUTED, 'middle'))
    render(os.path.join(IMG, 'annulus.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура (для вставки hist-propeller) — дві теоретичні лінії півстоліття течуть
# паралельно й зустрічаються лише на братах Райт. Ліворуч — теорія імпульсу
# (Ренкін → Ґрінгілл → Р.Е. Фруд): диск, що жбурляє воду; знає СКІЛЬКИ маси, але
# мовчить про форму лопаті. Праворуч — теорія елемента лопаті (В. Фруд →
# Джевецький): лопать як набір крил; знає силу КОЖНОЇ смужки, але не знає
# швидкості набігання. Обидві безсилі поодинці → зшиваються в розрахунку 1903.
# ═══════════════════════════════════════════════════════════════════════════
def fig_history_lines():
    W, H = 720, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Дві теорії гвинта сходяться на братах Райт',
                  16, INK, 'middle', bold=True))

    bw, bh = 250, 40          # розмір іменних рамок
    lx = 30                   # ліва колонка (імпульс)
    rx = W - 30 - bw          # права колонка (елемент лопаті)
    ys = [58, 118, 178]       # три рівні для трьох імен у кожній лінії

    # заголовки колонок
    f.append(fitbox(lx, ys[0] - 34, bw, 26, 'ТЕОРІЯ ІМПУЛЬСУ  (диск)',
                    13, fill="#eaf0fd", stroke=NEG, bold=True))
    f.append(fitbox(rx, ys[0] - 34, bw, 26, 'ЕЛЕМЕНТ ЛОПАТІ  (крила)',
                    13, fill="#eafaf0", stroke=FIELD, bold=True))

    left = [
        'Ренкін, 1865 — заклав ідею',
        'Ґрінгілл, 1888 — математика',
        'Р.Е. Фруд, 1889 — довів до пуття',
    ]
    right = [
        'В. Фруд, 1878 — кинув думку',
        'Джевецький, 1880–90-ті —',
        'зробив робочою (метод 1892)',
    ]
    # ліва лінія імпульсу
    for i, y in enumerate(ys):
        f.append(fitbox(lx, y, bw, bh, left[i], 12, fill="#f6f9ff", stroke=NEG))
        if i:
            f.append(line(lx + bw / 2, ys[i - 1] + bh, lx + bw / 2, y, color=NEG, sw=1.6))
    # права лінія елемента лопаті (два останні рядки — одна рамка на дві висоти)
    f.append(fitbox(rx, ys[0], bw, bh, right[0], 12, fill="#f4fbf6", stroke=FIELD))
    f.append(line(rx + bw / 2, ys[0] + bh, rx + bw / 2, ys[1], color=FIELD, sw=1.6))
    f.append(fitbox(rx, ys[1], bw, bh + 60, right[1] + '\n' + right[2],
                    12, fill="#f4fbf6", stroke=FIELD))

    # коротка суть під кожною колонкою — чого їй бракує
    f.append(fitbox(lx, ys[2] + 62, bw, 46,
                    'знає, СКІЛЬКИ маси відкинути,\nале мовчить про форму лопаті',
                    11, fill=BG, stroke=MUTED))
    f.append(fitbox(rx, ys[2] + 62, bw, 46,
                    'знає силу КОЖНОЇ смужки,\nале не знає швидкості набігання',
                    11, fill=BG, stroke=MUTED))

    # обидві стрілки сходяться донизу до спільної рамки Райтів
    conv_y = 340
    wx, wby, wbh = W / 2 - 150, conv_y, 56
    f.append(line(lx + bw / 2, ys[2] + 108, lx + bw / 2, conv_y - 22, color=NEG, sw=1.6))
    f.append(arrow(lx + bw / 2, conv_y - 22, wx + 60, conv_y, color=NEG, sw=2.2))
    f.append(line(rx + bw / 2, ys[2] + 108, rx + bw / 2, conv_y - 22, color=FIELD, sw=1.6))
    f.append(arrow(rx + bw / 2, conv_y - 22, wx + 300 - 60, conv_y, color=FIELD, sw=2.2))

    f.append(fitbox(wx, wby, 300, wbh,
                    'БРАТИ РАЙТ, 1903\nзшили обидві теорії в один розрахунок',
                    13, fill="#fff6ea", stroke=POS, bold=True))
    # підсумковий рядок унизу
    f.append(mtext(W / 2, conv_y + wbh + 34,
                   ['півстоліття лінії текли поруч і не зливалися;',
                    'їх поєднав розрахунок повітряного гвинта — ККД ≈ 66–70 %'],
                   11, MUTED, 'middle'))
    render(os.path.join(IMG, 'history-lines.svg'), W, H, *f)


fig_pitch()
fig_twist()
fig_two_views()
fig_bemt_triangle()
fig_annulus()
fig_history_lines()
print('Done.')
