import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render_svg():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, "macsec-frame.svg")
    
    frags = [
        svgkit.rect(50, 80, 100, 40, fill="#dcdcdc"),
        svgkit.text(100, 105, "Dest MAC"),
        
        svgkit.rect(150, 80, 100, 40, fill="#dcdcdc"),
        svgkit.text(200, 105, "Src MAC"),
        
        svgkit.rect(250, 80, 80, 40, fill="#ffcccc"),
        svgkit.text(290, 105, "SecTAG"),
        
        svgkit.rect(330, 80, 60, 40, fill="#dcdcdc"),
        svgkit.text(360, 105, "Type"),
        
        svgkit.rect(390, 80, 200, 40, fill="#ccffcc"),
        svgkit.text(490, 105, "Encrypted Payload"),
        
        svgkit.rect(590, 80, 80, 40, fill="#ffcccc"),
        svgkit.text(630, 105, "ICV"),
        
        svgkit.rect(670, 80, 60, 40, fill="#dcdcdc"),
        svgkit.text(700, 105, "FCS"),
        
        svgkit.line(250, 130, 250, 140),
        svgkit.line(250, 140, 590, 140),
        svgkit.line(590, 140, 590, 130),
        svgkit.text(420, 155, "Authenticated (ICV coverage)", size=12),
        
        svgkit.line(390, 60, 390, 50),
        svgkit.line(390, 50, 590, 50),
        svgkit.line(590, 50, 590, 60),
        svgkit.text(490, 45, "Encrypted", size=12)
    ]
    
    svgkit.render(path, 800, 200, *frags, title="MACsec Frame Format")

if __name__ == "__main__":
    render_svg()
