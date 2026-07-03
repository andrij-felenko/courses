# -*- coding: utf-8 -*-
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 1: сигнал → енергія кадрів → поріг → подія
# Три доріжки: сира хвиля, згладжена енергія з порогом, прапорець «подія».
# ────────────────────────────────────────────────────────────────────────────
def fig_energy_threshold():
    W, H = 760, 462
    x0, x1 = 70, 720
    span = x1 - x0
    N = 260
    random.seed(7)

    # Модель сигналу: тиша з дрібним шумом, потім гучний сплеск (слово), знову тиша,
    # тоді короткий тихий «стук», що НЕ має спрацювати.
    def envelope(i):
        t = i / (N - 1)
        e = 0.06  # фонова тиша
        # слово: 0.30..0.58
        if 0.30 <= t <= 0.58:
            c = (t - 0.44) / 0.14
            e = 0.06 + 0.9 * math.exp(-4.0 * c * c)
        # тихий стук: 0.74..0.80 — нижче порогу
        if 0.74 <= t <= 0.80:
            c = (t - 0.77) / 0.03
            e = max(e, 0.06 + 0.22 * math.exp(-3.0 * c * c))
        return e

    wave = []
    for i in range(N):
        a = envelope(i)
        s = a * math.sin(i * 0.9) * (0.6 + 0.4 * random.random()) + (random.random() - 0.5) * 0.05
        wave.append(s)

    # Короткочасна енергія: RMS у вікні
    win = 9
    energy = []
    for i in range(N):
        lo = max(0, i - win)
        hi = min(N, i + win + 1)
        acc = sum(v * v for v in wave[lo:hi]) / (hi - lo)
        energy.append(math.sqrt(acc))

    frags = []

    # --- Доріжка А: сира хвиля ---
    ay, ah = 66, 96
    amid = ay + ah / 2
    frags.append(text(x0, ay - 12, "Сирий сигнал (відліки)", size=13, color=MUTED, anchor="start"))
    frags.append(line(x0, amid, x1, amid, color="#d0d5db", sw=1))
    pts = []
    for i, s in enumerate(wave):
        px = x0 + span * i / (N - 1)
        py = amid - s * (ah * 0.46)
        pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.1"/>'
                 % (" ".join(pts), NEG))

    # --- Доріжка Б: енергія + поріг ---
    by, bh = 210, 120
    bbot = by + bh
    emax = max(energy) * 1.08
    thr = 0.20  # поріг (нормований до тієї ж шкали)
    frags.append(text(x0, by - 12, "Короткочасна енергія кадру + поріг", size=13, color=MUTED, anchor="start"))
    frags.append(line(x0, bbot, x1, bbot, color="#d0d5db", sw=1))
    # заливка енергії
    poly = ["%.1f,%.1f" % (x0, bbot)]
    for i, e in enumerate(energy):
        px = x0 + span * i / (N - 1)
        py = bbot - (e / emax) * bh
        poly.append("%.1f,%.1f" % (px, py))
    poly.append("%.1f,%.1f" % (x1, bbot))
    frags.append('<polygon points="%s" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
                 % (" ".join(poly), NEG))
    # лінія порогу
    thy = bbot - (thr / emax) * bh
    frags.append(line(x0, thy, x1, thy, color=POS, sw=2, dash="7 5"))
    frags.append(text(x1 + 4, thy + 4, "поріг", size=12, color=POS, anchor="start"))

    # --- Доріжка В: прапорець події (де енергія > поріг) ---
    cy, ch = 372, 30
    frags.append(text(x0, cy - 10, "Прапорець «подія»", size=13, color=MUTED, anchor="start"))
    active = [1 if e > thr else 0 for e in energy]
    # намалювати смуги активності
    i = 0
    while i < N:
        if active[i]:
            j = i
            while j < N and active[j]:
                j += 1
            px = x0 + span * i / (N - 1)
            pw = span * (j - i) / (N - 1)
            frags.append(rect(px, cy, pw, ch, fill="#d6f0df", stroke=FIELD, sw=1.8, rx=4))
            frags.append(text(px + pw / 2, cy + ch / 2 + 4,
                              "ПОДІЯ", size=12, color="#1e7a45", bold=True))
            i = j
        else:
            i += 1

    # підпис тихого стуку під порогом
    kx = x0 + span * 0.77
    frags.append(line(kx, by + 8, kx, bbot, color=MUTED, sw=1, dash="2 3"))
    tb, tw, th = textbox(kx, 415, "тихий стук —\nнижче порогу,\nвірно проігноровано",
                         size=10.5, color=MUTED, pad=6)
    frags.append(tb)

    render(os.path.join(OUT, "energy-threshold.svg"), W, H, *frags)


# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 2: гістерезис (два пороги) + утримання (hangover) як автомат
# ────────────────────────────────────────────────────────────────────────────
def fig_hysteresis_fsm():
    W, H = 720, 340
    frags = []
    frags.append(text(W / 2, 30, "Два пороги проти дребезгу + утримання хвоста", size=15, bold=True))

    # два стани
    sil = textbox(180, 150, "ТИША", size=17, bold=True, pad=22,
                  fill="#eaf0fd", stroke=NEG, min_w=150)
    spc = textbox(540, 150, "МОВА", size=17, bold=True, pad=22,
                  fill="#d6f0df", stroke=FIELD, min_w=150)
    frags.append(sil[0])
    frags.append(spc[0])

    # перехід ТИША → МОВА (верхній поріг)
    frags.append(arrow(258, 120, 462, 120, color=POS, sw=2.2))
    up = textbox(360, 92, "енергія > ПОРІГ_ВГОРУ", size=12, color=POS, pad=7,
                 fill="#fff", stroke=POS)
    frags.append(up[0])

    # перехід МОВА → ТИША (нижній поріг + вичерпано утримання)
    frags.append(arrow(462, 180, 258, 180, color=NEG, sw=2.2))
    dn = textbox(360, 208, "енергія < ПОРІГ_ВНИЗ\nі хвіст вичерпано", size=12, color=NEG, pad=7,
                 fill="#fff", stroke=NEG)
    frags.append(dn[0])

    # петля утримання на стані МОВА
    frags.append('<path d="M 600 108 A 46 46 0 1 1 592 106" fill="none" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>' % MUTED)
    hb = textbox(636, 60, "нижче порогу, але\nхвіст ще тримає → МОВА", size=10.5, color=MUTED, pad=6)
    frags.append(hb[0])

    # пояснення внизу — багаторядковий текст фіксованим шрифтом (не стискаємо)
    exp = ("ПОРІГ_ВГОРУ вищий за ПОРІГ_ВНИЗ: між ними стан не міняється —\n"
           "звук на межі не «тремтить». Хвіст (hangover) додає N тихих кадрів\n"
           "перед виходом, щоб не рвати слово на паузах між складами.")
    frags.append(rect(50, 262, 620, 62, fill="#f4f6f8", stroke="#d0d5db", sw=1.5))
    frags.append(mtext(360, 284, exp, size=12, color=INK))

    render(os.path.join(OUT, "hysteresis-fsm.svg"), W, H, *frags)


# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 3: площина «енергія × частота нуль-перетинів» — три області
# ────────────────────────────────────────────────────────────────────────────
def fig_energy_zcr_plane():
    W, H = 700, 470
    ox, oy = 90, 380          # початок осей
    ax, ay = 620, 70          # кінці осей
    frags = []
    frags.append(text(W / 2, 30, "Енергія × частота нуль-перетинів: що є що", size=15, bold=True))

    # осі
    frags.append(arrow(ox, oy, ax + 10, oy, color=INK, sw=1.8))   # X: ZCR
    frags.append(arrow(ox, oy, ox, ay - 10, color=INK, sw=1.8))   # Y: енергія
    frags.append(text(ax + 6, oy + 22, "частота нуль-перетинів (ZCR) →", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 14, ay - 16, "енергія", size=12, color=INK, anchor="start"))
    frags.append(text(ox - 14, ay - 2, "↑", size=13, color=INK, anchor="start"))

    def dot(cx, cy, col):
        return circle(cx, cy, 4.2, fill=col, stroke=col, sw=1)

    random.seed(11)
    def blob(cx, cy, sx, sy, n, col):
        out = []
        for _ in range(n):
            dx = (random.random() - 0.5) * 2 * sx
            dy = (random.random() - 0.5) * 2 * sy
            out.append(dot(cx + dx, cy + dy, col))
        return out

    # ТИША: низька енергія, будь-який ZCR (шум → радше високий), лівий-нижній..правий-нижній низ
    for f in blob(300, 340, 200, 22, 26, MUTED):
        frags.append(f)
    tb = textbox(300, 405, "ТИША: енергія майже нуль", size=12, color=MUTED, pad=6,
                 fill="#f0f1f3", stroke=MUTED)
    frags.append(tb[0])

    # ГОЛОСНІ (voiced): висока енергія, НИЗЬКИЙ ZCR — лівий верх
    for f in blob(210, 150, 55, 55, 30, FIELD):
        frags.append(f)
    vb = textbox(180, 88, "ГОЛОСНІ звуки:\nгучні, ZCR низький", size=12, color="#1e7a45", pad=7,
                 fill="#d6f0df", stroke=FIELD)
    frags.append(vb[0])

    # ГЛУХІ/шиплячі (unvoiced): помірна енергія, ВИСОКИЙ ZCR — правий центр
    for f in blob(500, 235, 55, 48, 28, POS):
        frags.append(f)
    ub = textbox(520, 158, "ГЛУХІ/шиплячі (с, ш, ф):\nтихіші, ZCR високий", size=12, color="#a12f22", pad=7,
                 fill="#fdecea", stroke=POS)
    frags.append(ub[0])

    render(os.path.join(OUT, "energy-zcr-plane.svg"), W, H, *frags)


# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 4 (для вставки proj): модуль-сторож як ланка між кільцем захоплення
# й важким споживачем. Показує API (feed/poll), і хто коли спить/прокидається.
# ────────────────────────────────────────────────────────────────────────────
def fig_vad_gate():
    W, H = 780, 300
    frags = []
    frags.append(text(W / 2, 28, "Сторож між кільцем захоплення і важким модулем", size=15, bold=True))

    # Кільце захоплення (ліворуч)
    ring = textbox(105, 130, "Кільце\nзахоплення\n(DMA)", size=12.5, pad=14,
                   fill="#eaf0fd", stroke=NEG, min_w=120)
    frags.append(ring[0])

    # Модуль VAD (центр)
    vad = textbox(390, 130, "VAD-сторож", size=15, bold=True, pad=20,
                  fill="#d6f0df", stroke=FIELD, min_w=200)
    frags.append(vad[0])
    # API-підписи всередині/під модулем
    api = textbox(390, 196, "vad_feed(frame)  →  vad_poll()", size=11.5, pad=6,
                  fill="#fff", stroke=FIELD, color="#1e7a45")
    frags.append(api[0])

    # Важкий споживач (праворуч)
    heavy = textbox(680, 130, "Важкий модуль\nзапис · стиснення\n· KWS", size=12,
                    pad=13, fill="#fdecea", stroke=POS, min_w=150)
    frags.append(heavy[0])

    # Стрілка: кільце → VAD (кадри)
    frags.append(arrow(168, 118, 288, 118, color=NEG, sw=2.2))
    frags.append(text(228, 104, "кадри", size=11, color=NEG))

    # Стрілка: VAD → важкий (прапорець «прокинься»)
    frags.append(arrow(492, 118, 604, 118, color=POS, sw=2.2))
    frags.append(text(548, 104, "прапорець", size=11, color=POS))

    # Стани сну під модулями
    sb = textbox(390, 258, "мікроват — дрімає на потоці", size=11, pad=6, color=MUTED,
                 fill="#f4f6f8", stroke="#d0d5db")
    frags.append(sb[0])
    hb = textbox(680, 210, "спить, поки\nсторож не збудить", size=10.5, pad=6, color="#a12f22",
                 fill="#fdecea", stroke=POS)
    frags.append(hb[0])

    render(os.path.join(OUT, "vad-gate.svg"), W, H, *frags)


# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 5 (для вставки proj): що робиться на КОЖЕН кадр усередині vad_feed().
# Ланцюг: кадр → (енергія, ZCR) → поріг = фон·K → FSM → вихід; і петля
# оновлення фону ЛИШЕ в гілці тиші (ключова інваріанта модуля).
# ────────────────────────────────────────────────────────────────────────────
def fig_feed_dataflow():
    W, H = 720, 430
    frags = []
    frags.append(text(W / 2, 28, "Один кадр усередині vad_feed(): що з чим", size=15, bold=True))

    # Вхід: кадр
    inb = textbox(120, 80, "кадр\nN відліків", size=12, pad=12, fill="#eaf0fd", stroke=NEG, min_w=110)
    frags.append(inb[0])

    # Дві прикмети
    en = textbox(340, 80, "енергія\n(сума x²)", size=12, pad=11, fill=FILL, stroke=LINE, min_w=120)
    zc = textbox(340, 165, "ZCR\n(зміни знаку)", size=12, pad=11, fill=FILL, stroke=LINE, min_w=120)
    frags.append(en[0]); frags.append(zc[0])
    frags.append(arrow(178, 72, 279, 72, color=INK, sw=1.8))
    frags.append(arrow(178, 90, 279, 158, color=INK, sw=1.8))

    # Пороги = фон·K
    thr = textbox(560, 80, "поріг_ВГ = фон·K_UP\nпоріг_ВН = фон·K_DOWN", size=11, pad=10,
                  fill="#fff", stroke=POS, color="#a12f22", min_w=170)
    frags.append(thr[0])
    frags.append(arrow(402, 72, 470, 76, color=INK, sw=1.8))

    # Автомат станів
    fsm = textbox(430, 270, "АВТОМАТ  ТИША ⇄ МОВА\n(гістерезис + хвіст)", size=12.5, bold=True, pad=16,
                  fill="#d6f0df", stroke=FIELD, min_w=250)
    frags.append(fsm[0])
    frags.append(arrow(560, 108, 470, 236, color=INK, sw=1.8))   # пороги → FSM
    frags.append(arrow(360, 200, 400, 236, color=INK, sw=1.8))   # ZCR-страховка → FSM
    # підпис ЛІВОРУЧ від діагональної стрілки (кінець на x=354, стрілка стартує з x=360) — не ріже напис
    frags.append(text(354, 214, "ZCR-страховка глухих", size=10.5, color=MUTED, anchor="end"))

    # Вихід прапорця
    outb = textbox(430, 360, "прапорець події → vad_poll()", size=12, pad=10,
                   fill="#fdecea", stroke=POS, color="#a12f22", min_w=250)
    frags.append(outb[0])
    frags.append(arrow(430, 300, 430, 336, color=INK, sw=2))

    # Ключова петля: оновлення фону ЛИШЕ в тиші
    frags.append('<path d="M 250 285 Q 120 300 130 150 Q 135 110 270 92" fill="none" '
                 'stroke="%s" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arrow)"/>' % FIELD)
    lb = textbox(150, 250, "фон += α·(енергія − фон)\nЛИШЕ якщо стан = ТИША", size=10.5, pad=7,
                 color="#1e7a45", fill="#eef8f1", stroke=FIELD)
    frags.append(lb[0])

    render(os.path.join(OUT, "feed-dataflow.svg"), W, H, *frags)


# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 6 (детальна): стала часу EMA. Один ступінчастий стрибок фону,
# згладжений трьома α; горизонтальний пунктир на рівні 1−1/e (≈63%),
# якого крива сягає за τ ≈ 1/α кадрів.
# ────────────────────────────────────────────────────────────────────────────
def fig_ema_time_constant():
    W, H = 760, 430
    ox, oy = 80, 350          # початок осей (лівий-нижній)
    ax, ay = 700, 80          # кінці осей
    frags = []
    frags.append(text(W / 2, 30, "Стала часу згладжування: α керує швидкістю фону", size=15, bold=True))

    # осі
    frags.append(arrow(ox, oy, ax + 8, oy, color=INK, sw=1.8))     # X: кадри
    frags.append(arrow(ox, oy, ox, ay - 8, color=INK, sw=1.8))     # Y: рівень
    frags.append(text(ax + 4, oy + 22, "кадри →", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 12, ay - 12, "оцінка фону", size=12, color=INK, anchor="start"))

    lo_y, hi_y = oy, ay + 20   # рівень «до» і «після» стрибка (у пікселях)
    step_x = ox + 70           # де стається стрибок фону
    x_end = ax

    # цільовий рівень (куди прямують усі криві) + старий рівень
    frags.append(line(ox, hi_y, ax, hi_y, color="#d0d5db", sw=1, dash="4 4"))
    frags.append(text(ax + 4, hi_y - 6, "новий фон", size=11, color=MUTED, anchor="end"))

    # рівень 1 − 1/e ≈ 0.632 між старим і новим
    frac = 0.632
    lvl_y = lo_y + (hi_y - lo_y) * frac
    frags.append(line(step_x, lvl_y, ax, lvl_y, color=POS, sw=1.4, dash="6 4"))
    frags.append(text(ax + 4, lvl_y + 14, "63 %  (1 − 1/e)", size=11, color=POS, anchor="end"))

    # сам ступінчастий вхід (те, що згладжуємо)
    inp = ["%.1f,%.1f" % (ox, lo_y), "%.1f,%.1f" % (step_x, lo_y),
           "%.1f,%.1f" % (step_x, hi_y), "%.1f,%.1f" % (x_end, hi_y)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" '
                 'stroke-dasharray="2 3"/>' % (" ".join(inp), MUTED))

    span = x_end - step_x
    # три експоненційні відгуки з різними α; τ_кадрів = 1/α, у пікселях
    curves = [(0.30, FIELD, "α велика (швидко, тремтить)"),
              (0.08, NEG,   "α помірна (компроміс)"),
              (0.02, INK,   "α мала (гладко, запізнюється)")]
    # масштаб кадрів→пікселі: візьмемо так, щоб τ малої α (=50) вписалось
    px_per_frame = span / 90.0
    for alpha, col, _ in curves:
        pts = []
        val = 0.0                                   # нормований 0..1 приріст
        n = int(span / px_per_frame) + 1
        for k in range(n):
            val = val + alpha * (1.0 - val)         # той самий EMA-крок
            px = step_x + k * px_per_frame
            py = lo_y + (hi_y - lo_y) * val
            pts.append("%.1f,%.1f" % (px, py))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                     % (" ".join(pts), col))
        # вертикальна позначка τ = 1/α кадрів на осі X (де крива ~63%)
        tau_px = step_x + (1.0 / alpha) * px_per_frame
        if tau_px < ax:
            frags.append(line(tau_px, lvl_y, tau_px, oy, color=col, sw=1, dash="1 3"))
            frags.append(circle(tau_px, lvl_y, 3.2, fill=col, stroke=col, sw=1))

    # легенда: три рядки зі зразком лінії (без накладань, ліворуч унизу)
    lx = 150
    for i, (alpha, col, lbl) in enumerate(curves):
        yy = 372 + i * 20
        frags.append(line(lx, yy, lx + 26, yy, color=col, sw=2.6))
        frags.append(text(lx + 34, yy + 4, lbl, size=11.5, color=INK, anchor="start"))

    # підпис «τ ≈ 1/α» біля позначок
    frags.append(text(step_x + 4, oy - 6, "вертикальні позначки — τ ≈ 1/α кадрів",
                      size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "ema-time-constant.svg"), W, H, *frags)


# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 7 (детальна): ZCR = 2f/fs. Дві хвилі однакової тривалості —
# низька частота (рідкі перетини) і висока (густі перетини); перетини нуля
# позначені кружечками; поруч формула для кожної.
# ────────────────────────────────────────────────────────────────────────────
def fig_zcr_frequency():
    W, H = 760, 430
    x0, x1 = 70, 560
    span = x1 - x0
    Np = 400
    frags = []
    frags.append(text(W / 2, 30, "Частота нуль-перетинів кодує частоту: ZCR = 2f/fs", size=15, bold=True))

    def draw_wave(cy, amp, cycles, col, jitter=0.0, seed=1):
        random.seed(seed)
        # нульова лінія
        frags.append(line(x0, cy, x1, cy, color="#d0d5db", sw=1))
        pts = []
        vals = []
        for i in range(Np):
            t = i / (Np - 1)
            v = math.sin(2 * math.pi * cycles * t)
            if jitter:
                v = v + (random.random() - 0.5) * jitter
            vals.append(v)
            px = x0 + span * t
            py = cy - v * amp
            pts.append("%.1f,%.1f" % (px, py))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>'
                     % (" ".join(pts), col))
        # позначити перетини нуля кружечками
        cnt = 0
        for i in range(1, Np):
            if (vals[i - 1] >= 0) != (vals[i] >= 0):
                cnt += 1
                px = x0 + span * (i / (Np - 1))
                frags.append(circle(px, cy, 3.0, fill="#fff", stroke=col, sw=1.6))
        return cnt

    # верхня: низька частота (голосні) — мало перетинів
    cyA = 130
    frags.append(text(x0, cyA - 58, "Низька частота — голосні звуки", size=12.5, color="#1e7a45", anchor="start"))
    nA = draw_wave(cyA, 44, 4, FIELD, jitter=0.0, seed=3)
    fb = textbox(650, cyA, "мало перетинів\n→ мала ZCR\n→ низька f", size=11.5, pad=9,
                 fill="#d6f0df", stroke=FIELD, color="#1e7a45", min_w=170)
    frags.append(fb[0])

    # нижня: висока частота (глухі шиплячі) — багато перетинів
    cyB = 320
    frags.append(text(x0, cyB - 58, "Висока частота — глухі шиплячі (с, ш, ф)", size=12.5, color="#a12f22", anchor="start"))
    nB = draw_wave(cyB, 40, 17, POS, jitter=0.35, seed=8)
    hb = textbox(650, cyB, "багато перетинів\n→ велика ZCR\n→ висока f", size=11.5, pad=9,
                 fill="#fdecea", stroke=POS, color="#a12f22", min_w=170)
    frags.append(hb[0])

    # нижній пояснювальний рядок у власній рамці
    frags.append(rect(60, 388, 640, 30, fill="#f4f6f8", stroke="#d0d5db", sw=1.4))
    frags.append(text(W / 2 - 40, 407,
                      "Синусоїда перетинає нуль двічі за період → перетинів за секунду = 2f → ZCR = 2f / fs",
                      size=11.5, color=INK))

    render(os.path.join(OUT, "zcr-frequency.svg"), W, H, *frags)


