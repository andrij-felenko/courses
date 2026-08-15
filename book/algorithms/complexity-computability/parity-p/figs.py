# -*- coding: utf-8 -*-
"""Фігури для теми «Клас ⊕P (Parity-P)»
(book/algorithms/complexity-computability/parity-p)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURP_F, PURP_S = "#f3f0fd", "#6b46c1"
BLU_F, BLU_S = "#eaf0fd", "#2b6cb0"
GRN_F, GRN_S = "#e9f7ef", "#276749"
RED_F, RED_S = "#fdecea", "#c53030"


def fig_parity_p_hierarchy():
    """Співвідношення класів складності та теорема Тоди: PH ⊆ P^(⊕P) ⊆ PSPACE."""
    W, H = 1040, 590
    cxc = W / 2
    frags = []

    # П'ять вкладених прямокутників (від зовнішнього PSPACE до внутрішнього P)
    frags.append(rect(40, 50, 960, 410, fill="#f8fafc", stroke=MUTED, sw=2, rx=18))
    frags.append(rect(100, 100, 840, 320, fill=PURP_F, stroke=PURP_S, sw=2.4, rx=16))
    frags.append(rect(160, 150, 720, 230, fill="#edf2f7", stroke="#4a5568", sw=2, rx=14))
    frags.append(rect(240, 200, 560, 140, fill=BLU_F, stroke=BLU_S, sw=2.2, rx=12))
    frags.append(rect(370, 245, 300, 65, fill=GRN_F, stroke=GRN_S, sw=2.4, rx=10))

    # Заголовки класів
    frags.append(text(cxc, 80, "PSPACE — поліноміальна пам'ять", size=15, bold=True, color=MUTED))
    frags.append(text(cxc, 128, "P^(⊕P) = P^(#P) — поліноміальний час з оракулом парності ⊕P",
                      size=15, bold=True, color=PURP_S))
    frags.append(text(cxc, 178, "PH — поліноміальна ієрархія (NP ⊆ Σ₂P ⊆ Π₂P ⊆ Σ₃P ⋯)",
                      size=14, bold=True, color="#4a5568"))
    frags.append(text(cxc, 225, "NP — існування свідка (чи > 0)", size=14, bold=True, color=BLU_S))
    frags.append(text(cxc, 282, "P — детермінований поліноміальний час", size=15, bold=True, color=GRN_S))

    # Акцент на теорему Тоди
    frags.append(textbox(cxc, 350, "⊕P-оракул поглинає весь PH за теоремою Тоди (1989)",
                         size=13, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=10)[0])

    # Нижній висновок-підпис
    band, _, _ = textbox(cxc, 515,
                         "Теорема Тоди доводить, що P^(⊕P) містить усю поліноміальну ієрархію PH.\nПитання парності (mod 2) має достатню алгебраїчну силу, щоб згорнути довільну кількість кванторів.",
                         size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=13)
    frags.append(band)

    render(os.path.join(IMG, "parity-p-hierarchy.svg"), W, H, *frags,
           title="Ієрархія класів складності та теорема Тоди")


def fig_valiant_vazirani_isolation():
    """Лема Валіанта–Вазірані: випадкові лінійні обмеження над GF(2) ізолюють розв'язок."""
    W, H = 1140, 560
    frags = []

    # Три етапи: Початковий простір -> Лінійні зрізи GF(2) -> Ізольований розв'язок
    x1, x2, x3 = 210, 570, 930
    y_center = 230

    # 1. Початковий простір розв'язків
    frags.append(textbox(x1, 80, "Початкова формула Φ\n(k розв'язків)", size=15, bold=True,
                         fill=BLU_F, stroke=BLU_S, sw=2.2, pad=12)[0])
    frags.append(rect(x1 - 120, 140, 240, 180, fill="#f7fafc", stroke=MUTED, sw=1.8, rx=12))
    # Малюємо точки розв'язків
    pts = [(-70, -40), (-30, 30), (20, -50), (60, 20), (-10, -10), (40, 50), (-50, 40)]
    for px, py in pts:
        frags.append(circle(x1 + px, y_center + py, 7, fill=RED_S, stroke=INK, sw=1))
    frags.append(text(x1, 350, "Багато розв'язків (парність довільна)", size=13, color=MUTED, bold=True))

    # Стрілка 1 -> 2
    frags.append(arrow(x1 + 135, y_center, x2 - 135, y_center, color=INK, sw=2.2))
    frags.append(text((x1 + x2) / 2, y_center - 20, "+ m лінійних рівнянь", size=13, bold=True, color=PURP_S))
    frags.append(text((x1 + x2) / 2, y_center + 20, "над GF(2)", size=13, bold=True, color=PURP_S))

    # 2. Накладання випадкових лінійних обмежень над GF(2)
    frags.append(textbox(x2, 80, "Система h(x) = 0\n(m ≈ log₂ k рівнянь)", size=15, bold=True,
                         fill=PURP_F, stroke=PURP_S, sw=2.2, pad=12)[0])
    frags.append(rect(x2 - 120, 140, 240, 180, fill="#f7fafc", stroke=MUTED, sw=1.8, rx=12))
    # Малюємо сітку лінійних зрізів
    frags.append(line(x2 - 110, y_center - 60, x2 + 110, y_center + 60, color=PURP_S, sw=2, dash="5 5"))
    frags.append(line(x2 - 100, y_center + 50, x2 + 100, y_center - 50, color=PURP_S, sw=2, dash="5 5"))
    for px, py in pts:
        is_kept = (px == -10 and py == -10)
        frags.append(circle(x2 + px, y_center + py, (8 if is_kept else 5),
                            fill=(GRN_S if is_kept else "#cbd5e0"),
                            stroke=INK, sw=1))
    frags.append(text(x2, 350, "Кожне рівняння відсікає ~50% свідків", size=13, color=MUTED, bold=True))

    # Стрілка 2 -> 3
    frags.append(arrow(x2 + 135, y_center, x3 - 135, y_center, color=INK, sw=2.2))
    frags.append(text((x2 + x3) / 2, y_center - 20, "з ймовірністю ≥ 1/8", size=13, bold=True, color=GRN_S))

    # 3. Ізольований розв'язок
    frags.append(textbox(x3, 80, "Нова формула Φ'\n(РІВНО 1 розв'язок)", size=15, bold=True,
                         fill=GRN_F, stroke=GRN_S, sw=2.4, pad=12)[0])
    frags.append(rect(x3 - 120, 140, 240, 180, fill="#f7fafc", stroke=MUTED, sw=1.8, rx=12))
    frags.append(circle(x3 - 10, y_center - 10, 10, fill=GRN_S, stroke=INK, sw=1.5))
    frags.append(text(x3, 350, "1 розв'язок = НЕПАРНА кількість!", size=13, color=GRN_S, bold=True))

    # Нижній висновок
    band, _, _ = textbox(W / 2, 485,
                         "Лема Валіанта–Вазірані: додавання m випадкових лінійних рівнянь над GF(2) з високою ймовірністю залишає рівно 1 розв'язок.\nОскільки 1 — непарне число, оракул парності ⊕P відрізняє 1 від 0, розв'язуючи задачі існування (NP).",
                         size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=13)
    frags.append(band)

    render(os.path.join(IMG, "valiant-vazirani-isolation.svg"), W, H, *frags,
           title="Лема Валіанта–Вазірані: лінійне ізолювання розв'язку над GF(2)")


if __name__ == "__main__":
    fig_parity_p_hierarchy()
    fig_valiant_vazirani_isolation()
    print("OK:", sorted(os.listdir(IMG)))
