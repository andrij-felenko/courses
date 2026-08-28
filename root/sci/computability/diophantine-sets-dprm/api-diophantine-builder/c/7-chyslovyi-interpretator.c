int64_t dioph_expr_eval(const DiophExpr* expr, const int64_t* var_values, DiophStatus* status) {
    if (!expr) {
        if (status) *status = DIOPH_ERR_INVALID_ARGUMENT;
        return 0;
    }
    switch (expr->type) {
        case EXPR_CONST:
            return expr->as.const_val;
        case EXPR_VAR:
            return var_values[expr->as.var_id];
        case EXPR_ADD: {
            int64_t l = dioph_expr_eval(expr->as.binary.lhs, var_values, status);
            int64_t r = dioph_expr_eval(expr->as.binary.rhs, var_values, status);
            return l + r;
        }
        case EXPR_SUB: {
            int64_t l = dioph_expr_eval(expr->as.binary.lhs, var_values, status);
            int64_t r = dioph_expr_eval(expr->as.binary.rhs, var_values, status);
            return l - r;
        }
        case EXPR_MUL: {
            int64_t l = dioph_expr_eval(expr->as.binary.lhs, var_values, status);
            int64_t r = dioph_expr_eval(expr->as.binary.rhs, var_values, status);
            return l * r;
        }
        case EXPR_SQR: {
            int64_t val = dioph_expr_eval(expr->as.unary_sqr, var_values, status);
            return val * val;
        }
    }
    return 0;
}
