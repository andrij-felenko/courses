#include <vector>
#include <optional>
#include <limits>
#include <cstdint>
#include <span>

class FloydWarshall {
public:
    static constexpr int64_t INF_DIST = std::numeric_limits<int64_t>::max() / 4;
    static constexpr int64_t NEG_INF  = -INF_DIST;
    static constexpr int NO_NEXT      = -1;

    explicit FloydWarshall(int n)
        : n_(n),
          dist_(static_cast<size_t>(n) * n, INF_DIST),
          next_(static_cast<size_t>(n) * n, NO_NEXT) {
        for (int i = 0; i < n_; ++i) {
            dist_[idx(i, i)] = 0;
            next_[idx(i, i)] = i;
        }
    }

    void add_edge(int u, int v, int64_t weight) {
        if (u < 0 || u >= n_ || v < 0 || v >= n_) return;
        size_t p = idx(u, v);
        if (weight < dist_[p]) {
            dist_[p] = weight;
            next_[p] = v;
        }
    }

    void compute() {
        // Фаза 1: Рекурентне оновлення за проміжною вершиною k
        for (int k = 0; k < n_; ++k) {
            for (int i = 0; i < n_; ++i) {
                int64_t dik = dist_[idx(i, k)];
                if (dik >= INF_DIST) continue;

                for (int j = 0; j < n_; ++j) {
                    int64_t dkj = dist_[idx(k, j)];
                    if (dkj >= INF_DIST) continue;

                    int64_t alt = dik + dkj;
                    size_t pij = idx(i, j);
                    if (alt < dist_[pij]) {
                        dist_[pij] = alt;
                        next_[pij] = next_[idx(i, k)];
                    }
                }
            }
        }

        // Фаза 2: Виявлення та маркування від'ємних циклів
        for (int k = 0; k < n_; ++k) {
            if (dist_[idx(k, k)] < 0) {
                for (int i = 0; i < n_; ++i) {
                    for (int j = 0; j < n_; ++j) {
                        if (dist_[idx(i, k)] < INF_DIST && dist_[idx(k, j)] < INF_DIST) {
                            dist_[idx(i, j)] = NEG_INF;
                            next_[idx(i, j)] = NO_NEXT;
                        }
                    }
                }
            }
        }
    }

    [[nodiscard]] int64_t get_distance(int u, int v) const {
        return dist_[idx(u, v)];
    }

    [[nodiscard]] std::optional<std::vector<int>> reconstruct_path(int u, int v) const {
        if (u < 0 || u >= n_ || v < 0 || v >= n_) return std::nullopt;
        size_t p = idx(u, v);
        if (dist_[p] >= INF_DIST || dist_[p] == NEG_INF || next_[p] == NO_NEXT) {
            return std::nullopt;
        }

        std::vector<int> path;
        path.push_back(u);
        int cur = u;
        int step_limit = 0;
        
        while (cur != v && step_limit < n_) {
            cur = next_[idx(cur, v)];
            if (cur == NO_NEXT) return std::nullopt;
            path.push_back(cur);
            step_limit++;
        }
        
        if (cur != v) return std::nullopt; // знайдено цикл або розрив
        return path;
    }

private:
    [[nodiscard]] inline size_t idx(int i, int j) const noexcept {
        return static_cast<size_t>(i) * static_cast<size_t>(n_) + static_cast<size_t>(j);
    }

    int n_;
    std::vector<int64_t> dist_;
    std::vector<int> next_;
};
