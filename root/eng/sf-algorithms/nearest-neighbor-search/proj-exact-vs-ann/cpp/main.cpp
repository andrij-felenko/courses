#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <memory>
#include <span>

struct Point {
    std::vector<float> coords;
    int id{0};
};

struct SearchResult {
    Point point;
    float distance{std::numeric_limits<float>::infinity()};
    size_t distance_evals{0};
};

class FlatIndex {
public:
    explicit FlatIndex(std::vector<Point> points, int dim)
        : points_(std::move(points)), dim_(dim) {}

    [[nodiscard]] SearchResult find_nearest(std::span<const float> query) const {
        SearchResult result;
        float min_dist_sq = std::numeric_limits<float>::max();

        for (const auto& pt : points_) {
            ++result.distance_evals;
            float d_sq = 0.0f;
            for (int i = 0; i < dim_; ++i) {
                float diff = pt.coords[i] - query[i];
                d_sq += diff * diff;
            }
            if (d_sq < min_dist_sq) {
                min_dist_sq = d_sq;
                result.point = pt;
            }
        }
        result.distance = std::sqrt(min_dist_sq);
        return result;
    }

private:
    std::vector<Point> points_;
    int dim_{0};
};

class VPTree {
public:
    explicit VPTree(std::vector<Point> points, int dim) : dim_(dim) {
        root_ = build(std::span<Point>(points));
    }

    [[nodiscard]] SearchResult find_nearest(std::span<const float> query) const {
        SearchResult result;
        search(root_.get(), query, result);
        return result;
    }

private:
    struct Node {
        Point vantage_point;
        float threshold{0.0f};
        std::unique_ptr<Node> inside;
        std::unique_ptr<Node> outside;
    };

    int dim_{0};
    std::unique_ptr<Node> root_;

    [[nodiscard]] float distance(std::span<const float> a, std::span<const float> b) const {
        float sum = 0.0f;
        for (int i = 0; i < dim_; ++i) {
            float diff = a[i] - b[i];
            sum += diff * diff;
        }
        return std::sqrt(sum);
    }

    std::unique_ptr<Node> build(std::span<Point> points) {
        if (points.empty()) return nullptr;

        auto node = std::make_unique<Node>();
        node->vantage_point = points[0];

        if (points.size() == 1) return node;

        const auto& vp_coords = node->vantage_point.coords;
        auto rest = points.subspan(1);

        size_t mid = rest.size() / 2;
        std::nth_element(rest.begin(), rest.begin() + mid, rest.end(),
            [this, &vp_coords](const Point& a, const Point& b) {
                return distance(a.coords, vp_coords) < distance(b.coords, vp_coords);
            });

        node->threshold = distance(rest[mid].coords, vp_coords);
        node->inside = build(rest.subspan(0, mid));
        node->outside = build(rest.subspan(mid));

        return node;
    }

    void search(const Node* node, std::span<const float> query, SearchResult& res) const {
        if (!node) return;

        float d = distance(query, node->vantage_point.coords);
        ++res.distance_evals;

        if (d < res.distance) {
            res.distance = d;
            res.point = node->vantage_point;
        }

        float tau = res.distance;

        if (d < node->threshold) {
            if (d - tau <= node->threshold) search(node->inside.get(), query, res);
            if (d + tau >= node->threshold) search(node->outside.get(), query, res);
        } else {
            if (d + tau >= node->threshold) search(node->outside.get(), query, res);
            if (d - tau <= node->threshold) search(node->inside.get(), query, res);
        }
    }
};
