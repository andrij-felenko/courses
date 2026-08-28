const svg = new SvgRenderer();
const scene = new Scene(svg, [
  new Rect(svg, 2, 2, 76, 36),
  new Circle(svg, 16, 20, 10),
  new Triangle(svg, [40, 8], [50, 32], [30, 32]),
  new Star(svg, 64, 20, 12, 5, 5),
]);
console.log(scene.draw(80, 40));     // SVG

scene.use(new AsciiRenderer());      // ← ті самі об'єкти фігур, інший носій
console.log(scene.draw(80, 40));     // прев'ю в терміналі

scene.use(new StatsRenderer());
console.log(scene.draw(80, 40));     // обмір для тесту
