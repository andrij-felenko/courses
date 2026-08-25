# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODEBG = "#f4f6f8"
CODEFONT = "'Consolas', 'DejaVu Sans Mono', monospace"


def codeblock(x, y, w, lines, size=12, lh=1.45, title=None, accent=INK):
    """Рамка з моноширинним кодом (рядки — список). Повертає (svg, висота)."""
    pad = 12
    head = (size + 8) if title else 0
    h = head + len(lines) * size * lh + 2 * pad
    out = [rect(x, y, w, h, fill=CODEBG, stroke=accent, sw=1.6, rx=8)]
    if title:
        out.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" '
                   'fill="%s" font-weight="700">%s</text>'
                   % (x + pad, y + pad + size - 2, FONT, size, accent, esc(title)))
    ty = y + pad + head + size - 2
    for i, ln in enumerate(lines):
        out.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" '
                   'fill="%s" xml:space="preserve">%s</text>'
                   % (x + pad, ty + i * size * lh, CODEFONT, size, INK, esc(ln)))
    return "".join(out), h


# ── two-loops: цикл перевірки на комп'ютері проти циклу з паянням ───────────────
# Ідея: без симуляції кожна помилка коштує повного кола синтез→прошити→паяти→
# зловити (години); з симуляцією помилку видно за секунди, не торкнувшись плати.

def fig_two_loops():
    W, H = 800, 380
    p = []
    colw = 350
    lx, rx = 34, W - 34 - colw

    # ── ЛІВО: коло без симуляції (довге, дороге) ──
    p.append(text(lx + colw / 2, 54, "Без симуляції: коло через залізо", size=13, bold=True, color=POS))
    steps_l = [("написати HDL", "#f4f6f8", INK),
               ("СИНТЕЗ (хвилини)", "#fdecea", POS),
               ("прошити плату", "#fdecea", POS),
               ("шукати баг тестером", "#fdecea", POS)]
    cx = lx + colw / 2
    ys = [96, 156, 216, 276]
    boxes_l = []
    for (lab, fill, col), yy in zip(steps_l, ys):
        b, bw, bh = textbox(cx, yy, lab, size=12, bold=True, fill=fill, stroke=col, sw=1.7, min_w=210)
        p.append(b); boxes_l.append((yy, bh))
    for i in range(len(ys) - 1):
        y0 = ys[i] + boxes_l[i][1] / 2
        y1 = ys[i + 1] - boxes_l[i + 1][1] / 2
        p.append(arrow(cx, y0, cx, y1, color=POS, sw=1.8))
    # зворотна дуга «і все спочатку»
    p.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (cx + 108, ys[3], cx + 190, ys[3], cx + 190, ys[0], cx + 108, ys[0], POS))
    p.append(text(cx + 196, (ys[0] + ys[3]) / 2, "і все", size=10, color=POS, anchor="start", italic=True))
    p.append(text(cx + 196, (ys[0] + ys[3]) / 2 + 14, "спочатку", size=10, color=POS, anchor="start", italic=True))
    p.append(text(cx, 330, "одна помилка = години", size=11, color=POS, bold=True))

    # ── ПРАВО: коло із симуляцією (коротке, дешеве) ──
    p.append(text(rx + colw / 2, 54, "Із симуляцією: коло на комп'ютері", size=13, bold=True, color=FIELD))
    steps_r = [("написати HDL", "#f4f6f8", INK),
               ("СИМУЛЯЦІЯ (секунди)", "#eafaf0", FIELD),
               ("тестбенч ловить баг", "#eafaf0", FIELD)]
    cxr = rx + colw / 2
    ysr = [96, 168, 240]
    boxes_r = []
    for (lab, fill, col), yy in zip(steps_r, ysr):
        b, bw, bh = textbox(cxr, yy, lab, size=12, bold=True, fill=fill, stroke=col, sw=1.7, min_w=220)
        p.append(b); boxes_r.append((yy, bh))
    for i in range(len(ysr) - 1):
        y0 = ysr[i] + boxes_r[i][1] / 2
        y1 = ysr[i + 1] - boxes_r[i + 1][1] / 2
        p.append(arrow(cxr, y0, cxr, y1, color=FIELD, sw=1.8))
    p.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (cxr - 114, ysr[2], cxr - 196, ysr[2], cxr - 196, ysr[0], cxr - 114, ysr[0], FIELD))
    p.append(text(cxr - 202, (ysr[0] + ysr[2]) / 2, "виправив —", size=10, color=FIELD, anchor="end", italic=True))
    p.append(text(cxr - 202, (ysr[0] + ysr[2]) / 2 + 14, "прогнав знову", size=10, color=FIELD, anchor="end", italic=True))
    # аж тоді на плату
    p.append(arrow(cxr, ysr[2] + boxes_r[2][1] / 2, cxr, 300, color=INK, sw=1.8))
    pb, pbw, pbh = textbox(cxr, 322, "аж коли чисто — синтез і плата\n(ОДИН раз)", size=11, bold=True,
                           fill="#fdf6e3", stroke=INK, sw=1.6)
    p.append(pb)

    render(os.path.join(OUT, "two-loops.svg"), W, H, *p,
           title="Навіщо симуляція: баг ловиться за секунди, а не паянням годинами")


