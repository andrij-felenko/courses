class DiophantineGadgets {
public:
    static PredPtr less_or_equal(DiophantineContext& ctx, ExprPtr a, ExprPtr b) {
        auto k = ctx.make_fresh_existential("k_le");
        return (std::move(b) == (std::move(a) + k));
    }

    static PredPtr divides(DiophantineContext& ctx, ExprPtr a, ExprPtr b) {
        auto q = ctx.make_fresh_existential("q_div");
        return (std::move(b) == (std::move(a) * q));
    }

    static PredPtr pell_relation(DiophantineContext& ctx, ExprPtr x, ExprPtr y, ExprPtr d) {
        auto x2 = x * x;
        auto y2 = y * y;
        auto dy2 = d * y2;
        auto lhs = x2 - dy2;
        auto one = ctx.make_const(1);
        return (lhs == one);
    }

    static PredPtr fibonacci_member(DiophantineContext& ctx, ExprPtr f) {
        auto g = ctx.make_fresh_existential("g_fib");
        auto cassini = (g * g - f * g - f * f == ctx.make_const(1));
        return cassini;
    }
};
