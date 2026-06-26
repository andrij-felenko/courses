# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = "#0f172a"   # темне тло
ACC1 = "#0ea5e9"   # блакитна лінія (платформа з пам'яттю)
ACC2 = "#9333ea"   # фіолетова лінія (прискорювач)


# ── roofline: дах із двох ліній (пам'ять і обчислення), точки платформ ─────────
# Ідея: продуктивність обмежена МЕНШИМ з двох дахів — похилого (пам'ять: I·β)
# і горизонтального (обчислення: пік). Зліва від злому виграє пам'ять, справа —
# обчислення. Точки конкретних платформ лягають під дах і показують,
# хто впирається в пам'ять, а хто — в лічбу.

def fig_roofline():
    W, H = 760, 460
    p = []
    # координатна рамка
    ox, oy = 90.0, 380.0          # початок осей (лівий низ)
    pw, ph = 600.0, 310.0         # робоче поле
    p.append(rect(ox, oy - ph, pw, ph, fill="#fbfdff", stroke=INK, sw=1.4, rx=8))

    # логарифмічні осі: X = arithmetic intensity (ops/байт), Y = продуктивність (ops/с)
    xlo, xhi = 0.1, 1000.0        # ops/байт
    ylo, yhi = 1e9, 1e13          # ops/с (1 GFLOP/s .. 10 TFLOP/s)

    def X(ix):
        return ox + pw * (math.log10(ix) - math.log10(xlo)) / (math.log10(xhi) - math.log10(xlo))

    def Y(perf):
        return oy - ph * (math.log10(perf) - math.log10(ylo)) / (math.log10(yhi) - math.log10(ylo))

    # сітка + підписи осей (степені десятки)
    for ix in (0.1, 1, 10, 100, 1000):
        gx = X(ix)
        p.append(line(gx, oy, gx, oy - ph, color="#e5e9ef", sw=1.0))
        lab = {0.1: "0.1", 1: "1", 10: "10", 100: "100", 1000: "1000"}[ix]
        p.append(text(gx, oy + 18, lab, size=11, color=MUTED))
    ypow = [(1e9, "10⁹"), (1e10, "10¹⁰"), (1e11, "10¹¹"), (1e12, "10¹²"), (1e13, "10¹³")]
    for yv, lab in ypow:
        gy = Y(yv)
        p.append(line(ox, gy, ox + pw, gy, color="#e5e9ef", sw=1.0))
        p.append(text(ox - 10, gy + 4, lab, size=11, color=MUTED, anchor="end"))

    p.append(text(ox + pw / 2, oy + 38, "арифметична інтенсивність  (операцій / байт)", size=12, color=INK))
    p.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">продуктивність (операцій / с)</text>'
             % (28, oy - ph / 2, FONT, INK, 28, oy - ph / 2))

    # ── дах прискорювача (фіолетовий): пік вищий, bandwidth теж вищий ──
    peak2 = 4e12         # 4 TOPS
    bw2 = 25e9           # 25 ГБ/с (LPDDR4)
    ridge2 = peak2 / bw2  # ops/байт у зломі
    # похила частина: perf = I * bw  →  від xlo до ridge
    p.append(line(X(xlo), Y(xlo * bw2), X(ridge2), Y(peak2), color=ACC2, sw=2.6))
    p.append(line(X(ridge2), Y(peak2), X(xhi), Y(peak2), color=ACC2, sw=2.6))
    p.append(text(X(xhi) - 6, Y(peak2) - 8, "прискорювач  4 TOPS", size=11, color=ACC2, bold=True, anchor="end"))

    # ── дах CPU/одноплатника (блакитний): пік нижчий, bandwidth нижчий ──
    peak1 = 5e10         # ~50 GFLOP/s
    bw1 = 8e9            # ~8 ГБ/с
    ridge1 = peak1 / bw1
    p.append(line(X(xlo), Y(xlo * bw1), X(ridge1), Y(peak1), color=ACC1, sw=2.6))
    p.append(line(X(ridge1), Y(peak1), X(xhi), Y(peak1), color=ACC1, sw=2.6))
    p.append(text(X(xhi) - 6, Y(peak1) - 8, "одноплатник CPU", size=11, color=ACC1, bold=True, anchor="end"))

    # точки операцій (їхня арифметична інтенсивність)
    def dot(ix, perf, lab, dx=8, dy=-8, anchor="start", col=INK):
        gx, gy = X(ix), Y(perf)
        out = circle(gx, gy, 4.5, fill=col, stroke=BG, sw=1.5)
        out += text(gx + dx, gy + dy, lab, size=10.5, color=col, anchor=anchor)
        return out

    # згортка добре переюзує дані (висока інтенсивність) → впирається в лічбу
    p.append(dot(120, peak2, "згортка 3×3", dx=-8, dy=16, anchor="end", col=ACC2))
    # поелементні операції (поріг, копія) — низька інтенсивність → впирається в пам'ять
    p.append(dot(0.5, 0.5 * bw1, "поріг / копія", dx=8, dy=-8, anchor="start", col=ACC1))
    # Собель — посередині
    p.append(dot(6, 6 * bw1, "Собель 3×3", dx=8, dy=18, anchor="start", col=INK))

    # вертикаль зламу — підпис «тут стає байдуже до пам'яті»
    p.append(line(X(ridge2), Y(peak2), X(ridge2), oy, color=ACC2, sw=1.0, dash="4 4"))

    # підписи зон
    p.append(text(X(0.3), Y(6e12), "впирається в ПАМ'ЯТЬ", size=11, color=NEG, bold=True))
    p.append(text(X(300), Y(1.6e9), "впирається в ЛІЧБУ", size=11, color=POS, bold=True, anchor="middle"))

    render(os.path.join(OUT, "roofline.svg"), W, H, *p,
           title="Дах продуктивності: пам'ять чи лічба")


