import sys
import os

# mock svgkit for context
class SvgKit:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def render(self):
        # generate simple SVG
        svg_content = """<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="200" fill="#f0f0f0" />
  <text x="50" y="50" font-family="Arial" font-size="20">XFRM Architecture</text>
  <rect x="50" y="80" width="100" height="50" fill="lightblue" />
  <text x="60" y="110" font-family="Arial" font-size="14">SPD (Policy)</text>
  <rect x="250" y="80" width="100" height="50" fill="lightgreen" />
  <text x="260" y="110" font-family="Arial" font-size="14">SAD (State)</text>
  <line x1="150" y1="105" x2="250" y2="105" stroke="black" stroke-width="2" />
</svg>"""
        with open(os.path.join(self.output_dir, "xfrm-arch.svg"), "w", encoding="utf-8") as f:
            f.write(svg_content)
        print("Generated xfrm-arch.svg")

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    kit = SvgKit(output_dir)
    kit.render()

if __name__ == "__main__":
    main()
