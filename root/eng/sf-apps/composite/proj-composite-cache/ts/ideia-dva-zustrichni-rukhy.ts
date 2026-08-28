type Rect = { minX: number; minY: number; maxX: number; maxY: number };

// порожній бокс — «нескінченно малий»: будь-яке об'єднання одразу його поглинає
const EMPTY: Rect = { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity };

function union(a: Rect, b: Rect): Rect {
  return {
    minX: Math.min(a.minX, b.minX), minY: Math.min(a.minY, b.minY),
    maxX: Math.max(a.maxX, b.maxX), maxY: Math.max(a.maxY, b.maxY),
  };
}

abstract class Shape {
  parent: Group | null = null;          // посилання ВГОРУ — по ньому піде інвалідизація
  abstract bounds(): Rect;
}

class Rectangle extends Shape {
  constructor(public x: number, public y: number, public w: number, public h: number) {
    super();
  }
  bounds(): Rect {                       // листок рахує прямо — власний кеш йому не потрібен
    return { minX: this.x, minY: this.y, maxX: this.x + this.w, maxY: this.y + this.h };
  }
  moveTo(x: number, y: number): void {
    this.x = x; this.y = y;
    this.parent?.invalidate();           // ← зсув ЛИСТКА теж псує кеш групи!
  }
}

class Group extends Shape {
  private children: Shape[] = [];
  private dirty = true;                  // нова/порожня група — брудна
  private cached: Rect = EMPTY;

  add(child: Shape): void {
    child.parent = this;
    this.children.push(child);
    this.invalidate();                   // структура змінилась
  }

  remove(child: Shape): void {
    const i = this.children.indexOf(child);
    if (i < 0) return;
    this.children.splice(i, 1);
    child.parent = null;                 // від'єднаний листок більше нікого не інвалідизує
    this.invalidate();                   // видалення могло стиснути бокс — треба перерахувати
  }

  bounds(): Rect {
    if (this.dirty) {                    // лінивий перерахунок — лише коли брудні
      let box = EMPTY;
      for (const c of this.children) box = union(box, c.bounds());  // чисті діти — O(1)
      this.cached = box;
      this.dirty = false;
    }
    return this.cached;                  // чистий — миттєво, O(1)
  }

  invalidate(): void {                   // себе й усіх пращурів — у брудні, зі зупинкою
    let g: Group | null = this;
    while (g && !g.dirty) {              // уже брудний → вище теж брудні, спиняємось
      g.dirty = true;
      g = g.parent;
    }
  }
}
