// Спільний інтерфейс: кожен вузол уміє обчислити сам себе
interface Expr {
  interpret(env: Map<string, number>): number;
}

// Термінали — листя дерева: обчислюються без звертань кудись далі
class Num implements Expr {
  constructor(private value: number) {}
  interpret(_env: Map<string, number>): number { return this.value; }
}
class Var implements Expr {
  constructor(private name: string) {}
  interpret(env: Map<string, number>): number {
    const v = env.get(this.name);
    if (v === undefined) throw new Error(`невідома змінна ${this.name}`);
    return v;
  }
}

// Нетермінали — тримають під-вирази й рекурсивно їх обчислюють
class Add implements Expr {
  constructor(private left: Expr, private right: Expr) {}
  interpret(env: Map<string, number>): number {
    return this.left.interpret(env) + this.right.interpret(env);
  }
}
class Mul implements Expr {
  constructor(private left: Expr, private right: Expr) {}
  interpret(env: Map<string, number>): number {
    return this.left.interpret(env) * this.right.interpret(env);
  }
}

// Вираз "x + 3 * 2" — зібраний як дерево об'єктів
const tree: Expr = new Add(new Var("x"), new Mul(new Num(3), new Num(2)));
console.log(tree.interpret(new Map([["x", 5]])));   // 11
