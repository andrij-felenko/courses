#include <iostream>
#include <memory>
#include <vector>
#include <optional>
#include <algorithm>

namespace geo {

// Ідіоматична структура 1D-інтервалу
struct Interval {
    double low;
    double high;

    [[nodiscard]] constexpr bool overlaps(const Interval& other) const noexcept {
        return (low <= other.high) && (high >= other.low);
    }
};

// Вузол доповненого інтервального дерева з автоматичним керуванням пам'яттю (RAII)
class IntervalNode {
public:
    Interval interval;
    double max_high;
    std::unique_ptr<IntervalNode> left;
    std::unique_ptr<IntervalNode> right;

    explicit IntervalNode(Interval it) noexcept
        : interval(it), max_high(it.high), left(nullptr), right(nullptr) {}

    // Оновлення атрибута max_high на основі дітей
    void update_max() noexcept {
        double cur_max = interval.high;
        if (left) {
            cur_max = std::max(cur_max, left->max_high);
        }
        if (right) {
            cur_max = std::max(cur_max, right->max_high);
        }
        max_high = cur_max;
    }
};

// Клас-обгортка інтервального дерева
class IntervalTree {
private:
    std::unique_ptr<IntervalNode> root_;

    // Внутрішня рекурсивна вставка
    static std::unique_ptr<IntervalNode> insert_rec(std::unique_ptr<IntervalNode> node, Interval it) {
        if (!node) {
            return std::make_unique<IntervalNode>(it);
        }

        if (it.low < node->interval.low) {
            node->left = insert_rec(std::move(node->left), it);
        } else {
            node->right = insert_rec(std::move(node->right), it);
        }

        node->update_max();
        return node;
    }

    // Внутрішній рекурсивний пошук усіх збігів
    static void search_all_rec(const IntervalNode* node, const Interval& query, std::vector<Interval>& result) {
        if (!node) return;

        if (node->interval.overlaps(query)) {
            result.push_back(node->interval);
        }

        if (node->left && node->left->max_high >= query.low) {
            search_all_rec(node->left.get(), query, result);
        }

        if (node->right && node->interval.low <= query.high && node->right->max_high >= query.low) {
            search_all_rec(node->right.get(), query, result);
        }
    }

public:
    IntervalTree() noexcept = default;

    // Публічна операція вставки
    void insert(Interval it) {
        root_ = insert_rec(std::move(root_), it);
    }

    // Одиничний пошук перетину (повертає std::optional)
    [[nodiscard]] std::optional<Interval> find_any_overlap(const Interval& query) const noexcept {
        const IntervalNode* curr = root_.get();
        while (curr != nullptr && !curr->interval.overlaps(query)) {
            if (curr->left && curr->left->max_high >= query.low) {
                curr = curr->left.get();
            } else {
                curr = curr->right.get();
            }
        }

        if (curr) {
            return curr->interval;
        }
        return std::nullopt;
    }

    // Пошук усіх перетинів з поверненням векторів
    [[nodiscard]] std::vector<Interval> find_all_overlaps(const Interval& query) const {
        std::vector<Interval> results;
        search_all_rec(root_.get(), query, results);
        return results;
    }

    [[nodiscard]] double get_root_max() const noexcept {
        return root_ ? root_->max_high : 0.0;
    }
};

} // namespace geo

int main() {
    geo::IntervalTree tree;

    const std::vector<geo::Interval> input_intervals = {
        {15.0, 20.0},
        {10.0, 30.0},
        {17.0, 19.0},
        {5.0, 20.0},
        {12.0, 15.0},
        {30.0, 40.0}
    };

    std::cout << "=== Побудова інтервального дерева (C++20) ===\n";
    for (const auto& it : input_intervals) {
        tree.insert(it);
        std::cout << "Вставлено інтервал: [" << it.low << ", " << it.high << "]\n";
    }

    std::cout << "\nМаксимальний корінь max_high: " << tree.get_root_max() << "\n";

    // 1. Одиничний пошук перетину Q1 = [21, 23]
    geo::Interval q1{21.0, 23.0};
    std::cout << "\nПошук одиничного перетину для Q1 = [" << q1.low << ", " << q1.high << "]:\n";
    if (auto match = tree.find_any_overlap(q1); match.has_value()) {
        std::cout << "Знайдено збіг: [" << match->low << ", " << match->high << "]\n";
    } else {
        std::cout << "Збігів не знайдено.\n";
    }

    // 2. Пошук усіх перетинів Q2 = [14, 18]
    geo::Interval q2{14.0, 18.0};
    std::cout << "\nПошук усіх перетинів для Q2 = [" << q2.low << ", " << q2.high << "]:\n";
    auto matches = tree.find_all_overlaps(q2);

    std::cout << "Знайдено " << matches.size() << " перетинів:\n";
    for (const auto& m : matches) {
        std::cout << " - [" << m.low << ", " << m.high << "]\n";
    }

    return 0;
}
