# -*- coding: utf-8 -*-
"""Фігури для теми «Евристика Фіата — Шаміра» (book/algorithms/complexity-computability/fiat-shamir-transform)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_BG = "#ffffff"
COLOR_HEADER = "#e2e8f0"
COLOR_PROVER = "#dbeafe"       # синій для Доводжувача
COLOR_PROVER_BORDER = "#2563eb"
COLOR_VERIFIER = "#fef3c7"     # жовтий для Верифікатора
COLOR_VERIFIER_BORDER = "#d97706"
COLOR_HASH = "#f3e8ff"         # фіолетовий для Хеш-функції
COLOR_HASH_BORDER = "#7e22ce"
COLOR_SUCCESS = "#d1fae5"      # зелений для Результату
COLOR_SUCCESS_BORDER = "#059669"
COLOR_DANGER = "#fee2e2"       # червоний для Вразливості
COLOR_DANGER_BORDER = "#dc2626"
COLOR_MUTED = "#64748b"
COLOR_LINE = "#333333"

def fig1_interactive_vs_noninteractive():
    """Фігура 1: Перетворення інтерактивного 3-раундового протоколу Сигма на неінтерактивний протокол Фіата — Шаміра."""
    W, H = 960, 520
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 35, "Інтерактивний протокол Сигма vs Неінтерактивне перетворення Фіата — Шаміра",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ліва панель — Інтерактивний протокол (3 раунди)
    frags.append(rect(25, 75, 440, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(245, 105, "1. Інтерактивний протокол Сигма", size=14, bold=True, color="#1e3a8a"))
    frags.append(text(245, 125, "Потрібен синхронний зв'язок у реальному часі", size=11, italic=True, color=COLOR_MUTED))

    # Стовпчики P та V
    frags.append(textbox(115, 160, "Доводжувач P\n(знає свідок w)", size=11, bold=True, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(textbox(360, 160, "Верифікатор V\n(підкидає монети)", size=11, bold=True, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])

    # Раунд 1: P -> V (Commitment α)
    frags.append(text(235, 208, "Раунд 1: Обов'язання α = P₁(x, w; r)", size=10.5, bold=True, color="#1e3a8a"))
    frags.append(arrow(135, 222, 340, 222, color=COLOR_LINE, sw=1.8))
    frags.append(text(235, 238, "α (зобов'язання)", size=10, color=COLOR_LINE))

    # Раунд 2: V -> P (Challenge β)
    frags.append(text(235, 273, "Раунд 2: Виклик β ← {0,1}ᵏ", size=10.5, bold=True, color="#7c2d12"))
    frags.append(arrow(340, 287, 135, 287, color=COLOR_LINE, sw=1.8))
    frags.append(text(235, 303, "β (випадковий виклик)", size=10, color=COLOR_LINE))

    # Раунд 3: P -> V (Response γ)
    frags.append(text(235, 338, "Раунд 3: Відповідь γ = P₂(x, w, r, β)", size=10.5, bold=True, color="#1e3a8a"))
    frags.append(arrow(135, 352, 340, 352, color=COLOR_LINE, sw=1.8))
    frags.append(text(235, 368, "γ (відповідь)", size=10, color=COLOR_LINE))

    # Перевірка V
    frags.append(textbox(355, 435, "Перевірка V(x, α, β, γ) = 1\n(Успіх)", size=10.5, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])


    # Права панель — Неінтерактивний протокол (Фіат — Шамір)
    frags.append(rect(490, 75, 445, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(712, 105, "2. Перетворення Фіата — Шаміра", size=14, bold=True, color="#5b21b6"))
    frags.append(text(712, 125, "Заміна верифікатора на хеш-функцію H(x || α)", size=11, italic=True, color=COLOR_MUTED))

    # Компоненти P, H, V
    frags.append(textbox(575, 160, "Доводжувач P\n(автономний)", size=11, bold=True, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(textbox(712, 160, "Випадковий оракул H\n(Хеш-функція)", size=11, bold=True, fill=COLOR_HASH, stroke=COLOR_HASH_BORDER)[0])
    frags.append(textbox(855, 160, "Верифікатор V\n(офлайн)", size=11, bold=True, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])

    # Крок 1: P генерує α
    frags.append(textbox(575, 230, "1. α = P₁(x, w; r)", size=10.5, fill="#ffffff", stroke=COLOR_PROVER_BORDER)[0])

    # Крок 2: P обчислює β локально через H
    frags.append(arrow(575, 255, 712, 280, color=COLOR_LINE, sw=1.5))
    frags.append(textbox(712, 305, "2. β = H(x || α)\n(локальний виклик)", size=10.5, bold=True, fill=COLOR_HASH, stroke=COLOR_HASH_BORDER)[0])

    # Крок 3: P обчислює γ
    frags.append(arrow(712, 330, 575, 355, color=COLOR_LINE, sw=1.5))
    frags.append(textbox(575, 380, "3. γ = P₂(x, w, r, β)\nДоказ π = (α, γ)", size=10, fill="#ffffff", stroke=COLOR_PROVER_BORDER)[0])

    # Передача доказу π верифікатору V
    frags.append(arrow(575, 425, 855, 425, color=COLOR_LINE, sw=1.8))
    frags.append(textbox(855, 435, "4. Перевірка V:\nβ' = H(x || α)\nV(x, α, β', γ) = 1", size=10, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])

    render(os.path.join(IMG, "fig1-interactive-vs-noninteractive.svg"), W, H, *frags)


def fig2_fiat_shamir_signature_flow():
    """Фігура 2: Конвеєр створення та перевірки цифрового підпису Фіата — Шаміра / Шнорра."""
    W, H = 940, 460
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(470, 30, "Конвеєр цифрового підпису на основі евристики Фіата — Шаміра",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Верхній блок — Генерація підпису
    frags.append(rect(25, 70, 890, 175, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(470, 95, "Генерація підпису σ (Секретний ключ sk = x, Повідомлення m)", size=13, bold=True, color="#0369a1"))

    frags.append(textbox(115, 145, "Випадкове r ← ℤ_q\nКомітмент α = gʳ", size=10.5, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(arrow(185, 145, 270, 145, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(370, 145, "Обчислення виклику:\nβ = H(m || α)", size=10.5, bold=True, fill=COLOR_HASH, stroke=COLOR_HASH_BORDER)[0])
    frags.append(arrow(470, 145, 540, 145, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(645, 145, "Обчислення відповіді:\nγ = r + β · x (mod q)", size=10.5, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(arrow(750, 145, 815, 145, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(855, 145, "Підпис σ\n(α, γ)", size=11, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])


    # Нижній блок — Перевірка підпису
    frags.append(rect(25, 265, 890, 175, fill="#fdf4ff", stroke="#c084fc", sw=1.5, rx=8))
    frags.append(text(470, 290, "Перевірка підпису (Публічний ключ pk = y = gˣ, Повідомлення m, Підпис σ = (α, γ))", size=12.5, bold=True, color="#6b21a8"))

    frags.append(textbox(145, 360, "Вхід:\nm, pk = y, σ = (α, γ)", size=10.5, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])
    frags.append(arrow(240, 360, 310, 360, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(415, 360, "1. Реконструкція виклику:\nβ' = H(m || α)", size=10.5, bold=True, fill=COLOR_HASH, stroke=COLOR_HASH_BORDER)[0])
    frags.append(arrow(520, 360, 595, 360, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(745, 360, "2. Перевірка ґрунтовності:\ng^γ =?= α · y^β' (mod p)\n(Якщо рівно — ПІДПИС ДІЙСНИЙ)", size=10.5, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])

    render(os.path.join(IMG, "fig2-fiat-shamir-signature-flow.svg"), W, H, *frags)


def fig3_weak_vs_strong_fiat_shamir():
    """Фігура 3: Порівняння слабкої (Weak) та сильної (Strong) евристики Фіата — Шаміра."""
    W, H = 940, 480
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(470, 30, "Порівняння Слабкого (Weak) та Сильного (Strong) Фіата — Шаміра",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ліва панель — Слабкий Фіат — Шамір (Вразливий)
    frags.append(rect(25, 75, 440, 380, fill="#fff5f5", stroke=COLOR_DANGER_BORDER, sw=1.5, rx=10))
    frags.append(text(245, 105, "Слабкий Фіат — Шамір (Weak FS)", size=14, bold=True, color="#991b1b"))
    frags.append(text(245, 125, "ВРАЗЛИВІСТЬ: контекст x випущено з хешу!", size=11, bold=True, color="#b91c1c"))

    frags.append(textbox(245, 175, "Обчислення виклику:\nβ = H(α)\n(не залежить від твердження x або m)", size=10.5, fill="#ffffff", stroke=COLOR_DANGER_BORDER)[0])
    frags.append(arrow(245, 212, 245, 245, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(245, 285, "Атака підробки (Forgery Attack):\n1. Атакуючий фіксує виклик β = H(α)\n2. Підбирає твердження x' під пару (α, γ)\n3. Генерує підроблений доказ для чужої теми", size=10, fill=COLOR_DANGER, stroke=COLOR_DANGER_BORDER)[0])
    frags.append(arrow(245, 345, 245, 375, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(245, 410, "РЕЗУЛЬТАТ: Повна підробка доказів\nта підписів для чужих контекстів", size=10.5, bold=True, color="#991b1b", fill="#ffffff", stroke=COLOR_DANGER_BORDER)[0])


    # Права панель — Сильний Фіат — Шамір (Безпечний)
    frags.append(rect(495, 75, 440, 380, fill="#f0fdf4", stroke=COLOR_SUCCESS_BORDER, sw=1.5, rx=10))
    frags.append(text(715, 105, "Сильний Фіат — Шамір (Strong FS)", size=14, bold=True, color="#166534"))
    frags.append(text(715, 125, "БЕЗПЕЧНО: контекст x та зобов'язання α в хеші", size=11, bold=True, color="#15803d"))

    frags.append(textbox(715, 175, "Обчислення виклику:\nβ = H(x || α)  або  β = H(m || α)\n(криптографічна прив'язка до контексту)", size=10.5, fill="#ffffff", stroke=COLOR_SUCCESS_BORDER)[0])
    frags.append(arrow(715, 212, 715, 245, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(715, 285, "Захист від підробки:\nБудь-яка зміна x' або m' змінює β'\nАтакуючий не може підібрати γ без\nзнання секретного свідка w", size=10, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])
    frags.append(arrow(715, 345, 715, 375, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(715, 410, "РЕЗУЛЬТАТ: Доведена обґрунтованість\nу моделі випадкового оракула (ROM)", size=10.5, bold=True, color="#166534", fill="#ffffff", stroke=COLOR_SUCCESS_BORDER)[0])

    render(os.path.join(IMG, "fig3-weak-vs-strong-fiat-shamir.svg"), W, H, *frags)


def fig4_multi_round_transcript_chain():
    """Фігура 4: Багатораундове каскадне ланцюгування транскрипту для протоколів із багатьма раундами (IOP, Sumcheck, STARKs)."""
    W, H = 960, 480
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 30, "Каскадне ланцюгування транскрипту для багатораундових протоколів (IOP / STARKs)",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ініціалізація стану транскрипту
    frags.append(textbox(115, 100, "Ініціалізація:\nState S₀ = H(Context || x)", size=10.5, bold=True, fill=COLOR_HASH, stroke=COLOR_HASH_BORDER)[0])
    frags.append(arrow(195, 100, 255, 100, color=COLOR_LINE, sw=1.8))

    # Раунд 1
    frags.append(rect(265, 60, 205, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(367, 85, "Раунд 1", size=13, bold=True, color="#1e3a8a"))
    frags.append(textbox(367, 130, "Повідомлення α₁\nвід Доводжувача", size=10.5, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(arrow(367, 160, 367, 195, color=COLOR_LINE, sw=1.5))
    frags.append(textbox(367, 235, "Оновлення стану:\nS₁ = H(S₀ || α₁)", size=10.5, bold=True, fill=COLOR_HASH, stroke=COLOR_HASH_BORDER)[0])
    frags.append(arrow(367, 275, 367, 310, color=COLOR_LINE, sw=1.5))
    frags.append(textbox(367, 350, "Виклик Раунду 1:\nβ₁ = H(S₁ || 'ch')", size=10.5, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])

    frags.append(arrow(470, 235, 500, 235, color=COLOR_LINE, sw=1.8))

    # Раунд 2
    frags.append(rect(510, 60, 205, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(612, 85, "Раунд 2", size=13, bold=True, color="#1e3a8a"))
    frags.append(textbox(612, 130, "Повідомлення α₂\n(залежить від β₁)", size=10.5, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(arrow(612, 160, 612, 195, color=COLOR_LINE, sw=1.5))
    frags.append(textbox(612, 235, "Оновлення стану:\nS₂ = H(S₁ || α₂)", size=10.5, bold=True, fill=COLOR_HASH, stroke=COLOR_HASH_BORDER)[0])
    frags.append(arrow(612, 275, 612, 310, color=COLOR_LINE, sw=1.5))
    frags.append(textbox(612, 350, "Виклик Раунду 2:\nβ₂ = H(S₂ || 'ch')", size=10.5, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])

    frags.append(arrow(715, 235, 745, 235, color=COLOR_LINE, sw=1.8))

    # Раунд k та Фінальний підсумок
    frags.append(rect(755, 60, 190, 380, fill="#f0fdf4", stroke=COLOR_SUCCESS_BORDER, sw=1.5, rx=8))
    frags.append(text(850, 85, "Фінал", size=13, bold=True, color="#166534"))
    frags.append(textbox(850, 160, "Секвенція викликів:\n(β₁, β₂, ..., βₖ)", size=10.5, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])
    frags.append(arrow(850, 200, 850, 235, color=COLOR_LINE, sw=1.5))
    frags.append(textbox(850, 305, "Повний доказ π:\n(α₁, α₂, ..., αₖ, γ)\nз незмінним H", size=10, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])

    render(os.path.join(IMG, "fig1-interactive-vs-noninteractive.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_interactive_vs_noninteractive()
    fig2_fiat_shamir_signature_flow()
    fig3_weak_vs_strong_fiat_shamir()
    fig4_multi_round_transcript_chain()
    print("Усі 4 фігури успішно згенеровано у book/algorithms/complexity-computability/fiat-shamir-transform/img/")
