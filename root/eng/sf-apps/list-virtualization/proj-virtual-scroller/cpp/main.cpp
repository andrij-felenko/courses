// C++20: Високопродуктивне ядро віртуалізації з деревом Фенвіка та пулом подань

#include <vector>
#include <memory>
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <span>

class FenwickTree {
private:
    std::vector<int64_t> tree;
    size_t n;

    static constexpr size_t lsb(size_t i) noexcept {
        return i & (-i);
    }

public:
    explicit FenwickTree(size_t size) : tree(size + 1, 0), n(size) {}

    void add(size_t idx, int64_t delta) noexcept {
        for (size_t i = idx + 1; i <= n; i += lsb(i)) {
            tree[i] += delta;
        }
    }

    [[nodiscard]] int64_t query(size_t idx) const noexcept {
        int64_t sum = 0;
        for (size_t i = idx + 1; i > 0; i -= lsb(i)) {
            sum += tree[i];
        }
        return sum;
    }

    // Двійковий підйом за O(log N) для пошуку першого індексу, де prefix_sum > target
    [[nodiscard]] size_t find_first_greater(int64_t target) const noexcept {
        size_t idx = 0;
        int64_t current_sum = 0;
        size_t max_bit = 1;
        while ((max_bit << 1) <= n) {
            max_bit <<= 1;
        }

        for (size_t step = max_bit; step > 0; step >>= 1) {
            if (idx + step <= n && current_sum + tree[idx + step] <= target) {
                idx += step;
                current_sum += tree[idx];
            }
        }
        return idx; // 0-based index
    }
};

struct ViewHolder {
    size_t bound_index{static_cast<size_t>(-1)};
    int64_t rendered_offset{0};
    int64_t rendered_height{0};
    bool is_active{false};
    std::string text_buffer;
};

class HeadlessVirtualizer {
private:
    size_t item_count;
    int64_t default_estimated_height;
    size_t overscan;

    FenwickTree fenwick;
    std::vector<int64_t> item_heights;
    std::vector<ViewHolder> view_pool;
    std::unordered_map<size_t, size_t> active_view_map; // index -> pool_slot

public:
    HeadlessVirtualizer(size_t count, int64_t estimate_height, size_t pool_capacity, size_t overscan_items = 3)
        : item_count(count),
          default_estimated_height(estimate_height),
          overscan(overscan_items),
          fenwick(count),
          item_heights(count, estimate_height),
          view_pool(pool_capacity) {
        // Лінійна ініціалізація дерева Фенвіка
        for (size_t i = 0; i < count; ++i) {
            fenwick.add(i, estimate_height);
        }
    }

    struct Range {
        size_t start_index;
        size_t end_index;
        int64_t start_offset;
    };

    [[nodiscard]] Range calculate_visible_range(int64_t scroll_top, int64_t viewport_height) const noexcept {
        if (item_count == 0) return {0, 0, 0};

        size_t first_visible = fenwick.find_first_greater(scroll_top);
        if (first_visible >= item_count) first_visible = item_count - 1;

        int64_t bottom_boundary = scroll_top + viewport_height;
        size_t last_visible = fenwick.find_first_greater(bottom_boundary);
        if (last_visible >= item_count) last_visible = item_count - 1;

        size_t start = (first_visible > overscan) ? (first_visible - overscan) : 0;
        size_t end = std::min(item_count - 1, last_visible + overscan);

        int64_t start_offset = (start == 0) ? 0 : fenwick.query(start - 1);
        return {start, end, start_offset};
    }

    // Оновлення реального розміру після вимірювання
    struct AnchorAdjustment {
        int64_t scroll_delta;
        int64_t new_total_height;
    };

    AnchorAdjustment update_measured_size(size_t index, int64_t measured_height, int64_t current_scroll_top) {
        if (index >= item_count) return {0, fenwick.query(item_count - 1)};

        int64_t old_height = item_heights[index];
        int64_t delta = measured_height - old_height;

        if (delta == 0) return {0, fenwick.query(item_count - 1)};

        // Фіксуємо якір для компенсації скрол-стрибків
        size_t anchor_index = fenwick.find_first_greater(current_scroll_top);
        int64_t old_anchor_offset = (anchor_index == 0) ? 0 : fenwick.query(anchor_index - 1);

        // Застосовуємо дельту в дерево
        item_heights[index] = measured_height;
        fenwick.add(index, delta);

        int64_t new_anchor_offset = (anchor_index == 0) ? 0 : fenwick.query(anchor_index - 1);
        int64_t scroll_delta = 0;

        // Якщо елемент змінився вище або на рівні якоря — коригуємо скрол
        if (index <= anchor_index) {
            scroll_delta = new_anchor_offset - old_anchor_offset;
        }

        int64_t total_height = fenwick.query(item_count - 1);
        return {scroll_delta, total_height};
    }

    // Ресайклінг пулу подань під новий видимий діапазон
    void recycle_and_bind(size_t start_index, size_t end_index) {
        std::vector<size_t> freed_slots;

        // 1. Позначаємо слоти поза діапазоном як вільні
        for (auto it = active_view_map.begin(); it != active_view_map.end();) {
            if (it->first < start_index || it->first > end_index) {
                size_t slot = it->second;
                view_pool[slot].is_active = false;
                freed_slots.push_back(slot);
                it = active_view_map.erase(it);
            } else {
                ++it;
            }
        }

        // 2. Прив'язуємо нові індекси з вільного пулу
        size_t free_idx = 0;
        for (size_t i = start_index; i <= end_index; ++i) {
            if (!active_view_map.contains(i)) {
                size_t target_slot;
                if (free_idx < freed_slots.size()) {
                    target_slot = freed_slots[free_idx++];
                } else {
                    // Шукаємо перший неактивний слот
                    auto inactive_it = std::find_if(view_pool.begin(), view_pool.end(),
                                                    [](const ViewHolder& v) { return !v.is_active; });
                    if (inactive_it == view_pool.end()) break; // Пул вичерпано
                    target_slot = std::distance(view_pool.begin(), inactive_it);
                }

                ViewHolder& vh = view_pool[target_slot];
                vh.bound_index = i;
                vh.rendered_offset = (i == 0) ? 0 : fenwick.query(i - 1);
                vh.rendered_height = item_heights[i];
                vh.is_active = true;
                vh.text_buffer = "Рядок #" + std::to_string(i);

                active_view_map[i] = target_slot;
            }
        }
    }

    [[nodiscard]] std::span<const ViewHolder> get_pool() const noexcept {
        return view_pool;
    }
};
