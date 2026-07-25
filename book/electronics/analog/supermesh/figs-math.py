# -*- coding: utf-8 -*-
"""Фігури до вставки «math-supermesh-system» (book/electronics/analog/supermesh).
Фігура про МАТРИЧНИЙ бік (дзеркало до supernode/figs-math.py, мовою опорів):
  matglue.svg  — супер-чарунка як склеювання двох рядків матриці опорів R:
                 рядки вікон I₁,I₂ додаються в один (напруга джерела гине);
                 рівняння-обмеження I₁−I₂=J заміщає звільнений рядок
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
# 1. matglue.svg — склеювання двох рядків матриці опорів
# ════════════════════════════════════════════════════════════════════════════
def fig_matglue():
    W, H = 880, 430
    f = []
    f.append(text(W / 2, 32, "Супер-чарунка = хірургія над рядками матриці опорів R", size=15, bold=True))

    cw, ch = 56, 34          # клітинка

    # ── ліворуч: «наївні» рядки вікон, у кожному висить напруга джерела U ──
    def matrix_naive(ox, oy):
        out = [text(ox + 1.0 * cw, oy - 16, "наївні рядки вікон", size=13, bold=True, color=INK)]
        for j, lj in enumerate(["I₁", "I₂"]):
            out.append(text(ox + (j + 0.5) * cw, oy - 2, lj, size=11, color=MUTED))
        rows = [["R₁", "0"], ["0", "R₃"]]
        extra = ["+U", "−U"]                 # невідома напруга джерела
        meta = ["= V   вікно I₁", "= 0   вікно I₂"]
        for i in range(2):
            for j in range(2):
                out.append(cell(ox + j * cw, oy + i * ch, cw, ch, rows[i][j],
                                fill="#fdecea", color=POS, bold=(rows[i][j] != "0")))
            # «зайвий» доданок — напруга джерела струму
            out.append(text(ox + 2 * cw + 16, oy + i * ch + ch / 2 + 4, extra[i],
                            size=14, color=POS, bold=True, anchor="middle"))
            out.append(text(ox + 2 * cw + 44, oy + i * ch + ch / 2 + 4, meta[i],
                            size=10, color=MUTED, anchor="start"))
        return "".join(out)

    f.append(matrix_naive(60, 92))
    tb, _, _ = textbox(60 + 1.6 * cw, 92 + 2 * ch + 40,
                       "Джерело струму на спільній гілці →\nу кожному рядку зайва невідома U\n(напруга на джерелі)",
                       size=10.5, color=INK, fill="#fdecea", stroke=POS)
    f.append(tb)

    # стрілка
    f.append(arrow(395, 150, 450, 150, color=MUTED, sw=2.6))
    f.append(text(422, 135, "супер-", size=11, color=FIELD, bold=True))
    f.append(text(422, 122, "чарунка", size=11, color=FIELD, bold=True))

    # ── праворуч: склеєна система ──
    ox, oy = 480, 92
    f.append(text(ox + 1.0 * cw, oy - 16, "склеєна система", size=13, bold=True))
    for j, lj in enumerate(["I₁", "I₂"]):
        f.append(text(ox + (j + 0.5) * cw, oy - 2, lj, size=11, color=MUTED))
    rowmeta = [("#eef7f0", FIELD, "= V   (I₁)+(I₂): U гине, КВН супер-чарунки"),
               ("#eaf0fd", NEG, "= J   обмеження  I₁ − I₂")]
    cellvals = [["R₁", "R₃"],
                ["+1", "−1"]]
    for i in range(2):
        fill, col, meta = rowmeta[i]
        for j in range(2):
            f.append(cell(ox + j * cw, oy + i * ch, cw, ch, cellvals[i][j], fill=fill, color=col, bold=True))
        f.append(text(ox + 2 * cw + 14, oy + i * ch + ch / 2 + 4, meta,
                      size=10, color=col, anchor="start", bold=True))

    tb2, _, _ = textbox(W / 2, 392,
                        "Рядок вікна I₁ й рядок вікна I₂ ЗЛИЛИСЯ в один (сума → закон напруг супер-чарунки: +U від першого\n"
                        "гасить −U від другого, лишаються самі опори периметра); звільнений рядок ЗАМІНЕНО на  I₁ − I₂ = J.",
                        size=10.5, color=INK, fill=FILL, stroke=LINE)
    f.append(tb2)
    render(os.path.join(IMG, "matglue.svg"), W, H, *f)


if __name__ == "__main__":
    fig_matglue()
    print("OK: 1 фігура у", IMG)
