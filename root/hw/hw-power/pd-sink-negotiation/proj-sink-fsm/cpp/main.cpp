#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace usb_pd {

enum class PdoType : uint8_t {
    Fixed = 0,
    Variable = 1,
    Battery = 2,
    AugmentedPps = 3
};

enum class State : uint8_t {
    Discovery,
    WaitForCap,
    EvaluateCap,
    SelectCap,
    TransitionSink,
    Ready,
    GiveBack,
    HardReset
};

enum class Event : uint8_t {
    None,
    VbusDetected,
    SourceCapsReceived,
    AcceptReceived,
    RejectReceived,
    WaitReceived,
    PsRdyReceived,
    GotoMinReceived,
    Timeout,
    Error
};

struct Pdo {
    uint8_t  position{0};
    PdoType  type{PdoType::Fixed};
    uint32_t voltage_mv{0};
    uint32_t max_current_ma{0};
    uint32_t max_power_mw{0};

    [[nodiscard]] static constexpr Pdo parse(uint32_t raw, uint8_t pos) noexcept {
        Pdo p;
        p.position = pos;
        p.type = static_cast<PdoType>((raw >> 30) & 0x03);
        if (p.type == PdoType::Fixed) {
            p.voltage_mv = ((raw >> 10) & 0x3FF) * 50;
            p.max_current_ma = (raw & 0x3FF) * 10;
            p.max_power_mw = (p.voltage_mv * p.max_current_ma) / 1000;
        } else {
            p.voltage_mv = 5000;
            p.max_current_ma = 500;
            p.max_power_mw = 2500;
        }
        return p;
    }
};

struct RequestData {
    uint8_t  position{1};
    uint32_t operating_current_ma{500};
    uint32_t max_current_ma{500};
    bool     capability_mismatch{false};
    bool     giveback{false};

    [[nodiscard]] constexpr uint32_t to_raw() const noexcept {
        uint32_t rdo = 0;
        rdo |= (static_cast<uint32_t>(position & 0x0F)) << 28;
        if (giveback)            rdo |= (1UL << 27);
        if (capability_mismatch) rdo |= (1UL << 26);
        rdo |= (1UL << 25); // USB Communications Capable
        rdo |= (1UL << 24); // No USB Suspend
        rdo |= (((operating_current_ma / 10) & 0x3FF) << 10);
        rdo |= (((max_current_ma / 10) & 0x3FF));
        return rdo;
    }
};

class PowerGateGuard {
public:
    static void set(bool enabled) noexcept;
};

class SinkPolicyEngine {
public:
    static constexpr uint32_t V_SAFE_MAX_MV = 20000;
    static constexpr uint32_t V_TARGET_MV   = 12000;
    static constexpr uint32_t I_REQUIRED_MA = 2000;
    static constexpr int32_t  R_CABLE_MOHM  = 200;

    SinkPolicyEngine() = default;

    void update(Event event, uint32_t elapsed_ms) noexcept {
        if (timer_ms_ > elapsed_ms) timer_ms_ -= elapsed_ms;
        else timer_ms_ = 0;

        switch (state_) {
        case State::Discovery:
            isolate_load();
            if (event == Event::VbusDetected) {
                state_ = State::WaitForCap;
                timer_ms_ = 620; // tTypeCSinkWaitCap
            }
            break;

        case State::WaitForCap:
            if (event == Event::SourceCapsReceived) {
                state_ = State::EvaluateCap;
            } else if (timer_ms_ == 0) {
                fallback_safe_5v();
            }
            break;

        case State::EvaluateCap: {
            auto req = evaluate_capabilities();
            if (req.has_value()) {
                send_request(*req);
                state_ = State::SelectCap;
                timer_ms_ = 30; // tSenderResponse
            } else {
                state_ = State::HardReset;
            }
            break;
        }

        case State::SelectCap:
            if (event == Event::AcceptReceived) {
                state_ = State::TransitionSink;
                timer_ms_ = 550; // tPSTransition
            } else if (event == Event::RejectReceived || event == Event::WaitReceived || timer_ms_ == 0) {
                state_ = State::WaitForCap;
                timer_ms_ = 100;
            }
            break;

        case State::TransitionSink:
            if (event == Event::PsRdyReceived) {
                engage_load();
                state_ = State::Ready;
            } else if (timer_ms_ == 0) {
                state_ = State::HardReset;
            }
            break;

        case State::Ready:
            if (event == Event::SourceCapsReceived) {
                state_ = State::EvaluateCap; // Реакція на перерозподіл потужності
            } else if (event == Event::GotoMinReceived) {
                negotiated_ma_ = 500;
                state_ = State::GiveBack;
            }
            break;

        case State::GiveBack:
            state_ = State::Ready;
            break;

        case State::HardReset:
            isolate_load();
            execute_hard_reset();
            state_ = State::Discovery;
            break;
        }
    }

    void load_pdos(std::span<const uint32_t> raw_pdos) noexcept {
        pdo_count_ = static_cast<uint8_t>(std::min(raw_pdos.size(), pdos_.size()));
        for (uint8_t i = 0; i < pdo_count_; ++i) {
            pdos_[i] = Pdo::parse(raw_pdos[i], static_cast<uint8_t>(i + 1));
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint32_t active_voltage() const noexcept { return negotiated_mv_; }
    [[nodiscard]] uint32_t active_current() const noexcept { return negotiated_ma_; }

private:
    [[nodiscard]] std::optional<RequestData> evaluate_capabilities() noexcept {
        int best_idx = -1;
        int32_t best_score = -1000000;

        for (uint8_t i = 0; i < pdo_count_; ++i) {
            const auto& p = pdos_[i];
            if (p.voltage_mv > V_SAFE_MAX_MV) continue;

            int32_t score = static_cast<int32_t>(p.max_power_mw / 100);
            if (p.voltage_mv == V_TARGET_MV) score += 500;

            int32_t cur_a = p.max_current_ma / 1000;
            int32_t loss_mw = cur_a * cur_a * R_CABLE_MOHM;
            score -= (loss_mw / 10);

            if (score > best_score) {
                best_score = score;
                best_idx = i;
            }
        }

        if (best_idx < 0) return std::nullopt;

        const auto& chosen = pdos_[best_idx];
        RequestData req;
        req.position = chosen.position;
        req.operating_current_ma = std::min(chosen.max_current_ma, I_REQUIRED_MA);
        req.max_current_ma = chosen.max_current_ma;
        req.capability_mismatch = (chosen.max_current_ma < I_REQUIRED_MA);
        req.giveback = false;

        negotiated_mv_ = chosen.voltage_mv;
        negotiated_ma_ = req.operating_current_ma;
        return req;
    }

    void isolate_load() noexcept {
        gate_closed_ = false;
        PowerGateGuard::set(false);
    }

    void engage_load() noexcept {
        gate_closed_ = true;
        PowerGateGuard::set(true);
    }

    void fallback_safe_5v() noexcept {
        negotiated_mv_ = 5000;
        negotiated_ma_ = 500;
        engage_load();
        state_ = State::Ready;
    }

    void send_request(const RequestData& req) noexcept;
    void execute_hard_reset() noexcept;

    State state_{State::Discovery};
    uint32_t timer_ms_{0};
    uint32_t negotiated_mv_{5000};
    uint32_t negotiated_ma_{500};
    bool gate_closed_{false};
    std::array<Pdo, 7> pdos_{};
    uint8_t pdo_count_{0};
};

} // namespace usb_pd
