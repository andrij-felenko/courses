// C++20: Реалізація шва в моноліті (В пам'яті) vs Виділений сервіс (gRPC/Network)
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <expected>
#include <chrono>
#include <stdexcept>

struct DiscountRequest {
    std::string user_id;
    uint64_t amount_cents;
};

struct DiscountResponse {
    uint64_t discount_cents;
    std::string promo_code;
};

enum class ExtractionError {
    Timeout,
    NetworkFailure,
    CircuitOpen,
    InvalidData
};

// 1. ДО РОЗПИЛУ: Модуль у пам'яті моноліта (In-Memory Module)
class InProcessDiscountModule {
public:
    std::expected<DiscountResponse, ExtractionError> CalculateDiscount(const DiscountRequest& req) const {
        // Виконання у пам'яті: ~150 наносекунд. Нуль алокацій мережевих буферів.
        if (req.amount_cents == 0) {
            return std::unexpected(ExtractionError::InvalidData);
        }
        uint64_t discount = (req.amount_cents > 10000) ? (req.amount_cents * 10 / 100) : 0;
        return DiscountResponse{ .discount_cents = discount, .promo_code = "IN_PROC_10" };
    }
};

// 2. ПІСЛЯ РОЗПИЛУ: Виділений сервіс через мережевий клієнт із Circuit Breaker та таймаутом
class RemoteDiscountServiceClient {
private:
    std::string endpoint_;
    std::chrono::milliseconds timeout_;
    mutable bool circuit_open_ = false;

public:
    explicit RemoteDiscountServiceClient(std::string_view endpoint, std::chrono::milliseconds timeout)
        : endpoint_(endpoint), timeout_(timeout) {}

    std::expected<DiscountResponse, ExtractionError> CalculateDiscount(const DiscountRequest& req) const {
        // Захист від зливи викликів при падінні сервісу (Circuit Breaker)
        if (circuit_open_) {
            return std::unexpected(ExtractionError::CircuitOpen);
        }

        // Імітація мережевого RPC виклику (gRPC/HTTP2 over TLS)
        // Реальний потік: SerDe -> Socket Write -> RTT -> Processing -> Socket Read -> Deser
        try {
            // Мережевий таймаут та обробка помилок сокета
            bool network_ok = true; // Симуляція статусу мережі
            if (!network_ok) {
                circuit_open_ = true;
                return std::unexpected(ExtractionError::NetworkFailure);
            }

            // Накладні витрати мережі: ~8.5 мілісекунд (в 50 000 разів повільніше за in-memory)
            uint64_t discount = (req.amount_cents > 10000) ? (req.amount_cents * 10 / 100) : 0;
            return DiscountResponse{ .discount_cents = discount, .promo_code = "REMOTE_RPC_10" };
        } catch (...) {
            return std::unexpected(ExtractionError::Timeout);
        }
    }
};
