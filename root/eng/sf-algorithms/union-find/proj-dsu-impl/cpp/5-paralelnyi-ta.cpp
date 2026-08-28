#include <vector>
#include <atomic>
#include <cstddef>
#include <utility>

class LockFreeDSU {
public:
    explicit LockFreeDSU(std::size_t n) : parent_(n) {
        for (std::size_t i = 0; i < n; ++i) {
            parent_[i].store(static_cast<int>(i), std::memory_order_relaxed);
        }
    }

    // Атомарне ітеративне уполовинення шляху
    [[nodiscard]] int find(int x) noexcept {
        while (true) {
            int p = parent_[x].load(std::memory_order_relaxed);
            if (p == x) return x;

            int grand_p = parent_[p].load(std::memory_order_relaxed);
            // Атомарно пробуємо перевизначити parent[x] -> grand_p
            parent_[x].compare_exchange_weak(p, grand_p, std::memory_order_relaxed);
            x = parent_[x].load(std::memory_order_relaxed);
        }
    }

    bool unite(int x, int y) noexcept {
        while (true) {
            int root_x = find(x);
            int root_y = find(y);

            if (root_x == root_y) return false;

            // Детермінований порядок об'єднання для запобігання дедлокам
            if (root_x > root_y) {
                std::swap(root_x, root_y);
            }

            int expected = root_y;
            if (parent_[root_y].compare_exchange_strong(expected, root_x, std::memory_order_acq_rel)) {
                return true;
            }
        }
    }

private:
    std::vector<std::atomic<int>> parent_;
};
