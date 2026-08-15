import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, mtext, textbox, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL
except ImportError:
    print("ERROR: svgkit not found.")
    sys.exit(1)

def draw_gaussian_lattice():
    """Малює гратку цілих чисел Ґаусса ℤ[i] з колом радіуса √13 та точками (±3, ±2) і (±2, ±3)."""
    frags = []
    w, h = 640, 440
    cx, cy = 320, 220
    scale = 45 # 1 unit = 45px
    
    # Фонові лінії сітки
    for u in range(-6, 7):
        x = cx + u * scale
        frags.append(line(x, 40, x, 400, color="#e5e7eb", sw=1.0))
    for v in range(-4, 5):
        y = cy - v * scale
        frags.append(line(40, y, 600, y, color="#e5e7eb", sw=1.0))
        
    # Головні осі Дійсна (Re) та Уявна (Im)
    frags.append(arrow(40, cy, 600, cy, color=LINE, sw=1.8))
    frags.append(arrow(cx, 400, cx, 40, color=LINE, sw=1.8))
    frags.append(text(590, cy - 10, "Re", size=13, bold=True, color=INK))
    frags.append(text(cx + 12, 50, "Im", size=13, bold=True, color=INK))
    
    # Коло радіуса √13 (13 = 3² + 2²)
    r_px = math.sqrt(13) * scale
    frags.append(circle(cx, cy, r_px, fill="none", stroke="#2563eb", sw=2.0))
    
    # Всі вузли гратки
    for u in range(-5, 6):
        for v in range(-3, 4):
            x = cx + u * scale
            y = cy - v * scale
            val = u*u + v*v
            if val == 13:
                # Точки розкладу 13 = 3² + 2²
                frags.append(circle(x, y, 6, fill=POS, stroke="#991b1b", sw=1.5))
            else:
                frags.append(circle(x, y, 2.5, fill=MUTED, stroke="none"))
                
    # Запис радіуса та вектора для z = 3 + 2i
    zx, zy = cx + 3 * scale, cy - 2 * scale
    frags.append(line(cx, cy, zx, zy, color="#dc2626", sw=2.2))
    frags.append(text(cx + 65, cy - 55, "|z|² = 3² + 2² = 13", size=13, bold=True, color="#dc2626"))
    frags.append(text(zx + 15, zy - 5, "z = 3 + 2i", size=13, bold=True, color=INK))
    
    # Спряжене число z_bar = 3 - 2i
    zbx, zby = cx + 3 * scale, cy + 2 * scale
    frags.append(line(cx, cy, zbx, zby, color="#059669", sw=2.2))
    frags.append(text(zbx + 15, zby + 12, "z̄ = 3 − 2i", size=13, bold=True, color="#059669"))
    
    # Підпис координатних міток
    for u in [-3, -1, 1, 3]:
        frags.append(text(cx + u * scale, cy + 18, str(u), size=11, color=MUTED))
    for v in [-2, 2]:
        frags.append(text(cx - 15, cy - v * scale + 4, f"{v}i", size=11, color=MUTED))
        
    os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'gaussian-lattice.svg')
    render(out_path, w, h, *frags, title="Гратка цілих чисел Ґаусса ℤ[i] та розклад n = a² + b²")
    print(f"Generated: {out_path}")

def draw_prime_split_structure():
    """Малює класифікаційне дерево простих чисел за модулем 4 та їхньої поведінки в ℤ[i]."""
    frags = []
    w, h = 640, 360
    
    # Корінь: Прості числа p
    b_root, _, _ = textbox(320, 50, "Прості числа p ∈ ℕ", size=15, bold=True, fill="#f3f4f6", stroke="#374151")
    frags.append(b_root)
    
    # Три гілки
    # Гілка 1: p = 2
    b1 = fitbox(40, 140, 170, 160, 
                "p = 2 (парне просте)\n\n2 = 1² + 1²\n\nРозгалужене в ℤ[i]:\n2 = −i·(1 + i)²", 
                size=12, fill="#fef3c7", stroke="#d97706")
    frags.append(b1)
    frags.append(arrow(260, 75, 125, 140, color="#d97706", sw=1.8))
    
    # Гілка 2: p ≡ 1 (mod 4)
    b2 = fitbox(235, 140, 170, 160, 
                "p ≡ 1 (mod 4)\n\np = a² + b²\n(Теорема Ферма)\n\nРозкладається в ℤ[i]:\np = (a + bi)(a − bi)", 
                size=12, fill="#dcfce7", stroke="#16a34a")
    frags.append(b2)
    frags.append(arrow(320, 75, 320, 140, color="#16a34a", sw=1.8))
    
    # Гілка 3: p ≡ 3 (mod 4)
    b3 = fitbox(430, 140, 170, 160, 
                "p ≡ 3 (mod 4)\n\np ≠ a² + b²\n(Не є сумою квадратів)\n\nІнертне в ℤ[i]:\nлишається простим", 
                size=12, fill="#fee2e2", stroke="#dc2626")
    frags.append(b3)
    frags.append(arrow(380, 75, 515, 140, color="#dc2626", sw=1.8))
    
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'prime-split-structure.svg')
    render(out_path, w, h, *frags, title="Класифікація простих чисел за модулем 4")
    print(f"Generated: {out_path}")

if __name__ == '__main__':
    draw_gaussian_lattice()
    draw_prime_split_structure()
