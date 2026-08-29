#pragma once

#include "divider.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace psu::nvm {

/* Зберігання калібрувальних коефіцієнтів в енергонезалежній пам'яті.
   Модуль навмисно не знає, що це за пам'ять: він пакує запис у байти,
   а хто його понесе в EEPROM, у сектор Flash чи у файл — справа виклику.

   Розкладка запису (14 байтів, порядок little-endian):
       [0..3]   магія "CAL1"
       [4..7]   offsetMv, int32
       [8..11]  gainPpm,  uint32
       [12..13] CRC-16/CCITT-FALSE перших 12 байтів                        */

enum class BlobError {
    shortBuffer,   // буфер коротший за запис
    badMagic,      // сторінка чиста (0xFF) або зайнята чимось іншим
    badCrc,        // запис побився: обрив живлення під час запису, знос комірки
    implausible    // CRC збігся, але коефіцієнти безглузді
};

[[nodiscard]] std::string_view describe(BlobError err) noexcept;

inline constexpr std::size_t blobSize = 14;
using Blob = std::array<std::byte, blobSize>;

[[nodiscard]] Blob pack(const Calibration& cal) noexcept;
[[nodiscard]] std::expected<Calibration, BlobError> unpack(std::span<const std::byte> raw) noexcept;

[[nodiscard]] std::uint16_t crc16Ccitt(std::span<const std::byte> data) noexcept;

} // namespace psu::nvm
