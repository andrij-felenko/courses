# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

HOT  = "#c0392b"   # гаряче, перевантажене
COOL = "#2457d6"   # холодне, із запасом
OK   = "#27ae60"   # здорове, у бюджеті
INKBG = "#1e1e2e"  # темна код-плашка
CODE  = "#7fb8a0"  # колір коду на темному


# ── two-budgets: дві скінченні скарбнички чипа ───────────────────────────────
# Ідея: усе, що робить пристрій, витрачає або такти, або байти, або обидва.
# Профілювання — облік обох бюджетів; третього не існує.
def fig_two_budgets():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 58, "усе, що робить пристрій, витрачає одне, друге або обидва",
                  size=12, color=MUTED, italic=True))

    # ліва скарбничка — ТАКТИ
    bx, bw = 70, 250
    p.append(rect(bx, 92, bw, 200, fill="#fbecec", stroke=HOT, sw=2.2, rx=12))
    cx = bx + bw / 2
    p.append(text(cx, 124, "ПРОЦЕСОРНІ ТАКТИ", size=15, color=HOT, bold=True))
    p.append(text(cx, 150, "скінченна швидкість", size=11, color=INK))
    p.append(text(cx, 196, "напр. 168 МГц", size=13, color=INK, bold=True))
    p.append(text(cx, 218, "= 168 млн тактів/с", size=11, color=MUTED))
    p.append(text(cx, 262, "профіль CPU:", size=11, color=HOT, bold=True))
    p.append(text(cx, 280, "«куди йдуть такти»", size=11, color=INK))

    # права скарбничка — БАЙТИ
    bx2 = 400
    p.append(rect(bx2, 92, bw, 200, fill="#e9eefb", stroke=COOL, sw=2.2, rx=12))
    cx2 = bx2 + bw / 2
    p.append(text(cx2, 124, "БАЙТИ ПАМ'ЯТІ", size=15, color=COOL, bold=True))
    p.append(text(cx2, 150, "скінченна RAM", size=11, color=INK))
    p.append(text(cx2, 196, "напр. кілька сотень КБ", size=12, color=INK, bold=True))
    p.append(text(cx2, 218, "стеки · купа · глобальні", size=11, color=MUTED))
    p.append(text(cx2, 262, "профіль пам'яті:", size=11, color=COOL, bold=True))
    p.append(text(cx2, 280, "«куди йдуть байти»", size=11, color=INK))

    p.append(text(W / 2, 330, "більше нічого немає — третього бюджета не існує",
                  size=12, color=OK, bold=True))
    render(os.path.join(OUT, "two-budgets.svg"), W, H, *p,
           title="Два скінченні бюджети мікроконтролера")


