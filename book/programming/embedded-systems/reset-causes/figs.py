# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Причини reset».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальний відтінок понад палітру svgkit (навмисні події — фіолетовий)
WILL = "#8a5fb0"   # навмисний перезапуск / свідомий шлях


# ── reset-overview: кілька джерел → спільна лінія RESET → засувка причини ──────
# Ідея: різні події (нормальні, симптоми біди, навмисні) сходяться на ОДНУ лінію
# скидання; ядро рестартує, а причину тримає засувка, яку прочитає прошивка.
def fig_reset_overview():
    W, H = 760, 470
    p = []

    # джерела зліва: (підпис, дрібний підпис, колір)
    srcs = [
        ("Power-on (POR)", "перше живлення — норма", NEG),
        ("Кнопка / пін EN", "зовнішнє скидання", NEG),
        ("Brownout (BOD)", "напруга просіла", POS),
        ("Watchdog", "програма зависла", POS),
        ("Panic / виняток", "крах коду", POS),
        ("esp_restart()", "навмисний перезапуск", FIELD),
        ("Вихід із deep-sleep", "прокидання зі сну", FIELD),
    ]
    bx, bw, bh = 36, 226, 40
    gap = 16
    top = 64
    busx = bx + bw + 90
    centers = []
    for i, (lab, sub, col) in enumerate(srcs):
        y = top + i * (bh + gap)
        cy = y + bh / 2
        fill = "#eaf0fd" if col == NEG else ("#fdecea" if col == POS else "#eef7f0")
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=1.6))
        p.append(text(bx + 12, cy - 3, lab, size=12, color=col, anchor="start", bold=True))
        p.append(text(bx + 12, cy + 12, sub, size=9.5, color=MUTED, anchor="start"))
        p.append(line(bx + bw, cy, busx, cy, color=col, sw=1.8))
        centers.append(cy)

    # спільна лінія RESET
    y0, y1 = centers[0], centers[-1]
    p.append(line(busx, y0 - 14, busx, y1 + 14, color=INK, sw=4))
    p.append(text(busx, y0 - 22, "лінія RESET", size=11.5, color=INK, bold=True))

    # праворуч — два наслідки
    rx, rw = busx + 60, 244
    # наслідок 1: ядро рестартує
    ry1, rh1 = 96, 92
    p.append(rect(rx, ry1, rw, rh1, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(rx + rw / 2, ry1 + 24, "Ядро рестартує", size=13, color=POS, bold=True))
    for k, ln in enumerate(["PC → вектор скидання",
                            "регістри — у стан за умовчанням",
                            "виконання з початку програми"]):
        p.append(text(rx + rw / 2, ry1 + 44 + k * 15, ln, size=9.5, color=MUTED))
    p.append(line(busx, ry1 + rh1 / 2, rx, ry1 + rh1 / 2, color=INK, sw=2.2))

    # наслідок 2: засувка причини
    ry2, rh2 = 232, 96
    p.append(rect(rx, ry2, rw, rh2, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    p.append(text(rx + rw / 2, ry2 + 24, "Регістр причини (засувка)", size=12.5, color=NEG, bold=True))
    for k, ln in enumerate(["зберігає, ХТО викликав скидання",
                            "переживає сам reset",
                            "прошивка читає esp_reset_reason()"]):
        p.append(text(rx + rw / 2, ry2 + 44 + k * 15, ln, size=9.5, color=MUTED))
    p.append(line(busx, ry2 + rh2 / 2, rx, ry2 + rh2 / 2, color=INK, sw=2.2))

    # підсумкова рамка
    ry3, rh3 = 372, 70
    p.append(rect(rx, ry3, rw, rh3, fill="#fff6e0", stroke="#caa24a", sw=1.5, rx=10))
    p.append(mtext(rx + rw / 2, ry3 + 26,
                   ["Майже кожна причина, крім POR", "і навмисного перезапуску, —"],
                   size=11, color=INK))
    p.append(text(rx + rw / 2, ry3 + 58, "симптом, який варто залогувати.", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "reset-overview.svg"), W, H, *p,
           title="Звідки береться reset і як чіп запам'ятовує причину")


# ── por: power-on reset у часі ────────────────────────────────────────────────
# Ідея: поки Vdd нижча за поріг — логіка невизначена, RESET утримується; коли
# напруга стала + минула затримка на такт — reset відпускають, старт програми.
def fig_por():
    W, H = 720, 340
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 12, oy - ah - 2, "Vdd", size=12, color=INK, bold=True, anchor="end"))

    # поріг надійної роботи
    thr_y = oy - ah * 0.62
    p.append(line(ox, thr_y, ox + aw, thr_y, color=MUTED, sw=1.3, dash="6 4"))
    p.append(text(ox + aw + 2, thr_y + 4, "поріг", size=10, color=MUTED, anchor="start"))

    # момент, коли Vdd перетинає поріг і стає
    span = 10.0
    sx = aw / span
    t_cross = 3.4
    x_cross = ox + t_cross * sx
    t_release = 4.6                 # + затримка на стабілізацію такту
    x_release = ox + t_release * sx

    # «червона зона»: логіка невизначена (Vdd < поріг)
    p.append(rect(ox, oy - ah, x_cross - ox, ah, fill="#fbecec", stroke="none", sw=0, rx=0))
    p.append(text((ox + x_cross) / 2, oy - ah + 16, "логіка невизначена", size=10, color=POS, bold=True))
    p.append(text((ox + x_cross) / 2, oy - ah + 32, "Flash не читається", size=9.5, color=POS))

    # крива наростання Vdd (RC-подібна)
    pts = []
    vmax = ah * 0.9
    for i in range(0, 301):
        t = span * i / 300.0
        v = vmax * (1 - math.exp(-1.4 * t))
        pts.append("%.1f,%.1f" % (ox + t * sx, oy - v))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    # лінія RESET (активна = високо, поки не відпустять)
    rly = oy - ah - 0   # окрема смужка під віссю? — кладемо вгорі праворуч як стан
    # стан RESET малюємо як цифрову лінію над графіком
    top = oy - ah - 0
    relh = oy - 18
    # «утримується» до x_release, тоді падає
    p.append(line(ox, oy - 8, x_release, oy - 8, color=POS, sw=3))
    p.append(line(x_release, oy - 8, x_release, oy - 8, color=POS, sw=3))
    p.append(line(x_release, oy - 8, ox + aw, oy - 8, color=FIELD, sw=3, dash="2 4"))
    p.append(text(ox + 6, oy - 14, "RESET утримується", size=10, color=POS, anchor="start", bold=True))

    # вертикалі-маркери
    p.append(line(x_cross, oy, x_cross, thr_y, color=MUTED, sw=1, dash="3 3"))
    p.append(line(x_release, oy, x_release, oy - ah, color=FIELD, sw=1.4, dash="4 3"))
    p.append(text(x_release, oy - ah - 4, "reset відпущено →", size=10, color=FIELD, bold=True))
    p.append(text(x_release + 6, oy - ah * 0.30, "старт програми", size=10.5, color=FIELD, anchor="start", bold=True))

    # затримка між «Vdd стала» і «reset відпущено»
    p.append(line(x_cross, oy - ah - 18, x_release, oy - ah - 18, color=MUTED, sw=1.2))
    p.append(text((x_cross + x_release) / 2, oy - ah - 22, "затримка на такт", size=9, color=MUTED))

    render(os.path.join(IMG, "por.svg"), W, H, *p,
           title="Power-on reset: чіп тримають у скиданні, поки живлення не стане надійним")


# ── brownout-dip: глибокий провал б'є reset, дрібний — ні ──────────────────────
# Ідея: BOD безперервно звіряє Vdd з порогом; провал нижче порога → чисте
# скидання; провал, що лишився вище, система переживає.
def fig_brownout_dip():
    W, H = 720, 320
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []

    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 12, oy - ah - 2, "Vdd", size=12, color=INK, bold=True, anchor="end"))

    thr_y = oy - ah * 0.5
    p.append(line(ox, thr_y, ox + aw, thr_y, color=POS, sw=1.4, dash="6 4"))
    p.append(text(ox + aw + 2, thr_y + 4, "поріг BOD", size=10, color=POS, anchor="start"))

    span = 10.0
    sx = aw / span
    nom = ah * 0.78               # номінальна Vdd над віссю

    # будуємо криву Vdd з двома провалами:
    #  - перший (t≈3) глибокий — нижче порога
    #  - другий (t≈7) дрібний — лишається вище порога
    def dip(t, t0, depth, wid):
        return depth * math.exp(-((t - t0) ** 2) / (2 * wid * wid))

    pts = []
    deep_t, deep_d = 3.0, ah * 0.55
    small_t, small_d = 7.0, ah * 0.20
    for i in range(0, 401):
        t = span * i / 400.0
        v = nom - dip(t, deep_t, deep_d, 0.22) - dip(t, small_t, small_d, 0.30)
        pts.append("%.1f,%.1f" % (ox + t * sx, oy - max(v, 6)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    # перший провал → reset
    x1 = ox + deep_t * sx
    p.append(line(x1, oy, x1, oy - ah, color=POS, sw=1.2, dash="3 3"))
    p.append(text(x1, oy - ah - 4, "провал нижче порога", size=9.5, color=POS, bold=True))
    p.append(text(x1, oy - ah + 12, "→ BOD б'є RESET", size=9.5, color=POS))
    # значок-блискавка скидання
    p.append(text(x1, oy - ah * 0.18, "RESET", size=10, color=POS, bold=True))

    # другий провал → пережили
    x2 = ox + small_t * sx
    p.append(text(x2, oy - ah * 0.95, "дрібний провал", size=9.5, color=FIELD, bold=True))
    p.append(text(x2, oy - ah * 0.95 + 14, "вище порога → працюємо далі", size=9, color=FIELD))

    render(os.path.join(IMG, "brownout-dip.svg"), W, H, *p,
           title="Brownout під час роботи: глибокий провал викликає скидання, дрібний — ні")


# ── watchdog: здорова програма годує лічильник, зависла — ні ───────────────────
# Ідея: два сценарії на одній шкалі часу. Угорі — регулярні «feed» скидають
# лічильник, межа недосяжна. Унизу — після кількох годувань програма зависла,
# лічильник безперешкодно доповзає до межі й б'є RESET.
def fig_watchdog():
    W, H = 720, 360
    ox = 70
    aw = 600
    span = 10.0
    sx = aw / span
    p = []

    def ramp(oy, ah, feeds, label, col):
        # вісь
        p.append(arrow(ox, oy, ox, oy - ah - 6, color=INK, sw=1.4))
        p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.4))
        # межа
        lim_y = oy - ah * 0.9
        p.append(line(ox, lim_y, ox + aw, lim_y, color=POS, sw=1.2, dash="6 4"))
        p.append(text(ox + aw + 2, lim_y + 4, "межа", size=9.5, color=POS, anchor="start"))
        # пилка лічильника: росте, на кожному feed падає в нуль
        slope = ah * 0.9 / 2.4     # за 2.4 c дійшов би до межі
        pts = ["%.1f,%.1f" % (ox, oy)]
        last_t = 0.0
        for ft in feeds:
            # від last_t до ft росте
            v = slope * (ft - last_t)
            pts.append("%.1f,%.1f" % (ox + ft * sx, oy - min(v, ah * 0.9)))
            if ft < feeds[-1] + 0.001:
                pts.append("%.1f,%.1f" % (ox + ft * sx, oy))  # feed → нуль
            last_t = ft
        return pts, slope, lim_y

    # ── верх: здорова ──
    oy1, ah1 = 150, 110
    feeds_ok = [1.4, 2.6, 3.8, 5.0, 6.2, 7.4, 8.6]
    pts1, slope1, lim1 = ramp(oy1, ah1, feeds_ok, "здорова", FIELD)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts1), FIELD))
    for ft in feeds_ok:
        p.append(text(ox + ft * sx, oy1 + 15, "feed", size=9, color=FIELD))
    p.append(text(ox + 6, oy1 - ah1 - 0, "Здорова програма: годує вчасно → межа недосяжна",
                  size=11, color=FIELD, anchor="start", bold=True))

    # ── низ: зависла ──
    oy2, ah2 = 320, 110
    feeds_hang = [1.4, 2.6, 3.8]       # далі завмерло
    # ручна пилка: три годування, потім безперервне зростання до межі
    slope2 = ah2 * 0.9 / 2.4
    p.append(arrow(ox, oy2, ox, oy2 - ah2 - 6, color=INK, sw=1.4))
    p.append(arrow(ox, oy2, ox + aw, oy2, color=INK, sw=1.4))
    lim2 = oy2 - ah2 * 0.9
    p.append(line(ox, lim2, ox + aw, lim2, color=POS, sw=1.2, dash="6 4"))
    p.append(text(ox + aw + 2, lim2 + 4, "межа", size=9.5, color=POS, anchor="start"))
    pts2 = ["%.1f,%.1f" % (ox, oy2)]
    last_t = 0.0
    for ft in feeds_hang:
        v = slope2 * (ft - last_t)
        pts2.append("%.1f,%.1f" % (ox + ft * sx, oy2 - min(v, ah2 * 0.9)))
        pts2.append("%.1f,%.1f" % (ox + ft * sx, oy2))
        p.append(text(ox + ft * sx, oy2 + 15, "feed", size=9, color=NEG))
        last_t = ft
    # зростання до межі після зависання
    t_hit = last_t + 2.4
    x_hit = ox + t_hit * sx
    pts2.append("%.1f,%.1f" % (x_hit, lim2))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts2), NEG))
    p.append(line(x_hit, lim2, x_hit, oy2, color=POS, sw=1.2, dash="3 3"))
    p.append(text(x_hit + 4, lim2 - 6, "межа досягнута → RESET", size=10, color=POS, anchor="start", bold=True))
    p.append(text(ox + (last_t + 0.4) * sx, oy2 - ah2 * 0.5, "завмерло —", size=9.5, color=NEG, anchor="start"))
    p.append(text(ox + (last_t + 0.4) * sx, oy2 - ah2 * 0.5 + 13, "годувань нема", size=9.5, color=NEG, anchor="start"))
    p.append(text(ox + 6, oy2 - ah2 - 0, "Зависла програма: годувати перестала → лічильник б'є RESET",
                  size=11, color=NEG, anchor="start", bold=True))

    render(os.path.join(IMG, "watchdog.svg"), W, H, *p,
           title="Сторожовий таймер: здорова програма годує вчасно, зависла — ні")


