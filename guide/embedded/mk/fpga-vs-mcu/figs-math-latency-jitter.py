# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MCU  = "#2457d6"   # мікроконтролер
FPGA = "#1f8a3b"   # FPGA
WARM = "#c0392b"   # небезпека / хвіст / зрив дедлайну


# ── jitter-distribution: затримка МК як РОЗПОДІЛ — тіло біля кращого разу + довгий хвіст ──
# Ідея вставки, яку неможливо передати смугою: затримка — не число, а випадкова
# величина. Гострий пік біля кращого разу (система вільна) + довгий правий хвіст
# (усі невдачі збіглися). Середнє лежить ЛІВОРУЧ від дедлайну — «в середньому
# встигаємо», — а хвіст РОЗПОДІЛУ перетинає дедлайн: саме ці рідкі випадки й зривають.
# FPGA поряд — вузька риска: одне число без хвоста.

def fig_jitter_distribution():
    W, H = 760, 430
    # осі графіка розподілу
    ox, oy = 70, 300            # початок координат (лівий-нижній)
    aw, ah = 620, 210           # ширина/висота поля
    p = [text(W/2, 30, "Затримка мікроконтролера — це розподіл, а не одне число",
              size=17, bold=True),
         text(W/2, 50, "гострий пік біля кращого разу + довгий хвіст, де збіглися всі невдачі",
              size=11.5, color=MUTED, italic=True)]

    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))              # X
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))             # Y
    p.append(text(ox + aw, oy + 22, "затримка реакції t", size=11, color=INK, anchor="end", italic=True))
    p.append(text(ox - 8, oy - ah + 4, "щільність ймовірності", size=10, color=MUTED, anchor="end"))

    # параметри розподілу (у «пікселях осі»): пік біля кращого разу + важкий хвіст
    best_x = ox + 0.16 * aw       # положення піку (кращий раз)
    peak   = 0.92 * ah            # висота піку
    # крива: швидкий підйом до піку, потім повільний спад із довгим хвостом
    def dens(u):                  # u ∈ [0..1] по осі, повертає висоту 0..1
        # ліва частина — крутий фронт; права — важкий хвіст ~ 1/(1+k(u-u0))
        u0 = 0.16
        if u < u0:
            return (u / u0) ** 2 * 0.92
        return 0.92 / (1.0 + 26.0 * (u - u0) ** 1.35)
    N = 240
    pts = []
    for i in range(N + 1):
        u = i / N
        x = ox + u * aw
        y = oy - dens(u) * ah
        pts.append((x, y))
    # заливка під кривою (тіло — синє, хвіст за дедлайном — червоне)
    dead_u = 0.62                 # положення дедлайну по осі
    dead_x = ox + dead_u * aw
    # тіло (до дедлайну)
    body = ["M %.1f %.1f" % (ox, oy)]
    for (x, y) in pts:
        if (x - ox) / aw <= dead_u:
            body.append("L %.1f %.1f" % (x, y))
    body.append("L %.1f %.1f Z" % (dead_x, oy))
    p.append('<path d="%s" fill="#e9effb" stroke="none"/>' % " ".join(body))
    # хвіст (за дедлайном) — червоний
    tail = ["M %.1f %.1f" % (dead_x, oy)]
    for (x, y) in pts:
        if (x - ox) / aw >= dead_u:
            tail.append("L %.1f %.1f" % (x, y))
    tail.append("L %.1f %.1f Z" % (ox + aw, oy))
    p.append('<path d="%s" fill="#fbe6e2" stroke="none"/>' % " ".join(tail))
    # сама крива поверх
    poly = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, MCU))

    # вертикалі: кращий раз, середнє, дедлайн
    mean_x = ox + 0.30 * aw
    p.append(line(best_x, oy, best_x, oy - peak - 4, color=MUTED, sw=1.3, dash="3 3"))
    p.append(text(best_x, oy - peak - 10, "кращий раз", size=9.5, color=MUTED))
    p.append(line(mean_x, oy, mean_x, oy - 0.62 * ah, color=INK, sw=1.6))
    p.append(text(mean_x, oy - 0.62 * ah - 8, "середнє", size=10, color=INK, bold=True))
    p.append(text(mean_x, oy - 0.62 * ah - 22, "«в середньому встигаємо»", size=9, color=MUTED, italic=True))
    p.append(line(dead_x, oy - ah - 6, dead_x, oy + 8, color=WARM, sw=2.2))
    p.append(text(dead_x + 6, oy - ah - 0, "ДЕДЛАЙН", size=11, color=WARM, anchor="start", bold=True))

    # підпис хвоста
    p.append(line(ox + 0.80 * aw, oy - 0.14 * ah, ox + 0.80 * aw, oy - 0.02 * ah, color=WARM, sw=1.0))
    box = fitbox(ox + 0.66 * aw, oy - 0.44 * ah, 0.33 * aw, 46,
                 "хвіст за дедлайном =\nймовірність зриву",
                 size=10, pad=6, fill="#fdf1ee", stroke=WARM, sw=1.4, bold=True, color=WARM)
    p.append(box)

    # FPGA поряд — вузька риска (одне число без хвоста)
    fx = ox + 0.10 * aw
    p.append(line(fx, oy, fx, oy - 0.30 * ah, color=FPGA, sw=5))
    p.append(text(fx - 4, oy - 0.30 * ah - 8, "FPGA:", size=9.5, color=FPGA, anchor="middle", bold=True))
    p.append(text(fx - 4, oy - 0.30 * ah - 21, "одне число,", size=8.5, color=FPGA, anchor="middle"))
    p.append(text(fx - 4, oy - 0.30 * ah - 32, "без хвоста", size=8.5, color=FPGA, anchor="middle"))

    # висновок
    p.append(text(W/2, oy + 58,
                  "Середнє ліворуч від дедлайну — та реальні зриви живуть у ХВОСТІ, який середнє не бачить.",
                  size=11, bold=True))
    p.append(text(W/2, oy + 76,
                  "Жорсткий реальний час вимірюється найгіршим випадком і формою хвоста, а не середнім.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "jitter-distribution.svg"), W, oy + 96, *p)


# ── miss-vs-load: ймовірність зриву дедлайну як функція завантаженості перериваннями ──
# Ідея: коли ядро зайняте іншими перериваннями, доданок витіснення росте, хвіст
# розповзається праворуч — і ймовірність зриву стрибає нелінійно. Є «коліно»:
# до нього майже нуль, після нього — швидко до одиниці. Показуємо криву P(зрив) vs U.

def fig_miss_vs_load():
    W, H = 760, 420
    ox, oy = 78, 300
    aw, ah = 610, 210
    p = [text(W/2, 30, "Завантаженість перериваннями -> ймовірність зриву дедлайну",
              size=17, bold=True),
         text(W/2, 50, "чим більше ядро зайняте, тим товщий хвіст витіснення — і тим ближче зрив",
              size=11.5, color=MUTED, italic=True)]

    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "завантаженість перериваннями  U = Σ fᵢ·t(ISR)ᵢ",
                  size=11, color=INK, anchor="end", italic=True))
    p.append(text(ox - 8, oy - ah + 2, "P(зрив дедлайну)", size=10, color=MUTED, anchor="end"))
    # позначки осі X
    for u, lab in [(0.0, "0"), (0.25, "25%"), (0.5, "50%"), (0.75, "75%"), (1.0, "100%")]:
        x = ox + u * aw
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        p.append(text(x, oy + 18, lab, size=9.5, color=MUTED))
    for pr, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]:
        y = oy - pr * ah
        p.append(line(ox - 5, y, ox, y, color=INK, sw=1.2))
        p.append(text(ox - 10, y + 4, lab, size=9.5, color=MUTED, anchor="end"))

    # крива: логістичне «коліно» — до ~0.6 майже нуль, потім різко вгору
    def pmiss(u):
        # згладжена сигмоїда з коліном біля u0
        u0, k = 0.68, 13.0
        return 1.0 / (1.0 + math.exp(-k * (u - u0)))
    N = 200
    pts = []
    for i in range(N + 1):
        u = i / N
        x = ox + u * aw
        y = oy - pmiss(u) * ah
        pts.append((x, y))
    poly = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, MCU))

    # позначити коліно
    knee_x = ox + 0.68 * aw
    knee_y = oy - 0.5 * ah
    p.append(circle(knee_x, knee_y, 5, fill=WARM, stroke=WARM, sw=1))
    p.append(line(knee_x, knee_y, knee_x + 70, knee_y - 46, color=WARM, sw=1.1))
    box = fitbox(knee_x + 40, knee_y - 84, 210, 40,
                 "«коліно»: далі кожен\nвідсоток U коштує дорого",
                 size=10, pad=6, fill="#fdf1ee", stroke=WARM, sw=1.4, bold=True, color=WARM)
    p.append(box)

    # зона «здоровий запас» ліворуч
    p.append(rect(ox, oy - 0.10 * ah, 0.5 * aw, 0.10 * ah, fill="#eef7ee", stroke="none"))
    p.append(text(ox + 0.25 * aw, oy - 0.045 * ah, "тут майже завжди встигаємо", size=9.5, color=FPGA))

    # права зона — «майже завжди спізнюємось»
    p.append(rect(ox + 0.82 * aw, oy - ah, 0.18 * aw, 0.14 * ah, fill="#fbe6e2", stroke="none"))
    p.append(text(ox + 0.91 * aw, oy - ah + 0.09 * ah, "зрив майже певний", size=9, color=WARM))

    p.append(text(W/2, oy + 54,
                  "Крива не лінійна: до коліна запас великий, після — система «раптом» починає спізнюватися.",
                  size=11, bold=True))
    p.append(text(W/2, oy + 72,
                  "Тому в жорсткому реальному часі тримають U далеко ліворуч від коліна, а не «під одиницею».",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "miss-vs-load.svg"), W, oy + 92, *p)


