# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ статті «Типи як дизайн». Вивід — ./img/*.svg.
Окремий файл, щоб не чіпати figs.py базової статті."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
RED_FILL = "#fdecea"
BLUE_FILL = "#eaf0fd"


def polygon(points, fill, stroke="none", sw=0):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    s = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ' stroke="none"'
    return '<polygon points="%s" fill="%s"%s/>' % (pts, fill, s)


def fig_algebra_cardinality():
    """Три дії алгебри типів із живим підрахунком: сума додає, добуток множить,
    функція підносить до степеня. Ключ: множення породжує перехресні члени —
    саме вони й є незаконні стани; додавання їх не породжує."""
    W, H = 800, 440
    frags = []
    frags.append(text(W / 2, 34, "Скільки значень уміщає тип: три дії алгебри",
                      size=16, bold=True))

    rows = [
        ("СУМА (АБО):   |A + B|  =  |A| + |B|",
         "Option⟨uint8⟩ = 1 + 256 = 257 значень",
         FIELD, GREEN_FILL),
        ("ДОБУТОК (І):   |A × B|  =  |A| · |B|",
         "(bool, uint8) = 2 · 256 = 512 значень",
         POS, RED_FILL),
        ("ФУНКЦІЯ (→):   |A → B|  =  |B| ^ |A|",
         "bool → bool = 2² = 4 функції",
         INK, FILL),
    ]
    x, w = 90, 620
    y = 66
    for head, body, col, fill in rows:
        frags.append(fitbox(x, y, w, 74, head + "\n" + body, size=15,
                            fill=fill, stroke=col, sw=1.8, color=INK))
        y += 96

    frags.append(text(W / 2, 420,
                      "Додавання не дає перехресних членів. Множення дає — і кожен зайвий перехресний є незаконний стан.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "algebra-cardinality.svg"), W, H, *frags)


def fig_range_invariant():
    """Інваріант lo ≤ hi. Ліворуч добуток (lo, hi) — пів-квадрата незаконне
    (hi < lo). Праворуч переписане подання (lo, len ≥ 0), hi = lo+len:
    незаконного регіону немає, бо інваріант став наслідком форми."""
    W, H = 820, 380
    frags = []
    frags.append(text(W / 2, 30, "Інваріант lo ≤ hi зробити наслідком форми даних",
                      size=16, bold=True))

    # ── Ліворуч: (lo, hi) — квадрат із діагоналлю ──
    lx0, lx1, ly0, ly1 = 80, 280, 80, 280      # ly0 — верх (hi max), ly1 — низ (hi min)
    # діагональ hi = lo: від (lo min, hi min)=(80,280) до (lo max, hi max)=(280,80)
    frags.append(polygon([(lx0, ly0), (lx1, ly0), (lx0, ly1)], GREEN_FILL))   # легально (hi ≥ lo)
    frags.append(polygon([(lx1, ly0), (lx1, ly1), (lx0, ly1)], RED_FILL))     # незаконно (hi < lo)
    frags.append(rect(lx0, ly0, lx1 - lx0, ly1 - ly0, fill="none", stroke=INK, sw=1.5))
    frags.append(line(lx0, ly1, lx1, ly0, color=INK, sw=1.6))
    frags.append(mtext(140, 138, ["hi ≥ lo", "легально"], size=12, color=FIELD, bold=True))
    frags.append(mtext(222, 210, ["hi < lo", "незаконно"], size=12, color=POS, bold=True))
    frags.append(text(66, 184, "hi ↑", size=12, color=MUTED, anchor="end"))
    frags.append(text(180, 300, "lo →", size=12, color=MUTED))
    frags.append(text(180, 322, "struct { lo, hi } — пів-квадрата незаконне", size=12, color=INK))

    # ── Праворуч: (lo, len ≥ 0) — увесь квадрат легальний ──
    rx0, rx1, ry0, ry1 = 520, 720, 80, 280
    frags.append(rect(rx0, ry0, rx1 - rx0, ry1 - ry0, fill=GREEN_FILL, stroke=INK, sw=1.5))
    frags.append(mtext(620, 168, ["будь-яке (lo, len)", "hi = lo + len ≥ lo"],
                      size=12, color=FIELD, bold=True))
    frags.append(text(620, 300, "lo →", size=12, color=MUTED))
    frags.append(text(620, 322, "struct { lo, len } — незаконного нема", size=12, color=INK))

    # ── Стрілка-перехід ──
    frags.append(arrow(300, 180, 500, 180, color=INK, sw=2))
    b, bw, bh = textbox(400, 150, "переписати\nподання", size=12, bold=True, fill=BG, stroke=INK)
    frags.append(b)

    render(os.path.join(IMG, "range-invariant.svg"), W, H, *frags)


def fig_typestate():
    """Типостан: стан як частина типу. Операція визначена лише на своєму
    стані-типі; виклик з чужого стану — помилка збірки, не рантайму."""
    W, H = 820, 320
    frags = []
    frags.append(text(W / 2, 30, "Типостан: дозволені лише легальні переходи", size=16, bold=True))

    # три стани-типи
    states = [("Closed", 90), ("Open", 335), ("Authed", 585)]
    boxes = {}
    for name, bx in states:
        frags.append(fitbox(bx, 82, 150, 54, name, size=15, bold=True,
                            fill=BLUE_FILL, stroke=NEG))
        boxes[name] = (bx, bx + 150, 82, 82 + 54)   # x0,x1,y0,y1

    midy = 109
    # connect: Closed → Open
    frags.append(arrow(240, midy, 335, midy, color=INK, sw=1.8))
    bb, _, _ = textbox(287, 88, "connect()", size=12, fill=BG, stroke=MUTED, color=INK)
    frags.append(bb)
    # authenticate: Open → Authed
    frags.append(arrow(485, midy, 585, midy, color=INK, sw=1.8))
    bb, _, _ = textbox(535, 88, "authenticate()", size=12, fill=BG, stroke=MUTED, color=INK)
    frags.append(bb)
    # close: Open → Closed (нижня смуга)
    frags.append(arrow(400, 168, 170, 168, color=INK, sw=1.6))
    bb, _, _ = textbox(292, 186, "close()", size=12, fill=BG, stroke=MUTED, color=INK)
    frags.append(bb)

    # незаконний виклик: request() зі стану Closed — не компілюється
    frags.append(line(160, 136, 160, 210, color=POS, sw=1.8, dash="5 4"))
    bb, _, _ = textbox(160, 232, "request() з Closed:\nне компілюється", size=11,
                       fill=RED_FILL, stroke=POS, color=INK, bold=True)
    frags.append(bb)

    frags.append(text(W / 2, 292,
                      "Кожна операція живе лише на своєму стані-типі: виклик з чужого стану — помилка збірки.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "typestate.svg"), W, H, *frags)


def fig_guarantee_spectrum():
    """Де живе доказ інваріанта: від «перевіряти всюди» (доказ ніде) до
    структурної неможливості й уточнених типів (доказ у самому типі).
    Що нижче — то сильніша гарантія й вища ціна."""
    W, H = 800, 390
    frags = []
    frags.append(text(W / 2, 32, "Де живе гарантія інваріанта", size=16, bold=True))

    rungs = [
        ("Перевіряти всюди", "доказ ніде не живе — кожне місце боронить себе саме", RED_FILL, POS),
        ("Розумний конструктор", "доказ в одній точці входу; далі його носить сам тип", "#fff6e6", "#c07a00"),
        ("Структурно неможливо", "незаконне не має форми взагалі — нема чого доводити", GREEN_FILL, FIELD),
        ("Уточнені / залежні типи", "систему типів змушено довести інваріант — ціною складності", BLUE_FILL, NEG),
    ]
    x, w = 130, 540
    y = 62
    for head, body, fill, col in rungs:
        frags.append(fitbox(x, y, w, 60, head + "\n" + body, size=13, fill=fill, stroke=col, color=INK))
        y += 76

    # вертикальна вісь «сильніше»
    frags.append(arrow(80, 74, 80, 356, color=INK, sw=2))
    frags.append(text(80, 66, "слабше", size=11, color=MUTED))
    frags.append(text(80, 372, "сильніше", size=11, color=MUTED))

    render(os.path.join(IMG, "guarantee-spectrum.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_algebra_cardinality()
    fig_range_invariant()
    fig_typestate()
    fig_guarantee_spectrum()
    print("ok")
