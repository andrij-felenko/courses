svg = SvgRenderer()
scene = Scene(svg, [
    Rect(svg, 2, 2, 76, 36),
    Circle(svg, 16, 20, 10),
    Triangle(svg, (40, 8), (50, 32), (30, 32)),
    Star(svg, 64, 20, 12, 5, 5),
])
print(scene.draw(80, 40))            # SVG

scene.use(AsciiRenderer())           # ← ті самі об'єкти фігур, інший носій
print(scene.draw(80, 40))            # прев'ю в терміналі

scene.use(StatsRenderer())
print(scene.draw(80, 40))            # обмір для тесту
