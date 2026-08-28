#include <memory>
#include <variant>
#include <string>
#include <vector>

enum class ExprKind { Const, Var, Add, Sub, Mul, Sqr };
enum class PredKind { EqualZero, And, Or, Exists, BoundedForall };

struct ExprNode;
using ExprPtr = std::shared_ptr<const ExprNode>;

struct BinaryExprPayload {
    ExprPtr lhs;
    ExprPtr rhs;
};

struct ExprNode {
    ExprKind kind;
    std::variant<int64_t, uint32_t, BinaryExprPayload, ExprPtr> payload;
};

struct PredNode;
using PredPtr = std::shared_ptr<const PredNode>;

struct BinaryPredPayload {
    PredPtr lhs;
    PredPtr rhs;
};

struct ExistsPayload {
    uint32_t var_id;
    PredPtr body;
};

struct BoundedForallPayload {
    uint32_t var_id;
    ExprPtr limit;
    PredPtr body;
};

struct PredNode {
    PredKind kind;
    std::variant<ExprPtr, BinaryPredPayload, ExistsPayload, BoundedForallPayload> payload;
};

struct VariableInfo {
    std::string name;
    uint32_t id{0};
    bool is_existential{false};
};
