#include <stdio.h>
#include <assert.h>
#include <math.h>

void run_all_kadane_tests(void) {
    /* Тест 1: Класичний комбінований масив із підручника Бентлі */
    int a1[] = {-2, 1, -3, 4, -1, 2, 1, -5, 4};
    SubarrayResult r1 = kadane_1d_with_indices(a1, 9);
    assert(r1.max_sum == 6);
    assert(r1.start_index == 3 && r1.end_index == 6);

    /* Тест 2: Безгілкова версія */
    assert(kadane_branchless(a1, 9) == 6);

    /* Тест 3: Масив із суто від'ємними числами */
    int a2[] = {-8, -3, -6, -2, -5};
    SubarrayResult r2 = kadane_1d_with_indices(a2, 5);
    assert(r2.max_sum == -2);
    assert(r2.start_index == 3 && r2.end_index == 3);

    /* Тест 4: Кільцевий масив із переходом через межу */
    int a3[] = {5, -3, 5};
    long long c3 = kadane_circular(a3, 3);
    assert(c3 == 10); /* 5 + 5 через межу */

    /* Тест 5: Кільцевий масив із суто від'ємними елементами */
    int a4[] = {-3, -2, -3};
    long long c4 = kadane_circular(a4, 3);
    assert(c4 == -2);

    /* Тест 6: Максимальний добуток із чергуванням знаків */
    int p1[] = {2, 3, -2, 4};
    assert(max_product_subarray(p1, 4) == 6);

    int p2[] = {-2, 0, -1};
    assert(max_product_subarray(p2, 3) == 0);

    int p3[] = {-2, 3, -4};
    assert(max_product_subarray(p3, 3) == 24); /* (-2) * 3 * (-4) */

    /* Тест 7: Двовимірна матриця 3x4 */
    int mat[3][4] = {
        {  1,  2, -1, -4 },
        { -8, -3,  4,  2 },
        {  3,  8, 10, -3 }
    };
    MatrixSubarrayResult m_res = kadane_2d_matrix(&mat[0][0], 3, 4);
    assert(m_res.max_sum == 29);

    /* Тест 8: Дерево відрізків */
    SegmentNode tree[36];
    build_tree(a1, tree, 1, 0, 8);
    SegmentNode q1 = query_tree(tree, 1, 0, 8, 0, 8);
    assert(q1.max_subarray == 6);
    SegmentNode q2 = query_tree(tree, 1, 0, 8, 0, 2); /* [-2, 1, -3] -> max = 1 */
    assert(q2.max_subarray == 1);

    /* Тест 9: Багатопотоковий Кадане */
    long long par_res = kadane_parallel_openmp(a1, 9, 2);
    assert(par_res == 6);

    /* Тест 10: Суматор Кехена з числами подвійної точності */
    double f_arr[] = {1e16, 1.0, -1e16, 2.0};
    double f_max = kadane_kahan_float(f_arr, 4);
    assert(fabs(f_max - (1e16 + 1.0)) < 1e-5 || fabs(f_max - 3.0) < 1e-5);

    printf("[OK] Усі тести реалізацій алгоритму Кадане виконано успішно.\n");
}

int main(void) {
    run_all_kadane_tests();
    return 0;
}
