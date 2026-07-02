# -*- coding: utf-8 -*-
# Фігури теми «Прескейлер і синтез частоти». svgkit імпортуємо, не переписуємо (§5 AUTHORING).
# Вивід — у ./img/. Після запуску: python ../../../../scripts/svgcheck.py . --min-font 8
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8862b"


def square_wave(x0, y_lo, y_hi, period, n, sw=2.2, color=INK, start_high=False):
    """Прямокутна хвиля: n півперіодів завширшки period/2 кожен."""
    half = period / 2.0
    pts, x, hi = [], x0, start_high
    pts.append((x, y_hi if hi else y_lo))
    for _ in range(n):
        pts.append((x, y_hi if hi else y_lo))
        x += half
        pts.append((x, y_hi if hi else y_lo))
        hi = not hi
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (s, color, sw))


# ── 1. Навіщо прескейлер: швидкий фронт-дільник перед програмованим лічильником ──
def fig_why():
    W, H = 780, 300
    p = []
    # блок «дуже швидкий сигнал»
    yb = 120
    p.append(text(70, 46, "2.4 ГГц — надто швидко", size=13, color=POS, bold=True))
    p.append(square_wave(30, yb + 26, yb - 4, 26, 16, color=POS, sw=1.8))
    p.append(text(96, yb + 58, "жоден програмований", size=11.5, color=MUTED))
    p.append(text(96, yb + 74, "лічильник не встигає", size=11.5, color=MUTED))

    # прескейлер (фіксований, швидка технологія)
    bx, bw = 250, 150
    p.append(fitbox(bx, yb - 18, bw, 76, "ПРЕСКЕЙЛЕР\n÷ 8\n(швидка логіка)",
                    size=13, fill="#f4f7f4", stroke=FIELD, sw=2.0, bold=True))
    p.append(arrow(170, yb + 20, bx - 6, yb + 20, color=INK, sw=2.0))

    # повільніший сигнал
    p.append(arrow(bx + bw + 6, yb + 20, bx + bw + 70, yb + 20, color=INK, sw=2.0))
    p.append(text(bx + bw + 150, 46, "300 МГц — уже посильно", size=13, color=FIELD, bold=True))
    p.append(square_wave(bx + bw + 76, yb + 26, yb - 4, 70, 6, color=INK, sw=2.0))

    # програмований лічильник
    lx = bx + bw + 76
    p.append(fitbox(lx + 4, yb + 70, 250, 60,
                    "ПРОГРАМОВАНИЙ ЛІЧИЛЬНИК\n(звичайна, гнучка логіка)",
                    size=12, fill="#f7f8fa", stroke=INK, sw=1.6, bold=True))
    p.append(arrow(lx + 60, yb + 34, lx + 120, yb + 68, color=MUTED, sw=1.6))
    return render(os.path.join(OUT, "why-prescaler.svg"), W, H, *p)


# ── 2. Прескейлер таймера MCU: ділить такт, робить повільніший «тик» ───────────
def fig_timer():
    W, H = 760, 250
    p = []
    yb = 110
    x0 = 40
    p.append(text(x0 + 60, 44, "такт 80 МГц", size=12.5, color=INK, bold=True))
    p.append(square_wave(x0, yb + 20, yb - 10, 26, 16, color=INK, sw=1.8))
    p.append(arrow(x0 + 210, yb + 5, x0 + 250, yb + 5, color=INK, sw=1.9))

    bx = x0 + 250
    p.append(fitbox(bx, yb - 22, 150, 64, "ПРЕСКЕЙЛЕР\nділити на 80",
                    size=13, fill="#f4f7f4", stroke=FIELD, sw=2.0, bold=True))
    p.append(arrow(bx + 150, yb + 5, bx + 194, yb + 5, color=INK, sw=1.9))

    tx = bx + 194
    p.append(text(tx + 96, 44, "тик 1 МГц  (1 мкс)", size=12.5, color=FIELD, bold=True))
    p.append(square_wave(tx, yb + 20, yb - 10, 92, 4, color=FIELD, sw=2.2))
    p.append(text(W / 2, yb + 76, "80 000 000 / 80 = 1 000 000 тиків/с  →  крок лічильника = 1 мкс",
                  size=12, color=MUTED))
    return render(os.path.join(OUT, "timer-prescaler.svg"), W, H, *p)


