#include <cstdint>
#include <string_view>
#include <chrono>
#include <optional>
#include <random>

/* Інтерфейс апаратного драйвера модема (C++ RAII/HAL) */
class IModemHal {
public:
    virtual ~IModemHal() = default;
    virtual void setPower(bool enable) = 0;
    virtual void pulsePwrkey() = 0;
    virtual void sendCommand(std::string_view cmd) = 0;
    virtual uint32_t getRandom(uint32_t min, uint32_t max) = 0;
};

/* Скінченний автомат з'єднання на C++20 */
class ConnectionStateMachine {
public:
    enum class State : uint8_t {
        NoPower,
        PoweringOn,
        ModemReady,
        SimReady,
        NetSearch,
        IpAttach,
        TcpConnect,
        ReadyToSend,
        Sending,
        BackoffWait,
        ErrorRecovery
    };

    enum class Event : uint8_t {
        None,
        StartConnect,
        Timeout,
        AtOk,
        AtError,
        NetRegistered,
        NetDenied,
        IpAllocated,
        TcpConnected,
        SocketClosed,
        TxSuccess
    };

    explicit ConnectionStateMachine(IModemHal& hal)
        : m_hal(hal), m_state(State::NoPower) {}

    [[nodiscard]] State getState() const noexcept { return m_state; }

    void tick(std::chrono::milliseconds now, Event incomingEvent = Event::None) {
        if (m_timeout.has_value() && now >= m_timeout.value()) {
            incomingEvent = Event::Timeout;
            m_timeout.reset();
        }

        switch (m_state) {
            case State::NoPower:
                if (incomingEvent == Event::StartConnect) {
                    m_hal.setPower(true);
                    m_hal.pulsePwrkey();
                    transitionTo(State::PoweringOn, now + std::chrono::milliseconds(3000));
                }
                break;

            case State::PoweringOn:
                if (incomingEvent == Event::Timeout) {
                    m_hal.sendCommand("ATE0\r\n");
                    transitionTo(State::ModemReady, now + std::chrono::milliseconds(1000));
                }
                break;

            case State::ModemReady:
                if (incomingEvent == Event::AtOk) {
                    m_retryCount = 0;
                    m_hal.sendCommand("AT+CPIN?\r\n");
                    transitionTo(State::SimReady, now + std::chrono::milliseconds(5000));
                } else if (incomingEvent == Event::Timeout || incomingEvent == Event::AtError) {
                    if (++m_retryCount >= kMaxRetries) {
                        transitionTo(State::ErrorRecovery, std::nullopt);
                    } else {
                        m_hal.sendCommand("AT\r\n");
                        transitionTo(State::ModemReady, now + std::chrono::milliseconds(1000));
                    }
                }
                break;

            case State::SimReady:
                if (incomingEvent == Event::AtOk) {
                    m_retryCount = 0;
                    m_hal.sendCommand("AT+CREG=1\r\n");
                    transitionTo(State::NetSearch, now + std::chrono::milliseconds(60000));
                } else if (incomingEvent == Event::Timeout || incomingEvent == Event::AtError) {
                    enterBackoff(State::ModemReady, now);
                }
                break;

            case State::NetSearch:
                if (incomingEvent == Event::NetRegistered) {
                    m_retryCount = 0;
                    m_hal.sendCommand("AT+CGATT=1\r\n");
                    transitionTo(State::IpAttach, now + std::chrono::milliseconds(30000));
                } else if (incomingEvent == Event::Timeout || incomingEvent == Event::NetDenied) {
                    if (++m_retryCount >= kMaxRetries) {
                        transitionTo(State::ErrorRecovery, std::nullopt);
                    } else {
                        enterBackoff(State::NetSearch, now);
                    }
                }
                break;

            case State::IpAttach:
                if (incomingEvent == Event::IpAllocated) {
                    m_retryCount = 0;
                    m_hal.sendCommand("AT+CIPSTART=\"TCP\",\"broker.local\",1883\r\n");
                    transitionTo(State::TcpConnect, now + std::chrono::milliseconds(20000));
                } else if (incomingEvent == Event::Timeout) {
                    enterBackoff(State::IpAttach, now);
                }
                break;

            case State::TcpConnect:
                if (incomingEvent == Event::TcpConnected) {
                    m_retryCount = 0;
                    transitionTo(State::ReadyToSend, std::nullopt);
                } else if (incomingEvent == Event::Timeout || incomingEvent == Event::AtError) {
                    if (++m_retryCount >= kMaxRetries) {
                        enterBackoff(State::IpAttach, now);
                    } else {
                        enterBackoff(State::TcpConnect, now);
                    }
                }
                break;

            case State::ReadyToSend:
                if (incomingEvent == Event::SocketClosed) {
                    transitionTo(State::TcpConnect, now + std::chrono::milliseconds(100));
                }
                break;

            case State::BackoffWait:
                if (incomingEvent == Event::Timeout) {
                    transitionTo(m_rollbackTarget, now + std::chrono::milliseconds(100));
                }
                break;

            case State::ErrorRecovery:
                m_hal.setPower(false);
                m_retryCount = 0;
                transitionTo(State::NoPower, now + std::chrono::milliseconds(5000));
                break;
        }
    }

private:
    static constexpr uint8_t kMaxRetries = 3;
    static constexpr uint32_t kBaseBackoffMs = 2000;

    IModemHal& m_hal;
    State m_state;
    State m_rollbackTarget{State::NoPower};
    uint8_t m_retryCount{0};
    std::optional<std::chrono::milliseconds> m_timeout{std::nullopt};

    void transitionTo(State next, std::optional<std::chrono::milliseconds> timeout) {
        m_state = next;
        m_timeout = timeout;
    }

    void enterBackoff(State target, std::chrono::milliseconds now) {
        uint32_t maxInterval = kBaseBackoffMs * (1U << m_retryCount);
        if (maxInterval > 300000) maxInterval = 300000;

        uint32_t jitterMs = m_hal.getRandom(500, maxInterval);
        m_rollbackTarget = target;
        transitionTo(State::BackoffWait, now + std::chrono::milliseconds(jitterMs));
    }
};
