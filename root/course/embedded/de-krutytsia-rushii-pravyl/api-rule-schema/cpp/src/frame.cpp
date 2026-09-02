#include "rules/frame.hpp"

#include <algorithm>

namespace rules {

std::uint16_t crc16Ccitt(std::span<const std::byte> data) noexcept {
    std::uint16_t crc = 0xFFFF;                       // поліном 0x1021
    for (std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint16_t>(b) << 8);
        for (int i = 0; i < 8; ++i) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

std::expected<std::size_t, RuleError> encodeFrame(FrameType type,
                                                  std::span<const std::byte> payload,
                                                  std::span<std::byte> out) noexcept {
    const std::size_t total = kFrameHeader + payload.size() + kFrameCrc;
    if (out.size() < total || payload.size() > kMaxRules * kDescriptorSize) {
        return std::unexpected(RuleError::BufferOverflow);
    }

    out[0] = kSofHi;
    out[1] = kSofLo;
    wire::write16(out, 2, static_cast<std::uint16_t>(payload.size()));
    out[4] = static_cast<std::byte>(type);
    std::copy(payload.begin(), payload.end(), out.begin() + kFrameHeader);

    // Сума береться з Length, Type і Payload — синхробайти в неї не входять.
    const std::uint16_t crc = crc16Ccitt(out.subspan(2, payload.size() + 3));
    wire::write16(out, kFrameHeader + payload.size(), crc);
    return total;
}

std::expected<std::size_t, RuleError> encodeRuleTable(std::span<const RuleDescriptor> table,
                                                      std::span<std::byte> out) noexcept {
    if (table.size() > kMaxRules) { return std::unexpected(RuleError::BufferOverflow); }

    std::array<std::byte, kMaxRules * kDescriptorSize> payload{};
    for (std::size_t i = 0; i < table.size(); ++i) {
        table[i].toWire(std::span{payload}.subspan(i * kDescriptorSize, kDescriptorSize));
    }
    return encodeFrame(FrameType::RuleTable,
                       std::span{payload}.first(table.size() * kDescriptorSize), out);
}

std::expected<RuleTable, RuleError> decodeRuleTable(std::span<const std::byte> frame) noexcept {
    if (frame.size() < kMinFrame || frame.size() > kMaxFrame) {
        return std::unexpected(RuleError::TruncatedFrame);
    }
    if (frame[0] != kSofHi || frame[1] != kSofLo) {
        return std::unexpected(RuleError::BadSof);
    }

    const std::size_t payloadLen = wire::read16(frame, 2);
    if (payloadLen + kFrameHeader + kFrameCrc != frame.size()) {
        return std::unexpected(RuleError::TruncatedFrame);
    }

    // 1. Цілісність: побитий кадр до розбору полів не доходить.
    const std::uint16_t got  = wire::read16(frame, kFrameHeader + payloadLen);
    const std::uint16_t want = crc16Ccitt(frame.subspan(2, payloadLen + 3));
    if (got != want) { return std::unexpected(RuleError::CrcMismatch); }

    if (std::to_integer<std::uint8_t>(frame[4]) != static_cast<std::uint8_t>(FrameType::RuleTable)) {
        return std::unexpected(RuleError::UnknownType);
    }
    if (payloadLen % kDescriptorSize != 0) { return std::unexpected(RuleError::LengthAlign); }

    // 2. Ліміт пам'яті: тіньова таблиця має фіксовану місткість.
    const std::size_t count = payloadLen / kDescriptorSize;
    if (count > kMaxRules) { return std::unexpected(RuleError::BufferOverflow); }

    RuleTable table{};
    table.count = count;
    for (std::size_t i = 0; i < count; ++i) {
        table.rules[i] = RuleDescriptor::fromWire(
            frame.subspan(kFrameHeader + i * kDescriptorSize, kDescriptorSize));
    }
    return table;
}

namespace {

Reply makeReply(FrameType type, std::uint8_t payload, RuleError status) noexcept {
    Reply reply{};
    reply.status = status;
    const std::byte body{payload};
    if (auto n = encodeFrame(type, std::span{&body, 1}, reply.bytes)) { reply.size = *n; }
    return reply;
}

}  // namespace

Reply handleFrame(RuleEngine& engine, std::span<const std::byte> frame) noexcept {
    const auto decoded = decodeRuleTable(frame);
    if (!decoded) {
        return makeReply(FrameType::Nack, static_cast<std::uint8_t>(decoded.error()),
                         decoded.error());
    }

    // 3–4. Семантика й атомарне перемикання — всередині рушія.
    if (auto ok = engine.install(decoded->view()); !ok) {
        return makeReply(FrameType::Nack, static_cast<std::uint8_t>(ok.error()), ok.error());
    }
    return makeReply(FrameType::Ack, static_cast<std::uint8_t>(decoded->count), RuleError::None);
}

}  // namespace rules
