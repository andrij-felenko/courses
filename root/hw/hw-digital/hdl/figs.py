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


# ── describe-vs-program: однаковий рядок — протилежний сенс ────────────────────
# Ідея: ліворуч C виконує рядки ПО ЧЕРЗІ (кроки в часі, стрілка вниз);
# праворуч Verilog ОПИСУЄ суматор, що існує постійно (дроти, не кроки).

def fig_describe_vs_program():
    W, H = 760, 360
    p = []
    colw = 320
    lx, rx = 40, W - 40 - colw

    # ── ЛІВО: C — кроки в часі ──
    p.append(text(lx + colw / 2, 56, "C на мікроконтролері", size=14, bold=True, color=NEG))
    p.append(text(lx + colw / 2, 74, "рядки виконуються по черзі", size=11, color=MUTED, italic=True))
    csrc, ch = codeblock(lx, 88, colw,
                         ["x = read(A);", "y = read(B);", "c = x + y;"],
                         size=13, accent=NEG)
    p.append(csrc)
    # стрілка часу збоку
    ay0, ay1 = 100, 88 + ch - 12
    p.append(arrow(lx - 14, ay0, lx - 14, ay1, color=NEG, sw=1.8))
    p.append(text(lx - 22, (ay0 + ay1) / 2, "час", size=10, color=NEG, anchor="end", italic=True))
    p.append(text(lx + colw / 2, 88 + ch + 60,
                  "крок за кроком: спершу одне", size=11, color=INK))
    p.append(text(lx + colw / 2, 88 + ch + 78,
                  "читання, тоді друге, тоді сума", size=11, color=INK))

    # ── ПРАВО: Verilog — постійний суматор ──
    p.append(text(rx + colw / 2, 56, "Verilog (опис заліза)", size=14, bold=True, color=POS))
    p.append(text(rx + colw / 2, 74, "усе існує водночас", size=11, color=MUTED, italic=True))
    vsrc, vh = codeblock(rx, 88, colw, ["assign c = a + b;"], size=13, accent=POS)
    p.append(vsrc)

    # схема суматора під кодом
    cy = 88 + vh + 70
    bx = rx + colw / 2 - 45
    sb, sbw, sbh = textbox(rx + colw / 2, cy, "+", size=22, bold=True,
                           fill="#fdecea", stroke=POS, sw=2, min_w=64)
    # входи a, b зліва
    p.append(line(rx + 20, cy - 14, rx + colw / 2 - sbw / 2, cy - 14, color=INK, sw=1.6))
    p.append(line(rx + 20, cy + 14, rx + colw / 2 - sbw / 2, cy + 14, color=INK, sw=1.6))
    p.append(text(rx + 14, cy - 10, "a", size=12, color=INK, anchor="end", italic=True))
    p.append(text(rx + 14, cy + 18, "b", size=12, color=INK, anchor="end", italic=True))
    # вихід c
    p.append(arrow(rx + colw / 2 + sbw / 2, cy, rx + colw - 16, cy, color=INK, sw=1.6))
    p.append(text(rx + colw - 10, cy - 6, "c", size=12, color=INK, anchor="start", italic=True))
    p.append(sb)
    p.append(text(rx + colw / 2, cy + 50,
                  "суматор завжди тримає на виході суму", size=11, color=INK))

    render(os.path.join(OUT, "describe-vs-program.svg"), W, H, *p,
           title="Однаковий рядок — протилежний сенс: наказ у часі чи постійне залізо")


# ── module: чорна скринька з виводами ─────────────────────────────────────────
# Ідея: input/output = ніжки корпусу (розпіновка), тіло = схема всередині,
# модулі вкладаються один в одного.

