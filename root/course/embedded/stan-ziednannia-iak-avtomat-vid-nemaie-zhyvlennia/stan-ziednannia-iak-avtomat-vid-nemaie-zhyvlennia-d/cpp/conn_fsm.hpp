#pragma once

#include "at_link.hpp"
#include "blackbox.hpp"
#include "modem_hal.hpp"
#include "mqtt.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

/* Стани життєвого циклу з'єднання. Порядок значущий: обробники URC
   порівнюють стани між собою («ми вже глибше за реєстрацію?»). */
enum class State : std::uint8_t {
    NoPower,
    PoweringOn,
    ModemReady,
    SimReady,
    NetSearch,
    IpAttach,
    TcpConnect,
    ProtocolAuth,
    ReadyToSend,
    Sending,
    Disconnecting,
    PsmSleep,
    Backoff,
    HwReset,
    PowerCycle,
    FatalStop
};

class ConnectionFsm {
public:
    using Clock = ModemHal::Clock;

    static constexpr std::size_t kPayloadMax = 256;

    ConnectionFsm(ModemHal& hal, AtLink& link, BlackBox& log);

    /* Квант диспетчеризації: викликати з суперциклу кожні 10–50 мс. */
    void tick();

    void connect();
    bool submit(std::span<const std::byte> payload);
    void disconnect();

    [[nodiscard]] State state() const noexcept { return m_state; }
    [[nodiscard]] bool idle() const noexcept
    {
        return m_state == State::ReadyToSend && !m_txPending && !m_logPending;
    }

private:
    void enter(State next, std::chrono::milliseconds timeout = std::chrono::milliseconds::zero());
    void armTimer(std::chrono::milliseconds timeout);
    void armPoll(std::chrono::milliseconds period);
    void txFrame(std::expected<mqtt::Frame, mqtt::Error> frame);
    void enterBackoff(State target);
    void escalate(unsigned level);
    void onMessage(const AtMessage& msg);
    void onSessionMessage(const AtMessage& msg);
    void onTimeout();

    ModemHal& m_hal;
    AtLink& m_link;
    BlackBox& m_log;

    State m_state{State::NoPower};
    State m_backoffTarget{State::NoPower};

    std::optional<Clock::time_point> m_deadline{};
    std::chrono::milliseconds m_pollPeriod{0};
    Clock::time_point m_pollLast{};

    std::uint8_t m_substep{0}; /* крок усередині стану */
    std::uint8_t m_probes{0};  /* спроби синхронізації "AT" */
    unsigned m_level{0};       /* сходинка драбини відновлення */
    unsigned m_retry{0};       /* спроб на цій сходинці */

    std::uint8_t m_lastEvent{0};
    std::uint16_t m_lastCme{0};
    std::int8_t m_rssiDbm{kRssiUnknown};

    bool m_pingPending{false};
    bool m_wantDisconnect{false};
    bool m_logPending{false};
    bool m_txPending{false};
    bool m_txIsLog{false};
    std::uint16_t m_packetId{0};

    std::array<std::byte, kPayloadMax> m_tx{}; /* навантаження в черзі */
    std::size_t m_txLen{0};
    std::array<std::byte, kPayloadMax + 64> m_out{}; /* кадр, що чекає на '>' */
    mqtt::Frame m_pending{};

    mqtt::Decoder m_mqtt{};
};
