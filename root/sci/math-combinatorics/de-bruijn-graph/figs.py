# -*- coding: utf-8 -*-
"""Фігури для теми «Граф де Брейнена» (book/algorithms/complexity-computability/de-bruijn-graph)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def svg_path(d, fill="none", stroke=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def fig_debruijn_graph_b23():
    """fig1-debruijn-graph-b23.svg: Топологія орієнтованого графа де Брейнена B(2, 3)."""
    W, H = 880, 520
    frags = []

    # Рамка та заголовок
    frags.append(rect(10, 10, 860, 500, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Орієнтований граф де Брейнена B(2, 3) над алфавітом {0, 1}", size=16, bold=True, color="#1e293b"))
    frags.append(text(440, 58, "Вершини = префікси/суфікси довжиною 2, Ребра = слова довжиною 3 (зсув бітів)", size=12, italic=True, color="#475569"))

    v_pos = {
        "00": (240, 150),
        "01": (640, 150),
        "10": (240, 330),
        "11": (640, 330)
    }

    # Малювання вершин
    for v, (x, y) in v_pos.items():
        frags.append(circle(x, y, 32, fill=BLUE_F, stroke=BLUE_S, sw=2.5))
        frags.append(text(x, y + 5, v, size=18, bold=True, color=BLUE_S))

    # Петлі (self-loops)
    frags.append(svg_path("M 215,135 C 160,100 160,200 212,160", fill="none", stroke=TEAL_S, sw=2))
    b1, _, _ = textbox(135, 140, "000", size=11, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b1)

    frags.append(svg_path("M 665,345 C 720,380 720,280 668,320", fill="none", stroke=TEAL_S, sw=2))
    b2, _, _ = textbox(745, 330, "111", size=11, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b2)

    # Ребра між вершинами
    # 00 -> 01
    frags.append(arrow(275, 140, 605, 140, color=AMBER_S, sw=2))
    b3, _, _ = textbox(440, 125, "001 (зсув 00→01)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b3)

    # 01 -> 10
    frags.append(arrow(618, 168, 262, 312, color=PURPLE_S, sw=2))
    b4, _, _ = textbox(470, 225, "010 (зсув 01→10)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b4)

    # 10 -> 01
    frags.append(arrow(262, 312, 618, 168, color=GREEN_S, sw=2))
    b5, _, _ = textbox(410, 255, "101 (зсув 10→01)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b5)

    # 01 -> 11
    frags.append(arrow(640, 185, 640, 295, color=AMBER_S, sw=2))
    b6, _, _ = textbox(705, 240, "011", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b6)

    # 11 -> 10
    frags.append(arrow(605, 340, 275, 340, color=PURPLE_S, sw=2))
    b7, _, _ = textbox(440, 360, "110 (зсув 11→10)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b7)

    # 10 -> 00
    frags.append(arrow(240, 295, 240, 185, color=GREEN_S, sw=2))
    b8, _, _ = textbox(175, 240, "100", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b8)

    # Пояснювальний блок параметрів
    info_str = "Властивості B(2, 3):\n• Кількість вершин |V| = 2³⁻¹ = 4\n• Кількість ребер |E| = 2³ = 8\n• Вхідна/вихідна ступінь d = 2\n• Ейлерів цикл → Послідовність де Брейнена довжиною 2³ = 8 бітів: 00011101"
    b_info, _, _ = textbox(440, 450, info_str, size=11, fill="#f1f5f9", stroke="#475569")
    frags.append(b_info)

    render(os.path.join(IMG, "fig1-debruijn-graph-b23.svg"), W, H, *frags)


def fig_kmer_assembly_dna():
    """fig2-kmer-assembly-dna.svg: Пайплайн De Novo складання геному на графі де Брейнена."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Складання ДНК-послідовностей (De Novo Assembly) через k-мери", size=16, bold=True, color="#1e293b"))

    # Блок 1: Вхідні зчитування (Reads)
    b_step1, _, _ = textbox(150, 80, "1. Сирі зчитування (Reads, k=4)\n'ATGC', 'TGCC', 'GCCA'", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_step1)

    # Стрілка 1->2
    frags.append(arrow(270, 80, 330, 80, color=BLUE_S, sw=2))

    # Блок 2: Розбиття на (k-1)-мери (Вершини) та k-мери (Ребра)
    b_step2, _, _ = textbox(480, 80, "2. Вершини (3-мери): 'ATG', 'TGC', 'GCC', 'CCA'\nРебра (4-мери): перекриття довжиною k-1=3 білки", size=12, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_step2)

    # Стрілка 2->3
    frags.append(arrow(480, 125, 480, 160, color=TEAL_S, sw=2))

    # Блок 3: Побудова орієнтованого графа де Брейнена (Посередині)
    frags.append(rect(40, 170, 800, 160, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 190, "3. Граф де Брейнена: Вершини (3-мери) та спрямовані ребра (4-мери)", size=13, bold=True, color="#334155"))

    # Вершини графа ДНК: ATG, TGC, GCC, CCA
    dna_v = ["ATG", "TGC", "GCC", "CCA"]
    v_xs = [120, 330, 550, 760]
    for x, lbl in zip(v_xs, dna_v):
        b, _, _ = textbox(x, 240, lbl, size=14, bold=True, fill=AMBER_F, stroke=AMBER_S)
        frags.append(b)

    # Ребра графа
    frags.append(arrow(160, 240, 290, 240, color=GREEN_S, sw=2.5))
    b_e1, _, _ = textbox(225, 220, "ATGC", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_e1)

    frags.append(arrow(370, 240, 510, 240, color=GREEN_S, sw=2.5))
    b_e2, _, _ = textbox(440, 220, "TGCC", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_e2)

    frags.append(arrow(590, 240, 720, 240, color=GREEN_S, sw=2.5))
    b_e3, _, _ = textbox(655, 220, "GCCA", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_e3)

    # Пояснення відновленого Ейлерового шляху під графом
    frags.append(text(440, 295, "Ейлерів шлях: ATG → TGC → GCC → CCA (відвідує кожне ребро-4-мер рівно один раз)", size=12, italic=True, color=GREEN_S))

    # Стрілка до фінального результату
    frags.append(arrow(440, 330, 440, 360, color=GREEN_S, sw=2))

    # Блок 4: Відновлений геном (Результат)
    b_step4, _, _ = textbox(440, 385, "4. Відновлений геном (Контиг): 'ATGCCA' (довжина N = 6 нуклеотидів)", size=13, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_step4)

    render(os.path.join(IMG, "fig2-kmer-assembly-dna.svg"), W, H, *frags)


