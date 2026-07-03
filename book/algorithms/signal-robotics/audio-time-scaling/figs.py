# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── resample-vs-tsm: чому просте прискорення підіймає тон, а нам треба інакше ──
# Ідея: угорі вихідна хвиля; ліворуч унизу — та сама хвиля «стиснута» (швидше →
# період коротший → тон вищий); праворуч — правильна зміна темпу: період той
# самий, змінилася лише кількість періодів у часі.
def fig_resample_vs_tsm():
    W, H = 720, 330
    p = []

    def wave(x0, x1, y, period_px, amp, color, sw=2.2):
        pts = []
        n = int((x1 - x0))
        for i in range(n + 1):
            x = x0 + i
            v = math.sin(2 * math.pi * (x - x0) / period_px)
            pts.append("%.1f,%.1f" % (x, y - v * amp))
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="%.1f" stroke-linejoin="round"/>' % (" ".join(pts), color, sw))

    # оригінал
    p.append(text(W / 2, 30, "Оригінал: період T, тривалість L", size=13, color=INK, bold=True))
    p.append(wave(70, 650, 74, 46, 26, INK))
    p.append(line(70, 108, 650, 108, color=MUTED, sw=1))

    # ліво: наївне прискорення
    lx0, lx1, ly = 70, 360, 210
    p.append(wave(lx0, lx1, ly, 30, 26, POS))
    p.append(line(lx0, ly + 40, lx1, ly + 40, color=MUTED, sw=1))
    b1, w1, h1 = textbox((lx0 + lx1) / 2, 268, "швидше → період коротший → ТОН ВИЩИЙ ✗",
                         size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.6, pad=9)
    p.append(b1)
    p.append(text((lx0 + lx1) / 2, 300, "просте прискорення (resample)", size=10, color=POS))

    # право: правильна зміна темпу
    rx0, rx1, ry = 400, 650, 210
    p.append(wave(rx0, rx1, ry, 46, 26, FIELD))
    p.append(line(rx0, ry + 40, rx1, ry + 40, color=MUTED, sw=1))
    b2, w2, h2 = textbox((rx0 + rx1) / 2, 268, "той самий період → ТОН ТОЙ САМИЙ ✓",
                         size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6, pad=9)
    p.append(b2)
    p.append(text((rx0 + rx1) / 2, 300, "зміна темпу (time-scaling)", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "resample-vs-tsm.svg"), W, H, *p,
           title="Дві дороги «зробити коротше»: одна псує тон, друга — ні")


