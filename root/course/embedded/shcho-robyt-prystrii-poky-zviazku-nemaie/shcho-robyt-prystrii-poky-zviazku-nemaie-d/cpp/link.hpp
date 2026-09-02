#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "hardware.hpp"

namespace cart {

// Канал до пульта. Поки кадр не пройшов CRC, перевірку мітки автентичності,
// звірку сесії та захист від повтору — це НЕ команда: він не годує мертвої
// руки й не доходить до приводів. Причину відмови віддаємо в error()
// std::expected, а не кодом -1 десь у глобальній змінній.
enum class LinkError { Length, Type, Crc, Auth, Session, Replay, Stale };
std::string_view describe(LinkError e) noexcept;

enum class FrameType : std::uint8_t { Hello = 0x01, Command = 0x02 };

inline constexpr std::size_t kFrameSize = 24;
inline constexpr Millis kMaxCommandAge = 500ms;

using Frame = std::array<std::byte, kFrameSize>;

struct Command {
    FrameType     type{FrameType::Command};
    std::uint32_t session{0};
    std::uint32_t seq{0};
    Millis        stamp{0};   // час відправника
    float throttle{0.0f};
    float steering{0.0f};
};

class Link {
public:
    struct Rejects {
        std::uint32_t crc{0};
        std::uint32_t auth{0};
        std::uint32_t session{0};
        std::uint32_t replay{0};
        std::uint32_t stale{0};
    };

    explicit Link(std::uint32_t key) noexcept : key_{key} {}

    std::expected<Command, LinkError> accept(std::span<const std::byte> frame, Millis now) noexcept;

    // Сесія й усі відкладені команди анульовані.
    void dropSession() noexcept {
        established_ = false;
        session_ = 0;
        lastSeq_ = 0;
    }

    [[nodiscard]] bool established() const noexcept { return established_; }
    [[nodiscard]] std::uint32_t accepted() const noexcept { return accepted_; }
    [[nodiscard]] const Rejects& rejects() const noexcept { return rejects_; }

    // Бік пульта — щоб сценарій справді збирав кадри, а не підсовував структуру.
    [[nodiscard]] static Frame makeHello(std::uint32_t key, std::uint32_t session, Millis stamp) noexcept;
    [[nodiscard]] static Frame makeCommand(std::uint32_t key, std::uint32_t session, std::uint32_t seq,
                                           Millis stamp, float throttle, float steering) noexcept;

private:
    std::uint32_t key_;
    std::uint32_t session_{0};
    std::uint32_t lastSeq_{0};
    std::uint32_t accepted_{0};
    Millis clockBias_{0};   // наскільки годинник пульта попереду нашого
    bool established_{false};
    Rejects rejects_{};
};

}  // namespace cart
