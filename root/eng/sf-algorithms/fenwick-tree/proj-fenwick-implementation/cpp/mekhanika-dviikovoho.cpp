#include <vector>
#include <cstddef>

// Знаходження найменшого 0-based індексу idx, для якого query_prefix(idx) >= target_sum
// Умова: усі елементи масиву неот'ємні (A[i] >= 0)
template <typename T = long long>
std::size_t lower_bound_fenwick(const FenwickTree<T>& ft, T target_sum) {
    if (target_sum <= 0) return 0;

    std::size_t n = ft.size();
    std::size_t idx = 0;
    T current_sum = T{0};

    // Знаходимо найближчу більшу або рівну степінь двійки
    std::size_t max_pow = 1;
    while ((max_pow << 1) <= n) {
        max_pow <<= 1;
    }

    for (std::size_t len = max_pow; len > 0; len >>= 1) {
        std::size_t next_idx = idx + len;
        if (next_idx <= n && current_sum + ft.tree_[next_idx] < target_sum) {
            idx = next_idx;
            current_sum += ft.tree_[idx];
        }
    }

    // idx повертає 0-based індекс шуканого елемента
    return idx;
}
