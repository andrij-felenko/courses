#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <future>
#include <chrono>
#include <functional>
#include <expected>

using namespace std::chrono_literals;

struct OrderRequest {
    std::string order_id;
    std::string user_id;
    int64_t amount_cents;
};

struct OrderResponse {
    std::string order_id;
    std::string status;
    int64_t balance_after;
};

enum class ExecutionError {
    Timeout,
    InternalFault,
    InvalidPayload
};

// Інтерфейс платіжного ядра
class OrderProcessor {
public:
    virtual ~OrderProcessor() = default;
    virtual std::expected<OrderResponse, ExecutionError> process(const OrderRequest& req) = 0;
};

// Диспетчер паралельного прогону (Parallel Run Dispatcher)
class DualRunDispatcher : public OrderProcessor {
private:
    std::shared_ptr<OrderProcessor> master_;    // Стара система (авторитетна)
    std::shared_ptr<OrderProcessor> candidate_; // Нова система (у тіні)
    std::function<void(const std::string&, const OrderResponse&, const OrderResponse&)> on_diff_;
    std::chrono::milliseconds shadow_timeout_;

public:
    DualRunDispatcher(
        std::shared_ptr<OrderProcessor> master,
        std::shared_ptr<OrderProcessor> candidate,
        std::function<void(const std::string&, const OrderResponse&, const OrderResponse&)> on_diff,
        std::chrono::milliseconds shadow_timeout = 200ms)
        : master_(std::move(master))
        , candidate_(std::move(candidate))
        , on_diff_(std::move(on_diff))
        , shadow_timeout_(shadow_timeout) {}

    std::expected<OrderResponse, ExecutionError> process(const OrderRequest& req) override {
        // 1. Асинхронний запуск кандидата у фоновому пулі
        auto shadow_future = std::async(std::launch::async, [this, req]() {
            return candidate_->process(req);
        });

        // 2. Синхронне авторитетне виконання на Legacy
        auto master_res = master_->process(req);
        if (!master_res) {
            return master_res; // Помилка майстра повертається негайно
        }

        // 3. Отримання результату кандидата з жорстким таймаутом
        // Кандидат НЕ має права затримувати відповідь клієнтові
        if (shadow_future.wait_for(shadow_timeout_) == std::future_status::ready) {
            auto candidate_res = shadow_future.get();
            if (candidate_res) {
                // Звіряємо результати обох гілок
                if (master_res->balance_after != candidate_res->balance_after ||
                    master_res->status != candidate_res->status) {
                    on_diff_(req.order_id, *master_res, *candidate_res);
                }
            }
        }

        // Завжди повертаємо результат авторитетного майстра
        return master_res;
    }
};
