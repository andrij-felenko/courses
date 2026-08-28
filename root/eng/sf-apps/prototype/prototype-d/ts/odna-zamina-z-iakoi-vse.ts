interface Shape {
  clone(): Shape;               // «зроблю ще один такий, як я»
  render(): void;
}

class Circle implements Shape {
  constructor(public x: number, public y: number, public r: number) {}
  clone(): Shape {              // повертає новий Circle — того самого класу
    return new Circle(this.x, this.y, this.r);
  }
  render() { /* намалювати коло */ }
}
