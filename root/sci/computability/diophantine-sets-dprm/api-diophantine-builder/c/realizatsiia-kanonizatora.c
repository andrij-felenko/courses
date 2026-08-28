const DiophExpr* dioph_compile_to_polynomial(DiophContext* ctx, const DiophPred* pred) {
    if (!pred) return NULL;

    switch (pred->type) {
        case PRED_EQUAL_ZERO: {
            const DiophExpr* e = pred->as.eq_zero_expr;
            return dioph_mul(ctx, e, e);
        }
        case PRED_AND: {
            const DiophExpr* cl = dioph_compile_to_polynomial(ctx, pred->as.binary.lhs);
            const DiophExpr* cr = dioph_compile_to_polynomial(ctx, pred->as.binary.rhs);
            return dioph_add(ctx, cl, cr);
        }
        case PRED_OR: {
            const DiophExpr* cl = dioph_compile_to_polynomial(ctx, pred->as.binary.lhs);
            const DiophExpr* cr = dioph_compile_to_polynomial(ctx, pred->as.binary.rhs);
            return dioph_mul(ctx, cl, cr);
        }
        case PRED_EXISTS: {
            return dioph_compile_to_polynomial(ctx, pred->as.exists.body);
        }
        default:
            ctx->last_error = DIOPH_ERR_INVALID_ARGUMENT;
            return NULL;
    }
}
