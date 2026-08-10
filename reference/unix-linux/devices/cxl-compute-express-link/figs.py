import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render():
    out_path = os.path.join(os.path.dirname(__file__), "cxl-arch.svg")
    
    frags = []
    
    # Процесор
    frags.append(svgkit.fitbox(50, 50, 150, 250, "CPU", size=24, fill="#cfe2ff", stroke="#0a58ca"))
    # Локальна пам'ять
    frags.append(svgkit.fitbox(250, 50, 100, 100, "DDR5", size=18, fill="#d1e7dd", stroke="#0f5132"))
    # CXL Switch
    frags.append(svgkit.fitbox(250, 200, 150, 100, "CXL Switch", size=18, fill="#e2e3e5", stroke="#41464b"))
    # CXL Пам'ять (Type 3)
    frags.append(svgkit.fitbox(450, 175, 200, 150, "CXL Memory\nExpander\n(Type 3)", size=16, fill="#fff3cd", stroke="#997404"))
    
    # Лінії
    frags.append(svgkit.rect(200, 95, 50, 10, fill="#0f5132", stroke="#0f5132")) # CPU - DDR
    frags.append(svgkit.rect(200, 245, 50, 10, fill="#41464b", stroke="#41464b")) # CPU - Switch
    frags.append(svgkit.rect(400, 245, 50, 10, fill="#997404", stroke="#997404")) # Switch - CXL Mem

    svgkit.render(out_path, 700, 350, *frags, title="Архітектура CXL")

if __name__ == "__main__":
    render()
