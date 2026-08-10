def render():
    print("Rendering SVG for PLT and GOT...")
    with open("E:\\develop\\courses\\reference\\unix-linux\\linking\\plt-and-got\\plt-got.svg", "w") as f:
        f.write("<svg xmlns='http://www.w3.org/2000/svg' width='800' height='600'><rect width='800' height='600' fill='lightgrey'/><text x='10' y='20'>PLT and GOT diagram</text></svg>")

if __name__ == "__main__":
    render()
