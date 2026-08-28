#include <vector>
#include <numeric>
#include <algorithm>

// Еталон: сума добутків по всіх n! перестановках стовпців. Складність O(n · n!).
template <class T>
T perm_naive(const std::vector<std::vector<T>>& A) {
    int n = (int)A.size();
    std::vector<int> col(n);
    std::iota(col.begin(), col.end(), 0);          // col = 0,1,…,n−1 — тотожна перестановка
    T total = 0;
    do {
        T prod = 1;
        for (int i = 0; i < n; ++i)
            prod *= A[i][col[i]];                   // по одному елементу з кожного рядка й стовпця
        total += prod;
    } while (std::next_permutation(col.begin(), col.end()));
    return total;
}
