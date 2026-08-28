type Point = [number, number];

// ── Реалізація: ЯК виводимо (вісь 1) ─────────────────────────
interface Renderer {
  begin(w: number, h: number): void;
  polyline(pts: Point[], closed: boolean): void;
  ellipse(cx: number, cy: number, rx: number, ry: number): void;
  end(): string;
}

class SvgRenderer implements Renderer {
  private out: string[] = [];
  begin(w: number, h: number) {
    this.out = [`<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">`];
  }
  polyline(pts: Point[], closed: boolean) {
    const d = pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
    this.out.push(`  <${closed ? "polygon" : "polyline"} points="${d}" fill="none" stroke="black"/>`);
  }
  ellipse(cx: number, cy: number, rx: number, ry: number) {
    this.out.push(`  <ellipse cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" ` +
                  `rx="${rx.toFixed(1)}" ry="${ry.toFixed(1)}" fill="none" stroke="black"/>`);
  }
  end() { this.out.push("</svg>"); return this.out.join("\n"); }
}

class AsciiRenderer implements Renderer {
  private w = 0;
  private h = 0;
  private g: string[][] = [];
  begin(w: number, h: number) {
    this.w = w; this.h = h;
    this.g = Array.from({ length: h }, () => new Array<string>(w).fill(" "));
  }
  private plot(x: number, y: number) {
    const xi = Math.round(x), yi = Math.round(y);
    if (xi >= 0 && xi < this.w && yi >= 0 && yi < this.h) this.g[yi][xi] = "#";
  }
  private segment([x1, y1]: Point, [x2, y2]: Point) {
    const steps = Math.max(Math.trunc(Math.abs(x2 - x1)), Math.trunc(Math.abs(y2 - y1)), 1) * 2;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      this.plot(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t);
    }
  }
  polyline(pts: Point[], closed: boolean) {
    const seq = closed ? [...pts, pts[0]] : pts;
    for (let i = 0; i + 1 < seq.length; i++) this.segment(seq[i], seq[i + 1]);
  }
  ellipse(cx: number, cy: number, rx: number, ry: number) {
    const steps = Math.max(8, Math.trunc(4 * (rx + ry)));
    for (let i = 0; i < steps; i++) {
      const t = (2 * Math.PI * i) / steps;
      this.plot(cx + rx * Math.cos(t), cy + ry * Math.sin(t));
    }
  }
  end() { return this.g.map((row) => row.join("").replace(/\s+$/, "")).join("\n"); }
}

class StatsRenderer implements Renderer {
  private n = 0;
  private box: number[] | null = null;
  begin(_w: number, _h: number) { this.n = 0; this.box = null; }
  private grow(x: number, y: number) {
    if (!this.box) { this.box = [x, y, x, y]; return; }
    this.box[0] = Math.min(this.box[0], x); this.box[1] = Math.min(this.box[1], y);
    this.box[2] = Math.max(this.box[2], x); this.box[3] = Math.max(this.box[3], y);
  }
  polyline(pts: Point[], _closed: boolean) { this.n++; for (const [x, y] of pts) this.grow(x, y); }
  ellipse(cx: number, cy: number, rx: number, ry: number) {
    this.n++; this.grow(cx - rx, cy - ry); this.grow(cx + rx, cy + ry);
  }
  end() {
    const [x1, y1, x2, y2] = this.box!;
    return `примітивів: ${this.n}; рамка: (${x1.toFixed(1)},${y1.toFixed(1)})–` +
           `(${x2.toFixed(1)},${y2.toFixed(1)})`;
  }
}
