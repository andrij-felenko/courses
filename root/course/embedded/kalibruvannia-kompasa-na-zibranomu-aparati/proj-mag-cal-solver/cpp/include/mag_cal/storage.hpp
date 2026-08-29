// ===========================================================================
//  mag_cal/storage.hpp — запис калібрування у Flash: 60 байтів і CRC32
//
//      байти 00..11 — вектор Hard Iron V0        (3 × float)
//      байти 12..47 — матриця Soft Iron W        (9 × float, по рядках)
//      байти 48..51 — еталонний модуль поля      (float)
//      байти 52..55 — залишкова нев'язка RMS     (float)
//      байти 56..59 — контрольна сума CRC32      (uint32)
//
//  Структуру C++ у Flash не пишемо: доповнення полів і порядок байтів
//  мовчки змінюються з компілятором, а запис має пережити зміну тулчейна.
// ===========================================================================
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "mag_cal/calibration.hpp"

namespace mag_cal {

enum class StorageError : std::uint8_t {
    Io,             // Flash не прочитався або не записався
    BadCrc,         // контрольна сума не збіглася
    BadValues,      // NaN чи нефізичні коефіцієнти
    PoorFitness,    // збережена нев'язка гірша за поріг
    VerifyFailed    // зчитане після запису не збіглося із записаним
};

[[nodiscard]] std::string_view describe(StorageError error) noexcept;

inline constexpr std::size_t kRecordSize = 60;
using RecordBuffer = std::array<std::byte, kRecordSize>;

[[nodiscard]] std::uint32_t crc32(std::span<const std::byte> data) noexcept;

[[nodiscard]] RecordBuffer encode(const Calibration& cal) noexcept;
[[nodiscard]] std::expected<Calibration, StorageError> decode(
    std::span<const std::byte, kRecordSize> raw) noexcept;

// Запис із обов'язковим зворотним читанням: напівстертий сектор приймає
// дані, але тримає біти лише до першого прогрівання.
[[nodiscard]] std::expected<void, StorageError> save(const Calibration& cal) noexcept;
[[nodiscard]] std::expected<Calibration, StorageError> load() noexcept;

// Порт плати. Реалізує BSP контролера: сектор Flash, сторінка EEPROM або
// файл у LittleFS — конвеєру байдуже, яка з них під ним.
namespace flash_port {
[[nodiscard]] bool erase() noexcept;
[[nodiscard]] bool write(std::span<const std::byte> data) noexcept;
[[nodiscard]] bool read(std::span<std::byte> data) noexcept;
}  // namespace flash_port

}  // namespace mag_cal
