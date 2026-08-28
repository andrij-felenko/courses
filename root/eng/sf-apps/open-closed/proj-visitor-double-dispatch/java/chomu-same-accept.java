interface Visitor {
    void visit(Num n);
    void visit(Add a);
    void visit(Mul m);
}

Expr e = new Add(new Num(2), new Num(3));   // статичний тип змінної — Expr
visitor.visit(e);   // ✗ не компілюється: перевантаження visit(Expr) немає.
                    //   Java обирає перевантаження за СТАТИЧНИМ типом e (Expr),
                    //   а не за тим, що там Add у рантаймі.
