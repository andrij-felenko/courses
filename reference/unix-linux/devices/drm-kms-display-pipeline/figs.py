def render():
    svg1 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300">
    <rect x="50" y="50" width="100" height="50" fill="#aaf" />
    <text x="75" y="80">Planes</text>
    <path d="M 150 75 L 250 75" stroke="black" stroke-width="2" />
    <rect x="250" y="50" width="100" height="50" fill="#afa" />
    <text x="275" y="80">CRTC</text>
    <path d="M 350 75 L 450 75" stroke="black" stroke-width="2" />
    <rect x="450" y="50" width="100" height="50" fill="#faa" />
    <text x="465" y="80">Encoder</text>
    <path d="M 550 75 L 650 75" stroke="black" stroke-width="2" />
    <rect x="650" y="50" width="100" height="50" fill="#ffa" />
    <text x="660" y="80">Connector</text>
</svg>'''
    
    with open("kms-pipeline.svg", "w", encoding="utf-8") as f:
        f.write(svg1)

if __name__ == "__main__":
    render()
