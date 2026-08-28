#include <cassert>
#include <random>
#include <iostream>

void run_invariant_fuzz_test(int num_tests = 1000) {
    std::mt19937_64 rng(1337);
    std::uniform_int_distribution<int> v_dist(10, 50);
    std::uniform_int_distribution<int> cap_dist(1, 1000);

    for (int t = 0; t < num_tests; ++t) {
        int n = v_dist(rng);
        int s = 0, target = n - 1;
        DinicSolver<int64_t> solver(n);

        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                if (i != j && (rng() % 4 == 0)) {
                    solver.add_edge(i, j, cap_dist(rng));
                }
            }
        }

        int64_t flow = solver.max_flow(s, target);
        std::vector<bool> cut = solver.min_cut(s);

        // Перевірка інваріантів розрізу
        assert(cut[s] == true);
        assert(cut[target] == false || flow == 0);
    }
    std::cout << "Усі стрес-тести інваріантів успішно пройдено!\n";
}
