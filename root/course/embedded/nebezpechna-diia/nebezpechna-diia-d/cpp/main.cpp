#include <cstdint>
#include <chrono>
#include <functional>
#include <optional>

class SafetyInterlock {
public:
    enum class State : uint8_t {
        SafeIdle = 0,
        ArmedLatch,
        HoldProgress,
        CountdownGrace,
        Triggered,
        Aborted
    };

    struct Config {
        std::chrono::milliseconds armWindow{5000};
        std::chrono::milliseconds holdRequired{3000};
        std::chrono::milliseconds graceCountdown{2000};
        std::function<void()> onExecute{};
        std::function<void(State)> onStateChange{};
    };

    explicit SafetyInterlock(Config config)
        : m_config(std::move(config)) {}

    void arm() noexcept {
        if (m_state == State::SafeIdle) {
            m_state = State::ArmedLatch;
            m_token = TokenArmed;
            m_timer = m_config.armWindow;
            m_holdAccum = std::chrono::milliseconds::zero();
            notifyStateChange(m_state);
        }
    }

    void abort() noexcept {
        m_state = State::SafeIdle;
        m_token = TokenDisarmed;
        m_timer = std::chrono::milliseconds::zero();
        m_holdAccum = std::chrono::milliseconds::zero();
        m_buttonPressed = false;
        notifyStateChange(State::Aborted);
    }

    void setButtonState(bool pressed) noexcept {
        m_buttonPressed = pressed;
    }

    void tick(std::chrono::milliseconds dt) noexcept {
        switch (m_state) {
        case State::SafeIdle:
            m_token = TokenDisarmed;
            m_holdAccum = std::chrono::milliseconds::zero();
            break;

        case State::ArmedLatch:
            if (m_token != TokenArmed) {
                abort();
                return;
            }
            if (m_buttonPressed) {
                m_state = State::HoldProgress;
                m_holdAccum = std::chrono::milliseconds::zero();
                notifyStateChange(m_state);
            } else {
                if (m_timer <= dt) {
                    abort();
                } else {
                    m_timer -= dt;
                }
            }
            break;

        case State::HoldProgress:
            if (m_token != TokenArmed || !m_buttonPressed) {
                abort();
                return;
            }
            m_holdAccum += dt;
            if (m_holdAccum >= m_config.holdRequired) {
                if (m_config.graceCountdown > std::chrono::milliseconds::zero()) {
                    m_state = State::CountdownGrace;
                    m_timer = m_config.graceCountdown;
                    notifyStateChange(m_state);
                } else {
                    executeAction();
                }
            }
            break;

        case State::CountdownGrace:
            if (m_timer <= dt) {
                executeAction();
            } else {
                m_timer -= dt;
            }
            break;

        default:
            abort();
            break;
        }
    }

    [[nodiscard]] State state() const noexcept { return m_state; }

    [[nodiscard]] float holdProgress() const noexcept {
        if (m_state != State::HoldProgress || m_config.holdRequired.count() == 0) {
            return 0.0f;
        }
        float p = static_cast<float>(m_holdAccum.count()) / static_cast<float>(m_config.holdRequired.count());
        return (p > 1.0f) ? 1.0f : p;
    }

    [[nodiscard]] std::chrono::milliseconds remainingGraceTime() const noexcept {
        return (m_state == State::CountdownGrace) ? m_timer : std::chrono::milliseconds::zero();
    }

private:
    static constexpr uint16_t TokenDisarmed = 0x0000;
    static constexpr uint16_t TokenArmed    = 0x5A5A;
    static constexpr uint16_t TokenExecute  = 0xA5A5;

    void executeAction() {
        m_state = State::Triggered;
        m_token = TokenExecute;
        notifyStateChange(m_state);
        if (m_config.onExecute) {
            m_config.onExecute();
        }
        abort();
    }

    void notifyStateChange(State s) {
        if (m_config.onStateChange) {
            m_config.onStateChange(s);
        }
    }

    Config m_config;
    State m_state{State::SafeIdle};
    uint16_t m_token{TokenDisarmed};
    std::chrono::milliseconds m_timer{0};
    std::chrono::milliseconds m_holdAccum{0};
    bool m_buttonPressed{false};
};
