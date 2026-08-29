// Формат журналу: константи, заголовки, CRC, пакування й розбирання кадрів.
//
// Структури у Flash не блітяться — усе серіалізується побайтово little-endian.
// Розкладка struct залежить від компілятора й прапорців, а формат мусить
// однаково читатися і мікроконтролером, і розбирачем на сервері.

#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace fl {

inline constexpr std::size_t   kSectorSize        = 4096;
inline constexpr std::size_t   kSectorCount       = 8;
inline constexpr std::uint16_t kSectorMagic       = 0xA55A;
inline constexpr std::uint16_t kRecordMagic       = 0x55AA;
inline constexpr std::uint16_t kFormatVersion     = 0x0001;

inline constexpr std::size_t   kSectorHeaderSize  = 16;
inline constexpr std::size_t   kSectorStateOffset = 12;
inline constexpr std::size_t   kRecordHeaderSize  = 13;
inline constexpr std::size_t   kCrcSize           = 2;
inline constexpr std::size_t   kMaxRecordSize     = 255;
inline constexpr std::size_t   kMaxPayloadSize    = kMaxRecordSize - kRecordHeaderSize - kCrcSize;

enum class Level : std::uint8_t { Trace = 0, Debug, Info, Warn, Error, Fatal };

// Кожен перехід лише гасить біти, тож стан міняється записом на місці:
// Erased -> Active -> Full -> Dirty.
enum class SectorState : std::uint32_t {
    Erased = 0xFFFFFFFFu,
    Active = 0xFFFFFFFEu,
    Full   = 0xFFFFFFFCu,
    Dirty  = 0x00000000u,
};

enum class CodecError { PayloadTooBig, BufferTooSmall, BadMagic, BadLength, CrcMismatch };

// Модуль 0 і верхній діапазон токенів належать самому журналові.
inline constexpr std::uint8_t  kLoggerModule   = 0;
inline constexpr std::uint32_t kTokenBadSector = 0xFFFF0001u;
inline constexpr std::uint32_t kTokenIsrDrops  = 0xFFFF0002u;

using SectorHeaderBytes = std::array<std::byte, kSectorHeaderSize>;

struct SectorHeader {
    std::uint16_t magic{kSectorMagic};
    std::uint16_t version{kFormatVersion};
    std::uint32_t seqNum{0};
    std::uint32_t eraseCount{0};
    SectorState   state{SectorState::Erased};

    [[nodiscard]] SectorHeaderBytes encode() const noexcept;
    [[nodiscard]] static SectorHeader decode(const SectorHeaderBytes& raw) noexcept;
};

struct RecordHeader {
    std::uint8_t  length{0};  // повна довжина кадру разом із заголовком і CRC
    Level         level{Level::Info};
    std::uint8_t  moduleId{0};
    std::uint32_t timestampMs{0};
    std::uint32_t tokenId{0};
};

struct DecodedRecord {
    RecordHeader header;
    std::span<const std::byte> payload;  // дивиться всередину переданого буфера
};

// Поліном 0x1021, початкове значення 0xFFFF, без інверсії на виході.
[[nodiscard]] std::uint16_t crc16Ccitt(std::span<const std::byte> data) noexcept;

// Складає кадр у out і повертає зріз рівно тієї довжини, що вийшла.
[[nodiscard]] std::expected<std::span<std::byte>, CodecError> encodeRecord(
    const RecordHeader& header, std::span<const std::byte> payload, std::span<std::byte> out) noexcept;

[[nodiscard]] std::expected<DecodedRecord, CodecError> decodeRecord(
    std::span<const std::byte> raw) noexcept;

// Примітиви little-endian: ними ж логер гасить біти стану сектора.
void putU16(std::span<std::byte> dst, std::uint16_t value) noexcept;
void putU32(std::span<std::byte> dst, std::uint32_t value) noexcept;
[[nodiscard]] std::uint16_t getU16(std::span<const std::byte> src) noexcept;
[[nodiscard]] std::uint32_t getU32(std::span<const std::byte> src) noexcept;

}  // namespace fl
