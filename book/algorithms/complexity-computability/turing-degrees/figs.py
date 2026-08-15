# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig1_lattice():
    """Семілатисна структура ступенів Тюринга (upper semilattice of Turing degrees)."""
    w, h = 640, 480
    frags = []

    frags.append(rect(20, 20, 600, 440, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    # Nodes (Degrees)
    # 0 (bottom)
    b0, w0, h0 = textbox(320, 420, "0 (Ступінь обчислюваних множин)\n(A ≡_T ∅)", size=12, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(b0)

    # Intermediate non-c.e. and c.e. degrees
    # Kleene-Post incomparable degrees a and b
    ba, wa, ha = textbox(160, 280, "Ступінь a\n(Непорівнянний з b)\na ≰_T b", size=12, fill="#f4f6f8", stroke=LINE, sw=1.5)
    frags.append(ba)

    bb, wb, hb = textbox(480, 280, "Ступінь b\n(Непорівнянний з a)\nb ≰_T a", size=12, fill="#f4f6f8", stroke=LINE, sw=1.5)
    frags.append(bb)

    # Intermediate c.e. degree d (Friedberg-Muchnik)
    bd, wd, hd = textbox(320, 270, "Проміжний р.п. ступінь d\n0 <_T d <_T 0'", size=12, fill="#eafaf1", stroke=FIELD, sw=2)
    frags.append(bd)

    # Join a v b
    bjoin, wj, hj = textbox(210, 160, "Верхня межа a ∨ b\ndeg(A ⊕ B)", size=12, fill="#f4f6f8", stroke=LINE, sw=1.5)
    frags.append(bjoin)

    # 0' (Halting Problem degree)
    b1, w1, h1 = textbox(430, 160, "0' (Ступінь проблеми зупинки K)\n(Найвищий р.п. ступінь)", size=12, fill="#fdecea", stroke=POS, sw=2)
    frags.append(b1)

    # 0'' (Second Jump)
    b2, w2, h2 = textbox(320, 60, "0'' (Другий стрибок Тюринга K'')\n(Складність Fin: Σ_2^0-повна)", size=12, fill="#f4f6f8", stroke=LINE, sw=1.5)
    frags.append(b2)

    # Connections / Ordering lines (arrows pointing upwards)
    frags.append(arrow(320, 395, 160, 305, color=MUTED, sw=1.5))
    frags.append(arrow(320, 395, 480, 305, color=MUTED, sw=1.5))
    frags.append(arrow(320, 395, 320, 295, color=FIELD, sw=2))

    frags.append(arrow(160, 255, 210, 185, color=MUTED, sw=1.5))
    frags.append(arrow(480, 255, 210, 185, color=MUTED, sw=1.5))

    frags.append(arrow(160, 255, 430, 185, color=MUTED, sw=1.5))
    frags.append(arrow(480, 255, 430, 185, color=MUTED, sw=1.5))
    frags.append(arrow(320, 245, 430, 185, color=FIELD, sw=2))

    frags.append(arrow(210, 135, 320, 85, color=MUTED, sw=1.5))
    frags.append(arrow(430, 135, 320, 85, color=POS, sw=2))

    render(os.path.join(IMG_DIR, "turing-degrees-lattice.svg"), w, h, *frags, title="Верхня напівґратка ступенів Тюринга D_T")


def fig2_oracle_machine():
    """Архітектура оракульної машини Тюринга (Oracle Turing Machine)."""
    w, h = 660, 420
    frags = []

    frags.append(rect(10, 10, 640, 400, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    # Work Tape (Top left)
    frags.append(rect(30, 60, 320, 60, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(190, 80, "Робоча стрічка M", size=13, bold=True))
    frags.append(text(190, 105, "[ ... | 1 | 0 | 1 | 1 | 0 | ... ]", size=12, color=MUTED))

    # Control Unit (Middle left)
    bcu, wcu, hcu = textbox(190, 200, "Управляючий автомат M\nСтан q_in -> обчислення -> q_out", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(bcu)

    # Query Tape (Bottom left)
    frags.append(rect(30, 300, 320, 60, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(190, 320, "Стрічка запиту до оракула", size=13, bold=True))
    frags.append(text(190, 345, "Запис елемента x у двійковому коді", size=12, color=MUTED))

    # Arrows control <-> tapes
    frags.append(arrow(190, 170, 190, 120, color=NEG, sw=1.5))
    frags.append(arrow(190, 230, 190, 300, color=NEG, sw=1.5))

    # Oracle Box (Right)
    boracle, wo, ho = textbox(520, 200, "Зовнішній оракул B\n(Характеристична множина B)\nМиттєва відповідь за 1 крок", size=13, fill="#eafaf1", stroke=FIELD, sw=2)
    frags.append(boracle)

    # Query & Response Arrows
    frags.append(arrow(350, 310, 450, 240, color=FIELD, sw=2))
    frags.append(text(400, 290, "Запит: 'Чи x ∈ B?'", size=12, color=FIELD, bold=True))

    frags.append(arrow(450, 170, 290, 200, color=POS, sw=2))
    frags.append(text(400, 165, "Відповідь: ТАК (1) / НІ (0)", size=12, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "oracle-turing-machine.svg"), w, h, *frags, title="Архітектура оракульної машини Тюринга M^B")


def fig3_jump_hierarchy():
    """Стрибок Тюринга та зв'язок з арифметичною ієрархією."""
    w, h = 680, 420
    frags = []

    frags.append(rect(10, 10, 660, 400, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    # Levels from left to right or bottom to top
    # Level 0: 0 (Computable)
    b0, w0, h0 = textbox(110, 220, "Ступінь 0\n(Обчислювані множини)\nΔ_1^0", size=12, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(b0)

    # Level 1: 0' (Halting)
    b1, w1, h1 = textbox(270, 220, "Ступінь 0'\n(Проблема зупинки K)\nΣ_1^0-повні множини", size=12, fill="#fdecea", stroke=POS, sw=2)
    frags.append(b1)

    # Level 2: 0'' (Fin)
    b2, w2, h2 = textbox(440, 220, "Ступінь 0''\n(Множина Fin)\nΣ_2^0-повні множини", size=12, fill="#eafaf1", stroke=FIELD, sw=2)
    frags.append(b2)

    # Level 3: 0''' (Cof)
    b3, w3, h3 = textbox(595, 220, "Ступінь 0'''\n(Множина Cof)\nΣ_3^0-повні множини", size=12, fill="#f4f6f8", stroke=LINE, sw=1.5)
    frags.append(b3)

    # Jump arrows
    frags.append(arrow(165, 220, 200, 220, color=POS, sw=2))
    frags.append(text(182, 205, "Стрибок A'", size=11, color=POS, bold=True))

    frags.append(arrow(335, 220, 370, 220, color=POS, sw=2))
    frags.append(text(352, 205, "Стрибок A''", size=11, color=POS, bold=True))

    frags.append(arrow(505, 220, 530, 220, color=POS, sw=2))
    frags.append(text(517, 205, "Стрибок A'''", size=11, color=POS, bold=True))

    # Upper box: Post's theorem correspondence
    frags.append(rect(30, 60, 620, 90, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(340, 85, "Теорема Поста про арифметичну ієрархію", size=13, bold=True))
    frags.append(text(340, 110, "Множина A ∈ Σ_{n+1}^0 ⇔ A є р.п. відносно оракула 0^{(n)}", size=12, color=INK))
    frags.append(text(340, 130, "Кожен стрибок піднімає складність опису на один квантор", size=11, color=MUTED, italic=True))

    # Lower box: Friedberg Jump Inversion
    frags.append(rect(30, 310, 620, 80, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(340, 335, "Теорема Фрідберга про обернення стрибка", size=13, bold=True))
    frags.append(text(340, 360, "Для будь-якого ступеня b ≥ 0' існує ступінь a такий, що a' = b", size=12, color=INK))

    render(os.path.join(IMG_DIR, "turing-jump-hierarchy.svg"), w, h, *frags, title="Ієрархія стрибків Тюринга та Теорема Поста")


if __name__ == "__main__":
    fig1_lattice()
    fig2_oracle_machine()
    fig3_jump_hierarchy()
    print("Figures generated successfully.")