# ── MACs: як набігає лічба згортки (W·H·C·K·K на вихідний канал) ───────────────
# Ідея: один вихідний піксель = K·K·C множень-додавань; помнож на W·H·(вих. канали)
# — і дрібна на вигляд згортка обертається мільярдами MAC. Стовпчики показують,
# як та сама операція дешевшає від зменшення кадру й каналів.

def fig_macs_breakdown():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 56, "Один вихідний піксель згортки 3×3:", size=13, color=INK))
    # формула в моноширинному вигляді через textbox
    b, bw, bh = textbox(W / 2, 92, "MAC = K · K · C  (множень-додавань)", size=13, bold=True,
                        fill="#eef6ff", stroke=ACC1)
    p.append(b)
    p.append(text(W / 2, 126, "× усі вихідні пікселі  ×  усі вихідні канали", size=12, color=MUTED))

    # стовпчики: та сама згортка на різних входах
    base = 300.0       # вісь стовпчиків (низ)
    items = [
        ("HD 720p\n3 канали", 1280 * 720 * 3 * 9 * 32, ACC2),
        ("VGA 640×480\n3 канали", 640 * 480 * 3 * 9 * 32, ACC1),
        ("QVGA 320×240\nсіре, 1 канал", 320 * 240 * 1 * 9 * 16, FIELD),
    ]
    maxv = max(v for _, v, _ in items)
    bx = 120.0
    bwid = 130.0
    gap = 70.0
    for lab, v, col in items:
        h = 150.0 * v / maxv
        y = base - h
        p.append(rect(bx, y, bwid, h, fill=col, stroke=INK, sw=1.2, rx=5))
        # число MAC у мільйонах
        mm = v / 1e6
        p.append(text(bx + bwid / 2, y - 10, "%.0f M MAC" % mm, size=11, color=INK, bold=True))
        p.append(mtext(bx + bwid / 2, base + 20, lab, size=10.5, color=MUTED))
        bx += bwid + gap

    p.append(line(100, base, 100 + 3 * bwid + 2 * gap + 20, base, color=INK, sw=1.4))
    p.append(text(W / 2, base + 66, "менший і сіріший кадр  →  у рази менше лічби", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "macs-breakdown.svg"), W, H, *p,
           title="Звідки набігають мільярди множень")


# ── квантування float32 → int8: діапазон ділять на 256 сходинок ───────────────
# Ідея: int8 кладе ту саму ось значень на 256 цілих сходинок із кроком (масштабом).
# Кожне значення округлюється до найближчої сходинки → дрібна похибка; зате вага
# важить учетверо менше й множиться цілими. Показуємо неперервну вісь зверху і
# 256 сходинок знизу зі стрілками округлення.

