#pragma once

#include <cstddef>
#include <functional>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

/// @brief Доменний статус замовлення у процесі комплектації та виконання.
enum class OrderStatus {
    Pending,     ///< Замовлення зареєстроване й очікує комплектації
    Processing,  ///< Замовлення перебуває в процесі обробки та пакування
    Fulfilled,   ///< Комплектацію успішно завершено, замовлення відправлено
    Failed       ///< Помилка комплектації (порушення бізнес-правил або відсутність позицій)
};

/// @brief Перетворює статус замовлення на текстовий вигляд для діагностики.
[[nodiscard]] std::string_view orderStatusToString(OrderStatus status) noexcept;

/// @brief Строго типізований об'єкт-значення (Value Object) ідентифікатора замовлення.
/// Гарантує валідацію формату та унеможливлює підміну числових технічних ключів бази даних.
class OrderId {
public:
    /// @brief Конструює та валідує ідентифікатор замовлення.
    /// @throws std::invalid_argument якщо ідентифікатор порожній або не відповідає формату.
    explicit OrderId(std::string value);

    [[nodiscard]] const std::string& value() const noexcept { return value_; }

    [[nodiscard]] bool operator==(const OrderId& other) const noexcept {
        return value_ == other.value_;
    }

    [[nodiscard]] bool operator!=(const OrderId& other) const noexcept {
        return value_ != other.value_;
    }

    struct Hash {
        std::size_t operator()(const OrderId& id) const noexcept {
            return std::hash<std::string>{}(id.value());
        }
    };

private:
    std::string value_;
};

/// @brief Доменна сутність замовлення.
/// Інкапсулює бізнес-правила переходу між станами виконання та захищає власні інваріанти.
class Order {
public:
    Order(OrderId id,
          std::string customer_name,
          double total_amount,
          std::vector<std::string> line_items,
          OrderStatus status = OrderStatus::Pending);

    [[nodiscard]] const OrderId& id() const noexcept { return id_; }
    [[nodiscard]] const std::string& customerName() const noexcept { return customer_name_; }
    [[nodiscard]] double totalAmount() const noexcept { return total_amount_; }
    [[nodiscard]] OrderStatus status() const noexcept { return status_; }
    [[nodiscard]] const std::vector<std::string>& lineItems() const noexcept { return line_items_; }

    [[nodiscard]] bool isPending() const noexcept { return status_ == OrderStatus::Pending; }
    [[nodiscard]] bool isFulfilled() const noexcept { return status_ == OrderStatus::Fulfilled; }

    /// @brief Переводить замовлення в стан комплектації.
    /// @throws std::domain_error якщо перехід із поточного стану не дозволений.
    void startProcessing();

    /// @brief Успішно фіксує виконання комплектації.
    /// @throws std::domain_error якщо замовлення не було переведено в стан обробки.
    void completeFulfillment();

    /// @brief Фіксує відхилення комплектації замовлення через доменну причину.
    void markFailed(std::string_view reason);

private:
    OrderId id_;
    std::string customer_name_;
    double total_amount_{0.0};
    std::vector<std::string> line_items_;
    OrderStatus status_{OrderStatus::Pending};
};

/// @brief Чистий рольовий порт виконання замовлень (Role Port).
///
/// ЧИСТИЙ ДИЗАЙН:
/// 1. Сформульований суто в термінах потреб прикладного сценарію (Fulfillment Use Case).
/// 2. Відсутність доступного замовлення виражається ідіоматичним std::optional<Order>,
///    а не технічними кодами помилок на кшталт SQL_NOT_FOUND чи NULL-вказівниками.
/// 3. Повністю ізольований від СКБД: жодних понять таблиць, пагінації (limit/offset),
///    транзакцій, локів або реляційних колонок.
class IOrderFulfillmentPort {
public:
    virtual ~IOrderFulfillmentPort() = default;

    /// @brief Отримує наступне замовлення, готове до комплектації.
    /// @return std::optional з сутністю Order або std::nullopt, якщо нових замовлень немає.
    [[nodiscard]] virtual std::optional<Order> fetchNextPendingOrder() = 0;

    /// @brief Зберігає результат зміни стану замовлення.
    virtual void save(const Order& order) = 0;

    /// @brief Отримує замовлення за типізованим ідентифікатором (для аудиту та перевірки).
    [[nodiscard]] virtual std::optional<Order> findById(const OrderId& id) = 0;
};

/// @brief Прикладний сервіс виконання замовлень.
/// Реалізує сценарій комплектації замовлень, спираючись виключно на рольовий порт.
class OrderFulfillmentService {
public:
    explicit OrderFulfillmentService(IOrderFulfillmentPort& fulfillment_port);

    /// @brief Виконує комплектацію наступного доступного замовлення.
    /// @return OrderId обробленого замовлення або std::nullopt, якщо черга порожня.
    std::optional<OrderId> processNextOrder();

    /// @brief Виконує комплектацію всіх доступних замовлень до спустошення черги.
    /// @return Кількість успішно оброблених замовлень.
    size_t processAllPendingOrders();

private:
    IOrderFulfillmentPort& port_;
};

namespace std {
    template <>
    struct hash<OrderId> {
        size_t operator()(const OrderId& id) const noexcept {
            return hash<string>{}(id.value());
        }
    };
}
