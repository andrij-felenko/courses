// Бортовий вузол: скінченний автомат селектора з розділу 3 профілю.
#pragma once

#include "protocol.hpp"

#include <array>
#include <optional>

namespace sbo {

class Node {
public:
    // Стан приводів, який чіпають критичні команди. У прошивці на його місці
    // регістри ESC, реле скидача та прапорці автопілота.
    struct Actuators {
        bool motors_live{true};
        bool armed{true};
        bool reboot_pending{false};
        bool params_default{false};
        bool payload_dropped{false};   // одноразовий замок скидача
        std::uint8_t flight_mode{0};
        bool healthy{true};            // кінцевик або перегрів
    };

    Node(std::uint8_t id, std::uint32_t seed);

    // Старіння замка: з періодичної задачі й перед розбором кожного кадру.
    void tick(Ms now);

    // nullopt — відповіді в ефір немає: кадр битий, чужий або відкинутий
    // фільтром безпеки.
    [[nodiscard]] std::optional<Frame> handle(std::span<const std::uint8_t> raw, Ms now);

    [[nodiscard]] State state() const noexcept;
    [[nodiscard]] Ms remaining(Ms now) const noexcept;
    [[nodiscard]] std::uint8_t heartbeat_flags() const noexcept { return flags_; }
    [[nodiscard]] std::uint32_t security_drops() const noexcept { return security_drops_; }
    [[nodiscard]] std::uint32_t rx_errors() const noexcept { return rx_errors_; }
    [[nodiscard]] const Actuators& actuators() const noexcept { return act_; }

    void set_healthy(bool ok) noexcept { act_.healthy = ok; }

private:
    struct Lock {
        std::uint8_t owner;
        Comp comp;
        Cmd cmd;
        std::uint32_t token;
        Ms deadline;
    };

    std::optional<Frame> on_select(const Frame& req, Ms now);
    std::optional<Frame> on_operate(const Frame& req, Ms now);
    std::optional<Frame> on_cancel(const Frame& req, Ms now);
    std::optional<Frame> on_ping(const Frame& req, Ms now);

    std::expected<void, Error> execute(Cmd cmd, std::span<const std::uint8_t> params);

    Frame reply(const Frame& req, MsgType type, std::uint32_t token, Ms window,
                std::optional<Error> reason);
    Frame nack(const Frame& req, MsgType type, Error reason);

    void release(Ms now, bool expired);
    std::uint32_t next_token();

    std::uint8_t id_;
    std::uint8_t seq_{0};
    std::uint32_t rng_;
    std::uint8_t flags_{0};

    std::optional<Lock> lock_{};
    bool executing_{false};
    std::uint32_t expired_token_{0};
    Ms cooldown_until_{0};

    std::uint32_t security_drops_{0};
    std::uint32_t rx_errors_{0};

    std::array<std::uint8_t, 4> password_{'S', 'B', 'O', '!'};
    Actuators act_{};
};

}  // namespace sbo
