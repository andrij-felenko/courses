#include <cstdint>
#include <concepts>
#include <chrono>
#include <expected>
#include <span>
#include <string_view>
#include <functional>
#include <array>
#include "stm32f4xx.h"

namespace hal::init {

using namespace std::chrono_literals;

enum class EngineStatus : uint8_t {
    Running,
    Success,
    Failed,
    Degraded
};

enum class StepError : uint8_t {
    ActionFailed,
    TimeoutExpired,
    HardwareFault
};

template <typename Context>
struct StepDescriptor {
    std::string_view name;
    std::function<std::expected<void, StepError>(Context&)> action{nullptr};
    std::chrono::microseconds hold_delay{0us};
    std::function<bool(Context&)> poll_condition{nullptr};
    std::chrono::microseconds timeout{0us};
    std::function<void(Context&)> rollback{nullptr};
    bool is_critical{true};
};

class DwtClock {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    [[nodiscard]] static uint32_t cycles() noexcept {
        return DWT->CYCCNT;
    }

    template <typename Rep, typename Period>
    [[nodiscard]] static uint32_t to_cycles(std::chrono::duration<Rep, Period> duration) noexcept {
        const auto us = std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
        return static_cast<uint32_t>(us) * (SystemCoreClock / 1'000'000U);
    }
};

template <typename Context>
class SequenceEngine {
public:
    explicit SequenceEngine(Context& context, std::span<const StepDescriptor<Context>> steps) noexcept
        : context_(context), steps_(steps), current_index_(0), status_(EngineStatus::Running) {
        DwtClock::init();
        phase_start_cycles_ = DwtClock::cycles();
    }

    [[nodiscard]] EngineStatus poll() noexcept {
        if (status_ != EngineStatus::Running) {
            return status_;
        }

        feed_watchdog();

        if (current_index_ >= steps_.size()) {
            status_ = (failed_mask_ == 0) ? EngineStatus::Success : EngineStatus::Degraded;
            return status_;
        }

        const auto& step = steps_[current_index_];
        const uint32_t now = DwtClock::cycles();

        switch (phase_) {
            case Phase::ExecuteAction: {
                if (step.action) {
                    auto result = step.action(context_);
                    if (!result.has_value()) {
                        handle_step_failure(step);
                        return status_;
                    }
                }
                phase_start_cycles_ = now;
                phase_ = Phase::WaitHoldDelay;
                break;
            }

            case Phase::WaitHoldDelay: {
                const uint32_t delay_ticks = DwtClock::to_cycles(step.hold_delay);
                if ((now - phase_start_cycles_) >= delay_ticks) {
                    if (step.poll_condition) {
                        poll_start_cycles_ = now;
                        phase_ = Phase::PollCondition;
                    } else {
                        advance_next_step();
                    }
                }
                break;
            }

            case Phase::PollCondition: {
                if (step.poll_condition(context_)) {
                    advance_next_step();
                } else {
                    const uint32_t timeout_ticks = DwtClock::to_cycles(step.timeout);
                    if ((now - poll_start_cycles_) >= timeout_ticks) {
                        handle_step_failure(step);
                    }
                }
                break;
            }
        }

        return status_;
    }

    [[nodiscard]] uint32_t failed_mask() const noexcept { return failed_mask_; }

private:
    enum class Phase : uint8_t {
        ExecuteAction,
        WaitHoldDelay,
        PollCondition
    };

    Context& context_;
    std::span<const StepDescriptor<Context>> steps_;
    size_t current_index_{0};
    Phase phase_{Phase::ExecuteAction};
    uint32_t phase_start_cycles_{0};
    uint32_t poll_start_cycles_{0};
    uint32_t failed_mask_{0};
    EngineStatus status_{EngineStatus::Running};

    static void feed_watchdog() noexcept {
        #if defined(IWDG)
        IWDG->KR = 0xAAAAU;
        #endif
    }

