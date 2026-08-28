// Кожна операція — метод у контракті.
struct Expr {
    virtual ~Expr() = default;
    virtual int eval() const = 0;
    virtual std::string print() const = 0;   // щоб додати друк, довелося ВІДКРИТИ інтерфейс…
};

struct Num : Expr {
    int value;
    explicit Num(int value) : value(value) {}
    int eval() const override { return value; }
    std::string print() const override { return std::to_string(value); }   // …і КОЖЕН клас
};
struct Add : Expr {
    const Expr *left, *right;
    Add(const Expr* left, const Expr* right) : left(left), right(right) {}
    int eval() const override { return left->eval() + right->eval(); }
    std::string print() const override { return "(" + left->print() + " + " + right->print() + ")"; }
};
struct Mul : Expr {
    const Expr *left, *right;
    Mul(const Expr* left, const Expr* right) : left(left), right(right) {}
    int eval() const override { return left->eval() * right->eval(); }
    std::string print() const override { return "(" + left->print() + " * " + right->print() + ")"; }
};
