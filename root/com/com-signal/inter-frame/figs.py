# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── frames-similar: два кадри-близнюки та їхня різниця ────────────────────────
# Ідея: кадри N і N+1 майже однакові (те саме тло, зрушений об'єкт); їхня
# поканальна різниця — майже суцільний нуль (чорне) з тонким обідком зміни.

def _scene(ox, oy, w, h, obj_dx, label, p):
    # рамка кадру
    p.append(rect(ox, oy, w, h, fill="#eaf2fb", stroke=INK, sw=1.6, rx=4))
    # земля (нижня смуга)
    gh = h * 0.32
    p.append(rect(ox, oy + h - gh, w, gh, fill="#dfeede", stroke="none", sw=0))
    p.append(line(ox, oy + h - gh, ox + w, oy + h - gh, color="#9ec79a", sw=1.2))
    # сонце (нерухоме тло)
    p.append(circle(ox + w * 0.80, oy + h * 0.24, 13, fill="#fbe7a6", stroke="#e0c060", sw=1.4))
    # об'єкт (зрушений на obj_dx)
    cx = ox + w * 0.34 + obj_dx
    cy = oy + h * 0.52
    p.append(rect(cx - 13, cy - 9, 26, 18, fill="#f3c6bf", stroke=POS, sw=1.6, rx=3))
    p.append(text(ox + w / 2, oy - 8, label, size=12, color=INK, bold=True))


def fig_frames_similar():
    W, H = 720, 250
    p = []
    w, h = 150, 110
    y = 64
    x1 = 40
    x2 = 220
    _scene(x1, y, w, h, 0, "кадр N", p)
    _scene(x2, y, w, h, 16, "кадр N+1", p)

    # знак мінус між кадрами
    p.append(text((x1 + w + x2) / 2, y + h / 2 + 6, "−", size=30, color=INK, bold=True))

    # знак рівності
    eqx = x2 + w + 26
    p.append(text(eqx, y + h / 2 + 6, "=", size=26, color=INK, bold=True))

    # кадр-різниця: чорний фон, тонкий обідок там, де об'єкт зрушився
    dx = eqx + 24
    p.append(rect(dx, y, w, h, fill="#111418", stroke=INK, sw=1.6, rx=4))
    p.append(text(dx + w / 2, y - 8, "різниця", size=12, color=INK, bold=True))
    # обідок зміни (де об'єкт був і де став) — світиться
    ocx = dx + w * 0.34
    ocy = y + h * 0.52
    p.append(rect(ocx - 13, ocy - 9, 26, 18, fill="none", stroke="#7fd0ff", sw=2.0, rx=3))
    p.append(rect(ocx + 16 - 13, ocy - 9, 26, 18, fill="none", stroke="#7fd0ff", sw=2.0, rx=3))
    p.append(text(dx + w / 2, y + h + 22, "майже все = 0 (чорне)", size=10, color=MUTED))

    render(os.path.join(OUT, "frames-similar.svg"), W, H, *p,
           title="Сусідні кадри — близнюки: різниця майже суцільний нуль")


# ── iframe-pframe: байтова вага кадрів у групі I-P-P-…-I ──────────────────────
# Ідея: стовпчики «вага в байтах»; I — високий, P — низенькі; бітрейт стрибає
# на кожному I.

def fig_iframe_pframe():
    W, H = 720, 300
    p = []
    ox, oy = 70, 250
    aw, ah = 600, 196
    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox - 14, oy - ah - 2, "байтів", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox + aw, oy + 20, "кадри в часі", size=11, color=INK, italic=True))

    seq = ["I", "P", "P", "P", "P", "P", "P", "I", "P", "P", "P", "P", "P", "P"]
    n = len(seq)
    slot = aw / (n + 0.5)
    bw = slot * 0.62
    for i, k in enumerate(seq):
        bx = ox + 6 + i * slot
        if k == "I":
            bh = ah * 0.92
            fill, stroke, col = "#f3c6bf", POS, POS
        else:
            bh = ah * 0.13
            fill, stroke, col = "#cfe0f5", NEG, NEG
        p.append(rect(bx, oy - bh, bw, bh, fill=fill, stroke=stroke, sw=1.4, rx=2))
        p.append(text(bx + bw / 2, oy + 14, k, size=11, color=col, bold=True))

    # підписи
    p.append(text(ox + 6 + 0 * slot + bw / 2, oy - ah * 0.92 - 8, "повний", size=10, color=POS))
    p.append(text(ox + 6 + 7 * slot + bw / 2, oy - ah * 0.92 - 8, "повний", size=10, color=POS))
    p.append(text(ox + 6 + 3.0 * slot, oy - ah * 0.13 - 14, "лише зміна", size=10, color=NEG))

    render(os.path.join(OUT, "iframe-pframe.svg"), W, H, *p,
           title="Група I-P-P-…-I: I важкий, P крихітні")


# ── motion: блок переїхав → вектор руху + залишок ─────────────────────────────
# Ідея: блок 16×16 знайдено в попередньому кадрі зсунутим; зберігаємо вектор
# (+5,+5) і крихітний залишок замість цілого блока.

