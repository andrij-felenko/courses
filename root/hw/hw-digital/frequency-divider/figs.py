# -*- coding: utf-8 -*-
"""Фігури до теми «Дільник частоти».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── помічники: прямокутні хвилі ─────────────────────────────────────────────
def _poly(pts, color=INK, sw=2.4):
    s = " ".join("%.1f,%.1f" % (p[0], p[1]) for p in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (s, color, sw)


def _clock(x0, y0, n, period, hi):
    """n повних періодів такту: півперіод LOW, півперіод HIGH."""
    pts = [(x0, y0)]
    x = x0
    for _ in range(n):
        pts.append((x, y0))
        pts.append((x, y0 - hi))
        pts.append((x + period * 0.5, y0 - hi))
        pts.append((x + period * 0.5, y0))
        x += period
    pts.append((x, y0))
    return pts


def _wave(x0, y0, levels, unit, hi):
    """Довільна хвиля: levels — список 0/1 на кожен півкрок шириною unit."""
    pts = [(x0, y0)]
    x = x0
    for lv in levels:
        y = y0 - hi if lv else y0
        pts.append((x, y))
        pts.append((x + unit, y))
        x += unit
    pts.append((x, y0))
    return pts


def _ffbox(x, y, w, h, label, sub=None):
    out = rect(x, y, w, h, fill=FILL, stroke=INK, sw=1.8)
    out += text(x + w / 2, y + h / 2 + (0 if sub else 5), label, size=14, bold=True)
    if sub:
        out += text(x + w / 2, y + h / 2 + 18, sub, size=9, color=MUTED)
    return out


def _clkmark(x, y):
    """Трикутник-позначка тактового входу на лівому боці рамки в точці (x,y)."""
    return ('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f" fill="none" '
            'stroke="%s" stroke-width="1.6"/>' % (x, y - 7, x + 12, y, x, y + 7, INK))


# ── 1. ÷2 одним тригером — і задарма рівно 50%% меандр ───────────────────────
def fig_div2():
    W, H = 840, 360
    f = [text(W / 2, 28, "Один тригер ділить частоту на 2 — і вихід виходить рівно симетричним",
              size=15, bold=True)]

    # тригер ліворуч (D=Q̄)
    bx, by, bw, bh = 60, 120, 120, 92
    f.append(_ffbox(bx, by, bw, bh, "D-тригер"))
    f.append(text(bx + 14, by + 30, "D", size=12, bold=True, anchor="start"))
    f.append(text(bx + bw - 12, by + 30, "Q", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(text(bx + bw - 12, by + 66, "Q̄", size=12, bold=True, color=MUTED, anchor="end"))
    f.append(_clkmark(bx, by + bh - 16))
    f.append(line(bx - 42, by + bh - 16, bx, by + bh - 16, color=INK, sw=1.6))
    f.append(text(bx - 6, by + bh - 22, "такт", size=11, anchor="end"))
    # зворотний зв'язок Q̄ → D
    f.append(line(bx + bw, by + 62, bx + bw + 20, by + 62, color=NEG, sw=1.5))
    f.append(line(bx + bw + 20, by + 62, bx + bw + 20, by + bh + 22, color=NEG, sw=1.5))
    f.append(line(bx + bw + 20, by + bh + 22, bx - 20, by + bh + 22, color=NEG, sw=1.5))
    f.append(line(bx - 20, by + bh + 22, bx - 20, by + 26, color=NEG, sw=1.5))
    f.append(arrow(bx - 20, by + 26, bx, by + 26, color=NEG, sw=1.5))
    f.append(text(bx + bw / 2, by + bh + 38, "Q̄ назад на D", size=10, color=NEG, italic=True))

    # хвилі праворуч
    x0 = 360
    period = 52
    n = 8
    yb = 118
    f.append(text(x0 - 14, yb - 8, "такт", size=12, bold=True, anchor="end"))
    f.append(_poly(_clock(x0, yb, n, period, 24), color=INK, sw=2.3))
    for i in range(n + 1):
        f.append(line(x0 + i * period, yb - 28, x0 + i * period, yb + 118, color="#d3d3d3", sw=0.8, dash="3 3"))
    # позначки активних фронтів (наростання)
    for i in range(n):
        f.append(circle(x0 + i * period, yb, 3, fill=POS, stroke=POS, sw=1))

    # Q ÷2, рівно 50%
    yb = 226
    f.append(text(x0 - 14, yb - 8, "Q  (÷2)", size=12, bold=True, color=FIELD, anchor="end"))
    q = []
    lv = 0
    for _ in range(n):
        q += [lv, lv]  # тримає рівень цілий такт, перемикається на наступному фронті
        lv ^= 1
    f.append(_poly(_wave(x0, yb, q, period / 2.0, 24), color=FIELD, sw=2.7))
    # позначка «HIGH = один такт, LOW = один такт» (на реальних сегментах Q)
    f.append(line(x0 + period, yb + 38, x0 + 2 * period, yb + 38, color=MUTED, sw=1.2))
    f.append(line(x0 + period, yb + 34, x0 + period, yb + 42, color=MUTED, sw=1.2))
    f.append(line(x0 + 2 * period, yb + 34, x0 + 2 * period, yb + 42, color=MUTED, sw=1.2))
    f.append(text(x0 + period * 1.5, yb + 52, "1 такт HIGH", size=9, color=MUTED))
    f.append(line(x0 + 2 * period, yb + 38, x0 + 3 * period, yb + 38, color=MUTED, sw=1.2))
    f.append(line(x0 + 3 * period, yb + 34, x0 + 3 * period, yb + 42, color=MUTED, sw=1.2))
    f.append(text(x0 + period * 2.5, yb + 52, "1 такт LOW", size=9, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "Тригер перемикається на кожному фронті, тож HIGH і LOW — рівно по одному такту: меандр 50%.",
                  size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "div2.svg"), W, H, *f)


# ── 2. Ділення на будь-яке ціле: лічильник + декодер межі ────────────────────
def fig_divn():
    W, H = 880, 470
    f = [text(W / 2, 28, "Ділення на будь-яке ціле N: лічильник рахує до N і скидається",
              size=15, bold=True)]

    # блок-схема зверху
    cx, cy, cw, ch = 90, 70, 150, 70
    f.append(_ffbox(cx, cy, cw, ch, "лічильник", "0,1,…,N−1"))
    f.append(_clkmark(cx, cy + ch - 16))
    f.append(line(cx - 44, cy + ch - 16, cx, cy + ch - 16, color=INK, sw=1.6))
    f.append(text(cx - 8, cy + ch - 22, "fᵢₙ", size=11, anchor="end", bold=True))
    dx, dy, dw, dh = 320, 70, 160, 70
    f.append(_ffbox(dx, dy, dw, dh, "декодер", "«дійшли до N?»"))
    f.append(arrow(cx + cw, cy + ch / 2, dx, dy + dh / 2, color=INK, sw=1.8))
    f.append(text((cx + cw + dx) / 2, cy + ch / 2 - 8, "число", size=10, color=MUTED))
    # скид назад
    f.append(line(dx + dw, dy + 20, dx + dw + 24, dy + 20, color=POS, sw=1.6))
    f.append(line(dx + dw + 24, dy + 20, dx + dw + 24, dy - 18, color=POS, sw=1.6))
    f.append(line(dx + dw + 24, dy - 18, cx + cw / 2, dy - 18, color=POS, sw=1.6))
    f.append(arrow(cx + cw / 2, dy - 18, cx + cw / 2, cy, color=POS, sw=1.6))
    f.append(text((dx + cx + cw) / 2, dy - 24, "скид у 0", size=10, color=POS, bold=True))
    # вихід f/N
    f.append(arrow(dx + dw, dy + dh - 18, dx + dw + 70, dy + dh - 18, color=FIELD, sw=1.9))
    f.append(text(dx + dw + 40, dy + dh - 26, "fᵢₙ/N", size=11, color=FIELD, bold=True))

    # ── парне N: 50%% легко ──
    x0 = 150
    unit = 40
    n = 12
    f.append(rect(30, 175, 820, 120, fill="none", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(60, 198, "Парне N (÷6): рівно пів-на-пів дається легко", size=12, bold=True, color=FIELD, anchor="start"))
    yb = 250
    f.append(text(x0 - 14, yb - 8, "такт", size=11, bold=True, anchor="end"))
    f.append(_poly(_clock(x0, yb, n, unit, 20), color=INK, sw=2.0))
    yb = 250
    # вихід ÷6, 50%%: HIGH 3 такти, LOW 3 такти — окремий рядок нижче
    yb2 = 285
    # (малюємо ÷6 як окрему хвилю праворуч від такту неможливо в тій самій смузі — робимо компактно)
    # замість цього: показуємо вихід ÷6 під тактом
    render_div6 = []
    q = []
    hi_lo = [1, 1, 1, 0, 0, 0]  # 3 HIGH, 3 LOW
    for i in range(n):
        q += [hi_lo[i % 6]]
    # малюємо як хвилю з кроком unit
    ff = _wave(x0, 285, q, unit, 18)
    f.append(text(x0 - 14, 277, "÷6", size=11, bold=True, color=FIELD, anchor="end"))
    f.append(_poly(ff, color=FIELD, sw=2.4))
    for i in range(n + 1):
        f.append(line(x0 + i * unit, 232, x0 + i * unit, 292, color="#e0e0e0", sw=0.7, dash="3 3"))

    # ── непарне N: 50%% не дається ──
    f.append(rect(30, 315, 820, 130, fill="none", stroke=POS, sw=1.4, rx=10))
    f.append(text(60, 338, "Непарне N (÷5): рівно навпіл не ділиться — виходить 3:2 або 2:3",
                  size=12, bold=True, color=POS, anchor="start"))
    yb = 388
    f.append(text(x0 - 14, yb - 8, "такт", size=11, bold=True, anchor="end"))
    f.append(_poly(_clock(x0, yb, n, unit, 20), color=INK, sw=2.0))
    q2 = []
    hi_lo2 = [1, 1, 1, 0, 0]  # 3 HIGH, 2 LOW → 60%%
    for i in range(n):
        q2 += [hi_lo2[i % 5]]
    f.append(text(x0 - 14, 425, "÷5", size=11, bold=True, color=POS, anchor="end"))
    f.append(_poly(_wave(x0, 425, q2, unit, 18), color=POS, sw=2.4))
    for i in range(n + 1):
        f.append(line(x0 + i * unit, 370, x0 + i * unit, 432, color="#e0e0e0", sw=0.7, dash="3 3"))
    f.append(text(x0 + 3 * unit + unit * 0.0, 425 - 26, "3 такти HIGH", size=9, color=POS))
    f.append(text(x0 + 4 * unit + unit * 0.0, 425 + 14, "2 LOW", size=9, color=POS))

    render(os.path.join(IMG, "divide-n.svg"), W, H, *f)


# ── 3. Непарне ділення з рівно 50%%: злиття двох фронтів ─────────────────────
def fig_odd50():
    W, H = 860, 440
    f = [text(W / 2, 28, "÷3 із рівно 50%: складаємо результат наростаючого й спадного фронту",
              size=15, bold=True)]

    x0 = 180
    unit = 40      # чверть-такт? ні: один такт = 2 unit (LOW+HIGH)
    period = 80    # один такт
    n = 7
    yb = 90
    f.append(text(x0 - 14, yb - 8, "такт", size=12, bold=True, anchor="end"))
    f.append(_poly(_clock(x0, yb, n, period, 22), color=INK, sw=2.2))
    for i in range(n + 1):
        f.append(line(x0 + i * period, yb - 26, x0 + i * period, 400, color="#dadada", sw=0.7, dash="3 3"))
    # напівфронти
    for i in range(n):
        f.append(circle(x0 + i * period, yb, 3, fill=POS, stroke=POS, sw=1))               # наростання
        f.append(circle(x0 + i * period + period / 2, yb, 3, fill=NEG, stroke=NEG, sw=1))   # спадання

    half = period / 2.0

    # A: ÷3 по наростаючому фронту (не 50%%): період 3 такти, HIGH 1 такт (33%%) — типова форма з лічильника
    yb = 175
    f.append(text(x0 - 14, yb - 8, "A: ÷3 по ↑", size=11, bold=True, color=POS, anchor="end"))
    # HIGH перший такт кожних трьох
    a = []
    for i in range(n):
        a += [1 if (i % 3 == 0) else 0]
    f.append(_poly(_wave(x0, yb, a, period, 18), color=POS, sw=2.3))
    f.append(text(x0 + n * period + 6, yb - 4, "фаза 0", size=9, color=POS, anchor="start"))

    # B: те саме, але зсунуте на півтакту (по спадному фронту)
    yb = 240
    f.append(text(x0 - 14, yb - 8, "B: ÷3 по ↓", size=11, bold=True, color=NEG, anchor="end"))
    # той самий візерунок, зсунутий праворуч на half
    b_levels = []
    # будуємо хвилю кроком half: перший півкрок 0, далі повторюємо a з кроком period=2*half
    # простіше: явно за півкроками
    seq = []
    for i in range(n):
        onoff = 1 if (i % 3 == 0) else 0
        seq += [onoff, onoff]   # два півкроки на такт
    seq = [0] + seq[:-1]        # зсув праворуч на півтакту
    f.append(_poly(_wave(x0, yb, seq, half, 18), color=NEG, sw=2.3))
    f.append(text(x0 + n * period + 6, yb - 4, "зсув ½ такту", size=9, color=NEG, anchor="start"))

    # C: A OR B → рівно 50%% меандр із періодом 3 такти
    yb = 315
    f.append(text(x0 - 14, yb - 8, "A OR B", size=11, bold=True, color=FIELD, anchor="end"))
    # A по півкроках
    a_half = []
    for i in range(n):
        onoff = 1 if (i % 3 == 0) else 0
        a_half += [onoff, onoff]
    orr = [1 if (a_half[k] or (seq[k] if k < len(seq) else 0)) else 0 for k in range(len(a_half))]
    f.append(_poly(_wave(x0, yb, orr, half, 20), color=FIELD, sw=2.7))
    # позначка симетрії: HIGH 1.5 такту, LOW 1.5 такту
    f.append(text(x0 + n * period + 6, yb - 4, "50% !", size=10, color=FIELD, anchor="start", bold=True))

    # підсумкова рамка
    bx, by, bw, bh = 70, 360, 720, 62
    f.append(rect(bx, by, bw, bh, fill="#f4f7f4", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(W / 2, by + 25,
                  "Період виходу = 3 такти. HIGH триває 1.5 такту, LOW 1.5 такту — рівно 50%.",
                  size=12, bold=True))
    f.append(text(W / 2, by + 47,
                  "Півтактовий зсув дало використання СПАДНОГО фронту; OR злило дві половинки в симетричний меандр.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "odd-50.svg"), W, H, *f)


# ── 4. [hist] Борг непарності: 5 тактів = 2.5 + 2.5, а цілими ріжеться 3:2 ────
def fig_odd_debt():
    W, H = 860, 400
    f = [text(W / 2, 28, "Чому непарний період не ділиться навпіл цілими тактами",
              size=15, bold=True)]

    period = 84
    n = 5
    x0 = 150

    # рядок 1: п'ять тактів; посередині — «ідеальна» межа 50%% (на 2.5-му такті)
    yb = 120
    f.append(text(x0 - 16, yb - 8, "5 тактів", size=12, bold=True, anchor="end"))
    f.append(_poly(_clock(x0, yb, n, period, 22), color=INK, sw=2.2))
    for i in range(n + 1):
        f.append(line(x0 + i * period, yb - 26, x0 + i * period, yb + 22, color="#dadada", sw=0.8, dash="3 3"))
    # ідеальна середина — на 2.5 такту
    mid = x0 + 2.5 * period
    f.append(line(mid, yb - 44, mid, yb + 34, color=NEG, sw=1.8, dash="5 4"))
    f.append(text(mid, yb - 50, "рівно середина (2.5 такту)", size=10, color=NEG, bold=True))
    f.append(text(mid, yb + 50, "але цілого фронту тут немає", size=10, color=NEG, italic=True))

    # рядок 2: що дає лічильник — поріг лише на цілому такті → 3:2
    yb = 250
    f.append(text(x0 - 16, yb - 8, "÷5 (лічильник)", size=11, bold=True, color=POS, anchor="end"))
    q = []
    hi_lo = [1, 1, 1, 0, 0]
    for i in range(n):
        q += [hi_lo[i % 5]]
    f.append(_poly(_wave(x0, yb, q, period, 20), color=POS, sw=2.6))
    for i in range(n + 1):
        f.append(line(x0 + i * period, yb - 26, x0 + i * period, yb + 30, color="#e6e6e6", sw=0.7, dash="3 3"))
    # брекети 3 / 2
    f.append(line(x0, yb + 40, x0 + 3 * period, yb + 40, color=POS, sw=1.3))
    f.append(line(x0, yb + 36, x0, yb + 44, color=POS, sw=1.3))
    f.append(line(x0 + 3 * period, yb + 36, x0 + 3 * period, yb + 44, color=POS, sw=1.3))
    f.append(text(x0 + 1.5 * period, yb + 55, "3 такти HIGH (60%)", size=10, color=POS, bold=True))
    f.append(line(x0 + 3 * period, yb + 40, x0 + 5 * period, yb + 40, color=MUTED, sw=1.3))
    f.append(line(x0 + 5 * period, yb + 36, x0 + 5 * period, yb + 44, color=MUTED, sw=1.3))
    f.append(text(x0 + 4 * period, yb + 55, "2 такти LOW (40%)", size=10, color=MUTED))

    # підсумкова рамка
    bx, by, bw, bh = 70, 330, 720, 56
    f.append(rect(bx, by, bw, bh, fill="#fdf0ee", stroke=POS, sw=1.5, rx=10))
    f.append(text(W / 2, by + 22,
                  "Ідеальна межа лежить на 2.5-му такті — між фронтами. Цілий поріг туди не стає.",
                  size=12, bold=True))
    f.append(text(W / 2, by + 43,
                  "Бракує рівно ПІВ такту. Саме його дає спадний фронт — ось звідки прийом «подвійного фронту».",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "odd-debt.svg"), W, H, *f)


# ── 5. [hist] Два цифрові шляхи Rockwell (1982): ланцюг ÷1½→÷2 та прямий S/R ──
def fig_rockwell():
    W, H = 880, 430
    f = [text(W / 2, 28, "Два цифрові розв'язки Rockwell на ÷3 із рівно 50% (обидва — 1982)",
              size=15, bold=True)]

    # ── верхній: US4348640 — ÷1½ → ÷2 ──
    f.append(rect(30, 55, 820, 150, fill="none", stroke=NEG, sw=1.5, rx=12))
    f.append(text(52, 80, "US 4 348 640  —  ланцюг: несиметричні ⅔F, тоді ÷2 їх «випрямляє»",
                  size=12.5, bold=True, color=NEG, anchor="start"))
    y = 130
    f.append(_ffbox(70, y, 150, 56, "÷1½", "два JK-тригери"))
    f.append(_clkmark(70, y + 40))
    f.append(line(30, y + 40, 70, y + 40, color=INK, sw=1.6))
    f.append(text(34, y + 34, "F", size=11, bold=True, anchor="start"))
    f.append(arrow(220, y + 28, 320, y + 28, color=INK, sw=1.8))
    f.append(text(270, y + 16, "⅔F", size=11, color=NEG, bold=True))
    f.append(text(270, y + 44, "несиметр.", size=9, color=MUTED))
    f.append(_ffbox(320, y, 150, 56, "÷2", "тригер-toggle"))
    f.append(_clkmark(320, y + 40))
    f.append(arrow(470, y + 28, 560, y + 28, color=FIELD, sw=1.9))
    f.append(text(515, y + 16, "F/3", size=12, color=FIELD, bold=True))
    f.append(text(515, y + 44, "рівно 50%", size=9, color=FIELD))
    f.append(mtext(600, y + 12, "÷2 у кінці\nзавжди дає\nчистий меандр", size=10, color=MUTED, anchor="start"))

    # ── нижній: US4366394 — прямий set/reset на почергових фронтах ──
    f.append(rect(30, 225, 820, 150, fill="none", stroke=POS, sw=1.5, rx=12))
    f.append(text(52, 250, "US 4 366 394  —  прямо: тримати set/reset два фронти поспіль",
                  size=12.5, bold=True, color=POS, anchor="start"))
    y = 300
    f.append(_ffbox(70, y, 170, 56, "тригер виходу", "set / reset"))
    f.append(_clkmark(70, y + 40))
    f.append(line(30, y + 40, 70, y + 40, color=INK, sw=1.6))
    f.append(text(34, y + 34, "F", size=11, bold=True, anchor="start"))
    f.append(_ffbox(300, y, 150, 56, "керуюча логіка", "2-й тригер + вентилі"))
    # петля зворотного зв'язку: логіка керує тригером, стан тригера вертається в логіку
    f.append(arrow(300, y + 20, 240, y + 20, color=INK, sw=1.5))     # логіка → тригер (set/reset)
    f.append(text(270, y + 14, "set/reset", size=9, color=MUTED))
    f.append(arrow(240, y + 40, 300, y + 40, color=INK, sw=1.5))     # Q тригера → логіка
    f.append(text(270, y + 52, "Q", size=10, color=MUTED))
    f.append(arrow(450, y + 28, 540, y + 28, color=FIELD, sw=1.9))
    f.append(text(495, y + 16, "F/3", size=12, color=FIELD, bold=True))
    f.append(text(495, y + 44, "рівно 50%", size=9, color=FIELD))
    f.append(mtext(590, y + 8, "перемикання —\nна ПОЧЕРГОВИХ\n(інвертованих)\nтретіх фронтах",
                   size=10, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 12,
                  "Спільне в обох: щоб поділити на непарне, схема мусить чіплятися за ОБИДВА фронти такту.",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "rockwell-two-paths.svg"), W, H, *f)


if __name__ == "__main__":
    fig_div2()
    fig_divn()
    fig_odd50()
    fig_odd_debt()
    fig_rockwell()
    print("OK: figures written to", IMG)