# ── testbench: DUT у «несправжньому світі» ─────────────────────────────────────
# Ідея: тестбенч — модуль БЕЗ виводів, що обгортає перевірюваний модуль (DUT):
# сам створює для нього clk і подразники, читає виходи й порівнює з очікуваним.

def fig_testbench():
    W, H = 780, 380
    p = []
    # зовнішня рамка — тестбенч (модуль без ніжок)
    tx, ty, tw, th = 40, 56, 700, 250
    p.append(rect(tx, ty, tw, th, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=12))
    p.append(text(tx + 16, ty + 24, "module tb;   // тестбенч — немає жодного виводу назовні",
                  size=12, bold=True, color=FIELD, anchor="start"))

    # усередині — DUT
    dx, dy, dw, dh = tx + 250, ty + 70, 200, 120
    p.append(rect(dx, dy, dw, dh, fill="#eef4ff", stroke=NEG, sw=1.9, rx=10))
    p.append(text(dx + dw / 2, dy + 26, "DUT", size=15, bold=True, color=NEG))
    p.append(text(dx + dw / 2, dy + 46, "(device under test)", size=9, color=NEG, italic=True))
    p.append(text(dx + dw / 2, dy + 70, "counter.v", size=12, color=INK))
    p.append(text(dx + dw / 2, dy + 90, "— наш дизайн", size=10, color=MUTED, italic=True))

    # ліворуч — генератор подразників (входи в DUT)
    gb, gbw, gbh = textbox(tx + 110, ty + 110, "генератор:\nробить clk,\nдає rst, en", size=11,
                           bold=True, fill=BG, stroke=FIELD, sw=1.7)
    p.append(gb)
    p.append(arrow(tx + 110 + gbw / 2, ty + 110, dx, dy + 40, color=INK, sw=1.8))
    p.append(text((tx + 110 + gbw / 2 + dx) / 2, dy + 22, "clk·rst·en", size=9, color=INK))

    # праворуч — перевіряч (читає виходи, порівнює)
    cb, cbw, cbh = textbox(tx + tw - 110, ty + 110, "перевіряч:\nчитає count,\nпорівнює з\nочікуваним", size=11,
                           bold=True, fill=BG, stroke=POS, sw=1.7)
    p.append(cb)
    p.append(arrow(dx + dw, dy + 60, tx + tw - 110 - cbw / 2, ty + 110, color=POS, sw=1.8))
    p.append(text((dx + dw + tx + tw - 110 - cbw / 2) / 2, dy + 44, "count", size=9, color=POS))

    # вердикт під рамкою
    p.append(arrow(W / 2, ty + th + 4, W / 2, ty + th + 34, color=INK, sw=1.8))
    vb, vbw, vbh = textbox(W / 2, ty + th + 56,
                           "$display(\"PASS\")  або  $display(\"FAIL @ %0t\", $time)",
                           size=11, bold=True, fill="#fdf6e3", stroke=INK, sw=1.6)
    p.append(vb)

    render(os.path.join(OUT, "testbench.svg"), W, H, *p,
           title="Тестбенч: обгортка, що сама годує дизайн і сама перевіряє виходи")


