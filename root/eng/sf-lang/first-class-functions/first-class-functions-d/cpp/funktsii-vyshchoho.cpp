#include <iostream>
#include <span>
#include <vector>
#include <algorithm>

/* В ідіоматичному C++ функція вищого порядку приймає довільний callable */
template <typename Predicate>
std::vector<int> filter_integers(std::span<const int> src, Predicate pred) {
    std::vector<int> dst;
    for (int val : src) {
        if (pred(val)) {
            dst.push_back(val);
        }
    }
    return dst;
}

int main() {
    std::vector<int> data = {12, 45, 3, 89, 23, 67, 8};
    int threshold = 25;

    // Лямбда-вираз автоматично захоплює поріг без ручного void*
    auto results = filter_integers(data, [threshold](int val) {
        return val > threshold;
    });

    for (int val : results) {
        std::cout << val << " "; /* 45 89 67 */
    }
    std::cout << "\n";
    return 0;
}
