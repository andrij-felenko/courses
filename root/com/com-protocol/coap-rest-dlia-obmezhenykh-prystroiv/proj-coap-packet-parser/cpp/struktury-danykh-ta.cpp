#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>
#include <optional>
#include <expected>
#include <algorithm>

namespace coap {

enum class Type : uint8_t {
    Confirmable = 0,
    NonConfirmable = 1,
    Acknowledgement = 2,
    Reset = 3
};

enum class ParseError {
    BufferTooSmall,
    InvalidVersion,
    InvalidTokenLength,
    MalformedOptions,
    OptionsNotSorted,
    EmptyPayloadMarker,
    OptionBufferOverflow
};

struct OptionView {
    uint16_t number{0};
    std::span<const uint8_t> value{};

    [[nodiscard]] std::string_view as_string() const noexcept {
        return {reinterpret_cast<const char*>(value.data()), value.size()};
    }

    [[nodiscard]] uint32_t as_uint() const noexcept {
        uint32_t res = 0;
        for (uint8_t b : value) {
            res = (res << 8) | b;
        }
        return res;
    }
};

class PacketView {
public:
    static constexpr size_t HeaderSize = 4;
    static constexpr uint8_t PayloadMarker = 0xFF;
    static constexpr size_t MaxOptions = 16;

    uint8_t version{1};
    Type type{Type::Confirmable};
    uint8_t code{0};
    uint16_t message_id{0};
    std::span<const uint8_t> token{};
    std::array<OptionView, MaxOptions> options{};
    size_t option_count{0};
    std::span<const uint8_t> payload{};

    static std::expected<PacketView, ParseError> parse(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < HeaderSize) {
            return std::unexpected(ParseError::BufferTooSmall);
        }

        PacketView pkt;
        pkt.version = (buffer[0] >> 6) & 0x03;
        if (pkt.version != 1) {
            return std::unexpected(ParseError::InvalidVersion);
        }

        pkt.type = static_cast<Type>((buffer[0] >> 4) & 0x03);
        const uint8_t tkl = buffer[0] & 0x0F;
        if (tkl > 8) {
            return std::unexpected(ParseError::InvalidTokenLength);
        }

        pkt.code = buffer[1];
        pkt.message_id = (static_cast<uint16_t>(buffer[2]) << 8) | buffer[3];

        size_t offset = HeaderSize;
        if (buffer.size() < offset + tkl) {
            return std::unexpected(ParseError::BufferTooSmall);
        }

        if (tkl > 0) {
            pkt.token = buffer.subspan(offset, tkl);
            offset += tkl;
        }

        uint16_t current_option_number = 0;

        while (offset < buffer.size()) {
            if (buffer[offset] == PayloadMarker) {
                offset++;
                if (offset >= buffer.size()) {
                    return std::unexpected(ParseError::EmptyPayloadMarker);
                }
                pkt.payload = buffer.subspan(offset);
                return pkt;
            }

            if (pkt.option_count >= MaxOptions) {
                return std::unexpected(ParseError::OptionBufferOverflow);
            }

            const uint8_t header = buffer[offset++];
            uint16_t delta = (header >> 4) & 0x0F;
            uint16_t length = header & 0x0F;

            if (delta == 15 || length == 15) {
                return std::unexpected(ParseError::MalformedOptions);
            }

            if (delta == 13) {
                if (offset >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                delta = static_cast<uint16_t>(buffer[offset++]) + 13;
            } else if (delta == 14) {
                if (offset + 1 >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                delta = ((static_cast<uint16_t>(buffer[offset]) << 8) | buffer[offset + 1]) + 269;
                offset += 2;
            }

            if (length == 13) {
                if (offset >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                length = static_cast<uint16_t>(buffer[offset++]) + 13;
            } else if (length == 14) {
                if (offset + 1 >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                length = ((static_cast<uint16_t>(buffer[offset]) << 8) | buffer[offset + 1]) + 269;
                offset += 2;
            }

            if (offset + length > buffer.size()) {
                return std::unexpected(ParseError::BufferTooSmall);
            }

            current_option_number += delta;
            pkt.options[pkt.option_count++] = OptionView{
                .number = current_option_number,
                .value = buffer.subspan(offset, length)
            };
            offset += length;
        }

        return pkt;
    }

    [[nodiscard]] std::optional<OptionView> find_option(uint16_t number) const noexcept {
        for (size_t i = 0; i < option_count; ++i) {
            if (options[i].number == number) {
                return options[i];
            }
        }
        return std::nullopt;
    }
};

} // namespace coap
