#include <iostream>
#include <vector>
#include <memory>
#include <queue>
#include <cmath>
#include <algorithm>
#include <optional>

constexpr size_t RTREE_MAX_ENTRIES = 4;
constexpr size_t RTREE_MIN_ENTRIES = 2;

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct Box2D {
    double min_x{0.0};
    double min_y{0.0};
    double max_x{0.0};
    double max_y{0.0};

    [[nodiscard]] double area() const noexcept {
        return (max_x - min_x) * (max_y - min_y);
    }

    [[nodiscard]] static Box2D combine(const Box2D& a, const Box2D& b) noexcept {
        return {
            std::min(a.min_x, b.min_x),
            std::min(a.min_y, b.min_y),
            std::max(a.max_x, b.max_x),
            std::max(a.max_y, b.max_y)
        };
    }

    [[nodiscard]] double enlargement(const Box2D& add) const noexcept {
        return combine(*this, add).area() - area();
    }

    [[nodiscard]] bool intersects(const Box2D& other) const noexcept {
        return (min_x <= other.max_x && max_x >= other.min_x &&
                min_y <= other.max_y && max_y >= other.min_y);
    }

    [[nodiscard]] double mindist_sq(const Point2D& p) const noexcept {
        double dx = 0.0, dy = 0.0;
        if (p.x < min_x) dx = min_x - p.x;
        else if (p.x > max_x) dx = p.x - max_x;
        if (p.y < min_y) dy = min_y - p.y;
        else if (p.y > max_y) dy = p.y - max_y;
        return dx * dx + dy * dy;
    }
};

struct RTreeNode;

struct RTreeEntry {
    Box2D box;
    std::unique_ptr<RTreeNode> child{nullptr};
    std::optional<long long> id{std::nullopt};
};

struct RTreeNode {
    bool is_leaf{true};
    std::vector<RTreeEntry> entries;

    [[nodiscard]] Box2D cover() const noexcept {
        if (entries.empty()) return {};
        Box2D res = entries.front().box;
        for (size_t i = 1; i < entries.size(); ++i) {
            res = Box2D::combine(res, entries[i].box);
        }
        return res;
    }
};

class RTree {
private:
    std::unique_ptr<RTreeNode> root_{nullptr};

    static std::unique_ptr<RTreeNode> split_node(RTreeNode& old_node) {
        std::vector<RTreeEntry> all = std::move(old_node.entries);
        const size_t total = all.size();

        /* 1. PickSeeds */
        size_t seed1 = 0, seed2 = 1;
        double max_dead_area = -1.0;

        for (size_t i = 0; i < total; ++i) {
            for (size_t j = i + 1; j < total; ++j) {
                Box2D combined = Box2D::combine(all[i].box, all[j].box);
                double dead = combined.area() - all[i].box.area() - all[j].box.area();
                if (dead > max_dead_area) {
                    max_dead_area = dead;
                    seed1 = i;
                    seed2 = j;
                }
            }
        }

        auto new_node = std::make_unique<RTreeNode>();
        new_node->is_leaf = old_node.is_leaf;

        std::vector<bool> taken(total, false);
        taken[seed1] = true;
        taken[seed2] = true;

        old_node.entries.push_back(std::move(all[seed1]));
        new_node->entries.push_back(std::move(all[seed2]));

        Box2D box1 = old_node.entries.front().box;
        Box2D box2 = new_node->entries.front().box;
        size_t assigned = 2;

        /* 2. Розподіл решти елементів */
        while (assigned < total) {
            if (old_node.entries.size() + (total - assigned) == RTREE_MIN_ENTRIES) {
                for (size_t i = 0; i < total; ++i) {
                    if (!taken[i]) {
                        old_node.entries.push_back(std::move(all[i]));
                        taken[i] = true;
                        ++assigned;
                    }
                }
                break;
            }
            if (new_node->entries.size() + (total - assigned) == RTREE_MIN_ENTRIES) {
                for (size_t i = 0; i < total; ++i) {
                    if (!taken[i]) {
                        new_node->entries.push_back(std::move(all[i]));
                        taken[i] = true;
                        ++assigned;
                    }
                }
                break;
            }

            /* PickNext */
            size_t best_idx = 0;
            double max_diff = -1.0;
            for (size_t i = 0; i < total; ++i) {
                if (taken[i]) continue;
                double d1 = box1.enlargement(all[i].box);
                double d2 = box2.enlargement(all[i].box);
                double diff = std::abs(d1 - d2);
                if (diff > max_diff) {
                    max_diff = diff;
                    best_idx = i;
                }
            }

            double d1 = box1.enlargement(all[best_idx].box);
            double d2 = box2.enlargement(all[best_idx].box);

            if (d1 < d2 || (d1 == d2 && box1.area() < box2.area()) ||
               (d1 == d2 && box1.area() == box2.area() && old_node.entries.size() <= new_node->entries.size())) {
                box1 = Box2D::combine(box1, all[best_idx].box);
                old_node.entries.push_back(std::move(all[best_idx]));
            } else {
                box2 = Box2D::combine(box2, all[best_idx].box);
                new_node->entries.push_back(std::move(all[best_idx]));
            }
            taken[best_idx] = true;
            ++assigned;
        }

        return new_node;
    }

