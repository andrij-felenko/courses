// ============================================================================
// emb_i18n.hpp — Ідіоматичний вбудований рушій локалізації на C++20
// ============================================================================
#pragma once

#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <optional>
#include <array>
#include <algorithm>
#include <concepts>
#include <cstring>

namespace embedded::i18n {

enum class PluralCategory : uint8_t {
    Zero  = 0,
    One   = 1,
    Two   = 2,
    Few   = 3,
    Many  = 4,
    Other = 5
};

enum class MessageType : uint8_t {
    Simple = 0,
    Plural = 1
};

#pragma pack(push, 4)
struct ImageHeader {
    uint32_t magic;
    uint16_t version;
    uint16_t flags;
    uint32_t locale_count;
    uint32_t locale_table_offset;
    uint32_t total_size;
    uint32_t crc32;
    uint32_t reserved[2];
};

struct LocaleDescriptor {
    uint32_t locale_id;
    uint16_t plural_rule_id;
    uint16_t flags;
    uint32_t message_count;
    uint32_t index_table_offset;
    uint32_t string_pool_offset;
};

struct IndexEntry {
    uint32_t key_hash;
    uint32_t msg_desc_offset;
};

struct MessageDescriptor {
    uint8_t  type;
    uint8_t  reserved;
    uint16_t form_count;
    uint32_t string_offsets[6];
};
#pragma pack(pop)

// Обчислення MurmurHash3 під час компіляції (consteval)
consteval uint32_t const_hash(std::string_view key) noexcept {
    uint32_t h = 0x9747b28c;
    for (uint8_t b : key) {
        uint32_t k = b;
        k *= 0xcc9e2d51;
        k = (k << 15) | (k >> 17);
        k *= 0x1b873593;
        
        h ^= k;
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }
    h ^= static_cast<uint32_t>(key.size());
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}

constexpr uint32_t runtime_hash(std::string_view key) noexcept {
    uint32_t h = 0x9747b28c;
    for (uint8_t b : key) {
        uint32_t k = b;
        k *= 0xcc9e2d51;
        k = (k << 15) | (k >> 17);
        k *= 0x1b873593;
        
        h ^= k;
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }
    h ^= static_cast<uint32_t>(key.size());
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}

class Engine {
public:
    constexpr Engine() = default;

    static constexpr std::optional<Engine> create(std::span<const uint8_t> memory, uint32_t locale_id) noexcept {
        if (memory.size() < sizeof(ImageHeader)) return std::nullopt;

        const auto *hdr = reinterpret_cast<const ImageHeader*>(memory.data());
        if (hdr->magic != 0x45493138 || hdr->version != 1) return std::nullopt;
        if (hdr->total_size > memory.size() || hdr->locale_table_offset >= memory.size()) {
            return std::nullopt;
        }

        const auto *loc_table = reinterpret_cast<const LocaleDescriptor*>(memory.data() + hdr->locale_table_offset);
        const LocaleDescriptor *target_loc = nullptr;

        for (uint32_t i = 0; i < hdr->locale_count; ++i) {
            if (loc_table[i].locale_id == locale_id) {
                target_loc = &loc_table[i];
                break;
            }
        }

        if (!target_loc && hdr->locale_count > 0) {
            target_loc = &loc_table[0];
        }

        if (!target_loc) return std::nullopt;

        size_t index_bytes = static_cast<size_t>(target_loc->message_count) * sizeof(IndexEntry);
        if (target_loc->index_table_offset + index_bytes > memory.size() ||
            target_loc->string_pool_offset >= memory.size()) {
            return std::nullopt;
        }

        Engine eng;
        eng.raw_data_     = memory;
        eng.locale_desc_  = target_loc;
        eng.index_table_  = reinterpret_cast<const IndexEntry*>(memory.data() + target_loc->index_table_offset);
        eng.string_pool_  = reinterpret_cast<const char*>(memory.data() + target_loc->string_pool_offset);
        eng.message_count_= target_loc->message_count;
        eng.plural_rule_  = target_loc->plural_rule_id;
        eng.is_rtl_       = (target_loc->flags & 0x0001) != 0;
        return eng;
    }

    [[nodiscard]] constexpr std::string_view get(std::string_view key) const noexcept {
        uint32_t h = runtime_hash(key);
        auto opt_msg = get_by_hash(h);
        return opt_msg.value_or(key);
    }

    [[nodiscard]] constexpr std::optional<std::string_view> get_by_hash(uint32_t hash) const noexcept {
        const auto *desc = find_descriptor(hash);
        if (!desc || desc->type != static_cast<uint8_t>(MessageType::Simple)) {
            return std::nullopt;
        }
        return read_pool_string(desc->string_offsets[0]);
    }

    [[nodiscard]] constexpr std::string_view get_plural(std::string_view key, int32_t count) const noexcept {
        uint32_t h = runtime_hash(key);
        auto opt_msg = get_plural_by_hash(h, count);
        return opt_msg.value_or(key);
    }