def fig_module():
    W, H = 720, 340
    p = []
    # великий модуль-корпус
    mx, my, mw, mh = 120, 70, 360, 200
    p.append(rect(mx, my, mw, mh, fill="#fbfcfe", stroke=INK, sw=2.2, rx=10))
    p.append(text(mx + mw / 2, my + 28, "module adder", size=15, bold=True, color=INK))

    # ніжки-входи зліва
    for i, lab in enumerate(["a [7:0]", "b [7:0]"]):
        py = my + 80 + i * 60
        p.append(line(mx - 46, py, mx, py, color=NEG, sw=2.0))
        p.append(circle(mx - 46, py, 4, fill=BG, stroke=NEG, sw=2))
        p.append(text(mx - 54, py + 4, lab, size=11, color=NEG, anchor="end"))
    p.append(text(mx - 30, my + mh - 8, "входи (input)", size=10, color=NEG, anchor="middle", italic=True))

    # ніжка-вихід справа
    py = my + 110
    p.append(line(mx + mw, py, mx + mw + 46, py, color=POS, sw=2.0))
    p.append(circle(mx + mw + 46, py, 4, fill=BG, stroke=POS, sw=2))
    p.append(text(mx + mw + 54, py + 4, "sum [7:0]", size=11, color=POS, anchor="start"))
    p.append(text(mx + mw + 30, my + mh - 8, "вихід (output)", size=10, color=POS, anchor="middle", italic=True))

    # тіло: assign-суматор усередині
    ib, ibw, ibh = textbox(mx + mw / 2, my + 120, "assign sum = a + b;",
                           size=13, fill=CODEBG, stroke=LINE, sw=1.5, pad=12)
    p.append(ib)
    p.append(text(mx + mw / 2, my + 120 + ibh / 2 + 22, "тіло = схема всередині", size=10, color=MUTED, italic=True))

    # підпис-аналогія
    p.append(text(W / 2, H - 36, "input / output — як ніжки корпусу (розпіновка); [7:0] — шина з 8 дротів",
                  size=11, color=INK))
    p.append(text(W / 2, H - 16, "модулі вкладають один в одного, як мікросхеми на платі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "module.svg"), W, H, *p,
           title="Модуль: чорна скринька з названими виводами")


# ── comb-vs-seq: комбінаційний (миттєвий) проти реєстрового (по такту) ─────────
# Ідея: assign → вентиль без пам'яті, реагує миттєво; always @(posedge clk) →
# тригер, оновлюється лише на фронті, має пам'ять.

def fig_comb_vs_seq():
    W, H = 760, 330
    p = []
    colw = 330
    lx, rx = 36, W - 36 - colw

    # ── комбінаційний ──
    p.append(text(lx + colw / 2, 56, "Комбінаційний (миттєвий)", size=14, bold=True, color=FIELD))
    cs, chh = codeblock(lx, 70, colw, ["assign y = a & b;"], size=13, accent=FIELD)
    p.append(cs)
    # вентиль AND
    gy = 70 + chh + 70
    gx = lx + colw / 2
    p.append(line(lx + 24, gy - 14, gx - 36, gy - 14, color=INK, sw=1.6))
    p.append(line(lx + 24, gy + 14, gx - 36, gy + 14, color=INK, sw=1.6))
    p.append(text(lx + 18, gy - 10, "a", size=11, color=INK, anchor="end", italic=True))
    p.append(text(lx + 18, gy + 18, "b", size=11, color=INK, anchor="end", italic=True))
    # D-подібний символ AND
    p.append('<path d="M%.1f %.1f L%.1f %.1f A28 28 0 0 1 %.1f %.1f L%.1f %.1f Z" '
             'fill="#eafaf0" stroke="%s" stroke-width="1.8"/>'
             % (gx - 36, gy - 22, gx, gy - 22, gx, gy + 22, gx - 36, gy + 22, FIELD))
    p.append(text(gx - 14, gy + 4, "&", size=15, color=FIELD, bold=True))
    p.append(arrow(gx + 28, gy, lx + colw - 18, gy, color=INK, sw=1.6))
    p.append(text(lx + colw - 12, gy + 4, "y", size=11, color=INK, anchor="start", italic=True))
    p.append(text(lx + colw / 2, gy + 56, "вентиль AND — без пам'яті", size=11, color=INK))
    p.append(text(lx + colw / 2, gy + 74, "вихід міняється миттєво за входами", size=10, color=MUTED, italic=True))

    # ── реєстровий ──
    p.append(text(rx + colw / 2, 56, "Реєстровий (по такту)", size=14, bold=True, color=NEG))
    ss, shh = codeblock(rx, 70, colw, ["always @(posedge clk)", "  q <= d;"], size=13, accent=NEG)
    p.append(ss)
    # тригер (прямокутник з трикутником такту)
    ty = 70 + shh + 64
    twx, tww, twh = rx + colw / 2, 90, 64
    fx, fy = twx - tww / 2, ty - twh / 2
    p.append(rect(fx, fy, tww, twh, fill="#eef4ff", stroke=NEG, sw=1.8, rx=4))
    p.append(text(twx, ty - 6, "D-тригер", size=11, color=NEG, bold=True))
    # вхід d
    p.append(line(fx - 30, fy + 16, fx, fy + 16, color=INK, sw=1.6))
    p.append(text(fx - 36, fy + 20, "d", size=11, color=INK, anchor="end", italic=True))
    # вихід q
    p.append(arrow(fx + tww, fy + 16, fx + tww + 30, fy + 16, color=INK, sw=1.6))
    p.append(text(fx + tww + 36, fy + 20, "q", size=11, color=INK, anchor="start", italic=True))
    # вхід такту (трикутник)
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (fx, fy + twh - 16, fx + 12, fy + twh - 22, fx, fy + twh - 28, NEG))
    p.append(line(fx - 30, fy + twh - 22, fx, fy + twh - 22, color=NEG, sw=1.6))
    p.append(text(fx - 36, fy + twh - 18, "clk", size=10, color=NEG, anchor="end"))
    p.append(text(rx + colw / 2, ty + twh / 2 + 26, "оновлюється лише на фронті такту", size=11, color=INK))
    p.append(text(rx + colw / 2, ty + twh / 2 + 44, "тримає стан — це пам'ять", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "comb-vs-seq.svg"), W, H, *p,
           title="Два роди опису породжують фізично різне залізо")