def fig_eulerian_hamiltonian_duality():
    """fig3-eulerian-hamiltonian-duality.svg: Двоїстість Ейлерового шляху B(k, n-1) та Гамільтонового шляху B(k, n)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Двоїстість лінійного графа: Ейлерів цикл у B(k, n-1) ≡ Гамільтонів цикл у B(k, n)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: B(2, 2) та Ейлерів цикл
    frags.append(rect(30, 60, 390, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Граф B(2, 2) [k=2, n=2]", size=14, bold=True, color=BLUE_S))
    frags.append(text(225, 105, "Вершини = 1 біт ('0', '1'), Ребра = 2 біти ('00', '01', '10', '11')", size=11, italic=True, color="#475569"))

    # Вершини B(2, 2): 0 та 1
    b_v0, _, _ = textbox(130, 180, "0", size=16, bold=True, fill="#ffffff", stroke=BLUE_S)
    b_v1, _, _ = textbox(320, 180, "1", size=16, bold=True, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_v0)
    frags.append(b_v1)

    # Ребра в B(2, 2)
    frags.append(arrow(160, 170, 290, 170, color=AMBER_S, sw=2))
    frags.append(text(225, 155, "Ребро '01'", size=11, bold=True, color=AMBER_S))

    frags.append(arrow(290, 190, 160, 190, color=PURPLE_S, sw=2))
    frags.append(text(225, 205, "Ребро '10'", size=11, bold=True, color=PURPLE_S))

    # Петлі
    frags.append(svg_path("M 115,165 C 70,140 70,220 112,190", fill="none", stroke=TEAL_S, sw=2))
    frags.append(text(65, 180, "00", size=11, bold=True, color=TEAL_S))

    frags.append(svg_path("M 335,165 C 380,140 380,220 338,190", fill="none", stroke=GREEN_S, sw=2))
    frags.append(text(385, 180, "11", size=11, bold=True, color=GREEN_S))

    b_left_note, _, _ = textbox(225, 295, "Задача: Знайти Ейлерів цикл\n(пройти кожне з 4-х ребер по 1 разу).\nОбчислювально ПРОСТО: O(|E|) = O(kⁿ⁻¹)", size=11, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_left_note)

    # Стрілка трансформації L(G)
    frags.append(arrow(430, 220, 460, 220, color="#475569", sw=2))
    frags.append(text(445, 200, "L(G)", size=12, bold=True, color="#475569"))

    # Права частина: B(2, 3) та Гамільтонів цикл
    frags.append(rect(470, 60, 380, 330, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(660, 85, "Граф B(2, 3) [k=2, n=3]", size=14, bold=True, color=PURPLE_S))
    frags.append(text(660, 105, "Ребра B(2, 2) стають вершинами в B(2, 3)", size=11, italic=True, color="#475569"))

    # 4 Вершини B(2, 3): 00, 01, 10, 11
    b_w00, _, _ = textbox(550, 160, "00", size=13, bold=True, fill=TEAL_F, stroke=TEAL_S)
    b_w01, _, _ = textbox(770, 160, "01", size=13, bold=True, fill=AMBER_F, stroke=AMBER_S)
    b_w10, _, _ = textbox(550, 240, "10", size=13, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    b_w11, _, _ = textbox(770, 240, "11", size=13, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_w00)
    frags.append(b_w01)
    frags.append(b_w10)
    frags.append(b_w11)

    # Гамільтонів шлях (червоні стрілки)
    frags.append(arrow(580, 160, 740, 160, color=RED_S, sw=2))
    frags.append(arrow(770, 180, 580, 240, color=RED_S, sw=2))
    frags.append(arrow(580, 240, 740, 240, color=RED_S, sw=2))
    frags.append(arrow(770, 240, 580, 160, color=RED_S, sw=2))

    b_right_note, _, _ = textbox(660, 310, "Задача: Знайти Гамільтонів цикл\n(пройти кожну з 4-х вершин по 1 разу).\nNP-повна у загальному випадку, але завдяки\nдвоїстісті з B(2,2) розв'язується за O(kⁿ)!", size=11, fill="#ffffff", stroke=PURPLE_S)
    frags.append(b_right_note)

    render(os.path.join(IMG, "fig3-eulerian-hamiltonian-duality.svg"), W, H, *frags)


def fig_shift_register_hardware():
    """fig4-shift-register-hardware.svg: Схема зсувного регістра з зворотним зв'язком (FSR) для генерації де Брейнена."""
    W, H = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Апаратна схема генерації послідовностей де Брейнена на зсувному регістрі (FSR)", size=16, bold=True, color="#1e293b"))

    # Регістри (каскад з n комірок)
    reg_labels = ["sₜ₊ₙ₋₁", "sₜ₊ₙ₋₂", "...", "sₜ₊₁", "sₜ"]
    reg_xs = [160, 290, 420, 550, 680]

    for x, lbl in zip(reg_xs, reg_labels):
        if lbl == "...":
            frags.append(text(x, 140, "...", size=20, bold=True, color="#64748b"))
        else:
            b, _, _ = textbox(x, 140, f"D-тригер\n[{lbl}]", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
            frags.append(b)

    # Зсув між комірками (стрілки вправо)
    frags.append(arrow(205, 140, 245, 140, color=BLUE_S, sw=2))
    frags.append(arrow(335, 140, 395, 140, color=BLUE_S, sw=2))
    frags.append(arrow(445, 140, 505, 140, color=BLUE_S, sw=2))
    frags.append(arrow(595, 140, 635, 140, color=BLUE_S, sw=2))

    # Вихід послідовності бітів (з останнього тригера s_t)
    frags.append(arrow(725, 140, 800, 140, color=GREEN_S, sw=2.5))
    b_out, _, _ = textbox(810, 180, "Вихідний потік бітів\nSequence Stream S", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_out)

    # Блок зворотного зв'язку f(s_t, ..., s_{t+n-1})
    b_feedback, _, _ = textbox(420, 270, "НЕЛІНІЙНА ФУНКЦІЯ ЗВОРОТНОГО ЗВ'ЯЗКУ f(sₜ, ..., sₜ₊ₙ₋₁)\nf(s) = g(s) ⊕ sₜ  (модифікований NLFSR)", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_feedback)

    # Входи до функції зворотного зв'язку від усіх комірок
    for x in [160, 290, 550, 680]:
        frags.append(line(x, 175, x, 240, color=AMBER_S, sw=1.5))
        frags.append(arrow(x, 240, 420, 245, color=AMBER_S, sw=1.2))

    # Повернення сигналу з зворотного зв'язку на вхід першої комірки s_{t+n-1}
    frags.append(line(240, 270, 80, 270, color=RED_S, sw=2))
    frags.append(line(80, 270, 80, 140, color=RED_S, sw=2))
    frags.append(arrow(80, 140, 115, 140, color=RED_S, sw=2))
    frags.append(text(75, 205, "Новий біт", size=10, bold=True, color=RED_S))

    render(os.path.join(IMG, "fig4-shift-register-hardware.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_debruijn_graph_b23()
    fig_kmer_assembly_dna()
    fig_eulerian_hamiltonian_duality()
    fig_shift_register_hardware()
    print("Усі 4 фігури графа де Брейнена успішно згенеровано у ./img/")
