// Крок рефакторингу: та сама поведінка, зрозуміліша будова.
// Магічні числа стали іменами, гілки — окремими функціями.
static constexpr double VIP_THRESHOLD = 1000.0;
static constexpr double VIP_RATE      = 0.15;

double compute_discount(const Cart& cart, bool vip) {
    const double subtotal = cart.subtotal();
    if (vip && subtotal >= VIP_THRESHOLD)
        return subtotal * VIP_RATE;          // 1200 · 0.15 = 180 — тест досі зелений
    return regular_discount(subtotal);
}
