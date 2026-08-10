import sys
import os

# Додаємо шлях до scripts/
script_dir = os.path.dirname(os.path.abspath(__file__))
courses_dir = os.path.abspath(os.path.join(script_dir, '../../../..'))
sys.path.append(os.path.join(courses_dir, 'scripts'))

try:
    from svgkit import Drawing, Rect, Text, Line, render
except ImportError:
    # Fallback/stub якщо svgkit недоступний для локального тестування
    class Drawing:
        def __init__(self, size): self.size = size; self.elements = []
        def add(self, e): self.elements.append(e)
        def save(self, name): 
            with open(name, 'w', encoding='utf-8') as f:
                f.write(f'<svg width="{self.size[0]}" height="{self.size[1]}" xmlns="http://www.w3.org/2000/svg">')
                for el in self.elements: f.write(str(el))
                f.write('</svg>')
    class Rect:
        def __init__(self, pos, size, fill="white", stroke="black"):
            self.pos = pos; self.size = size; self.fill = fill; self.stroke = stroke
        def __str__(self): return f'<rect x="{self.pos[0]}" y="{self.pos[1]}" width="{self.size[0]}" height="{self.size[1]}" fill="{self.fill}" stroke="{self.stroke}"/>'
    class Text:
        def __init__(self, text, pos, font_size=14, text_anchor="middle"):
            self.text = text; self.pos = pos; self.font_size = font_size; self.text_anchor = text_anchor
        def __str__(self): return f'<text x="{self.pos[0]}" y="{self.pos[1]}" font-size="{self.font_size}" text-anchor="{self.text_anchor}">{self.text}</text>'
    class Line:
        def __init__(self, start, end, stroke="black", marker_end=""):
            self.start = start; self.end = end; self.stroke = stroke; self.marker_end = marker_end
        def __str__(self): return f'<line x1="{self.start[0]}" y1="{self.start[1]}" x2="{self.end[0]}" y2="{self.end[1]}" stroke="{self.stroke}"/>'
    def render(filename, drawing): drawing.save(filename)

def draw_arch():
    d = Drawing((600, 400))
    # Userspace
    d.add(Rect((50, 50), (200, 100), fill="#eef"))
    d.add(Text("Android App (Game)", (150, 100)))
    d.add(Rect((350, 50), (200, 100), fill="#eef"))
    d.add(Text("Incremental Service", (450, 100)))
    
    # Kernel space
    d.add(Rect((50, 200), (500, 150), fill="#fee"))
    d.add(Text("Linux Kernel", (300, 220), font_size=16))
    
    d.add(Rect((100, 250), (100, 60), fill="#fcc"))
    d.add(Text("VFS", (150, 285)))
    
    d.add(Rect((250, 250), (250, 60), fill="#ffc"))
    d.add(Text("IncFS (Incremental FS)", (375, 285)))
    
    # Connections
    d.add(Line((150, 150), (150, 250))) # App to VFS
    d.add(Line((200, 280), (250, 280))) # VFS to IncFS
    d.add(Line((375, 250), (450, 150))) # IncFS to IncService
    d.add(Line((450, 50), (450, 20))) # IncService to Network
    d.add(Text("Network (Play Store)", (450, 15)))
    
    render(os.path.join(script_dir, "incfs_arch.svg"), d)

def draw_block_load():
    d = Drawing((600, 300))
    d.add(Rect((50, 50), (120, 50), fill="#ddf"))
    d.add(Text("App reads block", (110, 80)))
    
    d.add(Line((170, 75), (220, 75)))
    
    d.add(Rect((220, 50), (120, 50), fill="#fdd"))
    d.add(Text("IncFS Block", (280, 70)))
    d.add(Text("(Missing)", (280, 85)))
    
    d.add(Line((340, 75), (390, 75)))
    
    d.add(Rect((390, 50), (150, 50), fill="#dfd"))
    d.add(Text("Incremental Service", (465, 70)))
    d.add(Text("Downloads block", (465, 85)))
    
    d.add(Line((465, 100), (465, 150)))
    
    d.add(Rect((390, 150), (150, 50), fill="#ffd"))
    d.add(Text("ioctl FILL_BLOCKS", (465, 180)))
    
    d.add(Line((390, 175), (280, 175)))
    d.add(Line((280, 175), (280, 100)))
    
    render(os.path.join(script_dir, "incfs_block_load.svg"), d)

if __name__ == "__main__":
    draw_arch()
    draw_block_load()
