// node.hpp — стан вузла й уся його логіка: виміряти, спакувати, виконати команду.
//
// Клас нічого не знає про сокети: він приймає розібрану команду й повертає
// квитанцію значенням. Тому його поведінку видно з коду без запуску мережі.
#pragma once

#include <algorithm>
#include <random>

#include "protocol.hpp"

namespace field {

class EdgeNode {
public:
    explicit EdgeNode(std::uint16_t id) : node_id_(id), rng_(std::random_device{}()) {}

    [[nodiscard]] std::uint16_t id() const noexcept { return node_id_; }
    [[nodiscard]] bool relay_on() const noexcept { return flags_.relay_on; }

    // Замість АЦП — блукання довкола 22.00 °C і повільний розряд елемента.
    [[nodiscard]] Telemetry sample() {
        std::uniform_int_distribution<int> drift(-20, 20);
        std::uniform_int_distribution<int> fault(0, 49);
        std::uniform_int_distribution<int> drain(0, 1);

        temp_c100_ = static_cast<std::int16_t>(std::clamp(temp_c100_ + drift(rng_), 1000, 3500));
        if (battery_mv_ > 3000) {
            battery_mv_ = static_cast<std::uint16_t>(battery_mv_ - drain(rng_));
        }
        flags_.sensor_fault = fault(rng_) == 0;

        return Telemetry{node_id_, ++seq_, temp_c100_, battery_mv_, flags_};
    }

    // nullopt — команда адресована сусідові, відповідати не наше діло.
    [[nodiscard]] std::optional<Ack> apply(const Command& cmd) {
        if (cmd.node_id != node_id_) {
            return std::nullopt;
        }

        AckStatus status = AckStatus::UnknownCommand;
        if (cmd.id == CommandId::SetRelay) {
            if (cmd.value <= 1) {
                flags_.relay_on = cmd.value != 0;
                status = AckStatus::Ok;
            } else {
                status = AckStatus::BadValue;
            }
        }

        // Квитанція несе стан ПІСЛЯ застосування — саме він стає
        // підтвердженим станом цифрового двійника на шлюзі.
        return Ack{node_id_, cmd.seq, static_cast<std::uint8_t>(cmd.id), status, flags_};
    }

private:
    std::uint16_t node_id_;
    std::uint32_t seq_{0};
    std::int16_t temp_c100_{2200};
    std::uint16_t battery_mv_{3300};
    Flags flags_{};
    std::mt19937 rng_;
};

}  // namespace field
