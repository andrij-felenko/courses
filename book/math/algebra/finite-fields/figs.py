# -*- coding: utf-8 -*-
"""Фігури до статті «Скінченні поля»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Класифікація та структура скінченних полів GF(q)
# ─────────────────────────────────────────────────────────────────────────────
def fig_gf_classification():
    W, H = 840, 480
    frby = []

    # Заголовок зверху
    frby.append(text(W / 2, 28, "Класифікація та алгебраїчна побудова скінченних полів GF(q)", size=15, bold=True, color=INK))

    # Лівий блок: Прості поля GF(p)
    frby.append(rect(40, 60, 360, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(220, 88, "Прості поля: GF(p) ≅ ℤ/pℤ", size=14, bold=True, color=INK))
    frby.append(line(50, 100, 390, 100, color=LINE, sw=1))

    b1, _, _ = textbox(220, 140, "Кількість елементів: q = p\n(p — просте число: 2, 3, 5, 7, 11...)", size=12, pad=8, fill="#eff6ff", stroke=NEG, sw=1.2)
    frby.append(b1)

    b2, _, _ = textbox(220, 220, "Арифметика за модулем p:\n• Додавання: (a + b) mod p\n• Множення: (a · b) mod p\n• Обернення: розширений алгоритм Евкліда", size=12, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.2)
    frby.append(b2)

    b3, _, _ = textbox(220, 310, "Характеристика поля: char(F) = p\np · 1 = 1 + 1 + ... + 1 = 0", size=12, pad=8, fill="#fefce8", stroke="#ca8a04", sw=1.2)
    frby.append(b3)

    b4, _, _ = textbox(220, 395, "Мультиплікативна група:\n(ℤ/pℤ)* ≅ C_{p-1} (циклічна група)", size=12, pad=8, fill="#fdf2f8", stroke=POS, sw=1.2)
    frby.append(b4)

    # Центральна стрілка розширення
    frby.append(arrow(410, 255, 450, 255, color=FIELD, sw=2.5))
    frby.append(text(430, 235, "F[x]/(P)", size=11, bold=True, color=FIELD))
    frby.append(text(430, 280, "степінь n", size=10, color=MUTED))

    # Правий блок: Розширення полів GF(p^n)
    frby.append(rect(460, 60, 340, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(630, 88, "Поля розширення: GF(pⁿ) ≅ GF(p)[x]/(P(x))", size=14, bold=True, color=INK))
    frby.append(line(470, 100, 790, 100, color=LINE, sw=1))

    b5, _, _ = textbox(630, 140, "Кількість елементів: q = pⁿ\n(векторний простір розмірності n над GF(p))", size=12, pad=8, fill="#eff6ff", stroke=NEG, sw=1.2)
    frby.append(b5)

    b6, _, _ = textbox(630, 220, "Поліноміальна арифметика mod P(x):\n• Елементи: a_{n-1}x^{n-1} + ... + a₁x + a₀\n• P(x) — незвідний многочлен степеня n\n• Множення: (a(x) · b(x)) mod P(x)", size=12, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.2)
    frby.append(b6)

    b7, _, _ = textbox(630, 310, "Двійкові поля GF(2ⁿ) (p = 2):\n• Додавання/віднімання = XOR (без переносу)\n• Ідеальні для цифрових мікропроцесорів", size=12, pad=8, fill="#fefce8", stroke="#ca8a04", sw=1.2)
    frby.append(b7)

    b8, _, _ = textbox(630, 395, "Мультиплікативна група:\nGF(pⁿ)* ≅ C_{pⁿ-1} (циклічна порядку q-1)", size=12, pad=8, fill="#fdf2f8", stroke=POS, sw=1.2)
    frby.append(b8)

    render(os.path.join(OUT, "gf-hierarchy-classification.svg"), W, H, *frby,
           title="Класифікація та алгебраїчна побудова скінченних полів GF(q)")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Циклічна структура мультиплікативної групи GF(2^3)*
# ─────────────────────────────────────────────────────────────────────────────
def fig_multiplicative_cyclic():
    W, H = 840, 520
    frby = []

    frby.append(text(W / 2, 28, "Циклічна група GF(2³)* ≅ C₇ за модулем P(x) = x³ + x + 1", size=15, bold=True, color=INK))

    cx, cy, R = 420, 265, 160

    # Велике коло групи
    frby.append(circle(cx, cy, R, fill="none", stroke=LINE, sw=1.5))

    # Центральний блок: властивості
    b_c, _, _ = textbox(cx, cy, "Поле GF(2³) = GF(8)\nТвірна α = x\nПорядок групи = 7\nα⁷ = 1", size=12, pad=8, fill="#f8fafc", stroke=FIELD, sw=1.5)
    frby.append(b_c)

    # 7 точок на колі для C_7
    points = [
        ("α⁰ = 1", "001", "1", 0),
        ("α¹ = x", "010", "x", 1),
        ("α² = x²", "100", "x²", 2),
        ("α³ = x + 1", "011", "x+1", 3),
        ("α⁴ = x² + x", "110", "x²+x", 4),
        ("α⁵ = x² + x + 1", "111", "x²+x+1", 5),
        ("α⁶ = x² + 1", "101", "x²+1", 6),
    ]

    for label_pow, bits, poly, k in points:
        angle = -math.pi / 2 + k * (2 * math.pi / 7)
        px = cx + R * math.cos(angle)
        py = cy + R * math.sin(angle)

        # Точка на колі
        frby.append(circle(px, py, 6, fill=FIELD, stroke=INK, sw=1.5))

        # Виноска назовні
        tx = cx + (R + 58) * math.cos(angle)
        ty = cy + (R + 42) * math.sin(angle)

        box_str = f"{label_pow}\nБіти: {bits}"
        tb, _, _ = textbox(tx, ty, box_str, size=11, pad=5, fill="#eff6ff", stroke=NEG, sw=1.2)
        frby.append(tb)

        # Стрілка переходу до наступного степеня
        next_k = (k + 1) % 7
        next_angle = -math.pi / 2 + next_k * (2 * math.pi / 7)

        # Стрілка на дузі
        a_start_x = cx + (R + 8) * math.cos(angle + 0.15)
        a_start_y = cy + (R + 8) * math.sin(angle + 0.15)
        a_end_x = cx + (R + 8) * math.cos(next_angle - 0.15)
        a_end_y = cy + (R + 8) * math.sin(next_angle - 0.15)
        frby.append(arrow(a_start_x, a_start_y, a_end_x, a_end_y, color=POS, sw=1.5))

    render(os.path.join(OUT, "multiplicative-cyclic-group.svg"), W, H, *frby,
           title="Циклічна мультиплікативна група GF(2^3)* з генератором альфа = x")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Конвеєр S-Box у стандарті AES над полем GF(2^8)
# ─────────────────────────────────────────────────────────────────────────────
def fig_aes_sbox():
    W, H = 840, 440
    frby = []

    frby.append(text(W / 2, 28, "Алгебраїчна побудова AES S-Box над полем GF(2⁸)", size=15, bold=True, color=INK))

    # Крок 1: Вхідний байт
    b1, _, _ = textbox(130, 110, "Вхідний байт\nA ∈ GF(2⁸)\n(8-бітне значення)", size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    frby.append(b1)

    frby.append(arrow(210, 110, 270, 110, color=INK, sw=1.8))
    frby.append(text(240, 98, "A", size=11, color=MUTED))

    # Крок 2: Мультиплікативне обернення в GF(2^8)
    b2, _, _ = textbox(420, 110, "1. Нелінійне обернення в GF(2⁸):\nB = A⁻¹ = A²⁵⁴ mod P(x)\nде P(x) = x⁸ + x⁴ + x³ + x + 1 (0x11B)\n(для A = 0 визначається 0⁻¹ = 0)", size=12, pad=10, fill="#eff6ff", stroke=NEG, sw=1.2)
    frby.append(b2)

    frby.append(arrow(570, 110, 630, 110, color=INK, sw=1.8))
    frby.append(text(600, 98, "B = A⁻¹", size=11, color=NEG))

    # Крок 3: Вектор бітів
    b3, _, _ = textbox(720, 110, "Вектор бітів\nB = (b₀..b₇)ᵀ", size=12, pad=10, fill="#f8fafc", stroke=LINE, sw=1.5)
    frby.append(b3)

    # Вертикальна стрілка вниз
    frby.append(arrow(720, 160, 720, 210, color=INK, sw=1.8))

    # Крок 4: Афінне перетворення над GF(2)
    b4, _, _ = textbox(480, 270, "2. Афінне перетворення над GF(2):\nS = M · B ⊕ c\nде M — циклічна матриця 8×8, c = 0x63 (01100011₂)\nРуйнує прості алгебраїчні структури обернення", size=12, pad=10, fill="#fefce8", stroke="#ca8a04", sw=1.5)
    frby.append(b4)

    frby.append(arrow(670, 270, 720, 240, color=INK, sw=1.8))

    # Крок 5: Результат S-Box
    frby.append(arrow(300, 270, 230, 270, color=FIELD, sw=2.0))
    b5, _, _ = textbox(130, 270, "Вихідний байт S-Box\nS(A) ∈ {0..255}\n(Максимальна нелінійність)", size=12, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frby.append(b5)

    # Пояснювальний підвал
    b_foot, _, _ = textbox(W / 2, 385, "Чому саме GF(2⁸): обернення B = A⁻¹ гарантує максимальну стійкість до лінійного та диференціального криптоаналізу,\nа афінний зсув M·B ⊕ c захищає від атак на основі чистої алгебраїчної інтерполяції.", size=11, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.0)
    frby.append(b_foot)

    render(os.path.join(OUT, "aes-sbox-pipeline.svg"), W, H, *frby,
           title="Конвеєр обчислення байтового S-box у шифрі AES через поле Галуа GF(2^8)")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Кодування та виправлення помилок Ріда — Соломона
# ─────────────────────────────────────────────────────────────────────────────
def fig_reed_solomon():
    W, H = 840, 460
    frby = []

    frby.append(text(W / 2, 28, "Кодування та відновлення даних Ріда — Соломона над полем GF(2⁸)", size=15, bold=True, color=INK))

    # 1. Вхідні дані
    b1, _, _ = textbox(140, 95, "Блок даних k байтів\n(d₀, d₁, ..., d_{k-1})\nМногочлен: D(x) = ∑ d_i xⁱ", size=12, pad=8, fill="#f8fafc", stroke=LINE, sw=1.5)
    frby.append(b1)

    # 2. Додавання контрольних символів
    b2, _, _ = textbox(450, 95, "Генераторний многочлен g(x) = ∏ (x - αⁱ)\nДілення: x^{2t} · D(x) = q(x)·g(x) + R(x)\nКонтрольні байти: P(x) = R(x) (2t байтів)", size=12, pad=8, fill="#eff6ff", stroke=NEG, sw=1.5)
    frby.append(b2)

    frby.append(arrow(245, 95, 305, 95, color=INK, sw=1.8))
    frby.append(text(275, 83, "D(x)", size=11, color=MUTED))

    # 3. Передане кодове слово n = k + 2t
    b3, _, _ = textbox(710, 95, "Кодове слово n байтів\n[ Дані (k) | Перевірка (2t) ]\nC(x) = D(x)·x^{2t} + R(x)", size=12, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frby.append(b3)

    frby.append(arrow(595, 95, 615, 95, color=INK, sw=1.8))

    # Передача каналом зв'язку (помилки)
    frby.append(arrow(710, 150, 710, 200, color=POS, sw=1.8))
    frby.append(text(765, 175, "Шум / спотворення\nдо t байтів", size=10, color=POS))

    # 4. Прийняте слово
    b4, _, _ = textbox(710, 260, "Прийняте слово\nта синдроми S_j\nS_j = C_rec(αʲ)", size=12, pad=8, fill="#fef2f2", stroke=POS, sw=1.5)
    frby.append(b4)

    # 5. Алгоритм Берлекампа — Мессі / Евкліда
    b5, _, _ = textbox(430, 260, "Локалізація та оцінка помилок:\n• Многочлен локаторів Λ(x) (Берлекамп — Мессі)\n• Знаходження коренів Λ(x) (пошук Чіня)\n• Обчислення величин помилок (алгоритм Форні)", size=12, pad=8, fill="#fefce8", stroke="#ca8a04", sw=1.5)
    frby.append(b5)

    frby.append(arrow(620, 260, 595, 260, color=INK, sw=1.8))
    frby.append(text(608, 244, "S_j ≠ 0", size=11, color=POS))

    # 6. Відновлені вихідні дані
    b6, _, _ = textbox(130, 260, "100% відновлені дані\n(d₀, d₁, ..., d_{k-1})\nБез жодної втрати", size=12, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frby.append(b6)

    frby.append(arrow(260, 260, 235, 260, color=FIELD, sw=2.0))
    frby.append(text(248, 244, "Виправлено", size=10, bold=True, color=FIELD))

    # Підвал
    b_foot, _, _ = textbox(W / 2, 385, "Властивість коду Ріда — Соломона над полем Галуа: досягає теоретичної межі Сінглтона d = n - k + 1,\nдозволяючи гарантовано виправити до t = (n - k)/2 довільно пошкоджених байтів у блоці.", size=11, pad=8, fill="#f8fafc", stroke=MUTED, sw=1.0)
    frby.append(b_foot)

    render(os.path.join(OUT, "reed-solomon-encoding.svg"), W, H, *frby,
           title="Принцип кодування та виправлення помилок Ріда — Соломона над полем GF(2^8)")


if __name__ == "__main__":
    fig_gf_classification()
    fig_multiplicative_cyclic()
    fig_aes_sbox()
    fig_reed_solomon()
    print("Всі 4 фігури згенеровано успішно.")