# ── four-values: 0, 1, X, Z — і звідки беруться X та Z ─────────────────────────
# Ідея: у симуляції провід має не два, а ЧОТИРИ значення; X (невідомо) і
# Z (відключено) — саме те, заради чого симулюють до синтезу: вони світять баг.

def fig_four_values():
    W, H = 800, 360
    p = []
    cards = [
        (140, "0", NEG, "#eef4ff", "твердий нуль", "лог. низький рівень"),
        (330, "1", POS, "#fdecea", "тверда одиниця", "лог. високий рівень"),
        (520, "X", "#b8860b", "#fdf3d6", "НЕВІДОМО", "не задано / конфлікт"),
        (710, "Z", "#6b7280", "#eef1f4", "ВІДКЛЮЧЕНО", "ніхто не жене (три-стейт)"),
    ]
    cy = 120
    for cx, sym, col, fill, name, note in cards:
        b, bw, bh = textbox(cx, cy, sym, size=30, bold=True, color=col, fill=fill, stroke=col, sw=2.2, min_w=84)
        p.append(b)
        p.append(text(cx, cy + bh / 2 + 22, name, size=12, color=col, bold=True))
        p.append(mtext(cx, cy + bh / 2 + 40, note, size=9, color=MUTED, lh=1.25))

    # нижня стрічка: звідки X і Z, і чому це цінно
    by = 250
    xb = fitbox(70, by, 320, 78,
                "X з'являється, коли провід НЕ ІНІЦІАЛІЗОВАНО або два\nдрайвери тягнуть у різні боки. Симулятор РОЗНОСИТЬ X\nдалі схемою — і баг сам себе підсвічує ще до плати.",
                size=10.5, fill="#fdf3d6", stroke="#b8860b", sw=1.6, color=INK)
    p.append(xb)
    zb = fitbox(410, by, 320, 78,
                "Z — законний стан три-стейтового виходу (спільна шина).\nАле Z на внутрішньому дроті майже завжди означає\n«сюди нічого не під'єднано» — теж помилка, видима в симуляції.",
                size=10.5, fill="#eef1f4", stroke="#6b7280", sw=1.6, color=INK)
    p.append(zb)

    render(os.path.join(OUT, "four-values.svg"), W, H, *p,
           title="Провід у симуляції має чотири значення, не два — і саме X та Z ловлять баги")


# ── event-time: час у симуляторі рухають ПОДІЇ, а не рівномірний тік ────────────
# Ідея: симулятор не «біжить рівно» — він перестрибує від події до події за
# чергою подій; між подіями час стоїть, бо нічого не міняється.

def fig_event_time():
    W, H = 800, 320
    p = []
    ax0, ax1 = 80, 740
    midy = 150
    p.append(line(ax0, midy, ax1, midy, color=INK, sw=2.0))
    p.append(arrow(ax1 - 2, midy, ax1 + 22, midy, color=INK, sw=2.0))
    p.append(text(ax1 + 26, midy + 4, "час", size=10, color=MUTED, anchor="start", italic=True))

    # події у нерівномірних точках модельного часу
    events = [(0, "clk↑", NEG, "лічильник\n+1"),
              (5, "clk↓", MUTED, "нічого\nне міняє"),
              (10, "clk↑", NEG, "лічильник\n+1"),
              (12, "rst=1", POS, "скидання\n→ 0"),
              (20, "clk↑", NEG, "лишається 0\n(rst тримає)")]
    span = 22.0
    for t, lab, col, eff in events:
        x = ax0 + t / span * (ax1 - ax0)
        p.append(line(x, midy - 30, x, midy + 30, color=col, sw=1.4, dash="3 3"))
        p.append(circle(x, midy, 5, fill=col, stroke=col, sw=1))
        p.append(text(x, midy - 40, lab, size=11, color=col, bold=True))
        p.append(text(x, midy - 56, "t=%d" % t, size=9, color=MUTED))
        p.append(mtext(x, midy + 46, eff, size=9, color=INK, lh=1.2))

    # підсвітити «порожній» проміжок t=12..20, де час стоїть
    x12 = ax0 + 12 / span * (ax1 - ax0)
    x20 = ax0 + 20 / span * (ax1 - ax0)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="none" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="5 4"/>'
             % (x12, midy + 66, x20 - x12, 26, MUTED))
    p.append(text((x12 + x20) / 2, midy + 108, "між подіями час СТОЇТЬ — рахувати нічого",
                  size=10, color=MUTED, italic=True))

    p.append(text(W / 2, H - 16,
                  "симулятор перестрибує від події до події за чергою подій — так модельний час обганяє реальний",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "event-time.svg"), W, H, *p,
           title="Час у симуляції рухають події, а не рівномірний тік")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки hist-simulator-origins
