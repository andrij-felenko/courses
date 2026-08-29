#include "mission.hpp"

#include <cmath>
#include <cstddef>

namespace fm {
namespace {

constexpr double kEarthRadiusM = 6371000.0;
constexpr double kDegToRad     = 0.017453292519943295;

void crcByte(std::uint16_t& crc, std::byte value) noexcept
{
    // CRC-16/CCITT-FALSE: поліном 0x1021, початкове значення 0xFFFF.
    crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint8_t>(value) << 8);
    for (int bit = 0; bit < 8; ++bit) {
        crc = static_cast<std::uint16_t>((crc & 0x8000U) ? ((crc << 1) ^ 0x1021U) : (crc << 1));
    }
}

/* Сума береться полями, а не одним блоком структури: вирівнювання лишає в ній
   дірки, вміст яких у різних збірках різний — сума б пливла. */
template <typename T>
void crcField(std::uint16_t& crc, const T& field) noexcept
{
    for (std::byte b : std::as_bytes(std::span<const T, 1>{&field, 1})) {
        crcByte(crc, b);
    }
}

}  // namespace

NedOffset geoOffset(GeoPoint from, GeoPoint to) noexcept
{
    const double latA = static_cast<double>(from.lat1e7) * 1e-7;
    const double latB = static_cast<double>(to.lat1e7) * 1e-7;
    const double dLat = (latB - latA) * kDegToRad;
    // Довжина градуса довготи стискається косинусом широти — без цього множника
    // план у Скандинавії проходив би геозону, якої фактично не проходить.
    const double dLon = (static_cast<double>(to.lon1e7 - from.lon1e7) * 1e-7) * kDegToRad
                      * std::cos(0.5 * (latA + latB) * kDegToRad);

    return NedOffset{static_cast<float>(dLat * kEarthRadiusM),
                     static_cast<float>(dLon * kEarthRadiusM)};
}

float geoDistance(GeoPoint from, GeoPoint to) noexcept
{
    const NedOffset d = geoOffset(from, to);

    return std::hypot(d.north, d.east);
}

std::string_view describe(MissionError error) noexcept
{
    switch (error) {
    case MissionError::Empty:       return "mission empty";
    case MissionError::CrcMismatch: return "mission CRC mismatch";
    case MissionError::BadAltitude: return "mission altitude out of range";
    case MissionError::OutOfFence:  return "waypoint outside fence";
    case MissionError::BadCommand:  return "unknown mission command";
    }
    return "mission state unknown";
}

bool MissionPlan::add(const Waypoint& wp)
{
    if (items_.size() >= kMaxItems) {
        return false;
    }
    items_.push_back(wp);
    return true;
}

void MissionPlan::clear() noexcept
{
    items_.clear();
    storedCrc_ = 0;
}

std::uint16_t MissionPlan::crc() const noexcept
{
    std::uint16_t value = 0xFFFFU;

    for (const Waypoint& wp : items_) {
        crcField(value, wp.at.lat1e7);
        crcField(value, wp.at.lon1e7);
        crcField(value, wp.altRelM);
        crcField(value, wp.command);
    }
    return value;
}

std::expected<void, MissionError> MissionPlan::validate(GeoPoint home,
                                                        float fenceRadiusM,
                                                        float maxAltM) const
{
    if (items_.empty()) {
        return std::unexpected(MissionError::Empty);
    }
    if (crc() != storedCrc_) {
        return std::unexpected(MissionError::CrcMismatch);
    }

    for (const Waypoint& wp : items_) {
        if (wp.command == 0) {
            return std::unexpected(MissionError::BadCommand);
        }
        if (std::isnan(wp.altRelM) || wp.altRelM <= 0.0F || wp.altRelM > maxAltM) {
            return std::unexpected(MissionError::BadAltitude);
        }
        if (wp.at.lat1e7 == 0 && wp.at.lon1e7 == 0) {
            // Нульова координата — типовий слід недоотриманого пакета плану.
            return std::unexpected(MissionError::OutOfFence);
        }
        if (geoDistance(home, wp.at) > fenceRadiusM) {
            return std::unexpected(MissionError::OutOfFence);
        }
    }
    return {};
}

}  // namespace fm
