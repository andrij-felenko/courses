# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект Міллера».
Запуск:  python figs.py   → пише SVG у ./img/
Три фігури:
  multiply.svg  — ємність між входом і виходом інвертора множиться на (1+A) на вході
  bandwidth.svg — велика вхідна ємність + опір джерела = ФНЧ, що ріже смугу
  integrator.svg— той самий ефект навмисне: інтегратор з велетенською точною ємністю
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WIRE = "#333333"


def amp_triangle(cx, cy, w, h, label="−A"):
    """Трикутник підсилювача вершиною вправо; label у центрі."""
    x1, x2 = cx - w / 2, cx + w / 2
    p = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" '
         'fill="%s" stroke="%s" stroke-width="1.8"/>'
         % (x1, cy - h / 2, x1, cy + h / 2, x2, cy, FILL, LINE))
    p += text(cx - w * 0.12, cy + 6, label, size=17, bold=True, color=NEG)
    return p


def cap(cx, cy, horizontal=True, gap=8, plate=18, color=WIRE):
    """Дві пластини конденсатора з центром (cx,cy)."""
    if horizontal:
        return (line(cx - gap / 2, cy - plate / 2, cx - gap / 2, cy + plate / 2, color, 2.4) +
                line(cx + gap / 2, cy - plate / 2, cx + gap / 2, cy + plate / 2, color, 2.4))
    return (line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, color, 2.4) +
            line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, color, 2.4))


# ── 1. Множення ємності зворотного зв'язку ──────────────────────────────────
def fig_multiply():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, "Маленька ємність між входом і виходом стає велетенською на вході", size=15, bold=True))

    # ЛІВОРУЧ: реальна схема — інвертор із містковою ємністю C
    lx = 175
    midy = 200
    f.append(amp_triangle(lx, midy, 90, 96, "−A"))
    # вхідний вузол
    inx = lx - 120
    f.append(line(inx, midy, lx - 45, midy, WIRE, 2))
    f.append(circle(inx, midy, 4, fill=INK, stroke=INK))
    f.append(text(inx - 6, midy + 5, "вхід", size=12, color=MUTED, anchor="end"))
    # вихідний вузол
    outx = lx + 120
    f.append(line(lx + 45, midy, outx, midy, WIRE, 2))
    f.append(circle(outx, midy, 4, fill=INK, stroke=INK))
    f.append(text(outx + 6, midy + 5, "вихід", size=12, color=MUTED, anchor="start"))
    # містковий конденсатор C з входу на вихід (зверху)
    topy = midy - 78
    f.append(line(inx, midy, inx, topy, WIRE, 2))
    f.append(line(inx, topy, lx - 22, topy, WIRE, 2))
    f.append(cap(lx, topy, horizontal=True, gap=9, plate=22, color=POS))
    f.append(line(lx + 22, topy, outx, topy, WIRE, 2))
    f.append(line(outx, topy, outx, midy, WIRE, 2))
    f.append(text(lx, topy - 14, "C", size=16, bold=True, color=POS))
    f.append(text(lx, topy - 30, "мала", size=11, color=MUTED))
    f.append(text(lx, midy + 78, "реальна схема", size=12, color=MUTED, italic=True))

    # стрілка-перетворення
    f.append(arrow(lx + 175, midy, lx + 235, midy, color=FIELD, sw=2.4))
    f.append(text(lx + 205, midy - 12, "вхід «бачить»", size=11, color=FIELD))

    # ПРАВОРУЧ: еквівалент на вході — одна велика ємність на землю
    rx = 560
    f.append(line(rx, midy - 70, rx, midy - 18, WIRE, 2))
    f.append(circle(rx, midy - 70, 4, fill=INK, stroke=INK))
    f.append(text(rx, midy - 84, "вхід", size=12, color=MUTED))
    f.append(cap(rx, midy, horizontal=False, gap=10, plate=46, color=POS))
    f.append(line(rx, midy + 18, rx, midy + 56, WIRE, 2))
    # земля
    gy = midy + 56
    f.append(line(rx - 20, gy, rx + 20, gy, WIRE, 2.4))
    f.append(line(rx - 12, gy + 7, rx + 12, gy + 7, WIRE, 2))
    f.append(line(rx - 5, gy + 13, rx + 5, gy + 13, WIRE, 2))
    # підпис ємності праворуч від пластин
    f.append(text(rx + 34, midy - 8, "C·(1+A)", size=18, bold=True, color=POS, anchor="start"))
    f.append(text(rx + 34, midy + 12, "у стільки ж разів більша", size=11, color=INK, anchor="start"))
    f.append(text(rx, gy + 34, "що бачить джерело сигналу", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "multiply.svg"), W, H, *f)


