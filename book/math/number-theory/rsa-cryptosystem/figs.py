# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_rsa_encryption_flow():
    W, H = 1000, 480
    p = []

    p.append(text(W / 2, 40, "Схема роботи асиметричної криптосистеми RSA", size=18, bold=True))

    # Секція 1: Генерація ключів (ліворуч)
    p.append(rect(40, 85, 270, 355, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(175, 115, "1. Генерація ключів", size=15, bold=True, color=INK))

    b_p, _, _ = textbox(175, 170, ["Прості числа p, q", "N = p · q", "ϕ(N) = (p-1)(q-1)"],
                        size=13, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2)
    p.append(b_p)

    b_pub, _, _ = textbox(175, 260, ["Відкритий ключ (Public Key)", "K_pub = (N, e)", "НСД(e, ϕ(N)) = 1"],
                         size=13, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD, bold=True)
    p.append(b_pub)

    b_priv, _, _ = textbox(175, 360, ["Приватний ключ (Private Key)", "K_priv = (N, d)", "d · e ≡ 1 (mod ϕ(N))"],
                          size=13, pad=10, fill="#fdeded", stroke=POS, sw=1.6, color=POS, bold=True)
    p.append(b_priv)

    # Секція 2: Зашифрування (посередині)
    p.append(rect(360, 85, 270, 355, fill="#f4f6f8", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(495, 115, "2. Зашифрування (Аліса)", size=15, bold=True, color=INK))

    b_msg, _, _ = textbox(495, 170, ["Повідомлення: m < N", "(відкритий текст)"],
                         size=13, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2)
    p.append(b_msg)

    b_enc, _, _ = textbox(495, 260, ["Обчислення шифротексту:", "c = mᵉ mod N", "з використанням (N, e)"],
                         size=13, pad=12, fill="#eef2ff", stroke=NEG, sw=1.6, color=NEG, bold=True)
    p.append(b_enc)

    b_cip, _, _ = textbox(495, 360, ["Шифротекст c", "(непрозорі дані)"],
                         size=13, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2)
    p.append(b_cip)

    # Секція 3: Розшифрування (праворуч)
    p.append(rect(680, 85, 280, 355, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(820, 115, "3. Розшифрування (Боб)", size=15, bold=True, color=INK))

    b_rx, _, _ = textbox(820, 170, ["Отримано шифротекст c"],
                        size=13, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.2)
    p.append(b_rx)

    b_dec, _, _ = textbox(820, 260, ["Обернення піднесенням:", "m = cᵈ mod N", "з використанням (N, d)"],
                         size=13, pad=12, fill="#fdeded", stroke=POS, sw=1.6, color=POS, bold=True)
    p.append(b_dec)

    b_out, _, _ = textbox(820, 360, ["Відновлений текст m", "(початкове повідомлення)"],
                         size=13, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.6, color=FIELD, bold=True)
    p.append(b_out)

    # Стрілки між блоками
    p.append(arrow(310, 260, 360, 260, color=FIELD, sw=1.8))
    p.append(arrow(630, 360, 680, 170, color=NEG, sw=1.8))

    p.append(arrow(495, 205, 495, 225, color=LINE, sw=1.5))
    p.append(arrow(495, 298, 495, 335, color=LINE, sw=1.5))

    p.append(arrow(820, 195, 820, 225, color=LINE, sw=1.5))
    p.append(arrow(820, 298, 820, 335, color=LINE, sw=1.5))

    render(os.path.join(OUT, "rsa-encryption-flow.svg"), W, H,
           *p, title="Схема роботи асиметричної криптосистеми RSA")


def fig_rsa_trapdoor_permutation():
    W, H = 960, 420
    p = []

    p.append(text(W / 2, 40, "Одностороння функція з таємним входом (Trapdoor Permutation)", size=18, bold=True))

    # Лівий блок: Відкритий простір M
    b_m, _, _ = textbox(160, 220, ["Простір повідомлень", "m ∈ ℤ_N"],
                        size=14, pad=16, fill="#eef2ff", stroke=NEG, sw=1.8, color=NEG, bold=True)
    p.append(b_m)

    # Правий блок: Шифрований простір C
    b_c, _, _ = textbox(800, 220, ["Простір шифротекстів", "c ∈ ℤ_N"],
                        size=14, pad=16, fill="#fdeded", stroke=POS, sw=1.8, color=POS, bold=True)
    p.append(b_c)

    # Верхня стрілка: Пряма функція (легко)
    p.append(arrow(265, 170, 695, 170, color=FIELD, sw=2.2))
    b_fwd, _, _ = textbox(480, 140, ["Прямий напрямок: легко для кожного", "c = mᵉ mod N  (знаючи відкритий ключ e, N)"],
                          size=13, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.5, color=FIELD)
    p.append(b_fwd)

    # Нижня стрілка: Обернення без ключа (важко)
    p.append(line(695, 270, 265, 270, color=POS, sw=2.0, dash="6,4"))
    p.append(arrow(280, 270, 265, 270, color=POS, sw=2.0))
    b_rev_hard, _, _ = textbox(480, 310, ["Обернення БЕЗ таємного входу d: обчислювально неможливо", "Вимагає факторизації N = p · q (проблема обчислення d)"],
                              size=12.5, pad=10, fill="#fff5f5", stroke=POS, sw=1.5, color=POS)
    p.append(b_rev_hard)

    # Позначка таємного входу (Trapdoor d)
    b_key, _, _ = textbox(480, 220, ["🔑 Таємний вхід (Trapdoor): d ≡ e⁻¹ mod ϕ(N)", "Зі знанням d обернення легко: m = cᵈ mod N"],
                          size=13, pad=10, fill="#ffffff", stroke="#8b5cf6", sw=1.8, color="#6b21a8", bold=True)
    p.append(b_key)

    render(os.path.join(OUT, "rsa-trapdoor-permutation.svg"), W, H,
           *p, title="Одностороння функція з таємним входом RSA")


def fig_rsa_crt_speedup():
    W, H = 980, 480
    p = []

    p.append(text(W / 2, 40, "Прискорена розшифровка RSA через Китайську теорему про лишки (CRT)", size=18, bold=True))

    # Вхід
    b_in, _, _ = textbox(150, 240, ["Вхідний шифротекст c", "та приватний ключ", "(p, q, dP, dQ, qInv)"],
                         size=13, pad=12, fill="#f8fafc", stroke="#94a3b8", sw=1.5)
    p.append(b_in)

    # Верхня гілка (за модулем p)
    b_p_red, _, _ = textbox(430, 140, ["Зменшення модуля p:", "c_p = c mod p", "d_p = d mod (p-1)"],
                           size=12.5, pad=10, fill="#eef2ff", stroke=NEG, sw=1.5)
    p.append(b_p_red)

    b_p_exp, _, _ = textbox(670, 140, ["Піднесення mod p:", "m_p = (c_p)^(d_p) mod p", "(розмір операнда n/2 біт)"],
                           size=12.5, pad=10, fill="#eef2ff", stroke=NEG, sw=1.5, bold=True)
    p.append(b_p_exp)

    # Нижня гілка (за модулем q)
    b_q_red, _, _ = textbox(430, 340, ["Зменшення модуля q:", "c_q = c mod q", "d_q = d mod (q-1)"],
                           size=12.5, pad=10, fill="#fff7ed", stroke="#c2410c", sw=1.5)
    p.append(b_q_red)

    b_q_exp, _, _ = textbox(670, 340, ["Піднесення mod q:", "m_q = (c_q)^(d_q) mod q", "(розмір операнда n/2 біт)"],
                           size=12.5, pad=10, fill="#fff7ed", stroke="#c2410c", sw=1.5, bold=True)
    p.append(b_q_exp)

    # Рекомбінація Гарнера (Вихід)
    b_rec, _, _ = textbox(870, 240, ["Рекомбінація Гарнера:", "h = (m_p - m_q)·qInv mod p", "m = m_q + h · q", "", "⚡ Прискорення ~4×"],
                         size=12.5, pad=12, fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    p.append(b_rec)

    # З'єднувальні стрілки
    p.append(arrow(260, 220, 340, 140, color=LINE, sw=1.5))
    p.append(arrow(260, 260, 340, 340, color=LINE, sw=1.5))

    p.append(arrow(520, 140, 585, 140, color=NEG, sw=1.5))
    p.append(arrow(520, 340, 585, 340, color="#c2410c", sw=1.5))

    p.append(arrow(755, 140, 785, 220, color=NEG, sw=1.5))
    p.append(arrow(755, 340, 785, 260, color="#c2410c", sw=1.5))

    render(os.path.join(OUT, "rsa-crt-speedup.svg"), W, H,
           *p, title="Прискорення розшифровки RSA через CRT")


def fig_rsa_attack_vectors():
    W, H = 1000, 480
    p = []

    p.append(text(W / 2, 40, "Класифікація векторів атак на криптосистему RSA", size=18, bold=True))

    # Категорія 1: Математичні / Факторизація
    p.append(rect(30, 85, 220, 355, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(140, 115, "Факторизація модуля N", size=13.5, bold=True, color=POS))
    b_cat1, _, _ = textbox(140, 265, [
        "• Алгоритм GNFS",
        "  (квадратичне решето)",
        "• Метод Ферма",
        "  (якщо |p - q| мале)",
        "• P-1 Полларда",
        "  (якщо p-1 гладке)",
        "• Квантовий Шор",
        "  (поліноміальний час)"
    ], size=11.5, pad=8, fill="#ffffff", stroke="#fca5a5", sw=1.2)
    p.append(b_cat1)

    # Категорія 2: Малі показники ключа
    p.append(rect(270, 85, 220, 355, fill="#fff7ed", stroke="#c2410c", sw=1.5, rx=8))
    p.append(text(380, 115, "Малі показники (e, d)", size=13.5, bold=True, color="#c2410c"))
    b_cat2, _, _ = textbox(380, 265, [
        "• Атака Вінера",
        "  (якщо d < N^0.25)",
        "• Атака Копперсміта",
        "  (теорема про корені)",
        "• Трансляція Гостада",
        "  (мале e, k отримувачів)",
        "• Атака спільного модуля",
        "  (однакове N для багатьох)"
    ], size=11.5, pad=8, fill="#ffffff", stroke="#ffedd5", sw=1.2)
    p.append(b_cat2)

    # Категорія 3: Атаки на доповнення (Padding)
    p.append(rect(510, 85, 220, 355, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=8))
    p.append(text(620, 115, "Оракули доповнення", size=13.5, bold=True, color="#ca8a04"))
    b_cat3, _, _ = textbox(620, 265, [
        "• Атака Блейхенбахера",
        "  (PKCS#1 v1.5 oracle)",
        "• Атака Мангера",
        "  (помилки в OAEP)",
        "• Небезпека сырого RSA",
        "  без доповнення:",
        "  мультиплікативність",
        "  c₁ · c₂ = (m₁m₂)ᵉ mod N"
    ], size=11.5, pad=8, fill="#ffffff", stroke="#fef08a", sw=1.2)
    p.append(b_cat3)

    # Категорія 4: Побічні канали та реалізація
    p.append(rect(750, 85, 220, 355, fill="#f8fafc", stroke="#475569", sw=1.5, rx=8))
    p.append(text(860, 115, "Побічні канали (Side-Channel)", size=13.5, bold=True, color="#334155"))
    b_cat4, _, _ = textbox(860, 265, [
        "• Часові атаки (Timing)",
        "  (коригування Монтгомері)",
        "• Аналіз потужності",
        "  (SPA / DPA витоки)",
        "• Помилки CRT (Bellcore)",
        "  внесення збою у m_p",
        "  дає НСД(m_err - m, N) = q"
    ], size=11.5, pad=8, fill="#ffffff", stroke="#cbd5e1", sw=1.2)
    p.append(b_cat4)

    render(os.path.join(OUT, "rsa-attack-vectors.svg"), W, H,
           *p, title="Вектори атак на криптосистему RSA")


if __name__ == "__main__":
    fig_rsa_encryption_flow()
    fig_rsa_trapdoor_permutation()
    fig_rsa_crt_speedup()
    fig_rsa_attack_vectors()
    print("All RSA figures generated successfully.")
