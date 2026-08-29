#pragma once

#include <concepts>
#include <cstddef>
#include <cstdint>
#include <functional>

#include "node_state.hpp"
#include "telemetry_queue.hpp"

namespace iot {

enum class Link : std::uint8_t { Disconnected, Connecting, Connected, Syncing };

/*
 * Агент розподіленого стану: тримає desired (хоче хмара), active (залито в залізо)
 * і reported (про що вузол відзвітував), боронить залізо від застарілих і
 * небезпечних дельт та переживає обрив каналу офлайн-буфером телеметрії.
 */
class ShadowAgent {
public:
    explicit ShadowAgent(const NodeConfig& boot) noexcept;

    /* Прийом дельти з топіка .../shadow/update/delta. */
    [[nodiscard]] std::expected<void, DeltaError> applyDelta(const ConfigDelta& delta) noexcept;

    /* Що ще не доїхало до заліза (desired проти active). */
    [[nodiscard]] ConfigDelta pending() const noexcept;

    /* Запис у драйвери; повертає те, що справді записано. */
    ConfigDelta reconcileHardware() noexcept;

    void setLink(Link state) noexcept { link_ = state; }
    [[nodiscard]] Link link() const noexcept { return link_; }

    void recordTelemetry(TelemetryEntry entry) noexcept;

    /*
     * Дренаж офлайн-буфера. publish повертає false, коли вікно зв'язку скінчилося —
     * непереданий звіт лишається в черзі й поїде наступного разу.
     */
    template <std::predicate<const TelemetryEntry&> Publisher>
    std::size_t drainTelemetry(Publisher&& publish)
    {
        if (link_ != Link::Connected && link_ != Link::Syncing) {
            return 0; /* каналу немає — черга просто чекає далі */
        }

        std::size_t sent = 0;
        while (const TelemetryEntry* item = queue_.front()) {
            if (!std::invoke(publish, *item)) {
                break;
            }
            queue_.pop();
            ++sent;
        }
        return sent;
    }

    [[nodiscard]] const NodeConfig& desired() const noexcept { return desired_; }
    [[nodiscard]] const NodeConfig& active() const noexcept { return active_; }
    [[nodiscard]] const NodeConfig& reported() const noexcept { return reported_; }

    [[nodiscard]] bool reportedDirty() const noexcept { return reportedDirty_; }
    void markReportedSent() noexcept { reportedDirty_ = false; }

    [[nodiscard]] std::size_t bufferedCount() const noexcept { return queue_.size(); }
    [[nodiscard]] std::uint32_t droppedCount() const noexcept { return queue_.droppedTotal(); }
    [[nodiscard]] std::uint32_t staleRejected() const noexcept { return staleRejected_; }
    [[nodiscard]] std::uint32_t rangeRejected() const noexcept { return rangeRejected_; }

private:
    NodeConfig desired_{};
    NodeConfig active_{};
    NodeConfig reported_{};
    TelemetryQueue<32> queue_{};
    Link link_{Link::Disconnected};
    bool reportedDirty_{false};
    std::uint32_t staleRejected_{0};
    std::uint32_t rangeRejected_{0};
};

} // namespace iot
