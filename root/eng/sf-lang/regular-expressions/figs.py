# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_thompson_construction():
    """Конструкція Томпсона: базові будівельні блоки ε-NFA."""
    W, H = 840, 430
    f = []

    f.append(text(W / 2, 28, 'Конструкція Томпсона: перетворення виразу на автомат ε-NFA', size=16, bold=True))

    # Panel 1: Символ 'a'
    x1, y1, w1, h1 = 30, 50, 360, 160
    f.append(rect(x1, y1, w1, h1, fill='#f8fafc', stroke='#cbd5e1', rx=8))
    f.append(text(x1 + 20, y1 + 24, '1. Базовий символ: a', size=13, bold=True, anchor='start'))
    
    # State s0 -> s1 with label 'a'
    cx0, cy0 = x1 + 80, y1 + 90
    cx1, cy1 = x1 + 280, y1 + 90
    f.append(circle(cx0, cy0, 22, fill='#e0f2fe', stroke='#0284c7', sw=2))
    f.append(text(cx0, cy0 + 5, 's₀', size=13, bold=True))
    f.append(circle(cx1, cy1, 22, fill='#e0f2fe', stroke='#0284c7', sw=2))
    f.append(circle(cx1, cy1, 17, fill='#e0f2fe', stroke='#0284c7', sw=1.5))
    f.append(text(cx1, cy1 + 5, 's₁', size=13, bold=True))
    f.append(arrow(cx0 + 22, cy0, cx1 - 22, cy1, color='#0284c7', sw=2))
    f.append(text((cx0 + cx1) / 2, cy0 - 10, 'a', size=14, bold=True, color='#0369a1'))
    f.append(text(x1 + w1 / 2, y1 + 145, 'перехід за єдиним символом', size=11, color=MUTED))

    # Panel 2: Конкатенація A · B
    x2, y2, w2, h2 = 430, 50, 380, 160
    f.append(rect(x2, y2, w2, h2, fill='#f8fafc', stroke='#cbd5e1', rx=8))
    f.append(text(x2 + 20, y2 + 24, '2. Конкатенація: A · B', size=13, bold=True, anchor='start'))
    
    # Block A and Block B connected by epsilon
    bxA, byA = x2 + 30, y2 + 55
    f.append(rect(bxA, byA, 120, 60, fill='#fef3c7', stroke='#d97706', rx=6))
    f.append(text(bxA + 60, byA + 35, 'Автомат A', size=12, bold=True))
    
    bxB, byB = x2 + 230, y2 + 55
    f.append(rect(bxB, byB, 120, 60, fill='#fef3c7', stroke='#d97706', rx=6))
    f.append(text(bxB + 60, byB + 35, 'Автомат B', size=12, bold=True))
    
    f.append(arrow(bxA + 120, byA + 30, bxB, byB + 30, color='#d97706', sw=2))
    f.append(text(bxA + 175, byA + 22, 'ε', size=15, bold=True, color='#b45309'))
    f.append(text(x2 + w2 / 2, y2 + 145, 'вихід A зв’язується з входом B через ε-перехід', size=11, color=MUTED))

    # Panel 3: Чергування (альтернація) A | B
    x3, y3, w3, h3 = 30, 230, 360, 180
    f.append(rect(x3, y3, w3, h3, fill='#f8fafc', stroke='#cbd5e1', rx=8))
    f.append(text(x3 + 20, y3 + 24, '3. Чергування: A | B', size=13, bold=True, anchor='start'))
    
    in_cx, in_cy = x3 + 45, y3 + 100
    out_cx, out_cy = x3 + 315, y3 + 100
    f.append(circle(in_cx, in_cy, 18, fill='#f0fdf4', stroke='#16a34a', sw=2))
    f.append(text(in_cx, in_cy + 5, 'in', size=11, bold=True))
    f.append(circle(out_cx, out_cy, 18, fill='#f0fdf4', stroke='#16a34a', sw=2))
    f.append(circle(out_cx, out_cy, 14, fill='#f0fdf4', stroke='#16a34a', sw=1.2))
    f.append(text(out_cx, out_cy + 5, 'out', size=11, bold=True))
    
    # Sub-blocks A and B
    f.append(rect(x3 + 115, y3 + 55, 120, 38, fill='#fef3c7', stroke='#d97706', rx=4))
    f.append(text(x3 + 175, y3 + 79, 'Автомат A', size=11, bold=True))
    f.append(rect(x3 + 115, y3 + 115, 120, 38, fill='#fef3c7', stroke='#d97706', rx=4))
    f.append(text(x3 + 175, y3 + 139, 'Автомат B', size=11, bold=True))
    
    # Arrows from in to A and B, and from A and B to out
    f.append(arrow(in_cx + 18, in_cy - 5, x3 + 115, y3 + 74, color='#16a34a', sw=1.5))
    f.append(arrow(in_cx + 18, in_cy + 5, x3 + 115, y3 + 134, color='#16a34a', sw=1.5))
    f.append(arrow(x3 + 235, y3 + 74, out_cx - 18, out_cy - 5, color='#16a34a', sw=1.5))
    f.append(arrow(x3 + 235, y3 + 134, out_cx - 18, out_cy + 5, color='#16a34a', sw=1.5))
    f.append(text(x3 + 82, y3 + 60, 'ε', size=13, bold=True, color='#15803d'))
    f.append(text(x3 + 82, y3 + 135, 'ε', size=13, bold=True, color='#15803d'))
    f.append(text(x3 + 270, y3 + 60, 'ε', size=13, bold=True, color='#15803d'))
    f.append(text(x3 + 270, y3 + 135, 'ε', size=13, bold=True, color='#15803d'))

    # Panel 4: Замикання Кліні A*
    x4, y4, w4, h4 = 430, 230, 380, 180
    f.append(rect(x4, y4, w4, h4, fill='#f8fafc', stroke='#cbd5e1', rx=8))
    f.append(text(x4 + 20, y4 + 24, '4. Замикання Кліні: A*', size=13, bold=True, anchor='start'))
    
    k_in_cx, k_in_cy = x4 + 45, y4 + 100
    k_out_cx, k_out_cy = x4 + 335, y4 + 100
    f.append(circle(k_in_cx, k_in_cy, 18, fill='#fdf2f8', stroke='#db2777', sw=2))
    f.append(text(k_in_cx, k_in_cy + 5, 'in', size=11, bold=True))
    f.append(circle(k_out_cx, k_out_cy, 18, fill='#fdf2f8', stroke='#db2777', sw=2))
    f.append(circle(k_out_cx, k_out_cy, 14, fill='#fdf2f8', stroke='#db2777', sw=1.2))
    f.append(text(k_out_cx, k_out_cy + 5, 'out', size=11, bold=True))
    
    # Sub-block A
    f.append(rect(x4 + 125, y4 + 80, 130, 42, fill='#fef3c7', stroke='#d97706', rx=4))
    f.append(text(x4 + 190, y4 + 106, 'Автомат A', size=12, bold=True))
    
    # Direct arrow in -> A and A -> out
    f.append(arrow(k_in_cx + 18, k_in_cy, x4 + 125, k_in_cy, color='#db2777', sw=1.5))
    f.append(text(x4 + 90, k_in_cy - 8, 'ε', size=13, bold=True, color='#be185d'))
    f.append(arrow(x4 + 255, k_out_cy, k_out_cx - 18, k_out_cy, color='#db2777', sw=1.5))
    f.append(text(x4 + 290, k_out_cy - 8, 'ε', size=13, bold=True, color='#be185d'))
    
    # Top bypass: in -> out (zero matches)
    f.append(line(k_in_cx, k_in_cy - 18, k_in_cx, y4 + 50, color='#db2777', sw=1.5))
    f.append(line(k_in_cx, y4 + 50, k_out_cx, y4 + 50, color='#db2777', sw=1.5))
    f.append(arrow(k_out_cx, y4 + 50, k_out_cx, k_out_cy - 18, color='#db2777', sw=1.5))
    f.append(text(x4 + 190, y4 + 44, 'ε (0 повторів)', size=11, bold=True, color='#be185d'))
    
    # Bottom loop: out(A) -> in(A) (repeat)
    f.append(line(x4 + 240, y4 + 122, x4 + 240, y4 + 155, color='#db2777', sw=1.5))
    f.append(line(x4 + 240, y4 + 155, x4 + 140, y4 + 155, color='#db2777', sw=1.5))
    f.append(arrow(x4 + 140, y4 + 155, x4 + 140, y4 + 122, color='#db2777', sw=1.5))
    f.append(text(x4 + 190, y4 + 168, 'ε (повторний прохід)', size=11, bold=True, color='#be185d'))

    render(os.path.join(OUT, 'thompson-nfa-construction.svg'), W, H, *f)


