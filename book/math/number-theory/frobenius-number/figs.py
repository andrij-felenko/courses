import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def create_frobenius_line():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-frobenius-coin-line.svg")
    
    frags = []
    
    # Малюємо вісь
    frags.append(svgkit.line(50, 100, 750, 100, color=svgkit.LINE, sw=2))
    
    # Номінали 3 і 5
    a, b = 3, 5
    max_val = 15
    reachable = set([0])
    for i in range(1, max_val + 1):
        if i >= a and (i - a) in reachable:
            reachable.add(i)
        if i >= b and (i - b) in reachable:
            reachable.add(i)
            
    for i in range(max_val + 1):
        x = 50 + (700 / max_val) * i
        
        # Позначка на осі
        frags.append(svgkit.line(x, 95, x, 105, color=svgkit.LINE, sw=1))
        frags.append(svgkit.text(x, 120, str(i), size=12, anchor="middle"))
        
        if i in reachable:
            frags.append(svgkit.circle(x, 90, 8, fill="#27ae60", stroke=svgkit.LINE))
        else:
            frags.append(svgkit.circle(x, 90, 8, fill="#fdecea", stroke="#c0392b", sw=2))
            
    # Виділяємо число Фробеніуса 7
    fx = 50 + (700 / max_val) * 7
    frags.append(svgkit.text(fx, 60, "g(3,5) = 7", size=14, color="#c0392b", anchor="middle", bold=True))
    
    svgkit.render(out_path, 800, 160, *frags, title="Розподіл чисел Фробеніуса на числові осі")

if __name__ == "__main__":
    create_frobenius_line()
