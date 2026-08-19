# -*- coding: utf-8 -*-
"""Фігури для статті math/algebra/montgomery-reduction «Арифметика та перетворення Монтгомері».
svgkit імпортуємо зі scripts/, не переписуємо (§5 AUTHORING). Вивід — у ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "'Consolas', 'DejaVu Sans Mono', 'Courier New', monospace"
GOLD = "#caa24a"
POSF = "#fdecea"
NEGF = "#eaf0fd"
FLDF = "#eef7f0"
WARNF = "#fff8e7"
WARN_STROKE = "#d97706"

def mono_text(x, y, s, size=13, color=INK, anchor="middle", bold=True):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%g" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))

# ── 1. Порівняння класичного підходу та простору Монтгомері ──────────────────
def fig_montgomery_pipeline():
    W, H = 1000, 520
    P = []
    
    P.append(text(W / 2, 28, "Класичне модульне множення проти підходу Монтгомері", size=18, bold=True))
    P.append(text(W / 2, 50, "Заміна важкого довгого ділення на побітові зсуви при масових обчисленнях (піднесення до степеня)",
                  size=12, color=MUTED, italic=True))
    
    # ── Блок 1: Класичний підхід (згори) ──
    P.append(rect(30, 75, 940, 180, fill=FILL, stroke=LINE, rx=8))
    P.append(text(60, 102, "Класичний підхід: ділення на кожному кроці", size=15, bold=True, anchor="start", color=POS))
    
    # Схема класичного множення
    b1, _, _ = textbox(130, 160, "Вхідні числа\nA, B", size=13, fill="#ffffff", stroke=LINE, min_w=120)
    P.append(b1)
    P.append(arrow(190, 160, 240, 160, color=LINE))
    
    b2, _, _ = textbox(320, 160, "Множення цілих\nT = A × B", size=13, fill=NEGF, stroke=NEG, min_w=140)
    P.append(b2)
    P.append(arrow(390, 160, 440, 160, color=LINE))
    
    b3, _, _ = textbox(560, 160, "Довге ділення на N\n(T mod N: пошук частки,\nвіднімання з переносом)", size=12, fill=POSF, stroke=POS, min_w=200)
    P.append(b3)
    P.append(arrow(660, 160, 710, 160, color=LINE))
    
    b4, _, _ = textbox(810, 160, "Результат кроку\nC = (A × B) mod N", size=13, fill="#ffffff", stroke=LINE, min_w=160)
    P.append(b4)
    
    # Петля повторення класичного кроку
    P.append(line(810, 205, 810, 230, color=POS, dash="4,4"))
    P.append(line(810, 230, 320, 230, color=POS, dash="4,4"))
    P.append(arrow(320, 230, 320, 195, color=POS))
    P.append(text(560, 242, "Повторюється k разів: кожна операція містить важке довге ділення", size=11, color=POS, bold=True))
    
    # ── Блок 2: Простір Монтгомері (знизу) ──
    P.append(rect(30, 280, 940, 220, fill=FLDF, stroke=FIELD, rx=8))
    P.append(text(60, 307, "Підхід Монтгомері: обчислення у видозміненому просторі", size=15, bold=True, anchor="start", color=FIELD))
    
    # Вхід у простір
    b_in, _, _ = textbox(115, 380, "Вхід A, B\n(числа < N)", size=12, fill="#ffffff", stroke=LINE, min_w=110)
    P.append(b_in)
    P.append(arrow(170, 380, 220, 380, color=FIELD))
    
    b_conv, _, _ = textbox(305, 380, "Вхідне перетворення\n(одноразово):\nā = A·R mod N\nb̄ = B·R mod N", size=11, fill=WARNF, stroke=WARN_STROKE, min_w=150)
    P.append(b_conv)
    P.append(arrow(380, 380, 430, 380, color=FIELD))
    
    # Швидке ядро
    b_core, _, _ = textbox(575, 380, "Швидка редукція REDC(ā × b̄):\n1. Множення на сталу N' mod R\n2. Обнулення молодших бітів\n3. Зсув праворуч на k бітів (÷ R)", size=11, fill="#ffffff", stroke=FIELD, min_w=240)
    P.append(b_core)
    P.append(arrow(695, 380, 745, 380, color=FIELD))
    
    # Вихід
    b_out, _, _ = textbox(855, 380, "Вихідне зведення\n(одноразово):\nC = REDC(c̄)", size=11, fill=WARNF, stroke=WARN_STROKE, min_w=140)
    P.append(b_out)
    
    # Петля швидких операцій
    P.append(line(575, 440, 575, 465, color=FIELD))
    P.append(line(575, 465, 490, 465, color=FIELD))
    P.append(line(490, 465, 490, 440, color=FIELD))
    P.append(arrow(490, 440, 490, 425, color=FIELD))
    P.append(text(535, 480, "Цикл піднесення до степеня: сотні множень без жодного ділення", size=11, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "montgomery-pipeline.svg"), W, H, *P)

# ── 2. Покроковий механізм REDC: обнулення та зсув бітів ───────────────────────
def fig_redc_clearing_bits():
    W, H = 980, 540
    P = []
    
    P.append(text(W / 2, 28, "Механізм редукції REDC(T): обнулення молодших бітів та зсув", size=18, bold=True))
    P.append(text(W / 2, 50, "Як додавання кратного m·N перетворює ділення на R = 2^k на звичайний правий бітовий зсув",
                  size=12, color=MUTED, italic=True))
    
    # Крок 1: Початкове подвійне число T
    P.append(text(80, 95, "1. Добуток образів T = ā × b̄ (довжина 2k бітів):", size=14, bold=True, anchor="start"))
    P.append(rect(80, 115, 380, 45, fill=NEGF, stroke=NEG, rx=4))
    P.append(text(270, 142, "Старші k бітів (T / R)", size=12, color=NEG, bold=True))
    P.append(rect(460, 115, 380, 45, fill=POSF, stroke=POS, rx=4))
    P.append(text(650, 142, "Молодші k бітів (T mod R = T₀ ≠ 0)", size=12, color=POS, bold=True))
    
    # Крок 2: Обчислення коефіцієнта m
    P.append(text(80, 195, "2. Обчислення коефіцієнта обнулення m = ((T mod R) × N') mod R:", size=14, bold=True, anchor="start"))
    b_m, _, _ = textbox(490, 230, "Стала N' = -N⁻¹ mod R підібрана так, що (T₀ + m·N) ≡ 0 (mod R)", size=12, fill=WARNF, stroke=WARN_STROKE, min_w=600)
    P.append(b_m)
    
    # Крок 3: Додавання m·N до T
    P.append(text(80, 285, "3. Додавання m × N до числа T:", size=14, bold=True, anchor="start"))
    P.append(rect(80, 305, 380, 45, fill=NEGF, stroke=NEG, rx=4))
    P.append(text(270, 332, "Старша частина суми (T + m·N)", size=12, color=NEG, bold=True))
    P.append(rect(460, 305, 380, 45, fill=FLDF, stroke=FIELD, rx=4))
    P.append(mono_text(650, 332, "0 0 0 0 ... 0 0 0 (строго k нулів)", size=13, color=FIELD, bold=True))
    
    # Крок 4: Ділення на R (зсув праворуч)
    P.append(text(80, 385, "4. Ділення на R = 2^k (побітовий зсув праворуч >> k, відкидання нулів):", size=14, bold=True, anchor="start"))
    P.append(arrow(270, 355, 270, 405, color=FIELD, sw=2.5))
    P.append(rect(80, 410, 380, 45, fill=FLDF, stroke=FIELD, rx=4))
    P.append(text(270, 437, "Результат зсуву t = (T + m·N) / R (довжина k бітів, t < 2N)", size=11, color=FIELD, bold=True))
    
    # Крок 5: Умовне віднімання
    P.append(text(80, 490, "5. Фінальне приведення:", size=13, bold=True, anchor="start"))
    b_fin, _, _ = textbox(570, 490, "якщо t ≥ N, то повернути (t - N), інакше повернути t (результат строго < N)", size=12, fill="#ffffff", stroke=LINE, min_w=650)
    P.append(b_fin)
    
    render(os.path.join(OUT, "redc-clearing-bits.svg"), W, H, *P)

# ── 3. Драбина Монтгомері проти наївного бінарного піднесення ─────────────────
def fig_montgomery_ladder():
    W, H = 1000, 500
    P = []
    
    P.append(text(W / 2, 28, "Захист від атак за часом: Драбина Монтгомері проти наївного алгоритму", size=18, bold=True))
    P.append(text(W / 2, 50, "Усунення розгалужень за таємними бітами ключа для захисту від Simple Power Analysis (SPA)",
                  size=12, color=MUTED, italic=True))
    
    # Ліва колонка: Наївне піднесення до степеня
    P.append(rect(40, 75, 440, 400, fill=POSF, stroke=POS, rx=8))
    P.append(text(260, 105, "Наївний Square-and-Multiply (Вразливий)", size=14, bold=True, color=POS))
    
    b_n1, _, _ = textbox(260, 150, "Для кожного біта k[i] показника степеня:\nR = R² mod N (Square)", size=12, fill="#ffffff", stroke=LINE, min_w=380)
    P.append(b_n1)
    
    P.append(arrow(260, 180, 260, 215, color=POS))
    
    b_n2, _, _ = textbox(260, 245, "Розгалуження if (k[i] == 1):\nтак  →  R = R × A mod N (Multiply)\nні   →  пропуск операції", size=12, fill=WARNF, stroke=WARN_STROKE, min_w=380)
    P.append(b_n2)
    
    P.append(arrow(260, 285, 260, 320, color=POS))
    
    b_n3, _, _ = textbox(260, 385, "Атака за часом / живленням (SPA):\n• Біт 0: 1 операція (короткий час, низький струм)\n• Біт 1: 2 операції (довгий час, високий струм)\n→ Повний витік таємного ключа!", size=11, fill="#ffffff", stroke=POS, min_w=380)
    P.append(b_n3)
    
    # Права колонка: Драбина Монтгомері
    P.append(rect(520, 75, 440, 400, fill=FLDF, stroke=FIELD, rx=8))
    P.append(text(740, 105, "Драбина Монтгомері (Константний час)", size=14, bold=True, color=FIELD))
    
    b_l1, _, _ = textbox(740, 150, "Два регістри стану (R₀, R₁):\nПочатково: R₀ = 1, R₁ = A", size=12, fill="#ffffff", stroke=LINE, min_w=380)
    P.append(b_l1)
    
    P.append(arrow(740, 180, 740, 215, color=FIELD))
    
    b_l2, _, _ = textbox(740, 255, "Для кожного біта k[i] (незалежно від 0 чи 1):\nякщо k[i] == 0: R₁ = R₀·R₁,  R₀ = R₀²\nякщо k[i] == 1: R₀ = R₀·R₁,  R₁ = R₁²\n(Завжди строго 1 множення + 1 піднесення)", size=11, fill="#ffffff", stroke=FIELD, min_w=380)
    P.append(b_l2)
    
    P.append(arrow(740, 305, 740, 340, color=FIELD))
    
    b_l3, _, _ = textbox(740, 400, "Стійкість до Side-Channel атак:\n• Однаковий час виконання кожного біта\n• Однаковий профіль енергоспоживання\n• Інваріант R₁ - R₀ = A захищає від помилок", size=11, fill="#ffffff", stroke=FIELD, min_w=380)
    P.append(b_l3)
    
    render(os.path.join(OUT, "montgomery-ladder.svg"), W, H, *P)

if __name__ == "__main__":
    fig_montgomery_pipeline()
    fig_redc_clearing_bits()
    fig_montgomery_ladder()
    print("Всі 3 фігури згенеровано успішно.")