def fig_quant():
    W, H = 760, 360
    p = []
    ax = 90.0
    aw = 580.0
    # верх: неперервна float-вісь
    yf = 110.0
    p.append(line(ax, yf, ax + aw, yf, color=ACC1, sw=2.4))
    p.append(text(ax, yf - 18, "float32: неперервні значення активації", size=12, color=ACC1, bold=True, anchor="start"))
    p.append(text(ax - 6, yf + 5, "min", size=10.5, color=MUTED, anchor="end"))
    p.append(text(ax + aw + 6, yf + 5, "max", size=10.5, color=MUTED, anchor="start"))

    # низ: 256 цілих сходинок (малюємо рідше — кожну N-ту риску)
    yi = 230.0
    p.append(line(ax, yi, ax + aw, yi, color=ACC2, sw=2.4))
    p.append(text(ax, yi + 30, "int8: 256 цілих сходинок  (крок = масштаб S)", size=12, color=ACC2, bold=True, anchor="start"))
    nshow = 16
    for i in range(nshow + 1):
        gx = ax + aw * i / nshow
        p.append(line(gx, yi - 6, gx, yi + 6, color=ACC2, sw=1.2))
    p.append(text(ax - 6, yi + 5, "0", size=10.5, color=MUTED, anchor="end"))
    p.append(text(ax + aw + 6, yi + 5, "255", size=10.5, color=MUTED, anchor="start"))

    # три значення float → округлення до сходинки (стрілки вниз)
    for frac, lab in ((0.18, "v₁"), (0.52, "v₂"), (0.81, "v₃")):
        gx = ax + aw * frac
        # найближча сходинка
        step = round(frac * nshow) / nshow
        gxs = ax + aw * step
        p.append(circle(gx, yf, 4.5, fill=ACC1, stroke=BG, sw=1.5))
        p.append(arrow(gx, yf + 8, gxs, yi - 10, color=MUTED, sw=1.4))
        p.append(circle(gxs, yi, 4.5, fill=ACC2, stroke=BG, sw=1.5))
        p.append(text(gx, yf - 8, lab, size=10.5, color=ACC1))

    # формула масштабу
    b, bw2, bh2 = textbox(W / 2, 312, "q = round(v / S) + Z      S = (max − min) / 255",
                          size=12.5, bold=True, fill="#f6eefe", stroke=ACC2)
    p.append(b)

    render(os.path.join(OUT, "quantization.svg"), W, H, *p,
           title="Квантування float32 → int8")


# ── pipeline: затримки етапів бортового зору (Pi+Coral vs STM32) ───────────────
# Ідея: повна затримка «кадр → команда» складається з етапів; де саме вона осідає,
# залежить від платформи. У Pi+Coral важка нейромережа дешева (TPU), та додається
# копіювання й USB; на STM32 нейромережі нема — затримку дає класика на слабкому ядрі.
# Дві смуги в одному масштабі часу показують, де осідають мілісекунди.

def fig_pipeline():
    W, H = 780, 420
    p = []
    # часова шкала
    t0 = 70.0
    tw = 640.0
    tmax = 60.0   # мс на повну ширину
    p.append(line(t0, 360, t0 + tw, 360, color=INK, sw=1.4))
    for ms in range(0, int(tmax) + 1, 10):
        gx = t0 + tw * ms / tmax
        p.append(line(gx, 356, gx, 364, color=INK, sw=1.2))
        p.append(text(gx, 382, "%d мс" % ms, size=10.5, color=MUTED))

    stages = ["захоплення", "ROI", "класика", "нейромережа", "MAVLink"]
    colmap = [ACC1, FIELD, "#e08a1e", ACC2, NEG]

    def band(y, label, durs, note):
        out = [text(t0, y - 14, label, size=12, color=INK, bold=True, anchor="start")]
        x = t0
        for d, st, col in zip(durs, stages, colmap):
            w = tw * d / tmax
            out.append(rect(x, y, w, 34, fill=col, stroke=INK, sw=1.0, rx=4))
            # підпис етапу всередині — лише якщо смуга гарантовано вмістить 10px-напис;
            # інакше етап читається з легенди нижче (без дрібного шрифту)
            if w >= text_width(st, 10) + 10:
                out.append(text(x + w / 2, y + 22, st, size=10, color=INK))
            x += w
        total = sum(durs)
        out.append(text(x + 10, y + 22, "Σ ≈ %.0f мс" % total, size=11.5, color=INK, bold=True, anchor="start"))
        out.append(text(t0, y + 52, note, size=10, color=MUTED, anchor="start"))
        return out, total

    # Pi + Coral: захоплення 5, ROI 1, класика 2, нейромережа 8 (TPU!), MAVLink 1
    b1, _ = band(90, "Raspberry Pi + Coral TPU", [5, 1, 2, 8, 1],
                 "нейромережа дешева на TPU; час осідає в захопленні кадру й USB-обміні")
    p.extend(b1)

    # STM32: захоплення 8, ROI 2, класика 28, нейромережі нема (0), MAVLink 1
    b2, _ = band(210, "STM32 (без прискорювача)", [8, 2, 28, 0, 1],
                 "нейромережі нема; затримку дає класика на слабкому ядрі")
    p.extend(b2)

    # легенда
    lx = t0
    ly = 300
    for st, col in zip(stages, colmap):
        p.append(rect(lx, ly - 10, 14, 14, fill=col, stroke=INK, sw=1.0, rx=3))
        wlab = text_width(st, 10) + 24
        p.append(text(lx + 20, ly + 1, st, size=10, color=INK, anchor="start"))
        lx += wlab + 18

    render(os.path.join(OUT, "pipeline-latency.svg"), W, H, *p,
           title="Де осідають мілісекунди: етапи бортового зору")


if __name__ == "__main__":
    fig_roofline()
    fig_macs_breakdown()
    fig_quant()
    fig_pipeline()
    print("OK figs")
