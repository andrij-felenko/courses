struct Num; struct Add; struct Mul;          // попереднє оголошення вузлів

// Операція — окремий об'єкт. Один метод на кожен вид вузла.
struct Visitor {
    virtual ~Visitor() = default;
    virtual void visitNum(const Num& n) = 0;
    virtual void visitAdd(const Add& a) = 0;
    virtual void visitMul(const Mul& m) = 0;
};

// Вузли дерева — кожен уміє тільки прийняти відвідувача й покликати свій visit.
struct Expr {
    virtual ~Expr() = default;
    virtual void accept(Visitor& v) const = 0;
};

struct Num : Expr {
    int value;
    explicit Num(int value) : value(value) {}
    void accept(Visitor& v) const override { v.visitNum(*this); }
};
struct Add : Expr {
    const Expr *left, *right;
    Add(const Expr* left, const Expr* right) : left(left), right(right) {}
    void accept(Visitor& v) const override { v.visitAdd(*this); }
};
struct Mul : Expr {
    const Expr *left, *right;
    Mul(const Expr* left, const Expr* right) : left(left), right(right) {}
    void accept(Visitor& v) const override { v.visitMul(*this); }
};

// Прохід 1: обчислити значення. Кожен відвідувач несе свій типізований результат (int).
struct Eval : Visitor {
    int result = 0;
    int run(const Expr& e) { e.accept(*this); return result; }
    void visitNum(const Num& n) override { result = n.value; }
    void visitAdd(const Add& a) override { result = run(*a.left) + run(*a.right); }
    void visitMul(const Mul& m) override { result = run(*m.left) * run(*m.right); }
};

// Прохід 2: надрукувати у дужках (тут результат — std::string).
struct Print : Visitor {
    std::string result;
    std::string run(const Expr& e) { e.accept(*this); return result; }
    void visitNum(const Num& n) override { result = std::to_string(n.value); }
    void visitAdd(const Add& a) override { result = "(" + run(*a.left) + " + " + run(*a.right) + ")"; }
    void visitMul(const Mul& m) override { result = "(" + run(*m.left) + " * " + run(*m.right) + ")"; }
};
