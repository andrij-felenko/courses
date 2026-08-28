#include <iostream>
#include <vector>
#include <span>
#include <format>
#include <center_manifold.hpp>

int main() {
    CM::SolverConfig config{.max_taylor_order = 3};

    auto sys_exp = CM::create_system(1, 1);
    if (!sys_exp) {
        std::cerr << "Помилка створення системи\n";
        return 1;
    }

    auto sys = std::move(*sys_exp);
    sys.set_matrix_A(std::array{0.0});
    sys.set_matrix_B(std::array{-5.0});

    sys.set_nonlinearity_f([](auto x, auto y, auto out_f) {
        out_f[0] = x[0] * y[0];
    });

    sys.set_nonlinearity_g([](auto x, auto y, auto out_g) {
        out_g[0] = x[0] * x[0];
    });

    auto mf_exp = CM::compute_manifold(sys, config);
    if (!mf_exp) {
        std::cerr << "Помилка обчислення многовиду\n";
        return 1;
    }

    const auto& mf = *mf_exp;
    std::cout << std::format("Многовид успішно побудовано (порядок {})\n", mf.order());

    CM::Solver solver(sys, mf);
    std::vector<double> x_state{0.3};
    constexpr double dt = 0.01;

    for (int step = 0; step < 50; ++step) {
        solver.step_reduced_rk4(x_state, dt);
        if (step % 10 == 0) {
            auto y_eval = mf.evaluate(x_state);
            std::cout << std::format("Крок {:2d}: x = {:.6f}, h(x) = {:.6f}\n", 
                                     step, x_state[0], y_eval[0]);
        }
    }

    return 0;
}