# ── sampling-vs-instrumentation: дві оптики на CPU ───────────────────────────
# Ідея: семплінг фотографує систему таймером (статистичний портрет, дешево),
# інструментація ставить мітки на вхід/вихід ділянки (точний Δt, але видно лише обвішане).
def fig_sampling_vs_instr():
    W, H = 820, 400
    p = []

    # ── верх: СЕМПЛІНГ ──
    p.append(text(W / 2, 56, "СЕМПЛІНГ — фотокамера з таймером", size=14, color=COOL, bold=True))
    base_y = 92
    # «знімки» через рівні проміжки
    funcs = ["A", "B", "B", "B", "C", "B", "D", "B", "B", "A"]
    n = len(funcs)
    x0, span = 70, 560
    step = span / (n - 1)
    for i, fn in enumerate(funcs):
        x = x0 + i * step
        col = HOT if fn == "B" else MUTED
        p.append(line(x, base_y, x, base_y + 22, color=col, sw=2))
        p.append(text(x, base_y - 6, "📷", size=11, color=MUTED))
        p.append(text(x, base_y + 38, fn, size=11, color=col, bold=(fn == "B")))
    p.append(text(x0 + span + 36, base_y + 14, "→", size=20, color=INK))
    # портрет
    px = x0 + span + 70
    p.append(rect(px, base_y - 14, 110, 64, fill="#fbecec", stroke=HOT, sw=1.8, rx=8))
    p.append(text(px + 55, base_y + 6, "B: 60%", size=11, color=HOT, bold=True))
    p.append(text(px + 55, base_y + 24, "решта: 40%", size=10, color=INK))
    p.append(text(px + 55, base_y + 42, "статистика", size=9, color=MUTED, italic=True))
    p.append(text(W / 2, base_y + 70, "дешево, але рідкісний сплеск може проскочити між знімками",
                  size=10.5, color=MUTED, italic=True))

    # роздільник
    p.append(line(40, 224, W - 40, 224, color="#dddddd", sw=1))

    # ── низ: ІНСТРУМЕНТАЦІЯ ──
    p.append(text(W / 2, 256, "ІНСТРУМЕНТАЦІЯ — мітки на вході й виході", size=14, color=HOT, bold=True))
    iy = 300
    seg_x, seg_w = 220, 300
    p.append(rect(seg_x, iy, seg_w, 40, fill="#fbecec", stroke=HOT, sw=2, rx=8))
    p.append(text(seg_x + seg_w / 2, iy + 25, "підозріла ділянка", size=12, color=INK, bold=True))
    # мітки t0 / t1
    p.append(line(seg_x, iy - 14, seg_x, iy + 54, color=COOL, sw=2.2, dash="4,3"))
    p.append(text(seg_x, iy - 22, "t0 = CYCCNT", size=10.5, color=COOL, bold=True))
    p.append(line(seg_x + seg_w, iy - 14, seg_x + seg_w, iy + 54, color=COOL, sw=2.2, dash="4,3"))
    p.append(text(seg_x + seg_w, iy - 22, "t1 = CYCCNT", size=10.5, color=COOL, bold=True))
    p.append(text(seg_x + seg_w / 2, iy + 74, "Δt = t1 − t0 — точний час у тактах", size=11, color=OK, bold=True))
    p.append(text(W / 2, iy + 92, "точно, але видно лише те, що ви самі обвісили",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "sampling-vs-instrumentation.svg"), W, H, *p,
           title="Дві оптики на процесорний час")


# ── cpu-load: завантаженість як паливомір ────────────────────────────────────
# Ідея: метрика здоров'я — частка часу на корисну роботу проти простою; на
# багатоядерному чипі середнє бреше, дивитися треба поядрово.
def fig_cpu_load():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 56, "яку частку часу ядро робить корисне, а скільки дрімає",
                  size=12, color=MUTED, italic=True))

    def gauge(cx, cy, frac, label, sub):
        r = 64
        # дуга-фон (півколо)
        import math
        def pt(a):
            return cx + r * math.cos(a), cy - r * math.sin(a)
        x1, y1 = pt(math.pi)
        x2, y2 = pt(0)
        p.append('<path d="M %.1f %.1f A %d %d 0 0 1 %.1f %.1f" fill="none" stroke="#e5e7eb" stroke-width="16"/>'
                 % (x1, y1, r, r, x2, y2))
        # дуга-заповнення
        a_end = math.pi - frac * math.pi
        xe, ye = pt(a_end)
        col = HOT if frac > 0.85 else (OK if frac < 0.6 else "#caa24a")
        large = 0
        p.append('<path d="M %.1f %.1f A %d %d 0 %d 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="16"/>'
                 % (x1, y1, r, r, large, xe, ye, col))
        p.append(text(cx, cy - 8, "%d%%" % int(frac * 100), size=20, color=col, bold=True))
        p.append(text(cx, cy + 14, "зайнято", size=10, color=MUTED))
        p.append(text(cx, cy + 44, label, size=13, color=INK, bold=True))
        p.append(text(cx, cy + 64, sub, size=10.5, color=col))

    gauge(210, 170, 0.97, "Ядро 0 (радіо)", "idle ≈ 0 — на межі")
    gauge(510, 170, 0.35, "Ядро 1 (прикладне)", "є запас — дихає")

    p.append(text(W / 2, 322, "«середнє по чипу ≈ 66%» бреше: Ядро 0 уже задихається",
                  size=12, color=HOT, bold=True))
    render(os.path.join(OUT, "cpu-load.svg"), W, H, *p,
           title="Завантаженість процесора поядрово")


