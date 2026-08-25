import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def render_svg(w, h, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/>
        </marker>
    </defs>
    {body}
    </svg>'''

def draw():
    out = []
    out.append(rect(100, 50, 250, 300, fill="#f9f9f9", stroke="#333", sw=2))
    out.append(rect(550, 50, 250, 300, fill="#f9f9f9", stroke="#333", sw=2))
    out.append(text(225, 80, "Логіка", size=18, bold=True))
    out.append(text(675, 80, "Програмування", size=18, bold=True))
    
    pairs = [
        ("Висловлювання (A)", "Тип даних (A)"),
        ("Доведення (p)", "Програма/Функція (p)"),
        ("Імплікація (A → B)", "Функція (A → B)"),
        ("Кон'юнкція (A ∧ B)", "Пара/Кортеж (A × B)"),
        ("Диз'юнкція (A ∨ B)", "Об'єднання (A + B)"),
        ("Хибність (⊥)", "Порожній тип (Void)")
    ]
    
    y = 130
    for logic, prog in pairs:
        out.append(text(225, y, logic, size=14))
        out.append(text(675, y, prog, size=14))
        out.append(arrow(350, y - 5, 550, y - 5, color=MUTED, sw=1.5))
        y += 40
        
    svg = render_svg(900, 400, "".join(out))
    
    os.makedirs('img', exist_ok=True)
    with open('img/fig-curry-howard.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

if __name__ == '__main__':
    draw()
