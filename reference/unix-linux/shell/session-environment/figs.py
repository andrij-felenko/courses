import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
try:
    import svgkit
except ImportError:
    print("Warning: svgkit not found, skipping figure generation")
    sys.exit(0)

def render():
    # Фігура 1: Успадкування змінних
    # Створюємо полотно
    dwg = svgkit.Drawing("fig-env-inherit.svg", size=(600, 400))
    
    # Додаємо елементи
    dwg.add(svgkit.Rect(insert=(50, 50), size=(200, 150), fill="#f0f0f0", stroke="black"))
    dwg.add(svgkit.Text("Parent Process (Bash)", insert=(60, 70), font_size="16px", font_weight="bold"))
    
    dwg.add(svgkit.Text("Local: MY_VAR=1", insert=(60, 100), font_size="14px", fill="#555"))
    dwg.add(svgkit.Text("Exported: MY_ENV=2", insert=(60, 130), font_size="14px", fill="blue"))
    
    dwg.add(svgkit.Line(start=(150, 200), end=(150, 250), stroke="black", stroke_width=2, marker_end="url(#arrow)"))
    dwg.add(svgkit.Text("fork() + exec()", insert=(160, 230), font_size="14px"))
    
    dwg.add(svgkit.Rect(insert=(50, 250), size=(200, 100), fill="#e0f7fa", stroke="black"))
    dwg.add(svgkit.Text("Child Process (Script)", insert=(60, 270), font_size="16px", font_weight="bold"))
    
    dwg.add(svgkit.Text("MY_ENV=2", insert=(60, 300), font_size="14px", fill="blue"))
    dwg.add(svgkit.Text("(MY_VAR is missing)", insert=(60, 320), font_size="14px", fill="#999"))
    
    dwg.save()

if __name__ == "__main__":
    render()
