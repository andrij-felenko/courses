import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render_figs():
    svg_path = os.path.join(os.path.dirname(__file__), "fig-interrupt-vs-polling.svg")
    
    frags = []
    
    # Схема Interrupts
    frags.append(svgkit.rect(50, 50, 300, 300, fill="#f0f0f0", stroke="#333"))
    frags.append(svgkit.text(200, 80, "Interrupt-driven IO", size=16, bold=True))
    frags.append(svgkit.text(200, 130, "1. Submit IO request"))
    frags.append(svgkit.text(200, 170, "2. CPU context switch / sleep"))
    frags.append(svgkit.text(200, 210, "3. Device raises IRQ", color="red"))
    frags.append(svgkit.text(200, 250, "4. IRQ handler wakes CPU"))
    frags.append(svgkit.text(200, 290, "5. Complete IO"))
    
    # Схема Polling
    frags.append(svgkit.rect(450, 50, 300, 300, fill="#e0f0ff", stroke="#333"))
    frags.append(svgkit.text(600, 80, "Polling-driven IO", size=16, bold=True))
    frags.append(svgkit.text(600, 130, "1. Submit IO request"))
    frags.append(svgkit.text(600, 170, "2. CPU spins (polls CQ)", color="blue"))
    frags.append(svgkit.text(600, 210, "3. Device writes to CQ"))
    frags.append(svgkit.text(600, 250, "4. CPU detects completion"))
    frags.append(svgkit.text(600, 290, "5. Complete IO"))
    
    svgkit.render(svg_path, 800, 400, *frags, title="Interrupts vs Polling")

if __name__ == "__main__":
    render_figs()
