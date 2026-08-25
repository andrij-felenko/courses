# -*- coding: utf-8 -*-
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def create_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
    <rect width="100%" height="100%" fill="white" />
    <rect x="50" y="50" width="200" height="300" fill="#f0f0f0" stroke="black"/>
    <text x="150" y="40" text-anchor="middle" font-size="15" font-family="sans-serif">Процес (mmap)</text>
    <rect x="70" y="100" width="160" height="20" fill="#a0d0ff" stroke="black"/>
    <rect x="70" y="120" width="160" height="20" fill="#a0d0ff" stroke="black"/>
    <text x="150" y="170" text-anchor="middle" font-size="12" font-family="sans-serif">Вказівник fbp</text>

    <rect x="350" y="50" width="200" height="300" fill="#f0f0f0" stroke="black"/>
    <text x="450" y="40" text-anchor="middle" font-size="15" font-family="sans-serif">Відеопам'ять (/dev/fb0)</text>
    <rect x="370" y="100" width="160" height="80" fill="#a0ffca" stroke="black"/>
    <text x="450" y="145" text-anchor="middle" font-size="12" font-family="sans-serif">Кадровий буфер</text>

    <path d="M 250 150 L 350 150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
    <text x="300" y="138" text-anchor="middle" font-size="12" font-family="sans-serif">Відображення (mmap)</text>
    </svg>"""
    with open(os.path.join(IMG, 'fb-structure.svg'), "w", encoding="utf-8") as f:
        f.write(svg)


create_svg()
print("готово")
sys.exit(0)