# ── 3. ФАПЧ-синтезатор: петля робить f_out = N · f_ref ─────────────────────────
def fig_pll():
    W, H = 780, 400
    p = []
    yb = 120
    # блоки в ряд
    def blk(x, w, s, stroke=INK, fill=FILL):
        p.append(fitbox(x, yb, w, 58, s, size=12, fill=fill, stroke=stroke, sw=1.8, bold=True))
        return x + w

    x = 40
    p.append(text(24, yb + 30, "f_ref", size=12.5, color=NEG, bold=True, anchor="start"))
    p.append(text(56, yb + 46, "(кварц ÷R)", size=10, color=MUTED, anchor="start"))
    x = 110
    x2 = blk(x, 120, "ФАЗОВИЙ\nДЕТЕКТОР", stroke=NEG, fill="#eef2fd")
    p.append(arrow(x - 40, yb + 29, x - 2, yb + 29, color=NEG, sw=1.9))
    p.append(arrow(x2 + 2, yb + 29, x2 + 40, yb + 29, color=INK, sw=1.9))
    x3 = blk(x2 + 42, 110, "ФІЛЬТР\nПЕТЛІ")
    p.append(arrow(x3 + 2, yb + 29, x3 + 40, yb + 29, color=INK, sw=1.9))
    x4 = blk(x3 + 42, 110, "ГКН\n(VCO)", stroke=POS, fill="#fdecea")
    p.append(arrow(x4 + 2, yb + 29, x4 + 46, yb + 29, color=POS, sw=2.2))
    # вихід
    p.append(text(x4 + 116, yb + 20, "f_out", size=14, color=POS, bold=True, anchor="start"))
    p.append(text(x4 + 116, yb + 40, "= N · f_ref", size=12, color=POS, anchor="start"))

    # зворотний зв'язок через ÷N (прескейлер + лічильник)
    fy = yb + 150
    fbw = 240
    fbx = (x2 + 42 + x4) / 2 - fbw / 2
    p.append(fitbox(fbx, fy, fbw, 56, "÷ N\nпрескейлер + лічильник",
                    size=12.5, fill="#f4f7f4", stroke=FIELD, sw=2.0, bold=True))
    # від виходу ГКН вниз і в дільник
    xout = x4 + 108
    p.append(line(xout, yb + 29, xout, fy + 28, color=INK, sw=1.8))
    p.append(arrow(xout, fy + 28, fbx + fbw + 2, fy + 28, color=INK, sw=1.8))
    # з дільника назад у детектор (нижній вхід)
    p.append(line(fbx, fy + 28, 92, fy + 28, color=FIELD, sw=1.8))
    p.append(arrow(92, fy + 28, 92, yb + 44, color=FIELD, sw=1.8))
    p.append(text(fbx + fbw / 2, fy - 8, "поділена f_out порівнюється з f_ref", size=11, color=MUTED))

    # підсумок
    p.append(fitbox(150, fy + 74, 480, 40,
                    "у замку: f_out / N = f_ref   →   f_out = N · f_ref   (крок = f_ref)",
                    size=13, fill="#fffbe9", stroke=GOLD, sw=1.8, bold=True))
    return render(os.path.join(OUT, "pll-synth.svg"), W, H, *p)


