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


# ── 1. path: шлях від тригера до тригера ─────────────────────────────────────
# Ідея: один «перегін» синхронної схеми — три відрізки часу (t_cq, t_logic,
# t_setup) між двома тригерами під спільним тактом; їхня сума на найдовшому
# перегоні і є критичний шлях.
def fig_path():
    W, H = 720, 300
    midy = 150
    out = [text(W / 2, 34, "Шлях від тригера до тригера за один період такту", size=16, bold=True)]
    # формула зверху
    out.append(text(W / 2, 70, "критичний шлях = t_cq + t_logic + t_setup", size=13, bold=True, color=INK))
    # регістр-джерело
    out.append(rect(70, midy - 28, 86, 56, fill="#eaf0fd", stroke=NEG, sw=1.8))
    out.append(text(113, midy - 4, "тригер", size=11, color=NEG, bold=True))
    out.append(text(113, midy + 14, "джерело", size=10, color=NEG))
    # стрілка t_cq
    out.append(amark(156, midy, 226, midy))
    out.append(text(191, midy - 10, "t_cq", size=10, color=MUTED))
    # комбінаційна логіка
    out.append(rect(226, midy - 28, 268, 56, fill="#eafaf0", stroke=FIELD, sw=1.8))
    out.append(text(360, midy - 4, "комбінаційна логіка", size=12, color=FIELD, bold=True))
    out.append(text(360, midy + 15, "(кілька LUT + дроти між ними)", size=10, color=MUTED))
    # стрілка t_logic
    out.append(amark(494, midy, 564, midy))
    out.append(text(529, midy - 10, "t_logic", size=10, color=MUTED))
    # регістр-приймач
    out.append(rect(564, midy - 28, 86, 56, fill="#eaf0fd", stroke=NEG, sw=1.8))
    out.append(text(607, midy - 4, "тригер", size=11, color=NEG, bold=True))
    out.append(text(607, midy + 14, "приймач", size=10, color=NEG))
    # спільний такт
    cy = midy + 70
    out.append(line(113, midy + 28, 113, cy, color=POS, sw=1.5))
    out.append(line(607, midy + 28, 607, cy, color=POS, sw=1.5))
    out.append(line(113, cy, 607, cy, color=POS, sw=1.6))
    out.append(text(360, cy + 18, "спільний такт: обидва тригери ловлять один фронт", size=11, color=POS, bold=True))
    # підсумок
    b, bw, bh = textbox(W / 2, H - 32,
                        "За один період сигнал мусить вийти (t_cq), пройти логіку (t_logic) і встигнути на setup —\nнайдовший такий перегін у дизайні і є критичний шлях.",
                        size=11, fill="#eafaf0", stroke=FIELD)
    out.append(b)
    save(os.path.join(OUT, "path.svg"), W, H, *out)


# ── 2. fmax: критичний шлях → максимальна частота ────────────────────────────
# Ідея: період не коротший за критичний шлях ⇒ Fmax = 1/шлях; числовий приклад.
def fig_fmax():
    W, H = 720, 300
    out = [text(W / 2, 34, "Від критичного шляху до максимальної частоти", size=16, bold=True)]
    out.append(fitbox(90, 70, W - 180, 50,
                      "T_такт  ≥  t_cq + t_logic + t_setup  =  критичний шлях",
                      size=14, fill="#f0f1f4", stroke=INK, bold=True))
    out.append(amark(W / 2, 124, W / 2, 152))
    out.append(fitbox(200, 156, W - 400, 46, "Fmax = 1 / критичний шлях",
                      size=15, fill="#fff6e6", stroke="#b8860b", color="#8a6400", bold=True))
    out.append(fitbox(90, 224, W - 180, 46,
                      "Приклад: критичний шлях 8 нс  →  Fmax = 1 / 8 нс = 125 МГц",
                      size=12, fill="#eafaf0", stroke=FIELD, bold=True))
    out.append(text(W / 2, H - 14, "коротший шлях (менше логіки між тригерами) → вища Fmax; довший → нижча",
                    size=11, color=MUTED, italic=True))
    save(os.path.join(OUT, "fmax.svg"), W, H, *out)