# ── synth-not-exec: компіляція+виконання проти синтезу+втілення ────────────────
# Ідея: софт іде в інструкції, що процесор виконує в ЧАСІ; HDL іде в схему,
# що тканина FPGA втілює — і вона працює вся НАРАЗ.

def fig_synth_not_exec():
    W, H = 780, 320
    p = []

    def chain(y, title, color, src, mid, midlab, tgt, tgtlab, note):
        out = []
        out.append(text(40, y - 36, title, size=13, bold=True, color=color))
        # код
        bx, bw = 40, 150
        b1, h1 = codeblock(bx, y - 22, bw, src, size=11, accent=color)
        out.append(b1)
        # стрілка-перетворення
        out.append(arrow(bx + bw + 6, y + 6, bx + bw + 66, y + 6, color=color, sw=2.0))
        out.append(text(bx + bw + 36, y - 6, mid, size=10, color=color, bold=True))
        # середина
        mx2 = bx + bw + 72
        m1, mw1, mh1 = textbox(mx2 + 80, y + 6, midlab, size=11, fill=CODEBG, stroke=color, sw=1.6)
        out.append(m1)
        # стрілка до цілі
        out.append(arrow(mx2 + 80 + mw1 / 2 + 6, y + 6, mx2 + 80 + mw1 / 2 + 60, y + 6, color=color, sw=2.0))
        # ціль
        tx = mx2 + 80 + mw1 / 2 + 66
        t1, tw1, th1 = textbox(tx + 80, y + 6, tgt, size=11, bold=True, fill=fillfor(color), stroke=color, sw=1.8)
        out.append(t1)
        out.append(text(tx + 80, y + th1 / 2 + 18, tgtlab, size=10, color=MUTED, italic=True))
        out.append(text(40, y + 70, note, size=11, color=INK, anchor="start"))
        return out

    def fillfor(c):
        return {NEG: "#eef4ff", POS: "#fdecea"}.get(c, FILL)

    p += chain(95, "Софт: код → виконання", NEG,
               ["int c =", "  a + b;"], "компілятор",
               "LD · ADD · ST", "процесор\nвиконує", "крок за кроком у часі",
               "одна інструкція по одній — результат розгорнуто в ЧАСІ")

    # роздільник
    p.append(line(40, 175, W - 40, 175, color="#dddddd", sw=1.2, dash="5 4"))

    p += chain(245, "HDL: код → синтез", POS,
               ["assign c", "  = a+b;"], "синтезатор",
               "вентилі · тригери", "тканина FPGA\nвтілює", "усе працює вся нараз",
               "усі вентилі існують разом — результат розгорнуто в ПРОСТОРІ")

    render(os.path.join(OUT, "synth-not-exec.svg"), W, H, *p,
           title="Синтез ≠ виконання: однакові на вигляд мови — різна доля коду")


# ── same-code-diff-hw: той самий вираз — різне залізо за контекстом ────────────
# Ідея: один assign → один суматор; повторений → багато суматорів паралельно;
# усередині always @(posedge clk) → суматор ПЛЮС регістр.

