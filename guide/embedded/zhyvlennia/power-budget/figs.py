# -*- coding: utf-8 -*-
"""Фігури до теми «Бюджет потужності пристрою».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── demand-vs-source: попит проти спроможності джерела із запасом ──────────────
# Ідея бюджету в одній картинці. Зліва — стовпчик попиту, складений зі споживачів
# (сума знизу вгору). Праворуч — стеля джерела й зона запасу під нею. Якщо верх
# попиту нижчий за лінію запасу — бюджет сходиться; вище стелі — не влазить.
def fig_demand_vs_source():
    W, H = 720, 420
    p = []
    axis_y = 350
    top_y = 70
    full_h = axis_y - top_y

    src_max = 2500.0          # стеля джерела, мВт (умовний приклад)
    headroom_frac = 0.80      # практичний запас: вантажимо не вище 80 % стелі

    def yh(mw):               # висота в пікселях для мВт
        return full_h * mw / src_max

    # ── правий стовпчик: джерело зі стелею й зоною запасу ──
    sx, sw = 540, 130
    # повна стеля (контур)
    p.append(rect(sx - sw / 2, top_y, sw, full_h, fill="#fbfbfc", stroke=MUTED, sw=1.4, rx=4))
    # «заборонена» верхня смуга запасу (від 80 % до 100 %)
    hl_y = axis_y - yh(src_max * headroom_frac)
    p.append(rect(sx - sw / 2, top_y, sw, hl_y - top_y, fill="#fdecea", stroke="none", sw=0, rx=0))
    p.append(line(sx - sw / 2, hl_y, sx + sw / 2, hl_y, color=POS, sw=1.8, dash="6 4"))
    p.append(text(sx, top_y - 30, "Джерело", size=13, color=INK, bold=True))
    p.append(text(sx, top_y - 12, "стеля 2500 мВт", size=11, color=MUTED))
    p.append(text(sx, hl_y - 8, "лінія запасу (80 %) = 2000 мВт", size=10, color=POS))
    p.append(text(sx, top_y + (hl_y - top_y) / 2 + 4, "запас", size=11, color=POS))

    # ── лівий стовпчик: попит, складений зі споживачів ──
    dx, dw = 220, 130
    consumers = [
        ("МК + радіо\n(пік TX)", 1200.0, POS),
        ("давачі", 250.0, "#e67e22"),
        ("дисплей", 180.0, "#8a5fb0"),
        ("втрати\nперетворення", 220.0, MUTED),
    ]
    cur = axis_y
    for lab, mw, col in consumers:
        h = yh(mw)
        fill = {POS: "#fdecea", "#e67e22": "#fdf2e9", "#8a5fb0": "#f2ecf8",
                MUTED: "#eef0f2"}[col]
        p.append(rect(dx - dw / 2, cur - h, dw, h, fill=fill, stroke=col, sw=1.6, rx=3))
        if h > 26:
            p.append(mtext(dx, cur - h / 2 + 3, lab, size=9, color=INK))
        cur -= h
    demand_top = cur
    total = sum(mw for _, mw, _ in consumers)
    p.append(text(dx, top_y - 30, "Попит", size=13, color=INK, bold=True))
    p.append(text(dx, demand_top - 10, "Σ = %d мВт" % int(total), size=12, color=INK, bold=True))

    # ── вердикт: попит нижчий за лінію запасу → сходиться ──
    p.append(line(dx + dw / 2, demand_top, sx - sw / 2, demand_top, color=FIELD, sw=1.4, dash="4 3"))
    b, _, _ = textbox((dx + sx) / 2, demand_top - 34, "1850 < 2000\nсходиться ✓", size=11,
                      bold=True, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.6, pad=8)
    p.append(b)

    p.append(line(150, axis_y, 620, axis_y, color=INK, sw=1.6))
    p.append(text(W / 2, H - 14,
                  "бюджет = скласти попит знизу вгору й звірити з лінією запасу джерела",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "demand-vs-source.svg"), W, H, *p,
           title="Бюджет потужності: попит проти спроможності джерела")


# ── reflect-through-converter: попит навантаження «роздувається» втратами ──────
# Ідея: на вході джерела ти платиш не за корисну потужність, а за неї поділену
# на ККД. Чим нижчий ККД ланки, тим більший струм треба джерелу. Показуємо
# однакове корисне навантаження за двома перетворювачами різного ККД.
def fig_reflect():
    W, H = 720, 360
    p = []
    yL = 110          # верхній ряд: лінійний / низький ККД
    yS = 250          # нижній ряд: імпульсний / високий ККД

    def chain(y, conv_lab, eff, p_out, in_col):
        out = []
        p_in = p_out / eff
        # блок джерела (вхід)
        bx = 120
        b, w1, _ = textbox(bx, y, "джерело\n%d мВт" % round(p_in), size=11, bold=True,
                           fill="#fdecea" if in_col == POS else "#fff3e0",
                           stroke=in_col, sw=1.6, pad=9)
        out.append(b)
        # перетворювач
        cx = 360
        b, w2, _ = textbox(cx, y, conv_lab, size=11, fill=FILL, stroke=LINE, sw=1.6, pad=10)
        out.append(b)
        # навантаження (вихід)
        lx = 600
        b, w3, _ = textbox(lx, y, "навантаження\n%d мВт" % round(p_out), size=11, bold=True,
                           fill="#eafaf1", stroke=FIELD, sw=1.6, pad=9)
        out.append(b)
        # стрілки
        out.append(arrow(bx + w1 / 2 + 4, y, cx - w2 / 2 - 4, y, color=in_col, sw=2.0))
        out.append(arrow(cx + w2 / 2 + 4, y, lx - w3 / 2 - 4, y, color=FIELD, sw=2.0))
        # підпис втрат над ланкою
        loss = p_in - p_out
        out.append(text((bx + cx) / 2, y - 26, "ККД %d %% → +%d мВт у тепло" % (round(eff * 100), round(loss)),
                        size=10, color=MUTED))
        return out

    p += chain(yL, "лінійний\nстабілізатор", 0.45, 500.0, POS)
    p += chain(yS, "імпульсний\nперетворювач", 0.90, 500.0, "#e67e22")

    # підпис різниці входів
    b, _, _ = textbox(W / 2, 320, "те саме навантаження 500 мВт — а джерело бачить 1111 мВт проти 556 мВт",
                      size=11, bold=True, color=INK, fill="#fffbe6", stroke="#e0c44a", sw=1.4, pad=8)
    p.append(b)

    render(os.path.join(OUT, "reflect-through-converter.svg"), W, H, *p,
           title="Попит навантаження відбивається на вхід, поділений на ККД")


# ── peak-vs-worstcase: що сумувати — типове, середнє чи найгірше ───────────────
# Ідея: джерело сидить під одночасним піком, а батарея садиться середнім. Три
# смуги однієї системи: типова сума, найгірша одночасна сума (для джерела),
# і середня за цикл (для батареї). Сплутати їх — типова помилка бюджету.
def fig_peak_vs_worstcase():
    W, H = 720, 380
    p = []
    axis_y = 300
    top_y = 70
    full_h = axis_y - top_y
    scale = 2400.0            # верх шкали, мВт

    def yh(mw):
        return full_h * mw / scale

    bars = [
        ("Типове\n(звичний режим)", 900.0, MUTED,
         "те, що бачиш на столі\nщодня"),
        ("Найгірше одночасне\n(сайзинг джерела)", 1900.0, POS,
         "усі піки збіглися:\nза цим сайзимо джерело"),
        ("Середнє за цикл\n(життя батареї)", 140.0, FIELD,
         "розмазано по часу:\nза цим рахуємо автономність"),
    ]
    n = len(bars)
    x0 = 120
    slot = (W - 2 * x0) / n
    bw = slot * 0.42
    for i, (lab, mw, col, note) in enumerate(bars):
        cx = x0 + slot * (i + 0.5)
        h = yh(mw)
        fill = {MUTED: "#eef0f2", POS: "#fdecea", FIELD: "#eafaf1"}[col]
        p.append(rect(cx - bw / 2, axis_y - h, bw, h, fill=fill, stroke=col, sw=1.8, rx=3))
        p.append(text(cx, axis_y - h - 10, "%d мВт" % int(mw), size=12, color=col, bold=True))
        p.append(mtext(cx, axis_y + 20, lab, size=10, color=INK, bold=True))
        p.append(mtext(cx, axis_y + 50, note, size=9, color=MUTED))

    p.append(line(x0 - 10, axis_y, W - x0 + 10, axis_y, color=INK, sw=1.6))
    p.append(text(W / 2, H - 12,
                  "джерело сайзимо за найгіршим одночасним; батарею — за середнім; типове не годиться ні там, ні там",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "peak-vs-worstcase.svg"), W, H, *p,
           title="Три різні суми однієї системи — і для чого кожна")


if __name__ == "__main__":
    fig_demand_vs_source()
    fig_reflect()
    fig_peak_vs_worstcase()
    print("OK: figures written to", OUT)