# ── 3. slack: запас або борг часу ────────────────────────────────────────────
# Ідея: slack = період − потрібний час; знак вирішує долю дизайну. Дві смуги
# (A додатний, B від'ємний) на спільній шкалі періоду.
def fig_slack():
    W, H = 720, 320
    out = [text(W / 2, 34, "Slack: запас або борг часу проти заданого періоду", size=16, bold=True)]
    x0 = 150
    full = 470          # 470 px = 10 нс ⇒ 47 px/нс
    ppn = full / 10.0
    # шкала періоду (ціль 100 МГц = 10 нс)
    ytop = 78
    out.append(text(90, ytop + 4, "ціль 100 МГц", size=11, color=INK, bold=True))
    out.append(line(x0, ytop, x0 + full, ytop, color=MUTED, sw=2))
    out.append(line(x0, ytop - 6, x0, ytop + 6, color=MUTED, sw=2))
    out.append(line(x0 + full, ytop - 6, x0 + full, ytop + 6, color=MUTED, sw=2))
    out.append(text(x0 + full + 34, ytop + 4, "10 нс", size=10, color=MUTED, bold=True))
    # шлях A = 8 нс → slack +2
    ya = 128
    out.append(text(90, ya + 4, "шлях A", size=11, color=FIELD, bold=True))
    out.append(rect(x0, ya - 13, 8 * ppn, 26, fill="#eafaf0", stroke=FIELD, sw=1.6))
    out.append(text(x0 + 4 * ppn, ya + 5, "8 нс", size=10, color=FIELD, bold=True))
    out.append(rect(x0 + 8 * ppn, ya - 13, 2 * ppn, 26, fill="#eef0f2", stroke=MUTED, sw=1.2))
    out.append(text(x0 + full + 34, ya + 4, "slack +2 нс", size=11, color=FIELD, bold=True))
    # шлях B = 12 нс → slack −2
    yb = 184
    out.append(text(90, yb + 4, "шлях B", size=11, color=POS, bold=True))
    out.append(rect(x0, yb - 13, 12 * ppn, 26, fill="#fdecea", stroke=POS, sw=1.6))
    out.append(text(x0 + 6 * ppn, yb + 5, "12 нс (задовгий)", size=10, color=POS, bold=True))
    out.append(line(x0 + full, yb - 18, x0 + full, yb + 18, color=INK, sw=1.4, dash="3 3"))
    out.append(text(x0 + full + 34, yb + 4, "slack −2 нс", size=11, color=POS, bold=True))
    # підсумок
    b, bw, bh = textbox(W / 2, H - 40,
                        "slack = період такту − потрібний час шляху.\nДодатний — є запас; нуль — на межі; від'ємний — таймінг провалено.\nПерший обов'язок після трасування — щоб найгірший slack був невід'ємний.",
                        size=11, fill="#eafaf0", stroke=FIELD)
    out.append(b)
    save(os.path.join(OUT, "slack.svg"), W, H, *out)


# ── 4. pipeline: конвеєр розрізає довгий шлях ────────────────────────────────
# Ідея: регістр посередині ділить логіку навпіл ⇒ кожна половина коротша ⇒
# Fmax вдвічі вища, ціною +1 такту латентності.
def fig_pipeline():
    W, H = 720, 360
    out = [text(W / 2, 32, "Конвеєр розрізає довгий шлях регістром", size=16, bold=True)]

    def reg(x, y):
        return rect(x, y, 46, 42, fill="#eaf0fd", stroke=NEG, sw=1.8) + text(x + 23, y + 26, "тр.", size=10, color=NEG, bold=True)

    # БУЛО
    out.append(text(90, 70, "Було: уся логіка між двома тригерами", size=12, color=POS, bold=True))
    yr = 82
    out.append(reg(90, yr))
    out.append(rect(146, yr, 478, 42, fill="#fdecea", stroke=POS, sw=1.6))
    out.append(text(146 + 239, yr + 26, "довга логіка — 12 нс", size=11, color=POS, bold=True))
    out.append(reg(624, yr))
    out.append(text(W / 2, yr + 66, "критичний шлях ≈ 12 нс  →  Fmax ≈ 83 МГц", size=11, color=POS, bold=True))

    # СТАЛО
    out.append(text(90, 206, "Стало: посередині додано регістр (конвеєрний щабель)", size=12, color=FIELD, bold=True))
    yr2 = 218
    out.append(reg(90, yr2))
    out.append(rect(146, yr2, 218, 42, fill="#eafaf0", stroke=FIELD, sw=1.6))
    out.append(text(146 + 109, yr2 + 26, "пів-логіки — 6 нс", size=10, color=FIELD, bold=True))
    out.append(rect(364, yr2, 46, 42, fill="#eaf0fd", stroke=NEG, sw=2.4))
    out.append(text(364 + 23, yr2 + 26, "тр.", size=10, color=NEG, bold=True))
    out.append(text(364 + 23, yr2 - 6, "новий", size=9, color=NEG, bold=True))
    out.append(rect(410, yr2, 214, 42, fill="#eafaf0", stroke=FIELD, sw=1.6))
    out.append(text(410 + 107, yr2 + 26, "пів-логіки — 6 нс", size=10, color=FIELD, bold=True))
    out.append(reg(624, yr2))
    out.append(text(W / 2, yr2 + 66, "критичний шлях ≈ 6 нс  →  Fmax ≈ 166 МГц (удвічі вище)", size=11, color=FIELD, bold=True))

    b, bw, bh = textbox(W / 2, H - 28,
                        "Плата — зайвий такт латентності: результат на такт пізніше,\nале потік даних іде вдвічі швидше.",
                        size=11, fill="#eafaf0", stroke=FIELD)
    out.append(b)
    save(os.path.join(OUT, "pipeline.svg"), W, H, *out)


# ── 5. paths-graph (math): дизайн — це багато шляхів, критичний — найдовший ───
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


# ── 6. slack-timeline (math): slack = required − arrival на осі приймача ──────
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


# ── 7. routing-dominates (math): маршрут переважує логіку й гуляє між прогонами
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
    fig_path()
    fig_fmax()
    fig_slack()
    fig_pipeline()
    fig_paths_graph()
    fig_slack_timeline()
    fig_routing_dominates()
    print("OK: 7 figures ->", OUT)