# ── memory-over-time: профіль пам'яті в часі ловить витік ────────────────────
# Ідея: миттєвий знімок не бачить витоку; лише крива вільної купи в часі
# показує монотонний спад, що колись дасть крах.
def fig_memory_over_time():
    W, H = 760, 380
    p = []
    ox, oy = 80, 300        # початок осей
    aw, ah = 600, 220
    # осі
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 34, "час роботи, години", size=11, color=MUTED))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">вільна купа</text>'
             % (ox - 50, oy - ah / 2, FONT, MUTED, ox - 50, oy - ah / 2))

    # здорова лінія — рівна
    y_h = oy - ah * 0.72
    p.append(line(ox + 4, y_h, ox + aw - 4, y_h, color=OK, sw=2.6))
    p.append(text(ox + aw - 4, y_h - 10, "здорова: рівна лінія", size=11, color=OK, bold=True, anchor="end"))

    # витік — монотонний спад до нуля
    import math
    pts = []
    for i in range(0, 61):
        t = i / 60.0
        y = (oy - ah * 0.66) + ah * 0.62 * t      # спадає (y росте вниз)
        x = ox + 4 + (aw - 8) * t
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), HOT))
    p.append(text(ox + aw * 0.5, oy - ah * 0.30, "витік: монотонно тане", size=11, color=HOT, bold=True))
    # точка краху
    p.append(circle(ox + aw - 4, oy - ah * 0.04, 5, fill=HOT, stroke=HOT))
    p.append(text(ox + aw - 4, oy - ah * 0.04 - 12, "крах: malloc → NULL", size=10.5, color=HOT, bold=True, anchor="end"))

    p.append(text(W / 2, 350, "миттєвий знімок «вільно 120 КБ» цього спаду не бачить — лише крива в часі",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "memory-over-time.svg"), W, H, *p,
           title="Профіль пам'яті в часі ловить витік")


# ── observer-effect: важкий вимір сам спотворює систему ──────────────────────
# Ідея: дешевий лічильник тайминг не чіпає; рясний друк блокує задачу й роздуває
# виміряний час у десятки разів — профіль бреше.
def fig_observer_effect():
    W, H = 800, 360
    p = []
    # ліворуч — легкий вимір
    lx, lw = 50, 330
    p.append(rect(lx, 80, lw, 230, fill="#eafaf1", stroke=OK, sw=2, rx=12))
    lcx = lx + lw / 2
    p.append(text(lcx, 110, "ЛЕГКИЙ ВИМІР", size=14, color=OK, bold=True))
    p.append(text(lcx, 134, "лічильник тактів (DWT)", size=11, color=INK))
    # справжня ділянка
    p.append(rect(lcx - 70, 156, 140, 34, fill="#fff", stroke=OK, sw=1.6, rx=6))
    p.append(text(lcx, 178, "ділянка 50 мкс", size=11, color=INK, bold=True))
    p.append(text(lcx, 220, "Δt = 50 мкс", size=14, color=OK, bold=True))
    p.append(text(lcx, 244, "тайминг не змінено", size=11, color=OK))
    p.append(text(lcx, 286, "вимір ≈ реальність", size=12, color=INK, bold=True))

    # праворуч — важкий вимір
    rx_, rw = 420, 330
    p.append(rect(rx_, 80, rw, 230, fill="#fbecec", stroke=HOT, sw=2, rx=12))
    rcx = rx_ + rw / 2
    p.append(text(rcx, 110, "ВАЖКИЙ ВИМІР", size=14, color=HOT, bold=True))
    p.append(text(rcx, 134, "printf на кожній ітерації", size=11, color=INK))
    p.append(rect(rcx - 70, 156, 140, 34, fill="#fff", stroke=HOT, sw=1.6, rx=6))
    p.append(text(rcx, 178, "та сама 50 мкс", size=11, color=INK, bold=True))
    # роздутий блок
    p.append(rect(rcx - 110, 198, 220, 28, fill="#f6cccc", stroke=HOT, sw=1.4, rx=6))
    p.append(text(rcx, 217, "+ UART блокує ~2 мс", size=11, color=HOT, bold=True))
    p.append(text(rcx, 252, "вимір = 2 мс", size=14, color=HOT, bold=True))
    p.append(text(rcx, 274, "роздуття у 40 разів", size=11, color=HOT, bold=True))
    p.append(text(rcx, 296, "профіль бреше", size=12, color=HOT, bold=True))

    p.append(text(W / 2, 340, "ефект спостерігача: вимір сам споживає ресурс, який міряє",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, "observer-effect.svg"), W, H, *p,
           title="Ефект спостерігача у профілюванні")


