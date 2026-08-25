# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Криптографічні гешфункції'."""
import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def draw_merkle_damgard():
    path = os.path.join(IMG_DIR, "fig-merkle-damgard.svg")
    w, h = 820, 310

    frags = []

    # Заголовок секцій
    frags.append(text(410, 24, "Конструкція Меркла–Дамґорда та функція стиснення Девіса–Мейєра", size=15, bold=True))

    # Верхній потік: ланцюг Меркла-Дамґорда
    frags.append(rect(20, 48, 780, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(35, 68, "Ланцюг обробки блоків", size=12, bold=True, anchor="start", color=MUTED))

    # IV
    iv_box, _, _ = textbox(70, 108, "IV\n256 бітів", size=11, bold=True, fill="#e0f2fe", stroke="#0284c7")
    frags.append(iv_box)
    frags.append(arrow(110, 108, 155, 108, color=LINE, sw=1.5))
    frags.append(text(132, 100, "h₀", size=11, bold=True, color=INK))

    # Блок повідомлення M0
    m0_box, _, _ = textbox(190, 72, "Блок M₀ (512 бітів)", size=10, fill="#dcfce7", stroke="#16a34a")
    frags.append(m0_box)
    frags.append(arrow(190, 84, 190, 96, color=LINE, sw=1.5))

    # Функція стиснення f(1)
    f1_box, _, _ = textbox(190, 118, "Функція f\nстиснення", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(f1_box)

    frags.append(arrow(235, 118, 295, 118, color=LINE, sw=1.5))
    frags.append(text(265, 110, "h₁", size=11, bold=True, color=INK))

    # Блок повідомлення M1
    m1_box, _, _ = textbox(330, 72, "Блок M₁ (512 бітів)", size=10, fill="#dcfce7", stroke="#16a34a")
    frags.append(m1_box)
    frags.append(arrow(330, 84, 330, 96, color=LINE, sw=1.5))

    # Функція стиснення f(2)
    f2_box, _, _ = textbox(330, 118, "Функція f\nстиснення", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(f2_box)

    frags.append(arrow(375, 118, 435, 118, color=LINE, sw=1.5))
    frags.append(text(405, 110, "...", size=13, bold=True, color=MUTED))

    frags.append(arrow(435, 118, 485, 118, color=LINE, sw=1.5))
    frags.append(text(460, 110, "hₙ₋₁", size=11, bold=True, color=INK))

    # Останній блок з доповненням
    mn_box, _, _ = textbox(540, 72, "Mₙ₋₁ || 10* || Довжина", size=10, bold=True, fill="#fef3c7", stroke="#d97706")
    frags.append(mn_box)
    frags.append(arrow(540, 84, 540, 96, color=LINE, sw=1.5))

    # Функція стиснення f(n)
    fn_box, _, _ = textbox(540, 118, "Функція f\nстиснення", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(fn_box)

    frags.append(arrow(595, 118, 655, 118, color=LINE, sw=1.5))
    frags.append(text(625, 110, "hₙ", size=11, bold=True, color=INK))

    # Підсумковий геш
    out_box, _, _ = textbox(720, 118, "Підсумковий геш\n(256 бітів)", size=11, bold=True, fill="#fee2e2", stroke="#dc2626")
    frags.append(out_box)

    # Нижня частина: деталізація функції стиснення Девіса-Мейєра всередині f
    frags.append(rect(20, 172, 780, 125, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    frags.append(text(35, 192, "Внутрішня будова функції Девіса–Мейєра: f(hᵢ₋₁, Mᵢ) = E(Mᵢ, hᵢ₋₁) ⊕ hᵢ₋₁", size=12, bold=True, anchor="start", color=INK))

    # Вхід стану h_{i-1}
    hin_box, _, _ = textbox(110, 240, "Стан hᵢ₋₁\n(відкритий текст)", size=11, fill="#e0f2fe", stroke="#0284c7")
    frags.append(hin_box)

    # Розгалуження h_{i-1}
    frags.append(circle(200, 240, 3.5, fill=LINE, stroke=LINE))
    frags.append(line(170, 240, 200, 240, color=LINE, sw=1.5))
    frags.append(arrow(200, 240, 280, 240, color=LINE, sw=1.5))

    # Лінія прямого зв'язку (feed-forward)
    frags.append(line(200, 240, 200, 275, color=LINE, sw=1.5))
    frags.append(line(200, 275, 520, 275, color=LINE, sw=1.5))
    frags.append(arrow(520, 275, 520, 252, color=LINE, sw=1.5))
    frags.append(text(360, 287, "Прямий зв'язок (feed-forward) робить блоковий шифр незворотним", size=10, italic=True, color=MUTED))

    # Вхід повідомлення M_i (як ключ)
    m_key_box, _, _ = textbox(360, 198, "Блок Mᵢ (використовується як ключ шифрування)", size=10, fill="#dcfce7", stroke="#16a34a")
    frags.append(m_key_box)
    frags.append(arrow(360, 210, 360, 222, color=LINE, sw=1.5))

    # Блоковий шифр E
    cipher_box, _, _ = textbox(360, 240, "Блоковий шифр E\n(наприклад, раунди SHA-256)", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(cipher_box)

    frags.append(arrow(450, 240, 510, 240, color=LINE, sw=1.5))

    # Елемент XOR
    frags.append(plus(520, 240, r=10))

    frags.append(arrow(532, 240, 620, 240, color=LINE, sw=1.5))

    # Вихідний стан h_i
    hout_box, _, _ = textbox(690, 240, "Новий стан hᵢ\n(наступне chaining value)", size=11, bold=True, fill="#e0f2fe", stroke="#0284c7")
    frags.append(hout_box)

    render(path, w, h, *frags)


def draw_length_extension():
    path = os.path.join(IMG_DIR, "fig-length-extension.svg")
    w, h = 820, 290

    frags = []

    frags.append(text(410, 24, "Атака подовженням повідомлення на наївний префіксний MAC", size=15, bold=True))

    # 1. Легітимне обчислення
    frags.append(rect(20, 48, 780, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(35, 68, "1. Сервер обчислює легітимний токен: H(Secret || Data)", size=12, bold=True, anchor="start", color="#1e293b"))

    sec_box, _, _ = textbox(85, 105, "Secret\n(таємний)", size=10, fill="#fee2e2", stroke="#dc2626")
    frags.append(sec_box)

    data_box, _, _ = textbox(180, 105, "Data\n'user=alice'", size=10, fill="#dbeafe", stroke="#2563eb")
    frags.append(data_box)

    pad1_box, _, _ = textbox(285, 105, "Padding 1\n(0x80+нулі+len)", size=10, fill="#fef3c7", stroke="#d97706")
    frags.append(pad1_box)

    frags.append(arrow(350, 105, 395, 105, color=LINE, sw=1.5))

    md_box, _, _ = textbox(460, 105, "Функція стиснення MD\n(стан після блоку)", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(md_box)

    frags.append(arrow(545, 105, 595, 105, color=LINE, sw=1.5))

    tok_box, _, _ = textbox(685, 105, "Токен = Стан h₁\n(публічно передається)", size=11, bold=True, fill="#bbf7d0", stroke="#16a34a")
    frags.append(tok_box)

    # 2. Атака зловмисника
    frags.append(rect(20, 165, 780, 115, fill="#fff1f2", stroke="#fca5a5", sw=1.2, rx=8))
    frags.append(text(35, 185, "2. Зловмисник формує підроблений запит без знання Secret", size=12, bold=True, anchor="start", color="#991b1b"))

    # Стан як новий IV
    state_box, _, _ = textbox(110, 230, "Взятий стан h₁\n(як новий IV')", size=10, bold=True, fill="#bbf7d0", stroke="#16a34a")
    frags.append(state_box)

    frags.append(arrow(180, 230, 235, 230, color=LINE, sw=1.5))

    # Додані дані
    extra_box, _, _ = textbox(325, 230, "Extra Data: '&role=admin'\n+ Padding 2 (з урахуванням заг. довжини)", size=10, fill="#fef08a", stroke="#ca8a04")
    frags.append(extra_box)

    frags.append(arrow(455, 230, 500, 230, color=LINE, sw=1.5))

    ext_md_box, _, _ = textbox(565, 230, "Функція f\n(наступний крок)", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(ext_md_box)

    frags.append(arrow(630, 230, 680, 230, color=LINE, sw=1.5))

    forge_box, _, _ = textbox(735, 230, "Новий валідний\nтокен h₂ !", size=11, bold=True, fill="#fecaca", stroke="#dc2626")
    frags.append(forge_box)

    render(path, w, h, *frags)


def draw_sponge_construction():
    path = os.path.join(IMG_DIR, "fig-sponge-construction.svg")
    w, h = 820, 310

    frags = []

    frags.append(text(410, 24, "Губкова конструкція (Sponge) в алгоритмі Keccak / SHA-3", size=15, bold=True))

    # Контейнер стану b = r + c
    frags.append(rect(20, 50, 780, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    # Фаза Absorbing
    frags.append(rect(30, 65, 370, 215, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(215, 85, "Фаза вбирання (Absorbing)", size=13, bold=True, color="#15803d"))

    # Повідомлення P0
    p0_box, _, _ = textbox(95, 115, "Блок P₀ (r бітів)", size=10, fill="#dcfce7", stroke="#16a34a")
    frags.append(p0_box)
    frags.append(arrow(95, 128, 95, 142, color=LINE, sw=1.5))

    # Стан 1: Rate & Capacity
    frags.append(rect(60, 155, 70, 35, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    frags.append(text(95, 177, "Rate r", size=10, bold=True, color="#1e40af"))
    frags.append(plus(95, 148, r=7))

    frags.append(rect(60, 195, 70, 45, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    frags.append(text(95, 222, "Capacity c\n(закрита)", size=9, bold=True, color="#991b1b"))

    frags.append(arrow(135, 185, 175, 185, color=LINE, sw=1.5))

    # Перестановка f
    f1_box, _, _ = textbox(205, 185, "Keccak-f\n[1600]", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(f1_box)

    frags.append(arrow(240, 185, 280, 185, color=LINE, sw=1.5))

    # Повідомлення P1
    p1_box, _, _ = textbox(315, 115, "Блок P₁ (r бітів)", size=10, fill="#dcfce7", stroke="#16a34a")
    frags.append(p1_box)
    frags.append(arrow(315, 128, 315, 142, color=LINE, sw=1.5))

    frags.append(rect(280, 155, 70, 35, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    frags.append(text(315, 177, "Rate r", size=10, bold=True, color="#1e40af"))
    frags.append(plus(315, 148, r=7))

    frags.append(rect(280, 195, 70, 45, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    frags.append(text(315, 222, "Capacity c\n(закрита)", size=9, bold=True, color="#991b1b"))

    # Перехід до фази Squeezing
    frags.append(arrow(360, 185, 415, 185, color=LINE, sw=1.8))

    # Фаза Squeezing
    frags.append(rect(415, 65, 375, 215, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    frags.append(text(602, 85, "Фаза витискання (Squeezing)", size=13, bold=True, color="#1d4ed8"))

    # Стан 3
    frags.append(rect(460, 155, 70, 35, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    frags.append(text(495, 177, "Rate r", size=10, bold=True, color="#1e40af"))

    frags.append(rect(460, 195, 70, 45, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    frags.append(text(495, 222, "Capacity c\n(ізольована)", size=9, bold=True, color="#991b1b"))

    # Вихід Z0
    frags.append(arrow(495, 155, 495, 130, color=LINE, sw=1.5))
    z0_box, _, _ = textbox(495, 115, "Вихід Z₀ (r бітів)", size=10, bold=True, fill="#fef08a", stroke="#ca8a04")
    frags.append(z0_box)

    frags.append(arrow(535, 185, 575, 185, color=LINE, sw=1.5))

    # Перестановка f2
    f2_box, _, _ = textbox(605, 185, "Keccak-f\n[1600]", size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(f2_box)

    frags.append(arrow(640, 185, 680, 185, color=LINE, sw=1.5))

    # Стан 4
    frags.append(rect(680, 155, 70, 35, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    frags.append(text(715, 177, "Rate r", size=10, bold=True, color="#1e40af"))

    frags.append(rect(680, 195, 70, 45, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    frags.append(text(715, 222, "Capacity c\n(ізольована)", size=9, bold=True, color="#991b1b"))

    # Вихід Z1
    frags.append(arrow(715, 155, 715, 130, color=LINE, sw=1.5))
    z1_box, _, _ = textbox(715, 115, "Вихід Z₁ (r бітів)", size=10, bold=True, fill="#fef08a", stroke="#ca8a04")
    frags.append(z1_box)

    frags.append(text(410, 292, "Безпека: Capacity c = 512 бітів ніколи не віддається назовні → захист від Length Extension", size=11, bold=True, color="#475569"))

    render(path, w, h, *frags)


def draw_blake3_tree():
    path = os.path.join(IMG_DIR, "fig-blake3-tree.svg")
    w, h = 820, 310

    frags = []

    frags.append(text(410, 24, "Деревоподібне хешування та паралелізм у BLAKE3", size=15, bold=True))

    # Контейнер
    frags.append(rect(20, 48, 780, 245, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    # Рівень чанків (1 KiB кожен)
    frags.append(text(35, 255, "Вхідні чанки:", size=10, bold=True, anchor="start", color=MUTED))

    c0_box, _, _ = textbox(120, 255, "Чанк 0 (1024 B)", size=10, fill="#f1f5f9", stroke="#64748b")
    c1_box, _, _ = textbox(280, 255, "Чанк 1 (1024 B)", size=10, fill="#f1f5f9", stroke="#64748b")
    c2_box, _, _ = textbox(470, 255, "Чанк 2 (1024 B)", size=10, fill="#f1f5f9", stroke="#64748b")
    c3_box, _, _ = textbox(630, 255, "Чанк 3 (1024 B)", size=10, fill="#f1f5f9", stroke="#64748b")
    frags.extend([c0_box, c1_box, c2_box, c3_box])

    # SIMD банер
    frags.append(rect(320, 280, 400, 16, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(520, 292, "Паралельне обчислення чанків інструкціями SIMD (AVX-512 / NEON)", size=9, bold=True, color="#1d4ed8"))

    # Стрілки від чанків до вузлів листя
    frags.append(arrow(120, 240, 120, 205, color=LINE, sw=1.5))
    frags.append(arrow(280, 240, 280, 205, color=LINE, sw=1.5))
    frags.append(arrow(470, 240, 470, 205, color=LINE, sw=1.5))
    frags.append(arrow(630, 240, 630, 205, color=LINE, sw=1.5))

    # Рівень листя дерева (32-байтні chaining values)
    l0_box, _, _ = textbox(120, 190, "CV 0 (32 B)", size=10, bold=True, fill="#dcfce7", stroke="#16a34a")
    l1_box, _, _ = textbox(280, 190, "CV 1 (32 B)", size=10, bold=True, fill="#dcfce7", stroke="#16a34a")
    l2_box, _, _ = textbox(470, 190, "CV 2 (32 B)", size=10, bold=True, fill="#dcfce7", stroke="#16a34a")
    l3_box, _, _ = textbox(630, 190, "CV 3 (32 B)", size=10, bold=True, fill="#dcfce7", stroke="#16a34a")
    frags.extend([l0_box, l1_box, l2_box, l3_box])

    # Стрілки до батьківських вузлів
    frags.append(arrow(120, 175, 185, 140, color=LINE, sw=1.5))
    frags.append(arrow(280, 175, 215, 140, color=LINE, sw=1.5))
    frags.append(arrow(470, 175, 535, 140, color=LINE, sw=1.5))
    frags.append(arrow(630, 175, 565, 140, color=LINE, sw=1.5))

    # Батьківські вузли
    p01_box, _, _ = textbox(200, 125, "Батьківський вузол P₀₁\ncompress(CV₀ || CV₁, PARENT)", size=10, bold=True, fill="#fef3c7", stroke="#d97706")
    p23_box, _, _ = textbox(550, 125, "Батьківський вузол P₂₃\ncompress(CV₂ || CV₃, PARENT)", size=10, bold=True, fill="#fef3c7", stroke="#d97706")
    frags.extend([p01_box, p23_box])

    # Стрілки до кореня
    frags.append(arrow(200, 105, 345, 80, color=LINE, sw=1.5))
    frags.append(arrow(550, 105, 405, 80, color=LINE, sw=1.5))

    # Кореневий вузол
    root_box, _, _ = textbox(375, 68, "Корінь (Root Node): compress(P₀₁ || P₂₃, ROOT)\nВихідний геш BLAKE3 (32 байти або XOF-потік)", size=11, bold=True, fill="#fee2e2", stroke="#dc2626")
    frags.append(root_box)

    render(path, w, h, *frags)


if __name__ == "__main__":
    draw_merkle_damgard()
    draw_length_extension()
    draw_sponge_construction()
    draw_blake3_tree()
    print("Фігури успішно згенеровано.")
