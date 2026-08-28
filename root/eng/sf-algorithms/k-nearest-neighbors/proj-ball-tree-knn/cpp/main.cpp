#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <queue>
#include <numeric>
#include <algorithm>
#include <span>
#include <limits>
#include <array>

template <size_t Dim = 3>
struct Point {
    std::array<double, Dim> coords{};
    int id{-1};

    [[nodiscard]] double distance_to(const Point& other) const noexcept {
        double sum = 0.0;
        for (size_t i = 0; i < Dim; ++i) {
            const double diff = coords[i] - other.coords[i];
            sum += diff * diff;
        }
        return std::sqrt(sum);
    }
};

struct Neighbor {
    int id;
    double dist;

    bool operator<(const Neighbor& other) const noexcept {
        return dist < other.dist; // Для max-heap: найбільша відстань нагорі
    }
};

template <size_t Dim = 3>
class BallTree {
public:
    static constexpr size_t LeafCapacity = 2;

    explicit BallTree(std::span<const Point<Dim>> points) {
        std::vector<Point<Dim>> pts(points.begin(), points.end());
        root_ = build(pts);
    }

    [[nodiscard]] std::vector<Neighbor> find_knn(const Point<Dim>& query, size_t k) const {
        std::priority_queue<Neighbor> max_heap;
        search(root_.get(), query, k, max_heap);

        std::vector<Neighbor> result;
        result.reserve(max_heap.size());
        while (!max_heap.empty()) {
            result.push_back(max_heap.top());
            max_heap.pop();
        }
        std::reverse(result.begin(), result.end()); // Від найближчого до найдальшого
        return result;
    }

private:
    struct Node {
        Point<Dim> center{};
        double radius{0.0};
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;
        std::vector<Point<Dim>> leaf_points;
        bool is_leaf{false};
    };

    std::unique_ptr<Node> root_;

    static void compute_bounding_ball(Node& node, std::span<const Point<Dim>> pts) {
        std::array<double, Dim> sum{};
        for (const auto& p : pts) {
            for (size_t d = 0; d < Dim; ++d) {
                sum[d] += p.coords[d];
            }
        }
        for (size_t d = 0; d < Dim; ++d) {
            node.center.coords[d] = sum[d] / static_cast<double>(pts.size());
        }

        double max_r = 0.0;
        for (const auto& p : pts) {
            max_r = std::max(max_r, node.center.distance_to(p));
        }
        node.radius = max_r;
    }

    std::unique_ptr<Node> build(std::span<Point<Dim>> pts) {
        if (pts.empty()) return nullptr;

        auto node = std::make_unique<Node>();
        compute_bounding_ball(*node, pts);

        if (pts.size() <= LeafCapacity) {
            node->is_leaf = true;
            node->leaf_points.assign(pts.begin(), pts.end());
            return node;
        }

        // Пошук двох найвіддаленіших точок (півотів) A і B
        size_t pivot_a = 0;
        double max_d = -1.0;
        for (size_t i = 1; i < pts.size(); ++i) {
            if (double d = pts[0].distance_to(pts[i]); d > max_d) {
                max_d = d;
                pivot_a = i;
            }
        }

        size_t pivot_b = pivot_a;
        max_d = -1.0;
        for (size_t i = 0; i < pts.size(); ++i) {
            if (double d = pts[pivot_a].distance_to(pts[i]); d > max_d) {
                max_d = d;
                pivot_b = i;
            }
        }

        // Розбиття точок за відстанню до двох центрів
        const Point<Dim> pa = pts[pivot_a];
        const Point<Dim> pb = pts[pivot_b];

        auto mid = std::partition(pts.begin(), pts.end(), [&](const Point<Dim>& p) {
            return p.distance_to(pa) <= p.distance_to(pb);
        });

        size_t left_size = std::distance(pts.begin(), mid);
        if (left_size == 0 || left_size == pts.size()) {
            mid = pts.begin() + pts.size() / 2;
        }

        node->left = build(std::span<Point<Dim>>(pts.begin(), mid));
        node->right = build(std::span<Point<Dim>>(mid, pts.end()));

        return node;
    }

    void search(const Node* node, const Point<Dim>& query, size_t k,
                std::priority_queue<Neighbor>& heap) const {
        if (!node) return;

        const double d_center = query.distance_to(node->center);
        const double d_min = std::max(0.0, d_center - node->radius);

        const double current_max_dist = (heap.size() < k) ?
            std::numeric_limits<double>::infinity() : heap.top().dist;

        // Відсікання піддерева за нерівністю трикутника
        if (d_min >= current_max_dist) {
            return;
        }

        if (node->is_leaf) {
            for (const auto& pt : node->leaf_points) {
                const double d = query.distance_to(pt);
                if (heap.size() < k) {
                    heap.push(Neighbor{pt.id, d});
                } else if (d < heap.top().dist) {
                    heap.pop();
                    heap.push(Neighbor{pt.id, d});
                }
            }
            return;
        }

        // Пріоритетний спуск у ближчу сферу
        const double d_left = node->left ? query.distance_to(node->left->center) : std::numeric_limits<double>::infinity();
        const double d_right = node->right ? query.distance_to(node->right->center) : std::numeric_limits<double>::infinity();

        if (d_left < d_right) {
            search(node->left.get(), query, k, heap);
            search(node->right.get(), query, k, heap);
        } else {
            search(node->right.get(), query, k, heap);
            search(node->left.get(), query, k, heap);
        }
    }
};

int main() {
    std::vector<Point<3>> points = {
        {{{1.0, 2.0, 3.0}}, 1},
        {{{1.1, 2.1, 2.9}}, 2},
        {{{5.0, 6.0, 7.0}}, 3},
        {{{5.2, 5.9, 7.1}}, 4},
        {{{8.0, 9.0, 1.0}}, 5},
        {{{1.2, 1.9, 3.1}}, 6},
        {{{5.1, 6.2, 6.8}}, 7}
    };

    BallTree<3> tree(points);
    Point<3> query{{{1.05, 2.05, 3.0}}, 0};

    auto neighbors = tree.find_knn(query, 3);

    std::cout << "Результати точного 3-NN пошуку (C++):\n";
    for (const auto& n : neighbors) {
        std::cout << "  Сусід ID=" << n.id << ", dist=" << n.dist << "\n";
    }

    return 0;
}
