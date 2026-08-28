// НАЇВНО: клас на КОЖНУ пару «фігура × рушій»
class SvgStar {
  constructor(private cx: number, private cy: number,
              private outer: number, private inner: number, private n = 5) {}
  draw(out: string[]) {
    const pts: [number, number][] = [];
    for (let i = 0; i < this.n * 2; i++) {                 // ← математика зірки, копія №1
      const rad = i % 2 === 0 ? this.outer : this.inner;
      const t = (Math.PI * i) / this.n - Math.PI / 2;      // −π/2, щоб вістря дивилось угору
      pts.push([this.cx + rad * Math.cos(t), this.cy + rad * Math.sin(t)]);
    }
    const d = pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
    out.push(`<polygon points="${d}" fill="none" stroke="black"/>`);
  }
}

class AsciiStar {
  constructor(private cx: number, private cy: number,
              private outer: number, private inner: number, private n = 5) {}
  draw(grid: string[][]) {
    const pts: [number, number][] = [];
    for (let i = 0; i < this.n * 2; i++) {                 // ← ТА САМА математика, копія №2
      const rad = i % 2 === 0 ? this.outer : this.inner;
      const t = (Math.PI * i) / this.n - Math.PI / 2;
      pts.push([this.cx + rad * Math.cos(t), this.cy + rad * Math.sin(t)]);
    }
    for (let i = 0; i < pts.length; i++) plotSegment(grid, pts[i], pts[(i + 1) % pts.length]);
  }
}

// class StatsStar  ← копія №3, з тим самим циклом і тим самим −π/2
