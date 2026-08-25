# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_R = "#2457d6"
ORANGE = "#e08a1e"
GREEN  = "#27ae60"
RED    = "#d9534f"
GREY   = "#9aa3af"
DARK   = "#2c3e50"

def state(cx, cy, name, r=24, fill="#ffffff", stroke=BLUE_R, accept=False, sw=2.0):
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)
    if accept:
        out += circle(cx, cy, r - 4, fill="none", stroke=stroke, sw=sw)
    out += text(cx, cy + 4, name, size=13, color=INK, bold=True)
    return out

# ── ФІГ. 1: Архітектурний конвеєр рушія регулярних виразів ──
def fig_pipeline():
    W, H = 840, 220
    p = []
    
    # 5 блоків конвеєра
    boxes = [
        ("Шаблон", "`(a|b)*abb`", 90, ORANGE),
        ("Парсер / AST", "Дерево синтаксису", 250, BLUE_R),
        ("НКА Томпсона", "Автомат з ε-переходами", 420, BLUE_R),
        ("Лінивий ДКА", "Кеш станів (Pike VM)", 590, GREEN),
        ("Збіг у тексті", "Індекс початку/кінця", 750, GREEN),
    ]
    
    y = 110
    w_box, h_box = 120, 70
    
    for i, (title, sub, x, color) in enumerate(boxes):
        p.append(rect(x - w_box//2, y - h_box//2, w_box, h_box, fill="#ffffff", stroke=color, sw=2.0, rx=8))
        p.append(text(x, y - 10, title, size=13, color=INK, bold=True))
        p.append(text(x, y + 14, sub, size=11, color=MUTED))
        
        if i < len(boxes) - 1:
            x_next = boxes[i+1][2]
            x1 = x + w_box//2
            x2 = x_next - w_box//2
            p.append(arrow(x1, y, x2, y, color=DARK, sw=1.8))
            
    render(os.path.join(OUT, "regex-pipeline.svg"), W, H, "".join(p))

# ── ФІГ. 2: Базові конструкції Томпсона (Літерал, Конкатенація, Вибір, Зірочка Кліні) ──
def fig_thompson_constructions():
    W, H = 840, 480
    p = []
    
    # Секція А: Літерал 'a'
    p.append(rect(20, 20, 390, 210, fill="#fbfcfd", stroke=GREY, sw=1.0, rx=8))
    p.append(text(35, 45, "1. Літеральний перехід (символ 'a')", size=13, color=DARK, bold=True, anchor="start"))
    p.append(state(90, 130, "s0", r=22, stroke=BLUE_R))
    p.append(state(330, 130, "s1", r=22, stroke=GREEN, accept=True))
    p.append(arrow(112, 130, 308, 130, color=DARK, sw=1.8))
    p.append(text(210, 118, "'a'", size=13, color=ORANGE, bold=True))
    
    # Секція Б: Конкатенація A B
    p.append(rect(430, 20, 390, 210, fill="#fbfcfd", stroke=GREY, sw=1.0, rx=8))
    p.append(text(445, 45, "2. Конкатенація (A · B)", size=13, color=DARK, bold=True, anchor="start"))
    p.append(state(480, 130, "s0", r=20, stroke=BLUE_R))
    p.append(state(580, 130, "s1", r=20, stroke=BLUE_R))
    p.append(state(680, 130, "s2", r=20, stroke=BLUE_R))
    p.append(state(780, 130, "s3", r=20, stroke=GREEN, accept=True))
    p.append(arrow(500, 130, 560, 130, color=DARK, sw=1.5))
    p.append(text(530, 118, "A", size=12, color=ORANGE))
    p.append(arrow(600, 130, 660, 130, color=RED, sw=1.5))
    p.append(text(630, 118, "ε", size=14, color=RED, bold=True))
    p.append(arrow(700, 130, 760, 130, color=DARK, sw=1.5))
    p.append(text(730, 118, "B", size=12, color=ORANGE))

    # Секція В: Альтернація A | B
    p.append(rect(20, 250, 390, 210, fill="#fbfcfd", stroke=GREY, sw=1.0, rx=8))
    p.append(text(35, 275, "3. Альтернація / Вибір (A | B)", size=13, color=DARK, bold=True, anchor="start"))
    p.append(state(60, 365, "s_in", r=20, stroke=BLUE_R))
    p.append(state(170, 315, "A_in", r=18, stroke=BLUE_R))
    p.append(state(240, 315, "A_out", r=18, stroke=BLUE_R))
    p.append(state(170, 415, "B_in", r=18, stroke=BLUE_R))
    p.append(state(240, 415, "B_out", r=18, stroke=BLUE_R))
    p.append(state(350, 365, "s_out", r=20, stroke=GREEN, accept=True))
    
    # ε-переходи розгалуження і злиття
    p.append(arrow(80, 355, 152, 323, color=RED, sw=1.5))
    p.append(text(105, 328, "ε", size=13, color=RED, bold=True))
    p.append(arrow(80, 375, 152, 407, color=RED, sw=1.5))
    p.append(text(105, 402, "ε", size=13, color=RED, bold=True))
    
    p.append(arrow(188, 315, 222, 315, color=DARK, sw=1.5))
    p.append(text(205, 303, "A", size=12, color=ORANGE))
    p.append(arrow(188, 415, 222, 415, color=DARK, sw=1.5))
    p.append(text(205, 403, "B", size=12, color=ORANGE))
    
    p.append(arrow(258, 323, 330, 355, color=RED, sw=1.5))
    p.append(text(300, 328, "ε", size=13, color=RED, bold=True))
    p.append(arrow(258, 407, 330, 375, color=RED, sw=1.5))
    p.append(text(300, 402, "ε", size=13, color=RED, bold=True))

    # Секція Г: Зірочка Кліні A*
    p.append(rect(430, 250, 390, 210, fill="#fbfcfd", stroke=GREY, sw=1.0, rx=8))
    p.append(text(445, 275, "4. Зірочка Кліні (A*)", size=13, color=DARK, bold=True, anchor="start"))
    p.append(state(470, 365, "s_in", r=20, stroke=BLUE_R))
    p.append(state(570, 365, "A_in", r=18, stroke=BLUE_R))
    p.append(state(670, 365, "A_out", r=18, stroke=BLUE_R))
    p.append(state(770, 365, "s_out", r=20, stroke=GREEN, accept=True))
    
    # ε в обхід A
    p.append(line(486, 352, 754, 352, color=RED, sw=1.5, dash="3 3"))
    p.append(text(620, 340, "ε (0 повторів)", size=12, color=RED, bold=True))
    
    # ε зворотна петля
    p.append(line(670, 383, 570, 383, color=RED, sw=1.5, dash="3 3"))
    p.append(text(620, 398, "ε (повтор)", size=12, color=RED, bold=True))
    
    p.append(arrow(490, 365, 552, 365, color=RED, sw=1.5))
    p.append(arrow(588, 365, 652, 365, color=DARK, sw=1.5))
    p.append(text(620, 353, "A", size=12, color=ORANGE))
    p.append(arrow(688, 365, 750, 365, color=RED, sw=1.5))

    render(os.path.join(OUT, "thompson-constructions.svg"), W, H, "".join(p))

# ── ФІГ. 3: Катастрофічний бектрекінг проти паралельного НКА ──
def fig_backtracking_vs_nfa():
    W, H = 840, 320
    p = []
    
    # Ліва частина: Рекурсивний бектрекінг (Дерево викликів)
    p.append(rect(20, 20, 390, 280, fill="#fff5f5", stroke=RED, sw=1.5, rx=8))
    p.append(text(215, 48, "Рекурсивний бектрекінг (PCRE / Python re)", size=13, color=RED, bold=True))
    p.append(text(215, 68, "Шаблон (a+)+b, текст 'aaaaX'", size=11, color=MUTED))
    
    # Дерево бектрекінгу
    p.append(circle(215, 105, 12, fill="#ffffff", stroke=RED, sw=1.5))
    p.append(text(215, 108, "1", size=10, color=DARK))
    
    p.append(circle(145, 155, 12, fill="#ffffff", stroke=RED, sw=1.5))
    p.append(circle(285, 155, 12, fill="#ffffff", stroke=RED, sw=1.5))
    p.append(line(206, 113, 154, 147, color=RED, sw=1.2))
    p.append(line(224, 113, 276, 147, color=RED, sw=1.2))
    
    p.append(circle(110, 205, 10, fill="#ffffff", stroke=RED, sw=1.2))
    p.append(circle(180, 205, 10, fill="#ffffff", stroke=RED, sw=1.2))
    p.append(circle(250, 205, 10, fill="#ffffff", stroke=RED, sw=1.2))
    p.append(circle(320, 205, 10, fill="#ffffff", stroke=RED, sw=1.2))
    p.append(line(138, 163, 117, 197, color=RED, sw=1.0))
    p.append(line(152, 163, 173, 197, color=RED, sw=1.0))
    p.append(line(278, 163, 257, 197, color=RED, sw=1.0))
    p.append(line(292, 163, 313, 197, color=RED, sw=1.0))
    
    p.append(text(215, 245, "Експоненціальний вибух шляхів: O(2ⁿ)", size=12, color=RED, bold=True))
    p.append(text(215, 268, "Провал на тупиках, виснаження стеку", size=11, color=DARK))

    # Права частина: Симуляція Томпсона (Pike VM)
    p.append(rect(430, 20, 390, 280, fill="#f2f9f4", stroke=GREEN, sw=1.5, rx=8))
    p.append(text(625, 48, "Симуляція Томпсона (RE2 / Rust regex)", size=13, color=GREEN, bold=True))
    p.append(text(625, 68, "Множина активних станів Sₜ", size=11, color=MUTED))
    
    # Кроки симуляції
    steps = [
        ("Символ 'a'₁:", "S₀ = {s₀, s₁, s₂}"),
        ("Символ 'a'₂:", "S₁ = {s₁, s₂, s₃}"),
        ("Символ 'a'₃:", "S₂ = {s₁, s₂, s₃}"),
        ("Символ 'X':", "S₃ = ∅ (Провал без бектрекінгу)"),
    ]
    for i, (lbl, st) in enumerate(steps):
        sy = 110 + i * 42
        p.append(rect(455, sy - 14, 340, 32, fill="#ffffff", stroke=GREEN, sw=1.0, rx=4))
        p.append(text(470, sy + 4, lbl, size=11, color=DARK, bold=True, anchor="start"))
        p.append(text(620, sy + 4, st, size=12, color=BLUE_R, bold=True, anchor="start"))

    p.append(text(625, 268, "Гарантований лінійний час: O(M · N)", size=12, color=GREEN, bold=True))

    render(os.path.join(OUT, "catastrophic-backtracking-vs-thompson.svg"), W, H, "".join(p))

if __name__ == "__main__":
    fig_pipeline()
    fig_thompson_constructions()
    fig_backtracking_vs_nfa()
    print("Figures generated successfully.")
