#pragma once

#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <vector>

#include "telemetry.hpp"

namespace fm {

/* Зміщення в місцевій системі Північ-Схід, метри. */
struct NedOffset {
    float north{};
    float east{};
};

[[nodiscard]] NedOffset geoOffset(GeoPoint from, GeoPoint to) noexcept;
[[nodiscard]] float     geoDistance(GeoPoint from, GeoPoint to) noexcept;

struct Waypoint {
    GeoPoint      at{};
    float         altRelM{};
    std::uint16_t command{};   // код MAV_CMD
};

enum class MissionError : std::uint8_t {
    Empty,
    CrcMismatch,
    BadAltitude,
    OutOfFence,
    BadCommand
};

[[nodiscard]] std::string_view describe(MissionError error) noexcept;

/* План місії з власною валідацією. Клас, а не структура з полями назовні:
   контрольна сума й точки мусять мінятися разом, інакше «валідний план»
   означає лише «хтось не забув перерахувати CRC». */
class MissionPlan {
public:
    static constexpr std::size_t kMaxItems = 64;

    bool add(const Waypoint& wp);          // false — буфер повний
    void clear() noexcept;
    void setStoredCrc(std::uint16_t crc) noexcept { storedCrc_ = crc; }

    [[nodiscard]] std::uint16_t crc() const noexcept;
    [[nodiscard]] std::uint16_t storedCrc() const noexcept { return storedCrc_; }
    [[nodiscard]] std::span<const Waypoint> items() const noexcept { return items_; }
    [[nodiscard]] bool empty() const noexcept { return items_.empty(); }

    /* Непорожній, сума збігається, висоти в межах стелі, усі точки — в радіусі
       геозони від точки старту. */
    [[nodiscard]] std::expected<void, MissionError> validate(GeoPoint home,
                                                             float fenceRadiusM,
                                                             float maxAltM) const;

private:
    std::vector<Waypoint> items_;
    std::uint16_t         storedCrc_{};
};

}  // namespace fm
