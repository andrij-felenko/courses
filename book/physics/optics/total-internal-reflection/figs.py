# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GLASS = "#eaf2fb"   # світла заливка щільнішого середовища (скло/вода)
AIR   = "#ffffff"   # рідше середовище (повітря)


def ang(a):
    return math.radians(a)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — три режими на одній межі «щільне → рідке»:
#   (a) кут < критичного: промінь заломлюється й виходить, відхиляючись від нормалі;
#   (b) кут = критичного: заломлений промінь лягає вздовж самої межі (90°);
#   (c) кут > критичного: виходу немає — світло повністю відбивається всередину.
# Показує ЧОМУ є поріг: заломлений кут «упирається» в 90°.
# ═══════════════════════════════════════════════════════════════════════════
def fig_regimes():
    W, H = 720, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Три режими на межі «щільне середовище → рідке»',
                  16, INK, 'middle', bold=True))

    n1, n2 = 1.50, 1.00            # скло → повітря
    theta_c = math.degrees(math.asin(n2 / n1))   # ≈ 41.8°

    panels = [
        (120, 28.0, 'a) кут менший за критичний', 'промінь виходить'),
        (360, theta_c, 'b) кут = критичний', 'вихід лягає на межу (90°)'),
        (600, 55.0, 'c) кут більший за критичний', 'повне відбиття всередину'),
    ]
    py = 175          # рівень межі (горизонталь)
    half = 95         # півширина панелі
    L = 78            # довжина променів

    for cx, theta_i, cap, sub in panels:
        x0, x1 = cx - half, cx + half
        # нижнє (щільне) середовище — заливка
        f.append(rect(x0, py, 2 * half, H - py - 56, fill=GLASS, stroke='none', sw=0, rx=0))
        # межа
        f.append(line(x0, py, x1, py, color=INK, sw=2))
        # нормаль (пунктир)
        f.append(line(cx, py - 70, cx, py + 78, color=MUTED, sw=1.2, dash='5,4'))

        ti = ang(theta_i)
        # падаючий промінь — знизу зліва вгору до точки падіння (у щільному середовищі)
        ix = cx - L * math.sin(ti)
        iy = py + L * math.cos(ti)
        f.append(arrow(ix, iy, cx, py, color=POS, sw=2.4))

        # відбитий промінь — завжди є; яскравий лише коли він єдиний (режим c)
        rx = cx + L * math.sin(ti)
        ry = py + L * math.cos(ti)
        refl_strong = (theta_i > theta_c + 0.01)
        f.append(arrow(cx, py, rx, ry,
                       color=(NEG if refl_strong else MUTED),
                       sw=(2.4 if refl_strong else 1.4)))

        # заломлений промінь у верхньому (рідкому) середовищі — лише якщо кут < критичного
        if theta_i < theta_c - 0.01:
            st = (n1 / n2) * math.sin(ti)
            tr = math.asin(min(1.0, st))
            tx = cx + L * math.sin(tr)
            ty = py - L * math.cos(tr)
            f.append(arrow(cx, py, tx, ty, color=FIELD, sw=2.4))
        elif abs(theta_i - theta_c) <= 0.01:
            # заломлений промінь точно вздовж межі (90° від нормалі)
            f.append(arrow(cx, py, x1 - 4, py, color=FIELD, sw=2.4))
            f.append(text(cx + 52, py - 8, '90°', 12, FIELD, 'middle', bold=True))

        # позначка кута падіння біля нормалі
        f.append(text(cx - 16, py + 30, '%.0f°' % theta_i, 12, POS, 'end'))

        # підписи середовищ (один раз достатньо, але повторюємо тихо для ясності)
        f.append(text(x0 + 4, py - 8, 'рідке  n₂', 10, MUTED, 'start'))
        f.append(text(x0 + 4, py + 18, 'щільне  n₁', 10, MUTED, 'start'))

        # підпис панелі
        f.append(text(cx, H - 34, cap, 12, INK, 'middle', bold=True))
        f.append(text(cx, H - 16, sub, 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'regimes.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — критичний кут крупно: означення sin θ_c = n₂/n₁ і чому це поріг.
# Заломлений промінь «розкривається» до 90° саме на θ_c; усе, що положе — назад.
# ═══════════════════════════════════════════════════════════════════════════
def fig_critical():
    W, H = 660, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Критичний кут: коли вихід «упирається» в 90°',
                  16, INK, 'middle', bold=True))

    cx, py = 250, 210
    f.append(rect(70, py, 360, H - py - 14, fill=GLASS, stroke='none', sw=0, rx=0))
    f.append(line(70, py, 430, py, color=INK, sw=2))
    f.append(line(cx, py - 110, cx, py + 110, color=MUTED, sw=1.2, dash='5,4'))
    f.append(text(cx + 8, py - 100, 'нормаль', 10, MUTED, 'start'))

    n1, n2 = 1.50, 1.00
    theta_c = math.degrees(math.asin(n2 / n1))
    ti = ang(theta_c)
    L = 120

    # падаючий промінь під самим критичним кутом
    ix = cx - L * math.sin(ti)
    iy = py + L * math.cos(ti)
    f.append(arrow(ix, iy, cx, py, color=POS, sw=2.6))
    f.append(text(ix - 6, iy + 4, 'падаючий', 11, POS, 'end'))

    # заломлений лягає вздовж межі (рівно 90°)
    f.append(arrow(cx, py, 418, py, color=FIELD, sw=2.6))
    f.append(text(360, py - 10, 'заломлений  90°', 11, FIELD, 'middle', bold=True))

    # дуга кута θ_c між нормаллю (вниз) і падаючим променем
    r = 40
    a0, a1 = 90 - theta_c, 90   # від падаючого до нормалі-вниз, у системі екрана
    sx = cx - r * math.sin(ti)
    sy = py + r * math.cos(ti)
    ex = cx
    ey = py + r
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.6"/>' % (sx, sy, r, r, ex, ey, INK))
    f.append(text(cx - 30, py + 64, 'θc', 14, INK, 'middle', bold=True, italic=True))

    # формула-блок праворуч
    f.append(fitbox(450, 150, 190, 86,
                    'sin θc = n₂ / n₁\nположе за θc →\nвиходу немає',
                    size=13, color=INK, fill='#f4f6f8', stroke=LINE, sw=1.5))

    # підписи середовищ
    f.append(text(80, py - 10, 'рідке  n₂  (менший)', 11, MUTED, 'start'))
    f.append(text(80, py + 22, 'щільне  n₁  (більший)', 11, MUTED, 'start'))

    f.append(text(W / 2, H - 12,
                  'Точно під θc вихід лягає вздовж межі; ще положе — заломленому променю місця немає, і світло повертається',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'critical-angle.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — де це працює: зиґзаґ у волокні (відбиття без утрат) та поворотна
# призма 45°-45°-90° (кут падіння 45° > θc скла ≈ 42°, тож світло відбивається).
# ═══════════════════════════════════════════════════════════════════════════
def fig_uses():
    W, H = 720, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Де працює: світловод і поворотна призма',
                  16, INK, 'middle', bold=True))

    # ── ліворуч: волокно ───────────────────────────────────────────────────
    fx0, fx1 = 40, 360
    cyt, cyb = 110, 190         # межі ядра
    # оболонка
    f.append(rect(fx0, 80, fx1 - fx0, 160, fill='#eef0f2', stroke=MUTED, sw=1.2, rx=8))
    # ядро (щільніше — темніша заливка)
    f.append(rect(fx0, cyt, fx1 - fx0, cyb - cyt, fill=GLASS, stroke=INK, sw=1.6, rx=0))
    f.append(text(fx0 + 6, 96, 'оболонка  n₂', 10, MUTED, 'start'))
    f.append(text((fx0 + fx1) / 2, cyb + 18, 'ядро  n₁  (вищий показник)', 10, INK, 'middle'))

    # зиґзаґ променя: кілька повних відбиттів від верхньої й нижньої межі ядра
    x = fx0 + 6
    y = cyb - 4
    up = True
    seg = 58
    pts = [(x, y)]
    while x < fx1 - 6:
        nx = min(x + seg, fx1 - 6)
        ny = cyt + 4 if up else cyb - 4
        pts.append((nx, ny))
        x, y, up = nx, ny, not up
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        f.append(line(x1, y1, x2, y2, color=POS, sw=2.4))
    # точки повного відбиття на межах ядра
    for (mx, my) in pts[1:-1]:
        f.append(circle(mx, my, 3.2, fill=NEG, stroke=NEG, sw=1))
    f.append(text((fx0 + fx1) / 2, 70, 'промінь біжить зиґзаґом, відбиваючись повністю — без утрат',
                  11, MUTED, 'middle'))

    # ── праворуч: поворотна призма 45°-45°-90° ───────────────────────────────
    # Прямий кут — унизу зліва; катети: лівий вертикальний (A-B) і нижній
    # горизонтальний (B-C). Гіпотенуза A-C (нахил +1, рівно 45°) — дзеркальна грань.
    # Світло входить ⟂ крізь лівий катет, повністю відбивається від гіпотенузи
    # й виходить ⟂ крізь нижній катет (поворот на 90°).
    ax, ay = 470, 100    # верхній лівий
    bx, by = 470, 240    # нижній лівий (прямий кут)
    cxp, cyp = 610, 240  # нижній правий
    f.append('<path d="M %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" '
             'stroke-width="1.8"/>' % (ax, ay, bx, by, cxp, cyp, GLASS, INK))
    f.append(text(bx + 70, by + 18, 'призма (скло)', 11, INK, 'middle'))

    # точка зустрічі на гіпотенузі: y = 100 + (x − 470); беремо x = 540 → y = 170
    mx, my = 540, 170
    f.append(arrow(420, my, mx, my, color=POS, sw=2.6))     # вхід → крізь лівий катет
    f.append(arrow(mx, my, mx, 300, color=NEG, sw=2.6))     # вихід ↓ крізь нижній катет
    f.append(circle(mx, my, 3.4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(414, my - 6, 'вхід', 11, POS, 'end'))
    f.append(text(mx + 8, 296, 'вихід', 11, NEG, 'start'))
    f.append(text(mx + 34, my - 6, '45° > θc', 11, INK, 'middle', bold=True))

    f.append(text(bx + 70, H - 14,
                  'кут 45° більший за θc скла (~42°) → промінь повертає на 90°',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'uses.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4 — хвильова картина: стояча хвиля у середовищі 1 та згасаюча
# хвиля у середовищі 2 з глибиною проникнення dp.
# ═══════════════════════════════════════════════════════════════════════════
def fig_evanescent():
    W, H = 680, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Хвильова структура: згасаюче поле у рідшому середовищі',
                  16, INK, 'middle', bold=True))

    py = 180    # межа z = 0
    f.append(rect(40, py, 600, H - py - 40, fill=GLASS, stroke='none', sw=0, rx=0))
    f.append(line(40, py, 640, py, color=INK, sw=2))

    # підписи середовищ
    f.append(text(50, py - 12, 'рідке середовище  n₂  (z > 0)', 11, MUTED, 'start'))
    f.append(text(50, py + 22, 'щільне середовище  n₁  (z < 0)', 11, MUTED, 'start'))

    # профілі амплітуди по z (від x = 220 до 580)
    # Згасаюча хвиля у середовищі 2 (z > 0, вгору на екрані)
    # y = py - A * exp(-z/dp)
    dp_pixels = 45
    A0 = 70
    pts_ev = []
    for z in range(0, 130, 2):
        x = 340 + z * 1.8
        y = py - A0 * math.exp(-z / dp_pixels)
        pts_ev.append((x, y))
    
    # лінія огинаючої E0 * exp(-z/dp)
    d_str = "M " + " L ".join("%.1f %.1f" % p for p in pts_ev)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_str, FIELD))

    # пунктир на рівні z = dp (де амплітуда падає в e разів)
    y_dp = py - A0 * math.exp(-1.0)
    f.append(line(340, y_dp, 340 + 130 * 1.8, y_dp, color=MUTED, sw=1.2, dash='4,3'))
    f.append(text(340 + 130 * 1.8 + 8, y_dp + 4, 'E₀ / e', 11, MUTED, 'start'))

    # стрілка глибини проникнення dp
    f.append(line(320, py, 320, py - dp_pixels, color=NEG, sw=1.8))
    f.append(text(312, py - dp_pixels / 2, 'dp', 12, NEG, 'end', bold=True, italic=True))

    # Стояча хвиля у середовищі 1 (z < 0, вниз на екрані)
    pts_st = []
    for z in range(0, 130, 2):
        x = 340 - z * 1.8
        # інтерференція падаючої й відбитої хвиль вздовж z
        y = py + A0 * math.cos(z / 12.0)
        pts_st.append((x, y))
    d_st_str = "M " + " L ".join("%.1f %.1f" % p for p in pts_st)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_st_str, POS))

    # текстові блоки з поясненнями
    f.append(text(200, py + 80, 'Інтерференційна хвиля (z < 0)\nв узлах і пучностях', 11, POS, 'middle'))
    f.append(text(480, py - 80, 'Експоненційне згасання (z > 0)\nE(z) = E₀ · e⁻ᶻ/ᵈᵖ', 11, FIELD, 'middle'))

    f.append(text(W / 2, H - 12,
                  'За межею розділу електромагнітне поле не зникає миттєво: воно проникає на глибину dp ~ λ, згасаючи експоненційно',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'evanescent-wave.svg'), W, H, *f)


fig_regimes()
fig_critical()
fig_uses()
fig_evanescent()
print('Done.')

