#include <vector>
#include <cstddef>
#include <numeric>

class RollbackDSU {
public:
    struct Operation {
        std::size_t u;
        std::size_t v;
        std::size_t rank_u;
        std::size_t rank_v;
    };

    explicit RollbackDSU(std::size_t n)
        : parent_(n), rank_(n, 0), num_sets_(n) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    // Без стиснення шляхів! Зберігаємо точну висоту дерев
    [[nodiscard]] std::size_t find(std::size_t x) const noexcept {
        while (x != parent_[x]) {
            x = parent_[x];
        }
        return x;
    }

    bool unite(std::size_t x, std::size_t y) {
        std::size_t root_x = find(x);
        std::size_t root_y = find(y);

        history_.push_back({root_x, root_y, rank_[root_x], rank_[root_y]});

        if (root_x == root_y) {
            return false;
        }

        if (rank_[root_x] < rank_[root_y]) {
            parent_[root_x] = root_y;
        } else if (rank_[root_x] > rank_[root_y]) {
            parent_[root_y] = root_x;
        } else {
            parent_[root_y] = root_x;
            rank_[root_x]++;
        }

        num_sets_--;
        return true;
    }

    void undo() {
        if (history_.empty()) return;

        const auto op = history_.back();
        history_.pop_back();

        if (op.u == op.v) return;

        parent_[op.u] = op.u;
        parent_[op.v] = op.v;
        rank_[op.u] = op.rank_u;
        rank_[op.v] = op.rank_v;
        num_sets_++;
    }

    [[nodiscard]] std::size_t history_size() const noexcept {
        return history_.size();
    }

private:
    std::vector<std::size_t> parent_;
    std::vector<std::size_t> rank_;
    std::vector<Operation> history_;
    std::size_t num_sets_;
};
