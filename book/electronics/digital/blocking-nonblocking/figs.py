# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODEBG = "#f4f6f8"
CODEFONT = "'Consolas', 'DejaVu Sans Mono', monospace"


def codeblock(x, y, w, lines, size=12, lh=1.5, title=None, accent=INK):
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
        out.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
                   '><tspan xml:space="preserve">%s</tspan></text>'
                   % (x + pad, ty + i * size * lh, CODEFONT, size, INK, esc(ln)))
    return "".join(out), h


# ── fig 1: два оператори — дві миті ──────────────────────────────────────────
# Ідея: = читає й пише ОДРАЗУ (по черзі, як у C); <= читає всі праві частини
# ЗАРАЗ, а записує всі ліві РАЗОМ у кінці такту (двофазність).
def fig_two_moments():
    W, H = 780, 380
    p = []
    colw = 340
    lx, rx = 34, W - 34 - colw

    # ── блокуюче ──
    p.append(text(lx + colw / 2, 58, "Блокуюче  =  (одразу, по черзі)", size=14, bold=True, color=POS))
    cs, chh = codeblock(lx, 72, colw,
                        ["b = a;   // одразу: b дорівнює a",
                         "c = b;   // c бере вже НОВЕ b"],
                        size=12, accent=POS)
    p.append(cs)
    yb = 72 + chh + 26
    p.append(text(lx + colw / 2, yb, "рядок «блокує» наступний:", size=11, color=INK))
    p.append(text(lx + colw / 2, yb + 18, "запис стається до переходу далі", size=11, color=MUTED, italic=True))
    # часова вісь: два кроки
    ax = lx + 30
    p.append(line(ax, yb + 44, ax + colw - 60, yb + 44, color=INK, sw=1.6))
    for i, lab in enumerate(["b←a", "c←b"]):
        cx = ax + 60 + i * 150
        p.append(circle(cx, yb + 44, 5, fill=POS, stroke=POS))
        p.append(text(cx, yb + 66, lab, size=11, color=POS))
    p.append(text(lx + colw / 2, yb + 92, "дві окремі миті — як кроки програми на C", size=10, color=MUTED, italic=True))

    # ── неблокуюче ──
    p.append(text(rx + colw / 2, 58, "Неблокуюче  <=  (двофазно)", size=14, bold=True, color=NEG))
    ss, shh = codeblock(rx, 72, colw,
                        ["b <= a;  // читаємо праві",
                         "c <= b;  // ЧАСТИНИ разом — старе b"],
                        size=12, accent=NEG)
    p.append(ss)
    yn = 72 + shh + 26
    p.append(text(rx + colw / 2, yn, "фаза 1: усі праві частини читаються", size=11, color=INK))
    p.append(text(rx + colw / 2, yn + 18, "фаза 2: усі ліві записуються РАЗОМ", size=11, color=INK))
    # двофазна вісь
    ax2 = rx + 30
    p.append(line(ax2, yn + 44, ax2 + colw - 60, yn + 44, color=INK, sw=1.6))
    p.append(circle(ax2 + 30, yn + 44, 5, fill=FIELD, stroke=FIELD))
    p.append(text(ax2 + 30, yn + 66, "читання", size=10, color=FIELD, anchor="middle"))
    p.append(circle(ax2 + colw - 90, yn + 44, 5, fill=NEG, stroke=NEG))
    p.append(text(ax2 + colw - 90, yn + 66, "запис усіх", size=10, color=NEG, anchor="middle"))
    p.append(text(rx + colw / 2, yn + 92, "усі записи — в одну мить, наче одночасно", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-moments.svg"), W, H, *p,
           title="Той самий вигляд — різна мить запису")


# ── fig 2: обмін значеннями (swap) ───────────────────────────────────────────
# Ідея: a<=b; b<=a; РЕАЛЬНО міняє місцями (читає старі, пише разом);
# a=b; b=a; НЕ міняє — обидва стають b, бо друге читає вже нове.
def fig_swap():
    W, H = 780, 360
    p = []
    colw = 340
    lx, rx = 34, W - 34 - colw

    def cell(cx, cy, name, val, color):
        w, h = 58, 48
        out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#eef4ff" if color == NEG else "#fdecea",
                    stroke=color, sw=1.8, rx=5)]
        out.append(text(cx, cy - 4, name, size=12, color=color, bold=True))
        out.append(text(cx, cy + 16, val, size=13, color=INK, bold=True))
        return "".join(out)

    # ── неблокуюче: працює ──
    p.append(text(lx + colw / 2, 56, "a <= b;  b <= a;", size=14, bold=True, color=NEG))
    p.append(text(lx + colw / 2, 76, "обмін ВДАЄТЬСЯ", size=12, color=FIELD, bold=True))
    # до
    p.append(text(lx + colw / 2, 108, "до фронту:", size=11, color=MUTED))
    p.append(cell(lx + 100, 148, "a", "3", NEG))
    p.append(cell(lx + 240, 148, "b", "7", NEG))
    # стрілки хрест-навхрест
    p.append(arrow(lx + 100, 178, lx + 240, 214, color=FIELD, sw=1.8))
    p.append(arrow(lx + 240, 178, lx + 100, 214, color=FIELD, sw=1.8))
    p.append(text(lx + colw / 2, 200, "читаємо СТАРІ, пишемо разом", size=10, color=FIELD, italic=True, anchor="middle"))
    # після
    p.append(text(lx + colw / 2, 244, "після фронту:", size=11, color=MUTED))
    p.append(cell(lx + 100, 284, "a", "7", NEG))
    p.append(cell(lx + 240, 284, "b", "3", NEG))
    p.append(text(lx + colw / 2, 330, "справді помінялися місцями", size=11, color=FIELD, bold=True))

    # ── блокуюче: не працює ──
    p.append(text(rx + colw / 2, 56, "a = b;  b = a;", size=14, bold=True, color=POS))
    p.append(text(rx + colw / 2, 76, "обмін ЛАМАЄТЬСЯ", size=12, color=POS, bold=True))
    p.append(text(rx + colw / 2, 108, "до:", size=11, color=MUTED))
    p.append(cell(rx + 100, 148, "a", "3", POS))
    p.append(cell(rx + 240, 148, "b", "7", POS))
    # крок 1: a=b
    p.append(arrow(rx + 240, 178, rx + 100, 208, color=POS, sw=1.8))
    p.append(text(rx + colw / 2, 196, "1) a = b → a стає 7 (3 втрачено)", size=10, color=POS, anchor="middle"))
    p.append(text(rx + colw / 2, 220, "2) b = a → бере вже НОВЕ a = 7", size=10, color=POS, anchor="middle"))
    p.append(text(rx + colw / 2, 244, "після:", size=11, color=MUTED))
    p.append(cell(rx + 100, 284, "a", "7", POS))
    p.append(cell(rx + 240, 284, "b", "7", POS))
    p.append(text(rx + colw / 2, 330, "обидва 7 — трійку загублено", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "swap.svg"), W, H, *p,
           title="Обмін двох значень: <= міняє, = губить")