# ── 2. Велика вхідна ємність ріже смугу ─────────────────────────────────────
def fig_bandwidth():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 26, "Роздута вхідна ємність із опором джерела утворює фільтр і губить високі частоти", size=14, bold=True))

    # верх: схема Rs + Cвх
    sx = 90
    cy = 95
    f.append(circle(sx, cy, 4, fill=INK, stroke=INK))
    f.append(text(sx, cy - 14, "джерело", size=11, color=MUTED))
    # резистор Rs (зигзаг)
    rx0 = sx + 30
    rx1 = rx0 + 70
    f.append(line(sx, cy, rx0, cy, WIRE, 2))
    zz = "M%.0f,%.0f l8,-9 l12,18 l12,-18 l12,18 l12,-18 l8,9" % (rx0, cy)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (zz, WIRE))
    f.append(text((rx0 + rx1) / 2, cy - 16, "Rs (опір джерела)", size=12, color=INK))
    # вузол входу
    nx = rx1 + 60
    f.append(line(rx1, cy, nx, cy, WIRE, 2))
    f.append(circle(nx, cy, 4, fill=INK, stroke=INK))
    f.append(text(nx + 8, cy - 8, "вхід підсилювача", size=11, color=MUTED, anchor="start"))
    # ємність Міллера на землю
    f.append(line(nx, cy, nx, cy + 28, WIRE, 2))
    f.append(cap(nx, cy + 40, horizontal=False, gap=8, plate=34, color=POS))
    f.append(text(nx + 16, cy + 40, "C·(1+A)", size=13, bold=True, color=POS, anchor="start"))
    gy = cy + 70
    f.append(line(nx, cy + 52, nx, gy, WIRE, 2))
    f.append(line(nx - 16, gy, nx + 16, gy, WIRE, 2.4))
    f.append(line(nx - 9, gy + 6, nx + 9, gy + 6, WIRE, 2))

    # низ: АЧХ — пологий спад через злам
    ax0, ay0 = 110, 330      # початок осей
    axw, ayh = 520, 150
    f.append(line(ax0, ay0, ax0 + axw, ay0, INK, 2))           # вісь частоти
    f.append(line(ax0, ay0, ax0, ay0 - ayh, INK, 2))           # вісь рівня
    f.append(text(ax0 + axw, ay0 + 20, "частота →", size=12, color=MUTED, anchor="end"))
    f.append(text(ax0 - 8, ay0 - ayh + 4, "рівень", size=12, color=MUTED, anchor="end"))

    # пласка ділянка, тоді спад −20 дБ/дек після зламу
    fb = ax0 + 175           # частота зламу
    flat_y = ay0 - ayh + 18
    f.append(line(ax0, flat_y, fb, flat_y, NEG, 2.6))
    # спадна частина
    f.append(line(fb, flat_y, ax0 + axw - 20, ay0 - 14, NEG, 2.6))
    # пунктир зламу
    f.append(line(fb, ay0, fb, flat_y, MUTED, 1.4, dash="5,4"))
    f.append(text(fb, ay0 + 18, "частота зламу", size=11, color=INK))
    f.append(text(fb + 6, ay0 + 33, "f = 1 / (2π·Rs·C·(1+A))", size=11, color=POS, anchor="start"))
    # стрілка: чим більша C, тим лівіше злам
    f.append(arrow(fb - 6, flat_y - 26, fb - 80, flat_y - 26, color=POS, sw=2))
    f.append(text(fb - 10, flat_y - 32, "більша C → злам лівіше → смуга вужча", size=11, color=POS, anchor="end"))

    render(os.path.join(IMG, "bandwidth.svg"), W, H, *f)


