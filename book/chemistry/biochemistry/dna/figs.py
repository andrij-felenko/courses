# -*- coding: utf-8 -*-
"""Фігури до теми «ДНК» (book/chemistry/biochemistry/dna)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

BIG_LETTERS = ("А", "Г")
GRAY = ("#e9edf2", "#4a5568")
NEW = ("#e8f7ee", FIELD)


# ── Фігура 1: чому пари саме такі ───────────────────────────────────────────
def fig_pairs():
    W, H = 900, 430
    frags = [text(450, 38, "Навпроти кожної літери стоїть тільки її пара",
                  size=17, bold=True)]

    x0, x1 = 130, 790
    y_top_bone, y_bot_bone = 112, 310
    frags.append(line(x0, y_top_bone, x1, y_top_bone, color=MUTED, sw=6))
    frags.append(line(x0, y_bot_bone, x1, y_bot_bone, color=MUTED, sw=6))
    frags.append(text(450, 90, "хребет — однакові ланки цукру й фосфату",
                      size=13, color=MUTED))
    frags.append(text(450, 338, "друга нитка — дзеркальний запис першої",
                      size=13, color=MUTED))

    BIG, SMALL = 90, 50           # висоти великої та малої літери
    Y_UP, Y_DN = 118, 302         # межі, між якими стоїть сходинка
    pairs = [("А", "Т", 2), ("Т", "А", 2), ("Г", "Ц", 3), ("Ц", "Г", 3), ("А", "Т", 2)]
    xs = [180, 320, 460, 600, 740]

    for cx, (up, dn, nbond) in zip(xs, pairs):
        for lab, is_top in ((up, True), (dn, False)):
            wide = lab in BIG_LETTERS
            h = BIG if wide else SMALL
            w = 86 if wide else 64
            y = Y_UP if is_top else Y_DN - h
            fill, stroke = ("#fdecea", POS) if wide else ("#eaf0fd", NEG)
            frags.append(fitbox(cx - w / 2.0, y, w, h, lab, size=30, bold=True,
                                fill=fill, stroke=stroke, color=stroke))
        y_gap_top = Y_UP + (BIG if up in BIG_LETTERS else SMALL)
        y_gap_bot = Y_DN - (BIG if dn in BIG_LETTERS else SMALL)
        offs = (-10, 10) if nbond == 2 else (-16, 0, 16)
        for dx in offs:
            frags.append(line(cx + dx, y_gap_top + 3, cx + dx, y_gap_bot - 3,
                              color=MUTED, sw=2, dash="4,4"))

    frags.append(mtext(450, 370, [
        "рожеві — великі літери (А, Г), сині — малі (Т, Ц): велика завжди в парі з малою,",
        "тому всі сходинки однакової ширини; пунктир — слабкі водневі зачіпки (А–Т дві, Г–Ц три)",
    ], size=13, color=MUTED))

    render(os.path.join(IMG, 'pairs.svg'), W, H, *frags)


# ── Фігура 2: як робиться копія ─────────────────────────────────────────────
def _ladder(cx, y_row, tops, bots, top_style, bot_style, step, cw, ch, drop):
    out = []
    n = len(tops)
    xs = [cx + (i - (n - 1) / 2.0) * step for i in range(n)]
    y_row2 = y_row + drop
    left, right = xs[0] - cw / 2.0 - 14, xs[-1] + cw / 2.0 + 14
    out.append(line(left, y_row - 8, right, y_row - 8, color=MUTED, sw=5))
    out.append(line(left, y_row2 + ch + 8, right, y_row2 + ch + 8, color=MUTED, sw=5))
    for x, a, b in zip(xs, tops, bots):
        out.append(line(x, y_row + ch + 2, x, y_row2 - 2, color=MUTED, sw=2, dash="4,4"))
        out.append(fitbox(x - cw / 2.0, y_row, cw, ch, a, size=20, bold=True,
                          fill=top_style[0], stroke=top_style[1], color=top_style[1]))
        out.append(fitbox(x - cw / 2.0, y_row2, cw, ch, b, size=20, bold=True,
                          fill=bot_style[0], stroke=bot_style[1], color=bot_style[1]))
    return out


def fig_copy():
    W, H = 980, 480
    TOPS = list("АГТЦА")
    BOTS = list("ТЦАГТ")
    frags = [text(490, 36, "Копія робиться сама: кожна нитка диктує свою пару",
                  size=17, bold=True)]

    frags += _ladder(490, 100, TOPS, BOTS, GRAY, GRAY, step=90, cw=46, ch=34, drop=66)
    frags.append(text(150, 152, "запис у двох нитках", size=14, bold=True))

    frags.append(arrow(400, 222, 250, 296, color=MUTED))
    frags.append(arrow(580, 222, 730, 296, color=MUTED))
    frags.append(text(490, 264, "нитки розходяться", size=13, color=MUTED))

    frags += _ladder(250, 320, TOPS, BOTS, GRAY, NEW, step=76, cw=42, ch=32, drop=62)
    frags += _ladder(730, 320, TOPS, BOTS, NEW, GRAY, step=76, cw=42, ch=32, drop=62)

    frags.append(text(490, 456,
                      "кожна копія — одна стара нитка (сіра) і одна щойно добудована (зелена)",
                      size=13, color=MUTED))

    render(os.path.join(IMG, 'copying.svg'), W, H, *frags)


# ── Фігура 3: ген → трійки → амінокислоти ───────────────────────────────────
def fig_gene():
    W, H = 900, 350
    seq = "ТАГЦАЦАТГГАТЦААГЦТГАЦ"          # 21 літера
    lo, hi = 5, 17                          # межі гена в цій нитці
    cw, ch, y = 28, 26, 64
    x0 = 450 - len(seq) * cw / 2.0

    frags = [text(450, 34, "Ген: три літери — одна амінокислота", size=17, bold=True)]

    for i, letter in enumerate(seq):
        inside = lo <= i < hi
        fill, stroke = ("#e8f7ee", FIELD) if inside else ("#f2f2f2", MUTED)
        frags.append(fitbox(x0 + i * cw, y, cw, ch, letter, size=14, bold=inside,
                            fill=fill, stroke=stroke, color=INK if inside else MUTED))

    gene_cx = x0 + (lo + hi) / 2.0 * cw
    frags.append(text(gene_cx, 52, "ген — рецепт одного білка",
                      size=13, bold=True, color=FIELD))

    centers = []
    for k in range(4):
        s = lo + 3 * k
        cx = x0 + (s + 1.5) * cw
        centers.append(cx)
        frags.append(arrow(cx, y + ch + 6, cx, 138, color=MUTED))
        frags.append(fitbox(cx - 42, 140, 84, 34, seq[s:s + 3], size=18, bold=True))
        frags.append(arrow(cx, 178, cx, 216, color=MUTED))

    for k, cx in enumerate(centers):
        if k:
            frags.append(line(centers[k - 1] + 22, 246, cx - 22, 246, color=INK, sw=2))
        frags.append(circle(cx, 246, 22, fill="#fdecea", stroke=POS, sw=2))
        frags.append(text(cx, 253, str(k + 1), size=17, bold=True, color=POS))

    frags.append(arrow(centers[-1] + 30, 246, 676, 246, color=MUTED))
    body, _, _ = textbox(772, 246, "ланцюг згортається\nу білок", size=13,
                         fill="#e8f7ee", stroke=FIELD, sw=2)
    frags.append(body)

    frags.append(text(450, 312,
                      "чотири літери, узяті по три, дають 64 різні трійки — на двадцять амінокислот удосталь",
                      size=13, color=MUTED))

    render(os.path.join(IMG, 'gene-to-protein.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_pairs()
    fig_copy()
    fig_gene()
    print("ok")
