// ============================================================================
// i18n_engine.hpp — Ідіоматичний рушій локалізації на C++20 (Zero-Heap / XIP)
// ============================================================================
#pragma once

#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <optional>
#include <array>
#include <algorithm>
#include <format>

namespace i18n {

enum class PluralCategory : uint8_t {
    Zero,
    One,
    Two,
    Few,
    Many,
    Other
};

struct IndexEntry {
    uint32_t key_hash;
    uint32_t string_offset;
};

struct BinaryHeader {
    uint32_t magic;
    uint16_t version;
    uint16_t locale_id;
    uint32_t entry_count;
    uint32_t index_offset;
    uint32_t string_pool_offset;
    uint32_t plural_rule_id;
};

constexpr uint32_t hash_key(std::string_view key) noexcept {
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

class Catalog {
public:
    constexpr Catalog() = default;

    static constexpr std::optional<Catalog> create(std::span<const uint8_t> memory) noexcept {
        if (memory.size() < sizeof(BinaryHeader)) return std::nullopt;

        const auto *hdr = reinterpret_cast<const BinaryHeader*>(memory.data());
        if (hdr->magic != 0x4931384E) return std::nullopt;

        size_t index_size = hdr->entry_count * sizeof(IndexEntry);
        if (hdr->index_offset + index_size > memory.size() ||
            hdr->string_pool_offset >= memory.size()) {
            return std::nullopt;
        }

        Catalog cat;
        cat.raw_data_ = memory;
        cat.entry_count_ = hdr->entry_count;
        cat.plural_rule_id_ = hdr->plural_rule_id;
        cat.index_ = reinterpret_cast<const IndexEntry*>(memory.data() + hdr->index_offset);
        cat.string_pool_ = reinterpret_cast<const char*>(memory.data() + hdr->string_pool_offset);
        return cat;
    }

    [[nodiscard]] constexpr std::string_view get(std::string_view key) const noexcept {
        uint32_t hash = hash_key(key);
        auto opt_str = get_by_hash(hash);
        return opt_str.value_or(key);
    }

    [[nodiscard]] constexpr std::optional<std::string_view> get_by_hash(uint32_t hash) const noexcept {
        if (!index_ || entry_count_ == 0) return std::nullopt;

        int32_t low = 0;
        int32_t high = static_cast<int32_t>(entry_count_) - 1;

        while (low <= high) {
            int32_t mid = low + ((high - low) >> 1);
            uint32_t cur = index_[mid].key_hash;

            if (cur == hash) {
                uint32_t off = index_[mid].string_offset;
                const char *str_ptr = string_pool_ + off;
                return std::string_view(str_ptr);
            } else if (hash < cur) {
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] constexpr PluralCategory select_plural(int32_t n) const noexcept {
        int32_t abs_n = n < 0 ? -n : n;
        switch (plural_rule_id_) {
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
            default:
                return PluralCategory::Other;
        }
    }

private:
    std::span<const uint8_t> raw_data_{};
    const IndexEntry *index_{nullptr};
    const char *string_pool_{nullptr};
    uint32_t entry_count_{0};
    uint32_t plural_rule_id_{0};
};

} // namespace i18n
