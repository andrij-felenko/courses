#include <iostream>
#include <vector>
#include <cmath>
#include "qs_schrodinger_1d.h"

int main() {
    // 1. Конфігурація сітки
    qs_grid_config_t grid_cfg = {
        .x_min = -6.0,
        .x_max = 6.0,
        .num_points = 2001,
        .mass = 1.0, // m = 1
        .hbar = 1.0  // hbar = 1
    };

    // 2. Параметри розв'язувача
    qs_solver_params_t params = {
        .method = QS_METHOD_NUMEROV,
        .tolerance = 1e-8,
        .max_iterations = 300,
        .boundary_left = QS_BOUNDARY_DIRICHLET,
        .boundary_right = QS_BOUNDARY_DIRICHLET,
        .num_eigenvalues = 3
    };

    // 3. Створення розв'язувача
    qs_solver_t *solver = qs_solver_create(&grid_cfg, &params);
    if (!solver) {
        std::cerr << "Не вдалося створити розв'язувач!\n";
        return 1;
    }

    // 4. Задання параболічного потенціалу V(x) = 0.5 * x^2
    auto harmonic_potential = [](double x, void *user_data) -> double {
        (void)user_data;
        return 0.5 * x * x;
    };
    qs_solver_set_potential_func(solver, harmonic_potential, nullptr);

    // 5. Запуск обчислень
    qs_result_t result{};
    int status = qs_solver_run(solver, &result);

    if (status == QS_SUCCESS) {
        std::cout << "Розрахунок успішно завершено за " << result.compute_time_us << " мкс.\n";
        std::cout << "Знайдено власних станів: " << result.num_found << "\n\n";

        for (uint32_t i = 0; i < result.num_found; ++i) {
            const auto &st = result.states[i];
            std::cout << "Стан n=" << st.state_index 
                      << " | E = " << st.energy 
                      << " | Вузлів: " << st.node_count 
                      << " | Похибка: " << st.energy_error << "\n";
        }
    } else {
        std::cerr << "Помилка розрахунку! Код: " << status << "\n";
    }

    // 6. Звільнення ресурсів
    qs_result_free(&result);
    qs_solver_destroy(solver);

    return 0;
}
