#include <vector>
#include <cstddef>
#include <stdexcept>

template <typename T = long long>
class FenwickTree {
private:
    std::size_t n_;
    std::vector<T> tree_;

    static constexpr std::size_t lsb(std::size_t i) noexcept {
        return i & (-i);
    }

public:
    explicit FenwickTree(std::size_t size)
        : n_(size), tree_(size + 1, T{0}) {}

    // Ініціалізація за O(N) з вихідного вектора
    explicit FenwickTree(const std::vector<T>& data)
        : n_(data.size()), tree_(data.size() + 1, T{0}) {
        for (std::size_t i = 0; i < n_; ++i) {
            tree_[i + 1] += data[i];
            std::size_t parent = (i + 1) + lsb(i + 1);
            if (parent <= n_) {
                tree_[parent] += tree_[i + 1];
            }
        }
    }

    // Точкове додавання значення v до елемента за індексом idx (0-based)
    void add(std::size_t idx, T val) {
        if (idx >= n_) {
            throw std::out_of_range("Індекс виходить за межі дерева Фенвіка");
        }
        for (std::size_t i = idx + 1; i <= n_; i += lsb(i)) {
            tree_[i] += val;
        }
    }

    // Префіксна сума від елемента 0 до idx включно (0-based)
    [[nodiscard]] T query_prefix(std::size_t idx) const {
        if (idx >= n_) {
            throw std::out_of_range("Індекс виходить за межі дерева Фенвіка");
        }
        T sum = T{0};
        for (std::size_t i = idx + 1; i > 0; i -= lsb(i)) {
            sum += tree_[i];
        }
        return sum;
    }

    // Запит суми на відрізку [left, right] включно (0-based)
    [[nodiscard]] T query_range(std::size_t left, std::size_t right) const {
        if (left > right || right >= n_) {
            throw std::out_of_range("Некоректні межі відрізка запиту");
        }
        if (left == 0) {
            return query_prefix(right);
        }
        return query_prefix(right) - query_prefix(left - 1);
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return n_;
    }
};
