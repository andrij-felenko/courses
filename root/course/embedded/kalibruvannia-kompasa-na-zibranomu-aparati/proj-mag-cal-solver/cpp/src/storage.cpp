// ===========================================================================
//  storage.cpp — CRC32, пакування запису й робота з енергонезалежною пам'яттю
// ===========================================================================

#include "mag_cal/storage.hpp"

#include <algorithm>
#include <bit>
#include <cmath>

namespace mag_cal {
namespace {

constexpr std::size_t kCrcOffset = kRecordSize - 4;

// Побайтові примітиви little-endian: bit_cast дає биті float без гри в
// каламбур указівниками, і компілятор перетворює це на нуль інструкцій.
void put_u32(std::span<std::byte> dst, std::uint32_t value) noexcept {
    dst[0] = static_cast<std::byte>(value & 0xFFU);
    dst[1] = static_cast<std::byte>((value >> 8) & 0xFFU);
    dst[2] = static_cast<std::byte>((value >> 16) & 0xFFU);
    dst[3] = static_cast<std::byte>((value >> 24) & 0xFFU);
}

[[nodiscard]] std::uint32_t get_u32(std::span<const std::byte> src) noexcept {
    return static_cast<std::uint32_t>(src[0]) |
           (static_cast<std::uint32_t>(src[1]) << 8) |
           (static_cast<std::uint32_t>(src[2]) << 16) |
           (static_cast<std::uint32_t>(src[3]) << 24);
}

void put_f32(std::span<std::byte> dst, float value) noexcept {
    put_u32(dst, std::bit_cast<std::uint32_t>(value));
}

[[nodiscard]] float get_f32(std::span<const std::byte> src) noexcept {
    return std::bit_cast<float>(get_u32(src));
}

[[nodiscard]] bool sane_offset(const Vec3& v) noexcept {
    return std::isfinite(v.x) && std::isfinite(v.y) && std::isfinite(v.z) &&
           std::abs(v.x) <= limits::kMaxOffsetUt &&
           std::abs(v.y) <= limits::kMaxOffsetUt &&
           std::abs(v.z) <= limits::kMaxOffsetUt;
}

[[nodiscard]] bool sane_matrix(const Mat3& m) noexcept {
    if (!m.all_finite()) {
        return false;
    }
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) {
            if (std::abs(m.at(i, j)) > limits::kMaxGain) {
                return false;
            }
        }
    }
    return true;
}

}  // namespace

std::string_view describe(StorageError error) noexcept {
    switch (error) {
        case StorageError::Io:           return "помилка доступу до Flash";
        case StorageError::BadCrc:       return "CRC32 не збіглася";
        case StorageError::BadValues:    return "нефізичні коефіцієнти";
        case StorageError::PoorFitness:  return "збережена нев'язка завелика";
        case StorageError::VerifyFailed: return "перевірка після запису не пройшла";
    }
    return "невідома помилка";
}

// CRC-32/ISO-HDLC (той самий поліном, що в Ethernet і zip), відображений
// вигляд 0xEDB88320. Побітово: таблиця на кілобайт дорожча за 60 байтів,
// які вона перевіряє.
std::uint32_t crc32(std::span<const std::byte> data) noexcept {
    std::uint32_t crc = 0xFFFFFFFFU;
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint32_t>(b);
        for (int bit = 0; bit < 8; ++bit) {
            const std::uint32_t mask = -(crc & 1U);
            crc = (crc >> 1) ^ (0xEDB88320U & mask);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}

RecordBuffer encode(const Calibration& cal) noexcept {
    RecordBuffer buf{};
    const std::span<std::byte> out{buf};

    put_f32(out.subspan(0, 4), cal.offset.x);
    put_f32(out.subspan(4, 4), cal.offset.y);
    put_f32(out.subspan(8, 4), cal.offset.z);

    std::size_t pos = 12;
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) {
            put_f32(out.subspan(pos, 4), cal.soft_iron.at(i, j));
            pos += 4;
        }
    }

    put_f32(out.subspan(48, 4), cal.earth_field);
    put_f32(out.subspan(52, 4), cal.rms_residual);
    put_u32(out.subspan(kCrcOffset, 4), crc32(out.first(kCrcOffset)));
    return buf;
}

std::expected<Calibration, StorageError> decode(
    std::span<const std::byte, kRecordSize> raw) noexcept {
    const std::uint32_t stored = get_u32(raw.subspan(kCrcOffset, 4));
    if (stored != crc32(raw.first(kCrcOffset))) {
        return std::unexpected(StorageError::BadCrc);
    }

    Calibration cal{};
    cal.offset = {get_f32(raw.subspan(0, 4)), get_f32(raw.subspan(4, 4)),
                  get_f32(raw.subspan(8, 4))};

    Mat3::Rows rows{};
    std::size_t pos = 12;
    for (std::size_t i = 0; i < 3; ++i) {
        for (std::size_t j = 0; j < 3; ++j) {
            rows[i][j] = get_f32(raw.subspan(pos, 4));
            pos += 4;
        }
    }
    cal.soft_iron = Mat3{rows};
    cal.earth_field = get_f32(raw.subspan(48, 4));
    cal.rms_residual = get_f32(raw.subspan(52, 4));

    // Збіжна CRC доводить лише цілісність байтів. Сміття, записане цілим,
    // лишається сміттям — тому перевіряємо ще й фізичний зміст чисел.
    if (!sane_offset(cal.offset) || !sane_matrix(cal.soft_iron) ||
        !std::isfinite(cal.earth_field) || !std::isfinite(cal.rms_residual) ||
        cal.earth_field < 10.0F || cal.earth_field > 100.0F) {
        return std::unexpected(StorageError::BadValues);
    }

    cal.condition = cal.soft_iron.condition_number();
    cal.sphere_radius = cal.earth_field;
    if (!cal.passes_quality_gates()) {
        return std::unexpected(StorageError::PoorFitness);
    }

    cal.valid = true;
    return cal;
}

std::expected<void, StorageError> save(const Calibration& cal) noexcept {
    const RecordBuffer buf = encode(cal);

    if (!flash_port::erase() || !flash_port::write(buf)) {
        return std::unexpected(StorageError::Io);
    }

    RecordBuffer verify{};
    if (!flash_port::read(verify)) {
        return std::unexpected(StorageError::Io);
    }
    if (!std::ranges::equal(buf, verify)) {
        return std::unexpected(StorageError::VerifyFailed);
    }
    return {};
}

std::expected<Calibration, StorageError> load() noexcept {
    RecordBuffer buf{};
    if (!flash_port::read(buf)) {
        return std::unexpected(StorageError::Io);
    }
    return decode(std::span<const std::byte, kRecordSize>{buf});
}

}  // namespace mag_cal
