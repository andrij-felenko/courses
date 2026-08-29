#pragma once

#include "bsp/platform.hpp"
#include "bsp/status.hpp"
#include "bsp/types.hpp"

#include <chrono>
#include <memory>

namespace bsp {

/**
 * @brief Контракт пакета підтримки плати.
 *
 * Ті самі зобов'язання, що й у C-версії: init ≤ 50 мс, вмикання домену
 * блокує на 10–20 мс, батарея ≤ 1.5 мс, клімат ≤ 25 мс на I2C 100 кГц.
 * Усе, що блокує (power_domain_set, read_environment, enter_low_power),
 * викликається лише з потокового контексту; led_set і uptime дозволені в ISR.
 */
class IBoardSupport {
public:
    virtual ~IBoardSupport() = default;

    [[nodiscard]] virtual Result init() noexcept = 0;
    [[nodiscard]] virtual Result deinit() noexcept = 0;

    [[nodiscard]] virtual Result led_set(LedId led, LedState state) noexcept = 0;
    [[nodiscard]] virtual Result led_toggle(LedId led) noexcept = 0;

    [[nodiscard]] virtual Result power_domain_set(PowerDomain domain, bool enable) noexcept = 0;

    [[nodiscard]] virtual std::expected<BatteryMetrics, Status> battery_metrics() noexcept = 0;
    [[nodiscard]] virtual std::expected<EnvironmentMetrics, Status> read_environment() noexcept = 0;

    [[nodiscard]] virtual Result enter_low_power(SleepMode mode,
                                                 std::chrono::milliseconds timeout) noexcept = 0;

    [[nodiscard]] virtual std::chrono::milliseconds uptime() const noexcept = 0;
    virtual void delay(std::chrono::microseconds us) const noexcept = 0;
};

/**
 * @brief RAII-обгортка для автоматичного знеструмлення периферійного домену.
 *
 * Живить домен рівно стільки, скільки живе об'єкт: жодного «забув вимкнути»
 * на гілці помилки.
 */
class [[nodiscard]] PowerDomainGuard {
public:
    PowerDomainGuard(IBoardSupport& board, PowerDomain domain) noexcept
        : board_{&board}, domain_{domain}, result_{board.power_domain_set(domain, true)} {}

    ~PowerDomainGuard() {
        if (board_ != nullptr && result_.has_value()) {
            (void)board_->power_domain_set(domain_, false);
        }
    }

    PowerDomainGuard(const PowerDomainGuard&) = delete;
    PowerDomainGuard& operator=(const PowerDomainGuard&) = delete;

    /* Переміщення знеструмлює домен рівно один раз — у нового власника. */
    PowerDomainGuard(PowerDomainGuard&& other) noexcept
        : board_{other.board_}, domain_{other.domain_}, result_{other.result_} {
        other.board_ = nullptr;
    }
    PowerDomainGuard& operator=(PowerDomainGuard&&) = delete;

    [[nodiscard]] explicit operator bool() const noexcept { return result_.has_value(); }

    [[nodiscard]] Status error() const noexcept {
        return result_.has_value() ? Status::Ok : result_.error();
    }

private:
    IBoardSupport* board_;
    PowerDomain    domain_;
    Result         result_;
};

/**
 * @brief Створити реалізацію контракту поверх конкретної платформи.
 *
 * Платформа мусить пережити повернений об'єкт (звично вона статична).
 */
[[nodiscard]] std::unique_ptr<IBoardSupport> make_board(IPlatform& platform);

} // namespace bsp
