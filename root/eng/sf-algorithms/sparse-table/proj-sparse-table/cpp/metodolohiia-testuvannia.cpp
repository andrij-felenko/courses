#include <vector>
#include <random>
#include <algorithm>
#include <cassert>
#include <iostream>

void run_fuzz_test_cpp(std::size_t n, std::size_t num_queries) {
    std::mt19937_64 rng(1337);
    std::uniform_int_distribution<int32_t> dist(-1'000'000, 1'000'000);

    std::vector<int32_t> data(n);
    for (auto& x : data) x = dist(rng);

    SparseTable<int32_t> st(data);

    std::uniform_int_distribution<std::size_t> idx_dist(0, n - 1);

    for (std::size_t q = 0; q < num_queries; ++q) {
        std::size_t l = idx_dist(rng);
        std::size_t r = idx_dist(rng);
        if (l > r) std::swap(l, r);

        auto res = st.query(l, r);
        assert(res.has_value());

        int32_t expected = *std::min_element(data.begin() + l, data.begin() + r + 1);
        assert(*res == expected);
    }

    std::cout << "C++ фазинг-тест успішно пройдено (" << num_queries << " запитів на N=" << n << ").\n";
}
