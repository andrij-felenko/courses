import sys
import os

# Dummy svgkit for testing, since we might not have it installed or available in this directory
class SVG:
    def __init__(self, filename):
        self.filename = filename
        self.elements = []
    def rect(self, x, y, w, h, **kwargs):
        pass
    def text(self, x, y, text, **kwargs):
        pass
    def line(self, x1, y1, x2, y2, **kwargs):
        pass
    def render(self):
        with open(self.filename, 'w') as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"></svg>')

def draw_nested_arch():
    svg = SVG("nested_arch.svg")
    svg.render()

def draw_vmcs_shadowing():
    svg = SVG("vmcs_shadowing.svg")
    svg.render()

def draw_ept_routing():
    svg = SVG("ept_routing.svg")
    svg.render()

def render():
    draw_nested_arch()
    draw_vmcs_shadowing()
    draw_ept_routing()

if __name__ == '__main__':
    render()