    void advance_next_step() noexcept {
        current_index_++;
        phase_ = Phase::ExecuteAction;
    }

    void handle_step_failure(const StepDescriptor<Context>& step) noexcept {
        if (step.rollback) {
            step.rollback(context_);
        }
        failed_mask_ |= (1U << current_index_);
        if (step.is_critical) {
            status_ = EngineStatus::Failed;
        } else {
            advance_next_step();
        }
    }
};

// ── Приклад декларативного конфігурування на C++20 ──

struct FlightControllerContext {
    bool power_good{false};
    bool i2c_recovered{false};
    bool imu_ready{false};
    bool barometer_ready{false};
};

inline const std::array<StepDescriptor<FlightControllerContext>, 4> g_flight_steps{{
    {
        .name = "POWER_RAIL_STABILIZE",
        .action = [](FlightControllerContext& ctx) -> std::expected<void, StepError> {
            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
            GPIOC->BSRR = GPIO_BSRR_BS13; // Power ON
            GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER13_Msk) | (1U << GPIO_MODER_MODER13_Pos);
            ctx.power_good = true;
            return {};
        },
        .hold_delay = 12'000us,
        .poll_condition = [](FlightControllerContext& ctx) noexcept { return ctx.power_good; },
        .timeout = 5'000us,
        .rollback = [](FlightControllerContext& ctx) noexcept {
            GPIOC->BSRR = GPIO_BSRR_BR13;
            ctx.power_good = false;
        },
        .is_critical = true
    },
    {
        .name = "I2C_BUS_CLOCK_CLEANUP",
        .action = [](FlightControllerContext&) -> std::expected<void, StepError> {
            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
            GPIOB->MODER |= (1U << GPIO_MODER_MODER8_Pos);
            for (int i = 0; i < 9; ++i) {
                GPIOB->BSRR = GPIO_BSRR_BR8;
                for (volatile int d = 0; d < 40; ++d) __NOP();
                GPIOB->BSRR = GPIO_BSRR_BS8;
                for (volatile int d = 0; d < 40; ++d) __NOP();
            }
            return {};
        },
        .hold_delay = 2'000us,
        .poll_condition = [](FlightControllerContext& ctx) noexcept {
            ctx.i2c_recovered = true;
            return true;
        },
        .timeout = 3'000us,
        .rollback = [](FlightControllerContext& ctx) noexcept { ctx.i2c_recovered = false; },
        .is_critical = false
    },
    {
        .name = "IMU_HARDWARE_RESET_CYCLE",
        .action = [](FlightControllerContext&) -> std::expected<void, StepError> {
            GPIOC->BSRR = GPIO_BSRR_BR4; // Assert nRST
            return {};
        },
        .hold_delay = 15'000us,
        .poll_condition = nullptr,
        .timeout = 0us,
        .rollback = nullptr,
        .is_critical = false
    },
    {
        .name = "IMU_BOOT_AND_VALIDATE",
        .action = [](FlightControllerContext&) -> std::expected<void, StepError> {
            GPIOC->BSRR = GPIO_BSRR_BS4; // Release nRST
            return {};
        },
        .hold_delay = 25'000us,
        .poll_condition = [](FlightControllerContext& ctx) noexcept {
            ctx.imu_ready = true;
            return true;
        },
        .timeout = 10'000us,
        .rollback = [](FlightControllerContext& ctx) noexcept { ctx.imu_ready = false; },
        .is_critical = true // Для польотного контролера IMU є критичним
    }
}};

void run_cpp_bringup_example() {
    FlightControllerContext context;
    SequenceEngine<FlightControllerContext> engine(context, g_flight_steps);

    while (engine.poll() == EngineStatus::Running) {
        // Неблокувальний цикл диспетчера
    }

    if (engine.poll() == EngineStatus::Success) {
        // Усі датчики готові до навігаційного циклу
    }
}

} // namespace hal::init
