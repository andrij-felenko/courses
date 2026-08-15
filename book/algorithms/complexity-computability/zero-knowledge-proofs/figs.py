# -*- coding: utf-8 -*-
"""Фігури для теми «Протоколи нульового розголошення» (book/algorithms/complexity-computability/zero-knowledge-proofs)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_BG = "#ffffff"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_PROVER = "#fef3c7"         # бурштиновий для доводжувача (Prover)
COLOR_PROVER_BORDER = "#d97706"
COLOR_VERIFIER = "#dbeafe"       # синій для верифікатора (Verifier)
COLOR_VERIFIER_BORDER = "#2563eb"
COLOR_SIMULATOR = "#f3e8ff"      # фіолетовий для симулятора (Simulator)
COLOR_SIMULATOR_BORDER = "#9333ea"
COLOR_SUCCESS = "#d1fae5"        # зелений для успішної перевірки
COLOR_SUCCESS_BORDER = "#059669"
COLOR_MUTED = "#64748b"
COLOR_LINE = "#333333"

def fig1_zkp_simulation():
    """Фігура 1: Порівняння реальної взаємодії та симуляції у парадигмі нульового розголошення."""
    W, H = 960, 520
    frags = []

    # Заголовок
    t_box, _, _ = textbox(480, 35, "Парадигма симуляції у протоколах нульового розголошення (ZK)",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Ліва панель — Реальний світ (Real World)
    frags.append(rect(30, 75, 435, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(247, 105, "Реальний світ (Real Execution)", size=15, bold=True, color="#1e3a8a"))
    frags.append(text(247, 127, "Взаємодія справжнього Prover із секретом w та Verifier", size=11, italic=True, color=COLOR_MUTED))

    # Секретний свідок
    tb_w, _, _ = textbox(247, 168, "Секретний свідок w (Witness)\n(Наприклад: секретний ключ або NP-свідок)",
                         size=11, bold=True, fill="#fff7ed", stroke="#ea580c", sw=1.5, pad=6)
    frags.append(tb_w)

    # Доводжувач (Prover)
    tb_p, _, _ = textbox(247, 235, "Доводжувач P(x, w)\nОбчислює зобов'язання та відповіді\nвикористовуючи секрет w",
                         size=11, bold=True, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER, sw=1.5, pad=8)
    frags.append(tb_p)

    # Стрілки взаємодії
    frags.append(arrow(247, 275, 247, 305, color=COLOR_LINE, sw=1.5))
    frags.append(text(247, 290, "Протокол P(x,w) ↔ V*(x)", size=10, bold=True, color=COLOR_LINE))

    # Верифікатор (Verifier V*)
    tb_v, _, _ = textbox(247, 345, "Верифікатор V*(x)\n(Може діяти зловмисно,\nале з обмеженням PPT)",
                         size=11, bold=True, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER, sw=1.5, pad=8)
    frags.append(tb_v)

    # Результат реального виконання
    tb_view_real, _, _ = textbox(247, 435, "Транскрипт виконання: View_V*(P(x,w) ↔ V*(x))\nВключає всі випадкові монети та повідомлення",
                                 size=10, bold=True, fill="#f1f5f9", stroke="#475569", sw=1.5, pad=6)
    frags.append(tb_view_real)


    # Права панель — Ідеальний світ / Симуляція (Simulated World)
    frags.append(rect(495, 75, 435, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(712, 105, "Симуляція (Ideal World / Simulation)", size=15, bold=True, color="#581c87"))
    frags.append(text(712, 127, "Симулятор створює транскрипт БЕЗ secrets w", size=11, italic=True, color=COLOR_MUTED))

    # Симулятор (Simulator)
    tb_s, _, _ = textbox(712, 180, "Симулятор S^{V*}(x)\nНЕ знає секретного свідка w!\nМає доступ до стану та монет V*",
                         size=11, bold=True, fill=COLOR_SIMULATOR, stroke=COLOR_SIMULATOR_BORDER, sw=1.5, pad=8)
    frags.append(tb_s)

    # Механізм перемотування
    tb_rewind, _, _ = textbox(712, 275, "Механізм перемотування (Rewinding):\n1. Згенерувати фальшиве зобов'язання\n2. Отримати виклик від V*\n3. Перемотати стан V* при незбігу",
                              size=11, bold=True, fill="#fdf4ff", stroke="#c084fc", sw=1.5, pad=8)
    frags.append(tb_rewind)

    # Результат симулятора
    tb_view_sim, _, _ = textbox(712, 365, "Згенерований транскрипт: S(x)\nАбсолютно невідрізнюваний від View_V*",
                                size=10, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER, sw=1.5, pad=6)
    frags.append(tb_view_sim)

    # Нижнє твердження про невідрізнюваність
    tb_indist, _, _ = textbox(712, 440, "Розподіли імовірностей:\nView_V* ≈_c S(x) (Обчислювальна/Статистична)",
                               size=11, bold=True, fill="#fae8ff", stroke="#d8b4fe", sw=1.5, pad=6)
    frags.append(tb_indist)

    render(os.path.join(IMG, "fig1-zkp-simulation.svg"), W, H, *frags)


def fig2_schnorr_protocol():
    """Фігура 2: Діаграма обміну повідомленнями у протоколі Шнорра (Sigma-протокол)."""
    W, H = 940, 480
    frags = []

    # Заголовок
    t_box, _, _ = textbox(470, 35, "Інтерактивний Sigma-протокол Шнорра (Proof of Knowledge of Discrete Log)",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Загальні параметри
    t_param, _, _ = textbox(470, 82, "Спільний вхід: група G порядку q з генератором g. Публічний ключ Y = g^x mod p. Секрет: x",
                            size=12, bold=True, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, pad=6)
    frags.append(t_param)

    # Доводжувач (Ліворуч)
    frags.append(rect(50, 120, 240, 330, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER, sw=1.5, rx=8))
    frags.append(text(170, 145, "Доводжувач (Prover P)", size=14, bold=True, color="#7c2d12"))
    frags.append(mtext(170, 200, "Знає секретний ключ x\n\n1. Генерує r ∈_R Z_q\n2. Обчислює R = g^r mod p\n   (Зобов'язання / Commitment)\n\n3. Отримує виклик e від V\n\n4. Обчислює відповідь:\n   s = (r + e · x) mod q\n   (Відповідь / Response)", size=11, color="#7c2d12"))

    # Стрілка 1: Commitment R
    frags.append(arrow(300, 210, 630, 210, color="#d97706", sw=2))
    frags.append(text(465, 195, "1. Зобов'язання R = g^r mod p", size=12, bold=True, color="#b45309"))

    # Стрілка 2: Challenge e
    frags.append(arrow(630, 280, 300, 280, color="#2563eb", sw=2))
    frags.append(text(465, 265, "2. Випадковий виклик e ∈_R Z_q", size=12, bold=True, color="#1d4ed8"))

    # Стрілка 3: Response s
    frags.append(arrow(300, 350, 630, 350, color="#d97706", sw=2))
    frags.append(text(465, 335, "3. Відповідь s = r + e · x mod q", size=12, bold=True, color="#b45309"))

    # Верифікатор (Праворуч)
    frags.append(rect(640, 120, 250, 330, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER, sw=1.5, rx=8))
    frags.append(text(765, 145, "Верифікатор (Verifier V)", size=14, bold=True, color="#1e3a8a"))
    frags.append(mtext(765, 200, "Знає лише публічний ключ Y\n\n1. Чекає на R від P\n\n2. Обирає випадковий\n   виклик e ∈_R Z_q\n\n3. Отримує відповідь s\n\n4. Перевіряє тотожність:\n   g^s ≡ R · Y^e mod p", size=11, color="#1e3a8a"))

    # Блок перевірки на дні
    tb_check, _, _ = textbox(465, 415, "Рівність верифікації: g^s = g^(r + e·x) = g^r · (g^x)^e = R · Y^e (mod p)",
                             size=11, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER, sw=1.5, pad=6)
    frags.append(tb_check)

    render(os.path.join(IMG, "fig2-schnorr-protocol.svg"), W, H, *frags)


def fig3_snark_pipeline():
    """Фігура 3: Конвеєр перетворення обчислення на доказ ZK-SNARK."""
    W, H = 960, 480
    frags = []

    # Заголовок
    t_box, _, _ = textbox(480, 35, "Конвеєр ZK-SNARK: Від алгоритму до компактного доказу",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # 4 етапи трансформації
    # Етап 1: Обчислювальне твердження
    frags.append(rect(30, 95, 200, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(130, 120, "1. Програма / Код", size=13, bold=True, color="#1e293b"))
    frags.append(mtext(130, 200, "Обчислення:\ny = f(x, w)\n\nПриклад:\nw² + 3w = y\n\nМова вищого рівня\n(Circom, Leo, ZoKrates)", size=11, color="#334155"))

    # Стрілка 1 -> 2
    frags.append(arrow(235, 260, 265, 260, color=COLOR_LINE, sw=2))

    # Етап 2: Арифметична схема
    frags.append(rect(270, 95, 200, 340, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(370, 120, "2. Арифметична схема", size=13, bold=True, color="#0369a1"))
    frags.append(mtext(370, 200, "Гейти +, × над F_p\n\nВентилі вентильної\nмережі:\nv₁ = w × w\nv₂ = 3 × w\ny = v₁ + v₂", size=11, color="#0284c7"))

    # Стрілка 2 -> 3
    frags.append(arrow(475, 260, 505, 260, color=COLOR_LINE, sw=2))

    # Етап 3: R1CS та QAP
    frags.append(rect(510, 95, 200, 340, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(610, 120, "3. R1CS / QAP", size=13, bold=True, color="#b45309"))
    frags.append(mtext(610, 200, "Система обмежень\nрангу 1 (R1CS):\n(A·s) × (B·s) = (C·s)\n\nПеретворення у QAP:\nПоліноми A(x), B(x), C(x)\nділяться на T(x)", size=11, color="#b45309"))

    # Стрілка 3 -> 4
    frags.append(arrow(715, 260, 745, 260, color=COLOR_LINE, sw=2))

    # Етап 4: Криптографічний доказ
    frags.append(rect(750, 95, 180, 340, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER, sw=1.5, rx=8))
    frags.append(text(840, 120, "4. ZK-SNARK Доказ", size=13, bold=True, color="#065f46"))
    frags.append(mtext(840, 200, "Еліптичні криві\nта спарювання (Pairing)\n\nДоказ π = (A, B, C)\nРозмір: ~128-288 байт\n\nПеревірка V:\nза O(1) часу!", size=11, color="#065f46"))

    # Нижній інфо-блок
    tb_bottom, _, _ = textbox(480, 452, "Основні властивості SNARK: Succinct (стислий), Non-interactive (неінтерактивний), Zero-Knowledge (з нульовим розголошенням)",
                              size=11, bold=True, fill="#f1f5f9", stroke="#64748b", sw=1.5, pad=6)
    frags.append(tb_bottom)

    render(os.path.join(IMG, "fig3-snark-pipeline.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_zkp_simulation()
    fig2_schnorr_protocol()
    fig3_snark_pipeline()
    print("Всі фігури для zero-knowledge-proofs успішно згенеровано у", IMG)
