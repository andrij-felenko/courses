import sys
import os

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.abspath('../../../../../scripts'))
try:
    import svgkit
except ImportError:
    # A dummy svgkit in case the script directory doesn't exist or is not found
    class SVGCreator:
        def __init__(self, w, h):
            self.lines = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">']
        def add_rect(self, x, y, w, h, fill, stroke="black"):
            self.lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" />')
        def add_text(self, x, y, text, font_size=12, anchor="middle", fill="black"):
            self.lines.append(f'<text x="{x}" y="{y}" font-size="{font_size}" font-family="sans-serif" text-anchor="{anchor}" fill="{fill}">{text}</text>')
        def add_line(self, x1, y1, x2, y2, stroke="black", stroke_width=1, dasharray=""):
            dash = f' stroke-dasharray="{dasharray}"' if dasharray else ''
            self.lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"{dash} />')
        def render(self):
            self.lines.append('</svg>')
            return '\n'.join(self.lines)
    svgkit = type('svgkit', (), {'SVGCreator': SVGCreator})

def draw_scheduling_comparison():
    w, h = 800, 300
    svg = svgkit.SVGCreator(w, h)
    
    # Background
    svg.add_rect(0, 0, w, h, "#ffffff", "none")
    
    y_other = 50
    y_batch = 150
    y_idle = 250
    
    # Labels
    svg.add_text(80, y_other+15, "SCHED_OTHER", 14, "end", "#333333")
    svg.add_text(80, y_batch+15, "SCHED_BATCH", 14, "end", "#333333")
    svg.add_text(80, y_idle+15, "SCHED_IDLE", 14, "end", "#333333")
    
    # Timelines
    for y in [y_other, y_batch, y_idle]:
        svg.add_line(100, y+30, 750, y+30, "#aaaaaa", 2)
        
    # SCHED_OTHER: Frequent context switches
    x = 100
    for i in range(12):
        svg.add_rect(x, y_other, 20, 30, "#4caf50", "#388e3c") # Process A
        svg.add_rect(x+25, y_other, 20, 30, "#2196f3", "#1976d2") # Process B
        x += 50
        
    # SCHED_BATCH: Longer timeslices, less switching
    x = 100
    for i in range(4):
        svg.add_rect(x, y_batch, 70, 30, "#ff9800", "#f57c00") # Batch Process A
        svg.add_rect(x+75, y_batch, 70, 30, "#9c27b0", "#7b1fa2") # Batch Process B
        x += 150
        
    # SCHED_IDLE: Runs only when absolutely nothing else
    svg.add_rect(100, y_idle, 250, 30, "#e0e0e0", "#bdbdbd") # Idle period
    svg.add_text(225, y_idle+20, "CPU Busy (Other/Batch)", 12, "middle", "#757575")
    
    svg.add_rect(350, y_idle, 150, 30, "#00bcd4", "#0097a7") # IDLE task runs
    svg.add_text(425, y_idle+20, "IDLE Task Runs", 12, "middle", "#ffffff")
    
    svg.add_rect(500, y_idle, 100, 30, "#e0e0e0", "#bdbdbd")
    svg.add_text(550, y_idle+20, "CPU Busy", 12, "middle", "#757575")
    
    svg.add_rect(600, y_idle, 150, 30, "#00bcd4", "#0097a7")
    
    with open("fig-sched-comparison.svg", "w", encoding="utf-8") as f:
        f.write(svg.render())

def render():
    draw_scheduling_comparison()

if __name__ == "__main__":
    render()
