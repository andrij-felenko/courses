#include <cstdint>
#include <string_view>
#include <variant>
#include <optional>
#include <expected>
#include <atomic>
#include <array>
#include <span>
#include <bit>
#include <cstring>
#include <algorithm>

namespace drone {

// Поліном IEEE 802.3 (0xEDB88320)
inline constexpr std::array<uint32_t, 16> Crc32Table = {
    0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
    0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
    0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
    0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
};

constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = ~0U;
    for (const uint8_t byte : data) {
        crc ^= byte;
        crc = (crc >> 4) ^ Crc32Table[crc & 0x0F];
        crc = (crc >> 4) ^ Crc32Table[crc & 0x0F];
    }
    return ~crc;
}

enum class MavParamType : uint8_t {
    Int32  = 6,
    Real32 = 9
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

struct ParamMeta {
    std::string_view name;
    MavParamType     type;
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

    [[nodiscard]] float to_wire_float() const noexcept {
        if (meta_.type == MavParamType::Real32) {
            return std::get<float>(val_);
        }
        return std::bit_cast<float>(std::get<int32_t>(val_));
    }

    void from_wire_float(float wire_val) noexcept {
        if (meta_.type == MavParamType::Real32) {
            val_ = wire_val;
        } else {
            val_ = std::bit_cast<int32_t>(wire_val);
        }
    }

    [[nodiscard]] bool set(ParamValue new_val, bool is_armed) noexcept {
        if (has_flag(meta_.flags, ParamFlags::ReadOnly)) {
            return false;
        }

        if (has_flag(meta_.flags, ParamFlags::DisarmedOnly) && is_armed) {
            return false;
        }

        if (meta_.type == MavParamType::Real32) {
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
    const ParamMeta&  meta_;
    ParamValue        val_;
    std::atomic<bool> dirty_;
};

struct MavlinkParamSet {
    float            param_value{0.0f};
    uint8_t          target_system{0};
    uint8_t          target_component{0};
    std::string_view param_id{};
    uint8_t          param_type{0};
};

struct MavlinkParamValue {
    float            param_value{0.0f};
    uint16_t         param_count{0};
    uint16_t         param_index{0};
    std::string_view param_id{};
    uint8_t          param_type{0};
};

template <size_t MaxParams = 32, size_t FlashSectorSize = 512>
class ParamRegistry {
public:
    static constexpr uint32_t MagicHeader = 0x5041524DU; // "PARM"

    struct alignas(4) FlashSector {
        uint32_t            magic{0};
        uint32_t            seq_num{0};
        uint16_t            count{0};
        uint16_t            reserved{0};
        std::array<float, MaxParams> raw_values{};
        uint32_t            crc32{0};
    };

    constexpr ParamRegistry() noexcept = default;

    std::optional<size_t> register_param(const ParamMeta& meta) noexcept {
        if (count_ >= MaxParams) return std::nullopt;
        const size_t idx = count_++;
        entries_[idx].emplace(meta);
        return idx;
    }

    [[nodiscard]] std::optional<ParamValue> get_fast(size_t handle) const noexcept {
        if (handle >= count_ || !entries_[handle].has_value()) return std::nullopt;
        return entries_[handle]->get();
    }

    [[nodiscard]] std::optional<size_t> find(std::string_view name) const noexcept {
        for (size_t i = 0; i < count_; ++i) {
            if (entries_[i] && entries_[i]->meta().name == name) {
                return i;
            }
        }
        return std::nullopt;
    }

    bool set_value(size_t handle, ParamValue val, bool is_armed) noexcept {
        if (handle >= count_ || !entries_[handle].has_value()) return false;
        return entries_[handle]->set(val, is_armed);
    }

    bool save_to_flash() noexcept {
        const uint8_t next_sec = (active_sector_ == 0) ? 1 : 0;
        FlashSector sec{};
        sec.magic = MagicHeader;
        sec.seq_num = current_seq_ + 1;
        sec.count = static_cast<uint16_t>(count_);

        for (size_t i = 0; i < count_; ++i) {
            sec.raw_values[i] = entries_[i]->to_wire_float();
        }

        constexpr size_t payload_len = sizeof(FlashSector) - sizeof(uint32_t);
        auto payload_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&sec), payload_len);
        sec.crc32 = calculate_crc32(payload_bytes);

        std::memcpy(&flash_storage_[next_sec][0], &sec, sizeof(FlashSector));

        active_sector_ = next_sec;
        current_seq_ = sec.seq_num;
        for (size_t i = 0; i < count_; ++i) {
            entries_[i]->clear_dirty();
        }
        return true;
    }

    bool load_from_flash() noexcept {
        std::array<bool, 2> valid{false, false};
        std::array<FlashSector, 2> sectors{};
        constexpr size_t payload_len = sizeof(FlashSector) - sizeof(uint32_t);

        for (size_t i = 0; i < 2; ++i) {
            std::memcpy(&sectors[i], &flash_storage_[i][0], sizeof(FlashSector));
            if (sectors[i].magic == MagicHeader) {
                auto bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&sectors[i]), payload_len);
                if (calculate_crc32(bytes) == sectors[i].crc32) {
                    valid[i] = true;
                }
            }
        }

        int best = -1;
        if (valid[0] && valid[1]) {
            best = (sectors[0].seq_num >= sectors[1].seq_num) ? 0 : 1;
        } else if (valid[0]) {
            best = 0;
        } else if (valid[1]) {
            best = 1;
        }

        if (best < 0) {
            for (size_t i = 0; i < count_; ++i) {
                entries_[i]->set(entries_[i]->meta().def_val, false);
                entries_[i]->clear_dirty();
            }
            return false;
        }

        active_sector_ = static_cast<uint8_t>(best);
        current_seq_ = sectors[best].seq_num;
        const size_t load_cnt = std::min(count_, static_cast<size_t>(sectors[best].count));

        for (size_t i = 0; i < load_cnt; ++i) {
            entries_[i]->from_wire_float(sectors[best].raw_values[i]);
            entries_[i]->clear_dirty();
        }
        return true;
    }

    std::expected<MavlinkParamValue, MavlinkParamValue>
    handle_param_set(const MavlinkParamSet& msg, bool is_armed) noexcept {
        const auto handle_opt = find(msg.param_id);
        if (!handle_opt) {
            return std::unexpected(MavlinkParamValue{});
        }
        const size_t handle = *handle_opt;
        auto& entry = *entries_[handle];

        ParamValue incoming;
        if (entry.meta().type == MavParamType::Real32) {
            incoming = msg.param_value;
        } else {
            incoming = std::bit_cast<int32_t>(msg.param_value);
        }

        const bool success = entry.set(incoming, is_armed);

        MavlinkParamValue resp{};
        resp.param_id = entry.meta().name;
        resp.param_type = static_cast<uint8_t>(entry.meta().type);
        resp.param_count = static_cast<uint16_t>(count_);
        resp.param_index = static_cast<uint16_t>(handle);
        resp.param_value = entry.to_wire_float();

        if (success) {
            save_to_flash();
            return resp;
        }
        return std::unexpected(resp);
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }

private:
    std::array<std::optional<ParamEntry>, MaxParams> entries_{};
    size_t                                           count_{0};
    uint32_t                                         current_seq_{0};
    uint8_t                                          active_sector_{0};
    std::array<std::array<uint8_t, FlashSectorSize>, 2> flash_storage_{};
};

} // namespace drone
