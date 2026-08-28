#include <iostream>
#include <vector>
#include <span>
#include <algorithm>
#include <cmath>
#include <random>
#include <functional>
#include <stdexcept>

namespace algo {

/*
 * Шаблонний Introselect мовою C++20.
 * Поєднує ітеративний Quickselect із тристороннім розбиттям
 * та аварійним перемиканням на std::nth_element / heapsort при деградації.
 */
template <typename RandomIt, typename Compare = std::less<>>
void introselect(RandomIt first, RandomIt last, size_t k_idx, Compare comp = Compare{}) {
    auto n = std::distance(first, last);
    if (n <= 1 || k_idx >= static_cast<size_t>(n)) {
        return;
    }

    /* Ліміт глибини рекурсії: 2 * log2(n) */
    size_t depth_limit = static_cast<size_t>(2 * std::log2(n));
    RandomIt left = first;
    RandomIt right = last - 1;

    std::mt19937 rng(1337);

    while (left < right) {
        /* Аварійне перемикання при перевищенні глибини рекурсії */
        if (depth_limit == 0) {
            std::nth_element(left, left + (k_idx - std::distance(first, left)), right + 1, comp);
            return;
        }
        --depth_limit;

        /* Вибір півота за методом медіани трьох */
        RandomIt mid = left + std::distance(left, right) / 2;
        if (comp(*mid, *left)) std::iter_swap(left, mid);
        if (comp(*right, *left)) std::iter_swap(left, right);
        if (comp(*right, *mid)) std::iter_swap(mid, right);

        /* Ставимо pivot на початок діапазону */
        std::iter_swap(left, mid);
        auto pivot_val = *left;

        /* Тристороннє розбиття (3-way partition) */
        RandomIt lt = left;
        RandomIt i = left + 1;
        RandomIt gt = right;

        while (i <= gt) {
            if (comp(*i, pivot_val)) {
                std::iter_swap(lt, i);
                ++lt;
                ++i;
            } else if (comp(pivot_val, *i)) {
                std::iter_swap(i, gt);
                if (gt == left) break;
                --gt;
            } else {
                ++i;
            }
        }

        size_t lt_dist = static_cast<size_t>(std::distance(first, lt));
        size_t gt_dist = static_cast<size_t>(std::distance(first, gt));

        if (k_idx < lt_dist) {
            if (lt == first) break;
            right = lt - 1;
        } else if (k_idx > gt_dist) {
            left = gt + 1;
        } else {
            /* Елемент на індексі k знаходиться у зоні рівних півоту */
            return;
        }
    }
}

} // namespace algo

int main() {
    std::vector<int> numbers = {9, 1, 5, 3, 7, 2, 8, 5, 5, 0, 4, 6};
    size_t k = 6; /* 7-й найменший елемент */

    algo::introselect(numbers.begin(), numbers.end(), k);

    std::cout << "Елемент на індексі " << k << ": " << numbers[k] << "\n";
    std::cout << "Перші " << k << " елементів (перцентиль): ";
    for (size_t i = 0; i < k; ++i) {
        std::cout << numbers[i] << " ";
    }
    std::cout << "\n";

    return 0;
}
