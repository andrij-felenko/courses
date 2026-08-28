#include <iostream>
#include <string>
#include <vector>
#include <functional>
#include <expected>
#include <format>

struct OrderCtx {
    std::string order_id;
    double price{0.0};
    bool force_logistics_error{false};
};

enum class WorkflowError {
    InventoryUnavailable,
    PaymentFailed,
    LogisticsUnavailable
};

struct StepDef {
    std::string title;
    std::function<std::expected<void, WorkflowError>(OrderCtx&)> forward;
    std::function<void(OrderCtx&)> compensate;
};

class SagaOrchestrator {
public:
    void register_step(StepDef step) {
        steps_.push_back(std::move(step));
    }

    std::expected<void, WorkflowError> execute(OrderCtx& ctx) {
        std::cout << std::format("=== СТАРТ C++ ОРКЕСТРАЦІЇ: {} ===\n", ctx.order_id);
        std::vector<std::function<void(OrderCtx&)>> rollbacks;

        for (const auto& step : steps_) {
            std::cout << std::format("-> Виконання кроку: {}\n", step.title);
            auto res = step.forward(ctx);
            if (res.has_value()) {
                if (step.compensate) {
                    rollbacks.push_back(step.compensate);
                }
            } else {
                std::cout << std::format("\n[!] Збій на етапі {}. Запуск LIFO компенсацій:\n", step.title);
                for (auto it = rollbacks.rbegin(); it != rollbacks.rend(); ++it) {
                    (*it)(ctx);
                }
                std::cout << "=== ПРОЦЕС СКАСОВАНО ТА СТАБІЛІЗОВАНО ===\n";
                return std::unexpected(res.error());
            }
        }

        std::cout << "=== ВСІ КРОКИ УСПІШНО ЗАВЕРШЕНО ===\n";
        return {};
    }

private:
    std::vector<StepDef> steps_;
};
