# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)

def fig_nonce_reuse():
    w, h = 820, 430
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Катастрофа повторного використання Nonce у потоковому шифрі", size=16, bold=True))

    # Top Left: Message 1
    frags.append(rect(30, 55, 360, 140, fill="#f8fafc", stroke=LINE, sw=1.5))
    frags.append(text(210, 78, "Повідомлення 1 (Передача №1)", size=13, bold=True))
    frags.append(fitbox(45, 95, 150, 40, "Відкритий текст P₁", size=12, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(225, 95, 150, 40, "Гамма S(K, Nonce)", size=12, fill="#fef3c7", stroke="#d97706"))
    frags.append(text(202, 120, "⊕", size=18, bold=True))
    frags.append(arrow(210, 140, 210, 160, color=LINE, sw=1.5))
    frags.append(fitbox(110, 162, 200, 26, "Шифротекст C₁ = P₁ ⊕ S", size=11, fill="#eff6ff", stroke=NEG, bold=True))

    # Top Right: Message 2 (Same Nonce!)
    frags.append(rect(430, 55, 360, 140, fill="#fef2f2", stroke=POS, sw=1.5))
    frags.append(text(610, 78, "Повідомлення 2 (Той самий Nonce!)", size=13, bold=True, color=POS))
    frags.append(fitbox(445, 95, 150, 40, "Відкритий текст P₂", size=12, fill="#ffffff", stroke="#94a3b8"))
    frags.append(fitbox(625, 95, 150, 40, "Гамма S(K, Nonce)", size=12, fill="#fef3c7", stroke=POS, bold=True))
    frags.append(text(602, 120, "⊕", size=18, bold=True))
    frags.append(arrow(610, 140, 610, 160, color=LINE, sw=1.5))
    frags.append(fitbox(510, 162, 200, 26, "Шифротекст C₂ = P₂ ⊕ S", size=11, fill="#eff6ff", stroke=NEG, bold=True))

    # Middle Section: XOR elimination
    frags.append(arrow(210, 195, 340, 230, color=LINE, sw=1.5))
    frags.append(arrow(610, 195, 480, 230, color=LINE, sw=1.5))

    frags.append(rect(140, 230, 540, 75, fill="#fffbeb", stroke="#d97706", sw=1.8))
    frags.append(text(410, 255, "Знищення ключової гами через побітове додавання", size=13, bold=True, color="#92400e"))
    frags.append(text(410, 285, "C₁ ⊕ C₂ = (P₁ ⊕ S) ⊕ (P₂ ⊕ S) = P₁ ⊕ P₂", size=14, bold=True, color=INK))

    # Bottom Section: Attack vector
    frags.append(arrow(410, 305, 410, 335, color=POS, sw=1.8))
    frags.append(rect(60, 335, 700, 75, fill="#fef2f2", stroke=POS, sw=1.5))
    frags.append(text(410, 358, "Повне розкриття даних без знання секретного ключа K:", size=13, bold=True, color=POS))
    frags.append(text(410, 385, "Якщо відомий P₁ (наприклад, заголовок кадру), тоді P₂ = (C₁ ⊕ C₂) ⊕ P₁", size=13, color=INK))

    render(os.path.join(OUT_DIR, "nonce-reuse-xor.svg"), w, h, *frags)

def fig_timing_attack():
    w, h = 840, 450
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Анатомія таймінг-атаки: memcmp() проти захищеного порівняння", size=16, bold=True))

    # Top Track: Vulnerable memcmp
    frags.append(rect(25, 55, 790, 165, fill="#fef2f2", stroke=POS, sw=1.5))
    frags.append(text(190, 78, "Вразливий підхід: memcmp() з раннім виходом", size=13, bold=True, color=POS))

    # Visualizing byte comparison
    frags.append(fitbox(45, 100, 100, 45, "Байт [0]\nЗбіг ✓", size=11, fill="#dcfce7", stroke=FIELD))
    frags.append(arrow(145, 122, 175, 122, color=LINE, sw=1.5))
    frags.append(fitbox(175, 100, 100, 45, "Байт [1]\nЗбіг ✓", size=11, fill="#dcfce7", stroke=FIELD))
    frags.append(arrow(275, 122, 305, 122, color=LINE, sw=1.5))
    frags.append(fitbox(305, 100, 100, 45, "Байт [2]\nРозбіжність ✗", size=11, fill="#fee2e2", stroke=POS))
    frags.append(arrow(405, 122, 445, 122, color=POS, sw=1.8))
    frags.append(fitbox(445, 100, 150, 45, "Ранній return != 0\n(вихід з циклу)", size=11, fill="#ffffff", stroke=POS, bold=True))

    # Attack measurement
    frags.append(fitbox(615, 95, 185, 55, "Час = T₀ + 3·Δt\nВитік довжини префікса!", size=11, fill="#fee2e2", stroke=POS, bold=True, color=POS))
    frags.append(text(420, 185, "Нападник перебирає 256 варіантів на кожен байт і знаходить 16 байтів за 4096 спроб замість 2¹²⁸", size=12, italic=True, color="#991b1b"))

    # Bottom Track: Constant-Time
    frags.append(rect(25, 245, 790, 180, fill="#f0fdf4", stroke=FIELD, sw=1.5))
    frags.append(text(210, 268, "Безпечний підхід: константний час (crypto_verify16)", size=13, bold=True, color=FIELD))

    # Loop visualization
    frags.append(fitbox(45, 290, 150, 50, "Байт [0]\ndiff |= a[0] ^ b[0]", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(195, 315, 225, 315, color=LINE, sw=1.5))
    frags.append(fitbox(225, 290, 150, 50, "Байт [1..14]\ndiff |= a[i] ^ b[i]", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(375, 315, 405, 315, color=LINE, sw=1.5))
    frags.append(fitbox(405, 290, 150, 50, "Байт [15]\ndiff |= a[15] ^ b[15]", size=11, fill="#ffffff", stroke=LINE))
    frags.append(arrow(555, 315, 590, 315, color=FIELD, sw=1.8))
    frags.append(fitbox(590, 290, 210, 50, "return (diff == 0)\nЗавжди 16 ітерацій", size=11, fill="#dcfce7", stroke=FIELD, bold=True))

    frags.append(text(420, 380, "Час виконання T_const суворо однаковий незалежно від кількості збігів і значень байтів", size=12, bold=True, color="#166534"))
    frags.append(text(420, 405, "Жодної кореляції між часом відгуку пристрою та правильністю вгаданих байтів", size=11, italic=True, color=INK))

    render(os.path.join(OUT_DIR, "timing-attack-early-exit.svg"), w, h, *frags)

def fig_aead_packet():
    w, h = 860, 480
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Безпечний кадр AEAD: структура та порядок обробки", size=16, bold=True))

    # Frame Layout
    frags.append(rect(40, 55, 780, 85, fill="#f8fafc", stroke=LINE, sw=1.5))
    frags.append(text(430, 75, "Структура захищеного криптографічного пакета в ефірі", size=13, bold=True))

    frags.append(fitbox(55, 90, 220, 38, "Заголовок + Nonce / Seq\n(Відкриті, автентифіковані AAD)", size=11, fill="#e0f2fe", stroke="#0284c7"))
    frags.append(fitbox(285, 90, 300, 38, "Шифротекст (Ciphertext)\n(Зашифровані корисні дані)", size=11, fill="#fef3c7", stroke="#d97706"))
    frags.append(fitbox(595, 90, 210, 38, "Автентифікаційний тег (Tag)\n(16 байтів Poly1305 / GHASH)", size=11, fill="#dcfce7", stroke=FIELD, bold=True))

    # Pipeline Section
    frags.append(rect(40, 160, 780, 295, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(430, 185, "Порядок безпечної обробки на стороні приймача", size=13, bold=True))

    # Step 1
    frags.append(fitbox(60, 210, 200, 60, "1. Перевірка Nonce / Seq\nNonce > Last_Valid_Nonce\n(Захист від повтору)", size=11, fill="#f1f5f9", stroke=LINE))
    frags.append(arrow(260, 240, 290, 240, color=LINE, sw=1.5))

    # Step 2
    frags.append(fitbox(290, 210, 240, 60, "2. Обчислення тегу MAC\n над (AAD + Ciphertext)\nна ключі автентифікації", size=11, fill="#f1f5f9", stroke=LINE))
    frags.append(arrow(530, 240, 560, 240, color=LINE, sw=1.5))

    # Step 3
    frags.append(fitbox(560, 210, 240, 60, "3. Константне порівняння\nTag_calc == Tag_packet\n(Без раннього виходу!)", size=11, fill="#fef9c3", stroke="#ca8a04", bold=True))

    # Branches
    frags.append(arrow(680, 270, 680, 310, color=LINE, sw=1.5))

    # Valid branch
    frags.append(fitbox(460, 320, 340, 60, "4а. Тег дійсний:\nРозшифрувати Ciphertext та\nпередати корисне навантаження в логіку", size=11, fill="#dcfce7", stroke=FIELD, bold=True))

    # Invalid branch
    frags.append(arrow(600, 270, 300, 320, color=POS, sw=1.5))
    frags.append(fitbox(80, 320, 340, 60, "4б. Тег не зійшовся:\nНЕГАЙНО ВІДХИЛИТИ кадр!\nНе розшифровувати, не виконувати", size=11, fill="#fee2e2", stroke=POS, bold=True, color=POS))

    # Golden rule at the bottom
    frags.append(rect(60, 400, 740, 40, fill="#f8fafc", stroke="#64748b", sw=1.2))
    frags.append(text(430, 425, "Золоте правило: жоден байт шифротексту не розшифровується до успішної перевірки автентичності!", size=11, bold=True, color=INK))

    render(os.path.join(OUT_DIR, "aead-packet-structure.svg"), w, h, *frags)

if __name__ == "__main__":
    fig_nonce_reuse()
    fig_timing_attack()
    fig_aead_packet()
    print("Figures generated successfully.")
