#include <iostream>
#include <vector>
#include <unordered_set>
#include <optional>
#include <memory>
#include <cstdint>
#include <span>

// Статус виконання закрокованого автомата
enum class StepResult {
    Running,
    Halted,
    Failed
};

// Інтерфейс обчислювальної задачі (абстрактний покроковий автомат)
class IComputableTask {
public:
    virtual ~IComputableTask() = default;
    virtual StepResult step() = 0;
    [[nodiscard]] virtual std::optional<int32_t> result() const = 0;
    [[nodiscard]] virtual uint32_t id() const = 0;
    [[nodiscard]] virtual bool is_completed() const = 0;
};

// Конкретна реалізація задачі симуляції
class SimTask final : public IComputableTask {
private:
    uint32_t id_;
    uint32_t state_;
    uint64_t steps_{0};
    std::optional<int32_t> result_{std::nullopt};
    bool completed_{false};

public:
    explicit SimTask(uint32_t task_id)
        : id_(task_id), state_(task_id + 1) {}

    StepResult step() override {
        if (completed_) return StepResult::Halted;

        steps_++;
        state_ = (state_ * 1103515245U + 12345U) & 0x7FFFFFFFU;

        if ((state_ + id_) % 17U == 0U) {
            result_ = static_cast<int32_t>(steps_ * 10U + id_);
            completed_ = true;
            return StepResult::Halted;
        }
        return StepResult::Running;
    }

    [[nodiscard]] std::optional<int32_t> result() const override { return result_; }
    [[nodiscard]] uint32_t id() const override { return id_; }
    [[nodiscard]] bool is_completed() const override { return completed_; }
};

// Планувальник Dovetailing на C++20
class DovetailEnumerator {
private:
    std::vector<std::unique_ptr<IComputableTask>> tasks_;
    std::unordered_set<int32_t> enumerated_set_;
    std::vector<int32_t> ordered_results_;

public:
    void add_task(std::unique_ptr<IComputableTask> task) {
        tasks_.push_back(std::move(task));
    }

    // Запуск діагонального обходу
    void run(size_t max_diagonals) {
        for (size_t s = 1; s <= max_diagonals; ++s) {
            for (size_t i = 0; i < s && i < tasks_.size(); ++i) {
                auto& task = tasks_[i];
                if (task->is_completed()) continue;

                if (task->step() == StepResult::Halted) {
                    if (auto res = task->result(); res.has_value()) {
                        if (enumerated_set_.insert(*res).second) {
                            ordered_results_.push_back(*res);
                            std::cout << "[ENUMERATOR C++] Знайдено нове значення: "
                                      << *res << " (Задача ID: " << task->id() << ")\n";
                        }
                    }
                }
            }
        }
    }

    [[nodiscard]] std::span<const int32_t> get_results() const noexcept {
        return ordered_results_;
    }
};
