#include <vector>
#include <cstddef>
#include <utility>
#include <numeric>

class BipartiteDSU {
public:
    explicit BipartiteDSU(std::size_t n)
        : parent_(n), parity_(n, 0) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    // Повертає пару {корінь, парність відносно кореня}
    std::pair<std::size_t, int> find(std::size_t x) {
        if (parent_[x] == x) {
            return {x, 0};
        }
        auto [root, p] = find(parent_[x]);
        parent_[x] = root;
        parity_[x] ^= p;
        return {parent_[x], parity_[x]};
    }

    bool add_edge(std::size_t x, std::size_t y) {
        auto [rx, px] = find(x);
        auto [ry, py] = find(y);

        if (rx == ry) {
            // Граф залишається дводольним, якщо елементи мають різну парність
            return px != py;
        }

        parent_[rx] = ry;
        parity_[rx] = px ^ py ^ 1;
        return true;
    }

private:
    std::vector<std::size_t> parent_;
    std::vector<int> parity_;
};
