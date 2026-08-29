#pragma once

#include "link_quality.hpp"
#include "qos_queue.hpp"

#include <array>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace linkmux {

enum class BearerId : std::uint8_t { Primary = 0, Fallback = 1 };
inline constexpr std::size_t kBearerCount = 2;

enum class RadioMode : std::uint8_t {
    Active,   // підсилювач гріється, приймач слухає
    Listen,   // підсилювач вимкнено, приймач слухає
    Sleep     // усе вимкнено: пауза чергового прийому
};

enum class TxError : std::uint8_t {
    Blackout,
    PayloadTooLarge,
    NoBandwidth,
    QueueFull,
    HardwareFault
};

// Контракт драйвера трансивера — усе, чого арбітр потребує від заліза
class Transceiver {
public:
    virtual ~Transceiver() = default;

    [[nodiscard]] virtual std::expected<std::size_t, TxError> send(const Frame& frame) noexcept = 0;
    virtual void setMode(RadioMode mode) noexcept = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual Millis airTime() const noexcept = 0;   // час кадру в ефірі
    [[nodiscard]] virtual Millis slot() const noexcept = 0;      // період вхідних кадрів
};

enum class ArbiterState : std::uint8_t {
    PrimaryActive,
    FallbackActive,
    RecoveryEvaluation,
    Blackout
};

std::string_view stateName(ArbiterState state) noexcept;
std::string_view modeName(RadioMode mode) noexcept;

class MultiLinkArbiter {
public:
    // Асиметрія навмисна: падаємо на резерв за десятки мілісекунд, вертаємось
    // на основний лише після п'яти секунд безперервної стабільності.
    static constexpr std::uint8_t kFailoverPer = 25;
    static constexpr std::uint8_t kRecoveryPer = 5;
    static constexpr Millis kPrimarySilence{200};
    static constexpr Millis kFallbackSilence{3000};
    static constexpr Millis kHysteresisDwell{5000};
    static constexpr Millis kSniffPeriod{500};
    static constexpr Millis kSniffWindow{10};

    MultiLinkArbiter(Transceiver& primary, Transceiver& fallback, Millis now) noexcept;

    void onFrameReceived(BearerId id, const Frame& frame, Millis now) noexcept;
    void update(Millis now) noexcept;
    std::expected<void, TxError> routePacket(Priority prio, std::span<const std::uint8_t> data,
                                        Millis now) noexcept;
    std::size_t pump(Millis now) noexcept;

    [[nodiscard]] ArbiterState state() const noexcept { return state_; }
    [[nodiscard]] BearerId activeBearer() const noexcept { return active_; }
    [[nodiscard]] const LinkQuality& quality(BearerId id) const noexcept;
    [[nodiscard]] std::string_view bearerName(BearerId id) const noexcept;
    [[nodiscard]] std::uint32_t txFrames(BearerId id) const noexcept;
    [[nodiscard]] std::uint32_t txErrors(BearerId id) const noexcept;
    [[nodiscard]] std::uint32_t dropped(Priority prio) const noexcept { return queues_.dropped(prio); }
    [[nodiscard]] std::uint32_t switches() const noexcept { return switches_; }

private:
    struct Bearer {
        Transceiver&  radio;
        LinkQuality   quality;
        RadioMode     mode{RadioMode::Sleep};
        Millis        freeAt{0};
        std::uint32_t txFrames{0};
        std::uint32_t txErrors{0};
    };

    Bearer& bearer(BearerId id) noexcept { return bearers_[static_cast<std::size_t>(id)]; }
    const Bearer& bearer(BearerId id) const noexcept { return bearers_[static_cast<std::size_t>(id)]; }

    static void setMode(Bearer& b, RadioMode mode) noexcept;
    void enterState(ArbiterState next, Millis now) noexcept;
    void sniffTick(Millis now) noexcept;
    void duplicateCritical(const Frame& frame, Millis now) noexcept;

    std::array<Bearer, kBearerCount> bearers_;
    TxQueues      queues_{};
    ArbiterState  state_{ArbiterState::PrimaryActive};
    BearerId      active_{BearerId::Primary};
    Millis        stateSince_{0};
    Millis        sniffNext_{0};
    bool          sniffOpen_{false};
    std::uint16_t txSeq_{0};
    std::uint32_t switches_{0};
};

}  // namespace linkmux
