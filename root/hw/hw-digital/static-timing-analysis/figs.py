# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні маркери-стрілки в кольорах схеми (svgkit дає лише чорну #arrow).
MARK = ('<defs>'
        '<marker id="aInk" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
        '<marker id="aPos" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
        '</defs>') % (INK, POS)


def amark(x1, y1, x2, y2, mid="aInk", color=INK, sw=1.8):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#%s)"/>' % (x1, y1, x2, y2, color, sw, mid))


def save(path, w, h, *frags):
    """render() зі svgkit, але з нашими кольоровими маркерами в defs."""
    head = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'font-family="%s"><rect width="%d" height="%d" fill="%s"/>' % (w, h, FONT, w, h, BG))
    parts = [head, MARK]
    parts.extend(f for f in frags if f)
    parts.append("</svg>")
    import io
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


# ── 1. paths-graph: дизайн — це багато шляхів, критичний — найдовший ──────────
def fig_paths_graph():
    W, H = 720, 340
    out = [text(W / 2, 32, "Дизайн — це тисячі шляхів; критичний — найдовший", size=16, bold=True)]
    # джерела зліва, приймачі справа, поле LUT посередині
    srcx, dstx = 80, 640
    ys = [90, 150, 210, 270]
    src = ["a", "b", "c", "d"]
    dst = ["p", "q", "r", "s"]
    for i, y in enumerate(ys):
        out.append(rect(srcx - 26, y - 16, 52, 32, fill="#eaf0fd", stroke=NEG, sw=1.5))
        out.append(text(srcx, y + 5, "тр. " + src[i], size=10, color=NEG, bold=True))
        out.append(rect(dstx - 26, y - 16, 52, 32, fill="#eaf0fd", stroke=NEG, sw=1.5))
        out.append(text(dstx, y + 5, "тр. " + dst[i], size=10, color=NEG, bold=True))
    out.append(text(srcx, 308, "джерела", size=10, color=MUTED))
    out.append(text(dstx, 308, "приймачі", size=10, color=MUTED))
    # поле LUT
    out.append(rect(220, 74, 280, 212, fill="#eafaf0", stroke=FIELD, sw=1.4))
    out.append(text(360, 92, "поле LUT + маршрутизація", size=11, color=FIELD, bold=True))
    for lx, ly in [(280, 130), (360, 175), (440, 130), (300, 235), (420, 235)]:
        out.append(rect(lx - 18, ly - 12, 36, 24, fill=BG, stroke=FIELD, sw=1.2))
        out.append(text(lx, ly + 4, "LUT", size=9, color=FIELD))
    # три сині (із запасом) + один червоний (критичний)
    paths = [(0, 0, NEG, "5.1 нс"), (1, 2, NEG, "8.7 нс"), (3, 3, NEG, "6.3 нс"), (2, 1, POS, "12.4 нс")]
    for si, di, col, lbl in paths:
        sw = 2.4 if col == POS else 1.5
        out.append(line(srcx + 26, ys[si], dstx - 26, ys[di], color=col, sw=sw))
    out.append(text(360, 262, "12.4 нс — критичний шлях", size=11, color=POS, bold=True))
    b, bw, bh = textbox(W / 2, H - 22,
                        "T_мін = найдовший шлях; решта стоять із запасом. Скільки б не було швидких шляхів,\nстелю частоти тримає один найповільніший.",
                        size=11, fill="#fdecea", stroke=POS)
    out.append(b)
    save(os.path.join(OUT, "paths-graph.svg"), W, H, *out)