# ── fanout-tail: рідкісний зрив на ОДНІЙ події множиться на багато подій/каналів ──
# Ідея (з «The Tail at Scale»): нехай на одну подію ймовірність зриву q мала.
# Але за секунду подій багато (або каналів багато), і система зривається, якщо
# зірветься ХОЧ ОДНА: P = 1 − (1−q)^N. Навіть крихітне q за великого N -> майже 1.
# Це і є місток «в середньому встигаємо» -> «у полі стабільно спізнюємось».

def fig_fanout_tail():
    W, H = 760, 420
    ox, oy = 78, 300
    aw, ah = 610, 210
    p = [text(W/2, 30, "Рідкісний зрив на одній події стає певним на багатьох",
              size=17, bold=True),
         text(W/2, 50, "P(зрив хоч раз) = 1 − (1 − q)ᴺ — маленьке q за великого N прямує до одиниці",
              size=11.5, color=MUTED, italic=True)]

    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 22, "кількість подій за дедлайн-вікно  N", size=11, color=INK, anchor="end", italic=True))
    p.append(text(ox - 8, oy - ah + 2, "P(хоч один зрив)", size=10, color=MUTED, anchor="end"))

    Nmax = 5000
    def logx(n):                    # логарифмічна вісь N (1..Nmax)
        return ox + (math.log10(max(n, 1)) / math.log10(Nmax)) * aw
    # позначки осі X (лог)
    for n, lab in [(1, "1"), (10, "10"), (100, "100"), (1000, "1000"), (5000, "5000")]:
        x = logx(n)
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        p.append(text(x, oy + 18, lab, size=9.5, color=MUTED))
    for pr, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]:
        y = oy - pr * ah
        p.append(line(ox - 5, y, ox, y, color=INK, sw=1.2))
        p.append(text(ox - 10, y + 4, lab, size=9.5, color=MUTED, anchor="end"))

    # три криві для різних q
    curves = [
        (0.01,   MCU,  "q = 1%  (один зрив зі 100)"),
        (0.001,  WARM, "q = 0.1%  (один із 1000)"),
        (0.0001, FPGA, "q = 0.01%  (один із 10000)"),
    ]
    lx = ox + 0.04 * aw
    ly = oy - ah + 22
    for q, col, lab in curves:
        pts = []
        n = 1
        while n <= Nmax:
            x = logx(n)
            y = oy - (1.0 - (1.0 - q) ** n) * ah
            pts.append((x, y))
            n = int(n * 1.12) + 1
        poly = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, col))
        # легенда
        p.append(line(lx, ly, lx + 22, ly, color=col, sw=2.6))
        p.append(text(lx + 28, ly + 4, lab, size=10, color=col, anchor="start", bold=True))
        ly += 18

    # маркер: приклад «The Tail at Scale» (100 подій, q=1% -> ~63%)
    ex_x = logx(100)
    ex_y = oy - (1.0 - 0.99 ** 100) * ah
    p.append(circle(ex_x, ex_y, 5, fill=INK, stroke=INK, sw=1))
    p.append(line(ex_x, ex_y, ex_x + 60, ex_y + 40, color=INK, sw=1.0))
    box = fitbox(ex_x + 30, ex_y + 40, 250, 42,
                 "100 подій · q=1% -> 63% зривів\n(приклад Dean & Barroso, 2013)",
                 size=9.5, pad=6, fill="#eef0f4", stroke=INK, sw=1.3, bold=True)
    p.append(box)

    p.append(text(W/2, oy + 54,
                  "«Один раз на 10 000» звучить безпечно — доки подій не стануть тисячі за секунду.",
                  size=11, bold=True))
    p.append(text(W/2, oy + 72,
                  "FPGA прибирає q біля нуля структурно: немає хвоста -> немає чому множитися.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "fanout-tail.svg"), W, oy + 92, *p)


if __name__ == "__main__":
    fig_jitter_distribution()
    fig_miss_vs_load()
    fig_fanout_tail()
    print("figs-math-latency-jitter done")
