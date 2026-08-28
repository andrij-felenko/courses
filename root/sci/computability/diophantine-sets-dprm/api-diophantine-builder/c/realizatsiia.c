#include <stdio.h>

void dioph_expr_print(const DiophExpr* expr, const DiophContext* ctx) {
    if (!expr) return;
    switch (expr->type) {
        case EXPR_CONST:
            printf("%lld", (long long)expr->as.const_val);
            break;
        case EXPR_VAR:
            printf("%s", ctx->variables[expr->as.var_id].name);
            break;
        case EXPR_ADD:
            printf("(");
            dioph_expr_print(expr->as.binary.lhs, ctx);
            printf(" + ");
            dioph_expr_print(expr->as.binary.rhs, ctx);
            printf(")");
            break;
        case EXPR_SUB:
            printf("(");
            dioph_expr_print(expr->as.binary.lhs, ctx);
            printf(" - ");
            dioph_expr_print(expr->as.binary.rhs, ctx);
            printf(")");
            break;
        case EXPR_MUL:
            printf("(");
            dioph_expr_print(expr->as.binary.lhs, ctx);
            printf(" * ");
            dioph_expr_print(expr->as.binary.rhs, ctx);
            printf(")");
            break;
        case EXPR_SQR:
            printf("(");
            dioph_expr_print(expr->as.unary_sqr, ctx);
            printf("^2)");
            break;
    }
}