# ────────────────────────────────────────────────────────────────────────────
# ФІГУРА 8 (детальна): автомат ТИША ⇄ ПОДІЯ з таймінгом.
# Ліворуч два стани й три переходи (вхід ВГ, вихід ВН+хвіст, петля утримання),
# інваріанта «оновлення фону лише в ТИШІ» висить на стані ТИША;
# праворуч — дві часові смуги: затримка входу (1 кадр) і хвіст на виході.
# ────────────────────────────────────────────────────────────────────────────
def fig_vad_fsm_timing():
    W, H = 780, 470
    frags = []
    frags.append(text(W / 2, 28, "Автомат детектора з таймінгом входу й виходу", size=15, bold=True))

    # ── ліва половина: автомат ──
    sil = textbox(150, 150, "ТИША", size=17, bold=True, pad=22,
                  fill="#eaf0fd", stroke=NEG, min_w=140)
    evt = textbox(430, 150, "ПОДІЯ", size=17, bold=True, pad=22,
                  fill="#d6f0df", stroke=FIELD, min_w=140)
    frags.append(sil[0]); frags.append(evt[0])

    # ТИША → ПОДІЯ (верхній поріг)
    frags.append(arrow(222, 122, 358, 122, color=POS, sw=2.2))
    up = textbox(290, 96, "MSE > поріг_ВГ", size=11.5, color=POS, pad=6, fill="#fff", stroke=POS)
    frags.append(up[0])

    # ПОДІЯ → ТИША (нижній поріг + хвіст)
    frags.append(arrow(358, 182, 222, 182, color=NEG, sw=2.2))
    dn = textbox(290, 210, "MSE < поріг_ВН\nі хвіст = 0", size=11.5, color=NEG, pad=6, fill="#fff", stroke=NEG)
    frags.append(dn[0])

    # петля утримання на ПОДІЇ (праворуч від стану, щоб не налазити на стрілки)
    frags.append('<path d="M 492 132 A 42 42 0 1 1 486 128" fill="none" stroke="%s" '
                 'stroke-width="2" marker-end="url(#arrow)"/>' % MUTED)
    hb = textbox(560, 92, "MSE < поріг_ВН,\nале хвіст > 0 → тримаємось", size=10.5, color=MUTED, pad=6,
                 fill="#f4f6f8", stroke="#d0d5db")
    frags.append(hb[0])

    # інваріанта: оновлення фону лише в ТИШІ (петля вниз-ліворуч від ТИШІ)
    frags.append('<path d="M 108 178 A 40 40 0 1 0 118 200" fill="none" stroke="%s" '
                 'stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arrow)"/>' % NEG)
    inv = textbox(150, 258, "фон += α·(MSE − фон)\nЛИШЕ у стані ТИША", size=10.5, color=NEG, pad=7,
                  fill="#eaf0fd", stroke=NEG)
    frags.append(inv[0])

    # ── права половина: часові смуги ──
    tx0, tx1 = 300, 720
    # смуга «вхід»
    ty = 330
    frags.append(text(tx0, ty - 14, "Таймінг ВХОДУ", size=12, bold=True, color=INK, anchor="start"))
    frags.append(line(tx0, ty, tx1, ty, color=MUTED, sw=1))
    # тиша до, подія після — вхід запізнюється на кадр вирішення
    ev_x = tx0 + 150
    frags.append(rect(tx0, ty + 6, ev_x - tx0, 22, fill="#eaf0fd", stroke=NEG, sw=1.4))
    frags.append(rect(ev_x, ty + 6, tx1 - ev_x, 22, fill="#d6f0df", stroke=FIELD, sw=1.4))
    frags.append(text((tx0 + ev_x) / 2, ty + 21, "тиша", size=10.5, color=NEG))
    frags.append(text((ev_x + tx1) / 2, ty + 21, "прапорець піднято", size=10.5, color="#1e7a45"))
    # позначка кадру-затримки
    frags.append(line(ev_x - 26, ty + 4, ev_x - 26, ty + 34, color=POS, sw=1.3, dash="3 3"))
    frags.append(line(ev_x, ty + 4, ev_x, ty + 34, color=POS, sw=1.3, dash="3 3"))
    frags.append(text(ev_x - 13, ty + 50, "+1 кадр", size=10, color=POS))

    # смуга «вихід»
    oy2 = 410
    frags.append(text(tx0, oy2 - 14, "Таймінг ВИХОДУ", size=12, bold=True, color=INK, anchor="start"))
    frags.append(line(tx0, oy2, tx1, oy2, color=MUTED, sw=1))
    end_x = tx0 + 150            # реальний кінець звуку
    hang_x = end_x + 130         # прапорець тримається ще хвіст
    frags.append(rect(tx0, oy2 + 6, end_x - tx0, 22, fill="#d6f0df", stroke=FIELD, sw=1.4))
    frags.append(rect(end_x, oy2 + 6, hang_x - end_x, 22, fill="#eef8f1", stroke=FIELD, sw=1.2))
    frags.append(rect(hang_x, oy2 + 6, tx1 - hang_x, 22, fill="#eaf0fd", stroke=NEG, sw=1.4))
    frags.append(text((tx0 + end_x) / 2, oy2 + 21, "звук", size=10.5, color="#1e7a45"))
    frags.append(text((end_x + hang_x) / 2, oy2 + 21, "хвіст", size=10.5, color="#1e7a45"))
    frags.append(text((hang_x + tx1) / 2, oy2 + 21, "тиша", size=10.5, color=NEG))
    frags.append(line(end_x, oy2 + 4, end_x, oy2 + 34, color=MUTED, sw=1.3, dash="3 3"))
    frags.append(line(hang_x, oy2 + 4, hang_x, oy2 + 34, color=MUTED, sw=1.3, dash="3 3"))
    frags.append(text((end_x + hang_x) / 2, oy2 + 50, "HANG кадрів", size=10, color=MUTED))

    render(os.path.join(OUT, "vad-fsm-timing.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_energy_threshold()
    fig_hysteresis_fsm()
    fig_energy_zcr_plane()
    fig_vad_gate()
    fig_feed_dataflow()
    fig_ema_time_constant()
    fig_zcr_frequency()
    fig_vad_fsm_timing()
    print("figures written to", OUT)
