# -*- coding: utf-8 -*-
"""Фігури до теми «Бенчмаркінг на пристрої».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Розрив між «лабораторним» і «бортовим» FPS ────────────────────────────
def fig_gap():
    """Дві стовпчики: число з ноутбука/datasheet (велике) і реальне на борту
    (мале). Показує, чому цифру з паспорта не можна брати на віру — її треба
    переміряти на самому апараті, у його умовах."""
    W, H = 760, 380
    f = [text(W / 2, 30, "Чому міряємо на самому апараті, а не «на папері»", size=17, bold=True)]

    base = 300       # базова лінія стовпців
    ax_x = 120
    f.append(line(ax_x, base, W - 60, base, color=LINE, sw=1.4))
    f.append(text(ax_x - 8, base, "0", size=11, color=MUTED, anchor="end"))

    def bar(cx, val, top_lab, sub, col):
        # val у px висоти
        x = cx - 55
        f.append(rect(x, base - val, 110, val, fill=col, stroke=LINE, sw=1.4))
        f.append(text(cx, base - val - 10, top_lab, size=15, bold=True, color=col))
        f.append(text(cx, base + 20, sub, size=12))

    bar(250, 200, "60 FPS", "ноутбук / datasheet", FIELD)
    bar(530, 70, "9 FPS", "той самий код на борту", POS)

    f.append(text(W / 2, H - 22,
                  "слабший чіп, інша пам'ять, спека, живлення — цифра з паспорта на апараті НЕ повторюється",
                  size=12, color=INK))
    return render(os.path.join(IMG, "gap.svg"), W, H, *f)


# ── 2. Затримка проти пропускної здатності (конвеєр) ──────────────────────────
def fig_latency_throughput():
    """Конвеєр: кадр проходить захоплення → підготовку → модель → розбір.
    Затримка = повний час одного кадру наскрізь; пропускна здатність = скільки
    кадрів за секунду виходить, коли стадії працюють паралельно. Показує, що це
    РІЗНІ числа: можна мати високий FPS і велику затримку водночас."""
    W, H = 880, 380
    f = [text(W / 2, 30, "Затримка ≠ пропускна здатність", size=17, bold=True)]

    stages = ["захоплення", "підготовка", "модель", "розбір"]
    cols = [NEG, MUTED, POS, FIELD]
    x0, y0, bw, gap = 60, 110, 170, 20
    for i, (s, c) in enumerate(zip(stages, cols)):
        x = x0 + i * (bw + gap)
        f.append(rect(x, y0, bw, 56, fill=BG, stroke=c, sw=1.8))
        f.append(text(x + bw / 2, y0 + 34, s, size=13, bold=True, color=c))
        if i < 3:
            f.append(arrow(x + bw, y0 + 28, x + bw + gap, y0 + 28))

    # стрілка затримки — наскрізь
    ly = y0 + 92
    f.append(line(x0, ly, x0 + 4 * bw + 3 * gap, ly, color=INK, sw=2))
    f.append(arrow(x0, ly, x0 + 4 * bw + 3 * gap, ly, color=INK, sw=2))
    f.append(text(W / 2, ly + 22, "ЗАТРИМКА: повний шлях одного кадру наскрізь (напр. 110 мс)",
                  size=12, bold=True, color=INK))

    # пропускна — стадії працюють паралельно над різними кадрами
    py = ly + 64
    f.append(text(W / 2, py + 4,
                  "ПРОПУСКНА ЗДАТНІСТЬ: коли 4 стадії працюють над різними кадрами разом —",
                  size=12, bold=True, color=INK))
    f.append(text(W / 2, py + 24,
                  "кадри виходять частіше за повний прохід (напр. 25 FPS при затримці 110 мс)",
                  size=12, color=INK))

    f.append(text(W / 2, H - 16,
                  "для керування важить ЗАТРИМКА (як старе те, що ти бачиш), а не лише FPS",
                  size=12, color=POS, bold=True))
    return render(os.path.join(IMG, "latency-throughput.svg"), W, H, *f)


# ── 3. Розподіл затримок: середнє бреше, хвіст вирішує ───────────────────────
def fig_tail():
    """Гістограма часів одного й того ж виміру: купа коротких + довгий «хвіст»
    рідкісних повільних кадрів. Середнє лежить у купі, та p99 — далеко праворуч.
    Показує, чому для реального часу беруть перцентиль (p95/p99), а не середнє."""
    W, H = 820, 400
    f = [text(W / 2, 30, "Затримка — це розподіл, а не одне число", size=17, bold=True)]

    bx, by = 90, 300            # вісь
    bw = 640
    f.append(line(bx, by, bx + bw, by, color=LINE, sw=1.4))
    f.append(text(bx + bw, by + 20, "час одного кадру, мс →", size=12, color=MUTED, anchor="end"))

    # стовпчики-гістограма: висоти (умовні частоти)
    heights = [8, 30, 95, 150, 120, 70, 40, 22, 12, 8, 6, 5, 5, 6, 9, 16, 10, 4]
    n = len(heights)
    cw = bw / n
    for i, h in enumerate(heights):
        x = bx + i * cw
        # хвіст (далекі стовпці) — гарячим
        col = POS if i >= 14 else NEG
        f.append(rect(x + 2, by - h, cw - 4, h, fill=col, stroke="none", sw=0))

    # середнє — у купі
    mean_x = bx + 4 * cw + cw / 2
    f.append(line(mean_x, by, mean_x, by - 175, color=INK, sw=2, dash="5 4"))
    f.append(text(mean_x, by - 184, "середнє ≈ 28 мс", size=12, bold=True, color=INK))
    f.append(text(mean_x, by - 168, "(виглядає добре)", size=10, color=MUTED))

    # p99 — у хвості
    p99_x = bx + 15 * cw + cw / 2
    f.append(line(p99_x, by, p99_x, by - 130, color=POS, sw=2, dash="5 4"))
    f.append(text(p99_x + 4, by - 138, "p99 ≈ 90 мс", size=12, bold=True, color=POS, anchor="middle"))
    f.append(text(p99_x + 4, by - 122, "(саме він зриває дедлайн)", size=10, color=POS, anchor="middle"))

    f.append(text(W / 2, H - 18,
                  "рідкісний повільний кадр (хвіст) і провалює реальний час — тому беремо p95/p99, не середнє",
                  size=12, color=INK))
    return render(os.path.join(IMG, "tail.svg"), W, H, *f)


# ── 4. Прогрів і тепловий троттлінг у часі ───────────────────────────────────
def fig_thermal():
    """Крива FPS у часі під безперервним навантаженням: спершу повільний
    перший кадр (холодний старт), тоді стабільне плато, тоді — коли чіп
    нагрівся — провал (троттлінг). Показує, що один короткий замір бреше:
    треба тримати навантаження довго."""
    W, H = 840, 410
    f = [text(W / 2, 30, "Один короткий замір бреше: прогрів і перегрів у часі", size=17, bold=True)]

    ox, oy = 80, 320            # початок осей
    aw, ah = 690, 230
    f.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.4))         # час
    f.append(line(ox, oy, ox, oy - ah, color=LINE, sw=1.4))        # FPS
    f.append(text(ox + aw, oy + 20, "час під навантаженням →", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ah + 4, "FPS", size=12, color=MUTED, anchor="end"))

    # крива: холодний старт (низько) → плато → троттлінг (падіння)
    def P(t, fps):  # t у частці ширини, fps у частці висоти
        return (ox + t * aw, oy - fps * ah)
    pts = [P(0.00, 0.30), P(0.04, 0.78), P(0.10, 0.82), P(0.40, 0.82),
           P(0.55, 0.80), P(0.62, 0.55), P(0.72, 0.45), P(0.90, 0.43), P(1.00, 0.43)]
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, NEG))

    # зони
    x_warm = P(0.06, 0)[0]
    x_plateau0, x_plateau1 = P(0.10, 0)[0], P(0.55, 0)[0]
    x_thr = P(0.62, 0)[0]
    f.append(line(x_warm, oy, x_warm, oy - ah, color=MUTED, sw=1, dash="3 3"))
    f.append(line(x_plateau1, oy, x_plateau1, oy - ah, color=MUTED, sw=1, dash="3 3"))

    f.append(text(P(0.03, 0.30)[0], oy - 0.30 * ah - 12, "холодний", size=11, bold=True, color=POS))
    f.append(text(P(0.03, 0.30)[0], oy - 0.30 * ah + 2, "старт", size=11, bold=True, color=POS))
    f.append(text((x_plateau0 + x_plateau1) / 2, oy - 0.86 * ah, "стабільне плато (справжній результат)",
                  size=12, bold=True, color=FIELD))
    f.append(text(P(0.82, 0)[0], oy - 0.43 * ah - 14, "троттлінг: чіп нагрівся,", size=11, bold=True, color=POS))
    f.append(text(P(0.82, 0)[0], oy - 0.43 * ah, "частоту зрізано", size=11, bold=True, color=POS))

    f.append(text(W / 2, H - 16,
                  "міряй ПІСЛЯ прогріву й ДОВГО — інакше зловиш або повільний перший кадр, або фальшиве плато",
                  size=12, color=INK))
    return render(os.path.join(IMG, "thermal.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА proj-profiler: фігури бортового профайлера
# ════════════════════════════════════════════════════════════════════════════

# ── P1. Стадійний таймінг: кожна стадія — свій таймер, разом дають затримку ──
def fig_prof_stages():
    """Один кадр проходить чотири стадії; кожну обхоплює власний таймер. Сума
    стадій = затримка кадру. Показано стек часів (захоплення/підготовка/модель/
    розбір) і думку: розклад по стадіях каже, ЗА ЯКУ смикати, а не лише «повільно»."""
    W, H = 860, 430
    f = [text(W / 2, 30, "Профайлер міряє кожну стадію окремо, не лише модель", size=17, bold=True)]

    stages = ["захоплення", "підготовка", "модель", "розбір"]
    cols = [NEG, MUTED, POS, FIELD]
    # умовні мс на стадію (підготовка несподівано важка)
    msec = [6, 22, 41, 5]
    total = sum(msec)

    x0, y0, bw, gap = 60, 95, 175, 18
    # верх: конвеєр стадій, під кожною — t0…t1 і час
    for i, (s, c, m) in enumerate(zip(stages, cols, msec)):
        x = x0 + i * (bw + gap)
        f.append(rect(x, y0, bw, 54, fill=BG, stroke=c, sw=1.8))
        f.append(text(x + bw / 2, y0 + 24, s, size=13, bold=True, color=c))
        f.append(text(x + bw / 2, y0 + 44, "t0 → t1", size=10, color=MUTED))
        f.append(text(x + bw / 2, y0 + 78, "%d мс" % m, size=14, bold=True, color=c))
        if i < 3:
            f.append(arrow(x + bw, y0 + 27, x + bw + gap, y0 + 27))

    # стек: одна смуга, поділена на стадії пропорційно часу
    sy = y0 + 130
    sx, sw_, sh = 60, W - 120, 46
    f.append(text(W / 2, sy - 10, "затримка кадру = сума стадій (%d мс)" % total, size=13, bold=True))
    cur = sx
    for s, c, m in zip(stages, cols, msec):
        w = sw_ * m / total
        f.append(rect(cur, sy, w, sh, fill=c, stroke=BG, sw=2, rx=0))
        if w > 60:
            f.append(text(cur + w / 2, sy + sh / 2 + 5, "%d" % m, size=13, bold=True, color=BG))
        cur += w

    # висновок
    box, bwid, bh = textbox(W / 2, sy + sh + 60,
        "тут видно: «модель» — 41 мс, але «підготовка» — аж 22 мс\n"
        "одне середнє по всьому кадру цього НЕ показало б — а смикати треба за підготовку",
        size=12, fill=FILL, stroke=MUTED)
    f.append(box)
    return render(os.path.join(IMG, "prof-stages.svg"), W, H, *f)


# ── P2. Кільцевий буфер для онлайн-перцентилів ───────────────────────────────
def fig_prof_ring():
    """Кільцевий буфер фіксованого розміру: нові часи пишуться по колу, найстаріші
    затираються. У будь-яку мить копіюємо вміст, сортуємо й читаємо p50/p95/p99 —
    онлайн, без нескінченного росту пам'яті. Показує сталу пам'ять + ковзне вікно."""
    W, H = 820, 440
    f = [text(W / 2, 30, "Кільцевий буфер: перцентилі онлайн, пам'ять стала", size=17, bold=True)]

    cx, cy, R = 250, 235, 130
    N = 12
    import math
    # кільце комірок
    head = 3   # куди пишемо наступний час
    for i in range(N):
        a = -math.pi / 2 + 2 * math.pi * i / N
        x = cx + R * math.cos(a)
        y = cy + R * math.sin(a)
        filled = (i != head)
        col = FIELD if filled else BG
        f.append(circle(x, y, 20, fill=col, stroke=(LINE if filled else POS), sw=(1.5 if filled else 2.4)))
        if filled:
            f.append(text(x, y + 4, "%d" % (24 + (i * 7) % 60), size=10, color=BG, bold=True))
    # вказівник запису
    a = -math.pi / 2 + 2 * math.pi * head / N
    hx = cx + (R + 46) * math.cos(a)
    hy = cy + (R + 46) * math.sin(a)
    tx = cx + (R + 22) * math.cos(a)
    ty = cy + (R + 22) * math.sin(a)
    f.append(arrow(hx, hy, tx, ty, color=POS, sw=2))
    f.append(text(hx, hy - 8, "новий час", size=11, bold=True, color=POS, anchor="middle"))
    f.append(text(cx, cy - 4, "останні N", size=12, bold=True))
    f.append(text(cx, cy + 14, "часів", size=12, bold=True))

    # праворуч — що з нього беремо
    px = 470
    f.append(text(px, 120, "у будь-яку мить:", size=13, bold=True, anchor="start"))
    rows = ["1. копіюємо вміст у тимчасовий масив",
            "2. сортуємо копію",
            "3. читаємо p50 / p95 / p99 / max",
            "4. ориґінал НЕ чіпаємо — пише далі"]
    for i, r in enumerate(rows):
        f.append(text(px, 150 + i * 26, r, size=12, anchor="start"))

    box, bwid, bh = textbox((px + W) / 2 - 20, 300,
        "нове затирає найстаріше →\nвікно «останніх N» ковзає,\nпам'ять стала, рахунок миттєвий",
        size=12, fill=FILL, stroke=FIELD)
    f.append(box)

    f.append(text(W / 2, H - 18,
                  "масив не росте безмежно: бачимо перцентилі ЗА ОСТАННІЙ період прямо в польоті",
                  size=12, color=INK))
    return render(os.path.join(IMG, "prof-ring.svg"), W, H, *f)


# ── P3. Один кадр бреше (кеш) проти потоку різних кадрів ──────────────────────
def fig_prof_samecache():
    """Якщо ганяти модель по ОДНОМУ кадру, він осідає в кеш і дані вже теплі —
    часи штучно низькі й рівні. Потік РІЗНИХ кадрів б'є по пам'яті чесно — часи
    вищі й мають реальний розкид. Показує, чому профайлер годує різними кадрами."""
    W, H = 840, 410
    f = [text(W / 2, 30, "Один кадр осідає в кеш і бреше; різні — кажуть правду", size=17, bold=True)]

    ox, oy = 80, 300
    aw, ah = 690, 210
    f.append(line(ox, oy, ox + aw, oy, color=LINE, sw=1.4))
    f.append(line(ox, oy, ox, oy - ah, color=LINE, sw=1.4))
    f.append(text(ox + aw, oy + 20, "номер прогону →", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - ah + 4, "час, мс", size=12, color=MUTED, anchor="end"))

    import math
    def P(t, v):  # t,v у частках
        return (ox + t * aw, oy - v * ah)

    # один кадр: рівна низька лінія (кеш теплий)
    flat = [P(i / 20, 0.30 + 0.01 * math.sin(i)) for i in range(21)]
    d1 = "M %.1f %.1f " % flat[0] + " ".join("L %.1f %.1f" % p for p in flat[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d1, NEG))
    f.append(text(P(0.7, 0.30)[0], P(0.7, 0.30)[1] - 12,
                  "один кадр: ~30 мс, рівно (брехня — дані в кеші)", size=12, bold=True, color=NEG, anchor="middle"))

    # різні кадри: вище й рвано
    wig = [0.0, .12, -.05, .18, .04, .22, -.02, .15, .30, .06, .19,
           .42, .08, .21, .05, .17, .35, .03, .20, .10, .25]
    diff = [P(i / 20, 0.55 + wig[i] * 0.6) for i in range(21)]
    d2 = "M %.1f %.1f " % diff[0] + " ".join("L %.1f %.1f" % p for p in diff[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d2, POS))
    f.append(text(P(0.5, 0.92)[0], P(0.5, 0.92)[1] - 8,
                  "різні кадри: вище й з розкидом (правда — пам'ять холодна, як у польоті)",
                  size=12, bold=True, color=POS, anchor="middle"))

    f.append(text(W / 2, H - 16,
                  "годуй профайлер ПОТОКОМ різних кадрів — інакше зміряєш швидкість кеша, а не роботи",
                  size=12, color=INK))
    return render(os.path.join(IMG, "prof-samecache.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ВСТАВКА hist-benchmark-gaming: гра з тестом замість самої речі
# ════════════════════════════════════════════════════════════════════════════

# ── H1. Чесний прохід проти підлаштованого драйвера ──────────────────────────
def fig_gaming():
    """Дві доріжки. Чесна: відеокарта не знає траєкторії камери — рахує всю
    сцену, чистить буфер, малює як задумано. Підлаштована: драйвер УПІЗНАВ тест
    і дозволяє собі заборонене в реальній грі — пропускає очищення буфера й
    відрізає наперед «невидиму» геометрію. Робота зникає, бал росте, але вимір
    уже не той самий. Для вставки hist про гру з бенчмарком (3DMark03, 2003)."""
    W, H = 880, 460
    f = [text(W / 2, 30, "Як гра з тестом завищує бал: «поплилий репер»", size=17, bold=True)]

    lane_x0 = 230                 # де починаються «кроки» доріжки
    step_w, gap = 178, 18
    y_honest, y_gamed = 110, 290
    rh = 64

    def lane(y, label, lab_col, note, steps):
        f.append(text(36, y + rh / 2 + 5, label, size=13, bold=True, color=lab_col, anchor="start"))
        f.append(text(lane_x0 + 1.5 * step_w + gap, y - 12, note, size=11, color=MUTED))
        for i, (s, col, struck) in enumerate(steps):
            x = lane_x0 + i * (step_w + gap)
            f.append(rect(x, y, step_w, rh, fill=BG, stroke=col, sw=1.8))
            f.append(text(x + step_w / 2, y + rh / 2 + 5, s, size=12.5, bold=True, color=col))
            if struck:   # перекреслення — крок, який драйвер тихо викинув
                f.append(line(x + 12, y + rh / 2, x + step_w - 12, y + rh / 2, color=POS, sw=2.6))
            if i < len(steps) - 1:
                f.append(arrow(x + step_w, y + rh / 2, x + step_w + gap, y + rh / 2, color=INK))

    lane(y_honest, "ЧЕСНО", FIELD, "не знає, куди гляне камера", [
        ("рахує ВСЮ сцену", FIELD, False),
        ("чистить буфер", FIELD, False),
        ("малює як задумано", FIELD, False),
    ])
    lane(y_gamed, "ПІД ТЕСТ", POS, "знає політ камери наперед", [
        ("УПІЗНАВ тест", POS, False),
        ("буфер НЕ чистить", POS, True),
        ("відрізав «невидиме»", POS, True),
    ])

    f.append(text(W / 2, H - 62,
                  "робота зникає → FPS росте, але це працює ЛИШЕ бо тест завжди однаковий",
                  size=12.5, bold=True, color=INK))
    f.append(text(W / 2, H - 38,
                  "у реальній грі камерою керує гравець — відрізати наперед нічого не можна",
                  size=12, color=MUTED))
    f.append(text(W / 2, H - 13,
                  "вимір перестав бути «тим самим, що в інших» — реперна точка поплила",
                  size=12, color=POS, bold=True))
    return render(os.path.join(IMG, "gaming.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gap()
    fig_latency_throughput()
    fig_tail()
    fig_thermal()
    fig_prof_stages()
    fig_prof_ring()
    fig_prof_samecache()
    fig_gaming()
    print("OK: фігури у", IMG)