    static std::unique_ptr<RTreeNode> insert_recursive(RTreeNode& node, RTreeEntry entry) {
        if (node.is_leaf) {
            node.entries.push_back(std::move(entry));
        } else {
            /* ChooseLeaf евристика */
            size_t best_idx = 0;
            double min_enl = node.entries[0].box.enlargement(entry.box);
            double min_area = node.entries[0].box.area();

            for (size_t i = 1; i < node.entries.size(); ++i) {
                double enl = node.entries[i].box.enlargement(entry.box);
                double a = node.entries[i].box.area();
                if (enl < min_enl || (enl == min_enl && a < min_area)) {
                    min_enl = enl;
                    min_area = a;
                    best_idx = i;
                }
            }

            auto split_child = insert_recursive(*node.entries[best_idx].child, std::move(entry));
            node.entries[best_idx].box = node.entries[best_idx].child->cover();

            if (split_child) {
                RTreeEntry new_entry;
                new_entry.box = split_child->cover();
                new_entry.child = std::move(split_child);
                node.entries.push_back(std::move(new_entry));
            }
        }

        if (node.entries.size() > RTREE_MAX_ENTRIES) {
            return split_node(node);
        }
        return nullptr;
    }

    static void search_recursive(const RTreeNode& node, const Box2D& query, std::vector<long long>& results) {
        for (const auto& entry : node.entries) {
            if (entry.box.intersects(query)) {
                if (node.is_leaf) {
                    if (entry.id.has_value()) {
                        results.push_back(*entry.id);
                    }
                } else if (entry.child) {
                    search_recursive(*entry.child, query, results);
                }
            }
        }
    }

public:
    RTree() = default;

    void insert(Box2D box, long long id) {
        RTreeEntry entry{box, nullptr, id};

        if (!root_) {
            root_ = std::make_unique<RTreeNode>();
            root_->is_leaf = true;
            root_->entries.push_back(std::move(entry));
            return;
        }

        auto split_root = insert_recursive(*root_, std::move(entry));
        if (split_root) {
            auto new_root = std::make_unique<RTreeNode>();
            new_root->is_leaf = false;

            RTreeEntry e1{root_->cover(), std::move(root_), std::nullopt};
            RTreeEntry e2{split_root->cover(), std::move(split_root), std::nullopt};

            new_root->entries.push_back(std::move(e1));
            new_root->entries.push_back(std::move(e2));
            root_ = std::move(new_root);
        }
    }

    [[nodiscard]] std::vector<long long> search_range(const Box2D& query) const {
        std::vector<long long> results;
        if (root_) {
            search_recursive(*root_, query, results);
        }
        return results;
    }

    struct QueueItem {
        double dist_sq{0.0};
        const RTreeNode* node{nullptr};
        std::optional<long long> id{std::nullopt};

        bool operator>(const QueueItem& other) const noexcept {
            return dist_sq > other.dist_sq;
        }
    };

    [[nodiscard]] std::vector<long long> search_knn(const Point2D& query_point, size_t k) const {
        std::vector<long long> neighbors;
        if (!root_ || k == 0) return neighbors;

        std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<QueueItem>> pq;
        pq.push({root_->cover().mindist_sq(query_point), root_.get(), std::nullopt});

        while (!pq.empty() && neighbors.size() < k) {
            auto current = pq.top();
            pq.pop();

            if (current.id.has_value()) {
                neighbors.push_back(*current.id);
            } else if (current.node) {
                for (const auto& entry : current.node->entries) {
                    double d_sq = entry.box.mindist_sq(query_point);
                    if (current.node->is_leaf) {
                        pq.push({d_sq, nullptr, entry.id});
                    } else if (entry.child) {
                        pq.push({d_sq, entry.child.get(), std::nullopt});
                    }
                }
            }
        }
        return neighbors;
    }
};

int main() {
    RTree tree;

    /* Вставка тестових об'єктів */
    tree.insert({10, 10, 20, 20}, 101);
    tree.insert({15, 12, 25, 22}, 102);
    tree.insert({50, 60, 70, 80}, 103);
    tree.insert({55, 62, 75, 85}, 104);
    tree.insert({12, 14, 22, 24}, 105);
    tree.insert({80, 80, 90, 90}, 106);

    std::cout << "=== Віконний пошук у зоні [5, 5]x[30, 30] ===\n";
    auto in_range = tree.search_range({5, 5, 30, 30});
    for (auto id : in_range) {
        std::cout << "Знайдено об'єкт id: " << id << "\n";
    }

    std::cout << "\n=== Пошук 3 найближчих сусідів до точки (14, 14) ===\n";
    auto nearest = tree.search_knn({14.0, 14.0}, 3);
    for (size_t i = 0; i < nearest.size(); ++i) {
        std::cout << (i + 1) << "-й найближчий id: " << nearest[i] << "\n";
    }

    return 0;
}
