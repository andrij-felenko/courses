#include <cstddef>
#include <cstdint>
#include <span>
#include <optional>

namespace asn1 {

struct DerElement {
    uint8_t tag{};
    std::span<const uint8_t> value{};
    size_t total_tlv_size{};
};

/* Читання TLV-елемента у стилі сучасного C++20 без виділення пам'яті */
constexpr std::optional<DerElement> read_element(std::span<const uint8_t> data) noexcept {
    if (data.size() < 2) return std::nullopt;

    uint8_t tag = data[0];
    size_t offset = 1;
    size_t val_len = 0;

    if ((data[offset] & 0x80) == 0) {
        val_len = data[offset];
        offset += 1;
    } else {
        size_t len_octets = data[offset] & 0x7F;
        offset += 1;
        if (len_octets == 0 || len_octets > sizeof(size_t) || offset + len_octets > data.size()) {
            return std::nullopt;
        }
        val_len = 0;
        for (size_t i = 0; i < len_octets; ++i) {
            val_len = (val_len << 8) | data[offset + i];
        }
        offset += len_octets;
    }

    if (offset + val_len > data.size()) return std::nullopt;

    return DerElement{
        tag,
        data.subspan(offset, val_len),
        offset + val_len
    };
}

/* Пошук блоку SubjectPublicKeyInfo */
std::optional<std::span<const uint8_t>> find_spki(std::span<const uint8_t> cert_der) noexcept {
    auto cert_seq = read_element(cert_der);
    if (!cert_seq || cert_seq->tag != 0x30) return std::nullopt;

    auto tbs_seq = read_element(cert_seq->value);
    if (!tbs_seq || tbs_seq->tag != 0x30) return std::nullopt;

    auto cursor = tbs_seq->value;
    int field_index = 0;

    while (!cursor.empty()) {
        auto elem = read_element(cursor);
        if (!elem) return std::nullopt;

        if (field_index == 0 && elem->tag == 0xA0) {
            cursor = cursor.subspan(elem->total_tlv_size);
            continue;
        }

        if (field_index == 5 && elem->tag == 0x30) {
            return cursor.subspan(0, elem->total_tlv_size);
        }

        cursor = cursor.subspan(elem->total_tlv_size);
        field_index++;
    }
    return std::nullopt;
}

} // namespace asn1
