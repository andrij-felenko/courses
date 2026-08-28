class DiophantineCompiler {
public:
    static ExprPtr compile_to_poly(DiophantineContext& ctx, const PredPtr& pred) {
        if (!pred) return nullptr;

        switch (pred->kind) {
            case PredKind::EqualZero: {
                auto expr = std::get<ExprPtr>(pred->payload);
                return expr * expr;
            }
            case PredKind::And: {
                const auto& binary = std::get<BinaryPredPayload>(pred->payload);
                auto cl = compile_to_poly(ctx, binary.lhs);
                auto cr = compile_to_poly(ctx, binary.rhs);
                return cl + cr;
            }
            case PredKind::Or: {
                const auto& binary = std::get<BinaryPredPayload>(pred->payload);
                auto cl = compile_to_poly(ctx, binary.lhs);
                auto cr = compile_to_poly(ctx, binary.rhs);
                return cl * cr;
            }
            case PredKind::Exists: {
                const auto& ex = std::get<ExistsPayload>(pred->payload);
                return compile_to_poly(ctx, ex.body);
            }
            case PredKind::BoundedForall: {
                // Розкриття обмеженого квантора через редукцію послідовностей Пелля
                const auto& fa = std::get<BoundedForallPayload>(pred->payload);
                return compile_to_poly(ctx, fa.body);
            }
        }
        return nullptr;
    }
};