# ── ola: розрізати на вікна, зсунути щільніше/рідше, зшити перекриттям ─────────
# Ідея: смуга «аналіз» — вікна беруть із входу з кроком Ha; смуга «синтез» — ті
# самі вікна кладуть у вихід з кроком Hs; Hs<Ha → коротше (швидше), Hs>Ha →
# довше. Перекриття зшивають плавним переходом.
def fig_ola():
    W, H = 720, 340
    p = []
    winw = 120

    def grain(x, y, color, fill):
        # трапеція-вікно з «горбиком» усередині — символ віконного зерна
        pts = "%d,%d %d,%d %d,%d %d,%d" % (x, y, x + 18, y - 30, x + winw - 18, y - 30, x + winw, y)
        s = '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (pts, fill, color)
        return s

    # аналіз: вхід
    ay = 120
    p.append(text(70, 60, "Аналіз: беремо вікна з входу, крок Hₐ", size=12, color=INK, bold=True, anchor="start"))
    p.append(line(70, ay, 650, ay, color=INK, sw=1.6))
    Ha = 150
    for k, x in enumerate([80, 80 + Ha, 80 + 2 * Ha]):
        p.append(grain(x, ay, NEG, "#e9eefb"))
        p.append(text(x + winw / 2, ay + 18, "вікно %d" % (k + 1), size=9, color=NEG))
    # позначка кроку Ha
    p.append(line(80 + winw / 2, ay - 40, 80 + Ha + winw / 2, ay - 40, color=MUTED, sw=1.2))
    p.append(text(80 + Ha / 2 + winw / 2, ay - 46, "Hₐ", size=12, color=MUTED, italic=True))

    # синтез: вихід (щільніше — швидше)
    sy = 250
    p.append(text(70, 200, "Синтез: кладемо ті самі вікна, крок Hₛ < Hₐ → коротше", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(line(70, sy, 520, sy, color=INK, sw=1.6))
    Hs = 92
    for k, x in enumerate([80, 80 + Hs, 80 + 2 * Hs]):
        p.append(grain(x, sy, FIELD, "#eafaf0"))
    p.append(line(80 + winw / 2, sy + 24, 80 + Hs + winw / 2, sy + 24, color=POS, sw=1.4))
    p.append(text(80 + Hs / 2 + winw / 2, sy + 38, "Hₛ", size=12, color=POS, italic=True, bold=True))
    p.append(text(560, sy, "перекриття → плавний перехід", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "ola.svg"), W, H, *p,
           title="Overlap-add: та сама кількість вікон, інший крок укладання")


# ── seam: наївний стик рве фазу (тріск), зсув до збігу хвиль зшиває чисто ──────
# Ідея: два фрагменти хвилі; ліворуч склеєні «в лоб» — на стику злам (стрибок
# фази) → тріск; праворуч другий фрагмент зсунули так, що хвилі збіглися → гладко.
def fig_seam():
    W, H = 720, 300
    p = []

    def frag(x0, phase, y, color, n=150, period=42, amp=24, sw=2.4):
        pts = []
        for i in range(n + 1):
            x = x0 + i
            v = math.sin(2 * math.pi * i / period + phase)
            pts.append("%.1f,%.1f" % (x, y - v * amp))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round"/>' % (" ".join(pts), color, sw))

    # ЛІВО: стик у лоб — розрив фази
    lx, ly = 60, 110
    p.append(text(lx + 150, 58, "Стик «у лоб»", size=12, color=POS, bold=True))
    p.append(frag(lx, 0.0, ly, INK))
    p.append(frag(lx + 150, 2.4, ly, POS))          # інша фаза → злам
    p.append(line(lx + 150, ly - 40, lx + 150, ly + 40, color=POS, sw=1.4, dash="4 3"))
    p.append(text(lx + 150, ly + 60, "злам фази → тріск", size=10, color=POS, bold=True))

    # ПРАВО: зсув до збігу
    rx, ry = 400, 110
    p.append(text(rx + 150, 58, "Зсув до збігу хвиль (WSOLA)", size=12, color=FIELD, bold=True))
    p.append(frag(rx, 0.0, ry, INK))
    p.append(frag(rx + 150, 0.0, ry, FIELD))        # та сама фаза → гладко
    p.append(line(rx + 150, ry - 40, rx + 150, ry + 40, color=FIELD, sw=1.2, dash="4 3"))
    p.append(text(rx + 150, ry + 60, "хвилі збіглися → гладко", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "seam.svg"), W, H, *p,
           title="Секрет якості: зсунути точку склейки туди, де хвилі збігаються")


# ── search: пошук зсуву за схожістю — ковзаємо шаблоном, шукаємо max кореляції ─
# Ідея: «хвіст» уже викладеного виходу — шаблон; у вхідному сигналі скануємо
# вікно-кандидат навколо ідеального місця й беремо зсув δ із найбільшим збігом.
def fig_search():
    W, H = 720, 300
    p = []

    # шаблон (хвіст виходу)
    ty = 90
    p.append(text(60, 50, "Шаблон: хвіст уже викладеного виходу", size=11, color=NEG, bold=True, anchor="start"))
    pts = []
    for i in range(120):
        v = math.sin(2 * math.pi * i / 34)
        pts.append("%.1f,%.1f" % (70 + i, ty - v * 20))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), NEG))
    p.append(rect(66, ty - 30, 128, 60, fill="none", stroke=NEG, sw=1.4, rx=4))

    # вхід з вікном пошуку
    iy = 210
    p.append(text(60, 165, "Вхід: ковзаємо кандидатом у вікні ±Δ навколо ідеалу", size=11, color=INK, bold=True, anchor="start"))
    pts = []
    for i in range(560):
        v = math.sin(2 * math.pi * i / 34 + 0.4)
        pts.append("%.1f,%.1f" % (70 + i, iy - v * 20))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts), MUTED))

    # ідеальне місце + вікно пошуку
    ideal = 330
    p.append(line(ideal, iy - 46, ideal, iy + 46, color=INK, sw=1.4, dash="5 4"))
    p.append(text(ideal, iy + 62, "ідеал", size=10, color=INK))
    p.append(rect(ideal - 70, iy - 34, 140, 68, fill="none", stroke=POS, sw=1.3, rx=4, ))
    p.append(line(ideal - 70, iy + 46, ideal + 70, iy + 46, color=POS, sw=1.2))
    p.append(text(ideal, iy - 44, "вікно пошуку ±Δ", size=10, color=POS, bold=True))

    # найкращий кандидат (зелений)
    best = ideal + 28
    pts = []
    for i in range(128):
        v = math.sin(2 * math.pi * i / 34)
        pts.append("%.1f,%.1f" % (best - 64 + i, iy - v * 20))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), FIELD))
    p.append(text(best, iy + 62, "найкращий збіг → зсув δ", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "search.svg"), W, H, *p,
           title="Як знаходять місце склейки: max схожості шаблона й кандидата")


