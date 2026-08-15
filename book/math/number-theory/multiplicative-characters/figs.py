import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, mtext, textbox, arrow, POS, NEG, FIELD, INK, MUTED, FILL, BG
except ImportError:
    print("Error importing svgkit")
    sys.exit(1)

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))

def draw_character_orthogonality():
    frags = []
    # Background card
    frags.append(rect(10, 10, 780, 460, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    
    # Left panel: Unit Circle representation of roots of unity for Z/7Z* (order 6)
    frags.append(rect(25, 25, 340, 430, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(195, 50, "Комплексна колоподібна діаграма (Z/7Z)*", size=13, bold=True, color=INK))
    frags.append(text(195, 68, "Шості корені з одиниці: ζ₆ = exp(2πi / 6)", size=11, italic=True, color=MUTED))
    
    cx, cy, r = 195, 240, 120
    frags.append(circle(cx, cy, r, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    frags.append(line(cx - r - 20, cy, cx + r + 20, cy, color="#cbd5e1", sw=1.0, dash="4,4"))
    frags.append(line(cx, cy - r - 20, cx, cy + r + 20, color="#cbd5e1", sw=1.0, dash="4,4"))
    
    # Axes labels
    frags.append(text(cx + r + 25, cy + 4, "Re", size=11, bold=True, color=MUTED))
    frags.append(text(cx, cy - r - 25, "Im", size=11, bold=True, color=MUTED))
    
    # 6 roots of unity
    labels = ["1", "e^(iπ/3)", "e^(2iπ/3)", "-1", "e^(4iπ/3)", "e^(5iπ/3)"]
    angles = [0, 60, 120, 180, 240, 300]
    
    for i, (ang, lbl) in enumerate(zip(angles, labels)):
        rad = math.radians(ang)
        px = cx + r * math.cos(rad)
        py = cy - r * math.sin(rad)
        frags.append(line(cx, cy, px, py, color="#94a3b8", sw=1.0))
        frags.append(circle(px, py, 6, fill=POS if i == 0 else (FIELD if i % 2 == 0 else NEG), stroke=INK, sw=1.2))
        
        # Position label outside
        lx = cx + (r + 28) * math.cos(rad)
        ly = cy - (r + 28) * math.sin(rad) + 4
        frags.append(text(lx, ly, lbl, size=11, bold=True, color=INK))
        
    frags.append(text(195, 410, "Сума векторів будь-якого нетривіального", size=11, bold=True, color=POS))
    frags.append(text(195, 430, "характеру по групі дорівнює 0 (баланс)", size=11, color=INK))

    # Right panel: Character Table Modulo 7
    frags.append(rect(380, 25, 410, 430, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(585, 50, "Матриця характерів χ_m(g^k) mod 7", size=13, bold=True, color=INK))
    
    # Table grid
    tx0, ty0 = 400, 80
    cw, ch = 55, 42
    
    headers_col = ["g^k:", "1", "3", "2", "6", "4", "5"]
    headers_row = ["χ₀", "χ₁", "χ₂", "χ₃", "χ₄", "χ₅"]
    
    # Column headers
    for j, h in enumerate(headers_col):
        bx = tx0 + j * cw
        frags.append(rect(bx, ty0, cw, ch - 8, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=2))
        frags.append(text(bx + cw/2, ty0 + 22, h, size=11, bold=True, color=INK))
        
    # Matrix body
    matrix_vals = [
        ["1", "1", "1", "1", "1", "1"],
        ["1", "ζ", "ζ²", "-1", "ζ⁴", "ζ⁵"],
        ["1", "ζ²", "ζ⁴", "1", "ζ²", "ζ⁴"],
        ["1", "-1", "1", "-1", "1", "-1"],
        ["1", "ζ⁴", "ζ²", "1", "ζ⁴", "ζ²"],
        ["1", "ζ⁵", "ζ⁴", "-1", "ζ²", "ζ"]
    ]
    
    for i, row in enumerate(matrix_vals):
        ry = ty0 + (i + 1) * ch - 4
        # Row header
        frags.append(rect(tx0, ry, cw, ch - 6, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=2))
        frags.append(text(tx0 + cw/2, ry + 22, headers_row[i], size=11, bold=True, color=NEG if i>0 else INK))
        
        for j, val in enumerate(row):
            rx = tx0 + (j + 1) * cw
            bg_cell = "#fef2f2" if i == 3 and j % 2 == 1 else ("#f0fdf4" if i == 0 else "#ffffff")
            frags.append(rect(rx, ry, cw, ch - 6, fill=bg_cell, stroke="#e2e8f0", sw=1.0, rx=2))
            frags.append(text(rx + cw/2, ry + 22, val, size=11, bold=(val=="1" or val=="-1"), color=INK))
            
    # Bottom note on orthogonality
    frags.append(text(585, 385, "Рядки ортогональні: ∑_{g} χ_i(g) χ̄_j(g) = 6 · δ_{ij}", size=11, bold=True, color=FIELD))
    frags.append(text(585, 410, "Стовпчики ортогональні: ∑_{χ} χ(g₁) χ̄(g₂) = 6 · δ_{g₁g₂}", size=11, bold=True, color=NEG))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-character-orthogonality.svg'), 800, 480, *frags, title="Візуалізація ортогональності характерів")

def draw_additive_multiplicative_bridge():
    frags = []
    frags.append(rect(10, 10, 780, 430, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    
    frags.append(text(400, 40, "Міст між адитивним і мультиплікативним світом: Суми Ґаусса", size=15, bold=True, color=INK))
    frags.append(text(400, 62, "Перетворення Фур'є мультиплікативного характеру χ на адитивній групі Z/qZ", size=12, italic=True, color=MUTED))
    
    # Input node
    b_in, w_in, h_in = textbox(110, 200, "Вхідний елемент n\n(n ∈ Z/qZ)", size=12, pad=12, fill="#f1f5f9", stroke="#64748b", bold=True)
    frags.append(b_in)
    
    # Split arrows
    frags.append(arrow(175, 175, 260, 130, color="#64748b", sw=2.0))
    frags.append(arrow(175, 225, 260, 270, color="#64748b", sw=2.0))
    
    # Branch 1: Multiplicative character
    b_mult, w_mult, h_mult = textbox(380, 130, "Мультиплікативний характер χ(n)\nХомоморфізм (Z/qZ)* → C*\nПереводить множення у фазу", size=12, pad=12, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(b_mult)
    
    # Branch 2: Additive character
    b_add, w_add, h_add = textbox(380, 270, "Адитивний характер e_q(a·n)\ne_q(x) = exp(2πi x / q)\nПереводить додавання у фазу", size=12, pad=12, fill="#f0fdf4", stroke=FIELD, bold=True)
    frags.append(b_add)
    
    # Merging arrows to product
    frags.append(arrow(500, 130, 580, 175, color=NEG, sw=2.0))
    frags.append(arrow(500, 270, 580, 225, color=FIELD, sw=2.0))
    
    # Product & Accumulation node
    b_sum, w_sum, h_sum = textbox(670, 200, "Сума Ґаусса g(χ, a)\n∑_{n} χ(n) · e_q(a·n)\nОбгортка взаємодії", size=12, pad=12, fill="#fef2f2", stroke=POS, bold=True)
    frags.append(b_sum)
    
    # Key property highlight box at bottom
    b_prop, w_prop, h_prop = textbox(400, 370, "Фундаментальна властивість привідного характеру: |g(χ)| = √q\nСума Ґаусса діє як дискретна спектральна згортка, зсуваючи аргумент: g(χ, a) = χ̄(a) · g(χ)", size=12, pad=12, fill="#faf5ff", stroke="#9333ea", bold=True)
    frags.append(b_prop)
    
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-additive-multiplicative-bridge.svg'), 800, 450, *frags, title="Взаємозв'язок характерів через суму Ґаусса")

def draw_dirichlet_character_table():
    frags = []
    frags.append(rect(10, 10, 780, 460, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    
    frags.append(text(400, 40, "Структура характерів Діріхле за складеним модулем q = 15", size=15, bold=True, color=INK))
    frags.append(text(400, 62, "Ізоморфізм (Z/15Z)* ≅ (Z/3Z)* × (Z/5Z)* ≅ Z₂ × Z₄ (Порядок φ(15) = 8)", size=12, italic=True, color=MUTED))
    
    # Left column in a group transform to avoid panel rect collision
    frags.append('<g transform="translate(0,0)">')
    frags.append(rect(25, 85, 240, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(145, 110, "Факторизація модулів", size=13, bold=True, color=INK))
    
    b_m3, _, _ = textbox(145, 160, "Модуль d = 3\n(Z/3Z)* ≅ Z₂\n2 характери (χ₃⁽⁰⁾, χ₃⁽¹⁾)", size=11, pad=8, fill="#eff6ff", stroke=NEG)
    frags.append(b_m3)
    
    frags.append(text(145, 220, "⊗ (Тензорний добуток)", size=12, bold=True, color=MUTED))
    
    b_m5, _, _ = textbox(145, 280, "Модуль d = 5\n(Z/5Z)* ≅ Z₄\n4 характери (χ₅⁽⁰⁾...χ₅⁽³⁾)", size=11, pad=8, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_m5)
    
    frags.append(arrow(145, 325, 145, 355, color=INK, sw=1.5))
    
    b_m15, _, _ = textbox(145, 395, "Разом: 2 × 4 = 8 характерів\nχ₁₅(n) = χ₃(n mod 3) · χ₅(n mod 5)", size=11, pad=8, fill="#fef2f2", stroke=POS, bold=True)
    frags.append(b_m15)
    frags.append('</g>')
    
    # Right column: Conductor classification table
    frags.append(rect(280, 85, 490, 365, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(525, 110, "Класифікація за провідником (Conductor f_χ)", size=13, bold=True, color=INK))
    
    # Headers
    y0 = 135
    frags.append(rect(295, y0, 100, 30, fill="#e2e8f0", stroke="#cbd5e1", rx=2))
    frags.append(text(345, y0 + 19, "Провідник f_χ", size=11, bold=True, color=INK))
    
    frags.append(rect(400, y0, 120, 30, fill="#e2e8f0", stroke="#cbd5e1", rx=2))
    frags.append(text(460, y0 + 19, "Характер", size=11, bold=True, color=INK))
    
    frags.append(rect(525, y0, 230, 30, fill="#e2e8f0", stroke="#cbd5e1", rx=2))
    frags.append(text(640, y0 + 19, "Властивість та тип", size=11, bold=True, color=INK))
    
    rows = [
        ("f = 1", "χ₀ (Головний)", "Індукований з 1; χ₀(n)=1 для gcd(n,15)=1", "#f1f5f9", INK),
        ("f = 3", "χ₁₅⁽³⁾", "Індукований з mod 3 (нетривіальний χ₃)", "#eff6ff", NEG),
        ("f = 5", "χ₁₅⁽⁵,¹⁾, χ₁₅⁽⁵,²⁾...", "3 характери, індуковані з mod 5", "#f0fdf4", FIELD),
        ("f = 15", "χ₁₅⁽¹⁵,¹⁾, χ₁₅⁽¹⁵,²⁾...", "3 первісні (primitive) характери mod 15", "#fef2f2", POS)
    ]
    
    for i, (f_val, ch_name, desc, bg_c, txt_c) in enumerate(rows):
        ry = y0 + 40 + i * 42
        frags.append(rect(295, ry, 100, 36, fill=bg_c, stroke="#cbd5e1", rx=2))
        frags.append(text(345, ry + 22, f_val, size=11, bold=True, color=txt_c))
        
        frags.append(rect(400, ry, 120, 36, fill=bg_c, stroke="#cbd5e1", rx=2))
        frags.append(text(460, ry + 22, ch_name, size=11, bold=True, color=INK))
        
        frags.append(rect(525, ry, 230, 36, fill=bg_c, stroke="#cbd5e1", rx=2))
        frags.append(text(640, ry + 22, desc, size=10, color=INK))
        
    frags.append(text(525, 360, "Первісний характер mod q не піднімається з жодного дільника d < q.", size=11, italic=True, color=MUTED))
    frags.append(text(525, 385, "Провідник f_χ — це мінімальний модуль, на якому характер є первісним.", size=11, bold=True, color=INK))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-dirichlet-character-table.svg'), 800, 480, *frags, title="Структура характерів за складеним модулем 15")

if __name__ == '__main__':
    draw_character_orthogonality()
    draw_additive_multiplicative_bridge()
    draw_dirichlet_character_table()
