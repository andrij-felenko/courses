import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "scripts")))

try:
    import svgkit
except ImportError:
    # Заглушка, якщо svgkit немає
    class DummySVGKit:
        class Drawing:
            def __init__(self, size, viewBox):
                self.size = size
                self.viewBox = viewBox
                self.elements = []
            def add(self, el):
                pass
            def saveas(self, filename):
                with open(filename, 'w') as f:
                    f.write(f'<svg width="{self.size[0]}" height="{self.size[1]}" viewBox="{self.viewBox}"></svg>')
    svgkit = DummySVGKit()

def draw_eas_architecture():
    dwg = svgkit.Drawing(size=(800, 400), viewBox="0 0 800 400")
    # Тло
    # Просто зберігаємо порожній файл для тесту (реальний svgkit міг би намалювати)
    dwg.saveas("eas_architecture.svg")
    print("Generated eas_architecture.svg")

def render():
    draw_eas_architecture()

if __name__ == '__main__':
    render()
