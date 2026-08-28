class ImageProxy implements Image {
  private real: RealImage | null = null;   // ще немає — файл не читаний
  constructor(private path: string) {}     // конструктор дешевий: лише запам'ятали шлях

  private load(): RealImage {
    if (this.real === null) this.real = new RealImage(this.path);   // читаємо ОДИН раз
    return this.real;
  }

  draw(): void { this.load().draw(); }       // прийшли малювати → тепер треба справжній
  width(): number { return this.load().width(); }
}

// Клієнт не бачить різниці — тип той самий:
const gallery: Image[] = paths.map(p => new ImageProxy(p));   // 2000 картинок, 0 читань із диска
gallery[0].draw();   // читається РІВНО одна — перша
