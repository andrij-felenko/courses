// Вузли дерева — кожен уміє тільки прийняти відвідувача й покликати свій visit.
interface Expr {
    <R> R accept(Visitor<R> v);
}

final class Num implements Expr {
    final int value;
    Num(int value) { this.value = value; }
    public <R> R accept(Visitor<R> v) { return v.visitNum(this); }
}
final class Add implements Expr {
    final Expr left, right;
    Add(Expr left, Expr right) { this.left = left; this.right = right; }
    public <R> R accept(Visitor<R> v) { return v.visitAdd(this); }
}
final class Mul implements Expr {
    final Expr left, right;
    Mul(Expr left, Expr right) { this.left = left; this.right = right; }
    public <R> R accept(Visitor<R> v) { return v.visitMul(this); }
}

// Операція — окремий об'єкт. Один метод на кожен вид вузла.
interface Visitor<R> {
    R visitNum(Num n);
    R visitAdd(Add a);
    R visitMul(Mul m);
}

// Прохід 1: обчислити значення (R = Integer).
final class Eval implements Visitor<Integer> {
    public Integer visitNum(Num n) { return n.value; }
    public Integer visitAdd(Add a) { return a.left.accept(this) + a.right.accept(this); }
    public Integer visitMul(Mul m) { return m.left.accept(this) * m.right.accept(this); }
}

// Прохід 2: надрукувати у дужках (R = String).
final class Print implements Visitor<String> {
    public String visitNum(Num n) { return Integer.toString(n.value); }
    public String visitAdd(Add a) { return "(" + a.left.accept(this) + " + " + a.right.accept(this) + ")"; }
    public String visitMul(Mul m) { return "(" + m.left.accept(this) + " * " + m.right.accept(this) + ")"; }
}
