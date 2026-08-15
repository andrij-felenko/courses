# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. fig-zkp-three-properties: Три фундаментальні властивості ZKP
def fig_zkp_three_properties():
    W, H = 960, 360
    p = []

    p.append(text(W / 2, 35, "Три аксіоматичні стовпи доведення з нульовим розголошенням", size=16, bold=True))
    p.append(text(W / 2, 58, "Математичні гарантії для доводжувача, перевіряльника та приватності секрету", size=13, color=MUTED))

    box_w, box_h = 270, 220
    ys = 95
    xs = [50, 345, 640]

    props = [
        {
            "title": "1. Повнота (Completeness)",
            "sub": "Чесний прогон завжди успішний",
            "bg": "#eafaf0",
            "border": FIELD,
            "desc": [
                "Якщо твердження істинне,",
                "і обидві сторони чесно",
                "виконують протокол,",
                "перевіряльник прийняття",
                "гарантує з імовірністю 1.",
                "Pr[(P, V) = 1] = 1"
            ]
        },
        {
            "title": "2. Обґрунтованість (Soundness)",
            "sub": "Захист від обману та фальсифікацій",
            "bg": "#fff5f5",
            "border": POS,
            "desc": [
                "Якщо твердження хибне,",
                "жоден фальшивий P* не зможе",
                "переконати чесного V,",
                "окрім нехтовно малої",
                "імовірності помилки ε.",
                "Pr[(P*, V) = 1] ≤ ε"
            ]
        },
        {
            "title": "3. Нульове розголошення",
            "sub": "Абсолютна приватність свідка",
            "bg": "#f0f4fe",
            "border": NEG,
            "desc": [
                "Перевіряльник не дізнається",
                "жодного біта про свідок x.",
                "Існує симулятор S,",
                "що створює транскрипт",
                "без знання секрету:",
                "S(x) ≈ ⟨P(x,w), V(x)⟩"
            ]
        }
    ]

    for i, item in enumerate(props):
        x = xs[i]
        p.append(rect(x, ys, box_w, box_h, fill=item["bg"], stroke=item["border"], sw=1.8, rx=8))
        p.append(text(x + box_w/2, ys + 30, item["title"], size=13.5, bold=True, color=INK))
        p.append(text(x + box_w/2, ys + 50, item["sub"], size=11, color=MUTED))
        
        # Горизонтальний роздільник
        p.append(line(x + 20, ys + 65, x + box_w - 20, ys + 65, color=LINE, sw=1))

        # Описовий текст
        for j, line_txt in enumerate(item["desc"]):
            is_formula = j == len(item["desc"]) - 1
            font_sz = 12 if not is_formula else 12.5
            font_bold = is_formula
            t_color = INK if not is_formula else item["border"]
            p.append(text(x + box_w/2, ys + 88 + j * 20, line_txt, size=font_sz, bold=font_bold, color=t_color))

    render(os.path.join(OUT, "fig-zkp-three-properties.svg"), W, H, *p, title="Фундаментальні властивості ZKP")


