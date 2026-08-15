# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Теорема інваріантності (Invariance Theorem) ───────────────────────
def fig_invariance_theorem():
    W, H = 820, 320
    p = []

    # Тло та секції для двох машин
    p.append(rect(40, 40, 350, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(rect(430, 40, 350, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Машина 1
    p.append(text(215, 68, "Модель U₁ (мова 1)", size=15, bold=True, color=INK))
    b_p1, w_p1, _ = textbox(130, 130, "програма p₁\n(|p₁| = K₁(x))", size=12.5, fill="#e2e8f0", stroke=MUTED)
    p.append(b_p1)

    p.append(rect(220, 105, 150, 50, fill="#dbeafe", stroke=NEG, sw=1.5, rx=6))
    p.append(mtext(295, 126, ["Інтерпретатор U₁", "обчислює p₁"], size=12, color=NEG, bold=True))
    p.append(arrow(130 + w_p1 / 2 + 2, 130, 218, 130, color=NEG, sw=1.5))

    b_out1, w_out1, _ = textbox(215, 225, "Вихідний рядок x", size=13, fill="#dcfce7", stroke=FIELD, bold=True)
    p.append(arrow(295, 157, 215 + w_out1 / 3, 203, color=FIELD, sw=1.8))
    p.append(b_out1)

    # Машина 2
    p.append(text(605, 68, "Модель U₂ (мова 2)", size=15, bold=True, color=INK))

    # Комбінована програма для U2: транслятор c12 + p1
    p.append(rect(455, 105, 120, 50, fill="#fef3c7", stroke=POS, sw=1.5, rx=6))
    p.append(mtext(515, 126, ["Транслятор T₁₂", "довжина c"], size=11.5, color=POS, bold=True))

    p.append(rect(580, 105, 75, 50, fill="#e2e8f0", stroke=MUTED, sw=1.5, rx=6))
    p.append(mtext(617, 126, ["код p₁"], size=12, color=INK))

    p.append(text(575, 88, "програма p₂ = T₁₂ + p₁", size=12, bold=True, color=INK))

    p.append(rect(680, 105, 85, 50, fill="#dbeafe", stroke=NEG, sw=1.5, rx=6))
    p.append(mtext(722, 126, ["Модель U₂"], size=12, color=NEG, bold=True))

    p.append(arrow(657, 130, 678, 130, color=NEG, sw=1.5))

    b_out2, w_out2, _ = textbox(605, 225, "Вихідний рядок x", size=13, fill="#dcfce7", stroke=FIELD, bold=True)
    p.append(arrow(722, 157, 605 + w_out2 / 3, 203, color=FIELD, sw=1.8))
    p.append(b_out2)

    # Пояснення константи c
    p.append(rect(230, 280, 360, 32, fill="#fff7ed", stroke=POS, sw=1.2, rx=4))
    p.append(text(410, 301, "K₂(x) ≤ K₁(x) + c, де c = |T₁₂| = O(1)", size=13, bold=True, color=POS))

    render(os.path.join(OUT, "invariance-theorem.svg"), W, H, *p,
           title="Теорема інваріантності: незалежність складності від вибору універсальної машини")


# ── Фіг. 2: Стиснювані та випадкові рядки (Compressible vs Random) ────────────
def fig_compressible_vs_random():
    W, H = 820, 330
    p = []

    # Верхній блок: регулярний рядок
    p.append(rect(40, 35, 740, 125, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(190, 62, "Регулярний рядок A (N = 100 біт):", size=13, bold=True, color=INK))
    p.append(rect(60, 75, 280, 30, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(200, 95, "01010101010101...0101", size=12, color=NEG, bold=True))

    b_progA, _, _ = textbox(560, 95, "Коротка програма (20 біт):\nprint(\"01\" * 50)", size=12, fill="#dcfce7", stroke=FIELD, bold=True)
    p.append(arrow(345, 95, 450, 95, color=FIELD, sw=1.8))

    p.append(text(200, 142, "K(A) ≪ N  (висока стиснюваність, низька складність)", size=12, bold=True, color=FIELD))

    # Нижній блок: випадковий рядок
    p.append(rect(40, 175, 740, 135, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(190, 202, "Випадковий рядок B (N = 100 біт):", size=13, bold=True, color=INK))
    p.append(rect(60, 215, 280, 30, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(200, 235, "11010010110001...0110", size=12, color=POS, bold=True))

    b_progB, _, _ = textbox(560, 235, "Найкоротша програма (≥100 біт):\nprint(\"1101001011...\")", size=12, fill="#fee2e2", stroke=POS, bold=True)
    p.append(arrow(345, 235, 430, 235, color=POS, sw=1.8))

    p.append(text(200, 292, "K(B) ≈ N  (нестиснюваний рядок, алгоритмічна випадковість)", size=12, bold=True, color=POS))

    render(os.path.join(OUT, "compressible-vs-random.svg"), W, H, *p,
           title="Порівняння стиснюваного регулярного рядка та несжимаємого випадкового рядка")


# ── Фіг. 3: Метрика NCD та кластеризація (NCD Clustering) ──────────────────────
def fig_ncd_clustering():
    W, H = 820, 330
    p = []

    # Блок обчислення спільної інформації через стиснення
    p.append(rect(30, 35, 370, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(215, 62, "Перекриття інформації C(xy)", size=14, bold=True, color=INK))

    p.append(circle(165, 135, 55, fill="#dbeafe", stroke=NEG, sw=1.5))
    p.append(text(142, 135, "Об'єкт x\nC(x)", size=11.5, bold=True, color=NEG))

    p.append(circle(265, 135, 55, fill="#fef3c7", stroke=POS, sw=1.5))
    p.append(text(288, 135, "Об'єкт y\nC(y)", size=11.5, bold=True, color=POS))

    p.append(text(215, 135, "Спільний\nконтекст", size=10, bold=True, color=FIELD))

    b_formula, _, _ = textbox(215, 240, "NCD(x,y) = [C(xy) - min(C(x), C(y))]\n/ max(C(x), C(y))", size=11, fill="#ffffff", stroke=INK, bold=True)
    p.append(b_formula)

    # Дерево ієрархічної кластеризації за NCD
    p.append(rect(420, 35, 370, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(605, 62, "Ієрархічне дерево подібності", size=14, bold=True, color=INK))

    # Дендрограма
    p.append(line(490, 100, 490, 190, color=MUTED, sw=1.5))
    p.append(text(490, 215, "Текст A (UA)", size=11, bold=True, color=INK))

    p.append(line(560, 100, 560, 190, color=MUTED, sw=1.5))
    p.append(text(560, 215, "Текст B (UA)", size=11, bold=True, color=INK))

    p.append(line(490, 150, 560, 150, color=FIELD, sw=2.0))
    p.append(line(525, 150, 525, 100, color=FIELD, sw=2.0))
    p.append(text(525, 138, "NCD = 0.12", size=10, bold=True, color=FIELD))

    p.append(line(720, 100, 720, 190, color=MUTED, sw=1.5))
    p.append(text(720, 215, "Код C (C++)", size=11, bold=True, color=INK))

    p.append(line(525, 100, 720, 100, color=POS, sw=2.0))
    p.append(text(622, 88, "NCD = 0.84", size=10, bold=True, color=POS))

    p.append(text(605, 265, "Мала NCD ⇔ Близька алгоритмічна природа", size=12, bold=True, color=FIELD))

    render(os.path.join(OUT, "ncd-clustering.svg"), W, H, *p,
           title="Обчислення NCD через стиснення та побудова дерева подібності об'єктів")


if __name__ == "__main__":
    fig_invariance_theorem()
    fig_compressible_vs_random()
    fig_ncd_clustering()
    print("All figures generated successfully.")
