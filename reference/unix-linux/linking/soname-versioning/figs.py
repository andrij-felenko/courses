import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import render, textbox, rect, text, line, arrow, INK, LINE, FILL, BG

def render_soname_symlinks():
    frags = []
    
    # Files boxes (left column)
    frags.append(textbox(180, 70, "libfoo.so\n(Linker Name)", size=14, pad=12, fill="#e8f4f8")[0])
    frags.append(textbox(180, 190, "libfoo.so.1\n(SONAME)", size=14, pad=12, fill="#e8f4f8")[0])
    frags.append(textbox(180, 310, "libfoo.so.1.2.3\n(Real File)", size=14, pad=12, fill="#d4edda", bold=True)[0])
    
    # Arrows down
    frags.append(arrow(180, 115, 180, 160, color=LINE, sw=2))
    frags.append(arrow(180, 235, 180, 280, color=LINE, sw=2))
    
    # Explanatory blocks (right column)
    frags.append(textbox(480, 70, "Використовується gcc -lfoo під час компіляції", size=13, pad=10, fill="#f8f9fa")[0])
    frags.append(textbox(480, 190, "Вписується в DT_NEEDED і шукається ld.so під час запуску", size=13, pad=10, fill="#f8f9fa")[0])
    frags.append(textbox(480, 310, "Реальний бінарний файл з машинним кодом бібліотеки", size=13, pad=10, fill="#f8f9fa")[0])
    
    # Connect labels to boxes
    frags.append(line(290, 70, 330, 70, dash="4,4", color="#6c757d"))
    frags.append(line(290, 190, 310, 190, dash="4,4", color="#6c757d"))
    frags.append(line(290, 310, 310, 310, dash="4,4", color="#6c757d"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "soname-symlinks.svg"), 720, 390, *frags, title="Ієрархія символічних посилань SONAME")

def render_symbol_versioning():
    frags = []
    
    # Client Apps (left)
    frags.append(textbox(180, 100, "Додаток A (legacy)\nВимога: do_work@LIBFOO_1.0", size=13, pad=12, fill="#fff3cd")[0])
    frags.append(textbox(180, 270, "Додаток B (сучасний)\nВимога: do_work@@LIBFOO_2.0", size=13, pad=12, fill="#d1ecf1")[0])
    
    # Library Box (right)
    frags.append(rect(430, 50, 260, 310, fill="#fafafa", rx=8, stroke="#cccccc"))
    frags.append(text(560, 75, "libfoo.so.1 (.text)", size=15, bold=True))
    
    frags.append(textbox(560, 130, "do_work_v1()\n[do_work@LIBFOO_1.0]\nСтара сигнатура (int)", size=12, pad=10, fill="#e2e3e5")[0])
    frags.append(textbox(560, 260, "do_work_v2()\n[do_work@@LIBFOO_2.0]\nНова сигнатура (const char*)", size=12, pad=10, fill="#d4edda", bold=True)[0])
    
    # Routing Arrows
    frags.append(arrow(310, 100, 440, 130, color="#d9534f", sw=2))
    frags.append(arrow(310, 270, 440, 260, color="#28a745", sw=2))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "symbol-versioning.svg"), 740, 400, *frags, title="Резолвінг версіонованих символів у ld.so")

def main():
    render_soname_symlinks()
    render_symbol_versioning()

if __name__ == '__main__':
    main()
