#include <iostream>
#include <vector>
#include <array>
#include <algorithm>
#include <limits>
#include <memory>
#include <span>
#include <cmath>

template <size_t K>
struct Point {
    std::array<double, K> coords{};
    int id{0};

    [[nodiscard]] double distance_squared(const Point<K>& other) const noexcept {
        double sum = 0.0;
        for (size_t i = 0; i < K; ++i) {
            double diff = coords[i] - other.coords[i];
            sum += diff * diff;
        }
        return sum;
    }
};

template <size_t K>
class KDTree {
public:
    struct Node {
        Point<K> point;
        size_t left{std::numeric_limits<size_t>::max()};
        size_t right{std::numeric_limits<size_t>::max()};
    };

private:
    std::vector<Node> nodes_;
    size_t root_{std::numeric_limits<size_t>::max()};

    size_t build_recursive(std::span<Point<K>> pts, size_t depth) {
        if (pts.empty()) {
            return std::numeric_limits<size_t>::max();
        }

        const size_t mid = pts.size() / 2;
        const size_t d = depth % K;

        // Швидкий вибір медіани через std::nth_element за лінійний час O(N)
        std::nth_element(pts.begin(), pts.begin() + mid, pts.end(),
            [d](const Point<K>& a, const Point<K>& b) noexcept {
                return a.coords[d] < b.coords[d];
            });

        const size_t current_idx = nodes_.size();
        nodes_.push_back(Node{pts[mid], std::numeric_limits<size_t>::max(), std::numeric_limits<size_t>::max()});

        if (mid > 0) {
            nodes_[current_idx].left = build_recursive(pts.subspan(0, mid), depth + 1);
        }
        if (mid + 1 < pts.size()) {
            nodes_[current_idx].right = build_recursive(pts.subspan(mid + 1), depth + 1);
        }

        return current_idx;
    }

    void nn_search_recursive(size_t node_idx, const Point<K>& target, size_t depth,
                             const Point<K>*& best_pt, double& best_dist_sq) const noexcept {
        if (node_idx >= nodes_.size()) return;

        const auto& node = nodes_[node_idx];
        const double d_sq = node.point.distance_squared(target);

        if (d_sq < best_dist_sq) {
            best_dist_sq = d_sq;
            best_pt = &node.point;
        }

        const size_t d = depth % K;
        const double diff = target.coords[d] - node.point.coords[d];
        const double diff_sq = diff * diff;

        const size_t near_child = (diff <= 0.0) ? node.left : node.right;
        const size_t far_child  = (diff <= 0.0) ? node.right : node.left;

        // 1. Пріоритетний спуск у ближчу половину простору
        if (near_child < nodes_.size()) {
            nn_search_recursive(near_child, target, depth + 1, best_pt, best_dist_sq);
        }

        // 2. Геометричне відсікання гілок (Pruning) за відстанню до розділової площини
        if (diff_sq < best_dist_sq && far_child < nodes_.size()) {
            nn_search_recursive(far_child, target, depth + 1, best_pt, best_dist_sq);
        }
    }

    void range_query_recursive(size_t node_idx, const Point<K>& min_pt, const Point<K>& max_pt,
                               size_t depth, std::vector<Point<K>>& results) const {
        if (node_idx >= nodes_.size()) return;

        const auto& node = nodes_[node_idx];
        bool inside = true;
        for (size_t i = 0; i < K; ++i) {
            if (node.point.coords[i] < min_pt.coords[i] || node.point.coords[i] > max_pt.coords[i]) {
                inside = false;
                break;
            }
        }
        if (inside) {
            results.push_back(node.point);
        }

        const size_t d = depth % K;
        if (node.point.coords[d] >= min_pt->coords[d] && node.left < nodes_.size()) {
            range_query_recursive(node.left, min_pt, max_pt, depth + 1, results);
        }
        if (node.point.coords[d] <= max_pt->coords[d] && node.right < nodes_.size()) {
            range_query_recursive(node.right, min_pt, max_pt, depth + 1, results);
        }
    }

public:
    explicit KDTree(std::vector<Point<K>> points) {
        nodes_.reserve(points.size());
        root_ = build_recursive(std::span<Point<K>>(points), 0);
    }

    [[nodiscard]] std::pair<const Point<K>*, double> nearest_neighbor(const Point<K>& target) const noexcept {
        if (nodes_.empty() || root_ >= nodes_.size()) {
            return {nullptr, std::numeric_limits<double>::infinity()};
        }
        const Point<K>* best_pt = nullptr;
        double best_dist_sq = std::numeric_limits<double>::infinity();
        nn_search_recursive(root_, target, 0, best_pt, best_dist_sq);
        return {best_pt, best_dist_sq};
    }

    [[nodiscard]] std::vector<Point<K>> range_query(const Point<K>& min_pt, const Point<K>& max_pt) const {
        std::vector<Point<K>> results;
        if (!nodes_.empty() && root_ < nodes_.size()) {
            range_query_recursive(root_, min_pt, max_pt, 0, results);
        }
        return results;
    }

    [[nodiscard]] size_t size() const noexcept { return nodes_.size(); }
    [[nodiscard]] bool empty() const noexcept { return nodes_.empty(); }
};
