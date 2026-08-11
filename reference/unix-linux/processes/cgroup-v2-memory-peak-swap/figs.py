import sys
import os

# Додаємо шлях до скриптів
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))

try:
    from svgkit import render, rect, text, line, textbox
except ImportError:
    pass

def main():
    w, h = 800, 500
    
    frags = []
    
    # Cgroup ієрархія і ліміти пам'яті
    frags.append(rect(100, 100, 200, 300, fill="#e3f2fd", stroke="#1e88e5", sw=2))
    frags.append(text(200, 130, "Cgroup A", size=18, bold=True, color="#0d47a1"))
    
    # Рівні пам'яті
    # max
    frags.append(line(90, 150, 310, 150, color="#d32f2f", sw=2, dash="5,5"))
    frags.append(text(360, 155, "memory.max", size=14, color="#d32f2f"))
    
    # high
    frags.append(line(90, 200, 310, 200, color="#f57c00", sw=2, dash="5,5"))
    frags.append(text(360, 205, "memory.high", size=14, color="#f57c00"))
    
    # low
    frags.append(line(90, 300, 310, 300, color="#388e3c", sw=2, dash="5,5"))
    frags.append(text(360, 305, "memory.low", size=14, color="#388e3c"))
    
    # min
    frags.append(line(90, 350, 310, 350, color="#1976d2", sw=2, dash="5,5"))
    frags.append(text(360, 355, "memory.min", size=14, color="#1976d2"))
    
    # Поточне споживання і peak
    frags.append(rect(120, 250, 160, 150, fill="#bbdefb"))
    frags.append(text(200, 330, "Поточне", size=14))
    
    # Peak
    frags.append(line(120, 180, 280, 180, color="#7b1fa2", sw=2))
    frags.append(text(200, 175, "memory.peak", size=14, color="#7b1fa2"))
    
    render(os.path.join(IMG, 'cgroup-memory-limits.svg'), w, h, *frags, title="Cgroup v2 Memory Hierarchy")
    print("SVG generated successfully.")

if __name__ == "__main__":
    main()