# ════════════════════════════════════════════════════════════════════════════

# ── sim-cradles: дві колиски САМЕ СИМУЛЯТОРА ───────────────────────────────────
# Ідея (не мов, а симуляторів): ліворуч стартап — Verilog-XL, симулятор як
# інструмент перевірки; праворуч оборонне відомство — еталонний симулятор VHDL
# як спосіб просимулювати чужий задокументований чип. Спільне внизу: керована
# подіями модель, що вдає час без кремнію.

def fig_sim_cradles():
    W, H = 800, 330
    p = []
    colw = 340
    lx, rx = 36, W - 36 - colw

    # ── стартап: Verilog-XL ──
    p.append(rect(lx, 58, colw, 196, fill="#fdecea", stroke=POS, sw=2, rx=12))
    p.append(text(lx + colw / 2, 88, "Verilog-XL", size=19, bold=True, color=POS))
    p.append(text(lx + colw / 2, 110, "симулятор стартапу", size=12, color=POS, bold=True))
    p.append(mtext(lx + colw / 2, 140,
                   ["Gateway, жменька людей",
                    "Мурбі пише симулятор 1984",
                    "мета — ПЕРЕВІРИТИ власну",
                    "схему до кремнію"], size=11, color=INK, lh=1.42))
    p.append(text(lx + colw / 2, 236, "інструмент перевірки", size=11, color=POS, italic=True))

    # ── оборонне відомство: еталонний симулятор VHDL ──
    p.append(rect(rx, 58, colw, 196, fill="#eef4ff", stroke=NEG, sw=2, rx=12))
    p.append(text(rx + colw / 2, 88, "еталонний симулятор VHDL", size=15, bold=True, color=NEG))
    p.append(text(rx + colw / 2, 110, "замовлення оборони США", size=12, color=NEG, bold=True))
    p.append(mtext(rx + colw / 2, 140,
                   ["контракт ВПС, консорціум",
                    "Intermetrics будує симулятор",
                    "мета — ПРОСИМУЛЮВАТИ чужий",
                    "задокументований чип"], size=11, color=INK, lh=1.42))
    p.append(text(rx + colw / 2, 236, "перевірка задокументованого", size=11, color=NEG, italic=True))

    p.append(text(W / 2, H - 16,
                  "різні світи — та сама серцевина: керована подіями модель, що вдає час без жодного кремнію",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "sim-cradles.svg"), W, H, *p,
           title="Дві колиски самого симулятора, а не лише мови")


# ── sim-lineage: симулятор старший за Verilog — родовід від HILO ───────────────
# Ідея: керований подіями симулятор існував ДО Verilog. Мурбі приніс його з
# проєкту HILO (Брунел, перший RTL-симулятор), а Verilog-XL — спадкоємець тієї
# машини часу, не її винахід.

