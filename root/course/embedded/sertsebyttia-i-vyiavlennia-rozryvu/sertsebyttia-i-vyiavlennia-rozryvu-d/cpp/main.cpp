#include <cstdint>
#include <chrono>
#include <algorithm>
#include <functional>

enum class LinkState : uint8_t {
    Disconnected = 0,
    Connecting,
    ConnectedOk,
    Suspect,
    Failsafe
};

class HeartbeatMonitor {
public:
    using Milliseconds = std::chrono::milliseconds;
    using Callback = std::function<void()>;

    explicit HeartbeatMonitor(Callback on_failsafe_enter,
                              Callback on_failsafe_exit,
                              Milliseconds period = Milliseconds(200)) noexcept
        : period_(period),
          on_failsafe_enter_(std::move(on_failsafe_enter)),
          on_failsafe_exit_(std::move(on_failsafe_exit)) {}

    void start(Milliseconds now) noexcept {
        last_rx_time_ = now;
        last_tx_time_ = now;
        missed_count_ = 0;
        recovery_counter_ = 0;
        state_ = LinkState::Connecting;
    }

    void on_frame_received(Milliseconds now, Milliseconds rtt_sample, bool is_retransmit) noexcept {
        last_rx_time_ = now;
        missed_count_ = 0;

        if (!is_retransmit && rtt_sample.count() > 0) {
            update_rtt(rtt_sample);
        }

        switch (state_) {
            case LinkState::Disconnected:
            case LinkState::Connecting:
            case LinkState::Suspect:
                state_ = LinkState::ConnectedOk;
                break;

            case LinkState::Failsafe:
                if (++recovery_counter_ >= min_recovery_packets_) {
                    state_ = LinkState::ConnectedOk;
                    recovery_counter_ = 0;
                    if (on_failsafe_exit_) {
                        on_failsafe_exit_();
                    }
                }
                break;

            case LinkState::ConnectedOk:
                break;
        }
    }

    void tick(Milliseconds now) noexcept {
        if (state_ == LinkState::Disconnected) {
            return;
        }

        auto elapsed = now - last_rx_time_;
        if (elapsed >= rto_) {
            ++missed_count_;
            last_rx_time_ = now;

            if (state_ == LinkState::ConnectedOk) {
                state_ = LinkState::Suspect;
            }

            if (missed_count_ >= max_missed_count_ && state_ != LinkState::Failsafe) {
                state_ = LinkState::Failsafe;
                recovery_counter_ = 0;
                if (on_failsafe_enter_) {
                    on_failsafe_enter_();
                }
            }
        }
    }

    [[nodiscard]] LinkState state() const noexcept { return state_; }
    [[nodiscard]] Milliseconds current_rto() const noexcept { return rto_; }

private:
    void update_rtt(Milliseconds rtt_sample) noexcept {
        const int32_t sample_ms = static_cast<int32_t>(rtt_sample.count());
        const int32_t err = sample_ms - (srtt_scaled_ >> 3);
        srtt_scaled_ += err;

        const int32_t abs_err = std::abs(err);
        const int32_t err_var = abs_err - (rttvar_scaled_ >> 2);
        rttvar_scaled_ += err_var;

        const int32_t calculated_rto = (srtt_scaled_ >> 3) + rttvar_scaled_;
        const int32_t clamped_rto = std::clamp(calculated_rto, 100, 2000);
        rto_ = Milliseconds(clamped_rto);
    }

    static constexpr uint32_t max_missed_count_ = 3;
    static constexpr uint32_t min_recovery_packets_ = 5;

    Milliseconds period_{200};
    Milliseconds last_rx_time_{0};
    Milliseconds last_tx_time_{0};
    Milliseconds rto_{150};

    int32_t srtt_scaled_{50 * 8};
    int32_t rttvar_scaled_{25 * 4};

    uint32_t missed_count_{0};
    uint32_t recovery_counter_{0};

    LinkState state_{LinkState::Disconnected};
    Callback on_failsafe_enter_;
    Callback on_failsafe_exit_;
};
