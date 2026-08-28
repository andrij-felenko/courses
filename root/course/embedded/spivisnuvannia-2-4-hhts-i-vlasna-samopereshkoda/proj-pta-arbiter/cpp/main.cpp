#include <cstdint>
#include <chrono>
#include <optional>
#include <expected>

namespace coex {

using namespace std::chrono_literals;

enum class Priority : uint8_t {
    Low = 0,
    High = 1
};

enum class State : uint8_t {
    Idle = 0,
    Requesting,
    Granted,
    Denied,
    Aborted
};

enum class Error : uint8_t {
    Timeout,
    Preempted,
    HardwareFault
};

class HalInterface {
public:
    virtual ~HalInterface() = default;
    virtual void set_gpio(uint8_t pin, bool level) = 0;
    virtual bool read_gpio(uint8_t pin) = 0;
    virtual void delay(std::chrono::microseconds us) = 0;
    virtual void abort_radio_tx() = 0;
};

class PtaArbiter {
public:
    static constexpr auto ReqLeadTime = 30us;

    PtaArbiter(HalInterface& hal, uint8_t req_pin, uint8_t pri_pin, uint8_t gnt_pin)
        : hal_{hal}, req_pin_{req_pin}, pri_pin_{pri_pin}, gnt_pin_{gnt_pin}, state_{State::Idle} {
        hal_.set_gpio(req_pin_, false);
        hal_.set_gpio(pri_pin_, false);
    }

    ~PtaArbiter() {
        release();
    }

    PtaArbiter(const PtaArbiter&) = delete;
    PtaArbiter& operator=(const PtaArbiter&) = delete;

    std::expected<void, Error> request(Priority pri, std::chrono::microseconds timeout = 100us) {
        state_ = State::Requesting;
        hal_.set_gpio(pri_pin_, pri == Priority::High);
        hal_.set_gpio(req_pin_, true);

        hal_.delay(ReqLeadTime);

        auto elapsed = 0us;
        const auto step = 5us;

        while (elapsed < timeout) {
            if (hal_.read_gpio(gnt_pin_)) {
                state_ = State::Granted;
                return {};
            }
            hal_.delay(step);
            elapsed += step;
        }

        release();
        state_ = State::Denied;
        return std::unexpected(Error::Timeout);
    }

    void release() noexcept {
        hal_.set_gpio(req_pin_, false);
        hal_.set_gpio(pri_pin_, false);
        state_ = State::Idle;
    }

    void on_grant_revoked_isr() noexcept {
        if (state_ == State::Granted) {
            hal_.abort_radio_tx();
            hal_.set_gpio(req_pin_, false);
            hal_.set_gpio(pri_pin_, false);
            state_ = State::Aborted;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }

private:
    HalInterface& hal_;
    uint8_t req_pin_;
    uint8_t pri_pin_;
    uint8_t gnt_pin_;
    State state_;
};

/* RAII-обгортка для автоматичного звільнення радіоефіру */
class [[nodiscard]] ScopedPtaTransaction {
public:
    ScopedPtaTransaction(PtaArbiter& arbiter, Priority pri)
        : arbiter_{arbiter}, acquired_{false} {
        if (auto res = arbiter_.request(pri); res.has_value()) {
            acquired_ = true;
        }
    }

    ~ScopedPtaTransaction() {
        if (acquired_) {
            arbiter_.release();
        }
    }

    [[nodiscard]] bool is_granted() const noexcept { return acquired_; }

private:
    PtaArbiter& arbiter_;
    bool acquired_;
};

} // namespace coex
