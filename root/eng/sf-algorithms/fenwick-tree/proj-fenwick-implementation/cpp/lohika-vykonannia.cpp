#include <vector>
#include <cstddef>
#include <stdexcept>

template <typename T = long long>
class FenwickTree2D {
private:
    std::size_t rows_;
    std::size_t cols_;
    std::vector<std::vector<T>> tree_;

    static constexpr std::size_t lsb(std::size_t i) noexcept {
        return i & (-i);
    }

public:
    FenwickTree2D(std::size_t rows, std::size_t cols)
        : rows_(rows), cols_(cols),
          tree_(rows + 1, std::vector<T>(cols + 1, T{0})) {}

    void add(std::size_t r, std::size_t c, T val) {
        if (r >= rows_ || c >= cols_) {
            throw std::out_of_range("Некоректні індекси 2D дерева Фенвіка");
        }
        for (std::size_t i = r + 1; i <= rows_; i += lsb(i)) {
            for (std::size_t j = c + 1; j <= cols_; j += lsb(j)) {
                tree_[i][j] += val;
            }
        }
    }

    [[nodiscard]] T query_prefix(std::size_t r, std::size_t c) const {
        if (r >= rows_ || c >= cols_) {
            throw std::out_of_range("Некоректні індекси 2D дерева Фенвіка");
        }
        T sum = T{0};
        for (std::size_t i = r + 1; i > 0; i -= lsb(i)) {
            for (std::size_t j = c + 1; j > 0; j -= lsb(j)) {
                sum += tree_[i][j];
            }
        }
        return sum;
    }

    [[nodiscard]] T query_rect(std::size_t r1, std::size_t c1, std::size_t r2, std::size_t c2) const {
        if (r1 > r2 || c1 > c2 || r2 >= rows_ || c2 >= cols_) {
            throw std::out_of_range("Некоректні межі прямокутника");
        }
        T res = query_prefix(r2, c2);
        if (r1 > 0) res -= query_prefix(r1 - 1, c2);
        if (c1 > 0) res -= query_prefix(r2, c1 - 1);
        if (r1 > 0 && c1 > 0) res += query_prefix(r1 - 1, c1 - 1);
        return res;
    }
};
