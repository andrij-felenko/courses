#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <optional>
#include <chrono>
#include <thread>
#include <sstream>

enum class StepKind {
    Compensable,
    Pivot,
    Retryable
};

enum class StepState {
    NotStarted,
    Executing,
    Completed,
    Failed,
    Compensating,
    Compensated
};

struct StepContext {
    std::string saga_id;
    std::string payload;
    bool simulate_failure = false;
};

// Інтерфейс стійкого журналу виконання саги (Saga Execution Coordinator Log)
class ISagaLog {
public:
    virtual ~ISagaLog() = default;
    virtual void log_state(const std::string& saga_id, size_t step_idx, const std::string& step_name, StepState state) = 0;
};

class ConsoleSagaLog : public ISagaLog {
public:
    void log_state(const std::string& saga_id, size_t step_idx, const std::string& step_name, StepState state) override {
        const char* state_str = "UNKNOWN";
        switch (state) {
            case StepState::Executing:    state_str = "EXECUTING"; break;
            case StepState::Completed:    state_str = "COMPLETED"; break;
            case StepState::Failed:       state_str = "FAILED"; break;
            case StepState::Compensating: state_str = "COMPENSATING"; break;
            case StepState::Compensated:  state_str = "COMPENSATED"; break;
            default: break;
        }
        std::cout << " [SEC-LOG] Saga=" << saga_id << " Step[" << step_idx << "]=" 
                  << step_name << " -> State=" << state_str << "\n";
    }
};

// Визначення окремого кроку саги
class SagaStep {
public:
    std::string name;
    StepKind kind;
    std::function<bool(StepContext&)> action;
    std::function<bool(StepContext&)> compensate;

    SagaStep(std::string n, StepKind k,
             std::function<bool(StepContext&)> act,
             std::function<bool(StepContext&)> comp = nullptr)
        : name(std::move(n)), kind(k), action(std::move(act)), compensate(std::move(comp)) {}
};

// Оркестратор саги
class SagaOrchestrator {
private:
    std::string saga_id_;
    std::vector<SagaStep> steps_;
    std::shared_ptr<ISagaLog> log_;

public:
    SagaOrchestrator(std::string id, std::shared_ptr<ISagaLog> log)
        : saga_id_(std::move(id)), log_(std::move(log)) {}

    void add_step(SagaStep step) {
        steps_.push_back(std::move(step));
    }

    bool execute(StepContext& ctx) {
        std::cout << "\n=== Запуск Саги: " << saga_id_ << " ===\n";
        ctx.saga_id = saga_id_;
        size_t last_executed = 0;
        bool forward_success = true;

        // 1. Прямий хід (Forward execution)
        for (size_t i = 0; i < steps_.size(); ++i) {
            auto& step = steps_[i];
            log_->log_state(saga_id_, i, step.name, StepState::Executing);

            bool success = false;
            int retries = 0;
            const int max_retries = (step.kind == StepKind::Retryable) ? 3 : 1;

            while (!success && retries < max_retries) {
                if (retries > 0) {
                    std::cout << "  -> Повтор кроку " << step.name << " (спроба " << retries + 1 << ")...\n";
                    std::this_thread::sleep_for(std::chrono::milliseconds(50));
                }
                success = step.action(ctx);
                retries++;
            }

            if (success) {
                log_->log_state(saga_id_, i, step.name, StepState::Completed);
                last_executed = i;
            } else {
                log_->log_state(saga_id_, i, step.name, StepState::Failed);
                std::cout << " [ERROR] Крок " << step.name << " завершився фатальною помилкою!\n";
                forward_success = false;
                break;
            }
        }

        if (forward_success) {
            std::cout << "=== Сага " << saga_id_ << " успішно завершена ===\n";
            return true;
        }

        // 2. Зворотний хід (Backward compensation)
        std::cout << "\n--- Запуск каскаду компенсацій для Саги " << saga_id_ << " ---\n";
        for (int i = static_cast<int>(last_executed); i >= 0; --i) {
            auto& step = steps_[i];
            if (step.compensate) {
                log_->log_state(saga_id_, i, step.name, StepState::Compensating);
                bool comp_ok = false;
                int retries = 0;
                while (!comp_ok && retries < 5) {
                    comp_ok = step.compensate(ctx);
                    if (!comp_ok) {
                        std::cout << "  [WARN] Збій компенсації " << step.name << ", повтор...\n";
                        std::this_thread::sleep_for(std::chrono::milliseconds(50));
                    }
                    retries++;
                }
                log_->log_state(saga_id_, i, step.name, StepState::Compensated);
            }
        }

        std::cout << "=== Сага " << saga_id_ << " компенсована (стан узгоджено) ===\n";
        return false;
    }
};

int main() {
    auto log = std::make_shared<ConsoleSagaLog>();

    // Сценарій 1: Успішне виконання
    {
        SagaOrchestrator saga("ORD-1001", log);
        saga.add_step(SagaStep("Payment", StepKind::Compensable,
            [](StepContext& ctx) {
                std::cout << "  [Billing] Списано 1500 грн для " << ctx.saga_id << "\n";
                return true;
            },
            [](StepContext& ctx) {
                std::cout << "  [Billing-Comp] Повернуто 1500 грн для " << ctx.saga_id << "\n";
                return true;
            }
        ));

        saga.add_step(SagaStep("Inventory", StepKind::Pivot,
            [](StepContext& ctx) {
                std::cout << "  [Warehouse] Товар зарезервовано на складі\n";
                return true;
            },
            [](StepContext& ctx) {
                std::cout << "  [Warehouse-Comp] Знято резерв товару\n";
                return true;
            }
        ));

        saga.add_step(SagaStep("Notification", StepKind::Retryable,
            [](StepContext& ctx) {
                std::cout << "  [Notifier] Чек надіслано покупцю\n";
                return true;
            }
        ));

        StepContext ctx{"", "order_data_ok", false};
        saga.execute(ctx);
    }

    // Сценарій 2: Збій на етапі складу з відкатом платежу
    {
        SagaOrchestrator saga("ORD-1002", log);
        saga.add_step(SagaStep("Payment", StepKind::Compensable,
            [](StepContext& ctx) {
                std::cout << "  [Billing] Списано 1500 грн для " << ctx.saga_id << "\n";
                return true;
            },
            [](StepContext& ctx) {
                std::cout << "  [Billing-Comp] Повернуто 1500 грн для " << ctx.saga_id << "\n";
                return true;
            }
        ));

        saga.add_step(SagaStep("Inventory", StepKind::Pivot,
            [](StepContext& ctx) {
                std::cout << "  [Warehouse] ПОМИЛКА: Товару немає на залишку!\n";
                return false;
            },
            [](StepContext& ctx) {
                std::cout << "  [Warehouse-Comp] Знято резерв товару\n";
                return true;
            }
        ));

        StepContext ctx{"", "order_data_fail", true};
        saga.execute(ctx);
    }

    return 0;
}
