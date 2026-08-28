#include <iostream>
#include <string>
#include <vector>
#include <variant>
#include <memory>
#include <stdexcept>
#include <optional>
#include <functional>

// ── Типи подій у незмінному журналі історії ──────────────────────────────
struct WorkflowStartedEvent {
    std::string workflow_id;
    std::string input_data;
};

struct ActivityScheduledEvent {
    std::string activity_name;
    std::string input;
};

struct ActivityCompletedEvent {
    std::string activity_name;
    std::string result;
};

struct TimerFiredEvent {
    int duration_ms;
};

using WorkflowEvent = std::variant<
    WorkflowStartedEvent,
    ActivityScheduledEvent,
    ActivityCompletedEvent,
    TimerFiredEvent
>;

// ── Виняток для призупинення виконання при очікуванні результату ─────────
class ExecutionYieldedException : public std::exception {
public:
    const char* what() const noexcept override {
        return "Workflow execution yielded awaiting external event";
    }
};

// ── Виняток порушення детермінізму коду ──────────────────────────────────
class NonDeterminismException : public std::runtime_error {
public:
    explicit NonDeterminismException(const std::string& msg)
        : std::runtime_error("Non-determinism detected: " + msg) {}
};

// ── Контекст детермінованого робочого процесу ────────────────────────────
class WorkflowContext {
private:
    const std::vector<WorkflowEvent>& history_;
    std::vector<WorkflowEvent> new_events_;
    size_t replay_index_{0};
    bool is_replaying_{true};

public:
    explicit WorkflowContext(const std::vector<WorkflowEvent>& history)
        : history_(history) {}

    // Метод виклику activity з підтримкою відтворення з історії
    std::string execute_activity(const std::string& name, const std::string& input) {
        if (replay_index_ < history_.size()) {
            const auto& event = history_[replay_index_];
            
            // Якщо наступна подія — завершення цієї активності, повертаємо записаний результат
            if (auto completed = std::get_if<ActivityCompletedEvent>(&event)) {
                if (completed->activity_name != name) {
                    throw NonDeterminismException(
                        "Expected activity '" + completed->activity_name + 
                        "', but workflow requested '" + name + "'"
                    );
                }
                replay_index_++;
                return completed->result;
            }
            
            // Якщо подія в історії є плануванням, ми все ще чекаємо на її результат
            if (auto scheduled = std::get_if<ActivityScheduledEvent>(&event)) {
                if (scheduled->activity_name != name) {
                    throw NonDeterminismException("History mismatch on scheduled activity: " + name);
                }
                replay_index_++;
                throw ExecutionYieldedException();
            }
        }

        // Подій в історії більше немає: плануємо нову активність
        is_replaying_ = false;
        new_events_.push_back(ActivityScheduledEvent{name, input});
        throw ExecutionYieldedException();
    }

    bool is_replaying() const noexcept {
        return is_replaying_ && (replay_index_ < history_.size());
    }

    const std::vector<WorkflowEvent>& get_new_events() const noexcept {
        return new_events_;
    }
};

// ── Функція бізнес-процесу (Workflow Definition) ─────────────────────────
// Код пишеться як звичайна послідовна функція без ручних state-машин
std::string order_fulfillment_workflow(WorkflowContext& ctx, const std::string& order_id) {
    // Крок 1: Списання коштів
    std::string payment_res = ctx.execute_activity("ProcessPayment", order_id + ":amount=500");

    // Крок 2: Резервування товару на складі
    std::string inventory_res = ctx.execute_activity("ReserveInventory", order_id + ":item=SKU-99");

    // Крок 3: Створення накладної доставки
    std::string shipping_res = ctx.execute_activity("CreateShippingLabel", order_id + ":addr=Kyiv");

    return "Order " + order_id + " completed: " + payment_res + " | " + inventory_res + " | " + shipping_res;
}
