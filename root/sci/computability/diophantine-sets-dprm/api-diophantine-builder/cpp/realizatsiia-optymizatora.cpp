class DiophantineOptimizer {
public:
    static ExprPtr optimize(DiophantineContext& ctx, const ExprPtr& expr) {
        if (!expr) return nullptr;
        if (expr->kind == ExprKind::Const || expr->kind == ExprKind::Var) {
            return expr;
        }

        if (expr->kind == ExprKind::Add) {
            const auto& b = std::get<BinaryExprPayload>(expr->payload);
            auto lhs = optimize(ctx, b.lhs);
            auto rhs = optimize(ctx, b.rhs);

            if (lhs->kind == ExprKind::Const && rhs->kind == ExprKind::Const) {
                return ctx.make_const(std::get<int64_t>(lhs->payload) + std::get<int64_t>(rhs->payload));
            }
            if (lhs->kind == ExprKind::Const && std::get<int64_t>(lhs->payload) == 0) return rhs;
            if (rhs->kind == ExprKind::Const && std::get<int64_t>(rhs->payload) == 0) return lhs;
            return lhs + rhs;
        }

        if (expr->kind == ExprKind::Mul) {
            const auto& b = std::get<BinaryExprPayload>(expr->payload);
            auto lhs = optimize(ctx, b.lhs);
            auto rhs = optimize(ctx, b.rhs);

            if (lhs->kind == ExprKind::Const && rhs->kind == ExprKind::Const) {
                return ctx.make_const(std::get<int64_t>(lhs->payload) * std::get<int64_t>(rhs->payload));
            }
            if ((lhs->kind == ExprKind::Const && std::get<int64_t>(lhs->payload) == 0) ||
                (rhs->kind == ExprKind::Const && std::get<int64_t>(rhs->payload) == 0)) {
                return ctx.make_const(0);
            }
            if (lhs->kind == ExprKind::Const && std::get<int64_t>(lhs->payload) == 1) return rhs;
            if (rhs->kind == ExprKind::Const && std::get<int64_t>(rhs->payload) == 1) return lhs;
            return lhs * rhs;
        }

        return expr;
    }
};
