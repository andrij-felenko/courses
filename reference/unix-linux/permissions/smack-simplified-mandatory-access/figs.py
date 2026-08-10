import os

class SvgCanvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.elements = []
    def rect(self, x, y, w, h, fill, stroke="black"):
        self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" rx="5" ry="5"/>')
    def text(self, x, y, text, font_size=14, anchor="middle", font_weight="normal"):
        self.elements.append(f'<text x="{x}" y="{y}" font-size="{font_size}" font-family="Arial" font_weight="{font_weight}" text-anchor="{anchor}">{text}</text>')
    def render(self, path):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}">'
        svg += "".join(self.elements)
        svg += "</svg>"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)

def render():
    canvas = SvgCanvas(600, 400)
    canvas.rect(50, 50, 200, 120, "#e8f4f8", "#2c3e50")
    canvas.text(150, 80, "Subject (Process)", 16, "middle", "bold")
    canvas.text(150, 110, "Label: WebBrowser", 14)
    canvas.text(150, 130, "PID: 1234", 12)

    canvas.rect(350, 50, 200, 120, "#f9ebea", "#c0392b")
    canvas.text(450, 80, "Object (File)", 16, "middle", "bold")
    canvas.text(450, 110, "Label: UserData", 14)
    canvas.text(450, 130, "xattr: security.SMACK64", 12)

    canvas.rect(200, 250, 200, 80, "#fcf3cf", "#f1c40f")
    canvas.text(300, 280, "SMACK LSM (Kernel)", 16, "middle", "bold")
    canvas.text(300, 300, "Rule: WebBrowser UserData rw", 12)

    canvas.text(300, 180, "Access Request (rwx) ->", 14)
    canvas.text(300, 210, "<- Access Granted / Denied", 14)

    canvas.render("smack-architecture.svg")

if __name__ == "__main__":
    render()