# ── 3. Той самий ефект навмисне: інтегратор Міллера ─────────────────────────
def fig_integrator():
    W, H = 700, 330
    f = []
    f.append(text(W / 2, 26, "Той самий ефект — навмисне: одна ємність ЗЗ працює як велетенська й точна", size=14, bold=True))

    cx = 360
    cy = 185
    f.append(amp_triangle(cx, cy, 96, 104, "−A"))
    # інвертуючий вхід (−) зверху ліворуч
    inx = cx - 180
    iny = cy - 22
    f.append(line(inx, iny, cx - 48, iny, WIRE, 2))
    f.append(text(cx - 56, iny + 5, "−", size=18, bold=True, color=NEG, anchor="end"))
    # неінвертуючий (+) на землю
    f.append(line(cx - 48, cy + 22, cx - 80, cy + 22, WIRE, 2))
    f.append(text(cx - 56, cy + 27, "+", size=18, bold=True, color=POS, anchor="end"))
    gy = cy + 78
    f.append(line(cx - 80, cy + 22, cx - 80, gy, WIRE, 2))
    f.append(line(cx - 92, gy, cx - 68, gy, WIRE, 2.2))
    f.append(line(cx - 86, gy + 6, cx - 74, gy + 6, WIRE, 2))
    # вхідний резистор R
    rx0 = inx - 90
    f.append(circle(rx0, iny, 4, fill=INK, stroke=INK))
    f.append(text(rx0, iny - 14, "вхід", size=12, color=MUTED))
    zz = "M%.0f,%.0f l8,-8 l11,16 l11,-16 l11,16 l8,-8" % (rx0 + 8, iny)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (zz, WIRE))
    f.append(line(rx0, iny, rx0 + 8, iny, WIRE, 2))
    f.append(line(rx0 + 57, iny, inx, iny, WIRE, 2))
    f.append(text(rx0 + 30, iny + 22, "R", size=15, bold=True))

    # ємність зворотного зв'язку C з виходу на (−)
    outx = cx + 110
    f.append(line(cx + 48, cy, outx, cy, WIRE, 2))
    f.append(circle(outx, cy, 4, fill=INK, stroke=INK))
    f.append(text(outx + 8, cy + 5, "вихід", size=12, color=MUTED, anchor="start"))
    topy = cy - 86
    f.append(line(inx, iny, inx, topy, WIRE, 2))
    f.append(line(inx, topy, cx - 16, topy, WIRE, 2))
    f.append(cap(cx, topy, horizontal=True, gap=9, plate=24, color=POS))
    f.append(line(cx + 16, topy, outx, topy, WIRE, 2))
    f.append(line(outx, topy, outx, cy, WIRE, 2))
    f.append(text(cx, topy - 12, "C", size=16, bold=True, color=POS))

    # підпис унизу
    box, bw, bh = textbox(W / 2, 300, "вихід = −(1/RC) · ∫ вхід  dt    (рівне, точне інтегрування)",
                          size=13, fill="#eafaf0", stroke=FIELD, pad=8, color=INK)
    f.append(box)

    render(os.path.join(IMG, "integrator.svg"), W, H, *f)


# ── 4. Теорема Міллера: місток Z → дві ємності на землю ──────────────────────
def fig_theorem():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 26, "Теорема Міллера: одна ланка-місток Z стає двома на землю",
                  size=15, bold=True))

    # ЛІВОРУЧ: підсилювач −A з ланкою Z між входом і виходом
    lx = 175
    midy = 205
    f.append(amp_triangle(lx, midy, 86, 92, "−A"))
    inx = lx - 118
    outx = lx + 118
    f.append(line(inx, midy, lx - 43, midy, WIRE, 2))
    f.append(circle(inx, midy, 4, fill=INK, stroke=INK))
    f.append(text(inx - 6, midy + 5, "V₁", size=13, color=MUTED, anchor="end"))
    f.append(line(lx + 43, midy, outx, midy, WIRE, 2))
    f.append(circle(outx, midy, 4, fill=INK, stroke=INK))
    f.append(text(outx + 6, midy + 5, "V₂ = −A·V₁", size=12, color=MUTED, anchor="start"))
    # ланка Z містком зверху
    topy = midy - 80
    f.append(line(inx, midy, inx, topy, WIRE, 2))
    f.append(line(inx, topy, lx - 26, topy, WIRE, 2))
    f.append(rect(lx - 26, topy - 11, 52, 22, fill=FILL, stroke=POS, sw=1.8))
    f.append(text(lx, topy + 5, "Z", size=16, bold=True, color=POS))
    f.append(line(lx + 26, topy, outx, topy, WIRE, 2))
    f.append(line(outx, topy, outx, midy, WIRE, 2))
    f.append(text(lx, midy + 76, "місток між входом і виходом", size=12, color=MUTED, italic=True))

    # стрілка-перетворення
    f.append(arrow(lx + 168, midy, lx + 222, midy, color=FIELD, sw=2.4))
    f.append(text(lx + 195, midy - 12, "те саме для вузлів", size=11, color=FIELD))

    # ПРАВОРУЧ: дві окремі ланки на землю
    gy = midy + 92
    # вхідна гілка
    rxa = 520
    f.append(circle(rxa, midy - 78, 4, fill=INK, stroke=INK))
    f.append(text(rxa, midy - 92, "вхід", size=12, color=MUTED))
    f.append(line(rxa, midy - 78, rxa, midy - 40, WIRE, 2))
    f.append(rect(rxa - 28, midy - 40, 56, 26, fill=FILL, stroke=POS, sw=1.8))
    f.append(text(rxa, midy - 22, "Z/(1−K)", size=13, bold=True, color=POS))
    f.append(line(rxa, midy - 14, rxa, gy, WIRE, 2))
    f.append(line(rxa - 16, gy, rxa + 16, gy, WIRE, 2.4))
    f.append(line(rxa - 9, gy + 6, rxa + 9, gy + 6, WIRE, 2))
    # вихідна гілка
    rxb = 650
    f.append(circle(rxb, midy - 78, 4, fill=INK, stroke=INK))
    f.append(text(rxb, midy - 92, "вихід", size=12, color=MUTED))
    f.append(line(rxb, midy - 78, rxb, midy - 40, WIRE, 2))
    f.append(rect(rxb - 30, midy - 40, 60, 26, fill=FILL, stroke=NEG, sw=1.8))
    f.append(text(rxb, midy - 22, "Z/(1−1/K)", size=12, bold=True, color=NEG))
    f.append(line(rxb, midy - 14, rxb, gy, WIRE, 2))
    f.append(line(rxb - 16, gy, rxb + 16, gy, WIRE, 2.4))
    f.append(line(rxb - 9, gy + 6, rxb + 9, gy + 6, WIRE, 2))
    f.append(text((rxa + rxb) / 2, gy + 30, "K = V₂/V₁  (тут K = −A)", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "theorem.svg"), W, H, *f)