def fig_same_code_diff_hw():
    W, H = 780, 340
    p = []
    colw = 232
    xs = [24, 24 + colw + 16, 24 + 2 * (colw + 16)]

    def adder(cx, cy, label_out="c"):
        out = [textbox(cx, cy, "+", size=18, bold=True, fill="#fdecea", stroke=POS, sw=1.8, min_w=46)[0]]
        out.append(line(cx - 44, cy - 10, cx - 18, cy - 10, color=INK, sw=1.4))
        out.append(line(cx - 44, cy + 10, cx - 18, cy + 10, color=INK, sw=1.4))
        out.append(arrow(cx + 18, cy, cx + 44, cy, color=INK, sw=1.4))
        return out

    # ── 1: один суматор ──
    p.append(text(xs[0] + colw / 2, 58, "assign c = a + b;", size=12, bold=True, color=INK))
    p += adder(xs[0] + colw / 2, 150)
    p.append(text(xs[0] + colw / 2, 230, "ОДИН суматор", size=12, color=POS, bold=True))

    # ── 2: вісім суматорів паралельно ──
    p.append(text(xs[1] + colw / 2, 58, "той самий вираз × 8", size=12, bold=True, color=INK))
    for i in range(4):
        yy = 100 + i * 36
        b, bw, bh = textbox(xs[1] + colw / 2 - 40, yy, "+", size=12, bold=True,
                            fill="#fdecea", stroke=POS, sw=1.4, min_w=34)
        p.append(b)
        b2, _, _ = textbox(xs[1] + colw / 2 + 40, yy, "+", size=12, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.4, min_w=34)
        p.append(b2)
    p.append(text(xs[1] + colw / 2, 256, "ВІСІМ суматорів", size=12, color=POS, bold=True))
    p.append(text(xs[1] + colw / 2, 274, "працюють паралельно", size=10, color=MUTED, italic=True))

    # ── 3: суматор + регістр ──
    p.append(text(xs[2] + colw / 2, 58, "always @(posedge clk)", size=11, bold=True, color=INK))
    cx3 = xs[2] + colw / 2
    p += adder(cx3 - 28, 150)
    # регістр після суматора
    rgx, rgw, rgh = cx3 + 44, 52, 44
    p.append(rect(rgx - rgw / 2, 150 - rgh / 2, rgw, rgh, fill="#eef4ff", stroke=NEG, sw=1.6, rx=4))
    p.append(text(rgx, 150 + 4, "рег", size=11, color=NEG, bold=True))
    p.append(arrow(cx3 + 16, 150, rgx - rgw / 2, 150, color=INK, sw=1.4))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (rgx - rgw / 2, 150 + rgh / 2 - 6, rgx - rgw / 2 + 9, 150 + rgh / 2 - 11,
                rgx - rgw / 2, 150 + rgh / 2 - 16, NEG))
    p.append(text(cx3, 230, "суматор + РЕГІСТР", size=12, color=NEG, bold=True))
    p.append(text(cx3, 248, "результат фіксує такт", size=10, color=MUTED, italic=True))

    # вертикальні роздільники
    for sx in (xs[1] - 8, xs[2] - 8):
        p.append(line(sx, 44, sx, 290, color="#e2e2e2", sw=1.0))

    p.append(text(W / 2, H - 18, "опис однаковий — залізо різне, бо різний контекст",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "same-code-diff-hw.svg"), W, H, *p,
           title="Той самий вираз розгортається в різну схему")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки proj-verilog-first-projects
# ════════════════════════════════════════════════════════════════════════════

# ── blinker: той самий опис — і текст, і схема ─────────────────────────────────

