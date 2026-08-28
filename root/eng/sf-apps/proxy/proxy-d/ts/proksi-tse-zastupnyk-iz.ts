interface Image {
  draw(): void;
  width(): number;
}

// Справжній об'єкт: створення = читання файлу з диска (дорого).
class RealImage implements Image {
  private pixels: Uint8Array;
  constructor(private path: string) {
    this.pixels = loadFromDisk(path);   // читаємо ВЕСЬ файл уже в конструкторі
    console.log(`завантажено ${path}`);
  }
  draw(): void { /* малюємо pixels */ }
  width(): number { return readWidthOf(this.pixels); }
}
