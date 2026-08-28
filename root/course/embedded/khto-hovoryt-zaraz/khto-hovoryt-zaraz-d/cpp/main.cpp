#include <cstdint>
#include <cstddef>
#include <span>
#include <random>
#include <functional>

enum class CsmaState : uint8_t {
    Idle,
    WaitDifs,
    Backoff,
    Transmitting,
    WaitAck,
    Failed,
    Success
};

struct RadioHal {
    std::function<bool()> is_channel_busy;
    std::function<void(std::span<const uint8_t>)> start_tx;
    std::function<bool()> is_tx_done;
    std::function<uint32_t()> get_time_us;
};

class CsmaMacEngine {
public:
    static constexpr uint32_t SlotTimeUs   = 100;
    static constexpr uint32_t DifsTimeUs   = 400;
    static constexpr uint32_t AckTimeoutUs = 2000;
    static constexpr uint32_t CwMin        = 7;
    static constexpr uint32_t CwMax        = 127;
    static constexpr uint8_t  MaxRetries   = 4;

    explicit CsmaMacEngine(RadioHal hal)
        : hal_(std::move(hal)),
          rng_(std::random_device{}()) {}

    bool send(std::span<const uint8_t> packet) {
        if (state_ != CsmaState::Idle && state_ != CsmaState::Success && state_ != CsmaState::Failed) {
            return false;
        }
        current_packet_ = packet;
        retry_count_ = 0;
        cw_current_ = CwMin;
        state_ = CsmaState::WaitDifs;
        timer_start_us_ = hal_.get_time_us();
        return true;
    }

    void process() {
        const uint32_t now = hal_.get_time_us();

        switch (state_) {
            case CsmaState::WaitDifs:
                if (hal_.is_channel_busy()) {
                    timer_start_us_ = now;
                } else if ((now - timer_start_us_) >= DifsTimeUs) {
                    std::uniform_int_distribution<uint32_t> dist(0, cw_current_);
                    backoff_slots_ = dist(rng_);
                    timer_start_us_ = now;
                    state_ = CsmaState::Backoff;
                }
                break;

            case CsmaState::Backoff:
                if (hal_.is_channel_busy()) {
                    timer_start_us_ = now;
                    state_ = CsmaState::WaitDifs;
                } else if ((now - timer_start_us_) >= SlotTimeUs) {
                    timer_start_us_ = now;
                    if (backoff_slots_ == 0) {
                        hal_.start_tx(current_packet_);
                        state_ = CsmaState::Transmitting;
                    } else {
                        --backoff_slots_;
                    }
                }
                break;

            case CsmaState::Transmitting:
                if (hal_.is_tx_done()) {
                    timer_start_us_ = now;
                    state_ = CsmaState::WaitAck;
                }
                break;

            case CsmaState::WaitAck:
                if ((now - timer_start_us_) >= AckTimeoutUs) {
                    ++retry_count_;
                    if (retry_count_ > MaxRetries) {
                        state_ = CsmaState::Failed;
                    } else {
                        cw_current_ = std::min((cw_current_ << 1) | 1U, CwMax);
                        state_ = CsmaState::WaitDifs;
                        timer_start_us_ = now;
                    }
                }
                break;

            case CsmaState::Idle:
            case CsmaState::Success:
            case CsmaState::Failed:
                break;
        }
    }

    void on_ack_received() noexcept {
        if (state_ == CsmaState::WaitAck) {
            state_ = CsmaState::Success;
            cw_current_ = CwMin;
        }
    }

    [[nodiscard]] CsmaState state() const noexcept { return state_; }

private:
    RadioHal hal_;
    std::mt19937 rng_;
    CsmaState state_{CsmaState::Idle};
    std::span<const uint8_t> current_packet_{};
    uint32_t timer_start_us_{0};
    uint32_t cw_current_{CwMin};
    uint32_t backoff_slots_{0};
    uint8_t  retry_count_{0};
};
