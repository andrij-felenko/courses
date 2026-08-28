#include <iostream>
#include <cassert>
#include <vector>
#include <cmath>

void run_all_kadane_tests() {
    // Тест 1: Класичний масив із підручника Бентлі
    std::vector<int> a1{-2, 1, -3, 4, -1, 2, 1, -5, 4};
    auto r1 = kadane_1d_with_indices(a1);
    assert(r1.has_value());
    assert(r1->max_sum == 6);
    assert(r1->start_index == 3 && r1->end_index == 6);

    // Тест 2: Безгілкова версія
    assert(kadane_branchless(a1) == 6);

    // Тест 3: Масив із суто від'ємними числами
    std::vector<int> a2{-8, -3, -6, -2, -5};
    auto r2 = kadane_1d_with_indices(a2);
    assert(r2.has_value());
    assert(r2->max_sum == -2);
    assert(r2->start_index == 3 && r2->end_index == 3);

    // Тест 4: Кільцевий масив із переходом через межу
    std::vector<int> a3{5, -3, 5};
    assert(kadane_circular(a3) == 10);

    // Тест 5: Кільцевий масив із суто від'ємними числами
    std::vector<int> a4{-3, -2, -3};
    assert(kadane_circular(a4) == -2);

    // Тест 6: Максимальний добуток
    std::vector<int> p1{2, 3, -2, 4};
    assert(max_product_subarray(p1) == 6);

    std::vector<int> p2{-2, 0, -1};
    assert(max_product_subarray(p2) == 0);

    std::vector<int> p3{-2, 3, -4};
    assert(max_product_subarray(p3) == 24);

    // Тест 7: Двовимірна матриця 3x4
    std::vector<std::vector<int>> mat{
        {  1,  2, -1, -4 },
        { -8, -3,  4,  2 },
        {  3,  8, 10, -3 }
    };
    auto m_res = kadane_2d_matrix(mat);
    assert(m_res.has_value());
    assert(m_res->max_sum == 29);

    // Тест 8: Дерево відрізків
    KadaneSegmentTree seg_tree(a1);
    assert(seg_tree.query_max_subarray(0, 8) == 6);
    assert(seg_tree.query_max_subarray(0, 2) == 1);
    seg_tree.update(2, 10); // масив: [-2, 1, 10, 4, -1, 2, 1, -5, 4]
    assert(seg_tree.query_max_subarray(0, 8) == 17); // [1..6]: 1+10+4-1+2+1 = 17

    // Тест 9: Багатопотоковий Кадане
    assert(kadane_parallel_openmp(a1, 2) == 6);

    // Тест 10: Суматор Кехена
    std::vector<double> f_arr{1e16, 1.0, -1e16, 2.0};
    double f_max = kadane_kahan_float(f_arr);
    assert(std::fabs(f_max - (1e16 + 1.0)) < 1e-5 || std::fabs(f_max - 3.0) < 1e-5);

    std::cout << "[OK] Усі C++ тести реалізацій алгоритму Кадане виконано успішно.\n";
}

int main() {
    run_all_kadane_tests();
    return 0;
}
