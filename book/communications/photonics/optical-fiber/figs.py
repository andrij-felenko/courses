# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

CORE = "#fde9c8"   # ядро (вищий показник) — тепла заливка
CLAD = "#e6eef7"   # оболонка (нижчий показник) — холодна заливка
RAY  = "#c0392b"   # промінь світла


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — хід променя у волокні: повне внутрішнє відбиття.
# Промінь, що влучив у межу ядро/оболонка положе за критичний кут, не виходить
# назовні, а повністю відбивається — і так «біжить» уздовж ядра зиґзаґом.
# ═══════════════════════════════════════════════════════════════════════════
def fig_tir():
    W, H = 700, 340
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Світло тримає повне внутрішнє відбиття', 17, INK, 'middle', bold=True))

    x0, x1 = 70, 640
    cy = 180             # вісь ядра
    core_h = 70          # півтовщина ядра
    clad_h = 38          # товщина оболонки з кожного боку

    top_core, bot_core = cy - core_h, cy + core_h
    # оболонка (зверху й знизу від ядра)
    f.append(rect(x0, top_core - clad_h, x1 - x0, clad_h, fill=CLAD, stroke=MUTED, sw=1.2, rx=0))
    f.append(rect(x0, bot_core, x1 - x0, clad_h, fill=CLAD, stroke=MUTED, sw=1.2, rx=0))
    # ядро
    f.append(rect(x0, top_core, x1 - x0, 2 * core_h, fill=CORE, stroke=LINE, sw=1.5, rx=0))

    # підписи шарів і показники
    f.append(text(x0 + 84, top_core - clad_h / 2 + 4, 'оболонка   n₂ менший', 12, MUTED, 'middle'))
    f.append(text(x0 + 84, bot_core + clad_h / 2 + 4, 'оболонка   n₂ менший', 12, MUTED, 'middle'))
    f.append(text(x0 + 60, cy + 4, 'ядро  n₁', 13, INK, 'middle', bold=True))

    # зиґзаґ-промінь усередині ядра: відбивається від верхньої та нижньої межі
    pad = 22
    ys = [bot_core - 12, top_core + 12]   # точки дотику чергуються низ/верх
    pts = [(x0 + 6, cy + 8)]
    nseg = 5
    span = (x1 - 16 - (x0 + 6))
    for i in range(nseg + 1):
        bx = x0 + 6 + span * i / nseg
        by = ys[i % 2]
        pts.append((bx, by))
    # малюємо сегменти
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        f.append(line(ax, ay, bx, by, color=RAY, sw=2.4))
    # наконечник на виході
    lastx, lasty = pts[-1]
    f.append(arrow(lastx - 0.1, lasty - 0.1, lastx + 0.1, lasty + 0.1, color=RAY, sw=2.4))
    # точки відбиття + позначка кута на першому відбитті
    bx, by = pts[2]
    f.append(circle(bx, by, 3.5, fill=RAY, stroke=RAY, sw=1))
    f.append(line(x0, by, x1, by, color=MUTED, sw=0.8, dash='4,4'))
    f.append(text(bx + 4, by - 10, 'кут падіння > критичного → відбивається весь', 11, RAY, 'start'))

    # підпис «вхід» біля початку променя
    f.append(text(x0 - 2, cy + 30, 'вхід світла', 11, MUTED, 'middle'))
    f.append(text(W / 2, H - 18,
                  'Промінь, положе за критичний кут, відбивається 100% і «біжить» уздовж ядра',
                  12, MUTED, 'middle'))

    render(os.path.join(IMG, 'tir.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — одномодове проти багатомодового: чому товсте ядро «розмазує» імпульс.
# У товстому ядрі промені йдуть різними шляхами (модами) різної довжини → той
# самий імпульс приходить розтягнутим (модова дисперсія). Тонке ядро лишає один
# шлях → імпульс лишається гострим.
# ═══════════════════════════════════════════════════════════════════════════
def fig_modes():
    W, H = 700, 380
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Товсте ядро розмазує імпульс, тонке — ні', 17, INK, 'middle', bold=True))

    x0, x1 = 150, 560

    def fiber(cy, core_h, label):
        clad = 16
        f.append(rect(x0, cy - core_h - clad, x1 - x0, clad, fill=CLAD, stroke=MUTED, sw=1.0, rx=0))
        f.append(rect(x0, cy + core_h, x1 - x0, clad, fill=CLAD, stroke=MUTED, sw=1.0, rx=0))
        f.append(rect(x0, cy - core_h, x1 - x0, 2 * core_h, fill=CORE, stroke=LINE, sw=1.3, rx=0))
        f.append(text(x0 - 14, cy + 4, label, 12, INK, 'end'))

    # — багатомодове (товсте ядро): три промені різних шляхів —
    cy1, ch1 = 130, 42
    fiber(cy1, ch1, 'багатомодове\n(товсте ядро)')
    # прямий промінь (найкоротший шлях)
    f.append(line(x0, cy1, x1, cy1, color="#e67e22", sw=2.0))
    # два зиґзаґ-промені різної крутості (довші шляхи)
    for amp, col, segs in [(ch1 - 8, RAY, 4), (ch1 - 8, "#8e44ad", 6)]:
        ys = [cy1 + amp, cy1 - amp]
        pts = [(x0, cy1)]
        span = x1 - x0
        for i in range(segs + 1):
            pts.append((x0 + span * i / segs, ys[i % 2]))
        for i in range(len(pts) - 1):
            ax, ay = pts[i]; bx, by = pts[i + 1]
            f.append(line(ax, ay, bx, by, color=col, sw=1.8))
    # вхідний імпульс (гострий) і вихідний (розмазаний)
    f.append(_pulse(x0 - 70, cy1, 10, sharp=True))
    f.append(text(x0 - 70, cy1 - 30, 'вхід', 11, MUTED, 'middle'))
    f.append(_pulse(x1 + 70, cy1, 36, sharp=False))
    f.append(text(x1 + 70, cy1 - 30, 'вихід', 11, MUTED, 'middle'))
    f.append(text(x1 + 70, cy1 + 36, 'розтягнутий', 10, RAY, 'middle'))

    # — одномодове (тонке ядро): один шлях —
    cy2, ch2 = 280, 10
    fiber(cy2, ch2, 'одномодове\n(тонке ядро)')
    f.append(line(x0, cy2, x1, cy2, color=RAY, sw=2.2))
    f.append(_pulse(x0 - 70, cy2, 10, sharp=True))
    f.append(text(x0 - 70, cy2 - 26, 'вхід', 11, MUTED, 'middle'))
    f.append(_pulse(x1 + 70, cy2, 12, sharp=True))
    f.append(text(x1 + 70, cy2 - 26, 'вихід', 11, MUTED, 'middle'))
    f.append(text(x1 + 70, cy2 + 30, 'гострий', 10, FIELD, 'middle'))

    f.append(text(W / 2, H - 16,
                  'Різні моди йдуть шляхами різної довжини → приходять урізнобій; одна мода такого не має',
                  11, MUTED, 'middle'))

    render(os.path.join(IMG, 'modes.svg'), W, H, *f)


def _pulse(cx, cy, width, sharp=True):
    """Маленький стовпчик-«імпульс»: гострий (вузький, високий) або розмазаний (широкий, низький)."""
    h = 34 if sharp else 18
    col = FIELD if sharp else RAY
    w = max(6, width)
    return rect(cx - w / 2, cy - h / 2, w, h, fill=('#eafaf0' if sharp else '#fbeaea'),
                stroke=col, sw=1.6, rx=3)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — загасання від довжини хвилі: «вікна» прозорості.
# Скло прозоріше не для видимого світла, а для ближнього інфрачервоного; є кілька
# провалів загасання («вікон»), і саме на них працює зв'язок. Пік ~1383 нм — вода.
# ═══════════════════════════════════════════════════════════════════════════
def fig_windows():
    W, H = 700, 360
    f = []
    f.append(rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0))
    f.append(text(W / 2, 28, 'Скло найпрозоріше в інфрачервоному — там і працює звʼязок',
                  16, INK, 'middle', bold=True))

    # осі
    ox0, ox1 = 90, 650
    oy0, oy1 = 70, 270
    f.append(arrow(ox0, oy1, ox1 + 10, oy1, color=INK, sw=1.5))   # X: довжина хвилі
    f.append(arrow(ox0, oy1, ox0, oy0 - 8, color=INK, sw=1.5))    # Y: загасання
    f.append(text(ox1 + 12, oy1 + 16, 'λ, нм', 12, INK, 'start', italic=True))
    f.append(text(ox0 - 60, oy0 + 2, 'загасання', 12, INK, 'start'))
    f.append(text(ox0 - 60, oy0 + 18, 'дБ/км', 12, MUTED, 'start'))

    # шкала X: 800..1700 нм
    lam0, lam1 = 800.0, 1700.0
    def px(lam): return ox0 + (lam - lam0) / (lam1 - lam0) * (ox1 - ox0)
    for lam in [850, 1310, 1550]:
        x = px(lam)
        f.append(line(x, oy1, x, oy1 + 6, color=INK, sw=1.2))
        f.append(text(x, oy1 + 20, str(lam), 11, INK, 'middle'))

    # крива загасання (ілюстративна форма): спад у бік ІЧ, пік води ~1383, ріст за 1600
    def atten(lam):
        # дБ/км, схематично
        base = 0.2 + 6.0 * ((1000.0 / lam) ** 3.2)      # релеївське розсіяння росте на коротких λ
        water = 1.6 * math.exp(-((lam - 1383.0) / 26.0) ** 2)  # піки OH
        ir = 0.15 * math.exp((lam - 1500.0) / 90.0)     # ІЧ-поглинання росте на довгих λ
        return base + water + ir
    amax = 4.5
    def py(a): return oy1 - min(a, amax) / amax * (oy1 - oy0)

    pts = []
    lam = lam0
    while lam <= lam1 + 0.1:
        pts.append((px(lam), py(atten(lam))))
        lam += 8
    path = 'M %.1f %.1f ' % pts[0] + ' '.join('L %.1f %.1f' % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, RAY))

    # позначити «вікна» — провали, на яких працює зв'язок
    for lam, name in [(850, '1-ше вікно'), (1310, '2-ге  (нуль дисперсії)'), (1550, '3-тє  (мінімум втрат)')]:
        x = px(lam); y = py(atten(lam))
        f.append(circle(x, y, 4, fill=FIELD, stroke=FIELD, sw=1))
        f.append(line(x, y, x, oy0 + 6, color=FIELD, sw=0.8, dash='3,3'))
        f.append(text(x, oy0 - 2 if lam != 1310 else oy0 + 2, name, 10, FIELD, 'middle'))
    # пік води
    xw = px(1383); yw = py(atten(1383))
    f.append(circle(xw, yw, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(xw + 6, yw - 4, 'пік води (OH)', 10, NEG, 'start'))

    # видиме світло — окремою рискою зліва (контекст: воно НЕ найпрозоріше)
    f.append(fitbox(ox0 - 6, oy1 + 36, ox1 - ox0 + 16, 44,
                    'Видиме світло (≈400–700 нм) скло пропускає гірше за ближнє ІЧ — тому далекий\n'
                    'звʼязок працює саме на 1310 та 1550 нм, у «вікнах» найменшого загасання.',
                    size=11, color=INK, fill='#f4f6f8', stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, 'windows.svg'), W, H, *f)


fig_tir()
fig_modes()
fig_windows()
print('Done.')