def fig_sim_lineage():
    W, H = 820, 300
    p = []
    ax0, ax1 = 70, 752
    midy = 150
    p.append(line(ax0, midy, ax1, midy, color=INK, sw=2.0))
    p.append(arrow(ax1 - 2, midy, ax1 + 20, midy, color=INK, sw=2.0))
    p.append(text(ax1 + 24, midy + 4, "час", size=10, color=MUTED, anchor="start", italic=True))

    span_lo, span_hi = 1970.0, 1990.0

    def xfor(yr):
        return ax0 + (yr - span_lo) / (span_hi - span_lo) * (ax1 - ax0)

    # віхи родоводу симулятора
    miles = [
        (1972, "HILO-1", "поч. 1970-х", "Брунел (Англія):\nструктурний\nсимулятор", NEG, True),
        (1981, "HILO-2", "поч. 1980-х", "перший RTL-\nсимулятор\n(Флейк, Мурбі)", NEG, True),
        (1984, "Verilog", "1984", "Мурбі несе ту саму\nкеровану подіями\nмашину в Gateway", POS, False),
        (1987, "Verilog-XL", "1987", "той самий рушій,\nтільки швидший", POS, False),
    ]
    for xyr, lab, yrlab, note, col, up in miles:
        x = xfor(xyr)
        yy = midy - 40 if up else midy + 40
        p.append(line(x, midy, x, yy, color=col, sw=1.6))
        p.append(circle(x, midy, 4, fill=col, stroke=col, sw=1))
        if up:
            p.append(text(x, yy - 6, lab, size=12, color=col, bold=True))
            p.append(text(x, yy - 24, yrlab, size=9, color=MUTED))
            p.append(mtext(x, yy - 40, note, size=9, color=INK, lh=1.2))
        else:
            p.append(text(x, yy + 16, lab, size=12, color=col, bold=True))
            p.append(text(x, yy + 32, yrlab, size=9, color=MUTED))
            p.append(mtext(x, yy + 48, note, size=9, color=INK, lh=1.2))

    p.append(text(W / 2, H - 14,
                  "керований подіями симулятор — старший за Verilog: мову приладнали до вже готової машини часу",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "sim-lineage.svg"), W, H, *p,
           title="Родовід симулятора: Verilog успадкував машину часу, а не винайшов її")


# ── sim-credit: точна атрибуція симулятора по ролях ───────────────────────────
# Ідея: жодного одинокого генія — родовід HILO (Флейк, Мурбі, Давідманн),
# стартап Gateway (Мурбі, Ґоел, Хуанг), консорціум VHDL (Intermetrics/TI/IBM),
# і спільнота, що зробила рушій спільним стандартом.

def fig_sim_credit():
    W, H = 820, 340
    p = []
    cards = [
        (170, 108, "Проєкт HILO\n(Брунел, Англія)", FIELD, "#eafaf0",
         "РОДОВІД:\nперший RTL-симулятор —\nФлейк, Мурбі, Давідманн"),
        (490, 108, "Gateway: Мурбі,\nҐоел, Хуанг", POS, "#fdecea",
         "СТАРТАП:\nсимулятор Verilog-XL —\nінструмент перевірки"),
        (170, 240, "Intermetrics,\nTI, IBM", NEG, "#eef4ff",
         "КОНСОРЦІУМ (замовлення ВПС):\nеталонний симулятор VHDL\nдля чужих чипів"),
        (490, 240, "Спільноти й IEEE\n(OVI · 1076 · 1364)", MUTED, "#eef1f4",
         "СТАНДАРТ:\nзробили рушій\nнадбанням усіх"),
    ]
    for cx, cy, title, col, fill, role in cards:
        b, bw, bh = textbox(cx, cy, title, size=12, bold=True, color=col, fill=fill, stroke=col, sw=1.9, pad=12)
        p.append(b)
        p.append(mtext(cx, cy + bh / 2 + 16, role, size=9.5, color=MUTED, lh=1.3))

    p.append(mtext(715, 168,
                   ["Одинокого", "генія немає —", "керовану", "подіями", "машину часу", "будували", "багато рук"],
                   size=11, color=INK, lh=1.4, bold=True))

    render(os.path.join(OUT, "sim-credit.svg"), W, H, *p,
           title="Точна атрибуція симулятора: чотири ролі, жодного одинокого генія")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки proj-selfcheck-testbench
# ════════════════════════════════════════════════════════════════════════════

# ── golden-model: два лічильники поряд — DUT і незалежний еталон ────────────────
# Ідея: самоперевірка тримається не на одній лічбі, а на ДВОХ: DUT і окремо
# написаний еталон expected; компаратор звіряє їх чотиризначним !== .

