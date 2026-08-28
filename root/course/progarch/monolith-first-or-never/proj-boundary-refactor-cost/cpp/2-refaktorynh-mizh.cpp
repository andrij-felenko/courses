// C++20 — Мережева взаємодія та обробка відмов між мікросервісами
#include <iostream>
#include <string>
#include <vector>
#include <expected>
#include <chrono>
#include <thread>

namespace app::microservices {

enum class NetworkErrorCode {
    Timeout,
    ConnectionRefused,
    ServiceUnavailable,
    ParseError
};

struct DiscountResponse {
    double discount_amount;
    std::string applied_rule;
};

// Мережевий клієнт для виклику PricingService через gRPC/HTTP
class PricingServiceClient {
public:
    std::expected<DiscountResponse, NetworkErrorCode> fetch_remote_discount(
        const std::string& customer_id, double subtotal, const std::string& promo) const 
    {
        // Симуляція затримки мережевого транспорту (5 мілісекунд)
        std::this_thread::sleep_for(std::chrono::milliseconds(5));

        // Симуляція можливого мережевого збою у 5% випадків
        if (subtotal < 0) {
            return std::unexpected(NetworkErrorCode::ParseError);
        }

        double discount_rate = (subtotal >= 200.0) ? 0.15 : ((subtotal >= 100.0) ? 0.10 : 0.0);
        if (promo == "VIP_SUMMER") discount_rate += 0.05;

        return DiscountResponse{
            .discount_amount = subtotal * discount_rate,
            .applied_rule = "REMOTE_PRICING_V1"
        };
    }
};

class DistributedOrderService {
private:
    PricingServiceClient pricing_client_;

public:
    double process_order_checkout(const std::string& customer_id, double subtotal, const std::string& promo) const {
        // Мережева межа змушує писати захисний код відмов (Defensive Network Code)
        auto remote_result = pricing_client_.fetch_remote_discount(customer_id, subtotal, promo);

        double discount = 0.0;

        if (remote_result.has_value()) {
            discount = remote_result->discount_amount;
        } else {
            // Фолбек-стратегія (Fallback): у разі таймауту PricingService
            // застосовуємо безпечний локальний дефолт, щоб не зривати замовлення
            std::cerr << "WARN: PricingService недоступний. Застосовано аварійний фолбек (0% знижки)." << std::endl;
            discount = 0.0;
        }

        return subtotal - discount;
    }
};

} // namespace app::microservices

int main() {
    using namespace app::microservices;

    DistributedOrderService remote_order_service;

    auto start_time = std::chrono::high_resolution_clock::now();
    double final_price = remote_order_service.process_order_checkout("CUST-1092", 210.0, "VIP_SUMMER");
    auto end_time = std::chrono::high_resolution_clock::now();

    auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();

    std::cout << "=== МІКРОСЕРВІСНА АРХІТЕКТУРА ===" << std::endl;
    std::cout << "Підсумкова вартість: $" << final_price << std::endl;
    std::cout << "Час виконання із мережевим викликом: " << elapsed_ms << " мс" << std::endl;

    return 0;
}
