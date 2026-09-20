#pragma once

#include "order_domain.hpp"

#include <algorithm>
#include <optional>
#include <unordered_map>
#include <vector>

/// @brief Автономний тестовий двійник (In-Memory Fake) для модульного тестування.
///
/// ПЕРЕВАГИ ДВІЙНИКА:
/// 1. Реалізує рольовий контракт IOrderFulfillmentPort у пам'яті за допомогою std::unordered_map.
/// 2. Забезпечує миттєве, ізольоване й детерміноване тестування бізнес-сценаріїв без СКБД.
/// 3. Усуває потребу у важких, крихких бібліотеках моків (Google Mock тощо) і складних ланцюжках
///    налаштування очікувань викликів.
/// 4. Повертає копії сутностей, що точно відтворює фізичну ізоляцію кордонів пам'яті
///    (як і реальне сховище).
class InMemoryOrderFulfillmentAdapter : public IOrderFulfillmentPort {
public:
    InMemoryOrderFulfillmentAdapter() = default;
    ~InMemoryOrderFulfillmentAdapter() override = default;

    // --- Реалізація чистого рольового порту ---

    [[nodiscard]] std::optional<Order> fetchNextPendingOrder() override {
        // Проходимо у порядку реєстрації замовлень для забезпечення черги FIFO
        for (const auto& id : insertion_order_) {
            auto it = orders_.find(id);
            if (it != orders_.end() && it->second.isPending()) {
                // Повертаємо копію, як це робило б зовнішнє сховище
                return it->second;
            }
        }
        return std::nullopt;
    }

    void save(const Order& order) override {
        // Зберігаємо змінений стан замовлення
        orders_.insert_or_assign(order.id(), order);
    }

    [[nodiscard]] std::optional<Order> findById(const OrderId& id) override {
        auto it = orders_.find(id);
        if (it != orders_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    // --- Допоміжні методи для швидкого наповнення та аудиту в тестах ---

    void addOrder(Order order) {
        OrderId id = order.id();
        orders_.insert_or_assign(id, std::move(order));
        insertion_order_.push_back(id);
    }

    [[nodiscard]] size_t countByStatus(OrderStatus status) const noexcept {
        size_t count = 0;
        for (const auto& [id, order] : orders_) {
            if (order.status() == status) {
                ++count;
            }
        }
        return count;
    }

    [[nodiscard]] size_t size() const noexcept {
        return orders_.size();
    }

    void clear() noexcept {
        orders_.clear();
        insertion_order_.clear();
    }

private:
    std::unordered_map<OrderId, Order, OrderId::Hash> orders_;
    std::vector<OrderId> insertion_order_;
};
