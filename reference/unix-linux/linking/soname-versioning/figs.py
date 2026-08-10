import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import render, textbox, rect, text, line, arrow, INK, LINE, FILL, BG

def render_soname_symlinks():
    frags = []
    
    # Files boxes
    frags.append(textbox(200, 100, "libfoo.so", size=16, pad=15, fill="#e8f4f8")[0])
    frags.append(textbox(200, 200, "libfoo.so.1", size=16, pad=15, fill="#e8f4f8")[0])
    frags.append(textbox(200, 300, "libfoo.so.1.2.3", size=16, pad=15, fill="#d4edda", bold=True)[0])
    
    # Arrows
    frags.append(arrow(200, 125, 200, 175, color=LINE, sw=2))
    frags.append(arrow(200, 225, 200, 275, color=LINE, sw=2))
    
    # Labels
    frags.append(textbox(400, 100, "Linker name (для gcc / ld)", size=14, pad=10)[0])
    frags.append(textbox(400, 200, "SONAME (для ld.so)", size=14, pad=10)[0])
    frags.append(textbox(400, 300, "Real name (Сам бінарний файл)", size=14, pad=10)[0])
    
    # Connect labels to boxes
    frags.append(line(270, 100, 300, 100, dash="5,5"))
    frags.append(line(280, 200, 300, 200, dash="5,5"))
    frags.append(line(290, 300, 300, 300, dash="5,5"))

    render(os.path.join(os.path.dirname(__file__), "soname_symlinks.svg"), 600, 400, *frags, title="Символічні посилання")

def render_symbol_versioning():
    frags = []
    
    # Client App
    frags.append(textbox(200, 150, "App (Compiled against v1.0)\nCalls do_work()", size=14, pad=15, fill="#fff3cd")[0])
    frags.append(textbox(200, 300, "App (Compiled against v2.0)\nCalls do_work()", size=14, pad=15, fill="#fff3cd")[0])
    
    # Library
    frags.append(rect(450, 80, 250, 300, fill="#f8f9fa", rx=10))
    frags.append(text(575, 110, "libfoo.so.1", size=16, bold=True))
    
    frags.append(textbox(575, 160, "do_work@LIBFOO_1.0\n(старий ABI)", size=14, pad=10, fill="#e2e3e5")[0])
    frags.append(textbox(575, 290, "do_work@@LIBFOO_2.0\n(новий ABI, default)", size=14, pad=10, fill="#d4edda")[0])
    
    # Arrows
    frags.append(arrow(320, 150, 470, 160, color="#17a2b8", sw=2))
    frags.append(arrow(320, 300, 460, 290, color="#28a745", sw=2))

    render(os.path.join(os.path.dirname(__file__), "symbol_versioning.svg"), 750, 450, *frags, title="Резолвінг версіонованих символів")

def main():
    render_soname_symlinks()
    render_symbol_versioning()

if __name__ == '__main__':
    main()
