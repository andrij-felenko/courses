abstract class Figure {
  // фабричний метод — ШОВ між ієрархією фігур та ієрархією маніпуляторів
  abstract createManipulator(): Manipulator;
  abstract draw(): void;
}

class LineFigure extends Figure {
  createManipulator(): Manipulator { return new LineManipulator(this); }
  draw(): void { /* ... */ }
}
class TextFigure extends Figure {
  createManipulator(): Manipulator { return new TextManipulator(this); }
  draw(): void { /* ... */ }
}
