#pragma once
#include <cstdint>
#include <chrono>
#include <optional>

namespace fleet {

enum class BootBank : uint8_t {
    BankA = 0,
    BankB = 1
};

class TrialBootController {
public:
    using Seconds = std::chrono::seconds;

    constexpr TrialBootController(BootBank active, Seconds timeout) noexcept
        : active_bank_(active), timeout_(timeout), elapsed_(0), confirmed_(false) {}

    [[nodiscard]] bool process_heartbeat(Seconds dt, bool sensors_ok, bool network_ok) noexcept {
        if (confirmed_) {
            return true;
        }

        if (!sensors_ok || !network_ok) {
            trigger_rollback();
            return false;
        }

        elapsed_ += dt;
        if (elapsed_ >= timeout_) {
            confirmed_ = true;
            return true;
        }
        return true;
    }

    [[nodiscard]] constexpr bool is_stable() const noexcept { return confirmed_; }
    [[nodiscard]] constexpr BootBank active_bank() const noexcept { return active_bank_; }

    void trigger_rollback() noexcept {
        active_bank_ = (active_bank_ == BootBank::BankB) ? BootBank::BankA : BootBank::BankB;
        confirmed_ = false;
    }

private:
    BootBank active_bank_;
    Seconds timeout_;
    Seconds elapsed_;
    bool confirmed_;
};

} // namespace fleet
