#include <vector>
#include <string>

enum class ASTOp { Var, Not, And, Or };

struct ASTNode {
    ASTOp op;
    int var_id{0}; // Заповнюється, якщо op == Var
    std::vector<ASTNode> children; // Для And/Or містить n аргументів
};
