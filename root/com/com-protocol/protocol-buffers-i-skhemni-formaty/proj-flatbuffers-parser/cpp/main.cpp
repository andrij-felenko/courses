#include <cstdint>
#include <cstddef>
#include <cstring>
#include <string_view>
#include <span>
#include <optional>

// Типізований доступ до FlatBuffers буфера мовою C++
namespace flight {

struct alignas(4) Vector3 {
    float x;
    float y;
    float z;
};

class SensorReportView {
public:
    explicit SensorReportView(std::span<const uint8_t> buffer) noexcept
        : buffer_(buffer), table_(nullptr), vtable_(nullptr), vtable_entries_(0) {
        if (buffer.size() < 4) return;

        uint32_t root_offset = 0;
        std::memcpy(&root_offset, buffer.data(), sizeof(root_offset));
        if (root_offset + sizeof(int32_t) > buffer.size()) return;

        table_ = buffer.data() + root_offset;

        int32_t vt_offset = 0;
        std::memcpy(&vt_offset, table_, sizeof(vt_offset));
        const uint8_t* vt_ptr = table_ - vt_offset;

        if (vt_ptr < buffer.data() || vt_ptr + 2 > buffer.data() + buffer.size()) {
            table_ = nullptr;
            return;
        }

        vtable_ = reinterpret_cast<const uint16_t*>(vt_ptr);
        uint16_t vtable_byte_size = 0;
        std::memcpy(&vtable_byte_size, vtable_, sizeof(uint16_t));
        vtable_entries_ = vtable_byte_size / sizeof(uint16_t);
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

    [[nodiscard]] std::optional<Vector3> accel() const noexcept {
        if (!has_field(6)) return std::nullopt;
        const uint16_t off = vtable_[6];
        Vector3 v{};
        std::memcpy(&v, table_ + off, sizeof(Vector3));
        return v;
    }

    [[nodiscard]] std::string_view device_name() const noexcept {
        if (!has_field(7)) return {};
        const uint16_t field_off = vtable_[7];
        const uint8_t* field_ptr = table_ + field_off;

        uint32_t rel_offset = 0;
        std::memcpy(&rel_offset, field_ptr, sizeof(rel_offset));
        const uint8_t* str_head = field_ptr + rel_offset;

        uint32_t len = 0;
        std::memcpy(&len, str_head, sizeof(len));
        const char* str_chars = reinterpret_cast<const char*>(str_head + 4);

        return std::string_view{str_chars, len};
    }

private:
    [[nodiscard]] bool has_field(size_t field_index) const noexcept {
        return is_valid() && (field_index < vtable_entries_) && (vtable_[field_index] != 0);
    }

    template <typename T>
    [[nodiscard]] T read_field(size_t field_index, T default_value) const noexcept {
        if (!has_field(field_index)) return default_value;
        const uint16_t offset = vtable_[field_index];
        T val{};
        std::memcpy(&val, table_ + offset, sizeof(T));
        return val;
    }

    std::span<const uint8_t> buffer_;
    const uint8_t* table_;
    const uint16_t* vtable_;
    size_t vtable_entries_;
};

} // namespace flight