# ── mul-overflow: чому int16×int16, накопичене в int32, переповнюється ─────────
# Ідея: смуга бітів. Один добуток двох 16-бітних відліків займає до 31 біта —
# ще влазить у int32. Але кореляція додає L таких добутків; сума росте на log2(L)
# бітів і вилітає за 32 — тому акумулятор мусить бути int64.
def fig_mul_overflow():
    W, H = 700, 340
    p = []
    x0 = 128
    px = 8.0            # px на біт; 64 біти → 512 px, кінець 640 < 700

    def bar(y, filled, color, fill, label, note):
        p.append(rect(x0, y, 64 * px, 26, fill=BG, stroke=MUTED, sw=1))
        p.append(rect(x0, y, filled * px, 26, fill=fill, stroke=color, sw=1.6))
        p.append(text(x0 - 10, y + 18, label, size=11, color=INK, bold=True, anchor="end"))
        # підпис усередині смуги праворуч від заповненого краю або над нею
        p.append(text(x0 + filled * px + 7, y + 18, note, size=10.5, color=color,
                      bold=True, anchor="start"))

    p.append(text(W / 2, 28, "Скільки бітів займає число на кожному кроці", size=16, bold=True))

    # орієнтири-межі
    for b, cap in [(16, "16"), (31, "31"), (32, "32"), (63, "63")]:
        xb = x0 + b * px
        p.append(line(xb, 58, xb, 292, color="#d0d5dd", sw=1, dash="3 4"))
        p.append(text(xb, 306, cap, size=9, color=MUTED))
    p.append(text(x0 + 32 * px + 2, 52, "межа int32", size=10, color=POS, bold=True, anchor="start"))

    bar(78,  16, NEG,   "#eaf0fd", "відлік", "16 біт")
    bar(118, 31, INK,   "#e9eefb", "×",       "≈31 біт: влазить у int32")
    bar(158, 41, POS,   "#fdecea", "+…",      "≈41 біт: ПЕРЕЛИВ int32")
    bar(198, 41, FIELD, "#eafaf0", "int64",   "41 біт: вільно")

    b, w, h = textbox(W / 2, 262,
                      "сума L≈1024 добутків додає ~log₂(1024)=10 бітів згори",
                      size=11, bold=True, fill=FILL, stroke=MUTED, sw=1.4, pad=9)
    p.append(b)

    render(os.path.join(OUT, "mul-overflow.svg"), W, H, *p, title=None)


# ── ring-oa: overlap-add у кільцевому буфері — куди наростає вихід ─────────────
# Ідея: кільце виходу; курсор запису кладе новий кадр, накладаючи його на вже
# наявний хвіст (зона перекриття = сума). Позаду курсора на Hs відліків вихід
# уже НІКОЛИ не зміниться — його можна віддавати (drain). Попереду — ще нулі.
def fig_ring_oa():
    W, H = 720, 360
    p = []
    cx, cy, R = 250, 190, 120

    import math as _m

    def pt(ang, r):
        a = _m.radians(ang - 90)  # 0° угорі, за годинниковою
        return cx + r * _m.cos(a), cy + r * _m.sin(a)

    def arcseg(a0, a1, r, color, sw, dash=None):
        x0, y0 = pt(a0, r); x1, y1 = pt(a1, r)
        large = 1 if (a1 - a0) % 360 > 180 else 0
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d 1 %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f"%s/>' % (x0, y0, r, r, large, x1, y1, color, sw, d))

    # кільце-основа
    p.append(circle(cx, cy, R, fill=BG, stroke=MUTED, sw=1.4))

    # зони (за годинниковою від верху):
    # готовий вихід (drain) 250..350, зона перекриття 350..40, попереду нулі 40..250
    p.append(arcseg(250, 350, R, FIELD, 9))                 # уже незмінний → віддаємо
    p.append(arcseg(350, 400, R, POS, 9))                   # зона накладання (350..40)
    p.append(arcseg(40, 250, R, "#c7cdd6", 7, dash="2 5"))  # попереду — ще нулі

    # курсор запису (де кладемо новий кадр) — на ~15°
    wx, wy = pt(15, R)
    p.append(line(cx, cy, wx, wy, color=INK, sw=1.6))
    p.append(circle(wx, wy, 6, fill=INK, stroke=INK))
    b, w, h = textbox(wx + 60, wy - 40, "курсор запису\n(+= новий кадр × вікно)",
                      size=10, bold=True, fill="#fff7f0", stroke=POS, sw=1.4, pad=7)
    p.append(b)

    # підписи зон
    lx, ly = pt(300, R + 6)
    b1, _, _ = textbox(lx - 8, ly + 46, "готово → віддати\n(на Hₛ позаду курсора)",
                       size=10, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.4, pad=7)
    p.append(b1)
    b2, _, _ = textbox(cx, cy - 4, "перекриття\n(додаємо)", size=10, bold=True,
                       fill="#fdecea", stroke=POS, sw=1.4, pad=7)
    p.append(b2)
    b3, _, _ = textbox(cx - 130, cy + 96, "попереду — нулі\n(ще не писали)", size=10,
                       fill=FILL, stroke=MUTED, sw=1.3, pad=7)
    p.append(b3)

    # права колонка — суть у трьох рядках
    rx = 470
    p.append(text(rx, 96, "Правило кільця:", size=13, color=INK, bold=True, anchor="start"))
    for i, s in enumerate([
        "• пишемо кадр += вікно·відлік",
        "  (накладаємо на хвіст)",
        "• курсор іде вперед на Hₛ",
        "• усе, що на Hₛ позаду —",
        "  уже не зміниться → drain",
        "• маска (& (N−1)) замикає",
        "  індекс у кільце, N = 2ᵏ",
    ]):
        p.append(text(rx, 122 + i * 24, s, size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "ring-oa.svg"), W, H, *p,
           title=None)