def fig_blinker():
    W, H = 780, 320
    p = []
    # ліворуч — код
    src = [
        "module blink(",
        "  input  clk,",
        "  output led);",
        "  reg [23:0] cnt = 0;",
        "  always @(posedge clk)",
        "    cnt <= cnt + 1;",
        "  assign led = cnt[23];",
        "endmodule",
    ]
    b, bh = codeblock(40, 64, 300, src, size=12, accent=INK, title="blink.v — читає людина")
    p.append(b)

    # праворуч — схема
    rx = 400
    p.append(text(rx + 170, 56, "у що це перекладе синтез", size=12, bold=True, color=POS))
    # лічильник
    cb, cbw, cbh = textbox(rx + 90, 130, "лічильник cnt\n[23:0]\n(банк тригерів)", size=11,
                           bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(cb)
    # суматор +1 у петлі
    ab, abw, abh = textbox(rx + 90, 240, "+1", size=15, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.8, min_w=58)
    p.append(ab)
    # петля cnt -> +1 -> cnt
    p.append(arrow(rx + 90, 130 + cbh / 2, rx + 90, 240 - abh / 2, color=INK, sw=1.6))
    p.append(line(rx + 90 + abw / 2, 240, rx + 175, 240, color=INK, sw=1.6))
    p.append(line(rx + 175, 240, rx + 175, 130, color=INK, sw=1.6))
    p.append(arrow(rx + 175, 130, rx + 90 + cbw / 2, 130, color=INK, sw=1.6))
    p.append(text(rx + 182, 188, "зворотний", size=9, color=MUTED, anchor="start"))
    p.append(text(rx + 182, 200, "зв'язок", size=9, color=MUTED, anchor="start"))
    # такт у лічильник
    p.append(line(rx + 10, 130, rx + 90 - cbw / 2, 130, color=NEG, sw=1.6))
    p.append(text(rx + 6, 134, "clk", size=10, color=NEG, anchor="end"))
    # вихідний тригер cnt[23] -> led
    tb, tbw, tbh = textbox(rx + 250, 130, "тригер\nled", size=11, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(arrow(rx + 90 + cbw / 2, 130, rx + 250 - tbw / 2, 130, color=INK, sw=1.6))
    p.append(text((rx + 90 + cbw / 2 + rx + 250 - tbw / 2) / 2, 122, "cnt[23]", size=9, color=MUTED))
    p.append(tb)
    p.append(arrow(rx + 250 + tbw / 2, 130, rx + 340, 130, color=INK, sw=1.6))
    p.append(text(rx + 346, 134, "LED", size=11, color=INK, anchor="start", bold=True))

    p.append(text(W / 2, H - 16, "старший біт перемикається у 2²⁴ разів повільніше за такт — око бачить блимання",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "blinker.svg"), W, H, *p,
           title="Мигалка: той самий опис — і текст для людини, і схема для кремнію")


# ── uart: три блоки передавача + кадр у часі ──────────────────────────────────

def fig_uart():
    W, H = 800, 380
    p = []
    # три блоки в ряд усередині модуля
    mx, my, mw, mh = 40, 60, 720, 170
    p.append(rect(mx, my, mw, mh, fill="#fbfcfe", stroke=INK, sw=1.8, rx=10))
    p.append(text(mx + 14, my + 22, "module uart_tx", size=12, bold=True, color=INK, anchor="start"))

    blocks = [
        ("Дільник бода\n(лічильник ÷N)", "#eef4ff", NEG, "задає швидкість:\n1 імпульс на біт"),
        ("Автомат (FSM)\nIDLE→START→\n8×DATA→STOP", "#eafaf0", FIELD, "коли вантажити,\nколи зсувати"),
        ("Зсувний реєстр\n10 бітів кадру", "#f2ecf8", "#8a5fb0", "виштовхує\nпо одному біту"),
    ]
    bw = 190
    gap = (mw - 3 * bw) / 4
    cxs = []
    for i, (lab, fill, col, note) in enumerate(blocks):
        bx = mx + gap + i * (bw + gap)
        b = fitbox(bx, my + 50, bw, 66, lab, size=11, fill=fill, stroke=col, sw=1.8, bold=True, color=col)
        p.append(b)
        cxs.append((bx, bx + bw))
        p.append(mtext(bx + bw / 2, my + 138, note, size=9, color=MUTED, lh=1.25))
        if i > 0:
            p.append(arrow(cxs[i - 1][1] + 4, my + 83, bx - 4, my + 83, color=INK, sw=1.7))
    # тик від дільника до автомата вже стрілкою; вихід TX
    p.append(arrow(cxs[2][1], my + 83, mx + mw - 6, my + 83, color=POS, sw=2.0))
    p.append(text(mx + mw - 2, my + 70, "TX", size=12, color=POS, anchor="end", bold=True))

    # ── кадр у часі ──
    wy = 300
    wx0, wx1 = 70, 730
    unit = (wx1 - wx0) / 11.0
    # рівні: 1 = верх, 0 = низ
    hi, lo = wy - 26, wy + 8
    # послідовність: спокій(1), старт(0), d0..d7, стоп(1)  -> приклад байта 0b01001011
    bits = [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1]  # idle, start, потім дані LSB-first, stop
    labels = ["спокій", "старт", "d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "стоп"]
    x = wx0
    prev = hi if bits[0] else lo
    pts = []
    for i, bval in enumerate(bits):
        ylvl = hi if bval else lo
        if i > 0 and ylvl != prev:
            pts.append("%.1f,%.1f" % (x, prev))
            pts.append("%.1f,%.1f" % (x, ylvl))
        pts.append("%.1f,%.1f" % (x, ylvl))
        pts.append("%.1f,%.1f" % (x + unit, ylvl))
        # підпис фази
        col = MUTED
        if labels[i] == "старт":
            col = POS
        elif labels[i] == "стоп":
            col = FIELD
        p.append(text(x + unit / 2, wy + 30, labels[i], size=9, color=col))
        x += unit
        prev = ylvl
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), INK))
    p.append(text(wx0 - 8, hi + 4, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(wx0 - 8, lo + 4, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(W / 2, wy + 54, "кадр у часі: спокій=1, провал старту, вісім даних молодшим бітом уперед, стоп=1",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "uart.svg"), W, H, *p,
           title="Передавач UART: три знайомі блоки в одному модулі")


# ── testbench: перевірка модуля в симуляторі до плати ─────────────────────────

def fig_testbench():
    W, H = 760, 360
    p = []
    # рамка симулятора
    sx, sy, sw, sh = 40, 56, 460, 200
    p.append(rect(sx, sy, sw, sh, fill="#f6f8fb", stroke=MUTED, sw=1.6, rx=10, ))
    p.append(text(sx + 14, sy + 22, "симулятор (на комп'ютері, не на платі)", size=11,
                  bold=True, color=MUTED, anchor="start"))

    # тестбенч
    tb, tbw, tbh = textbox(sx + 110, sy + 120, "тестбенч\n«несправжній світ»\nгенерує clk,\nдає data, start",
                           size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(tb)
    # DUT
    db, dbw, dbh = textbox(sx + 340, sy + 120, "DUT\nuart_tx.v\n(наш дизайн)", size=11,
                           bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(db)
    # стрілки tb -> dut (clk/data/start), dut -> назад (TX як хвиля)
    p.append(arrow(sx + 110 + tbw / 2, sy + 110, sx + 340 - dbw / 2, sy + 110, color=INK, sw=1.7))
    p.append(text((sx + 110 + sx + 340) / 2, sy + 100, "clk · data · start", size=9, color=INK))
    p.append(arrow(sx + 340 - dbw / 2, sy + 140, sx + 110 + tbw / 2, sy + 140, color=POS, sw=1.7))
    p.append(text((sx + 110 + sx + 340) / 2, sy + 156, "TX (хвиля)", size=9, color=POS))

    # хвиля TX праворуч від симулятора
    wx0, wx1 = 540, 720
    wy = 130
    hi, lo = wy - 16, wy + 14
    bits = [1, 0, 1, 0, 1, 1, 0, 0, 1, 1]
    unit = (wx1 - wx0) / len(bits)
    x = wx0
    prev = hi if bits[0] else lo
    pts = []
    for i, bv in enumerate(bits):
        yl = hi if bv else lo
        if i > 0 and yl != prev:
            pts.append("%.1f,%.1f" % (x, prev)); pts.append("%.1f,%.1f" % (x, yl))
        pts.append("%.1f,%.1f" % (x, yl)); pts.append("%.1f,%.1f" % (x + unit, yl))
        x += unit; prev = yl
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (" ".join(pts), POS))
    p.append(text((wx0 + wx1) / 2, wy - 30, "вихід TX видно як хвилю", size=10, color=POS, bold=True))
    p.append(text((wx0 + wx1) / 2, wy + 40, "старт · дані · стоп —", size=9, color=MUTED))
    p.append(text((wx0 + wx1) / 2, wy + 54, "читаються відразу", size=9, color=MUTED))

    # стрілка «аж тоді на плату»
    p.append(arrow(W / 2, sy + sh + 6, W / 2, sy + sh + 40, color=INK, sw=1.8))
    pb, pbw, pbh = textbox(W / 2, sy + sh + 62, "аж коли хвиля сходиться — синтез і прошивання в плату",
                           size=11, bold=True, fill="#fdf6e3", stroke=INK, sw=1.6)
    p.append(pb)

    render(os.path.join(OUT, "testbench.svg"), W, H, *p,
           title="Тестбенч: помилку видно за секунди симуляції, а не паянням")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки hist-hdl
# ════════════════════════════════════════════════════════════════════════════

# ── two-cradles: дві колиски HDL ──────────────────────────────────────────────

def fig_two_cradles():
    W, H = 780, 300
    p = []
    colw = 330
    lx, rx = 40, W - 40 - colw

    # ── VHDL: держава ──
    p.append(rect(lx, 60, colw, 200, fill="#eef4ff", stroke=NEG, sw=2, rx=12))
    p.append(text(lx + colw / 2, 92, "VHDL", size=20, bold=True, color=NEG))
    p.append(text(lx + colw / 2, 116, "замовлення Пентагону", size=12, color=NEG, bold=True))
    p.append(mtext(lx + colw / 2, 150,
                   ["міністерство оборони США",
                    "велика програма, консорціум",
                    "мета — ДОКУМЕНТУВАТИ",
                    "поведінку чужих чипів"], size=11, color=INK, lh=1.45))
    p.append(text(lx + colw / 2, 240, "строга мова-документ", size=11, color=NEG, italic=True))

    # ── Verilog: стартап ──
    p.append(rect(rx, 60, colw, 200, fill="#fdecea", stroke=POS, sw=2, rx=12))
    p.append(text(rx + colw / 2, 92, "Verilog", size=20, bold=True, color=POS))
    p.append(text(rx + colw / 2, 116, "мова стартапу", size=12, color=POS, bold=True))
    p.append(mtext(rx + colw / 2, 150,
                   ["маленька фірма, жменька людей",
                    "написана за одну зиму",
                    "мета — ПРОСИМУЛЮВАТИ",
                    "власну схему до кремнію"], size=11, color=INK, lh=1.45))
    p.append(text(rx + colw / 2, 240, "гнучкий інструмент перевірки", size=11, color=POS, italic=True))

    # спільна думка посередині знизу
    p.append(text(W / 2, H - 18, "різні світи — одна думка: описати залізо текстом, а решту хай зробить машина",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "two-cradles.svg"), W, H, *p,
           title="Дві колиски HDL: замовлення держави й чип стартапу")


# ── timeline: спільний таймлайн обох мов ──────────────────────────────────────

def fig_timeline():
    W, H = 820, 320
    p = []
    ax0, ax1 = 70, 750
    midy = 165
    p.append(line(ax0, midy, ax1, midy, color=INK, sw=2.0))
    p.append(text(ax0 - 8, midy + 4, "час", size=10, color=MUTED, anchor="end", italic=True))

    span_lo, span_hi = 1980.0, 1996.0

    def xfor(yr):
        return ax0 + (yr - span_lo) / (span_hi - span_lo) * (ax1 - ax0)

    # VHDL — сині віхи зверху
    vhdl = [(1980, "VHSIC\n(програма)"), (1983, "контракт\nВПС"), (1987, "IEEE 1076\n(стандарт)")]
    for yr, lab in vhdl:
        x = xfor(yr)
        p.append(line(x, midy, x, midy - 40, color=NEG, sw=1.6))
        p.append(circle(x, midy, 4, fill=NEG, stroke=NEG, sw=1))
        p.append(mtext(x, midy - 52, lab, size=10, color=NEG, lh=1.2, bold=True))
        p.append(text(x, midy - 90, str(yr), size=9, color=NEG))

    # Verilog — червоні віхи знизу
    veri = [(1984, "Мурбі й Кº\nпишуть мову"), (1989, "Cadence\nкупує"),
            (1991, "відкрито\n(OVI)"), (1995, "IEEE 1364\n(стандарт)")]
    for yr, lab in veri:
        x = xfor(yr)
        p.append(line(x, midy, x, midy + 40, color=POS, sw=1.6))
        p.append(circle(x, midy, 4, fill=POS, stroke=POS, sw=1))
        p.append(mtext(x, midy + 54, lab, size=10, color=POS, lh=1.2, bold=True))
        p.append(text(x, midy + 92, str(yr), size=9, color=POS))

    # зелене — синтез (спільний перелом)
    xs = xfor(1987)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#eafaf0" '
             'stroke="%s" stroke-width="1.6"/>' % (xs - 56, midy - 14, 112, 28, FIELD))
    p.append(text(xs, midy + 4, "СИНТЕЗ", size=11, color=FIELD, bold=True))

    # легенда
    p.append(text(ax0, 40, "сині — лінія VHDL (від держави)", size=11, color=NEG, anchor="start", bold=True))
    p.append(text(ax0, H - 22, "червоні — лінія Verilog (від бізнесу) · зелене — спільний перелом: синтез",
                  size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Спільний таймлайн: від креслення до тексту, що будує залізо")


# ── synthesis: текст, з якого РОСТЕ схема ─────────────────────────────────────

def fig_synthesis():
    W, H = 780, 300
    p = []

    # верх — програма (в часі)
    p.append(text(40, 64, "Програма: розгорнута в ЧАСІ", size=13, bold=True, color=NEG))
    b1, h1 = codeblock(40, 76, 150, ["текст коду"], size=11, accent=NEG)
    p.append(b1)
    p.append(arrow(196, 76 + h1 / 2, 250, 76 + h1 / 2, color=NEG, sw=1.8))
    m1, mw1, mh1 = textbox(310, 76 + h1 / 2, "інструкції", size=11, fill=CODEBG, stroke=NEG, sw=1.6)
    p.append(m1)
    p.append(arrow(310 + mw1 / 2 + 6, 76 + h1 / 2, 376, 76 + h1 / 2, color=NEG, sw=1.8))
    t1, tw1, th1 = textbox(470, 76 + h1 / 2, "процесор виконує\nпо черзі, такт за тактом",
                           size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(t1)
    p.append(text(620, 76 + h1 / 2 + 4, "→ у ЧАСІ", size=12, color=NEG, anchor="start", bold=True))

    p.append(line(40, 165, W - 40, 165, color="#dddddd", sw=1.2, dash="5 4"))

    # низ — опис заліза (в просторі)
    p.append(text(40, 205, "Опис заліза на HDL: розгорнутий у ПРОСТОРІ", size=13, bold=True, color=POS))
    b2, h2 = codeblock(40, 217, 150, ["текст опису"], size=11, accent=POS)
    p.append(b2)
    p.append(arrow(196, 217 + h2 / 2, 250, 217 + h2 / 2, color=POS, sw=1.8))
    m2, mw2, mh2 = textbox(310, 217 + h2 / 2, "СИНТЕЗ", size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(m2)
    p.append(arrow(310 + mw2 / 2 + 6, 217 + h2 / 2, 376, 217 + h2 / 2, color=POS, sw=1.8))
    t2, tw2, th2 = textbox(470, 217 + h2 / 2, "схема вентилів і тригерів\nпрацює вся разом",
                           size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(t2)
    p.append(text(620, 217 + h2 / 2 + 4, "→ у ПРОСТОРІ", size=12, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "synthesis.svg"), W, H, *p,
           title="Що винайшли із синтезом: текст, з якого РОСТЕ схема")


# ── credit: точна атрибуція по ролях ──────────────────────────────────────────

def fig_credit():
    W, H = 800, 330
    p = []
    cards = [
        (160, 110, "Програма VHSIC\nі ВПС США", NEG, "#eef4ff", "ЗАМОВНИК:\nпоставили задачу,\nдали гроші"),
        (470, 110, "Intermetrics, TI, IBM", NEG, "#eef4ff", "ВИКОНАВЦІ контракту\n1983: спроєктували VHDL\n(синтаксис від Ada)"),
        (160, 240, "Філ Мурбі,\nҐоел, Хуанг", POS, "#fdecea", "СТАРТАП Gateway:\nпридумали Verilog\nі симулятор Verilog-XL"),
        (470, 240, "Спільноти й IEEE\n(OVI · 1076 · 1364)", FIELD, "#eafaf0", "ВІДКРИЛИ обидві мови,\nзробили надбанням усіх"),
    ]
    for cx, cy, title, col, fill, role in cards:
        b, bw, bh = textbox(cx, cy, title, size=12, bold=True, color=col, fill=fill, stroke=col, sw=1.9, pad=12)
        p.append(b)
        p.append(mtext(cx, cy + bh / 2 + 16, role, size=10, color=MUTED, lh=1.3))

    # підсумок праворуч
    p.append(mtext(700, 165,
                   ["Двох одиноких", "геніїв тут", "немає —", "дві колективні", "історії, що", "зрослися в", "один інструмент"],
                   size=11, color=INK, lh=1.4, bold=True))

    render(os.path.join(OUT, "credit.svg"), W, H, *p,
           title="Точна атрибуція: дві команди, жодного одинокого генія")


if __name__ == "__main__":
    # стаття
    fig_describe_vs_program()
    fig_module()
    fig_comb_vs_seq()
    fig_synth_not_exec()
    fig_same_code_diff_hw()
    # proj-вставка
    fig_blinker()
    fig_uart()
    fig_testbench()
    # hist-вставка
    fig_two_cradles()
    fig_timeline()
    fig_synthesis()
    fig_credit()
    print("OK: figures written to", OUT)