# ── optimize-loop: замкнена петля чотирьох кроків ────────────────────────────
# Ідея: сенс профілю — підґрунтя для дій; виміряй → знайди ОДНУ точку → виправ
# лише її → переміряй; не чіпай того, що й так у бюджеті.
def fig_optimize_loop():
    W, H = 640, 460
    p = []
    cx, cy, r = W / 2, 250, 150
    import math
    steps = [
        ("ВИМІРЯЙ", "профіль CPU\nі пам'яті", COOL),
        ("ЗНАЙДИ", "рівно ОДНУ\nгарячу точку", HOT),
        ("ВИПРАВ", "торкнися лише\nцієї точки", OK),
        ("ПЕРЕМІРЯЙ", "стало краще?\nне зламалось?", "#caa24a"),
    ]
    pos = []
    for i in range(4):
        a = -math.pi / 2 + i * math.pi / 2
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        pos.append((x, y))
    # стрілки по колу
    for i in range(4):
        x1, y1 = pos[i]
        x2, y2 = pos[(i + 1) % 4]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # трохи підтягнути кінці до країв вузлів
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        p.append(arrow(x1 + ux * 60, y1 + uy * 38, x2 - ux * 60, y2 - uy * 38, color=MUTED, sw=2))
    # вузли
    for (x, y), (title, sub, col) in zip(pos, steps):
        p.append(circle(x, y, 56, fill="#fff", stroke=col, sw=2.6))
        p.append(text(x, y - 8, title, size=13, color=col, bold=True))
        p.append(mtext(x, y + 12, sub, size=9.5, color=INK, lh=1.25))
    # центр
    p.append(text(cx, cy + 4, "цикл", size=13, color=MUTED, bold=True))
    p.append(text(cx, cy + 22, "оптимізації", size=13, color=MUTED, bold=True))
    # застереження збоку
    p.append(rect(40, 408, W - 80, 36, fill="#eafaf1", stroke=OK, sw=1.6, rx=8))
    p.append(text(cx, 431, "не чіпай того, що й так у бюджеті із запасом",
                  size=12, color=OK, bold=True))
    render(os.path.join(OUT, "optimize-loop.svg"), W, H, *p,
           title="Замкнена петля оптимізації")