def fig_dfa_vs_backtracking():
    """Порівняння виконання: паралельний DFA/NFA проти бектрекінгу PCRE."""
    W, H = 820, 360
    f = []

    f.append(text(W / 2, 28, 'Моделі виконання: автоматний потік проти рекурсивного пошуку', size=16, bold=True))

    # Left Column: DFA / Thompson NFA (Linear streaming)
    lx, ly, lw, lh = 25, 55, 370, 285
    f.append(rect(lx, ly, lw, lh, fill='#f0fdf4', stroke='#86efac', rx=8))
    f.append(text(lx + lw / 2, ly + 28, 'Автоматний рушій (DFA / Thompson NFA)', size=13, bold=True, color='#15803d'))
    f.append(text(lx + lw / 2, ly + 48, 'Час: O(N) строго лінійний | Пам’ять: O(M)', size=11, color='#166534'))

    # Streaming flow
    steps_y = [ly + 80, ly + 130, ly + 180, ly + 230]
    labels = [
        ('Символ c₁', 'Множина станів {s₀, s₁}'),
        ('Символ c₂', 'Множина станів {s₂, s₅}'),
        ('Символ c₃', 'Множина станів {s₃, s₆}'),
        ('Кінець рядка', 'Фінальний стан ∈ Активні → Збіг!'),
    ]
    for i, (sym, st) in enumerate(labels):
        sy = steps_y[i]
        f.append(rect(lx + 20, sy, 110, 34, fill='#dcfce7', stroke='#4ade80', rx=4))
        f.append(text(lx + 75, sy + 22, sym, size=11.5, bold=True, color='#14532d'))
        f.append(arrow(lx + 130, sy + 17, lx + 165, sy + 17, color='#16a34a', sw=1.5))
        f.append(rect(lx + 165, sy, 185, 34, fill='#ffffff', stroke='#86efac', rx=4))
        f.append(text(lx + 257, sy + 22, st, size=10.5, color='#166534'))

    f.append(text(lx + lw / 2, ly + 272, 'Всі шляхи обробляються синхронно, відкатів немає', size=11, bold=True, color='#15803d'))

    # Right Column: Backtracking NFA (PCRE / Perl / Python)
    rx, ry, rw, rh = 425, 55, 370, 285
    f.append(rect(rx, ry, rw, rh, fill='#fef2f2', stroke='#fca5a5', rx=8))
    f.append(text(rx + rw / 2, ry + 28, 'Бектрекінг-рушій (PCRE / Perl / Python / JS)', size=13, bold=True, color='#b91c1c'))
    f.append(text(rx + rw / 2, ry + 48, 'Час: O(2ⁿ) найгірший | Підтримка: Lookahead, \\1', size=11, color='#991b1b'))

    # Tree search simulation
    f.append(circle(rx + 185, ry + 85, 16, fill='#fee2e2', stroke='#ef4444', sw=1.5))
    f.append(text(rx + 185, ry + 89, 'Старт', size=10, bold=True))

    # Branch left (deep exploration)
    f.append(arrow(rx + 175, ry + 95, rx + 100, ry + 135, color='#ef4444', sw=1.5))
    f.append(circle(rx + 90, ry + 145, 16, fill='#fee2e2', stroke='#ef4444', sw=1.5))
    f.append(text(rx + 90, ry + 149, 'Гілка 1', size=10, bold=True))

    f.append(arrow(rx + 90, ry + 160, rx + 60, ry + 195, color='#ef4444', sw=1.5))
    f.append(rect(rx + 25, ry + 200, 75, 26, fill='#fca5a5', stroke='#dc2626', rx=3))
    f.append(text(rx + 62, ry + 217, 'Глухий кут ✗', size=10, bold=True, color='#7f1d1d'))

    # Rollback dashed arrow
    f.append(line(rx + 60, ry + 195, rx + 120, ry + 155, color='#dc2626', sw=1.5, dash='3,3'))
    f.append(arrow(rx + 120, ry + 155, rx + 175, ry + 100, color='#dc2626', sw=1.5))
    f.append(text(rx + 160, ry + 150, 'відкат стеку', size=10, bold=True, color='#b91c1c'))

    # Branch right (try next alternative)
    f.append(arrow(rx + 195, ry + 95, rx + 270, ry + 135, color='#b91c1c', sw=1.5))
    f.append(circle(rx + 280, ry + 145, 16, fill='#dcfce7', stroke='#16a34a', sw=1.5))
    f.append(text(rx + 280, ry + 149, 'Гілка 2', size=10, bold=True))
    f.append(arrow(rx + 280, ry + 160, rx + 280, ry + 200, color='#16a34a', sw=1.5))
    f.append(rect(rx + 240, ry + 205, 80, 26, fill='#86efac', stroke='#16a34a', rx=3))
    f.append(text(rx + 280, ry + 222, 'Збіг знайшов ✓', size=10, bold=True, color='#14532d'))

    f.append(text(rx + rw / 2, ry + 272, 'Пошук у глибину зі збереженням точок повернення', size=11, bold=True, color='#b91c1c'))

    render(os.path.join(OUT, 'dfa-vs-backtracking.svg'), W, H, *f)


