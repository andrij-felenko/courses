// C++20 — Внутрішньопроцесорний рефакторинг у Модульному моноліті
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <optional>
#include <chrono>

namespace app::domain {

// Сутності предметної області в єдиній пам'яті
struct OrderItem {
    std::string item_id;
    double unit_price;
    int quantity;
};

struct OrderContext {
    std::string order_id;
    std::string customer_id;
    std::vector<OrderItem> items;
    std::string promo_code;
};

// Модуль Order після рефакторингу: містить автономну логіку обчислення підсумку
class OrderModule {
public:
    double calculate_order_total(const OrderContext& ctx) const {
        // Step 1: Обчислення базової вартості кошика
        double subtotal = 0.0;
        for (const auto& item : ctx.items) {
            subtotal += item.unit_price * item.quantity;
        }

        // Step 2: Локальний виклик перенесеного методу розрахунку знижки (150 нс)
        double discount = calculate_bulk_discount(ctx.customer_id, subtotal, ctx.promo_code);

        // Step 3: Фінальний підсумок без жодних мережевих накладних витрат
        return subtotal - discount;
    }

private:
    // Перенесена бізнес-логіка з модуля Pricing у модуль Order
    double calculate_bulk_discount(const std::string& customer_id, double subtotal, const std::string& promo) const {
        double discount_rate = 0.0;

        // Перевірка об'ємної знижки
        if (subtotal >= 200.0) {
            discount_rate += 0.15; // 15% за велике замовлення
        } else if (subtotal >= 100.0) {
            discount_rate += 0.10; // 10% за середнє замовлення
        }

        // Врахування спеціального промокоду у тому самому контексті
        if (promo == "VIP_SUMMER") {
            discount_rate += 0.05;
        }

        return subtotal * discount_rate;
    }
};

} // namespace app::domain

int main() {
    using namespace app::domain;

    OrderModule order_processor;
    OrderContext context{
        .order_id = "ORD-2026-8891",
        .customer_id = "CUST-1092",
        .items = {
            {"LAPTOP-STAND", 45.0, 2},
            {"MECHANICAL-KEYBOARD", 120.0, 1}
        },
        .promo_code = "VIP_SUMMER"
    };

    auto start_time = std::chrono::high_resolution_clock::now();
    double final_price = order_processor.calculate_order_total(context);
    auto end_time = std::chrono::high_resolution_clock::now();

    auto elapsed_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time).count();

    std::cout << "=== МОДУЛЬНИЙ МОНОЛІТ ===" << std::endl;
    std::cout << "Підсумкова вартість: $" << final_price << std::endl;
    std::cout << "Час виконання обчислення у пам'яті: " << elapsed_ns << " нс" << std::endl;

    return 0;
}
