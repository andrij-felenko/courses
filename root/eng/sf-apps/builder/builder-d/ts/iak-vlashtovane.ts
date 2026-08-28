class PizzaBuilder {
  private size: number;
  private hasCheese = false;
  private hasBacon = false;

  constructor(size: number) {          // обов'язкове поле — у конструкторі
    this.size = size;
  }

  cheese(): this {                     // крок повертає САМ будівельник...
    this.hasCheese = true;
    return this;                       // ...тому виклики й чіпляються в ланцюжок
  }
  bacon(): this {
    this.hasBacon = true;
    return this;
  }

  build(): Pizza {                     // остаточне зібрання — тут
    return new Pizza(this.size, this.hasCheese, this.hasBacon);
  }
}
