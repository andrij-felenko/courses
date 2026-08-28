// Реалізація: ЯК фізично намалювати примітив (вісь 1)
interface Renderer {
  drawCircle(x: number, y: number, r: number): string;
}

class VectorRenderer implements Renderer {
  drawCircle(x: number, y: number, r: number) {
    return `<circle cx=${x} cy=${y} r=${r}/>`;        // SVG
  }
}
class RasterRenderer implements Renderer {
  drawCircle(x: number, y: number, r: number) {
    return `піксельне коло R=${r} у (${x},${y})`;      // растр
  }
}

// Абстракція: ЩО малюємо; тримає рушій і делегує (вісь 2)
abstract class Shape {
  constructor(protected r: Renderer) {}               // ← міст до реалізації
  abstract draw(): string;
}
class Circle extends Shape {
  constructor(r: Renderer, private x: number, private y: number, private rad: number) {
    super(r);
  }
  draw() { return this.r.drawCircle(this.x, this.y, this.rad); }
}

const c = new Circle(new VectorRenderer(), 10, 10, 5);
console.log(c.draw());          // <circle .../>  — векторний
// той самий Circle з іншим рушієм: жодного нового класу
console.log(new Circle(new RasterRenderer(), 10, 10, 5).draw());
