// ── Абстракція: ЩО малюємо (вісь 2) ──────────────────────────
abstract class Shape {
  constructor(public r: Renderer) {}          // ← МІСТ до реалізації
  abstract draw(): void;
}

class Circle extends Shape {
  constructor(r: Renderer, private cx: number, private cy: number, private rad: number) { super(r); }
  draw() { this.r.ellipse(this.cx, this.cy, this.rad, this.rad); }
}

class Rect extends Shape {
  constructor(r: Renderer, private x: number, private y: number,
              private w: number, private h: number) { super(r); }
  draw() {
    const { x, y, w, h } = this;
    this.r.polyline([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], true);
  }
}

class Triangle extends Shape {
  private pts: Point[];
  constructor(r: Renderer, a: Point, b: Point, c: Point) { super(r); this.pts = [a, b, c]; }
  draw() { this.r.polyline(this.pts, true); }
}

class Star extends Shape {
  constructor(r: Renderer, private cx: number, private cy: number,
              private outer: number, private inner: number, private points = 5) { super(r); }
  draw() {
    const pts: Point[] = [];
    for (let i = 0; i < this.points * 2; i++) {
      const rad = i % 2 === 0 ? this.outer : this.inner;
      const t = (Math.PI * i) / this.points - Math.PI / 2;
      pts.push([this.cx + rad * Math.cos(t), this.cy + rad * Math.sin(t)]);
    }
    this.r.polyline(pts, true);               // геометрія зірки — ОДИН раз на всі рушії
  }
}

class Scene {
  private r!: Renderer;
  constructor(r: Renderer, private shapes: Shape[]) { this.use(r); }
  use(r: Renderer) {                          // ← жива заміна рушія на льоту
    this.r = r;
    for (const s of this.shapes) s.r = r;
  }
  draw(w: number, h: number): string {
    this.r.begin(w, h);
    for (const s of this.shapes) s.draw();
    return this.r.end();
  }
}