# ── 2. fig-schnorr-protocol-flow: Інтерактивний протокол Шнорра
def fig_schnorr_protocol_flow():
    W, H = 960, 420
    p = []

    p.append(text(W / 2, 35, "Інтерактивний трикроковий діалог протоколу Шнорра", size=16, bold=True))
    p.append(text(W / 2, 58, "Доведення знання дискретного логарифма y = g^x mod p без розкриття x", size=13, color=MUTED))

    # Вертикальні лінії ліній часу (Prover & Verifier)
    px, vx = 220, 740
    top_y, bot_y = 90, 380

    # Блоки учасників
    p.append(rect(px - 100, top_y, 200, 45, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=6))
    p.append(text(px, top_y + 20, "Доводжувач (Prover)", size=14, bold=True, color=INK))
    p.append(text(px, top_y + 36, "Секрет: x ∈ ℤ_q", size=11, color=MUTED))

    p.append(rect(vx - 100, top_y, 200, 45, fill="#f8f9fa", stroke=LINE, sw=1.5, rx=6))
    p.append(text(vx, top_y + 20, "Перевіряльник (Verifier)", size=14, bold=True, color=INK))
    p.append(text(vx, top_y + 36, "Публічний ключ: y = g^x mod p", size=11, color=MUTED))

    # Вертикальні осі
    p.append(line(px, top_y + 45, px, bot_y, color=LINE, sw=1.5, dash="4 4"))
    p.append(line(vx, top_y + 45, vx, bot_y, color=LINE, sw=1.5, dash="4 4"))

    # Крок 1: Зобов'язання (Commitment)
    y1 = 170
    b1, _, _ = textbox(px - 130, y1, "Випадкове k ∈ ℤ_q\nr = g^k mod p", size=11.5, fill="#ffffff", stroke=NEG, sw=1.2, pad=6)
    p.append(b1)
    p.append(arrow(px + 10, y1, vx - 10, y1, color=NEG, sw=2))
    p.append(text((px + vx)/2, y1 - 12, "1. Зобов'язання: r", size=12.5, bold=True, color=NEG))

    # Крок 2: Виклик (Challenge)
    y2 = 250
    b2, _, _ = textbox(vx + 130, y2, "Випадковий виклик\nc ∈ ℤ_q", size=11.5, fill="#ffffff", stroke=POS, sw=1.2, pad=6)
    p.append(b2)
    p.append(arrow(vx - 10, y2, px + 10, y2, color=POS, sw=2))
    p.append(text((px + vx)/2, y2 - 12, "2. Випробовувальний виклик: c", size=12.5, bold=True, color=POS))

    # Крок 3: Відповідь (Response)
    y3 = 330
    b3, _, _ = textbox(px - 130, y3, "s = (k + c · x) mod q", size=11.5, fill="#ffffff", stroke=FIELD, sw=1.2, pad=6)
    p.append(b3)
    p.append(arrow(px + 10, y3, vx - 10, y3, color=FIELD, sw=2))
    p.append(text((px + vx)/2, y3 - 12, "3. Підтверджувальна відповідь: s", size=12.5, bold=True, color=FIELD))

    # Блок перевірки на боці Verifier
    b4, _, _ = textbox(vx + 130, y3, "Перевірка тотожності:\ng^s ≡ r · y^c (mod p)", size=11.5, fill="#eafaf0", stroke=FIELD, sw=1.5, pad=8)
    p.append(b4)

    render(os.path.join(OUT, "fig-schnorr-protocol-flow.svg"), W, H, *p, title="Протокол Шнорра")