def fig_golden_model():
    W, H = 800, 400
    p = []
    # спільні входи ліворуч
    ib, ibw, ibh = textbox(90, 200, "спільні входи:\nclk · rst · en", size=12, bold=True,
                           fill="#fdf6e3", stroke=INK, sw=1.7, min_w=150)
    p.append(ib)

    # DUT — синій, угорі
    dx, dy, dw, dh = 300, 70, 260, 108
    p.append(rect(dx, dy, dw, dh, fill="#eef4ff", stroke=NEG, sw=2.0, rx=10))
    p.append(text(dx + dw / 2, dy + 26, "DUT — counter.v", size=14, bold=True, color=NEG))
    p.append(text(dx + dw / 2, dy + 48, "(перевіряємо його правильність)", size=9.5, color=NEG, italic=True))
    p.append(text(dx + dw / 2, dy + 74, "count <= count + 1", size=12, color=INK))
    p.append(text(dx + dw / 2, dy + 93, "— своя логіка", size=9.5, color=MUTED, italic=True))

    # еталон — зелений, унизу
    ex, ey, ew, eh = 300, 222, 260, 108
    p.append(rect(ex, ey, ew, eh, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=10))
    p.append(text(ex + ew / 2, ey + 26, "ЕТАЛОН — expected", size=14, bold=True, color=FIELD))
    p.append(text(ex + ew / 2, ey + 48, "(написаний НЕЗАЛЕЖНО, прозоро)", size=9.5, color=FIELD, italic=True))
    p.append(text(ex + ew / 2, ey + 74, "expected <= expected + 1", size=12, color=INK))
    p.append(text(ex + ew / 2, ey + 93, "— тривіально правильний", size=9.5, color=MUTED, italic=True))

    # входи годують обидва
    p.append(arrow(90 + ibw / 2, 180, dx, dy + dh / 2, color=INK, sw=1.7))
    p.append(arrow(90 + ibw / 2, 220, ex, ey + eh / 2, color=INK, sw=1.7))

    # компаратор праворуч
    cx = 660
    cb, cbw, cbh = textbox(cx, 200, "count !== expected ?", size=12, bold=True,
                           fill="#ffffff", stroke=POS, sw=1.8, min_w=170)
    p.append(cb)
    p.append(arrow(dx + dw, dy + dh / 2, cx - cbw / 2, 180, color=NEG, sw=1.7))
    p.append(text((dx + dw + cx - cbw / 2) / 2, dy + dh / 2 - 8, "count", size=9.5, color=NEG))
    p.append(arrow(ex + ew, ey + eh / 2, cx - cbw / 2, 220, color=FIELD, sw=1.7))
    p.append(text((ex + ew + cx - cbw / 2) / 2, ey + eh / 2 + 16, "expected", size=9.5, color=FIELD))

    # вердикт
    p.append(arrow(cx, 200 + cbh / 2, cx, 300, color=INK, sw=1.7))
    vb, vbw, vbh = textbox(cx, 332, "збіг → тиша\nрозбіжність →\nFAIL @ час", size=11, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.6, min_w=150)
    p.append(vb)

    render(os.path.join(OUT, "golden-model.svg"), W, H, *p,
           title="Самоперевірка = дві незалежні лічби поряд: DUT проти еталона")


# ── edge-timing: коли міняти входи й коли читати вихід відносно фронту ──────────
# Ідея: DUT защіпує на наростному фронті; входи міняємо на СПАДІ (безпечно),
# вихід читаємо ТРОХИ ПІСЛЯ наростного (коли встоявся) — інакше гонка / off-by-one.

