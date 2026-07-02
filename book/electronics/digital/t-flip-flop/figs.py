# -*- coding: utf-8 -*-
"""Фігури до теми «T-тригер і ділення частоти».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def dff_box(x, y, w=110, h=90, din="D", label="D"):
    """Прямокутник тригера з входом (din), тактом (трикутник) і виходами Q, Q̄."""
    out = rect(x, y, w, h)
    out += text(x + w / 2, y - 8, label, size=13, color=MUTED)
    # вхід даних
    out += text(x + 14, y + 26, din, size=15, bold=True, anchor="start")
    # тактовий вхід із трикутником «❯»
    ty = y + h - 24
    out += text(x + 14, ty + 5, "clk", size=12, color=MUTED, anchor="start")
    # трикутник спрацювання по фронту (біля лівої грані на рівні clk)
    out += ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
            'stroke="%s" stroke-width="1.6"/>' % (x, ty - 7, x + 11, ty, x, ty + 7, LINE))
    # виходи
    out += text(x + w - 12, y + 26, "Q", size=15, bold=True, anchor="end")
    out += text(x + w - 12, y + h - 20, "Q̄", size=15, bold=True, anchor="end")
    return out


# ── 1. T-тригер із D-тригера: Q̄ → D ─────────────────────────────────────────
def fig_t_from_d():
    W, H = 560, 300
    bx, by, bw, bh = 210, 95, 130, 100
    f = [dff_box(bx, by, bw, bh, din="D", label="D-тригер")]
    # такт зліва
    f.append(text(bx - 118, by + bh - 19, "такт", size=14, bold=True, anchor="start"))
    f.append(arrow(bx - 60, by + bh - 24, bx - 1, by + bh - 24, color=INK))
    # вихід Q праворуч
    qx = bx + bw
    f.append(line(qx, by + 26, qx + 70, by + 26, color=INK, sw=1.8))
    f.append(text(qx + 78, by + 31, "Q", size=15, bold=True, anchor="start"))
    # зворотний дріт Q̄ → D (знизу навколо)
    qbx = qx
    qby = by + bh - 20
    loop_y = by + bh + 45
    f.append(line(qbx, qby, qbx + 40, qby, color=FIELD, sw=2.2))
    f.append(line(qbx + 40, qby, qbx + 40, loop_y, color=FIELD, sw=2.2))
    f.append(line(qbx + 40, loop_y, bx - 40, loop_y, color=FIELD, sw=2.2))
    f.append(line(bx - 40, loop_y, bx - 40, by + 26, color=FIELD, sw=2.2))
    f.append(arrow(bx - 40, by + 26, bx - 1, by + 26, color=FIELD))
    f.append(text((bx - 40 + qbx + 40) / 2, loop_y + 20,
                  "зворотний дріт: Q̄ → D", size=14, bold=True, color=FIELD))
    f.append(text(qbx + 48, qby - 8, "Q̄", size=14, bold=True, color=FIELD, anchor="start"))
    render(os.path.join(OUT, 't-from-d.svg'), W, H, *f)


# ── допоміжне: осі часу для хвиль ────────────────────────────────────────────
def clock_wave(x0, y0, unit, n, hi=26, level_hi=None):
    """Меандр такту: n повних періодів, кожен = 2*unit (unit — півперіод).
    Повертає (svg, [x-координати наростань])."""
    seg = []
    rises = []
    x = x0
    y_hi = y0 - hi
    y_lo = y0
    # починаємо з низу
    cur = y_lo
    seg.append(('M', x, cur))
    for i in range(n):
        # наростання
        rises.append(x)
        seg.append(('L', x, y_hi)); cur = y_hi
        seg.append(('L', x + unit, y_hi))
        # спад
        seg.append(('L', x + unit, y_lo)); cur = y_lo
        seg.append(('L', x + 2 * unit, y_lo))
        x += 2 * unit
    d = " ".join("%s%.1f %.1f" % (c, xx, yy) for c, xx, yy in seg)
    svg = '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)
    return svg, rises, x


def toggle_wave(x0, y0, rises, xend, hi=26, start=0):
    """Вихід Q: перевертається на кожній x із rises. start — початковий рівень (0/1)."""
    y_lo = y0
    y_hi = y0 - hi
    lvl = start
    pts = [('M', x0, y_lo if lvl == 0 else y_hi)]
    for rx in rises:
        # горизонталь до фронту на поточному рівні
        pts.append(('L', rx, y_lo if lvl == 0 else y_hi))
        lvl ^= 1
        pts.append(('L', rx, y_lo if lvl == 0 else y_hi))
    pts.append(('L', xend, y_lo if lvl == 0 else y_hi))
    d = " ".join("%s%.1f %.1f" % (c, xx, yy) for c, xx, yy in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, FIELD)


def rise_marks(rises, y):
    out = ""
    for rx in rises:
        out += ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                % (rx - 5, y, rx + 5, y, rx, y - 9, POS))
    return out


# ── 2. Часова діаграма: поділ на 2 ───────────────────────────────────────────
def fig_divide_by_2():
    W, H = 620, 300
    x0 = 120
    unit = 34
    n = 6
    f = []
    # такт
    yc = 90
    clk, rises, xend = clock_wave(x0, yc, unit, n)
    f.append(rise_marks(rises, yc - 26 - 6))
    f.append(clk)
    f.append(text(x0 - 14, yc - 12, "такт", size=15, bold=True, anchor="end"))
    f.append(text(x0 - 14, yc + 4, "f", size=13, color=MUTED, italic=True, anchor="end"))
    # Q
    yq = 210
    f.append(toggle_wave(x0, yq, rises, xend, start=0))
    f.append(text(x0 - 14, yq - 12, "Q", size=15, bold=True, anchor="end"))
    f.append(text(x0 - 14, yq + 4, "f / 2", size=13, color=MUTED, italic=True, anchor="end"))
    # осі-базові тонкі лінії
    for yy in (yc, yq):
        f.append(line(x0, yy + 2, xend + 6, yy + 2, color=MUTED, sw=0.8, dash="2 3"))
    # позначка: один період Q = два періоди такту
    bx1, bx2 = rises[0], rises[2]
    f.append(line(bx1, yq + 22, bx2, yq + 22, color=INK, sw=1.4))
    f.append(line(bx1, yq + 16, bx1, yq + 28, color=INK, sw=1.4))
    f.append(line(bx2, yq + 16, bx2, yq + 28, color=INK, sw=1.4))
    f.append(text((bx1 + bx2) / 2, yq + 40, "1 період Q = 2 періоди такту",
                  size=13, color=INK))
    render(os.path.join(OUT, 'divide-by-2.svg'), W, H, *f)


# ── 3. Ланцюг: f/2, f/4, f/8 ─────────────────────────────────────────────────
def fig_chain_divide():
    W, H = 640, 320
    x0 = 120
    unit = 18
    n = 12
    f = []
    ys = [70, 160, 250]
    labels = [("такт", "f"), ("Q0", "f / 2"), ("Q1", "f / 4"), ("Q2", "f / 8")]
    # такт
    yc = ys[0] - 0  # виведемо 4 доріжки: такт + 3 виходи
    # доріжка тактів окремо зверху
    ytop = 60
    clk, rises0, xend = clock_wave(x0, ytop, unit, n)
    f.append(clk)
    f.append(text(x0 - 14, ytop - 12, "такт", size=14, bold=True, anchor="end"))
    f.append(text(x0 - 14, ytop + 4, "f", size=12, color=MUTED, italic=True, anchor="end"))
    # Q0 ділить такт: фронти Q0 — наростання такту
    y1 = 140
    f.append(toggle_wave(x0, y1, rises0, xend, start=0))
    f.append(text(x0 - 14, y1 - 12, "Q0", size=14, bold=True, anchor="end"))
    f.append(text(x0 - 14, y1 + 4, "f/2", size=12, color=MUTED, italic=True, anchor="end"))
    # наростання Q0 = кожен 2-й фронт такту (Q0 йде 0→1 на rises0[0],2,4..)
    rises1 = rises0[0::2]
    y2 = 220
    f.append(toggle_wave(x0, y2, rises1, xend, start=0))
    f.append(text(x0 - 14, y2 - 12, "Q1", size=14, bold=True, anchor="end"))
    f.append(text(x0 - 14, y2 + 4, "f/4", size=12, color=MUTED, italic=True, anchor="end"))
    rises2 = rises1[0::2]
    y3 = 300
    f.append(toggle_wave(x0, y3, rises2, xend, start=0))
    f.append(text(x0 - 14, y3 - 12, "Q2", size=14, bold=True, anchor="end"))
    f.append(text(x0 - 14, y3 + 4, "f/8", size=12, color=MUTED, italic=True, anchor="end"))
    for yy in (ytop, y1, y2, y3):
        f.append(line(x0, yy + 2, xend + 4, yy + 2, color=MUTED, sw=0.7, dash="2 3"))
    render(os.path.join(OUT, 'chain-divide.svg'), W, H, *f)


# ── 4. Символ T-тригера ──────────────────────────────────────────────────────
def fig_symbol():
    W, H = 420, 260
    bx, by, bw, bh = 150, 70, 130, 110
    f = [rect(bx, by, bw, bh)]
    # вхід T
    f.append(line(bx - 55, by + 30, bx, by + 30, color=INK, sw=1.8))
    f.append(text(bx - 62, by + 35, "T", size=17, bold=True, anchor="end"))
    f.append(text(bx + 14, by + 35, "T", size=16, bold=True, anchor="start"))
    # тактовий вхід із трикутником
    ty = by + bh - 28
    f.append(line(bx - 55, ty, bx, ty, color=INK, sw=1.8))
    f.append(text(bx - 62, ty + 5, "такт", size=14, bold=True, anchor="end"))
    f.append(('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
              'stroke="%s" stroke-width="1.8"/>' % (bx, ty - 8, bx + 13, ty, bx, ty + 8, LINE)))
    # виходи
    f.append(line(bx + bw, by + 30, bx + bw + 55, by + 30, color=INK, sw=1.8))
    f.append(text(bx + bw + 62, by + 35, "Q", size=17, bold=True, anchor="start"))
    f.append(line(bx + bw, by + bh - 28, bx + bw + 55, by + bh - 28, color=INK, sw=1.8))
    f.append(text(bx + bw + 62, by + bh - 23, "Q̄", size=17, bold=True, anchor="start"))
    # підпис-нагадування про трикутник
    box, w, h = textbox(W / 2, by + bh + 45,
                        "трикутник «❯» = спрацювання по фронту",
                        size=13, color=INK)
    f.append(box)
    render(os.path.join(OUT, 'symbol.svg'), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до історичної вставки «hist-jk-flip-flop.md»
# ════════════════════════════════════════════════════════════════════════════

# ── 5. Драбина літер Нельсона: A&B, C&D … J&K (а не ініціали) ─────────────────
def fig_hist_nelson_ladder():
    W, H = 640, 380
    f = []
    f.append(text(W / 2, 34, "Як Нельсон роздавав літери входам тригерів", size=16, bold=True))
    f.append(text(W / 2, 56, "по дві на кожен наступний тригер — просто за абеткою", size=12, color=MUTED))

    pairs = [("1", "A", "B"), ("2", "C", "D"), ("3", "E", "F"), ("4", "G", "H"), ("5", "J", "K")]
    x_no = 150
    x_a = 320
    x_b = 410
    y0 = 110
    dy = 46
    for i, (no, a, b) in enumerate(pairs):
        y = y0 + i * dy
        last = (i == len(pairs) - 1)
        col = POS if last else INK
        fill = "#fdecea" if last else "#f4f6f8"
        f.append(text(x_no, y + 5, "тригер №" + no + ":", size=13, color=MUTED, anchor="end"))
        # два кружечки-входи
        for cx, lab in ((x_a, a), (x_b, b)):
            f.append(circle(cx, y, 15, fill=fill, stroke=col, sw=2.2))
            f.append(text(cx, y + 5, lab, size=15, color=col, bold=True))
    # підпис до останньої пари
    f.append(text(x_b + 40, y0 + 4 * dy + 5,
                  "← кінчалися зручні літери", size=12, color=POS, bold=True, anchor="start"))

    # винесений висновок
    body, w0, h0 = textbox(W / 2, 348,
                           "J і K — просто п’ята пара за абеткою (I пропущено, щоб не плутати з одиницею).\n"
                           "Це НЕ ініціали — на відміну від S/R, що таки скорочення від set/reset.",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(OUT, 'hist-nelson-ladder.svg'), W, H, *f)


# ── 6. SR-заборона проти JK-toggle: що саме прибрали ─────────────────────────
def fig_hist_sr_vs_jk():
    W, H = 660, 360
    f = []
    f.append(text(W / 2, 32, "Що JK виправив у SR: заборонений куток став toggle", size=15, bold=True))

    # дві таблиці 2×2 поруч; рядки — входи, клітинка — що з виходом
    def truthbox(x0, y0, title, cells, col_title):
        out = [text(x0 + 95, y0 - 14, title, size=13, bold=True, color=col_title)]
        cw, ch = 95, 46
        # шапка стовпців (другий вхід)
        out.append(text(x0 + cw / 2, y0 - 30, "", size=11))
        # підписи осей
        out.append(text(x0 - 14, y0 + ch, hdr_row, size=11, color=MUTED, anchor="end", italic=True) if False else "")
        for r in range(2):
            for c in range(2):
                x = x0 + c * cw
                y = y0 + r * ch
                val, kind = cells[r][c]
                fill = {"ok": "#eef7f0", "hold": "#f4f6f8", "bad": "#fdecea", "tog": "#eaf0fd"}[kind]
                stroke = {"ok": FIELD, "hold": MUTED, "bad": POS, "tog": NEG}[kind]
                out.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=2))
                out.append(text(x + cw / 2, y + ch / 2 + 4, val, size=12,
                                color=stroke, bold=(kind in ("bad", "tog"))))
        return "".join(out)

    hdr_row = ""
    # SR-таблиця
    sx, sy = 90, 120
    sr_cells = [
        [("тримає", "hold"), ("Q=1 (set)", "ok")],     # S=0: R=0 тримає, R=1 ... насправді R скидає
        [("Q=0 (reset)", "ok"), ("ЗАБОРОНА", "bad")],  # S=1
    ]
    # осі підпишемо руками нижче — тут лише клітинки
    f.append(truthbox(sx, sy, "SR-засувка", sr_cells, POS))
    # підписи входів навколо SR
    f.append(text(sx + 95, sy - 32, "R=0     R=1", size=11, color=MUTED))
    f.append(text(sx - 16, sy + 23, "S=0", size=11, color=MUTED, anchor="end"))
    f.append(text(sx - 16, sy + 69, "S=1", size=11, color=MUTED, anchor="end"))
    f.append(text(sx + 95, sy + 118, "S=R=1 — обидва разом:", size=11, color=POS, anchor="middle"))
    f.append(text(sx + 95, sy + 134, "вихід невизначений", size=11, color=POS, anchor="middle"))

    # стрілка «замінили на»
    f.append(arrow(sx + 250, sy + 46, sx + 320, sy + 46, color=INK, sw=2.4))
    f.append(text(sx + 285, sy + 34, "JK", size=13, bold=True))

    # JK-таблиця
    jx, jy = sx + 360, sy
    jk_cells = [
        [("тримає", "hold"), ("Q=1 (set)", "ok")],       # J=0: K=0 тримає, K=1 скидає? розкладка нижче
        [("Q=0 (reset)", "ok"), ("TOGGLE", "tog")],      # J=1
    ]
    f.append(truthbox(jx, jy, "JK-тригер", jk_cells, NEG))
    f.append(text(jx + 95, jy - 32, "K=0     K=1", size=11, color=MUTED))
    f.append(text(jx - 16, jy + 23, "J=0", size=11, color=MUTED, anchor="end"))
    f.append(text(jx - 16, jy + 69, "J=1", size=11, color=MUTED, anchor="end"))
    f.append(text(jx + 95, jy + 118, "J=K=1 — обидва разом:", size=11, color=NEG, anchor="middle"))
    f.append(text(jx + 95, jy + 134, "вихід перекидається (T!)", size=11, color=NEG, anchor="middle"))

    body, w0, h0 = textbox(W / 2, 336,
                           "Той самий «обидва входи=1», що в SR був забороною, у JK робить корисне: перемикання.\n"
                           "З’єднай J і K разом — і цей куток стає єдиним режимом: чистий T-тригер.",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(OUT, 'hist-sr-vs-jk.svg'), W, H, *f)


if __name__ == '__main__':
    fig_t_from_d()
    fig_divide_by_2()
    fig_chain_divide()
    fig_symbol()
    fig_hist_nelson_ladder()
    fig_hist_sr_vs_jk()
    print("done:", os.listdir(OUT))
