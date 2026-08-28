#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>

namespace flat_telemetry {

// Безпечний типізований переглядач буфера FlatBuffers
class ReadingView {
public:
    explicit constexpr ReadingView(std::span<const uint8_t> buffer) noexcept
        : buffer_(buffer), table_(nullptr), vtable_(nullptr), vtable_len_(0) {
        if (buffer.size() < 4) return;

        uint32_t root_offset = 0;
        std::memcpy(&root_offset, buffer.data(), sizeof(root_offset));
        if (root_offset + sizeof(int32_t) > buffer.size()) return;

        table_ = buffer.data() + root_offset;
        int32_t vt_rel = 0;
        std::memcpy(&vt_rel, table_, sizeof(vt_rel));

        const uint8_t* vt_ptr = table_ + vt_rel;
        if (vt_ptr < buffer.data() || vt_ptr + sizeof(uint16_t) > buffer.data() + buffer.size()) {
            table_ = nullptr;
            return;
        }

        vtable_ = reinterpret_cast<const uint16_t*>(vt_ptr);
        uint16_t vtable_bytes = 0;
        std::memcpy(&vtable_bytes, vtable_, sizeof(uint16_t));
        vtable_len_ = vtable_bytes / sizeof(uint16_t);
    }

    [[nodiscard]] bool is_valid() const noexcept { return table_ != nullptr; }

    [[nodiscard]] uint32_t timestamp_s() const noexcept {
        return read_field<uint32_t>(2, 0);
    }

    [[nodiscard]] uint32_t sensor_id() const noexcept {
        return read_field<uint32_t>(3, 0);
    }

    [[nodiscard]] int32_t temperature_c100() const noexcept {
        return read_field<int32_t>(4, 0);
    }

    [[nodiscard]] uint32_t battery_mv() const noexcept {
        return read_field<uint32_t>(5, 3300); // 3300 mV за замовчуванням
    }

private:
    template <typename T>
    [[nodiscard]] T read_field(size_t vtable_index, T default_value) const noexcept {
        if (!is_valid() || vtable_index >= vtable_len_) return default_value;
        const uint16_t field_offset = vtable_[vtable_index];
        if (field_offset == 0) return default_value;

        T val{};
        std::memcpy(&val, table_ + field_offset, sizeof(T));
        return val;
    }

    std::span<const uint8_t> buffer_;
    const uint8_t* table_;
    const uint16_t* vtable_;
    size_t vtable_len_;
};

} // namespace flat_telemetry