# ── fig 3: зсувний регістр ───────────────────────────────────────────────────
# Ідея: три тригери a→b→c. З <= на фронті кожен бере СТАРЕ значення сусіда —
# біт крокує на один щабель. З = усі беруть уже оновлене — біт «протікає»
# крізь усі три за один фронт, регістр колапсує в один тригер.
def fig_shift():
    W, H = 780, 400
    p = []

    def ff(cx, cy, name, val, color):
        w, h = 66, 56
        out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#eef4ff" if color == NEG else "#fdecea",
                    stroke=color, sw=1.8, rx=5)]
        out.append(text(cx, cy - 6, name, size=12, color=color, bold=True))
        out.append(text(cx, cy + 15, val, size=14, color=INK, bold=True))
        # трикутник такту
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="1.4"/>'
                   % (cx - w / 2, cy + h / 2 - 6, cx - w / 2 + 9, cy + h / 2 - 11, cx - w / 2, cy + h / 2 - 16, color))
        return "".join(out)

    xs = [150, 360, 570]
    labels = ["a", "b", "c"]

    # ── неблокуюче: чистий зсув ──
    yr = 118
    p.append(text(W / 2, 58, "always @(posedge clk) begin  a <= in;  b <= a;  c <= b;  end", size=13, bold=True, color=NEG))
    p.append(text(W / 2, 80, "кожен тригер бере СТАРЕ значення сусіда → біт крокує на один щабель", size=11, color=INK))
    p.append(text(70, yr, "було:", size=11, color=MUTED, anchor="start"))
    vals_before = ["1", "0", "0"]
    for x, lab, v in zip(xs, labels, vals_before):
        p.append(ff(x, yr, lab, v, NEG))
    # стрілки-передачі старих значень
    p.append(text(W / 2, yr + 46, "in=0 →", size=11, color=MUTED, anchor="middle"))
    for i in range(len(xs) - 1):
        p.append(arrow(xs[i] + 33, yr + 40, xs[i + 1] - 33, yr + 40, color=FIELD, sw=1.7))
    yr2 = yr + 78
    p.append(text(70, yr2, "стало:", size=11, color=MUTED, anchor="start"))
    vals_after = ["0", "1", "0"]
    for x, lab, v in zip(xs, labels, vals_after):
        p.append(ff(x, yr2, lab, v, NEG))
    p.append(text(W / 2, yr2 + 46, "одиниця зсунулась на ОДИН щабель — це справжній зсувний регістр", size=11, color=FIELD, bold=True))

    # роздільник
    p.append(line(34, 268, W - 34, 268, color=MUTED, sw=1.0, dash="4,4"))

    # ── блокуюче: колапс ──
    yb = 312
    p.append(text(W / 2, 296, "…з  =  замість  <=  :  a = in;  b = a;  c = b;", size=13, bold=True, color=POS))
    p.append(ff(xs[0], yb, "a", "0", POS))
    p.append(ff(xs[1], yb, "b", "0", POS))
    p.append(ff(xs[2], yb, "c", "0", POS))
    for i in range(len(xs) - 1):
        p.append(arrow(xs[i] + 33, yb, xs[i + 1] - 33, yb, color=POS, sw=1.7))
    p.append(text(W / 2, yb + 44, "in=0 «протікає» крізь усі три за ОДИН фронт → біти не зсуваються, регістр злипся в один",
                  size=11, color=POS, bold=True))

    render(os.path.join(OUT, "shift.svg"), W, H, *p,
           title="Зсувний регістр: <= крокує, = колапсує")


