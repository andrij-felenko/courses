import sys
import os

class DummySVGKit:
    def __init__(self, size):
        self.svg_content = f'<svg width="{size[0]}" height="{size[1]}" xmlns="http://www.w3.org/2000/svg">'
    def rect(self, pos, size, **kwargs):
        fill = kwargs.get('fill', 'white')
        stroke = kwargs.get('stroke', 'black')
        self.svg_content += f'<rect x="{pos[0]}" y="{pos[1]}" width="{size[0]}" height="{size[1]}" fill="{fill}" stroke="{stroke}"/>'
    def text(self, pos, text, **kwargs):
        self.svg_content += f'<text x="{pos[0]}" y="{pos[1]}" dominant-baseline="middle" text-anchor="middle">{text}</text>'
    def line(self, start, end, **kwargs):
        self.svg_content += f'<line x1="{start[0]}" y1="{start[1]}" x2="{end[0]}" y2="{end[1]}" stroke="black" marker-end="url(#arrowhead)"/>'
    def save(self, filepath):
        self.svg_content += '</svg>'
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(self.svg_content)

def render():
    out_dir = os.path.join(os.path.dirname(__file__), "figs")
    os.makedirs(out_dir, exist_ok=True)
    
    svg = DummySVGKit((600, 400))
    
    # IIO Architecture diagram
    if hasattr(svg, 'rect'):
        # using dummy
        svg.rect((200, 50), (200, 50), fill="#eee", stroke="#333")
        svg.text((300, 75), "User Space App")
        
        svg.rect((50, 150), (150, 50), fill="#d0f0c0")
        svg.text((125, 175), "Sysfs")
        
        svg.rect((225, 150), (150, 50), fill="#d0f0c0")
        svg.text((300, 175), "Char Dev (/dev/iio)")
        
        svg.rect((400, 150), (150, 50), fill="#d0f0c0")
        svg.text((475, 175), "Events")
        
        svg.rect((200, 250), (200, 80), fill="#add8e6")
        svg.text((300, 275), "IIO Core")
        svg.text((300, 310), "(Buffer & Triggers)")
        
        svg.rect((200, 360), (200, 30), fill="#f0d0c0")
        svg.text((300, 375), "Hardware (Sensors)")
        
        # Connections
        svg.line((300, 100), (300, 150))
        svg.line((125, 200), (250, 250))
        svg.line((300, 200), (300, 250))
        svg.line((475, 200), (350, 250))
        svg.line((300, 330), (300, 360))
        
        svg.save(os.path.join(out_dir, "iio-arch.svg"))
    else:
        # real svgkit code would go here
        pass

if __name__ == "__main__":
    render()
