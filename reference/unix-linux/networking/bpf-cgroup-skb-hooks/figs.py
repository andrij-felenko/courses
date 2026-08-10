import sys
import os

# Припускаємо наявність svgkit у скриптах
sys.path.insert(0, os.path.abspath("../../../../scripts"))

try:
    import svgkit
except ImportError:
    class DummySVGKit:
        def __init__(self):
            self.svg_content = ""
            
        class _Drawing:
            def __init__(self, name, size):
                self.name = name
                self.size = size
                self.elements = []
                
            def rect(self, x, y, w, h, fill, stroke="black"):
                self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" />')
                
            def text(self, text, x, y, fill="black"):
                self.elements.append(f'<text x="{x}" y="{y}" fill="{fill}" font-family="Arial" font-size="14">{text}</text>')
                
            def line(self, x1, y1, x2, y2, stroke="black"):
                self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="2" />')

            def save(self):
                with open(self.name + ".svg", "w") as f:
                    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.size[0]} {self.size[1]}">\n')
                    for el in self.elements:
                        f.write("  " + el + "\n")
                    f.write('</svg>')

        def drawing(self, name, size=(800, 600)):
            return self._Drawing(name, size)
            
    svgkit = DummySVGKit()

def render():
    # Створюємо діаграму для візуалізації ієрархії cgroups та eBPF хуків
    d = svgkit.drawing("cgroup-ebpf-hooks", size=(800, 500))
    
    # Фон та заголовок
    d.rect(0, 0, 800, 500, fill="#f9f9f9", stroke="none")
    d.text("cgroup v2 Hierarchy and eBPF Hooks", 250, 40, fill="#333")
    
    # Root cgroup
    d.rect(300, 80, 200, 50, fill="#dae8fc", stroke="#6c8ebf")
    d.text("/sys/fs/cgroup", 340, 110)
    
    # Pod level cgroups
    d.line(400, 130, 250, 180)
    d.line(400, 130, 550, 180)
    
    d.rect(150, 180, 200, 50, fill="#d5e8d4", stroke="#82b366")
    d.text("kubepods/pod-a", 195, 210)
    
    d.rect(450, 180, 200, 50, fill="#d5e8d4", stroke="#82b366")
    d.text("kubepods/pod-b", 495, 210)
    
    # BPF Program attached to pod-a
    d.rect(10, 180, 120, 60, fill="#ffe6cc", stroke="#d79b00")
    d.text("BPF_PROG", 35, 200)
    d.text("(EGRESS)", 35, 220)
    d.line(130, 210, 150, 210, stroke="#d79b00") # attachment line
    
    # Container level cgroups
    d.line(250, 230, 150, 290)
    d.line(250, 230, 350, 290)
    
    d.rect(50, 290, 200, 150, fill="#f5f5f5", stroke="#666")
    d.text("container-1", 110, 315)
    d.rect(70, 330, 160, 40, fill="#e1d5e7", stroke="#9673a6")
    d.text("Process 1 (app)", 95, 355)
    d.rect(70, 380, 160, 40, fill="#e1d5e7", stroke="#9673a6")
    d.text("Process 2 (worker)", 85, 405)
    
    d.rect(280, 290, 200, 100, fill="#f5f5f5", stroke="#666")
    d.text("container-2", 340, 315)
    
    # BPF INGRESS Program for container-2
    d.rect(510, 310, 120, 60, fill="#ffe6cc", stroke="#d79b00")
    d.text("BPF_PROG", 535, 330)
    d.text("(INGRESS)", 530, 350)
    d.line(480, 340, 510, 340, stroke="#d79b00")
    
    # Traffic flow arrows
    d.text("Outgoing Packet", 70, 470, fill="#d79b00")
    d.line(150, 420, 150, 480, stroke="#d79b00") # App sends packet
    
    d.text("Hooks enforce policies per-cgroup natively", 250, 480, fill="#555")

    d.save()

if __name__ == "__main__":
    render()
