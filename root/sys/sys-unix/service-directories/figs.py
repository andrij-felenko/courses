import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def draw_managed_dirs_arch():
    out = []
    
    # Systemd manager
    out.append(svgkit.rect(50, 50, 150, 100, fill="#3498db", stroke="#2980b9", rx=10))
    out.append(svgkit.text(125, 100, "systemd", color="white", bold=True, anchor="middle"))
    
    # Process
    out.append(svgkit.rect(600, 50, 150, 100, fill="#e74c3c", stroke="#c0392b", rx=10))
    out.append(svgkit.text(675, 90, "Service Process", color="white", bold=True, anchor="middle"))
    out.append(svgkit.text(675, 115, "(User=appuser)", color="white", size=12, anchor="middle"))
    
    # Environment Variables
    out.append(svgkit.arrow(200, 100, 600, 100, color="#34495e", sw=2))
    out.append(svgkit.text(400, 90, "RUNTIME_DIRECTORY=/run/myapp", color="#34495e", size=12, anchor="middle"))
    
    # File system
    out.append(svgkit.rect(50, 250, 700, 120, fill="#ecf0f1", stroke="#bdc3c7", rx=10))
    out.append(svgkit.text(80, 275, "Файлова система", bold=True, size=14, anchor="start"))
    
    # Directories
    dirs = [
        ("RuntimeDirectory", "/run/myapp", 100),
        ("StateDirectory", "/var/lib/myapp", 300),
        ("LogsDirectory", "/var/log/myapp", 500)
    ]
    
    for label, path, x in dirs:
        out.append(svgkit.rect(x, 300, 180, 50, fill="#f1c40f", stroke="#f39c12", rx=5))
        out.append(svgkit.text(x+90, 320, label, size=12, bold=True, anchor="middle"))
        out.append(svgkit.text(x+90, 340, path, size=11, anchor="middle"))
        
        # Systemd creates them
        out.append(svgkit.line(125, 150, x+90, 290, color="#27ae60", sw=2, dash="5,5"))
        out.append(svgkit.circle(x+90, 290, 3, fill="#27ae60", stroke="#27ae60"))
        
        # Process uses them
        out.append(svgkit.line(675, 150, x+90, 290, color="#8e44ad", sw=2))
        out.append(svgkit.circle(x+90, 290, 3, fill="#8e44ad", stroke="#8e44ad"))

    out.append(svgkit.text(150, 200, "1. Створює & chown", color="#27ae60", size=12, anchor="start"))
    out.append(svgkit.text(600, 200, "2. Читає / Пише", color="#8e44ad", size=12, anchor="end"))
    
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "managed-dirs-arch.svg")
    svgkit.render(out_path, 800, 400, *out)

if __name__ == "__main__":
    draw_managed_dirs_arch()
