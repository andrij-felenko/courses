#include <span>

class DiophantineEvaluator {
public:
    static int64_t evaluate(const ExprPtr& expr, std::span<const int64_t> var_values) {
        if (!expr) return 0;

        switch (expr->kind) {
            case ExprKind::Const:
                return std::get<int64_t>(expr->payload);
            case ExprKind::Var:
                return var_values[std::get<uint32_t>(expr->payload)];
            case ExprKind::Add: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                return evaluate(b.lhs, var_values) + evaluate(b.rhs, var_values);
            }
            case ExprKind::Sub: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                return evaluate(b.lhs, var_values) - evaluate(b.rhs, var_values);
            }
            case ExprKind::Mul: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                return evaluate(b.lhs, var_values) * evaluate(b.rhs, var_values);
            }
            case ExprKind::Sqr: {
                int64_t val = evaluate(std::get<ExprPtr>(expr->payload), var_values);
                return val * val;
            }
        }
        return 0;
    }
};