# ── 2. slack-timeline: slack = required − arrival на осі приймача ─────────────
def fig_slack_timeline():
    W, H = 720, 360
    out = [text(W / 2, 30, "Запас = «коли треба» − «коли прийшло»", size=16, bold=True)]
    x0, full = 150, 430          # 430 px = 16 нс
    ppn = full / 16.0

    def lane(y, title, arr, slack_ok):
        col = FIELD if slack_ok else POS
        o = [text(90, y - 28, title, size=11, color=col, bold=True)]
        # вісь часу: фронт N .. фронт N+1 (період 16 нс)
        o.append(line(x0, y, x0 + full, y, color=MUTED, sw=1.5))
        o.append(line(x0, y - 8, x0, y + 8, color=INK, sw=2))
        o.append(line(x0 + full, y - 8, x0 + full, y + 8, color=INK, sw=2))
        o.append(text(x0, y + 22, "фронт N", size=9, color=MUTED))
        o.append(text(x0 + full, y + 22, "фронт N+1", size=9, color=MUTED))
        # required = 14 нс (фронт N+1 − setup 2)
        rq = x0 + 14 * ppn
        o.append(line(rq, y - 22, rq, y + 12, color="#b8860b", sw=1.6, dash="4 3"))
        o.append(text(rq, y - 26, "треба (14)", size=9, color="#8a6400", bold=True))
        # smuga arrival
        o.append(rect(x0, y - 12, arr * ppn, 12, fill="#eafaf0" if slack_ok else "#fdecea", stroke=col, sw=1.4))
        o.append(text(x0 + arr * ppn / 2, y - 2, "прийшло %.1f" % arr, size=9, color=col, bold=True))
        sign = "+2.5 нс" if slack_ok else "−2.2 нс"
        o.append(text(x0 + full + 4, y + 4, "slack " + sign, size=11, color=col, bold=True))
        return o

    out += lane(110, "приймач p — встигає", 11.5, True)
    out += lane(220, "приймач r — зрив (критичний)", 16.2, False)
    b, bw, bh = textbox(W / 2, H - 48,
                        "slack = required − arrival для кожного приймача;\nнайменший по всіх приймачах і є WNS. WNS ≥ 0 — дизайн тримає частоту.",
                        size=11, fill="#f0f1f4", stroke=INK)
    out.append(b)
    save(os.path.join(OUT, "slack-timeline.svg"), W, H, *out)


# ── 3. routing-dominates: маршрут переважує логіку й гуляє між прогонами ──────
def fig_routing_dominates():
    W, H = 720, 340
    out = [text(W / 2, 30, "У FPGA Fmax плаває: важить маршрут, не логіка", size=16, bold=True)]
    x0, ppn = 150, 26.0          # 26 px на 1 нс
    out.append(text(90, 60, "Розклад критичного шляху (нс):", size=11, color=INK, bold=True))
    rows = [("прогін A", 8.5, 16, "65 МГц"), ("прогін B", 6.0, 13, "77 МГц"), ("прогін C", 12.0, 19, "53 МГц")]
    base = 3.0   # clk→q + setup
    lutd = 4.0   # LUT
    y = 90
    for name, rt, T, fm in rows:
        out.append(text(90, y + 16, name, size=11, bold=True))
        seg = [(base, "#eaf0fd", NEG, "clk→q+su"), (lutd, "#eafaf0", FIELD, "LUT"), (rt, "#fdecea", POS, "маршрут")]
        cx = x0
        for val, fill, st, lbl in seg:
            w = val * ppn
            out.append(rect(cx, y, w, 30, fill=fill, stroke=st, sw=1.4))
            if w > 40:
                out.append(text(cx + w / 2, y + 19, lbl, size=9, color=st, bold=True))
            cx += w
        out.append(text(cx + 8, y + 19, "T=%d → f_max≈%s" % (T, fm), size=10, color=INK, bold=True))
        y += 52
    # вісь нс
    ay = y + 6
    out.append(line(x0, ay, x0 + 20 * ppn, ay, color=MUTED, sw=1.3))
    for nv in range(0, 21, 5):
        xx = x0 + nv * ppn
        out.append(line(xx, ay - 4, xx, ay + 4, color=MUTED, sw=1.2))
        out.append(text(xx, ay + 18, str(nv), size=9, color=MUTED))
    out.append(text(x0 + 20 * ppn + 16, ay + 4, "нс", size=10, color=MUTED))
    b, bw, bh = textbox(W / 2, H - 22,
                        "Той самий опис після іншого розміщення й трасування дає інший критичний шлях, а отже й f_max.\nРеальну стелю знає лише часовий аналіз ПІСЛЯ трасування.",
                        size=11, fill="#f0f1f4", stroke=INK)
    out.append(b)
    save(os.path.join(OUT, "routing-dominates.svg"), W, H, *out)


if __name__ == "__main__":
    fig_paths_graph()
    fig_slack_timeline()
    fig_routing_dominates()
    print("OK: 3 figures ->", OUT)