# ── flame-graph: як зі стеків-знімків виростає полум'я (для -d.md) ────────────
# Ідея: кожен знімок семплінгу — це стек викликів; однакові кадри сусідніх
# знімків зливаються в один широкий прямокутник. Ширина = частка часу, не час.
def fig_flame_graph():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 54, "ширина кадру = частка знімків, де він був у стеку (не час!)",
                  size=11.5, color=MUTED, italic=True))
    x0, y0 = 60, 320
    fullw = 640
    rh = 30
    gap = 3

    def frame(x, w, level, label, col):
        y = y0 - (level + 1) * (rh + gap)
        p.append(rect(x, y, w, rh, fill=col, stroke="#ffffff", sw=1.2, rx=3))
        fs = fit_font(label, w - 6, 11, bold=False)
        if fs >= 8:
            p.append(text(x + w / 2, y + rh / 2 + 4, label, size=fs, color="#1a1a1a"))

    warm = ["#f6c453", "#f0a04b", "#e9853b", "#e06c2d", "#d65420"]
    # рівень 0 — корінь (увесь час)
    frame(x0, fullw, 0, "main → loop", warm[0])
    # рівень 1 — два піддерева
    frame(x0, fullw * 0.62, 1, "read_sensor()", warm[1])
    frame(x0 + fullw * 0.62, fullw * 0.38, 1, "send_packet()", warm[1])
    # рівень 2
    frame(x0, fullw * 0.45, 2, "i2c_xfer()  ← гаряче", warm[3])
    frame(x0 + fullw * 0.45, fullw * 0.17, 2, "filter()", warm[2])
    frame(x0 + fullw * 0.62, fullw * 0.24, 2, "crc()", warm[2])
    frame(x0 + fullw * 0.62 + fullw * 0.24, fullw * 0.14, 2, "tx()", warm[2])
    # рівень 3 — найгарячіший лист
    frame(x0, fullw * 0.45, 3, "i2c_wait_ack()  ← найширший лист", warm[4])

    # вісь
    p.append(line(x0, y0, x0 + fullw, y0, color=INK, sw=1.4))
    p.append(text(x0, y0 + 18, "0%", size=10, color=MUTED, anchor="start"))
    p.append(text(x0 + fullw, y0 + 18, "100% знімків", size=10, color=MUTED, anchor="end"))
    p.append(text(W / 2, 358, "найширший лист угорі — там процесор буває найчастіше",
                  size=11, color=HOT, bold=True))
    render(os.path.join(OUT, "flame-graph.svg"), W, H, *p,
           title="Полум'яний графік: стеки-знімки, злиті в кадри")


# ── amdahl: межа прискорення (для -d.md) ─────────────────────────────────────
# Ідея: прискорюємо частку p коду; навіть за нескінченного прискорення цієї
# частки загальний виграш упирається в стелю 1/(1−p).
def fig_amdahl():
    W, H = 740, 420
    p = []
    ox, oy = 90, 340
    aw, ah = 580, 270
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 36, "у скільки разів прискорено гарячу частину (s)",
                  size=11, color=MUTED))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">загальне прискорення S</text>'
             % (ox - 56, oy - ah / 2, FONT, MUTED, ox - 56, oy - ah / 2))

    import math
    # три криві для різних p
    curves = [(0.95, HOT, "p = 0.95 → стеля ×20"),
              (0.75, "#caa24a", "p = 0.75 → стеля ×4"),
              (0.50, COOL, "p = 0.50 → стеля ×2")]
    s_max = 64.0
    S_max_plot = 22.0  # верх осі по S
    for pf, col, lab in curves:
        ceil = 1.0 / (1.0 - pf)
        pts = []
        for k in range(0, 121):
            s = 1.0 + (s_max - 1.0) * (k / 120.0)
            S = 1.0 / ((1.0 - pf) + pf / s)
            x = ox + aw * (math.log(s) / math.log(s_max))   # лог-шкала по s
            y = oy - ah * (S / S_max_plot)
            pts.append("%.1f,%.1f" % (x, y))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), col))
        # пунктир-стеля
        yc = oy - ah * (min(ceil, S_max_plot) / S_max_plot)
        p.append(line(ox, yc, ox + aw, yc, color=col, sw=1.2, dash="5,4"))
        p.append(text(ox + aw - 4, yc - 6, lab, size=10.5, color=col, bold=True, anchor="end"))

    # позначки осі s (лог)
    for s in [1, 2, 4, 8, 16, 32, 64]:
        x = ox + aw * (math.log(s) / math.log(s_max))
        p.append(line(x, oy, x, oy + 5, color=INK, sw=1.2))
        p.append(text(x, oy + 19, "×%d" % s, size=9.5, color=MUTED))

    p.append(text(W / 2, 384, "S = 1 / ((1−p) + p/s) → за s→∞ упирається у стелю 1/(1−p)",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "amdahl.svg"), W, H, *p,
           title="Закон Амдала: межа прискорення")


if __name__ == "__main__":
    fig_two_budgets()
    fig_sampling_vs_instr()
    fig_cpu_load()
    fig_memory_over_time()
    fig_observer_effect()
    fig_optimize_loop()
    fig_flame_graph()
    fig_amdahl()
    print("OK: 8 figures ->", OUT)
