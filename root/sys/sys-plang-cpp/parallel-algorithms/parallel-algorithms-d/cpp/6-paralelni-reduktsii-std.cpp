#include <numeric>
#include <execution>
#include <vector>
#include <iostream>

void demonstrate_reduction() {
    std::vector<double> values(10'000'000, 1.0);

    // 1. Послідовне лінійне згортання C++98 (O(N) кроків)
    double sum_seq = std::accumulate(values.begin(), values.end(), 0.0);

    // 2. Паралельне деревоподібне згортання C++17 (O(log N) глибина)
    double sum_par = std::reduce(std::execution::par_unseq, values.begin(), values.end(), 0.0);

    std::cout << "Сума seq: " << sum_seq << ", Сума par: " << sum_par << '\n';
}
