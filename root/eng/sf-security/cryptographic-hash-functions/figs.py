# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. fig-security-properties ───────────────────────────────────────────────
def fig_security_properties():
    W, H = 780, 310
    elems = []

    # Title / Header
    elems.append(text(W / 2, 25, "Три базові властивості безпеки криптографічного хеша", size=14, bold=True))

    # Box 1: Preimage Resistance
    b1, _, _ = textbox(135, 110, "1. Стійкість до прообразу\n(Preimage Resistance)", size=11, bold=True, fill="#fdfefe", stroke=INK, min_w=220)
    elems.append(b1)
    elems.append(rect(25, 145, 220, 115, fill="#ffffff", stroke=LINE, rx=6))
    elems.append(text(135, 168, "Дано:  y = H(x)", size=11, color=INK))
    elems.append(text(135, 192, "Шукаємо:  x'  так, що H(x') = y", size=10, color=MUTED))
    elems.append(text(135, 220, "Складність:  O(2ⁿ)", size=11, color=POS, bold=True))
    elems.append(text(135, 242, "(Сліпий перебір входу)", size=9, color=MUTED))

    # Box 2: Second Preimage Resistance
    b2, _, _ = textbox(390, 110, "2. Стійкість до 2-го прообразу\n(Second Preimage Resistance)", size=11, bold=True, fill="#fdfefe", stroke=INK, min_w=230)
    elems.append(b2)
    elems.append(rect(275, 145, 230, 115, fill="#ffffff", stroke=LINE, rx=6))
    elems.append(text(390, 168, "Дано:  відомий  x₁", size=11, color=INK))
    elems.append(text(390, 192, "Шукаємо:  x₂ ≠ x₁  так, що", size=10, color=MUTED))
    elems.append(text(390, 208, "H(x₂) = H(x₁)", size=10, color=INK))
    elems.append(text(390, 232, "Складність:  O(2ⁿ)", size=11, color=POS, bold=True))
    elems.append(text(390, 248, "(Підміна повідомлення)", size=9, color=MUTED))

    # Box 3: Collision Resistance
    b3, _, _ = textbox(655, 110, "3. Стійкість до колізій\n(Collision Resistance)", size=11, bold=True, fill="#fdfefe", stroke=INK, min_w=220)
    elems.append(b3)
    elems.append(rect(545, 145, 220, 115, fill="#ffffff", stroke=LINE, rx=6))
    elems.append(text(655, 168, "Дано:  нічого", size=11, color=INK))
    elems.append(text(655, 192, "Шукаємо:  будь-які  x₁ ≠ x₂", size=10, color=MUTED))
    elems.append(text(655, 208, "так, що  H(x₁) = H(x₂)", size=10, color=INK))
    elems.append(text(655, 232, "Складність:  O(2ⁿ/²)", size=11, color=FIELD, bold=True))
    elems.append(text(655, 248, "(Парадокс днів народжень)", size=9, color=MUTED))

    # Footer note
    elems.append(fitbox(25, 275, 730, 26, "Стійкість до колізій імпликує стійкість до другого прообразу. Поріг колізій нижчий через імовірнісний збіг у парадоксі днів народжень.", size=10, color=INK, fill="#f4f6f8", stroke=MUTED, sw=1.0))

    render(os.path.join(OUT, "fig-security-properties.svg"), W, H, *elems, title="Властивості безпеки хеш-функцій")


