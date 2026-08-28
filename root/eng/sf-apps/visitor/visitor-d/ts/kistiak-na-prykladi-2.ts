class AreaVisitor implements ShapeVisitor<number> {         // операція «площа» — ЦІЛА, в одному класі
  visitCircle(c: Circle): number       { return Math.PI * c.r * c.r; }
  visitRectangle(r: Rectangle): number { return r.w * r.h; }
  visitTriangle(t: Triangle): number   { return t.base * t.height / 2; }
}

class SvgVisitor implements ShapeVisitor<string> {          // інша операція — інший клас
  visitCircle(c: Circle): string       { return `<circle r="${c.r}"/>`; }
  visitRectangle(r: Rectangle): string { return `<rect width="${r.w}" height="${r.h}"/>`; }
  visitTriangle(t: Triangle): string   { return `<polygon points="0,0 ${t.base},0 0,${t.height}"/>`; }
}

const shapes: Shape[] = [new Circle(2), new Rectangle(3, 4), new Triangle(6, 2)];

const area = new AreaVisitor();
const total = shapes.reduce((s, sh) => s + sh.accept(area), 0);   // 12.566… + 12 + 6 = 30.566…

const svg = new SvgVisitor();
const markup = shapes.map(sh => sh.accept(svg)).join("\n");
