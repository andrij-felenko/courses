#include <vector>
#include <cstddef>
#include <stdexcept>

template <typename T = long long>
class FenwickRangeRange {
private:
    std::size_t n_;
    FenwickTree<T> t1_;
    FenwickTree<T> t2_;

    [[nodiscard]] T prefix_sum(std::size_t idx) const {
        if (idx == static_cast<std::size_t>(-1)) return T{0};
        T sum1 = t1_.query_prefix(idx);
        T sum2 = t2_.query_prefix(idx);
        return sum1 * static_cast<T>(idx + 1) - sum2;
    }

public:
    explicit FenwickRangeRange(std::size_t size)
        : n_(size), t1_(size), t2_(size) {}

    // Додати val до всіх елементів на відрізку [left, right] (0-based)
    void range_add(std::size_t left, std::size_t right, T val) {
        if (left > right || right >= n_) {
            throw std::out_of_range("Некоректні межі для RangeAdd");
        }
        t1_.add(left, val);
        t2_.add(left, val * static_cast<T>(left));

        if (right + 1 < n_) {
            t1_.add(right + 1, -val);
            t2_.add(right + 1, -val * static_cast<T>(right + 1));
        }
    }

    // Сума елементів на відрізку [left, right] (0-based)
    [[nodiscard]] T query_range(std::size_t left, std::size_t right) const {
        if (left > right || right >= n_) {
            throw std::out_of_range("Некоректні межі для RangeQuery");
        }
        if (left == 0) return prefix_sum(right);
        return prefix_sum(right) - prefix_sum(left - 1);
    }
};
