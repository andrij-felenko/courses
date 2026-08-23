# -*- coding: utf-8 -*-
"""Фігури для теми «Проблема дискретного логарифма» (book/algorithms/complexity-computability/discrete-logarithm)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра кольорів
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig1_dlog_asymmetry():
    """fig1-dlog-asymmetry.svg: Асиметрія між модульним піднесенням до степеня та дискретним логарифмуванням."""
    W, H = 840, 360
    frags = []

    # Рамка фону
    frags.append(rect(10, 10, W-20, H-20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W//2, 34, "Обчислювальна асиметрія: Одностороння функція дискретного логарифма", size=15, bold=True, color="#1e293b"))

    # Прямий напрямок (Прямий шлях: Піднесення до степеня)
    b1, _, _ = textbox(160, 120, "Основа g, експонента x, модуль p\nВхідні дані (x)", size=12, bold=False, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b1)

    b2, _, _ = textbox(420, 120, "Модульне піднесення gˣ mod p\nШвидке піднесення (Square-and-Multiply)\nЧас: O(log x) кроків", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b2)

    b3, _, _ = textbox(680, 120, "Результат y ≡ gˣ mod p\nВихідне значення (y)", size=12, bold=False, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b3)

    # Стрілки прямого шляху
    frags.append(arrow(265, 120, 305, 120, color=GREEN_S, sw=2))
    frags.append(arrow(535, 120, 595, 120, color=GREEN_S, sw=2))
    frags.append(text(W//2, 80, "Прямий напрямок: ЛЕГКО (Поліноміальний час)", size=12, bold=True, color=GREEN_S))

    # Зворотний напрямок (Дискретне логарифмування)
    frags.append(arrow(595, 240, 535, 240, color=RED_S, sw=2))
    frags.append(arrow(305, 240, 265, 240, color=RED_S, sw=2))

    b4, _, _ = textbox(680, 240, "Дано y, g, p\nВідоме значення y", size=12, bold=False, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b4)

    b5, _, _ = textbox(420, 240, "Дискретне логарифмування x = log_g y\nПошук експоненти x у скінченній групі\nЧас: O(√N) або Lₚ[1/3, c] (Експонента/Субекспонента)", size=12, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b5)

    b6, _, _ = textbox(160, 240, "Шукана експонента x\nНевідомий секрет x", size=12, bold=False, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b6)

    frags.append(text(W//2, 285, "Зворотний напрямок: ВАЖКО (Класично складна задача)", size=12, bold=True, color=RED_S))

    # Нижній підпис
    frags.append(text(W//2, 330, "Асиметрія між O(log x) та O(√N) утворює основу криптографії з відкритим ключем (DH, ElGamal, ECC)", size=11, italic=True, color=GRAY_S))

    render(os.path.join(IMG, "fig1-dlog-asymmetry.svg"), W, H, *frags)

def fig2_pohlig_hellman_reduction():
    """fig2-pohlig-hellman-reduction.svg: Редукція Поліґа — Геллмана у групі гладкого порядку."""
    W, H = 840, 380
    frags = []

    frags.append(rect(10, 10, W-20, H-20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W//2, 32, "Схема алгоритму Поліґа — Геллмана: Декомпозиція гладкого порядку групи", size=15, bold=True, color="#1e293b"))

    # Вхідна група
    b0, _, _ = textbox(420, 75, "Група G порядку N = p₁ᵉ¹ · p₂ᵉ² ... pₖᵉnk\nЗадача: gˣ = y у G", size=13, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b0)

    # Три гілки підгруп
    subgroups = [
        ("Підгрупа порядку p₁ᵉ¹\nx ≡ x₁ (mod p₁ᵉ¹)", 160, 175, BLUE_F, BLUE_S),
        ("Підгрупа порядку p₂ᵉ²\nx ≡ x₂ (mod p₂ᵉ²)", 420, 175, BLUE_F, BLUE_S),
        ("Підгрупа порядку pₖᵉnk\nx ≡ xₖ (mod pₖᵉnk)", 680, 175, BLUE_F, BLUE_S)
    ]

    for label, x, y, fill_c, stroke_c in subgroups:
        b, _, _ = textbox(x, y, label, size=11, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b)
        frags.append(arrow(420, 98, x, 150, color=PURPLE_S, sw=1.5))

    # Локальне розв'язання в кожній підгрупі (BSGS / Pollard Rho)
    solvers = [
        ("BSGS / Pollard Rho\nПошук x₁ mod p₁ᵉ¹", 160, 255),
        ("BSGS / Pollard Rho\nПошук x₂ mod p₂ᵉ²", 420, 255),
        ("BSGS / Pollard Rho\nПошук xₖ mod pₖᵉnk", 680, 255)
    ]

    for label, x, y in solvers:
        b, _, _ = textbox(x, y, label, size=11, bold=False, fill=TEAL_F, stroke=TEAL_S)
        frags.append(b)
        frags.append(arrow(x, 200, x, 235, color=BLUE_S, sw=1.5))

    # Відновлення через Китайську теорему про лишки (CRT)
    b_crt, _, _ = textbox(420, 330, "Китайська теорема про лишки (CRT)\nРеконструювання x ≡ xᵢ (mod pᵢᵉⁱ) ⇒ Повний логарифм x mod N", size=12, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_crt)

    for x in [160, 420, 680]:
        frags.append(arrow(x, 278, 420, 310, color=TEAL_S, sw=1.5))

    render(os.path.join(IMG, "fig2-pohlig-hellman-reduction.svg"), W, H, *frags)

def fig3_algorithm_complexity_comparison():
    """fig3-algorithm-complexity-comparison.svg: Порівняння складності алгоритмів дискретного логарифмування."""
    W, H = 840, 380
    frags = []

    frags.append(rect(10, 10, W-20, H-20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W//2, 30, "Порівняльний спектр складності алгоритмів розв'язання DLP", size=15, bold=True, color="#1e293b"))

    algos = [
        ("Перебір (Trial Search)", "O(N)", "Експоненціальна", "Усі групи", RED_F, RED_S, 100),
        ("Shanks BSGS", "O(√N) час / O(√N) пам'ять", "Універсальна (Generic)", "Усі групи", AMBER_F, AMBER_S, 155),
        ("Pollard's Rho", "O(√N) час / O(1) пам'ять", "Універсальна (Generic)", "Усі групи", AMBER_F, AMBER_S, 210),
        ("Index Calculus", "Lₚ[1/2, c]", "Субекспоненціальна", "Скінченні поля 𝔽ₚ*", BLUE_F, BLUE_S, 265),
        ("Number Field Sieve (NFS)", "Lₚ[1/3, c]", "Субекспоненціальна", "Великі поля 𝔽ₚ*", TEAL_F, TEAL_S, 320)
    ]

    headers = [("Алгоритм", 130), ("Часова складність", 340), ("Тип складності", 550), ("Область застосування", 730)]
    for title, x in headers:
        frags.append(text(x, 60, title, size=12, bold=True, color="#334155"))

    frags.append(line(30, 75, W-30, 75, color="#cbd5e1", sw=1.5))

    for name, compl, ctype, scope, fill_c, stroke_c, y in algos:
        frags.append(rect(30, y-15, W-60, 30, fill=fill_c, stroke=stroke_c, sw=1, rx=4))
        frags.append(text(130, y, name, size=11, bold=True, color="#1e293b"))
        frags.append(text(340, y, compl, size=11, bold=True, color="#0f172a"))
        frags.append(text(550, y, ctype, size=11, color="#334155"))
        frags.append(text(730, y, scope, size=11, color="#334155"))

    render(os.path.join(IMG, "fig3-algorithm-complexity-comparison.svg"), W, H, *frags)

def fig4_diffie_hellman_hierarchy():
    """fig4-diffie-hellman-hierarchy.svg: Ієрархія важкості криптографічних задач DH."""
    W, H = 840, 320
    frags = []

    frags.append(rect(10, 10, W-20, H-20, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(W//2, 30, "Ієрархія складності криптографічних припущень Діффі — Геллмана", size=15, bold=True, color="#1e293b"))

    # Три блоки
    b1, _, _ = textbox(170, 130, "DLP (Discrete Logarithm Problem)\nДано: g, gᵃ mod p\nЗнайти: a\nНАЙВАЖЧА ЗАДАЧА", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b1)

    b2, _, _ = textbox(420, 130, "CDH (Computational Diffie-Hellman)\nДано: g, gᵃ, gᵇ mod p\nОбчислити: gᵃᵇ mod p\nОБЧИСЛЮВАЛЬНА ЗАДАЧА", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b2)

    b3, _, _ = textbox(670, 130, "DDH (Decisional Diffie-Hellman)\nДано: g, gᵃ, gᵇ, gᶜ mod p\nВизначити: c ≡ ab чи випадковий?\nРОЗРІЗНЯЛЬНА ЗАДАЧА", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b3)

    # Стрілки зведення
    frags.append(arrow(275, 130, 310, 130, color=RED_S, sw=2))
    frags.append(text(292, 110, "Зведення", size=10, bold=True, color=RED_S))

    frags.append(arrow(530, 130, 565, 130, color=AMBER_S, sw=2))
    frags.append(text(547, 110, "Зведення", size=10, bold=True, color=AMBER_S))

    # Пояснення відносин
    b_exp, _, _ = textbox(W//2, 240, "Відношення складності: DLP ≥ CDH ≥ DDH\nЯкщо DLP легко розв'язується → CDH і DDH миттєво ламаються.\nБезпека протоколів ElGamal та DH спирається на стійкість CDH та DDH.", size=11, bold=False, fill=GRAY_F, stroke=GRAY_S)
    frags.append(b_exp)

    render(os.path.join(IMG, "fig4-diffie-hellman-hierarchy.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_dlog_asymmetry()
    fig2_pohlig_hellman_reduction()
    fig3_algorithm_complexity_comparison()
    fig4_diffie_hellman_hierarchy()
    print("All figures successfully generated in img/")
