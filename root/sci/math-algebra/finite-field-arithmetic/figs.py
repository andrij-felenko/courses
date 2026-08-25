# -*- coding: utf-8 -*-
"""Фігури для теми «Скінченні поля (поля Галуа)» (book/algorithms/complexity-computability/finite-fields)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_field_classification():
    """fig1-field-classification.svg: Алгебраїчна ієрархія структур та місце скінченних полів."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Алгебраїчна ієрархія структур та місце скінченних полів Галуа GF(q)", size=16, bold=True, color="#1e293b"))

    # Гілка 1: Групи (ліворуч)
    b_g, _, _ = textbox(150, 90, "Групи (Group)\nАдитивна (G, +) чи Мультиплікативна (G, ·)\nЗамикання, асоціативність, 0/1, обернений", size=11, fill="#f1f5f9", stroke="#64748b")
    frags.append(b_g)

    # Гілка 2: Кільця (середина вгорі)
    b_r, _, _ = textbox(440, 90, "Кільця (Ring)\nДві операції (+, ·)\n(R, +) — абелева група, (R, ·) — моноід\nДистрибутивність: a·(b+c) = a·b + a·c", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_r)

    frags.append(line(240, 90, 330, 90, color="#94a3b8", sw=1.5))

    # Кільця многочленів та цілих чисел modulo n
    b_zn, _, _ = textbox(440, 180, "Комутативні кільця та кільця modulo n\nZ_n (цілі числа mod n), GF(p)[x] (многочлени)\nЯкщо n складене — є дільники нуля (2 · 4 = 0 mod 8)", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_zn)
    frags.append(line(440, 125, 440, 155, color=AMBER_S, sw=1.5))

    # Гілка 3: Поля (унизу)
    b_f, _, _ = textbox(440, 260, "Алгебраїчні поля (Field)\nВсі елементи крім 0 утворюють мультиплікативну абелеву групу\nДовільний елемент a ≠ 0 має унікальний обернений a⁻¹ (a · a⁻¹ = 1)", size=11, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_f)
    frags.append(line(440, 215, 440, 235, color=BLUE_S, sw=1.5))

    # Розгалуження Скінченні поля GF(q)
    b_gfp, _, _ = textbox(240, 350, "Прості поля GF(p)\nРозмір p — просте число\nЕлементи: Z_p = {0, 1, ..., p-1}\nАрифметика modulo p", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_gfp)

    b_gfpm, _, _ = textbox(640, 350, "Поля розширення GF(pᵐ)\nРозмір q = pᵐ (p — характеристика, m ≥ 1)\nФактор-кільце GF(p)[x] / (f(x))\nf(x) — незвідний многочлен степеня m", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_gfpm)

    frags.append(line(370, 290, 240, 320, color=GREEN_S, sw=1.5))
    frags.append(line(510, 290, 640, 320, color=PURPLE_S, sw=1.5))

    render(os.path.join(IMG, "fig1-field-classification.svg"), W, H, *frags)


