# -*- coding: utf-8 -*-
"""Фігури для статті «Дерево Меркла»."""
import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_structure():
    """Малює загальну анатомію Дерева Меркла для 4 елементів."""
    w, h = 760, 380
    frags = []

    # Заголовок / Шар даних (найнижчий рівень)
    frags.append(text(380, 25, "Анатомія Дерева Меркла (Merkle Tree)", size=16, bold=True))

    # Рівень даних (Data Blocks)
    d_y = 330
    x_coords = [110, 290, 470, 650]
    data_labels = ["Data 0\n(\"Tx 0\")", "Data 1\n(\"Tx 1\")", "Data 2\n(\"Tx 2\")", "Data 3\n(\"Tx 3\")"]

    for i in range(4):
        b, bw, bh = textbox(x_coords[i], d_y, data_labels[i], size=12, fill="#f8fafc", stroke="#94a3b8")
        frags.append(b)

    # Рівень листків (Leaf Hashes H(0x00 || Data))
    l_y = 230
    leaf_labels = [
        "L₀ = Hash(0x00 || D₀)",
        "L₁ = Hash(0x00 || D₁)",
        "L₂ = Hash(0x00 || D₂)",
        "L₃ = Hash(0x00 || D₃)"
    ]

    for i in range(4):
        b, bw, bh = textbox(x_coords[i], l_y, leaf_labels[i], size=11, fill="#e0f2fe", stroke="#0284c7", bold=True)
        frags.append(b)
        frags.append(arrow(x_coords[i], d_y - 20, x_coords[i], l_y + 18, color="#0284c7"))

    # Рівень внутрішніх вузлів (Internal Hashes H(0x01 || L_L || L_R))
    n_y = 130
    n_coords = [200, 560]
    n_labels = [
        "N₀₁ = Hash(0x01 || L₀ || L₁)",
        "N₂₃ = Hash(0x01 || L₂ || L₃)"
    ]

    for i in range(2):
        b, bw, bh = textbox(n_coords[i], n_y, n_labels[i], size=12, fill="#fef3c7", stroke="#d97706", bold=True)
        frags.append(b)

    # Стрілки від листків до внутрішніх вузлів
    frags.append(arrow(x_coords[0], l_y - 18, n_coords[0] - 30, n_y + 18, color="#d97706"))
    frags.append(arrow(x_coords[1], l_y - 18, n_coords[0] + 30, n_y + 18, color="#d97706"))
    frags.append(arrow(x_coords[2], l_y - 18, n_coords[1] - 30, n_y + 18, color="#d97706"))
    frags.append(arrow(x_coords[3], l_y - 18, n_coords[1] + 30, n_y + 18, color="#d97706"))

    # Рівень кореня (Merkle Root)
    r_y = 55
    r_coord = 380
    r_label = "Merkle Root = Hash(0x01 || N₀₁ || N₂₃)"
    b, bw, bh = textbox(r_coord, r_y, r_label, size=13, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(b)

    # Стрілки до кореня
    frags.append(arrow(n_coords[0], n_y - 18, r_coord - 60, r_y + 18, color="#16a34a"))
    frags.append(arrow(n_coords[1], n_y - 18, r_coord + 60, r_y + 18, color="#16a34a"))

    return render(os.path.join(OUT, "merkle-tree-structure.svg"), w, h, *frags)


def fig_proof_path():
    """Малює шлях доказу підтвердження (Merkle Proof) для конкретного елемента."""
    w, h = 760, 380
    frags = []

    frags.append(text(380, 25, "Шлях аудиторського доказу (Merkle Proof для Data 1)", size=16, bold=True))

    d_y = 330
    x_coords = [110, 290, 470, 650]

    # Данні
    frags.append(textbox(x_coords[0], d_y, "Data 0", size=12, fill="#f1f5f9", stroke="#94a3b8")[0])
    # Перевіряємий елемент
    frags.append(textbox(x_coords[1], d_y, "Data 1\n(Перевіряється)", size=12, fill="#dcfce7", stroke="#16a34a", bold=True)[0])
    frags.append(textbox(x_coords[2], d_y, "Data 2", size=12, fill="#f1f5f9", stroke="#cbd5e1")[0])
    frags.append(textbox(x_coords[3], d_y, "Data 3", size=12, fill="#f1f5f9", stroke="#cbd5e1")[0])

    # Листки
    l_y = 230
    # L0 - Сестринський хеш (входить до Proof!)
    frags.append(textbox(x_coords[0], l_y, "L₀ (Сестра 1: LEFT)", size=12, fill="#fef3c7", stroke="#d97706", bold=True)[0])
    # L1 - Хеш перевіряємого елемента
    frags.append(textbox(x_coords[1], l_y, "L₁ = Hash(0x00||Data 1)", size=12, fill="#dcfce7", stroke="#16a34a", bold=True)[0])
    # L2, L3 - не потрібні для доказу (сірі)
    frags.append(textbox(x_coords[2], l_y, "L₂ (пропущено)", size=11, fill="#f8fafc", stroke="#cbd5e1", color=MUTED)[0])
    frags.append(textbox(x_coords[3], l_y, "L₃ (пропущено)", size=11, fill="#f8fafc", stroke="#cbd5e1", color=MUTED)[0])

    frags.append(arrow(x_coords[1], d_y - 20, x_coords[1], l_y + 18, color="#16a34a"))

    # Внутрішній рівень
    n_y = 130
    n_coords = [200, 560]
    # N01 - обчислюється клієнтом
    frags.append(textbox(n_coords[0], n_y, "N₀₁ = Hash(0x01 || L₀ || L₁)\n[Обчислено клієнтом]", size=12, fill="#e0f2fe", stroke="#0284c7", bold=True)[0])
    # N23 - Сестринський хеш (входить до Proof!)
    frags.append(textbox(n_coords[1], n_y, "N₂₃ (Сестра 2: RIGHT)\n[Надається у Proof]", size=12, fill="#fef3c7", stroke="#d97706", bold=True)[0])

    frags.append(arrow(x_coords[0], l_y - 18, n_coords[0] - 30, n_y + 18, color="#d97706"))
    frags.append(arrow(x_coords[1], l_y - 18, n_coords[0] + 30, n_y + 18, color="#16a34a"))

    # Корінь
    r_y = 55
    r_coord = 380
    frags.append(textbox(r_coord, r_y, "Merkle Root = Hash(0x01 || N₀₁ || N₂₃)\n[Звіряється з очікуваним]", size=12, fill="#dcfce7", stroke="#16a34a", bold=True)[0])

    frags.append(arrow(n_coords[0], n_y - 18, r_coord - 60, r_y + 18, color="#0284c7"))
    frags.append(arrow(n_coords[1], n_y - 18, r_coord + 60, r_y + 18, color="#d97706"))

    return render(os.path.join(OUT, "merkle-proof-path.svg"), w, h, *frags)


def fig_domain_separation():
    """Малює порівняння вразливої схеми та захисту префіксами доменів."""
    w, h = 760, 320
    frags = []

    frags.append(text(380, 25, "Захист від атак другого прообразу (Domain Separation)", size=16, bold=True))

    # Ліва частина — без префіксів (вразливість)
    frags.append(text(190, 60, "Без префіксів (ВРАЗЛИВО)", size=14, color=POS, bold=True))
    frags.append(rect(20, 75, 340, 225, fill="#fff5f5", stroke=POS, sw=1.5))

    frags.append(textbox(190, 100, "Внутрішній вузол: N₁₂ = Hash(L₁ || L₂)", size=11, fill="#ffffff", stroke="#cbd5e1")[0])
    frags.append(textbox(190, 160, "Підроблений листок: Data* = L₁ || L₂", size=11, fill="#fee2e2", stroke=POS, bold=True)[0])
    frags.append(textbox(190, 220, "Hash(Data*) = Hash(L₁ || L₂) = N₁₂", size=11, fill="#fee2e2", stroke=POS, bold=True)[0])
    frags.append(text(190, 275, "⚠ Внутрішній вузол прийнято за листок!", size=11, color=POS, bold=True))

    # Права частина — з префіксами (безпечно)
    frags.append(text(570, 60, "З префіксами 0x00 та 0x01 (БЕЗПЕЧНО)", size=14, color=FIELD, bold=True))
    frags.append(rect(400, 75, 340, 225, fill="#f0fdf4", stroke=FIELD, sw=1.5))

    frags.append(textbox(570, 100, "Вузол: N₁₂ = Hash(0x01 || L₁ || L₂)", size=11, fill="#ffffff", stroke="#cbd5e1")[0])
    frags.append(textbox(570, 160, "Спроба: Data* = L₁ || L₂", size=11, fill="#ffffff", stroke="#cbd5e1")[0])
    frags.append(textbox(570, 220, "Hash(0x00 || Data*) ≠ Hash(0x01 || L₁ || L₂)", size=11, fill="#dcfce7", stroke=FIELD, bold=True)[0])
    frags.append(text(570, 275, "✓ Розділення доменів блокує підробку", size=11, color=FIELD, bold=True))

    return render(os.path.join(OUT, "merkle-domain-separation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_structure()
    fig_proof_path()
    fig_domain_separation()
    print("Фігури успішно згенеровано у ./img/")
