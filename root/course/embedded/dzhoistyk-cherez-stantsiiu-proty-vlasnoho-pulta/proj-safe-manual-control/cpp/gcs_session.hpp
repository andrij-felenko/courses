#pragma once

#include "arbiter.hpp"
#include "mavlink_codec.hpp"

#include <array>
#include <cstdint>
#include <span>

namespace manual_control {

/* Радіоміст «наземна станція — борт»: розбирає байти з UART радіомодема,
 * відсіює чужі станції й чужі адреси і годує арбітра.
 *
 * Бар'єр 4 живе тут: HEARTBEAT оновлює ЛИШЕ власну мітку часу й до арбітра
 * не доходить. Станція із завислим вікном джойстика далі шле серцебиття 1 Гц —
 * якби воно заходило в арбітра, таймаут ніколи б не спрацював. */

inline constexpr Millis kGcsRelatch{3000};  // після такої тиші можна фіксувати іншу станцію

class GcsSession {
public:
    struct Stats {
        std::uint32_t manual{};
        std::uint32_t heartbeats{};
        std::uint32_t foreign{};      // пакети від незафіксованої станції
        std::uint32_t wrongTarget{};  // адресовані не нам
        std::uint32_t armCommands{};
    };

    GcsSession(Arbiter& arbiter, std::uint8_t sysid, std::uint8_t compid) noexcept
        : arbiter_{arbiter}, ourSysid_{sysid}, ourCompid_{compid} {}

    void consume(std::span<const std::byte> bytes, Millis now) noexcept;

    // Порожній span — відповідати нічим.
    [[nodiscard]] std::span<const std::byte> takeAck() noexcept;

    [[nodiscard]] const Stats& stats() const noexcept { return stats_; }
    [[nodiscard]] const mavlink::Parser::Stats& linkStats() const noexcept { return parser_.stats(); }
    [[nodiscard]] Millis lastHeartbeat() const noexcept { return lastHeartbeat_; }

private:
    void onHeartbeat(const mavlink::Frame& f, Millis now) noexcept;
    void onManualControl(const mavlink::ManualControl& mc, const mavlink::Frame& f, Millis now) noexcept;
    void onCommandLong(const mavlink::CommandLong& cl, const mavlink::Frame& f, Millis now) noexcept;
    void queueAck(std::uint16_t command, mavlink::Result result) noexcept;

    [[nodiscard]] bool fromOurGcs(const mavlink::Frame& f) const noexcept
    {
        return gcsSysid_ != 0 && f.sysid == gcsSysid_;
    }

    Arbiter&     arbiter_;
    std::uint8_t ourSysid_;
    std::uint8_t ourCompid_;

    std::uint8_t gcsSysid_{0};  // 0 — авторизованої станції ще немає
    std::uint8_t gcsCompid_{0};
    Millis       lastGcsFrame_{0};
    Millis       lastHeartbeat_{0};

    mavlink::Parser parser_{};
    std::uint8_t    txSeq_{0};

    std::array<std::byte, 32> ack_{};
    std::size_t               ackLen_{0};

    Stats stats_{};
};

}  // namespace manual_control