def fig_gf2m_construction():
    """fig2-gf2m-construction.svg: Конструкція та двоїсте представлення елементів GF(2^m)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Конструкція поля GF(2ᵐ) та векторно-поліноміальне представлення", size=16, bold=True, color="#1e293b"))

    # Ліва колонка: Вхідний незвідний многочлен
    b_poly, _, _ = textbox(220, 100, "Незвідний многочлен f(x) степеня m\nGF(2)[x] / (f(x))\nПриклад AES: f(x) = x⁸ + x⁴ + x³ + x + 1", size=11, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_poly)

    # Права колонка: Операції в полі
    b_ops, _, _ = textbox(660, 100, "Арифметичні операції в GF(2ᵐ)\nДодавання: A(x) + B(x) mod 2  ⇒  XOR (^)\nМноження: (A(x) · B(x)) mod f(x)", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_ops)

    # Центральний блок: Еквівалентність 3 форм представлення
    frags.append(rect(60, 170, 760, 210, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(440, 195, "Три еквівалентні форми представлення елемента A ∈ GF(2ᵐ)", size=13, bold=True, color=BLUE_S))

    # 1. Поліноміальна форма
    b_f1, _, _ = textbox(200, 260, "1. Поліноміальна форма\nA(x) = aₘ₋₁xᵐ⁻¹ + ... + a₁x + a₀\naᵢ ∈ {0, 1}", size=11, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_f1)

    # 2. Векторна / Бітова форма
    b_f2, _, _ = textbox(440, 260, "2. Бітовий вектор (Integer)\na = (aₘ₋₁, aₘ₋₂, ..., a₁, a₀)₂\nm-бітне слово в пам'яті (uint8, uint32)", size=11, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_f2)

    # 3. Степінь примітивного елемента
    b_f3, _, _ = textbox(680, 260, "3. Мультиплікативна форма\nA = αᵏ (k ∈ {0, ..., 2ᵐ-2})\nα — корінь f(x), α²ᵐ⁻¹ = 1", size=11, fill="#ffffff", stroke=PURPLE_S)
    frags.append(b_f3)

    # Стрілки еквівалентності
    frags.append(line(290, 260, 330, 260, color="#64748b", sw=1.5))
    frags.append(line(545, 260, 580, 260, color="#64748b", sw=1.5))

    # Нижній підпис
    frags.append(text(440, 350, "Додавання виконується за 1 такт CPU через побітовий XOR (без переносу розрядів)\nМноження вимагає множення без переносу (clmul) та редукції за модулем f(x)", size=11, italic=True, color="#334155"))

    render(os.path.join(IMG, "fig2-gf2m-construction.svg"), W, H, *frags)


def fig_multiplicative_group_cycle():
    """fig3-multiplicative-group-cycle.svg: Циклічна структура групи GF(2^3)* з породжувальним α."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Циклічна мультиплікативна група GF(2³)★ породжена примітивним α (f(x) = x³ + x + 1)", size=15, bold=True, color="#1e293b"))

    # Таблиця елементів циклу у формі градуйованого кільця
    cx, cy, r = 320, 230, 130
    import math

    elements = [
        ("α⁰ = 1", "001", "1", 0),
        ("α¹ = x", "010", "x", 1),
        ("α² = x²", "100", "x²", 2),
        ("α³ = x+1", "011", "x + 1", 3),
        ("α⁴ = x²+x", "110", "x² + x", 4),
        ("α⁵ = x²+x+1", "111", "x² + x + 1", 5),
        ("α⁶ = x²+1", "101", "x² + 1", 6),
    ]

    n = len(elements)
    for i, (pow_str, vec_str, poly_str, idx) in enumerate(elements):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)

        fill_c = GREEN_F if i == 0 else (PURPLE_F if i == 1 else BLUE_F)
        stroke_c = GREEN_S if i == 0 else (PURPLE_S if i == 1 else BLUE_S)

        b, _, _ = textbox(x, y, f"{pow_str}\n[{vec_str}]", size=10, bold=True, fill=fill_c, stroke=stroke_c)
        frags.append(b)

        # Стрілка напрямку множення на α
        next_angle = 2 * math.pi * (i + 1) / n - math.pi / 2
        nx = cx + (r - 5) * math.cos(next_angle)
        ny = cy + (r - 5) * math.sin(next_angle)
        px = cx + (r - 5) * math.cos(angle)
        py = cy + (r - 5) * math.sin(angle)
        frags.append(line(px, py, nx, ny, color="#94a3b8", sw=1.5))

    # Права панель з поясненням редукції
    b_expl, _, _ = textbox(700, 220, "Правило степенів α в GF(2³):\nf(α) = α³ + α + 1 = 0  ⇒  α³ = α + 1\n\n• α⁰ = 1  [001]\n• α¹ = x  [010]\n• α² = x²  [100]\n• α³ = x + 1  [011]\n• α⁴ = x² + x  [110]\n• α⁵ = x³ + x² = x² + x + 1  [111]\n• α⁶ = x³ + x² + x = x² + 1  [101]\n• α⁷ = α · α⁶ = x³ + x = 1  [001] (Замикання!)", size=11, fill="#ffffff", stroke="#475569")
    frags.append(b_expl)

    render(os.path.join(IMG, "fig3-multiplicative-group-cycle.svg"), W, H, *frags)


def fig_reed_solomon_aes_apps():
    """fig4-reed-solomon-aes-apps.svg: Карта застосувань скінченних полів у кодуванні, криптографії та верифікації."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Практичні застосування скінченних полів Галуа в комп'ютерних науках", size=16, bold=True, color="#1e293b"))

    # Блок 1: Симетрична криптографія (AES S-Box)
    b_aes, _, _ = textbox(170, 120, "1. Симетрична криптографія\nAES (Advanced Encryption Standard)\nS-Box: Обернення у GF(2⁸)\nS(x) = Affine(x⁻¹) mod (x⁸+x⁴+x³+x+1)\nМаксимальна алгебраїчна нелінійність", size=11, fill=RED_F, stroke=RED_S)
    frags.append(b_aes)

    # Блок 2: Повадостійке кодування (Reed-Solomon)
    b_rs, _, _ = textbox(440, 120, "2. Завадостійке кодування\nКоди Ріда — Соломона (Reed-Solomon)\nОцінка многочленів над GF(2ᵐ)\nRAID-6, QR-коди, CD/DVD, супутники\nВиправлення t помилок за 2t паролів", size=11, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_rs)

    # Блок 3: Складність та ZK-доведення (Schwartz-Zippel, FRI, STARKs)
    b_zk, _, _ = textbox(710, 120, "3. Верифікація та ZK-Proof\nЛема Шварца — Ціппеля, STARKs\nТестування еквівалентності P(x) ≡ 0\nОцінка у випадковій точці з GF(q)\nЙмовірність помилки ≤ d / |GF(q)|", size=11, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_zk)

    # Блок 4: Криптографія на еліптичних кривих (ECC)
    b_ecc, _, _ = textbox(305, 300, "4. Асиметрична криптографія (ECC)\nЕліптичні криві y² = x³ + ax + b над GF(p) / GF(2ᵐ)\nECDSA, Ed25519, криптографія на ґратках\nОснова сучасного TLS/HTTPS та Bitcoin/Ethereum", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_ecc)

    # Блок 5: Розділення таємниці Шаміра (Secret Sharing)
    b_sss, _, _ = textbox(575, 300, "5. Порогові схеми Шаміра\n(k, n)-пороги розділення секрету\nІнтерполяція Лагранжа над GF(p)\nk частин відновлюють секрет P(0),\nk-1 частин не дають жодної інформації", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_sss)

    # Зв'язуючі лінії
    frags.append(line(260, 175, 305, 230, color="#94a3b8", sw=1.2))
    frags.append(line(440, 185, 575, 230, color="#94a3b8", sw=1.2))

    render(os.path.join(IMG, "fig4-reed-solomon-aes-apps.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_field_classification()
    fig_gf2m_construction()
    fig_multiplicative_group_cycle()
    fig_reed_solomon_aes_apps()
    print("Усі 4 фігури успішно згенеровано у теку img/")
