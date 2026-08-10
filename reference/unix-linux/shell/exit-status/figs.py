import sys
import os

# Додаємо шлях до скриптів, щоб імпортувати svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

try:
    import svgkit
except ImportError:
    # Заглушка, якщо svgkit немає
    class svgkit:
        @staticmethod
        def render(filename, content):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

def render():
    svg_content = '''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="white"/>
  <text x="50" y="50" font-family="Arial" font-size="20" fill="black">Exit Status Flow</text>
  <rect x="50" y="80" width="100" height="50" fill="lightblue" stroke="black"/>
  <text x="65" y="110" font-family="Arial" font-size="14" fill="black">Process</text>
  <path d="M 150 105 L 250 105" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="250" y="80" width="100" height="50" fill="lightgreen" stroke="black"/>
  <text x="270" y="110" font-family="Arial" font-size="14" fill="black">waitpid()</text>
</svg>'''
    
    # Виклик svgkit.render (або нашої заглушки)
    try:
        svgkit.render('exit_status_flow.svg', svg_content)
    except Exception as e:
        with open('exit_status_flow.svg', 'w', encoding='utf-8') as f:
            f.write(svg_content)

if __name__ == '__main__':
    render()