def fig_dialects_hierarchy():
    """Ієрархія та відмінності синтаксису діалектів: BRE, ERE, PCRE."""
    W, H = 840, 390
    f = []

    f.append(text(W / 2, 28, 'Еволюція діалектів регулярних виразів та правила екранування', size=16, bold=True))

    # Box 1: BRE (Basic Regular Expressions)
    b1_x, b1_y, b1_w, b1_h = 30, 55, 240, 310
    f.append(rect(b1_x, b1_y, b1_w, b1_h, fill='#f1f5f9', stroke='#94a3b8', rx=8))
    f.append(text(b1_x + b1_w / 2, b1_y + 26, 'BRE (POSIX Базові)', size=13, bold=True, color='#1e293b'))
    f.append(text(b1_x + b1_w / 2, b1_y + 44, 'grep, sed, ed, vi', size=11, color='#475569'))
    f.append(line(b1_x + 15, b1_y + 55, b1_x + b1_w - 15, b1_y + 55, color='#cbd5e1'))

    bre_items = [
        'Метасимволи: . ^ $ * [ ]',
        'Групи: \\( ... \\)',
        'Діапазон лічильника: \\{m,n\\}',
        'Зворотні посилання: \\1 ... \\9',
        'Символи ( { + ? | є ЛІТЕРАЛАМИ',
        'Немає вбудованого +, ?, |',
        'GNU-розширення: \\+, \\?, \\|',
    ]
    for i, item in enumerate(bre_items):
        f.append(text(b1_x + 15, b1_y + 80 + i * 32, '• ' + item, size=10.5, color='#334155', anchor='start'))

    # Box 2: ERE (Extended Regular Expressions)
    b2_x, b2_y, b2_w, b2_h = 295, 55, 250, 310
    f.append(rect(b2_x, b2_y, b2_w, b2_h, fill='#eff6ff', stroke='#93c5fd', rx=8))
    f.append(text(b2_x + b2_w / 2, b2_y + 26, 'ERE (POSIX Розширені)', size=13, bold=True, color='#1e40af'))
    f.append(text(b2_x + b2_w / 2, b2_y + 44, 'egrep, awk, regcomp(REG_EXTENDED)', size=11, color='#3b82f6'))
    f.append(line(b2_x + 15, b2_y + 55, b2_x + b2_w - 15, b2_y + 55, color='#bfdbfe'))

    ere_items = [
        'Всі можливості BRE плюс:',
        'Групи БЕЗ слешів: ( ... )',
        'Лічильники: {m,n}',
        'Квантифікатори: +, ?',
        'Чергування: |',
        'Літерали: \\(, \\{, \\+, \\?, \\|',
        'У стандарті НЕМАЄ \\1 (посилань)',
    ]
    for i, item in enumerate(ere_items):
        f.append(text(b2_x + 15, b2_y + 80 + i * 32, '• ' + item, size=10.5, color='#1e3a8a', anchor='start'))

    # Box 3: PCRE / Сучасні рушії
    b3_x, b3_y, b3_w, b3_h = 570, 55, 240, 310
    f.append(rect(b3_x, b3_y, b3_w, b3_h, fill='#faf5ff', stroke='#d8b4fe', rx=8))
    f.append(text(b3_x + b3_w / 2, b3_y + 26, 'PCRE (Perl-сумісні)', size=13, bold=True, color='#6b21a8'))
    f.append(text(b3_x + b3_w / 2, b3_y + 44, 'PCRE2, Python, JS, Java, PHP', size=11, color='#9333ea'))
    f.append(line(b3_x + 15, b3_y + 55, b3_x + b3_w - 15, b3_y + 55, color='#e9d5ff'))

    pcre_items = [
        'Всі можливості ERE плюс:',
        'Нефіксуючі групи: (?: ... )',
        'Lookahead: (?= ... ), (?! ... )',
        'Lookbehind: (?<= ... ), (?<! ... )',
        'Атомарні групи: (?> ... )',
        'Ліниві квантифікатори: *?, +?',
        'Посесивні: ++, *+, ?+',
        'Класи: \\d, \\w, \\s, \\b, \\p{L}',
    ]
    for i, item in enumerate(pcre_items):
        f.append(text(b3_x + 15, b3_y + 80 + i * 29, '• ' + item, size=10.5, color='#581c87', anchor='start'))

    # Evolution arrows connecting boxes
    f.append(arrow(b1_x + b1_w, b1_y + 150, b2_x, b1_y + 150, color='#3b82f6', sw=2))
    f.append(arrow(b2_x + b2_w, b2_y + 150, b3_x, b2_y + 150, color='#9333ea', sw=2))

    render(os.path.join(OUT, 'bre-vs-ere-vs-pcre-dialects.svg'), W, H, *f)