# ── 2. fig-merkle-damgard ───────────────────────────────────────────────────
def fig_merkle_damgard():
    W, H = 780, 270
    elems = []

    elems.append(text(W / 2, 22, "Ітеративна побудова Меркле — Дамґорда (Merkle-Damgård)", size=13, bold=True))

    # Input message blocks at top
    elems.append(rect(50, 48, 140, 36, fill="#eaf2f8", stroke="#2980b9", rx=5))
    elems.append(text(120, 70, "Блок M₁", size=11, bold=True, color="#1b4f72"))

    elems.append(rect(270, 48, 140, 36, fill="#eaf2f8", stroke="#2980b9", rx=5))
    elems.append(text(340, 70, "Блок M₂", size=11, bold=True, color="#1b4f72"))

    elems.append(rect(490, 48, 180, 36, fill="#fcf3cf", stroke="#b7950b", rx=5))
    elems.append(text(580, 70, "M_k  ||  10...0  ||  |M|", size=10, bold=True, color="#7d6608"))

    # Down arrows from inputs
    elems.append(arrow(120, 84, 120, 120, color=LINE, sw=1.6))
    elems.append(arrow(340, 84, 340, 120, color=LINE, sw=1.6))
    elems.append(arrow(580, 84, 580, 120, color=LINE, sw=1.6))

    # IV start
    elems.append(rect(20, 130, 50, 36, fill="#f4f6f8", stroke=MUTED, rx=4))
    elems.append(text(45, 152, "IV", size=11, bold=True, color=INK))
    elems.append(arrow(70, 148, 95, 148, color=LINE, sw=1.8))

    # Compression function 1
    elems.append(rect(95, 120, 115, 56, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    elems.append(text(152, 145, "Стиснення  f", size=11, bold=True, color=POS))
    elems.append(text(152, 162, "f(IV, M₁)", size=9, color=MUTED))

    # Arrow to next stage
    elems.append(arrow(210, 148, 315, 148, color=LINE, sw=1.8))
    elems.append(text(262, 138, "стан  h₁", size=10, color=INK, bold=True))

    # Compression function 2
    elems.append(rect(315, 120, 115, 56, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    elems.append(text(372, 145, "Стиснення  f", size=11, bold=True, color=POS))
    elems.append(text(372, 162, "f(h₁, M₂)", size=9, color=MUTED))

    # Arrow to dots
    elems.append(arrow(430, 148, 470, 148, color=LINE, sw=1.8))
    elems.append(text(495, 148, "• • •", size=14, color=MUTED, bold=True))
    elems.append(arrow(520, 148, 555, 148, color=LINE, sw=1.8))

    # Compression function final
    elems.append(rect(555, 120, 125, 56, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    elems.append(text(617, 145, "Стиснення  f", size=11, bold=True, color=POS))
    elems.append(text(617, 162, "f(h_{k-1}, M_k')", size=9, color=MUTED))

    # Final Output Arrow
    elems.append(arrow(680, 148, 715, 148, color=FIELD, sw=2.2))
    b_out, _, _ = textbox(745, 148, "H(M)", size=12, bold=True, fill="#eafaf1", stroke=FIELD, min_w=50)
    elems.append(b_out)

    # Explanatory footer note
    elems.append(fitbox(20, 205, 740, 50,
                        "Зміцнення Меркле — Дамґорда додає довжину |M| в останній блок. "
                        "Доведено: якщо функція стиснення f є стійкою до колізій, то й увесь ітеративний хеш H є стійким до колізій.",
                        size=10, color=INK, fill="#fcfcfc", stroke=MUTED, sw=1.0))

    render(os.path.join(OUT, "fig-merkle-damgard.svg"), W, H, *elems, title="Побудова Меркле — Дамґорда")


# ── 3. fig-sponge-construction ──────────────────────────────────────────────
def fig_sponge_construction():
    W, H = 780, 290
    elems = []

    elems.append(text(W / 2, 22, "Губчаста архітектура (Sponge Construction) — приклад SHA-3 / Keccak", size=13, bold=True))

    # Left box: Absorbing Phase
    elems.append(rect(30, 48, 340, 180, fill="#f4f9f9", stroke="#16a085", sw=1.6, rx=8))
    elems.append(text(200, 70, "1. Фаза поглинання (Absorbing)", size=12, bold=True, color="#0e6251"))

    # State layout in Absorb
    elems.append(rect(50, 90, 180, 40, fill="#d4efdf", stroke=FIELD, rx=4))
    elems.append(text(140, 114, "Швидкість r  (Rate)", size=10, bold=True, color=FIELD))
    elems.append(rect(230, 90, 120, 40, fill="#fadbd8", stroke=POS, rx=4))
    elems.append(text(290, 114, "Ємність c (Capacity)", size=9, bold=True, color=POS))

    elems.append(arrow(140, 140, 140, 160, color=LINE, sw=1.5))
    elems.append(text(140, 155, "⊕ M_i", size=11, bold=True, color=INK))
    elems.append(rect(80, 170, 240, 40, fill="#ffffff", stroke=INK, rx=6))
    elems.append(text(200, 194, "Перестановка  π  (1600 бітів)", size=10, bold=True, color=INK))

    # Center transition arrow
    elems.append(arrow(380, 138, 420, 138, color=LINE, sw=2.0))
    elems.append(text(400, 125, "поглинули", size=9, color=MUTED))

    # Right box: Squeezing Phase
    elems.append(rect(430, 48, 320, 180, fill="#fef9e7", stroke="#d4ac0d", sw=1.6, rx=8))
    elems.append(text(590, 70, "2. Фаза вижимання (Squeezing)", size=12, bold=True, color="#7d6608"))

    # State layout in Squeeze
    elems.append(rect(450, 90, 170, 40, fill="#d4efdf", stroke=FIELD, rx=4))
    elems.append(text(535, 114, "Вихід  Z_i  з  r", size=10, bold=True, color=FIELD))
    elems.append(rect(620, 90, 110, 40, fill="#fadbd8", stroke=POS, rx=4))
    elems.append(text(675, 114, "Ємність  c", size=9, bold=True, color=POS))

    elems.append(arrow(535, 130, 535, 160, color=LINE, sw=1.5))
    elems.append(rect(470, 170, 240, 40, fill="#ffffff", stroke=INK, rx=6))
    elems.append(text(590, 194, "Перестановка  π", size=10, bold=True, color=INK))

    # Footer note
    elems.append(fitbox(30, 238, 720, 42,
                        "Стійкість до колізій визначається ємністю c: складність 2^{c/2}. "
                        "Частина c ніколи не контактує безпосередньо з вхідними чи вихідними даними, захищаючи від атак подовження.",
                        size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.0))

    render(os.path.join(OUT, "fig-sponge-construction.svg"), W, H, *elems, title="Губчаста архітектура Хеш-функції")


# ── 4. fig-chp-hash ─────────────────────────────────────────────────────────
def fig_chp_hash():
    W, H = 780, 280
    elems = []

    elems.append(text(W / 2, 22, "Доказово стійка хеш-функція Чаума — ван Гейста — Пфітцманна (CHP)", size=13, bold=True))

    # Input message blocks
    elems.append(rect(60, 55, 200, 40, fill="#eaf2f8", stroke="#2980b9", rx=6))
    elems.append(text(160, 79, "Вхідні блоки: (x₁, x₂) ∈ ℤ_q × ℤ_q", size=10, bold=True, color="#1b4f72"))

    # Generators
    elems.append(rect(310, 55, 200, 40, fill="#fcf3cf", stroke="#b7950b", rx=6))
    elems.append(text(410, 79, "Генератори: g, h ∈ ℤ_p*", size=10, bold=True, color="#7d6608"))

    # Down arrows to powers
    elems.append(arrow(160, 95, 160, 125, color=LINE, sw=1.6))
    elems.append(arrow(410, 95, 410, 125, color=LINE, sw=1.6))

    # Intermediate exponentiation boxes
    b_pow1, _, _ = textbox(160, 150, "A = g^{x₁} mod p", size=11, bold=True, fill="#ffffff", stroke=INK, min_w=180)
    elems.append(b_pow1)

    b_pow2, _, _ = textbox(410, 150, "B = h^{x₂} mod p", size=11, bold=True, fill="#ffffff", stroke=INK, min_w=180)
    elems.append(b_pow2)

    # Multiplication and modulo
    elems.append(arrow(250, 150, 295, 150, color=LINE, sw=1.8))
    elems.append(arrow(410, 175, 410, 200, color=LINE, sw=1.8))
    elems.append(arrow(160, 175, 330, 215, color=LINE, sw=1.6))

    b_final, _, _ = textbox(410, 220, "CHP(x₁, x₂) = (A · B) mod p = (g^{x₁} · h^{x₂}) mod p", size=11, bold=True, fill="#eafaf1", stroke=FIELD, min_w=380)
    elems.append(b_final)

    # Side callout for Discrete Log link
    elems.append(rect(550, 55, 200, 115, fill="#fbecec", stroke=POS, rx=6))
    elems.append(text(650, 76, "Зв'язок зі складністю:", size=10, bold=True, color=POS))
    elems.append(text(650, 98, "Знайти колізію ≡", size=10, color=INK))
    elems.append(text(650, 120, "обчислити дискретний", size=10, color=INK))
    elems.append(text(650, 140, "логарифм  a = log_g h", size=10, bold=True, color=POS))

    render(os.path.join(OUT, "fig-chp-hash.svg"), W, H, *elems, title="Доказово стійка хеш-функція CHP")


if __name__ == "__main__":
    fig_security_properties()
    fig_merkle_damgard()
    fig_sponge_construction()
    fig_chp_hash()
    print("figs: 4 written to", OUT)