def fig_motion():
    W, H = 720, 290
    p = []
    w, h = 200, 150
    y = 70
    x1 = 50
    x2 = 330

    # кадр N (опорний)
    p.append(rect(x1, y, w, h, fill="#eaf2fb", stroke=INK, sw=1.6, rx=4))
    p.append(text(x1 + w / 2, y - 8, "кадр N (опорний)", size=12, color=INK, bold=True))
    # сітка блоків
    for gx in range(1, 4):
        p.append(line(x1 + gx * w / 4, y, x1 + gx * w / 4, y + h, color="#c4d6ee", sw=0.8))
    for gy in range(1, 3):
        p.append(line(x1, y + gy * h / 3, x1 + w, y + gy * h / 3, color="#c4d6ee", sw=0.8))
    # цільовий блок у кадрі N
    b1x, b1y = x1 + w * 0.30, y + h * 0.34
    p.append(rect(b1x, b1y, 40, 36, fill="#f3c6bf", stroke=POS, sw=2.0, rx=2))
    p.append(text(b1x + 20, b1y + 22, "16×16", size=9, color=POS, bold=True))

    # кадр N+1
    p.append(rect(x2, y, w, h, fill="#eaf2fb", stroke=INK, sw=1.6, rx=4))
    p.append(text(x2 + w / 2, y - 8, "кадр N+1", size=12, color=INK, bold=True))
    # той самий блок, зсунутий
    b2x, b2y = x2 + w * 0.30 + 34, y + h * 0.34 + 26
    # привид старого положення
    p.append(rect(x2 + w * 0.30, y + h * 0.34, 40, 36, fill="none", stroke="#c0b0ac", sw=1.2, rx=2))
    p.append(rect(b2x, b2y, 40, 36, fill="#f3c6bf", stroke=POS, sw=2.0, rx=2))
    # вектор руху
    p.append(arrow(x2 + w * 0.30 + 20, y + h * 0.34 + 18, b2x + 20, b2y + 18, color=FIELD, sw=2.4))

    # підпис унизу: що зберігаємо
    box, bw, bh = textbox(W / 2, y + h + 44,
                          "зберігаємо:  вектор руху (+5,+5)  +  крихітний залишок",
                          size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK)
    p.append(box)

    render(os.path.join(OUT, "motion.svg"), W, H, *p,
           title="Компенсація руху: блок переїхав — пишемо вектор, не блок")


# ── propagation: помилка в P розмазується, доки I не скине ─────────────────────
# Ідея: ланцюг I-P-P-P…; один P псується завадою, артефакт росте по наступних
# P, аж доки наступний I не перезапише картину чисто.

def fig_propagation():
    W, H = 720, 280
    p = []
    y = 120
    bw, bh = 58, 58
    gap = 78
    x0 = 40
    seq = ["I", "P", "P", "P", "P", "P", "I", "P"]
    bad_from = 2          # індекс, де стався збій
    reset_at = 6          # індекс I, що скидає
    centers = []
    for i, k in enumerate(seq):
        bx = x0 + i * gap
        cx = bx + bw / 2
        centers.append(cx)
        if k == "I":
            fill, stroke, col = "#f3c6bf", POS, POS
        elif bad_from <= i < reset_at:
            # зіпсовані P: тим темніші «квадрати», чим далі від збою
            sev = (i - bad_from + 1) / (reset_at - bad_from)
            g = int(220 - 90 * sev)
            fill = "#%02x%02x%02x" % (g, g, g + 6)
            stroke, col = "#888", INK
        else:
            fill, stroke, col = "#cfe0f5", NEG, NEG
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=stroke, sw=1.6, rx=3))
        p.append(text(cx, y + bh / 2 + 6, k, size=14, color=col, bold=True))
        # стрілка залежності (P спирається на попередній)
        if i > 0:
            p.append(arrow(centers[i - 1] + bw / 2 + 2, y + bh / 2,
                           bx - 2, y + bh / 2, color=MUTED, sw=1.3))

    # позначка збою
    bx_bad = x0 + bad_from * gap
    p.append(text(bx_bad + bw / 2, y - 14, "✦ завада", size=11, color=POS, bold=True))
    p.append(arrow(bx_bad + bw / 2, y - 8, bx_bad + bw / 2, y - 2, color=POS, sw=1.6))

    # дуга «помилка розмазується»
    p.append(text((x0 + bad_from * gap + x0 + (reset_at - 1) * gap) / 2 + bw / 2, y + bh + 30,
                  "артефакт росте по наступних P", size=11, color=INK, bold=True))

    # позначка скидання
    bx_rst = x0 + reset_at * gap
    p.append(text(bx_rst + bw / 2, y - 14, "I скидає чисто", size=11, color=POS, bold=True))
    p.append(arrow(bx_rst + bw / 2, y - 8, bx_rst + bw / 2, y - 2, color=POS, sw=1.6))

    render(os.path.join(OUT, "propagation.svg"), W, H, *p,
           title="Збій у P повзе по ланцюгу, доки I не перезапише картину")


if __name__ == "__main__":
    fig_frames_similar()
    fig_iframe_pframe()
    fig_motion()
    fig_propagation()
    print("OK: figures written to", OUT)