# ── 3. fig-fiat-shamir-transform: Перетворення Фіата — Шаміра
def fig_fiat_shamir_transform():
    W, H = 960, 380
    p = []

    p.append(text(W / 2, 35, "Перетворення Фіата — Шаміра: від інтерактивного до NIZK", size=16, bold=True))
    p.append(text(W / 2, 58, "Заміна живого перевіряльника детермінованою криптографічною хеш-функцією", size=13, color=MUTED))

    # Ліва частина: Інтерактивний діалог
    p.append(rect(40, 90, 420, 260, fill="#fafafa", stroke=LINE, sw=1.3, rx=8))
    p.append(text(250, 115, "Інтерактивний протокол (3 кроки)", size=14, bold=True, color=INK))

    p.append(rect(70, 140, 100, 35, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(120, 162, "Доводжувач", size=12, bold=True))

    p.append(rect(330, 140, 100, 35, fill="#ffffff", stroke=LINE, rx=4))
    p.append(text(380, 162, "Перевіряльник", size=12, bold=True))

    p.append(arrow(175, 195, 325, 195, color=NEG, sw=1.5))
    p.append(text(250, 188, "1. Commitment r", size=11, color=NEG))

    p.append(arrow(325, 240, 175, 240, color=POS, sw=1.5))
    p.append(text(250, 233, "2. Random Challenge c", size=11, color=POS))

    p.append(arrow(175, 285, 325, 285, color=FIELD, sw=1.5))
    p.append(text(250, 278, "3. Response s", size=11, color=FIELD))

    p.append(text(250, 330, "Потрібен синхронний канал зв'язку", size=11.5, color=MUTED))

    # Центральна стрілка трансформації
    p.append(arrow(470, 220, 520, 220, color=INK, sw=2.5))
    p.append(text(495, 200, "Хешування", size=11, bold=True, color=INK))
    p.append(text(495, 240, "c = H(g,y,r)", size=11, bold=True, color=NEG))

    # Права частина: Неінтерактивний аргумент (NIZK)
    p.append(rect(530, 90, 390, 260, fill="#f0f4fe", stroke=NEG, sw=1.5, rx=8))
    p.append(text(725, 115, "Неінтерактивний доказ (NIZK)", size=14, bold=True, color=NEG))

    b_p, _, _ = textbox(725, 175, "Доводжувач автономно:\n1. r = g^k mod p\n2. c = H(g, y, r) mod q\n3. s = (k + c · x) mod q",
                        size=11.5, fill="#ffffff", stroke=NEG, pad=8)
    p.append(b_p)

    p.append(arrow(725, 235, 725, 265, color=FIELD, sw=1.8))
    p.append(text(725, 250, "Пакетований доказ π = (r, s)", size=11, bold=True, color=FIELD))

    b_v, _, _ = textbox(725, 305, "Перевіряльник перевіряє у будь-який час:\nc' = H(g, y, r)\ng^s ≡ r · y^{c'} (mod p)",
                        size=11.5, fill="#eafaf0", stroke=FIELD, pad=8)
    p.append(b_v)

    render(os.path.join(OUT, "fig-fiat-shamir-transform.svg"), W, H, *p, title="Трансформація Фіата — Шаміра")


# ── 4. fig-simulator-game: Симуляційна гра для вимірювання Zero-Knowledge
def fig_simulator_game():
    W, H = 960, 380
    p = []

    p.append(text(W / 2, 35, "Парадигма симуляційного експерименту (Zero-Knowledge Game)", size=16, bold=True))
    p.append(text(W / 2, 58, "Нерозрізнюваність реального протоколу від транскрипту штучного симулятора", size=13, color=MUTED))

    # Ліва вежа: Реальний прогон
    p.append(rect(60, 95, 380, 250, fill="#fafafa", stroke=LINE, sw=1.3, rx=8))
    p.append(text(250, 120, "Реальний протокол ⟨P(x), V⟩", size=13.5, bold=True, color=INK))

    p.append(rect(90, 145, 140, 40, fill="#ffffff", stroke=LINE, rx=5))
    p.append(text(160, 168, "Prover (знає секрет x)", size=11, bold=True))

    p.append(rect(270, 145, 140, 40, fill="#ffffff", stroke=LINE, rx=5))
    p.append(text(340, 168, "Verifier V", size=11, bold=True))

    p.append(arrow(160, 185, 340, 185, color=NEG, sw=1.4))
    p.append(text(250, 205, "Транскрипт взаємодії:", size=11, color=MUTED))
    
    b_real, _, _ = textbox(250, 255, "T_real = (r, c, s)\nr = g^k, c = challenge, s = k + cx", size=11.5, fill="#ffffff", stroke=LINE, pad=8)
    p.append(b_real)

    # Статистична нерозрізнюваність у центрі
    p.append(rect(455, 180, 50, 50, fill="#f0f4fe", stroke=NEG, sw=1.5, rx=25))
    p.append(text(480, 209, "≈", size=24, bold=True, color=NEG))
    p.append(text(480, 245, "Нерозрізнювані", size=10.5, bold=True, color=MUTED))

    # Права вежа: Симулятор S
    p.append(rect(520, 95, 380, 250, fill="#f0f4fe", stroke=NEG, sw=1.5, rx=8))
    p.append(text(710, 120, "Симулятор S(y) без секрету x", size=13.5, bold=True, color=NEG))

    b_sim_proc, _, _ = textbox(710, 175, "Алгоритм симулятора:\n1. Обирає випадкові c, s ∈ ℤ_q\n2. Обчислює r = g^s · y^{-c} mod p",
                                size=11.5, fill="#ffffff", stroke=NEG, pad=8)
    p.append(b_sim_proc)

    b_sim, _, _ = textbox(710, 255, "T_sim = (r, c, s)\nЗадовольняє g^s ≡ r · y^c (mod p)", size=11.5, fill="#eafaf0", stroke=FIELD, pad=8)
    p.append(b_sim)

    render(os.path.join(OUT, "fig-simulator-game.svg"), W, H, *p, title="Симуляційна гра ZKP")


if __name__ == "__main__":
    fig_zkp_three_properties()
    fig_schnorr_protocol_flow()
    fig_fiat_shamir_transform()
    fig_simulator_game()
    print("Zero-Knowledge Proofs figures generated successfully.")