# ── deepsleep-wake: холодний старт проти прокидання зі сну ─────────────────────
# Ідея: дві дороги до setup() сходяться на ОДНУ точку входу (вектор скидання),
# але стан пам'яті різний: холодний старт — RAM порожня, повна ініціалізація;
# прокидання — жива RTC-пам'ять дає пропустити важку ініціалізацію.
def fig_deepsleep_wake():
    W, H = 740, 320
    p = []
    cx = W / 2

    # дві колонки джерел
    lx, rx = 180, 560
    topy = 70
    bw, bh = 230, 56
    # ліворуч — холодний старт
    p.append(rect(lx - bw / 2, topy, bw, bh, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    p.append(text(lx, topy + 22, "Холодний старт", size=12.5, color=NEG, bold=True))
    p.append(text(lx, topy + 40, "причина POWERON", size=10, color=MUTED))
    # праворуч — прокидання
    p.append(rect(rx - bw / 2, topy, bw, bh, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(rx, topy + 22, "Прокидання зі сну", size=12.5, color=FIELD, bold=True))
    p.append(text(rx, topy + 40, "причина DEEPSLEEP", size=10, color=MUTED))

    # спільна точка входу
    ey, ew, eh = 168, 280, 50
    p.append(rect(cx - ew / 2, ey, ew, eh, fill="#fff6e0", stroke="#caa24a", sw=1.8, rx=8))
    p.append(text(cx, ey + 21, "та сама точка входу", size=12, color=INK, bold=True))
    p.append(text(cx, ey + 39, "вектор скидання → setup()", size=10.5, color=MUTED))

    # стрілки джерел до точки входу
    p.append(line(lx, topy + bh, cx - ew / 2 + 40, ey, color=NEG, sw=2))
    p.append(line(rx, topy + bh, cx + ew / 2 - 40, ey, color=FIELD, sw=2))

    # наслідки під точкою входу
    by = 252
    p.append(rect(lx - bw / 2, by, bw, 52, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=8))
    p.append(text(lx, by + 20, "RAM порожня", size=11, color=NEG, bold=True))
    p.append(text(lx, by + 38, "повна ініціалізація", size=9.5, color=MUTED))
    p.append(rect(rx - bw / 2, by, bw, 52, fill="#eef7f0", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(rx, by + 20, "жива RTC-пам'ять", size=11, color=FIELD, bold=True))
    p.append(text(rx, by + 38, "пропустити важку ініціалізацію", size=9.5, color=MUTED))

    p.append(line(cx - ew / 2 + 40, ey + eh, lx, by, color=NEG, sw=1.6))
    p.append(line(cx + ew / 2 - 40, ey + eh, rx, by, color=FIELD, sw=1.6))

    render(os.path.join(IMG, "deepsleep-wake.svg"), W, H, *p,
           title="Дві дороги до setup(): спільний вектор, різний стан пам'яті")


# ── reason-register: засувка → esp_reset_reason() → switch ────────────────────
# Ідея: причину фіксує засувка (переживає reset); прошивка читає її одним
# викликом і гілкується switch'ем — невидима причина стає конкретною дією.
def fig_reason_register():
    W, H = 720, 360
    p = []

    # верхній потік: засувка → виклик → switch
    y = 70
    bh = 56
    boxes = [
        ("Засувка причини", "переживає reset", NEG, "#eaf0fd"),
        ("esp_reset_reason()", "читаємо рано в boot", INK, FILL),
        ("switch (причина)", "гілка на кожен випадок", FIELD, "#eef7f0"),
    ]
    bw = 196
    xs = [40, 40 + bw + 46, 40 + 2 * (bw + 46)]
    for (lab, sub, col, fill), x in zip(boxes, xs):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(x + bw / 2, y + 23, lab, size=12, color=col, bold=True))
        p.append(text(x + bw / 2, y + 41, sub, size=9.5, color=MUTED))
    p.append(arrow(xs[0] + bw, y + bh / 2, xs[1] - 2, y + bh / 2, color=INK, sw=1.8))
    p.append(arrow(xs[1] + bw, y + bh / 2, xs[2] - 2, y + bh / 2, color=INK, sw=1.8))

    # таблиця значень і реакцій
    ty = 168
    rows = [
        ("ESP_RST_POWERON", "увімкнули живлення", "нова сесія", NEG),
        ("ESP_RST_BROWNOUT", "просіла напруга", "лічи, захистись", POS),
        ("ESP_RST_TASK_WDT", "задача зависла", "шукай блокування", POS),
        ("ESP_RST_PANIC", "виняток у коді", "дивись backtrace", POS),
        ("ESP_RST_SW", "esp_restart()", "так і задумано", FIELD),
        ("ESP_RST_DEEPSLEEP", "прокинулись зі сну", "віднови контекст", FIELD),
    ]
    cols_x = [60, 270, 470]
    rh = 26
    p.append(text(cols_x[0], ty - 6, "значення", size=10, color=INK, anchor="start", bold=True))
    p.append(text(cols_x[1], ty - 6, "що сталося", size=10, color=INK, anchor="start", bold=True))
    p.append(text(cols_x[2], ty - 6, "типова реакція", size=10, color=INK, anchor="start", bold=True))
    p.append(line(50, ty + 2, W - 40, ty + 2, color=MUTED, sw=1))
    for i, (val, what, act, col) in enumerate(rows):
        ry = ty + 8 + i * rh
        if i % 2 == 1:
            p.append(rect(50, ry - 4, W - 90, rh, fill="#f4f6f8", stroke="none", sw=0, rx=0))
        p.append(text(cols_x[0], ry + 12, val, size=10.5, color=col, anchor="start", bold=True))
        p.append(text(cols_x[1], ry + 12, what, size=10, color=INK, anchor="start"))
        p.append(text(cols_x[2], ry + 12, act, size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "reason-register.svg"), W, H, *p,
           title="Один виклик перетворює невидиму причину на конкретну дію")


# ── triage: причина reset веде прямо до джерела й способу полагодити ───────────
# Ідея: від кореня «читаємо причину» — чотири найчастіші гілки несподіваного
# перезапуску, кожна з типовим джерелом і конкретною дією.
def fig_triage():
    W, H = 760, 340
    p = []
    cx = W / 2

    # корінь
    rw, rh = 280, 50
    rx, ry = cx - rw / 2, 40
    p.append(rect(rx, ry, rw, rh, fill="#fff6e0", stroke="#caa24a", sw=1.8, rx=8))
    p.append(text(cx, ry + 22, "Несподіваний перезапуск:", size=12.5, color=INK, bold=True))
    p.append(text(cx, ry + 39, "читаємо причину reset", size=11, color=MUTED))

    # чотири гілки
    branches = [
        ("BROWNOUT", "слабке живлення", "конденсатор, кабель", POS),
        ("TASK_WDT", "задача блокується", "шукай де застрягло", POS),
        ("PANIC", "справжній баг", "розгорни backtrace", POS),
        ("POWERON?", "контакт чи брязкіт EN", "перевір живлення/пін", NEG),
    ]
    bw, bh = 168, 78
    gap = (W - 40 - 4 * bw) / 3
    by = 180
    for i, (val, src, act, col) in enumerate(branches):
        bx = 20 + i * (bw + gap)
        fill = "#fdecea" if col == POS else "#eaf0fd"
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(bx + bw / 2, by + 20, val, size=12, color=col, bold=True))
        p.append(text(bx + bw / 2, by + 40, src, size=9.8, color=INK))
        p.append(text(bx + bw / 2, by + 58, "→ " + act, size=9.5, color=MUTED))
        # лінія від кореня
        p.append(line(cx, ry + rh, bx + bw / 2, by, color=col, sw=1.5))

    p.append(text(cx, H - 18, "причина звужує пошук від «усього коду й заліза» до однієї ділянки",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "triage.svg"), W, H, *p,
           title="Триаж несподіваного перезапуску: причина веде прямо до джерела")


# ── glitch-zone (вставка comp-brownout): три зони напруги ──────────────────────
# Ідея: між надійною роботою і чесним нулем є СІРА ЗОНА, де логіка ще жива, але
# робить дурниці. Завдання детектора — скинути чіп чисто ДО входу в неї.
def fig_glitch_zone():
    W, H = 740, 380
    p = []
    L, R = 70.0, 670.0
    y_ok = 70.0       # верх «надійно»
    y_bod = 196.0     # поріг BOD
    y_off = 274.0     # верх «мертво»
    y_bot = 320.0     # дно

    # три смуги
    p.append(rect(L, y_ok, R - L, y_bod - y_ok, fill="#eef7f0", stroke="none", sw=0, rx=0))
    p.append(rect(L, y_bod, R - L, y_off - y_bod, fill="#fbeede", stroke="none", sw=0, rx=0))
    p.append(rect(L, y_off, R - L, y_bot - y_off, fill="#e3e3e3", stroke="none", sw=0, rx=0))

    # рамка довкола шкали
    p.append(rect(L, y_ok, R - L, y_bot - y_ok, fill="none", stroke=MUTED, sw=1.2, rx=0))

    # поріг BOD
    p.append(line(L, y_bod, R, y_bod, color=POS, sw=1.8, dash="7 4"))
    p.append(text(R + 4, y_bod + 4, "поріг BOD", size=10.5, color=POS, anchor="start", bold=True))

    # підписи зон
    cx = (L + R) / 2
    p.append(text(cx, (y_ok + y_bod) / 2 - 6, "Надійна робота", size=13, color=FIELD, bold=True))
    p.append(text(cx, (y_ok + y_bod) / 2 + 12, "рівні «0» і «1» чіткі, Flash читається", size=10, color=MUTED))
    p.append(text(cx, (y_bod + y_off) / 2 - 4, "СІРА ЗОНА: логіка жива, але хибна", size=12.5, color=POS, bold=True))
    p.append(text(cx, (y_bod + y_off) / 2 + 13, "зависання шин, биті біти, напівінструкції", size=9.5, color=POS))
    p.append(text(cx, (y_off + y_bot) / 2 + 4, "Чіп мертвий — і це чесно", size=11.5, color=MUTED, bold=True))

    # вісь напруги
    p.append(arrow(L - 16, y_bot, L - 16, y_ok, color=INK, sw=1.4))
    p.append(text(L - 22, y_ok - 6, "Vdd", size=11, color=INK, anchor="end", bold=True))

    p.append(text(W / 2, H - 20, "Завдання детектора — скинути чіп чисто ДО входу в сіру зону",
                  size=11, color=INK, italic=True))

    render(os.path.join(IMG, "glitch-zone.svg"), W, H, *p,
           title="Три зони напруги: «сіра зона» гірша за чесний нуль")


# ── decoupling (вставка comp-brownout): без / з накопичувальним C ──────────────
# Ідея: той самий кидок струму. Без розв'язки Vdd провалюється нижче порога →
# скидання; з локальними й накопичувальним C заряд віддається миттєво — тримається.
def fig_decoupling():
    W, H = 740, 320
    ox, oy = 70, 250
    aw, ah = 600, 196
    p = []

    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 12, oy - ah - 2, "Vdd", size=12, color=INK, bold=True, anchor="end"))

    thr_y = oy - ah * 0.46
    p.append(line(ox, thr_y, ox + aw, thr_y, color=POS, sw=1.4, dash="6 4"))
    p.append(text(ox + aw + 2, thr_y + 4, "поріг BOD", size=10, color=POS, anchor="start"))

    span = 10.0
    sx = aw / span
    nom = ah * 0.78
    burst_t = 5.0

    def dip(t, depth, wid):
        return depth * math.exp(-((t - burst_t) ** 2) / (2 * wid * wid))

    # без C — глибокий провал нижче порога
    pts_no = []
    for i in range(0, 401):
        t = span * i / 400.0
        v = nom - dip(t, ah * 0.55, 0.30)
        pts_no.append("%.1f,%.1f" % (ox + t * sx, oy - max(v, 6)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts_no), POS))

    # з C — дрібний провал, лишається вище порога
    pts_c = []
    for i in range(0, 401):
        t = span * i / 400.0
        v = nom - dip(t, ah * 0.18, 0.34)
        pts_c.append("%.1f,%.1f" % (ox + t * sx, oy - v))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join(pts_c), FIELD))

    # позначка кидка струму
    xb = ox + burst_t * sx
    p.append(line(xb, oy, xb, oy - ah, color=MUTED, sw=1, dash="3 3"))
    p.append(text(xb, oy - ah - 4, "кидок струму (Wi-Fi / мотор)", size=10, color=MUTED))

    # легенда
    p.append(line(ox + 20, oy - ah + 8, ox + 46, oy - ah + 8, color=POS, sw=2.4))
    p.append(text(ox + 52, oy - ah + 12, "без накопичувального C → провал нижче порога → RESET",
                  size=10.5, color=POS, anchor="start", bold=True))
    p.append(line(ox + 20, oy - ah + 28, ox + 46, oy - ah + 28, color=FIELD, sw=2.6))
    p.append(text(ox + 52, oy - ah + 32, "з локальними + накопичувальним C → тримається",
                  size=10.5, color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, "decoupling.svg"), W, H, *p,
           title="Той самий кидок струму: розв'язка не дає Vdd просісти нижче порога")


if __name__ == "__main__":
    fig_reset_overview()
    fig_por()
    fig_brownout_dip()
    fig_watchdog()
    fig_deepsleep_wake()
    fig_reason_register()
    fig_triage()
    fig_glitch_zone()
    fig_decoupling()
    print("OK: figures written to", IMG)
