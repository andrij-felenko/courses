interface Shape {
  area(): number;
  perimeter(): number;          // набір операцій «зашитий» в інтерфейс — це стовпці
}
class Circle implements Shape {
  constructor(private r: number) {}
  area()      { return Math.PI * this.r ** 2; }
  perimeter() { return 2 * Math.PI * this.r; }
}
class Rect implements Shape {
  constructor(private w: number, private h: number) {}
  area()      { return this.w * this.h; }
  perimeter() { return 2 * (this.w + this.h); }
}
// + новий ТИП: один новий клас, старе не чіпаємо ───────────── дешево
class Triangle implements Shape { /* area(); perimeter(); */ }
// + нова ОПЕРАЦІЯ draw(): метод у інтерфейс і в КОЖЕН клас ──── дорого
