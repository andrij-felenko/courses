interface Shape {
  accept<R>(v: ShapeVisitor<R>): R;          // тут починається подвійна диспетчеризація
}

interface ShapeVisitor<R> {                  // по методу на КОЖЕН вид фігури
  visitCircle(c: Circle): R;
  visitRectangle(r: Rectangle): R;
  visitTriangle(t: Triangle): R;
}

class Circle implements Shape {
  constructor(public r: number) {}
  accept<R>(v: ShapeVisitor<R>): R { return v.visitCircle(this); }    // я — коло
}
class Rectangle implements Shape {
  constructor(public w: number, public h: number) {}
  accept<R>(v: ShapeVisitor<R>): R { return v.visitRectangle(this); }
}
class Triangle implements Shape {
  constructor(public base: number, public height: number) {}
  accept<R>(v: ShapeVisitor<R>): R { return v.visitTriangle(this); }
}
