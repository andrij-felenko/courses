# -*- coding: utf-8 -*-
"""Фігури до теми «Slew rate виходу: швидкість і шум».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Що таке slew rate на ніжці: dV/dt = нахил фронту, В/нс ─────────────────
# Ідея: показати ДВІ вихідні напруги на спільних осях — пологий і крутий фронт,
# і що slew rate — це просто НАХИЛ ΔV/Δt. Джерело нахилу — сила драйвера (Rout),
# що заряджає ємність лінії C. Той самий розмах, різний час → різний нахил.
def fig_slew_on_pin():
    W, H = 760, 400
    f = []
    f.append(text(W / 2, 28, "Slew rate — це нахил фронту на ніжці: скільки вольтів за наносекунду", size=15, bold=True))

    ox, oy = 96, 300
    ax_w, ax_h = 520, 220
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # вісь часу
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # вісь напруги
    f.append(text(ox + ax_w, oy + 22, "час t, нс", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ax_h + 6, "V", size=12, color=MUTED, anchor="end"))

    def yv(frac):
        return oy - ax_h * 0.9 * frac
    Vdd_y = yv(1.0)
    f.append(line(ox, Vdd_y, ox + ax_w, Vdd_y, color=POS, sw=1, dash="5,4"))
    f.append(text(ox + ax_w + 3, Vdd_y + 4, "VDD", size=11, color=POS, anchor="start", bold=True))
    f.append(line(ox, oy, ox + ax_w, oy, color=MUTED, sw=1))
    f.append(text(ox - 8, oy + 4, "0", size=10, color=MUTED, anchor="end"))

    # крутий фронт (сильний драйвер): від 0 до VDD за короткий час
    x0 = ox + ax_w * 0.10
    x_fast = ox + ax_w * 0.28
    f.append(line(ox, oy, x0, oy, color=POS, sw=3))
    f.append(line(x0, oy, x_fast, Vdd_y, color=POS, sw=3))
    f.append(line(x_fast, Vdd_y, ox + ax_w, Vdd_y, color=POS, sw=3))
    f.append(text((x0 + x_fast) / 2 + 66, yv(0.5) - 6, "крутий: сильний драйвер", size=11, color=POS, bold=True, anchor="start"))

    # пологий фронт (слабкий драйвер / більша C): той самий розмах, довший час
    x_slow = ox + ax_w * 0.72
    f.append(line(x0, oy, x_slow, Vdd_y, color=NEG, sw=3))
    f.append(text((x0 + x_slow) / 2, yv(0.5) + 26, "пологий: слабкий драйвер / більша C", size=11, color=NEG, bold=True))

    # позначка нахилу ΔV/Δt для пологого
    f.append(line(x0, oy + 16, x_slow, oy + 16, color=NEG, sw=1.4))
    f.append(line(x0, oy + 12, x0, oy + 20, color=NEG, sw=1.4))
    f.append(line(x_slow, oy + 12, x_slow, oy + 20, color=NEG, sw=1.4))
    f.append(text((x0 + x_slow) / 2, oy + 34, "Δt", size=10, color=NEG))
    f.append(line(ox - 30, oy, ox - 30, Vdd_y, color=MUTED, sw=1.2))
    f.append(text(ox - 36, yv(0.5) + 4, "ΔV", size=10, color=MUTED, anchor="end"))

    fb = fitbox(ox, oy + 52, ax_w + 40, 40,
                "slew rate = ΔV / Δt   (В/нс)   —   той самий розмах ΔV, "
                "але коротший фронт = крутіший нахил = вищий slew rate",
                size=12, fill="#f4f6f8", stroke=INK)
    f.append(fb)

    render(os.path.join(IMG, "slew-on-pin.svg"), W, H, *f)


# ── 2. Ядро теми (DSP-кут): спектр фронту — дві злами, крутіший край свистить вище
# Ідея: цифровий сигнал = сума синусоїд (спектр). Обвідна спектру трапецієподібного
# імпульсу має дві злами: f1=1/(π·T) (спад −20 дБ/дек) і f2=1/(π·τ) (спад −40 дБ/дек).
# Другу зламу СУНЕ час фронту τ: крутіший фронт → f2 праворуч → більше енергії на
# високих частотах → сильніше випромінювання. Показуємо ДВІ обвідні: повільний
# фронт (f2 ліворуч, тихо вгорі) і швидкий фронт (f2 праворуч, гучно вгорі).
def fig_edge_spectrum():
    W, H = 780, 430
    f = []
    f.append(text(W / 2, 26, "Фронт у частотах: крутіший край засвічує вищі частоти", size=15, bold=True))

    ox, oy = 92, 330
    ax_w, ax_h = 590, 250
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))          # вісь частоти (log)
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))          # вісь амплітуди (dB)
    f.append(text(ox + ax_w, oy + 22, "частота (лог)", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ax_h + 6, "амплітуда", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ax_h + 20, "гармонік, дБ", size=11, color=MUTED, anchor="end"))

    top = oy - ax_h * 0.86         # рівень «пласкої» полиці
    f.append(line(ox, top, ox + ax_w, top, color=MUTED, sw=1, dash="4,4"))

    # характерні частоти вздовж осі (умовні позиції в лог-масштабі)
    xf1 = ox + ax_w * 0.16     # f1 = 1/(π·T)   (від тривалості імпульсу)
    xf2s = ox + ax_w * 0.42    # f2 повільного фронту = 1/(π·τ_slow)
    xf2f = ox + ax_w * 0.70    # f2 швидкого  фронту = 1/(π·τ_fast)

    def env(x_start, y_start, x_knee, slope1_dydx, x_end, slope2_dydx):
        # ламана: полиця → −20 дБ/дек від f1 → −40 дБ/дек від f2
        return [(x_start, y_start), (x_knee, y_start + slope1_dydx * (x_knee - x_start)),
                (x_end, y_start + slope1_dydx * (x_knee - x_start) + slope2_dydx * (x_end - x_knee))]

    # нахили в пікселях (умовні, лише для наочності «−20» vs «−40»)
    s20 = 0.30      # спад після f1
    s40s = 0.66     # крутіший спад після f2 (повільний фронт)
    s40f = 0.66

    # ── обвідна ПОВІЛЬНОГО фронту (f2 ліворуч): рано валиться, вгорі тихо ──
    y_at_f1 = top
    pts_s = env(ox, top, xf1, 0, xf1, 0)  # полиця до f1
    # від f1 до f2s: −20; від f2s далі: −40
    yf2s = top + s20 * (xf2s - xf1)
    x_end = ox + ax_w
    ye_s = yf2s + s40s * (x_end - xf2s)
    seg_s = [(ox, top), (xf1, top), (xf2s, yf2s), (x_end, min(ye_s, oy))]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in seg_s), NEG))
    f.append(text(x_end - 4, min(ye_s, oy) - 8, "повільний фронт", size=11, color=NEG, anchor="end", bold=True))

    # ── обвідна ШВИДКОГО фронту (f2 праворуч): тримається довше, вгорі гучно ──
    yf2f = top + s20 * (xf2f - xf1)
    ye_f = yf2f + s40f * (x_end - xf2f)
    seg_f = [(ox, top), (xf1, top), (xf2f, yf2f), (x_end, min(ye_f, oy))]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in seg_f), POS))
    f.append(text(x_end - 4, min(ye_f, oy) - 8, "швидкий фронт", size=11, color=POS, anchor="end", bold=True))

    # злами й підписи
    for xx, lab, sub, col in [
        (xf1, "f1 = 1/(π·T)", "тривалість імпульсу", MUTED),
        (xf2s, "f2 = 1/(π·τ)", "повільний τ", NEG),
        (xf2f, "f2 = 1/(π·τ)", "швидкий τ", POS)]:
        f.append(line(xx, oy, xx, oy - ax_h + 8, color=col, sw=1, dash="3,4"))
        f.append(circle(xx, top if xx == xf1 else (yf2s if col == NEG else yf2f), 4, fill=col, stroke=col, sw=1))
    f.append(text(xf1, oy + 16, "f1", size=11, color=INK, bold=True))
    f.append(text(xf1, oy + 30, "1/(π·T)", size=9, color=MUTED))
    f.append(text(xf2s, oy + 16, "f2 (повільн.)", size=10, color=NEG))
    f.append(text(xf2f, oy + 16, "f2 (швидк.)", size=10, color=POS))

    # позначки нахилів
    f.append(text((xf1 + xf2s) / 2, top + s20 * ((xf1 + xf2s) / 2 - xf1) - 10, "−20 дБ/дек", size=10, color=MUTED, bold=True))
    f.append(text(xf2f + 60, yf2f + s40f * 60 - 8, "−40 дБ/дек", size=10, color=POS, bold=True))

    # стрілка «τ ↓ → f2 сунеться праворуч»
    f.append(arrow(xf2s + 6, oy - ax_h + 22, xf2f - 6, oy - ax_h + 22, color=INK, sw=2))
    f.append(text((xf2s + xf2f) / 2, oy - ax_h + 14, "коротший фронт τ  →  f2 праворуч", size=10.5, color=INK, bold=True))

    fb = fitbox(ox, oy + 44, ax_w + 40, 38,
                "уся зайва енергія над f2 — це радіозавада: крутіший фронт (менший τ) "
                "піднімає f2, і високі частоти лунають гучніше",
                size=11.5, fill="#fdecea", stroke=POS)
    f.append(fb)

    render(os.path.join(IMG, "edge-spectrum.svg"), W, H, *f)


# ── 3. i = C·dV/dt: крутіший фронт — вищий пік струму живлення → стрибок землі ─
# Ідея: заряд ємності лінії Q=C·ΔV однаковий, хоч крутий фронт, хоч пологий. Але
# крутий втискає той самий заряд у КОРОТШИЙ час → пік струму i=C·dV/dt ВИЩИЙ і
# вужчий. Цей різкий пік через індуктивність виводу L дає стрибок «землі»
# V=L·di/dt, що фонить у сусідні тихі ніжки. Дві пари: фронт V(t) і струм i(t).
def fig_current_spike():
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 26, "Той самий заряд за коротший час — вищий пік струму живлення", size=15, bold=True))

    left = 84
    right = 700
    def X(t):  # t у 0..1
        return left + (right - left) * t

    # ── верх: два фронти напруги ──
    ax_v = 70
    f.append(text(left - 8, ax_v - 8, "напруга на лінії V", size=11, anchor="end", bold=True))
    lo_v, hi_v = ax_v + 54, ax_v
    f.append(line(left, lo_v, right, lo_v, color=MUTED, sw=1))
    # пологий фронт (широкий)
    xs0, xs1 = X(0.10), X(0.52)
    f.append(line(left, lo_v, xs0, lo_v, color=NEG, sw=2.6))
    f.append(line(xs0, lo_v, xs1, hi_v, color=NEG, sw=2.6))
    f.append(line(xs1, hi_v, right, hi_v, color=NEG, sw=2.6))
    f.append(text(xs1 + 8, hi_v + 4, "пологий", size=10, color=NEG, anchor="start", bold=True))
    # крутий фронт (вузький)
    xf0, xf1 = X(0.10), X(0.22)
    f.append(line(xf0, lo_v, xf1, hi_v, color=POS, sw=2.6))
    f.append(text(xf1 + 6, hi_v - 8, "крутий", size=10, color=POS, anchor="start", bold=True))

    # ── низ: піки струму i = C·dV/dt (площа = заряд Q = C·ΔV однакова) ──
    ax_i = 210
    base_i = ax_i + 110
    f.append(text(left - 8, ax_i - 6, "струм заряду i = C·(dV/dt)", size=11, anchor="end", bold=True))
    f.append(line(left, base_i, right, base_i, color=INK, sw=1.6))
    f.append(text(right, base_i + 16, "час t", size=10, color=MUTED, anchor="end"))

    # пологий: низький широкий горб (напівхвиля), площа A
    def bump(x0, x1, peak, col, dash=None):
        n = 40
        pts = [(x0, base_i)]
        for k in range(n + 1):
            t = k / n
            x = x0 + (x1 - x0) * t
            y = base_i - peak * math.sin(math.pi * t)
            pts.append((x, y))
        pts.append((x1, base_i))
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="2.4"%s/>'
                % (" ".join("%.1f,%.1f" % p for p in pts), col, col, da))

    # площі рівні: peak_slow*(width_slow) ≈ peak_fast*(width_fast)
    w_slow = 0.42
    w_fast = 0.12
    peak_slow = 46
    peak_fast = peak_slow * (w_slow / w_fast)   # ↑ у стільки ж разів, у скільки вужче
    f.append(bump(X(0.10), X(0.10 + w_slow), peak_slow, NEG))
    f.append(bump(X(0.10), X(0.10 + w_fast), peak_fast, POS))
    f.append(text(X(0.10 + w_slow) + 6, base_i - peak_slow / 2, "низький пік", size=10, color=NEG, anchor="start", bold=True))
    f.append(text(X(0.10 + w_fast) + 8, base_i - peak_fast + 6, "високий вузький пік", size=10.5, color=POS, anchor="start", bold=True))
    f.append(text(X(0.30), base_i - 8, "площа = заряд Q = C·ΔV  (однакова!)", size=10, color=MUTED))

    fb = fitbox(left, base_i + 30, right - left, 42,
                "різкий пік струму на індуктивності виводу L дає стрибок «землі»  V = L·(di/dt)  —  "
                "тихі сусідні ніжки на мить підстрибують: це власний шум крутого фронту",
                size=11, fill="#fdecea", stroke=POS)
    f.append(fb)

    render(os.path.join(IMG, "current-spike.svg"), W, H, *f)


# ── 4. Регістр швидкості: під кожну частоту — свій драйвер; бери найповільніший ─
# Ідея: практичний висновок. Поле output-speed (напр. OSPEEDR STM32) — 4 сходинки:
# кожна вмикає драйвер із певною крутістю під певну стелю частоти. Правило: бери
# найповільнішу сходинку, що ще встигає за сигналом. Показуємо сходинки+приклади.
def fig_speed_setting():
    W, H = 760, 400
    f = []
    f.append(text(W / 2, 26, "Поле швидкості ніжки: обери найповільнішу сходинку, що ще встигає", size=15, bold=True))

    # чотири сходинки (умовні межі — залежать від сім'ї МК, ємності, живлення)
    steps = [
        ("Low",       "до ~кількох МГц",  "миготіння LED, кнопка, реле",       FIELD, "#eaf6ee"),
        ("Medium",    "до ~десятків МГц", "UART, повільний SPI/I2C",           "#2e8b57", "#e8f7ee"),
        ("High",      "до ~сотні МГц",    "швидкий SPI, тактові лінії",        "#e08a2b", "#fff3cd"),
        ("Very High", "найкрутіший фронт","пам'ять, високошвидкісні шини",     POS, "#fdecea"),
    ]
    x0 = 60
    row_w = 640
    row_h = 58
    top = 60
    for i, (name, band, use, col, fill) in enumerate(steps):
        y = top + i * (row_h + 10)
        f.append(rect(x0, y, row_w, row_h, fill=fill, stroke=col, sw=1.8, rx=8))
        # сходинка-«стовпчик» ліворуч показує зростання крутості
        bar_h = 12 + (i + 1) * 8
        f.append(rect(x0 + 16, y + row_h - 10 - bar_h, 22, bar_h, fill=col, stroke=col, sw=1, rx=3))
        f.append(text(x0 + 70, y + 24, name, size=14, color=col, anchor="start", bold=True))
        f.append(text(x0 + 70, y + 44, band, size=11, color=MUTED, anchor="start"))
        f.append(text(x0 + 300, y + 24, "приклад: " + use, size=11.5, color=INK, anchor="start"))
        f.append(text(x0 + 300, y + 44, "крутість фронту тим вища, чим нижче тут", size=9.5, color=MUTED, anchor="start"))

    # стрілка «повільніше=тихіше» ліворуч
    f.append(arrow(x0 - 22, top + 6, x0 - 22, top + 3 * (row_h + 10) + row_h - 6, color=INK, sw=2))
    f.append(text(x0 - 34, top + 2 * (row_h + 10), "крутість ↑", size=10, color=INK, anchor="middle", bold=True))

    fb = fitbox(60, top + 4 * (row_h + 10) + 4, 640, 34,
                "правило: НЕ став «Very High» про всяк випадок — зайва крутість іде не в користь, "
                "а в дзвін, стрибок землі й радіозаваду",
                size=11.5, fill="#f4f6f8", stroke=INK)
    f.append(fb)

    render(os.path.join(IMG, "speed-setting.svg"), W, H, *f)


# ── 5. [math-вставка] Прямокутник → sinc: звідки береться π у зламі 1/(π·T) ────
# Ідея: спектр прямокутника ширини T — це A·T·sin(πfT)/(πfT). Малюємо |X(f)| у
# лінійних осях: пелюстки sinc з нулями на 1/T, 2/T… НАД ними — дві асимптоти
# обвідної: пласка полиця A·T (низькі f) і спадна гілка A/(πf) (високі f). Вони
# перетинаються рівно на f = 1/(π·T) — ОСЬ звідки π: це стик двох асимптот, а не
# перший нуль (той на 1/T). Показуємо обидва: нуль на 1/T і злам-асимптоту на 1/(πT).
def fig_rect_to_sinc():
    W, H = 780, 400
    f = []
    f.append(text(W / 2, 26, "Спектр прямокутника — sinc; π у зламі — це стик двох асимптот обвідної", size=14.5, bold=True))

    ox, oy = 84, 300
    ax_w, ax_h = 620, 232
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))            # вісь частоти
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))            # вісь |X(f)|
    f.append(text(ox + ax_w, oy + 22, "частота f (лінійна)", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy - ax_h + 8, "|X(f)|", size=11, color=MUTED, anchor="end"))

    AT = ax_h * 0.80          # рівень A·T (значення обвідної на f→0)
    top = oy - AT
    # горизонт «частоти» у px: 1/T → xT ; масштаб так, щоб влізло ~4/T
    per = (ax_w - 30) / 4.3   # px на 1/T
    def X(finvT):             # аргумент у одиницях 1/T
        return ox + per * finvT

    # sinc |sin(πx)/(πx)| у одиницях x = f·T (пелюстки з нулями на цілих x)
    n = 260
    pts = []
    for k in range(n + 1):
        x = 0.001 + (4.2) * k / n
        val = abs(math.sin(math.pi * x) / (math.pi * x))
        pts.append((X(x), oy - AT * val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), INK))

    # асимптота 1: пласка полиця A·T
    f.append(line(ox, top, X(2.4), top, color=FIELD, sw=2, dash="7,4"))
    f.append(text(X(0.62), top - 9, "полиця A·T (обвідна при низьких f)", size=10.5, color=FIELD, anchor="start", bold=True))

    # асимптота 2: спадна гілка A/(πf) = (A·T)/(πx) — гіпербола обвідної
    hyp = []
    for k in range(n + 1):
        x = 1.0 / math.pi + (4.2 - 1.0 / math.pi) * k / n
        val = 1.0 / (math.pi * x)
        hyp.append((X(x), oy - AT * val))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="7,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in hyp), POS))
    f.append(text(X(2.55), oy - AT / (math.pi * 2.55) - 6, "спад A/(π·f) → −20 дБ/дек", size=10.5, color=POS, anchor="start", bold=True))

    # точка стику асимптот: x = 1/π  (тобто f = 1/(π·T))
    xk = 1.0 / math.pi
    f.append(line(X(xk), oy, X(xk), top, color=NEG, sw=1.4, dash="3,4"))
    f.append(circle(X(xk), top, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(X(xk) - 4, top - 12, "злам обвідної", size=10.5, color=NEG, anchor="middle", bold=True))
    f.append(text(X(xk), oy + 16, "f = 1/(π·T)", size=11, color=NEG, bold=True))
    f.append(text(X(xk), oy + 30, "x = 1/π ≈ 0.318", size=9, color=MUTED))

    # перший НУЛЬ sinc: x = 1 (f = 1/T) — щоб не сплутати з π-зламом
    f.append(line(X(1), oy, X(1), oy - 8, color=MUTED, sw=1.2))
    f.append(text(X(1), oy + 16, "1/T", size=10, color=MUTED))
    f.append(text(X(1), oy + 29, "(перший нуль)", size=8.5, color=MUTED))
    f.append(text(X(2), oy + 16, "2/T", size=10, color=MUTED))
    f.append(line(X(2), oy, X(2), oy - 6, color=MUTED, sw=1))

    fb = fitbox(ox, oy + 40, ax_w + 30, 34,
                "π — не з нуля sinc (той на 1/T), а зі СТИКУ асимптот: "
                "полиця A·T зустрічає гілку A/(π·f) саме на 1/(π·T)",
                size=12, fill="#eaf0fd", stroke=NEG)
    f.append(fb)

    render(os.path.join(IMG, "rect-to-sinc.svg"), W, H, *f)


# ── 6. [math-вставка] Дві злами обвідної: тривалість дає першу, час фронту — другу
# Ідея: трапеція = прямокутник(T) ⊛ прямокутник(τ) → спектр = A·T·sinc(fT)·sinc(fτ)
# → ДОБУТОК двох гіпербол обвідної. Кожен множник додає свій злам-корінь: sinc(fT)
# ламає на 1/(π·T) (−20), sinc(fτ) додає ще −20 на 1/(π·τ) → сумарно −40. Малюємо
# лог-лог обвідну як складання двох «сходинок нахилу»; підпис: T керує нижнім
# зламом, τ — верхнім, і саме τ (час фронту) визначає, ДОКИ спектр тягнеться.
def fig_two_corners():
    W, H = 780, 420
    f = []
    f.append(text(W / 2, 26, "Трапеція = два прямокутники згорнуто → два зломи обвідної (−20, потім −40)", size=14, bold=True))

    ox, oy = 92, 322
    ax_w, ax_h = 600, 250
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))            # log f
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))            # dB
    f.append(text(ox + ax_w, oy + 22, "частота f (лог)", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy - ax_h + 8, "обвідна, дБ", size=11, color=MUTED, anchor="end"))

    top = oy - ax_h * 0.86
    f.append(line(ox, top, ox + ax_w, top, color=MUTED, sw=1, dash="4,4"))
    f.append(text(ox + 6, top - 8, "полиця A·T (уся енергія тут і нижче)", size=10, color=MUTED, anchor="start"))

    # злами вздовж лог-осі
    xf1 = ox + ax_w * 0.30       # f1 = 1/(π·T)
    xf2 = ox + ax_w * 0.66       # f2 = 1/(π·τ)
    s20 = 0.34
    y_f2 = top + s20 * (xf2 - xf1)
    x_end = ox + ax_w
    y_end = y_f2 + 2 * s20 * (x_end - xf2)      # −40 = удвічі крутіше
    y_end = min(y_end, oy - 6)
    seg = [(ox, top), (xf1, top), (xf2, y_f2), (x_end, y_end)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in seg), INK))

    # позначки зламів
    for xx, lab, sub, col in [(xf1, "f1 = 1/(π·T)", "тривалість T", NEG),
                              (xf2, "f2 = 1/(π·τ)", "час фронту τ", POS)]:
        f.append(line(xx, oy, xx, oy - ax_h + 8, color=col, sw=1.2, dash="3,4"))
        f.append(circle(xx, top if xx == xf1 else y_f2, 5, fill=col, stroke=col, sw=1))
        f.append(text(xx, oy + 16, lab.split(" = ")[0], size=11, color=col, bold=True))
        f.append(text(xx, oy + 30, sub, size=9.5, color=col))

    # нахили
    f.append(text((xf1 + xf2) / 2, top + s20 * ((xf1 + xf2) / 2 - xf1) - 9, "−20 дБ/дек", size=10.5, color=INK, bold=True))
    f.append(text(xf2 + 66, y_f2 + 2 * s20 * 66 - 8, "−40 дБ/дек", size=10.5, color=POS, bold=True))

    # який множник додає який злам — дві мітки-«sinc»
    f.append(textbox(xf1, top - 34, "sinc(f·T)\nламає тут", size=9.5, fill="#eaf0fd", stroke=NEG, color=NEG)[0])
    f.append(textbox(xf2, y_f2 - 40, "sinc(f·τ)\nдодає ще −20", size=9.5, fill="#fdecea", stroke=POS, color=POS)[0])

    # стрілка «τ↓ → f2 праворуч → спектр тягнеться вище»
    f.append(arrow(xf2 + 6, oy - ax_h + 20, x_end - 20, oy - ax_h + 20, color=INK, sw=2))
    f.append(text((xf2 + x_end) / 2 - 8, oy - ax_h + 12, "коротший τ → f2 вгору → спектр тягнеться вище", size=10, color=INK, bold=True))

    fb = fitbox(ox, oy + 44, ax_w + 30, 34,
                "верхню межу спектра тримає f2 = 1/(π·τ): керує НЕ висота A, а час фронту τ — "
                "тому крутість фронту прямо визначає радіозаваду",
                size=11, fill="#fdecea", stroke=POS)
    f.append(fb)

    render(os.path.join(IMG, "two-corners.svg"), W, H, *f)


# ── 7. [hist-вставка] Дві нитки історії: логіка крутішає ↔ регулятор наздоганяє ─
# Ідея: верхня нитка — марш логіки до крутіших фронтів (TTL 1966 → 74HC 1983 →
# 74AC 1985), і разом із фронтами верхня межа спектра повзе в радіодіапазон.
# Нижня нитка — регулятор наздоганяє (справа FCC 1976, Part 15 для цифри 1979,
# обов'язкові дати 1981-83, CISPR 22 1985, Директива EMC обов'язкова 1996).
# У точці перетину крутість фронту стає питанням допуску виробу на ринок.
def fig_emc_history_timeline():
    W, H = 820, 430
    f = []
    f.append(text(W / 2, 26, "Дві нитки, що зійшлися: фронти крутішають ↔ регулятор наздоганяє", size=15, bold=True))

    left, right = 70, 770
    # спільна вісь років: 1966..1996 → x
    y0, y1 = 1965.0, 1997.0
    def X(year):
        return left + (right - left) * (year - y0) / (y1 - y0)

    # ── верхня нитка: логіка крутішає фронтами ──
    top_y = 96
    f.append(line(left, top_y, right, top_y, color=NEG, sw=2.4))
    f.append(text(left, top_y - 40, "ЛОГІКА: фронти крутішають → спектр повзе в ефір", size=12, color=NEG, anchor="start", bold=True))
    logic = [
        (1966, "TTL 7400", "~22 нс, пологі\nв ефір тихо"),
        (1971, "74LS",     "~15 нс\nпомірні"),
        (1983, "74HC",     "~наносекундні\nфронти"),
        (1985, "74AC",     "~1-2 нс, круті\nв ефір гучно"),
    ]
    for yr, name, sub in logic:
        x = X(yr)
        # висота маркера росте з крутістю фронту (умовно: чим пізніше, тим вище «спектр»)
        rise = 8 + (yr - 1966) * 0.9
        col = NEG if yr < 1983 else POS
        f.append(line(x, top_y, x, top_y - rise, color=col, sw=2))
        f.append(circle(x, top_y - rise, 4.5, fill=col, stroke=col, sw=1))
        f.append(text(x, top_y + 16, str(yr), size=10.5, color=INK, bold=True))
        f.append(text(x, top_y + 30, name, size=11, color=col, bold=True))
        f.append(mtext(x, top_y - rise - 20, sub.split("\n"), size=9, color=MUTED, lh=1.25))

    # ── нижня нитка: регулятор наздоганяє ──
    bot_y = 300
    f.append(line(left, bot_y, right, bot_y, color=FIELD, sw=2.4))
    f.append(text(left, bot_y + 62, "РЕГУЛЯТОР: обов'язкові межі випромінювання", size=12, color=FIELD, anchor="start", bold=True))
    rules = [
        (1976, "Docket 20780", "FCC відкриває\nсправу"),
        (1979, "FCC Part 15", "правила для\nцифри (79-555)"),
        (1981, "обов'язково", "нова техніка\n(США)"),
        (1985, "CISPR 22", "норма для IT\n(→ EN 55022)"),
        (1996, "Директива EMC", "обов'язкова\nв ЄС (CE)"),
    ]
    for yr, name, sub in rules:
        x = X(yr)
        f.append(line(x, bot_y, x, bot_y + 10, color=FIELD, sw=2))
        f.append(circle(x, bot_y + 10, 4.5, fill=FIELD, stroke=FIELD, sw=1))
        f.append(text(x, bot_y - 8, str(yr), size=10.5, color=INK, bold=True))
        f.append(text(x, bot_y - 22, name, size=10.5, color=FIELD, bold=True))
        f.append(mtext(x, bot_y + 30, sub.split("\n"), size=9, color=MUTED, lh=1.25))

    # ── точка перетину: 1979-1981, крутість фронту = питання допуску на ринок ──
    xc = X(1980)
    f.append(line(xc, top_y + 40, xc, bot_y - 40, color=POS, sw=1.6, dash="5,4"))
    box = textbox(xc, (top_y + bot_y) / 2 + 6,
                  "точка перетину:\nкрутість фронту стає\nпитанням ДОПУСКУ\nвиробу на ринок",
                  size=10, fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(box[0])

    fb = fitbox(left, bot_y + 78, right - left, 34,
                "індустрія прискорила фронти, не думаючи про ефір → плати заговорили в радіодіапазоні → "
                "з'явилися межі й сертифікація → керування крутістю стало стандартним прийомом",
                size=11, fill="#f4f6f8", stroke=INK)
    f.append(fb)

    render(os.path.join(IMG, "emc-history-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_slew_on_pin()
    fig_edge_spectrum()
    fig_current_spike()
    fig_speed_setting()
    fig_rect_to_sinc()
    fig_two_corners()
    fig_emc_history_timeline()
    print("OK: figures written to", IMG)
