#pragma once

// Задача з власним стеком як об'єкт. Стек — член класу, тож його розмір
// видно типу: бюджет RAM рахується static_assert-ом, а не на папері.
#include "FreeRTOS.h"
#include "task.h"

#include <array>
#include <cstddef>

namespace rtos {

template <class Worker>
concept Runnable = requires(Worker &w) {
    { w.run() };
};

template <std::size_t StackWords>
class StaticTask {
public:
    template <Runnable Worker>
    StaticTask(Worker &worker, const char *name, UBaseType_t priority) noexcept
        : handle_{xTaskCreateStatic(&entry<Worker>, name, StackWords, &worker, priority,
                                    stack_.data(), &tcb_)}
    {
        configASSERT(handle_ != nullptr);
    }

    StaticTask(const StaticTask &) = delete;
    StaticTask &operator=(const StaticTask &) = delete;

    [[nodiscard]] static constexpr std::size_t stack_bytes() noexcept
    {
        return StackWords * sizeof(StackType_t);
    }

    // Скільки стека жодного разу не було зачеплено — єдина чесна міра запасу.
    [[nodiscard]] std::size_t untouched_bytes() const noexcept
    {
        return uxTaskGetStackHighWaterMark(handle_) * sizeof(StackType_t);
    }

    [[nodiscard]] TaskHandle_t handle() const noexcept { return handle_; }

    void notify(std::uint32_t bits) noexcept
    {
        xTaskNotify(handle_, bits, eSetBits);
    }

private:
    template <Runnable Worker>
    static void entry(void *arg)
    {
        // Тіло задачі не повертається: run() — нескінченний цикл.
        static_cast<Worker *>(arg)->run();
        configASSERT(0);
    }

    std::array<StackType_t, StackWords> stack_{};
    StaticTask_t tcb_{};
    TaskHandle_t handle_{nullptr};
};

} // namespace rtos
