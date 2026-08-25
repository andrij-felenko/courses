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


# Фігури про STA (paths-graph, slack-timeline, routing-dominates) переїхали
# до окремої статті book/electronics/digital/static-timing-analysis/ разом
# зі своїм figs.py — їхній генератор тепер там.


if __name__ == "__main__":
    fig_path()
    fig_fmax()
    fig_slack()
    fig_pipeline()
    print("OK: 4 figures ->", OUT)
