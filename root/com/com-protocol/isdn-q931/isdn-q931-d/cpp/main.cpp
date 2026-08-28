#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <string_view>

namespace isdn {

inline constexpr uint8_t ProtocolDiscriminatorQ931 = 0x08;

struct InformationElement {
    uint8_t ie_id{0};
    bool single_octet{false};
    std::span<const uint8_t> payload{};
};

struct Q931Header {
    uint8_t protocol_discriminator{0};
    uint16_t call_reference{0};
    bool flag_destination{false};
    uint8_t message_type{0};
    std::span<const uint8_t> ie_block{};
};

/* Ідіоматичний нуль-копійний розбір повідомлення Q.931 */
[[nodiscard]] constexpr std::optional<Q931Header> parse_header(std::span<const uint8_t> frame) noexcept {
    if (frame.size() < 3) return std::nullopt;

    if (frame[0] != ProtocolDiscriminatorQ931) {
        return std::nullopt;
    }

    const uint8_t cr_len = frame[1] & 0x0F;
    Q931Header hdr{};
    hdr.protocol_discriminator = frame[0];

    if (cr_len == 0) {
        hdr.call_reference = 0;
        hdr.flag_destination = false;
        hdr.message_type = frame[2];
        hdr.ie_block = frame.subspan(3);
        return hdr;
    }

    if (cr_len == 1) {
        if (frame.size() < 4) return std::nullopt;
        hdr.flag_destination = (frame[2] & 0x80) != 0;
        hdr.call_reference = frame[2] & 0x7F;
        hdr.message_type = frame[3];
        hdr.ie_block = frame.subspan(4);
        return hdr;
    }

    if (cr_len == 2) {
        if (frame.size() < 5) return std::nullopt;
        hdr.flag_destination = (frame[2] & 0x80) != 0;
        hdr.call_reference = (static_cast<uint16_t>(frame[2] & 0x7F) << 8) | frame[3];
        hdr.message_type = frame[4];
        hdr.ie_block = frame.subspan(5);
        return hdr;
    }

    return std::nullopt;
}

/* Генератор-ітератор інформаційних елементів */
class IEParser {
public:
    explicit constexpr IEParser(std::span<const uint8_t> data) noexcept : remaining_(data) {}

    [[nodiscard]] std::optional<InformationElement> next() noexcept {
        if (remaining_.empty()) return std::nullopt;

        const uint8_t first = remaining_[0];
        if (first & 0x80) {
            InformationElement ie{
                .ie_id = static_cast<uint8_t>(first & 0xF0),
                .single_octet = true,
                .payload = remaining_.subspan(0, 1)
            };
            remaining_ = remaining_.subspan(1);
            return ie;
        }

        if (remaining_.size() < 2) return std::nullopt;

        const uint8_t len = remaining_[1];
        if (remaining_.size() < 2U + len) return std::nullopt;

        InformationElement ie{
            .ie_id = first,
            .single_octet = false,
            .payload = remaining_.subspan(2, len)
        };
        remaining_ = remaining_.subspan(2U + len);
        return ie;
    }

private:
    std::span<const uint8_t> remaining_;
};

} // namespace isdn