# ── fig 4: обчислювальний конвеєр ────────────────────────────────────────────
# Ідея: три щаблі з регістрами між ними. З <= кожен щабель бере готовий
# результат сусіда з МИНУЛОГО такту — три набори даних повзуть одночасно,
# y виходить щотакту з затримкою 3. З = усі щаблі злипаються в один довгий
# комбінаційний ланцюг (три множення + два додавання) за ОДИН фронт.
def fig_pipeline():
    W, H = 800, 430
    p = []

    def stage(cx, cy, title, sub, color):
        w, h = 132, 62
        out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#eef4ff" if color == NEG else "#fdecea",
                    stroke=color, sw=1.8, rx=6)]
        out.append(text(cx, cy - 8, title, size=12, color=color, bold=True))
        out.append(text(cx, cy + 13, sub, size=11, color=INK))
        return "".join(out)

    def reg(cx, cy, color):
        # маленька засувка-регістр між щаблями (трикутник такту)
        w, h = 20, 40
        out = [rect(cx - w / 2, cy - h / 2, w, h, fill=BG, stroke=color, sw=1.6, rx=3)]
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" '
                   'stroke="%s" stroke-width="1.3"/>'
                   % (cx - w / 2, cy + h / 2 - 5, cx - w / 2 + 7, cy + h / 2 - 9,
                      cx - w / 2, cy + h / 2 - 13, color))
        return "".join(out)

    xs = [150, 400, 650]

    # ── неблокуюче: справжній конвеєр ──
    yr = 118
    p.append(text(W / 2, 56, "Конвеєр на  <=  :  щаблі розділені регістрами", size=14, bold=True, color=NEG))
    p.append(text(W / 2, 78, "кожен щабель бере результат сусіда з МИНУЛОГО такту — три набори повзуть одночасно",
                  size=11, color=INK))
    p.append(stage(xs[0], yr, "щабель 1", "p ← a·k", NEG))
    p.append(stage(xs[1], yr, "щабель 2", "s ← p1+p2", NEG))
    p.append(stage(xs[2], yr, "щабель 3", "y ← s+p3", NEG))
    # регістри-межі між щаблями
    p.append(reg((xs[0] + xs[1]) / 2, yr, FIELD))
    p.append(reg((xs[1] + xs[2]) / 2, yr, FIELD))
    p.append(arrow(xs[0] + 66, yr, (xs[0] + xs[1]) / 2 - 10, yr, color=INK, sw=1.6))
    p.append(arrow((xs[0] + xs[1]) / 2 + 10, yr, xs[1] - 66, yr, color=INK, sw=1.6))
    p.append(arrow(xs[1] + 66, yr, (xs[1] + xs[2]) / 2 - 10, yr, color=INK, sw=1.6))
    p.append(arrow((xs[1] + xs[2]) / 2 + 10, yr, xs[2] - 66, yr, color=INK, sw=1.6))
    p.append(text((xs[0] + xs[1]) / 2, yr + 42, "регістр", size=9, color=FIELD, italic=True))
    p.append(text((xs[1] + xs[2]) / 2, yr + 42, "регістр", size=9, color=FIELD, italic=True))
    p.append(text(xs[2] + 78, yr, "→ y", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(W / 2, yr + 74, "результат y виходить щотакту — але із затримкою 3 такти (стільки щаблів)",
                  size=11, color=FIELD, bold=True))

    # роздільник
    p.append(line(34, 268, W - 34, 268, color=MUTED, sw=1.0, dash="4,4"))

    # ── блокуюче: колапс у довгий ланцюг ──
    yb = 340
    p.append(text(W / 2, 296, "…з  =  замість  <=  :  s = p1+p2;  y = s+p3;  усі беруть ВЖЕ нові значення",
                  size=13, bold=True, color=POS))
    # довгий комбінаційний ланцюг без регістрів
    cs, chh = codeblock(90, yb - 26, W - 180,
                        ["y = a·k1 + b·k2 + c·k3   // весь вираз за ОДИН фронт"],
                        size=12, accent=POS)
    p.append(cs)
    p.append(text(W / 2, yb + 44, "регістри-межі зникли → конвеєр колапсує в один довгий ланцюг: "
                                  "правильне число, але вбита частота й затримка",
                  size=11, color=POS, bold=True))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Конвеєр: <= розділяє щаблі, = зливає їх у один")


# ── fig 5: серіалізатор на зсувному регістрі ─────────────────────────────────
# Ідея: зсувний регістр щотакту віддає молодший біт у tx і зсувається на один
# розряд. З <= кадр UART виходить біт-за-бітом (старт, 8 даних LSB, стоп).
# З = поразрядний зсув q0→q1→q2→q3 колапсує — вхід протікає за один фронт.
def fig_serializer():
    W, H = 800, 430
    p = []

    def bitcell(cx, cy, v, color, w=34, h=34):
        out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#eef4ff" if color == NEG else "#fdecea",
                    stroke=color, sw=1.6, rx=4)]
        out.append(text(cx, cy + 5, v, size=13, color=INK, bold=True))
        return "".join(out)

    # ── неблокуюче: кадр виходить біт-за-бітом ──
    p.append(text(W / 2, 56, "Серіалізатор на  <=  :  зсув на один розряд за такт", size=14, bold=True, color=NEG))
    p.append(text(W / 2, 78, "щотакту молодший біт іде в лінію tx, регістр зсувається — кадр виходить у часі",
                  size=11, color=INK))
    # зсувний регістр: 10 біт кадру
    frame = ["1", "1", "0", "1", "0", "0", "1", "1", "0", "0"]  # {стоп, дані, старт}, молодший праворуч
    bx0 = 120
    for i, b in enumerate(frame):
        p.append(bitcell(bx0 + i * 40, 118, b, NEG))
    p.append(text(bx0 - 34, 118, "…1", size=11, color=MUTED, anchor="middle"))
    p.append(text(bx0 + len(frame) * 40 - 6, 148, "молодший →", size=9, color=MUTED, anchor="middle"))
    # стрілка зсуву й видача біта
    p.append(arrow(bx0 + len(frame) * 40 - 24, 148, bx0 + len(frame) * 40 + 26, 148, color=FIELD, sw=1.8))
    p.append(text(bx0 + len(frame) * 40 + 44, 152, "tx", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(W / 2, 168, "shreg зсув на 1 →", size=9, color=MUTED, anchor="middle"))

    # хвиля кадру UART
    wy = 210
    seq = [1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1]  # спокій, старт, 8 даних, стоп, спокій
    step = 46
    wx0 = 90
    hi, lo = wy, wy + 34
    labels = ["спок", "СТАРТ", "d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "СТОП", "спок"]
    prev = seq[0]
    px = wx0
    py = hi if prev else lo
    path = ["M%.1f %.1f" % (px, py)]
    for i, v in enumerate(seq):
        ny = hi if v else lo
        if ny != py:
            path.append("L%.1f %.1f" % (px, ny))
        px2 = px + step
        path.append("L%.1f %.1f" % (px2, ny))
        # підпис під інтервалом
        p.append(text(px + step / 2, wy + 54, labels[i], size=8, color=MUTED))
        px, py = px2, ny
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(path), NEG))
    p.append(text(wx0 - 6, hi + 4, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(wx0 - 6, lo + 4, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(W / 2, wy + 78, "кожен біт = один такт: старт-0, вісім даних молодшим уперед, стоп-1 — чіткий кадр",
                  size=11, color=FIELD, bold=True))

    # роздільник
    p.append(line(34, 312, W - 34, 312, color=MUTED, sw=1.0, dash="4,4"))

    # ── блокуюче: колапс поразрядного зсуву ──
    yb = 356
    p.append(text(W / 2, 340, "…з  =  :  q0=in; q1=q0; q2=q1; q3=q2;  — вхід протікає крізь усі за ОДИН фронт",
                  size=13, bold=True, color=POS))
    xs = [230, 330, 430, 530]
    for i, lab in enumerate(["q0", "q1", "q2", "q3"]):
        p.append(bitcell(xs[i], yb + 8, "=in", POS, w=44, h=32))
        p.append(text(xs[i], yb - 12, lab, size=11, color=POS, bold=True))
        if i < 3:
            p.append(arrow(xs[i] + 24, yb + 8, xs[i + 1] - 24, yb + 8, color=POS, sw=1.7))
    p.append(text(W / 2, yb + 44, "усі розряди миттю однакові → регістр колапсує в один тригер, кадр вироджується",
                  size=11, color=POS, bold=True))

    render(os.path.join(OUT, "serializer.svg"), W, H, *p,
           title="Серіалізатор: <= крокує кадр, = зливає його")


if __name__ == "__main__":
    fig_two_moments()
    fig_swap()
    fig_shift()
    fig_pipeline()
    fig_serializer()
    print("figures written to", OUT)
