import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
import svgkit

def generate_prime_sieve():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-prime-sieve.svg")
    
    frags = []
    
    cell_size = 70
    margin_x = 50
    margin_y = 50
    
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
    
    for i in range(1, 101):
        row = (i - 1) // 10
        col = (i - 1) % 10
        
        x = margin_x + col * cell_size
        y = margin_y + row * cell_size
        cx = x + cell_size / 2 - 2
        cy = y + cell_size / 2 - 2
        
        if i == 1:
            bg_color = "#e0e0e0"
            stroke_color = "#cccccc"
        elif i in primes:
            bg_color = "#c8e6c9"
            stroke_color = "#2e7d32"
        else:
            bg_color = "#ffebee"
            stroke_color = "#c62828"
            
        frags.append(svgkit.rect(x, y, cell_size-4, cell_size-4, fill=bg_color, stroke=stroke_color, sw=2, rx=5))
        frags.append(svgkit.text(cx, cy + 5, str(i), size=24, color="#000000", bold=(i in primes)))
        
        if i not in primes and i != 1:
            frags.append(svgkit.line(x + 5, y + 5, x + cell_size - 9, y + cell_size - 9, color="#c62828", sw=3))
            frags.append(svgkit.line(x + cell_size - 9, y + 5, x + 5, y + cell_size - 9, color="#c62828", sw=3))
            
    svgkit.render(out_path, 800, 800, *frags)

if __name__ == "__main__":
    generate_prime_sieve()
