#include "order_domain.hpp"

#include <stdexcept>
#include <utility>

std::string_view orderStatusToString(OrderStatus status) noexcept {
    switch (status) {
        case OrderStatus::Pending:
            return "Pending";
        case OrderStatus::Processing:
            return "Processing";
        case OrderStatus::Fulfilled:
            return "Fulfilled";
        case OrderStatus::Failed:
            return "Failed";
    }
    return "Unknown";
}

OrderId::OrderId(std::string value) : value_(std::move(value)) {
    if (value_.empty()) {
        throw std::invalid_argument("Ідентифікатор OrderId не може бути порожнім.");
    }
    // Перевіряємо префікс для гарантії семантичної коректності ідентифікатора
    if (value_.rfind("ORD-", 0) != 0) {
        throw std::invalid_argument(
            "Некоректний формат OrderId: \"" + value_ + "\". Очікується префікс \"ORD-\"."
        );
    }
}

Order::Order(OrderId id,
             std::string customer_name,
             double total_amount,
             std::vector<std::string> line_items,
             OrderStatus status)
    : id_(std::move(id)),
      customer_name_(std::move(customer_name)),
      total_amount_(total_amount),
      line_items_(std::move(line_items)),
      status_(status) {
    if (total_amount_ < 0.0) {
        throw std::invalid_argument("Загальна сума замовлення не може бути від'ємною.");
    }
}

void Order::startProcessing() {
    if (status_ != OrderStatus::Pending) {
        throw std::domain_error(
            "Неможливо почати комплектацію замовлення " + id_.value() +
            ": поточний статус не є Pending (" + std::string(orderStatusToString(status_)) + ")."
        );
    }
    status_ = OrderStatus::Processing;
}

void Order::completeFulfillment() {
    if (status_ != OrderStatus::Processing) {
        throw std::domain_error(
            "Неможливо завершити комплектацію замовлення " + id_.value() +
            ": замовлення повинно перебувати в статусі Processing."
        );
    }
    status_ = OrderStatus::Fulfilled;
}

void Order::markFailed(std::string_view reason) {
    status_ = OrderStatus::Failed;
    // Примітка: причина відхилення може логуватися або зберігатися в аудиті
    static_cast<void>(reason);
}

OrderFulfillmentService::OrderFulfillmentService(IOrderFulfillmentPort& fulfillment_port)
    : port_(fulfillment_port) {}

std::optional<OrderId> OrderFulfillmentService::processNextOrder() {
    // 1. Отримуємо наступне замовлення через абстрактний рольовий порт.
    // Ядро нічого не знає про розмір партій, SQL-запити, курсори чи таблиці.
    auto order_opt = port_.fetchNextPendingOrder();
    if (!order_opt.has_value()) {
        return std::nullopt; // Черга замовлень порожня
    }

    Order order = std::move(*order_opt);
    const OrderId current_id = order.id();

    // 2. Виконуємо бізнес-правила комплектації
    order.startProcessing();

    // Валідація бізнес-інваріанта: замовлення з ненульовою сумою повинно мати позиції
    if (order.lineItems().empty() && order.totalAmount() > 0.0) {
        order.markFailed("Відсутні товарні позиції для замовлення з ненульовою сумою.");
        port_.save(order);
        return current_id;
    }

    // Завершуємо комплектацію
    order.completeFulfillment();

    // 3. Зберігаємо сутність через рольовий контракт
    port_.save(order);

    return current_id;
}

size_t OrderFulfillmentService::processAllPendingOrders() {
    size_t processed_count = 0;
    while (processNextOrder().has_value()) {
        ++processed_count;
    }
    return processed_count;
}
