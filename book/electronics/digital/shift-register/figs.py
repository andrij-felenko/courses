# -*- coding: utf-8 -*-
"""Фігури до теми «Зсувний регістр».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def ff(x, y, w, h, top, qlabel, qval=None):
    """Один тригер: прямокутник із входом D зліва, виходом Q справа,
    трикутником такту знизу. top — підпис над тригером, qval — біт усередині."""
    f = [rect(x, y, w, h, fill=FILL, stroke=LINE, sw=2)]
    f.append(text(x + w / 2, y - 8, top, size=12, bold=True, color=MUTED))
    f.append(text(x + 13, y + h / 2 + 4, "D", size=12, bold=True))
    f.append(text(x + w - 13, y + h / 2 + 4, qlabel, size=12, bold=True))
    # трикутник такту біля нижнього краю
    cy = y + h - 11
    f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" stroke="%s" '
             'stroke-width="1.6"/>' % (x + 6, cy - 6, x + 16, cy, x + 6, cy + 6, LINE))
    if qval is not None:
        f.append(text(x + w / 2, y + h / 2 + 6, qval, size=18, bold=True, color=NEG))
    return "".join(f), x + w, x  # фрагмент, правий край (вихід), лівий край (вхід)


# ── 1. Механізм зсуву: ланцюг тригерів, біти крокують по такту ───────────────
def fig_shift_mechanism():
    W, H = 760, 380
    f = [text(W / 2, 28, "Зсув: вихід кожного тригера — вхід наступного", size=16, bold=True)]

    bw, bh, gap = 92, 70, 42
    x0, yT = 132, 86
    bits_now = ["1", "0", "1", "1"]          # стан до фронту: Q3 Q2 Q1 Q0
    rights, lefts = [], []
    for i, b in enumerate(bits_now):
        x = x0 + i * (bw + gap)
        frag, r, l = ff(x, yT, bw, bh, "Q%d" % (3 - i), "Q", b)
        f.append(frag)
        rights.append(r); lefts.append(l)
        if i > 0:
            f.append(arrow(rights[i - 1], yT + bh / 2, lefts[i] , yT + bh / 2, sw=2))

    # вхід даних зліва (новий біт), і «випадання» справа
    f.append(mtext(x0 - 66, yT + bh / 2 - 14, ["новий", "біт"], size=12, bold=True, color=POS))
    f.append(arrow(x0 - 66, yT + bh / 2 + 8, lefts[0], yT + bh / 2 + 8, color=POS, sw=2.2))
    f.append(arrow(rights[-1], yT + bh / 2, rights[-1] + 34, yT + bh / 2, color=MUTED, sw=2))
    f.append(mtext(rights[-1] + 32, yT + bh / 2 - 6, ["випав", "(старий Q0)"], size=11, color=MUTED, anchor="middle"))

    # спільний такт під усіма
    yC = yT + bh + 60
    f.append(line(x0 + 8, yC, rights[-1] - bw + 16, yC, color=LINE, sw=2))
    for i in range(4):
        x = x0 + i * (bw + gap)
        f.append(line(x + 11, yC, x + 11, yT + bh, color=LINE, sw=1.6))
    f.append(text(x0 - 18, yC + 5, "такт", size=12, bold=True, anchor="end"))

    # стан ПІСЛЯ одного фронту, у рядок
    yA = yC + 64
    b, w, h = textbox(W / 2, yA,
                      "Один фронт такту →  усі біти зсунулись на щабель праворуч:\n"
                      "було  Q3Q2Q1Q0 = 1 0 1 1   стало  = (новий) 1 0 1   (старий Q0 — випав)",
                      size=12.5, fill="#eef6ef", stroke=FIELD, pad=12)
    f.append(b)
    return W, H, f


# ── 2. SIPO ↔ PISO: два напрями того самого ланцюга ─────────────────────────
def fig_sipo_piso():
    W, H = 760, 430
    f = [text(W / 2, 28, "Той самий ланцюг, два напрями: SIPO і PISO", size=16, bold=True)]

    bw, bh, gap = 78, 56, 34

    def row(y, bits, title):
        x0 = 196
        rights, lefts = [], []
        for i, b in enumerate(bits):
            x = x0 + i * (bw + gap)
            frag, r, l = ff(x, y, bw, bh, "", "Q", b)
            f.append(frag)
            rights.append(r); lefts.append(l)
            if i > 0:
                f.append(arrow(rights[i - 1], y + bh / 2, lefts[i], y + bh / 2, sw=1.8))
        return x0, rights, lefts

    # SIPO: один вхід зліва (по одному біту), знімаємо всі Q разом (паралельно)
    yS = 78
    f.append(text(40, yS + bh / 2 + 4, "SIPO", size=15, bold=True, color=NEG, anchor="start"))
    f.append(text(40, yS + bh / 2 + 24, "серійно→", size=11, color=MUTED, anchor="start"))
    f.append(text(40, yS + bh / 2 + 40, "паралельно", size=11, color=MUTED, anchor="start"))
    x0, rights, lefts = row(yS, ["b3", "b2", "b1", "b0"], "")
    f.append(text(x0 - 80, yS + bh / 2 - 8, "вхід", size=12, bold=True, color=POS))
    f.append(arrow(x0 - 78, yS + bh / 2 + 6, lefts[0], yS + bh / 2 + 6, color=POS, sw=2.2))
    f.append(text(x0 - 78, yS + bh / 2 + 22, "1 дріт", size=11, color=MUTED, anchor="start"))
    # вісім паралельних виходів угору
    for x in [l for l in lefts] :
        f.append(arrow(x + bw / 2, yS, x + bw / 2, yS - 22, color=FIELD, sw=1.8))
    f.append(text(rights[-1] + 30, yS + bh / 2 + 4, "усі Q\nразом", size=11, bold=True, color=FIELD, anchor="start"))

    # роздільник
    f.append(line(60, 210, W - 40, 210, color=MUTED, sw=1, dash="5 5"))

    # PISO: завантажили все паралельно, висуваємо по одному біту праворуч
    yP = 268
    f.append(text(40, yP + bh / 2 + 4, "PISO", size=15, bold=True, color=NEG, anchor="start"))
    f.append(text(40, yP + bh / 2 + 24, "паралельно→", size=11, color=MUTED, anchor="start"))
    f.append(text(40, yP + bh / 2 + 40, "серійно", size=11, color=MUTED, anchor="start"))
    x0, rights, lefts = row(yP, ["b3", "b2", "b1", "b0"], "")
    # паралельне завантаження зверху
    for x in lefts:
        f.append(arrow(x + bw / 2, yP - 22, x + bw / 2, yP, color=POS, sw=1.8))
    f.append(text(x0 - 96, yP - 14, "паралельне\nзавантаження", size=11, bold=True, color=POS, anchor="start"))
    # один серійний вихід праворуч
    f.append(arrow(rights[-1], yP + bh / 2, rights[-1] + 64, yP + bh / 2, color=FIELD, sw=2.2))
    f.append(text(rights[-1] + 70, yP + bh / 2 - 8, "вихід", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(rights[-1] + 70, yP + bh / 2 + 10, "1 дріт", size=11, color=MUTED, anchor="start"))

    b, w, h = textbox(W / 2, 408,
                      "SIPO збирає вісім входів у байт; PISO розкладає байт у вісім входів — дзеркала.",
                      size=12.5, fill="#eef6ef", stroke=FIELD, pad=11)
    f.append(b)
    return W, H, f


# ── 3. Вихідний латч: подвійний буфер, виходи не мерехтять ───────────────────
def fig_output_latch():
    W, H = 760, 390
    f = [text(W / 2, 28, "Вихідний латч: засуваємо тихо, показуємо одним рухом", size=16, bold=True)]

    bw, bh, gap = 86, 54, 24
    x0 = 150

    # верхній ряд — зсувний регістр (приймає біти)
    yR = 92
    f.append(text(x0 - 22, yR + bh / 2 + 4, "зсувний\nрегістр", size=11, bold=True, anchor="end", color=MUTED))
    sr_x = []
    for i in range(4):
        x = x0 + i * (bw + gap)
        sr_x.append(x)
        frag, r, l = ff(x, yR, bw, bh, "", "", ["b3", "b2", "b1", "b0"][i])
        f.append(frag)
        if i > 0:
            f.append(arrow(sr_x[i - 1] + bw, yR + bh / 2, x, yR + bh / 2, sw=1.6))
    f.append(text(x0 - 86, yR + bh / 2 + 4, "SER", size=12, bold=True, color=POS))
    f.append(arrow(x0 - 80, yR + bh / 2, x0, yR + bh / 2, color=POS, sw=2))

    # нижній ряд — вихідний латч (тримає показ)
    yL = yR + bh + 70
    f.append(text(x0 - 22, yL + bh / 2 + 4, "вихідний\nлатч", size=11, bold=True, anchor="end", color=MUTED))
    for i in range(4):
        x = x0 + i * (bw + gap)
        f.append(rect(x, yL, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2))
        f.append(text(x + bw / 2, yL + bh / 2 + 5, "·", size=18, color=MUTED))
        # копіювання згори вниз — пунктир із стрілкою
        f.append(arrow(x + bw / 2, yR + bh, x + bw / 2, yL, color=MUTED, sw=1.6))
        # виходи вниз
        f.append(arrow(x + bw / 2, yL + bh, x + bw / 2, yL + bh + 22, color=FIELD, sw=1.8))
        f.append(text(x + bw / 2, yL + bh + 38, ["Q3", "Q2", "Q1", "Q0"][i], size=11, bold=True, color=FIELD))

    # два РІЗНІ такти
    f.append(text(x0 + 3.6 * (bw + gap), yR + bh / 2 - 6, "SRCLK", size=12, bold=True, anchor="start", color=NEG))
    f.append(text(x0 + 3.6 * (bw + gap), yR + bh / 2 + 12, "(засув)", size=10, anchor="start", color=MUTED))
    f.append(text(x0 + 3.6 * (bw + gap), yL + bh / 2 - 6, "RCLK", size=12, bold=True, anchor="start", color=POS))
    f.append(text(x0 + 3.6 * (bw + gap), yL + bh / 2 + 12, "(показ)", size=10, anchor="start", color=MUTED))

    b, w, h = textbox(W / 2, H - 26,
                      "SRCLK тихо набиває верхній ряд; виходи стоять. Один RCLK копіює рядок униз — і весь байт з'являється разом.",
                      size=12, fill=FILL, stroke=LINE, pad=11)
    f.append(b)
    return W, H, f


# ── 4. Часова діаграма: 4 фронти SRCLK набивають байт, RCLK показує ──────────
def fig_waveform():
    W, H = 760, 410
    f = [text(W / 2, 26, "Часова діаграма: засув по одному, показ — разом", size=16, bold=True)]

    left = 120
    right = W - 40
    span = right - left
    n = 5                      # 4 фронти SRCLK + 1 RCLK
    dt = span / (n + 1)
    hi, lo = 0, 26             # відносні рівні (менше y = вище)

    def wave(y, label, edges, color=INK):
        """Малює прямокутний сигнал: edges — список x, де фронт ↑ (потім сам ↓)."""
        f.append(text(left - 14, y - lo / 2 - 2, label, size=12, bold=True, anchor="end", color=color))
        f.append(line(left - 6, y, left - 6, y - lo, color=MUTED, sw=1))
        pts = [(left, y)]
        x = left
        for ex in edges:
            pts.append((ex, y)); pts.append((ex, y - lo))           # ↑
            pts.append((ex + dt * 0.42, y - lo)); pts.append((ex + dt * 0.42, y))  # ↓
        pts.append((right, y))
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, color))

    edges = [left + dt * (i + 1) for i in range(4)]
    yclk = 86
    wave(yclk, "SRCLK", edges, color=NEG)
    for i, ex in enumerate(edges):
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                 % (ex - 5, yclk - lo - 6, ex + 5, yclk - lo - 6, ex, yclk - lo + 2, POS))

    # SER: біти, які виставляємо перед кожним фронтом (старший першим): 1 0 1 1
    serbits = [1, 0, 1, 1]
    yser = 168
    f.append(text(left - 14, yser - lo / 2 - 2, "SER", size=12, bold=True, anchor="end"))
    f.append(line(left - 6, yser, left - 6, yser - lo, color=MUTED, sw=1))
    pts = [(left, yser if serbits[0] == 0 else yser - lo)]
    for i in range(4):
        x1 = left + dt * (i + 0.55)
        x2 = left + dt * (i + 1.55)
        lvl = yser - lo if serbits[i] else yser
        pts.append((x1, pts[-1][1])); pts.append((x1, lvl)); pts.append((x2, lvl))
    pts.append((right, pts[-1][1]))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, INK))
    for i in range(4):
        f.append(text(left + dt * (i + 1), yser + 18, str(serbits[i]), size=12, bold=True, color=MUTED))

    # RCLK: один фронт у кінці
    rclk_x = left + dt * 5
    yrc = 250
    wave(yrc, "RCLK", [rclk_x], color=POS)

    # Виходи Q: тримають старе, стрибають разом по RCLK
    yq = 332
    f.append(text(left - 14, yq - lo / 2 - 2, "Q0…Q7", size=12, bold=True, anchor="end", color=FIELD))
    f.append(line(left - 6, yq, left - 6, yq - lo, color=MUTED, sw=1))
    f.append(line(left, yq - lo / 2, rclk_x, yq - lo / 2, color=FIELD, sw=2, dash="6 4"))
    f.append(text((left + rclk_x) / 2, yq - lo / 2 - 8, "старе значення (стоїть)", size=11, color=MUTED))
    f.append(line(rclk_x, yq - lo / 2, rclk_x, yq - lo, color=FIELD, sw=2))
    f.append(line(rclk_x, yq - lo, right, yq - lo, color=FIELD, sw=2))
    f.append(text((rclk_x + right) / 2, yq - lo - 8, "новий байт 1011", size=11, bold=True, color=FIELD))

    # вертикальні гайдлайни через усі фронти
    for ex in edges + [rclk_x]:
        f.append(line(ex, 70, ex, 350, color="#dfe6ee", sw=1, dash="3 5"))

    b, w, h = textbox(W / 2, H - 24,
                      "Чотири фронти SRCLK заводять SER-біти (старший першим), виходи мовчать; один RCLK — і байт виходить разом.",
                      size=11.5, fill="#eef6ef", stroke=FIELD, pad=10)
    f.append(b)
    return W, H, f


def main():
    jobs = [
        ("shift-mechanism.svg", fig_shift_mechanism),
        ("sipo-piso.svg", fig_sipo_piso),
        ("output-latch.svg", fig_output_latch),
        ("waveform.svg", fig_waveform),
    ]
    for name, fn in jobs:
        W, H, frags = fn()
        render(os.path.join(IMG, name), W, H, *frags)
        print("wrote", name)


if __name__ == "__main__":
    main()
