// nec_transceiver.hpp - Драйвер протоколу NEC на мові C++
#pragma once

#include <cstdint>
#include <optional>
#include <span>

namespace ir {

struct NecPacket {
    uint8_t address{0};
    uint8_t address_inv{0};
    uint8_t command{0};
    uint8_t command_inv{0};
    bool is_repeat{false};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (address == static_cast<uint8_t>(~address_inv)) &&
               (command == static_cast<uint8_t>(~command_inv));
    }
};

class NecDecoder {
public:
    enum class State : uint8_t {
        Idle,
        LeaderBurst,
        LeaderSpace,
        BitPulse,
        BitSpace
    };

    constexpr NecDecoder() noexcept = default;

    // Викликається в обробнику переривання захоплення входу
    void handle_edge(uint32_t timestamp_us, bool pin_state) noexcept;

    // Опитування наявності декодованого пакета в головному циклі
    [[nodiscard]] std::optional<NecPacket> pop_packet() noexcept;

    void reset() noexcept {
        state_ = State::Idle;
        raw_data_ = 0;
        bit_index_ = 0;
        ready_packet_.reset();
    }

private:
    State state_{State::Idle};
    uint32_t last_timestamp_us_{0};
    uint32_t raw_data_{0};
    uint8_t bit_index_{0};
    std::optional<NecPacket> ready_packet_{};
};

} // namespace ir