    [[nodiscard]] constexpr std::optional<std::string_view> get_plural_by_hash(uint32_t hash, int32_t count) const noexcept {
        const auto *desc = find_descriptor(hash);
        if (!desc) return std::nullopt;

        if (desc->type == static_cast<uint8_t>(MessageType::Simple)) {
            return read_pool_string(desc->string_offsets[0]);
        }

        PluralCategory cat = evaluate_plural(plural_rule_, count);
        uint32_t offset = desc->string_offsets[static_cast<size_t>(cat)];
        if (offset == 0 && cat != PluralCategory::Other) {
            offset = desc->string_offsets[static_cast<size_t>(PluralCategory::Other)];
        }
        return read_pool_string(offset);
    }

    [[nodiscard]] constexpr bool is_rtl() const noexcept { return is_rtl_; }

    static constexpr PluralCategory evaluate_plural(uint16_t rule_id, int32_t n) noexcept {
        int32_t abs_n = n < 0 ? -n : n;
        switch (rule_id) {
            case 1: // English
                return (abs_n == 1) ? PluralCategory::One : PluralCategory::Other;
            case 2: { // Ukrainian
                int32_t rem10 = abs_n % 10;
                int32_t rem100 = abs_n % 100;
                if (rem10 == 1 && rem100 != 11) return PluralCategory::One;
                if (rem10 >= 2 && rem10 <= 4 && (rem100 < 10 || rem100 >= 20)) {
                    return PluralCategory::Few;
                }
                return PluralCategory::Many;
            }
            case 3: { // Polish
                if (abs_n == 1) return PluralCategory::One;
                int32_t rem10 = abs_n % 10;
                int32_t rem100 = abs_n % 100;
                if (rem10 >= 2 && rem10 <= 4 && (rem100 < 12 || rem100 > 14)) {
                    return PluralCategory::Few;
                }
                return PluralCategory::Many;
            }
            case 4: { // Arabic
                if (abs_n == 0) return PluralCategory::Zero;
                if (abs_n == 1) return PluralCategory::One;
                if (abs_n == 2) return PluralCategory::Two;
                int32_t rem100 = abs_n % 100;
                if (rem100 >= 3 && rem100 <= 10) return PluralCategory::Few;
                if (rem100 >= 11 && rem100 <= 99) return PluralCategory::Many;
                return PluralCategory::Other;
            }
            default:
                return PluralCategory::Other;
        }
    }

private:
    std::span<const uint8_t>  raw_data_{};
    const LocaleDescriptor    *locale_desc_{nullptr};
    const IndexEntry          *index_table_{nullptr};
    const char                *string_pool_{nullptr};
    uint32_t                  message_count_{0};
    uint16_t                  plural_rule_{0};
    bool                      is_rtl_{false};

    [[nodiscard]] constexpr const MessageDescriptor* find_descriptor(uint32_t hash) const noexcept {
        if (!index_table_ || message_count_ == 0) return nullptr;

        int32_t low = 0;
        int32_t high = static_cast<int32_t>(message_count_) - 1;

        while (low <= high) {
            int32_t mid = low + ((high - low) >> 1);
            uint32_t cur = index_table_[mid].key_hash;

            if (cur == hash) {
                uint32_t off = index_table_[mid].msg_desc_offset;
                if (off + sizeof(MessageDescriptor) <= raw_data_.size()) {
                    return reinterpret_cast<const MessageDescriptor*>(raw_data_.data() + off);
                }
                return nullptr;
            } else if (hash < cur) {
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        return nullptr;
    }

    [[nodiscard]] constexpr std::optional<std::string_view> read_pool_string(uint32_t pool_offset) const noexcept {
        if (!locale_desc_ || locale_desc_->string_pool_offset + pool_offset >= raw_data_.size()) {
            return std::nullopt;
        }
        const char *ptr = string_pool_ + pool_offset;
        return std::string_view(ptr);
    }
};

// Безпечний форматувальник рядків у статичний масив на стеку
template <size_t N>
class StaticBuffer {
public:
    constexpr StaticBuffer() { data_[0] = '\0'; }

    constexpr void format_1i(std::string_view fmt, int32_t val) noexcept {
        char num_str[16];
        int num_len = to_chars(num_str, val);
        size_t d = 0;

        for (size_t s = 0; s < fmt.size() && d < N - 1; ++s) {
            if (s + 2 < fmt.size() && fmt[s] == '{' && fmt[s+1] == '0' && fmt[s+2] == '}') {
                s += 2;
                for (int i = 0; i < num_len && d < N - 1; ++i) {
                    data_[d++] = num_str[i];
                }
            } else {
                data_[d++] = fmt[s];
            }
        }
        data_[d] = '\0';
        size_ = d;
    }

    [[nodiscard]] constexpr std::string_view view() const noexcept {
        return std::string_view(data_.data(), size_);
    }

    [[nodiscard]] constexpr const char* c_str() const noexcept {
        return data_.data();
    }

private:
    std::array<char, N> data_{};
    size_t size_{0};

    static constexpr int to_chars(char *buf, int32_t val) noexcept {
        char temp[16];
        int tlen = 0;
        int32_t v = val;
        bool neg = v < 0;
        if (neg) v = -v;

        do {
            temp[tlen++] = static_cast<char>('0' + (v % 10));
            v /= 10;
        } while (v > 0 && tlen < 14);

        if (neg) temp[tlen++] = '-';

        int out = 0;
        for (int i = tlen - 1; i >= 0; --i) {
            buf[out++] = temp[i];
        }
        buf[out] = '\0';
        return out;
    }
};

} // namespace embedded::i18n
