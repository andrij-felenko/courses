import os
import sys

# Додаємо scripts/ до шляху пошуку для імпорту svgkit (якщо він є, але ми зробимо standalone render)
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../scripts'))
import svgkit   # заглушки тут немає навмисно: зламаний імпорт має падати ГОЛОСНО,
                # інакше фігури тихо перестають з'являтися, а прогін виглядає успішним


def render():
    filepath = os.path.join(os.path.dirname(__file__), "proc-structure.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">\n')
        
        # Background
        svgkit.draw_rect(f, 0, 0, 800, 600, fill="#f8f9fa", stroke="none")
        
        # Title
        svgkit.draw_text(f, 400, 40, "Структура псевдофайлової системи /proc", font_size=20, text_anchor="middle")
        
        # Root /proc
        svgkit.draw_rect(f, 350, 80, 100, 40, fill="#e3f2fd", stroke="#1e88e5")
        svgkit.draw_text(f, 400, 105, "/proc", font_size=16, text_anchor="middle")
        
        # Level 1 branches
        svgkit.draw_line(f, 400, 120, 200, 180, stroke="#90caf9", stroke_width=2)
        svgkit.draw_line(f, 400, 120, 400, 180, stroke="#90caf9", stroke_width=2)
        svgkit.draw_line(f, 400, 120, 600, 180, stroke="#90caf9", stroke_width=2)
        
        # /proc/PID
        svgkit.draw_rect(f, 150, 180, 100, 40, fill="#e8f5e9", stroke="#43a047")
        svgkit.draw_text(f, 200, 205, "/proc/1234", font_size=14, text_anchor="middle")
        
        # /proc/sys
        svgkit.draw_rect(f, 350, 180, 100, 40, fill="#fff3e0", stroke="#fb8c00")
        svgkit.draw_text(f, 400, 205, "/proc/sys", font_size=14, text_anchor="middle")
        
        # /proc/meminfo etc
        svgkit.draw_rect(f, 550, 180, 100, 40, fill="#fce4ec", stroke="#e91e63")
        svgkit.draw_text(f, 600, 205, "/proc/meminfo", font_size=14, text_anchor="middle")
        
        # Under /proc/PID
        items = ["cmdline", "status", "maps", "fd/", "task/"]
        for i, item in enumerate(items):
            y = 260 + i * 50
            svgkit.draw_line(f, 200, 220, 200, y, stroke="#a5d6a7", stroke_width=2)
            svgkit.draw_rect(f, 160, y, 80, 30, fill="#ffffff", stroke="#43a047")
            svgkit.draw_text(f, 200, y + 20, item, font_size=12, text_anchor="middle")
            
        # Under /proc/sys
        sys_items = ["kernel/", "net/", "vm/"]
        for i, item in enumerate(sys_items):
            y = 260 + i * 50
            svgkit.draw_line(f, 400, 220, 400, y, stroke="#ffcc80", stroke_width=2)
            svgkit.draw_rect(f, 360, y, 80, 30, fill="#ffffff", stroke="#fb8c00")
            svgkit.draw_text(f, 400, y + 20, item, font_size=12, text_anchor="middle")
            
        f.write('</svg>\n')
    print(f"Generated {filepath}")

if __name__ == '__main__':
    render()
