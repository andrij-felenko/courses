const DiophExpr* dioph_optimize_expr(DiophContext* ctx, const DiophExpr* expr) {
    if (!expr) return NULL;
    if (expr->type == EXPR_CONST || expr->type == EXPR_VAR) return expr;

    if (expr->type == EXPR_ADD) {
        const DiophExpr* lhs = dioph_optimize_expr(ctx, expr->as.binary.lhs);
        const DiophExpr* rhs = dioph_optimize_expr(ctx, expr->as.binary.rhs);
        if (lhs->type == EXPR_CONST && rhs->type == EXPR_CONST) {
            return dioph_const(ctx, lhs->as.const_val + rhs->as.const_val);
        }
        if (lhs->type == EXPR_CONST && lhs->as.const_val == 0) return rhs;
        if (rhs->type == EXPR_CONST && rhs->as.const_val == 0) return lhs;
        return dioph_add(ctx, lhs, rhs);
    }

    if (expr->type == EXPR_MUL) {
        const DiophExpr* lhs = dioph_optimize_expr(ctx, expr->as.binary.lhs);
        const DiophExpr* rhs = dioph_optimize_expr(ctx, expr->as.binary.rhs);
        if (lhs->type == EXPR_CONST && rhs->type == EXPR_CONST) {
            return dioph_const(ctx, lhs->as.const_val * rhs->as.const_val);
        }
        if ((lhs->type == EXPR_CONST && lhs->as.const_val == 0) ||
            (rhs->type == EXPR_CONST && rhs->as.const_val == 0)) {
            return dioph_const(ctx, 0);
        }
        if (lhs->type == EXPR_CONST && lhs->as.const_val == 1) return rhs;
        if (rhs->type == EXPR_CONST && rhs->as.const_val == 1) return lhs;
        return dioph_mul(ctx, lhs, rhs);
    }

    return expr;
}