# ── hist-timeline: дві лінії — спектральна й часова; довга пауза до музики ─────
# Ідея: угорі спектральна лінія (Дадлі → Фленаган&Ґолден 1966 → Портнофф 1976 →
# музика 1978), унизу часова (SOLA 1985 → PSOLA 1990 → WSOLA 1993). Показати, що
# вокодер винайшли за десятиліття до того, як він знадобився для темпу, а
# швидкі часові методи прийшли пізніше й перемогли простотою.
def fig_hist_timeline():
    W, H = 760, 440
    p = []

    yr0, yr1 = 1935, 2000
    hx0, hx1 = 70, 700
    def xat(year):
        return hx0 + (hx1 - hx0) * (year - yr0) / (yr1 - yr0)

    # вісь років
    axy = 225
    p.append(line(hx0, axy, hx1, axy, color=INK, sw=1.6))
    for yr in (1940, 1950, 1960, 1970, 1980, 1990, 2000):
        xx = xat(yr)
        p.append(line(xx, axy - 4, xx, axy + 4, color=MUTED, sw=1))
        p.append(text(xx, axy + 20, str(yr), size=10, color=MUTED))

    def node(year, ytext, label, sub, color, up=True):
        xx = xat(year)
        b, w, h = textbox(xx, ytext, label, size=11, bold=True, fill=BG, stroke=color, sw=1.5, pad=7)
        edge = ytext + h / 2 if up else ytext - h / 2
        p.append(line(xx, axy, xx, edge, color=color, sw=1.2, dash="3 3"))
        p.append(circle(xx, axy, 4.5, fill=color, stroke=color, sw=1))
        p.append(b)
        p.append(text(xx, (ytext + h / 2 + 13) if up else (ytext - h / 2 - 6),
                      sub, size=9, color=MUTED))
        return xx

    # ── верх: спектральна лінія ──
    p.append(text(hx0, 44, "Спектральна лінія — з телефонії, не з музики", size=12,
                  color=NEG, bold=True, anchor="start"))
    node(1939, 86, "Вокодер Дадлі", "стиснути смугу", NEG)
    node(1966, 128, "Фазовий вокодер", "Фленаґан і Ґолден", NEG)
    node(1976, 86, "Портнофф: ШПФ", "робоча форма", NEG)
    node(1978, 165, "Музика (Мурер)", "аж тепер для темпу", FIELD)

    # дуга-пауза між 1966 і 1978
    px0, px1 = xat(1966), xat(1978)
    p.append('<path d="M %.1f %d Q %.1f %d %.1f %d" fill="none" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="5 4"/>'
             % (px0, 182, (px0 + px1) / 2, 208, px1, 182, MUTED))
    p.append(text((px0 + px1) / 2, 203, "≈ 12 років вокодер чекав", size=9.5,
                  color=MUTED, italic=True))

    # ── низ: часова лінія ──
    p.append(text(hx0, 420, "Часова лінія — простіша, швидша, для живої мови", size=12,
                  color=POS, bold=True, anchor="start"))
    node(1985, 300, "SOLA", "Рукос і Вілґус", POS, up=False)
    node(1990, 355, "PSOLA / TD-PSOLA", "Мулен і Шарпантьє", POS, up=False)
    node(1993, 300, "WSOLA", "Вергелст і Роландс", POS, up=False)

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Дві дороги до зміни темпу й довга пауза між винаходом і вжитком")


if __name__ == "__main__":
    fig_resample_vs_tsm()
    fig_ola()
    fig_seam()
    fig_search()
    fig_mul_overflow()
    fig_ring_oa()
    fig_hist_timeline()
    print("OK: figures written to", OUT)
