#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <expected>

// Ідіоматичний C++20 кодувальник CBOR без виділення динамічної пам'яті
class CborWriter {
public:
    constexpr explicit CborWriter(std::span<uint8_t> buffer) noexcept 
        : buf_{buffer}, pos_{0}, overflow_{false} {}

    constexpr void write_byte(uint8_t val) noexcept {
        if (pos_ < buf_.size()) {
            buf_[pos_++] = val;
        } else {
            overflow_ = true;
        }
    }

    constexpr void write_uint(uint8_t major, uint32_t val) noexcept {
        const uint8_t type_hdr = static_cast<uint8_t>(major << 5);
        if (val < 24) {
            write_byte(static_cast<uint8_t>(type_hdr | val));
        } else if (val <= 0xFF) {
            write_byte(static_cast<uint8_t>(type_hdr | 24));
            write_byte(static_cast<uint8_t>(val));
        } else if (val <= 0xFFFF) {
            write_byte(static_cast<uint8_t>(type_hdr | 25));
            write_byte(static_cast<uint8_t>(val >> 8));
            write_byte(static_cast<uint8_t>(val & 0xFF));
        } else {
            write_byte(static_cast<uint8_t>(type_hdr | 26));
            write_byte(static_cast<uint8_t>(val >> 24));
            write_byte(static_cast<uint8_t>((val >> 16) & 0xFF));
            write_byte(static_cast<uint8_t>((val >> 8) & 0xFF));
            write_byte(static_cast<uint8_t>(val & 0xFF));
        }
    }

    [[nodiscard]] constexpr size_t bytes_written() const noexcept { return pos_; }
    [[nodiscard]] constexpr bool has_overflow() const noexcept { return overflow_; }

private:
    std::span<uint8_t> buf_;
    size_t pos_;
    bool overflow_;
};

struct TelemetrySample {
    uint32_t node_id;
    uint32_t timestamp;
    bool fault_flag;
    float temperature;
    float humidity;
    uint16_t vbat_mv;
};

// Безпечне пакування з поверненням std::span на записаний зріз або коду помилки
[[nodiscard]] std::expected<std::span<const uint8_t>, std::string_view>
encode_telemetry(const TelemetrySample& sample, std::span<uint8_t> out_buffer) noexcept {
    CborWriter writer{out_buffer};

    // 0xA6 = CBOR Map з 6 елементів
    writer.write_byte(0xA6);

    // 1: node_id
    writer.write_uint(0, 1);
    writer.write_uint(0, sample.node_id);

    // 2: timestamp
    writer.write_uint(0, 2);
    writer.write_uint(0, sample.timestamp);

    // 3: fault_flag
    writer.write_uint(0, 3);
    writer.write_byte(sample.fault_flag ? 0xF5 : 0xF4);

    // 4: temperature (фіксована кома x10)
    writer.write_uint(0, 4);
    const auto temp_scaled = static_cast<int16_t>(sample.temperature * 10.0f);
    if (temp_scaled >= 0) {
        writer.write_uint(0, static_cast<uint32_t>(temp_scaled));
    } else {
        writer.write_uint(1, static_cast<uint32_t>(-1 - temp_scaled));
    }

    // 5: humidity
    writer.write_uint(0, 5);
    writer.write_uint(0, static_cast<uint32_t>(sample.humidity * 10.0f));

    // 6: vbat_mv
    writer.write_uint(0, 6);
    writer.write_uint(0, sample.vbat_mv);

    if (writer.has_overflow()) {
        return std::unexpected{"CBOR buffer capacity exceeded"};
    }
    return out_buffer.first(writer.bytes_written());
}
