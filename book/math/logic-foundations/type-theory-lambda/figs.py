import sys, os

sys.path.append(os.path.abspath('../../../../scripts'))
import svgkit

def draw_derivation():
    # Width and height
    W = 850
    H = 200
    
    os.makedirs('img', exist_ok=True)
    
    frags = []
    
    # Abstraction Rule
    x_abs = 200
    y_line = 100
    line_w = 200
    
    frags.append(svgkit.text(x_abs, y_line - 15, "Γ, x : τ₁ ⊢ e : τ₂", size=18, anchor="middle", bold=True))
    frags.append(svgkit.line(x_abs - line_w/2, y_line, x_abs + line_w/2, y_line, sw=2))
    frags.append(svgkit.text(x_abs + line_w/2 + 10, y_line + 5, "[Abs]", size=16, anchor="start", italic=True, color=svgkit.MUTED))
    frags.append(svgkit.text(x_abs, y_line + 25, "Γ ⊢ λx.e : τ₁ → τ₂", size=18, anchor="middle", bold=True))
    
    # Application Rule
    x_app = 600
    y_line2 = 100
    line2_w = 340
    
    frags.append(svgkit.text(x_app - 80, y_line2 - 15, "Γ ⊢ e₁ : τ₁ → τ₂", size=18, anchor="middle", bold=True))
    frags.append(svgkit.text(x_app + 80, y_line2 - 15, "Γ ⊢ e₂ : τ₁", size=18, anchor="middle", bold=True))
    frags.append(svgkit.line(x_app - line2_w/2, y_line2, x_app + line2_w/2, y_line2, sw=2))
    frags.append(svgkit.text(x_app + line2_w/2 + 10, y_line2 + 5, "[App]", size=16, anchor="start", italic=True, color=svgkit.MUTED))
    frags.append(svgkit.text(x_app, y_line2 + 25, "Γ ⊢ e₁ e₂ : τ₂", size=18, anchor="middle", bold=True))
    
    svgkit.render('img/fig-type-derivation.svg', W, H, *frags, title="Правила виводу типів: Абстракція та Аплікація")

if __name__ == '__main__':
    draw_derivation()