# ── 5. Ефективна ємність спадає з частотою (множник не сталий) ───────────────
def fig_caprolloff():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, "Множник Міллера не сталий: ефективна ємність спадає, коли підсилення падає",
                  size=14, bold=True))

    ax0, ay0 = 110, 300          # початок осей
    axw, ayh = 540, 220
    f.append(line(ax0, ay0, ax0 + axw, ay0, INK, 2))            # вісь частоти
    f.append(line(ax0, ay0, ax0, ay0 - ayh, INK, 2))            # вісь ємності
    f.append(text(ax0 + axw, ay0 + 20, "частота (лог) →", size=12, color=MUTED, anchor="end"))
    f.append(text(ax0 - 8, ay0 - ayh + 6, "C_еф", size=12, color=MUTED, anchor="end"))

    # плато C·(1+A₀), тоді спад до голої C
    plat_y = ay0 - ayh + 30      # рівень плато
    bare_y = ay0 - 24            # рівень «гола C»
    fp = ax0 + 210               # частота полюса (де спад починається)
    fz = ax0 + 430               # вище — множник ≈1
    f.append(line(ax0, plat_y, fp, plat_y, POS, 2.8))
    # спадна ділянка (−1 нахил у лог-лог): з плато до голої C
    f.append(line(fp, plat_y, fz, bare_y, POS, 2.8))
    f.append(line(fz, bare_y, ax0 + axw - 10, bare_y, NEG, 2.6))
    # позначки рівнів на осі
    f.append(line(ax0 - 4, plat_y, ax0 + 4, plat_y, INK, 2))
    f.append(text(ax0 - 8, plat_y + 4, "C·(1+A₀)", size=12, bold=True, color=POS, anchor="end"))
    f.append(line(ax0 - 4, bare_y, ax0 + 4, bare_y, INK, 2))
    f.append(text(ax0 - 8, bare_y + 4, "C", size=12, bold=True, color=NEG, anchor="end"))
    # вертикаль домінантного полюса
    f.append(line(fp, ay0, fp, plat_y, MUTED, 1.4, dash="5,4"))
    f.append(text(fp, ay0 + 18, "полюс (тут падає A)", size=11, color=INK))
    # підписи зон
    f.append(text((ax0 + fp) / 2, plat_y - 12, "A≈A₀: повний множник", size=11, color=POS))
    f.append(text((fz + axw + ax0) / 2 - 10, bare_y - 12, "A≈1: множника нема", size=11, color=NEG, anchor="middle"))

    render(os.path.join(IMG, "caprolloff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_multiply()
    fig_bandwidth()
    fig_integrator()
    fig_theorem()
    fig_caprolloff()
    print("written:", os.listdir(IMG))
