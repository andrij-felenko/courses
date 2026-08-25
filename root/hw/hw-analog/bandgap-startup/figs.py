# -*- coding: utf-8 -*-
"""Фігури до теми «Старт-схема bandgap-осередку» (аналогова, кутом теорії кіл).
П'ять фігур:
  two-states.svg   — самозміщена петля I = f(I): дві точки перетину з прямою рівноваги
                     (нульовий струм + робоча точка), нуль теж стійкий → треба штовхнути
  startup-block.svg — блок-схема: осередок + старт-вузол, що ВПОРСКУЄ струм при нулі
                      й ВІДЧЕПЛЯЄТЬСЯ, коли осередок прокинувся
  ramp.svg         — два запуски на одній шкалі часу: добрий (вихід виходить на Vref)
                     і застряглий (без старту лишається 0 В назавжди)
  window.svg       — числова вісь відліку АЦП: мертва опора кидає відлік на КРАЇ
                     (≈0 або ≈повна шкала), жива тримає його у вузькому вікні правдоподібності
  bringup.svg      — стан-машина прошивки на старті: міряй вузол → у вікні? →
                     живий / повтор із таймаутом / відмова → перезавантаження чи деградація
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def two_states():
    """Петля самозміщення: крива I=f(I) перетинає пряму рівноваги у ДВОХ точках."""
    W, H = 720, 440
    p = [text(W / 2, 28, "Самозміщена петля має дві точки рівноваги", size=17, bold=True)]

    # осі (графік: по горизонталі — струм у петлі зараз, по вертикалі — який струм петля поверне)
    ox, oy = 110, 360          # початок координат
    ax, ay = 560, 70           # кінці осей
    p.append(arrow(ox, oy, ax + 18, oy, color=INK, sw=1.8))   # вісь струму-входу
    p.append(arrow(ox, oy, ox, ay - 8, color=INK, sw=1.8))    # вісь струму-відгуку
    p.append(text(ax + 6, oy + 26, "струм у петлі зараз  I", size=13, color=MUTED))
    p.append(text(ox - 8, ay - 16, "який струм петля поверне  f(I)", size=13, color=MUTED, anchor="start"))
    p.append(text(ox - 12, oy + 18, "0", size=12, color=MUTED, anchor="end"))

    # пряма рівноваги f(I) = I (де «повернутий» струм = поточному → стала точка)
    p.append(line(ox, oy, ax, ay + 20, color=MUTED, sw=1.6, dash="6,5"))
    p.append(text(ax - 4, ay + 8, "рівновага: f(I)=I", size=12, color=MUTED, anchor="end"))

    # крива відгуку петлі f(I): стартує з 0 у нулі (нема струму → нема й відгуку),
    # круто росте, насичується — перетинає пряму в нулі та в робочій точці
    pts = []
    for i in range(0, 101):
        I = i / 100.0
        # насичувальна S-крива, що йде з (0,0); підібрана так, щоб перетнути y=x при ~0.62
        f = 1.15 * (1 - math.exp(-3.2 * I)) - 0.18 * I
        x = ox + I * (ax - ox)
        y = oy - max(0.0, f) * (oy - ay) / 1.05
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), FIELD))
    p.append(text(ox + 250, ay + 36, "f(I): струм, що його осередок", size=12, color=FIELD, anchor="start"))
    p.append(text(ox + 250, ay + 52, "віддає назад у себе", size=12, color=FIELD, anchor="start"))

    # точка A — нульова рівновага (початок координат)
    p.append(circle(ox, oy, 7, fill="#fdecea", stroke=POS, sw=2.4))
    b, _, _ = textbox(ox + 70, oy - 6, ["A — мертва точка", "I = 0, вихід 0 В", "теж СТІЙКА"],
                      size=12, fill="#fdecea", stroke=POS, color=POS, bold=False)
    p.append(b)

    # точка B — робоча рівновага (другий перетин)
    Ib = 0.62
    xb = ox + Ib * (ax - ox)
    yb = oy - Ib * (oy - ay)
    p.append(circle(xb, yb, 7, fill="#eafaf0", stroke=FIELD, sw=2.4))
    b, _, _ = textbox(xb + 8, yb - 58, ["B — робоча точка", "I ≠ 0, є Vref", "осередок живий"],
                      size=12, fill="#eafaf0", stroke=FIELD, color="#1e7a45", bold=False)
    p.append(b)

    # стрілки «куди тягне» між точками: трохи штовхнули від A → котиться до B
    p.append(arrow(ox + 28, oy - 26, ox + 80, oy - 70, color=NEG, sw=1.8))
    p.append(text(ox + 150, oy - 92, "ледь штовхнули струм →", size=12, color=NEG))
    p.append(text(ox + 150, oy - 76, "петля сама докочує до B", size=12, color=NEG))

    return render(os.path.join(OUT, "two-states.svg"), W, H, *p)


def startup_block():
    """Блок-схема: осередок + старт-вузол, що впорскує й відчепляється."""
    W, H = 720, 380
    p = [text(W / 2, 28, "Старт-вузол штовхає при нулі — і зникає, коли осередок ожив", size=16, bold=True)]

    # ── основний bandgap-осередок (праворуч) ──
    cell_x, cell_y, cell_w, cell_h = 380, 90, 230, 200
    p.append(rect(cell_x, cell_y, cell_w, cell_h, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(cell_x + cell_w / 2, cell_y + 26, "BANDGAP-ОСЕРЕДОК", size=14, bold=True, color="#1e7a45"))
    p.append(text(cell_x + cell_w / 2, cell_y + 48, "(самозміщена петля)", size=12, color=MUTED))
    p.append(fitbox(cell_x + 24, cell_y + 70, cell_w - 48, 30,
                    "ΔVbe → струм → дзеркало → той самий струм",
                    size=11, fill="#ffffff", stroke=FIELD, color=INK))
    p.append(fitbox(cell_x + 24, cell_y + 112, cell_w - 48, 30,
                    "тримає себе сама, коли вже біжить струм",
                    size=11, fill="#ffffff", stroke=MUTED, color=MUTED))
    # вихід Vref
    p.append(arrow(cell_x + cell_w, cell_y + cell_h / 2, cell_x + cell_w + 24, cell_y + cell_h / 2,
                   color=INK, sw=2))
    p.append(text(cell_x + cell_w + 28, cell_y + cell_h / 2 - 6, "Vref", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(cell_x + cell_w + 28, cell_y + cell_h / 2 + 12, "≈1.25 В", size=12, color=MUTED, anchor="start"))

    # ── старт-вузол (ліворуч) ──
    su_x, su_y, su_w, su_h = 60, 110, 250, 160
    p.append(rect(su_x, su_y, su_w, su_h, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(su_x + su_w / 2, su_y + 26, "СТАРТ-ВУЗОЛ", size=14, bold=True, color=NEG))
    p.append(fitbox(su_x + 20, su_y + 42, su_w - 40, 28,
                    "бачить: струм = 0 ?", size=12, fill="#ffffff", stroke=NEG, color=INK))
    p.append(fitbox(su_x + 20, su_y + 80, su_w - 40, 28,
                    "так → впорскує струм", size=12, fill="#ffffff", stroke=POS, color=POS))
    p.append(fitbox(su_x + 20, su_y + 118, su_w - 40, 28,
                    "ні → відчепляється", size=12, fill="#ffffff", stroke=MUTED, color=MUTED))

    # стрілка впорскування (старт → осередок)
    p.append(arrow(su_x + su_w, su_y + 80, cell_x, cell_y + 90, color=POS, sw=2.2))
    p.append(text((su_x + su_w + cell_x) / 2, su_y + 64, "поштовх", size=12, color=POS, bold=True))

    # зворотний «нюх» струму (осередок → старт), пунктир
    p.append(line(cell_x, cell_y + 150, su_x + su_w, su_y + 138, color=MUTED, sw=1.6, dash="5,4"))
    p.append(text((su_x + su_w + cell_x) / 2, su_y + 158, "нюхає струм", size=11, color=MUTED))

    return render(os.path.join(OUT, "startup-block.svg"), W, H, *p)


def ramp():
    """Два запуски на одній шкалі: добрий (виходить на Vref) і застряглий (0 В)."""
    W, H = 720, 360
    p = [text(W / 2, 28, "Той самий чип, два запуски: зі стартом і без", size=17, bold=True)]

    ox, oy = 90, 300
    ax, ay = 640, 70
    p.append(arrow(ox, oy, ax + 14, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, ay - 6, color=INK, sw=1.8))
    p.append(text(ax + 4, oy + 24, "час після подачі живлення", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 6, ay - 12, "вихід Vref", size=12, color=MUTED, anchor="start"))

    # рівень Vref
    yref = ay + 30
    p.append(line(ox, yref, ax, yref, color=MUTED, sw=1.2, dash="4,4"))
    p.append(text(ox - 8, yref + 4, "1.25 В", size=12, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy + 4, "0 В", size=12, color=MUTED, anchor="end"))

    # добрий запуск: плавно виходить на Vref і тримається
    good = []
    for i in range(0, 101):
        t = i / 100.0
        v = 1.0 - math.exp(-5.0 * t)             # експоненційний вихід на 1
        x = ox + 0.18 * (ax - ox) + t * 0.7 * (ax - ox)
        y = oy - v * (oy - yref)
        good.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(good), FIELD))
    p.append(text(ax - 6, yref - 14, "зі старт-вузлом → живий", size=13, color="#1e7a45", anchor="end"))

    # застряглий: лишається біля 0
    p.append(line(ox + 0.18 * (ax - ox), oy - 3, ax - 10, oy - 3, color=POS, sw=2.8))
    p.append(text(ax - 6, oy - 12, "без старту → мертвий, 0 В назавжди", size=13, color=POS, anchor="end"))

    # момент подачі живлення
    tx = ox + 0.18 * (ax - ox)
    p.append(line(tx, oy + 6, tx, ay, color=MUTED, sw=1.2, dash="3,3"))
    p.append(text(tx, oy + 24, "живлення увімкнули", size=11, color=MUTED))

    return render(os.path.join(OUT, "ramp.svg"), W, H, *p)


def window():
    """Числова вісь відліку АЦП: де опиниться відлік при живій і мертвій опорі.
    Жива опора → відлік вузла з відомою часткою живлення сидить у ВУЗЬКОМУ вікні
    коло середини. Мертва опора (Vref≈0) → знаменник перетворення зник, і будь-який
    вхід читається як майже повна шкала або тоне в шумі коло нуля — на КРАЯХ, не в вікні."""
    W, H = 720, 320
    p = [text(W / 2, 28, "Де сяде відлік АЦП: жива опора — у вікні, мертва — на краю", size=16, bold=True)]

    # числова вісь відліку 0..ADC_FULL_SCALE
    ax_x0, ax_x1, ax_y = 90, 630, 180
    p.append(arrow(ax_x0 - 10, ax_y, ax_x1 + 16, ax_y, color=INK, sw=1.8))
    p.append(text(ax_x0 - 12, ax_y + 5, "0", size=12, color=MUTED, anchor="end"))
    p.append(text(ax_x1 + 20, ax_y + 5, "повна\nшкала", size=11, color=MUTED, anchor="start"))
    p.append(text(ax_x1 + 8, ax_y + 28, "(код відліку →)", size=11, color=MUTED, anchor="end"))

    span = ax_x1 - ax_x0

    # вікно правдоподібності 7/16..9/16 (коло середини) — зелена смуга
    wx0 = ax_x0 + span * 7 / 16
    wx1 = ax_x0 + span * 9 / 16
    p.append(rect(wx0, ax_y - 44, wx1 - wx0, 88, fill="#eafaf0", stroke=FIELD, sw=2))
    xm = ax_x0 + span * 0.5
    p.append(line(xm, ax_y - 44, xm, ax_y + 44, color=FIELD, sw=1.4, dash="4,3"))
    p.append(text(xm, ax_y - 52, "½ шкали", size=12, color="#1e7a45", bold=True))
    b, _, _ = textbox(xm, ax_y + 92, ["опора ЖИВА", "відлік ½-вузла тут", "7/16 … 9/16"],
                      size=12, fill="#eafaf0", stroke=FIELD, color="#1e7a45", bold=False)
    p.append(b)
    # межі вікна
    p.append(text(wx0 - 4, ax_y - 50, "7/16", size=11, color=MUTED, anchor="end"))
    p.append(text(wx1 + 4, ax_y - 50, "9/16", size=11, color=MUTED, anchor="start"))

    # мертва опора — два можливі краї
    # ліворуч: тоне в шумі коло нуля
    p.append(circle(ax_x0 + span * 0.03, ax_y, 7, fill="#fdecea", stroke=POS, sw=2.4))
    b, _, _ = textbox(ax_x0 + span * 0.03 + 78, ax_y - 8, ["опора мертва:", "шум коло 0"],
                      size=11, fill="#fdecea", stroke=POS, color=POS, bold=False)
    p.append(b)
    # праворуч: будь-який вхід = майже повна шкала
    p.append(circle(ax_x0 + span * 0.97, ax_y, 7, fill="#fdecea", stroke=POS, sw=2.4))
    b, _, _ = textbox(ax_x0 + span * 0.97 - 86, ax_y - 8, ["опора мертва:", "майже повна шкала"],
                      size=11, fill="#fdecea", stroke=POS, color=POS, bold=False)
    p.append(b)

    return render(os.path.join(OUT, "window.svg"), W, H, *p)


def bringup():
    """Стан-машина прошивки на старті: один прохід рішення довіри до АЦП."""
    W, H = 720, 470
    p = [text(W / 2, 26, "Старт системи: довіряти АЦП лише по доведенню, що опора жива", size=16, bold=True)]

    cx = W / 2

    # вузол стан-машини: рамка + багаторядковий підпис (рамку малюємо самі, без подвійних)
    def node(cy, lines, w=320, h=48, fill=FILL, stroke=LINE, color=INK, bold=False):
        x, y = cx - w / 2, cy - h / 2
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8)
        ls = lines if isinstance(lines, list) else [lines]
        ty = cy - (len(ls) - 1) * 13 * 1.25 / 2 + 13 * 0.35
        out += mtext(cx, ty, ls, size=13, color=color, bold=bold)
        return out

    y1, y2, y3, y4 = 70, 150, 236, 236
    # старт
    p.append(node(y1, "увімкнули живлення · adc_init() · чекати t прокидання", w=440, h=46,
                  fill="#eaf0fd", stroke=NEG, color=INK))
    p.append(arrow(cx, y1 + 23, cx, y2 - 24, color=INK, sw=1.8))

    # вимір + перевірка вікна (ромб-рішення як рамка)
    p.append(node(y2, ["виміряти вузол ½·Vживл", "відлік у вікні 7/16…9/16 ?"], w=360, h=56,
                  fill=FILL, stroke=INK, bold=True))

    # гілка ТАК → праворуч униз
    rx = cx + 250
    p.append(line(cx + 180, y2, rx, y2, color=FIELD, sw=1.8))
    p.append(line(rx, y2, rx, 360, color=FIELD, sw=1.8))
    p.append(arrow(rx, 360, cx + 160, 360, color=FIELD, sw=1.8))
    p.append(text(cx + 196, y2 - 8, "так", size=12, color="#1e7a45", bold=True))
    p.append(node(360, ["опора ЖИВА →", "enter_normal_mode()"], w=240, h=52,
                  fill="#eafaf0", stroke=FIELD, color="#1e7a45", bold=True))

    # гілка НІ → ліворуч: повтор із таймаутом
    lx = cx - 250
    p.append(line(cx - 180, y2, lx, y2, color=POS, sw=1.8))
    p.append(line(lx, y2, lx, 300, color=POS, sw=1.8))
    p.append(arrow(lx, 300, cx - 160, 300, color=POS, sw=1.8))
    p.append(text(cx - 208, y2 - 8, "ні", size=12, color=POS, bold=True))
    p.append(node(300, ["ще є спроби?", "(таймаут не вичерпано)"], w=240, h=52,
                  fill="#fff7e6", stroke="#b8860b", color=INK))
    # петля «спробувати ще» назад угору до виміру
    p.append(line(cx, 300 - 26, cx, 300 - 40, color="#b8860b", sw=1.6, dash="4,3"))
    p.append(arrow(cx, 300 - 40, cx, y2 + 30, color="#b8860b", sw=1.6))
    p.append(text(cx + 8, (y2 + 300) / 2, "почекати ще трохи й перевиміряти", size=11,
                  color="#b8860b", anchor="start"))

    # таймаут вичерпано → відмова
    p.append(arrow(cx, 300 + 26, cx, 410 - 26, color=POS, sw=1.8))
    p.append(text(cx + 8, (300 + 410) / 2, "таймаут вичерпано", size=11, color=POS, anchor="start"))
    p.append(node(410, ["fault_latch(FAULT_VREF_DEAD)  →", "перезавантаження  АБО  деградований режим"],
                  w=460, h=52, fill="#fdecea", stroke=POS, color=POS, bold=True))

    return render(os.path.join(OUT, "bringup.svg"), W, H, *p)


if __name__ == "__main__":
    two_states()
    startup_block()
    ramp()
    window()
    bringup()
    print("OK: two-states.svg, startup-block.svg, ramp.svg, window.svg, bringup.svg")
