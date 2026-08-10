import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def render():
    if not svgkit: return
    frags = [
        svgkit.rect(100, 100, 600, 200, fill="#f0f0f0", stroke="#333", rx=10),
        svgkit.rect(150, 150, 150, 100, fill="#cce5ff", stroke="#004085", rx=5),
        svgkit.text(225, 205, "App (login, su)", anchor="middle", size=16),
        svgkit.line(300, 200, 400, 200, color="#333", sw=2),
        svgkit.rect(400, 150, 150, 100, fill="#d4edda", stroke="#155724", rx=5),
        svgkit.text(475, 205, "libpam.so", anchor="middle", size=16),
        svgkit.line(550, 200, 600, 160, color="#333", sw=2),
        svgkit.line(550, 200, 600, 240, color="#333", sw=2),
        svgkit.rect(600, 140, 100, 40, fill="#fff3cd", stroke="#856404"),
        svgkit.text(650, 165, "pam_unix.so", anchor="middle", size=14),
        svgkit.rect(600, 220, 100, 40, fill="#fff3cd", stroke="#856404"),
        svgkit.text(650, 245, "pam_deny.so", anchor="middle", size=14)
    ]
    out_path = os.path.join(os.path.dirname(__file__), "pam_arch.svg")
    svgkit.render(out_path, 800, 400, *frags)

if __name__ == '__main__':
    render()
