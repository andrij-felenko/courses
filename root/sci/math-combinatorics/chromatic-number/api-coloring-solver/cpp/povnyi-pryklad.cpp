#include <iostream>
#include <format>
#include "coloring_solver.hpp"

int main() {
    using namespace coloring;

    Graph graph(11);

    /* Базовий цикл C5 */
    (void)graph.add_edge(0, 1);
    (void)graph.add_edge(1, 2);
    (void)graph.add_edge(2, 3);
    (void)graph.add_edge(3, 4);
    (void)graph.add_edge(4, 0);

    /* Тіньові вершини */
    (void)graph.add_edge(5, 1);
    (void)graph.add_edge(5, 4);
    (void)graph.add_edge(6, 0);
    (void)graph.add_edge(6, 2);
    (void)graph.add_edge(7, 1);
    (void)graph.add_edge(7, 3);
    (void)graph.add_edge(8, 2);
    (void)graph.add_edge(8, 4);
    (void)graph.add_edge(9, 0);
    (void)graph.add_edge(9, 3);

    /* Верхівка apex */
    for (int32_t i = 5; i <= 9; ++i) {
        (void)graph.add_edge(10, i);
    }

    SolverConfig config{
        .engine = Engine::BranchAndPrice,
        .time_limit = std::chrono::milliseconds{10000},
        .symmetry_breaking_level = 2,
        .enable_kempe_pass = true,
        .random_seed = 1337
    };

    Solver solver(config);

    auto solve_result = solver.solve(graph);
    if (!solve_result) {
        const auto& diag = solve_result.error();
        std::cerr << std::format("Помилка розв'язання: {} (код {})\n",
                                 diag.message, static_cast<int32_t>(diag.last_error));
        return 1;
    }

    const auto& res = *solve_result;
    std::cout << std::format("Отримано розв'язок: χ(G) = {}, знайдено за {} мкс\n",
                             res.chromatic_number, res.elapsed.count());

    for (size_t i = 0; i < res.colors.size(); ++i) {
        std::cout << std::format("  Вузол {:2} -> Колір {}\n", i, res.colors[i]);
    }

    /* Верифікація правильності розфарбування */
    auto verify_res = Solver::verify(graph, res);
    if (verify_res) {
        std::cout << "Верифікація успішна: розфарбування строго правильне, конфліктів немає.\n";
    } else {
        std::cerr << std::format("Помилка верифікації на ребрі ({}, {})\n",
                                 verify_res.error().conflict_u, verify_res.error().conflict_v);
    }

    /* Експорт результату в JSON */
    auto export_res = Solver::export_json("grotzsch_result.json", graph, res);
    if (!export_res) {
        std::cerr << "Не вдалося зберегти JSON-звіт.\n";
    }

    return 0;
}
