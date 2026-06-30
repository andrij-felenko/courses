# -*- coding: utf-8 -*-
"""Фігури до вставки «math-supernode-system» (book/electronics/analog/supernode).
Дві фігури про МАТРИЧНИЙ бік:
  matglue.svg  — суперузол як склеювання двох рядків і одного стовпця матриці G:
                 рядки a,b додаються в один; рівняння-обмеження заміщає рядок b
  mna.svg      — модифікований вузловий аналіз: облямована матриця [[G B],[C D]]·[v;j]=[i;e],
                 додатковий рядок/стовпець під струм джерела
Запуск:  python figs-math.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def cell(x, y, w, h, s, fill="#ffffff", stroke=LINE, color=INK, size=13, bold=False, sw=1.3):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=3)
    if s != "":
        out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


def bracket_l(x, y, h, color=INK, sw=2.2):
    t = 8
    return (line(x, y, x, y + h, color=color, sw=sw) +
            line(x, y, x + t, y, color=color, sw=sw) +
            line(x, y + h, x + t, y + h, color=color, sw=sw))


def bracket_r(x, y, h, color=INK, sw=2.2):
    t = 8
    return (line(x, y, x, y + h, color=color, sw=sw) +
            line(x, y, x - t, y, color=color, sw=sw) +
            line(x, y + h, x - t, y + h, color=color, sw=sw))


# ════════════════════════════════════════════════════════════════════════════
# 1. matglue.svg — склеювання рядків і стовпця
# ════════════════════════════════════════════════════════════════════════════
def fig_matglue():
    W, H = 860, 430
    f = []
    f.append(text(W / 2, 32, "Суперузол = хірургія над рядками й стовпцями матриці G", size=15, bold=True))

    cw, ch = 52, 34          # клітинка
    labels = ["a", "b", "c"]

    def matrix(ox, oy, rows, title_, glue_rows=None, repl_row=None):
        out = [text(ox + 1.5 * cw, oy - 16, title_, size=13, bold=True, color=INK)]
        # підписи стовпців (V_a V_b V_c)
        for j, lj in enumerate(labels):
            out.append(text(ox + (j + 0.5) * cw, oy - 2, "V_%s" % lj, size=11, color=MUTED))
        for i in range(3):
            for j in range(3):
                x = ox + j * cw
                y = oy + i * ch
                fill = "#ffffff"
                col = INK
                bold = False
                if glue_rows and i in glue_rows:
                    fill = "#eef7f0"
                    col = FIELD
                    bold = True
                if repl_row is not None and i == repl_row:
                    fill = "#eaf0fd"
                    col = NEG
                    bold = True
                out.append(cell(x, y, cw, ch, rows[i][j], fill=fill, color=col, bold=bold))
            # підпис рядка праворуч
            out.append(text(ox + 3 * cw + 14, oy + i * ch + ch / 2 + 4,
                            ["рядок a", "рядок b", "рядок c"][i], size=10, color=MUTED, anchor="start"))
        return "".join(out)

    # ── ліворуч: «наївна» матриця, рядки a і b зіпсовані (невідомий струм) ──
    L = [["g₁+g_ab", "−g_ab", "0"],
         ["−g_ab", "g₃+g_ab", "0"],
         ["0", "0", "g_c"]]
    f.append(matrix(70, 90, L, "якби між a,b був резистор g_ab", glue_rows=None))
    tb, _, _ = textbox(70 + 1.5 * cw, 90 + 3 * ch + 34,
                       "Ідеальне E → g_ab = ∞:\nрядки a і b писати ні з чого",
                       size=10.5, color=INK, fill="#fdecea", stroke=POS)
    f.append(tb)

    # стрілка
    f.append(arrow(395, 165, 445, 165, color=MUTED, sw=2.6))
    f.append(text(420, 150, "суперузол", size=11, color=FIELD, bold=True))

    # ── праворуч: склеєна матриця (рендеримо вручну, бо вміст особливий) ──
    ox, oy = 470, 90
    f.append(text(ox + 1.5 * cw, oy - 16, "склеєна система", size=13, bold=True))
    for j, lj in enumerate(labels):
        f.append(text(ox + (j + 0.5) * cw, oy - 2, "V_%s" % lj, size=11, color=MUTED))
    rowmeta = [("#eef7f0", FIELD, "= I   (a)+(b): баланс суперузла"),
               ("#eaf0fd", NEG, "= E   обмеження V_a−V_b"),
               ("#ffffff", INK, "= 0   звичайний рядок c")]
    cellvals = [["g₁", "g₃", "0"],
                ["+1", "−1", "0"],
                ["0", "0", "g_c"]]
    for i in range(3):
        fill, col, meta = rowmeta[i]
        for j in range(3):
            x = ox + j * cw
            y = oy + i * ch
            f.append(cell(x, y, cw, ch, cellvals[i][j], fill=fill, color=col,
                          bold=(i < 2 and cellvals[i][j] not in ("0",))))
        f.append(text(ox + 3 * cw + 14, oy + i * ch + ch / 2 + 4, meta,
                      size=10, color=col, anchor="start", bold=(i < 2)))
    # вектор невідомих [V_a;V_b;V_c] — компактно зліва від матриці як підпис стовпців уже є

    tb2, _, _ = textbox(W / 2, 392,
                        "Рядок a й рядок b ЗЛИЛИСЯ в один (сума → баланс суперузла, зовнішні g лишилися, спільне g_ab зникло);\n"
                        "звільнений рядок b ЗАМІНЕНО рівнянням-обмеженням  +1·V_a − 1·V_b = E.  Розмір системи той самий.",
                        size=10.5, color=INK, fill=FILL, stroke=LINE)
    f.append(tb2)
    render(os.path.join(IMG, "matglue.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. mna.svg — облямована матриця модифікованого вузлового аналізу
# ════════════════════════════════════════════════════════════════════════════
def fig_mna():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 32, "Як це робить SPICE: модифікований вузловий аналіз", size=15, bold=True))

    # велика блокова матриця 2×2: [[G B],[C D]] · [v;j] = [i;e]
    ox, oy = 150, 80
    BW, BH = 150, 150      # блок G
    sw_blk = 2.0

    # блок G (n×n провідності)
    f.append(rect(ox, oy, BW, BH, fill="#f0f4ff", stroke=NEG, sw=sw_blk, rx=6))
    f.append(text(ox + BW / 2, oy + BH / 2 - 6, "G", size=22, bold=True, color=NEG))
    f.append(text(ox + BW / 2, oy + BH / 2 + 16, "вузлові провідності", size=10, color=MUTED))

    # блок B (n×1) праворуч від G
    bw = 46
    f.append(rect(ox + BW, oy, bw, BH, fill="#eef7f0", stroke=FIELD, sw=sw_blk, rx=6))
    f.append(text(ox + BW + bw / 2, oy + BH / 2 - 6, "B", size=18, bold=True, color=FIELD))
    f.append(text(ox + BW + bw / 2, oy + BH / 2 + 14, "±1", size=11, color=FIELD))

    # блок C (1×n) під G
    bh = 40
    f.append(rect(ox, oy + BH, BW, bh, fill="#eef7f0", stroke=FIELD, sw=sw_blk, rx=6))
    f.append(text(ox + BW / 2, oy + BH + bh / 2 + 5, "C   (±1, …)", size=14, bold=True, color=FIELD))

    # блок D (1×1) кут
    f.append(rect(ox + BW, oy + BH, bw, bh, fill="#ffffff", stroke=LINE, sw=sw_blk, rx=6))
    f.append(text(ox + BW + bw / 2, oy + BH + bh / 2 + 5, "0", size=14, bold=True))

    # дужки навколо всієї матриці
    f.append(bracket_l(ox - 12, oy - 6, BH + bh + 12, sw=2.4))
    f.append(bracket_r(ox + BW + bw + 12, oy - 6, BH + bh + 12, sw=2.4))

    # вектор невідомих [v ; j]
    vx = ox + BW + bw + 40
    vh = BH + bh + 12
    f.append(bracket_l(vx, oy - 6, vh, sw=2.4))
    f.append(text(vx + 26, oy + BH / 2 + 4, "v", size=18, bold=True, color=NEG))
    f.append(text(vx + 26, oy + BH / 2 + 22, "(вузли)", size=9, color=MUTED))
    f.append(line(vx + 6, oy + BH + 2, vx + 46, oy + BH + 2, color="#c8ccd2", sw=1.0, dash="3 3"))
    f.append(text(vx + 26, oy + BH + bh / 2 + 5, "j", size=16, bold=True, color=FIELD))
    f.append(text(vx + 26, oy + BH + bh / 2 + 19, "(струм E)", size=8.5, color=MUTED))
    f.append(bracket_r(vx + 52, oy - 6, vh, sw=2.4))

    # =
    f.append(text(vx + 72, oy + (BH + bh) / 2 + 4, "=", size=20, bold=True))

    # права частина [i ; e]
    rx = vx + 92
    f.append(bracket_l(rx, oy - 6, vh, sw=2.4))
    f.append(text(rx + 26, oy + BH / 2 + 4, "i", size=16, bold=True, color=INK))
    f.append(text(rx + 26, oy + BH / 2 + 20, "(струми)", size=8.5, color=MUTED))
    f.append(line(rx + 6, oy + BH + 2, rx + 46, oy + BH + 2, color="#c8ccd2", sw=1.0, dash="3 3"))
    f.append(text(rx + 26, oy + BH + bh / 2 + 5, "E", size=15, bold=True, color=NEG))
    f.append(text(rx + 26, oy + BH + bh / 2 + 19, "(напруга)", size=8.5, color=MUTED))
    f.append(bracket_r(rx + 52, oy - 6, vh, sw=2.4))

    # підпис під фігурою
    tb3, _, _ = textbox(W / 2, 332,
                        "Кожне джерело напруги додає в систему ОДИН рядок і ОДИН стовпець під свій струм j.\n"
                        "Рядок-обмеження C·v = E задає V₊−V₋; стовпець B вкидає ±j у баланси вузлів. Суперузол отримується сам.",
                        size=10.5, color=INK, fill=FILL, stroke=LINE)
    f.append(tb3)
    render(os.path.join(IMG, "mna.svg"), W, H, *f)


if __name__ == "__main__":
    fig_matglue()
    fig_mna()
    print("OK: 2 фігури у", IMG)
