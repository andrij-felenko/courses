#include <iostream>
#include <vector>
#include <span>

void run_cpp_parity_workflow() {
    using namespace kalmar;

    auto div_expr = Expression::make_div(Expression::make_variable(0), Expression::make_constant(2));
    auto mul_expr = Expression::make_mul(Expression::make_constant(2), std::move(div_expr));
    auto rem_expr = Expression::make_sub(Expression::make_variable(0), std::move(mul_expr));
    auto is_even  = Expression::make_sub(Expression::make_constant(1), std::move(rem_expr));

    size_t k = is_even.tower_height();
    std::cout << "C++ API: Verified tower height k = " << k << "\n";

    std::vector<uint64_t> env_vars(2, 0);
    env_vars[0] = 42;

    auto res = is_even.evaluate_as_predicate(env_vars);
    if (res.has_value()) {
        std::cout << "Number 42 is " << (res.value() ? "EVEN" : "ODD") << "\n";
    }
}
