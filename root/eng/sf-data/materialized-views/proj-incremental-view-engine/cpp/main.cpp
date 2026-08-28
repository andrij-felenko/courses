#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <mutex>
#include <shared_mutex>
#include <optional>
#include <cstdint>

// Базові структури реляційних кортежів
struct Order {
    uint64_t order_id;
    uint64_t customer_id;
    bool is_paid;
};

struct OrderItem {
    uint64_t item_id;
    uint64_t order_id;
    uint32_t category_id;
    uint32_t quantity;
    double price;
};

// Збережений агрегований стан матеріалізованого рядка
struct MaterializedCategoryStats {
    uint32_t category_id;
    double total_revenue = 0.0;
    int64_t item_count = 0; // Лічильник кратності для коректного DELETE
};

class IncrementalViewEngine {
private:
    // Базові сховища даних з індексами
    std::unordered_map<uint64_t, Order> orders_;
    std::unordered_map<uint64_t, OrderItem> items_;
    std::unordered_multimap<uint64_t, uint64_t> order_to_items_idx_; // order_id -> item_id

    // Матеріалізований стан (групування за category_id)
    std::unordered_map<uint32_t, MaterializedCategoryStats> mat_view_;

    mutable std::shared_mutex rw_lock_;

    // Внутрішній метод диференційного оновлення стану матеріалізованого в'ю
    void apply_delta(uint32_t category_id, double delta_revenue, int64_t delta_count) {
        auto it = mat_view_.find(category_id);
        if (it == mat_view_.end()) {
            if (delta_count > 0) {
                mat_view_[category_id] = {category_id, delta_revenue, delta_count};
            }
            return;
        }

        it->second.total_revenue += delta_revenue;
        it->second.item_count += delta_count;

        // Якщо всі входження категорії видалені — прибираємо рядок зі стану
        if (it->second.item_count <= 0) {
            mat_view_.erase(it);
        }
    }

public:
    // Вставка або оновлення замовлення
    void upsert_order(const Order& new_order) {
        std::unique_lock lock(rw_lock_);
        
        bool old_paid = false;
        bool had_old = false;

        auto it = orders_.find(new_order.order_id);
        if (it != orders_.end()) {
            had_old = true;
            old_paid = it->second.is_paid;
            it->second = new_order;
        } else {
            orders_[new_order.order_id] = new_order;
        }

        // Якщо статус оплати не змінився, диференційне з'єднання не змінює MV
        if (had_old && old_paid == new_order.is_paid) {
            return;
        }

        // Зміна предиката: замовлення оплатили (+1) або скасували оплату (-1)
        int64_t sign = (new_order.is_paid ? 1 : 0) - (old_paid ? 1 : 0);
        if (sign == 0) return;

        // Поширюємо дельту на всі прив'язані позиції товарів
        auto [range_begin, range_end] = order_to_items_idx_.equal_range(new_order.order_id);
        for (auto item_it = range_begin; item_it != range_end; ++item_it) {
            const auto& item = items_[item_it->second];
            double rev = item.quantity * item.price * sign;
            apply_delta(item.category_id, rev, sign);
        }
    }

    // Додавання позиції товару до замовлення
    void insert_order_item(const OrderItem& item) {
        std::unique_lock lock(rw_lock_);

        items_[item.item_id] = item;
        order_to_items_idx_.emplace(item.order_id, item.item_id);

        // Перевіряємо, чи оплачене відповідне замовлення
        auto order_it = orders_.find(item.order_id);
        if (order_it != orders_.end() && order_it->second.is_paid) {
            double rev = item.quantity * item.price;
            apply_delta(item.category_id, rev, 1);
        }
    }

    // Видалення позиції товару
    void delete_order_item(uint64_t item_id) {
        std::unique_lock lock(rw_lock_);

        auto it = items_.find(item_id);
        if (it == items_.end()) return;

        const OrderItem item = it->second;
        items_.erase(it);

        // Видалення з індексу
        auto [begin, end] = order_to_items_idx_.equal_range(item.order_id);
        for (auto cur = begin; cur != end; ++cur) {
            if (cur->second == item_id) {
                order_to_items_idx_.erase(cur);
                break;
            }
        }

        auto order_it = orders_.find(item.order_id);
        if (order_it != orders_.end() && order_it->second.is_paid) {
            double rev = -(item.quantity * item.price);
            apply_delta(item.category_id, rev, -1);
        }
    }

    // Миттєве читання матеріалізованого агрегату за O(1)
    std::optional<MaterializedCategoryStats> get_category_stats(uint32_t category_id) const {
        std::shared_lock lock(rw_lock_);
        auto it = mat_view_.find(category_id);
        if (it != mat_view_.end()) {
            return it->second;
        }
        return std::nullopt;
    }
};

int main() {
    IncrementalViewEngine engine;

    // Створюємо неоплачене замовлення #1
    engine.upsert_order({1, 1001, false});

    // Додаємо дві позиції товарів у категорію #42
    engine.insert_order_item({101, 1, 42, 2, 50.0});  // 100.0 грн
    engine.insert_order_item({102, 1, 42, 1, 150.0}); // 150.0 грн

    // Оскільки замовлення не оплачене, матеріалізоване в'ю порожнє
    auto stats = engine.get_category_stats(42);
    std::cout << "До оплати: категорія 42 існує? " << (stats.has_value() ? "Так" : "Ні") << "\n";

    // Оплачуємо замовлення #1 — спрацьовує диференційне оновлення IVM
    engine.upsert_order({1, 1001, true});

    stats = engine.get_category_stats(42);
    if (stats) {
        std::cout << "Після оплати:\n";
        std::cout << "  - Дохід (Revenue): " << stats->total_revenue << " грн\n";
        std::cout << "  - Кількість товарів (Count): " << stats->item_count << "\n";
    }

    // Видаляємо одну позицію
    engine.delete_order_item(101);

    stats = engine.get_category_stats(42);
    if (stats) {
        std::cout << "Після видалення позиції 101:\n";
        std::cout << "  - Новий дохід: " << stats->total_revenue << " грн\n";
        std::cout << "  - Нова кількість: " << stats->item_count << "\n";
    }

    return 0;
}
