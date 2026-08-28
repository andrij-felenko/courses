#include <stdio.h>

int main(void) {
    printf("=== Демонстрація DiophBuilder API (C) ===\n");
    DiophContext* ctx = dioph_context_create(64 * 1024); // 64 КБ арени

    const DiophExpr* x = dioph_var(ctx, "x");
    const DiophExpr* y = dioph_var(ctx, "y");
    const DiophExpr* z = dioph_var(ctx, "z");

    // Предикат 1: x^2 + y^2 = z^2
    const DiophExpr* x2 = dioph_mul(ctx, x, x);
    const DiophExpr* y2 = dioph_mul(ctx, y, y);
    const DiophExpr* z2 = dioph_mul(ctx, z, z);
    const DiophExpr* x2_plus_y2 = dioph_add(ctx, x2, y2);
    const DiophPred* pythagoras = dioph_equal(ctx, x2_plus_y2, z2);

    // Предикат 2: x | y (x ділить y)
    const DiophPred* divides = dioph_gadget_div(ctx, x, y);

    // Повний предикат: pythagoras AND divides
    const DiophPred* system = dioph_and(ctx, pythagoras, divides);

    // Компіляція у єдиний многочлен P(x, y, z, q) = 0
    const DiophExpr* compiled_poly = dioph_compile_to_polynomial(ctx, system);
    const DiophExpr* opt_poly = dioph_optimize_expr(ctx, compiled_poly);

    if (opt_poly && ctx->last_error == DIOPH_OK) {
        printf("Многочлен успішно скомпільовано та оптимізовано.\n");
        printf("Вираз: ");
        dioph_expr_print(opt_poly, ctx);
        printf("\nЗагальна кількість змінних у системі: %zu\n", ctx->var_count);
        for (size_t i = 0; i < ctx->var_count; ++i) {
            printf("  Змінна [%zu]: %s\n", i, ctx->variables[i].name);
        }
        printf("Використано пам'яті арени: %zu байтів\n", ctx->allocated_bytes);
    } else {
        printf("Помилка компіляції діофантового виразу: код %d\n", ctx->last_error);
    }

    dioph_context_free(ctx);
    return 0;
}
