# -*- coding: utf-8 -*-
"""Фігури до статті «Підсилення в контурі (loop gain)» (book/electronics/analog/loop-gain).
Фігури статті:
  loop.svg     — петля від'ємного зв'язку: пряме A, зворотне β, добуток T = A·β у контурі
  break.svg    — як міряють T: розірвати петлю, увігнати пробу, прочитати, що повернулось
  fall.svg     — T падає з частотою; поки T велике — підсилення ≈ 1/β, на T=1 точиться стійкість
Фігури вставки hist-barkhausen-bode.md:
  lineage.svg  — стрічка часу поняття: Баркгаузен 1921 → Блек 1927 → Найквіст 1932 → Боде 1945 → далі
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def block(cx, cy, w, h, label, sub=None, fill=FILL, stroke=INK):
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=2, rx=8)]
    if sub:
        out.append(text(cx, cy - 2, label, size=18, bold=True))
        out.append(text(cx, cy + 16, sub, size=11, color=MUTED))
    else:
        out.append(text(cx, cy + 6, label, size=18, bold=True))
    return "".join(out)


def summer(cx, cy, r=18):
    """Вузол-суматор: кружечок із «+» зверху-зліва, «−» знизу."""
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=2),
           line(cx - r * 0.6, cy, cx + r * 0.6, cy, color=INK, sw=1.4),
           line(cx, cy - r * 0.6, cx, cy + r * 0.6, color=INK, sw=1.4)]
    out.append(text(cx - r - 6, cy - r + 2, "+", size=15, color=POS, bold=True, anchor="end"))
    out.append(text(cx - r - 6, cy + r + 8, "−", size=17, color=NEG, bold=True, anchor="end"))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. loop.svg — петля: пряме A, зворотне β, добуток A·β і є підсилення в контурі
# ════════════════════════════════════════════════════════════════════════════
def fig_loop():
    W, H = 660, 340
    f = []
    sx, sy = 130, 120          # суматор
    ax, ay = 330, 120          # блок A
    fx, fy = 330, 250          # блок β (нижній зворотний)

    # вхід → суматор
    f.append(arrow(50, sy, sx - 18, sy, color=INK, sw=2))
    f.append(text(56, sy - 12, "вхід", size=13, color=INK, anchor="start", bold=True))
    f.append(summer(sx, sy))

    # суматор → A
    f.append(arrow(sx + 18, sy, ax - 95, sy, color=INK, sw=2))

    # блок A
    f.append(block(ax, ay, 150, 70, "A", "пряме підсилення", fill="#eef7f0", stroke=FIELD))

    # A → вихід (вузол відгалуження)
    nodex = 560
    f.append(line(ax + 75, sy, nodex, sy, color=INK, sw=2))
    f.append(arrow(nodex, sy, 630, sy, color=INK, sw=2))
    f.append(text(624, sy - 12, "вихід", size=13, color=INK, anchor="end", bold=True))
    f.append(circle(nodex, sy, 3, fill=INK, stroke=INK))

    # відгалуження вниз до β
    f.append(line(nodex, sy, nodex, fy, color=INK, sw=2))
    f.append(arrow(nodex, fy, fx + 95, fy, color=INK, sw=2))

    # блок β
    f.append(block(fx, fy, 150, 70, "β", "зворотна частка", fill="#fdecea", stroke=POS))

    # β → суматор (мінус-вхід знизу)
    f.append(line(fx - 75, fy, sx, fy, color=INK, sw=2))
    f.append(arrow(sx, fy, sx, sy + 18, color=NEG, sw=2))

    # підпис петлі: T = A·β
    body, w0, h0 = textbox(W / 2, 312,
                           "Сигнал у контурі множиться на A, тоді на β:  T = A · β — підсилення в контурі",
                           size=12, color=INK, fill="#f4f6f8", stroke=INK)
    f.append(body)

    render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. break.svg — як виміряти T: розірвати петлю, увігнати пробу x, прочитати −Tx
# ════════════════════════════════════════════════════════════════════════════
def fig_break():
    W, H = 680, 360
    f = []
    ax, ay = 250, 130
    fx, fy = 250, 260

    # блок A
    f.append(block(ax, ay, 150, 66, "A", fill="#eef7f0", stroke=FIELD))
    # блок β
    f.append(block(fx, fy, 150, 66, "β", fill="#fdecea", stroke=POS))

    # вихід A праворуч вниз до β (ціла гілка)
    nodex = 470
    f.append(line(ax + 75, ay, nodex, ay, color=INK, sw=2))
    f.append(line(nodex, ay, nodex, fy, color=INK, sw=2))
    f.append(arrow(nodex, fy, fx + 75, fy, color=INK, sw=2))

    # ЛІВА сторона: тут петлю РОЗІРВАНО між β і входом A
    cutx = 110
    # кінець від β ліворуч (це «вихід петлі», що повернувся)
    f.append(line(fx - 75, fy, cutx, fy, color=INK, sw=2))
    f.append(line(cutx, fy, cutx, ay, color=INK, sw=2))
    # розрив на вході A
    gap = 26
    f.append(line(cutx, ay, ax - 75 - gap, ay, color=INK, sw=2))

    # значок ножиць/розриву
    f.append(line(ax - 75 - gap - 6, ay - 14, ax - 75 - gap + 6, ay + 14, color=POS, sw=2.4))
    f.append(line(ax - 75 - gap + 6, ay - 14, ax - 75 - gap - 6, ay + 14, color=POS, sw=2.4))
    f.append(text(ax - 75 - gap, ay - 26, "розрив", size=11, color=POS, anchor="middle", bold=True))

    # увігнали пробу x у вхід A
    f.append(arrow(ax - 150, ay, ax - 75, ay, color=NEG, sw=2.6))
    f.append(text(ax - 150, ay - 14, "увігнали x", size=12, color=NEG, anchor="start", bold=True))

    # прочитали те, що повернулось, на іншому боці розриву (нижня ліва вертикаль)
    f.append(circle(cutx, fy, 3, fill=INK, stroke=INK))
    f.append(text(cutx - 8, fy + 24, "читаємо тут:", size=11, color=INK, anchor="start"))
    f.append(text(cutx - 8, fy + 40, "повернулось −T·x", size=12, color=NEG, anchor="start", bold=True))

    # формула-висновок
    body, w0, h0 = textbox(W / 2 + 70, 56,
                           "T = − (що повернулось) / (що увігнали)",
                           size=13, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(body)

    render(os.path.join(IMG, "break.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. fall.svg — |T| падає з частотою; де воно велике — підсилення тримається 1/β,
#               на |T|=1 (0 дБ) вирішується стійкість (точка перетину з нулем)
# ════════════════════════════════════════════════════════════════════════════
def fig_fall():
    W, H = 680, 400
    f = []
    ox, oy = 90, 320           # початок осей
    axw, axh = 520, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))            # вісь X (частота, лог)
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))            # вісь Y (дБ)
    f.append(text(ox + axw - 4, oy + 24, "частота (лог)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - axh + 8, "|T|, дБ", size=12, color=INK, bold=True, anchor="end"))

    # рівень 0 дБ (|T| = 1) — критична горизонталь
    y0db = oy - 70
    f.append(line(ox, y0db, ox + axw, y0db, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(ox + 6, y0db - 8, "0 дБ  (|T| = 1)", size=11, color=MUTED, anchor="start"))

    # крива |T|: висока поличка зліва, тоді спад −20 дБ/дек до перетину з 0 дБ і нижче
    # поличка
    yhi = oy - 210
    knee = ox + 120
    f.append(line(ox + 4, yhi, knee, yhi, color=NEG, sw=2.8))
    # спад до перетину 0 дБ
    crossx = ox + 360
    f.append(line(knee, yhi, crossx, y0db, color=NEG, sw=2.8))
    # далі нижче нуля
    f.append(line(crossx, y0db, ox + axw - 10, y0db + 60, color=NEG, sw=2.8))

    f.append(text(ox + 60, yhi - 12, "велике T", size=12, color=NEG, bold=True, anchor="middle"))

    # зона «T велике → підсилення = 1/β, точне»
    f.append(rect(ox + 4, yhi - 4, knee - ox, 8, fill="none", stroke="none"))
    body, w0, h0 = textbox(ox + 130, yhi + 46,
                           "поки T велике —\nпідсилення = 1/β,\nточне й стале",
                           size=11, color=FIELD, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    # точка перетину 0 дБ — критична
    f.append(circle(crossx, y0db, 5, fill="#ffffff", stroke=POS, sw=2.6))
    f.append(line(crossx, y0db, crossx, oy, color=POS, sw=1.4, dash="4 4"))
    f.append(text(crossx, oy + 18, "тут T = 1", size=12, color=POS, anchor="middle", bold=True))
    body, w0, h0 = textbox(crossx + 70, y0db - 70,
                           "на цій частоті\nвирішується стійкість:\nважить фаза петлі",
                           size=11, color=POS, fill="#fdecea", stroke=POS)
    f.append(body)

    render(os.path.join(IMG, "fall.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. lineage.svg (вставка) — стрічка часу самого ПОНЯТТЯ «підсилення в контурі»
#    Баркгаузен 1921 (генератор: |Aβ|=1) → Блек 1927 (від'ємний зв'язок) →
#    Найквіст 1932 (строга стійкість) → Боде 1945 (return ratio 1+T) → далі
# ════════════════════════════════════════════════════════════════════════════
def fig_lineage():
    W, H = 760, 470
    f = []
    axy = 210                    # рівень осі часу (посередині, щоб картки лізли вгору й униз)
    x0, x1 = 70, 600
    f.append(line(x0, axy, x1, axy, color=INK, sw=2))
    f.append(arrow(x1, axy, x1 + 22, axy, color=INK, sw=2))
    f.append(text(x1 + 20, axy - 12, "час", size=12, color=MUTED, anchor="end"))

    # віхи: (x, рік, хто, суть, де картка — 'down'/'up', колір рамки)
    miles = [
        (120, "1921", "Баркгаузен", "генератор:\n|A·β| = 1,\nфаза = n·360°\n(потрібна,\nне достатня)", "down", POS),
        (260, "1927", "Блек",       "від'ємний\nзв'язок —\nнадлишок A\nна якість",                    "up",   FIELD),
        (400, "1932", "Найквіст",   "строгий\nкритерій\nстійкості\n(охоплення −1)",                   "down", NEG),
        (540, "1945", "Боде",       "return ratio,\nрізниця\nповернення\n1 + T",                       "up",   NEG),
    ]
    for (x, yr, who, what, side, col) in miles:
        f.append(circle(x, axy, 6, fill="#ffffff", stroke=col, sw=2.6))
        f.append(text(x, axy - 16 if side == "up" else axy + 26, yr,
                      size=14, color=INK, bold=True))
        # картка з підписом, з'єднана рискою до осі
        if side == "down":
            cy = axy + 128
            f.append(line(x, axy + 6, x, cy - 56, color=col, sw=1.2, dash="3 4"))
        else:
            cy = axy - 128
            f.append(line(x, axy - 6, x, cy + 56, color=col, sw=1.2, dash="3 4"))
        f.append(text(x, cy - 58, who, size=14, color=col, bold=True))
        body, w0, h0 = textbox(x, cy, what, size=11, color=INK,
                               fill="#ffffff", stroke=col, min_w=128)
        f.append(body)

    # хвіст «далі»: бліда віха-продовження за стрілкою, на рівні осі
    dx = 678
    f.append(circle(dx, axy, 5, fill="#ffffff", stroke=MUTED, sw=2))
    body, w0, h0 = textbox(dx, axy - 92,
                           "далі:\nозначення для\nтранзисторів\n(IEE, 1965),\nупорскування\n(Міддлбрук,\n1975)",
                           size=11, color=MUTED, fill="#f4f6f8", stroke=MUTED, min_w=128)
    f.append(line(dx, axy - 6, dx, axy - 92 + h0 / 2, color=MUTED, sw=1.2, dash="3 4"))
    f.append(body)

    # підпис-стрижень знизу
    body, w0, h0 = textbox(W / 2, H - 22,
                           "одне число — підсилення за повний обхід петлі — від ламп до строгої теорії",
                           size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)

    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# lever.svg (вставка math-return-difference) — різниця повернення (1+T) як ЄДИНИЙ
#   важіль: один корінь (вузол отримує свою копію назад → ×(1+T)) → чотири
#   наслідки. Те, за чим петля стежить, ділиться на (1+T); те, що передує
#   стеженому (вхідний струм), множиться.
# ════════════════════════════════════════════════════════════════════════════
def fig_lever():
    W, H = 720, 430
    f = []

    # корінь: рівняння петлі
    rx, ry = 158, 215
    body, w0, h0 = textbox(rx, ry,
                           "вузол у петлі\nотримує свою ж\nкопію назад\n×(1 + T)",
                           size=14, color=INK, fill="#eef2ff", stroke=NEG, sw=2.4)
    f.append(body)
    half = w0 / 2

    # чотири виходи праворуч: (заголовок, формула, колір, заливка, знак)
    bx = 545                     # центр правих рамок
    bw = 312                     # ширина правих рамок
    ys = [70, 165, 260, 355]
    outs = [
        ("підсилення → 1/β",  "чутливість до A  ÷ (1+T)",  FIELD, "#eef7f0", "÷"),
        ("вихідний опір",     "Rвих = Rо ÷ (1+T)",         FIELD, "#eef7f0", "÷"),
        ("спотворення / шум", "THD = THD(голого) ÷ (1+T)", FIELD, "#eef7f0", "÷"),
        ("вхідний опір",      "Rвх = Rд × (1+T)",          POS,   "#fdecea", "×"),
    ]
    fork_x = rx + half + 28      # звідки розгалужується
    f.append(line(rx + half, ry, fork_x, ry, color=INK, sw=2))
    f.append(circle(fork_x, ry, 3.5, fill=INK, stroke=INK))

    for (title_, formula, col, fill, op), yc in zip(outs, ys):
        # лінія від розгалуження до рамки
        f.append(line(fork_x, ry, fork_x, yc, color=INK, sw=1.6))
        f.append(arrow(fork_x, yc, bx - bw / 2, yc, color=INK, sw=1.8))
        # значок ділення/множення на лінії
        mid = (fork_x + bx - bw / 2) / 2
        f.append(circle(mid, yc, 12, fill="#ffffff", stroke=col, sw=2.2))
        f.append(text(mid, yc + 5, op, size=16, color=col, bold=True))
        # рамка наслідку (заголовок + формула)
        x0 = bx - bw / 2
        f.append(fitbox(x0, yc - 28, bw, 56,
                        title_ + "\n" + formula, size=13, pad=8,
                        fill=fill, stroke=col, sw=2, color=INK, bold=False))

    # підпис під коренем
    f.append(text(rx, ry + h0 / 2 + 28,
                  "F = 1 + T  (різниця повернення)",
                  size=13, color=NEG, bold=True))
    f.append(text(rx, ry + h0 / 2 + 50,
                  "÷ — за чим петля стежить;",
                  size=11, color=MUTED))
    f.append(text(rx, ry + h0 / 2 + 66,
                  "× — що передує стеженому",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "lever.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop()
    fig_break()
    fig_fall()
    fig_lineage()
    fig_lever()
    print("OK: фігури у", IMG)
