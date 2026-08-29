#include "record_codec.hpp"

#include <algorithm>

namespace fl {

void putU16(std::span<std::byte> dst, std::uint16_t value) noexcept
{
    dst[0] = static_cast<std::byte>(value & 0xFFu);
    dst[1] = static_cast<std::byte>((value >> 8) & 0xFFu);
}

void putU32(std::span<std::byte> dst, std::uint32_t value) noexcept
{
    dst[0] = static_cast<std::byte>(value & 0xFFu);
    dst[1] = static_cast<std::byte>((value >> 8) & 0xFFu);
    dst[2] = static_cast<std::byte>((value >> 16) & 0xFFu);
    dst[3] = static_cast<std::byte>((value >> 24) & 0xFFu);
}

std::uint16_t getU16(std::span<const std::byte> src) noexcept
{
    return static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(src[0]) |
                                      (std::to_integer<std::uint16_t>(src[1]) << 8));
}

std::uint32_t getU32(std::span<const std::byte> src) noexcept
{
    return std::to_integer<std::uint32_t>(src[0]) |
           (std::to_integer<std::uint32_t>(src[1]) << 8) |
           (std::to_integer<std::uint32_t>(src[2]) << 16) |
           (std::to_integer<std::uint32_t>(src[3]) << 24);
}

std::uint16_t crc16Ccitt(std::span<const std::byte> data) noexcept
{
    std::uint16_t crc = 0xFFFFu;

    // Побітово: кадри короткі, і таблиця на 512 байтів у ПЗП дорожча за такти.
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(b) << 8);
        for (int bit = 0; bit < 8; ++bit) {
            const bool msb = (crc & 0x8000u) != 0;
            crc = static_cast<std::uint16_t>(crc << 1);
            if (msb) {
                crc = static_cast<std::uint16_t>(crc ^ 0x1021u);
            }
        }
    }
    return crc;
}

SectorHeaderBytes SectorHeader::encode() const noexcept
{
    SectorHeaderBytes raw{};
    std::span<std::byte> out{raw};

    putU16(out.subspan(0, 2), magic);
    putU16(out.subspan(2, 2), version);
    putU32(out.subspan(4, 4), seqNum);
    putU32(out.subspan(8, 4), eraseCount);
    putU32(out.subspan(kSectorStateOffset, 4), static_cast<std::uint32_t>(state));
    return raw;
}

SectorHeader SectorHeader::decode(const SectorHeaderBytes& raw) noexcept
{
    std::span<const std::byte> in{raw};
    return SectorHeader{
        .magic = getU16(in.subspan(0, 2)),
        .version = getU16(in.subspan(2, 2)),
        .seqNum = getU32(in.subspan(4, 4)),
        .eraseCount = getU32(in.subspan(8, 4)),
        .state = static_cast<SectorState>(getU32(in.subspan(kSectorStateOffset, 4))),
    };
}

std::expected<std::span<std::byte>, CodecError> encodeRecord(const RecordHeader& header,
                                                             std::span<const std::byte> payload,
                                                             std::span<std::byte> out) noexcept
{
    if (payload.size() > kMaxPayloadSize) {
        return std::unexpected(CodecError::PayloadTooBig);
    }

    const std::size_t total = kRecordHeaderSize + payload.size() + kCrcSize;
    if (out.size() < total) {
        return std::unexpected(CodecError::BufferTooSmall);
    }

    putU16(out.subspan(0, 2), kRecordMagic);
    out[2] = static_cast<std::byte>(total);
    out[3] = static_cast<std::byte>(header.level);
    out[4] = static_cast<std::byte>(header.moduleId);
    putU32(out.subspan(5, 4), header.timestampMs);
    putU32(out.subspan(9, 4), header.tokenId);
    std::ranges::copy(payload, out.begin() + static_cast<std::ptrdiff_t>(kRecordHeaderSize));

    // CRC покриває байти від поля довжини до останнього байта навантаження:
    // магічне число перевіряється окремо й у суму не входить.
    const std::uint16_t crc = crc16Ccitt(out.subspan(2, total - 4));
    putU16(out.subspan(total - kCrcSize, kCrcSize), crc);

    return out.subspan(0, total);
}

std::expected<DecodedRecord, CodecError> decodeRecord(std::span<const std::byte> raw) noexcept
{
    if (raw.size() < kRecordHeaderSize + kCrcSize) {
        return std::unexpected(CodecError::BadLength);
    }
    if (getU16(raw.subspan(0, 2)) != kRecordMagic) {
        return std::unexpected(CodecError::BadMagic);
    }

    const auto total = std::to_integer<std::size_t>(raw[2]);
    if (total < kRecordHeaderSize + kCrcSize || total > raw.size()) {
        return std::unexpected(CodecError::BadLength);
    }
    if (getU16(raw.subspan(total - kCrcSize, kCrcSize)) != crc16Ccitt(raw.subspan(2, total - 4))) {
        return std::unexpected(CodecError::CrcMismatch);
    }

    return DecodedRecord{
        .header = {
            .length = static_cast<std::uint8_t>(total),
            .level = static_cast<Level>(std::to_integer<std::uint8_t>(raw[3])),
            .moduleId = std::to_integer<std::uint8_t>(raw[4]),
            .timestampMs = getU32(raw.subspan(5, 4)),
            .tokenId = getU32(raw.subspan(9, 4)),
        },
        .payload = raw.subspan(kRecordHeaderSize, total - kRecordHeaderSize - kCrcSize),
    };
}

}  // namespace fl