def fig_edge_timing():
    W, H = 820, 366
    p = []
    ax0, ax1 = 90, 748
    top, bot = 96, 156            # рівні меандру такту
    seg = (ax1 - ax0) / 4.0
    xs = [ax0 + i * seg for i in range(5)]
    # clk стартує з 0: ↑ на x1 і x3, ↓ на x2
    pts = [(xs[0], bot), (xs[1], bot), (xs[1], top), (xs[2], top),
           (xs[2], bot), (xs[3], bot), (xs[3], top), (xs[4], top)]
    d = "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % q for q in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK))
    p.append(text(ax0 - 22, (top + bot) / 2 + 4, "clk", size=12, bold=True, color=INK, anchor="end"))

    # наростні фронти (гарячі, червоні) на x1, x3
    for xf in (xs[1], xs[3]):
        p.append(line(xf, top - 42, xf, bot + 98, color=POS, sw=1.6, dash="4 3"))
    p.append(text(xs[1], top - 52, "↑ФРОНТ: DUT защіпує count", size=10.5, color=POS, bold=True))
    p.append(text(xs[3], top - 52, "↑ФРОНТ", size=10.5, color=POS, bold=True))

    # спадний фронт (безпечний, зелений) на x2
    p.append(line(xs[2], top - 24, xs[2], bot + 98, color=FIELD, sw=1.6, dash="4 3"))
    p.append(text(xs[2], top - 34, "↓спад: безпечна зона", size=10.5, color=FIELD, bold=True))

    # міняємо входи на спаді
    p.append(arrow(xs[2], bot + 122, xs[2], bot + 98, color=FIELD, sw=1.8))
    p.append(fitbox(xs[2] - 108, bot + 124, 216, 48,
                    "МІНЯЄМО ВХОДИ тут (rst, en)\nу протифазі → вхід устоявся\nдо наступного ↑, без гонки",
                    size=9.5, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK))

    # читаємо вихід трохи ПІСЛЯ наростного фронту
    xread = xs[3] + seg * 0.15
    p.append(circle(xread, top, 4.5, fill=NEG, stroke=NEG, sw=1))
    p.append(arrow(xread, bot + 122, xread, top + 8, color=NEG, sw=1.8))
    p.append(fitbox(xread - 40, bot + 124, 210, 48,
                    "ЧИТАЄМО count тут — трохи ПІСЛЯ\n↑, коли <= вже защіпнув. На самому\n↑ → старе значення → off-by-one",
                    size=9.5, fill="#eef4ff", stroke=NEG, sw=1.5, color=INK))

    render(os.path.join(OUT, "edge-timing.svg"), W, H, *p,
           title="Дисципліна часу: входи — на спаді, вихід — трохи після наростного фронту")


# ── pitfalls: чотири пастки самоперевірного тестбенча ──────────────────────────
# Ідея: 2 пастки — баги дизайну (ловляться через X оператором !==),
# 1 — баг самого тестбенча (off-by-one), 1 — забутий $finish (вічний прогін).

def fig_pitfalls():
    W, H = 820, 384
    p = []
    cards = [
        (215, 122, NEG, "#eef4ff", "1 · Забутий скид → X",
         "Регістр без rst лишається X.\n!== ловить на ПЕРШОМУ фронті.\n(!= на X дав би X → проспав би.)\nБаг ДИЗАЙНУ."),
        (605, 122, POS, "#fdecea", "2 · Гонитва драйверів → X",
         "Два джерела женуть count →\nсимулятор дає X. Рецепт:\nвихід DUT — wire, жене ЛИШЕ\nдизайн. Баг ДИЗАЙНУ."),
        (215, 272, "#b8860b", "#fdf3d6", "3 · Off-by-one у зчитуванні",
         "Читаєш до защіпки <= → старе\nзначення → чесний DUT «відстає».\nЛікує: та сама фаза + #0.\nБаг ТЕСТБЕНЧА!"),
        (605, 272, MUTED, "#eef1f4", "4 · Забутий $finish",
         "always #5 clk=~clk тіпає\nВІЧНО → симуляція висить.\n$finish і в PASS, і в FAIL.\nБез нього тесту нема кінця."),
    ]
    for cx, cy, col, fill, title, body in cards:
        p.append(rect(cx - 186, cy - 64, 372, 128, fill=fill, stroke=col, sw=1.9, rx=10))
        p.append(text(cx, cy - 42, title, size=12.5, bold=True, color=col))
        p.append(mtext(cx, cy - 20, body, size=10, color=INK, lh=1.34))

    render(os.path.join(OUT, "pitfalls.svg"), W, H, *p,
           title="Чотири пастки: дві — баги дизайну (X), одна — баг тестбенча, одна — вічний прогін")


if __name__ == "__main__":
    fig_two_loops()
    fig_testbench()
    fig_four_values()
    fig_event_time()
    # hist-вставка
    fig_sim_cradles()
    fig_sim_lineage()
    fig_sim_credit()
    # proj-вставка
    fig_golden_model()
    fig_edge_timing()
    fig_pitfalls()
    print("OK: figures written to", OUT)
