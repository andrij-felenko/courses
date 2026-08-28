const DiophPred* dioph_gadget_le(DiophContext* ctx, const DiophExpr* a, const DiophExpr* b) {
    const DiophExpr* k = dioph_var(ctx, "_k_le");
    const DiophExpr* a_plus_k = dioph_add(ctx, a, k);
    return dioph_equal(ctx, b, a_plus_k);
}

const DiophPred* dioph_gadget_div(DiophContext* ctx, const DiophExpr* a, const DiophExpr* b) {
    const DiophExpr* q = dioph_var(ctx, "_q_div");
    const DiophExpr* a_mul_q = dioph_mul(ctx, a, q);
    return dioph_equal(ctx, b, a_mul_q);
}

const DiophPred* dioph_gadget_pell(DiophContext* ctx, const DiophExpr* x, 
                                   const DiophExpr* y, const DiophExpr* d) {
    const DiophExpr* x2 = dioph_mul(ctx, x, x);
    const DiophExpr* y2 = dioph_mul(ctx, y, y);
    const DiophExpr* dy2 = dioph_mul(ctx, d, y2);
    const DiophExpr* lhs = dioph_sub(ctx, x2, dy2);
    const DiophExpr* one = dioph_const(ctx, 1);
    return dioph_equal(ctx, lhs, one);
}

const DiophPred* dioph_gadget_fibonacci(DiophContext* ctx, const DiophExpr* f) {
    const DiophExpr* g = dioph_var(ctx, "_g_fib");
    const DiophExpr* g2 = dioph_mul(ctx, g, g);
    const DiophExpr* fg = dioph_mul(ctx, f, g);
    const DiophExpr* f2 = dioph_mul(ctx, f, f);
    const DiophExpr* diff1 = dioph_sub(ctx, g2, fg);
    const DiophExpr* diff2 = dioph_sub(ctx, diff1, f2);
    const DiophExpr* one = dioph_const(ctx, 1);
    return dioph_equal(ctx, diff2, one);
}
