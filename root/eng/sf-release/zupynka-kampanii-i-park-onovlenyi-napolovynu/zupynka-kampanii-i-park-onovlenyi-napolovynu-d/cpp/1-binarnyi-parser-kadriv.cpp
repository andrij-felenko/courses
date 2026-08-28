#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <cstdint>
#include <expected>
#include <cstring>
#include <algorithm>

namespace mixed_fleet::wire {

enum class WireType : uint8_t {
    Varint = 0,
    Fixed64 = 1,
    LengthDelimited = 2
};

struct UnknownField {
    uint32_t tag{0};
    WireType wire_type{WireType::Varint};
    std::vector<uint8_t> payload;
};

class TransactionMessageV1 {
public:
    uint64_t transaction_id{0};
    uint64_t amount_cents{0};
    uint64_t timestamp_utc{0};
    std::vector<UnknownField> unknown_fields;

    static std::expected<TransactionMessageV1, std::string_view>
    parse(std::span<const uint8_t> buffer) noexcept {
        TransactionMessageV1 msg;
        size_t cursor = 0;

        while (cursor < buffer.size()) {
            if (cursor + 1 > buffer.size()) {
                return std::unexpected("Premature end of buffer while reading wire header");
            }

            const uint8_t header = buffer[cursor++];
            const uint32_t tag = static_cast<uint32_t>(header >> 3);
            const auto wtype = static_cast<WireType>(header & 0x07);

            if (tag == 1 && wtype == WireType::Varint) {
                if (cursor + sizeof(uint64_t) > buffer.size()) return std::unexpected("Malformed tag 1");
                std::memcpy(&msg.transaction_id, buffer.data() + cursor, sizeof(uint64_t));
                cursor += sizeof(uint64_t);
            } else if (tag == 2 && wtype == WireType::Varint) {
                if (cursor + sizeof(uint64_t) > buffer.size()) return std::unexpected("Malformed tag 2");
                std::memcpy(&msg.amount_cents, buffer.data() + cursor, sizeof(uint64_t));
                cursor += sizeof(uint64_t);
            } else if (tag == 3 && wtype == WireType::Varint) {
                if (cursor + sizeof(uint64_t) > buffer.size()) return std::unexpected("Malformed tag 3");
                std::memcpy(&msg.timestamp_utc, buffer.data() + cursor, sizeof(uint64_t));
                cursor += sizeof(uint64_t);
            } else {
                UnknownField uf;
                uf.tag = tag;
                uf.wire_type = wtype;

                if (wtype == WireType::Varint || wtype == WireType::Fixed64) {
                    if (cursor + sizeof(uint64_t) > buffer.size()) return std::unexpected("Malformed fixed field");
                    uf.payload.resize(sizeof(uint64_t));
                    std::memcpy(uf.payload.data(), buffer.data() + cursor, sizeof(uint64_t));
                    cursor += sizeof(uint64_t);
                } else if (wtype == WireType::LengthDelimited) {
                    if (cursor + 1 > buffer.size()) return std::unexpected("Malformed length prefix");
                    const size_t len = buffer[cursor++];
                    if (cursor + len > buffer.size()) return std::unexpected("Payload exceeds buffer bounds");
                    uf.payload.resize(len);
                    std::memcpy(uf.payload.data(), buffer.data() + cursor, len);
                    cursor += len;
                } else {
                    return std::unexpected("Unknown wire encoding type");
                }
                msg.unknown_fields.push_back(std::move(uf));
            }
        }
        return msg;
    }

    [[nodiscard]] std::vector<uint8_t> serialize() const {
        std::vector<uint8_t> out;
        out.reserve(64 + unknown_fields.size() * 16);

        auto write_u64 = [&out](uint32_t tag, WireType wt, uint64_t val) {
            out.push_back(static_cast<uint8_t>((tag << 3) | static_cast<uint8_t>(wt)));
            const size_t pos = out.size();
            out.resize(pos + sizeof(uint64_t));
            std::memcpy(out.data() + pos, &val, sizeof(uint64_t));
        };

        write_u64(1, WireType::Varint, transaction_id);
        write_u64(2, WireType::Varint, amount_cents);
        write_u64(3, WireType::Varint, timestamp_utc);

        for (const auto& uf : unknown_fields) {
            out.push_back(static_cast<uint8_t>((uf.tag << 3) | static_cast<uint8_t>(uf.wire_type)));
            if (uf.wire_type == WireType::LengthDelimited) {
                out.push_back(static_cast<uint8_t>(uf.payload.size()));
            }
            out.insert(out.end(), uf.payload.begin(), uf.payload.end());
        }

        return out;
    }
};

} // namespace mixed_fleet::wire