def fig_redos_explosion():
    """Катастрофічний бектрекінг (ReDoS): комбінаторний вибух розбиттів."""
    W, H = 840, 370
    f = []

    f.append(text(W / 2, 26, 'Катастрофічний бектрекінг (ReDoS): вираз (a+)+$ на рядку "aaaa!"', size=16, bold=True))

    # Pattern box
    f.append(rect(180, 48, 480, 42, fill='#fef2f2', stroke='#ef4444', rx=6))
    f.append(text(420, 68, 'Вираз: (a+)+$   |   Вхід: "aaaa!" (4 символи "a" + невдача на "!")', size=12.5, bold=True, color='#991b1b'))
    f.append(text(420, 83, 'Кожне розбиття N символів "a" перевіряється окремо перед фіксацією відмови', size=10.5, color='#b91c1c'))

    # Tree root
    rx, ry = 420, 115
    f.append(circle(rx, ry, 12, fill='#fee2e2', stroke='#b91c1c', sw=1.5))
    f.append(text(rx, ry + 4, '4a', size=10, bold=True))

    # Level 1 Partitions (8 combinatorial ways to partition 4 into sums of positive integers)
    # 8 leaves at the bottom
    leaves = [
        ('1+1+1+1', 60),
        ('1+1+2', 160),
        ('1+2+1', 260),
        ('1+3', 360),
        ('2+1+1', 480),
        ('2+2', 580),
        ('3+1', 680),
        ('4', 780),
    ]

    for label, lx in leaves:
        # Draw branch from root area to leaf
        mid_x = (rx + lx) / 2
        f.append(line(rx, ry + 12, mid_x, 160, color='#fca5a5', sw=1.2))
        f.append(arrow(mid_x, 160, lx, 215, color='#ef4444', sw=1.2))
        
        # Partition Box
        f.append(rect(lx - 42, 220, 84, 30, fill='#fff1f2', stroke='#f43f5e', rx=4))
        f.append(text(lx, 239, label, size=11, bold=True, color='#9f1239'))
        
        # Mismatch indicator below each leaf
        f.append(arrow(lx, 252, lx, 275, color='#be123c', sw=1.5))
        f.append(rect(lx - 40, 278, 80, 24, fill='#fecdd3', stroke='#e11d48', rx=3))
        f.append(text(lx, 294, '≠ "!" (відкат)', size=9.5, bold=True, color='#881337'))

    # Formula Box
    body, bw, bh = textbox(W / 2, 342, size=12, pad=10,
                           fill='#f8fafc', stroke='#94a3b8',
                           s='Кількість розбиттів довжини N = 2^(N-1). Для N=30: ~536 мільйонів кроків → секунди зависання процесора.')
    f.append(body)

    render(os.path.join(OUT, 'redos-backtracking-explosion.svg'), W, H, *f)


if __name__ == '__main__':
    fig_thompson_construction()
    fig_dfa_vs_backtracking()
    fig_dialects_hierarchy()
    fig_redos_explosion()
    print("All figures generated successfully.")
