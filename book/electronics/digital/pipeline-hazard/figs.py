# -*- coding: utf-8 -*-
"""Фігури до статті «Конфлікти конвеєра (дані, керування, ресурси)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def stage_block(x, cy, w, h, label, fill=FILL):
    """Комбінаційна ділянка (станція конвеєра) з підписом."""
    out = rect(x, cy - h / 2, w, h, fill=fill, stroke=LINE, sw=1.6, rx=8)
    out += text(x + w / 2, cy + 5, label, size=15, bold=True)
    return out


def reg(x, cy, h, label=None):
    """Регістр між ділянками — вузька засувка."""
    w = 12
    out = rect(x - w / 2, cy - h / 2, w, h, fill="#e9edf2", stroke=LINE, sw=1.5, rx=3)
    if label:
        out += text(x, cy - h / 2 - 8, label, size=11, color=MUTED)
    return out


# ── Фігура 1: три класи конфліктів на спільному конвеєрі ────────────────────
def fig_three():
    W, H = 760, 420
    els = []
    names = ["Вибірка", "Декод", "Викон", "Пам'ять", "Запис"]
    n = len(names)
    cy = 300
    bh = 62
    bw = 96
    gap = 34
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    xs = []
    for i, nm in enumerate(names):
        x = x0 + i * (bw + gap)
        xs.append(x)
        els.append(stage_block(x, cy, bw, bh, nm))
        # регістр перед ділянкою (крім першої)
        if i > 0:
            els.append(reg(x - gap / 2, cy, bh + 10))
        # стрілка потоку
        if i < n - 1:
            els.append(arrow(x + bw, cy, x + bw + gap, cy, color=MUTED, sw=1.6))
    els.append(text(W / 2, cy + bh / 2 + 34,
                    "спільний такт цокає всі регістри водночас — щотакту команда зсувається праворуч",
                    size=12, color=MUTED))

    # три «хмари» конфліктів над відповідними ділянками
    ex, dx, mx, wx = xs[0] + bw / 2, xs[2] + bw / 2, xs[3] + bw / 2, xs[4] + bw / 2

    b1, w1, h1 = textbox(dx + 20, 70, ["ДАНІ", "результат ще в дорозі,", "а наступний уже читає"],
                         size=12, bold=False, fill="#fdecea", stroke=POS, sw=1.8)
    els.append(b1)
    els.append(arrow(dx + 20, 70 + h1 / 2, dx, cy - bh / 2 - 4, color=POS, sw=1.8))

    b2, w2, h2 = textbox(mx + 40, 165, ["РЕСУРС", "дві команди хочуть", "той самий блок"],
                         size=12, fill="#eafaf1", stroke=FIELD, sw=1.8)
    els.append(b2)
    els.append(arrow(mx + 40, 165 + h2 / 2, mx, cy - bh / 2 - 4, color=FIELD, sw=1.8))

    b3, w3, h3 = textbox(ex + 6, 120, ["КЕРУВАННЯ", "перехід зробить уже", "вибране — зайвим"],
                         size=12, fill="#eaf0fd", stroke=NEG, sw=1.8)
    els.append(b3)
    els.append(arrow(ex + 6, 120 + h3 / 2, ex, cy - bh / 2 - 4, color=NEG, sw=1.8))

    render(os.path.join(IMG, 'three-hazards.svg'), W, H, *els,
           title="Три роди конфліктів на одному конвеєрі")


# ── Фігура 2: RAW — проброс проти бульбашки ─────────────────────────────────
def fig_forward():
    W, H = 860, 430
    els = []
    # сітка стадія×такт
    stages = ["ВБ", "ДК", "ВК", "ПМ", "ЗП"]
    ns = len(stages)
    x0, y0 = 150, 70
    cw, rh = 108, 46
    # заголовки тактів
    ntacts = 6
    for t in range(ntacts):
        els.append(text(x0 + cw / 2 + t * cw, y0 - 14, "t%d" % (t + 1), size=13, bold=True, color=MUTED))
    # підписи стадій ліворуч
    for s in range(ns):
        els.append(text(x0 - 16, y0 + rh / 2 + 6 + s * rh, stages[s], size=12, color=MUTED, anchor="end"))

    def cell(stage, tact, txt, fill):
        x = x0 + tact * cw
        y = y0 + stage * rh
        return fitbox(x + 3, y + 3, cw - 6, rh - 6, txt, size=12, fill=fill, stroke=LINE, sw=1.3, bold=True)

    # команда 1: ДОДАЙ R3 (пише R3) — діагональ із t1
    c1 = "#eafaf1"
    for s in range(ns):
        els.append(cell(s, s, "I1", c1))
    # команда 2: ВІДНІМИ (читає R3) — діагональ із t2, стадія ВК на t4
    c2 = "#fdecea"
    for s in range(ns):
        els.append(cell(s, s + 1, "I2", c2))

    els.append(text(W / 2, y0 + ns * rh + 26,
                    "I1: ДОДАЙ R3 ← R1+R2   (результат готовий у кінці ВК, такт t3)", size=12, color=INK, anchor="middle"))
    els.append(text(W / 2, y0 + ns * rh + 46,
                    "I2: ВІДНІМИ R4 ← R3−1   (потребує R3 на вході ВК, такт t4)", size=12, color=INK, anchor="middle"))

    # стрілка пробросу: з кінця ВК I1 (t3) у вхід ВК I2 (t4)
    x_src = x0 + 2 * cw + cw  # правий край клітинки I1-ВК (стадія 2, такт 2 → x0+2cw..+3cw)
    y_src = y0 + 2 * rh + rh / 2
    x_dst = x0 + 3 * cw       # лівий край клітинки I2-ВК (стадія 2, такт 3)
    y_dst = y0 + 2 * rh + rh / 2
    els.append(line(x_src, y_src, x_src + 18, y_src, color=POS, sw=2.4))
    els.append(text(x_src + 210, y_src - 10, "ПРОБРОС: результат подають прямо на вхід ВК —",
                    size=12, color=POS, bold=True, anchor="middle"))
    els.append(text(x_src + 176, y_src + 10, "не чекаючи запису в регістр, затримки нема",
                    size=12, color=POS, anchor="middle"))
    els.append(arrow(x_src + 18, y_src, x_dst, y_dst - 1, color=POS, sw=2.4))

    render(os.path.join(IMG, 'forward-vs-stall.svg'), W, H, *els,
           title="Залежність даних (RAW): проброс закриває розрив без простою")


# ── Фігура 3: бульбашка (стоп) і змив (flush) — дві панелі ───────────────────
def _grid(els, ox, oy, stages, cw, rh, ntacts):
    ns = len(stages)
    for t in range(ntacts):
        els.append(text(ox + cw / 2 + t * cw, oy - 11, "t%d" % (t + 1), size=11, bold=True, color=MUTED))
    for s in range(ns):
        els.append(text(ox - 12, oy + rh / 2 + 5 + s * rh, stages[s], size=10, color=MUTED, anchor="end"))


def _cell(ox, oy, cw, rh, stage, tact, txt, fill, stroke=LINE, dash=False):
    x = ox + tact * cw
    y = oy + stage * rh
    if dash:
        r = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" fill="%s" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>'
             % (x + 3, y + 3, cw - 6, rh - 6, fill, stroke))
    else:
        r = rect(x + 3, y + 3, cw - 6, rh - 6, fill=fill, stroke=stroke, sw=1.3, rx=5)
    col = MUTED if txt in ("—", "×") else INK
    r += text(x + cw / 2, y + rh / 2 + 5, txt, size=12, bold=True, color=col)
    return r


def fig_bubble_flush():
    W, H = 924, 320
    els = []
    stages = ["ВБ", "ДК", "ВК", "ПМ", "ЗП"]
    ns = len(stages)
    cw, rh = 66, 38
    BLUE, RED, GREEN = "#eaf0fd", "#fdecea", "#eafaf1"

    # ── ліва панель: СТОП (бульбашка) ──
    ox, oy = 92, 78
    nt = 6
    _grid(els, ox, oy, stages, cw, rh, nt)
    for s in range(ns):
        els.append(_cell(ox, oy, cw, rh, s, s, "I1", GREEN))
    # I2 застрягла в ВБ зайвий такт, тоді зсув
    els.append(_cell(ox, oy, cw, rh, 0, 1, "I2", BLUE))
    els.append(_cell(ox, oy, cw, rh, 0, 2, "I2", BLUE))
    els.append(_cell(ox, oy, cw, rh, 1, 3, "I2", BLUE))
    els.append(_cell(ox, oy, cw, rh, 2, 4, "I2", BLUE))
    els.append(_cell(ox, oy, cw, rh, 3, 5, "I2", BLUE))
    # бульбашка їде замість I2
    els.append(_cell(ox, oy, cw, rh, 1, 2, "—", BG, stroke=MUTED, dash=True))
    els.append(_cell(ox, oy, cw, rh, 2, 3, "—", BG, stroke=MUTED, dash=True))
    els.append(text(ox + nt * cw / 2, oy - 34, "СТОП: тримаємо регістр — у конвеєр їде «—»",
                    size=12.5, bold=True, color=NEG, anchor="middle"))
    els.append(text(ox + nt * cw / 2, oy + ns * rh + 24,
                    "I2 чекає на дані; порожня бульбашка", size=11, color=MUTED, anchor="middle"))

    # ── права панель: ЗМИВ (flush) ──
    ox2 = 500
    _grid(els, ox2, oy, stages, cw, rh, nt)
    # перехід I1 узято: вже вибрані I2,I3 стають недійсними
    els.append(_cell(ox2, oy, cw, rh, 0, 0, "I1", GREEN))
    els.append(_cell(ox2, oy, cw, rh, 1, 1, "I1", GREEN))
    els.append(_cell(ox2, oy, cw, rh, 2, 2, "I1*", GREEN))  # тут стало відомо: перехід
    # спекулятивно вибрані сусіди
    els.append(_cell(ox2, oy, cw, rh, 0, 1, "I2", RED))
    els.append(_cell(ox2, oy, cw, rh, 1, 2, "I2", RED))
    els.append(_cell(ox2, oy, cw, rh, 0, 2, "I3", RED))
    # на t3 — стерто (×), з t4 їде правильна ціль T
    els.append(_cell(ox2, oy, cw, rh, 1, 3, "×", BG, stroke=MUTED, dash=True))
    els.append(_cell(ox2, oy, cw, rh, 2, 3, "×", BG, stroke=MUTED, dash=True))
    els.append(_cell(ox2, oy, cw, rh, 0, 3, "T", "#fff6e6"))
    els.append(_cell(ox2, oy, cw, rh, 1, 4, "T", "#fff6e6"))
    els.append(_cell(ox2, oy, cw, rh, 2, 5, "T", "#fff6e6"))
    els.append(text(ox2 + nt * cw / 2, oy - 34, "ЗМИВ: перехід узято — вибране стирають («×»)",
                    size=12.5, bold=True, color=POS, anchor="middle"))
    els.append(text(ox2 + nt * cw / 2, oy + ns * rh + 24,
                    "з такту t4 їде правильна ціль T", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'bubble-flush.svg'), W, H, *els,
           title="Коли пробросу мало: стоп-бульбашка (ліворуч) і змив (праворуч)")


# ── Фігура 4: датапас моделі — регістри-структури й два проброс-шляхи в ВК ────
def fig_datapath():
    W, H = 900, 470
    els = []
    # чотири міжстадійні регістри як «структури» (рядки полів)
    names = ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]
    fields = [
        ["pc", "instr"],
        ["rs1", "rs2", "op", "rd"],
        ["alu", "rd", "wen"],
        ["val", "rd", "wen"],
    ]
    n = len(names)
    bw, gap = 150, 62
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    cy = 250
    xs = []
    for i, nm in enumerate(names):
        x = x0 + i * (bw + gap)
        xs.append(x)
        fl = fields[i]
        bh = 26 + len(fl) * 20
        top = cy - bh / 2
        els.append(rect(x, top, bw, bh, fill="#eef2f7", stroke=LINE, sw=1.7, rx=8))
        els.append(text(x + bw / 2, top - 9, nm, size=13, bold=True, color=MUTED))
        for k, f in enumerate(fl):
            els.append(text(x + bw / 2, top + 22 + k * 20, f, size=12, color=INK))
        if i < n - 1:
            els.append(arrow(x + bw, cy, x + bw + gap, cy, color=MUTED, sw=1.8))
    # блок ВК (ALU) — під регістром ID/EX
    ex_x = xs[1]
    ex_cy = cy + 118
    ebw, ebh = bw, 52
    els.append(rect(ex_x, ex_cy - ebh / 2, ebw, ebh, fill="#eafaf1", stroke=FIELD, sw=1.9, rx=8))
    els.append(text(ex_x + ebw / 2, ex_cy + 5, "ALU (стадія ВК)", size=13, bold=True))
    # мультиплексори на входах ALU
    mux_a = (ex_x + 22, ex_cy - ebh / 2 - 30)
    mux_b = (ex_x + ebw - 22, ex_cy - ebh / 2 - 30)
    for (mxx, mxy), lbl in ((mux_a, "muxA"), (mux_b, "muxB")):
        els.append(rect(mxx - 20, mxy - 16, 40, 32, fill="#fff6e6", stroke=POS, sw=1.6, rx=5))
        els.append(text(mxx, mxy + 4, lbl, size=11, bold=True, color=POS))
        els.append(arrow(mxx, mxy + 16, mxx, ex_cy - ebh / 2, color=POS, sw=1.7))
    # базовий вхід: з ID/EX (rs1/rs2) вниз у мультиплексори
    els.append(line(ex_x + 30, cy + len(fields[1]) * 20 - 6, ex_x + 30, mux_a[1] - 16, color=MUTED, sw=1.5, dash="4 3"))
    els.append(line(ex_x + ebw - 30, cy + len(fields[1]) * 20 - 6, ex_x + ebw - 30, mux_b[1] - 16, color=MUTED, sw=1.5, dash="4 3"))
    els.append(text(ex_x + ebw / 2, mux_a[1] - 30, "з регістрового файла (за замовчуванням)", size=10.5, color=MUTED))
    # проброс-шлях 1: EX/MEM.alu → mux (ближчий, вищий пріоритет)
    sx1 = xs[2] + bw / 2
    sy1 = cy + len(fields[2]) * 20 - 4
    els.append(line(sx1, sy1, sx1, sy1 + 40, color=POS, sw=2.4))
    els.append(line(sx1, sy1 + 40, mux_b[0] + 26, sy1 + 40, color=POS, sw=2.4))
    els.append(arrow(mux_b[0] + 26, sy1 + 40, mux_b[0] + 20, mux_b[1], color=POS, sw=2.4))
    els.append(text(sx1 - 4, sy1 + 34, "EX/MEM→ВК (ближчий: ПРІОРИТЕТ)", size=11, bold=True, color=POS, anchor="end"))
    # проброс-шлях 2: MEM/WB.val → mux (дальший)
    sx2 = xs[3] + bw / 2
    sy2 = cy + len(fields[3]) * 20 - 4
    els.append(line(sx2, sy2, sx2, sy2 + 70, color=NEG, sw=2.2))
    els.append(line(sx2, sy2 + 70, mux_b[0] + 46, sy2 + 70, color=NEG, sw=2.2))
    els.append(arrow(mux_b[0] + 46, sy2 + 70, mux_b[0] + 24, mux_b[1] + 2, color=NEG, sw=2.2))
    els.append(text(sx2 - 4, sy2 + 64, "MEM/WB→ВК (дальший)", size=11, bold=True, color=NEG, anchor="end"))
    render(os.path.join(IMG, 'forward-datapath.svg'), W, H, *els,
           title="Два проброс-шляхи в стадію ВК: ближче джерело має пріоритет")


# ── Фігура 5: масив регістрів моделі зсувається за такт (як живе код) ─────────
def fig_shift_model():
    W, H = 820, 300
    els = []
    stages = ["reg[0]=IF/ID", "reg[1]=ID/EX", "reg[2]=EX/MEM", "reg[3]=MEM/WB"]
    ns = len(stages)
    bw, bh = 168, 44
    x0 = (W - bw) / 2
    y0 = 70
    for i, s in enumerate(stages):
        y = y0 + i * (bh + 18)
        fill = "#eef2f7"
        els.append(rect(x0, y, bw, bh, fill=fill, stroke=LINE, sw=1.6, rx=8))
        els.append(text(x0 + bw / 2, y + bh / 2 + 5, s, size=13, bold=True))
        if i < ns - 1:
            # стрілка «зсув на такт»: reg[i+1] = reg[i]
            yy = y + bh
            els.append(arrow(x0 + bw / 2, yy, x0 + bw / 2, yy + 18, color=POS, sw=2.0))
    els.append(text(x0 + bw + 30, y0 + bh / 2 + 5, "нове →", size=12, color=MUTED, anchor="start"))
    els.append(text(x0 - 30, y0 + (ns - 1) * (bh + 18) + bh / 2 + 5, "→ запис", size=12, color=MUTED, anchor="end"))
    # праворуч — псевдо-порядок кроку такту
    steps = ["1. детекція: порівняти rd", "2. проброс: вибрати вхід", "3. стоп? бульбашка : зсув",
             "4. взято перехід? змив"]
    bx = x0 + bw + 70
    by = y0 - 6
    b, bwid, bht = textbox(bx + 150, by + 92, steps, size=12, bold=False,
                           fill="#f7f9fb", stroke=MUTED, sw=1.5)
    els.append(b)
    els.append(text(bx + 150, by + 92 - bht / 2 - 12, "порядок одного такту", size=12, bold=True, color=MUTED))
    render(os.path.join(IMG, 'shift-model.svg'), W, H, *els,
           title="Масив пайплайн-регістрів зсувається на такт — серце моделі")


# ── Фігура (до вставки hist): родовід конфліктів 1961→1964→1967 ──────────────
def fig_hist_timeline():
    W, H = 900, 440
    els = []

    # горизонтальна вісь часу
    ax_y = 92
    els.append(line(60, ax_y, W - 40, ax_y, color=MUTED, sw=2))
    els.append(arrow(W - 62, ax_y, W - 34, ax_y, color=MUTED, sw=2))

    cols = [
        (200, "1961", "IBM 7030 Stretch"),
        (460, "1964", "CDC 6600"),
        (720, "1967", "System/360 Mod. 91"),
    ]
    for x, yr, name in cols:
        els.append(circle(x, ax_y, 6, fill=INK, stroke=INK, sw=1))
        els.append(text(x, ax_y - 20, yr, size=16, bold=True))
        els.append(text(x, ax_y - 40, name, size=12, color=MUTED))

    # три картки: що ДАЛА машина, кольором «свого» конфлікту
    card_y = 210
    box_w = 244
    gains = [
        (200, POS, "#fdecea",
         ["Багато команд у польоті", "(до 11). Проброс store→load,",
          "відкат наперед вибраного —", "усе ще БЕЗ назв"]),
        (460, NEG, "#eaf0fd",
         ["Незалежні вузли + табло:", "уперше ПОЗАЧЕРГОВЕ",
          "виконання. WAR/WAW", "розв'язують ЗУПИНКОЮ"]),
        (720, FIELD, "#eafaf1",
         ["Станції + спільна шина +", "ПЕРЕЙМЕНУВАННЯ регістрів:",
          "WAR/WAW усунено в корені", "(різні імена — нема сутички)"]),
    ]
    for x, stroke, fill, lines in gains:
        els.append(fitbox(x - box_w / 2, card_y, box_w, 92, "\n".join(lines),
                          size=11.5, fill=fill, stroke=stroke, sw=1.8))
        els.append(line(x, ax_y + 6, x, card_y, color=stroke, sw=1.4, dash="3 3"))

    # містки «створює задачу для наступної»
    def bridge(x1, x2, y, lines):
        mid = (x1 + x2) / 2
        els.append(arrow(x1, y, x2, y, color=INK, sw=1.6))
        b, w, h = textbox(mid, y - 22, lines, size=11, fill="#fff6e6",
                          stroke=MUTED, sw=1.2)
        els.append(b)

    by = card_y + 148
    bridge(200 + box_w / 2 - 8, 460 - box_w / 2 + 8, by,
           ["перекриття в часі →", "уперше можливий RAW"])
    bridge(460 + box_w / 2 - 8, 720 - box_w / 2 + 8, by,
           ["позачерговість →", "можливі WAR/WAW"])

    els.append(text(W / 2, H - 20,
                    "кожна машина, розв'язавши свою задачу, породжувала задачу для наступної",
                    size=12.5, bold=True, color=INK))

    render(os.path.join(IMG, 'hazard-timeline.svg'), W, H, *els,
           title="Родовід конфліктів: 1961 → 1964 → 1967")


if __name__ == '__main__':
    fig_three()
    fig_forward()
    fig_bubble_flush()
    fig_datapath()
    fig_shift_model()
    fig_hist_timeline()
    print("figs done")
