#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <optional>
#include <bit>
#include <algorithm>
#include <cstring>

class MoFileReader {
public:
    struct StringDesc {
        uint32_t length;
        uint32_t offset;
    };

    constexpr MoFileReader() = default;

    static std::optional<MoFileReader> create(std::span<const uint8_t> memory) noexcept {
        if (memory.size() < 28) return std::nullopt;

        uint32_t magic = read_u32(memory.data());
        bool swap = false;
        if (magic == 0x950412DE) {
            swap = false;
        } else if (magic == 0xDE120495) {
            swap = true;
        } else {
            return std::nullopt;
        }

        uint32_t count     = swap_val(read_u32(memory.data() + 8), swap);
        uint32_t orig_off  = swap_val(read_u32(memory.data() + 12), swap);
        uint32_t trans_off = swap_val(read_u32(memory.data() + 16), swap);

        size_t table_bytes = static_cast<size_t>(count) * sizeof(StringDesc);
        if (orig_off + table_bytes > memory.size() || trans_off + table_bytes > memory.size()) {
            return std::nullopt;
        }

        MoFileReader reader;
        reader.raw_data_    = memory;
        reader.num_strings_ = count;
        reader.orig_table_  = reinterpret_cast<const StringDesc*>(memory.data() + orig_off);
        reader.trans_table_ = reinterpret_cast<const StringDesc*>(memory.data() + trans_off);
        reader.swap_endian_ = swap;
        return reader;
    }

    [[nodiscard]] std::string_view lookup(std::string_view msgid) const noexcept {
        if (raw_data_.empty()) return msgid;

        int32_t low = 0;
        int32_t high = static_cast<int32_t>(num_strings_) - 1;

        while (low <= high) {
            int32_t mid = low + ((high - low) >> 1);
            uint32_t len = swap_val(orig_table_[mid].length, swap_endian_);
            uint32_t off = swap_val(orig_table_[mid].offset, swap_endian_);

            if (off + len >= raw_data_.size()) break;

            std::string_view candidate(reinterpret_cast<const char*>(raw_data_.data() + off), len);
            if (msgid == candidate) {
                uint32_t tr_len = swap_val(trans_table_[mid].length, swap_endian_);
                uint32_t tr_off = swap_val(trans_table_[mid].offset, swap_endian_);
                if (tr_off + tr_len < raw_data_.size()) {
                    return { reinterpret_cast<const char*>(raw_data_.data() + tr_off), tr_len };
                }
                break;
            } else if (msgid < candidate) {
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        return msgid;
    }

private:
    std::span<const uint8_t> raw_data_{};
    uint32_t num_strings_{0};
    const StringDesc *orig_table_{nullptr};
    const StringDesc *trans_table_{nullptr};
    bool swap_endian_{false};

    static inline uint32_t read_u32(const uint8_t *ptr) noexcept {
        uint32_t v;
        std::memcpy(&v, ptr, sizeof(v));
        return v;
    }

    static inline uint32_t swap_val(uint32_t val, bool swap) noexcept {
        return swap ? std::byteswap(val) : val;
    }
};
