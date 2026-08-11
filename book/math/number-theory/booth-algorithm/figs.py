import sys
import os

# Add path to scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import textbox, text, line, render
except ImportError as e:
    print(f"Error importing svgkit: {e}")
    sys.exit(1)

def main():
    w, h = 800, 450
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "fig-booth-radix4.svg")
    
    frags = []
    
    # Схема Radix-4 Booth Encoding
    box, bw, bh = textbox(400, 40, "Модифікований алгоритм Бута (Radix-4)", size=18, bold=True)
    frags.append(box)
    
    # Таблиця
    table_x = 400
    table_y = 110
    row_h = 35
    
    headers = ["x_{i+1}", "x_i", "x_{i-1}", "Операція", "Коментар"]
    for i, head in enumerate(headers):
        frags.append(text(table_x - 300 + i*150, table_y, head, bold=True, size=16))
        
    rows = [
        ("0", "0", "0", "+0", "+0 (ряд нулів)"),
        ("0", "0", "1", "+M", "+1 (кінець одиниць)"),
        ("0", "1", "0", "+M", "+1 (ізольована одиниця)"),
        ("0", "1", "1", "+2M", "+2 (кінець послідовності)"),
        ("1", "0", "0", "-2M", "-2 (початок послідовності)"),
        ("1", "0", "1", "-M", "-1 (ізольований нуль)"),
        ("1", "1", "0", "-M", "-1 (початок одиниць)"),
        ("1", "1", "1", "-0", "-0 (ряд одиниць)")
    ]
    
    for r, row in enumerate(rows):
        y = table_y + (r+1)*row_h
        for i, val in enumerate(row):
            frags.append(text(table_x - 300 + i*150, y, val, size=15))
            
    # Додамо лінії для таблиці
    for r in range(len(rows) + 2):
        y = table_y - 18 + r*row_h
        frags.append(line(table_x - 380, y, table_x + 350, y, sw=1, dash="4,4" if r > 1 else None))
    
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")

if __name__ == "__main__":
    main()
