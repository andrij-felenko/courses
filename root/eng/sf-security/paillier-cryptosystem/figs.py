# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_paillier_homomorphic_concept():
    W, H = 1000, 480
    p = []

    p.append(text(W / 2, 45, "Гомоморфне додавання Пайє: обчислення над зашифрованими даними",
                  size=18, bold=True))

    # Секція клієнтів (ліворуч)
    p.append(rect(40, 90, 260, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(170, 120, "Клієнти (власники даних)", size=15, bold=True, color=INK))

    # Голос/Дане 1
    b1, _, _ = textbox(170, 180, ["Повідомлення m₁ = 15", "Зашифрування: c₁ = E(m₁)"],
                       size=13, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2)
    p.append(b1)

    # Голос/Дане 2
    b2, _, _ = textbox(170, 280, ["Повідомлення m₂ = 27", "Зашифрування: c₂ = E(m₂)"],
                       size=13, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2)
    p.append(b2)

    # Результат розшифрування
    b3, _, _ = textbox(170, 380, ["Отримано: m₁ + m₂ = 42", "Розшифрування: D(c_sum)"],
                       size=13, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    p.append(b3)

    # Секція сервера (праворуч)
    p.append(rect(580, 90, 380, 340, fill="#f4f6f8", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(770, 120, "Недовірений сервер (без приватного ключа)", size=15, bold=True, color=INK))

    b_srv, _, _ = textbox(770, 230, [
        "Множення шифротекстів mod n²:",
        "c_sum = (c₁ · c₂) mod n²",
        "",
        "Сервер обчислив суму,",
        "НЕ знаючи m₁ та m₂!"
    ], size=13.5, pad=14, fill="#ffffff", stroke=FIELD, sw=1.6)
    p.append(b_srv)

    # Стрілки
    p.append(arrow(300, 180, 580, 200, color=FIELD, sw=1.8))
    p.append(text(440, 178, "c₁ mod n²", size=12.5, bold=True, color=FIELD))

    p.append(arrow(300, 280, 580, 250, color=FIELD, sw=1.8))
    p.append(text(440, 275, "c₂ mod n²", size=12.5, bold=True, color=FIELD))

    p.append(arrow(580, 340, 300, 380, color=FIELD, sw=1.8))
    p.append(text(440, 375, "c_sum mod n²", size=12.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "paillier-homomorphic-concept.svg"), W, H,
           *p, title="Принцип гомоморфного додавання криптосистеми Пайє")


def fig_paillier_isomorphism():
    W, H = 1020, 460
    p = []

    p.append(text(W / 2, 45, "Алгебраїчна структура ℤ_{n²}* ≅ ℤ_n × ℤ_n*",
                  size=18, bold=True))

    # Лівий блок - група шифротекстів
    b_group, _, _ = textbox(240, 200, [
        "Мультиплікативна група ℤ_{n²}*",
        "Порядок: n · φ(n)",
        "Шифротекст c = g^m · r^n mod n²"
    ], size=14, pad=14, fill="#ffffff", stroke="#94a3b8", sw=1.5, bold=True)
    p.append(b_group)

    # Ізоморфізм (стрілка по центру)
    p.append(arrow(430, 200, 590, 200, color=FIELD, sw=2.2))
    p.append(arrow(590, 230, 430, 230, color=FIELD, sw=2.2))
    p.append(text(510, 185, "ізоморфізм ε", size=13.5, bold=True, color=FIELD))
    p.append(text(510, 252, "ε(m, r) = (1+n)^m · r^n mod n²", size=12.5, color=MUTED))

    # Правий блок - розкладання на компоненти
    # Підгрупа повідомлень
    b_m, _, _ = textbox(790, 140, [
        "Аддитивна підгрупа повідомлень ℤ_n",
        "Елементи: (1 + n)^m ≡ 1 + m·n mod n²",
        "Порядок підгрупи: n"
    ], size=13, pad=12, fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD)
    p.append(b_m)

    p.append(text(790, 235, "× (прямий добуток)", size=14, bold=True, color=INK))

    # Підгрупа випадкового шуму
    b_r, _, _ = textbox(790, 330, [
        "Мультиплікативна підгрупа n-х степенів ℤ_n*",
        "Елементи: r^n mod n²",
        "Маскування випадковим шумом r"
    ], size=13, pad=12, fill="#f4f6f8", stroke="#94a3b8", sw=1.4)
    p.append(b_r)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 420,
                          "Розділення компонентів: піднесення до степеня λ знищує маску r^n mod n², виділяючи m·λ mod n",
                          size=13.5, pad=10, fill="#fbfbfc", stroke=LINE, sw=1.3, bold=True)
    p.append(b_bot)

    render(os.path.join(OUT, "paillier-isomorphism.svg"), W, H,
           *p, title="Ізоморфізм залишків у криптосистемі Пайє")


def fig_paillier_decryption_flow():
    W, H = 1050, 470
    p = []

    p.append(text(W / 2, 42, "Конвеєр операцій: Генерація ключів → Шифрування → Розшифрування",
                  size=18, bold=True))

    # Етап 1: Генерація ключів
    b1, _, _ = textbox(190, 170, [
        "1. Генерація ключів",
        "• Обрати прості p, q",
        "• Обчислити n = p·q",
        "• λ = нск(p−1, q−1)",
        "• g = 1 + n",
        "• μ = (L(g^λ mod n²))⁻¹ mod n",
        "Публічний: (n, g)",
        "Приватний: (λ, μ)"
    ], size=12.5, pad=12, fill="#ffffff", stroke="#94a3b8", sw=1.4)
    p.append(b1)

    p.append(arrow(340, 170, 420, 170, color=FIELD, sw=1.8))

    # Етап 2: Шифрування
    b2, _, _ = textbox(540, 170, [
        "2. Шифрування E(m, r)",
        "• Вхід: m ∈ ℤ_n, (n, g)",
        "• Випадковий r ∈ ℤ_n*",
        "• Обчислити:",
        "  c = g^m · r^n mod n²",
        "Вихід: шифротекст c"
    ], size=12.5, pad=12, fill="#f4f6f8", stroke="#94a3b8", sw=1.4)
    p.append(b2)

    p.append(arrow(660, 170, 740, 170, color=FIELD, sw=1.8))

    # Етап 3: Розшифрування
    b3, _, _ = textbox(890, 170, [
        "3. Розшифрування D(c)",
        "• Вхід: c, приватний (λ, μ)",
        "• u = c^λ mod n²",
        "• L(u) = (u − 1) / n",
        "• m = L(u) · μ mod n",
        "Вихід: повідомлення m"
    ], size=12.5, pad=12, fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(b3)

    # Нижня частина: гомоморфне маніпулювання
    b_hom, _, _ = textbox(W / 2, 385, [
        "Гомоморфні властивості без розшифрування:",
        "Додавання: E(m₁) · E(m₂) mod n² = E(m₁ + m₂ mod n)     |     Скалярний добуток: E(m)^k mod n² = E(k · m mod n)"
    ], size=13.5, pad=14, fill="#fbfbfc", stroke=FIELD, sw=1.6, bold=True)
    p.append(b_hom)

    render(os.path.join(OUT, "paillier-decryption-flow.svg"), W, H,
           *p, title="Схема конвеєра шифрування та розшифрування Пайє")


def fig_paillier_performance_tradeoff():
    W, H = 1000, 440
    p = []

    p.append(text(W / 2, 45, "Порівняння параметрів: RSA проти Пайє (при n = 2048 біт)",
                  size=18, bold=True))

    # RSA Картка
    b_rsa, _, _ = textbox(260, 200, [
        "Криптосистема RSA",
        "",
        "• Модуль обчислень: n (2048 біт)",
        "• Розмір шифротексту: 2048 біт",
        "• Піднесення до степеня mod n",
        "• Гомоморфізм: Множення E(m₁)·E(m₂)",
        "• Швидкість обчислень: Базова"
    ], size=13, pad=14, fill="#f8fafc", stroke="#94a3b8", sw=1.4)
    p.append(b_rsa)

    # Paillier Картка
    b_pai, _, _ = textbox(740, 200, [
        "Криптосистема Пайє",
        "",
        "• Модуль обчислень: n² (4096 біт)",
        "• Розмір шифротексту: 4096 біт (×2 розширення)",
        "• Піднесення до степеня mod n² (~4-8× повільніше)",
        "• Гомоморфізм: Додавання E(m₁)+E(m₂)",
        "• Призначення: Конфіденційні підсумки"
    ], size=13, pad=14, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(b_pai)

    # Нижній висновок про компроміс
    b_trade, _, _ = textbox(W / 2, 385, [
        "Ціна аддитивного гомоморфізму: подвоєння обсягу шифротексту (n → n²) та збільшення",
        "обчислювальної складності модульного піднесення до степеня за модулем n²."
    ], size=13.5, pad=12, fill="#ffffff", stroke=LINE, sw=1.3, bold=True)
    p.append(b_trade)

    render(os.path.join(OUT, "paillier-performance-tradeoff.svg"), W, H,
           *p, title="Порівняння накладних витрат RSA та Пайє")


fig_paillier_homomorphic_concept()
fig_paillier_isomorphism()
fig_paillier_decryption_flow()
fig_paillier_performance_tradeoff()
print("ok:", sorted(os.listdir(OUT)))
