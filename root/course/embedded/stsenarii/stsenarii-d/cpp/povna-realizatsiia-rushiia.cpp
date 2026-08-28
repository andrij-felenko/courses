#include <cstdint>
#include <cstddef>
#include <string_view>
#include <vector>
#include <span>
#include <functional>
#include <expected>
#include <chrono>

/* Типізовані стани та коди результатів сценарію */
enum class ScenarioStatus : uint8_t {
    Idle,
    Running,
    Success,
    Failed,
    RollingBack,
    AbortedSafe
};

enum class ScenarioError : uint8_t {
    None,
    PreconditionFailed,
    Timeout,
    InvariantViolated,
    UserAborted,
    EngineBusy
};

/* Декларативний крок сценарію на базі C++20 */
struct ScenarioStep {
    std::string_view             name;
    std::function<void()>        action;
    std::function<bool()>        precondition;      /* Може бути порожнім */
    std::function<bool()>        postcondition;     /* Може бути порожнім */
    std::function<void()>        rollback;          /* Компенсатор LIFO */
    std::chrono::milliseconds    timeout{0};
    std::chrono::milliseconds    settle_delay{0};
};

class ScenarioEngine {
public:
    using InvariantChecker = std::function<bool()>;

    explicit ScenarioEngine(InvariantChecker invariant_fn = nullptr)
        : invariant_checker_(std::move(invariant_fn)) {}

    /* Запуск сценарію на виконання */
    std::expected<void, ScenarioError> start(std::span<const ScenarioStep> steps,
                                            std::chrono::milliseconds now) {
        if (steps.empty()) {
            return std::unexpected(ScenarioError::PreconditionFailed);
        }
        if (status_ == ScenarioStatus::Running || status_ == ScenarioStatus::RollingBack) {
            return std::unexpected(ScenarioError::EngineBusy);
        }

        steps_ = steps;
        current_step_idx_ = 0;
        status_ = ScenarioStatus::Running;
        last_error_ = ScenarioError::None;
        step_phase_ = StepPhase::Precheck;
        step_start_time_ = now;
        rollback_stack_.clear();
        return {};
    }

    /* Примусове скасування з ініціалізацією компенсацій */
    void abort(ScenarioError error) {
        if (status_ != ScenarioStatus::Running) return;
        status_ = ScenarioStatus::RollingBack;
        last_error_ = error;
    }

    /* Періодичний неблокуючий тік рушія */
    void tick(std::chrono::milliseconds now) {
        if (status_ == ScenarioStatus::RollingBack) {
            process_rollback();
            return;
        }

        if (status_ != ScenarioStatus::Running) {
            return;
        }

        /* 1. Наскрізні інваріанти безпеки */
        if (invariant_checker_ && !invariant_checker_()) {
            abort(ScenarioError::InvariantViolated);
            return;
        }

        const auto& step = steps_[current_step_idx_];

        switch (step_phase_) {
            case StepPhase::Precheck:
                if (step.precondition && !step.precondition()) {
                    abort(ScenarioError::PreconditionFailed);
                    return;
                }
                step_phase_ = StepPhase::Enter;
                [[fallthrough]];

            case StepPhase::Enter:
                if (step.action) {
                    step.action();
                }
                if (step.rollback) {
                    rollback_stack_.push_back(step.rollback);
                }
                step_start_time_ = now;
                step_phase_ = StepPhase::Executing;
                break;

            case StepPhase::Executing: {
                auto elapsed = now - step_start_time_;

                /* Перевірка таймауту */
                if (step.timeout > std::chrono::milliseconds::zero() && elapsed >= step.timeout) {
                    abort(ScenarioError::Timeout);
                    return;
                }

                /* Витримка технологічної затримки стабілізації */
                if (elapsed < step.settle_delay) {
                    return;
                }

                /* Перевірка постумови */
                bool done = true;
                if (step.postcondition) {
                    done = step.postcondition();
                }

                if (done) {
                    current_step_idx_++;
                    if (current_step_idx_ >= steps_.size()) {
                        status_ = ScenarioStatus::Success;
                        rollback_stack_.clear();
                    } else {
                        step_phase_ = StepPhase::Precheck;
                    }
                }
                break;
            }
        }
    }

    [[nodiscard]] ScenarioStatus status() const noexcept { return status_; }
    [[nodiscard]] ScenarioError last_error() const noexcept { return last_error_; }
    [[nodiscard]] size_t current_step() const noexcept { return current_step_idx_; }

private:
    enum class StepPhase : uint8_t { Precheck, Enter, Executing };

    void process_rollback() {
        if (!rollback_stack_.empty()) {
            auto undo = rollback_stack_.back();
            rollback_stack_.pop_back();
            if (undo) {
                undo();
            }
        } else {
            status_ = ScenarioStatus::AbortedSafe;
        }
    }

    std::span<const ScenarioStep> steps_{};
    size_t                        current_step_idx_{0};
    ScenarioStatus                status_{ScenarioStatus::Idle};
    ScenarioError                 last_error_{ScenarioError::None};
    StepPhase                     step_phase_{StepPhase::Precheck};
    std::chrono::milliseconds     step_start_time_{0};
    InvariantChecker              invariant_checker_{nullptr};
    std::vector<std::function<void()>> rollback_stack_{};
};
