// Нова операція — НОВИЙ клас. Жоден вузол не відкрито.
struct Rpn : Visitor {
    std::string result;
    std::string run(const Expr& e) { e.accept(*this); return result; }
    void visitNum(const Num& n) override { result = std::to_string(n.value); }
    void visitAdd(const Add& a) override { result = run(*a.left) + " " + run(*a.right) + " +"; }
    void visitMul(const Mul& m) override { result = run(*m.left) + " " + run(*m.right) + " *"; }
};

Rpn{}.run(tree);   // "2 3 + 4 *"
