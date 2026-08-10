import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'scripts'))
from svgkit import *

b1, w1, h1 = textbox(100, 80, "Thermal Zone\n(Sensors)", size=13, fill="#dbeafe", stroke="#3b82f6")
b2, w2, h2 = textbox(300, 80, "Trip Points\n(Passive/Active/Critical)", size=13, fill="#fef3c7", stroke="#f59e0b")
b3, w3, h3 = textbox(500, 80, "Cooling Device\n(Fans/Throttling)", size=13, fill="#dcfce7", stroke="#22c55e")
b4, w4, h4 = textbox(300, 180, "Thermal Governor\n(step_wise / IPA)", size=13, fill="#f3e8ff", stroke="#a855f7")

a1 = arrow(160, 80, 192, 80)
a2 = arrow(408, 80, 422, 80)
a3 = arrow(100, 112, 222, 168)
a4 = arrow(378, 168, 498, 112)

out_dir = Path(__file__).parent / 'img'
out_dir.mkdir(exist_ok=True)
render(out_dir / 'thermal-architecture.svg', 600, 240, b1, b2, b3, b4, a1, a2, a3, a4, title="Thermal Framework Architecture")
print('Generated thermal-architecture.svg successfully')
