// receiver.hpp — автомат приймача Stop-and-Wait.
//
// Уся пам'ять приймача — один байт expected_. Черг, буферів переупорядкування
// й динамічної алокації тут немає й бути не може.
#pragma once

#include "frame.hpp"

#include <array>
#include <cstdint>
#include <functional>
#include <optional>
#include <span>
#include <utility>

namespace arq {

class Receiver {
public:
    using WireOut = std::function<void(std::span<const std::uint8_t>)>;
    using Deliver = std::function<void(std::span<const std::uint8_t>)>;

    struct Stats {
        unsigned delivered{};
        unsigned duplicates{};
        unsigned corrupted{};
        unsigned ignored{};
    };

    Receiver(WireOut out, Deliver deliver)
        : out_{std::move(out)}, deliver_{std::move(deliver)} {}

    void onWire(std::span<const std::uint8_t> wire)
    {
        const auto frame = decode(wire);
        if (!frame) {
            ++stats_.corrupted;
            lastError_ = frame.error();
            // Номер побитого кадру невідомий (він і сам міг бути спотворений),
            // тому просимо повторити той кадр, якого чекаємо.
            sendControl(Type::Nack, expected_);
            return;
        }

        if (frame->type() != Type::Data) {
            ++stats_.ignored; // приймач сам квитанцій не чекає
            return;
        }

        if (frame->seq() == expected_) {
            ++stats_.delivered;
            if (deliver_) {
                deliver_(frame->payload());
            }
            expected_ ^= 1u;
        } else {
            // Дублікат: наш ACK загубився на зворотному шляху. Додатку дані
            // вдруге НЕ віддаємо — інакше «зупинити привід» виконається двічі.
            ++stats_.duplicates;
        }

        // Квитуємо в обох випадках: і свіжий кадр, і повтор. Мовчання на
        // дублікат залишило б передавача заблокованим до вичерпання спроб.
        sendControl(Type::Ack, frame->seq());
    }

    [[nodiscard]] std::uint8_t expectedSeq() const noexcept { return expected_; }
    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }
    [[nodiscard]] std::optional<DecodeError> lastError() const noexcept { return lastError_; }

private:
    void sendControl(Type type, std::uint8_t seq)
    {
        const auto ctrl = Frame::make(type, seq, std::span<const std::uint8_t>{});
        if (!ctrl) {
            return;
        }
        std::array<std::uint8_t, kCtrlFrame> buffer{};
        const auto wire = encode(*ctrl, buffer);
        if (wire && out_) {
            out_(*wire);
        }
    }

    WireOut      out_;
    Deliver      deliver_;
    std::uint8_t expected_{0};
    Stats        stats_{};
    std::optional<DecodeError> lastError_{};
};

} // namespace arq
