import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_dynamic_ftrace(path):
    frags = []
    
    # Compilation
    frags.append(rect(50, 70, 150, 60, fill="#e8f4f8", stroke="#2b7b98"))
    frags.append(text(125, 95, "Компіляція (-pg)"))
    frags.append(text(125, 115, "call __fentry__", size=12))
    
    # Boot time
    frags.append(rect(225, 70, 150, 60, fill="#f9f2e7", stroke="#d98c21"))
    frags.append(text(300, 95, "Завантаження ОС"))
    frags.append(text(300, 115, "Патчинг в NOP", size=12))
    
    # Runtime (Disabled)
    frags.append(rect(130, 200, 150, 60, fill="#eef7e9", stroke="#4b9932"))
    frags.append(text(205, 225, "Трасування ВИМКНЕНО"))
    frags.append(text(205, 245, "Виконується NOP", size=12))
    
    # Runtime (Enabled)
    frags.append(rect(320, 200, 150, 60, fill="#fceaea", stroke="#c9302c"))
    frags.append(text(395, 225, "Трасування УВІМКНЕНО"))
    frags.append(text(395, 245, "call ftrace_caller", size=12))
    
    # Arrows
    frags.append(arrow(200, 100, 225, 100))
    frags.append(arrow(300, 130, 205, 200))
    frags.append(arrow(300, 130, 395, 200))
    
    render(path, 600, 300, *frags, title="Механізм Dynamic Ftrace: Від компіляції до виконання")

def render_tracefs(path):
    frags = []
    
    frags.append(rect(50, 70, 500, 150, fill="#f4f4f4", stroke="#888"))
    
    frags.append(text(70, 100, "Файли керування:", bold=True, anchor="start"))
    frags.append(text(80, 120, "• available_tracers (функції, графіки, тощо)", size=14, anchor="start"))
    frags.append(text(80, 140, "• current_tracer (встановлення поточного трасера)", size=14, anchor="start"))
    frags.append(text(80, 160, "• tracing_on (1 - увімкнути запис, 0 - вимкнути)", size=14, anchor="start"))
    frags.append(text(80, 180, "• trace (зчитування результатів трасування)", size=14, anchor="start"))
    frags.append(text(80, 200, "• set_ftrace_filter (фільтрація функцій)", size=14, anchor="start"))
    
    render(path, 600, 250, *frags, title="Інтерфейс tracefs (/sys/kernel/debug/tracing/)")

def build_svgs():
    out_dir = os.path.dirname(__file__)
    render_dynamic_ftrace(os.path.join(out_dir, "dynamic-ftrace.svg"))
    render_tracefs(os.path.join(out_dir, "tracefs.svg"))
    print("ftrace SVG figures generated.")

if __name__ == "__main__":
    build_svgs()
