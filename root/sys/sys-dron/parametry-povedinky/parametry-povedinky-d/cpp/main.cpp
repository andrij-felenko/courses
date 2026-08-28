#include <cstdint>
#include <string_view>
#include <variant>
#include <optional>
#include <atomic>
#include <bit>

enum class ParamType : uint8_t {
    Int32,
    Float
};

enum class ParamFlags : uint16_t {
    None           = 0,
    DisarmedOnly   = 1 << 0,
    RebootRequired = 1 << 1,
    ReadOnly       = 1 << 2
};

inline constexpr ParamFlags operator|(ParamFlags a, ParamFlags b) noexcept {
    return static_cast<ParamFlags>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

inline constexpr bool has_flag(ParamFlags flags, ParamFlags check) noexcept {
    return (static_cast<uint16_t>(flags) & static_cast<uint16_t>(check)) != 0;
}

using ParamValue = std::variant<int32_t, float>;

// Опис метаданих для розміщення у .rodata
struct ParamMeta {
    std::string_view name;
    ParamType        type;
    ParamValue       min_val;
    ParamValue       max_val;
    ParamValue       def_val;
    ParamFlags       flags{ParamFlags::None};
};

class ParamEntry {
public:
    constexpr explicit ParamEntry(const ParamMeta& meta) noexcept
        : meta_(meta), val_(meta.def_val), dirty_(false) {}

    [[nodiscard]] ParamValue get() const noexcept {
        return val_;
    }

    [[nodiscard]] bool set(ParamValue new_val, bool is_armed) noexcept {
        if (has_flag(meta_.flags, ParamFlags::ReadOnly)) {
            return false;
        }

        if (has_flag(meta_.flags, ParamFlags::DisarmedOnly) && is_armed) {
            return false;
        }

        if (meta_.type == ParamType::Float) {
            const float v = std::get<float>(new_val);
            const float min_v = std::get<float>(meta_.min_val);
            const float max_v = std::get<float>(meta_.max_val);
            if (v < min_v || v > max_v) {
                return false;
            }
        } else {
            const int32_t v = std::get<int32_t>(new_val);
            const int32_t min_v = std::get<int32_t>(meta_.min_val);
            const int32_t max_v = std::get<int32_t>(meta_.max_val);
            if (v < min_v || v > max_v) {
                return false;
            }
        }

        val_ = new_val;
        dirty_.store(true, std::memory_order_release);
        return true;
    }

    [[nodiscard]] bool is_dirty() const noexcept {
        return dirty_.load(std::memory_order_acquire);
    }

    void clear_dirty() noexcept {
        dirty_.store(false, std::memory_order_release);
    }

    [[nodiscard]] const ParamMeta& meta() const noexcept {
        return meta_;
    }

private:
    const ParamMeta&   meta_;
    ParamValue         val_;
    std::atomic<bool>  dirty_;
};
