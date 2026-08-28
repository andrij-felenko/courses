// geoid.hpp — та сама сітка, але межі буфера й одиниці стереже тип.
// C++23: <span> і <expected>.
#pragma once
#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace geo {

enum class GridError { badMagic, badSize, badStep };

// Окремі типи замість голих int32. Переставити місцями широту з довготою
// або підставити сантиметри туди, де чекають міліметри, компілятор не дасть —
// а саме ці дві помилки в геодезичному коді трапляються найчастіше.
struct Lat        { std::int32_t e7; };   // широта,  1e−7 градуса, як у MAVLink
struct Lon        { std::int32_t e7; };   // довгота, так само
struct Centimetre { std::int32_t v; };
struct Millimetre { std::int32_t v; };

class Geoid {
public:
    // Довжина буфера приїздить разом із вказівником — окремого len, який
    // можна передати не той, більше не існує.
    static std::expected<Geoid, GridError> open(std::span<const std::byte> blob) noexcept
    {
        if (blob.size() < kHeader) return std::unexpected(GridError::badSize);
        if (blob[0] != std::byte{'G'} || blob[1] != std::byte{'U'} ||
            blob[2] != std::byte{'N'} || blob[3] != std::byte{'1'})
            return std::unexpected(GridError::badMagic);

        const std::uint32_t nlat = rd16(blob, 4);
        const std::uint32_t nlon = rd16(blob, 6);
        if (nlat < 2 || nlon < 2) return std::unexpected(GridError::badSize);
        if (blob.size() - kHeader != std::size_t{nlat} * nlon * 2)
            return std::unexpected(GridError::badSize);

        const std::uint32_t dlat = 1'800'000'000u / (nlat - 1);
        const std::uint32_t dlon = 3'600'000'000u / nlon;
        if (dlat * (nlat - 1) != 1'800'000'000u) return std::unexpected(GridError::badStep);
        if (dlon * nlon != 3'600'000'000u)       return std::unexpected(GridError::badStep);
        if (dlat > 0xFF'FFFFu || dlon > 0xFF'FFFFu) return std::unexpected(GridError::badStep);

        return Geoid{blob.subspan(kHeader), nlat, nlon, dlat, dlon, rd16(blob, 8)};
    }

    [[nodiscard]] Centimetre undulation(Lat lat, Lon lon) const noexcept
    {
        const auto [r0, r1, fy] = rowCell(lat);
        const auto [c0, c1, fx] = colCell(lon);

        const auto wx  = static_cast<std::int32_t>(fx);
        const auto wy  = static_cast<std::int32_t>(fy);
        const std::int32_t top = node(r0, c0) * (256 - wx) + node(r0, c1) * wx;   // Q8
        const std::int32_t bot = node(r1, c0) * (256 - wx) + node(r1, c1) * wx;   // Q8
        const std::int32_t val = top * (256 - wy) + bot * wy;                     // Q16
        return Centimetre{(val + 32768) >> 16};
    }

    [[nodiscard]] Millimetre toAmsl(Lat lat, Lon lon, Millimetre h) const noexcept
    { return Millimetre{h.v - undulation(lat, lon).v * 10}; }

    [[nodiscard]] Millimetre toEllipsoid(Lat lat, Lon lon, Millimetre amsl) const noexcept
    { return Millimetre{amsl.v + undulation(lat, lon).v * 10}; }

private:
    struct Cell { std::uint32_t lo, hi, frac; };

    static constexpr std::size_t   kHeader     = 12;
    static constexpr std::uint32_t kSouthFirst = 0x0001;

    std::span<const std::byte> data_;
    std::uint32_t nlat_, nlon_, dlat_, dlon_, flags_;

    Geoid(std::span<const std::byte> d, std::uint32_t nlat, std::uint32_t nlon,
          std::uint32_t dlat, std::uint32_t dlon, std::uint32_t flags) noexcept
        : data_{d}, nlat_{nlat}, nlon_{nlon}, dlat_{dlat}, dlon_{dlon}, flags_{flags} {}

    static std::uint32_t rd16(std::span<const std::byte> b, std::size_t at) noexcept
    {
        return std::to_integer<std::uint32_t>(b[at]) |
               (std::to_integer<std::uint32_t>(b[at + 1]) << 8);
    }

    [[nodiscard]] Cell rowCell(Lat lat) const noexcept
    {
        const std::int32_t phi = std::clamp(lat.e7, -900'000'000, 900'000'000);
        const std::uint32_t t = (flags_ & kSouthFirst)
            ? static_cast<std::uint32_t>(phi + 900'000'000)
            : static_cast<std::uint32_t>(900'000'000 - phi);

        std::uint32_t r = t / dlat_;
        std::uint32_t f = ((t - r * dlat_) << 8) / dlat_;
        if (r >= nlat_ - 1) { r = nlat_ - 2; f = 256; }   // дальній полюс
        return {r, r + 1, f};
    }

    [[nodiscard]] Cell colCell(Lon lon) const noexcept
    {
        std::int64_t l = (static_cast<std::int64_t>(lon.e7) + 1'800'000'000) % 3'600'000'000;
        if (l < 0) l += 3'600'000'000;
        const auto u = static_cast<std::uint32_t>(l);
        const std::uint32_t c = u / dlon_;
        const std::uint32_t f = ((u - c * dlon_) << 8) / dlon_;
        return {c, (c + 1 == nlon_) ? 0u : c + 1, f};     // замикання меридіана
    }

    [[nodiscard]] std::int32_t node(std::uint32_t row, std::uint32_t col) const noexcept
    {
        const std::size_t at = (static_cast<std::size_t>(row) * nlon_ + col) * 2;
        assert(at + 1 < data_.size());   // індекси вже перевірені в open() — це запобіжник на випадок правки
        const auto raw = static_cast<std::uint16_t>(
            std::to_integer<std::uint16_t>(data_[at]) |
            static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(data_[at + 1]) << 8));
        return static_cast<std::int16_t>(raw);
    }
};

} // namespace geo

// Сітку відкривають один раз при старті, далі йдуть самі пошуки.
// Переставити широту з довготою на цьому виклику вже неможливо.
inline geo::Millimetre amslFromFix(const geo::Geoid &grid, std::int32_t lat_e7,
                                   std::int32_t lon_e7, std::int32_t h_mm) noexcept
{
    return grid.toAmsl(geo::Lat{lat_e7}, geo::Lon{lon_e7}, geo::Millimetre{h_mm});
}
