import sys
import os

import svgkit   # заглушки тут немає навмисно: зламаний імпорт має падати ГОЛОСНО,
                # інакше фігури тихо перестають з'являтися, а прогін виглядає успішним


def render():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    d = svgkit.Drawing(800, 500)
    
    # Background
    d.add(svgkit.rect(0, 0, 800, 500, fill="#ffffff", stroke="#cccccc"))
    
    # Title
    d.add(svgkit.text(400, 40, "Device Tree Lifecycle", size=24, anchor="middle", weight="bold"))
    
    # Development phase
    d.add(svgkit.rect(50, 100, 200, 350, fill="#f0f8ff", rx=10))
    d.add(svgkit.text(150, 130, "Build Time", size=18, anchor="middle", weight="bold"))
    
    d.add(svgkit.rect(80, 170, 140, 60, fill="#ccffcc", stroke="#009900", rx=5))
    d.add(svgkit.text(150, 205, ".dts / .dtsi", size=16, anchor="middle"))
    
    d.add(svgkit.line(150, 230, 150, 280))
    d.add(svgkit.text(160, 260, "dtc", size=14))
    
    d.add(svgkit.rect(80, 280, 140, 60, fill="#ccccff", stroke="#000099", rx=5))
    d.add(svgkit.text(150, 315, ".dtb (Blob)", size=16, anchor="middle"))
    
    # Boot phase
    d.add(svgkit.rect(300, 100, 200, 350, fill="#fff0f5", rx=10))
    d.add(svgkit.text(400, 130, "Bootloader", size=18, anchor="middle", weight="bold"))
    
    d.add(svgkit.rect(330, 280, 140, 60, fill="#ffcccc", stroke="#990000", rx=5))
    d.add(svgkit.text(400, 315, "U-Boot / GRUB", size=16, anchor="middle"))
    
    d.add(svgkit.line(220, 310, 330, 310))
    
    d.add(svgkit.line(400, 340, 400, 400))
    d.add(svgkit.text(410, 375, "Pass DTB ptr", size=14))
    
    # Kernel phase
    d.add(svgkit.rect(550, 100, 200, 350, fill="#f5fffa", rx=10))
    d.add(svgkit.text(650, 130, "Kernel", size=18, anchor="middle", weight="bold"))
    
    d.add(svgkit.rect(580, 280, 140, 60, fill="#ffffcc", stroke="#999900", rx=5))
    d.add(svgkit.text(650, 315, "Unflatten DT", size=16, anchor="middle"))
    
    d.add(svgkit.line(470, 310, 580, 310))
    
    d.add(svgkit.rect(580, 170, 140, 60, fill="#ffebcd", stroke="#cc6600", rx=5))
    d.add(svgkit.text(650, 195, "of_match_table", size=14, anchor="middle"))
    d.add(svgkit.text(650, 215, "Driver Probing", size=14, anchor="middle"))
    
    d.add(svgkit.line(650, 280, 650, 230))
    
    d.save(os.path.join(out_dir, "dt-lifecycle.svg"))

if __name__ == "__main__":
    render()
