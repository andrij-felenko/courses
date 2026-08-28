#include <iostream>
#include <vector>
#include <optional>
#include <functional>
#include <span>

struct SearchProfile {
    std::size_t num_vars{0};
    int64_t max_bound{0};
    uint64_t evaluated_points{0};
};

template <typename Predicate>
class DiophantineSolver {
public:
    explicit DiophantineSolver(Predicate poly, std::size_t dimensions)
        : poly_(std::move(poly)), dimensions_(dimensions) {}

    std::optional<std::vector<int64_t>> search(int64_t max_bound, SearchProfile& stats) {
        stats.num_vars = dimensions_;
        stats.max_bound = max_bound;
        stats.evaluated_points = 0;

        std::vector<int64_t> current(dimensions_, 0);

        for (int64_t b = 0; b <= max_bound; ++b) {
            if (search_layer(current, 0, b, (b == 0), stats)) {
                return current;
            }
        }
        return std::nullopt;
    }

private:
    bool search_layer(std::vector<int64_t>& current, std::size_t idx, 
                      int64_t bound, bool has_boundary, SearchProfile& stats) {
        if (idx == dimensions_) {
            if (!has_boundary) return false;
            stats.evaluated_points++;
            return poly_(std::span<const int64_t>(current)) == 0;
        }

        for (int64_t val = 0; val <= bound; ++val) {
            current[idx] = val;
            const bool on_bound = has_boundary || (val == bound);
            if (search_layer(current, idx + 1, bound, on_bound, stats)) {
                return true;
            }
        }
        return false;
    }

    Predicate poly_;
    std::size_t dimensions_;
};
