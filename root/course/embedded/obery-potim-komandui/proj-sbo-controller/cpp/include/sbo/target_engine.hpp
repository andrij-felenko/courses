// target_engine.hpp — бортовий автомат SBO та контракт плати, на яку він спирається.
#pragma once

#include "sbo/protocol.hpp"

#include <chrono>

namespace sbo {

enum class DiagLine : std::uint8_t {
    Armed,          // рівень: високий, поки вузол зведено
    OperateExec,    // імпульс 10 мкс: команду пропущено до приводу
    SecurityDrop    // імпульс 50 мкс: кадр відкинуто валідатором
};

// Усе, що ядру потрібно від заліза. Плата реалізує це поверх GPIO й драйверів,
// тест — поверх лічильників; ядро не знає про жодне з двох.
class Board {
public:
    virtual ~Board() = default;
    virtual bool execute(CommandCode cmd, std::span<const std::uint8_t> payload) noexcept = 0;
    virtual void diag_level(DiagLine line, bool high) noexcept = 0;
    virtual void diag_pulse(DiagLine line, std::chrono::microseconds width) noexcept = 0;
};

class TargetEngine {
public:
    using Clock     = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    // Після кожного старту (у тому числі після brownout-скидання) вузол — Idle,
    // а зерно генератора нове: токен у Flash не зберігається ніколи.
    TargetEngine(NodeId self, Board& board, std::uint32_t seed) noexcept;

    // true — замок щойно знято таймером. Викликати кожні 10..50 мс.
    bool tick(TimePoint now) noexcept;

    // Значення — кадр, який треба відіслати (у тому числі NACK із причиною
    // в payload[0]); помилка — «відповідати нема чого», кадр просто зникає.
    [[nodiscard]] std::expected<Frame, Error> process(const Frame& rx, TimePoint now) noexcept;

    // Вхід із радіоканалу: байти → валідатор → автомат → байти відповіді.
    [[nodiscard]] std::expected<std::span<std::uint8_t>, Error>
    handle_wire(std::span<const std::uint8_t> in, std::span<std::uint8_t> out, TimePoint now) noexcept;

    [[nodiscard]] State  state() const noexcept { return state_; }
    [[nodiscard]] NodeId id() const noexcept { return self_; }
    [[nodiscard]] std::uint16_t select_count() const noexcept { return select_count_; }
    [[nodiscard]] std::uint16_t exec_count() const noexcept { return exec_count_; }
    [[nodiscard]] std::uint16_t timeout_count() const noexcept { return timeout_count_; }

private:
    [[nodiscard]] Frame response(const Frame& rx, MessageType type) const noexcept;
    [[nodiscard]] Frame nack(const Frame& rx, MessageType type, Error err) noexcept;
    void  disarm() noexcept;
    Token next_token(TimePoint now) noexcept;

    NodeId        self_;
    Board&        board_;
    State         state_{State::Idle};
    NodeId        locked_source_{};
    CommandCode   locked_command_{};
    Token         active_token_{};
    TimePoint     arm_expiry_{};
    std::uint32_t prng_seed_;
    std::uint16_t select_count_{0};
    std::uint16_t exec_count_{0};
    std::uint16_t reject_count_{0};
    std::uint16_t timeout_count_{0};
};

}  // namespace sbo
