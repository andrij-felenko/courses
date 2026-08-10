import os
import sys

# Додаємо шлях до scripts/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

try:
    from svgkit import *
except ImportError:
    # Заглушка, якщо svgkit не знайдено, але треба згенерувати SVG
    class Element:
        def __init__(self, tag, **kwargs):
            self.tag = tag
            self.kwargs = kwargs
            self.children = []
        def add(self, child):
            self.children.append(child)
        def to_svg(self):
            attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in self.kwargs.items())
            inner = "".join(c.to_svg() if hasattr(c, 'to_svg') else str(c) for c in self.children)
            return f"<{self.tag} {attrs}>{inner}</{self.tag}>"
    class Drawing(Element):
        def __init__(self, width, height, bg="white"):
            super().__init__("svg", xmlns="http://www.w3.org/2000/svg", viewBox=f"0 0 {width} {height}", width=width, height=height)
            self.add(Element("rect", x=0, y=0, width=width, height=height, fill=bg))
    def Rect(**kwargs): return Element("rect", **kwargs)
    def Text(text, **kwargs):
        el = Element("text", **kwargs)
        el.children.append(text)
        return el
    def Arrow(**kwargs):
        # simple line as arrow
        return Element("line", **kwargs)

def render():
    doc = Drawing(width=800, height=300, bg="#ffffff")
    
    # Primary Kernel
    doc.add(Rect(x=50, y=50, width=250, height=200, fill="#f0f0f0", stroke="#333333", rx="5", ry="5"))
    doc.add(Text("Первинне ядро (Primary Kernel)", x=175, y=80, text_anchor="middle", font_family="sans-serif", font_weight="bold", fill="#333333"))
    doc.add(Rect(x=70, y=100, width=210, height=130, fill="#ffffff", stroke="#999999"))
    doc.add(Text("Пам'ять (RAM)", x=175, y=120, text_anchor="middle", font_family="sans-serif", fill="#666666"))
    doc.add(Rect(x=90, y=140, width=170, height=70, fill="#e6f7ff", stroke="#1890ff"))
    doc.add(Text("Зарезервовано", x=175, y=165, text_anchor="middle", font_family="sans-serif", fill="#0050b3", font_size="14"))
    doc.add(Text("crashkernel=...", x=175, y=190, text_anchor="middle", font_family="monospace", fill="#0050b3", font_size="12"))

    # Crash Kernel
    doc.add(Rect(x=450, y=130, width=250, height=120, fill="#fff0f6", stroke="#eb2f96", rx="5", ry="5"))
    doc.add(Text("Crash Kernel (kdump)", x=575, y=160, text_anchor="middle", font_family="sans-serif", font_weight="bold", fill="#a8071a"))
    doc.add(Text("Працює в зарезервованій", x=575, y=190, text_anchor="middle", font_family="sans-serif", fill="#a8071a", font_size="14"))
    doc.add(Text("області пам'яті", x=575, y=210, text_anchor="middle", font_family="sans-serif", fill="#a8071a", font_size="14"))
    
    # Transition
    doc.add(Arrow(x1=300, y1=150, x2=450, y2=150, stroke="#ff4d4f", stroke_width="3", marker_end="url(#arrow)"))
    doc.add(Text("Kernel Panic!", x=375, y=140, text_anchor="middle", font_family="sans-serif", font_weight="bold", fill="#ff4d4f"))
    doc.add(Text("kexec transition", x=375, y=170, text_anchor="middle", font_family="sans-serif", fill="#ff4d4f", font_size="12"))
    
    return [("kexec-kdump-arch", doc)]

if __name__ == "__main__":
    import os
    for name, doc in render():
        with open(os.path.join(os.path.dirname(__file__), f"{name}.svg"), "w", encoding="utf-8") as f:
            f.write(doc.to_svg())