# ── 4. Двомодульний прескейлер: N та N+1 дають точний поділ N·P + S ────────────
def fig_dualmod():
    W, H = 760, 320
    p = []
    top = 70
    p.append(text(W / 2, top, "Двомодульний прескейлер ділить то на N+1, то на N", size=13.5, bold=True))
    # два режими як смуги
    y1 = top + 40
    # S циклів по (N+1)
    x0 = 60
    seg1 = 300
    p.append(rect(x0, y1, seg1, 46, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(x0 + seg1 / 2, y1 + 20, "спершу ÷(N+1)", size=12.5, color=POS, bold=True))
    p.append(text(x0 + seg1 / 2, y1 + 38, "S разів  (S «зайвих» імпульсів)", size=11, color=POS))
    seg2 = 340
    p.append(rect(x0 + seg1, y1, seg2, 46, fill="#f4f7f4", stroke=FIELD, sw=1.8))
    p.append(text(x0 + seg1 + seg2 / 2, y1 + 20, "потім ÷N", size=12.5, color=FIELD, bold=True))
    p.append(text(x0 + seg1 + seg2 / 2, y1 + 38, "решту (P − S) разів", size=11, color=FIELD))

    # керує лічильник-«ковтач»
    p.append(text(x0, y1 + 78, "керує лічильник-«ковтач» S; головний лічильник рахує P повних циклів прескейлера",
                  size=11.5, color=MUTED, anchor="start"))

    # формула
    p.append(fitbox(120, y1 + 100, 520, 92,
                    "усього вхідних імпульсів на один вихідний:\n"
                    "(N+1)·S + N·(P − S) = N·P + S\n"
                    "S = 0…P−1 змінює поділ по ОДИНИЦІ, хоч фронт-дільник швидкий",
                    size=13, fill="#fffbe9", stroke=GOLD, sw=1.8, bold=True))
    return render(os.path.join(OUT, "dual-modulus.svg"), W, H, *p)


# ── 5. Вставка math: «бухгалтерія» двох фаз — скільки вхідних імпульсів набігло ─
def fig_ledger():
    W, H = 780, 360
    p = []
    p.append(text(W / 2, 34, "Один повний цикл = дві фази. Складаємо вхідні імпульси прескейлера",
                  size=13.5, bold=True))

    # Часова смуга: перші S циклів ÷(N+1), решта (P−S) циклів ÷N
    y = 78
    barh = 52
    x0 = 60
    seg1 = 288          # фаза ÷(N+1)
    seg2 = 372          # фаза ÷N
    p.append(rect(x0, y, seg1, barh, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(x0 + seg1 / 2, y + 21, "S циклів у режимі ÷(N+1)", size=12.5, color=POS, bold=True))
    p.append(text(x0 + seg1 / 2, y + 40, "кожен цикл = N+1 вхідних імпульсів", size=11, color=POS))
    p.append(rect(x0 + seg1, y, seg2, barh, fill="#f4f7f4", stroke=FIELD, sw=1.8))
    p.append(text(x0 + seg1 + seg2 / 2, y + 21, "(P − S) циклів у режимі ÷N", size=12.5, color=FIELD, bold=True))
    p.append(text(x0 + seg1 + seg2 / 2, y + 40, "кожен цикл = N вхідних імпульсів", size=11, color=FIELD))

    # Стан лічильників під смугою (стрілки-переходи)
    yc = y + barh + 40
    p.append(text(x0, yc, "лічильник-ковтач S:", size=11.5, color=MUTED, anchor="start"))
    p.append(text(x0 + seg1 / 2, yc, "рахує від S до 0", size=11.5, color=POS, anchor="middle"))
    p.append(text(x0 + seg1 + seg2 / 2, yc, "стоїть (вже вичерпаний)", size=11.5, color=MUTED, anchor="middle"))
    p.append(text(x0, yc + 22, "головний лічильник P:", size=11.5, color=MUTED, anchor="start"))
    p.append(text(x0 + seg1 / 2, yc + 22, "минуло S циклів", size=11.5, color=INK, anchor="middle"))
    p.append(text(x0 + seg1 + seg2 / 2, yc + 22, "лишилось (P − S)", size=11.5, color=INK, anchor="middle"))

    # Підсумкова бухгалтерія
    p.append(fitbox(120, yc + 44, 540, 96,
                    "вхідних імпульсів за фазу ÷(N+1):  (N+1)·S\n"
                    "вхідних імпульсів за фазу ÷N:      N·(P − S)\n"
                    "разом за цикл:  (N+1)·S + N·(P−S)  =  N·P + S",
                    size=13, fill="#fffbe9", stroke=GOLD, sw=1.8, bold=True))
    return render(os.path.join(OUT, "ledger-pulse-swallow.svg"), W, H, *p)


# ── 6. Сітка досяжних коефіцієнтів: S=0…P−1 дає безперервний крок; де провал ────
def fig_grid():
    W, H = 780, 360
    p = []
    p.append(text(W / 2, 34, "S ковзає 0…P−1 → коефіцієнт росте по одиниці, без пропусків",
                  size=13.5, bold=True))

    # числова вісь коефіцієнтів поділу з рисками
    axy = 150
    ax0, ax1 = 70, 710
    p.append(line(ax0, axy, ax1, axy, color=INK, sw=1.8))
    p.append(arrow(ax1 - 2, axy, ax1 + 20, axy, color=INK, sw=1.8))
    p.append(text(ax1 + 24, axy + 5, "поділ", size=11.5, color=INK, anchor="start"))

    # позначки: два сусідні «блоки P» — при P та при P+1 повних циклах
    # блок при P: значення N·P … N·P+(P−1), потім стрибок керується збільшенням P
    def tick(x, label, sub, color=INK):
        p.append(line(x, axy - 7, x, axy + 7, color=color, sw=1.6))
        p.append(text(x, axy - 14, label, size=11, color=color, bold=True))
        if sub:
            p.append(text(x, axy + 24, sub, size=9.5, color=MUTED))

    xs = [ax0 + 40 + i * 52 for i in range(11)]
    labels = ["N·P", "+1", "+2", "…", "N·P", "+(P−1)", "N(P+1)", "+1", "+2", "…", ""]
    # спрощені підписи під рисками
    tick(xs[0], "N·P",        "S=0",   color=FIELD)
    tick(xs[1], "N·P+1",      "S=1",   color=FIELD)
    tick(xs[2], "N·P+2",      "S=2",   color=FIELD)
    p.append(text(xs[3], axy - 14, "…", size=13, color=INK))
    tick(xs[4], "N·P+(P−1)",  "S=P−1", color=FIELD)
    # перехід: збільшуємо головний лічильник P на 1 → наступне значення N·(P+1)
    tick(xs[5], "N·(P+1)",    "S=0, P+1", color=POS)
    p.append(text((xs[4] + xs[5]) / 2, axy + 44,
                  "стик: N·P+(P−1)+1 = N·P+P = N·(P+1)  ⟺  сусідні блоки P змикаються без діри",
                  size=10.5, color=MUTED))

    # умова неперервності праворуч
    p.append(fitbox(150, axy + 78, 480, 74,
                    "щоб блоки P змикалися без пропуску, крок S має покрити стрибок по P:\n"
                    "діапазон S (0…P−1) завширшки P  ≥  крок по P, що дорівнює N\n"
                    "⟹  умова неперервності:  P ≥ N   (мінімальний суцільний поділ ≈ N·(N−1))",
                    size=12, fill="#eef2fd", stroke=NEG, sw=1.8, bold=True))
    return render(os.path.join(OUT, "coverage-grid.svg"), W, H, *p)


# ── 7. Вставка hist: дорога від «банки кварців» до одного числа N ──────────────
def fig_history():
    W, H = 820, 300
    p = []
    p.append(text(W / 2, 34, "Одна нота кварцу — багато потрібних частот: як розв'язували",
                  size=13.5, bold=True))

    # горизонтальна вісь-дорога
    axy = 118
    ax0, ax1 = 60, 760
    p.append(line(ax0, axy, ax1, axy, color=INK, sw=2.0))
    p.append(arrow(ax1 - 2, axy, ax1 + 18, axy, color=INK, sw=2.0))

    # чотири віхи; кожна — вузол на дорозі з підписом угорі (рік+хто) і внизу (суть)
    def milestone(x, yr, who, gist, color):
        p.append(circle(x, axy, 7, fill=color, stroke=INK, sw=1.6))
        p.append(line(x, axy - 7, x, axy - 30, color=color, sw=1.4))
        p.append(text(x, axy - 36, yr, size=12.5, color=color, bold=True))
        p.append(text(x, axy - 52, who, size=10.5, color=INK))
        p.append(line(x, axy + 7, x, axy + 26, color=color, sw=1.4))

    xs = [150, 340, 530, 690]
    milestone(xs[0], "до ~1960-х", "банка кварців", "", MUTED)
    milestone(xs[1], "1931–32", "де Беллескіз", "", NEG)
    milestone(xs[2], "1969", "Signetics", "", FIELD)
    milestone(xs[3], "1970–73", "Ніколс · Motorola", "", POS)

    # рамки-суть під кожною віхою
    p.append(fitbox(xs[0] - 78, axy + 30, 156, 66,
                    "по кристалу на канал\nне масштабується",
                    size=10.5, fill="#f4f6f8", stroke=MUTED, sw=1.4))
    p.append(fitbox(xs[1] - 82, axy + 30, 164, 66,
                    "петля за фазою —\nдля ПРИЙМАННЯ радіо,\nне для синтезу",
                    size=10, fill="#eef2fd", stroke=NEG, sw=1.4))
    p.append(fitbox(xs[2] - 82, axy + 30, 164, 66,
                    "монолітна ФАПЧ\nза копійки → петля\nстає масовою",
                    size=10, fill="#f4f7f4", stroke=FIELD, sw=1.4))
    p.append(fitbox(xs[3] - 88, axy + 30, 176, 66,
                    "двомодульний\nпрескейлер:\nтонкий крок на ГГц",
                    size=10, fill="#fdecea", stroke=POS, sw=1.4))

    # висновок унизу
    p.append(fitbox(190, H - 34, 440, 26,
                    "підсумок: один кварц + число N  →  будь-яка частота сітки",
                    size=12, fill="#fffbe9", stroke=GOLD, sw=1.6, bold=True))
    return render(os.path.join(OUT, "history-synth.svg"), W, H, *p)


if __name__ == "__main__":
    fig_why()
    fig_timer()
    fig_pll()
    fig_dualmod()
    fig_ledger()
    fig_grid()
    fig_history()
    print("figs written to", OUT)
