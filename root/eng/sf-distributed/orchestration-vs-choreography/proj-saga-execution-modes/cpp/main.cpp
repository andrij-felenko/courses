#include <iostream>
#include <string>
#include <vector>
#include <functional>
#include <memory>
#include <expected>
#include <format>

struct OrderContext {
    std::string order_id;
    double amount{0.0};
    bool simulate_delivery_failure{false};
};

enum class StepError {
    InventoryOutOfStock,
    PaymentDeclined,
    DeliveryUnavailable,
    InternalTimeout
};

struct StepResult {
    bool success;
    std::string message;
};

/* Опис кроку саги */
struct SagaStep {
    std::string name;
    std::function<std::expected<StepResult, StepError>(OrderContext&)> forward;
    std::function<void(OrderContext&)> compensate;
};

class SagaOrchestrator {
public:
    void add_step(std::string name,
                  std::function<std::expected<StepResult, StepError>(OrderContext&)> forward,
                  std::function<void(OrderContext&)> compensate) {
        steps_.push_back(SagaStep{
            .name = std::move(name),
            .forward = std::move(forward),
            .compensate = std::move(compensate)
        });
    }

    std::expected<void, StepError> execute(OrderContext& ctx) {
        std::cout << std::format("\n=== ЗАПУСК C++ ОРКЕСТРАТОРА САГИ: {} ===\n", ctx.order_id);
        std::vector<std::function<void(OrderContext&)>> rollback_stack;

        for (size_t i = 0; i < steps_.size(); ++i) {
            const auto& step = steps_[i];
            std::cout << std::format("-> Оркестратор виконує крок {}: {}\n", i + 1, step.name);

            auto outcome = step.forward(ctx);
            if (outcome.has_value()) {
                if (step.compensate) {
                    rollback_stack.push_back(step.compensate);
                }
            } else {
                std::cout << std::format("\n[!] Збій на етапі {}. Початок LIFO розмотування компенсацій.\n", step.name);
                for (auto it = rollback_stack.rbegin(); it != rollback_stack.rend(); ++it) {
                    (*it)(ctx);
                }
                std::cout << "=== САГУ СКАСОВАНО ТА СТАБІЛІЗОВАНО ===\n";
                return std::unexpected(outcome.error());
            }
        }

        std::cout << "=== САГУ УСПІШНО ЗАВЕРШЕНО ===\n";
        return {};
    }

private:
    std::vector<SagaStep> steps_;
};

int main() {
    OrderContext ctx{
        .order_id = "ORD-CPP-2026",
        .amount = 45000.0,
        .simulate_delivery_failure = true
    };

    SagaOrchestrator orchestrator;

    orchestrator.add_step(
        "ReserveInventory",
        [](OrderContext& c) -> std::expected<StepResult, StepError> {
            std::cout << std::format("[Склад] Резервування для {}... [OK]\n", c.order_id);
            return StepResult{true, "Reserved"};
        },
        [](OrderContext& c) {
            std::cout << std::format("[Склад] КОМПЕНСАЦІЯ: Зняття резерву для {}.\n", c.order_id);
        }
    );

    orchestrator.add_step(
        "ChargePayment",
        [](OrderContext& c) -> std::expected<StepResult, StepError> {
            std::cout << std::format("[Оплата] Списання {:.2f} грн для {}... [OK]\n", c.amount, c.order_id);
            return StepResult{true, "Captured"};
        },
        [](OrderContext& c) {
            std::cout << std::format("[Оплата] КОМПЕНСАЦІЯ: Повернення {:.2f} грн для {}.\n", c.amount, c.order_id);
        }
    );

    orchestrator.add_step(
        "BookDelivery",
        [](OrderContext& c) -> std::expected<StepResult, StepError> {
            std::cout << std::format("[Доставка] Перевірка кур'єрів для {}...\n", c.order_id);
            if (c.simulate_delivery_failure) {
                std::cout << "[Доставка] ПОМИЛКА: Немає вільних авто (HTTP 503).\n";
                return std::unexpected(StepError::DeliveryUnavailable);
            }
            return StepResult{true, "Booked"};
        },
        [](OrderContext& c) {
            std::cout << std::format("[Доставка] КОМПЕНСАЦІЯ: Скасування кур'єра для {}.\n", c.order_id);
        }
    );

    auto res = orchestrator.execute(ctx);
    if (!res.has_value()) {
        std::cout << "Результат: Процес завершився з помилкою та повним відкатом.\n";
    }
    return 0;
}
