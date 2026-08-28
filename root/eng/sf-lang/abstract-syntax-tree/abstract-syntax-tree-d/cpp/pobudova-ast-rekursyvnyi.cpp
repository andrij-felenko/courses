#include <memory>
#include <string>
#include <utility>

// Базовий вузол AST
struct ASTNode {
    virtual ~ASTNode() = default;
};

// Вузол чисельної константи (Листок)
struct NumberNode : public ASTNode {
    double value;
    explicit NumberNode(double val) : value(val) {}
};

// Вузол бінарної операції (Внутрішній вузол)
struct BinaryOpNode : public ASTNode {
    char op;
    std::unique_ptr<ASTNode> left;
    std::unique_ptr<ASTNode> right;

    BinaryOpNode(char op, std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r)
        : op(op), left(std::move(l)), right(std::move(r)) {}
};
