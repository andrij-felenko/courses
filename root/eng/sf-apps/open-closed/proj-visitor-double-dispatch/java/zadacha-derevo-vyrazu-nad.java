interface Expr {
    int eval();
    String print();   // щоб додати друк, довелося ВІДКРИТИ інтерфейс…
}

final class Num implements Expr {
    final int value;
    Num(int value) { this.value = value; }
    public int eval() { return value; }
    public String print() { return Integer.toString(value); }   // …і КОЖЕН клас
}
final class Add implements Expr {
    final Expr left, right;
    Add(Expr left, Expr right) { this.left = left; this.right = right; }
    public int eval() { return left.eval() + right.eval(); }
    public String print() { return "(" + left.print() + " + " + right.print() + ")"; }
}
final class Mul implements Expr {
    final Expr left, right;
    Mul(Expr left, Expr right) { this.left = left; this.right = right; }
    public int eval() { return left.eval() * right.eval(); }
    public String print() { return "(" + left.print() + " * " + right.print() + ")"; }
}
