import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, rect, line, text, circle, POS

def draw_euler_product():
    frags = []
    
    # Background and Title
    frags.append(rect(0, 0, 800, 400, fill="#1e293b"))
    frags.append(text(400, 40, "Тотожність та добуток Ейлера для Дзета-функції", size=20, bold=True, color="#e2e8f0", anchor="middle"))
    frags.append(text(400, 75, "ζ(s) = ∑ (1 / nˢ) = ∏ (1 / (1 - p⁻ˢ))", size=18, bold=True, color="#38bdf8", anchor="middle"))
    
    # Left Box: Sum over All Integers
    frags.append(rect(60, 120, 300, 220, fill="#0f172a", stroke="#3b82f6", sw=2, rx=12))
    frags.append(text(210, 150, "Дискретна сума (усі n ∈ ℕ)", size=15, bold=True, color="#60a5fa", anchor="middle"))
    frags.append(text(210, 195, "1 + 1/2ˢ + 1/3ˢ + 1/4ˢ + 1/5ˢ + ...", size=14, color="#94a3b8", anchor="middle"))
    frags.append(text(210, 240, "Сума за канонічним розкладом:", size=13, color="#cbd5e1", anchor="middle"))
    frags.append(text(210, 275, "∑ (p₁ᵃ¹ · p₂ᵃ² ... pₖᵃᵏ)⁻ˢ", size=14, color="#f59e0b", anchor="middle"))
    
    # Equals Sign
    frags.append(text(400, 230, "=", size=36, bold=True, color="#38bdf8", anchor="middle"))
    
    # Right Box: Product over Primes
    frags.append(rect(440, 120, 300, 220, fill="#0f172a", stroke="#10b981", sw=2, rx=12))
    frags.append(text(590, 150, "Нескінченний добуток (p ∈ ℙ)", size=15, bold=True, color="#34d399", anchor="middle"))
    frags.append(text(590, 195, "(1 + 1/2ˢ + ...) · (1 + 1/3ˢ + ...)", size=13, color="#94a3b8", anchor="middle"))
    frags.append(text(590, 240, "Геометричні прогресії множників:", size=13, color="#cbd5e1", anchor="middle"))
    frags.append(text(590, 275, "∏ (1 / (1 - p⁻ˢ))", size=16, bold=True, color="#10b981", anchor="middle"))
    
    os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'fig-euler-product.svg')
    render(out_path, 800, 400, *frags, title="Тотожність та добуток Ейлера")
    print("Generated fig-euler-product.svg successfully.")

if __name__ == "__main__":
    draw_euler_product()
